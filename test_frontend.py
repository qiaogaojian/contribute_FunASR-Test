#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 模拟ASR数据发送，测试前端显示
"""

import socket
import time
import threading

def send_test_data():
    """发送测试数据到UDP端口"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    test_messages = [
        "你好，这是一个测试消息",
        "语音识别正在工作",
        "实时显示功能正常",
        "WebSocket连接成功",
        "前端界面显示正常",
        "测试完成，系统运行良好"
    ]
    
    print("开始发送测试数据...")
    
    for i, message in enumerate(test_messages):
        try:
            sock.sendto(message.encode('utf-8'), ('127.0.0.1', 6009))
            print(f"发送: {message}")
            time.sleep(3)  # 每3秒发送一条消息
        except Exception as e:
            print(f"发送失败: {e}")
    
    sock.close()
    print("测试数据发送完成")

def main():
    """主函数"""
    print("=" * 50)
    print("🧪 前端测试工具")
    print("=" * 50)
    print("此工具将模拟ASR程序发送测试数据")
    print("请确保WebSocket服务器正在运行")
    print("然后打开前端页面查看效果")
    print("=" * 50)
    
    input("按回车键开始发送测试数据...")
    
    # 在新线程中发送数据
    test_thread = threading.Thread(target=send_test_data, daemon=True)
    test_thread.start()
    
    try:
        test_thread.join()
    except KeyboardInterrupt:
        print("\n测试已停止")

if __name__ == "__main__":
    main()
