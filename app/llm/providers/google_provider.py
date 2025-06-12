#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Provider实现
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
from app.llm.constants import GOOGLE_MODELS, DEFAULT_BASE_URLS, ApiProvider


class GoogleProvider(BaseLLMProvider):
    """Google Provider实现"""
    
    def __init__(self, config: LLMProviderConfig):
        """初始化Google Provider"""
        super().__init__(config)
        
        # 设置默认base_url
        if not config.base_url:
            config.base_url = DEFAULT_BASE_URLS[ApiProvider.GOOGLE]
        
        # 创建HTTP客户端
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            params={"key": config.api_key},
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
            endpoint = f"/models/{request.model}:generateContent"
            response = await self.client.post(endpoint, json=request_data)
            
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
            endpoint = f"/models/{request.model}:streamGenerateContent"
            async with self.client.stream(
                "POST", 
                endpoint, 
                json=request_data
            ) as response:
                
                # 处理HTTP错误
                self._handle_http_error(response)
                
                # 处理流式响应 - Google API返回多个JSON对象，用逗号分隔
                full_response = ""

                # 首先收集所有数据
                async for line in response.aiter_lines():
                    if line.strip():
                        full_response += line

                # 解析完整响应
                try:
                    # 尝试作为JSON数组解析
                    if full_response.startswith('[') and full_response.endswith(']'):
                        chunk_list = json.loads(full_response)
                        for chunk_data in chunk_list:
                            chunk = self._parse_streaming_chunk(chunk_data, request.model)
                            if chunk:
                                yield chunk
                    else:
                        # 尝试分割多个JSON对象
                        # 移除外层的方括号（如果存在）
                        clean_response = full_response.strip()
                        if clean_response.startswith('['):
                            clean_response = clean_response[1:]
                        if clean_response.endswith(']'):
                            clean_response = clean_response[:-1]

                        # 分割JSON对象（基于 "},{"模式）
                        json_objects = []
                        current_obj = ""
                        brace_count = 0

                        for char in clean_response:
                            current_obj += char
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    # 完整的JSON对象
                                    try:
                                        obj = json.loads(current_obj.strip())
                                        json_objects.append(obj)
                                        current_obj = ""
                                    except json.JSONDecodeError:
                                        pass
                            elif char == ',' and brace_count == 0:
                                # 对象分隔符
                                current_obj = ""

                        # 处理最后一个对象
                        if current_obj.strip():
                            try:
                                obj = json.loads(current_obj.strip())
                                json_objects.append(obj)
                            except json.JSONDecodeError:
                                pass

                        # 处理所有解析出的对象
                        for chunk_data in json_objects:
                            chunk = self._parse_streaming_chunk(chunk_data, request.model)
                            if chunk:
                                yield chunk

                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse streaming response: {e}")
                    self.logger.error(f"Response data: {full_response[:500]}...")
                    # 如果解析失败，至少尝试提取一些文本
                    pass
                            
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
        return GOOGLE_MODELS.copy()
    
    def validate_config(self) -> bool:
        """验证配置"""
        if not self.config.api_key:
            raise LLMConfigurationError(
                "Google API key is required",
                provider=self.get_provider_name()
            )
        
        if not self.config.base_url:
            raise LLMConfigurationError(
                "Base URL is required",
                provider=self.get_provider_name()
            )
        
        return True
    
    def _build_request_data(self, request: LLMRequest, stream: bool = False) -> Dict[str, Any]:
        """构建请求数据"""
        # 转换消息格式
        contents = []
        for msg in request.messages:
            if msg.role == MessageRole.SYSTEM:
                # Google API将system消息作为第一个user消息
                contents.append({
                    "role": "user",
                    "parts": [{"text": f"System: {msg.content}"}]
                })
            else:
                role = "model" if msg.role == MessageRole.ASSISTANT else "user"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg.content}]
                })
        
        data = {
            "contents": contents
        }
        
        # 添加生成配置
        generation_config = {}
        if request.max_tokens is not None:
            generation_config["maxOutputTokens"] = request.max_tokens
        if request.temperature is not None:
            generation_config["temperature"] = request.temperature
        if request.top_p is not None:
            generation_config["topP"] = request.top_p
        if request.stop is not None:
            generation_config["stopSequences"] = request.stop if isinstance(request.stop, list) else [request.stop]
        
        if generation_config:
            data["generationConfig"] = generation_config
        
        # 添加额外参数
        if request.extra_params:
            data.update(request.extra_params)
        
        return data
    
    def _parse_response(self, response_data: Dict[str, Any], model: str) -> LLMResponse:
        """解析响应数据"""
        content = ""
        if response_data.get("candidates"):
            candidate = response_data["candidates"][0]
            if candidate.get("content", {}).get("parts"):
                for part in candidate["content"]["parts"]:
                    content += part.get("text", "")

        # 转换Google API的usage格式为标准格式
        usage = None
        if response_data.get("usageMetadata"):
            usage_data = response_data["usageMetadata"]
            usage = {
                "prompt_tokens": usage_data.get("promptTokenCount", 0),
                "completion_tokens": usage_data.get("candidatesTokenCount", 0),
                "total_tokens": usage_data.get("totalTokenCount", 0)
            }

        return LLMResponse(
            content=content,
            model=model,
            usage=usage,
            finish_reason=response_data.get("candidates", [{}])[0].get("finishReason"),
            extra_data={"raw_response": response_data}
        )
    
    def _parse_streaming_chunk(
        self,
        chunk_data: Dict[str, Any],
        model: str
    ) -> Optional[LLMResponseStreaming]:
        """解析流式响应块"""
        content = ""
        if chunk_data.get("candidates"):
            candidate = chunk_data["candidates"][0]
            if candidate.get("content", {}).get("parts"):
                for part in candidate["content"]["parts"]:
                    content += part.get("text", "")

        # 转换Google API的usage格式为标准格式
        usage = None
        if chunk_data.get("usageMetadata"):
            usage_data = chunk_data["usageMetadata"]
            usage = {
                "prompt_tokens": usage_data.get("promptTokenCount", 0),
                "completion_tokens": usage_data.get("candidatesTokenCount", 0),
                "total_tokens": usage_data.get("totalTokenCount", 0)
            }

        if content or chunk_data.get("candidates", [{}])[0].get("finishReason"):
            return LLMResponseStreaming(
                delta=content,
                model=model,
                finish_reason=chunk_data.get("candidates", [{}])[0].get("finishReason"),
                usage=usage,
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
