package com.example.asrclient;

import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.util.Log;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

public class AudioRecordManager {
    private static final String TAG = "AudioRecordManager";
    
    // 音频参数 - 与服务器端保持一致
    private static final int SAMPLE_RATE = 16000;
    private static final int CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO;
    private static final int AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT;
    private static final int BUFFER_SIZE_FACTOR = 2;
    
    private AudioRecord audioRecord;
    private boolean isRecording = false;
    private Thread recordingThread;
    private AudioDataCallback callback;
    private int bufferSize;

    public interface AudioDataCallback {
        void onAudioData(byte[] audioData);
        void onError(String error);
    }

    public AudioRecordManager(AudioDataCallback callback) {
        this.callback = callback;
        initAudioRecord();
    }

    private void initAudioRecord() {
        try {
            // 计算缓冲区大小
            bufferSize = AudioRecord.getMinBufferSize(SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT);
            if (bufferSize == AudioRecord.ERROR || bufferSize == AudioRecord.ERROR_BAD_VALUE) {
                throw new RuntimeException("无法获取音频缓冲区大小");
            }
            
            // 使用较大的缓冲区以确保稳定性
            bufferSize *= BUFFER_SIZE_FACTOR;
            
            // 创建 AudioRecord 实例
            audioRecord = new AudioRecord(
                MediaRecorder.AudioSource.MIC,
                SAMPLE_RATE,
                CHANNEL_CONFIG,
                AUDIO_FORMAT,
                bufferSize
            );
            
            if (audioRecord.getState() != AudioRecord.STATE_INITIALIZED) {
                throw new RuntimeException("AudioRecord 初始化失败");
            }
            
            Log.d(TAG, "AudioRecord 初始化成功，缓冲区大小: " + bufferSize);
            
        } catch (Exception e) {
            Log.e(TAG, "AudioRecord 初始化失败", e);
            if (callback != null) {
                callback.onError("音频录制初始化失败: " + e.getMessage());
            }
        }
    }

    /**
     * 开始录音
     */
    public synchronized boolean startRecording() {
        if (isRecording) {
            Log.w(TAG, "录音已在进行中");
            return false;
        }

        if (audioRecord == null || audioRecord.getState() != AudioRecord.STATE_INITIALIZED) {
            Log.e(TAG, "AudioRecord 未正确初始化");
            return false;
        }

        try {
            audioRecord.startRecording();
            isRecording = true;
            
            // 启动录音线程
            recordingThread = new Thread(this::recordingLoop, "AudioRecordThread");
            recordingThread.start();
            
            Log.d(TAG, "开始录音");
            return true;
            
        } catch (Exception e) {
            Log.e(TAG, "启动录音失败", e);
            if (callback != null) {
                callback.onError("启动录音失败: " + e.getMessage());
            }
            return false;
        }
    }

    /**
     * 停止录音
     */
    public synchronized void stopRecording() {
        if (!isRecording) {
            return;
        }

        isRecording = false;
        
        try {
            if (audioRecord != null) {
                audioRecord.stop();
            }
            
            if (recordingThread != null) {
                recordingThread.interrupt();
                recordingThread = null;
            }
            
            Log.d(TAG, "停止录音");
            
        } catch (Exception e) {
            Log.e(TAG, "停止录音失败", e);
        }
    }

    /**
     * 录音循环
     */
    private void recordingLoop() {
        byte[] buffer = new byte[bufferSize];
        
        while (isRecording && !Thread.currentThread().isInterrupted()) {
            try {
                int bytesRead = audioRecord.read(buffer, 0, buffer.length);
                
                if (bytesRead > 0) {
                    // 创建实际大小的数组
                    byte[] audioData = new byte[bytesRead];
                    System.arraycopy(buffer, 0, audioData, 0, bytesRead);
                    
                    // 回调音频数据
                    if (callback != null) {
                        callback.onAudioData(audioData);
                    }
                } else if (bytesRead < 0) {
                    Log.e(TAG, "读取音频数据错误: " + bytesRead);
                    break;
                }
                
            } catch (Exception e) {
                Log.e(TAG, "录音循环异常", e);
                break;
            }
        }
    }

    /**
     * 释放资源
     */
    public void release() {
        stopRecording();
        
        if (audioRecord != null) {
            try {
                audioRecord.release();
                audioRecord = null;
            } catch (Exception e) {
                Log.e(TAG, "释放 AudioRecord 失败", e);
            }
        }
    }

    public boolean isRecording() {
        return isRecording;
    }
}
