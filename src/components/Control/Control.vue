<template>
  <aside class="panel panel-left">
    <div class="panel-title">
      <span class="dot" />
      <span class="title-text">无人机实时控制</span>
    </div>

    <!-- 飞行控制 -->
    <el-card class="card card-takeoff" shadow="never">
      <template #header><div class="card-h">飞行控制</div></template>
      <div class="form-row">
        <el-button @click="takeoff" type="success" style="width: 100%" size="large">Takeoff</el-button>
        <el-button @click="land" type="warning" style="width: 100%" size="large">Land</el-button>
      </div>
    </el-card>

    <!-- 遥控控制 -->
    <div class="remote-control">
      <div class="hv-card">
        <!-- 平移 -->
        <div class="move-control">
          <div class="move-direction">
            <div class="direction-button up" @click="move('up')"></div>
            <div class="direction-button left" @click="move('left')"></div>
            <div class="icon">
              <img src="@/assets/control.png" alt="control icon" />
            </div>
            <div class="direction-button right" @click="move('right')"></div>
            <div class="direction-button down" @click="move('down')"></div>
          </div>
          <span>平移控制</span>
        </div>
      </div>

      <div class="hv-card">
        <div class="altitude-control">
          <div class="move-altitude">
            <div class="direction-button up" @click="moveAltitude('up')"></div>
            <div class="icon">
              <img src="@/assets/control.png" alt="control icon" />
            </div>
            <div class="direction-button down" @click="moveAltitude('down')"></div>
          </div>
          <span>高度控制</span>
        </div>
      </div>
    </div>

    <!-- 偏转调整 -->
    <el-card class="card" shadow="never">
      <template #header><div class="card-h">偏转调整</div></template>
      <div class="yaw-container">
        <el-slider v-model="yaw" :min="-180" :max="180" step="1" show-input label="偏转角度" @change="adjustYaw"></el-slider>
      </div>
    </el-card>

  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { ElButton, ElMessage } from 'element-plus'
import * as ctrl from '@/api/control'

const loading = ref(false)

// 发送起飞命令
const takeoff = async () => {
  try {
    await ctrl.takeoff()
    ElMessage.success('起飞成功')
  } catch (e) {
    ElMessage.error('起飞失败')
  }
}

// 发送降落命令
const land = async () => {
  try {
    await ctrl.land()
    ElMessage.success('降落成功')
  } catch (e) {
    ElMessage.error('降落失败')
  }
}

// 平移控制：上、下、左、右
const move = async (direction) => {
  if (loading.value) return
  loading.value = true
  try {
    // 控制水平移动
    if (direction === 'up') {
      await ctrl.stick(0, 1, 0, 0) // 前
    } else if (direction === 'down') {
      await ctrl.stick(0, -1, 0, 0) // 后
    } else if (direction === 'left') {
      await ctrl.stick(-1, 0, 0, 0) // 左
    } else if (direction === 'right') {
      await ctrl.stick(1, 0, 0, 0) // 右
    }
    ElMessage.success(`移动 ${direction} 成功`)
  } catch (e) {
    ElMessage.error(`移动 ${direction} 失败`)
  } finally {
    loading.value = false
  }
}

// 高度控制：升高、降低
const moveAltitude = async (direction) => {
  if (loading.value) return
  loading.value = true
  try {
    // 控制飞行高度
    if (direction === 'up') {
      await ctrl.gotoAltitude(1)  // 升高
    } else if (direction === 'down') {
      await ctrl.gotoAltitude(-1)   // 降低
    }
    ElMessage.success(`高度 ${direction} 成功`)
  } catch (e) {
    ElMessage.error(`高度 ${direction} 失败`)
  } finally {
    loading.value = false
  }
}

// 调整偏转角度
const adjustYaw = async (newYaw) => {
  if (loading.value) return
  loading.value = true
  try {
    await ctrl.gotoYaw(newYaw) // 偏转角度调整
    ElMessage.success(`偏转调整为 ${newYaw}°`)
  } catch (e) {
    ElMessage.error(`偏转调整失败`)
  } finally {
    loading.value = false
  }
}

// 增加偏转角度
const increaseYaw = () => {
  yaw.value += 1
  adjustYaw(yaw.value)
}

// 减少偏转角度
const decreaseYaw = () => {
  yaw.value -= 1
  adjustYaw(yaw.value)
}
</script>

<style scoped>
.panel {
  background: rgba(9, 35, 60, 0.78);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  padding: 14px;
}

.panel-left {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 6px 12px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #3aa3ff;
  box-shadow: 0 0 16px rgba(58, 163, 255, 0.55);
}

.title-text {
  font-size: 16px;
  letter-spacing: 1px;
}

/* 起飞和降落 */
.card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.10);
  box-shadow: inset 0 0 20px rgba(58, 163, 255, 0.10);
}

.card-takeoff{
  height: 140px;
}

.card-h {
  font-size: 14px;
  color:rgba(158, 208, 255, 0.75);
  opacity: 0.75;
}

.form-row {
  display: flex;  /* 使用flex布局 */
  margin-top: 5px;
  gap: 20px;  /* 按钮之间的间距 */
  width: 100%;
}

.control-button {
  flex: 1;  /* 使按钮填满空间，宽度相等 */
  height: 50px;  /* 统一按钮高度 */
  font-size: 16px;  /* 设置字体大小 */
  font-weight: bold;  /* 设置字体加粗 */
  border-radius: 30px;  /* 设置圆角 */
  transition: all 0.3s ease;  /* 添加平滑过渡 */
}

.control-button:hover {
  opacity: 0.8;  /* 悬停时透明度变低 */
}

.control-button:focus {
  outline: none;  /* 去除聚焦时的默认外框 */
}

/* 遥控器控制 */
.remote-control {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 10px;
}

.hv-card {
  height: 140px;
  border-radius: 5px;
  padding: 5px 5px;
  margin: 0 0 8px 0;

  /* display: grid; */
  /* grid-template-columns: 46px 1fr; */
  /* align-items: center; */

  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.10);
  box-shadow: inset 0 0 20px rgba(58, 163, 255, 0.10);
}


/* 容器设置 */
.move-control, .altitude-control{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;  /* 确保按钮与文本之间的空间分配 */
  width: 100%;
  max-width: 300px;
  height: auto;
  width: 100%;
  max-width: 300px;
  height: auto;
  gap: 10px;
  position: relative; /* 添加相对定位 */
}

.move-direction {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  width: 100px; /* 让它占满 move-control 容器的宽度 */
  height: 100px; /* 让它占满 move-control 容器的高度 */
  border-radius: 50%; /* 圆形容器 */
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(0, 0, 0, 0.14);
}

.move-altitude {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  width: 70px; /* 让它占满 move-control 容器的宽度 */
  height: 100px; /* 让它占满 move-control 容器的高度 */
  background-color: rgba(58, 163, 255, 0.3); /* 背景色 */
  position: relative;

  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.14);
}

.direction-button {
  width: 0;  /* 去掉宽度设置 */
  height: 0;  /* 去掉高度设置 */
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  position: absolute; /* 使用绝对定位 */
  transition: all 0.3s ease;
  border: none; /* 去除外边框 */
  z-index: 10;
}

/* 按钮鼠标悬停效果 */
.direction-button:hover {
  background-color: transparent; /* 不改变背景色 */
  border: none;
}

/* 点击效果：缩放并改变透明度 */
.direction-button:active {
  transform: scale(0.95); /* 按钮被点击时稍微缩小 */
  opacity: 0.7; /* 增加按下时的透明度变化 */
}

/* 上三角形 */
.direction-button.up {
  top: 5px; 
  left: 50%;
  transform: translateX(-50%);
  border-left: 15px solid transparent;
  border-right: 15px solid transparent;
  border-bottom: 25px solid #3aa3ff;
}

/* 下三角形 */
.direction-button.down {
  bottom: 5px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 15px solid transparent;
  border-right: 15px solid transparent;
  border-top: 25px solid #3aa3ff;
}

/* 左三角形 */
.direction-button.left {
  left: 5px;
  top:50%;
  transform: translateY(-50%);
  border-top: 15px solid transparent;
  border-bottom: 15px solid transparent;
  border-right: 25px solid #3aa3ff;
}

/* 右三角形 */
.direction-button.right {
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  border-top: 15px solid transparent;
  border-bottom: 15px solid transparent;
  border-left: 25px solid #3aa3ff;
}

/* 图标居中 */
.icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  justify-content: center;
  align-items: center;
  width: 50px; /* 图标的宽度 */
  height: 50px; /* 图标的高度 */
  border-radius: 50%; /* 圆形背景 */
  padding: 10px; /* 图标与边界之间的间距 */
}

.icon img {
  width: 60%; /* 图片宽度占容器的70%，使其稍微小一些 */
  height: 60%; /* 图片高度占容器的70% */
  object-fit: contain; /* 确保图片按比例缩放 */
}


/* 偏转调整 */
.yaw-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.el-slider {
  width: 110%;
}
</style>