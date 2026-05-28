const HF_INCLUDE = "*.tar,*.zip,*.parquet,*.json,*.jsonl,*.csv,*.jpg,*.jpeg,*.png,*.webp";

function hf(repoId, title, group, description, badge = "HF 数据集") {
  return {
    id: `hf-${repoId.toLowerCase().replaceAll("/", "-").replaceAll("_", "-")}`,
    tab: "hf",
    group,
    title,
    badge,
    description,
    fields: {repo_id: repoId, include: HF_INCLUDE, max_files: "1"},
    endpoint: "/api/hf",
    sourceUrl: `https://huggingface.co/datasets/${repoId}`
  };
}

function wikimediaCategory(query, title, group, description, maxFiles = "5") {
  return {
    id: `wm-cat-${query.toLowerCase().replaceAll(" ", "-").replaceAll(":", "")}`,
    tab: "wikimedia",
    group,
    title,
    badge: "Wikimedia 分类",
    description,
    fields: {mode: "category", query, limit: "80", max_files: maxFiles},
    endpoint: "/api/wikimedia",
    sourceUrl: `https://commons.wikimedia.org/wiki/Category:${encodeURIComponent(query.replace(/^Category:/, ""))}`
  };
}

function wikimediaSearch(query, title, group, description, maxFiles = "5") {
  return {
    id: `wm-search-${query.toLowerCase().replaceAll(" ", "-")}`,
    tab: "wikimedia",
    group,
    title,
    badge: "Wikimedia 搜索",
    description,
    fields: {mode: "search", query, limit: "50", max_files: maxFiles},
    endpoint: "/api/wikimedia",
    sourceUrl: `https://commons.wikimedia.org/w/index.php?search=${encodeURIComponent(query)}&title=Special:MediaSearch&type=image`
  };
}

function ia(itemId, title, group, description, include = "*.pdf", maxFiles = "1") {
  return {
    id: `ia-${itemId}`,
    tab: "ia",
    group,
    title,
    badge: "Internet Archive",
    description,
    fields: {item_id: itemId, include, max_files: maxFiles},
    endpoint: "/api/ia",
    sourceUrl: `https://archive.org/details/${itemId}`
  };
}

function iaSearch(query, title, group, description, include = "*.pdf,*.zip,*.cbz,*.jpg,*.png", maxItems = "1") {
  return {
    id: `ia-search-${query.toLowerCase().replaceAll(" ", "-").replaceAll("\"", "").replaceAll(":", "")}`,
    tab: "iaSearch",
    group,
    title,
    badge: "Internet Archive 搜索",
    description,
    fields: {query, include, max_items: maxItems, max_files_per_item: "1"},
    endpoint: "/api/ia-search",
    sourceUrl: `https://archive.org/search?query=${encodeURIComponent(query)}`
  };
}

function direct(url, filename, title, group, description, badge = "直链") {
  return {
    id: `direct-${filename.replaceAll(".", "-")}`,
    tab: "direct",
    group,
    title,
    badge,
    description,
    fields: {url, filename, header: ""},
    endpoint: "/api/download-url",
    sourceUrl: url
  };
}

window.ANIMA_PRESETS = [
  hf("deepghs/anime-bg", "Anime BG 背景图", "背景/场景", "动漫背景与壁纸图，适合先做背景、构图、场景风格预训练。", "HF · CC0 · WebDataset"),
  hf("deepghs/csip_eval", "CSIP 动漫风格评估集", "评估/标签", "动漫风格分类评估数据，体量较小，适合测试下载和筛选管线。", "HF · CC-BY-4.0 · 小型"),
  hf("deepghs/csip_v1", "CSIP v1 风格集", "评估/标签", "CSIP 系列风格数据，可用于风格识别、聚类和测试。"),
  hf("deepghs/csip", "CSIP 完整风格集", "评估/标签", "CSIP 系列完整数据入口，适合逐分片测试。"),
  hf("deepghs/anime_dbrating", "Anime DB Rating", "评估/标签", "动漫图片评分/质量相关数据，用于筛选和排序实验。"),
  hf("deepghs/nsfw_detect", "NSFW 检测样本", "评估/标签", "用于内容过滤与安全分类的样本或标签数据。"),
  hf("deepghs/anime_blurry_preparation", "动漫模糊检测准备集", "质量过滤", "用于模糊图、低质量图识别的准备数据。"),
  hf("deepghs/anime_halfbody_detection", "动漫半身检测数据", "角色/检测", "面向动漫人物半身检测的训练或评估数据。"),
  hf("deepghs/anime_eye_detection", "动漫眼部检测数据", "角色/检测", "适合做眼部检测、裁切和细节标注实验。"),
  hf("deepghs/AnimeText", "AnimeText 文本数据", "OCR/文字", "动漫画面文字或 OCR 相关数据，适合字幕、文字区域处理。"),
  hf("deepghs/wd14_tagger_inversion", "WD14 Tagger 反推数据", "标签/标注", "用于标签反推、tagger 对齐或标签质量实验。"),
  hf("deepghs/tagger_vocabs", "Tagger 词表", "标签/标注", "常见动漫 tagger 词表，可用于 caption 和标签归一化。"),
  hf("deepghs/site_tags", "站点标签集", "标签/标注", "不同站点标签数据，适合做标签合并和映射。"),
  hf("deepghs/character_index", "角色索引", "角色/元数据", "动漫角色索引类数据，可辅助角色名、系列名和素材组织。"),
  hf("deepghs/sankaku_tags_categorize_for_WD14Tagger", "Sankaku 标签分类", "标签/标注", "面向 WD14 tagger 的 Sankaku 标签分类数据。"),
  hf("deepghs/generic_character_skins", "通用角色皮肤素材", "角色/素材", "角色皮肤/外观相关素材，适合游戏角色训练或分类。"),
  hf("deepghs/game_character_skins", "游戏角色皮肤素材", "角色/素材", "游戏角色皮肤素材入口，适合角色风格整理。"),
  hf("deepghs/anime_pictures-webp-4Mpixel", "Anime-Pictures WebP 4M", "大型图像源", "动漫图片站整理数据，WebP 版本，先用 1 个文件测试。", "HF · 大型 · WebP"),
  hf("deepghs/anime_pictures_full", "Anime-Pictures Full", "大型图像源", "Anime-Pictures 完整入口，体量较大，谨慎下载。", "HF · 大型"),
  hf("deepghs/konachan-webp-4Mpixel", "Konachan WebP 4M", "大型图像源", "Konachan 整理数据 WebP 版本，适合风格预训练试验。", "HF · 大型 · WebP"),
  hf("deepghs/konachan_full", "Konachan Full", "大型图像源", "Konachan 完整入口，适合后续分片下载。", "HF · 大型"),
  hf("deepghs/zerochan-webp-4Mpixel", "Zerochan WebP 4M", "大型图像源", "Zerochan 整理数据 WebP 版本，先拉 1 个文件测试。", "HF · 大型 · WebP"),
  hf("deepghs/zerochan_full", "Zerochan Full", "大型图像源", "Zerochan 完整入口，适合后续大规模扩展。", "HF · 大型"),
  hf("deepghs/nozomi_standalone-webp-4Mpixel", "Nozomi Standalone WebP", "大型图像源", "Nozomi 整理数据 WebP 版本，适合分片测试。", "HF · 大型 · WebP"),
  hf("deepghs/nozomi_standalone_full", "Nozomi Standalone Full", "大型图像源", "Nozomi 完整入口，体量较大。", "HF · 大型"),
  hf("deepghs/gelbooru-webp-4Mpixel", "Gelbooru WebP 4M", "大型图像源", "Gelbooru 整理数据 WebP 版本，先拉 1 个分片。", "HF · 大型 · WebP"),
  hf("deepghs/gelbooru_full", "Gelbooru Full", "大型图像源", "Gelbooru 完整入口，适合后续批处理。", "HF · 大型"),
  hf("deepghs/aibooru_full", "AIBooru Full", "AI/动漫图像", "AIBooru 整理入口，适合 AI 图像识别、过滤与对照实验。", "HF · 大型"),
  hf("deepghs/e6ai_full", "E6AI Full", "AI/动漫图像", "AI 图像整理入口，适合过滤器和质量管线测试。", "HF · 大型"),
  hf("deepghs/fancaps-webp-4Mpixel", "Fancaps WebP 4M", "动画截图", "动画截图类数据，适合镜头、背景和角色构图分析。", "HF · 大型 · WebP"),
  hf("deepghs/subsplease_animes", "SubsPlease 动画元数据", "动画元数据", "动画剧集/字幕相关元数据入口，可辅助番剧来源整理。"),
  hf("Dhiraj45/Animes", "Animes 图像集", "通用动漫图像", "动漫图像数据集，适合快速验证 HF 下载链路。", "HF · CC-BY-4.0"),
  hf("ComputerVisionAnimeProject/AnimeFaceColorization", "动漫脸部上色数据", "角色/人脸", "动漫脸部或上色相关数据，适合线稿上色实验。"),
  hf("ityizNola/Anime-LineArt-Dataset", "Anime LineArt 线稿集", "线稿/上色", "动漫线稿数据，适合上色、线稿增强、边缘提取。"),
  hf("RyokoExtra/LFANIME", "LFANIME 数据集", "通用动漫图像", "动漫图像入口，适合测试通用图像下载和筛选。"),
  hf("picollect/danbooru", "Danbooru PicCollect", "大型图像源", "Danbooru 相关整理入口，适合研究环境下分片测试。", "HF · 大型"),
  hf("WarriorMama777/PureDanbooru", "PureDanbooru", "大型图像源", "Danbooru 派生整理入口，适合标签和图像联合实验。", "HF · 大型"),
  hf("nyuuzyou/OpenGameArt-CC0", "OpenGameArt CC0 索引", "游戏/开放素材", "OpenGameArt CC0 素材索引，含 2D 图像、精灵、贴图和附件 URL。", "HF · CC0"),
  hf("zenless-fab/animepics", "AnimePics 大规模预训练集", "大型图像源", "大规模 WebDataset 动漫图像预训练集，建议从 1 个 tar 分片开始。", "HF · 需同意访问 · 很大"),
  hf("hal-utokyo/Manga109-s", "Manga109-s", "漫画/受限", "接近现代漫画的数据集，需要在 HF 页面申请并接受条款。", "HF · 需申请/token"),
  hf("hal-utokyo/Manga109", "Manga109", "漫画/受限", "经典漫画研究数据集，通常需要学术申请和 token。", "HF · 学术/token"),
  hf("lowres/anime", "Lowres Anime", "通用动漫图像", "低分辨率动漫图像入口，适合小样本管线测试。"),
  hf("absinc/stable-anime", "Stable Anime", "通用动漫图像", "动漫图像/提示相关数据入口，适合 caption 管线试验。"),
  hf("lambdalabs/pokemon-blip-captions", "Pokemon BLIP Captions", "图文配对", "类动漫角色图文配对数据，适合 caption 和图像文本对齐测试。"),
  hf("huggan/anime-faces", "Anime Faces", "角色/人脸", "动漫头像/脸部数据入口，适合人脸裁切、头像 LoRA 测试。"),
  hf("AppleHarem/anime_image_classification", "Anime Image Classification", "评估/分类", "动漫图片分类数据入口，适合类别筛选和分类器测试。"),
  hf("takkki/anime_image_classification", "Anime Classification 变体 A", "评估/分类", "动漫图片分类入口，用于分类标签与下载测试。"),
  hf("svjack/anime_image_classification", "Anime Classification 变体 B", "评估/分类", "动漫图片分类数据入口，适合小规模测试。"),
  hf("NandemoGHS/Chika", "Chika 角色数据", "角色/专题", "角色专题数据入口，适合角色专属素材管线测试。"),
  hf("NandemoGHS/AniFaceDrawing", "AniFaceDrawing", "角色/人脸", "动漫人脸绘制/头像相关数据入口。"),
  hf("NandemoGHS/anime-head-detection", "动漫头部检测", "角色/检测", "头部检测相关数据入口，适合检测训练和裁切。"),
  hf("NandemoGHS/anime-face-detector", "动漫脸部检测", "角色/检测", "脸部检测相关数据入口，用于自动裁脸和质量筛选。"),
  hf("NandemoGHS/anime_person_detection", "动漫人物检测", "角色/检测", "动漫人物检测数据入口，适合全身/半身检测测试。"),
  hf("NandemoGHS/anime_segmentation", "动漫分割数据", "分割/抠图", "动漫人物或画面分割入口，适合前景抠图和 mask 管线。"),
  hf("NandemoGHS/anime_character_classification", "动漫角色分类", "评估/分类", "角色分类数据入口，适合人物识别和标签归并。"),
  hf("NandemoGHS/anime_screenshot", "动画截图数据", "动画截图", "动画截图入口，适合场景、构图和画面质量分析。"),
  hf("NandemoGHS/anime_style", "动漫风格数据", "风格/标签", "动漫风格相关数据入口，适合风格标签测试。"),
  hf("NandemoGHS/anime_lineart", "动漫线稿入口", "线稿/上色", "线稿相关数据入口，适合上色和边线提取。"),
  hf("NandemoGHS/anime_colorization", "动漫上色入口", "线稿/上色", "上色相关数据入口，适合线稿到彩色任务。"),

  wikimediaCategory("Hokusai manga (The sketchbooks of Hokusai)", "北斋漫画分类", "公版/馆藏", "葛饰北斋相关公版素材，适合线稿、构图和传统日式视觉参考。", "3"),
  wikimediaCategory("Katsushika Hokusai", "葛饰北斋", "公版/馆藏", "葛饰北斋作品分类，适合日式构图和人物线稿参考。", "5"),
  wikimediaCategory("Kitazawa Rakuten", "北泽乐天", "公版/馆藏", "早期日本漫画家相关馆藏素材入口。", "5"),
  wikimediaCategory("Okamoto Ippei", "冈本一平", "公版/馆藏", "大正/昭和早期漫画与插画相关素材入口。", "5"),
  wikimediaCategory("Kawanabe Kyosai", "河锅晓斋", "公版/馆藏", "传统人物、妖怪、讽刺画风格参考。", "5"),
  wikimediaCategory("Utagawa Kuniyoshi", "歌川国芳", "公版/馆藏", "浮世绘人物、武者、奇想构图参考。", "5"),
  wikimediaCategory("Tsukioka Yoshitoshi", "月冈芳年", "公版/馆藏", "传统人物、戏剧化画面与构图参考。", "5"),
  wikimediaCategory("Japanese woodblock prints", "日本木版画", "公版/馆藏", "传统日式线条、色块、构图参考。", "5"),
  wikimediaCategory("Ukiyo-e", "浮世绘", "公版/馆藏", "大类浮世绘素材入口，适合历史视觉底座。", "5"),
  wikimediaCategory("Ehon", "绘本 Ehon", "公版/馆藏", "日本古绘本和插图书素材入口。", "5"),
  wikimediaCategory("Kibyoshi", "黄表纸 Kibyoshi", "公版/馆藏", "江户时期图文叙事资料，适合漫画史风格参考。", "5"),
  wikimediaCategory("Public domain comics", "公版漫画", "公版/馆藏", "Wikimedia 公版漫画分类，适合安全小规模测试。", "5"),
  wikimediaCategory("Open source comics", "开源漫画", "公版/馆藏", "开放源漫画分类，适合授权明确素材测试。", "5"),
  wikimediaCategory("Comic strips", "漫画条", "公版/馆藏", "漫画条和报纸漫画素材入口。", "5"),
  wikimediaCategory("Winsor McCay", "Winsor McCay", "公版/馆藏", "Little Nemo 作者相关公版素材入口。", "5"),
  wikimediaCategory("Little Nemo in Slumberland", "Little Nemo", "公版/馆藏", "经典彩色漫画条素材，适合分镜和幻想构图参考。", "5"),
  wikimediaCategory("George Herriman", "George Herriman", "公版/馆藏", "Krazy Kat 作者相关素材入口。", "5"),
  wikimediaCategory("Krazy Kat", "Krazy Kat", "公版/馆藏", "实验性漫画条和图文关系参考。", "5"),
  wikimediaCategory("Manga", "Manga 分类", "漫画/分类", "Wikimedia Manga 分类，适合搜索和小批量下载测试。", "5"),
  wikimediaCategory("Anime", "Anime 分类", "动画/分类", "Wikimedia Anime 分类，适合动画相关开放图像测试。", "5"),
  wikimediaCategory("Japanese animation", "日本动画", "动画/分类", "日本动画相关开放素材分类。", "5"),
  wikimediaCategory("Caricatures of Japan", "日本讽刺漫画", "漫画/历史", "历史讽刺漫画和人物夸张绘制参考。", "5"),
  wikimediaSearch("anime girl illustration", "Wikimedia 动漫少女插画搜索", "搜索/开放图像", "按关键词搜索开放图像，适合补充小样本测试。", "5"),
  wikimediaSearch("manga drawing", "Wikimedia 漫画绘图搜索", "搜索/开放图像", "漫画绘图关键词搜索，适合快速找开放图像。", "5"),
  wikimediaSearch("line art character", "Wikimedia 角色线稿搜索", "搜索/开放图像", "角色线稿关键词搜索，适合线稿上色测试。", "5"),
  wikimediaSearch("chibi illustration", "Wikimedia Q版插画搜索", "搜索/开放图像", "Q版/萌系插画关键词搜索。", "5"),
  wikimediaSearch("cosplay anime", "Wikimedia Cosplay 搜索", "搜索/开放图像", "Cosplay 开放图像，可作为角色服装参考。", "5"),
  wikimediaSearch("Japanese mascot character", "日本吉祥物角色搜索", "搜索/开放图像", "吉祥物/角色设计开放素材搜索。", "5"),

  ia("hokusaimanga01kats", "Hokusai Manga Vol. 1", "Internet Archive", "北斋漫画第 1 卷候选条目，先下载 PDF 测试。"),
  ia("hokusaimanga02kats", "Hokusai Manga Vol. 2", "Internet Archive", "北斋漫画第 2 卷候选条目，适合传统线稿参考。"),
  ia("hokusaimanga03kats", "Hokusai Manga Vol. 3", "Internet Archive", "北斋漫画第 3 卷候选条目。"),
  ia("hokusaimanga04kats", "Hokusai Manga Vol. 4", "Internet Archive", "已验证常见条目，适合测试 IA PDF 下载。"),
  ia("hokusaimanga05kats", "Hokusai Manga Vol. 5", "Internet Archive", "北斋漫画第 5 卷候选条目。"),
  ia("hokusaimanga06kats", "Hokusai Manga Vol. 6", "Internet Archive", "北斋漫画第 6 卷候选条目。"),
  ia("hokusaimanga07kats", "Hokusai Manga Vol. 7", "Internet Archive", "北斋漫画第 7 卷候选条目。"),
  ia("hokusaimanga08kats", "Hokusai Manga Vol. 8", "Internet Archive", "北斋漫画第 8 卷候选条目。"),
  ia("hokusaimanga09kats1912", "Hokusai Manga Vol. 9", "Internet Archive", "北斋漫画第 9 卷候选条目。"),
  ia("hokusaimanga10kats", "Hokusai Manga Vol. 10", "Internet Archive", "北斋漫画第 10 卷候选条目。"),
  ia("hokusaimanga11kats", "Hokusai Manga Vol. 11", "Internet Archive", "北斋漫画第 11 卷候选条目。"),
  ia("hokusaimanga12kats", "Hokusai Manga Vol. 12", "Internet Archive", "北斋漫画第 12 卷候选条目。"),
  ia("hokusaimanga13kats", "Hokusai Manga Vol. 13", "Internet Archive", "北斋漫画第 13 卷候选条目。"),
  ia("little-nemo-in-slumberland", "Little Nemo 候选条目", "Internet Archive", "Little Nemo 公版扫描候选入口，若失败可点来源页人工挑选 item。", "*.pdf,*.zip,*.cbz", "1"),
  ia("krazy-kat", "Krazy Kat 候选条目", "Internet Archive", "Krazy Kat 公版漫画条候选入口，若失败可用来源页搜索。", "*.pdf,*.zip,*.cbz", "1"),

  direct("https://opengameart.org/sites/default/files/ahkiabara.zip", "opengameart-ahkiabara.zip", "OpenGameArt 动漫精灵包", "游戏/开放素材", "anime-collection 的 zip 附件，包含 sprites 和 tilesets，适合快速验证直链下载。", "直链 · CC0 · 5.4MB"),
  wikimediaSearch("openclipart anime", "OpenClipart 动漫风格搜索", "搜索/开放图像", "通过 Wikimedia 搜索开放剪贴画和动漫风格素材。", "5"),
  wikimediaSearch("public domain cartoon character", "公版卡通角色搜索", "搜索/开放图像", "公版卡通角色关键词搜索，适合角色造型参考。", "5"),
  wikimediaSearch("public domain comic book", "公版漫画书搜索", "搜索/开放图像", "公版漫画书关键词搜索，适合找页面级样本。", "5"),
  wikimediaSearch("Japanese comic book", "日本漫画书搜索", "搜索/开放图像", "日本漫画/图书关键词搜索，适合开放图像探索。", "5"),
  wikimediaSearch("anime background", "动漫背景搜索", "搜索/开放图像", "开放图像中的动漫背景关键词搜索。", "5")
];

const generatedSubjects = [
  ["anime girl", "角色/人物"], ["anime boy", "角色/人物"], ["manga character", "角色/人物"], ["chibi character", "角色/人物"],
  ["kawaii mascot", "角色/人物"], ["magical girl", "角色/人物"], ["mecha robot", "机械/科幻"], ["cyberpunk anime", "机械/科幻"],
  ["samurai character", "历史/服装"], ["ninja character", "历史/服装"], ["yokai illustration", "妖怪/幻想"], ["kitsune illustration", "妖怪/幻想"],
  ["school uniform anime", "服装/道具"], ["sailor uniform illustration", "服装/道具"], ["kimono character", "服装/道具"], ["maid costume illustration", "服装/道具"],
  ["anime eyes", "角色/细节"], ["anime hair", "角色/细节"], ["anime face", "角色/细节"], ["anime hand pose", "姿势/动作"],
  ["action pose manga", "姿势/动作"], ["running pose illustration", "姿势/动作"], ["fighting pose illustration", "姿势/动作"], ["dance pose anime", "姿势/动作"],
  ["anime background", "背景/场景"], ["anime city", "背景/场景"], ["anime street", "背景/场景"], ["anime room", "背景/场景"],
  ["anime school", "背景/场景"], ["anime cafe", "背景/场景"], ["anime train station", "背景/场景"], ["anime landscape", "背景/场景"],
  ["Japanese shrine illustration", "背景/场景"], ["fantasy castle illustration", "背景/场景"], ["forest anime background", "背景/场景"], ["night city illustration", "背景/场景"],
  ["line art character", "线稿/上色"], ["manga line art", "线稿/上色"], ["coloring page anime", "线稿/上色"], ["black and white manga", "线稿/上色"],
  ["comic panel", "漫画/分镜"], ["manga panel", "漫画/分镜"], ["comic strip", "漫画/分镜"], ["speech bubble comic", "漫画/分镜"],
  ["anime screenshot", "动画截图"], ["cel animation", "动画截图"], ["Japanese animation still", "动画截图"], ["storyboard animation", "动画截图"],
  ["pixel art character", "游戏/开放素材"], ["game sprite anime", "游戏/开放素材"], ["visual novel background", "游戏/开放素材"], ["2d game character", "游戏/开放素材"],
  ["fantasy anime character", "幻想/题材"], ["dragon girl illustration", "幻想/题材"], ["witch anime", "幻想/题材"], ["angel anime character", "幻想/题材"],
  ["demon anime character", "幻想/题材"], ["catgirl illustration", "幻想/题材"], ["vampire anime", "幻想/题材"], ["steampunk anime", "机械/科幻"]
];

const generatedQualifiers = [
  ["public domain", "公版优先"], ["creative commons", "开放授权"], ["CC0", "开放授权"], ["open source", "开放授权"],
  ["Wikimedia Commons", "Wikimedia 搜索"], ["illustration", "插画"], ["drawing", "插画"], ["sketch", "线稿/草图"],
  ["lineart", "线稿/草图"], ["concept art", "设定/概念"], ["reference sheet", "设定/概念"], ["turnaround", "设定/概念"],
  ["background art", "背景/场景"], ["wallpaper", "背景/场景"], ["transparent png", "透明素材"], ["sprite sheet", "游戏/开放素材"],
  ["old Japan", "历史/公版"], ["vintage", "历史/公版"], ["woodblock print", "历史/公版"], ["ukiyo-e", "历史/公版"]
];

const iaTerms = [
  ["manga", "Internet Archive 搜索"], ["anime", "Internet Archive 搜索"], ["comic book", "Internet Archive 搜索"], ["comic strip", "Internet Archive 搜索"],
  ["Japanese comics", "Internet Archive 搜索"], ["Hokusai manga", "Internet Archive 搜索"], ["Little Nemo", "Internet Archive 搜索"], ["Krazy Kat", "Internet Archive 搜索"],
  ["public domain comics", "Internet Archive 搜索"], ["golden age comics", "Internet Archive 搜索"], ["cartoon drawing", "Internet Archive 搜索"], ["animation storyboard", "Internet Archive 搜索"],
  ["ukiyo-e", "Internet Archive 搜索"], ["woodblock print", "Internet Archive 搜索"], ["Japanese illustration", "Internet Archive 搜索"], ["ehon", "Internet Archive 搜索"],
  ["kibyoshi", "Internet Archive 搜索"], ["manga art book", "Internet Archive 搜索"], ["comic illustration", "Internet Archive 搜索"], ["public domain cartoon", "Internet Archive 搜索"]
];

function uniquePresets(items) {
  const seen = new Set();
  return items.filter(item => {
    const key = item.id;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

const generatedPresets = [];
for (const [subject, subjectGroup] of generatedSubjects) {
  for (const [qualifier, qualifierGroup] of generatedQualifiers) {
    const query = `${qualifier} ${subject}`;
    generatedPresets.push(wikimediaSearch(
      query,
      `${subject} · ${qualifier}`,
      `${subjectGroup} / ${qualifierGroup}`,
      `Wikimedia 关键词入口：${query}。适合先下载少量开放图像做筛选和训练管线测试。`,
      "3"
    ));
  }
}

for (const [term, group] of iaTerms) {
  for (const mediaType of ["mediatype:texts", "mediatype:image", "collection:comics", "collection:additional_collections"]) {
    const query = `${term} ${mediaType}`;
    generatedPresets.push(iaSearch(
      query,
      `${term} · ${mediaType}`,
      group,
      `Internet Archive 搜索入口：${query}。点击下载测试会先取 1 个条目的 1 个匹配文件。`
    ));
  }
}

window.ANIMA_PRESETS = uniquePresets([...window.ANIMA_PRESETS, ...generatedPresets]);
