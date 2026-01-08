

<template>
  <router-view></router-view>
  <div class="live-wrapper">
    <video
      ref="videoRef"
      class="video"
      muted
      autoplay
      playsinline
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const videoRef = ref(null)
let webRtcServer = null

// webrtc-streamer 地址（Docker）
const WEBRTC_SERVER = `${location.protocol}//${location.hostname}:8000`

// RTSP 地址
const RTSP_URL = 'rtsp://aaa:aaa@192.168.3.245:8554/streaming/live/1'

// ⚠️ 关键参数（来自你给的 HTML 示例）
const RTSP_OPTIONS = 'rtptransport=tcp&timeout=60'

onMounted(() => {
  webRtcServer = new window.WebRtcStreamer(
    videoRef.value,
    WEBRTC_SERVER
  )

  // 等价于你给的 connect(...) 调用
  webRtcServer.connect(
    RTSP_URL,
    '',                // user
    RTSP_OPTIONS       // options
  )
})

// onBeforeUnmount(() => {
//   if (webRtcServer) {
//     webRtcServer.disconnect()
//     webRtcServer = null
//   }
// })
</script>

<style scoped>
.video {
  width: 100%;
  height: 400px;
  background: black;
  border-radius: 8px;
}
</style>