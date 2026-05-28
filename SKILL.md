# 贞贞的训练集下载器维护说明

本项目是一个面向 anime / 漫画训练数据准备的本地中文下载器。它优先保证“能预检、能小批量下载、能记录来源和哈希”，前端是静态页面，后端是 Python 标准库 HTTP 服务。

GitHub 仓库：https://github.com/T8mars/TrainData-Download-T8

## 项目结构

- `src/anima_dataset/gui_server.py`：中文 Web GUI 后端、API 路由、预检逻辑、默认下载目录。
- `src/anima_dataset/web/index.html`、`app.js`、`styles.css`：中文前端界面。标题应保持为“贞贞的训练集下载器”。
- `src/anima_dataset/download.py`：断点下载、重试、哈希、任务记录的核心下载器。
- `src/anima_dataset/catalog.py`：把 `sources/` 下的 JSON 来源目录归一化给前端。
- `src/anima_dataset/plugins/`：各下载通道插件。
- `sources/providers/providers.json`：来源类型、中文标签、授权提示。
- `sources/catalogs/base.json`：人工维护的重点训练集来源。
- `sources/catalogs/generators.json`：批量生成来源入口，当前主要用于 Wikimedia、Internet Archive、Booru、Zenodo、Kaggle、GitHub、直链。
- `tools/launch_gui.ps1`：推荐 GUI 启动脚本，默认下载目录 `D:\zhenzhen-asset`。
- `启动贞贞的训练集下载器.vbs`：推荐双击启动器，隐藏黑色命令窗口并打开浏览器。
- `launch.bat`：备用启动器，调用隐藏 VBS。
- `tools/launcher.ps1`、`launch_cli.bat`：旧版 CLI 菜单，仅备用。
- `electron/main.js`：Electron 桌面壳，启动内置 `zhenzhen-backend.exe` 并加载本地前端；打包版默认数据目录是用户文档目录下的 `ZhenzhenTrainData`，避免读取开发机历史库。
- `tools/build_backend.ps1`、`tools/backend_entry.py`：PyInstaller 后端打包入口。

## 运行方式

推荐启动：

```powershell
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File .\tools\launch_gui.ps1
```

只启动服务、不自动打开浏览器：

```powershell
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File .\tools\launch_gui.ps1 -NoOpen
```

指定下载目录：

```powershell
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File .\tools\launch_gui.ps1 -DataRoot "D:\zhenzhen-asset"
```

如果机器上的 `python.exe` 指向 WindowsApps 假入口，启动器会自动跳过；也可以设置 `ANIMA_PYTHON` 指向真实 Python，例如 `C:\ProgramData\anaconda3\python.exe`。

## 下载源行为

- `direct`：HTTP/HTTPS/file 单文件下载；预检会先 HEAD，失败后用 Range 请求兜底；支持临时请求头。
- `hf`：Hugging Face dataset tree API，支持 `HF_TOKEN` 或表单 token，按 glob 匹配文件。
- `wikimedia`：Wikimedia Commons 分类或搜索；下载时有轻量间隔，避免过快请求；无结果会明确报错。
- `ia`：Internet Archive item 元数据与文件下载；规则不匹配时会返回样例文件名，方便改 include。
- `iaSearch`：先 advanced search，再扫描候选 item 的匹配文件；无结果会说明已检查条目。
- `kaggle`：需要 `~/.kaggle/kaggle.json` 或 `KAGGLE_USERNAME` / `KAGGLE_KEY`；不要把密钥写进仓库。
- `zenodo`：支持 record id 或搜索词；按文件名 glob 匹配。
- `github`：先查 latest release，再查 release 列表；如果没有 release，会退回默认分支源码 zip/tar。
- `booru`：推荐目录默认生成 Safebooru、Danbooru；表单仍可手动测试 Gelbooru、Konachan、Yande.re。公开 API 可能限速或要求站点侧权限，不做验证码、DRM、付费墙或反爬绕过。
- `local`：导入本地文件或文件夹；解包逻辑在 `extract.py`。

## 增加来源

优先只改 JSON，不改代码：

1. 新增人工重点来源：编辑 `sources/catalogs/base.json`。
2. 批量增加同模式来源：编辑 `sources/catalogs/generators.json`。
3. 新增来源类型：补 `sources/providers/providers.json`，再新增 `src/anima_dataset/plugins/<name>.py`，最后在 `gui_server.py` 加 `/api/...` 路由和 `preflight()` 分支。

来源卡片字段约定：

- `id`：稳定唯一 ID。
- `provider`：`direct`、`hf`、`wikimedia`、`ia`、`iaSearch`、`kaggle`、`zenodo`、`github`、`booru`、`local`。
- `group`：中文分类。
- `title`、`badge`、`description`：前端展示文本。
- `fields`：对应表单参数。
- `sourceUrl`：来源页面链接。

## 验证清单

修改代码后至少跑：

```powershell
& "C:\ProgramData\anaconda3\python.exe" -m compileall src
```

目录加载检查：

```powershell
$env:PYTHONPATH = "src"
& "C:\ProgramData\anaconda3\python.exe" -c "from anima_dataset.catalog import load_catalog; d=load_catalog(); print(d['count']); print([p['id'] for p in d['providers']])"
```

服务检查：

```powershell
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File .\tools\launch_gui.ps1 -NoOpen
Invoke-RestMethod http://127.0.0.1:8422/api/status
Invoke-RestMethod http://127.0.0.1:8422/api/catalog
```

前端检查要确认：

- 页面标题和 H1 是“贞贞的训练集下载器”。
- 源码/VBS 启动时默认下载目录显示 `D:\zhenzhen-asset`。
- Electron 打包版未设置 `ANIMA_DATASET_ROOT` 时默认下载目录显示用户文档目录下的 `ZhenzhenTrainData`。
- 推荐数据集一页 9 个，桌面为 3 列 3 行。
- 预检按钮能显示命中文件，不会直接下载。
- 失败 toast 显示中文可行动错误。

下载源回归建议每次覆盖这些小样本：

- `direct`：OpenGameArt 小 zip 或图片。
- `hf`：`deepghs/anime-bg` 的 `README.md` 或一个小文件，不要默认下载大 tar。
- `ia`：`hokusaimanga04kats` + `*.pdf`。
- `iaSearch`：`Hokusai manga mediatype:texts` + `*.pdf`。
- `wikimedia`：搜索 `Hokusai manga`，小批量。
- `zenodo`：搜索 `anime manga`，最多一个记录一个文件。
- `github`：`nagadomi/lbpcascade_animeface` + `*.zip`，验证源码包兜底。
- `booru`：`safebooru` + `anime_girl rating:general`。
- `kaggle`：无凭据时应给出“需要配置 kaggle.json 或环境变量”的中文错误。

## Electron 打包

用户机器不要求安装 Python。流程是先用 PyInstaller 打出内置后端 exe，再用 electron-builder 打 Windows x64 portable：

```powershell
npm install
npm run dist
```

关键产物：

- `dist_backend/zhenzhen-backend.exe`：内置 Python 运行时的后端。
- `dist_electron/win-unpacked/贞贞的训练集下载器.exe`：未压缩调试版。
- `dist_electron/Zhenzhen-Dataset-Downloader-0.1.0-portable.exe`：发给用户的 portable 单文件。

打包复用流程：

1. 先确认 `.gitignore` 继续排除 `data/`、`logs/`、`reports/*.png`、`manifests/*.sqlite*`、`node_modules/`、`build_backend/`、`dist_backend/`、`dist_electron/`、`*.log` 和 `*.spec`。
2. 更新代码后运行 `& "C:\ProgramData\anaconda3\python.exe" -m compileall src`。
3. 运行目录加载检查，确认来源数量和 provider 列表正常。
4. 执行 `npm run dist`。脚本会先跑 `tools/build_backend.ps1`，再跑 electron-builder。
5. 启动 `dist_electron/Zhenzhen-Dataset-Downloader-0.1.0-portable.exe`，检查 `/api/status`。
6. 验证 packaged backend 时，`/api/status` 里的 `python` 必须指向 `zhenzhen-backend.exe`，不能是系统 `python.exe`。
7. 未设置 `ANIMA_DATASET_ROOT` 时，`/api/status` 的 `root` 必须是用户文档目录下的 `ZhenzhenTrainData`，避免发布包在开发机上读取 `D:\zhenzhen-asset` 的历史任务。
8. 前端检查标题、GitHub 项目链接、推荐数据集分页、最近素材表的“时间”列。
9. 关闭 Electron 后确认没有残留 `zhenzhen-backend.exe`。

发布包只应包含 Electron 壳、`package.json` 和 `resources/backend/zhenzhen-backend.exe`。如果用户截图里出现旧“最近任务/最近素材”，优先判断是否读取了同一台机器上的旧 manifest，而不是把数据真的打进了 portable。

## 稳定性原则

- 保持 Python 标准库优先，不为小功能引入重依赖。
- 手工代码修改使用 `apply_patch`。
- 预检只枚举和校验，不创建下载任务。
- 下载失败要留下 job 记录、错误文本和日志。
- 外部站点抖动时优先加重试、限速、友好错误和小批量默认值。
- 不把 token、账号、密钥写入源码、JSON 或日志。
- 保留旧启动器兼容，但 README 和主入口推荐新中文名。

## Key / Token 处理

- Hugging Face 受限数据集要先在数据集页面登录并申请或接受访问条款。
- 下载器读取前端 `HF Token` 字段，或环境变量 `HF_TOKEN`。
- Windows 持久设置可用 `setx HF_TOKEN "hf_xxx"`，设置后重启启动器。
- Kaggle 读取 `C:\Users\<你>\.kaggle\kaggle.json`，或 `KAGGLE_USERNAME` / `KAGGLE_KEY`。
- GitHub 私有仓库或更高限额可填表单 token，或设置 `GITHUB_TOKEN`。
- 不要把任何 token 写入 `sources/*.json`、README 示例真实值、截图或日志。
