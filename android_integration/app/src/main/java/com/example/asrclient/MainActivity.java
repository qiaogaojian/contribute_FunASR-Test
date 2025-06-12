package com.example.asrclient;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;
import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity implements ASRManager.ASRListener {

    private static final int PERMISSION_REQUEST_CODE = 1001;

    private ASRManager asrManager;
    private Button btnConnect, btnRecord, btnClearResults, btnSaveResults, btnMeetingSummary;
    private TextView tvStatus, tvResults;
    private EditText etServerHost, etServerPort;
    private ScrollView scrollResults;

    private StringBuilder recognitionResults = new StringBuilder();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // 先初始化 ASRManager，再初始化 Views
        initASRManager();
        initViews();
        requestPermissions();
    }

    private void initViews() {
        btnConnect = findViewById(R.id.btn_connect);
        btnRecord = findViewById(R.id.btn_record);
        btnClearResults = findViewById(R.id.btn_clear_results);
        btnSaveResults = findViewById(R.id.btn_save_results);
        btnMeetingSummary = findViewById(R.id.btn_meeting_summary);
        tvStatus = findViewById(R.id.tv_status);
        tvResults = findViewById(R.id.tv_results);
        etServerHost = findViewById(R.id.et_server_host);
        etServerPort = findViewById(R.id.et_server_port);
        scrollResults = findViewById(R.id.scroll_results);

        // 设置默认服务器地址
        etServerHost.setText("192.168.1.163");
        etServerPort.setText("8000");

        // 设置按钮点击事件
        btnConnect.setOnClickListener(this::onConnectClick);
        btnRecord.setOnClickListener(this::onRecordClick);
        btnClearResults.setOnClickListener(this::onClearResultsClick);
        btnSaveResults.setOnClickListener(this::onSaveResultsClick);
        btnMeetingSummary.setOnClickListener(this::onMeetingSummaryClick);

        // 初始状态
        updateUI();
    }

    private void initASRManager() {
        try {
            // 运行音频诊断
            AudioDiagnostics.DiagnosticResult diagnostic = AudioDiagnostics.runDiagnostics(this);
            Log.d("MainActivity", "音频诊断结果:\n" + diagnostic.toString());

            if (!diagnostic.audioRecordSupported) {
                Toast.makeText(this, "设备不支持音频录制: " + diagnostic.errorMessage, Toast.LENGTH_LONG).show();
                asrManager = null;
                return;
            }

            asrManager = new ASRManager(this, this);
            Log.d("MainActivity", "ASRManager 初始化成功");
        } catch (Exception e) {
            Log.e("MainActivity", "ASRManager 初始化失败", e);
            Toast.makeText(this, "ASR服务初始化失败: " + e.getMessage(), Toast.LENGTH_LONG).show();
            // 即使初始化失败，也要确保 UI 能正常显示
            asrManager = null;
        }
    }

    private void requestPermissions() {
        List<String> permissionsNeeded = new ArrayList<>();

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
                != PackageManager.PERMISSION_GRANTED) {
            permissionsNeeded.add(Manifest.permission.RECORD_AUDIO);
        }

        if (!permissionsNeeded.isEmpty()) {
            ActivityCompat.requestPermissions(this,
                permissionsNeeded.toArray(new String[0]),
                PERMISSION_REQUEST_CODE);
        } else {
            Toast.makeText(this, getString(R.string.permissions_granted), Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        if (requestCode == PERMISSION_REQUEST_CODE) {
            boolean allGranted = true;
            for (int result : grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    allGranted = false;
                    break;
                }
            }

            if (allGranted) {
                Toast.makeText(this, getString(R.string.permissions_granted), Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(this, getString(R.string.permissions_required), Toast.LENGTH_LONG).show();
            }
        }
    }

    private void onConnectClick(View view) {
        if (asrManager == null) {
            Toast.makeText(this, "ASR服务未初始化", Toast.LENGTH_SHORT).show();
            return;
        }

        if (asrManager.isConnected()) {
            // 断开连接
            asrManager.disconnect();
        } else {
            // 连接服务器
            String host = etServerHost.getText().toString().trim();
            String portStr = etServerPort.getText().toString().trim();
            
            if (host.isEmpty()) {
                Toast.makeText(this, getString(R.string.please_enter_server_address), Toast.LENGTH_SHORT).show();
                return;
            }

            try {
                int port = Integer.parseInt(portStr);
                asrManager.setServerAddress(host, port);
                asrManager.connect();

                tvStatus.setText(getString(R.string.connecting));
                btnConnect.setEnabled(false);

            } catch (NumberFormatException e) {
                Toast.makeText(this, getString(R.string.invalid_port_format), Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void onRecordClick(View view) {
        if (asrManager == null) {
            Toast.makeText(this, "ASR服务未初始化", Toast.LENGTH_SHORT).show();
            return;
        }

        if (asrManager.isRecording()) {
            // 停止录音
            asrManager.stopRecording();
        } else {
            // 开始录音
            if (!asrManager.isConnected()) {
                Toast.makeText(this, getString(R.string.please_connect_first), Toast.LENGTH_SHORT).show();
                return;
            }
            
            asrManager.startRecording();
        }
    }

    private void onClearResultsClick(View view) {
        recognitionResults.setLength(0);
        tvResults.setText(getString(R.string.waiting_results));
        Toast.makeText(this, "识别结果已清空", Toast.LENGTH_SHORT).show();
    }

    private void onSaveResultsClick(View view) {
        String resultsText = recognitionResults.toString();
        if (resultsText.trim().isEmpty()) {
            Toast.makeText(this, "没有识别结果可保存", Toast.LENGTH_SHORT).show();
            return;
        }

        // 这里可以实现文件保存逻辑
        // 由于Android文件保存涉及权限和存储访问框架，这里先显示提示
        Toast.makeText(this, "保存功能待实现", Toast.LENGTH_SHORT).show();

        // TODO: 实现文件保存功能
    }

    private void onMeetingSummaryClick(View view) {
        String meetingText = recognitionResults.toString();
        if (meetingText.trim().isEmpty()) {
            Toast.makeText(this, getString(R.string.no_meeting_text), Toast.LENGTH_SHORT).show();
            return;
        }

        // 启动会议总结Activity
        Intent intent = new Intent(this, MeetingSummaryActivity.class);
        intent.putExtra(MeetingSummaryActivity.EXTRA_MEETING_TEXT, meetingText);
        intent.putExtra(MeetingSummaryActivity.EXTRA_SERVER_HOST, etServerHost.getText().toString().trim());
        intent.putExtra(MeetingSummaryActivity.EXTRA_SERVER_PORT,
            Integer.parseInt(etServerPort.getText().toString().trim()));
        startActivity(intent);
    }

    private void updateUI() {
        runOnUiThread(() -> {
            // 添加 null 检查，防止 NullPointerException
            if (asrManager == null) {
                // ASRManager 未初始化时的默认状态
                btnConnect.setText(getString(R.string.connect_server));
                btnConnect.setEnabled(true);
                btnRecord.setText(getString(R.string.start_recording));
                btnRecord.setEnabled(false);
                tvStatus.setText(getString(R.string.not_connected));
                etServerHost.setEnabled(true);
                etServerPort.setEnabled(true);
                return;
            }

            boolean connected = asrManager.isConnected();
            boolean recording = asrManager.isRecording();
            
            // 更新连接按钮
            btnConnect.setText(connected ? getString(R.string.disconnect_server) : getString(R.string.connect_server));
            btnConnect.setEnabled(true);

            // 更新录音按钮
            btnRecord.setText(recording ? getString(R.string.stop_recording) : getString(R.string.start_recording));
            btnRecord.setEnabled(connected);

            // 更新状态文本
            if (recording) {
                tvStatus.setText(getString(R.string.recording));
            } else if (connected) {
                tvStatus.setText(getString(R.string.connected));
            } else {
                tvStatus.setText(getString(R.string.not_connected));
            }
            
            // 更新服务器配置输入框
            etServerHost.setEnabled(!connected);
            etServerPort.setEnabled(!connected);
        });
    }

    // ASRManager.ASRListener 回调方法
    @Override
    public void onConnected() {
        Toast.makeText(this, getString(R.string.connection_successful), Toast.LENGTH_SHORT).show();
        updateUI();
    }

    @Override
    public void onDisconnected() {
        Toast.makeText(this, getString(R.string.connection_lost), Toast.LENGTH_SHORT).show();
        updateUI();
    }

    @Override
    public void onRecognitionResult(String text, boolean isFinal) {
        runOnUiThread(() -> {
            if (isFinal) {
                // 最终结果
                recognitionResults.append("[").append(getCurrentTime()).append("] ")
                    .append(text).append("\n");
                tvResults.setText(recognitionResults.toString());
                
                // 滚动到底部
                scrollResults.post(() -> scrollResults.fullScroll(View.FOCUS_DOWN));
            } else {
                // 临时结果 - 可以在状态栏显示
                tvStatus.setText(getString(R.string.recording) + ": " + text);
            }
        });
    }

    @Override
    public void onError(String error) {
        runOnUiThread(() -> {
            Toast.makeText(this, getString(R.string.error_prefix) + error, Toast.LENGTH_LONG).show();
            updateUI();
        });
    }

    @Override
    public void onRecordingStarted() {
        Toast.makeText(this, getString(R.string.recording_started), Toast.LENGTH_SHORT).show();
        updateUI();
    }

    @Override
    public void onRecordingStopped() {
        Toast.makeText(this, getString(R.string.recording_stopped), Toast.LENGTH_SHORT).show();
        updateUI();
    }

    private String getCurrentTime() {
        return new java.text.SimpleDateFormat("HH:mm:ss", java.util.Locale.getDefault())
            .format(new java.util.Date());
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (asrManager != null) {
            asrManager.release();
        }
    }
}
