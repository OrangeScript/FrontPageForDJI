<template>
  <div class="reg-page">
    <div class="bg-grid"></div>
    <div class="bg-scanline"></div>
    <div class="bg-vignette"></div>
    <div class="particles"><span v-for="i in 20" :key="i" class="particle" :style="pStyle(i)"></span></div>

    <div class="reg-card">
      <i class="corner tl"></i><i class="corner tr"></i>
      <i class="corner bl"></i><i class="corner br"></i>

      <div class="card-head">
        <div class="logo">🛡️</div>
        <h1 class="title">OPERATOR REGISTRATION</h1>
        <p class="sub">操作员身份注册 · 安全通道</p>
      </div>

      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" class="reg-form">
        <div class="form-grid">
          <el-form-item label="操作员编号" prop="username">
            <el-input v-model="form.username" placeholder="3-20 位字母或数字" :prefix-icon="User" />
          </el-form-item>
          <el-form-item label="电子邮箱" prop="email">
            <el-input v-model="form.email" placeholder="name@domain.com" :prefix-icon="Message" />
          </el-form-item>
          <el-form-item label="访问密钥" prop="password">
            <el-input v-model="form.password" type="password" placeholder="至少 6 位" :prefix-icon="Lock" show-password />
          </el-form-item>
          <el-form-item label="操作员角色" prop="role">
            <el-select v-model="form.role" placeholder="选择角色" style="width:100%">
              <el-option label="飞行员" value="飞行员" />
              <el-option label="任务操作员" value="任务操作员" />
              <el-option label="数据分析员" value="数据分析员" />
              <el-option label="系统管理员" value="系统管理员" />
            </el-select>
          </el-form-item>
        </div>

        <div class="btn-row">
          <el-button class="submit-btn" :loading="loading" @click="handleRegister">
            <span v-if="!loading">📡 提交注册 / REGISTER</span>
            <span v-else>注册中…</span>
          </el-button>
          <el-button class="back-btn" @click="$router.push('/login')">↩ 返回登录</el-button>
        </div>
      </el-form>
    </div>

    <div class="sys-bar">
      <span>🔒 SECURE REGISTRATION</span>
      <span>NODE: CN-EAST-1</span>
      <span>{{ clock }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { registerUser } from '@/utils/mockAuth'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const clock = ref('')
let timer = null

const form = ref({ username: '', password: '', email: '', role: '任务操作员' })

const rules = {
  username: [{ required: true, message: '请输入操作员编号', trigger: 'blur' }, { min: 3, max: 20, message: '3-20 个字符', trigger: 'blur' }],
  password: [{ required: true, message: '请输入访问密钥', trigger: 'blur' }, { min: 6, message: '至少 6 位', trigger: 'blur' }],
  email:    [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
  role:     [{ required: true, message: '请选择角色', trigger: 'change' }],
}

const pStyle = (i) => ({ left:`${Math.random()*100}%`, top:`${Math.random()*100}%`, animationDelay:`${Math.random()*8}s`, animationDuration:`${6+Math.random()*10}s`, width:`${2+Math.random()*3}px`, height:`${2+Math.random()*3}px` })

const tick = () => { clock.value = new Date().toLocaleTimeString('zh-CN',{hour12:false}) }
onMounted(()=>{ tick(); timer=setInterval(tick,1000) })
onUnmounted(()=>clearInterval(timer))

const handleRegister = async () => {
  const valid = await formRef.value?.validate().catch(()=>false)
  if (!valid) return

  loading.value = true
  await new Promise(r=>setTimeout(r,1000))
  const res = registerUser(form.value)
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
.reg-page {
  position:fixed;inset:0;display:flex;justify-content:center;align-items:center;
  background:#040c18;overflow:hidden;font-family:'Segoe UI','PingFang SC',sans-serif;
}
.bg-grid{position:absolute;inset:0;background-image:linear-gradient(rgba(58,163,255,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(58,163,255,.06) 1px,transparent 1px);background-size:60px 60px;animation:gridMove 20s linear infinite}
@keyframes gridMove{to{background-position:60px 60px}}
.bg-scanline{position:absolute;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(58,163,255,.03) 2px,rgba(58,163,255,.03) 4px);pointer-events:none}
.bg-scanline::after{content:'';position:absolute;left:0;right:0;height:120px;background:linear-gradient(180deg,rgba(0,212,255,.08),transparent);animation:scanDown 4s linear infinite}
@keyframes scanDown{0%{top:-120px}100%{top:100%}}
.bg-vignette{position:absolute;inset:0;background:radial-gradient(ellipse at center,transparent 40%,rgba(0,0,0,.6));pointer-events:none}

.particles{position:absolute;inset:0;pointer-events:none}
.particle{position:absolute;border-radius:50%;background:rgba(0,212,255,.5);animation:floatUp linear infinite;opacity:0}
@keyframes floatUp{0%{transform:translateY(0) scale(1);opacity:0}10%{opacity:.7}90%{opacity:.4}100%{transform:translateY(-100vh) scale(.3);opacity:0}}

.reg-card{
  position:relative;width:520px;max-width:94vw;padding:40px 38px 30px;
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

/* 表单 */
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:0 20px}
.reg-form :deep(.el-form-item__label){color:rgba(160,180,200,.7);font-size:12px;letter-spacing:1px}
.reg-form :deep(.el-input__wrapper),
.reg-form :deep(.el-select .el-input__wrapper){
  background:rgba(0,40,80,.5);border:1px solid rgba(58,163,255,.2);
  border-radius:4px;box-shadow:none !important;height:42px;transition:all .3s;
}
.reg-form :deep(.el-input__wrapper:hover),.reg-form :deep(.el-input__wrapper.is-focus){
  border-color:rgba(0,212,255,.5);box-shadow:0 0 12px rgba(0,212,255,.15) !important;
}
.reg-form :deep(.el-input__inner){color:rgba(255,255,255,.9);font-size:14px}
.reg-form :deep(.el-input__inner::placeholder){color:rgba(160,180,200,.4)}
.reg-form :deep(.el-input__prefix .el-icon){color:#3aa3ff}
.reg-form :deep(.el-select-dropdown__item){background:rgba(6,22,42,.95);color:#c0ccda}
.reg-form :deep(.el-select-dropdown__item.hover){background:rgba(58,163,255,.15)}

.btn-row{display:flex;gap:14px;margin-top:8px}
.submit-btn{
  flex:1;height:44px;font-size:14px;font-weight:600;letter-spacing:1.5px;color:#fff;
  background:linear-gradient(135deg,#0060c0,#00a0ff);border:1px solid rgba(0,212,255,.3);
  border-radius:4px;cursor:pointer;transition:all .3s;
}
.submit-btn:hover{box-shadow:0 0 24px rgba(0,120,255,.35);border-color:#00d4ff}
.back-btn{
  flex:1;height:44px;font-size:14px;font-weight:500;letter-spacing:1px;
  color:rgba(160,180,200,.7);background:rgba(0,40,80,.3);
  border:1px solid rgba(58,163,255,.15);border-radius:4px;cursor:pointer;transition:all .3s;
}
.back-btn:hover{color:#00d4ff;border-color:rgba(0,212,255,.4)}

.sys-bar{
  position:fixed;bottom:0;left:0;right:0;display:flex;justify-content:center;gap:32px;
  padding:8px 0;background:rgba(4,12,24,.85);border-top:1px solid rgba(58,163,255,.1);
  font-size:11px;letter-spacing:1.5px;color:rgba(0,212,255,.4);z-index:20;
}
</style>
