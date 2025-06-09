#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能会议助手后端服务
基于FastAPI、WebSocket和FunASR实现实时语音识别和会议记录
"""

import os
import sys
import json
import uuid
import base64
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

import uvicorn
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# 导入自定义模块
from models import (
    Meeting, TranscriptRecord, MeetingSummary, CreateMeetingRequest,
    StartRecordingRequest, StopRecordingRequest, AudioDataMessage,
    TranscriptMessage, ErrorMessage, StatusMessage, WebSocketMessage,
    APIResponse, MeetingListResponse, MeetingDetailResponse,
    TranscriptListResponse, MeetingSummaryResponse, MeetingStatus
)
from database import DatabaseService
from asr_service import ASRService
from summary_service import SummaryService
from file_service import FileService
from meeting_service import MeetingManager

# 创建别名以保持兼容性
AISummarizer = SummaryService

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="智能会议助手API",
    description="基于FunASR的实时语音识别和会议记录系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/assets", StaticFiles(directory="../frontend/dist/assets"), name="assets")

# 全局服务实例
asr_service = ASRService()
meeting_manager = MeetingManager()
ai_summarizer = AISummarizer()

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.meeting_connections: Dict[str, List[str]] = {}  # meeting_id -> [client_ids]
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"客户端 {client_id} 已连接")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        # 从所有会议中移除该客户端
        for meeting_id, clients in self.meeting_connections.items():
            if client_id in clients:
                clients.remove(client_id)
        logger.info(f"客户端 {client_id} 已断开连接")
    
    def join_meeting(self, client_id: str, meeting_id: str):
        if meeting_id not in self.meeting_connections:
            self.meeting_connections[meeting_id] = []
        if client_id not in self.meeting_connections[meeting_id]:
            self.meeting_connections[meeting_id].append(client_id)
    
    async def send_to_client(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"发送消息到客户端 {client_id} 失败: {e}")
                self.disconnect(client_id)
    
    async def broadcast_to_meeting(self, meeting_id: str, message: dict):
        if meeting_id in self.meeting_connections:
            for client_id in self.meeting_connections[meeting_id].copy():
                await self.send_to_client(client_id, message)

manager = ConnectionManager()

# 数据模型
class MeetingCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    participants: Optional[List[str]] = []

class MeetingResponse(BaseModel):
    id: str
    title: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str
    participants: List[str]
    duration: Optional[int] = None

class TranscriptResponse(BaseModel):
    meeting_id: str
    speaker_name: str
    content: str
    timestamp: float
    confidence: float

# API路由
@app.get("/")
async def read_root():
    """返回前端页面"""
    return FileResponse("../frontend/dist/index.html")

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "asr_status": asr_service.is_ready(),
        "version": "1.0.0"
    }

@app.post("/api/meetings", response_model=MeetingResponse)
async def create_meeting(request: MeetingCreateRequest):
    """创建新会议"""
    try:
        meeting = meeting_manager.create_meeting(request)
        return MeetingResponse(**meeting.dict())
    except Exception as e:
        logger.error(f"创建会议失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/meetings")
async def list_meetings(limit: int = 20, offset: int = 0):
    """获取会议列表"""
    try:
        meetings = meeting_manager.list_meetings(limit=limit, offset=offset)
        meeting_responses = [MeetingResponse(**meeting.dict()) for meeting in meetings]
        return {
            "success": True,
            "data": meeting_responses,
            "message": "获取会议列表成功"
        }
    except Exception as e:
        logger.error(f"获取会议列表失败: {e}")
        return {
            "success": False,
            "data": [],
            "message": str(e)
        }

@app.get("/api/meetings/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: str):
    """获取会议详情"""
    try:
        meeting = await meeting_manager.get_meeting(meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="会议不存在")
        return MeetingResponse(**meeting)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会议详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/meetings/{meeting_id}/end")
async def end_meeting(meeting_id: str):
    """结束会议并生成总结"""
    try:
        # 结束会议
        meeting = await meeting_manager.end_meeting(meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="会议不存在")
        
        # 生成AI总结
        summary = await ai_summarizer.generate_summary(meeting_id)
        
        # 广播会议结束消息
        await manager.broadcast_to_meeting(meeting_id, {
            "type": "meeting_ended",
            "meeting_id": meeting_id,
            "summary": summary
        })
        
        return {
            "status": "success",
            "meeting": MeetingResponse(**meeting),
            "summary": summary
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"结束会议失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/meetings/{meeting_id}/transcripts")
async def get_transcripts(meeting_id: str):
    """获取会议转录记录"""
    try:
        transcripts = await meeting_manager.get_transcripts(meeting_id)
        return [TranscriptResponse(**transcript) for transcript in transcripts]
    except Exception as e:
        logger.error(f"获取转录记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/meetings/{meeting_id}/summary")
async def get_meeting_summary(meeting_id: str):
    """获取会议总结"""
    try:
        summary = await meeting_manager.get_meeting_summary(meeting_id)
        if not summary:
            raise HTTPException(status_code=404, detail="会议总结不存在")
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会议总结失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/meetings/{meeting_id}/download")
async def download_meeting_files(meeting_id: str, file_type: str = "all"):
    """下载会议文件"""
    try:
        file_path = await meeting_manager.export_meeting(meeting_id, file_type)
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        return FileResponse(file_path, filename=os.path.basename(file_path))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载会议文件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket端点
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket连接处理"""
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            if message_type == "join_meeting":
                meeting_id = message.get("meeting_id")
                manager.join_meeting(client_id, meeting_id)
                await manager.send_to_client(client_id, {
                    "type": "joined_meeting",
                    "meeting_id": meeting_id,
                    "status": "success"
                })
            
            elif message_type == "start_recording":
                meeting_id = message.get("meeting_id")
                # 启动ASR服务
                await asr_service.start_recording(meeting_id, client_id)
                await manager.send_to_client(client_id, {
                    "type": "recording_started",
                    "meeting_id": meeting_id
                })
            
            elif message_type == "stop_recording":
                meeting_id = message.get("meeting_id")
                # 停止ASR服务
                await asr_service.stop_recording(meeting_id, client_id)
                await manager.send_to_client(client_id, {
                    "type": "recording_stopped",
                    "meeting_id": meeting_id
                })
            
            elif message_type == "audio_data":
                meeting_id = message.get("meeting_id")
                audio_data = message.get("data")  # base64编码的音频数据
                
                # 处理音频数据
                if audio_data:
                    transcript = await asr_service.process_audio(
                        meeting_id, audio_data, client_id
                    )
                    
                    if transcript:
                        # 保存转录记录
                        await meeting_manager.add_transcript(
                            meeting_id=meeting_id,
                            speaker_name=transcript.get("speaker", "未知"),
                            content=transcript.get("text", ""),
                            timestamp=transcript.get("timestamp", 0),
                            confidence=transcript.get("confidence", 0.0)
                        )
                        
                        # 广播转录结果
                        await manager.broadcast_to_meeting(meeting_id, {
                            "type": "transcript",
                            "data": transcript
                        })
            
            elif message_type == "ping":
                await manager.send_to_client(client_id, {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        logger.info(f"客户端 {client_id} 断开连接")
    except Exception as e:
        logger.error(f"WebSocket处理错误: {e}")
    finally:
        manager.disconnect(client_id)

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info("智能会议助手后端服务启动中...")
    
    # 初始化ASR服务
    await asr_service.initialize()
    
    # 初始化会议管理器
    await meeting_manager.initialize()
    
    # 创建输出目录
    os.makedirs("../output/meeting", exist_ok=True)
    
    logger.info("智能会议助手后端服务启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    logger.info("智能会议助手后端服务关闭中...")
    
    # 清理ASR服务
    await asr_service.cleanup()
    
    # 清理会议管理器
    await meeting_manager.cleanup()
    
    logger.info("智能会议助手后端服务已关闭")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )