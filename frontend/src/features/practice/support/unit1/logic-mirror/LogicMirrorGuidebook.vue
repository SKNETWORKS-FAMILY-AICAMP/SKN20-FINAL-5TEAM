<template>
  <transition name="guidebook-fade">
    <div v-if="isOpen" class="guidebook-overlay" @click.self="$emit('close')">
      <div class="guidebook-container">
        <header class="guidebook-header">
          <div class="header-main">
            <div class="header-icon">📖</div>
            <div class="header-titles">
              <h2 class="main-title">{{ tutorial.name }}</h2>
              <p class="sub-title">{{ tutorial.description }}</p>
            </div>
          </div>
          <button class="close-btn" @click="$emit('close')">&times;</button>
        </header>

        <div class="guidebook-content">
          <div v-for="step in tutorial.steps" :key="step.id" class="guide-step-card">
            <div class="step-badge">Tutorial Step</div>
            <h3 class="step-title">{{ step.title }}</h3>
            <p class="step-desc">{{ step.description }}</p>
            
            <div class="instruction-box">
              <div class="inst-label">💡 학습 목표</div>
              <p>{{ step.instruction }}</p>
            </div>

            <div class="blocks-preview">
              <div class="preview-label">사용 예시 블록</div>
              <div class="preview-list">
                <div 
                  v-for="card in step.cards" 
                  :key="card.id" 
                  class="preview-card"
                  :class="`card-${card.color}`"
                >
                  <div class="card-icon">{{ card.icon }}</div>
                  <div class="card-text">{{ card.text_ko }}</div>
                </div>
              </div>
            </div>

            <div class="hint-strip">
              <span class="hint-icon">🎯</span>
              <span class="hint-text">{{ step.hint }}</span>
            </div>
          </div>
        </div>

        <footer class="guidebook-footer">
          <button class="understand-btn" @click="$emit('close')">이해했습니다! 코드 연습하러 가기</button>
        </footer>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed } from 'vue';
import { gameData } from './data/stages.js';

/* 
  수정일: 2026-01-24
  수정내용: stages.js의 튜토리얼 데이터를 기반으로 한 가이드북 모달 컴포넌트 신규 생성
*/

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close']);

const tutorial = computed(() => gameData.tutorial);
</script>

<style scoped>
.guidebook-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(12px);
  z-index: 11000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.guidebook-container {
  width: 100%;
  max-width: 800px;
  max-height: 85vh;
  background: #0f172a;
  border-radius: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.5), 0 0 20px rgba(99, 102, 241, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modalPop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes modalPop {
  from { opacity: 0; transform: scale(0.9) translateY(20px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.guidebook-header {
  padding: 2rem;
  background: rgba(255, 255, 255, 0.03);
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

.header-icon {
  font-size: 2.5rem;
  background: rgba(99, 102, 241, 0.1);
  padding: 0.5rem;
  border-radius: 1rem;
}

.main-title {
  color: white;
  font-size: 1.75rem;
  font-weight: 800;
  margin: 0;
}

.sub-title {
  color: rgba(255, 255, 255, 0.5);
  margin: 0.25rem 0 0 0;
  font-size: 1rem;
}

.close-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  font-size: 2rem;
  cursor: pointer;
  transition: color 0.2s;
}

.close-btn:hover {
  color: white;
}

.guidebook-content {
  flex: 1;
  padding: 2.5rem;
  overflow-y: auto;
}

.guide-step-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1.5rem;
  padding: 2rem;
}

.step-badge {
  display: inline-block;
  background: #6366f1;
  color: white;
  font-size: 0.7rem;
  font-weight: 900;
  padding: 0.3rem 0.8rem;
  border-radius: 1rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 1rem;
}

.step-title {
  color: white;
  font-size: 1.5rem;
  margin: 0 0 0.75rem 0;
}

.step-desc {
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
  font-size: 1.1rem;
}

.instruction-box {
  margin-top: 2rem;
  background: rgba(99, 102, 241, 0.08);
  border-radius: 1rem;
  padding: 1.5rem;
  border-left: 4px solid #6366f1;
}

.inst-label {
  font-weight: 800;
  color: #818cf8;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.instruction-box p {
  color: white;
  margin: 0;
  font-size: 1rem;
}

.blocks-preview {
  margin-top: 2.5rem;
}

.preview-label {
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.9rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.preview-card {
  background: rgba(255, 255, 255, 0.04);
  padding: 1rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border-left: 4px solid #ccc;
}

.card-blue { border-left-color: #60a5fa; }
.card-green { border-left-color: #4ade80; }
.card-orange { border-left-color: #fb923c; }

.card-icon { font-size: 1.5rem; }
.card-text { color: white; font-weight: 600; }

.hint-strip {
  margin-top: 2rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #b6ff40;
  font-weight: 700;
  font-size: 0.95rem;
}

.guidebook-footer {
  padding: 1.5rem 2.5rem;
  background: rgba(255, 255, 255, 0.02);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.understand-btn {
  width: 100%;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
  border: none;
  padding: 1.25rem;
  border-radius: 1rem;
  font-size: 1.1rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s;
}

.understand-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(79, 70, 229, 0.4);
}

/* Transitions */
.guidebook-fade-enter-active, .guidebook-fade-leave-active {
  transition: opacity 0.3s ease;
}
.guidebook-fade-enter-from, .guidebook-fade-leave-to {
  opacity: 0;
}
</style>
