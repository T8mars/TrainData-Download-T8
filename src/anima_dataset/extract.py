from __future__ import annotations

import shutil
import tarfile
import zipfile
from pathlib import Path

from .download import sha256_file
from .models import AssetRecord
from .paths import safe_name
from .storage import Database

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
ARCHIVE_SUFFIXES = {".zip", ".cbz", ".tar", ".tgz", ".gz"}


def _safe_target(base: Path, member_name: str) -> Path:
    target = (base / member_name).resolve()
    target.relative_to(base.resolve())
    return target


class Extractor:
    def __init__(self, root: Path, db: Database) -> None:
        self.root = root
        self.db = db

    def extract(self, archive_path: Path, *, source_id: str = "extract") -> list[AssetRecord]:
        archive_path = archive_path.resolve()
        if not archive_path.exists():
            raise FileNotFoundError(archive_path)
        suffix = archive_path.suffix.lower()
        if suffix not in ARCHIVE_SUFFIXES and not archive_path.name.lower().endswith(".tar.gz"):
            raise ValueError(f"unsupported archive type: {archive_path}")

        out_dir = self.root / "data" / "extracted" / safe_name(archive_path.stem)
        out_dir.mkdir(parents=True, exist_ok=True)
        if zipfile.is_zipfile(archive_path):
            self._extract_zip(archive_path, out_dir)
        elif tarfile.is_tarfile(archive_path):
            self._extract_tar(archive_path, out_dir)
        else:
            raise ValueError(f"unsupported archive type: {archive_path}")
        return self._record_outputs(out_dir, source_url=str(archive_path), source_id=source_id)

    def _extract_zip(self, archive_path: Path, out_dir: Path) -> None:
        with zipfile.ZipFile(archive_path) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                target = _safe_target(out_dir, info.filename)
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info) as source, target.open("wb") as dest:
                    shutil.copyfileobj(source, dest)

    def _extract_tar(self, archive_path: Path, out_dir: Path) -> None:
        with tarfile.open(archive_path) as tf:
            for member in tf.getmembers():
                if not member.isfile():
                    continue
                source = tf.extractfile(member)
                if source is None:
                    continue
                target = _safe_target(out_dir, member.name)
                target.parent.mkdir(parents=True, exist_ok=True)
                with source, target.open("wb") as dest:
                    shutil.copyfileobj(source, dest)

    def _record_outputs(self, out_dir: Path, *, source_url: str, source_id: str) -> list[AssetRecord]:
        records: list[AssetRecord] = []
        for path in out_dir.rglob("*"):
            if not path.is_file():
                continue
            digest = sha256_file(path)
            record = AssetRecord(
                asset_id=f"sha256:{digest}",
                source_id=source_id,
                source_url=source_url,
                local_path=path,
                sha256=digest,
                status="EXTRACTED",
                metadata={"image_candidate": path.suffix.lower() in IMAGE_SUFFIXES},
            )
            self.db.record_asset(record)
            records.append(record)
        return records
