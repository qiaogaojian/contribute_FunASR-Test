package com.example.asrclient;

import com.google.gson.annotations.SerializedName;
import java.util.List;

/**
 * 会议总结相关的数据模型
 * 对应后端API的数据结构
 */
public class MeetingSummaryModels {

    /**
     * 总结类型枚举
     */
    public enum SummaryType {
        BRIEF("brief", "简要总结", "重点摘要"),
        DETAILED("detailed", "详细总结", "完整分析"),
        ACTION("action", "行动项总结", "待办事项");

        private final String value;
        private final String name;
        private final String description;

        SummaryType(String value, String name, String description) {
            this.value = value;
            this.name = name;
            this.description = description;
        }

        public String getValue() { return value; }
        public String getName() { return name; }
        public String getDescription() { return description; }

        public static SummaryType fromValue(String value) {
            for (SummaryType type : values()) {
                if (type.value.equals(value)) {
                    return type;
                }
            }
            return BRIEF; // 默认值
        }
    }

    /**
     * 会议总结请求模型
     */
    public static class MeetingSummaryRequest {
        @SerializedName("meeting_text")
        private String meetingText;

        @SerializedName("summary_type")
        private String summaryType;

        @SerializedName("model")
        private String model = "gemini-1.5-flash";

        @SerializedName("temperature")
        private float temperature = 0.3f;

        public MeetingSummaryRequest(String meetingText, SummaryType summaryType) {
            this.meetingText = meetingText;
            this.summaryType = summaryType.getValue();
        }

        // Getters and Setters
        public String getMeetingText() { return meetingText; }
        public void setMeetingText(String meetingText) { this.meetingText = meetingText; }

        public String getSummaryType() { return summaryType; }
        public void setSummaryType(String summaryType) { this.summaryType = summaryType; }

        public String getModel() { return model; }
        public void setModel(String model) { this.model = model; }

        public float getTemperature() { return temperature; }
        public void setTemperature(float temperature) { this.temperature = temperature; }
    }

    /**
     * 基础响应模型
     */
    public static class BaseResponse {
        @SerializedName("success")
        private boolean success;

        @SerializedName("message")
        private String message;

        @SerializedName("timestamp")
        private String timestamp;

        // Getters and Setters
        public boolean isSuccess() { return success; }
        public void setSuccess(boolean success) { this.success = success; }

        public String getMessage() { return message; }
        public void setMessage(String message) { this.message = message; }

        public String getTimestamp() { return timestamp; }
        public void setTimestamp(String timestamp) { this.timestamp = timestamp; }
    }

    /**
     * 会议总结响应模型
     */
    public static class MeetingSummaryResponse extends BaseResponse {
        @SerializedName("summary")
        private String summary;

        @SerializedName("summary_type")
        private String summaryType;

        @SerializedName("model")
        private String model;

        @SerializedName("processing_time")
        private float processingTime;

        @SerializedName("optimized_text")
        private String optimizedText;

        // Getters and Setters
        public String getSummary() { return summary; }
        public void setSummary(String summary) { this.summary = summary; }

        public String getSummaryType() { return summaryType; }
        public void setSummaryType(String summaryType) { this.summaryType = summaryType; }

        public String getModel() { return model; }
        public void setModel(String model) { this.model = model; }

        public float getProcessingTime() { return processingTime; }
        public void setProcessingTime(float processingTime) { this.processingTime = processingTime; }

        public String getOptimizedText() { return optimizedText; }
        public void setOptimizedText(String optimizedText) { this.optimizedText = optimizedText; }
    }

    /**
     * 总结类型信息
     */
    public static class SummaryTypeInfo {
        @SerializedName("type")
        private String type;

        @SerializedName("name")
        private String name;

        @SerializedName("description")
        private String description;

        // Getters and Setters
        public String getType() { return type; }
        public void setType(String type) { this.type = type; }

        public String getName() { return name; }
        public void setName(String name) { this.name = name; }

        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
    }

    /**
     * 总结类型列表响应
     */
    public static class SummaryTypesResponse extends BaseResponse {
        @SerializedName("types")
        private List<SummaryTypeInfo> types;

        // Getters and Setters
        public List<SummaryTypeInfo> getTypes() { return types; }
        public void setTypes(List<SummaryTypeInfo> types) { this.types = types; }
    }

    /**
     * 错误响应模型
     */
    public static class ErrorResponse {
        @SerializedName("detail")
        private String detail;

        // Getters and Setters
        public String getDetail() { return detail; }
        public void setDetail(String detail) { this.detail = detail; }
    }

    /**
     * 健康检查响应
     */
    public static class HealthResponse extends BaseResponse {
        @SerializedName("service")
        private String service;

        @SerializedName("version")
        private String version;

        // Getters and Setters
        public String getService() { return service; }
        public void setService(String service) { this.service = service; }

        public String getVersion() { return version; }
        public void setVersion(String version) { this.version = version; }
    }
}
