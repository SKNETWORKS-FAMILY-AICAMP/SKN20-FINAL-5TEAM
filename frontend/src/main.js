// 수정일: 2026-01-23
// 수정내용: 퀘스트 기반 Logic Mirror로 교체

import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import axios from 'axios'
import App from './App.vue'

// [2026-01-25] Axios 전역 인증/보안 설정: 세션 쿠키 공유 및 Django CSRF 연동
axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

// 새로운 퀘스트 기반 Logic Mirror 임포트
import PseudocodePractice from './features/practice/pseudocode/PseudocodePractice.vue'
import SystemArchitecturePractice from './features/practice/architecture/SystemArchitecturePractice.vue'
import BugHunt from './features/practice/bughunt/BugHunt.vue'
// import OpsPractice from './features/practice/OpsPractice.vue'
import ManagementView from './features/admin/ManagementView.vue'
import MyRecordsView from './features/my-records/MyRecordsView.vue'
import AICoach from './features/ai-coach/AICoach.vue'
import MockInterview from './features/interview/MockInterview.vue'
import MissionBriefing from './features/wars/MissionBriefing.vue'
import PressureInterviewRoom from './features/wars/PressureInterviewRoom.vue'
import GrowthReport from './features/wars/GrowthReport.vue'
import WarLobby from './features/wars/WarLobby.vue'
// [수정일: 2026-02-23] Coduck Wars 미니게임 모드 추가
import WarsModeSelect from './features/wars/WarsModeSelect.vue'
import ArchDrawQuiz from './features/wars/minigames/ArchDrawQuiz.vue'
// [수정일: 2026-02-24] SpeedArchBuilder → LogicRun으로 교체
import LogicRun from './features/wars/minigames/LogicRun.vue'
import ArchBattle from './features/wars/minigames/ArchBattle.vue'

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
  /*
    {
      path: '/practice/ops-practice',
      name: 'OpsPractice',
      component: OpsPractice
    },
  */
  {
    path: '/practice/coduck-wars',
    name: 'CoduckWars',
    component: WarsModeSelect
  },
  {
    path: '/practice/coduck-wars/briefing',
    name: 'MissionBriefing',
    component: MissionBriefing
  },
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
    path: '/practice/coduck-wars/arch-battle',
    name: 'ArchBattle',
    component: ArchBattle
  },
  {
    path: '/practice/coduck-wars/battle',
    name: 'PressureInterviewRoom',
    component: PressureInterviewRoom
  },
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
    path: '/management/progress',
    name: 'Management',
    component: ManagementView
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
