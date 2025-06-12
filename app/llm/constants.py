#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM相关常量定义
"""

from typing import Dict
from app.llm.models import ModelInfo, ApiProvider

# 默认API端点
DEFAULT_BASE_URLS = {
    ApiProvider.OPENAI: "https://api.openai.com/v1",
    ApiProvider.ANTHROPIC: "https://api.anthropic.com",
    ApiProvider.GOOGLE: "https://generativelanguage.googleapis.com/v1beta",
    ApiProvider.GROQ: "https://api.groq.com/openai/v1",
    ApiProvider.DEEPSEEK: "https://api.deepseek.com",
    ApiProvider.OPENROUTER: "https://openrouter.ai/api/v1",
    ApiProvider.SILICONFLOW: "https://api.siliconflow.cn/v1",
    ApiProvider.ALIBABA_QWEN: "https://dashscope.aliyuncs.com/compatible-mode/v1",
    ApiProvider.GROK: "https://api.x.ai/v1",
    ApiProvider.OLLAMA: "http://localhost:11434",
}

# OpenAI模型信息
OPENAI_MODELS = {
    "gpt-4o": ModelInfo(
        max_tokens=16384,
        context_window=128000,
        supports_images=True,
        supports_prompt_cache=False,
        input_price=2.50,
        output_price=10.00,
        description="Most advanced GPT-4 model with vision capabilities"
    ),
    "gpt-4o-mini": ModelInfo(
        max_tokens=16384,
        context_window=128000,
        supports_images=True,
        supports_prompt_cache=False,
        input_price=0.15,
        output_price=0.60,
        description="Faster and cheaper GPT-4 model"
    ),
    "o1": ModelInfo(
        max_tokens=100000,
        context_window=200000,
        supports_images=True,
        supports_prompt_cache=False,
        input_price=15.00,
        output_price=60.00,
        description="Advanced reasoning model",
        reasoning_effort="high",
        thinking=True
    ),
    "o1-mini": ModelInfo(
        max_tokens=65536,
        context_window=128000,
        supports_images=True,
        supports_prompt_cache=False,
        input_price=1.10,
        output_price=4.40,
        description="Faster reasoning model",
        reasoning_effort="medium",
        thinking=True
    ),
    "gpt-3.5-turbo": ModelInfo(
        max_tokens=4096,
        context_window=16385,
        supports_images=False,
        supports_prompt_cache=False,
        input_price=0.50,
        output_price=1.50,
        description="Fast and efficient model for simple tasks"
    ),
}

# Anthropic模型信息
ANTHROPIC_MODELS = {
    "claude-3-5-sonnet-20241022": ModelInfo(
        max_tokens=8192,
        context_window=200000,
        supports_images=True,
        supports_prompt_cache=True,
        supports_computer_use=True,
        input_price=3.00,
        output_price=15.00,
        cache_writes_price=3.75,
        cache_reads_price=0.30,
        description="Most intelligent Claude model"
    ),
    "claude-3-5-haiku-20241022": ModelInfo(
        max_tokens=8192,
        context_window=200000,
        supports_images=False,
        supports_prompt_cache=True,
        input_price=1.00,
        output_price=5.00,
        cache_writes_price=1.25,
        cache_reads_price=0.10,
        description="Fastest Claude model"
    ),
    "claude-3-opus-20240229": ModelInfo(
        max_tokens=4096,
        context_window=200000,
        supports_images=True,
        supports_prompt_cache=True,
        input_price=15.00,
        output_price=75.00,
        cache_writes_price=18.75,
        cache_reads_price=1.50,
        description="Most powerful Claude model"
    ),
}

# Google模型信息
GOOGLE_MODELS = {
    "gemini-2.0-flash-001": ModelInfo(
        max_tokens=8192,
        context_window=1048576,
        supports_images=True,
        supports_prompt_cache=False,
        input_price=0.10,
        output_price=0.40,
        description="Latest Gemini model with large context"
    ),
    "gemini-1.5-pro": ModelInfo(
        max_tokens=8192,
        context_window=2097152,
        supports_images=True,
        supports_prompt_cache=False,
        input_price=1.25,
        output_price=5.00,
        description="Advanced Gemini model with very large context"
    ),
    "gemini-1.5-flash": ModelInfo(
        max_tokens=8192,
        context_window=1048576,
        supports_images=True,
        supports_prompt_cache=False,
        input_price=0.075,
        output_price=0.30,
        description="Fast Gemini model"
    ),
}

# Groq模型信息
GROQ_MODELS = {
    "llama-3.1-70b-versatile": ModelInfo(
        max_tokens=8192,
        context_window=131072,
        supports_images=False,
        supports_prompt_cache=False,
        input_price=0.59,
        output_price=0.79,
        description="Large Llama model optimized for speed"
    ),
    "llama-3.1-8b-instant": ModelInfo(
        max_tokens=8192,
        context_window=131072,
        supports_images=False,
        supports_prompt_cache=False,
        input_price=0.05,
        output_price=0.08,
        description="Fast Llama model"
    ),
    "mixtral-8x7b-32768": ModelInfo(
        max_tokens=32768,
        context_window=32768,
        supports_images=False,
        supports_prompt_cache=False,
        input_price=0.24,
        output_price=0.24,
        description="Mixtral model with large context"
    ),
}

# 嵌入模型信息
EMBEDDING_MODELS = {
    "text-embedding-3-small": ModelInfo(
        context_window=8191,
        description="OpenAI small embedding model",
        input_price=0.02
    ),
    "text-embedding-3-large": ModelInfo(
        context_window=8191,
        description="OpenAI large embedding model",
        input_price=0.13
    ),
    "text-embedding-004": ModelInfo(
        context_window=2048,
        description="Google embedding model",
        input_price=0.00001
    ),
}

# 所有模型信息汇总
ALL_MODELS = {
    **OPENAI_MODELS,
    **ANTHROPIC_MODELS,
    **GOOGLE_MODELS,
    **GROQ_MODELS,
    **EMBEDDING_MODELS,
}
