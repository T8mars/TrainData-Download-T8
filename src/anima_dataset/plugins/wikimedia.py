from __future__ import annotations

import json
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ..download import DownloadEngine
from ..models import DownloadRequest

API_URL = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "anima-dataset-studio/0.1"
DOWNLOAD_PAUSE_SECONDS = 0.35


class WikimediaCommonsPlugin:
    source_id = "wikimedia_commons"

    def __init__(self, engine: DownloadEngine) -> None:
        self.engine = engine

    def category_files(self, category: str, *, limit: int = 50) -> list[dict]:
        if not category.startswith("Category:"):
            category = f"Category:{category}"
        params = {
            "action": "query",
            "format": "json",
            "generator": "categorymembers",
            "gcmtitle": category,
            "gcmtype": "file",
            "gcmlimit": str(min(limit, 500)),
            "prop": "imageinfo",
            "iiprop": "url|mime|size|extmetadata",
        }
        return self._fetch_pages(params)

    def search_files(self, query: str, *, limit: int = 50) -> list[dict]:
        params = {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": query,
            "gsrnamespace": "6",
            "gsrlimit": str(min(limit, 50)),
            "prop": "imageinfo",
            "iiprop": "url|mime|size|extmetadata",
        }
        return self._fetch_pages(params)

    def _fetch_pages(self, params: dict[str, str]) -> list[dict]:
        url = f"{API_URL}?{urlencode(params)}"
        try:
            with urlopen(Request(url, headers={"User-Agent": USER_AGENT}), timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"Wikimedia API 请求失败：{describe_http_error(exc)}") from exc
        if data.get("error"):
            message = data["error"].get("info") or data["error"].get("code") or data["error"]
            raise RuntimeError(f"Wikimedia API 返回错误：{message}")
        pages = data.get("query", {}).get("pages", {})
        return list(pages.values())

    def download_pages(self, pages: list[dict], *, max_files: int | None = None):
        if not pages:
            raise RuntimeError("Wikimedia 没有找到可下载文件，请调整分类或搜索词。")
        results = []
        for page in pages:
            imageinfo = (page.get("imageinfo") or [{}])[0]
            url = imageinfo.get("url")
            if not url:
                continue
            title = page.get("title", "wikimedia_file").replace("File:", "")
            results.append(
                self.engine.download(
                    DownloadRequest(
                        url=url,
                        source_id=self.source_id,
                        filename=title,
                        metadata={"page": page},
                    )
                )
            )
            if max_files and len(results) >= max_files:
                break
            time.sleep(DOWNLOAD_PAUSE_SECONDS)
        if not results:
            raise RuntimeError("Wikimedia 没有解析到文件 URL，请调整分类或搜索词。")
        if all(result.status == "FAILED" for result in results):
            raise RuntimeError(f"Wikimedia 下载全部失败，最近错误：{results[-1].error}")
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
