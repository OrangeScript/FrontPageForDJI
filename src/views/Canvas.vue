<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const canvasRef = ref(null)
const pos = ref({ x: 300, y: 200 })
const yaw = ref(0)
const altitude = ref(10)        // 当前高度（m，用于显示）
const verticalSpeed = ref(0)    // m/s
const climbSpeed = 1.0          // 上升速度 m/s

const speed = 80 // px/s
const keys = {}

const api = axios.create({
  baseURL: 'http://localhost:8080/drone'
})


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

  if (keys['w']) vy += 1
  if (keys['s']) vy -= 1
  if (keys['a']) vx -= 1
  if (keys['d']) vx += 1

  // ===== 水平运动 =====
  if (vx || vy) {
    yaw.value = Math.atan2(vx, vy) * 180 / Math.PI
    pos.value.x += vx * speed * dt
    pos.value.y -= vy * speed * dt
  }

  // ===== 垂直油门 =====
  if (keys['space']) {
    verticalSpeed.value = climbSpeed
  } else {
    verticalSpeed.value = 0
  }

  altitude.value += verticalSpeed.value * dt
  altitude.value = Math.max(0, altitude.value)

  // ===== 发送给后端 =====
  api.post('/vs', {
    mode: 'ADVANCED',
    pitch: vy,
    roll: vx,
    yaw: yaw.value,
    throttle: verticalSpeed.value
  })
}

let last = performance.now()

function loop(now) {
  const dt = (now - last) / 1000
  last = now

  update(dt)
  draw()

  requestAnimationFrame(loop)
}

function draw() {
  const ctx = canvasRef.value.getContext('2d')
  ctx.clearRect(0, 0, 600, 400)

  // 地图
  ctx.strokeStyle = '#ddd'
  ctx.strokeRect(0, 0, 600, 400)

  // 无人机
  ctx.save()
  ctx.translate(pos.value.x, pos.value.y)
  ctx.rotate(yaw.value * Math.PI / 180)

  ctx.beginPath()
  ctx.moveTo(0, -10)
  ctx.lineTo(6, 10)
  ctx.lineTo(-6, 10)
  ctx.closePath()
  ctx.fillStyle = 'red'
  ctx.fill()

  ctx.restore()
}

onMounted(() => {
  window.addEventListener('keydown', e => onKey(e, true))
  window.addEventListener('keyup', e => onKey(e, false))
  requestAnimationFrame(loop)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKey)
  window.removeEventListener('keyup', onKey)
})
</script>
<template>
  <div class="control-layout">
    <!-- 左侧：游戏区 -->
    <el-card class="game-panel">
      <h3>🎮 无人机实时控制</h3>
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