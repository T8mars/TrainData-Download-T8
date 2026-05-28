const state = {
  activeTab: "direct",
  activity: [],
  presetPage: 1,
  presetPageSize: 9,
  catalogLoaded: false
};

const tabs = {
  direct: "directForm",
  hf: "hfForm",
  wikimedia: "wikimediaForm",
  ia: "iaForm",
  iaSearch: "iaSearchForm",
  kaggle: "kaggleForm",
  zenodo: "zenodoForm",
  github: "githubForm",
  booru: "booruForm",
  local: "localForm"
};

const builtinPresets = [
  {
    id: "anime-bg",
    tab: "hf",
    title: "Anime BG 背景图",
    badge: "HF · CC0 · WebDataset",
    description: "动漫背景/壁纸图，适合先做背景、构图、场景风格预训练。先下载 1 个 tar 分片试跑。",
    fields: {repo_id: "deepghs/anime-bg", include: "*.tar", max_files: "1"},
    endpoint: "/api/hf",
    sourceUrl: "https://huggingface.co/datasets/deepghs/anime-bg"
  },
  {
    id: "csip-eval",
    tab: "hf",
    title: "CSIP 动漫风格评估集",
    badge: "HF · CC-BY-4.0 · 小型",
    description: "人工整理的动漫风格分类/评估数据，体量较小，适合测试管线和风格分类。",
    fields: {repo_id: "deepghs/csip_eval", include: "*.parquet", max_files: "1"},
    endpoint: "/api/hf",
    sourceUrl: "https://huggingface.co/datasets/deepghs/csip_eval"
  },
  {
    id: "animes-small",
    tab: "hf",
    title: "Animes 图像集",
    badge: "HF · CC-BY-4.0 · 约 829MB",
    description: "动漫图像数据集，页面标注 CC BY 4.0。适合做小规模图像下载测试。",
    fields: {repo_id: "Dhiraj45/Animes", include: "*.parquet", max_files: "1"},
    endpoint: "/api/hf",
    sourceUrl: "https://huggingface.co/datasets/Dhiraj45/Animes"
  },
  {
    id: "opengameart-cc0",
    tab: "hf",
    title: "OpenGameArt CC0 索引",
    badge: "HF · CC0 · 游戏/动漫素材",
    description: "OpenGameArt CC0 素材索引，含 2D 图像、精灵、贴图和附件 URL，适合后续批量扩展。",
    fields: {repo_id: "nyuuzyou/OpenGameArt-CC0", include: "*.parquet", max_files: "1"},
    endpoint: "/api/hf",
    sourceUrl: "https://huggingface.co/datasets/nyuuzyou/OpenGameArt-CC0"
  },
  {
    id: "opengameart-anime-zip",
    tab: "direct",
    title: "OpenGameArt 动漫精灵包",
    badge: "直链 · CC0 · 5.4MB",
    description: "anime-collection 的 zip 附件，包含 sprites 和 tilesets，适合快速验证直链下载。",
    fields: {
      url: "https://opengameart.org/sites/default/files/ahkiabara.zip",
      filename: "opengameart-ahkiabara.zip",
      header: ""
    },
    endpoint: "/api/download-url",
    sourceUrl: "https://opengameart.org/content/anime-collection"
  },
  {
    id: "hokusai-commons",
    tab: "wikimedia",
    title: "北斋漫画 Commons 分类",
    badge: "Wikimedia · 公版",
    description: "葛饰北斋相关公版素材，适合线稿、构图、传统日式视觉参考。默认最多 3 个文件。",
    fields: {
      mode: "category",
      query: "Hokusai manga (The sketchbooks of Hokusai)",
      limit: "50",
      max_files: "3"
    },
    endpoint: "/api/wikimedia",
    sourceUrl: "https://commons.wikimedia.org/wiki/Category:Hokusai_manga_(The_sketchbooks_of_Hokusai)"
  },
  {
    id: "hokusai-ia",
    tab: "ia",
    title: "Hokusai Manga PDF",
    badge: "Internet Archive · PDF",
    description: "互联网档案馆中的北斋漫画条目，先下载 1 个 PDF 测试档案馆插件。",
    fields: {item_id: "hokusaimanga04kats", include: "*.pdf", max_files: "1"},
    endpoint: "/api/ia",
    sourceUrl: "https://archive.org/details/hokusaimanga04kats"
  },
  {
    id: "manga109s",
    tab: "hf",
    title: "Manga109-s",
    badge: "HF · 需申请/token",
    description: "更接近现代漫画的数据集。需要在 Hugging Face 页面申请并接受条款后，填 token 再下载。",
    fields: {repo_id: "hal-utokyo/Manga109-s", include: "*.zip", max_files: "1"},
    endpoint: "/api/hf",
    sourceUrl: "https://huggingface.co/datasets/hal-utokyo/Manga109-s"
  },
  {
    id: "animepics",
    tab: "hf",
    title: "AnimePics 大规模预训练集",
    badge: "HF · 需同意访问 · 很大",
    description: "大规模 WebDataset 动漫图像预训练集，建议只在确认磁盘空间后从 1 个 tar 分片开始。",
    fields: {repo_id: "zenless-fab/animepics", include: "*.tar", max_files: "1"},
    endpoint: "/api/hf",
    sourceUrl: "https://huggingface.co/datasets/zenless-fab/animepics"
  }
];

let presets = window.ANIMA_PRESETS || builtinPresets;
let providerLabels = {
  direct: "直链",
  hf: "Hugging Face",
  wikimedia: "Wikimedia",
  ia: "Internet Archive Item",
  iaSearch: "Internet Archive 搜索",
  kaggle: "Kaggle",
  zenodo: "Zenodo",
  github: "GitHub Releases",
  booru: "Booru",
  local: "本地导入"
};

function byId(id) {
  return document.getElementById(id);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: {"Content-Type": "application/json"},
    ...options
  });
  const data = await response.json();
  if (!response.ok || data.ok === false) {
    throw new Error(data.error || `请求失败：${response.status}`);
  }
  return data;
}

function formData(form) {
  return Object.fromEntries(new FormData(form).entries());
}

async function loadCatalog() {
  const catalog = await api("/api/catalog");
  presets = catalog.items || presets;
  providerLabels = Object.fromEntries((catalog.providers || []).map(provider => [provider.id, provider.label]));
  state.catalogLoaded = true;
  renderPresetGroups();
  renderPresets();
}

function setFormValues(formId, values) {
  const form = byId(formId);
  Object.entries(values).forEach(([key, value]) => {
    const input = form.querySelector(`[name="${key}"]`);
    if (!input) return;
    if (input.type === "radio") {
      const radio = form.querySelector(`[name="${key}"][value="${value}"]`);
      if (radio) radio.checked = true;
    } else {
      input.value = value ?? "";
    }
  });
}

function setToast(message, isError = false) {
  const toast = byId("toast");
  toast.textContent = message;
  toast.classList.toggle("error", isError);
}

function statusClass(status) {
  const lower = String(status || "").toLowerCase();
  if (lower.includes("fail")) return "status fail";
  if (lower.includes("run") || lower.includes("queue")) return "status run";
  if (lower.includes("extract")) return "status extracted";
  return "status down";
}

function displayStatus(status) {
  const value = String(status || "");
  const map = {
    DOWNLOADED: "已下载",
    EXTRACTED: "已解包",
    FAILED: "失败",
    RUNNING: "运行中",
    QUEUED: "排队中"
  };
  return map[value] || value;
}

function displayLevel(level) {
  const map = {
    http: "请求",
    info: "信息",
    error: "错误"
  };
  return map[level] || level;
}

function renderRows(tableId, rows, renderer) {
  const tbody = document.querySelector(`#${tableId} tbody`);
  tbody.innerHTML = rows.map(renderer).join("");
}

function shortHash(value) {
  if (!value) return "";
  return value.length > 18 ? `${value.slice(0, 18)}...` : value;
}

function formatTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false
  });
}

async function refresh() {
  const [status, jobs, assets] = await Promise.all([
    api("/api/status"),
    api("/api/jobs"),
    api("/api/assets")
  ]);

  byId("rootPath").textContent = status.root;
  const rootInput = byId("rootInput");
  if (document.activeElement !== rootInput) {
    rootInput.value = status.root;
  }
  byId("pythonInfo").textContent = `${status.version} · ${status.python}`;
  byId("assetCount").textContent = status.asset_count;
  byId("completedCount").textContent = status.job_counts.DOWNLOADED || 0;
  byId("failedCount").textContent = status.job_counts.FAILED || 0;
  byId("runningCount").textContent = status.job_counts.RUNNING || 0;
  byId("downloadedCount").textContent = status.job_counts.DOWNLOADED || 0;
  byId("overviewFailed").textContent = status.job_counts.FAILED || 0;

  renderRows("jobsTable", jobs.jobs, row => `
    <tr>
      <td><span class="${statusClass(row.status)}">${displayStatus(row.status)}</span></td>
      <td>${escapeHtml(row.source_id)}</td>
      <td class="path-cell" title="${escapeHtml(row.target_path)}">${escapeHtml(row.target_path)}</td>
      <td>${escapeHtml(row.error || "")}</td>
    </tr>
  `);

  renderRows("assetsTable", assets.assets, row => `
    <tr>
      <td><span class="${statusClass(row.status)}">${displayStatus(row.status)}</span></td>
      <td class="time-cell" title="${escapeHtml(row.created_at)}">${escapeHtml(formatTime(row.created_at))}</td>
      <td>${escapeHtml(row.source_id)}</td>
      <td class="path-cell" title="${escapeHtml(row.local_path)}">${escapeHtml(row.local_path)}</td>
      <td class="hash-cell" title="${escapeHtml(row.sha256)}">${escapeHtml(shortHash(row.sha256))}</td>
    </tr>
  `);

  state.activity = status.activity || [];
  byId("activityLog").textContent = state.activity.map(item => `[${displayLevel(item.level)}] ${item.message}`).join("\n");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function selectTab(tab) {
  state.activeTab = tab;
  document.querySelectorAll(".source-card").forEach(card => {
    card.classList.toggle("selected", card.dataset.tab === tab);
  });
  Object.entries(tabs).forEach(([key, formId]) => {
    byId(formId).classList.toggle("active", key === tab);
  });
}

function renderPresets() {
  const grid = byId("presetGrid");
  const visiblePresets = filteredPresets();
  const totalPages = Math.max(1, Math.ceil(visiblePresets.length / state.presetPageSize));
  if (state.presetPage > totalPages) state.presetPage = totalPages;
  if (state.presetPage < 1) state.presetPage = 1;
  const start = (state.presetPage - 1) * state.presetPageSize;
  const pageItems = visiblePresets.slice(start, start + state.presetPageSize);
  byId("presetCount").textContent = `${visiblePresets.length} / ${presets.length} 个来源`;
  byId("presetPageInfo").textContent = `第 ${state.presetPage} / ${totalPages} 页`;
  byId("presetPrev").disabled = state.presetPage <= 1;
  byId("presetNext").disabled = state.presetPage >= totalPages;
  grid.innerHTML = pageItems.map(preset => `
    <article class="preset-card">
      <div class="preset-top">
        <span>${escapeHtml(preset.badge || preset.group || "来源")}</span>
        <a href="${escapeHtml(preset.sourceUrl)}" target="_blank" rel="noreferrer">来源</a>
      </div>
      <h3>${escapeHtml(preset.title)}</h3>
      <div class="preset-group">${escapeHtml(preset.group || "未分类")}</div>
      <p>${escapeHtml(preset.description)}</p>
      <div class="preset-actions">
        <button class="secondary-button" type="button" data-preset-fill="${escapeHtml(preset.id)}">填入参数</button>
        <button class="secondary-button" type="button" data-preset-preflight="${escapeHtml(preset.id)}">预检</button>
        <button class="primary-button" type="button" data-preset-run="${escapeHtml(preset.id)}">下载测试</button>
      </div>
    </article>
  `).join("");
}

function renderPresetGroups() {
  const select = byId("presetGroup");
  const groups = [...new Set(presets.map(preset => preset.group).filter(Boolean))].sort((a, b) => a.localeCompare(b, "zh-Hans-CN"));
  select.innerHTML = `<option value="">全部分类</option>` + groups.map(group => `<option value="${escapeHtml(group)}">${escapeHtml(group)}</option>`).join("");

  const typeSelect = byId("presetType");
  const types = [...new Set(presets.map(preset => preset.tab).filter(Boolean))].sort();
  typeSelect.innerHTML = `<option value="">全部来源类型</option>` + types.map(type => `<option value="${escapeHtml(type)}">${escapeHtml(providerLabels[type] || type)}</option>`).join("");
}

function filteredPresets() {
  const query = byId("presetSearch")?.value.trim().toLowerCase() || "";
  const group = byId("presetGroup")?.value || "";
  const type = byId("presetType")?.value || "";
  return presets.filter(preset => {
    const haystack = [
      preset.title,
      preset.badge,
      preset.group,
      preset.description,
      preset.sourceUrl,
      preset.provider,
      preset.fields?.repo_id,
      preset.fields?.query,
      preset.fields?.item_id,
      preset.fields?.dataset,
      preset.fields?.repo,
      preset.fields?.tags,
      preset.fields?.url
    ].join(" ").toLowerCase();
    return (!group || preset.group === group) && (!type || preset.tab === type) && (!query || haystack.includes(query));
  });
}

function applyPreset(preset) {
  const provider = preset.provider || preset.tab;
  selectTab(provider);
  setFormValues(tabs[provider], preset.fields);
  byId("downloadPanel").scrollIntoView({behavior: "smooth", block: "start"});
  setToast(`已填入：${preset.title}`);
}

async function runPreset(preset) {
  applyPreset(preset);
  try {
    const data = await api(preset.endpoint, {
      method: "POST",
      body: JSON.stringify(preset.fields)
    });
    setToast(data.message || `${preset.title} 下载任务已开始`);
    await refresh();
  } catch (error) {
    setToast(error.message, true);
  }
}

async function preflightPreset(preset) {
  applyPreset(preset);
  await runPreflight(preset.provider || preset.tab, preset.fields);
}

function renderPreflight(result) {
  const box = byId("preflightBox");
  const samples = result.samples || [];
  box.innerHTML = `
    <strong>${escapeHtml(result.message || "预检完成")}</strong>
    <span>命中：${escapeHtml(result.count ?? samples.length)} 个</span>
    <ul>
      ${samples.slice(0, 6).map(sample => `<li>${escapeHtml(sample.name || sample.url || sample.item || "文件")} ${sample.size ? `· ${escapeHtml(sample.size)}` : ""}</li>`).join("")}
    </ul>
  `;
}

async function runPreflight(provider = state.activeTab, fields = null) {
  const formId = tabs[provider];
  if (!formId) return;
  const payload = {
    provider,
    fields: fields || formData(byId(formId))
  };
  setToast("正在预检...");
  try {
    const data = await api("/api/preflight", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    renderPreflight(data.preflight || data);
    setToast("预检完成");
  } catch (error) {
    byId("preflightBox").innerHTML = `<strong>预检失败</strong><span>${escapeHtml(error.message)}</span>`;
    setToast(error.message, true);
  }
}

async function submitForm(form, path, transform = values => values) {
  const button = form.querySelector("button[type='submit']");
  button.disabled = true;
  try {
    const data = await api(path, {
      method: "POST",
      body: JSON.stringify(transform(formData(form)))
    });
    setToast(data.message || `已完成${data.count ? `：${data.count} 项` : ""}`);
    form.reset();
    await refresh();
  } catch (error) {
    setToast(error.message, true);
  } finally {
    button.disabled = false;
  }
}

document.querySelectorAll(".source-card").forEach(card => {
  card.addEventListener("click", () => selectTab(card.dataset.tab));
});

byId("presetGrid").addEventListener("click", event => {
  const fillId = event.target.dataset.presetFill;
  const runId = event.target.dataset.presetRun;
  const preflightId = event.target.dataset.presetPreflight;
  const preset = presets.find(item => item.id === (fillId || runId || preflightId));
  if (!preset) return;
  if (fillId) applyPreset(preset);
  if (preflightId) preflightPreset(preset);
  if (runId) runPreset(preset);
});

byId("presetSearch").addEventListener("input", () => { state.presetPage = 1; renderPresets(); });
byId("presetGroup").addEventListener("change", () => { state.presetPage = 1; renderPresets(); });
byId("presetType").addEventListener("change", () => { state.presetPage = 1; renderPresets(); });
byId("presetPrev").addEventListener("click", () => { state.presetPage -= 1; renderPresets(); });
byId("presetNext").addEventListener("click", () => { state.presetPage += 1; renderPresets(); });

document.querySelectorAll(".nav-item").forEach(button => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach(item => item.classList.remove("active"));
    button.classList.add("active");
    byId(button.dataset.focus).scrollIntoView({behavior: "smooth", block: "start"});
  });
});

byId("initBtn").addEventListener("click", async () => {
  try {
    const data = await api("/api/init", {method: "POST", body: "{}"});
    setToast(data.message);
    await refresh();
  } catch (error) {
    setToast(error.message, true);
  }
});

byId("refreshBtn").addEventListener("click", () => refresh().catch(error => setToast(error.message, true)));
byId("preflightBtn").addEventListener("click", () => runPreflight());

byId("rootForm").addEventListener("submit", async event => {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector("button[type='submit']");
  button.disabled = true;
  try {
    const data = await api("/api/root", {
      method: "POST",
      body: JSON.stringify(formData(form))
    });
    setToast(data.message || "下载目录已更新");
    state.presetPage = 1;
    await refresh();
  } catch (error) {
    setToast(error.message, true);
  } finally {
    button.disabled = false;
  }
});

byId("directForm").addEventListener("submit", event => {
  event.preventDefault();
  submitForm(event.currentTarget, "/api/download-url");
});

byId("hfForm").addEventListener("submit", event => {
  event.preventDefault();
  submitForm(event.currentTarget, "/api/hf");
});

byId("wikimediaForm").addEventListener("submit", event => {
  event.preventDefault();
  submitForm(event.currentTarget, "/api/wikimedia");
});

byId("iaForm").addEventListener("submit", event => {
  event.preventDefault();
  submitForm(event.currentTarget, "/api/ia");
});

byId("iaSearchForm").addEventListener("submit", event => {
  event.preventDefault();
  submitForm(event.currentTarget, "/api/ia-search");
});

byId("kaggleForm").addEventListener("submit", event => {
  event.preventDefault();
  submitForm(event.currentTarget, "/api/kaggle");
});

byId("zenodoForm").addEventListener("submit", event => {
  event.preventDefault();
  submitForm(event.currentTarget, "/api/zenodo");
});

byId("githubForm").addEventListener("submit", event => {
  event.preventDefault();
  submitForm(event.currentTarget, "/api/github");
});

byId("booruForm").addEventListener("submit", event => {
  event.preventDefault();
  submitForm(event.currentTarget, "/api/booru");
});

byId("localForm").addEventListener("submit", event => {
  event.preventDefault();
  const submitter = event.submitter;
  const path = submitter?.dataset.mode === "extract" ? "/api/extract" : "/api/import";
  submitForm(event.currentTarget, path);
});

byId("clearActivity").addEventListener("click", () => {
  byId("activityLog").textContent = "";
});

selectTab("direct");
renderPresetGroups();
renderPresets();
loadCatalog().catch(error => {
  setToast(`目录加载失败，使用内置预设：${error.message}`, true);
});
refresh().catch(error => setToast(error.message, true));
setInterval(() => refresh().catch(() => {}), 3500);
