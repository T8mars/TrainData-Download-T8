# 贞贞的训练集下载器

面向 anime 模型研究的下载优先训练集下载器。

项目地址：[https://github.com/T8mars/TrainData-Download-T8](https://github.com/T8mars/TrainData-Download-T8)

这是一个带中文前端的本地数据集下载工作台，也保留 Python CLI 和可复用下载核心。它会把文件放入本地数据仓库，并记录断点下载、哈希、解包结果和 SQLite manifest。

## Quick Start

```powershell
python -m anima_dataset.cli --root E:\manga-resource init
python -m anima_dataset.cli --root E:\manga-resource download-url https://example.com/file.zip
python -m anima_dataset.cli --root E:\manga-resource import E:\some-local-dataset
python -m anima_dataset.cli --root E:\manga-resource extract E:\manga-resource\data\raw\direct_url\file.zip
```

## 启动器

推荐双击这个文件打开中文前端，全程不显示黑色命令行窗口：

```text
启动贞贞的训练集下载器.vbs
```

备用启动器：

```text
launch.bat
```

启动器会后台启动本地服务并自动打开浏览器。源码/VBS 启动器的默认下载目录是 `D:\zhenzhen-asset`，也可以在页面顶部的“自定义下载目录”里改成其他路径。`launch.bat` 不再显示“按任意键继续”，如果失败，会把日志写到 `logs/gui_stdout.log` 和 `logs/gui_stderr.log`。旧的 `启动ANIMA数据集工作台.vbs` 仍保留兼容。

旧版命令行菜单仍保留备用：

```text
launch_cli.bat
```

只启动 GUI 服务、不自动打开浏览器：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\launch_gui.ps1 -NoOpen
```

指定下载目录启动：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\launch_gui.ps1 -DataRoot "D:\zhenzhen-asset"
```

前台调试模式：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\launch_gui.ps1 -Foreground
```

启动器会自动设置 `PYTHONPATH`，使用当前文件夹作为项目根目录，并跳过 WindowsApps 里的假 `python.exe`。如需指定解释器，可设置 `ANIMA_PYTHON`。

## Source Plugins

前端内置 1400+ 个来源入口，并支持按关键词、分类、来源类型分页筛选。推荐数据集每页显示 9 个，桌面布局为 3 行。来源类型包括直链、Hugging Face、Wikimedia Commons、Internet Archive item、Internet Archive 搜索、Kaggle、Zenodo、GitHub Release、Booru 和本地导入。

前端每个推荐卡片都有三个动作：

- `填入参数`：把该来源的默认参数写入当前下载表单。
- `预检`：先列出命中文件或样本，不立即下载。
- `下载测试`：按默认小批量参数创建下载任务。

数据源目录是可扩展的 JSON：

- `sources/providers/providers.json`：来源类型、中文标签和授权提示。
- `sources/catalogs/base.json`：人工维护的重点数据集入口。
- `sources/catalogs/generators.json`：按关键词、站点、标签、直链 URL、Kaggle slug、GitHub release 批量生成来源入口。

新增来源时优先改 JSON；只有接入全新站点 API 时才需要新增 `src/anima_dataset/plugins/*.py` 插件和 `/api/...` 路由。

当前内置的直链下载入口覆盖 OpenGameArt zip/PNG 角色包、Internet Archive 北斋漫画 PDF、公版漫画扫描，以及 Wikimedia 公版 JPG。直链入口可以直接通过“预检”确认文件可访问，不需要账号。

```powershell
# Batch direct URLs
python -m anima_dataset.cli --root E:\manga-resource download-list examples\url_list.txt

# Direct URL with transient headers for authorized academic downloads
python -m anima_dataset.cli --root E:\manga-resource download-url https://example.edu/dataset/file.zip --header "Authorization=Bearer YOUR_TOKEN"

# Hugging Face dataset files by pattern
python -m anima_dataset.cli --root E:\manga-resource hf deepghs/anime-bg --include "*.tar" --max-files 1

# Wikimedia Commons by category
python -m anima_dataset.cli --root E:\manga-resource wikimedia --category "Katsushika Hokusai" --max-files 5

# Internet Archive item files by pattern
python -m anima_dataset.cli --root E:\manga-resource ia hokusaimanga04kats --include "*.pdf" --max-files 1
```

Kaggle、Zenodo、GitHub Release、Booru 目前优先通过中文前端使用。Kaggle 需要 `C:\Users\<你>\.kaggle\kaggle.json`，或设置 `KAGGLE_USERNAME` / `KAGGLE_KEY`；GitHub 可选 `GITHUB_TOKEN`；Hugging Face 可选 `HF_TOKEN` 或表单 token。

## Key / Token 配置

Hugging Face 受限数据集，例如 `hal-utokyo/Manga109-s`，需要先在数据集页面登录、申请或接受访问条款。通过后创建一个有读取权限的 Hugging Face token，然后二选一：

- 在前端 `Hugging Face` 表单的 `HF Token` 输入框里粘贴 `hf_...` token，再点击预检或下载。
- 设置环境变量 `HF_TOKEN` 后重新启动软件：

```powershell
setx HF_TOKEN "hf_xxx"
```

`setx` 对新启动的终端/启动器生效，设置后请重新打开“贞贞的训练集下载器”。不要把 token 写进 `sources/*.json`、截图或日志里。

GitHub Release 下载会先尝试 `latest`，如果仓库没有 latest release，会退回 release 列表；如果仍没有 release，会下载仓库默认分支的源码 zip/tar 作为兜底。

## Outputs

- Raw downloads: `data/raw/<source_id>/`
- Extracted files: `data/extracted/`
- SQLite manifest: `manifests/anima_dataset.sqlite`

## Electron 打包

桌面版会把 Python 后端打成 `zhenzhen-backend.exe`，再由 Electron 启动这个内置后端，因此用户机器不需要安装 Python。

```powershell
npm install
npm run dist
```

打包产物：

- `dist_backend/zhenzhen-backend.exe`：PyInstaller 后端，内含 Python 运行时、前端静态文件和 `sources` 来源目录。
- `dist_electron/win-unpacked/贞贞的训练集下载器.exe`：未压缩桌面版，适合本机调试。
- `dist_electron/Zhenzhen-Dataset-Downloader-0.1.0-portable.exe`：可直接发给用户的 Windows x64 portable 单文件。

发布包只包含 Electron 桌面壳、`package.json` 和 `dist_backend/zhenzhen-backend.exe`。本地下载数据、manifest 数据库、运行日志、截图报告、`node_modules`、`build_backend`、`dist_backend` 和 `dist_electron` 都通过 `.gitignore` 或 electron-builder `files` 配置排除，不会进入 Git 仓库或 portable 包。

为避免开发机的历史任务和最近素材出现在用户第一次启动界面，Electron 打包版默认下载目录是 `%USERPROFILE%\Documents\ZhenzhenTrainData`。源码/VBS 启动器仍默认使用 `D:\zhenzhen-asset`。如需强制指定目录，可以在启动前设置环境变量：

```powershell
setx ANIMA_DATASET_ROOT "D:\zhenzhen-asset"
```

Electron 启动后会默认监听 `127.0.0.1:8422`，如果端口被占用，后端会在后续 20 个端口内自动寻找可用端口，Electron 会跟随实际端口打开页面。关闭 Electron 时会清理内置后端进程树。

打包后至少验证三件事：

- `/api/status` 里的 `python` 指向 `zhenzhen-backend.exe`，不是系统 `python.exe`。
- `/api/status` 里的默认 `root` 是用户文档目录下的 `ZhenzhenTrainData`，除非显式设置了 `ANIMA_DATASET_ROOT`。
- 关闭桌面窗口后没有残留 `zhenzhen-backend.exe` 进程。

## Current Commands

- `init`: create workspace folders and manifest database.
- `download-url`: download one URL with optional transient headers.
- `download-list`: download many URLs from a text file.
- `import`: copy local files or folders into the warehouse.
- `extract`: extract zip/cbz/tar/tgz archives and record outputs.
- `hf`: download files from a Hugging Face dataset repo.
- `wikimedia`: download files by Commons category or search.
- `ia`: download files from an Internet Archive item.
- GUI routes: `/api/catalog`, `/api/preflight`, `/api/kaggle`, `/api/zenodo`, `/api/github`, `/api/booru`.
- `jobs`: show recent download jobs.
- `assets`: show recent asset records.

## Notes

The MVP does not make license decisions before downloading. It records source and hash data first, then later training/export modes can decide what to include.

The downloader supports authorized access through user-provided tokens or transient request headers. It does not store passwords.
