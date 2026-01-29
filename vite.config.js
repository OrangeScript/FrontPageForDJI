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
    host: '0.0.0.0', 
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8080', // 无人机的真实地址
        changeOrigin: true, // 允许跨域
        secure: false,      // 如果是https的话忽略证书，这里http其实无所谓
        rewrite: (path) => path.replace(/^\/api/, '') ,
        configure: (proxy, options) => {
          
          // 1. 当代理向无人机发出请求时触发
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // 获取客户端的原始请求 URL
            const clientUrl = req.url; 
            // 获取最终发给无人机的 URL
            const targetUrl = options.target + proxyReq.path;
            
            console.log('-----------------------------------------');
            console.log('🚀 [代理发送] 浏览器请求:', clientUrl);
            console.log('🎯 [代理转发] 目标地址:', targetUrl);
            console.log('📋 [请求方法]', req.method);
            
            // 为了防止 socket hang up，这里顺便做一下“净化”
            proxyReq.setHeader('Connection', 'close');
            proxyReq.removeHeader('origin');
            proxyReq.removeHeader('referer');
          });

          // 2. 当无人机回复数据时触发
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('✅ [代理接收] 无人机响应状态码:', proxyRes.statusCode);
            console.log('-----------------------------------------');
          });

          // 3. 当发生错误时触发
          proxy.on('error', (err, req, res) => {
            console.log('❌ [代理报错] 发生错误:', err.message);
            console.log('-----------------------------------------');
          });}
      }
    }
  }
})
