@echo off
REM Script khởi động MINH Desktop App
echo ========================================
echo    MINH Desktop Launcher
echo ========================================
echo.

REM Kiểm tra Node.js
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js chưa được cài đặt!
    echo Vui lòng cài đặt Node.js từ: https://nodejs.org/
    pause
    exit /b 1
)

REM Chuyển vào thư mục desktop
cd /d "%~dp0desktop"

REM Kiểm tra node_modules
if not exist "node_modules" (
    echo [INFO] Đang cài đặt dependencies lần đầu...
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Cài đặt dependencies thất bại!
        pause
        exit /b 1
    )
)

echo [INFO] Khởi động MINH Desktop App...
echo [INFO] Frontend: http://localhost:5173
echo [INFO] Backend API: http://127.0.0.1:8000
echo.
echo [TIP] Nhấn Ctrl+C để dừng
echo.

REM Chạy Electron + Vite dev mode
call npm run dev

pause
