#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI总结服务
实现会议内容的智能总结功能
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta

from models import TranscriptRecord, MeetingSummary

logger = logging.getLogger(__name__)

class SummaryService:
    """AI总结服务类"""
    
    def __init__(self):
        # 关键词模式
        self.action_keywords = [
            r'需要.*?做', r'要.*?完成', r'负责.*?处理', r'安排.*?进行',
            r'计划.*?实施', r'准备.*?材料', r'联系.*?确认', r'跟进.*?进展',
            r'提交.*?报告', r'完善.*?方案', r'优化.*?流程', r'改进.*?方法'
        ]
        
        self.key_point_keywords = [
            r'重点.*?是', r'关键.*?在于', r'核心.*?问题', r'主要.*?目标',
            r'重要.*?事项', r'关注.*?方面', r'优先.*?考虑', r'首先.*?要',
            r'其次.*?是', r'最后.*?需要', r'总结.*?来说', r'综合.*?分析'
        ]
        
        self.decision_keywords = [
            r'决定.*?采用', r'确定.*?方案', r'同意.*?建议', r'批准.*?计划',
            r'通过.*?提案', r'选择.*?方式', r'采纳.*?意见', r'接受.*?建议'
        ]
    
    def generate_summary(self, transcripts: List[TranscriptRecord], 
                        meeting_duration: int) -> MeetingSummary:
        """生成会议总结"""
        if not transcripts:
            return self._create_empty_summary("暂无转录内容")
        
        # 合并转录文本
        full_text = self._merge_transcripts(transcripts)
        
        # 分析参与者发言
        participants_analysis = self._analyze_participants(transcripts)
        
        # 提取关键要点
        key_points = self._extract_key_points(full_text)
        
        # 提取行动项
        action_items = self._extract_action_items(full_text)
        
        # 生成总结文本
        summary_text = self._generate_summary_text(
            full_text, key_points, action_items, len(participants_analysis)
        )
        
        # 生成时长总结
        duration_summary = self._generate_duration_summary(meeting_duration)
        
        return MeetingSummary(
            meeting_id=transcripts[0].meeting_id,
            summary=summary_text,
            key_points=key_points,
            action_items=action_items,
            participants_summary=participants_analysis,
            duration_summary=duration_summary
        )
    
    def _merge_transcripts(self, transcripts: List[TranscriptRecord]) -> str:
        """合并转录文本"""
        # 只使用最终确认的转录结果
        final_transcripts = [t for t in transcripts if t.is_final]
        
        if not final_transcripts:
            final_transcripts = transcripts
        
        # 按时间戳排序
        final_transcripts.sort(key=lambda x: x.timestamp)
        
        # 合并文本，去除重复
        merged_text = ""
        last_text = ""
        
        for transcript in final_transcripts:
            text = transcript.text.strip()
            if text and text != last_text:
                merged_text += text + " "
                last_text = text
        
        return merged_text.strip()
    
    def _analyze_participants(self, transcripts: List[TranscriptRecord]) -> Dict[str, str]:
        """分析参与者发言"""
        participants = {}
        
        for transcript in transcripts:
            if not transcript.is_final:
                continue
                
            speaker = transcript.speaker
            text = transcript.text.strip()
            
            if speaker not in participants:
                participants[speaker] = ""
            
            participants[speaker] += text + " "
        
        # 为每个参与者生成发言总结
        summaries = {}
        for speaker, content in participants.items():
            content = content.strip()
            if content:
                summary = self._summarize_participant_content(content)
                summaries[speaker] = summary
        
        return summaries
    
    def _summarize_participant_content(self, content: str) -> str:
        """总结参与者发言内容"""
        if len(content) <= 50:
            return content
        
        # 简单的总结逻辑：提取关键句子
        sentences = re.split(r'[。！？.!?]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 2:
            return content[:100] + "..."
        
        # 选择前两个句子作为总结
        summary = "。".join(sentences[:2])
        if len(summary) > 100:
            summary = summary[:100] + "..."
        
        return summary
    
    def _extract_key_points(self, text: str) -> List[str]:
        """提取关键要点"""
        key_points = []
        
        # 使用关键词模式提取
        for pattern in self.key_point_keywords:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # 提取匹配位置前后的文本作为要点
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 50)
                point = text[start:end].strip()
                
                if len(point) > 10 and point not in key_points:
                    key_points.append(point)
        
        # 如果没有找到关键词，则提取句子
        if not key_points:
            sentences = re.split(r'[。！？.!?]', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
            
            # 选择前3个较长的句子作为要点
            key_points = sentences[:3]
        
        return key_points[:5]  # 最多返回5个要点
    
    def _extract_action_items(self, text: str) -> List[str]:
        """提取行动项"""
        action_items = []
        
        # 使用行动关键词模式提取
        for pattern in self.action_keywords:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # 提取匹配位置前后的文本作为行动项
                start = max(0, match.start() - 10)
                end = min(len(text), match.end() + 40)
                action = text[start:end].strip()
                
                if len(action) > 8 and action not in action_items:
                    action_items.append(action)
        
        # 查找决策相关内容
        for pattern in self.decision_keywords:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 10)
                end = min(len(text), match.end() + 40)
                decision = text[start:end].strip()
                
                if len(decision) > 8 and decision not in action_items:
                    action_items.append(decision)
        
        return action_items[:8]  # 最多返回8个行动项
    
    def _generate_summary_text(self, full_text: str, key_points: List[str], 
                              action_items: List[str], participant_count: int) -> str:
        """生成总结文本"""
        if not full_text:
            return "本次会议暂无有效的转录内容。"
        
        # 计算文本长度和字数
        word_count = len(full_text)
        
        # 生成基础总结
        summary_parts = []
        
        # 会议概述
        summary_parts.append(f"本次会议共有{participant_count}位参与者，")
        summary_parts.append(f"会议内容共计{word_count}字。")
        
        # 主要内容总结
        if len(full_text) > 200:
            # 提取前100字作为开头总结
            opening = full_text[:100].strip()
            if not opening.endswith(('。', '！', '？', '.', '!', '?')):
                opening += "..."
            summary_parts.append(f"会议主要讨论了：{opening}")
        else:
            summary_parts.append(f"会议内容：{full_text}")
        
        # 关键要点总结
        if key_points:
            summary_parts.append(f"\n会议重点包括{len(key_points)}个方面：")
            for i, point in enumerate(key_points, 1):
                summary_parts.append(f"{i}. {point}")
        
        # 行动项总结
        if action_items:
            summary_parts.append(f"\n会议确定了{len(action_items)}项后续行动：")
            for i, action in enumerate(action_items, 1):
                summary_parts.append(f"{i}. {action}")
        
        return "\n".join(summary_parts)
    
    def _generate_duration_summary(self, duration_seconds: int) -> str:
        """生成时长总结"""
        if duration_seconds <= 0:
            return "会议时长：未知"
        
        duration = timedelta(seconds=duration_seconds)
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        seconds = duration.seconds % 60
        
        if hours > 0:
            return f"会议时长：{hours}小时{minutes}分钟{seconds}秒"
        elif minutes > 0:
            return f"会议时长：{minutes}分钟{seconds}秒"
        else:
            return f"会议时长：{seconds}秒"
    
    def _create_empty_summary(self, reason: str) -> MeetingSummary:
        """创建空的总结"""
        return MeetingSummary(
            meeting_id="",
            summary=f"无法生成会议总结：{reason}",
            key_points=[],
            action_items=[],
            participants_summary={},
            duration_summary="会议时长：未知"
        )
    
    def generate_real_time_summary(self, recent_transcripts: List[TranscriptRecord], 
                                  window_minutes: int = 5) -> Dict[str, str]:
        """生成实时总结（最近几分钟的内容）"""
        if not recent_transcripts:
            return {"summary": "暂无最新内容"}
        
        # 过滤最近的转录记录
        now = datetime.now()
        cutoff_time = (now - timedelta(minutes=window_minutes)).timestamp()
        
        recent = [
            t for t in recent_transcripts 
            if t.timestamp >= cutoff_time and t.is_final
        ]
        
        if not recent:
            return {"summary": f"最近{window_minutes}分钟暂无新内容"}
        
        # 合并最近的文本
        recent_text = self._merge_transcripts(recent)
        
        # 生成简短总结
        if len(recent_text) <= 100:
            summary = recent_text
        else:
            # 提取前50字和后50字
            summary = recent_text[:50] + "..." + recent_text[-50:]
        
        return {
            "summary": f"最近{window_minutes}分钟：{summary}",
            "word_count": len(recent_text),
            "transcript_count": len(recent)
        }