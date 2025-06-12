# 会议总结API文档

## 概述

会议总结API提供了专门的接口来处理会议记录的总结功能，支持多种总结类型，并自动优化ASR（语音识别）文本。

## 功能特性

- 🔧 **自动文本优化**: 自动修正ASR文本中的同音字、语法、标点等错误
- 📋 **多种总结类型**: 支持简要总结、详细总结、行动项总结
- 🚀 **高性能处理**: 基于FastAPI的异步处理架构
- 🔌 **模块化设计**: 独立的API模块，便于其他客户端集成
- 📊 **详细响应**: 包含处理时间、模型信息等详细数据

## API端点

### 1. 生成会议总结

**POST** `/api/meeting/summary`

生成会议总结，支持三种总结类型。

#### 请求参数

```json
{
  "meeting_text": "会议记录文本内容",
  "summary_type": "总结类型 (brief/detailed/action)",
  "model": "LLM模型名称 (可选，默认: gemini-1.5-flash)",
  "temperature": "温度参数 (可选，默认: 0.3)"
}
```

#### 总结类型说明

- **brief**: 简要总结 - 重点摘要，提取关键决策和重要信息
- **detailed**: 详细总结 - 完整分析，包含会议概述、讨论内容、决策事项等
- **action**: 行动项总结 - 待办事项，提取具体的任务、负责人和时间节点

#### 响应格式

```json
{
  "success": true,
  "message": "会议总结生成成功",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "summary": "生成的总结内容",
  "summary_type": "brief",
  "model": "gemini-1.5-flash",
  "processing_time": 3.45,
  "optimized_text": "优化后的原始文本 (仅调试模式)"
}
```

#### 示例请求

```bash
curl -X POST "http://localhost:8000/api/meeting/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_text": "[14:30:15] 今天我们讨论项目进度...",
    "summary_type": "brief",
    "model": "gemini-1.5-flash",
    "temperature": 0.3
  }'
```

### 2. 获取支持的总结类型

**GET** `/api/meeting/summary/types`

获取所有支持的总结类型列表。

#### 响应格式

```json
{
  "success": true,
  "message": "总结类型列表获取成功",
  "types": [
    {
      "type": "brief",
      "name": "简要总结",
      "description": "重点摘要，提取关键决策和重要信息"
    },
    {
      "type": "detailed", 
      "name": "详细总结",
      "description": "完整分析，包含会议概述、讨论内容、决策事项等"
    },
    {
      "type": "action",
      "name": "行动项总结", 
      "description": "待办事项，提取具体的任务、负责人和时间节点"
    }
  ]
}
```

### 3. 健康检查

**GET** `/api/meeting/health`

检查会议总结服务的健康状态。

#### 响应格式

```json
{
  "success": true,
  "message": "会议总结服务运行正常",
  "service": "Meeting Summary API",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## 处理流程

会议总结API采用两步处理流程：

1. **文本优化阶段**: 
   - 自动修正ASR文本中的同音字错误
   - 优化标点符号和语法结构
   - 保持原始时间戳和格式

2. **总结生成阶段**:
   - 基于优化后的文本生成对应类型的总结
   - 使用专门优化的提示词模板
   - 返回结构化的总结内容

## 错误处理

### 常见错误码

- **400 Bad Request**: 请求参数错误
  - 不支持的总结类型
  - 缺少必需参数
  - LLM调用失败

- **500 Internal Server Error**: 服务器内部错误
  - LLM服务异常
  - 系统资源不足

### 错误响应格式

```json
{
  "detail": "错误详细信息"
}
```

## 集成示例

### JavaScript/前端集成

```javascript
async function generateMeetingSummary(meetingText, summaryType) {
  const response = await fetch('/api/meeting/summary', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      meeting_text: meetingText,
      summary_type: summaryType,
      model: 'gemini-1.5-flash',
      temperature: 0.3
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '请求失败');
  }

  const data = await response.json();
  return data.summary;
}
```

### Python客户端集成

```python
import aiohttp
import asyncio

async def generate_meeting_summary(meeting_text, summary_type):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'http://localhost:8000/api/meeting/summary',
            json={
                'meeting_text': meeting_text,
                'summary_type': summary_type,
                'model': 'gemini-1.5-flash',
                'temperature': 0.3
            }
        ) as response:
            data = await response.json()
            return data['summary']
```

## 性能优化

- **异步处理**: 基于FastAPI的异步架构，支持高并发
- **智能缓存**: 可配置LLM响应缓存（未来版本）
- **资源管理**: 自动管理LLM连接池和资源释放
- **错误重试**: 内置LLM调用重试机制

## 配置说明

API使用现有的LLM配置，支持多种LLM提供商：

- OpenAI (GPT系列)
- Google (Gemini系列) 
- Anthropic (Claude系列)
- Ollama (本地模型)

配置方式请参考主项目的LLM配置文档。

## 测试

使用提供的测试脚本验证API功能：

```bash
python test_meeting_summary_api.py
```

测试脚本会验证：
- 健康检查端点
- 总结类型列表端点  
- 各种类型的会议总结生成

## 版本历史

- **v1.0.0**: 初始版本
  - 支持三种总结类型
  - 自动ASR文本优化
  - 完整的错误处理和日志记录
