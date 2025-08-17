import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        rewrite: (path) => {
          // 健康检查：/api/healthz/* -> /healthz/
          if (path.startsWith('/api/healthz')) {
            return '/healthz/'
          }
          // 其他 /api/* 保持 /api/* 前缀
          return path
        },
      },
      '/ai': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
        rewrite: (path) => {
          // 移除 /ai 前缀，直接转发到 AI 服务
          return path.replace(/^\/ai/, '')
        }
      }
    }
  }
})