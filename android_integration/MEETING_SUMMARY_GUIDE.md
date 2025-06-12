# Android端会议总结功能指南

## 概述

Android端会议总结功能完全对应web端的功能逻辑，提供了与后端API的无缝集成，支持三种总结类型，并具有完整的用户界面。

## 功能特性

### 🎯 核心功能
- **三种总结类型**: 简要总结、详细总结、行动项总结
- **自动文本优化**: 后端自动优化ASR文本中的错误
- **实时处理**: 异步API调用，不阻塞UI
- **完整的错误处理**: 网络错误、服务器错误的友好提示
- **结果操作**: 复制到剪贴板、保存文件等

### 📱 用户界面
- **Material Design**: 遵循Android设计规范
- **响应式布局**: 适配不同屏幕尺寸
- **进度指示**: 清晰的加载状态和进度提示
- **导航支持**: 支持返回键和ActionBar导航

## 架构设计

### 📁 文件结构
```
android_integration/app/src/main/java/com/example/asrclient/
├── MainActivity.java                    # 主界面，包含ASR功能和会议总结入口
├── MeetingSummaryActivity.java          # 会议总结界面
├── MeetingSummaryModels.java            # 数据模型定义
├── MeetingSummaryApiClient.java         # API客户端
├── MeetingSummaryTestHelper.java        # 测试辅助工具
└── ... (其他ASR相关文件)

android_integration/app/src/main/res/
├── layout/
│   ├── activity_main.xml               # 主界面布局
│   └── activity_meeting_summary.xml    # 会议总结界面布局
├── values/
│   └── strings.xml                     # 字符串资源
└── ...
```

### 🏗️ 组件说明

#### 1. MeetingSummaryModels.java
定义了所有数据模型，对应后端API的数据结构：
- `SummaryType`: 总结类型枚举
- `MeetingSummaryRequest`: 请求模型
- `MeetingSummaryResponse`: 响应模型
- `ErrorResponse`: 错误响应模型

#### 2. MeetingSummaryApiClient.java
网络API客户端，负责与后端通信：
- 使用OkHttp进行HTTP请求
- 使用Gson进行JSON序列化/反序列化
- 支持异步回调
- 完整的错误处理

#### 3. MeetingSummaryActivity.java
会议总结主界面：
- 显示会议文本预览
- 提供总结类型选择
- 处理API调用和结果显示
- 支持结果操作（复制、保存等）

## 使用流程

### 📝 基本使用步骤

1. **录制会议**: 在主界面使用ASR功能录制会议内容
2. **启动总结**: 点击"会议总结"按钮
3. **选择类型**: 在总结界面选择总结类型
4. **生成总结**: 点击"生成总结"按钮
5. **查看结果**: 等待处理完成，查看总结结果
6. **操作结果**: 复制到剪贴板或保存文件

### 🔄 处理流程

```
用户操作 → 选择总结类型 → API请求 → 后端处理 → 返回结果 → 显示界面
    ↓           ↓            ↓         ↓         ↓         ↓
录制会议 → [简要/详细/行动项] → HTTP POST → [优化+总结] → JSON响应 → 格式化显示
```

## API集成

### 🌐 网络配置

Android端使用与web端相同的后端API：

```java
// API端点
POST /api/meeting/summary          // 生成会议总结
GET  /api/meeting/summary/types    // 获取总结类型
GET  /api/meeting/health           // 健康检查
```

### 📊 请求示例

```java
// 创建API客户端
MeetingSummaryApiClient apiClient = new MeetingSummaryApiClient(serverHost, serverPort);

// 生成会议总结
apiClient.generateMeetingSummary(meetingText, SummaryType.BRIEF, 
    new ApiCallback<MeetingSummaryResponse>() {
        @Override
        public void onSuccess(MeetingSummaryResponse result) {
            // 处理成功结果
            displaySummary(result.getSummary());
        }

        @Override
        public void onError(String error) {
            // 处理错误
            showError(error);
        }
    });
```

## 配置说明

### 🔧 依赖项

在 `app/build.gradle` 中已包含必要的依赖：

```gradle
dependencies {
    // JSON 处理
    implementation 'com.google.code.gson:gson:2.10.1'
    
    // 网络请求
    implementation 'com.squareup.okhttp3:okhttp:4.12.0'
    
    // WebSocket (用于ASR)
    implementation 'org.java-websocket:Java-WebSocket:1.5.3'
}
```

### 📱 权限配置

在 `AndroidManifest.xml` 中已配置必要权限：

```xml
<!-- 网络权限 -->
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

<!-- 音频录制权限 -->
<uses-permission android:name="android.permission.RECORD_AUDIO" />
```

## 测试指南

### 🧪 测试工具

使用 `MeetingSummaryTestHelper` 进行功能测试：

```java
// 测试API连接
MeetingSummaryTestHelper.testApiConnection(serverHost, serverPort, callback);

// 测试获取总结类型
MeetingSummaryTestHelper.testGetSummaryTypes(serverHost, serverPort, callback);

// 测试生成总结
MeetingSummaryTestHelper.testGenerateSummary(serverHost, serverPort, SummaryType.BRIEF, callback);
```

### 📋 测试检查清单

- [ ] 网络连接正常
- [ ] 服务器地址配置正确
- [ ] ASR功能正常录制
- [ ] 会议总结按钮可点击
- [ ] 总结界面正常显示
- [ ] 三种总结类型都能正常生成
- [ ] 错误处理正常工作
- [ ] 复制功能正常
- [ ] 界面导航正常

## 故障排除

### ❗ 常见问题

#### 1. 网络连接失败
- 检查服务器地址和端口配置
- 确认设备与服务器网络连通
- 检查防火墙设置

#### 2. API调用超时
- 检查网络稳定性
- 确认服务器负载正常
- 考虑增加超时时间

#### 3. 总结生成失败
- 检查会议文本是否有效
- 确认LLM服务正常运行
- 查看服务器日志

#### 4. 界面显示异常
- 检查布局文件是否正确
- 确认字符串资源完整
- 重启应用重试

### 🔍 调试方法

1. **查看日志**: 使用 `adb logcat` 查看应用日志
2. **网络抓包**: 使用工具检查HTTP请求
3. **服务器日志**: 查看后端API日志
4. **断点调试**: 在Android Studio中设置断点

## 扩展功能

### 🚀 未来改进

1. **文件保存**: 实现本地文件保存功能
2. **历史记录**: 保存总结历史
3. **分享功能**: 支持分享到其他应用
4. **离线模式**: 支持离线文本处理
5. **自定义配置**: 支持自定义LLM参数

### 🔌 集成建议

1. **数据持久化**: 使用Room数据库保存历史记录
2. **文件管理**: 使用Storage Access Framework
3. **分享集成**: 使用Android分享Intent
4. **通知系统**: 长时间处理时显示通知
5. **主题支持**: 支持深色模式

## 版本信息

- **当前版本**: 1.0.0
- **最低Android版本**: API 21 (Android 5.0)
- **目标Android版本**: API 33 (Android 13)
- **编译SDK版本**: 33

## 相关文档

- [后端API文档](../docs/Meeting-Summary-API.md)
- [Android项目README](./README.md)
- [使用指南](./USAGE_GUIDE.md)
- [故障排除](./AUDIO_TROUBLESHOOTING.md)
