# -*- coding: utf-8 -*-
"""
WebSocket ASR引擎 - 专门处理来自前端的音频数据
"""

import numpy as np
import logging
from funasr import AutoModel
import os
from modelscope import snapshot_download

# 导入配置文件
try:
    from src.config.asr_config import get_config, SENTENCE_END_PUNCTUATION, AVOID_SPLIT_PUNCTUATION, MIN_SENTENCE_LENGTH, COMPLETE_SENTENCE_MIN_LENGTH
except ImportError:
    print("警告: 无法导入配置文件，使用默认配置")
    # 默认配置
    def get_config(name="meeting"):
        return {
            "vad_config": {
                "max_end_silence_time": 1200,
                "speech_noise_thres": 0.8,
                "max_start_silence_time": 3000,
                "min_speech_time": 300,
            },
            "chunk_size": [15, 60, 15],
            "prediction_interval": 15
        }
    SENTENCE_END_PUNCTUATION = ('。', '！', '？', '.', '!', '?')
    AVOID_SPLIT_PUNCTUATION = ('，', '、', ',', ';', '；')
    MIN_SENTENCE_LENGTH = 2
    COMPLETE_SENTENCE_MIN_LENGTH = 10

logger = logging.getLogger(__name__)

class WebSocketASR:
    def __init__(self, config_name="meeting"):
        self.config = get_config(config_name)
        self.model = None
        self.cache = {}
        self.audio_buffer = []
        self.chunk_size = 16000  # 1秒的音频数据
        self.sample_rate = 16000
        
        self._init_model()
        
    def _init_model(self):
        """初始化ASR模型"""
        try:
            home_directory = os.path.expanduser("D:/Cache/model/asr")
            
            asr_model_path = os.path.join(home_directory, "iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch")
            vad_model_path = os.path.join(home_directory, "iic/speech_fsmn_vad_zh-cn-16k-common-pytorch")
            punc_model_path = os.path.join(home_directory, "iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch")
            spk_model_path = os.path.join(home_directory, "iic/speech_campplus_sv_zh-cn_16k-common")
            
            # 检查模型是否存在，不存在则下载
            if not os.path.exists(os.path.join(asr_model_path, 'configuration.json')):
                logger.info("正在下载ASR模型文件...")
                snapshot_download('iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch', 
                                cache_dir=home_directory)
            
            # 初始化模型
            self.model = AutoModel(
                model=asr_model_path,
                vad_model=vad_model_path,
                punc_model=punc_model_path,
                spk_model=spk_model_path,
                vad_kwargs=self.config["vad_config"],
                ngpu=1,
                ncpu=4,
                device="cuda",
                disable_pbar=True,
                disable_log=True,
                disable_update=True
            )
            
            logger.info("ASR模型初始化成功")
            
        except Exception as e:
            logger.error(f"ASR模型初始化失败: {e}")
            self.model = None
    
    def recognize_chunk(self, audio_data):
        """识别音频块"""
        if not self.model:
            return None
            
        try:
            # 确保音频数据是正确的格式
            if isinstance(audio_data, list):
                audio_data = np.array(audio_data, dtype=np.float32)
            elif audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # 添加到缓冲区
            self.audio_buffer.extend(audio_data)
            
            # 当缓冲区有足够数据时进行识别
            if len(self.audio_buffer) >= self.chunk_size:
                # 获取一个chunk的数据
                chunk_data = np.array(self.audio_buffer[:self.chunk_size])
                self.audio_buffer = self.audio_buffer[self.chunk_size:]
                
                # 进行ASR识别
                result = self.model.generate(
                    input=chunk_data,
                    cache=self.cache,
                    is_final=True
                )
                
                if result and len(result) > 0 and result[0].get('text'):
                    text = result[0]['text'].strip()
                    if len(text) >= MIN_SENTENCE_LENGTH:
                        return text
            
            return None
            
        except Exception as e:
            logger.error(f"音频识别失败: {e}")
            # 清空缓冲区以避免错误累积
            self.audio_buffer = []
            return None
    
    def reset(self):
        """重置ASR状态"""
        self.cache = {}
        self.audio_buffer = []
        logger.info("ASR状态已重置")