import os
import soundfile
from funasr import AutoModel
from pathlib import Path
import subprocess
import wave
import numpy as np
import time

# 先用 ffmpeg 转格式
file_path = 'audio/out.mp3'
wav_path = 'audio/input.mp3'
command = ['ffmpeg', '-y', '-i', file_path, '-ar', '16000', '-ac', '1', wav_path]
subprocess.run(command, capture_output=True)

# 载入模型
chunk_size = [20, 40, 20] # 左回看，片段，右回看，单位 60ms


home_directory = os.path.expanduser("D:/Cache/model/asr")
# https://www.modelscope.cn/models/iic/SenseVoiceSmall
asr_model_path = os.path.join(home_directory, "models--FunAudioLLM--SenseVoiceSmall/snapshots/3eb3b4eeffc2f2dde6051b853983753db33e35c3")
asr_model_revision = "v2.0.4"
vad_model_path = os.path.join(home_directory,"iic/speech_fsmn_vad_zh-cn-16k-common-pytorch")
vad_model_revision = "v2.0.4"
punc_model_path = os.path.join(home_directory,"iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch")
punc_model_revision = "v2.0.4"
# SenseVoiceSmall 不需要说话人分离模型
spk_model_path = os.path.join(home_directory,"iic/speech_campplus_sv_zh-cn_16k-common")
spk_model_revision = "v2.0.4"

ngpu = 1
device = "cuda"
ncpu = 4

# ASR 模型 - SenseVoiceSmall 不支持时间戳和说话人分离，简化配置
model = AutoModel(model=asr_model_path,
                  model_revision=asr_model_revision,
                  vad_model=vad_model_path,
                  vad_model_revision=vad_model_revision,
                  punc_model=punc_model_path,
                  punc_model_revision=punc_model_revision,
                  # 移除 spk_model 配置，SenseVoiceSmall 不支持说话人分离
                  # spk_model=spk_model_path,
                  # spk_model_revision = spk_model_revision,
                  ngpu=ngpu,
                  ncpu=ncpu,
                  device=device,
                  disable_pbar=True,
                  disable_log=True,
                  disable_update=True
                  )

##online asr
print('开始识别了')
print(f'chunk_size: {chunk_size}')
speech, sample_rate = soundfile.read(wav_path)
speech_length = speech.shape[0]
sample_offset = 0
step = chunk_size[1] * 960
param_dict = {'cache': dict()}
final_result = ""
for sample_offset in range(0, speech_length, min(step, speech_length - sample_offset)):
    if sample_offset + step >= speech_length - 1:
        step = speech_length - sample_offset
        is_final = True
    else:
        is_final = False
    param_dict['is_final'] = is_final
    data = speech[sample_offset: sample_offset + step]
    data = data.astype(np.float32)
    # 将第 63 行的调用方式：
    # rec_result = model.generate(input=data, cache=param_dict['cache'], is_final=param_dict['is_final'])
    
    # 修改为：
    # rec_result = model.generate(input=data, cache=param_dict.get('cache', {}), is_final=param_dict['is_final'])
    
    # 或者完全按照 01 文件的方式（推荐）：
    rec_result = model.generate(input=data, cache=param_dict.get('cache', {}))
    if len(rec_result) > 0:
       final_result += rec_result[0]["text"]
    if rec_result:
        print(rec_result[0]['text'], end='', flush=True)
print('')
