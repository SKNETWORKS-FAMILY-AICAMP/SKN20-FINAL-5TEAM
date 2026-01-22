// 수정일: 2026-01-21
// 수정내용: Vue 앱 엔트리 포인트 설정 (Pinia, Router 초기화, Logic Mirror 추가)

import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import axios from 'axios' // [수정일: 2026-01-22] axios 임포트 추가 (Antigravity)
import App from './App.vue'

// [수정일: 2026-01-22] 새로고침 시 로그인 유지를 위해 세션 쿠키 전달 허용 (Antigravity)
axios.defaults.withCredentials = true
import CodePracticeLogicMirror from './features/practice/CodePracticeLogicMirror.vue'
import SystemArchitecturePractice from './features/practice/SystemArchitecturePractice.vue'
import DebugPractice from './features/practice/DebugPractice.vue'
import OpsPractice from './features/practice/OpsPractice.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: App
  },
  {
    path: '/practice/logic-mirror',
    name: 'CodePracticeLogicMirror',
    component: CodePracticeLogicMirror
  },
  {
    path: '/practice/system-architecture',
    name: 'SystemArchitecturePractice',
    component: SystemArchitecturePractice
  },
  {
    path: '/practice/debug-practice',
    name: 'DebugPractice',
    component: DebugPractice
  },
  {
    path: '/practice/ops-practice',
    name: 'OpsPractice',
    component: OpsPractice
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
