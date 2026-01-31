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

      <!-- Deep Dive 모달 (3개 질문 순차 처리) - 평가는 여기서만 진행 -->
      <DeepDiveModal
        :is-active="isDeepDiveModalActive"
        :question="deepDiveQuestion"
        :is-generating="isGeneratingDeepDive"
        :current-question="currentQuestionIndex + 1"
        :total-questions="deepDiveQuestions.length"
        :category="deepDiveQuestions[currentQuestionIndex]?.category || ''"
        :mermaid-code="mermaidCode"
        @skip="skipDeepDive"
        @submit="submitDeepDiveAnswer"
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
        "거기 서! 도망갈 생각 마라. 꽥!",
        "네가 오늘 발생한 대규모 서버 폭파 사건의 가장 유력한 용의자로 지목되었다.",
        "억울하다고? 그렇다면 취조실로 들어와서 직접 증명해 봐.",
        "올바른 시스템 아키텍처를 설계해서 네 결백을 입증하는 거다!",
        "(철창 문이 열린다...)"
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
      clearPendingEvaluation: evaluation.clearPendingEvaluation
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
        '자, 여기에 앉아. 오른쪽 팔레트에서 컴포넌트를 드래그해서 캔버스에 배치해. 꽥!',
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
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Courier+Prime:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap');

/* === 취조실 테마 변수 === */
.arch-challenge-container.panic-room-theme {
  --bg-dark: #0f1115;
  --bg-metal: #2c3e50;
  --panel-grey: #1a1a1a;
  --accent-yellow: #f1c40f;
  --danger-red: #e74c3c;
  --neon-blue: #00f3ff;
  --text-white: #ecf0f1;
  --border-black: #000;
  --pixel-font: 'Press Start 2P', cursive;
  --typewriter-font: 'Courier Prime', monospace;

  font-family: var(--pixel-font);
  background-color: var(--bg-dark);
  color: var(--text-white);
  height: 100vh;
  overflow: hidden;
  position: relative;
  user-select: none;
  /* CRT 스캔라인 효과 */
  background-image:
    linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%),
    linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
  background-size: 100% 2px, 6px 100%;
}

/* === 글로벌 FX 레이어 === */
.vignette {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, transparent 50%, rgba(0, 0, 0, 0.9) 100%);
  pointer-events: none;
  z-index: 900;
}

.noise {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0.03;
  background-image: repeating-radial-gradient(#000 0 0.0001%, #fff 0 0.0002%);
  pointer-events: none;
  z-index: 899;
}

/* === 나사 장식 === */
.screw {
  position: fixed;
  width: 15px;
  height: 15px;
  background: #555;
  border-radius: 50%;
  border: 2px solid #222;
  box-shadow: inset 2px 2px 5px rgba(255, 255, 255, 0.2), 2px 2px 5px rgba(0, 0, 0, 0.5);
  z-index: 950;
  pointer-events: none;
}

.screw::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 10%;
  width: 80%;
  height: 2px;
  background: #111;
  transform: translateY(-50%) rotate(45deg);
}

.screw.tl { top: 10px; left: 10px; }
.screw.tr { top: 10px; right: 10px; }
.screw.bl { bottom: 10px; left: 10px; }
.screw.br { bottom: 10px; right: 10px; }

/* === MAIN GAME === */
.game-container {
  display: flex;
  width: 100%;
  height: 100%;
  position: relative;
  z-index: 1;
  /* 금속 패널 텍스처 */
  background: #1e272e;
  background-image:
    linear-gradient(90deg, transparent 50%, rgba(0, 0, 0, 0.2) 50%),
    linear-gradient(0deg, transparent 50%, rgba(0, 0, 0, 0.2) 50%);
  background-size: 50px 50px;
  box-shadow: inset 0 0 100px rgba(0, 0, 0, 0.8);
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
  background: #222;
}

.toolbox-panel {
  width: 130px;
  min-width: 130px;
  background: var(--bg-metal);
  border-right: 4px solid #000;
  padding: 15px;
  overflow-y: auto;
  /* 금속 스트라이프 패턴 */
  background-image: linear-gradient(0deg, #34495e 50%, #2c3e50 50%);
  background-size: 100% 20px;
  box-shadow: inset -5px 0 15px rgba(0, 0, 0, 0.5);
}

.canvas-panel {
  flex: 1;
  position: relative;
  /* 블루프린트 그리드 패턴 */
  background-color: #2f3542;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
  background-size: 40px 40px;
  box-shadow: inset 0 0 50px rgba(0, 0, 0, 0.8);
}

.canvas-panel::after {
  content: "SYSTEM ARCHITECTURE (DRAFT)";
  position: absolute;
  bottom: 20px;
  right: 20px;
  font-family: var(--typewriter-font);
  font-size: 2rem;
  color: rgba(255, 255, 255, 0.05);
  transform: rotate(-5deg);
  pointer-events: none;
}
</style>
