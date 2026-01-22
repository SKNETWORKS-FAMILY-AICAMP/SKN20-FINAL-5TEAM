<template>
  <div class="parsons-puzzle h-full flex flex-col relative">
    <!-- 
      [수정일: 2026-01-23]
      [수정내용: 디자인 고도화 및 데이터 바인딩 버그 수정 (가독성 개선)]
    -->
    <div class="mb-8">
      <h3 class="text-sm font-black text-cyan-400 tracking-[0.4em] uppercase mb-3 flex items-center gap-3 orbitron">
        <span class="w-2 h-2 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_10px_#22d3ee]"></span>
        Logic_Grid_Reconstruction
      </h3>
      <p class="text-xs text-slate-500 font-bold uppercase tracking-widest rajdhani">블록을 재배열하여 논리적 무결성을 확보하십시오.</p>
    </div>

    <!-- 퍼즐 컨테이너 -->
    <div class="puzzle-container flex-1 space-y-3 custom-scrollbar overflow-y-auto pr-2 pb-20">
      <div
        v-for="(block, index) in blocks"
        :key="block.id"
        draggable="true"
        @dragstart="onDragStart($event, index)"
        @dragover.prevent
        @drop="onDrop($event, index)"
        class="puzzle-block group relative p-4 bg-slate-900/60 border border-slate-800/80 rounded-2xl cursor-move hover:border-cyan-500/50 hover:bg-slate-800/80 transition-all active:scale-[0.98] drop-shadow-sm"
        :class="{ 'match-hint': block.originalIndex === index && resultMessage }"
      >
        <!-- 인덱스 표시 -->
        <span class="absolute left-4 top-1/2 -translate-y-1/2 text-[10px] font-black text-slate-700 group-hover:text-cyan-500 transition-colors">
          {{ (index + 1).toString().padStart(2, '0') }}
        </span>
        
        <!-- 텍스트 내용 -->
        <div class="ml-12 font-mono text-base leading-relaxed text-slate-200 group-hover:text-white transition-colors">
          {{ block.text }}
        </div>

        <!-- 데코레이션 -->
        <div class="absolute right-4 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
          <div class="flex gap-1">
            <div class="w-1 h-1 rounded-full bg-cyan-500"></div>
            <div class="w-1 h-1 rounded-full bg-cyan-500/50"></div>
          </div>
        </div>
      </div>

      <!-- 데이터 없을 때 표시 -->
      <div v-if="blocks.length === 0" class="h-full flex items-center justify-center text-slate-700 font-mono text-[10px] uppercase tracking-widest">
        Waiting_For_Neural_Data...
      </div>
    </div>

    <!-- 푸팅 액션 -->
    <div class="absolute bottom-0 right-0 left-0 p-6 bg-gradient-to-t from-[#080c14] via-[#080c14]/90 to-transparent flex justify-end">
      <button 
        @click="checkAnswer"
        class="group relative px-10 py-3 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-black text-[11px] tracking-widest uppercase rounded-xl transition-all shadow-[0_0_20px_rgba(6,182,212,0.2)] active:scale-95"
      >
        Verify_Sequence
        <div class="absolute inset-0 border border-white/20 rounded-xl pointer-events-none"></div>
      </button>
    </div>

    <!-- 결과 알림 (Floating 모드로 변경) -->
    <Transition name="slide-up">
      <div v-if="resultMessage" :class="['absolute top-4 right-4 p-4 rounded-2xl border backdrop-blur-xl shadow-2xl z-50 flex items-center gap-4', isCorrect ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400' : 'bg-rose-500/10 border-rose-500/40 text-rose-400']">
        <div class="w-8 h-8 rounded-full flex items-center justify-center bg-current/10">
          <component :is="isCorrect ? 'CheckCircle2' : 'TriangleAlert'" class="w-4 h-4" />
        </div>
        <div class="flex flex-col">
          <span class="text-[10px] font-black uppercase tracking-widest">{{ isCorrect ? 'Sync_Complete' : 'Sync_Error' }}</span>
          <span class="text-xs font-bold">{{ resultMessage }}</span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { storeToRefs } from 'pinia';
// 2026-01-23: support/unit1 폴더 구조에 맞춘 상대 경로 수정
import { useProblemStore } from '../../../../stores/useProblemStore';
import { CheckCircle2, TriangleAlert } from 'lucide-vue-next';

const store = useProblemStore();
const { currentProblem } = storeToRefs(store);

const emit = defineEmits(['impact']); // 타격감 이벤트

const blocks = ref([]);
const resultMessage = ref('');
const isCorrect = ref(false);

const onDragStart = (event, index) => {
  event.dataTransfer.setData('sourceIndex', index);
  event.dataTransfer.effectAllowed = 'move';
};

const onDrop = (event, targetIndex) => {
  const sourceIndex = event.dataTransfer.getData('sourceIndex');
  if (sourceIndex === '') return;
  
  const moveIndex = parseInt(sourceIndex);
  if (moveIndex === targetIndex) return;
  
  const items = [...blocks.value];
  const [removed] = items.splice(moveIndex, 1);
  items.splice(targetIndex, 0, removed);
  blocks.value = items;
  resultMessage.value = '';
  
  // 2026-01-23: 드롭 시 타격감 이벤트 발생
  emit('impact');
};

const checkAnswer = () => {
  isCorrect.value = store.validatePuzzle(blocks.value);
  resultMessage.value = isCorrect.value 
    ? '정답입니다! 다음 미션 준비가 완료되었습니다.' 
    : '논리 구조가 일치하지 않습니다. 다시 시도해 주세요.';
  
  setTimeout(() => { resultMessage.value = ''; }, 4000);
};

// 데이터 로드 보장 로직
const initPuzzle = () => {
  if (currentProblem.value) {
    blocks.value = store.shufflePseudocode();
  }
};

onMounted(initPuzzle);
watch(currentProblem, initPuzzle, { deep: true, immediate: true });
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }

.puzzle-block:hover {
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.1);
  transform: translateY(-2px);
}

/* 퍼즐 맞춤 힌트 효과 */
.match-hint {
  border-color: rgba(16, 185, 129, 0.4) !important;
  background-color: rgba(16, 185, 129, 0.05) !important;
  box-shadow: 0 0 15px rgba(16, 185, 129, 0.1);
}

.slide-up-enter-active, .slide-up-leave-active { transition: all 0.4s ease; }
.slide-up-enter-from { opacity: 0; transform: translateY(-20px) scale(0.9); }
.slide-up-leave-to { opacity: 0; transform: translateY(-20px) scale(0.9); }
</style>
