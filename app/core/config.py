#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置管理
基于Pydantic的配置系统，支持环境变量
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置设置"""
    
    # 应用基础配置
    app_name: str = Field(default="ASR Service", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    
    # 服务配置
    host: str = Field(default="0.0.0.0", description="服务监听地址")
    port: int = Field(default=8000, description="HTTP服务端口")
    
    # WebSocket配置
    websocket_host: str = Field(default="0.0.0.0", description="WebSocket监听地址")
    websocket_port: int = Field(default=8766, description="WebSocket端口")
    
    # CORS配置
    cors_origins: List[str] = Field(default=["*"], description="允许的CORS源")
    
    # ASR配置
    asr_model_path: str = Field(
        default="iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
        description="ASR模型路径"
    )
    vad_model_path: str = Field(
        default="iic/speech_fsmn_vad_zh-cn-16k-common-pytorch",
        description="VAD模型路径"
    )
    punc_model_path: str = Field(
        default="iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
        description="标点模型路径"
    )
    spk_model_path: str = Field(
        default="iic/speech_campplus_sv_zh-cn_16k-common",
        description="说话人模型路径"
    )
    
    # 默认ASR配置
    default_asr_config: str = Field(default="balanced", description="默认ASR配置名称")
    asr_device: str = Field(default="cuda", description="ASR设备")
    asr_ncpu: int = Field(default=4, description="CPU核心数")
    asr_ngpu: int = Field(default=1, description="GPU数量")
    
    # 音频配置
    default_sample_rate: int = Field(default=16000, description="默认采样率")
    max_audio_duration: int = Field(default=3600, description="最大音频时长（秒）")
    
    # 会话配置
    session_timeout_minutes: int = Field(default=30, description="会话超时时间（分钟）")
    max_sessions_per_client: int = Field(default=5, description="每客户端最大会话数")
    
    # 文件上传配置
    upload_dir: str = Field(default="uploads", description="上传目录")
    max_file_size: int = Field(default=100, description="最大文件大小（MB）")
    allowed_audio_formats: List[str] = Field(
        default=["wav", "mp3", "flac", "m4a"], 
        description="允许的音频格式"
    )
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="日志格式")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # 环境变量前缀
        env_prefix = "ASR_"
    
    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.debug
    
    def get_upload_path(self) -> str:
        """获取上传路径"""
        upload_path = os.path.abspath(self.upload_dir)
        os.makedirs(upload_path, exist_ok=True)
        return upload_path


# 全局设置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取设置实例（单例模式）"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """重新加载设置"""
    global _settings
    _settings = Settings()
    return _settings
