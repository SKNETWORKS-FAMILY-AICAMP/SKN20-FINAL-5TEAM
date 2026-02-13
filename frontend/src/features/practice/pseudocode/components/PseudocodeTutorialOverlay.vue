<template>
  <Teleport to="body">
    <div class="tutorial-overlay" @click.self="handleOverlayClick">
      <!-- 하이라이트 컷아웃 -->
      <div
        class="tutorial-highlight"
        :style="highlightStyle"
      ></div>

      <!-- 설명 카드 -->
      <div class="tutorial-card" :style="cardStyle">
        <div class="card-header">
          <span class="step-indicator">{{ currentStep + 1 }} / {{ steps.length }}</span>
          <span class="step-title">{{ steps[currentStep].title }}</span>
        </div>
        <p class="card-description">{{ steps[currentStep].description }}</p>
        <div class="step-dots">
          <span
            v-for="(_, idx) in steps"
            :key="idx"
            class="dot"
            :class="{ active: idx === currentStep, done: idx < currentStep }"
          ></span>
        </div>
        <div class="card-actions">
          <button class="btn-quit" @click="emit('quit')">EXIT PRACTICE</button>
          <div class="main-nav">
            <button class="btn-skip" @click="skip">SKIP</button>
            <button class="btn-next" @click="next">
              {{ currentStep === steps.length - 1 ? 'FINISH' : 'NEXT' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
/* 
  수정일: 2026-02-14
  수정 내용: 의사코드 실습용 튜토리얼 오버레이 컴포넌트 생성
*/
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue';

const emit = defineEmits(['complete', 'skip', 'change-phase']);

const STEPS = [
  {
    targetPhase: 'DIAGNOSTIC_1',
    selector: '.choice-interaction-area',
    title: 'PHASE 01: CONCEPT CHECK',
    description: '설계에 들어가기 앞서 핵심 원칙을 점검합니다. 상단의 질문을 읽고 아래의 옵션 중 정답이라고 생각하는 것을 클릭하세요.',
    cardPosition: 'left'
  },
  {
    targetPhase: 'DIAGNOSTIC_1',
    selector: '.options-list',
    title: 'CHOICE INTERACTION',
    description: '각 옵션을 클릭하여 즉시 답변을 제출할 수 있습니다. 정답 여부에 따라 보너스 점수나 피드백을 받게 됩니다.',
    cardPosition: 'left'
  },
  {
    targetPhase: 'PSEUDO_WRITE',
    selector: '.mission-instruction-compact',
    title: 'PHASE 02: MISSION BRIEF',
    description: '해결해야 할 문제 시나리오와 필수 포함 조건(Constraint)을 반드시 숙지하세요. 설계의 핵심 기준이 됩니다.',
    cardPosition: 'bottom'
  },
  {
    targetPhase: 'PSEUDO_WRITE',
    selector: '.monaco-wrapper',
    title: 'ARCHITECTURE EDITOR',
    description: '설계도를 작성하는 공간입니다. 한글 의사코드와 파이썬 키워드를 사용하여 논리적인 흐름을 구성하세요.',
    cardPosition: 'bottom'
  },
  {
    targetPhase: 'PSEUDO_WRITE',
    selector: '.rule-checklist-bar',
    title: 'REAL-TIME INTEGRITY CHECK',
    description: '작성 중인 코드에 세 가지 핵심 원칙(격리, 기준점, 일관성)이 반영되었는지 실시간으로 감지하여 표시합니다.',
    cardPosition: 'top'
  },
  {
    targetPhase: 'PSEUDO_WRITE',
    selector: '.btn-hint-toggle',
    title: 'DUCK_TIP HINT',
    description: '설계가 막힌다면 힌트 버튼을 눌러 실시간 조언을 받으세요. 오리 형사가 여러분의 설계를 분석해 도와줍니다.',
    cardPosition: 'top'
  },
  {
    targetPhase: 'PYTHON_VISUALIZATION',
    selector: '.pseudo-panel',
    title: 'INPUT LOGIC VIEW',
    description: '여러분이 설계한 의사코드가 최종적으로 어떻게 정리되었는지 확인하는 공간입니다.',
    cardPosition: 'right'
  },
  {
    targetPhase: 'PYTHON_VISUALIZATION',
    selector: '.python-panel',
    title: 'AI IMPLEMENTATION',
    description: '아키텍트가 여러분의 논리를 바탕으로 구현한 실제 Python 코드입니다. 논리적 매핑 과정을 대조하며 학습하세요.',
    cardPosition: 'left'
  },
  {
    targetPhase: 'PYTHON_VISUALIZATION',
    selector: '.question-interactive-box',
    title: 'DEEP DIVE CHALLENGE',
    description: '설계 완료 후, 예외 상황이나 심화 기술에 대한 AI의 질문에 답하며 아키텍처 역량을 한층 더 끌어올리세요.',
    cardPosition: 'top'
  },
  {
    targetPhase: 'EVALUATION',
    selector: '.ai-analysis-simulation',
    title: 'AI ANALYSIS SIMULATION',
    description: '여러분의 설계가 제출되었습니다! AI 아키텍트가 전체적인 논리 정합성과 데이터 누수 방지 원칙 준수 여부를 정밀 분석하는 과정입니다.',
    cardPosition: 'top'
  },
  {
    targetPhase: 'EVALUATION',
    selector: '.report-billboard-premium',
    title: 'PHASE 03: ARCHITECT STATUS',
    description: '분석이 완료되었습니다! 여러분의 총점과 최종적인 아키텍처 등급(A+ ~ F)을 한눈에 확인하세요.',
    cardPosition: 'bottom'
  },
  {
    targetPhase: 'EVALUATION',
    selector: '.radar-container-neo',
    title: '5D BALANCE SCAN',
    description: '디자인, 일관성, 구현, 예외처리, 추상화의 5가지 지표를 시각화하여 여러분의 설계 강점과 약점을 입체적으로 분석합니다.',
    cardPosition: 'right'
  },
  {
    targetPhase: 'EVALUATION',
    selector: '.hub-cell.metrics-matrix',
    title: 'DIMENSION MATRIX',
    description: '각 지표별 상세 점수와 성취도를 수치로 명확하게 확인하고 어떤 부분이 부족한지 정밀하게 체크하세요.',
    cardPosition: 'left'
  },
  {
    targetPhase: 'EVALUATION',
    selector: '.expert-section-neo',
    title: 'AI SENIOR VERDICT',
    description: 'AI 시니어 아키텍트의 피드백입니다. 구체적인 설계 평가와 실무에서 바로 쓸 수 있는 원포인트 레슨을 제공합니다.',
    cardPosition: 'top'
  },
  {
    targetPhase: 'EVALUATION',
    selector: '.pathway-section-neo',
    title: 'CONTINUOUS LEARNING',
    description: '부족한 부분을 채워줄 맞춤형 학습 경로를 추천합니다. 영상 강의를 통해 아키텍처 실무 역량을 더욱 강화하세요.',
    cardPosition: 'top'
  }
];

const currentStep = ref(0);
const steps = STEPS;
const targetRect = ref(null);
const cardStyle = ref({});

const highlightStyle = computed(() => {
  if (!targetRect.value) {
    return { display: 'none' };
  }
  const padding = 6;
  const r = targetRect.value;
  return {
    top: `${r.top - padding}px`,
    left: `${r.left - padding}px`,
    width: `${r.width + padding * 2}px`,
    height: `${r.height + padding * 2}px`
  };
});

const computeCardStyle = (rect, position) => {
  const cardWidth = 340;
  const cardGap = 20;
  const style = { width: `${cardWidth}px` };
  const vw = window.innerWidth;
  const vh = window.innerHeight;

  switch (position) {
    case 'right': {
      let left = rect.right + cardGap;
      if (left + cardWidth > vw - 16) {
        left = rect.left - cardWidth - cardGap;
      }
      let top = rect.top + rect.height / 2 - 100;
      top = Math.max(16, Math.min(top, vh - 260));
      style.left = `${left}px`;
      style.top = `${top}px`;
      break;
    }
    case 'left': {
      let left = rect.left - cardWidth - cardGap;
      if (left < 16) {
        left = rect.right + cardGap;
      }
      let top = rect.top + rect.height / 2 - 100;
      top = Math.max(16, Math.min(top, vh - 260));
      style.left = `${left}px`;
      style.top = `${top}px`;
      break;
    }
    case 'bottom': {
      let top = rect.bottom + cardGap;
      if (top + 220 > vh - 16) {
        top = rect.top - 220 - cardGap;
      }
      let left = rect.left + rect.width / 2 - cardWidth / 2;
      left = Math.max(16, Math.min(left, vw - cardWidth - 16));
      style.left = `${left}px`;
      style.top = `${top}px`;
      break;
    }
    case 'top': {
      let top = rect.top - 220 - cardGap;
      if (top < 16) {
        top = rect.bottom + cardGap;
      }
      let left = rect.left + rect.width / 2 - cardWidth / 2;
      left = Math.max(16, Math.min(left, vw - cardWidth - 16));
      style.left = `${left}px`;
      style.top = `${top}px`;
      break;
    }
  }

  return style;
};

const updatePosition = () => {
  const step = steps[currentStep.value];
  
  // 페이즈 전환 요청
  if (step.targetPhase) {
    emit('change-phase', step.targetPhase);
  }

  // DOM 렌더링 대기 후 하이라이트 위치 계산
  nextTick(() => {
    setTimeout(() => {
      const el = document.querySelector(step.selector);
      if (!el) {
        targetRect.value = null;
        cardStyle.value = { left: '50%', top: '50%', transform: 'translate(-50%, -50%)', width: '340px' };
        return;
      }
      const rect = el.getBoundingClientRect();
      targetRect.value = rect;
      cardStyle.value = computeCardStyle(rect, step.cardPosition);
    }, 150); // UI 전환 및 애니메이션 대기 시간 확보
  });
};

const next = () => {
  if (currentStep.value < steps.length - 1) {
    currentStep.value++;
    nextTick(() => updatePosition());
  } else {
    emit('complete');
  }
};

const skip = () => {
  emit('skip');
};

const handleOverlayClick = () => {
  next();
};

onMounted(() => {
  nextTick(() => updatePosition());
  window.addEventListener('resize', updatePosition);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', updatePosition);
});
</script>

<style scoped>
.tutorial-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(5, 5, 20, 0.05);
  animation: overlayFadeIn 0.3s ease;
}

@keyframes overlayFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* === 하이라이트 컷아웃 === */
.tutorial-highlight {
  position: fixed;
  border-radius: 8px;
  box-shadow: 0 0 0 9999px rgba(5, 5, 20, 0.82);
  border: 2px solid rgba(59, 130, 246, 0.7);
  pointer-events: none;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 10000;
  animation: highlightPulse 2s ease-in-out infinite;
}

@keyframes highlightPulse {
  0%, 100% {
    border-color: rgba(59, 130, 246, 0.7);
    box-shadow: 0 0 0 9999px rgba(5, 5, 20, 0.82), 0 0 20px rgba(59, 130, 246, 0.3);
  }
  50% {
    border-color: rgba(96, 165, 250, 0.9);
    box-shadow: 0 0 0 9999px rgba(5, 5, 20, 0.82), 0 0 35px rgba(96, 165, 250, 0.5);
  }
}

/* === 설명 카드 === */
.tutorial-card {
  position: fixed;
  z-index: 10001;
  background: linear-gradient(135deg, rgba(8, 12, 28, 0.98) 0%, rgba(15, 23, 42, 0.98) 100%);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(59, 130, 246, 0.4);
  border-radius: 20px;
  padding: 28px;
  color: #f1f5f9;
  box-shadow:
    0 12px 48px rgba(0, 0, 0, 0.6),
    0 0 60px rgba(59, 130, 246, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 18px;
}

.step-indicator {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 800;
  color: #60a5fa;
  background: rgba(59, 130, 246, 0.12);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 20px;
  padding: 6px 14px;
  letter-spacing: 1px;
}

.step-title {
  font-weight: 900;
  font-size: 1.1rem;
  color: #fff;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.card-description {
  font-size: 1.05rem;
  font-weight: 500;
  line-height: 1.7;
  color: #cbd5e1;
  margin-bottom: 24px;
  word-break: keep-all;
}

.step-dots {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 24px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  transition: all 0.3s;
}

.dot.active {
  background: #3b82f6;
  box-shadow: 0 0 10px #3b82f6;
  transform: scale(1.4);
}

.dot.done {
  background: #1e40af;
}

.card-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
}

.main-nav {
  display: flex;
  gap: 8px;
}

.btn-quit {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #f87171;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-quit:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: #ef4444;
  color: #fff;
}

.btn-skip {
  background: rgba(255, 255, 255, 0.05);
  color: #94a3b8;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-skip:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #cbd5e1;
}

.btn-next {
  background: #3b82f6;
  color: #fff;
  border: none;
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
}

.btn-next:hover {
  background: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.5);
}
</style>
