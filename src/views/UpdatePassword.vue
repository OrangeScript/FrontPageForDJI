<template>
  <div class="pwd-page">
    <div class="bg-grid"></div>
    <div class="bg-scanline"></div>
    <div class="bg-vignette"></div>

    <div class="pwd-card">
      <i class="corner tl"></i><i class="corner tr"></i>
      <i class="corner bl"></i><i class="corner br"></i>

      <div class="card-head">
        <div class="logo">🔑</div>
        <h1 class="title">RESET ACCESS KEY</h1>
        <p class="sub">访问密钥重置 · 身份校验通道</p>
      </div>

      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" class="pwd-form">
        <el-form-item label="操作员编号" prop="username">
          <el-input v-model="form.username" placeholder="Operator ID" :prefix-icon="User" />
        </el-form-item>
        <el-form-item label="当前访问密钥" prop="oldPassword">
          <el-input v-model="form.oldPassword" type="password" placeholder="Current Key" :prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item label="新访问密钥" prop="newPassword">
          <el-input v-model="form.newPassword" type="password" placeholder="New Key (≥6 位)" :prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item label="确认新密钥" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="Confirm New Key" :prefix-icon="Lock" show-password />
        </el-form-item>

        <div class="btn-row">
          <el-button class="submit-btn" :loading="loading" @click="handleUpdate">
            <span v-if="!loading">🔄 更新密钥 / UPDATE</span>
            <span v-else>验证中…</span>
          </el-button>
          <el-button class="back-btn" @click="$router.push('/login')">↩ 返回登录</el-button>
        </div>
      </el-form>
    </div>

    <div class="sys-bar">
      <span>🔒 SECURE CHANNEL</span>
      <span>{{ clock }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { updatePassword } from '@/utils/mockAuth'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const clock = ref('')
let timer = null

const form = ref({ username:'', oldPassword:'', newPassword:'', confirmPassword:'' })

const validateConfirm = (_r, v, cb) => {
  if (v !== form.value.newPassword) cb(new Error('两次输入密钥不一致'))
  else cb()
}
const rules = {
  username:        [{ required:true, message:'请输入操作员编号', trigger:'blur' }],
  oldPassword:     [{ required:true, message:'请输入当前密钥', trigger:'blur' }],
  newPassword:     [{ required:true, message:'请输入新密钥', trigger:'blur' },{ min:6, message:'至少 6 位', trigger:'blur' }],
  confirmPassword: [{ required:true, message:'请确认新密钥', trigger:'blur' },{ validator:validateConfirm, trigger:'blur' }],
}

const tick=()=>{clock.value=new Date().toLocaleTimeString('zh-CN',{hour12:false})}
onMounted(()=>{tick();timer=setInterval(tick,1000)})
onUnmounted(()=>clearInterval(timer))

const handleUpdate = async () => {
  const valid = await formRef.value?.validate().catch(()=>false)
  if (!valid) return
  loading.value = true
  await new Promise(r=>setTimeout(r,1000))
  const res = updatePassword(form.value.username, form.value.oldPassword, form.value.newPassword)
  loading.value = false

  if (res.success) {
    ElMessage.success(res.message)
    setTimeout(()=>router.push('/login'),600)
  } else {
    ElMessage.error(res.message)
  }
}
</script>

<style scoped>
.pwd-page{position:fixed;inset:0;display:flex;justify-content:center;align-items:center;background:#040c18;overflow:hidden;font-family:'Segoe UI','PingFang SC',sans-serif}
.bg-grid{position:absolute;inset:0;background-image:linear-gradient(rgba(58,163,255,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(58,163,255,.06) 1px,transparent 1px);background-size:60px 60px;animation:gm 20s linear infinite}
@keyframes gm{to{background-position:60px 60px}}
.bg-scanline{position:absolute;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(58,163,255,.03) 2px,rgba(58,163,255,.03) 4px);pointer-events:none}
.bg-scanline::after{content:'';position:absolute;left:0;right:0;height:120px;background:linear-gradient(180deg,rgba(0,212,255,.08),transparent);animation:sd 4s linear infinite}
@keyframes sd{0%{top:-120px}100%{top:100%}}
.bg-vignette{position:absolute;inset:0;background:radial-gradient(ellipse at center,transparent 40%,rgba(0,0,0,.6));pointer-events:none}

.pwd-card{
  position:relative;width:440px;max-width:92vw;padding:40px 38px 28px;
  background:rgba(6,22,42,.92);border:1px solid rgba(58,163,255,.2);border-radius:4px;
  backdrop-filter:blur(20px);box-shadow:0 0 60px rgba(0,120,255,.08),inset 0 1px 0 rgba(58,163,255,.15);z-index:10;
}
.corner{position:absolute;width:18px;height:18px;border-color:#00d4ff;border-style:solid;border-width:0}
.corner.tl{top:-1px;left:-1px;border-top-width:2px;border-left-width:2px}
.corner.tr{top:-1px;right:-1px;border-top-width:2px;border-right-width:2px}
.corner.bl{bottom:-1px;left:-1px;border-bottom-width:2px;border-left-width:2px}
.corner.br{bottom:-1px;right:-1px;border-bottom-width:2px;border-right-width:2px}

.card-head{text-align:center;margin-bottom:24px}
.logo{font-size:36px;margin-bottom:6px;filter:drop-shadow(0 0 12px rgba(0,212,255,.5))}
.title{font-size:20px;font-weight:700;letter-spacing:3px;color:#fff;text-shadow:0 0 20px rgba(58,163,255,.4);margin:0}
.sub{font-size:12px;color:rgba(160,180,200,.6);margin-top:6px;letter-spacing:1px}

.pwd-form :deep(.el-form-item__label){color:rgba(160,180,200,.7);font-size:12px;letter-spacing:1px}
.pwd-form :deep(.el-input__wrapper){
  background:rgba(0,40,80,.5);border:1px solid rgba(58,163,255,.2);
  border-radius:4px;box-shadow:none !important;height:42px;transition:all .3s;
}
.pwd-form :deep(.el-input__wrapper:hover),.pwd-form :deep(.el-input__wrapper.is-focus){border-color:rgba(0,212,255,.5);box-shadow:0 0 12px rgba(0,212,255,.15) !important}
.pwd-form :deep(.el-input__inner){color:rgba(255,255,255,.9);font-size:14px}
.pwd-form :deep(.el-input__inner::placeholder){color:rgba(160,180,200,.4)}
.pwd-form :deep(.el-input__prefix .el-icon){color:#3aa3ff}

.btn-row{display:flex;gap:14px;margin-top:10px}
.submit-btn{flex:1;height:44px;font-size:14px;font-weight:600;letter-spacing:1.5px;color:#fff;background:linear-gradient(135deg,#0060c0,#00a0ff);border:1px solid rgba(0,212,255,.3);border-radius:4px;transition:all .3s}
.submit-btn:hover{box-shadow:0 0 24px rgba(0,120,255,.35);border-color:#00d4ff}
.back-btn{flex:1;height:44px;font-size:14px;font-weight:500;color:rgba(160,180,200,.7);background:rgba(0,40,80,.3);border:1px solid rgba(58,163,255,.15);border-radius:4px;transition:all .3s}
.back-btn:hover{color:#00d4ff;border-color:rgba(0,212,255,.4)}

.sys-bar{position:fixed;bottom:0;left:0;right:0;display:flex;justify-content:center;gap:32px;padding:8px 0;background:rgba(4,12,24,.85);border-top:1px solid rgba(58,163,255,.1);font-size:11px;letter-spacing:1.5px;color:rgba(0,212,255,.4);z-index:20}
</style>
