"""
多线程高性能版本 - YOLO + PaddleOCR V5 (GPU加速)
PaddleOCR安装: pip install paddlepaddle-gpu paddleocr
或CPU版本: pip install paddlepaddle paddleocr
"""
import cv2
import numpy as np
from ultralytics import YOLO
from paddleocr import PaddleOCR
import time
from collections import deque
from threading import Thread, Lock
import queue
from PIL import Image, ImageDraw, ImageFont
import subprocess

def cv2_add_chinese_text(img, text, position, textColor=(0, 255, 0), textSize=30):
    """
    向 OpenCV 图片添加中文
    :param img: OpenCV 图片对象 (numpy array)
    :param text: 要写入的中文文本
    :param position: 文字左上角坐标 (x, y)
    :param textColor: 文字颜色 (B, G, R)
    :param textSize: 文字大小
    :return: 绘制了中文的 OpenCV 图片
    """
    if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)

    # 字体的格式，请注意：
    # 1. 确保你的系统中存在该字体文件
    # 2. Windows 下通常在 "C:/Windows/Fonts/simhei.ttf" (黑体) 或 "simsun.ttc" (宋体)
    # 3. Linux/Mac 下需替换为你系统中的中文字体路径
    fontStyle = ImageFont.truetype(
        "simhei.ttf", textSize, encoding="utf-8")

    # 绘制文本
    draw.text(position, text, fill=textColor, font=fontStyle)

    # 转换回 OpenCV 格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

class HighPerformanceDetectorPaddle:
    def __init__(self, stream_source = 0, yolo_model='yolo11n.pt', use_gpu=True,rtsp_url=None):
        print("="*60)
        print("🚀 高性能检测系统 (PaddleOCR V5)")
        print("="*60)
        self.rtsp_url = rtsp_url
        self.pipe = None

        self.use_gpu = use_gpu
        print(f"🎮 GPU模式: {'✅ 启用' if use_gpu else '❌ 禁用'}")

        # 摄像头
        try:
            self.source = int(stream_source)
            source_type = "USB Camera"
        except ValueError:
            self.source = stream_source
            source_type = "RTSP/Video Stream"

        print(f"📹 打开视频源: {self.source} [{source_type}]")

        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise Exception(f"无法打开:{self.source}")

        if source_type == "USB Camera":
            # 只有 USB 摄像头才需要手动设置分辨率
            # RTSP 流的分辨率由推流端决定，客户端强行 set 通常无效或导致错误
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            print("✅ USB摄像头参数已配置")
        else:
            # 对于 RTSP，稍微做一下缓冲区优化（可选）
            # 读取实际流的分辨率用于显示信息
            w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"✅ RTSP流已连接 (分辨率: {w}x{h})")

        print("✅ 视频源初始化完成")

        # YOLO模型
        print(f"📦 加载YOLO模型: {yolo_model}")
        self.yolo = YOLO(yolo_model)
        self.yolo.fuse()
        print("✅ YOLO模型已加载")

        # PaddleOCR - 延迟初始化
        self.ocr = None

        # 线程控制
        self.running = False
        self.yolo_queue = queue.Queue(maxsize=2)
        self.ocr_queue = queue.Queue(maxsize=2)

        # 结果存储
        self.latest_detections = []
        self.latest_ocr = []
        self.detections_lock = Lock()
        self.ocr_lock = Lock()

        # 性能统计
        self.fps_deque = deque(maxlen=30)
        self.frame_count = 0
        self.yolo_fps = 0
        self.ocr_fps = 0
        self.ocr_processing = False
        self.last_ocr_time = 0

        # 显示设置
        self.show_detections = True
        self.show_ocr = True
        self.show_info = True
        # 在 self.show_info = True 后面添加：
        self.auto_ocr = True  # 自动OCR开关
        self.ocr_interval = 1.0  # 自动OCR间隔（秒）
        self.last_auto_ocr_time = 0  # 上次自动OCR时间
        # 颜色
        self.colors = {}
        self.color_palette = [
            (0, 212, 255), (74, 222, 128), (251, 191, 36), (239, 68, 68),
            (168, 85, 247), (236, 72, 153), (20, 184, 166), (249, 115, 22)
        ]

        print("\n⌨️  控制键:")
        print("   q - 退出")
        print("   s - 截图")
        print("   o - 触发OCR识别")
        print("   c - 清除OCR结果")
        print("   d - 切换检测框显示")
        print("   i - 切换信息面板")
        print("="*60)
        print()

    def _init_paddle_ocr(self):
        if self.ocr is None:
            print("📦 初始化 PaddleOCR (新Pipeline版)...")

            try:
                self.ocr = PaddleOCR(
                    use_gpu=False,
                    lang='ch',
                    use_textline_orientation=True
                )
                print("✅ PaddleOCR 初始化成功")

                dummy = np.zeros((100, 100, 3), dtype=np.uint8)
                self.ocr.ocr(dummy)
                print("🔥 模型预热完成")

            except Exception as e:
                print("❌ PaddleOCR 初始化失败:", e)
                raise

    def get_color(self, class_name):
        """获取类别颜色"""
        if class_name not in self.colors:
            idx = len(self.colors) % len(self.color_palette)
            self.colors[class_name] = self.color_palette[idx]
        return self.colors[class_name]

    def yolo_worker(self):
        """YOLO检测线程"""
        print("🧵 YOLO线程已启动")
        yolo_frame_count = 0
        last_time = time.time()

        while self.running:
            try:
                frame = self.yolo_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            # YOLO检测
            results = self.yolo(frame, verbose=False, conf=0.25, imgsz=640)

            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    detections.append({
                        'class': result.names[int(box.cls[0])],
                        'confidence': float(box.conf[0]),
                        'bbox': [int(x1), int(y1), int(x2), int(y2)]
                    })

            # 更新检测结果
            with self.detections_lock:
                self.latest_detections = detections

            # 计算YOLO FPS
            yolo_frame_count += 1
            if time.time() - last_time >= 1.0:
                self.yolo_fps = yolo_frame_count
                yolo_frame_count = 0
                last_time = time.time()

        print("🛑 YOLO线程已停止")

    def ocr_worker(self):
        """PaddleOCR识别线程"""
        print("🧵 OCR线程已启动")
        self._init_paddle_ocr()

        ocr_count = 0
        last_time = time.time()

        while self.running:
            try:
                frame = self.ocr_queue.get(timeout=0.5)
                self.ocr_processing = True
            except queue.Empty:
                self.ocr_processing = False
                continue

            # OCR识别
            start_time = time.time()

            try:
                # PaddleOCR调用（新版本不需要cls参数）
                result = self.ocr.ocr(frame)

                ocr_results = []
                print("🔍 OCR原始结果:", result)

                # 解析PaddleOCR结果
                ocr_results = []

                if result and isinstance(result, list) and len(result) > 0:
                    res = result[0]

                    texts = res.get("rec_texts", [])
                    scores = res.get("rec_scores", [])
                    polys = res.get("rec_polys", [])

                    for text, score, poly in zip(texts, scores, polys):
                        if score > 0.5:
                            ocr_results.append({
                                'text': text,
                                'confidence': float(score),
                                'bbox': [[int(p[0]), int(p[1])] for p in poly]
                            })

                elapsed = (time.time() - start_time) * 1000

                # 更新OCR结果
                with self.ocr_lock:
                    self.latest_ocr = ocr_results
                    self.last_ocr_time = time.time()

                # 计算OCR FPS
                ocr_count += 1
                if time.time() - last_time >= 1.0:
                    self.ocr_fps = ocr_count
                    ocr_count = 0
                    last_time = time.time()

                print(f"✅ OCR完成: {len(ocr_results)} 个文字, 耗时 {elapsed:.0f}ms")
                for ocr in ocr_results:
                    print(f"   - {ocr['text']} ({ocr['confidence']:.2f})")

            except Exception as e:
                print(f"❌ OCR错误: {e}")
                import traceback
                traceback.print_exc()

            finally:
                self.ocr_processing = False

        print("🛑 OCR线程已停止")

    def draw_detections(self, frame, detections):
        """绘制检测框"""
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            color = self.get_color(det['class'])

            # 边框
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # 标签
            label = f"{det['class']} {det['confidence']:.2f}"
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(frame, (x1, y1 - 25), (x1 + w + 10, y1), color, -1)
            cv2.putText(frame, label, (x1 + 5, y1 - 7),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)

        return frame

    def draw_ocr(self, frame, ocr_results):
        """
        绘制OCR结果 (支持中文)
        优化策略：OpenCV画几何图形 -> 转PIL画中文 -> 转回OpenCV
        """
        # 1. 初始化字体 (建议放在 __init__ 中只加载一次，这里为了演示放在这里)
        # Windows 默认黑体: "simhei.ttf", Mac: "/System/Library/Fonts/PingFang.ttc"
        font_path = "simhei.ttf"
        font_size = 20
        try:
            font = ImageFont.truetype(font_path, font_size, encoding="utf-8")
        except OSError:
            # 如果找不到字体，回退到默认
            font = ImageFont.load_default()
            print(f"⚠️ 未找到字体 {font_path}，已回退默认字体")

        # 2. 第一轮循环：使用 OpenCV 绘制几何图形 (框、半透明背景、标签底色)
        #    同时收集需要绘制的文字信息
        text_tasks = []  # 存储待绘制的文字任务 [(x, y, text, color), ...]

        for ocr in ocr_results:
            bbox = ocr['bbox']
            points = np.array(bbox, np.int32)

            # --- 几何图形绘制 (保持 OpenCV 的高性能) ---

            # A. 绘制多边形框
            cv2.polylines(frame, [points], True, (74, 222, 128), 2)

            # B. 填充半透明背景
            overlay = frame.copy()
            cv2.fillPoly(overlay, [points], (74, 222, 128))
            cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)

            # --- 准备文字标签信息 ---
            x, y = int(bbox[0][0]), int(bbox[0][1])
            text = ocr['text']
            conf = ocr['confidence']
            label = f"{text} ({conf:.2f})"

            # C. 计算中文文字的宽高 (关键：用 PIL 字体计算，而不是 cv2.getTextSize)
            # getbbox 返回 (left, top, right, bottom)
            left, top, right, bottom = font.getbbox(label)
            w = right - left
            h = bottom - top

            # D. 绘制标签背景 (OpenCV rectangle)
            # 注意：Pillow文字绘制基线和OpenCV不同，y坐标需要微调
            # 这里背景框的高度适当加高一点以容纳中文
            cv2.rectangle(frame, (x, y - h - 10), (x + w + 10, y), (74, 222, 128), -1)

            # E. 将文字任务加入列表，稍后统一绘制
            # 记录：(坐标x, 坐标y, 文本内容)
            # 这里的 y - h - 5 是为了让文字落在绿色背景框里
            text_tasks.append((x + 5, y - h - 5, label))

        # 3. 转换图片格式 (只做一次转换，性能损耗最小)
        img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)

        # 4. 第二轮循环：批量绘制中文
        for (tx, ty, t_label) in text_tasks:
            # 参数：坐标, 文本, 颜色(RGB), 字体
            draw.text((tx, ty), t_label, fill=(0, 0, 0), font=font)

        # 5. 转回 OpenCV 格式并返回
        return cv2.cvtColor(np.asarray(img_pil), cv2.COLOR_RGB2BGR)

    def draw_info(self, frame, detections, fps):
        """绘制信息面板"""
        h, w = frame.shape[:2]

        # 背景
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (340, 200), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # 文字
        y = 35
        cv2.putText(frame, f"Display FPS: {fps:.1f}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 212, 255), 2)
        y += 30
        cv2.putText(frame, f"YOLO FPS: {self.yolo_fps}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (74, 222, 128), 2)
        y += 30
        cv2.putText(frame, f"Detections: {len(detections)}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (251, 191, 36), 2)
        y += 30

        # OCR状态
        if self.ocr_processing:
            ocr_text = "Processing..."
            color = (239, 68, 68)
        elif self.latest_ocr:
            ocr_text = f"{len(self.latest_ocr)} texts"
            color = (74, 222, 128)
        else:
            ocr_text = "Press 'o'"
            color = (168, 85, 247)
        cv2.putText(frame, f"OCR: {ocr_text}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        y += 30
        gpu_text = "GPU ✅" if self.use_gpu else "CPU"
        cv2.putText(frame, f"Mode: {gpu_text}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (236, 72, 153), 2)

        y += 30
        cv2.putText(frame, f"Frame: {self.frame_count}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # 类别统计
        class_counts = {}
        for det in detections:
            cls = det['class']
            class_counts[cls] = class_counts.get(cls, 0) + 1

        if class_counts:
            y = h - 20 - len(class_counts) * 25
            for cls, count in class_counts.items():
                color = self.get_color(cls)
                cv2.putText(frame, f"{cls}: {count}", (20, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                y += 25

        return frame

    def request_ocr(self, frame):
        """请求OCR处理"""
        if self.ocr_processing:
            print("⚠️ OCR正在处理中，请稍后...")
            return

        # 清空队列，只保留最新请求
        while not self.ocr_queue.empty():
            try:
                self.ocr_queue.get_nowait()
            except:
                break

        try:
            self.ocr_queue.put_nowait(frame.copy())
            print("📝 OCR请求已提交")
            return True
        except queue.Full:
            print("⚠️ OCR队列已满")
            return False

    def run(self):
        """主循环"""
        print("🚀 启动检测系统...")

        # 启动工作线程
        self.running = True
        yolo_thread = Thread(target=self.yolo_worker, daemon=True, name="YOLO")
        ocr_thread = Thread(target=self.ocr_worker, daemon=True, name="PaddleOCR")
        yolo_thread.start()
        ocr_thread.start()

        print("✅ 所有线程已启动")
        print("🎬 开始检测...\n")
        ret, first_frame = self.cap.read()
        if not ret: return
        height, width = first_frame.shape[:2]

        # 【修改点3】初始化 FFmpeg 管道 (如果有 RTSP 地址)
        if self.rtsp_url:
            print(f"📺 正在连接推流服务器: {self.rtsp_url}")
            # 注意：这里加上了 -bf 0 和 -profile:v baseline 以完美兼容 WebRTC
            command = [
                'ffmpeg',
                '-y', '-an',
                '-f', 'rawvideo',
                '-vcodec', 'rawvideo',
                '-pix_fmt', 'bgr24',  # OpenCV 默认也是 bgr24
                '-s', f"{width}x{height}",  # 动态获取宽高
                '-r', '25',  # 帧率
                '-i', '-',  # 从标准输入读取
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-preset', 'ultrafast',
                '-tune', 'zerolatency',
                '-profile:v', 'baseline',  # 关键：兼容 WebRTC
                '-bf', '0',  # 关键：去 B 帧
                '-rtsp_transport', 'tcp',
                '-f', 'rtsp',
                self.rtsp_url
            ]
            # 启动子进程
            try:
                self.pipe = subprocess.Popen(command, stdin=subprocess.PIPE)
                print("✅ 推流管道建立成功")
            except Exception as e:
                print(f"❌ FFmpeg启动失败: {e}")
        try:
            while True:
                start_time = time.time()

                # 读取帧
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ 无法读取摄像头")
                    break

                self.frame_count += 1

                # 提交YOLO处理
                # 自动OCR逻辑
                if self.auto_ocr:
                    current_time = time.time()
                    if current_time - self.last_auto_ocr_time >= self.ocr_interval:
                        if self.request_ocr(frame):  # 只有成功提交才更新时间
                            self.last_auto_ocr_time = current_time
                try:
                    if self.yolo_queue.full():
                        self.yolo_queue.get_nowait()
                    self.yolo_queue.put_nowait(frame.copy())
                except:
                    pass

                # 获取最新结果
                with self.detections_lock:
                    detections = self.latest_detections.copy()

                with self.ocr_lock:
                    ocr_results = self.latest_ocr.copy()

                # 绘制
                display_frame = frame.copy()

                if self.show_detections and detections:
                    display_frame = self.draw_detections(display_frame, detections)

                if self.show_ocr and ocr_results:
                    display_frame = self.draw_ocr(display_frame, ocr_results)

                # 计算FPS
                elapsed = time.time() - start_time
                self.fps_deque.append(elapsed)
                fps = 1.0 / (sum(self.fps_deque) / len(self.fps_deque))

                if self.show_info:
                    display_frame = self.draw_info(display_frame, detections, fps)

                if self.pipe:
                    try:
                        self.pipe.stdin.write(display_frame.tobytes())
                    except Exception as e:
                        print(f"⚠️ 推流中断: {e}")
                        self.pipe = None  # 避免重复报错






        except KeyboardInterrupt:
            print("\n⚠️ 程序被中断")

        finally:
            # 清理
            self.running = False
            if self.pipe:
                self.pipe.stdin.close()
                self.pipe.wait()
            time.sleep(0.5)  # 等待线程结束
            self.cap.release()
            cv2.destroyAllWindows()
            print("✅ 程序已退出")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='YOLO + PaddleOCR V5 实时检测')
    parser.add_argument('--camera', type=str, default="0", help='视频源: 传入摄像头ID (如 0) 或 RTSP流地址/视频文件路径')
    parser.add_argument('--push', type=str, default="", help='推流地址, 例如: rtsp://IP:8554/mystream')
    parser.add_argument('--yolo', type=str, default='yolo11n.pt',
                       help='YOLO模型 (默认: yolov8n.pt)')
    parser.add_argument('--cpu', action='store_true', help='强制使用CPU')

    args = parser.parse_args()

    use_gpu = not args.cpu

    try:
        detector = HighPerformanceDetectorPaddle(
            stream_source=args.camera,
            yolo_model=args.yolo,
            rtsp_url=args.push if args.push else None,
            use_gpu=use_gpu
        )
        detector.run()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()