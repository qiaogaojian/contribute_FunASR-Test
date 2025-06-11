# Android 端接入 FastAPI ASR 服务

## 📱 项目概述

这是一个 Android 客户端，用于连接 FastAPI ASR 语音识别服务，实现实时语音转文字功能。

## 🏗️ 架构说明

```
Android App
├── ASRManager (主管理器)
├── ASRWebSocketClient (WebSocket客户端)
├── AudioRecordManager (音频录制)
└── MainActivity (用户界面)
```

## 🚀 快速开始

### 1. 项目导入

#### 1.1 使用 Android Studio
1. 打开 Android Studio
2. 选择 "Open an existing Android Studio project"
3. 选择 `android_integration` 文件夹
4. 等待 Gradle 同步完成

#### 1.2 命令行编译
```bash
cd android_integration
./gradlew assembleDebug
```

### 2. 服务器端配置

确保您的 FastAPI ASR 服务正在运行：

```bash
# 启动 FastAPI 服务
./venv/python.exe run_fastapi.py
```

服务器将在以下地址运行：
- HTTP: `http://0.0.0.0:8000`
- WebSocket: `ws://0.0.0.0:8000/ws/audio`

### 2. 网络配置

#### 2.1 获取服务器IP地址

在服务器机器上运行：
```bash
# Windows
ipconfig

# Linux/Mac
ifconfig
```

找到局域网IP地址，例如：`192.168.1.163`

#### 2.2 防火墙配置

确保服务器防火墙允许 8000 端口访问：

**Windows:**
```cmd
netsh advfirewall firewall add rule name="FastAPI ASR" dir=in action=allow protocol=TCP localport=8000
```

**Linux:**
```bash
sudo ufw allow 8000
```

### 3. Android 端配置

#### 3.1 修改服务器地址

在 `ASRManager.java` 中修改服务器地址：

```java
private String serverHost = "192.168.1.163"; // 替换为您的服务器IP
private int serverPort = 8000;
```

或者在应用中动态设置：

```java
asrManager.setServerAddress("192.168.1.163", 8000);
```

#### 3.2 网络安全配置

在 `AndroidManifest.xml` 中已添加：
```xml
android:usesCleartextTraffic="true"
```

这允许 HTTP 连接（开发环境）。生产环境建议使用 HTTPS。

## 📋 功能特性

### ✅ 已实现功能

- [x] WebSocket 实时连接
- [x] 实时音频录制（16kHz, 16bit, 单声道）
- [x] 实时语音识别
- [x] 连接状态管理
- [x] 错误处理和重连
- [x] 心跳保活机制
- [x] 权限管理
- [x] 用户界面

### 🎯 核心特性

1. **实时识别**: 边说边识别，实时显示结果
2. **高质量音频**: 16kHz采样率，与服务器端匹配
3. **稳定连接**: 自动心跳，连接状态监控
4. **Meeting模式**: 默认使用高精度会议模式
5. **错误恢复**: 自动重连和错误处理

## 🔧 API 接口

### WebSocket 连接

```
ws://[服务器IP]:8000/ws/audio?config_name=meeting
```

### 消息格式

#### 发送音频数据
```
二进制数据: PCM 16bit 音频流
```

#### 接收识别结果
```json
{
  "type": "asr_result",
  "result": {
    "text": "识别的文字内容",
    "is_final": true
  }
}
```

## 📱 使用步骤

1. **启动应用**: 打开 Android 应用
2. **配置服务器**: 输入服务器IP和端口
3. **连接服务器**: 点击"连接服务器"按钮
4. **开始录音**: 连接成功后点击"开始录音"
5. **查看结果**: 实时查看语音识别结果

## 🛠️ 开发配置

### 依赖库

```gradle
// WebSocket 客户端
implementation 'org.java-websocket:Java-WebSocket:1.5.3'

// JSON 处理
implementation 'com.google.code.gson:gson:2.10.1'

// 权限处理
implementation 'com.karumi:dexter:6.2.3'
```

### 权限要求

```xml
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

## 🔍 故障排除

### 常见问题

1. **连接失败**
   - 检查服务器是否运行
   - 确认IP地址和端口正确
   - 检查防火墙设置

2. **无法录音**
   - 检查麦克风权限
   - 确认设备麦克风正常

3. **识别效果差**
   - 确保环境安静
   - 说话清晰，距离麦克风适中
   - 检查网络连接稳定性

### 调试日志

在 Android Studio 中查看 Logcat：
```
标签过滤: ASRManager|ASRWebSocketClient|AudioRecordManager
```

## 🚀 高级配置

### 自定义 ASR 配置

```java
// 可选配置: meeting, balanced, realtime, noisy, long_speech
asrManager.setConfigName("meeting");
```

### 音频参数调整

在 `AudioRecordManager.java` 中可调整：
- 采样率: `SAMPLE_RATE = 16000`
- 缓冲区大小: `BUFFER_SIZE_FACTOR = 2`

## 📞 技术支持

如有问题，请检查：
1. 服务器端日志
2. Android 端 Logcat
3. 网络连接状态
4. 权限设置
