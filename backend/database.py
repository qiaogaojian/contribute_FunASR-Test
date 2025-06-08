#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库服务
管理会议数据的存储和检索，使用JSON文件作为简单数据库
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from models import Meeting, TranscriptRecord, MeetingSummary, MeetingStatus

logger = logging.getLogger(__name__)

class DatabaseService:
    """数据库服务类"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.meetings_file = self.data_dir / "meetings.json"
        self.transcripts_file = self.data_dir / "transcripts.json"
        self.summaries_file = self.data_dir / "summaries.json"
        
        # 确保数据目录存在
        self.data_dir.mkdir(exist_ok=True)
        
        # 初始化数据文件
        self._init_data_files()
        
        logger.info(f"数据库服务初始化完成，数据目录: {self.data_dir}")
    
    def _init_data_files(self):
        """初始化数据文件"""
        for file_path in [self.meetings_file, self.transcripts_file, self.summaries_file]:
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    def _load_data(self, file_path: Path) -> List[Dict]:
        """加载数据文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"加载数据文件失败 {file_path}: {e}")
            return []
    
    def _save_data(self, file_path: Path, data: List[Dict]):
        """保存数据文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"保存数据文件失败 {file_path}: {e}")
            raise
    
    # 会议相关操作
    def create_meeting(self, title: str, description: Optional[str] = None, 
                      participants: List[str] = None) -> Meeting:
        """创建新会议"""
        meeting_id = str(uuid.uuid4())
        meeting = Meeting(
            id=meeting_id,
            title=title,
            description=description,
            participants=participants or [],
            status=MeetingStatus.WAITING
        )
        
        meetings = self._load_data(self.meetings_file)
        meetings.append(meeting.dict())
        self._save_data(self.meetings_file, meetings)
        
        logger.info(f"创建会议: {meeting_id} - {title}")
        return meeting
    
    def get_meeting(self, meeting_id: str) -> Optional[Meeting]:
        """获取会议详情"""
        meetings = self._load_data(self.meetings_file)
        for meeting_data in meetings:
            if meeting_data['id'] == meeting_id:
                return Meeting(**meeting_data)
        return None
    
    def get_meetings(self, limit: int = 50, offset: int = 0) -> List[Meeting]:
        """获取会议列表"""
        meetings = self._load_data(self.meetings_file)
        # 按创建时间倒序排列
        meetings.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # 分页
        start = offset
        end = offset + limit
        page_meetings = meetings[start:end]
        
        return [Meeting(**meeting_data) for meeting_data in page_meetings]
    
    def list_meetings(self, limit: int = 50, offset: int = 0) -> List[Meeting]:
        """列出会议（get_meetings的别名）"""
        return self.get_meetings(limit, offset)
    
    def save_meeting(self, meeting: Meeting) -> bool:
        """保存会议（新建或更新）"""
        meetings = self._load_data(self.meetings_file)
        
        # 检查是否已存在
        updated = False
        for i, meeting_data in enumerate(meetings):
            if meeting_data['id'] == meeting.id:
                meetings[i] = meeting.dict()
                updated = True
                break
        
        if not updated:
            meetings.append(meeting.dict())
        
        self._save_data(self.meetings_file, meetings)
        logger.info(f"保存会议: {meeting.id} - {meeting.title}")
        return True
    
    def update_meeting(self, meeting: Meeting) -> bool:
        """更新会议信息"""
        meetings = self._load_data(self.meetings_file)
        
        for i, meeting_data in enumerate(meetings):
            if meeting_data['id'] == meeting.id:
                meeting.updated_at = datetime.now()
                meetings[i] = meeting.dict()
                self._save_data(self.meetings_file, meetings)
                
                logger.info(f"更新会议: {meeting.id}")
                return True
        
        return False
    
    def start_meeting(self, meeting_id: str) -> Optional[Meeting]:
        """开始会议"""
        meeting = self.get_meeting(meeting_id)
        if meeting:
            meeting.status = MeetingStatus.RECORDING
            meeting.start_time = datetime.now()
            if self.update_meeting(meeting):
                return meeting
        return None
    
    def end_meeting(self, meeting_id: str) -> Optional[Meeting]:
        """结束会议"""
        meeting = self.get_meeting(meeting_id)
        if meeting and meeting.start_time:
            meeting.status = MeetingStatus.COMPLETED
            meeting.end_time = datetime.now()
            meeting.duration = int((meeting.end_time - meeting.start_time).total_seconds())
            if self.update_meeting(meeting):
                return meeting
        return None
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """删除会议"""
        meetings = self._load_data(self.meetings_file)
        original_length = len(meetings)
        
        meetings = [m for m in meetings if m['id'] != meeting_id]
        
        if len(meetings) < original_length:
            self._save_data(self.meetings_file, meetings)
            
            # 同时删除相关的转录记录和总结
            self.delete_transcripts_by_meeting(meeting_id)
            self.delete_summary_by_meeting(meeting_id)
            
            logger.info(f"删除会议: {meeting_id}")
            return True
        
        return False
    
    # 转录记录相关操作
    def add_transcript(self, meeting_id: str, speaker: str, text: str, 
                     timestamp: float, confidence: float = 0.95, 
                     is_final: bool = True) -> TranscriptRecord:
        """添加转录记录"""
        transcript_id = str(uuid.uuid4())
        transcript = TranscriptRecord(
            id=transcript_id,
            meeting_id=meeting_id,
            speaker=speaker,
            text=text,
            timestamp=timestamp,
            confidence=confidence,
            is_final=is_final
        )
        
        transcripts = self._load_data(self.transcripts_file)
        transcripts.append(transcript.dict())
        self._save_data(self.transcripts_file, transcripts)
        
        return transcript
    
    def get_transcripts(self, meeting_id: str) -> List[TranscriptRecord]:
        """获取会议转录记录"""
        transcripts = self._load_data(self.transcripts_file)
        meeting_transcripts = [
            TranscriptRecord(**t) for t in transcripts 
            if t['meeting_id'] == meeting_id
        ]
        
        # 按时间戳排序
        meeting_transcripts.sort(key=lambda x: x.timestamp)
        return meeting_transcripts
    
    def delete_transcripts_by_meeting(self, meeting_id: str) -> bool:
        """删除会议的所有转录记录"""
        transcripts = self._load_data(self.transcripts_file)
        original_length = len(transcripts)
        
        transcripts = [t for t in transcripts if t['meeting_id'] != meeting_id]
        
        if len(transcripts) < original_length:
            self._save_data(self.transcripts_file, transcripts)
            return True
        
        return False
    
    # 会议总结相关操作
    def save_summary(self, meeting_id: str, summary: str, key_points: List[str] = None,
                    action_items: List[str] = None, participants_summary: Dict[str, str] = None,
                    duration_summary: str = "") -> MeetingSummary:
        """保存会议总结"""
        meeting_summary = MeetingSummary(
            meeting_id=meeting_id,
            summary=summary,
            key_points=key_points or [],
            action_items=action_items or [],
            participants_summary=participants_summary or {},
            duration_summary=duration_summary
        )
        
        summaries = self._load_data(self.summaries_file)
        
        # 检查是否已存在总结，如果存在则更新
        updated = False
        for i, s in enumerate(summaries):
            if s['meeting_id'] == meeting_id:
                summaries[i] = meeting_summary.dict()
                updated = True
                break
        
        if not updated:
            summaries.append(meeting_summary.dict())
        
        self._save_data(self.summaries_file, summaries)
        
        logger.info(f"保存会议总结: {meeting_id}")
        return meeting_summary
    
    def get_summary(self, meeting_id: str) -> Optional[MeetingSummary]:
        """获取会议总结"""
        summaries = self._load_data(self.summaries_file)
        for summary_data in summaries:
            if summary_data['meeting_id'] == meeting_id:
                return MeetingSummary(**summary_data)
        return None
    
    def delete_summary_by_meeting(self, meeting_id: str) -> bool:
        """删除会议总结"""
        summaries = self._load_data(self.summaries_file)
        original_length = len(summaries)
        
        summaries = [s for s in summaries if s['meeting_id'] != meeting_id]
        
        if len(summaries) < original_length:
            self._save_data(self.summaries_file, summaries)
            return True
        
        return False
    
    # 统计相关操作
    def get_meeting_stats(self) -> Dict[str, Any]:
        """获取会议统计信息"""
        meetings = self._load_data(self.meetings_file)
        transcripts = self._load_data(self.transcripts_file)
        summaries = self._load_data(self.summaries_file)
        
        # 按状态统计会议
        status_counts = {}
        total_duration = 0
        
        for meeting in meetings:
            status = meeting.get('status', 'waiting')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if meeting.get('duration'):
                total_duration += meeting['duration']
        
        return {
            "total_meetings": len(meetings),
            "total_transcripts": len(transcripts),
            "total_summaries": len(summaries),
            "status_counts": status_counts,
            "total_duration_seconds": total_duration,
            "average_duration_seconds": total_duration / max(len(meetings), 1)
        }

# 创建别名以保持兼容性
DatabaseManager = DatabaseService