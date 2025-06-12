#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama Provider实现
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
    LLMNetworkError,
    LLMValidationError,
    LLMConfigurationError,
    LLMModelNotFoundError
)
from app.llm.constants import DEFAULT_BASE_URLS, ApiProvider


class OllamaProvider(BaseLLMProvider):
    """Ollama Provider实现"""
    
    def __init__(self, config: LLMProviderConfig):
        """初始化Ollama Provider"""
        super().__init__(config)
        
        # 设置默认base_url
        if not config.base_url:
            config.base_url = DEFAULT_BASE_URLS[ApiProvider.OLLAMA]
        
        # 创建HTTP客户端
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers={"Content-Type": "application/json"}
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
            response = await self.client.post("/api/chat", json=request_data)
            
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
                "/api/chat", 
                json=request_data
            ) as response:
                
                # 处理HTTP错误
                self._handle_http_error(response)
                
                # 处理流式响应
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            chunk_data = json.loads(line)
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
        # Ollama的模型是动态的，这里返回一些常见模型
        return {
            "llama3.2": ModelInfo(
                max_tokens=4096,
                context_window=8192,
                supports_images=False,
                supports_prompt_cache=False,
                description="Llama 3.2 model"
            ),
            "llama3.1": ModelInfo(
                max_tokens=4096,
                context_window=131072,
                supports_images=False,
                supports_prompt_cache=False,
                description="Llama 3.1 model"
            ),
            "qwen2.5": ModelInfo(
                max_tokens=4096,
                context_window=32768,
                supports_images=False,
                supports_prompt_cache=False,
                description="Qwen 2.5 model"
            ),
            "mistral": ModelInfo(
                max_tokens=4096,
                context_window=8192,
                supports_images=False,
                supports_prompt_cache=False,
                description="Mistral model"
            ),
        }
    
    def validate_config(self) -> bool:
        """验证配置"""
        if not self.config.base_url:
            raise LLMConfigurationError(
                "Base URL is required for Ollama",
                provider=self.get_provider_name()
            )
        
        return True
    
    def _build_request_data(self, request: LLMRequest, stream: bool = False) -> Dict[str, Any]:
        """构建请求数据"""
        # 转换消息格式
        messages = []
        for msg in request.messages:
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        data = {
            "model": request.model,
            "messages": messages,
            "stream": stream
        }
        
        # 添加可选参数
        options = {}
        if request.temperature is not None:
            options["temperature"] = request.temperature
        if request.top_p is not None:
            options["top_p"] = request.top_p
        if request.max_tokens is not None:
            options["num_predict"] = request.max_tokens
        if request.stop is not None:
            options["stop"] = request.stop if isinstance(request.stop, list) else [request.stop]
        
        if options:
            data["options"] = options
        
        # 添加额外参数
        if request.extra_params:
            data.update(request.extra_params)
        
        return data
    
    def _parse_response(self, response_data: Dict[str, Any], model: str) -> LLMResponse:
        """解析响应数据"""
        message = response_data.get("message", {})
        content = message.get("content", "")
        
        return LLMResponse(
            content=content,
            model=model,
            finish_reason="stop" if response_data.get("done") else None,
            extra_data={"raw_response": response_data}
        )
    
    def _parse_streaming_chunk(
        self, 
        chunk_data: Dict[str, Any], 
        model: str
    ) -> Optional[LLMResponseStreaming]:
        """解析流式响应块"""
        message = chunk_data.get("message", {})
        content = message.get("content", "")
        
        return LLMResponseStreaming(
            delta=content,
            model=model,
            finish_reason="stop" if chunk_data.get("done") else None,
            extra_data={"raw_chunk": chunk_data}
        )
    
    def _handle_http_error(self, response: httpx.Response) -> None:
        """处理HTTP错误"""
        if response.status_code == 404:
            raise LLMModelNotFoundError(
                "Model not found or not pulled",
                provider=self.get_provider_name()
            )
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                error_message = error_data.get("error", "Unknown error")
            except:
                error_message = f"HTTP {response.status_code}: {response.text}"
            
            raise LLMValidationError(
                error_message,
                provider=self.get_provider_name()
            )
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """清理资源"""
        await self.client.aclose()
