from __future__ import annotations

import argparse
import os
from pathlib import Path

from .download import DownloadEngine
from .extract import Extractor
from .models import DownloadRequest
from .paths import ensure_workspace, workspace_root
from .plugins.huggingface import HuggingFaceDatasetPlugin
from .plugins.internet_archive import InternetArchivePlugin
from .plugins.wikimedia import WikimediaCommonsPlugin
from .storage import Database


def make_context(root_arg: str | None):
    root = workspace_root(root_arg or os.environ.get("ANIMA_DATASET_ROOT"))
    ensure_workspace(root)
    db = Database(root / "manifests" / "anima_dataset.sqlite")
    return root, db, DownloadEngine(root, db)


def parse_headers(values: list[str] | None) -> dict[str, str]:
    headers: dict[str, str] = {}
    for value in values or []:
        if ":" in value:
            key, header_value = value.split(":", 1)
        elif "=" in value:
            key, header_value = value.split("=", 1)
        else:
            raise SystemExit(f"invalid header, use Key=Value or Key:Value: {value}")
        headers[key.strip()] = header_value.strip()
    return headers


def print_results(results) -> None:
    for result in results if isinstance(results, list) else [results]:
        print(f"{result.status}\t{result.target_path}\t{result.sha256 or ''}\t{result.error or ''}")


def cmd_init(args) -> None:
    root, _, _ = make_context(args.root)
    print(f"initialized {root}")


def cmd_download_url(args) -> None:
    _, _, engine = make_context(args.root)
    result = engine.download(
        DownloadRequest(
            url=args.url,
            source_id=args.source,
            filename=args.filename,
            expected_sha256=args.sha256,
            headers=parse_headers(args.header),
            metadata={"cli": "download-url"},
        )
    )
    print_results(result)


def cmd_download_list(args) -> None:
    _, _, engine = make_context(args.root)
    urls = [
        line.strip()
        for line in Path(args.file).read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    results = [
        engine.download(
            DownloadRequest(
                url=url,
                source_id=args.source,
                headers=parse_headers(args.header),
                metadata={"cli": "download-list", "list_file": args.file},
            )
        )
        for url in urls
    ]
    print_results(results)


def cmd_import(args) -> None:
    _, _, engine = make_context(args.root)
    path = Path(args.path)
    if path.is_dir():
        records = engine.import_directory(path, source_id=args.source)
    else:
        records = [engine.import_file(path, source_id=args.source)]
    for record in records:
        print(f"{record.status}\t{record.local_path}\t{record.sha256}")


def cmd_extract(args) -> None:
    root, db, _ = make_context(args.root)
    records = Extractor(root, db).extract(Path(args.path), source_id=args.source)
    for record in records:
        print(f"{record.status}\t{record.local_path}\t{record.sha256}")


def cmd_hf(args) -> None:
    _, _, engine = make_context(args.root)
    token = args.token or (os.environ.get(args.token_env) if args.token_env else None)
    plugin = HuggingFaceDatasetPlugin(engine, token=token)
    results = plugin.download(args.repo_id, revision=args.revision, include=args.include, max_files=args.max_files)
    print_results(results)


def cmd_wikimedia(args) -> None:
    _, _, engine = make_context(args.root)
    plugin = WikimediaCommonsPlugin(engine)
    if args.category:
        pages = plugin.category_files(args.category, limit=args.limit)
    elif args.search:
        pages = plugin.search_files(args.search, limit=args.limit)
    else:
        raise SystemExit("use --category or --search")
    results = plugin.download_pages(pages, max_files=args.max_files)
    print_results(results)


def cmd_ia(args) -> None:
    _, _, engine = make_context(args.root)
    plugin = InternetArchivePlugin(engine)
    results = plugin.download(args.item_id, include=args.include, max_files=args.max_files)
    print_results(results)


def cmd_jobs(args) -> None:
    _, db, _ = make_context(args.root)
    for row in db.list_jobs(limit=args.limit):
        print(f"{row['status']}\t{row['source_id']}\t{row['target_path']}\t{row['error'] or ''}")


def cmd_assets(args) -> None:
    _, db, _ = make_context(args.root)
    for row in db.list_assets(limit=args.limit):
        print(f"{row['status']}\t{row['source_id']}\t{row['local_path']}\t{row['sha256']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="anima-dataset")
    parser.add_argument("--root", help="Workspace root. Defaults to current directory.")
    sub = parser.add_subparsers(required=True)

    p = sub.add_parser("init")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("download-url")
    p.add_argument("url")
    p.add_argument("--source", default="direct_url")
    p.add_argument("--filename")
    p.add_argument("--sha256")
    p.add_argument("--header", action="append", help="Transient request header, e.g. Authorization=Bearer ...")
    p.set_defaults(func=cmd_download_url)

    p = sub.add_parser("download-list")
    p.add_argument("file")
    p.add_argument("--source", default="direct_url")
    p.add_argument("--header", action="append")
    p.set_defaults(func=cmd_download_list)

    p = sub.add_parser("import")
    p.add_argument("path")
    p.add_argument("--source", default="local_import")
    p.set_defaults(func=cmd_import)

    p = sub.add_parser("extract")
    p.add_argument("path")
    p.add_argument("--source", default="extract")
    p.set_defaults(func=cmd_extract)

    p = sub.add_parser("hf")
    p.add_argument("repo_id")
    p.add_argument("--revision", default="main")
    p.add_argument("--include", action="append", default=None)
    p.add_argument("--max-files", type=int)
    p.add_argument("--token")
    p.add_argument("--token-env", default="HF_TOKEN")
    p.set_defaults(func=cmd_hf)

    p = sub.add_parser("wikimedia")
    p.add_argument("--category")
    p.add_argument("--search")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--max-files", type=int)
    p.set_defaults(func=cmd_wikimedia)

    p = sub.add_parser("ia")
    p.add_argument("item_id")
    p.add_argument("--include", action="append", default=None)
    p.add_argument("--max-files", type=int)
    p.set_defaults(func=cmd_ia)

    p = sub.add_parser("jobs")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_jobs)

    p = sub.add_parser("assets")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_assets)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
