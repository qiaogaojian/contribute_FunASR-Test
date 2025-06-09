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
            
    def udp_listener(self):
        """UDP监听器，接收ASR数据"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.1', self.udp_port))
        sock.settimeout(1.0)  # 设置超时，便于优雅退出
        
        logger.info(f"UDP监听器启动，端口: {self.udp_port}")
        
        while self.is_running:
            try:
                data, addr = sock.recvfrom(4096)
                text = data.decode('utf-8', errors='ignore').strip()
                
                if text:
                    logger.info(f"收到ASR数据: {text}")
                    # 在事件循环中广播文本
                    asyncio.run_coroutine_threadsafe(
                        self.broadcast_text(text), 
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
                    if data.get("type") == "ping":
                        await websocket.send(json.dumps({"type": "pong"}))
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
