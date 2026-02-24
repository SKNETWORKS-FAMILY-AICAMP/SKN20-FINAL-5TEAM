<template>
  <div class="interview-chat">
    <!-- 헤더: 슬롯 진행 상황 -->
    <div class="chat-header">
      <div class="slot-info">
        <span class="slot-label">{{ currentTopic || currentSlot }}</span>
        <span class="turn-badge">턴 {{ currentTurn }}</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: slotProgress + '%' }"></div>
      </div>
      <div class="progress-text">역량 {{ slotsCleared }}/{{ totalSlots }} 확인</div>
    </div>

    <!-- 대화 영역 -->
    <div class="chat-messages" ref="messagesContainerRef">
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        class="message-row"
        :class="`message-row--${msg.role}`"
      >
        <!-- Coach 피드백 -->
        <div v-if="msg.role === 'coach'" class="coach-bubble">
          <span class="coach-icon">💡</span>
          <span class="coach-text">{{ msg.content }}</span>
        </div>

        <!-- 면접관 질문 -->
        <div v-else-if="msg.role === 'interviewer'" class="interviewer-bubble">
          <div class="avatar interviewer-avatar">🎙️</div>
          <div class="bubble">
            <span v-if="!msg.content && isStreaming" class="typing-dots">
              <span></span><span></span><span></span>
            </span>
            <span v-else>{{ msg.content }}</span>
          </div>
        </div>

        <!-- 사용자 답변 -->
        <div v-else class="user-bubble">
          <div class="bubble bubble--user">{{ msg.content }}</div>
          <div class="avatar user-avatar">🙋</div>
        </div>
      </div>

      <!-- 스트리밍 중 새 메시지 로딩 표시 -->
      <div v-if="isStreaming && !hasStreamedToken" class="message-row message-row--interviewer">
        <div class="interviewer-bubble">
          <div class="avatar interviewer-avatar">🎙️</div>
          <div class="bubble">
            <span class="typing-dots">
              <span></span><span></span><span></span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 입력 영역 -->
    <div class="chat-input-area">
      <!-- 음성 모드 -->
      <template v-if="voiceMode">
        <AudioRecorder :disabled="isStreaming || isTTSPlaying" @submit="onSubmit" />
        <button class="mode-toggle" @click="voiceMode = false" title="텍스트로 입력">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M20 2H4a2 2 0 0 0-2 2v18l4-4h14a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2z"/>
          </svg>
          텍스트 입력
        </button>
      </template>

      <!-- 텍스트 모드 -->
      <template v-else>
        <textarea
          ref="inputRef"
          v-model="inputText"
          class="chat-input"
          placeholder="답변을 입력하세요... (Enter로 전송, Shift+Enter 줄바꿈)"
          :disabled="isStreaming"
          @keydown.enter.exact.prevent="onSubmitText"
        ></textarea>
        <div class="text-mode-actions">
          <button class="mode-toggle" @click="voiceMode = true" title="음성으로 입력">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 14 0h-2z"/>
            </svg>
            음성 입력
          </button>
          <button
            class="send-btn"
            :disabled="isStreaming || isTTSPlaying || !inputText.trim()"
            @click="onSubmitText"
          >
            전송
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue';
import AudioRecorder from './AudioRecorder.vue';
import { tts } from '@/utils/tts';

const props = defineProps({
  messages: { type: Array, default: () => [] },
  isStreaming: { type: Boolean, default: false },
  hasStreamedToken: { type: Boolean, default: false },
  currentSlot: { type: String, default: '' },
  currentTopic: { type: String, default: '' },
  currentTurn: { type: Number, default: 0 },
  totalSlots: { type: Number, default: 0 },
  slotsCleared: { type: Number, default: 0 },
  slotProgress: { type: Number, default: 0 },
});

const emit = defineEmits(['submit']);

const inputText = ref('');
const messagesContainerRef = ref(null);
const inputRef = ref(null);
const voiceMode = ref(true);  // 기본: 음성 모드
const lastSpokenContent = ref('');  // 중복 재생 방지
const isTTSPlaying = ref(!!props.messages.find(m => m.role === 'interviewer')?.content);

// TTS 시작 + isTTSPlaying 추적
function startTTS(text) {
  if (!text?.trim()) return;
  if (!isTTSPlaying.value) {
    isTTSPlaying.value = true;
    tts.onQueueEmpty = () => { isTTSPlaying.value = false; };
  }
  tts.speak(text.trim());
}

// 음성 모드에서 호출 (AudioRecorder가 transcript를 emit)
function onSubmit(text) {
  if (!text || props.isStreaming || isTTSPlaying.value) return;
  emit('submit', text);
}

// 텍스트 모드에서 호출
function onSubmitText() {
  const text = inputText.value.trim();
  if (!text || props.isStreaming || isTTSPlaying.value) return;
  emit('submit', text);
  inputText.value = '';
}

// 첫 질문 TTS (컴포넌트 마운트 시 — messages가 이미 있을 수 있음)
onMounted(async () => {
  await nextTick();
  const firstMsg = props.messages.find(m => m.role === 'interviewer');
  if (firstMsg?.content) {
    lastSpokenContent.value = firstMsg.content;
    // isTTSPlaying은 이미 true로 초기화됨. onQueueEmpty만 등록하면 됨.
    tts.onQueueEmpty = () => { isTTSPlaying.value = false; };
    tts.speak(firstMsg.content.trim());
  }
});

// case 1: 스트리밍 없이 바로 추가된 면접관 메시지 → 즉시 TTS
watch(
  () => props.messages.length,
  async (newLen, oldLen) => {
    if (newLen <= oldLen) return;
    const newMsg = props.messages[newLen - 1];
    if (newMsg?.role === 'interviewer' && newMsg?.content && !props.isStreaming) {
      if (newMsg.content !== lastSpokenContent.value) {
        lastSpokenContent.value = newMsg.content;
        startTTS(newMsg.content);
      }
    }
  }
);

// case 3: 스트리밍 완료 → 전체 텍스트 TTS + 포커스
watch(
  () => props.isStreaming,
  async (val, oldVal) => {
    if (val && !oldVal) {
      // 스트리밍 시작: 이전 TTS 중단
      tts.stop();
      isTTSPlaying.value = false;
    }
    if (!val && oldVal) {  // true → false (스트리밍 끝)
      // nextTick 전에 미리 블록 → AudioRecorder가 켜지는 틈 방지
      isTTSPlaying.value = true;
      tts.onQueueEmpty = () => { isTTSPlaying.value = false; };

      await nextTick();
      inputRef.value?.focus();

      const lastMsg = [...props.messages].reverse().find(m => m.role === 'interviewer');
      if (lastMsg?.content && lastMsg.content !== lastSpokenContent.value) {
        lastSpokenContent.value = lastMsg.content;
        tts.speak(lastMsg.content.trim());
      } else {
        // TTS할 내용이 없으면 즉시 해제
        tts.onQueueEmpty = null;
        isTTSPlaying.value = false;
      }
    }
  }
);

// 새 메시지 추가 시 자동 스크롤
watch(
  () => props.messages.length,
  async () => {
    await nextTick();
    if (messagesContainerRef.value) {
      messagesContainerRef.value.scrollTop = messagesContainerRef.value.scrollHeight;
    }
  }
);

// 스트리밍 중 계속 스크롤
watch(
  () => props.messages,
  async () => {
    await nextTick();
    if (messagesContainerRef.value) {
      const el = messagesContainerRef.value;
      const isNearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 120;
      if (isNearBottom) {
        el.scrollTop = el.scrollHeight;
      }
    }
  },
  { deep: true }
);
</script>

<style scoped>
.interview-chat {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

/* 헤더 */
.chat-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  background: #fff;
}

.slot-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.slot-label {
  font-size: 14px;
  font-weight: 600;
  color: #4f46e5;
}

.turn-badge {
  font-size: 12px;
  color: #888;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 99px;
}

.progress-bar {
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 4px;
}

.progress-fill {
  height: 100%;
  background: #6366f1;
  transition: width 0.4s ease;
}

.progress-text {
  font-size: 11px;
  color: #9ca3af;
  text-align: right;
}

/* 메시지 영역 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  scroll-behavior: smooth;
}

.message-row {
  display: flex;
  flex-direction: column;
}

/* Coach 피드백 */
.coach-bubble {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #fef9c3;
  border: 1px solid #fde047;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 13px;
  color: #713f12;
  max-width: 90%;
  align-self: center;
}

.coach-icon {
  flex-shrink: 0;
}

/* 면접관 */
.interviewer-bubble {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.avatar {
  font-size: 22px;
  flex-shrink: 0;
  margin-top: 4px;
}

.bubble {
  background: #f3f4f6;
  border-radius: 0 12px 12px 12px;
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.6;
  color: #111;
  max-width: 80%;
  white-space: pre-wrap;
}

/* 사용자 */
.user-bubble {
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  gap: 10px;
}

.bubble--user {
  background: #ede9fe;
  border-radius: 12px 0 12px 12px;
  color: #4c1d95;
}

/* 타이핑 애니메이션 */
.typing-dots {
  display: inline-flex;
  gap: 4px;
  align-items: center;
  padding: 4px 0;
}

.typing-dots span {
  width: 7px;
  height: 7px;
  background: #9ca3af;
  border-radius: 50%;
  animation: bounce 1.2s infinite;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 100% { transform: translateY(0); opacity: 0.5; }
  50% { transform: translateY(-5px); opacity: 1; }
}

/* 입력 영역 */
.chat-input-area {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #e5e7eb;
  background: #fff;
}

.chat-input {
  flex: 1;
  resize: none;
  border: 1.5px solid #d1d5db;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 14px;
  line-height: 1.5;
  min-height: 60px;
  max-height: 160px;
  font-family: inherit;
  color: #111827;
  background: #ffffff;
  transition: border-color 0.15s;
}

.chat-input:focus {
  outline: none;
  border-color: #6366f1;
}

.chat-input:disabled {
  background: #f9fafb;
  color: #9ca3af;
}

.send-btn {
  padding: 0 18px;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  align-self: flex-end;
  height: 44px;
}

.send-btn:hover:not(:disabled) {
  background: #4f46e5;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 텍스트 모드 액션 */
.text-mode-actions {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

/* 모드 전환 버튼 */
.mode-toggle {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  background: none;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 12px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
  align-self: flex-end;
}

.mode-toggle:hover {
  border-color: #6366f1;
  color: #6366f1;
  background: #f5f3ff;
}
</style>
