from __future__ import annotations

import fnmatch
import json
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from ..download import DownloadEngine
from ..models import DownloadRequest


class InternetArchivePlugin:
    source_id = "internet_archive"

    def __init__(self, engine: DownloadEngine) -> None:
        self.engine = engine

    def metadata(self, item_id: str) -> dict:
        clean_item_id = item_id.strip()
        url = f"https://archive.org/metadata/{quote(clean_item_id, safe='')}"
        try:
            with urlopen(Request(url, headers={"User-Agent": "anima-dataset-studio/0.1"}), timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"Internet Archive 元数据请求失败：{describe_http_error(exc)}") from exc
        if data.get("error"):
            raise RuntimeError(f"Internet Archive 条目不可用：{clean_item_id} - {data['error']}")
        return data

    def search(self, query: str, *, rows: int = 5) -> list[dict]:
        params = {
            "q": query,
            "fl[]": ["identifier", "title"],
            "rows": str(rows),
            "page": "1",
            "output": "json",
        }
        url = f"https://archive.org/advancedsearch.php?{urlencode(params, doseq=True)}"
        try:
            with urlopen(Request(url, headers={"User-Agent": "anima-dataset-studio/0.1"}), timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"Internet Archive 搜索失败：{describe_http_error(exc)}") from exc
        return data.get("response", {}).get("docs", [])

    def matching_files(self, item_id: str, *, include: list[str] | None = None) -> tuple[dict, list[dict]]:
        include = include or ["*"]
        meta = self.metadata(item_id)
        files = [
            file_info
            for file_info in meta.get("files", [])
            if self._matches(file_info, include)
        ]
        return meta, files

    def download(
        self,
        item_id: str,
        *,
        include: list[str] | None = None,
        max_files: int | None = None,
        fail_if_empty: bool = True,
    ):
        include = include or ["*"]
        meta, files = self.matching_files(item_id, include=include)
        results = []
        for file_info in files:
            name = file_info.get("name")
            if not name:
                continue
            url = f"https://archive.org/download/{quote(item_id.strip(), safe='')}/{quote(name, safe='/')}"
            results.append(
                self.engine.download(
                    DownloadRequest(
                        url=url,
                        source_id=self.source_id,
                        filename=name.replace("/", "__"),
                        metadata={"item_id": item_id, "file": file_info, "metadata_title": meta.get("metadata", {}).get("title")},
                    )
                )
            )
            if max_files and len(results) >= max_files:
                break
        if fail_if_empty and not results:
            raise RuntimeError(self.empty_message(item_id, meta, include))
        return results

    def download_search(
        self,
        query: str,
        *,
        include: list[str] | None = None,
        max_items: int = 1,
        max_files_per_item: int = 1,
    ):
        include = include or ["*.pdf", "*.zip", "*.cbz", "*.jpg", "*.png"]
        results = []
        scanned: list[str] = []
        rows = min(max(max_items * 10, 10), 100)
        for doc in self.search(query, rows=rows):
            item_id = doc.get("identifier")
            if not item_id:
                continue
            scanned.append(item_id)
            item_results = self.download(
                item_id,
                include=include,
                max_files=max_files_per_item,
                fail_if_empty=False,
            )
            if item_results:
                results.extend(item_results)
            if len(results) >= max_items * max_files_per_item:
                break
        if not results:
            raise RuntimeError(
                "Internet Archive 搜索没有找到匹配文件："
                f"query={query}, include={', '.join(include)}, 已检查条目={', '.join(scanned[:8]) or '无'}"
            )
        return results

    def _matches(self, file_info: dict, include: list[str]) -> bool:
        name = str(file_info.get("name") or "")
        file_format = str(file_info.get("format") or "")
        if not name:
            return False
        candidates = [name, file_format, file_format.lower().replace(" ", "_")]
        return any(fnmatch.fnmatch(candidate, pattern) for candidate in candidates for pattern in include)

    def empty_message(self, item_id: str, meta: dict, include: list[str]) -> str:
        names = [str(file_info.get("name")) for file_info in meta.get("files", []) if file_info.get("name")]
        sample = ", ".join(names[:8]) if names else "无文件列表"
        title = meta.get("metadata", {}).get("title") or item_id
        return (
            f"Internet Archive 条目没有匹配文件：{title} ({item_id})；"
            f"规则={', '.join(include)}；样例文件={sample}"
        )


def describe_http_error(exc: HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8", errors="replace").strip()
    except Exception:  # noqa: BLE001
        body = ""
    detail = f"HTTP {exc.code} {exc.reason}"
    if body:
        detail = f"{detail} - {body[:500]}"
    return detail
