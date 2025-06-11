#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASR服务封装
封装现有的ASR引擎，提供统一的服务接口
"""

import asyncio
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import tempfile
import os

from app.models.schemas import RecognitionResult

logger = logging.getLogger(__name__)


class ASRService:
    """ASR服务"""
    
    def __init__(self):
        self._asr_engines: Dict[str, Any] = {}  # session_id -> ASR引擎实例
        self._session_configs: Dict[str, str] = {}  # session_id -> config_name
        self._initialized = False
        
    async def _ensure_initialized(self):
        """确保ASR引擎已初始化"""
        if not self._initialized:
            try:
                # 导入ASR模块
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                
                self._initialized = True
                logger.info("ASR service initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize ASR service: {e}")
                raise
    
    async def create_asr_engine(self, session_id: str, config_name: str = "meeting"):
        """为会话创建ASR引擎"""
        await self._ensure_initialized()
        
        try:
            from src.asr.websocket_asr import WebSocketASR
            
            # 创建ASR引擎实例
            asr_engine = WebSocketASR(config_name)
            self._asr_engines[session_id] = asr_engine
            self._session_configs[session_id] = config_name
            
            logger.info(f"Created ASR engine for session {session_id} with config {config_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create ASR engine for session {session_id}: {e}")
            return False
    
    async def process_audio_chunk(self, session_id: str, audio_data: bytes) -> List[RecognitionResult]:
        """处理音频数据块"""
        try:
            # 获取预创建的 ASR 引擎
            asr_engine = self._asr_engines.get(session_id)
            if not asr_engine:
                # 如果引擎不存在，尝试创建（兜底机制）
                logger.warning(f"ASR engine not found for session {session_id}, creating on-demand")
                config_name = self._session_configs.get(session_id, "meeting")
                await self.create_asr_engine(session_id, config_name)
                asr_engine = self._asr_engines.get(session_id)

                if not asr_engine:
                    raise Exception(f"Failed to create ASR engine for session {session_id}")

            # 转换音频数据格式
            try:
                # 尝试从二进制数据解析为 int16 PCM
                audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                # logger.info(f"Audio data converted: shape={audio_array.shape}, dtype={audio_array.dtype}, min={audio_array.min():.4f}, max={audio_array.max():.4f}")
            except Exception as e:
                logger.error(f"Failed to convert audio data: {e}")
                return []
            
            # 调用ASR引擎处理
            results = await asyncio.get_event_loop().run_in_executor(
                None, asr_engine.recognize_chunk, audio_array
            )

            # 转换结果格式
            recognition_results = []
            if results:
                # 只在有有效结果时打印日志
                logger.info(f"ASR识别结果: {results}")
                # 处理不同格式的结果
                if isinstance(results, dict):
                    # 单个字典结果
                    recognition_results.append(RecognitionResult(
                        session_id=session_id,
                        text=results.get("text", ""),
                        is_final=results.get("type") == "final",
                        confidence=results.get("confidence"),
                        start_time=results.get("start_time"),
                        end_time=results.get("end_time"),
                        timestamp=datetime.utcnow()
                    ))
                elif isinstance(results, list):
                    # 字典列表结果
                    for result in results:
                        if isinstance(result, dict):
                            recognition_results.append(RecognitionResult(
                                session_id=session_id,
                                text=result.get("text", ""),
                                is_final=result.get("type") == "final",
                                confidence=result.get("confidence"),
                                start_time=result.get("start_time"),
                                end_time=result.get("end_time"),
                                timestamp=datetime.utcnow()
                            ))
                        elif isinstance(result, str):
                            # 字符串结果（向后兼容）
                            recognition_results.append(RecognitionResult(
                                session_id=session_id,
                                text=result,
                                is_final=True,
                                confidence=None,
                                start_time=None,
                                end_time=None,
                                timestamp=datetime.utcnow()
                            ))
                elif isinstance(results, str):
                    # 字符串结果（向后兼容）
                    recognition_results.append(RecognitionResult(
                        session_id=session_id,
                        text=results,
                        is_final=True,
                        confidence=None,
                        start_time=None,
                        end_time=None,
                        timestamp=datetime.utcnow()
                    ))

            return recognition_results
            
        except Exception as e:
            logger.error(f"Failed to process audio chunk for session {session_id}: {e}")
            raise
    
    async def process_audio_file(self, session_id: str, audio_data: bytes, filename: str) -> List[RecognitionResult]:
        """处理音频文件"""
        try:
            # 确保会话有ASR引擎
            if session_id not in self._asr_engines:
                config_name = self._session_configs.get(session_id, "meeting")
                await self.create_asr_engine(session_id, config_name)
            
            asr_engine = self._asr_engines.get(session_id)
            if not asr_engine:
                raise Exception(f"No ASR engine for session {session_id}")
            
            # 保存临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # 处理音频文件
                results = await asyncio.get_event_loop().run_in_executor(
                    None, self._process_file_sync, asr_engine, temp_file_path
                )
                
                # 转换结果格式
                recognition_results = []
                if results:
                    for i, result in enumerate(results):
                        recognition_results.append(RecognitionResult(
                            session_id=session_id,
                            text=result.get("text", ""),
                            is_final=True,  # 文件处理的结果都是最终结果
                            confidence=result.get("confidence"),
                            start_time=result.get("start_time", i * 1.0),
                            end_time=result.get("end_time", (i + 1) * 1.0),
                            timestamp=datetime.utcnow()
                        ))
                
                return recognition_results
                
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            
        except Exception as e:
            logger.error(f"Failed to process audio file for session {session_id}: {e}")
            raise
    
    def _process_file_sync(self, asr_engine, file_path: str):
        """同步处理音频文件"""
        try:
            # 这里需要根据实际的ASR引擎接口来实现
            # 暂时返回模拟结果
            return [{"text": "音频文件识别结果", "confidence": 0.95}]
            
        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")
            raise
    
    async def cleanup_session(self, session_id: str):
        """清理会话的ASR引擎"""
        try:
            if session_id in self._asr_engines:
                # 清理ASR引擎资源
                asr_engine = self._asr_engines[session_id]
                # 这里可以添加具体的清理逻辑
                
                del self._asr_engines[session_id]
                
            if session_id in self._session_configs:
                del self._session_configs[session_id]
                
            logger.info(f"Cleaned up ASR engine for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup session {session_id}: {e}")
    
    async def update_session_config(self, session_id: str, config_name: str):
        """更新会话的ASR配置"""
        try:
            # 清理现有引擎
            await self.cleanup_session(session_id)
            
            # 创建新引擎
            await self.create_asr_engine(session_id, config_name)
            
            logger.info(f"Updated ASR config for session {session_id} to {config_name}")
            
        except Exception as e:
            logger.error(f"Failed to update config for session {session_id}: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            await self._ensure_initialized()
            
            return {
                "status": "healthy",
                "active_sessions": len(self._asr_engines),
                "initialized": self._initialized
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "active_sessions": len(self._asr_engines),
                "initialized": self._initialized
            }
    
    def get_active_sessions(self) -> List[str]:
        """获取活跃的ASR会话"""
        return list(self._asr_engines.keys())
    
    def get_session_config(self, session_id: str) -> Optional[str]:
        """获取会话的配置名称"""
        return self._session_configs.get(session_id)
    
    async def get_available_configs(self) -> List[str]:
        """获取可用的配置列表"""
        try:
            from config.asr_config import list_configs
            return list_configs()
        except Exception as e:
            logger.error(f"Failed to get available configs: {e}")
            return ["meeting"]  # 返回默认配置
