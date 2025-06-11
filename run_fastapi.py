#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI ASR Service 启动脚本
使用uvicorn启动FastAPI应用
"""

import sys
import subprocess
import webbrowser
import time
import logging
from pathlib import Path

from app.core.config import get_settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        logger.info("✅ FastAPI dependencies are available")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependencies: {e}")
        logger.error("Please install dependencies: pip install fastapi uvicorn pydantic")
        return False


def check_python_interpreter():
    """检查Python解释器是否可用"""
    python_exe = Path("./venv/python.exe")
    if python_exe.exists():
        try:
            result = subprocess.run([str(python_exe), '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Python解释器可用: {result.stdout.strip()}")
                return str(python_exe)
            else:
                logger.error("❌ Python解释器不可用")
                return None
        except Exception as e:
            logger.error(f"❌ Python解释器检查失败: {e}")
            return None
    else:
        # 尝试使用系统Python
        try:
            result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ 使用系统Python: {result.stdout.strip()}")
                return sys.executable
        except Exception as e:
            logger.error(f"❌ 系统Python检查失败: {e}")
        
        logger.error("❌ 找不到可用的Python解释器")
        return None


def start_fastapi_server(python_exe: str, settings):
    """启动FastAPI服务器"""
    logger.info("🚀 启动FastAPI服务器...")
    
    try:
        # 构建启动命令
        cmd = [
            python_exe, "-m", "uvicorn", "app.main:app",
            "--host", settings.host,
            "--port", str(settings.port),
            "--log-level", "info"
        ]
        
        if settings.debug:
            cmd.append("--reload")
        
        logger.info(f"启动命令: {' '.join(cmd)}")
        
        # 启动服务器
        process = subprocess.Popen(cmd)
        logger.info(f"✅ FastAPI服务器已启动 (PID: {process.pid})")
        logger.info(f"🌐 服务地址: http://{settings.host}:{settings.port}")
        logger.info(f"📚 API文档: http://{settings.host}:{settings.port}/docs")
        
        return process
        
    except Exception as e:
        logger.error(f"❌ FastAPI服务器启动失败: {e}")
        return None


def open_frontend(settings):
    """打开前端页面"""
    time.sleep(3)  # 等待服务器启动
    
    try:
        # 检查服务器是否启动 - 使用 localhost 进行健康检查
        import requests
        display_host = "localhost" if settings.host == "0.0.0.0" else settings.host
        health_url = f"http://{display_host}:{settings.port}/health"
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            logger.info("✅ 服务器健康检查通过")
        else:
            logger.warning(f"⚠️ 服务器健康检查失败: {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠️ 无法连接到服务器: {e}")
    
    # 打开前端页面 - 使用 localhost 而不是 0.0.0.0
    display_host = "localhost" if settings.host == "0.0.0.0" else settings.host
    frontend_url = f"http://{display_host}:{settings.port}/"
    logger.info(f"🌐 打开前端页面: {frontend_url}")
    webbrowser.open(frontend_url)

    # 打开API文档
    docs_url = f"http://{display_host}:{settings.port}/docs"
    logger.info(f"📚 API文档地址: {docs_url}")


def main():
    """主函数"""
    print("=" * 60)
    print("🎤 FastAPI ASR 实时语音转文字服务")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查Python解释器
    python_exe = check_python_interpreter()
    if not python_exe:
        return
    
    # 获取配置
    settings = get_settings()
    
    print("\n📋 服务配置:")
    print(f"- 应用名称: {settings.app_name}")
    print(f"- 应用版本: {settings.app_version}")
    print(f"- 监听地址: {settings.host}:{settings.port}")
    print(f"- 调试模式: {settings.debug}")
    print(f"- ASR配置: {settings.default_asr_config}")
    print(f"- ASR设备: {settings.asr_device}")
    
    # 显示用户友好的地址
    display_host = "localhost" if settings.host == "0.0.0.0" else settings.host
    print("\n🔗 服务地址:")
    print(f"- 主页: http://{display_host}:{settings.port}/")
    print(f"- API文档: http://{display_host}:{settings.port}/docs")
    print(f"- 健康检查: http://{display_host}:{settings.port}/health")
    print(f"- WebSocket: ws://{display_host}:{settings.port}/ws/audio")
    
    print("\n💡 使用说明:")
    print("1. 服务启动后会自动打开前端页面")
    print("2. 可以通过WebSocket进行实时语音识别")
    print("3. 可以通过REST API进行会话管理")
    print("4. 按 Ctrl+C 停止服务")
    
    print("\n" + "=" * 60)
    
    try:
        # 启动FastAPI服务器
        process = start_fastapi_server(python_exe, settings)
        if not process:
            return
        
        # 打开前端页面
        open_frontend(settings)
        
        # 等待用户中断
        logger.info("服务运行中，按 Ctrl+C 停止...")
        process.wait()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 收到停止信号")
        if 'process' in locals() and process:
            logger.info("正在停止服务器...")
            process.terminate()
            try:
                process.wait(timeout=5)
                logger.info("✅ 服务器已停止")
            except subprocess.TimeoutExpired:
                logger.warning("强制终止服务器...")
                process.kill()
    except Exception as e:
        logger.error(f"❌ 服务运行错误: {e}")
    
    print("\n✅ 服务已停止")


if __name__ == "__main__":
    main()
