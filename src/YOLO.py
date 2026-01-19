import cv2
import json
import base64
import time
import threading
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ultralytics import YOLO

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 帧缓冲区类 - 存储最新帧
class FrameBuffer:
    def __init__(self):
        self.latest_frame = None
        self.lock = threading.Lock()
        self.frame_ready = threading.Event()
        self.is_active = True  # 标记缓冲区是否活跃

    def update(self, frame):
        with self.lock:
            if self.is_active:
                self.latest_frame = frame
                self.frame_ready.set()

    def get_latest(self):
        with self.lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None

    def deactivate(self):
        with self.lock:
            self.is_active = False
            self.latest_frame = None


# 初始化FastAPI应用
app = FastAPI(title="YOLOv8 目标检测 API", description="提供实时目标检测服务")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 仅用于开发环境，生产环境应限制为可信域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加载YOLO模型
try:
    models = {
        "yolo11n.pt": YOLO("yolo11n.pt"),  # Nano版本，最快
        "yolo11s.pt": YOLO("yolo11n.pt"),  # Small版本，较快
        "yolo11m.pt": YOLO("yolo11n.pt"),  # Medium版本，平衡
        "yolo11l.pt": YOLO("yolo11n.pt"),  # Large版本，更准确
        "yolo11x.pt": YOLO("yolo11n.pt"),  # Extra版本，最准确
    }
except Exception as e:
    logger.error(f"模型加载失败: {str(e)}")
    models = {}


# 连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}  # 连接ID -> WebSocket
        self.rtsp_clients: Dict[str, cv2.VideoCapture] = {}  # RTSP URL -> VideoCapture
        self.rtsp_connections: Dict[str, int] = {}  # RTSP URL -> 连接数
        self.rtsp_frame_buffers: Dict[str, FrameBuffer] = {}  # RTSP URL -> FrameBuffer
        self.rtsp_threads: Dict[str, threading.Thread] = {}  # RTSP URL -> 线程
        self.max_connections_per_rtsp = 5  # 每个RTSP源的最大连接数
        self.heartbeat_interval = 30  # 心跳间隔（秒）
        self._lock = threading.Lock()  # 用于线程安全的锁

    async def connect(self, websocket: WebSocket, connection_id: str, rtsp_url: str):
        # 检查RTSP连接数限制
        with self._lock:
            if rtsp_url in self.rtsp_connections and self.rtsp_connections[rtsp_url] >= self.max_connections_per_rtsp:
                await websocket.close(code=1008, reason="连接数超过上限")
                raise HTTPException(status_code=429, detail="连接数超过上限")

        await websocket.accept()

        with self._lock:
            self.active_connections[connection_id] = websocket

            # 更新RTSP连接数
            self.rtsp_connections[rtsp_url] = self.rtsp_connections.get(rtsp_url, 0) + 1
            logger.info(f"新连接: {connection_id}, RTSP: {rtsp_url}, 当前连接数: {self.rtsp_connections[rtsp_url]}")

            # 如果是第一个连接到该RTSP的客户端，启动读取线程
            if self.rtsp_connections[rtsp_url] == 1:
                if rtsp_url not in self.rtsp_frame_buffers:
                    self.rtsp_frame_buffers[rtsp_url] = FrameBuffer()

                # 启动独立线程读取RTSP流
                thread = threading.Thread(target=self._read_rtsp_stream, args=(rtsp_url,), daemon=True)
                self.rtsp_threads[rtsp_url] = thread
                thread.start()

    def disconnect(self, connection_id: str, rtsp_url: str):
        with self._lock:
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]

            # 减少RTSP连接数
            if rtsp_url in self.rtsp_connections:
                self.rtsp_connections[rtsp_url] -= 1
                if self.rtsp_connections[rtsp_url] <= 0:
                    logger.info(f"没有更多连接，准备关闭RTSP流: {rtsp_url}")

                    # 释放RTSP客户端
                    if rtsp_url in self.rtsp_clients:
                        self.rtsp_clients[rtsp_url].release()
                        del self.rtsp_clients[rtsp_url]
                        logger.info(f"释放RTSP客户端: {rtsp_url}")

                    # 停用帧缓冲区
                    if rtsp_url in self.rtsp_frame_buffers:
                        self.rtsp_frame_buffers[rtsp_url].deactivate()
                        del self.rtsp_frame_buffers[rtsp_url]
                        logger.info(f"释放帧缓冲区: {rtsp_url}")

                    # RTSP URL从连接数统计中移除
                    del self.rtsp_connections[rtsp_url]

                    # 移除线程引用（线程会在检测到连接数为0时自行退出）
                    if rtsp_url in self.rtsp_threads:
                        del self.rtsp_threads[rtsp_url]

            logger.info(
                f"断开连接: {connection_id}, RTSP: {rtsp_url}, 当前连接数: {self.rtsp_connections.get(rtsp_url, 0)}")

    async def send_message(self, message: str, connection_id: str):
        if connection_id in self.active_connections:
            try:
                # 尝试发送消息
                await self.active_connections[connection_id].send_text(message)
            except WebSocketDisconnect:
                logger.info(f"WebSocket连接已关闭，终止发送数据: {connection_id}")
                # 获取RTSP URL并断开连接
                rtsp_url = next((url for url, conns in self.rtsp_connections.items() if
                                 connection_id in [k for k in self.active_connections]), None)
                if rtsp_url:
                    self.disconnect(connection_id, rtsp_url)
            except Exception as e:
                logger.error(f"发送消息失败: {connection_id}, 错误: {str(e)}")
                # 获取RTSP URL并断开连接
                rtsp_url = next((url for url, conns in self.rtsp_connections.items() if
                                 connection_id in [k for k in self.active_connections]), None)
                if rtsp_url:
                    self.disconnect(connection_id, rtsp_url)

    def get_frame_buffer(self, rtsp_url: str):
        return self.rtsp_frame_buffers.get(rtsp_url)

    def _read_rtsp_stream(self, rtsp_url: str):
        logger.info(f"启动RTSP读取线程: {rtsp_url}")

        # 创建新的RTSP客户端
        cap = cv2.VideoCapture(rtsp_url)
        # 设置参数，减少延迟
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 尽量减少缓冲区
        cap.set(cv2.CAP_PROP_FPS, 25)  # 设置期望的帧率

        with self._lock:
            self.rtsp_clients[rtsp_url] = cap

        frame_buffer = self.rtsp_frame_buffers.get(rtsp_url)
        if not frame_buffer:
            logger.error(f"帧缓冲区不存在: {rtsp_url}")
            return

        while True:
            # 检查是否还有连接
            with self._lock:
                if rtsp_url not in self.rtsp_connections or self.rtsp_connections[rtsp_url] <= 0:
                    logger.info(f"没有活动连接，停止读取RTSP流: {rtsp_url}")
                    break

            try:
                ret, frame = cap.read()
            except cv2.error as e:
                logger.error(f"读取RTSP流时出错: {rtsp_url}, 错误: {str(e)}")
                # 尝试重新连接
                with self._lock:
                    if rtsp_url in self.rtsp_clients:
                        self.rtsp_clients[rtsp_url].release()
                        cap = cv2.VideoCapture(rtsp_url)
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        self.rtsp_clients[rtsp_url] = cap
                time.sleep(1)  # 等待并重试
                continue

            if not ret:
                logger.warning(f"无法从RTSP流读取帧: {rtsp_url}")
                # 尝试重新连接
                with self._lock:
                    if rtsp_url in self.rtsp_clients:
                        self.rtsp_clients[rtsp_url].release()
                        cap = cv2.VideoCapture(rtsp_url)
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        self.rtsp_clients[rtsp_url] = cap
                time.sleep(1)  # 等待并重试
                continue

            # 更新帧缓冲区为最新帧
            if frame_buffer:
                frame_buffer.update(frame)

            # 不需要延时，让线程尽可能快地读取最新帧

        # 清理资源
        with self._lock:
            if rtsp_url in self.rtsp_clients:
                self.rtsp_clients[rtsp_url].release()
                del self.rtsp_clients[rtsp_url]

        logger.info(f"RTSP读取线程已停止: {rtsp_url}")


# 优化的HTML页面，添加防缓存机制
@app.get("/", response_class=HTMLResponse)
async def get():
    return """
    <html>
        <head>
            <title>RTSP摄像头检测测试</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                h1 { color: #333; }
                #video-container { margin-top: 20px; }
                #video { max-width: 100%; border: 1px solid #ddd; }
                #status { margin-top: 10px; color: #666; }
            </style>
        </head>
        <body>
            <h1>RTSP摄像头检测测试</h1>
            <div id="video-container">
                <img id="video" src="" alt="RTSP视频流">
            </div>
            <div id="status">连接中...</div>

            <script>
                const videoElement = document.getElementById('video');
                const statusElement = document.getElementById('status');
                let lastTimestamp = 0;

                // 创建WebSocket连接
                function createWebSocket() {
                    const ws = new WebSocket(`ws://${window.location.host}/ws/camera_detection?camera_id=rtsp://aaa:aaa@10.87.49.48:8554/streaming/live/1`);

                    ws.onopen = function() {
                        statusElement.textContent = '已连接';
                        console.log('WebSocket连接已建立');
                    };

                    ws.onmessage = function(event) {
                        try {
                            const data = JSON.parse(event.data);

                            if (data.image_base64) {
                                // 只显示比当前更新的帧
                                if (!lastTimestamp || data.timestamp > lastTimestamp) {
                                    lastTimestamp = data.timestamp;
                                    // 添加随机查询参数，防止浏览器缓存
                                    videoElement.src = data.image_base64;
                                    statusElement.textContent = `已更新: ${new Date(data.timestamp * 1000).toLocaleTimeString()}`;
                                }
                            } else if (data.error) {
                                statusElement.textContent = `错误: ${data.error}`;
                                console.error('接收错误:', data.error);
                            } else if (data.type === 'heartbeat') {
                                // 处理心跳
                                statusElement.textContent = '连接活跃中...';
                            }
                        } catch (error) {
                            console.error('解析消息失败:', error);
                        }
                    };

                    ws.onclose = function() {
                        statusElement.textContent = '连接已关闭，尝试重新连接...';
                        console.log('WebSocket连接已关闭');
                        // 5秒后尝试重新连接
                        setTimeout(createWebSocket, 5000);
                    };

                    ws.onerror = function(error) {
                        statusElement.textContent = '连接错误，正在重试...';
                        console.error('WebSocket错误:', error);
                    };

                    return ws;
                }

                // 初始化WebSocket
                const ws = createWebSocket();

                // 添加页面卸载时关闭WebSocket的处理
                window.addEventListener('beforeunload', function() {
                    ws.close();
                });
            </script>
        </body>
    </html>
    """


# 用于摄像头/RTSP流检测的WebSocket端点
@app.websocket("/ws/camera_detection")
async def websocket_camera_detection(
        websocket: WebSocket,
        camera_id: str = Query(...),
        model_path: str = Query("yolo11n.pt"),
        conf: float = Query(0.3),
        target_classes: Optional[str] = Query(None),
        fps_limit: int = Query(1)  # 每秒处理一帧
):
    # 生成唯一连接ID
    connection_id = f"{camera_id}_{int(time.time() * 1000)}"
    last_activity_time = time.perf_counter()  # 使用更精确的计时器
    frame_retry_count = 0
    max_frame_retries = 10
    processing_time = 0  # 记录处理一帧的时间

    try:
        # 检查模型是否存在
        if model_path not in models:
            await manager.send_message(json.dumps({"error": f"模型 {model_path} 不存在"}), connection_id)
            return

        # 解析目标类别
        classes = None
        if target_classes:
            try:
                classes = [c.strip() for c in target_classes.split(',')]
                # 将类别名称转换为类别ID
                model = models[model_path]
                class_names = list(model.names.values())
                classes = [class_names.index(c) for c in classes if c in class_names]
            except Exception as e:
                await manager.send_message(json.dumps({"error": f"解析目标类别失败: {str(e)}"}), connection_id)
                return

        # 连接到WebSocket
        await manager.connect(websocket, connection_id, camera_id)

        # 获取帧缓冲区
        frame_buffer = manager.get_frame_buffer(camera_id)
        if frame_buffer is None:
            await manager.send_message(json.dumps({"error": f"无法获取RTSP帧缓冲区: {camera_id}"}), connection_id)
            await manager.disconnect(connection_id, camera_id)
            return

        # 发送连接成功消息
        await manager.send_message(json.dumps({"status": "connected", "message": "已成功连接到RTSP流"}), connection_id)

        # 帧处理逻辑
        frame_interval = 1.0 / fps_limit  # 计算帧间隔时间
        next_process_time = time.perf_counter() + frame_interval  # 下一次处理的时间点

        model = models[model_path]

        while True:
            current_time = time.perf_counter()

            # 等待到下一个处理时间点
            if current_time < next_process_time:
                time.sleep(next_process_time - current_time)
                current_time = time.perf_counter()

            # 更新下一次处理时间
            next_process_time = current_time + frame_interval

            # 检查连接是否仍然存在
            if connection_id not in manager.active_connections:
                logger.info(f"连接已断开，终止处理: {connection_id}")
                break

            # 发送心跳包
            if current_time - last_activity_time > manager.heartbeat_interval:
                await manager.send_message(json.dumps({"type": "heartbeat"}), connection_id)
                last_activity_time = current_time

            # 获取最新帧
            frame = frame_buffer.get_latest()
            if frame is None:
                frame_retry_count += 1
                logger.warning(f"获取帧失败 ({frame_retry_count}/{max_frame_retries}): {camera_id}")

                if frame_retry_count >= max_frame_retries:
                    await manager.send_message(json.dumps({"error": "连续多次无法获取视频帧，尝试重新连接"}),
                                               connection_id)
                    # 等待一段时间再继续尝试
                    time.sleep(1)

                # 发送空帧消息
                await manager.send_message(json.dumps({"type": "empty_frame", "retry_count": frame_retry_count}),
                                           connection_id)
                continue
            else:
                # 成功获取帧，重置重试计数
                frame_retry_count = 0

            # 执行检测
            try:
                process_start_time = time.perf_counter()

                # 执行目标检测
                results = model(frame, conf=conf, classes=classes)
                inference_time = time.perf_counter() - process_start_time

                # 绘制检测结果
                annotated_frame = results[0].plot()

                # 转换为JPEG并编码为Base64
                _, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                frame_base64 = base64.b64encode(buffer).decode('utf-8')

                # 统计检测到的类别
                class_counts = {}
                if results[0].boxes is not None:
                    for box in results[0].boxes:
                        class_id = int(box.cls)
                        class_name = model.names[class_id]
                        class_counts[class_name] = class_counts.get(class_name, 0) + 1

                # 计算处理时间
                processing_time = time.perf_counter() - process_start_time
                logger.info(f"处理时间: {processing_time:.3f}秒, 推理时间: {inference_time:.3f}秒")

                # 发送结果到客户端
                message = {
                    "image_base64": f"data:image/jpeg;base64,{frame_base64}",
                    "inference_time": inference_time,
                    "processing_time": processing_time,  # 添加处理时间
                    "fps": fps_limit,  # 显示设定的FPS，而不是计算值
                    "object_count": len(results[0].boxes) if results[0].boxes is not None else 0,
                    "classes": class_counts,
                    "timestamp": time.time()
                }

                await manager.send_message(json.dumps(message), connection_id)

                # 检查处理时间是否超过间隔时间
                if processing_time > frame_interval:
                    logger.warning(f"警告: 处理时间({processing_time:.3f}秒)超过帧间隔时间({frame_interval:.3f}秒)")

            except WebSocketDisconnect:
                logger.info(f"WebSocket连接已关闭，终止处理帧: {connection_id}")
                break
            except Exception as e:
                frame_retry_count += 1
                logger.error(f"处理帧时出错 ({frame_retry_count}/{max_frame_retries}): {str(e)}")

                if frame_retry_count >= max_frame_retries:
                    await manager.send_message(json.dumps({"error": "连续多次处理帧失败，尝试重新连接"}), connection_id)
                    # 等待一段时间再继续尝试
                    time.sleep(1)

                # 发送错误消息
                await manager.send_message(
                    json.dumps({"type": "processing_error", "error": str(e), "retry_count": frame_retry_count}),
                    connection_id)

    except WebSocketDisconnect:
        logger.info(f"客户端断开连接: {connection_id}")
        # 获取RTSP URL并断开连接
        rtsp_url = next((url for url, conns in manager.rtsp_connections.items() if
                         connection_id in [k for k in manager.active_connections]), None)
        if rtsp_url:
            manager.disconnect(connection_id, rtsp_url)
    except Exception as e:
        logger.error(f"WebSocket处理异常: {str(e)}")
        # 获取RTSP URL并断开连接
        rtsp_url = next((url for url, conns in manager.rtsp_connections.items() if
                         connection_id in [k for k in manager.active_connections]), None)
        if rtsp_url:
            manager.disconnect(connection_id, rtsp_url)
    finally:
        # 确保资源被释放
        if connection_id in manager.active_connections:
            # 获取RTSP URL并断开连接
            rtsp_url = next((url for url, conns in manager.rtsp_connections.items() if
                             connection_id in [k for k in manager.active_connections]), None)
            if rtsp_url:
                manager.disconnect(connection_id, rtsp_url)


# 全局连接管理器实例
manager = ConnectionManager()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8008)