#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会议管理服务
负责会议的创建、状态管理、录制控制等功能
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from models import Meeting, MeetingStatus, CreateMeetingRequest
from database import DatabaseManager

logger = logging.getLogger(__name__)

class MeetingManager:
    """会议管理器"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager or DatabaseManager()
        self.active_meetings: Dict[str, Meeting] = {}
        self.recording_meetings: Dict[str, str] = {}  # meeting_id -> client_id
        
    async def initialize(self):
        """初始化会议管理器"""
        logger.info("初始化会议管理器...")
        
        # 加载活跃会议
        meetings = self.db_manager.list_meetings()
        for meeting in meetings:
            if meeting.status in [MeetingStatus.WAITING, MeetingStatus.RECORDING]:
                self.active_meetings[meeting.id] = meeting
                if meeting.status == MeetingStatus.RECORDING:
                    # 恢复录制状态（假设客户端ID为unknown）
                    self.recording_meetings[meeting.id] = "unknown"
        
        logger.info(f"加载了 {len(self.active_meetings)} 个活跃会议")
        
    async def cleanup(self):
        """清理会议管理器"""
        logger.info("清理会议管理器...")
        
        # 停止所有正在录制的会议
        for meeting_id in list(self.recording_meetings.keys()):
            meeting = self.get_meeting(meeting_id)
            if meeting:
                meeting.status = MeetingStatus.CANCELLED
                self.db_manager.update_meeting(meeting)
        
        self.active_meetings.clear()
        self.recording_meetings.clear()
        
        logger.info("会议管理器清理完成")
        
    def create_meeting(self, request: CreateMeetingRequest) -> Meeting:
        """创建新会议"""
        meeting_id = str(uuid.uuid4())
        
        meeting = Meeting(
            id=meeting_id,
            title=request.title,
            description=request.description,
            participants=request.participants,
            status=MeetingStatus.WAITING
        )
        
        # 保存到数据库
        self.db_manager.save_meeting(meeting)
        
        # 添加到活跃会议列表
        self.active_meetings[meeting_id] = meeting
        
        logger.info(f"Created meeting: {meeting_id} - {meeting.title}")
        return meeting
    
    def get_meeting(self, meeting_id: str) -> Optional[Meeting]:
        """获取会议信息"""
        # 先从内存中查找
        if meeting_id in self.active_meetings:
            return self.active_meetings[meeting_id]
        
        # 从数据库中查找
        meeting = self.db_manager.get_meeting(meeting_id)
        if meeting:
            self.active_meetings[meeting_id] = meeting
        
        return meeting
    
    def start_recording(self, meeting_id: str, client_id: str) -> bool:
        """开始录制会议"""
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            logger.error(f"Meeting not found: {meeting_id}")
            return False
        
        if meeting.status != MeetingStatus.WAITING:
            logger.error(f"Meeting {meeting_id} is not in waiting status")
            return False
        
        # 更新会议状态
        meeting.status = MeetingStatus.RECORDING
        meeting.start_time = datetime.now()
        
        # 记录录制信息
        self.recording_meetings[meeting_id] = client_id
        
        # 更新数据库
        self.db_manager.update_meeting(meeting)
        
        logger.info(f"Started recording for meeting: {meeting_id}")
        return True
    
    def stop_recording(self, meeting_id: str, client_id: str) -> bool:
        """停止录制会议"""
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            logger.error(f"Meeting not found: {meeting_id}")
            return False
        
        if meeting.status != MeetingStatus.RECORDING:
            logger.error(f"Meeting {meeting_id} is not recording")
            return False
        
        # 检查客户端权限
        if self.recording_meetings.get(meeting_id) != client_id:
            logger.error(f"Client {client_id} is not authorized to stop recording for meeting {meeting_id}")
            return False
        
        # 更新会议状态
        meeting.status = MeetingStatus.COMPLETED
        meeting.end_time = datetime.now()
        
        # 计算会议时长
        if meeting.start_time:
            duration = (meeting.end_time - meeting.start_time).total_seconds()
            meeting.duration = int(duration)
        
        # 清理录制信息
        self.recording_meetings.pop(meeting_id, None)
        
        # 更新数据库
        self.db_manager.update_meeting(meeting)
        
        logger.info(f"Stopped recording for meeting: {meeting_id}")
        return True
    
    def is_recording(self, meeting_id: str) -> bool:
        """检查会议是否正在录制"""
        return meeting_id in self.recording_meetings
    
    def get_recording_client(self, meeting_id: str) -> Optional[str]:
        """获取录制客户端ID"""
        return self.recording_meetings.get(meeting_id)
    
    def list_meetings(self, status: Optional[MeetingStatus] = None, limit: int = 50, offset: int = 0) -> List[Meeting]:
        """列出会议"""
        meetings = self.db_manager.list_meetings(limit=limit, offset=offset)
        
        if status:
            meetings = [m for m in meetings if m.status == status]
        
        return meetings
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """删除会议"""
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            return False
        
        # 如果正在录制，先停止录制
        if meeting.status == MeetingStatus.RECORDING:
            logger.warning(f"Force stopping recording for meeting {meeting_id} before deletion")
            meeting.status = MeetingStatus.CANCELLED
            self.recording_meetings.pop(meeting_id, None)
        
        # 从数据库删除
        success = self.db_manager.delete_meeting(meeting_id)
        
        # 从内存中移除
        self.active_meetings.pop(meeting_id, None)
        
        if success:
            logger.info(f"Deleted meeting: {meeting_id}")
        
        return success
    
    def update_meeting(self, meeting: Meeting) -> bool:
        """更新会议信息"""
        meeting.updated_at = datetime.now()
        
        # 更新内存中的会议
        self.active_meetings[meeting.id] = meeting
        
        # 更新数据库
        return self.db_manager.update_meeting(meeting)
    
    def cleanup_expired_meetings(self, hours: int = 24) -> int:
        """清理过期会议"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        expired_meetings = []
        
        for meeting in self.active_meetings.values():
            if (meeting.status == MeetingStatus.COMPLETED and 
                meeting.end_time and meeting.end_time < cutoff_time):
                expired_meetings.append(meeting.id)
        
        cleaned_count = 0
        for meeting_id in expired_meetings:
            if self.delete_meeting(meeting_id):
                cleaned_count += 1
        
        logger.info(f"Cleaned up {cleaned_count} expired meetings")
        return cleaned_count