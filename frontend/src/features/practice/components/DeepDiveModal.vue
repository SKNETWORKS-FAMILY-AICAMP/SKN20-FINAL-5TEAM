<template>
  <div class="modal-overlay" :class="{ active: isActive }">
    <div class="modal-window deep-dive-modal">
      <div class="modal-header">
        <h3>🎯 아키텍처 심층 분석</h3>
        <div class="modal-subtitle">Architecture Deep Dive</div>
        <div v-if="totalQuestions > 0" class="question-progress">
          <span class="progress-text">질문 {{ currentQuestion }} / {{ totalQuestions }}</span>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
          </div>
        </div>
      </div>
      <div class="modal-body">
        <div v-if="isGenerating" class="loading-question">
          <div class="loading-spinner-large"></div>
          <p>아키텍처를 분석하여 질문을 생성하는 중...</p>
        </div>
        <template v-else>
          <!-- Mermaid Preview -->
          <div class="mermaid-preview-section" v-if="mermaidCode">
            <span class="preview-title">📊 아키텍처 다이어그램</span>
            <div class="mermaid-preview" ref="mermaidPreview"></div>
          </div>

          <div class="question-category-badge" v-if="category">
            {{ categoryIcon }} {{ category }}
          </div>
          <div class="ai-question deep-dive">
            <span class="ai-question-title">DEEP DIVE QUESTION</span>
            <span>{{ question }}</span>
          </div>
          <textarea
            class="user-answer"
            v-model="answer"
            placeholder="설계 의도와 함께 구체적으로 설명해주세요..."
          ></textarea>
        </template>
      </div>
      <div class="modal-footer">
        <button class="btn-cancel" @click="$emit('skip')">
          {{ isLastQuestion ? '스킵하고 평가하기' : '건너뛰기' }}
        </button>
        <button
          class="btn-submit"
          @click="submitAnswer"
          :disabled="isGenerating"
        >
          {{ isLastQuestion ? '답변 후 평가하기' : '다음 질문' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import mermaid from 'mermaid';

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
    },
    currentQuestion: {
      type: Number,
      default: 1
    },
    totalQuestions: {
      type: Number,
      default: 3
    },
    category: {
      type: String,
      default: ''
    },
    mermaidCode: {
      type: String,
      default: ''
    }
  },
  emits: ['skip', 'submit'],
  data() {
    return {
      answer: ''
    };
  },
  computed: {
    progressPercent() {
      if (this.totalQuestions === 0) return 0;
      return (this.currentQuestion / this.totalQuestions) * 100;
    },
    isLastQuestion() {
      return this.currentQuestion >= this.totalQuestions;
    },
    categoryIcon() {
      const icons = {
        '설계 의도': '🎨',
        '확장성/성능': '📈',
        '장애 대응': '🛡️'
      };
      return icons[this.category] || '💡';
    }
  },
  watch: {
    question(newVal) {
      // 질문이 변경되면 답변 초기화
      if (newVal) {
        this.answer = '';
      }
    },
    isActive(newVal) {
      if (newVal) {
        this.answer = '';
        this.$nextTick(() => {
          this.renderMermaid();
        });
      }
    },
    isGenerating(newVal) {
      if (!newVal && this.mermaidCode) {
        this.$nextTick(() => {
          this.renderMermaid();
        });
      }
    }
  },
  methods: {
    submitAnswer() {
      this.$emit('submit', this.answer.trim());
      this.answer = '';
    },
    async renderMermaid() {
      const container = this.$refs.mermaidPreview;
      if (!container || !this.mermaidCode) return;

      try {
        const { svg } = await mermaid.render('deepdive-mermaid-' + Date.now(), this.mermaidCode);
        container.innerHTML = svg;
      } catch (error) {
        container.innerHTML = '<p class="mermaid-error">다이어그램 렌더링 중 오류가 발생했습니다.</p>';
      }
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

.question-progress {
  margin-top: 15px;
}

.progress-text {
  display: block;
  font-size: 0.85em;
  color: #b0bec5;
  margin-bottom: 8px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 71, 133, 0.2);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff4785, #ff1744);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.question-category-badge {
  display: inline-block;
  padding: 6px 14px;
  background: rgba(255, 71, 133, 0.2);
  border: 1px solid rgba(255, 71, 133, 0.4);
  border-radius: 20px;
  font-size: 0.85em;
  color: #ff4785;
  margin-bottom: 15px;
  font-weight: 600;
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

/* Mermaid Preview */
.mermaid-preview-section {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 255, 157, 0.2);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.preview-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.85em;
  color: #64b5f6;
  letter-spacing: 1px;
  display: block;
  margin-bottom: 12px;
}

.mermaid-preview {
  background: rgba(0, 0, 0, 0.2);
  padding: 15px;
  border-radius: 8px;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
}

.mermaid-preview :deep(svg) {
  max-width: 100%;
  height: auto;
}

.mermaid-error {
  color: #ff4785;
  font-size: 0.85em;
}
</style>
