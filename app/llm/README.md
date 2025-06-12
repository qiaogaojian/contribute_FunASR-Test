# LLM Provider模块

统一的大语言模型接口，支持多种LLM Provider，提供一致的API体验。

## 功能特性

- 🔌 **多Provider支持**: OpenAI、Anthropic、Google、Ollama等
- 🌊 **流式响应**: 支持实时流式输出
- 🛠️ **工具调用**: 支持Function Calling
- 📊 **模型信息**: 完整的模型能力和价格信息
- ⚙️ **配置管理**: 灵活的配置系统
- 🔄 **异步支持**: 完全异步的API设计
- 🛡️ **错误处理**: 完善的错误处理和重试机制

## 支持的Provider

| Provider | 状态 | 流式 | 工具调用 | 图像支持 |
|----------|------|------|----------|----------|
| OpenAI | ✅ | ✅ | ✅ | ✅ |
| Anthropic | ✅ | ✅ | ✅ | ✅ |
| Google/Gemini | ✅ | ✅ | ❌ | ✅ |
| Ollama | ✅ | ✅ | ❌ | ❌ |
| Deepseek | ✅ | ✅ | ✅ | ❌ |
| OpenRouter | ✅ | ✅ | ✅ | ✅ |
| SiliconFlow | ✅ | ✅ | ✅ | ❌ |
| Groq | ✅ | ✅ | ✅ | ❌ |

## 快速开始

### 1. 基本使用

```python
import asyncio
from app.llm import LLMManager, LLMRequest, LLMProviderConfig, ChatMessage, MessageRole, ApiProvider

async def basic_example():
    # 创建管理器
    manager = LLMManager()
    
    # 配置Provider
    config = LLMProviderConfig(
        provider=ApiProvider.OPENAI,
        api_key="your-api-key"
    )
    
    # 注册Provider
    manager.register_provider(ApiProvider.OPENAI, config)
    
    # 创建请求
    request = LLMRequest(
        model="gpt-3.5-turbo",
        messages=[
            ChatMessage(role=MessageRole.USER, content="Hello, world!")
        ]
    )
    
    # 生成响应
    response = await manager.generate_response(request)
    print(response.content)

asyncio.run(basic_example())
```

### 2. 流式响应

```python
async def streaming_example():
    # ... 配置代码同上 ...
    
    request = LLMRequest(
        model="gpt-3.5-turbo",
        messages=[ChatMessage(role=MessageRole.USER, content="写一首诗")],
        stream=True
    )
    
    async for chunk in manager.stream_response(request):
        print(chunk.delta, end="", flush=True)
```

### 3. 多Provider使用

```python
async def multi_provider_example():
    manager = LLMManager()
    
    # 注册多个Provider
    providers = [
        (ApiProvider.OPENAI, {"api_key": "openai-key"}),
        (ApiProvider.ANTHROPIC, {"api_key": "anthropic-key"}),
        (ApiProvider.OLLAMA, {"base_url": "http://localhost:11434"})
    ]
    
    for provider_type, config_dict in providers:
        config = LLMProviderConfig(provider=provider_type, **config_dict)
        manager.register_provider(provider_type, config)
    
    # 自动选择Provider
    request = LLMRequest(
        model="gpt-4o",  # 会自动选择OpenAI
        messages=[ChatMessage(role=MessageRole.USER, content="Hello")]
    )
    
    response = await manager.generate_response(request)
```

## 配置

### 环境变量配置

在`.env`文件中设置：

```env
# 默认LLM配置
ASR_LLM_PROVIDER=openai
ASR_LLM_MODEL=gpt-3.5-turbo
ASR_LLM_API_KEY=your-default-api-key
ASR_LLM_TEMPERATURE=0.7
ASR_LLM_MAX_TOKENS=1000

# 各Provider的API密钥
ASR_OPENAI_API_KEY=your-openai-key
ASR_ANTHROPIC_API_KEY=your-anthropic-key
ASR_GOOGLE_API_KEY=your-google-key
ASR_OLLAMA_BASE_URL=http://localhost:11434
```

### 代码配置

```python
from app.llm import LLMProviderConfig, ApiProvider

config = LLMProviderConfig(
    provider=ApiProvider.OPENAI,
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",  # 可选
    timeout=30,
    max_retries=3,
    extra_config={"organization": "your-org"}  # Provider特定配置
)
```

## 模型信息

查询模型能力和价格信息：

```python
# 查询特定模型
model_info = manager.get_model_info("gpt-4o")
print(f"最大tokens: {model_info.max_tokens}")
print(f"支持图像: {model_info.supports_images}")
print(f"输入价格: ${model_info.input_price}/百万tokens")

# 列出所有可用模型
all_models = manager.list_available_models()
for name, info in all_models.items():
    print(f"{name}: {info.description}")
```

## 错误处理

```python
from app.llm.exceptions import (
    LLMError,
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMModelNotFoundError
)

try:
    response = await manager.generate_response(request)
except LLMAuthenticationError:
    print("API密钥无效")
except LLMRateLimitError as e:
    print(f"速率限制，请等待 {e.retry_after} 秒")
except LLMModelNotFoundError:
    print("模型不存在")
except LLMError as e:
    print(f"LLM错误: {e}")
```

## 高级功能

### 工具调用

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "城市名称"}
                },
                "required": ["location"]
            }
        }
    }
]

request = LLMRequest(
    model="gpt-4o",
    messages=[ChatMessage(role=MessageRole.USER, content="北京天气如何？")],
    tools=tools,
    tool_choice="auto"
)
```

### 上下文管理

```python
async with manager.provider_context(ApiProvider.OPENAI) as provider:
    # 直接使用Provider
    response = await provider.generate_response(request)
```

## 扩展新Provider

1. 继承`BaseLLMProvider`类
2. 实现必要的抽象方法
3. 在`LLMManager`中注册

```python
from app.llm.base import BaseLLMProvider

class CustomProvider(BaseLLMProvider):
    async def generate_response(self, request, **kwargs):
        # 实现生成逻辑
        pass
    
    async def stream_response(self, request, **kwargs):
        # 实现流式逻辑
        pass
    
    def get_available_models(self):
        # 返回可用模型
        pass
    
    def validate_config(self):
        # 验证配置
        pass
```

## 注意事项

1. **API密钥安全**: 不要在代码中硬编码API密钥，使用环境变量
2. **速率限制**: 注意各Provider的速率限制，实现适当的重试逻辑
3. **成本控制**: 监控token使用量，特别是昂贵的模型
4. **错误处理**: 实现完善的错误处理和降级策略
5. **异步使用**: 所有API都是异步的，确保正确使用`await`

## 示例代码

查看 `app/llm/example.py` 获取更多使用示例。
