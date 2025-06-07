import os
import logging
import torch
import soundfile

from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from modelscope.utils.logger import get_logger

logger = get_logger(log_level=logging.CRITICAL)
logger.setLevel(logging.CRITICAL)

os.environ["MODELSCOPE_CACHE"] = "./model"
inference_pipeline = pipeline(
    task=Tasks.auto_speech_recognition,
    model='iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online',
    model_revision='v2.0.4',
)

model_dir = os.path.join(os.environ["MODELSCOPE_CACHE"], "damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online")
speech, sample_rate = soundfile.read(os.path.join(model_dir, "example/asr_example.wav"))
speech_length = speech.shape[0]

sample_offset = 0
chunk_size = [0, 10, 5] #[5, 10, 5] 600ms, [8, 8, 4] 480ms
encoder_chunk_look_back = 4
decoder_chunk_look_back = 1
stride_size =  chunk_size[1] * 960

is_final = False
for sample_offset in range(0, speech_length, min(stride_size, speech_length - sample_offset)):
    if sample_offset + stride_size >= speech_length - 1:
        stride_size = speech_length - sample_offset
        is_final = True

    res = inference_pipeline(speech[sample_offset: sample_offset + stride_size], cache=cache, is_final=is_final, encoder_chunk_look_back=encoder_chunk_look_back, decoder_chunk_look_back=decoder_chunk_look_back)
    if len(res[0]["value"]):
        print(res)
