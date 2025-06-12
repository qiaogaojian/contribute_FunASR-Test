#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会议总结API模块
提供会议记录总结相关的REST API接口
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import logging
from datetime import datetime

from app.llm import (
    LLMManager,
    LLMRequest,
    ChatMessage,
    MessageRole
)
from app.llm.exceptions import LLMError
from app.models.schemas import BaseResponse
from app.api.llm_routes import get_llm_manager

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/meeting", tags=["Meeting Summary"])


# ============================================================================
# 数据模型
# ============================================================================

class SummaryType(str):
    """总结类型枚举"""
    BRIEF = "brief"
    DETAILED = "detailed"
    ACTION = "action"
    OPTIMIZE = "optimize"  # 内部使用，用于文本优化


class MeetingSummaryRequest(BaseModel):
    """会议总结请求模型"""
    meeting_text: str = Field(..., description="会议记录文本", min_length=1)
    summary_type: str = Field(..., description="总结类型: brief, detailed, action")
    model: str = Field(default="gemini-1.5-flash", description="使用的LLM模型")
    temperature: Optional[float] = Field(default=0.3, description="温度参数")
    
    class Config:
        schema_extra = {
            "example": {
                "meeting_text": "[14:30:15] 今天我们讨论项目进度...",
                "summary_type": "brief",
                "model": "gemini-1.5-flash",
                "temperature": 0.3
            }
        }


class MeetingSummaryResponse(BaseResponse):
    """会议总结响应模型"""
    summary: str = Field(description="总结内容")
    summary_type: str = Field(description="总结类型")
    model: str = Field(description="使用的模型")
    processing_time: float = Field(description="处理时间（秒）")
    optimized_text: Optional[str] = Field(None, description="优化后的原始文本（仅用于调试）")


# ============================================================================
# 提示词模板
# ============================================================================

class PromptTemplates:
    """提示词模板类"""
    
    @staticmethod
    def get_optimize_prompt(meeting_text: str) -> str:
        """获取文本优化提示词"""
        return f"""你是一个专业的语音识别文本优化专家。以下是通过ASR(语音识别)技术转换的会议记录文本，由于语音识别技术的局限性，文本中存在各种识别错误。请帮助我优化和修正这些文本，确保优化后的文本语义准确、语言流畅、逻辑清晰，同时完全保持会议记录的原始含义和重要信息。

**原始ASR识别文本：**
{meeting_text}

**详细优化要求：**

1. **同音字错误修正**：
   - 修正常见同音字错误：在/再、的/得、做/作、那/哪、因为/应为、以后/已后、现在/现再等
   - 根据上下文语境选择正确用字
   - 特别注意动词、介词、助词的正确使用

2. **标点符号优化**：
   - 补充缺失的逗号、句号、问号、感叹号、冒号、分号
   - 优化语句断句，提升文本可读性
   - 为直接引语添加引号
   - 合理使用顿号分隔并列成分

3. **语法和表达优化**：
   - 修正语序错误和不通顺的表达
   - 补充缺失的主语、谓语、宾语
   - 修正时态和语态错误
   - 优化口语化表达，使其更加书面化和专业

4. **格式和结构保持**：
   - 严格保持原始时间戳格式：[HH:MM:SS]
   - 保持会议记录的时间顺序
   - 维持发言人信息（如有）
   - 保持段落结构的逻辑性

5. **内容准确性**：
   - 保持原意不变，只进行必要的修正
   - 对专业术语和人名根据上下文进行合理推断
   - 不添加原文中没有的信息
   - 保持会议内容的真实性和完整性

**输出格式要求：**

[在此输出完整的优化后会议记录，严格保持时间戳格式]
"""

    @staticmethod
    def get_brief_prompt(meeting_text: str) -> str:
        """获取简要总结提示词"""
        return f"""你是一个专业的会议记录分析专家。以下是会议记录文本，请提取关键要点并进行简要总结。

**会议记录：**
{meeting_text}

**分析要求：**
1. **关键信息提取**: 重点关注决策、行动项、重要讨论点
2. **逻辑梳理**: 整理会议的主要脉络和核心内容
3. **准确表达**: 用准确、专业的语言表达总结内容

**输出格式：**
## 📋 会议简要总结

### 🎯 主要议题
- [列出主要讨论的议题]

### ✅ 关键决定
- [列出重要决定和结论]

### 💡 重要信息
- [列出其他重要信息]
"""

    @staticmethod
    def get_detailed_prompt(meeting_text: str) -> str:
        """获取详细总结提示词"""
        return f"""你是一个资深的会议分析师，擅长提取和整理完整的会议信息。以下是会议记录文本，请进行详细分析和总结。

**会议记录：**
{meeting_text}

**分析要求：**
1. **全面分析**: 深入分析会议的各个方面和层次
2. **逻辑梳理**: 组织和梳理会议内容的逻辑结构
3. **专业表达**: 使用准确、专业的商务语言进行表述
4. **细节保留**: 保留重要的讨论细节和关键信息

**输出格式：**
## 📊 会议详细总结

### 🎯 会议概述
[描述会议的整体情况、背景和目标]

### 💬 讨论内容
[详细描述各个议题的讨论过程，保持逻辑清晰]

### 📋 决策事项
[列出所有决定和决策]

### 🔍 关键观点
[记录重要的观点和建议]

### 📅 后续安排
[整理后续计划或安排]
"""

    @staticmethod
    def get_action_prompt(meeting_text: str) -> str:
        """获取行动项总结提示词"""
        return f"""你是一个专业的项目管理专家，擅长从会议记录中提取可执行的行动项。以下是会议记录文本，请提取准确的行动项和待办事项。

**会议记录：**
{meeting_text}

**提取要求：**
1. **准确识别**: 准确识别会议中的行动项
2. **责任明确**: 识别和明确任务的负责人
3. **时间明确**: 准确提取时间节点和截止日期
4. **任务具体**: 将模糊的表述转化为具体可执行的任务
5. **优先级判断**: 根据讨论内容判断任务的重要性和紧急性

**输出格式：**
## 📋 行动项总结

### ✅ 待办事项
- **任务**: [具体的待办任务]
- **负责人**: [负责人姓名或部门，如有提及]
- **截止时间**: [时间节点]
- **优先级**: [高/中/低，基于讨论内容判断]

### 🔄 跟进事项
- [需要持续跟进的事项]

### 📅 下次会议议题
- [下次会议需要讨论的内容]

### ⚠️ 注意事项
- [需要特别注意的事项和风险点]
"""


# ============================================================================
# 业务逻辑
# ============================================================================

class MeetingSummaryService:
    """会议总结服务类"""
    
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
        self.token_limits = {
            SummaryType.BRIEF: 1200,
            SummaryType.DETAILED: 1800,
            SummaryType.ACTION: 1500,
            SummaryType.OPTIMIZE: 2000
        }
    
    async def generate_summary(
        self,
        meeting_text: str,
        summary_type: str,
        model: str = "gemini-1.5-flash",
        temperature: float = 0.3
    ) -> tuple[str, str]:
        """
        生成会议总结
        
        Args:
            meeting_text: 会议记录文本
            summary_type: 总结类型
            model: LLM模型
            temperature: 温度参数
            
        Returns:
            tuple[总结内容, 优化后的原始文本]
        """
        # 验证总结类型
        if summary_type not in [SummaryType.BRIEF, SummaryType.DETAILED, SummaryType.ACTION]:
            raise ValueError(f"不支持的总结类型: {summary_type}")
        
        # 第一步：优化ASR文本
        logger.info(f"开始优化ASR文本，原始文本长度: {len(meeting_text)}")
        optimized_text = await self._call_llm(
            meeting_text=meeting_text,
            prompt_type=SummaryType.OPTIMIZE,
            model=model,
            temperature=temperature
        )
        logger.info(f"ASR文本优化完成，优化后长度: {len(optimized_text)}")
        
        # 第二步：使用优化后的文本生成总结
        logger.info(f"开始生成{summary_type}总结")
        summary = await self._call_llm(
            meeting_text=optimized_text,
            prompt_type=summary_type,
            model=model,
            temperature=temperature
        )
        logger.info(f"{summary_type}总结生成完成，总结长度: {len(summary)}")
        
        return summary, optimized_text
    
    async def _call_llm(
        self,
        meeting_text: str,
        prompt_type: str,
        model: str,
        temperature: float
    ) -> str:
        """调用LLM生成内容"""
        # 获取提示词
        prompt = self._get_prompt(meeting_text, prompt_type)
        
        # 创建消息
        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        
        # 创建LLM请求
        llm_request = LLMRequest(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=self.token_limits.get(prompt_type, 1000),
            stream=False
        )
        
        # 调用LLM
        try:
            response = await self.llm_manager.generate_response(llm_request)
            return response.content
        except LLMError as e:
            logger.error(f"LLM调用失败: {e}")
            raise HTTPException(status_code=400, detail=f"LLM调用失败: {str(e)}")
        except Exception as e:
            logger.error(f"LLM调用异常: {e}")
            raise HTTPException(status_code=500, detail=f"内部错误: {str(e)}")
    
    def _get_prompt(self, meeting_text: str, prompt_type: str) -> str:
        """获取对应类型的提示词"""
        if prompt_type == SummaryType.OPTIMIZE:
            return PromptTemplates.get_optimize_prompt(meeting_text)
        elif prompt_type == SummaryType.BRIEF:
            return PromptTemplates.get_brief_prompt(meeting_text)
        elif prompt_type == SummaryType.DETAILED:
            return PromptTemplates.get_detailed_prompt(meeting_text)
        elif prompt_type == SummaryType.ACTION:
            return PromptTemplates.get_action_prompt(meeting_text)
        else:
            raise ValueError(f"未知的提示词类型: {prompt_type}")


# ============================================================================
# API端点
# ============================================================================

@router.post("/summary", response_model=MeetingSummaryResponse)
async def create_meeting_summary(
    request: MeetingSummaryRequest,
    llm_manager: LLMManager = Depends(get_llm_manager)
):
    """
    生成会议总结

    支持的总结类型：
    - brief: 简要总结（重点摘要）
    - detailed: 详细总结（完整分析）
    - action: 行动项总结（待办事项）

    处理流程：
    1. 自动优化ASR文本（修正同音字、语法、标点等错误）
    2. 基于优化后的文本生成对应类型的总结
    """
    start_time = datetime.utcnow()

    try:
        # 验证总结类型
        valid_types = [SummaryType.BRIEF, SummaryType.DETAILED, SummaryType.ACTION]
        if request.summary_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的总结类型: {request.summary_type}。支持的类型: {', '.join(valid_types)}"
            )

        # 创建服务实例
        service = MeetingSummaryService(llm_manager)

        # 生成总结
        summary, optimized_text = await service.generate_summary(
            meeting_text=request.meeting_text,
            summary_type=request.summary_type,
            model=request.model,
            temperature=request.temperature
        )

        # 计算处理时间
        processing_time = (datetime.utcnow() - start_time).total_seconds()

        logger.info(f"会议总结生成成功: 类型={request.summary_type}, 模型={request.model}, 处理时间={processing_time:.2f}s")

        return MeetingSummaryResponse(
            success=True,
            message="会议总结生成成功",
            summary=summary,
            summary_type=request.summary_type,
            model=request.model,
            processing_time=processing_time,
            optimized_text=optimized_text if logger.isEnabledFor(logging.DEBUG) else None
        )

    except HTTPException:
        raise
    except Exception as e:
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"会议总结生成失败: {e}, 处理时间={processing_time:.2f}s")
        raise HTTPException(
            status_code=500,
            detail=f"会议总结生成失败: {str(e)}"
        )


@router.get("/summary/types")
async def get_summary_types():
    """获取支持的总结类型列表"""
    return {
        "success": True,
        "message": "总结类型列表获取成功",
        "types": [
            {
                "type": SummaryType.BRIEF,
                "name": "简要总结",
                "description": "重点摘要，提取关键决策和重要信息"
            },
            {
                "type": SummaryType.DETAILED,
                "name": "详细总结",
                "description": "完整分析，包含会议概述、讨论内容、决策事项等"
            },
            {
                "type": SummaryType.ACTION,
                "name": "行动项总结",
                "description": "待办事项，提取具体的任务、负责人和时间节点"
            }
        ]
    }


@router.get("/health")
async def health_check():
    """会议总结服务健康检查"""
    return {
        "success": True,
        "message": "会议总结服务运行正常",
        "service": "Meeting Summary API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
