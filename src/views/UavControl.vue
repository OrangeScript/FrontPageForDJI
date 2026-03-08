<script setup>
import { reactive } from 'vue'
import UavControl from '@/components/Control/Control.vue'
import UavShow from '@/components/Control/Path.vue'
import UavStatus from '@/components/Uav/UavStatus.vue'


const ui = reactive({
  taskType: '巡检',
  autoRun: true,
})

/** 先 mock，后续你接接口就更新这里 */
const uav = reactive({
  stateText: '开机',
  x: 14.99444,
  y: 4.466357,
  altitude: 0.0,
  zoom:2.0,
  hSpeed: 14.0,
  vSpeed: -3,
  elPitch: -10,
  elYaw:90,
  rcStateText: '开机',
  rcSignal: 100,
  linkPercent: 80,
})
</script>

<template>
  <div class="page">
    <UavControl :ui="ui" />
    <UavShow :ui="ui" />
    <UavStatus :data="uav" />
  </div>
</template>

<style scoped>
.page {
  height: 100vh;
  width: 100%;
  display: grid;
  grid-template-columns: 280px 1fr 320px;

  background: #061a2c;
  color: rgba(255, 255, 255, 0.88);
  overflow: hidden;     
  min-height: 0;        
}


.page > * {
  min-height: 0;        
}

</style>
