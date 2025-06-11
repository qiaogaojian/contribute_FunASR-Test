#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话管理服务
负责音频识别会话的生命周期管理
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from uuid import uuid4

from app.models.schemas import SessionStatus

logger = logging.getLogger(__name__)


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        # 内存存储会话信息（生产环境应使用数据库）
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._client_sessions: Dict[str, List[str]] = {}
        self._session_timeout = 30  # 分钟
        self._cleanup_task = None
        self._initialized = False

    async def _ensure_initialized(self):
        """确保清理任务已启动"""
        if not self._initialized:
            try:
                if not self._cleanup_task:
                    self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to start cleanup task: {e}")

    async def create_session(
        self,
        client_id: str,
        user_id: Optional[str] = None,
        config_name: str = "balanced",
        language: str = "zh-cn",
        sample_rate: int = 16000,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """创建新会话"""
        await self._ensure_initialized()
        session_id = str(uuid4())
        
        session_data = {
            "session_id": session_id,
            "client_id": client_id,
            "user_id": user_id,
            "status": SessionStatus.CREATED.value,
            "config_name": config_name,
            "language": language,
            "sample_rate": sample_rate,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "metadata": metadata or {},
            "statistics": {
                "total_audio_duration": 0.0,
                "total_text_length": 0,
                "recognition_count": 0,
                "error_count": 0
            }
        }
        
        self._sessions[session_id] = session_data
        
        # 记录客户端会话
        if client_id not in self._client_sessions:
            self._client_sessions[client_id] = []
        self._client_sessions[client_id].append(session_id)
        
        logger.info(f"Created session: {session_id} for client: {client_id}")
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        return self._sessions.get(session_id)
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """更新会话信息"""
        if session_id not in self._sessions:
            return False
        
        session = self._sessions[session_id]
        session.update(updates)
        session["updated_at"] = datetime.utcnow()
        
        logger.debug(f"Updated session: {session_id}")
        return True
    
    async def start_session(self, session_id: str) -> bool:
        """启动会话并预创建 ASR 引擎"""
        if session_id not in self._sessions:
            return False

        session = self._sessions[session_id]
        if session["status"] != SessionStatus.CREATED.value:
            logger.warning(f"Cannot start session {session_id} in status: {session['status']}")
            return False

        # 预创建 ASR 引擎以减少首次识别延迟
        try:
            from app.api.websocket import get_asr_service
            asr_service = get_asr_service()
            config_name = session.get("config_name", "balanced")

            logger.info(f"Pre-creating ASR engine for session {session_id} with config {config_name}")
            success = await asr_service.create_asr_engine(session_id, config_name)

            if not success:
                logger.error(f"Failed to pre-create ASR engine for session {session_id}")
                return False

        except Exception as e:
            logger.error(f"Error pre-creating ASR engine for session {session_id}: {e}")
            return False

        session["status"] = SessionStatus.ACTIVE.value
        session["updated_at"] = datetime.utcnow()

        logger.info(f"Started session: {session_id}")
        return True
    
    async def pause_session(self, session_id: str) -> bool:
        """暂停会话"""
        if session_id not in self._sessions:
            return False
        
        session = self._sessions[session_id]
        if session["status"] != SessionStatus.ACTIVE.value:
            logger.warning(f"Cannot pause session {session_id} in status: {session['status']}")
            return False
        
        session["status"] = SessionStatus.PAUSED.value
        session["updated_at"] = datetime.utcnow()
        
        logger.info(f"Paused session: {session_id}")
        return True
    
    async def resume_session(self, session_id: str) -> bool:
        """恢复会话"""
        if session_id not in self._sessions:
            return False
        
        session = self._sessions[session_id]
        if session["status"] != SessionStatus.PAUSED.value:
            logger.warning(f"Cannot resume session {session_id} in status: {session['status']}")
            return False
        
        session["status"] = SessionStatus.ACTIVE.value
        session["updated_at"] = datetime.utcnow()
        
        logger.info(f"Resumed session: {session_id}")
        return True
    
    async def end_session(self, session_id: str) -> bool:
        """结束会话"""
        if session_id not in self._sessions:
            return False
        
        session = self._sessions[session_id]
        session["status"] = SessionStatus.COMPLETED.value
        session["updated_at"] = datetime.utcnow()
        
        logger.info(f"Ended session: {session_id}")
        return True
    
    async def fail_session(self, session_id: str, error_message: str) -> bool:
        """标记会话失败"""
        if session_id not in self._sessions:
            return False
        
        session = self._sessions[session_id]
        session["status"] = SessionStatus.FAILED.value
        session["updated_at"] = datetime.utcnow()
        session["metadata"]["error_message"] = error_message
        session["statistics"]["error_count"] += 1
        
        logger.error(f"Failed session: {session_id}, error: {error_message}")
        return True
    
    async def list_sessions(
        self,
        client_id: Optional[str] = None,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """列出会话"""
        sessions = list(self._sessions.values())
        
        # 过滤条件
        if client_id:
            sessions = [s for s in sessions if s["client_id"] == client_id]
        
        if user_id:
            sessions = [s for s in sessions if s["user_id"] == user_id]
        
        if status:
            sessions = [s for s in sessions if s["status"] == status]
        
        # 按创建时间倒序排列
        sessions.sort(key=lambda x: x["created_at"], reverse=True)
        
        return sessions[:limit]
    
    async def get_active_sessions(self) -> List[str]:
        """获取活跃会话列表"""
        return [
            session_id for session_id, session in self._sessions.items()
            if session["status"] == SessionStatus.ACTIVE.value
        ]
    
    async def get_client_sessions(self, client_id: str) -> List[str]:
        """获取客户端的会话列表"""
        return self._client_sessions.get(client_id, [])
    
    async def update_session_statistics(
        self,
        session_id: str,
        audio_duration: float = 0.0,
        text_length: int = 0,
        recognition_count: int = 0,
        error_count: int = 0
    ) -> bool:
        """更新会话统计信息"""
        if session_id not in self._sessions:
            return False
        
        session = self._sessions[session_id]
        stats = session["statistics"]
        
        stats["total_audio_duration"] += audio_duration
        stats["total_text_length"] += text_length
        stats["recognition_count"] += recognition_count
        stats["error_count"] += error_count
        
        session["updated_at"] = datetime.utcnow()
        
        return True
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        total_sessions = len(self._sessions)
        active_sessions = len([
            s for s in self._sessions.values()
            if s["status"] == SessionStatus.ACTIVE.value
        ])
        
        status_counts = {}
        for session in self._sessions.values():
            status = session["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "status_distribution": status_counts,
            "total_clients": len(self._client_sessions),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _cleanup_expired_sessions(self):
        """清理过期会话"""
        while True:
            try:
                await asyncio.sleep(300)  # 每5分钟检查一次
                
                cutoff_time = datetime.utcnow() - timedelta(minutes=self._session_timeout)
                expired_sessions = []
                
                for session_id, session in self._sessions.items():
                    if (session["updated_at"] < cutoff_time and 
                        session["status"] in [SessionStatus.ACTIVE.value, SessionStatus.PAUSED.value]):
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    await self.end_session(session_id)
                    logger.info(f"Cleaned up expired session: {session_id}")
                
            except Exception as e:
                logger.error(f"Error in session cleanup task: {e}")
    
    def is_session_active(self, session_id: str) -> bool:
        """检查会话是否活跃"""
        session = self._sessions.get(session_id)
        return session and session["status"] == SessionStatus.ACTIVE.value
    
    def get_session_count(self) -> int:
        """获取会话总数"""
        return len(self._sessions)
    
    def get_active_session_count(self) -> int:
        """获取活跃会话数"""
        return len([
            s for s in self._sessions.values()
            if s["status"] == SessionStatus.ACTIVE.value
        ])
