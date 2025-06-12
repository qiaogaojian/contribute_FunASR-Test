package com.example.asrclient;

import android.util.Log;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import java.io.IOException;
import java.util.concurrent.TimeUnit;
import okhttp3.*;

/**
 * 会议总结API客户端
 * 负责与后端会议总结API进行通信
 */
public class MeetingSummaryApiClient {
    private static final String TAG = "MeetingSummaryApiClient";
    private static final int TIMEOUT_SECONDS = 60; // 60秒超时，因为LLM处理需要时间

    private OkHttpClient httpClient;
    private Gson gson;
    private String baseUrl;

    public interface ApiCallback<T> {
        void onSuccess(T result);
        void onError(String error);
    }

    public MeetingSummaryApiClient(String serverHost, int serverPort) {
        this.baseUrl = String.format("http://%s:%d", serverHost, serverPort);
        
        // 配置HTTP客户端
        this.httpClient = new OkHttpClient.Builder()
                .connectTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
                .readTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
                .writeTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
                .build();

        // 配置JSON解析器
        this.gson = new GsonBuilder()
                .setLenient()
                .create();
    }

    /**
     * 生成会议总结
     */
    public void generateMeetingSummary(
            String meetingText,
            MeetingSummaryModels.SummaryType summaryType,
            ApiCallback<MeetingSummaryModels.MeetingSummaryResponse> callback) {

        // 创建请求数据
        MeetingSummaryModels.MeetingSummaryRequest request = 
                new MeetingSummaryModels.MeetingSummaryRequest(meetingText, summaryType);

        String jsonBody = gson.toJson(request);
        Log.d(TAG, "发送会议总结请求: " + summaryType.getName());

        RequestBody body = RequestBody.create(
                jsonBody, 
                MediaType.get("application/json; charset=utf-8")
        );

        Request httpRequest = new Request.Builder()
                .url(baseUrl + "/api/meeting/summary")
                .post(body)
                .build();

        httpClient.newCall(httpRequest).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e(TAG, "网络请求失败", e);
                callback.onError("网络请求失败: " + e.getMessage());
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                try {
                    String responseBody = response.body().string();
                    Log.d(TAG, "收到响应: " + response.code());

                    if (response.isSuccessful()) {
                        MeetingSummaryModels.MeetingSummaryResponse summaryResponse = 
                                gson.fromJson(responseBody, MeetingSummaryModels.MeetingSummaryResponse.class);
                        
                        Log.d(TAG, "会议总结生成成功，处理时间: " + summaryResponse.getProcessingTime() + "秒");
                        callback.onSuccess(summaryResponse);
                    } else {
                        // 解析错误响应
                        try {
                            MeetingSummaryModels.ErrorResponse errorResponse = 
                                    gson.fromJson(responseBody, MeetingSummaryModels.ErrorResponse.class);
                            callback.onError("服务器错误: " + errorResponse.getDetail());
                        } catch (Exception e) {
                            callback.onError("服务器错误 (HTTP " + response.code() + "): " + responseBody);
                        }
                    }
                } catch (Exception e) {
                    Log.e(TAG, "响应解析失败", e);
                    callback.onError("响应解析失败: " + e.getMessage());
                }
            }
        });
    }

    /**
     * 获取支持的总结类型列表
     */
    public void getSummaryTypes(ApiCallback<MeetingSummaryModels.SummaryTypesResponse> callback) {
        Request request = new Request.Builder()
                .url(baseUrl + "/api/meeting/summary/types")
                .get()
                .build();

        httpClient.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e(TAG, "获取总结类型失败", e);
                callback.onError("网络请求失败: " + e.getMessage());
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                try {
                    String responseBody = response.body().string();
                    
                    if (response.isSuccessful()) {
                        MeetingSummaryModels.SummaryTypesResponse typesResponse = 
                                gson.fromJson(responseBody, MeetingSummaryModels.SummaryTypesResponse.class);
                        callback.onSuccess(typesResponse);
                    } else {
                        callback.onError("服务器错误 (HTTP " + response.code() + ")");
                    }
                } catch (Exception e) {
                    Log.e(TAG, "响应解析失败", e);
                    callback.onError("响应解析失败: " + e.getMessage());
                }
            }
        });
    }

    /**
     * 健康检查
     */
    public void checkHealth(ApiCallback<MeetingSummaryModels.HealthResponse> callback) {
        Request request = new Request.Builder()
                .url(baseUrl + "/api/meeting/health")
                .get()
                .build();

        httpClient.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e(TAG, "健康检查失败", e);
                callback.onError("网络请求失败: " + e.getMessage());
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                try {
                    String responseBody = response.body().string();
                    
                    if (response.isSuccessful()) {
                        MeetingSummaryModels.HealthResponse healthResponse = 
                                gson.fromJson(responseBody, MeetingSummaryModels.HealthResponse.class);
                        callback.onSuccess(healthResponse);
                    } else {
                        callback.onError("服务器错误 (HTTP " + response.code() + ")");
                    }
                } catch (Exception e) {
                    Log.e(TAG, "响应解析失败", e);
                    callback.onError("响应解析失败: " + e.getMessage());
                }
            }
        });
    }

    /**
     * 更新服务器地址
     */
    public void updateServerAddress(String serverHost, int serverPort) {
        this.baseUrl = String.format("http://%s:%d", serverHost, serverPort);
        Log.d(TAG, "更新服务器地址: " + baseUrl);
    }

    /**
     * 释放资源
     */
    public void release() {
        if (httpClient != null) {
            httpClient.dispatcher().executorService().shutdown();
            httpClient.connectionPool().evictAll();
        }
    }
}
