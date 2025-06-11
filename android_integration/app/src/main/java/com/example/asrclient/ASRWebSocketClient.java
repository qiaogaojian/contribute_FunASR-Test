package com.example.asrclient;

import android.util.Log;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;
import java.net.URI;
import java.nio.ByteBuffer;

public class ASRWebSocketClient extends WebSocketClient {
    private static final String TAG = "ASRWebSocketClient";
    private ASRCallback callback;
    private Gson gson;
    private boolean isConnected = false;

    public interface ASRCallback {
        void onConnected();
        void onDisconnected();
        void onRecognitionResult(String text, boolean isFinal);
        void onError(String error);
    }

    public ASRWebSocketClient(String serverUrl, ASRCallback callback) {
        super(URI.create(serverUrl));
        this.callback = callback;
        this.gson = new Gson();
        
        // 设置连接超时
        setConnectionLostTimeout(30);
    }

    @Override
    public void onOpen(ServerHandshake handshake) {
        Log.d(TAG, "WebSocket连接已建立");
        isConnected = true;
        if (callback != null) {
            callback.onConnected();
        }
    }

    @Override
    public void onMessage(String message) {
        Log.d(TAG, "收到消息: " + message);
        try {
            JsonObject jsonObject = gson.fromJson(message, JsonObject.class);
            String type = jsonObject.get("type").getAsString();
            
            switch (type) {
                case "welcome":
                    Log.d(TAG, "收到欢迎消息");
                    break;
                    
                case "asr_result":
                case "recognition_result":
                    handleRecognitionResult(jsonObject);
                    break;
                    
                case "error":
                    String errorMsg = jsonObject.get("error_message").getAsString();
                    if (callback != null) {
                        callback.onError(errorMsg);
                    }
                    break;
                    
                default:
                    Log.d(TAG, "未知消息类型: " + type);
            }
        } catch (Exception e) {
            Log.e(TAG, "解析消息失败", e);
        }
    }

    private void handleRecognitionResult(JsonObject jsonObject) {
        try {
            String text = "";
            boolean isFinal = false;
            
            // 处理不同格式的识别结果
            if (jsonObject.has("result")) {
                JsonObject result = jsonObject.getAsJsonObject("result");
                text = result.get("text").getAsString();
                isFinal = result.get("is_final").getAsBoolean();
            } else {
                text = jsonObject.get("text").getAsString();
                isFinal = jsonObject.get("is_final").getAsBoolean();
            }
            
            if (callback != null) {
                callback.onRecognitionResult(text, isFinal);
            }
        } catch (Exception e) {
            Log.e(TAG, "处理识别结果失败", e);
        }
    }

    @Override
    public void onClose(int code, String reason, boolean remote) {
        Log.d(TAG, "WebSocket连接已关闭: " + reason);
        isConnected = false;
        if (callback != null) {
            callback.onDisconnected();
        }
    }

    @Override
    public void onError(Exception ex) {
        Log.e(TAG, "WebSocket错误", ex);
        if (callback != null) {
            callback.onError(ex.getMessage());
        }
    }

    /**
     * 发送音频数据
     */
    public void sendAudioData(byte[] audioData) {
        if (isConnected && audioData != null && audioData.length > 0) {
            send(audioData);
        }
    }

    /**
     * 发送心跳
     */
    public void sendHeartbeat() {
        if (isConnected) {
            JsonObject ping = new JsonObject();
            ping.addProperty("type", "ping");
            send(ping.toString());
        }
    }

    public boolean isConnected() {
        return isConnected && !isClosed();
    }
}
