package com.example.asrclient;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageManager;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.util.Log;
import androidx.core.content.ContextCompat;

/**
 * 音频诊断工具类
 * 用于检测设备音频录制能力和配置兼容性
 */
public class AudioDiagnostics {
    private static final String TAG = "AudioDiagnostics";

    public static class DiagnosticResult {
        public boolean permissionGranted;
        public boolean audioRecordSupported;
        public String supportedConfig;
        public String errorMessage;
        public String deviceInfo;

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            sb.append("音频诊断结果:\n");
            sb.append("权限状态: ").append(permissionGranted ? "已授予" : "未授予").append("\n");
            sb.append("录音支持: ").append(audioRecordSupported ? "支持" : "不支持").append("\n");
            sb.append("支持的配置: ").append(supportedConfig != null ? supportedConfig : "无").append("\n");
            sb.append("设备信息: ").append(deviceInfo).append("\n");
            if (errorMessage != null) {
                sb.append("错误信息: ").append(errorMessage).append("\n");
            }
            return sb.toString();
        }
    }

    /**
     * 执行完整的音频诊断
     */
    public static DiagnosticResult runDiagnostics(Context context) {
        DiagnosticResult result = new DiagnosticResult();
        
        // 检查权限
        result.permissionGranted = checkPermission(context);
        
        // 获取设备信息
        result.deviceInfo = getDeviceInfo();
        
        // 测试音频录制
        if (result.permissionGranted) {
            testAudioRecord(result);
        } else {
            result.errorMessage = "录音权限未授予";
        }
        
        return result;
    }

    private static boolean checkPermission(Context context) {
        return ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) 
                == PackageManager.PERMISSION_GRANTED;
    }

    private static String getDeviceInfo() {
        return String.format("设备: %s %s, Android: %s", 
            android.os.Build.MANUFACTURER, 
            android.os.Build.MODEL, 
            android.os.Build.VERSION.RELEASE);
    }

    private static void testAudioRecord(DiagnosticResult result) {
        // 测试配置列表
        AudioConfig[] configs = {
            new AudioConfig("16kHz单声道16bit", 16000, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT),
            new AudioConfig("8kHz单声道16bit", 8000, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT),
            new AudioConfig("44.1kHz单声道16bit", 44100, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT),
            new AudioConfig("16kHz立体声16bit", 16000, AudioFormat.CHANNEL_IN_STEREO, AudioFormat.ENCODING_PCM_16BIT),
            new AudioConfig("22kHz单声道16bit", 22050, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT)
        };

        StringBuilder supportedConfigs = new StringBuilder();
        boolean anySupported = false;

        for (AudioConfig config : configs) {
            if (testSingleConfig(config)) {
                if (anySupported) {
                    supportedConfigs.append(", ");
                }
                supportedConfigs.append(config.name);
                anySupported = true;
                
                // 第一个支持的配置作为推荐配置
                if (result.supportedConfig == null) {
                    result.supportedConfig = config.name;
                }
            }
        }

        result.audioRecordSupported = anySupported;
        if (anySupported) {
            result.supportedConfig = supportedConfigs.toString();
        } else {
            result.errorMessage = "设备不支持任何测试的音频配置";
        }
    }

    private static boolean testSingleConfig(AudioConfig config) {
        AudioRecord audioRecord = null;
        try {
            // 检查最小缓冲区大小
            int minBufferSize = AudioRecord.getMinBufferSize(
                config.sampleRate, config.channelConfig, config.audioFormat);
            
            if (minBufferSize == AudioRecord.ERROR || minBufferSize == AudioRecord.ERROR_BAD_VALUE) {
                Log.d(TAG, "配置不支持 (缓冲区): " + config.name);
                return false;
            }

            // 尝试创建 AudioRecord
            audioRecord = new AudioRecord(
                MediaRecorder.AudioSource.MIC,
                config.sampleRate,
                config.channelConfig,
                config.audioFormat,
                minBufferSize * 2
            );

            boolean supported = audioRecord.getState() == AudioRecord.STATE_INITIALIZED;
            Log.d(TAG, "配置测试 " + config.name + ": " + (supported ? "支持" : "不支持"));
            
            return supported;

        } catch (Exception e) {
            Log.d(TAG, "配置测试异常 " + config.name + ": " + e.getMessage());
            return false;
        } finally {
            if (audioRecord != null) {
                try {
                    audioRecord.release();
                } catch (Exception e) {
                    // 忽略释放异常
                }
            }
        }
    }

    private static class AudioConfig {
        final String name;
        final int sampleRate;
        final int channelConfig;
        final int audioFormat;

        AudioConfig(String name, int sampleRate, int channelConfig, int audioFormat) {
            this.name = name;
            this.sampleRate = sampleRate;
            this.channelConfig = channelConfig;
            this.audioFormat = audioFormat;
        }
    }

    /**
     * 快速检查音频录制是否可用
     */
    public static boolean isAudioRecordAvailable(Context context) {
        if (!checkPermission(context)) {
            return false;
        }

        AudioRecord audioRecord = null;
        try {
            int minBufferSize = AudioRecord.getMinBufferSize(
                16000, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT);
            
            if (minBufferSize == AudioRecord.ERROR || minBufferSize == AudioRecord.ERROR_BAD_VALUE) {
                return false;
            }

            audioRecord = new AudioRecord(
                MediaRecorder.AudioSource.MIC,
                16000,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT,
                minBufferSize * 2
            );

            return audioRecord.getState() == AudioRecord.STATE_INITIALIZED;

        } catch (Exception e) {
            return false;
        } finally {
            if (audioRecord != null) {
                try {
                    audioRecord.release();
                } catch (Exception e) {
                    // 忽略释放异常
                }
            }
        }
    }
}
