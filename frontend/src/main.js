// 수정일: 2026-01-23
// 수정내용: 퀘스트 기반 Logic Mirror로 교체

import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import axios from 'axios'
import './index.css'
import App from './App.vue'

axios.defaults.withCredentials = true

// 새로운 퀘스트 기반 Logic Mirror 임포트
import LogicMirror from './features/practice/support/unit1/logic-mirror/LogicMirror.vue'
import SystemArchitecturePractice from './features/practice/SystemArchitecturePractice.vue'
import BugHunt from './features/practice/BugHunt.vue'
import VibeCodeCleanUp from './features/practice/VibeCodeCleanUp.vue'
import OpsPractice from './features/practice/OpsPractice.vue'

const routes = [
  // Home route removed - App.vue handles root path directly
  // [2026-01-24] 라우트 기반 모달을 위한 Logic Mirror 경로 등록 (App.vue에서 감시하여 모달 처리)
  {
    path: '/practice/logic-mirror',
    name: 'LogicMirror',
    component: { render: () => null } // 실제 컴포넌트는 GlobalModals에서 렌더링
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
    path: '/main.html',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')
