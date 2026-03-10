<template>
  <div class="login-page">
    <!-- 动态网格背景 -->
    <div class="bg-grid"></div>
    <div class="bg-scanline"></div>
    <div class="bg-vignette"></div>

    <!-- 浮动粒子 -->
    <div class="particles">
      <span v-for="i in 30" :key="i" class="particle" :style="particleStyle(i)"></span>
    </div>

    <!-- 登录主卡片 -->
    <div class="login-card" :class="{ shake: shakeCard }">
      <i class="corner tl"></i><i class="corner tr"></i>
      <i class="corner bl"></i><i class="corner br"></i>

      <div class="card-head">
        <div class="logo">🛸</div>
        <h1 class="title">UAV COMMAND SYSTEM</h1>
        <p class="subtitle">无人机态势感知与指挥控制平台 <span class="ver">v3.2.1</span></p>
        <div class="status-bar">
          <span class="dot online"></span>
          <span class="status-text">SYSTEM ONLINE · ENCRYPTED CHANNEL</span>
        </div>
      </div>

      <el-form :model="form" class="login-form" @keyup.enter="handleLogin">
        <el-form-item>
          <el-input v-model="form.username" placeholder="操作员编号 / Operator ID" :prefix-icon="User" clearable />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="访问密钥 / Access Key" :prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="form.remember" label="记住此终端" class="remember" />
        </el-form-item>
        <el-form-item>
          <el-button class="access-btn" :loading="loading" @click="handleLogin">
            <span v-if="!loading">⚡ 系统接入 / ACCESS</span>
            <span v-else>身份核验中…</span>
          </el-button>
        </el-form-item>
      </el-form>

      <div class="card-foot">
        <router-link to="/register">申请操作员账号</router-link>
        <router-link to="/update-password">重置访问密钥</router-link>
      </div>

      <div class="hint">
        <span>ℹ️</span> 测试账号：<b>admin</b> / <b>admin123</b>
      </div>
    </div>

    <!-- 底部系统信息 -->
    <div class="sys-bar">
      <span>🔒 AES-256 ENCRYPTED</span>
      <span>NODE: CN-EAST-1</span>
      <span>LATENCY: {{ latency }}ms</span>
      <span>{{ clock }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { loginUser } from '@/utils/mockAuth'

const router = useRouter()
const loading = ref(false)
const shakeCard = ref(false)
const clock = ref('')
const latency = ref(12)
let timer = null

const form = ref({ username: '', password: '', remember: false })

const particleStyle = (i) => ({
  left: `${Math.random() * 100}%`,
  top: `${Math.random() * 100}%`,
  animationDelay: `${Math.random() * 8}s`,
  animationDuration: `${6 + Math.random() * 10}s`,
  width: `${2 + Math.random() * 3}px`,
  height: `${2 + Math.random() * 3}px`,
})

const tick = () => {
  clock.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
  latency.value = 8 + Math.floor(Math.random() * 12)
}

onMounted(() => { tick(); timer = setInterval(tick, 1000) })
onUnmounted(() => clearInterval(timer))

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入操作员编号与访问密钥')
    return
  }
  loading.value = true
  await new Promise(r => setTimeout(r, 1200))
  const res = loginUser(form.value.username, form.value.password)
  loading.value = false

  if (res.success) {
    ElMessage.success('身份验证通过，正在接入指挥系统…')
    setTimeout(() => router.push('/index'), 500)
  } else {
    shakeCard.value = true
    setTimeout(() => (shakeCard.value = false), 600)
    ElMessage.error(res.message)
  }
}
</script>

<style scoped>
.login-page {
  position: fixed; inset: 0;
  display: flex; justify-content: center; align-items: center;
  background: #040c18;
  overflow: hidden;
  font-family: 'Segoe UI', 'PingFang SC', sans-serif;
}

/* ---------- 网格背景 ---------- */
.bg-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(58,163,255,.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(58,163,255,.06) 1px, transparent 1px);
  background-size: 60px 60px;
  animation: gridMove 20s linear infinite;
}
@keyframes gridMove { to { background-position: 60px 60px; } }

.bg-scanline {
  position: absolute; inset: 0;
  background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(58,163,255,.03) 2px, rgba(58,163,255,.03) 4px);
  pointer-events: none;
}
.bg-scanline::after {
  content: ''; position: absolute; left: 0; right: 0; height: 120px;
  background: linear-gradient(180deg, rgba(0,212,255,.08), transparent);
  animation: scanDown 4s linear infinite;
}
@keyframes scanDown { 0%{top:-120px} 100%{top:100%} }

.bg-vignette {
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,.6));
  pointer-events: none;
}

/* ---------- 粒子 ---------- */
.particles { position: absolute; inset: 0; pointer-events: none; }
.particle {
  position: absolute; border-radius: 50%;
  background: rgba(0,212,255,.5);
  animation: floatUp linear infinite; opacity: 0;
}
@keyframes floatUp {
  0%  { transform: translateY(0) scale(1); opacity: 0; }
  10% { opacity: .7; }
  90% { opacity: .4; }
  100%{ transform: translateY(-100vh) scale(.3); opacity: 0; }
}

/* ---------- 卡片 ---------- */
.login-card {
  position: relative; width: 440px; max-width: 92vw;
  padding: 44px 40px 30px;
  background: rgba(6,22,42,.92);
  border: 1px solid rgba(58,163,255,.2);
  border-radius: 4px;
  backdrop-filter: blur(20px);
  box-shadow: 0 0 60px rgba(0,120,255,.08), inset 0 1px 0 rgba(58,163,255,.15);
  z-index: 10;
}
.login-card.shake { animation: shake .5s; }
@keyframes shake {
  0%,100%{transform:translateX(0)} 20%{transform:translateX(-12px)}
  40%{transform:translateX(10px)} 60%{transform:translateX(-6px)}
  80%{transform:translateX(4px)}
}

/* 四角 */
.corner { position: absolute; width: 18px; height: 18px; border-color: #00d4ff; border-style: solid; border-width: 0; }
.corner.tl { top:-1px; left:-1px; border-top-width:2px; border-left-width:2px; }
.corner.tr { top:-1px; right:-1px; border-top-width:2px; border-right-width:2px; }
.corner.bl { bottom:-1px; left:-1px; border-bottom-width:2px; border-left-width:2px; }
.corner.br { bottom:-1px; right:-1px; border-bottom-width:2px; border-right-width:2px; }

/* ---------- 头部 ---------- */
.card-head { text-align: center; margin-bottom: 28px; }
.logo { font-size: 40px; margin-bottom: 8px; filter: drop-shadow(0 0 12px rgba(0,212,255,.5)); }
.title { font-size: 22px; font-weight: 700; letter-spacing: 3px; color: #fff; text-shadow: 0 0 20px rgba(58,163,255,.4); margin: 0; }
.subtitle { font-size: 13px; color: rgba(160,180,200,.65); margin-top: 6px; }
.ver { color: #00d4ff; font-weight: 600; }

.status-bar {
  display: inline-flex; align-items: center; gap: 8px;
  margin-top: 12px; padding: 4px 16px;
  background: rgba(0,212,255,.08);
  border: 1px solid rgba(0,212,255,.15);
  border-radius: 20px;
  font-size: 11px; letter-spacing: 1.5px; color: #00d4ff;
}
.dot { width: 7px; height: 7px; border-radius: 50%; background: #00d4ff; box-shadow: 0 0 8px #00d4ff; animation: pulse 1.5s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.7)} }

/* ---------- 表单 ---------- */
.login-form :deep(.el-input__wrapper) {
  background: rgba(0,40,80,.5);
  border: 1px solid rgba(58,163,255,.2);
  border-radius: 4px; box-shadow: none !important;
  height: 44px; transition: all .3s;
}
.login-form :deep(.el-input__wrapper:hover),
.login-form :deep(.el-input__wrapper.is-focus) {
  border-color: rgba(0,212,255,.5);
  box-shadow: 0 0 12px rgba(0,212,255,.15) !important;
}
.login-form :deep(.el-input__inner) { color: rgba(255,255,255,.9); font-size: 14px; letter-spacing: .5px; }
.login-form :deep(.el-input__inner::placeholder) { color: rgba(160,180,200,.4); }
.login-form :deep(.el-input__prefix .el-icon) { color: #3aa3ff; }

.remember :deep(.el-checkbox__label) { color: rgba(160,180,200,.5); font-size: 13px; }
.remember :deep(.el-checkbox__inner) { background: transparent; border-color: rgba(58,163,255,.3); }

.access-btn {
  width: 100%; height: 46px;
  font-size: 15px; font-weight: 600; letter-spacing: 2px;
  color: #fff;
  background: linear-gradient(135deg, #0060c0, #00a0ff);
  border: 1px solid rgba(0,212,255,.3);
  border-radius: 4px; cursor: pointer;
  transition: all .3s; position: relative; overflow: hidden;
}
.access-btn::before {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,.1), transparent);
  transform: translateX(-100%); transition: transform .5s;
}
.access-btn:hover::before { transform: translateX(100%); }
.access-btn:hover { box-shadow: 0 0 30px rgba(0,120,255,.35); border-color: #00d4ff; }

/* ---------- 底部 ---------- */
.card-foot {
  display: flex; justify-content: space-between;
  margin-top: 16px; padding-top: 16px;
  border-top: 1px solid rgba(58,163,255,.1);
}
.card-foot a { color: rgba(0,212,255,.55); font-size: 13px; text-decoration: none; transition: color .3s; }
.card-foot a:hover { color: #00d4ff; }

.hint {
  margin-top: 14px; padding: 10px 14px;
  background: rgba(0,212,255,.05); border: 1px dashed rgba(0,212,255,.12);
  border-radius: 4px; font-size: 12px; color: rgba(160,180,200,.55); text-align: center;
}
.hint b { color: #00d4ff; }

.sys-bar {
  position: fixed; bottom: 0; left: 0; right: 0;
  display: flex; justify-content: center; gap: 32px;
  padding: 8px 0;
  background: rgba(4,12,24,.85);
  border-top: 1px solid rgba(58,163,255,.1);
  font-size: 11px; letter-spacing: 1.5px; color: rgba(0,212,255,.4);
  z-index: 20;
}
</style>
