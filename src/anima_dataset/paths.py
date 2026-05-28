from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlparse


def workspace_root(root: str | Path | None = None) -> Path:
    return Path(root or ".").resolve()


def ensure_workspace(root: Path) -> None:
    for relative in (
        "data/raw",
        "data/quarantine",
        "data/extracted",
        "data/processed",
        "data/exports",
        "manifests",
        "reports/license_audit",
        "reports/dataset_cards",
        "reports/license_snapshots",
        "sources",
    ):
        (root / relative).mkdir(parents=True, exist_ok=True)


def safe_name(value: str, fallback: str = "download") -> str:
    value = unquote(value).strip().replace("\\", "/").split("/")[-1] or fallback
    value = re.sub(r"[^A-Za-z0-9._() -]+", "_", value)
    value = value.strip(" .")
    return value or fallback


def filename_from_url(url: str, fallback: str = "download") -> str:
    parsed = urlparse(url)
    return safe_name(parsed.path, fallback=fallback)


def source_dir_name(source_id: str) -> str:
    return safe_name(source_id, fallback="source").replace(" ", "_")


def assert_within(path: Path, root: Path) -> None:
    path.resolve().relative_to(root.resolve())
