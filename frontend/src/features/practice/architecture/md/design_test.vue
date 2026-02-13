<template>
  <div class="arch-challenge-container neon-theme">
    
    <div class="bg-grid"></div>
    <div class="scanline"></div>
    
    <IntroScene
      v-if="showIntro"
      :intro-lines="introLines"
      @enter-game="onEnterGame"
    />

    <EvaluationResultScreen
      v-else-if="showResultScreen"
      :result="evaluationResult"
      :problem="currentProblem"
      :is-loading="isEvaluating"
      :total-problems="problems.length"
      :current-problem-index="currentProblemIndex"
      @retry="handleRetry"
      @next="handleNext"
    />

    <template v-else>
      <div class="game-container">
        
        <CaseFilePanel
          class="case-file-panel neon-panel"
          :problem="currentProblem"
          :is-connection-mode="isConnectionMode"
          :can-evaluate="droppedComponents.length > 0"
          :is-evaluating="isEvaluating"
          :mermaid-code="mermaidCode"
          @start-evaluation="openEvaluationModal"
        />

        <div class="main-workspace">
          
          <GameHeader
            class="game-header neon-panel-flat"
            :is-connection-mode="isConnectionMode"
            :is-hint-active="isHintActive"
            @toggle-mode="toggleMode"
            @clear-canvas="clearCanvas"
            @toggle-hint="toggleHint"
          />

          <div class="workspace-content">
            <ComponentPalette
              class="toolbox-panel neon-panel"
              :required-types="currentProblem?.expectedComponents || []"
              :is-hint-active="isHintActive"
              @drag-start="onPaletteDragStart"
            />

            <ArchitectureCanvas
              class="canvas-panel neon-panel"
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
            />
            
          </div>
        </div>
      </div>

      <TutorialOverlay v-if="showTutorial" @complete="onTutorialComplete" @skip="onTutorialComplete" />
      <DetectiveToast :show="showToast" :message="toastMessage" :type="toastType" @dismiss="dismissToast" />
      
      <DeepDiveModal
        :is-active="isDeepDiveModalActive"
        :question="deepDiveQuestion"
        :is-generating="isGeneratingDeepDive"
        :is-judging="isJudgingAnswer"
        :current-question="currentQuestionIndex + 1"
        :total-questions="deepDiveQuestions.length"
        :category="deepDiveQuestions[currentQuestionIndex]?.category || ''"
        :mermaid-code="mermaidCode"
        :phase="evaluationPhase"
        @submit="submitDeepDiveAnswer"
        @submit-explanation="submitUserExplanation"
      />
    </template>
  </div>
</template>

<script>
// 기존 스크립트 로직을 그대로 유지합니다.
// (import문, data, setup, methods 등 원본 파일의 내용을 그대로 두세요)
import mermaid from 'mermaid';
import ComponentPalette from './components/ComponentPalette.vue';
import ArchitectureCanvas from './components/ArchitectureCanvas.vue';
import DeepDiveModal from './components/DeepDiveModal.vue';
import EvaluationResultScreen from './components/EvaluationResultScreen.vue';
import DetectiveToast from './components/DetectiveToast.vue';
import GameHeader from './components/GameHeader.vue';
import IntroScene from './components/IntroScene.vue';
import CaseFilePanel from './components/CaseFilePanel.vue';
import TutorialOverlay from './components/TutorialOverlay.vue';
import { useToast } from './composables/useToast';
import { useHint } from './composables/useHint';
import { useCanvasState } from './composables/useCanvasState';
import { useEvaluation } from './composables/useEvaluation';
import { fetchProblems } from './services/architectureQuestionApi';
import { transformProblems } from './utils/architectureUtils';
import { useGameStore } from '@/stores/game';

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
    TutorialOverlay
  },
  data() {
    return {
      showIntro: true,
      showTutorial: false,
      introLines: [
        "[SYSTEM ALERT] 아키텍트님, 마더 서버에 이상 징후가 감지되었습니다. 꽥!",
        "오염된 AI들이 환각(Hallucination)에 빠져 시스템을 붕괴시키고 있습니다.",
        "당신만이 이 상황을 복구할 수 있습니다.",
        "올바른 시스템 아키텍처를 설계하여 데이터 무결성을 확보하세요!",
        "[PROTOCOL READY] 복구 터미널에 접속합니다..."
      ],
      currentProblemIndex: 0,
      problems: []
    };
  },
  setup() {
    const toast = useToast();
    const hint = useHint();
    const canvas = useCanvasState();
    const evaluation = useEvaluation();

    return {
      showToast: toast.showToast,
      toastMessage: toast.toastMessage,
      toastType: toast.toastType,
      showToastMessage: toast.showToastMessage,
      dismissToast: toast.dismissToast,
      cleanupToast: toast.cleanup,
      isHintActive: hint.isHintActive,
      toggleHintComposable: hint.toggleHint,
      cleanupHint: hint.cleanup,
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
      isEvaluating: evaluation.isEvaluating,
      evaluationResult: evaluation.evaluationResult,
      showResultScreen: evaluation.showResultScreen,
      isDeepDiveModalActive: evaluation.isDeepDiveModalActive,
      isGeneratingDeepDive: evaluation.isGeneratingDeepDive,
      isJudgingAnswer: evaluation.isJudgingAnswer,
      deepDiveQuestion: evaluation.deepDiveQuestion,
      deepDiveQuestions: evaluation.deepDiveQuestions,
      currentQuestionIndex: evaluation.currentQuestionIndex,
      submitDeepDiveAnswerComposable: evaluation.submitDeepDiveAnswer,
      openEvaluationModalComposable: evaluation.openEvaluationModal,
      directEvaluateComposable: evaluation.directEvaluate,
      handleRetryComposable: evaluation.handleRetry,
      resetEvaluationState: evaluation.resetEvaluationState,
      isPendingEvaluation: evaluation.isPendingEvaluation,
      clearPendingEvaluation: evaluation.clearPendingEvaluation,
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
        primaryColor: '#00f3ff',     // Neon Cyan
        primaryTextColor: '#ffffff',
        primaryBorderColor: '#00f3ff',
        lineColor: '#bc13fe',        // Neon Purple
        secondaryColor: '#ff0055',   // Neon Pink
        tertiaryColor: '#050510',
        background: '#050510',
        mainBkg: 'rgba(20, 20, 35, 0.8)',
        textColor: '#e0f7fa'
      },
      securityLevel: 'loose'
    });

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
    onEnterGame() {
      this.showIntro = false;
      if (!localStorage.getItem('arch-tutorial-done')) {
        this.$nextTick(() => { this.showTutorial = true; });
      } else {
        this.showToastMessage('[GUIDE] 준비 완료! 설계를 시작하세요.', 'guide');
      }
    },
    onTutorialComplete() {
      this.showTutorial = false;
      localStorage.setItem('arch-tutorial-done', 'true');
      this.showToastMessage('[GUIDE] 준비 완료! 설계를 시작하세요.', 'guide');
    },
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
    toggleMode() { this.toggleModeComposable(this.showToastMessage); },
    clearCanvas() { this.clearCanvasComposable(); this.resetEvaluationState(); },
    onPaletteDragStart() {},
    onComponentDropped(data) { this.onComponentDroppedComposable(data); },
    onComponentMoved(data) { this.onComponentMovedComposable(data); },
    onComponentRenamed(data) { this.onComponentRenamedComposable(data); },
    onComponentDeleted(compId) { this.onComponentDeletedComposable(compId); },
    onConnectionCreated(data) { this.onConnectionCreatedComposable(data); },
    toggleHint() { this.toggleHintComposable(this.showToastMessage, this.currentProblem?.expectedComponents); },
    async submitUserExplanation(explanation) {
      this.showToastMessage('[PROCESSING] 시스템 분석 중...', 'guide');
      const allDone = await this.submitUserExplanationComposable(explanation, this.currentProblem, this.droppedComponents, this.connections, this.mermaidCode);
      if (allDone && this.isPendingEvaluation()) {
        this.clearPendingEvaluation();
        await this.directEvaluateComposable(this.currentProblem, this.droppedComponents, this.connections, this.mermaidCode);
      } else {
        this.showToastMessage('[ALERT] 추가 검증이 필요합니다.', 'guide');
      }
    },
    async submitDeepDiveAnswer(answer) {
      const allDone = await this.submitDeepDiveAnswerComposable(answer);
      if (allDone && this.isPendingEvaluation()) {
        this.clearPendingEvaluation();
        await this.directEvaluateComposable(this.currentProblem, this.droppedComponents, this.connections, this.mermaidCode);
      }
    },
    async openEvaluationModal() {
      await this.openEvaluationModalComposable(this.currentProblem, this.droppedComponents, this.connections, this.mermaidCode);
    },
    handleRetry() { this.handleRetryComposable(); this.clearCanvas(); },
    handleNext() {
      const gameStore = useGameStore();
      gameStore.unlockNextStage('System Practice', this.currentProblemIndex + 1);
      if (this.currentProblemIndex < this.problems.length - 1) {
        this.currentProblemIndex++;
        this.handleRetryComposable();
        this.clearCanvas();
        this.showToastMessage(`[CASE ${this.currentProblemIndex + 1}] 다음 미션을 로드합니다.`, 'guide');
      }
    }
  }
};
</script>

<style scoped>
/* 폰트 임포트 */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');

/* === NEON ARCADE THEME (Global Vars for this component) === */
.arch-challenge-container.neon-theme {
  --bg-deep: #090910;
  --bg-panel: rgba(18, 18, 35, 0.7);
  --neon-cyan: #00f3ff;
  --neon-purple: #bc13fe;
  --neon-pink: #ff00ff;
  --neon-lime: #ccf381;
  --glass-border: 1px solid rgba(255, 255, 255, 0.1);
  --font-header: 'Orbitron', sans-serif;
  --font-body: 'Rajdhani', sans-serif;

  /* 컨테이너 스타일 */
  width: 100%;
  height: 100vh;
  background-color: var(--bg-deep);
  background-image: 
    radial-gradient(circle at 10% 20%, rgba(188, 19, 254, 0.15) 0%, transparent 40%),
    radial-gradient(circle at 90% 80%, rgba(0, 243, 255, 0.1) 0%, transparent 40%);
  color: #fff;
  font-family: var(--font-body);
  position: relative;
  overflow: hidden;
}

/* === 1. 배경 효과 (Grid + Scanline) === */
.bg-grid {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background-image: 
    linear-gradient(rgba(0, 0, 0, 0.2) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 0, 0, 0.2) 1px, transparent 1px);
  background-size: 40px 40px;
  z-index: 0;
  pointer-events: none;
}

.scanline {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,0) 50%, rgba(0,0,0,0.1) 50%, rgba(0,0,0,0.1));
  background-size: 100% 4px;
  z-index: 1;
  pointer-events: none;
}

/* === 2. 레이아웃 구조 === */
.game-container {
  position: relative; z-index: 10;
  width: 98%; height: 96%;
  display: flex;
  margin: 0 auto;
  top: 2%;
  gap: 15px;
}

.main-workspace {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
  overflow: hidden;
}

.workspace-content {
  flex: 1;
  display: flex;
  gap: 15px;
  overflow: hidden;
}

/* === 3. 컴포넌트 스타일링 (Deep Selector 활용) === */

/* [좌측 패널] CaseFilePanel 스타일 오버라이드 */
:deep(.case-file-panel) {
  width: 320px;
  min-width: 320px;
  background: var(--bg-panel) !important;
  border: 1px solid var(--neon-purple) !important;
  border-radius: 16px !important;
  box-shadow: inset 0 0 30px rgba(188, 19, 254, 0.1), 0 0 15px rgba(188, 19, 254, 0.2) !important;
  backdrop-filter: blur(10px);
}

:deep(.case-file-panel h2), :deep(.case-file-panel h3) {
  font-family: var(--font-header) !important;
  color: var(--neon-cyan) !important;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* [상단 헤더] GameHeader 스타일 오버라이드 */
:deep(.game-header) {
  height: 60px;
  background: transparent !important;
  border-bottom: 1px solid var(--neon-cyan) !important;
  display: flex; align-items: center;
}

/* 버튼 스타일 (헤더 및 내부 버튼) */
:deep(button) {
  font-family: var(--font-header) !important;
  border-radius: 20px !important;
  text-transform: uppercase;
  transition: all 0.2s ease;
}

:deep(.btn-primary), :deep(.action-btn) {
  background: rgba(0, 0, 0, 0.3) !important;
  border: 1px solid var(--neon-cyan) !important;
  color: var(--neon-cyan) !important;
  box-shadow: 0 0 10px rgba(0, 243, 255, 0.2);
}

:deep(.btn-primary:hover) {
  background: var(--neon-cyan) !important;
  color: #000 !important;
  box-shadow: 0 0 20px rgba(0, 243, 255, 0.6);
}

/* [중앙] 툴박스 ComponentPalette */
:deep(.toolbox-panel) {
  width: 140px;
  min-width: 140px;
  background: rgba(10, 15, 30, 0.6) !important;
  border: 1px solid rgba(80, 80, 255, 0.3) !important;
  border-radius: 12px !important;
}

:deep(.component-item) {
  background: rgba(255, 255, 255, 0.03) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 8px !important;
  color: #ccc !important;
  transition: all 0.2s;
}

:deep(.component-item:hover) {
  border-color: var(--neon-cyan) !important;
  background: rgba(0, 243, 255, 0.1) !important;
  box-shadow: 0 0 15px rgba(0, 243, 255, 0.3);
  transform: translateX(5px);
}

/* [우측] 캔버스 ArchitectureCanvas */
:deep(.canvas-panel) {
  background-color: #050508 !important;
  border: 1px solid #333 !important;
  border-radius: 12px !important;
  box-shadow: inset 0 0 50px rgba(0,0,0,0.8);
  position: relative;
}

/* 캔버스 내부 그리드 패턴 */
:deep(.canvas-panel)::before {
  content: '';
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background-image: 
    linear-gradient(rgba(100, 100, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(100, 100, 255, 0.05) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
  z-index: 0;
}


/* === 5. 스크롤바 커스텀 === */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #000; }
::-webkit-scrollbar-thumb { background: var(--neon-purple); border-radius: 3px; }
</style>