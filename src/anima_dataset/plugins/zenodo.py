from __future__ import annotations

import fnmatch
import json
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from ..download import DownloadEngine
from ..models import DownloadRequest


class ZenodoPlugin:
    source_id = "zenodo"
    api_base = "https://zenodo.org/api"

    def __init__(self, engine: DownloadEngine) -> None:
        self.engine = engine

    def record(self, record_id: str) -> dict:
        url = f"{self.api_base}/records/{quote(str(record_id).strip(), safe='')}"
        try:
            with urlopen(Request(url, headers={"User-Agent": "anima-dataset-studio/0.1"}), timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"Zenodo 记录请求失败：{describe_http_error(exc)}") from exc

    def search(self, query: str, *, rows: int = 5) -> list[dict]:
        params = {"q": query, "size": str(rows)}
        url = f"{self.api_base}/records?{urlencode(params)}"
        try:
            with urlopen(Request(url, headers={"User-Agent": "anima-dataset-studio/0.1"}), timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"Zenodo 搜索失败：{describe_http_error(exc)}") from exc
        return data.get("hits", {}).get("hits", [])

    def matching_files(self, record: dict, include: list[str] | None = None) -> list[dict]:
        include = include or ["*"]
        files = record.get("files") or []
        return [
            file for file in files
            if any(fnmatch.fnmatch(str(file.get("key") or ""), pattern) for pattern in include)
        ]

    def preflight(self, *, record_id: str | None = None, query: str | None = None, include: list[str] | None = None, max_records: int = 1) -> dict:
        records = [self.record(record_id)] if record_id else self.search(query or "", rows=max_records)
        samples = []
        for record in records:
            for file in self.matching_files(record, include=include)[:10]:
                samples.append({"name": file.get("key"), "size": file.get("size"), "record": record.get("id")})
        if not samples:
            raise RuntimeError("Zenodo 预检没有匹配文件，请调整 record_id/query/include。")
        return {"ok": True, "provider": "zenodo", "count": len(samples), "samples": samples, "message": "Zenodo 预检通过。"}

    def download(
        self,
        *,
        record_id: str | None = None,
        query: str | None = None,
        include: list[str] | None = None,
        max_records: int = 1,
        max_files: int = 1,
    ):
        records = [self.record(record_id)] if record_id else self.search(query or "", rows=max_records)
        results = []
        for record in records:
            for file in self.matching_files(record, include=include):
                links = file.get("links") or {}
                url = links.get("self") or links.get("download")
                name = file.get("key")
                if not url or not name:
                    continue
                results.append(
                    self.engine.download(
                        DownloadRequest(
                            url=url,
                            source_id=self.source_id,
                            filename=str(name).replace("/", "__"),
                            metadata={"record_id": record.get("id"), "title": record.get("metadata", {}).get("title"), "file": file},
                        )
                    )
                )
                if len(results) >= max_files:
                    return results
        if not results:
            raise RuntimeError("Zenodo 没有下载到任何文件，请先预检确认匹配规则。")
        return results


def describe_http_error(exc: HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8", errors="replace").strip()
    except Exception:  # noqa: BLE001
        body = ""
    detail = f"HTTP {exc.code} {exc.reason}"
    if body:
        detail = f"{detail} - {body[:500]}"
    return detail
