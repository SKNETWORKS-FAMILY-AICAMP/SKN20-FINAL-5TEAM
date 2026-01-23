<template>
  <div class="modal-overlay" :class="{ active: isActive }">
    <div class="modal-window deep-dive-modal">
      <div class="modal-header">
        <h3>🔗 연결 심화 질문</h3>
        <div class="modal-subtitle">Connection Deep Dive</div>
      </div>
      <div class="modal-body">
        <div v-if="isGenerating" class="loading-question">
          <div class="loading-spinner-large"></div>
          <p>연결에 대한 질문을 생성하는 중...</p>
        </div>
        <template v-else>
          <div class="ai-question deep-dive">
            <span class="ai-question-title">DEEP DIVE QUESTION</span>
            <span>{{ question }}</span>
          </div>
          <textarea
            class="user-answer"
            v-model="answer"
            placeholder="이 연결에 대해 설명해주세요..."
          ></textarea>
        </template>
      </div>
      <div class="modal-footer">
        <button class="btn-cancel" @click="$emit('skip')">건너뛰기</button>
        <button
          class="btn-submit"
          @click="submitAnswer"
          :disabled="isGenerating"
        >
          답변 저장
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DeepDiveModal',
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
  emits: ['skip', 'submit'],
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
  border: 2px solid #ff4785;
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 20px 60px rgba(255, 71, 133, 0.3);
  transform: scale(0.9);
  transition: transform 0.3s ease;
}

.modal-overlay.active .modal-window {
  transform: scale(1);
}

.modal-header {
  padding: 25px;
  border-bottom: 1px solid rgba(255, 71, 133, 0.3);
  text-align: center;
}

.modal-header h3 {
  margin: 0 0 5px 0;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.5em;
  color: #ff4785;
  text-shadow: 0 0 15px rgba(255, 71, 133, 0.5);
}

.modal-subtitle {
  color: #ff4785;
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
  border: 4px solid rgba(255, 71, 133, 0.3);
  border-top-color: #ff4785;
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
  background: rgba(255, 71, 133, 0.1);
  border: 1px solid rgba(255, 71, 133, 0.3);
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
  color: #ff4785;
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
  border: 2px solid rgba(255, 71, 133, 0.3);
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
  border-color: #ff4785;
}

.user-answer::placeholder {
  color: rgba(224, 224, 224, 0.4);
}

.modal-footer {
  padding: 20px 25px;
  border-top: 1px solid rgba(255, 71, 133, 0.3);
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
  background: linear-gradient(135deg, #ff4785, #ff1744);
  border: none;
  border-radius: 8px;
  color: #fff;
  font-family: 'Space Mono', monospace;
  font-size: 0.9em;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(255, 71, 133, 0.4);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
