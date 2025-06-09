#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本 - 启动WebSocket服务器并打开前端页面
"""

import os
import sys
import time
import webbrowser
import subprocess
import threading
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import websockets
        print("✓ websockets 已安装")
    except ImportError:
        print("❌ websockets 未安装")
        print("正在安装 websockets...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets"])
        print("✓ websockets 安装完成")

def start_websocket_server():
    """启动WebSocket服务器"""
    try:
        # 导入并启动服务器
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from websocket_server import main
        import asyncio
        
        print("🚀 启动WebSocket服务器...")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  WebSocket服务器已停止")
    except Exception as e:
        print(f"❌ WebSocket服务器启动失败: {e}")

def open_frontend():
    """打开前端页面"""
    frontend_path = Path(__file__).parent / "frontend" / "index.html"
    if frontend_path.exists():
        # 等待服务器启动
        time.sleep(2)
        
        # 打开浏览器
        url = f"file://{frontend_path.absolute()}"
        print(f"🌐 打开前端页面: {url}")
        webbrowser.open(url)
    else:
        print(f"❌ 前端文件不存在: {frontend_path}")

def main():
    """主函数"""
    print("=" * 50)
    print("🎤 FunASR 实时语音转文字前端")
    print("=" * 50)
    
    # 检查依赖
    check_dependencies()
    
    # 启动前端页面（在新线程中）
    frontend_thread = threading.Thread(target=open_frontend, daemon=True)
    frontend_thread.start()
    
    print("\n📋 使用说明:")
    print("1. 确保 ASR 程序 (streaming_paraformer.py) 正在运行")
    print("2. 前端页面将自动打开")
    print("3. 开始说话，文字将实时显示在网页上")
    print("4. 按 Ctrl+C 停止服务器")
    print("\n💡 快捷键:")
    print("- Ctrl+L: 清空文本")
    print("- Ctrl+S: 保存文本")
    print("- Ctrl+R: 重新连接")
    print("\n" + "=" * 50)
    
    # 启动WebSocket服务器（阻塞）
    start_websocket_server()

if __name__ == "__main__":
    main()
