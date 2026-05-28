from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

PROJECT_ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
CATALOG_ROOT = PROJECT_ROOT / "sources"

ENDPOINTS = {
    "direct": "/api/download-url",
    "hf": "/api/hf",
    "wikimedia": "/api/wikimedia",
    "ia": "/api/ia",
    "iaSearch": "/api/ia-search",
    "kaggle": "/api/kaggle",
    "zenodo": "/api/zenodo",
    "github": "/api/github",
    "booru": "/api/booru",
    "local": "/api/import",
}

TYPE_LABELS = {
    "direct": "直链",
    "hf": "Hugging Face",
    "wikimedia": "Wikimedia",
    "ia": "Internet Archive Item",
    "iaSearch": "Internet Archive 搜索",
    "kaggle": "Kaggle",
    "zenodo": "Zenodo",
    "github": "GitHub Releases",
    "booru": "Booru",
    "local": "本地导入",
}


def load_catalog() -> dict[str, Any]:
    providers = read_json(CATALOG_ROOT / "providers" / "providers.json")
    entries = read_json(CATALOG_ROOT / "catalogs" / "base.json")
    generators = read_json(CATALOG_ROOT / "catalogs" / "generators.json")
    entries = unique_entries([*entries, *generated_entries(generators)])
    normalized = [normalize_entry(entry) for entry in entries]
    return {
        "providers": providers,
        "items": normalized,
        "count": len(normalized),
        "groups": sorted({item.get("group", "未分类") for item in normalized}),
        "types": sorted({item.get("provider") for item in normalized}),
    }


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_entry(entry: dict[str, Any]) -> dict[str, Any]:
    item = dict(entry)
    provider = item.get("provider") or item.get("tab") or "direct"
    item["provider"] = provider
    item["tab"] = provider
    item.setdefault("badge", TYPE_LABELS.get(provider, provider))
    item.setdefault("group", "未分类")
    item.setdefault("task", [])
    item.setdefault("fields", {})
    item.setdefault("endpoint", ENDPOINTS.get(provider, "/api/download-url"))
    item.setdefault("sourceUrl", source_url(provider, item["fields"]))
    return item


def source_url(provider: str, fields: dict[str, Any]) -> str:
    if provider == "hf" and fields.get("repo_id"):
        return f"https://huggingface.co/datasets/{fields['repo_id']}"
    if provider == "ia" and fields.get("item_id"):
        return f"https://archive.org/details/{fields['item_id']}"
    if provider == "iaSearch" and fields.get("query"):
        return f"https://archive.org/search?query={quote(str(fields['query']))}"
    if provider == "wikimedia" and fields.get("query") and fields.get("mode") == "category":
        return f"https://commons.wikimedia.org/wiki/Category:{quote(str(fields['query']).replace(' ', '_'), safe='()_')}"
    if provider == "wikimedia" and fields.get("query"):
        return f"https://commons.wikimedia.org/w/index.php?search={quote(str(fields['query']))}&title=Special:MediaSearch&type=image"
    if provider == "kaggle" and fields.get("dataset"):
        return f"https://www.kaggle.com/datasets/{fields['dataset']}"
    if provider == "zenodo" and fields.get("record_id"):
        return f"https://zenodo.org/records/{fields['record_id']}"
    if provider == "github" and fields.get("repo"):
        return f"https://github.com/{fields['repo']}"
    return str(fields.get("url") or "#")


def generated_entries(config: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for entry in config.get("direct_urls", []):
        title = entry["title"]
        filename = entry.get("filename") or Path(str(entry["url"])).name
        items.append({
            "id": entry.get("id") or f"direct-{slug(title)}",
            "provider": "direct",
            "group": entry.get("group", "直链数据集"),
            "task": entry.get("task", ["direct-download"]),
            "title": title,
            "badge": entry.get("badge", "直链"),
            "description": entry.get("description", "可直接下载的公开文件入口。"),
            "fields": {"url": entry["url"], "filename": filename, "header": entry.get("header", "")},
            "sourceUrl": entry.get("sourceUrl", entry["url"]),
            "format": entry.get("format", []),
            "size_hint": entry.get("size_hint"),
        })
    for entry in config.get("kaggle_datasets", []):
        dataset = entry["dataset"]
        owner, name = dataset.split("/", 1)
        items.append({
            "id": entry.get("id") or f"kaggle-{slug(dataset)}",
            "provider": "kaggle",
            "group": entry.get("group", "Kaggle 数据集"),
            "task": entry.get("task", ["kaggle-dataset"]),
            "title": entry.get("title", dataset),
            "badge": entry.get("badge", "Kaggle · 需账号密钥"),
            "description": entry.get("description", "Kaggle 数据集入口，需要本机配置 kaggle.json 或环境变量。"),
            "fields": {"dataset": dataset, "filename": entry.get("filename", f"{safe_file_part(owner)}__{safe_file_part(name)}.zip")},
            "sourceUrl": f"https://www.kaggle.com/datasets/{dataset}",
            "requires_token": True,
            "format": entry.get("format", ["zip"]),
            "size_hint": entry.get("size_hint"),
        })
    for entry in config.get("github_releases", []):
        repo = entry["repo"]
        items.append({
            "id": entry.get("id") or f"github-{slug(repo)}",
            "provider": "github",
            "group": entry.get("group", "GitHub Release"),
            "task": entry.get("task", ["release-asset"]),
            "title": entry.get("title", repo),
            "badge": entry.get("badge", "GitHub Releases"),
            "description": entry.get("description", "GitHub Release 资产入口，适合下载公开发布的 zip/tar/模型/工具资产。"),
            "fields": {
                "repo": repo,
                "release": entry.get("release", "latest"),
                "include": entry.get("include", "*.zip,*.tar.gz,*.7z,*.txt,*.json,*.onnx,*.pt,*.safetensors"),
                "max_files": str(entry.get("max_files", 1)),
            },
            "sourceUrl": f"https://github.com/{repo}/releases",
            "format": entry.get("format", ["release"]),
        })
    for subject, subject_group in config.get("wikimedia_subjects", []):
        for qualifier, qualifier_group in config.get("wikimedia_qualifiers", []):
            query = f"{qualifier} {subject}"
            items.append({
                "id": f"wm-search-{slug(query)}",
                "provider": "wikimedia",
                "group": f"{subject_group} / {qualifier_group}",
                "task": ["search", "open-image"],
                "title": f"{subject} · {qualifier}",
                "badge": "Wikimedia 搜索",
                "description": f"Wikimedia 关键词入口：{query}。适合先下载少量开放图像做筛选和训练管线测试。",
                "fields": {"mode": "search", "query": query, "limit": "50", "max_files": "3"},
                "format": ["image"],
            })
    for term, group in config.get("ia_terms", []):
        for media_type in ("mediatype:texts", "mediatype:image", "collection:comics", "collection:additional_collections"):
            query = f"{term} {media_type}"
            items.append({
                "id": f"ia-search-{slug(query)}",
                "provider": "iaSearch",
                "group": group,
                "task": ["archive-search"],
                "title": f"{term} · {media_type}",
                "badge": "Internet Archive 搜索",
                "description": f"Internet Archive 搜索入口：{query}。预检会先看候选条目是否有匹配文件。",
                "fields": {"query": query, "include": "*.pdf,*.zip,*.cbz,*.jpg,*.png", "max_items": "1", "max_files_per_item": "1"},
                "format": ["pdf", "zip", "image"],
            })
    for site in config.get("booru_sites", []):
        for tags, group in config.get("booru_tags", []):
            site_tags = booru_tags_for_site(site, tags)
            items.append({
                "id": f"booru-{site}-{slug(site_tags)}",
                "provider": "booru",
                "group": f"Booru 标签图像 / {group}",
                "task": ["tagged-image"],
                "title": f"{site} · {site_tags}",
                "badge": f"Booru · {site}",
                "description": f"{site} 标签搜索：{site_tags}。默认只下载少量图片做管线测试。",
                "fields": {"site": site, "tags": site_tags, "limit": "20", "max_files": "3"},
                "sourceUrl": booru_url(site, site_tags),
                "format": ["image"],
            })
    for query, group in config.get("zenodo_queries", []):
        items.append({
            "id": f"zenodo-search-{slug(query)}",
            "provider": "zenodo",
            "group": group,
            "task": ["research", "search"],
            "title": f"Zenodo · {query}",
            "badge": "Zenodo 搜索",
            "description": f"Zenodo 公开记录搜索：{query}，默认下载第一个匹配记录里的一个文件。",
            "fields": {"query": query, "include": "*.zip,*.tar,*.jpg,*.png,*.pdf", "max_records": "1", "max_files": "1"},
            "format": ["zip", "image", "pdf"],
        })
    return items


def booru_url(site: str, tags: str) -> str:
    if site == "danbooru":
        return f"https://danbooru.donmai.us/posts?tags={quote(tags)}"
    if site == "konachan":
        return f"https://konachan.com/post?tags={quote(tags)}"
    if site == "yandere":
        return f"https://yande.re/post?tags={quote(tags)}"
    host = "safebooru.org" if site == "safebooru" else "gelbooru.com"
    return f"https://{host}/index.php?page=post&s=list&tags={quote(tags)}"


def booru_tags_for_site(site: str, tags: str) -> str:
    if site == "danbooru":
        return tags.replace("rating:general", "rating:g")
    if site in {"konachan", "yandere"}:
        return tags.replace("rating:general", "rating:safe")
    return tags


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def safe_file_part(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")


def unique_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for entry in entries:
        entry_id = str(entry.get("id") or slug(entry.get("title", "item")))
        if entry_id in seen:
            continue
        seen.add(entry_id)
        unique.append(entry)
    return unique
