<template>
  <div class="update-pwd-container" :class="{ 'mobile': isMobile }">
    <div class="update-pwd-box">
      <h2 class="update-title">修改密码</h2>
      
      <div class="update-pwd-content">
        <!-- 左侧表单 -->
        <div class="left-section">
          <el-form 
            :model="updateForm" 
            :rules="rules"
            ref="updateFormRef"
            class="update-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="updateForm.username"
                placeholder="用户名"
                prefix-icon="User"
              />
            </el-form-item>
            <el-form-item prop="oldPassword">
              <el-input
                v-model="updateForm.oldPassword"
                type="password"
                placeholder="旧密码"
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>
          </el-form>
        </div>

        <!-- 右侧表单 -->
        <div class="right-section">
          <el-form 
            :model="updateForm" 
            :rules="rules"
            ref="updateFormRef"
            class="update-form"
          >
            <el-form-item prop="newPassword">
              <el-input
                v-model="updateForm.newPassword"
                type="password"
                placeholder="新密码"
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-form-item prop="confirmPassword">
              <el-input
                v-model="updateForm.confirmPassword"
                type="password"
                placeholder="确认新密码"
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>
          </el-form>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="bottom-buttons">
        <el-button type="primary" class="submit-button" @click="handleUpdate">
          修改密码
        </el-button>
        <el-button class="back-button" @click="goToLogin">
          返回登录
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { User, Lock } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const updateFormRef = ref(null)

const updateForm = ref({
  username: '',
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== updateForm.value.newPassword) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  oldPassword: [
    { required: true, message: '请输入旧密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const isMobile = ref(false)

const checkScreenSize = () => {
  isMobile.value = window.innerWidth <= 800
}

onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})

// const handleUpdate = async () => {
//   updateFormRef.value?.validate(async (valid) => {
//     if (valid) {
//       try {
//         const response = await fetch('/api/user/update-password', {
//           method: 'POST',
//           headers: {
//             'Content-Type': 'application/json'
//           },
//           body: JSON.stringify(updateForm.value)
//         })

//         const result = await response.json()
        
//         if (result.code === 200) {
//           ElMessage.success('密码修改成功！')
//           router.push('/login')
//         } else {
//           ElMessage.error(result.message || '密码修改失败')
//         }
//       } catch (error) {
//         console.error('修改密码失败:', error)
//         ElMessage.error('修改密码失败，请稍后重试')
//       }
//     }
//   })
// }

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.update-pwd-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: url('@/assets/background.jpg') center/cover no-repeat fixed;
}

.update-pwd-box {
  background: rgba(9, 35, 60, 0.8);
  padding: 2.5rem;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  width: 600px;
}

.update-title {
  color: #3aa3ff; /* 设置颜色为蓝色 */
}

.update-pwd-content {
  display: flex;
  gap: 3rem;
  margin: 0.5rem 0;
}

.left-section {
  flex: 1;
  padding-right: 3rem;
  border-right: 1px solid #ddd;
}

.right-section {
  flex: 1;
  padding-left: 1rem;
}

.update-form {
  width: 100%;
}

.update-form :deep(.el-input__wrapper),
.update-form :deep(.el-input__inner) {
  height: 40px;
  font-size: 16px;
}

.bottom-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #ddd;
  gap: 1rem;
}

.submit-button,
.back-button {
  flex: 1;
  height: 40px;
  font-size: 16px;
}

h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
  font-size: 24px;
}

/* 移动端样式 */
.mobile .update-pwd-box {
  width: 90%;
  max-width: 400px;
  padding: 2rem;
}

.mobile .update-pwd-content {
  flex-direction: column;
  gap: 0.5rem;
}

.mobile .left-section {
  border-right: none;
  border-bottom: 1px solid #ddd;
  padding-right: 0;
  padding-bottom: 0.5rem;
}

.mobile .right-section {
  padding-left: 0;
  padding-top: 1rem;
}

.mobile .bottom-buttons {
  flex-direction: column;
  gap: 1rem;
}

.mobile .submit-button,
.mobile .back-button {
  width: 100%;
  margin: 0;
}
</style> 