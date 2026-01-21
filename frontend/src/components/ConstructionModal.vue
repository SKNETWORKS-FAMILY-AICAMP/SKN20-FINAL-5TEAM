<!--
  역할: '공사 중' 상태인 페이지/기능 접근 시 보여주는 안내 모달
  디자인: 네온 옐로우/오렌지 경고 테마
-->
<template>
  <transition name="fade">
    <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
      <div class="auth-container construction-card">
        <div class="construction-icon-wrapper">
          <i data-lucide="hard-hat" class="construction-icon"></i>
        </div>
        
        <header class="auth-header">
          <div class="auth-badge warning">System Alert</div>
          <h2 class="auth-title">Under Construction 🚧</h2>
          <p class="auth-subtitle">
            해당 훈련 구역은 현재 <strong>확장 공사 중</strong>입니다.<br>
            더 멋진 퀘스트로 찾아뵐게요!
          </p>
        </header>

        <div class="construction-visual">
          <div class="progress-bar-container">
            <div class="progress-bar-stripe"></div>
          </div>
          <span class="loading-text">Building Logic blocks...</span>
        </div>

        <footer class="auth-footer">
          <button class="btn btn-primary" @click="$emit('close')" style="width: 100%;">
            확인 (Okay)
          </button>
        </footer>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'ConstructionModal',
  props: {
    isOpen: {
      type: Boolean,
      required: true
    }
  },
  updated() {
    // Lucide 아이콘 렌더링
    this.$nextTick(() => {
        if (window.lucide) window.lucide.createIcons();
    });
  }
}
</script>

<style scoped>
.construction-card {
  max-width: 400px;
  border: 1px solid rgba(255, 200, 0, 0.3);
  box-shadow: 0 0 30px rgba(255, 180, 0, 0.1);
}

.construction-icon-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
}

.construction-icon {
  width: 64px;
  height: 64px;
  color: #fbbf24; /* Amber-400 */
  animation: bounce-slow 2s infinite;
}

.construction-visual {
  margin: 1.5rem 0;
  text-align: center;
}

.progress-bar-container {
  width: 100%;
  height: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  overflow: hidden;
  position: relative;
  margin-bottom: 0.5rem;
}

.progress-bar-stripe {
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    45deg,
    #fbbf24,
    #fbbf24 10px,
    #d97706 10px,
    #d97706 20px
  );
  animation: move-stripe 1s linear infinite;
}

.loading-text {
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  color: var(--text-muted);
}

@keyframes bounce-slow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes move-stripe {
  0% { transform: translateX(0); }
  100% { transform: translateX(-20px); }
}

/* Inherit auth-badge color override */
.auth-badge.warning {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.3);
}
</style>
