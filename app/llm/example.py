#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM Provider使用示例
"""

import asyncio
import logging
from typing import List

import sys
import os

from app.llm.manager import LLMManager
from app.llm.models import (
    ApiProvider,
    LLMRequest,
    LLMProviderConfig,
    ChatMessage,
    MessageRole
)
from app.core.config import get_settings


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_google():
    """Google Provider使用示例"""
    settings = get_settings()

    # 调试信息
    logger.info(f"Google API Key from settings: {settings.google_api_key}")

    # 检查API密钥
    if not settings.google_api_key or settings.google_api_key == "your-google-key":
        logger.error("Google API密钥未设置或使用了占位符。请在.env文件中设置ASR_GOOGLE_API_KEY")
        return

    # 创建LLM管理器
    manager = LLMManager()

    # 配置Google Provider
    ai_config = LLMProviderConfig(
        provider=ApiProvider.GOOGLE,
        api_key=settings.google_api_key,
        timeout=30
    )
    
    try:
        # 注册Provider
        manager.register_provider(ApiProvider.GOOGLE, ai_config)
        
        # 创建请求
        request = LLMRequest(
            model="gemini-1.5-flash",
            messages=[
                ChatMessage(
                    role=MessageRole.SYSTEM,
                    content="你是一个有用的AI助手。"
                ),
                ChatMessage(
                    role=MessageRole.USER,
                    content="请介绍一下Python编程语言。"
                )
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # 生成响应
        logger.info("正在生成响应...")
        response = await manager.generate_response(request)
        
        logger.info(f"响应内容: {response.content}")
        logger.info(f"使用的模型: {response.model}")
        logger.info(f"Token使用情况: {response.usage}")
        
    except Exception as e:
        logger.error(f"错误: {e}")


async def example_streaming():
    """流式响应示例"""
    settings = get_settings()

    # 检查API密钥
    if not settings.google_api_key or settings.google_api_key == "your-google-key":
        logger.error("Google API密钥未设置或使用了占位符。请在.env文件中设置ASR_GOOGLE_API_KEY")
        return

    # 创建LLM管理器
    manager = LLMManager()

    # 配置Google Provider
    ai_config = LLMProviderConfig(
        provider=ApiProvider.GOOGLE,
        api_key=settings.google_api_key,
        timeout=30
    )
    
    try:
        # 注册Provider
        manager.register_provider(ApiProvider.GOOGLE, ai_config)
        
        # 创建请求
        request = LLMRequest(
            model="gemini-1.5-flash",
            messages=[
                ChatMessage(
                    role=MessageRole.USER,
                    content="请写一首关于春天的诗。"
                )
            ],
            max_tokens=300,
            temperature=0.8,
            stream=True
        )
        
        # 流式生成响应
        logger.info("正在流式生成响应...")
        full_content = ""
        
        async for chunk in manager.stream_response(request):
            if chunk.delta:
                print(chunk.delta, end="", flush=True)
                full_content += chunk.delta
            
            if chunk.finish_reason:
                logger.info(f"\n完成原因: {chunk.finish_reason}")
                break
        
        logger.info(f"\n完整内容: {full_content}")
        
    except Exception as e:
        logger.error(f"错误: {e}")


async def example_multiple_providers():
    """多Provider示例"""
    settings = get_settings()
    
    # 创建LLM管理器
    manager = LLMManager()
    
    # 配置多个Provider
    providers_config = [
        LLMProviderConfig(
            provider=ApiProvider.OPENAI,
            api_key=settings.openai_api_key or "your-openai-api-key"
        ),
        LLMProviderConfig(
            provider=ApiProvider.ANTHROPIC,
            api_key=settings.anthropic_api_key or "your-anthropic-api-key"
        ),
        LLMProviderConfig(
            provider=ApiProvider.OLLAMA,
            base_url=settings.ollama_base_url or "http://localhost:11434"
        )
    ]
    
    try:
        # 注册所有Provider
        for config in providers_config:
            manager.register_provider(config.provider, config)
        
        # 列出所有可用模型
        models = manager.list_available_models()
        logger.info(f"可用模型数量: {len(models)}")
        
        # 使用不同的Provider
        requests = [
            LLMRequest(
                model="gpt-3.5-turbo",
                messages=[ChatMessage(role=MessageRole.USER, content="Hello from OpenAI!")]
            ),
            LLMRequest(
                model="claude-3-5-haiku-20241022",
                messages=[ChatMessage(role=MessageRole.USER, content="Hello from Anthropic!")]
            ),
            LLMRequest(
                model="llama3.2",
                messages=[ChatMessage(role=MessageRole.USER, content="Hello from Ollama!")]
            )
        ]
        
        for request in requests:
            try:
                response = await manager.generate_response(request)
                logger.info(f"模型 {request.model} 响应: {response.content[:100]}...")
            except Exception as e:
                logger.error(f"模型 {request.model} 错误: {e}")
        
    except Exception as e:
        logger.error(f"错误: {e}")


async def example_model_info():
    """模型信息查询示例"""
    # 创建LLM管理器
    manager = LLMManager()
    
    # 查询模型信息
    model_names = ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-2.0-flash-001"]
    
    for model_name in model_names:
        model_info = manager.get_model_info(model_name)
        if model_info:
            logger.info(f"模型: {model_name}")
            logger.info(f"  最大tokens: {model_info.max_tokens}")
            logger.info(f"  上下文窗口: {model_info.context_window}")
            logger.info(f"  支持图像: {model_info.supports_images}")
            logger.info(f"  输入价格: ${model_info.input_price}/百万tokens")
            logger.info(f"  输出价格: ${model_info.output_price}/百万tokens")
            logger.info(f"  描述: {model_info.description}")
            logger.info("---")
        else:
            logger.warning(f"未找到模型信息: {model_name}")


async def main():
    """主函数"""
    logger.info("=== LLM Provider使用示例 ===")
    
    # 运行示例
    examples = [
        # ("模型信息查询", example_model_info),
        # 注意：以下示例需要有效的API密钥才能运行
        ("OpenAI示例", example_google),
        ("流式响应示例", example_streaming),
        # ("多Provider示例", example_multiple_providers),
    ]
    
    for name, example_func in examples:
        logger.info(f"\n--- {name} ---")
        try:
            await example_func()
        except Exception as e:
            logger.error(f"{name} 执行失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())
