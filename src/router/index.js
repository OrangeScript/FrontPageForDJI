import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated } from '@/utils/mockAuth'

import UavControlView from '@/views/UavControl.vue'
import TaskView from '@/views/Task.vue'
import YoloIdentifyView from '@/views/YoloIdentify.vue'
import ControlView from '@/views/Control.vue'
import LayoutView from '@/views/Layout.vue'
import IndexView from '@/views/index.vue'
import InfoView from '@/views/Info.vue'
import CanvasView from '@/views/Canvas.vue'
import LiveView from '@/views/LiveStream.vue'
import LoginView from '@/views/Login.vue'
import RegisterView from '@/views/Register.vue'
import UpdatePasswordView from '@/views/UpdatePassword.vue'

const routes = [
  {
    path: '/',
    redirect: '/index'
  },
  {
    path: '/login',
    component: LoginView,
    meta: { guest: true }
  },
  {
    path: '/register',
    component: RegisterView,
    meta: { guest: true }
  },
  {
    path: '/update-password',
    component: UpdatePasswordView,
    meta: { guest: true }
  },
  {
    path: '/',
    name: 'Layout',
    component: LayoutView,
    redirect: '/index',
    meta: { requiresAuth: true },
    children: [
      { path: 'index', component: IndexView },
      { path: 'uavcontrol', component: UavControlView },
      { path: 'task', component: TaskView },
      { path: 'info', component: InfoView },
      { path: 'yolo', component: YoloIdentifyView },
      { path: 'control', component: ControlView },
      { path: 'canvas', component: CanvasView },
      { path: 'live', component: LiveView },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

/* ---------- 导航守卫：未登录跳转登录页 ---------- */
router.beforeEach((to, _from, next) => {
  if (to.matched.some(r => r.meta.requiresAuth) && !isAuthenticated()) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router