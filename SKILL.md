# 贞贞的训练集下载器维护说明

本项目是一个面向 anime / 漫画训练数据准备的本地中文下载器。它优先保证“能预检、能小批量下载、能记录来源和哈希”，前端是静态页面，后端是 Python 标准库 HTTP 服务。

GitHub 仓库：https://github.com/T8mars/TrainData-Download-T8

## 多 Agent 协同入口

新 Agent 接手前必须先读这些文件，不要只靠聊天摘要：

1. `SKILL.md`：本文件是协同总入口，优先级最高。
2. `features.json`：项目能力、端口、默认路径、provider 列表和验证命令。
3. `README.md`：对外说明，尤其是用户可见启动、Key 配置和打包说明。
4. `package.json`：Electron 打包入口、版本号、GitHub 仓库地址和 electron-builder 配置。
5. `.gitignore`：确认 data、logs、reports、manifest、dist、node_modules 不会被提交或打包。
6. 相关源码：后端先看 `src/anima_dataset/gui_server.py`，前端先看 `src/anima_dataset/web/`，打包先看 `electron/main.js` 和 `tools/build_backend.ps1`。

协同工作默认约定：

- 一个 Agent 只改自己负责的层，除非任务确实跨层。跨层修改要在最终说明里列出影响面。
- 修改数据源目录优先改 JSON；只有接入全新站点 API 时才新增 Python 插件和 API 路由。
- 前端改动必须保持中文界面、标题“贞贞的训练集下载器”、一页 9 个推荐数据集、最近素材表包含“时间”列。
- 打包改动必须验证 portable 使用内置 `zhenzhen-backend.exe`，用户机器不应依赖系统 Python。
- 不要把 token、账号、下载数据、manifest、运行日志、截图报告或构建产物提交进 Git。
- 若遇到和旧聊天记录冲突的地方，以当前仓库文件为准，再用实际命令验证。

## Agent 分工建议

- `后端/下载 Agent`：负责 `src/anima_dataset/gui_server.py`、`download.py`、`storage.py`、`plugins/`。重点看 API 路由、预检、失败日志、断点续传、哈希记录。
- `数据源 Agent`：负责 `sources/providers/providers.json`、`sources/catalogs/base.json`、`sources/catalogs/generators.json`。重点保证 `id` 唯一、字段能填入对应表单、默认下载量小。
- `前端 Agent`：负责 `src/anima_dataset/web/index.html`、`app.js`、`styles.css`、`presets.js`。重点保证中文、分页、表格列、错误 toast、移动端不溢出。
- `打包/发布 Agent`：负责 `package.json`、`electron/main.js`、`tools/build_backend.ps1`、`.gitignore`、README/SKILL 发布说明。重点保证不打进本机数据、portable 可启动、关闭后无后端残留。
- `文档/交接 Agent`：负责 `README.md`、`SKILL.md`、`features.json`。重点记录真实验证结果、已知坑、未完成项和对外用户说明。

多人并行时建议先拆分为“数据源 JSON”“下载插件”“前端 UI”“打包发布”四条线。合并前由一个 Agent 统一跑验证清单，避免各自只验证局部。

## 交接模板

每次 Agent 完成较大改动后，在回复或提交说明里至少交代：

- 改了哪些层：数据源、后端、前端、打包、文档。
- 影响的入口：VBS/PowerShell 启动器、Electron portable、CLI、具体 API。
- 跑过的验证命令：至少列出 `compileall`、catalog 检查、必要的 API/前端/打包检查。
- 没跑的验证：例如外网下载、Kaggle 凭据、受限 Hugging Face、GitHub Release 上传。
- 遗留风险：站点限速、凭据缺失、远端数据变动、大文件下载、Windows 权限。
- Git 状态：是否已提交、是否已推送、远端分支和提交号。

## 当前已知状态

- 默认服务端口是 `8422`，代码和文档不要回退到旧端口。
- 本地源码/VBS 启动默认下载目录是 `D:\zhenzhen-asset`。
- Electron 打包版默认下载目录是用户文档目录下的 `ZhenzhenTrainData`，这是为了避免开发机历史任务出现在用户首次启动界面。
- 最近一次已知目录加载数量是 `1472` 个来源，provider 是 `direct`、`hf`、`wikimedia`、`ia`、`iaSearch`、`kaggle`、`zenodo`、`github`、`booru`、`local`。
- GitHub 仓库是 `https://github.com/T8mars/TrainData-Download-T8`，本地 `main` 已配置跟踪 `origin/main`。
- 已知本机没有 `gh` 命令；GitHub Release 附件上传不能假设可用，除非先安装/验证 `gh` 或改用其他明确授权的上传方式。
- Windows 下这个仓库可能触发 Git `safe.directory` 或 `.git/*.lock Permission denied`，必要时使用已授权的 PowerShell 执行 Git 元数据操作。

## 已知错误和处理方式

- `python.exe` 指向 WindowsApps 假入口：使用 `tools/python.ps1` 的解释器探测，或设置 `ANIMA_PYTHON=C:\ProgramData\anaconda3\python.exe`。
- 启动器一闪而过：优先检查 `tools/launch_gui.ps1`、`logs/gui_stdout.log`、`logs/gui_stderr.log`；VBS/launch.bat 不应要求用户按任意键。
- 打包版显示开发机旧“最近任务/最近素材”：先看 `/api/status.root`，通常是读到了旧 manifest，不代表日志真的被打包；Electron 默认 root 应保持为用户文档目录 `ZhenzhenTrainData`。
- Hugging Face 401：受限数据集需要用户先在网页申请/接受条款，再填前端 HF Token 或设置 `HF_TOKEN`。
- GitHub Release 404：插件应先查 latest release，再查 release 列表，最后退回默认分支源码 zip/tar。
- Internet Archive 搜索 0 条：先用预检看关键词和 include 规则，必要时放宽 include 或改用 item id。
- Kaggle 下载失败：多数是本机没有 `~/.kaggle/kaggle.json` 或 `KAGGLE_USERNAME`/`KAGGLE_KEY`。
- Booru 无结果/401/限速：站点公开 API 行为不稳定，只做小批量测试，不做验证码、登录墙或反爬绕过。

## 需要完善但未完成

- GitHub Release 自动发布：当前只能本地生成 portable，未实现稳定的 Release 上传流程。
- 自动化测试：目前以手工命令和浏览器检查为主，缺少固定 pytest/e2e 测试套件。
- 大文件下载队列：已有后台线程和记录，但没有完整的暂停、取消、并发队列 UI。
- 数据源可用性巡检：目录有 1400+ 来源，但不是每个来源都做了实时下载验证；应增加批量预检报告。
- 凭据管理：当前 token 来自表单或环境变量，没有本地加密凭据库。
- 图标/签名：Electron 仍使用默认图标，没有代码签名，发布给普通用户时可能被 Windows SmartScreen 提醒。
- 版本发布规范：`package.json` 是 `0.1.0`，以后发版要同步 README、features.json、SKILL.md、portable 文件名和 Git tag。

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
