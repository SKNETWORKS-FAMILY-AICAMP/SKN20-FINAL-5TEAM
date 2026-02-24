<template>
  <div class="audio-recorder">

    <!-- 상태: idle (자동 시작 대기 중) -->
    <div v-if="state === 'idle'" class="recorder-idle">
      <p class="idle-hint">잠시 후 자동으로 녹음이 시작됩니다...</p>
    </div>

    <!-- 상태: recording — 실시간 텍스트 표시 -->
    <div v-else-if="state === 'recording'" class="recorder-recording">
      <div class="recording-bar">
        <span class="rec-dot"></span>
        <span class="rec-label">녹음 중</span>
        <span class="rec-timer">{{ formatTime(elapsedSec) }}</span>
        <button class="btn-stop" @click="stopRecording">답변 완료</button>
      </div>

      <!-- 실시간 인식 텍스트 -->
      <div class="live-transcript-box">
        <span class="live-transcript-final">{{ finalTranscript }}{{ interimTranscript }}</span>
        <span v-if="!finalTranscript && !interimTranscript" class="live-placeholder">
          말씀해주세요...
        </span>
      </div>

      <div class="waveform">
        <span v-for="(h, i) in waveHeights" :key="i" class="wave-bar" :style="{ height: h + 'px' }"></span>
      </div>
    </div>

    <!-- 상태: refining — faster-whisper 보정 중 -->
    <div v-else-if="state === 'refining'" class="recorder-refining">
      <div class="refining-row">
        <div class="refining-spinner"></div>
        <span class="refining-text">정확도 보정 중...</span>
      </div>
      <!-- 보정 중에도 Web Speech 결과 미리 보여줌 -->
      <div class="live-transcript-box live-transcript-box--dim">
        {{ finalTranscript || '(인식 중...)' }}
      </div>
    </div>

    <!-- 상태: confirm — 최종 확인 -->
    <div v-else-if="state === 'confirm'" class="recorder-confirm">
      <div class="confirm-header">
        <span class="confirm-badge" :class="whisperUsed ? 'badge--whisper' : 'badge--browser'">
          {{ whisperUsed ? 'Whisper 보정 완료' : '브라우저 인식' }}
        </span>
        <span class="confirm-label">수정 후 제출하세요</span>
      </div>
      <!-- [수정일: 2026-02-23] 모의면접 답변 확인 단계에서 Enter 키를 통해 즉시 제출 가능하게 수정 (Shift+Enter는 줄바꿈) -->
      <textarea
        ref="transcriptInputRef"
        v-model="transcript"
        class="transcript-input"
        rows="4"
        placeholder="인식된 텍스트..."
        @keydown.enter.exact.prevent="submitTranscript"
      ></textarea>
      <p v-if="!transcript" class="no-speech-hint">음성이 감지되지 않았습니다. 다시 녹음해주세요.</p>
      <div class="confirm-actions">
        <button class="btn-submit" @click="submitTranscript" :disabled="!transcript.trim()">
          제출
        </button>
      </div>
    </div>

    <!-- 오류 -->
    <div v-if="errorMsg" class="recorder-error">
      {{ errorMsg }}
      <button @click="errorMsg = ''">✕</button>
    </div>

  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue';
import axios from 'axios';

const props = defineProps({
  disabled: { type: Boolean, default: false },
});
const emit = defineEmits(['submit']);

// ── 상태 ──────────────────────────────────────────────────
const state = ref('idle');            // idle | recording | refining | confirm
const finalTranscript = ref('');      // Web Speech 최종 누적 텍스트
const interimTranscript = ref('');    // Web Speech 임시 텍스트
const transcript = ref('');           // 최종 제출용 텍스트 (수정 가능)
const transcriptInputRef = ref(null);
const errorMsg = ref('');
const elapsedSec = ref(0);
const whisperUsed = ref(false);

let recognition = null;
let mediaRecorder = null;
let audioChunks = [];
let stream = null;
let timerInterval = null;
let audioContext = null;
let analyser = null;
let animFrameId = null;
let sessionBase = '';  // 세션 간 누적 텍스트

const waveHeights = ref(Array(14).fill(3));

// ── 포맷 ──────────────────────────────────────────────────
function formatTime(sec) {
  const m = Math.floor(sec / 60).toString().padStart(2, '0');
  const s = (sec % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

// ── 녹음 시작 ─────────────────────────────────────────────
async function startRecording() {
  errorMsg.value = '';
  finalTranscript.value = '';
  interimTranscript.value = '';
  whisperUsed.value = false;
  sessionBase = '';

  try {
    // 1. 마이크 스트림 획득
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    // 2. MediaRecorder 시작 (faster-whisper용 오디오 녹음)
    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : 'audio/webm';
    mediaRecorder = new MediaRecorder(stream, { mimeType });
    audioChunks = [];
    mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) audioChunks.push(e.data); };
    mediaRecorder.start(100);

    // 3. Web Speech API 시작 (실시간 표시용)
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognition = new SpeechRecognition();
      recognition.lang = 'ko-KR';
      recognition.continuous = true;
      recognition.interimResults = true;

      recognition.onresult = (event) => {
        let sessionFinal = '';
        let interim = '';
        // 매 이벤트마다 현재 세션의 전체 결과를 처음부터 재처리
        for (let i = 0; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            sessionFinal += event.results[i][0].transcript;
          } else {
            interim += event.results[i][0].transcript;
          }
        }
        finalTranscript.value = sessionBase + sessionFinal;
        interimTranscript.value = interim;
      };

      recognition.onerror = (e) => {
        // no-speech 등 경미한 오류는 무시
        if (e.error !== 'no-speech' && e.error !== 'aborted') {
          console.warn('[SpeechRecognition]', e.error);
        }
      };

      // 녹음 중 Web Speech API가 침묵 감지로 끊기면 자동 재시작
      recognition.onend = () => {
        if (state.value === 'recording' && recognition) {
          // 재시작 전 현재 세션 결과를 sessionBase에 저장
          sessionBase = finalTranscript.value;
          try { recognition.start(); } catch (_) {}
        }
      };

      recognition.start();
    }

    // 4. 웨이브폼 (실제 마이크 입력 반응)
    audioContext = new AudioContext();
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 64;
    audioContext.createMediaStreamSource(stream).connect(analyser);
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    const BAR_COUNT = 14;
    function drawWave() {
      animFrameId = requestAnimationFrame(drawWave);
      analyser.getByteFrequencyData(dataArray);
      const step = Math.floor(dataArray.length / BAR_COUNT);
      waveHeights.value = Array.from({ length: BAR_COUNT }, (_, i) => {
        const val = dataArray[i * step] / 255;
        return Math.max(3, Math.round(val * 24));
      });
    }
    drawWave();

    // 5. 타이머
    state.value = 'recording';
    elapsedSec.value = 0;
    timerInterval = setInterval(() => { elapsedSec.value += 1; }, 1000);

  } catch (err) {
    errorMsg.value = '마이크 접근 권한이 필요합니다.';
  }
}

// ── 녹음 중지 ─────────────────────────────────────────────
async function stopRecording() {
  clearInterval(timerInterval);
  cancelAnimationFrame(animFrameId);
  waveHeights.value = Array(14).fill(3);
  if (audioContext) { audioContext.close(); audioContext = null; }

  // Web Speech 중지 (null을 먼저 설정해 onend의 자동 재시작 방지)
  if (recognition) {
    const recToStop = recognition;
    recognition = null;
    recToStop.stop();
  }

  // MediaRecorder 중지 (Whisper 전송 없이 종료)
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  }

  // 마이크 스트림 해제
  if (stream) {
    stream.getTracks().forEach(t => t.stop());
    stream = null;
  }

  // [수정일: 2026-02-24] Web Speech 결과를 즉시 confirm으로 보내는 대신, faster-whisper(RunPod) 보정 과정을 거치도록 수정
  state.value = 'refining';
  await sendToWhisper();
}

// ── faster-whisper로 정확도 보정 ──────────────────────────
async function sendToWhisper() {
  try {
    const mimeType = audioChunks[0]?.type || 'audio/webm';
    const blob = new Blob(audioChunks, { type: mimeType });

    const formData = new FormData();
    formData.append('audio', blob, 'recording.webm');

    const response = await axios.post('/api/core/stt/transcribe/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      withCredentials: true,
    });

    const whisperText = response.data.transcript?.trim();

    if (whisperText) {
      transcript.value = whisperText;
      whisperUsed.value = true;
    } else {
      // Whisper 결과 없으면 Web Speech 결과 사용
      transcript.value = (finalTranscript.value + ' ' + interimTranscript.value).trim();
      whisperUsed.value = false;
    }

  } catch (err) {
    // Whisper 실패 → Web Speech 결과로 폴백
    transcript.value = (finalTranscript.value + ' ' + interimTranscript.value).trim();
    whisperUsed.value = false;
    if (err.response?.status !== 401) {
      console.warn('[Whisper] 폴백 to Web Speech:', err.message);
    }
  }

  state.value = 'confirm';
  await nextTick();
  transcriptInputRef.value?.focus();
}

// ── 제출 ──────────────────────────────────────────────────
function submitTranscript() {
  const text = transcript.value.trim();
  if (!text) return;
  emit('submit', text);
  resetToIdle();
}

// ── 초기화 ────────────────────────────────────────────────
function resetToIdle() {
  state.value = 'idle';
  transcript.value = '';
  finalTranscript.value = '';
  interimTranscript.value = '';
  errorMsg.value = '';
  elapsedSec.value = 0;
  audioChunks = [];
  whisperUsed.value = false;
}

// ── 다시 녹음 (바로 시작) ──────────────────────────────────
function retryRecording() {
  resetToIdle();
  startRecording();
}

// ── 마운트 시 자동 녹음 시작 (첫 질문) ───────────────────
onMounted(() => {
  if (!props.disabled) startRecording();
});

// ── 질문 완료 시 자동 녹음 시작 (이후 질문) ──────────────
watch(
  () => props.disabled,
  (newVal, oldVal) => {
    if (oldVal === true && newVal === false && state.value === 'idle') {
      startRecording();
    }
  }
);

// ── 정리 ──────────────────────────────────────────────────
onUnmounted(() => {
  clearInterval(timerInterval);
  if (recognition) recognition.stop();
  if (stream) stream.getTracks().forEach(t => t.stop());
});
</script>

<style scoped>
.audio-recorder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  width: 100%;
  box-sizing: border-box;
}

/* ── idle ─────────────────────────────────────────────── */
.recorder-idle {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.btn-start {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 13px 30px;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 99px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s;
}

.btn-start:hover:not(:disabled) { background: #4f46e5; transform: scale(1.02); }
.btn-start:disabled { opacity: 0.4; cursor: not-allowed; }

.idle-hint { font-size: 12px; color: #9ca3af; margin: 0; }

/* ── recording ────────────────────────────────────────── */
.recorder-recording {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.recording-bar {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rec-dot {
  width: 9px;
  height: 9px;
  background: #ef4444;
  border-radius: 50%;
  animation: blink 1s infinite;
  flex-shrink: 0;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.2; }
}

.rec-label {
  font-size: 13px;
  font-weight: 600;
  color: #ef4444;
}

.rec-timer {
  font-size: 12px;
  color: #6b7280;
  font-variant-numeric: tabular-nums;
  flex: 1;
}

.btn-stop {
  padding: 7px 18px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 99px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  white-space: nowrap;
}

.btn-stop:hover { background: #dc2626; }

/* 실시간 텍스트 박스 */
.live-transcript-box {
  width: 100%;
  min-height: 64px;
  max-height: 120px;
  overflow-y: auto;
  background: #f9fafb;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 14px;
  line-height: 1.6;
  color: #111827;
  box-sizing: border-box;
  word-break: break-all;
}

.live-transcript-box--dim {
  color: #6b7280;
}

.live-transcript-final { color: #111827; }

.live-transcript-interim {
  color: #9ca3af;
  font-style: italic;
}

.live-placeholder {
  color: #d1d5db;
  font-style: italic;
}

/* 웨이브폼 */
.waveform {
  display: flex;
  align-items: center;
  gap: 3px;
  height: 28px;
  justify-content: center;
}

.wave-bar {
  display: block;
  width: 4px;
  background: #6366f1;
  border-radius: 2px;
  transition: height 0.05s ease;
  min-height: 3px;
}

/* ── refining ─────────────────────────────────────────── */
.recorder-refining {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.refining-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.refining-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid #e5e7eb;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes spin { to { transform: rotate(360deg); } }

.refining-text {
  font-size: 13px;
  color: #6b7280;
}

/* ── confirm ──────────────────────────────────────────── */
.recorder-confirm {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.confirm-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.confirm-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 99px;
}

.badge--whisper {
  background: #dbeafe;
  color: #1d4ed8;
}

.badge--browser {
  background: #f3f4f6;
  color: #6b7280;
}

.confirm-label {
  font-size: 12px;
  color: #9ca3af;
}

.transcript-input {
  width: 100%;
  border: 1.5px solid #6366f1;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 14px;
  font-family: inherit;
  color: #111827;
  background: #f5f3ff;
  resize: none;
  line-height: 1.6;
  box-sizing: border-box;
}

.transcript-input:focus {
  outline: none;
  border-color: #4f46e5;
}

.no-speech-hint {
  font-size: 12px;
  color: #ef4444;
  margin: 0;
  text-align: center;
}

.confirm-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.btn-retry {
  padding: 9px 18px;
  border: 1.5px solid #d1d5db;
  background: white;
  color: #374151;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-retry:hover { background: #f3f4f6; }

.btn-submit {
  padding: 9px 22px;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-submit:hover:not(:disabled) { background: #4f46e5; }
.btn-submit:disabled { opacity: 0.4; cursor: not-allowed; }

/* ── 오류 ─────────────────────────────────────────────── */
.recorder-error {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fee2e2;
  color: #b91c1c;
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 12px;
  width: 100%;
  box-sizing: border-box;
}

.recorder-error button {
  background: none;
  border: none;
  cursor: pointer;
  color: #b91c1c;
  margin-left: auto;
}
</style>
