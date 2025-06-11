#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REST API路由
提供HTTP接口用于会话管理、配置管理等
"""

import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.models.schemas import (
    CreateSessionRequest, CreateSessionResponse, UpdateSessionRequest,
    SessionDetailResponse, BaseResponse, ConfigListResponse, ASRConfigInfo,
    AudioUploadRequest, AudioProcessResponse, HealthCheckResponse
)
from app.core.config import get_settings, Settings
from app.services.session_manager import SessionManager
from app.services.asr_service import ASRService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_session_manager() -> SessionManager:
    """获取会话管理器"""
    return SessionManager()


def get_asr_service() -> ASRService:
    """获取ASR服务"""
    return ASRService()


# ============================================================================
# 会话管理接口
# ============================================================================

@router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(
    request: CreateSessionRequest,
    session_manager: SessionManager = Depends(get_session_manager),
    settings: Settings = Depends(get_settings)
):
    """创建新的音频识别会话"""
    try:
        logger.info(f"Creating session for client: {request.client_id}")
        
        session_id = await session_manager.create_session(
            client_id=request.client_id,
            user_id=request.user_id,
            config_name=request.config_name,
            language=request.language,
            sample_rate=request.sample_rate,
            metadata=request.metadata
        )
        
        # 构建WebSocket URL
        websocket_url = f"ws://{settings.websocket_host}:{settings.websocket_port}/ws/audio/{session_id}"
        
        return CreateSessionResponse(
            success=True,
            message="Session created successfully",
            session_id=session_id,
            status="created",
            websocket_url=websocket_url
        )
        
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """获取会话详情"""
    try:
        session = await session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionDetailResponse(
            success=True,
            message="Session retrieved successfully",
            **session
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/sessions/{session_id}", response_model=BaseResponse)
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """更新会话配置"""
    try:
        await session_manager.update_session(session_id, request.dict(exclude_unset=True))
        
        return BaseResponse(
            success=True,
            message="Session updated successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to update session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}", response_model=BaseResponse)
async def delete_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """删除会话"""
    try:
        await session_manager.end_session(session_id)
        
        return BaseResponse(
            success=True,
            message="Session deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to delete session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=List[SessionDetailResponse])
async def list_sessions(
    client_id: Optional[str] = None,
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """列出会话"""
    try:
        sessions = await session_manager.list_sessions(
            client_id=client_id,
            user_id=user_id,
            status=status,
            limit=limit
        )
        
        return [
            SessionDetailResponse(
                success=True,
                message="Session retrieved successfully",
                **session
            )
            for session in sessions
        ]
        
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 音频处理接口
# ============================================================================

@router.post("/audio/upload", response_model=AudioProcessResponse)
async def upload_audio(
    file: UploadFile = File(..., description="音频文件"),
    session_id: Optional[str] = Form(None, description="会话ID"),
    config_name: str = Form("balanced", description="ASR配置名称"),
    language: str = Form("zh-cn", description="语言"),
    asr_service: ASRService = Depends(get_asr_service),
    session_manager: SessionManager = Depends(get_session_manager),
    settings: Settings = Depends(get_settings)
):
    """上传音频文件进行识别"""
    try:
        # 验证文件格式
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in settings.allowed_audio_formats:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported audio format: {file_extension}"
            )
        
        # 验证文件大小
        content = await file.read()
        if len(content) > settings.max_file_size * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.max_file_size}MB"
            )
        
        # 如果没有提供会话ID，创建临时会话
        if not session_id:
            session_id = await session_manager.create_session(
                client_id="upload_client",
                config_name=config_name,
                language=language
            )
        
        # 处理音频文件
        start_time = datetime.utcnow()
        results = await asr_service.process_audio_file(session_id, content, file.filename)
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return AudioProcessResponse(
            success=True,
            message="Audio processed successfully",
            session_id=session_id,
            results=results,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process audio upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 配置管理接口
# ============================================================================

@router.get("/configs", response_model=ConfigListResponse)
async def list_configs():
    """列出可用的ASR配置"""
    try:
        from config.asr_config import list_configs, get_config
        
        config_names = list_configs()
        configs = []
        
        for name in config_names:
            config = get_config(name)
            configs.append(ASRConfigInfo(
                name=name,
                description=config.get("description", ""),
                vad_config=config["vad_config"],
                chunk_size=config["chunk_size"],
                prediction_interval=config["prediction_interval"],
                is_active=False  # TODO: 实现当前配置检测
            ))
        
        return ConfigListResponse(
            success=True,
            message="Configs retrieved successfully",
            configs=configs,
            current_config="balanced"  # TODO: 获取当前配置
        )
        
    except Exception as e:
        logger.error(f"Failed to list configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/configs/{config_name}", response_model=ASRConfigInfo)
async def get_config_detail(config_name: str):
    """获取配置详情"""
    try:
        from config.asr_config import get_config
        
        config = get_config(config_name)
        if not config:
            raise HTTPException(status_code=404, detail="Config not found")
        
        return ASRConfigInfo(
            name=config_name,
            description=config.get("description", ""),
            vad_config=config["vad_config"],
            chunk_size=config["chunk_size"],
            prediction_interval=config["prediction_interval"],
            is_active=False  # TODO: 实现当前配置检测
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get config {config_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 系统接口
# ============================================================================

@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    asr_service: ASRService = Depends(get_asr_service),
    settings: Settings = Depends(get_settings)
):
    """健康检查接口"""
    try:
        # 检查ASR服务状态
        asr_status = await asr_service.health_check()
        
        details = {
            "asr_service": asr_status,
            "config": {
                "default_config": settings.default_asr_config,
                "device": settings.asr_device
            }
        }
        
        return HealthCheckResponse(
            status="healthy",
            service=settings.app_name,
            version=settings.app_version,
            timestamp=datetime.utcnow().timestamp(),
            details=details
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            service=settings.app_name,
            version=settings.app_version,
            timestamp=datetime.utcnow().timestamp(),
            details={"error": str(e)}
        )


@router.get("/stats")
async def get_stats(
    session_manager: SessionManager = Depends(get_session_manager)
):
    """获取系统统计信息"""
    try:
        stats = await session_manager.get_stats()
        return JSONResponse(content=stats)
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
