#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket服务器 - 接收ASR的UDP数据并转发给前端
"""

import asyncio
import socket
import threading
import json
import logging
from datetime import datetime
import numpy as np
import wave
import io

import websockets

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ASRWebSocketServer:
    def __init__(self, udp_port: int = 6009, websocket_port: int = 8766):
        self.udp_port = udp_port
        self.websocket_port = websocket_port
        self.clients = set()
        self.latest_text = ""
        self.is_running = False
        
        # 音频处理相关
        self.audio_buffer = []
        self.sample_rate = 16000
        self.chunk_size = 1024
        
        # 导入ASR模块
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from src.asr.websocket_asr import WebSocketASR
            self.asr_engine = WebSocketASR()
            self.use_local_asr = True
            logger.info("已加载WebSocket ASR引擎")
        except ImportError as e:
            logger.warning(f"无法加载WebSocket ASR引擎: {e}")
            self.asr_engine = None
            self.use_local_asr = False

    async def register_client(self, websocket):
        """注册新的WebSocket客户端"""
        self.clients.add(websocket)
        logger.info(f"新客户端连接: {websocket.remote_address}")
        
        # 发送欢迎消息和当前文本
        welcome_msg = {
            "type": "welcome",
            "message": "连接成功，等待语音识别数据...",
            "timestamp": datetime.now().isoformat(),
            "current_text": self.latest_text
        }
        await websocket.send(json.dumps(welcome_msg, ensure_ascii=False))
        
    async def unregister_client(self, websocket):
        """注销WebSocket客户端"""
        self.clients.discard(websocket)
        logger.info(f"客户端断开连接: {websocket.remote_address}")
        
    async def broadcast_text(self, text: str, is_final: bool = True):
        """向所有连接的客户端广播文本"""
        if not self.clients:
            return
            
        message = {
            "type": "asr_result",
            "text": text,
            "is_final": is_final,
            "timestamp": datetime.now().isoformat()
        }
        
        # 更新最新文本
        if is_final:
            self.latest_text = text
            
        # 广播给所有客户端
        disconnected_clients = set()
        for client in self.clients:
            try:
                await client.send(json.dumps(message, ensure_ascii=False))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"发送消息到客户端失败: {e}")
                disconnected_clients.add(client)
                
        # 移除断开连接的客户端
        for client in disconnected_clients:
            self.clients.discard(client)
            
    async def process_audio_data(self, data):
        """处理音频数据"""
        try:
            audio_data = data.get('data', [])
            sample_rate = data.get('sampleRate', 16000)
            
            if not audio_data:
                return
                
            # 转换为numpy数组
            audio_array = np.array(audio_data, dtype=np.int16)
            
            # 添加到音频缓冲区
            self.audio_buffer.extend(audio_array)
            
            # 当缓冲区达到一定大小时进行ASR处理
            if len(self.audio_buffer) >= self.chunk_size:
                await self.process_audio_chunk()
                
        except Exception as e:
            logger.error(f"处理音频数据失败: {e}")
            
    async def process_audio_chunk(self):
        """处理音频块 - 支持优化后的两阶段识别"""
        try:
            if not self.use_local_asr or not self.asr_engine:
                # 如果没有本地ASR引擎，清空缓冲区
                self.audio_buffer = []
                return

            # 获取音频数据
            chunk_data = np.array(self.audio_buffer[:self.chunk_size], dtype=np.int16)
            self.audio_buffer = self.audio_buffer[self.chunk_size:]

            # 转换为float32格式
            audio_float = chunk_data.astype(np.float32) / 32768.0

            # 调用优化后的ASR引擎进行识别
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.asr_engine.recognize_chunk, audio_float
            )

            if result and isinstance(result, dict):
                # 处理新的结构化结果
                text = result.get('text', '').strip()
                result_type = result.get('type', 'final')
                is_final = (result_type == 'final')

                if text:
                    # 广播识别结果，区分预测和最终结果
                    await self.broadcast_text(text, is_final)
                    logger.info(f"ASR识别结果 ({result_type}): {text}")

            elif result and isinstance(result, str) and result.strip():
                # 兼容旧格式的字符串结果
                await self.broadcast_text(result.strip(), True)
                logger.info(f"ASR识别结果 (兼容模式): {result}")

        except Exception as e:
            logger.error(f"处理音频块失败: {e}")
            # 清空缓冲区以避免错误累积
            self.audio_buffer = []
            
    def udp_listener(self):
        """UDP监听器，接收ASR数据"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.1', self.udp_port))
        sock.settimeout(1.0)  # 设置超时，便于优雅退出
        
        logger.info(f"UDP监听器启动，端口: {self.udp_port}")
        
        while self.is_running:
            try:
                data, addr = sock.recvfrom(4096)
                message = data.decode('utf-8', errors='ignore').strip()

                if message:
                    # 解析消息类型和内容
                    if message.startswith('PREVIEW:'):
                        text = message[8:]  # 移除 'PREVIEW:' 前缀
                        is_final = False
                        logger.info(f"收到预览数据: {text}")
                    elif message.startswith('FINAL:'):
                        text = message[6:]  # 移除 'FINAL:' 前缀
                        is_final = True
                        logger.info(f"收到最终数据: {text}")
                    else:
                        # 兼容旧格式，默认为最终结果
                        text = message
                        is_final = True
                        logger.info(f"收到ASR数据: {text}")

                    # 在事件循环中广播文本
                    asyncio.run_coroutine_threadsafe(
                        self.broadcast_text(text, is_final),
                        self.loop
                    )
                    
            except socket.timeout:
                continue
            except Exception as e:
                if self.is_running:
                    logger.error(f"UDP监听错误: {e}")
                    
        sock.close()
        logger.info("UDP监听器已停止")
        
    async def handle_websocket(self, websocket, path):
        """处理WebSocket连接"""
        await self.register_client(websocket)
        try:
            async for message in websocket:
                # 处理客户端发送的消息
                try:
                    data = json.loads(message)
                    message_type = data.get("type")
                    
                    if message_type == "ping":
                        await websocket.send(json.dumps({"type": "pong"}))
                    elif message_type == "audio_data":
                        await self.process_audio_data(data)
                    else:
                        logger.warning(f"未知消息类型: {message_type}")
                        
                except json.JSONDecodeError:
                    logger.warning(f"收到无效JSON消息: {message}")
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)
            
    async def start_server(self):
        """启动WebSocket服务器"""
        self.is_running = True
        self.loop = asyncio.get_event_loop()

        # 启动UDP监听器线程
        udp_thread = threading.Thread(target=self.udp_listener, daemon=True)
        udp_thread.start()

        # 启动WebSocket服务器
        logger.info(f"WebSocket服务器启动，端口: {self.websocket_port}")

        # 使用websockets.serve的新API
        async with websockets.serve(
            self.handle_websocket,
            "localhost",
            self.websocket_port
        ) as server:
            logger.info("服务器运行中，按Ctrl+C停止...")

            try:
                await asyncio.Future()  # 永远运行
            except KeyboardInterrupt:
                logger.info("收到停止信号")
                
    def stop(self):
        """停止服务器"""
        self.is_running = False

async def main():
    """主函数"""
    server = ASRWebSocketServer()
    try:
        await server.start_server()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        logger.info("服务器已停止")

if __name__ == "__main__":
    asyncio.run(main())
