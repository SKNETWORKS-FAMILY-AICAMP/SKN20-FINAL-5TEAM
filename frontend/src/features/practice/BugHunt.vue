<template>
  <div class="debug-practice-page">
    <!-- 레벨업 이펙트 -->
    <transition name="levelup">
      <div v-if="showLevelUp" class="levelup-overlay">
        <div class="levelup-content">
          <div class="levelup-badge">🎖️</div>
          <div class="levelup-text">LEVEL UP!</div>
          <div class="levelup-level">{{ levelUpInfo.oldLevel }} → {{ levelUpInfo.newLevel }}</div>
          <div class="levelup-title">{{ levelUpInfo.title }}</div>
        </div>
      </div>
    </transition>

    <!-- 도전과제 달성 팝업 -->
    <transition name="achievement">
      <div v-if="showAchievementPopup && newAchievement" class="achievement-popup">
        <div class="achievement-icon">{{ newAchievement.icon }}</div>
        <div class="achievement-info">
          <div class="achievement-label">ACHIEVEMENT UNLOCKED!</div>
          <div class="achievement-name">{{ newAchievement.name }}</div>
          <div class="achievement-desc">{{ newAchievement.desc }}</div>
        </div>
      </div>
    </transition>

    <!-- 모드 선택 화면 -->
    <div v-if="currentView === 'menu'" class="menu-container">
      <header class="header">
        <h1>DEBUG GYM</h1>
        <div class="subtitle">// PYTHON BUG HUNTING TRAINING SYSTEM v3.0</div>

        <!-- 플레이어 스탯 바 -->
        <div class="player-stats-bar">
          <div class="stat-item level-stat">
            <span class="stat-icon">🎖️</span>
            <span class="stat-label">Lv.{{ gameData.level }}</span>
            <span class="stat-title">{{ currentLevelInfo.title }}</span>
          </div>
          <div class="stat-item xp-stat">
            <div class="xp-bar-container">
              <div class="xp-bar-fill" :style="{ width: currentLevelInfo.progress + '%' }"></div>
              <span class="xp-text">{{ gameData.xp }} XP</span>
            </div>
          </div>
          <div class="stat-item score-stat">
            <span class="stat-icon">🏆</span>
            <span class="stat-value">{{ gameData.totalScore }}</span>
          </div>
          <button class="stats-btn" @click="showStatsPanel = true">📊 STATS</button>
        </div>
      </header>

      <!-- 미션 선택 그리드 (순차 해금) -->
      <div class="mission-selection">
        <h2 class="section-title">🎯 PROGRESSIVE MISSIONS</h2>
        <div class="mission-grid">
          <div
            v-for="(mission, index) in progressiveProblems"
            :key="mission.id"
            class="mission-card"
            :class="{
              completed: isMissionCompleted(mission.id),
              locked: !isMissionUnlocked(index),
              current: isMissionUnlocked(index) && !isMissionCompleted(mission.id)
            }"
            @click="startProgressiveMission(mission, index)"
          >
            <div class="mission-lock" v-if="!isMissionUnlocked(index)">
              <span class="lock-icon">🔒</span>
              <span class="lock-text">Mission {{ index }} 완료 필요</span>
            </div>
            <div class="mission-content" :class="{ blurred: !isMissionUnlocked(index) }">
              <div class="mission-header">
                <span class="mission-id">{{ mission.id }}</span>
                <span class="difficulty">
                  <span v-for="n in 3" :key="n" :class="{ active: n <= mission.difficulty }">★</span>
                </span>
              </div>
              <h3>{{ mission.project_title }}</h3>
              <p class="mission-scenario">{{ mission.scenario.substring(0, 80) }}...</p>
              <div class="step-progress">
                <div
                  v-for="step in mission.steps"
                  :key="step.step"
                  class="step-dot"
                  :class="{
                    completed: isStepCompleted(mission.id, step.step),
                    current: getCurrentStep(mission.id) === step.step
                  }"
                >
                  <span class="step-type">{{ step.bug_type }}</span>
                </div>
              </div>
              <div v-if="isMissionCompleted(mission.id)" class="completed-badge">✓ ALL CLEAR</div>
              <button
                v-if="isMissionCompleted(mission.id)"
                class="replay-btn"
                @click.stop="replayMission(mission)"
              >
                🔄 다시 풀기
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 도전과제 섹션 -->
      <div class="achievements-section">
        <h2>🏅 ACHIEVEMENTS ({{ unlockedAchievements.length }}/{{ allAchievements.length }})</h2>
        <div class="achievements-grid">
          <div
            v-for="achievement in allAchievements"
            :key="achievement.id"
            class="achievement-card"
            :class="{ unlocked: gameData.achievements.includes(achievement.id) }"
          >
            <span class="achievement-icon">{{ achievement.icon }}</span>
            <span class="achievement-name">{{ achievement.name }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 스탯 패널 -->
    <transition name="fade">
      <div v-if="showStatsPanel" class="stats-overlay" @click.self="showStatsPanel = false">
        <div class="stats-panel">
          <div class="stats-header">
            <h2>📊 YOUR STATS</h2>
            <button class="close-btn" @click="showStatsPanel = false">×</button>
          </div>
          <div class="stats-content">
            <div class="stat-row">
              <span class="stat-label">🎖️ Level</span>
              <span class="stat-value">{{ gameData.level }} ({{ currentLevelInfo.title }})</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">✨ Total XP</span>
              <span class="stat-value">{{ gameData.xp }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">🏆 Total Score</span>
              <span class="stat-value">{{ gameData.totalScore }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">🐛 Bugs Fixed</span>
              <span class="stat-value">{{ gameData.stats.totalBugsFixed }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">🔥 Max Combo</span>
              <span class="stat-value">{{ gameData.maxCombo }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">🏅 Achievements</span>
              <span class="stat-value">{{ unlockedAchievements.length }}/{{ allAchievements.length }}</span>
            </div>
          </div>
          <button class="reset-stats-btn" @click="resetGameData">🔄 Reset All Progress</button>
        </div>
      </div>
    </transition>

    <!-- Progressive Mission 연습 화면 -->
    <div v-if="currentView === 'progressivePractice'" class="progressive-practice-container">
      <!-- 단계 완료 이펙트 -->
      <transition name="stepComplete">
        <div v-if="showStepComplete" class="step-complete-overlay">
          <div class="step-complete-content">
            <div class="complete-icon">💀</div>
            <div class="complete-text">BUG {{ justCompletedStep }} ELIMINATED!</div>
            <div class="bug-killed">
              <span class="dead-bug">{{ getBugEmoji(getStepData(justCompletedStep)?.bug_type) }}</span>
              <span class="kill-text">☠️ SQUASHED!</span>
            </div>
            <div class="coaching-box">
              <div class="coaching-title">💡 시니어 개발자 조언</div>
              <p class="coaching-text">{{ getStepData(justCompletedStep)?.coaching }}</p>
            </div>
          </div>
        </div>
      </transition>

      <!-- 미션 완료 이펙트 -->
      <transition name="missionComplete">
        <div v-if="showMissionComplete" class="mission-complete-overlay">
          <div class="mission-complete-content">
            <div class="complete-fireworks">🎆</div>
            <div class="complete-title">MISSION COMPLETE!</div>
            <div class="complete-project">{{ currentProgressiveMission?.project_title }}</div>
            <div class="all-bugs-dead">
              <span class="dead-bug-row">
                <span class="dead-bug">☠️</span>
                <span class="dead-bug">☠️</span>
                <span class="dead-bug">☠️</span>
              </span>
              <span class="all-dead-text">ALL BUGS EXTERMINATED!</span>
            </div>
            <div class="mission-rewards">
              <div class="reward-item">
                <span class="reward-icon">✨</span>
                <span class="reward-value">+{{ progressiveMissionXP }} XP</span>
              </div>
              <div class="reward-item">
                <span class="reward-icon">🏆</span>
                <span class="reward-value">+{{ progressiveMissionScore }} Points</span>
              </div>
            </div>
            <button class="continue-btn" @click="finishProgressiveMission">CONTINUE</button>
          </div>
        </div>
      </transition>

      <!-- 헤더 -->
      <header class="header compact progressive-header">
        <div class="header-left">
          <h1>🎯 {{ currentProgressiveMission?.project_title }}</h1>
        </div>
        <div class="header-center">
          <!-- 버그 상태 표시 (3마리) -->
          <div class="bugs-status">
            <div
              v-for="step in 3"
              :key="step"
              class="bug-status-item"
              :class="{ dead: progressiveCompletedSteps.includes(step), active: step === currentProgressiveStep }"
            >
              <span class="bug-icon">{{ progressiveCompletedSteps.includes(step) ? '☠️' : getBugEmoji(getStepData(step)?.bug_type) }}</span>
              <span class="bug-label">{{ getStepData(step)?.bug_type }}</span>
            </div>
          </div>
        </div>
        <div class="header-right">
          <div class="remaining-bugs">
            🐛 {{ 3 - progressiveCompletedSteps.length }} bugs left
          </div>
          <button class="back-btn" @click="confirmExit">EXIT</button>
        </div>
      </header>

      <div class="progressive-main-layout">
        <!-- 좌측: 미션 브리핑 -->
        <aside class="mission-briefing-panel">
          <div class="panel-box scenario-box">
            <div class="panel-title">📋 MISSION BRIEFING</div>
            <p class="scenario-text">{{ currentProgressiveMission?.scenario }}</p>
          </div>

          <div class="panel-box current-target-box" v-if="currentProgressiveStep <= 3">
            <div class="panel-title">🎯 TARGET: STEP {{ currentProgressiveStep }}</div>
            <div class="target-content">
              <div class="target-bug">
                <span class="target-bug-emoji">{{ getBugEmoji(getCurrentStepData()?.bug_type) }}</span>
                <span class="target-bug-name">{{ getCurrentStepData()?.bug_type_name }}</span>
              </div>
              <p class="target-instruction">{{ getCurrentStepData()?.instruction }}</p>
            </div>
          </div>

          <div class="side-controls">
            <button class="action-btn hint-btn" @click="showProgressiveHint" :disabled="progressiveHintUsed[currentProgressiveStep]">
              <span class="btn-icon">💡</span>
              {{ progressiveHintUsed[currentProgressiveStep] ? 'HINT USED' : 'HINT' }}
            </button>
            <button class="action-btn submit-btn" @click="submitProgressiveStep" :disabled="currentProgressiveStep > 3">
              <span class="btn-icon">🚀</span>
              {{ currentProgressiveStep > 3 ? 'DONE!' : 'SUBMIT' }}
            </button>
            <button class="action-btn reset-btn" @click="resetCurrentStep">
              <span class="btn-icon">↺</span>
              RESET
            </button>
          </div>
        </aside>

        <!-- 중앙: 전체 코드 에디터 (3단계 모두 표시) -->
        <main class="full-code-editor" ref="editorFrameRef">
          <!-- 3마리 벌레 애니메이션 -->
          <div class="bugs-container">
            <div
              v-for="step in 3"
              :key="'bug-' + step"
              class="code-bug"
              :class="{
                dead: progressiveCompletedSteps.includes(step),
                eating: !progressiveCompletedSteps.includes(step),
                targeted: step === currentProgressiveStep && isRunning
              }"
              :style="bugPositions[step]"
            >
              <span class="bug-emoji">{{ progressiveCompletedSteps.includes(step) ? '💀' : getBugEmoji(getStepData(step)?.bug_type) }}</span>
              <div class="eating-effect" v-if="!progressiveCompletedSteps.includes(step)">
                <span v-for="n in 3" :key="n" class="bite-mark">×</span>
              </div>
            </div>
          </div>

          <!-- 저격 이펙트 -->
          <div v-if="showBullet" class="bullet" :style="bulletStyle">
            <span class="bullet-trail">💥</span>
          </div>

          <transition name="explode">
            <div v-if="showHitEffect" class="hit-effect" :style="hitEffectStyle">
              <span class="hit-text">{{ hitEffectText }}</span>
              <div class="explosion-particles">
                <span v-for="n in 8" :key="n" class="particle" :style="`--angle: ${n * 45}deg`"></span>
              </div>
            </div>
          </transition>

          <!-- MISS 이펙트 -->
          <transition name="miss">
            <div v-if="showMissEffect" class="miss-effect" :style="missEffectStyle">
              <span class="miss-text">MISS!</span>
            </div>
          </transition>

          <div class="editor-header">
            <div class="code-progress">
              <span class="progress-text">{{ progressiveCompletedSteps.length }}/3 BUGS FIXED</span>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: (progressiveCompletedSteps.length / 3 * 100) + '%' }"></div>
              </div>
            </div>
          </div>

          <div class="editor-body">
            <!-- 전체 코드를 3개 섹션으로 표시 -->
            <div class="code-sections">
              <div
                v-for="step in 3"
                :key="'section-' + step"
                class="code-section"
                :class="{
                  locked: step > currentProgressiveStep && !progressiveCompletedSteps.includes(step),
                  active: step === currentProgressiveStep,
                  completed: progressiveCompletedSteps.includes(step)
                }"
              >
                <div class="section-header">
                  <span class="section-label">
                    <span class="step-num">{{ step }}</span>
                    {{ getStepData(step)?.title }}
                  </span>
                  <span class="section-status">
                    <span v-if="progressiveCompletedSteps.includes(step)" class="status-fixed">✅ FIXED</span>
                    <span v-else-if="step === currentProgressiveStep" class="status-current">🔧 CURRENT</span>
                    <span v-else class="status-locked">🔒 LOCKED</span>
                  </span>
                </div>

                <!-- 잠긴 섹션 -->
                <div v-if="step > currentProgressiveStep && !progressiveCompletedSteps.includes(step)" class="locked-overlay">
                  <div class="lock-content">
                    <span class="lock-icon">🔒</span>
                    <span class="lock-text">Step {{ step - 1 }} 완료 필요</span>
                  </div>
                  <pre class="blurred-code">{{ getStepData(step)?.buggy_code }}</pre>
                </div>

                <!-- 편집 가능한 섹션 (현재 스텝) -->
                <div v-else-if="step === currentProgressiveStep" class="code-editor-wrapper">
                  <div class="line-numbers">
                    <div v-for="n in getLineCount(progressiveStepCodes[step])" :key="n" class="line-num">{{ n }}</div>
                  </div>
                  <textarea
                    class="section-code editable game-code"
                    v-model="progressiveStepCodes[step]"
                    @input="onProgressiveCodeChange"
                    spellcheck="false"
                    wrap="off"
                  ></textarea>
                </div>

                <!-- 완료된 섹션 -->
                <div v-else class="code-editor-wrapper completed-wrapper">
                  <div class="line-numbers">
                    <div v-for="n in getLineCount(progressiveStepCodes[step])" :key="n" class="line-num">{{ n }}</div>
                  </div>
                  <pre class="section-code readonly game-code">{{ progressiveStepCodes[step] }}</pre>
                </div>
              </div>
            </div>
          </div>

          <div class="terminal-section">
            <div class="terminal-header">
              <span>DIAGNOSTIC TERMINAL</span>
              <span class="terminal-status" :class="terminalStatus">{{ terminalStatus.toUpperCase() }}</span>
            </div>
            <div class="terminal-body">
              <div v-for="(line, idx) in terminalOutput" :key="idx" class="terminal-line" :class="line.type">
                <span class="prompt">{{ line.prompt }}</span>
                <span class="text">{{ line.text }}</span>
              </div>
            </div>
          </div>
        </main>
      </div>

      <!-- Progressive 힌트 패널 -->
      <transition name="slide-down">
        <div v-if="showProgressiveHintPanel" class="hint-overlay">
          <div class="hint-panel">
            <div class="hint-header">
              <span class="hint-icon">💡</span>
              <span>STEP {{ currentProgressiveStep }} HINT</span>
              <button class="close-btn" @click="showProgressiveHintPanel = false">×</button>
            </div>
            <div class="hint-content">
              {{ getCurrentStepData()?.hint }}
            </div>
          </div>
        </div>
      </transition>
    </div>

    <!-- 종료 확인 모달 -->
    <transition name="fade">
      <div v-if="showExitConfirm" class="confirm-overlay">
        <div class="confirm-modal">
          <h3>⚠️ EXIT PRACTICE?</h3>
          <p>진행 중인 문제를 종료하시겠습니까?</p>
          <div class="confirm-actions">
            <button class="confirm-btn cancel" @click="showExitConfirm = false">CANCEL</button>
            <button class="confirm-btn exit" @click="exitPractice">EXIT</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue';
import progressiveData from './progressive-problems.json';

// ============================================
// 게임 상태 저장/로드 (LocalStorage)
// ============================================
const STORAGE_KEY = 'bugHuntGameData';

function loadGameData() {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : null;
  } catch {
    return null;
  }
}

function saveGameData(data) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch (e) {
    console.warn('Failed to save game data:', e);
  }
}

// 초기 게임 데이터
const defaultGameData = {
  level: 1,
  xp: 0,
  totalScore: 0,
  combo: 0,
  maxCombo: 0,
  completedProblems: [],
  achievements: [],
  stats: {
    totalBugsFixed: 0,
    perfectClears: 0,
    hintsUsed: 0
  }
};

// 게임 데이터 로드 또는 초기화
const savedData = loadGameData();
const gameData = reactive(savedData || { ...defaultGameData });

// 게임 데이터 변경 시 자동 저장
watch(gameData, (newData) => {
  saveGameData(newData);
}, { deep: true });

// ============================================
// 레벨 시스템
// ============================================
const levelTitles = [
  { level: 1, title: 'Bug Rookie', xpRequired: 0 },
  { level: 2, title: 'Bug Spotter', xpRequired: 100 },
  { level: 3, title: 'Bug Tracker', xpRequired: 250 },
  { level: 4, title: 'Bug Hunter', xpRequired: 500 },
  { level: 5, title: 'Bug Slayer', xpRequired: 800 },
  { level: 6, title: 'Bug Terminator', xpRequired: 1200 },
  { level: 7, title: 'Bug Master', xpRequired: 1800 },
  { level: 8, title: 'Debug Legend', xpRequired: 2500 },
  { level: 9, title: 'Code Guardian', xpRequired: 3500 },
  { level: 10, title: 'Supreme Debugger', xpRequired: 5000 }
];

const currentLevelInfo = computed(() => {
  const levelInfo = levelTitles.find(l => l.level === gameData.level) || levelTitles[0];
  const nextLevel = levelTitles.find(l => l.level === gameData.level + 1);
  const xpForNext = nextLevel ? nextLevel.xpRequired - levelInfo.xpRequired : 0;
  const currentLevelXp = gameData.xp - levelInfo.xpRequired;
  const progress = xpForNext > 0 ? (currentLevelXp / xpForNext) * 100 : 100;

  return {
    ...levelInfo,
    nextLevelXp: nextLevel?.xpRequired || levelInfo.xpRequired,
    progress: Math.min(100, Math.max(0, progress)),
    xpToNext: xpForNext - currentLevelXp
  };
});

function addXP(amount) {
  gameData.xp += amount;
  for (let i = levelTitles.length - 1; i >= 0; i--) {
    if (gameData.xp >= levelTitles[i].xpRequired && gameData.level < levelTitles[i].level) {
      const oldLevel = gameData.level;
      gameData.level = levelTitles[i].level;
      showLevelUpEffect(oldLevel, gameData.level, levelTitles[i].title);
      break;
    }
  }
}

// ============================================
// 도전 과제 시스템
// ============================================
const allAchievements = [
  { id: 'first_blood', name: 'First Blood', desc: '첫 번째 버그를 잡았습니다', icon: '🎯', condition: () => gameData.stats.totalBugsFixed >= 1 },
  { id: 'bug_hunter', name: 'Bug Hunter', desc: '10개의 버그를 잡았습니다', icon: '🐛', condition: () => gameData.stats.totalBugsFixed >= 10 },
  { id: 'perfectionist', name: 'Perfectionist', desc: '힌트 없이 문제를 해결했습니다', icon: '💎', condition: () => gameData.stats.perfectClears >= 1 },
  { id: 'combo_starter', name: 'Combo Starter', desc: '3연속 콤보를 달성했습니다', icon: '🔥', condition: () => gameData.maxCombo >= 3 },
  { id: 'combo_master', name: 'Combo Master', desc: '5연속 콤보를 달성했습니다', icon: '💥', condition: () => gameData.maxCombo >= 5 },
  { id: 'level_5', name: 'Rising Star', desc: '레벨 5에 도달했습니다', icon: '⭐', condition: () => gameData.level >= 5 },
  { id: 'mission_master', name: 'Mission Master', desc: '모든 미션을 완료했습니다', icon: '👑', condition: () => getProgressiveMissionsCompleted() >= progressiveProblems.length }
];

const unlockedAchievements = computed(() => {
  return allAchievements.filter(a => gameData.achievements.includes(a.id));
});

function checkAchievements() {
  for (const achievement of allAchievements) {
    if (!gameData.achievements.includes(achievement.id) && achievement.condition()) {
      gameData.achievements.push(achievement.id);
      showAchievementUnlock(achievement);
    }
  }
}

// UI 상태
const showLevelUp = ref(false);
const levelUpInfo = ref({ oldLevel: 0, newLevel: 0, title: '' });
const showAchievementPopup = ref(false);
const newAchievement = ref(null);
const showStatsPanel = ref(false);

function showLevelUpEffect(oldLevel, newLevel, title) {
  levelUpInfo.value = { oldLevel, newLevel, title };
  showLevelUp.value = true;
  setTimeout(() => { showLevelUp.value = false; }, 3000);
}

function showAchievementUnlock(achievement) {
  newAchievement.value = achievement;
  showAchievementPopup.value = true;
  setTimeout(() => { showAchievementPopup.value = false; }, 3000);
}

// ============================================
// Progressive Mission 시스템
// ============================================
const progressiveProblems = progressiveData.progressiveProblems;
const currentProgressiveMission = ref(null);
const currentProgressiveStep = ref(1);
const progressiveCompletedSteps = ref([]);
const progressiveStepCodes = ref({ 1: '', 2: '', 3: '' });
const progressiveHintUsed = ref({ 1: false, 2: false, 3: false });
const showProgressiveHintPanel = ref(false);
const justCompletedStep = ref(0);

// Progressive UI 이펙트
const showStepComplete = ref(false);
const showMissionComplete = ref(false);
const progressiveMissionXP = ref(0);
const progressiveMissionScore = ref(0);

// 미션 해금 여부 (순차적)
function isMissionUnlocked(index) {
  if (index === 0) return true;
  return isMissionCompleted(progressiveProblems[index - 1].id);
}

// 미션 완료 여부 확인
function isMissionCompleted(missionId) {
  return gameData.completedProblems.includes(`progressive_${missionId}`);
}

// 스텝 완료 여부 확인
function isStepCompleted(missionId, step) {
  return gameData.completedProblems.includes(`progressive_${missionId}_step${step}`);
}

// 현재 진행 중인 스텝 가져오기
function getCurrentStep(missionId) {
  for (let i = 1; i <= 3; i++) {
    if (!isStepCompleted(missionId, i)) return i;
  }
  return 3;
}

// 완료된 Progressive 미션 수
function getProgressiveMissionsCompleted() {
  return progressiveProblems.filter(m => isMissionCompleted(m.id)).length;
}

// 스텝 데이터 가져오기
function getStepData(stepNum) {
  if (!currentProgressiveMission.value) return null;
  return currentProgressiveMission.value.steps.find(s => s.step === stepNum);
}

// 현재 스텝 데이터 가져오기
function getCurrentStepData() {
  return getStepData(currentProgressiveStep.value);
}

// 버그 타입별 이모지
function getBugEmoji(bugType) {
  const emojis = { 'A': '🐛', 'B': '🐝', 'C': '🦗' };
  return emojis[bugType] || '🐛';
}

// 라인 수 계산
function getLineCount(code) {
  return (code || '').split('\n').length;
}

// Progressive Mission 시작
function startProgressiveMission(mission, index) {
  if (!isMissionUnlocked(index)) return;

  currentProgressiveMission.value = mission;
  currentProgressiveStep.value = 1;
  progressiveCompletedSteps.value = [];
  progressiveHintUsed.value = { 1: false, 2: false, 3: false };

  // 모든 스텝의 버그 코드 로드
  progressiveStepCodes.value = {
    1: mission.steps[0].buggy_code,
    2: mission.steps[1].buggy_code,
    3: mission.steps[2].buggy_code
  };

  currentView.value = 'progressivePractice';

  // 버그 애니메이션 시작
  setTimeout(() => {
    startBugAnimations();
  }, 500);

  // 터미널 초기화
  terminalOutput.value = [
    { prompt: '>', text: `Mission loaded: ${mission.project_title}`, type: 'info' },
    { prompt: '>', text: `3 bugs detected! Hunt them down!`, type: 'warning' },
    { prompt: '>', text: 'Fix Step 1 to unlock Step 2!', type: 'success' }
  ];
  terminalStatus.value = 'ready';
}

// 다시 풀기
function replayMission(mission) {
  // 해당 미션의 진행도 초기화
  gameData.completedProblems = gameData.completedProblems.filter(
    id => !id.startsWith(`progressive_${mission.id}`)
  );

  const index = progressiveProblems.findIndex(m => m.id === mission.id);
  startProgressiveMission(mission, index);
}

// Progressive 코드 변경 감지
function onProgressiveCodeChange() {
  // 코드 변경 감지
}

// 현재 스텝 리셋
function resetCurrentStep() {
  const stepData = getCurrentStepData();
  if (stepData) {
    progressiveStepCodes.value[currentProgressiveStep.value] = stepData.buggy_code;
    terminalOutput.value.push({
      prompt: '>',
      text: `Step ${currentProgressiveStep.value} code reset.`,
      type: 'info'
    });
  }
}

// Progressive 힌트 보기
function showProgressiveHint() {
  if (!progressiveHintUsed.value[currentProgressiveStep.value]) {
    progressiveHintUsed.value[currentProgressiveStep.value] = true;
    showProgressiveHintPanel.value = true;
    terminalOutput.value.push({
      prompt: '!',
      text: 'Hint accessed.',
      type: 'warning'
    });
  }
}

// Progressive 솔루션 체크
function checkProgressiveSolution() {
  const stepData = getCurrentStepData();
  if (!stepData) return false;

  const check = stepData.solution_check;
  const code = progressiveStepCodes.value[currentProgressiveStep.value];

  switch (check.type) {
    case 'contains':
      return code.includes(check.value);
    case 'notContains':
      return !code.includes(check.value);
    default:
      return code.includes(check.value);
  }
}

// Progressive 스텝 제출
function submitProgressiveStep() {
  if (currentProgressiveStep.value > 3) return;

  isRunning.value = true;
  terminalOutput.value.push({
    prompt: '$',
    text: 'Running tests...',
    type: 'command'
  });

  setTimeout(() => {
    const passed = checkProgressiveSolution();

    // 저격 애니메이션
    shootBug(currentProgressiveStep.value, passed);

    setTimeout(() => {
      if (passed) {
        // 성공!
        justCompletedStep.value = currentProgressiveStep.value;
        progressiveCompletedSteps.value.push(currentProgressiveStep.value);

        const stepId = `progressive_${currentProgressiveMission.value.id}_step${currentProgressiveStep.value}`;
        if (!gameData.completedProblems.includes(stepId)) {
          gameData.completedProblems.push(stepId);
        }

        gameData.stats.totalBugsFixed++;
        if (!progressiveHintUsed.value[currentProgressiveStep.value]) {
          gameData.stats.perfectClears++;
        }

        terminalStatus.value = 'success';
        terminalOutput.value.push({
          prompt: '✓',
          text: `Bug ${currentProgressiveStep.value} eliminated!`,
          type: 'success'
        });

        // 스텝 완료 이펙트
        showStepComplete.value = true;

        setTimeout(() => {
          showStepComplete.value = false;

          if (currentProgressiveStep.value < 3) {
            // 다음 스텝으로
            currentProgressiveStep.value++;
            terminalOutput.value.push({
              prompt: '🔓',
              text: `Step ${currentProgressiveStep.value} unlocked!`,
              type: 'success'
            });
          } else {
            // 미션 완료!
            completeMission();
          }
        }, 2500);
      } else {
        // 실패
        terminalStatus.value = 'error';
        terminalOutput.value.push({
          prompt: '✗',
          text: 'MISS! Bug still alive. Try again!',
          type: 'error'
        });
      }
      isRunning.value = false;
    }, 500);
  }, 800);
}

// 미션 완료 처리
function completeMission() {
  const missionId = `progressive_${currentProgressiveMission.value.id}`;
  if (!gameData.completedProblems.includes(missionId)) {
    gameData.completedProblems.push(missionId);
  }

  // 보상 계산
  progressiveMissionXP.value = 100;
  progressiveMissionScore.value = 500;

  addXP(progressiveMissionXP.value);
  gameData.totalScore += progressiveMissionScore.value;

  showMissionComplete.value = true;
  checkAchievements();
}

// Progressive 미션 종료
function finishProgressiveMission() {
  showMissionComplete.value = false;
  stopBugAnimations();
  currentView.value = 'menu';
}

// 에디터 프레임 참조
const editorFrameRef = ref(null);

// 버그 위치 상태
const bugPositions = reactive({
  1: { x: 0.6, y: 0.15 },
  2: { x: 0.7, y: 0.45 },
  3: { x: 0.65, y: 0.75 }
});

// 버그 애니메이션 ID
let bugAnimationIds = { 1: null, 2: null, 3: null };

// 버그 상태
const isRunning = ref(false);

// 총알/이펙트 상태
const showBullet = ref(false);
const bulletPosition = ref({ x: 0, y: 0 });
const showHitEffect = ref(false);
const showMissEffect = ref(false);
const hitEffectPosition = ref({ x: 0, y: 0 });
const missEffectPosition = ref({ x: 0, y: 0 });
const hitEffectText = ref('SQUASH!');

const bulletStyle = computed(() => ({
  left: `${bulletPosition.value.x}px`,
  top: `${bulletPosition.value.y}px`
}));

const hitEffectStyle = computed(() => ({
  left: `${hitEffectPosition.value.x}px`,
  top: `${hitEffectPosition.value.y}px`
}));

const missEffectStyle = computed(() => ({
  left: `${missEffectPosition.value.x}px`,
  top: `${missEffectPosition.value.y}px`
}));

// 버그 움직임 애니메이션
function animateBug(step) {
  if (progressiveCompletedSteps.value.includes(step)) return;

  const basePositions = {
    1: { baseX: 60, baseY: 15 },
    2: { baseX: 70, baseY: 45 },
    3: { baseX: 65, baseY: 75 }
  };

  const { baseX, baseY } = basePositions[step];
  const time = Date.now() / 1000;
  const offsetX = Math.sin(time * 2 + step) * 5;
  const offsetY = Math.cos(time * 1.5 + step * 2) * 3;

  bugPositions[step] = {
    left: `${baseX + offsetX}%`,
    top: `${baseY + offsetY}%`
  };

  bugAnimationIds[step] = requestAnimationFrame(() => animateBug(step));
}

// 버그 애니메이션 시작
function startBugAnimations() {
  for (let step = 1; step <= 3; step++) {
    if (!progressiveCompletedSteps.value.includes(step)) {
      animateBug(step);
    }
  }
}

// 버그 애니메이션 중지
function stopBugAnimations() {
  for (let step = 1; step <= 3; step++) {
    if (bugAnimationIds[step]) {
      cancelAnimationFrame(bugAnimationIds[step]);
      bugAnimationIds[step] = null;
    }
  }
}

// 저격 애니메이션
function shootBug(targetStep, isHit) {
  if (!editorFrameRef.value) return;

  const frame = editorFrameRef.value;
  const rect = frame.getBoundingClientRect();

  const startX = 50;
  const startY = rect.height - 50;

  // 버그 위치 계산
  const bugLeft = parseFloat(bugPositions[targetStep].left);
  const bugTop = parseFloat(bugPositions[targetStep].top);
  const targetX = (bugLeft / 100) * window.innerWidth;
  const targetY = (bugTop / 100) * window.innerHeight;

  bulletPosition.value = { x: startX, y: startY };
  showBullet.value = true;

  const duration = 300;
  const startTime = performance.now();

  function animateBullet(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const easeProgress = 1 - Math.pow(1 - progress, 3);

    bulletPosition.value.x = startX + (targetX - startX) * easeProgress;
    bulletPosition.value.y = startY + (targetY - startY) * easeProgress;

    if (progress < 1) {
      requestAnimationFrame(animateBullet);
    } else {
      showBullet.value = false;

      if (isHit) {
        hitEffectPosition.value = { x: targetX, y: targetY };
        hitEffectText.value = ['SQUASH!', 'GOTCHA!', 'ELIMINATED!'][Math.floor(Math.random() * 3)];
        showHitEffect.value = true;

        // 해당 버그 애니메이션 중지
        if (bugAnimationIds[targetStep]) {
          cancelAnimationFrame(bugAnimationIds[targetStep]);
          bugAnimationIds[targetStep] = null;
        }

        setTimeout(() => { showHitEffect.value = false; }, 1500);
      } else {
        missEffectPosition.value = { x: targetX + 30, y: targetY - 20 };
        showMissEffect.value = true;
        setTimeout(() => { showMissEffect.value = false; }, 1000);
      }
    }
  }

  requestAnimationFrame(animateBullet);
}

// 상태 관리
const currentView = ref('menu');
const showExitConfirm = ref(false);

// 터미널 상태
const terminalOutput = ref([]);
const terminalStatus = ref('ready');

function confirmExit() {
  showExitConfirm.value = true;
}

function exitPractice() {
  showExitConfirm.value = false;
  stopBugAnimations();
  currentView.value = 'menu';
}

function resetGameData() {
  if (confirm('정말로 모든 진행 상황을 초기화하시겠습니까?')) {
    Object.assign(gameData, { ...defaultGameData });
    showStatsPanel.value = false;
  }
}

// 라이프사이클
onUnmounted(() => {
  stopBugAnimations();
});
</script>

<style scoped>
/* 기본 변수 */
.debug-practice-page {
  --neon-cyan: #00f3ff;
  --neon-magenta: #ff00ff;
  --neon-yellow: #ffff00;
  --neon-green: #00ff88;
  --neon-red: #ff3366;
  --bg-dark: #0a0e17;
  --bg-darker: #060810;
  --panel-bg: rgba(26, 31, 46, 0.95);
  --border-color: rgba(0, 243, 255, 0.3);

  background: var(--bg-dark);
  color: #e0e0e0;
  min-height: 100vh;
  font-family: 'Rajdhani', 'Noto Sans KR', sans-serif;
}

/* 헤더 */
.header {
  text-align: center;
  padding: 30px;
  border-bottom: 1px solid var(--border-color);
  background: linear-gradient(180deg, rgba(0, 243, 255, 0.1) 0%, transparent 100%);
}

.header h1 {
  font-family: 'Orbitron', 'Press Start 2P', monospace;
  font-size: 2.5rem;
  color: var(--neon-cyan);
  margin: 0;
  text-shadow: 0 0 20px rgba(0, 243, 255, 0.5);
  letter-spacing: 4px;
}

.header .subtitle {
  color: #718096;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;
  margin-top: 8px;
}

.header.compact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
}

.header-left, .header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-left h1 {
  font-size: 1.3rem;
}

.back-btn {
  background: transparent;
  border: 1px solid var(--neon-cyan);
  color: var(--neon-cyan);
  padding: 8px 16px;
  font-family: 'Orbitron', monospace;
  cursor: pointer;
  transition: all 0.3s;
}

.back-btn:hover {
  background: var(--neon-cyan);
  color: #000;
}

/* 플레이어 스탯 바 */
.player-stats-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 30px;
  margin-top: 20px;
  padding: 15px 30px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 50px;
  border: 1px solid var(--border-color);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-icon { font-size: 1.2rem; }
.stat-label {
  font-family: 'Orbitron', monospace;
  font-size: 0.9rem;
  color: var(--neon-cyan);
}

.stat-title {
  color: var(--neon-yellow);
  font-size: 0.85rem;
}

.stat-value {
  font-family: 'Orbitron', monospace;
  font-size: 1.1rem;
  color: var(--neon-green);
}

.xp-stat { min-width: 200px; }

.xp-bar-container {
  position: relative;
  height: 20px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 10px;
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.xp-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--neon-cyan), var(--neon-magenta));
  border-radius: 10px;
  transition: width 0.5s ease;
}

.xp-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-family: 'Orbitron', monospace;
  font-size: 0.7rem;
  color: #fff;
  text-shadow: 0 0 5px rgba(0, 0, 0, 0.8);
}

.stats-btn {
  background: transparent;
  border: 1px solid var(--neon-cyan);
  color: var(--neon-cyan);
  padding: 8px 15px;
  border-radius: 20px;
  font-family: 'Orbitron', monospace;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s;
}

.stats-btn:hover {
  background: var(--neon-cyan);
  color: #000;
}

/* 미션 선택 */
.menu-container {
  max-width: 1400px;
  margin: 0 auto;
}

.mission-selection {
  padding: 40px;
}

.section-title {
  font-family: 'Orbitron', monospace;
  font-size: 1.5rem;
  color: var(--neon-magenta);
  text-align: center;
  margin-bottom: 30px;
  text-shadow: 0 0 15px rgba(255, 0, 255, 0.5);
}

.mission-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
}

.mission-card {
  background: var(--panel-bg);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 25px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.mission-card:hover:not(.locked) {
  border-color: var(--neon-magenta);
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(255, 0, 255, 0.2);
}

.mission-card.locked {
  cursor: not-allowed;
  opacity: 0.7;
}

.mission-card.completed {
  border-color: var(--neon-green);
  background: rgba(0, 255, 136, 0.05);
}

.mission-card.current {
  border-color: var(--neon-magenta);
  animation: currentMissionPulse 2s ease-in-out infinite;
}

@keyframes currentMissionPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255, 0, 255, 0.4); }
  50% { box-shadow: 0 0 20px 5px rgba(255, 0, 255, 0.2); }
}

.mission-lock {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 10px;
}

.mission-lock .lock-icon {
  font-size: 3rem;
  margin-bottom: 10px;
}

.mission-lock .lock-text {
  font-family: 'Orbitron', monospace;
  font-size: 0.9rem;
  color: #718096;
}

.mission-content.blurred {
  filter: blur(3px);
}

.mission-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.mission-id {
  background: var(--neon-magenta);
  color: #fff;
  padding: 5px 12px;
  border-radius: 5px;
  font-family: 'Orbitron', monospace;
  font-size: 0.85rem;
  font-weight: bold;
}

.difficulty span {
  color: #4a5568;
  font-size: 1rem;
}

.difficulty span.active {
  color: var(--neon-yellow);
}

.mission-card h3 {
  color: #fff;
  font-size: 1.2rem;
  margin-bottom: 10px;
}

.mission-scenario {
  color: #a0aec0;
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 15px;
}

.step-progress {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 15px;
}

.step-dot {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.3);
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.step-dot .step-type {
  font-family: 'Orbitron', monospace;
  font-size: 0.9rem;
  color: #718096;
}

.step-dot.completed {
  background: var(--neon-green);
  border-color: var(--neon-green);
}

.step-dot.completed .step-type {
  color: #000;
}

.step-dot.current {
  border-color: var(--neon-magenta);
  animation: stepPulse 1s ease-in-out infinite;
}

@keyframes stepPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255, 0, 255, 0.4); }
  50% { box-shadow: 0 0 10px 3px rgba(255, 0, 255, 0.2); }
}

.completed-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  background: var(--neon-green);
  color: #000;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: bold;
  font-family: 'Orbitron', monospace;
}

.replay-btn {
  margin-top: 15px;
  padding: 10px 20px;
  background: transparent;
  border: 1px solid var(--neon-cyan);
  color: var(--neon-cyan);
  border-radius: 20px;
  font-family: 'Orbitron', monospace;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s;
}

.replay-btn:hover {
  background: var(--neon-cyan);
  color: #000;
}

/* 도전과제 섹션 */
.achievements-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px;
}

.achievements-section h2 {
  font-family: 'Orbitron', monospace;
  color: var(--neon-yellow);
  margin-bottom: 25px;
  text-align: center;
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
}

.achievement-card {
  background: var(--panel-bg);
  border: 2px solid var(--border-color);
  border-radius: 10px;
  padding: 20px 15px;
  text-align: center;
  opacity: 0.4;
  filter: grayscale(100%);
  transition: all 0.3s;
}

.achievement-card.unlocked {
  opacity: 1;
  filter: grayscale(0%);
  border-color: var(--neon-yellow);
  box-shadow: 0 0 15px rgba(255, 255, 0, 0.2);
}

.achievement-card .achievement-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 10px;
}

.achievement-card .achievement-name {
  font-size: 0.75rem;
  color: #a0aec0;
}

.achievement-card.unlocked .achievement-name {
  color: #fff;
}

/* 스탯 패널 */
.stats-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 500;
}

.stats-panel {
  background: var(--panel-bg);
  border: 2px solid var(--neon-cyan);
  border-radius: 16px;
  max-width: 450px;
  width: 90%;
  overflow: hidden;
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  background: rgba(0, 243, 255, 0.1);
  border-bottom: 1px solid var(--border-color);
}

.stats-header h2 {
  font-family: 'Orbitron', monospace;
  font-size: 1.2rem;
  color: var(--neon-cyan);
  margin: 0;
}

.close-btn {
  background: transparent;
  border: none;
  color: #a0aec0;
  font-size: 1.5rem;
  cursor: pointer;
}

.close-btn:hover {
  color: #fff;
}

.stats-content {
  padding: 25px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-row .stat-label {
  color: #a0aec0;
  font-size: 0.95rem;
}

.stat-row .stat-value {
  font-family: 'Orbitron', monospace;
  color: var(--neon-cyan);
  font-size: 1rem;
}

.reset-stats-btn {
  width: calc(100% - 50px);
  margin: 0 25px 25px;
  padding: 12px;
  background: transparent;
  border: 1px solid var(--neon-red);
  color: var(--neon-red);
  border-radius: 8px;
  font-family: 'Orbitron', monospace;
  cursor: pointer;
  transition: all 0.3s;
}

.reset-stats-btn:hover {
  background: var(--neon-red);
  color: #fff;
}

/* Progressive 연습 화면 */
.progressive-practice-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.progressive-header {
  background: linear-gradient(180deg, rgba(255, 0, 255, 0.15) 0%, transparent 100%);
  border-bottom-color: var(--neon-magenta);
}

.progressive-header h1 {
  color: var(--neon-magenta);
}

.header-center {
  display: flex;
  align-items: center;
}

.bugs-status {
  display: flex;
  gap: 20px;
}

.bug-status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 15px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  border: 1px solid var(--border-color);
  transition: all 0.3s;
}

.bug-status-item.active {
  border-color: var(--neon-magenta);
  background: rgba(255, 0, 255, 0.1);
}

.bug-status-item.dead {
  opacity: 0.5;
}

.bug-status-item .bug-icon {
  font-size: 1.8rem;
}

.bug-status-item .bug-label {
  font-family: 'Orbitron', monospace;
  font-size: 0.7rem;
  color: #718096;
}

.remaining-bugs {
  font-family: 'Orbitron', monospace;
  font-size: 1rem;
  color: var(--neon-red);
  background: rgba(255, 51, 102, 0.1);
  padding: 8px 15px;
  border-radius: 20px;
  border: 1px solid var(--neon-red);
}

.progressive-main-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 20px;
  padding: 20px;
  overflow: hidden;
}

/* 미션 브리핑 패널 */
.mission-briefing-panel {
  display: flex;
  flex-direction: column;
  gap: 15px;
  overflow-y: auto;
}

.panel-box {
  background: var(--panel-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
}

.panel-title {
  font-family: 'Orbitron', monospace;
  font-size: 0.85rem;
  color: var(--neon-cyan);
  margin-bottom: 15px;
  padding-left: 12px;
  border-left: 3px solid var(--neon-cyan);
}

.scenario-text {
  color: #a0aec0;
  line-height: 1.6;
  font-size: 0.95rem;
}

.current-target-box {
  border-color: var(--neon-magenta);
}

.current-target-box .panel-title {
  color: var(--neon-magenta);
  border-left-color: var(--neon-magenta);
}

.target-content {
  text-align: center;
}

.target-bug {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 15px;
}

.target-bug-emoji {
  font-size: 2.5rem;
  animation: bugWiggle 0.5s ease-in-out infinite;
}

@keyframes bugWiggle {
  0%, 100% { transform: rotate(-5deg); }
  50% { transform: rotate(5deg); }
}

.target-bug-name {
  font-family: 'Orbitron', monospace;
  font-size: 1.1rem;
  color: var(--neon-magenta);
}

.target-instruction {
  color: #e0e0e0;
  line-height: 1.6;
  font-size: 0.95rem;
}

.side-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: auto;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 15px;
  border-radius: 8px;
  font-family: 'Orbitron', monospace;
  font-size: 0.9rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  background: transparent;
}

.hint-btn {
  border: 2px solid var(--neon-yellow);
  color: var(--neon-yellow);
}

.hint-btn:hover:not(:disabled) {
  background: var(--neon-yellow);
  color: #000;
}

.submit-btn {
  border: 2px solid var(--neon-green);
  color: var(--neon-green);
  font-size: 1rem;
}

.submit-btn:hover:not(:disabled) {
  background: var(--neon-green);
  color: #000;
}

.reset-btn {
  border: 2px solid #718096;
  color: #718096;
}

.reset-btn:hover {
  background: #718096;
  color: #000;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 전체 코드 에디터 */
.full-code-editor {
  background: var(--bg-darker);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.editor-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 12px 20px;
  background: #1a202c;
  border-bottom: 1px solid var(--border-color);
}

.code-progress {
  display: flex;
  align-items: center;
  gap: 15px;
}

.progress-text {
  font-family: 'Orbitron', monospace;
  font-size: 0.9rem;
  color: var(--neon-green);
}

.progress-bar {
  width: 150px;
  height: 8px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--neon-green), var(--neon-cyan));
  border-radius: 4px;
  transition: width 0.5s ease;
}

.editor-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding: 15px;
}

/* 코드 섹션 */
.code-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.code-section {
  background: rgba(0, 0, 0, 0.3);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
}

.code-section.active {
  border-color: var(--neon-magenta);
  box-shadow: 0 0 20px rgba(255, 0, 255, 0.2);
}

.code-section.completed {
  border-color: var(--neon-green);
  background: rgba(0, 255, 136, 0.05);
}

.code-section.locked {
  opacity: 0.6;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: rgba(0, 0, 0, 0.5);
  border-bottom: 1px solid var(--border-color);
}

.section-label {
  font-family: 'Orbitron', monospace;
  font-size: 0.9rem;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 10px;
}

.step-num {
  background: var(--neon-magenta);
  color: #fff;
  width: 25px;
  height: 25px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
}

.code-section.completed .step-num {
  background: var(--neon-green);
}

.section-status {
  font-family: 'Orbitron', monospace;
  font-size: 0.8rem;
}

.status-fixed { color: var(--neon-green); }
.status-current { color: var(--neon-magenta); }
.status-locked { color: #718096; }

/* 잠긴 오버레이 */
.locked-overlay {
  position: relative;
  padding: 20px;
}

.lock-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
  text-align: center;
  background: rgba(0, 0, 0, 0.9);
  padding: 20px 30px;
  border-radius: 10px;
  border: 1px solid var(--border-color);
}

.lock-content .lock-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 10px;
}

.lock-content .lock-text {
  font-family: 'Orbitron', monospace;
  font-size: 0.85rem;
  color: #718096;
}

.blurred-code {
  filter: blur(4px);
  opacity: 0.5;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #718096;
  margin: 0;
  white-space: pre-wrap;
}

/* 코드 에디터 래퍼 */
.code-editor-wrapper {
  display: flex;
  min-height: 200px;
}

.completed-wrapper {
  background: rgba(0, 255, 136, 0.03);
}

.line-numbers {
  width: 45px;
  background: rgba(0, 0, 0, 0.3);
  padding: 15px 0;
  text-align: right;
  user-select: none;
}

.line-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #4b5563;
  padding-right: 10px;
}

/* 게임 스타일 코드 */
.game-code {
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.6;
  letter-spacing: 0.5px;
}

.section-code.editable {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #00ff88;
  padding: 15px;
  resize: none;
  white-space: pre;
  overflow: auto;
  text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
}

.section-code.readonly {
  flex: 1;
  color: #a0aec0;
  padding: 15px;
  margin: 0;
  white-space: pre-wrap;
}

/* 버그 컨테이너 */
.bugs-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 50;
}

.code-bug {
  position: absolute;
  z-index: 51;
  transition: left 0.1s ease-out, top 0.1s ease-out;
}

.code-bug .bug-emoji {
  font-size: 2.5rem;
  display: block;
  filter: drop-shadow(0 0 10px rgba(255, 0, 0, 0.5));
}

.code-bug.eating .bug-emoji {
  animation: bugEat 0.3s ease-in-out infinite;
}

@keyframes bugEat {
  0%, 100% { transform: scale(1) rotate(-5deg); }
  50% { transform: scale(1.1) rotate(5deg); }
}

.code-bug.dead {
  opacity: 0;
  transition: opacity 0.5s ease;
}

.code-bug.targeted .bug-emoji {
  animation: bugPanic 0.1s ease-in-out infinite;
  filter: drop-shadow(0 0 20px rgba(255, 0, 0, 1));
}

@keyframes bugPanic {
  0%, 100% { transform: scale(1.2) rotate(-15deg); }
  50% { transform: scale(0.9) rotate(15deg); }
}

.eating-effect {
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 3px;
}

.bite-mark {
  color: var(--neon-red);
  font-size: 0.8rem;
  animation: biteFloat 0.5s ease-out infinite;
}

.bite-mark:nth-child(2) { animation-delay: 0.15s; }
.bite-mark:nth-child(3) { animation-delay: 0.3s; }

@keyframes biteFloat {
  0% { transform: translateY(0); opacity: 1; }
  100% { transform: translateY(-10px); opacity: 0; }
}

/* 총알 */
.bullet {
  position: absolute;
  z-index: 60;
  pointer-events: none;
  font-size: 2rem;
  animation: bulletSpin 0.1s linear infinite;
}

@keyframes bulletSpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 명중 이펙트 */
.hit-effect {
  position: absolute;
  z-index: 70;
  pointer-events: none;
  text-align: center;
}

.hit-text {
  display: block;
  font-family: 'Orbitron', monospace;
  font-size: 1.8rem;
  font-weight: bold;
  color: var(--neon-green);
  text-shadow: 0 0 20px var(--neon-green), 0 0 40px var(--neon-green);
  animation: hitTextPop 0.5s ease-out forwards;
}

@keyframes hitTextPop {
  0% { transform: scale(0) rotate(-10deg); opacity: 0; }
  50% { transform: scale(1.5) rotate(5deg); opacity: 1; }
  100% { transform: scale(1) rotate(0deg) translateY(-30px); opacity: 0.8; }
}

.explosion-particles {
  position: absolute;
  top: 50%;
  left: 50%;
}

.particle {
  position: absolute;
  width: 10px;
  height: 10px;
  background: var(--neon-yellow);
  border-radius: 50%;
  animation: particleExplode 0.6s ease-out forwards;
  box-shadow: 0 0 15px var(--neon-yellow);
}

@keyframes particleExplode {
  0% { transform: rotate(var(--angle)) translateX(0); opacity: 1; }
  100% { transform: rotate(var(--angle)) translateX(100px); opacity: 0; }
}

.explode-enter-active { animation: explodeIn 0.3s ease-out; }
.explode-leave-active { animation: explodeOut 0.5s ease-in forwards; }

@keyframes explodeIn {
  from { transform: scale(0); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

@keyframes explodeOut {
  from { transform: scale(1); opacity: 1; }
  to { transform: scale(2); opacity: 0; }
}

/* MISS 이펙트 */
.miss-effect {
  position: absolute;
  z-index: 70;
  pointer-events: none;
}

.miss-text {
  font-family: 'Orbitron', monospace;
  font-size: 2rem;
  font-weight: bold;
  color: var(--neon-red);
  text-shadow: 0 0 20px var(--neon-red);
  animation: missShake 0.5s ease-out;
}

@keyframes missShake {
  0%, 100% { transform: translateX(0) rotate(0deg); }
  20% { transform: translateX(-10px) rotate(-5deg); }
  40% { transform: translateX(10px) rotate(5deg); }
  60% { transform: translateX(-5px) rotate(-3deg); }
  80% { transform: translateX(5px) rotate(3deg); }
}

.miss-enter-active { animation: missIn 0.2s ease-out; }
.miss-leave-active { animation: missOut 0.3s ease-in forwards; }

@keyframes missIn {
  from { transform: scale(0); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

@keyframes missOut {
  from { transform: scale(1); opacity: 1; }
  to { transform: scale(0.5) translateY(-20px); opacity: 0; }
}

/* 터미널 */
.terminal-section {
  height: 150px;
  background: #000;
  border-top: 2px solid var(--border-color);
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 20px;
  background: #1a202c;
  font-size: 0.8rem;
  color: #718096;
  letter-spacing: 1px;
}

.terminal-status {
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 0.75rem;
}

.terminal-status.ready { background: #2d3748; color: #a0aec0; }
.terminal-status.running { background: var(--neon-cyan); color: #000; }
.terminal-status.success { background: var(--neon-green); color: #000; }
.terminal-status.error { background: var(--neon-red); color: #fff; }

.terminal-body {
  padding: 15px 20px;
  height: calc(100% - 35px);
  overflow-y: auto;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
}

.terminal-line {
  margin-bottom: 5px;
}

.terminal-line .prompt {
  color: var(--neon-cyan);
  margin-right: 10px;
}

.terminal-line.info .text { color: #a0aec0; }
.terminal-line.success .text { color: var(--neon-green); }
.terminal-line.error .text { color: var(--neon-red); }
.terminal-line.warning .text { color: var(--neon-yellow); }
.terminal-line.command .text { color: #fff; }

/* 힌트 패널 */
.hint-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.hint-panel {
  background: var(--panel-bg);
  border: 2px solid var(--neon-yellow);
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
}

.hint-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px 20px;
  border-bottom: 1px solid var(--border-color);
  font-family: 'Orbitron', monospace;
  color: var(--neon-yellow);
}

.hint-content {
  padding: 25px;
  line-height: 1.7;
  color: #e0e0e0;
}

/* 스텝 완료 이펙트 */
.step-complete-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.step-complete-content {
  text-align: center;
  max-width: 500px;
  animation: completePop 0.5s ease-out;
}

@keyframes completePop {
  0% { transform: scale(0); opacity: 0; }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); opacity: 1; }
}

.complete-icon {
  font-size: 5rem;
  animation: completeShake 0.5s ease-out;
}

@keyframes completeShake {
  0%, 100% { transform: rotate(0); }
  25% { transform: rotate(-10deg); }
  75% { transform: rotate(10deg); }
}

.complete-text {
  font-family: 'Orbitron', monospace;
  font-size: 2rem;
  color: var(--neon-green);
  text-shadow: 0 0 20px var(--neon-green);
  margin: 20px 0;
}

.bug-killed {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 25px;
}

.bug-killed .dead-bug {
  font-size: 3rem;
  animation: deadBugFade 1s ease-out forwards;
}

@keyframes deadBugFade {
  0% { transform: scale(1); filter: grayscale(0); }
  100% { transform: scale(0.5) rotate(180deg); filter: grayscale(100%); }
}

.kill-text {
  font-family: 'Orbitron', monospace;
  font-size: 1.5rem;
  color: var(--neon-red);
}

.coaching-box {
  background: rgba(0, 243, 255, 0.1);
  border: 1px solid var(--neon-cyan);
  border-radius: 12px;
  padding: 20px;
  text-align: left;
}

.coaching-title {
  font-family: 'Orbitron', monospace;
  font-size: 0.9rem;
  color: var(--neon-cyan);
  margin-bottom: 10px;
}

.coaching-text {
  color: #e0e0e0;
  line-height: 1.7;
  font-size: 0.95rem;
}

.stepComplete-enter-active { animation: completePop 0.5s ease-out; }
.stepComplete-leave-active { animation: completeFade 0.5s ease-in forwards; }

@keyframes completeFade {
  from { opacity: 1; transform: scale(1); }
  to { opacity: 0; transform: scale(1.2); }
}

/* 미션 완료 이펙트 */
.mission-complete-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.95), rgba(50, 0, 50, 0.95));
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.mission-complete-content {
  text-align: center;
  animation: missionCompletePop 0.8s ease-out;
}

@keyframes missionCompletePop {
  0% { transform: scale(0) rotate(-10deg); opacity: 0; }
  50% { transform: scale(1.1) rotate(5deg); }
  100% { transform: scale(1) rotate(0); opacity: 1; }
}

.complete-fireworks {
  font-size: 6rem;
  animation: fireworksBurst 1s ease-out infinite;
}

@keyframes fireworksBurst {
  0%, 100% { transform: scale(1); filter: hue-rotate(0deg); }
  50% { transform: scale(1.2); filter: hue-rotate(180deg); }
}

.complete-title {
  font-family: 'Orbitron', monospace;
  font-size: 3rem;
  color: var(--neon-yellow);
  text-shadow: 0 0 40px var(--neon-yellow);
  margin: 20px 0;
}

.complete-project {
  font-size: 1.5rem;
  color: #fff;
  margin-bottom: 30px;
}

.all-bugs-dead {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  margin-bottom: 30px;
}

.dead-bug-row {
  display: flex;
  gap: 20px;
}

.dead-bug-row .dead-bug {
  font-size: 3rem;
  animation: allDeadSpin 2s linear infinite;
}

@keyframes allDeadSpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.all-dead-text {
  font-family: 'Orbitron', monospace;
  font-size: 1.2rem;
  color: var(--neon-green);
  text-shadow: 0 0 15px var(--neon-green);
}

.mission-rewards {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 30px;
}

.reward-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.1);
  padding: 15px 25px;
  border-radius: 30px;
}

.reward-icon { font-size: 1.5rem; }
.reward-value {
  font-family: 'Orbitron', monospace;
  font-size: 1.2rem;
  color: var(--neon-yellow);
}

.continue-btn {
  background: var(--neon-magenta);
  border: none;
  color: #fff;
  padding: 15px 50px;
  font-family: 'Orbitron', monospace;
  font-size: 1.1rem;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s;
}

.continue-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 0 30px var(--neon-magenta);
}

.missionComplete-enter-active { animation: missionCompletePop 0.8s ease-out; }
.missionComplete-leave-active { animation: missionFade 0.5s ease-in forwards; }

@keyframes missionFade {
  from { opacity: 1; }
  to { opacity: 0; }
}

/* 종료 확인 모달 */
.confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 300;
}

.confirm-modal {
  background: var(--panel-bg);
  border: 2px solid var(--neon-yellow);
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  max-width: 400px;
}

.confirm-modal h3 {
  color: var(--neon-yellow);
  margin-bottom: 15px;
}

.confirm-modal p {
  color: #a0aec0;
  line-height: 1.6;
  margin-bottom: 25px;
}

.confirm-actions {
  display: flex;
  gap: 15px;
}

.confirm-btn {
  flex: 1;
  padding: 12px;
  border-radius: 6px;
  font-family: 'Orbitron', monospace;
  cursor: pointer;
  transition: all 0.3s;
}

.confirm-btn.cancel {
  background: transparent;
  border: 2px solid #718096;
  color: #718096;
}

.confirm-btn.cancel:hover {
  background: #718096;
  color: #000;
}

.confirm-btn.exit {
  background: transparent;
  border: 2px solid var(--neon-red);
  color: var(--neon-red);
}

.confirm-btn.exit:hover {
  background: var(--neon-red);
  color: #fff;
}

/* 레벨업 이펙트 */
.levelup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: levelupFlash 0.5s ease-out;
}

@keyframes levelupFlash {
  0% { background: rgba(255, 215, 0, 0.5); }
  100% { background: rgba(0, 0, 0, 0.9); }
}

.levelup-content {
  text-align: center;
  animation: levelupBounce 0.5s ease-out;
}

@keyframes levelupBounce {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.levelup-badge {
  font-size: 5rem;
  animation: badgeShine 1s ease-in-out infinite;
}

@keyframes badgeShine {
  0%, 100% { filter: drop-shadow(0 0 20px gold); }
  50% { filter: drop-shadow(0 0 40px gold); }
}

.levelup-text {
  font-family: 'Orbitron', monospace;
  font-size: 3rem;
  color: var(--neon-yellow);
  text-shadow: 0 0 30px var(--neon-yellow);
  margin: 20px 0;
}

.levelup-level {
  font-family: 'Orbitron', monospace;
  font-size: 2rem;
  color: #fff;
  margin-bottom: 10px;
}

.levelup-title {
  font-size: 1.5rem;
  color: var(--neon-cyan);
}

.levelup-enter-active { animation: levelupIn 0.3s ease-out; }
.levelup-leave-active { animation: levelupOut 0.5s ease-in forwards; }

@keyframes levelupIn {
  from { opacity: 0; transform: scale(0.5); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes levelupOut {
  from { opacity: 1; transform: scale(1); }
  to { opacity: 0; transform: scale(1.5); }
}

/* 도전과제 팝업 */
.achievement-popup {
  position: fixed;
  top: 80px;
  right: 30px;
  display: flex;
  align-items: center;
  gap: 15px;
  background: linear-gradient(135deg, rgba(26, 31, 46, 0.98), rgba(0, 0, 0, 0.95));
  border: 2px solid var(--neon-yellow);
  border-radius: 12px;
  padding: 20px 25px;
  z-index: 500;
  box-shadow: 0 10px 40px rgba(255, 255, 0, 0.3);
  animation: achievementSlide 0.5s ease-out;
}

@keyframes achievementSlide {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

.achievement-popup .achievement-icon {
  font-size: 2.5rem;
}

.achievement-info .achievement-label {
  font-family: 'Orbitron', monospace;
  font-size: 0.7rem;
  color: var(--neon-yellow);
  letter-spacing: 2px;
}

.achievement-info .achievement-name {
  font-size: 1.1rem;
  color: #fff;
  font-weight: bold;
  margin: 5px 0;
}

.achievement-info .achievement-desc {
  font-size: 0.85rem;
  color: #a0aec0;
}

.achievement-enter-active { animation: achievementSlide 0.5s ease-out; }
.achievement-leave-active { animation: achievementSlideOut 0.3s ease-in forwards; }

@keyframes achievementSlideOut {
  from { transform: translateX(0); opacity: 1; }
  to { transform: translateX(100%); opacity: 0; }
}

/* 트랜지션 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-down-enter-active, .slide-down-leave-active { transition: all 0.3s; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-20px); }

/* 반응형 */
@media (max-width: 1200px) {
  .progressive-main-layout {
    grid-template-columns: 300px 1fr;
  }
}

@media (max-width: 900px) {
  .mission-grid {
    grid-template-columns: 1fr;
  }

  .progressive-main-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }

  .mission-briefing-panel {
    flex-direction: row;
    flex-wrap: wrap;
    overflow-x: auto;
  }

  .panel-box {
    min-width: 250px;
  }
}
</style>
