// 수정일: 2026-01-23
// 수정내용: 퀘스트 기반 Logic Mirror로 교체

import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import axios from 'axios'
import './index.css'
import App from './App.vue'

// [2026-01-25] Axios 전역 인증/보안 설정: 세션 쿠키 공유 및 Django CSRF 연동
axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

// 새로운 퀘스트 기반 Logic Mirror 임포트
import PseudoPractice from './features/practice/pseudoProblem.vue'
import SystemArchitecturePractice from './features/practice/SystemArchitecturePractice.vue'
import BugHunt from './features/practice/BugHunt.vue'
import VibeCodeCleanUp from './features/practice/VibeCodeCleanUp.vue'
import OpsPractice from './features/practice/OpsPractice.vue'
import ProgressiveProblems from './features/practice/ProgressiveProblems.vue'
// [수정일: 2026-01-31] 사용하지 않는 구버전/비활성 컴포넌트 임포트 주석 처리
// import AiDetectivePractice from './features/practice/AiDetectivePractice.vue'
// import PseudoForest from './features/practice/PseudoForest.vue'
// import PseudoCompany from './features/practice/PseudoCompany.vue'
// import PseudoEmergency from './features/practice/PseudoEmergency.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: { render: () => null }
  },
  // [2026-01-27] Pseudo Practice (구 Logic Mirror) 라우트 최신화
  {
    path: '/practice/pseudo-code',
    name: 'PseudoCode',
    component: PseudoPractice
  },
  {
    path: '/practice/system-architecture',
    name: 'SystemArchitecturePractice',
    component: SystemArchitecturePractice
  },
  {
    path: '/practice/bug-hunt',
    name: 'BugHunt',
    component: BugHunt
  },
  {
    path: '/practice/vibe-cleanup',
    name: 'VibeCodeCleanUp',
    component: VibeCodeCleanUp
  },
  {
    path: '/practice/ops-practice',
    name: 'OpsPractice',
    component: OpsPractice
  },
  {
    path: '/practice/progressive-problems',
    name: 'ProgressiveProblems',
    component: ProgressiveProblems
  },
  /* [수정일: 2026-01-31] 비활성 라우트 주석 처리
  {
    path: '/practice/ai-detective',
    name: 'AiDetective',
    component: AiDetectivePractice
  },
  {
    path: '/practice/pseudo-forest',
    name: 'PseudoForest',
    component: PseudoForest
  },
  {
    path: '/practice/pseudo-company',
    name: 'PseudoCompany',
    component: PseudoCompany
  },
  {
    path: '/practice/pseudo-emergency',
    name: 'PseudoEmergency',
    component: PseudoEmergency
  },
  */
  {
    path: '/main.html',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

import {
  Gamepad2,
  Bug,
  Layers,
  Zap,
  Bot,
  BookOpen,
  Users,
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  Home,
  AlertCircle
} from 'lucide-vue-next'

const app = createApp(App)

// [2026-01-25] Lucide 아이콘을 전역 컴포넌트로 등록하여 DB 기반 동적 아이콘 렌더링 지원
app.component('gamepad-2', Gamepad2)
app.component('bug', Bug)
app.component('layers', Layers)
app.component('zap', Zap)
app.component('bot', Bot)
app.component('book-open', BookOpen)
app.component('Users', Users)
app.component('ArrowRight', ArrowRight)
app.component('ChevronLeft', ChevronLeft)
app.component('ChevronRight', ChevronRight)
app.component('Home', Home)
app.component('alert-circle', AlertCircle)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')
