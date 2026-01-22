<template>
  <div class="vibe-cleanup-page">
    <!-- 개발중 모달 (즉시 표시) -->
    <div class="modal-overlay">
      <div class="construction-modal">
        <div class="debug-mode-switch">
          <button class="mode-btn" @click="goToMode('bug-hunt')">🐞 Bug Hunt</button>
          <button class="mode-btn active">✨ Vibe Code Clean Up</button>
        </div>
        <div class="construction-icon">🚧</div>
        <h2 class="construction-title">개발 진행 중</h2>
        <p class="construction-message">
          <strong>Vibe Code Clean Up</strong> 모드는 현재 개발 중입니다.<br><br>
          곧 멋진 리팩토링 챌린지를 만나보실 수 있습니다!<br>
          코드 품질을 향상시키는 다양한 스테이지가 준비될 예정입니다.
        </p>
        <div class="construction-progress">
          <div class="progress-bar">
            <div class="progress-fill" style="width: 45%;"></div>
          </div>
          <span class="progress-text">개발 진행률: 45%</span>
        </div>
        <div class="feature-list">
          <h3>예정된 기능</h3>
          <ul>
            <li>✨ Legacy Code Cleanup</li>
            <li>🔧 Function Decomposition</li>
            <li>📝 Variable Naming Best Practices</li>
            <li>♻️ DRY Principle</li>
            <li>🏗️ SOLID Refactoring</li>
            <li>🎯 Design Patterns</li>
          </ul>
        </div>
        <button class="btn-back" @click="goBack">
          메인으로 돌아가기
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const goBack = () => {
  router.push('/');
};

const goToMode = (mode) => {
  if (mode === 'bug-hunt') {
    router.push('/practice/bug-hunt');
  }
};
</script>

<style scoped>
.vibe-cleanup-page {
  --neon-cyan: #00f3ff;
  --neon-magenta: #ff00ff;
  --neon-yellow: #ffff00;
  --bg-dark: #0a0e17;
  --panel-bg: rgba(26, 31, 46, 0.9);

  background: var(--bg-dark);
  min-height: 100vh;
  font-family: 'Rajdhani', sans-serif;
}

/* 모달 오버레이 */
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
  z-index: 1000;
  padding: 20px;
  overflow-y: auto;
}

.construction-modal {
  background: var(--panel-bg);
  border: 3px solid var(--neon-yellow);
  border-radius: 16px;
  padding: 50px 60px;
  max-width: 600px;
  width: 100%;
  text-align: center;
  box-shadow: 0 0 50px rgba(255, 255, 0, 0.4);
  animation: modalAppear 0.4s ease-out;
}

.debug-mode-switch {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
}

.mode-btn {
  padding: 10px 16px;
  font-family: 'Orbitron';
  font-weight: 700;
  background: transparent;
  border: 1px solid rgba(255, 255, 0, 0.4);
  color: var(--neon-yellow);
  cursor: pointer;
  border-radius: 6px;
  transition: 0.2s ease;
}

.mode-btn.active {
  background: rgba(255, 255, 0, 0.12);
  box-shadow: 0 0 12px rgba(255, 255, 0, 0.35);
}

.mode-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 0 16px rgba(255, 255, 0, 0.45);
}

@keyframes modalAppear {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.construction-icon {
  font-size: 100px;
  margin-bottom: 25px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-15px);
  }
}

.construction-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 2.5em;
  color: var(--neon-yellow);
  margin: 0 0 25px 0;
  text-shadow: 0 0 20px var(--neon-yellow);
  letter-spacing: 2px;
}

.construction-message {
  color: #e5e7eb;
  line-height: 1.9;
  margin-bottom: 35px;
  font-size: 1.15em;
}

.construction-message strong {
  color: var(--neon-yellow);
  font-weight: bold;
}

.construction-progress {
  margin-bottom: 35px;
}

.progress-bar {
  width: 100%;
  height: 24px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 12px;
  border: 1px solid rgba(255, 255, 0, 0.3);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--neon-yellow), var(--neon-cyan));
  border-radius: 12px;
  transition: width 0.3s ease;
  box-shadow: 0 0 15px var(--neon-yellow);
}

.progress-text {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.95em;
  color: var(--neon-yellow);
  font-weight: bold;
}

.feature-list {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 0, 0.2);
  border-radius: 8px;
  padding: 25px;
  margin-bottom: 35px;
  text-align: left;
}

.feature-list h3 {
  font-family: 'Orbitron', sans-serif;
  color: var(--neon-cyan);
  margin: 0 0 15px 0;
  font-size: 1.2em;
  text-align: center;
}

.feature-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-list li {
  color: #a0aec0;
  padding: 8px 0;
  font-size: 1.05em;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.feature-list li:last-child {
  border-bottom: none;
}

.btn-back {
  background: var(--neon-yellow);
  color: #000;
  border: none;
  padding: 18px 45px;
  font-family: 'Orbitron', sans-serif;
  font-weight: bold;
  font-size: 1.15em;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  max-width: 400px;
}

.btn-back:hover {
  box-shadow: 0 0 30px var(--neon-yellow);
  transform: scale(1.02);
  background: #ffd700;
}

.btn-back:active {
  transform: scale(0.98);
}

@media (max-width: 768px) {
  .construction-modal {
    padding: 35px 25px;
  }

  .construction-title {
    font-size: 1.8em;
  }

  .construction-icon {
    font-size: 70px;
  }
}
</style>
