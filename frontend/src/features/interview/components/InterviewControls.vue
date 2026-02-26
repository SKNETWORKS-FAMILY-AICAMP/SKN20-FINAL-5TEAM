<template>
  <div class="interview-controls">
    <div class="controls-container">
      <!-- 음성 모드 -->
      <template v-if="voiceMode">
        <AudioRecorder :disabled="disabled" @submit="onVoiceSubmit" />
        <button class="mode-toggle" @click="voiceMode = false" title="텍스트로 입력">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M20 2H4a2 2 0 0 0-2 2v18l4-4h14a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2z"/>
          </svg>
          <span class="btn-text">텍스트 입력</span>
        </button>
      </template>

      <!-- 텍스트 모드 -->
      <template v-else>
        <div class="text-input-wrap">
          <textarea
            ref="inputRef"
            v-model="inputText"
            class="chat-input"
            placeholder="답변을 입력하세요... (Enter로 전송, Shift+Enter 줄바꿈)"
            :disabled="disabled"
            @keydown.enter.exact.prevent="onSubmitText"
          ></textarea>
        </div>
        <div class="actions-wrap">
          <button class="mode-toggle" @click="voiceMode = true" title="음성으로 입력">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 14 0h-2z"/>
            </svg>
            <span class="btn-text">음성 입력</span>
          </button>
          <button
            class="send-btn"
            :disabled="disabled || !inputText.trim()"
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
import { ref, watch, nextTick } from 'vue';
import AudioRecorder from './AudioRecorder.vue';

const props = defineProps({
  disabled: { type: Boolean, default: false }
});

const emit = defineEmits(['submit']);

const inputText = ref('');
const inputRef = ref(null);
const voiceMode = ref(true);

function onVoiceSubmit(text) {
  if (!text || props.disabled) return;
  emit('submit', text);
}

function onSubmitText() {
  const text = inputText.value.trim();
  if (!text || props.disabled) return;
  emit('submit', text);
  inputText.value = '';
}

// 텍스트 모드로 전환 시 포커스
watch(voiceMode, async (val) => {
  if (!val) {
    await nextTick();
    inputRef.value?.focus();
  }
});
</script>

<style scoped>
.interview-controls {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 640px; /* 자막 너비보다 약간 넓게 조정 */
  z-index: 10;
  padding: 0 20px;
}

.controls-container {
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.text-input-wrap {
  flex: 1;
}

.chat-input {
  width: 100%;
  height: 60px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px 16px;
  color: #fff;
  font-size: 15px;
  resize: none;
  font-family: inherit;
  transition: border-color 0.2s;
}

.chat-input:focus {
  outline: none;
  border-color: #6366f1;
}

.actions-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mode-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 8px 16px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
  white-space: nowrap;
}

.mode-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.3);
}

.btn-text {
  font-weight: 500;
}

.send-btn {
  background: #6366f1;
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #4f46e5;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
