<template>
  <transition name="toast">
    <div v-if="ui.toast.show" class="global-toast" :class="ui.toast.type">
      <div class="toast-icon">
        <i v-if="ui.toast.type === 'success'" data-lucide="check-circle"></i>
        <i v-else-if="ui.toast.type === 'error'" data-lucide="alert-circle"></i>
        <i v-else-if="ui.toast.type === 'warning'" data-lucide="alert-triangle"></i>
        <i v-else data-lucide="info"></i>
      </div>
      <div class="toast-content">
        <p class="toast-message">{{ ui.toast.message }}</p>
      </div>
      <button class="toast-close" @click="ui.toast.show = false">&times;</button>
    </div>
  </transition>
</template>

<script setup>
import { onUpdated, nextTick } from 'vue';
import { useUiStore } from '@/stores/ui';

const ui = useUiStore();

// 아이콘 렌더링을 위해 업데이트 시 호출
onUpdated(() => {
    nextTick(() => {
        if (window.lucide) window.lucide.createIcons();
    });
});
</script>

<style scoped>
.global-toast {
  position: fixed;
  top: 30px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  min-width: 450px;
  max-width: 650px;
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  padding: 24px 32px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(255, 255, 255, 0.05);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.toast-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 14px;
  flex-shrink: 0;
}

/* Success Style */
.global-toast.success {
  border-left: 4px solid #b6ff40;
}
.global-toast.success .toast-icon {
  background: rgba(182, 255, 64, 0.15);
  color: #b6ff40;
}

/* Error Style */
.global-toast.error {
  border-left: 4px solid #ef4444;
}
.global-toast.error .toast-icon {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.toast-content {
  flex: 1;
}

.toast-message {
  margin: 0;
  color: #f8fafc;
  font-size: 1.15rem;
  font-weight: 700;
  line-height: 1.5;
}

.toast-close {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  transition: color 0.2s;
}

.toast-close:hover {
  color: #f8fafc;
}

/* Animation */
.toast-enter-from {
  opacity: 0;
  transform: translate(-50%, -20px);
}
.toast-enter-to {
  opacity: 1;
  transform: translate(-50%, 0);
}
.toast-leave-from {
  opacity: 1;
  transform: translate(-50%, 0);
}
.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, -20px);
}
</style>
