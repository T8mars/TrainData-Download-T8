# 漫画/漫画风格训练素材采集规划

更新时间：2026-05-28

## 0. 工作区上下文检查

当前工作区：`E:\manga-resource`

检查结果：

- 目录存在，但当前为空。
- 不是 Git 仓库。
- 未找到 `SKILL.md`、`meta.json`、`features.json`、配置文件、源码或测试。

因此本规划先作为项目启动文档使用。后续如果补入现有项目或上游源码，需要先重新读取项目上下文，再决定具体技术栈和目录约束。

## 1. 目标边界

目标不是“尽可能多抓漫画图”，而是构建一个权利边界清楚、可审计、可复用的训练素材工作流：

- 能记录每张图或每本书的来源、许可证、下载时间、原始 URL、哈希、处理步骤。
- 能按用途区分：内部实验、商业模型结果、论文展示、样张发布、图片再分发。
- 能自动阻断未知授权、盗版扫图、站点条款不清或禁止自动化下载的来源。
- 能导出不同训练任务需要的数据：图像/字幕对、面板检测、OCR、气泡检测、角色/身体/脸部标注等。

本规划不是法律意见。正式商用前应保留来源快照，并对关键来源做一次人工或法务复核。

## 2. 素材源目录

### A. 首选来源：权利边界相对清楚

1. Digital Comic Museum

- URL: https://digitalcomicmuseum.com/
- 定位：Public Domain Golden Age Comics。
- 优点：站点明确称内容经工作人员和用户研究，目标是确认 public domain；适合做漫画页、面板、排版、复古漫画风格训练。
- 限制：需要注册账号下载；主要是美国黄金时代漫画，不是日本现代漫画；仍需保存每本书页面和站点声明快照。
- 建议用途：面板检测、漫画版式、黑白/彩色漫画风格、公共领域图像训练。

2. Comic Book Plus

- URL: https://comicbookplus.com/
- 定位：Public Domain comics、comic strips、pulp、fanzines、non-English comics 等。
- 优点：站点声明内容 free and legal，并持续防止侵犯版权或商标；类型更广，含非英语漫画。
- 限制：下载需要免费账号；不同栏目可能来源不同，需逐项记录条款。
- 建议用途：补充多语种漫画、老漫画、漫画条、杂志版式素材。

3. Wikimedia Commons

- URL: https://commons.wikimedia.org/wiki/Category:Manga
- 相关分类：`Category:Manga`、`Category:Public domain comics`、`Category:Open source comics`
- 优点：每个文件有独立许可页，可通过 MediaWiki API 采集 license、author、attribution、source。
- 限制：分类内并非全是漫画页；CC-BY/CC-BY-SA/PD/CC0 混合，必须按单文件许可处理；CC-BY-SA 对再分发和衍生物有传染/共享要求。
- 建议用途：小规模高置信素材、许可测试集、来源审计样板。

4. PD12M / Source.Plus

- URL: https://arxiv.org/abs/2410.23144
- 定位：public domain 和 CC0 图像文本数据集。
- 优点：规模大，适合给通用图像/文本训练做干净底座。
- 限制：不是漫画专用；需要二次过滤漫画、插画、线稿、分镜等标签；合成 caption 需要质量抽检。
- 建议用途：通用视觉底座、公共领域/CC0 安全池、漫画风格数据不足时的背景补充。

### B. 申请/研究来源：可用但限制强

1. Manga109-s

- URL: https://huggingface.co/datasets/hal-utokyo/Manga109-s
- 定位：Manga109 中 87 本，允许商业使用机器学习或图像处理实验得到的结果。
- 关键限制：禁止第三方再分发数据集；公开模型或结果时必须声明使用；禁止把数据集漫画图像或其直接改作当作产品销售；展示整页不得超过每卷 20%。
- 建议用途：商业研发实验、OCR、面板/人物/气泡检测、模型评估。
- 接入方式：只做 gated import，不在本项目内镜像数据。

2. Manga109

- URL: https://huggingface.co/datasets/hal-utokyo/Manga109
- 定位：学术用途 Manga 数据集。
- 关键限制：仅限非商业机构学术目的；需要学术机构邮箱申请；禁止第三方转让。
- 建议用途：学术研究、论文复现、非商用评估。
- 接入方式：只做 gated import，强制标记为 `ACADEMIC_ONLY`。

3. eBDtheque

- URL: https://ebdtheque.univ-lr.fr/database/
- 定位：100 页欧美日漫画，含文本行、气泡、面板等人工标注。
- 优点：标注结构适合检测/OCR/阅读顺序任务。
- 限制：需要注册申请；具体使用条款需在申请后快照保存。
- 建议用途：面板/气泡/文本检测验证集。

4. OpenMantra

- URL: https://github.com/mantra-inc/open-mantra-dataset
- 定位：漫画机器翻译评估数据，含原图与日英中翻译标注。
- 优点：适合翻译/OCR/气泡文本任务。
- 限制：仓库页面未清晰展示通用训练许可时，先作为评估/研究候选，禁止默认并入商用训练池。
- 建议用途：翻译评估、标注结构参考。

5. C3B

- URL: https://huggingface.co/datasets/Coder109/C3B
- 定位：约 1K 行漫画/文化感知图文基准，HF 显示 `cc-by-4.0`。
- 优点：许可证标签清楚，规模小，便于快速验证管线。
- 限制：仍需抽查图片来源与 attribution 字段是否完整。
- 建议用途：小型基准、VQA/图文理解验证。

### C. 只做元数据或默认排除

1. Grand Comics Database

- URL: https://www.comics.org/
- 定位：漫画元数据和索引，有 API 与 JSON/YAML 导入。
- 建议：用于书名、出版社、年代、issue 元数据、去重和权利核验辅助；不要默认把封面图作为训练素材。

2. Danbooru、Gelbooru、Safebooru、MangaDex、扫图站、盗版/汉化站

- 问题：用户上传内容、同人/商业 IP 混杂，图片训练授权通常不清楚。
- 建议：默认排除图片训练。若有需要，只能在单独插件里作为“metadata-only / blocked”来源，且不下载图片。

3. Internet Archive 漫画集合

- 问题：既有 public domain/CC，也有受版权保护的借阅或上传内容。
- 建议：只有在单条 item 的 license 明确为 Public Domain、CC0 或可训练许可，并保存证据时才允许导入。

## 3. 下载插件框架

建议先做“插件化采集核心”，桌面端只调用核心能力。

```text
E:\manga-resource\
  MANGA_DATASET_PLAN.md
  sources\
    registry.yaml
    policies.yaml
  packages\
    core\
      source_plugin.py
      manifest_schema.py
      rights_policy.py
      pipeline.py
    source_plugins\
      local_import\
      wikimedia_commons\
      digital_comic_museum\
      comic_book_plus\
      manga109_gated\
      ebdtheque_gated\
  apps\
    desktop\
  data\
    raw\
    extracted\
    processed\
  manifests\
    items.parquet
    assets.parquet
    licenses.parquet
    audit_log.jsonl
  docs\
    sources\
    license_snapshots\
```

插件接口建议：

```python
class SourcePlugin:
    source_id: str
    display_name: str
    requires_auth: bool
    supports_auto_download: bool

    def discover(self, query, cursor=None): ...
    def fetch_metadata(self, item_id): ...
    def download(self, item_id, target_dir): ...
    def extract(self, raw_path, target_dir): ...
    def build_manifest(self, item_id, files): ...
    def validate_rights(self, manifest): ...
```

每个插件必须输出统一 manifest：

- `source_id`
- `source_item_id`
- `title`
- `creator`
- `publisher`
- `publication_year`
- `source_url`
- `download_url`
- `downloaded_at`
- `license_id`
- `license_url`
- `license_snapshot_path`
- `rights_tier`
- `allowed_uses`
- `sha256`
- `phash`
- `content_warnings`
- `processing_history`

## 4. 授权/校验/后处理流水线

### 4.1 权利等级

建议统一成内部枚举：

- `PUBLIC_DOMAIN`: 可训练、可导出处理结果，可按来源条款发布样张。
- `CC0`: 可训练、可商用、通常无需 attribution，但仍保留来源。
- `CC_BY`: 可训练和商用，但导出/展示必须保留作者与许可。
- `CC_BY_SA`: 可训练和商用，但再分发/衍生物需遵守 ShareAlike。
- `MANGA109_S_RESTRICTED`: 可用于机器学习/图像处理实验和商业化实验结果，但禁止再分发原图，公开模型需声明使用。
- `ACADEMIC_ONLY`: 仅学术/非商业，不能进入商业训练池。
- `UNKNOWN_BLOCKED`: 不允许下载或训练，只保留人工复核记录。

### 4.2 合规闸门

导入前：

- 必须有来源 URL 和许可 URL。
- 必须保存许可页面快照或条款文本 hash。
- 需要账号的来源不保存密码，只保存“用户已自行授权/已接受条款”的状态。
- 自动下载前检查 robots、站点条款和频率限制。

导入中：

- 生成 `sha256`、文件大小、页数、分辨率。
- 记录原始压缩包和解包后的每页关系。
- 对未知许可、缺少来源、下载页变化的条目直接进入隔离区。

导入后：

- pHash/CLIP 去重，避免同一页跨站重复进入训练池。
- OCR 水印/页脚/扫图组标记，发现 scanlation 或版权声明时降级为 `UNKNOWN_BLOCKED`。
- 内容安全分类：成人、血腥、仇恨符号、儿童相关风险等。
- 质量校验：过低分辨率、严重压缩、倾斜、破页、双页跨页、扫描阴影。

### 4.3 后处理

基础处理：

- CBZ/ZIP/PDF 解包。
- 页图标准化：方向、色彩空间、DPI、尺寸上限。
- 双页拆分、边框裁切、去扫描黑边。
- OCR 初筛和文字区域检测。

训练任务处理：

- 面板检测：导出 COCO/YOLO 格式。
- 气泡/OCR：导出框、文字、阅读顺序。
- 扩散/LoRA：导出 image/caption pairs，caption 中加入来源、年代、风格、是否 public domain。
- 图文理解/VQA：保留页级和面板级上下文，不混入未知授权图像。

输出目录建议：

```text
exports\
  diffusion_image_caption\
  panel_detection_coco\
  balloon_ocr\
  manga_translation_eval\
  license_report\
```

## 5. 桌面软件落地

建议先做本地核心，再做桌面壳：

1. CLI / Core MVP

- `source registry` + `manifest schema`
- `local_import` 插件
- `wikimedia_commons` 插件
- 许可审计报告导出

2. 下载与处理 MVP

- DCM / Comic Book Plus 先做半自动导入：用户手动登录下载，软件负责导入、解包、审计、后处理。
- 避免一开始就做账号自动化下载，降低条款和风控风险。

3. Gated Dataset MVP

- Manga109-s / Manga109 / eBDtheque 只做“本地导入已授权数据”。
- 软件中展示限制 badge，不提供再分发按钮。

4. 桌面端

推荐界面模块：

- Sources：素材源列表、授权等级、账号/申请状态。
- Download Queue：下载/导入队列、失败原因、限速。
- Dataset Builder：按用途筛选 `allowed_uses`，构建训练集。
- License Audit：每个导出包的来源、许可证、attribution、风险项。
- Processing：拆页、裁边、面板检测、OCR、caption 生成。
- Exports：LoRA、COCO、YOLO、Parquet、CSV、HTML 报告。
- Settings：数据目录、代理、并发、模型路径、许可策略。

技术栈建议：

- 核心处理：Python，适合图像处理、OCR、Parquet、ML 工具链。
- 桌面端：Tauri + React 或 Electron + React。若更重视打包简单和现有 Node 生态，用 Electron；若更重视体积，用 Tauri。
- 本地服务：FastAPI 或直接命令式 worker。后续要跑长任务队列时再引入 SQLite + worker。

## 6. 第一阶段可执行任务

1. 初始化项目脚手架和 `sources/registry.yaml`。
2. 定义 `rights_policy.py` 和 manifest schema。
3. 实现 `local_import`：导入本地 CBZ/ZIP/PDF/图片目录，生成审计记录。
4. 实现 `wikimedia_commons`：按分类或搜索下载，逐文件读取 license/author/source。
5. 实现 HTML/CSV 许可审计报告。
6. 再接 DCM / Comic Book Plus 的半自动导入。
7. 最后接 Manga109-s gated import，并强制输出限制说明。

## 7. 待确认问题

开工前建议确认：

- 训练目标是扩散/LoRA、OCR、面板检测、漫画翻译，还是通用图文理解？
- 是否需要支持商业模型输出？如果需要，`ACADEMIC_ONLY` 必须默认排除。
- 桌面端优先 Tauri 还是 Electron？
- 是否接受“手动登录下载 + 本地导入”的 DCM/Comic Book Plus 流程？
- 是否需要内置 OCR/caption 模型，还是只负责整理素材？
