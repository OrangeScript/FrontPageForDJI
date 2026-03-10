<template>
  <div class="task-management">
    <el-row :gutter="20" class="full-height">
      <!-- 第一个图表: 任务执行次数统计 -->
      <el-col :span="12">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span class="title">任务执行次数</span>
              <div class="time-selector">
                <el-button size="small" :type="selectedDate1 === 'previous' ? 'primary' : 'default'" @click="updateDate1('previous')">
                  前日
                </el-button>
                <el-button size="small" :type="selectedDate1 === 'yesterday' ? 'primary' : 'default'" @click="updateDate1('yesterday')">
                  昨日
                </el-button>
                <el-button size="small" :type="selectedDate1 === 'today' ? 'primary' : 'default'" @click="updateDate1('today')">
                  今日
                </el-button>
              </div>
            </div>
          </template>
          <div class="chart-container">
            <div id="taskExecutionChart"></div>
          </div>
        </el-card>
      </el-col>

      <!-- 第二个图表: 任务执行状态统计 -->
      <el-col :span="12">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span class="title">任务执行状态</span>
              <div class="time-selector">
                <el-button size="small" :type="selectedDate2 === 'previous' ? 'primary' : 'default'" @click="updateDate2('previous')">
                  前日
                </el-button>
                <el-button size="small" :type="selectedDate2 === 'yesterday' ? 'primary' : 'default'" @click="updateDate2('yesterday')">
                  昨日
                </el-button>
                <el-button size="small" :type="selectedDate2 === 'today' ? 'primary' : 'default'" @click="updateDate2('today')">
                  今日
                </el-button>
              </div>
            </div>
          </template>
          <div class="chart-container">
            <div id="taskStatusChart"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- 第四个图表: 任务站点分布统计 -->
      <el-col :span="12">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span class="title">站点分布</span>
              <div class="time-selector">
                <el-button size="small" :type="selectedDate4 === 'yesterday' ? 'primary' : 'default'" @click="updateDate4('yesterday')">
                  上周
                </el-button>
                <el-button size="small" :type="selectedDate4 === 'today' ? 'primary' : 'default'" @click="updateDate4('today')">
                  本周
                </el-button>
              </div>
            </div>
          </template>
          <div class="chart-container">
            <div id="taskSiteDistributionChart"></div>
          </div>
        </el-card>
      </el-col>
      <!-- 第三个图表: 任务执行进度统计 -->
      <el-col :span="12">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span class="title">任务执行进度</span>
              <div class="time-selector">
                <el-button size="small" :type="selectedDate3 === 'yesterday' ? 'primary' : 'default'" @click="updateDate3('yesterday')">
                  上周
                </el-button>
                <el-button size="small" :type="selectedDate3 === 'today' ? 'primary' : 'default'" @click="updateDate3('today')">
                  本周
                </el-button>
              </div>
            </div>
          </template>
          <div class="chart-container">
            <div id="taskProgressChart"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

// 当前选择的时间
const selectedDate1 = ref('today')
const selectedDate2 = ref('today')
const selectedDate3 = ref('today')
const selectedDate4 = ref('today')

// 图表实例
const chartTaskExecution = ref(null)
const chartTaskStatus = ref(null)
const chartTaskProgress = ref(null)
const chartTaskSiteDistribution = ref(null)

// 更新选中的时间
const updateDate1 = (date) => {
  selectedDate1.value = date
  updateTaskExecutionChart() // 每次选择时间后，更新图表
}
const updateDate2 = (date) => {
  selectedDate2.value = date
  updateTaskStatusChart() // 每次选择时间后，更新图表
}
const updateDate3 = (date) => {
  selectedDate3.value = date
  updateTaskProgressChart() // 每次选择时间后，更新图表
}
const updateDate4 = (date) => {
  selectedDate4.value = date
  updateTaskSiteDistributionChart() // 每次选择时间后，更新图表
}


// 更新执行次数图表
const updateCharts = () => {
  updateTaskExecutionChart()
  updateTaskStatusChart()
  updateTaskProgressChart()
  updateTaskSiteDistributionChart()
}

// 任务执行次数统计图
const updateTaskExecutionChart = () => {
  if (!chartTaskExecution.value) {
    chartTaskExecution.value = echarts.init(document.getElementById('taskExecutionChart'))
  }

  const taskExecutionData = {
    previous: [15, 44, 22, 19],
    yesterday: [20, 43, 19, 18],
    today: [45, 12, 27, 16]
  }

  const option = {
    xAxis: {
      type: 'category',
      data: ['任务A', '任务B', '任务C', '任务D'],
      axisLabel: {
        color: '#fff'
      }
    },
    yAxis: {
      type: 'value',
      name: '执行次数',
      nameTextStyle: {
        color: '#fff',  
        fontSize: 12
      },
      axisLabel: {
        color: '#fff'
      }
    },
    series: [{
      data: taskExecutionData[selectedDate1.value],
      type: 'bar',
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

  chartTaskExecution.value.setOption(option)
}

// 任务执行状态统计图
const updateTaskStatusChart = () => {
  if (!chartTaskStatus.value) {
    chartTaskStatus.value = echarts.init(document.getElementById('taskStatusChart'))
  }

  const taskStatusData = {
    previous: { '初始化中': 19, '执行中': 15, '执行失败': 2, '执行完成':  64},
    yesterday: { '初始化中': 6, '执行中': 12, '执行失败': 5, '执行完成': 77 },
    today: { '初始化中': 7, '执行中': 17, '执行失败': 9, '执行完成': 67 }
  }

  const statusColors = {
    '初始化中': '#FF6F61',  // Red
    '执行中': '#FFB547',    // Orange
    '执行失败': '#FF4C4C',   // Dark Red
    '执行完成': '#4CAF50'   // Green
  }

  const option = {
    yAxis: {
      type: 'category',
      data: Object.keys(taskStatusData[selectedDate2.value]),
      axisLabel: {
        color: '#fff'
      }
    },
    xAxis: {
      type: 'value',
      name: '任务数量',
      nameTextStyle: {
        color: '#fff',  
        fontSize: 12
      },
      axisLabel: {
        color: '#fff'
      }
    },
    series: [{
      data: Object.keys(taskStatusData[selectedDate2.value]).map(status => {
        return {
          value: taskStatusData[selectedDate2.value][status],
          itemStyle: {
            color: statusColors[status]  // Assign color based on status
          }
        }
      }),
      type: 'bar',
      label: {
        show: true,
        position: 'right',
        color: '#fff'
      }
    }]
  }

  chartTaskStatus.value.setOption(option)
}

// 任务执行进度统计图
const updateTaskProgressChart = () => {
  if (!chartTaskProgress.value) {
    chartTaskProgress.value = echarts.init(document.getElementById('taskProgressChart'))
  }

  const taskProgressData = {
    yesterday: [78, 90, 68, 82, 92, 75, 88],
    today: [90, 75, 82, 70, 64, 77, 67]
  }

  const option = {
    xAxis: {
      type: 'category',
      data: ['03-02', '03-03', '03-04', '03-05', '03-06', '03-07', '03-08'],
      axisLabel: {
        color: '#fff'
      }
    },
    yAxis: {
      type: 'value',
      name: '任务数量',
      nameTextStyle: {
        color: '#fff',  
        fontSize: 12
      },
      axisLabel: {
        color: '#fff'
      }
    },
    series: [{
      data: taskProgressData[selectedDate3.value],
      type: 'line',
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

  chartTaskProgress.value.setOption(option)
}

// 任务站点分布统计图
const updateTaskSiteDistributionChart = () => {
  if (!chartTaskSiteDistribution.value) {
    chartTaskSiteDistribution.value = echarts.init(document.getElementById('taskSiteDistributionChart'))
  }

  const taskSiteData = {
    yesterday: [{ value: 23, name: '站点A' }, { value: 46, name: '站点B' }, { value: 11, name: '站点C' }, { value: 20, name: '站点D' }],
    today: [{ value: 38, name: '站点A' }, { value: 17, name: '站点B' }, { value: 128, name: '站点C' }, { value: 17, name: '站点D' }]
  }

  const siteColors = {
    '站点A': '#FF6F61',  // Red
    '站点B': '#FFB547',  // Orange
    '站点C': '#4CAF50',  // Green
    '站点D': '#409EFF'   // Blue
  }

  const dataWithColors = taskSiteData[selectedDate4.value].map(site => {
    return {
      value: site.value,
      name: site.name,
      itemStyle: {
        color: siteColors[site.name]  // Assign color based on site name
      }
    }
  })

  const option = {
    series: [{
      type: 'pie',
      radius: '50%',
      data: dataWithColors,  // Use data with assigned colors
      label: {
        color: '#fff'
      }
    }]
  }

  chartTaskSiteDistribution.value.setOption(option)
}

// 初始化图表
onMounted(() => {
  updateCharts()
})

onUnmounted(() => {
  if (chartTaskExecution.value) chartTaskExecution.value.dispose()
  if (chartTaskStatus.value) chartTaskStatus.value.dispose()
  if (chartTaskProgress.value) chartTaskProgress.value.dispose()
  if (chartTaskSiteDistribution.value) chartTaskSiteDistribution.value.dispose()
})
</script>


<style scoped>
.task-management {
  height: 100%;
  padding: 10px;
  box-sizing: border-box;
  width: 100%;
  position: relative;
  background-color: rgba(9, 35, 60, 0.78);
}

.full-height {
  height: 100%;
}

.el-row {
  margin: 0 !important;
  height: 50%;
  width: 100%;
  display: flex;
  flex-wrap: wrap; /* 允许换行 */
}

.el-col {
  flex: 1 0 48%; /* 使每个图表占50%的宽度，添加间隙 */
  height: 100%; /* 每个图表占据一半的高度 */
  padding: 0 !important;
}

.box-card {
  display: flex;
  flex-direction: column;
  height: 100%; /* 设置卡片高度为100% */
  background-color: rgba(9, 35, 60, 0.78); /* 深蓝色背景 */
  border: 1px solid rgba(58, 163, 255, 0.15); /* 边框颜色 */
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden; /* 确保内容不溢出 */
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
  padding-left: 10px;
}

.time-selector {
  display: flex;
  gap: 10px;
}

.time-selector .el-button {
  font-size: 14px;
}

/* 图表 */
.chart-container {
  flex: 1;
  height: calc(100% - 20px); /* 设置图表容器的高度为100% */
  min-height: 300px;
  position: relative;
}

#taskExecutionChart,
#taskStatusChart,
#taskProgressChart,
#taskSiteDistributionChart {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}
</style>