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
        <span class="toast-dismiss">CLICK_TO_DISMISS</span>
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
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&display=swap');

/* === DETECTIVE TOAST MESSAGE (Terminal 2077 스타일) === */
.detective-toast {
  --accent-green: #A3FF47;
  --accent-cyan: #00f3ff;
  --accent-pink: #ec4899;
  --terminal-font: 'Fira Code', monospace;

  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  max-width: 700px;
  min-height: 100px;
  display: flex;
  gap: 20px;
  background: rgba(5, 7, 10, 0.95);
  border: 1px solid rgba(163, 255, 71, 0.3);
  backdrop-filter: blur(10px);
  padding: 20px;
  z-index: 100;
  cursor: pointer;
}

/* Toast Type Variations */
.detective-toast.guide {
  border-color: var(--accent-green);
  box-shadow: 0 0 30px rgba(163, 255, 71, 0.15);
}

.detective-toast.connect {
  border-color: var(--accent-cyan);
  box-shadow: 0 0 30px rgba(0, 243, 255, 0.2);
}

.detective-toast.place {
  border-color: var(--accent-green);
  box-shadow: 0 0 30px rgba(163, 255, 71, 0.2);
}

.detective-toast.hint {
  border-color: var(--accent-green);
  box-shadow: 0 0 30px rgba(163, 255, 71, 0.2);
  animation: hint-toast-pulse 1.5s infinite;
}

@keyframes hint-toast-pulse {
  0%, 100% { box-shadow: 0 0 30px rgba(163, 255, 71, 0.2); }
  50% { box-shadow: 0 0 50px rgba(163, 255, 71, 0.4); }
}

.toast-duck {
  width: 70px;
  height: 70px;
  border: 2px solid var(--accent-green);
  background: #000;
  flex-shrink: 0;
  overflow: hidden;
  box-shadow: 0 0 15px rgba(163, 255, 71, 0.3);
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
  color: var(--accent-green);
  font-family: var(--terminal-font);
  font-size: 0.95rem;
  line-height: 1.6;
  text-shadow: 0 0 8px rgba(163, 255, 71, 0.4);
}

.detective-toast.connect .toast-message {
  color: var(--accent-cyan);
  text-shadow: 0 0 8px rgba(0, 243, 255, 0.4);
}

.detective-toast.place .toast-message {
  color: var(--accent-green);
  text-shadow: 0 0 8px rgba(163, 255, 71, 0.4);
}

.detective-toast.hint .toast-message {
  color: var(--accent-green);
  text-shadow: 0 0 8px rgba(163, 255, 71, 0.4);
}

.toast-dismiss {
  color: rgba(163, 255, 71, 0.4);
  font-size: 0.65rem;
  font-family: var(--terminal-font);
  text-align: right;
  border-top: 1px dashed rgba(163, 255, 71, 0.2);
  padding-top: 10px;
  letter-spacing: 1px;
}

/* Toast Slide Animation */
.toast-slide-enter-active {
  animation: toast-in 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-slide-leave-active {
  animation: toast-out 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes toast-in {
  0% {
    opacity: 0;
    transform: translateX(-50%) translateY(100%);
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
    transform: translateX(-50%) translateY(100%);
  }
}
</style>
