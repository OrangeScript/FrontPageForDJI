<script setup>
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

import {
  takeOff,
  land,
  goHome,
  hover,
  emergencyStop
} from '@/api/control'

import { sendVS } from '@/api/virtualStick'

/* ===== 虚拟摇杆状态 ===== */
const vs = reactive({
  mode: 'NORMAL',

  // NORMAL
  lv: 0,
  lh: 0,
  rv: 0,
  rh: 0,

  // ADVANCED
  pitch: 0,
  roll: 0,
  yaw: 0,
  throttle: 0
})


function onSendVS() {
  sendVS(vs)
  ElMessage.success('虚拟摇杆指令已发送')
}
</script>


<template>
  <div class="station">

    <!-- 标题 -->
    <el-page-header content="无人机地面控制站" />

    <el-row :gutter="20" class="main">

      <!-- 左：基础控制 -->
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header>🚁 基础控制</template>

          <el-space direction="vertical" fill size="large">

            <el-button-group>
              <el-button type="success" @click="takeOff">起飞</el-button>
              <el-button type="warning" @click="land">降落</el-button>
              <el-button type="primary" @click="hover">悬停</el-button>
              <el-button type="info" @click="goHome">返航</el-button>
            </el-button-group>

            <el-divider />

            <el-button
              type="danger"
              size="large"
              @click="emergencyStop"
            >
              紧急停止
            </el-button>

          </el-space>
        </el-card>
      </el-col>

      <!-- 右：虚拟摇杆 -->
      <el-col :span="14">
  <el-card shadow="hover">
    <template #header>🎮 虚拟摇杆</template>

    <el-form label-width="90px">

      <!-- 模式选择 -->
      <el-form-item label="模式">
        <el-radio-group v-model="vs.mode">
          <el-radio-button value="NORMAL">普通</el-radio-button>
          <el-radio-button value="ADVANCED">高级</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <!-- ========== NORMAL 模式 ========== -->
      <template v-if="vs.mode === 'NORMAL'">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="左摇杆">
              <el-slider v-model="vs.lv" :min="-1" :max="1" :step="0.05" />
              <el-slider v-model="vs.lh" :min="-1" :max="1" :step="0.05" />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="右摇杆">
              <el-slider v-model="vs.rv" :min="-1" :max="1" :step="0.05" />
              <el-slider v-model="vs.rh" :min="-1" :max="1" :step="0.05" />
            </el-form-item>
          </el-col>
        </el-row>
      </template>

      <!-- ========== ADVANCED 模式 ========== -->
      <template v-else>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="Pitch (°)">
              <el-slider v-model="vs.pitch" :min="-30" :max="30" />
            </el-form-item>

            <el-form-item label="Roll (°)">
              <el-slider v-model="vs.roll" :min="-30" :max="30" />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="Yaw (°/s)">
              <el-slider v-model="vs.yaw" :min="-180" :max="180" />
            </el-form-item>

            <el-form-item label="Throttle (%)">
              <el-slider v-model="vs.throttle" :min="0" :max="100" />
            </el-form-item>
          </el-col>
        </el-row>
      </template>

      <el-button
        type="primary"
        style="margin-top: 12px"
        @click="onSendVS"
      >
        发送摇杆指令
      </el-button>

    </el-form>
  </el-card>
</el-col>


    </el-row>
  </div>
</template>
