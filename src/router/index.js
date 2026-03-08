import { createRouter, createWebHistory } from 'vue-router'
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
    redirect: '/index'  // 默认重定向到 index 页面
  },
  {
    path: '/login',
    component: LoginView  // 登录页面
  },
  {
    path: '/register',
    component: RegisterView
  },
  {
    path: '/update-password',
    component: UpdatePasswordView
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

export default router