#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频处理工具函数
"""

import numpy as np
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


def convert_audio_format(
    audio_data: bytes,
    source_format: str = "int16",
    target_format: str = "float32",
    sample_rate: int = 16000
) -> np.ndarray:
    """
    转换音频数据格式
    
    Args:
        audio_data: 原始音频数据
        source_format: 源格式 (int16, float32)
        target_format: 目标格式 (int16, float32)
        sample_rate: 采样率
    
    Returns:
        转换后的音频数组
    """
    try:
        if source_format == "int16":
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            if target_format == "float32":
                # 转换为float32，范围[-1, 1]
                audio_array = audio_array.astype(np.float32) / 32768.0
        elif source_format == "float32":
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            if target_format == "int16":
                # 转换为int16
                audio_array = (audio_array * 32768.0).astype(np.int16)
        else:
            raise ValueError(f"Unsupported source format: {source_format}")
        
        return audio_array
        
    except Exception as e:
        logger.error(f"Failed to convert audio format: {e}")
        raise


def resample_audio(
    audio_data: np.ndarray,
    source_rate: int,
    target_rate: int
) -> np.ndarray:
    """
    重采样音频数据
    
    Args:
        audio_data: 音频数据数组
        source_rate: 源采样率
        target_rate: 目标采样率
    
    Returns:
        重采样后的音频数组
    """
    try:
        if source_rate == target_rate:
            return audio_data
        
        # 简单的线性插值重采样
        ratio = target_rate / source_rate
        new_length = int(len(audio_data) * ratio)
        
        # 创建新的索引
        old_indices = np.arange(len(audio_data))
        new_indices = np.linspace(0, len(audio_data) - 1, new_length)
        
        # 线性插值
        resampled_data = np.interp(new_indices, old_indices, audio_data)
        
        return resampled_data.astype(audio_data.dtype)
        
    except Exception as e:
        logger.error(f"Failed to resample audio: {e}")
        raise


def normalize_audio(audio_data: np.ndarray, target_level: float = 0.8) -> np.ndarray:
    """
    音频归一化
    
    Args:
        audio_data: 音频数据数组
        target_level: 目标电平 (0-1)
    
    Returns:
        归一化后的音频数组
    """
    try:
        # 计算当前最大值
        max_val = np.max(np.abs(audio_data))
        
        if max_val > 0:
            # 计算缩放因子
            scale_factor = target_level / max_val
            normalized_data = audio_data * scale_factor
        else:
            normalized_data = audio_data
        
        return normalized_data
        
    except Exception as e:
        logger.error(f"Failed to normalize audio: {e}")
        raise


def detect_silence(
    audio_data: np.ndarray,
    threshold: float = 0.01,
    min_silence_duration: float = 0.5,
    sample_rate: int = 16000
) -> Tuple[bool, float]:
    """
    检测音频中的静音
    
    Args:
        audio_data: 音频数据数组
        threshold: 静音阈值
        min_silence_duration: 最小静音持续时间（秒）
        sample_rate: 采样率
    
    Returns:
        (是否为静音, 静音持续时间)
    """
    try:
        # 计算音频能量
        energy = np.mean(np.abs(audio_data))
        
        # 检查是否低于阈值
        is_silence = energy < threshold
        
        # 计算持续时间
        duration = len(audio_data) / sample_rate
        
        # 只有持续时间足够长才认为是静音
        is_long_silence = is_silence and duration >= min_silence_duration
        
        return is_long_silence, duration if is_silence else 0.0
        
    except Exception as e:
        logger.error(f"Failed to detect silence: {e}")
        return False, 0.0


def split_audio_chunks(
    audio_data: np.ndarray,
    chunk_size: int,
    overlap: int = 0
) -> list:
    """
    将音频分割为块
    
    Args:
        audio_data: 音频数据数组
        chunk_size: 块大小（采样点数）
        overlap: 重叠大小（采样点数）
    
    Returns:
        音频块列表
    """
    try:
        chunks = []
        step = chunk_size - overlap
        
        for i in range(0, len(audio_data) - chunk_size + 1, step):
            chunk = audio_data[i:i + chunk_size]
            chunks.append(chunk)
        
        # 处理最后一个不完整的块
        if len(audio_data) % step != 0:
            last_chunk = audio_data[-(chunk_size):]
            if len(last_chunk) == chunk_size:
                chunks.append(last_chunk)
        
        return chunks
        
    except Exception as e:
        logger.error(f"Failed to split audio chunks: {e}")
        return []


def calculate_audio_features(audio_data: np.ndarray, sample_rate: int = 16000) -> dict:
    """
    计算音频特征
    
    Args:
        audio_data: 音频数据数组
        sample_rate: 采样率
    
    Returns:
        音频特征字典
    """
    try:
        features = {}
        
        # 基本统计特征
        features["duration"] = len(audio_data) / sample_rate
        features["max_amplitude"] = float(np.max(np.abs(audio_data)))
        features["mean_amplitude"] = float(np.mean(np.abs(audio_data)))
        features["rms"] = float(np.sqrt(np.mean(audio_data ** 2)))
        
        # 零交叉率
        zero_crossings = np.where(np.diff(np.signbit(audio_data)))[0]
        features["zero_crossing_rate"] = len(zero_crossings) / len(audio_data)
        
        # 能量
        features["energy"] = float(np.sum(audio_data ** 2))
        
        # 动态范围
        features["dynamic_range"] = float(np.max(audio_data) - np.min(audio_data))
        
        return features
        
    except Exception as e:
        logger.error(f"Failed to calculate audio features: {e}")
        return {}


def validate_audio_format(
    audio_data: bytes,
    expected_sample_rate: int = 16000,
    expected_channels: int = 1,
    expected_format: str = "int16"
) -> Tuple[bool, str]:
    """
    验证音频格式
    
    Args:
        audio_data: 音频数据
        expected_sample_rate: 期望的采样率
        expected_channels: 期望的声道数
        expected_format: 期望的格式
    
    Returns:
        (是否有效, 错误信息)
    """
    try:
        # 检查数据长度
        if len(audio_data) == 0:
            return False, "Empty audio data"
        
        # 检查数据长度是否符合格式要求
        if expected_format == "int16":
            if len(audio_data) % 2 != 0:
                return False, "Invalid data length for int16 format"
        elif expected_format == "float32":
            if len(audio_data) % 4 != 0:
                return False, "Invalid data length for float32 format"
        
        # 转换并检查数据
        try:
            if expected_format == "int16":
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
            elif expected_format == "float32":
                audio_array = np.frombuffer(audio_data, dtype=np.float32)
            else:
                return False, f"Unsupported format: {expected_format}"
        except Exception:
            return False, "Failed to parse audio data"
        
        # 检查声道数
        if expected_channels > 1:
            if len(audio_array) % expected_channels != 0:
                return False, f"Invalid data length for {expected_channels} channels"
        
        # 检查数据范围
        if expected_format == "int16":
            if np.any(audio_array < -32768) or np.any(audio_array > 32767):
                return False, "Audio data out of int16 range"
        elif expected_format == "float32":
            if np.any(np.abs(audio_array) > 1.0):
                return False, "Audio data out of float32 range [-1, 1]"
        
        return True, "Valid audio format"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"
