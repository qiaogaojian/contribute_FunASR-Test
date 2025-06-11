#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FunASR Paraformer 语音识别配置文件
用于优化语音转文字效果，解决句子错误拆分问题
"""

# =============================================================================
# VAD模型参数配置
# =============================================================================

# 默认优化配置（推荐）
DEFAULT_VAD_CONFIG = {
    "max_end_silence_time": 1200,      # 尾部静音检测时间(ms) - 增加以减少语音提前截断
    "speech_noise_thres": 0.8,         # 语音噪声阈值 - 提高对噪声的容忍度
    "max_start_silence_time": 3000,    # 最大起始静音时间(ms)
    "min_speech_time": 300,            # 最小语音时长(ms) - 避免短音频被误判
}

# 高精度配置（适用于会议、讲座等正式场合）
HIGH_ACCURACY_VAD_CONFIG = {
    "max_end_silence_time": 1500,      # 更长的静音检测时间
    "speech_noise_thres": 0.9,         # 更高的噪声阈值
    "max_start_silence_time": 4000,    
    "min_speech_time": 500,            # 更长的最小语音时长
}

# 快速响应配置（适用于实时对话、客服等场景）
FAST_RESPONSE_VAD_CONFIG = {
    "max_end_silence_time": 800,       # 较短的静音检测时间
    "speech_noise_thres": 0.7,         
    "max_start_silence_time": 2000,    
    "min_speech_time": 200,            # 较短的最小语音时长
}

# 噪声环境配置（适用于嘈杂环境）
NOISY_ENV_VAD_CONFIG = {
    "max_end_silence_time": 1000,      
    "speech_noise_thres": 0.6,         # 降低噪声阈值，更敏感
    "max_start_silence_time": 2500,    
    "min_speech_time": 400,            
}

# =============================================================================
# Chunk Size 配置
# =============================================================================

# 默认优化配置（推荐）
DEFAULT_CHUNK_SIZE = [15, 60, 15]     # 左回看15，总长60，右回看15 (总时长3.6s)

# 高精度配置（更大的上下文窗口）
HIGH_ACCURACY_CHUNK_SIZE = [20, 80, 20]  # 总时长4.8s，更多上下文

# 快速响应配置（较小的窗口，更快响应）
FAST_RESPONSE_CHUNK_SIZE = [10, 40, 10]  # 总时长2.4s，快速响应

# 长语音配置（适用于长篇讲话）
LONG_SPEECH_CHUNK_SIZE = [25, 100, 25]   # 总时长6.0s，最大上下文

# =============================================================================
# 预测频率配置
# =============================================================================

# 默认优化配置
DEFAULT_PREDICTION_INTERVAL = 15      # 每15个片段预测一次 (900ms)

# 高精度配置
HIGH_ACCURACY_PREDICTION_INTERVAL = 20  # 每20个片段预测一次 (1200ms)

# 快速响应配置
FAST_RESPONSE_PREDICTION_INTERVAL = 10  # 每10个片段预测一次 (600ms)

# =============================================================================
# 句子分割配置
# =============================================================================

# 句末标点符号
SENTENCE_END_PUNCTUATION = ('。', '！', '？', '.', '!', '?')

# 避免分割的标点符号
AVOID_SPLIT_PUNCTUATION = ('，', '、', ',', ';', '；')

# 最小句子长度（字符数）
MIN_SENTENCE_LENGTH = 2

# 完整句子的最小长度（用于判断是否为完整语义单元）
COMPLETE_SENTENCE_MIN_LENGTH = 10

# =============================================================================
# 预设配置组合
# =============================================================================

# 会议转录配置
MEETING_CONFIG = {
    "vad_config": HIGH_ACCURACY_VAD_CONFIG,
    "chunk_size": HIGH_ACCURACY_CHUNK_SIZE,
    "prediction_interval": HIGH_ACCURACY_PREDICTION_INTERVAL,
    "description": "适用于会议、讲座等正式场合，追求高精度"
}

# 实时对话配置
REALTIME_CHAT_CONFIG = {
    "vad_config": FAST_RESPONSE_VAD_CONFIG,
    "chunk_size": FAST_RESPONSE_CHUNK_SIZE,
    "prediction_interval": FAST_RESPONSE_PREDICTION_INTERVAL,
    "description": "适用于实时对话、客服等场景，追求快速响应"
}

# 默认平衡配置
BALANCED_CONFIG = {
    "vad_config": DEFAULT_VAD_CONFIG,
    "chunk_size": DEFAULT_CHUNK_SIZE,
    "prediction_interval": DEFAULT_PREDICTION_INTERVAL,
    "description": "平衡精度和响应速度的默认配置"
}

# 噪声环境配置
NOISY_ENV_CONFIG = {
    "vad_config": NOISY_ENV_VAD_CONFIG,
    "chunk_size": DEFAULT_CHUNK_SIZE,
    "prediction_interval": DEFAULT_PREDICTION_INTERVAL,
    "description": "适用于嘈杂环境，提高噪声容忍度"
}

# 长语音配置
LONG_SPEECH_CONFIG = {
    "vad_config": HIGH_ACCURACY_VAD_CONFIG,
    "chunk_size": LONG_SPEECH_CHUNK_SIZE,
    "prediction_interval": HIGH_ACCURACY_PREDICTION_INTERVAL,
    "description": "适用于长篇讲话、演讲等场景"
}

# =============================================================================
# 配置选择函数
# =============================================================================

def get_config(config_name="balanced"):
    """
    获取指定的配置
    
    Args:
        config_name (str): 配置名称
            - "meeting": 会议转录配置
            - "realtime": 实时对话配置  
            - "balanced": 默认平衡配置
            - "noisy": 噪声环境配置
            - "long_speech": 长语音配置
    
    Returns:
        dict: 配置字典
    """
    configs = {
        "meeting": MEETING_CONFIG,
        "realtime": REALTIME_CHAT_CONFIG,
        "balanced": BALANCED_CONFIG,
        "noisy": NOISY_ENV_CONFIG,
        "long_speech": LONG_SPEECH_CONFIG
    }
    
    if config_name not in configs:
        print(f"警告: 未知配置 '{config_name}'，使用默认配置")
        return BALANCED_CONFIG
    
    return configs[config_name]

def list_configs():
    """列出所有可用的配置"""
    configs = {
        "meeting": MEETING_CONFIG,
        "realtime": REALTIME_CHAT_CONFIG,
        "balanced": BALANCED_CONFIG,
        "noisy": NOISY_ENV_CONFIG,
        "long_speech": LONG_SPEECH_CONFIG
    }
    
    print("可用的配置:")
    for name, config in configs.items():
        print(f"  {name}: {config['description']}")

# =============================================================================
# 使用示例
# =============================================================================

if __name__ == "__main__":
    # 列出所有配置
    list_configs()
    
    print("\n" + "="*50)
    
    # 获取会议配置示例
    meeting_config = get_config("meeting")
    print(f"会议配置: {meeting_config['description']}")
    print(f"VAD配置: {meeting_config['vad_config']}")
    print(f"Chunk大小: {meeting_config['chunk_size']}")
    print(f"预测间隔: {meeting_config['prediction_interval']}")
