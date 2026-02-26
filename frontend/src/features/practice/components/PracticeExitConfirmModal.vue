<template>
  <transition name="exit-modal-fade">
    <div v-if="isActive" class="exit-modal-overlay">
      <div class="exit-modal-card" role="dialog" aria-modal="true" aria-labelledby="exit-modal-title">
        <div class="exit-modal-header">
          <div class="exit-modal-icon">⚠️</div>
          <h3 id="exit-modal-title" class="exit-modal-title">{{ title }}</h3>
        </div>

        <div class="exit-modal-body">
          <p class="exit-modal-main">{{ message }}</p>
          <p class="exit-modal-sub">{{ subMessage }}</p>
        </div>

        <div class="exit-modal-actions">
          <button type="button" class="exit-btn exit-btn-cancel" @click="$emit('cancel')">
            {{ cancelText }}
          </button>
          <button type="button" class="exit-btn exit-btn-confirm" @click="$emit('confirm')">
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'PracticeExitConfirmModal',
  props: {
    isActive: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: '실습 종료'
    },
    message: {
      type: String,
      default: '실습을 종료할까요?'
    },
    subMessage: {
      type: String,
      default: '진행 중인 내용은 저장되지 않습니다.'
    },
    cancelText: {
      type: String,
      default: '계속 진행하기'
    },
    confirmText: {
      type: String,
      default: '종료하기'
    }
  },
  emits: ['confirm', 'cancel']
};
</script>

<style scoped>
.exit-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(9, 14, 26, 0.72);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.exit-modal-card {
  width: min(92vw, 440px);
  border-radius: 14px;
  padding: 22px 20px 18px;
  border: 1px solid rgba(79, 195, 247, 0.35);
  background: linear-gradient(160deg, rgba(9, 14, 26, 0.96), rgba(17, 24, 39, 0.96));
  box-shadow: 0 16px 36px rgba(2, 6, 23, 0.45), 0 0 20px rgba(79, 195, 247, 0.18);
}

.exit-modal-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.exit-modal-icon {
  font-size: 1.1rem;
}

.exit-modal-title {
  color: #e2e8f0;
  font-size: 1.05rem;
  font-weight: 700;
}

.exit-modal-body {
  margin-top: 12px;
}

.exit-modal-main {
  color: #f8fafc;
  font-size: 0.96rem;
  line-height: 1.45;
}

.exit-modal-sub {
  margin-top: 5px;
  color: #94a3b8;
  font-size: 0.84rem;
  line-height: 1.4;
}

.exit-modal-actions {
  margin-top: 16px;
  display: flex;
  gap: 10px;
}

.exit-btn {
  flex: 1;
  border-radius: 8px;
  padding: 10px 12px;
  cursor: pointer;
  border: 1px solid transparent;
  font-size: 0.86rem;
  font-weight: 700;
  transition: all 0.2s ease;
}

.exit-btn-cancel {
  background: rgba(79, 195, 247, 0.08);
  border-color: rgba(79, 195, 247, 0.35);
  color: #4fc3f7;
}

.exit-btn-cancel:hover {
  background: rgba(79, 195, 247, 0.18);
  color: #f8fafc;
}

.exit-btn-confirm {
  background: rgba(255, 51, 102, 0.1);
  border-color: rgba(255, 51, 102, 0.7);
  color: #ff5c87;
}

.exit-btn-confirm:hover {
  background: #ff3366;
  color: #ffffff;
  box-shadow: 0 0 18px rgba(255, 51, 102, 0.38);
}

.exit-modal-fade-enter-active,
.exit-modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.exit-modal-fade-enter-from,
.exit-modal-fade-leave-to {
  opacity: 0;
}
</style>
