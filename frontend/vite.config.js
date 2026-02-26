// 수정일: 2026-02-25
// 수정내용: ngrok 접속 허용 및 로컬 환경 최적화 (localhost 설정)

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

    // [수정: 2026-02-25] 명시적 호스트 허용으로 ngrok 도메인 등록하여 ngrok 에러 방지 및 보안 강화
    // [추가: 2026-02-26] AWS 도메인 (aiarcade) 접속 허용
    allowedHosts: [
      'flockier-harlee-ontogenically.ngrok-free.dev',
      'localhost',
      '.ngrok-free.dev',
      'aiarcade.kro.kr'
    ],

    // [추가: 2026-02-25] ngrok (https) 환경에서 웹소켓 통신(HMR)을 위한 설정 
    // hmr: {
    //   host: 'flockier-harlee-ontogenically.ngrok-free.dev',
    //   port: 443,
    //   clientPort: 443,
    //   protocol: 'wss'
    // },

    // watch: {
    //   usePolling: true,
    //   interval: 1000,
    // },
    // [수정] target을 localhost로 변경하여 장소에 상관없이 내 컴퓨터의 백엔드와 통신합니다.
    proxy: {
      '/api': {
        target: process.env.VITE_API_Target || 'http://localhost:8000',
        changeOrigin: true,
        cookieDomainRewrite: ""
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