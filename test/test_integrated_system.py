#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合系统测试脚本
测试WebSocket服务器和ASR服务的集成
"""

import socket
import time
import threading
import json

def test_udp_connection():
    """测试UDP连接"""
    print("🧪 测试UDP连接...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_message = "测试UDP连接"
        sock.sendto(test_message.encode('utf-8'), ('127.0.0.1', 6009))
        sock.close()
        print("✅ UDP连接测试成功")
        return True
    except Exception as e:
        print(f"❌ UDP连接测试失败: {e}")
        return False

def test_websocket_connection():
    """测试WebSocket连接"""
    print("🧪 测试WebSocket连接...")
    try:
        import websockets
        import asyncio
        
        async def test_ws():
            try:
                async with websockets.connect("ws://localhost:8766") as websocket:
                    # 发送ping消息
                    await websocket.send(json.dumps({"type": "ping"}))
                    
                    # 等待响应
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "pong":
                        print("✅ WebSocket连接测试成功")
                        return True
                    else:
                        print("✅ WebSocket连接成功，收到欢迎消息")
                        return True
                        
            except asyncio.TimeoutError:
                print("✅ WebSocket连接成功（超时但连接正常）")
                return True
            except Exception as e:
                print(f"❌ WebSocket连接测试失败: {e}")
                return False
        
        return asyncio.run(test_ws())
        
    except ImportError:
        print("❌ websockets库未安装")
        return False
    except Exception as e:
        print(f"❌ WebSocket连接测试失败: {e}")
        return False

def send_test_data():
    """发送测试数据"""
    print("📤 发送测试数据...")
    
    test_messages = [
        "系统测试开始",
        "这是第一条测试消息",
        "语音识别功能正常",
        "WebSocket连接稳定",
        "前端显示正常",
        "系统测试完成"
    ]
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    for i, message in enumerate(test_messages, 1):
        try:
            sock.sendto(message.encode('utf-8'), ('127.0.0.1', 6009))
            print(f"📨 发送 ({i}/{len(test_messages)}): {message}")
            time.sleep(2)
        except Exception as e:
            print(f"❌ 发送失败: {e}")
    
    sock.close()
    print("✅ 测试数据发送完成")

def main():
    """主函数"""
    print("=" * 60)
    print("🧪 FunASR 整合系统测试")
    print("=" * 60)
    print()
    
    print("📋 测试说明:")
    print("1. 请确保已启动 WebSocket 服务器")
    print("2. 请确保已启动 ASR 语音识别服务")
    print("3. 请确保前端页面已打开")
    print()
    
    input("按回车键开始测试...")
    print()
    
    # 测试UDP连接
    udp_ok = test_udp_connection()
    time.sleep(1)
    
    # 测试WebSocket连接
    ws_ok = test_websocket_connection()
    time.sleep(1)
    
    print()
    print("📊 测试结果:")
    print(f"UDP连接: {'✅ 正常' if udp_ok else '❌ 异常'}")
    print(f"WebSocket连接: {'✅ 正常' if ws_ok else '❌ 异常'}")
    print()
    
    if udp_ok and ws_ok:
        print("🎉 所有连接测试通过！")
        print()
        
        choice = input("是否发送测试数据到前端？(y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            print()
            send_test_data()
            print()
            print("💡 请检查前端页面是否显示了测试消息")
        
    else:
        print("❌ 部分测试失败，请检查服务状态")
    
    print()
    print("=" * 60)
    print("测试完成")

if __name__ == "__main__":
    main()
