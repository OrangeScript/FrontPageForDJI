<template>
  <div class="register-container" :class="{ 'mobile': isMobile }">
    <div class="register-box">
      <h2 class="register-title">用户注册</h2>
      
      <div class="register-content">
        <!-- 左侧表单 -->
        <div class="left-section">
          <el-form 
            :model="registerForm" 
            :rules="rules"
            ref="registerFormRef"
            class="register-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="用户名"
                prefix-icon="User"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="密码"
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="电子邮箱"
                prefix-icon="Message"
              />
            </el-form-item>
            <el-form-item prop="birthDate">
              <el-date-picker
                v-model="registerForm.birthDate"
                type="date"
                placeholder="年/月/日"
                style="width: 100%"
                :clearable="false"
              />
            </el-form-item>
          </el-form>
        </div>

        <!-- 右侧头像上传 -->
        <div class="right-section">
          <div class="avatar-uploader">
            <div class="avatar-title">请上传头像</div>
            <el-upload
              class="avatar-upload"
              action="#"
              :show-file-list="false"
              :auto-upload="false"
              :on-change="handleAvatarChange"
            >
              <img v-if="imageUrl" :src="imageUrl" class="avatar" />
              <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
            </el-upload>
          </div>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="bottom-buttons">
        <el-button type="primary" class="submit-button" @click="handleRegister">
          注册用户
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
import { User, Lock, Message, Plus } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const registerFormRef = ref(null)

const registerForm = ref({
  username: '',
  password: '',
  email: '',
  birthDate: '',
  avatar: ''
})

const imageUrl = ref('')
const uploadLoading = ref(false)

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  birthDate: [
    { required: true, message: '请选择出生日期', trigger: 'change' },
    {
      validator: (rule, value, callback) => {
        if (value && new Date(value) > new Date()) {
          callback(new Error('出生日期不能大于当前日期'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ],
  avatar: [
    { required: true, message: '请上传头像', trigger: 'change' }
  ]
}

const isMobile = ref(false)

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

// const handleAvatarChange = async (file) => {
//   // 验证文件类型
//   const isImage = file.raw.type.startsWith('image/')
//   if (!isImage) {
//     ElMessage.error('只能上传图片文件！')
//     return false
//   }
  
//   // 验证文件大小（限制为2MB）
//   const isLt2M = file.raw.size / 1024 / 1024 < 2
//   if (!isLt2M) {
//     ElMessage.error('图片大小不能超过2MB！')
//     return false
//   }

//   // 创建FormData对象
//   const formData = new FormData()
//   formData.append('file', file.raw)

//   try {
//     uploadLoading.value = true
//     // 上传文件
//     const response = await fetch('/api/file/upload', {
//       method: 'POST',
//       body: formData
//     })
//     const result = await response.json()
    
//     if (result.code === 200) {
//       imageUrl.value = URL.createObjectURL(file.raw)
//       registerForm.value.avatar = result.data
//       ElMessage.success('头像上传成功')
//     } else {
//       ElMessage.error(result.message || '头像上传失败')
//     }
//   } catch (error) {
//     console.error('上传失败:', error)
//     ElMessage.error('头像上传失败')
//   } finally {
//     uploadLoading.value = false
//   }
// }

// const handleRegister = async () => {
//   if (!registerForm.value.avatar) {
//     ElMessage.warning('请上传头像')
//     return
//   }

//   registerFormRef.value?.validate(async (valid) => {
//     if (valid) {
//       try {
//         // 修复日期格式化，避免时区问题
//         let formattedDate = '';
//         if (registerForm.value.birthDate) {
//           // 直接使用日期对象，避免时区转换
//           const date = new Date(registerForm.value.birthDate);
//           const year = date.getFullYear();
//           const month = String(date.getMonth() + 1).padStart(2, '0');
//           const day = String(date.getDate()).padStart(2, '0');
//           formattedDate = `${year}-${month}-${day}`;
//         }
        
//         const response = await fetch('/api/user/register', {
//           method: 'POST',
//           headers: {
//             'Content-Type': 'application/json'
//           },
//           body: JSON.stringify({
//             ...registerForm.value,
//             birthDate: formattedDate
//           })
//         })

//         const result = await response.json()
        
//         if (result.code === 200) {
//           ElMessage.success('注册成功！')
//           router.push('/login')
//         } else {
//           ElMessage.error(result.message || '注册失败')
//         }
//       } catch (error) {
//         console.error('注册失败:', error)
//         ElMessage.error('注册失败，请稍后重试')
//       }
//     }
//   })
// }

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: url('@/assets/background.jpg') center/cover no-repeat fixed;
}

.register-box {
  background: rgba(9, 35, 60, 0.8);
  padding: 2.5rem;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  width: 600px;
}

.register-title {
  color: #3aa3ff; /* 设置颜色为蓝色 */
}

.register-content {
  display: flex;
  gap: 3rem;
  margin: 0.5rem 0;
}

.left-section {
  flex: 1;
  padding-right: 2.5rem;
  border-right: 1px solid #ddd;
}

.right-section {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.register-form {
  width: 100%;
}

.register-form :deep(.el-input__wrapper),
.register-form :deep(.el-input__inner) {
  height: 40px;
  font-size: 16px;
}

.avatar-uploader {
  text-align: center;
}

.avatar-title {
  margin-bottom: 0.5rem;
  color: #3aa3ff;
}

.avatar-upload {
  border: 1px dashed #3aa3ff;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 180px;
  height: 180px;
  margin: 0 auto;
}

.avatar-upload:hover {
  border-color: #409EFF;
}

.avatar-uploader-icon {
  font-size: 20px;
  color: #3aa3ff;
  width: 180px;
  height: 180px;
  line-height: 180px;
  text-align: center;
}

.avatar {
  width: 180px;
  height: 180px;
  display: block;
  object-fit: cover;
}

.bottom-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #ddd;
  gap: 3.5rem;
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
.mobile .register-box {
  width: 90%;
  max-width: 400px;
  padding: 2rem;
}

.mobile .register-content {
  flex-direction: column;
  gap: 0rem;
}

.mobile .left-section {
  border-right: none;
  padding-right: 0;
}

.mobile .avatar-upload {
  width: 300px;  /* 调整头像上传框的宽度 */
  height: 150px;  /* 调整头像上传框的高度 */
  margin: 0 auto;  /* 确保上传框在父容器中水平居中 */
}

.mobile .avatar-uploader-icon {
  font-size: 20px;  /* 增大图标的字体大小，使其更容易点击 */
  width: 300px;  /* 确保图标与上传框一致 */
  height: 150px;  /* 确保图标与上传框一致 */
  line-height: 150px;  /* 垂直居中图标 */
}

.mobile .avatar {
  width: 150px;  /* 确保头像图片适配移动端大小 */
  height: 150px;  /* 确保头像图片适配移动端大小 */
  object-fit: cover;  /* 保持头像比例并裁剪 */
}

.mobile .avatar-title {
  font-size: 14px;  /* 设置标题文字更小，适应小屏幕 */
}

.mobile .bottom-buttons {
  flex-direction: column;
  gap: 0.5rem;
}

.mobile .submit-button,
.mobile .back-button {
  width: 100%;
  margin: 0;
}
</style> 