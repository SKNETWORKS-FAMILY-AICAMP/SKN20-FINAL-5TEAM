<template>
  <div class="ops-practice-page">
    <div class="game-container">
      <!-- 헤더 -->
      <div class="header">
        <h1>OPS PRACTICE</h1>
        <div class="subtitle">// INCIDENT RESPONSE TRAINING SYSTEM v2.0</div>
      </div>

      <!-- 난이도 선택 화면 -->
      <div class="difficulty-screen" :class="{ hidden: currentScreen !== 'difficulty' }">
        <div class="difficulty-title">난이도를 선택하세요</div>
        <div class="difficulty-buttons">
          <button class="difficulty-btn easy" @click="startGame('easy')">
            <span>EASY</span>
          </button>
          <button class="difficulty-btn medium" @click="startGame('medium')">
            <span>MEDIUM</span>
          </button>
          <button class="difficulty-btn hard" @click="startGame('hard')">
            <span>HARD</span>
          </button>
        </div>
      </div>

      <!-- 게임 화면 -->
      <div class="game-screen" :style="{ display: currentScreen === 'game' ? 'block' : 'none' }">
        <div class="game-grid">
          <!-- 왼쪽: 문제 화면 (컴퓨터 모니터) -->
          <div class="monitor">
            <div class="screen-content">
              <div class="problem-header">{{ problemTitle }}</div>
              <div class="problem-content" v-html="problemContent"></div>
            </div>
          </div>

          <!-- 오른쪽: 사이드 패널 -->
          <div class="side-panel">
            <!-- 시도 횟수 -->
            <div class="panel-box">
              <div class="panel-title">남은 시도 횟수</div>
              <div class="attempts-counter">{{ attempts }}</div>
            </div>

            <!-- 힌트 -->
            <div class="panel-box">
              <div class="panel-title">힌트</div>
              <button class="hint-btn" @click="toggleHint">힌트 보기</button>
              <div class="hint-content" :class="{ active: showHint }">
                {{ hintContent }}
              </div>
            </div>

            <!-- 액션 로그 -->
            <div class="panel-box">
              <div class="panel-title">액션 로그</div>
              <div class="action-log">
                <div v-for="(log, idx) in actionLogs" :key="idx" :class="'log-entry ' + log.type">
                  {{ log.message }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 메트릭스 디스플레이 -->
        <div class="metrics-display">
          <div v-for="(metric, key) in metrics" :key="key" class="metric-card">
            <div class="metric-label">{{ formatMetricLabel(key) }}</div>
            <div class="metric-value" :class="getMetricClass(metric)">
              {{ metric.value }}{{ metric.unit }}
            </div>
            <div class="metric-bar">
              <div class="metric-fill" :class="getMetricClass(metric)" :style="{ width: getMetricWidth(metric) + '%' }"></div>
            </div>
          </div>
        </div>

        <!-- 입력 영역 -->
        <div class="input-area">
          <input type="text" v-model="actionInput" @keypress.enter="submitAction" class="action-input" placeholder="대응 명령을 입력하세요... (예: restart service, scale up, check logs)">
          <button class="submit-btn" @click="submitAction">명령 실행</button>
        </div>
      </div>

      <!-- 결과 화면 -->
      <div class="result-screen" :style="{ display: currentScreen === 'result' ? 'flex' : 'none' }">
        <div class="result-title">{{ resultTitle }}</div>
        <div class="result-stats">
          <div class="stat-box">
            <div class="stat-label">사용한 시도</div>
            <div class="stat-value">{{ usedAttempts }}</div>
          </div>
          <div class="stat-box">
            <div class="stat-label">최종 점수</div>
            <div class="stat-value">{{ finalScore }}</div>
          </div>
          <div class="stat-box">
            <div class="stat-label">난이도</div>
            <div class="stat-value">{{ difficultyLevel }}</div>
          </div>
        </div>
        <div style="margin: 30px 0; font-size: 1.2em; line-height: 1.8;" v-html="resultMessage"></div>
        
        <!-- AI 코치 피드백 섹션 -->
        <div style="margin: 30px 0;">
          <button class="hint-btn" @click="getAIFeedback" :disabled="aiFeedbackLoading" style="margin-bottom: 20px;">
            🤖 AI 코치 해설 받기
          </button>
          <div v-if="showAIFeedback" style="background: rgba(0, 243, 255, 0.05); border: 2px solid var(--neon-cyan); border-radius: 10px; padding: 20px; margin-top: 20px; text-align: left;">
            <div style="font-size: 1.3em; font-weight: 600; margin-bottom: 15px; color: var(--neon-cyan);">
              📋 AI 코치 분석
            </div>
            <div style="font-size: 1.1em; line-height: 1.8; color: rgba(255, 255, 255, 0.9);">
              <div v-if="aiFeedbackLoading" style="text-align: center; padding: 20px;">
                <div class="loading-spinner"></div>
                <div style="margin-top: 15px; color: var(--neon-cyan);">분석 중...</div>
              </div>
              <div v-else style="white-space: pre-line;">{{ aiFeedbackContent }}</div>
            </div>
          </div>
        </div>
        
        <button class="hint-btn" @click="resetGame">다시 도전하기</button>
      </div>

      <!-- 피드백 메시지 -->
      <div class="feedback-message" :class="{ show: showFeedback, [feedbackType]: true }">
        {{ feedbackMessage }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import { useGameStore } from '@/stores/game';

// 게임 및 UI 상태
const gameStore = useGameStore();
const currentScreen = ref('difficulty');
const difficulty = ref('');
const attempts = ref(7);
const currentProblem = ref(null);
const metrics = reactive({});
const actions = ref([]);
const solved = ref(false);

// UI 상태
const actionInput = ref('');
const showHint = ref(false);
const actionLogs = ref([{ message: '시스템 준비 완료...', type: 'action' }]);
const problemTitle = ref('시스템 장애 발생!');
const problemContent = ref('');
const hintContent = ref('');

// 피드백
const showFeedback = ref(false);
const feedbackMessage = ref('');
const feedbackType = ref('');

// 결과
const resultTitle = ref('');
const resultMessage = ref('');
const usedAttempts = ref(0);
const finalScore = ref(0);
const difficultyLevel = ref('');

// AI 피드백
const showAIFeedback = ref(false);
const aiFeedbackLoading = ref(false);
const aiFeedbackContent = ref('');

/**
 * [2026-01-25] 하드코딩된 problems 객체 제거. 
 * 대신 startGame 시 gameStore.activeUnit.problems에서 난이도(difficulty)가 일치하는 문제를 찾습니다.
 */

function startGame(diff) {
  difficulty.value = diff;
  
  // [2026-01-25] DB 연동: 현재 유닛의 문제 목록에서 선택한 난이도와 일치하는 시나리오 로드
  const unitProblems = gameStore.activeUnit?.problems || [];
  const found = unitProblems.find(p => p.difficulty === diff || p.config?.difficulty === diff);
  
  if (!found) {
    addLog(`[Error] ${diff} 난이도에 해당하는 시나리오가 DB에 없습니다.`, 'warning');
    // 임시 폴백 (데이터 로딩 전일 경우 대비)
    return;
  }
  
  currentProblem.value = found.config || found;
  
  // 기존 metrics 완전히 초기화
  Object.keys(metrics).forEach(key => delete metrics[key]);
  
  // 새로운 metrics 할당
  Object.assign(metrics, JSON.parse(JSON.stringify(currentProblem.value.initialMetrics)));
  
  attempts.value = 7;
  actions.value = [];
  solved.value = false;
  currentScreen.value = 'game';
  
  displayProblem();
}

function displayProblem() {
  const problem = currentProblem.value;
  problemTitle.value = problem.title;
  problemContent.value = `
    <div style="margin-bottom: 20px;">
      <strong style="color: var(--danger-red);">🚨 상황:</strong><br>
      ${problem.scenario}
    </div>
    <div style="margin-bottom: 20px;">
      <strong style="color: var(--warning-orange);">⚠️ 제약사항:</strong><br>
      ${problem.constraints?.replace(/\n/g, '<br>') || ''}
    </div>
  `;
  hintContent.value = problem.hint;
}

function toggleHint() {
  showHint.value = !showHint.value;
}

/**
 * [2026-01-25] 승리 조건 검증 유틸리티
 * - DB의 winConditionType 필드에 따라 각기 다른 평가 로직 적용
 */
function checkWinCondition(m) {
  const type = currentProblem.value.winConditionType;
  if (!type) {
    // 폴백: 기본 조건 (응답 시간 1초 미만)
    return m.responseTime?.value < 1000;
  }
  
  switch(type) {
    case 'ops_basic':
      return m.responseTime?.value < 1000 && (m.cpu ? m.cpu.value < 70 : true);
    case 'ops_db':
      return m.errorRate?.value < 2 && (m.activeConnections ? m.activeConnections.value < 400 : true);
    case 'ops_oom':
      return m.heapUsage?.value < 75 && m.responseTime?.value < 2000;
    default:
      return false;
  }
}

function submitAction() {
  if (!actionInput.value.trim()) return;
  
  attempts.value--;
  actions.value.push(actionInput.value);
  addLog(actionInput.value, 'action');
  
  const result = processAction(actionInput.value.toLowerCase());
  showFeedbackMsg(result.message, result.type);
  
  actionInput.value = '';
  
  setTimeout(() => {
    // [2026-01-25] 동적 검증 함수 호출
    if (checkWinCondition(metrics)) {
      solved.value = true;
      showResult(true);
    } else if (attempts.value <= 0) {
      showResult(false);
    }
  }, 1500);
}

function processAction(action) {
  const solutions = currentProblem.value.solutions;
  let matched = false;
  
  for (let solution of solutions) {
    const hasKeyword = solution.keywords.some(keyword => action.includes(keyword));
    if (hasKeyword) {
      matched = true;
      for (let [metricKey, change] of Object.entries(solution.effect)) {
        if (metrics[metricKey]) {
          metrics[metricKey].value += change;
        }
      }
      break;
    }
  }
  
  if (!matched) {
    return { type: 'warning', message: '명령이 효과가 없습니다...' };
  } else {
    return { type: 'success', message: '명령을 실행했습니다.' };
  }
}

function showFeedbackMsg(message, type) {
  feedbackMessage.value = message;
  feedbackType.value = type;
  showFeedback.value = true;
  
  setTimeout(() => {
    showFeedback.value = false;
  }, 2000);
}

function addLog(message, type) {
  actionLogs.value.push({ message, type });
}

function showResult(won) {
  currentScreen.value = 'result';
  usedAttempts.value = 7 - attempts.value;
  finalScore.value = won ? Math.max(100 - (usedAttempts.value * 10), 50) : 0;
  difficultyLevel.value = difficulty.value.toUpperCase();
  
  if (won) {
    resultTitle.value = '미션 성공!';
    resultMessage.value = `
      <span style="color: var(--success-green);">훌륭합니다! 시스템을 성공적으로 복구했습니다.</span><br>
      효율적인 문제 해결 능력을 보여주셨습니다.
    `;
  } else {
    resultTitle.value = '미션 실패';
    resultMessage.value = `
      <span style="color: var(--danger-red);">시도 횟수를 모두 소진했습니다.</span><br>
      다시 한번 도전해보세요. 힌트를 참고하면 도움이 될 것입니다.
    `;
  }
}

function resetGame() {
  currentScreen.value = 'difficulty';
  actionLogs.value = [{ message: '시스템 준비 완료...', type: 'action' }];
  showAIFeedback.value = false;
}

async function getAIFeedback() {
  showAIFeedback.value = true;
  aiFeedbackLoading.value = true;
  
  try {
    const actionsList = actions.value.map((a, i) => `${i + 1}. ${a}`).join('\n');
    
    // [2026-01-25] Anthropic API 호출 (실제 환경에서는 백엔드 프록시 권장)
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "claude-3-5-sonnet-20241022",
        max_tokens: 1000,
        messages: [{
          role: "user",
          content: `당신은 Staff SRE 코치입니다. 장애 대응 훈련에서 학습자의 행동을 분석하고 피드백을 제공하세요.

**장애 정보:**
- 시나리오: ${currentProblem.value.title}
- 상황: ${currentProblem.value.scenario}
- 난이도: ${difficulty.value}

**학습자 수행:**
- 취한 조치들:
${actionsList || '(조치 없음)'}
- 사용한 시도 횟수: ${usedAttempts.value}/7
- 최종 점수: ${finalScore.value}/100
- 해결 여부: ${solved.value ? '성공' : '실패'}

**피드백 요구사항 (3-4문장, 한국어로):**
1. 수행에 대한 전반적 평가
2. 가장 효과적이었을 접근법 제시
3. 구체적인 개선점 1-2가지

간결하고 실용적인 조언을 해주세요.`
        }]
      })
    });

    const data = await response.json();
    
    if (data.content && data.content[0]) {
      aiFeedbackContent.value = data.content[0].text;
    }
  } catch (error) {
    console.error('AI 피드백 오류:', error);
    aiFeedbackContent.value = '⚠️ AI 피드백을 불러오는데 실패했습니다. 네트워크 연결을 확인해주세요.';
  } finally {
    aiFeedbackLoading.value = false;
  }
}

function formatMetricLabel(key) {
  const labels = {
    responseTime: '응답 시간',
    cpu: 'CPU 사용률',
    memory: '메모리 사용률',
    errorRate: '에러율',
    activeConnections: '활성 연결',
    maxConnections: '최대 연결',
    queryTime: '쿼리 시간',
    heapUsage: '힙 사용률',
    gcTime: 'GC 시간',
    throughput: '처리량'
  };
  return labels[key] || key;
}

function getMetricClass(metric) {
  if (metric.value <= metric.threshold.good) return 'good';
  if (metric.value <= metric.threshold.warning) return 'warning';
  return 'critical';
}

function getMetricWidth(metric) {
  const max = metric.threshold.warning * 1.5;
  return Math.min((metric.value / max) * 100, 100);
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --neon-cyan: #00f3ff;
  --neon-magenta: #ff00ff;
  --neon-yellow: #ffff00;
  --dark-bg: #0a0e17;
  --panel-bg: #1a1f2e;
  --screen-glow: rgba(0, 243, 255, 0.3);
  --danger-red: #ff0055;
  --success-green: #00ff88;
  --warning-orange: #ff9500;
}

.ops-practice-page {
  font-family: 'Rajdhani', sans-serif;
  background: linear-gradient(135deg, #0a0e17 0%, #1a1f2e 50%, #0a0e17 100%);
  color: var(--neon-cyan);
  min-height: 100vh;
  overflow-x: hidden;
  position: relative;
}

.ops-practice-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    repeating-linear-gradient(0deg, rgba(0, 243, 255, 0.03) 0px, transparent 1px, transparent 2px, rgba(0, 243, 255, 0.03) 3px),
    repeating-linear-gradient(90deg, rgba(0, 243, 255, 0.03) 0px, transparent 1px, transparent 2px, rgba(0, 243, 255, 0.03) 3px);
  pointer-events: none;
  z-index: 1;
}

.game-container {
  position: relative;
  z-index: 2;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
}

.header h1 {
  font-family: 'Orbitron', sans-serif;
  font-size: 4em;
  font-weight: 900;
  background: linear-gradient(45deg, var(--neon-cyan), var(--neon-magenta), var(--neon-yellow));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 30px var(--screen-glow);
  animation: glitch 3s infinite;
  letter-spacing: 8px;
}

@keyframes glitch {
  0%, 100% { transform: translate(0); }
  20% { transform: translate(-2px, 2px); }
  40% { transform: translate(-2px, -2px); }
  60% { transform: translate(2px, 2px); }
  80% { transform: translate(2px, -2px); }
}

.subtitle {
  font-family: 'JetBrains Mono', monospace;
  color: var(--neon-cyan);
  font-size: 1.2em;
  margin-top: 10px;
  opacity: 0.8;
}

/* 난이도 선택 화면 */
.difficulty-screen {
  background: var(--panel-bg);
  border: 3px solid var(--neon-cyan);
  border-radius: 20px;
  padding: 60px;
  box-shadow: 0 0 40px var(--screen-glow), inset 0 0 20px rgba(0, 243, 255, 0.1);
  text-align: center;
}

.difficulty-screen.hidden {
  display: none;
}

.difficulty-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 2.5em;
  margin-bottom: 40px;
  color: var(--neon-yellow);
  text-shadow: 0 0 20px var(--neon-yellow);
}

.difficulty-buttons {
  display: flex;
  justify-content: center;
  gap: 30px;
  flex-wrap: wrap;
}

.difficulty-btn {
  font-family: 'Orbitron', sans-serif;
  padding: 30px 50px;
  font-size: 1.5em;
  border: 3px solid;
  background: transparent;
  cursor: pointer;
  border-radius: 15px;
  transition: all 0.3s;
  font-weight: 700;
  position: relative;
  overflow: hidden;
}

.difficulty-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.3s, height 0.3s;
}

.difficulty-btn:hover::before {
  width: 300%;
  height: 300%;
}

.difficulty-btn span {
  position: relative;
  z-index: 1;
}

.difficulty-btn.easy {
  border-color: var(--success-green);
  color: var(--success-green);
}

.difficulty-btn.easy::before {
  background: var(--success-green);
}

.difficulty-btn.easy:hover {
  box-shadow: 0 0 30px var(--success-green);
}

.difficulty-btn.medium {
  border-color: var(--warning-orange);
  color: var(--warning-orange);
}

.difficulty-btn.medium::before {
  background: var(--warning-orange);
}

.difficulty-btn.medium:hover {
  box-shadow: 0 0 30px var(--warning-orange);
}

.difficulty-btn.hard {
  border-color: var(--danger-red);
  color: var(--danger-red);
}

.difficulty-btn.hard::before {
  background: var(--danger-red);
}

.difficulty-btn.hard:hover {
  box-shadow: 0 0 30px var(--danger-red);
}

.difficulty-btn:hover span {
  color: var(--dark-bg);
}

/* 메인 게임 화면 */
.game-screen {
  animation: fadeIn 0.5s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.game-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

/* 컴퓨터 모니터 스타일 */
.monitor {
  background: #000;
  border: 15px solid #2a2a2a;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 
    0 0 0 3px #1a1a1a,
    0 0 50px rgba(0, 243, 255, 0.3),
    inset 0 0 30px rgba(0, 243, 255, 0.1);
  position: relative;
}

.monitor::before {
  content: '';
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 10px;
  background: #1a1a1a;
  border-radius: 5px;
}

.monitor::after {
  content: '';
  position: absolute;
  bottom: -40px;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 30px;
  background: linear-gradient(to bottom, #2a2a2a, #1a1a1a);
  border-radius: 0 0 20px 20px;
}

.screen-content {
  background: rgba(0, 20, 10, 0.9);
  border: 2px solid var(--neon-cyan);
  border-radius: 10px;
  padding: 30px;
  min-height: 500px;
  position: relative;
  overflow: hidden;
}

.screen-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 243, 255, 0.03) 0px,
    transparent 1px,
    transparent 2px,
    rgba(0, 243, 255, 0.03) 3px
  );
  pointer-events: none;
  animation: scanline 8s linear infinite;
}

@keyframes scanline {
  0% { transform: translateY(0); }
  100% { transform: translateY(100%); }
}

.problem-header {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.8em;
  color: var(--neon-yellow);
  margin-bottom: 20px;
  text-shadow: 0 0 10px var(--neon-yellow);
}

.problem-content {
  font-family: 'JetBrains Mono', monospace;
  line-height: 1.8;
  color: var(--success-green);
  position: relative;
  z-index: 1;
}

/* 사이드 패널 */
.side-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-box {
  background: var(--panel-bg);
  border: 2px solid var(--neon-cyan);
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 0 20px rgba(0, 243, 255, 0.2);
}

.panel-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.2em;
  margin-bottom: 15px;
  color: var(--neon-cyan);
  text-shadow: 0 0 10px var(--neon-cyan);
}

.attempts-counter {
  font-family: 'Orbitron', sans-serif;
  font-size: 3em;
  text-align: center;
  color: var(--neon-yellow);
  text-shadow: 0 0 20px var(--neon-yellow);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.hint-btn {
  width: 100%;
  padding: 12px;
  background: transparent;
  border: 2px solid var(--neon-magenta);
  color: var(--neon-magenta);
  font-family: 'Orbitron', sans-serif;
  font-size: 1em;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.hint-btn:hover:not(:disabled) {
  background: var(--neon-magenta);
  color: #000;
  box-shadow: 0 0 20px var(--neon-magenta);
}

.hint-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hint-content {
  overflow: hidden;
  transition: max-height 0.3s;
  margin-top: 15px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.9);
}

.hint-content.active {
  max-height: 300px;
}

.action-log {
  background: rgba(0, 0, 0, 0.5);
  border-radius: 8px;
  padding: 15px;
  max-height: 200px;
  overflow-y: auto;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9em;
}

.log-entry {
  padding: 5px;
  margin-bottom: 5px;
  border-left: 3px solid;
  padding-left: 10px;
}

.log-entry.action {
  border-color: var(--neon-cyan);
  color: var(--neon-cyan);
}

.log-entry.system {
  border-color: var(--success-green);
  color: var(--success-green);
}

/* 메트릭 디스플레이 */
.metrics-display {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  background: var(--panel-bg);
  border: 2px solid var(--neon-cyan);
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 0 20px rgba(0, 243, 255, 0.2);
}

.metric-label {
  font-size: 0.9em;
  opacity: 0.8;
  margin-bottom: 10px;
}

.metric-value {
  font-family: 'Orbitron', sans-serif;
  font-size: 2em;
  font-weight: 700;
  margin-bottom: 15px;
}

.metric-value.good {
  color: var(--success-green);
}

.metric-value.warning {
  color: var(--warning-orange);
}

.metric-value.critical {
  color: var(--danger-red);
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.5; }
}

.metric-bar {
  width: 100%;
  height: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  transition: width 0.5s;
}

.metric-fill.good {
  background: var(--success-green);
}

.metric-fill.warning {
  background: var(--warning-orange);
}

.metric-fill.critical {
  background: var(--danger-red);
}

/* 입력 영역 */
.input-area {
  display: flex;
  gap: 15px;
  background: var(--panel-bg);
  padding: 20px;
  border-radius: 15px;
  border: 2px solid var(--neon-cyan);
}

.action-input {
  flex: 1;
  background: rgba(0, 0, 0, 0.5);
  border: 2px solid var(--neon-cyan);
  color: var(--neon-cyan);
  padding: 15px;
  border-radius: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 1em;
}

.action-input:focus {
  outline: none;
  box-shadow: 0 0 15px var(--screen-glow);
}

.submit-btn {
  padding: 15px 40px;
  background: var(--neon-magenta);
  color: #000;
  border: none;
  border-radius: 8px;
  font-family: 'Orbitron', sans-serif;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 1em;
}

.submit-btn:hover {
  background: var(--neon-cyan);
  box-shadow: 0 0 20px var(--screen-glow);
  transform: scale(1.05);
}

/* 결과 화면 */
.result-screen {
  background: var(--panel-bg);
  border: 3px solid var(--neon-cyan);
  border-radius: 20px;
  padding: 60px;
  box-shadow: 0 0 40px var(--screen-glow), inset 0 0 20px rgba(0, 243, 255, 0.1);
  text-align: center;
  flex-direction: column;
  align-items: center;
  animation: fadeIn 0.5s;
}

.result-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 3em;
  margin-bottom: 40px;
  background: linear-gradient(45deg, var(--neon-cyan), var(--neon-magenta), var(--neon-yellow));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 30px var(--screen-glow);
}

.result-stats {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.stat-box {
  background: rgba(0, 0, 0, 0.5);
  border: 2px solid var(--neon-cyan);
  border-radius: 15px;
  padding: 20px 40px;
  min-width: 150px;
}

.stat-label {
  font-size: 0.9em;
  opacity: 0.8;
  margin-bottom: 10px;
}

.stat-value {
  font-family: 'Orbitron', sans-serif;
  font-size: 2.5em;
  font-weight: 700;
  color: var(--neon-yellow);
  text-shadow: 0 0 20px var(--neon-yellow);
}

/* 피드백 메시지 */
.feedback-message {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0);
  padding: 30px 50px;
  border-radius: 15px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.5em;
  font-weight: 700;
  z-index: 1000;
  opacity: 0;
  transition: all 0.3s;
}

.feedback-message.show {
  transform: translate(-50%, -50%) scale(1);
  opacity: 1;
}

.feedback-message.success {
  background: var(--success-green);
  color: #000;
  box-shadow: 0 0 50px var(--success-green);
}

.feedback-message.warning {
  background: var(--warning-orange);
  color: #000;
  box-shadow: 0 0 50px var(--warning-orange);
}

.feedback-message.error {
  background: var(--danger-red);
  color: #fff;
  box-shadow: 0 0 50px var(--danger-red);
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(0, 243, 255, 0.2);
  border-top-color: var(--neon-cyan);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 1024px) {
  .game-grid {
    grid-template-columns: 1fr;
  }
  
  .header h1 {
    font-size: 2.5em;
  }
  
  .metrics-display {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
}
</style>