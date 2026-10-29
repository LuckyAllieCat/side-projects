const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('widget', {
  resize: (height) => ipcRenderer.send('widget:resize', height),
  pin: (pinned) => ipcRenderer.send('widget:pin', pinned),
  minimize: () => ipcRenderer.send('widget:minimize'),
  open: (url) => ipcRenderer.send('widget:open', url),
  close: () => ipcRenderer.send('widget:close'),
  loadPins: () => ipcRenderer.invoke('pins:load'),
  savePins: (pins) => ipcRenderer.invoke('pins:save', pins),
  loadGif: () => ipcRenderer.invoke('gif:load'),
  saveGif: (dataUrl) => ipcRenderer.invoke('gif:save', dataUrl),
  clearGif: () => ipcRenderer.invoke('gif:clear')
});
