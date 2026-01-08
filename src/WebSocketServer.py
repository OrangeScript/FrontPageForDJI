import asyncio
import websockets
import socket
import json
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)

async def telemetry_bridge(websocket, path):
    """WebSocket 处理函数"""
    logging.info(f"Client connected from {websocket.remote_address}")
    
    try:
        # 连接到TCP服务器
        rc_ip = "192.168.3.245"
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.settimeout(5)  # 设置超时
        tcp_socket.connect((rc_ip, 8081))
        
        buffer = ""
        try:
            while True:
                try:
                    # 从TCP接收数据
                    data = tcp_socket.recv(4096).decode('utf-8')
                    if not data:
                        logging.info("TCP connection closed")
                        break
                    
                    buffer += data
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.strip():
                            # 验证JSON格式
                            try:
                                telemetry = json.loads(line)
                                # 转发到WebSocket
                                await websocket.send(line)
                                logging.debug(f"Sent: {telemetry.get('batteryLevel', 'N/A')}%")
                            except json.JSONDecodeError:
                                logging.error(f"Invalid JSON: {line}")
                                
                except socket.timeout:
                    # 发送心跳保持连接
                    await websocket.send(json.dumps({"heartbeat": True}))
                    continue
                    
        except Exception as e:
            logging.error(f"TCP error: {e}")
        finally:
            tcp_socket.close()
            
    except Exception as e:
        logging.error(f"Connection error: {e}")
    finally:
        logging.info(f"Client {websocket.remote_address} disconnected")

async def main():
    """主函数"""
    # 启动WebSocket服务器
    server = await websockets.serve(
        telemetry_bridge, 
        "0.0.0.0",  # 监听所有IP
        8765,        # 端口
        ping_interval=20,  # 心跳间隔
        ping_timeout=40    # 心跳超时
    )
    
    logging.info("WebSocket server started on ws://0.0.0.0:8765")
    logging.info("Press Ctrl+C to stop")
    
    # 保持服务器运行
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")