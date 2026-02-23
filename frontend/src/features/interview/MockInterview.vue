<template>
  <div class="mock-interview-page">
    <!-- 오류 배너 -->
    <div v-if="error" class="global-error-banner">
      {{ error }}
      <button @click="error = ''">✕</button>
    </div>

    <!-- Phase 1: 채용공고 선택 -->
    <transition name="fade">
      <div v-if="phase === 'select'" class="select-wrapper">
        <button class="btn-history" @click="phase = 'history'">📋 면접 기록</button>
        <JobPostingSelector @start="onStartSession" />
      </div>
    </transition>

    <!-- Phase 5: 면접 기록 -->
    <transition name="fade">
      <div v-if="phase === 'history'" class="history-layout">
        <InterviewHistory @back="phase = 'select'" />
      </div>
    </transition>

    <!-- Phase 2: 세션 로딩 -->
    <transition name="fade">
      <div v-if="phase === 'loading'" class="loading-overlay">
        <div class="loading-content">
          <div class="loading-spinner-ring"></div>
          <p class="loading-text">면접 준비 중입니다...</p>
          <p class="loading-sub">취약점 분석 및 맞춤 면접 계획을 세우고 있어요.</p>
          
          <!-- [수정일: 2026-02-23] [vision] 비전 엔진 로딩 상태 표시 -->
          <div v-if="!visionSystem.isReady.value && !visionSystem.initError.value" class="vision-init-loader mt-4">
             <div class="flex items-center justify-center gap-2 text-indigo-300 text-xs">
                <span class="animate-pulse">●</span> AI 비전 분석 모듈 가동 중...
             </div>
          </div>
          <div v-if="visionSystem.initError.value" class="text-red-400 text-xs mt-4">
            {{ visionSystem.initError.value }} (분석 없이 진행됨)
          </div>
        </div>
      </div>
    </transition>

    <!-- Phase 3: 면접 진행 -->
    <transition name="fade">
      <div v-if="phase === 'interview'" class="interview-layout">
        <!-- 왼쪽: 면접관 패널 -->
        <div class="interviewer-panel">
          <!-- 웹캠 영역 -->
          <div class="iv-webcam-wrap">
            <WebcamDisplay ref="webcamRef" @ready="onWebcamReady" />
          </div>

          <div class="iv-label">면접관</div>
          <div class="iv-topic">{{ currentTopic || currentSlot }}</div>

          <div class="iv-progress-dots">
            <span
              v-for="i in totalSlots"
              :key="i"
              class="iv-dot"
              :class="{ 'iv-dot--done': i <= slotsCleared, 'iv-dot--active': i === slotsCleared + 1 }"
            ></span>
          </div>

          <div class="iv-turn-info">{{ currentTurn }}번째 질문</div>

          <div class="iv-status" :class="{ 'iv-status--active': isStreaming }">
            <span v-if="isStreaming">
              <span class="iv-blink">●</span> 질문 생성 중...
            </span>
            <span v-else>답변 대기 중</span>
          </div>
        </div>

        <!-- 오른쪽: 채팅 패널 -->
        <div class="chat-panel">
          <InterviewChat
            :messages="messages"
            :is-streaming="isStreaming"
            :has-streamed-token="hasStreamedToken"
            :current-slot="currentSlot"
            :current-topic="currentTopic"
            :current-turn="currentTurn"
            :total-slots="totalSlots"
            :slots-cleared="slotsCleared"
            :slot-progress="slotProgress"
            @submit="onSubmitAnswer"
          />
        </div>
      </div>
    </transition>

    <!-- Phase 4: 최종 피드백 -->
    <transition name="fade">
      <div v-if="phase === 'feedback'" class="feedback-layout">
        <InterviewFeedback
          :feedback="finalFeedback"
          @restart="onRestart"
        />
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useInterview } from './composables/useInterview';
import JobPostingSelector from './components/JobPostingSelector.vue';
import InterviewChat from './components/InterviewChat.vue';
import InterviewFeedback from './components/InterviewFeedback.vue';
import InterviewHistory from './components/InterviewHistory.vue';
import WebcamDisplay from './components/WebcamDisplay.vue';

// [수정일: 2026-02-23] [vision] WebcamDisplay 컴포넌트 참조
const webcamRef = ref(null);

// 화면 단계: 'select' | 'loading' | 'interview' | 'feedback'
const phase = ref('select');

const {
  sessionId,
  currentQuestion,
  currentSlot,
  currentTopic,
  currentTurn,
  totalSlots,
  slotsCleared,
  messages,
  isLoading,
  isStreaming,
  hasStreamedToken,
  isFinished,
  finalFeedback,
  error,
  slotProgress,
  visionSystem, // [수정일: 2026-02-23] [vision] 비전 시스템 추출
  startSession,
  submitUserAnswer,
  resetSession,
} = useInterview();

// 면접 완료 시 피드백 화면으로 전환
watch(isFinished, (val) => {
  if (val) {
    phase.value = 'feedback';
  }
});

async function onStartSession(jobPostingId) {
  phase.value = 'loading';
  try {
    await startSession(jobPostingId);
    phase.value = 'interview';

    // [수정일: 2026-02-23] [vision] 카메라 권한 획득 및 스트림 준비 완료 시점인 onWebcamReady 로직으로 위임 (setTimeout 제거)
  } catch {
    phase.value = 'select';
  }
}

// [수정일: 2026-02-23] [vision] 웹캠이 완전히 준비된 직후 호출되어 분석 시작
function onWebcamReady(videoEl) {
  if (visionSystem && visionSystem.startAnalysis) {
    visionSystem.startAnalysis(videoEl);
  }
}

async function onSubmitAnswer(answer) {
  await submitUserAnswer(answer);
}

function onRestart() {
  resetSession();
  phase.value = 'select';
}
</script>

<style scoped>
.mock-interview-page {
  height: 100vh;
  width: 100%;
  background: #f0f2f5;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 오류 배너 */
.global-error-banner {
  background: #fee2e2;
  color: #b91c1c;
  padding: 10px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  flex-shrink: 0;
}
.global-error-banner button {
  background: none; border: none; cursor: pointer; color: #b91c1c; font-size: 16px;
}

/* ── 선택 / 히스토리 / 피드백 화면 ───────────────────────── */
.select-wrapper {
  flex: 1;
  overflow-y: auto;
  background: #0c0e14;
  position: relative;
}

.btn-history {
  position: fixed;
  top: 20px;
  right: 28px;
  padding: 8px 16px;
  background: white;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  z-index: 20;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: background 0.15s, border-color 0.15s;
}
.btn-history:hover { background: #f5f3ff; border-color: #6366f1; color: #4f46e5; }

.history-layout {
  flex: 1;
  overflow-y: auto;
  background: #f0f2f5;
}

.feedback-layout {
  flex: 1;
  overflow-y: auto;
  background: #f0f2f5;
  padding: 32px 40px;
}

/* ── 로딩 ─────────────────────────────────────────────────── */
.loading-overlay {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a1a2e;
}
.loading-content { text-align: center; }
.loading-spinner-ring {
  width: 60px; height: 60px;
  border: 5px solid rgba(255,255,255,0.15);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
  margin: 0 auto 24px;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 20px; font-weight: 600; color: #fff; margin-bottom: 8px; }
.loading-sub { font-size: 14px; color: rgba(255,255,255,0.5); }

/* ── 면접 진행 레이아웃 (2칸 1:1) ───────────────────────── */
.interview-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 0;
  overflow: hidden;
}

/* 왼쪽: 면접관 패널 */
.interviewer-panel {
  background: linear-gradient(170deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 18px;
  padding: 40px 28px;
  overflow: hidden;
  position: relative;
}

/* 배경 장식 */
.interviewer-panel::before {
  content: '';
  position: absolute;
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
}

/* 웹캠 영역 */
.iv-webcam-wrap {
  width: 100%;
  max-width: 380px;
  flex-shrink: 0;
}

.iv-label {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255,255,255,0.5);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.iv-topic {
  font-size: 17px;
  font-weight: 700;
  color: #fff;
  text-align: center;
  line-height: 1.4;
  padding: 0 8px;
}

/* 진행 점 */
.iv-progress-dots {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}
.iv-dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  transition: background 0.3s;
}
.iv-dot--done { background: #6366f1; }
.iv-dot--active { background: #a5b4fc; box-shadow: 0 0 8px rgba(165,180,252,0.8); }

.iv-turn-info {
  font-size: 13px;
  color: rgba(255,255,255,0.4);
}

/* 상태 표시 */
.iv-status {
  font-size: 13px;
  color: rgba(255,255,255,0.4);
  padding: 6px 16px;
  border-radius: 99px;
  border: 1px solid rgba(255,255,255,0.1);
  transition: all 0.3s;
}
.iv-status--active {
  color: #a5b4fc;
  border-color: rgba(165,180,252,0.4);
  background: rgba(99,102,241,0.1);
}
.iv-blink {
  animation: blink 1s infinite;
  margin-right: 4px;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.2; }
}

/* 오른쪽: 채팅 패널 */
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  background: #fff;
  border-left: 1px solid #e5e7eb;
}

/* ── 페이드 트랜지션 ──────────────────────────────────────── */
.fade-enter-active,
.fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from,
.fade-leave-to { opacity: 0; }
</style>
