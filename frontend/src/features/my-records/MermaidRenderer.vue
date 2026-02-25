<template>
  <div class="mermaid-renderer-wrapper" :id="containerId">
    <div v-if="isLoading" class="mermaid-loading">
      <div class="spinner"></div>
      <span>Rendering Diagram...</span>
    </div>
    <div ref="mermaidContainer" class="mermaid-target"></div>
    <div v-if="error" class="mermaid-error">
      <p>⚠️ Diagram Rendering Error</p>
      <small>{{ error }}</small>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import mermaid from 'mermaid';

const props = defineProps({
  code: {
    type: String,
    required: true
  },
  id: {
    type: String,
    default: () => `mermaid-${Math.random().toString(36).substr(2, 9)}`
  },
  theme: {
    type: String,
    default: 'dark'
  }
});

const mermaidContainer = ref(null);
const isLoading = ref(true);
const error = ref(null);
const containerId = ref(props.id);

// Mermaid 초기화 설정
const initializeMermaid = () => {
  mermaid.initialize({
    startOnLoad: false,
    theme: props.theme,
    securityLevel: 'loose',
    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
    themeVariables: {
      primaryColor: '#bc13fe',
      primaryTextColor: '#e8eaed',
      primaryBorderColor: '#bc13fe',
      lineColor: '#00f3ff',
      secondaryColor: '#ff00ff',
      tertiaryColor: '#00f3ff',
      background: 'transparent',
      mainBkg: 'rgba(255, 255, 255, 0.05)',
      textColor: '#e8eaed'
    }
  });
};

const renderDiagram = async () => {
  if (!props.code || !mermaidContainer.value) return;
  
  isLoading.value = true;
  error.value = null;
  
  try {
    // 렌더링 전 컨테이너 비우기
    mermaidContainer.value.innerHTML = '';
    
    // 고유 ID 생성 (DOM 충돌 방지)
    const renderId = `render-${props.id}-${Date.now()}`;
    
    // Mermaid 렌더링 호출
    const { svg } = await mermaid.render(renderId, props.code);
    
    if (mermaidContainer.value) {
      mermaidContainer.value.innerHTML = svg;
      
      // SVG 스타일 조정 (반응형)
      const svgElement = mermaidContainer.value.querySelector('svg');
      if (svgElement) {
        svgElement.style.maxWidth = '100%';
        svgElement.style.height = 'auto';
        svgElement.style.display = 'block';
        svgElement.style.margin = '0 auto';
      }
    }
  } catch (err) {
    console.error('Mermaid Render Exception:', err);
    error.value = err.message || 'Unknown error occurred during rendering.';
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  initializeMermaid();
  renderDiagram();
});

// 코드가 변경되면 다시 렌더링
watch(() => props.code, () => {
  nextTick(renderDiagram);
});
</script>

<style scoped>
.mermaid-renderer-wrapper {
  width: 100%;
  min-height: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
}

.mermaid-target {
  width: 100%;
  overflow-x: auto;
}

.mermaid-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: #64748b;
  font-size: 0.85rem;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(188, 19, 254, 0.1);
  border-top-color: #bc13fe;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.mermaid-error {
  width: 100%;
  padding: 1rem;
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.3);
  border-radius: 6px;
  color: #ff6b6b;
  font-size: 0.8rem;
  text-align: center;
}

.mermaid-error p {
  font-weight: 700;
  margin-bottom: 4px;
}

.mermaid-error small {
  opacity: 0.8;
  word-break: break-all;
}

/* Mermaid SVG 내부 텍스트 스타일 보정 */
:deep(.mermaid svg) {
  font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
}
</style>
