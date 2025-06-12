#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM Provider基础接口定义
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, AsyncIterable
import logging

from app.llm.models import (
    LLMRequest, 
    LLMResponse, 
    LLMResponseStreaming,
    LLMProviderConfig,
    ModelInfo
)
from app.llm.exceptions import LLMError


logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """LLM Provider基础抽象类"""
    
    def __init__(self, config: LLMProviderConfig):
        """
        初始化Provider
        
        Args:
            config: Provider配置
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def generate_response(
        self, 
        request: LLMRequest,
        **kwargs
    ) -> LLMResponse:
        """
        生成非流式响应
        
        Args:
            request: LLM请求
            **kwargs: 额外参数
            
        Returns:
            LLM响应
            
        Raises:
            LLMError: 各种LLM相关错误
        """
        pass
    
    @abstractmethod
    async def stream_response(
        self, 
        request: LLMRequest,
        **kwargs
    ) -> AsyncIterable[LLMResponseStreaming]:
        """
        生成流式响应
        
        Args:
            request: LLM请求
            **kwargs: 额外参数
            
        Yields:
            流式LLM响应
            
        Raises:
            LLMError: 各种LLM相关错误
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> Dict[str, ModelInfo]:
        """
        获取可用模型列表
        
        Returns:
            模型名称到模型信息的映射
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        验证配置是否有效
        
        Returns:
            配置是否有效
            
        Raises:
            LLMConfigurationError: 配置错误
        """
        pass
    
    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """
        获取特定模型信息
        
        Args:
            model_name: 模型名称
            
        Returns:
            模型信息，如果模型不存在则返回None
        """
        models = self.get_available_models()
        return models.get(model_name)
    
    def supports_streaming(self) -> bool:
        """
        是否支持流式输出
        
        Returns:
            是否支持流式输出
        """
        return True
    
    def supports_tools(self) -> bool:
        """
        是否支持工具调用
        
        Returns:
            是否支持工具调用
        """
        return False
    
    def get_provider_name(self) -> str:
        """
        获取Provider名称
        
        Returns:
            Provider名称
        """
        return self.config.provider.value
    
    def _handle_error(self, error: Exception, context: str = "") -> LLMError:
        """
        处理和转换错误
        
        Args:
            error: 原始错误
            context: 错误上下文
            
        Returns:
            转换后的LLM错误
        """
        provider_name = self.get_provider_name()
        
        if isinstance(error, LLMError):
            return error
        
        # 根据错误类型进行转换
        error_message = f"{context}: {str(error)}" if context else str(error)
        
        # 这里可以根据不同的错误类型进行更精细的处理
        from .exceptions import LLMProviderError
        return LLMProviderError(
            message=error_message,
            provider=provider_name
        )
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        pass
