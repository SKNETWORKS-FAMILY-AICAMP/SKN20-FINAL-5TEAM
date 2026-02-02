<template>
  <div class="arch-challenge-container panic-room-theme">
    <!-- 글로벌 FX 레이어 -->
    <div class="vignette"></div>
    <div class="noise"></div>

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
      <!-- 나사 장식 -->
      <div class="screw tl"></div>
      <div class="screw tr"></div>
      <div class="screw bl"></div>
      <div class="screw br"></div>

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
        @skip="skipDeepDive"
        @submit="submitDeepDiveAnswer"
        @submit-explanation="submitUserExplanation"
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
    CaseFilePanel
  },
  data() {
    return {
      // Intro State
      showIntro: true,
      introLines: [
        "[SYSTEM ALERT] 아키텍트님, 마더 서버에 이상 징후가 감지되었습니다. 꽥!",
        "오염된 AI들이 환각(Hallucination)에 빠져 시스템을 붕괴시키고 있습니다.",
        "당신만이 이 상황을 복구할 수 있습니다.",
        "올바른 시스템 아키텍처를 설계하여 데이터 무결성을 확보하세요!",
        "[PROTOCOL READY] 복구 터미널에 접속합니다..."
      ],

      // Problem State
      currentProblemIndex: 0,
      problems: []
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
      skipDeepDiveComposable: evaluation.skipDeepDive,
      submitDeepDiveAnswerComposable: evaluation.submitDeepDiveAnswer,
      openEvaluationModalComposable: evaluation.openEvaluationModal,
      directEvaluateComposable: evaluation.directEvaluate,
      handleRetryComposable: evaluation.handleRetry,
      resetEvaluationState: evaluation.resetEvaluationState,
      isPendingEvaluation: evaluation.isPendingEvaluation,
      clearPendingEvaluation: evaluation.clearPendingEvaluation,

      // NEW: 설명 Phase
      evaluationPhase: evaluation.evaluationPhase,
      submitUserExplanationComposable: evaluation.submitUserExplanation
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
        primaryColor: '#f1c40f',
        primaryTextColor: '#1a1a1a',
        primaryBorderColor: '#f1c40f',
        lineColor: '#f1c40f',
        secondaryColor: '#e74c3c',
        tertiaryColor: '#3498db'
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

    // === Deep Dive ===
    async skipDeepDive() {
      // 설명 Phase에서 skip하면 기본 질문으로 진행
      if (this.evaluationPhase === 'explanation') {
        await this.submitUserExplanation('(설명 생략)');
        return;
      }

      const allDone = await this.skipDeepDiveComposable();
      if (allDone && this.isPendingEvaluation()) {
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

    // NEW: 사용자 설명 제출 핸들러
    async submitUserExplanation(explanation) {
      this.showToastMessage('[PROCESSING] 아키텍처 분석 및 질문 생성 중... 꽥!', 'guide');

      const allDone = await this.submitUserExplanationComposable(
        explanation,
        this.currentProblem,
        this.droppedComponents,
        this.connections,
        this.mermaidCode
      );

      if (allDone && this.isPendingEvaluation()) {
        // 질문 없이 바로 평가로 진행
        this.clearPendingEvaluation();
        await this.directEvaluateComposable(
          this.currentProblem,
          this.droppedComponents,
          this.connections,
          this.mermaidCode
        );
      } else {
        this.showToastMessage('[READY] 검증 질문에 응답해주세요. 꽥!', 'guide');
      }
    },

    async submitDeepDiveAnswer(answer) {
      const allDone = await this.submitDeepDiveAnswerComposable(answer);
      if (allDone && this.isPendingEvaluation()) {
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
      await this.openEvaluationModalComposable(
        this.currentProblem,
        this.droppedComponents,
        this.connections,
        this.mermaidCode
      );
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
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&display=swap');

/* === Architect Terminal 2077 테마 변수 === */
.arch-challenge-container.panic-room-theme {
  --bg-dark: #05070A;
  --bg-panel: rgba(163, 255, 71, 0.05);
  --panel-border: rgba(163, 255, 71, 0.2);
  --accent-green: #A3FF47;
  --accent-cyan: #00f3ff;
  --accent-pink: #ec4899;
  --text-white: #ecf0f1;
  --text-muted: rgba(163, 255, 71, 0.6);
  --terminal-font: 'Fira Code', monospace;

  font-family: var(--terminal-font);
  background-color: var(--bg-dark);
  color: var(--accent-green);
  height: 100vh;
  overflow: hidden;
  position: relative;
  user-select: none;
}

/* === 글로벌 FX 레이어 === */
.vignette {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, transparent 40%, rgba(0, 0, 0, 0.7) 100%);
  pointer-events: none;
  z-index: 900;
}

.noise {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0.02;
  background-image: repeating-radial-gradient(#A3FF47 0 0.0001%, transparent 0 0.0002%);
  pointer-events: none;
  z-index: 899;
}

/* === 나사 장식 (숨김) === */
.screw {
  display: none;
}

/* === MAIN GAME === */
.game-container {
  display: flex;
  width: 100%;
  height: 100%;
  position: relative;
  z-index: 1;
  background: var(--bg-dark);
  /* 도트 그리드 패턴 */
  background-image: radial-gradient(rgba(163, 255, 71, 0.08) 1px, transparent 1px);
  background-size: 40px 40px;
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
  width: 140px;
  min-width: 140px;
  background: var(--bg-panel);
  border-right: 1px solid var(--panel-border);
  padding: 12px;
  overflow-y: auto;
  backdrop-filter: blur(10px);
}

/* 스크롤바 커스텀 */
.toolbox-panel::-webkit-scrollbar {
  width: 4px;
}

.toolbox-panel::-webkit-scrollbar-track {
  background: transparent;
}

.toolbox-panel::-webkit-scrollbar-thumb {
  background: rgba(163, 255, 71, 0.2);
  border-radius: 10px;
}

.toolbox-panel::-webkit-scrollbar-thumb:hover {
  background: rgba(163, 255, 71, 0.4);
}

.canvas-panel {
  flex: 1;
  position: relative;
  background-color: rgba(5, 7, 10, 0.8);
  background-image:
    linear-gradient(rgba(163, 255, 71, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(163, 255, 71, 0.03) 1px, transparent 1px);
  background-size: 40px 40px;
}

.canvas-panel::after {
  content: "SYSTEM_ARCHITECTURE.draft";
  position: absolute;
  bottom: 20px;
  right: 20px;
  font-family: var(--terminal-font);
  font-size: 1rem;
  color: rgba(163, 255, 71, 0.1);
  letter-spacing: 2px;
  pointer-events: none;
}
</style>
