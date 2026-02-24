<!-- 
  수정일자: 2026-02-23
  수정내용: VisionAnalysisReport 컴포넌트의 각 섹션 및 기능에 대한 상세 주석 추가.
            사용자의 비언어적 태도(시선, 자세, 표정) 분석 결과를 시각적으로 보여주는 UI 컴포넌트입니다.
-->
<template>
  <div class="vision-report-v4 mt-8 p-8 bg-slate-900 border-2 border-slate-700/50 rounded-3xl shadow-2xl overflow-hidden relative">
    <!-- 배경 장식: 컴포넌트 모서리의 시각적 디자인 포인트 (그라데이션 원형 블러) -->
    <div class="absolute -top-24 -right-24 w-64 h-64 bg-indigo-600/10 blur-[100px] rounded-full"></div>
    <div class="absolute -bottom-24 -left-24 w-64 h-64 bg-emerald-600/10 blur-[100px] rounded-full"></div>

    <!-- 헤더 섹션: 리포트 타이틀 및 대표 아이콘 표시 영역 -->
    <div class="flex items-center gap-4 mb-8 relative z-10">
      <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
        <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
        </svg>
      </div>
      <div>
        <h3 class="text-white font-extrabold text-2xl tracking-tight">AI 비언어 태도 분석 결과</h3>
        <p class="text-indigo-300/80 text-xs font-semibold uppercase tracking-widest mt-1">Non-verbal Interaction Behavioral Analysis</p>
      </div>
    </div>

    <!-- 데이터 부족 경고: 비전 분석 샘플수(sampleCount)가 충분하지 않을 때 표시되는 알림 -->
    <div v-if="!hasData" class="mb-6 relative z-10 rounded-xl border border-amber-400/30 bg-amber-500/10 p-3">
      <p class="text-xs text-amber-200 font-medium">
        분석 데이터가 충분히 수집되지 않았습니다.
        <span v-if="analysis?.error" class="text-amber-100">({{ analysis.error }})</span>
      </p>
    </div>

    <!-- 1. 주요 지표 섹션: 종합 안정성, 시선, 자세, 표정에 대한 주요 분석 수치를 대시보드 형태로 보여주는 영역 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8 relative z-10">
      <!-- 종합 태도 안정성: 시선 점수와 자세 점수의 평균값을 도넛 형태의 원형 프로그레스 바로 시각화 -->
      <div class="lg:col-span-1 flex flex-col items-center justify-center p-8 bg-white/5 rounded-3xl border border-white/10 backdrop-blur-sm">
        <div class="relative w-40 h-40 flex items-center justify-center mb-6">
          <svg class="w-full h-full transform -rotate-90">
            <circle cx="80" cy="80" r="72" stroke="currentColor" stroke-width="12" fill="transparent" class="text-slate-800" />
            <circle cx="80" cy="80" r="72" stroke="currentColor" stroke-width="12" fill="transparent" 
              class="text-indigo-400 drop-shadow-[0_0_8px_rgba(129,140,248,0.5)]" 
              :stroke-dasharray="2 * Math.PI * 72"
              :stroke-dashoffset="2 * Math.PI * 72 * (1 - totalStability / 100)"
              stroke-linecap="round"
            />
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <span class="text-5xl font-black text-white lining-nums">{{ totalStability }}</span>
            <span class="text-[10px] text-indigo-300 font-black tracking-[0.2em] uppercase mt-1">Stability</span>
          </div>
        </div>
        <div class="text-center">
           <p class="text-lg font-bold text-white mb-1">종합 안정성</p>
           <p class="text-xs text-indigo-300/60 font-medium">시선 및 자세 정면 유지 비율</p>
        </div>
      </div>

      <!-- 세부 바 지표: 시선 집중도, 자세 유지력, 표정 밸런스를 가로형 바 차트(Bar Chart)로 상세히 표시하는 영역 -->
      <div class="lg:col-span-2 space-y-6 flex flex-col justify-center p-8 bg-white/5 rounded-3xl border border-white/10 backdrop-blur-sm">
        <!-- 시선 집중도: 사용자가 화면 중앙(카메라 렌즈 방향)을 얼마나 지속적으로 응시했는지 나타내는 백분율 지표 -->
        <div class="space-y-3">
          <div class="flex justify-between items-end">
            <div class="flex items-center gap-2">
               <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
               <span class="text-gray-300 text-sm font-bold">시선 집중도 (Gaze Focus)</span>
            </div>
            <span class="text-2xl font-black text-white lining-nums">{{ analysis?.gazeScore || 0 }}<span class="text-sm font-normal text-gray-400 ml-0.5">%</span></span>
          </div>
          <div class="h-3 w-full bg-slate-800 rounded-full overflow-hidden p-0.5">
            <div class="h-full bg-gradient-to-r from-emerald-600 to-emerald-400 rounded-full transition-all duration-1000 ease-out" :style="{ width: (analysis?.gazeScore || 0) + '%' }"></div>
          </div>
        </div>

        <!-- 자세 안정성: 머리의 기울기나 신체의 움직임을 분석해 올바른 자세를 유지한 비율을 나타내는 지표 -->
        <div class="space-y-3">
          <div class="flex justify-between items-end">
            <div class="flex items-center gap-2">
               <span class="w-2 h-2 rounded-full bg-amber-400"></span>
               <span class="text-gray-300 text-sm font-bold">자세 유지력 (Posture)</span>
            </div>
            <span class="text-2xl font-black text-white lining-nums">{{ analysis?.poseScore || 0 }}<span class="text-sm font-normal text-gray-400 ml-0.5">%</span></span>
          </div>
          <div class="h-3 w-full bg-slate-800 rounded-full overflow-hidden p-0.5">
            <div class="h-full bg-gradient-to-r from-amber-600 to-amber-400 rounded-full transition-all duration-1000 ease-out" :style="{ width: (analysis?.poseScore || 0) + '%' }"></div>
          </div>
        </div>

        <!-- 감정 분석 (표정 밸런스): 사용자의 안면 근육 분석을 통해 미소, 무표정, 긴장의 변화를 3색 바 차트로 시각화 -->
        <div class="space-y-3">
          <div class="flex justify-between items-end">
            <div class="flex items-center gap-2">
               <span class="w-2 h-2 rounded-full bg-indigo-400"></span>
               <span class="text-gray-300 text-sm font-bold">표정 밸런스 (Emotions)</span>
            </div>
            <div class="flex gap-1 items-baseline">
                <span class="text-lg font-bold text-indigo-400">{{ emotionsPercent.smile }}%</span>
                <span class="text-xs text-gray-500 font-medium">Positive</span>
            </div>
          </div>
          <div class="h-3 w-full bg-slate-800 rounded-full overflow-hidden flex p-0.5 shadow-inner">
            <div class="h-full bg-indigo-500/80 transition-all duration-700" :style="{ width: emotionsPercent.smile + '%' }"></div>
            <div class="h-full bg-slate-600 transition-all duration-700" :style="{ width: emotionsPercent.neutral + '%' }"></div>
            <div class="h-full bg-red-500/80 transition-all duration-700" :style="{ width: emotionsPercent.tension + '%' }"></div>
          </div>
          <div class="flex justify-between text-[10px] items-center text-gray-400 font-bold px-1">
             <span class="flex items-center gap-1.5"><i class="w-2 h-2 rounded-full bg-indigo-500"></i> 미소</span>
             <span class="flex items-center gap-1.5"><i class="w-2 h-2 rounded-full bg-slate-600"></i> 무표정</span>
             <span class="flex items-center gap-1.5"><i class="w-2 h-2 rounded-full bg-red-500"></i> 긴장</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. 감지 로그 섹션: 면접 도중 발생한 주요 이벤트(시선 이탈, 자세 흐트러짐 등)를 시간 순으로 표시하는 타임라인 -->
    <div class="bg-black/30 rounded-2xl p-6 border border-white/5 relative z-10">
       <div class="flex items-center justify-between mb-4">
          <h4 class="text-xs font-black text-indigo-300 uppercase tracking-[0.2em]">Behavioral Logs</h4>
          <span class="text-[10px] text-gray-500 font-medium">총 {{ analysis?.events?.length || 0 }}건 감지</span>
       </div>
       <ul v-if="analysis?.events?.length" class="space-y-3">
          <li v-for="(evt, idx) in analysis.events.slice(-4)" :key="idx" 
            class="text-xs text-gray-300 flex items-start gap-3 p-3 bg-white/5 rounded-xl border border-white/5 hover:bg-white/10 transition-colors">
             <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-1.5 flex-shrink-0 animate-pulse"></span>
             <span class="leading-relaxed">{{ evt }}</span>
          </li>
       </ul>
       <div v-else class="py-6 flex flex-col items-center justify-center opacity-40">
          <p class="text-xs text-gray-500 italic">특이 사항이 감지되지 않았습니다. 바른 태도를 잘 유지하셨습니다.</p>
       </div>
    </div>
  </div>
</template>

<script setup>
// 수정일자: 2026-02-23
// 수정내용: Props 정의 및 Computed 속성들이 어떻게 비전 분석 데이터를 계산하는지에 대한 주석 추가.
import { computed } from 'vue';

// 부모 컴포넌트로부터 전달받는 AI 비전 분석 결과 데이터 객체 (기본값 구성)
const props = defineProps({
  analysis: {
    type: Object,
    default: () => ({ 
        gazeScore: 0, 
        poseScore: 0, 
        emotions: { smile: 0, tension: 0, neutral: 0 },
        events: []
    })
  }
});

// 종합 안정성 계산: 시선 집중도(gazeScore)와 자세 유지력(poseScore)의 평균값을 산출하여 정수로 반환
const totalStability = computed(() => {
  const g = props.analysis?.gazeScore || 0;
  const p = props.analysis?.poseScore || 0;
  return Math.round((g + p) / 2);
});

// 표정 분석 결과 백분율 계산: 미소, 무표정, 긴장 점수의 총합을 100% 비율로 변환
const emotionsPercent = computed(() => {
  const e = props.analysis?.emotions || { smile: 0, tension: 0, neutral: 0 };
  const total = (e.smile + e.tension + e.neutral) || 1;
  
  // [수정일: 2026-02-24] 퍼센트 합계 100% 초과 방지 (각자 독립적으로 반올림하면 99%나 101%가 될 수 있음)
  const smilePct = Math.round((e.smile / total) * 100);
  const tensionPct = Math.round((e.tension / total) * 100);
  
  // 데이터가 아예 없는 초기상태(total이 강제 1인 경우)가 아니면 무표정(neutral)을 나머지 값으로 채움
  const isZero = (e.smile === 0 && e.tension === 0 && e.neutral === 0);
  const neutralPct = isZero ? 0 : Math.max(0, 100 - smilePct - tensionPct);

  return {
    smile: smilePct,
    tension: tensionPct,
    neutral: neutralPct
  };
});

// 데이터 유무 판단: 전달받은 샘플 카운트(분석 프레임 수)가 0 초과인지 확인하여 렌더링 여부 결정에 사용
const hasData = computed(() => (props.analysis?.sampleCount || 0) > 0);
</script>

<style scoped>
.vision-report-v4 {
  animation: slideUpFade 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUpFade {
  from { opacity: 0; transform: translateY(30px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.lining-nums {
  font-variant-numeric: tabular-nums;
}
</style>
