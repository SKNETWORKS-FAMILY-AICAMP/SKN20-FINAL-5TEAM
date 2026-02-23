<template>
  <!-- [Phase 6] gamePhase에 따라 전체 분위기 전환 -->
  <div class="pressure-room-container" :class="'phase-' + gamePhase">
    <!-- Header: Mission Status & Timer -->
    <header class="room-header">
      <div class="mission-info">
        <span class="mission-tag" :class="gamePhase">
          {{ gamePhase === 'design' ? '🕊️ DESIGNING' : gamePhase === 'blackout' ? '🚨 BLACKOUT!' : gamePhase === 'defense' ? '⚔️ DEFENSE' : '📊 REPORT' }}
        </span>
        <h1 class="mission-title">{{ missionTitle || '트래픽 폭주 대응 아키텍처 설계' }}</h1>
      </div>
      <div class="room-stats">
        <div class="stat-item">
          <span class="label">PROGRESS</span>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progress + '%' }"></div>
          </div>
          <span class="value">{{ progress }}%</span>
        </div>
        <div class="stat-item timer" :class="{ 'warning': timeLeft < 60 }">
          <span class="label">TIME LEFT</span>
          <span class="value">{{ formatTime(timeLeft) }}</span>
        </div>
        <!-- [Phase 6] phase별 액션 버튼 -->
        <button v-if="gamePhase === 'blackout'" @click="submitFix" class="btn-fix-submit">
          ✅ 수정 완료 - 디펜스 도전
        </button>
        <button v-else @click="finishMission" class="btn-finish" :disabled="isEvaluating">
          <span v-if="!isEvaluating">FINISH MISSION</span>
          <span v-else class="loader-mini"></span>
        </button>
      </div>
    </header>

    <main class="room-layout">
      <!-- Left Panel: AI Interviewer & Chat -->
      <section class="glass-panel interviewer-panel">
        <!-- [Phase 3] Role Specific Mini Dashboard -->
        <div class="role-dashboard" :class="gameStore.userRole">
          <div class="role-info-mini">
            <span class="role-label">{{ gameStore.userRole?.toUpperCase() }} VIEW</span>
            <div class="status-dot">ACTIVE</div>
          </div>
          
          <!-- Dashboard for Architect -->
          <div v-if="gameStore.userRole === 'architect'" class="dashboard-content">
            <div class="stat-item">
              <span class="stat-label">System Structural Integrity</span>
              <div class="progress-bar-mini"><div class="fill" style="width: 85%"></div></div>
            </div>
          </div>

          <!-- Dashboard for Ops/Security -->
          <div v-if="gameStore.userRole === 'ops'" class="dashboard-content">
            <div class="stat-item">
              <span class="stat-label">Real-time Traffic (TPS)</span>
              <div class="chart-mock">1.2k / 5.0k</div>
            </div>
            <div class="stat-item">
              <span class="stat-label">Security Threat Level</span>
              <span class="stat-value low">LOW</span>
            </div>
          </div>

          <!-- Dashboard for DB/Performance -->
          <div v-if="gameStore.userRole === 'db'" class="dashboard-content">
            <div class="stat-item">
              <span class="stat-label">P99 Latency</span>
              <span class="stat-value">124ms</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">DB Cache Hit Rate</span>
              <span class="stat-value highlight">94.2%</span>
            </div>
          </div>
        </div>

        <div class="interviewer-header">
          <div class="avatar-container">
            <div class="ai-avatar" :class="interviewerStatus"></div>
            <div class="status-pulse"></div>
          </div>
          <div class="interviewer-info">
            <span class="name">{{ interviewerName || '강팀장' }}</span>
            <span class="status">{{ interviewerStatusText }}</span>
          </div>
        </div>

        <div class="chat-log" ref="chatLog">
          <div v-for="(msg, idx) in chatMessages" :key="idx" class="message" :class="msg.role">
            <div class="message-bubble">
              <span class="speaker">{{ msg.role === 'ai' ? interviewerName : 'YOU' }}</span>
              <p>{{ msg.content }}</p>
            </div>
          </div>
          <div v-if="isAiTyping" class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>

        <div class="input-area">
          <textarea 
            v-model="userResponse" 
            placeholder="면접관의 질문에 답변하거나 설계를 설명하세요..."
            @keyup.enter.exact="sendMessage"
            class="response-input"
          ></textarea>
          <button @click="sendMessage" class="btn-send" :disabled="!userResponse.trim()">
            SEND
          </button>
        </div>

        <!-- [Phase 4] In-Basket Emergency Alert Center -->
        <div v-if="myChaosAlerts.length > 0" class="in-basket-alerts">
          <div v-for="alert in myChaosAlerts" :key="alert.event_id" class="in-basket-card">
            <div class="alert-header">
              <span class="emergency-tag">URGENT REPORT</span>
              <span class="time">{{ new Date(alert.timestamp).toLocaleTimeString() }}</span>
            </div>
            <h4 class="alert-title">{{ alert.title }}</h4>
            <p class="alert-desc">{{ alert.description }}</p>
            <div class="target-roles">TARGET: <span class="role-chip">{{ alert.target_role }}</span></div>
            <div class="vfx-alert-bar"></div>
          </div>
        </div>
      </section>

      <!-- Right Panel: Live Coding Editor -->
      <!-- [수정일: 2026-02-23] 아키텍처 캔버스를 Monaco Editor 라이브 코딩으로 교체 -->
      <section class="glass-panel main-game-view" :class="{ 'editor-blackout': gamePhase === 'blackout' }">
        <div class="panel-tabs">
          <button
            v-for="tab in codeTabs"
            :key="tab.id"
            @click="activeCodeTab = tab.id"
            class="tab-btn"
            :class="{ active: activeCodeTab === tab.id }"
          >
            {{ tab.icon }} {{ tab.label }}
          </button>
        </div>

        <div class="editor-container">
          <VueMonacoEditor
            v-model:value="currentCode"
            :language="currentLanguage"
            :theme="editorTheme"
            :options="monacoOptions"
            @mount="handleEditorMount"
            class="code-editor"
          />
        </div>

        <!-- [수정일: 2026-02-23] 실시간 설계 점수 게이지 바 -->
        <div class="live-score-panel" v-if="liveScores">
          <div class="score-header">
            <span class="score-icon">📊</span>
            <span>LIVE SCORE</span>
            <span v-if="isAnalyzing" class="analyzing-badge">🔄 분석중...</span>
          </div>
          <div class="score-bars">
            <div class="score-row">
              <span class="score-label">가용성</span>
              <div class="score-bar-track">
                <div class="score-bar-fill availability" :style="{ width: liveScores.availability + '%' }"></div>
              </div>
              <span class="score-value" :class="{ low: liveScores.availability < 40 }">{{ liveScores.availability }}%</span>
            </div>
            <div class="score-row">
              <span class="score-label">확장성</span>
              <div class="score-bar-track">
                <div class="score-bar-fill scalability" :style="{ width: liveScores.scalability + '%' }"></div>
              </div>
              <span class="score-value" :class="{ low: liveScores.scalability < 40 }">{{ liveScores.scalability }}%</span>
            </div>
            <div class="score-row">
              <span class="score-label">보안</span>
              <div class="score-bar-track">
                <div class="score-bar-fill security" :style="{ width: liveScores.security + '%' }"></div>
              </div>
              <span class="score-value" :class="{ low: liveScores.security < 40 }">{{ liveScores.security }}%</span>
            </div>
            <div class="score-row">
              <span class="score-label">비용효율</span>
              <div class="score-bar-track">
                <div class="score-bar-fill cost" :style="{ width: liveScores.cost_efficiency + '%' }"></div>
              </div>
              <span class="score-value" :class="{ low: liveScores.cost_efficiency < 40 }">{{ liveScores.cost_efficiency }}%</span>
            </div>
          </div>
          <p class="score-assessment" v-if="overallAssessment">{{ overallAssessment }}</p>
        </div>

        <!-- Mission Objective -->
        <div class="mission-objectives-mini">
          <div class="objective-header">MISSION OBJECTIVE</div>
          <p>{{ gameStore.activeWarsMission?.initial_quest || '시나리오에 맞는 코드를 작성하세요.' }}</p>
        </div>
      </section>
    </main>

    <!-- [수정일: 2026-02-23] AI 동적 장애 이벤트 팝업 -->
    <transition name="fade">
      <div v-if="showChaosEvent" class="chaos-event-overlay" @click="showChaosEvent = false">
        <div class="chaos-event-card">
          <div class="chaos-event-icon">⚡</div>
          <h2 class="chaos-event-title">{{ activeChaosEvent?.title }}</h2>
          <p class="chaos-event-desc">{{ activeChaosEvent?.description }}</p>
          <div class="chaos-event-hint" v-if="activeChaosEvent?.hint">
            <span>💡</span> {{ activeChaosEvent.hint }}
          </div>
          <div class="chaos-event-target">
            🎯 대상 탭: <strong>{{ activeChaosEvent?.target_tab === 'api' ? 'API 설계' : activeChaosEvent?.target_tab === 'db' ? 'DB 스키마' : '보안 설정' }}</strong>
          </div>
          <button class="btn-fix-chaos" @click="handleChaosFixClick">
            🛠️ 코드 수정하러 가기
          </button>
        </div>
      </div>
    </transition>

    <!-- [Phase 6] 블랙아웃 경고 오버레이 -->
    <transition name="fade">
      <div v-if="gamePhase === 'blackout' && showBlackoutAlert" class="blackout-overlay" @click="showBlackoutAlert = false">
        <div class="blackout-alert-card">
          <div class="alert-icon">🚨</div>
          <h2>SYSTEM BLACKOUT</h2>
          <p>서버 3대가 동시에 다운되었습니다!<br/>원인을 파악하고 구조도를 수정하세요.</p>
          <span class="dismiss-hint">클릭하여 닫기</span>
        </div>
      </div>
    </transition>

    <!-- [Phase 5] Real-time Video Bubbles -->
    <div class="video-overlay">
      <div class="video-card me">
        <video ref="localVideo" :srcObject="localStream" autoplay muted playsinline></video>
        <span class="user-name">YOU ({{ gameStore.userRole?.toUpperCase() }})</span>
      </div>
      <div v-for="(stream, sid) in remoteStreams" :key="sid" class="video-card">
        <video :srcObject="stream" autoplay playsinline></video>
        <span class="user-name">TEAM-MATE</span>
      </div>
    </div>

    <!-- [수정일: 2026-02-23] 게임 시작 튜토리얼 오버레이 -->
    <transition name="fade">
      <div v-if="showTutorial" class="tutorial-overlay">
        <div class="tutorial-card">
          <h2 class="tutorial-title">🎮 HOW TO PLAY</h2>
          <p class="tutorial-subtitle">시스템 아키텍처 설계 서바이벌</p>

          <div class="tutorial-steps">
            <div class="tutorial-step">
              <div class="step-icon">🕊️</div>
              <div class="step-info">
                <h3>ACT 1: 설계 (3분)</h3>
                <p>우측 에디터에서 <b>API 설계 / DB 스키마 / 보안 설정</b> 탭을 전환하며 코드를 작성하세요. 시나리오에 맞는 서버 아키텍처를 설계하는 것이 목표입니다.</p>
              </div>
            </div>

            <div class="step-arrow">▼</div>

            <div class="tutorial-step alert">
              <div class="step-icon">🚨</div>
              <div class="step-info">
                <h3>ACT 2: 블랙아웃</h3>
                <p>3분 후 <b>서버 장애가 발생</b>합니다! 에디터가 빨갛게 변하고, AI 교관이 긴급 지시를 내립니다. 코드를 수정하여 장애를 복구하세요.</p>
              </div>
            </div>

            <div class="step-arrow">▼</div>

            <div class="tutorial-step defense">
              <div class="step-icon">⚔️</div>
              <div class="step-info">
                <h3>ACT 3: 디펜스</h3>
                <p>AI 교관이 당신의 설계를 <b>공격적으로 질문</b>합니다. 좌측 채팅에서 왜 이렇게 설계했는지 논리적으로 답변하세요!</p>
              </div>
            </div>
          </div>

          <div class="tutorial-tips">
            <span>💡 좌측 채팅으로 AI에게 질문 가능 | 각 탭은 독립된 파일입니다</span>
          </div>

          <button class="btn-start-game" @click="showTutorial = false">
            🚀 게임 시작
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { useGameStore } from '@/stores/game';

// [수정일: 2026-02-23] 라이브 코딩 에디터로 전환 - Monaco Editor 임포트
import { VueMonacoEditor } from '@guolao/vue-monaco-editor';
import { useWarsSocket } from './composables/useWarsSocket';
import { useWebRTC } from './composables/useWebRTC';

// [수정일: 2026-02-23] 압박 면접 게임 룸 (Screen 2) 초기 구현
const gameStore = useGameStore();
const router = useRouter();

// [수정일: 2026-02-23] 게임 시작 튜토리얼 오버레이 표시 상태
const showTutorial = ref(true);

// [수정일: 2026-02-23] AI 실시간 코드 분석 + 동적 장애 이벤트 상태
const liveScores = ref({
  availability: 0,
  scalability: 0,
  security: 0,
  cost_efficiency: 0
});
const overallAssessment = ref('');
const isAnalyzing = ref(false);
const showChaosEvent = ref(false);
const activeChaosEvent = ref(null);
const firedChaosEvents = ref([]);  // 이미 발동된 이벤트 (중복 방지)
let analysisInterval = null;

// [수정일: 2026-02-23] AI 코드 분석 실행 함수 (runAnalysisLoop에서 호출)
const triggerAnalysis = async () => {
  // 튜토리얼 표시 중이거나 리포트 단계면 분석 안 함
  if (showTutorial.value || gamePhase.value === 'report') return;

  try {
    isAnalyzing.value = true;
    const mission = gameStore.activeWarsMission;

    const response = await axios.post('/api/core/wars/analyze-code/', {
      scenario_context: mission?.context || '서비스 트래픽 급증 시나리오',
      code_files: {
        api: codeFiles.value.api,
        db: codeFiles.value.db,
        security: codeFiles.value.security
      },
      game_phase: gamePhase.value,
      previous_events: firedChaosEvents.value.map(e => e.title)
    });

    if (response.data.status === 'success') {
      const analysis = response.data.analysis;

      // 실시간 점수 업데이트
      if (analysis.scores) {
        liveScores.value = analysis.scores;
      }
      if (analysis.overall_assessment) {
        overallAssessment.value = analysis.overall_assessment;
      }

      // 취약점 2개 이상이면 장애 이벤트 발동
      const vulnCount = analysis.vulnerabilities?.length || 0;
      const chaosEvent = analysis.chaos_event;
      if (vulnCount >= 2 && chaosEvent?.should_trigger && !showChaosEvent.value) {
        const alreadyFired = firedChaosEvents.value.some(e => e.title === chaosEvent.title);
        if (!alreadyFired) {
          activeChaosEvent.value = chaosEvent;
          showChaosEvent.value = true;
          firedChaosEvents.value.push(chaosEvent);

          chatMessages.value.push({
            role: 'ai',
            content: `🚨 장애 발생! ${chaosEvent.title}\n\n${chaosEvent.description}\n\n💡 ${chaosEvent.hint}`
          });
          console.log(`[ChaosAgent] 장애 발동: ${chaosEvent.title}`);
        }
      }

      // progress 업데이트 (4개 점수 평균)
      if (analysis.scores) {
        const s = analysis.scores;
        progress.value = Math.round((s.availability + s.scalability + s.security + s.cost_efficiency) / 4);
      }
    }
  } catch (error) {
    console.warn('[ChaosAgent] 분석 API 호출 실패:', error.message);
  } finally {
    isAnalyzing.value = false;
  }
};

// [수정일: 2026-02-23] 30초마다 AI에게 코드를 보내서 분석 요청 (첫 분석은 5초 후 즉시 실행)
const runAnalysisLoop = () => {
  // 첫 분석: 5초 후 즉시 1회 실행
  setTimeout(() => triggerAnalysis(), 5000);

  // 이후 30초 간격으로 반복
  analysisInterval = setInterval(() => triggerAnalysis(), 30000);
};

// [수정일: 2026-02-23] 장애 이벤트에서 "코드 수정하러 가기" 클릭 핸들러
const handleChaosFixClick = () => {
  showChaosEvent.value = false;
  if (activeChaosEvent.value?.target_tab) {
    activeCodeTab.value = activeChaosEvent.value.target_tab;
  }
};

// [수정일: 2026-02-23] 라이브 코딩 에디터 상태
const codeTabs = ref([
  { id: 'api', icon: '🔌', label: 'API 설계', language: 'javascript' },
  { id: 'db', icon: '🗄️', label: 'DB 스키마', language: 'sql' },
  { id: 'security', icon: '🛡️', label: '보안 설정', language: 'yaml' }
]);
const activeCodeTab = ref('api');
const codeFiles = ref({ api: '', db: '', security: '' });

// [수정일: 2026-02-23] 시나리오별 맞춤 코드 템플릿 생성
const getScenarioTemplates = (scenarioId) => {
  const templates = {
    traffic_surge: {
      api: `// ===================================
// 🔥 미션: 트래픽 폭주 대응 아키텍처
// ===================================
// 현재 상황: 트래픽 10배 급증, CPU 95%, 응답 5초 초과
// 목표: 고가용성 서버 아키텍처 설계
// ===================================

const serverConfig = {
  // TODO: 서버 포트와 워커 수를 설정하세요
  port: 8080,
  workers: 1,  // ⚠️ 현재 워커가 1개뿐입니다! 수정 필요

  // TODO: 로드밸런서를 설정하세요
  loadBalancer: {
    enabled: false,  // ⚠️ 비활성화 상태! 활성화 필요
    type: '',        // round-robin? least-connections? ip-hash?
    healthCheck: '', // 헬스체크 경로
    maxRetries: 3
  },

  // TODO: 오토스케일링 정책을 추가하세요
  autoScaling: {
    enabled: false,
    minInstances: 1,
    maxInstances: 1,  // ⚠️ 최소/최대가 같으면 스케일링 불가!
    cpuThreshold: 80  // CPU 몇%에서 스케일아웃?
  },

  // TODO: 캐시 레이어를 설정하세요
  cache: {
    provider: '',  // redis? memcached?
    ttl: 0
  }
};

// TODO: CDN 설정을 추가하세요
const cdnConfig = {
  // ...
};
`,
      db: `-- ===================================
-- 🔥 미션: 트래픽 폭주 - DB 최적화
-- ===================================
-- 현재 상황: 커넥션 풀 포화, 쿼리 타임아웃 발생
-- 목표: DB 부하 분산 및 성능 최적화
-- ===================================

-- 현재 테이블 (수정이 필요합니다!)
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  amount DECIMAL(10,2),
  status VARCHAR(20),
  created_at TIMESTAMP DEFAULT NOW()
);
-- ⚠️ 인덱스가 없습니다! 조회 성능이 매우 느립니다

-- TODO: 자주 조회되는 컬럼에 인덱스를 추가하세요
-- CREATE INDEX ...

-- TODO: Read Replica를 활용한 읽기/쓰기 분리 설정
-- 읽기 전용 쿼리는 어디로 보내야 할까요?

-- TODO: 커넥션 풀 설정 (현재 max_connections: 20)
-- SET max_connections = ???;
`,
      security: `# ===================================
# 🔥 미션: 트래픽 폭주 - 보안 설정
# ===================================
# 목표: 트래픽 급증 시에도 안전한 보안 정책
# ===================================

firewall:
  rules:
    - name: allow-https
      port: 443
      protocol: tcp
      action: allow

# TODO: Rate Limiting을 설정하세요
rate_limiting:
  enabled: false  # ⚠️ 비활성화 상태!
  requests_per_minute: 0
  burst: 0

# TODO: DDoS 방어 설정을 추가하세요
ddos_protection:
  enabled: false

# TODO: CDN 보안 헤더를 추가하세요
`
    },
    db_deadlock: {
      api: `// ===================================
// ⚡ 미션: 결제 시스템 데드락 해결
// ===================================
// 현재 상황: 결제 트랜잭션에서 데드락 빈번 발생
// 목표: 데드락 없는 결제 시스템 설계
// ===================================

// 현재 결제 처리 로직 (⚠️ 데드락 발생 원인!)
const processPayment = async (orderId, userId) => {
  // TODO: 트랜잭션 격리 수준을 설정하세요
  // 현재: SERIALIZABLE (너무 엄격해서 데드락 발생)
  const isolationLevel = 'SERIALIZABLE'; // 수정 필요!

  // TODO: 락 순서를 통일하세요 (데드락 방지의 핵심!)
  // 현재 문제: A가 orders→payments 순서, B가 payments→orders 순서로 락
  await lockTable('orders');   // 1번째 락
  await lockTable('payments'); // 2번째 락

  // TODO: 타임아웃을 설정하세요
  const lockTimeout = 0; // ⚠️ 무한 대기! 타임아웃 필요

  // TODO: 재시도 로직을 추가하세요
  const maxRetries = 0; // ⚠️ 재시도 없음!

  return { status: 'processed' };
};

// TODO: 캐시 레이어를 추가하여 DB 부하를 줄이세요
// TODO: 읽기/쓰기 분리 전략을 설계하세요
`,
      db: `-- ===================================
-- ⚡ 미션: 데드락 해결 - DB 스키마
-- ===================================
-- 현재 상황: orders↔payments 간 교차 락 발생
-- 목표: 데드락 방지 스키마 설계
-- ===================================

-- 주문 테이블
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  total_amount DECIMAL(10,2) NOT NULL,
  status VARCHAR(20) DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT NOW()
);

-- 결제 테이블
CREATE TABLE payments (
  id SERIAL PRIMARY KEY,
  order_id INTEGER REFERENCES orders(id),
  amount DECIMAL(10,2) NOT NULL,
  payment_method VARCHAR(50),
  status VARCHAR(20) DEFAULT 'pending',
  processed_at TIMESTAMP
);

-- ⚠️ 현재 문제점:
-- 1. 인덱스가 없어서 풀테이블 스캔 발생
-- 2. 외래키 락으로 인한 교차 대기
-- 3. 파티셔닝 없이 모든 데이터가 단일 테이블

-- TODO: 필요한 인덱스를 추가하세요
-- CREATE INDEX idx_orders_... ON orders(...);

-- TODO: 파티셔닝 전략을 설계하세요 (날짜별? 상태별?)

-- TODO: 트랜잭션 격리 수준을 설정하세요
-- SET default_transaction_isolation = '???';
`,
      security: `# ===================================
# ⚡ 미션: 결제 시스템 - 보안 설정
# ===================================
# 목표: 결제 데이터 보안 + 데드락 방지
# ===================================

# 결제 API 보안
payment_security:
  encryption: AES-256
  pci_compliance: true

# TODO: 결제 API Rate Limiting
rate_limiting:
  payment_api:
    requests_per_minute: 0  # ⚠️ 설정 필요!
    burst: 0

# TODO: DB 접근 제어
database_access:
  read_replicas:
    - host: ""  # ⚠️ Read Replica 미설정!
  connection_pool:
    max_size: 20  # ⚠️ 충분한가요?
    timeout: 5000

# TODO: 감사 로그 설정
audit_logging:
  enabled: false  # ⚠️ 결제 데이터 변경 추적 필요!
`
    },
    security_breach: {
      api: `// ===================================
// 🛡️ 미션: 보안 침해 대응
// ===================================
// 현재 상황: SQL Injection + SSRF 동시 공격
// 목표: 즉시 방어 체계 구축
// ===================================

// 현재 API 설정 (⚠️ 보안 취약!)
const apiConfig = {
  // TODO: CORS 정책을 설정하세요
  cors: {
    origin: '*',  // ⚠️ 모든 도메인 허용! 위험!
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
  },

  // TODO: 입력값 검증을 추가하세요
  inputValidation: {
    enabled: false,  // ⚠️ SQL Injection에 취약!
    sanitizeSQL: false,
    maxBodySize: '100mb'  // ⚠️ 너무 큽니다!
  },

  // TODO: 인증/인가를 강화하세요
  auth: {
    jwtSecret: 'secret123',  // ⚠️ 약한 시크릿!
    tokenExpiry: '30d',       // ⚠️ 만료기간 너무 김!
  },

  // TODO: Rate Limiting을 설정하세요
  rateLimiting: {
    enabled: false  // ⚠️ 무제한 요청 허용!
  }
};
`,
      db: `-- ===================================
-- 🛡️ 미션: 보안 침해 - DB 보안
-- ===================================
-- 목표: DB 수준 보안 강화
-- ===================================

-- 현재 사용자 테이블 (⚠️ 보안 취약!)
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255),
  password VARCHAR(100),  -- ⚠️ 평문 저장?! 해시 필요!
  phone VARCHAR(20),       -- ⚠️ 개인정보 암호화 필요!
  role VARCHAR(20) DEFAULT 'admin'  -- ⚠️ 기본값이 admin?!
);

-- TODO: 비밀번호를 해시로 저장하도록 수정하세요
-- TODO: 개인정보 컬럼에 암호화를 적용하세요
-- TODO: role 기본값을 'user'로 변경하세요

-- TODO: 접근 로그 테이블을 만드세요
-- CREATE TABLE access_logs (...);

-- TODO: DB 사용자 권한을 최소화하세요
-- 앱용 DB 사용자는 SELECT, INSERT만!
`,
      security: `# ===================================
# 🛡️ 미션: 보안 침해 - 방어 설정
# ===================================
# 현재: SQL Injection + SSRF 공격 진행 중!
# 목표: 즉시 방어 체계 가동
# ===================================

# TODO: WAF (Web Application Firewall) 설정
waf:
  enabled: false  # ⚠️ 즉시 활성화 필요!
  rules:
    - sql_injection: false
    - xss: false
    - ssrf: false

# TODO: 네트워크 세그먼테이션
network:
  segmentation:
    public_subnet: []
    private_subnet: []
    # ⚠️ 모든 서버가 같은 네트워크!

# TODO: IP 차단 리스트
ip_blacklist:
  enabled: false
  auto_block_threshold: 0  # 비정상 요청 몇 회시 차단?

# TODO: 제로 트러스트 원칙 적용
zero_trust:
  verify_always: false  # ⚠️ 내부 통신도 검증해야!
  mutual_tls: false
`
    },
    global_expansion: {
      api: `// ===================================
// 🌐 미션: 글로벌 서비스 확장
// ===================================
// 목표: 미국/유럽/동남아 동시 론칭, 200ms 이하 응답
// ===================================

const globalConfig = {
  // TODO: 멀티 리전 설정
  regions: [
    // { name: 'ap-northeast-2', location: '서울' }
    // ⚠️ 현재 서울 리전만 있습니다!
  ],

  // TODO: Global Load Balancer 설정
  globalLoadBalancer: {
    enabled: false,  // ⚠️ 활성화 필요!
    routingPolicy: '',  // geo? latency? weighted?
  },

  // TODO: CDN 설정
  cdn: {
    provider: '',  // CloudFront? Cloudflare?
    cachePolicy: '',
    regions: []
  },

  // TODO: 데이터 복제 전략
  dataReplication: {
    strategy: '',  // active-active? active-passive?
    conflictResolution: '',  // last-write-wins? manual?
  }
};
`,
      db: `-- ===================================
-- 🌐 미션: 글로벌 확장 - DB 설계
-- ===================================
-- 목표: 멀티 리전 데이터 복제 + GDPR 준수
-- ===================================

-- 사용자 테이블 (글로벌)
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  region VARCHAR(20) NOT NULL,  -- 사용자 거주 리전
  data_residency VARCHAR(20),   -- 데이터 저장 위치 (GDPR)
  created_at TIMESTAMP DEFAULT NOW()
);

-- ⚠️ 현재 문제점:
-- 1. 단일 리전 DB만 존재
-- 2. GDPR 데이터 거주 요건 미충족
-- 3. 복제 지연 미고려

-- TODO: 리전별 파티셔닝 전략 설계
-- TODO: GDPR 준수를 위한 데이터 격리 설계
-- TODO: Cross-region 복제 설정
-- TODO: 리전별 Read Replica 설정
`,
      security: `# ===================================
# 🌐 미션: 글로벌 확장 - 보안/규정
# ===================================
# 목표: 지역별 규정 준수 + 글로벌 보안
# ===================================

# TODO: GDPR 준수 설정 (유럽)
gdpr:
  data_residency: false  # ⚠️ EU 데이터는 EU에 저장!
  right_to_deletion: false
  data_portability: false

# TODO: 리전별 방화벽
regional_firewall:
  us-east-1:
    rules: []  # ⚠️ 규칙 없음!
  eu-west-1:
    rules: []
  ap-southeast-1:
    rules: []

# TODO: Cross-region 암호화
encryption:
  in_transit: false   # ⚠️ 리전 간 통신 암호화 필요!
  at_rest: false
  key_management: ''  # AWS KMS? 자체 관리?

# TODO: DNS 보안
dns:
  dnssec: false
  failover: false
`
    }
  };

  return templates[scenarioId] || templates['traffic_surge'];
};

let editorInstance = null;

const currentCode = computed({
  get: () => codeFiles.value[activeCodeTab.value],
  set: (val) => { codeFiles.value[activeCodeTab.value] = val; }
});

const currentLanguage = computed(() => {
  return codeTabs.value.find(t => t.id === activeCodeTab.value)?.language || 'javascript';
});

const editorTheme = computed(() => {
  if (gamePhase.value === 'blackout') return 'hc-black';
  return 'vs-dark';
});

const monacoOptions = {
  fontSize: 14,
  fontFamily: 'Fira Code, Consolas, monospace',
  minimap: { enabled: false },
  scrollBeyondLastLine: false,
  lineNumbers: 'on',
  roundedSelection: true,
  wordWrap: 'on',
  padding: { top: 12 },
  renderLineHighlight: 'all',
  cursorBlinking: 'smooth',
  smoothScrolling: true
};

const handleEditorMount = (editor) => {
  editorInstance = editor;
  console.log('[Monaco] 라이브 코딩 에디터 마운트 완료');
};

// [Phase 3-5] 실시간 팀 동기화 소켓 및 WebRTC 상태 관리
const {
  isConnected: isSocketConnected,
  teamMessages,
  teamMembers,
  chaosEvents, // [Phase 4] 실시간 장애 목록
  connectSocket,
  emitCanvasUpdate,
  sendTeamChat,
  changeRole,
  disconnectSocket,
  socket // 소켓 객체 직접 접근용
} = useWarsSocket();

// [Phase 5] WebRTC 상사/팀원 화상 통화 관리
const {
  localStream,
  remoteStreams,
  initLocalStream,
  callPeer,
  setupSignaling,
  stopStreams
} = useWebRTC(socket);

const missionTitle = ref('');
const interviewerName = ref('');
const progress = ref(0);
const timeLeft = ref(600); // 10분
const interviewerStatus = ref('neutral'); // neutral, thinking, aggressive
const interviewerStatusText = ref('준비됨');
const isEvaluating = ref(false);

// [Phase 6] 3막 드라마 게임 상태 머신
const gamePhase = ref('design'); // 'design' → 'blackout' → 'defense' → 'report'
const showBlackoutAlert = ref(false);
const defenseRound = ref(0);
const maxDefenseRounds = 3;
let blackoutTimer = null;

const userResponse = ref('');
const isAiTyping = ref(false);
const chatMessages = ref([]);

// AI 분석용 코드는 자동 생성된 코드를 사용
// [Phase 4] 장애 발생 노드 ID 추출
const errorNodeIds = computed(() => {
  const ids = [];
  chaosEvents.value.forEach(event => {
    if (event.target_node_ids) {
      ids.push(...event.target_node_ids);
    }
  });
  return ids;
});

// 내 역할이 타겟인 장애만 필터링 (In-Basket용)
const myChaosAlerts = computed(() => {
  return chaosEvents.value.filter(event => 
    event.target_role === gameStore.userRole?.toUpperCase() || !event.target_role
  );
});

// 타임아웃/인터벌 관리
let timerInterval = null;

onMounted(async () => {
  // [수정일: 2026-02-23] 스토어에서 미션 데이터 불러오기 + 라이브 코딩 에디터 초기화
  if (gameStore.activeWarsMission) {
    const mission = gameStore.activeWarsMission;
    missionTitle.value = mission.mission_title;
    interviewerName.value = mission.interviewer?.name || '강팀장';

    // [수정일: 2026-02-23] 시나리오별 맞춤 코드 템플릿 적용
    const scenarioId = mission.scenario_id || 'traffic_surge';
    codeFiles.value = getScenarioTemplates(scenarioId);
    console.log(`[Editor] 시나리오 템플릿 적용: ${scenarioId}`);
    
    // 초기 메시지 설정 (라이브 코딩 가이드)
    chatMessages.value = [
      { 
        role: 'ai', 
        content: `반갑습니다. 시나리오: ${mission.context}\n\n우선 과제: ${mission.initial_quest}\n\n[GUIDE] 우측 에디터에 시나리오에 맞는 코드가 준비되어 있습니다. ⚠️ 표시된 부분을 찾아 수정하고, TODO 항목을 완성하세요. 완료 후 저에게 설명을 남겨주시면 분석을 시작하겠습니다.` 
      }
    ];

    // 소켓 연결 및 WebRTC 시그널링 설정
    connectSocket(mission.id, '이민재');
    setupSignaling();
    await initLocalStream();

    // 팀원 입장 시 WebRTC 연결 시도
    socket.value.on('user_joined', (data) => {
      if (data.sid !== socket.value.id) {
        console.log(`Starting WebRTC call to: ${data.sid}`);
        callPeer(data.sid);
      }
    });

    // [수정일: 2026-02-23] 코드 동기화 이벤트 수신
    socket.value.on('code_sync', (data) => {
      if (data.code_files) {
        // 타입별로 코드 업데이트 (내가 편집 중이 아닌 탭만)
        Object.keys(data.code_files).forEach(tabId => {
          if (tabId !== activeCodeTab.value) {
            codeFiles.value[tabId] = data.code_files[tabId];
          }
        });
      }
    });

  } else {
    // 직접 접속 등을 위한 기본 시나리오 + 기본 템플릿 적용
    missionTitle.value = '긴급 장애 대응 모의 훈련';
    interviewerName.value = 'AI 교관';
    codeFiles.value = getScenarioTemplates('traffic_surge');

    chatMessages.value = [
      {
        role: 'ai',
        content: `🕊️ 반갑습니다. 저는 오늘 여러분의 시스템 설계 역량을 평가할 AI 교관입니다.\n\n[시나리오] 서비스 트래픽이 급증하여 기존 아키텍처가 한계에 도달했습니다.\n\n[GUIDE] 우측 에디터에 준비된 코드에서 ⚠️ 표시 부분을 찾아 수정하세요. 평화로운 설계 시간이 얼마 안 남았습니다...`
      }
    ];

    // 3분 후 블랙아웃 자동 트리거
    blackoutTimer = setTimeout(() => {
      if (gamePhase.value === 'design') {
        triggerBlackout();
      }
    }, 180000);
  }

  // 타이머 작동
  timerInterval = setInterval(() => {
    if (timeLeft.value > 0) timeLeft.value--;
  }, 1000);

  // [수정일: 2026-02-23] AI 코드 분석 루프 시작 (30초마다)
  runAnalysisLoop();
});


onUnmounted(() => {
  stopStreams();
  disconnectSocket();
  if (timerInterval) clearInterval(timerInterval);
  // [수정일: 2026-02-23] AI 분석 루프 정리
  if (analysisInterval) clearInterval(analysisInterval);
});

const formatTime = (seconds) => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
};


const sendMessage = () => {
  if (!userResponse.value.trim()) return;
  
  chatMessages.value.push({ role: 'user', content: userResponse.value });
  const message = userResponse.value;
  userResponse.value = '';
  
  // AI 응답 연출
  simulateAiResponse(message);
  
  // 스크롤 동기화
  nextTick(() => {
    const chatLog = document.querySelector('.chat-log');
    if (chatLog) chatLog.scrollTop = chatLog.scrollHeight;
  });
};

// [Phase 6] 블랙아웃 트리거 - 평화로운 설계 중 갑자기 장애 발생
const triggerBlackout = () => {
  gamePhase.value = 'blackout';
  showBlackoutAlert.value = true;
  interviewerStatus.value = 'aggressive';
  interviewerStatusText.value = '긴급 상황 보고 중';
  progress.value = 40;

  // 아키텍처 캔버스에 장애 VFX 트리거
  chaosEvents.value.push({
    event_id: 'blackout_main',
    title: '🚨 CRITICAL: 다중 서버 동시 다운',
    description: '메인 서버 3대가 동시에 응답 불능 상태입니다. 로드밸런서와 DB 연결도 불안정합니다.',
    target_role: 'ALL',
    target_node_ids: ['Server', 'RDBMS', 'Load Balancer'],
    timestamp: new Date(),
    is_read: false
  });

  chatMessages.value.push({
    role: 'ai',
    content: `⚠️ 긴급 상황입니다!\n\n방금 서버 3대가 동시에 다운되었습니다. 모니터링 시스템에서 DB 연결 타임아웃과 로드밸런서 장애가 동시에 감지되었습니다.\n\n현재 구조도에서 장애 원인을 파악하고, 구조도를 강화해주세요. 시간이 없습니다!`
  });
};

// [Phase 6] 수정 완료 버튼 클릭 → 디펜스 모드 진입
const submitFix = () => {
  gamePhase.value = 'defense';
  interviewerStatus.value = 'aggressive';
  interviewerStatusText.value = '설계 공격 준비 중';
  progress.value = 65;
  defenseRound.value = 0;

  // 장애 VFX 제거
  chaosEvents.value = [];

  chatMessages.value.push({
    role: 'ai',
    content: `수정을 확인했습니다. 이제 당신의 설계 결정을 검증하겠습니다.\n\n수정하신 아키텍처에 대해 설명해주세요. 어떤 부분을 어떻게 변경했고, 왜 그렇게 판단했는지 논리적으로 말씀해주십시오. (${maxDefenseRounds}라운드 디펜스)`
  });
};

const simulateAiResponse = async (userMsg) => {
  isAiTyping.value = true;
  interviewerStatus.value = 'thinking';
  interviewerStatusText.value = gamePhase.value === 'defense' ? '반박 논리 준비 중...' : '설계 분석 중...';
  
  try {
    // [Phase 6] phase별 AI 프롬프트 분기
    let phaseContext = '';
    if (gamePhase.value === 'design') {
      phaseContext = '당신은 친절한 가이드입니다. 유저의 설계를 격려하고 부드럽게 안내하세요.';
    } else if (gamePhase.value === 'blackout') {
      phaseContext = '긴급 장애 상황입니다. 다급하고 긴박한 톤으로 장애 복구를 독촉하세요.';
    } else if (gamePhase.value === 'defense') {
      phaseContext = `디펜스 ${defenseRound.value + 1}/${maxDefenseRounds}라운드. 유저의 설계 결정을 공격적으로 반박하세요. 비용, 확장성, 장애 대응력 측면에서 도전적 질문을 하세요.`;
    }

    const response = await axios.post('/api/core/wars/pressure/', {
      context: (gameStore.activeWarsMission?.context || '기본 장애 상황') + '\n\n[AI 역할 지침]: ' + phaseContext,
      current_design: Object.entries(codeFiles.value).map(([k, v]) => `[${k}]\n${v}`).join('\n\n'),
      user_input: userMsg,
      game_phase: gamePhase.value
    });

    if (response.data.status === 'success') {
      const qData = response.data.question;
      chatMessages.value.push({ role: 'ai', content: qData.question });

      // [Phase 6] 디펜스 라운드 진행
      if (gamePhase.value === 'defense') {
        defenseRound.value++;
        progress.value = 65 + Math.round((defenseRound.value / maxDefenseRounds) * 35);
        if (defenseRound.value >= maxDefenseRounds) {
          gamePhase.value = 'report';
          chatMessages.value.push({
            role: 'ai',
            content: '디펜스가 종료되었습니다. 최종 역량 리포트를 생성합니다. "미션 종료" 버튼을 눌러주세요.'
          });
          progress.value = 100;
        }
      } else {
        if (progress.value < 100) {
          progress.value = Math.min(100, progress.value + 10);
        }
      }
    }
  } catch (error) {
    console.error('AI 응답 생성 실패:', error);
    // [Phase 6] phase별 펴백 메시지
    const fallbackMsg = gamePhase.value === 'defense'
      ? '그 방법의 단점은 무엇인가요? trade-off를 설명해주세요.'
      : '방금 그 부분에 대해 조금 더 자세히 설명해 주시겠습니까?';
    chatMessages.value.push({ role: 'ai', content: fallbackMsg });

    if (gamePhase.value === 'defense') {
      defenseRound.value++;
      if (defenseRound.value >= maxDefenseRounds) {
        gamePhase.value = 'report';
        progress.value = 100;
      }
    }
  } finally {
    isAiTyping.value = false;
    interviewerStatus.value = gamePhase.value === 'design' ? 'neutral' : 'aggressive';
    interviewerStatusText.value = gamePhase.value === 'defense'
      ? `디펜스 ${defenseRound.value}/${maxDefenseRounds} 라운드`
      : gamePhase.value === 'design' ? '가이드 모드' : '분석 중';

    nextTick(() => {
      const scrollTarget = document.querySelector('.chat-log');
      if (scrollTarget) scrollTarget.scrollTop = scrollTarget.scrollHeight;
    });
  }
};

// [Phase 3] 드래그 앤 드롭 이벤트 발생 시 팀원에게 동기화
const syncCanvas = () => {
  if (gameStore.activeWarsMission) {
    emitCanvasUpdate(gameStore.activeWarsMission.id, droppedComponents.value, connections.value);
  }
};

const handleComponentDropped = (data) => {
  onComponentDropped(data);
  syncCanvas();
};

const handleComponentMoved = (data) => {
  onComponentMoved(data);
  syncCanvas();
};

const handleComponentRenamed = (data) => {
  onComponentRenamed(data);
  syncCanvas();
};

const handleComponentDeleted = (id) => {
  onComponentDeleted(id);
  syncCanvas();
};

const handleConnectionCreated = (data) => {
  onConnectionCreated(data);
  syncCanvas();
};

const finishMission = async () => {
  if (isEvaluating.value) return;

  const confirmFinish = confirm('미션을 종료하고 최종 평가 보고서를 생성하시겠습니까?');
  if (!confirmFinish) return;

  isEvaluating.value = true;
  try {
    // 대화 기록 문자열화
    const historyText = chatMessages.value
      .map(m => `${m.role === 'ai' ? interviewerName.value : '플레이어'}: ${m.content}`)
      .join('\n\n');

    // [수정일: 2026-02-23] 최종 평가 API 호출
    // 버그 수정: mermaidCode(미정의 변수) → codeFiles(실제 작성한 코드)
    const response = await axios.post('/api/core/wars/evaluate/', {
      context: gameStore.activeWarsMission?.context || '기본 장애 상황',
      final_design: JSON.stringify(codeFiles.value),
      chat_history: historyText,
      live_scores: liveScores.value,
      chaos_events_fired: firedChaosEvents.value.map(e => e.title)
    });

    if (response.data.status === 'success') {
      gameStore.setEvaluation(response.data.evaluation, JSON.stringify(codeFiles.value));
      router.push('/practice/coduck-wars/report');
    }
  } catch (error) {
    console.error('평가 생성 실패:', error);
    alert('보고서 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
  } finally {
    isEvaluating.value = false;
  }
};

// 캔버스 컨트롤 (임시)
const zoomIn = () => {};
const zoomOut = () => {};
const resetView = () => {};

</script>

<style scoped>
/* [수정일: 2026-02-23] 압박 면접 게임 룸 스타일링 */
.pressure-room-container {
  min-height: 100vh;
  background: #030712;
  color: #f8fafc;
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  gap: 1.5rem;
  font-family: 'Inter', sans-serif;
}

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(30, 41, 59, 0.4);
  backdrop-filter: blur(12px);
  padding: 1rem 2rem;
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.mission-tag {
  font-size: 0.75rem;
  font-weight: 800;
  color: #f59e0b;
  letter-spacing: 1px;
}

.mission-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin-top: 0.25rem;
  background: linear-gradient(to right, #f8fafc, #94a3b8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.room-stats {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.btn-finish {
  background: #f8fafc;
  color: #030712;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 0.5rem;
  font-weight: 800;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-finish:hover:not(:disabled) {
  background: #38bdf8;
  transform: translateY(-2px);
}

.btn-finish:disabled {
  background: #334155;
  color: #64748b;
  cursor: not-allowed;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.stat-item .label {
  font-size: 0.7rem;
  font-weight: 700;
  color: #64748b;
}

.progress-bar {
  width: 150px;
  height: 6px;
  background: #1e293b;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #38bdf8, #818cf8);
  transition: width 0.5s ease;
}

.stat-item .value {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  font-size: 1.1rem;
}

.timer.warning .value {
  color: #ef4444;
  animation: blink 1s infinite;
}

@keyframes blink {
  50% { opacity: 0.6; }
}

.room-layout {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 1.5rem;
  flex: 1;
  min-height: 0;
}

.glass-panel {
  background: rgba(30, 41, 59, 0.3);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 1.25rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Interviewer Panel */
.interviewer-header {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(15, 23, 42, 0.4);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.avatar-container {
  position: relative;
}

.ai-avatar {
  width: 50px;
  height: 50px;
  background: #334155;
  border-radius: 50%;
  border: 2px solid #38bdf8;
}

.ai-avatar.thinking { border-color: #f59e0b; }
.ai-avatar.aggressive { border-color: #ef4444; box-shadow: 0 0 10px rgba(239, 68, 68, 0.3); }

.status-pulse {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 12px;
  height: 12px;
  background: #10b981;
  border-radius: 50%;
  border: 2px solid #030712;
}

.interviewer-info .name {
  display: block;
  font-weight: 700;
  font-size: 1.1rem;
}

.interviewer-info .status {
  font-size: 0.8rem;
  color: #94a3b8;
}

.chat-log {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.message {
  max-width: 85%;
}

.message.ai { align-self: flex-start; }
.message.user { align-self: flex-end; }

.message-bubble {
  padding: 1rem;
  border-radius: 1rem;
  font-size: 0.95rem;
  line-height: 1.6;
}

.ai .message-bubble {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(56, 189, 248, 0.2);
  border-top-left-radius: 0;
}

.user .message-bubble {
  background: linear-gradient(135deg, #1e293b, #334155);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-top-right-radius: 0;
}

.speaker {
  font-size: 0.7rem;
  font-weight: 800;
  color: #38bdf8;
  display: block;
  margin-bottom: 0.4rem;
}

.user .speaker { color: #818cf8; }

.input-area {
  padding: 1.5rem;
  background: rgba(15, 23, 42, 0.4);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.response-input {
  width: 100%;
  height: 80px;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.75rem;
  padding: 0.75rem;
  color: #f8fafc;
  resize: none;
  font-size: 0.9rem;
}

.btn-send {
  padding: 0.75rem;
  background: #38bdf8;
  color: #030712;
  border-radius: 0.5rem;
  font-weight: 700;
  border: none;
  cursor: pointer;
}

/* [Phase 2] 새로운 게임 레이아웃 스타일 */
.main-game-view {
  display: flex;
  flex-direction: column;
  position: relative;
  border: 1px solid rgba(0, 243, 255, 0.2);
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
}

.game-content-area {
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
  background: #020617;
}

.palette-container {
  width: 280px;
  background: rgba(15, 23, 42, 0.9);
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  overflow-y: auto;
  z-index: 20;
}

.canvas-container {
  flex: 1;
  position: relative;
  background-image: 
    radial-gradient(circle at 2px 2px, rgba(255, 255, 255, 0.05) 1px, transparent 0);
  background-size: 30px 30px;
}

.canvas-hint {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
  text-align: center;
  color: rgba(148, 163, 184, 0.4);
  font-weight: 700;
  letter-spacing: 1px;
}

.mission-objectives-mini {
  padding: 1rem 1.5rem;
  background: rgba(15, 23, 42, 0.6);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.objective-header {
  font-size: 0.7rem;
  font-weight: 800;
  color: #f59e0b;
  margin-bottom: 0.25rem;
}

.mission-objectives-mini p {
  font-size: 0.85rem;
  color: #94a3b8;
  line-height: 1.4;
}

.tab-btn.connection-mode.active {
  background: #f59e0b;
  color: #030712;
  border-radius: 4px;
  padding: 2px 8px;
}

.tab-btn.clear-btn {
  color: #ef4444;
  margin-left: auto;
}

.loader-mini {
  width: 16px;
  height: 16px;
  border: 2px solid #030712;
  border-bottom-color: transparent;
  border-radius: 50%;
  display: inline-block;
  animation: rotation 1s linear infinite;
}

@keyframes rotation {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* [Phase 3] Role Specific Dashboard Styles */
.role-dashboard {
  padding: 1rem;
  background: rgba(15, 23, 42, 0.8);
  border-bottom: 2px solid rgba(255, 255, 255, 0.05);
  margin-bottom: 1rem;
}

.role-dashboard.architect { border-color: #38bdf8; }
.role-dashboard.ops { border-color: #ef4444; }
.role-dashboard.db { border-color: #f59e0b; }

.role-info-mini {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.role-label {
  font-size: 0.65rem;
  font-weight: 900;
  color: #94a3b8;
  letter-spacing: 1.5px;
}

.status-dot {
  font-size: 0.6rem;
  color: #10b981;
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-dot::before {
  content: '';
  width: 6px;
  height: 6px;
  background: #10b981;
  border-radius: 50%;
  box-shadow: 0 0 5px #10b981;
}

.dashboard-content {
  display: flex;
  gap: 1.5rem;
}

.stat-item {
  flex: 1;
}

.stat-label {
  display: block;
  font-size: 0.6rem;
  color: #64748b;
  margin-bottom: 0.25rem;
  text-transform: uppercase;
}

.stat-value {
  font-size: 0.9rem;
  font-weight: 800;
}

.stat-value.highlight { color: #f59e0b; }
.stat-value.low { color: #10b981; }

.progress-bar-mini {
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar-mini .fill {
  height: 100%;
  background: #38bdf8;
}

.chart-mock {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  color: #ef4444;
}
/* [Phase 4] In-Basket Emergency Alerts Styles */
.in-basket-alerts {
  position: absolute;
  top: 1rem;
  right: 1rem;
  left: 1rem;
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  pointer-events: none;
}

.in-basket-card {
  pointer-events: auto;
  background: rgba(127, 29, 29, 0.85); /* Dark Red Glass */
  backdrop-filter: blur(12px);
  border: 1px solid #ef4444;
  border-radius: 0.75rem;
  padding: 1.25rem;
  box-shadow: 0 0 30px rgba(239, 68, 68, 0.3);
  position: relative;
  overflow: hidden;
  animation: slideInRight 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes slideInRight {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

.alert-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.emergency-tag {
  font-size: 0.6rem;
  font-weight: 900;
  color: #fff;
  background: #b91c1c;
  padding: 2px 8px;
  border-radius: 4px;
  letter-spacing: 1px;
}

.alert-title {
  font-size: 1rem;
  font-weight: 800;
  color: #fff;
  margin: 0.25rem 0;
}

.alert-desc {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.4;
  margin-bottom: 0.75rem;
}

.role-chip {
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  color: #fb923c; /* Orange for roles */
  font-weight: 700;
}

.vfx-alert-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: #fff;
  width: 100%;
  animation: drainBar 15s linear forwards;
}

@keyframes drainBar {
  from { width: 100%; }
  to { width: 0%; }
}

/* [Phase 5] Video Overlay Styles */
.video-overlay {
  position: absolute;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  z-index: 200;
  pointer-events: none;
}

.video-card {
  pointer-events: auto;
  width: 180px;
  height: 120px;
  background: #000;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  overflow: hidden;
  position: relative;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  transition: all 0.3s ease;
}

.video-card:hover {
  transform: scale(1.05);
  border-color: #38bdf8;
}

.video-card.me {
  width: 140px;
  height: 90px;
  border-color: #10b981;
}

.video-card video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-card .user-name {
  position: absolute;
  bottom: 0.5rem;
  left: 0.5rem;
  font-size: 0.6rem;
  font-weight: 800;
  background: rgba(0, 0, 0, 0.6);
  padding: 2px 6px;
  border-radius: 4px;
}

/* ============================================= */
/* [Phase 6] 3막 드라마 게임 루프 스타일 시스템   */
/* ============================================= */

/* ACT 1: 평화로운 설계 모드 */
.phase-design {
  background: #0a1628;
  transition: background 1s ease;
}
.phase-design .mission-tag {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

/* ACT 2: 블랙아웃 모드 - 경고 */
.phase-blackout {
  background: #1a0808;
  transition: background 0.5s ease;
}
.phase-blackout .room-header {
  border-bottom-color: #ef4444;
}
.phase-blackout .mission-tag {
  background: rgba(239, 68, 68, 0.3);
  color: #ef4444;
  animation: emergencyFlash 0.8s infinite;
}

@keyframes emergencyFlash {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* ACT 3: 설계 디펜스 모드 - 전투 */
.phase-defense {
  background: #0f0a1a;
  transition: background 1s ease;
}
.phase-defense .mission-tag {
  background: rgba(139, 92, 246, 0.3);
  color: #a78bfa;
}

/* ACT 4: 리포트 완료 모드 */
.phase-report {
  background: #030712;
}
.phase-report .mission-tag {
  background: rgba(56, 189, 248, 0.2);
  color: #38bdf8;
}

/* 블랙아웃 경고 오버레이 */
.blackout-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  cursor: pointer;
}

.blackout-alert-card {
  text-align: center;
  padding: 3rem 4rem;
  border: 2px solid #ef4444;
  border-radius: 1.5rem;
  background: rgba(30, 10, 10, 0.95);
  animation: alertShake 0.5s ease-in-out;
}

@keyframes alertShake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-10px); }
  40% { transform: translateX(10px); }
  60% { transform: translateX(-6px); }
  80% { transform: translateX(6px); }
}

.blackout-alert-card .alert-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.blackout-alert-card h2 {
  font-size: 2rem;
  font-weight: 900;
  color: #ef4444;
  letter-spacing: 0.3em;
  margin-bottom: 1rem;
}

.blackout-alert-card p {
  font-size: 1.1rem;
  color: #fca5a5;
  line-height: 1.8;
}

.blackout-alert-card .dismiss-hint {
  display: block;
  margin-top: 1.5rem;
  color: #666;
  font-size: 0.8rem;
}

/* 수정 완료 버튼 */
.btn-fix-submit {
  padding: 0.7rem 1.5rem;
  border: 2px solid #10b981;
  border-radius: 0.5rem;
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  font-weight: 800;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: fixButtonGlow 1.5s infinite;
}

.btn-fix-submit:hover {
  background: rgba(16, 185, 129, 0.3);
  transform: scale(1.05);
}

@keyframes fixButtonGlow {
  0%, 100% { box-shadow: 0 0 5px rgba(16, 185, 129, 0.3); }
  50% { box-shadow: 0 0 20px rgba(16, 185, 129, 0.6); }
}

/* ============================================= */
/* [수정일: 2026-02-23] Monaco Editor 라이브 코딩  */
/* ============================================= */

.editor-container {
  flex: 1;
  min-height: 400px;
  border-radius: 0.75rem;
  overflow: hidden;
  border: 1px solid #334155;
  transition: border-color 0.5s ease;
}

.code-editor {
  width: 100%;
  height: 100%;
  min-height: 400px;
}

/* 블랙아웃 시 에디터 빨간 테두리 */
.editor-blackout .editor-container {
  border-color: #ef4444;
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
  animation: editorAlarm 1s infinite;
}

@keyframes editorAlarm {
  0%, 100% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.2); }
  50% { box-shadow: 0 0 30px rgba(239, 68, 68, 0.5); }
}

/* 탭 시스템 */
.panel-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tab-btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid #334155;
  color: #94a3b8;
  font-weight: 600;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn.active {
  background: rgba(56, 189, 248, 0.15);
  border-color: #38bdf8;
  color: #38bdf8;
}

.tab-btn:hover:not(.active) {
  border-color: #64748b;
  color: #cbd5e1;
}

/* ============================================= */
/* [수정일: 2026-02-23] 게임 시작 튜토리얼 오버레이 */
/* ============================================= */

.tutorial-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(8px);
}

.tutorial-card {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 1.5rem;
  padding: 2.5rem;
  max-width: 560px;
  width: 90%;
  box-shadow: 0 0 40px rgba(56, 189, 248, 0.15);
}

.tutorial-title {
  font-size: 1.8rem;
  text-align: center;
  color: #38bdf8;
  margin-bottom: 0.25rem;
}

.tutorial-subtitle {
  text-align: center;
  color: #94a3b8;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.tutorial-steps {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tutorial-step {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.75rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid #1e293b;
}

.tutorial-step.alert {
  border-color: rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.05);
}

.tutorial-step.defense {
  border-color: rgba(168, 85, 247, 0.3);
  background: rgba(168, 85, 247, 0.05);
}

.step-icon {
  font-size: 1.8rem;
  flex-shrink: 0;
}

.step-info h3 {
  color: #e2e8f0;
  font-size: 0.95rem;
  margin-bottom: 0.25rem;
}

.step-info p {
  color: #94a3b8;
  font-size: 0.8rem;
  line-height: 1.4;
}

.step-info b {
  color: #38bdf8;
}

.step-arrow {
  text-align: center;
  color: #475569;
  font-size: 0.8rem;
}

.tutorial-tips {
  margin-top: 1rem;
  padding: 0.6rem;
  background: rgba(56, 189, 248, 0.08);
  border-radius: 0.5rem;
  text-align: center;
}

.tutorial-tips span {
  color: #94a3b8;
  font-size: 0.75rem;
}

.btn-start-game {
  display: block;
  width: 100%;
  margin-top: 1.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, #38bdf8, #818cf8);
  border: none;
  border-radius: 0.75rem;
  color: white;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-start-game:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(56, 189, 248, 0.4);
}

/* ============================================= */
/* [수정일: 2026-02-23] 실시간 점수 게이지 바     */
/* ============================================= */

.live-score-panel {
  padding: 0.75rem 1rem;
  background: rgba(15, 23, 42, 0.8);
  border-top: 1px solid rgba(56, 189, 248, 0.15);
}

.score-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.7rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.score-icon { font-size: 1rem; }

.analyzing-badge {
  margin-left: auto;
  color: #38bdf8;
  animation: pulse 1s infinite;
}

.score-bars { display: flex; flex-direction: column; gap: 0.35rem; }

.score-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.score-label {
  width: 50px;
  font-size: 0.65rem;
  color: #64748b;
  text-align: right;
}

.score-bar-track {
  flex: 1;
  height: 6px;
  background: rgba(30, 41, 59, 0.8);
  border-radius: 3px;
  overflow: hidden;
}

.score-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 1s ease;
}

.score-bar-fill.availability { background: linear-gradient(90deg, #22d3ee, #06b6d4); }
.score-bar-fill.scalability { background: linear-gradient(90deg, #a78bfa, #8b5cf6); }
.score-bar-fill.security { background: linear-gradient(90deg, #34d399, #10b981); }
.score-bar-fill.cost { background: linear-gradient(90deg, #fbbf24, #f59e0b); }

.score-value {
  width: 32px;
  font-size: 0.65rem;
  font-weight: 700;
  color: #e2e8f0;
  text-align: right;
}

.score-value.low { color: #ef4444; }

.score-assessment {
  margin-top: 0.4rem;
  font-size: 0.65rem;
  color: #64748b;
  font-style: italic;
}

/* ============================================= */
/* [수정일: 2026-02-23] AI 동적 장애 이벤트 팝업  */
/* ============================================= */

.chaos-event-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(127, 29, 29, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9998;
  backdrop-filter: blur(4px);
}

.chaos-event-card {
  background: linear-gradient(135deg, rgba(30, 10, 10, 0.98), rgba(50, 20, 20, 0.95));
  border: 2px solid rgba(239, 68, 68, 0.6);
  border-radius: 1.5rem;
  padding: 2.5rem;
  max-width: 480px;
  width: 90%;
  text-align: center;
  box-shadow: 0 0 60px rgba(239, 68, 68, 0.3);
  animation: shake 0.5s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-8px); }
  40% { transform: translateX(8px); }
  60% { transform: translateX(-4px); }
  80% { transform: translateX(4px); }
}

.chaos-event-icon {
  font-size: 3rem;
  animation: pulse 1s infinite;
}

.chaos-event-title {
  color: #ef4444;
  font-size: 1.4rem;
  margin: 0.5rem 0;
}

.chaos-event-desc {
  color: #fca5a5;
  font-size: 0.85rem;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.chaos-event-hint {
  background: rgba(250, 204, 21, 0.1);
  border: 1px solid rgba(250, 204, 21, 0.3);
  border-radius: 0.5rem;
  padding: 0.6rem;
  color: #fde68a;
  font-size: 0.8rem;
  margin-bottom: 0.75rem;
}

.chaos-event-target {
  color: #94a3b8;
  font-size: 0.75rem;
  margin-bottom: 1rem;
}

.chaos-event-target strong { color: #38bdf8; }

.btn-fix-chaos {
  width: 100%;
  padding: 0.8rem;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  border: none;
  border-radius: 0.75rem;
  color: white;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-fix-chaos:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* fade 트랜지션 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
