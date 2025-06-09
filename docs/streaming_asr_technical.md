# 流式语音识别技术文档

## 概述

流式语音识别模块 (`streaming_asr.py`) 是项目的核心组件，实现了基于 SenseVoiceSmall 模型的实时语音转文字功能。该模块采用多进程架构，确保音频录制和模型推理的并行处理，实现低延迟的实时转录。

## 技术架构

### 整体架构图

```mermaid
graph TB
    subgraph "主进程"
        A[音频设备初始化]
        B[音频流录制]
        C[音频预处理]
        D[队列管理]
    end
    
    subgraph "识别进程"
        E[模型加载]
        F[音频缓存]
        G[实时预测]
        H[最终识别]
        I[结果输出]
    end
    
    subgraph "输出通道"
        J[控制台显示]
        K[UDP网络发送]
        L[文件保存]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    F --> H
    G --> I
    H --> I
    I --> J
    I --> K
    I --> L
```

### 核心组件

#### 1. 模型初始化
```python
# 模型配置
model = AutoModel(
    model=asr_model_path,           # SenseVoiceSmall 主模型
    vad_model=vad_model_path,       # 语音活动检测模型
    punc_model=punc_model_path,     # 标点符号预测模型
    ngpu=1,                         # GPU 数量
    device="cuda",                  # 计算设备
    disable_pbar=True,              # 禁用进度条
    disable_log=True,               # 禁用日志
    disable_update=True             # 禁用更新检查
)
```

#### 2. 多进程架构
```mermaid
sequenceDiagram
    participant M as 主进程
    participant Q as 队列
    participant R as 识别进程
    participant U as UDP输出
    
    M->>M: 初始化音频设备
    M->>R: 启动识别进程
    R->>R: 加载AI模型
    R->>M: 发送就绪信号
    
    loop 音频录制循环
        M->>M: 录制音频片段
        M->>M: 音频预处理
        M->>Q: 放入音频队列
        Q->>R: 获取音频数据
        R->>R: 模型推理
        R->>U: 发送识别结果
        R->>M: 控制台输出
    end
    
    M->>Q: 发送结束信号
    R->>R: 处理剩余音频
    R->>R: 清理资源
```

## 核心算法

### 1. 音频处理流程

```mermaid
flowchart TD
    A[48kHz 音频输入] --> B[降采样到16kHz]
    B --> C[转换为单声道]
    C --> D[归一化处理]
    D --> E[分片处理<br/>60ms/片段]
    E --> F[放入处理队列]
    
    F --> G{片段数量检查}
    G -->|< 20片段| H[实时预测模式]
    G -->|= 20片段| I[最终识别模式]
    
    H --> J[虚拟推理]
    I --> K[正式推理]
    
    J --> L[预测文本输出]
    K --> M[确认文本输出]
    
    L --> N[UDP发送]
    M --> N
    N --> O[控制台显示]
```

### 2. 滑动窗口机制

```mermaid
graph LR
    subgraph "滑动窗口 [10, 20, 10]"
        A[左回看<br/>10片段]
        B[当前窗口<br/>20片段]
        C[右回看<br/>10片段]
    end
    
    D[新音频片段] --> E[窗口滑动]
    E --> F[模型推理]
    F --> G[输出结果]
    
    subgraph "时间轴"
        H[t-600ms]
        I[t-0ms]
        J[t+600ms]
    end
    
    A -.-> H
    B -.-> I
    C -.-> J
```

### 3. 双模式识别策略

```mermaid
stateDiagram-v2
    [*] --> 音频累积
    音频累积 --> 实时预测: 每5片段
    音频累积 --> 最终识别: 达到20片段
    
    实时预测 --> 虚拟推理
    虚拟推理 --> 预测输出
    预测输出 --> 音频累积
    
    最终识别 --> 正式推理
    正式推理 --> 确认输出
    确认输出 --> 清空缓存
    清空缓存 --> 音频累积
    
    预测输出 --> UDP发送
    确认输出 --> UDP发送
    UDP发送 --> 控制台显示
```

## 关键代码解析

### 1. 音频录制回调函数

```python
def record_callback(indata: np.ndarray, 
                    frames: int, time_info, 
                    status: sd.CallbackFlags) -> None:
    """
    音频录制回调函数
    - 将48kHz音频降采样到16kHz
    - 转换为单声道
    - 放入处理队列
    """
    # 降采样：48kHz -> 16kHz (每3个采样点取1个)
    data = np.mean(indata.copy()[::3], axis=1)
    
    # 放入队列供识别进程处理
    queue_in.put({'type':'feed', 'samples':data})
    
    # 同时保存到文件
    f.writeframes((data * (2**15-1)).astype(np.int16).tobytes())
```

### 2. 识别处理核心逻辑

```python
def recognize(queue_in: Queue, queue_out: Queue):
    """
    识别进程主函数
    - 处理音频队列
    - 执行模型推理
    - 输出识别结果
    """
    chunk_size = [10, 20, 10]  # 滑动窗口配置
    chunks = []                # 音频片段缓存
    param_dict = {'cache': dict()}  # 模型状态缓存
    
    while instruction := queue_in.get():
        match instruction['type']:
            case 'feed':
                chunks.append(instruction['samples'])
                
                # 实时预测模式
                if len(chunks) < chunk_size[1] and pre_num == pre_expect:
                    虚字典 = deepcopy(param_dict)
                    虚字典['is_final'] = True
                    data = np.concatenate(chunks)
                    rec_result = model.generate(input=data, cache=虚字典.get('cache', {}))
                    # 输出预测结果...
                
                # 最终识别模式
                if len(chunks) == chunk_size[1]:
                    data = np.concatenate(chunks)
                    rec_result = model.generate(input=data, cache=param_dict.get('cache', {}))
                    # 输出确认结果...
                    chunks.clear()
```

## 性能优化

### 1. 内存管理

```mermaid
graph TB
    A[音频缓存池] --> B[循环复用]
    C[模型状态缓存] --> D[增量更新]
    E[队列大小限制] --> F[防止内存溢出]
    
    subgraph "优化策略"
        G[预分配内存]
        H[及时释放]
        I[缓存复用]
    end
    
    B --> G
    D --> H
    F --> I
```

### 2. 计算优化

```mermaid
graph LR
    A[GPU加速] --> B[CUDA推理]
    C[批处理] --> D[提高吞吐量]
    E[模型量化] --> F[减少计算量]
    G[缓存机制] --> H[避免重复计算]
    
    subgraph "性能指标"
        I[延迟 < 2秒]
        J[CPU使用率 < 50%]
        K[内存使用 < 2GB]
    end
    
    B --> I
    D --> J
    F --> K
    H --> I
```

## 配置参数

### 模型配置
```python
# 模型路径配置
asr_model_path = "SenseVoiceSmall模型路径"
vad_model_path = "VAD模型路径"  
punc_model_path = "标点模型路径"

# 硬件配置
ngpu = 1                    # GPU数量
device = "cuda"             # 计算设备
ncpu = 4                    # CPU核心数
```

### 音频配置
```python
# 录制参数
samplerate = 48000          # 原始采样率
channels = 1                # 声道数
blocksize = int(3 * 960)    # 缓冲区大小 (0.06秒)

# 处理参数
target_samplerate = 16000   # 目标采样率
chunk_duration = 60         # 片段时长(ms)
chunk_size = [10, 20, 10]   # 滑动窗口配置
```

### 网络配置
```python
udp_port = 6009             # UDP发送端口
line_width = 50             # 显示行宽度
```

## 错误处理

### 1. 异常处理机制

```mermaid
graph TB
    A[音频设备异常] --> B[设备检测]
    B --> C[错误提示]
    C --> D[优雅退出]
    
    E[模型加载异常] --> F[路径检查]
    F --> G[自动下载]
    G --> H[重新加载]
    
    I[网络异常] --> J[重连机制]
    J --> K[降级处理]
    
    L[内存不足] --> M[缓存清理]
    M --> N[参数调整]
```

### 2. 信号处理
```python
def signal_handler(sig, frame):
    """处理Ctrl+C中断信号"""
    print("\n\033[31m收到中断信号 Ctrl+C，退出程序\033[0m")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
```

## 使用示例

### 基本使用
```bash
# 启动流式识别
python streaming_asr.py

# 程序会自动：
# 1. 加载模型
# 2. 初始化音频设备  
# 3. 开始实时录制和识别
# 4. 按回车键结束当前句子
```

### 高级配置
```python
# 自定义模型路径
home_directory = "自定义模型目录"
asr_model_path = os.path.join(home_directory, "模型名称")

# 自定义网络端口
udp_port = 8080

# 自定义显示参数
line_width = 80
```

## 性能监控

### 关键指标
- **延迟**: 音频输入到文本输出的时间差
- **准确率**: 识别文本的正确率
- **资源使用**: CPU、内存、GPU使用情况
- **网络状态**: UDP发送成功率

### 监控方法
```python
# 延迟监控
start_time = time.time()
# ... 处理逻辑 ...
latency = time.time() - start_time

# 资源监控
import psutil
cpu_percent = psutil.cpu_percent()
memory_percent = psutil.virtual_memory().percent
```

---

**文档版本**: v1.0  
**创建日期**: 2024-01-15  
**维护者**: 技术团队
