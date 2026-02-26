<template>
  <transition name="modal-fade">
    <div v-if="isActive" class="exit-modal-overlay">
      <div class="exit-modal-content">
        <!-- 헤더 -->
        <div class="modal-header">
          <div class="header-icon">⚠️</div>
          <h2 class="modal-title">SESSION TERMINATION</h2>
          <div class="header-line"></div>
        </div>

        <!-- 메시지 -->
        <div class="modal-message">
          <p class="warning-text">시스템 아키텍처 설계를 종료하시겠습니까?</p>
          <p class="sub-text">진행 중인 내용은 저장되지 않습니다.</p>
        </div>

        <!-- 버튼 -->
        <div class="modal-actions">
          <button class="btn-cancel" @click="handleCancel">
            <span>CONTINUE SESSION</span>
          </button>
          <button class="btn-confirm" @click="handleConfirm">
            <span>EXIT</span>
          </button>
        </div>

        <!-- 장식 요소 -->
        <div class="corner-decor top-left"></div>
        <div class="corner-decor top-right"></div>
        <div class="corner-decor bottom-left"></div>
        <div class="corner-decor bottom-right"></div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'ExitConfirmModal',
  props: {
    isActive: {
      type: Boolean,
      default: false
    }
  },
  emits: ['confirm', 'cancel'],
  methods: {
    handleCancel() {
      this.$emit('cancel');
    },
    handleConfirm() {
      this.$emit('confirm');
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');

/* === 오버레이 === */
.exit-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(9, 9, 16, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

/* === 모달 컨테이너 === */
.exit-modal-content {
  position: relative;
  width: 90%;
  max-width: 450px;
  background: linear-gradient(135deg, rgba(18, 18, 35, 0.95), rgba(10, 15, 30, 0.95));
  border: 2px solid #bc13fe;
  border-radius: 20px;
  padding: 40px 30px;
  box-shadow:
    0 0 50px rgba(188, 19, 254, 0.3),
    inset 0 0 30px rgba(188, 19, 254, 0.1);
  backdrop-filter: blur(10px);
  animation: modal-scale-in 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modal-scale-in {
  from {
    opacity: 0;
    transform: scale(0.85);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* === 헤더 === */
.modal-header {
  text-align: center;
  margin-bottom: 25px;
}

.header-icon {
  font-size: 3rem;
  margin-bottom: 12px;
  animation: icon-pulse 1.5s infinite;
}

@keyframes icon-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.modal-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.5rem;
  font-weight: 900;
  color: #bc13fe;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin: 0;
  text-shadow: 0 0 20px rgba(188, 19, 254, 0.5);
}

.header-line {
  height: 2px;
  background: linear-gradient(90deg, transparent, #bc13fe, transparent);
  margin-top: 15px;
  border-radius: 1px;
}

/* === 메시지 === */
.modal-message {
  margin-bottom: 30px;
  text-align: center;
}

.warning-text {
  font-family: 'Rajdhani', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 8px 0;
  line-height: 1.5;
}

.sub-text {
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.85rem;
  color: #a0aec0;
  margin: 0;
  line-height: 1.4;
}

/* === 버튼 === */
.modal-actions {
  display: flex;
  gap: 12px;
}

.btn-cancel,
.btn-confirm {
  flex: 1;
  padding: 12px 20px;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid;
}

.btn-cancel {
  background: transparent;
  border-color: #00f3ff;
  color: #00f3ff;
  box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
}

.btn-cancel:hover {
  background: rgba(0, 243, 255, 0.1);
  box-shadow: 0 0 25px rgba(0, 243, 255, 0.4);
  transform: translateY(-2px);
}

.btn-confirm {
  background: linear-gradient(135deg, #bc13fe, #ff00ff);
  border-color: transparent;
  color: #ffffff;
  box-shadow: 0 0 20px rgba(188, 19, 254, 0.4);
}

.btn-confirm:hover {
  box-shadow: 0 0 30px rgba(188, 19, 254, 0.6);
  transform: translateY(-2px);
}

/* === 장식 코너 === */
.corner-decor {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid #00f3ff;
  opacity: 0.4;
}

.corner-decor.top-left {
  top: 15px;
  left: 15px;
  border-right: none;
  border-bottom: none;
  border-radius: 8px 0 0 0;
}

.corner-decor.top-right {
  top: 15px;
  right: 15px;
  border-left: none;
  border-bottom: none;
  border-radius: 0 8px 0 0;
}

.corner-decor.bottom-left {
  bottom: 15px;
  left: 15px;
  border-right: none;
  border-top: none;
  border-radius: 0 0 0 8px;
}

.corner-decor.bottom-right {
  bottom: 15px;
  right: 15px;
  border-left: none;
  border-top: none;
  border-radius: 0 0 8px 0;
}

/* === 트랜지션 === */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
