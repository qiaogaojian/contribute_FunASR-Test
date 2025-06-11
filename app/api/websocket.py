#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket API路由
处理实时音频识别的WebSocket连接
"""

import json
import asyncio
import logging
from typing import Dict, Set
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.websockets import WebSocketState

from app.models.schemas import (
    WelcomeMessage, PingMessage, PongMessage, AudioDataMessage,
    RecognitionResultMessage, ErrorMessage, SessionStatus
)
from app.core.config import get_settings
from app.services.session_manager import SessionManager
from app.services.asr_service import ASRService

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 活跃连接: session_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # 会话到客户端的映射: session_id -> client_id
        self.session_clients: Dict[str, str] = {}
        # 客户端到会话的映射: client_id -> Set[session_id]
        self.client_sessions: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, client_id: str):
        """连接WebSocket"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.session_clients[session_id] = client_id
        
        if client_id not in self.client_sessions:
            self.client_sessions[client_id] = set()
        self.client_sessions[client_id].add(session_id)
        
        logger.info(f"WebSocket connected: session={session_id}, client={client_id}")
    
    def disconnect(self, session_id: str):
        """断开WebSocket连接"""
        if session_id in self.active_connections:
            client_id = self.session_clients.get(session_id)
            
            # 清理连接记录
            del self.active_connections[session_id]
            if session_id in self.session_clients:
                del self.session_clients[session_id]
            
            # 清理客户端会话记录
            if client_id and client_id in self.client_sessions:
                self.client_sessions[client_id].discard(session_id)
                if not self.client_sessions[client_id]:
                    del self.client_sessions[client_id]
            
            logger.info(f"WebSocket disconnected: session={session_id}, client={client_id}")
    
    async def send_message(self, session_id: str, message: dict):
        """发送消息到指定会话"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            if websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await websocket.send_text(json.dumps(message, ensure_ascii=False, default=str))
                except Exception as e:
                    logger.error(f"Failed to send message to session {session_id}: {e}")
                    self.disconnect(session_id)
    
    async def broadcast_to_client(self, client_id: str, message: dict):
        """广播消息到客户端的所有会话"""
        if client_id in self.client_sessions:
            for session_id in self.client_sessions[client_id].copy():
                await self.send_message(session_id, message)
    
    def get_active_sessions(self) -> list:
        """获取活跃会话列表"""
        return list(self.active_connections.keys())


# 全局实例
connection_manager = ConnectionManager()
session_manager = SessionManager()
asr_service = ASRService()


def get_connection_manager() -> ConnectionManager:
    """获取连接管理器"""
    return connection_manager


def get_session_manager() -> SessionManager:
    """获取会话管理器"""
    return session_manager


def get_asr_service() -> ASRService:
    """获取ASR服务"""
    return asr_service


@router.websocket("/audio/{session_id}")
async def websocket_audio_endpoint(
    websocket: WebSocket,
    session_id: str,
    client_id: str = Query(default=None, description="客户端ID"),
    conn_manager: ConnectionManager = Depends(get_connection_manager),
    session_manager: SessionManager = Depends(get_session_manager),
    asr_service: ASRService = Depends(get_asr_service)
):
    """WebSocket音频处理端点"""
    
    # 生成客户端ID
    if not client_id:
        client_id = f"{websocket.client.host}:{websocket.client.port}"
    
    try:
        # 建立连接
        await conn_manager.connect(websocket, session_id, client_id)
        
        # 验证会话是否存在
        session = await session_manager.get_session(session_id)
        if not session:
            error_msg = ErrorMessage(
                error_code="SESSION_NOT_FOUND",
                error_message=f"Session {session_id} not found"
            )
            await websocket.send_text(error_msg.json())
            await websocket.close(code=1008, reason="Session not found")
            return
        
        # 发送欢迎消息
        welcome_msg = WelcomeMessage(
            session_id=session_id,
            message="WebSocket connection established successfully",
            session_info={
                "status": session["status"],
                "config_name": session["config_name"],
                "created_at": session["created_at"]
            }
        )
        await conn_manager.send_message(session_id, welcome_msg.dict())
        
        # 启动会话
        await session_manager.start_session(session_id)
        
        # 消息处理循环
        while True:
            try:
                # 接收消息
                message = await websocket.receive()
                
                if message["type"] == "websocket.disconnect":
                    break
                
                # 处理文本消息
                if message["type"] == "websocket.receive" and "text" in message:
                    await handle_text_message(
                        websocket, session_id, message["text"], 
                        conn_manager, session_manager, asr_service
                    )
                
                # 处理二进制消息（音频数据）
                elif message["type"] == "websocket.receive" and "bytes" in message:
                    await handle_audio_data(
                        websocket, session_id, message["bytes"],
                        conn_manager, session_manager, asr_service
                    )
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket message loop: {e}")
                error_msg = ErrorMessage(
                    error_code="MESSAGE_PROCESSING_ERROR",
                    error_message=str(e)
                )
                await conn_manager.send_message(session_id, error_msg.dict())
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    
    finally:
        # 清理连接
        conn_manager.disconnect(session_id)
        
        # 结束会话
        try:
            await session_manager.end_session(session_id)
        except Exception as e:
            logger.error(f"Failed to end session {session_id}: {e}")


async def handle_text_message(
    websocket: WebSocket,
    session_id: str,
    text: str,
    conn_manager: ConnectionManager,
    session_manager: SessionManager,
    asr_service: ASRService
):
    """处理文本消息"""
    try:
        data = json.loads(text)
        message_type = data.get("type")
        
        if message_type == "ping":
            # 处理ping消息
            pong_msg = PongMessage(data=data.get("data"))
            await conn_manager.send_message(session_id, pong_msg.dict())
            
        elif message_type == "pause":
            # 暂停会话
            await session_manager.pause_session(session_id)
            
        elif message_type == "resume":
            # 恢复会话
            await session_manager.resume_session(session_id)
            
        elif message_type == "config_update":
            # 更新配置（暂不支持运行时更新）
            error_msg = ErrorMessage(
                error_code="CONFIG_UPDATE_NOT_SUPPORTED",
                error_message="Configuration update during active session is not supported"
            )
            await conn_manager.send_message(session_id, error_msg.dict())
            
        else:
            logger.warning(f"Unknown message type: {message_type}")
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON message: {e}")
        error_msg = ErrorMessage(
            error_code="INVALID_JSON",
            error_message="Invalid JSON format"
        )
        await conn_manager.send_message(session_id, error_msg.dict())


async def handle_audio_data(
    websocket: WebSocket,
    session_id: str,
    audio_bytes: bytes,
    conn_manager: ConnectionManager,
    session_manager: SessionManager,
    asr_service: ASRService
):
    """处理音频数据"""
    try:
        logger.debug(f"Received audio data: session={session_id}, size={len(audio_bytes)}")
        
        # 处理音频数据
        results = await asr_service.process_audio_chunk(session_id, audio_bytes)
        
        # 发送识别结果
        for result in results:
            result_msg = RecognitionResultMessage(
                session_id=session_id,
                result=result
            )
            await conn_manager.send_message(session_id, result_msg.dict())
            
    except Exception as e:
        logger.error(f"Error processing audio data: {e}")
        error_msg = ErrorMessage(
            error_code="AUDIO_PROCESSING_ERROR",
            error_message=f"Audio processing error: {str(e)}"
        )
        await conn_manager.send_message(session_id, error_msg.dict())


@router.websocket("/audio")
async def websocket_audio_create_endpoint(
    websocket: WebSocket,
    client_id: str = Query(default=None, description="客户端ID"),
    config_name: str = Query(default="meeting", description="ASR配置名称"),
    language: str = Query(default="zh-cn", description="语言"),
    conn_manager: ConnectionManager = Depends(get_connection_manager),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """WebSocket音频端点（自动创建会话）"""
    
    # 生成客户端ID
    if not client_id:
        client_id = f"{websocket.client.host}:{websocket.client.port}"
    
    try:
        # 创建新会话
        session_id = await session_manager.create_session(
            client_id=client_id,
            config_name=config_name,
            language=language
        )

        # 立即启动会话并预创建 ASR 引擎
        await session_manager.start_session(session_id)

        # 重定向到具体会话的WebSocket处理
        await websocket_audio_endpoint(
            websocket, session_id, client_id,
            conn_manager, session_manager, get_asr_service()
        )
        
    except Exception as e:
        logger.error(f"Failed to create session for WebSocket: {e}")
        await websocket.close(code=1011, reason=str(e))
