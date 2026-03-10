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
          <el-table-column label="操作" width="90" align="center">
            <template #default="{ row }">
              <el-button size="small" class="detail-btn" @click="openDetail(row)">👁️‍🗨️详情</el-button>
            </template>
          </el-table-column>
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

    <!-- 任务详情弹窗 -->
    <el-dialog v-model="showDetail" :title="'任务详情 · ' + (detailData?.id || '')" width="880" class="detail-dialog" :append-to-body="true" destroy-on-close>
      <div class="detail-content" v-if="detailData">
        <!-- 左侧：数据信息 -->
        <div class="detail-left">
          <div class="detail-section">
            <div class="section-title"><span class="accent-bar"></span>基本信息</div>
            <div class="info-grid">
              <div class="info-cell" v-for="f in detailFields" :key="f.label">
                <span class="info-label">{{ f.label }}</span>
                <span class="info-value" :class="f.cls || ''">{{ f.value }}</span>
              </div>
            </div>
          </div>
          <!-- 航点完成度雷达图 -->
          <div class="detail-section">
            <div class="section-title"><span class="accent-bar"></span>航点执行分析</div>
            <div ref="detailRadarRef" class="detail-chart"></div>
          </div>
        </div>
        <!-- 右侧：地图+进度环 -->
        <div class="detail-right">
          <div class="detail-section">
            <div class="section-title"><span class="accent-bar"></span>飞行轨迹地图</div>
            <div class="map-wrapper">
              <img src="@/assets/map.png" alt="flight map" class="map-img" />
              <div class="map-overlay"></div>
              <div class="map-ping"></div>
            </div>
          </div>
          <div class="detail-section">
            <div class="section-title"><span class="accent-bar"></span>执行进度</div>
            <div class="progress-row">
              <div class="progress-ring">
                <el-progress type="circle" :percentage="detailData.progressH" :width="90" :stroke-width="6" color="#00d4ff" :format="()=>detailData.progressH+'%'" />
                <span class="ring-label">水平航点</span>
              </div>
              <div class="progress-ring">
                <el-progress type="circle" :percentage="detailData.progressV" :width="90" :stroke-width="6" color="#00ff88" :format="()=>detailData.progressV+'%'" />
                <span class="ring-label">垂直航点</span>
              </div>
              <div class="progress-ring">
                <el-progress type="circle" :percentage="Math.round(detailData.flightDuration/detailData.estDuration*100)" :width="90" :stroke-width="6" color="#f59e0b" :format="()=>Math.round(detailData.flightDuration/detailData.estDuration*100)+'%'" />
                <span class="ring-label">时间利用率</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

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
  { id:'TSK-001', name:'220kV 继电保护室设备巡检',   type:'巡检', priority:'高',  status:'已完成', operator:'张伟',  date:'2026-03-01', drone:'Mavic 3', station:'220kV 继电保护室',       startTime:'2026-03-01 08:00:00', endTime:'2026-03-01 10:00:00', flightDuration:7200,  flightDistance:5000,  hWaypoints:150, vWaypoints:200, progressH:100, progressV:100, estDuration:7200 },
  { id:'TSK-002', name:'继电保护设备测绘',      type:'测绘', priority:'中',  status:'已完成', operator:'李明',  date:'2026-03-02', drone:'Mavic 3', station:'继电保护室',    startTime:'2026-03-02 09:30:00', endTime:'2026-03-02 11:15:00', flightDuration:6300,  flightDistance:4200,  hWaypoints:120, vWaypoints:80,  progressH:100, progressV:100, estDuration:7000 },
  { id:'TSK-003', name:'配电室继电保护巡检',      type:'巡检', priority:'紧急',status:'执行中', operator:'王强',  date:'2026-03-03', drone:'Mavic 3',      station:'配电室继电保护中心',  startTime:'2026-03-03 06:00:00', endTime:'—',                    flightDuration:3600,  flightDistance:8200,  hWaypoints:200, vWaypoints:50,  progressH:65,  progressV:40,  estDuration:7200 },
  { id:'TSK-004', name:'继电保护室电力设施巡检',      type:'巡检', priority:'低',  status:'待执行', operator:'赵敏',  date:'2026-03-04', drone:'Mavic 3', station:'继电保护室电力设施',      startTime:'—',                   endTime:'—',                    flightDuration:0,     flightDistance:0,     hWaypoints:180, vWaypoints:120, progressH:0,   progressV:0,   estDuration:5400 },
  { id:'TSK-005', name:'电力监控室设备测绘',  type:'测绘', priority:'中',  status:'已完成', operator:'刘芳',  date:'2026-03-04', drone:'Mavic 3',  station:'电力监控室',      startTime:'2026-03-04 14:00:00', endTime:'2026-03-04 15:20:00', flightDuration:4800,  flightDistance:3100,  hWaypoints:90,  vWaypoints:60,  progressH:100, progressV:100, estDuration:5400 },
  { id:'TSK-006', name:'电力继电室设备巡检',    type:'巡检', priority:'高',  status:'执行中', operator:'陈浩',  date:'2026-03-05', drone:'Mavic 3',      station:'电力继电室',     startTime:'2026-03-05 07:00:00', endTime:'—',                    flightDuration:5400,  flightDistance:6800,  hWaypoints:220, vWaypoints:100, progressH:78,  progressV:55,  estDuration:7200 },
  { id:'TSK-007', name:'继电保护室监控设备巡检',      type:'搜救', priority:'紧急',status:'已完成', operator:'杨涛',  date:'2026-03-05', drone:'Mavic 3', station:'继电保护监控室',        startTime:'2026-03-05 05:30:00', endTime:'2026-03-05 08:00:00', flightDuration:9000,  flightDistance:12000, hWaypoints:300, vWaypoints:150, progressH:100, progressV:100, estDuration:9000 },
  { id:'TSK-008', name:'继电保护指挥室侦察',  type:'侦察', priority:'紧急',status:'已完成', operator:'周洁',  date:'2026-03-06', drone:'Mavic 3',      station:'继电保护指挥室',    startTime:'2026-03-06 16:45:00', endTime:'2026-03-06 17:30:00', flightDuration:2700,  flightDistance:3500,  hWaypoints:80,  vWaypoints:40,  progressH:100, progressV:100, estDuration:3600 },
  { id:'TSK-009', name:'继电保护设备 NDVI 测绘',    type:'测绘', priority:'低',  status:'待执行', operator:'吴磊',  date:'2026-03-07', drone:'Mavic 3', station:'继电保护设施监控室',    startTime:'—',                   endTime:'—',                    flightDuration:0,     flightDistance:0,     hWaypoints:250, vWaypoints:60,  progressH:0,   progressV:0,   estDuration:10800 },
  { id:'TSK-010', name:'继电保护控制中心巡检',      type:'巡检', priority:'高',  status:'执行中', operator:'孙丽',  date:'2026-03-07', drone:'Mavic 3', station:'继电保护控制室A区',   startTime:'2026-03-07 10:00:00', endTime:'—',                    flightDuration:4200,  flightDistance:5500,  hWaypoints:170, vWaypoints:90,  progressH:82,  progressV:60,  estDuration:7200 },
  { id:'TSK-011', name:'继电保护监控巡检',      type:'巡检', priority:'高',  status:'已完成', operator:'张伟',  date:'2026-03-08', drone:'Mavic 3', station:'继电保护监控室',        startTime:'2026-03-08 07:00:00', endTime:'2026-03-08 09:30:00', flightDuration:9000,  flightDistance:7200,  hWaypoints:200, vWaypoints:180, progressH:100, progressV:100, estDuration:9000 },
  { id:'TSK-012', name:'继电保护室测绘',  type:'测绘', priority:'中',  status:'已取消', operator:'李明',  date:'2026-03-08', drone:'Mavic 3',  station:'继电保护通信室',    startTime:'—',                   endTime:'—',                    flightDuration:0,     flightDistance:0,     hWaypoints:160, vWaypoints:40,  progressH:0,   progressV:0,   estDuration:5400 },
  { id:'TSK-013', name:'继电保护设备夜间巡检',      type:'巡检', priority:'紧急',status:'执行中', operator:'王强',  date:'2026-03-09', drone:'Mavic 3',      station:'继电保护设施控制室',  startTime:'2026-03-09 22:00:00', endTime:'—',                    flightDuration:2700,  flightDistance:4100,  hWaypoints:130, vWaypoints:70,  progressH:45,  progressV:30,  estDuration:7200 },
  { id:'TSK-014', name:'继电保护灾区监控指挥室巡检',      type:'搜救', priority:'紧急',status:'待执行', operator:'杨涛',  date:'2026-03-10', drone:'Mavic 3', station:'继电保护灾区指挥室',        startTime:'—',                   endTime:'—',                    flightDuration:0,     flightDistance:0,     hWaypoints:400, vWaypoints:200, progressH:0,   progressV:0,   estDuration:14400 },
  { id:'TSK-015', name:'继电保护监控室巡检',    type:'巡检', priority:'中',  status:'待执行', operator:'陈浩',  date:'2026-03-10', drone:'Mavic 3', station:'继电保护监控室 B 区',       startTime:'—',                   endTime:'—',                    flightDuration:0,     flightDistance:0,     hWaypoints:100, vWaypoints:300, progressH:0,   progressV:0,   estDuration:10800 },
  { id:'TSK-016', name:'继电保护指挥中心侦察',    type:'侦察', priority:'高',  status:'待执行', operator:'周洁',  date:'2026-03-11', drone:'Mavic 3',      station:'继电保护指挥室 A-7',          startTime:'—',                   endTime:'—',                    flightDuration:0,     flightDistance:0,     hWaypoints:350, vWaypoints:50,  progressH:0,   progressV:0,   estDuration:10800 },
  { id:'TSK-017', name:'继电保护控制室巡检',      type:'巡检', priority:'低',  status:'已取消', operator:'刘芳',  date:'2026-03-11', drone:'Mavic 3',  station:'继电保护室',          startTime:'—',                   endTime:'—',                    flightDuration:0,     flightDistance:0,     hWaypoints:60,  vWaypoints:400, progressH:0,   progressV:0,   estDuration:7200 },
  { id:'TSK-018', name:'继电监控室测绘',    type:'测绘', priority:'中',  status:'待执行', operator:'吴磊',  date:'2026-03-12', drone:'Mavic 3', station:'继电保护室',    startTime:'—',                   endTime:'—',                    flightDuration:0,     flightDistance:0,     hWaypoints:280, vWaypoints:80,  progressH:0,   progressV:0,   estDuration:10800 },
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

/* ============ 任务详情 ============ */
const showDetail = ref(false)
const detailData = ref(null)
const detailRadarRef = ref(null)
let detailRadarChart = null

const detailFields = computed(() => {
  const d = detailData.value
  if (!d) return []
  return [
    { label:'任务编号',            value: d.id },
    { label:'任务名称',            value: d.name },
    { label:'站点名称',            value: d.station },
    { label:'任务状态',            value: d.status, cls: statusClass(d.status) },
    { label:'执行机型',            value: d.drone },
    { label:'责任操作员',          value: d.operator },
    { label:'开始时间',            value: d.startTime },
    { label:'结束时间',            value: d.endTime },
    { label:'飞行时长 (秒)',       value: d.flightDuration.toLocaleString() },
    { label:'飞行距离 (米)',       value: d.flightDistance.toLocaleString() },
    { label:'完成水平航点数',      value: d.hWaypoints },
    { label:'完成垂直航点数',      value: d.vWaypoints },
  ]
})

const openDetail = async (row) => {
  detailData.value = row
  showDetail.value = true
  await nextTick()
  // 渲染详情雷达图
  if (detailRadarRef.value) {
    if (detailRadarChart) detailRadarChart.dispose()
    detailRadarChart = echarts.init(detailRadarRef.value)
    detailRadarChart.setOption({
      tooltip: { backgroundColor:'rgba(6,22,42,.92)', borderColor:'rgba(58,163,255,.3)', textStyle:{color:'#e0e6ed'} },
      radar: {
        indicator: [
          { name:'水平航点', max: row.hWaypoints || 1 },
          { name:'垂直航点', max: row.vWaypoints || 1 },
          { name:'飞行距离', max: Math.max(row.flightDistance, 1) },
          { name:'飞行时长', max: Math.max(row.estDuration, 1) },
          { name:'任务进度', max: 100 },
        ],
        shape: 'polygon',
        axisName: { color:'#718096', fontSize:11 },
        splitLine: { lineStyle:{ color:'rgba(58,163,255,.1)' } },
        splitArea: { areaStyle:{ color:['rgba(58,163,255,.02)','rgba(58,163,255,.06)'] } },
        axisLine: { lineStyle:{ color:'rgba(58,163,255,.15)' } },
      },
      series: [{
        type: 'radar',
        data: [{
          value: [
            Math.round(row.hWaypoints * row.progressH / 100),
            Math.round(row.vWaypoints * row.progressV / 100),
            row.flightDistance,
            row.flightDuration,
            Math.round((row.progressH + row.progressV) / 2),
          ],
          name: '执行情况',
          lineStyle: { color:'#00d4ff', width:2 },
          areaStyle: { color:'rgba(0,212,255,.2)' },
          itemStyle: { color:'#00d4ff', borderColor:'#061a2c', borderWidth:2 },
        }],
      }],
    })
  }
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

/* ---- 详情按钮：彻底覆盖 el-button 默认白色 ---- */
:deep(.detail-btn.el-button) {
  --el-button-bg-color: transparent !important;
  --el-button-border-color: rgba(0,212,255,.25) !important;
  --el-button-text-color: #00d4ff !important;
  --el-button-hover-bg-color: rgba(0,212,255,.15) !important;
  --el-button-hover-border-color: #00d4ff !important;
  --el-button-hover-text-color: #00d4ff !important;
  --el-button-active-bg-color: rgba(0,212,255,.2) !important;
  --el-button-active-border-color: #00d4ff !important;
  --el-button-active-text-color: #00d4ff !important;
  background: rgba(0,212,255,.08) !important;
  color: #00d4ff !important;
  border: 1px solid rgba(0,212,255,.25) !important;
  font-size:12px; font-weight:600; letter-spacing:.5px; padding:4px 10px; border-radius:4px;
  transition:all .25s;
}
:deep(.detail-btn.el-button:hover),
:deep(.detail-btn.el-button:focus) {
  background: rgba(0,212,255,.18) !important;
  color: #00d4ff !important;
  border-color: #00d4ff !important;
  box-shadow: 0 0 12px rgba(0,212,255,.2);
}

/* ---- 详情弹窗 ---- */
:deep(.detail-dialog .el-dialog) { background:rgba(6,20,38,.96);border:1px solid rgba(58,163,255,.2);border-radius:8px;color:#e0e6ed; }
:deep(.detail-dialog .el-dialog__title) { color:#e0e6ed;font-weight:700;letter-spacing:1px; }
:deep(.detail-dialog .el-dialog__headerbtn .el-dialog__close) { color:#a0aec0; }

.detail-content { display:grid;grid-template-columns:1fr 1fr;gap:24px;min-height:460px; }
.detail-left,.detail-right { display:flex;flex-direction:column;gap:18px; }

.detail-section {
  background:rgba(8,30,55,.7);border:1px solid rgba(58,163,255,.1);border-radius:6px;
  padding:16px 18px;
}
.section-title {
  font-size:13px;font-weight:600;color:#e0e6ed;margin-bottom:14px;
  display:flex;align-items:center;gap:6px;
}

/* 信息网格 */
.info-grid { display:grid;grid-template-columns:1fr 1fr;gap:10px 16px; }
.info-cell { display:flex;flex-direction:column;gap:2px; }
.info-label { font-size:11px;color:#718096;letter-spacing:.5px; }
.info-value { font-size:14px;font-weight:600;color:#e0e6ed;font-family:'Courier New',monospace; }
.info-value.done { color:#00ff88; }
.info-value.running { color:#f59e0b; }
.info-value.pending { color:#00d4ff; }
.info-value.cancelled { color:#ff3366; }

/* 详情雷达图 */
.detail-chart { height:200px; }

/* 地图 */
.map-wrapper {
  position:relative;border-radius:6px;overflow:hidden;border:1px solid rgba(58,163,255,.15);
  background:#000;
}
.map-img { width:100%;display:block;opacity:.85; }
.map-overlay {
  position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(6,26,44,.1) 0%,rgba(6,26,44,.5) 100%);
  pointer-events:none;
}
.map-ping {
  position:absolute;top:42%;left:55%;
  width:14px;height:14px;border-radius:50%;
  background:#ff3366;box-shadow:0 0 12px #ff3366;
  animation:mapPing 1.5s ease-in-out infinite;
}
@keyframes mapPing {
  0%,100%{transform:scale(1);opacity:1}
  50%{transform:scale(1.6);opacity:.4}
}

/* 进度环行 */
.progress-row { display:flex;justify-content:space-around;padding:8px 0; }
.progress-ring { display:flex;flex-direction:column;align-items:center;gap:8px; }
.ring-label { font-size:11px;color:#718096; }
:deep(.el-progress__text) { color:#e0e6ed !important;font-weight:700;font-family:'Courier New',monospace; }
:deep(.el-progress path.el-progress-circle__track) { stroke:rgba(58,163,255,.1); }
</style>

<!-- 全局样式：彻底修复 append-to-body 弹窗白色背景 -->
<style>
/* === 详情弹窗：所有层级 === */
.detail-dialog.el-overlay { background:rgba(0,0,0,.55) !important; }
.detail-dialog .el-overlay-dialog { background:transparent !important; }
.detail-dialog .el-dialog,
.detail-dialog.el-dialog {
  --el-dialog-bg-color: rgba(6,20,38,.98) !important;
  background: rgba(6,20,38,.98) !important;
  border: 1px solid rgba(58,163,255,.25) !important;
  border-radius: 10px !important;
  box-shadow: 0 0 60px rgba(0,100,255,.18), 0 0 120px rgba(0,0,0,.7) !important;
  color: #e0e6ed !important;
}
.detail-dialog .el-dialog__header,
.detail-dialog.el-dialog .el-dialog__header {
  background: rgba(6,20,38,.98) !important;
  border-bottom: 1px solid rgba(58,163,255,.15) !important;
  padding: 16px 20px !important;
  margin-right: 0 !important;
}
.detail-dialog .el-dialog__title,
.detail-dialog.el-dialog .el-dialog__title {
  color: #e0e6ed !important;
  font-weight: 700 !important;
  font-size: 16px !important;
  letter-spacing: 1.5px !important;
}
.detail-dialog .el-dialog__headerbtn .el-dialog__close,
.detail-dialog.el-dialog .el-dialog__headerbtn .el-dialog__close {
  color: #718096 !important;
  font-size: 18px !important;
}
.detail-dialog .el-dialog__headerbtn .el-dialog__close:hover {
  color: #00d4ff !important;
}
.detail-dialog .el-dialog__body,
.detail-dialog.el-dialog .el-dialog__body {
  background: rgba(6,20,38,.98) !important;
  color: #e0e6ed !important;
  padding: 20px !important;
}
/* 详情弹窗内部面板 */
.detail-dialog .detail-content { display:grid;grid-template-columns:1fr 1fr;gap:24px;min-height:460px; }
.detail-dialog .detail-left,
.detail-dialog .detail-right { display:flex;flex-direction:column;gap:18px; }
.detail-dialog .detail-section {
  background:rgba(8,30,55,.8) !important;border:1px solid rgba(58,163,255,.12);border-radius:6px;
  padding:16px 18px;
}
.detail-dialog .section-title {
  font-size:13px;font-weight:600;color:#e0e6ed;margin-bottom:14px;
  display:flex;align-items:center;gap:6px;
}
.detail-dialog .accent-bar { width:4px;height:18px;background:#3aa3ff;border-radius:2px;display:inline-block; }
.detail-dialog .info-grid { display:grid;grid-template-columns:1fr 1fr;gap:10px 16px; }
.detail-dialog .info-cell { display:flex;flex-direction:column;gap:2px; }
.detail-dialog .info-label { font-size:11px;color:#718096;letter-spacing:.5px; }
.detail-dialog .info-value { font-size:14px;font-weight:600;color:#e0e6ed;font-family:'Courier New',monospace; }
.detail-dialog .info-value.done { color:#00ff88; }
.detail-dialog .info-value.running { color:#f59e0b; }
.detail-dialog .info-value.pending { color:#00d4ff; }
.detail-dialog .info-value.cancelled { color:#ff3366; }
.detail-dialog .detail-chart { height:200px; }
.detail-dialog .map-wrapper {
  position:relative;border-radius:6px;overflow:hidden;border:1px solid rgba(58,163,255,.15);background:#000;
}
.detail-dialog .map-img { width:100%;display:block;opacity:.85; }
.detail-dialog .map-overlay {
  position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(6,26,44,.1) 0%,rgba(6,26,44,.5) 100%);
  pointer-events:none;
}
.detail-dialog .map-ping {
  position:absolute;top:42%;left:55%;width:14px;height:14px;border-radius:50%;
  background:#ff3366;box-shadow:0 0 12px #ff3366;
  animation:mapPing 1.5s ease-in-out infinite;
}
.detail-dialog .progress-row { display:flex;justify-content:space-around;padding:8px 0; }
.detail-dialog .progress-ring { display:flex;flex-direction:column;align-items:center;gap:8px; }
.detail-dialog .ring-label { font-size:11px;color:#718096; }
.detail-dialog .el-progress__text { color:#e0e6ed !important;font-weight:700;font-family:'Courier New',monospace; }
.detail-dialog .el-progress path.el-progress-circle__track { stroke:rgba(58,163,255,.1); }
@keyframes mapPing { 0%,100%{transform:scale(1);opacity:1} 50%{transform:scale(1.6);opacity:.4} }

/* === 新建任务弹窗 === */
.add-dialog.el-overlay { background:rgba(0,0,0,.5) !important; }
.add-dialog .el-dialog,
.add-dialog.el-dialog {
  --el-dialog-bg-color: rgba(6,20,38,.97) !important;
  background: rgba(6,20,38,.97) !important;
  border: 1px solid rgba(58,163,255,.2) !important;
  border-radius: 8px !important;
  color: #e0e6ed !important;
}
.add-dialog .el-dialog__header { background:transparent !important;border-bottom:1px solid rgba(58,163,255,.1) !important; }
.add-dialog .el-dialog__title { color:#e0e6ed !important; }
.add-dialog .el-dialog__body { background:transparent !important;color:#e0e6ed !important; }
.add-dialog .el-dialog__footer { background:transparent !important;border-top:1px solid rgba(58,163,255,.1) !important; }
.add-dialog .el-form-item__label { color:#a0aec0 !important; }
.add-dialog .el-input__wrapper { background:rgba(0,40,80,.5) !important;border:1px solid rgba(58,163,255,.2) !important;box-shadow:none !important; }
.add-dialog .el-input__inner { color:#e0e6ed !important; }
.add-dialog .el-select .el-input__wrapper { background:rgba(0,40,80,.5) !important;border:1px solid rgba(58,163,255,.2) !important;box-shadow:none !important; }
</style>
