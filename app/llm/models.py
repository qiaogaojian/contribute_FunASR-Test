#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM数据模型和类型定义
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Union, AsyncIterable
from pydantic import BaseModel, Field


class ApiProvider(str, Enum):
    """支持的API Provider枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROQ = "groq"
    OLLAMA = "ollama"
    DEEPSEEK = "deepseek"
    OPENROUTER = "openrouter"
    SILICONFLOW = "siliconflow"
    ALIBABA_QWEN = "alibaba_qwen"
    GROK = "grok"
    OPENAI_COMPATIBLE = "openai_compatible"


class MessageRole(str, Enum):
    """消息角色枚举"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: MessageRole = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")
    name: Optional[str] = Field(None, description="消息发送者名称")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="工具调用")
    tool_call_id: Optional[str] = Field(None, description="工具调用ID")


class ModelInfo(BaseModel):
    """模型信息"""
    max_tokens: Optional[int] = Field(None, description="最大输出token数")
    context_window: Optional[int] = Field(None, description="上下文窗口大小")
    supports_images: bool = Field(False, description="是否支持图像")
    supports_computer_use: bool = Field(False, description="是否支持计算机使用")
    supports_prompt_cache: bool = Field(False, description="是否支持提示缓存")
    input_price: Optional[float] = Field(None, description="输入价格(USD/百万token)")
    output_price: Optional[float] = Field(None, description="输出价格(USD/百万token)")
    cache_writes_price: Optional[float] = Field(None, description="缓存写入价格")
    cache_reads_price: Optional[float] = Field(None, description="缓存读取价格")
    description: Optional[str] = Field(None, description="模型描述")
    reasoning_effort: Optional[str] = Field(None, description="推理能力级别")
    thinking: bool = Field(False, description="是否支持思考模式")


class LLMRequest(BaseModel):
    """LLM请求模型"""
    messages: List[ChatMessage] = Field(..., description="消息列表")
    model: str = Field(..., description="模型名称")
    max_tokens: Optional[int] = Field(None, description="最大生成token数")
    temperature: Optional[float] = Field(None, description="温度参数")
    top_p: Optional[float] = Field(None, description="Top-p参数")
    frequency_penalty: Optional[float] = Field(None, description="频率惩罚")
    presence_penalty: Optional[float] = Field(None, description="存在惩罚")
    stop: Optional[Union[str, List[str]]] = Field(None, description="停止词")
    stream: bool = Field(False, description="是否流式输出")
    tools: Optional[List[Dict[str, Any]]] = Field(None, description="可用工具")
    tool_choice: Optional[Union[str, Dict[str, Any]]] = Field(None, description="工具选择")
    extra_params: Optional[Dict[str, Any]] = Field(None, description="额外参数")


class LLMResponse(BaseModel):
    """LLM响应模型"""
    content: str = Field(..., description="响应内容")
    model: str = Field(..., description="使用的模型")
    usage: Optional[Dict[str, int]] = Field(None, description="token使用情况")
    finish_reason: Optional[str] = Field(None, description="完成原因")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="工具调用")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="额外数据")


class LLMResponseStreaming(BaseModel):
    """LLM流式响应模型"""
    delta: str = Field("", description="增量内容")
    model: str = Field(..., description="使用的模型")
    finish_reason: Optional[str] = Field(None, description="完成原因")
    usage: Optional[Dict[str, int]] = Field(None, description="token使用情况")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="工具调用")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="额外数据")


class LLMProviderConfig(BaseModel):
    """LLM Provider配置"""
    provider: ApiProvider = Field(..., description="Provider类型")
    api_key: Optional[str] = Field(None, description="API密钥")
    base_url: Optional[str] = Field(None, description="基础URL")
    model: Optional[str] = Field(None, description="默认模型")
    timeout: int = Field(30, description="请求超时时间(秒)")
    max_retries: int = Field(3, description="最大重试次数")
    extra_config: Optional[Dict[str, Any]] = Field(None, description="额外配置")
