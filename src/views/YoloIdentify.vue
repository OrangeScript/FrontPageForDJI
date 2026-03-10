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

      <!-- 右侧数据面板 -->
      <div class="side-col">
        <!-- 检测统计 -->
        <div class="side-panel">
          <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
          <div class="side-title"><span class="accent-bar"></span>实时检测统计</div>
          <div class="det-stats">
            <div class="det-item" v-for="d in detStats" :key="d.label">
              <span class="det-icon">{{ d.icon }}</span>
              <span class="det-label">{{ d.label }}</span>
              <span class="det-val" :style="{ color: d.color }">{{ d.count }}</span>
            </div>
          </div>
        </div>

        <!-- 置信度分布 -->
        <div class="side-panel">
          <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
          <div class="side-title"><span class="accent-bar"></span>置信度分布</div>
          <div class="conf-bars">
            <div class="conf-row" v-for="c in confBars" :key="c.range">
              <span class="conf-label">{{ c.range }}</span>
              <div class="conf-track">
                <div class="conf-fill" :style="{ width: c.pct + '%', background: c.color }"></div>
              </div>
              <span class="conf-pct">{{ c.pct }}%</span>
            </div>
          </div>
        </div>

        <!-- 检测日志 -->
        <div class="side-panel log-panel">
          <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
          <div class="side-title"><span class="accent-bar"></span>检测事件日志</div>
          <div class="log-scroll" ref="logRef">
            <div class="log-item" v-for="(log, i) in logs" :key="i">
              <span class="log-time">{{ log.time }}</span>
              <span class="log-cls" :style="{ color: log.color }">{{ log.cls }}</span>
              <span class="log-conf">{{ log.conf }}%</span>
            </div>
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

const detStats = ref([
  { icon:'🚗', label:'车辆',   count:18, color:'#3aa3ff' },
  { icon:'🚶', label:'行人',   count:12, color:'#00ff88' },
  { icon:'🏍️', label:'摩托车', count:5,  color:'#f59e0b' },
  { icon:'🚲', label:'自行车', count:4,  color:'#00d4ff' },
  { icon:'🐕', label:'动物',   count:2,  color:'#a78bfa' },
  { icon:'📦', label:'其他',   count:6,  color:'#718096' },
])

const confBars = ref([
  { range:'90-100%', pct:35, color:'#00ff88' },
  { range:'80-90%',  pct:28, color:'#3aa3ff' },
  { range:'70-80%',  pct:22, color:'#00d4ff' },
  { range:'60-70%',  pct:10, color:'#f59e0b' },
  { range:'<60%',    pct:5,  color:'#ff3366' },
])

const classNames = ['车辆','行人','摩托车','自行车','动物','卡车','公交车','交通标志']
const classColors = ['#3aa3ff','#00ff88','#f59e0b','#00d4ff','#a78bfa','#ff8c00','#ff3366','#718096']

const logs = ref([])
const logRef = ref(null)

const genLog = () => {
  const idx = Math.floor(Math.random() * classNames.length)
  const conf = (60 + Math.random() * 39).toFixed(1)
  const now = new Date().toLocaleTimeString('zh-CN', { hour12: false })
  logs.value.unshift({ time: now, cls: classNames[idx], conf, color: classColors[idx] })
  if (logs.value.length > 50) logs.value.pop()
}

const tick = () => {
  clock.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
  fps.value = 24 + Math.floor(Math.random() * 8)
  inferMs.value = 8 + Math.floor(Math.random() * 10)
  totalDetections.value = 35 + Math.floor(Math.random() * 25)

  // 随机更新检测数
  detStats.value.forEach(d => { d.count = Math.max(0, d.count + Math.floor(Math.random() * 5) - 2) })

  genLog()
}

onMounted(() => {
  tick()
  for (let i = 0; i < 15; i++) genLog()
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
.main-grid { display:grid; grid-template-columns:1fr 320px; gap:16px; height:calc(100vh - 80px); }

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

/* 侧栏 */
.side-col { display:flex; flex-direction:column; gap:14px; min-height:0; overflow-y:auto; }
.side-panel {
  position:relative; padding:14px 16px;
  background:rgba(8,30,55,.85); border:1px solid rgba(58,163,255,.1); border-radius:6px;
  flex-shrink:0;
}
.log-panel { flex:1; min-height:200px; display:flex; flex-direction:column; }
.side-title { font-size:13px; font-weight:600; color:#e0e6ed; margin-bottom:12px; display:flex; align-items:center; gap:6px; }
.accent-bar { display:inline-block; width:3px; height:14px; background:#3aa3ff; border-radius:2px; }

/* 检测统计 */
.det-stats { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.det-item {
  display:flex; align-items:center; gap:8px; padding:8px 10px;
  background:rgba(0,40,80,.3); border-radius:4px; border:1px solid rgba(58,163,255,.06);
}
.det-icon { font-size:18px; }
.det-label { flex:1; font-size:12px; color:#a0aec0; }
.det-val { font-size:18px; font-weight:700; font-family:'Courier New',monospace; }

/* 置信度条 */
.conf-bars { display:flex; flex-direction:column; gap:8px; }
.conf-row { display:flex; align-items:center; gap:8px; }
.conf-label { width:60px; font-size:11px; color:#718096; text-align:right; font-family:'Courier New',monospace; }
.conf-track { flex:1; height:8px; background:rgba(255,255,255,.06); border-radius:4px; overflow:hidden; }
.conf-fill { height:100%; border-radius:4px; transition:width .5s ease; }
.conf-pct { width:36px; font-size:11px; color:#a0aec0; font-family:'Courier New',monospace; }

/* 检测日志 */
.log-scroll { flex:1; overflow-y:auto; max-height:260px; }
.log-scroll::-webkit-scrollbar { width:4px; }
.log-scroll::-webkit-scrollbar-thumb { background:rgba(58,163,255,.2); border-radius:2px; }
.log-item {
  display:flex; align-items:center; gap:10px; padding:5px 0;
  border-bottom:1px solid rgba(58,163,255,.05); font-size:12px;
}
.log-time { color:#718096; font-family:'Courier New',monospace; width:70px; flex-shrink:0; }
.log-cls { font-weight:600; flex:1; }
.log-conf { color:#a0aec0; font-family:'Courier New',monospace; width:42px; text-align:right; }

/* 侧栏滚动条 */
.side-col::-webkit-scrollbar { width:4px; }
.side-col::-webkit-scrollbar-thumb { background:rgba(58,163,255,.2); border-radius:2px; }
</style>
