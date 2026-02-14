<template>
  <div class="code-flow-visualizer">
    <!-- 상단: 대조 영역 (의사코드 vs Python) -->
    <div class="comparison-area">
      <!-- Left: Input Pseudocode -->
      <div class="code-panel pseudocode-panel">
        <div class="panel-header">
          <span class="icon">📝</span>
          <span class="title">INPUT_LOGIC (PSEUDO CODE)</span>
        </div>
        <div class="code-content pre-wrap">{{ pseudocode }}</div>
      </div>

      <!-- Right: Generated Python -->
      <div class="code-panel python-panel">
        <div class="panel-header">
          <span class="icon">🐍</span>
          <span class="title">AI_IMPLEMENTATION (PYTHON)</span>
        </div>
        <div class="code-content">
          <pre class="python-code"><code>{{ pythonCode }}</code></pre>
        </div>
      </div>
    </div>

    <!-- 하단: 단계별 검증 영역 -->
    <div class="validation-area">
      <!-- 1단계: AI 어드바이스 (공통) -->
      <div class="advice-block">
        <div class="advice-header">
          <span class="icon">💡</span>
          <span class="title">AI ARCHITECT ADVICE</span>
          <span class="score-badge">LOGIC SCORE: {{ evaluationScore }}</span>
        </div>
        <p class="advice-text">{{ evaluationFeedback }}</p>
      </div>

      <!-- 2단계: 챌린지 영역 (MCQ 또는 서술형 Deep Dive) -->
      <div v-if="phase === 'PYTHON_VISUALIZATION' || phase === 'TAIL_QUESTION'" class="challenge-block mcq-section">
        <div class="challenge-header">
          <span class="badge">DEEP DIVE CHALLENGE</span>
          <h4 class="challenge-question">[{{ mcqData.context }}] {{ mcqData.question }}</h4>
        </div>
        
        <div class="options-grid">
          <button 
            v-for="(opt, idx) in mcqData.options" 
            :key="idx"
            class="option-btn"
            :class="{ 
              'selected': selectedIdx === idx,
              'correct': isMcqAnswered && (opt.is_correct || opt.correct),
              'wrong': isMcqAnswered && selectedIdx === idx && !(opt.is_correct || opt.correct)
            }"
            :disabled="isMcqAnswered"
            @click="handleMcqSelect(idx)"
          >
            <span class="option-label">{{ String.fromCharCode(65 + idx) }}</span>
            <span class="option-text">{{ opt.text }}</span>
          </button>
        </div>

        <!-- MCQ 답변 후 피드백 루프 -->
        <div v-if="isMcqAnswered" class="mcq-feedback-popup">
          <p :class="isCorrect ? 'text-success' : 'text-danger'">
            {{ isCorrect ? '🎯 정답입니다! 아키텍처 결함이 보완되었습니다.' : '⚠️ 오답입니다. 설계의 허점이 발견되었습니다.' }}
          </p>
          <div class="mcq-explanation" v-if="selectedIdx !== null">
            <span class="explanation-label">정답 및 해설:</span>
            {{ mcqData.options[selectedIdx].feedback || mcqData.options[selectedIdx].reason }}
          </div>
        </div>
      </div>

      <!-- 3단계: 실무 시나리오 Deep Dive (서술형) -->
      <div v-if="phase === 'DEEP_DIVE_DESCRIPTIVE'" class="challenge-block descriptive-section">
        <div class="challenge-header">
          <span class="badge scenario-badge">{{ assignedScenario?.axis }}의 축 챌린지</span>
          <h4 class="challenge-question">
            <strong>[시나리오: {{ assignedScenario?.title }}]</strong><br/>
            {{ assignedScenario?.question }}
          </h4>
        </div>

        <div class="descriptive-input-wrapper">
          <textarea 
            v-model="descriptiveAnswer"
            class="descriptive-textarea"
            placeholder="시나리오에 대한 해결책을 1~2문장의 자연어로 서술하세요..."
            :disabled="isDescriptionSubmitted"
          ></textarea>
          <div class="input-footer">
            <span class="char-count">{{ descriptiveAnswer.length }} / 200</span>
            <span class="guide-text">💡 힌트: {{ assignedScenario?.intent }}를 고려해 보세요.</span>
          </div>
        </div>
      </div>

      <!-- 하단 액션 버튼 -->
      <div class="action-footer">
        <button 
          v-if="!isDescriptionSubmitted"
          class="final-btn" 
          :disabled="!isPhaseReady"
          @click="handleNext"
        >
          {{ nextButtonText }} →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  phase: String,
  pseudocode: String,
  pythonCode: String,
  evaluationScore: Number,
  evaluationFeedback: String,
  mcqData: Object,           // { question, options, context }
  assignedScenario: Object,  // { title, question, intent, axis }
  isMcqAnswered: Boolean
});

const emit = defineEmits(['answer-mcq', 'submit-descriptive', 'next-phase']);

const selectedIdx = ref(null);
const descriptiveAnswer = ref("");
const isDescriptionSubmitted = ref(false);

const isCorrect = computed(() => {
  if (selectedIdx.value === null) return false;
  const opt = props.mcqData.options[selectedIdx.value];
  return opt?.is_correct || opt?.correct;
});

const isPhaseReady = computed(() => {
  if (props.phase === 'PYTHON_VISUALIZATION' || props.phase === 'TAIL_QUESTION') {
    return props.isMcqAnswered;
  }
  if (props.phase === 'DEEP_DIVE_DESCRIPTIVE') {
    return descriptiveAnswer.value.trim().length >= 10;
  }
  return true;
});

const nextButtonText = computed(() => {
  if (props.phase === 'PYTHON_VISUALIZATION' || props.phase === 'TAIL_QUESTION') return "DEEP DIVE 진입";
  if (props.phase === 'DEEP_DIVE_DESCRIPTIVE') return "최종 평가 리포트 생성";
  return "다음 단계";
});

const handleMcqSelect = (idx) => {
  if (props.isMcqAnswered) return;
  selectedIdx.value = idx;
  emit('answer-mcq', idx);
};

const handleNext = () => {
  if (props.phase === 'DEEP_DIVE_DESCRIPTIVE') {
    isDescriptionSubmitted.value = true;
    emit('submit-descriptive', descriptiveAnswer.value);
  } else {
    emit('next-phase');
  }
};
</script>

<style scoped>
.code-flow-visualizer {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  background: transparent;
  color: #f8fafc;
}

.comparison-area {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  padding: 1.5rem;
  min-height: 70vh;
}

.code-panel {
  background: rgba(30, 41, 59, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  padding: 0.75rem 1rem;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  color: #94a3b8;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.code-content {
  flex: 1;
  padding: 1.5rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 1rem; /* 폰트 크기 소폭 상향 */
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-all;
}

.python-code {
  color: #34d399;
}

.validation-area {
  background: #1e293b;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1.5rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.advice-block {
  background: rgba(15, 23, 42, 0.5);
  padding: 1rem 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
}

.advice-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.score-badge {
  margin-left: auto;
  font-size: 0.75rem;
  font-weight: 800;
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
}

.challenge-block {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.challenge-header .badge {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 900;
  padding: 2px 8px;
  background: #f472b6;
  color: white;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.scenario-badge {
  background: #fbbf24 !important;
}

.challenge-question {
  font-size: 1.1rem;
  font-weight: 700;
  line-height: 1.4;
  color: #e2e8f0;
}

.options-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.option-btn {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.option-btn:hover:not(:disabled) {
  background: rgba(15, 23, 42, 0.9);
  border-color: #3b82f6;
}

.option-btn.selected {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
}

.option-btn.correct {
  border-color: #10b981 !important;
  background: rgba(16, 185, 129, 0.1) !important;
}

.option-btn.wrong {
  border-color: #ef4444 !important;
  background: rgba(239, 68, 68, 0.1) !important;
}

.option-label {
  width: 28px;
  height: 28px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.8rem;
  flex-shrink: 0;
}

.descriptive-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.descriptive-textarea {
  width: 100%;
  height: 100px;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 1rem;
  color: white;
  font-size: 1rem;
  resize: none;
  outline: none;
}

.descriptive-textarea:focus {
  border-color: #fbbf24;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #94a3b8;
}

.action-footer {
  margin-top: 0.5rem;
  display: flex;
  justify-content: center;
}

.final-btn {
  padding: 1rem 3rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 99px;
  font-weight: 800;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
}

.final-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  background: #1d4ed8;
}

.final-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}

.mcq-feedback-popup {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1.2rem;
  border-radius: 12px;
  animation: fadeIn 0.3s ease;
}

.mcq-explanation {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed rgba(255, 255, 255, 0.1);
  color: #94a3b8;
  font-size: 0.9rem;
  line-height: 1.5;
}

.explanation-label {
  display: block;
  font-weight: 800;
  color: #60a5fa;
  font-size: 0.75rem;
  margin-bottom: 4px;
}

.text-success { color: #10b981; }
.text-danger { color: #ef4444; }
.pre-wrap { white-space: pre-wrap; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
