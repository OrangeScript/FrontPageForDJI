<template>
  <aside class="panel panel-right">
    <div class="panel-title">
      <span class="dot" />
      <span class="title-text">无人机状态</span>
    </div>

    <!-- 1) 开机/关机状态 -->
    <div class="right-scroll">
      <el-card class="card_status" shadow="never">
        <div class="uav-hero">
          <img class="uav-img" src="@/assets/Uav/无人机.png" alt="uav" />
          <div class="uav-state">{{ d.stateText }}</div>
        </div>
      </el-card>


      <!-- 2) X / Y 坐标 -->
      <el-card class="card_coords" shadow="never">
          <div class="metric">
            <div class="k">X坐标</div>
            <div class="v">{{ d.x }}</div>
          </div>
      </el-card>
      <el-card class="card_coords" shadow="never">
          <div class="metric">
            <div class="k">Y坐标</div>
            <div class="v">{{ d.y }}</div>
          </div>
      </el-card>

      <!-- 3) 高度 + 变焦 -->
      <div class="hv-row">
        <!-- 高度 -->
        <div class="hv-card">
          <div class="hv-icon">
            <!-- 简单上下箭头图标（纯 CSS） -->
            <span class="arrow up"></span>
            <span class="arrow down"></span>
          </div>

          <div class="hv-content">
            <div class="hv-label">高度(米)</div>
            <div class="hv-value">{{ Number(d.altitude).toFixed(1) }}</div>
          </div>
        </div>

        <!-- 变焦 -->
        <div class="hv-card">
          <div class="hv-icon zoom">
            <!-- 简单“手机/变焦框”图标（纯 CSS） -->
            <div class="zoom-rect"></div>
            <div class="zoom-corner tl"></div>
            <div class="zoom-corner tr"></div>
            <div class="zoom-corner bl"></div>
            <div class="zoom-corner br"></div>
          </div>

          <div class="hv-content">
            <div class="hv-label">变焦</div>
            <div class="hv-value">
              {{ d.zoom ?? 1 }}
              <span class="hv-unit">倍</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 4）速度 -->
      <div class="speed-row">
        <div class="speed-item">
          <div class="speed-title">水平速度 (m/s)</div>
          <div class="speed-gauge" ref="elHSpeed"></div>
        </div>

        <div class="speed-item">
          <div class="speed-title">垂直速度 (m/s)</div>
          <div class="speed-gauge" ref="elVSpeed"></div>
        </div>
      </div>

      <!-- 5）姿态：云台俯仰角 + 偏航角 -->
      <div class="att-row">
        <div class="att-item">
          <div class="att-title">云台俯仰角</div>
          <div class="att-gauge" ref="elPitch"></div>
          <div class="att-corner left">0°</div>
          <div class="att-corner right">-90°</div>
        </div>

        <div class="att-item">
          <div class="att-title">偏航角</div>
          <div class="att-gauge" ref="elYaw"></div>
        </div>
      </div>

      <!-- 6)遥控器状态/信号 -->
      <div class="rc-row">
        <!-- 遥控器状态 -->
        <div class="rc-item">
          <img class="rc-icon" src="@/assets/Uav/遥控器.png" alt="rc" />
          <div class="rc-text">
            <div class="rc-title">遥控器状态</div>
            <div class="rc-value rc-value-on">{{ d.rcStateText ?? '开机' }}</div>
          </div>
        </div>

        <!-- 遥控器信号 -->
        <div class="rc-item">
          <img class="rc-icon rc-icon-signal" src="@/assets/Uav/信号.png" alt="signal" />
          <div class="rc-text">
            <div class="rc-title">遥控器信号</div>
            <div class="rc-value rc-value-red">{{ d.rcSignal ?? 100 }}</div>
          </div>
        </div>
      </div>

      <!-- 7)电量 -->
      <div class="link-item">
        <div class="link-title">电量</div>

        <div class="link-body">
          <div class="link-bar" role="progressbar"
              :aria-valuenow="d.linkPercent ?? 0"
              aria-valuemin="0" aria-valuemax="100">
            <!-- 18格：根据百分比点亮 -->
            <span
              v-for="i in 18"
              :key="i"
              class="link-seg"
              :class="{ on: i <= Math.round(((d.linkPercent ?? 0) / 100) * 18) }"
            />
          </div>

          <div class="link-right">
            <span class="link-num">{{ Math.round(d.linkPercent ?? 0) }}</span>
            <span class="link-unit">%</span>
          </div>

        </div>
      </div>



    </div>

  </aside>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts/core'
import { GaugeChart } from 'echarts/charts'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([GaugeChart, CanvasRenderer])

// 绑定数据
const props = defineProps({
  data: {
    type: Object,
    default: () => ({
      stateText: '未知',  //无人机状态--开机/关机 
      x: 0,  //x坐标
      y: 0,  //y坐标
      altitude: 0.0,  //高度
      zoom: 1,  //变焦
      hSpeed: 0,  //水平速度
      vSpeed: 0,  //垂直速度
      elPitch: 0,  //俯仰角
      elYaw: 0,  //偏航角
      rcStateText: '关机',  //遥控器状态--开机/关机
      rcSignal: 100,  //遥控器信号
      linkPercent: 0,  //电量
    }),
  },
})

const d = computed(() => props.data || {})

// 无人机速度
const elHSpeed = ref(null)
const elVSpeed = ref(null)

let cH = null
let cV = null

function clamp(n, min, max) {
  const x = Number.isFinite(n) ? n : 0
  return Math.min(max, Math.max(min, x))
}

// 速度仪表盘
function speedGaugeOption(value, min, max, unit) {
  const v = clamp(value, min, max)
  const ratio = (v - min) / (max - min)
  const range = max - min
  const mid = (0 - min) / range              // 0 对应的百分比位置，比如 -10~10 就是 0.5
  const pos = (v - min) / range              // v 对应的百分比位置
  const eps = 1e-4                           // 防止 stop 相等导致渲染怪

  let stops
  if (v >= 0) {
    const p = Math.max(mid + eps, Math.min(1, pos))
    stops = [
      [mid, 'rgba(255,255,255,0.14)'],
      [p,   'rgba(58,163,255,0.95)'],
      [1,   'rgba(255,255,255,0.14)'],
    ]
  } else {
    const p = Math.max(0, Math.min(mid - eps, pos))
    stops = [
      [p,   'rgba(255,255,255,0.14)'],
      [mid, 'rgba(80, 255, 120, 0.85)'],
      [1,   'rgba(255,255,255,0.14)'],
    ]
  }


  return {
    backgroundColor: 'transparent',
    series: [
      {
        type: 'gauge',
        startAngle: 210,
        endAngle: -30,
        min,
        max,
        splitNumber: 5,

        axisLine: {
          lineStyle: {
            width: 10,
            color: stops,
          },
        },

        axisTick: {
          length: 6,
          lineStyle: { color: 'rgba(255,255,255,0.22)' },
        },
        splitLine: {
          length: 10,
          lineStyle: { color: 'rgba(255,255,255,0.22)' },
        },
        axisLabel: {
          color: 'rgba(255,255,255,0.55)',
          fontSize: 5,
        },

        pointer: {
          length: '60%',
          width: 3,
          itemStyle: { color: 'rgba(255,80,80,0.95)' },
        },
        anchor: {
          show: true,
          size: 6,
          itemStyle: {
            color: 'rgba(255,255,255,0.9)',
            borderColor: 'rgba(58, 163, 255, 0.85)',
            borderWidth: 2,
          },
        },

        detail: {
          valueAnimation: true,
          offsetCenter: [0, '42%'],
          formatter: (val) => `${Number(val).toFixed(1)}`,
          color: 'rgba(255,255,255,0.92)',
          fontSize: 14,
          fontWeight: 800,
        },

        title: {
          show: true,
          offsetCenter: [0, '72%'],
          color: 'rgba(255,255,255,0.55)',
          fontSize: 11,
          fontWeight: 600,
        },

        data: [{ value: v, name: unit }],
      },
    ],
  }
}


let inited = false
function initSpeed() {
  if (elHSpeed.value) cH = echarts.init(elHSpeed.value)
  if (elVSpeed.value) cV = echarts.init(elVSpeed.value)

  // 关键：第一次先画 0 作为初始位置
  cH && cH.setOption(speedGaugeOption(0, 0, 20, 'm/s'), true)       // 第一次可以 true
  cV && cV.setOption(speedGaugeOption(0, -10, 10, 'm/s'), true)     // 第一次可以 true

  inited = true

  // 再把真实值更新进去（这一步不要 notMerge=true）
  renderSpeed()
}

function renderSpeed() {
  if (!cH || !cV) return
  if (!inited) return

  // 关键：不要传 true（也就是 notMerge=false）
  cH.setOption(speedGaugeOption(d.value.hSpeed ?? 0, 0, 20, 'm/s'))
  cV.setOption(speedGaugeOption(d.value.vSpeed ?? 0, -10, 10, 'm/s'))
}


// ====== 俯仰角 + 偏航角 ======
const elPitch = ref(null)
const elYaw = ref(null)

let cPitch = null
let cYaw = null

function pitchOption(value) {
  // 0 ~ -90
  const min = -90
  const max = 0
  const v = clamp(value ?? 0, min, max)

  return {
    backgroundColor: 'transparent',

    // 右侧竖线（-90°边界）+ 可选上边线（0°边界）
    graphic: [
      // -90° 竖线（右侧）
      {
        id: 'pitch_line_down',
        type: 'line',
        silent: true,
        shape: { x1: 0, y1: 0, x2: 0, y2: 0 }, // 由 updatePitchGuides 动态写入
        style: {
          stroke: 'rgba(58,163,255,0.75)',
          lineWidth: 2,
        },
      },
      // 0° 上边线（可选：想更像图里“框”，就保留；不想要就删掉这个块）
      {
        id: 'pitch_line_left',
        type: 'line',
        silent: true,
        shape: { x1: 0, y1: 0, x2: 0, y2: 0 },
        style: {
          stroke: 'rgba(58,163,255,0.55)',
          lineWidth: 2,
        },
      },
    ],

    series: [
      // 1) 青蓝弧 + 9个中间刻度
      {
        type: 'gauge',
        startAngle: 270,  // 左
        endAngle: 180,    // 下（1/4圆）
        min,
        max,

        // 关键：只要“中间9个刻度”
        splitNumber: 9,
        axisTick: {
          show: true,
          splitNumber: 1, // 每一段只画 1 个刻度 => 一共 9 个刻度（不含两端）
          length: 7,
          lineStyle: { color: 'rgba(58,163,255,0.55)', width: 2 },
        },
        splitLine: { show: false }, // 关掉大刻度，避免画出两端分割线
        axisLabel: { show: false },

        // 弧线本体
        axisLine: {
          roundCap: false,
          lineStyle: {
            width: 10,
            color: [[1, 'rgba(58,163,255,0.55)']],
          },
        },

        pointer: { show: false },
        detail: { show: false },
        title: { show: false },

        // 中心放到右上角，留一点边距防止裁切
        center: ['84%', '18%'],
        radius: '140%',
        data: [{ value: 0 }],
      },

      // 2) 指针
      {
        type: 'gauge',
        startAngle: 270,
        endAngle: 180,
        min,
        max,
        splitNumber: 10,

        center: ['84%', '18%'],
        radius: '120%',

        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },

        pointer: {
          show: true,
          length: '92%',
          width: 3,
          itemStyle: { color: 'rgba(255,80,80,0.95)' },
        },
        anchor: {
          show: true,
          size: 7,
          itemStyle: {
            color: 'rgba(255,255,255,0.95)',
            borderColor: 'rgba(58,163,255,0.85)',
            borderWidth: 2,
          },
        },

        detail: { show: false },
        title: { show: false },
        data: [{ value: v }],
      },
    ],
  }
}

/**
 * 让右侧竖线/上边线跟随容器尺寸。
 * 你需要在 setOption 之后调用一次，并在 resize 后也调用。
 */
function updatePitchGuides(chart) {
  if (!chart) return
  const w = chart.getWidth()
  const h = chart.getHeight()

  // 必须和 option 里的 center/radius 对齐
  const cx = w * 0.84
  const cy = h * 0.18
  const r = Math.min(w, h) * 0.60 // 这个系数你可以微调到最像截图

  chart.setOption({
    graphic: [
      {
        id: 'pitch_line_down',
        shape: { x1: cx, y1: cy, x2: cx, y2: cy + r },
      },
      {
        id: 'pitch_line_left',
        shape: { x1: cx - r, y1: cy, x2: cx, y2: cy },
      },
    ],
  })
}

function yawCompassOption(value) {
  // 偏航角 0~360
  let v = Number.isFinite(value) ? value : 0
  v = ((v % 360) + 360) % 360

  return {
    backgroundColor: 'transparent',
    series: [
      {
        type: 'gauge',
        startAngle: 90,
        endAngle: -270,
        min: 0,
        max: 360,
        splitNumber: 12,
        radius: '92%',
        center: ['50%', '55%'],

        axisLine: {
          lineStyle: {
            width: 10,
            color: [[1, 'rgba(58,163,255,0.55)']],
          },
        },
        axisTick: { length: 6, lineStyle: { color: 'rgba(58,163,255,0.35)' } },
        splitLine: { length: 12, lineStyle: { color: 'rgba(58,163,255,0.50)' } },

        axisLabel: {
          color: 'rgba(180,220,255,0.85)',
          fontSize: 10,
          distance: 8,
          formatter: (val) => {
            // 只显示 东南西北
            if (val === 0 || val === 360) return '北'
            if (val === 90) return '东'
            if (val === 180) return '南'
            if (val === 270) return '西'
            return ''
          },
        },

        pointer: {
          length: '62%',
          width: 3,
          itemStyle: { color: 'rgba(255,80,80,0.95)' },
        },
        anchor: {
          show: true,
          size: 8,
          itemStyle: {
            color: 'rgba(255,255,255,0.95)',
            borderColor: 'rgba(58,163,255,0.85)',
            borderWidth: 2,
          },
        },

        title: { show: false },
        detail: { show: false },

        data: [{ value: v }],
      },
    ],

    // 中心“飞机/无人机”符号（用文字先占位，后面你也可以换成图片）
    graphic: [
      {
        type: 'circle',
        left: 'center',
        top: '52%',
        shape: { r: 18 },
        style: {
          fill: 'rgba(0,0,0,0.25)',
          stroke: 'rgba(58,163,255,0.55)',
          lineWidth: 2,
        },
      },
      {
        type: 'text',
        left: 'center',
        top: '50.5%',
        style: {
          text: '✈',
          fill: 'rgba(210,235,255,0.9)',
          fontSize: 16,
          fontWeight: 700,
          textAlign: 'center',
          textVerticalAlign: 'middle',
        },
      },
    ],
  }
}

function renderAtt() {
  if (!cPitch || !cYaw) return
  cPitch.setOption(pitchOption(d.value.elPitch), true)
  updatePitchGuides(cPitch)   
  cYaw.setOption(yawCompassOption(d.value.elYaw), true)
}

function initAtt() {
  if (elPitch.value) cPitch = echarts.init(elPitch.value)
  if (elYaw.value) cYaw = echarts.init(elYaw.value)

  renderAtt()

  requestAnimationFrame(() => {
    updatePitchGuides(cPitch)
  })
}

window.addEventListener('resize', () => {
  if (cPitch) {
    cPitch.resize()
    updatePitchGuides(cPitch)
  }
  if (cYaw) cYaw.resize()
})


// ===== 生命周期 =====
function resize() {
  cH?.resize()
  cV?.resize()
  cPitch?.resize()
  cYaw?.resize()
}

onMounted(() => {
  initSpeed()
  initAtt()
  window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  cH?.dispose()
  cV?.dispose()
  cPitch?.dispose()
  cYaw?.dispose()
})

watch(d, () => {
  renderSpeed()
  renderAtt()
}, { deep: true })

</script>

<style scoped>
.panel {
  background: rgba(9, 35, 60, 0.78);
  border-left: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  padding: 14px;
}

.panel-right{
  height: 100%;
  min-height: 0;               /* 关键：允许内部滚动容器计算高度 */
  display: flex;
  flex-direction: column;
  overflow: hidden;            /* 外层不滚，避免滚动条跑到外层 */
}

/* 真正滚动的容器 */
.right-scroll{
  flex: 1;
  min-height: 0;               /* 关键：没有它滚不出来 */
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 6px;          /* 给滚动条留点空间，避免遮挡 */
  padding-bottom: 16px;  /* 关键：给底部留白 */
  box-sizing: border-box;
}

/* 禁止卡片被压扁（关键） */
.right-scroll > *{
  flex-shrink: 0;
}

/* 滚动条样式（可选） */
.right-scroll::-webkit-scrollbar { width: 8px; }
.right-scroll::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.18);
  border-radius: 999px;
}
.right-scroll::-webkit-scrollbar-track { background: transparent; }


/* 标题 */
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

/* 无人机状态 */
.card_status {
  height: 120px;
  border-radius: 5px;
  margin: 0 0 8px 0;
  padding: 5px;
  display: grid;
  /* grid-template-rows: 1fr auto; */
  align-items: center;
  justify-items: center;

  /* 重点：蓝色略微透明 */
  background: rgba(6, 68, 138, 0.22);
  border: 1px solid rgba(47, 150, 246, 0.342);
  box-shadow: inset 0 0 20px rgba(58, 163, 255, 0.10);
}

.uav-hero {
  padding: 0px;
  display: grid;
  /* grid-template-rows: 1fr auto; */
  align-items: center;
  justify-items: center;
}

.uav-img {
  max-width: 80%;
  max-height: 80px;
  object-fit: contain;
  display: block;
}

.uav-state {
  margin-top: 6px;
  font-size: 16px;
  font-weight: 800;
  letter-spacing: 2px;
  color: rgba(0, 255, 210, 0.85); /* 偏青绿的“开机”效果 */
  text-shadow: 0 0 18px rgba(0, 255, 210, 0.25);
}

/* x/y坐标 */
.card_coords {
  height: 40px;
  border-radius: 5px;
  margin: 0 0 8px 0;
 
  display: flex;
  align-items: center;

  /* 重点：蓝色略微透明 */
  background: rgba(6, 68, 138, 0.22);
  border: 1px solid rgba(47, 150, 246, 0.342);
  box-shadow: inset 0 0 20px rgba(58, 163, 255, 0.10);
}

.card_coords :deep(.el-card__body) {
  padding: 0 15px; /* 你想要的左右内边距 */
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
}

.metric {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.k {
  order: 2;
  min-width: 52px;
  text-align: right !important;
  font-size: 12px;
  color: rgba(158, 208, 255, 0.65);
}

.v {
  order: 1;
  font-size: 18px;
  font-weight: 800;
  text-align: left !important;
  color: rgba(227, 239, 251, 0.92);
  letter-spacing: 0.5px;
}

/* 高度+变焦 */
/* 高度 + 变焦 一行两格 */
.hv-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.hv-card {
  height: 70px;
  border-radius: 5px;
  padding: 5px 15px;
  margin: 0 0 8px 0;

  display: grid;
  grid-template-columns: 46px 1fr;
  align-items: center;

  background: rgba(6, 68, 138, 0.22);
  border: 1px solid rgba(47, 150, 246, 0.342);
  box-shadow: inset 0 0 20px rgba(58, 163, 255, 0.10);
}

/* 左侧图标区域 */
.hv-icon {
  width: 40px;
  height: 56px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  position: relative;

  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(0, 0, 0, 0.14);
}

/* 高度上下箭头（纯 CSS） */
.hv-icon .arrow {
  position: absolute;
  width: 14px;
  height: 2px;
  background: rgba(120, 220, 255, 0.9);
  border-radius: 2px;
}
.hv-icon .arrow.up {
  top: 14px;
}
.hv-icon .arrow.down {
  bottom: 14px;
}
.hv-icon .arrow.up::after,
.hv-icon .arrow.down::after {
  content: "";
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
}
.hv-icon .arrow.up::after {
  top: -8px;
  border-bottom: 8px solid rgba(120, 220, 255, 0.9);
}
.hv-icon .arrow.down::after {
  bottom: -8px;
  border-top: 8px solid rgba(120, 220, 255, 0.9);
}

/* 变焦图标（纯 CSS） */
.hv-icon.zoom {
  display: grid;
  place-items: center;
}
.zoom-rect {
  width: 16px;
  height: 34px;
  border-radius: 3px;
  border: 2px solid rgba(140, 220, 255, 0.85);
  opacity: 0.9;
}
.zoom-corner {
  position: absolute;
  width: 10px;
  height: 10px;
  border: 2px solid rgba(140, 220, 255, 0.85);
  opacity: 0.55;
}
.zoom-corner.tl { left: 6px; top: 6px; border-right: 0; border-bottom: 0; }
.zoom-corner.tr { right: 6px; top: 6px; border-left: 0; border-bottom: 0; }
.zoom-corner.bl { left: 6px; bottom: 6px; border-right: 0; border-top: 0; }
.zoom-corner.br { right: 6px; bottom: 6px; border-left: 0; border-top: 0; }

/* 文字区 */
.hv-content {
  display: grid;
  gap: 6px;
  margin-left: 12px;
}

.hv-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.70);
}

.hv-value {
  font-size: 20px;
  font-weight: 800;
  color: rgba(255, 255, 255, 0.92);
  letter-spacing: 0.3px;
}

.hv-unit {
  margin-left: 6px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.65);
}

/* 速度 */
.speed-row{
  display:grid;
  grid-template-columns: 1fr 1fr;
  gap:12px;
  align-items: stretch;
}

.speed-item{
  display:grid;
  grid-template-rows: 8px 1fr;
  min-width:0;                 /* 防止 grid 子项撑破 */
}

.speed-title{
  font-size:12px;
  color:rgba(255,255,255,0.70);
  padding:0;                   /* 去掉左 padding */
  text-align:center;           /* 标题居中 */
  line-height:18px;
  white-space:nowrap;
}

.speed-gauge{
  width:100%;
  height:140px;
  display:flex;                
  align-items:center;
  justify-content:center;
  overflow:hidden;             /* 防止 ECharts 文字溢出 */
}

.speed-gauge > div,
.speed-gauge canvas{
  width:100% !important;
  height:100% !important;
}

/* 俯仰角+偏航角 */
.att-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  align-items: stretch;
  margin: 0 0 12px 0;
}

.att-item {
  position: relative;   /* ✅ 关键：让 corner 以这个块为参照 */
  display: grid;
  grid-template-rows: 15px 1fr;
  min-width: 0;
}

.att-title {
  font-size:12px;
  color:rgba(255,255,255,0.70);
  padding:0;                   /* 去掉左 padding */
  text-align:center;           /* 标题居中 */
  line-height:18px;
  white-space:nowrap;
}

.att-gauge {
  width:100%;
  height:140px;
  display:flex;                
  align-items:center;
  justify-content:center;
  overflow:hidden; 
}

.att-corner {
  position: absolute;
  font-size: 12px;
  color: rgba(58,163,255,0.9);
  line-height: 1;
  pointer-events: none;
}

.att-corner.left {   /* 0° */
  left: 2px;
  top: 38px;         /* 避开标题，数值可微调 */
}

.att-corner.right {  /* -90° */
  right: 15px;
  bottom: 0px;
}

/* 遥控器状态/信号 */
/* 两块并排 */
.rc-row{
  display:grid;
  grid-template-columns: 1fr 1fr;
  gap: 45px;
  align-items: center;
  margin: 0 0 8px 8px;
}

/* 单块：透明，无卡片 */
.rc-item{
  display:grid;
  grid-template-columns: 48px 1fr;
  align-items:center;
  column-gap: 5px;
  min-width: 0;
}

/* 图标 */
.rc-icon{
  width: 40px;
  height: 55px;
  object-fit: contain;
  display:block;
  filter: drop-shadow(0 0 10px rgba(58,163,255,0.18));
}

/* 信号图标更细长一点（按你图） */
.rc-icon-signal{
  width: 34px;
  height: 55px;
}

/* 右侧两行文字 */
.rc-text{
  display:grid;
  grid-template-rows: 16px 1fr;
  row-gap: 8px;
  min-width: 0;
}

/* 小标题 */
.rc-title{
  font-size: 12px;
  color: rgba(255,255,255,0.70);
  line-height: 16px;
  white-space: nowrap;
}

/* 大数值 */
.rc-value{
  font-size: 22px;
  font-weight: 800;
  letter-spacing: 1px;
  line-height: 24px;
  color: rgba(235, 248, 255, 0.95);
  text-shadow: 0 0 10px rgba(58,163,255,0.18);
  white-space: nowrap;
}

/* “开机”更像图里的青绿（可选） */
.rc-value-on{
  color: rgba(0, 255, 210, 0.85);
  text-shadow: 0 0 18px rgba(0, 255, 210, 0.22);
}

/* “100”红色 */
.rc-value-red{
  color: rgba(255, 80, 80, 0.95);
  text-shadow: 0 0 12px rgba(255, 80, 80, 0.18);
}

/* 电量 */
.link-item{
  margin-top: 15px;
  margin-bottom: 10px;
}

.link-title{
  font-size: 12px;
  color: rgba(255,255,255,0.70);
  line-height: 16px;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.link-body{
  display:flex;
  align-items:center;
  gap: 10px;
}

/* 外框条 */
.link-bar{
  height: 18px;
  flex: 1;
  min-width: 0;

  display:grid;
  grid-template-columns: repeat(18, 1fr);
  column-gap: 3px;

  padding: 3px 4px;
  border-radius: 2px;

  border: 1px solid rgba(58, 163, 255, 0.55);
  background: rgba(0, 0, 0, 0.16);
  box-shadow: inset 0 0 12px rgba(58, 163, 255, 0.10);
}

/* 每一小格 */
.link-seg{
  border-radius: 1px;
  background: rgba(58, 163, 255, 0.18);
}

/* 点亮的小格 */
.link-seg.on{
  background: rgba(58, 163, 255, 0.92);
  box-shadow: 0 0 10px rgba(58, 163, 255, 0.22);
}

/* 右侧数值+单位 % */
.link-right{
  display:flex;
  align-items: baseline;
  gap: 4px;
  min-width: 44px;          /* 保证右侧不会太挤 */
  justify-content: flex-end;
}

.link-num{
  font-size: 14px;
  font-weight: 900;
  color: rgba(58, 163, 255, 0.85);   /* 数值偏白 */
  line-height: 18px;
  text-shadow: 0 0 10px rgba(58, 163, 255, 0.12);
}

.link-unit{
  font-size: 14px;
  font-weight: 700;
  color: rgba(58, 163, 255, 0.85);   /* % 偏蓝 */
  line-height: 18px;
}


</style>
