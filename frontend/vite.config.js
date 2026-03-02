// 수정일: 2026-03-02
// 수정내용: 로컬 및 AWS 환경 설정 (ngrok/localtunnel 제거)

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
    host: '0.0.0.0', // 모든 네트워크 인터페이스 허용
    port: 5173,

    // 허용 호스트: 로컬 및 AWS 도메인
    allowedHosts: [
      'localhost',
      'aiarcade.kro.kr'
    ],

    proxy: {
      '/api': {
        target: process.env.VITE_API_Target || 'http://localhost:8000',
        changeOrigin: true,
        cookieDomainRewrite: "localhost"
      },
      '/media': {
        target: process.env.VITE_API_Target || 'http://localhost:8000',
        changeOrigin: true
      },
      // [수정일: 2026-02-26] 프론트엔드 소켓 연결 경로 변경에 맞춰 프록시 규칙명 업데이트
      '/api/socket.io': {
        target: process.env.VITE_API_Target || 'http://localhost:8000',
        changeOrigin: true,
        ws: true
      }
    },
    // SPA 라우팅 지원 미들웨어
    middlewares: [
      {
        name: 'spa-fallback',
        apply: 'serve',
        enforce: 'pre',
        handle(req, res, next) {
          const mainPageRequests = ['/main.html', '/index.html', '/', '/practice/logic-mirror'];
          if (req.url.startsWith('/api')) return next();
          if (req.url.includes('.') && !req.url.endsWith('.html')) return next();
          if (req.url.includes('main.html') || !req.url.includes('.')) {
            req.url = '/index.html';
          }
          next();
        }
      }
    ]
  },
  build: {
    rollupOptions: {
      input: {
        index: path.resolve(__dirname, 'index.html')
      }
    },
  }
})