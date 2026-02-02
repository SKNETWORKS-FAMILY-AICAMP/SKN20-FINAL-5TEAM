<template>
  <transition name="guidebook-fade">
    <div v-if="isOpen" class="tutorial-overlay" @click.self="$emit('close')">
      <div class="tutorial-container">
        <!-- 헤더 -->
        <header class="tutorial-header">
          <div class="header-main">
            <span class="tutorial-badge">🎓 TUTORIAL</span>
            <h2 class="tutorial-title">Bug Hunt 가이드</h2>
          </div>
          <button class="close-btn" @click="$emit('close')" title="닫기">×</button>
        </header>

        <!-- 진행 상황 -->
        <div class="progress-section">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
          </div>
          <span class="progress-text">{{ currentStep }}/{{ maxSteps }}</span>
        </div>

        <!-- 콘텐츠 영역 -->
        <main class="tutorial-content">
          <!-- 말풍선 가이드 -->
          <div class="guide-bubble" :key="currentStep">
            <div class="bubble-icon">💬</div>
            <div class="bubble-text">{{ currentMessage }}</div>
          </div>

          <!-- Step 1: 환영 -->
          <div v-if="currentStep === 1" class="step-content intro-step">
            <div class="intro-visual">
              <div class="game-preview">
                <div class="preview-left">
                  <div class="preview-box">📋 문제</div>
                  <div class="preview-box">💬 채팅</div>
                </div>
                <div class="preview-right">
                  <div class="preview-box code-preview">
                    <span class="code-line">let total = <span class="bug-text">"0"</span>;</span>
                    <span class="bug-emoji-float">🐛</span>
                  </div>
                </div>
              </div>
              <div class="intro-steps">
                <div class="intro-step-item">
                  <span class="step-icon">1️⃣</span>
                  <span>분석 퀴즈</span>
                </div>
                <div class="intro-arrow">→</div>
                <div class="intro-step-item">
                  <span class="step-icon">2️⃣</span>
                  <span>버그 수정</span>
                </div>
                <div class="intro-arrow">→</div>
                <div class="intro-step-item">
                  <span class="step-icon">3️⃣</span>
                  <span>설명 작성</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 2: 분석 퀴즈 -->
          <div v-if="currentStep === 2" class="step-content quiz-step">
            <div class="quiz-container">
              <div class="quiz-header">
                <span class="phase-badge">PHASE 1</span>
                <h3>분석 퀴즈</h3>
              </div>
              <div class="quiz-question">
                <p>❓ 다음 코드의 버그는 무엇일까요?</p>
                <div class="code-display">
                  <code>let total = "0";</code>
                </div>
              </div>
              <div class="quiz-options">
                <button
                  v-for="(option, idx) in quizOptions"
                  :key="idx"
                  class="quiz-option"
                  :class="{
                    selected: autoSelectedQuiz === idx,
                    correct: autoSelectedQuiz === idx && idx === 1
                  }"
                >
                  <span class="option-num">{{ idx + 1 }}</span>
                  {{ option }}
                  <span v-if="autoSelectedQuiz === idx && idx === 1" class="check-mark">✓</span>
                </button>
              </div>
              <div v-if="showQuizFeedback" class="quiz-feedback success">
                ✅ 정답! 문자열을 숫자로 바꿔야 합니다
              </div>
            </div>
          </div>

          <!-- Step 3: 버그 수정 -->
          <div v-if="currentStep === 3" class="step-content debug-step">
            <div class="debug-container">
              <div class="debug-header">
                <span class="phase-badge">PHASE 2</span>
                <h3>버그 수정하기</h3>
              </div>
              <div class="code-editor-demo">
                <div class="editor-toolbar">
                  <span class="file-name">example.js</span>
                  <div class="bug-indicator">
                    <span class="bug-status" :class="{ dead: bugFixed }">
                      {{ bugFixed ? '💀' : '🐛' }}
                    </span>
                  </div>
                </div>
                <div class="code-content">
                  <div class="code-line">
                    <span class="line-num">1</span>
                    <span class="code-text">
                      let total = <span
                        class="code-value"
                        :class="{
                          buggy: !bugFixed && codeTransition,
                          fixed: bugFixed
                        }"
                      >{{ displayCode }}</span>;
                    </span>
                  </div>
                </div>
              </div>
              <div v-if="bugFixed" class="debug-feedback success">
                🎉 버그 수정 완료! "0" → 0
              </div>
            </div>
          </div>

          <!-- Step 4: 설명 작성 -->
          <div v-if="currentStep === 4" class="step-content explain-step">
            <div class="explain-container">
              <div class="explain-header">
                <span class="phase-badge">PHASE 3</span>
                <h3>설명 작성하기</h3>
              </div>
              <div class="chat-demo">
                <div class="chat-messages">
                  <div class="chat-message system">
                    <div class="message-avatar">🤖</div>
                    <div class="message-bubble">
                      어떻게 버그를 수정했나요?
                    </div>
                  </div>
                  <div v-if="typedExplanation" class="chat-message user">
                    <div class="message-bubble typing">
                      {{ typedExplanation }}
                      <span v-if="isTyping" class="cursor">|</span>
                    </div>
                    <div class="message-avatar">👤</div>
                  </div>
                </div>
              </div>
              <div v-if="explanationComplete" class="explain-feedback success">
                ✅ 설명 작성 완료!
              </div>
            </div>
          </div>

          <!-- Step 5: 완료 -->
          <div v-if="currentStep === 5" class="step-content complete-step">
            <div class="complete-container">
              <div class="complete-icon">🎉</div>
              <h2 class="complete-title">튜토리얼 완료!</h2>
              <div class="complete-summary">
                <div class="summary-item">
                  <span class="summary-icon">✅</span>
                  <span>분석 퀴즈 통과</span>
                </div>
                <div class="summary-item">
                  <span class="summary-icon">✅</span>
                  <span>버그 수정 완료</span>
                </div>
                <div class="summary-item">
                  <span class="summary-icon">✅</span>
                  <span>설명 작성 완료</span>
                </div>
              </div>
              <div class="complete-message">
                이제 실전 문제에 도전해보세요! 🚀
              </div>
            </div>
          </div>
        </main>

        <!-- 푸터 (다음 버튼) -->
        <footer class="tutorial-footer">
          <button
            class="next-btn"
            @click="goToNext"
            :class="{ pulse: canProceed }"
          >
            {{ nextButtonText }}
          </button>
        </footer>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close']);

// 상태 관리
const currentStep = ref(1);
const maxSteps = 5;

// 퀴즈 관련
const autoSelectedQuiz = ref(null);
const showQuizFeedback = ref(false);
const quizOptions = [
  '변수명이 잘못되었습니다',
  '문자열을 숫자로 초기화해야 합니다',
  '세미콜론이 누락되었습니다'
];

// 코드 수정 관련
const displayCode = ref('"0"');
const bugFixed = ref(false);
const codeTransition = ref(false);

// 설명 작성 관련
const typedExplanation = ref('');
const isTyping = ref(false);
const explanationComplete = ref(false);
const fullExplanation = '문자열 "0"을 숫자 0으로 변경했습니다. 숫자 연산을 위해 올바른 타입을 사용해야 합니다.';
let typingInterval = null;

// 진행 상황
const progressPercent = computed(() => {
  return (currentStep.value / maxSteps) * 100;
});

const canProceed = computed(() => {
  if (currentStep.value === 2) return showQuizFeedback.value;
  if (currentStep.value === 3) return bugFixed.value;
  if (currentStep.value === 4) return explanationComplete.value;
  return true;
});

// 메시지
const messages = {
  1: '안녕하세요! Bug Hunt는 3단계로 진행됩니다. 차근차근 따라해보세요!',
  2: '먼저 코드를 분석하는 퀴즈를 풀어요. 어떤 게 문제일까요?',
  3: '이제 버그를 직접 고쳐볼게요. 코드가 자동으로 수정됩니다!',
  4: '마지막으로 어떻게 수정했는지 설명을 작성해요.',
  5: '축하합니다! 이제 실전 문제를 풀 준비가 되었어요!'
};

const currentMessage = computed(() => messages[currentStep.value]);

const nextButtonText = computed(() => {
  if (currentStep.value === maxSteps) return '시작하기! 🎯';
  return '다음 →';
});

// 자동 액션 실행
const triggerAutoActions = () => {
  if (currentStep.value === 2) {
    // 퀴즈 자동 선택
    setTimeout(() => {
      autoSelectedQuiz.value = 1;
      setTimeout(() => {
        showQuizFeedback.value = true;
      }, 500);
    }, 800);
  } else if (currentStep.value === 3) {
    // 코드 자동 수정
    setTimeout(() => {
      codeTransition.value = true;
      setTimeout(() => {
        displayCode.value = '0';
        bugFixed.value = true;
        codeTransition.value = false;
      }, 800);
    }, 1000);
  } else if (currentStep.value === 4) {
    // 설명 자동 타이핑
    setTimeout(() => {
      isTyping.value = true;
      typeExplanation();
    }, 800);
  }
};

// 타이핑 애니메이션
const typeExplanation = () => {
  // 이전 인터벌 정리
  if (typingInterval) {
    clearInterval(typingInterval);
    typingInterval = null;
  }

  // 초기화
  typedExplanation.value = '';
  let index = 0;
  const typingSpeed = 50;

  typingInterval = setInterval(() => {
    if (index < fullExplanation.length) {
      typedExplanation.value += fullExplanation[index];
      index++;
    } else {
      isTyping.value = false;
      explanationComplete.value = true;
      clearInterval(typingInterval);
      typingInterval = null;
    }
  }, typingSpeed);
};

// 다음 단계로
const goToNext = () => {
  if (currentStep.value < maxSteps) {
    currentStep.value++;
    triggerAutoActions();
  } else {
    // 완료 - 가이드북 닫기
    emit('close');
  }
};

// 단계 변경 시 자동 액션 실행
watch(currentStep, (newStep) => {
  if (newStep > 1) {
    triggerAutoActions();
  }
});

// 가이드북 열릴 때마다 초기화
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    // 타이핑 인터벌 정리
    if (typingInterval) {
      clearInterval(typingInterval);
      typingInterval = null;
    }

    // 모든 상태 초기화
    currentStep.value = 1;
    autoSelectedQuiz.value = null;
    showQuizFeedback.value = false;
    displayCode.value = '"0"';
    bugFixed.value = false;
    codeTransition.value = false;
    typedExplanation.value = '';
    isTyping.value = false;
    explanationComplete.value = false;
  } else {
    // 가이드북 닫힐 때도 인터벌 정리
    if (typingInterval) {
      clearInterval(typingInterval);
      typingInterval = null;
    }
  }
});
</script>

<script>
export default {
  emits: ['close']
};
</script>

<style scoped>
/* 오버레이 */
.tutorial-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(10px);
}

/* 컨테이너 */
.tutorial-container {
  background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 100%);
  border: 2px solid #00ff88;
  border-radius: 20px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 0 40px rgba(0, 255, 136, 0.4);
  animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 헤더 */
.tutorial-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: linear-gradient(to right, rgba(0, 255, 136, 0.1), rgba(239, 68, 68, 0.1));
  border-bottom: 2px solid #00ff88;
}

.header-main {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.tutorial-badge {
  font-size: 0.75rem;
  color: #00ff88;
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 2px;
}

.tutorial-title {
  font-size: 1.5rem;
  font-weight: 900;
  color: #00ff88;
  font-family: 'Orbitron', sans-serif;
  margin: 0;
  text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
}

.close-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(239, 68, 68, 0.2);
  border: 2px solid #ef4444;
  border-radius: 8px;
  color: #ef4444;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.3s;
}

.close-btn:hover {
  background: rgba(239, 68, 68, 0.4);
  transform: rotate(90deg);
}

/* 진행 상황 */
.progress-section {
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid rgba(0, 255, 136, 0.2);
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00ff88, #00cc6a);
  border-radius: 10px;
  transition: width 0.5s ease;
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.6);
}

.progress-text {
  font-family: 'Orbitron', monospace;
  color: #00ff88;
  font-weight: 700;
  font-size: 0.9rem;
  min-width: 50px;
  text-align: right;
}

/* 콘텐츠 */
.tutorial-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* 말풍선 */
.guide-bubble {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: rgba(0, 255, 136, 0.1);
  border: 2px solid #00ff88;
  border-radius: 16px;
  animation: bubblePop 0.4s ease-out;
}

@keyframes bubblePop {
  0% {
    transform: scale(0.8);
    opacity: 0;
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.bubble-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.bubble-text {
  color: rgba(255, 255, 255, 0.95);
  font-size: 1.1rem;
  line-height: 1.6;
  font-family: 'Noto Sans KR', sans-serif;
}

/* Step 콘텐츠 */
.step-content {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Step 1: 인트로 */
.intro-visual {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  align-items: center;
}

.game-preview {
  display: flex;
  gap: 1rem;
  width: 100%;
  max-width: 600px;
}

.preview-left,
.preview-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.preview-box {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(0, 255, 136, 0.3);
  border-radius: 8px;
  padding: 1rem;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  text-align: center;
}

.code-preview {
  position: relative;
  font-family: 'JetBrains Mono', monospace;
  background: #0a0a0a;
  padding: 1.5rem;
}

.code-line {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
}

.bug-text {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.2);
  padding: 0 4px;
  border-radius: 3px;
}

.bug-emoji-float {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 1.5rem;
  animation: float 2s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.intro-steps {
  display: flex;
  align-items: center;
  gap: 1rem;
  justify-content: center;
}

.intro-step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid rgba(0, 255, 136, 0.3);
  border-radius: 12px;
  min-width: 120px;
}

.step-icon {
  font-size: 2rem;
}

.intro-step-item span:last-child {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  font-weight: 600;
}

.intro-arrow {
  color: #00ff88;
  font-size: 1.5rem;
  font-weight: bold;
}

/* Step 2: 퀴즈 */
.quiz-container {
  background: rgba(0, 0, 0, 0.3);
  border: 2px solid rgba(0, 255, 136, 0.3);
  border-radius: 12px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.quiz-header,
.debug-header,
.explain-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.phase-badge {
  padding: 0.25rem 0.75rem;
  background: rgba(0, 255, 136, 0.2);
  border: 1px solid #00ff88;
  border-radius: 20px;
  color: #00ff88;
  font-size: 0.75rem;
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 1px;
  font-weight: 700;
}

.quiz-header h3,
.debug-header h3,
.explain-header h3 {
  color: #00ff88;
  font-family: 'Rajdhani', sans-serif;
  font-size: 1.3rem;
  margin: 0;
}

.quiz-question {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.quiz-question p {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.05rem;
  margin: 0;
}

.code-display {
  background: #0a0a0a;
  border: 1px solid rgba(0, 255, 136, 0.3);
  border-radius: 8px;
  padding: 1rem;
  font-family: 'JetBrains Mono', monospace;
  color: #ef4444;
  font-size: 1rem;
}

.quiz-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.quiz-option {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
  border: 2px solid rgba(0, 255, 136, 0.2);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;
  font-size: 1rem;
}

.quiz-option.selected {
  border-color: #00ff88;
  background: rgba(0, 255, 136, 0.15);
  transform: scale(1.02);
}

.quiz-option.correct {
  border-color: #00ff88;
  background: rgba(0, 255, 136, 0.2);
  animation: pulse 1s ease-out;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.option-num {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 255, 136, 0.2);
  border: 1px solid #00ff88;
  border-radius: 50%;
  color: #00ff88;
  font-family: 'Orbitron', sans-serif;
  font-weight: 700;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.check-mark {
  margin-left: auto;
  color: #00ff88;
  font-size: 1.5rem;
  font-weight: bold;
}

.quiz-feedback {
  padding: 1rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  animation: slideIn 0.4s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(-20px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.quiz-feedback.success,
.debug-feedback.success,
.explain-feedback.success {
  background: rgba(0, 255, 136, 0.15);
  border: 1px solid #00ff88;
  color: #00ff88;
}

/* Step 3: 디버그 */
.debug-container {
  background: rgba(0, 0, 0, 0.3);
  border: 2px solid rgba(0, 255, 136, 0.3);
  border-radius: 12px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.code-editor-demo {
  background: #0a0a0a;
  border: 1px solid rgba(0, 255, 136, 0.3);
  border-radius: 8px;
  overflow: hidden;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: rgba(0, 0, 0, 0.5);
  border-bottom: 1px solid rgba(0, 255, 136, 0.2);
}

.file-name {
  color: rgba(255, 255, 255, 0.7);
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;
}

.bug-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.bug-status {
  font-size: 1.5rem;
  transition: all 0.5s;
}

.bug-status.dead {
  animation: bugDeath 0.6s ease-out;
}

@keyframes bugDeath {
  0% {
    transform: rotate(0deg) scale(1);
  }
  50% {
    transform: rotate(180deg) scale(1.5);
  }
  100% {
    transform: rotate(360deg) scale(1);
  }
}

.code-content {
  padding: 1.5rem;
}

.code-line {
  display: flex;
  gap: 1rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.1rem;
  line-height: 1.8;
}

.line-num {
  color: #666;
  user-select: none;
  min-width: 20px;
}

.code-text {
  color: rgba(255, 255, 255, 0.9);
}

.code-value {
  transition: all 0.5s;
}

.code-value.buggy {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.2);
  padding: 0 4px;
  border-radius: 3px;
  animation: shake 0.5s;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
}

.code-value.fixed {
  color: #00ff88;
  background: rgba(0, 255, 136, 0.2);
  padding: 0 4px;
  border-radius: 3px;
  animation: glow 0.8s;
}

@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 0 rgba(0, 255, 136, 0);
  }
  50% {
    box-shadow: 0 0 20px rgba(0, 255, 136, 0.8);
  }
}

/* Step 4: 설명 */
.explain-container {
  background: rgba(0, 0, 0, 0.3);
  border: 2px solid rgba(0, 255, 136, 0.3);
  border-radius: 12px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.chat-demo {
  background: #0a0a0a;
  border: 1px solid rgba(0, 255, 136, 0.3);
  border-radius: 12px;
  padding: 1.5rem;
  min-height: 200px;
}

.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chat-message {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.chat-message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid rgba(0, 255, 136, 0.3);
  border-radius: 50%;
  font-size: 1.3rem;
  flex-shrink: 0;
}

.message-bubble {
  max-width: 70%;
  padding: 1rem;
  border-radius: 12px;
  font-size: 1rem;
  line-height: 1.6;
}

.chat-message.system .message-bubble {
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid rgba(0, 255, 136, 0.3);
  color: rgba(255, 255, 255, 0.9);
}

.chat-message.user .message-bubble {
  background: rgba(0, 123, 255, 0.2);
  border: 1px solid rgba(0, 123, 255, 0.4);
  color: rgba(255, 255, 255, 0.9);
}

.message-bubble.typing {
  animation: slideInRight 0.4s ease-out;
}

@keyframes slideInRight {
  from {
    transform: translateX(20px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.cursor {
  display: inline-block;
  animation: blink 1s infinite;
  margin-left: 2px;
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

/* Step 5: 완료 */
.complete-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  padding: 2rem;
  text-align: center;
}

.complete-icon {
  font-size: 5rem;
  animation: bounce 1s ease-out;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-30px);
  }
  60% {
    transform: translateY(-15px);
  }
}

.complete-title {
  font-size: 2.5rem;
  font-weight: 900;
  color: #00ff88;
  font-family: 'Orbitron', sans-serif;
  margin: 0;
  text-shadow: 0 0 20px rgba(0, 255, 136, 0.6);
  animation: fadeIn 0.8s ease-out;
}

.complete-summary {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 400px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid rgba(0, 255, 136, 0.3);
  border-radius: 8px;
  animation: slideInLeft 0.6s ease-out backwards;
}

.summary-item:nth-child(1) {
  animation-delay: 0.2s;
}

.summary-item:nth-child(2) {
  animation-delay: 0.4s;
}

.summary-item:nth-child(3) {
  animation-delay: 0.6s;
}

@keyframes slideInLeft {
  from {
    transform: translateX(-30px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.summary-icon {
  font-size: 1.5rem;
}

.summary-item span:last-child {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
}

.complete-message {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.2rem;
  font-weight: 600;
  animation: fadeIn 1s ease-out;
}

/* 푸터 */
.tutorial-footer {
  padding: 1.5rem;
  background: linear-gradient(to top, rgba(0, 255, 136, 0.1), transparent);
  border-top: 2px solid #00ff88;
  display: flex;
  justify-content: center;
}

.next-btn {
  padding: 1rem 3rem;
  background: linear-gradient(135deg, #00ff88, #00cc6a);
  border: none;
  border-radius: 12px;
  color: #0a0e27;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.1rem;
  font-weight: 900;
  cursor: pointer;
  transition: all 0.3s;
  text-transform: uppercase;
  letter-spacing: 2px;
  box-shadow: 0 4px 15px rgba(0, 255, 136, 0.4);
}

.next-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 255, 136, 0.6);
}

.next-btn.pulse {
  animation: pulseBtn 2s infinite;
}

@keyframes pulseBtn {
  0%, 100% {
    box-shadow: 0 4px 15px rgba(0, 255, 136, 0.4);
  }
  50% {
    box-shadow: 0 4px 25px rgba(0, 255, 136, 0.8);
  }
}

/* 페이드 트랜지션 */
.guidebook-fade-enter-active,
.guidebook-fade-leave-active {
  transition: opacity 0.3s;
}

.guidebook-fade-enter-from,
.guidebook-fade-leave-to {
  opacity: 0;
}

/* 스크롤바 */
.tutorial-content::-webkit-scrollbar {
  width: 8px;
}

.tutorial-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.3);
}

.tutorial-content::-webkit-scrollbar-thumb {
  background: rgba(0, 255, 136, 0.5);
  border-radius: 4px;
}

.tutorial-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 255, 136, 0.7);
}
</style>
