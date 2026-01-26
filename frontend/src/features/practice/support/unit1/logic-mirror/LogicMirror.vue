<template>
  <div class="logic-mirror-modal-overlay" @click.self="$emit('close')">
    <div class="logic-mirror-modal-container">
      <button class="modal-close-btn" @click="$emit('close')">&times;</button>

      <!-- Loading State -->
      <div v-if="!currentQuest" class="loading-screen">
        <div class="loading-content">
          <!-- [2026-01-24] 템플릿 내 이모지가 유니코드 코드로 노출되는 문제 해결을 위해 HTML 엔티티로 교체 -->
          <div class="loading-spinner">&#x1F3AE;</div>
          <p class="loading-text">게임을 준비하고 있습니다...</p>
        </div>
      </div>

      <!-- Game Content -->
      <div class="logic-mirror-pipeline" v-else>
    <!-- Pipeline Progress Bar -->
    <div class="pipeline-progress">
      <div class="progress-steps">
        <div 
          v-for="(step, index) in pipelineSteps" 
          :key="index"
          class="progress-step"
          :class="{ 
            'active': currentStepIndex === index,
            'completed': currentStepIndex > index
          }"
        >
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-label">{{ step }}</div>
        </div>
      </div>
    </div>

    <!-- Step 1: Problem & Interviewer Q&A -->
    <div v-if="currentStepIndex === 0" class="pipeline-step problem-step">
      <div class="step-container">
        <div class="problem-header">
          <div class="problem-emoji">{{ currentQuest.emoji }}</div>
          <div class="problem-info">
            <h1 class="problem-title">
              <span class="quest-num-label">{{ questDisplayNumber }}</span>
              {{ currentQuest.title }}
            </h1>
            <p class="problem-description">{{ currentQuest.description }}</p>
            <div class="problem-meta">
              <span class="logic-type">{{ currentQuest.logic_type }}</span>
              <span class="level-badge">LV {{ currentQuest.level }}</span>
            </div>
          </div>
        </div>

        <div class="examples-box">
          <h3>&#x1F4DD; 예제 입출력</h3>
          <pre>{{ currentQuest.examples }}</pre>
        </div>

        <div class="interviewer-intro">
          <div class="interviewer-avatar">
            <img src="/image/problem_duck.gif" alt="Duck Coach" class="duck-coach-img" />
          </div>
          <div class="interviewer-bubble">
            <div class="interviewer-label">덕 코치</div>
            <p>"이 문제를 어떻게 해결하시겠어요? 단계별로 나눠서 생각해보세요."</p>
          </div>
        </div>

        <button @click="goToNextStep" class="next-step-btn">
          <span>수도코드 작성하기 →</span>
        </button>
      </div>
    </div>

    <!-- Step 2: Pseudo Code Interface -->
    <div v-if="currentStepIndex === 1" class="pipeline-step pseudocode-step">
      <div class="step-container">
        <h2 class="step-title">&#x1F4DD; 수도코드로 풀이 과정 표현하기</h2>
        <p class="step-subtitle">카드를 드래그해서 올바른 순서로 배치하세요</p>

        <div class="pseudocode-layout">
          <!-- Card Deck -->
          <div class="card-deck-section">
            <h3 class="section-title">&#x1F3B4; 사용 가능한 블록</h3>
            <div class="cards-list">
              <div 
                v-for="card in currentQuest.cards" 
                :key="card.id"
                class="action-card"
                :class="`card-${card.color}`"
                draggable="true"
                @dragstart="handleDragStart(card)"
                @dragend="handleDragEnd"
              >
                <div class="card-icon">{{ card.icon }}</div>
                <div class="card-content">
                  <div class="card-text">{{ card.text_ko }}</div>
                  <div class="card-code">{{ card.text_py }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Drop Zone -->
          <div class="drop-zone-section flex-column">
            <div class="section-header">
              <h3 class="section-title">&#x1F9E0; 내가 구성한 순서</h3>
              <button v-if="userSequence.length > 0" @click="clearSequence" class="clear-btn">
                &#x1F5D1;&#xFE0F; 초기화
              </button>
            </div>
            
            <div 
              class="drop-zone"
              @drop="handleDrop"
              @dragover.prevent
              @dragenter.prevent="isDragOver = true"
              @dragleave="isDragOver = false"
              :class="{ 'drag-over': isDragOver }"
            >
              <div v-if="userSequence.length === 0" class="empty-state">
                <div class="empty-icon">&#x2728;</div>
                <p>왼쪽에서 카드를 드래그해서 순서를 만드세요</p>
              </div>

              <div v-else class="sequence-list">
                <div 
                  v-for="(card, index) in userSequence" 
                  :key="`${card.id}-${index}`"
                  class="sequence-card"
                  :class="{
                    [`card-${card.color}`]: true,
                    'shake': wrongBlockIndices.includes(index)
                  }"
                  :style="{ marginLeft: (card.indent || 0) * 30 + 'px' }"
                >
                  <div class="seq-number">{{ index + 1 }}</div>
                  <div class="card-icon">{{ card.icon }}</div>
                  <div class="card-text">{{ card.text_ko }}</div>
                  <button @click="removeCard(index)" class="remove-btn">✕</button>
                </div>
              </div>
            </div>

            <button 
              v-if="userSequence.length > 0"
              @click="goToNextStep" 
              class="submit-btn"
            >
              제출하기 →
            </button>
          </div>

          <!-- Mermaid Visualization Area [2026-01-24] New -->
          <div class="visualization-section">
            <div class="section-header">
              <h3 class="section-title">&#x1F52E; 실시간 흐름도</h3>
            </div>
            <div class="mermaid-container" ref="mermaidTarget">
              <div v-if="userSequence.length === 0" class="vis-empty-state">
                카드가 구성되면 흐름도가 나타납니다
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 3: Pre-submission Query -->
    <div v-if="currentStepIndex === 2" class="pipeline-step query-step">
      <div class="step-container">
        <h2 class="step-title">&#x1F914; 제출 전 확인</h2>
        
        <div class="submitted-code-box">
          <h3>제출한 수도코드</h3>
          <div class="code-preview">
            <div 
              v-for="(card, index) in userSequence" 
              :key="index"
              class="code-line"
              :style="{ paddingLeft: (card.indent || 0) * 20 + 'px' }"
            >
              <span class="line-number">{{ index + 1 }}</span>
              <span class="line-code">{{ card.text_py }}</span>
            </div>
          </div>
        </div>

        <div class="interviewer-questions">
          <div class="interviewer-avatar">
            <img src="/image/problem_duck.gif" alt="Duck Coach" class="duck-coach-img" />
          </div>
          <div class="question-bubble">
            <div class="interviewer-label">덕 코치</div>
            <p class="question-text">{{ preSubmissionQuestion }}</p>
            
            <div class="answer-options">
              <button 
                v-for="(option, index) in answerOptions" 
                :key="index"
                @click="selectAnswer(index)"
                class="option-btn"
                :class="{ 'selected': selectedAnswer === index }"
              >
                {{ option }}
              </button>
            </div>
          </div>
        </div>

        <div class="action-buttons">
          <button @click="goToPreviousStep" class="back-btn">← 수정하기</button>
          <button 
            @click="submitAndCheck" 
            class="confirm-btn"
            :disabled="selectedAnswer === null"
          >
            최종 제출
          </button>
        </div>
      </div>
    </div>

    <!-- Step 4: Real Implementation (Optional) -->
    <div v-if="currentStepIndex === 3" class="pipeline-step implementation-step">
      <div class="step-container">
        <div class="result-header" :class="isCorrect ? 'success' : 'failure'">
          <div class="result-icon">{{ isCorrect ? '&#x2705;' : '&#x1F914;' }}</div>
          <div class="result-content">
            <div class="judge-mini-badge" v-if="isCorrect">PUZZLE ACCEPTED</div>
            <h2>{{ feedbackMessage }}</h2>
            <p class="hint-text" v-if="hintMessage">&#x1F4A1; {{ hintMessage }}</p>
          </div>
        </div>

        <div v-if="isCorrect" class="implementation-section">
          <h3>&#x1F4BB; Pseudo Implementer</h3>
          <p class="section-desc">수도코드를 바탕으로 실제 파이썬 코드를 완성하고 검증받으세요</p>
          
          <div class="code-editor monaco-wrapper">
            <vue-monaco-editor
              v-model:value="userCode"
              theme="vs-dark"
              language="python"
              :options="editorOptions"
              class="professional-editor"
              @mount="handleEditorMount"
            />
          </div>

          <!-- Duck Coach Execution Feedback -->
          <div class="execution-feedback" v-if="executionOutput || executionError">
            <div class="interviewer-intro">
               <div class="interviewer-avatar">
                 <img :src="isRunPassed ? '/image/success_duck.gif' : '/image/problem_duck.gif'" alt="Duck Coach" class="duck-coach-img" />
               </div>
               <div class="interviewer-bubble">
                 <div class="interviewer-label">덕 코치</div>

                  <!-- Judge Status Badge -->
                  <div class="judge-status-container" v-if="judgeStatus">
                    <div class="status-badge" :class="judgeStatus.toLowerCase().replace(' ', '-')">
                      {{ judgeStatus }}
                    </div>
                    <div class="accuracy-info" v-if="testResults.length > 0">
                      정확도: <span class="percent">{{ accuracy }}%</span>
                      <div class="accuracy-bar">
                        <div class="accuracy-fill" :style="{ width: accuracy + '%' }"></div>
                      </div>
                    </div>
                  </div>

                 <p class="execution-msg" :class="{ 'error': executionError }">
                    {{ judgeMessage }}
                 </p>
                  <!-- Test Case Results Table -->
                  <div v-if="testResults.length > 0" class="test-results-container">
                    <table class="test-results-table">
                      <thead>
                        <tr>
                          <th>입력값</th>
                          <th>실행결과</th>
                          <th>상태</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(res, idx) in testResults" :key="idx" :class="res.passed ? 'pass' : 'fail'">
                          <td><code>{{ res.input }}</code></td>
                          <td><code>{{ res.output }}</code></td>
                          <td>{{ res.passed ? '✅ Pass' : '❌ Fail' }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <pre class="stdout-box" v-if="executionOutput && !isRunPassed">{{ executionOutput }}</pre>
               </div>
            </div>
          </div>

          <div class="implementation-actions">
            <div class="left-actions">
              <button @click="skipImplementation" class="skip-btn">건너뛰기</button>
              <button @click="toggleHint" class="hint-btn">
                <span class="btn-icon">&#x1F4E6;</span> 힌트 보기
              </button>
            </div>
            <button @click="handleRunPython" class="run-btn" :disabled="isPyodideLoading">
               {{ isPyodideLoading ? '엔진 로드 중...' : '▶ 프로젝트 실행' }}
            </button>
          </div>

          <div v-if="showHint" class="hint-overlay-box">
             <div class="hint-header">
               <span class="hint-status-dot"></span>
               덕 코치의 보따리 힌트
             </div>
             <div class="hint-content">
               <p class="hint-main-desc">{{ implementationHint.main }}</p>
               <div class="hint-divider"></div>
               <p class="hint-sub-desc">{{ implementationHint.sub }}</p>
               <ul class="hint-code-list">
                  <li v-for="card in currentQuest.cards" :key="card.id">
                    <span class="card-icon">{{ card.icon }}</span>
                    <code>{{ card.text_py }}</code>
                    <span class="card-text-ko">{{ card.text_ko }}</span>
                  </li>
               </ul>
             </div>
          </div>
        </div>

        <div v-else class="retry-section">
          <button @click="retry" class="retry-btn">다시 시도하기</button>
        </div>
      </div>
    </div>

    <!-- Step 5: Follow-up Questioning -->
    <div v-if="currentStepIndex === 4" class="pipeline-step followup-step">
      <div class="step-container">
        <div class="completion-header">
          <div class="completion-icon">&#x1F389;</div>
          <h1 class="completion-title">문제 완료!</h1>
        </div>

        <div class="interviewer-followup">
          <div class="interviewer-avatar">
            <img src="/image/problem_duck.gif" alt="Duck Coach" class="duck-coach-img" />
          </div>
          <div class="followup-bubble">
            <div class="interviewer-label">덕 코치</div>
            <p class="followup-question">{{ currentFollowupQuestion.question }}</p>
            
            <!-- [2026-01-24] 심화 평가용 선택지 UI 추가 -->
            <div class="followup-options" v-if="!followupAnswered">
              <button 
                v-for="(option, idx) in currentFollowupQuestion.options" 
                :key="idx"
                @click="checkFollowupAnswer(idx)"
                class="followup-option-btn"
              >
                {{ option }}
              </button>
            </div>

            <!-- [2026-01-24] 답변 후 피드백 박스 -->
            <div class="followup-feedback-box" v-else :class="followupIsCorrect ? 'pass' : 'fail'">
              <div class="feedback-status">
                {{ followupIsCorrect ? '✅ 정답입니다!' : '🤔 조금 더 생각해볼까요?' }}
              </div>
              <p class="explanation-text">{{ currentFollowupQuestion.explanation }}</p>
              <button v-if="!followupIsCorrect" @click="followupAnswered = false" class="re-answer-btn">다시 선택하기</button>
            </div>
          </div>
        </div>

        <div class="learning-summary">
          <h3>📚 이번 문제에서 배운 점</h3>
          <ul class="learning-points">
            <li v-for="(point, index) in learningPoints" :key="index">
              {{ point }}
            </li>
          </ul>
        </div>

        <div class="navigation-buttons">
          <button @click="finishSession" class="next-quest-btn">
             학습 완료
          </button>
        </div>
      </div>
    </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick, shallowRef } from 'vue';
import { VueMonacoEditor } from '@guolao/vue-monaco-editor';
import mermaid from 'mermaid';
import { gameData } from './data/stages.js';
import { usePyodide } from '@/composables/usePyodide';

/* 
  수정일: 2026-01-24
  수정내용: 
  - Monaco Editor(VS Code 엔진) 통합으로 입축 환경 개선 (Tab 키 지원 및 문법 강조)
  - 덕 코치(오리 캐릭터) 이미지 및 애니메이션 적용 (성공 시 댄스 GIF 포함)
  - 단계별 정밀 평가 로직 고도화 및 Pyodide 기반 파이썬 실행 엔진 통합
*/

const props = defineProps({
  initialQuestIndex: {
    type: Number,
    default: 0
  }
});

const emit = defineEmits(['close', 'quest-complete']);

// Pipeline Steps
const pipelineSteps = [
  'Problem & Q&A',
  'Pseudo Code',
  'Pre-submission',
  'Implementation',
  'Follow-up'
];

// Game State
const currentStepIndex = ref(0);
const currentQuestIndex = ref(props.initialQuestIndex);
const currentQuest = ref(null);
const userSequence = ref([]);
const selectedAnswer = ref(null);
const userCode = ref('');
const isCorrect = ref(false);
const feedbackMessage = ref('');
const hintMessage = ref('');
const isDragOver = ref(false);
const draggedCard = ref(null);
const wrongBlockIndices = ref([]); // 틀린 블록 인덱스 추적
const duckCoachHint = ref(''); // 덕 코치 실시간 힌트
const executionOutput = ref('');
const executionError = ref('');
const judgeStatus = ref('READY');
const judgeMessage = ref('');
const isRunPassed = ref(false);

/* [2026-01-24] 심화 평가(Follow-up) 인터랙티브 상태 관리를 위한 변수 추가 */
const followupAnswered = ref(false);
const followupIsCorrect = ref(false);

/* [2026-01-24] Mermaid 실시간 시각화 컴포넌트 변수 */
const mermaidTarget = ref(null);

const { runCode: runPython, initPyodide, isLoading: isPyodideLoading } = usePyodide();

// Monaco Editor Config [2026-01-24]
const monacoEditorRef = shallowRef(null);
const editorOptions = {
  theme: 'vs-dark',
  language: 'python',
  tabSize: 4,
  automaticLayout: true,
  minimap: { enabled: false },
  fontSize: 14,
  lineNumbers: 'on',
  scrollBeyondLastLine: false,
  roundedSelection: true,
  cursorSmoothCaretAnimation: "on",
  fontFamily: "'JetBrains Mono', 'Courier New', monospace",
  contextmenu: false,
  padding: { top: 15, bottom: 15 }
};

const handleEditorMount = (editorInstance) => {
  monacoEditorRef.value = editorInstance;
};

// Computed
const isLastQuest = computed(() => currentQuestIndex.value === gameData.quests.length - 1);

/* [2026-01-24] 퀘스트 번호를 1-1, 1-2 형식으로 표시하기 위한 계산된 속성 추가 */
const questDisplayNumber = computed(() => {
  if (!currentQuest.value) return '';
  return `1-${currentQuestIndex.value + 1}`;
});


/* [2026-01-24] 하드코딩된 질문 대신 현재 퀘스트 데이터(stages.js)에 정의된 맞춤형 질문을 반환하도록 수정 */
const preSubmissionQuestion = computed(() => {
  return currentQuest.value?.reasoning?.question || "이 순서를 선택한 이유를 설명해주세요.";
});

/* [2026-01-24] 하드코딩된 선택지 대신 현재 퀘스트 데이터에 정의된 맞춤형 선택지 배열을 반환하도록 수정 */
const answerOptions = computed(() => {
  return currentQuest.value?.reasoning?.options || [
    "순서대로 실행되어야 하기 때문입니다",
    "조건에 맞을 때만 실행되어야 합니다",
    "반복해서 실행되어야 합니다",
    "확실하지 않습니다"
  ];
});

/* [2026-01-24] 심화 평가 질문 정보를 안전하게 가져오는 계산된 속성 추가 (데이터 부재 시 Fallback 처리) */
const currentFollowupQuestion = computed(() => {
  const q = currentQuest.value?.interviewQuestions?.[0];
  return {
    question: q?.question || "수고하셨습니다! 마무리 단계로 넘어가볼까요?",
    options: q?.options || ["네, 좋습니다!"],
    correctIndex: q?.correctIndex ?? 0,
    explanation: q?.explanation || "오늘 배운 내용을 잘 기억해보시길 바란다꽥!"
  };
});

const learningPoints = computed(() => {
  return [
    currentQuest.value?.feedback?.hint || "문제 해결 과정을 단계별로 나눠서 생각하기",
    "수도코드로 로직을 먼저 설계하기",
    "각 단계의 순서와 의미 이해하기"
    ];
});

/* [2026-01-24] 덕 코치의 보따리 힌트 문구를 동적으로 생성하는 계산된 속성 추가 (하드코딩 제거) */
const implementationHint = computed(() => {
  const hint = currentQuest.value?.validation?.execution?.implementation_hint;
  const funcName = currentQuest.value?.validation?.execution?.function_name || 'my_function';
  
  return {
    main: hint?.main || `이 문제의 파이썬 정답은 def ${funcName}(): 로 시작해야 하꽥!`,
    sub: hint?.sub || "카드에 있던 명령어들을 순서대로 넣어주면 된다꽥:"
  };
});

/* [2026-01-24] userSequence 변화에 따라 실시간으로 그려질 Mermaid 코드 생성 로직 */
const mermaidCode = computed(() => {
    if (userSequence.value.length === 0) return '';
    
    let code = 'flowchart TD\n';
    // Style Definitions
    code += '  classDef default fill:#1e1e2e,stroke:#45475a,color:#cdd6f4,stroke-width:2px,rx:10,ry:10;\n';
    code += '  classDef loop fill:#1e1e2e,stroke:#f9e2af,color:#f9e2af,stroke-width:2px;\n';
    code += '  classDef cond fill:#1e1e2e,stroke:#cba6f7,color:#cba6f7,stroke-width:2px;\n';
    code += '  classDef startEnd fill:#1e1e2e,stroke:#a6e3a1,color:#a6e3a1,stroke-width:3px;\n';

    // Start Node
    code += '  START([시작])\n';
    code += '  class START startEnd\n';
    
    let prevId = 'START';
    
    userSequence.value.forEach((card, idx) => {
        const nodeId = `node_${idx}`;
        const cleanText = card.text_ko.replace(/[\[\]"']/g, '').trim();
        
        if (card.isCondition || card.isLoop) {
            // Condition/Loop nodes (Diamond or Hexagon shape)
            code += `  ${nodeId}{{"${cleanText}"}}\n`;
            code += card.isLoop ? `  class ${nodeId} loop\n` : `  class ${nodeId} cond\n`;
        } else {
            // Normal nodes
            code += `  ${nodeId}["${cleanText}"]\n`;
        }
        
        code += `  ${prevId} --> ${nodeId}\n`;
        prevId = nodeId;
    });
    
    // End Node
    code += `  END([끝])\n`;
    code += `  ${prevId} --> END\n`;
    code += '  class END startEnd\n';
    
    return code;
});

// Watcher for Mermaid rendering
watch(mermaidCode, async (newCode) => {
    if (!newCode || !mermaidTarget.value) return;
    
    await nextTick();
    try {
        const { svg } = await mermaid.render(`mermaid-svg-${Date.now()}`, newCode);
        if (mermaidTarget.value) {
            mermaidTarget.value.innerHTML = svg;
        }
    } catch (e) {
        console.error('Mermaid render error:', e);
    }
});

// Initialize
const initGame = () => {
  /* [2026-01-24] Mermaid 초기화 */
  mermaid.initialize({
    startOnLoad: false,
    theme: 'dark',
    securityLevel: 'loose',
    flowchart: {
        useMaxWidth: true,
        htmlLabels: true,
        curve: 'basis'
    }
  });

  console.log('[DEBUG] initGame called');
  console.log('[DEBUG] gameData:', gameData);
  console.log('[DEBUG] gameData.quests:', gameData.quests);
  console.log('[DEBUG] gameData.quests.length:', gameData.quests?.length);
  
  try {
    if (!gameData || !gameData.quests || gameData.quests.length === 0) {
      console.error('[ERROR] gameData is invalid:', gameData);
      alert('게임 데이터를 불러올 수 없습니다. 페이지를 새로고침해주세요.');
      return;
    }
    loadQuest(currentQuestIndex.value);
  } catch (error) {
    console.error('[ERROR] initGame failed:', error);
    alert('게임 초기화 실패: ' + error.message);
  }
};

const loadQuest = (index) => {
  console.log('[DEBUG] loadQuest called with index:', index);
  try {
    if (!gameData.quests[index]) {
      console.error('[ERROR] Quest not found at index:', index);
      return;
    }
    currentQuestIndex.value = index;
    currentQuest.value = gameData.quests[index];
    console.log('[DEBUG] currentQuest loaded:', currentQuest.value);
    resetState();
  } catch (error) {
    console.error('[ERROR] loadQuest failed:', error);
  }
};

const resetState = () => {
  currentStepIndex.value = 0;
  userSequence.value = [];
  selectedAnswer.value = null;
  userCode.value = '';
  isCorrect.value = false;
  wrongBlockIndices.value = [];
  duckCoachHint.value = '';
  executionOutput.value = '';
  executionError.value = '';
  isRunPassed.value = false;
  feedbackMessage.value = '';
  hintMessage.value = '';
  showHint.value = false;
  testResults.value = [];
};

const testResults = ref([]);
const showHint = ref(false);
const toggleHint = () => {
    showHint.value = !showHint.value;
};

// Navigation
const goToNextStep = () => {
  if (currentStepIndex.value < pipelineSteps.length - 1) {
    currentStepIndex.value++;
  }
};

const goToPreviousStep = () => {
  if (currentStepIndex.value > 0) {
    currentStepIndex.value--;
  }
};

const finishSession = () => {
  /* [2026-01-24] 개별 스테이지 진행을 위해 학습 종료 시 모달을 닫고 부모에게 완료 알림 */
  emit('close');
  emit('quest-complete', currentQuestIndex.value);
};

// Drag & Drop
const handleDragStart = (card) => {
  draggedCard.value = card;
};

const handleDragEnd = () => {
  draggedCard.value = null;
  isDragOver.value = false;
};

const handleDrop = (e) => {
  e.preventDefault();
  isDragOver.value = false;
  
  if (draggedCard.value) {
    userSequence.value.push({ ...draggedCard.value });
    draggedCard.value = null;
  }
};

const removeCard = (index) => {
  userSequence.value.splice(index, 1);
};

const clearSequence = () => {
  userSequence.value = [];
};

// Answer Selection
const selectAnswer = (index) => {
  selectedAnswer.value = index;
};

/* [2026-01-24] 심화 평가 답변 검증 로직 추가 */
const checkFollowupAnswer = (index) => {
  followupAnswered.value = true;
  followupIsCorrect.value = index === currentFollowupQuestion.value.correctIndex;
};

// Submission
const submitAndCheck = () => {
  /* [2026-01-24] 단순 JSON.stringify 비교에서 ID 및 Indent 개별 정밀 비교 로직으로 고도화 */
  const userBlocks = userSequence.value;
  const solution = currentQuest.value.validation?.puzzle_solution;
  
  if (!solution) {
    // 레거시 지원
    const userOrder = userBlocks.map(card => card.id);
    const correctOrder = currentQuest.value.correctSequence;
    isCorrect.value = JSON.stringify(userOrder) === JSON.stringify(correctOrder);
    if (!isCorrect.value) {
      wrongBlockIndices.value = Array.from({length: userBlocks.length}, (_, i) => i);
    }
  } else {
    wrongBlockIndices.value = [];
    let correctCount = 0;
    
    const maxLength = Math.max(userBlocks.length, solution.length);
    
    for (let i = 0; i < maxLength; i++) {
        const userBlock = userBlocks[i];
        const solutionStep = solution[i];
        
        if (!userBlock || !solutionStep || userBlock.id !== solutionStep.id || (userBlock.indent || 0) !== (solutionStep.indent || 0)) {
            if (i < userBlocks.length) {
                wrongBlockIndices.value.push(i);
            }
        } else {
            correctCount++;
        }
    }
    
    isCorrect.value = correctCount === solution.length && userBlocks.length === solution.length;
  }
  
  /* [2026-01-24] 블록 순서뿐만 아니라 추론 질문(selectedAnswer)의 정답 여부도 함께 검증하도록 로직 고도화 */
  const isReasoningCorrect = selectedAnswer.value === (currentQuest.value?.reasoning?.correctIndex ?? 0);
  
  if (isCorrect.value) {
    if (isReasoningCorrect) {
      feedbackMessage.value = currentQuest.value.feedback?.success || '정답입니다!';
      hintMessage.value = '';
    } else {
      /* [2026-01-24] 블록 순서는 맞았지만 추론이 틀린 경우 별도의 피드백과 함께 재배치 허용 혹은 힌트 제공 */
      isCorrect.value = false; // 둘 다 맞아야 통과로 처리
      feedbackMessage.value = '블록 순서는 완벽하지만, 이유는 조금 더 생각해보자꽥!';
      hintMessage.value = '선택한 이유가 논리에 맞는지 다시 한번 확인해보세요.';
      duckCoachHint.value = "논리적인 이유를 정확히 이해하는 것이 중요하꽥!";
    }
  } else {
    feedbackMessage.value = currentQuest.value.feedback?.failure || '다시 생각해보세요';
    hintMessage.value = currentQuest.value.feedback?.hint || '';
    
    // 덕 코치 힌트 강화
    if (wrongBlockIndices.value.length > 0) {
        const firstWrong = wrongBlockIndices.value[0];
        const userBlock = userBlocks[firstWrong];
        const solutionStep = solution ? solution[firstWrong] : null;
        
        if (!userBlock) {
             duckCoachHint.value = "블록이 더 필요한 것 같꽥!";
        } else if (!solutionStep || userBlock.id !== solutionStep.id) {
             duckCoachHint.value = `${firstWrong + 1}번째 블록 종류가 틀린 것 같꽥!`;
        } else if (userBlock.indent !== solutionStep.indent) {
             duckCoachHint.value = `${firstWrong + 1}번째 블록의 들여쓰기를 확인해보꽥!`;
        }
    }
  }
  
  goToNextStep();
};

const skipImplementation = () => {
  goToNextStep();
};

const handleRunPython = async () => {
    /* [2026-01-24] Pyodide 엔진을 활용한 실제 코드 실행 및 테스트 케이스 검증 로직 구현 */
    executionError.value = '';
    executionOutput.value = '';
    isRunPassed.value = false;
    duckCoachHint.value = '';

    const validation = currentQuest.value.validation?.execution;
    
    /* [2026-01-24] 사용자가 카드에 적힌 함수를 그대로 쓸 수 있도록 Mock 함수 주입 */
    let injectCode = "";
    const cards = currentQuest.value.cards || [];
    const seenFuncs = new Set();
    
    cards.forEach(card => {
        if (card.text_py && card.text_py.includes('(')) {
            const funcName = card.text_py.split('(')[0].trim().split(' ').pop();
            if (funcName && !seenFuncs.has(funcName)) {
                injectCode += `def ${funcName}(*args, **kwargs): return f"${funcName}_done"\n`;
                seenFuncs.add(funcName);
            }
        }
    });

    // 실행할 최종 코드: Mock 함수들 + 사용자 코드
    const finalCode = injectCode + "\n" + userCode.value;

    const result = await runPython(
        finalCode, 
        validation?.test_cases || [], 
        validation?.function_name || ""
    );

    // [2026-01-24] Parse structured test results from stdout
    testResults.value = [];
    let passCount = 0;

    if (result.output) {
        const lines = result.output.split('\n');
        lines.forEach(line => {
            if (line.startsWith('TEST_CASE|')) {
                const parts = line.split('|');
                const passed = parts[3] === 'True';
                if (passed) passCount++;
                testResults.value.push({
                    input: parts[1],
                    output: parts[2],
                    passed: passed
                });
            }
        });
    }

    if (testResults.value.length > 0) {
        accuracy.value = Math.round((passCount / testResults.value.length) * 100);
    } else {
        accuracy.value = 0;
    }

    if (result.success) {
        const allPassed = testResults.value.length === 0 || testResults.value.every(r => r.passed);
        executionOutput.value = result.output.split('\n').filter(l => !l.startsWith('TEST_CASE|')).join('\n');
        isRunPassed.value = allPassed;
        
        if (allPassed) {
            judgeStatus.value = 'ACCEPTED';
            judgeMessage.value = "와! 완벽하꽥! 모든 테스트 케이스를 통과했어!";
        } else {
            judgeStatus.value = 'WRONG ANSWER';
            judgeMessage.value = "음... 일부 결과가 예상과 다르꽥. 다시 확인해보자꽥!";
        }
    } else {
        executionError.value = result.error;
        executionOutput.value = result.output;
        judgeStatus.value = 'RUNTIME ERROR';
        
        // 덕 코치 에러 피드백 연결 (Module C)
        if (result.error.includes("NameError")) {
            judgeMessage.value = "변수 선언을 깜빡한 것 같아꽥! 정의되지 않은 이름을 쓰고 있진 않은지 확인해보꽥!";
        } else if (result.error.includes("IndentationError")) {
            judgeMessage.value = "파이썬은 들여쓰기가 정말 중요하꽥! 줄 맞춤을 다시 확인해보꽥!";
            judgeStatus.value = 'SYNTAX ERROR';
        } else if (result.error.includes("AssertionError")) {
            judgeMessage.value = "결과값이 예상과 다르꽥! 논리나 계산 과정을 다시 검토해보꽥!";
            judgeStatus.value = 'WRONG ANSWER';
        } else {
            judgeMessage.value = "코드를 실행하다 넘어져버렸어꽥! 에러 메시지를 보고 같이 고쳐보자꽥.";
        }
    }
    
    if (isRunPassed.value) {
        setTimeout(() => {
            goToNextStep();
        }, 3000);
    }
};

const retry = () => {
  currentStepIndex.value = 1; // Go back to pseudo code step
};

onMounted(() => {
  initGame();
  initPyodide();
});
</script>

<style scoped>
.logic-mirror-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.logic-mirror-modal-container {
  position: relative;
  width: 100%;
  max-width: 1600px;
  height: 95vh;
  background: #0d1117;
  border-radius: 1.5rem;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
}

.modal-close-btn {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10010;
  transition: all 0.3s;
}

.modal-close-btn:hover {
  background: #ff4b4b;
  transform: rotate(90deg);
}

.loading-screen {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logic-mirror-pipeline {
  flex: 1;
  padding: 1.5rem 2rem;
  overflow-y: auto;
}

.pipeline-progress {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 1rem;
  padding: 1rem 1.5rem;
  margin-bottom: 1.5rem;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  position: relative;
}

.progress-steps::before {
  content: '';
  position: absolute;
  top: 20px;
  left: 0;
  right: 0;
  height: 2px;
  background: rgba(255, 255, 255, 0.1);
  z-index: 0;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  z-index: 1;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 700;
  transition: all 0.3s ease;
}

.progress-step.active .step-number {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  color: white;
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
}

.progress-step.completed .step-number {
  background: #4ade80;
  border-color: #4ade80;
  color: white;
}

.step-number {
  width: 32px;
  height: 32px;
  font-size: 0.8rem;
}

.step-label {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.85rem;
  font-weight: 600;
}

.progress-step.active .step-label {
  color: white;
}

.pipeline-step {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.step-container {
  max-width: 1400px;
  margin: 0 auto;
}

/* Problem Step */
.problem-header {
  display: flex;
  gap: 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  padding: 1.5rem 2rem;
  border-radius: 1rem;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.problem-emoji {
  font-size: 3rem;
}

.problem-info {
  flex: 1;
}

.problem-title {
  color: white;
  font-size: 1.8rem;
  font-weight: 800;
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.quest-num-label {
  background: #ffeb3b;
  color: #1a1f2e;
  padding: 0.2rem 0.6rem;
  border-radius: 0.5rem;
  font-size: 1.2rem;
  font-weight: 900;
  box-shadow: 0 0 10px rgba(255, 235, 59, 0.5);
}

.problem-description {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
  line-height: 1.5;
  margin: 0 0 0.75rem 0;
}

.problem-meta {
  display: flex;
  gap: 0.75rem;
}

.logic-type,
.level-badge {
  background: rgba(102, 126, 234, 0.3);
  color: #a5b4fc;
  padding: 0.35rem 0.75rem;
  border-radius: 0.75rem;
  font-size: 0.8rem;
  font-weight: 700;
}

.level-badge {
  background: rgba(255, 215, 0, 0.3);
  color: #ffd700;
}

.examples-box {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.examples-box h3 {
  color: white;
  margin: 0 0 1rem 0;
}

.examples-box pre {
  color: rgba(255, 255, 255, 0.8);
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  margin: 0;
}

.interviewer-intro {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

/* [2026-01-24] 덕 코칭 아바타(노란 영역) 크기를 60px에서 100px로 확대하고 시인성 개선을 위해 border 및 shadow 추가 */
.interviewer-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
  border: 3px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.duck-coach-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.05);
}

.interviewer-bubble {
  flex: 1;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 1rem;
  padding: 1.5rem;
}

.interviewer-label {
  background: rgba(102, 126, 234, 0.3);
  color: #a5b4fc;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 700;
  display: inline-block;
  margin-bottom: 0.75rem;
}

.interviewer-bubble p {
  color: white;
  font-size: 1rem;
  line-height: 1.5;
  margin: 0;
}

.next-step-btn,
.submit-btn,
.confirm-btn,
.next-quest-btn,
.complete-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  padding: 1.25rem 2rem;
  border-radius: 0.75rem;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  width: 100%;
}

.next-step-btn:hover,
.submit-btn:hover,
.confirm-btn:hover,
.next-quest-btn:hover,
.complete-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.4);
}

/* Pseudo Code Step */
.step-title {
  color: white;
  font-size: 1.5rem;
  font-weight: 800;
  margin: 0 0 0.25rem 0;
}

.step-subtitle {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
  margin: 0 0 1.5rem 0;
}

.pseudocode-layout {
  display: grid;
  grid-template-columns: 350px 450px 1fr; /* [2026-01-24] 3단 레이아웃으로 확대 */
  gap: 1.5rem;
  align-items: stretch;
}

.flex-column {
  display: flex;
  flex-direction: column;
}

.card-deck-section,
.drop-zone-section {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-title {
  color: white;
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0 0 1.5rem 0;
}

.cards-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 450px;
  overflow-y: auto;
}

.action-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  padding: 0.75rem;
  display: flex;
  gap: 0.75rem;
  cursor: grab;
  transition: all 0.3s ease;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.action-card:active {
  cursor: grabbing;
}

.card-blue { border-left: 4px solid #60a5fa; }
.card-purple { border-left: 4px solid #a78bfa; }
.card-green { border-left: 4px solid #4ade80; }
.card-orange { border-left: 4px solid #fb923c; }
.card-red { border-left: 4px solid #f87171; }
.card-pink { border-left: 4px solid #f472b6; }

.card-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.card-content {
  flex: 1;
}

.card-text {
  color: white;
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 0.25rem;
}

.card-code {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.75rem;
  font-family: 'Courier New', monospace;
}

.drop-zone {
  min-height: 400px;
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  transition: all 0.3s ease;
}

.drop-zone.drag-over {
  border-color: #60a5fa;
  background: rgba(96, 165, 250, 0.1);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 350px;
  gap: 0.75rem;
}

.empty-icon {
  font-size: 4rem;
  opacity: 0.3;
}

.empty-state p {
  color: rgba(255, 255, 255, 0.4);
  font-size: 1rem;
}

.sequence-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.sequence-card {
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  padding: 1rem;
  display: flex;
  gap: 0.75rem;
  align-items: center;
  animation: slideIn 0.3s ease;
}

.sequence-card.shake {
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
  border-color: #ff4b4b !important;
  background: rgba(255, 75, 75, 0.1) !important;
}

@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.seq-number {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

.remove-btn,
.clear-btn {
  background: rgba(248, 113, 113, 0.2);
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: #f87171;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.remove-btn:hover,
.clear-btn:hover {
  background: rgba(248, 113, 113, 0.3);
}

.remove-btn {
  flex-shrink: 0;
}

/* Visualization Section [2026-01-24] */
.visualization-section {
  background: rgba(15, 15, 20, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1.2rem;
  padding: 1.8rem;
  display: flex;
  flex-direction: column;
  min-height: 500px;
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.3);
}

.mermaid-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
  padding: 1rem;
}

.vis-empty-state {
  color: rgba(255, 255, 255, 0.2);
  font-style: italic;
  font-size: 0.95rem;
  text-align: center;
}

/* Mermaid SVG Style Overrides */
:deep(.mermaid-container svg) {
  max-width: 100%;
  height: auto;
  filter: drop-shadow(0 5px 15px rgba(0, 0, 0, 0.4));
}

/* Pre-submission Query */
.submitted-code-box {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 2rem;
}

.submitted-code-box h3 {
  color: white;
  margin: 0 0 1rem 0;
}

.code-preview {
  background: #0d1117;
  border-radius: 0.5rem;
  padding: 1.5rem;
  font-family: 'Courier New', monospace;
}

.code-line {
  display: flex;
  gap: 1rem;
  color: white;
  font-size: 0.95rem;
  line-height: 1.8;
}

.line-number {
  color: rgba(255, 255, 255, 0.3);
  min-width: 30px;
  text-align: right;
}

.line-code {
  flex: 1;
}

.interviewer-questions {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.question-bubble {
  flex: 1;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 1rem;
  padding: 1.5rem;
}

.question-text {
  color: white;
  font-size: 1.1rem;
  margin: 0 0 1.5rem 0;
}

.answer-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.option-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  color: white;
  padding: 1rem;
  border-radius: 0.5rem;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s ease;
}

.option-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}

.option-btn.selected {
  background: rgba(102, 126, 234, 0.3);
  border-color: #667eea;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

.back-btn,
.skip-btn,
.retry-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  padding: 1rem 1.5rem;
  border-radius: 0.75rem;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
}

.back-btn:hover,
.skip-btn:hover,
.retry-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
  color: white;
  border-color: rgba(255, 255, 255, 0.3);
}

.confirm-btn {
  flex: 2;
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Implementation Step */
.result-header {
  display: flex;
  gap: 2rem;
  padding: 2rem;
  border-radius: 1rem;
  margin-bottom: 2rem;
}

.result-header.success {
  background: rgba(74, 222, 128, 0.1);
  border: 2px solid #4ade80;
}

.result-header.failure {
  background: rgba(251, 146, 60, 0.1);
  border: 2px solid #fb923c;
}

.result-icon {
  font-size: 4rem;
}

.result-content h2 {
  color: white;
  font-size: 1.75rem;
  margin: 0 0 0.5rem 0;
}

.hint-text {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
  margin: 0;
}

.implementation-section {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 2rem;
}

.implementation-section h3 {
  color: white;
  margin: 0 0 0.5rem 0;
}

.section-desc {
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 1.5rem 0;
}

.code-editor.monaco-wrapper {
  background: #1e1e1e;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 2rem;
  height: 350px; /* Fixed height for Monaco */
  box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.code-editor.monaco-wrapper:focus-within {
  border-color: #6366f1;
  box-shadow: 0 0 15px rgba(99, 102, 241, 0.2);
}

.professional-editor {
  width: 100%;
  height: 100%;
}

.editor-header {
  background: rgba(255, 255, 255, 0.05);
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
}

/* Old textarea removed in favor of Monaco */

.implementation-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.left-actions {
  display: flex;
  gap: 1rem;
  flex: 2;
}

.hint-btn {
  background: rgba(255, 184, 0, 0.08);
  color: #FFB800;
  border: 1px solid rgba(255, 184, 0, 0.2);
  padding: 1rem 2rem;
  border-radius: 0.75rem;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  flex: 1;
}

.hint-btn:hover {
  background: rgba(255, 184, 0, 0.15);
  border-color: rgba(255, 184, 0, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(255, 184, 0, 0.1);
}

.hint-overlay-box {
  margin-top: 2rem;
  background: rgba(15, 15, 20, 0.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 184, 0, 0.3);
  border-left: 5px solid #FFB800;
  border-radius: 12px;
  overflow: hidden;
  animation: slideDown 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 0 0 20px rgba(255, 184, 0, 0.1);
}

.hint-header {
  background: rgba(255, 184, 0, 0.1);
  padding: 1rem 1.5rem;
  color: #FFB800;
  font-weight: 800;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  border-bottom: 1px solid rgba(255, 184, 0, 0.1);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.hint-status-dot {
  width: 10px;
  height: 10px;
  background: #FFB800;
  border-radius: 50%;
  box-shadow: 0 0 12px #FFB800;
}

.hint-content {
  padding: 1.8rem;
}

.hint-main-desc {
  color: white;
  margin-bottom: 1.2rem;
  font-size: 1.05rem;
  line-height: 1.6;
}

.hint-main-desc code {
  color: #FFB800;
  background: rgba(0, 0, 0, 0.4);
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 700;
}

.hint-divider {
  height: 1px;
  background: linear-gradient(90deg, rgba(255, 184, 0, 0.2), transparent);
  margin: 1.5rem 0;
}

.hint-sub-desc {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.95rem;
  margin-bottom: 1.2rem;
}

.hint-code-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.hint-code-list li {
  background: rgba(255, 255, 255, 0.04);
  padding: 0.9rem 1.2rem;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: transform 0.2s;
}

.hint-code-list li:hover {
  transform: translateX(5px);
  background: rgba(255, 255, 255, 0.06);
}

.card-icon {
  font-size: 1.4rem;
}

.hint-code-list code {
  color: #b6ff40;
  background: rgba(0, 0, 0, 0.3);
  padding: 4px 10px;
  border-radius: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.4);
}

.card-text-ko {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  margin-left: auto;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-15px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Test Results Table [2026-01-24] */
.test-results-container {
  margin-top: 1rem;
  overflow-x: auto;
}

.test-results-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  overflow: hidden;
}

.test-results-table th, 
.test-results-table td {
  padding: 0.6rem 1rem;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.test-results-table th {
  background: rgba(0, 0, 0, 0.2);
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
}

.test-results-table tr.pass {
  background: rgba(88, 204, 2, 0.05);
}

.test-results-table tr.fail {
  background: rgba(255, 75, 75, 0.05);
}

.test-results-table tr.pass td:last-child {
  color: #58cc02;
}

.test-results-table tr.fail td:last-child {
  color: #ff4b4b;
}

.test-results-table code {
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
}

.execution-feedback {
  margin-top: 1.5rem;
  animation: fadeIn 0.4s ease;
  background: rgba(10, 10, 15, 0.6);
  backdrop-filter: blur(10px);
  padding: 1.8rem;
  border-radius: 1.2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

/* Judge Status UI [2026-01-24] */
.judge-status-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.status-badge {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 900;
  letter-spacing: 1px;
  font-size: 0.9rem;
  text-transform: uppercase;
  background: rgba(255, 255, 255, 0.05); /* Default */
  color: rgba(255, 255, 255, 0.4);
}

.status-badge.ready {
  background: rgba(33, 150, 243, 0.2);
  color: #2196f3;
  border: 1px solid rgba(33, 150, 243, 0.3);
}

.judge-mini-badge {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 900;
  padding: 2px 6px;
  border-radius: 4px;
  background: #58cc02;
  color: white;
  margin-bottom: 0.4rem;
  letter-spacing: 0.5px;
}

.status-badge.accepted {
  background: rgba(88, 204, 2, 0.2);
  color: #58cc02;
  border: 1px solid rgba(88, 204, 2, 0.3);
}

.status-badge.wrong-answer {
  background: rgba(255, 75, 75, 0.2);
  color: #ff4b4b;
  border: 1px solid rgba(255, 75, 75, 0.3);
}

.status-badge.runtime-error,
.status-badge.syntax-error {
  background: rgba(255, 152, 0, 0.2);
  color: #ff9800;
  border: 1px solid rgba(255, 152, 0, 0.3);
}

.accuracy-info {
  text-align: right;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
}

.accuracy-info .percent {
  color: white;
  font-weight: bold;
}

.accuracy-bar {
  width: 120px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  margin-top: 4px;
}

.accuracy-fill {
  height: 100%;
  background: linear-gradient(90deg, #FFB800, #b6ff40);
  border-radius: 3px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.execution-msg {
  color: white;
  font-weight: 600;
  line-height: 1.6;
}

.execution-msg.error {
  color: #ff9e9e;
}

.stdout-box {
  background: rgba(0, 0, 0, 0.5);
  padding: 1rem;
  border-radius: 0.5rem;
  margin-top: 1rem;
  color: #a7f3d0;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  max-height: 150px;
  overflow-y: auto;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.run-btn {
  background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
  border: none;
  color: white;
  padding: 1rem 2rem;
  border-radius: 0.75rem;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.run-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(74, 222, 128, 0.3);
}

/* Follow-up Step */
.completion-header {
  text-align: center;
  margin-bottom: 3rem;
}

.completion-icon {
  font-size: 6rem;
  margin-bottom: 1rem;
}

.completion-title {
  color: white;
  font-size: 3rem;
  font-weight: 800;
  margin: 0;
}

.interviewer-followup {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.followup-bubble {
  flex: 1;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 1rem;
  padding: 1.5rem;
}

.followup-question {
  color: white;
  font-size: 1.2rem;
  line-height: 1.6;
  margin: 0;
}

/* [2026-01-24] 심화 평가 인터랙티브 요소 스타일 추가 */
.followup-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 2rem;
}

.followup-option-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  padding: 1.25rem 1.5rem;
  border-radius: 1rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: left;
  line-height: 1.4;
}

.followup-option-btn:hover {
  background: rgba(102, 126, 234, 0.15);
  border-color: #667eea;
  transform: translateZ(10px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

.followup-feedback-box {
  margin-top: 2rem;
  padding: 2rem;
  border-radius: 1.2rem;
  animation: fadeIn 0.4s ease;
  backdrop-filter: blur(10px);
}

.followup-feedback-box.pass {
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid rgba(74, 222, 128, 0.2);
}

.followup-feedback-box.fail {
  background: rgba(255, 75, 75, 0.1);
  border: 1px solid rgba(255, 75, 75, 0.2);
}

.feedback-status {
  font-weight: 900;
  font-size: 1.2rem;
  margin-bottom: 0.75rem;
}

.pass .feedback-status { color: #4ade80; }
.fail .feedback-status { color: #ff6b6b; }

.explanation-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  line-height: 1.7;
}

.re-answer-btn {
  margin-top: 1.25rem;
  background: #ff4b4b;
  border: none;
  color: white;
  padding: 0.6rem 1.2rem;
  border-radius: 0.75rem;
  cursor: pointer;
  font-weight: 700;
  font-size: 0.95rem;
  transition: all 0.2s;
}

.re-answer-btn:hover {
  background: #ff6b6b;
}

.learning-summary {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 2rem;
}

.learning-summary h3 {
  color: white;
  margin: 0 0 1rem 0;
}

.learning-points {
  list-style: none;
  padding: 0;
  margin: 0;
}

.learning-points li {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
  padding: 0.75rem 0;
  padding-left: 2rem;
  position: relative;
}

.learning-points li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #4ade80;
  font-weight: 700;
}

.navigation-buttons {
  display: flex;
  gap: 1rem;
}

@media (max-width: 1024px) {
  .pseudocode-layout {
    grid-template-columns: 1fr;
  }
}
</style>
