<template>
  <div class="video-box">
    <canvas ref="canvas" width="960" height="540"></canvas>
    <!-- <div class="info">{{ status }}</div> -->
     <!-- 这个status显示有问题，暂时不知道原因 -->
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const canvas = ref(null)
const status = ref('未连接')
let ws = null

onMounted(() => {
  const ctx = canvas.value.getContext('2d')

  ws = new WebSocket(
    `ws://${location.hostname}:8007/ws/camera_detection?camera_id=rtsp://aaa:aaa@10.87.49.48:8554/streaming/live/1&fps_limit=30`
  )

  ws.onopen = () => {
    status.value = '已连接'
  }

  ws.onmessage = (e) => {
    status.value = '已连接'
    const data = JSON.parse(e.data)
    if (!data.image_base64) return

    const img = new Image()
    img.onload = () => {
      ctx.drawImage(img, 0, 0, canvas.value.width, canvas.value.height)
    }
    img.src = data.image_base64
  }

  ws.onclose = () => {
    status.value = '已断开'
  }
})

onBeforeUnmount(() => {
  if (ws) ws.close()
})
</script>

<style scoped>
.video-box {
  display: flex;
  flex-direction: column;
  align-items: center;
}
canvas {
  border: 1px solid #333;
  background: black;
}
.info {
  margin-top: 6px;
}
</style>
