const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('minh', {
  startPython: () => ipcRenderer.invoke('start-python'),
  stopPython: () => ipcRenderer.invoke('stop-python')
})
