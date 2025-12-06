# MINH Desktop (Electron + Vite + React + Tailwind)

GUI giống Microsoft Copilot cho MINH AI Assistant.

---

## 📋 Yêu cầu hệ thống

- **Windows 10/11** (64-bit)
- **Node.js** >= 18.x (khuyến nghị LTS 20.x)
- **npm** >= 9.x (đi kèm với Node.js)
- **Python 3.11+** và conda environment `minh-ai` (cho backend)

---

## 🔧 Cài đặt Node.js (Windows)

### Cách 1: Tải trực tiếp từ trang chủ (Khuyến nghị)

1. Truy cập: https://nodejs.org/
2. Tải **LTS version** (ví dụ: 20.11.0)
3. Chạy file `.msi` vừa tải về
4. Trong quá trình cài đặt:
   - ✅ Chọn "Automatically install the necessary tools" (tự động cài build tools)
   - ✅ Chọn "Add to PATH" (thêm vào biến môi trường)
5. Sau khi cài xong, **khởi động lại PowerShell**
6. Kiểm tra:
   ```powershell
   node --version
   npm --version
   ```
   Kết quả mong đợi:
   ```
   v20.11.0
   10.2.4
   ```

### Cách 2: Dùng Chocolatey (nếu đã cài Chocolatey)

```powershell
choco install nodejs-lts -y
```

### Cách 3: Dùng Winget (Windows 11)

```powershell
winget install OpenJS.NodeJS.LTS
```

---

## 🚀 Chạy MINH Desktop

### Bước 1: Cài đặt dependencies

```powershell
cd desktop
npm install
```

**Lưu ý:** Lần đầu chạy có thể mất 2-5 phút để tải các package (React, Electron, Vite, Tailwind, v.v.)

### Bước 2: Chạy development mode

```powershell
npm run dev
```

Lệnh này sẽ:
1. Khởi động Vite dev server (http://localhost:5173)
2. Mở cửa sổ Electron tự động
3. Hot reload khi bạn sửa code

### Bước 3: Test tính năng

- Click nút **"Start"** trên header để khởi động Python backend
- Nhập câu hỏi vào search bar và nhấn Enter
- Kiểm tra Console (View → Toggle Developer Tools) để xem log IPC

---

## 📦 Build & Package (Tạo file .exe)

### Build production

```powershell
npm run build
```

Kết quả: file build sẽ nằm trong `dist/`

### Tạo installer Windows (.exe)

```powershell
npm install --save-dev @vitejs/plugin-react electron-builder
npm run build
npx electron-builder --win
```

File installer sẽ được tạo trong `dist/` (ví dụ: `MINH-Setup-0.1.0.exe`)

---

## 🛠️ Troubleshooting

### Lỗi: "npm: The term 'npm' is not recognized"

**Nguyên nhân:** Node.js chưa được thêm vào PATH.

**Giải pháp:**
1. Cài lại Node.js và chọn "Add to PATH"
2. Hoặc thêm thủ công:
   - Mở **System Properties** → **Environment Variables**
   - Thêm `C:\Program Files\nodejs\` vào biến `Path`
   - Khởi động lại PowerShell

### Lỗi: "Python backend not starting"

**Nguyên nhân:** Electron không tìm thấy Python executable.

**Giải pháp:**
1. Set biến môi trường `PY_PATH`:
   ```powershell
   $env:PY_PATH = "C:\Users\Minh\anaconda3\envs\minh-ai\python.exe"
   npm run dev
   ```
2. Hoặc sửa file `electron/main.js` line 37:
   ```javascript
   const pyPath = 'C:/Users/Minh/anaconda3/envs/minh-ai/python.exe'
   ```

### Lỗi: Port 5173 already in use

**Giải pháp:** Đổi port trong `vite.config.js`:
```javascript
server: { port: 5174 }
```

### Lỗi: "Cannot find module 'electron'"

**Giải pháp:**
```powershell
rm -r node_modules
rm package-lock.json
npm install
```

---

## 📁 Cấu trúc project

```
desktop/
├── package.json          # Dependencies & scripts
├── electron/
│   ├── main.js          # Electron main process (window, IPC)
│   └── preload.js       # IPC bridge (secure context)
├── src/
│   ├── App.jsx          # React UI (Copilot-like layout)
│   ├── main.jsx         # React entry point
│   └── index.css        # Tailwind + custom styles
├── index.html           # HTML template
├── vite.config.js       # Vite config
├── tailwind.config.cjs  # Tailwind config
└── postcss.config.cjs   # PostCSS config
```

---

## 🔗 Tích hợp Backend

Hiện tại Electron main process (`electron/main.js`) đã expose IPC handlers:

- `minh.startPython()` - Khởi động Python backend (`main.py`)
- `minh.stopPython()` - Dừng Python backend

**TODO (tiếp theo):**
- Thêm HTTP server trong Python backend (FastAPI/Flask)
- Gọi API từ React (axios/fetch) để chat với MINH
- Thêm WebSocket cho streaming responses
- System tray + global hotkey (Ctrl+Shift+M)

---

## 📝 Notes

- File này chỉ là UI scaffold. Backend integration đang được phát triển.
- Để xem log backend, check terminal Python hoặc file `data/logs/conversation.json`
- Tailwind CSS unknown @tailwind warnings là bình thường, sẽ biến mất sau khi `npm install`

---

## 🎯 Next Steps

1. ✅ Setup Node.js + npm
2. ✅ Run `npm install` && `npm run dev`
3. ⏳ Connect React → Python backend (HTTP/WebSocket)
4. ⏳ Add system tray + global hotkey
5. ⏳ Package installer (.exe)
