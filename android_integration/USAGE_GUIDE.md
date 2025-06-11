# Android ASR 客户端使用指南

## 📱 项目概述

这是一个完整的 Android 应用，用于连接 FastAPI ASR 语音识别服务，实现实时语音转文字功能。

## 🏗️ 项目结构

```
android_integration/
├── app/
│   ├── src/main/
│   │   ├── java/com/example/asrclient/
│   │   │   ├── MainActivity.java              # 基础版主活动
│   │   │   ├── MainActivityImproved.java      # 改进版主活动 (推荐)
│   │   │   ├── ASRManager.java                # ASR 服务管理器
│   │   │   ├── ASRWebSocketClient.java        # WebSocket 客户端
│   │   │   └── AudioRecordManager.java        # 音频录制管理
│   │   ├── res/
│   │   │   ├── layout/
│   │   │   │   ├── activity_main.xml          # 基础布局
│   │   │   │   └── activity_main_improved.xml # 改进布局 (推荐)
│   │   │   ├── values/
│   │   │   │   ├── strings.xml                # 字符串资源
│   │   │   │   ├── colors.xml                 # 颜色资源
│   │   │   │   ├── styles.xml                 # 样式资源
│   │   │   │   └── themes.xml                 # 主题配置
│   │   │   └── drawable/                      # 图标资源
│   │   └── AndroidManifest.xml                # 应用配置
│   └── build.gradle                           # 项目依赖
└── README.md                                  # 项目说明
```

## 🚀 快速开始

### 1. 环境准备

#### 服务器端
```bash
# 启动 FastAPI ASR 服务
cd /path/to/fastapi-asr-project
./venv/python.exe run_fastapi.py
```

#### Android 开发环境
- Android Studio Arctic Fox 或更高版本
- Android SDK API 21+ (Android 5.0+)
- Java 8 或更高版本

### 2. 项目导入

1. 打开 Android Studio
2. 选择 "Open an existing Android Studio project"
3. 导航到 `android_integration` 目录
4. 点击 "OK" 导入项目

### 3. 配置修改

#### 3.1 服务器地址配置

在 `ASRManager.java` 中修改服务器地址：

```java
// 第 25-27 行
private String serverHost = "192.168.1.100"; // 替换为您的服务器IP
private int serverPort = 8000;
private String configName = "meeting"; // ASR配置模式
```

#### 3.2 选择主活动

在 `AndroidManifest.xml` 中选择要使用的主活动：

**使用基础版本：**
```xml
<activity android:name=".MainActivity" ... />
```

**使用改进版本（推荐）：**
```xml
<activity android:name=".MainActivityImproved" ... />
```

### 4. 编译和运行

1. 连接 Android 设备或启动模拟器
2. 点击 "Run" 按钮或按 Shift+F10
3. 应用将自动安装并启动

## 📱 应用使用

### 1. 权限授予

首次启动时，应用会请求以下权限：
- 🎤 **录音权限**: 用于音频录制
- 🌐 **网络权限**: 用于连接服务器

### 2. 连接服务器

1. 在 "服务器配置" 区域输入：
   - **地址**: 服务器IP地址（如：192.168.1.100）
   - **端口**: 服务器端口（默认：8000）

2. 点击 **"连接服务器"** 按钮

3. 等待连接成功提示

### 3. 开始语音识别

1. 确保已连接到服务器
2. 点击 **"开始录音"** 按钮
3. 开始说话，应用会实时显示识别结果
4. 点击 **"停止录音"** 结束识别

### 4. 查看结果

- **实时结果**: 在状态栏显示临时识别结果
- **最终结果**: 在结果区域显示完整的识别文本
- **时间戳**: 每条结果都带有时间标记

## 🎨 界面功能

### 基础版界面 (MainActivity)

- ✅ 简洁的线性布局
- ✅ 基本的连接和录音功能
- ✅ 文本结果显示

### 改进版界面 (MainActivityImproved) 🌟

- ✅ Material Design 设计
- ✅ 卡片式布局，更美观
- ✅ 状态颜色指示
- ✅ 浮动清空按钮
- ✅ 改进的输入框设计
- ✅ 图标按钮

## 🔧 技术特性

### 音频处理
- **采样率**: 16kHz
- **位深度**: 16bit
- **声道**: 单声道
- **格式**: PCM

### 网络通信
- **协议**: WebSocket
- **数据格式**: 二进制音频流
- **心跳机制**: 30秒间隔
- **自动重连**: 支持

### ASR 配置
- **默认模式**: Meeting（会议模式）
- **高精度**: 适合正式场合
- **低延迟**: 实时响应

## 🛠️ 自定义配置

### 1. 修改 ASR 模式

在 `ASRManager.java` 中：

```java
private String configName = "meeting"; // 可选: meeting, balanced, realtime, noisy, long_speech
```

### 2. 调整音频参数

在 `AudioRecordManager.java` 中：

```java
private static final int SAMPLE_RATE = 16000;        // 采样率
private static final int BUFFER_SIZE_FACTOR = 2;     // 缓冲区倍数
```

### 3. 修改界面主题

在 `res/values/themes.xml` 中自定义颜色和样式。

## 🔍 故障排除

### 常见问题

#### 1. 连接失败
**症状**: 点击连接后显示连接失败
**解决方案**:
- 检查服务器是否正在运行
- 确认IP地址和端口正确
- 检查防火墙设置
- 确保设备与服务器在同一网络

#### 2. 无法录音
**症状**: 点击开始录音没有反应
**解决方案**:
- 检查麦克风权限是否已授予
- 确认设备麦克风正常工作
- 重启应用重新申请权限

#### 3. 识别效果差
**症状**: 识别结果不准确
**解决方案**:
- 确保环境安静
- 说话清晰，距离麦克风适中
- 检查网络连接稳定性
- 尝试不同的ASR配置模式

#### 4. 应用崩溃
**症状**: 应用意外退出
**解决方案**:
- 查看 Android Studio Logcat 日志
- 检查权限设置
- 重新编译安装应用

### 调试方法

#### 1. 查看日志
在 Android Studio 中打开 Logcat，过滤标签：
```
ASRManager|ASRWebSocketClient|AudioRecordManager
```

#### 2. 网络测试
使用浏览器访问服务器健康检查：
```
http://[服务器IP]:8000/health
```

#### 3. 权限检查
在设备设置中检查应用权限是否正确授予。

## 📞 技术支持

### 开发者选项

1. **启用USB调试**: 设置 → 开发者选项 → USB调试
2. **保持屏幕唤醒**: 防止调试时屏幕关闭
3. **显示布局边界**: 帮助调试界面问题

### 性能优化

1. **内存使用**: 监控应用内存占用
2. **网络流量**: 检查数据传输效率
3. **电池优化**: 避免后台运行时过度耗电

### 扩展功能建议

- 📁 **文件识别**: 支持音频文件上传识别
- 🌍 **多语言**: 支持不同语言识别
- 💾 **历史记录**: 本地保存识别历史
- 🔐 **用户认证**: 添加登录功能
- 📊 **统计分析**: 识别准确率统计

---

**注意**: 此应用仅供开发和测试使用，生产环境请确保网络安全和数据隐私保护。
