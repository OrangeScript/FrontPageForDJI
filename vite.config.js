import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    // 这里配置反向代理
    host: '0.0.0.0', // ✅ 允许远程访问的关键！不加这个，你在远程打不开网页
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://10.87.49.48:8080', // 无人机的真实地址
        changeOrigin: true, // 允许跨域
        secure: false,      // 如果是https的话忽略证书，这里http其实无所谓
        // 关键步骤：重写路径
        // 浏览器发的是 /api/send/takeoff
        // 转发给无人机变成 /send/takeoff (因为Python端只认这个)
        rewrite: (path) => path.replace(/^\/api/, '') 
      }
    }
  }
})
