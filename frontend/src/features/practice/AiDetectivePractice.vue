<!--
수정일: 2026-01-28
수정내용: AI Detective 실습 페이지를 모달 오버레이 구조로 전환하고 프리미엄 UI/UX 적용.
-->
<template>
  <div class="modal-overlay detective-theme" @click.self="$emit('close')">
    <!-- 메인 모달 컨테이너 -->
    <div class="detective-modal-container animate-scale-in">
      
      <!-- 헤더 영역 -->
      <header class="detective-header">
        <div class="header-left">
          <div class="badge-dna">DNA-TRACE #{{ currentQuest.id }}</div>
          <h1 class="detective-title">{{ currentQuest.title }}</h1>
          <span :class="['level-badge', levelClass]">{{ currentQuest.level }}</span>
        </div>
        <div class="header-right">
          <!-- [수정일: 2026-01-28] AI 가이드 버튼 위치 및 스타일 유지 -->
          <button @click="showHint" class="btn-hint">
            <i data-lucide="sparkles"></i>
            <span>AI 가이드</span>
          </button>
          <!-- [수정일: 2026-01-28] 닫기 버튼을 직접 SVG로 구현하여 렌더링 무결성 확보 및 가시성 극대화 -->
          <button @click="$emit('close')" class="btn-close-detective" title="닫기">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </header>

      <!-- 바디 영역 -->
      <div class="detective-body">
        <!-- 왼쪽: 브리핑 창 -->
        <aside class="detective-sidebar">
          <section class="info-card scenario">
            <h3 class="card-label"><i data-lucide="shield-alert"></i> CASE BRIEFING</h3>
            <div class="card-content italic">{{ currentQuest.briefing }}</div>
          </section>

          <section class="info-card data-stream">
            <h3 class="card-label"><i data-lucide="database"></i> INPUT STREAM</h3>
            <div class="data-list custom-scrollbar">
              <div v-for="d in currentQuest.data" :key="d.name" class="data-item">
                <span class="data-name">{{ d.name }}</span>
                <code :class="d.color">{{ d.value }}</code>
              </div>
            </div>
          </section>

          <section class="mission-alert">
            <h3 class="mission-label">MISSION</h3>
            <p class="mission-text">{{ currentQuest.mission }}</p>
          </section>
        </aside>

        <!-- 오른쪽: 에디터 및 결과 -->
        <main class="detective-main">
          <div class="editor-wrapper" :class="{ 'analyzing': isSubmitting }">
            <div class="editor-toolbar">
              <div class="file-name"><span class="neon-dot"></span> PIPELINE_ANALYSER.py</div>
              <button @click="submitLogic" :disabled="isSubmitting" class="btn-run">
                <i v-if="!isSubmitting" data-lucide="cpu"></i>
                <i v-else data-lucide="loader-2" class="animate-spin"></i>
                {{ isSubmitting ? 'ANALYZING...' : 'RUN LOGIC' }}
              </button>
            </div>
            
            <div class="textarea-container">
              <!-- [수정일: 2026-01-28] 분석 중일 때 나타나는 스캐닝 가이드 라인 -->
              <div v-if="isSubmitting" class="scan-line"></div>
              
              <textarea 
                v-model="userCode" 
                placeholder="데이터 수사 로직을 기술하세요..."
                spellcheck="false"
                class="detective-textarea"
              ></textarea>
            </div>
          </div>

          <!-- 결과창 (조건부 렌더링) -->
          <transition name="slide-up">
            <div v-if="result" :class="['result-panel', result.success ? 'success' : 'failure']">
              <div class="result-icon-box">
                <i v-if="result.success" data-lucide="check-circle-2"></i>
                <i v-else data-lucide="x-octagon"></i>
              </div>
              <div class="result-info">
                <div class="result-header">
                  <h4>{{ result.success ? '수사 성공! 로직 일치' : '수사 실패! 로직 결함' }}</h4>
                  <span class="rank-tag">{{ result.rank }}</span>
                </div>
                <!-- [수정일: 2026-01-28] 상세 분석 지표 시각화 -->
                <div class="analysis-indicators">
                  <div class="indicator-item">
                    <span class="ind-label">Insight</span>
                    <div class="ind-bar-bg"><div class="ind-bar-fill" :style="{ width: (result.insight * 2) + '%', background: '#facc15' }"></div></div>
                  </div>
                  <div class="indicator-item">
                    <span class="ind-label">Structure</span>
                    <div class="ind-bar-bg"><div class="ind-bar-fill" :style="{ width: (result.structure * 3.33) + '%', background: '#60a5fa' }"></div></div>
                  </div>
                  <div class="indicator-item">
                    <span class="ind-label">Precision</span>
                    <div class="ind-bar-bg"><div class="ind-bar-fill" :style="{ width: (result.precision * 5) + '%', background: '#34d399' }"></div></div>
                  </div>
                </div>
                <p class="feedback-text">{{ result.feedback }}</p>
              </div>
              <div class="score-box">
                <span class="score-val">{{ result.score }}</span>
                <span class="score-label">TOTAL</span>
              </div>
              <div v-if="result.success" class="next-action">
                <button @click="$emit('close')" class="btn-list">목록으로</button>
                <!-- [수정일: 2026-01-28] 다음 단계 즉시 진행 버튼 추가 -->
                <button v-if="currentQuestIdx < 29" @click="startNextQuest" class="btn-next">
                  다음 수사 착수 <i data-lucide="arrow-right"></i>
                </button>
              </div>
            </div>
          </transition>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useGameStore } from '@/stores/game';
import { aiDetectiveQuests } from './support/unit1/logic-mirror/data/aiDetectiveQuests.js';

const props = defineProps({
  initialQuestIndex: { type: Number, default: 0 }
});

const emit = defineEmits(['close']);

const game = useGameStore();
const currentQuestIdx = ref(props.initialQuestIndex);

/**
 * [수정일: 2026-01-28] 다음 미션으로 즉시 전환하는 로직
 */
const startNextQuest = () => {
    if (currentQuestIdx.value < 29) {
        currentQuestIdx.value++;
        result.value = null; // 결과 초기화
        code.value = '';     // 코드 초기화
        // Lucide 아이콘 재랜더링
        nextTick(() => { if (window.lucide) window.lucide.createIcons(); });
    }
};

const currentQuest = computed(() => aiDetectiveQuests[currentQuestIdx.value] || aiDetectiveQuests[0]);

const userCode = ref('');
const isSubmitting = ref(false);
const result = ref(null);

const levelClass = computed(() => {
  const l = currentQuest.value.level;
  if (l === '초급') return 'easy';
  if (l === '중급') return 'medium';
  return 'hard';
});

const showHint = () => {
  alert(`🕵️ 수사관 힌트:\n${currentQuest.value.hint}`);
};

const submitLogic = async () => {
  if (!userCode.value.trim()) return;
  isSubmitting.value = true;
  result.value = null;

  // [수정일: 2026-01-28] 고도화된 AI 평가 엔진 로직
  setTimeout(() => {
    const code = userCode.value.toLowerCase();
    const quest = currentQuest.value;
    
    // 1. 통찰력 (Insight) 평가: 타겟 데이터 및 미션 핵심 키워드 인식 여부
    let insightScore = 0;
    const targetKeywords = quest.target.toLowerCase().split(/[,|]/).map(s => s.trim());
    const dataKeywords = quest.data.map(d => d.name.toLowerCase());
    
    // [수정일: 2026-01-28] 미션에서 수치(임계값 등) 추출하여 동적 검증 루틴 추가
    const missionNumbers = quest.mission.match(/\d+(\.\d+)?/g) || [];
    const hasMissionNumbers = missionNumbers.some(num => code.includes(num));

    const hasDataRef = dataKeywords.some(k => code.includes(k));
    const hasTargetRef = targetKeywords.some(k => code.includes(k));
    
    if (hasDataRef) insightScore += 20;
    if (hasTargetRef) insightScore += 20;
    if (hasMissionNumbers) insightScore += 10; // 미션 내 조건(수치) 반영 시 가점

    // 2. 구성력 (Structure) 평가: 알고리즘 구조(루프, 조건문) 타당성
    let structureScore = 0;
    const hasLoop = code.includes('for') || code.includes('while') || code.includes('반복') || code.includes('순회');
    const hasIf = code.includes('if') || code.includes('만약') || code.includes('조건');
    if (hasLoop) structureScore += 20;
    if (hasIf) structureScore += 10;

    // 3. 정밀도 (Precision) 평가: 출력 명령 및 논리적 완결성
    let precisionScore = 0;
    const hasOutput = code.includes('print') || code.includes('출력') || code.includes('return') || code.includes('collect') || code.includes('filter');
    if (hasOutput) precisionScore += 10;
    if (code.length > 40) precisionScore += 10; 

    const totalScore = insightScore + structureScore + precisionScore;
    const isSuccess = totalScore >= 60; // 통과 기준

    // 다중 지표 결과 객체 생성
    result.value = {
      success: isSuccess,
      score: totalScore,
      rank: totalScore >= 90 ? 'LEGEND' : (totalScore >= 70 ? 'ELITE' : 'ROOKIE'),
      insight: insightScore,
      structure: structureScore,
      precision: precisionScore,
      feedback: generateAiFeedback(isSuccess, quest, code, { insightScore, structureScore, precisionScore }),
      logicCheck: {
        data: hasDataRef,
        target: hasTargetRef,
        flow: hasLoop && hasIf
      }
    };

    if (isSuccess) {
      game.unlockNextStage('AI Detective', currentQuestIdx.value);
    }
    isSubmitting.value = false;
    nextTick(() => { if (window.lucide) window.lucide.createIcons(); });
  }, 1500); // 분석 시간 연장 (몰입감)
};

/**
 * [수정일: 2026-01-28] 분석 점수 및 문제 컨텍스트를 바탕으로 동적 AI 수사 리포트 생성
 */
function generateAiFeedback(isSuccess, quest, code, scores) {
  const { insightScore, structureScore, precisionScore } = scores;
  const targetVal = quest.target;
  const dataNames = quest.data.map(d => d.name).join(', ');

  let report = '';

  if (isSuccess) {
    report = `[AI 수사 본부 분석 완료] `;
    report += `데이터 스트림(${dataNames})에서 핵심 타겟인 '${targetVal}'을(를) 정확히 식별했습니다. `;
    
    if (structureScore >= 30) {
      report += `구조화된 알고리즘을 통해 효율적으로 접근하셨군요. `;
    } else {
      report += `로직이 다소 단순하지만 결과 도출 방식은 유효합니다. `;
    }

    if (precisionScore >= 20) {
      report += `수사관님의 상세한 기술 방식은 수사 무결성을 보장하기에 충분합니다.`;
    }
  } else {
    report = `[수사 결함 분석 리포트] `;
    
    if (insightScore < 25) {
      report += `가장 큰 결함은 '데이터 식별' 단계입니다. '${dataNames}' 변수를 로직에 명시하고 수사 대상을 명확히 정의하세요. `;
    } else if (insightScore < 50) {
      report += `데이터 대조 과정에서 핵심 타겟인 '${targetVal}'에 대한 구체적인 검증이 누락된 것으로 보입니다. `;
    }

    if (structureScore < 20) {
      report += `알고리즘 구성이 미흡합니다. 반복문 등을 사용하여 데이터 전체를 전수 조사하는 구조를 권장합니다. `;
    }

    if (report === `[수사 결함 분석 리포트] `) {
      report += `제시된 미션을 해결하기 위한 논리적 완결성이 부족합니다. 브리핑을 다시 정독하고 로직을 재구성하세요.`;
    }
  }

  return report;
}

onMounted(() => {
  nextTick(() => { if (window.lucide) window.lucide.createIcons(); });
});
</script>

<style scoped>
/* 모달 오버레이 */
.modal-overlay.detective-theme {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.9);
  backdrop-filter: blur(20px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

/* 모달 컨테이너 */
.detective-modal-container {
  width: 100%;
  max-width: 1100px;
  height: 80vh;
  background: #0f172a;
  border: 1px solid rgba(250, 204, 21, 0.2);
  border-radius: 2rem;
  box-shadow: 0 0 50px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(250, 204, 21, 0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 헤더 */
.detective-header {
  height: 80px;
  padding: 0 2.5rem;
  background: rgba(30, 41, 59, 0.5);
  border-bottom: 2px solid rgba(250, 204, 21, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.badge-dna {
  background: rgba(250, 204, 21, 0.1);
  color: #facc15;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 800;
  border: 1px solid rgba(250, 204, 21, 0.3);
}

.detective-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: white;
}

.level-badge {
  font-size: 0.65rem;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 900;
  text-transform: uppercase;
}
.level-badge.easy { background: rgba(52, 211, 153, 0.1); color: #34d399; }
.level-badge.medium { background: rgba(96, 165, 250, 0.1); color: #60a5fa; }
.level-badge.hard { background: rgba(248, 113, 113, 0.1); color: #f87171; }

/* [수정일: 2026-01-28] 헤더 오른쪽 버튼 정렬을 위한 Flex 레이아웃 추가 */
.header-right {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.btn-hint {
  background: #1e293b;
  color: #94a3b8;
  padding: 8px 16px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  font-weight: 700;
  transition: all 0.2s;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.btn-hint:hover { background: #334155; color: #facc15; }

/* [수정일: 2026-01-28] 닫기 버튼 가시성 극대화 (완전 흰색 #ffffff 적용 및 SVG 크기 고정) */
.btn-close-detective {
  background: none;
  border: none;
  color: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  border-radius: 10px;
  transition: all 0.2s;
}
.btn-close-detective svg {
  width: 24px;
  height: 24px;
  display: block;
}
.btn-close-detective:hover { 
  color: #facc15; 
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.1);
}

/* 바디 레이아웃 */
.detective-body {
  flex: 1;
  display: flex;
  min-height: 0;
}

/* 사이드바 */
.detective-sidebar {
  width: 320px;
  padding: 2rem;
  background: rgba(2, 6, 23, 0.3);
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  overflow-y: auto;
}

.info-card {
  background: rgba(30, 41, 59, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.03);
  padding: 1.25rem;
  border-radius: 1rem;
}

.card-label {
  font-size: 0.65rem;
  font-weight: 800;
  color: #64748b;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 6px;
  letter-spacing: 1px;
}

.card-content {
  font-size: 0.85rem;
  color: #94a3b8;
  line-height: 1.6;
}

.data-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.data-item {
  background: rgba(0, 0, 0, 0.2);
  padding: 10px;
  border-radius: 8px;
}

.data-name {
  font-size: 0.6rem;
  color: #475569;
  display: block;
  margin-bottom: 4px;
  font-weight: 800;
}

/* [수정일: 2026-01-28] 노란 영역(Input Stream 데이터)의 폰트 크기 축소 */
.data-item code {
  font-size: 0.85rem;
  font-family: 'JetBrains Mono', monospace;
  line-height: 1.4;
  word-break: break-all;
}

.mission-alert {
  background: linear-gradient(135deg, rgba(250, 204, 21, 0.1), rgba(250, 204, 21, 0.05));
  border: 1px solid rgba(250, 204, 21, 0.2);
  padding: 1.25rem;
  border-radius: 1rem;
}

.mission-label {
  color: #facc15;
  font-weight: 900;
  font-size: 0.7rem;
  margin-bottom: 0.5rem;
}

.mission-text {
  font-size: 0.9rem;
  font-weight: 700;
  color: #fef08a;
}

/* 메인 에디터 영역 */
.detective-main {
  flex: 1;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  min-height: 0;
}

.editor-wrapper {
  flex: 1;
  background: #020617;
  border-radius: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-toolbar {
  height: 50px;
  background: rgba(30, 41, 59, 0.4);
  padding: 0 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.file-name {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: #475569;
  display: flex;
  align-items: center;
  gap: 8px;
}

.neon-dot {
  width: 6px;
  height: 6px;
  background: #facc15;
  border-radius: 50%;
  box-shadow: 0 0 10px #facc15;
}

.btn-run {
  background: #facc15;
  color: #0f172a;
  padding: 6px 16px;
  border-radius: 99px;
  font-size: 0.75rem;
  font-weight: 900;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}
.btn-run:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(250, 204, 21, 0.3); }

.detective-textarea {
  flex: 1;
  background: transparent;
  padding: 2rem;
  color: #f8fafc; /* 더욱 밝은 텍스트 */
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.15rem; /* 가독성 향상 */
  line-height: 1.8;
  resize: none;
  border: none;
  outline: none;
}

/* [수정일: 2026-01-28] 스캐닝 효과 및 컨테이너 스타일 */
.textarea-container {
  flex: 1;
  position: relative;
  display: flex;
  flex-direction: column;
}

.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #facc15, transparent);
  box-shadow: 0 0 15px #facc15;
  z-index: 10;
  animation: scanMove 2s infinite ease-in-out;
  pointer-events: none;
}

@keyframes scanMove {
  0% { top: 0; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}

.editor-wrapper.analyzing {
  border-color: rgba(250, 204, 21, 0.4);
  box-shadow: 0 0 30px rgba(250, 204, 21, 0.1);
}

/* 결과 패널 */
.result-panel {
  height: auto; /* 상세 지표를 위해 가변 높이로 변경 */
  min-height: 120px;
  background: rgba(30, 41, 59, 0.8);
  border-radius: 1.5rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  border: 1px solid transparent;
}

/* [수정일: 2026-01-28] 상세 분석 지표 스타일 */
.analysis-indicators {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 12px 0;
}

.indicator-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ind-label {
  font-size: 0.65rem;
  font-weight: 800;
  color: #64748b;
  width: 60px;
  letter-spacing: 0.5px;
}

.ind-bar-bg {
  flex: 1;
  height: 4px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 2px;
  overflow: hidden;
}

.ind-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 1s cubic-bezier(0.16, 1, 0.3, 1);
}
.result-panel.success { border-color: rgba(52, 211, 153, 0.3); background: rgba(6, 78, 59, 0.2); }
.result-panel.failure { border-color: rgba(248, 113, 113, 0.3); background: rgba(127, 29, 29, 0.2); }

.result-icon-box {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
}
.result-panel.success .result-icon-box { color: #34d399; }
.result-panel.failure .result-icon-box { color: #f87171; }

.result-info { flex: 1; }
.result-header { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.result-header h4 { font-weight: 800; font-size: 1.1rem; color: white; }
.rank-tag { background: rgba(250, 204, 21, 0.1); color: #facc15; font-size: 0.6rem; padding: 2px 6px; border-radius: 4px; font-weight: 900; }
.feedback-text { font-size: 0.85rem; color: #94a3b8; }

.score-box { text-align: center; padding: 0 1.5rem; border-left: 1px solid rgba(255, 255, 255, 0.05); }
.score-val { display: block; font-size: 2rem; font-weight: 900; color: #facc15; line-height: 1; }
.score-label { font-size: 0.6rem; color: #475569; font-weight: 800; }

.next-action { display: flex; gap: 12px; }
.btn-list { background: rgba(255, 255, 255, 0.05); color: #94a3b8; padding: 10px 20px; border-radius: 12px; font-weight: 800; border: 1px solid rgba(255, 255, 255, 0.1); cursor: pointer; transition: all 0.2s; }
.btn-list:hover { background: rgba(255, 255, 255, 0.1); color: white; }
.btn-next { background: #facc15; color: #422006; padding: 10px 24px; border-radius: 12px; font-weight: 900; display: flex; align-items: center; gap: 8px; border: none; cursor: pointer; transition: all 0.2s; }
.btn-next:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(250, 204, 21, 0.3); }

/* 애니메이션 */
.animate-scale-in { animation: scaleIn 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes scaleIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }

.slide-up-enter-active { transition: all 0.4s ease-out; }
.slide-up-enter-from { opacity: 0; transform: translateY(20px); }

.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
</style>
