<template>
  <div class="modal-overlay" :class="{ active: isActive }">
    <div class="interrogation-modal">
      <!-- 헤더 -->
      <div class="modal-header">
        <h3>🔍 심문 진행 중</h3>
        <div class="modal-subtitle">INTERROGATION IN PROGRESS</div>
        <div v-if="totalQuestions > 0" class="question-progress">
          <span class="progress-text">질문 {{ currentQuestion }} / {{ totalQuestions }}</span>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- 본문 -->
      <div class="modal-body">
        <div v-if="isGenerating" class="loading-question">
          <div class="loading-spinner-large"></div>
          <p>용의자의 설계도를 분석 중... 꽥!</p>
        </div>
        <template v-else>
          <div class="content-layout">
            <!-- 왼쪽: Mermaid Preview -->
            <div class="mermaid-preview-section" v-if="mermaidCode">
              <span class="preview-title">[증거물] 설계 다이어그램</span>
              <div class="mermaid-preview" ref="mermaidPreview"></div>
            </div>

            <!-- 오른쪽: 질문 및 답변 -->
            <div class="question-section">
              <!-- 오리 형사 -->
              <div class="detective-question-box">
                <div class="detective-mini">
                  <img src="/image/duck_det.png" alt="Detective Duck" />
                </div>
                <div class="question-content">
                  <div class="question-category-badge" v-if="category">
                    {{ categoryIcon }} {{ category }}
                  </div>
                  <div class="question-text">
                    <span class="question-label">DET. DUCK</span>
                    <p>{{ question }}</p>
                  </div>
                </div>
              </div>

              <!-- 용의자 답변 -->
              <div class="answer-section">
                <span class="answer-label">[용의자 진술]</span>
                <textarea
                  class="user-answer"
                  v-model="answer"
                  placeholder="설계 의도와 함께 진술하세요... (거짓말은 금지! 꽥!)"
                ></textarea>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- 푸터 -->
      <div class="modal-footer">
        <button class="btn-skip" @click="$emit('skip')">
          {{ isLastQuestion ? '묵비권 행사 (평가)' : '묵비권 (건너뛰기)' }}
        </button>
        <button
          class="btn-submit"
          @click="submitAnswer"
          :disabled="isGenerating"
        >
          {{ isLastQuestion ? '최종 진술 (평가)' : '진술 완료' }}
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
        container.innerHTML = '<p class="mermaid-error">다이어그램 렌더링 오류</p>';
      }
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Courier+Prime:wght@400;700&display=swap');

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.modal-overlay.active {
  opacity: 1;
  visibility: visible;
}

.interrogation-modal {
  background: #1a1a1a;
  border: 6px solid #f1c40f;
  width: 95%;
  max-width: 1100px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 0 50px rgba(241, 196, 15, 0.3), 20px 20px 0 rgba(0, 0, 0, 0.8);
  transform: scale(0.9);
  transition: transform 0.3s ease;
}

.modal-overlay.active .interrogation-modal {
  transform: scale(1);
}

.modal-header {
  padding: 20px;
  border-bottom: 4px solid #f1c40f;
  text-align: center;
  background: #000;
}

.modal-header h3 {
  margin: 0 0 5px 0;
  font-family: 'Press Start 2P', cursive;
  font-size: 1.1rem;
  color: #f1c40f;
  text-shadow: 2px 2px 0 #000;
}

.modal-subtitle {
  color: #e74c3c;
  font-family: 'Press Start 2P', cursive;
  font-size: 0.6rem;
  letter-spacing: 2px;
}

.question-progress {
  margin-top: 15px;
}

.progress-text {
  display: block;
  font-family: 'Courier Prime', monospace;
  font-size: 0.9rem;
  color: #ecf0f1;
  margin-bottom: 8px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #333;
  border: 2px solid #f1c40f;
}

.progress-fill {
  height: 100%;
  background: #f1c40f;
  transition: width 0.3s ease;
}

.modal-body {
  padding: 20px;
  background: #2c3e50;
}

.content-layout {
  display: flex;
  gap: 20px;
  align-items: stretch;
}

.question-section {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 15px;
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
  border: 4px solid rgba(241, 196, 15, 0.3);
  border-top-color: #f1c40f;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-question p {
  color: #f1c40f;
  font-family: 'Courier Prime', monospace;
  font-size: 1rem;
}

/* 오리 형사 질문 박스 */
.detective-question-box {
  display: flex;
  gap: 15px;
  background: rgba(0, 0, 0, 0.5);
  border: 3px solid #f1c40f;
  padding: 15px;
}

.detective-mini {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  border: 3px solid #fff;
  background: #81ecec;
  border-radius: 4px;
  overflow: hidden;
}

.detective-mini img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.question-content {
  flex: 1;
}

.question-category-badge {
  display: inline-block;
  padding: 4px 10px;
  background: rgba(231, 76, 60, 0.3);
  border: 2px solid #e74c3c;
  font-family: 'Press Start 2P', cursive;
  font-size: 0.5rem;
  color: #e74c3c;
  margin-bottom: 10px;
}

.question-text {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.question-label {
  font-family: 'Press Start 2P', cursive;
  font-size: 0.6rem;
  color: #f1c40f;
}

.question-text p {
  font-family: 'Courier Prime', monospace;
  font-size: 1rem;
  color: #ecf0f1;
  line-height: 1.6;
  margin: 0;
}

/* 답변 섹션 */
.answer-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.answer-label {
  font-family: 'Press Start 2P', cursive;
  font-size: 0.6rem;
  color: #3498db;
}

.user-answer {
  width: 100%;
  min-height: 100px;
  background: #000;
  border: 3px solid #3498db;
  padding: 12px;
  color: #ecf0f1;
  font-family: 'Courier Prime', monospace;
  font-size: 0.95rem;
  resize: vertical;
  transition: border-color 0.3s ease;
}

.user-answer:focus {
  outline: none;
  border-color: #f1c40f;
}

.user-answer::placeholder {
  color: rgba(236, 240, 241, 0.4);
}

/* Mermaid Preview */
.mermaid-preview-section {
  flex: 1;
  min-width: 0;
  background: rgba(0, 0, 0, 0.5);
  border: 3px solid #f1c40f;
  padding: 12px;
  display: flex;
  flex-direction: column;
}

.preview-title {
  font-family: 'Press Start 2P', cursive;
  font-size: 0.55rem;
  color: #f1c40f;
  letter-spacing: 1px;
  margin-bottom: 10px;
}

.mermaid-preview {
  flex: 1;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
}

.mermaid-preview :deep(svg) {
  width: 100%;
  height: auto;
  max-height: 250px;
}

.mermaid-error {
  color: #e74c3c;
  font-size: 0.8rem;
}

/* 푸터 */
.modal-footer {
  padding: 15px 20px;
  border-top: 4px solid #f1c40f;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  background: #000;
}

.btn-skip {
  padding: 12px 20px;
  background: transparent;
  border: 3px solid #7f8c8d;
  color: #7f8c8d;
  font-family: 'Press Start 2P', cursive;
  font-size: 0.6rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-skip:hover {
  background: #7f8c8d;
  color: #000;
}

.btn-submit {
  padding: 12px 25px;
  background: #e74c3c;
  border: 3px solid #000;
  color: #fff;
  font-family: 'Press Start 2P', cursive;
  font-size: 0.6rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.5);
}

.btn-submit:hover:not(:disabled) {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 rgba(0, 0, 0, 0.5);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
