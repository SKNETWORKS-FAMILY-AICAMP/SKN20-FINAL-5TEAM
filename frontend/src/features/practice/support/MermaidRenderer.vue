<template>
  <div class="mermaid-renderer h-64 bg-slate-950/50 border border-slate-800/50 rounded-[2.5rem] overflow-hidden relative group">
    <!-- 
      [수정일: 2026-01-23]
      [수정내용: Mermaid.js를 활용한 실시간 로직 시각화 컴포넌트]
    -->
    <div class="absolute top-4 left-6 flex items-center gap-2 z-10">
      <div class="w-2 h-2 bg-indigo-500 rounded-full animate-pulse shadow-[0_0_8px_#6366f1]"></div>
      <span class="text-[9px] text-slate-500 font-black tracking-[0.3em] uppercase orbitron">Logic_Flow_Live</span>
    </div>

    <div ref="mermaidTarget" class="mermaid-container h-full flex items-center justify-center p-4">
      <!-- 렌더링된 SVG가 여기에 삽입됨 -->
      <div v-if="!definition" class="text-slate-700 text-[10px] orbitron animate-pulse">
        WAITING_FOR_DATA_STREAM...
      </div>
    </div>

    <!-- 배경 그리드 데코레이션 -->
    <div class="absolute inset-0 opacity-[0.03] pointer-events-none tech-pattern"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import mermaid from 'mermaid';

const props = defineProps({
  definition: {
    type: String,
    required: true
  }
});

const mermaidTarget = ref(null);

// Mermaid 초기화 설정
mermaid.initialize({
  startOnLoad: false,
  theme: 'base',
  themeVariables: {
    primaryColor: '#1e1b4b',
    primaryTextColor: '#fff',
    primaryBorderColor: '#38bdf8',
    lineColor: '#334155',
    secondaryColor: '#020617',
    tertiaryColor: '#0f172a'
  },
  flowchart: {
    curve: 'basis',
    useMaxWidth: true,
    htmlLabels: true
  }
});

const renderDiagram = async () => {
  if (!props.definition || !mermaidTarget.value) return;

  try {
    const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
    const { svg } = await mermaid.render(id, props.definition);
    mermaidTarget.value.innerHTML = svg;
    
    // SVG 스타일 보정 (네온 효과 등)
    const svgElement = mermaidTarget.value.querySelector('svg');
    if (svgElement) {
      svgElement.style.maxWidth = '100%';
      svgElement.style.height = 'auto';
      svgElement.style.filter = 'drop-shadow(0 0 2px rgba(56, 189, 248, 0.2))';
    }
  } catch (error) {
    console.error('Mermaid render error:', error);
  }
};

onMounted(() => {
  renderDiagram();
});

watch(() => props.definition, () => {
  nextTick(renderDiagram);
});
</script>

<style scoped>
.tech-pattern {
  background-image: radial-gradient(rgba(51, 65, 85, 0.4) 1px, transparent 1px);
  background-size: 15px 15px;
}

:deep(.node rect), :deep(.node circle), :deep(.node polygon) {
  stroke-width: 1.5px !important;
}

:deep(.edgePath path) {
  stroke: #475569 !important;
  stroke-width: 1.5px !important;
}

:deep(.label text) {
  font-family: 'Rajdhani', sans-serif !important;
  font-weight: 600 !important;
}
</style>
