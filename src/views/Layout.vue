<script setup>
</script>
<template>
    <el-container>
        <!-- 左侧菜单 -->
        <el-aside width="200px" class="aside">
          <!-- 左侧菜单栏 -->
          <el-menu router>
            <!-- 首页菜单 -->
            <el-menu-item index="/index">
              <el-icon><Promotion /></el-icon> 首页
            </el-menu-item>
            
            
            <!-- 班级管理菜单 -->
            <el-sub-menu index="/me">
              <template #title>
                <el-icon><UserFilled /></el-icon> 控制
              </template>
              <el-menu-item index="/control">
                <el-icon><UserFilled /></el-icon>飞行控制
              </el-menu-item>
            </el-sub-menu>
            <el-menu-item index="/info">
                <el-icon><UserFilled /></el-icon>飞行信息
              </el-menu-item>
            <el-menu-item index="/canvas">
                <el-icon><UserFilled /></el-icon>画图执行路线
              </el-menu-item>
            <el-menu-item index="/live">
                <el-icon><UserFilled /></el-icon>直播
              </el-menu-item>
          </el-menu>
        </el-aside>
        
        <el-main>
          <router-view></router-view>
        </el-main>
      </el-container>
</template>

