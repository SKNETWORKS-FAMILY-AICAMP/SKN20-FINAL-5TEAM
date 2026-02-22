<template>
  <transition name="fade">
    <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
      <div class="agent-analysis-modal">
        <!-- 헤더 -->
        <header class="analysis-header">
          <div class="header-top">
            <h2>🤖 에이전트 학습 분석</h2>
            <button @click="closeModal" class="btn-close">
              <i data-lucide="x"></i>
            </button>
          </div>
          <p class="header-subtitle">당신의 약점을 AI 에이전트가 분석해드립니다</p>
        </header>

        <!-- 로딩 상태 -->
        <div v-if="isLoading" class="loading-container">
          <div class="spinner"></div>
          <p>에이전트가 분석 중입니다...</p>
          <div class="agent-status">
            <span v-if="currentAgent" :key="currentAgent" class="agent-badge">
              {{ currentAgent }}
            </span>
          </div>
        </div>

        <!-- 결과 표시 -->
        <div v-else-if="analysisResult" class="analysis-result">
          <!-- 종합 분석 -->
          <section class="result-section overview-section">
            <div class="section-header">
              <i data-lucide="zap" class="section-icon"></i>
              <h3>종합 분석</h3>
            </div>
            <p class="overview-text">{{ analysisResult.overview }}</p>
          </section>

          <!-- 상위 약점 (약점 프로필이 있을 때) -->
          <section v-if="weaknessProfile && weaknessProfile.top_weaknesses" class="result-section">
            <div class="section-header">
              <i data-lucide="alert-circle" class="section-icon"></i>
              <h3>주요 약점</h3>
            </div>
            <div class="weakness-tags">
              <span v-for="(weakness, idx) in weaknessProfile.top_weaknesses" :key="idx" class="weakness-tag">
                {{ weakness }}
              </span>
            </div>
          </section>

          <!-- 실행 계획 -->
          <section v-if="analysisResult.action_plan" class="result-section">
            <div class="section-header">
              <i data-lucide="list-checks" class="section-icon"></i>
              <h3>실행 계획</h3>
            </div>
            <div class="action-plan">
              <div v-for="(step, idx) in analysisResult.action_plan" :key="idx" class="action-step">
                <div class="step-number">{{ step.step }}</div>
                <div class="step-content">
                  <h4>{{ step.title }}</h4>
                  <p>{{ step.description }}</p>
                  <span class="step-time">⏱️ {{ step.time_estimate }}</span>
                </div>
              </div>
            </div>
          </section>

          <!-- 추천 문제 -->
          <section v-if="analysisResult.problems && analysisResult.problems.length > 0" class="result-section">
            <div class="section-header">
              <i data-lucide="target" class="section-icon"></i>
              <h3>추천 문제</h3>
            </div>
            <div class="problems-list">
              <div v-for="(problem, idx) in analysisResult.problems" :key="idx" class="problem-card">
                <div class="problem-badge">{{ problem.problem_id }}</div>
                <div class="problem-info">
                  <h5>{{ problem.title }}</h5>
                  <p>{{ problem.reason }}</p>
                </div>
                <button class="btn-problem" @click="openProblem(problem)">
                  도전하기 →
                </button>
              </div>
            </div>
          </section>

          <!-- 격려 메시지 -->
          <section v-if="analysisResult.motivation" class="result-section motivation-section">
            <p>💪 {{ analysisResult.motivation }}</p>
          </section>

          <!-- 액션 버튼 -->
          <div class="modal-actions">
            <button @click="refreshAnalysis" class="btn btn-secondary">
              <i data-lucide="refresh-cw"></i>
              다시 분석
            </button>
            <button @click="closeModal" class="btn btn-primary">
              닫기
            </button>
          </div>
        </div>

        <!-- 에러 상태 -->
        <div v-else-if="error" class="error-container">
          <i data-lucide="alert-triangle" class="error-icon"></i>
          <h3>분석 중 오류 발생</h3>
          <p>{{ error }}</p>
          <button @click="refreshAnalysis" class="btn btn-primary">
            다시 시도
          </button>
        </div>

        <!-- 초기 상태 -->
        <div v-else class="initial-state">
          <div class="initial-content">
            <h3>어떤 분석을 원하시나요?</h3>
            <div class="option-buttons">
              <button @click="analyzeWithMessage('내 약점을 분석해줘')" class="option-btn">
                <i data-lucide="bar-chart-3"></i>
                <span>약점 분석</span>
              </button>
              <button @click="analyzeWithMessage('뭘 공부해야 하나')" class="option-btn">
                <i data-lucide="book"></i>
                <span>학습 가이드</span>
              </button>
              <button @click="analyzeWithMessage('해결할 문제를 추천해줘')" class="option-btn">
                <i data-lucide="target"></i>
                <span>문제 추천</span>
              </button>
              <button @click="analyzeWithMessage('종합 분석해줘')" class="option-btn large">
                <i data-lucide="zap"></i>
                <span>전체 분석</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import { AgentAnalysisService } from '@/services/AgentAnalysisService';

export default {
  name: 'AgentAnalysisModal',
  props: {
    isOpen: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['close'],
  data() {
    return {
      isLoading: false,
      analysisResult: null,
      weaknessProfile: null,
      error: null,
      currentAgent: null,
    };
  },
  methods: {
    async analyzeWithMessage(message) {
      this.isLoading = true;
      this.error = null;
      this.currentAgent = 'Orchestrator Agent';

      try {
        // 병렬로 약점 프로필과 분석 요청
        const [profile, result] = await Promise.all([
          AgentAnalysisService.getWeaknessProfile().catch(() => null),
          this.performAnalysis(message),
        ]);

        this.weaknessProfile = profile;
        this.analysisResult = result;
      } catch (err) {
        this.error = err.message || '분석 중 오류가 발생했습니다';
      } finally {
        this.isLoading = false;
        this.currentAgent = null;
      }
    },

    async performAnalysis(message) {
      // Orchestrator 단계
      this.currentAgent = 'Orchestrator Agent';
      await this.delay(500);

      // Analysis 단계
      this.currentAgent = 'Analysis Agent';
      await this.delay(500);

      // 실제 분석 호출
      const result = await AgentAnalysisService.analyzeLearning(message);

      // Integration 단계
      this.currentAgent = 'Integration Agent';
      await this.delay(500);

      return result;
    },

    delay(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    },

    async refreshAnalysis() {
      if (this.analysisResult) {
        await this.analyzeWithMessage('내 학습을 분석해줘');
      }
    },

    openProblem(problem) {
      // 문제 풀이 페이지로 이동 (추후 구현)
      console.log('문제 열기:', problem);
      this.$emit('close');
    },

    closeModal() {
      this.$emit('close');
      // 모달 닫을 때 상태 초기화
      setTimeout(() => {
        this.analysisResult = null;
        this.weaknessProfile = null;
        this.error = null;
      }, 300);
    },
  },
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out;
}

.agent-analysis-modal {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  animation: slideUp 0.4s ease-out;
}

/* 헤더 */
.analysis-header {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.header-top h2 {
  margin: 0;
  font-size: 24px;
  color: #fff;
}

.btn-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  font-size: 24px;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.btn-close:hover {
  color: #fff;
}

.header-subtitle {
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

/* 로딩 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 24px;
  gap: 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(99, 102, 241, 0.2);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.agent-status {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.agent-badge {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

/* 결과 섹션 */
.analysis-result {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.result-section {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.section-icon {
  width: 20px;
  height: 20px;
  color: #6366f1;
  flex-shrink: 0;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  color: #fff;
  font-weight: 600;
}

/* 종합 분석 */
.overview-section {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  border-color: rgba(99, 102, 241, 0.3);
}

.overview-text {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  font-size: 15px;
}

/* 약점 태그 */
.weakness-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.weakness-tag {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

/* 실행 계획 */
.action-plan {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-step {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.step-number {
  min-width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
}

.step-content h4 {
  margin: 0 0 4px 0;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}

.step-content p {
  margin: 0 0 8px 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  line-height: 1.5;
}

.step-time {
  display: inline-block;
  background: rgba(99, 102, 241, 0.2);
  color: rgba(255, 255, 255, 0.8);
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
}

/* 문제 카드 */
.problems-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.problem-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  transition: all 0.2s;
}

.problem-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(99, 102, 241, 0.3);
}

.problem-badge {
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  min-width: 80px;
  text-align: center;
}

.problem-info {
  flex: 1;
}

.problem-info h5 {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #fff;
  font-weight: 600;
}

.problem-info p {
  margin: 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.btn-problem {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-problem:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

/* 격려 메시지 */
.motivation-section {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
  border-color: rgba(34, 197, 94, 0.3);
  text-align: center;
}

.motivation-section p {
  margin: 0;
  font-size: 15px;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
}

/* 초기 상태 */
.initial-state {
  padding: 40px 24px;
}

.initial-content h3 {
  margin: 0 0 24px 0;
  font-size: 18px;
  color: #fff;
  text-align: center;
}

.option-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}

.option-btn {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: #a5b4fc;
  padding: 16px 12px;
  border-radius: 10px;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.option-btn:hover {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(139, 92, 246, 0.3) 100%);
  border-color: rgba(99, 102, 241, 0.5);
  color: #fff;
}

.option-btn.large {
  grid-column: 1 / -1;
}

.option-btn i {
  width: 24px;
  height: 24px;
}

/* 에러 */
.error-container {
  padding: 40px 24px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.error-icon {
  width: 48px;
  height: 48px;
  color: #ef4444;
}

.error-container h3 {
  margin: 0;
  color: #fff;
}

.error-container p {
  margin: 0;
  color: rgba(255, 255, 255, 0.7);
}

/* 액션 버튼 */
.modal-actions {
  display: flex;
  gap: 12px;
  padding: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
}

.btn {
  flex: 1;
  padding: 12px 16px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

/* 애니메이션 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 스크롤바 스타일 */
.agent-analysis-modal::-webkit-scrollbar {
  width: 8px;
}

.agent-analysis-modal::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

.agent-analysis-modal::-webkit-scrollbar-thumb {
  background: rgba(99, 102, 241, 0.4);
  border-radius: 4px;
}

.agent-analysis-modal::-webkit-scrollbar-thumb:hover {
  background: rgba(99, 102, 241, 0.6);
}

/* 반응형 */
@media (max-width: 600px) {
  .agent-analysis-modal {
    width: 95%;
    max-height: 90vh;
  }

  .option-buttons {
    grid-template-columns: 1fr;
  }

  .option-btn.large {
    grid-column: 1;
  }

  .modal-actions {
    flex-direction: column;
  }
}
</style>
