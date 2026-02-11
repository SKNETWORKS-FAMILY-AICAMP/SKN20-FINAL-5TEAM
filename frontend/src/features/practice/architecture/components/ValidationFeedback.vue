<template>
  <div v-if="validationResult" class="validation-feedback-container" :class="statusClass">
    <!-- 배경 오버레이 -->
    <div class="validation-overlay" @click="closeModal" v-if="showOverlay"></div>

    <!-- 피드백 카드 -->
    <div class="validation-card">
      <!-- 헤더 -->
      <div class="validation-header" :class="statusClass">
        <div class="header-content">
          <span class="status-icon">{{ statusIcon }}</span>
          <h3 class="header-title">{{ validationResult.headline }}</h3>
        </div>
        <button class="close-btn" @click="closeModal" aria-label="Close">
          ✕
        </button>
      </div>

      <!-- 메인 메시지 -->
      <div class="main-message">
        <p>{{ validationResult.mainMessage }}</p>
      </div>

      <!-- 제안 (실패 시) -->
      <div v-if="validationResult.suggestion" class="suggestion-box">
        <strong>💡 제안:</strong>
        <p>{{ validationResult.suggestion }}</p>
      </div>

      <!-- 상세 정보 (3단계) -->
      <div v-if="validationResult.details && isPassed" class="details-section">
        <div class="details-title">✅ 검증 단계별 결과</div>

        <!-- Stage 1 -->
        <div class="stage-card">
          <div class="stage-header">
            <span class="stage-badge stage-1">Stage 1</span>
            <span class="stage-name">기본 구조</span>
            <span class="stage-status" :class="{ passed: validationResult.details.stage1.status === '✅' }">
              {{ validationResult.details.stage1.status }}
            </span>
          </div>
          <div class="stage-body">
            <p>✓ 컴포넌트: {{ componentCount }}개</p>
            <p>✓ 연결: {{ connectionCount }}개</p>
            <div v-if="validationResult.details.stage1.isolated.length > 0" class="warning-text">
              ⚠️ 고립된 컴포넌트: {{ validationResult.details.stage1.isolated.join(', ') }}
            </div>
          </div>
        </div>

        <!-- Stage 2 -->
        <div class="stage-card">
          <div class="stage-header">
            <span class="stage-badge stage-2">Stage 2</span>
            <span class="stage-name">필수 요구사항</span>
            <span class="stage-status" :class="{ passed: validationResult.details.stage2.status === '✅' }">
              {{ validationResult.details.stage2.status }}
            </span>
          </div>
          <div class="stage-body">
            <p>필수 컴포넌트: <strong>{{ validationResult.details.stage2.componentFulfillment }}%</strong> 충족</p>
            <p>필수 연결: <strong>{{ validationResult.details.stage2.requiredFlows.fulfilled }}/{{ validationResult.details.stage2.requiredFlows.fulfilled + validationResult.details.stage2.requiredFlows.missing }}</strong> 구현</p>
          </div>
        </div>

        <!-- Stage 3 -->
        <div class="stage-card">
          <div class="stage-header">
            <span class="stage-badge stage-3">Stage 3</span>
            <span class="stage-name">설계 품질 (정보)</span>
            <span class="stage-status info">ℹ️</span>
          </div>
          <div class="stage-body">
            <p>컴포넌트 타입: <strong>{{ validationResult.details.stage3.componentTypes }}가지</strong></p>
            <p>다양성 점수: <strong>{{ validationResult.details.stage3.diversity }}%</strong></p>
          </div>
        </div>
      </div>

      <!-- 경고 리스트 -->
      <div v-if="validationResult.warnings && validationResult.warnings.length > 0" class="warnings-section">
        <div class="warnings-title">⚠️ 개선 권장사항</div>
        <div v-for="(warning, idx) in validationResult.warnings" :key="idx" class="warning-item">
          <span class="warning-dot"></span>
          <p>{{ warning }}</p>
        </div>
      </div>

      <!-- 디버그 정보 (개발용) -->
      <details v-if="showDebugInfo" class="debug-info">
        <summary>🐛 상세 검증 데이터</summary>
        <pre>{{ JSON.stringify(validationResult.details || validationResult.rawValidation, null, 2) }}</pre>
      </details>

      <!-- 액션 버튼 -->
      <div class="action-buttons">
        <button v-if="isPassed" class="btn btn-primary" @click="proceedToExplanation">
          계속 진행 → 설명 입력
        </button>
        <button v-else class="btn btn-secondary" @click="closeModal">
          확인 및 수정
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ValidationFeedback',
  props: {
    validationResult: {
      type: Object,
      default: null
    },
    componentCount: {
      type: Number,
      default: 0
    },
    connectionCount: {
      type: Number,
      default: 0
    },
    showOverlay: {
      type: Boolean,
      default: true
    },
    showDebugInfo: {
      type: Boolean,
      default: false // 개발 환경에서 true로 설정 가능
    }
  },
  emits: ['close', 'proceed'],
  computed: {
    isPassed() {
      return this.validationResult?.passed === true;
    },
    statusClass() {
      if (this.validationResult?.passed) return 'passed';
      return 'failed';
    },
    statusIcon() {
      if (this.validationResult?.passed) return '✅';
      return '❌';
    }
  },
  methods: {
    closeModal() {
      this.$emit('close');
    },
    proceedToExplanation() {
      this.$emit('proceed');
      this.closeModal();
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

.validation-feedback-container {
  --nebula-purple: #6b5ce7;
  --nebula-blue: #4fc3f7;
  --nebula-pink: #f06292;
  --success-color: #4ade80;
  --error-color: #ff6b6b;
  --warning-color: #fbbf24;
  --text-primary: #e8eaed;
  --text-secondary: rgba(232, 234, 237, 0.7);
  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.1);
  --space-deep: #0a0a1a;

  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.validation-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  cursor: pointer;
  z-index: -1;
}

.validation-card {
  background: var(--space-deep);
  border: 2px solid var(--glass-border);
  border-radius: 16px;
  backdrop-filter: blur(20px);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* ===== 헤더 ===== */
.validation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  border-bottom: 2px solid var(--glass-border);
  border-radius: 14px 14px 0 0;
}

.validation-header.passed {
  background: linear-gradient(135deg, rgba(74, 222, 128, 0.1), rgba(79, 195, 247, 0.1));
  border-bottom-color: rgba(74, 222, 128, 0.3);
}

.validation-header.failed {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(251, 191, 36, 0.1));
  border-bottom-color: rgba(255, 107, 107, 0.3);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-icon {
  font-size: 24px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.header-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: 1px;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 24px;
  cursor: pointer;
  padding: 4px 8px;
  transition: color 0.2s;
}

.close-btn:hover {
  color: var(--text-primary);
}

/* ===== 메인 메시지 ===== */
.main-message {
  padding: 20px 24px;
  border-bottom: 1px solid var(--glass-border);
}

.main-message p {
  color: var(--text-primary);
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

/* ===== 제안 박스 ===== */
.suggestion-box {
  padding: 16px 24px;
  background: rgba(251, 191, 36, 0.08);
  border-left: 4px solid var(--warning-color);
  margin: 12px 24px;
  border-radius: 8px;
}

.suggestion-box strong {
  color: var(--warning-color);
  display: block;
  margin-bottom: 8px;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.85rem;
}

.suggestion-box p {
  color: var(--text-secondary);
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.5;
}

/* ===== 상세 정보 섹션 ===== */
.details-section {
  padding: 20px 24px;
  border-top: 1px solid var(--glass-border);
  border-bottom: 1px solid var(--glass-border);
}

.details-title {
  color: var(--nebula-blue);
  font-family: 'Orbitron', sans-serif;
  font-size: 0.85rem;
  font-weight: 700;
  margin-bottom: 12px;
  letter-spacing: 1px;
}

/* ===== 단계 카드 ===== */
.stage-card {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  margin-bottom: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.stage-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.stage-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid var(--glass-border);
}

.stage-badge {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 20px;
  letter-spacing: 1px;
  color: white;
}

.stage-badge.stage-1 {
  background: linear-gradient(135deg, #6b5ce7, #4fc3f7);
}

.stage-badge.stage-2 {
  background: linear-gradient(135deg, #f06292, #ff7043);
}

.stage-badge.stage-3 {
  background: linear-gradient(135deg, #4ade80, #22c55e);
}

.stage-name {
  flex: 1;
  color: var(--text-primary);
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.9rem;
  font-weight: 600;
}

.stage-status {
  font-size: 1rem;
  font-weight: 700;
}

.stage-status.passed {
  color: var(--success-color);
}

.stage-status.info {
  color: var(--nebula-blue);
}

.stage-body {
  padding: 12px 16px;
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.85rem;
}

.stage-body p {
  margin: 6px 0;
  color: var(--text-secondary);
}

.stage-body strong {
  color: var(--text-primary);
}

.warning-text {
  color: var(--warning-color);
  margin-top: 8px;
  font-size: 0.8rem;
}

/* ===== 경고 섹션 ===== */
.warnings-section {
  padding: 20px 24px;
  border-top: 1px solid var(--glass-border);
  border-bottom: 1px solid var(--glass-border);
}

.warnings-title {
  color: var(--warning-color);
  font-family: 'Orbitron', sans-serif;
  font-size: 0.85rem;
  font-weight: 700;
  margin-bottom: 12px;
  letter-spacing: 1px;
}

.warning-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  padding: 10px;
  background: rgba(251, 191, 36, 0.05);
  border-radius: 8px;
  border-left: 3px solid var(--warning-color);
}

.warning-item:last-child {
  margin-bottom: 0;
}

.warning-dot {
  flex-shrink: 0;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--warning-color);
  margin-top: 5px;
}

.warning-item p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.85rem;
  line-height: 1.5;
  flex: 1;
}

/* ===== 디버그 정보 ===== */
.debug-info {
  padding: 12px 24px;
  border-top: 1px solid var(--glass-border);
}

.debug-info summary {
  cursor: pointer;
  color: var(--nebula-purple);
  font-size: 0.8rem;
  font-family: 'Rajdhani', sans-serif;
  user-select: none;
  padding: 8px 0;
}

.debug-info summary:hover {
  color: var(--nebula-blue);
}

.debug-info pre {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 12px;
  color: var(--nebula-blue);
  font-size: 0.75rem;
  overflow-x: auto;
  margin: 12px 0 0 0;
  max-height: 300px;
}

/* ===== 액션 버튼 ===== */
.action-buttons {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
}

.btn {
  flex: 1;
  padding: 14px 20px;
  border: none;
  border-radius: 10px;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
}

.btn-primary {
  background: linear-gradient(135deg, #4ade80, #22c55e);
  color: white;
  border: 2px solid transparent;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(74, 222, 128, 0.3);
}

.btn-secondary {
  background: transparent;
  color: var(--nebula-blue);
  border: 2px solid var(--nebula-blue);
}

.btn-secondary:hover {
  background: rgba(79, 195, 247, 0.1);
  transform: translateY(-2px);
}

/* ===== 스크롤바 ===== */
.validation-card::-webkit-scrollbar {
  width: 8px;
}

.validation-card::-webkit-scrollbar-track {
  background: transparent;
}

.validation-card::-webkit-scrollbar-thumb {
  background: rgba(107, 92, 231, 0.3);
  border-radius: 10px;
}

.validation-card::-webkit-scrollbar-thumb:hover {
  background: rgba(107, 92, 231, 0.5);
}

/* ===== 반응형 ===== */
@media (max-width: 768px) {
  .validation-card {
    width: 95%;
    max-height: 90vh;
  }

  .validation-header {
    padding: 16px;
  }

  .header-title {
    font-size: 1rem;
  }

  .main-message {
    padding: 16px;
  }

  .action-buttons {
    flex-direction: column;
  }

  .stage-header {
    flex-wrap: wrap;
  }

  .stage-name {
    flex: 1 0 100%;
    order: 2;
  }
}
</style>
