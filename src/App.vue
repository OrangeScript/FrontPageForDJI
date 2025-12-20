<script setup>
import { ref } from 'vue'
import axios from 'axios'

// 后端地址
const api = axios.create({
  baseURL: 'http://localhost:8080',
  timeout: 5000
})

// 表单数据（直接映射 ControlRequest）
const form = ref({
  command: 'TAKE_OFF',
  forward: null,
  right: null,
  up: null,
  yaw: null
})

function sendCommand() {
  api.post('/control', form.value)
    .then(() => {
      alert('指令已发送')
    })
    .catch(err => {
      console.error(err)
      alert('发送失败')
    })
}
</script>

<template>
  <img src="https://www.google.com/logos/doodles/2025/seasonal-holidays-2025-6753651837110711.4-la1f1f1f.gif"/>
  <div class="container">
    <h2>无人机控制面板</h2>


    <div class="row">
      <label>指令类型</label>
      <select v-model="form.command">
        <option value="TAKE_OFF">起飞</option>
        <option value="LAND">降落</option>
        <option value="GO_HOME">返航</option>
        <option value="MOVE">移动</option>
        <option value="ROTATE">旋转</option>
      </select>
    </div>

    <div v-if="form.command === 'MOVE'" class="row">
      <label>前后 (m)</label>
      <input type="number" v-model.number="form.forward" />
    </div>

    <div v-if="form.command === 'MOVE'" class="row">
      <label>左右 (m)</label>
      <input type="number" v-model.number="form.right" />
    </div>

    <div v-if="form.command === 'MOVE'" class="row">
      <label>上下 (m)</label>
      <input type="number" v-model.number="form.up" />
    </div>

    <div v-if="form.command === 'ROTATE'" class="row">
      <label>偏航角 (°)</label>
      <input type="number" v-model.number="form.yaw" />
    </div>

    <button @click="sendCommand">发送指令</button>
  </div>
</template>

<style scoped>
.container {
  max-width: 400px;
  margin: 40px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.row {
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
}

label {
  width: 120px;
}

input, select {
  flex: 1;
}

button {
  width: 100%;
  padding: 10px;
  cursor: pointer;
}
</style>
