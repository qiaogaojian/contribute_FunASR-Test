package com.example.asrclient;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import android.Manifest;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.floatingactionbutton.FloatingActionButton;
import com.google.android.material.textfield.TextInputEditText;
import androidx.core.widget.NestedScrollView;
import java.util.ArrayList;
import java.util.List;

public class MainActivityImproved extends AppCompatActivity implements ASRManager.ASRListener {
    
    private static final int PERMISSION_REQUEST_CODE = 1001;
    
    private ASRManager asrManager;
    private MaterialButton btnConnect, btnRecord;
    private TextView tvStatus, tvResults;
    private TextInputEditText etServerHost, etServerPort;
    private NestedScrollView scrollResults;
    private FloatingActionButton fabClear;
    
    private StringBuilder recognitionResults = new StringBuilder();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main_improved);

        // 先初始化 ASRManager，再初始化 Views
        initASRManager();
        initViews();
        requestPermissions();
    }

    private void initViews() {
        btnConnect = findViewById(R.id.btn_connect);
        btnRecord = findViewById(R.id.btn_record);
        tvStatus = findViewById(R.id.tv_status);
        tvResults = findViewById(R.id.tv_results);
        etServerHost = findViewById(R.id.et_server_host);
        etServerPort = findViewById(R.id.et_server_port);
        scrollResults = findViewById(R.id.scroll_results);
        fabClear = findViewById(R.id.fab_clear);
        
        // 设置按钮点击事件
        btnConnect.setOnClickListener(this::onConnectClick);
        btnRecord.setOnClickListener(this::onRecordClick);
        fabClear.setOnClickListener(this::onClearClick);
        
        // 初始状态
        updateUI();
    }

    private void initASRManager() {
        asrManager = new ASRManager(this, this);
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

    private void onClearClick(View view) {
        recognitionResults.setLength(0);
        tvResults.setText(getString(R.string.waiting_results));
        Toast.makeText(this, "识别结果已清空", Toast.LENGTH_SHORT).show();
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
            btnRecord.setIcon(getDrawable(recording ? R.drawable.ic_mic_off : R.drawable.ic_mic));
            
            // 更新状态文本和颜色
            if (recording) {
                tvStatus.setText(getString(R.string.recording));
                tvStatus.setTextColor(getColor(R.color.recording_active));
            } else if (connected) {
                tvStatus.setText(getString(R.string.connected));
                tvStatus.setTextColor(getColor(R.color.status_connected));
            } else {
                tvStatus.setText(getString(R.string.not_connected));
                tvStatus.setTextColor(getColor(R.color.status_disconnected));
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
                    .append(text).append("\n\n");
                tvResults.setText(recognitionResults.toString());
                
                // 滚动到底部
                scrollResults.post(() -> scrollResults.fullScroll(View.FOCUS_DOWN));
            } else {
                // 临时结果 - 在状态栏显示
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
