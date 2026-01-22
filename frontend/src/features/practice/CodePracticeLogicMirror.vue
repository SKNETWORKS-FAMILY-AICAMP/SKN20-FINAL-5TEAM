<template>
  <!-- 
    [수정일: 2026-01-23]
    [수정내용: LogicTrainer를 고성능 모달 레이아웃으로 변환]
  -->
  <div 
    class="fixed inset-0 flex items-center justify-center p-4 bg-black/95 backdrop-blur-2xl animate-in fade-in duration-500 overflow-y-auto"
    style="z-index: 9999;"
  >
    <!-- 메인 컨테이너 (사이버펑크 스타일) -->
    <div 
      class="bg-[#020617] border border-slate-800/50 w-full max-w-[1400px] min-h-[650px] h-[95vh] my-auto rounded-[3rem] shadow-[0_0_120px_rgba(30,58,138,0.2)] flex flex-col overflow-hidden relative interactive-border"
      :class="{ 'shake-active': isShaking }"
    >
      <!-- 배경 글로우 효과 -->
      <div class="absolute top-0 left-1/4 w-[500px] h-[500px] bg-blue-600/5 rounded-full blur-[150px] -z-10 animate-pulse"></div>
      <div class="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-indigo-600/5 rounded-full blur-[150px] -z-10"></div>

      <!-- 헤더 (CodePracticeLogicMirror 스타일 계승) -->
      <header class="h-24 border-b border-slate-800/50 px-10 flex items-center justify-between bg-slate-900/5 backdrop-blur-md z-20">
        <div class="flex items-center gap-10">
          <div class="flex flex-col">
            <h1 class="text-5xl font-black italic tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-400 to-indigo-500 uppercase leading-none mb-1">
              Logic_Trainer <span class="text-white/20 text-2xl">v4.0</span>
            </h1>
            <div class="flex items-center gap-4 mt-1">
              <span class="w-3 h-3 rounded-full bg-emerald-500 animate-ping"></span>
              <p class="text-xs text-slate-400 font-black tracking-[0.6em] uppercase orbitron">Neural_Learning_Unit_Active</p>
            </div>
          </div>

          <!-- 네비게이션 HUD -->
          <div class="flex items-center gap-4 bg-slate-950/80 p-2 rounded-3xl border border-slate-800/50 shadow-inner">
            <button 
              @click="store.prevProblem" 
              class="p-3 bg-slate-900/50 hover:bg-slate-800 rounded-2xl transition-all active:scale-90"
            >
              <ChevronLeft class="w-5 h-5 text-slate-400" />
            </button>
            <div class="px-8 border-x border-slate-800 text-center min-w-[200px]">
              <div class="text-[10px] text-slate-600 font-black tracking-widest mb-1 uppercase orbitron">Mission_Module</div>
              <div class="text-lg font-black text-white truncate max-w-[180px] rajdhani italic">{{ currentProblem?.title_ko }}</div>
            </div>
            <button 
              @click="store.nextProblem"
              class="p-3 bg-slate-900/50 hover:bg-slate-800 rounded-2xl transition-all active:scale-90"
            >
              <ChevronRight class="w-5 h-5 text-slate-400" />
            </button>
          </div>
        </div>

        <div class="flex items-center gap-8">
          <button 
            @click="$emit('close')" 
            class="group p-4 bg-slate-900/50 hover:bg-red-500/10 text-slate-500 hover:text-red-400 rounded-2xl border border-slate-800/50 hover:border-red-500/30 transition-all active:scale-95"
          >
            <X class="w-6 h-6 transition-transform group-hover:rotate-90" />
          </button>
        </div>
      </header>

      <!-- 실제 작업 영역 -->
      <div class="flex-1 overflow-hidden p-10 flex gap-10">
        <!-- 왼쪽 사이드바 (문제 정보) -->
        <aside class="w-80 flex flex-col gap-6 shrink-0 overflow-y-auto custom-scrollbar pr-2">
          <!-- Mission Intelligence -->
          <div class="bg-slate-900/40 border-l-4 border-cyan-500 p-8 rounded-3xl shadow-2xl backdrop-blur-xl">
             <h2 class="text-[10px] font-black flex items-center gap-2 text-cyan-400 tracking-widest uppercase mb-4">
               <ShieldAlert class="w-4 h-4" /> Operational_Brief
             </h2>
             <div class="text-lg font-bold text-slate-200 leading-relaxed mb-6 tracking-tight">
               {{ currentProblem?.description_ko }}
             </div>
             
             <!-- IO Reference -->
             <div class="space-y-3">
                <div v-for="(ex, i) in parsedExamples" :key="i" class="bg-slate-950/80 p-5 rounded-3xl border border-slate-800/80 group hover:border-cyan-500/50 transition-all hover:-translate-y-1">
                  <div class="text-[10px] text-slate-600 font-black uppercase mb-3 orbitron group-hover:text-cyan-400">Target_Stream_{{ i+1 }}</div>
                  <div class="text-sm font-mono flex items-center gap-2 mb-1"><span class="text-cyan-500/50 text-[10px] orbitron uppercase">IN:</span> {{ ex.parsed.input }}</div>
                  <div class="text-sm font-mono flex items-center gap-2"><span class="text-emerald-500/50 text-[10px] orbitron uppercase">OUT:</span> {{ ex.parsed.output }}</div>
                </div>
             </div>
          </div>

          <!-- Neural Link Gauge (NEW: 게임 느낌 강화) -->
          <div class="bg-slate-900/20 border border-slate-800/30 p-10 rounded-[2.5rem] backdrop-blur-sm relative overflow-hidden group">
            <div class="absolute inset-0 bg-blue-600/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <h3 class="text-xs text-slate-500 font-black tracking-[0.5em] uppercase mb-8 flex items-center justify-between orbitron">
              Sync_Telemetry
              <Zap class="w-5 h-5 text-cyan-500 animate-pulse" />
            </h3>
            <div class="relative z-10">
              <div class="flex justify-between items-end mb-4">
                <span class="text-xs text-slate-400 font-black uppercase tracking-widest orbitron">Core_Stability</span>
                <span :class="['text-2xl font-black italic rajdhani', syncStatusClass]">{{ syncRate }}%</span>
              </div>
              <div class="h-3 bg-slate-950 rounded-full p-0.5 border border-slate-800/50 overflow-hidden shadow-inner">
                <div 
                  class="h-full bg-gradient-to-r from-blue-600 via-cyan-400 to-indigo-500 rounded-full transition-all duration-700 ease-out shadow-[0_0_15px_rgba(6,182,212,0.4)]"
                  :style="{ width: `${syncRate}%` }"
                ></div>
              </div>
            </div>
          </div>

          <!-- Mermaid Logic Visualizer (NEW: 실시간 순서도) -->
          <div class="mt-auto">
             <MermaidRenderer :definition="mermaidDefinition" />
          </div>
        </aside>

        <!-- 메인 워크스테이션 -->
        <main class="flex-1 flex flex-col gap-8 h-full bg-[#080c14] border-2 border-slate-800/80 rounded-[3.5rem] overflow-hidden">
          <!-- 탭 시스템 -->
          <div class="h-20 border-b border-slate-800/50 flex bg-slate-900/10">
            <button 
              @click="activeTab = 'guide'; showDiff = false"
              :class="['flex-1 text-xs font-black tracking-[0.3em] uppercase transition-all orbitron border-r border-slate-800/50', activeTab === 'guide' ? 'text-indigo-400 bg-indigo-500/10' : 'text-indigo-400/40 hover:bg-slate-800/50']"
            >
              [ 00_Mission_Guide ]
            </button>
            <button 
              @click="activeTab = 'parsons'; showDiff = false"
              :class="['flex-1 text-xs font-black tracking-[0.3em] uppercase transition-all orbitron border-r border-slate-800/50', activeTab === 'parsons' ? 'text-cyan-400 bg-cyan-500/10' : 'text-slate-600 hover:bg-slate-800/50']"
            >
              [ 01_Neural_Puzzle ]
            </button>
            <button 
              @click="activeTab = 'editor'; showDiff = false"
              :class="['flex-1 text-xs font-black tracking-[0.3em] uppercase transition-all orbitron', activeTab === 'editor' ? 'text-indigo-400 bg-indigo-500/10' : 'text-slate-600 hover:bg-slate-800/50']"
            >
              [ 02_Logic_Expert ]
            </button>
          </div>

          <!-- 콘텐츠 영역 -->
          <div class="flex-1 p-8 overflow-y-auto custom-scrollbar relative">
            <template v-if="currentProblem">
              <!-- Guidebook (NEW: 게임 매뉴얼) -->
              <Guidebook v-if="activeTab === 'guide'" />

              <!-- impact 수신하여 화면 진동 트리거 -->
              <ParsonsPuzzle 
                v-if="activeTab === 'parsons'" 
                @impact="triggerImpact" 
              />
              
              <div v-if="activeTab === 'editor'" class="space-y-6 h-full flex flex-col">
                <template v-if="!showDiff">
                  <CodeEditor 
                    @submit="handleEvaluation" 
                    @impact="triggerImpact"
                    @syncUpdate="val => syncRate = val"
                    @change="handleCodeChange"
                  />
                  <CodeEvaluationResult 
                    :result="evaluationResult" 
                    v-if="evaluationResult" 
                    @show-diff="showDiff = true"
                  />
                </template>
                
                <CodeDiffViewer 
                  v-else
                  :original-code="currentProblem?.solution_code"
                  :modified-code="userSubmittedCode"
                  @close="showDiff = false"
                />
              </div>
            </template>
            
            <!-- 로딩 상태 표시 -->
            <div v-else class="h-full flex items-center justify-center text-slate-500 font-mono text-xs animate-pulse tracking-[1em]">
              LINKING_TO_CORE...
            </div>

            <!-- 배경 테크 패턴 -->
            <div class="absolute inset-0 opacity-[0.02] pointer-events-none tech-pattern"></div>
          </div>
        </main>
      </div>

      <!-- 푸터 텔레메트리 -->
      <footer class="h-14 border-t border-slate-800/50 px-12 flex items-center justify-between bg-slate-950/20 backdrop-blur-xl shrink-0">
        <div class="flex gap-12">
           <div class="flex items-center gap-3">
             <div class="flex gap-1">
               <div class="w-1 h-3 bg-blue-500/50 rounded-full"></div>
               <div class="w-1 h-3 bg-blue-500 rounded-full animate-bounce"></div>
             </div>
             <span class="text-[10px] text-slate-500 font-black tracking-[0.2em] uppercase italic">SKN20-FINAL-5TEAM</span>
           </div>
        </div>
        <div class="text-[10px] text-slate-700 font-black tracking-[0.4em] uppercase">SYSTEM_READY // 2026-01-23</div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useProblemStore } from '../../stores/useProblemStore';
import { parseAllExamples } from '../../utils/parser';
import { convertToMermaid } from '../../utils/logicToMermaid';
import { X, ChevronLeft, ChevronRight, ShieldAlert, Zap } from 'lucide-vue-next';

// 2026-01-23: 컴포넌트 구조화(unit별 분리)에 따른 unit1 경로 적용
import ParsonsPuzzle from './support/unit1/ParsonsPuzzle.vue';
import CodeEditor from './support/unit1/CodeEditor.vue';
import CodeEvaluationResult from './support/unit1/CodeEvaluationResult.vue';
import CodeDiffViewer from './support/unit1/CodeDiffViewer.vue';
import MermaidRenderer from './support/MermaidRenderer.vue';
import Guidebook from './support/Guidebook.vue';

const emit = defineEmits(['close']);

const store = useProblemStore();
const { currentProblem } = storeToRefs(store);

const activeTab = ref('guide');
const evaluationResult = ref(null);
const userSubmittedCode = ref('');
const showDiff = ref(false);
const syncRate = ref(0); // 실시간 싱크율
const isShaking = ref(false); // 타격감 트리거
const mermaidDefinition = ref(''); // Mermaid 도표 정의

const parsedExamples = computed(() => {
  if (!currentProblem.value || !currentProblem.value.examples) return [];
  return parseAllExamples(currentProblem.value.examples);
});

const handleEvaluation = async (userCode) => {
  userSubmittedCode.value = userCode;
  triggerImpact(); // 제출 시 강한 임팩트
  
  // 시뮬레이션
  setTimeout(() => {
    evaluationResult.value = {
      score: 85,
      status: 'SUCCESS',
      feedback: '전반적인 로직 구조가 파이썬스럽게(Pythonic) 잘 작성되었습니다. 특히 첫 번째 일치 항목 제거 후 루프를 중단하는 방식이 효율적입니다.',
      suggestions: [
        '변수명을 조금 더 직관적으로 지으면 읽기 좋습니다.',
        '스트링 인덱싱 대신 find/rfind 메서드를 활용해 보세요.'
      ]
    };
  }, 1500);
};

/**
 * [수정일: 2026-01-23]
 * [수정내용: 에디터 코드 변경 시 Mermaid 정의 갱신]
 */
const handleCodeChange = (newCode) => {
  mermaidDefinition.value = convertToMermaid(newCode);
};

/**
 * [수정일: 2026-01-23]
 * [수정내용: 게임 타격감을 위한 셰이크 효과]
 */
const triggerImpact = () => {
  isShaking.value = true;
  setTimeout(() => { isShaking.value = false; }, 150);
};

const syncStatusClass = computed(() => {
  if (syncRate.value >= 90) return 'text-emerald-400 drop-shadow-[0_0_8px_rgba(52,211,153,0.5)]';
  if (syncRate.value >= 50) return 'text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]';
  return 'text-slate-400';
});

onMounted(() => {
  if (!currentProblem.value) {
    store.setProblemById(11);
  }
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Orbitron:wght@400;900&display=swap');

.orbitron { font-family: 'Orbitron', sans-serif; }
.rajdhani { font-family: 'Rajdhani', sans-serif; }

.interactive-border {
  position: relative;
}
.interactive-border::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 3rem;
  padding: 1px;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.4), transparent 40%, transparent 60%, rgba(99, 102, 241, 0.4));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

/* 스캔라인 효과 */
.interactive-border::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
  background-size: 100% 4px, 3px 100%;
  pointer-events: none;
  z-index: 30;
  opacity: 0.1;
}

.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
.tech-pattern {
  background-image: radial-gradient(rgba(51, 65, 85, 0.3) 1px, transparent 1px);
  background-size: 30px 30px;
}

/* 타격감 효과 (Shake) */
.shake-active {
  animation: shake-anim 0.2s cubic-bezier(.36,.07,.19,.97) both;
}

@keyframes shake-anim {
  10%, 90% { transform: translate3d(-2px, 0, 2px); }
  20%, 80% { transform: translate3d(4px, 0, -2px); }
  30%, 50%, 70% { transform: translate3d(-6px, 0, 3px); }
  40%, 60% { transform: translate3d(6px, 0, -3px); }
}

:deep(.rajdhani) { font-family: 'Rajdhani', sans-serif; }
</style>
