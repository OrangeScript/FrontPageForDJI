<template>
  <div class="live-wrapper">
    <el-card class="live-card">
      <template #header>
        <span>📡 实时视频</span>
      </template>
    </el-card>

    <!-- ⚠️ video 不放在 el-card 里面 -->
    <video
      ref="videoRef"
      class="video"
      autoplay
      playsinline
      muted
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const videoRef = ref(null)
let webRtcServer = null

// ===== 固定 RTSP 地址 =====


const RTSP_URL = 'rtsp://196.21.92.82/axis-media/media.amp'

// ===== webrtc-streamer 地址 =====
const WEBRTC_SERVER = 'http://localhost:8000'

onMounted(() => {
  // webrtcstreamer.js 挂在 window 上
  webRtcServer = new window.WebRtcStreamer(
    videoRef.value,
    WEBRTC_SERVER
  )

  webRtcServer.connect(RTSP_URL)
})

onBeforeUnmount(() => {
  if (webRtcServer) {
    webRtcServer.disconnect()
    webRtcServer = null
  }
})
</script>

<style scoped>
.live-card {
  width: 100%;
}

.video {
  width: 100%;
  height: 400px;
  background: black;
  border-radius: 8px;
}
</style>
