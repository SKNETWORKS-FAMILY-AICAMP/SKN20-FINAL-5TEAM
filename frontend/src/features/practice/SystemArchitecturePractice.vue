<template>
  <div class="arch-challenge-container">
    <!-- 평가 결과 화면 -->
    <EvaluationResultScreen
      v-if="showResultScreen"
      :result="evaluationResult"
      :problem="currentProblem"
      :is-loading="isEvaluating"
      @retry="handleRetry"
    />

    <!-- 메인 게임 화면 -->
    <template v-else>
      <div class="bg-animation"></div>

      <div class="game-container">
        
        <!-- 결과 패널 -->
        <div class="result-panel">
          <!-- 문제 카드 -->
          <ProblemCard
          :problem="currentProblem"
          :is-connection-mode="isConnectionMode"
          :can-evaluate="droppedComponents.length > 0"
          :is-evaluating="isEvaluating"
          @start-evaluation="openEvaluationModal"
          />
          
          <!-- 채팅 패널 -->
          <!-- <ChatPanel
          :messages="chatMessages"
          :is-loading="isChatLoading"
          @send-message="handleChatMessage"
          /> -->
        </div>

        <!-- 아키텍처 캔버스 -->
        <ArchitectureCanvas
          :components="droppedComponents"
          :connections="connections"
          :is-connection-mode="isConnectionMode"
          @toggle-mode="toggleMode"
          @clear-canvas="clearCanvas"
          @component-dropped="onComponentDropped"
          @component-moved="onComponentMoved"
          @component-renamed="onComponentRenamed"
          @component-deleted="onComponentDeleted"
          @connection-created="onConnectionCreated"
          />
          
          <!-- 컴포넌트 팔레트 -->
          <ComponentPalette @drag-start="onPaletteDragStart" />
        </div>
  
      <!-- 평가 모달 -->
      <EvaluationModal
        :is-active="isModalActive"
        :question="generatedQuestion"
        :is-generating="isGeneratingQuestion"
        :components="droppedComponents"
        :connections="connections"
        @close="closeModal"
        @submit="submitEvaluationAnswer"
      />

      <!-- Deep Dive 모달 (3개 질문 순차 처리) -->
      <DeepDiveModal
        :is-active="isDeepDiveModalActive"
        :question="deepDiveQuestion"
        :is-generating="isGeneratingDeepDive"
        :current-question="currentQuestionIndex + 1"
        :total-questions="deepDiveQuestions.length"
        :category="deepDiveQuestions[currentQuestionIndex]?.category || ''"
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
import ProblemCard from './components/ProblemCard.vue';
import ChatPanel from './components/ChatPanel.vue';
import EvaluationModal from './components/EvaluationModal.vue';
import DeepDiveModal from './components/DeepDiveModal.vue';
import EvaluationResultScreen from './components/EvaluationResultScreen.vue';

// Services & Utils
import {
  fetchProblems,
  generateDeepDiveQuestion,
  generateEvaluationQuestion,
  evaluateArchitecture,
  sendChatMessage,
  generateArchitectureAnalysisQuestions
} from './services/architectureApi';

import {
  transformProblems,
  detectMessageType,
  buildChatContext,
  buildArchitectureContext,
  generateMermaidCode,
  mockEvaluations
} from './utils/architectureUtils';

export default {
  name: 'SystemArchitectureChallenge',
  components: {
    ComponentPalette,
    ArchitectureCanvas,
    ProblemCard,
    ChatPanel,
    EvaluationModal,
    DeepDiveModal,
    EvaluationResultScreen
  },
  data() {
    return {
      // Canvas State
      isConnectionMode: false,
      droppedComponents: [],
      connections: [],
      componentCounter: 0,

      // Problem State
      currentProblemIndex: 0,
      problems: [],

      // Evaluation State
      isModalActive: false,
      isEvaluating: false,
      evaluationResult: null,
      isGeneratingQuestion: false,
      generatedQuestion: null,
      userAnswer: '',
      mermaidCode: 'graph LR\n    %% 컴포넌트를 배치하고 연결하세요!',
      showResultScreen: false,

      // Deep Dive State (3개 질문 순차 처리)
      isDeepDiveModalActive: false,
      isGeneratingDeepDive: false,
      deepDiveQuestion: null,
      deepDiveQuestions: [], // 3개 질문 배열
      currentQuestionIndex: 0, // 현재 질문 인덱스
      collectedDeepDiveAnswers: [], // 수집된 답변들
      pendingEvaluationAfterDeepDive: false, // 심화질문 후 평가 진행 플래그

      // Chat State
      chatMessages: [],
      isChatLoading: false
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
        primaryColor: '#00ff9d',
        primaryTextColor: '#0a0e27',
        primaryBorderColor: '#00e676',
        lineColor: '#64b5f6',
        secondaryColor: '#ff4785',
        tertiaryColor: '#ffc107'
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
  methods: {
    // === Problem Loading ===
    async loadProblems() {
      try {
        const data = await fetchProblems();
        this.problems = transformProblems(data);
        // 인덱스 범위 체크
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
      this.isConnectionMode = !this.isConnectionMode;
    },

    clearCanvas() {
      this.droppedComponents = [];
      this.connections = [];
      this.componentCounter = 0;
      this.evaluationResult = null;
      this.deepDiveQuestions = [];
      this.currentQuestionIndex = 0;
      this.collectedDeepDiveAnswers = [];
      this.chatMessages = [];
      this.updateMermaid();
    },

    // === Palette Events ===
    onPaletteDragStart() {
      // Optional: track drag start for analytics
    },

    // === Canvas Events ===
    onComponentDropped({ type, text, x, y }) {
      this.droppedComponents.push({
        id: `comp_${this.componentCounter++}`,
        type,
        text,
        x,
        y
      });
      this.updateMermaid();
    },

    onComponentMoved({ id, x, y }) {
      const comp = this.droppedComponents.find(c => c.id === id);
      if (comp) {
        comp.x = x;
        comp.y = y;
      }
    },

    onComponentRenamed({ id, text }) {
      const comp = this.droppedComponents.find(c => c.id === id);
      if (comp) {
        comp.text = text;
        this.updateMermaid();
      }
    },

    onComponentDeleted(compId) {
      // Remove the component
      this.droppedComponents = this.droppedComponents.filter(c => c.id !== compId);
      // Remove all connections involving this component
      this.connections = this.connections.filter(
        conn => conn.from !== compId && conn.to !== compId
      );
      this.updateMermaid();
    },

    onConnectionCreated({ from, to, fromType, toType }) {
      // Check for existing connection
      const exists = this.connections.some(c =>
        (c.from === from && c.to === to) ||
        (c.from === to && c.to === from)
      );

      if (!exists) {
        this.connections.push({ from, to, fromType, toType });
        this.updateMermaid();
        // 심화질문은 최종 제출 시에만 진행 (단계별 질문 제거)
      }
    },

    // === Mermaid ===
    updateMermaid() {
      this.mermaidCode = generateMermaidCode(this.droppedComponents, this.connections);
    },

    // === Deep Dive Modal (3개 질문 순차 처리) ===
    async skipDeepDive() {
      // 답변 없이 스킵 - 빈 답변 기록
      this.collectedDeepDiveAnswers.push({
        category: this.deepDiveQuestions[this.currentQuestionIndex]?.category || '',
        question: this.deepDiveQuestion,
        answer: '(스킵됨)'
      });

      // 다음 질문으로 이동
      await this.moveToNextQuestion();
    },

    async submitDeepDiveAnswer(answer) {
      // 답변 저장
      if (answer) {
        this.collectedDeepDiveAnswers.push({
          category: this.deepDiveQuestions[this.currentQuestionIndex]?.category || '',
          question: this.deepDiveQuestion,
          answer: answer
        });

        // 채팅 메시지에도 기록 (평가에 사용)
        this.chatMessages.push({
          role: 'user',
          content: `[심화 질문 - ${this.deepDiveQuestions[this.currentQuestionIndex]?.category}] ${this.deepDiveQuestion}\n\n[답변] ${answer}`,
          type: 'answer'
        });
      }

      // 다음 질문으로 이동
      await this.moveToNextQuestion();
    },

    async moveToNextQuestion() {
      this.currentQuestionIndex++;

      // 아직 질문이 남아있으면 다음 질문 표시
      if (this.currentQuestionIndex < this.deepDiveQuestions.length) {
        this.deepDiveQuestion = this.deepDiveQuestions[this.currentQuestionIndex].question;
      } else {
        // 모든 질문 완료 - 평가 모달로 진행
        this.isDeepDiveModalActive = false;
        this.deepDiveQuestion = null;

        if (this.pendingEvaluationAfterDeepDive) {
          this.pendingEvaluationAfterDeepDive = false;
          await this.showEvaluationModal();
        }
      }
    },

    // === Evaluation Modal ===
    async openEvaluationModal() {
      // 컴포넌트가 있으면 먼저 아키텍처 분석 기반 심화질문 진행
      if (this.droppedComponents.length > 0) {
        this.pendingEvaluationAfterDeepDive = true;
        await this.triggerFinalDeepDiveQuestions();
        return;
      }

      // 컴포넌트가 없으면 바로 평가 모달 열기
      await this.showEvaluationModal();
    },

    async showEvaluationModal() {
      this.isModalActive = true;
      this.isGeneratingQuestion = true;
      this.generatedQuestion = null;

      try {
        const architectureContext = buildArchitectureContext(
          this.droppedComponents,
          this.connections,
          this.mermaidCode
        );
        this.generatedQuestion = await generateEvaluationQuestion(
          this.currentProblem,
          architectureContext
        );
      } finally {
        this.isGeneratingQuestion = false;
      }
    },

    // 최종 제출 시 아키텍처 분석 기반 3개 심화질문 생성
    async triggerFinalDeepDiveQuestions() {
      this.isDeepDiveModalActive = true;
      this.isGeneratingDeepDive = true;
      this.currentQuestionIndex = 0;
      this.collectedDeepDiveAnswers = [];

      try {
        // Mermaid 다이어그램과 아키텍처 정보를 분석하여 3개 질문 생성
        this.deepDiveQuestions = await generateArchitectureAnalysisQuestions(
          this.currentProblem,
          this.droppedComponents,
          this.connections,
          this.mermaidCode
        );

        // 첫 번째 질문 표시
        if (this.deepDiveQuestions.length > 0) {
          this.deepDiveQuestion = this.deepDiveQuestions[0].question;
        }
      } finally {
        this.isGeneratingDeepDive = false;
      }
    },

    closeModal() {
      this.isModalActive = false;
      this.generatedQuestion = null;
    },

    async submitEvaluationAnswer(answer) {
      this.userAnswer = answer;
      this.isModalActive = false;
      // 평가 결과 화면으로 전환
      this.showResultScreen = true;
      await this.evaluate();
    },

    async evaluate() {
      this.isEvaluating = true;
      this.evaluationResult = null;

      const architectureContext = buildArchitectureContext(
        this.droppedComponents,
        this.connections,
        this.mermaidCode
      );

      // 수집된 심화질문 답변들 정리
      const deepDiveAnswers = this.collectedDeepDiveAnswers
        .filter(item => item.answer !== '(스킵됨)')
        .map(item => `[${item.category}] Q: ${item.question}\nA: ${item.answer}`)
        .join('\n\n');

      try {
        this.evaluationResult = await evaluateArchitecture(
          this.currentProblem,
          architectureContext,
          this.generatedQuestion,
          this.userAnswer,
          deepDiveAnswers
        );
      } catch (error) {
        console.error('Evaluation error:', error);
        const mock = mockEvaluations[this.currentProblemIndex] || mockEvaluations[0];
        this.evaluationResult = {
          ...JSON.parse(JSON.stringify(mock)),
          summary: `API 연결 문제로 기본 평가를 제공합니다. ${mock.summary}`
        };
      } finally {
        this.isEvaluating = false;
      }
    },

    // === Retry (from result screen) ===
    handleRetry() {
      this.showResultScreen = false;
      this.clearCanvas();
    },

    // === Chat ===
    async handleChatMessage(userMessage) {
      const messageType = detectMessageType(userMessage);

      this.chatMessages.push({
        role: 'user',
        content: userMessage,
        type: messageType
      });

      this.isChatLoading = true;

      try {
        const chatContext = buildChatContext(this.currentProblem);
        const response = await sendChatMessage(
          chatContext,
          this.chatMessages.slice(0, -1), // Exclude the just-added message
          userMessage
        );

        const hasFollowUp = response.includes('?') && response.split('?').length > 1;

        this.chatMessages.push({
          role: 'assistant',
          content: response,
          type: hasFollowUp ? 'followup' : 'answer'
        });
      } catch (error) {
        console.error('Chat error:', error);
        this.chatMessages.push({
          role: 'assistant',
          content: 'API 연결에 문제가 발생했습니다. API 키를 확인해주세요.',
          type: 'error'
        });
      } finally {
        this.isChatLoading = false;
      }
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Orbitron:wght@700;900&family=Space+Mono:wght@400;700&display=swap');

.arch-challenge-container {
  font-family: 'Space Mono', monospace;
  background: #0a0e27;
  color: #e0e0e0;
  height: 100vh;
  overflow: hidden;
  position: relative;
}

.bg-animation {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.3;
  background:
    radial-gradient(ellipse at 20% 30%, rgba(0, 255, 157, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 70%, rgba(255, 71, 133, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(100, 181, 246, 0.1) 0%, transparent 50%);
  animation: float 20s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.1); }
  66% { transform: translate(-30px, 30px) scale(0.9); }
}

.game-container {
  display: grid;
  grid-template-columns: 350px 1fr 350px;
  width: 100%;
  height: 100vh;
  gap: 0;
  position: relative;
  z-index: 1;
}

.result-panel {
  background: rgba(17, 24, 39, 0.98);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
</style>
