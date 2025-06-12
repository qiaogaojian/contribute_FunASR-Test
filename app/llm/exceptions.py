#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM相关异常定义
"""


class LLMError(Exception):
    """LLM基础异常类"""
    
    def __init__(self, message: str, provider: str = None, model: str = None):
        self.message = message
        self.provider = provider
        self.model = model
        super().__init__(self.message)
    
    def __str__(self):
        parts = [self.message]
        if self.provider:
            parts.append(f"Provider: {self.provider}")
        if self.model:
            parts.append(f"Model: {self.model}")
        return " | ".join(parts)


class LLMProviderError(LLMError):
    """Provider相关错误"""
    pass


class LLMConfigurationError(LLMError):
    """配置错误"""
    pass


class LLMAuthenticationError(LLMError):
    """认证错误"""
    pass


class LLMRateLimitError(LLMError):
    """速率限制错误"""
    
    def __init__(self, message: str, provider: str = None, model: str = None, 
                 retry_after: int = None):
        super().__init__(message, provider, model)
        self.retry_after = retry_after


class LLMModelNotFoundError(LLMError):
    """模型不存在错误"""
    pass


class LLMNetworkError(LLMError):
    """网络错误"""
    pass


class LLMTimeoutError(LLMError):
    """超时错误"""
    pass


class LLMValidationError(LLMError):
    """验证错误"""
    pass
