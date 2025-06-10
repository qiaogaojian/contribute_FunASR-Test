#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合的ASR系统启动脚本
同时启动WebSocket服务器和ASR语音识别服务
"""

import os
import sys
import time
import asyncio
import threading
import subprocess
import webbrowser
from pathlib import Path
import signal

def check_dependencies():
    """检查依赖是否安装"""
    required_packages = ['websockets', 'funasr', 'sounddevice', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 未安装")
    
    if missing_packages:
        print(f"\n正在安装缺失的依赖: {', '.join(missing_packages)}")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✓ {package} 安装完成")
            except subprocess.CalledProcessError:
                print(f"❌ {package} 安装失败")
                return False
    
    return True

def start_websocket_server():
    """启动WebSocket服务器"""
    try:
        print("🚀 启动WebSocket服务器...")
        # 导入WebSocket服务器
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from websocket_server import ASRWebSocketServer
        
        async def run_websocket():
            server = ASRWebSocketServer()
            try:
                await server.start_server()
            except KeyboardInterrupt:
                pass
            finally:
                server.stop()
                print("WebSocket服务器已停止")
        
        # 在新的事件循环中运行WebSocket服务器
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_websocket())
        
    except Exception as e:
        print(f"❌ WebSocket服务器启动失败: {e}")

def start_asr_service():
    """启动ASR语音识别服务"""
    try:
        print("🎤 启动ASR语音识别服务...")
        # 等待WebSocket服务器启动
        time.sleep(3)
        
        # 导入ASR模块
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'asr'))
        from streaming_paraformer import main as asr_main
        
        # 运行ASR服务
        asr_main()
        
    except Exception as e:
        print(f"❌ ASR服务启动失败: {e}")

def open_frontend():
    """打开前端页面"""
    try:
        frontend_path = Path(__file__).parent / "frontend" / "index.html"
        if frontend_path.exists():
            # 等待服务器启动
            time.sleep(5)
            
            # 打开浏览器
            url = f"file://{frontend_path.absolute()}"
            print(f"🌐 打开前端页面: {url}")
            webbrowser.open(url)
        else:
            print(f"❌ 前端文件不存在: {frontend_path}")
    except Exception as e:
        print(f"❌ 打开前端页面失败: {e}")

def signal_handler(sig, frame):
    """信号处理器"""
    print("\n\n🛑 收到停止信号，正在关闭所有服务...")
    sys.exit(0)

def main():
    """主函数"""
    print("=" * 60)
    print("🎤 FunASR 实时语音转文字系统")
    print("=" * 60)
    
    # 设置信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    # 检查依赖
    print("📦 检查依赖...")
    if not check_dependencies():
        print("❌ 依赖检查失败，请手动安装缺失的依赖")
        return
    
    print("\n✅ 依赖检查完成")
    
    # 创建线程列表
    threads = []
    
    # 启动WebSocket服务器线程
    websocket_thread = threading.Thread(target=start_websocket_server, daemon=True)
    websocket_thread.start()
    threads.append(websocket_thread)
    
    # 启动前端页面线程
    frontend_thread = threading.Thread(target=open_frontend, daemon=True)
    frontend_thread.start()
    threads.append(frontend_thread)
    
    # 启动ASR服务（在主线程中运行）
    print("\n📋 系统启动说明:")
    print("1. WebSocket服务器正在启动...")
    print("2. 前端页面将自动打开")
    print("3. ASR语音识别服务即将启动")
    print("4. 开始说话，文字将实时显示在网页上")
    print("5. 按 Ctrl+C 停止所有服务")
    print("\n💡 快捷键:")
    print("- Ctrl+L: 清空文本")
    print("- Ctrl+S: 保存文本")
    print("- Ctrl+R: 重新连接")
    print("\n" + "=" * 60)
    
    try:
        # 在主线程中运行ASR服务
        start_asr_service()
    except KeyboardInterrupt:
        print("\n🛑 用户主动停止程序")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
    finally:
        print("\n🔄 正在清理资源...")
        # 等待所有线程结束
        for thread in threads:
            if thread.is_alive():
                thread.join(timeout=2)
        print("✅ 程序已完全停止")

if __name__ == "__main__":
    main()
