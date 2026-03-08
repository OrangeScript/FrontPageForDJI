<template>
  <main class="center">
    <div ref="canvasRef" class="canvas">
      <!-- 1.背景网络 -->
      <div class="floor-bg"></div>

      <!-- 2.路线叠加层 -->
      <svg class="overlay" viewBox="0 0 1000 560" preserveAspectRatio="none">
        <path d="M 220 380 L 180 280 L 300 250 L 420 260 L 520 220" class="route-dashed" />
        <path d="M 520 220 L 420 260 L 420 360 L 280 360" class="route-solid" />
      </svg>

      <!-- 3.点位 -->
      <div class="wp wp-6">6</div>
      <div class="wp wp-7 active">7</div>
      <div class="wp wp-3">3</div>
      <div class="wp wp-2">2</div>
      <div class="wp wp-4">4</div>

      <div class="wp wp-5 drone" title="5">
        <el-icon :size="16"><Position /></el-icon>
      </div>

      <!-- 4. 图纸层：后续按任务动态替换图片 -->
      <div class="paper-layer">
        <!-- 方案A：直接放图片 -->
        <img class="paper-img" :src="paperUrl" alt="任务图纸" />
        <!-- 方案B：你也可以换成 <canvas class="paper-canvas" /> -->
      </div>

      <!-- 5.视频 -->
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
              src="http://192.168.246.214:8889/live" 
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

// const props = defineProps({
//   ui: { type: Object, required: true },
// })

// // 三张图纸：你把文件名换成你真实的三张图
// import paperInspect from '@/assets/Uav/paper_inspect.png'
// import paperPhoto from '@/assets/Uav/paper_photo.png'
// import paperRoute from '@/assets/Uav/paper_route.png'

// // 任务 -> 图纸映射
// const taskPaperMap = {
//   巡检: paperInspect,
//   拍照: paperPhoto,
//   定线: paperRoute,
// }

// // 当前图纸 URL（跟随 ui.taskType 变化）
// const paperUrl = computed(() => taskPaperMap[props.ui.taskType] || paperInspect)

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

.overlay {
  position: absolute;
  inset: 0;
  z-index: 2;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.route-dashed {
  fill: none;
  stroke: rgba(0, 255, 160, 0.75);
  stroke-width: 4;
  stroke-dasharray: 10 10;
  stroke-linecap: round;
}

.route-solid {
  fill: none;
  stroke: rgba(255, 60, 60, 0.85);
  stroke-width: 6;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.wp {
  position: absolute;
  z-index: 3;
  width: 30px;
  height: 30px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.95);
  background: rgba(0, 170, 255, 0.22);
  border: 1px solid rgba(0, 170, 255, 0.35);
  box-shadow: 0 0 18px rgba(0, 170, 255, 0.25);
}

.wp.active {
  background: rgba(0, 255, 210, 0.20);
  border: 1px solid rgba(0, 255, 210, 0.55);
  box-shadow: 0 0 20px rgba(0, 255, 210, 0.25);
}

.wp.drone {
  width: 34px;
  height: 34px;
}

.wp-6 { left: 160px; top: 240px; }
.wp-7 { left: 270px; top: 235px; }
.wp-3 { left: 345px; top: 250px; }
.wp-2 { left: 500px; top: 210px; }
.wp-4 { left: 320px; top: 340px; }
.wp-5 { left: 190px; top: 310px; }

/* 图纸层 */
.paper-layer {
  position: absolute;
  z-index: 9;
  pointer-events: none;
  overflow: hidden;

  /* 尺寸：不占满 */
  width: 90%;
  height: 75%;
  max-width: 1100px;   /* 可选：防止太大 */
  max-height: 700px;   /* 可选 */

  /* 居中 */
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}


/* 图纸图片 */
.paper-img {
  width: 100%;
  height: 100%;
  object-fit: contain; /* 或 cover，看你的图纸需求 */
  opacity: 0.95;       /* 想“更像底图”可以略微透明 */
  pointer-events: none; /* 底图不抢点击，点位可以点到 */
}

/* 1) 整个视频卡片：蓝色半透明 + 发光边框 + 模糊玻璃感 */
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
