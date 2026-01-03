<script setup>
import { onMounted, computed } from 'vue'
import { telemetry, connectTelemetry } from '@/api/info'

onMounted(() => {
  connectTelemetry()
})

const batteryColor = computed(() => {
  if (telemetry.batteryLevel > 50) return 'success'
  if (telemetry.batteryLevel > 20) return 'warning'
  return 'exception'
})
</script>

<template>
  <el-scrollbar height="100%">
    <el-space direction="vertical" fill size="large">

      <!-- Status -->
      <el-card shadow="hover">
        <template #header>📡 Flight Status</template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Mode">
            {{ telemetry.flightMode }}
          </el-descriptions-item>

          <el-descriptions-item label="Heading">
            {{ telemetry.heading }}°
          </el-descriptions-item>

          <el-descriptions-item label="Satellites">
            {{ telemetry.satelliteCount }}
          </el-descriptions-item>

          <el-descriptions-item label="Distance Home">
            {{ telemetry.distanceToHome }} m
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- Battery -->
      <el-card shadow="hover">
        <template #header>🔋 Battery</template>

        <el-progress
          :percentage="telemetry.batteryLevel"
          :status="batteryColor"
          :stroke-width="18"
        />
        <p>Remaining Flight Time: {{ telemetry.remainingFlightTime }} s</p>
      </el-card>

      <!-- Location -->
      <el-card shadow="hover">
        <template #header>📍 Location</template>

        <el-descriptions :column="1" border>
          <el-descriptions-item label="Latitude">
            {{ telemetry.location?.lat }}
          </el-descriptions-item>
          <el-descriptions-item label="Longitude">
            {{ telemetry.location?.lon }}
          </el-descriptions-item>
          <el-descriptions-item label="Altitude">
            {{ telemetry.location?.alt }} m
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- Attitude -->
      <el-card shadow="hover">
        <template #header>🧭 Attitude</template>

        <el-descriptions :column="3" border>
          <el-descriptions-item label="Pitch">
            {{ telemetry.attitude?.pitch }}
          </el-descriptions-item>
          <el-descriptions-item label="Roll">
            {{ telemetry.attitude?.roll }}
          </el-descriptions-item>
          <el-descriptions-item label="Yaw">
            {{ telemetry.attitude?.yaw }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- Speed -->
      <el-card shadow="hover">
        <template #header>🚀 Speed</template>
        <pre>{{ telemetry.speed }}</pre>
      </el-card>

    </el-space>
  </el-scrollbar>
</template>

<style scoped>
pre {
  background: #111;
  color: #0f0;
  padding: 8px;
}
</style>
