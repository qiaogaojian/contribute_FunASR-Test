#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI兼容Provider实现
用于支持OpenAI API兼容的服务，如Deepseek、OpenRouter等
"""

from typing import Dict
from app.llm.models import ModelInfo, ApiProvider
from app.llm.constants import DEFAULT_BASE_URLS
from app.llm.providers.openai_provider import OpenAIProvider


class OpenAICompatibleProvider(OpenAIProvider):
    """OpenAI兼容Provider实现"""
    
    def __init__(self, config):
        """初始化OpenAI兼容Provider"""
        # 根据provider类型设置默认base_url
        if not config.base_url and config.provider in DEFAULT_BASE_URLS:
            config.base_url = DEFAULT_BASE_URLS[config.provider]
        
        super().__init__(config)
    
    def get_available_models(self) -> Dict[str, ModelInfo]:
        """获取可用模型列表"""
        # 根据不同的provider返回不同的模型列表
        if self.config.provider == ApiProvider.DEEPSEEK:
            return self._get_deepseek_models()
        elif self.config.provider == ApiProvider.GROQ:
            return self._get_groq_models()
        elif self.config.provider == ApiProvider.OPENROUTER:
            return self._get_openrouter_models()
        elif self.config.provider == ApiProvider.SILICONFLOW:
            return self._get_siliconflow_models()
        elif self.config.provider == ApiProvider.ALIBABA_QWEN:
            return self._get_qwen_models()
        elif self.config.provider == ApiProvider.GROK:
            return self._get_grok_models()
        else:
            # 通用OpenAI兼容模型
            return self._get_generic_models()
    
    def _get_deepseek_models(self) -> Dict[str, ModelInfo]:
        """获取Deepseek模型"""
        return {
            "deepseek-chat": ModelInfo(
                max_tokens=4096,
                context_window=32768,
                supports_images=False,
                supports_prompt_cache=False,
                input_price=0.14,
                output_price=0.28,
                description="Deepseek Chat model"
            ),
            "deepseek-coder": ModelInfo(
                max_tokens=4096,
                context_window=16384,
                supports_images=False,
                supports_prompt_cache=False,
                input_price=0.14,
                output_price=0.28,
                description="Deepseek Coder model"
            ),
        }
    
    def _get_groq_models(self) -> Dict[str, ModelInfo]:
        """获取Groq模型"""
        return {
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
    
    def _get_openrouter_models(self) -> Dict[str, ModelInfo]:
        """获取OpenRouter模型"""
        return {
            "openai/gpt-4o": ModelInfo(
                max_tokens=16384,
                context_window=128000,
                supports_images=True,
                supports_prompt_cache=False,
                input_price=5.00,
                output_price=15.00,
                description="GPT-4o via OpenRouter"
            ),
            "anthropic/claude-3.5-sonnet": ModelInfo(
                max_tokens=8192,
                context_window=200000,
                supports_images=True,
                supports_prompt_cache=False,
                input_price=3.00,
                output_price=15.00,
                description="Claude 3.5 Sonnet via OpenRouter"
            ),
        }
    
    def _get_siliconflow_models(self) -> Dict[str, ModelInfo]:
        """获取SiliconFlow模型"""
        return {
            "deepseek-ai/DeepSeek-V2.5": ModelInfo(
                max_tokens=8192,
                context_window=32768,
                supports_images=False,
                supports_prompt_cache=False,
                input_price=0.14,
                output_price=0.28,
                description="DeepSeek V2.5 via SiliconFlow"
            ),
            "Qwen/Qwen2.5-72B-Instruct": ModelInfo(
                max_tokens=8192,
                context_window=32768,
                supports_images=False,
                supports_prompt_cache=False,
                input_price=0.56,
                output_price=0.56,
                description="Qwen2.5 72B via SiliconFlow"
            ),
        }
    
    def _get_qwen_models(self) -> Dict[str, ModelInfo]:
        """获取阿里云Qwen模型"""
        return {
            "qwen-turbo": ModelInfo(
                max_tokens=8192,
                context_window=8192,
                supports_images=False,
                supports_prompt_cache=False,
                input_price=0.3,
                output_price=0.6,
                description="Qwen Turbo model"
            ),
            "qwen-plus": ModelInfo(
                max_tokens=8192,
                context_window=32768,
                supports_images=False,
                supports_prompt_cache=False,
                input_price=0.8,
                output_price=2.0,
                description="Qwen Plus model"
            ),
            "qwen-max": ModelInfo(
                max_tokens=8192,
                context_window=8192,
                supports_images=True,
                supports_prompt_cache=False,
                input_price=20.0,
                output_price=60.0,
                description="Qwen Max model with vision"
            ),
        }
    
    def _get_grok_models(self) -> Dict[str, ModelInfo]:
        """获取Grok模型"""
        return {
            "grok-beta": ModelInfo(
                max_tokens=8192,
                context_window=131072,
                supports_images=False,
                supports_prompt_cache=False,
                input_price=5.00,
                output_price=15.00,
                description="Grok Beta model"
            ),
        }
    
    def _get_generic_models(self) -> Dict[str, ModelInfo]:
        """获取通用模型"""
        return {
            "default": ModelInfo(
                max_tokens=4096,
                context_window=8192,
                supports_images=False,
                supports_prompt_cache=False,
                description="Generic OpenAI-compatible model"
            ),
        }
