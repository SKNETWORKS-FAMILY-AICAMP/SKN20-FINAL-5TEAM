// 수정일: 2026-01-21
// 수정내용: Vite SPA 라우팅 설정 (Vue Router 히스토리 모드 지원)

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0', // Docker 환경 접속 허용
    port: 5173,
    allowedHosts: ['coduck-frontend.loca.lt'],
    watch: {
      usePolling: true,
      interval: 1000,
    },
    // [수정일: 2026-01-21] 백엔드 API와의 연동을 위한 Proxy 설정 추가
    proxy: {
      '/api': {
        target: process.env.VITE_API_Target || 'http://127.0.0.1:8000',
        changeOrigin: true,
        cookieDomainRewrite: "localhost"
      },
      '/media': {
        target: process.env.VITE_API_Target || 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/socket.io': {
        target: process.env.VITE_API_Target || 'http://127.0.0.1:8000',
        changeOrigin: true,
        ws: true
      }
    },
  },
})

