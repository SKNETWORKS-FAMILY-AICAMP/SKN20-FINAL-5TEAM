<template>
  <div class="modal-overlay" :class="{ active: isActive }">
    <div class="modal-window">
      <div class="modal-header">
        <h3>🧐 심층 분석 질문</h3>
        <div class="modal-subtitle">AI Architect Bot</div>
      </div>
      <div class="modal-body">
        <div v-if="isGenerating" class="loading-question">
          <div class="loading-spinner-large"></div>
          <p>아키텍처를 분석하여 질문을 생성하는 중...</p>
        </div>
        <template v-else>
          <div class="ai-question">
            <span class="ai-question-title">QUESTION</span>
            <span>{{ question }}</span>
          </div>
          <textarea
            class="user-answer"
            v-model="answer"
            placeholder="여기에 답변을 작성해주세요... (예: CDN을 사용하여 정적 리소스를 캐싱하여 부하를 줄입니다.)"
          ></textarea>
        </template>
      </div>
      <div class="modal-footer">
        <button class="btn-cancel" @click="$emit('close')">취소</button>
        <button
          class="btn-submit"
          @click="submitAnswer"
          :disabled="isGenerating"
        >
          답변 제출 및 평가
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EvaluationModal',
  props: {
    isActive: {
      type: Boolean,
      default: false
    },
    question: {
      type: String,
      default: ''
    },
    isGenerating: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'submit'],
  data() {
    return {
      answer: ''
    };
  },
  watch: {
    isActive(newVal) {
      if (newVal) {
        this.answer = '';
      }
    }
  },
  methods: {
    submitAnswer() {
      if (!this.answer.trim()) {
        alert('답변을 입력해주세요!');
        return;
      }
      this.$emit('submit', this.answer.trim());
      this.answer = '';
    }
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.modal-overlay.active {
  opacity: 1;
  visibility: visible;
}

.modal-window {
  background: linear-gradient(145deg, #0a0e27, #111827);
  border: 2px solid #64b5f6;
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 20px 60px rgba(100, 181, 246, 0.3);
  transform: scale(0.9);
  transition: transform 0.3s ease;
}

.modal-overlay.active .modal-window {
  transform: scale(1);
}

.modal-header {
  padding: 25px;
  border-bottom: 1px solid rgba(100, 181, 246, 0.3);
  text-align: center;
}

.modal-header h3 {
  margin: 0 0 5px 0;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.5em;
  color: #64b5f6;
  text-shadow: 0 0 15px rgba(100, 181, 246, 0.5);
}

.modal-subtitle {
  color: #64b5f6;
  font-size: 0.9em;
}

.modal-body {
  padding: 25px;
  min-height: 200px;
}

.loading-question {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.loading-spinner-large {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(100, 181, 246, 0.3);
  border-top-color: #64b5f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-question p {
  color: #b0bec5;
  font-size: 1em;
}

.ai-question {
  background: rgba(100, 181, 246, 0.1);
  border: 1px solid rgba(100, 181, 246, 0.3);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ai-question-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.8em;
  color: #64b5f6;
  letter-spacing: 2px;
}

.ai-question > span:last-child {
  font-size: 1.1em;
  color: #e0e0e0;
  line-height: 1.6;
}

.user-answer {
  width: 100%;
  min-height: 120px;
  background: rgba(0, 0, 0, 0.4);
  border: 2px solid rgba(100, 181, 246, 0.3);
  border-radius: 12px;
  padding: 15px;
  color: #e0e0e0;
  font-family: 'Space Mono', monospace;
  font-size: 0.95em;
  resize: vertical;
  transition: border-color 0.3s ease;
}

.user-answer:focus {
  outline: none;
  border-color: #00ff9d;
}

.user-answer::placeholder {
  color: rgba(224, 224, 224, 0.4);
}

.modal-footer {
  padding: 20px 25px;
  border-top: 1px solid rgba(100, 181, 246, 0.3);
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

.btn-cancel {
  padding: 12px 25px;
  background: transparent;
  border: 2px solid #78909c;
  border-radius: 8px;
  color: #78909c;
  font-family: 'Space Mono', monospace;
  font-size: 0.9em;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel:hover {
  background: #78909c;
  color: #0a0e27;
}

.btn-submit {
  padding: 12px 25px;
  background: linear-gradient(135deg, #00ff9d, #00e676);
  border: none;
  border-radius: 8px;
  color: #0a0e27;
  font-family: 'Space Mono', monospace;
  font-size: 0.9em;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 255, 157, 0.4);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
