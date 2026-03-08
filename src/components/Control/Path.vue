<template>
  <main class="center">
    <div ref="canvasRef" class="canvas">
      <!-- 背景网络 -->
      <div class="floor-bg"></div>

      <!-- 路径绘制 -->
      

      <!-- 视频 -->
      <el-card v-show="videoReady" ref="canvasRef" class="video" shadow="never" :style="{ left: videoPos.x + 'px', top: videoPos.y + 'px' }">
        <template #header>
          <div class="video-head" @pointerdown="onVideoDragStart" :class="{ dragging }">
            <span>视频直播窗口</span>
            <el-button circle size="small" class="video-setting-btn" @pointerdown.stop>
              <el-icon><Setting /></el-icon>
            </el-button>
          </div>
        </template>

        <div class="video-body">
          <div class="video-player">
            <iframe
              :src="liveUrl"
              scrolling="no"
              frameborder="0"
              allow="autoplay; fullscreen"
            ></iframe>
          </div>
        </div>

      </el-card>
    </div>
  </main>
</template>

<script setup>
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import { Setting, Position, VideoPlay, Back, Right, Microphone, FullScreen } from '@element-plus/icons-vue'

// 路径绘制
const pathCanvas = ref(null)  // 绘制路径的canvas
const trail = []  // 存储路径点

const pos = ref({ x: 300, y: 200 })  // 飞机位置
const yaw = ref(0)  // 偏转角度
const altitude = ref(10)  // 高度
const drawingPath = ref(false)  // 控制是否绘制路径

// 记录路径
function recordTrail() {
  const now = performance.now()
  trail.push({
    x: pos.value.x,
    y: pos.value.y,
    t: now
  })

  // 保持路径在屏幕上的有效时间
  const maxTrailTime = 5000  // 5秒内的轨迹
  while (trail.length && now - trail[0].t > maxTrailTime) {
    trail.shift()
  }
}

// 绘制路径


// 直播流
const liveUrl = ref('http://192.168.246.214:8889/live') // 或 /stream

// 视频拖拽逻辑
const videoPos = ref({ x: 0, y: 0 }) // 初始位置（距离右上角你原来是 right:22/top:18，这里用 left:22/top:18）

// 放置右上角
const canvasRef = ref(null)
const videoRef = ref(null)
const videoReady = ref(false)

onMounted(() => {
  const rightOffset = 22
  const topOffset = 18
  const canvasW = canvasRef.value?.clientWidth ?? 0
  const videoW = videoRef.value?.$el?.offsetWidth ?? 430

  videoPos.value.x = Math.max(0, canvasW - videoW - rightOffset)
  videoPos.value.y = topOffset

  videoReady.value = true
})

const dragging = ref(false)
let startX = 0
let startY = 0
let originX = 0
let originY = 0

function onVideoDragStart(e) {
  // 鼠标左键才拖
  if (e.pointerType === 'mouse' && e.button !== 0) return

  dragging.value = true
  startX = e.clientX
  startY = e.clientY
  originX = videoPos.value.x
  originY = videoPos.value.y

  document.body.style.userSelect = 'none'
  document.addEventListener('pointermove', onVideoDragMove, { passive: true })
  document.addEventListener('pointerup', onVideoDragEnd, { passive: true })
  document.addEventListener('pointercancel', onVideoDragEnd, { passive: true })
}

function onVideoDragMove(e) {
  if (!dragging.value) return
  const dx = e.clientX - startX
  const dy = e.clientY - startY
  videoPos.value.x = originX + dx
  videoPos.value.y = originY + dy
}

function onVideoDragEnd() {
  dragging.value = false
  document.body.style.userSelect = ''
  document.removeEventListener('pointermove', onVideoDragMove)
  document.removeEventListener('pointerup', onVideoDragEnd)
  document.removeEventListener('pointercancel', onVideoDragEnd)
}

onBeforeUnmount(() => {
  document.removeEventListener('pointermove', onVideoDragMove)
  document.removeEventListener('pointerup', onVideoDragEnd)
  document.removeEventListener('pointercancel', onVideoDragEnd)
})

</script>


<style scoped>
.center {
  position: relative;
  overflow: hidden;
  background: radial-gradient(1200px 700px at 40% 30%, rgba(30, 120, 255, 0.16), transparent 60%),
    radial-gradient(900px 500px at 70% 70%, rgba(0, 220, 255, 0.10), transparent 55%);
}

.canvas {
  position: relative;
  height: 100%;
  width: 100%;
  isolation: isolate;
}

.floor-bg {
  position: absolute;
  inset: 0;
  z-index: 1;
  opacity: 0.45;
  pointer-events: none;
  background:
    linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px) 0 0 / 40px 40px,
    linear-gradient(90deg, rgba(255,255,255,0.06) 1px, transparent 1px) 0 0 / 40px 40px,
    radial-gradient(800px 450px at 50% 30%, rgba(255,255,255,0.10), transparent 60%);
}

.background-canvas {
  position: absolute;
  z-index: 0;
}

.video{
  position:absolute;
  z-index:10;
  width:430px;
  height:265px;
  border-radius:12px;
  overflow:hidden;

  background: rgba(18, 70, 150, 0.01);      /* 蓝色偏透明 */
  border: 1px solid rgba(120, 200, 255, 0.35);
  box-shadow: 0 10px 30px rgba(0,0,0,0.35), 0 0 18px rgba(80,160,255,0.25);
  backdrop-filter: blur(2px);               /* 玻璃感（部分浏览器需要） */
}

/* 2) el-card 的 header 变成透明蓝，并且分割线也改掉 */
.video :deep(.el-card__header){
  background: rgba(18, 70, 150, 0.1);
  border-bottom: 1px solid rgba(120, 200, 255, 0.18);
  padding: 10px 12px;
}

/* 设置按钮：默认态 */
.video :deep(.video-setting-btn){
  background: rgba(18, 70, 150, 0.35);
  border: 1px solid rgba(120, 200, 255, 0.35);
  color: rgba(230, 250, 255, 0.95); /* 影响图标/文字 */
  backdrop-filter: blur(6px);
}

/* hover 态 */
.video :deep(.video-setting-btn:hover){
  background: rgba(18, 70, 150, 0.55);
  border-color: rgba(120, 200, 255, 0.55);
}

/* active/按下态 */
.video :deep(.video-setting-btn:active){
  background: rgba(18, 70, 150, 0.70);
}

/* 图标本身（有时需要单独指定） */
.video :deep(.video-setting-btn .el-icon){
  color: rgba(230, 250, 255, 0.95);
}


/* 3) el-card 的 body 也必须透明，否则会继续白底 */
.video :deep(.el-card__body){
  background: transparent;
  padding: 12px;
  height: calc(100% - 44px); /* 让 body 吃满剩余高度（按你header实际高度微调） */
}

/* 4) 标题文字从黑色改成偏亮的蓝白 */
.video-head{
  display:flex;
  align-items:center;
  justify-content:space-between;
  color: rgba(230, 250, 255, 0.95);
  font-size: 14px;
  opacity: 1;
}

/* 5) 你的视频容器和 iframe 保持不变即可 */
.video-player{
  flex:1;
  position:relative;
  border-radius:10px;
  overflow:hidden;
}
.video-player iframe{
  position:absolute;
  inset:0;
  width:100%;
  height:100%;
  border:0;
}

</style>
