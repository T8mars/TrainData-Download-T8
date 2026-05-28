from __future__ import annotations

import json
from urllib.error import HTTPError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

from ..download import DownloadEngine
from ..models import DownloadRequest
from ..paths import filename_from_url

BOORU_SITES = {
    "gelbooru": {"kind": "gelbooru", "base": "https://gelbooru.com"},
    "safebooru": {"kind": "gelbooru", "base": "https://safebooru.org"},
    "danbooru": {"kind": "danbooru", "base": "https://danbooru.donmai.us"},
    "konachan": {"kind": "moebooru", "base": "https://konachan.com"},
    "yandere": {"kind": "moebooru", "base": "https://yande.re"},
}


class BooruPlugin:
    source_id = "booru"

    def __init__(self, engine: DownloadEngine) -> None:
        self.engine = engine

    def search(self, site: str, tags: str, *, limit: int = 20, page: int = 1) -> list[dict]:
        config = BOORU_SITES.get(site)
        if not config:
            raise ValueError(f"不支持的 Booru 站点：{site}")
        if config["kind"] == "gelbooru":
            params = {"page": "dapi", "s": "post", "q": "index", "json": "1", "tags": tags, "limit": str(limit), "pid": str(max(page - 1, 0))}
            url = f"{config['base']}/index.php?{urlencode(params)}"
        elif config["kind"] == "danbooru":
            params = {"tags": tags, "limit": str(limit), "page": str(page)}
            url = f"{config['base']}/posts.json?{urlencode(params)}"
        else:
            params = {"tags": tags, "limit": str(limit), "page": str(page)}
            url = f"{config['base']}/post.json?{urlencode(params)}"
        try:
            with urlopen(Request(url, headers={"User-Agent": "anima-dataset-studio/0.1"}), timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"Booru 搜索失败：{describe_http_error(exc)}") from exc
        if isinstance(data, dict) and "post" in data:
            posts = data["post"]
        else:
            posts = data
        return posts if isinstance(posts, list) else []

    def image_url(self, site: str, post: dict) -> str | None:
        raw_url = (
            post.get("file_url")
            or post.get("large_file_url")
            or post.get("sample_url")
            or post.get("jpeg_url")
            or post.get("preview_file_url")
            or post.get("preview_url")
            or media_asset_url(post)
            or post.get("source")
        )
        if not raw_url:
            return None
        if raw_url.startswith("//"):
            return f"https:{raw_url}"
        config = BOORU_SITES.get(site)
        return urljoin(f"{config['base']}/" if config else "", raw_url)

    def preflight(self, site: str, tags: str, *, limit: int = 20) -> dict:
        posts = self.search(site, tags, limit=limit)
        samples = []
        for post in posts:
            url = self.image_url(site, post)
            if url:
                samples.append({"name": filename_from_url(url), "url": url, "id": post.get("id")})
        if not samples:
            raise RuntimeError("Booru 预检没有找到可下载图片 URL，请调整站点或 tags。")
        return {"ok": True, "provider": "booru", "count": len(samples), "samples": samples[:10], "message": "Booru 预检通过。"}

    def download(self, site: str, tags: str, *, limit: int = 20, max_files: int | None = None):
        results = []
        for post in self.search(site, tags, limit=limit):
            url = self.image_url(site, post)
            if not url:
                continue
            results.append(
                self.engine.download(
                    DownloadRequest(
                        url=url,
                        source_id=self.source_id,
                        filename=filename_from_url(url, fallback=f"{site}-{post.get('id', 'image')}.jpg"),
                        metadata={"site": site, "tags": tags, "post": post},
                    )
                )
            )
            if max_files and len(results) >= max_files:
                break
        if not results:
            raise RuntimeError("Booru 没有下载到任何图片，请先预检确认标签。")
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


def media_asset_url(post: dict) -> str | None:
    media_asset = post.get("media_asset") or {}
    variants = media_asset.get("variants") or []
    if not isinstance(variants, list):
        return None
    preferred = ["original", "sample", "720x720", "preview"]
    by_type = {
        str(variant.get("type")): variant.get("url")
        for variant in variants
        if isinstance(variant, dict) and variant.get("url")
    }
    for key in preferred:
        if by_type.get(key):
            return by_type[key]
    return next(iter(by_type.values()), None)
