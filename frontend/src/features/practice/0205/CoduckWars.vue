
<template>
  <div class="coduck-wars-container">
    <!-- Header -->
    <header class="header">
      <div class="brand">
        <span class="chapter-text">CHAPTER 1: 튜토리얼 존</span>
        <h1 class="logo-text">CODUCK WARS</h1>
      </div>
      <div class="stats-bar">
        <div class="stat-item">
          <span class="label">프로토콜: AI 사고법 입문</span>
          <span class="value">{{ gameState.score }} PTS</span>
        </div>
        <div class="stat-item health-bar">
          <span class="label">정화 무결성</span>
          <div class="hp-track">
            <div class="hp-fill" :style="{ width: gameState.playerHP + '%' }"></div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="battle-ground">
      
      <!-- Center: Evaluation Report (Phase: EVALUATION) -->
      <transition name="fade-slide">
        <div v-if="gameState.phase === 'EVALUATION'" class="evaluation-view">
          <!-- Background Watermark -->
          <div class="watermark-bg">
            <span v-if="evaluationResult.finalScore >= 80" class="success-mark">SYSTEM RESTORED</span>
            <span v-else class="fail-mark">시스템 오류</span>
          </div>

          <!-- Report Card -->
          <div class="report-card">
            <div class="report-header">
              <h2>MISSION EVALUATION REPORT</h2>
              <div class="date-stamp">{{ new Date().toLocaleString() }}</div>
            </div>

            <!-- Top Section: Score & Tier -->
            <div class="score-section">
              <div class="score-circle-container">
                <svg viewBox="0 0 36 36" class="circular-chart">
                  <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                  <path class="circle" :stroke-dasharray="evaluationResult.finalScore + ', 100'" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                  <text x="18" y="20.35" class="percentage">{{ evaluationResult.finalScore }}</text>
                </svg>
                <div class="score-label">SYNC RATE</div>
              </div>
              
              <div class="tier-badge">
                <div class="tier-label">ENGINEER CLASS</div>
                <div class="tier-value" :class="evaluationResult.scoreTier.toLowerCase().replace(' ', '-')">
                  {{ evaluationResult.scoreTier }}
                </div>
              </div>
            </div>

            <!-- Analysis Box -->
            <div class="analysis-box">
              <div class="box-icon">
                <div class="coduck-avatar-small"></div>
              </div>
              <div class="box-content">
                <h3>CODUCK'S ANALYSIS</h3>
                <p>{{ evaluationResult.aiAnalysis }}</p>
              </div>
            </div>

            <!-- Detailed Breakdown Accordion -->
            <div class="breakdown-list">
              <div v-for="(detail, index) in evaluationResult.details" :key="index" class="breakdown-item">
                <div class="item-header">
                  <span class="item-title">{{ detail.category }}</span>
                  <div class="item-score-bar">
                    <div class="item-score-fill" :style="{ width: detail.score + '%' }"></div>
                  </div>
                  <span class="item-points">{{ detail.score }}</span>
                </div>
                <div class="item-body">
                  <p class="comment">{{ detail.comment }}</p>
                  <ul class="improvements">
                    <li v-for="(imp, i) in detail.improvements" :key="i">▹ {{ imp }}</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Bottom Actions -->
            <div class="report-actions">
              <button class="btn-retry" @click="restartMission">
                <span class="icon">↺</span> 재시도
              </button>
              <button class="btn-next-report" @click="exitToHub">징검다리로 돌아가기</button>
            </div>
          </div>
        </div>
      </transition>

      <!-- Center: Battle Interface (All other phases) -->
      <transition name="fade">
        <div class="center-stage" v-if="gameState.phase !== 'EVALUATION' && gameState.phase !== 'CAMPAIGN_END'">
          
          <!-- Enemy (Anomaly) Visualization -->
          <div class="enemy-container">
            <div class="hologram-effect">
              <div class="glitch-layer"></div>
              <div class="enemy-avatar">
                <div class="anomaly-scanlines"></div>
                <div class="anomaly-core"></div>
              </div>
            </div>
            <div class="enemy-meta">
              <span class="threat-level">THREAT LEVEL: HIGH</span>
              <h2 class="target-name">{{ enemyThreat.name }}</h2>
              <p class="target-desc">{{ enemyThreat.description }}</p>
            </div>
          </div>

          <!-- Interaction Zone -->
          <div class="interaction-zone">
            <!-- Phase 1 & 2: Diagnostic Choice -->
             <div v-if="['DIAGNOSTIC_1', 'DIAGNOSTIC_2'].includes(gameState.phase)" class="choice-grid">
               <template v-if="gameState.phase === 'DIAGNOSTIC_1'">
                  <div class="question-card">
                    <h3>{{ diagnosticQuestion1.question }}</h3>
                  </div>
                  <button 
                    v-for="(opt, idx) in diagnosticQuestion1.options" 
                    :key="idx" 
                    class="option-card"
                    @click="submitDiagnostic1(idx)"
                  >
                    <span class="opt-text">{{ opt.text }}</span>
                    <ul class="opt-bullets">
                      <li v-for="(b, bIdx) in opt.bullets" :key="bIdx">{{ b }}</li>
                    </ul>
                  </button>
               </template>
               <template v-else>
                  <div class="question-card">
                    <h3>{{ diagnosticQuestion2.question }}</h3>
                  </div>
                  <button 
                    v-for="(opt, idx) in diagnosticQuestion2.options" 
                    :key="idx" 
                    class="option-card"
                    @click="submitDiagnostic2(idx)"
                  >
                    <span class="opt-text">{{ opt.text }}</span>
                    <ul class="opt-bullets">
                      <li v-for="(b, bIdx) in opt.bullets" :key="bIdx">{{ b }}</li>
                    </ul>
                  </button>
               </template>
             </div>

             <!-- Phase 3: Pseudo Write -->
             <div v-if="gameState.phase === 'PSEUDO_WRITE'" class="pseudo-editor">
               <div class="editor-header">
                 <span>STRATEGY LOG (Step-by-Step)</span>
               </div>
               <textarea 
                  class="terminal-input" 
                  placeholder="시스템을 복구할 논리적 단계를 서술하십시오... (예: 1. 데이터 로드 -> 2. 결측치 확인...)"
                  :value="gameState.phase3Reasoning"
                  @input="handlePseudoInput"
               ></textarea>
               <div class="editor-footer">
                  <div class="hint-box" :class="{ visible: gameState.showHint }">
                    <span class="hint-icon">💡</span>
                    <span class="hint-text">힌트: 데이터의 기준(Scale)을 정할 때, 미래의 데이터(Test)를 미리 보면 안 됩니다.</span>
                  </div>
                  <button class="btn-primary" @click="submitPseudo">전송 (TRANSMIT)</button>
               </div>
             </div>

             <!-- Phase 4: Python Fill -->
             <div v-if="gameState.phase === 'PYTHON_FILL'" class="code-implementation">
               <div class="ide-container">
                 <div class="file-tab">restoration_script.py</div>
                 <vue-monaco-editor
                    v-model:value="gameState.userCode"
                    theme="vs-dark"
                    language="python"
                    :options="{ 
                      minimap: { enabled: false }, 
                      fontSize: 14, 
                      lineNumbers: 'on',
                      roundedSelection: false,
                      scrollBeyondLastLine: false,
                      readOnly: false,
                      automaticLayout: true
                    }"
                    class="monaco-editor-instance"
                 />
                 
               </div>
               <div class="snippet-sidebar">
                 <h4>AVAILABLE MODULES</h4>
                 <div class="snippet-list">
                   <button 
                      v-for="(snip, idx) in pythonSnippets" 
                      :key="idx" 
                      class="snippet-btn"
                      @click="insertSnippet(snip.code)"
                   >
                     <span class="code-preview">{{ snip.code }}</span>
                     <span class="code-label">{{ snip.label }}</span>
                   </button>
                 </div>
                 <button class="btn-compile" @click="submitPythonFill">
                   <span>⚡ COMPILE & DEPLOY</span>
                 </button>
               </div>
             </div>

             <!-- Phase 5: Deep Quiz -->
             <div v-if="gameState.phase === 'DEEP_QUIZ'" class="quiz-interface">
               <div class="quiz-question">
                 <h3>{{ deepQuizQuestion.question }}</h3>
               </div>
               <div class="quiz-options">
                 <button 
                    v-for="(opt, idx) in deepQuizQuestion.options" 
                    :key="idx"
                    class="quiz-btn"
                    @click="submitDeepQuiz(idx)"
                 >
                   {{ opt.text }}
                 </button>
               </div>
             </div>

          </div>
        </div>
      </transition>
      
      <!-- Feedback Toast -->
      <transition name="pop">
        <div v-if="gameState.feedbackMessage && gameState.phase !== 'EVALUATION'" class="feedback-toast" :class="{ error: gameState.feedbackMessage.includes('오류') || gameState.feedbackMessage.includes('불일치') }">
          <span class="toast-icon">{{ gameState.feedbackMessage.includes('오류') ? '⚠️' : '✅' }}</span>
          <span class="toast-msg">{{ gameState.feedbackMessage }}</span>
        </div>
      </transition>

    </main>

    <!-- Chat Overlay: Coduck -->
    <div class="coduck-comms">
      <div class="comms-avatar">
        <div class="avatar-img"></div>
        <div class="signal-ring"></div>
      </div>
      <div class="comms-box">
        <div class="comms-header">CODUCK.AI [CONNECTED]</div>
        <div class="comms-text type-writer">{{ gameState.coduckMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useGameStore } from '@/stores/game';
import { useCoduckWars } from './CoduckWarsLogic.js';
// Monaco Editor for Python
import { Editor as VueMonacoEditor } from '@guolao/vue-monaco-editor';

const router = useRouter();
const gameStore = useGameStore();

const { 
    gameState, 
    diagnosticQuestion1, 
    diagnosticQuestion2, 
    deepQuizQuestion, 
    pythonSnippets,
    evaluationResult,
    // Actions
    startGame, 
    submitDiagnostic1, 
    submitDiagnostic2,
    submitPseudo,
    submitPythonFill,
    submitDeepQuiz,
    insertSnippet,
    nextMission,
    restartMission,
    handlePseudoInput,
    enemyThreat
} = useCoduckWars();

// Start game on mount
startGame();

const emit = defineEmits(['close', 'complete']);

const exitToHub = () => {
    // Stage cleared logic
    // Unlock next stage (Current Stage ID is 1-based, convert to 0-based index)
    const currentIdx = gameState.currentStageId - 1;
    gameStore.unlockNextStage('Pseudo Practice', currentIdx);
    
    // Return to hub
    router.push('/');
    emit('close');
};

</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

.coduck-wars-container {
  width: 100%;
  height: 100vh;
  background: #000508;
  color: #e0f2fe;
  font-family: 'Share Tech Mono', monospace;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
}

/* --- Header --- */
.header {
  height: 60px;
  background: rgba(2, 6, 23, 0.95);
  border-bottom: 1px solid #0ea5e9;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  z-index: 50;
  box-shadow: 0 4px 20px rgba(14, 165, 233, 0.2);
}

.brand {
  display: flex;
  flex-direction: column;
}

.chapter-text {
  font-size: 0.7rem;
  color: #0ea5e9;
  letter-spacing: 0.2em;
}

.logo-text {
  font-family: 'Orbitron', sans-serif;
  font-weight: 900;
  font-size: 1.5rem;
  background: linear-gradient(90deg, #fff, #38bdf8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
  letter-spacing: 0.1em;
}

.stats-bar {
  display: flex;
  gap: 2rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.stat-item.health-bar {
    width: 200px;
}

.hp-track {
    width: 100%;
    height: 8px;
    background: #1e293b;
    border: 1px solid #334155;
    margin-top: 4px;
}

.hp-fill {
    height: 100%;
    background: #0ea5e9;
    box-shadow: 0 0 10px #0ea5e9;
    transition: width 0.3s ease;
}

.label {
    font-size: 0.7rem;
    color: #64748b;
}

.value {
    font-size: 1.2rem;
    color: #38bdf8;
    font-weight: bold;
}

/* --- Main Battle Ground --- */
.battle-ground {
    flex: 1;
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    background: radial-gradient(circle at center, #0c4a6e22 0%, #000000 70%);
}

/* --- Enemy Hologram --- */
.enemy-container {
    position: absolute;
    top: 5%;
    display: flex;
    flex-direction: column;
    align-items: center;
    z-index: 10;
}

.hologram-effect {
    width: 200px;
    height: 200px;
    position: relative;
    margin-bottom: 1rem;
}

.enemy-avatar {
    width: 100%;
    height: 100%;
    background: rgba(220, 38, 38, 0.1);
    border: 1px solid #ef4444;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    box-shadow: 0 0 30px rgba(220, 38, 38, 0.2);
    animation: pulse 4s infinite;
}

.anomaly-core {
    width: 60%;
    height: 60%;
    background: #ef4444;
    border-radius: 50%;
    filter: blur(20px);
    opacity: 0.6;
}

.enemy-meta {
    text-align: center;
    background: rgba(0,0,0,0.7);
    padding: 1rem;
    border: 1px solid #7f1d1d;
    border-radius: 8px;
}

.threat-level {
    color: #ef4444;
    font-size: 0.8rem;
    font-weight: bold;
    animation: blink 2s infinite;
}

.target-name {
    margin: 5px 0;
    font-family: 'Orbitron';
    color: #fff;
    font-size: 1.5rem;
}

.target-desc {
    color: #9ca3af;
    font-size: 0.9rem;
    max-width: 300px;
}

/* --- Interaction Zone --- */
.interaction-zone {
    width: 80%;
    max-width: 1000px;
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 2rem;
    z-index: 20;
    margin-top: 250px; /* Space for hologram */
    box-shadow: 0 10px 50px rgba(0,0,0,0.8);
    backdrop-filter: blur(10px);
}

/* Choice Grid (Diagnostics) */
.choice-grid {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.question-card h3 {
    text-align: center;
    color: #e2e8f0;
    font-size: 1.5rem;
    margin-bottom: 2rem;
}

.option-card {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid #334155;
    padding: 1.5rem;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
}

.option-card:hover {
    background: rgba(56, 189, 248, 0.1);
    border-color: #38bdf8;
    transform: translateX(10px);
}

.opt-text {
    display: block;
    font-size: 1.2rem;
    color: #38bdf8;
    margin-bottom: 0.5rem;
    font-weight: bold;
}

.opt-bullets {
    margin: 0;
    padding-left: 1.2rem;
    color: #94a3b8;
    font-size: 0.9rem;
}

/* Pseudo Editor */
.editor-header {
    background: #0f172a;
    padding: 0.5rem 1rem;
    border-bottom: 1px solid #333;
    color: #64748b;
    font-size: 0.8rem;
}

.terminal-input {
    width: 100%;
    height: 150px;
    background: #020617;
    border: none;
    color: #22d3ee;
    padding: 1rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.1rem;
    resize: none;
    outline: none;
}

.editor-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 1rem;
}

.hint-box {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #451a03;
    color: #fbbf24;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    opacity: 0;
    transition: opacity 0.5s;
}

.hint-box.visible {
    opacity: 1;
}

/* Python Fill */
.code-implementation {
    display: flex;
    height: 400px;
    border: 1px solid #334155;
}

.ide-container {
    flex: 2;
    display: flex;
    flex-direction: column;
}

.file-tab {
    background: #1e293b;
    padding: 0.5rem 1rem;
    color: #94a3b8;
    font-size: 0.8rem;
}

.monaco-editor-instance {
    flex: 1;
}

.snippet-sidebar {
    flex: 1;
    background: #0f172a;
    border-left: 1px solid #334155;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.snippet-sidebar h4 {
    margin: 0 0 1rem 0;
    color: #64748b;
    font-size: 0.9rem;
}

.snippet-btn {
    background: #1e293b;
    border: 1px solid #334155;
    padding: 0.8rem;
    text-align: left;
    cursor: pointer;
    display: flex;
    flex-direction: column;
}

.snippet-btn:hover {
    border-color: #38bdf8;
    background: rgba(56, 189, 248, 0.1);
}

.code-preview {
    font-family: 'Consolas', monospace;
    color: #a5f3fc;
    font-size: 0.9rem;
    margin-bottom: 4px;
}

.code-label {
    font-size: 0.8rem;
    color: #64748b;
}

.btn-compile {
    margin-top: auto;
    padding: 1rem;
    background: #16a34a;
    color: white;
    border: none;
    font-weight: bold;
    cursor: pointer;
    font-family: 'Orbitron';
}

.btn-compile:hover {
    background: #15803d;
}

/* Quiz */
.quiz-options {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-top: 2rem;
}

.quiz-btn {
    padding: 2rem;
    background: #1e293b;
    border: 1px solid #475569;
    color: #e2e8f0;
    font-size: 1.1rem;
    cursor: pointer;
}

.quiz-btn:hover {
    background: #334155;
    border-color: #94a3b8;
}


/* --- Feedback & Comms --- */
.feedback-toast {
  position: absolute;
  top: 100px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(22, 163, 74, 0.9);
  padding: 1rem 2rem;
  border-radius: 50px;
  display: flex;
  align-items: center;
  gap: 1rem;
  z-index: 100;
  box-shadow: 0 4px 20px rgba(0,0,0,0.5);
}

.feedback-toast.error {
    background: rgba(220, 38, 38, 0.9);
}

.toast-msg {
    color: white;
    font-weight: bold;
    font-size: 1.2rem;
}

.coduck-comms {
    position: absolute;
    bottom: 2rem;
    left: 2rem;
    display: flex;
    align-items: flex-end;
    gap: 1rem;
    z-index: 50;
}

.comms-avatar {
    width: 60px;
    height: 60px;
    background: #000;
    border: 2px solid #0ea5e9;
    border-radius: 50%;
    position: relative;
    overflow: hidden;
}

.avatar-img {
    width: 100%;
    height: 100%;
    background-image: url('/image/coduck_face.png');
    background-size: cover;
}

.comms-box {
    background: rgba(2, 6, 23, 0.9);
    border: 1px solid #0ea5e9;
    padding: 1rem;
    border-radius: 12px 12px 12px 0;
    width: 300px;
}

.comms-header {
    color: #38bdf8;
    font-size: 0.7rem;
    margin-bottom: 0.5rem;
}

.comms-text {
    color: #e0f2fe;
    font-size: 0.9rem;
    line-height: 1.4;
}

/* --- EVALUATION VIEW --- */
.evaluation-view {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: #000;
    z-index: 1000;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow-y: auto; /* Enable scrolling if needed */
}

.watermark-bg {
    position: absolute;
    font-family: 'Orbitron';
    font-size: 10vw;
    font-weight: 900;
    color: rgba(255, 255, 255, 0.03);
    z-index: 0;
    transform: rotate(-15deg);
    pointer-events: none;
}

.report-card {
    position: relative;
    z-index: 10;
    width: 90%;
    max-width: 600px;
    background: #0c0a09;
    border: 1px solid #333;
    box-shadow: 0 0 50px rgba(0, 0, 0, 0.8);
    display: flex;
    flex-direction: column;
    padding: 0;
    margin: 2rem 0; /* Margin for scroll */
}

.report-header {
    background: #1c1917;
    padding: 1rem 2rem;
    border-bottom: 2px solid #0ea5e9;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.report-header h2 {
    color: #0ea5e9;
    margin: 0;
    font-family: 'Orbitron';
    font-size: 1.2rem;
}

.date-stamp {
    color: #57534e;
    font-size: 0.8rem;
}

/* Score Section */
.score-section {
    padding: 2rem;
    display: flex;
    justify-content: space-around;
    align-items: center;
    border-bottom: 1px dashed #333;
}

.score-circle-container {
    width: 120px;
    height: 120px;
    position: relative;
}

.circular-chart {
    display: block;
    margin: 0 auto;
    max-width: 100%;
    max-height: 100%;
}

.circle-bg {
    fill: none;
    stroke: #292524;
    stroke-width: 2.5;
}

.circle {
    fill: none;
    stroke-width: 2.5;
    stroke-linecap: round;
    stroke: #0ea5e9;
    animation: progress 1s ease-out forwards;
}

.percentage {
    fill: #fff;
    font-family: 'Orbitron';
    font-weight: bold;
    font-size: 0.5em; /* Scaled SVG font size */
    text-anchor: middle;
}

.score-label {
    text-align: center;
    font-size: 0.7rem;
    color: #78716c;
    margin-top: 0.5rem;
}

.tier-badge {
    text-align: center;
}

.tier-label {
    font-size: 0.8rem;
    color: #a8a29e;
    margin-bottom: 0.5rem;
}

.tier-value {
    font-family: 'Orbitron';
    font-size: 1.5rem;
    font-weight: 900;
    padding: 0.5rem 1rem;
    border: 1px solid #444;
    border-radius: 4px;
    color: #fff;
}
.tier-value.senior-architect { color: #f59e0b; border-color: #f59e0b; }
.tier-value.junior-architect { color: #38bdf8; border-color: #38bdf8; }

/* Analysis Box */
.analysis-box {
    margin: 1.5rem;
    background: #1c1917;
    border-left: 4px solid #0ea5e9;
    padding: 1.5rem;
    display: flex;
    gap: 1rem;
}

.box-icon {
    flex-shrink: 0;
}

.coduck-avatar-small {
    width: 40px;
    height: 40px;
    background: #000;
    border-radius: 50%;
    border: 1px solid #555;
    background-image: url('/image/coduck_face.png');
    background-size: cover;
}

.box-content h3 {
    margin: 0 0 0.5rem 0;
    color: #0ea5e9;
    font-size: 0.9rem;
}

.box-content p {
    margin: 0;
    color: #d6d3d1;
    font-size: 0.9rem;
    line-height: 1.5;
}

/* Breakdown List */
.breakdown-list {
    padding: 0 1.5rem 1.5rem 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.breakdown-item {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid #292524;
    padding: 1rem;
}

.item-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.8rem;
}

.item-title {
    width: 100px;
    font-size: 0.9rem;
    color: #a8a29e;
    font-weight: bold;
}

.item-score-bar {
    flex: 1;
    height: 6px;
    background: #292524;
    border-radius: 3px;
}

.item-score-fill {
    height: 100%;
    background: #0ea5e9;
    border-radius: 3px;
}

.item-points {
    font-family: 'Share Tech Mono';
    color: #fff;
}

.item-body {
    padding-left: 116px; /* Align with text */
}

.comment {
    color: #d6d3d1;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}

.improvements {
    margin: 0;
    padding: 0;
    list-style: none;
    color: #78716c;
    font-size: 0.85rem;
}

.report-actions {
    padding: 1.5rem;
    border-top: 1px solid #292524;
    display: flex;
    gap: 1rem;
}

.btn-retry, .btn-next-report {
    flex: 1;
    padding: 1rem;
    border: none;
    cursor: pointer;
    font-weight: bold;
    font-family: 'Orbitron';
    text-transform: uppercase;
    transition: all 0.2s;
}

.btn-retry {
    background: #292524;
    color: #a8a29e;
}
.btn-retry:hover { background: #44403c; }

.btn-next-report {
    background: #0ea5e9;
    color: #000;
}
.btn-next-report:hover { background: #38bdf8; }


/* Transitions */
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.pop-enter-active { animation: popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.pop-leave-active { transition: opacity 0.3s; opacity: 0; }

@keyframes popIn {
    from { opacity: 0; transform: translate(-50%, 20px) scale(0.9); }
    to { opacity: 1; transform: translate(-50%, 0) scale(1); }
}

.btn-primary {
    background: #0ea5e9;
    color: white;
    padding: 0.8rem 1.5rem;
    border: none;
    border-radius: 4px;
    font-weight: bold;
    cursor: pointer;
}
.btn-primary:hover { background: #0284c7; }

/* Animations */
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); } 70% { box-shadow: 0 0 0 20px rgba(239, 68, 68, 0); } 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); } }
@keyframes progress { from { stroke-dasharray: 0, 100; } }

</style>
