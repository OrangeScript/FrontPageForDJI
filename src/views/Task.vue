<template>
  <div class="task-page">
    <!-- 顶部指标条 -->
    <div class="metrics-strip">
      <div class="metric-box" v-for="m in metrics" :key="m.label">
        <div class="metric-icon">{{ m.icon }}</div>
        <div class="metric-body">
          <span class="metric-val" :style="{ color: m.color }">{{ m.value }}</span>
          <span class="metric-label">{{ m.label }}</span>
        </div>
      </div>
    </div>

    <!-- 主体：左表格 + 右图表 -->
    <div class="main-grid">
      <!-- 左侧：任务列表 -->
      <div class="panel table-panel">
        <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
        <div class="panel-head">
          <span class="panel-title"><span class="accent-bar"></span>任务作战清单</span>
          <div class="head-actions">
            <el-select v-model="filterStatus" placeholder="状态筛选" size="small" clearable class="filter-select">
              <el-option label="全部" value="" />
              <el-option label="已完成" value="已完成" />
              <el-option label="执行中" value="执行中" />
              <el-option label="待执行" value="待执行" />
              <el-option label="已取消" value="已取消" />
            </el-select>
            <el-button size="small" class="add-btn" @click="showAddDialog = true">+ 新建任务</el-button>
          </div>
        </div>

        <el-table :data="pagedTasks" style="width:100%" :stripe="false" border max-height="520" :table-layout="'auto'">
          <el-table-column prop="id" label="编号" width="90" align="center" />
          <el-table-column prop="name" label="任务名称" min-width="150">
            <template #default="{ row }">
              <span class="task-name">{{ row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="type" label="类型" width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small" :type="typeTag(row.type)" effect="dark" round>{{ row.type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="priority" label="优先级" width="90" align="center">
            <template #default="{ row }">
              <span class="priority-dot" :class="row.priority"></span>{{ row.priority }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <span class="status-badge" :class="statusClass(row.status)">
                <span class="status-dot"></span>{{ row.status }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="operator" label="操作员" width="100" align="center" />
          <el-table-column prop="date" label="执行日期" width="120" align="center" />
        </el-table>

        <div class="pagination-footer">
          <el-pagination background small
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[8,15,30]"
            layout="total, sizes, prev, pager, next"
            :total="filteredTasks.length"
          />
        </div>
      </div>

      <!-- 右侧：图表区域 -->
      <div class="chart-col">
        <div class="panel chart-panel">
          <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
          <div class="panel-head"><span class="panel-title"><span class="accent-bar"></span>任务状态分布</span></div>
          <div ref="pieRef" class="chart-box"></div>
        </div>
        <div class="panel chart-panel">
          <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
          <div class="panel-head"><span class="panel-title"><span class="accent-bar"></span>月度任务趋势</span></div>
          <div ref="lineRef" class="chart-box"></div>
        </div>
      </div>
    </div>

    <!-- 新建任务弹窗 -->
    <el-dialog v-model="showAddDialog" title="创建新任务" width="440" class="add-dialog" :append-to-body="true">
      <el-form :model="newTask" label-width="80px">
        <el-form-item label="任务名称"><el-input v-model="newTask.name" placeholder="输入任务名称" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="newTask.type" style="width:100%">
            <el-option label="巡检" value="巡检" /><el-option label="测绘" value="测绘" />
            <el-option label="搜救" value="搜救" /><el-option label="侦察" value="侦察" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-radio-group v-model="newTask.priority">
            <el-radio label="紧急" /><el-radio label="高" /><el-radio label="中" /><el-radio label="低" />
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog=false">取消</el-button>
        <el-button type="primary" @click="addTask">确认创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

/* ============ Mock 数据 ============ */
const allTasks = ref([
  { id:'TSK-001', name:'北区 220kV 线路巡检',   type:'巡检', priority:'高',  status:'已完成', operator:'张伟',  date:'2026-03-01', drone:'M300 RTK' },
  { id:'TSK-002', name:'南区光伏阵列测绘',      type:'测绘', priority:'中',  status:'已完成', operator:'李明',  date:'2026-03-02', drone:'Phantom 4' },
  { id:'TSK-003', name:'西区山林火情侦察',      type:'侦察', priority:'紧急',status:'执行中', operator:'王强',  date:'2026-03-03', drone:'M30T' },
  { id:'TSK-004', name:'东区河道水质采样',      type:'巡检', priority:'低',  status:'待执行', operator:'赵敏',  date:'2026-03-04', drone:'M300 RTK' },
  { id:'TSK-005', name:'中心广场人流热力测绘',  type:'测绘', priority:'中',  status:'已完成', operator:'刘芳',  date:'2026-03-04', drone:'Mavic 3E' },
  { id:'TSK-006', name:'港口集装箱盘点巡检',    type:'巡检', priority:'高',  status:'执行中', operator:'陈浩',  date:'2026-03-05', drone:'M30T' },
  { id:'TSK-007', name:'山区失联人员搜救',      type:'搜救', priority:'紧急',status:'已完成', operator:'杨涛',  date:'2026-03-05', drone:'M300 RTK' },
  { id:'TSK-008', name:'高速公路事故现场侦察',  type:'侦察', priority:'紧急',status:'已完成', operator:'周洁',  date:'2026-03-06', drone:'M30T' },
  { id:'TSK-009', name:'农田植被 NDVI 测绘',    type:'测绘', priority:'低',  status:'待执行', operator:'吴磊',  date:'2026-03-07', drone:'Phantom 4' },
  { id:'TSK-010', name:'化工园区泄漏排查',      type:'巡检', priority:'高',  status:'执行中', operator:'孙丽',  date:'2026-03-07', drone:'M300 RTK' },
  { id:'TSK-011', name:'水库大坝裂缝检测',      type:'巡检', priority:'高',  status:'已完成', operator:'张伟',  date:'2026-03-08', drone:'M300 RTK' },
  { id:'TSK-012', name:'城区 5G 信号覆盖测绘',  type:'测绘', priority:'中',  status:'已取消', operator:'李明',  date:'2026-03-08', drone:'Mavic 3E' },
  { id:'TSK-013', name:'森林防火夜间巡检',      type:'巡检', priority:'紧急',status:'执行中', operator:'王强',  date:'2026-03-09', drone:'M30T' },
  { id:'TSK-014', name:'地震灾区生存搜救',      type:'搜救', priority:'紧急',status:'待执行', operator:'杨涛',  date:'2026-03-10', drone:'M300 RTK' },
  { id:'TSK-015', name:'风电场叶片缺陷检测',    type:'巡检', priority:'中',  status:'待执行', operator:'陈浩',  date:'2026-03-10', drone:'M300 RTK' },
  { id:'TSK-016', name:'边境线异常活动侦察',    type:'侦察', priority:'高',  status:'待执行', operator:'周洁',  date:'2026-03-11', drone:'M30T' },
  { id:'TSK-017', name:'高层建筑外墙巡检',      type:'巡检', priority:'低',  status:'已取消', operator:'刘芳',  date:'2026-03-11', drone:'Mavic 3E' },
  { id:'TSK-018', name:'湿地生态多光谱测绘',    type:'测绘', priority:'中',  status:'待执行', operator:'吴磊',  date:'2026-03-12', drone:'Phantom 4' },
])

/* ============ 顶部指标 ============ */
const metrics = computed(() => {
  const t = allTasks.value
  return [
    { icon:'📋', label:'任务总数',  value: t.length,                          color:'#3aa3ff' },
    { icon:'✅', label:'已完成',    value: t.filter(x=>x.status==='已完成').length, color:'#00ff88' },
    { icon:'🔥', label:'执行中',    value: t.filter(x=>x.status==='执行中').length, color:'#f59e0b' },
    { icon:'⏳', label:'待执行',    value: t.filter(x=>x.status==='待执行').length, color:'#00d4ff' },
    { icon:'🚨', label:'紧急任务',  value: t.filter(x=>x.priority==='紧急').length, color:'#ff3366' },
  ]
})

/* ============ 筛选 & 分页 ============ */
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(8)

const filteredTasks = computed(() => {
  if (!filterStatus.value) return allTasks.value
  return allTasks.value.filter(t => t.status === filterStatus.value)
})
const pagedTasks = computed(() => {
  const s = (currentPage.value - 1) * pageSize.value
  return filteredTasks.value.slice(s, s + pageSize.value)
})

/* 标签颜色 */
const typeTag = (t) => ({ '巡检':'', '测绘':'success', '搜救':'danger', '侦察':'warning' }[t] || '')
const statusClass = (s) => ({ '已完成':'done', '执行中':'running', '待执行':'pending', '已取消':'cancelled' }[s] || '')

/* ============ 新建任务 ============ */
const showAddDialog = ref(false)
const newTask = ref({ name:'', type:'巡检', priority:'中' })
const addTask = () => {
  if (!newTask.value.name) { ElMessage.warning('请输入任务名称'); return }
  const id = `TSK-${String(allTasks.value.length + 1).padStart(3,'0')}`
  allTasks.value.unshift({
    id, name: newTask.value.name, type: newTask.value.type, priority: newTask.value.priority,
    status:'待执行', operator:'当前用户', date: new Date().toISOString().slice(0,10), drone:'M300 RTK'
  })
  showAddDialog.value = false
  newTask.value = { name:'', type:'巡检', priority:'中' }
  ElMessage.success('任务已创建')
  renderCharts()
}

/* ============ ECharts ============ */
const pieRef = ref(null)
const lineRef = ref(null)
let pieChart = null, lineChart = null

const renderCharts = () => {
  // 饼图
  const statusMap = {}
  allTasks.value.forEach(t => { statusMap[t.status] = (statusMap[t.status]||0) + 1 })
  const pieData = Object.entries(statusMap).map(([name,value]) => ({ name, value }))
  const colorMap = { '已完成':'#00ff88', '执行中':'#f59e0b', '待执行':'#00d4ff', '已取消':'#ff3366' }

  if (!pieChart && pieRef.value) pieChart = echarts.init(pieRef.value)
  pieChart?.setOption({
    tooltip:{ trigger:'item', backgroundColor:'rgba(6,22,42,.9)', borderColor:'rgba(58,163,255,.3)', textStyle:{color:'#e0e6ed'} },
    legend:{ bottom:0, textStyle:{color:'#a0aec0',fontSize:11}, itemWidth:10, itemHeight:10 },
    series:[{
      type:'pie', radius:['42%','68%'], center:['50%','45%'],
      label:{ color:'#a0aec0', fontSize:11, formatter:'{b}\n{d}%' },
      labelLine:{ lineStyle:{color:'rgba(58,163,255,.3)'} },
      data: pieData.map(d=>({ ...d, itemStyle:{ color: colorMap[d.name]||'#3aa3ff' } })),
      emphasis:{ itemStyle:{ shadowBlur:20, shadowColor:'rgba(0,212,255,.4)' } }
    }]
  })

  // 折线图
  const months = ['1月','2月','3月','4月','5月','6月']
  if (!lineChart && lineRef.value) lineChart = echarts.init(lineRef.value)
  lineChart?.setOption({
    tooltip:{ trigger:'axis', backgroundColor:'rgba(6,22,42,.9)', borderColor:'rgba(58,163,255,.3)', textStyle:{color:'#e0e6ed'} },
    grid:{ top:30, right:16, bottom:28, left:40 },
    xAxis:{ type:'category', data:months, axisLine:{lineStyle:{color:'rgba(58,163,255,.2)'}}, axisLabel:{color:'#a0aec0',fontSize:11} },
    yAxis:{ type:'value', splitLine:{lineStyle:{color:'rgba(58,163,255,.08)'}}, axisLabel:{color:'#a0aec0',fontSize:11} },
    series:[
      { name:'新增任务', type:'line', smooth:true, data:[12,19,15,22,18,allTasks.value.length], lineStyle:{color:'#3aa3ff',width:2}, itemStyle:{color:'#3aa3ff'}, areaStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(58,163,255,.25)'},{offset:1,color:'rgba(58,163,255,.02)'}])} },
      { name:'完成任务', type:'line', smooth:true, data:[8,14,11,18,15,allTasks.value.filter(x=>x.status==='已完成').length], lineStyle:{color:'#00ff88',width:2}, itemStyle:{color:'#00ff88'}, areaStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(0,255,136,.2)'},{offset:1,color:'rgba(0,255,136,.02)'}])} },
    ]
  })
}

const onResize = () => { pieChart?.resize(); lineChart?.resize() }

onMounted(async () => {
  await nextTick()
  renderCharts()
  window.addEventListener('resize', onResize)
})
onUnmounted(() => {
  pieChart?.dispose(); lineChart?.dispose()
  window.removeEventListener('resize', onResize)
})

watch(allTasks, renderCharts, { deep: true })
</script>

<style scoped>
.task-page {
  min-height:100vh; padding:20px 24px;
  background:#061a2c; color:#e0e6ed;
  font-family:'Segoe UI','PingFang SC',sans-serif;
}

/* ---- 指标条 ---- */
.metrics-strip {
  display:flex; gap:16px; margin-bottom:20px;
}
.metric-box {
  flex:1; display:flex; align-items:center; gap:12px;
  padding:16px 20px;
  background:rgba(8,30,55,.85);
  border:1px solid rgba(58,163,255,.12);
  border-radius:6px;
  transition:border-color .3s, box-shadow .3s;
}
.metric-box:hover {
  border-color:rgba(0,212,255,.3);
  box-shadow:0 0 20px rgba(0,120,255,.1);
}
.metric-icon { font-size:28px; }
.metric-val { font-size:28px; font-weight:700; font-family:'Courier New',monospace; }
.metric-label { font-size:12px; color:#718096; letter-spacing:.5px; }
.metric-body { display:flex; flex-direction:column; }

/* ---- 主布局 ---- */
.main-grid { display:grid; grid-template-columns:1fr 420px; gap:20px; }

/* ---- 面板通用 ---- */
.panel {
  position:relative; padding:20px;
  background:rgba(8,30,55,.85);
  border:1px solid rgba(58,163,255,.12);
  border-radius:6px;
}
.corner{position:absolute;width:14px;height:14px;border-color:#00d4ff;border-style:solid;border-width:0}
.corner.tl{top:-1px;left:-1px;border-top-width:2px;border-left-width:2px}
.corner.tr{top:-1px;right:-1px;border-top-width:2px;border-right-width:2px}
.corner.bl{bottom:-1px;left:-1px;border-bottom-width:2px;border-left-width:2px}
.corner.br{bottom:-1px;right:-1px;border-bottom-width:2px;border-right-width:2px}

.panel-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.panel-title { font-size:15px; font-weight:600; color:#e0e6ed; display:flex; align-items:center; gap:8px; }
.accent-bar { width:4px; height:18px; background:#3aa3ff; border-radius:2px; display:inline-block; }

.head-actions { display:flex; gap:10px; align-items:center; }
.filter-select { width:120px; }
.filter-select :deep(.el-input__wrapper){background:rgba(0,40,80,.5);border:1px solid rgba(58,163,255,.2);box-shadow:none !important;height:30px}
.filter-select :deep(.el-input__inner){color:#c0ccda;font-size:12px}

.add-btn {
  background:linear-gradient(135deg,#0060c0,#00a0ff);color:#fff;border:none;
  font-weight:600;letter-spacing:.5px;
}
.add-btn:hover { box-shadow:0 0 16px rgba(0,120,255,.3); }

/* ---- 表格 ---- */
:deep(.el-table){background:transparent;--el-table-border-color:rgba(58,163,255,.08);--el-table-header-bg-color:rgba(58,163,255,.05);--el-table-tr-bg-color:transparent;--el-table-row-hover-bg-color:rgba(58,163,255,.08);color:#c0ccda}
:deep(.el-table th.el-table__cell){color:#3aa3ff;font-weight:600;border-bottom:1px solid rgba(58,163,255,.15);font-size:12px}
:deep(.el-table td.el-table__cell){border-bottom:1px solid rgba(58,163,255,.06);font-size:13px}

.task-name { font-weight:500; color:#e0e6ed; }

/* 优先级圆点 */
.priority-dot {
  display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px;
}
.priority-dot.紧急 { background:#ff3366; box-shadow:0 0 6px #ff3366; }
.priority-dot.高   { background:#f59e0b; box-shadow:0 0 6px #f59e0b; }
.priority-dot.中   { background:#3aa3ff; }
.priority-dot.低   { background:#718096; }

/* 状态徽章 */
.status-badge {
  display:inline-flex; align-items:center; gap:5px;
  padding:2px 10px; border-radius:12px; font-size:12px; font-weight:500;
}
.status-dot { width:6px; height:6px; border-radius:50%; }
.status-badge.done     { background:rgba(0,255,136,.1); color:#00ff88; }
.status-badge.done .status-dot { background:#00ff88; }
.status-badge.running  { background:rgba(245,158,11,.1); color:#f59e0b; }
.status-badge.running .status-dot { background:#f59e0b; animation:blink 1.2s infinite; }
.status-badge.pending  { background:rgba(0,212,255,.1); color:#00d4ff; }
.status-badge.pending .status-dot { background:#00d4ff; }
.status-badge.cancelled{ background:rgba(255,51,102,.1); color:#ff3366; }
.status-badge.cancelled .status-dot { background:#ff3366; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

/* 分页 */
.pagination-footer { margin-top:16px; display:flex; justify-content:flex-end; }
:deep(.el-pagination){color:#a0aec0}
:deep(.el-pagination .el-pager li:not(.is-active)){background:rgba(255,255,255,.06);color:#a0aec0;border-radius:4px}
:deep(.el-pagination .el-pager li.is-active){background:#3aa3ff;color:#fff;border-radius:4px}
:deep(.el-pagination .btn-prev),:deep(.el-pagination .btn-next){background:rgba(255,255,255,.06);color:#a0aec0;border-radius:4px}

/* ---- 图表 ---- */
.chart-col { display:flex; flex-direction:column; gap:20px; }
.chart-panel { flex:1; display:flex; flex-direction:column; }
.chart-box { flex:1; min-height:200px; }

/* ---- 弹窗暗色 ---- */
:deep(.el-dialog){background:rgba(8,30,55,.95);border:1px solid rgba(58,163,255,.2);color:#e0e6ed}
:deep(.el-dialog__title){color:#e0e6ed}
:deep(.el-dialog__headerbtn .el-dialog__close){color:#a0aec0}

/* Tag 颜色 */
:deep(.el-tag--dark) { border:none; }
</style>
