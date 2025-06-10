# FunASR 实时语音转文字前端

基于WebSocket的实时语音转文字显示前端，配合FunASR Paraformer模型使用。

## 功能特性

- 🎤 **实时显示**: 实时显示语音识别结果
- 🌐 **WebSocket连接**: 基于WebSocket的低延迟通信
- 📱 **响应式设计**: 支持桌面和移动设备
- 💾 **文本保存**: 支持保存识别结果到文件
- 🔄 **自动重连**: 连接断开时自动重连
- ⌨️ **快捷键支持**: 支持键盘快捷键操作
- 🎨 **美观界面**: 现代化的用户界面设计

## 项目结构

```
├── src/
│   ├── asr/
│   │   └── streaming_paraformer.py    # ASR主程序
│   └── websocket_server.py            # WebSocket服务器
├── frontend/
│   ├── index.html                     # 前端页面
│   └── style.css                      # 样式文件
├── start_frontend.py                  # 启动脚本
└── README.md                          # 说明文档
```

## 安装依赖

```bash
# 安装WebSocket依赖
pip install websockets

# 或者运行启动脚本会自动安装
python start_frontend.py
```

## 使用方法

### 方法一：一键启动（推荐）

#### Windows批处理脚本
```bash
start_asr_system.bat
```

#### PowerShell脚本
```powershell
.\start_asr_system.ps1
```

#### Python脚本
```bash
python start_asr_system.py
```

这将自动：
1. 激活虚拟环境
2. 启动WebSocket服务器
3. 启动ASR语音识别服务
4. 打开前端页面

### 方法二：分步启动

1. **激活虚拟环境**
   ```bash
   micromamba activate ./venv
   ```

2. **启动WebSocket服务器**
   ```bash
   python src/websocket_server.py
   ```

3. **启动ASR程序**
   ```bash
   python src/asr/streaming_paraformer.py
   ```

4. **打开前端页面**
   - 直接打开 `frontend/index.html` 文件
   - 或访问 `file:///path/to/frontend/index.html`

## 配置说明

### 端口配置

- **UDP端口**: 6009 (ASR程序发送数据)
- **WebSocket端口**: 8766 (前端连接)

如需修改端口，请同时修改以下文件：
- `src/asr/streaming_paraformer.py` 中的 `udp_port`
- `src/websocket_server.py` 中的端口参数
- `frontend/index.html` 中的WebSocket连接地址

### ASR模型配置

ASR程序使用以下模型：
- **ASR模型**: speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch
- **VAD模型**: speech_fsmn_vad_zh-cn-16k-common-pytorch
- **标点模型**: punc_ct-transformer_zh-cn-common-vocab272727-pytorch
- **说话人模型**: speech_campplus_sv_zh-cn_16k-common

模型将自动下载到 `D:/Cache/model/asr` 目录。

### 语音识别优化配置

为了解决**一句话被错误拆分**的问题，系统提供了多种优化配置：

#### 可用配置类型
- **balanced** (默认): 平衡精度和响应速度
- **meeting**: 会议转录，追求高精度
- **realtime**: 实时对话，追求快速响应
- **noisy**: 噪声环境，提高噪声容忍度
- **long_speech**: 长语音，适用于演讲等场景

#### 配置切换方法

**交互式切换**：
```bash
python switch_asr_config.py
```

**命令行快速切换**：
```bash
python switch_asr_config.py meeting    # 切换到会议模式
python switch_asr_config.py realtime   # 切换到实时模式
```

#### 优化效果
- ✅ 减少句子错误拆分
- ✅ 提高识别连续性
- ✅ 改善语义完整性
- ✅ 智能句子边界检测

详细配置说明请参考 `FunASR_优化配置说明.md`

## 快捷键

- **Ctrl + L**: 清空文本
- **Ctrl + S**: 保存文本到文件
- **Ctrl + R**: 重新连接WebSocket

## 界面说明

### 状态指示器
- 🟢 **绿色**: 已连接
- 🔴 **红色**: 连接断开/错误
- 🟠 **橙色**: 重连中

### 文本显示
- **蓝色边框**: 最终识别结果
- **橙色边框**: 预览文本（可能变化）

### 控制按钮
- **清空文本**: 清除显示的所有文本
- **保存文本**: 将当前文本保存为txt文件
- **重新连接**: 手动重新连接WebSocket

## 技术架构

```
┌─────────────────┐    UDP     ┌──────────────────┐    WebSocket    ┌─────────────────┐
│   ASR程序       │ ---------> │  WebSocket服务器  │ <-----------> │   前端页面      │
│ (Paraformer)    │   6009     │                  │     8765        │   (HTML/JS)     │
└─────────────────┘            └──────────────────┘                 └─────────────────┘
```

1. **ASR程序**: 实时语音识别，通过UDP发送结果
2. **WebSocket服务器**: 接收UDP数据，转发给前端
3. **前端页面**: 显示识别结果，提供用户交互

## 故障排除

### 连接问题
1. 确保ASR程序正在运行
2. 检查端口是否被占用
3. 确认防火墙设置

### 显示问题
1. 刷新页面重新连接
2. 检查浏览器控制台错误信息
3. 确认WebSocket服务器正常运行

### 性能优化
1. 关闭不必要的浏览器标签页
2. 确保网络连接稳定
3. 调整ASR程序的chunk_size参数

## 开发说明

### 自定义样式
修改 `frontend/style.css` 文件可以自定义界面样式。

### 扩展功能
- 在 `frontend/index.html` 中添加JavaScript代码
- 在 `src/websocket_server.py` 中扩展服务器功能

### 调试模式
在浏览器开发者工具中查看WebSocket连接状态和消息。

## 许可证

本项目基于MIT许可证开源。

## 贡献

欢迎提交Issue和Pull Request来改进项目。
