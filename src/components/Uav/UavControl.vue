<template>
  <aside class="panel panel-left">
    <div class="panel-title">
      <span class="dot" />
      <span class="title-text">无人机任务信息</span>
    </div>

    <!-- 1）任务执行 -->
    <el-card class="card card-task" shadow="never">
      <template #header><div class="card-h">手动任务列表</div></template>

      <div class="form-row">
        <div class="label">任务类型</div>
        <el-select v-model="ui.taskType" placeholder="选择任务" size="small" style="width: 100%">
          <el-option label="一键巡检任务" value="巡检" />
          <el-option label="定点拍照任务" value="拍照" />
          <el-option label="定线飞行任务" value="定线" />
        </el-select>
      </div>

      <el-button type="primary" style="width: 100%">执行</el-button>
    </el-card>

    <!-- 2）倒计时 -->
    <el-card class="card card-countdown" shadow="never">
      <template #header><div class="card-h">下次执行倒计时</div></template>

      <div class="countdown">
        <div class="count-label">下一次将于</div>
        <div class="count-time">00:00:00</div>
        <div class="count-sub">后执行</div>
      </div>
    </el-card>

    <!-- 3）站点日志 -->
    <el-card class="card card-log" shadow="never">
      <template #header><div class="card-h">站点日志</div></template>

      <div class="log-box" ref="logBoxRef">
        <!-- 接真实数据，将这里面的logs改为v-for="... in ui.logs"
 -->
        <div
          v-for="(it, idx) in logs"
          :key="it.id ?? idx"
          class="log-item"
        >
          <div class="log-title">【{{ it.tag }}】{{ it.text }}</div>
          <div class="log-time">{{ it.time }}</div>
        </div>
      </div>
    </el-card>

    <div class="panel-footer">
      <span>版本：v2.6</span>
      <span>连接：已连接</span>
    </div>
  </aside>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  ui: {
    type: Object,
    required: true,
    validator: (v) =>
      v &&
      typeof v.taskType === 'string' &&
      typeof v.autoRun === 'boolean',
  },
})

const logBoxRef = ref(null)

// ✅ 静态日志（先看样式）
const logs = ref([
  { id: 1, tag: '任务状态', text: '任务执行中', time: '2023-07-24 15:51:19' },
  { id: 2, tag: '任务状态', text: '巡检任务完成', time: '2023-07-24 15:51:55' },
  { id: 3, tag: '任务状态', text: '起飞成功', time: '2023-07-24 15:51:55' },
  { id: 4, tag: '无人机状态', text: '旋转', time: '2023-07-24 15:52:12' },
  { id: 5, tag: '任务状态', text: '拍照成功', time: '2023-07-24 15:52:19' },
  { id: 6, tag: '无人机状态', text: '旋转', time: '2023-07-24 15:52:43' },
  { id: 7, tag: '任务状态', text: '降落成功', time: '2023-07-24 15:52:48' },
])

// 新日志进来滚到底（静态也能看效果）
watch(
  () => logs.value.length,
  async () => {
    await nextTick()
    const el = logBoxRef.value
    if (!el) return
    el.scrollTop = el.scrollHeight
  },
  { immediate: true }
)
</script>



<style scoped>
.panel {
  background: rgba(9, 35, 60, 0.78);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  padding: 14px;
}

.panel-left{
  height: 100%;
  min-height: 0;         /* ✅ 允许子元素在 flex 中收缩 */
  display: flex;
  flex-direction: column;
  overflow: hidden;      /* 外层不滚 */
}


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

.card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.10);
  box-shadow: inset 0 0 20px rgba(58, 163, 255, 0.10);
  margin-bottom: 10px;
}

/* ✅ 只有前两个卡片固定高度 */
.card-task,
.card-countdown{
  height: 180px;
}


.card-h {
  font-size: 14px;
  color:rgba(158, 208, 255, 0.75);
  opacity: 0.75;
}

.form-row {
  display: grid;
  grid-template-columns: 60px 1fr;
  gap: 10px;
  align-items: center;
  margin-bottom: 20px;
}

.label {
  font-size: 13px;
  color:rgba(255,255,255,0.70);
  opacity: 0.85;
}

.countdown {
  display: grid;
  gap: 6px;
  text-align: center;
  color: rgba(255, 255, 255, 0.92);
}

.count-label,
.count-sub {
  font-size: 14px;
  opacity: 0.8;
}

.count-time {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: 2px;
}

.panel-footer {
  display: flex;
  justify-content: space-between;
  padding: 10px 6px 2px;
  font-size: 12px;
  opacity: 0.75;
}

/* 站点日志 */
.card-log{
  flex: 1;
  min-height: 0;
  display: flex;              /* ✅ 关键 */
  flex-direction: column;     /* ✅ 关键 */
}

/* ✅ header 高度固定，body 吃剩余空间 */
.card-log :deep(.el-card__body){
  flex: 1;                    /* ✅ 关键 */
  min-height: 0;              /* ✅ 关键 */
  padding: 8px 10px;
  box-sizing: border-box;
}


.log-box{
  height: 100%;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;

  /* 透明列表（按你要的图一效果） */
  background: transparent;
  border: none;
  box-shadow: none;
  border-radius: 0;
  padding: 0;
}


/* ✅ 每条日志：用虚线分隔 */
.log-item{
  padding: 10px 2px;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.22);
}
.log-item:last-child{ border-bottom: none; }


.log-title{
  font-size: 12px;
  color: rgba(235, 248, 255, 0.92);
  line-height: 16px;
}

.log-time{
  margin-top: 4px;
  font-size: 12px;
  color: rgba(158, 208, 255, 0.65);
  line-height: 14px;
}

/* 滚动条样式（沿用你 right-scroll 风格） */
.log-box::-webkit-scrollbar { width: 8px; }
.log-box::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.18);
  border-radius: 999px;
}
.log-box::-webkit-scrollbar-track { background: transparent; }

.panel-footer{
  margin-bottom: 0px;
}
</style>
