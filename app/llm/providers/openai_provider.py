#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI Provider实现
"""

import json
from typing import Dict, AsyncIterable, Optional, Any
import httpx

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
from app.llm.constants import OPENAI_MODELS, DEFAULT_BASE_URLS, ApiProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider实现"""
    
    def __init__(self, config: LLMProviderConfig):
        """初始化OpenAI Provider"""
        super().__init__(config)
        
        # 设置默认base_url
        if not config.base_url:
            config.base_url = DEFAULT_BASE_URLS[ApiProvider.OPENAI]
        
        # 创建HTTP客户端
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
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
            response = await self.client.post("/chat/completions", json=request_data)
            
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
                "/chat/completions", 
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
        return OPENAI_MODELS.copy()
    
    def validate_config(self) -> bool:
        """验证配置"""
        if not self.config.api_key:
            raise LLMConfigurationError(
                "OpenAI API key is required",
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
        data = {
            "model": request.model,
            "messages": [self._convert_message(msg) for msg in request.messages],
            "stream": stream
        }
        
        # 添加可选参数
        if request.max_tokens is not None:
            data["max_tokens"] = request.max_tokens
        if request.temperature is not None:
            data["temperature"] = request.temperature
        if request.top_p is not None:
            data["top_p"] = request.top_p
        if request.frequency_penalty is not None:
            data["frequency_penalty"] = request.frequency_penalty
        if request.presence_penalty is not None:
            data["presence_penalty"] = request.presence_penalty
        if request.stop is not None:
            data["stop"] = request.stop
        if request.tools is not None:
            data["tools"] = request.tools
        if request.tool_choice is not None:
            data["tool_choice"] = request.tool_choice
        
        # 添加额外参数
        if request.extra_params:
            data.update(request.extra_params)
        
        return data
    
    def _convert_message(self, message: ChatMessage) -> Dict[str, Any]:
        """转换消息格式"""
        msg_data = {
            "role": message.role.value,
            "content": message.content
        }
        
        if message.name:
            msg_data["name"] = message.name
        if message.tool_calls:
            msg_data["tool_calls"] = message.tool_calls
        if message.tool_call_id:
            msg_data["tool_call_id"] = message.tool_call_id
        
        return msg_data
    
    def _parse_response(self, response_data: Dict[str, Any], model: str) -> LLMResponse:
        """解析响应数据"""
        choice = response_data["choices"][0]
        message = choice["message"]
        
        return LLMResponse(
            content=message.get("content", ""),
            model=model,
            usage=response_data.get("usage"),
            finish_reason=choice.get("finish_reason"),
            tool_calls=message.get("tool_calls"),
            extra_data={"raw_response": response_data}
        )
    
    def _parse_streaming_chunk(
        self, 
        chunk_data: Dict[str, Any], 
        model: str
    ) -> Optional[LLMResponseStreaming]:
        """解析流式响应块"""
        if not chunk_data.get("choices"):
            return None
        
        choice = chunk_data["choices"][0]
        delta = choice.get("delta", {})
        
        return LLMResponseStreaming(
            delta=delta.get("content", ""),
            model=model,
            finish_reason=choice.get("finish_reason"),
            usage=chunk_data.get("usage"),
            tool_calls=delta.get("tool_calls"),
            extra_data={"raw_chunk": chunk_data}
        )
    
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
