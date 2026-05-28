const { app, BrowserWindow, dialog, shell } = require("electron");
const { spawn, spawnSync } = require("child_process");
const fs = require("fs");
const http = require("http");
const path = require("path");

const APP_TITLE = "贞贞的训练集下载器";
const DEFAULT_HOST = "127.0.0.1";
const DEFAULT_PORT = 8422;
const DEV_DATA_ROOT = "D:\\zhenzhen-asset";
const PACKAGED_DATA_DIR_NAME = "ZhenzhenTrainData";
const PORT_SCAN_COUNT = 20;

let mainWindow = null;
let backendProcess = null;
let backendUrl = null;

function backendExecutablePath() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, "backend", "zhenzhen-backend.exe");
  }
  return path.join(app.getAppPath(), "dist_backend", "zhenzhen-backend.exe");
}

function defaultDataRoot() {
  if (app.isPackaged) {
    return path.join(app.getPath("documents"), PACKAGED_DATA_DIR_NAME);
  }
  return DEV_DATA_ROOT;
}

function dataRoot() {
  return process.env.ANIMA_DATASET_ROOT || defaultDataRoot();
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1360,
    height: 900,
    minWidth: 980,
    minHeight: 680,
    title: APP_TITLE,
    backgroundColor: "#f6f8fb",
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  });

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  mainWindow.webContents.on("will-navigate", (event, url) => {
    if (backendUrl && url.startsWith(backendUrl)) return;
    if (url.startsWith("http://127.0.0.1:")) return;
    event.preventDefault();
    shell.openExternal(url);
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });

  return mainWindow;
}

function loadingHtml(message) {
  return `<!doctype html>
<html lang="zh-CN">
<meta charset="utf-8">
<title>${APP_TITLE}</title>
<body style="margin:0;background:#f6f8fb;color:#1b2430;font:14px 'Segoe UI',Arial,sans-serif;display:grid;place-items:center;height:100vh">
  <div style="width:min(520px,calc(100vw - 48px));border:1px solid #dfe6ee;background:#fff;border-radius:8px;padding:22px;box-shadow:0 10px 30px rgba(22,36,51,.08)">
    <h1 style="font-size:20px;margin:0 0 8px">${APP_TITLE}</h1>
    <p style="margin:0;color:#647184;line-height:1.6">${message}</p>
  </div>
</body>
</html>`;
}

function loadHtml(window, message) {
  window.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(loadingHtml(message))}`);
}

function httpJson(port, pathname = "/api/status", timeoutMs = 1200) {
  return new Promise((resolve, reject) => {
    const request = http.get(
      {
        host: DEFAULT_HOST,
        port,
        path: pathname,
        timeout: timeoutMs
      },
      response => {
        let body = "";
        response.setEncoding("utf8");
        response.on("data", chunk => {
          body += chunk;
        });
        response.on("end", () => {
          if (response.statusCode < 200 || response.statusCode >= 300) {
            reject(new Error(`HTTP ${response.statusCode}`));
            return;
          }
          try {
            resolve(JSON.parse(body));
          } catch (error) {
            reject(error);
          }
        });
      }
    );
    request.on("timeout", () => {
      request.destroy(new Error("timeout"));
    });
    request.on("error", reject);
  });
}

async function findRunningServer() {
  const expectedRoot = path.resolve(dataRoot()).toLowerCase();
  for (let offset = 0; offset < PORT_SCAN_COUNT; offset += 1) {
    const port = DEFAULT_PORT + offset;
    try {
      const status = await httpJson(port);
      const serverRoot = status.root ? path.resolve(status.root).toLowerCase() : "";
      if (serverRoot === expectedRoot) {
        return { port, url: `http://${DEFAULT_HOST}:${port}/`, existing: true };
      }
    } catch {
      // Keep scanning candidate ports.
    }
  }
  return null;
}

function parseBackendUrl(text) {
  const match = text.match(/http:\/\/127\.0\.0\.1:(\d+)\//);
  if (!match) return null;
  return { port: Number(match[1]), url: `http://${DEFAULT_HOST}:${match[1]}/`, existing: false };
}

async function startBackend() {
  const existing = await findRunningServer();
  if (existing) return existing;

  const exe = backendExecutablePath();
  if (!fs.existsSync(exe)) {
    throw new Error(`后端程序不存在：${exe}`);
  }

  return new Promise((resolve, reject) => {
    let settled = false;
    let output = "";
    const args = ["--host", DEFAULT_HOST, "--port", String(DEFAULT_PORT), "--root", dataRoot(), "--no-open"];
    backendProcess = spawn(exe, args, {
      cwd: path.dirname(exe),
      env: { ...process.env, ANIMA_DATASET_ROOT: dataRoot() },
      windowsHide: true
    });

    const finish = result => {
      if (settled) return;
      settled = true;
      clearInterval(poller);
      clearTimeout(timeout);
      resolve(result);
    };

    const fail = error => {
      if (settled) return;
      settled = true;
      clearInterval(poller);
      clearTimeout(timeout);
      reject(error);
    };

    const handleOutput = chunk => {
      output += chunk.toString();
      const parsed = parseBackendUrl(output);
      if (parsed) finish(parsed);
    };

    backendProcess.stdout.on("data", handleOutput);
    backendProcess.stderr.on("data", handleOutput);
    backendProcess.on("error", fail);
    backendProcess.on("exit", code => {
      if (!settled) {
        fail(new Error(`后端启动失败，退出码 ${code}。${output.trim()}`));
      }
    });

    const poller = setInterval(async () => {
      try {
        const running = await findRunningServer();
        if (running) finish({ ...running, existing: false });
      } catch {
        // Poll again until timeout.
      }
    }, 500);

    const timeout = setTimeout(() => {
      fail(new Error(`后端启动超时。${output.trim()}`));
    }, 30000);
  });
}

async function boot() {
  const window = createWindow();
  loadHtml(window, "正在启动本地后端，首次启动可能需要几秒钟。");
  try {
    const backend = await startBackend();
    backendUrl = backend.url;
    await window.loadURL(backendUrl);
  } catch (error) {
    const message = error && error.message ? error.message : String(error);
    loadHtml(window, `启动失败：${message}`);
    dialog.showErrorBox(APP_TITLE, message);
  }
}

app.whenReady().then(boot);

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    boot();
  }
});

app.on("window-all-closed", () => {
  app.quit();
});

function stopBackend() {
  if (!backendProcess || backendProcess.killed) return;
  if (process.platform === "win32") {
    spawnSync("taskkill", ["/pid", String(backendProcess.pid), "/T", "/F"], {
      windowsHide: true,
      stdio: "ignore"
    });
  } else {
    backendProcess.kill();
  }
  backendProcess = null;
}

app.on("before-quit", () => {
  stopBackend();
});
