const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("booWatcher", {
  onMessage(callback) {
    const listener = (_event, payload) => callback(payload);
    ipcRenderer.on("boo:watcher-message", listener);
    ipcRenderer.send("boo:watcher-ready");
    return () => ipcRenderer.removeListener("boo:watcher-message", listener);
  },
});
