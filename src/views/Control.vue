<template>
  <el-card shadow="hover">
    <h3>🚁 无人机控制面板</h3>

    <!-- 基础控制 -->
    <div class="control-section">
      <el-button type="success" @click="sendCommand('takeoff')">起飞</el-button>
      <el-button type="danger" @click="sendCommand('land')">降落</el-button>
      <el-button type="warning" @click="sendCommand('RTH')">返航</el-button>
      <el-button @click="sendCommand('abortMission')">停止虚拟杆</el-button>
      <el-button @click="sendCommand('abort/DJIMission')">停止DJI任务</el-button>
      <el-button type="primary" @click="sendCommand('enableVirtualStick')">启用虚拟杆</el-button>
    </div>

    <el-divider>导航控制</el-divider>

    <!-- 直接到坐标 -->
    <div class="control-section">
      <el-input-number v-model="wp.lat" placeholder="纬度" label="lat" :step="0.000001" />
      <el-input-number v-model="wp.lon" placeholder="经度" label="lon" :step="0.000001" />
      <el-input-number v-model="wp.alt" placeholder="高度(m)" label="alt" />
      <el-input-number v-model="wp.yaw" placeholder="航向(°)" label="yaw" />
      <el-button @click="sendCommand('gotoWP')">导航到坐标</el-button>
      <el-button @click="sendCommand('gotoWPwithPID')">PID导航</el-button>
      <el-button @click="sendCommand('gotoYaw')">旋转到航向</el-button>
      <el-button @click="sendCommand('gotoAltitude')">变更高度</el-button>
    </div>

    <el-divider>轨迹控制 (虚拟杆 / 原生任务)</el-divider>

    <div class="control-section">
      <el-input
        type="textarea"
        v-model="trajectory"
        placeholder="lat,lon,alt;lat,lon,alt,yaw"
        rows="3"
      />
      <el-button @click="sendCommand('navigateTrajectory')">虚拟杆轨迹</el-button>
      <el-button @click="sendCommand('navigateTrajectoryDJINative')">DJI原生任务</el-button>
    </div>

    <el-divider>虚拟杆输入</el-divider>
    <div class="control-section">
      <el-input-number v-model="stick.leftX" placeholder="左摇杆X" />
      <el-input-number v-model="stick.leftY" placeholder="左摇杆Y" />
      <el-input-number v-model="stick.rightX" placeholder="右摇杆X" />
      <el-input-number v-model="stick.rightY" placeholder="右摇杆Y" />
      <el-button @click="sendCommand('stick')">发送虚拟杆</el-button>
    </div>

    <el-divider>相机控制</el-divider>
    <div class="control-section">
      <el-input-number v-model="cameraZoom" placeholder="缩放倍数" />
      <el-button @click="sendCommand('camera/zoom')">缩放</el-button>
      <el-button @click="sendCommand('camera/startRecording')">开始录像</el-button>
      <el-button @click="sendCommand('camera/stopRecording')">停止录像</el-button>
    </div>

    <el-divider>云台控制</el-divider>
    <div class="control-section">
      <el-input-number v-model="gimbal.roll" placeholder="roll" />
      <el-input-number v-model="gimbal.pitch" placeholder="pitch" />
      <el-input-number v-model="gimbal.yaw" placeholder="yaw" />
      <el-button @click="sendCommand('gimbal/pitch')">云台Pitch</el-button>
      <el-button @click="sendCommand('gimbal/yaw')">云台Yaw</el-button>
    </div>

    <el-divider></el-divider>

    <div>
      <h4>返回结果：</h4>
      <pre>{{ result }}</pre>
    </div>
  </el-card>
</template>

<script setup>
import { reactive, ref } from 'vue';
import axios from 'axios';

const API_BASE = 'http://localhost:8080/send';

const result = ref('');

const wp = reactive({ lat: null, lon: null, alt: null, yaw: null });
const trajectory = ref('');
const stick = reactive({ leftX: 0, leftY: 0, rightX: 0, rightY: 0 });
const cameraZoom = ref(1);
const gimbal = reactive({ roll: 0, pitch: 0, yaw: 0 });

async function sendCommand(command) {
  let url = `${API_BASE}/${command}`;
  let payload = {};

  switch (command) {
    case 'gotoWP':
      payload = { lat: wp.lat, lon: wp.lon, alt: wp.alt };
      break;
    case 'gotoWPwithPID':
      payload = { lat: wp.lat, lon: wp.lon, alt: wp.alt, yaw: wp.yaw };
      break;
    case 'gotoYaw':
      payload = { yaw_angle: wp.yaw };
      break;
    case 'gotoAltitude':
      payload = { altitude: wp.alt };
      break;
    case 'navigateTrajectory':
    case 'navigateTrajectoryDJINative':
      payload = { trajectory: trajectory.value };
      break;
    case 'stick':
      payload = { leftX: stick.leftX, leftY: stick.leftY, rightX: stick.rightX, rightY: stick.rightY };
      break;
    case 'camera/zoom':
      payload = { zoom_ratio: cameraZoom.value };
      break;
    case 'gimbal/pitch':
    case 'gimbal/yaw':
      payload = { roll: gimbal.roll, pitch: gimbal.pitch, yaw: gimbal.yaw };
      break;
  }

  try {
    const res = await axios.post(url, payload);
    result.value = JSON.stringify(res.data, null, 2);
  } catch (err) {
    result.value = err.toString();
  }
}
</script>

<style scoped>
.control-section {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
}
</style>
