<template>
  <el-container class="layout">
    <!-- 侧边栏：默认收起，hover 展开 -->
    <el-aside
      class="aside"
      :width="asideWidth"
      @mouseenter="isHover = true"
      @mouseleave="isHover = false"
    >
      <el-menu router class="menu" :collapse="menuCollapse" :collapse-transition="false">
        <el-menu-item index="/index">
          <el-icon class="emoji-icon"><span>🏠</span></el-icon>
          <span class="menu-text">首页</span>
        </el-menu-item>

        <el-menu-item index="/uavcontrol">
          <el-icon class="emoji-icon"><span>🕹️</span></el-icon>
          <span class="menu-text">无人机操控</span>
        </el-menu-item>

        <el-menu-item index="/task">
          <el-icon class="emoji-icon"><span>🗺️</span></el-icon>
          <span class="menu-text">任务管理</span>
        </el-menu-item>
        <el-menu-item index="/mission">
          <el-icon class="emoji-icon"><span>�</span></el-icon>
          <span class="menu-text">任务统计</span>
        </el-menu-item>

        <el-menu-item index="/info">
          <el-icon class="emoji-icon"><span>📡</span></el-icon>
          <span class="menu-text">飞行数据中心</span>
        </el-menu-item>

        <el-menu-item index="/yolo">
          <el-icon class="emoji-icon"><span>📺</span></el-icon>
          <span class="menu-text">YOLO识别结果</span>
        </el-menu-item>

        <!-- 退出登录 -->
        <el-menu-item @click="handleLogout" class="logout-item">
          <el-icon class="emoji-icon"><span>🚪</span></el-icon>
          <span class="menu-text">退出登录</span>
        </el-menu-item>

        <!-- <el-sub-menu index="/me">
          <template #title>
            <el-icon class="emoji-icon"><span>🕹️</span></el-icon>
            <span class="menu-text">控制</span>
          </template>

          <el-menu-item index="/control">
            <el-icon class="emoji-icon"><span>🛫</span></el-icon>
            <span class="menu-text">飞行控制</span>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/canvas">
          <el-icon class="emoji-icon"><span>🗺️</span></el-icon>
          <span class="menu-text">画图执行路线</span>
        </el-menu-item>

        <el-menu-item index="/live">
          <el-icon class="emoji-icon"><span>📺</span></el-icon>
          <span class="menu-text">直播</span>
        </el-menu-item>

        <el-menu-item index="/test">
          <el-icon class="emoji-icon"><span>🧪</span></el-icon>
          <span class="menu-text">测试</span>
        </el-menu-item> -->
      </el-menu>
    </el-aside>

    <!-- 主体：加一个壳，保证 router-view 撑满并且可滚动 -->
    <el-main class="main">
      <div class="main-inner">
        <router-view />
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { logout } from '@/utils/mockAuth'

const router = useRouter()
const isHover = ref(false)

const COLLAPSE_W = 64
const EXPAND_W = 200

const asideWidth = computed(() => (isHover.value ? `${EXPAND_W}px` : `${COLLAPSE_W}px`))
const menuCollapse = computed(() => !isHover.value)

const handleLogout = () => {
  logout()
  router.push('/login')
}
</script>

<style scoped>
/* 整体铺满屏幕，且不让外层出现奇怪滚动 */
.layout {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  background: #061a2c;

  overflow: hidden;    /* 外层不滚，滚动交给 main-inner */
  min-width: 0;
  min-height: 0;
}

/* 侧边栏背景统一成深蓝 */
.aside {
  height: 100%;
  transition: width 180ms ease;
  overflow: hidden;
  background: rgba(9, 35, 60, 0.85);
  border-right: 1px solid rgba(255, 255, 255, 0.10);

  flex: 0 0 auto;      /* 防止被挤压 */
}

/* menu 撑满，去掉默认边框 */
.menu {
  height: 100%;
  border-right: none;
  background: transparent;
}

/* 统一每项高度 */
.menu :deep(.el-menu-item),
.menu :deep(.el-sub-menu__title) {
  height: 52px;
  line-height: 52px;
  color: rgba(255, 255, 255, 0.86);
}

/* emoji 作为“图标位”，收起时也会显示 */
.emoji-icon {
  width: 24px;
  display: inline-flex;
  justify-content: center;
  align-items: center;
}

.emoji-icon span {
  font-size: 18px;
  line-height: 1;
}

/* 文本样式 */
.menu-text {
  font-size: 14px;
}

/* hover / active 统一配色 */
.menu :deep(.el-menu-item:hover),
.menu :deep(.el-sub-menu__title:hover) {
  background: rgba(58, 163, 255, 0.12);
}

.menu :deep(.el-menu-item.is-active) {
  background: rgba(58, 163, 255, 0.18);
  color: rgba(255, 255, 255, 0.95);
  font-weight: 700;
}

/* 子菜单展开的背景也压暗一点 */
.menu :deep(.el-menu--inline) {
  background: rgba(0, 0, 0, 0.12);
}

/* 退出登录在底部 */
.menu :deep(.logout-item) {
  position: absolute;
  bottom: 12px;
  width: 100%;
}
.menu :deep(.logout-item:hover) {
  background: rgba(255, 51, 102, 0.12);
  color: #ff3366;
}

/* 收起模式下，把 tooltip 的视觉抖动降到最低 */
.menu :deep(.el-menu-tooltip__trigger) {
  display: flex;
  align-items: center;
}

/* 主体区域：必须允许内部滚动生效 */
.main {
  height: 100%;
  padding: 0;
  background: transparent;

  min-width: 0;   /* 关键：防止 router-view 撑破 */
  min-height: 0;  /* 关键：防止高度撑破导致内容被裁剪 */
  overflow: hidden;
}

/* router-view 的容器：负责滚动 */
.main-inner {
  height: 100%;
  width: 100%;

  overflow: auto;
  min-width: 0;
  min-height: 0;
}

/* 你想要的话，加个滚动条样式（可删） */
.main-inner::-webkit-scrollbar {
  width: 8px;
}
.main-inner::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.18);
  border-radius: 999px;
}
.main-inner::-webkit-scrollbar-track {
  background: transparent;
}
</style>
