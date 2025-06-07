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
chunk_size = [10, 20, 10] # 左回看，片段，右回看，单位 60ms

home_directory = os.path.expanduser("D:/Cache/model/asr")

asr_model_path = os.path.join(home_directory,"iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch")
asr_model_revision = "v2.0.4"
vad_model_path = os.path.join(home_directory,"iic/speech_fsmn_vad_zh-cn-16k-common-pytorch")
vad_model_revision = "v2.0.4"
punc_model_path = os.path.join(home_directory,"iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch")
punc_model_revision = "v2.0.4"
spk_model_path = os.path.join(home_directory,"iic/speech_campplus_sv_zh-cn_16k-common")
spk_model_revision = "v2.0.4"

ngpu = 1
device = "cuda"
ncpu = 4

# ASR 模型
model = AutoModel(model=asr_model_path,
                  model_revision=asr_model_revision,
                  vad_model=vad_model_path,
                  vad_model_revision=vad_model_revision,
                  punc_model=punc_model_path,
                  punc_model_revision=punc_model_revision,
                  spk_model=spk_model_path,
                  spk_model_revision = spk_model_revision,
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
    rec_result = model.generate(input=data, cache=param_dict['cache'], is_final=param_dict['is_final'])
    if len(rec_result) > 0:
       final_result += rec_result[0]["text"]
    if rec_result:
        print(rec_result[0]['text'], end='', flush=True)
print('')
