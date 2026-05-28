from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from ..download import DownloadEngine
from ..models import DownloadRequest
from ..paths import safe_name


class KaggleDatasetPlugin:
    source_id = "kaggle_dataset"
    api_base = "https://www.kaggle.com/api/v1"

    def __init__(self, engine: DownloadEngine, username: str | None = None, key: str | None = None) -> None:
        self.engine = engine
        self.username, self.key = self._credentials(username, key)

    def _credentials(self, username: str | None, key: str | None) -> tuple[str | None, str | None]:
        username = username or os.environ.get("KAGGLE_USERNAME")
        key = key or os.environ.get("KAGGLE_KEY")
        if username and key:
            return username, key
        config_path = Path.home() / ".kaggle" / "kaggle.json"
        if config_path.exists():
            try:
                config = json.loads(config_path.read_text(encoding="utf-8"))
                return config.get("username"), config.get("key")
            except json.JSONDecodeError:
                return username, key
        return username, key

    def auth_headers(self) -> dict[str, str]:
        if not self.username or not self.key:
            raise RuntimeError("Kaggle 需要配置 kaggle.json 或 KAGGLE_USERNAME/KAGGLE_KEY")
        token = base64.b64encode(f"{self.username}:{self.key}".encode("utf-8")).decode("ascii")
        return {"Authorization": f"Basic {token}", "User-Agent": "anima-dataset-studio/0.1"}

    def info(self, dataset: str) -> dict:
        owner, name = split_dataset(dataset)
        url = f"{self.api_base}/datasets/view/{quote(owner, safe='')}/{quote(name, safe='')}"
        try:
            with urlopen(Request(url, headers=self.auth_headers()), timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"Kaggle 数据集信息请求失败：{describe_http_error(exc)}") from exc

    def preflight(self, dataset: str) -> dict:
        info = self.info(dataset)
        files = info.get("files") or []
        return {
            "ok": True,
            "provider": "kaggle",
            "title": info.get("title") or dataset,
            "count": len(files) or 1,
            "requiresAuth": True,
            "samples": [
                {"name": file.get("name"), "size": file.get("totalBytes")}
                for file in files[:10]
                if file.get("name")
            ],
            "message": "Kaggle 预检通过，将下载数据集 zip。"
        }

    def download(self, dataset: str, *, filename: str | None = None):
        owner, name = split_dataset(dataset)
        url = f"{self.api_base}/datasets/download/{quote(owner, safe='')}/{quote(name, safe='')}"
        filename = filename or f"{safe_name(owner)}__{safe_name(name)}.zip"
        return self.engine.download(
            DownloadRequest(
                url=url,
                source_id=self.source_id,
                filename=filename,
                headers=self.auth_headers(),
                metadata={"dataset": dataset},
            )
        )


def split_dataset(dataset: str) -> tuple[str, str]:
    parts = dataset.strip().strip("/").split("/")
    if len(parts) != 2 or not all(parts):
        raise ValueError("Kaggle 数据集格式必须是 owner/dataset")
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
