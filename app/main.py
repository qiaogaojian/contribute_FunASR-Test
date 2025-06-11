#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI ASR Service 主应用
提供WebSocket和REST API接口
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import time
import logging
from pathlib import Path

from app.core.config import get_settings
from app.api import websocket, rest

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """创建FastAPI应用"""
    settings = get_settings()
    
    app = FastAPI(
        title="ASR Service API",
        description="实时语音识别服务",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应该限制具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加请求日志中间件
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.4f}s"
        )
        return response
    
    # 注册路由
    app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
    app.include_router(rest.router, prefix="/api/v1", tags=["REST API"])
    
    # 静态文件服务（前端）
    frontend_path = Path(__file__).parent.parent / "frontend"
    if frontend_path.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
        
        @app.get("/", response_class=HTMLResponse)
        async def serve_frontend():
            """提供前端页面"""
            index_file = frontend_path / "index.html"
            if index_file.exists():
                return HTMLResponse(content=index_file.read_text(encoding='utf-8'))
            return HTMLResponse("<h1>ASR Service</h1><p>Frontend not found</p>")
    
    # 健康检查
    @app.get("/health")
    async def health_check():
        """健康检查接口"""
        return {
            "status": "healthy",
            "service": "ASR Service",
            "version": "1.0.0",
            "timestamp": time.time()
        }
    
    # 启动事件
    @app.on_event("startup")
    async def startup_event():
        logger.info("ASR Service starting up...")
        # 这里可以添加启动时的初始化逻辑
        
    # 关闭事件
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("ASR Service shutting down...")
        # 这里可以添加关闭时的清理逻辑
    
    return app

# 创建应用实例
app = create_app()

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
