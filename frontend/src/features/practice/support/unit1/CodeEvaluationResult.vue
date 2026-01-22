<template>
  <div v-if="result" class="evaluation-result mt-6 animate-in slide-in-from-top-4 duration-500">
    <!-- 
      [수정일: 2026-01-23]
      [수정내용: AI 채점 결과를 보여주는 UI 컴포넌트 구현]
    -->
    <div class="bg-slate-900 border border-slate-700 rounded-2xl overflow-hidden shadow-2xl">
      <div :class="['p-4 flex items-center justify-between', scoreColor]">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center font-black">
            {{ result.score }}
          </div>
          <div>
            <h4 class="font-bold text-white">AI 채점 리포트</h4>
            <p class="text-[10px] opacity-70 uppercase tracking-widest font-mono">Neural_Analysis_Complete</p>
          </div>
        </div>
        <div class="text-xs font-black px-3 py-1 bg-black/30 rounded-full">
          {{ result.status }}
        </div>
      </div>

      <div class="p-6 space-y-6">
        <!-- 총평 -->
        <section>
          <div class="flex items-center gap-2 text-indigo-400 mb-2">
            <span class="text-[10px] font-black uppercase tracking-tighter">Feedback</span>
            <div class="flex-1 h-[1px] bg-slate-800"></div>
          </div>
          <p class="text-sm text-slate-300 leading-relaxed">{{ result.feedback }}</p>
        </section>

        <!-- 개선 사항 -->
        <section v-if="result.suggestions && result.suggestions.length">
          <div class="flex items-center gap-2 text-rose-400 mb-2">
            <span class="text-[10px] font-black uppercase tracking-tighter">Advice</span>
            <div class="flex-1 h-[1px] bg-slate-800"></div>
          </div>
          <ul class="space-y-2">
            <li v-for="(suggestion, i) in result.suggestions" :key="i" class="text-xs text-slate-400 flex gap-2">
              <span class="text-rose-500">•</span> {{ suggestion }}
            </li>
          </ul>
        </section>

        <!-- 정답 확인 버튼 -->
        <div class="pt-4 border-t border-slate-800 flex justify-end">
          <button class="text-xs font-bold text-slate-500 hover:text-white transition-colors">
            정답 코드와 비교하기 (Diff View) →
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  result: {
    type: Object,
    default: null
  }
});

const scoreColor = computed(() => {
  const score = props.result?.score || 0;
  if (score >= 80) return 'bg-emerald-600';
  if (score >= 50) return 'bg-amber-600';
  return 'bg-rose-600';
});
</script>
