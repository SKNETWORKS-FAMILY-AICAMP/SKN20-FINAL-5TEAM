<template>
  <div class="code-flow-visualizer">
    <div class="content flex flex-col gap-8">
      <!-- Dual Code View Grid -->
      <div class="code-comparison-grid grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Pseudo Code Section -->
        <div class="code-panel pseudo-panel">
          <div class="panel-header">
            <div class="flex items-center gap-2">
              <Code2 class="w-4 h-4 text-blue-400" />
              <span class="label">PSEUDO CODE</span>
            </div>
            <span class="status">INPUT_LOGIC</span>
          </div>
          <div class="code-block">
            <pre><code class="language-plaintext">{{ pseudoCode || '의사코드가 없습니다.' }}</code></pre>
          </div>
        </div>

        <!-- Python Code Section -->
        <div class="code-panel python-panel">
          <div class="panel-header">
            <div class="flex items-center gap-2">
              <Play class="w-4 h-4 text-green-400" />
              <span class="label">PYTHON CODE</span>
            </div>
            <span class="status">CONVERTED_STABLE</span>
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
              <p class="text-slate-300 leading-relaxed text-lg">{{ feedback }}</p>
            </div>
          </div>
        </div>

        <!-- Interactive Question Section -->
        <div v-if="questionData" class="question-interactive-box border-t border-slate-700/50 pt-8 animate-fadeIn">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-2 h-8 bg-blue-500 rounded-full"></div>
            <h4 class="text-xl font-black text-white uppercase tracking-tighter">
              {{ score < 80 ? 'ARCHITECTURE TAIL QUESTION' : 'DEEP DIVE CHALLENGE' }}
            </h4>
          </div>

          <div class="question-wrapper mb-8">
            <p class="text-2xl font-bold text-slate-100 mb-6 leading-snug">{{ questionData.question }}</p>
            
            <div class="options-grid grid grid-cols-1 md:grid-cols-2 gap-4">
              <button 
                v-for="(opt, idx) in questionData.options" 
                :key="idx"
                @click="onSelectOption(idx)"
                :disabled="isAnswered"
                class="option-btn"
                :class="{
                  'selected': selectedIdx === idx,
                  'correct': isAnswered && opt.is_correct,
                  'wrong': isAnswered && selectedIdx === idx && !opt.is_correct,
                  'opacity-50 pointer-events-none': isAnswered && selectedIdx !== idx && !opt.is_correct
                }"
              >
                <div class="flex items-center gap-4">
                  <span class="opt-id">{{ String.fromCharCode(65 + idx) }}</span>
                  <span class="opt-text">{{ opt.text }}</span>
                </div>
                <CheckCircle v-if="isAnswered && opt.is_correct" class="w-6 h-6 text-green-400" />
                <AlertOctagon v-if="isAnswered && selectedIdx === idx && !opt.is_correct" class="w-6 h-6 text-red-400" />
              </button>
            </div>
          </div>

          <!-- Result Feedback -->
          <div v-if="isAnswered" class="result-feedback p-6 rounded-2xl animate-scaleIn" :class="isCorrect ? 'bg-green-500/10 border border-green-500/30' : 'bg-red-500/10 border border-red-500/30'">
            <div class="flex items-center gap-4 mb-3">
              <component :is="isCorrect ? CheckCircle : AlertOctagon" :class="isCorrect ? 'text-green-400' : 'text-red-400'" class="w-8 h-8" />
              <h5 class="text-xl font-black uppercase tracking-widest" :class="isCorrect ? 'text-green-400' : 'text-red-400'">
                {{ isCorrect ? 'STABILITY MATCHED' : 'SYSTEM VULNERABILITY FOUND' }}
              </h5>
            </div>
            <p class="text-slate-200 text-lg leading-relaxed">{{ resultReason }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Final Action Button -->
    <div class="actions mt-12 flex justify-center">
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
</template>

<script setup>
import { defineProps, defineEmits, ref, computed } from 'vue';
import { Lightbulb, ArrowRight, Code2, Play, CheckCircle, AlertOctagon } from 'lucide-vue-next';

const props = defineProps({
  pseudoCode: String,
  pythonCode: String,
  score: { type: Number, required: true },
  feedback: String,
  questionData: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['next', 'select-option']);

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
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 1px;
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

.code-block pre {
  margin: 0;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 18px;
  line-height: 1.7;
  white-space: pre-wrap;
  letter-spacing: -0.2px;
}

.pseudo-panel code { color: #e2e8f0; }
.python-panel code { color: #4ade80; }

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
</style>
