<template>
  <Teleport to="body">
    <div class="tutorial-overlay" @click.self="handleOverlayClick">
      <!-- 하이라이트 컷아웃 -->
      <div
        class="tutorial-highlight"
        :style="highlightStyle"
      ></div>

      <!-- 설명 카드 -->
      <div class="tutorial-card" :style="cardStyle">
        <div class="card-header">
          <span class="step-indicator">{{ currentStep + 1 }} / {{ steps.length }}</span>
          <span class="step-title">{{ steps[currentStep].title }}</span>
        </div>
        <p class="card-description">{{ steps[currentStep].description }}</p>
        <div class="step-dots">
          <span
            v-for="(_, idx) in steps"
            :key="idx"
            class="dot"
            :class="{ active: idx === currentStep, done: idx < currentStep }"
          ></span>
        </div>
        <div class="card-actions">
          <button class="btn-skip" @click="skip">SKIP</button>
          <button class="btn-next" @click="next">
            {{ currentStep === steps.length - 1 ? 'FINISH' : 'NEXT' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
export default {
  name: 'BugHuntTutorialOverlay',
  emits: ['complete', 'skip'],
  props: {
    tutorialSteps: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      currentStep: 0,
      steps: this.tutorialSteps,
      targetRect: null,
      cardStyle: {},
      resizeObserver: null
    };
  },
  computed: {
    highlightStyle() {
      if (!this.targetRect) {
        return { display: 'none' };
      }
      const padding = 6;
      const r = this.targetRect;
      return {
        top: `${r.top - padding}px`,
        left: `${r.left - padding}px`,
        width: `${r.width + padding * 2}px`,
        height: `${r.height + padding * 2}px`
      };
    }
  },
  mounted() {
    this.$nextTick(() => this.updatePosition());
    window.addEventListener('resize', this.updatePosition);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.updatePosition);
  },
  methods: {
    updatePosition() {
      // Re-calculate position with a small delay for DOM rendering
      setTimeout(() => {
        const step = this.steps[this.currentStep];
        const el = document.querySelector(step.selector);
        if (!el) {
          console.warn(`[BugHuntTutorial] Element not found for selector: ${step.selector}`);
          this.targetRect = null;
          this.cardStyle = {};
          return;
        }

        const rect = el.getBoundingClientRect();
        this.targetRect = rect;
        this.cardStyle = this.computeCardStyle(rect, step.cardPosition);
      }, 50);
    },

    computeCardStyle(rect, position) {
      const cardWidth = 340;
      const cardGap = 16;
      const style = { width: `${cardWidth}px` };
      const vw = window.innerWidth;
      const vh = window.innerHeight;

      switch (position) {
        case 'right': {
          let left = rect.right + cardGap;
          if (left + cardWidth > vw - 16) {
            left = rect.left - cardWidth - cardGap;
          }
          let top = rect.top + rect.height / 2 - 100;
          top = Math.max(16, Math.min(top, vh - 260));
          style.left = `${left}px`;
          style.top = `${top}px`;
          break;
        }
        case 'left': {
          let left = rect.left - cardWidth - cardGap;
          if (left < 16) {
            left = rect.right + cardGap;
          }
          let top = rect.top + rect.height / 2 - 100;
          top = Math.max(16, Math.min(top, vh - 260));
          style.left = `${left}px`;
          style.top = `${top}px`;
          break;
        }
        case 'bottom': {
          let top = rect.bottom + cardGap;
          if (top + 220 > vh - 16) {
            top = rect.top - 220 - cardGap;
          }
          let left = rect.left + rect.width / 2 - cardWidth / 2;
          left = Math.max(16, Math.min(left, vw - cardWidth - 16));
          style.left = `${left}px`;
          style.top = `${top}px`;
          break;
        }
        case 'top': {
          let top = rect.top - 220 - cardGap;
          if (top < 16) {
            top = rect.bottom + cardGap;
          }
          let left = rect.left + rect.width / 2 - cardWidth / 2;
          left = Math.max(16, Math.min(left, vw - cardWidth - 16));
          style.left = `${left}px`;
          style.top = `${top}px`;
          break;
        }
      }

      return style;
    },

    next() {
      if (this.currentStep < this.steps.length - 1) {
        this.currentStep++;
        this.$nextTick(() => this.updatePosition());
      } else {
        this.$emit('complete');
      }
    },

    skip() {
      this.$emit('skip');
    },

    handleOverlayClick() {
      this.next();
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

.tutorial-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(5, 5, 20, 0.05);
  animation: overlayFadeIn 0.3s ease;
}

@keyframes overlayFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.tutorial-highlight {
  position: fixed;
  border-radius: 10px;
  box-shadow: 0 0 0 9999px rgba(5, 5, 20, 0.75);
  border: 2px solid rgba(79, 195, 247, 0.7);
  pointer-events: none;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 10000;
  animation: highlightPulse 2s ease-in-out infinite;
}

@keyframes highlightPulse {
  0%, 100% {
    border-color: rgba(79, 195, 247, 0.7);
    box-shadow: 0 0 0 9999px rgba(5, 5, 20, 0.75), 0 0 20px rgba(79, 195, 247, 0.3);
  }
  50% {
    border-color: rgba(107, 92, 231, 0.9);
    box-shadow: 0 0 0 9999px rgba(5, 5, 20, 0.75), 0 0 35px rgba(107, 92, 231, 0.5);
  }
}

.tutorial-card {
  position: fixed;
  z-index: 10001;
  background: linear-gradient(135deg, rgba(18, 18, 42, 0.95) 0%, rgba(26, 26, 58, 0.95) 100%);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(107, 92, 231, 0.4);
  border-radius: 16px;
  padding: 24px;
  color: #e8eaed;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.4),
    0 0 60px rgba(107, 92, 231, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  animation: cardSlideIn 0.4s ease;
}

@keyframes cardSlideIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.step-indicator {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.65rem;
  font-weight: 700;
  color: #4fc3f7;
  background: rgba(79, 195, 247, 0.12);
  border: 1px solid rgba(79, 195, 247, 0.3);
  border-radius: 20px;
  padding: 4px 12px;
  letter-spacing: 1px;
  white-space: nowrap;
}

.step-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.85rem;
  font-weight: 700;
  color: #e8eaed;
  letter-spacing: 2px;
}

.card-description {
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.95rem;
  font-weight: 500;
  line-height: 1.6;
  color: rgba(232, 234, 237, 0.85);
  margin: 0 0 18px 0;
}

.step-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 18px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.dot.active {
  background: #4fc3f7;
  border-color: #4fc3f7;
  box-shadow: 0 0 8px rgba(79, 195, 247, 0.6);
  transform: scale(1.3);
}

.dot.done {
  background: #6b5ce7;
  border-color: #6b5ce7;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-skip,
.btn-next {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 2px;
  border-radius: 30px;
  padding: 8px 22px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
}

.btn-skip {
  background: transparent;
  color: rgba(232, 234, 237, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.btn-skip:hover {
  color: rgba(232, 234, 237, 0.8);
  border-color: rgba(255, 255, 255, 0.3);
}

.btn-next {
  background: linear-gradient(135deg, #6b5ce7, #4fc3f7);
  color: #ffffff;
  border: none;
  box-shadow: 0 0 20px rgba(107, 92, 231, 0.3);
}

.btn-next:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 30px rgba(107, 92, 231, 0.5);
}

.btn-next:active {
  transform: translateY(0);
}
</style>
