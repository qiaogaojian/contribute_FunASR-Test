package com.example.asrclient;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

public class ASRManager implements ASRWebSocketClient.ASRCallback, AudioRecordManager.AudioDataCallback {
    private static final String TAG = "ASRManager";
    private static final long HEARTBEAT_INTERVAL = 30000; // 30秒心跳间隔
    
    private Context context;
    private ASRWebSocketClient webSocketClient;
    private AudioRecordManager audioRecordManager;
    private ASRListener listener;
    private Handler mainHandler;
    private Handler heartbeatHandler;
    private Runnable heartbeatRunnable;
    
    // 服务器配置
    private String serverHost = "192.168.1.163"; // 替换为您的服务器IP
    private int serverPort = 8000;
    private String configName = "meeting"; // 使用meeting配置

    public interface ASRListener {
        void onConnected();
        void onDisconnected();
        void onRecognitionResult(String text, boolean isFinal);
        void onError(String error);
        void onRecordingStarted();
        void onRecordingStopped();
    }

    public ASRManager(Context context, ASRListener listener) {
        this.context = context;
        this.listener = listener;
        this.mainHandler = new Handler(Looper.getMainLooper());
        this.heartbeatHandler = new Handler(Looper.getMainLooper());
        
        // 初始化音频录制管理器
        this.audioRecordManager = new AudioRecordManager(context, this);
        
        // 初始化心跳任务
        this.heartbeatRunnable = new Runnable() {
            @Override
            public void run() {
                if (webSocketClient != null && webSocketClient.isConnected()) {
                    webSocketClient.sendHeartbeat();
                    heartbeatHandler.postDelayed(this, HEARTBEAT_INTERVAL);
                }
            }
        };
    }

    /**
     * 连接到ASR服务器
     */
    public void connect() {
        if (webSocketClient != null && webSocketClient.isConnected()) {
            Log.w(TAG, "已经连接到服务器");
            return;
        }

        try {
            String wsUrl = String.format("ws://%s:%d/ws/audio?config_name=%s", 
                serverHost, serverPort, configName);
            
            Log.d(TAG, "连接到: " + wsUrl);
            
            webSocketClient = new ASRWebSocketClient(wsUrl, this);
            webSocketClient.connect();
            
        } catch (Exception e) {
            Log.e(TAG, "连接失败", e);
            notifyError("连接失败: " + e.getMessage());
        }
    }

    /**
     * 断开连接
     */
    public void disconnect() {
        // 停止录音
        stopRecording();
        
        // 停止心跳
        heartbeatHandler.removeCallbacks(heartbeatRunnable);
        
        // 关闭WebSocket连接
        if (webSocketClient != null) {
            webSocketClient.close();
            webSocketClient = null;
        }
    }

    /**
     * 开始录音和识别
     */
    public boolean startRecording() {
        if (!isConnected()) {
            notifyError("未连接到服务器");
            return false;
        }

        boolean success = audioRecordManager.startRecording();
        if (success && listener != null) {
            mainHandler.post(() -> listener.onRecordingStarted());
        }
        return success;
    }

    /**
     * 停止录音
     */
    public void stopRecording() {
        audioRecordManager.stopRecording();
        if (listener != null) {
            mainHandler.post(() -> listener.onRecordingStopped());
        }
    }

    /**
     * 设置服务器地址
     */
    public void setServerAddress(String host, int port) {
        this.serverHost = host;
        this.serverPort = port;
    }

    /**
     * 设置ASR配置
     */
    public void setConfigName(String configName) {
        this.configName = configName;
    }

    public boolean isConnected() {
        return webSocketClient != null && webSocketClient.isConnected();
    }

    public boolean isRecording() {
        return audioRecordManager.isRecording();
    }

    /**
     * 释放资源
     */
    public void release() {
        disconnect();
        audioRecordManager.release();
    }

    // WebSocket回调方法
    @Override
    public void onConnected() {
        Log.d(TAG, "WebSocket连接成功");
        // 启动心跳
        heartbeatHandler.post(heartbeatRunnable);
        
        if (listener != null) {
            mainHandler.post(() -> listener.onConnected());
        }
    }

    @Override
    public void onDisconnected() {
        Log.d(TAG, "WebSocket连接断开");
        // 停止心跳
        heartbeatHandler.removeCallbacks(heartbeatRunnable);
        
        if (listener != null) {
            mainHandler.post(() -> listener.onDisconnected());
        }
    }

    @Override
    public void onRecognitionResult(String text, boolean isFinal) {
        Log.d(TAG, "识别结果: " + text + " (final: " + isFinal + ")");
        if (listener != null) {
            mainHandler.post(() -> listener.onRecognitionResult(text, isFinal));
        }
    }

    @Override
    public void onError(String error) {
        notifyError(error);
    }

    // 音频数据回调方法
    @Override
    public void onAudioData(byte[] audioData) {
        if (webSocketClient != null && webSocketClient.isConnected()) {
            webSocketClient.sendAudioData(audioData);
        }
    }

    private void notifyError(String error) {
        Log.e(TAG, "错误: " + error);
        if (listener != null) {
            mainHandler.post(() -> listener.onError(error));
        }
    }
}
