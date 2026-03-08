<template>
  <div class="task-management">
    <el-row :gutter="20" class="full-height">
      <!-- 左侧任务列表 -->
      <el-col :span="12" class="full-height">
        <el-card shadow="never" class="table-card">
          <template #header>
            <div class="card-header">
              <span class="title">任务管理</span>
            </div>
          </template>

          <el-table 
            :data="tasks" 
            style="width: 100%" 
            :stripe="false"
            min-height="600"
            border
            :table-layout="'auto'" 
          >
            <el-table-column prop="index" label="任务编号" width="100" align="center" />
            <el-table-column prop="taskName" label="任务名称" align="center" />
            <el-table-column prop="dueDate" label="执行日期" align="center" />
            <el-table-column prop="status" label="任务状态" align="center" />
          </el-table>
          <!-- 分页 -->
          <div class="pagination-footer">
            <el-pagination
              background
              v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[5, 10, 20, 50]"
                layout="total, sizes, prev, pager, next, jumper"
                :total="total"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧任务状态统计图表 -->
      <el-col :span="12" class="full-height">
        <el-card class="box-card full-height">
          <template #header>
            <div class="card-header">
              <span class="title">任务状态统计图表</span>
            </div>
          </template>
          <div class="chart-container">
            <div id="taskChart"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const tasks = ref([])  // 任务数据
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)


// 模拟任务数据
const mockTasks = [
  { taskName: '任务1', dueDate: '2023-07-01', status: '完成', index: 1 },
  { taskName: '任务2', dueDate: '2023-07-10', status: '进行中', index: 2 },
  { taskName: '任务3', dueDate: '2023-07-15', status: '未开始', index: 3 },
  { taskName: '任务4', dueDate: '2023-07-20', status: '完成', index: 4 },
  { taskName: '任务5', dueDate: '2023-07-25', status: '进行中', index: 5 },
  { taskName: '任务6', dueDate: '2023-07-20', status: '完成', index: 6 },
  { taskName: '任务7', dueDate: '2023-07-25', status: '进行中', index: 7 }
]

// 模拟分页操作
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchTasks()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchTasks()
}

const fetchTasks = () => {
  // 模拟分页数据
  const paginatedTasks = mockTasks.slice(
    (currentPage.value - 1) * pageSize.value,
    currentPage.value * pageSize.value
  )
  tasks.value = paginatedTasks
  total.value = mockTasks.length
  updateChart(tasks.value)  // 更新图表
}

onMounted(() => {
  fetchTasks()  // 页面初始化时获取任务数据
})

// 图表实例
const chart = ref(null)

// 更新图表
const updateChart = (tasks) => {
  if (!chart.value) {
    chart.value = echarts.init(document.getElementById('taskChart'))
  }

  const taskStatusData = tasks.reduce((acc, task) => {
    if (!acc[task.status]) acc[task.status] = 0
    acc[task.status]++
    return acc
  }, {})

  const taskStatus = Object.keys(taskStatusData)
  const taskCounts = Object.values(taskStatusData)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      top: '10%',
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: taskStatus,
      axisLabel: {
        interval: 0,
        rotate: 30,
        color: '#fff'
      }
    },
    yAxis: {
      type: 'value',
      name: '任务数量',
      axisLabel: {
        color: '#fff', // 设置 Y 轴文本为白色
      }
    },
    series: [{
      name: '任务数量',
      data: taskCounts,
      type: 'bar',
      showBackground: true,
      backgroundStyle: {
        color: 'rgba(180, 180, 180, 0.2)'
      },
      itemStyle: {
        color: '#409EFF'
      },
      label: {
        show: true,
        position: 'top',
        color: '#fff'
      }
    }]
  }

  chart.value.setOption(option)
}

// 处理图表窗口大小改变
const handleResize = () => {
  if (chart.value) {
    chart.value.resize()
  }
}

onUnmounted(() => {
  if (chart.value) {
    chart.value.dispose()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.task-management {
  height: 100%;
  padding: 10px;
  box-sizing: border-box;
  width: 100%;
  position: relative;
  background-color: rgba(9, 35, 60, 0.78); /* 设置深蓝色背景 */
}

.full-height {
  height: 100%;
}

.el-row {
  margin: 0 !important;
  height: 100%;
  width: 100%;
}

.el-col {
  padding: 0 5px !important;
  height: 100%;
}

.table-card {
  border-radius: 8px;
  background-color: rgba(9, 35, 60, 0.78);  /* 更新卡片背景色 */
  border: 1px solid rgba(58, 163, 255, 0.15);
  backdrop-filter: blur(8px);
  margin-bottom: 20px;
  height: 100%;
}

/* 卡片头部排版 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-weight: 500;
  font-size: 16px;
  color: #e0e6ed;
  border-left: 4px solid #3aa3ff;
  padding-left: 10px;  /* 标题文本颜色 */
}

/* 表格行背景和文本颜色 */
:deep(.el-table) {
  background-color: transparent;
  --el-table-border-color: rgba(58, 163, 255, 0.1);
  --el-table-header-bg-color: rgba(58, 163, 255, 0.05);
  --el-table-tr-bg-color: transparent;
  --el-table-row-hover-bg-color: rgba(58, 163, 255, 0.1);
  color: #c0ccda;
}

:deep(.el-table th.el-table__cell) {
  color: #3aa3ff;
  font-weight: 600;
  border-bottom: 1px solid rgba(58, 163, 255, 0.2);
}

:deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid rgba(58, 163, 255, 0.1);
}

/* 分页器样式 */
:deep(.el-pagination) {
  background-color: rgba(9, 35, 60, 0.78);  /* 设置深色背景，符合整体风格 */
  color: #e0e6ed;  /* 设置字体颜色为浅色 */
  border-radius: 8px;  /* 圆角 */
  padding: 6px 10px;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 非选中分页按钮 */
:deep(.el-pagination .el-pager li:not(.is-active)) {
  background-color: rgba(255, 255, 255, 0.1);  /* 设置未选中时的按钮背景色 */
  color: #a0aec0;  /* 设置未选中时的文本颜色 */
  border-radius: 6px;
  border: 1px solid rgba(58, 163, 255, 0.1);  /* 设置边框颜色 */
  margin: 0 2px;  /* 缩小按钮之间的间距 */
  padding: 5px 10px;  /* 设置按钮的内边距 */
}

/* 选中分页按钮 */
:deep(.el-pagination .el-pager li.is-active) {
  background-color: #3aa3ff;  /* 设置选中按钮的背景色 */
  color: #fff;  /* 设置选中时的字体颜色 */
  border: 1px solid #3aa3ff;  /* 设置选中时的边框颜色 */
  border-radius: 6px;
  margin: 0 2px;  /* 缩小按钮之间的间距 */
  padding: 5px 10px;  /* 设置按钮的内边距 */
}

/* 上一页按钮样式 */
:deep(.el-pagination .btn-prev) {
  background-color: rgba(9, 35, 60, 0.78);  /* 设置上一页、下一页按钮的背景色 */
  color: #a0aec0;  /* 设置按钮文本颜色 */
  border-radius: 6px;
  border: 1px solid rgba(58, 163, 255, 0.1);  /* 设置边框 */
  padding: 5px 10px;  /* 设置按钮的内边距 */
}

/* 下一页按钮样式 */
:deep(.el-pagination .btn-next) {
  background-color: rgba(9, 35, 60, 0.78);  /* 设置上一页、下一页按钮的背景色 */
  color: #a0aec0;  /* 设置按钮文本颜色 */
  border-radius: 6px;
  border: 1px solid rgba(58, 163, 255, 0.1);  /* 设置边框 */
  padding: 5px 10px;  /* 设置按钮的内边距 */
}

/* 上一页按钮 hover 效果 */
:deep(.el-pagination .btn-prev:hover) {
  background-color: rgba(58, 163, 255, 0.2);  /* 鼠标悬停时的按钮背景色 */
  color: #3aa3ff;  /* 鼠标悬停时的字体颜色 */
}

/* 下一页按钮 hover 效果 */
:deep(.el-pagination .btn-next:hover) {
  background-color: rgba(58, 163, 255, 0.2);  /* 鼠标悬停时的按钮背景色 */
  color: #3aa3ff;  /* 鼠标悬停时的字体颜色 */
}

/* 分页按钮 hover 效果 */
:deep(.el-pagination .el-pager li:hover) {
  background-color: rgba(58, 163, 255, 0.2);  /* 鼠标悬停时的按钮背景色 */
  color: #3aa3ff;  /* 鼠标悬停时的字体颜色 */
}

/* 分页器底部的上一页、下一页文字 */
:deep(.el-pagination .el-pager .btn-prev, .el-pagination .el-pager .btn-next) {
  color: #3aa3ff;  /* 设置文字颜色为蓝色 */
}

.pagination-footer {
  margin-top: 10px;  /* 为分页器添加上边距，调整与表格的距离 */
  text-align: right;
}

/* 统计图表 */
.box-card {
  display: flex;
  flex-direction: column;
  height: 100%; /* 设置卡片高度为100% */
  margin: 0;
  background-color: rgba(9, 35, 60, 0.78); /* 深蓝色背景 */
  border: 1px solid rgba(58, 163, 255, 0.15); /* 边框颜色 */
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden; /* 确保内容不溢出 */
}

.chart-container {
  flex: 1;
  height: calc(100% - 20px); /* 设置图表容器的高度为100% */
  min-height: 500px;
  position: relative;
}

#taskChart {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}

</style>