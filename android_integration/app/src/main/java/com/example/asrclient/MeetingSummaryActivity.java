package com.example.asrclient;

import androidx.appcompat.app.AppCompatActivity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.widget.*;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/**
 * 会议总结Activity
 * 提供会议记录总结功能，对应web端的会议总结功能
 */
public class MeetingSummaryActivity extends AppCompatActivity {
    private static final String TAG = "MeetingSummaryActivity";
    public static final String EXTRA_MEETING_TEXT = "meeting_text";
    public static final String EXTRA_SERVER_HOST = "server_host";
    public static final String EXTRA_SERVER_PORT = "server_port";

    private TextView tvMeetingText;
    private RadioGroup rgSummaryType;
    private Button btnGenerateSummary;
    private ProgressBar progressBar;
    private TextView tvProgress;
    private ScrollView scrollSummary;
    private TextView tvSummaryResult;
    private LinearLayout layoutButtons;
    private Button btnSaveSummary, btnCopySummary, btnBackToMain;

    private String meetingText;
    private String serverHost;
    private int serverPort;
    private MeetingSummaryApiClient apiClient;
    private Handler mainHandler;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_meeting_summary);

        // 获取传入的数据
        Intent intent = getIntent();
        meetingText = intent.getStringExtra(EXTRA_MEETING_TEXT);
        serverHost = intent.getStringExtra(EXTRA_SERVER_HOST);
        serverPort = intent.getIntExtra(EXTRA_SERVER_PORT, 8000);

        if (meetingText == null || meetingText.trim().isEmpty()) {
            Toast.makeText(this, "没有会议记录可以总结", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }

        mainHandler = new Handler(Looper.getMainLooper());
        apiClient = new MeetingSummaryApiClient(serverHost, serverPort);

        initViews();
        setupListeners();
        displayMeetingText();
    }

    private void initViews() {
        tvMeetingText = findViewById(R.id.tv_meeting_text);
        rgSummaryType = findViewById(R.id.rg_summary_type);
        btnGenerateSummary = findViewById(R.id.btn_generate_summary);
        progressBar = findViewById(R.id.progress_bar);
        tvProgress = findViewById(R.id.tv_progress);
        scrollSummary = findViewById(R.id.scroll_summary);
        tvSummaryResult = findViewById(R.id.tv_summary_result);
        layoutButtons = findViewById(R.id.layout_buttons);
        btnSaveSummary = findViewById(R.id.btn_save_summary);
        btnCopySummary = findViewById(R.id.btn_copy_summary);
        btnBackToMain = findViewById(R.id.btn_back_to_main);

        // 设置标题
        if (getSupportActionBar() != null) {
            getSupportActionBar().setTitle("会议记录总结");
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }
    }

    private void setupListeners() {
        btnGenerateSummary.setOnClickListener(this::onGenerateSummaryClick);
        btnSaveSummary.setOnClickListener(this::onSaveSummaryClick);
        btnCopySummary.setOnClickListener(this::onCopySummaryClick);
        btnBackToMain.setOnClickListener(v -> finish());
    }

    private void displayMeetingText() {
        // 显示会议文本的前200个字符作为预览
        String preview = meetingText.length() > 200 ? 
            meetingText.substring(0, 200) + "..." : meetingText;
        tvMeetingText.setText("会议记录预览:\n" + preview + 
            "\n\n总字符数: " + meetingText.length());
    }

    private void onGenerateSummaryClick(View view) {
        // 获取选中的总结类型
        MeetingSummaryModels.SummaryType summaryType = getSelectedSummaryType();
        
        Log.d(TAG, "开始生成" + summaryType.getName());
        
        // 显示加载状态
        showLoading(summaryType);
        
        // 调用API生成总结
        apiClient.generateMeetingSummary(meetingText, summaryType, 
            new MeetingSummaryApiClient.ApiCallback<MeetingSummaryModels.MeetingSummaryResponse>() {
                @Override
                public void onSuccess(MeetingSummaryModels.MeetingSummaryResponse result) {
                    mainHandler.post(() -> {
                        hideLoading();
                        displaySummaryResult(result);
                        Log.d(TAG, summaryType.getName() + "生成成功，处理时间: " + 
                            result.getProcessingTime() + "秒");
                    });
                }

                @Override
                public void onError(String error) {
                    mainHandler.post(() -> {
                        hideLoading();
                        showError("生成总结失败: " + error);
                        Log.e(TAG, "生成总结失败: " + error);
                    });
                }
            });
    }

    private MeetingSummaryModels.SummaryType getSelectedSummaryType() {
        int selectedId = rgSummaryType.getCheckedRadioButtonId();
        
        if (selectedId == R.id.rb_detailed) {
            return MeetingSummaryModels.SummaryType.DETAILED;
        } else if (selectedId == R.id.rb_action) {
            return MeetingSummaryModels.SummaryType.ACTION;
        } else {
            return MeetingSummaryModels.SummaryType.BRIEF; // 默认
        }
    }

    private void showLoading(MeetingSummaryModels.SummaryType summaryType) {
        btnGenerateSummary.setEnabled(false);
        progressBar.setVisibility(View.VISIBLE);
        tvProgress.setVisibility(View.VISIBLE);
        tvProgress.setText("正在生成" + summaryType.getName() + "，请稍候...");
        
        scrollSummary.setVisibility(View.GONE);
        layoutButtons.setVisibility(View.GONE);
    }

    private void hideLoading() {
        btnGenerateSummary.setEnabled(true);
        progressBar.setVisibility(View.GONE);
        tvProgress.setVisibility(View.GONE);
    }

    private void displaySummaryResult(MeetingSummaryModels.MeetingSummaryResponse result) {
        // 显示总结结果
        tvSummaryResult.setText(result.getSummary());
        scrollSummary.setVisibility(View.VISIBLE);
        layoutButtons.setVisibility(View.VISIBLE);
        
        // 更新保存按钮文本
        MeetingSummaryModels.SummaryType type = 
            MeetingSummaryModels.SummaryType.fromValue(result.getSummaryType());
        btnSaveSummary.setText("保存" + type.getName());
        
        Toast.makeText(this, type.getName() + "生成成功！处理时间: " + 
            String.format("%.1f", result.getProcessingTime()) + "秒", Toast.LENGTH_SHORT).show();
    }

    private void showError(String error) {
        Toast.makeText(this, error, Toast.LENGTH_LONG).show();
    }

    private void onSaveSummaryClick(View view) {
        String summaryText = tvSummaryResult.getText().toString();
        if (summaryText.isEmpty()) {
            Toast.makeText(this, "没有总结内容可保存", Toast.LENGTH_SHORT).show();
            return;
        }

        // 生成文件名
        String timestamp = new SimpleDateFormat("yyyy-MM-dd_HH-mm-ss", Locale.getDefault())
            .format(new Date());
        MeetingSummaryModels.SummaryType type = getSelectedSummaryType();
        String fileName = type.getName() + "_" + timestamp + ".txt";

        // 这里可以实现文件保存逻辑
        // 由于Android文件保存涉及权限和存储访问框架，这里先显示提示
        Toast.makeText(this, "保存功能待实现: " + fileName, Toast.LENGTH_SHORT).show();
        
        // TODO: 实现文件保存功能
        // 可以使用 Storage Access Framework 或者分享Intent
    }

    private void onCopySummaryClick(View view) {
        String summaryText = tvSummaryResult.getText().toString();
        if (summaryText.isEmpty()) {
            Toast.makeText(this, "没有总结内容可复制", Toast.LENGTH_SHORT).show();
            return;
        }

        // 复制到剪贴板
        android.content.ClipboardManager clipboard = 
            (android.content.ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
        android.content.ClipData clip = android.content.ClipData.newPlainText("会议总结", summaryText);
        clipboard.setPrimaryClip(clip);
        
        Toast.makeText(this, "总结已复制到剪贴板", Toast.LENGTH_SHORT).show();
    }

    @Override
    public boolean onSupportNavigateUp() {
        finish();
        return true;
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (apiClient != null) {
            apiClient.release();
        }
    }
}
