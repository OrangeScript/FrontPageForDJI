<template>
  <div class="live-wrapper">
    <video
      ref="videoRef"
      class="video"
      muted
      autoplay
      playsinline
    />
    <!-- <img :src="videoUrl" class="video" /> -->
    <YOLOView/>
    <rawStream/>
  </div>
</template>

<script setup>
import rawStream from './rawStream.vue'
import YOLOView from './YOLO.vue'
import { ref, onMounted, onBeforeUnmount } from 'vue'
const videoUrl = 'http://localhost:5000/video_feed' 
const videoRef = ref(null)
const yoloVideoRef = ref(null)
let webRtcServer = null
// let yoloStreamer = null

// webrtc-streamer 地址（Docker）
const WEBRTC_SERVER = `${location.protocol}//${location.hostname}:8000`

// RTSP 地址
// const RTSP_URL = 'rtsp://aaa:aaa@10.87.49.48:8554/streaming/live/1'
const RTSP_URL = 'rtsp://192.168.31.198:554/live'

// YOLO_RTSP = ""
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
