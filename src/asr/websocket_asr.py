# -*- coding: utf-8 -*-
"""
WebSocket ASR引擎 - 专门处理来自前端的音频数据
优化版本：参考streaming_paraformer.py的优秀实现，支持两阶段识别
"""

import numpy as np
import logging
from funasr import AutoModel
import os
from modelscope import snapshot_download
from copy import deepcopy
from string import ascii_letters

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
        self.config_name = config_name
        self.model = None

        # 缓存管理 - 参考streaming_paraformer.py的实现
        self.param_dict = {'cache': dict()}  # 主缓存，用于最终识别

        # 音频处理相关 - 使用配置文件中的参数
        self.audio_buffer = []  # 音频缓冲区，存储原始音频数据
        self.chunks = []        # 音频块列表，用于分块处理
        self.sample_rate = 16000

        # 使用配置文件中的chunk_size参数（单位：60ms片段）
        self.chunk_size_config = self.config["chunk_size"]  # [左回看, 总长度, 右回看]
        self.chunk_samples = self.chunk_size_config[1] * 960  # 总长度对应的采样点数

        # 预测控制 - 参考streaming_paraformer.py的预测机制
        self.prediction_interval = self.config["prediction_interval"]
        self.pre_num = 0  # 预测计数器
        self.last_prediction = ''  # 上次预测结果

        # 初始化模型
        self._init_model()

        logger.info(f"WebSocketASR初始化完成，使用配置: {config_name}")
        logger.info(f"Chunk配置: {self.chunk_size_config} (总时长: {self.chunk_size_config[1] * 60}ms)")
        logger.info(f"预测间隔: 每{self.prediction_interval}个片段({self.prediction_interval * 60}ms)")
        logger.info(f"VAD配置: {self.config['vad_config']}")
        
    def _init_model(self):
        """初始化ASR模型 - 参考streaming_paraformer.py的模型配置"""
        try:
            home_directory = os.path.expanduser("D:/Cache/model/asr")

            # 模型路径配置 - 与streaming_paraformer.py保持一致
            asr_model_path = os.path.join(home_directory, "iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch")
            asr_model_revision = "v2.0.4"
            vad_model_path = os.path.join(home_directory, "iic/speech_fsmn_vad_zh-cn-16k-common-pytorch")
            vad_model_revision = "v2.0.4"
            punc_model_path = os.path.join(home_directory, "iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch")
            punc_model_revision = "v2.0.4"
            spk_model_path = os.path.join(home_directory, "iic/speech_campplus_sv_zh-cn_16k-common")
            spk_model_revision = "v2.0.4"

            # 检查模型是否存在，不存在则下载
            if not os.path.exists(os.path.join(asr_model_path, 'configuration.json')):
                logger.info("正在下载ASR模型文件...")
                snapshot_download('iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch', cache_dir=home_directory)
                snapshot_download('iic/speech_fsmn_vad_zh-cn-16k-common-pytorch', cache_dir=home_directory)
                snapshot_download('iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch', cache_dir=home_directory)
                snapshot_download('iic/speech_campplus_sv_zh-cn_16k-common', cache_dir=home_directory)

            # 使用配置文件中的VAD参数
            vad_kwargs = self.config["vad_config"]
            logger.info(f"使用VAD配置: {vad_kwargs}")

            # 初始化模型 - 与streaming_paraformer.py保持一致的参数
            self.model = AutoModel(
                model=asr_model_path,                  model_revision=asr_model_revision,
                vad_model=vad_model_path,              vad_model_revision=vad_model_revision,
                punc_model=punc_model_path,            punc_model_revision=punc_model_revision,
                spk_model=spk_model_path,              spk_model_revision=spk_model_revision,
                vad_kwargs=vad_kwargs,                 # 使用配置文件中的VAD参数
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
        """
        识别音频块 - 优化版本，支持两阶段识别
        返回格式: {"type": "preview/final", "text": "识别文本"}
        """
        if not self.model:
            return None

        try:
            # 确保音频数据是正确的格式
            if isinstance(audio_data, list):
                audio_data = np.array(audio_data, dtype=np.float32)
            elif audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)

            # 将音频数据转换为960采样点的片段（60ms）
            segment_size = 960  # 60ms at 16kHz
            segments = []
            for i in range(0, len(audio_data), segment_size):
                segment = audio_data[i:i+segment_size]
                if len(segment) == segment_size:
                    segments.append(segment)

            results = []

            # 处理每个音频片段
            for segment in segments:
                self.chunks.append(segment)
                self.pre_num += 1

                # 预测阶段 - 参考streaming_paraformer.py的预测逻辑
                prediction_result = self._try_prediction()
                if prediction_result:
                    results.append(prediction_result)

                # 最终识别阶段
                final_result = self._try_final_recognition()
                if final_result:
                    results.append(final_result)

            # 返回最后一个有效结果
            return results[-1] if results else None

        except Exception as e:
            logger.error(f"音频识别失败: {e}")
            # 清空缓冲区以避免错误累积
            self._reset_buffers()
            return None
    
    def _try_prediction(self):
        """
        尝试进行预测识别 - 参考streaming_paraformer.py的预测逻辑
        """
        # 优化预测条件，减少过度预测
        if (len(self.chunks) < self.chunk_size_config[1] and
            self.pre_num == self.prediction_interval and
            len(self.chunks) >= 8):  # 确保有足够的音频数据再进行预测

            self.pre_num = 0
            data = np.concatenate(self.chunks)

            # 使用虚拟缓存进行预测，不影响主缓存
            virtual_cache = deepcopy(self.param_dict)
            virtual_cache['is_final'] = False

            try:
                # 进行预测识别
                rec_result = self.model.generate(input=data, cache=virtual_cache.get('cache', {}))
                if rec_result and rec_result[0].get('text'):
                    prediction = rec_result[0]['text']

                    # 使用配置文件中的过滤规则
                    if (prediction and prediction != self.last_prediction and
                        len(prediction.strip()) >= MIN_SENTENCE_LENGTH and
                        not any(prediction.endswith(p) for p in AVOID_SPLIT_PUNCTUATION)):

                        self.last_prediction = prediction
                        return {
                            "type": "preview",
                            "text": prediction.strip()
                        }

            except Exception as e:
                logger.error(f"预测识别失败: {e}")

        elif self.pre_num == 8:  # 重置计数器
            self.pre_num = 0

        return None

    def _try_final_recognition(self):
        """
        尝试进行最终识别 - 参考streaming_paraformer.py的最终识别逻辑
        """
        if len(self.chunks) == self.chunk_size_config[1]:
            data = np.concatenate(self.chunks)

            try:
                # 使用主缓存进行最终识别
                rec_result = self.model.generate(input=data,
                                               cache=self.param_dict.get('cache', {}),
                                               is_final=True)
                if rec_result and rec_result[0].get('text'):
                    text = rec_result[0]['text']

                    # 清理和标准化文字
                    if text:
                        text = text.strip()
                        if text and text[-1] in ascii_letters:
                            text += ' '  # 英文后面加空格

                        # 发送最终结果
                        if len(text) >= 1:  # 至少1个字符才发送
                            self.chunks.clear()  # 清空chunks
                            return {
                                "type": "final",
                                "text": text
                            }

            except Exception as e:
                logger.error(f"最终识别失败: {e}")

            # 清空chunks，无论是否成功
            self.chunks.clear()

        return None

    def _reset_buffers(self):
        """重置所有缓冲区"""
        self.audio_buffer = []
        self.chunks = []
        self.pre_num = 0
        self.last_prediction = ''

    def recognize_chunk_simple(self, audio_data):
        """
        简单识别方法 - 保持与原有接口的兼容性
        只返回文本字符串，用于向后兼容
        """
        result = self.recognize_chunk(audio_data)
        if result and result.get('text'):
            return result['text']
        return None

    def reset(self):
        """重置ASR状态"""
        self.param_dict = {'cache': dict()}
        self._reset_buffers()
        logger.info("ASR状态已重置")