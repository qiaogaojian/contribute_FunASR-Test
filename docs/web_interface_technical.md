# Web界面技术文档

## 概述

Web界面模块 (`live_transcription.html`) 提供了基于浏览器的实时语音转录功能。该模块使用现代Web技术，通过WebSocket与后端服务通信，实现音频录制、实时转录显示、说话人分离等功能。

## 技术架构

### 整体架构图

```mermaid
graph TB
    subgraph "前端组件"
        A[用户界面]
        B[音频录制模块]
        C[WebSocket客户端]
        D[波形可视化]
        E[转录显示模块]
    end
    
    subgraph "浏览器API"
        F[MediaDevices API]
        G[MediaRecorder API]
        H[WebSocket API]
        I[Canvas API]
    end
    
    subgraph "后端服务"
        J[WebSocket服务器]
        K[ASR引擎]
        L[说话人分离]
    end
    
    A --> B
    B --> F
    B --> G
    C --> H
    D --> I
    
    B --> C
    C --> J
    J --> K
    K --> L
    L --> J
    J --> C
    C --> E
```

### 核心技术栈

- **前端框架**: 原生JavaScript (ES6+)
- **音频处理**: Web Audio API, MediaRecorder API
- **实时通信**: WebSocket
- **可视化**: Canvas 2D API
- **样式**: CSS3 (Flexbox, Animations)

## 功能模块详解

### 1. 音频录制模块

```mermaid
sequenceDiagram
    participant U as 用户
    participant UI as 界面
    participant M as MediaRecorder
    participant A as AudioContext
    participant W as WebSocket
    
    U->>UI: 点击录制按钮
    UI->>UI: 请求麦克风权限
    UI->>M: 创建MediaRecorder
    UI->>A: 创建AudioContext
    UI->>A: 连接音频分析器
    
    loop 录制过程
        M->>M: 录制音频块
        M->>W: 发送音频数据
        A->>UI: 更新波形显示
    end
    
    U->>UI: 点击停止按钮
    UI->>M: 停止录制
    UI->>W: 发送停止信号
    UI->>A: 关闭音频上下文
```

#### 关键代码实现

```javascript
async function startRecording() {
    try {
        // 获取麦克风权限
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // 创建音频上下文用于波形显示
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        microphone = audioContext.createMediaStreamSource(stream);
        microphone.connect(analyser);
        
        // 创建录制器
        recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
        recorder.ondataavailable = (e) => {
            if (websocket && websocket.readyState === WebSocket.OPEN) {
                websocket.send(e.data);  // 发送音频数据到服务器
            }
        };
        
        recorder.start(chunkDuration);  // 开始录制，按块发送
        drawWaveform();  // 开始波形绘制
        
    } catch (err) {
        console.error("录制启动失败:", err);
    }
}
```

### 2. WebSocket通信模块

```mermaid
stateDiagram-v2
    [*] --> 连接中
    连接中 --> 已连接: 连接成功
    连接中 --> 连接失败: 连接超时
    
    已连接 --> 录制中: 开始录制
    录制中 --> 处理中: 停止录制
    处理中 --> 已连接: 处理完成
    
    已连接 --> 断开连接: 用户关闭
    录制中 --> 断开连接: 网络异常
    处理中 --> 断开连接: 服务器错误
    
    连接失败 --> [*]
    断开连接 --> [*]
```

#### WebSocket消息协议

```javascript
// 发送音频数据
websocket.send(audioBlob);

// 接收转录结果
websocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case "transcription":
            // 处理转录结果
            updateTranscription(data);
            break;
            
        case "ready_to_stop":
            // 处理停止确认
            finalizeTranscription();
            break;
            
        case "error":
            // 处理错误信息
            handleError(data.message);
            break;
    }
};
```

### 3. 实时转录显示模块

```mermaid
flowchart TD
    A[接收转录数据] --> B{数据类型检查}
    B -->|实时转录| C[更新缓冲区显示]
    B -->|确认转录| D[添加到历史记录]
    B -->|说话人信息| E[更新说话人标签]
    
    C --> F[渲染临时文本]
    D --> G[渲染确认文本]
    E --> H[渲染说话人信息]
    
    F --> I[更新界面]
    G --> I
    H --> I
    
    I --> J[滚动到底部]
```

#### 转录结果渲染

```javascript
function renderLinesWithBuffer(lines, buffer_diarization, buffer_transcription, 
                              remaining_time_diarization, remaining_time_transcription, 
                              isFinalizing = false, current_status = "active_transcription") {
    
    // 检查音频状态
    if (current_status === "no_audio_detected") {
        linesTranscriptDiv.innerHTML = "<p style='text-align: center; color: #666;'><em>No audio detected...</em></p>";
        return; 
    }

    // 渲染历史转录行
    const linesHtml = lines.map((item, idx) => {
        let timeInfo = "";
        if (item.beg !== undefined && item.end !== undefined) {
            timeInfo = ` ${item.beg} - ${item.end}`;
        }
        
        const speakerLabel = item.spk !== undefined 
            ? `<strong>说话人 ${item.spk}</strong>${timeInfo}` 
            : "";
            
        let currentLineText = item.text || "";
        
        // 添加缓冲区内容
        if (idx === lines.length - 1) {
            if (buffer_diarization && !isFinalizing) {
                currentLineText += `<span class="buffer_diarization">${buffer_diarization}</span>`;
            }
            if (buffer_transcription) {
                if (isFinalizing) {
                    currentLineText += (currentLineText.length > 0 ? " " : "") + buffer_transcription.trim();
                } else {
                    currentLineText += `<span class="buffer_transcription">${buffer_transcription}</span>`;
                }
            }
        }
        
        return `<p>${speakerLabel}<br/><div class='textcontent'>${currentLineText}</div></p>`;
    }).join("");

    linesTranscriptDiv.innerHTML = linesHtml;
}
```

### 4. 波形可视化模块

```mermaid
graph LR
    A[音频分析器] --> B[频域数据获取]
    B --> C[时域数据转换]
    C --> D[Canvas绘制]
    D --> E[动画循环]
    E --> A
    
    subgraph "绘制参数"
        F[采样点数: 256]
        G[刷新率: 60fps]
        H[波形颜色: 黑色]
    end
    
    B --> F
    D --> G
    D --> H
```

#### 波形绘制实现

```javascript
function drawWaveform() {
    if (!analyser) return;
    
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyser.getByteTimeDomainData(dataArray);
    
    // 清空画布
    waveCtx.clearRect(0, 0, waveCanvas.width / (window.devicePixelRatio || 1), 
                             waveCanvas.height / (window.devicePixelRatio || 1));
    
    // 设置绘制样式
    waveCtx.lineWidth = 1;
    waveCtx.strokeStyle = 'rgb(0, 0, 0)';
    waveCtx.beginPath();
    
    const sliceWidth = (waveCanvas.width / (window.devicePixelRatio || 1)) / bufferLength;
    let x = 0;
    
    // 绘制波形
    for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = v * (waveCanvas.height / (window.devicePixelRatio || 1)) / 2;
        
        if (i === 0) {
            waveCtx.moveTo(x, y);
        } else {
            waveCtx.lineTo(x, y);
        }
        
        x += sliceWidth;
    }
    
    waveCtx.stroke();
    animationFrame = requestAnimationFrame(drawWaveform);
}
```

## 用户界面设计

### 1. 响应式布局

```mermaid
graph TB
    subgraph "界面组件"
        A[录制按钮<br/>圆形/椭圆形切换]
        B[设置面板<br/>音频参数配置]
        C[状态显示<br/>录制状态/时间]
        D[波形显示<br/>实时音频可视化]
        E[转录区域<br/>滚动文本显示]
    end
    
    subgraph "交互状态"
        F[待机状态<br/>圆形按钮]
        G[录制状态<br/>椭圆形按钮+波形]
        H[处理状态<br/>禁用按钮+等待]
    end
    
    A --> F
    A --> G
    A --> H
    D --> G
    E --> G
    E --> H
```

### 2. 样式系统

```css
/* 录制按钮样式 */
#recordButton {
    width: 50px;
    height: 50px;
    border: none;
    border-radius: 50%;
    background-color: white;
    cursor: pointer;
    transition: all 0.3s ease;
}

#recordButton.recording {
    width: 180px;
    border-radius: 40px;
    justify-content: flex-start;
    padding-left: 20px;
}

/* 转录文本样式 */
.buffer_transcription {
    color: #666;
    font-style: italic;
}

.buffer_diarization {
    color: #999;
    font-size: 0.9em;
}

.textcontent {
    margin-top: 5px;
    line-height: 1.4;
}
```

## 状态管理

### 1. 应用状态机

```mermaid
stateDiagram-v2
    [*] --> 初始化
    初始化 --> 就绪: 页面加载完成
    
    就绪 --> 连接中: 点击录制
    连接中 --> 录制中: WebSocket连接成功
    连接中 --> 就绪: 连接失败
    
    录制中 --> 停止中: 点击停止
    停止中 --> 处理中: 发送停止信号
    处理中 --> 就绪: 接收完成信号
    
    录制中 --> 就绪: 网络断开
    停止中 --> 就绪: 超时
    处理中 --> 就绪: 错误
```

### 2. 状态变量管理

```javascript
// 全局状态变量
let isRecording = false;           // 录制状态
let websocket = null;              // WebSocket连接
let recorder = null;               // 媒体录制器
let waitingForStop = false;        // 等待停止状态
let audioContext = null;           // 音频上下文
let analyser = null;               // 音频分析器

// 配置变量
let chunkDuration = 1000;          // 音频块时长(ms)
let websocketUrl = "ws://localhost:8000/asr";  // WebSocket地址

// UI更新函数
function updateUI() {
    recordButton.classList.toggle("recording", isRecording);
    recordButton.disabled = waitingForStop;
    
    if (waitingForStop) {
        statusText.textContent = "Please wait for processing to complete...";
    } else if (isRecording) {
        statusText.textContent = "Recording...";
    } else {
        statusText.textContent = "Click to start transcription";
    }
}
```

## 错误处理

### 1. 异常处理策略

```mermaid
graph TB
    A[麦克风权限被拒绝] --> B[显示权限提示]
    C[WebSocket连接失败] --> D[显示连接错误]
    E[音频录制异常] --> F[重置录制状态]
    G[网络断开] --> H[自动重连机制]
    
    subgraph "错误恢复"
        I[状态重置]
        J[资源清理]
        K[用户提示]
    end
    
    B --> I
    D --> I
    F --> J
    H --> K
```

### 2. 错误处理实现

```javascript
// WebSocket错误处理
websocket.onerror = (error) => {
    console.error("WebSocket错误:", error);
    statusText.textContent = "Connection error. Please try again.";
    if (isRecording) {
        stopRecording();
    }
};

// 麦克风权限错误处理
try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
} catch (err) {
    if (err.name === 'NotAllowedError') {
        statusText.textContent = "Microphone access denied. Please allow microphone access.";
    } else if (err.name === 'NotFoundError') {
        statusText.textContent = "No microphone found. Please connect a microphone.";
    } else {
        statusText.textContent = "Error accessing microphone: " + err.message;
    }
}
```

## 性能优化

### 1. 内存管理

```javascript
// 资源清理函数
function cleanupResources() {
    if (recorder) {
        recorder.stop();
        recorder = null;
    }
    
    if (microphone) {
        microphone.disconnect();
        microphone = null;
    }
    
    if (audioContext && audioContext.state !== 'closed') {
        audioContext.close();
        audioContext = null;
    }
    
    if (animationFrame) {
        cancelAnimationFrame(animationFrame);
        animationFrame = null;
    }
}
```

### 2. 性能监控

```javascript
// 性能指标监控
const performanceMetrics = {
    startTime: null,
    audioChunks: 0,
    totalLatency: 0,
    
    recordStart() {
        this.startTime = performance.now();
        this.audioChunks = 0;
        this.totalLatency = 0;
    },
    
    recordChunk() {
        this.audioChunks++;
    },
    
    recordLatency(latency) {
        this.totalLatency += latency;
    },
    
    getAverageLatency() {
        return this.audioChunks > 0 ? this.totalLatency / this.audioChunks : 0;
    }
};
```

## 部署配置

### 1. 服务器配置

```javascript
// WebSocket服务器地址配置
const host = window.location.hostname || "localhost";
const port = window.location.port || "8000";
const protocol = window.location.protocol === "https:" ? "wss" : "ws";
const defaultWebSocketUrl = `${protocol}://${host}:${port}/asr`;
```

### 2. 浏览器兼容性

```javascript
// 浏览器API兼容性检查
function checkBrowserSupport() {
    const support = {
        mediaDevices: !!navigator.mediaDevices,
        mediaRecorder: !!window.MediaRecorder,
        webSocket: !!window.WebSocket,
        audioContext: !!(window.AudioContext || window.webkitAudioContext)
    };
    
    const unsupported = Object.keys(support).filter(key => !support[key]);
    
    if (unsupported.length > 0) {
        console.warn("不支持的浏览器功能:", unsupported);
        return false;
    }
    
    return true;
}
```

---

**文档版本**: v1.0  
**创建日期**: 2024-01-15  
**维护者**: 技术团队
