<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const state = ref(null)

const api = axios.create({
  baseURL: 'http://localhost:8080/drone'
})

async function fetchState() {
  const res = await api.get('/info')
  state.value = res.data.data
}

onMounted(() => {
  fetchState()
  setInterval(fetchState, 1000)
})
</script>

<template>
  <el-row :gutter="16">
    <el-col :span="8">
      <el-card>
        <h3>📍 位置信息</h3>
        <p>纬度：{{ state?.latitude }}</p>
        <p>经度：{{ state?.longitude }}</p>
        <p>高度：{{ state?.altitude }} m</p>
      </el-card>
    </el-col>

    <el-col :span="8">
      <el-card>
        <h3>✈️ 姿态</h3>
        <p>Pitch：{{ state?.pitch }}°</p>
        <p>Roll：{{ state?.roll }}°</p>
        <p>Yaw：{{ state?.yaw }}°</p>
      </el-card>
    </el-col>

    <el-col :span="8">
      <el-card>
        <h3>🔋 状态</h3>
        <p>电量：{{ state?.battery }}%</p>
        <p>速度：{{ state?.speed }} m/s</p>
        <p>状态：{{ state?.status }}</p>
      </el-card>
    </el-col>
  </el-row>
</template>
