#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic数据模型
定义API请求和响应的数据结构
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator


class SessionStatus(str, Enum):
    """会话状态枚举"""
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class MessageType(str, Enum):
    """消息类型枚举"""
    WELCOME = "welcome"
    PING = "ping"
    PONG = "pong"
    AUDIO_DATA = "audio_data"
    RECOGNITION_RESULT = "recognition_result"
    SESSION_STATUS = "session_status"
    ERROR = "error"


# ============================================================================
# 请求模型
# ============================================================================

class CreateSessionRequest(BaseModel):
    """创建会话请求"""
    client_id: Optional[str] = Field(None, description="客户端ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    config_name: str = Field(default="balanced", description="ASR配置名称")
    language: str = Field(default="zh-cn", description="语言")
    sample_rate: int = Field(default=16000, description="采样率")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")


class UpdateSessionRequest(BaseModel):
    """更新会话请求"""
    config_name: Optional[str] = Field(None, description="ASR配置名称")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class AudioUploadRequest(BaseModel):
    """音频上传请求"""
    session_id: Optional[str] = Field(None, description="会话ID")
    config_name: str = Field(default="balanced", description="ASR配置名称")
    language: str = Field(default="zh-cn", description="语言")


# ============================================================================
# 响应模型
# ============================================================================

class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(description="是否成功")
    message: str = Field(description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")


class CreateSessionResponse(BaseResponse):
    """创建会话响应"""
    session_id: str = Field(description="会话ID")
    status: SessionStatus = Field(description="会话状态")
    websocket_url: str = Field(description="WebSocket连接URL")


class SessionDetailResponse(BaseResponse):
    """会话详情响应"""
    session_id: str = Field(description="会话ID")
    client_id: Optional[str] = Field(description="客户端ID")
    user_id: Optional[str] = Field(description="用户ID")
    status: SessionStatus = Field(description="会话状态")
    config_name: str = Field(description="ASR配置名称")
    language: str = Field(description="语言")
    sample_rate: int = Field(description="采样率")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    metadata: Dict[str, Any] = Field(description="元数据")
    statistics: Optional[Dict[str, Any]] = Field(None, description="统计信息")


class RecognitionResult(BaseModel):
    """识别结果"""
    session_id: str = Field(description="会话ID")
    text: str = Field(description="识别文本")
    is_final: bool = Field(description="是否为最终结果")
    confidence: Optional[float] = Field(None, description="置信度")
    start_time: Optional[float] = Field(None, description="开始时间")
    end_time: Optional[float] = Field(None, description="结束时间")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")


class AudioProcessResponse(BaseResponse):
    """音频处理响应"""
    session_id: str = Field(description="会话ID")
    results: List[RecognitionResult] = Field(description="识别结果列表")
    processing_time: float = Field(description="处理时间（秒）")


# ============================================================================
# WebSocket消息模型
# ============================================================================

class WebSocketMessage(BaseModel):
    """WebSocket消息基类"""
    type: MessageType = Field(description="消息类型")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")


class WelcomeMessage(WebSocketMessage):
    """欢迎消息"""
    type: MessageType = MessageType.WELCOME
    session_id: str = Field(description="会话ID")
    message: str = Field(description="欢迎信息")
    session_info: Dict[str, Any] = Field(description="会话信息")


class PingMessage(WebSocketMessage):
    """Ping消息"""
    type: MessageType = MessageType.PING
    data: Optional[Any] = Field(None, description="附加数据")


class PongMessage(WebSocketMessage):
    """Pong消息"""
    type: MessageType = MessageType.PONG
    data: Optional[Any] = Field(None, description="附加数据")


class AudioDataMessage(WebSocketMessage):
    """音频数据消息"""
    type: MessageType = MessageType.AUDIO_DATA
    session_id: str = Field(description="会话ID")
    audio_format: str = Field(default="pcm", description="音频格式")
    sample_rate: int = Field(default=16000, description="采样率")
    channels: int = Field(default=1, description="声道数")


class RecognitionResultMessage(WebSocketMessage):
    """识别结果消息"""
    type: MessageType = MessageType.RECOGNITION_RESULT
    session_id: str = Field(description="会话ID")
    result: RecognitionResult = Field(description="识别结果")


class SessionStatusMessage(WebSocketMessage):
    """会话状态消息"""
    type: MessageType = MessageType.SESSION_STATUS
    session_id: str = Field(description="会话ID")
    status: SessionStatus = Field(description="会话状态")
    message: str = Field(description="状态信息")


class ErrorMessage(WebSocketMessage):
    """错误消息"""
    type: MessageType = MessageType.ERROR
    error_code: str = Field(description="错误代码")
    error_message: str = Field(description="错误信息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")


# ============================================================================
# 配置模型
# ============================================================================

class ASRConfigInfo(BaseModel):
    """ASR配置信息"""
    name: str = Field(description="配置名称")
    description: str = Field(description="配置描述")
    vad_config: Dict[str, Any] = Field(description="VAD配置")
    chunk_size: List[int] = Field(description="音频块大小")
    prediction_interval: int = Field(description="预测间隔")
    is_active: bool = Field(description="是否为当前配置")


class ConfigListResponse(BaseResponse):
    """配置列表响应"""
    configs: List[ASRConfigInfo] = Field(description="配置列表")
    current_config: str = Field(description="当前配置名称")


# ============================================================================
# 健康检查模型
# ============================================================================

class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(description="服务状态")
    service: str = Field(description="服务名称")
    version: str = Field(description="服务版本")
    timestamp: float = Field(description="时间戳")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")


# ============================================================================
# 验证器
# ============================================================================

@validator('sample_rate')
def validate_sample_rate(cls, v):
    """验证采样率"""
    if v not in [8000, 16000, 22050, 44100, 48000]:
        raise ValueError('不支持的采样率')
    return v


# 为相关模型添加验证器
CreateSessionRequest.validate_sample_rate = validate_sample_rate
AudioUploadRequest.validate_sample_rate = validate_sample_rate
