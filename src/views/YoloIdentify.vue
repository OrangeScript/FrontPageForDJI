<template>
  <div class="monitor-container">
    <div class="video-grid">
      <div class="video-card">
        <h3>原始摄像头</h3>
        <div class="video-wrapper">
          <iframe 
            src="http://192.168.3.4:8889/live" 
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
            src="http://192.168.3.4:8889/stream" 
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
  padding: 24px;
  position: relative;
  color: white;
  min-height: 100vh;
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
}

/* 添加伪元素作为背景并设置透明度 */
.monitor-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('@/assets/background.png');
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  opacity: 0.3; /* 调整透明度 */
  z-index: -1; /* 使背景图在内容下层 */
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(600px, 1fr)); /* 每一列最小宽度为320px */
  gap: 20px; /* 卡片之间的间距 */
  width: 100%;
  max-width: 1500px; /* 最大宽度限制 */
}

.video-card {
  background: rgba(13, 47, 80, 0.6); /* 深色背景 */
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(8px); /* 背景模糊效果 */
  transition: transform 0.3s ease, box-shadow 0.3s ease; /* 悬停时增加动画 */
}

h3 {
  margin-bottom: 15px;
  text-align: center;
  color: #1972c0; /* 绿色标题，与前面的界面一致 */
  font-weight: 600;
  font-size: 18px;
}

.video-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%; /* 16:9 比例 */
  height: 0;
  overflow: hidden;
  border-radius: 8px;
  background: black;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5); /* 加阴影效果 */
}

.video-wrapper iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 8px; /* 让视频框有圆角 */
}

.video-card h3, .video-wrapper iframe {
  transition: all 0.3s ease; /* 添加动画效果 */
}

.video-card:hover {
  background-color: rgba(58, 163, 255, 0.1); /* 悬停时背景微微变色 */
}

.video-card:hover h3 {
  color: #3aa3ff; /* 悬停时标题颜色变成蓝色 */
}
</style>