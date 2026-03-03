import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import axios from 'axios'
import App from './App.vue'

// [2026-01-25] Axios 전역 인증/보안 설정: 세션 쿠키 공유 및 Django CSRF 연동
axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
// [2026-02-25] Nginx 배포 환경을 위한 전역 Base URL 설정
axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || ''

import PseudocodePractice from './features/practice/pseudocode/PseudocodePractice.vue'
import SystemArchitecturePractice from './features/practice/architecture/SystemArchitecturePractice.vue'
import BugHunt from './features/practice/bughunt/BugHunt.vue'
import ManagementView from './features/admin/ManagementView.vue'
import MyRecordsView from './features/my-records/MyRecordsView.vue'
import AICoach from './features/ai-coach/AICoach.vue'
import MockInterview from './features/interview/MockInterview.vue'
// [수정일: 2026-02-27] PressureInterviewRoom.vue 파일 삭제 및 사용 중지에 따른 임포트 제거
import GrowthReport from './features/wars/GrowthReport.vue'
import WarLobby from './features/wars/WarLobby.vue'
// [수정일: 2026-02-23] Coduck Wars 미니게임 모드 추가
import WarsModeSelect from './features/wars/WarsModeSelect.vue'
import ArchDrawQuiz from './features/wars/minigames/ArchDrawQuiz.vue'
// [수정일: 2026-02-24] SpeedArchBuilder → LogicRun으로 교체
import LogicRun from './features/wars/minigames/LogicRun.vue'
// [추가일: 2026-02-25] 신규 1:1 디펜스 게임 Bug-Bubble Monster
import BugBubbleMonster from './features/wars/minigames/BugBubbleMonster.vue'
// [수정일: 2026-02-25] 미사용 ArchBattle 컴포넌트 제거
// import ArchBattle from './features/wars/minigames/ArchBattle.vue'

// [수정일: 2026-02-26] 로그 뷰어화면 임포트
import LogViewer from './features/admin/LogViewer.vue'


const routes = [
  {
    path: '/',
    name: 'Home',
    component: { render: () => null }
  },
  {
    path: '/practice/pseudo-code',
    name: 'PseudoCode',
    component: PseudocodePractice
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
    path: '/practice/coduck-wars',
    name: 'CoduckWars',
    component: WarsModeSelect
  },
  // [삭제: 2026-02-26] 아키텍처 서바이벌(MissionBriefing) 삭제
  // [수정일: 2026-02-23] 미니게임 모드 라우트
  {
    path: '/practice/coduck-wars/draw-quiz',
    name: 'ArchDrawQuiz',
    component: ArchDrawQuiz
  },
  // [수정일: 2026-02-24] speed-build → logic-run 경로 변경, LogicRun 컴포넌트 연결
  {
    path: '/practice/coduck-wars/logic-run',
    name: 'LogicRun',
    component: LogicRun
  },
  {
    path: '/practice/coduck-wars/bug-bubble',
    name: 'BugBubbleMonster',
    component: BugBubbleMonster
  },

  // [수정일: 2026-02-27] 압박 면접 방(PressureInterviewRoom)을 삭제함에 따라 라우터 경로도 함께 정리했습니다.
  {
    path: '/practice/coduck-wars/report',
    name: 'GrowthReport',
    component: GrowthReport
  },
  {
    path: '/practice/coduck-wars/lobby',
    name: 'WarLobby',
    component: WarLobby
  },
  {
    path: '/management/progress',
    name: 'Management',
    component: ManagementView
  },
  {
    path: '/management/logs',
    name: 'LogViewer',
    component: LogViewer
  },
  {
    path: '/my-records',
    name: 'MyRecords',
    component: MyRecordsView
  },
  {
    path: '/coach',
    name: 'AICoach',
    component: AICoach
  },
  {
    path: '/interview',
    name: 'MockInterview',
    component: MockInterview
  },
  {
    path: '/practice/',
    redirect: '/practice/pseudo-code'
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
  AlertCircle,
  Lock,
  CheckCircle
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
app.component('lock', Lock)
app.component('check-circle', CheckCircle)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')
