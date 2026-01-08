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
    <div class="dashboard">

      <!-- ===== TOP STATUS BAR ===== -->
      <div class="status-bar">
        <div class="status-item">
          <span>MODE</span>
          <strong>{{ telemetry.flightMode }}</strong>
        </div>
        <div class="status-item">
          <span>HDG</span>
          <strong>{{ telemetry.heading }}°</strong>
        </div>
        <div class="status-item">
          <span>SAT</span>
          <strong>{{ telemetry.satelliteCount }}</strong>
        </div>
        <div class="status-item">
          <span>HOME</span>
          <strong>{{ telemetry.distanceToHome }} m</strong>
        </div>
      </div>

      <!-- ===== MAIN GRID ===== -->
      <div class="main-grid">

        <!-- Battery -->
        <el-card class="panel battery" shadow="never">
          <template #header>🔋 BATTERY</template>

          <el-progress
            :percentage="telemetry.batteryLevel"
            :status="batteryColor"
            :stroke-width="16"
            striped
            striped-flow
          />

          <div class="battery-meta">
            <span>Remaining</span>
            <strong>{{ telemetry.remainingFlightTime }} s</strong>
          </div>
        </el-card>

        <!-- Attitude -->
        <el-card class="panel attitude" shadow="never">
          <template #header>🧭 ATTITUDE</template>

          <div class="attitude-grid">
            <div class="attitude-item">
              <span>PITCH</span>
              <strong>{{ telemetry.attitude?.pitch?.toFixed(2) }}</strong>
            </div>
            <div class="attitude-item">
              <span>ROLL</span>
              <strong>{{ telemetry.attitude?.roll?.toFixed(2) }}</strong>
            </div>
            <div class="attitude-item">
              <span>YAW</span>
              <strong>{{ telemetry.attitude?.yaw?.toFixed(2) }}</strong>
            </div>
          </div>
        </el-card>

        <!-- Location -->
        <el-card class="panel location" shadow="never">
          <template #header>📍 LOCATION</template>

          <div class="kv">
            <span>LAT</span>
            <strong>{{ telemetry.location?.lat }}</strong>
          </div>
          <div class="kv">
            <span>LON</span>
            <strong>{{ telemetry.location?.lon }}</strong>
          </div>
          <div class="kv">
            <span>ALT</span>
            <strong>{{ telemetry.location?.alt }} m</strong>
          </div>
        </el-card>

      </div>

      <!-- Speed -->
      <el-card class="panel speed" shadow="never">
        <template #header>🚀 SPEED VECTOR</template>
        <pre>{{ telemetry.speed }}</pre>
      </el-card>

    </div>
  </el-scrollbar>
</template>

<style scoped>
/* ===== Overall ===== */
.dashboard {
  padding: 16px;
  color: #e5eaf3;
  font-family: Inter, system-ui, sans-serif;
}

/* ===== Top Status Bar ===== */
.status-bar {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.status-item {
  background: rgba(18, 22, 30, 0.85);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  padding: 10px 12px;
  text-align: center;
}

.status-item span {
  display: block;
  font-size: 11px;
  color: #7c8593;
  letter-spacing: 1px;
}

.status-item strong {
  font-family: monospace;
  font-size: 18px;
  color: #4fd1c5;
}

/* ===== Main Grid ===== */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 1.4fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

/* ===== Panels ===== */
.panel {
  background: linear-gradient(180deg, #141822, #0b0f16);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 16px;
}

:deep(.el-card__header) {
  border-bottom: none;
  padding-bottom: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #9aa4b2;
  letter-spacing: 0.5px;
}

/* ===== Battery ===== */
.battery-meta {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 12px;
  color: #9aa4b2;
}

.battery-meta strong {
  color: #e5eaf3;
}

/* ===== Attitude ===== */
.attitude-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  text-align: center;
}

.attitude-item span {
  display: block;
  font-size: 11px;
  color: #7c8593;
  letter-spacing: 1px;
}

.attitude-item strong {
  font-family: monospace;
  font-size: 26px;
  color: #00ffd5;
}

/* ===== Location ===== */
.kv {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13px;
}

.kv span {
  color: #7c8593;
}

.kv strong {
  font-family: monospace;
  color: #e5eaf3;
}

/* ===== Speed ===== */
pre {
  background: #020409;
  border-radius: 12px;
  padding: 12px;
  color: #00ff88;
  font-size: 12px;
  overflow-x: auto;
}
</style>
