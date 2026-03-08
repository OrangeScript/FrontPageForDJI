<template>
  <div class="uav-dashboard-container">
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="never" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>历史总里程</span>
              <el-icon><Position /></el-icon>
            </div>
          </template>
          <div class="stat-body">
            <el-statistic :value="totalMileage" :precision="2">
              <template #suffix>
                <span class="unit-label">公里 (km)</span>
              </template>
            </el-statistic>
            <div ref="mileageChartRef" class="trend-chart-container"></div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="never" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>累计在空飞行时长</span>
              <el-icon><Timer /></el-icon>
            </div>
          </template>
          <div class="stat-body">
            <el-statistic :value="totalDuration">
              <template #suffix>
                <span class="unit-label">小时 (hrs)</span>
              </template>
            </el-statistic>
            <div ref="durationChartRef" class="trend-chart-container"></div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="never" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>已完成起降总次数</span>
              <el-icon><Promotion /></el-icon>
            </div>
          </template>
          <div class="stat-body">
            <el-statistic :value="totalFlights" />
            <div ref="flightsChartRef" class="trend-chart-container"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="table-card">
        <template #header>
            <div class="table-header">
            <span class="table-title">单次飞行遥测日志明细</span>
            </div>
        </template>
      
        <el-table 
            :data="flightRecords" 
            style="width: 100%" 
            :stripe="false"
            max-height="600"
            border
            :table-layout="'auto'" 
            >
            <el-table-column prop="id" label="飞行任务编号" width="120" align="center"/>
            <el-table-column prop="datetime" label="起飞时间 (UTC)" align="center"/>
            <el-table-column prop="operator" label="责任操作员" align="center"/>
            <el-table-column prop="duration" label="飞行时长 (分钟)" align="center" />
            <el-table-column prop="mileage" label="单次里程 (公里)" align="center" />
            <el-table-column prop="maxAltitude" label="最高海拔 (米)" align="center" />
        </el-table>

      <div class="pagination-footer">
        <el-pagination
          background
          layout="total, prev, pager, next, jumper"
          :total="88"
          :page-size="10"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { Position, Timer, Promotion } from '@element-plus/icons-vue'

// 静态数据
const totalMileage = 15000.25 // 历史总里程
const totalDuration = 320.5 // 累计飞行时长
const totalFlights = 120 // 已完成起降总次数

// 假设的飞行记录数据
const flightRecords = ref([
  { id: 'F001', datetime: '2023-07-01 10:00:00', operator: '操作员A', duration: 120, mileage: 200, maxAltitude: 1500 },
  { id: 'F002', datetime: '2023-07-01 11:00:00', operator: '操作员B', duration: 90, mileage: 180, maxAltitude: 1300 },
  { id: 'F003', datetime: '2023-07-01 12:00:00', operator: '操作员C', duration: 150, mileage: 250, maxAltitude: 1600 },
  // 添加更多静态数据
]);

// 分页数据
const totalItems = 88; // 总条数（假设的静态数据）
const pageSize = 10; // 每页显示数量
const currentPage = ref(1); // 当前页码

// 分页更新处理函数（用于替换为后端接口）
const handlePageChange = (page: number) => {
  currentPage.value = page;
  // 这里可以用后端接口替换，例如获取该页的数据：
  // fetchData(page);
};

// 后端数据接口示例（待替换）
const fetchData = (page: number) => {
  // 调用后端API获取数据
  // const response = await fetch(`/api/flightRecords?page=${page}&size=${pageSize}`);
  // flightRecords.value = response.data.records; // 假设返回的数据结构
};

onMounted(() => {
  // 你可以在这里初始化图表等内容，例如：
  // const chart = echarts.init(document.getElementById('mileageChartRef') as HTMLDivElement);
  // chart.setOption({
  //   // 初始化图表的数据和配置
  // });
});
</script>

<style scoped>
/* 全局背景风格 */
.uav-dashboard-container {
  padding: 24px;
  background-color: rgba(9, 35, 60, 0.78); /* 更新背景色为深蓝色 */
  min-height: 100vh;
  color: #e0e6ed;
}

/* 统计卡片和表格卡片样式 */
.stat-card, .table-card {
  border-radius: 8px;
  background-color: rgba(9, 35, 60, 0.78);  /* 更新卡片背景色 */
  border: 1px solid rgba(58, 163, 255, 0.15);
  backdrop-filter: blur(8px);
  margin-bottom: 20px;
}

/* 卡片标题 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
  font-size: 15px;
  color: #a0aec0;
}

.card-header.el-icon {
  font-size: 20px;
  color: #3aa3ff;
}

/* 内容统计数值样式 */
:deep(.el-statistic__content) {
  font-size: 34px !important;
  font-weight: 700;
  color: #3aa3ff;
  text-shadow: 0 0 10px rgba(58, 163, 255, 0.3);
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

.unit-label {
  font-size: 13px;
  color: #718096;
  margin-left: 6px;
  font-weight: 400;
}

/* 表格样式 */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-title {
  font-weight: 500;
  font-size: 16px;
  color: #e0e6ed;
  border-left: 4px solid #3aa3ff;
  padding-left: 10px;
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
  margin-top: 40px;  /* 为分页器添加上边距，调整与表格的距离 */
}
</style>