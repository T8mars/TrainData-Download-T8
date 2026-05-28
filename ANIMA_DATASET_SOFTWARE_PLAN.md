# ANIMA 动漫模型训练集下载器规划

更新时间：2026-05-28

## 0. 当前工作区状态

当前目录 `E:\manga-resource` 已检查：

- 当前不是 Git 仓库。
- 现有文件：`MANGA_DATASET_PLAN.md`。
- 未发现 `SKILL.md`、`meta.json`、`features.json`、源码、测试或配置。

本文件作为后续开发 ANIMA 数据集下载器的规划基线。正式开工前如果补入项目代码，应先重新读取项目上下文。

## 1. 目标修正

目标从“漫画资源整理”调整为：

> 做一个可扩展的数据集下载与训练集整理软件，服务 ANIMA / Anime 风格模型训练，优先采集公版、CC0、CC-BY、明确授权、可商用实验或可研究使用的数据源。

当前优先级调整为“下载能力优先”：先保证公开直链、公开 API、Hugging Face、Wikimedia、Internet Archive、OpenGameArt、本地导入、用户手动下载后的素材包都能稳定进入本地数据仓库。

版权/授权信息先不作为 MVP 的强阻断条件，但仍保留字段和审计记录，方便后续再切换到合规筛选模式。软件不内置绕过 DRM、付费墙、反爬、账号限制或盗版漫画站批量抓取的能力。

## 1.1 下载优先 MVP 策略

第一阶段目标不是判断所有素材能不能训练，而是让“能正常访问的资源”先稳定下载、断点续传、校验、解包、入库。

### MVP 必须支持

- 公开 URL 批量下载：用户粘贴图片、压缩包、PDF、WebDataset tar、Hugging Face 文件 URL。
- Hugging Face 数据集下载：支持 dataset id、revision、subset、split、文件模式。
- Wikimedia Commons 下载：按分类、作者、搜索词抓取文件和元数据。
- Internet Archive 下载：按 item id 下载指定格式文件。
- OpenGameArt 下载：按页面 URL 或资源 ID 下载附件。
- 本地导入：支持目录、zip、cbz、pdf、tar、webdataset。
- 失败重试：超时、断线、部分文件损坏可恢复。
- 哈希校验：每个文件生成 `sha256`。
- 解包入库：原始文件保留，解包文件进入 `data/extracted`。
- 基础 manifest：即使 license 未知，也记录来源和下载时间。

### MVP 暂不强制

- 不强制 license 通过才下载。
- 不强制人工复核。
- 不强制生成完整法律报告。
- 不强制判断训练/商用/再分发用途。

### MVP 仍然不做

- 不绕过 DRM。
- 不破解付费下载。
- 不模拟盗版漫画站的批量抓取。
- 不绕过 Cloudflare/验证码/封禁。
- 不保存用户密码。

### 结果状态

下载优先模式下，每个资源只分三类：

- `DOWNLOADED`: 已下载并通过哈希/文件完整性检查。
- `FAILED`: 下载失败，可重试。
- `NEEDS_REVIEW`: 下载成功但来源、许可、内容质量或解包结果需要后续确认。

后续进入训练集构建时，再按用途启用更严格的版权、质量和内容过滤。

## 2. 关于“已故知名漫画家素材集”的现实边界

### 2.1 不能简单按“作者已故”判断

已故不等于可用。现代漫画家作品通常仍受保护：

- 日本一般是作者死亡后 70 年；2018 年延长到 70 年，但已在旧规则下进入公版的作品一般不会复活。
- 中国大陆自然人作品通常是作者终生及死亡后 50 年，截止到第 50 年 12 月 31 日。
- 美国对 1978 年以前出版作品有复杂规则，常用粗略规则是：2026 年时，1930 年及以前出版的很多作品已进入美国公版，但外国作品、未出版作品、续展、商标和角色后续设定仍需细查。

因此软件必须按“单件作品/单个文件”判断，不按“艺术家名字”整包放行。

### 2.2 可作为首批候选的已故作者/素材方向

以下不是一次性全都可商用，而是建议纳入插件的“候选源”。每个条目仍要按文件级许可筛选。

#### A. 高置信公版/可 API 采集

1. 葛饰北斋 Katsushika Hokusai，1760-1849

- 相关素材：`Hokusai Manga`、浮世绘、人物动态、线稿、风景。
- 来源：Wikimedia Commons、Internet Archive、博物馆开放数据。
- 风险：不是现代 anime，但对线稿、姿态、构图、日式视觉母题很有价值。
- 建议用途：公版底座、线稿/构图 LoRA、风格预训练辅助。

2. 北泽乐天 Kitazawa Rakuten，1876-1955

- 相关素材：早期日本漫画、讽刺漫画、`Jiji Manga` 等。
- 来源：Wikimedia Commons、Tokyo Museum Collection、Saitama Manga Museum 相关馆藏。
- 风险：馆藏图片的数字化权利和下载条款要单件确认；跨司法辖区也要区分。
- 建议用途：日本现代漫画早期线条、讽刺漫画、版式参考。

3. 冈本一平 Okamoto Ippei，1886-1948

- 相关素材：大正/昭和早期漫画、新闻漫画、插图。
- 来源：Wikimedia Commons、NDL/馆藏、公开图书馆资源。
- 风险：可下载图像数量可能有限，需要从馆藏 API 和 Commons 扩展。
- 建议用途：历史漫画风格、小样本风格集。

4. Winsor McCay，1869-1934

- 相关素材：`Little Nemo in Slumberland`、`Dream of the Rarebit Fiend`。
- 来源：Comic Strip Library、Wikimedia Commons、Internet Archive。
- 风险：现代再版合集可能有新排版/修复版权，应优先用原始公版扫描。
- 建议用途：角色幻想构图、分镜、色彩、超现实场景。

5. George Herriman，1880-1944

- 相关素材：`Krazy Kat` 早期漫画条。
- 来源：公版漫画条资源、Internet Archive、馆藏。
- 风险：需要按出版年份和续展情况过滤，优先 1930 年及以前。
- 建议用途：实验性分镜、图文关系、漫画语言。

6. E. C. Segar，1894-1938

- 相关素材：`Thimble Theatre` 中 1929 年早期 Popeye。
- 来源：公共领域漫画条资料、Internet Archive、Duke 公版清单辅助核验。
- 风险：只能用早期版本；后续动画、菠菜设定、现代形象、商标使用都要分开处理。
- 建议用途：角色设计历史样本，不建议作为商业形象输出主素材。

#### B. 中国作者候选，需按司法辖区分池

1. 丰子恺，1898-1975

- 相关素材：现代中国漫画/抒情漫画。
- 中国大陆视角：2026 年起，死亡满 50 年后的财产权期限边界值得纳入复核。
- 全球/美国/欧盟视角：不宜直接按公版处理，life+70 地区通常未到期。
- 建议用途：中国大陆本地合规研究池、人工复核池，不进入默认全球商用池。

2. 张光宇，1900-1965

- 相关素材：装饰风格、漫画、插画、西游相关现代视觉。
- 中国大陆视角：死亡后 50 年已过。
- 全球/美国/欧盟视角：life+70 地区通常要到 2036 年后更稳。
- 建议用途：中国风动漫视觉参考池，默认需人工复核。

3. 不建议首批纳入的现代中文漫画家

- 张乐平，1992 年逝世。
- 叶浅予，1995 年逝世。
- 华君武，2010 年逝世。
- 丁聪，2009 年逝世。
- 廖冰兄，2006 年逝世。

这些作者知名度高，但距离公版期还远，不适合做“一键训练集”默认源。

#### C. 现代日本漫画家，默认不作为可下载训练集

以下可以作为“不可下载/版权提醒”的知识库条目，不作为数据源：

- 手冢治虫，1989 年逝世。
- 石森章太郎，1998 年逝世。
- 藤子·F·不二雄，1996 年逝世。
- 赤冢不二夫，2008 年逝世。
- 水木茂，2015 年逝世。
- 三浦建太郎，2021 年逝世。

这些都不适合作为默认下载训练集。软件可以只保留“需授权购买/联系版权方”的状态。

## 3. 数据源分级

### 3.1 下载优先的一键来源

在下载优先 MVP 中，先做这些“技术上稳定”的来源：

- Hugging Face datasets：通过 `huggingface_hub` 下载，支持 token。
- Wikimedia Commons：通过 MediaWiki API 下载。
- Internet Archive：通过 metadata API 下载。
- OpenGameArt：通过页面附件或解析下载链接。
- 公开 HTTP/HTTPS URL 列表：按 txt/csv/json 批量下载。
- 本地文件导入：用户已下载的压缩包或目录。

这些来源即使 license 未知，也可以先进入 `NEEDS_REVIEW`，但不能默认进入“可商用训练集”。

### 3.2 默认允许合规一键下载

满足以下条件才进入 `AUTO_DOWNLOAD_ALLOWED`：

- 文件级 license 明确为 `PUBLIC_DOMAIN`、`CC0`、`CC-BY`、`CC-BY-SA` 或类似自由许可。
- 有公开 API 或直链下载方式。
- 站点条款允许下载或未禁止合理自动化访问。
- 可保存许可证快照和来源记录。

首批建议：

- Wikimedia Commons：按作者、分类、license 拉取。
- OpenGameArt：CC0 / CC-BY 动漫素材、精灵、tile。
- Hugging Face：只允许 license 白名单数据集，例如 `cc0-1.0`、`cc-by-4.0`，并保留 dataset card 快照。
- Internet Archive：只允许 item 元数据明确为 public domain / CC0 / CC-BY 的条目。
- Comic Strip Library：公版漫画条，按作品页和图片页记录。

### 3.3 半自动下载/导入

这些源可以支持，但不应默认模拟登录或绕过限制：

- Digital Comic Museum：免费注册下载 public domain golden age comics。
- Comic Book Plus：免费注册下载 public domain comic books / strips / pulps。
- Manga109-s：用户在 Hugging Face 接受条款后，用 token 导入；不能再分发原图。
- Manga109：学术账户 gated import，仅学术非商业池。
- eBDtheque：申请后导入，按申请条款保存。

### 3.4 默认阻断

以下只做 metadata-only 或完全阻断：

- Pixiv 扫图/排行榜抓图。
- Danbooru / Gelbooru / Zerochan 等用户上传站的原图。
- MangaDex、盗版漫画站、汉化扫图站。
- 商业电子书/Kindle/Kobo/DRM 资源。
- 现代 IP 角色图包。

原因：来源、授权、作者同意和训练许可不清楚，无法做成负责任的一键训练集软件。

## 4. 软件总体架构

建议项目名：`anima-dataset-studio`

```text
E:\manga-resource\
  ANIMA_DATASET_SOFTWARE_PLAN.md
  sources\
    registry.yaml
    policies.yaml
  packages\
    core\
      plugin_base.py
      manifest.py
      rights_policy.py
      downloader.py
      resumable_download.py
      extractor.py
      dedupe.py
      processors.py
      exporters.py
    plugins\
      wikimedia_commons\
      huggingface_dataset\
      opengameart\
      internet_archive\
      comic_strip_library\
      digital_comic_museum_import\
      comic_book_plus_import\
      manga109_gated\
      local_import\
  apps\
    desktop\
    cli\
  data\
    raw\
    quarantine\
    extracted\
    processed\
    exports\
  manifests\
    sources.parquet
    items.parquet
    assets.parquet
    licenses.parquet
    audit_log.jsonl
  reports\
    license_audit\
    dataset_cards\
```

### 4.1 核心分层

1. Source Plugin Layer

- 负责搜索、列目录、读取元数据、下载或导入。
- 每个插件必须声明能力和风险等级。

2. Rights Policy Layer

- 统一判断是否能下载、训练、商用、再分发、发布样张。
- 下载优先 MVP 中，`UNKNOWN` 不阻断下载，只标记 `NEEDS_REVIEW`。
- 进入训练导出时，`NO_AI_TRAINING`、`COPYRIGHTED`、`UNKNOWN` 是否阻断由用户选择的模式决定。

3. Asset Pipeline Layer

- 解压、PDF 转图、CBZ/ZIP 处理、图片标准化。
- pHash / sha256 去重。
- 水印、扫图组标识、版权页检测。
- NSFW 和敏感内容分级。

4. Training Export Layer

- 输出给 Kohya/SDXL/Flux/自研训练脚本。
- 支持 image-caption、WebDataset、Parquet、COCO、YOLO、OCR JSON。

5. Desktop/CLI Layer

- 桌面端负责队列、可视化、筛选和报告。
- CLI 负责自动化、批处理和后续复用。

## 5. 插件接口设计

```python
class DatasetSourcePlugin:
    source_id: str
    display_name: str
    source_type: str
    supports_search: bool
    supports_auto_download: bool
    requires_auth: bool
    default_rights_tier: str

    def check_health(self) -> SourceHealth: ...
    def search(self, query: SourceQuery) -> list[SourceItem]: ...
    def list_collections(self) -> list[SourceCollection]: ...
    def fetch_item(self, item_id: str) -> SourceItem: ...
    def fetch_license(self, item: SourceItem) -> LicenseEvidence: ...
    def download(self, item: SourceItem, target_dir: str) -> DownloadResult: ...
    def import_local(self, path: str) -> ImportResult: ...
    def build_manifest(self, item: SourceItem, files: list[str]) -> AssetManifest: ...
```

下载器接口单独抽象，保证所有插件共用断点续传、限速、重试、哈希校验：

```python
class DownloadEngine:
    def enqueue(self, request: DownloadRequest) -> DownloadJob: ...
    def pause(self, job_id: str) -> None: ...
    def resume(self, job_id: str) -> None: ...
    def retry(self, job_id: str) -> None: ...
    def verify(self, job_id: str) -> VerifyResult: ...
```

下载任务字段：

```json
{
  "job_id": "...",
  "source_id": "direct_url",
  "url": "https://...",
  "target_path": "data/raw/...",
  "headers_profile": "default",
  "expected_sha256": null,
  "status": "queued",
  "retry_count": 0,
  "bytes_total": null,
  "bytes_done": 0
}
```

插件元数据：

```yaml
source_id: wikimedia_commons
display_name: Wikimedia Commons
mode: auto_download
auth: none
license_strategy: file_level
allowed_license_ids:
  - public-domain
  - cc0-1.0
  - cc-by-4.0
  - cc-by-sa-4.0
rate_limit:
  requests_per_second: 2
requires_license_snapshot: true
```

## 6. Manifest 标准

每个文件都生成一条资产记录：

```json
{
  "asset_id": "sha256:...",
  "source_id": "wikimedia_commons",
  "source_item_id": "File:Hokusai...",
  "creator": "Katsushika Hokusai",
  "creator_death_year": 1849,
  "title": "Hokusai Manga ...",
  "publication_year": 1834,
  "source_url": "https://...",
  "download_url": "https://...",
  "license_id": "public-domain",
  "license_url": "https://...",
  "license_snapshot_path": "reports/license_snapshots/...",
  "rights_tier": "PUBLIC_DOMAIN",
  "allowed_uses": ["train", "commercial_train", "publish_samples", "redistribute_processed"],
  "blocked_uses": [],
  "jurisdictions_checked": ["US", "CN", "JP"],
  "sha256": "...",
  "phash": "...",
  "width": 2048,
  "height": 3072,
  "mime_type": "image/jpeg",
  "content_tags": ["line_art", "historical_manga", "public_domain"],
  "caption": "public domain historical Japanese manga sketch...",
  "processing_history": []
}
```

## 7. 权利等级模型

建议内部枚举：

- `PUBLIC_DOMAIN_GLOBAL`: 多数主要辖区均低风险。
- `PUBLIC_DOMAIN_US_ONLY`: 美国公版，其他辖区待确认。
- `PUBLIC_DOMAIN_CN_ONLY`: 中国大陆财产权到期，但 life+70 地区不默认放行。
- `CC0`: 最优先。
- `CC_BY`: 可用，但导出报告必须 attribution。
- `CC_BY_SA`: 可用，但衍生物/再分发要共享相同许可或人工确认。
- `MANGA109_S_RESTRICTED`: 可训练和商用实验结果，但不能再分发原图，公开模型需说明。
- `ACADEMIC_ONLY`: 仅学术。
- `LICENSED_USER_LOCAL_ONLY`: 用户自备授权素材，仅在本机使用，不导出原图。
- `UNKNOWN_BLOCKED`: 阻断。
- `COPYRIGHTED_BLOCKED`: 阻断。

## 8. 训练集构建模式

### 8.1 Safe Commercial 模式

只允许：

- `PUBLIC_DOMAIN_GLOBAL`
- `CC0`
- 明确可商用的 `CC_BY`
- 人工确认过的授权素材

排除：

- Manga109 普通版
- Manga109-s 原图再分发
- CN-only / US-only 未复核
- 用户上传站抓图

### 8.2 Research 模式

允许：

- Manga109
- eBDtheque
- Manga109-s
- 本地授权材料

输出：

- 强制带 dataset card。
- 禁止发布原图包。
- 导出结果加用途限制提示。

### 8.3 Historical Public Domain 模式

用于：

- Hokusai、Kitazawa、Okamoto、McCay、Herriman、早期 comic strip。

输出：

- 适合风格底座、线稿、构图、分镜。
- 附带作者和年代标签，避免把历史风格误标成现代 anime。

### 8.4 User Licensed 模式

用户自己购买或授权的素材：

- 软件只做本地导入、哈希、标注和训练导出。
- 不做上传共享。
- 需要用户填写授权说明或上传合同/发票快照。

## 9. ANIMA 训练数据处理流水线

1. 下载/导入

- 从插件获取文件。
- 保存原始包到 `data/raw`。
- 生成来源和许可证快照。

2. 解包/标准化

- 支持 jpg/png/webp/cbz/zip/pdf/webdataset。
- 自动旋转、裁黑边、去空白页。
- 转 RGB，限制最大边长。

3. 去重与污染过滤

- sha256 精确去重。
- pHash 近重复去重。
- OCR 检测“scan by”“fan translation”“copyright”等风险词。
- logo、水印、网站地址检测。

4. 质量筛选

- 分辨率阈值。
- 压缩噪声评分。
- 人物/背景/线稿分类。
- 成人/血腥/儿童风险分类。

5. 自动标注

- WD tagger / anime tagger。
- OCR 提取画面中文字。
- BLIP/Florence/QwenVL 等 caption。
- 人工编辑 caption 界面。

6. 训练导出

- LoRA image-caption 文件夹。
- WebDataset tar。
- Parquet manifest。
- COCO/YOLO 检测集。
- dataset card + license report。

## 10. 桌面软件设计

首屏不做营销页，直接是工作台。

### 10.1 页面

1. Sources

- 数据源列表。
- 权利等级 badge。
- 是否支持一键下载。
- 是否需要登录/申请/token。

2. Search & Collect

- 搜索作者、关键词、license、年代。
- 支持“只看可商用安全源”。
- 批量加入下载队列。

3. Download Queue

- 下载进度。
- 失败原因。
- 许可证阻断原因。
- 重试/跳过/转人工复核。

4. Dataset Builder

- 按用途选择：商业、研究、公版历史、用户授权。
- 按作者、来源、风格、分辨率、NSFW、语言筛选。
- 训练集预估规模和风险摘要。

5. Review

- 预览图片。
- 编辑 caption。
- 标记错误授权。
- 手动确认/隔离。

6. Export

- Kohya / SDXL / Flux / WebDataset / COCO / YOLO。
- 自动生成 `dataset_card.md` 和 `license_report.html`。

7. Settings

- 数据目录。
- Hugging Face token。
- 代理。
- 并发与限速。
- OCR/caption 模型路径。

### 10.2 技术栈建议

推荐：

- Core：Python。
- Backend：FastAPI + SQLite。
- Desktop：Electron + React。
- Worker：Python subprocess / Celery 可后置。
- Image：Pillow、OpenCV、imagehash、pypdfium2、rarfile/7zip。
- Data：Parquet + SQLite 双写；Parquet 方便训练，SQLite 方便桌面检索。

原因：

- 数据处理和训练生态主要在 Python。
- Electron 打包更直接，和本地 Python worker 协作成熟。
- 后续可以单独保留 CLI，不被桌面端绑死。

## 11. 开发里程碑

### M0：下载核心

- SQLite 任务表。
- 断点续传下载器。
- 并发/限速/重试。
- sha256 校验。
- raw/extracted/processed 目录约定。
- direct URL 批量下载。

### M1：基础导入

- 本地导入。
- zip/cbz/pdf/tar/webdataset 解包。
- manifest 最小字段。
- 下载结果页面/CLI 输出。

### M2：公开源插件

- Hugging Face dataset。
- Wikimedia Commons。
- Internet Archive。
- OpenGameArt。

### M3：桌面下载器 MVP

- Sources 页面。
- URL 批量输入。
- 下载队列。
- 本地导入。
- 解包结果查看。

### M4：训练集导出

- LoRA image-caption 导出。
- WebDataset 导出。
- Parquet manifest。
- 基础 caption 文件生成。

### M5：合规和质量增强

- 权利等级过滤。
- license report。
- pHash 去重。
- 水印/版权页检测。
- 人工复核队列。

### 原规划里程碑：合规优先版

以下保留作为第二阶段参考。

#### M0：规划与清单

- 完成数据源 registry。
- 完成权利等级和用途策略。
- 完成 manifest schema。

#### M1：CLI MVP

- `local_import`
- `wikimedia_commons`
- `huggingface_dataset`
- `opengameart`
- license report
- LoRA 导出

#### M2：桌面 MVP

- Sources 页面。
- 下载队列。
- Dataset Builder。
- Export 页面。
- SQLite 检索。

#### M3：公版漫画增强

- Comic Strip Library 插件。
- Internet Archive 插件。
- Digital Comic Museum / Comic Book Plus 半自动导入。
- 历史作者 preset：Hokusai、Kitazawa、Okamoto、McCay、Herriman。

#### M4：受限数据集

- Manga109-s gated import。
- Manga109 academic import。
- eBDtheque import。
- 强制用途限制和导出警告。

#### M5：训练质量工具

- 自动 caption。
- WD tagger。
- pHash/CLIP 去重。
- 水印和版权页检测。
- 数据集评分和抽样报告。

## 12. 首批可落地源清单

优先做这些：

1. Wikimedia Commons

- 用处：Hokusai、Kitazawa、Okamoto、公版漫画、开放授权图片。
- 自动化程度：高。
- 风险：低到中，取决于单文件 license。

2. Hugging Face License Filter

- 用处：筛选 cc0/cc-by 的动漫相关数据集，例如 anime-bg、C3B 等。
- 自动化程度：高。
- 风险：中。HF license label 不是最终法务结论，仍需保留 dataset card 和抽样复核。

3. OpenGameArt

- 用处：CC0 动漫 sprite / tile / 游戏素材。
- 自动化程度：中。
- 风险：低到中。

4. Comic Strip Library

- 用处：Little Nemo 等公版漫画条。
- 自动化程度：中。
- 风险：低到中。

5. Internet Archive

- 用处：Hokusai Manga、公版漫画、早期动画/漫画资料。
- 自动化程度：中。
- 风险：中。必须严格按 item license 过滤。

6. Digital Comic Museum / Comic Book Plus

- 用处：大量 public domain Golden Age comics。
- 自动化程度：半自动。
- 风险：中。需要尊重账号和下载条款。

7. Manga109-s

- 用处：真正接近现代 manga 的可商用实验数据。
- 自动化程度：用户授权后中。
- 风险：中。不能再分发原图，必须用途限制。

## 13. 不做的事

- 不做 Pixiv 一键爬图。
- 不做 Danbooru/Zerochan 原图训练集默认下载。
- 不绕过电子书 DRM。
- 不把现代已故漫画家的作品当作公版。
- 不把“网上能看”视为“能训练/能商用/能再分发”。

## 14. 下一步建议

如果开始实现，建议第一步不是桌面 UI，而是建核心：

1. `sources/registry.yaml`
2. `packages/core/manifest.py`
3. `packages/core/rights_policy.py`
4. `packages/plugins/wikimedia_commons`
5. `packages/plugins/huggingface_dataset`
6. `packages/cli/anima_dataset`

这样后续桌面端、批处理、训练脚本都能复用同一个可信数据底座。
