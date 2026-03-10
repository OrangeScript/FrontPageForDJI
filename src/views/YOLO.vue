<template>
  <div class="monitor-container">
    <div class="video-grid">
      <div class="video-card">
        <h3>原始摄像头</h3>
        <div class="video-wrapper">
          <iframe 
            src="http://192.168.246.214:8889/live" 
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
            src="http://192.168.246.214:8889/stream" 
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
  padding:24px; background:#061a2c; min-height:100vh; color:#e0e6ed;
  display:flex; justify-content:center; align-items:center;
}
.video-grid { display:grid; grid-template-columns:1fr 1fr; gap:20px; width:100%; max-width:1500px; }
.video-card {
  background:rgba(8,30,55,.85); padding:20px; border-radius:8px;
  border:1px solid rgba(58,163,255,.1); backdrop-filter:blur(8px);
  transition:transform .3s,box-shadow .3s;
}
.video-card:hover { border-color:rgba(0,212,255,.3); box-shadow:0 0 24px rgba(0,120,255,.12); }
h3 { margin-bottom:14px; text-align:center; color:#3aa3ff; font-weight:600; font-size:16px; letter-spacing:1px; }
.video-wrapper { position:relative; width:100%; padding-bottom:56.25%; height:0; overflow:hidden; border-radius:6px; background:#000; }
.video-wrapper iframe { position:absolute; inset:0; width:100%; height:100%; border-radius:6px; }
</style>
