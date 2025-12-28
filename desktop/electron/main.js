const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')
const { spawn } = require('child_process')

let mainWindow
let pythonProcess = null

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 700,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  })

  // Development: load from Vite dev server
  if (process.env.NODE_ENV !== 'production') {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    // Production: load from dist
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'))
  }
}

app.whenReady().then(() => {
  createWindow()
  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit()
})

ipcMain.handle('start-python', async () => {
  if (pythonProcess) return { ok: true, pid: pythonProcess.pid }
  
  // Use .venv environment python
  const projectRoot = path.join(__dirname, '..', '..')
  const venvPython = path.join(projectRoot, '.venv', 'Scripts', 'python.exe')
  const pyPath = venvPython
  
  console.log('Starting Python with:', pyPath)
  
  // Start FastAPI server instead of main.py
  pythonProcess = spawn(pyPath, [
    '-m', 'uvicorn', 
    'api_server:app', 
    '--host', '127.0.0.1', 
    '--port', '8000'
  ], {
    cwd: path.join(__dirname, '..', '..'),
    stdio: 'pipe'
  })
  
  // Log output for debugging
  pythonProcess.stdout.on('data', (data) => {
    console.log(`[Python API] ${data}`)
  })
  
  pythonProcess.stderr.on('data', (data) => {
    console.error(`[Python API Error] ${data}`)
  })
  
  pythonProcess.on('close', (code) => {
    console.log(`Python API process exited with code ${code}`)
    pythonProcess = null
  })
  
  return { ok: true, pid: pythonProcess.pid }
})

ipcMain.handle('stop-python', async () => {
  if (!pythonProcess) return { ok: false, reason: 'not running' }
  try {
    process.kill(pythonProcess.pid)
    pythonProcess = null
    return { ok: true }
  } catch (e) {
    return { ok: false, reason: String(e) }
  }
})
