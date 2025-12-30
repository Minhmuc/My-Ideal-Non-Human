@echo off
REM Script khởi động backend API server riêng
echo ========================================
echo    MINH Backend API Server
echo ========================================
echo.

REM Activate virtual environment và chạy FastAPI
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment không tồn tại!
    echo Vui lòng chạy: python -m venv .venv
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [INFO] Khởi động API server...
echo [INFO] URL: http://127.0.0.1:8000
echo [INFO] Docs: http://127.0.0.1:8000/docs
echo.
echo [TIP] Nhấn Ctrl+C để dừng
echo.

REM Chạy với uvicorn
python -m uvicorn api_server:app --host 127.0.0.1 --port 8000 --reload

pause
