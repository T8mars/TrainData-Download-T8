from __future__ import annotations

import fnmatch
import json
from urllib.parse import quote
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from ..download import DownloadEngine
from ..models import DownloadRequest


class HuggingFaceDatasetPlugin:
    source_id = "huggingface_dataset"

    def __init__(self, engine: DownloadEngine, token: str | None = None) -> None:
        self.engine = engine
        self.token = token

    def list_files(self, repo_id: str, revision: str = "main") -> list[dict]:
        encoded_repo = quote(repo_id.strip(), safe="/")
        encoded_revision = quote(revision, safe="")
        url = f"https://huggingface.co/api/datasets/{encoded_repo}/tree/{encoded_revision}?recursive=true"
        headers = {"User-Agent": "anima-dataset-studio/0.1"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            with urlopen(Request(url, headers=headers), timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"Hugging Face 文件列表请求失败：{describe_http_error(exc)}") from exc
        if isinstance(data, dict) and "siblings" in data:
            return data["siblings"]
        return data

    def download(
        self,
        repo_id: str,
        *,
        revision: str = "main",
        include: list[str] | None = None,
        max_files: int | None = None,
    ):
        include = include or ["*"]
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        results = []
        encoded_repo = quote(repo_id.strip(), safe="/")
        encoded_revision = quote(revision, safe="")
        for entry in self.list_files(repo_id, revision=revision):
            path = entry.get("path")
            entry_type = entry.get("type")
            if not path or entry_type == "directory":
                continue
            if not any(fnmatch.fnmatch(path, pattern) for pattern in include):
                continue
            encoded_path = quote(path, safe="/")
            url = f"https://huggingface.co/datasets/{encoded_repo}/resolve/{encoded_revision}/{encoded_path}"
            results.append(
                self.engine.download(
                    DownloadRequest(
                        url=url,
                        source_id=self.source_id,
                        filename=path.replace("/", "__"),
                        headers=headers,
                        metadata={"repo_id": repo_id, "revision": revision, "path": path},
                    )
                )
            )
            if max_files and len(results) >= max_files:
                break
        if not results:
            raise RuntimeError(f"Hugging Face 仓库没有匹配文件：repo={repo_id}, include={', '.join(include)}")
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
