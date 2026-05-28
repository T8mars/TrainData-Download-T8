from __future__ import annotations

import argparse
import fnmatch
import json
import os
import sys
import threading
import webbrowser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from socketserver import TCPServer
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .catalog import load_catalog
from .download import DownloadEngine
from .extract import Extractor
from .models import DownloadRequest
from .paths import ensure_workspace, workspace_root
from .plugins.booru import BooruPlugin
from .plugins.github_release import GitHubReleasePlugin
from .plugins.huggingface import HuggingFaceDatasetPlugin
from .plugins.internet_archive import InternetArchivePlugin
from .plugins.kaggle import KaggleDatasetPlugin
from .plugins.wikimedia import WikimediaCommonsPlugin
from .plugins.zenodo import ZenodoPlugin
from .storage import Database

DEFAULT_DATA_ROOT = Path(r"D:\zhenzhen-asset")


def parse_header_line(value: str | None) -> dict[str, str]:
    if not value:
        return {}
    if ":" in value:
        key, header_value = value.split(":", 1)
    elif "=" in value:
        key, header_value = value.split("=", 1)
    else:
        raise ValueError("请求头格式必须是 Key=Value 或 Key:Value")
    return {key.strip(): header_value.strip()}


def parse_patterns(value: Any, defaults: list[str] | None = None) -> list[str] | None:
    if value is None:
        return defaults
    if isinstance(value, list):
        patterns = [str(item).strip() for item in value if str(item).strip()]
    else:
        text = str(value).replace(";", ",").replace("\n", ",")
        patterns = [item.strip() for item in text.split(",") if item.strip()]
    return patterns or defaults


def parse_int(value: Any, default: int | None = None) -> int | None:
    if value is None or str(value).strip() == "":
        return default
    return int(value)


def row_to_dict(row: Any) -> dict[str, Any]:
    data = dict(row)
    for key in ("metadata_json",):
        if key in data:
            try:
                data[key.replace("_json", "")] = json.loads(data[key] or "{}")
            except json.JSONDecodeError:
                data[key.replace("_json", "")] = {}
            del data[key]
    return data


class AppContext:
    def __init__(self, root: Path) -> None:
        self.root = root
        ensure_workspace(root)
        self.db = Database(root / "manifests" / "anima_dataset.sqlite")
        self.engine = DownloadEngine(root, self.db)
        self.extractor = Extractor(root, self.db)
        self.activity: list[dict[str, str]] = []
        self.lock = threading.Lock()

    def log(self, level: str, message: str) -> None:
        with self.lock:
            self.activity.append({"level": level, "message": message})
            self.activity = self.activity[-200:]

    def summary(self) -> dict[str, Any]:
        with self.db.connect() as conn:
            job_counts = {
                row["status"]: row["count"]
                for row in conn.execute("select status, count(*) as count from jobs group by status")
            }
            asset_count = conn.execute("select count(*) as count from assets").fetchone()["count"]
        return {
            "root": str(self.root),
            "raw_dir": str(self.root / "data" / "raw"),
            "manifest": str(self.root / "manifests" / "anima_dataset.sqlite"),
            "python": sys.executable,
            "version": sys.version.split()[0],
            "job_counts": job_counts,
            "asset_count": asset_count,
            "activity": list(self.activity[-50:]),
        }


class AnimaGuiHandler(SimpleHTTPRequestHandler):
    server_version = "ZhenzhenDatasetDownloader/0.1"

    def __init__(self, *args: Any, directory: str | None = None, **kwargs: Any) -> None:
        web_dir = Path(__file__).resolve().parent / "web"
        super().__init__(*args, directory=str(web_dir), **kwargs)

    @property
    def app(self) -> AppContext:
        return self.server.app_context  # type: ignore[attr-defined]

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        self.app.log("http", format % args)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/status":
            self.send_json(self.app.summary())
            return
        if path == "/api/catalog":
            self.send_json(load_catalog())
            return
        if path == "/api/jobs":
            rows = [row_to_dict(row) for row in self.app.db.list_jobs(limit=50)]
            self.send_json({"jobs": rows})
            return
        if path == "/api/assets":
            rows = [row_to_dict(row) for row in self.app.db.list_assets(limit=80)]
            self.send_json({"assets": rows})
            return
        if path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            body = self.read_json()
            if path == "/api/init":
                ensure_workspace(self.app.root)
                self.app.log("info", "工作区已初始化")
                self.send_json({"ok": True, "message": "工作区已初始化"})
            elif path == "/api/root":
                new_root = workspace_root(required(body, "root"))
                self.server.app_context = AppContext(new_root)  # type: ignore[attr-defined]
                self.app.log("info", f"下载目录已切换到 {new_root}")
                self.send_json({"ok": True, "message": f"下载目录已切换到 {new_root}", "root": str(new_root)})
            elif path == "/api/download-url":
                self.spawn("直链下载", lambda: self.app.engine.download(
                    DownloadRequest(
                        url=required(body, "url"),
                        source_id=body.get("source_id") or "direct_url",
                        filename=body.get("filename") or None,
                        headers=parse_header_line(body.get("header")),
                        metadata={"ui": "download-url"},
                    )
                ))
                self.send_json({"ok": True, "message": "下载任务已开始"})
            elif path == "/api/import":
                target = Path(required(body, "path"))
                if target.is_dir():
                    records = self.app.engine.import_directory(target, source_id=body.get("source_id") or "local_import")
                else:
                    records = [self.app.engine.import_file(target, source_id=body.get("source_id") or "local_import")]
                self.app.log("info", f"已导入 {len(records)} 个素材")
                self.send_json({"ok": True, "count": len(records), "message": f"已导入 {len(records)} 个素材"})
            elif path == "/api/extract":
                records = self.app.extractor.extract(Path(required(body, "path")), source_id=body.get("source_id") or "extract")
                self.app.log("info", f"已解包 {len(records)} 个文件")
                self.send_json({"ok": True, "count": len(records), "message": f"已解包 {len(records)} 个文件"})
            elif path == "/api/hf":
                plugin = HuggingFaceDatasetPlugin(self.app.engine, token=body.get("token") or os.environ.get("HF_TOKEN"))
                include_list = parse_patterns(body.get("include"))
                max_files = parse_int(body.get("max_files"))
                self.spawn("Hugging Face 下载", lambda: plugin.download(required(body, "repo_id"), include=include_list, max_files=max_files))
                self.send_json({"ok": True, "message": "Hugging Face 下载任务已开始"})
            elif path == "/api/wikimedia":
                plugin = WikimediaCommonsPlugin(self.app.engine)
                mode = body.get("mode") or "category"
                text = required(body, "query")
                limit = int(body.get("limit") or 50)
                max_files = parse_int(body.get("max_files"))
                def task() -> None:
                    pages = plugin.search_files(text, limit=limit) if mode == "search" else plugin.category_files(text, limit=limit)
                    plugin.download_pages(pages, max_files=max_files)
                self.spawn("Wikimedia Commons 下载", task)
                self.send_json({"ok": True, "message": "Wikimedia 下载任务已开始"})
            elif path == "/api/ia":
                plugin = InternetArchivePlugin(self.app.engine)
                include_list = parse_patterns(body.get("include"))
                max_files = parse_int(body.get("max_files"))
                self.spawn("互联网档案馆下载", lambda: plugin.download(required(body, "item_id"), include=include_list, max_files=max_files))
                self.send_json({"ok": True, "message": "互联网档案馆下载任务已开始"})
            elif path == "/api/ia-search":
                plugin = InternetArchivePlugin(self.app.engine)
                include_list = parse_patterns(body.get("include"), defaults=["*.pdf", "*.zip", "*.cbz", "*.jpg", "*.png"])
                max_items = int(body.get("max_items") or 1)
                max_files_per_item = int(body.get("max_files_per_item") or 1)
                self.spawn(
                    "互联网档案馆搜索下载",
                    lambda: plugin.download_search(
                        required(body, "query"),
                        include=include_list,
                        max_items=max_items,
                        max_files_per_item=max_files_per_item,
                    ),
                )
                self.send_json({"ok": True, "message": "互联网档案馆搜索下载任务已开始"})
            elif path == "/api/kaggle":
                plugin = KaggleDatasetPlugin(self.app.engine, username=body.get("username"), key=body.get("key"))
                self.spawn("Kaggle 下载", lambda: plugin.download(required(body, "dataset"), filename=body.get("filename") or None))
                self.send_json({"ok": True, "message": "Kaggle 下载任务已开始"})
            elif path == "/api/zenodo":
                plugin = ZenodoPlugin(self.app.engine)
                include_list = parse_patterns(body.get("include"))
                self.spawn(
                    "Zenodo 下载",
                    lambda: plugin.download(
                        record_id=body.get("record_id") or None,
                        query=body.get("query") or None,
                        include=include_list,
                        max_records=parse_int(body.get("max_records"), 1) or 1,
                        max_files=parse_int(body.get("max_files"), 1) or 1,
                    ),
                )
                self.send_json({"ok": True, "message": "Zenodo 下载任务已开始"})
            elif path == "/api/github":
                plugin = GitHubReleasePlugin(self.app.engine, token=body.get("token") or None)
                include_list = parse_patterns(body.get("include"))
                self.spawn(
                    "GitHub Release 下载",
                    lambda: plugin.download(
                        required(body, "repo"),
                        release=body.get("release") or "latest",
                        include=include_list,
                        max_files=parse_int(body.get("max_files")),
                    ),
                )
                self.send_json({"ok": True, "message": "GitHub Release 下载任务已开始"})
            elif path == "/api/booru":
                plugin = BooruPlugin(self.app.engine)
                self.spawn(
                    "Booru 下载",
                    lambda: plugin.download(
                        body.get("site") or "safebooru",
                        required(body, "tags"),
                        limit=parse_int(body.get("limit"), 20) or 20,
                        max_files=parse_int(body.get("max_files")),
                    ),
                )
                self.send_json({"ok": True, "message": "Booru 下载任务已开始"})
            elif path == "/api/preflight":
                self.send_json({"ok": True, "preflight": self.preflight(body)})
            else:
                self.send_error(HTTPStatus.NOT_FOUND, "未知 API 路由")
        except Exception as exc:  # noqa: BLE001 - API returns structured error.
            self.app.log("error", str(exc))
            self.send_json({"ok": False, "error": str(exc)}, status=500)

    def spawn(self, label: str, func: Any) -> None:
        def runner() -> None:
            self.app.log("info", f"{label}已开始")
            try:
                result = func()
                self.log_task_result(label, result)
            except Exception as exc:  # noqa: BLE001
                self.app.log("error", f"{label}失败：{exc}")

        threading.Thread(target=runner, daemon=True).start()

    def log_task_result(self, label: str, result: Any) -> None:
        if isinstance(result, list):
            count = len(result)
            failed = [item for item in result if getattr(item, "status", None) == "FAILED"]
            if count and len(failed) == count:
                error = getattr(failed[-1], "error", None) or "全部下载结果失败"
                raise RuntimeError(error)
            suffix = f"{count} 个结果"
            if failed:
                suffix = f"{suffix}，{len(failed)} 个失败"
            self.app.log("info", f"{label}已完成（{suffix}）")
            return
        if getattr(result, "status", None) == "FAILED":
            raise RuntimeError(getattr(result, "error", None) or "下载失败")
        self.app.log("info", f"{label}已完成（1 个结果）")

    def preflight(self, body: dict[str, Any]) -> dict[str, Any]:
        provider = body.get("provider") or body.get("tab")
        fields = body.get("fields") if isinstance(body.get("fields"), dict) else body
        if provider == "direct":
            url = required(fields, "url")
            headers = {
                "User-Agent": "anima-dataset-studio/0.1",
                "Accept": "*/*",
                **parse_header_line(fields.get("header")),
            }
            try:
                request = Request(url, headers=headers, method="HEAD")
                response = urlopen(request, timeout=30)
            except Exception:  # noqa: BLE001 - Some file hosts reject HEAD.
                request = Request(url, headers={**headers, "Range": "bytes=0-0"})
                response = urlopen(request, timeout=30)
            with response:
                return {
                    "provider": provider,
                    "count": 1,
                    "samples": [{"name": fields.get("filename") or url.split("/")[-1], "size": response.headers.get("Content-Length")}],
                    "message": "直链可访问。"
                }
        if provider == "hf":
            plugin = HuggingFaceDatasetPlugin(self.app.engine, token=fields.get("token") or os.environ.get("HF_TOKEN"))
            include = parse_patterns(fields.get("include"), defaults=["*"]) or ["*"]
            matches = [
                entry for entry in plugin.list_files(required(fields, "repo_id"))
                if entry.get("path") and entry.get("type") != "directory" and any(fnmatch.fnmatch(entry.get("path"), pattern) for pattern in include)
            ]
            if not matches:
                raise RuntimeError(f"Hugging Face 没有匹配文件：{', '.join(include)}")
            return {"provider": provider, "count": len(matches), "samples": [{"name": item.get("path"), "size": item.get("size")} for item in matches[:10]], "message": "Hugging Face 预检通过。"}
        if provider == "wikimedia":
            plugin = WikimediaCommonsPlugin(self.app.engine)
            mode = fields.get("mode") or "category"
            limit = parse_int(fields.get("limit"), 20) or 20
            pages = plugin.search_files(required(fields, "query"), limit=limit) if mode == "search" else plugin.category_files(required(fields, "query"), limit=limit)
            samples = []
            for page in pages[:10]:
                info = (page.get("imageinfo") or [{}])[0]
                samples.append({"name": page.get("title"), "url": info.get("url"), "size": info.get("size")})
            if not samples:
                raise RuntimeError("Wikimedia 预检没有找到文件。")
            return {"provider": provider, "count": len(pages), "samples": samples, "message": "Wikimedia 预检通过。"}
        if provider == "ia":
            plugin = InternetArchivePlugin(self.app.engine)
            _, files = plugin.matching_files(required(fields, "item_id"), include=parse_patterns(fields.get("include"), defaults=["*"]))
            if not files:
                raise RuntimeError("Internet Archive item 没有匹配文件。")
            return {"provider": provider, "count": len(files), "samples": [{"name": item.get("name"), "size": item.get("size"), "format": item.get("format")} for item in files[:10]], "message": "Internet Archive 预检通过。"}
        if provider == "iaSearch":
            plugin = InternetArchivePlugin(self.app.engine)
            include = parse_patterns(fields.get("include"), defaults=["*.pdf", "*.zip", "*.cbz", "*.jpg", "*.png"])
            samples = []
            for doc in plugin.search(required(fields, "query"), rows=10):
                item_id = doc.get("identifier")
                if not item_id:
                    continue
                try:
                    _, files = plugin.matching_files(item_id, include=include)
                except Exception:  # noqa: BLE001
                    continue
                for file in files[:3]:
                    samples.append({"item": item_id, "name": file.get("name"), "size": file.get("size")})
                if samples:
                    break
            if not samples:
                raise RuntimeError("Internet Archive 搜索没有找到匹配文件。")
            return {"provider": provider, "count": len(samples), "samples": samples, "message": "Internet Archive 搜索预检通过。"}
        if provider == "kaggle":
            return KaggleDatasetPlugin(self.app.engine, username=fields.get("username"), key=fields.get("key")).preflight(required(fields, "dataset"))
        if provider == "zenodo":
            return ZenodoPlugin(self.app.engine).preflight(
                record_id=fields.get("record_id") or None,
                query=fields.get("query") or None,
                include=parse_patterns(fields.get("include")),
                max_records=parse_int(fields.get("max_records"), 1) or 1,
            )
        if provider == "github":
            return GitHubReleasePlugin(self.app.engine, token=fields.get("token") or None).preflight(
                required(fields, "repo"),
                release=fields.get("release") or "latest",
                include=parse_patterns(fields.get("include")),
            )
        if provider == "booru":
            return BooruPlugin(self.app.engine).preflight(
                fields.get("site") or "safebooru",
                required(fields, "tags"),
                limit=parse_int(fields.get("limit"), 20) or 20,
            )
        raise ValueError(f"暂不支持预检来源：{provider}")

    def read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def send_json(self, payload: dict[str, Any], *, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def required(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if value is None or str(value).strip() == "":
        raise ValueError(f"缺少必填字段：{key}")
    return str(value).strip()


def make_server(root: Path, host: str, port: int) -> ThreadingHTTPServer:
    app_context = AppContext(root)
    last_error: Exception | None = None
    for candidate in range(port, port + 20):
        try:
            server = ThreadingHTTPServer((host, candidate), AnimaGuiHandler)
            server.app_context = app_context  # type: ignore[attr-defined]
            return server
        except OSError as exc:
            last_error = exc
            continue
    raise OSError(f"无法绑定端口 {port} 到 {port + 19}：{last_error}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="anima-dataset-gui")
    parser.add_argument("--root", default=None)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8422)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args(argv)

    root = workspace_root(args.root or os.environ.get("ANIMA_DATASET_ROOT") or DEFAULT_DATA_ROOT)
    server = make_server(root, args.host, args.port)
    host, port = server.server_address
    url = f"http://{host}:{port}/"
    print(f"Zhenzhen Training Dataset Downloader GUI: {url}")
    print(f"Root: {root}")
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server...")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
