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
    // [수정일: 2026-01-21] 백엔드 API와의 연동을 위한 Proxy 설정 추가
    proxy: {
      '/api': {
        target: process.env.VITE_API_Target || 'http://backend:8000',
        changeOrigin: true,
        // [수정일: 2026-01-22] 백엔드에서 보낸 쿠키 도메인(backend)을 localhost로 리라이트 (Antigravity)
        cookieDomainRewrite: "localhost"
      }
    },
    // [수정일: 2026-01-21] SPA 라우팅을 위한 미들웨어 추가 (main.html 경로 지원)
    middlewares: [
      {
        name: 'spa-fallback',
        apply: 'serve',
        enforce: 'pre',
        handle(req, res, next) {
          // 메인 페이지 요청들
          const mainPageRequests = [
            '/main.html',
            '/index.html',
            '/',
            '/practice/logic-mirror',
          ];

          // API 요청 제외
          if (req.url.startsWith('/api')) {
            return next();
          }

          // 정적 파일 제외 (확장자가 있는 파일)
          if (req.url.includes('.') && !req.url.endsWith('.html')) {
            return next();
          }

          // main.html 또는 라우트 요청이면 index.html로 리다이렉트
          if (req.url.includes('main.html') || !req.url.includes('.')) {
            req.url = '/index.html';
          }

          next();
        }
      }
    ]
  },
  build: {
    // [수정일: 2026-02-04] main.html 접근을 위해 rollupOptions input 수정
    rollupOptions: {
      input: {
        index: path.resolve(__dirname, 'index.html'),
        main: path.resolve(__dirname, 'main.html'),
      }
    },
  }
})

