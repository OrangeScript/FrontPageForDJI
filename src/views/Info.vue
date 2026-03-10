<template>
  <div class="info-page">
    <!-- 顶部状态栏 -->
    <div class="top-bar">
      <div class="top-left">
        <span class="sys-tag"><span class="pulse-dot"></span>DATA CENTER ONLINE</span>
        <span class="sep">|</span>
        <span class="clock">{{ clock }}</span>
      </div>
      <div class="top-right">
        <span>刷新周期: 1s</span>
        <span class="sep">|</span>
        <span>数据节点: CN-EAST-1</span>
      </div>
    </div>

    <!-- 统计卡片行 -->
    <div class="stat-row">
      <div class="stat-card" v-for="s in stats" :key="s.label">
        <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
        <div class="stat-icon">{{ s.icon }}</div>
        <div class="stat-info">
          <div class="stat-value" :style="{ color: s.color }">
            <span class="stat-num">{{ s.display }}</span>
            <span class="stat-unit">{{ s.unit }}</span>
          </div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
        <div ref="sparkRefs" class="spark-area"></div>
      </div>
    </div>

    <!-- 中间图表行 -->
    <div class="chart-row">
      <div class="panel wide-panel">
        <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
        <div class="panel-head"><span class="accent-bar"></span><span>飞行里程趋势 (近 12 月)</span></div>
        <div ref="areaChartRef" class="chart-box"></div>
      </div>
      <div class="panel narrow-panel">
        <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
        <div class="panel-head"><span class="accent-bar"></span><span>系统健康度</span></div>
        <div ref="radarChartRef" class="chart-box"></div>
      </div>
    </div>

    <!-- 飞行记录表 -->
    <div class="panel table-panel">
      <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
      <div class="panel-head">
        <div><span class="accent-bar"></span><span>单次飞行遥测日志明细</span></div>
        <el-input v-model="searchText" placeholder="搜索编号/操作员…" size="small" class="search-input" clearable :prefix-icon="Search" />
      </div>

      <el-table :data="pagedRecords" style="width:100%" :stripe="false" border max-height="400" :table-layout="'auto'">
        <el-table-column prop="id" label="任务编号" width="110" align="center" />
        <el-table-column prop="datetime" label="起飞时间 (UTC)" min-width="170" align="center" />
        <el-table-column prop="operator" label="操作员" width="110" align="center" />
        <el-table-column prop="drone" label="机型" width="120" align="center">
          <template #default="{ row }"><el-tag size="small" effect="dark" round>{{ row.drone }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="duration" label="飞行时长" width="100" align="center">
          <template #default="{ row }"><span class="mono">{{ row.duration }} min</span></template>
        </el-table-column>
        <el-table-column prop="mileage" label="里程 (km)" width="100" align="center">
          <template #default="{ row }"><span class="mono cyan">{{ row.mileage }}</span></template>
        </el-table-column>
        <el-table-column prop="maxAltitude" label="最大海拔 (m)" width="120" align="center">
          <template #default="{ row }"><span class="mono">{{ row.maxAltitude }}</span></template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <span class="flight-status" :class="row.status === '正常' ? 'ok' : 'warn'">{{ row.status }}</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-footer">
        <el-pagination background small
          v-model:current-page="currentPage"
          :page-size="pageSize"
          layout="total, prev, pager, next"
          :total="filteredRecords.length"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Search } from '@element-plus/icons-vue'

/* ============ 时钟 ============ */
const clock = ref('')
let clockTimer = null
const tickClock = () => { clock.value = new Date().toLocaleString('zh-CN', { hour12: false }) }

/* ============ 统计数据 ============ */
const stats = ref([
  { icon:'🛤️', label:'历史总里程',      value: 15280.5,  unit:'km',   color:'#3aa3ff', display:'15,280.5' },
  { icon:'⏱️', label:'累计飞行时长',    value: 326.8,    unit:'hrs',  color:'#00d4ff', display:'326.8' },
  { icon:'🛫', label:'起降总次数',      value: 142,      unit:'次',   color:'#00ff88', display:'142' },
  { icon:'📡', label:'活跃无人机数',    value: 6,        unit:'架',   color:'#f59e0b', display:'6' },
  { icon:'⚠️', label:'本月异常事件',    value: 3,        unit:'次',   color:'#ff3366', display:'3' },
])

/* ============ 飞行记录 ============ */
const allRecords = ref([
  { id:'FLT-001', datetime:'2026-03-01 08:15:22', operator:'张伟', drone:'M300 RTK',  duration:95,  mileage:18.4, maxAltitude:320, status:'正常' },
  { id:'FLT-002', datetime:'2026-03-01 10:30:00', operator:'李明', drone:'Phantom 4',  duration:42,  mileage:8.2,  maxAltitude:150, status:'正常' },
  { id:'FLT-003', datetime:'2026-03-02 06:45:10', operator:'王强', drone:'M30T',       duration:120, mileage:25.6, maxAltitude:450, status:'正常' },
  { id:'FLT-004', datetime:'2026-03-02 14:20:33', operator:'赵敏', drone:'Mavic 3E',   duration:38,  mileage:6.1,  maxAltitude:120, status:'正常' },
  { id:'FLT-005', datetime:'2026-03-03 09:00:00', operator:'刘芳', drone:'M300 RTK',  duration:110, mileage:22.3, maxAltitude:380, status:'异常' },
  { id:'FLT-006', datetime:'2026-03-04 07:30:45', operator:'陈浩', drone:'M30T',       duration:88,  mileage:15.7, maxAltitude:280, status:'正常' },
  { id:'FLT-007', datetime:'2026-03-05 11:15:20', operator:'杨涛', drone:'M300 RTK',  duration:135, mileage:28.9, maxAltitude:500, status:'正常' },
  { id:'FLT-008', datetime:'2026-03-06 08:00:00', operator:'周洁', drone:'M30T',       duration:72,  mileage:13.4, maxAltitude:260, status:'异常' },
  { id:'FLT-009', datetime:'2026-03-07 13:45:00', operator:'吴磊', drone:'Phantom 4',  duration:55,  mileage:9.8,  maxAltitude:180, status:'正常' },
  { id:'FLT-010', datetime:'2026-03-08 06:20:00', operator:'孙丽', drone:'M300 RTK',  duration:148, mileage:31.2, maxAltitude:520, status:'正常' },
  { id:'FLT-011', datetime:'2026-03-08 15:10:00', operator:'张伟', drone:'Mavic 3E',   duration:30,  mileage:4.5,  maxAltitude:100, status:'正常' },
  { id:'FLT-012', datetime:'2026-03-09 09:30:00', operator:'王强', drone:'M30T',       duration:105, mileage:20.1, maxAltitude:350, status:'异常' },
])

const searchText = ref('')
const currentPage = ref(1)
const pageSize = 8

const filteredRecords = computed(() => {
  if (!searchText.value) return allRecords.value
  const kw = searchText.value.toLowerCase()
  return allRecords.value.filter(r => r.id.toLowerCase().includes(kw) || r.operator.includes(kw))
})
const pagedRecords = computed(() => {
  const s = (currentPage.value - 1) * pageSize
  return filteredRecords.value.slice(s, s + pageSize)
})

/* ============ ECharts ============ */
const areaChartRef = ref(null)
const radarChartRef = ref(null)
let areaChart = null, radarChart = null

const initCharts = () => {
  // 面积图
  if (areaChartRef.value) {
    areaChart = echarts.init(areaChartRef.value)
    const months = ['4月','5月','6月','7月','8月','9月','10月','11月','12月','1月','2月','3月']
    areaChart.setOption({
      tooltip:{ trigger:'axis', backgroundColor:'rgba(6,22,42,.92)', borderColor:'rgba(58,163,255,.3)', textStyle:{color:'#e0e6ed'} },
      grid:{ top:20, right:20, bottom:30, left:50 },
      xAxis:{ type:'category', data:months, axisLine:{lineStyle:{color:'rgba(58,163,255,.2)'}}, axisLabel:{color:'#718096',fontSize:11} },
      yAxis:{ type:'value', name:'km', nameTextStyle:{color:'#718096'}, splitLine:{lineStyle:{color:'rgba(58,163,255,.06)'}}, axisLabel:{color:'#718096',fontSize:11} },
      series:[
        { type:'line', smooth:true, data:[980,1120,1350,1580,1420,1680,1520,1240,1380,1560,1290,1480],
          lineStyle:{color:'#3aa3ff',width:2.5}, symbol:'circle', symbolSize:6,
          itemStyle:{color:'#3aa3ff', borderColor:'#061a2c', borderWidth:2},
          areaStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(58,163,255,.3)'},{offset:1,color:'rgba(58,163,255,.02)'}])}
        },
        { type:'line', smooth:true, data:[820,950,1100,1320,1180,1400,1280,1050,1200,1380,1100,1300],
          lineStyle:{color:'#00ff88',width:2}, symbol:'circle', symbolSize:5,
          itemStyle:{color:'#00ff88', borderColor:'#061a2c', borderWidth:2},
          areaStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(0,255,136,.15)'},{offset:1,color:'rgba(0,255,136,.01)'}])}
        }
      ]
    })
  }

  // 雷达图
  if (radarChartRef.value) {
    radarChart = echarts.init(radarChartRef.value)
    radarChart.setOption({
      tooltip:{ backgroundColor:'rgba(6,22,42,.92)', borderColor:'rgba(58,163,255,.3)', textStyle:{color:'#e0e6ed'} },
      radar:{
        indicator:[
          {name:'通信链路',max:100},{name:'电池系统',max:100},{name:'飞控稳定',max:100},
          {name:'GPS信号',max:100},{name:'避障传感',max:100},{name:'云台精度',max:100}
        ],
        shape:'polygon',
        axisName:{color:'#718096',fontSize:11},
        splitLine:{lineStyle:{color:'rgba(58,163,255,.1)'}},
        splitArea:{areaStyle:{color:['rgba(58,163,255,.02)','rgba(58,163,255,.05)']}},
        axisLine:{lineStyle:{color:'rgba(58,163,255,.15)'}}
      },
      series:[{
        type:'radar',
        data:[{
          value:[92,88,95,90,85,93],
          name:'系统健康度',
          lineStyle:{color:'#00d4ff',width:2},
          areaStyle:{color:'rgba(0,212,255,.15)'},
          itemStyle:{color:'#00d4ff',borderColor:'#061a2c',borderWidth:2}
        }]
      }]
    })
  }
}

const onResize = () => { areaChart?.resize(); radarChart?.resize() }

onMounted(async () => {
  tickClock(); clockTimer = setInterval(tickClock, 1000)
  await nextTick()
  initCharts()
  window.addEventListener('resize', onResize)
})
onUnmounted(() => {
  clearInterval(clockTimer)
  areaChart?.dispose(); radarChart?.dispose()
  window.removeEventListener('resize', onResize)
})
</script>

<style scoped>
.info-page {
  min-height:100vh; padding:16px 24px 24px;
  background:#061a2c; color:#e0e6ed;
  font-family:'Segoe UI','PingFang SC',sans-serif;
}

/* 顶部栏 */
.top-bar {
  display:flex; justify-content:space-between; align-items:center;
  padding:8px 16px; margin-bottom:18px;
  background:rgba(8,30,55,.7); border:1px solid rgba(58,163,255,.08); border-radius:4px;
  font-size:12px; color:#718096; letter-spacing:.5px;
}
.sys-tag { color:#00ff88; display:inline-flex; align-items:center; gap:6px; font-weight:600; letter-spacing:1.5px; }
.pulse-dot { width:7px; height:7px; border-radius:50%; background:#00ff88; box-shadow:0 0 8px #00ff88; animation:pulse 1.5s ease-in-out infinite; }
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(.7)}}
.clock { font-family:'Courier New',monospace; color:#3aa3ff; }
.sep { margin:0 10px; color:rgba(58,163,255,.2); }

/* 统计卡片 */
.stat-row { display:grid; grid-template-columns:repeat(5,1fr); gap:16px; margin-bottom:20px; }
.stat-card {
  position:relative; display:flex; align-items:center; gap:14px;
  padding:18px 20px;
  background:rgba(8,30,55,.85); border:1px solid rgba(58,163,255,.1);
  border-radius:6px; transition:all .3s;
}
.stat-card:hover { border-color:rgba(0,212,255,.3); box-shadow:0 0 24px rgba(0,120,255,.1); }
.stat-icon { font-size:30px; }
.stat-info { display:flex; flex-direction:column; }
.stat-value { display:flex; align-items:baseline; gap:4px; }
.stat-num { font-size:26px; font-weight:700; font-family:'Courier New',monospace; }
.stat-unit { font-size:12px; color:#718096; }
.stat-label { font-size:12px; color:#718096; margin-top:2px; letter-spacing:.5px; }

/* 面板 */
.panel {
  position:relative; padding:18px 20px;
  background:rgba(8,30,55,.85); border:1px solid rgba(58,163,255,.1);
  border-radius:6px; margin-bottom:20px;
}
.corner{position:absolute;width:12px;height:12px;border-color:#00d4ff;border-style:solid;border-width:0}
.corner.tl{top:-1px;left:-1px;border-top-width:2px;border-left-width:2px}
.corner.tr{top:-1px;right:-1px;border-top-width:2px;border-right-width:2px}
.corner.bl{bottom:-1px;left:-1px;border-bottom-width:2px;border-left-width:2px}
.corner.br{bottom:-1px;right:-1px;border-bottom-width:2px;border-right-width:2px}

.panel-head {
  display:flex; justify-content:space-between; align-items:center;
  margin-bottom:14px; font-size:14px; font-weight:600; color:#e0e6ed;
}
.accent-bar { display:inline-block; width:4px; height:16px; background:#3aa3ff; border-radius:2px; margin-right:8px; vertical-align:middle; }

.search-input { width:220px; }
.search-input :deep(.el-input__wrapper){background:rgba(0,40,80,.5);border:1px solid rgba(58,163,255,.15);box-shadow:none !important;height:30px}
.search-input :deep(.el-input__inner){color:#c0ccda;font-size:12px}
.search-input :deep(.el-input__prefix .el-icon){color:#3aa3ff}

/* 图表行 */
.chart-row { display:grid; grid-template-columns:1fr 360px; gap:20px; }
.chart-box { height:240px; }

/* 表格 */
:deep(.el-table){background:transparent;--el-table-border-color:rgba(58,163,255,.08);--el-table-header-bg-color:rgba(58,163,255,.04);--el-table-tr-bg-color:transparent;--el-table-row-hover-bg-color:rgba(58,163,255,.08);color:#c0ccda}
:deep(.el-table th.el-table__cell){color:#3aa3ff;font-weight:600;border-bottom:1px solid rgba(58,163,255,.15);font-size:12px}
:deep(.el-table td.el-table__cell){border-bottom:1px solid rgba(58,163,255,.06);font-size:13px}

.mono { font-family:'Courier New',monospace; font-weight:600; }
.cyan { color:#00d4ff; }

.flight-status { padding:2px 10px; border-radius:10px; font-size:12px; font-weight:500; }
.flight-status.ok   { background:rgba(0,255,136,.1); color:#00ff88; }
.flight-status.warn { background:rgba(255,51,102,.1); color:#ff3366; }

.pagination-footer { margin-top:14px; display:flex; justify-content:flex-end; }
:deep(.el-pagination){color:#a0aec0}
:deep(.el-pagination .el-pager li:not(.is-active)){background:rgba(255,255,255,.06);color:#a0aec0;border-radius:4px}
:deep(.el-pagination .el-pager li.is-active){background:#3aa3ff;color:#fff;border-radius:4px}
:deep(.el-pagination .btn-prev),:deep(.el-pagination .btn-next){background:rgba(255,255,255,.06);color:#a0aec0;border-radius:4px}
</style>
