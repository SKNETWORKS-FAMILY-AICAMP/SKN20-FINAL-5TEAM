<!--
  수정일자: 2026-02-23
  수정내용: VisionAnalysisReport 컴포넌트의 각 섹션 및 기능에 대한 상세 주석 추가.
            사용자의 비언어적 태도(시선, 자세, 표정) 분석 결과를 시각적으로 보여주는 UI 컴포넌트입니다.
-->
<template>
  <div class="vision-report-card mt-8">
    <!-- 헤더 섹션 -->
    <h3 class="section-title">태도 분석 결과</h3>

    <!-- 데이터 부족 경고 -->
    <div v-if="!hasData" class="mb-4 rounded-xl border border-amber-300 bg-amber-50 p-3">
      <p class="text-xs text-amber-700 font-medium">
        분석 데이터가 충분히 수집되지 않았습니다.
        <span v-if="analysis?.error" class="text-amber-800">({{ analysis.error }})</span>
      </p>
    </div>

    <!-- 주요 지표: 시선, 자세, 표정 -->
    <div class="metrics-panel">
      <!-- 시선 집중도 링 -->
      <div class="metric-item">
        <div class="relative w-28 h-28">
          <svg class="w-full h-full transform -rotate-90" viewBox="0 0 110 110">
            <circle cx="55" cy="55" r="45" stroke-width="10" fill="none"
              class="stroke-emerald-500"
              stroke-linecap="round"
              :stroke-dasharray="2 * Math.PI * 45"
              :stroke-dashoffset="2 * Math.PI * 45 * (1 - (analysis?.gazeScore || 0) / 100)"
              style="transition: stroke-dashoffset 1.2s cubic-bezier(0.16, 1, 0.3, 1); filter: drop-shadow(0 0 4px rgba(16,185,129,0.4))"
            />
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <span class="text-2xl font-black text-gray-900 lining-nums">{{ analysis?.gazeScore || 0 }}</span>
            <span class="text-[10px] text-emerald-600 font-bold mt-0.5">%</span>
          </div>
        </div>
        <div class="text-center">
          <p class="text-sm font-bold text-gray-700">시선 집중도</p>
          <p class="text-[10px] text-gray-400 mt-0.5">Gaze Focus</p>
        </div>
      </div>

      <!-- 자세 유지력 링 -->
      <div class="metric-item">
        <div class="relative w-28 h-28">
          <svg class="w-full h-full transform -rotate-90" viewBox="0 0 110 110">
            <circle cx="55" cy="55" r="45" stroke-width="10" fill="none"
              class="stroke-amber-500"
              stroke-linecap="round"
              :stroke-dasharray="2 * Math.PI * 45"
              :stroke-dashoffset="2 * Math.PI * 45 * (1 - (analysis?.poseScore || 0) / 100)"
              style="transition: stroke-dashoffset 1.2s cubic-bezier(0.16, 1, 0.3, 1); filter: drop-shadow(0 0 4px rgba(245,158,11,0.4))"
            />
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <span class="text-2xl font-black text-gray-900 lining-nums">{{ analysis?.poseScore || 0 }}</span>
            <span class="text-[10px] text-amber-600 font-bold mt-0.5">%</span>
          </div>
        </div>
        <div class="text-center">
          <p class="text-sm font-bold text-gray-700">자세 유지력</p>
          <p class="text-[10px] text-gray-400 mt-0.5">Posture</p>
        </div>
      </div>

      <!-- 표정 밸런스 -->
      <div class="metric-item">
        <div class="w-28 h-28 rounded-full border-2 border-indigo-200 flex items-center justify-center">
          <span class="text-5xl" role="img" :aria-label="dominantEmotion">
            {{ dominantEmotion === 'smile' ? '😊' : dominantEmotion === 'tension' ? '😰' : '😐' }}
          </span>
        </div>
        <div class="text-center">
          <p class="text-sm font-bold text-gray-700">표정 밸런스</p>
          <p class="text-[10px] font-bold mt-0.5"
            :class="dominantEmotion === 'smile' ? 'text-indigo-500' : dominantEmotion === 'tension' ? 'text-red-500' : 'text-gray-400'">
            {{ dominantEmotion === 'smile' ? `미소 ${emotionsPercent.smile}%` : dominantEmotion === 'tension' ? `긴장 ${emotionsPercent.tension}%` : `무표정 ${emotionsPercent.neutral}%` }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

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

const emotionsPercent = computed(() => {
  const e = props.analysis?.emotions || { smile: 0, tension: 0, neutral: 0 };
  const total = (e.smile + e.tension + e.neutral) || 1;
  const smilePct = Math.round((e.smile / total) * 100);
  const tensionPct = Math.round((e.tension / total) * 100);
  const isZero = (e.smile === 0 && e.tension === 0 && e.neutral === 0);
  const neutralPct = isZero ? 0 : Math.max(0, 100 - smilePct - tensionPct);
  return { smile: smilePct, tension: tensionPct, neutral: neutralPct };
});

const dominantEmotion = computed(() => {
  const p = emotionsPercent.value;
  if (p.smile === 0 && p.tension === 0 && p.neutral === 0) return 'neutral';
  if (p.smile >= p.neutral && p.smile >= p.tension) return 'smile';
  if (p.tension >= p.neutral) return 'tension';
  return 'neutral';
});

const hasData = computed(() => (props.analysis?.sampleCount || 0) > 0);
</script>

<style scoped>
.vision-report-card {
  background: white;
  border-radius: 12px;
  padding: 20px 24px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 16px;
  animation: slideUpFade 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.section-title {
  font-family: 'Outfit', sans-serif;
  font-size: 15px;
  font-weight: 700;
  color: #1f2937;
  -webkit-text-fill-color: #1f2937;
  background: none;
  -webkit-background-clip: unset;
  background-clip: unset;
  margin-bottom: 14px;
  padding-left: 10px;
  border-left: 3px solid #6366f1;
}

.metrics-panel {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 20px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  background: none;
  padding: 0;
}

@keyframes slideUpFade {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.lining-nums {
  font-variant-numeric: tabular-nums;
}
</style>
