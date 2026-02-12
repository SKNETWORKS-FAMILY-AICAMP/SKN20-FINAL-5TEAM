<template>
  <div class="arch-challenge-container among-theme">
    <!-- 별 배경 -->
    <div class="stars-container">
      <div class="stars"></div>
      <div class="stars2"></div>
      <div class="stars3"></div>
    </div>

    <!-- 성운 오버레이 -->
    <div class="nebula-overlay"></div>

    <!-- 인트로 씬 (비주얼 노벨 스타일) -->
    <IntroScene
      v-if="showIntro"
      :intro-lines="introLines"
      @enter-game="onEnterGame"
    />

    <!-- 평가 결과 화면 -->
    <EvaluationResultScreen
      v-else-if="showResultScreen"
      :result="evaluationResult"
      :problem="currentProblem"
      :is-loading="isEvaluating"
      @retry="handleRetry"
    />

    <!-- 메인 게임 화면 -->
    <template v-else>
      <div class="game-container">
        <!-- 케이스 파일 패널 (좌측 사이드바) -->
        <CaseFilePanel
          :problem="currentProblem"
          :is-connection-mode="isConnectionMode"
          :can-evaluate="droppedComponents.length > 0"
          :is-evaluating="isEvaluating"
          :mermaid-code="mermaidCode"
          @start-evaluation="openEvaluationModal"
        />

        <!-- 메인 작업 영역 -->
        <div class="main-workspace">
          <!-- 헤더 바 -->
          <GameHeader
            :is-connection-mode="isConnectionMode"
            :is-hint-active="isHintActive"
            @toggle-mode="toggleMode"
            @clear-canvas="clearCanvas"
            @toggle-hint="toggleHint"
          />

          <!-- 작업 공간 (툴박스 + 캔버스) -->
          <div class="workspace-content">
            <!-- 좌측 툴박스 (컴포넌트 팔레트) -->
            <ComponentPalette
              :required-types="currentProblem?.expectedComponents || []"
              :is-hint-active="isHintActive"
              @drag-start="onPaletteDragStart"
              class="toolbox-panel"
            />

            <!-- 캔버스 영역 -->
            <ArchitectureCanvas
              :components="droppedComponents"
              :connections="connections"
              :is-connection-mode="isConnectionMode"
              :hide-header="true"
              @toggle-mode="toggleMode"
              @clear-canvas="clearCanvas"
              @component-dropped="onComponentDropped"
              @component-moved="onComponentMoved"
              @component-renamed="onComponentRenamed"
              @component-deleted="onComponentDeleted"
              @connection-created="onConnectionCreated"
              class="canvas-panel"
            />
          </div>
        </div>
      </div>

      <!-- 튜토리얼 오버레이 -->
      <TutorialOverlay
        v-if="showTutorial"
        @complete="onTutorialComplete"
        @skip="onTutorialComplete"
      />

      <!-- 오리 형사 토스트 메시지 -->
      <DetectiveToast
        :show="showToast"
        :message="toastMessage"
        :type="toastType"
        @dismiss="dismissToast"
      />

      <!-- Deep Dive 모달 (설명 입력 + 꼬리질문 순차 처리) -->
      <DeepDiveModal
        :is-active="isDeepDiveModalActive"
        :question="deepDiveQuestion"
        :is-generating="isGeneratingDeepDive"
        :current-question="currentQuestionIndex + 1"
        :total-questions="deepDiveQuestions.length"
        :category="deepDiveQuestions[currentQuestionIndex]?.category || ''"
        :mermaid-code="mermaidCode"
        :phase="evaluationPhase"
        :validation-error="answerValidationError"
        @submit="submitDeepDiveAnswer"
        @submit-explanation="submitUserExplanation"
      />

      <!-- ✅ NEW: 검증 피드백 모달 -->
      <ValidationFeedback
        v-if="showValidationFeedback"
        :validation-result="validationResult"
        :component-count="droppedComponents.length"
        :connection-count="connections.length"
        :show-debug-info="isValidationDebugMode"
        @close="closeValidationFeedback"
        @proceed="proceedFromValidation"
      />
    </template>
  </div>
</template>

<script>
import mermaid from 'mermaid';

// Components
import ComponentPalette from './components/ComponentPalette.vue';
import ArchitectureCanvas from './components/ArchitectureCanvas.vue';
import DeepDiveModal from './components/DeepDiveModal.vue';
import EvaluationResultScreen from './components/EvaluationResultScreen.vue';
import DetectiveToast from './components/DetectiveToast.vue';
import GameHeader from './components/GameHeader.vue';
import IntroScene from './components/IntroScene.vue';
import CaseFilePanel from './components/CaseFilePanel.vue';
import TutorialOverlay from './components/TutorialOverlay.vue';
// ✅ NEW: 검증 피드백 컴포넌트
import ValidationFeedback from './components/ValidationFeedback.vue';

// Composables
import { useToast } from './composables/useToast';
import { useHint } from './composables/useHint';
import { useCanvasState } from './composables/useCanvasState';
import { useEvaluation } from './composables/useEvaluation';

// Services & Utils
import { fetchProblems } from './services/architectureApiFastTest';
import { transformProblems } from './utils/architectureUtils';

export default {
  name: 'SystemArchitectureChallenge',
  components: {
    ComponentPalette,
    ArchitectureCanvas,
    DeepDiveModal,
    EvaluationResultScreen,
    DetectiveToast,
    GameHeader,
    IntroScene,
    CaseFilePanel,
    TutorialOverlay,
    ValidationFeedback
  },
  data() {
    return {
      // Intro State
      showIntro: true,
      showTutorial: false,
      introLines: [
        "[SYSTEM ALERT] 아키텍트님, 마더 서버에 이상 징후가 감지되었습니다. 꽥!",
        "오염된 AI들이 환각(Hallucination)에 빠져 시스템을 붕괴시키고 있습니다.",
        "당신만이 이 상황을 복구할 수 있습니다.",
        "올바른 시스템 아키텍처를 설계하여 데이터 무결성을 확보하세요!",
        "[PROTOCOL READY] 복구 터미널에 접속합니다..."
      ],

      // Problem State
      currentProblemIndex: 0,
      problems: [],

      // ✅ NEW: 검증 상태
      showValidationFeedback: false,
      validationResult: null,
      isValidationDebugMode: false // 개발 환경에서 true로 설정
    };
  },
  setup() {
    // Initialize composables
    const toast = useToast();
    const hint = useHint();
    const canvas = useCanvasState();
    const evaluation = useEvaluation();

    return {
      // Toast
      showToast: toast.showToast,
      toastMessage: toast.toastMessage,
      toastType: toast.toastType,
      showToastMessage: toast.showToastMessage,
      dismissToast: toast.dismissToast,
      cleanupToast: toast.cleanup,

      // Hint
      isHintActive: hint.isHintActive,
      toggleHintComposable: hint.toggleHint,
      cleanupHint: hint.cleanup,

      // Canvas
      isConnectionMode: canvas.isConnectionMode,
      droppedComponents: canvas.droppedComponents,
      connections: canvas.connections,
      mermaidCode: canvas.mermaidCode,
      toggleModeComposable: canvas.toggleMode,
      clearCanvasComposable: canvas.clearCanvas,
      onComponentDroppedComposable: canvas.onComponentDropped,
      onComponentMovedComposable: canvas.onComponentMoved,
      onComponentRenamedComposable: canvas.onComponentRenamed,
      onComponentDeletedComposable: canvas.onComponentDeleted,
      onConnectionCreatedComposable: canvas.onConnectionCreated,

      // Evaluation
      isEvaluating: evaluation.isEvaluating,
      evaluationResult: evaluation.evaluationResult,
      showResultScreen: evaluation.showResultScreen,
      isDeepDiveModalActive: evaluation.isDeepDiveModalActive,
      isGeneratingDeepDive: evaluation.isGeneratingDeepDive,
      deepDiveQuestion: evaluation.deepDiveQuestion,
      deepDiveQuestions: evaluation.deepDiveQuestions,
      currentQuestionIndex: evaluation.currentQuestionIndex,
      submitDeepDiveAnswerComposable: evaluation.submitDeepDiveAnswer,
      openEvaluationModalComposable: evaluation.openEvaluationModal,
      openDeepDiveModalComposable: evaluation.openDeepDiveModal, // ✅ NEW
      directEvaluateComposable: evaluation.directEvaluate,
      handleRetryComposable: evaluation.handleRetry,
      resetEvaluationState: evaluation.resetEvaluationState,
      isPendingEvaluation: evaluation.isPendingEvaluation,
      clearPendingEvaluation: evaluation.clearPendingEvaluation,

      // NEW: 설명 Phase
      evaluationPhase: evaluation.evaluationPhase,
      submitUserExplanationComposable: evaluation.submitUserExplanation,

      // 🔥 검증 에러 메시지
      answerValidationError: evaluation.answerValidationError
    };
  },
  computed: {
    currentProblem() {
      return this.problems[this.currentProblemIndex];
    }
  },
  async mounted() {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'dark',
      themeVariables: {
        primaryColor: '#6b5ce7',
        primaryTextColor: '#e8eaed',
        primaryBorderColor: '#6b5ce7',
        lineColor: '#4fc3f7',
        secondaryColor: '#f06292',
        tertiaryColor: '#4fc3f7',
        background: '#12122a',
        mainBkg: 'rgba(255, 255, 255, 0.05)',
        textColor: '#e8eaed'
      },
      securityLevel: 'loose'
    });

    // 라우터 쿼리에서 문제 인덱스 설정
    const problemIndex = parseInt(this.$route?.query?.problem);
    if (!isNaN(problemIndex) && problemIndex >= 0) {
      this.currentProblemIndex = problemIndex;
    }

    await this.loadProblems();
  },
  beforeUnmount() {
    this.cleanupToast();
    this.cleanupHint();
  },
  methods: {
    // === Enter Game ===
    onEnterGame() {
      this.showIntro = false;
      if (!localStorage.getItem('arch-tutorial-done')) {
        this.$nextTick(() => {
          this.showTutorial = true;
        });
      } else {
        this.showToastMessage(
          '[GUIDE] 팔레트에서 컴포넌트를 드래그하여 캔버스에 배치하세요. 꽥!',
          'guide'
        );
      }
    },

    onTutorialComplete() {
      this.showTutorial = false;
      localStorage.setItem('arch-tutorial-done', 'true');
      this.showToastMessage(
        '[GUIDE] 팔레트에서 컴포넌트를 드래그하여 캔버스에 배치하세요. 꽥!',
        'guide'
      );
    },

    // === Problem Loading ===
    async loadProblems() {
      try {
        const data = await fetchProblems();
        this.problems = transformProblems(data);
        if (this.currentProblemIndex >= this.problems.length) {
          this.currentProblemIndex = 0;
        }
      } catch (error) {
        console.error('Failed to load problems:', error);
        this.problems = [];
      }
    },

    // === Mode & Canvas Control ===
    toggleMode() {
      this.toggleModeComposable(this.showToastMessage);
    },

    clearCanvas() {
      this.clearCanvasComposable();
      this.resetEvaluationState();
    },

    // === Palette Events ===
    onPaletteDragStart() {
      // Optional: track drag start for analytics
    },

    // === Canvas Events ===
    onComponentDropped(data) {
      this.onComponentDroppedComposable(data);
    },

    onComponentMoved(data) {
      this.onComponentMovedComposable(data);
    },

    onComponentRenamed(data) {
      this.onComponentRenamedComposable(data);
    },

    onComponentDeleted(compId) {
      this.onComponentDeletedComposable(compId);
    },

    onConnectionCreated(data) {
      this.onConnectionCreatedComposable(data);
    },

    // === Hint System ===
    toggleHint() {
      this.toggleHintComposable(
        this.showToastMessage,
        this.currentProblem?.expectedComponents
      );
    },

    // NEW: 사용자 설명 제출 핸들러
    async submitUserExplanation(explanation) {
      this.showToastMessage('[PROCESSING] 아키텍처 분석 및 질문 생성 중... 꽥!', 'guide');

      const result = await this.submitUserExplanationComposable(
        explanation,
        this.currentProblem,
        this.droppedComponents,
        this.connections,
        this.mermaidCode
      );

      // 🔥 검증 실패 감지 - 모달에 메시지 표시되도록 함
      if (result.validationFailed) {
        this.showToastMessage('[검증] 더 구체적인 설명을 입력해주세요. 꽥!', 'warning');
        return; // 여기서 멈춤 - 모달에 에러메시지 표시
      }

      // ✅ 검증 통과
      if (result.finished && this.isPendingEvaluation()) {
        // 질문 없이 바로 평가로 진행
        this.clearPendingEvaluation();
        await this.directEvaluateComposable(
          this.currentProblem,
          this.droppedComponents,
          this.connections,
          this.mermaidCode
        );
      } else if (result.success) {
        this.showToastMessage('[READY] 검증 질문에 응답해주세요. 꽥!', 'guide');
      }
    },

    async submitDeepDiveAnswer(answer) {
      const result = await this.submitDeepDiveAnswerComposable(answer);

      // 🔥 검증 실패 감지
      if (result.success === false) {
        this.showToastMessage('[검증] 더 구체적인 답변을 입력해주세요. 꽥!', 'warning');
        return; // 여기서 멈춤 - 모달에 에러메시지 표시
      }

      // ✅ 검증 통과 후 진행
      if (result.finished && this.isPendingEvaluation()) {
        this.clearPendingEvaluation();
        // EvaluationModal 없이 바로 평가 진행
        await this.directEvaluateComposable(
          this.currentProblem,
          this.droppedComponents,
          this.connections,
          this.mermaidCode
        );
      }
    },

    // === Evaluation ===
    async openEvaluationModal() {
      const result = await this.openEvaluationModalComposable(
        this.currentProblem,
        this.droppedComponents,
        this.connections,
        this.mermaidCode
      );

      // ✅ Step 1: 검증 실패 처리
      if (result.validationFailed) {
        // ValidationFeedback 모달 표시
        this.validationResult = result.validationResult;
        this.showValidationFeedback = true;

        // 토스트 알림
        this.showToastMessage(
          '[검증] 아키텍처를 다시 확인해주세요. 꽥!',
          'warning'
        );

        // 디버깅용 상세 정보 출력
        console.log('[Validation Failed]', result.validationResult);
        return;
      }

      // ⚠️ Step 2: 검증 경고 처리
      if (result.validationWarnings && result.validationWarnings.length > 0) {
        this.validationResult = result.validationResult;
        this.showValidationFeedback = true;

        // 토스트로도 안내
        this.showToastMessage('[검증] 통과했습니다. 경고 사항을 확인하세요. 꽥!', 'guide');
        return;
      }

      // ✅ Step 3: 검증 통과 후 계속 진행
      if (result.shouldContinue !== false && result.validationPassed) {
        this.validationResult = result.validationResult;
        this.showValidationFeedback = true;

        this.showToastMessage('[검증] 통과했습니다! 꽥!', 'success');
      }
    },

    // ✅ ValidationFeedback에서 호출되는 메서드
    closeValidationFeedback() {
      this.showValidationFeedback = false;
      this.validationResult = null;
    },

    proceedFromValidation() {
      this.showValidationFeedback = false;

      // ✅ ValidationFeedback 닫은 후 설명 입력 모달 열기
      this.$nextTick(() => {
        this.openDeepDiveModalComposable();
        this.showToastMessage('[PHASE 1] 아키텍처 설명을 입력해주세요. 꽥!', 'guide');
      });
    },

    // === Retry ===
    handleRetry() {
      this.handleRetryComposable();
      this.clearCanvas();
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

/* === Space Mission Report 테마 변수 === */
.arch-challenge-container.among-theme {
  --space-deep: #0a0a1a;
  --space-dark: #12122a;

  --nebula-purple: #6b5ce7;
  --nebula-blue: #4fc3f7;
  --nebula-pink: #f06292;
  --star-white: #ffffff;

  --text-primary: #e8eaed;
  --text-secondary: rgba(232, 234, 237, 0.7);

  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.1);

  font-family: 'Rajdhani', sans-serif;
  background: linear-gradient(135deg, var(--space-deep) 0%, var(--space-dark) 50%, #1a1a3a 100%);
  color: var(--text-primary);
  height: 100vh;
  overflow: hidden;
  position: relative;
  user-select: none;
}

/* === 별 배경 애니메이션 === */
.stars-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.stars, .stars2, .stars3 {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: transparent;
}

.stars {
  background-image:
    radial-gradient(2px 2px at 20px 30px, var(--star-white), transparent),
    radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.8), transparent),
    radial-gradient(1px 1px at 90px 40px, var(--star-white), transparent),
    radial-gradient(2px 2px at 160px 120px, rgba(255,255,255,0.9), transparent),
    radial-gradient(1px 1px at 230px 80px, var(--star-white), transparent),
    radial-gradient(2px 2px at 300px 150px, rgba(255,255,255,0.7), transparent),
    radial-gradient(1px 1px at 350px 200px, var(--star-white), transparent),
    radial-gradient(2px 2px at 420px 50px, rgba(255,255,255,0.8), transparent),
    radial-gradient(1px 1px at 500px 180px, var(--star-white), transparent),
    radial-gradient(2px 2px at 580px 100px, rgba(255,255,255,0.9), transparent);
  background-size: 600px 300px;
  animation: twinkle 4s ease-in-out infinite;
}

.stars2 {
  background-image:
    radial-gradient(1px 1px at 100px 150px, var(--nebula-blue), transparent),
    radial-gradient(2px 2px at 200px 250px, rgba(79, 195, 247, 0.6), transparent),
    radial-gradient(1px 1px at 350px 100px, var(--nebula-blue), transparent),
    radial-gradient(2px 2px at 450px 300px, rgba(79, 195, 247, 0.7), transparent),
    radial-gradient(1px 1px at 550px 200px, var(--nebula-blue), transparent);
  background-size: 600px 400px;
  animation: twinkle 6s ease-in-out infinite 1s;
}

.stars3 {
  background-image:
    radial-gradient(1px 1px at 50px 200px, var(--nebula-purple), transparent),
    radial-gradient(2px 2px at 150px 50px, rgba(107, 92, 231, 0.6), transparent),
    radial-gradient(1px 1px at 280px 180px, var(--nebula-purple), transparent),
    radial-gradient(2px 2px at 400px 120px, rgba(107, 92, 231, 0.7), transparent),
    radial-gradient(1px 1px at 520px 280px, var(--nebula-purple), transparent);
  background-size: 600px 400px;
  animation: twinkle 5s ease-in-out infinite 2s;
}

@keyframes twinkle {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 성운 오버레이 */
.nebula-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background:
    radial-gradient(ellipse at 20% 20%, rgba(107, 92, 231, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 80%, rgba(240, 98, 146, 0.1) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(79, 195, 247, 0.08) 0%, transparent 60%);
  pointer-events: none;
  animation: nebulaPulse 10s ease-in-out infinite;
  z-index: 0;
}

@keyframes nebulaPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(107, 92, 231, 0.3); }
  50% { box-shadow: 0 0 40px rgba(107, 92, 231, 0.6); }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* === MAIN GAME === */
.game-container {
  display: flex;
  width: 100%;
  height: 100%;
  position: relative;
  z-index: 1;
  background: transparent;
}

/* === MAIN WORKSPACE === */
.main-workspace {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

/* === WORKSPACE CONTENT === */
.workspace-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  background: transparent;
}

.toolbox-panel {
  width: 150px;
  min-width: 150px;
  background: rgba(255, 255, 255, 0.05);
  border-right: 1px solid var(--glass-border);
  backdrop-filter: blur(10px);
  padding: 12px;
  overflow-y: auto;
}

/* 스크롤바 커스텀 */
.toolbox-panel::-webkit-scrollbar {
  width: 6px;
}

.toolbox-panel::-webkit-scrollbar-track {
  background: var(--space-deep);
}

.toolbox-panel::-webkit-scrollbar-thumb {
  background: rgba(107, 92, 231, 0.4);
  border-radius: 10px;
}

.toolbox-panel::-webkit-scrollbar-thumb:hover {
  background: var(--nebula-purple);
}

.canvas-panel {
  flex: 1;
  position: relative;
  background-color: rgba(10, 10, 26, 0.85);
  background-image:
    radial-gradient(rgba(107, 92, 231, 0.04) 1px, transparent 1px);
  background-size: 30px 30px;
}

.canvas-panel::after {
  content: "ARCHITECTURE WORKSPACE";
  position: absolute;
  bottom: 20px;
  right: 20px;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.7rem;
  font-weight: 700;
  color: rgba(107, 92, 231, 0.15);
  letter-spacing: 3px;
  pointer-events: none;
}
</style>
