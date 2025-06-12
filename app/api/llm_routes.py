#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM API路由
提供LLM相关的REST API接口
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import json
import asyncio

from app.llm import (
    LLMManager,
    LLMRequest,
    LLMResponse,
    LLMProviderConfig,
    ChatMessage,
    MessageRole,
    ApiProvider
)
from app.llm.exceptions import LLMError
from app.core.config import get_settings
from app.models.schemas import BaseResponse


# 创建路由器
router = APIRouter(prefix="/llm", tags=["LLM"])

# 全局LLM管理器实例
_llm_manager: Optional[LLMManager] = None


async def get_llm_manager() -> LLMManager:
    """获取LLM管理器实例（依赖注入）"""
    global _llm_manager
    
    if _llm_manager is None:
        _llm_manager = LLMManager()
        
        # 根据配置初始化Provider
        settings = get_settings()
        await _initialize_providers(_llm_manager, settings)
    
    return _llm_manager


async def _initialize_providers(manager: LLMManager, settings):
    """初始化LLM Providers"""
    try:
        # OpenAI Provider
        if settings.openai_api_key:
            openai_config = LLMProviderConfig(
                provider=ApiProvider.OPENAI,
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                timeout=settings.llm_timeout,
                max_retries=settings.llm_max_retries
            )
            manager.register_provider(ApiProvider.OPENAI, openai_config)
        
        # Anthropic Provider
        if settings.anthropic_api_key:
            anthropic_config = LLMProviderConfig(
                provider=ApiProvider.ANTHROPIC,
                api_key=settings.anthropic_api_key,
                timeout=settings.llm_timeout,
                max_retries=settings.llm_max_retries
            )
            manager.register_provider(ApiProvider.ANTHROPIC, anthropic_config)
        
        # Google Provider
        if settings.google_api_key:
            google_config = LLMProviderConfig(
                provider=ApiProvider.GOOGLE,
                api_key=settings.google_api_key,
                timeout=settings.llm_timeout,
                max_retries=settings.llm_max_retries
            )
            manager.register_provider(ApiProvider.GOOGLE, google_config)
        
        # Ollama Provider
        if settings.ollama_base_url:
            ollama_config = LLMProviderConfig(
                provider=ApiProvider.OLLAMA,
                base_url=settings.ollama_base_url,
                timeout=settings.llm_timeout,
                max_retries=settings.llm_max_retries
            )
            manager.register_provider(ApiProvider.OLLAMA, ollama_config)
        
    except Exception as e:
        print(f"Warning: Failed to initialize some LLM providers: {e}")


# API数据模型
class ChatRequest(BaseResponse):
    """聊天请求模型"""
    model: str
    messages: List[Dict[str, str]]
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: bool = False
    provider: Optional[str] = None


class ChatResponse(BaseResponse):
    """聊天响应模型"""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None


class ModelListResponse(BaseResponse):
    """模型列表响应"""
    models: List[Dict[str, Any]]


class ProviderListResponse(BaseResponse):
    """Provider列表响应"""
    providers: List[str]


@router.get("/models", response_model=ModelListResponse)
async def list_models(manager: LLMManager = Depends(get_llm_manager)):
    """列出所有可用模型"""
    try:
        models = manager.list_available_models()
        
        model_list = []
        for name, info in models.items():
            model_list.append({
                "name": name,
                "max_tokens": info.max_tokens,
                "context_window": info.context_window,
                "supports_images": info.supports_images,
                "supports_tools": info.supports_computer_use,
                "input_price": info.input_price,
                "output_price": info.output_price,
                "description": info.description
            })
        
        return ModelListResponse(
            success=True,
            message="Models retrieved successfully",
            models=model_list
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers", response_model=ProviderListResponse)
async def list_providers(manager: LLMManager = Depends(get_llm_manager)):
    """列出所有已注册的Provider"""
    try:
        providers = manager.list_providers()
        provider_names = [provider.value for provider in providers.keys()]
        
        return ProviderListResponse(
            success=True,
            message="Providers retrieved successfully",
            providers=provider_names
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    manager: LLMManager = Depends(get_llm_manager)
):
    """聊天接口（非流式）"""
    try:
        # 转换消息格式
        messages = []
        for msg in request.messages:
            role = MessageRole(msg["role"])
            content = msg["content"]
            messages.append(ChatMessage(role=role, content=content))
        
        # 创建LLM请求
        llm_request = LLMRequest(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=False
        )
        
        # 指定Provider（如果提供）
        provider_type = None
        if request.provider:
            try:
                provider_type = ApiProvider(request.provider)
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid provider: {request.provider}"
                )
        
        # 生成响应
        response = await manager.generate_response(llm_request, provider_type)
        
        return ChatResponse(
            success=True,
            message="Chat response generated successfully",
            content=response.content,
            model=response.model,
            usage=response.usage,
            finish_reason=response.finish_reason
        )
    
    except LLMError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    manager: LLMManager = Depends(get_llm_manager)
):
    """聊天接口（流式）"""
    try:
        # 转换消息格式
        messages = []
        for msg in request.messages:
            role = MessageRole(msg["role"])
            content = msg["content"]
            messages.append(ChatMessage(role=role, content=content))
        
        # 创建LLM请求
        llm_request = LLMRequest(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True
        )
        
        # 指定Provider（如果提供）
        provider_type = None
        if request.provider:
            try:
                provider_type = ApiProvider(request.provider)
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid provider: {request.provider}"
                )
        
        # 流式响应生成器
        async def generate_stream():
            try:
                async for chunk in manager.stream_response(llm_request, provider_type):
                    # 构建SSE格式的数据
                    chunk_data = {
                        "delta": chunk.delta,
                        "model": chunk.model,
                        "finish_reason": chunk.finish_reason,
                        "usage": chunk.usage
                    }
                    
                    yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
                    
                    # 如果完成，发送结束标记
                    if chunk.finish_reason:
                        yield "data: [DONE]\n\n"
                        break
                        
            except LLMError as e:
                error_data = {"error": str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"
            except Exception as e:
                error_data = {"error": f"Internal error: {str(e)}"}
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
    
    except LLMError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check(manager: LLMManager = Depends(get_llm_manager)):
    """健康检查"""
    try:
        providers = manager.list_providers()
        return {
            "success": True,
            "message": "LLM service is healthy",
            "providers_count": len(providers),
            "available_providers": [p.value for p in providers.keys()]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
