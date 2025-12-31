import { createRouter, createWebHistory } from 'vue-router'
import ControlView from '@/views/Control.vue'
import LayoutView from '@/views/Layout.vue'
import IndexView from '@/views/index.vue'
import InfoView from '@/views/Info.vue'
import CanvasView from '@/views/Canvas.vue'
import LiveView from '@/views/LiveStream.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: '',
      component: LayoutView,
      redirect: '/index',
      children: [
        {path: 'control', component: ControlView},
        {path: 'index', component: IndexView},
        {path: 'info' , component: InfoView},
        {path: 'canvas', component: CanvasView},
        {path: 'live', component : LiveView}
      ]
    }
  ]
})

export default router
