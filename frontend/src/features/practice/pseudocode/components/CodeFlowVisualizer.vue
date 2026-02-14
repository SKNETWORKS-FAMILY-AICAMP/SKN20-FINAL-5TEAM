<template>
  <div class="code-flow-visualizer">
    <div class="content flex flex-col gap-8">
      <!-- [2026-02-14] MISSION & CONSTRAINTS: 가독성을 위해 최상단에 고정 배치 -->
      <div class="mission-instruction-compact animate-slideDownFade">
          <div class="mi-section">
              <h4 class="mi-title text-blue-400" style="font-family: 'Pretendard', sans-serif;">[미션]</h4>
              <p class="mi-desc" style="font-family: 'Pretendard', sans-serif;">{{ missionDesc }}</p>
          </div>
          <div class="mi-section mi-border-top" v-if="missionConstraints">
              <h4 class="mi-title text-amber-400" style="font-family: 'Pretendard', sans-serif;">[필수 포함 조건 (CONSTRAINT)]</h4>
              <p class="mi-desc-small" style="font-family: 'Pretendard', sans-serif;">
                {{ missionConstraints.replace('[필수 포함 조건 (Constraint)]\n', '').replace('[필수 포함 조건 (CONSTRAINT)]\n', '') }}
              </p>
          </div>
      </div>

      <!-- Dual Code View Grid -->
      <div class="code-comparison-grid grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Pseudo Code Section (Editable in Retry Mode) -->
        <div class="code-panel pseudo-panel" :class="{ 'is-editing-mode': isEditing }">
          <div class="panel-header">
            <div class="flex items-center gap-2">
              <Code2 class="w-4 h-4 text-blue-400" />
              <span class="label">{{ isEditing ? 'RE-DESIGNING ARCHITECTURE' : 'PSEUDO CODE' }}</span>
            </div>
            <span class="status">{{ isEditing ? 'EDITING_ACTIVE' : 'INPUT_LOGIC' }}</span>
          </div>
          
          <div class="code-block relative">
            <!-- Static View -->
            <pre v-if="!isEditing"><code class="language-plaintext">{{ pseudoCode || '의사코드가 없습니다.' }}</code></pre>
            
            <!-- Editor View [2026-02-13] 인라인 편집 고도화 -->
            <div v-else class="pseudo-editor-container h-full flex flex-col">
              <textarea 
                v-model="localPseudo" 
                class="pseudo-editor-textarea custom-scrollbar"
                placeholder="청사진을 참고하여 설계를 보완해 보세요..."
                spellcheck="false"
              ></textarea>
              <div class="editor-actions mt-4 flex gap-3">
                <button @click="submitEdit" class="re-submit-btn flex-1">
                  평가 다시 받기
                </button>
                <button @click="isEditing = false" class="cancel-edit-btn">
                  취소
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Python Code Section -->
        <div 
          class="code-panel python-panel"
          :class="{ 'blueprint-highlight': isLowEffort && !isEditing }"
          @click="isLowEffort && !isEditing && (isEditing = true)"
        >
          <!-- [2026-02-13] 청사진 학습 권유 오버레이 (무성의 입력 시) -->
          <div v-if="isLowEffort && !isEditing" class="blueprint-hover-overlay">
            <div class="overlay-content animate-scaleIn">
              <div class="sparkle-icon-wrapper mb-4">
                <RotateCcw class="w-12 h-12 text-green-400 animate-spin-slow" />
              </div>
              <h5 class="text-2xl font-black text-green-400 mb-2 tracking-tighter">아키텍트의 설계 엿보기</h5>
              <p class="text-slate-100 text-lg mb-4 leading-relaxed font-bold" style="font-family: 'Pretendard', sans-serif;">
                "어렵다면 <span class="text-green-400">파이썬 코드</span>를 보고<br/>
                논리 흐름을 먼저 파악해볼까요?"
              </p>
              <p class="text-[11px] text-amber-400/90 mb-6 font-medium">* 청사진을 참고하여 복습하면 실력이 더 빠르게 늘어납니다.</p>
              <div class="retry-trigger-btn px-8 py-3 bg-green-500 text-slate-900 font-black rounded-full hover:bg-green-400 transition-all shadow-lg text-lg">
                정답 보고 다시 설계하기
              </div>
            </div>
          </div>

          <div class="panel-header">
            <div class="flex items-center gap-2">
              <Play class="w-4 h-4 text-green-400" />
              <span class="label">ARCHITECT BLUEPRINT</span>
            </div>
            <span class="status">{{ isLowEffort ? 'ISOLATION_BLUEPRINT' : 'AI_IMPLEMENTATION' }}</span>
          </div>
          <div class="code-block">
            <pre><code class="language-python">{{ pythonCode || '# 변환된 코드가 없습니다.' }}</code></pre>
          </div>
        </div>
      </div>

      <!-- Analysis & Question Section -->
      <div class="analysis-container bg-[#0d1525] border border-slate-700/50 rounded-2xl p-6 shadow-2xl">
        <!-- Feedback Section -->
        <div class="feedback-section mb-8" v-if="feedback">
          <div class="flex items-start gap-4">
            <div class="feedback-icon bg-blue-500/10 p-3 rounded-xl border border-blue-500/20">
              <Lightbulb class="w-6 h-6 text-blue-400" />
            </div>
            <div class="feedback-content flex-1">
              <div class="flex items-center justify-between mb-2">
                <h4 class="text-blue-400 font-bold tracking-tight">AI ARCHITECT ADVICE</h4>
                <div class="score-pill bg-blue-500/10 px-3 py-1 rounded-full border border-blue-500/20">
                  <span class="text-xs font-bold text-blue-300">LOGIC SCORE: {{ score }}</span>
                </div>
              </div>
              <p class="text-slate-300 leading-relaxed text-lg" style="font-family: 'Pretendard', sans-serif;">{{ feedback }}</p>
            </div>
          </div>
        </div>

        <!-- Interactive Question Section -->
        <div v-if="questionData" class="question-interactive-box border-t border-slate-700/50 pt-8 animate-fadeIn">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-1.5 h-8 bg-blue-500 rounded-full"></div>
            <h4 class="text-xl font-black text-white uppercase tracking-tighter">
              {{ isLowEffort ? 'ARCHITECTURE REVIEW QUESTION' : 'DEEP DIVE CHALLENGE' }}
            </h4>
          </div>

          <div class="question-body mb-8">
            <p class="text-xl font-bold text-slate-100 leading-snug">{{ questionData.question }}</p>
          </div>

          <!-- Answer Logic -->
          <div class="options-grid grid grid-cols-1 md:grid-cols-2 gap-4">
            <button 
              v-for="(opt, idx) in questionData.options" 
              :key="idx"
              @click="onSelectOption(idx)"
              :disabled="isAnswered"
              class="option-btn group"
              :class="{
                'selected': selectedIdx === idx,
                'correct': isAnswered && opt.is_correct,
                'wrong': isAnswered && selectedIdx === idx && !opt.is_correct
              }"
            >
              <div class="flex items-center gap-4">
                <div class="opt-id">{{ String.fromCharCode(65 + idx) }}</div>
                <span class="opt-text">{{ opt.text }}</span>
              </div>
              <CheckCircle v-if="isAnswered && opt.is_correct" class="w-6 h-6 text-emerald-400" />
              <AlertOctagon v-if="isAnswered && selectedIdx === idx && !opt.is_correct" class="w-6 h-6 text-rose-500" />
            </button>
          </div>

          <!-- [2026-02-13] 답변 후 미션 완료 전 심화 통찰(심화질문 1~2줄 대응) 노출 -->
          <div v-if="isAnswered" class="ans-feedback-panel mt-8 p-6 rounded-2xl bg-blue-500/5 border border-blue-500/20 animate-scaleIn">
             <div class="flex items-start gap-4">
                <div class="ans-status p-2 rounded-lg" :class="isCorrect ? 'bg-emerald-500/10' : 'bg-rose-500/10'">
                   <component :is="isCorrect ? CheckCircle : AlertOctagon" :class="isCorrect ? 'text-emerald-400' : 'text-rose-400'" />
                </div>
                <div class="ans-content flex-1">
                   <h5 class="text-sm font-black uppercase tracking-widest mb-1" :class="isCorrect ? 'text-emerald-400' : 'text-rose-400'">
                      {{ isCorrect ? 'STRATEGY VALIDATED' : 'CONCEPT MISALIGNMENT' }}
                   </h5>
                   <p class="text-slate-300 font-medium leading-relaxed">{{ resultReason }}</p>
                   
                   <!-- [심화 질문/조언 1-2줄] -->
                   <div class="deep-insight-highlight mt-4 pt-4 border-t border-blue-500/10">
                      <h6 class="text-[10px] font-bold text-blue-400 uppercase mb-1">Architect's Deep Insight</h6>
                      <p class="text-blue-100/90 text-sm italic italic tracking-tight">"{{ seniorAdvice || '설계의 일관성을 유지하는 것이 실무 데이터 사이언스의 핵심입니다.' }}"</p>
                   </div>
                </div>
             </div>
          </div>
        </div>
      </div>

    <!-- Final Action Button -->
    <div class="actions mt-12 flex justify-center gap-6">
      <!-- [2026-02-13] 복기 모드 시 재설계 버튼 추가 -->
      <button 
        v-if="isLowEffort"
        @click="$emit('retry')"
        class="btn-retry-action group"
      >
        <div class="flex items-center gap-3">
          <RotateCcw class="w-6 h-6 group-hover:rotate-[-120deg] transition-transform" />
          <span class="text-xl font-black italic tracking-tighter">RETRY WITH BLUEPRINT</span>
        </div>
      </button>

      <button 
        v-if="!questionData || isAnswered"
        @click="$emit('next')" 
        class="btn-finish-action group"
      >
        <div class="flex items-center gap-3">
          <span class="text-xl font-black italic tracking-tighter">{{ isAnswered ? 'COMPLETE MISSION' : 'START FINAL EVALUATION' }}</span>
          <ArrowRight class="w-6 h-6 group-hover:translate-x-2 transition-transform" />
        </div>
      </button>
    </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, computed } from 'vue';
import { Lightbulb, ArrowRight, Code2, Play, CheckCircle, AlertOctagon, RotateCcw } from 'lucide-vue-next';

const props = defineProps({
  pseudoCode: String,
  pythonCode: String,
  score: { type: Number, required: true },
  feedback: String,
  isLowEffort: Boolean,
  seniorAdvice: String,
  missionTitle: { type: String, default: 'MISSION_ACTIVE' },
  missionDesc: { type: String, default: '설계 미션 설명이 없습니다.' },
  missionConstraints: { type: String, default: '제약조건이 없습니다.' },
  questionData: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['next', 'select-option', 'retry', 'submit-pseudo']);

const isEditing = ref(false);
const localPseudo = ref(props.pseudoCode || '');

const submitEdit = () => {
  if (!localPseudo.value.trim()) return;
  emit('submit-pseudo', localPseudo.value);
  isEditing.value = false;
};

const selectedIdx = ref(null);
const isAnswered = ref(false);
const isCorrect = ref(false);
const resultReason = ref('');

const onSelectOption = (idx) => {
  if (isAnswered.value) return;
  selectedIdx.value = idx;
  isAnswered.value = true;
  
  const selected = props.questionData.options[idx];
  isCorrect.value = selected.is_correct || selected.correct; // 심화/꼬리 질문 프로퍼티 호환
  resultReason.value = selected.reason || (isCorrect.value ? '정답입니다!' : '오답입니다.');
  
  emit('select-option', idx);
};
</script>

<style scoped>
.code-flow-visualizer {
  background: rgba(10, 15, 25, 0.4);
  color: #fff;
  width: 100%;
  height: 100%;
}

/* Dual Panel Styles */
.code-panel {
  background: #0a1220;
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.pseudo-panel {
  border-color: rgba(59, 130, 246, 0.3);
}

.python-panel {
  border-color: rgba(74, 222, 128, 0.3);
}

.panel-header {
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.panel-header .label {
  /* [수정 2026-02-14] 가독성을 위해 폰트군을 Pretendard로 강제 고정 */
  font-family: 'Pretendard', sans-serif !important;
  font-size: 14px !important;
  font-weight: 800;
  letter-spacing: 0.5px;
}

.pseudo-panel .label { color: #3b82f6; }
.python-panel .label { color: #4ade80; }

.panel-header .status {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  opacity: 0.5;
}

.code-block {
  padding: 24px;
  flex: 1;
  overflow-y: auto;
  min-height: 350px;
  max-height: 550px;
  background: rgba(0, 0, 0, 0.3);
}

.code-block pre,
.code-block code {
  margin: 0;
  /* [수정 2026-02-14] NES.css 등의 픽셀 폰트 간섭을 완전히 차단하고 VS Code 스타일로 강제 고정 */
  font-family: 'Consolas', 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace !important;
  font-size: 17px !important;
  line-height: 1.7 !important;
  white-space: pre-wrap !important;
  letter-spacing: 0px !important;
  font-weight: 400 !important;
}

.pseudo-panel code { color: #e2e8f0; }
.python-panel code { color: #4ade80; }

/* System Context Reference */
.system-context-reference {
  animation: slideDownFade 0.6s ease-out;
}

.context-scroll {
  scrollbar-width: thin;
  scrollbar-color: rgba(59, 130, 246, 0.3) transparent;
  cursor: grab;
}

.context-scroll:active {
  cursor: grabbing;
}

.context-scroll::-webkit-scrollbar {
  width: 4px;
}

.context-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.context-scroll::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.3);
  border-radius: 10px;
}

@keyframes slideDownFade {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.mission-instruction-compact {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(51, 65, 85, 0.5);
  border-radius: 16px;
  margin-bottom: 24px;
}

.mi-section {
  display: flex;
  flex-direction: column;
}

.mi-border-top {
  border-top: 1px solid rgba(51, 65, 85, 0.3);
  padding-top: 16px;
}

.mi-title {
  font-weight: 900;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 8px;
}

.mi-desc {
  color: #e2e8f0;
  font-size: 0.875rem;
  line-height: 1.6;
}

.mi-desc-small {
  color: #cbd5e1;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-line;
}

.animate-slideDownFade {
  animation: slideDownFade 0.6s ease-out forwards;
}

/* Action Button */
.btn-finish-action {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  padding: 24px 60px;
  border-radius: 20px;
  border: none;
  cursor: pointer;
  box-shadow: 0 15px 35px rgba(37, 99, 235, 0.4);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.btn-finish-action:hover {
  transform: translateY(-5px) scale(1.05);
  box-shadow: 0 20px 45px rgba(37, 99, 235, 0.6);
}

.btn-retry-action {
  background: rgba(30, 41, 59, 0.6);
  border: 2px solid #3b82f6;
  color: #3b82f6;
  padding: 24px 60px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.btn-retry-action:hover {
  background: #3b82f6;
  color: white;
  transform: translateY(-5px) scale(1.05);
  box-shadow: 0 15px 35px rgba(59, 130, 246, 0.4);
}

/* Question Interactive Box */
.option-btn {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 20px;
  text-align: left;
  transition: all 0.3s;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #e2e8f0;
}

.option-btn:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.4);
  transform: translateX(8px);
}

.option-btn.selected {
  background: rgba(59, 130, 246, 0.15);
  border-color: #3b82f6;
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.2);
}

.option-btn.correct {
  background: rgba(16, 185, 129, 0.2);
  border-color: #10b981;
  color: #10b981;
}

.option-btn.wrong {
  background: rgba(239, 68, 68, 0.2);
  border-color: #ef4444;
  color: #ef4444;
}

.opt-id {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-weight: 900;
  font-size: 14px;
}

.opt-text {
  font-size: 18px;
  font-weight: 600;
}

.animate-fadeIn {
  animation: fadeIn 0.8s ease-out forwards;
}

.animate-scaleIn {
  animation: scaleIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.9); }
  to { opacity: 1; transform: scale(1); }
}

/* [2026-02-13] Blueprint Highlight & Sparkle Effects */
.blueprint-highlight {
  position: relative;
  cursor: pointer;
  border: 2px solid rgba(74, 222, 128, 0.5) !important;
  box-shadow: 0 0 20px rgba(74, 222, 128, 0.2);
  overflow: hidden;
  transition: all 0.4s ease;
}

.blueprint-highlight::before {
  content: '';
  position: absolute;
  top: -150%;
  left: -50%;
  width: 200%;
  height: 400%;
  background: linear-gradient(
    to bottom,
    transparent,
    rgba(74, 222, 128, 0.1),
    transparent
  );
  transform: rotate(45deg);
  animation: shimmer 4s infinite linear;
  pointer-events: none;
}

@keyframes shimmer {
  0% { transform: translate(-100%, -100%) rotate(45deg); }
  100% { transform: translate(100%, 100%) rotate(45deg); }
}

.blueprint-hover-overlay {
  position: absolute;
  inset: 0;
  background: rgba(8, 12, 21, 0.88);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 50;
  backdrop-filter: blur(6px);
  border-radius: inherit;
}

.blueprint-highlight:hover .blueprint-hover-overlay {
  opacity: 1;
}

.blueprint-highlight:hover {
  transform: scale(1.01);
  box-shadow: 0 0 35px rgba(74, 222, 128, 0.4);
  border-color: #4ade80 !important;
}

.overlay-content {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
}

.animate-spin-slow {
  animation: spin-slow 6s linear infinite;
}

@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(-360deg); }
}

.retry-trigger-btn {
  animation: pulse-green 2s infinite;
}

@keyframes pulse-green {
  0% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.4); }
  70% { box-shadow: 0 0 15px 15px rgba(74, 222, 128, 0); }
  100% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0); }
}

/* [2026-02-13] Inline Pseudo Editor Styles */
.pseudo-editor-textarea {
  width: 100%;
  min-height: 400px;
  background: rgba(10, 15, 25, 0.6);
  color: #fff;
  /* [수정 2026-02-14] 에디터 폰트 가독성 강제 상향 */
  font-family: 'Consolas', 'JetBrains Mono', 'Fira Code', monospace !important;
  font-size: 18px !important;
  line-height: 1.7 !important;
  padding: 20px;
  border: 1px dashed rgba(59, 130, 246, 0.4);
  border-radius: 12px;
  resize: none;
  outline: none;
  transition: all 0.3s ease;
  letter-spacing: 0px !important;
}

.pseudo-editor-textarea:focus {
  border-color: #3b82f6;
  border-style: solid;
  background: rgba(10, 15, 25, 0.8);
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.15);
}

.re-submit-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 14px 28px;
  border-radius: 12px;
  font-weight: 800;
  font-size: 16px;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
  transition: all 0.3s ease;
}

.re-submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
}

.cancel-edit-btn {
  background: rgba(255, 255, 255, 0.05);
  color: #94a3b8;
  padding: 14px 24px;
  border-radius: 12px;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-edit-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.is-editing-mode {
  border-color: #3b82f6 !important;
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.2) !important;
}
</style>
