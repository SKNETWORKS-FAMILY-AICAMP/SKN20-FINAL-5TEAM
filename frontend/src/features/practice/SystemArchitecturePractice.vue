<template>
  <div class="arch-challenge-container panic-room-theme">
    <!-- 인트로 씬 (비주얼 노벨 스타일) -->
    <div v-if="showIntro" class="scene-intro" @click="nextIntroLine">
      <div class="spotlight"></div>

      <div class="intro-duck" :class="{ appear: duckAppeared }">
        <img src="/image/duck_det.png" alt="Detective Duck" />
      </div>

      <div class="intro-dialog-box" v-if="!showStartBtn">
        <div class="speaker-name">DET. DUCK</div>
        <div class="intro-text">{{ displayedIntroText }}</div>
        <div class="next-indicator">▼ Click to continue</div>
      </div>

      <button v-if="showStartBtn" class="start-btn" @click="enterGame">
        취조실 입장 (ENTER)
      </button>
    </div>

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
      <div class="bg-animation"></div>

      <div class="game-container">

        <!-- 케이스 파일 패널 (좌측) -->
        <div class="case-file-panel">
          <!-- 오리 형사 프로필 -->
          <div class="detective-profile">
            <div class="img-box">
              <img src="/image/duck_det.png" alt="Detective Duck" class="detective-avatar" />
            </div>
            <p class="detective-name">DET. DUCK</p>
          </div>

          <!-- 문제 카드 -->
          <ProblemCard
            :problem="currentProblem"
            :is-connection-mode="isConnectionMode"
            :can-evaluate="droppedComponents.length > 0"
            :is-evaluating="isEvaluating"
            :mermaid-code="mermaidCode"
            @start-evaluation="openEvaluationModal"
          />
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

      <!-- 오리 형사 심문 패널 (하단) -->
      <div
        class="interrogation-panel"
        :class="{ 'panel-minimized': isPanelMinimized }"
        @click="handlePanelClick"
      >
        <div class="detective-face">
          <img src="/image/duck_det.png" alt="Detective Duck" />
        </div>
        <div class="dialog-container">
          <div class="dialog-box">{{ detectiveMessage }}</div>
        </div>
      </div>

      <!-- 평가 모달 -->
      <EvaluationModal
        :is-active="isModalActive"
        :question="generatedQuestion"
        :is-generating="isGeneratingQuestion"
        :components="droppedComponents"
        :connections="connections"
        :mermaid-code="mermaidCode"
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
} from './services/architectureApiFast'

import {
  transformProblems,
  detectMessageType,
  buildChatContext,
  buildArchitectureContext,
  generateMermaidCode,
  generateMockEvaluation
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
      // Intro State (비주얼 노벨 스타일)
      showIntro: true,
      introLines: [
        "거기 서! 도망갈 생각 마라. 꽥!",
        "네가 오늘 발생한 대규모 서버 폭파 사건의 가장 유력한 용의자로 지목되었다.",
        "억울하다고? 그렇다면 취조실로 들어와서 직접 증명해 봐.",
        "올바른 시스템 아키텍처를 설계해서 네 결백을 입증하는 거다!",
        "(철창 문이 열린다...)"
      ],
      introIndex: 0,
      displayedIntroText: '',
      duckAppeared: false,
      showStartBtn: false,
      introTypingInterval: null,
      introIsTyping: false,
      currentIntroFullText: '',

      // Detective Panel State
      detectiveMessage: '자, 여기에 앉아. 왼쪽 사건 파일을 보고 설계도를 완성해. 꽥!',
      isPanelMinimized: false,

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

    // 인트로 애니메이션 시작
    setTimeout(() => {
      this.duckAppeared = true;
      this.typeIntroText(this.introLines[0]);
    }, 500);
  },
  methods: {
    // === Intro Methods ===
    typeIntroText(text) {
      this.displayedIntroText = '';
      this.currentIntroFullText = text;
      this.introIsTyping = true;
      let i = 0;

      clearInterval(this.introTypingInterval);
      this.introTypingInterval = setInterval(() => {
        if (i < text.length) {
          this.displayedIntroText += text.charAt(i);
          i++;
        } else {
          this.finishIntroTyping();
        }
      }, 30);
    },

    finishIntroTyping() {
      clearInterval(this.introTypingInterval);
      this.displayedIntroText = this.currentIntroFullText;
      this.introIsTyping = false;
    },

    nextIntroLine() {
      if (this.introIsTyping) {
        this.finishIntroTyping();
        return;
      }

      this.introIndex++;
      if (this.introIndex < this.introLines.length) {
        this.typeIntroText(this.introLines[this.introIndex]);
      } else {
        this.showStartBtn = true;
      }
    },

    enterGame() {
      this.showIntro = false;
      this.typeDetectiveMessage('자, 여기에 앉아. 왼쪽 사건 파일을 보고 설계도를 완성해. (패널을 클릭하면 내려갑니다) 꽥!');
    },

    // === Detective Panel Methods ===
    typeDetectiveMessage(text) {
      this.detectiveMessage = '';
      let i = 0;
      const interval = setInterval(() => {
        if (i < text.length) {
          this.detectiveMessage += text.charAt(i);
          i++;
        } else {
          clearInterval(interval);
        }
      }, 30);
    },

    handlePanelClick(e) {
      if (e.target.closest('.dialog-box')) return;
      this.isPanelMinimized = !this.isPanelMinimized;
    },

    showPanel() {
      this.isPanelMinimized = false;
    },

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

      // 수집된 심화질문 답변들 (배열 형태로 전달)
      const deepDiveQnA = this.collectedDeepDiveAnswers.map(item => ({
        category: item.category,
        question: item.question,
        answer: item.answer === '(스킵됨)' ? '' : item.answer
      }));

      try {
        this.evaluationResult = await evaluateArchitecture(
          this.currentProblem,
          architectureContext,
          this.generatedQuestion,
          this.userAnswer,
          deepDiveQnA
        );
      } catch (error) {
        console.error('Evaluation error:', error);
        // 문제 데이터 기반으로 동적 Mock 평가 생성
        this.evaluationResult = generateMockEvaluation(
          this.currentProblem,
          this.droppedComponents
        );
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
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Courier+Prime:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap');

:root {
  --bg-color: #1a1a1a;
  --accent-yellow: #f1c40f;
  --danger-red: #e74c3c;
  --text-white: #ecf0f1;
  --border-black: #000;
}

.arch-challenge-container.panic-room-theme {
  font-family: 'Press Start 2P', cursive;
  background: #1a1a1a;
  color: #ecf0f1;
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
  opacity: 0.15;
  background:
    radial-gradient(ellipse at 20% 30%, rgba(241, 196, 15, 0.2) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 70%, rgba(231, 76, 60, 0.2) 0%, transparent 50%);
}

/* === INTRO SCENE === */
.scene-intro {
  width: 100%;
  height: 100%;
  background: #111;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  cursor: pointer;
}

.spotlight {
  position: absolute;
  top: -100px;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  height: 100%;
  background: radial-gradient(ellipse at top, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
  pointer-events: none;
  z-index: 1;
}

.intro-duck {
  width: 400px;
  height: 400px;
  z-index: 2;
  filter: drop-shadow(0 0 20px rgba(0, 0, 0, 0.5));
  transform: translateY(50px);
  transition: transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.intro-duck.appear {
  transform: translateY(0);
}

.intro-duck img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.intro-dialog-box {
  width: 90%;
  /* max-width: 800px; */
  min-height: 180px;
  background: rgba(0, 0, 0, 0.9);
  border: 4px solid white;
  border-radius: 10px;
  margin-bottom: 40px;
  padding: 25px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 1);
}

.speaker-name {
  color: #f1c40f;
  font-size: 1.5rem;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.intro-text {
  font-family: 'Courier Prime', monospace;
  font-size: 1.6rem;
  line-height: 1.8;
  color: white;
  flex: 1;
}

.next-indicator {
  align-self: flex-end;
  color: #f1c40f;
  animation: bounce 1s infinite;
  font-size: 1.2rem;
}

.start-btn {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: #e74c3c;
  color: white;
  border: 4px solid white;
  padding: 20px 40px;
  font-family: 'Press Start 2P', cursive;
  font-size: 1rem;
  cursor: pointer;
  z-index: 20;
  box-shadow: 10px 10px 0 black;
  animation: pulse-btn 1s infinite;
  transition: transform 0.2s;
}

.start-btn:hover {
  transform: translate(-50%, -55%);
}

/* === MAIN GAME === */
.game-container {
  display: grid;
  grid-template-columns: 320px 1fr 320px;
  width: 100%;
  height: calc(100vh - 220px);
  gap: 0;
  position: relative;
  z-index: 1;
}

.case-file-panel {
  background: #222;
  border-right: 6px solid #000;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  z-index: 20;
}

.detective-profile {
  text-align: center;
  border-bottom: 2px dashed #555;
  padding-bottom: 15px;
}

.detective-profile .img-box {
  display: flex;
  justify-content: center;
}

.detective-avatar {
  width: 80px;
  height: 80px;
  border: 3px solid white;
  border-radius: 50%;
  object-fit: contain;
  background: #81ecec;
}

.detective-name {
  color: #f1c40f;
  margin-top: 8px;
  font-size: 0.7rem;
}

/* === INTERROGATION PANEL === */
.interrogation-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 200px;
  background: rgba(0, 0, 0, 0.95);
  border-top: 6px solid #f1c40f;
  display: flex;
  padding: 20px;
  gap: 20px;
  z-index: 100;
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  cursor: pointer;
}

.interrogation-panel.panel-minimized {
  transform: translateY(194px);
}

.interrogation-panel::before {
  content: "▲ CLICK TO SHOW DETECTIVE ▲";
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  background: #f1c40f;
  color: black;
  padding: 5px 15px;
  font-size: 0.6rem;
  font-weight: bold;
  border: 4px solid black;
  border-bottom: none;
  display: none;
}

.interrogation-panel.panel-minimized::before {
  display: block;
  animation: bounce 1s infinite;
}

.detective-face {
  width: 100px;
  height: 100px;
  border: 4px solid white;
  background: #81ecec;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
}

.detective-face img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.dialog-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dialog-box {
  flex: 1;
  border: 2px dashed #555;
  padding: 15px;
  color: #f1c40f;
  font-family: 'Courier Prime', monospace;
  font-size: 1rem;
  line-height: 1.6;
  overflow-y: auto;
}

/* === ANIMATIONS === */
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

@keyframes pulse-btn {
  50% { opacity: 0.8; transform: translate(-50%, -50%) scale(0.98); }
}
</style>
