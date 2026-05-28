from __future__ import annotations

import hashlib
import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import AssetRecord, DownloadRequest, DownloadResult
from .paths import filename_from_url, source_dir_name
from .storage import Database

CHUNK_SIZE = 1024 * 1024
USER_AGENT = "anima-dataset-studio/0.1"
MAX_DOWNLOAD_ATTEMPTS = 3
RETRY_HTTP_CODES = {429, 500, 502, 503, 504}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def unique_target(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    index = 1
    while True:
        candidate = parent / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


class DownloadEngine:
    def __init__(self, root: Path, db: Database) -> None:
        self.root = root
        self.db = db

    def download(self, request: DownloadRequest) -> DownloadResult:
        job_id = uuid.uuid4().hex
        raw_dir = self.root / "data" / "raw" / source_dir_name(request.source_id)
        raw_dir.mkdir(parents=True, exist_ok=True)
        filename = request.filename or filename_from_url(request.url)
        target = unique_target(raw_dir / filename)
        part = target.with_suffix(target.suffix + ".part")
        self.db.upsert_job(
            job_id=job_id,
            source_id=request.source_id,
            url=request.url,
            target_path=target,
            status="RUNNING",
            bytes_done=part.stat().st_size if part.exists() else 0,
            metadata=request.metadata,
        )

        try:
            bytes_done = self._download_to_part(request, part)
            if target.exists():
                target.unlink()
            part.replace(target)
            digest = sha256_file(target)
            if request.expected_sha256 and digest.lower() != request.expected_sha256.lower():
                error = "sha256 mismatch"
                self.db.update_job(
                    job_id,
                    status="FAILED",
                    bytes_done=bytes_done,
                    sha256=digest,
                    error=error,
                )
                return DownloadResult(job_id, "FAILED", target, digest, bytes_done, error)

            asset = AssetRecord(
                asset_id=f"sha256:{digest}",
                source_id=request.source_id,
                source_url=request.url,
                local_path=target,
                sha256=digest,
                metadata=request.metadata,
            )
            self.db.record_asset(asset)
            self.db.update_job(job_id, status="DOWNLOADED", bytes_done=bytes_done, sha256=digest)
            return DownloadResult(job_id, "DOWNLOADED", target, digest, bytes_done)
        except Exception as exc:  # noqa: BLE001 - CLI should persist any failure.
            self.db.update_job(job_id, status="FAILED", bytes_done=part.stat().st_size if part.exists() else 0, error=str(exc))
            return DownloadResult(job_id, "FAILED", target, None, part.stat().st_size if part.exists() else 0, str(exc))

    def _download_to_part(self, request: DownloadRequest, part: Path) -> int:
        last_error: Exception | None = None
        for attempt in range(1, MAX_DOWNLOAD_ATTEMPTS + 1):
            resume_from = part.stat().st_size if part.exists() else 0
            headers = {"User-Agent": USER_AGENT, **request.headers}
            if resume_from:
                headers["Range"] = f"bytes={resume_from}-"
            req = Request(request.url, headers=headers)

            try:
                response = urlopen(req, timeout=60)
                return self._write_response(response, part, resume_from)
            except HTTPError as exc:
                if exc.code == 416 and part.exists():
                    return part.stat().st_size
                last_error = exc
                if exc.code in RETRY_HTTP_CODES and attempt < MAX_DOWNLOAD_ATTEMPTS:
                    time.sleep(retry_delay(exc, attempt))
                    continue
                raise RuntimeError(describe_http_error(exc)) from exc
            except URLError as exc:
                last_error = exc
                if attempt < MAX_DOWNLOAD_ATTEMPTS:
                    time.sleep(retry_delay(None, attempt))
                    continue
                raise RuntimeError(f"网络请求失败：{exc.reason}") from exc
            except (TimeoutError, OSError) as exc:
                last_error = exc
                if attempt < MAX_DOWNLOAD_ATTEMPTS:
                    time.sleep(retry_delay(None, attempt))
                    continue
                raise
        raise RuntimeError(f"下载失败：{last_error}")

    def _write_response(self, response: Any, part: Path, resume_from: int) -> int:
        mode = "ab" if resume_from and response.status == 206 else "wb"
        if mode == "wb":
            resume_from = 0
        bytes_done = resume_from
        with response, part.open(mode) as handle:
            while True:
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                handle.write(chunk)
                bytes_done += len(chunk)
        return bytes_done

    def import_file(self, path: Path, *, source_id: str = "local_import", metadata: dict | None = None) -> AssetRecord:
        source = path.resolve()
        raw_dir = self.root / "data" / "raw" / source_dir_name(source_id)
        raw_dir.mkdir(parents=True, exist_ok=True)
        target = unique_target(raw_dir / source.name)
        shutil.copy2(source, target)
        digest = sha256_file(target)
        asset = AssetRecord(
            asset_id=f"sha256:{digest}",
            source_id=source_id,
            source_url=str(source),
            local_path=target,
            sha256=digest,
            metadata=metadata or {},
        )
        self.db.record_asset(asset)
        return asset

    def import_directory(self, path: Path, *, source_id: str = "local_import") -> list[AssetRecord]:
        records: list[AssetRecord] = []
        for child in path.rglob("*"):
            if child.is_file():
                records.append(self.import_file(child, source_id=source_id, metadata={"relative_path": os.fspath(child.relative_to(path))}))
        return records


def describe_http_error(exc: HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8", errors="replace").strip()
    except Exception:  # noqa: BLE001
        body = ""
    detail = f"HTTP {exc.code} {exc.reason}"
    if body:
        detail = f"{detail} - {body[:500]}"
    return detail


def retry_delay(exc: HTTPError | None, attempt: int) -> float:
    if exc and exc.headers:
        retry_after = exc.headers.get("Retry-After")
        if retry_after and retry_after.isdigit():
            return min(float(retry_after), 30.0)
    return min(float(2 ** (attempt - 1)), 8.0)
