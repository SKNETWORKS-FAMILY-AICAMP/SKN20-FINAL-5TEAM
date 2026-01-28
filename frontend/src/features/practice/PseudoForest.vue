<!-- 
  수정일: 2026-01-28 
  내용: 3단계 퀘스트 시스템 구축 (Stage 7개 x Step 3개)
  - 스테이지별 심화/꼬리 질문 흐름 적용
  - 객관식(Objective) 및 주관식(Subjective) 입력 방식 지원
  - AI 단계별 피드백 및 3단계 완료 시 다각도 종합 평가 리포트 구현
-->
<template>
  <div class="pseudo-forest-overlay" :style="{ backgroundImage: `url('/image/forest/village_bg.png')` }">
    <div id="game-container" class="forest-glass">
      <!-- 닫기 버튼 -->
      <button @click="$emit('close')" class="btn-close-forest" title="마을 나가기">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>

      <!-- Main Layer -->
      <div id="content-layer">
        <!-- Header: 상태 바 및 프로그레스 -->
        <div id="status-bar">
          <div class="status-item">🏆 점수: <span>{{ totalScore }}</span></div>
          <div class="status-item">🌳 Stage: <span>{{ currentStageIndex + 1 }}/{{ gameData.length }}</span></div>
          <div class="step-indicator">
            <span v-for="s in currentStage.steps.length" :key="s" :class="['step-dot', { active: currentStepIndex + 1 >= s, current: currentStepIndex + 1 === s }]"></span>
          </div>
        </div>

        <!-- 실습 영역 -->
        <div id="game-area">
          <!-- 왼쪽: 주민 인터랙션 -->
          <div id="left-panel">
            <div id="character-container" 
                 @mouseenter="isCharHovered = true" 
                 @mouseleave="isCharHovered = false"
                 :class="{ 'talking': isAnalyzing }">
              <transition name="fade-char" mode="out-in">
                <img :key="isCharHovered" 
                     :src="isCharHovered ? (currentStage.character.hoverImage || currentStage.character.image) : currentStage.character.image" 
                     :alt="currentStage.character.name"
                     class="character-img">
              </transition>
            </div>
            <div id="dialogue-box">
              <div id="speaker-name">{{ currentStage.character.name }}</div>
              <p id="dialogue-text">{{ currentStage.dialogue }}</p>
              <!-- 단계별 질문 텍스트 -->
              <div class="step-question animate-fade-in" :key="currentStepIndex" v-if="currentStep">
                <strong>질문 {{ currentStepIndex + 1 }}:</strong> {{ currentStep.question }}
              </div>
            </div>
          </div>

          <!-- 오른쪽: 응답 및 결과 -->
          <div id="right-panel">
            <!-- 퀘스트 설명 (도움말) [수정일: 2026-01-28] 가시성 보정 -->
            <div id="quest-info" v-if="currentStep.type === 'subjective'">
              <p id="quest-desc" class="dark-text">주민의 질문에 적절한 **의사코드(Pseudo-code)**나 논리를 자유롭게 작성해보세요.</p>
            </div>

            <!-- 입력 영역: 주관식 [수정일: 2026-01-28] Monaco Editor 적용 -->
            <div id="code-section" v-if="currentStep.type === 'subjective'">
              <div class="monaco-forest-container">
                <vue-monaco-editor
                  v-model:value="userResponse"
                  theme="vs-light"
                  language="plaintext"
                  :options="forestEditorOptions"
                  class="forest-monaco-editor"
                  :disabled="isStepFeedbackOpen"
                />
              </div>
            </div>

            <!-- 입력 영역: 파이썬 빈칸 채우기 (4단계) [수정일: 2026-01-28] -->
            <div id="python-fill-input" v-if="currentStep.type === 'python-fill'">
              <p id="quest-desc" class="dark-text">의사코드를 파이썬으로 변환해봅시다. 빈칸을 채워 완성하세요!</p>
              <div class="python-code-block">
                <div class="python-code-content"><template v-for="(part, pIdx) in codeParts" :key="pIdx"><span v-if="part.type === 'text'" class="code-text-part">{{ part.content }}</span><input v-else type="text" class="code-blank-input" v-model="pythonBlanks[part.blankIndex]" :style="{ width: Math.max(40, (pythonBlanks[part.blankIndex] || '').length * 12) + 'px' }" :disabled="isStepFeedbackOpen" /></template></div>
              </div>
            </div>

            <!-- 입력 영역: 객관식 -->
            <div id="objective-section" v-else-if="currentStep.type === 'objective'">
              <div class="options-grid">
                <button 
                  v-for="(opt, idx) in currentStep.options" 
                  :key="idx"
                  class="option-btn"
                  @click="submitObjective(idx)"
                  :disabled="isStepFeedbackOpen"
                >
                  <span class="opt-num">{{ idx + 1 }}</span> {{ opt }}
                </button>
              </div>
            </div>

            <!-- 컨트롤 버튼 (주관식/파이썬 빈칸용) -->
            <div id="controls" v-if="currentStep.type === 'subjective' || currentStep.type === 'python-fill'">
              <!-- [수정일: 2026-01-28] 실시간 AI 오리 가이드 영역 (상시 노출로 변경하여 초기 안내 제공) -->
              <div class="ai-duck-guide animate-fade-in">
                <div class="duck-speech-bubble">
                  <p>{{ duckHint }}</p>
                </div>
                <img src="/image/forest/i_duck_guide.png" alt="AI Duck" class="duck-img">
              </div>

              <button 
                @click="currentStep.type === 'subjective' ? submitSubjective() : submitPythonFill()" 
                class="btn primary"
                :disabled="isAnalyzing || isStepFeedbackOpen"
              >
                {{ isAnalyzing ? 'AI 분석 중...' : '답변 제출하기' }}
              </button>
            </div>
          </div>
        </div>

        <!-- 단계별 AI 피드백 모달 -->
        <transition name="pop">
          <div v-if="isStepFeedbackOpen" id="step-feedback-overlay">
            <div class="step-feedback-card">
              <div class="feedback-header">
                <span class="icon">{{ stepResult.success ? '✅' : '💡' }}</span>
                <h3>{{ stepResult.success ? '훌륭해요!' : '조금 더 생각해볼까요?' }}</h3>
              </div>
              <p class="feedback-msg" v-html="stepResult.message"></p>
              <button @click="proceedNext" class="btn next-btn">
                {{ currentStepIndex < currentStage.steps.length - 1 ? '다음 단계로' : '종합 평가 보기' }}
              </button>
            </div>
          </div>
        </transition>

        <!-- 스테이지 완료 AI 종합 평가 모달 -->
        <transition name="pop">
          <div v-if="isFinalEvalOpen" id="final-eval-overlay">
            <div class="final-eval-card">
              <div class="eval-header">
                <h2>🌳 Stage {{ currentStageIndex + 1 }} 완료 보고서</h2>
                <div class="resident-seal">마을 주민 인증 완료</div>
              </div>
              
              <div class="eval-body">
                <div class="eval-scores">
                  <div class="score-card insight">
                    <div class="card-icon">💡</div>
                    <div class="card-label">통찰력</div>
                    <div class="card-val">{{ finalEval.insight }}</div>
                  </div>
                  <div class="score-card structure">
                    <div class="card-icon">🏗️</div>
                    <div class="card-label">구성력</div>
                    <div class="card-val">{{ finalEval.structure }}</div>
                  </div>
                  <div class="score-card precision">
                    <div class="card-icon">🎯</div>
                    <div class="card-label">정밀도</div>
                    <div class="card-val">{{ finalEval.precision }}</div>
                  </div>
                </div>
                <div class="eval-report-box">
                  <h4>🤖 AI 분석관 리포트</h4>
                  <p v-html="finalEval.report"></p>
                </div>
              </div>

              <div class="eval-footer">
                <button @click="finishStage" class="btn primary">수련 마치고 마을로 (Stage 완료)</button>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue';
import { useGameStore } from '@/stores/game';
import { VueMonacoEditor } from '@guolao/vue-monaco-editor';
import gameData from './PseudoForestData'; // [수정일: 2026-01-28] 외부 데이터 임포트

const emit = defineEmits(['close']);
const game = useGameStore();

// [수정일: 2026-01-28] 내부 gameData 제거 (PseudoForestData.js 사용)

// --- 상태 관리 ---
// [수정일: 2026-01-28] 상태 관리 변수 선언 (순서 최적화)
const currentStageIndex = ref(game.selectedQuestIndex || 0);
const currentStepIndex = ref(0);
const totalScore = ref(0);
const userResponse = ref('');
const pythonBlanks = ref([]);
const isCharHovered = ref(false); // [수정일: 2026-01-28] 캐릭터 호버 상태 추가

// [수정일: 2026-01-28] 동숲 감성 모나코 에디터 옵션 - 가독성 극대화를 위해 폰트 크기 대폭 확대 (28px)
const forestEditorOptions = {
  minimap: { enabled: false },
  fontSize: 28,
  lineNumbers: 'off',
  glyphMargin: false,
  folding: false,
  lineDecorationsWidth: 0,
  lineNumbersMinChars: 0,
  wordWrap: 'on',
  scrollbar: { vertical: 'hidden', horizontal: 'hidden' },
  scrollBeyondLastLine: false,
  automaticLayout: true,
  placeholder: "여기에 답변을 작성하세요...",
  fontFamily: "'Gaegu', cursive, 'Jua', sans-serif"
};

const currentStage = computed(() => gameData[currentStageIndex.value]);
const currentStep = computed(() => {
  if (!currentStage.value || !currentStage.value.steps) return null;
  return currentStage.value.steps[currentStepIndex.value] || null;
});

// [수정일: 2026-01-28] 파이썬 코드를 텍스트와 빈칸(input)으로 조각내기
const codeParts = computed(() => {
  if (!currentStep.value || currentStep.value.type !== 'python-fill') return [];
  const snippet = currentStep.value.codeSnippet || '';
  const parts = [];
  const splitPattern = /{{blank}}/;
  const splitTexts = snippet.split(splitPattern);
  
  splitTexts.forEach((text, i) => {
    // 텍스트 추가
    parts.push({ type: 'text', content: text });
    // 마지막 텍스트가 아니면 빈칸 추가
    if (i < splitTexts.length - 1) {
      parts.push({ type: 'blank', blankIndex: i });
    }
  });
  return parts;
});

// [수정일: 2026-01-28] 다음 단계로 넘어갈 때 빈칸 모델 초기화 (방어 코드 추가)
watch(() => currentStepIndex.value, (newIdx) => {
  if (!currentStep.value || currentStep.value.type !== 'python-fill') return;
  
  // 이미 값이 있으면 유지, 없으면 빈 문자열로 초기화
  const snippet = currentStep.value.codeSnippet || '';
  const blankCount = (snippet.match(/{{blank}}/g) || []).length;
  if (pythonBlanks.value.length !== blankCount) {
    pythonBlanks.value = new Array(blankCount).fill('');
  }
}, { immediate: true });

// [수정일: 2026-01-28] 실시간 오리 힌트 상태 관리 (데이터 주도형으로 개편)
const duckHint = computed(() => {
  const step = currentStep.value;
  if (!step) return "새마을 정신으로 일하면 못할 게 없슈! 논리적으로 차근차근 써보세유.";

  if (step.type === 'subjective') {
    const resp = userResponse.value.trim().toLowerCase();
    if (resp.length === 0) return "이장님, 뭐라도 적어보슈! 내가 옆에서 도와줄게유~";
    
    // 핵심 키워드가 포함되었을 때 (데이터 기반 리액션)
    const hits = step.evalCriteria.insightKeywords.filter(kw => resp.includes(kw));
    if (hits.length > 0) return `오! '${hits[0]}' 같은 핵심을 잘 짚으셨구먼유. 계속 가보슈!`;
    
    // 입력이 길어지는데 키워드가 없을 때 보조 힌트
    if (resp.length > 20) return "오호, 말이 길어지는 걸 보니 뭔가 생각 중이시구먼유? 키워드를 좀 더 섞어보슈!";
    
    return step.duckEncouragement || "새마을 정신으로 일하면 못할 게 없슈! 논리적으로 차근차근 써보세유.";
  }

  if (step.type === 'python-fill') {
    const filledCount = pythonBlanks.value.filter(b => b && b.trim()).length;
    if (filledCount === 0) return step.duckEncouragement || "파이썬으로 빈칸을 채워보슈! 실력이 아주 일취월장 하셨구먼유.";
    if (filledCount < step.blanks.length) return "그렇쥬! 빈칸을 마저 채우면 완벽한 코드가 되겠구먼유. 힘내슈!";
    return "오오, 다 채우셨구먼유! 이제 '답변 제출하기'를 눌러 검사를 받아보슈.";
  }
  
  return "새마을 정신으로 일하면 못할 게 없슈! 논리적으로 차근차근 써보세유.";
});

const isAnalyzing = ref(false);
const isStepFeedbackOpen = ref(false);
const isFinalEvalOpen = ref(false);

const stepResult = ref({ success: false, message: '' });
const finalEval = ref({ insight: 0, structure: 0, precision: 0, report: '' });
const stageLogs = ref([]); // 현재 스테이지의 3단계 답변 및 평가 로그


// --- 핸들러: 주관식 제출 ---
const submitSubjective = () => {
  // [수정일: 2026-01-28] 빈 입력값에 대한 예외 처리 및 사용자 안내 추가 (무반응 현상 해결)
  if (!userResponse.value.trim()) {
    stepResult.value = { 
      success: false, 
      message: "이장님, 뭐라도 적어주셔야 마을 정비를 할 수 있어유! 빈 칸으론 안 돼유~" 
    };
    isStepFeedbackOpen.value = true;
    return;
  }
  isAnalyzing.value = true;

  // AI 분석 시뮬레이션
  setTimeout(() => {
    const code = userResponse.value.toLowerCase();
    const criteria = currentStep.value.evalCriteria;
    
    let score = 0;
    if (criteria.insightKeywords.some(kw => code.includes(kw))) score += 40;
    if (criteria.structureKeywords.some(kw => code.includes(kw))) score += 40;
    if (criteria.precisionKeywords.some(kw => code.includes(kw))) score += 20;

    const success = score >= 60;
    const msg = success 
      ? `<strong>AI 통찰:</strong> 논리적 키워드가 정확합니다! 단계별 요구사항을 완벽히 이해하셨네요.`
      : `<strong>AI 조언:</strong> 핵심 개념인 '${criteria.insightKeywords[0]}' 등에 대해 조금 더 명확히 서술해보세요.`;

    stepResult.value = { success, message: msg, rawScore: score, response: userResponse.value };
    stageLogs.value.push(stepResult.value);
    
    isAnalyzing.value = false;
    isStepFeedbackOpen.value = true;
    totalScore.value += score;
  }, 1000);
};

// --- 핸들러: 객관식 제출 ---
const submitObjective = (idx) => {
  const isCorrect = idx === currentStep.value.correctIndex;
  const score = isCorrect ? 100 : 20;
  
  stepResult.value = { 
    success: isCorrect, 
    message: isCorrect 
      ? `정답입니다! 🎯<br>${currentStep.value.explanation}`
      : `아쉽습니다. 정답은 <strong>'${currentStep.value.options[currentStep.value.correctIndex]}'</strong>입니다.<br>${currentStep.value.explanation}`,
    rawScore: score,
    response: currentStep.value.options[idx]
  };
  
  stageLogs.value.push(stepResult.value);
  isStepFeedbackOpen.value = true;
  totalScore.value += score;
};

// --- 핸들러: 파이썬 빈칸 제출 [수정일: 2026-01-28] ---
const submitPythonFill = () => {
  const blanks = currentStep.value.blanks;
  if (pythonBlanks.value.length < blanks.length || pythonBlanks.value.some(b => !b?.trim())) {
    stepResult.value = { success: false, message: "빈칸을 모두 채워주셔야 마을 정비가 끝나유!" };
    isStepFeedbackOpen.value = true;
    return;
  }

  isAnalyzing.value = true;
  setTimeout(() => {
    let correctCount = 0;
    pythonBlanks.value.forEach((val, idx) => {
      if (val.trim() === blanks[idx]) correctCount++;
    });

    const success = correctCount === blanks.length;
    const score = Math.round((correctCount / blanks.length) * 100);
    
    stepResult.value = {
      success,
      message: success 
        ? "<strong>AI 통찰:</strong> 완벽한 파이썬 코드구먼유! 의사코드의 논리를 정확히 이해하셨네유."
        : `<strong>AI 조언:</strong> 조금 아깝구먼유! ${blanks.length - correctCount}개가 틀려슈. 문법을 다시 한 번 확인해보슈!`,
      rawScore: score,
      response: pythonBlanks.value.join(', ')
    };

    stageLogs.value.push(stepResult.value);
    isAnalyzing.value = false;
    isStepFeedbackOpen.value = true;
    totalScore.value += score;
  }, 1000);
};

// --- 다음 단계 또는 종합 평가로 이동 ---
const proceedNext = () => {
  isStepFeedbackOpen.value = false;
  userResponse.value = '';
  
  const stepCount = currentStage.value.steps.length;
  if (currentStepIndex.value < stepCount - 1) {
    currentStepIndex.value++;
  } else {
    // 현재 스테이지 모든 단계 완료 -> 종합 평가 생성
    generateFinalEvaluation();
  }
};

/**
 * [수정일: 2026-01-28] 3단계 답변 로그를 기반으로 다각도 AI 최종 리포트 생성
 */
const generateFinalEvaluation = () => {
  const totalRaw = stageLogs.value.reduce((acc, log) => acc + log.rawScore, 0);
  
  // [수정일: 2026-01-28] 단계 수에 따른 유연한 분석 로직 적용 (3단계 vs 4단계 대응)
  const stepCount = stageLogs.value.length;
  const step1 = stageLogs.value[0] || { rawScore: 0 };
  const step2 = stageLogs.value[1] || { rawScore: 0 };
  const step3 = stageLogs.value[2] || { rawScore: 0 };
  const step4 = stageLogs.value[3] || null; // 4단계가 없을 수 있음

  // Step 1: 통찰력 (Insight)
  const insight = Math.min(Math.round(step1.rawScore * 1.1), 100);
  
  // Step 2 & 3: 구성력 (Structure)
  let structure = 0;
  if (step2 && !step4) {
    // 3단계 구성일 경우 2단계를 구성력의 핵심으로 평가
    structure = Math.min(Math.round(step2.rawScore * 1.05), 100);
  } else {
    structure = Math.min(Math.round(((step2.rawScore + step3.rawScore) / 2) * 1.05), 100);
  }
  
  // Step 3 or 4: 정밀도 (Precision)
  const precision = step4 ? step4.rawScore : step3.rawScore;

  const avg = (insight + structure + precision) / 3;
  
  // [수정일: 2026-01-28] 데이터에 appraisal 정보가 없을 경우를 위한 폴백 처리
  const appraisal = currentStage.value?.finalAppraisal || {
    overallSummary: { high: "훌륭한 논리력입니다!", mid: "준수한 실력이군요.", low: "조금 더 연습해봅시다." },
    insightMentions: { high: "핵심을 꿰뚫는 통찰력이 보입니다.", low: "기본적인 접근은 좋았습니다." },
    structureMentions: { high: "구조적인 설계가 매우 안정적입니다.", low: "구성 단계를 차근차근 밟아보세요." },
    precisionMentions: { high: "정밀한 구현 능력이 돋보입니다.", low: "세부적인 구현에 주의를 기울여주세요." }
  };

  // 개인화된 분석 리포트 생성 (데이터 기반)
  let comment = "";
  if (avg >= 90) comment = appraisal.overallSummary.high;
  else if (avg >= 70) comment = appraisal.overallSummary.mid;
  else comment = appraisal.overallSummary.low;

  finalEval.value = {
    insight,
    structure,
    precision,
    report: `<div class="report-main-title">[${currentStage.value?.character?.name || '마을'} 스테이지 분석]</div>` +
            `<ul class="report-list">` +
            `<li><strong>통찰 분석:</strong> ${insight >= 80 ? appraisal.insightMentions.high : appraisal.insightMentions.low}</li>` +
            `<li><strong>논리 구성:</strong> ${structure >= 80 ? appraisal.structureMentions.high : appraisal.structureMentions.low}</li>` +
            `<li><strong>실전 구현:</strong> ${precision >= 80 ? appraisal.precisionMentions.high : appraisal.precisionMentions.low}</li>` +
            `</ul>` +
            `<div class="report-summary"><strong>🤖 총평:</strong> ${comment}</div>`
  };
  
  isFinalEvalOpen.value = true;
};

// --- 스테이지 완료 및 다음 해금 ---
const finishStage = () => {
  isFinalEvalOpen.value = false;
  
  // gameStore 연동: 현재 스테이지 완료 처리 및 다음 해금
  game.unlockNextStage('Pseudo Forest', currentStageIndex.value);
  
  // [수정일: 2026-01-28] 스테이지 완료 후 즉시 창을 닫아 맵에서 해금 상태를 확인하도록 변경
  emit('close');
};

</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Gaegu:wght@400;700&family=Nanum+Gothic+Coding:wght@400;700&display=swap');

.pseudo-forest-overlay {
  position: fixed; inset: 0; background-size: cover; background-position: center; z-index: 2000;
  display: flex; align-items: center; justify-content: center; padding: 20px; font-family: 'Gaegu', cursive;
}
.pseudo-forest-overlay::before { content: ''; position: absolute; inset: 0; background: rgba(0, 0, 0, 0.45); backdrop-filter: blur(8px); }

#game-container {
  position: relative; width: 100%; max-width: 1100px; height: 90vh;
  background: rgba(255, 255, 255, 0.88); backdrop-filter: blur(20px);
  border-radius: 40px; border: 8px solid #5d4037; box-shadow: 0 40px 100px rgba(0,0,0,0.5);
  overflow: hidden; display: flex; flex-direction: column;
}

.btn-close-forest {
  position: absolute; top: 20px; right: 20px; background: #8b4513; color: white;
  width: 44px; height: 44px; border-radius: 12px; border: none; cursor: pointer;
  z-index: 10; display: flex; align-items: center; justify-content: center; transition: 0.3s;
}
.btn-close-forest:hover { transform: scale(1.1) rotate(90deg); background: #d32f2f; }

#content-layer { flex: 1; display: flex; flex-direction: column; padding: 30px; }

#status-bar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 30px; background: #795548; color: white; border-radius: 20px; margin-bottom: 20px;
}
.status-item span { font-weight: 800; color: #ffeb3b; }

.step-indicator { display: flex; gap: 10px; }
.step-dot { width: 12px; height: 12px; border-radius: 50%; background: rgba(255,255,255,0.3); transition: 0.4s; }
.step-dot.active { background: #ffeb3b; }
.step-dot.current { box-shadow: 0 0 15px #ffeb3b; transform: scale(1.3); }

#game-area { flex: 1; display: grid; grid-template-columns: 1fr 1.2fr; gap: 30px; min-height: 0; }

#left-panel { display: flex; flex-direction: column; gap: 20px; overflow-y: auto; }
#character-container { flex: 1; display: flex; align-items: center; justify-content: center; transition: 0.3s; cursor: pointer; }
.character-img { 
  max-height: 250px; 
  filter: drop-shadow(0 10px 20px rgba(0,0,0,0.2)); 
  transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
#character-container:hover .character-img { 
  transform: scale(1.15) rotate(3deg); 
  filter: drop-shadow(0 20px 40px rgba(0,0,0,0.3));
}
#character-container.talking { animation: bounce 0.5s infinite alternate; }

/* 캐릭터 페이드 전환 애니메이션 [수정일: 2026-01-28] */
.fade-char-enter-active, .fade-char-leave-active { transition: opacity 0.2s ease; }
.fade-char-enter-from, .fade-char-leave-to { opacity: 0; }

#dialogue-box {
  background: #fff9c4; border: 4px solid #fbc02d; border-radius: 20px; padding: 20px; position: relative;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}
#speaker-name { position: absolute; top: -20px; left: 20px; background: #f9a825; color: white; padding: 5px 20px; border-radius: 12px; font-weight: 800; font-size: 1.1rem; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
#dialogue-text { font-size: 1.8rem; font-weight: 700; margin-bottom: 12px; color: #5d4037; line-height: 1.6; }
.step-question { font-size: 2rem; font-weight: 800; color: #1b5e20; border-top: 3px dashed #fbc02d; padding-top: 15px; line-height: 1.5; }

#right-panel { display: flex; flex-direction: column; gap: 20px; }
#code-section { flex: 1; display: flex; flex-direction: column; min-height: 400px; }

#quest-desc { 
  font-size: 1.8rem; 
  font-weight: 800; 
  margin-bottom: 10px; 
  color: #5d4037; 
  line-height: 1.6;
  text-shadow: 1px 1px 0px rgba(255,255,255,0.5);
}
.dark-text { color: #5d4037 !important; font-weight: 800; } 

/* 모나코 에디터 동숲 테마 컨테이너 [수정일: 2026-01-28] */
.monaco-forest-container {
  background: #fff9c4;
  border: 8px solid #8d6e63; /* 나무색 두꺼운 테두리 */
  border-radius: 30px;
  padding: 15px;
  box-shadow: 
    inset 0 0 20px rgba(0,0,0,0.1),
    0 10px 20px rgba(0,0,0,0.2);
  flex: 1;
  overflow: hidden;
  position: relative;
  display: flex;
}

.monaco-forest-container::after {
  content: '🍃';
  position: absolute;
  top: 10px;
  right: 15px;
  font-size: 1.5rem;
  z-index: 10;
  opacity: 0.8;
}

.forest-monaco-editor {
  width: 100%;
  height: 100%;
}

/* 모나코 내부 배경 투명화 및 폰트 보정 */
:deep(.monaco-editor), :deep(.monaco-editor-background), :deep(.monaco-editor .margin) {
  background-color: #fff9c4 !important;
}
:deep(.monaco-editor .view-line) {
  color: #5d4037 !important;
}

#code-input { display: none; } /* 기존 input 제거 */

/* [수정일: 2026-01-28] 실시간 AI 오리 가이드 스타일 - 에디터와 너비 맞춤 및 오리 크기 조정 */
.ai-duck-guide {
  display: flex;
  align-items: flex-end; /* 말풍선 바닥과 오리 바닥 정렬 */
  justify-content: space-between;
  gap: 15px;
  margin-top: 15px;
  margin-bottom: 5px;
  width: 100%;
}
.duck-speech-bubble {
  flex: 1; /* 가용한 너비 모두 차지 */
  background: #fff9c4;
  border: 4px solid #fbc02d;
  padding: 15px 20px;
  border-radius: 24px;
  font-size: 1.5rem;
  font-weight: 700;
  color: #5d4037;
  line-height: 1.5;
  box-shadow: 0 6px 15px rgba(0,0,0,0.1);
  position: relative;
}

/* 말풍선 꼬리 추가하여 생동감 부여 */
.duck-speech-bubble::after {
  content: '';
  position: absolute;
  bottom: 20px;
  right: -15px;
  border-left: 15px solid #fbc02d;
  border-top: 10px solid transparent;
  border-bottom: 10px solid transparent;
}
.duck-img {
  width: 130px; /* 더 크게 확대 (100px -> 130px) */
  height: 130px;
  object-fit: contain;
  filter: drop-shadow(0 8px 16px rgba(0,0,0,0.2));
  flex-shrink: 0;
  margin-bottom: -10px; /* 위치 상향 조정 */
  transition: transform 0.3s ease;
}
.duck-img:hover {
  transform: scale(1.1) rotate(5deg);
}

/* 객관식 스타일 */
.options-grid { display: flex; flex-direction: column; gap: 15px; }
.option-btn {
  background: white; border: 3px solid #e0e0e0; border-radius: 15px; padding: 15px 25px;
  font-family: inherit; font-size: 1.4rem; color: #5d4037; cursor: pointer; text-align: left;
  display: flex; align-items: center; gap: 15px; transition: 0.2s;
}
.option-btn:hover:not(:disabled) { transform: translateX(10px); background: #fffde7; border-color: #fbc02d; }
.opt-num { background: #f5f5f5; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; border-radius: 50%; font-weight: 800; }

.btn {
  width: 100%; padding: 15px; border-radius: 20px; font-family: inherit; font-size: 1.5rem; font-weight: 800;
  cursor: pointer; border: none; box-shadow: 0 8px 0 rgba(0,0,0,0.1); transition: 0.2s;
}
.btn.primary { background: #fbc02d; color: #5d4037; }
.btn.primary:hover { transform: translateY(-3px); box-shadow: 0 11px 0 rgba(0,0,0,0.1); background: #fdd835; }
.btn:active { transform: translateY(5px); box-shadow: 0 3px 0 rgba(0,0,0,0.1); }

/* 모달 및 피드백 */
#step-feedback-overlay, #final-eval-overlay {
  position: absolute; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 100;
  padding: 40px;
}
.step-feedback-card, .final-eval-card {
  background: white; border-radius: 30px; padding: 40px; max-width: 600px; width: 100%;
  border: 6px solid #8b4513; animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.feedback-header { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
.feedback-header .icon { font-size: 3rem; }
.feedback-msg { font-size: 1.3rem; line-height: 1.6; color: #5d4037; margin-bottom: 30px; }

/* 평가 보고서 콤팩트화 [수정일: 2026-01-28] */
.final-eval-card { max-width: 650px; background: #fffdf9; border: 6px solid #8b4513; padding: 25px; }
.eval-header { 
  display: flex; justify-content: space-between; align-items: center; 
  padding-bottom: 12px; border-bottom: 3px double #deb887; margin-bottom: 20px;
}
.eval-header h2 { color: #5d4037; font-size: 2.22rem; margin: 0; }

/* 주민 인증 도장 크기 축소 */
.resident-seal { 
  width: 80px; height: 80px;
  border: 4px solid #d32f2f; color: #d32f2f; 
  font-weight: 900; font-size: 1rem;
  display: flex; align-items: center; justify-content: center; text-align: center;
  border-radius: 50%; background: rgba(211, 47, 47, 0.03);
  transform: rotate(-15deg);
  box-shadow: 0 0 0 2px white, 0 0 0 4px #d32f2f;
  line-height: 1.1;
  position: relative;
}
.resident-seal::after {
  content: '인';
  position: absolute; bottom: 6px; right: 6px; font-size: 0.7rem; opacity: 0.6;
}

/* 점수 카드 크기 축소 */
.eval-scores { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 25px; }
.score-card {
  background: white; padding: 15px 10px; border-radius: 20px;
  border: 3px solid #deb887; text-align: center;
  transition: 0.3s; box-shadow: 0 3px 6px rgba(0,0,0,0.05);
}
.score-card:hover { transform: translateY(-3px); box-shadow: 0 6px 12px rgba(0,0,0,0.1); border-color: #fbc02d; }
.card-icon { font-size: 2rem; margin-bottom: 4px; }
.card-label { font-size: 1.2rem; font-weight: 800; color: #8b4513; margin-bottom: 4px; }
.card-val { font-size: 2.8rem; font-weight: 900; color: #2e7d32; text-shadow: 1.5px 1.5px 0 #e8f5e9; }

/* 리포트 박스 크기 및 여백 최적화 */
.eval-report-box { 
  background: #fff9c4; padding: 20px 25px; border-radius: 20px; 
  border: 3px solid #fbc02d; box-shadow: inset 0 2px 8px rgba(0,0,0,0.05); 
}
.eval-report-box h4 { 
  margin-bottom: 12px; color: #5d4037; font-size: 1.5rem; 
  display: flex; align-items: center; gap: 10px;
  border-bottom: 2px solid rgba(139, 69, 19, 0.1); padding-bottom: 8px;
}
.eval-report-box p { 
  margin: 0;
}
:deep(.report-main-title) {
  font-size: 1.25rem; color: #d84315; font-weight: 800; margin-bottom: 8px;
}
:deep(.report-list) {
  list-style: none; padding: 0; margin: 0 0 12px 0;
}
:deep(.report-list li) {
  line-height: 1.4; font-size: 1.2rem; color: #4e342e; margin-bottom: 6px;
  position: relative; padding-left: 18px; font-weight: 700;
}
:deep(.report-list li::before) {
  content: '•'; position: absolute; left: 0; color: #fbc02d; font-size: 1.4rem;
}
:deep(.report-summary) {
  border-top: 2px dashed rgba(139, 69, 19, 0.1);
  padding-top: 12px; line-height: 1.4; font-size: 1.3rem; color: #4e342e;
  font-weight: 800; word-break: keep-all;
}
:deep(.eval-report-box strong) { color: #d84315; }

.eval-footer { margin-top: 15px; }
.eval-footer .btn { font-size: 1.5rem; padding: 12px; }

@keyframes popIn { from { opacity: 0; transform: scale(0.8); } to { opacity: 1; transform: scale(1); } }
@keyframes bounce { from { transform: translateY(0); } to { transform: translateY(-10px); } }

/* [수정일: 2026-01-28] 파이썬 빈칸 채우기 스타일 */
.python-code-block {
  background: #23241f; color: #f8f8f2; padding: 25px; border-radius: 20px;
  font-family: 'Nanum Gothic Coding', monospace; font-size: 1.1rem; line-height: 1.6;
  overflow-x: auto; border: 4px solid #5d4037; box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
}
.python-code-content {
  white-space: pre; word-break: normal; margin: 0;
  display: block; font-family: 'Nanum Gothic Coding', monospace;
  font-size: 1.1rem; line-height: 1.8;
}
.code-text-part {
  display: inline; white-space: pre;
}
.code-blank-input {
  background: #3e3e3e; border: 2px solid #fbc02d; color: #ffeb3b;
  padding: 1px 8px; border-radius: 6px; font-family: inherit; font-size: 1.1rem;
  transition: 0.3s; margin: 0 4px; outline: none;
  vertical-align: middle; display: inline-block;
  box-sizing: border-box; position: relative; top: -1px;
}
.code-blank-input:focus { background: #4e4e4e; box-shadow: 0 0 10px #fbc02d; border-color: #fdd835; }

.animate-fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
