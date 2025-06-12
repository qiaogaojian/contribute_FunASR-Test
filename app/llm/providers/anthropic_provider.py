#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anthropic Provider实现
"""

from typing import Dict, AsyncIterable, Optional, Any
import httpx
import json

from app.llm.base import BaseLLMProvider
from app.llm.models import (
    LLMRequest,
    LLMResponse,
    LLMResponseStreaming,
    LLMProviderConfig,
    ModelInfo,
    ChatMessage,
    MessageRole
)
from app.llm.exceptions import (
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMModelNotFoundError,
    LLMNetworkError,
    LLMValidationError,
    LLMConfigurationError
)
from app.llm.constants import ANTHROPIC_MODELS, DEFAULT_BASE_URLS, ApiProvider


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Provider实现"""
    
    def __init__(self, config: LLMProviderConfig):
        """初始化Anthropic Provider"""
        super().__init__(config)
        
        # 设置默认base_url
        if not config.base_url:
            config.base_url = DEFAULT_BASE_URLS[ApiProvider.ANTHROPIC]
        
        # 创建HTTP客户端
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers={
                "x-api-key": config.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
        )
    
    async def generate_response(
        self, 
        request: LLMRequest,
        **kwargs
    ) -> LLMResponse:
        """生成非流式响应"""
        try:
            # 构建请求数据
            request_data = self._build_request_data(request, stream=False)
            
            # 发送请求
            response = await self.client.post("/v1/messages", json=request_data)
            
            # 处理响应
            self._handle_http_error(response)
            response_data = response.json()
            
            # 解析响应
            return self._parse_response(response_data, request.model)
            
        except httpx.RequestError as e:
            raise LLMNetworkError(
                f"Network error: {str(e)}",
                provider=self.get_provider_name(),
                model=request.model
            )
        except Exception as e:
            raise self._handle_error(e, "Failed to generate response")
    
    async def stream_response(
        self, 
        request: LLMRequest,
        **kwargs
    ) -> AsyncIterable[LLMResponseStreaming]:
        """生成流式响应"""
        try:
            # 构建请求数据
            request_data = self._build_request_data(request, stream=True)
            
            # 发送流式请求
            async with self.client.stream(
                "POST", 
                "/v1/messages", 
                json=request_data
            ) as response:
                
                # 处理HTTP错误
                self._handle_http_error(response)
                
                # 处理流式响应
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # 移除 "data: " 前缀
                        
                        if data.strip() == "[DONE]":
                            break
                        
                        try:
                            chunk_data = json.loads(data)
                            chunk = self._parse_streaming_chunk(chunk_data, request.model)
                            if chunk:
                                yield chunk
                        except json.JSONDecodeError:
                            continue
                            
        except httpx.RequestError as e:
            raise LLMNetworkError(
                f"Network error: {str(e)}",
                provider=self.get_provider_name(),
                model=request.model
            )
        except Exception as e:
            raise self._handle_error(e, "Failed to stream response")
    
    def get_available_models(self) -> Dict[str, ModelInfo]:
        """获取可用模型列表"""
        return ANTHROPIC_MODELS.copy()
    
    def validate_config(self) -> bool:
        """验证配置"""
        if not self.config.api_key:
            raise LLMConfigurationError(
                "Anthropic API key is required",
                provider=self.get_provider_name()
            )
        
        if not self.config.base_url:
            raise LLMConfigurationError(
                "Base URL is required",
                provider=self.get_provider_name()
            )
        
        return True
    
    def supports_tools(self) -> bool:
        """是否支持工具调用"""
        return True
    
    def _build_request_data(self, request: LLMRequest, stream: bool = False) -> Dict[str, Any]:
        """构建请求数据"""
        # 分离system消息和其他消息
        system_message = None
        messages = []
        
        for msg in request.messages:
            if msg.role == MessageRole.SYSTEM:
                system_message = msg.content
            else:
                messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
        data = {
            "model": request.model,
            "messages": messages,
            "stream": stream
        }
        
        # 添加system消息
        if system_message:
            data["system"] = system_message
        
        # 添加可选参数
        if request.max_tokens is not None:
            data["max_tokens"] = request.max_tokens
        if request.temperature is not None:
            data["temperature"] = request.temperature
        if request.top_p is not None:
            data["top_p"] = request.top_p
        if request.stop is not None:
            data["stop_sequences"] = request.stop if isinstance(request.stop, list) else [request.stop]
        if request.tools is not None:
            data["tools"] = request.tools
        
        # 添加额外参数
        if request.extra_params:
            data.update(request.extra_params)
        
        return data
    
    def _parse_response(self, response_data: Dict[str, Any], model: str) -> LLMResponse:
        """解析响应数据"""
        content = ""
        if response_data.get("content"):
            for item in response_data["content"]:
                if item.get("type") == "text":
                    content += item.get("text", "")
        
        return LLMResponse(
            content=content,
            model=model,
            usage=response_data.get("usage"),
            finish_reason=response_data.get("stop_reason"),
            extra_data={"raw_response": response_data}
        )
    
    def _parse_streaming_chunk(
        self, 
        chunk_data: Dict[str, Any], 
        model: str
    ) -> Optional[LLMResponseStreaming]:
        """解析流式响应块"""
        if chunk_data.get("type") == "content_block_delta":
            delta = chunk_data.get("delta", {})
            return LLMResponseStreaming(
                delta=delta.get("text", ""),
                model=model,
                extra_data={"raw_chunk": chunk_data}
            )
        elif chunk_data.get("type") == "message_stop":
            return LLMResponseStreaming(
                delta="",
                model=model,
                finish_reason="stop",
                usage=chunk_data.get("usage"),
                extra_data={"raw_chunk": chunk_data}
            )
        
        return None
    
    def _handle_http_error(self, response: httpx.Response) -> None:
        """处理HTTP错误"""
        if response.status_code == 401:
            raise LLMAuthenticationError(
                "Invalid API key",
                provider=self.get_provider_name()
            )
        elif response.status_code == 429:
            raise LLMRateLimitError(
                "Rate limit exceeded",
                provider=self.get_provider_name()
            )
        elif response.status_code == 404:
            raise LLMModelNotFoundError(
                "Model not found",
                provider=self.get_provider_name()
            )
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", "Unknown error")
            except:
                error_message = f"HTTP {response.status_code}: {response.text}"
            
            raise LLMValidationError(
                error_message,
                provider=self.get_provider_name()
            )
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """清理资源"""
        await self.client.aclose()
