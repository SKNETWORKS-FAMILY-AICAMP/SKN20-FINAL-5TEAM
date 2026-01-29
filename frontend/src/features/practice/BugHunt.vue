<template>
  <div class="debug-practice-page" :class="{ 'shake-effect': isShaking }">
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

    <!-- 버그 수정 알림 팝업 (중앙 → 대화창 애니메이션) -->
    <div
      v-if="showAlertPopup"
      class="alert-popup-overlay"
      @click="dismissAlertPopup"
    >
      <div
        class="alert-popup-content"
        :class="[alertPopupPhase]"
      >
        <div class="alert-popup-icon">⚠️</div>
        <div class="alert-popup-message">{{ alertPopupMessage }}</div>
        <div class="alert-popup-hint">화면을 터치하면 닫힙니다</div>
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
            <button class="continue-btn" @click="showEvaluation">VIEW EVALUATION REPORT</button>
          </div>
        </div>
      </transition>

      <!-- 1단계: 객관식 팝업 -->
      <transition name="fade">
        <div v-if="showQuizPopup" class="quiz-overlay">
          <div class="quiz-modal neon-border">
            <div class="quiz-header">
              <span class="phase-badge">PHASE 1: ANALYSIS</span>
              <h3>STEP {{ currentProgressiveStep }} 분석 퀴즈</h3>
            </div>
            <div class="quiz-question">
              <p>{{ getCurrentStepData()?.questions?.text }}</p>
            </div>
            <div class="quiz-options">
              <button
                v-for="(option, idx) in getCurrentStepData()?.questions?.options"
                :key="idx"
                class="quiz-option-btn"
                :class="{ selected: selectedQuizOption === idx }"
                @click="selectedQuizOption = idx"
              >
                <span class="option-num">{{ idx + 1 }}</span>
                {{ option }}
              </button>
            </div>
            <div class="quiz-footer">
              <button class="quiz-submit-btn" @click="submitQuiz" :disabled="selectedQuizOption === null">
                분석 완료 (디버깅 시작)
              </button>
              <p v-if="quizFeedback" class="quiz-feedback" :class="quizFeedbackType">{{ quizFeedback }}</p>
            </div>
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

          <div class="side-controls">
            <template v-if="currentProgressivePhase === 'debug'">
            </template>
            
            <!-- PHASE 3: EXPLAIN은 팝업으로 표시됨 -->
            <!-- CHAT INTERFACE -->
            <!-- CHAT INTERFACE -->
            <div class="chat-interface neon-border" ref="chatInterfaceRef">
              <div class="chat-header">
                <span class="chat-icon">💬</span>
                <span class="chat-title">MISSION LOG</span>
              </div>
              <div class="chat-messages" ref="chatMessagesRef">
                <div 
                  v-for="(msg, idx) in chatMessages" 
                  :key="idx" 
                  class="chat-message"
                  :class="[msg.role, { 'new-message': msg.isNew }]"
                >
                  <div class="message-avatar" v-if="msg.role === 'system'">🤖</div>
                  <div class="message-content">
                    <div class="message-bubble" :class="{ 'flash-bubble': msg.isNew && msg.role === 'system' }">{{ msg.text }}</div>
                  </div>
                  <div class="message-avatar" v-if="msg.role === 'user'">👤</div>
                </div>
              </div>
              <div class="chat-input-area">
                <input 
                  v-model="chatInput" 
                  @keyup.enter="handleChatSubmit"
                  placeholder="Type your message..."
                  :disabled="currentProgressivePhase !== 'explain'"
                  class="chat-input-box"
                />
                <button 
                  class="chat-send-btn" 
                  @click="handleChatSubmit"
                  :disabled="!chatInput.trim() || currentProgressivePhase !== 'explain'"
                >
                  SEND
                </button>
              </div>
            </div>
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
                targeted: step === currentProgressiveStep && isRunning,
                clickable: step === currentProgressiveStep && currentProgressivePhase === 'debug'
              }"
              :style="bugPositions[step]"
              @click="onBugClick(step)"
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
            <!-- 에디터 상단 버튼들 -->
            <div class="editor-top-buttons" v-if="currentProgressivePhase === 'debug'">
              <button class="editor-btn hint-btn" @click="showProgressiveHint">
                💡 HINT
              </button>
              <button class="editor-btn reset-btn" @click="resetCurrentStep">
                ↺ RESET
              </button>
              <button class="editor-btn submit-btn" @click="submitProgressiveStep" :disabled="currentProgressiveStep > 3 || isRunning">
                🚀 SUBMIT
              </button>
            </div>
          </div>

          <div class="editor-body" ref="editorBodyRef">
            <!-- 전체 코드를 3개 섹션으로 표시 -->
            <div class="code-sections">
              <div
                v-for="step in 3"
                :key="'section-' + step"
                ref="sectionRefs"
                class="code-section"
                :class="{
                  locked: Number(step) > Number(currentProgressiveStep) && !progressiveCompletedSteps.includes(Number(step)),
                  active: Number(step) === Number(currentProgressiveStep),
                  completed: progressiveCompletedSteps.includes(Number(step))
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
                <div v-if="Number(step) > Number(currentProgressiveStep) && !progressiveCompletedSteps.includes(Number(step))" class="locked-overlay">
                  <div class="lock-content">
                    <span class="lock-icon">🔒</span>
                    <span class="lock-text">Step {{ Number(step) - 1 }} 완료 필요</span>
                  </div>
                  <pre class="blurred-code">{{ getStepData(step)?.buggy_code || 'Loading code...' }}</pre>
                </div>

                <!-- 편집 가능한 섹션 (현재 스텝) -->
                <div v-else-if="Number(step) === Number(currentProgressiveStep)" class="code-editor-wrapper active-wrapper monaco-active-wrapper">
                  <vue-monaco-editor
                    v-model:value="progressiveStepCodes[Number(step)]"
                    theme="vs-dark"
                    language="python"
                    :options="editorOptions"
                    @mount="handleEditorMount"
                    class="bughunt-monaco-editor"
                  />
                </div>

                <!-- 완료된 섹션 -->
                <div v-else class="code-editor-wrapper completed-wrapper">
                  <div class="line-numbers">
                    <div v-for="n in getLineCount(progressiveStepCodes[Number(step)])" :key="n" class="line-num">{{ n }}</div>
                  </div>
                  <pre class="section-code readonly game-code">{{ progressiveStepCodes[Number(step)] || 'Code not found' }}</pre>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 힌트 오리 (말풍선 포함) -->
          <transition name="duck-pop">
            <div v-if="showProgressiveHintPanel" class="hint-duck-container">
              <div class="hint-speech-bubble">
                <div class="bubble-header">DUC-TIP! 💡</div>
                <div class="bubble-content">{{ getCurrentStepData()?.hint }}</div>
              </div>
              <img src="/image/unit_duck.png" class="hint-duck-img" alt="Hint Duck">
            </div>
          </transition>
        </main>
      </div>
    </div>

    <!-- 최종 평가 화면 -->
    <div v-if="currentView === 'evaluation'" class="evaluation-container">
      <header class="header">
        <h1>DEBUGGING REPORT</h1>
        <div class="subtitle">// MISSION CLEAR ANALYSIS</div>
      </header>

      <div class="evaluation-content">
        <div class="report-card neon-border">
          <div class="report-header">
            <div class="project-info">
              <span class="id-badge">CLEAR!</span>
              <h2>{{ currentProgressiveMission?.project_title }}</h2>
            </div>
            <div class="score-summary">
              <div class="score-item">
                <span class="label">FINAL SCORE</span>
                <span class="value">{{ progressiveMissionScore }}</span>
              </div>
              <div class="penalty-stats" v-if="(quizIncorrectCount || codeSubmitFailCount || Object.values(progressiveHintUsed).filter(v => v).length)">
                 <div class="penalty-item">
                   <span class="p-label">WRONG QUIZ ({{ quizIncorrectCount }})</span>
                   <span class="p-value">-{{ quizIncorrectCount * 2 }}</span>
                 </div>
                 <div class="penalty-item">
                   <span class="p-label">CODE RETRY ({{ codeSubmitFailCount }})</span>
                   <span class="p-value">-{{ codeSubmitFailCount * 2 }}</span>
                 </div>
                 <div class="penalty-item">
                   <span class="p-label">HINTS USED ({{ Object.values(progressiveHintUsed).filter(v => v).length }})</span>
                   <span class="p-value">-{{ Object.values(progressiveHintUsed).filter(v => v).length }}</span>
                 </div>
              </div>
            </div>
          </div>

          <div class="stats-grid">
            <div class="stat-box">
              <div class="stat-icon">🎓</div>
              <div class="stat-details">
                <span class="label">QUIZ ACCURACY</span>
                <span class="value text-cyan">{{ quizCorrectCount }}/3</span>
              </div>
            </div>
            <div class="stat-box">
              <div class="stat-icon">⏱️</div>
              <div class="stat-details">
                <span class="label">TIME TAKEN</span>
                <span class="value text-magenta">{{ formatTime(totalDebugTime) }}</span>
              </div>
            </div>
            <div class="stat-box">
              <div class="stat-icon">💎</div>
              <div class="stat-details">
                <span class="label">PERFECT CLEARS</span>
                <span class="value text-green">{{ evaluationStats.perfectClears }}/3</span>
              </div>
            </div>
          </div>

          <!-- AI 디버깅 사고 평가 섹션 -->
          <div class="ai-report-section neon-border">
            <div class="report-section-title">
              <span class="ai-icon">🧠</span>
              디버깅 사고 평가
            </div>

            <div v-if="isEvaluatingAI" class="ai-loading">
              <div class="pulse-loader"></div>
              <p>AI가 당신의 디버깅 사고를 분석 중입니다...</p>
            </div>

            <div v-else-if="aiEvaluationResult" class="ai-result">
              <!-- 사고 방향 통과/탈락 -->
              <div class="thinking-eval-grid">
                <div class="eval-card thinking-pass-card">
                  <div class="eval-card-header">
                    <span class="eval-icon">🎯</span>
                    <span class="eval-title">사고 방향</span>
                  </div>
                  <div class="eval-card-body">
                    <span
                      class="pass-badge"
                      :class="aiEvaluationResult.thinking_pass ? 'pass' : 'fail'"
                    >
                      {{ aiEvaluationResult.thinking_pass ? '✅ 안전' : '🚫 위험' }}
                    </span>
                  </div>
                </div>

                <!-- 코드 위험도 -->
                <div class="eval-card risk-card">
                  <div class="eval-card-header">
                    <span class="eval-icon">⚠️</span>
                    <span class="eval-title">코드 위험도</span>
                  </div>
                  <div class="eval-card-body">
                    <div class="risk-gauge">
                      <div
                        class="risk-fill"
                        :style="{ width: aiEvaluationResult.code_risk + '%' }"
                        :class="getRiskLevel(aiEvaluationResult.code_risk)"
                      ></div>
                    </div>
                    <span class="risk-value">{{ aiEvaluationResult.code_risk }}/100</span>
                  </div>
                </div>

                <!-- 사고력 점수 -->
                <div class="eval-card thinking-score-card">
                  <div class="eval-card-header">
                    <span class="eval-icon">💡</span>
                    <span class="eval-title">사고력 점수</span>
                  </div>
                  <div class="eval-card-body">
                    <span class="thinking-score-value">{{ aiEvaluationResult.thinking_score }}</span>
                    <span class="thinking-score-max">/100</span>
                  </div>
                </div>
              </div>

              <!-- 총평 -->
              <div class="summary-box">
                <div class="summary-label">📝 총평</div>
                <p class="summary-text">{{ aiEvaluationResult.총평 }}</p>
              </div>
            </div>
          </div>

          <div class="explanations-list">
            <div class="list-title">📋 DEBBUGING LOG & STRATEGY</div>
            <div 
              v-for="step in 3" 
              :key="'eval-step-' + step" 
              class="eval-step-box"
            >
              <div class="step-header">
                <span class="step-num">STEP {{ step }}</span>
                <span class="step-title">{{ getStepData(step)?.title }}</span>
              </div>
              <div class="step-explanation">
                <span class="label">Strategy:</span>
                <p>{{ stepExplanations[step] || '설명이 작성되지 않았습니다.' }}</p>
              </div>

              <!-- AI 피드백 -->
              <div v-if="getStepFeedback(step)" class="step-feedback">
                <div class="feedback-label">🤖 AI FEEDBACK</div>
                <p class="feedback-text">{{ getStepFeedback(step) }}</p>
              </div>
            </div>
          </div>

          <div class="evaluation-actions">
            <button class="back-to-menu-btn" @click="finishProgressiveMission">BACK TO HQ</button>
          </div>
        </div>
      </div>
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

<style scoped>
/* 기존 스타일 유지 */

/* 채팅 인터페이스 스타일 */
.chat-interface {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(10, 10, 15, 0.8);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 8px;
  margin-top: 1rem;
  overflow: hidden;
  min-height: 300px;
  max-height: 450px;
}

.chat-header {
  padding: 0.8rem;
  background: rgba(0, 255, 255, 0.1);
  border-bottom: 1px solid rgba(0, 255, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: bold;
  color: #0ff;
}

.chat-messages {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chat-message {
  display: flex;
  gap: 0.5rem;
  max-width: 90%;
}

.chat-message.system {
  align-self: flex-start;
}

.chat-message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-avatar {
  font-size: 1.2rem;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}

.message-bubble {
  padding: 0.8rem;
  border-radius: 12px;
  font-size: 0.9rem;
  line-height: 1.4;
  white-space: pre-wrap;
}

.chat-message.system .message-bubble {
  background: rgba(0, 255, 255, 0.15);
  border: 1px solid rgba(0, 255, 255, 0.3);
  color: #e0f0ff;
  border-top-left-radius: 2px;
}

.chat-message.user .message-bubble {
  background: rgba(255, 0, 255, 0.15);
  border: 1px solid rgba(255, 0, 255, 0.3);
  color: #ffe0ff;
  border-top-right-radius: 2px;
}

.chat-input-area {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 0.5rem;
  background: rgba(0, 0, 0, 0.3);
}

.chat-input-box {
  flex: 1;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  padding: 0.8rem;
  color: white;
  font-family: inherit;
}

.chat-input-box:focus {
  outline: none;
  border-color: #0ff;
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
}

.chat-input-box:disabled {
  background: rgba(255, 255, 255, 0.05);
  cursor: not-allowed;
  opacity: 0.5;
}

.chat-send-btn {
  background: linear-gradient(135deg, #0ff, #0088ff);
  border: none;
  color: black;
  font-weight: bold;
  padding: 0 1.2rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.chat-send-btn:hover:not(:disabled) {
  filter: brightness(1.2);
  transform: translateY(-1px);
}

.chat-send-btn:disabled {
  background: #333;
  color: #666;
  cursor: not-allowed;
}

/* Scrollbar styling for chat */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(0, 255, 255, 0.2);
  border-radius: 3px;
}

/* New Message Effects */
.flash-bubble {
  animation: bubbleFlash 1.5s ease-out infinite alternate;
}

@keyframes bubbleFlash {
  0% { box-shadow: 0 0 5px var(--neon-cyan); border-color: var(--neon-cyan); }
  100% { box-shadow: 0 0 15px var(--neon-cyan), 0 0 5px #fff; border-color: #fff; }
}

.chat-message.new-message {
  animation: slideInMessage 0.3s ease-out, highlightMessage 1s ease-out;
}

@keyframes slideInMessage {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes highlightMessage {
  0% { filter: brightness(1.5); }
  100% { filter: brightness(1); }
}

/* 버그 수정 알림 팝업 스타일 */
.alert-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  pointer-events: auto;
  cursor: pointer;
  background: rgba(0, 0, 0, 0.3);
}

.alert-popup-content {
  background: linear-gradient(135deg, rgba(0, 255, 255, 0.15), rgba(255, 0, 128, 0.15));
  border: 2px solid var(--neon-cyan);
  border-radius: 16px;
  padding: 30px 50px;
  text-align: center;
  box-shadow:
    0 0 30px rgba(0, 255, 255, 0.5),
    0 0 60px rgba(0, 255, 255, 0.3),
    inset 0 0 30px rgba(0, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  max-width: 500px;
}

.alert-popup-icon {
  font-size: 3rem;
  margin-bottom: 15px;
  animation: iconPulse 0.5s ease-in-out infinite alternate;
}

@keyframes iconPulse {
  from { transform: scale(1); filter: brightness(1); }
  to { transform: scale(1.1); filter: brightness(1.3); }
}

.alert-popup-message {
  font-size: 1.1rem;
  color: #fff;
  line-height: 1.8;
  white-space: pre-wrap;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
}

.alert-popup-hint {
  margin-top: 20px;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  animation: hintBlink 1.5s ease-in-out infinite;
}

@keyframes hintBlink {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* 흔들림 애니메이션 (shake) */
.alert-popup-content.shake {
  animation: popupShake 0.6s ease-out, popupAppear 0.3s ease-out;
}

@keyframes popupAppear {
  0% {
    opacity: 0;
    transform: scale(0.5);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes popupShake {
  0%, 100% { transform: translateX(0) rotate(0deg); }
  10% { transform: translateX(-8px) rotate(-2deg); }
  20% { transform: translateX(8px) rotate(2deg); }
  30% { transform: translateX(-8px) rotate(-2deg); }
  40% { transform: translateX(8px) rotate(2deg); }
  50% { transform: translateX(-5px) rotate(-1deg); }
  60% { transform: translateX(5px) rotate(1deg); }
  70% { transform: translateX(-3px) rotate(0deg); }
  80% { transform: translateX(3px) rotate(0deg); }
  90% { transform: translateX(-1px) rotate(0deg); }
}

/* 대화창으로 날아가는 애니메이션 (fly) */
.alert-popup-content.fly {
  animation: flyToChat 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes flyToChat {
  0% {
    opacity: 1;
    transform: scale(1) translate(0, 0);
  }
  30% {
    opacity: 1;
    transform: scale(0.8) translate(0, -20px);
  }
  100% {
    opacity: 0;
    transform: scale(0.3) translate(-60vw, 30vh);
  }
}
</style>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, shallowRef, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { VueMonacoEditor } from '@guolao/vue-monaco-editor';
import progressiveData from './progressive-problems.json';
import { evaluateBugHunt } from './services/bugHuntApi';

const route = useRoute();
const router = useRouter();

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

// Monaco Editor 설정
const monacoEditorRef = shallowRef(null);
const editorOptions = {
  theme: 'vs-dark',
  language: 'python',
  tabSize: 4,
  automaticLayout: true,
  fontSize: 14,
  lineNumbers: 'on',
  minimap: { enabled: false },
  scrollBeyondLastLine: false,
  wordWrap: 'off',
  folding: false,
  renderLineHighlight: 'all',
  contextmenu: false,
  padding: { top: 10, bottom: 10 }
};

const handleEditorMount = (editorInstance) => {
  monacoEditorRef.value = editorInstance;
};

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
const currentProgressivePhase = ref('quiz'); // 'quiz', 'debug', 'explain'
const progressiveCompletedSteps = ref([]);
const progressiveStepCodes = ref({ 1: '', 2: '', 3: '' });
const progressiveHintUsed = ref({ 1: false, 2: false, 3: false });
const showProgressiveHintPanel = ref(false);
const justCompletedStep = ref(0);

// 분석 퀴즈 상태
const showQuizPopup = ref(false);
const selectedQuizOption = ref(null);
const quizFeedback = ref('');
const quizFeedbackType = ref('');
const quizCorrectCount = ref(0);
const quizIncorrectCount = ref(0);
const codeSubmitFailCount = ref(0);

// 설명 및 평가 데이터
const stepExplanations = reactive({ 1: '', 2: '', 3: '' });
const chatMessages = ref([]);
const chatInput = ref('');
const chatMessagesRef = ref(null);
const hasNewMessage = ref(false);

const stepStartTime = ref(null);
const totalDebugTime = ref(0);
const evaluationStats = reactive({
  perfectClears: 0,
});

// AI 평가 상태
const isEvaluatingAI = ref(false);
const aiEvaluationResult = ref(null);

// Progressive UI 이펙트
const showStepComplete = ref(false);
const showMissionComplete = ref(false);
const progressiveMissionXP = ref(0);
const progressiveMissionScore = ref(0);

// 화면 흔들림 효과
const isShaking = ref(false);

// 버그 수정 알림 팝업 (중앙에서 대화창으로 날아가는 효과)
const showAlertPopup = ref(false);
const alertPopupMessage = ref('');
const alertPopupPhase = ref(''); // 'shake' | 'fly' | ''
const chatInterfaceRef = ref(null);



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
  const s1 = isStepCompleted(missionId, 1);
  const s2 = isStepCompleted(missionId, 2);
  const s3 = isStepCompleted(missionId, 3);
  
  if (!s1) return 1;
  if (!s2) return 2;
  if (!s3) return 3;
  
  // 모든 단계를 이미 완료했다면 (Replay 모드) 1단계부터 다시 시작
  return 1;
}

// 완료된 Progressive 미션 수
function getProgressiveMissionsCompleted() {
  return progressiveProblems.filter(m => isStepCompleted(m.id, 3)).length;
}

// 스텝 데이터 가져오기 (타입 안정성 강화)
function getStepData(stepNum) {
  if (!currentProgressiveMission.value?.steps) return null;
  return currentProgressiveMission.value.steps.find(s => Number(s.step) === Number(stepNum));
}

// 스텝별 AI 피드백 가져오기
function getStepFeedback(stepNum) {
  if (!aiEvaluationResult.value?.step_feedbacks) return null;
  const feedback = aiEvaluationResult.value.step_feedbacks.find(f => f.step === stepNum);
  return feedback?.feedback || null;
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
function startProgressiveMission(mission, index, startAtStep = 1) {
  if (!isMissionUnlocked(index) && !route.query.mapMode) return;

  currentProgressiveMission.value = mission;
  currentProgressiveStep.value = startAtStep;
  progressiveCompletedSteps.value = [];
  
  // 이미 진행된 스텝들은 완료 처리 (현재 스텝 미만)
  for (let i = 1; i < startAtStep; i++) {
    progressiveCompletedSteps.value.push(i);
  }

  progressiveHintUsed.value = { 1: false, 2: false, 3: false };

  // 모든 스텝의 버그 코드 로드 (키 불일치 방지를 위해 번호로 강제 변환)
  progressiveStepCodes.value = {};
  mission.steps.forEach(s => {
    progressiveStepCodes.value[Number(s.step)] = s.buggy_code;
  });

  stepExplanations[1] = '';
  stepExplanations[2] = '';
  stepExplanations[3] = '';
  quizCorrectCount.value = 0;
  quizIncorrectCount.value = 0;
  codeSubmitFailCount.value = 0;
  totalDebugTime.value = 0;
  evaluationStats.perfectClears = 0;

  currentView.value = 'progressivePractice';
  
  // 시작할 스텝의 퀴즈부터 표시
  showQuizPhase();
  
  // 채팅 초기화
  chatMessages.value = [
    { role: 'system', text: `MISSION STARTED: ${mission.project_title}\n\n${mission.scenario}`, isNew: false }
  ];

  // 버그 애니메이션 시작
  setTimeout(() => {
    startBugAnimations();
  }, 500);

  // 터미널 초기화
  terminalOutput.value = [
    { prompt: '>', text: `Project: ${mission.project_title} Initialized.`, type: 'info' },
    { prompt: '>', text: `Total Errors: 3 | Current: Step ${startAtStep}`, type: 'warning' }
  ];
  terminalStatus.value = 'ready';
}

// 퀴즈 페이즈 시작
function showQuizPhase() {
  currentProgressivePhase.value = 'quiz';
  selectedQuizOption.value = null;
  quizFeedback.value = '';
  showQuizPopup.value = true;
}

// 퀴즈 제출
function submitQuiz() {
  const stepData = getCurrentStepData();
  if (!stepData || !stepData.questions) {
    console.error('Step data or questions not found');
    return;
  }

  if (selectedQuizOption.value === stepData.questions.answer) {
    quizCorrectCount.value++;
    quizFeedback.value = '정답입니다! 디버깅을 시작하세요.';
    quizFeedbackType.value = 'success';

    setTimeout(() => {
      showQuizPopup.value = false;
      startDebugPhase();
    }, 1000);
  } else {
    quizIncorrectCount.value++;
    quizFeedback.value = '틀렸습니다. 다시 생각해보세요!';
    quizFeedbackType.value = 'error';
    setTimeout(() => { quizFeedback.value = ''; }, 2000);
  }
}

// 디버깅 페이즈 시작
function startDebugPhase() {
  currentProgressivePhase.value = 'debug';
  stepStartTime.value = Date.now();
  terminalOutput.value.push({
    prompt: '>',
    text: `Step ${currentProgressiveStep.value} debugging started.`,
    type: 'info'
  });
}

// 채팅 메시지 추가 헬퍼
function addChatMessage(role, text) {
  const isSystem = role === 'system';
  
  chatMessages.value.push({ 
    role, 
    text, 
    isNew: true 
  });
  
  if (isSystem) {
    hasNewMessage.value = true;
    setTimeout(() => { hasNewMessage.value = false; }, 500);
  }

  // DOM 업데이트 후 스크롤
  nextTick(() => {
    scrollToBottom();
  });
}

// 중앙 팝업 표시 후 대화창으로 날아가는 애니메이션
function showAlertWithAnimation(message) {
  alertPopupMessage.value = message;
  alertPopupPhase.value = 'shake';
  showAlertPopup.value = true;
}

// 팝업 닫기 (터치)
function dismissAlertPopup() {
  if (!showAlertPopup.value || alertPopupPhase.value === 'fly') return;

  // 날아가는 애니메이션 시작
  alertPopupPhase.value = 'fly';

  // 0.8초 후 팝업 숨기고 대화창에 메시지 추가
  setTimeout(() => {
    showAlertPopup.value = false;
    const message = alertPopupMessage.value;
    alertPopupPhase.value = '';
    alertPopupMessage.value = '';
    addChatMessage('system', `⚠️ ${message}`);
  }, 800);
}

// 다음 문제로 이동 (설명 완료 후)
function moveToNextStep() {
  if (currentProgressiveStep.value < 3) {
    currentProgressiveStep.value++;
    showQuizPhase();
  } else {
    completeMission();
  }
}

// 채팅 메시지 스크롤
function scrollToBottom() {
  if (chatMessagesRef.value) {
    // 부드러운 스크롤을 위해 약간의 딜레이 보장 및 smooth behavior
    setTimeout(() => {
      chatMessagesRef.value.scrollTo({
        top: chatMessagesRef.value.scrollHeight,
        behavior: 'smooth'
      });
    }, 50);
  }
}

// 채팅 제출 (설명 처리)
function handleChatSubmit() {
  if (!chatInput.value.trim() || currentProgressivePhase.value !== 'explain') return;

  const userText = chatInput.value.trim();
  
  // 사용자 메시지 추가
  addChatMessage('user', userText);
  chatInput.value = '';

  // 설명 저장
  stepExplanations[currentProgressiveStep.value] = userText;

  // 시스템 응답 및 다음 단계 진행
  setTimeout(() => {
    addChatMessage('system', '설명이 기록되었습니다. 훌륭합니다! 데이터가 처리되는 동안 잠시만 기다려주세요...');
    
    setTimeout(() => {
      if (currentProgressiveStep.value < 3) {
        addChatMessage('system', `STEP ${currentProgressiveStep.value} 완료. 다음 보안 레벨로 접근합니다.`);
        moveToNextStep();
      } else {
        addChatMessage('system', '모든 미션이 완료되었습니다! 최종 리포트를 생성합니다.');
        completeMission();
      }
    }, 1500);
  }, 500);
}

// 평가 화면 보기
async function showEvaluation() {
  showMissionComplete.value = false;
  currentView.value = 'evaluation';

  if (currentProgressiveMission.value) {
    isEvaluatingAI.value = true;
    try {
      aiEvaluationResult.value = await evaluateBugHunt(
        currentProgressiveMission.value.project_title,
        currentProgressiveMission.value.steps,
        stepExplanations,
        progressiveStepCodes.value,
        {
          quizIncorrectCount: quizIncorrectCount.value,
          codeSubmitFailCount: codeSubmitFailCount.value,
          hintCount: Object.values(progressiveHintUsed.value).filter(v => v).length,
          totalDebugTime: totalDebugTime.value
        }
      );
    } catch (error) {
      console.error('❌ AI Evaluation failed:', error);
    } finally {
      isEvaluatingAI.value = false;
    }
  }
}

// 시간 포맷팅
function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
}

// 위험도 레벨 계산
function getRiskLevel(risk) {
  if (risk <= 30) return 'low';
  if (risk <= 60) return 'medium';
  return 'high';
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

// Progressive 힌트 보기 (토글 방식으로 변경 - 여러 번 볼 수 있음)
function showProgressiveHint() {
  // 첫 사용 시에만 기록 (점수 계산용)
  if (!progressiveHintUsed.value[currentProgressiveStep.value]) {
    progressiveHintUsed.value[currentProgressiveStep.value] = true;
    terminalOutput.value.push({
      prompt: '!',
      text: 'Hint accessed.',
      type: 'warning'
    });
  }
  // 힌트 패널 토글 (열려있으면 닫고, 닫혀있으면 열기)
  showProgressiveHintPanel.value = !showProgressiveHintPanel.value;
}

// Progressive 솔루션 체크
function checkProgressiveSolution() {
  const stepData = getCurrentStepData();
  if (!stepData) return false;

  const check = stepData.solution_check;
  const code = progressiveStepCodes.value[currentProgressiveStep.value];

  switch (check.type) {
    case 'multi_condition':
      // required_all: 모든 조건이 코드에 포함되어야 함 (AND)
      const hasAllRequired = check.required_all?.every(req => code.includes(req)) ?? true;

      // required_any: 조건 중 하나라도 코드에 포함되어야 함 (OR)
      const hasAnyRequired = check.required_any?.length > 0
        ? check.required_any.some(req => code.includes(req))
        : true;

      // forbidden: 금지된 패턴이 코드에 없어야 함
      const hasNoForbidden = check.forbidden?.every(forbidden => !code.includes(forbidden)) ?? true;

      return hasAllRequired && hasAnyRequired && hasNoForbidden;

    case 'contains':
      return code.includes(check.value);

    case 'notContains':
      return !code.includes(check.value);

    case 'regex':
      // 패턴 일치 여부 확인 (string -> RegExp)
      try {
        const re = new RegExp(check.value, check.flags ?? '');
        return re.test(code);
      } catch {
        return false;
      }

    default:
      return false;
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
        const endTime = Date.now();
        const duration = Math.floor((endTime - stepStartTime.value) / 1000);
        totalDebugTime.value += duration;

        justCompletedStep.value = currentProgressiveStep.value;
        progressiveCompletedSteps.value.push(currentProgressiveStep.value);

        const stepId = `progressive_${currentProgressiveMission.value.id}_step${currentProgressiveStep.value}`;
        if (!gameData.completedProblems.includes(stepId)) {
          gameData.completedProblems.push(stepId);
        }

        gameData.stats.totalBugsFixed++;
        if (!progressiveHintUsed.value[currentProgressiveStep.value]) {
          gameData.stats.perfectClears++;
          evaluationStats.perfectClears++;
        }

        terminalStatus.value = 'success';
        terminalOutput.value.push({
          prompt: '✓',
          text: `Bug ${currentProgressiveStep.value} eliminated! (${duration}s)`,
          type: 'success'
        });

        // 성공 시 힌트 창 닫기
        showProgressiveHintPanel.value = false;

        // 스텝 완료 이펙트 (폭발 효과) - 1초 딜레이 후 표시
        setTimeout(() => {
          showStepComplete.value = true;
          setTimeout(() => {
            showStepComplete.value = false;
            // 3단계: 설명 페이즈로 전환 (채팅으로)
            currentProgressivePhase.value = 'explain';

            // 중앙 팝업 표시 후 대화창으로 날아가는 애니메이션
            const message = `ALERT: Bug ${currentProgressiveStep.value} Neutralized!\n\n${getCurrentStepData()?.title}\n\n버그를 해결하셨군요. 어떤 전략을 사용했는지 기록(Log)을 남겨주세요.`;
            showAlertWithAnimation(message);
          }, 2000);
        }, 1000);

      } else {
        // 실패
        codeSubmitFailCount.value++;
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



// 버그 클릭 이벤트
function onBugClick(step) {
  if (step === currentProgressiveStep.value && currentProgressivePhase.value === 'debug' && !isRunning.value) {
    submitProgressiveStep();
  }
}

// 미션 완료 처리
function completeMission() {
  const missionId = `progressive_${currentProgressiveMission.value.id}`;
  if (!gameData.completedProblems.includes(missionId)) {
    gameData.completedProblems.push(missionId);
  }

  // 보상 계산
  // 보상 계산 (감점 로직 적용)
  const baseScore = 100;
  const hintCount = Object.values(progressiveHintUsed.value).filter(v => v).length;
  const penalty = (quizIncorrectCount.value * 2) + (codeSubmitFailCount.value * 2) + (hintCount * 1);
  
  progressiveMissionXP.value = 100;
  progressiveMissionScore.value = Math.max(0, baseScore - penalty);

  addXP(progressiveMissionXP.value);
  gameData.totalScore += progressiveMissionScore.value;

  showMissionComplete.value = true;
  checkAchievements();
}

// Progressive 미션 종료
function finishProgressiveMission() {
  showMissionComplete.value = false;
  stopBugAnimations();
  router.push('/'); // 메인 페이지로 복귀
}

// 에디터 프레임 참조
const editorFrameRef = ref(null);
const editorBodyRef = ref(null);
const sectionRefs = ref([]);

// 스텝 변경 시 자동 스크롤
watch(currentProgressiveStep, (newStep) => {
  setTimeout(() => {
    const el = sectionRefs.value[newStep - 1];
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, 100);
});

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

// 버그 움직임 애니메이션 (전체 화면 이동으로 수정)
function animateBug(step) {
  if (progressiveCompletedSteps.value.includes(step)) return;

  const time = Date.now() / 1000;
  
  // 전체 화면을 부드럽게 돌아다니도록 노이즈 섞인 움직임 구현
  // baseX, baseY를 시간에 따라 크게 변하게 함
  const movementRadiusX = 35; // 35% radius
  const movementRadiusY = 35; 
  const centerX = 50;
  const centerY = 50;

  const x = centerX + Math.sin(time * 0.5 + step * 10) * movementRadiusX + Math.cos(time * 0.3) * 5;
  const y = centerY + Math.cos(time * 0.4 + step * 7) * movementRadiusY + Math.sin(time * 0.6) * 5;

  bugPositions[step] = {
    left: `${x}%`,
    top: `${y}%`
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

  // 버그 위치 계산 (이펙트가 버그 위치에서 발현되도록)
  const bugLeft = parseFloat(bugPositions[targetStep].left);
  const bugTop = parseFloat(bugPositions[targetStep].top);
  
  // 에디터 프레임 기준 좌표로 변환
  const targetX = (bugLeft / 100) * rect.width;
  const targetY = (bugTop / 100) * rect.height;

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
      
      // 화면 흔들림 효과
      isShaking.value = true;
      setTimeout(() => { isShaking.value = false; }, 500);

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
  router.push('/');
}

function resetGameData() {
  if (confirm('정말로 모든 진행 상황을 초기화하시겠습니까?')) {
    Object.assign(gameData, { ...defaultGameData });
    showStatsPanel.value = false;
  }
}

// 라이프사이클
onMounted(() => {
  // 맵 모드 체크
  if (route.query.missionId) {
    const missionId = route.query.missionId;
    const missionIndex = progressiveProblems.findIndex(m => m.id === missionId);
    
    if (missionIndex !== -1) {
      const mission = progressiveProblems[missionIndex];
      // [수정] 맵에서 미션을 클릭하면 항상 1-1부터 시작하도록 변경하여 순차적 진행 보장
      startProgressiveMission(mission, missionIndex, 1);
    }
  }
});

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
  grid-template-columns: 1fr 2fr; /* 문제창 1/3, 에디터 2/3 */
  gap: 20px;
  padding: 20px;
  width: 100%;
  overflow: hidden;
}

/* 미션 브리핑 패널 */
.mission-briefing-panel {
  display: flex;
  flex-direction: column;
  gap: 15px;
  overflow: hidden;
  min-height: 0;
  max-height: 100%;
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
  color: #ffffff;
  line-height: 1.6;
  font-size: 1.1rem;
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
  flex: 1;
  min-height: 0;
  overflow: hidden;
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
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #1a202c;
  border-bottom: 1px solid var(--border-color);
}

.editor-top-buttons {
  display: flex;
  gap: 10px;
}

.editor-btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-family: 'Orbitron', monospace;
  font-size: 0.85rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid;
}

.editor-btn.reset-btn {
  background: transparent;
  border-color: #718096;
  color: #718096;
}

.editor-btn.reset-btn:hover {
  background: #718096;
  color: #000;
}

.editor-btn.submit-btn {
  background: var(--neon-green);
  border-color: var(--neon-green);
  color: #000;
}

.editor-btn.submit-btn:hover:not(:disabled) {
  background: #00e67a;
  box-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
}

.editor-btn.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  gap: 60px;
  padding: 40px 0;
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
  filter: blur(6px);
  opacity: 0.4;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 16px;
  line-height: 1.8;
  color: #718096;
  margin: 0;
  white-space: pre-wrap;
}

/* 코드 에디터 래퍼 */
.code-editor-wrapper {
  display: flex;
  min-height: 350px;
}

/* Monaco Editor 스타일 */
.monaco-active-wrapper {
  display: block;
  height: 350px;
  border: 1px solid rgba(0, 255, 136, 0.3);
  border-radius: 8px;
  overflow: hidden;
}

.bughunt-monaco-editor {
  width: 100%;
  height: 100%;
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
  font-size: 16px;
  line-height: 1.8;
  color: #4b5563;
  padding-right: 10px;
}

/* 게임 스타일 코드 */
.game-code {
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 18px;
  line-height: 1.8;
  letter-spacing: 0.8px;
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

/* Terminal styles removed */

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
  z-index: 500;
}

.hint-panel {
  background: var(--panel-bg);
  border: 4px solid var(--neon-yellow);
  border-radius: 20px;
  max-width: 600px;
  width: 95%;
  height: 40vh;
  min-height: 300px;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 0 50px rgba(255, 255, 0, 0.3), inset 0 0 20px rgba(255, 255, 0, 0.1);
  animation: modalPop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modalPop {
  from { transform: scale(0.9); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.hint-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 20px;
  border-bottom: 2px solid var(--border-color);
  font-family: 'Orbitron', monospace;
  color: var(--neon-yellow);
  flex-shrink: 0;
}

.hint-header span:not(.close-btn) {
  font-size: 1rem;
  letter-spacing: 2px;
  text-shadow: 0 0 10px var(--neon-yellow);
}

.hint-content {
  padding: 15px 20px;
  line-height: 1.6;
  color: #f0f0f0;
  overflow-y: auto;
  font-size: 1rem;
  flex: 1;
}

.hint-content::-webkit-scrollbar {
  width: 12px;
}

.hint-content::-webkit-scrollbar-thumb {
  background: var(--neon-yellow);
  border-radius: 3px;
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
/* 퀴즈 오버레이 */
.quiz-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 150;
  backdrop-filter: blur(8px);
}

.quiz-modal {
  background: var(--panel-bg);
  width: 90%;
  max-width: 600px;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 0 40px rgba(0, 243, 255, 0.2);
}

.neon-border {
  border: 2px solid var(--neon-cyan);
  box-shadow: 0 0 15px var(--neon-cyan), inset 0 0 10px rgba(0, 243, 255, 0.3);
}

.phase-badge {
  display: inline-block;
  background: var(--neon-cyan);
  color: #000;
  padding: 4px 12px;
  border-radius: 4px;
  font-family: 'Orbitron', monospace;
  font-size: 0.75rem;
  font-weight: bold;
  margin-bottom: 15px;
}

.quiz-header h3 {
  font-family: 'Orbitron', monospace;
  font-size: 1.8rem;
  color: #fff;
  margin-bottom: 25px;
}

.quiz-question p {
  font-size: 1.15rem;
  line-height: 1.6;
  color: #e0e0e0;
  margin-bottom: 30px;
}

.quiz-options {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.quiz-option-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 18px 25px;
  border-radius: 12px;
  color: #fff;
  text-align: left;
  font-size: 1.05rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 20px;
}

.quiz-option-btn:hover {
  background: rgba(0, 243, 255, 0.1);
  border-color: var(--neon-cyan);
}

.quiz-option-btn.selected {
  background: rgba(0, 243, 255, 0.2);
  border-color: var(--neon-cyan);
  box-shadow: 0 0 15px rgba(0, 243, 255, 0.3);
}

.option-num {
  font-family: 'Orbitron', monospace;
  width: 30px;
  height: 30px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  color: var(--neon-cyan);
}

.quiz-footer {
  margin-top: 40px;
  text-align: center;
}

.quiz-submit-btn {
  width: 100%;
  padding: 18px;
  background: var(--neon-cyan);
  color: #000;
  border: none;
  border-radius: 12px;
  font-family: 'Orbitron', monospace;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.quiz-submit-btn:disabled {
  background: #2d3748;
  color: #718096;
  cursor: not-allowed;
}

.quiz-feedback {
  margin-top: 20px;
  font-weight: bold;
  font-size: 1.1rem;
}

.quiz-feedback.success { color: var(--neon-green); }
.quiz-feedback.error { color: var(--neon-red); }

/* 설명 영역 */
.explain-action-box {
  padding: 20px;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 12px;
  border: 1px solid var(--neon-magenta);
  animation: slideUp 0.3s ease-out;
}

.explain-title {
  font-family: 'Orbitron', monospace;
  color: var(--neon-magenta);
  margin-bottom: 15px;
  font-size: 0.9rem;
}

.explain-textarea {
  width: 100%;
  height: 120px;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 0, 255, 0.3);
  border-radius: 8px;
  padding: 15px;
  color: #fff;
  font-family: inherit;
  font-size: 0.95rem;
  resize: none;
  margin-bottom: 15px;
  outline: none;
}

.explain-textarea:focus {
  border-color: var(--neon-magenta);
  box-shadow: 0 0 10px rgba(255, 0, 255, 0.2);
}

.next-step-btn {
  width: 100%;
  border-color: var(--neon-magenta);
  color: var(--neon-magenta);
}

.next-step-btn:hover:not(:disabled) {
  background: var(--neon-magenta);
  color: #fff;
}

/* 평가 화면 */
.evaluation-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
}

.evaluation-content {
  margin-top: 40px;
  animation: fadeIn 0.8s ease-out;
}

.report-card {
  background: var(--panel-bg);
  padding: 50px;
  border-radius: 24px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 50px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.05);
  padding-bottom: 30px;
}

.project-info h2 {
  font-family: 'Orbitron', monospace;
  font-size: 2.2rem;
  margin-top: 15px;
  color: #fff;
}

.id-badge {
  background: var(--neon-green);
  color: #000;
  padding: 5px 15px;
  border-radius: 20px;
  font-weight: bold;
  font-family: 'Orbitron', monospace;
  font-size: 0.9rem;
}

.score-item {
  text-align: right;
}

.score-item .label {
  display: block;
  font-family: 'Orbitron', monospace;
  font-size: 0.9rem;
  color: #a0aec0;
}

.score-item .value {
  font-family: 'Orbitron', monospace;
  font-size: 3.5rem;
  color: var(--neon-yellow);
  text-shadow: 0 0 30px rgba(255, 255, 0, 0.5);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 25px;
  margin-bottom: 50px;
}

.stat-box {
  background: rgba(0, 0, 0, 0.3);
  padding: 30px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-details .label {
  display: block;
  font-size: 0.85rem;
  color: #718096;
  margin-bottom: 5px;
}

.stat-details .value {
  font-family: 'Orbitron', monospace;
  font-size: 1.8rem;
  font-weight: bold;
}

.text-cyan { color: var(--neon-cyan); }
.text-magenta { color: var(--neon-magenta); }
.text-green { color: var(--neon-green); }

.explanations-list {
  margin-bottom: 50px;
}

.list-title {
  font-family: 'Orbitron', monospace;
  font-size: 1.1rem;
  color: #fff;
  margin-bottom: 25px;
  border-left: 4px solid var(--neon-cyan);
  padding-left: 15px;
}

.eval-step-box {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  padding: 25px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.eval-step-box .step-header {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
  font-family: 'Orbitron', monospace;
}

.eval-step-box .step-num {
  background: none;
  width: auto;
  height: auto;
  border-radius: 0;
  color: var(--neon-magenta);
  font-size: 1rem;
  font-weight: bold;
}

.eval-step-box .step-title {
  color: #e0e0e0;
}

.step-explanation .label {
  font-size: 0.85rem;
  color: #718096;
  margin-bottom: 8px;
  display: block;
}

.step-explanation p {
  line-height: 1.7;
  color: #a0aec0;
  font-size: 1rem;
}

.step-feedback {
  margin-top: 20px;
  padding: 15px;
  background: rgba(0, 255, 255, 0.05);
  border-left: 3px solid var(--neon-cyan);
  border-radius: 8px;
}

.step-feedback .feedback-label {
  font-size: 0.85rem;
  color: var(--neon-cyan);
  font-weight: bold;
  margin-bottom: 10px;
  display: block;
  font-family: 'Orbitron', monospace;
}

.step-feedback .feedback-text {
  line-height: 1.8;
  color: #e0e0e0;
  font-size: 0.95rem;
  margin: 0;
}

.evaluation-actions {
  text-align: center;
}

.back-to-menu-btn {
  padding: 20px 60px;
  background: var(--neon-cyan);
  color: #000;
  border: none;
  font-family: 'Orbitron', monospace;
  font-size: 1.2rem;
  font-weight: bold;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 10px 30px rgba(0, 243, 255, 0.3);
}

.back-to-menu-btn:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 243, 255, 0.5);
}

.code-bug.clickable {
  cursor: crosshair;
}

.code-bug.clickable:hover .bug-emoji {
  filter: drop-shadow(0 0 25px var(--neon-red));
  transform: scale(1.3);
}

/* AI 리포트 섹션 */
.ai-report-section {
  background: rgba(0, 243, 255, 0.03);
  padding: 30px;
  border-radius: 16px;
  margin-bottom: 40px;
  position: relative;
  overflow: hidden;
}

.report-section-title {
  font-family: 'Orbitron', monospace;
  font-size: 1.1rem;
  color: var(--neon-cyan);
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-loading {
  text-align: center;
  padding: 40px 0;
}

.pulse-loader {
  width: 40px;
  height: 40px;
  background: var(--neon-cyan);
  border-radius: 50%;
  margin: 0 auto 20px;
  animation: pulse 1.5s ease-in-out infinite;
  box-shadow: 0 0 20px var(--neon-cyan);
}

@keyframes pulse {
  0% { transform: scale(0.8); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(0.8); opacity: 0.5; }
}

.ai-score-row {
  display: grid;
  grid-template-columns: 150px 1fr;
  gap: 30px;
  margin-bottom: 30px;
  align-items: center;
}

.ai-overall-score {
  text-align: center;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  padding-right: 30px;
}

.ai-overall-score .score-label {
  display: block;
  font-size: 0.75rem;
  color: #718096;
  margin-bottom: 10px;
}

.ai-overall-score .score-value {
  font-family: 'Orbitron', monospace;
  font-size: 3rem;
  color: var(--neon-cyan);
  text-shadow: 0 0 15px var(--neon-cyan);
}

.ai-summary p {
  line-height: 1.7;
  color: #e0e0e0;
  font-size: 1.05rem;
}

.pros-cons-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.pros-box, .cons-box {
  padding: 20px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.2);
}

.pros-box { border-left: 4px solid var(--neon-green); }
.cons-box { border-left: 4px solid var(--neon-red); }

.box-label {
  font-family: 'Orbitron', monospace;
  font-size: 0.8rem;
  margin-bottom: 15px;
}

.pros-box .box-label { color: var(--neon-green); }
.cons-box .box-label { color: var(--neon-red); }

.pros-cons-grid ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.pros-cons-grid li {
  font-size: 0.95rem;
  color: #a0aec0;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.pros-box li::before { content: '✓'; color: var(--neon-green); }
.cons-box li::before { content: '•'; color: var(--neon-red); }

/* 디버깅 사고 평가 스타일 */
.thinking-eval-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 25px;
}

.eval-card {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.eval-card:hover {
  border-color: rgba(0, 255, 255, 0.3);
  transform: translateY(-2px);
}

.eval-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.eval-icon {
  font-size: 1.3rem;
}

.eval-title {
  font-family: 'Orbitron', monospace;
  font-size: 0.85rem;
  color: #a0aec0;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.eval-card-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

/* 통과/탈락 배지 */
.pass-badge {
  font-family: 'Orbitron', monospace;
  font-size: 1.5rem;
  font-weight: bold;
  padding: 10px 25px;
  border-radius: 8px;
}

.pass-badge.pass {
  color: var(--neon-green);
  background: rgba(0, 255, 100, 0.1);
  border: 2px solid var(--neon-green);
  text-shadow: 0 0 10px var(--neon-green);
}

.pass-badge.fail {
  color: var(--neon-red);
  background: rgba(255, 0, 100, 0.1);
  border: 2px solid var(--neon-red);
  text-shadow: 0 0 10px var(--neon-red);
}

/* 위험도 게이지 */
.risk-gauge {
  width: 100%;
  height: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  overflow: hidden;
}

.risk-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 1s ease-out;
}

.risk-fill.low {
  background: linear-gradient(90deg, #00ff64, #00d454);
  box-shadow: 0 0 10px rgba(0, 255, 100, 0.5);
}

.risk-fill.medium {
  background: linear-gradient(90deg, #ffc107, #ff9800);
  box-shadow: 0 0 10px rgba(255, 193, 7, 0.5);
}

.risk-fill.high {
  background: linear-gradient(90deg, #ff4757, #ff0044);
  box-shadow: 0 0 10px rgba(255, 71, 87, 0.5);
}

.risk-value {
  font-family: 'Orbitron', monospace;
  font-size: 1.1rem;
  color: #e0e0e0;
}

/* 사고력 점수 */
.thinking-score-value {
  font-family: 'Orbitron', monospace;
  font-size: 3rem;
  color: var(--neon-cyan);
  text-shadow: 0 0 15px var(--neon-cyan);
}

.thinking-score-max {
  font-family: 'Orbitron', monospace;
  font-size: 1.2rem;
  color: #718096;
}

/* 총평 박스 */
.summary-box {
  background: rgba(0, 255, 255, 0.05);
  border: 1px solid rgba(0, 255, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
}

.summary-label {
  font-family: 'Orbitron', monospace;
  font-size: 0.85rem;
  color: var(--neon-cyan);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.summary-text {
  font-size: 1.1rem;
  line-height: 1.7;
  color: #e0e0e0;
  margin: 0;
}

/* 반응형 처리 */
@media (max-width: 900px) {
  .thinking-eval-grid {
    grid-template-columns: 1fr;
  }
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* --- 화면 흔들림 효과 --- */
@keyframes shake {
  0% { transform: translate(1px, 1px) rotate(0deg); }
  20% { transform: translate(-3px, 0px) rotate(1deg); }
  40% { transform: translate(1px, -1px) rotate(1deg); }
  60% { transform: translate(-1px, 1px) rotate(-1deg); }
  80% { transform: translate(-1px, -1px) rotate(1deg); }
  100% { transform: translate(1px, 2px) rotate(0deg); }
}

.shake-effect {
  animation: shake 0.5s;
}

/* --- PHASE 3: EXPLAIN 팝업 --- */
.explain-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(5px);
}

.explain-popup-content {
  background: var(--panel-bg);
  border: 3px solid var(--neon-cyan);
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 0 50px rgba(0, 243, 255, 0.4), inset 0 0 30px rgba(0, 243, 255, 0.1);
  animation: explainPopIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes explainPopIn {
  from { transform: scale(0.8) translateY(30px); opacity: 0; }
  to { transform: scale(1) translateY(0); opacity: 1; }
}

.explain-popup-header {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px 30px;
  border-bottom: 2px solid var(--border-color);
  background: linear-gradient(180deg, rgba(0, 243, 255, 0.15) 0%, transparent 100%);
  border-radius: 17px 17px 0 0;
}

.explain-icon {
  font-size: 2rem;
}

.explain-title-text {
  font-family: 'Orbitron', monospace;
  font-size: 1.5rem;
  color: var(--neon-cyan);
  text-shadow: 0 0 15px var(--neon-cyan);
  letter-spacing: 2px;
}

.explain-popup-body {
  padding: 30px;
}

.explain-prompt {
  color: #e0e0e0;
  font-size: 1.1rem;
  margin-bottom: 20px;
  text-align: center;
}

.explain-popup-textarea {
  width: 100%;
  height: 150px;
  background: rgba(0, 0, 0, 0.4);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 15px;
  color: #fff;
  font-size: 1rem;
  font-family: inherit;
  resize: none;
  transition: all 0.3s ease;
}

.explain-popup-textarea:focus {
  outline: none;
  border-color: var(--neon-cyan);
  box-shadow: 0 0 15px rgba(0, 243, 255, 0.3);
}

.explain-popup-textarea::placeholder {
  color: #666;
}

.explain-popup-footer {
  padding: 20px 30px;
  border-top: 2px solid var(--border-color);
  display: flex;
  justify-content: center;
}

.explain-submit-btn {
  background: linear-gradient(135deg, var(--neon-cyan), #0088ff);
  color: #fff;
  border: none;
  padding: 15px 40px;
  border-radius: 12px;
  font-family: 'Orbitron', monospace;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  box-shadow: 0 4px 20px rgba(0, 243, 255, 0.4);
}

.explain-submit-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 6px 30px rgba(0, 243, 255, 0.6);
}

.explain-submit-btn:disabled {
  background: #444;
  cursor: not-allowed;
  box-shadow: none;
}

/* Explain 팝업 트랜지션 */
.explainPopup-enter-active,
.explainPopup-leave-active {
  transition: opacity 0.3s ease;
}

.explainPopup-enter-from,
.explainPopup-leave-to {
  opacity: 0;
}

/* 대기 박스 (사이드바 내) */
.explain-waiting-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px;
  background: rgba(0, 243, 255, 0.1);
  border: 2px solid var(--neon-cyan);
  border-radius: 12px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.waiting-icon {
  font-size: 2rem;
}

.waiting-text {
  color: var(--neon-cyan);
  font-family: 'Orbitron', monospace;
  font-size: 0.9rem;
  text-shadow: 0 0 10px var(--neon-cyan);
}

/* --- HINT DUCK UI --- */
.hint-duck-container {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  z-index: 200;
  pointer-events: none;
}

.hint-duck-img {
  width: 100px;
  height: auto;
  filter: drop-shadow(0 0 15px rgba(0, 243, 255, 0.4));
  animation: duckFloat 3s ease-in-out infinite;
}

@keyframes duckFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-10px) rotate(5deg); }
}

.hint-speech-bubble {
  background: rgba(15, 23, 42, 0.95);
  border: 2px solid var(--neon-cyan);
  border-radius: 16px;
  padding: 15px 20px;
  max-width: 280px;
  margin-bottom: 10px;
  position: relative;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), 0 0 15px rgba(0, 243, 255, 0.2);
  pointer-events: auto;
}

.hint-speech-bubble::after {
  content: '';
  position: absolute;
  bottom: -10px;
  right: 30px;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-top: 10px solid var(--neon-cyan);
}

.bubble-header {
  font-family: 'Orbitron', monospace;
  font-size: 0.8rem;
  color: var(--neon-cyan);
  font-weight: bold;
  margin-bottom: 8px;
  border-bottom: 1px solid rgba(0, 243, 255, 0.2);
  padding-bottom: 4px;
}

.bubble-content {
  font-size: 0.95rem;
  line-height: 1.5;
  color: #fff;
  font-family: 'Noto Sans KR', sans-serif;
}

/* Duck Pop Transition */
.duck-pop-enter-active {
  animation: duckPopIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.duck-pop-leave-active {
  animation: duckPopIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) reverse;
}

@keyframes duckPopIn {
  from { transform: scale(0.5) translateY(50px); opacity: 0; }
  to { transform: scale(1) translateY(0); opacity: 1; }
}

/* Penalty Stats */
.penalty-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: rgba(255, 0, 0, 0.1);
  padding: 15px;
  border-radius: 8px;
  margin-top: 15px;
  border-left: 2px solid var(--neon-red);
  min-width: 200px;
}

.penalty-item {
  display: flex;
  justify-content: space-between;
  gap: 15px;
  font-size: 0.85rem;
  color: #fab1b1;
}

.p-label {
  font-family: 'Orbitron', monospace;
  letter-spacing: 0.5px;
  font-size: 0.75rem;
}

.p-value {
  color: var(--neon-red);
  font-family: 'Orbitron', monospace;
  font-weight: bold;
}
</style>
