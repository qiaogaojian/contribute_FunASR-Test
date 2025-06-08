import sys 
import time
import wave
import socket
from multiprocessing import Process, Queue 
from string import ascii_letters
from copy import deepcopy

import numpy as np
import sounddevice as sd
from rich.console import Console
# from funasr_onnx.paraformer_online_bin import Paraformer
import colorama; colorama.init()
console = Console()
import signal 
from funasr import AutoModel

# paraformer 的单位片段长 60ms，在 16000 采样率下，就是 960 个采样
# 它的 chunk_size ，如果设为 [10, 20, 10]
# 就表示左回看 10 个片段，总长度 20 片段，右回看 10 片段
# 20 个片段，也就是 1.2s

# 它的每一个流，是保存在一个字典中，即 param_dict 
# 每次解析，都会修改 param_dict 这个词典

# 将识别到的文字从 udp 端口发送
udp_port = 6009

# 一行最多显示多少宽度（每个中文宽度为2，英文字母宽度为1）
line_width = 50

# 在 recognize 函数开始处添加
from modelscope import snapshot_download
import os


# home_directory = os.path.expanduser("~")
# asr_model_path = os.path.join(home_directory, ".cache", "modelscope", "hub", "models", "iic", "speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch")

home_directory = os.path.expanduser("D:/Cache/model/asr")
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

# 检查模型是否存在，不存在则下载
# model_dir = asr_model_path
# if not os.path.exists(os.path.join(model_dir, 'configuration.json')):
#     print("正在下载模型文件...")
#     snapshot_download('iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch', 
#                         cache_dir=home_directory)

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

def recognize(queue_in: Queue, queue_out: Queue):     
    # 创建一个 udp socket，用于实时发送文字
    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    chunk_size = [10, 50, 10] # 左回看数，总片段数，右回看数。每片段长 60ms

    # 通知主进程，可以开始了
    queue_out.put(True)

    # 每攒够 5 个片段，就预测一下虚文字
    pre_num = 0; pre_expect = 10
    printed_num = 0   # 记录一行已输出多少个字
    chunks = []
    param_dict = {'cache': dict()}
    行缓冲 = ''
    旧预测 = ''
    while instruction := queue_in.get() :
        match instruction['type']:
            case 'feed':
                # 吃下片段
                chunks.append(instruction['samples'])
                pre_num += 1

                # 显示虚文字
                if len(chunks) < chunk_size[1] and pre_num == pre_expect and queue_in.qsize() < 3:
                    pre_num = 0
                    data = np.concatenate(chunks)
                    虚字典 = deepcopy(param_dict)
                    虚字典['is_final'] = True 

                    # 修改推理调用方式
                    rec_result = model.generate(input=data, cache=虚字典.get('cache', {}))
                    if rec_result and rec_result[0].get('text'):
                        预测 = rec_result[0]['text']
                        if 预测 and 预测 != 旧预测: 
                            旧预测 = 预测
                            sk.sendto((行缓冲+预测).encode('utf-8'), ('127.0.0.1', udp_port))  # 网络发送
                            print(f'\033[0K\033[32m{行缓冲}\033[33m{预测}\033[0m',             # 控制台打印
                                  end=f'\033[0G', flush=True)
                elif pre_num == 5: pre_num = 0

                # 显示实文字
                if len(chunks) == chunk_size[1]:
                    data = np.concatenate(chunks)
                    rec_result = model.generate(input=data, cache=param_dict.get('cache', {}))
                    if rec_result and rec_result[0].get('text'):
                        文字 = rec_result[0]['text']                   # 得到文字
                        if 文字 and 文字[-1] in ascii_letters: 文字 += ' '  # 英文后面加空格
                        行缓冲 += 文字                                      # 加入缓冲
                        sk.sendto(行缓冲.encode('utf-8'), ('127.0.0.1', udp_port))           # 网络发送
                        print(f'\033[0K\033[32m{行缓冲}\033[0m', end='\033[0G', flush=True)  # 控制台打印
                        printed_num += len(文字.encode('gbk'))              # 统计数字
                        if printed_num >= line_width: print(''); 行缓冲 = ''; printed_num=0    # 每到长度极限，就清空换行
                    chunks.clear()

            case 'end': 
                if not chunks:
                    chunks.append(np.zeros(960, dtype=np.float32))
                data = np.concatenate(chunks)
                rec_result = model.generate(input=data, cache=param_dict.get('cache', {}))
                if rec_result and rec_result[0].get('text'): 
                    print(rec_result[0]['text'], end='', flush=True)
                chunks.clear()
                param_dict = {'cache': dict()}
                print('\n\n')
                
        

def record_callback(indata: np.ndarray, 
                    frames: int, time_info, 
                    status: sd.CallbackFlags) -> None:
    
    # 转成单声道、16000采样率
    data = np.mean(indata.copy()[::3], axis=1)

    # 放入队列
    queue_in.put({'type':'feed', 'samples':data})

    # 保存音频
    f.writeframes((data * (2**15-1)).astype(np.int16).tobytes())


    
def main():

    def signal_handler(sig, frame): print("\n\033[31m收到中断信号 Ctrl+C，退出程序\033[0m"); sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    global queue_in, queue_out
    queue_in = Queue()
    queue_out = Queue()
    process = Process(target=recognize, args=[queue_in, queue_out], daemon=True)
    process.start()

    # 等待模型加载完
    print('正在加载语音模型');queue_out.get()
    print(f'模型加载完成\n\n')

    try:
        device = sd.query_devices(kind='input')
        channels = device['max_input_channels']
        console.print(f'使用默认音频设备：[italic]{device["name"]}', end='\n\n')
    except UnicodeDecodeError:
        console.print("由于编码问题，暂时无法获得麦克风设备名字", end='\n\n', style='bright_red')
    except sd.PortAudioError:
        console.print("没有找到麦克风设备", end='\n\n', style='bright_red')
        input('按回车键退出'); sys.exit()
    
    # 将音频保存到 wav，以作检查用
    global f
    f = wave.open('audio/out.wav', 'w')
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(16000)

    # 我们原生录制的是 48000 采样率的，便于以后保存高品质录音
    # 可后续处理为 16000 采样率
    stream = sd.InputStream(
        channels=1,
        dtype="float32",
        samplerate=48000,
        blocksize=int(3 * 960),  # 0.06 seconds
        callback=record_callback
    ); stream.start()

    print('开始了')
    while True:
        input()
        queue_in.put({'type': 'end'})

if __name__ == '__main__':
    main()



