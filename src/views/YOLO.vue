<template>
  <div class="monitor-container">
    <div class="video-grid">
      <div class="video-card">
        <h3>原始摄像头</h3>
        <div class="video-wrapper">
          <iframe 
            src="http://localhost:8889/live" 
            scrolling="no" 
            frameborder="0"
            allow="autoplay; fullscreen"
          ></iframe>
        </div>
      </div>

      <div class="video-card">
        <h3>YOLO 识别结果</h3>
        <div class="video-wrapper">
          <iframe 
            src="http://localhost:8889/stream" 
            scrolling="no" 
            frameborder="0"
            allow="autoplay; fullscreen"
          ></iframe>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.monitor-container {
  padding: 20px;
  background-color: #1a1a1a;
  min-height: 100vh;
  color: white;
}

.video-grid {
  display: grid;
  grid-template-columns: 1fr 1fr; /* 左右两栏 */
  gap: 20px;
}

.video-card {
  background: #2c2c2c;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}

h3 {
  margin-bottom: 10px;
  text-align: center;
  color: #4ade80; /* 绿色 */
}

.video-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%; /* 16:9 比例 */
  height: 0;
  overflow: hidden;
  border-radius: 4px;
  background: black;
}

.video-wrapper iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
</style>