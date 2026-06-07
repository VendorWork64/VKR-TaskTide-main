const { app, BrowserWindow, screen, ipcMain, Notification } = require("electron");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const BASE_WIDTH = 1280;
const MIN_WIDTH = 960;
const API_BASE = process.env.TASKTIDE_API_BASE || "http://127.0.0.1:8765";

let mainWindow = null;
let bundledApiProcess = null;

function parseApiBase(rawValue) {
  try {
    return new URL(rawValue);
  } catch {
    return new URL("http://127.0.0.1:8765");
  }
}

function resolveBundledApiExecutable() {
  const binDir = path.join(process.resourcesPath, "server-bin");
  if (process.platform === "win32") {
    return path.join(binDir, "tasktide-api-server.exe");
  }
  return path.join(binDir, "tasktide-api-server");
}

function startBundledApiServerIfNeeded() {
  if (!app.isPackaged) return null;

  const parsed = parseApiBase(API_BASE);
  if (!["127.0.0.1", "localhost"].includes(parsed.hostname)) {
    return null;
  }

  const apiExecutable = resolveBundledApiExecutable();
  if (!fs.existsSync(apiExecutable)) {
    console.warn(`Bundled API executable not found: ${apiExecutable}`);
    return null;
  }

  const userDataDir = app.getPath("userData");
  const serverDataDir = path.join(userDataDir, "server-data");
  fs.mkdirSync(serverDataDir, { recursive: true });

  const serverDbPath = path.join(serverDataDir, "tasktide_server.db");
  const jwtSecretPath = path.join(serverDataDir, "jwt_secret.txt");
  const port = parsed.port || "8765";
  const host = parsed.hostname === "localhost" ? "127.0.0.1" : parsed.hostname;

  const child = spawn(apiExecutable, [], {
    cwd: serverDataDir,
    env: {
      ...process.env,
      TASKTIDE_HOST: host,
      TASKTIDE_PORT: String(port),
      TASKTIDE_DB_PATH: serverDbPath,
      TASKTIDE_JWT_SECRET_FILE: jwtSecretPath
    },
    stdio: "ignore",
    windowsHide: true
  });

  child.unref();
  return child;
}

function stopBundledApiServer() {
  if (!bundledApiProcess || bundledApiProcess.killed) return;
  try {
    bundledApiProcess.kill("SIGTERM");
  } catch {
    // ignore
  }
}

function createWindow() {
  const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize;
  const fullscreenAspect = screenWidth / screenHeight;
  const baseHeight = Math.round(BASE_WIDTH / fullscreenAspect);

  mainWindow = new BrowserWindow({
    width: BASE_WIDTH,
    height: baseHeight,
    minWidth: MIN_WIDTH,
    minHeight: Math.round(MIN_WIDTH / fullscreenAspect),
    useContentSize: true,
    resizable: true,
    maximizable: true,
    fullscreenable: true,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, "preload.js"),
      additionalArguments: [`--tasktide-api-base=${API_BASE}`]
    }
  });

  const applyResponsiveZoom = () => {
    const [contentWidth, contentHeight] = mainWindow.getContentSize();
    const widthScale = contentWidth / BASE_WIDTH;
    const heightScale = contentHeight / baseHeight;
    const nextZoom = Math.max(0.78, Math.min(1.3, Math.min(widthScale, heightScale)));
    mainWindow.webContents.setZoomFactor(nextZoom);
  };

  mainWindow.on("resize", applyResponsiveZoom);
  mainWindow.webContents.on("did-finish-load", applyResponsiveZoom);
  mainWindow.setAspectRatio(fullscreenAspect);
  mainWindow.loadFile(path.join(__dirname, "index.html"));
}

ipcMain.handle("tasktide:show-system-notification", (_event, payload) => {
  try {
    const title = String(payload?.title || "TaskTide");
    const body = String(payload?.body || "");
    const silent = Boolean(payload?.silent);
    const notification = new Notification({ title, body, silent });
    notification.show();
    return { ok: true };
  } catch (error) {
    return { ok: false, error: String(error?.message || error) };
  }
});

app.whenReady().then(() => {
  bundledApiProcess = startBundledApiServerIfNeeded();
  createWindow();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on("before-quit", () => {
  stopBundledApiServer();
});

app.on("window-all-closed", () => {
  stopBundledApiServer();
  if (process.platform !== "darwin") {
    app.quit();
  }
});
