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
        <!-- [복구 작전 모드] 라면 현재 진행 상황 표시 -->
        <div v-if="isBlueprintMode" class="code-content pre-wrap reconstruction-list">
           <div v-for="(s, idx) in blueprintSteps" :key="idx" 
                class="recon-step" :class="{ 'active': currentStepIdx === idx, 'completed': currentStepIdx > idx }">
              <span class="step-num">{{ idx + 1 }}</span>
              <span class="step-pseudo">{{ currentStepIdx > idx ? (userRestoredSteps[idx] || s.pseudo) : (currentStepIdx === idx ? '?? 설계 진행 중 ??' : '...') }}</span>
           </div>
        </div>
        <div v-else class="code-content pre-wrap">{{ pseudocode }}</div>
      </div>

      <!-- Right: Generated Python -->
      <div class="code-panel python-panel">
        <div class="panel-header">
          <span class="icon">🐍</span>
          <span class="title">AI_IMPLEMENTATION (PYTHON)</span>
        </div>
        <div class="code-content">
          <!-- [복구 작전 모드] 현재 맞춘 단계까지 하이라이트 -->
          <div v-if="isBlueprintMode" class="blueprint-python-viewer">
             <div v-for="(s, idx) in blueprintSteps" :key="idx" 
                  class="py-step-block" :class="{ 'highlight': currentStepIdx === idx, 'faded': currentStepIdx < idx }">
                <pre><code>{{ s.python }}</code></pre>
             </div>
          </div>
          <pre v-else class="python-code"><code>{{ pythonCode }}</code></pre>
        </div>
      </div>
    </div>

    <!-- 하단: 단계별 검증 영역 -->
    <div class="validation-area">
      <div class="advice-block" :class="{ 'is-recovery-complete': isBlueprintComplete }">
        <div class="advice-header">
          <span class="icon">💡</span>
          <span class="title">{{ isBlueprintComplete ? 'SYSTEM RECOVERED' : 'AI ARCHITECT ADVICE' }}</span>
        </div>
        <p class="advice-text">
            <template v-if="isBlueprintComplete">
              성공적으로 아키텍처를 복구했습니다! 당신은 이제 올바른 설계 원칙을 이해한 아키텍트입니다.
            </template>
            <template v-else-if="isLowEffort && pythonCode">
              청사진(Blueprint)을 통해 올바른 Python 구현을 확인하세요. 아래 문제를 풀어 설계 원리를 완성하세요!
            </template>
            <template v-else>
              {{ evaluationFeedback }}
            </template>
        </p>
      </div>

      <!-- 2-1단계: [복구 작전] 매칭 영역 -->
      <div v-if="isBlueprintMode && !isBlueprintComplete" class="challenge-block blueprint-section recovery-action">
        <div class="challenge-header">
           <div class="recovery-guide-banner">
              <span class="guide-icon">🛠️</span>
              <div class="guide-text">
                <strong>아키텍처 복구 작전:</strong> 하이라이트된 파이썬 코드에 알맞은 설계 의도(의사코드)를 <span class="highlight-text">직접 입력</span>하거나 아래에서 <span class="highlight-text">선택</span>하세요.
              </div>
           </div>
        </div>

        <div class="recovery-interaction-hub">
           <!-- [NEW] 핵심 키워드 가이드 영역 -->
           <div class="keyword-hint-area">
              <span class="hint-label">🔑 핵심 키워드:</span>
              <div class="keyword-tags">
                 <span v-for="k in currentStepKeywords" :key="k" class="keyword-tag">{{ k }}</span>
              </div>
           </div>

           <!-- [NEW] 수동 입력 모드 -->
           <div class="manual-input-zone">
              <input 
                v-model="manualInput" 
                class="recovery-input" 
                :class="{ 'error-shake': showInputError }"
                placeholder="키워드를 활용해 설계 의도를 작성해 보세요..."
                @keyup.enter="handleManualSubmit"
              />
              <button class="btn-verify" @click="handleManualSubmit">확인</button>
           </div>
           <div v-if="showInputError" class="input-error-msg animate-fadeIn">
              입력하신 내용에 핵심 키워드가 부족합니다. 위 힌트를 참고해 보세요!
           </div>

           <div class="divider"><span>OR SELECT BELOW</span></div>
           <div class="options-grid">
             <button 
               v-for="(opt, idx) in blueprintOptions" 
               :key="idx"
               class="option-btn recovery-opt"
               :class="{ 
                 'selected': selectedIdx === idx,
                 'correct': isStepAnswered && opt.isCorrect,
                 'wrong': isStepAnswered && selectedIdx === idx && !opt.isCorrect
               }"
               :disabled="isStepAnswered"
               @click="handleStepPick(idx)"
             >
               <span class="option-label">{{ String.fromCharCode(65 + idx) }}</span>
               <span class="option-text">{{ opt.pseudo }}</span>
             </button>
           </div>
        </div>
      </div>

      <!-- 2-2단계: 일반 MCQ 또는 완료 후 노출 -->
      <div v-else-if="(phase === 'PYTHON_VISUALIZATION' || phase === 'TAIL_QUESTION') && !isBlueprintMode" class="challenge-block mcq-section">
        <div class="challenge-header">
          <span class="badge">DEEP DIVE CHALLENGE</span>
          <h4 class="challenge-question">[{{ mcqData?.context || '검증' }}] {{ mcqData?.question || '데이터를 분석할 수 없습니다.' }}</h4>
        </div>
        
        <div class="options-grid">
          <button 
            v-for="(opt, idx) in mcqData.options" 
            :key="idx"
            class="option-btn"
            :class="{ 
              'selected': selectedIdx === idx,
              'correct': isMcqAnswered && selectedIdx === idx && (opt.is_correct || opt.correct),
              'wrong': isMcqAnswered && selectedIdx === idx && !(opt.is_correct || opt.correct)
            }"
            :disabled="isMcqAnswered"
            @click="handleMcqSelect(idx)"
          >
            <div class="option-content-wrapper">
              <div class="option-main">
                <span class="option-label">{{ String.fromCharCode(65 + idx) }}</span>
                <span class="option-text">{{ opt.text }}</span>
              </div>
              <div v-if="isMcqAnswered && selectedIdx === idx" class="option-feedback animate-fadeIn">
                {{ opt.feedback || '설계 원칙에 따른 분석 결과입니다.' }}
              </div>
            </div>
          </button>
        </div>
      </div>

      <div v-if="isBlueprintComplete" class="mcq-feedback-popup">
          <p class="text-success">🎯 아키텍처 복구 작전 완료! 설계 원칙을 완전히 이해했습니다.</p>
      </div>
      <div v-else-if="isMcqAnswered" class="mcq-feedback-popup">
          <p v-if="selectedMcqIsCorrect" class="text-success animate-fadeIn">🎯 정답입니다! 다음 단계로 진행하세요.</p>
          <div v-else class="incorrect-feedback-with-retry animate-shake">
             <p class="text-error">❌ 오답입니다. 설계적 결함이 감지되었습니다. (피드백을 확인하세요)</p>
             <button class="btn-retry-mcq-action" @click="handleMcqRetry">아키텍처 다시 보완하기</button>
          </div>
      </div>

      <div v-if="phase === 'DEEP_DIVE_DESCRIPTIVE'" class="challenge-block descriptive-section">
        <div class="challenge-header">
          <span class="badge scenario-badge">{{ assignedScenario?.axis }}의 축 챌린지</span>
          <div class="scenario-intent-guide">
            <span class="guide-label">🎯 설계 의도:</span>
            <span class="guide-text">{{ assignedScenario?.intent }}</span>
          </div>
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
        </div>

        <!-- [추가] 모범 답안 노출 영역 -->
        <div v-if="isDescriptionSubmitted" class="model-answer-block animate-fadeIn">
            <div class="model-answer-header">
                <span class="model-icon">🏆</span>
                <strong>AI 아키텍트의 모범 답안</strong>
            </div>
            <div class="model-answer-content">
                <p class="model-answer-text">{{ assignedScenario?.modelAnswer }}</p>
                
                <div v-if="assignedScenario?.scoringKeywords?.length" class="key-points-zone">
                    <span class="key-label">💡 엔지니어링 핵심 포인트:</span>
                    <div class="key-tags">
                        <span v-for="tag in assignedScenario.scoringKeywords" :key="tag" class="key-tag">#{{ tag }}</span>
                    </div>
                </div>
            </div>
            <div class="model-answer-tip">
                * 실제 평가 점수는 리포트 생성 시 5차원 메트릭으로 상세 분석됩니다.
            </div>
        </div>
      </div>
        <div class="action-footer">
          <button 
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
import { ref, computed, watch } from 'vue';

const props = defineProps({
  phase: String,
  pseudocode: String,
  pythonCode: String,
  evaluationScore: Number,
  evaluationFeedback: String,
  isLowEffort: Boolean,   // is_low_effort 여부 (advice 문구 분기용)
  mcqData: Object,
  blueprintSteps: Array,
  assignedScenario: Object,
  isMcqAnswered: Boolean
});

const emit = defineEmits(['answer-mcq', 'retry-mcq', 'submit-descriptive', 'next-phase', 'blueprint-complete']);

const currentStepIdx = ref(0);
const selectedIdx = ref(null);
const isStepAnswered = ref(false);
const descriptiveAnswer = ref("");
const isDescriptionSubmitted = ref(false);
const manualInput = ref("");
const showInputError = ref(false);
const userRestoredSteps = ref([]); // 사용자가 직접 타이핑하거나 선택한 문장 저장

// 청사진 완료 방식 추적: 'keyword'(주관식 입력) | 'block'(객관식 선택)
// 각 스텝에서 한 번이라도 block 선택을 했으면 'block'으로 기록
const blueprintCompletionMode = ref('keyword');

const isBlueprintMode = computed(() => props.blueprintSteps && props.blueprintSteps.length > 0);
const isBlueprintComplete = computed(() => isBlueprintMode.value && currentStepIdx.value >= props.blueprintSteps.length);

const currentStepKeywords = computed(() => {
    if (!isBlueprintMode.value || isBlueprintComplete.value) return [];
    return props.blueprintSteps[currentStepIdx.value]?.keywords || [];
});

// 청사진 모드용 랜덤 옵션 생성 (정답 + 오답 섞기)
const blueprintOptions = computed(() => {
  if (!isBlueprintMode.value || isBlueprintComplete.value) return [];
  const current = props.blueprintSteps[currentStepIdx.value];
  if (!current) return [];
  const others = props.blueprintSteps.filter((_, i) => i !== currentStepIdx.value).map(s => s.pseudo);
  
  const options = [{ pseudo: current.pseudo, isCorrect: true }];
  others.slice(0, 3).forEach(p => options.push({ pseudo: p, isCorrect: false }));
  
  return options.sort(() => Math.random() - 0.5);
});

const isPhaseReady = computed(() => {
  if (isBlueprintMode.value) return isBlueprintComplete.value;
  if (props.phase === 'PYTHON_VISUALIZATION' || props.phase === 'TAIL_QUESTION') return props.isMcqAnswered;
  if (props.phase === 'DEEP_DIVE_DESCRIPTIVE') return descriptiveAnswer.value.trim().length >= 10;
  return true;
});

const selectedMcqIsCorrect = computed(() => {
  if (selectedIdx.value === null || !props.mcqData?.options) return false;
  const opt = props.mcqData.options[selectedIdx.value];
  return opt?.is_correct || opt?.correct;
});

const nextButtonText = computed(() => {
  if (isBlueprintMode.value && !isBlueprintComplete.value) return "설계 복구 진행 중";
  if (props.phase === 'PYTHON_VISUALIZATION' || props.phase === 'TAIL_QUESTION') return "DEEP DIVE 진입";
  if (props.phase === 'DEEP_DIVE_DESCRIPTIVE') {
    return isDescriptionSubmitted.value ? "최종 리포트 확인하기" : "답안 제출 및 분석";
  }
  return "다음 단계";
});

const handleStepPick = (idx) => {
  if (isStepAnswered.value) return;
  selectedIdx.value = idx;
  const opt = blueprintOptions.value[idx];

  if (opt.isCorrect) {
    userRestoredSteps.value[currentStepIdx.value] = opt.pseudo;
    // 객관식 선택 사용 → 'block' 모드로 기록
    blueprintCompletionMode.value = 'block';
    proceedToNextStep();
  } else {
    isStepAnswered.value = true;
    setTimeout(() => {
      isStepAnswered.value = false;
      selectedIdx.value = null;
    }, 1500);
  }
};

const handleManualSubmit = () => {
    if (!manualInput.value.trim() || isStepAnswered.value) return;

    const current = props.blueprintSteps[currentStepIdx.value];
    const targetKeywords = current.keywords || [];
    const matchCount = targetKeywords.filter(k => manualInput.value.includes(k)).length;

    if (matchCount >= 1 || manualInput.value.length > 30) {
        userRestoredSteps.value[currentStepIdx.value] = manualInput.value;
        // 주관식 입력 사용 → 이미 block이 등록된 경우는 유지, 아니면 keyword
        // (keyword가 기본값이라 별도 승격 없음)
        proceedToNextStep();
        showInputError.value = false;
    } else {
        showInputError.value = true;
        setTimeout(() => { showInputError.value = false; }, 3000);
    }
};

const proceedToNextStep = () => {
    isStepAnswered.value = true;
    setTimeout(() => {
        currentStepIdx.value++;
        isStepAnswered.value = false;
        selectedIdx.value = null;
        manualInput.value = "";

        // 모든 스텝 완료 시 emit으로 부모에 알림
        if (currentStepIdx.value >= (props.blueprintSteps?.length || 0)) {
            emit('blueprint-complete', blueprintCompletionMode.value);
        }
    }, 800);
};

const handleMcqSelect = (idx) => {
    if (props.isMcqAnswered) return;
    selectedIdx.value = idx;
    emit('answer-mcq', idx);
};

const handleMcqRetry = () => {
    selectedIdx.value = null;
    emit('retry-mcq');
};

const handleNext = () => {
    if (props.phase === 'DEEP_DIVE_DESCRIPTIVE') {
        if (!isDescriptionSubmitted.value) {
            isDescriptionSubmitted.value = true;
            emit('submit-descriptive', descriptiveAnswer.value);
        } else {
            emit('next-phase');
        }
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
  flex-shrink: 0; /* 상단 고정 */
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  padding: 1.5rem;
  min-height: 55vh; /* [2026-02-14] 하단 버튼 노출 확보를 위해 하향 */
}

/* [2026-02-14] 복구 작전 전용 UI 스타일 */
.recovery-guide-banner {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 8px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.guide-icon { font-size: 1.5rem; }
.guide-text { font-size: 0.95rem; line-height: 1.5; color: #bfdbfe; }
.highlight-text { color: #60a5fa; font-weight: 800; text-decoration: underline; }

.recovery-interaction-hub {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.manual-input-zone {
  display: flex;
  gap: 0.75rem;
}

.recovery-input {
  flex: 1;
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  color: white;
  font-size: 0.95rem;
}

.btn-verify {
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0 1.5rem;
  font-weight: 700;
  cursor: pointer;
}

/* [2026-02-14] 키워드 힌트 스타일 */
.keyword-hint-area {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.hint-label {
  font-size: 0.8rem;
  color: #94a3b8;
  font-weight: 700;
}

.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.keyword-tag {
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.4);
  color: #93c5fd;
  padding: 2px 10px;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 600;
}

.input-error-msg {
  color: #f87171;
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

.error-shake {
  animation: shake 0.4s ease;
  border-color: #ef4444 !important;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  font-size: 0.7rem;
  color: #64748b;
  font-weight: 900;
  margin: 0.5rem 0;
}

.divider::before, .divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.divider span { padding: 0 10px; }

.recovery-opt {
  padding: 0.85rem !important;
  font-size: 0.9rem !important;
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
  white-space: pre-wrap;
  word-break: break-all;
  overflow-x: hidden;
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
  transition: all 0.5s ease;
}

.advice-block.is-recovery-complete {
  border-left-color: #10b981;
  background: rgba(16, 185, 129, 0.1);
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

.scenario-intent-guide {
  background: rgba(30, 41, 59, 0.4);
  border: 1px dashed rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
}

.guide-label {
  font-size: 0.8rem;
  font-weight: 800;
  color: #fbbf24;
  margin-right: 0.5rem;
}

.guide-text {
  font-size: 0.85rem;
  color: #cad1d9;
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

/* [2026-02-14] 모범 답안 스타일 */
.model-answer-block {
  background: rgba(251, 191, 36, 0.08);
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 12px;
  padding: 1.25rem;
  margin-top: 1rem;
  animation: fadeIn 0.5s ease-out;
}

.model-answer-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #fbbf24;
  font-size: 0.95rem;
  margin-bottom: 0.75rem;
}

.model-answer-text {
  color: #f1f5f9;
  font-size: 0.95rem;
  line-height: 1.6;
  white-space: pre-wrap;
}

.model-answer-tip {
  margin-top: 0.75rem;
  font-size: 0.75rem;
  color: #94a3b8;
  font-style: italic;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
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

/* [청사진 복구 작전 전용 스타일] */
.reconstruction-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.recon-step {
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  display: flex;
  gap: 1rem;
  transition: all 0.3s ease;
  opacity: 0.5;
}

.recon-step.active {
  opacity: 1;
  background: rgba(59, 130, 246, 0.1);
  border-color: #3b82f6;
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.2);
}

.recon-step.completed {
  opacity: 1;
  border-color: #10b981;
  color: #10b981;
}

.step-num {
  font-weight: 800;
  color: #64748b;
}

.recon-step.completed .step-num {
  color: #10b981;
}

.blueprint-python-viewer {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.py-step-block {
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.4s ease;
  border: 1px solid transparent;
}

.py-step-block.highlight {
  background: rgba(52, 211, 153, 0.15);
  border-color: rgba(52, 211, 153, 0.4);
  transform: scale(1.02);
  z-index: 10;
}

.py-step-block.faded {
  opacity: 0.2;
  filter: blur(1px);
}

.blueprint-badge {
  background: #3b82f6 !important;
}

.mcq-feedback-popup {
  background: rgba(15, 23, 42, 0.82);
  border: 1px solid rgba(16, 185, 129, 0.3);
  padding: 1.2rem;
  border-radius: 12px;
  text-align: center;
  animation: fadeIn 0.4s ease-out;
}

.text-success { color: #10b981; font-weight: 800; }
.text-error { color: #ef4444; font-weight: 800; }
.animate-shake { animation: shake 0.4s ease-in-out; }

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-8px); }
  75% { transform: translateX(8px); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.incorrect-feedback-with-retry {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.btn-retry-mcq-action {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid #ef4444;
  color: #ef4444;
  padding: 8px 20px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-retry-mcq-action:hover {
  background: #ef4444;
  color: white;
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
}

/* [NEW] MCQ 피드백 스타일 */
.option-content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
  text-align: left;
}

.option-main {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.option-feedback {
  font-size: 0.8rem;
  color: #94a3b8;
  padding-left: 2rem;
  line-height: 1.5;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 0.5rem;
}

.option-btn.correct .option-feedback {
  color: #a7f3d0;
}

.option-btn.wrong .option-feedback {
  color: #fecaca;
}

/* [NEW] 서술형 모범 답안 강화 스타일 */
.model-answer-block {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 1rem;
}

.model-answer-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  color: #60a5fa;
  font-size: 1rem;
}

.model-answer-text {
  font-size: 1rem;
  line-height: 1.6;
  color: #f1f5f9;
  margin-bottom: 1.25rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
}

.key-points-zone {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.key-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #94a3b8;
}

.key-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.key-tag {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.model-answer-tip {
  margin-top: 1.5rem;
  font-size: 0.75rem;
  color: #64748b;
  font-style: italic;
}

.model-answer-tip {
  margin-top: 1.5rem;
  font-size: 0.75rem;
  color: #64748b;
  font-style: italic;
}

.action-footer {
  margin-top: 1rem;
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
  background: #334155;
  color: #64748b;
  cursor: not-allowed;
  box-shadow: none;
}
</style>
