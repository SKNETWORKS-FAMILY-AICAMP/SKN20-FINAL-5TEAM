<template>
  <Teleport to="body">
    <transition name="fade">
      <div v-if="isVisible" class="strategy-overlay">
        <div class="strategy-backdrop" @click="$emit('close')"></div>
        <div class="strategy-card">
          <div class="strategy-header">
            <span class="strategy-title">
              🎯 Step {{ currentStep }} 해결 전략
            </span>
            <button class="close-btn" @click="$emit('close')">×</button>
          </div>
          <div class="strategy-body">
            <label class="strategy-label">
              💭 어떤 전략으로 이 버그를 해결했나요?
            </label>
            <textarea
              v-model="strategyText"
              @keydown.ctrl.enter="handleSubmit"
              class="strategy-textarea"
              placeholder="버그 해결 전략을 작성해주세요...&#10;&#10;• 어떤 문제를 발견했나요?&#10;• 왜 이렇게 수정했나요?&#10;• 어떤 효과가 있나요?"
              rows="10"
              autofocus
            ></textarea>
            <div class="strategy-hint">💡 Ctrl + Enter로 빠르게 제출</div>
          </div>
          <div class="strategy-footer">
            <button
              class="submit-btn"
              @click="handleSubmit"
              :disabled="!strategyText.trim()"
            >
              📝 전략 제출하기
            </button>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script>
export default {
  name: 'StrategyOverlay',
  props: {
    isVisible: {
      type: Boolean,
      required: true
    },
    currentStep: {
      type: Number,
      required: true
    }
  },
  emits: ['submit', 'close'],
  data() {
    return {
      strategyText: ''
    };
  },
  methods: {
    handleSubmit() {
      if (!this.strategyText.trim()) return;
      this.$emit('submit', this.strategyText);
      this.strategyText = ''; // 제출 후 초기화
    }
  },
  watch: {
    isVisible(newVal) {
      // 오버레이가 열릴 때마다 초기화
      if (newVal) {
        this.strategyText = '';
      }
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

/* 오버레이 컨테이너 */
.strategy-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 반투명 배경 (코드 에디터 살짝 보임) */
.strategy-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(5, 5, 20, 0.7);
  backdrop-filter: blur(4px);
}

/* 전략 카드 (중앙 정렬, 코드를 완전히 가리지 않음) */
.strategy-card {
  position: relative;
  z-index: 2001;
  width: 600px;
  max-width: 90vw;
  max-height: 70vh;
  background: linear-gradient(135deg, rgba(18, 18, 42, 0.95), rgba(26, 26, 58, 0.95));
  border: 2px solid rgba(107, 92, 231, 0.5);
  border-radius: 16px;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.4),
    0 0 60px rgba(107, 92, 231, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  animation: cardSlideIn 0.4s ease;
}

@keyframes cardSlideIn {
  from { opacity: 0; transform: translateY(-20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* 헤더 */
.strategy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(107, 92, 231, 0.3);
}

.strategy-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: #4fc3f7;
  letter-spacing: 1px;
}

.close-btn {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.6);
  font-size: 1.5rem;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.4);
}

/* 본문 */
.strategy-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
}

.strategy-label {
  font-family: 'Rajdhani', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: rgba(232, 234, 237, 0.9);
}

.strategy-textarea {
  flex: 1;
  min-height: 200px;
  background: rgba(0, 0, 0, 0.5);
  border: 2px solid rgba(79, 195, 247, 0.3);
  border-radius: 8px;
  padding: 16px;
  color: #fff;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;
  line-height: 1.6;
  resize: vertical;
  transition: all 0.3s ease;
}

.strategy-textarea:focus {
  outline: none;
  border-color: rgba(79, 195, 247, 0.6);
  box-shadow: 0 0 20px rgba(79, 195, 247, 0.2);
}

.strategy-hint {
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.85rem;
  color: rgba(232, 234, 237, 0.5);
  font-style: italic;
}

/* 푸터 */
.strategy-footer {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid rgba(107, 92, 231, 0.3);
}

.submit-btn {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 2px;
  background: linear-gradient(135deg, #6b5ce7, #4fc3f7);
  color: #ffffff;
  border: none;
  border-radius: 30px;
  padding: 12px 28px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  box-shadow: 0 0 20px rgba(107, 92, 231, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 0 30px rgba(107, 92, 231, 0.5);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 반응형 */
@media (max-width: 768px) {
  .strategy-card {
    width: 95vw;
    max-height: 80vh;
    padding: 20px;
  }

  .strategy-title {
    font-size: 0.9rem;
  }

  .strategy-textarea {
    min-height: 150px;
    font-size: 0.85rem;
  }
}
</style>
