#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASR语音识别服务
基于FunASR实现实时语音识别，支持多会议并发处理
"""

import os
import sys
import json
import base64
import asyncio
import logging
import numpy as np
from typing import Dict, Optional, Any
from datetime import datetime
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from funasr import AutoModel

logger = logging.getLogger(__name__)

class ASRService:
    """ASR语音识别服务类"""
    
    def __init__(self):
        self.model = None
        self.is_initialized = False
        self.active_sessions: Dict[str, Dict] = {}  # meeting_id -> session_data
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # 模型配置
        self.home_directory = os.path.expanduser("D:/Cache/model/asr")
        self.asr_model_path = os.path.join(
            self.home_directory, 
            "models--FunAudioLLM--SenseVoiceSmall/snapshots/3eb3b4eeffc2f2dde6051b853983753db33e35c3"
        )
        self.asr_model_revision = "v2.0.4"
        self.vad_model_path = os.path.join(
            self.home_directory, 
            "iic/speech_fsmn_vad_zh-cn-16k-common-pytorch"
        )
        self.vad_model_revision = "v2.0.4"
        self.punc_model_path = os.path.join(
            self.home_directory, 
            "iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch"
        )
        self.punc_model_revision = "v2.0.4"
        
        # ASR参数
        self.chunk_size = [10, 20, 10]  # 左回看数，总片段数，右回看数
        self.sample_rate = 16000
        self.chunk_duration = 0.06  # 60ms per chunk
        self.samples_per_chunk = int(self.sample_rate * self.chunk_duration)  # 960 samples
    
    async def initialize(self):
        """初始化ASR模型"""
        if self.is_initialized:
            return
        
        try:
            logger.info("正在初始化ASR模型...")
            
            # 在线程池中加载模型，避免阻塞事件循环
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                self.executor, self._load_model
            )
            
            self.is_initialized = True
            logger.info("ASR模型初始化完成")
            
        except Exception as e:
            logger.error(f"ASR模型初始化失败: {e}")
            raise
    
    def _load_model(self):
        """加载ASR模型（在线程池中执行）"""
        return AutoModel(
            model=self.asr_model_path,
            model_revision=self.asr_model_revision,
            vad_model=self.vad_model_path,
            vad_model_revision=self.vad_model_revision,
            punc_model=self.punc_model_path,
            punc_model_revision=self.punc_model_revision,
            ngpu=1,
            ncpu=4,
            device="cuda",
            disable_pbar=True,
            disable_log=True,
            disable_update=True
        )
    
    def is_ready(self) -> bool:
        """检查ASR服务是否就绪"""
        return self.is_initialized and self.model is not None
    
    async def start_recording(self, meeting_id: str, client_id: str):
        """开始录制会议"""
        if not self.is_ready():
            raise RuntimeError("ASR服务未就绪")
        
        session_data = {
            "meeting_id": meeting_id,
            "client_id": client_id,
            "start_time": datetime.now(),
            "chunks": [],
            "param_dict": {'cache': dict()},
            "line_buffer": "",
            "old_prediction": "",
            "pre_num": 0,
            "pre_expect": 5,
            "printed_num": 0,
            "line_width": 50,
            "is_recording": True
        }
        
        self.active_sessions[meeting_id] = session_data
        logger.info(f"开始录制会议 {meeting_id}")
    
    async def stop_recording(self, meeting_id: str, client_id: str):
        """停止录制会议"""
        if meeting_id in self.active_sessions:
            session = self.active_sessions[meeting_id]
            session["is_recording"] = False
            session["end_time"] = datetime.now()
            
            # 处理剩余的音频块
            if session["chunks"]:
                final_result = await self._process_final_chunks(session)
                if final_result:
                    logger.info(f"会议 {meeting_id} 最终识别结果: {final_result}")
            
            logger.info(f"停止录制会议 {meeting_id}")
        
    async def process_audio(self, meeting_id: str, audio_data: str, client_id: str) -> Optional[Dict[str, Any]]:
        """处理音频数据"""
        if not self.is_ready():
            logger.error("ASR服务未就绪")
            return None
        
        if meeting_id not in self.active_sessions:
            logger.error(f"会议 {meeting_id} 未开始录制")
            return None
        
        session = self.active_sessions[meeting_id]
        if not session["is_recording"]:
            return None
        
        try:
            # 解码音频数据
            audio_bytes = base64.b64decode(audio_data)
            audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
            
            # 重采样到16kHz（如果需要）
            if len(audio_array) != self.samples_per_chunk:
                # 简单的重采样处理
                audio_array = self._resample_audio(audio_array)
            
            # 添加到音频块列表
            session["chunks"].append(audio_array)
            session["pre_num"] += 1
            
            # 预测处理
            prediction_result = await self._handle_prediction(session)
            
            # 实际识别处理
            recognition_result = await self._handle_recognition(session)
            
            # 返回识别结果
            if recognition_result:
                return {
                    "text": recognition_result,
                    "speaker": "说话人1",  # SenseVoiceSmall不支持说话人分离
                    "timestamp": (datetime.now() - session["start_time"]).total_seconds(),
                    "confidence": 0.95,  # 模拟置信度
                    "is_final": True
                }
            elif prediction_result:
                return {
                    "text": prediction_result,
                    "speaker": "说话人1",
                    "timestamp": (datetime.now() - session["start_time"]).total_seconds(),
                    "confidence": 0.8,
                    "is_final": False
                }
            
            return None
            
        except Exception as e:
            logger.error(f"处理音频数据失败: {e}")
            return None
    
    def _resample_audio(self, audio_array: np.ndarray) -> np.ndarray:
        """重采样音频到目标长度"""
        target_length = self.samples_per_chunk
        current_length = len(audio_array)
        
        if current_length == target_length:
            return audio_array
        elif current_length > target_length:
            # 下采样
            step = current_length / target_length
            indices = np.arange(0, current_length, step)[:target_length]
            return audio_array[indices.astype(int)]
        else:
            # 上采样（零填充）
            padded = np.zeros(target_length, dtype=np.float32)
            padded[:current_length] = audio_array
            return padded
    
    async def _handle_prediction(self, session: Dict) -> Optional[str]:
        """处理预测识别"""
        chunks = session["chunks"]
        pre_num = session["pre_num"]
        pre_expect = session["pre_expect"]
        
        # 每攒够5个片段，就预测一下虚文字
        if len(chunks) < self.chunk_size[1] and pre_num == pre_expect:
            session["pre_num"] = 0
            
            try:
                data = np.concatenate(chunks)
                virtual_dict = deepcopy(session["param_dict"])
                virtual_dict['is_final'] = True
                
                # 在线程池中执行识别
                loop = asyncio.get_event_loop()
                rec_result = await loop.run_in_executor(
                    self.executor,
                    lambda: self.model.generate(input=data, cache=virtual_dict.get('cache', {}))
                )
                
                if rec_result and rec_result[0].get('text'):
                    prediction = rec_result[0]['text']
                    if prediction and prediction != session["old_prediction"]:
                        session["old_prediction"] = prediction
                        return session["line_buffer"] + prediction
                        
            except Exception as e:
                logger.error(f"预测识别失败: {e}")
        
        elif pre_num == 5:
            session["pre_num"] = 0
        
        return None
    
    async def _handle_recognition(self, session: Dict) -> Optional[str]:
        """处理实际识别"""
        chunks = session["chunks"]
        
        # 显示实文字
        if len(chunks) == self.chunk_size[1]:
            try:
                data = np.concatenate(chunks)
                
                # 在线程池中执行识别
                loop = asyncio.get_event_loop()
                rec_result = await loop.run_in_executor(
                    self.executor,
                    lambda: self.model.generate(input=data, cache=session["param_dict"].get('cache', {}))
                )
                
                if rec_result and rec_result[0].get('text'):
                    text = rec_result[0]['text']
                    if text:
                        # 英文后面加空格
                        if text and text[-1].isalpha():
                            text += ' '
                        
                        session["line_buffer"] += text
                        session["printed_num"] += len(text.encode('utf-8'))
                        
                        # 每到长度极限，就清空换行
                        if session["printed_num"] >= session["line_width"]:
                            result = session["line_buffer"]
                            session["line_buffer"] = ""
                            session["printed_num"] = 0
                            chunks.clear()
                            return result
                        
                        chunks.clear()
                        return session["line_buffer"]
                
                chunks.clear()
                
            except Exception as e:
                logger.error(f"实际识别失败: {e}")
                chunks.clear()
        
        return None
    
    async def _process_final_chunks(self, session: Dict) -> Optional[str]:
        """处理最终的音频块"""
        chunks = session["chunks"]
        
        if not chunks:
            chunks.append(np.zeros(self.samples_per_chunk, dtype=np.float32))
        
        try:
            data = np.concatenate(chunks)
            
            # 在线程池中执行识别
            loop = asyncio.get_event_loop()
            rec_result = await loop.run_in_executor(
                self.executor,
                lambda: self.model.generate(input=data, cache=session["param_dict"].get('cache', {}))
            )
            
            if rec_result and rec_result[0].get('text'):
                final_text = rec_result[0]['text']
                chunks.clear()
                session["param_dict"] = {'cache': dict()}
                return final_text
                
        except Exception as e:
            logger.error(f"处理最终音频块失败: {e}")
        
        return None
    
    async def get_session_info(self, meeting_id: str) -> Optional[Dict]:
        """获取会议录制会话信息"""
        if meeting_id in self.active_sessions:
            session = self.active_sessions[meeting_id]
            return {
                "meeting_id": meeting_id,
                "client_id": session["client_id"],
                "start_time": session["start_time"].isoformat(),
                "is_recording": session["is_recording"],
                "chunks_count": len(session["chunks"]),
                "line_buffer": session["line_buffer"]
            }
        return None
    
    async def cleanup(self):
        """清理ASR服务"""
        logger.info("正在清理ASR服务...")
        
        # 停止所有活动会话
        for meeting_id in list(self.active_sessions.keys()):
            session = self.active_sessions[meeting_id]
            session["is_recording"] = False
        
        self.active_sessions.clear()
        
        # 关闭线程池
        if self.executor:
            self.executor.shutdown(wait=True)
        
        self.is_initialized = False
        logger.info("ASR服务清理完成")