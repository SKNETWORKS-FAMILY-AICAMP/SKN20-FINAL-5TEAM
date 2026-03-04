<template>
  <div class="arch-challenge-container neon-theme">
    <!-- 네온 그리드 배경 -->
    <div class="bg-grid"></div>

    <!-- 스캔라인 효과 -->
    <div class="scanline"></div>

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
      :is-passed="evaluationResult && evaluationResult.totalScore >= 60"
      :has-next-problem="currentProblemIndex < problems.length - 1"
      @retry="handleRetry"
      @next="handleNextProblem"
      @complete="handleComplete"
      @home="goHome"
    />

    <!-- ✅ 미션 잠금 화면 제거 (모든 미션이 항상 해금됨) -->
    <!-- <div v-else-if="!isProblemUnlocked" class="locked-screen">
      <div class="locked-content">
        <div class="lock-icon">🔒</div>
        <h2>MISSION LOCKED</h2>
        <p>이전 미션을 60점 이상으로 완료해야 해금됩니다.</p>
        <button class="unlock-btn" @click="currentProblemIndex = getFirstUncompletedProblemIndex()">
          진행 가능한 미션으로 이동
        </button>
      </div>
    </div> -->

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
            @exit-game="handleExitGame"
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

      <!-- ✅ NEW: EXIT 컨펌 모달 -->
      <PracticeExitConfirmModal
        :is-active="showExitModal"
        @confirm="confirmExit"
        @cancel="cancelExit"
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
// ✅ NEW: EXIT 컨펌 모달 (공통 컴포넌트 직접 사용)
import PracticeExitConfirmModal from '../components/PracticeExitConfirmModal.vue';

// Composables
import { useToast } from './composables/useToast';
import { useHint } from './composables/useHint';
import { useCanvasState } from './composables/useCanvasState';
import { useEvaluation } from './composables/useEvaluation';

// Services & Utils
import { transformProblems } from './utils/architectureUtils';

// [2026-02-20 수정] 맵 진행도 해금을 위해 게임 스토어 추가
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
    TutorialOverlay,
    ValidationFeedback,
    PracticeExitConfirmModal
  },
  data() {
    return {
      // Intro State
      showIntro: false,
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
      isValidationDebugMode: false, // 개발 환경에서 true로 설정

      // ✅ NEW: 진행 상태 관리
      completedProblems: [], // 완료된 문제 ID 목록
      problemScores: {}, // 문제별 점수 저장

      // ✅ NEW: EXIT 컨펌 모달 상태
      showExitModal: false
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
    },
    isProblemUnlocked() {
      // ✅ 모든 문제가 항상 해금됨 (순차 잠금 제거)
      return true;

      // 이전 코드 (순차 해금 시스템 - 비활성화):
      // if (this.currentProblemIndex === 0) return true;
      // const prevProblem = this.problems[this.currentProblemIndex - 1];
      // if (!prevProblem) return false;
      // return this.isProblemCompleted(prevProblem.problem_id);
    },
    allProblemsCompleted() {
      return this.problems.every(p => this.isProblemCompleted(p.problem_id));
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

    // ✅ 진행 상태 불러오기
    this.loadProgress();

    // 라우터 쿼리에서 문제 인덱스 설정
    const problemIndex = parseInt(this.$route?.query?.problem);
    if (!isNaN(problemIndex) && problemIndex >= 0) {
      this.currentProblemIndex = problemIndex;
    }

    await this.loadProblems();

    // ✅ 미션 순차 해금 기능 제거 (모든 미션이 항상 해금됨)
    // if (!this.isProblemUnlocked) {
    //   this.currentProblemIndex = this.getFirstUncompletedProblemIndex();
    // }

    // 인트로 건너뛰는 경우 가이드 메시지 표시
    if (!this.showIntro) {
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
    }
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
        // DB에서 문제 데이터 로드
        const response = await fetch('/api/core/practices/unit03/');
        const practiceData = await response.json();

        // [2026-02-24 수정] game.js의 mapDetailsToProblems와 동일하게 display_order 기준 정렬 및 필터
        // - 정렬 불일치 시 스테이지 맵의 questIndex와 currentProblemIndex가 어긋나 해금이 엉킴
        const sortedDetails = (practiceData.details || [])
          .filter(d => d.detail_type === 'PROBLEM' && d.is_active)
          .sort((a, b) => a.display_order - b.display_order);

        const problemsFromDB = sortedDetails.map(detail => ({
          ...detail.content_data,
          practice_detail_id: detail.id  // DB ID를 추가로 저장 (제출 시 사용)
        }));

        this.problems = transformProblems(problemsFromDB);
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
    },

    // ✅ NEW: 다음 문제로 이동
    handleNextProblem() {
      this.moveToNextProblem();
      this.handleRetryComposable(); // 평가 상태 리셋
    },

    // ✅ NEW: 모든 문제 완료
    handleComplete() {
      this.showToastMessage(
        '[MISSION COMPLETE] 모든 미션을 완료했습니다! 꽥! 🎉',
        'success'
      );
      // 필요시 메인 화면으로 이동
      // this.$router.push('/');
    },

    // ✅ NEW: EXIT 버튼 클릭 - 모달로 확인 메시지 표시
    handleExitGame() {
      this.showExitModal = true;
    },

    // ✅ NEW: EXIT 모달 - 확인 (게임 종료)
    confirmExit() {
      this.showExitModal = false;
      this.$router.push('/');
    },

    // ✅ NEW: EXIT 모달 - 취소 (계속 진행)
    cancelExit() {
      this.showExitModal = false;
    },

    // ✅ NEW: 결과 화면에서 HOME 버튼 클릭
    goHome() {
      this.$router.push('/');
    },

    // ✅ NEW: 진행 상태 관리 (Progress Store 연동)
    async loadProgress() {
      try {
        const { useProgressStore } = await import('@/stores/progress');
        const progressStore = useProgressStore();

        // 데이터가 아직 없다면 가져오기
        if (progressStore.solvedRecords.length === 0) {
            await progressStore.fetchAllProgress();
        }

        // [수정일: 2026-02-24] System Practice(Unit 3)에 해당하는 기록들만 추출
        // - 실제 DB ID 패턴은 'unit03_XX'이므로 'unit03'으로 필터링
        const systemRecords = progressStore.solvedRecords.filter(r =>
            r.practice_detail && String(r.practice_detail).startsWith('unit03')
        );

        const completed = [];
        const scores = {};

        systemRecords.forEach(record => {
            completed.push(record.practice_detail);
            if (!scores[record.practice_detail] || scores[record.practice_detail] < record.score) {
                scores[record.practice_detail] = record.score;
            }
        });

        this.completedProblems = completed;
        this.problemScores = scores;

      } catch (error) {
        console.error('Failed to load progress via Pinia:', error);
        this.completedProblems = [];
        this.problemScores = {};
      }
    },
    async saveProgress() {
      // 로컬 스토리지가 아닌, DB 측 데이터가 알아서 보관되므로 프론트엔드 캐싱용 동작은 fetchAllProgress로 커버됨
      // (혹시 모를 에러 방지를 위해 빈 함수 유지)
    },

    isProblemCompleted(problemId) {
      // System 실습은 practice_detail id 가 problemId 로 넘어온다고 가정하거나 
      // 현재 문제의 db_id/practice_detail_id 와 매칭해야 함
      return this.completedProblems.includes(problemId);
    },

    getFirstUncompletedProblemIndex() {
      for (let i = 0; i < this.problems.length; i++) {
        if (!this.isProblemCompleted(this.problems[i].practice_detail_id || this.problems[i].problem_id)) {
          return i;
        }
      }
      return 0; // 모두 완료되었으면 첫 번째로
    },

    async completeProblem(problemId, score) {
      // 완료 목록에 리액티브 추가
      if (!this.completedProblems.includes(problemId)) {
        this.completedProblems.push(problemId);
      }

      if (!this.problemScores[problemId] || this.problemScores[problemId] < score) {
        this.problemScores[problemId] = score;
      }
      
      const { useProgressStore } = await import('@/stores/progress');
      const progressStore = useProgressStore();
      
      try {
          // 백엔드로 최종 점수 전송 (`practice_detail_id` 필수)
          // `problemId`가 디비 상의 `practice_detail_id` (예. system03_1) 형태라고 가정
          await progressStore.submitScore(problemId, score, {
              title: this.currentProblem?.title,
              mode: 'system_architecture'
          });
      } catch (e) {
          console.error('[Score Submission Failed]', e);
      }
    },

    moveToNextProblem() {
      if (this.currentProblemIndex < this.problems.length - 1) {
        this.currentProblemIndex++;
        this.clearCanvas();
        this.showToastMessage(
          `[NEXT MISSION] ${this.currentProblem.title} 시작! 꽥!`,
          'guide'
        );
      } else {
        this.showToastMessage(
          '[MISSION COMPLETE] 모든 미션을 완료했습니다! 꽥! 🎉',
          'success'
        );
      }
    },

    async checkEvaluationComplete() {
      // 평가 결과가 있고, 결과 화면이 보이고 있을 때
      if (this.showResultScreen && this.evaluationResult) {
        const score = this.evaluationResult.totalScore || this.evaluationResult.score || 0;
        const problemId = this.currentProblem?.problem_id;

        console.log('[SystemArch] checkEvaluationComplete:', {
          score,
          problemId,
          practice_detail_id: this.currentProblem?.practice_detail_id,
          currentProblemIndex: this.currentProblemIndex
        });

        // ✅ 60점 이상이면 통과
        if (score >= 60) {
          // DB 식별용 ID가 우선순위
          const targetDetailId = this.currentProblem?.practice_detail_id || problemId;
          // [수정일: 2026-02-24] await 전에 currentProblemIndex를 캡처하여 비동기 완료 후 인덱스 변동 방지
          const capturedIndex = this.currentProblemIndex;

          await this.completeProblem(targetDetailId, score);

          // [수정일: 2026-02-27] progressStore.unlockNextStage()로 직접 해금 (DB 단일 소스)
          const { useProgressStore } = await import('@/stores/progress');
          const progressStore = useProgressStore();
          const gameStore = useGameStore();

          const practiceId = gameStore.activeUnit?.id;
          await progressStore.unlockNextStage(practiceId, capturedIndex + 1);

          console.log('[SystemArch] unlockNextStage done for questIndex:', capturedIndex + 1);

          // 다음 문제가 있으면 자동으로 이동 안내
          if (capturedIndex < this.problems.length - 1) {
            this.showToastMessage(
              `[PASS] 통과! 다음 단계가 해금되었습니다. 꽥! (${score}점)`,
              'success'
            );
          } else {
            this.showToastMessage(
              `[ALL CLEAR] 모든 미션 완료! 최종 점수: ${score}점 꽥! 🎉`,
              'success'
            );
          }
        } else {
          this.showToastMessage(
            `[평가 완료] 점수: ${score}점 꽥!`,
            'info'
          );
        }
      }
    }
  },
  watch: {
    // ✅ 평가 결과 변경 감지
    evaluationResult(newValue) {
      if (newValue) {
        this.$nextTick(() => {
          this.checkEvaluationComplete();
        });
      }
    }
  }
};
</script>

<style scoped>
/* 폰트 임포트 */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');

/* === NEON ARCADE THEME === */
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
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image:
    linear-gradient(rgba(0, 0, 0, 0.2) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 0, 0, 0.2) 1px, transparent 1px);
  background-size: 40px 40px;
  z-index: 0;
  pointer-events: none;
}

.scanline {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,0) 50%, rgba(0,0,0,0.1) 50%, rgba(0,0,0,0.1));
  background-size: 100% 4px;
  z-index: 1;
  pointer-events: none;
}

/* === 2. 레이아웃 구조 === */
.game-container {
  position: relative;
  z-index: 10;
  width: 98%;
  height: 96%;
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

/* === 3. 컴포넌트 스타일링 === */

/* [좌측 패널] CaseFilePanel 스타일 오버라이드 */
:deep(.case-file-panel) {
  width: 420px;
  min-width: 420px;
  background: var(--bg-panel) !important;
  border: 1px solid var(--neon-purple) !important;
  border-radius: 16px !important;
  box-shadow: inset 0 0 30px rgba(188, 19, 254, 0.1), 0 0 15px rgba(188, 19, 254, 0.2) !important;
  backdrop-filter: blur(10px);
}

:deep(.case-file-panel h2),
:deep(.case-file-panel h3) {
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
  display: flex;
  align-items: center;
}

/* 버튼 스타일 (헤더 및 내부 버튼) */
:deep(button) {
  font-family: var(--font-header) !important;
  border-radius: 20px !important;
  text-transform: uppercase;
  transition: all 0.2s ease;
}

:deep(.btn-primary),
:deep(.action-btn) {
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
.toolbox-panel {
  width: 140px;
  min-width: 140px;
  background: rgba(10, 15, 30, 0.6) !important;
  border: 1px solid rgba(80, 80, 255, 0.3) !important;
  border-radius: 12px !important;
  padding: 12px;
  overflow-y: auto;
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
.canvas-panel {
  flex: 1;
  position: relative;
  background-color: #050508 !important;
  border: 1px solid #333 !important;
  border-radius: 12px !important;
  box-shadow: inset 0 0 50px rgba(0,0,0,0.8);
}

/* 캔버스 내부 그리드 패턴 */
.canvas-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image:
    linear-gradient(rgba(100, 100, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(100, 100, 255, 0.05) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
  z-index: 0;
}

.canvas-panel::after {
  content: "ARCHITECTURE WORKSPACE";
  position: absolute;
  bottom: 20px;
  right: 20px;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.7rem;
  font-weight: 700;
  color: rgba(0, 243, 255, 0.15);
  letter-spacing: 3px;
  pointer-events: none;
}

/* ✅ 미션 잠금 화면 스타일 제거 (모든 미션 자유 접근) */
/* .locked-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--bg-deep);
  z-index: 100;
}

.locked-content {
  text-align: center;
  padding: 60px;
  background: var(--bg-panel);
  border: 2px solid var(--neon-purple);
  border-radius: 20px;
  box-shadow: 0 0 50px rgba(188, 19, 254, 0.3);
  backdrop-filter: blur(10px);
}

.lock-icon {
  font-size: 5rem;
  margin-bottom: 20px;
  animation: shake 2s infinite;
}

@keyframes shake {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-10deg); }
  75% { transform: rotate(10deg); }
}

.locked-content h2 {
  font-family: var(--font-header);
  font-size: 2.5rem;
  color: var(--neon-cyan);
  margin-bottom: 15px;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.locked-content p {
  font-size: 1.2rem;
  color: #ccc;
  margin-bottom: 30px;
  line-height: 1.6;
}

.unlock-btn {
  padding: 15px 40px;
  background: linear-gradient(135deg, var(--neon-purple), var(--neon-cyan));
  color: white;
  border: none;
  border-radius: 30px;
  font-family: var(--font-header);
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.3s ease;
}

.unlock-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(188, 19, 254, 0.5);
} */

/* === 5. 스크롤바 커스텀 === */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #000;
}

::-webkit-scrollbar-thumb {
  background: var(--neon-purple);
  border-radius: 3px;
}
</style>
