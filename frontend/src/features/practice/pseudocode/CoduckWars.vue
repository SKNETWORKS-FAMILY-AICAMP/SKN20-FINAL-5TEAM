<template>
  <div class="coduck-wars-container">
    <!-- BACKGROUND WATERMARK -->
    <div class="bg-watermark">시스템 오류</div>
    <div class="scan-line"></div>

    <!-- HEADER -->
    <header class="war-room-header">
      <div class="chapter-info">
        <span class="chapter-title">CHAPTER 1: 각성 (튜토리얼 존)</span>
        <span class="sub-info">프로토콜: AI 사고법 입문 [BOOT_PROTOCOL]</span>
      </div>
      <div class="integrity-monitor">
        <span class="integrity-label">정화 무결성</span>
        <div class="hp-bar-bg">
             <div class="hp-bar-fill" :style="{ width: Math.max(0, gameState.playerHP) + '%' }"></div>
        </div>
        <span class="integrity-val">{{ Math.max(0, gameState.playerHP) }}%</span>
      </div>
    </header>

    <!-- MAIN VIEWPORT -->
    <main class="viewport">
      
      <!-- PHASE: DIAGNOSTIC 1 & 2 (Shared Layout) -->
      <section v-if="gameState.phase.startsWith('DIAGNOSTIC')" class="combat-grid">
         <!-- LEFT: Entity Card -->
        <div class="panel entity-card">
           <div class="entity-header">
              <span class="entity-label">개체명: 코덕</span>
              <span class="entity-status">⚠ 불안정</span>
           </div>
           <div class="visual-frame">
              <img src="/assets/characters/coduck_sad.png" class="coduck-portrait" />
              <div class="scan-overlay"></div>
              <div class="disconnect-tag">! 연결 끊김 !</div>
           </div>
           <div class="dialogue-box">
              <span class="speaker">Coduck</span>
              <p class="dialogue-text">"{{ gameState.coduckMessage }}"</p>
           </div>
        </div>

        <!-- RIGHT: Decision Engine -->
        <div class="panel decision-panel">
          <!-- Background Decor -->
          <div class="grid-overlay"></div>
          
          <div class="panel-top-bar">
             <div class="system-status-text">_ 진단 프로토콜 활성화</div>
          </div>
          
          <div class="question-zone">
             <div class="decorative-corner top-left"></div>
             <div class="decorative-corner bottom-right"></div>
             <h1 class="big-question">
                {{ currentDiagnosticQuestion.question }}
             </h1>
          </div>

          <div class="options-list">
             <button 
               v-for="(opt, idx) in currentDiagnosticQuestion.options" 
               :key="idx"
               class="option-card"
               @click="handleDiagnosticSubmit(idx)"
             >
                <div class="opt-index">0{{ idx + 1 }}</div>
                <div class="opt-content">
                    <div class="opt-main">{{ opt.text }}</div>
                    <div class="opt-desc" v-if="opt.bullets && opt.bullets.length > 0">
                        {{ opt.bullets[0] }}
                    </div>
                </div>
                <div class="opt-arrow">→</div>
             </button>
          </div>

           <!-- Expanded Footer: System Log -->
          <div class="tactical-console">
             <div class="console-header">/// 시스템 이벤트 로그 ///</div>
             <div class="console-body">
                <transition-group name="log-fade">
                   <div 
                       v-for="(log, idx) in gameState.systemLogs" 
                       :key="idx" 
                       class="log-line"
                       :class="{ 'active-line': idx === gameState.systemLogs.length - 1 }"
                   >
                       <span class="t-time">{{ log.time }}</span> 
                       <span :class="getLogTypeClass(log.type)">[{{ getLogLabel(log.type) }}]</span> 
                       {{ log.message }}
                       <span v-if="idx === gameState.systemLogs.length - 1" class="cursor-blink">_</span>
                   </div>
                </transition-group>
             </div>
          </div>
        </div>
      </section>

      <!-- PHASE: LOGIC DESIGN (Phase 3) - REFINED LAYOUT -->
      <section v-if="gameState.phase === 'PSEUDO_WRITE'" class="combat-grid">
          <!-- LEFT: Standard Entity Card (Reusing Phase 1/2 Size) -->
          <div class="panel entity-card">
             <div class="entity-header">
                <span class="entity-label">목표: 정밀 아키텍처 설계</span>
                <span class="entity-status">자연어 분석 중</span>
             </div>
             
             <!-- 1. Visual Frame -->
             <div class="visual-frame">
                <img src="/assets/characters/coduck_sad.png" class="coduck-portrait" />
                <div class="scan-overlay"></div>
                <div class="disconnect-tag">! 분석 대기 !</div>
             </div>



             <!-- 3. Mission Box -->
             <div class="mission-problem-box">
                <h3 class="mp-title">미션 목표: 사고 과정 상세 분석</h3>
                <div class="mp-content">
                    <p class="mp-desc">
                        제기된 [제약 사건]을 해결하기 위한 공학적 의사결정을 오른쪽 에디터에 상세히 서술하십시오.
                    </p>
                </div>
             </div>
          </div>
          
          <!-- RIGHT: Decision Panel + Logic Briefing -->
          <div class="panel decision-panel full-width-panel">
             <div class="panel-header-row">
                 <span class="p-title-small">아키텍처 설계 (자연어 서술 모드)</span>
                 <span class="p-sub-small badge-natural">Python 코드 금지</span>
             </div>

             <!-- Top Briefing Zone (Incident + Rules) -->
             <div class="top-briefing-zone">
                <div class="briefing-section">
                    <div class="briefing-label"><span class="b-icon">🚨</span> 제약 사건 (Current Incident)</div>
                    <p class="incident-text">{{ gameState.missionContext }}</p>
                </div>
                
                <div class="briefing-divider"></div>

                <div class="briefing-section">
                    <div class="briefing-label"><span class="b-icon">⚙️</span> 핵심 설계 원칙 (Engineering Rules)</div>
                    <p class="briefing-sub">아래 원칙을 반드시 준수하여 설계 리포트를 작성하십시오.</p>
                    <ul class="briefing-list">
                        <li v-for="(cons, i) in gameState.constraints" :key="i">{{ cons }}</li>
                    </ul>
                </div>
             </div>

             <div class="monaco-wrapper">
                <div class="line-numbers">
                    <span v-for="n in 15" :key="n">{{ n }}</span>
                </div>
                <textarea 
                    :value="gameState.phase3Reasoning"
                    @input="handlePseudoInput"
                    class="monaco-textarea"
                    placeholder="여기에 한글이나 영어로 본인의 사고 과정을 서술하세요. (예: 1. 먼저 스케일러를...)"
                    spellcheck="false"
                ></textarea>
             </div>



             <div class="editor-action-bar">
                <div class="writing-notice">※ 코드가 아닌 '말(설명)'로 적어주세요.</div>
                <button class="btn-execute-large" @click="submitPseudo">
                    <span class="btn-text">설계 확정 및 AI 제출</span>
                    <span class="btn-icon">→</span>
                </button>
             </div>
          </div>
      </section>

      <!-- PHASE: IMPLEMENTATION BLUEPRINT (Phase 4) -->
      <section v-if="gameState.phase === 'PYTHON_FILL'" class="combat-grid">
         <!-- LEFT: Entity Card -->
         <div class="panel entity-card">
              <div class="entity-header">
                  <span class="entity-label">개체명: 코덕</span>
                  <span class="entity-status">모니터링 중</span>
              </div>
              <div class="visual-frame">
                  <img src="/assets/characters/coduck_sad.png" class="coduck-portrait" />
                  <div class="scan-overlay"></div>
                  <div class="disconnect-tag">! 동기화됨 !</div>
              </div>
              <div class="dialogue-box">
                  <span class="speaker">Coduck</span>
                  <p class="dialogue-text">"{{ gameState.coduckMessage }}"</p>
              </div>
         </div>

         <!-- RIGHT: Implementation Panel -->
         <div class="panel implementation-panel">
            <div class="panel-header-row">
                <span class="p-title">구현 (IMPLEMENTATION)</span>
                <span class="p-sub">참조: 3단계 로직</span>
            </div>
            
            <div class="split-view">
                <!-- Column 1: Commented Logic (Guide) -->
                <div class="logic-viewer">
                    <div class="viewer-header">/// 로직 추적 ///</div>
                    <div class="commented-content">
                        <div v-for="(line, i) in commentedLogicLines" :key="i" class="code-line comment-style">{{ line }}</div>
                    </div>
                </div>

                <!-- Column 2: Code Editor -->
                <div class="code-editor-area">
                    <div class="code-header">def leakage_free_scaling(train_df, test_df):</div>
                    
                    <!-- Slot 1 -->
                    <div class="code-block">
                        <div class="comment-line"># 1. 학습 데이터(train) 기준으로 스케일러 생성</div>
                        <div 
                            class="drop-zone"
                            :class="{ 'filled': gameState.codeSlots.slot1.content }"
                            @dragover.prevent
                            @drop="onDrop('slot1', $event)"
                        >
                            {{ gameState.codeSlots.slot1.content || "▼ [ 스케일러 생성 코드를 드래그 ] ▼" }}
                        </div>
                    </div>

                    <!-- Slot 2 -->
                    <div class="code-block">
                        <div class="comment-line"># 2. 학습 데이터로만 기준 학습 (fit)</div>
                        <div 
                            class="drop-zone"
                            :class="{ 'filled': gameState.codeSlots.slot2.content }"
                            @dragover.prevent
                            @drop="onDrop('slot2', $event)"
                        >
                             {{ gameState.codeSlots.slot2.content || "▼ [ 기준 학습(fit) 코드를 드래그 ] ▼" }}
                        </div>
                    </div>

                    <!-- Slot 3 -->
                    <div class="code-block">
                        <div class="comment-line"># 3. 동일한 기준을 학습 데이터에 적용 (transform)</div>
                        <div 
                            class="drop-zone"
                            :class="{ 'filled': gameState.codeSlots.slot3.content }"
                            @dragover.prevent
                            @drop="onDrop('slot3', $event)"
                        >
                             {{ gameState.codeSlots.slot3.content || "▼ [ 학습 데이터 반환 코드를 드래그 ] ▼" }}
                        </div>
                    </div>

                    <!-- Slot 4 -->
                    <div class="code-block">
                        <div class="comment-line"># 4. 동일한 기준을 테스트 데이터에 적용 (transform)</div>
                         <div 
                            class="drop-zone"
                            :class="{ 'filled': gameState.codeSlots.slot4.content }"
                            @dragover.prevent
                            @drop="onDrop('slot4', $event)"
                        >
                             {{ gameState.codeSlots.slot4.content || "▼ [ 테스트 데이터 반환 코드를 드래그 ] ▼" }}
                        </div>
                    </div>

                    <div class="code-footer">return train_scaled, test_scaled</div>
                </div>

                <!-- Column 3: Snippets (Draggable Modules) -->
                <div class="modules-sidebar">
                    <div class="phase-header-green-small">모듈 (MODULES)</div>
                    <div class="snippet-list-scroll">
                        <div 
                            v-for="(snip, idx) in pythonSnippets" 
                            :key="idx" 
                            class="snippet-block" 
                            draggable="true"
                            @dragstart="handleDragStart($event, snip.code)"
                            @click="insertSnippet(snip.code)"
                        >
                            <span class="s-icon">::</span>
                            <span class="s-label">{{ snip.label }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Bottom Action Bar -->
            <div class="action-bar-bottom">
                 <div class="error-console" v-if="gameState.feedbackMessage">
                      <span class="bad-signal">시스템 경고 >></span> {{ gameState.feedbackMessage }}
                 </div>
                 <div v-else style="flex:1"></div>

                 <div class="btn-group">
                      <button class="btn-reset" @click="initPhase4Scaffolding">초기화</button>
                      <button class="btn-execute" @click="submitPythonFill">코드 배포</button>
                 </div>
            </div>
         </div>
      </section>

      <!-- PHASE: DEEP DIVE (Phase 5) -->
      <section v-if="gameState.phase === 'DEEP_QUIZ'" class="combat-grid centered-layout">
         <div class="panel center-panel">
           <div class="phase-header-gold">최종 검증</div>
           <div class="panel-content centered-content">
             <h1 class="big-question-center">
                {{ deepQuizQuestion.question }}
             </h1>
             
             <div class="options-list options-wide">
                <button 
                  v-for="(opt, idx) in deepQuizQuestion.options" 
                  :key="idx"
                  class="option-card gold-hover"
                  @click="submitDeepQuiz(idx)"
                >
                   <div class="opt-index gold-idx">0{{ idx + 1 }}</div>
                   <div class="opt-content">
                        <div class="opt-main">{{ opt.text }}</div>
                   </div>
                </button>
             </div>
           </div>
         </div>
      </section>
      
      <!-- PHASE: EVALUATION (Refined with 2nd/3rd Reference Style) -->
      <section v-if="gameState.phase === 'EVALUATION'" class="panel evaluation-view">
         <div class="report-card">
            <!-- Header Stamp -->
            <div class="report-header">
                <span class="report-title">시스템 복구 리포트</span>
                <div class="stamp-box" :class="{ 'stamp-success': evaluationResult.finalScore >= 50, 'stamp-fail': evaluationResult.finalScore < 50 }">
                    {{ evaluationResult.verdict }}
                </div>
            </div>

            <div class="report-meta">
                <span>날짜: 2026.02.05</span>
                <span>담당 AI: CODUCK_AI</span>
                <span>미션: 데이터 파이프라인 복구</span>
            </div>

            <!-- Score Circle -->
            <div class="score-section">
                <div class="score-circle">
                    <svg viewBox="0 0 36 36" class="circular-chart">
                        <path class="circle-bg"
                            d="M18 2.0845
                            a 15.9155 15.9155 0 0 1 0 31.831
                            a 15.9155 15.9155 0 0 1 0 -31.831"
                        />
                        <path class="circle"
                            :stroke-dasharray="evaluationResult.finalScore + ', 100'"
                            d="M18 2.0845
                            a 15.9155 15.9155 0 0 1 0 31.831
                            a 15.9155 15.9155 0 0 1 0 -31.831"
                        />
                        <text x="18" y="20.35" class="percentage">{{ evaluationResult.finalScore }}</text>
                    </svg>
                </div>
                <div class="score-label">아키텍트 등급: {{ evaluationResult.scoreTier }}</div>
            </div>

            <!-- Evaluation Areas (Accordion) -->
            <div class="evaluation-areas">
                <div class="area-header">평가 영역 (클릭하여 상세 보기)</div>
                <div class="area-list">
                    <div 
                        v-for="(detail, idx) in evaluationResult.details" 
                        :key="idx" 
                        class="area-item"
                        :class="{ 'area-expanded': activeDetail === idx }"
                        @click="toggleDetail(idx)"
                    >
                        <div class="area-summary">
                            <span class="area-name">{{ detail.category }}</span>
                            <span class="area-score">{{ detail.score }} / 100</span>
                            <span class="area-arrow">▼</span>
                        </div>
                        <div class="area-detail-content" v-if="activeDetail === idx">
                             <div class="detail-row">
                                 <span class="detail-label">분석 결과</span>
                                 <p class="detail-text">"{{ detail.comment }}"</p>
                             </div>
                             <div class="detail-row">
                                 <span class="detail-label">개선 제안</span>
                                 <ul class="detail-list">
                                     <li v-for="(imp, i) in detail.improvements" :key="i">- {{ imp }}</li>
                                 </ul>
                             </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Analysis Box (Bottom) -->
            <div class="analysis-box">
                <div class="coduck-avatar-small">
                    <img src="/assets/characters/coduck_sad.png" />
                </div>
                <div class="analysis-text-wrapper">
                    <p class="ai-comment" v-if="!isEvaluating">"{{ evaluationResult.aiAnalysis }}"</p>
                    <p class="ai-comment" v-else>장치 정밀 분석 중...</p>
                    <p class="senior-tip" v-if="!isEvaluating">조언: {{ evaluationResult.seniorAdvice }}</p>
                </div>
            </div>

            <!-- New: LLM Supplementary Topics -->
            <div v-if="evaluationResult.supplementary && evaluationResult.supplementary.length > 0" class="supplement-section">
                <div class="s-header">
                    <span class="s-icon">📘</span>
                    <span class="s-title">LLM 추천 보충 학습 리스트</span>
                </div>
                <div class="s-grid">
                    <div v-for="(item, i) in evaluationResult.supplementary" :key="i" class="s-card">
                        <div class="s-card-title">{{ item.title }}</div>
                        <div class="s-card-desc">{{ item.desc }}</div>
                    </div>
                </div>
            </div>

            <button class="btn-next-report" @click="exitToHub" :disabled="isEvaluating">징검다리로 돌아가기</button>
         </div>
      </section>

      <!-- PHASE: DEFEAT -->
      <section v-if="gameState.phase === 'DEFEAT'" class="panel defeat-view">
            <h1 class="glitch-text">시스템 실패</h1>
            <p>치명적인 무결성 손실</p>
            <button class="btn-retry" @click="restartMission">시스템 재부팅</button>
      </section>

       <!-- PHASE: CAMPAIGN END -->
      <section v-if="gameState.phase === 'CAMPAIGN_END'" class="panel victory-view">
            <h1 class="gold-text">모든 섹터 확보됨</h1>
            <p>최종 점수: {{ gameState.score }}</p>
      </section>

    </main>
    
    <!-- FEEDBACK TOAST -->
    <div v-if="gameState.feedbackMessage && gameState.phase !== 'PYTHON_FILL' && gameState.phase !== 'EVALUATION' && gameState.phase !== 'DEFEAT' && gameState.phase !== 'CAMPAIGN_END'" class="feedback-toast">
      <span class="toast-icon">!</span> {{ gameState.feedbackMessage }}
    </div>

  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useGameStore } from '@/stores/game';
import { useCoduckWars } from './composables/useCoduckWars.js'; // [수정일: 2026-02-06] 폴더 계층화(composables) 반영 및 로직 통합

const router = useRouter();
const gameStore = useGameStore();

const { 
    gameState, 
    diagnosticQuestion1, 
    diagnosticQuestion2, 
    deepQuizQuestion,
    pythonSnippets,
    evaluationResult,
    isEvaluating,
    logicBlocks, // Add this
    submitDiagnostic1,
    submitDiagnostic2,
    submitPseudo,
    submitPythonFill,
    submitDeepQuiz,
    insertSnippet,
    handleSlotDrop,
    nextMission,
    restartMission,
    initPhase4Scaffolding,
    handlePseudoInput,
    addLogicBlock // Add this
} = useCoduckWars();

// Helper to switch questions based on diagnostic phase
const currentDiagnosticQuestion = computed(() => {
    if (gameState.phase === 'DIAGNOSTIC_1') return diagnosticQuestion1.value;
    if (gameState.phase === 'DIAGNOSTIC_2') return diagnosticQuestion2.value;
    return { question: "", options: [] };
});

const handleDiagnosticSubmit = (idx) => {
    if (gameState.phase === 'DIAGNOSTIC_1') submitDiagnostic1(idx);
    else submitDiagnostic2(idx);
};

// --- NEW HELPER FOR PHASE 4 ---
const commentedLogicLines = computed(() => {
    if (!gameState.phase3Reasoning) return ["# No logic trace found."];
    // Split by newlines and add Python comment hash
    return gameState.phase3Reasoning.split('\n').map(line => `# ${line}`);
});

const handleDragStart = (evt, code) => {
    if (evt.dataTransfer) {
        evt.dataTransfer.setData('text/plain', code);
        evt.dataTransfer.effectAllowed = 'copy';
    }
};

const exitToHub = () => {
    // Unlock next stage (Current Stage ID is 1-based, convert to 0-based index)
    const currentIdx = gameState.currentStageId - 1;
    gameStore.unlockNextStage('Pseudo Practice', currentIdx);
    
    // Return to hub
    router.push('/');
    // emit('close'); // emit is not defined here script setup logic might need defineEmits if used
};

// Drag and Drop Logic
const onDrop = (slotKey, evt) => {
    const code = evt.dataTransfer.getData('text/plain');
    if (code) {
        // Direct update since we might not have exported a helper yet, 
        // or just use the helper if we export it.
        // Let's assume we need to update state directly if helper is missing, 
        // but `handleSlotDrop` is better. 
        // I will check if `handleSlotDrop` is available in `useCoduckWars` return.
        // For now, let's update directly to be safe as `gameState` is reactive.
        if (gameState.codeSlots[slotKey]) {
            gameState.codeSlots[slotKey].content = code;
        }
    }
};

// Evaluation Detail Toggle
const activeDetail = ref(null);
const toggleDetail = (idx) => {
    activeDetail.value = activeDetail.value === idx ? null : idx;
};

// --- LOGGING HELPERS ---
const getLogTypeClass = (type) => {
    switch (type) {
        case 'WARN': return 't-warn';
        case 'ERROR': return 't-error';
        case 'SUCCESS': return 't-success';
        case 'READY': return 't-ready';
        default: return 't-info';
    }
};

const getLogLabel = (type) => {
    switch (type) {
        case 'WARN': return '경고';
        case 'ERROR': return '오류';
        case 'SUCCESS': return '성공';
        case 'READY': return '준비';
        default: return '정보';
    }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=JetBrains+Mono:wght@400;700&display=swap');

/* GLOBAL CONTAINER */
.coduck-wars-container {
  width: 100vw;
  height: 100vh;
  background-color: #050505; /* Pitch Black */
  color: #E5E7EB;
  font-family: 'Inter', sans-serif;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* BACKGROUND WATERMARK */
.bg-watermark {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-15deg);
    font-size: 15rem; /* Huge */
    font-weight: 900;
    color: rgba(255, 255, 255, 0.03); /* Subtle */
    white-space: nowrap;
    z-index: 0;
    pointer-events: none;
    user-select: none;
}
.scan-line {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 5px;
  background: rgba(74, 222, 128, 0.05);
  animation: scan 4s linear infinite;
  z-index: 10;
  pointer-events: none;
}
@keyframes scan {
  0% { top: -10%; }
  100% { top: 110%; }
}

/* HEADER - TERMINAL STYLE */
.war-room-header {
  height: 80px; /* Slightly taller */
  background: transparent;
  display: flex;
  justify-content: space-between;
  align-items: center; /* Center vertically */
  padding: 0 40px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  z-index: 100;
  position: relative;
}
.chapter-info { display: flex; flex-direction: column; }
.chapter-title {
    color: #4ade80; /* Neon Green */
    font-weight: 900;
    font-size: 1.4rem;
    font-style: italic;
    letter-spacing: 1px;
}
.sub-info {
    color: #6b7280;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    margin-top: 5px;
}
.integrity-monitor {
    display: flex;
    align-items: center;
    gap: 20px; /* Wider gap */
    font-family: 'JetBrains Mono', monospace;
}
.integrity-label { color: #4ade80; font-size: 0.9rem; font-weight: bold; }
.hp-bar-bg {
    width: 250px; /* Wider bar */
    height: 10px;
    background: #1f2937;
    border-radius: 4px;
    overflow: hidden;
}
.hp-bar-fill { height: 100%; background: #4ade80; transition: width 0.3s; }
.integrity-val { color: #fff; font-weight: bold; font-size: 1.1rem; }

/* LAYOUT GRID */
.viewport { flex: 1; position: relative; z-index: 50; padding: 0; display: flex; }
.combat-grid {
    display: flex;
    width: 100%;
    height: 100%;
}

/* LEFT PANEL - ENTITY CARD */
.entity-card {
    width: 500px; /* Wider Left Panel */
    background: #0a0a0a;
    border-right: 1px solid #333;
    padding: 50px;
    display: flex;
    flex-direction: column;
}
.entity-header {
    display: flex;
    justify-content: space-between;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    color: #fbbf24; /* Amber Warning */
    margin-bottom: 30px;
    border-bottom: 2px solid #fbbf24;
    padding-bottom: 10px;
}
.visual-frame {
    position: relative;
    border: 2px solid #333;
    flex: 1; /* Fill vertical space */
    max-height: 500px;
    background: #000;
    margin-bottom: 30px;
    overflow: hidden;
}
.coduck-portrait { width: 100%; height: 100%; object-fit: cover; filter: grayscale(100%) sepia(20%) hue-rotate(50deg) saturate(300%) contrast(1.2); opacity: 0.9; }
.scan-overlay {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: repeating-linear-gradient(
        0deg,
        rgba(0, 0, 0, 0.2),
        rgba(0, 0, 0, 0.2) 2px,
        transparent 2px,
        transparent 4px
    );
    pointer-events: none;
}
.disconnect-tag {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    background: #ef4444; /* Red */
    color: #000;
    font-weight: 900;
    padding: 10px;
    text-align: center;
    font-size: 1rem;
    letter-spacing: 2px;
}
.dialogue-box {
    background: #111;
    border: 1px solid #333;
    padding: 25px;
    border-left: 4px solid #3b82f6; /* Blue Accent */
}
.speaker { color: #3b82f6; font-size: 0.9rem; font-weight: bold; display: block; margin-bottom: 10px; text-transform: uppercase; }
.dialogue-text { color: #e5e7eb; font-style: italic; line-height: 1.6; font-size: 1.1rem; }


/* RIGHT PANEL - DECISION ENGINE */
.decision-panel {
    flex: 1;
    padding: 60px 100px; /* Big padding */
    display: flex;
    flex-direction: column;
    justify-content: center; /* Center Vertically */
    background: rgba(10, 10, 10, 0.3); /* Slight tint */
}
.system-status-text {
    color: #6b7280;
    font-family: 'JetBrains Mono', monospace;
    font-size: 1rem;
    margin-bottom: 30px;
    letter-spacing: 1px;
}
.big-question {
    font-size: 3.5rem; /* Massive Font */
    font-weight: 900;
    letter-spacing: -2px;
    line-height: 1.2;
    color: #fff;
    margin-bottom: 60px;
    text-shadow: 0 0 50px rgba(0,0,0,0.8); /* Shadow for readability */
}

/* Stretched Options to Fill Space */
.options-list { 
    display: flex; 
    flex-direction: column; 
    gap: 30px; /* Big Gap */
    width: 100%; 
}

.option-card {
    background: rgba(20, 20, 20, 0.6);
    border: 1px solid rgba(255,255,255,0.1);
    display: flex;
    align-items: stretch;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    height: 140px; /* Taller Cards */
    text-align: left;
    padding: 0;
    position: relative;
    z-index: 60;
    pointer-events: auto;
    overflow: hidden;
}
.option-card:hover {
    background: rgba(74, 222, 128, 0.05);
    border-color: #4ade80;
    transform: translateX(10px); /* Slide effect */
}
.opt-index {
    width: 100px;
    background: #1f2937; /* Default Dark Grey */
    color: #9ca3af;
    font-weight: 900;
    font-size: 2.2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s, color 0.2s;
}
.option-card:hover .opt-index {
    background: #4ade80; /* Neon Green on Hover */
    color: #000;
}
.opt-content {
    flex: 1;
    padding: 0 40px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.opt-main { font-size: 1.6rem; font-weight: 800; color: #fff; margin-bottom: 10px; letter-spacing: -0.5px; }
.opt-desc { color: #9ca3af; font-size: 1rem; font-family: 'JetBrains Mono', monospace; }
.opt-arrow {
    width: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    color: #4ade80;
    opacity: 0;
    transition: opacity 0.2s, transform 0.2s;
    transform: translateX(-20px);
}
.option-card:hover .opt-arrow { opacity: 1; transform: translateX(0); }

.terminal-footer { margin-top: auto; font-family: 'JetBrains Mono', monospace; color: #4b5563; font-size: 0.9rem; padding-top: 40px; }

/* SYSTEM LOG STYLES */
.tactical-console {
    margin-top: auto;
    background: rgba(0,0,0,0.4);
    border-top: 1px solid rgba(255,255,255,0.1);
    padding: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    height: 150px; /* Fixed height for scrolling */
    display: flex;
    flex-direction: column;
}
.console-header { color: #4b5563; font-size: 0.8rem; margin-bottom: 10px; font-weight: bold; }
.console-body { 
    flex: 1; 
    overflow-y: auto; 
    display: flex; 
    flex-direction: column; 
    justify-content: flex-end; /* Keep bottom */
}
.log-line { margin-bottom: 5px; color: #aaa; }
.active-line { color: #fff; text-shadow: 0 0 5px rgba(255,255,255,0.5); }
.t-time { color: #555; margin-right: 10px; }
.t-info { color: #3b82f6; font-weight: bold; }
.t-warn { color: #fbbf24; font-weight: bold; }
.t-error { color: #ef4444; font-weight: bold; }
.t-success { color: #4ade80; font-weight: bold; }
.t-ready { color: #4ade80; font-weight: bold; animation: pulse 2s infinite; }
.cursor-blink { animation: blink 1s step-end infinite; color: #4ade80; margin-left: 5px; }

@keyframes blink { 50% { opacity: 0; } }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

/* FADE TRANSITION FOR LOGS */
.log-fade-enter-active,
.log-fade-leave-active {
  transition: all 0.3s ease;
}
.log-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.log-fade-leave-to {
  opacity: 0;
}


/* PHASE 3 REVISED CSS */
.mission-problem-box {
    margin-top: 20px;
    background: #111;
    border: 1px solid #333;
    border-left: 4px solid #4ade80;
    padding: 20px;
}
.mp-title { color: #6b7280; font-size: 0.8rem; font-weight: bold; margin-bottom: 15px; letter-spacing: 1px; }
.selected-strat-tag { 
    color: #4ade80; 
    font-weight: 900; 
    font-size: 1.4rem; /* Larger font for visibility */
    margin-bottom: 15px; 
    line-height: 1.3;
    border-bottom: 1px solid #333;
    padding-bottom: 15px;
}
.mp-desc { color: #d1d5db; font-size: 1rem; line-height: 1.6; }

/* HINT BUBBLE */
.coduck-speech-bubble {
    margin-top: 15px;
    background: #050505; /* Dark background */
    border: 2px solid #4ade80; /* Neon Green Border */
    color: #fff; /* High contrast text */
    padding: 20px;
    border-radius: 8px;
    position: relative;
    font-weight: bold;
    animation: fadeIn 0.5s;
    box-shadow: 0 0 15px rgba(74, 222, 128, 0.15); /* Green Glow */
}
.coduck-speech-bubble::before {
    content: '';
    position: absolute;
    top: -12px;
    left: 40px;
    border-left: 10px solid transparent;
    border-right: 10px solid transparent;
    border-bottom: 10px solid #4ade80;
}
.coduck-speech-bubble::after {
    content: '';
    position: absolute;
    top: -9px;
    left: 40px;
    border-left: 10px solid transparent;
    border-right: 10px solid transparent;
    border-bottom: 10px solid #050505;
}
.hint-content { display: flex; align-items: flex-start; gap: 10px; }
.h-icon { font-size: 1.5rem; }
.h-text { font-size: 1rem; line-height: 1.4; }
.h-highlight { color: #4ade80; font-weight: 900; } /* Text Highlight instead of background */

/* MONACO STYLE EDITOR WRAPPER */
.monaco-wrapper {
    flex: 1;
    background: #1e1e1e; /* VS Code Logic Background */
    border: 1px solid #333;
    display: flex;
    position: relative;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    overflow: hidden;
    margin-bottom: 20px;
}
.line-numbers {
    width: 50px; /* Slightly wider */
    background: #1e1e1e;
    border-right: 1px solid #333;
    color: #858585;
    text-align: right;
    padding: 20px 10px;
    font-size: 14px;
    line-height: 1.5;
    user-select: none;
    display: flex; /* Flex column for vertical numbers */
    flex-direction: column;
}
.monaco-textarea {
    flex: 1;
    background: transparent;
    border: none;
    color: #d4d4d4;
    padding: 20px;
    font-family: inherit;
    font-size: 14px;
    line-height: 1.5;
    resize: none;
    outline: none;
    white-space: pre;
}

.editor-action-bar {
    display: flex;
    justify-content: flex-end;
}


/* PHASE 4, 5, etc preserved */
/* PHASE 4, 5, etc preserved */
.code-panel { flex:2; background:#000; display:flex; flex-direction:column; padding:30px; border-right:1px solid #333; }
.code-editor-monaco-style { 
    flex:1; 
    background:#1E1E1E; /* Distinct VS Code Dark */
    color:#d4d4d4; 
    border:none; 
    border-top: 2px solid #3776AB; /* Python Blue Accent */
    padding:20px; 
    font-family:'JetBrains Mono'; 
    font-size:14px; 
    resize:none; 
    outline:none; 
    z-index:60; 
    position:relative; 
    box-shadow: inset 0 0 20px rgba(0,0,0,0.5); /* Inner Depth */
}
.error-console { background:#300; color:#f88; padding:10px; font-family:'JetBrains Mono'; margin-top:10px; }
.snippet-panel { width:350px; background:#111; padding:30px; display:flex; flex-direction:column; }
.snippet-list { flex:1; display:flex; flex-direction:column; gap:10px; overflow-y:auto; margin-bottom:20px; }
.snippet-btn { background:#222; border:1px solid #333; color:#eee; padding:15px; text-align:left; cursor:pointer; display:flex; align-items:center; gap:10px; z-index:60; position:relative; }
.snippet-btn:hover { border-color:#4ade80; color:#4ade80; }
.command-box { display:flex; flex-direction:column; gap:10px; }
.btn-reset { background:transparent; border:1px solid #666; color:#666; padding:10px; cursor:pointer; z-index:60; position:relative; }

/* PHASE 5 & RESULT */
.centered-layout { justify-content:center; align-items:center; height:100vh; }
.center-panel { width:100%; max-width:1000px; text-align:center; } /* Wider */
.big-question-center { font-size:3rem; font-weight:900; margin-bottom:60px; color:#fff; }
.gold-hover:hover { background:rgba(251, 191, 36, 0.1); border-color:#fbbf24; }
.gold-idx { background:#fbbf24; color: black; }
.phase-header-gold { color:#fbbf24; font-weight:900; font-size:1.4rem; margin-bottom:40px; text-align:center; display:block;}
.options-wide { gap: 20px; display:flex; flex-direction:column; } /* Ensure gap */


.evaluation-view { 
    display: flex; 
    justify-content: center; 
    align-items: center; 
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    background: rgba(0,0,0,0.85); 
    z-index: 80; 
    backdrop-filter: blur(10px);
    overflow-y: auto; /* Enable vertical scrolling */
}
.report-card { 
    width: 650px; 
    background: #080808; 
    border: 1px solid #333; 
    border-radius: 12px;
    padding: 40px; 
    text-align: center; 
    box-shadow: 0 0 50px rgba(0,0,0,0.8);
    position: relative;
    overflow: hidden;
}
/* Report Header */
.report-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;
    position: relative;
}
.report-title {
    font-family: 'Inter', sans-serif;
    font-weight: 900;
    font-size: 2rem;
    letter-spacing: 2px;
    color: #fff;
    text-transform: uppercase;
    background: linear-gradient(90deg, #4ade80, #22c55e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stamp-box {
    border: 3px solid;
    padding: 5px 15px;
    font-weight: 900;
    font-size: 1rem;
    text-transform: uppercase;
    transform: rotate(-10deg);
    opacity: 0.8;
}
.stamp-success { color: #4ade80; border-color: #4ade80; box-shadow: 0 0 10px #4ade80; }
.stamp-fail { color: #ef4444; border-color: #ef4444; box-shadow: 0 0 10px #ef4444; }

.report-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #666;
    display: flex;
    flex-direction: column;
    gap: 5px;
    margin-bottom: 30px;
    border-bottom: 1px solid #222;
    padding-bottom: 20px;
}

/* Score Circle */
.score-section { margin-bottom: 40px; }
.score-circle {
    width: 120px;
    height: 120px;
    margin: 0 auto 15px;
    position: relative;
}
.circular-chart { display: block; margin: 0 auto; max-width: 100%; max-height: 100%; }
.circle-bg { fill: none; stroke: #222; stroke-width: 2.5; }
.circle { fill: none; stroke-width: 2.5; stroke-linecap: round; animation: progress 1s ease-out forwards; stroke: #4ade80; }
.percentage { fill: #fff; font-family: 'Inter', sans-serif; font-weight: 900; font-size: 0.8em; text-anchor: middle; dominant-baseline: middle; }
.score-label { font-weight: bold; color: #4ade80; font-size: 1.1rem; }

@keyframes progress { 0% { stroke-dasharray: 0 100; } }

/* Accordion */
.evaluation-areas { text-align: left; margin-bottom: 30px; }
.area-header { color: #888; font-size: 0.85rem; letter-spacing: 2px; margin-bottom: 10px; font-weight: bold; text-align: center; }
.area-list { display: flex; flex-direction: column; gap: 10px; }
.area-item {
    background: #111;
    border: 1px solid #333;
    border-radius: 6px;
    overflow: hidden;
    transition: all 0.3s;
    cursor: pointer;
}
.area-item:hover { border-color: #4ade80; }
.area-expanded { border-color: #4ade80; background: #1a1a1a; }

.area-summary {
    padding: 15px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.area-name { font-weight: bold; font-size: 1rem; color: #ddd; }
.area-score { font-family: 'JetBrains Mono'; color: #4ade80; font-weight: bold; }
.area-arrow { font-size: 0.8rem; color: #555; transition: transform 0.3s; }
.area-expanded .area-arrow { transform: rotate(180deg); }

.area-detail-content {
    background: #0f1510; /* Very dark green hint */
    border-top: 1px solid #333;
    padding: 20px;
    font-size: 0.9rem;
    animation: slideDown 0.3s ease-out;
}
@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

.detail-row { margin-bottom: 15px; }
.detail-row:last-child { margin-bottom: 0; }
.detail-label { display: block; font-size: 0.75rem; color: #4ade80; margin-bottom: 5px; font-weight: bold; letter-spacing: 1px; }
.detail-text { color: #ccc; line-height: 1.5; }
.detail-list { list-style: none; padding: 0; margin: 0; color: #aaa; }

/* Analysis Box */
.analysis-box {
    background: rgba(74, 222, 128, 0.05);
    border: 1px solid rgba(74, 222, 128, 0.2);
    border-radius: 8px;
    padding: 20px;
    display: flex;
    align-items: flex-start;
    gap: 15px;
    text-align: left;
    margin-bottom: 25px;
}
.coduck-avatar-small img { width: 50px; height: 50px; border-radius: 50%; border: 2px solid #4ade80; object-fit: cover; }
.analysis-text-wrapper { flex: 1; }
.ai-comment { font-style: italic; color: #fff; margin-bottom: 8px; font-size: 0.95rem; }
.senior-tip { font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #4ade80; }

.btn-next-report {
    width: 100%;
    padding: 18px;
    font-weight: 900;
    background: #4ade80;
    color: #000;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: transform 0.2s, box-shadow 0.2s;
}
.btn-next-report:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 20px rgba(74, 222, 128, 0.4);
}

/* FEEDBACK */
.feedback-toast {
    position: fixed;
    bottom: 40px;
    left: 50%;
    transform: translateX(-50%);
    background: #000;
    color: #4ade80;
    border: 2px solid #4ade80;
    padding: 15px 40px;
    font-weight: 900;
    z-index: 200;
    box-shadow: 0 0 20px rgba(74, 222, 128, 0.2);
}

/* --- PYTHON FILL REVISED STYLES --- */
.implementation-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: rgba(10, 10, 10, 0.5);
    padding: 30px;
    overflow: hidden;
}
.split-view {
    flex: 1;
    display: flex;
    gap: 15px;
    overflow: hidden;
    margin-bottom: 20px;
    margin-top: 10px;
}

/* Logic Viewer (Left Col) */
/* Logic Viewer (Left Col - 40%) */
.logic-viewer {
    flex: 4;
    width: auto; /* Remove fixed width */
    background: #0d0d0d;
    border: 1px solid #333;
    display: flex;
    flex-direction: column;
}
.viewer-header {
    background: #222;
    color: #999;
    font-size: 0.75rem;
    font-weight: bold;
    padding: 8px 12px;
    letter-spacing: 1px;
}
.commented-content {
    flex: 1;
    padding: 15px;
    overflow-y: auto;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.85rem;
    line-height: 1.5;
    color: #6a9955; /* Comment Green */
    white-space: pre-wrap;
}

/* Code Editor (Middle Col - 60%) */
.code-editor-area {
    flex: 6;
    background: #1e1e1e;
    border: 1px solid #444;
    display: flex;
    flex-direction: column;
    position: relative;
}

/* Modules Sidebar (Right Col) */
.modules-sidebar {
    width: 220px;
    background: #0a0a0a;
    border: 1px solid #333;
    display: flex;
    flex-direction: column;
    padding: 10px;
}
.phase-header-green-small {
    color: #4ade80;
    font-weight: 900;
    font-size: 1rem;
    margin-bottom: 10px;
    padding-bottom: 5px;
    border-bottom: 1px solid #333;
}
.snippet-list-scroll {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.snippet-block {
    background: #1f1f1f;
    color: #cecece;
    padding: 12px;
    border-radius: 4px;
    cursor: grab;
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    border: 1px solid #333;
    transition: all 0.2s;
}
.snippet-block:hover {
    border-color: #4ade80;
    background: #2a2a2a;
    transform: translateX(-2px);
}
.snippet-block:active {
    cursor: grabbing;
}
.s-icon { color: #555; font-weight: bold; }

/* Bottom Action Bar */
.action-bar-bottom {
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.btn-group { display: flex; gap: 10px; }

/* DEFEAT & VICTORY SCREENS */
.defeat-view, .victory-view {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0, 0, 0, 0.95);
    z-index: 200;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    backdrop-filter: blur(5px);
}

.glitch-text {
    font-size: 5rem;
    font-weight: 900;
    color: #ef4444;
    text-transform: uppercase;
    letter-spacing: 8px;
    margin-bottom: 20px;
    text-shadow: 2px 2px 0px #000;
    animation: glitch-anim 0.3s infinite;
}

.btn-retry {
    margin-top: 40px;
    background: transparent;
    border: 2px solid #ef4444;
    color: #ef4444;
    padding: 15px 50px;
    font-size: 1.2rem;
    font-weight: 900;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 2px;
    transition: all 0.2s;
}
.btn-retry:hover {
    background: #ef4444;
    color: #000;
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.5);
}

.gold-text {
    font-size: 4rem;
    font-weight: 900;
    color: #fbbf24;
    text-shadow: 0 0 20px rgba(251, 191, 36, 0.5);
    margin-bottom: 20px;
}

@keyframes glitch-anim {
    0% { transform: translate(0); text-shadow: 2px 2px 0px #000; }
    25% { transform: translate(-2px, 2px); text-shadow: -2px -2px 0px #000; }
    50% { transform: translate(2px, -2px); text-shadow: 2px -2px 0px #000; }
    75% { transform: translate(-2px, -2px); text-shadow: -2px 2px 0px #000; }
    100% { transform: translate(0); text-shadow: 2px 2px 0px #000; }
}

/* NEW DROP ZONE STYLES */
.code-editor-area {
    padding: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    overflow-y: auto;
    gap: 15px; /* Spacing between blocks */
}
.code-header, .code-footer {
    color: #569cd6; /* Python Blue Keyword */
    font-weight: bold;
}
.code-block {
    display: flex;
    flex-direction: column;
    gap: 5px;
}
.comment-line {
    color: #6a9955;
    font-size: 0.9rem;
    margin-bottom: 2px;
}
.drop-zone {
    background: #252526;
    border: 1px dashed #555;
    padding: 12px;
    color: #888;
    cursor: default;
    transition: all 0.2s;
    border-radius: 4px;
    text-align: center;
    min-height: 45px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.drop-zone:hover {
    border-color: #4ade80;
    background: rgba(74, 222, 128, 0.05);
    color: #4ade80;
}
.drop-zone.filled {
    border: 1px solid #3776AB; /* Python Blue */
    background: #0d1117;
    color: #fff;
    font-weight: bold;
    justify-content: flex-start; /* Align text left */
    padding-left: 15px;
}


/* LLM SUPPLEMENT SECTION */
.supplement-section {
    margin-top: 24px;
    padding: 16px;
    background: rgba(59, 130, 246, 0.05);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 12px;
}
.s-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
}
.s-title {
    font-weight: bold;
    color: #60a5fa;
    font-size: 0.9rem;
    text-transform: uppercase;
}
.s-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}
.s-card {
    background: rgba(0, 0, 0, 0.3);
    padding: 12px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}
.s-card-title {
    font-weight: bold;
    font-size: 0.85rem;
    color: #fbbf24;
    margin-bottom: 4px;
}
.s-card-desc {
    font-size: 0.75rem;
    color: #9ca3af;
    line-height: 1.4;
}

/* MISSION BRIEFING BOX STYLES */
.full-width-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.top-briefing-zone {
    background: rgba(15, 23, 42, 0.6);
    border-bottom: 1px solid rgba(59, 130, 246, 0.2);
    padding: 15px 20px;
}

.briefing-divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.05);
    margin: 12px 0;
}

.incident-text {
    font-size: 1.15rem; /* Slightly larger */
    color: #cbd5e1; /* Changed from reddish to soft light grey/blue */
    font-weight: 500;
    line-height: 1.6;
}

.briefing-sub {
    font-size: 0.95rem; /* Scaled up */
    color: #94a3b8;
    margin-bottom: 12px;
}

.briefing-section {
    margin-bottom: 0;
}

.briefing-label {
    font-size: 0.95rem; /* Scaled up */
    font-weight: bold;
    color: #4ade80; /* Text Emerald */
    margin-bottom: 10px;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.b-icon {
    font-size: 1.25rem;
}

.briefing-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.briefing-list li {
    font-size: 1.1rem; /* Scaled up */
    color: #cbd5e1;
    margin-bottom: 8px;
    padding-left: 22px;
    position: relative;
    line-height: 1.6;
}

.briefing-list li::before {
    content: '▪';
    position: absolute;
    left: 0;
    color: #3b82f6;
}

.badge-natural {
    background: #ef4444;
    color: white;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: bold;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.7; }
    100% { opacity: 1; }
}

.writing-notice {
    font-size: 0.75rem;
    color: #94a3b8;
    margin-right: auto;
}

</style>
