package com.example.asrclient;

import android.util.Log;

/**
 * 会议总结测试辅助类
 * 提供测试数据和辅助方法
 */
public class MeetingSummaryTestHelper {
    private static final String TAG = "MeetingSummaryTestHelper";

    /**
     * 获取测试用的会议记录文本
     */
    public static String getTestMeetingText() {
        return "[14:30:15] 大家好，今天我们开会讨论项目进度。\n" +
               "[14:30:30] 张三：我们的开发进度目前完成了百分之七十，预计下周可以完成全部功能。\n" +
               "[14:31:00] 李四：测试这边已经准备好了，等开发完成就可以开始测试。\n" +
               "[14:31:30] 王五：产品文档需要更新，我会在明天完成。\n" +
               "[14:32:00] 张三：那我们下周三进行最终的验收，大家没问题吧？\n" +
               "[14:32:15] 李四：没问题，我会准备好测试报告。\n" +
               "[14:32:30] 王五：好的，我也会准备相关文档。\n" +
               "[14:33:00] 会议结束，谢谢大家。";
    }

    /**
     * 测试API连接
     */
    public static void testApiConnection(String serverHost, int serverPort, 
                                       MeetingSummaryApiClient.ApiCallback<MeetingSummaryModels.HealthResponse> callback) {
        Log.d(TAG, "测试API连接: " + serverHost + ":" + serverPort);
        
        MeetingSummaryApiClient apiClient = new MeetingSummaryApiClient(serverHost, serverPort);
        apiClient.checkHealth(new MeetingSummaryApiClient.ApiCallback<MeetingSummaryModels.HealthResponse>() {
            @Override
            public void onSuccess(MeetingSummaryModels.HealthResponse result) {
                Log.d(TAG, "API连接测试成功: " + result.getService() + " v" + result.getVersion());
                callback.onSuccess(result);
            }

            @Override
            public void onError(String error) {
                Log.e(TAG, "API连接测试失败: " + error);
                callback.onError(error);
            }
        });
    }

    /**
     * 测试总结类型获取
     */
    public static void testGetSummaryTypes(String serverHost, int serverPort,
                                         MeetingSummaryApiClient.ApiCallback<MeetingSummaryModels.SummaryTypesResponse> callback) {
        Log.d(TAG, "测试获取总结类型");
        
        MeetingSummaryApiClient apiClient = new MeetingSummaryApiClient(serverHost, serverPort);
        apiClient.getSummaryTypes(new MeetingSummaryApiClient.ApiCallback<MeetingSummaryModels.SummaryTypesResponse>() {
            @Override
            public void onSuccess(MeetingSummaryModels.SummaryTypesResponse result) {
                Log.d(TAG, "获取总结类型成功，共" + result.getTypes().size() + "种类型");
                for (MeetingSummaryModels.SummaryTypeInfo type : result.getTypes()) {
                    Log.d(TAG, "  - " + type.getType() + ": " + type.getName() + " - " + type.getDescription());
                }
                callback.onSuccess(result);
            }

            @Override
            public void onError(String error) {
                Log.e(TAG, "获取总结类型失败: " + error);
                callback.onError(error);
            }
        });
    }

    /**
     * 测试会议总结生成
     */
    public static void testGenerateSummary(String serverHost, int serverPort,
                                         MeetingSummaryModels.SummaryType summaryType,
                                         MeetingSummaryApiClient.ApiCallback<MeetingSummaryModels.MeetingSummaryResponse> callback) {
        Log.d(TAG, "测试生成" + summaryType.getName());
        
        String testText = getTestMeetingText();
        MeetingSummaryApiClient apiClient = new MeetingSummaryApiClient(serverHost, serverPort);
        
        apiClient.generateMeetingSummary(testText, summaryType, 
            new MeetingSummaryApiClient.ApiCallback<MeetingSummaryModels.MeetingSummaryResponse>() {
                @Override
                public void onSuccess(MeetingSummaryModels.MeetingSummaryResponse result) {
                    Log.d(TAG, summaryType.getName() + "生成成功");
                    Log.d(TAG, "处理时间: " + result.getProcessingTime() + "秒");
                    Log.d(TAG, "总结长度: " + result.getSummary().length() + "字符");
                    Log.d(TAG, "总结预览: " + result.getSummary().substring(0, 
                        Math.min(100, result.getSummary().length())) + "...");
                    callback.onSuccess(result);
                }

                @Override
                public void onError(String error) {
                    Log.e(TAG, summaryType.getName() + "生成失败: " + error);
                    callback.onError(error);
                }
            });
    }

    /**
     * 格式化会议文本显示
     */
    public static String formatMeetingTextForDisplay(String meetingText, int maxLength) {
        if (meetingText == null || meetingText.isEmpty()) {
            return "没有会议记录";
        }

        // 计算行数
        String[] lines = meetingText.split("\n");
        int lineCount = lines.length;

        // 如果文本太长，截取前面部分
        String displayText = meetingText.length() > maxLength ? 
            meetingText.substring(0, maxLength) + "..." : meetingText;

        return displayText + "\n\n📊 统计信息:\n" +
               "• 总字符数: " + meetingText.length() + "\n" +
               "• 总行数: " + lineCount + "\n" +
               "• 预计处理时间: " + estimateProcessingTime(meetingText.length()) + "秒";
    }

    /**
     * 估算处理时间
     */
    private static int estimateProcessingTime(int textLength) {
        // 基于文本长度估算处理时间（经验值）
        // 大约每1000字符需要3-5秒处理时间
        return Math.max(5, (textLength / 1000) * 4 + 3);
    }

    /**
     * 验证会议文本是否有效
     */
    public static boolean isValidMeetingText(String meetingText) {
        if (meetingText == null || meetingText.trim().isEmpty()) {
            return false;
        }

        // 检查最小长度（至少50个字符）
        if (meetingText.trim().length() < 50) {
            Log.w(TAG, "会议文本太短，可能影响总结质量");
            return false;
        }

        return true;
    }

    /**
     * 获取总结类型的显示名称
     */
    public static String getSummaryTypeDisplayName(MeetingSummaryModels.SummaryType type) {
        switch (type) {
            case BRIEF:
                return "📋 " + type.getName();
            case DETAILED:
                return "📊 " + type.getName();
            case ACTION:
                return "✅ " + type.getName();
            default:
                return type.getName();
        }
    }

    /**
     * 格式化处理时间显示
     */
    public static String formatProcessingTime(float processingTime) {
        if (processingTime < 1.0f) {
            return String.format("%.1f秒", processingTime);
        } else if (processingTime < 60.0f) {
            return String.format("%.1f秒", processingTime);
        } else {
            int minutes = (int) (processingTime / 60);
            int seconds = (int) (processingTime % 60);
            return String.format("%d分%d秒", minutes, seconds);
        }
    }
}
