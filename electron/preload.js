const { contextBridge, ipcRenderer } = require("electron");

const apiArg = process.argv.find((arg) => arg.startsWith("--tasktide-api-base="));
const apiBase = apiArg ? apiArg.slice("--tasktide-api-base=".length) : "http://127.0.0.1:8765";

contextBridge.exposeInMainWorld("tasktideNative", {
  showSystemNotification: (payload) => ipcRenderer.invoke("tasktide:show-system-notification", payload)
});

contextBridge.exposeInMainWorld("tasktideConfig", {
  apiBase
});
