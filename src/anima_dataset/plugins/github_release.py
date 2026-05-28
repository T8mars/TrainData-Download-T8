from __future__ import annotations

import fnmatch
import json
import os
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from ..download import DownloadEngine
from ..models import DownloadRequest


class GitHubReleasePlugin:
    source_id = "github_release"

    def __init__(self, engine: DownloadEngine, token: str | None = None) -> None:
        self.engine = engine
        self.token = token or os.environ.get("GITHUB_TOKEN")

    def headers(self) -> dict[str, str]:
        headers = {
            "User-Agent": "anima-dataset-studio/0.1",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def release(self, repo: str, release: str = "latest") -> dict:
        owner, name = split_repo(repo)
        if release == "latest":
            url = f"https://api.github.com/repos/{quote(owner, safe='')}/{quote(name, safe='')}/releases/latest"
        else:
            url = f"https://api.github.com/repos/{quote(owner, safe='')}/{quote(name, safe='')}/releases/tags/{quote(release, safe='')}"
        try:
            with urlopen(Request(url, headers=self.headers()), timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if release == "latest" and exc.code == 404:
                releases = self.releases(repo)
                if releases:
                    return releases[0]
                return self.repository_archive_release(repo)
            raise RuntimeError(f"GitHub Release 请求失败：{describe_http_error(exc)}") from exc

    def releases(self, repo: str) -> list[dict]:
        owner, name = split_repo(repo)
        url = f"https://api.github.com/repos/{quote(owner, safe='')}/{quote(name, safe='')}/releases?per_page=20"
        try:
            with urlopen(Request(url, headers=self.headers()), timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"GitHub Release 列表请求失败：{describe_http_error(exc)}") from exc
        return data if isinstance(data, list) else []

    def repository_archive_release(self, repo: str) -> dict:
        owner, name = split_repo(repo)
        info = self.repository_info(repo)
        branch = info.get("default_branch") or "main"
        base = f"https://github.com/{owner}/{name}/archive/refs/heads/{quote(branch, safe='')}"
        return {
            "tag_name": branch,
            "name": f"{repo} source archive",
            "assets": [
                {
                    "name": f"{name}-{branch}.zip",
                    "size": None,
                    "browser_download_url": f"{base}.zip",
                    "content_type": "application/zip",
                    "synthetic": "source_zip",
                },
                {
                    "name": f"{name}-{branch}.tar.gz",
                    "size": None,
                    "browser_download_url": f"{base}.tar.gz",
                    "content_type": "application/gzip",
                    "synthetic": "source_tar",
                },
            ],
            "source_archive_fallback": True,
        }

    def repository_info(self, repo: str) -> dict:
        owner, name = split_repo(repo)
        url = f"https://api.github.com/repos/{quote(owner, safe='')}/{quote(name, safe='')}"
        try:
            with urlopen(Request(url, headers=self.headers()), timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"GitHub 仓库请求失败：{describe_http_error(exc)}") from exc

    def matching_assets(self, repo: str, release: str = "latest", include: list[str] | None = None) -> list[dict]:
        include = include or ["*"]
        data = self.release(repo, release=release)
        assets = data.get("assets") or []
        matches = [asset for asset in assets if any(fnmatch.fnmatch(asset.get("name", ""), pattern) for pattern in include)]
        if matches:
            return matches
        source_archives = [
            asset for asset in self.source_archive_assets(data)
            if any(fnmatch.fnmatch(asset.get("name", ""), pattern) for pattern in include)
        ]
        return source_archives

    def source_archive_assets(self, release: dict) -> list[dict]:
        assets = []
        tag = release.get("tag_name") or "source"
        if release.get("zipball_url"):
            assets.append({
                "name": f"source-{tag}.zip",
                "size": None,
                "browser_download_url": release["zipball_url"],
                "content_type": "application/zip",
                "synthetic": "release_source_zip",
            })
        if release.get("tarball_url"):
            assets.append({
                "name": f"source-{tag}.tar.gz",
                "size": None,
                "browser_download_url": release["tarball_url"],
                "content_type": "application/gzip",
                "synthetic": "release_source_tar",
            })
        return assets

    def preflight(self, repo: str, release: str = "latest", include: list[str] | None = None) -> dict:
        assets = self.matching_assets(repo, release=release, include=include)
        if not assets:
            raise RuntimeError("GitHub Release 没有匹配资产，请调整 repo/release/include。")
        return {
            "ok": True,
            "provider": "github",
            "count": len(assets),
            "samples": [{"name": asset.get("name"), "size": asset.get("size")} for asset in assets[:10]],
            "message": "GitHub Release 预检通过。"
        }

    def download(self, repo: str, release: str = "latest", include: list[str] | None = None, max_files: int | None = None):
        results = []
        for asset in self.matching_assets(repo, release=release, include=include):
            url = asset.get("browser_download_url")
            name = asset.get("name")
            if not url or not name:
                continue
            results.append(
                self.engine.download(
                    DownloadRequest(
                        url=url,
                        source_id=self.source_id,
                        filename=name,
                        headers={"Authorization": f"Bearer {self.token}"} if self.token else {},
                        metadata={"repo": repo, "release": release, "asset": asset},
                    )
                )
            )
            if max_files and len(results) >= max_files:
                break
        if not results:
            raise RuntimeError("GitHub Release 没有下载到任何文件，请先预检确认匹配规则。")
        return results


def split_repo(repo: str) -> tuple[str, str]:
    parts = repo.strip().strip("/").split("/")
    if len(parts) != 2 or not all(parts):
        raise ValueError("GitHub 仓库格式必须是 owner/repo")
    if parts[0].lower() == "owner" and parts[1].lower() == "repo":
        raise ValueError("请把 GitHub 模板 owner/repo 替换成真实仓库，例如 Fuyucch1/yolov8_animeface")
    return parts[0], parts[1]


def describe_http_error(exc: HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8", errors="replace").strip()
    except Exception:  # noqa: BLE001
        body = ""
    detail = f"HTTP {exc.code} {exc.reason}"
    if body:
        detail = f"{detail} - {body[:500]}"
    return detail
