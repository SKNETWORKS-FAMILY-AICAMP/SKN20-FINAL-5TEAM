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
        <button class="btn-exit" @click="router.push('/')">✕ 나가기</button>
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
        <!-- 왼쪽: 면접관 아바타 패널 -->
        <div class="interviewer-panel">
          <button class="btn-exit" @click="onExit">✕ 나가기</button>
          <div class="iv-avatar-wrap">
            <video v-if="avatarVideoUrl" :src="avatarVideoUrl" class="iv-avatar-video" autoplay loop muted playsinline @error="avatarVideoUrl = null" />
            <img v-else :src="'/media/avatars/interviewer_woman.png'" class="iv-avatar-video" alt="면접관" />
          </div>
        </div>

        <!-- 가운데: 면접자 웹캠 패널 -->
        <div class="interviewer-panel">
          <div class="iv-webcam-wrap">
            <WebcamDisplay ref="webcamRef" @ready="onWebcamReady" />
            <div class="iv-overlay-top">
              <span class="iv-rec"><span class="iv-rec-dot"></span>REC</span>
              <span class="iv-timer">{{ formatTime(elapsedSec) }}</span>
            </div>
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
import { ref, watch, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useInterview } from './composables/useInterview';
import JobPostingSelector from './components/JobPostingSelector.vue';
import InterviewChat from './components/InterviewChat.vue';
import InterviewFeedback from './components/InterviewFeedback.vue';
import InterviewHistory from './components/InterviewHistory.vue';
import WebcamDisplay from './components/WebcamDisplay.vue';

const router = useRouter();

// [수정일: 2026-02-23] [vision] WebcamDisplay 컴포넌트 참조
const webcamRef = ref(null);

// 화면 단계: 'select' | 'loading' | 'interview' | 'feedback'
const phase = ref('select');

// 면접 경과 시간
const elapsedSec = ref(0);
let timerInterval = null;

function startTimer() {
  elapsedSec.value = 0;
  timerInterval = setInterval(() => { elapsedSec.value++; }, 1000);
}
function stopTimer() {
  clearInterval(timerInterval);
  timerInterval = null;
}
function formatTime(sec) {
  const m = String(Math.floor(sec / 60)).padStart(2, '0');
  const s = String(sec % 60).padStart(2, '0');
  return `${m}:${s}`;
}
onUnmounted(stopTimer);

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
  avatarVideoUrl,
  startSession,
  submitUserAnswer,
  resetSession,
} = useInterview();

// 면접 완료 시 피드백 화면으로 전환
watch(isFinished, (val) => {
  if (val) {
    stopTimer();
    phase.value = 'feedback';
  }
});

async function onStartSession(jobPostingId) {
  phase.value = 'loading';
  try {
    await startSession(jobPostingId);
    phase.value = 'interview';
    startTimer();

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

function onExit() {
  if (window.confirm('면접을 종료하시겠습니까? 진행 중인 내용은 저장되지 않습니다.')) {
    stopTimer();
    resetSession();
    phase.value = 'select';
  }
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

/* ── 면접 진행 레이아웃 (3칸) ───────────────────────── */
.interview-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
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
  padding: 40px 28px;
  overflow: hidden;
  position: relative;
}

.btn-exit {
  position: absolute;
  top: 16px;
  left: 16px;
  padding: 6px 12px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 6px;
  font-size: 12px;
  color: rgba(255,255,255,0.5);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  z-index: 10;
}
.btn-exit:hover {
  background: rgba(239,68,68,0.2);
  border-color: rgba(239,68,68,0.4);
  color: #fca5a5;
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

/* 아바타 영역 */
.iv-avatar-wrap {
  width: 100%;
  max-width: 380px;
  aspect-ratio: 4/3;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(0,0,0,0.3);
}
.iv-avatar-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.iv-avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border: 2px dashed rgba(255,255,255,0.2);
  border-radius: 12px;
}
.iv-avatar-icon { font-size: 64px; }
.iv-avatar-label { font-size: 14px; color: rgba(255,255,255,0.5); }

/* 웹캠 영역 */
.iv-webcam-wrap {
  width: 100%;
  max-width: 380px;
  flex-shrink: 0;
  position: relative;
}

/* REC + 타이머 오버레이 */
.iv-overlay-top {
  position: absolute;
  top: 10px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 12px;
  pointer-events: none;
}

.iv-rec {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.08em;
  background: rgba(0, 0, 0, 0.45);
  padding: 3px 8px;
  border-radius: 4px;
  backdrop-filter: blur(4px);
}

.iv-rec-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #ef4444;
  animation: recBlink 1.2s ease-in-out infinite;
}

@keyframes recBlink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.2; }
}

.iv-timer {
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  letter-spacing: 0.05em;
  font-variant-numeric: tabular-nums;
  background: rgba(0, 0, 0, 0.45);
  padding: 3px 8px;
  border-radius: 4px;
  backdrop-filter: blur(4px);
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
