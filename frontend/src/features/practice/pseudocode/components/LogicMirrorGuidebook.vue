<template>
  <!-- [2026-02-12] Restored Component -->
  <transition name="guidebook-fade">
    <div v-if="isOpen" class="guidebook-overlay" @click.self="$emit('close')">
      <div class="guidebook-container">
        <!-- Header -->
        <header class="guidebook-header">
          <div class="header-main">
            <div class="header-icon-wrapper">
              <BookOpen class="w-8 h-8 text-indigo-400" />
            </div>
            <div class="header-titles">
              <h2 class="main-title tracking-tighter">{{ tutorial?.name || '가이드' }}</h2>
              <p class="sub-title font-medium">{{ tutorial?.description || '사용 방법 안내' }}</p>
            </div>
          </div>
          <button class="close-btn" @click="$emit('close')" title="가이드 닫기">
            <X class="w-6 h-6" />
          </button>
        </header>

        <!-- Content Area -->
        <div class="guidebook-content custom-scrollbar">
          <div v-for="(step, index) in (tutorial?.steps || [])" :key="step.id || index" class="guide-step-card group">
            <div class="step-header">
              <div class="step-number">STEP 0{{ index + 1 }}</div>
              <div class="step-badge">Tutorial Phase</div>
            </div>
            
            <div class="step-body">
              <div class="step-icon-box" v-if="step.icon">
                <span class="text-4xl leading-none">{{ step.icon }}</span>
              </div>
              <div class="step-text-content">
                <h3 class="step-title tracking-tight">{{ step.title }}</h3>
                <p class="step-desc leading-relaxed">{{ step.description }}</p>
                
                <div class="instruction-box" v-if="step.instruction">
                  <div class="inst-label flex items-center gap-2">
                    <Sparkles class="w-4 h-4 text-indigo-400" />
                    <span>핵심 목표</span>
                  </div>
                  <p class="inst-text">{{ step.instruction }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <footer class="guidebook-footer">
          <div class="footer-hint flex items-center gap-3 text-slate-500 text-sm font-medium mb-6">
            <div class="w-2 h-2 rounded-full bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.5)]"></div>
            <span>가이드를 모두 읽으셨다면 실습을 시작해보세요!</span>
          </div>
          <button class="understand-btn group" @click="$emit('close')">
            <span>훈련 시작하기</span>
            <ArrowRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </footer>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed } from 'vue';
import { useGameStore } from '@/stores/game';
import { 
  BookOpen, 
  X, 
  Sparkles, 
  ArrowRight
} from 'lucide-vue-next';

/* 
  수정일: 2026-01-26
  수정내용: 
  - 본문 내용이 보이지 않는 문제 해결을 위해 렌더링 로직 단순화
  - 복잡한 아이콘 동적 컴포넌트 로직을 제거하고 데이터의 이모지를 직접 출력
  - 스타일 강화를 통해 텍스트 가시성 보장 및 레이아웃 붕괴 방지
*/

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close']);

// 튜토리얼 데이터 로드 (gameData.quests -> activeUnit.problems)
const tutorialSteps = computed(() => {
  const problems = useGameStore().activeUnit?.problems || [];
  return problems.slice(0, 3).map(p => {
    const q = p.config || {};
    return {
      title: q.title || p.title,
      icon: q.emoji || '🚀', // emoji 필드 사용
      desc: q.description || q.desc || '미션 설명이 없습니다.',
      instruction: q.instruction || '가이드를 참고하세요.', // instruction 필드 추가
      logicType: q.logic_type || '순차'
    };
  });
});

const tutorialName = computed(() => "AI 훈련 가이드");
const tutorialDescription = computed(() => "AI 훈련의 핵심 단계를 안내합니다.");
</script>

<style scoped>
.guidebook-overlay {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.9);
  backdrop-filter: blur(20px);
  z-index: 20000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.guidebook-container {
  width: 100%;
  max-width: 900px;
  max-height: 85vh;
  background: #0f172a;
  border-radius: 3rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 
    0 50px 100px -20px rgba(0, 0, 0, 0.8),
    0 0 60px rgba(99, 102, 241, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modalIn 0.5s cubic-bezier(0.16, 1, 0.3, 1);
  font-family: var(--font-main), sans-serif;
}

@keyframes modalIn {
  from { opacity: 0; transform: translateY(30px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.guidebook-header {
  padding: 2.5rem 3.5rem;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-main {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.header-icon-wrapper {
  background: rgba(99, 102, 241, 0.15);
  padding: 1rem;
  border-radius: 1.5rem;
  border: 1px solid rgba(99, 102, 241, 0.3);
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.1);
}

.main-title {
  color: #ffffff;
  font-size: 2.25rem;
  font-weight: 950;
  margin: 0;
}

.sub-title {
  color: #94a3b8;
  margin-top: 0.25rem;
  font-size: 1rem;
}

.close-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #64748b;
  width: 52px;
  height: 52px;
  border-radius: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.close-btn:hover {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.3);
  transform: rotate(90deg) scale(1.1);
}

.guidebook-content {
  flex: 1;
  padding: 3rem 3.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 10px; }

.guide-step-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 2.5rem;
  padding: 2.5rem;
  transition: all 0.5s;
  position: relative;
  min-height: 200px;
}

.guide-step-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(99, 102, 241, 0.4);
  transform: translateY(-4px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.step-number {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;
  font-weight: 900;
  color: #818cf8;
  background: rgba(79, 70, 229, 0.15);
  padding: 0.3rem 0.8rem;
  border-radius: 0.75rem;
}

.step-badge {
  color: #475569;
  font-size: 0.75rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.step-body {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}

.step-icon-box {
  flex-shrink: 0;
  width: 80px;
  height: 80px;
  background: #1e293b;
  border-radius: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
}

.step-text-content {
  flex: 1;
}

.step-title {
  color: #ffffff;
  font-size: 1.6rem;
  font-weight: 800;
  margin-bottom: 0.75rem;
  line-height: 1.25;
}

.step-desc {
  color: #94a3b8;
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.instruction-box {
  background: #020617;
  border-radius: 1.5rem;
  padding: 1.5rem;
  border: 1px solid rgba(99, 102, 241, 0.2);
  position: relative;
}

.inst-label {
  font-weight: 900;
  color: #818cf8;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 0.5rem;
}

.inst-text {
  color: #f1f5f9;
  font-size: 1rem;
  margin: 0;
  line-height: 1.5;
}

.guidebook-footer {
  padding: 2.5rem 3.5rem;
  background: rgba(255, 255, 255, 0.02);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.understand-btn {
  width: 100%;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: #ffffff;
  border: none;
  padding: 1.5rem;
  border-radius: 1.5rem;
  font-size: 1.3rem;
  font-weight: 900;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  box-shadow: 0 15px 35px -10px rgba(79, 70, 229, 0.5);
}

.understand-btn:hover {
  transform: translateY(-2px);
  filter: brightness(1.1);
}

/* Transitions */
.guidebook-fade-enter-active, .guidebook-fade-leave-active { transition: opacity 0.5s ease; }
.guidebook-fade-enter-from, .guidebook-fade-leave-to { opacity: 0; }

.tracking-tighter { letter-spacing: -0.05em; }
.tracking-tight { letter-spacing: -0.025em; }
</style>
