<template>
  <div class="login-container" :class="{ 'mobile': isMobile }">
    <div class="login-box">
      <h2  class="login-title">用户登录</h2>
      
      <div class="login-content">
        <!-- 左侧第三方登录 -->
        <div class="left-section">
          <div class="third-party-login">
            <el-button class="third-party-btn qq-login">
              <img src="@/assets/qq-icon.png" alt="QQ" />
              QQ登录
            </el-button>
            <el-button class="third-party-btn wechat-login">
              <img src="@/assets/wechat-icon.png" alt="微信" />
              微信登录
            </el-button>
            <el-button class="third-party-btn alipay-login">
              <img src="@/assets/alipay-icon.png" alt="支付宝" />
              支付宝登录
            </el-button>
          </div>
        </div>

        <!-- 右侧登录表单 -->
        <div class="right-section">
          <el-form :model="loginForm" class="login-form">
            <el-form-item>
              <el-input
                v-model="loginForm.username"
                placeholder="用户名"
                prefix-icon="User"
              />
            </el-form-item>
            <el-form-item>
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                prefix-icon="Lock"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" class="login-button" @click="handleLogin">
                登录
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>

      <!-- 底部链接 -->
      <div class="bottom-links">
        <router-link to="/register">注册用户</router-link>
        <router-link to="/update-password">修改密码</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'

const loginForm = ref({
  username: '',
  password: ''
})

// const isMobile = ref(false)
// const router = useRouter()
// const route = useRoute()

// const checkScreenSize = () => {
//   isMobile.value = window.innerWidth <= 800
// }

// onMounted(() => {
//   checkScreenSize()
//   window.addEventListener('resize', checkScreenSize)
// })

// onUnmounted(() => {
//   window.removeEventListener('resize', checkScreenSize)
// })

// const handleLogin = async () => {
//   if (!loginForm.value.username || !loginForm.value.password) {
//     ElMessage.error('请输入用户名和密码')
//     return
//   }

//   try {
//     const response = await fetch('/api/user/login', {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json'
//       },
//       body: JSON.stringify(loginForm.value)
//     })

//     const result = await response.json()
    
//     if (result.code === 200) {
//       ElMessage.success('登录成功！')
//       // 存储用户信息到localStorage
//       localStorage.setItem('user', JSON.stringify(result.data))
//       // 获取重定向地址
//       const redirectPath = route.query.redirect || '/home'
//       router.push(redirectPath)
//     } else {
//       // 统一错误提示
//       if (result.message.includes('用户不存在') || result.message.includes('密码错误')) {
//         ElMessage.error('用户名或密码错误')
//       } else {
//         ElMessage.error(result.message)
//       }
//     }
//   } catch (error) {
//     console.error('登录失败:', error)
//     ElMessage.error('登录失败，请稍后重试')
//   }
// }
</script>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: url('@/assets/background.jpg') center/cover no-repeat fixed;
}

.login-box {
  background: rgba(9, 35, 60, 0.8);
  padding: 2.5rem;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  width: 600px;
}

.login-title {
  color: #3aa3ff; /* 设置颜色为蓝色 */
}

.login-content {
  display: flex;
  gap: 2rem;
  margin: 0.5rem 0;
}

.left-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  padding-right: 3rem;
  border-right: 1px solid #ddd;
  justify-content: center;
}

.right-section {
  flex: 1;
  padding-left: 1rem;
}

.third-party-login {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  margin-bottom: 2px;
}

.third-party-login .el-button {
  width: 100%;
  margin: 0;
  justify-content: center;
}

.third-party-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  font-size: 16px;
  border-radius: 4px;
  padding: 0;
  margin: 0;
  border: none;
  color: #fff;
  transition: all 0.3s ease;
}

.third-party-btn img {
  width: 24px;
  height: 24px;
  margin-right: 12px;
  object-fit: contain;
}

.login-form {
  width: 100%;
}

.login-form :deep(.el-input__wrapper) {
  height: 40px;
  font-size: 16px;
}

.login-form :deep(.el-input__inner) {
  height: 40px;
  line-height: 40px;
}

.login-button {
  width: 100%;
  height: 40px;
  font-size: 16px;
}

.bottom-links {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #ddd;
}

.bottom-links a {
  color: #3aa3ff;
  text-decoration: none;
  font-size: 14px;
}

.bottom-links a:hover {
  text-decoration: underline;
}

/* 移动端样式 */
.mobile .login-box {
  width: 90%;
  max-width: 400px;
  padding: 2rem;
}

.mobile .login-content {
  flex-direction: column;
  gap: 2rem;
}

.mobile .left-section {
  border-right: none;
  border-bottom: 1px solid #ddd;
  padding-right: 0;
  padding-bottom: 2rem;
}

.mobile .right-section {
  padding-left: 0;
}

.mobile .bottom-links {
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
  font-size: 24px;
}

/* QQ登录按钮样式 */
.qq-login {
  background-color: #12B7F5;
  border-color: #12B7F5;
  color: #fff;
}

.qq-login:hover {
  background-color: #2DC2F7;
  border-color: #2DC2F7;
}

/* 微信登录按钮样式 */
.wechat-login {
  background-color: #07C160;
  border-color: #07C160;
  color: #fff;
}

.wechat-login:hover {
  background-color: #26CD77;
  border-color: #26CD77;
}

/* 支付宝登录按钮样式 */
.alipay-login {
  background-color: #1677FF;
  border-color: #1677FF;
  color: #fff;
}

.alipay-login:hover {
  background-color: #3D91FF;
  border-color: #3D91FF;
}
</style> 