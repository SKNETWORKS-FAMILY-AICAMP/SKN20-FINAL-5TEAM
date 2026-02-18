<template>
  <div class="code-flow-visualizer">
    <!-- ?곷떒: ?議??곸뿭 (?섏궗肄붾뱶 vs Python) -->
    <div class="comparison-area">
      <!-- Left: Input Pseudocode -->
      <div class="code-panel pseudocode-panel">
        <div class="panel-header">
          <span class="icon">?뱷</span>
          <span class="title">INPUT_LOGIC (PSEUDO CODE)</span>
        </div>
        <!-- [蹂듦뎄 ?묒쟾 紐⑤뱶] ?쇰㈃ ?꾩옱 吏꾪뻾 ?곹솴 ?쒖떆 -->
        <div v-if="isBlueprintMode" class="code-content pre-wrap reconstruction-list">
           <div v-for="(s, idx) in blueprintSteps" :key="idx" 
                class="recon-step" :class="{ 'active': currentStepIdx === idx, 'completed': currentStepIdx > idx }">
              <span class="step-num">{{ idx + 1 }}</span>
              <span class="step-pseudo">{{ currentStepIdx > idx ? (userRestoredSteps[idx] || s.pseudo) : (currentStepIdx === idx ? '?? ?ㅺ퀎 吏꾪뻾 以???' : '...') }}</span>
           </div>
        </div>
        <div v-else class="code-content pre-wrap">{{ pseudocode }}</div>
      </div>

      <!-- Right: Generated Python -->
      <div class="code-panel python-panel">
        <div class="panel-header">
          <span class="icon">?릫</span>
          <span class="title">AI_IMPLEMENTATION (PYTHON)</span>
        </div>
        <div class="code-content">
          <!-- [蹂듦뎄 ?묒쟾 紐⑤뱶] ?꾩옱 留욎텣 ?④퀎源뚯? ?섏씠?쇱씠??-->
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

    <!-- ?섎떒: ?④퀎蹂?寃利??곸뿭 -->
    <div class="validation-area">
      <div class="advice-block" :class="{ 'is-recovery-complete': isBlueprintComplete }">
        <div class="advice-header">
          <span class="icon">?뮕</span>
          <span class="title">{{ isBlueprintComplete ? 'SYSTEM RECOVERED' : 'AI ARCHITECT ADVICE' }}</span>
        </div>
        <p class="advice-text">
            {{ isBlueprintComplete ? '?깃났?곸쑝濡??꾪궎?띿쿂瑜?蹂듦뎄?덉뒿?덈떎! ?뱀떊? ?댁젣 ?щ컮瑜??ㅺ퀎 ?먯튃???댄빐???꾪궎?랁듃?낅땲??' : evaluationFeedback }}
        </p>
      </div>

      <!-- 2-1?④퀎: [蹂듦뎄 ?묒쟾] 留ㅼ묶 ?곸뿭 -->
      <div v-if="isBlueprintMode && !isBlueprintComplete" class="challenge-block blueprint-section recovery-action">
        <div class="challenge-header">
           <div class="recovery-guide-banner">
              <span class="guide-icon">?썱截?/span>
              <div class="guide-text">
                <strong>?꾪궎?띿쿂 蹂듦뎄 ?묒쟾:</strong> ?섏씠?쇱씠?몃맂 ?뚯씠??肄붾뱶???뚮쭪? ?ㅺ퀎 ?섎룄(?섏궗肄붾뱶)瑜?<span class="highlight-text">吏곸젒 ?낅젰</span>?섍굅???꾨옒?먯꽌 <span class="highlight-text">?좏깮</span>?섏꽭??
              </div>
           </div>
        </div>

        <div class="recovery-interaction-hub">
           <!-- [NEW] ?듭떖 ?ㅼ썙??媛?대뱶 ?곸뿭 -->
           <div class="keyword-hint-area">
              <span class="hint-label">?뵎 ?듭떖 ?ㅼ썙??</span>
              <div class="keyword-tags">
                 <span v-for="k in currentStepKeywords" :key="k" class="keyword-tag">{{ k }}</span>
              </div>
           </div>

           <!-- [NEW] ?섎룞 ?낅젰 紐⑤뱶 -->
           <div class="manual-input-zone">
              <input 
                v-model="manualInput" 
                class="recovery-input" 
                :class="{ 'error-shake': showInputError }"
                placeholder="?ㅼ썙?쒕? ?쒖슜???ㅺ퀎 ?섎룄瑜??묒꽦??蹂댁꽭??.."
                @keyup.enter="handleManualSubmit"
              />
              <button class="btn-verify" @click="handleManualSubmit">?뺤씤</button>
           </div>
           <div v-if="showInputError" class="input-error-msg animate-fadeIn">
              ?낅젰?섏떊 ?댁슜???듭떖 ?ㅼ썙?쒓? 遺議깊빀?덈떎. ???뚰듃瑜?李멸퀬??蹂댁꽭??
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

      <!-- 2-2?④퀎: ?쇰컲 MCQ ?먮뒗 ?꾨즺 ???몄텧 -->
      <div v-else-if="(phase === 'PYTHON_VISUALIZATION' || phase === 'TAIL_QUESTION') && !isBlueprintMode" class="challenge-block mcq-section">
        <div class="challenge-header">
          <span class="badge">DEEP DIVE CHALLENGE</span>
          <h4 class="challenge-question">[{{ mcqData?.context || '寃利? }}] {{ mcqData?.question || '?곗씠?곕? 遺꾩꽍?????놁뒿?덈떎.' }}</h4>
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
      </div>

      <div v-if="isMcqAnswered || isBlueprintComplete" class="mcq-feedback-popup">
          <p class="text-success">?렞 ?뺣떟?낅땲?? ?꾪궎?띿쿂 ?먮쫫???꾨꼍??蹂듦뎄?섏뿀?듬땲??</p>
      </div>

      <div v-if="phase === 'DEEP_DIVE_DESCRIPTIVE'" class="challenge-block descriptive-section">
        <div class="challenge-header">
          <span class="badge scenario-badge">{{ assignedScenario?.axis }}??異?梨뚮┛吏</span>
          <div class="scenario-intent-guide">
            <span class="guide-label">?렞 ?ㅺ퀎 ?섎룄:</span>
            <span class="guide-text">{{ assignedScenario?.intent }}</span>
          </div>
          <h4 class="challenge-question">
            <strong>[?쒕굹由ъ삤: {{ assignedScenario?.title }}]</strong><br/>
            {{ assignedScenario?.question }}
          </h4>
        </div>

        <div class="descriptive-input-wrapper">
          <textarea 
            v-model="descriptiveAnswer"
            class="descriptive-textarea"
            placeholder="?쒕굹由ъ삤??????닿껐梨낆쓣 1~2臾몄옣???먯뿰?대줈 ?쒖닠?섏꽭??.."
            :disabled="isDescriptionSubmitted"
          ></textarea>
        </div>

        <!-- [異붽?] 紐⑤쾾 ?듭븞 ?몄텧 ?곸뿭 -->
        <div v-if="isDescriptionSubmitted" class="model-answer-block animate-fadeIn">
            <div class="model-answer-header">
                <span class="model-icon">?룇</span>
                <strong>AI ?꾪궎?랁듃??紐⑤쾾 ?듭븞</strong>
            </div>
            <p class="model-answer-text">{{ assignedScenario?.modelAnswer }}</p>
            <div class="model-answer-tip">
                * ?ㅼ젣 ?됯? ?먯닔??由ы룷???앹꽦 ??5李⑥썝 硫뷀듃由?쑝濡??곸꽭 遺꾩꽍?⑸땲??
            </div>
        </div>
      </div>

      <div class="action-footer">
        <button 
          v-if="!isDescriptionSubmitted"
          class="final-btn" 
          :disabled="!isPhaseReady"
          @click="handleNext"
        >
          {{ nextButtonText }} ??        </button>
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
  mcqData: Object,
  blueprintSteps: Array,      // 異붽?: [{python, pseudo}]
  assignedScenario: Object,
  isMcqAnswered: Boolean
});

const emit = defineEmits(['answer-mcq', 'submit-descriptive', 'next-phase']);

const currentStepIdx = ref(0);
const selectedIdx = ref(null);
const isStepAnswered = ref(false);
const descriptiveAnswer = ref("");
const isDescriptionSubmitted = ref(false);
const manualInput = ref("");
const showInputError = ref(false);
const userRestoredSteps = ref([]); // ?ъ슜?먭? 吏곸젒 ??댄븨?섍굅???좏깮??臾몄옣 ???
const isBlueprintMode = computed(() => props.blueprintSteps && props.blueprintSteps.length > 0);
const isBlueprintComplete = computed(() => isBlueprintMode.value && currentStepIdx.value >= props.blueprintSteps.length);

const currentStepKeywords = computed(() => {
    if (!isBlueprintMode.value || isBlueprintComplete.value) return [];
    return props.blueprintSteps[currentStepIdx.value]?.keywords || [];
});

// 泥?궗吏?紐⑤뱶???쒕뜡 ?듭뀡 ?앹꽦 (?뺣떟 + ?ㅻ떟 ?욊린)
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

const nextButtonText = computed(() => {
  if (isBlueprintMode.value && !isBlueprintComplete.value) return "?ㅺ퀎 蹂듦뎄 吏꾪뻾 以?;
  if (props.phase === 'PYTHON_VISUALIZATION' || props.phase === 'TAIL_QUESTION') return "DEEP DIVE 吏꾩엯";
  if (props.phase === 'DEEP_DIVE_DESCRIPTIVE') return "理쒖쥌 ?됯? 由ы룷???앹꽦";
  return "?ㅼ쓬 ?④퀎";
});

const handleStepPick = (idx) => {
  if (isStepAnswered.value) return;
  selectedIdx.value = idx;
  const opt = blueprintOptions.value[idx];

  if (opt.isCorrect) {
    userRestoredSteps.value[currentStepIdx.value] = opt.pseudo; 
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
    
    // [?먮퉬濡쒖슫 寃利? ?ㅼ썙?쒓? 1媛쒕쭔 ?덉뼱???몄젙
    if (matchCount >= 1 || manualInput.value.length > 30) {
        userRestoredSteps.value[currentStepIdx.value] = manualInput.value; 
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
    }, 800);
};

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
  min-height: 55vh; /* [2026-02-14] ?섎떒 踰꾪듉 ?몄텧 ?뺣낫瑜??꾪빐 ?섑뼢 */
}

/* [2026-02-14] 蹂듦뎄 ?묒쟾 ?꾩슜 UI ?ㅽ???*/
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

/* [2026-02-14] ?ㅼ썙???뚰듃 ?ㅽ???*/
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
  font-size: 1rem; /* ?고듃 ?ш린 ?뚰룺 ?곹뼢 */
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

/* [2026-02-14] 紐⑤쾾 ?듭븞 ?ㅽ???*/
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

/* [泥?궗吏?蹂듦뎄 ?묒쟾 ?꾩슜 ?ㅽ??? */
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
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
