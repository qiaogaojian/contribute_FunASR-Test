#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义
定义会议、转录记录、会议总结等数据结构
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class MeetingStatus(str, Enum):
    """会议状态枚举"""
    WAITING = "waiting"      # 等待开始
    RECORDING = "recording"  # 录制中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消

class TranscriptType(str, Enum):
    """转录类型枚举"""
    PREDICTION = "prediction"  # 预测文本
    FINAL = "final"           # 最终文本

class Meeting(BaseModel):
    """会议模型"""
    id: str = Field(..., description="会议ID")
    title: str = Field(..., description="会议标题")
    description: Optional[str] = Field(None, description="会议描述")
    status: MeetingStatus = Field(MeetingStatus.WAITING, description="会议状态")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    duration: Optional[int] = Field(None, description="会议时长（秒）")
    participants: List[str] = Field(default_factory=list, description="参与者列表")
    audio_file_path: Optional[str] = Field(None, description="音频文件路径")
    transcript_file_path: Optional[str] = Field(None, description="转录文件路径")
    summary_file_path: Optional[str] = Field(None, description="总结文件路径")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TranscriptRecord(BaseModel):
    """转录记录模型"""
    id: str = Field(..., description="记录ID")
    meeting_id: str = Field(..., description="会议ID")
    speaker: str = Field(..., description="说话人")
    text: str = Field(..., description="转录文本")
    timestamp: float = Field(..., description="时间戳（相对于会议开始时间的秒数）")
    confidence: float = Field(..., description="置信度")
    type: TranscriptType = Field(TranscriptType.FINAL, description="转录类型")
    is_final: bool = Field(True, description="是否为最终结果")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class MeetingSummary(BaseModel):
    """会议总结模型"""
    meeting_id: str = Field(..., description="会议ID")
    summary: str = Field(..., description="会议总结")
    key_points: List[str] = Field(default_factory=list, description="关键要点")
    action_items: List[str] = Field(default_factory=list, description="行动项")
    participants_summary: Dict[str, str] = Field(default_factory=dict, description="参与者发言总结")
    duration_summary: str = Field(..., description="时长总结")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CreateMeetingRequest(BaseModel):
    """创建会议请求模型"""
    title: str = Field(..., description="会议标题")
    description: Optional[str] = Field(None, description="会议描述")
    participants: List[str] = Field(default_factory=list, description="参与者列表")

class StartRecordingRequest(BaseModel):
    """开始录制请求模型"""
    meeting_id: str = Field(..., description="会议ID")
    client_id: str = Field(..., description="客户端ID")

class StopRecordingRequest(BaseModel):
    """停止录制请求模型"""
    meeting_id: str = Field(..., description="会议ID")
    client_id: str = Field(..., description="客户端ID")

class AudioDataMessage(BaseModel):
    """音频数据消息模型"""
    meeting_id: str = Field(..., description="会议ID")
    client_id: str = Field(..., description="客户端ID")
    audio_data: str = Field(..., description="Base64编码的音频数据")
    timestamp: float = Field(..., description="时间戳")

class TranscriptMessage(BaseModel):
    """转录消息模型"""
    meeting_id: str = Field(..., description="会议ID")
    transcript: TranscriptRecord = Field(..., description="转录记录")
    message_type: str = Field("transcript", description="消息类型")

class ErrorMessage(BaseModel):
    """错误消息模型"""
    error: str = Field(..., description="错误信息")
    message_type: str = Field("error", description="消息类型")

class StatusMessage(BaseModel):
    """状态消息模型"""
    status: str = Field(..., description="状态信息")
    message_type: str = Field("status", description="消息类型")
    data: Optional[Dict[str, Any]] = Field(None, description="附加数据")

class WebSocketMessage(BaseModel):
    """WebSocket消息基类"""
    type: str = Field(..., description="消息类型")
    data: Dict[str, Any] = Field(..., description="消息数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# API响应模型
class APIResponse(BaseModel):
    """API响应基类"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class MeetingListResponse(APIResponse):
    """会议列表响应"""
    data: List[Meeting]

class MeetingDetailResponse(APIResponse):
    """会议详情响应"""
    data: Meeting

class TranscriptListResponse(APIResponse):
    """转录列表响应"""
    data: List[TranscriptRecord]

class MeetingSummaryResponse(APIResponse):
    """会议总结响应"""
    data: MeetingSummary