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
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

/* === DETECTIVE TOAST MESSAGE (Among Us 스타일) === */
.detective-toast {
  --bg-panel: #1c2128;
  --bg-card: #252c35;
  --border-color: #373e47;
  --cyan: #38ffdd;
  --yellow: #f5f557;
  --green: #4dff77;
  --blue: #4d7fff;
  --white: #d3d4d4;
  --white-dim: #8b949e;

  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  max-width: 700px;
  min-height: 90px;
  display: flex;
  gap: 20px;
  background: var(--bg-panel);
  border: 3px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  z-index: 100;
  cursor: pointer;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
}

/* Toast Type Variations */
.detective-toast.guide {
  border-color: var(--cyan);
}

.detective-toast.connect {
  border-color: var(--blue);
}

.detective-toast.place {
  border-color: var(--green);
}

.detective-toast.hint {
  border-color: var(--yellow);
  animation: hint-toast-pulse 1.5s infinite;
}

@keyframes hint-toast-pulse {
  0%, 100% { box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5); }
  50% { box-shadow: 0 10px 40px rgba(245, 245, 87, 0.3); }
}

.toast-duck {
  width: 60px;
  height: 60px;
  border: 3px solid var(--cyan);
  border-radius: 50%;
  background: #0d1117;
  flex-shrink: 0;
  overflow: hidden;
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
  color: var(--white);
  font-family: 'Nunito', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.6;
}

.detective-toast.connect .toast-message {
  color: var(--blue);
}

.detective-toast.place .toast-message {
  color: var(--green);
}

.detective-toast.hint .toast-message {
  color: var(--yellow);
}

.toast-dismiss {
  color: var(--white-dim);
  font-size: 0.7rem;
  font-family: 'Nunito', sans-serif;
  font-weight: 700;
  text-align: right;
  border-top: 2px solid var(--border-color);
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
