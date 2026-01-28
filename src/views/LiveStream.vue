<template>
  <div class="live-wrapper">
    <YOLOView/>
    <rawStream/>
  </div>
</template>

<script setup>
import YOLOView from './YOLO.vue'
</script>

<style scoped>
.video {
  width: 100%;
  height: 400px;
  background: black;
  border-radius: 8px;
}
</style>
