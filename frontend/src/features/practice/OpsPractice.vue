<template>
  <div class="game-container">
    <!-- 헤더 -->
    <div class="header">
      <h1>OPS PRACTICE</h1>
      <div class="subtitle">// INCIDENT RESPONSE TRAINING SYSTEM v2.0</div>
    </div>

    <!-- 난이도 선택 화면 -->
    <div v-if="currentScreen === 'difficulty'" class="difficulty-screen">
      <h2 class="difficulty-title">난이도 선택</h2>
      <div class="difficulty-buttons">
        <button @click="selectDifficulty('easy')" class="difficulty-btn easy">
          <span>EASY<br><small>입문자</small></span>
        </button>
        <button @click="selectDifficulty('medium')" class="difficulty-btn medium">
          <span>MEDIUM<br><small>중급자</small></span>
        </button>
        <button @click="selectDifficulty('hard')" class="difficulty-btn hard">
          <span>HARD<br><small>전문가</small></span>
        </button>
      </div>
    </div>

    <!-- 메인 게임 화면 -->
    <div v-if="currentScreen === 'game'" class="game-screen">
      <div class="game-grid">
        <!-- 왼쪽: 메인 화면 -->
        <div>
          <!-- 문제 설명 모니터 -->
          <div class="monitor">
            <div class="screen-header">
              <span class="screen-title">{{ currentProblem.title }}</span>
              <span class="terminal-indicator">◉ LIVE</span>
            </div>
            <div class="problem-description">
              <div class="alert-badge">🚨 ALERT</div>
              <p>{{ currentProblem.scenario }}</p>
            </div>
          </div>

          <!-- 메트릭 대시보드 -->
          <div class="metrics-dashboard">
            <div class="dashboard-header">
              <span>SYSTEM METRICS</span>
              <span class="live-indicator">● MONITORING</span>
            </div>
            <div class="metrics-grid">
              <div
                v-for="(metric, key) in metrics"
                :key="key"
                class="metric-card"
                :class="getMetricStatus(metric)"
              >
                <div class="metric-label">{{ metric.label }}</div>
                <div class="metric-value">{{ metric.value }}{{ metric.unit }}</div>
                <div class="metric-bar">
                  <div
                    class="metric-fill"
                    :style="{ width: getMetricPercentage(metric) + '%' }"
                  ></div>
                </div>
                <div class="metric-threshold" v-if="metric.threshold">
                  <span>임계값: {{ metric.threshold.critical }}{{ metric.unit }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 액션 입력 패널 -->
          <div class="action-panel">
            <div class="panel-header">
              <span>COMMAND INPUT</span>
              <span class="attempts-counter">남은 시도: {{ attempts }}</span>
            </div>
            <div class="input-group">
              <input
                v-model="actionInput"
                @keypress.enter="submitAction"
                type="text"
                class="action-input"
                placeholder="조치를 입력하세요... (예: restart service)"
                :disabled="solved"
              />
              <button @click="submitAction" class="submit-btn" :disabled="solved">
                실행 →
              </button>
            </div>
            <div class="feedback-message" :class="feedbackType" v-show="showFeedback">
              {{ feedbackMessage }}
            </div>
          </div>
        </div>

        <!-- 오른쪽: 사이드바 -->
        <div>
          <!-- 힌트 패널 -->
          <div class="hint-panel">
            <div class="panel-header">
              <span>💡 HINTS</span>
            </div>
            <div class="hint-content">
              <div v-for="(hint, index) in currentProblem.hints" :key="index" class="hint-item">
                <span class="hint-number">{{ index + 1 }}</span>
                <span>{{ hint }}</span>
              </div>
            </div>
          </div>

          <!-- 액션 로그 -->
          <div class="log-panel">
            <div class="panel-header">
              <span>ACTION LOG</span>
            </div>
            <div class="action-log" ref="actionLog">
              <div
                v-for="(log, index) in actionLogs"
                :key="index"
                :class="['log-entry', log.type]"
              >
                > {{ log.message }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 결과 화면 -->
    <div v-if="currentScreen === 'result'" class="result-screen">
      <div class="result-container">
        <h2 :class="['result-title', solved ? 'success' : 'failure']">
          {{ solved ? '미션 성공!' : '미션 실패' }}
        </h2>
        <div class="result-message" v-html="resultMessage"></div>

        <div class="result-stats">
          <div class="stat-item">
            <div class="stat-label">사용한 시도</div>
            <div class="stat-value">{{ usedAttempts }} / 7</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">점수</div>
            <div class="stat-value score">{{ finalScore }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">난이도</div>
            <div class="stat-value">{{ difficulty.toUpperCase() }}</div>
          </div>
        </div>

        <div class="result-actions">
          <button @click="getAIFeedback" class="ai-feedback-btn" :disabled="aiFeedbackLoading">
            {{ aiFeedbackLoading ? '분석 중...' : aiFeedbackReceived ? '✓ 분석 완료' : '🤖 AI 코치 해설 받기' }}
          </button>
          <button @click="resetGame" class="retry-btn">다시 도전하기</button>
        </div>

        <!-- AI 피드백 섹션 -->
        <div v-if="showAIFeedback" class="ai-feedback-section">
          <div class="feedback-header">
            <span>🎯 AI 코치의 분석</span>
          </div>
          <div class="ai-feedback-content">
            <div v-if="aiFeedbackLoading" style="text-align: center; padding: 20px;">
              <div class="loading-spinner"></div>
              <div style="margin-top: 15px; color: var(--neon-cyan);">
                AI가 당신의 대응을 분석하고 있습니다...
              </div>
            </div>
            <div v-else-if="aiFeedbackError" style="color: var(--danger-red); text-align: center; padding: 20px;">
              ⚠️ AI 피드백을 불러오는데 실패했습니다.<br>
              <span style="font-size: 0.9em; opacity: 0.7;">네트워크 연결을 확인해주세요.</span>
            </div>
            <div v-else style="white-space: pre-line; line-height: 1.8;">
              {{ aiFeedback }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick } from 'vue';

// 화면 상태
const currentScreen = ref('difficulty');
const difficulty = ref('');
const attempts = ref(7);
const solved = ref(false);
const actionInput = ref('');
const actionLogs = ref([{ message: '시스템 준비 완료...', type: 'action' }]);
const userActions = ref([]);

// 피드백
const showFeedback = ref(false);
const feedbackMessage = ref('');
const feedbackType = ref('');

// AI 피드백
const showAIFeedback = ref(false);
const aiFeedbackLoading = ref(false);
const aiFeedbackReceived = ref(false);
const aiFeedbackError = ref(false);
const aiFeedback = ref('');

// 문제 데이터베이스
const problems = {
  easy: [
    {
      title: 'CPU 과부하 경고',
      scenario: '웹 서버의 CPU 사용률이 갑자기 90%를 넘어섰습니다. 사용자들이 느린 응답 속도를 보고하고 있습니다.',
      hints: [
        'CPU를 많이 사용하는 프로세스를 확인해보세요',
        '불필요한 서비스를 중지하거나 재시작할 수 있습니다',
        '서버 스케일링도 고려해볼 수 있습니다'
      ],
      solutions: [
        {
          keywords: ['restart', 'service', '재시작', '서비스'],
          effect: { cpu: -30, latency: -20 }
        },
        {
          keywords: ['scale', 'autoscale', '스케일', '확장'],
          effect: { cpu: -40, latency: -30 }
        },
        {
          keywords: ['kill', 'process', '프로세스', '종료'],
          effect: { cpu: -25, latency: -15 }
        }
      ],
      winCondition: (metrics) => metrics.cpu.value < 50 && metrics.latency.value < 300
    },
    {
      title: '메모리 누수 감지',
      scenario: '애플리케이션 서버의 메모리 사용량이 계속 증가하고 있습니다. 현재 85%를 초과했습니다.',
      hints: [
        '메모리를 많이 사용하는 프로세스를 찾아보세요',
        '애플리케이션을 재시작하면 메모리가 해제됩니다',
        '메모리 프로파일링 도구를 사용할 수 있습니다'
      ],
      solutions: [
        {
          keywords: ['restart', 'application', '재시작', '앱'],
          effect: { memory: -50, cpu: -10 }
        },
        {
          keywords: ['clear', 'cache', '캐시', '삭제'],
          effect: { memory: -30 }
        },
        {
          keywords: ['gc', 'garbage', '가비지'],
          effect: { memory: -25 }
        }
      ],
      winCondition: (metrics) => metrics.memory.value < 70
    }
  ],
  medium: [
    {
      title: '데이터베이스 연결 풀 고갈',
      scenario: '데이터베이스 연결 풀이 가득 차서 새로운 요청을 처리할 수 없습니다. 에러율이 급증하고 있습니다.',
      hints: [
        '연결 풀 설정을 확인해보세요',
        '좀비 커넥션을 정리해야 할 수 있습니다',
        '데이터베이스 서버의 상태도 확인이 필요합니다'
      ],
      solutions: [
        {
          keywords: ['pool', 'increase', 'size', '풀', '증가', '크기'],
          effect: { errorRate: -30, latency: -20 }
        },
        {
          keywords: ['kill', 'idle', 'connection', '종료', '유휴', '연결'],
          effect: { errorRate: -25, cpu: -10 }
        },
        {
          keywords: ['restart', 'database', '재시작', 'db'],
          effect: { errorRate: -40, latency: -25, cpu: 10 }
        }
      ],
      winCondition: (metrics) => metrics.errorRate.value < 2 && metrics.latency.value < 400
    }
  ],
  hard: [
    {
      title: '대규모 DDoS 공격',
      scenario: '비정상적인 트래픽이 급증하여 초당 50,000개 이상의 요청이 들어오고 있습니다. 정상 사용자도 서비스를 이용할 수 없습니다.',
      hints: [
        'Rate limiting을 적용해야 합니다',
        'CDN이나 WAF 서비스 활용을 고려하세요',
        'IP 차단 규칙을 설정할 수 있습니다',
        '트래픽 패턴을 분석하여 악성 요청을 식별하세요'
      ],
      solutions: [
        {
          keywords: ['rate', 'limit', 'throttle', '제한'],
          effect: { traffic: -200, latency: -30, errorRate: -15 }
        },
        {
          keywords: ['firewall', 'waf', 'block', '방화벽', '차단'],
          effect: { traffic: -300, errorRate: -25 }
        },
        {
          keywords: ['cdn', 'cache', 'cloudflare'],
          effect: { traffic: -250, latency: -40 }
        },
        {
          keywords: ['scale', 'autoscale', '스케일'],
          effect: { latency: -20, cpu: -15, traffic: 50 }
        }
      ],
      winCondition: (metrics) => 
        metrics.traffic.value < 1000 && 
        metrics.latency.value < 500 && 
        metrics.errorRate.value < 5
    }
  ]
};

// 현재 문제
const currentProblem = ref(null);

// 메트릭
const metrics = reactive({});

// 난이도 선택
function selectDifficulty(level) {
  difficulty.value = level;
  const problemList = problems[level];
  currentProblem.value = problemList[Math.floor(Math.random() * problemList.length)];
  initializeMetrics();
  currentScreen.value = 'game';
  addLog('미션 시작...', 'system');
}

// 메트릭 초기화
function initializeMetrics() {
  const baseMetrics = {
    cpu: { label: 'CPU 사용률', value: 85, unit: '%', max: 100, threshold: { warning: 70, critical: 90 } },
    memory: { label: '메모리 사용량', value: 78, unit: '%', max: 100, threshold: { warning: 75, critical: 90 } },
    latency: { label: '응답 시간', value: 450, unit: 'ms', max: 1000, threshold: { warning: 300, critical: 500 } },
    errorRate: { label: '에러율', value: 8.5, unit: '%', max: 20, threshold: { warning: 3, critical: 10 } }
  };

  if (difficulty.value === 'hard') {
    baseMetrics.traffic = { 
      label: '초당 요청수', 
      value: 5200, 
      unit: ' req/s', 
      max: 6000, 
      threshold: { warning: 1000, critical: 3000 } 
    };
  }

  Object.assign(metrics, baseMetrics);
}

// 메트릭 상태
function getMetricStatus(metric) {
  if (!metric.threshold) return '';
  if (metric.value >= metric.threshold.critical) return 'critical';
  if (metric.value >= metric.threshold.warning) return 'warning';
  return 'normal';
}

// 메트릭 퍼센티지
function getMetricPercentage(metric) {
  return Math.min((metric.value / metric.max) * 100, 100);
}

// 액션 제출
function submitAction() {
  const action = actionInput.value.trim().toLowerCase();
  if (!action || solved.value) return;

  attempts.value--;
  userActions.value.push(actionInput.value);
  addLog(actionInput.value, 'action');

  const result = processAction(action);
  showFeedbackMessage(result);

  actionInput.value = '';

  setTimeout(() => {
    if (currentProblem.value.winCondition(metrics)) {
      solved.value = true;
      showResult();
    } else if (attempts.value <= 0) {
      showResult();
    }
  }, 1500);
}

// 액션 처리
function processAction(action) {
  const solutions = currentProblem.value.solutions;
  let matched = false;
  let totalImprovement = 0;

  for (let solution of solutions) {
    const hasKeyword = solution.keywords.some(keyword => action.includes(keyword));
    if (hasKeyword) {
      matched = true;
      for (let [metric, change] of Object.entries(solution.effect)) {
        if (metrics[metric]) {
          metrics[metric].value = Math.max(0, Math.min(metrics[metric].max, metrics[metric].value + change));
          totalImprovement += Math.abs(change);
        }
      }
      break;
    }
  }

  if (!matched) {
    return { type: 'neutral', message: '명령이 효과가 없습니다...' };
  } else if (totalImprovement > 0) {
    return { type: 'improved', message: '상황이 개선되었습니다!' };
  } else {
    return { type: 'neutral', message: '명령을 실행했습니다.' };
  }
}

// 피드백 표시
function showFeedbackMessage(result) {
  feedbackMessage.value = result.message;
  feedbackType.value = result.type;
  showFeedback.value = true;

  setTimeout(() => {
    showFeedback.value = false;
  }, 2000);
}

// 로그 추가
const actionLog = ref(null);
function addLog(message, type) {
  actionLogs.value.push({ message, type });
  nextTick(() => {
    if (actionLog.value) {
      actionLog.value.scrollTop = actionLog.value.scrollHeight;
    }
  });
}

// 결과 화면 표시
const usedAttempts = computed(() => 7 - attempts.value);
const finalScore = computed(() => solved.value ? Math.max(100 - (usedAttempts.value * 10), 50) : 0);

const resultMessage = computed(() => {
  if (solved.value) {
    return `<span style="color: var(--success-green);">훌륭합니다! 시스템을 성공적으로 복구했습니다.</span><br>
            효율적인 문제 해결 능력을 보여주셨습니다.`;
  } else {
    return `<span style="color: var(--danger-red);">시도 횟수를 모두 소진했습니다.</span><br>
            다시 한번 도전해보세요. 힌트를 참고하면 도움이 될 것입니다.`;
  }
});

function showResult() {
  currentScreen.value = 'result';
}

// 게임 리셋
function resetGame() {
  currentScreen.value = 'difficulty';
  attempts.value = 7;
  solved.value = false;
  actionInput.value = '';
  actionLogs.value = [{ message: '시스템 준비 완료...', type: 'action' }];
  userActions.value = [];
  showAIFeedback.value = false;
  aiFeedbackLoading.value = false;
  aiFeedbackReceived.value = false;
  aiFeedbackError.value = false;
  aiFeedback.value = '';
}

// AI 피드백
async function getAIFeedback() {
  showAIFeedback.value = true;
  aiFeedbackLoading.value = true;
  aiFeedbackError.value = false;

  try {
    const actionsList = userActions.value.map((a, i) => `${i + 1}. ${a}`).join('\n');

    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
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
      aiFeedback.value = data.content[0].text;
      aiFeedbackReceived.value = true;
    } else {
      throw new Error('응답 형식 오류');
    }
  } catch (error) {
    console.error('AI 피드백 오류:', error);
    aiFeedbackError.value = true;
  } finally {
    aiFeedbackLoading.value = false;
  }
}
</script>

<style scoped>
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

.game-container {
  position: relative;
  z-index: 2;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Rajdhani', sans-serif;
  color: var(--neon-cyan);
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

/* 모니터 스타일 */
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
  margin-bottom: 30px;
}

.screen-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid var(--neon-cyan);
}

.screen-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.5em;
  font-weight: 700;
  color: var(--neon-cyan);
}

.terminal-indicator {
  color: var(--danger-red);
  font-family: 'JetBrains Mono', monospace;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.3; }
}

.problem-description {
  background: linear-gradient(135deg, rgba(255, 0, 85, 0.1), rgba(255, 149, 0, 0.1));
  border-left: 4px solid var(--danger-red);
  padding: 20px;
  border-radius: 10px;
}

.alert-badge {
  display: inline-block;
  background: var(--danger-red);
  color: #000;
  padding: 5px 15px;
  border-radius: 20px;
  font-weight: 700;
  margin-bottom: 15px;
  font-size: 0.9em;
}

.problem-description p {
  color: #fff;
  line-height: 1.8;
  font-size: 1.1em;
}

/* 메트릭 대시보드 */
.metrics-dashboard {
  background: var(--panel-bg);
  border: 2px solid var(--neon-cyan);
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 0 20px rgba(0, 243, 255, 0.2);
  margin-bottom: 30px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--neon-cyan);
  font-family: 'Orbitron', sans-serif;
  font-weight: 700;
}

.live-indicator {
  color: var(--success-green);
  font-size: 0.9em;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.metric-card {
  background: rgba(0, 0, 0, 0.5);
  border: 2px solid;
  border-radius: 10px;
  padding: 15px;
  transition: all 0.3s;
}

.metric-card.normal {
  border-color: var(--success-green);
}

.metric-card.warning {
  border-color: var(--warning-orange);
  box-shadow: 0 0 15px rgba(255, 149, 0, 0.3);
}

.metric-card.critical {
  border-color: var(--danger-red);
  box-shadow: 0 0 20px rgba(255, 0, 85, 0.5);
  animation: shake 0.5s infinite;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-2px); }
  75% { transform: translateX(2px); }
}

.metric-label {
  font-size: 0.9em;
  opacity: 0.8;
  margin-bottom: 5px;
}

.metric-value {
  font-size: 2em;
  font-weight: 700;
  font-family: 'Orbitron', sans-serif;
  margin-bottom: 10px;
}

.metric-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 5px;
}

.metric-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--success-green), var(--warning-orange), var(--danger-red));
  transition: width 0.5s ease;
}

.metric-threshold {
  font-size: 0.8em;
  opacity: 0.6;
}

/* 액션 패널 */
.action-panel {
  background: var(--panel-bg);
  border: 2px solid var(--neon-magenta);
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 0 20px rgba(255, 0, 255, 0.2);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--neon-cyan);
  font-family: 'Orbitron', sans-serif;
  font-weight: 700;
}

.attempts-counter {
  color: var(--neon-yellow);
  font-size: 1.1em;
}

.input-group {
  display: flex;
  gap: 10px;
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
  outline: none;
  transition: all 0.3s;
}

.action-input:focus {
  box-shadow: 0 0 15px var(--screen-glow);
  border-color: var(--neon-magenta);
}

.action-input::placeholder {
  color: rgba(0, 243, 255, 0.4);
}

.submit-btn {
  background: var(--neon-magenta);
  color: #000;
  border: none;
  padding: 15px 30px;
  border-radius: 8px;
  font-family: 'Orbitron', sans-serif;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 1em;
}

.submit-btn:hover:not(:disabled) {
  background: var(--neon-cyan);
  box-shadow: 0 0 20px var(--screen-glow);
  transform: scale(1.05);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.feedback-message {
  margin-top: 15px;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  font-weight: 600;
  opacity: 0;
  transform: translateY(-10px);
  transition: all 0.3s;
}

.feedback-message.show {
  opacity: 1;
  transform: translateY(0);
}

.feedback-message.improved {
  background: rgba(0, 255, 136, 0.2);
  border: 2px solid var(--success-green);
  color: var(--success-green);
}

.feedback-message.worsened {
  background: rgba(255, 0, 85, 0.2);
  border: 2px solid var(--danger-red);
  color: var(--danger-red);
}

.feedback-message.neutral {
  background: rgba(255, 149, 0, 0.2);
  border: 2px solid var(--warning-orange);
  color: var(--warning-orange);
}

/* 힌트 패널 */
.hint-panel {
  background: var(--panel-bg);
  border: 2px solid var(--neon-yellow);
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 0 20px rgba(255, 255, 0, 0.2);
  margin-bottom: 20px;
}

.hint-content {
  max-height: 300px;
  overflow-y: auto;
}

.hint-item {
  display: flex;
  gap: 15px;
  padding: 12px;
  margin-bottom: 10px;
  background: rgba(255, 255, 0, 0.1);
  border-radius: 8px;
  align-items: flex-start;
}

.hint-number {
  flex-shrink: 0;
  width: 25px;
  height: 25px;
  background: var(--neon-yellow);
  color: #000;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9em;
}

/* 로그 패널 */
.log-panel {
  background: var(--panel-bg);
  border: 2px solid var(--success-green);
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 0 20px rgba(0, 255, 136, 0.2);
}

.action-log {
  background: #000;
  padding: 15px;
  border-radius: 8px;
  max-height: 300px;
  overflow-y: auto;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9em;
}

.log-entry {
  padding: 8px;
  margin-bottom: 5px;
  border-left: 3px solid;
  padding-left: 12px;
}

.log-entry.action {
  border-color: var(--neon-cyan);
  color: var(--neon-cyan);
}

.log-entry.system {
  border-color: var(--success-green);
  color: var(--success-green);
}

/* 결과 화면 */
.result-screen {
  animation: fadeIn 0.5s;
}

.result-container {
  background: var(--panel-bg);
  border: 3px solid var(--neon-cyan);
  border-radius: 20px;
  padding: 60px;
  box-shadow: 0 0 40px var(--screen-glow), inset 0 0 20px rgba(0, 243, 255, 0.1);
  text-align: center;
}

.result-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 3em;
  margin-bottom: 30px;
  text-shadow: 0 0 30px currentColor;
}

.result-title.success {
  color: var(--success-green);
}

.result-title.failure {
  color: var(--danger-red);
}

.result-message {
  font-size: 1.3em;
  line-height: 1.8;
  margin-bottom: 40px;
  color: #fff;
}

.result-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.stat-item {
  background: rgba(0, 0, 0, 0.5);
  border: 2px solid var(--neon-cyan);
  border-radius: 15px;
  padding: 20px 30px;
  min-width: 150px;
}

.stat-label {
  font-size: 0.9em;
  opacity: 0.8;
  margin-bottom: 10px;
}

.stat-value {
  font-family: 'Orbitron', sans-serif;
  font-size: 2em;
  font-weight: 700;
  color: var(--neon-yellow);
}

.stat-value.score {
  color: var(--neon-magenta);
  font-size: 2.5em;
}

.result-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.ai-feedback-btn,
.retry-btn {
  font-family: 'Orbitron', sans-serif;
  padding: 15px 40px;
  font-size: 1.2em;
  border: 3px solid;
  cursor: pointer;
  border-radius: 10px;
  font-weight: 700;
  transition: all 0.3s;
}

.ai-feedback-btn {
  background: transparent;
  border-color: var(--neon-magenta);
  color: var(--neon-magenta);
}

.ai-feedback-btn:hover:not(:disabled) {
  background: var(--neon-magenta);
  color: #000;
  box-shadow: 0 0 20px var(--neon-magenta);
}

.ai-feedback-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.retry-btn {
  background: var(--neon-cyan);
  border-color: var(--neon-cyan);
  color: #000;
}

.retry-btn:hover {
  box-shadow: 0 0 20px var(--screen-glow);
  transform: scale(1.05);
}

/* AI 피드백 섹션 */
.ai-feedback-section {
  background: rgba(0, 0, 0, 0.5);
  border: 2px solid var(--neon-magenta);
  border-radius: 15px;
  padding: 20px;
  margin-top: 30px;
  text-align: left;
}

.feedback-header {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.3em;
  font-weight: 700;
  color: var(--neon-magenta);
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--neon-magenta);
}

.ai-feedback-content {
  color: #fff;
  line-height: 1.8;
  font-size: 1.1em;
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

  .difficulty-buttons {
    flex-direction: column;
  }

  .metrics-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
}
</style>
