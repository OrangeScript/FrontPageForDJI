<template>
  <div class="task-management">
    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="card-header">
          <span class="title">任务管理</span>
        </div>
      </template>

      <!-- 表格显示任务数据 -->
      <el-table :data="paginatedTasks" style="width: 100%" :stripe="false" min-height="600" border :table-layout="'auto'">
        <el-table-column prop="index" label="任务编号" width="100" align="center" />
        <el-table-column prop="taskName" label="任务名称" align="center" />
        <el-table-column prop="siteName" label="站点名称" align="center" />
        <el-table-column prop="status" label="任务状态" align="center" />
        <el-table-column prop="startTime" label="开始时间" align="center" />
        <el-table-column prop="endTime" label="结束时间" align="center" />
        <el-table-column label="操作" width="180" align="center">
          <template #default="{ row }">
            <div class="button-container">
              <!-- 确保点击时传递正确的行数据 -->
              <el-button size="mini" @click="showDetails(row)" class="custom-detail-button">👁️‍🗨️ 详情</el-button>
              <el-button size="mini" type="danger" class="custom-delete-button">🗑️ 删除</el-button>
            </div>
          </template>
        </el-table-column>
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

    <!-- 详情抽屉 -->
    <el-drawer
      v-model="dialogVisible"
      title="任务详情"
      size="45%"  
      direction="rtl"  
      :before-close="handleClose"
    >
      <div class="task-details">
        <div class="task-detail-row">
          <div class="task-detail-item task-label-container">
            <span class="task-label">任务编号:</span>
          </div>
          <div class="task-detail-item task-value-container">
            <span class="task-value">{{ selectedTask.index }}</span>
          </div>

          <div class="task-detail-item task-label-container">
            <span class="task-label">任务名称:</span>
          </div>
          <div class="task-detail-item task-value-container">
            <span class="task-value">{{ selectedTask.taskName }}</span>
          </div>
        </div>

        <div class="task-detail-row">
          <div class="task-detail-item task-label-container">
            <span class="task-label">站点名称:</span>
          </div>
          <div class="task-detail-item task-value-container">
            <span class="task-value">{{ selectedTask.siteName }}</span>
          </div>
        
          <div class="task-detail-item task-label-container">
            <span class="task-label">任务状态:</span>
          </div>
          <div class="task-detail-item task-value-container">
            <span class="task-value">{{ selectedTask.status }}</span>
          </div>
        </div>

        <div class="task-detail-row">
          <div class="task-detail-item task-label-container">
            <span class="task-label">开始时间:</span>
          </div>
          <div class="task-detail-item task-value-container">
            <span class="task-value">{{ selectedTask.startTime }}</span>
          </div>
        
          <div class="task-detail-item task-label-container">
            <span class="task-label">结束时间:</span>
          </div>
          <div class="task-detail-item task-value-container">
            <span class="task-value">{{ selectedTask.endTime }}</span>
          </div>
        </div>

        <div class="task-detail-row">
          <div class="task-detail-item task-label-container">
            <span class="task-label">飞行时长 (秒):</span>
          </div>
          <div class="task-detail-item task-value-container">
            <span class="task-value">{{ selectedTask.flightDuration }}</span>
          </div>
        
          <div class="task-detail-item task-label-container">
            <span class="task-label">飞行距离 (米):</span>
          </div>
          <div class="task-detail-item task-value-container">
            <span class="task-value">{{ selectedTask.flightDistance }}</span>
          </div>
        </div>

        <div class="task-detail-row">
          <div class="task-detail-item task-label-container">
            <span class="task-label">完成水平航点数:</span>
          </div>
          <div class="task-detail-item task-value-container">
            <span class="task-value">{{ selectedTask.horizontalWaypoints }}</span>
          </div>
        
          <div class="task-detail-item task-label-container">
            <span class="task-label">完成垂直航点数:</span>
          </div>
          <div class="task-detail-item task-value-container">
            <span class="task-value">{{ selectedTask.verticalWaypoints }}</span>
          </div>
        </div>
      </div>

      <div class="map">
        <img src="@/assets/map.png" alt="map" />
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElIcon } from 'element-plus'
import { Search, Delete } from '@element-plus/icons-vue'

const dialogVisible = ref(false)  // 控制抽屉的显示与隐藏
const selectedTask = ref({})  // 当前选中的任务详情

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 静态任务数据
const tasks = ref([
  { 
    index: 1, 
    taskName: '任务1', 
    siteName: '220kV/GIS开关场', 
    status: '完成', 
    startTime: '2023-03-16 08:00:00', 
    endTime: '2023-03-16 10:00:00',
    flightDuration: 7200, // 飞行时长（秒）
    flightDistance: 5000, // 飞行距离（米）
    horizontalWaypoints: 150, // 完成水平航点数
    verticalWaypoints: 200 // 完成垂直航点数
  },
  { 
    index: 2, 
    taskName: '任务2', 
    siteName: '220kV/GIS开关场', 
    status: '进行中', 
    startTime: '2023-03-16 10:00:00', 
    endTime: '2023-03-16 12:00:00', 
    flightDuration: 7200,
    flightDistance: 6000,
    horizontalWaypoints: 160,
    verticalWaypoints: 210
  },
  { 
    index: 3, 
    taskName: '任务3', 
    siteName: '220kV/GIS开关场', 
    status: '未开始', 
    startTime: '2023-03-16 12:00:00', 
    endTime: '2023-03-16 14:00:00', 
    flightDuration: 5000,
    flightDistance: 4500,
    horizontalWaypoints: 140,
    verticalWaypoints: 190
  },
  { 
    index: 4, 
    taskName: '任务4', 
    siteName: '220kV/GIS开关场', 
    status: '完成', 
    startTime: '2023-03-16 14:00:00', 
    endTime: '2023-03-16 16:00:00',
    flightDuration: 6800,
    flightDistance: 5200,
    horizontalWaypoints: 155,
    verticalWaypoints: 195
  },
  { 
    index: 5, 
    taskName: '任务5', 
    siteName: '220kV/GIS开关场', 
    status: '进行中', 
    startTime: '2023-03-16 16:00:00', 
    endTime: '2023-03-16 18:00:00',
    flightDuration: 6900,
    flightDistance: 5500,
    horizontalWaypoints: 165,
    verticalWaypoints: 200
  },
  { 
    index: 6, 
    taskName: '任务6', 
    siteName: '220kV/GIS开关场', 
    status: '完成', 
    startTime: '2023-03-16 18:00:00', 
    endTime: '2023-03-16 20:00:00',
    flightDuration: 7500,
    flightDistance: 5700,
    horizontalWaypoints: 170,
    verticalWaypoints: 210
  },
  { 
    index: 7, 
    taskName: '任务7', 
    siteName: '220kV/GIS开关场', 
    status: '进行中', 
    startTime: '2023-03-16 20:00:00', 
    endTime: '2023-03-16 22:00:00',
    flightDuration: 7100,
    flightDistance: 4900,
    horizontalWaypoints: 145,
    verticalWaypoints: 185
  }
])

// 计算分页数据
const fetchTasks = () => {
  const paginatedTasks = tasks.value.slice(
    (currentPage.value - 1) * pageSize.value,
    currentPage.value * pageSize.value
  )
  total.value = tasks.value.length
  return paginatedTasks
}

// 更新表格数据
const paginatedTasks = ref(fetchTasks())

// 模拟分页操作
const handleSizeChange = (val) => {
  pageSize.value = val
  paginatedTasks.value = fetchTasks()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  paginatedTasks.value = fetchTasks()
}

// 展示任务详情
const showDetails = (task) => {
  selectedTask.value = { 
    index: task.index,
    taskName: task.taskName,
    siteName: task.siteName,
    status: task.status,
    startTime: task.startTime,
    endTime: task.endTime,
    flightDuration: task.flightDuration, // 飞行时长
    flightDistance: task.flightDistance, // 飞行距离
    horizontalWaypoints: task.horizontalWaypoints, // 完成水平航点数
    verticalWaypoints: task.verticalWaypoints // 完成垂直航点数
  }
  dialogVisible.value = true  // 显示抽屉
}

// 关闭抽屉
const handleClose = () => {
  dialogVisible.value = false
}

onMounted(() => {
  fetchTasks()  // 页面初始化时获取任务数据
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

.pagination-footer {
  margin-top: 10px;  /* 为分页器添加上边距，调整与表格的距离 */
  text-align: right;
}

/* 按钮样式 */
.button-container {
  display: flex; /* 使用flex布局 */
  gap: 10px; /* 设置按钮间距 */
  justify-content: flex-start; /* 可选：使按钮靠左 */
  align-items: center; /* 可选：使按钮垂直居中 */
}

.button-container {
  display: flex; /* 使用flex布局 */
  gap: 10px; /* 设置按钮间距 */
  justify-content: center; /* 可选，居中对齐按钮 */
  align-items: center; /* 可选，垂直居中对齐 */
}

.custom-detail-button {
  background-color: #3aa3ff; /* 设置背景色 */
  color: white; /* 设置文本颜色 */
  border-radius: 12px; /* 设置圆角 */
  padding: 6px 12px; /* 内边距 */
  font-weight: bold; /* 加粗文本 */
  box-shadow: 0 4px 8px rgba(0, 150, 255, 0.2); /* 添加阴影 */
  transition: all 0.3s ease; /* 添加过渡效果 */
}

.custom-detail-button:hover {
  background-color: #1e8fd8; /* 悬浮时改变背景色 */
  box-shadow: 0 6px 12px rgba(0, 150, 255, 0.3); /* 增加阴影效果 */
}

.custom-delete-button {
  background-color: #f44336; /* 删除按钮背景色 */
  color: white; /* 文本颜色 */
  border-radius: 12px; /* 圆角 */
  padding: 6px 12px; /* 内边距 */
  font-weight: bold; /* 加粗文本 */
  box-shadow: 0 4px 8px rgba(244, 67, 54, 0.2); /* 阴影效果 */
  transition: all 0.3s ease; /* 过渡效果 */
}

.custom-delete-button:hover {
  background-color: #d32f2f; /* 悬浮时改变背景色 */
  box-shadow: 0 6px 12px rgba(244, 67, 54, 0.3); /* 增加阴影效果 */
}

/* 抽屉样式 */
:deep(.el-drawer) {
  background-color: rgba(9, 35, 60, 0.85);  /* 深蓝色背景 */
  color: #fff;  /* 白色文字 */
  border-radius: 10px;  /* 圆角 */
  border: 1px solid rgba(58, 163, 255, 0.2);  /* 边框 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);  /* 阴影效果 */
  overflow-y: auto;
}

/* 抽屉标题样式 */
:deep(.el-drawer__header) {
  font-size: 18px;
  color: #e0e6ed;
  font-weight: bold;
  padding-left: 10px;
  border-left: 4px solid #3aa3ff;  /* 蓝色边框 */
  margin-left: 18px;
  margin-top: 10px;
  background-color: transparent;
}

.task-details {
  color: #c0ccda;
}

/* 每两个字段放在一个行容器里 */
.task-detail-row {
  display: flex;
  justify-content: space-between; /* 两个字段一行 */
}

/* 标签容器样式 */
.task-label-container {
  display: flex;
  flex-direction: column;  /* 标签和数据上下排列 */
  width: 45%;  /* 控制宽度 */
  background-color: rgba(58, 163, 255, 0.1);  /* 浅蓝色背景 */
  padding: 5px;  /* 内边距 */
  border: 1px solid rgba(255, 255, 255, 0.1); 
  height: 40px;
  justify-content: center;
  text-align: right;
}

/* 数据容器样式 */
.task-value-container {
  display: flex;
  flex-direction: column;
  width: 50%;
  /* background-color: rgba(255, 255, 255, 0.1);   */
  padding: 5px;
  border: 1px solid rgba(255, 255, 255, 0.1); 
  height: 40px;
  justify-content: center;
}

/* 标签样式 */
.task-label {
  font-weight: bold;
  color: #3aa3ff;
  margin-bottom: 5px;  /* 标签和数据之间的间距 */
}

/* 数据样式 */
.task-value {
  color: #e0e6ed;
  word-break: break-word;
}

.map {
  display: flex;  /* 使用 flex 布局 */
  justify-content: center;  /* 水平居中对齐 */
  align-items: center;  /* 垂直居中对齐 */
  margin-top: 30px;  /* 上边距，可以根据需要调整 */
}

.map img {
  max-width: 100%;  /* 图像最大宽度为容器的 100% */
  max-height: 400px;  /* 限制图像的最大高度，避免过大 */
  object-fit: contain;  /* 保持图像比例并适应容器 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);  /* 添加轻微阴影效果 */
}

</style>