#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM Manager - 中央协调器
统一管理所有LLM Provider
"""

import logging
from typing import Dict, Optional, AsyncIterable, Type
from contextlib import asynccontextmanager

from app.llm.base import BaseLLMProvider
from app.llm.models import (
    ApiProvider,
    LLMRequest,
    LLMResponse,
    LLMResponseStreaming,
    LLMProviderConfig,
    ModelInfo
)
from app.llm.exceptions import (
    LLMError,
    LLMConfigurationError,
    LLMProviderError,
    LLMModelNotFoundError
)
from app.llm.constants import DEFAULT_BASE_URLS, ALL_MODELS


logger = logging.getLogger(__name__)


class LLMManager:
    """LLM管理器 - 统一管理所有LLM Provider"""
    
    def __init__(self):
        """初始化LLM管理器"""
        self.providers: Dict[ApiProvider, BaseLLMProvider] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_provider(
        self, 
        provider_type: ApiProvider, 
        config: LLMProviderConfig
    ) -> None:
        """
        注册LLM Provider
        
        Args:
            provider_type: Provider类型
            config: Provider配置
            
        Raises:
            LLMConfigurationError: 配置错误
        """
        try:
            # 动态导入对应的Provider类
            provider_class = self._get_provider_class(provider_type)
            
            # 创建Provider实例
            provider = provider_class(config)
            
            # 验证配置
            if not provider.validate_config():
                raise LLMConfigurationError(
                    f"Invalid configuration for provider {provider_type.value}",
                    provider=provider_type.value
                )
            
            # 注册Provider
            self.providers[provider_type] = provider
            self.logger.info(f"Registered provider: {provider_type.value}")
            
        except Exception as e:
            raise LLMConfigurationError(
                f"Failed to register provider {provider_type.value}: {str(e)}",
                provider=provider_type.value
            )
    
    def unregister_provider(self, provider_type: ApiProvider) -> None:
        """
        注销LLM Provider
        
        Args:
            provider_type: Provider类型
        """
        if provider_type in self.providers:
            del self.providers[provider_type]
            self.logger.info(f"Unregistered provider: {provider_type.value}")
    
    def get_provider(self, provider_type: ApiProvider) -> Optional[BaseLLMProvider]:
        """
        获取指定的Provider
        
        Args:
            provider_type: Provider类型
            
        Returns:
            Provider实例，如果不存在则返回None
        """
        return self.providers.get(provider_type)
    
    def list_providers(self) -> Dict[ApiProvider, BaseLLMProvider]:
        """
        列出所有已注册的Provider
        
        Returns:
            Provider字典
        """
        return self.providers.copy()
    
    async def generate_response(
        self,
        request: LLMRequest,
        provider_type: Optional[ApiProvider] = None,
        **kwargs
    ) -> LLMResponse:
        """
        生成非流式响应
        
        Args:
            request: LLM请求
            provider_type: 指定的Provider类型，如果为None则自动选择
            **kwargs: 额外参数
            
        Returns:
            LLM响应
            
        Raises:
            LLMError: 各种LLM相关错误
        """
        provider = self._select_provider(request.model, provider_type)
        
        try:
            return await provider.generate_response(request, **kwargs)
        except Exception as e:
            raise provider._handle_error(e, "Failed to generate response")
    
    async def stream_response(
        self,
        request: LLMRequest,
        provider_type: Optional[ApiProvider] = None,
        **kwargs
    ) -> AsyncIterable[LLMResponseStreaming]:
        """
        生成流式响应
        
        Args:
            request: LLM请求
            provider_type: 指定的Provider类型，如果为None则自动选择
            **kwargs: 额外参数
            
        Yields:
            流式LLM响应
            
        Raises:
            LLMError: 各种LLM相关错误
        """
        provider = self._select_provider(request.model, provider_type)
        
        if not provider.supports_streaming():
            raise LLMProviderError(
                f"Provider {provider.get_provider_name()} does not support streaming",
                provider=provider.get_provider_name()
            )
        
        try:
            async for chunk in provider.stream_response(request, **kwargs):
                yield chunk
        except Exception as e:
            raise provider._handle_error(e, "Failed to stream response")
    
    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """
        获取模型信息
        
        Args:
            model_name: 模型名称
            
        Returns:
            模型信息，如果模型不存在则返回None
        """
        # 首先从常量中查找
        if model_name in ALL_MODELS:
            return ALL_MODELS[model_name]
        
        # 然后从已注册的Provider中查找
        for provider in self.providers.values():
            model_info = provider.get_model_info(model_name)
            if model_info:
                return model_info
        
        return None
    
    def list_available_models(self) -> Dict[str, ModelInfo]:
        """
        列出所有可用模型
        
        Returns:
            模型名称到模型信息的映射
        """
        all_models = ALL_MODELS.copy()
        
        # 添加各Provider的模型
        for provider in self.providers.values():
            provider_models = provider.get_available_models()
            all_models.update(provider_models)
        
        return all_models
    
    def _select_provider(
        self, 
        model_name: str, 
        provider_type: Optional[ApiProvider] = None
    ) -> BaseLLMProvider:
        """
        选择合适的Provider
        
        Args:
            model_name: 模型名称
            provider_type: 指定的Provider类型
            
        Returns:
            选中的Provider
            
        Raises:
            LLMProviderError: Provider相关错误
            LLMModelNotFoundError: 模型不存在错误
        """
        if provider_type:
            # 使用指定的Provider
            provider = self.providers.get(provider_type)
            if not provider:
                raise LLMProviderError(
                    f"Provider {provider_type.value} is not registered",
                    provider=provider_type.value
                )
            return provider
        
        # 自动选择Provider
        for provider in self.providers.values():
            if provider.get_model_info(model_name):
                return provider
        
        # 如果没有找到，抛出错误
        raise LLMModelNotFoundError(
            f"Model {model_name} is not available in any registered provider",
            model=model_name
        )
    
    def _get_provider_class(self, provider_type: ApiProvider) -> Type[BaseLLMProvider]:
        """
        获取Provider类
        
        Args:
            provider_type: Provider类型
            
        Returns:
            Provider类
            
        Raises:
            LLMConfigurationError: 配置错误
        """
        # 这里使用延迟导入避免循环依赖
        try:
            if provider_type == ApiProvider.OPENAI:
                from .providers.openai_provider import OpenAIProvider
                return OpenAIProvider
            elif provider_type == ApiProvider.ANTHROPIC:
                from .providers.anthropic_provider import AnthropicProvider
                return AnthropicProvider
            elif provider_type == ApiProvider.GOOGLE:
                from .providers.google_provider import GoogleProvider
                return GoogleProvider
            elif provider_type == ApiProvider.OLLAMA:
                from .providers.ollama_provider import OllamaProvider
                return OllamaProvider
            elif provider_type in [
                ApiProvider.DEEPSEEK,
                ApiProvider.OPENROUTER,
                ApiProvider.SILICONFLOW,
                ApiProvider.ALIBABA_QWEN,
                ApiProvider.GROK,
                ApiProvider.OPENAI_COMPATIBLE
            ]:
                from .providers.openai_compatible import OpenAICompatibleProvider
                return OpenAICompatibleProvider
            else:
                raise LLMConfigurationError(
                    f"Unsupported provider type: {provider_type.value}",
                    provider=provider_type.value
                )
        except ImportError as e:
            raise LLMConfigurationError(
                f"Failed to import provider class for {provider_type.value}: {str(e)}",
                provider=provider_type.value
            )
    
    @asynccontextmanager
    async def provider_context(self, provider_type: ApiProvider):
        """
        Provider上下文管理器
        
        Args:
            provider_type: Provider类型
            
        Yields:
            Provider实例
        """
        provider = self.get_provider(provider_type)
        if not provider:
            raise LLMProviderError(
                f"Provider {provider_type.value} is not registered",
                provider=provider_type.value
            )
        
        async with provider:
            yield provider
