<template>
  <div class="video-analysis-container">
    <div class="header">
      <h1>🎥 实时视频分析系统</h1>
      <div class="connection-status">
        <span :class="['status-indicator', connectionStatus]">
          ● {{ statusText }}
        </span>
        <button @click="toggleConnection" class="btn-control">
          {{ isConnected ? '断开' : '连接' }}
        </button>
      </div>
    </div>

    <div class="main-grid">
      <!-- 视频显示区域 -->
      <div class="video-section">
        <div class="video-wrapper">
          <canvas ref="videoCanvas" class="video-canvas"></canvas>
          <div v-if="!isConnected" class="overlay">
            <p>等待连接...</p>
          </div>
          
          <!-- 视频上的检测框叠加层 -->
          <canvas ref="overlayCanvas" class="overlay-canvas"></canvas>
        </div>
        
        <div class="video-controls">
          <button @click="saveSnapshot" class="btn-secondary">
            📸 截图
          </button>
          <button 
            @click="requestOCR" 
            :disabled="ocrProcessing"
            class="btn-secondary"
          >
            {{ ocrProcessing ? '⏳ OCR处理中...' : '📝 执行OCR识别' }}
          </button>
          <label class="toggle-switch">
            <input type="checkbox" v-model="showDetections" />
            <span>显示检测框</span>
          </label>
        </div>

        <!-- 性能指标 -->
        <div class="metrics-bar">
          <div class="metric">
            <span class="metric-label">视频FPS:</span>
            <span class="metric-value">{{ videoFPS }}</span>
          </div>
          <div class="metric">
            <span class="metric-label">检测FPS:</span>
            <span class="metric-value">{{ detectionFPS }}</span>
          </div>
          <div class="metric">
            <span class="metric-label">延迟:</span>
            <span class="metric-value">{{ latency }}ms</span>
          </div>
        </div>
      </div>

      <!-- 信息面板 -->
      <div class="info-section">
        <!-- 统计信息 -->
        <div class="info-card">
          <h2>📊 实时统计</h2>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ detections.length }}</div>
              <div class="stat-label">当前检测</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ totalDetections }}</div>
              <div class="stat-label">累计检测</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ ocrResults.length }}</div>
              <div class="stat-label">OCR结果</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ frameCount }}</div>
              <div class="stat-label">总帧数</div>
            </div>
          </div>
        </div>

        <!-- 目标检测结果 -->
        <div class="info-card">
          <h2>🎯 检测对象</h2>
          <div class="scrollable-content">
            <transition-group name="list">
              <div
                v-for="(detection, index) in detections"
                :key="`det-${frameCount}-${index}`"
                class="detection-item"
                :style="{ borderLeftColor: getClassColor(detection.class) }"
              >
                <div class="item-header">
                  <span class="item-class">{{ detection.class }}</span>
                  <span class="confidence">
                    {{ (detection.confidence * 100).toFixed(1) }}%
                  </span>
                </div>
              </div>
            </transition-group>
            <p v-if="detections.length === 0" class="empty-message">
              未检测到对象
            </p>
          </div>
        </div>

        <!-- OCR识别结果 -->
        <div class="info-card">
          <div class="card-header">
            <h2>📝 OCR识别</h2>
            <span v-if="lastOCRTime" class="time-badge">
              {{ formatTime(lastOCRTime) }}
            </span>
          </div>
          <div class="scrollable-content">
            <transition-group name="list">
              <div
                v-for="(ocr, index) in ocrResults"
                :key="`ocr-${lastOCRTime}-${index}`"
                class="ocr-item"
              >
                <div class="item-header">
                  <span class="item-text">{{ ocr.text }}</span>
                  <span class="confidence">
                    {{ (ocr.confidence * 100).toFixed(1) }}%
                  </span>
                </div>
              </div>
            </transition-group>
            <p v-if="ocrResults.length === 0" class="empty-message">
              点击"执行OCR识别"按钮进行文字识别
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'

const props = defineProps({
  wsUrl: {
    type: String,
    default: 'ws://localhost:8765'
  }
})

const emit = defineEmits(['connected', 'disconnected', 'error'])

// Refs
const videoCanvas = ref(null)
const overlayCanvas = ref(null)
const ws = ref(null)
const isConnected = ref(false)
const showDetections = ref(true)
const ocrProcessing = ref(false)

// 数据
const detections = ref([])
const ocrResults = ref([])
const frameCount = ref(0)
const totalDetections = ref(0)

// 性能指标
const videoFPS = ref(0)
const detectionFPS = ref(0)
const latency = ref(0)
const lastOCRTime = ref(null)

// Canvas上下文
let videoCtx = null
let overlayCtx = null

// 性能统计
let videoFrameCount = 0
let detectionFrameCount = 0
let lastVideoTime = Date.now()
let lastDetectionTime = Date.now()

// 颜色映射
const classColors = {}
const colorPalette = [
  '#00d4ff', '#4ade80', '#f59e0b', '#ef4444', 
  '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'
]

// Computed
const connectionStatus = computed(() => {
  return isConnected.value ? 'connected' : 'disconnected'
})

const statusText = computed(() => {
  return isConnected.value ? '已连接' : '未连接'
})

// 获取类别颜色
const getClassColor = (className) => {
  if (!classColors[className]) {
    const index = Object.keys(classColors).length % colorPalette.length
    classColors[className] = colorPalette[index]
  }
  return classColors[className]
}

// WebSocket连接
const connect = () => {
  if (ws.value?.readyState === WebSocket.OPEN) return

  try {
    ws.value = new WebSocket(props.wsUrl)

    ws.value.onopen = () => {
      console.log('✅ WebSocket已连接')
      isConnected.value = true
      emit('connected')
    }

    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleMessage(data)
      } catch (error) {
        console.error('解析消息失败:', error)
      }
    }

    ws.value.onerror = (error) => {
      console.error('WebSocket错误:', error)
      emit('error', error)
    }

    ws.value.onclose = () => {
      console.log('❌ WebSocket已断开')
      isConnected.value = false
      emit('disconnected')
      
      // 3秒后重连
      setTimeout(() => {
        if (!isConnected.value) {
          connect()
        }
      }, 3000)
    }
  } catch (error) {
    console.error('连接失败:', error)
    emit('error', error)
  }
}

// 处理不同类型的消息
const handleMessage = (data) => {
  switch (data.type) {
    case 'video':
      handleVideoFrame(data)
      break
    case 'detection':
      handleDetection(data)
      break
    case 'ocr':
      handleOCR(data)
      break
    case 'response':
      handleResponse(data)
      break
  }
}

// 处理视频帧
const handleVideoFrame = (data) => {
  if (!videoCtx || !data.image) return

  const img = new Image()
  img.onload = () => {
    // 设置canvas尺寸
    if (videoCanvas.value.width !== img.width || videoCanvas.value.height !== img.height) {
      videoCanvas.value.width = img.width
      videoCanvas.value.height = img.height
      overlayCanvas.value.width = img.width
      overlayCanvas.value.height = img.height
    }
    
    // 绘制视频帧
    videoCtx.drawImage(img, 0, 0)
    
    // 更新视频FPS
    videoFrameCount++
    const now = Date.now()
    if (now - lastVideoTime >= 1000) {
      videoFPS.value = Math.round(videoFrameCount * 1000 / (now - lastVideoTime))
      videoFrameCount = 0
      lastVideoTime = now
    }
  }
  
  img.src = `data:image/jpeg;base64,${data.image}`
}

// 处理检测结果
const handleDetection = (data) => {
  detections.value = data.detections || []
  frameCount.value = data.frame_number || 0
  totalDetections.value += detections.value.length
  latency.value = Math.round(data.processing_time_ms || 0)
  
  // 重绘检测框
  if (showDetections.value) {
    drawDetections()
  }
  
  // 更新检测FPS
  detectionFrameCount++
  const now = Date.now()
  if (now - lastDetectionTime >= 1000) {
    detectionFPS.value = Math.round(detectionFrameCount * 1000 / (now - lastDetectionTime))
    detectionFrameCount = 0
    lastDetectionTime = now
  }
}

// 处理OCR结果
const handleOCR = (data) => {
  ocrResults.value = data.ocr_texts || []
  lastOCRTime.value = Date.now()
  ocrProcessing.value = false
  console.log(`📝 OCR完成: ${ocrResults.value.length}个文字, 耗时${data.processing_time_ms}ms`)
}

// 处理响应
const handleResponse = (data) => {
  if (data.command === 'request_ocr') {
    if (!data.success) {
      ocrProcessing.value = false
      console.log('⚠️', data.message)
    }
  }
}

// 绘制检测框
const drawDetections = () => {
  if (!overlayCtx) return
  
  // 清空画布
  overlayCtx.clearRect(0, 0, overlayCanvas.value.width, overlayCanvas.value.height)
  
  if (!showDetections.value) return
  
  detections.value.forEach(det => {
    const [x1, y1, x2, y2] = det.bbox
    const width = x2 - x1
    const height = y2 - y1
    const color = getClassColor(det.class)
    
    // 绘制边框
    overlayCtx.strokeStyle = color
    overlayCtx.lineWidth = 3
    overlayCtx.strokeRect(x1, y1, width, height)
    
    // 绘制标签
    const label = `${det.class} ${(det.confidence * 100).toFixed(0)}%`
    overlayCtx.font = 'bold 16px Arial'
    const textWidth = overlayCtx.measureText(label).width
    
    overlayCtx.fillStyle = color
    overlayCtx.fillRect(x1, y1 - 30, textWidth + 20, 30)
    
    overlayCtx.fillStyle = '#000'
    overlayCtx.fillText(label, x1 + 10, y1 - 8)
  })
}

// 监听显示检测框的变化
watch(showDetections, (newVal) => {
  if (newVal) {
    drawDetections()
  } else {
    overlayCtx?.clearRect(0, 0, overlayCanvas.value.width, overlayCanvas.value.height)
  }
})

// 请求OCR识别
const requestOCR = () => {
  if (!isConnected.value || ocrProcessing.value) return
  
  ocrProcessing.value = true
  ws.value.send(JSON.stringify({
    command: 'request_ocr'
  }))
  
  console.log('📝 OCR识别请求已发送...')
  
  // 超时保护
  setTimeout(() => {
    if (ocrProcessing.value) {
      ocrProcessing.value = false
    }
  }, 10000)
}

// 截图
const saveSnapshot = () => {
  if (!videoCanvas.value) return
  
  // 创建临时canvas合并视频和检测框
  const tempCanvas = document.createElement('canvas')
  tempCanvas.width = videoCanvas.value.width
  tempCanvas.height = videoCanvas.value.height
  const tempCtx = tempCanvas.getContext('2d')
  
  // 绘制视频
  tempCtx.drawImage(videoCanvas.value, 0, 0)
  
  // 绘制检测框
  if (showDetections.value) {
    tempCtx.drawImage(overlayCanvas.value, 0, 0)
  }
  
  const link = document.createElement('a')
  link.download = `snapshot_${Date.now()}.png`
  link.href = tempCanvas.toDataURL()
  link.click()
}

// 断开连接
const disconnect = () => {
  if (ws.value) {
    ws.value.close()
    ws.value = null
  }
}

const toggleConnection = () => {
  if (isConnected.value) {
    disconnect()
  } else {
    connect()
  }
}

// 格式化时间
const formatTime = (timestamp) => {
  const diff = Date.now() - timestamp
  if (diff < 60000) {
    return `${Math.floor(diff / 1000)}秒前`
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  }
  return '很久前'
}

// 生命周期
onMounted(() => {
  videoCtx = videoCanvas.value?.getContext('2d')
  overlayCtx = overlayCanvas.value?.getContext('2d')
  connect()
})

onUnmounted(() => {
  disconnect()
})

defineExpose({
  connect,
  disconnect,
  isConnected,
  requestOCR
})
</script>

<style scoped>
/* ... 保持之前的样式 ... */
.video-analysis-container {
  width: 100%;
  min-height: 100vh;
  background: #1a1a1a;
  color: #fff;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

h1 {
  margin: 0;
  color: #00d4ff;
  font-size: 28px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 15px;
}

.status-indicator {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.status-indicator.connected {
  background: #166534;
  color: #4ade80;
}

.status-indicator.disconnected {
  background: #7f1d1d;
  color: #f87171;
}

.main-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.video-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.video-wrapper {
  position: relative;
  background: #2a2a2a;
  border-radius: 12px;
  overflow: hidden;
  min-height: 400px;
}

.video-canvas, .overlay-canvas {
  width: 100%;
  height: auto;
  display: block;
}

.overlay-canvas {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  color: #888;
  font-size: 18px;
}

.video-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.toggle-switch {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
  cursor: pointer;
  user-select: none;
}

.toggle-switch input {
  cursor: pointer;
}

.metrics-bar {
  display: flex;
  gap: 20px;
  padding: 12px;
  background: #2a2a2a;
  border-radius: 8px;
}

.metric {
  display: flex;
  gap: 8px;
  align-items: center;
}

.metric-label {
  color: #888;
  font-size: 13px;
}

.metric-value {
  color: #00d4ff;
  font-weight: bold;
  font-size: 14px;
}

.btn-control, .btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-control {
  background: #00d4ff;
  color: #000;
}

.btn-control:hover {
  background: #00b8e6;
}

.btn-secondary {
  background: #363636;
  color: #fff;
}

.btn-secondary:hover:not(:disabled) {
  background: #454545;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-card {
  background: #2a2a2a;
  border-radius: 12px;
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.info-card h2 {
  margin: 0 0 15px 0;
  color: #00d4ff;
  font-size: 18px;
}

.time-badge {
  background: #363636;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  color: #888;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-item {
  background: #363636;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #00d4ff;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: #888;
  margin-top: 8px;
}

.scrollable-content {
  max-height: 300px;
  overflow-y: auto;
}

.scrollable-content::-webkit-scrollbar {
  width: 6px;
}

.scrollable-content::-webkit-scrollbar-track {
  background: #363636;
  border-radius: 3px;
}

.scrollable-content::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 3px;
}

.detection-item, .ocr-item {
  background: #363636;
  padding: 12px;
  margin-bottom: 10px;
  border-radius: 8px;
  border-left: 3px solid;
}

.ocr-item {
  border-left-color: #4ade80;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-class, .item-text {
  font-weight: 600;
  font-size: 14px;
}

.confidence {
  color: #4ade80;
  font-weight: bold;
  font-size: 13px;
}

.empty-message {
  color: #666;
  text-align: center;
  padding: 20px;
  font-size: 14px;
}

.list-enter-active, .list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

@media (max-width: 1024px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
}
</style>