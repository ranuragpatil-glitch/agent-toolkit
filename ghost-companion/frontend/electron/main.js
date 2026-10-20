import { app, BrowserWindow, desktopCapturer, ipcMain, screen } from "electron";
import activeWindow from "active-win";
import { createWorker } from "tesseract.js";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const isDevelopment = !app.isPackaged;
const OLLAMA_URL = (process.env.OLLAMA_URL || "http://127.0.0.1:11434").replace(/\/$/, "");
const QWEN_MODEL = process.env.OLLAMA_MODEL || "qwen3:4b-instruct-2507-q4_K_M";
const WATCH_INTERVAL_MS = 5_000;
const CODE_EDITOR_NAMES = ["code", "cursor", "pycharm", "xcode", "visual studio code"];

let mainWindow;
let watcherTimer;
let watcherBusy = false;
let lastEditorFingerprint = "";
let permissionNoticeSent = false;
let ocrWorkerPromise;
let visionModelPromise;
let rendererReady = false;
let pendingWatcherMessages = [];

function enforceOverlayWindow(win) {
  if (!win || win.isDestroyed()) return;

  win.setAlwaysOnTop(true, "screen-saver");

  if (process.platform === "darwin") {
    win.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
    win.setFullScreenable(false);
  }
}

function sendWatcherMessage(payload) {
  if (!mainWindow || mainWindow.isDestroyed() || mainWindow.webContents.isDestroyed() || !rendererReady) {
    pendingWatcherMessages = [...pendingWatcherMessages, payload].slice(-20);
    return;
  }
  mainWindow.webContents.send("boo:watcher-message", payload);
}

function showScreenRecordingNotice() {
  if (permissionNoticeSent) return;
  permissionNoticeSent = true;
  sendWatcherMessage({
    type: "permission",
    mood: "concerned",
    text: "Pookie ko editor dekhne ke liye macOS ki Screen Recording aur Accessibility permissions chahiye 👀\nSystem Settings → Privacy & Security → Screen Recording + Accessibility mein Pookie Ghost Companion ko enable karke app restart kar do.",
  });
}

function isCodeEditor(name = "") {
  const normalized = name.toLowerCase();
  return CODE_EDITOR_NAMES.some((editorName) => normalized === editorName || normalized.includes(editorName));
}

async function findVisionModel() {
  if (!visionModelPromise) {
    visionModelPromise = fetch(`${OLLAMA_URL}/api/tags`)
      .then((response) => (response.ok ? response.json() : { models: [] }))
      .then((body) => {
        const models = Array.isArray(body.models) ? body.models : [];
        const match = models.find((model) => /vision|llava/i.test(model.name || model.model || ""));
        return match?.name || match?.model || null;
      })
      .catch(() => null);
  }
  return visionModelPromise;
}

async function captureEditorWindow(active) {
  const sources = await desktopCapturer.getSources({
    types: ["window"],
    thumbnailSize: { width: 1600, height: 1000 },
    fetchWindowIcons: false,
  });
  const activeId = String(active.id);
  const source = sources.find((candidate) => candidate.id.includes(`window:${activeId}:`))
    || sources.find((candidate) => candidate.name === active.title);

  if (!source?.thumbnail || source.thumbnail.isEmpty()) {
    throw new Error("Editor window capture was empty; Screen Recording permission may be missing.");
  }

  const image = source.thumbnail.toPNG();
  if (!image?.length) {
    throw new Error("Editor window capture returned no image data.");
  }
  return image;
}

async function getOcrText(image) {
  if (!ocrWorkerPromise) {
    ocrWorkerPromise = createWorker("eng").catch((error) => {
      ocrWorkerPromise = null;
      throw error;
    });
  }
  const worker = await ocrWorkerPromise;
  const result = await worker.recognize(image);
  return result.data.text.trim();
}

async function askLocalModel({ image, ocrText, visionModel }) {
  const prompt = [
    "You are Pookie, a concise local coding companion.",
    "Look at the current code editor window and suggest one short, genuinely useful code improvement or next step.",
    "Do not invent context that is not visible. If there is not enough code to help, say so briefly.",
    "Reply in short supportive Hinglish, maximum 2-3 lines. Do not use markdown headings.",
  ].join(" ");
  const message = {
    role: "user",
    content: visionModel ? prompt : `${prompt}\n\nOCR text from the editor window:\n${ocrText || "(No readable code was detected.)"}`,
  };
  if (visionModel) message.images = [image.toString("base64")];

  const response = await fetch(`${OLLAMA_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: visionModel || QWEN_MODEL,
      stream: false,
      think: false,
      options: { temperature: 0.2, num_predict: 180 },
      messages: [message],
    }),
  });
  if (!response.ok) throw new Error(`Ollama returned HTTP ${response.status}`);
  const body = await response.json();
  const reply = String(body.message?.content || "").replace(/<think>[\s\S]*?<\/think>/gi, "").trim();
  if (!reply) throw new Error("Ollama returned an empty suggestion.");
  return reply;
}

async function pollActiveEditor() {
  if (watcherBusy) return;

  let active;
  try {
    active = await activeWindow({ screenRecordingPermission: true });
  } catch (error) {
    const errorText = [error?.message, error?.stdout, error?.stderr].filter(Boolean).join(" ");
    if (process.platform === "darwin" && /permission|screen|accessibility/i.test(errorText)) {
      showScreenRecordingNotice();
    }
    return;
  }

  const editorName = active?.owner?.name || "";
  if (!active || !isCodeEditor(editorName)) return;
  if (!active.title) {
    showScreenRecordingNotice();
    return;
  }

  const fingerprint = `${editorName}|${active.id}|${active.title}`;
  if (fingerprint === lastEditorFingerprint) return;
  lastEditorFingerprint = fingerprint;
  watcherBusy = true;

  try {
    const image = await captureEditorWindow(active);
    const visionModel = await findVisionModel();
    const ocrText = visionModel ? "" : await getOcrText(image);
    const reply = await askLocalModel({ image, ocrText, visionModel });
    sendWatcherMessage({
      type: "suggestion",
      mood: "thinking",
      text: reply,
      analysisPath: visionModel ? "vision" : "ocr+text",
    });
  } catch (error) {
    if (/capture|screen recording|permission|empty/i.test(error.message || "")) {
      showScreenRecordingNotice();
    }
  } finally {
    watcherBusy = false;
  }
}

function startEditorWatcher() {
  if (watcherTimer) return;
  watcherTimer = setInterval(() => {
    pollActiveEditor().catch(() => {});
  }, WATCH_INTERVAL_MS);
  pollActiveEditor().catch(() => {});
}

function createWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;
  const windowWidth = 440;
  const windowHeight = 700;

  mainWindow = new BrowserWindow({
    width: windowWidth,
    height: windowHeight,
    x: Math.max(0, width - windowWidth - 20),
    y: Math.max(0, height - windowHeight - 20),
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    resizable: false,
    movable: true,
    skipTaskbar: true,
    hasShadow: false,
    backgroundColor: "#00000000",
    show: false,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      preload: path.join(__dirname, "preload.cjs"),
    },
  });

  enforceOverlayWindow(mainWindow);

  if (isDevelopment) {
    mainWindow.loadURL("http://localhost:5173");
  } else {
    mainWindow.loadFile(path.join(__dirname, "..", "dist", "index.html"));
  }

  mainWindow.once("ready-to-show", () => {
    enforceOverlayWindow(mainWindow);
    mainWindow.showInactive();
    enforceOverlayWindow(mainWindow);
    startEditorWatcher();
  });
  mainWindow.on("show", () => enforceOverlayWindow(mainWindow));
  mainWindow.on("restore", () => enforceOverlayWindow(mainWindow));
  mainWindow.on("closed", () => {
    if (watcherTimer) clearInterval(watcherTimer);
    watcherTimer = null;
    rendererReady = false;
    mainWindow = null;
  });
}

ipcMain.on("boo:watcher-ready", (event) => {
  if (!mainWindow || event.sender !== mainWindow.webContents) return;
  rendererReady = true;
  for (const payload of pendingWatcherMessages) {
    mainWindow.webContents.send("boo:watcher-message", payload);
  }
  pendingWatcherMessages = [];
});

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
