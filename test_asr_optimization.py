#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASR优化效果测试脚本
测试不同配置下的语音识别效果
"""

import socket
import time
import json
from datetime import datetime

def send_test_sentences():
    """发送测试句子，模拟容易被错误拆分的语音"""
    
    # 测试句子 - 这些句子容易在某些位置被错误拆分
    test_sentences = [
        # 长句子测试
        ("FINAL:今天天气很好，我们决定去公园里面散步，顺便看看那些美丽的花朵。", "长句子完整性测试"),
        
        # 带停顿的句子
        ("PREVIEW:我想要，", "预览：带逗号停顿"),
        ("FINAL:我想要，买一些新鲜的水果。", "最终：完整句子"),
        
        # 英文混合测试
        ("FINAL:这个项目使用了Python和JavaScript两种编程语言。", "中英文混合测试"),
        
        # 数字和标点测试
        ("PREVIEW:今天是2024年，", "预览：年份停顿"),
        ("FINAL:今天是2024年，1月15日，星期一。", "最终：完整日期"),
        
        # 专业术语测试
        ("FINAL:FunASR是阿里巴巴达摩院开发的语音识别工具包。", "专业术语测试"),
        
        # 连续短句测试
        ("FINAL:你好。", "短句1"),
        ("FINAL:我是小明。", "短句2"),
        ("FINAL:很高兴认识你。", "短句3"),
        
        # 长对话测试
        ("FINAL:请问您需要什么帮助吗？我可以为您提供各种服务和支持。", "客服对话测试"),
        
        # 技术讨论测试
        ("PREVIEW:这个算法的时间复杂度是，", "预览：技术术语"),
        ("FINAL:这个算法的时间复杂度是O(n log n)，空间复杂度是O(1)。", "最终：完整技术描述"),
    ]
    
    print("🧪 开始发送ASR优化测试数据...")
    print("=" * 60)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    for i, (message, description) in enumerate(test_sentences, 1):
        try:
            # 发送消息
            sock.sendto(message.encode('utf-8'), ('127.0.0.1', 6009))
            
            # 记录发送信息
            timestamp = datetime.now().strftime("%H:%M:%S")
            msg_type = "预览" if message.startswith("PREVIEW:") else "最终"
            content = message.split(":", 1)[1] if ":" in message else message
            
            print(f"[{timestamp}] 测试 {i:2d} ({msg_type}): {description}")
            print(f"           内容: {content}")
            
            # 预览消息间隔短，最终消息间隔长
            sleep_time = 1 if msg_type == "预览" else 3
            time.sleep(sleep_time)
            
        except Exception as e:
            print(f"❌ 发送失败: {e}")
    
    sock.close()
    print("\n" + "=" * 60)
    print("✅ 测试数据发送完成")
    print("\n💡 请观察前端页面的显示效果：")
    print("1. 预览文字应该显示为橙色边框")
    print("2. 最终文字应该显示为蓝色边框，并累积显示")
    print("3. 长句子不应该被错误拆分")
    print("4. 每条最终文字都应该有时间戳")

def test_websocket_connection():
    """测试WebSocket连接"""
    try:
        import websockets
        import asyncio
        
        async def test_connection():
            try:
                uri = "ws://localhost:8766"
                async with websockets.connect(uri) as websocket:
                    # 发送ping
                    await websocket.send(json.dumps({"type": "ping"}))
                    
                    # 等待响应
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print("✅ WebSocket连接正常")
                    return True
                    
            except Exception as e:
                print(f"❌ WebSocket连接失败: {e}")
                return False
        
        return asyncio.run(test_connection())
        
    except ImportError:
        print("❌ websockets库未安装，无法测试WebSocket连接")
        return False

def check_asr_config():
    """检查当前ASR配置"""
    try:
        from asr_config import get_config
        
        # 读取当前配置
        asr_file_path = "src/asr/streaming_paraformer.py"
        with open(asr_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找配置名称
        config_line_start = 'CONFIG_NAME = "'
        config_line_end = '"'
        
        start_pos = content.find(config_line_start)
        if start_pos != -1:
            start_pos += len(config_line_start)
            end_pos = content.find(config_line_end, start_pos)
            if end_pos != -1:
                config_name = content[start_pos:end_pos]
                config_info = get_config(config_name)
                
                print(f"📋 当前ASR配置: {config_name}")
                print(f"   配置说明: {config_info.get('description', '无说明')}")
                print(f"   VAD配置: {config_info['vad_config']}")
                print(f"   Chunk大小: {config_info['chunk_size']}")
                print(f"   预测间隔: {config_info['prediction_interval']}")
                return True
        
        print("❌ 无法读取当前配置")
        return False
        
    except Exception as e:
        print(f"❌ 检查配置失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🧪 FunASR 优化效果测试")
    print("=" * 60)
    
    # 检查当前配置
    print("1. 检查当前配置...")
    check_asr_config()
    
    print("\n" + "=" * 60)
    
    # 检查WebSocket连接
    print("2. 检查WebSocket连接...")
    ws_ok = test_websocket_connection()
    
    print("\n" + "=" * 60)
    
    # 提示用户
    print("3. 测试准备...")
    print("请确保以下服务正在运行：")
    print("   ✓ WebSocket服务器 (python src/websocket_server.py)")
    print("   ✓ ASR语音识别服务 (python src/asr/streaming_paraformer.py)")
    print("   ✓ 前端页面已打开 (frontend/index.html)")
    
    if not ws_ok:
        print("\n❌ WebSocket连接失败，请先启动相关服务")
        return
    
    print("\n" + "=" * 60)
    
    # 开始测试
    choice = input("是否开始发送测试数据？(y/n): ").strip().lower()
    if choice in ['y', 'yes', '是']:
        print("\n4. 开始测试...")
        send_test_sentences()
        
        print("\n" + "=" * 60)
        print("🎯 测试完成！")
        print("\n请检查前端页面的显示效果：")
        print("- 文字是否按预期累积显示？")
        print("- 长句子是否保持完整？")
        print("- 预览和最终文字是否正确区分？")
        print("- 时间戳是否正确显示？")
        
    else:
        print("测试已取消")

if __name__ == "__main__":
    main()
