<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import {WebRTCReceiver} from '../client.js'
// Axios 实例

const api = axios.create({
  baseURL: 'http://localhost:8080/drone',
  timeout: 5000
})

const remoteVideo = ref(null)
let webrtc = null
// 预留：后续 WebRTC 成功后
function attachStream(stream) {
  if (remoteVideo.value) {
    remoteVideo.value.srcObject = stream
  }
}

// ===== 表单数据 =====
const controlForm = reactive({
  command: 'TAKE_OFF',
  forward: null,
  right: null,
  up: null,
  yaw: null,
  speed: null,
  latitude: null,
  longitude: null,
  altitude: null
})

const vsForm = reactive({
  mode: 'NORMAL', // NORMAL / ADVANCED
  lv: 0, lh: 0, rv: 0, rh: 0,
  roll: 0, pitch: 0, yaw: 0, throttle: 0
})

// ===== 飞行器状态 =====
const vsState = ref(null)

// ===== 通用发送函数 =====
async function sendControl() {
  try {
    await api.post('/control', controlForm)
    alert('Control 指令已发送')
    resetControlForm()
  } catch (e) {
    console.error(e)
    alert('发送失败')
  }
}

async function sendVS() {
  try {
    await api.post('/vs', vsForm)
    alert('Virtual Stick 指令已发送')
    resetVSForm()
  } catch (e) {
    console.error(e)
    alert('发送失败')
  }
}

// ===== 获取飞行器状态 =====
async function fetchState() {
  try {
    const res = await api.get('/info')
    vsState.value = res.data.data
  } catch (e) {
    console.error('状态获取失败', e)
  }
}

// 自动刷新状态
let stateTimer = null
onMounted(() => {
  webrtc = new WebRTCReceiver(
    remoteVideo.value,
    'ws://localhost:8080/signal?'
  )
  webrtc.start()

  fetchState()
  stateTimer = setInterval(fetchState, 1000)
})

function resetControlForm() {
  controlForm.command = 'TAKE_OFF'
  controlForm.forward = null
  controlForm.right = null
  controlForm.up = null
  controlForm.yaw = null
  controlForm.speed = null
  controlForm.latitude = null
  controlForm.longitude = null
  controlForm.altitude = null
}

function resetVSForm() {
  vsForm.mode = 'NORMAL'
  vsForm.lv = 0
  vsForm.lh = 0
  vsForm.rv = 0
  vsForm.rh = 0
  vsForm.roll = 0
  vsForm.pitch = 0
  vsForm.yaw = 0
  vsForm.throttle = 0
}

</script>

<template>
  <div class="layout">
  <div class="container">
    <h2>无人机控制面板</h2>

    <!-- 基础指令 -->
    <div class="section">
      <h3>基础指令</h3>
      <button @click="controlForm.command='TAKE_OFF'; sendControl()">起飞</button>
      <button @click="controlForm.command='LAND'; sendControl()">降落</button>
      <button @click="controlForm.command='GO_HOME'; sendControl()">返航</button>
      <button @click="controlForm.command='HOVER'; sendControl()">悬停</button>
      <button @click="controlForm.command='EMERGENCY_STOP'; sendControl()">紧急停止</button>
    </div>

    <!-- MOVE / ROTATE -->
    <div class="section">
      <h3>移动/旋转</h3>
      <label>命令
        <select v-model="controlForm.command">
          <option value="MOVE">移动</option>
          <option value="ROTATE">旋转</option>
        </select>
      </label>

      <div v-if="controlForm.command === 'MOVE'">
        <label>前后 (m) <input type="number" v-model.number="controlForm.forward"/></label>
        <label>左右 (m) <input type="number" v-model.number="controlForm.right"/></label>
        <label>上下 (m) <input type="number" v-model.number="controlForm.up"/></label>
      </div>

      <div v-if="controlForm.command === 'ROTATE'">
        <label>偏航角 (°) <input type="number" v-model.number="controlForm.yaw"/></label>
      </div>

      <button @click="sendControl()">发送</button>
    </div>

    <!-- 虚拟摇杆 -->
    <div class="section">
      <h3>虚拟摇杆</h3>
      <label>模式
        <select v-model="vsForm.mode">
          <option value="NORMAL">普通</option>
          <option value="ADVANCED">高级</option>
        </select>
      </label>

      <div v-if="vsForm.mode === 'NORMAL'">
        <label>左竖 LV <input type="number" v-model.number="vsForm.lv"/></label>
        <label>左横 LH <input type="number" v-model.number="vsForm.lh"/></label>
        <label>右竖 RV <input type="number" v-model.number="vsForm.rv"/></label>
        <label>右横 RH <input type="number" v-model.number="vsForm.rh"/></label>
      </div>

      <div v-if="vsForm.mode === 'ADVANCED'">
        <label>Pitch <input type="number" v-model.number="vsForm.pitch"/></label>
        <label>Roll <input type="number" v-model.number="vsForm.roll"/></label>
        <label>Yaw <input type="number" v-model.number="vsForm.yaw"/></label>
        <label>Throttle <input type="number" v-model.number="vsForm.throttle"/></label>
      </div>

      <button @click="sendVS()">发送摇杆</button>
    </div>

    <!-- 当前状态 -->
    
  </div>
  <div class="video-panel">
      <h3>无人机实时画面</h3>

      <video
        ref="remoteVideo"
        autoplay
        playsinline
        muted
      ></video>

      <div class="video-tip">
        等待无人机视频流接入…
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 整体左右布局 */
.layout {
  display: flex;
  gap: 20px;
  padding: 20px;
}

/* 左侧控制面板 */
.container {
  flex: 1;
  max-width: 600px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 6px;
}

/* 右侧视频面板 */
.video-panel {
  flex: 1;
  min-width: 400px;
  background: #000;
  color: #fff;
  padding: 12px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 视频本体 */
.video-panel video {
  width: 100%;
  max-height: 420px;
  background: black;
  border: 1px solid #333;
}

/* 提示文字 */
.video-tip {
  margin-top: 8px;
  font-size: 13px;
  opacity: 0.7;
}

/* 原有样式保留 */
.section {
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
}
label { display:block; margin: 6px 0;}
input, select { width: 100%; padding: 4px;}
button { margin-top: 6px; padding: 6px 12px; cursor:pointer;}

</style>
