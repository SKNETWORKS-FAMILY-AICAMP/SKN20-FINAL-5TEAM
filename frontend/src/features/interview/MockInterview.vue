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
        <button class="btn-exit btn-exit-right" @click="router.push('/')">✕ 나가기</button>
        <JobPostingSelector @start="onStartSession" @showHistory="phase = 'history'" />
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

    <!-- Phase 3: 면접 진행 (2분할 이머시브 레이아웃) -->
    <transition name="fade">
      <div v-if="phase === 'interview'" class="interview-layout-immersive">
        <!-- 왼쪽: 면접관 패널 -->
        <div class="interviewer-panel">
          <div class="panel-content">
            <div class="iv-avatar-wrap">
              <!-- 정적 아바타 이미지 -->
              <img :src="avatarImageSrc" :class="['iv-avatar-video', { 'idle-pulse': !isStreaming }]" :alt="`면접관-${avatarType}`" />
            </div>

            <!-- 면접관 자막 오버레이 -->
            <div class="subtitle-wrap subtitle-left">
              <div class="subtitle-badge iv-badge">INTERVIEWER</div>
              <div class="subtitle-text interviewer-text">
                <span v-if="interviewerTypewriterText">{{ interviewerTypewriterText }}</span>
                <span v-else class="typing-dots"><span></span><span></span><span></span></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 오른쪽: 면접자 웹캠 패널 -->
        <div class="user-panel">
          <button class="btn-exit btn-exit-right" @click="onExit">✕ 나가기</button>
          <div class="panel-content">
            <div class="iv-webcam-wrap">
              <WebcamDisplay ref="webcamRef" @ready="onWebcamReady" />
              <div class="iv-overlay-top">
                <span class="iv-rec"><span class="iv-rec-dot"></span>REC</span>
                <span class="iv-timer">{{ formatTime(elapsedSec) }}</span>
              </div>
            </div>

            <!-- 면접자 자막 오버레이 -->
            <div class="subtitle-wrap subtitle-right">
              <div class="subtitle-badge user-badge">YOU</div>
              <div class="subtitle-text user-text" ref="userSubtitleRef">
                <span v-if="userTypewriterText">{{ userTypewriterText }}</span>
                <span v-else class="subtitle-placeholder">답변을 입력해 주세요...</span>
              </div>
            </div>
          </div>

          <!-- 면접자 컨트롤바 (우측 하단 배치 - 절대 위치로 비디오 위치 영향 안 주게 설정) -->
          <InterviewControls
            :disabled="isStreaming || isTTSPlaying"
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
import { ref, computed, watch, onUnmounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useInterview } from './composables/useInterview';
import JobPostingSelector from './components/JobPostingSelector.vue';
import InterviewControls from './components/InterviewControls.vue';
import InterviewFeedback from './components/InterviewFeedback.vue';
import InterviewHistory from './components/InterviewHistory.vue';
import WebcamDisplay from './components/WebcamDisplay.vue';
import { tts } from './tts';

const router = useRouter();

// [수정일: 2026-02-23] [vision] WebcamDisplay 컴포넌트 참조
const webcamRef = ref(null);
const userSubtitleRef = ref(null);

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
  messages,
  isStreaming,
  hasStreamedToken,
  isFinished,
  finalFeedback,
  error,
  visionSystem,
  avatarType,
  videoQueue,
  startSession,
  submitUserAnswer,
  resetSession,
} = useInterview();

// TTS 큐 재생 상태
let queuePlayIndex = 0;
let isPlayingChunk = false;

// TTS 큐 재생 함수 (정적 이미지 모드: TTS + 자막만)
async function playNextChunk() {
  if (isPlayingChunk) return;
  if (queuePlayIndex >= videoQueue.value.length) return;

  const nextChunk = videoQueue.value[queuePlayIndex];
  if (!nextChunk.isReady) {
    setTimeout(playNextChunk, 100);
    return;
  }
  if (nextChunk.failed) {
    queuePlayIndex++;
    playNextChunk();
    return;
  }

  isPlayingChunk = true;
  isTTSPlaying.value = true; // 오디오 재생 전에 먼저 설정 (AudioRecorder 비활성화)
  queuePlayIndex++;

  // TTS 재생 후 완료 시 다음 청크 처리
  tts.onQueueEmpty = () => {
    isTTSPlaying.value = false;
    isPlayingChunk = false;
    tts.onQueueEmpty = null;
    playNextChunk();
  };

  // TTS 재생 시작 시점에 타이핑 시작 (음성과 텍스트 동기화)
  startTTS(nextChunk.text).then(() => startInterviewerTypewriter(nextChunk.text));
}

// 큐에 새 아이템이 들어오면 재생 시작 (현재 idle인 경우)
watch(() => videoQueue.value.length, (newLen) => {
  if (newLen > 0 && !isPlayingChunk) {
    playNextChunk();
  }
});

// --- [UI] 자막 및 동기화 관련 로직 ---
const interviewerTypewriterText = ref('');
const userTypewriterText = ref('');
const isTTSPlaying = ref(false);
let interviewerTimer = null;
let userTimer = null;
let lastSpokenText = ''; // 중복 TTS 방지

const imageCacheBuster = Date.now(); // 컴포넌트 마운트 시점 고정 (재다운로드 방지)

// 아바타 이미지 경로
const avatarImageSrc = computed(() => `/media/avatars/interviewer_${avatarType.value}.png?t=${imageCacheBuster}`);

// 면접관 타자기 효과 (스페이스가 아닌 문장 단위 누적)
function startInterviewerTypewriter(newChunk) {
  clearInterval(interviewerTimer);
  const baseText = interviewerTypewriterText.value;
  let i = 0;
  interviewerTimer = setInterval(() => {
    i = Math.min(i + 4, newChunk.length);
    interviewerTypewriterText.value = baseText + (baseText ? ' ' : '') + newChunk.slice(0, i);
    if (i >= newChunk.length) {
      clearInterval(interviewerTimer);
      interviewerTimer = null;
    }
  }, 30);
}

// 면접자 타자기 효과
function startUserTypewriter(fullText) {
  clearInterval(userTimer);
  userTypewriterText.value = '';
  let i = 0;
  userTimer = setInterval(() => {
    i = Math.min(i + 4, fullText.length);
    userTypewriterText.value = fullText.slice(0, i);
    if (i >= fullText.length) {
      clearInterval(userTimer);
      userTimer = null;
    }
  }, 30);
}

// TTS 재생 시작 (중복 호출 방지)
async function startTTS(text) {
  if (!text?.trim()) return Promise.resolve();
  if (text === lastSpokenText) return Promise.resolve();
  lastSpokenText = text;
  isTTSPlaying.value = true;
  await tts.speak(text.trim());
}

// 사용자 자막 자동 스크롤
watch(userTypewriterText, async () => {
  await nextTick();
  if (userSubtitleRef.value) {
    userSubtitleRef.value.scrollTop = userSubtitleRef.value.scrollHeight;
  }
});

// 메시지 변화 감시 (사용자 자막만 처리, 면접관은 TTS 큐에서 처리)
watch(() => messages.value.length, (newLen) => {
  if (newLen === 0) {
    interviewerTypewriterText.value = '';
    userTypewriterText.value = '';
    return;
  }
  const lastMsg = messages.value[newLen - 1];

  if (lastMsg.role === 'user') {
    startUserTypewriter(lastMsg.content);
    interviewerTypewriterText.value = '';
  }
});

// 스트리밍 시작 시 상태 초기화
watch(isStreaming, (val, oldVal) => {
  if (val && !oldVal) {
    tts.stop();
    lastSpokenText = '';
    clearInterval(interviewerTimer);
    interviewerTimer = null;
    isTTSPlaying.value = false;
    interviewerTypewriterText.value = '';
    queuePlayIndex = 0;
    isPlayingChunk = false;
  }
});

// 면접 완료 시 피드백 화면으로 전환
watch(isFinished, (val) => {
  if (val) {
    stopTimer();
    phase.value = 'feedback';
  }
});

function cleanupPlayback() {
  tts.stop();
  lastSpokenText = '';
  queuePlayIndex = 0;
  isPlayingChunk = false;
  isTTSPlaying.value = false;
  clearInterval(interviewerTimer);
  interviewerTimer = null;
  interviewerTypewriterText.value = '';
}

async function onStartSession({ jobPostingId, avatarType: selectedAvatarType }) {
  cleanupPlayback();
  phase.value = 'loading';
  try {
    await startSession(jobPostingId, selectedAvatarType);
    phase.value = 'interview';
    startTimer();
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
  cleanupPlayback();
  resetSession();
  phase.value = 'select';
}

function onExit() {
  if (window.confirm('면접을 종료하시겠습니까? 진행 중인 내용은 저장되지 않습니다.')) {
    stopTimer();
    cleanupPlayback();
    resetSession();
    phase.value = 'select';
  }
}
</script>

<style scoped>
.mock-interview-page {
  height: 100vh;
  width: 100%;
  background: #0c0e14;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  color: #fff;
}

/* ── 선택 / 히스토리 / 피드백 화면 ───────────────────────── */
.select-wrapper {
  flex: 1;
  overflow-y: auto;
  background: #0c0e14;
  position: relative;
}

/* 면접기록 버튼 클래스 제거됨 */

.history-layout {
  flex: 1;
  overflow-y: auto;
  background: #f0f2f5;
  color: #333;
}

.feedback-layout {
  flex: 1;
  overflow-y: auto;
  background: #f0f2f5;
  padding: 32px 40px;
  color: #333;
}

/* ── 로딩 ─────────────────────────────────────────────────── */
.loading-overlay {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0f172a;
}
.loading-content { text-align: center; }
.loading-spinner-ring {
  width: 60px; height: 60px;
  border: 5px solid rgba(255,255,255,0.1);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
  margin: 0 auto 24px;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 20px; font-weight: 600; color: #fff; margin-bottom: 8px; }
.loading-sub { font-size: 14px; color: rgba(255,255,255,0.5); }

/* ── 레이아웃 (이머시브 2분할) ───────────────────────── */
.interview-layout-immersive {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 0;
  overflow: hidden;
  position: relative;
}

.interviewer-panel, .user-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
  overflow: hidden;
  height: 100%;
}

.panel-content {
  width: 100%;
  max-width: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.interviewer-panel {
  background: linear-gradient(160deg, #0f172a 0%, #1e1b4b 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.05);
}

.user-panel {
  background: linear-gradient(200deg, #1e1b4b 0%, #0f172a 100%);
}

/* 아바타 / 웹캠 공통 랩퍼 */
.iv-avatar-wrap, .iv-webcam-wrap {
  width: 100%;
  max-width: 600px;
  aspect-ratio: 16/9;
  border-radius: 20px;
  overflow: hidden;
  background: #000;
  box-shadow: 0 20px 50px rgba(0,0,0,0.5);
  border: 1px solid rgba(255,255,255,0.1);
  margin-bottom: 30px;
  position: relative;
}

.iv-avatar-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* ── 아이들 상태 연출 (Living Avatar) ─────────────────────── */
.idle-pulse {
  animation: avatar-living 4s ease-in-out infinite;
}

@keyframes avatar-living {
  0%, 100% { transform: scale(1); filter: brightness(1) saturate(1); }
  50% { transform: scale(1.005); filter: brightness(1.05) saturate(1.05); }
}

/* ── 자막 시스템 ────────────────────────────────────────── */
.subtitle-wrap {
  width: 100%;
  max-width: 600px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
}

.subtitle-badge {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.1em;
}

.iv-badge { background: rgba(99, 102, 241, 0.2); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); }
.user-badge { background: rgba(234, 179, 8, 0.2); color: #fbbf24; border: 1px solid rgba(234, 179, 8, 0.3); }

.subtitle-text {
  width: 100%;
  height: 120px;
  overflow-y: auto;
  font-size: 18px;
  line-height: 1.6;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.9);
  white-space: pre-wrap;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.user-text { color: #fff; font-weight: 500; }

.subtitle-placeholder {
  color: rgba(255, 255, 255, 0.2);
  font-style: italic;
  font-size: 16px;
}

/* ── 기타 컴포넌트 스타일 ────────────────────────────────── */
.btn-exit {
  position: absolute;
  top: 24px;
  left: 24px;
  padding: 8px 16px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  font-size: 13px;
  color: rgba(255,255,255,0.6);
  cursor: pointer;
  z-index: 10;
  transition: all 0.2s;
}

.btn-exit:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.3);
  color: #fca5a5;
}

.btn-exit-right {
  left: auto;
  right: 24px;
}

/* 타이머 / REC */
.iv-overlay-top {
  position: absolute;
  top: 15px;
  left: 15px;
  right: 15px;
  display: flex;
  justify-content: space-between;
  pointer-events: none;
}

.iv-rec {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 800;
  background: rgba(0,0,0,0.6);
  padding: 4px 10px;
  border-radius: 6px;
  backdrop-filter: blur(4px);
}

.iv-rec-dot {
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 50%;
  animation: blink 1s infinite;
}

@keyframes blink { 50% { opacity: 0.3; } }

.iv-timer {
  font-size: 13px;
  font-weight: 600;
  background: rgba(0,0,0,0.6);
  padding: 4px 10px;
  border-radius: 6px;
  backdrop-filter: blur(4px);
  font-variant-numeric: tabular-nums;
}

/* 타이핑 애니메이션 (자막용) */
.typing-dots {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}
.typing-dots span {
  width: 6px; height: 6px;
  background: #6366f1;
  border-radius: 50%;
  animation: bounce 1s infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }

/* 오류 배너 */
.global-error-banner {
  background: #450a0a;
  color: #fca5a5;
  padding: 12px 24px;
  display: flex;
  justify-content: space-between;
}

/* ── 페이드 트랜지션 ──────────────────────────────────────── */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
