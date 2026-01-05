<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { stick } from '../api/control'

const canvasRef = ref(null)
const pos = ref({ x: 300, y: 200 })
const yaw = ref(0)
const altitude = ref(10)        // 当前高度（m，用于显示）
const verticalSpeed = ref(0)    // m/s
const climbSpeed = 1.0          // 上升速度 m/s

const speed = 80 // px/s
const keys = {}



const controlState = ref({
  pitch: 0,
  roll: 0,
  yaw: 0,
  throttle: 0
})

let lastSentState = {
  pitch: 0,
  roll: 0,
  yaw: 0,
  throttle: 0
}

function hasChanged(a, b) {
  return (
    a.pitch !== b.pitch ||
    a.roll !== b.roll ||
    a.yaw !== b.yaw ||
    a.throttle !== b.throttle
  )
}

function onKey(e, down) {
  const k = e.key.toLowerCase()
  if (k === ' ') {
    keys['space'] = down
  } else {
    keys[k] = down
  }
}

function update(dt) {
  let vx = 0
  let vy = 0

  if (keys['w']) vy += 0.01
  if (keys['s']) vy -= 0.01
  if (keys['a']) vx -= 0.01
  if (keys['d']) vx += 0.01

  // ===== 水平运动 =====
  if (vx || vy) {
    yaw.value = 0
    pos.value.x += vx * speed * dt
    pos.value.y -= vy * speed * dt
  }

  
  if (keys['space']) {
    verticalSpeed.value = climbSpeed
  } else {
    verticalSpeed.value = 0
  }

  altitude.value += verticalSpeed.value * dt
  altitude.value = Math.max(0, altitude.value)


  controlState.value.pitch = vy
  controlState.value.roll = vx
  controlState.value.yaw = yaw.value
  controlState.value.throttle = verticalSpeed.value

}

let sendTimer = null

function startSendLoop() {
  sendTimer = setInterval(() => {
    const cur = controlState.value

    if (hasChanged(cur, lastSentState)) {
      stick(
        cur.yaw,
        cur.throttle,
        cur.roll,
        cur.pitch
      )
      lastSentState = { ...cur }
    }
  }, 200) // 10Hz，真实无人机常用
}

let last = performance.now()

function loop(now) {
  const dt = (now - last) / 1000
  last = now

  update(dt)
  draw()
  recordTrail()
  requestAnimationFrame(loop)
}

function draw() {
  const ctx = canvasRef.value.getContext('2d')
  const W = 600
  const H = 400

  ctx.clearRect(0, 0, W, H)

  const cx = W / 2
  const cy = H / 2

  ctx.save()

  // ===== 摄像机反向移动 =====
  ctx.translate(cx - pos.value.x, cy - pos.value.y)

  // ===== 尾巴 =====
  ctx.strokeStyle = 'rgba(0, 150, 255, 0.6)'
  ctx.beginPath()
  trail.forEach((p, i) => {
    if (i === 0) ctx.moveTo(p.x, p.y)
    else ctx.lineTo(p.x, p.y)
  })
  ctx.stroke()

  // ===== 飞机 =====
  ctx.save()
  ctx.translate(pos.value.x, pos.value.y)
  ctx.rotate(yaw.value * Math.PI / 180)

  ctx.beginPath()
  ctx.moveTo(0, -12)
  ctx.lineTo(8, 10)
  ctx.lineTo(-8, 10)
  ctx.closePath()
  ctx.fillStyle = 'red'
  ctx.fill()

  ctx.restore()
  ctx.restore()

  // ===== UI 边框 =====
  ctx.strokeStyle = '#ccc'
  ctx.strokeRect(0, 0, W, H)
}

onMounted(() => {
  window.addEventListener('keydown', e => onKey(e, true))
  window.addEventListener('keyup', e => onKey(e, false))
  startSendLoop()
  requestAnimationFrame(loop)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKey)
  window.removeEventListener('keyup', onKey)
  clearInterval(sendTimer)
})
const trail = []
const TRAIL_TIME = 3000 // ms
function recordTrail() {
  trail.push({
    x: pos.value.x,
    y: pos.value.y,
    t: performance.now()
  })

  const now = performance.now()
  while (trail.length && now - trail[0].t > TRAIL_TIME) {
    trail.shift()
  }
}


</script>
<template>
  <div class="control-layout">
    <!-- 左侧：游戏区 -->
    <el-card class="game-panel">
      <h3>无人机实时控制</h3>
      <canvas
        ref="canvasRef"
        width="600"
        height="400"
        class="canvas"
      />
      <p>使用 W / A / S / D 控制无人机</p>
    </el-card>

    <!-- 右侧：高度油门 -->
    <div class="right-panel">
      <div class="altitude-box">
        <div class="altitude-text">
          高度 {{ altitude.toFixed(1) }} m
        </div>

        <el-slider
          vertical
          :min="0"
          :max="50"
          :model-value="altitude"
          disabled
          height="300px"
        />
      </div>
    </div>
  </div>
</template>


<style scoped>
.control-layout {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
}

.game-panel {
  width: 650px;
}

.right-panel {
  margin-left: 20px;
  display: flex;
  align-items: center;
}

.canvas {
  border: 1px solid #ccc;
}

</style>