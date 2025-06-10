@echo off
chcp 65001 >nul
title FunASR 实时语音转文字系统

echo ============================================================
echo 🎤 FunASR 实时语音转文字系统
echo ============================================================
echo.

echo 📦 检查虚拟环境...
if not exist ".\venv\python.exe" (
    echo ❌ 找不到虚拟环境解释器: .\venv\python.exe
    echo 请确保虚拟环境已正确安装
    pause
    exit /b 1
)

echo ✅ 虚拟环境检查通过
echo.

echo 🚀 启动WebSocket服务器...
start "WebSocket服务器" cmd /k ".\venv\python.exe -m src.websocket_server"

echo ⏳ 等待WebSocket服务器启动...
timeout /t 3 /nobreak >nul

echo 🌐 打开前端页面...
start "" "frontend/index.html"

echo ⏳ 等待前端页面加载...
timeout /t 2 /nobreak >nul

echo.
echo 📋 系统启动说明:
echo 1. WebSocket服务器已在新窗口中启动
echo 2. 前端页面已自动打开
echo 3. 即将启动ASR语音识别服务
echo 4. 开始说话，文字将实时显示在网页上
echo 5. 按 Ctrl+C 停止ASR服务
echo.
echo 💡 前端快捷键:
echo - Ctrl+L: 清空文本
echo - Ctrl+S: 保存文本  
echo - Ctrl+R: 重新连接
echo.
echo ============================================================
echo.

echo 🎤 启动ASR语音识别服务...
.\venv\python.exe -m src.asr.streaming_paraformer

echo.
echo 🛑 ASR服务已停止
echo 💡 请手动关闭WebSocket服务器窗口
pause
