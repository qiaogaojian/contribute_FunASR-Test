# ASR Service - 实时语音识别服务

基于FastAPI和FunASR的现代化实时语音转文字系统，支持WebSocket和REST API，提供多客户端接入能力。

## 🚀 功能特性

### 核心功能
- 🎤 **实时语音识别**：基于FunASR Paraformer模型的高精度识别
- 🌐 **双协议支持**：WebSocket实时通信 + REST API接口
- 📱 **多客户端支持**：Web、移动端、桌面端统一接口
- ⚙️ **多种ASR配置**：会议、实时对话、噪声环境等场景优化
- 🔄 **配置热切换**：运行时动态切换识别配置
- 📊 **会话管理**：完整的会话生命周期管理

### 技术特性
- 🏗️ **现代架构**：基于FastAPI的高性能异步框架
- 📚 **自动文档**：OpenAPI/Swagger自动生成API文档
- 🔒 **类型安全**：Pydantic数据验证和类型检查
- 📈 **可扩展性**：清晰的模块划分，易于扩展
- 🐳 **容器化就绪**：支持Docker部署

## 📋 系统要求

- Python 3.9+
- Poetry包管理器（推荐）或pip
- FunASR模型文件
- 现代Web浏览器
- CUDA环境（推荐，用于GPU加速）

## 🛠️ 安装部署

### 方式一：使用Poetry（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd asr-service

# 2. 安装依赖
poetry install

# 3. 激活虚拟环境
poetry shell

# 4. 启动服务
python run_fastapi.py
```

### 方式二：使用pip

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 2. 安装依赖
pip install fastapi uvicorn[standard] pydantic python-multipart
pip install -r requirements.txt

# 3. 启动服务
python run_fastapi.py
```

## 🚀 快速开始

### 启动服务

```bash
# 启动FastAPI服务（推荐）
python run_fastapi.py

# 或启动原版服务
python run_system.py
```

### 访问服务

启动后可访问以下地址：

- **前端界面**: http://localhost:8000/
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **WebSocket**: ws://localhost:8000/ws/audio

## 📖 API使用指南

### WebSocket实时识别

```javascript
// 连接WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/audio');

// 发送音频数据
ws.send(audioData);  // 发送二进制音频数据

// 接收识别结果
ws.onmessage = function(event) {
    const result = JSON.parse(event.data);
    console.log('识别结果:', result);
};
```

### REST API接口

```bash
# 创建会话
curl -X POST "http://localhost:8000/api/v1/sessions" \
     -H "Content-Type: application/json" \
     -d '{"client_id": "test_client", "config_name": "balanced"}'

# 获取会话详情
curl "http://localhost:8000/api/v1/sessions/{session_id}"

# 上传音频文件
curl -X POST "http://localhost:8000/api/v1/audio/upload" \
     -F "file=@audio.wav" \
     -F "config_name=balanced"

# 获取配置列表
curl "http://localhost:8000/api/v1/configs"
```

## ⚙️ 配置管理

### 环境配置

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

主要配置项：

```env
# 服务配置
ASR_HOST=0.0.0.0
ASR_PORT=8000
ASR_DEBUG=false

# ASR配置
ASR_DEFAULT_ASR_CONFIG=balanced
ASR_ASR_DEVICE=cuda

# 会话配置
ASR_SESSION_TIMEOUT_MINUTES=30
ASR_MAX_SESSIONS_PER_CLIENT=5
```

### ASR配置切换

```bash
# 使用配置切换工具
python scripts/switch_config.py

# 或通过API切换
curl -X GET "http://localhost:8000/api/v1/configs"
```

### 可用配置

| 配置名称 | 描述 | 适用场景 |
|---------|------|----------|
| `balanced` | 默认平衡配置 | 一般场景 |
| `meeting` | 会议转录配置 | 会议记录，高精度 |
| `realtime` | 实时对话配置 | 实时对话，快速响应 |
| `noisy` | 噪声环境配置 | 嘈杂环境 |
| `long_speech` | 长语音配置 | 长时间语音处理 |

## 🏗️ 项目结构

```
asr-service/
├── app/                    # FastAPI应用
│   ├── api/               # API路由
│   │   ├── websocket.py   # WebSocket处理
│   │   └── rest.py        # REST API
│   ├── core/              # 核心配置
│   │   └── config.py      # 配置管理
│   ├── models/            # 数据模型
│   │   └── schemas.py     # Pydantic模型
│   └── main.py            # 应用入口
├── services/              # 业务服务
│   ├── asr_service.py     # ASR服务封装
│   └── session_manager.py # 会话管理
├── src/                   # 原有ASR引擎（保持兼容）
│   ├── asr/               # ASR引擎
│   └── config/            # 配置文件
├── frontend/              # 前端界面
├── utils/                 # 工具函数
├── tests/                 # 测试文件
├── run_fastapi.py         # FastAPI启动脚本
├── run_system.py          # 原版启动脚本（兼容）
└── README.md
```

## 🔧 开发指南

### 添加新的API接口

1. 在 `app/models/schemas.py` 中定义数据模型
2. 在 `app/api/rest.py` 中添加路由处理
3. 在 `services/` 中实现业务逻辑

### 扩展ASR功能

1. 在 `services/asr_service.py` 中添加新方法
2. 在 `src/config/asr_config.py` 中添加新配置
3. 通过API或配置工具应用新功能

### 自定义前端

前端文件位于 `frontend/` 目录，支持：
- 实时WebSocket连接
- 音频录制和播放
- 识别结果显示
- 会话管理界面

## 🧪 测试

```bash
# 安装测试依赖
poetry install --extras test

# 运行测试
pytest tests/ -v

# 运行覆盖率测试
pytest tests/ --cov=app --cov=services
```

## 📊 监控和日志

### 健康检查

```bash
curl http://localhost:8000/health
```

### 系统统计

```bash
curl http://localhost:8000/api/v1/stats
```

### 日志配置

通过环境变量配置日志级别：

```env
ASR_LOG_LEVEL=INFO
ASR_LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## 🚀 部署

### Docker部署（即将支持）

```bash
# 构建镜像
docker build -t asr-service .

# 运行容器
docker run -p 8000:8000 asr-service
```

### 生产环境部署

```bash
# 使用gunicorn部署
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🔍 故障排除

### 常见问题

1. **FastAPI启动失败**
   ```bash
   # 检查依赖是否安装
   pip list | grep fastapi
   
   # 检查端口是否被占用
   netstat -an | grep 8000
   ```

2. **WebSocket连接失败**
   ```bash
   # 检查防火墙设置
   # 确认WebSocket端点可访问
   curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
        http://localhost:8000/ws/audio
   ```

3. **ASR模型加载失败**
   ```bash
   # 检查模型路径配置
   # 确认网络连接正常
   # 查看详细错误日志
   ```

### 性能优化

- 使用GPU加速：设置 `ASR_ASR_DEVICE=cuda`
- 调整会话超时：设置 `ASR_SESSION_TIMEOUT_MINUTES`
- 限制并发会话：设置 `ASR_MAX_SESSIONS_PER_CLIENT`

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [FunASR](https://github.com/alibaba-damo-academy/FunASR) - 语音识别引擎
- [FastAPI](https://fastapi.tiangolo.com/) - Web框架
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证
