<template>
  <div class="yolo-page">
    <!-- 顶部状态栏 -->
    <div class="top-bar">
      <div class="top-left">
        <span class="live-tag"><span class="rec-dot"></span>LIVE DETECTION</span>
        <span class="sep">|</span>
        <span class="model-tag">YOLOv8-X · INT8 TensorRT</span>
      </div>
      <div class="top-right">
        <span>FPS: <b class="cyan">{{ fps }}</b></span>
        <span class="sep">|</span>
        <span>推理延迟: <b class="cyan">{{ inferMs }}ms</b></span>
        <span class="sep">|</span>
        <span>{{ clock }}</span>
      </div>
    </div>

    <!-- 主体：视频 + 侧栏 -->
    <div class="main-grid">
      <!-- 双视频区 -->
      <div class="video-col">
        <div class="video-panel">
          <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
          <div class="video-head">
            <span class="video-label">📹 原始视频流 / RAW STREAM</span>
            <span class="resolution">1920×1080 · H.264</span>
          </div>
          <div class="video-wrapper">
            <iframe
              src="http://192.168.3.4:8889/live"
              scrolling="no" frameborder="0"
              allow="autoplay; fullscreen"
            ></iframe>
            <div class="scanline-overlay"></div>
            <div class="crosshair"></div>
          </div>
        </div>

        <div class="video-panel">
          <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
          <div class="video-head">
            <span class="video-label">🎯 YOLO 实时检测 / DETECTION STREAM</span>
            <span class="det-count">检测目标: <b class="green">{{ totalDetections }}</b></span>
          </div>
          <div class="video-wrapper">
            <iframe
              src="http://192.168.3.4:8889/stream"
              scrolling="no" frameborder="0"
              allow="autoplay; fullscreen"
            ></iframe>
            <div class="scanline-overlay"></div>
          </div>
        </div>
      </div>


    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

/* ============ 模拟实时数据 ============ */
const clock = ref('')
const fps = ref(28)
const inferMs = ref(12)
const totalDetections = ref(47)
let timer = null



const tick = () => {
  clock.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
  fps.value = 24 + Math.floor(Math.random() * 8)
  inferMs.value = 8 + Math.floor(Math.random() * 10)
  totalDetections.value = 35 + Math.floor(Math.random() * 25)
}

onMounted(() => {
  tick()
  timer = setInterval(tick, 1500)
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.yolo-page {
  min-height:100vh; padding:14px 20px 20px;
  background:#061a2c; color:#e0e6ed;
  font-family:'Segoe UI','PingFang SC',sans-serif;
}

/* 顶部栏 */
.top-bar {
  display:flex; justify-content:space-between; align-items:center;
  padding:8px 16px; margin-bottom:14px;
  background:rgba(8,30,55,.7); border:1px solid rgba(58,163,255,.08); border-radius:4px;
  font-size:12px; color:#718096; letter-spacing:.5px;
}
.live-tag { color:#ff3366; display:inline-flex; align-items:center; gap:6px; font-weight:700; letter-spacing:1.5px; }
.rec-dot { width:8px; height:8px; border-radius:50%; background:#ff3366; box-shadow:0 0 10px #ff3366; animation:blink 1s infinite; }
@keyframes blink{0%,100%{opacity:1}50%{opacity:.2}}
.model-tag { color:#a0aec0; }
.sep { margin:0 10px; color:rgba(58,163,255,.2); }
.cyan { color:#00d4ff; }
.green { color:#00ff88; }

/* 主布局 */
.main-grid { display:grid; grid-template-columns:1fr; gap:16px; height:calc(100vh - 80px); }

/* 视频列 */
.video-col { display:flex; flex-direction:column; gap:16px; min-height:0; }
.video-panel {
  position:relative; flex:1; display:flex; flex-direction:column;
  padding:12px 14px; min-height:0;
  background:rgba(8,30,55,.85); border:1px solid rgba(58,163,255,.1); border-radius:6px;
}
.corner{position:absolute;width:12px;height:12px;border-color:#00d4ff;border-style:solid;border-width:0}
.corner.tl{top:-1px;left:-1px;border-top-width:2px;border-left-width:2px}
.corner.tr{top:-1px;right:-1px;border-top-width:2px;border-right-width:2px}
.corner.bl{bottom:-1px;left:-1px;border-bottom-width:2px;border-left-width:2px}
.corner.br{bottom:-1px;right:-1px;border-bottom-width:2px;border-right-width:2px}

.video-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }
.video-label { font-size:13px; font-weight:600; color:#e0e6ed; letter-spacing:.5px; }
.resolution { font-size:11px; color:#718096; font-family:'Courier New',monospace; }
.det-count { font-size:12px; color:#a0aec0; }

.video-wrapper {
  position:relative; flex:1; border-radius:4px; overflow:hidden; background:#000;
}
.video-wrapper iframe { position:absolute; inset:0; width:100%; height:100%; }

/* 扫描线效果 */
.scanline-overlay {
  position:absolute; inset:0; pointer-events:none;
  background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,212,255,.02) 2px,rgba(0,212,255,.02) 4px);
}
.scanline-overlay::after {
  content:''; position:absolute; left:0; right:0; height:80px;
  background:linear-gradient(180deg,rgba(0,212,255,.06),transparent);
  animation:scan 3s linear infinite;
}
@keyframes scan{0%{top:-80px}100%{top:100%}}

/* 十字准星 */
.crosshair {
  position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
  width:40px; height:40px; pointer-events:none;
}
.crosshair::before,.crosshair::after {
  content:''; position:absolute; background:rgba(0,212,255,.3);
}
.crosshair::before { width:1px; height:100%; left:50%; top:0; }
.crosshair::after  { height:1px; width:100%; top:50%; left:0; }
</style>
