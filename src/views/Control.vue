<script setup>
import { ref } from 'vue'
import * as ctrl from '@/api/control'
import { ElMessage } from 'element-plus'

const loading = ref(false)

const wp = ref({ lat: 0, lon: 0, alt: 10, yaw: 0 })
const stick = ref({ lx: 0, ly: 0, rx: 0, ry: 0 })
const gimbal = ref({ roll: 0, pitch: 0, yaw: 0 })
const zoom = ref(1)

async function exec(fn, msg) {
  try {
    loading.value = true
    await fn()
    ElMessage.success(msg)
  } catch (e) {
    ElMessage.error('Command failed')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <el-scrollbar height="100%">
    <el-row :gutter="16">

      <!-- Flight -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>✈️ Flight</template>
          <el-space>
            <el-button type="success" @click="exec(ctrl.takeoff,'Takeoff')" :loading="loading">Takeoff</el-button>
            <el-button type="warning" @click="exec(ctrl.land,'Land')" :loading="loading">Land</el-button>
            <el-button type="danger" @click="exec(ctrl.RTH,'RTH')" :loading="loading">RTH</el-button>
          </el-space>
        </el-card>
      </el-col>

      <!-- Navigation -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>📍 Navigation</template>

          <el-form label-width="70px" inline>
            <el-form-item label="Lat">
              <el-input-number v-model="wp.lat" :step="0.00001" />
            </el-form-item>
            <el-form-item label="Lon">
              <el-input-number v-model="wp.lon" :step="0.00001" />
            </el-form-item>
            <el-form-item label="Alt">
              <el-input-number v-model="wp.alt" />
            </el-form-item>
            <el-form-item label="Yaw">
              <el-input-number v-model="wp.yaw" />
            </el-form-item>
          </el-form>

          <el-space>
            <el-button type="primary"
              @click="exec(() => ctrl.gotoWP(wp.lat, wp.lon, wp.alt),'gotoWP')"
              :loading="loading">gotoWP</el-button>

            <el-button type="primary"
              @click="exec(() => ctrl.gotoWPwithPID(wp.lat, wp.lon, wp.alt, wp.yaw),'gotoWPwithPID')"
              :loading="loading">PID</el-button>
          </el-space>
        </el-card>
      </el-col>

      <!-- Virtual Stick -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>🎮 Virtual Stick</template>

          <el-form label-width="60px" inline>
            <el-form-item label="LX上下"><el-input-number v-model="stick.lx" /></el-form-item>
            <el-form-item label="LY旋转"><el-input-number v-model="stick.ly" /></el-form-item>
            <el-form-item label="RX左右"><el-input-number v-model="stick.rx" /></el-form-item>
            <el-form-item label="RY前后"><el-input-number v-model="stick.ry" /></el-form-item>
          </el-form>

          <el-space>
            <el-button @click="exec(ctrl.enableVirtualStick,'Enable VS')" type="success">Enable</el-button>
            <el-button
              @click="exec(() => ctrl.stick(stick.lx, stick.ly, stick.rx, stick.ry),'Stick sent')"
              type="primary">Send</el-button>
            <el-button @click="exec(ctrl.abortMission,'Abort VS')" type="danger">Abort</el-button>
          </el-space>
        </el-card>
      </el-col>

      <!-- Attitude -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>🧭 Attitude</template>
          <el-space>
            <el-input-number v-model="wp.yaw" />
            <el-button @click="exec(() => ctrl.gotoYaw(wp.yaw),'Yaw')" type="primary">Yaw</el-button>
            <el-input-number v-model="wp.alt" />
            <el-button @click="exec(() => ctrl.gotoAltitude(wp.alt),'Altitude')" type="primary">Alt</el-button>
          </el-space>
        </el-card>
      </el-col>

      <!-- Camera -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>🎥 Camera</template>
          <el-space>
            <el-input-number v-model="zoom" :min="1" />
            <el-button @click="exec(() => ctrl.zoomCamera(zoom),'Zoom')" type="primary">Zoom</el-button>
            <el-button @click="exec(ctrl.startRecording,'REC')" type="success">REC</el-button>
            <el-button @click="exec(ctrl.stopRecording,'STOP')" type="danger">STOP</el-button>
          </el-space>
        </el-card>
      </el-col>

      <!-- Gimbal -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>🎛 Gimbal</template>
          <el-form inline>
            <el-input-number v-model="gimbal.roll" />
            <el-input-number v-model="gimbal.pitch" />
            <el-input-number v-model="gimbal.yaw" />
          </el-form>
          <el-space>
            <el-button
              @click="exec(() => ctrl.gimbalPitch(gimbal.roll,gimbal.pitch,gimbal.yaw),'Pitch')">
              Pitch
            </el-button>
            <el-button
              @click="exec(() => ctrl.gimbalYaw(gimbal.roll,gimbal.pitch,gimbal.yaw),'Yaw')">
              Yaw
            </el-button>
          </el-space>
        </el-card>
      </el-col>

    </el-row>
  </el-scrollbar>
</template>

<style scoped>
.el-card {
  min-height: 220px;
}
</style>
