package com.example.asrclient;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageManager;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.util.Log;
import androidx.core.content.ContextCompat;
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
    private Context context;
    private int bufferSize;

    public interface AudioDataCallback {
        void onAudioData(byte[] audioData);
        void onError(String error);
    }

    public AudioRecordManager(Context context, AudioDataCallback callback) {
        this.context = context;
        this.callback = callback;
        initAudioRecord();
    }

    private void initAudioRecord() {
        // 检查录音权限
        if (!checkRecordPermission()) {
            Log.e(TAG, "录音权限未授予");
            if (callback != null) {
                callback.onError("录音权限未授予，请在设置中开启录音权限");
            }
            return;
        }

        // 尝试多种配置，提高兼容性
        AudioConfig[] configs = {
            // 首选配置：16kHz, 单声道, 16bit
            new AudioConfig(16000, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT),
            // 备选配置1：8kHz, 单声道, 16bit
            new AudioConfig(8000, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT),
            // 备选配置2：44.1kHz, 单声道, 16bit
            new AudioConfig(44100, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT),
            // 备选配置3：16kHz, 立体声, 16bit
            new AudioConfig(16000, AudioFormat.CHANNEL_IN_STEREO, AudioFormat.ENCODING_PCM_16BIT)
        };

        for (AudioConfig config : configs) {
            if (tryInitWithConfig(config)) {
                Log.d(TAG, "AudioRecord 初始化成功，使用配置: " + config.toString());
                return;
            }
        }

        // 所有配置都失败
        Log.e(TAG, "所有音频配置都初始化失败");
        if (callback != null) {
            callback.onError("音频录制初始化失败：设备不支持任何音频配置");
        }
    }

    private boolean checkRecordPermission() {
        if (context == null) {
            return false;
        }
        return ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO)
                == PackageManager.PERMISSION_GRANTED;
    }

    private boolean tryInitWithConfig(AudioConfig config) {
        try {
            // 计算缓冲区大小
            int minBufferSize = AudioRecord.getMinBufferSize(
                config.sampleRate, config.channelConfig, config.audioFormat);

            if (minBufferSize == AudioRecord.ERROR || minBufferSize == AudioRecord.ERROR_BAD_VALUE) {
                Log.w(TAG, "配置不支持: " + config.toString());
                return false;
            }

            // 使用较大的缓冲区以确保稳定性
            bufferSize = minBufferSize * BUFFER_SIZE_FACTOR;

            // 创建 AudioRecord 实例
            audioRecord = new AudioRecord(
                MediaRecorder.AudioSource.MIC,
                config.sampleRate,
                config.channelConfig,
                config.audioFormat,
                bufferSize
            );

            if (audioRecord.getState() == AudioRecord.STATE_INITIALIZED) {
                Log.d(TAG, "AudioRecord 初始化成功，缓冲区大小: " + bufferSize);
                return true;
            } else {
                Log.w(TAG, "AudioRecord 状态异常: " + audioRecord.getState());
                if (audioRecord != null) {
                    audioRecord.release();
                    audioRecord = null;
                }
                return false;
            }

        } catch (Exception e) {
            Log.w(TAG, "配置初始化失败: " + config.toString(), e);
            if (audioRecord != null) {
                try {
                    audioRecord.release();
                } catch (Exception ex) {
                    // 忽略释放异常
                }
                audioRecord = null;
            }
            return false;
        }
    }

    // 音频配置类
    private static class AudioConfig {
        final int sampleRate;
        final int channelConfig;
        final int audioFormat;

        AudioConfig(int sampleRate, int channelConfig, int audioFormat) {
            this.sampleRate = sampleRate;
            this.channelConfig = channelConfig;
            this.audioFormat = audioFormat;
        }

        @Override
        public String toString() {
            return String.format("AudioConfig{sampleRate=%d, channelConfig=%d, audioFormat=%d}",
                sampleRate, channelConfig, audioFormat);
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

        if (audioRecord == null) {
            Log.e(TAG, "AudioRecord 对象为 null，请检查初始化");
            if (callback != null) {
                callback.onError("音频录制器未初始化，请重启应用或检查权限");
            }
            return false;
        }

        if (audioRecord.getState() != AudioRecord.STATE_INITIALIZED) {
            Log.e(TAG, "AudioRecord 状态异常: " + audioRecord.getState());
            if (callback != null) {
                callback.onError("音频录制器状态异常，请检查设备兼容性");
            }
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
