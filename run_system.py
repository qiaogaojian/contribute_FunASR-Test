#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统启动入口脚本
使用Poetry配置的包结构启动ASR系统
"""

import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_python_interpreter():
    """检查Python解释器是否可用"""
    python_exe = Path("./venv/python.exe")
    if python_exe.exists():
        try:
            result = subprocess.run([str(python_exe), '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Python解释器可用: {result.stdout.strip()}")
                return True
            else:
                print("❌ Python解释器不可用")
                return False
        except Exception as e:
            print(f"❌ Python解释器检查失败: {e}")
            return False
    else:
        print("❌ 找不到虚拟环境解释器: ./venv/python.exe")
        print("请确保虚拟环境已正确安装")
        return False

def run_websocket_server():
    """启动WebSocket服务器"""
    print("🚀 启动WebSocket服务器...")
    try:
        python_exe = Path("./venv/python.exe")
        if not python_exe.exists():
            print("❌ 找不到虚拟环境解释器: ./venv/python.exe")
            return False

        subprocess.Popen([
            str(python_exe), '-m', 'src.websocket_server'
        ], creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0)
        print("✅ WebSocket服务器已在新窗口启动")
        return True
    except Exception as e:
        print(f"❌ WebSocket服务器启动失败: {e}")
        return False

def run_asr_service():
    """启动ASR服务"""
    print("🎤 启动ASR语音识别服务...")
    try:
        python_exe = Path("./venv/python.exe")
        if not python_exe.exists():
            print("❌ 找不到虚拟环境解释器: ./venv/python.exe")
            return False

        subprocess.run([
            str(python_exe), '-m', 'src.asr.streaming_paraformer'
        ])
    except KeyboardInterrupt:
        print("\n🛑 ASR服务已停止")
    except Exception as e:
        print(f"❌ ASR服务启动失败: {e}")

def open_frontend():
    """打开前端页面"""
    frontend_path = Path(__file__).parent / "frontend" / "index.html"
    if frontend_path.exists():
        url = f"file://{frontend_path.absolute()}"
        print(f"🌐 打开前端页面: {url}")
        webbrowser.open(url)
        return True
    else:
        print(f"❌ 前端文件不存在: {frontend_path}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🎤 FunASR 实时语音转文字系统")
    print("=" * 60)
    
    # 检查Python解释器
    if not check_python_interpreter():
        print("\n请确保虚拟环境已正确安装在 ./venv/ 目录")
        return
    
    print("\n📋 系统启动说明:")
    print("1. WebSocket服务器将在新窗口启动")
    print("2. 前端页面将自动打开")
    print("3. ASR语音识别服务将在当前窗口启动")
    print("4. 开始说话，文字将实时显示在网页上")
    print("5. 按 Ctrl+C 停止ASR服务")
    print("\n💡 前端快捷键:")
    print("- Ctrl+L: 清空文本")
    print("- Ctrl+S: 保存文本")
    print("- Ctrl+R: 重新连接")
    print("\n" + "=" * 60)
    
    # 启动WebSocket服务器
    if not run_websocket_server():
        return
    
    # 等待WebSocket服务器启动
    print("⏳ 等待WebSocket服务器启动...")
    time.sleep(3)
    
    # 打开前端页面
    open_frontend()
    
    # 等待前端页面加载
    print("⏳ 等待前端页面加载...")
    time.sleep(2)
    
    # 启动ASR服务（阻塞）
    # run_asr_service()
    
    print("\n✅ 系统已停止")

if __name__ == "__main__":
    main()
