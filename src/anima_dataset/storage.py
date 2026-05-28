from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import AssetRecord, utc_now


class Database:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                create table if not exists jobs (
                    job_id text primary key,
                    source_id text not null,
                    url text not null,
                    target_path text not null,
                    status text not null,
                    bytes_total integer,
                    bytes_done integer not null default 0,
                    sha256 text,
                    error text,
                    metadata_json text not null default '{}',
                    created_at text not null,
                    updated_at text not null
                )
                """
            )
            conn.execute(
                """
                create table if not exists assets (
                    asset_id text primary key,
                    source_id text not null,
                    source_url text not null,
                    local_path text not null,
                    sha256 text not null,
                    status text not null,
                    metadata_json text not null default '{}',
                    created_at text not null
                )
                """
            )

    def upsert_job(
        self,
        *,
        job_id: str,
        source_id: str,
        url: str,
        target_path: Path,
        status: str,
        bytes_total: int | None = None,
        bytes_done: int = 0,
        sha256: str | None = None,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        now = utc_now()
        with self.connect() as conn:
            conn.execute(
                """
                insert into jobs (
                    job_id, source_id, url, target_path, status, bytes_total,
                    bytes_done, sha256, error, metadata_json, created_at, updated_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                on conflict(job_id) do update set
                    status=excluded.status,
                    bytes_total=excluded.bytes_total,
                    bytes_done=excluded.bytes_done,
                    sha256=excluded.sha256,
                    error=excluded.error,
                    metadata_json=excluded.metadata_json,
                    updated_at=excluded.updated_at
                """,
                (
                    job_id,
                    source_id,
                    url,
                    str(target_path),
                    status,
                    bytes_total,
                    bytes_done,
                    sha256,
                    error,
                    json.dumps(metadata or {}, ensure_ascii=False),
                    now,
                    now,
                ),
            )

    def update_job(
        self,
        job_id: str,
        *,
        status: str,
        bytes_total: int | None = None,
        bytes_done: int = 0,
        sha256: str | None = None,
        error: str | None = None,
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                update jobs
                set status=?, bytes_total=?, bytes_done=?, sha256=?, error=?, updated_at=?
                where job_id=?
                """,
                (status, bytes_total, bytes_done, sha256, error, utc_now(), job_id),
            )

    def record_asset(self, asset: AssetRecord) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                insert into assets (
                    asset_id, source_id, source_url, local_path, sha256,
                    status, metadata_json, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?)
                on conflict(asset_id) do update set
                    source_id=excluded.source_id,
                    source_url=excluded.source_url,
                    local_path=excluded.local_path,
                    status=excluded.status,
                    metadata_json=excluded.metadata_json
                """,
                (
                    asset.asset_id,
                    asset.source_id,
                    asset.source_url,
                    str(asset.local_path),
                    asset.sha256,
                    asset.status,
                    json.dumps(asset.metadata, ensure_ascii=False),
                    asset.created_at,
                ),
            )

    def list_jobs(self, limit: int = 20) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return list(
                conn.execute(
                    "select * from jobs order by updated_at desc limit ?",
                    (limit,),
                )
            )

    def list_assets(self, limit: int = 20) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return list(
                conn.execute(
                    "select * from assets order by created_at desc limit ?",
                    (limit,),
                )
            )
