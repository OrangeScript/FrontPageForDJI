<template>
  <el-card shadow="hover">
    <template #header>📹 无人机直播画面</template>

    <iframe
      src="http://localhost:8080/player.html?url=http://localhost:8080/live/test.m3u8"
      style="width:100%; height:600px; border:none;"
    />
  </el-card>
</template>
