from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class DownloadRequest:
    url: str
    source_id: str = "direct_url"
    filename: str | None = None
    expected_sha256: str | None = None
    headers: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DownloadResult:
    job_id: str
    status: str
    target_path: Path
    sha256: str | None
    bytes_done: int
    error: str | None = None


@dataclass(frozen=True)
class AssetRecord:
    asset_id: str
    source_id: str
    source_url: str
    local_path: Path
    sha256: str
    status: str = "DOWNLOADED"
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
