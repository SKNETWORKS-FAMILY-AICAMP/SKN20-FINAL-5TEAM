<template>
  <transition name="toast-slide">
    <div
      v-if="show"
      class="detective-toast"
      :class="type"
      @click="$emit('dismiss')"
    >
      <div class="toast-duck">
        <img src="/image/duck_det.png" alt="Detective Duck" />
      </div>
      <div class="toast-content">
        <p class="toast-message">{{ message }}</p>
        <span class="toast-dismiss">클릭하여 닫기</span>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'DetectiveToast',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    message: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'guide',
      validator: (value) => ['guide', 'connect', 'place', 'hint'].includes(value)
    }
  },
  emits: ['dismiss']
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Courier+Prime:wght@400;700&display=swap');

/* === DETECTIVE TOAST MESSAGE (심문 패널 스타일) === */
.detective-toast {
  --accent-yellow: #f1c40f;
  --neon-blue: #00f3ff;
  --pixel-font: 'Press Start 2P', cursive;
  --typewriter-font: 'Courier Prime', monospace;

  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  max-width: 700px;
  min-height: 120px;
  display: flex;
  gap: 20px;
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid #444;
  padding: 20px;
  z-index: 100;
  cursor: pointer;
  box-shadow: 0 10px 50px rgba(0, 0, 0, 1);
  /* 테이프 데코 패턴 */
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255, 255, 0, 0.05) 10px, rgba(255, 255, 0, 0.05) 20px);
}

/* Toast Type Variations */
.detective-toast.guide {
  border-color: var(--accent-yellow);
}

.detective-toast.connect {
  border-color: var(--neon-blue);
  box-shadow: 0 10px 50px rgba(0, 0, 0, 1), 0 0 20px rgba(0, 243, 255, 0.2);
}

.detective-toast.place {
  border-color: #2ecc71;
  box-shadow: 0 10px 50px rgba(0, 0, 0, 1), 0 0 20px rgba(46, 204, 113, 0.2);
}

.detective-toast.hint {
  border-color: #e67e22;
  box-shadow: 0 10px 50px rgba(0, 0, 0, 1), 0 0 20px rgba(230, 126, 34, 0.2);
  animation: hint-toast-pulse 1s infinite;
}

@keyframes hint-toast-pulse {
  0%, 100% { box-shadow: 0 10px 50px rgba(0, 0, 0, 1), 0 0 20px rgba(230, 126, 34, 0.2); }
  50% { box-shadow: 0 10px 50px rgba(0, 0, 0, 1), 0 0 35px rgba(230, 126, 34, 0.4); }
}

.toast-duck {
  width: 80px;
  height: 80px;
  border: 2px solid #fff;
  background: #000;
  flex-shrink: 0;
  overflow: hidden;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
}

.toast-duck img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.toast-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.toast-message {
  margin: 0;
  color: var(--accent-yellow);
  font-family: var(--typewriter-font);
  font-size: 1.1rem;
  line-height: 1.5;
  text-shadow: 0 0 5px rgba(241, 196, 15, 0.3);
}

.detective-toast.connect .toast-message {
  color: var(--neon-blue);
  text-shadow: 0 0 5px rgba(0, 243, 255, 0.3);
}

.detective-toast.place .toast-message {
  color: #2ecc71;
  text-shadow: 0 0 5px rgba(46, 204, 113, 0.3);
}

.detective-toast.hint .toast-message {
  color: #e67e22;
  text-shadow: 0 0 5px rgba(230, 126, 34, 0.3);
}

.toast-dismiss {
  color: #7f8c8d;
  font-size: 0.6rem;
  font-family: var(--pixel-font);
  text-align: right;
  border-top: 1px dashed #555;
  padding-top: 10px;
}

/* Toast Slide Animation */
.toast-slide-enter-active {
  animation: toast-in 0.5s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.toast-slide-leave-active {
  animation: toast-out 0.5s cubic-bezier(0.25, 0.8, 0.25, 1);
}

@keyframes toast-in {
  0% {
    opacity: 0;
    transform: translateX(-50%) translateY(150%);
  }
  100% {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

@keyframes toast-out {
  0% {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
  100% {
    opacity: 0;
    transform: translateX(-50%) translateY(150%);
  }
}
</style>
