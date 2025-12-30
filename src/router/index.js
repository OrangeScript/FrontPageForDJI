import { createRouter, createWebHistory } from 'vue-router'
import ControlView from '@/views/Control.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'control',
      component: ControlView
    }
  ]
})

export default router
