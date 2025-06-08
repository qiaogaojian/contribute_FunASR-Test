#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理服务
处理音频文件、转录文件和总结文件的存储和管理
"""

import os
import json
import wave
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

import numpy as np

from models import Meeting, TranscriptRecord, MeetingSummary

logger = logging.getLogger(__name__)

class FileService:
    """文件管理服务类"""
    
    def __init__(self, output_dir: str = "output/meeting"):
        self.output_dir = Path(output_dir)
        self.audio_dir = self.output_dir / "audio"
        self.transcript_dir = self.output_dir / "transcripts"
        self.summary_dir = self.output_dir / "summaries"
        
        # 确保目录存在
        self._ensure_directories()
        
        # 音频参数
        self.sample_rate = 16000
        self.channels = 1
        self.sample_width = 2  # 16-bit
    
    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        for directory in [self.output_dir, self.audio_dir, self.transcript_dir, self.summary_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"确保目录存在: {directory}")
    
    def get_meeting_audio_path(self, meeting_id: str) -> Path:
        """获取会议音频文件路径"""
        return self.audio_dir / f"{meeting_id}.wav"
    
    def get_meeting_transcript_path(self, meeting_id: str) -> Path:
        """获取会议转录文件路径"""
        return self.transcript_dir / f"{meeting_id}.json"
    
    def get_meeting_summary_path(self, meeting_id: str) -> Path:
        """获取会议总结文件路径"""
        return self.summary_dir / f"{meeting_id}.json"
    
    def get_meeting_text_path(self, meeting_id: str) -> Path:
        """获取会议纯文本文件路径"""
        return self.transcript_dir / f"{meeting_id}.txt"
    
    def start_audio_recording(self, meeting_id: str) -> 'AudioRecorder':
        """开始音频录制"""
        audio_path = self.get_meeting_audio_path(meeting_id)
        return AudioRecorder(audio_path, self.sample_rate, self.channels, self.sample_width)
    
    def save_transcript_file(self, meeting_id: str, transcripts: List[TranscriptRecord]) -> str:
        """保存转录文件"""
        transcript_path = self.get_meeting_transcript_path(meeting_id)
        text_path = self.get_meeting_text_path(meeting_id)
        
        try:
            # 保存JSON格式的详细转录数据
            transcript_data = {
                "meeting_id": meeting_id,
                "created_at": datetime.now().isoformat(),
                "total_records": len(transcripts),
                "transcripts": [t.dict() for t in transcripts]
            }
            
            with open(transcript_path, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, ensure_ascii=False, indent=2, default=str)
            
            # 保存纯文本格式
            self._save_text_transcript(text_path, transcripts)
            
            logger.info(f"保存转录文件: {transcript_path}")
            return str(transcript_path)
            
        except Exception as e:
            logger.error(f"保存转录文件失败: {e}")
            raise
    
    def _save_text_transcript(self, text_path: Path, transcripts: List[TranscriptRecord]):
        """保存纯文本转录文件"""
        try:
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(f"会议转录记录\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"总记录数: {len(transcripts)}\n")
                f.write("=" * 50 + "\n\n")
                
                current_speaker = None
                for transcript in transcripts:
                    if not transcript.is_final:
                        continue
                    
                    # 格式化时间戳
                    minutes = int(transcript.timestamp // 60)
                    seconds = int(transcript.timestamp % 60)
                    time_str = f"[{minutes:02d}:{seconds:02d}]"
                    
                    # 如果说话人变化，添加分隔
                    if current_speaker != transcript.speaker:
                        if current_speaker is not None:
                            f.write("\n")
                        f.write(f"\n{transcript.speaker}:\n")
                        current_speaker = transcript.speaker
                    
                    f.write(f"{time_str} {transcript.text}\n")
                
            logger.info(f"保存纯文本转录: {text_path}")
            
        except Exception as e:
            logger.error(f"保存纯文本转录失败: {e}")
    
    def save_summary_file(self, meeting_id: str, summary: MeetingSummary) -> str:
        """保存会议总结文件"""
        summary_path = self.get_meeting_summary_path(meeting_id)
        
        try:
            summary_data = {
                "meeting_id": meeting_id,
                "created_at": datetime.now().isoformat(),
                "summary": summary.dict()
            }
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2, default=str)
            
            # 同时保存纯文本格式的总结
            text_summary_path = self.summary_dir / f"{meeting_id}.txt"
            self._save_text_summary(text_summary_path, summary)
            
            logger.info(f"保存总结文件: {summary_path}")
            return str(summary_path)
            
        except Exception as e:
            logger.error(f"保存总结文件失败: {e}")
            raise
    
    def _save_text_summary(self, text_path: Path, summary: MeetingSummary):
        """保存纯文本总结文件"""
        try:
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(f"会议总结报告\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"会议时长: {summary.duration_summary}\n")
                f.write("=" * 50 + "\n\n")
                
                # 会议总结
                f.write("## 会议总结\n")
                f.write(f"{summary.summary}\n\n")
                
                # 关键要点
                if summary.key_points:
                    f.write("## 关键要点\n")
                    for i, point in enumerate(summary.key_points, 1):
                        f.write(f"{i}. {point}\n")
                    f.write("\n")
                
                # 行动项
                if summary.action_items:
                    f.write("## 行动项\n")
                    for i, action in enumerate(summary.action_items, 1):
                        f.write(f"{i}. {action}\n")
                    f.write("\n")
                
                # 参与者发言总结
                if summary.participants_summary:
                    f.write("## 参与者发言总结\n")
                    for speaker, content in summary.participants_summary.items():
                        f.write(f"**{speaker}**: {content}\n")
                    f.write("\n")
                
            logger.info(f"保存纯文本总结: {text_path}")
            
        except Exception as e:
            logger.error(f"保存纯文本总结失败: {e}")
    
    def load_transcript_file(self, meeting_id: str) -> Optional[List[TranscriptRecord]]:
        """加载转录文件"""
        transcript_path = self.get_meeting_transcript_path(meeting_id)
        
        if not transcript_path.exists():
            return None
        
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            transcripts = [TranscriptRecord(**t) for t in data['transcripts']]
            return transcripts
            
        except Exception as e:
            logger.error(f"加载转录文件失败: {e}")
            return None
    
    def load_summary_file(self, meeting_id: str) -> Optional[MeetingSummary]:
        """加载总结文件"""
        summary_path = self.get_meeting_summary_path(meeting_id)
        
        if not summary_path.exists():
            return None
        
        try:
            with open(summary_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            summary = MeetingSummary(**data['summary'])
            return summary
            
        except Exception as e:
            logger.error(f"加载总结文件失败: {e}")
            return None
    
    def get_file_info(self, meeting_id: str) -> Dict[str, Any]:
        """获取会议文件信息"""
        audio_path = self.get_meeting_audio_path(meeting_id)
        transcript_path = self.get_meeting_transcript_path(meeting_id)
        summary_path = self.get_meeting_summary_path(meeting_id)
        text_path = self.get_meeting_text_path(meeting_id)
        
        info = {
            "meeting_id": meeting_id,
            "files": {
                "audio": {
                    "path": str(audio_path),
                    "exists": audio_path.exists(),
                    "size": audio_path.stat().st_size if audio_path.exists() else 0
                },
                "transcript_json": {
                    "path": str(transcript_path),
                    "exists": transcript_path.exists(),
                    "size": transcript_path.stat().st_size if transcript_path.exists() else 0
                },
                "transcript_text": {
                    "path": str(text_path),
                    "exists": text_path.exists(),
                    "size": text_path.stat().st_size if text_path.exists() else 0
                },
                "summary": {
                    "path": str(summary_path),
                    "exists": summary_path.exists(),
                    "size": summary_path.stat().st_size if summary_path.exists() else 0
                }
            }
        }
        
        return info
    
    def delete_meeting_files(self, meeting_id: str) -> Dict[str, bool]:
        """删除会议相关文件"""
        results = {}
        
        files_to_delete = [
            ("audio", self.get_meeting_audio_path(meeting_id)),
            ("transcript_json", self.get_meeting_transcript_path(meeting_id)),
            ("transcript_text", self.get_meeting_text_path(meeting_id)),
            ("summary_json", self.get_meeting_summary_path(meeting_id)),
            ("summary_text", self.summary_dir / f"{meeting_id}.txt")
        ]
        
        for file_type, file_path in files_to_delete:
            try:
                if file_path.exists():
                    file_path.unlink()
                    results[file_type] = True
                    logger.info(f"删除文件: {file_path}")
                else:
                    results[file_type] = True  # 文件不存在也算成功
            except Exception as e:
                logger.error(f"删除文件失败 {file_path}: {e}")
                results[file_type] = False
        
        return results

class AudioRecorder:
    """音频录制器"""
    
    def __init__(self, file_path: Path, sample_rate: int, channels: int, sample_width: int):
        self.file_path = file_path
        self.sample_rate = sample_rate
        self.channels = channels
        self.sample_width = sample_width
        self.audio_data = []
        self.is_recording = False
        self._wave_file = None
    
    def start(self):
        """开始录制"""
        try:
            self._wave_file = wave.open(str(self.file_path), 'wb')
            self._wave_file.setnchannels(self.channels)
            self._wave_file.setsampwidth(self.sample_width)
            self._wave_file.setframerate(self.sample_rate)
            self.is_recording = True
            logger.info(f"开始音频录制: {self.file_path}")
        except Exception as e:
            logger.error(f"开始音频录制失败: {e}")
            raise
    
    def add_audio_data(self, audio_data: np.ndarray):
        """添加音频数据"""
        if not self.is_recording or self._wave_file is None:
            return
        
        try:
            # 转换为16位整数
            audio_int16 = (audio_data * 32767).astype(np.int16)
            self._wave_file.writeframes(audio_int16.tobytes())
        except Exception as e:
            logger.error(f"写入音频数据失败: {e}")
    
    def stop(self):
        """停止录制"""
        if self._wave_file:
            try:
                self._wave_file.close()
                self.is_recording = False
                logger.info(f"停止音频录制: {self.file_path}")
            except Exception as e:
                logger.error(f"停止音频录制失败: {e}")
            finally:
                self._wave_file = None
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()