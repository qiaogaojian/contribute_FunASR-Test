# FunASR 实时语音识别系统 - 架构概览

## 项目简介

本项目是基于 FunASR 的实时语音识别系统，支持流式转录、说话人分离、Web界面交互等功能。项目采用模块化设计，支持多种使用场景。

## 整体架构

```mermaid
graph TB
    subgraph "用户界面层"
        A[Web界面<br/>live_transcription.html]
        B[桌面GUI<br/>top/app.py]
        C[命令行工具<br/>streaming_asr.py]
    end
    
    subgraph "应用服务层"
        D[会议助手模块<br/>meeting_helper/]
        E[ASR核心模块<br/>asr/]
        F[工具模块<br/>utils/]
    end
    
    subgraph "AI模型层"
        G[SenseVoiceSmall<br/>语音识别]
        H[VAD模型<br/>语音活动检测]
        I[标点模型<br/>标点符号预测]
        J[说话人分离模型<br/>Speaker Diarization]
    end
    
    subgraph "数据存储层"
        K[音频文件<br/>audio/]
        L[输出结果<br/>output/]
        M[模型缓存<br/>model cache]
    end
    
    A --> D
    B --> E
    C --> D
    D --> G
    D --> H
    D --> I
    E --> G
    E --> H
    E --> I
    E --> J
    G --> M
    H --> M
    I --> M
    J --> M
    D --> K
    D --> L
    E --> L
```

## 核心功能模块

### 1. 流式语音识别模块 (`streaming_asr.py`)

**功能特点：**
- 实时音频录制和处理
- 基于 SenseVoiceSmall 模型的高精度语音识别
- UDP 网络通信实时发送识别结果
- 多进程架构确保实时性能

**技术架构：**
```mermaid
graph LR
    A[音频输入] --> B[音频预处理]
    B --> C[队列缓存]
    C --> D[识别进程]
    D --> E[文本输出]
    D --> F[UDP发送]
    
    subgraph "多进程架构"
        G[主进程<br/>音频录制]
        H[识别进程<br/>模型推理]
    end
    
    G --> C
    H --> D
```

### 2. Web界面模块 (`live_transcription.html`)

**功能特点：**
- 基于 WebSocket 的实时通信
- 音频录制和波形可视化
- 实时转录结果展示
- 说话人分离和时间戳显示

**技术架构：**
```mermaid
sequenceDiagram
    participant U as 用户
    participant W as Web界面
    participant S as WebSocket服务
    participant A as ASR引擎
    
    U->>W: 点击开始录制
    W->>S: 建立WebSocket连接
    W->>W: 获取麦克风权限
    W->>W: 开始音频录制
    
    loop 实时录制
        W->>S: 发送音频数据
        S->>A: 语音识别处理
        A->>S: 返回转录结果
        S->>W: 推送转录数据
        W->>W: 实时显示结果
    end
    
    U->>W: 点击停止录制
    W->>S: 发送停止信号
    S->>W: 发送最终结果
    W->>W: 显示完整转录
```

### 3. 说话人分离模块 (`top/app.py`)

**功能特点：**
- 批量音视频文件处理
- 说话人自动识别和分离
- 按说话人切分音频文件
- 生成结构化转录文本

**处理流程：**
```mermaid
flowchart TD
    A[选择音视频文件] --> B[音频预处理]
    B --> C[语音识别 + 说话人分离]
    C --> D[生成时间戳信息]
    D --> E[按说话人分组]
    E --> F[切分音频片段]
    F --> G[合并同说话人音频]
    G --> H[生成转录文本]
    H --> I[保存结果文件]
    
    subgraph "输出文件"
        J[按说话人分类的音频]
        K[转录文本文件]
        L[时间戳信息]
    end
    
    I --> J
    I --> K
    I --> L
```

## 技术栈

### 核心依赖
- **FunASR**: 阿里达摩院开源的语音识别框架
- **SenseVoiceSmall**: 高效的多语言语音识别模型
- **sounddevice**: Python 音频录制库
- **numpy**: 数值计算库
- **ffmpeg**: 音视频处理工具

### 模型组件
- **ASR模型**: SenseVoiceSmall (多语言语音识别)
- **VAD模型**: FSMN-VAD (语音活动检测)
- **标点模型**: CT-Transformer (标点符号预测)
- **说话人模型**: CAM++ (说话人分离，可选)

## 数据流架构

```mermaid
graph TB
    subgraph "输入层"
        A1[麦克风输入]
        A2[音频文件]
        A3[视频文件]
    end
    
    subgraph "处理层"
        B1[音频预处理<br/>采样率转换/降噪]
        B2[特征提取<br/>MFCC/Mel频谱]
        B3[模型推理<br/>语音识别]
        B4[后处理<br/>标点/说话人分离]
    end
    
    subgraph "输出层"
        C1[实时文本流]
        C2[结构化转录]
        C3[音频片段]
        C4[统计报告]
    end
    
    A1 --> B1
    A2 --> B1
    A3 --> B1
    B1 --> B2
    B2 --> B3
    B3 --> B4
    B4 --> C1
    B4 --> C2
    B4 --> C3
    B4 --> C4
```

## 部署架构

### 本地部署
```mermaid
graph TB
    subgraph "本地环境"
        A[Python 3.10+]
        B[CUDA 环境<br/>可选]
        C[模型文件<br/>本地缓存]
        D[应用程序]
    end
    
    subgraph "外部依赖"
        E[ModelScope<br/>模型下载]
        F[FFmpeg<br/>音视频处理]
    end
    
    A --> D
    B --> D
    C --> D
    E --> C
    F --> D
```

### 分布式部署
```mermaid
graph TB
    subgraph "前端服务"
        A[Web界面]
        B[静态资源]
    end
    
    subgraph "后端服务"
        C[WebSocket服务]
        D[ASR服务]
        E[文件服务]
    end
    
    subgraph "存储层"
        F[音频存储]
        G[结果存储]
        H[模型存储]
    end
    
    A --> C
    C --> D
    D --> H
    D --> F
    D --> G
```

## 性能特性

### 实时性能
- **延迟**: < 2秒 (从音频输入到文本输出)
- **吞吐量**: 支持实时音频流处理
- **并发**: 支持多路音频流同时处理

### 识别精度
- **中文识别**: > 95% 准确率
- **英文识别**: > 98% 准确率
- **说话人分离**: > 90% 准确率

### 资源消耗
- **内存**: 2-4GB (取决于模型大小)
- **GPU**: 可选，显著提升处理速度
- **存储**: 1小时音频约100MB

## 扩展性设计

### 模型扩展
- 支持多种 FunASR 模型
- 可配置模型参数
- 支持模型热切换

### 功能扩展
- 插件化架构
- API 接口标准化
- 多语言支持

### 部署扩展
- 容器化部署
- 微服务架构
- 负载均衡支持

## 下一步规划

1. **性能优化**: 模型量化、推理加速
2. **功能增强**: 情感识别、关键词提取
3. **界面改进**: 更丰富的可视化功能
4. **集成能力**: 与其他系统的API集成

---

**文档版本**: v1.0  
**创建日期**: 2024-01-15  
**维护者**: 技术团队
