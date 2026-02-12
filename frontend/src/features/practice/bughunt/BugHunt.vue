<template>
  <div class="debug-practice-page" :class="{ 'shake-effect': isShaking }">
    <!-- 별 배경 -->
    <div class="stars-container">
      <div class="stars"></div>
      <div class="stars2"></div>
      <div class="stars3"></div>
    </div>
    <!-- 성운 오버레이 -->
    <div class="nebula-overlay"></div>

    <!-- 데이터 로딩 오버레이 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p>데이터 로딩 중...</p>
      </div>
    </div>

    <!-- 에러 오버레이 -->
    <div v-if="error && !loading" class="error-overlay">
      <div class="error-content">
        <div class="error-icon">⚠️</div>
        <p>{{ error }}</p>
        <button @click="fetchProgressiveProblems" class="retry-btn">다시 시도</button>
      </div>
    </div>

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
      <!-- 날아가는 먹은 지렁이 애니메이션 - 제거됨 -->

      <!-- 헤더 -->
      <header class="header compact progressive-header">
        <div class="header-left">
          <h1>🎯 {{ currentProgressiveMission?.stage_title }}</h1>
        </div>
        <div class="header-center">
          <!-- 버그 상태 표시 (3마리) -->
          <div class="bugs-status">
            <div
              v-for="step in totalStepsComputed"
              :key="step"
              class="bug-status-item"
              :class="{ dead: progressiveCompletedSteps.includes(step), active: step === currentProgressiveStep }"
            >
              <span class="bug-icon" v-if="progressiveCompletedSteps.includes(step)">✅</span>
              <svg v-else width="24" height="24" viewBox="0 0 40 20" class="bug-icon-svg">
                <path d="M5,10 Q10,7 15,10 Q20,13 25,10 Q30,7 35,10"
                      stroke="#FFB6C1"
                      stroke-width="5"
                      stroke-linecap="round"
                      fill="none"/>
                <circle cx="35" cy="10" r="2.5" fill="#FFB6C1"/>
              </svg>
              <span class="bug-label">{{ getStepData(step)?.bug_type }}</span>
            </div>
          </div>
        </div>
        <div class="header-right">
          <div class="shake-counter">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="shake-icon">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
            </svg>
            <span class="shake-count-text">{{ authStore.userProteinShakes }}</span>
          </div>
          <div class="remaining-bugs">
            🪱 {{ totalStepsComputed - progressiveCompletedSteps.length }} worms left
          </div>
          <button class="editor-btn tutorial-btn" @click="startTutorial" style="margin-right: 10px;">
            📖 튜토리얼
          </button>
          <button class="back-btn" @click="confirmExit">EXIT</button>
        </div>
      </header>

      <div class="progressive-main-layout">
        <!-- 좌측: 미션 브리핑 -->
        <aside class="left-panel-wrapper">
          <div class="left-panel-body">
            <div class="panel-box scenario-box">
              <div class="panel-title">📋 MISSION BRIEFING</div>
              <p class="scenario-text">{{ currentProgressiveMission?.scenario }}</p>
            </div>

            <!-- 단서창 (문제 관련 로그/힌트 표시) - 항상 표시 -->
            <div class="clue-panel neon-border" :class="{ 'attention-pulse': showAttentionEffect }">
              <!-- 로그 항상 표시 -->
              <div class="clue-header">
                <span class="clue-icon">🔍</span>
                <span class="clue-title">CLUES & LOGS</span>
              </div>
              <div class="clue-content" ref="clueContentRef">
                <div
                  v-for="(clue, idx) in clueMessages"
                  :key="idx"
                  class="clue-item"
                  :class="{
                    'new-clue': clue.isNew,
                    'clue-success': clue.type === 'SUCCESS',
                    'clue-error': clue.type === 'ERROR'
                  }"
                >
                  <span class="clue-badge" :class="`badge-${clue.type.toLowerCase()}`">{{ clue.type }}</span>
                  <span class="clue-text">{{ clue.text }}</span>
                </div>
              </div>
            </div>
          </div>
        </aside>

        <!-- ========== TUTORIAL MODE ========== -->
        <main v-if="currentStageMode === 'tutorial'" class="full-code-editor tutorial-mode" ref="editorFrameRef">
          <!-- 3마리 지렁이 SVG 애니메이션 -->
          <div class="bugs-container">
            <div
              v-for="step in totalStepsComputed"
              :key="'bug-' + step"
              class="code-bug"
              :ref="el => (bugRefs[step] = el)"
              :class="{
                dead: progressiveCompletedSteps.includes(step),
                eating: !progressiveCompletedSteps.includes(step),
                targeted: step === currentProgressiveStep && isRunning,
                clickable: step === currentProgressiveStep && currentProgressivePhase === 'debug'
              }"
              :style="bugPositions[step]"
              @click="onBugClick(step)"
            >
              <!-- 지렁이 SVG (더 리얼하게) -->
              <svg v-if="!progressiveCompletedSteps.includes(step)"
                   width="60" height="60" viewBox="0 0 80 40"
                   class="worm-svg">
                <!-- 지렁이 몸통 (세그먼트화된 구조) -->
                <defs>
                  <linearGradient id="wormGradientTutorial" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#FFE4E1;stop-opacity:1" />
                    <stop offset="50%" style="stop-color:#FFB6C1;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#FFC0CB;stop-opacity:1" />
                  </linearGradient>
                </defs>

                <!-- 메인 몸통 -->
                <path class="worm-body-main"
                      d="M10,20 Q20,15 30,20 Q40,25 50,20 Q60,15 70,20"
                      stroke="url(#wormGradientTutorial)"
                      stroke-width="10"
                      stroke-linecap="round"
                      fill="none">
                  <animate attributeName="d"
                           dur="2s"
                           repeatCount="indefinite"
                           values="M10,20 Q20,15 30,20 Q40,25 50,20 Q60,15 70,20;
                                   M10,20 Q20,25 30,20 Q40,15 50,20 Q60,25 70,20;
                                   M10,20 Q20,15 30,20 Q40,25 50,20 Q60,15 70,20"/>
                </path>

                <!-- 세그먼트 링 -->
                <ellipse cx="18" cy="20" rx="2" ry="4" fill="#FFB6C1" opacity="0.8">
                  <animate attributeName="cy" dur="2s" repeatCount="indefinite"
                           values="20;17;20;23;20"/>
                </ellipse>
                <ellipse cx="30" cy="20" rx="2" ry="4" fill="#FFB6C1" opacity="0.8">
                  <animate attributeName="cy" dur="2s" repeatCount="indefinite"
                           values="20;23;20;17;20"/>
                </ellipse>
                <ellipse cx="42" cy="20" rx="2" ry="4" fill="#FFB6C1" opacity="0.8">
                  <animate attributeName="cy" dur="2s" repeatCount="indefinite"
                           values="20;17;20;23;20"/>
                </ellipse>
                <ellipse cx="54" cy="20" rx="2" ry="4" fill="#FFB6C1" opacity="0.8">
                  <animate attributeName="cy" dur="2s" repeatCount="indefinite"
                           values="20;23;20;17;20"/>
                </ellipse>

                <!-- 머리 부분 -->
                <circle cx="70" cy="20" r="5" fill="#FFB6C1"/>
                <!-- 눈 (작게) -->
                <circle cx="68" cy="18" r="1.5" fill="#000">
                  <animate attributeName="r"
                           dur="3s"
                           repeatCount="indefinite"
                           values="1.5;0.3;1.5;1.5;1.5"/>
                </circle>
              </svg>
            </div>
          </div>

          <!-- [2026-02-03] 메인 화면 걷는 오리 PNG 교체 (v-show로 변경하여 부드러운 전환) -->
          <div v-show="!showBullet" class="walking-duck" :style="walkingDuckStyle">
            <!-- [2026-02-03] 에셋 임포트 방식으로 안정적인 이미지 로딩 보장 -->
            <img v-if="isEating" :src="duckEating" class="duck-walking-img eating-motion" alt="Eating Duck">
            <img v-else-if="isSad" :src="duckSad" class="duck-walking-img sad-motion" alt="Sad Duck">
            <img v-else :src="duckIdle" class="duck-walking-img" alt="Walking Duck Bird">
          </div>

          <!-- [2026-02-03] 오리가 날아가서 도착 지점에서 지렁이를 먹는 동작 (v-show로 변경하여 부드러운 전환) -->
          <div v-show="showBullet" class="bullet duck-flying cinematic" :style="bulletStyle">
            <img :src="isEating ? duckEating : (isSad ? duckSad : duckFlying)"
                 class="duck-flying-img"
                 :class="{ 'eating-at-target': isEating, 'sad-at-target': isSad }"
                 alt="Flying/Eating/Sad Duck">
            <!-- 속도선 효과 (비행 중에만 표시) -->
            <div v-if="!isEating && !isSad" class="speed-lines">
              <span v-for="n in 5" :key="n" class="speed-line"></span>
            </div>
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
              <span class="miss-text">MISSED!</span>
            </div>
          </transition>

          <!-- 에디터 헤더: 튜토리얼 페이즈 표시 -->
          <div class="editor-header">
            <div class="code-progress">
              <span class="progress-text">TUTORIAL</span>
            </div>
            <div class="tutorial-phase-indicator">
              <span :class="{ active: tutorialPhase === 'explore' }">1. EXPLORE</span>
              <span class="phase-arrow">→</span>
              <span :class="{ active: tutorialPhase === 'fix' }">2. FIX</span>
              <span class="phase-arrow">→</span>
              <span :class="{ active: tutorialPhase === 'review' }">3. REVIEW</span>
            </div>
          </div>

          <div class="editor-body">
            <!-- Phase A+B: Explore/Fix - 코드 뷰어 유지 + 코드 아래 객관식 -->
            <div v-if="tutorialPhase === 'explore' || tutorialPhase === 'fix'" class="tutorial-explore tutorial-combined">
              <div class="tutorial-instruction">
                <template v-if="tutorialPhase === 'explore'">
                  코드에서 버그가 있는 줄을 찾아 클릭하세요!
                </template>
                <template v-else>
                  아래 보기에서 올바른 수정 방법을 선택하세요!
                </template>
              </div>
              <div class="tutorial-code-viewer">
                <div
                  v-for="(line, idx) in (getCurrentStepData()?.buggy_code?.split('\n') || [])"
                  :key="idx"
                  class="code-line"
                  :class="{
                    'hovered': hoveredLine === idx + 1,
                    'selected-correct': selectedBugLine === idx + 1 && bugLineCorrect,
                    'selected-wrong': selectedBugLine === idx + 1 && !bugLineCorrect && selectedBugLine !== null
                  }"
                  @mouseenter="tutorialPhase === 'explore' ? (hoveredLine = idx + 1) : null"
                  @mouseleave="hoveredLine = null"
                  @click="handleTutorialLineClick(idx + 1)"
                >
                  <span class="line-number">{{ idx + 1 }}</span>
                  <pre class="line-content">{{ line }}</pre>
                </div>
              </div>

              <div v-if="tutorialPhase === 'fix'" class="tutorial-fix-inline" ref="tutorialFixRef">
                <div class="tutorial-coaching">
                  {{ getCurrentStepData()?.coaching }}
                </div>
                <div class="choice-grid inline-four">
                  <button
                    v-for="(choice, idx) in getCurrentStepData()?.choices"
                    :key="idx"
                    class="choice-btn"
                    :class="{
                      'selected': !choiceSubmitted && selectedChoice === idx,
                      'correct': choiceSubmitted && tutorialChoiceCorrect && choice.correct,
                      'wrong': choiceSubmitted && selectedChoice === idx && !choice.correct
                    }"
                    @click="handleTutorialChoice(idx)"
                    :disabled="choiceSubmitted"
                  >
                    <code>{{ choice.label }}</code>
                  </button>
                </div>
                <button
                  v-if="!choiceSubmitted"
                  class="editor-btn submit-btn"
                  @click="submitTutorialChoice"
                  :disabled="selectedChoice === null"
                >
                  SUBMIT
                </button>
              </div>
            </div>

            <!-- Phase C: Review - 리뷰 카드 -->
            <div v-else-if="tutorialPhase === 'review'" class="tutorial-review">
              <div class="review-card neon-border">
                <div class="review-header">STAGE CLEAR!</div>
                <h3>{{ getCurrentStepData()?.review_card?.title }}</h3>
                <p class="review-explanation">{{ getCurrentStepData()?.review_card?.explanation }}</p>
                <pre class="review-pattern">{{ getCurrentStepData()?.review_card?.correct_pattern }}</pre>
              </div>
              <button class="stage-clear-btn" @click="completeTutorialStage">
                {{ currentProgressiveStep < totalStepsComputed ? '다음 단계' : 'STAGE CLEAR' }}
              </button>
            </div>
          </div>
        </main>

        <!-- ========== GUIDED MODE ========== -->
        <main v-else-if="currentStageMode === 'guided'" class="full-code-editor guided-mode" ref="editorFrameRef">
          <!-- 3마리 지렁이 SVG 애니메이션 (tutorial과 동일) -->
          <div class="bugs-container">
            <div
              v-for="step in totalStepsComputed"
              :key="'bug-' + step"
              class="code-bug"
              :ref="el => (bugRefs[step] = el)"
              :class="{
                dead: progressiveCompletedSteps.includes(step),
                eating: !progressiveCompletedSteps.includes(step),
                targeted: step === currentProgressiveStep && isRunning,
                clickable: step === currentProgressiveStep && currentProgressivePhase === 'debug'
              }"
              :style="bugPositions[step]"
              @click="onBugClick(step)"
            >
              <!-- 지렁이 SVG -->
              <svg v-if="!progressiveCompletedSteps.includes(step)"
                   width="60" height="60" viewBox="0 0 80 40"
                   class="worm-svg">
                <defs>
                  <linearGradient id="wormGradientGuided" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#FFE4E1;stop-opacity:1" />
                    <stop offset="50%" style="stop-color:#FFB6C1;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#FFC0CB;stop-opacity:1" />
                  </linearGradient>
                </defs>
                <path class="worm-body-main"
                      d="M10,20 Q20,15 30,20 Q40,25 50,20 Q60,15 70,20"
                      stroke="url(#wormGradientGuided)"
                      stroke-width="10"
                      stroke-linecap="round"
                      fill="none">
                  <animate attributeName="d"
                           dur="2s"
                           repeatCount="indefinite"
                           values="M10,20 Q20,15 30,20 Q40,25 50,20 Q60,15 70,20;
                                   M10,20 Q20,25 30,20 Q40,15 50,20 Q60,25 70,20;
                                   M10,20 Q20,15 30,20 Q40,25 50,20 Q60,15 70,20"/>
                </path>
                <ellipse cx="18" cy="20" rx="2" ry="4" fill="#FFB6C1" opacity="0.8">
                  <animate attributeName="cy" dur="2s" repeatCount="indefinite"
                           values="20;17;20;23;20"/>
                </ellipse>
                <ellipse cx="30" cy="20" rx="2" ry="4" fill="#FFB6C1" opacity="0.8">
                  <animate attributeName="cy" dur="2s" repeatCount="indefinite"
                           values="20;23;20;17;20"/>
                </ellipse>
                <ellipse cx="42" cy="20" rx="2" ry="4" fill="#FFB6C1" opacity="0.8">
                  <animate attributeName="cy" dur="2s" repeatCount="indefinite"
                           values="20;17;20;23;20"/>
                </ellipse>
                <ellipse cx="54" cy="20" rx="2" ry="4" fill="#FFB6C1" opacity="0.8">
                  <animate attributeName="cy" dur="2s" repeatCount="indefinite"
                           values="20;23;20;17;20"/>
                </ellipse>
                <circle cx="70" cy="20" r="5" fill="#FFB6C1"/>
                <circle cx="68" cy="18" r="1.5" fill="#000">
                  <animate attributeName="r"
                           dur="3s"
                           repeatCount="indefinite"
                           values="1.5;0.3;1.5;1.5;1.5"/>
                </circle>
              </svg>
            </div>
          </div>

          <!-- 걷는 오리 -->
          <div v-show="!showBullet" class="walking-duck" :style="walkingDuckStyle">
            <img v-if="isEating" :src="duckEating" class="duck-walking-img eating-motion" alt="Eating Duck">
            <img v-else-if="isSad" :src="duckSad" class="duck-walking-img sad-motion" alt="Sad Duck">
            <img v-else :src="duckIdle" class="duck-walking-img" alt="Walking Duck Bird">
          </div>

          <!-- 날아가는 오리 -->
          <div v-show="showBullet" class="bullet duck-flying cinematic" :style="bulletStyle">
            <img :src="isEating ? duckEating : (isSad ? duckSad : duckFlying)"
                 class="duck-flying-img"
                 :class="{ 'eating-at-target': isEating, 'sad-at-target': isSad }"
                 alt="Flying/Eating/Sad Duck">
            <div v-if="!isEating && !isSad" class="speed-lines">
              <span v-for="n in 5" :key="n" class="speed-line"></span>
            </div>
          </div>

          <transition name="explode">
            <div v-if="showHitEffect" class="hit-effect" :style="hitEffectStyle">
              <span class="hit-text">{{ hitEffectText }}</span>
              <div class="explosion-particles">
                <span v-for="n in 8" :key="n" class="particle" :style="`--angle: ${n * 45}deg`"></span>
              </div>
            </div>
          </transition>

          <transition name="miss">
            <div v-if="showMissEffect" class="miss-effect" :style="missEffectStyle">
              <span class="miss-text">MISSED!</span>
            </div>
          </transition>

          <div class="editor-header">
            <div class="code-progress">
              <span class="progress-text">{{ progressiveCompletedSteps.length }}/{{ totalStepsComputed }} BLANKS FILLED</span>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: (progressiveCompletedSteps.length / totalStepsComputed * 100) + '%' }"></div>
              </div>
            </div>
            <div class="editor-top-buttons">
              <button class="editor-btn hint-btn" @click="showProgressiveHint">HINT</button>
            </div>
          </div>

          <div class="editor-body">
            <div class="guided-step-container">
              <div class="section-header">
                <span class="section-label">
                  <span class="step-num">{{ currentProgressiveStep }}</span>
                  {{ getCurrentStepData()?.title }}
                </span>
              </div>
              <div class="guided-code-display">
                <pre class="guided-code" v-html="renderBlankTemplate(currentProgressiveStep)"></pre>
              </div>
              <div class="blank-input-area">
                <label class="blank-label">Fill in the blank:</label>
                <input
                  v-model="blankInputs[currentProgressiveStep]"
                  class="blank-input"
                  :placeholder="getCurrentStepData()?.blank_placeholder || '___'"
                  @keydown.enter="submitGuidedBlank(currentProgressiveStep)"
                  :disabled="blankVerified[currentProgressiveStep]"
                />
                <button
                  class="editor-btn submit-btn"
                  @click="submitGuidedBlank(currentProgressiveStep)"
                  :disabled="!blankInputs[currentProgressiveStep]?.trim() || blankVerified[currentProgressiveStep]"
                >
                  VERIFY
                </button>
              </div>
            </div>
          </div>

          <!-- 힌트 오리 -->
          <transition name="duck-pop">
            <div v-if="showProgressiveHintPanel" class="hint-duck-container">
              <div class="hint-speech-bubble">
                <div class="bubble-header">DUC-TIP!</div>
                <div class="bubble-content">{{ getCurrentStepData()?.hint }}</div>
              </div>
              <img :src="unitDuck" class="hint-duck-img" alt="Hint Duck">
            </div>
          </transition>
        </main>

        <!-- ========== LINE EDIT MODE ========== -->
        <main v-else-if="currentStageMode === 'line_edit'" class="full-code-editor line-edit-mode" ref="editorFrameRef">
          <div class="bugs-container">
            <div
              v-for="step in totalStepsComputed"
              :key="'bug-' + step"
              class="code-bug"
              :ref="el => (bugRefs[step] = el)"
              :class="{
                dead: progressiveCompletedSteps.includes(step),
                eating: !progressiveCompletedSteps.includes(step),
                targeted: step === currentProgressiveStep && isRunning,
                clickable: false
              }"
              :style="bugPositions[step]"
            >
              <svg v-if="!progressiveCompletedSteps.includes(step)"
                   width="60" height="60" viewBox="0 0 80 40"
                   class="worm-svg">
                <defs>
                  <linearGradient id="wormGradientLineEdit" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#FFE4E1;stop-opacity:1" />
                    <stop offset="50%" style="stop-color:#FFB6C1;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#FFC0CB;stop-opacity:1" />
                  </linearGradient>
                </defs>
                <path class="worm-body-main"
                      d="M10,20 Q20,15 30,20 Q40,25 50,20 Q60,15 70,20"
                      stroke="url(#wormGradientLineEdit)"
                      stroke-width="10"
                      stroke-linecap="round"
                      fill="none">
                  <animate attributeName="d"
                           dur="2s"
                           repeatCount="indefinite"
                           values="M10,20 Q20,15 30,20 Q40,25 50,20 Q60,15 70,20;
                                   M10,20 Q20,25 30,20 Q40,15 50,20 Q60,25 70,20;
                                   M10,20 Q20,15 30,20 Q40,25 50,20 Q60,15 70,20"/>
                </path>
                <circle cx="70" cy="20" r="5" fill="#FFB6C1"/>
              </svg>
            </div>
          </div>

          <div v-show="!showBullet" class="walking-duck" :style="walkingDuckStyle">
            <img v-if="isEating" :src="duckEating" class="duck-walking-img eating-motion" alt="Eating Duck">
            <img v-else-if="isSad" :src="duckSad" class="duck-walking-img sad-motion" alt="Sad Duck">
            <img v-else :src="duckIdle" class="duck-walking-img" alt="Walking Duck Bird">
          </div>

          <div v-show="showBullet" class="bullet duck-flying cinematic" :style="bulletStyle">
            <img :src="isEating ? duckEating : (isSad ? duckSad : duckFlying)"
                 class="duck-flying-img"
                 :class="{ 'eating-at-target': isEating, 'sad-at-target': isSad }"
                 alt="Flying/Eating/Sad Duck">
            <div v-if="!isEating && !isSad" class="speed-lines">
              <span v-for="n in 5" :key="n" class="speed-line"></span>
            </div>
          </div>

          <transition name="explode">
            <div v-if="showHitEffect" class="hit-effect" :style="hitEffectStyle">
              <span class="hit-text">{{ hitEffectText }}</span>
              <div class="explosion-particles">
                <span v-for="n in 8" :key="n" class="particle" :style="`--angle: ${n * 45}deg`"></span>
              </div>
            </div>
          </transition>

          <transition name="miss">
            <div v-if="showMissEffect" class="miss-effect" :style="missEffectStyle">
              <span class="miss-text">MISSED!</span>
            </div>
          </transition>

          <div class="editor-header">
            <div class="code-progress">
              <span class="progress-text">{{ progressiveCompletedSteps.length }}/{{ totalStepsComputed }} BUGS FIXED</span>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: (progressiveCompletedSteps.length / totalStepsComputed * 100) + '%' }"></div>
              </div>
            </div>
            <div class="line-edit-phase-indicator">
              <span :class="{ active: lineEditPhase === 'find' }">1. FIND</span>
              <span class="phase-arrow">→</span>
              <span :class="{ active: lineEditPhase === 'edit' }">2. EDIT</span>
            </div>
            <div class="editor-top-buttons">
              <button class="editor-btn hint-btn" @click="showProgressiveHint">💡 HINT</button>
            </div>
          </div>

          <div class="editor-body">
            <div class="section-header">
              <span class="section-label">
                <span class="step-num">{{ currentProgressiveStep }}</span>
                {{ getCurrentStepData()?.title }}
              </span>
            </div>

            <div class="line-edit-instruction">
              <template v-if="lineEditPhase === 'find'">
                코드에서 잘못된(틀린) 줄을 찾아 클릭하세요!
              </template>
              <template v-else>
                클릭한 줄을 올바른 코드로 수정하세요!
              </template>
            </div>

            <div class="line-edit-code-viewer">
              <template v-for="(line, idx) in (getCurrentStepData()?.buggy_code?.split('\n') || [])" :key="idx">
                <div
                  class="code-line"
                  :class="{
                    'hovered': lineEditPhase === 'find' && hoveredLine === idx + 1,
                    'selected-correct': lineEditSelectedLine === idx + 1 && lineEditCorrect,
                    'selected-wrong': lineEditSelectedLine === idx + 1 && !lineEditCorrect && lineEditSelectedLine !== null,
                    'strikethrough': lineEditPhase === 'edit' && lineEditSelectedLine === idx + 1
                  }"
                  @mouseenter="lineEditPhase === 'find' ? (hoveredLine = idx + 1) : null"
                  @mouseleave="hoveredLine = null"
                  @click="lineEditPhase === 'find' ? handleLineEditClick(idx + 1) : null"
                >
                  <span class="line-number">{{ idx + 1 }}</span>
                  <pre class="line-content">{{ line }}</pre>
                </div>

                <div v-if="lineEditPhase === 'edit' && lineEditSelectedLine === idx + 1" class="line-edit-input-area">
                  <div class="line-edit-input-wrapper">
                    <span class="edit-arrow">↳</span>
                    <textarea
                      v-model="lineEditInput"
                      class="line-edit-textarea"
                      placeholder="올바른 코드를 입력하세요..."
                      rows="2"
                      @keydown.ctrl.enter="submitLineEdit"
                      autofocus
                    ></textarea>
                  </div>
                  <button class="editor-btn submit-btn line-edit-submit" @click="submitLineEdit" :disabled="!lineEditInput.trim()">
                    SUBMIT
                  </button>
                </div>
              </template>
            </div>
          </div>

          <transition name="duck-pop">
            <div v-if="showProgressiveHintPanel" class="hint-duck-container">
              <div class="hint-speech-bubble">
                <div class="bubble-header">DUC-TIP! 💡</div>
                <div class="bubble-content">{{ getCurrentStepData()?.hint }}</div>
              </div>
              <img :src="unitDuck" class="hint-duck-img" alt="Hint Duck">
            </div>
          </transition>
        </main>

        <!-- ========== STANDARD MODE ========== -->
        <main v-else class="full-code-editor" ref="editorFrameRef">
          <!-- 3마리 지렁이 SVG 애니메이션 -->
          <div class="bugs-container">
            <div
              v-for="step in totalStepsComputed"
              :key="'bug-' + step"
              class="code-bug"
              :ref="el => (bugRefs[step] = el)"
              :class="{
                dead: progressiveCompletedSteps.includes(step),
                eating: !progressiveCompletedSteps.includes(step),
                targeted: step === currentProgressiveStep && isRunning,
                clickable: step === currentProgressiveStep && currentProgressivePhase === 'debug'
              }"
              :style="bugPositions[step]"
              @click="onBugClick(step)"
            >
              <!-- 지렁이 SVG (더 리얼하게) -->
              <svg v-if="!progressiveCompletedSteps.includes(step)"
                   width="60" height="60" viewBox="0 0 80 40"
                   class="worm-svg">
                <!-- 지렁이 몸통 (세그먼트화된 구조) -->
                <defs>
                  <linearGradient id="wormGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#FFE4E1;stop-opacity:1" />
                    <stop offset="50%" style="stop-color:#FFB6C1;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#FFC0CB;stop-opacity:1" />
                  </linearGradient>
                </defs>

                <!-- 메인 몸통 -->
                <path class="worm-body-main"
                      d="M10,20 Q20,15 30,20 Q40,25 50,20 Q60,15 70,20"
                      stroke="url(#wormGradient)"
                      stroke-width="10"
                      stroke-linecap="round"
                      fill="none">
                  <animate attributeName="d"
                           dur="2s"
                           repeatCount="indefinite"
                           values="M10,20 Q20,15 30,20 Q40,25 50,20 Q60,15 70,20;
                                   M10,20 Q20,25 30,20 Q40,15 50,20 Q60,25 70,20;
                                   M10,20 Q20,15 30,20 Q40,25 50,20 Q60,15 70,20"/>
                </path>

                <!-- 세그먼트 링 -->
                <ellipse cx="18" cy="20" rx="2" ry="4" fill="#FFB6C1" opacity="0.8">
                  <animate attributeName="cy" dur="2s" repeatCount="indefinite"
                           values="20;17;20;23;20"/>
                </ellipse>
                <ellipse cx="30" cy="20" rx="2" ry="4" fill="#FFB6C1" opacity="0.8">
                  <animate attributeName="cy" dur="2s" repeatCount="indefinite"
                           values="20;23;20;17;20"/>
                </ellipse>
                <ellipse cx="42" cy="20" rx="2" ry="4" fill="#FFB6C1" opacity="0.8">
                  <animate attributeName="cy" dur="2s" repeatCount="indefinite"
                           values="20;17;20;23;20"/>
                </ellipse>
                <ellipse cx="54" cy="20" rx="2" ry="4" fill="#FFB6C1" opacity="0.8">
                  <animate attributeName="cy" dur="2s" repeatCount="indefinite"
                           values="20;23;20;17;20"/>
                </ellipse>

                <!-- 머리 부분 -->
                <circle cx="70" cy="20" r="5" fill="#FFB6C1"/>
                <!-- 눈 (작게) -->
                <circle cx="68" cy="18" r="1.5" fill="#000">
                  <animate attributeName="r"
                           dur="3s"
                           repeatCount="indefinite"
                           values="1.5;0.3;1.5;1.5;1.5"/>
                </circle>
              </svg>
            </div>
          </div>

          <!-- [2026-02-03] 메인 화면 걷는 오리 PNG 교체 (v-show로 변경하여 부드러운 전환) -->
          <div v-show="!showBullet" class="walking-duck" :style="walkingDuckStyle">
            <!-- [2026-02-03] 에셋 임포트 방식으로 안정적인 이미지 로딩 보장 -->
            <img v-if="isEating" :src="duckEating" class="duck-walking-img eating-motion" alt="Eating Duck">
            <img v-else-if="isSad" :src="duckSad" class="duck-walking-img sad-motion" alt="Sad Duck">
            <img v-else :src="duckIdle" class="duck-walking-img" alt="Walking Duck Bird">
          </div>

          <!-- [2026-02-03] 오리가 날아가서 도착 지점에서 지렁이를 먹는 동작 (v-show로 변경하여 부드러운 전환) -->
          <div v-show="showBullet" class="bullet duck-flying cinematic" :style="bulletStyle">
            <img :src="isEating ? duckEating : (isSad ? duckSad : duckFlying)"
                 class="duck-flying-img"
                 :class="{ 'eating-at-target': isEating, 'sad-at-target': isSad }"
                 alt="Flying/Eating/Sad Duck">
            <!-- 속도선 효과 (비행 중에만 표시) -->
            <div v-if="!isEating && !isSad" class="speed-lines">
              <span v-for="n in 5" :key="n" class="speed-line"></span>
            </div>
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
              <span class="miss-text">MISSED!</span>
            </div>
          </transition>

          <div class="editor-header">
            <div class="code-progress">
              <span class="progress-text">{{ progressiveCompletedSteps.length }}/{{ totalStepsComputed }} BUGS FIXED</span>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: (progressiveCompletedSteps.length / totalStepsComputed * 100) + '%' }"></div>
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
              <button class="editor-btn submit-btn" @click="submitProgressiveStep" :disabled="currentProgressiveStep > totalStepsComputed || isRunning || showStepResultOverlay || showStrategyDuck">
                🚀 SUBMIT
              </button>
            </div>
          </div>

          <!-- 전략 작성 오리 (힌트 오리와 동일한 UI) -->
          <transition name="duck-pop">
            <div v-if="showStrategyDuck && currentStageMode === 'standard'" class="hint-duck-container">
              <div class="hint-speech-bubble strategy-bubble">
                <div class="bubble-header">전략을 작성해주세요! ✍️</div>
                <div class="bubble-content">
                  <textarea
                    v-model="strategyInput"
                    @keydown.ctrl.enter="handleStrategySubmit"
                    placeholder="버그 해결 전략을 작성해주세요...&#10;&#10;• 어떤 문제를 발견했나요?&#10;• 왜 이렇게 수정했나요?&#10;• 어떤 효과가 있나요?"
                    class="strategy-textarea"
                    rows="6"
                    autofocus
                  ></textarea>
                  <button
                    class="submit-strategy-btn"
                    @click="handleStrategySubmit"
                    :disabled="!strategyInput.trim()"
                  >
                    📝 전략 제출하기
                  </button>
                </div>
              </div>
              <img :src="unitDuck" class="hint-duck-img" alt="Strategy Duck">
            </div>
          </transition>

          <div class="editor-body" ref="editorBodyRef">
            <!-- 현재 스텝만 표시 -->
            <div class="code-sections">
              <template v-for="step in totalStepsComputed" :key="'section-' + step">
                <div
                  v-if="Number(step) === Number(currentProgressiveStep)"
                  ref="sectionRefs"
                  class="code-section-wrapper"
                >
                <!-- 코드 에디터 (항상 표시) -->
                <div class="code-section active">
                  <div class="section-header">
                    <span class="section-label">
                      <span class="step-num">{{ step }}</span>
                      {{ getStepData(step)?.title }}
                    </span>
                    <span class="section-status">
                      <span v-if="step === currentProgressiveStep && !progressiveCompletedSteps.includes(step)" class="status-current">🔧 CURRENT</span>
                      <span v-else-if="progressiveCompletedSteps.includes(step)" class="status-success">✅ SOLVED</span>
                    </span>
                  </div>

                  <!-- 편집 가능한 섹션 (디버그 모드) 또는 읽기 전용 (전략 입력 시) -->
                  <div class="code-editor-wrapper active-wrapper monaco-active-wrapper">
                    <vue-monaco-editor
                      v-model:value="progressiveStepCodes[Number(step)]"
                      theme="vs-dark"
                      language="python"
                      :options="editorOptions"
                      @mount="handleEditorMount"
                      class="bughunt-monaco-editor"
                    />
                  </div>
                </div>
              </div>

            </template>
          </div>
          </div>

          <!-- 힌트 오리 (말풍선 포함) -->
          <transition name="duck-pop">
            <div v-if="showProgressiveHintPanel" class="hint-duck-container">
              <div class="hint-speech-bubble">
                <div class="bubble-header">DUC-TIP! 💡</div>
                <div class="bubble-content">{{ getCurrentStepData()?.hint }}</div>
              </div>
              <img :src="unitDuck" class="hint-duck-img" alt="Hint Duck">
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
          <div class="report-header mission-summary">
            <div class="project-info">
              <span class="id-badge">CLEAR!</span>
              <h2>{{ currentProgressiveMission?.stage_title }}</h2>
            </div>
            <div class="score-summary center-focus">
              <div class="score-item">
                <span class="label">FINAL SCORE</span>
                <span class="value">{{ progressiveMissionScore }}</span>
              </div>
              <div class="shake-earned">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="shake-earned-icon">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                </svg>
                <span class="shake-earned-text">+{{ progressiveMissionScore }} Protein Shake</span>
              </div>
              <div class="penalty-stats" v-if="hasPenalties">
                 <div class="penalty-item">
                   <span class="p-label">CODE RETRY ({{ codeSubmitFailCount }})</span>
                   <span class="p-value">-{{ codeSubmitFailCount * codeRetryPenalty }}</span>
                 </div>
                 <div v-if="currentProgressiveMission?.id !== 'S1'" class="penalty-item">
                    <span class="p-label">HINTS USED ({{ totalHintCount }})</span>
                    <span class="p-value">-{{ totalHintCount }}</span>
                 </div>
              </div>
            </div>
          </div>

          <!-- AI 디버깅 사고 평가 섹션 (S4 이후 stage에서만) -->
          <div v-if="!isBasicStage" class="ai-report-section neon-border">
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

          <!-- DEBUGGING LOG & STRATEGY 섹션 (S4 이후에만 표시) -->
          <div v-if="!isBasicStage" class="explanations-list">
            <div class="list-title">📋 DEBBUGING LOG & STRATEGY</div>
            <div
              v-for="step in totalStepsComputed"
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

    <!-- 튜토리얼 오버레이 -->
    <BugHuntTutorialOverlay
      v-if="showTutorial && currentView === 'progressivePractice'"
      :tutorial-steps="activeTutorialSteps"
      @complete="onTutorialComplete"
      @skip="onTutorialComplete"
    />

    <transition name="fade">
      <div
        v-if="showStepResultOverlay && currentView === 'progressivePractice'"
        class="step-result-overlay"
        @click="continueStepAfterReview"
      >
        <div class="step-result-hint">
          CLUES & LOGS를 확인했으면 화면 아무 곳이나 클릭하세요
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, shallowRef, nextTick } from 'vue';
// [2026-02-03] 이미지 경로 문제를 근본적으로 해결하기 위해 Vite 에셋 파이프라인(Import) 도입
import duckIdle from '@/assets/image/duck_idle_change.png';
import duckEating from '@/assets/image/duck_eating.png';
import duckFlying from '@/assets/image/duck_flying.png';
import duckSad from '@/assets/image/duck_sad.png';
import unitDuck from '@/assets/image/unit_duck.png';
import { useRoute, useRouter } from 'vue-router';
import { VueMonacoEditor } from '@guolao/vue-monaco-editor';
import axios from 'axios';
import { evaluateBugHunt, verifyCodeBehavior } from './api/bugHuntApi';
import BugHuntTutorialOverlay from './composables/BugHuntTutorialOverlay.vue';
import { useAuthStore } from '@/stores/auth';
import './BugHunt.css';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

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

// 타이머 관리 (언마운트 시 정리)
const activeTimeouts = new Set();
function scheduleTimeout(fn, ms) {
  const id = setTimeout(fn, ms);
  activeTimeouts.add(id);
  return id;
}
function clearAllTimeouts() {
  activeTimeouts.forEach((id) => clearTimeout(id));
  activeTimeouts.clear();
}

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
  { id: 'mission_master', name: 'Mission Master', desc: '모든 미션을 완료했습니다', icon: '👑', condition: () => getProgressiveMissionsCompleted() >= progressiveProblems.value.length }
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

const hasPenalties = computed(() => {
  return codeSubmitFailCount.value > 0 || totalHintCount.value > 0;
});

const totalHintCount = computed(() => {
  return Object.values(progressiveHintUsed.value).filter(v => v).length;
});

// [2026-02-03] 오리 캐릭터의 상태(평상시/먹기)를 제어하기 위한 반응형 변수 추가
const isEating = ref(false);
const isSad = ref(false);
const headerEatingStep = ref(null);

function showLevelUpEffect(oldLevel, newLevel, title) {
  levelUpInfo.value = { oldLevel, newLevel, title };
  showLevelUp.value = true;
  scheduleTimeout(() => { showLevelUp.value = false; }, 3000);
}

function showAchievementUnlock(achievement) {
  newAchievement.value = achievement;
  showAchievementPopup.value = true;
  scheduleTimeout(() => { showAchievementPopup.value = false; }, 3000);
}

// ============================================
// Progressive Mission 시스템
// ============================================
const progressiveProblems = ref([]);
const loading = ref(true);
const error = ref(null);
const currentProgressiveMission = ref(null);
const currentProgressiveStep = ref(1);
const currentProgressivePhase = ref('quiz'); // 'quiz', 'debug', 'explain'
const progressiveCompletedSteps = ref([]);
const progressiveStepCodes = ref({ 1: '', 2: '', 3: '', 4: '', 5: '' });
const progressiveHintUsed = ref({ 1: false, 2: false, 3: false, 4: false, 5: false });
const showProgressiveHintPanel = ref(false);

// ============================================
// Stage Mode 시스템
// ============================================
const currentStageMode = ref('standard');  // 'tutorial' | 'guided' | 'line_edit' | 'standard'
const totalStepsComputed = computed(() => currentProgressiveMission.value?.totalSteps || 3);

// Stage 기반 평가 구분 (S1, S2, S3는 간단한 평가 / S4 이후는 LLM 평가 포함)
const isBasicStage = computed(() => {
  const stageId = currentProgressiveMission.value?.id;
  return ['S1', 'S2', 'S3'].includes(stageId);
});

// Tutorial Mode refs
const tutorialPhase = ref('explore');     // 'explore' | 'fix' | 'review'
const hoveredLine = ref(null);
const selectedBugLine = ref(null);
const bugLineCorrect = ref(false);
const selectedChoice = ref(null);
const choiceSubmitted = ref(false);
const tutorialChoiceCorrect = ref(false);

// Guided Mode refs
const blankInputs = ref({});
const blankVerified = ref({});

// Line Edit Mode refs
const lineEditPhase = ref('find');       // 'find' | 'edit'
const lineEditSelectedLine = ref(null);  // 클릭한 줄 번호
const lineEditCorrect = ref(false);      // 정답 줄 찾았는지
const lineEditInput = ref('');           // 수정 코드 입력값
const lineEditSubmitted = ref(false);    // 제출 여부


// 로그창 주목 효과
const showAttentionEffect = ref(false);

// 전략 입력 관련 상태
const showStrategyDuck = ref(false);      // 전략 오리 + 말풍선 표시 여부
const strategyInput = ref('');             // 전략 입력 내용

// 코드 제출 상태
const codeSubmitFailCount = ref(0);
const codeRetryPenalty = 5;

// 설명 및 평가 데이터
const stepExplanations = reactive({ 1: '', 2: '', 3: '', 4: '', 5: '' });
const clueMessages = ref([]); // 단서 메시지 (로그, 힌트 등)
const clueContentRef = ref(null);

const stepStartTime = ref(null);
const totalDebugTime = ref(0);
const evaluationStats = reactive({
  perfectClears: 0,
});

// AI 평가 상태
const isEvaluatingAI = ref(false);
const aiEvaluationResult = ref(null);

// Progressive UI 이펙트
const progressiveMissionXP = ref(0);
const progressiveMissionScore = ref(0);
const showStepResultOverlay = ref(false);

// 화면 흔들림 효과
const isShaking = ref(false);

// 버그 수정 알림 팝업 (중앙에서 대화창으로 날아가는 효과)

// 튜토리얼 상태
const showTutorial = ref(false);
const STAGE_TUTORIAL_KEY = 'bughunt-stage-tutorial-done';

function loadStageTutorialDone() {
  try {
    const raw = localStorage.getItem(STAGE_TUTORIAL_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function saveStageTutorialDone(doneMap) {
  try {
    localStorage.setItem(STAGE_TUTORIAL_KEY, JSON.stringify(doneMap));
  } catch (e) {
    console.warn('Failed to save stage tutorial state:', e);
  }
}

const stageTutorialDone = ref(loadStageTutorialDone());

const stageTutorialSteps = {
  S1: [
    {
      selector: '.progressive-header',
      title: '첫 스테이지 목표',
      description: '첫번째 스테이지는 로그를 읽고 버그 줄을 찾은 뒤, 올바른 수정 방법을 선택하는 튜토리얼 단계입니다.',
      cardPosition: 'bottom'
    },
    {
      selector: '.clue-panel',
      title: '로그 읽기',
      description: 'TypeError 메시지에서 str/int 같은 타입 힌트를 먼저 찾으면 원인 파악이 빨라집니다.',
      cardPosition: 'right'
    },
    {
      selector: '.tutorial-code-viewer',
      title: '버그 줄 찾기',
      description: '코드 줄을 클릭해 어디가 문제인지 확인하세요. 맞는 줄을 고르면 다음 단계로 이동합니다.',
      cardPosition: 'left'
    },
    {
      selector: '.choice-grid',
      title: '수정 방법 선택',
      description: '객관식에서 가장 안전한 수정 코드를 선택하고 SUBMIT으로 검증하세요.',
      cardPosition: 'top'
    }
  ],
  S2: [
    {
      selector: '.progressive-header',
      title: 'S2 목표',
      description: 'S2는 빈칸 채우기로 자주 나오는 기초 버그를 빠르게 고치는 단계입니다.',
      cardPosition: 'bottom'
    },
    {
      selector: '.clue-panel',
      title: '에러 단서 확인',
      description: 'IndexError, 모드 관련 경고처럼 핵심 키워드를 먼저 확인하세요.',
      cardPosition: 'right'
    },
    {
      selector: '.guided-code-display',
      title: '빈칸 위치 파악',
      description: '코드 흐름에서 빈칸이 어떤 역할인지 먼저 이해한 뒤 답을 입력합니다.',
      cardPosition: 'left'
    },
    {
      selector: '.blank-input-area',
      title: '답 입력/검증',
      description: '정답 코드를 입력하고 VERIFY를 눌러 다음 스텝으로 진행합니다.',
      cardPosition: 'top'
    }
  ],
  S3: [
    {
      selector: '.progressive-header',
      title: 'S3 목표',
      description: 'S3는 줄 찾기(FIND)와 직접 수정(EDIT)을 연습하는 브릿지 단계입니다.',
      cardPosition: 'bottom'
    },
    {
      selector: '.line-edit-phase-indicator',
      title: 'FIND → EDIT',
      description: '먼저 틀린 줄을 클릭해 FIND를 통과한 뒤, EDIT에서 코드를 직접 입력합니다.',
      cardPosition: 'bottom'
    },
    {
      selector: '.line-edit-code-viewer',
      title: '틀린 줄 클릭',
      description: '코드 뷰어에서 문제 줄을 정확히 찾아 클릭하세요. 정답이면 수정 입력창이 열립니다.',
      cardPosition: 'left'
    },
    {
      selector: '.line-edit-instruction',
      title: '수정 후 제출',
      description: '올바른 코드 한 줄을 입력하고 SUBMIT으로 검증합니다. Ctrl+Enter도 지원합니다.',
      cardPosition: 'top'
    }
  ],
  S4: [
    {
      selector: '.progressive-header',
      title: 'S4 실전 시작',
      description: '여기서부터 자유코딩 실전입니다. 로그를 보고 원인을 추론한 뒤 직접 코드 수정을 완료해야 합니다.',
      cardPosition: 'bottom'
    },
    {
      selector: '.clue-panel',
      title: '1) 로그 우선 분석',
      description: '정답 코드를 바로 쓰기 전에 로그의 핵심 신호(Loss 폭주, 모드 불일치, LR 급감)를 먼저 찾으세요.',
      cardPosition: 'right'
    },
    {
      selector: '.code-editor-wrapper',
      title: '2) 최소 수정 전략',
      description: '한 번에 전부 고치기보다, 원인으로 보이는 지점부터 최소 수정 후 SUBMIT으로 검증하세요.',
      cardPosition: 'left'
    },
    {
      selector: '.editor-top-buttons',
      title: '3) 실전 조작',
      description: '힌트(HINT), 초기화(RESET), 제출(SUBMIT) 버튼을 상황에 맞게 사용해 디버깅 루프를 완성하세요.',
      cardPosition: 'top'
    }
  ],
  default: [
    {
      selector: '.progressive-header',
      title: '미션 정보',
      description: '현재 진행 중인 프로젝트 제목과 남은 벌레 수를 확인할 수 있습니다.',
      cardPosition: 'bottom'
    },
    {
      selector: '.scenario-box',
      title: '미션 브리핑',
      description: '여기에서 현재 해결해야 할 문제의 시나리오를 확인하세요.',
      cardPosition: 'right'
    },
    {
      selector: '.clue-panel',
      title: '단서 및 로그',
      description: '시스템 로그와 힌트가 표시되는 곳입니다. 디버깅의 중요한 실마리를 찾으세요.',
      cardPosition: 'right'
    },
    {
      selector: '.full-code-editor',
      title: '코드 에디터',
      description: '실제 코드를 수정하는 영역입니다. 벌레가 숨어있는 부분을 찾아 올바르게 수정해 주세요.',
      cardPosition: 'left'
    }
  ]
};

const activeTutorialSteps = computed(() => {
  const missionId = currentProgressiveMission.value?.id;
  return stageTutorialSteps[missionId] || stageTutorialSteps.default;
});

function onTutorialComplete() {
  showTutorial.value = false;
  const missionId = currentProgressiveMission.value?.id;
  if (missionId && ['S1', 'S2', 'S3', 'S4'].includes(missionId)) {
    const next = { ...stageTutorialDone.value, [missionId]: true };
    stageTutorialDone.value = next;
    saveStageTutorialDone(next);
  }
}

function startTutorial() {
  showTutorial.value = true;
}



// 미션 해금 여부 (순차적)
function isMissionUnlocked(index) {
  if (index === 0) return true;
  const prevMission = progressiveProblems[index - 1];
  if (!prevMission) return false;

  // 미션 완료 플래그가 없더라도, 마지막 스텝을 완료한 기록이 있으면 해금 처리
  // (스테이지 구조 변경/마이그레이션 상황에서 잠금이 영구화되는 문제 방지)
  return (
    isMissionCompleted(prevMission.id) ||
    isStepCompleted(prevMission.id, prevMission.totalSteps || 3)
  );
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
  const mission = progressiveProblems.value.find(m => m.id === missionId);
  const totalSteps = mission?.totalSteps || 3;

  for (let step = 1; step <= totalSteps; step++) {
    if (!isStepCompleted(missionId, step)) return step;
  }

  // 모든 단계를 이미 완료했다면 (Replay 모드) 1단계부터 다시 시작
  return 1;
}

// 완료된 Progressive 미션 수
function getProgressiveMissionsCompleted() {
  return progressiveProblems.value.filter(m => isStepCompleted(m.id, m.totalSteps || 3)).length;
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

  // 변경: 동적 초기화
  const totalSteps = mission.totalSteps || 3;
  currentStageMode.value = mission.mode || 'standard';

  // 힌트 동적 초기화
  progressiveHintUsed.value = {};
  for (let i = 1; i <= totalSteps; i++) {
    progressiveHintUsed.value[i] = false;
  }

  // 모든 스텝의 버그 코드 로드 (키 불일치 방지를 위해 번호로 강제 변환)
  progressiveStepCodes.value = {};
  mission.steps.forEach(s => {
    progressiveStepCodes.value[Number(s.step)] = s.buggy_code;
  });

  // 설명 동적 초기화
  for (let i = 1; i <= totalSteps; i++) {
    stepExplanations[i] = '';
  }

  codeSubmitFailCount.value = 0;
  totalDebugTime.value = 0;
  evaluationStats.perfectClears = 0;
  showStepResultOverlay.value = false;
  pendingStepContinue = null;
  showStrategyDuck.value = false;
  strategyInput.value = '';

  currentView.value = 'progressivePractice';

  // 모드별 초기화
  if (currentStageMode.value === 'tutorial') {
    tutorialPhase.value = 'explore';
    selectedBugLine.value = null;
    bugLineCorrect.value = false;
    selectedChoice.value = null;
    choiceSubmitted.value = false;
    tutorialChoiceCorrect.value = false;
    // tutorial은 startDebugPhase 호출 안 함
  } else if (currentStageMode.value === 'guided') {
    blankInputs.value = {};
    blankVerified.value = {};
    startDebugPhase();
  } else if (currentStageMode.value === 'line_edit') {
    lineEditPhase.value = 'find';
    lineEditSelectedLine.value = null;
    lineEditCorrect.value = false;
    lineEditInput.value = '';
    lineEditSubmitted.value = false;
    hoveredLine.value = null;
    currentProgressivePhase.value = 'quiz';
  } else {
    startDebugPhase();
  }

  // 단서 초기화 (공통)
  const stepData = getCurrentStepData();
  clueMessages.value = [];

  // 에러 로그만 표시
  if (stepData?.error_log) {
    clueMessages.value.push({
      type: 'ERROR',
      text: stepData.error_log,
      isNew: false
    });
  }

  // 버그 애니메이션 시작 (공통)
  scheduleTimeout(() => {
    startBugAnimations();
  }, 500);

  if (['S1', 'S2', 'S3', 'S4'].includes(mission.id) && !stageTutorialDone.value[mission.id]) {
    scheduleTimeout(() => {
      showTutorial.value = true;
    }, 300);
  }
}

// 디버깅 페이즈 시작
function startDebugPhase() {
  currentProgressivePhase.value = 'debug';
  stepStartTime.value = Date.now();
}

// 단서 메시지 추가 헬퍼
function addClue(type, text) {
  clueMessages.value.push({
    type, // 'INFO', 'WARN', 'ERROR', 'SUCCESS', 'HINT'
    text,
    isNew: true
  });

  // DOM 업데이트 후 스크롤
  nextTick(() => {
    scrollClues();
  });

  // 짧은 시간 후 isNew 제거
  scheduleTimeout(() => {
    const lastClue = clueMessages.value[clueMessages.value.length - 1];
    if (lastClue) lastClue.isNew = false;
  }, 1000);
}

// 단서창 스크롤
function scrollClues() {
  if (clueContentRef.value) {
    scheduleTimeout(() => {
      clueContentRef.value.scrollTo({
        top: clueContentRef.value.scrollHeight,
        behavior: 'smooth'
      });
    }, 50);
  }
}

function holdStepResult(stepData, { onContinue = null } = {}) {
  const successLog = stepData?.success_log || '수정이 정상 반영되었습니다.';
  const coaching = stepData?.coaching || '';

  const hasSuccessLog = clueMessages.value.some(
    (msg) => msg.type === 'SUCCESS' && msg.text === successLog
  );
  if (!hasSuccessLog) {
    clueMessages.value.push({ type: 'SUCCESS', text: successLog, isNew: true });
  }

  if (coaching) {
    const hasCoaching = clueMessages.value.some(
      (msg) => msg.type === 'HINT' && msg.text === coaching
    );
    if (!hasCoaching) {
      clueMessages.value.push({ type: 'HINT', text: coaching, isNew: true });
    }
  }

  nextTick(() => {
    scrollClues();
  });

  showAttentionEffect.value = true;
  scheduleTimeout(() => {
    showAttentionEffect.value = false;
  }, 1800);

  pendingStepContinue = onContinue;
  showStepResultOverlay.value = true;
}

function continueStepAfterReview() {
  showStepResultOverlay.value = false;
  const nextFn = pendingStepContinue;
  pendingStepContinue = null;
  if (typeof nextFn === 'function') {
    nextFn();
  }
}

// 다음 문제로 이동 (설명 완료 후)
function moveToNextStep() {
  if (currentProgressiveStep.value < totalStepsComputed.value) {
    currentProgressiveStep.value++;
    startDebugPhase();
  } else {
    completeMission();
  }
}

/**
 * 전략 제출 처리
 */
function handleStrategySubmit() {
  if (!strategyInput.value.trim()) return;

  // 전략 저장
  stepExplanations[currentProgressiveStep.value] = strategyInput.value.trim();

  // 로그에 기록
  addClue('SUCCESS', `Step ${currentProgressiveStep.value} 전략이 기록되었습니다.`);

  // 입력창 초기화
  strategyInput.value = '';

  // 오리와 말풍선 숨기기
  showStrategyDuck.value = false;

  // 다음 단계로 이동 또는 미션 완료
  if (currentProgressiveStep.value < totalStepsComputed.value) {
    scheduleTimeout(() => {
      moveToNextStep();

      // 다음 단계 에러 로그만 표시
      const stepData = getCurrentStepData();
      if (stepData?.error_log) {
        clueMessages.value = [{
          type: 'ERROR',
          text: stepData.error_log,
          isNew: true
        }];
      }
    }, 500);
  } else {
    scheduleTimeout(() => {
      completeMission();
    }, 500);
  }
}

// 평가 화면 보기
async function showEvaluation() {
  currentView.value = 'evaluation';

  // S1, S2, S3 기본 stage에서는 AI 평가 skip
  if (isBasicStage.value) {
    aiEvaluationResult.value = null;
    isEvaluatingAI.value = false;
    return;
  }

  // S4 이후 고급 stage에서만 AI 평가 로직 실행
  if (currentProgressiveMission.value) {
    isEvaluatingAI.value = true;
    try {
      aiEvaluationResult.value = await evaluateBugHunt(
        currentProgressiveMission.value.stage_title,
        currentProgressiveMission.value.steps,
        stepExplanations,
        progressiveStepCodes.value,
        {
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

  const index = progressiveProblems.value.findIndex(m => m.id === mission.id);
  startProgressiveMission(mission, index);
}

// 현재 스텝 리셋
function resetCurrentStep() {
  const stepData = getCurrentStepData();
  if (stepData) {
    progressiveStepCodes.value[currentProgressiveStep.value] = stepData.buggy_code;
  }
}

// ============================================
// Tutorial Mode 메서드
// ============================================

// Tutorial Phase A - 라인 클릭
function handleTutorialLineClick(lineNum) {
  if (tutorialPhase.value !== 'explore') return;

  const stepData = getCurrentStepData();
  const correctLine = stepData?.bug_line;

  selectedBugLine.value = lineNum;

  if (lineNum === correctLine) {
    bugLineCorrect.value = true;
    addClue('SUCCESS', 'Bug Found! 이 줄에 문제가 있습니다.');
    scheduleTimeout(() => {
      tutorialPhase.value = 'fix';
    }, 1500);
  } else {
    // 틀린 줄 - shake 효과 및 차감
    codeSubmitFailCount.value++;
    isShaking.value = true;
    scheduleTimeout(() => { isShaking.value = false; }, 500);
    addClue('HINT', '다시 살펴보세요. 코드의 흐름을 따라가며 빠진 것이 없는지 확인해보세요.');
    // 선택 초기화 (재시도 가능)
    scheduleTimeout(() => { selectedBugLine.value = null; }, 1000);
  }
}

// Tutorial Phase B - 선택지
function handleTutorialChoice(idx) {
  if (tutorialPhase.value !== 'fix' || choiceSubmitted.value) return;
  selectedChoice.value = idx;
}

function submitTutorialChoice() {
  if (selectedChoice.value === null) return;

  const stepData = getCurrentStepData();
  const choices = stepData?.choices || [];
  const chosen = choices[selectedChoice.value];

  choiceSubmitted.value = true;
  tutorialChoiceCorrect.value = !!chosen?.correct;

  if (chosen?.correct) {
    // 정답: 오리가 벌레 잡는 애니메이션
    shootBug(currentProgressiveStep.value, true);

    scheduleTimeout(() => {
      progressiveCompletedSteps.value.push(currentProgressiveStep.value);
      const stepId = `progressive_${currentProgressiveMission.value.id}_step${currentProgressiveStep.value}`;
      if (!gameData.completedProblems.includes(stepId)) {
        gameData.completedProblems.push(stepId);
      }
      gameData.stats.totalBugsFixed++;

      // 리뷰 페이즈로 이동
      tutorialPhase.value = 'review';
    }, 2000);
  } else {
    // 오답: 오리가 빗나가는 애니메이션
    shootBug(currentProgressiveStep.value, false);
    codeSubmitFailCount.value++;

    // 재시도 가능하도록 초기화
    scheduleTimeout(() => {
      choiceSubmitted.value = false;
      selectedChoice.value = null;
      tutorialChoiceCorrect.value = false;
    }, 2000);
  }
}

// Tutorial Phase C - 리뷰 + 스테이지 클리어
function completeTutorialStage() {
  const totalSteps = currentProgressiveMission.value.totalSteps || 1;

  if (currentProgressiveStep.value < totalSteps) {
    // 다음 step으로 진행
    currentProgressiveStep.value++;

    // Tutorial 상태 초기화 (S2/S3 패턴과 동일)
    tutorialPhase.value = 'explore';
    selectedBugLine.value = null;
    bugLineCorrect.value = false;
    selectedChoice.value = null;
    choiceSubmitted.value = false;
    tutorialChoiceCorrect.value = false;
    hoveredLine.value = null;

    // 다음 step의 error_log 로드
    const nextStepData = getCurrentStepData();
    clueMessages.value = [];
    if (nextStepData?.error_log) {
      clueMessages.value.push({
        type: 'ERROR',
        text: nextStepData.error_log,
        isNew: true
      });
    }

    nextTick(() => {
      scrollClues();
    });
  } else {
    // 마지막 step → 미션 완료
    completeMission();
  }
}

// ============================================
// Guided Mode 메서드
// ============================================

function submitGuidedBlank(stepNum) {
  const stepData = getStepData(stepNum);
  if (!stepData) return;

  const userInput = (blankInputs.value[stepNum] || '').trim();
  const correctAnswer = stepData.blank_answer;

  // 비교: 공백 제거 후 case-insensitive
  const normalize = (s) => s.toLowerCase().replace(/\s+/g, '').replace(/[()]/g, '');
  const isCorrect = normalize(userInput) === normalize(correctAnswer);

  if (isCorrect) {
    blankVerified.value[stepNum] = true;
    shootBug(stepNum, true);
    addClue('SUCCESS', `Step ${stepNum} 정답! ${stepData.coaching}`);

    scheduleTimeout(() => {
      progressiveCompletedSteps.value.push(stepNum);
      const stepId = `progressive_${currentProgressiveMission.value.id}_step${stepNum}`;
      if (!gameData.completedProblems.includes(stepId)) {
        gameData.completedProblems.push(stepId);
      }
      gameData.stats.totalBugsFixed++;

      const totalSteps = currentProgressiveMission.value.totalSteps;
      holdStepResult(stepData, {
        isFinal: stepNum >= totalSteps,
        onContinue: () => {
          if (stepNum < totalSteps) {
            currentProgressiveStep.value = stepNum + 1;
            const nextStepData = getCurrentStepData();
            clueMessages.value = [];
            if (nextStepData?.error_log) {
              clueMessages.value.push({ type: 'ERROR', text: nextStepData.error_log, isNew: true });
            }
          } else {
            completeMission();
          }
        }
      });
    }, 2000);
  } else {
    shootBug(stepNum, false);
    codeSubmitFailCount.value++;
    addClue('ERROR', '답이 맞지 않습니다. 힌트를 확인해보세요.');
  }
}

function renderBlankTemplate(stepNum) {
  const stepData = getStepData(stepNum);
  if (!stepData?.blank_template) return '';

  const escaped = stepData.blank_template
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  return escaped.replace(/_{3,}/g, '<span class="blank-slot">___</span>');
}

// ============================================
// Line Edit Mode 메서드
// ============================================

function handleLineEditClick(lineNum) {
  if (lineEditPhase.value !== 'find') return;

  const stepData = getCurrentStepData();
  const correctLine = Number(stepData?.bug_line);
  const clickTolerance = Number.isInteger(stepData?.click_tolerance) ? Number(stepData.click_tolerance) : 0;
  lineEditSelectedLine.value = lineNum;

  if (Number.isInteger(correctLine) && Math.abs(lineNum - correctLine) <= clickTolerance) {
    lineEditCorrect.value = true;
    addClue('SUCCESS', 'Bug Found! 이 줄에 문제가 있습니다.');
    scheduleTimeout(() => {
      lineEditPhase.value = 'edit';
    }, 1200);
    return;
  }

  isShaking.value = true;
  scheduleTimeout(() => { isShaking.value = false; }, 500);
  addClue('HINT', '다시 살펴보세요. 에러 로그를 참고해보세요.');
  scheduleTimeout(() => { lineEditSelectedLine.value = null; }, 800);
}

function submitLineEdit() {
  if (!lineEditInput.value.trim()) return;

  const stepData = getCurrentStepData();
  if (!stepData) return;

  const correctLine = stepData.correct_line || '';
  const userInput = lineEditInput.value;
  const normalize = (s) => String(s || '').trim().replace(/\s+/g, ' ').toLowerCase();

  const normalizedUser = normalize(userInput);
  const normalizedCorrect = normalize(correctLine);
  const requiredKeywords = stepData?.solution_check?.required_all || [];
  const forbiddenKeywords = stepData?.solution_check?.forbidden || [];
  const allKeywordsPresent = requiredKeywords.every((kw) => normalizedUser.includes(normalize(kw)));
  const hasNoForbidden = forbiddenKeywords.every((kw) => !normalizedUser.includes(normalize(kw)));
  const isCorrect = hasNoForbidden && (allKeywordsPresent || normalizedUser.includes(normalizedCorrect));

  lineEditSubmitted.value = true;

  if (isCorrect) {
    shootBug(currentProgressiveStep.value, true);
    addClue('SUCCESS', `정답! ${stepData.coaching || ''}`);

    scheduleTimeout(() => {
      progressiveCompletedSteps.value.push(currentProgressiveStep.value);

      const stepId = `progressive_${currentProgressiveMission.value.id}_step${currentProgressiveStep.value}`;
      if (!gameData.completedProblems.includes(stepId)) {
        gameData.completedProblems.push(stepId);
      }
      gameData.stats.totalBugsFixed++;

      const totalSteps = currentProgressiveMission.value.totalSteps;
      holdStepResult(stepData, {
        isFinal: currentProgressiveStep.value >= totalSteps,
        onContinue: () => {
          if (currentProgressiveStep.value < totalSteps) {
            currentProgressiveStep.value++;
            lineEditPhase.value = 'find';
            lineEditSelectedLine.value = null;
            lineEditCorrect.value = false;
            lineEditInput.value = '';
            lineEditSubmitted.value = false;
            hoveredLine.value = null;

            const nextStepData = getCurrentStepData();
            clueMessages.value = [];
            if (nextStepData?.error_log) {
              clueMessages.value.push({ type: 'ERROR', text: nextStepData.error_log, isNew: true });
            }
          } else {
            completeMission();
          }
        }
      });
    }, 2000);
  } else {
    shootBug(currentProgressiveStep.value, false);
    codeSubmitFailCount.value++;
    addClue('ERROR', '코드가 올바르지 않습니다. 다시 확인해보세요.');
    lineEditSubmitted.value = false;
  }
}

// Progressive 힌트 보기 (토글 방식으로 변경 - 여러 번 볼 수 있음)
function showProgressiveHint() {
  // 첫 사용 시에만 기록 (점수 계산용)
  if (!progressiveHintUsed.value[currentProgressiveStep.value]) {
    progressiveHintUsed.value[currentProgressiveStep.value] = true;
  }
  // 힌트 패널 토글 (열려있으면 닫고, 닫혀있으면 열기)
  showProgressiveHintPanel.value = !showProgressiveHintPanel.value;
}

// Progressive 솔루션 체크 (행동 기반 검증 + 문자열 폴백)
// 반환값: { passed: boolean, result: object }
async function checkProgressiveSolution() {
  const stepData = getCurrentStepData();
  if (!stepData) return { passed: false, result: null };

  const code = progressiveStepCodes.value[currentProgressiveStep.value];
  const problemId = `${currentProgressiveMission.value?.id}_step${currentProgressiveStep.value}`;

  // 1. 행동 기반 검증 시도 (verification_code가 있는 경우)
  if (stepData.verification_code) {
    try {
      const result = await verifyCodeBehavior(code, stepData.verification_code, problemId);

      // 검증 성공/실패가 명확한 경우
      if (result.verified !== null) {
        console.log('🔬 행동 기반 검증 결과:', result);
        return { passed: result.verified, result };  // result 객체도 함께 반환
      }
      // result.verified === null 이면 폴백으로 진행
      console.log('⚠️ 행동 기반 검증 불가, 문자열 검증으로 폴백');
    } catch (e) {
      console.warn('행동 기반 검증 실패, 문자열 검증으로 폴백:', e);
      // 에러가 발생한 경우에도 에러 메시지를 result로 반환
      return { passed: false, result: { message: e.message, details: {} } };
    }
  }

  // 2. 폴백: 기존 문자열 기반 검증
  const check = stepData.solution_check;
  if (!check) return { passed: false, result: null };

  let passed = false;
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

      passed = hasAllRequired && hasAnyRequired && hasNoForbidden;
      break;

    case 'contains':
      passed = code.includes(check.value);
      break;

    case 'notContains':
      passed = !code.includes(check.value);
      break;

    case 'regex':
      // 패턴 일치 여부 확인 (string -> RegExp)
      try {
        const re = new RegExp(check.value, check.flags ?? '');
        passed = re.test(code);
      } catch {
        passed = false;
      }
      break;

    default:
      passed = false;
  }

  return { passed, result: null };
}

// Progressive 스텝 제출
async function submitProgressiveStep() {
  if (currentProgressiveStep.value > totalStepsComputed.value) return;
  if (progressiveCompletedSteps.value.includes(currentProgressiveStep.value)) return;
  if (currentStageMode.value === 'standard' && showStrategyDuck.value) return;
  if (showStepResultOverlay.value) return;

  isRunning.value = true;
  isSad.value = false; // 새로운 제출 시 슬픈 상태 초기화

  scheduleTimeout(async () => {
    const { passed, result } = await checkProgressiveSolution();
    const stepData = getCurrentStepData();

    // 🔍 디버깅 로그
    console.log('📊 검증 결과:', { passed, result });
    console.log('📊 result?.details:', result?.details);
    console.log('📊 simulation_logs 있음?:', !!result?.details?.simulation_logs);

    // 검증 결과에 따라 로그 업데이트
    if (passed && stepData?.success_log) {
      // 성공 시: success_log로 교체
      clueMessages.value = [{
        type: 'SUCCESS',
        text: stepData.success_log,
        isNew: true
      }];
    } else if (!passed) {
      // 실패 시: 실제 실행 로그 또는 error_log 표시
      if (result?.details?.simulation_logs) {
        // 실제 실행 결과 로그 표시
        clueMessages.value = [{
          type: 'ERROR',
          text: `=== 실시간 추론 로그 ===\n${result.details.simulation_logs}\n\n[ALERT] ${result.message}`,
          isNew: true
        }];
      } else if (stepData?.error_log) {
        // 기본 error_log 표시 (폴백)
        const hasErrorLog = clueMessages.value.some(msg => msg.text === stepData.error_log);
        if (!hasErrorLog) {
          clueMessages.value.push({
            type: 'ERROR',
            text: stepData.error_log,
            isNew: true
          });
        }
      }
    }

    // 저격 애니메이션
    shootBug(currentProgressiveStep.value, passed);

    scheduleTimeout(() => {
      if (passed) {
        // 성공!
        const endTime = Date.now();
        const duration = Math.floor((endTime - stepStartTime.value) / 1000);
        totalDebugTime.value += duration;

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

        // 성공 시 힌트 창 닫기
        showProgressiveHintPanel.value = false;

        // 전략 작성 오리 표시 (클릭하면 오버레이 열림) - standard 모드에서만
        if (currentStageMode.value === 'standard') {
          holdStepResult(stepData, {
            isFinal: currentProgressiveStep.value >= totalStepsComputed.value,
            onContinue: () => {
              currentProgressivePhase.value = 'explain';
              showStrategyDuck.value = true;
            }
          });
        }

      } else {
        // 실패
        codeSubmitFailCount.value++;
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
  const penalty = (codeSubmitFailCount.value * codeRetryPenalty) + (hintCount * 1);

  progressiveMissionXP.value = 100;
  progressiveMissionScore.value = Math.max(0, baseScore - penalty);

  addXP(progressiveMissionXP.value);
  gameData.totalScore += progressiveMissionScore.value;

  // 백엔드 activity API에 점수 제출 (Protein Shake 적립)
  submitToActivity();

  checkAchievements();
  showEvaluation();
}

// Activity API에 점수 제출 (Protein Shake 적립)
async function submitToActivity() {
  try {
    const detail_id = `bughunt01_${currentProgressiveMission.value.id}`;
    const score = progressiveMissionScore.value;

    await axios.post('/api/core/activity/submit/', {
      detail_id: detail_id,
      score: score,
      submitted_data: {
        mission_id: currentProgressiveMission.value.id,
        completed_steps: progressiveCompletedSteps.value.length,
        total_steps: currentProgressiveMission.value.totalSteps,
        hint_used: Object.values(progressiveHintUsed.value).filter(v => v).length,
        retry_count: codeSubmitFailCount.value
      }
    });

    // auth store 업데이트 (세션 새로고침)
    await authStore.checkSession();

    console.log('✅ Protein Shake 적립 완료:', authStore.userProteinShakes);
  } catch (error) {
    console.error('❌ Activity API 제출 실패:', error);
    // 에러가 나도 게임 진행은 계속되도록 함
  }
}

// Progressive 미션 종료
function finishProgressiveMission() {
  stopBugAnimations();
  router.push('/'); // 메인 페이지로 복귀
}

// 에디터 프레임 참조
const editorFrameRef = ref(null);
const editorBodyRef = ref(null);
const tutorialFixRef = ref(null);
const sectionRefs = ref([]);
const bugRefs = reactive({}); // 버그 요소 참조

// 스텝 변경 시 자동 스크롤
watch(currentProgressiveStep, (newStep) => {
  scheduleTimeout(() => {
    const el = sectionRefs.value[newStep - 1];
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, 100);
});

watch(tutorialPhase, (newPhase, oldPhase) => {
  if (currentStageMode.value !== 'tutorial') return;
  if (oldPhase === 'explore' && newPhase === 'fix') {
    nextTick(() => {
      scheduleTimeout(() => {
        tutorialFixRef.value?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }, 80);
    });
  }
});

// 버그 위치 상태
const bugPositions = reactive({
  1: { x: 0.6, y: 0.15 },
  2: { x: 0.7, y: 0.45 },
  3: { x: 0.65, y: 0.75 },
  4: { x: 0.55, y: 0.35 },
  5: { x: 0.75, y: 0.60 }
});

// 버그 애니메이션 ID
let bugAnimationIds = { 1: null, 2: null, 3: null, 4: null, 5: null };
let duckAnimationId = null;

// 버그 상태
const isRunning = ref(false);

// 오리/이펙트 상태
const walkingDuckPosition = reactive({ left: '10%', top: '85%' });
const showBullet = ref(false);
const bulletPosition = ref({ x: 0, y: 0 });
// [2026-02-03] 오리가 날아가는 방향을 바라보도록 회전값을 관리하는 변수 추가
const bulletRotation = ref(0);
const showHitEffect = ref(false);
const showMissEffect = ref(false);
const hitEffectPosition = ref({ x: 0, y: 0 });
const missEffectPosition = ref({ x: 0, y: 0 });
const hitEffectText = ref('SQUASH!');

const walkingDuckStyle = computed(() => ({
  left: walkingDuckPosition.left,
  top: walkingDuckPosition.top
}));

const bulletStyle = computed(() => ({
  left: `${bulletPosition.value.x}px`,
  top: `${bulletPosition.value.y}px`,
  // [2026-02-03] 실시간 궤적에 따른 회전값 적용
  transform: `translate(-50%, -50%) rotate(${bulletRotation.value}deg)`
}));

const hitEffectStyle = computed(() => ({
  left: `${hitEffectPosition.value.x}px`,
  top: `${hitEffectPosition.value.y}px`
}));

const missEffectStyle = computed(() => ({
  left: `${missEffectPosition.value.x}px`,
  top: `${missEffectPosition.value.y}px`
}));

// 지렁이 움직임 애니메이션 (땅 영역 30%에서만 움직이도록 수정)
function animateBug(step) {
  if (progressiveCompletedSteps.value.includes(step)) return;

  const time = Date.now() / 1000;

  // 땅 영역: 하단 75~95% 구간 (코드 70% + 땅 30%)
  const movementRadiusX = 30; // 좌우 이동 범위
  const centerX = 50; // 중앙 기준

  // Y축은 땅 영역(하단 30%)에서만 움직임
  const groundMinY = 75; // 땅 시작 위치
  const groundMaxY = 95; // 땅 끝 위치
  const baseY = (groundMinY + groundMaxY) / 2; // 중간 위치
  const verticalWiggle = 5; // 상하 움직임

  // 위치 계산
  let x = centerX + Math.sin(time * 0.3 + step * 10) * movementRadiusX + Math.cos(time * 0.5) * 5;
  let y = baseY + Math.sin(time * 0.8 + step * 5) * verticalWiggle;

  // 경계 제한 (땅 영역 내에서만)
  x = Math.max(10, Math.min(90, x));
  y = Math.max(groundMinY, Math.min(groundMaxY, y));

  bugPositions[step] = {
    left: `${x}%`,
    top: `${y}%`
  };

  bugAnimationIds[step] = requestAnimationFrame(() => animateBug(step));
}

// 오리 걷기 애니메이션 (땅 영역 30%에서만 움직이도록 수정)
function animateDuck() {
  const time = Date.now() / 1000;

  // 땅 영역: 하단 75~95% 구간 (코드 70% + 땅 30%)
  const movementRadiusX = 25; // 이동 범위
  const centerX = 30; // 왼쪽 영역

  const groundMinY = 75; // 땅 시작 위치
  const groundMaxY = 95; // 땅 끝 위치
  const baseY = (groundMinY + groundMaxY) / 2;
  const verticalBob = 5; // 상하 움직임

  // 위치 계산
  let x = centerX + Math.sin(time * 0.4) * movementRadiusX;
  let y = baseY + Math.sin(time * 2) * verticalBob;

  // 경계 제한 (땅 영역 내에서만)
  x = Math.max(5, Math.min(55, x));
  y = Math.max(groundMinY, Math.min(groundMaxY, y));

  walkingDuckPosition.left = `${x}%`;
  walkingDuckPosition.top = `${y}%`;

  duckAnimationId = requestAnimationFrame(animateDuck);
}

// 버그 애니메이션 시작
function startBugAnimations() {
  const totalSteps = totalStepsComputed.value;
  for (let step = 1; step <= totalSteps; step++) {
    if (!progressiveCompletedSteps.value.includes(step)) {
      animateBug(step);
    }
  }
  // 오리도 함께 시작
  animateDuck();
}

// 버그 애니메이션 중지
function stopBugAnimations() {
  const totalSteps = totalStepsComputed.value || 3;
  for (let step = 1; step <= totalSteps; step++) {
    if (bugAnimationIds[step]) {
      cancelAnimationFrame(bugAnimationIds[step]);
      bugAnimationIds[step] = null;
    }
  }
  // 오리 애니메이션도 중지
  if (duckAnimationId) {
    cancelAnimationFrame(duckAnimationId);
    duckAnimationId = null;
  }
}

// 오리가 지렁이를 잡으러 가는 애니메이션
function shootBug(targetStep, isHit) {
  if (!editorFrameRef.value) return;

  const frame = editorFrameRef.value;
  const rect = frame.getBoundingClientRect();

  // 오리의 현재 위치에서 출발 (백분율을 픽셀로 변환)
  const duckLeft = parseFloat(walkingDuckPosition.left);
  const duckTop = parseFloat(walkingDuckPosition.top);
  const startX = (duckLeft / 100) * rect.width;
  const startY = (duckTop / 100) * rect.height;

  // 버그 위치 계산 (이펙트가 버그 위치에서 발현되도록)
  const bugLeft = parseFloat(bugPositions[targetStep].left);
  const bugTop = parseFloat(bugPositions[targetStep].top);

  // 에디터 프레임 기준 좌표로 변환
  const targetX = (bugLeft / 100) * rect.width;
  const targetY = (bugTop / 100) * rect.height;

  // 오리 날아가기 시작 - 위치를 먼저 설정
  bulletPosition.value = { x: startX, y: startY };

  // nextTick을 사용하여 DOM 업데이트 후 표시
  nextTick(() => {
    showBullet.value = true;
    startDuckFlight();
  });

  function startDuckFlight() {

    const duration = 1200; // 속도를 느리게 조정 (500 -> 1200ms)
    const startTime = performance.now();

    function animateBullet(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easeProgress = 1 - Math.pow(1 - progress, 3);

      // 포물선 궤적 계산 (더 자연스러운 날아가기)
      const arcHeight = 50; // 포물선 높이
      const parabola = 4 * arcHeight * progress * (1 - progress);

      bulletPosition.value.x = startX + (targetX - startX) * easeProgress;
      bulletPosition.value.y = startY + (targetY - startY) * easeProgress - parabola;

      // [2026-02-03] 날아가는 방향(궤적의 기울기)에 맞춰 이미지 회전 계산
      const dx = targetX - startX;
      // 포물선 궤적의 1차 미분값을 활용해 현재 진행 방향의 기울기 산출
      const dy_dp = (targetY - startY) - 4 * arcHeight * (1 - 2 * progress);
      const angle = Math.atan2(dy_dp, dx) * (180 / Math.PI);
      bulletRotation.value = angle;

      if (progress < 1) {
        requestAnimationFrame(animateBullet);
      } else {
        // [2026-02-03] 도착 시 회전값 초기화 (정면을 보고 먹기 위해)
        bulletRotation.value = 0;

        // 화면 흔들림 효과
        isShaking.value = true;
        
        // [2026-02-03] 버그 타격 시 오리 이미지(메인 및 헤더)를 먹기 상태로 전환
        if (isHit) {
          isEating.value = true;
          headerEatingStep.value = targetStep;

          // [2026-02-03] 정답일 경우 지렁이를 잡아먹는 시간을 1200ms로 연장하여 가시성 확보
          scheduleTimeout(() => {
            showBullet.value = false; // 먹기 완료 후 비행 오브젝트 제거
            isShaking.value = false;

            // [2026-02-03] 비행체가 사라진 후에도 바닥 오리가 잠시 더 냠냠거리는 여운을 남김 (800ms 추가)
            scheduleTimeout(() => {
              isEating.value = false;
              headerEatingStep.value = null;
            }, 800);
          }, 1200);
        } else {
          // 오답일 경우 타겟 위치에서 슬픈 상태 활성화
          isSad.value = true;

          // 2초 후 비행 오브젝트 제거 및 상태 해제 (타겟 지점에서 머물기)
          scheduleTimeout(() => {
            showBullet.value = false;
            isSad.value = false;
            isShaking.value = false;
          }, 2000);
        }

        if (isHit) {
          hitEffectPosition.value = { x: targetX, y: targetY };
          hitEffectText.value = ['YUMMY!', 'DELICIOUS!', 'NOM NOM!', 'TASTY!'][Math.floor(Math.random() * 4)];
          showHitEffect.value = true;

          // 해당 버그 애니메이션 중지
          if (bugAnimationIds[targetStep]) {
            cancelAnimationFrame(bugAnimationIds[targetStep]);
            bugAnimationIds[targetStep] = null;
          }

          scheduleTimeout(() => { showHitEffect.value = false; }, 1500);
        } else {
          missEffectPosition.value = { x: targetX + 30, y: targetY - 20 };
          showMissEffect.value = true;
          scheduleTimeout(() => { showMissEffect.value = false; }, 1000);
        }
      }
    }

    requestAnimationFrame(animateBullet);
  }
}

// 상태 관리
const currentView = ref('menu');
const showExitConfirm = ref(false);
let pendingStepContinue = null;

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

// ============================================
// LocalStorage 마이그레이션
// ============================================

function migrateGameDataToStages() {
  const data = loadGameData();
  if (!data || data._migrated_v3) return;

  const completed = data.completedProblems || [];
  const newCompleted = [...completed];

  // P1 step1 → S1 step1
  if (completed.includes('progressive_P1_step1')) {
    if (!newCompleted.includes('progressive_S1_step1')) newCompleted.push('progressive_S1_step1');
  }
  // P1 step2 → S2 step1
  if (completed.includes('progressive_P1_step2')) {
    if (!newCompleted.includes('progressive_S2_step1')) newCompleted.push('progressive_S2_step1');
  }
  // P1 step3 → S2 step2
  if (completed.includes('progressive_P1_step3')) {
    if (!newCompleted.includes('progressive_S2_step2')) newCompleted.push('progressive_S2_step2');
  }
  // P1 mission complete → S1 + S2
  if (completed.includes('progressive_P1')) {
    if (!newCompleted.includes('progressive_S1')) newCompleted.push('progressive_S1');
    if (!newCompleted.includes('progressive_S2')) newCompleted.push('progressive_S2');
  }

  // P2→S4, P3→S5, P4→S6, P5→S7
  const mapping = { 'P2': 'S4', 'P3': 'S5', 'P4': 'S6', 'P5': 'S7' };
  for (const [oldId, newId] of Object.entries(mapping)) {
    for (const entry of completed) {
      if (entry.startsWith(`progressive_${oldId}`)) {
        const newEntry = entry.replace(`progressive_${oldId}`, `progressive_${newId}`);
        if (!newCompleted.includes(newEntry)) newCompleted.push(newEntry);
      }
    }
  }

  // 기존 S3~S6 데이터를 S4~S7로 시프트 (덮어쓰기 방지를 위해 역순 적용)
  const shiftMapping = { 'S6': 'S7', 'S5': 'S6', 'S4': 'S5', 'S3': 'S4' };
  for (const oldId of Object.keys(shiftMapping)) {
    const newId = shiftMapping[oldId];
    for (const entry of completed) {
      if (entry.startsWith(`progressive_${oldId}`)) {
        const newEntry = entry.replace(`progressive_${oldId}`, `progressive_${newId}`);
        if (!newCompleted.includes(newEntry)) newCompleted.push(newEntry);
      }
    }
  }

  data.completedProblems = newCompleted;
  data._migrated_v3 = true;
  saveGameData(data);
  Object.assign(gameData, data);
}

// ============================================
// API 데이터 로딩
// ============================================
const fetchProgressiveProblems = async () => {
  try {
    loading.value = true;
    error.value = null;

    // Practice API를 사용해서 전체 details를 가져오기
    const response = await axios.get('/api/core/practices/bughunt01/');

    console.log('🔍 API Response:', response);
    console.log('📦 Response Data:', response.data);
    console.log('📄 Details:', response.data.details);

    // details 배열의 각 항목에서 content_data를 추출하여 progressiveProblems 배열 생성
    // details는 [{ id: 'bughunt01_S1', content_data: {...} }, ...] 형태
    if (response.data.details && Array.isArray(response.data.details)) {
      progressiveProblems.value = response.data.details
        .map(detail => detail.content_data)
        .filter(data => data && data.id); // id가 있는 유효한 문제만 필터링
    } else {
      progressiveProblems.value = [];
    }

    console.log('✅ Loaded progressive problems from DB:', progressiveProblems.value);
    console.log('📊 Number of problems:', progressiveProblems.value.length);
  } catch (err) {
    console.error('❌ Error fetching progressive problems:', err);
    console.error('Error details:', err.response?.data);
    error.value = '데이터를 불러오는 중 오류가 발생했습니다.';
  } finally {
    loading.value = false;
  }
};

// 라이프사이클
onMounted(async () => {
  // DB에서 데이터 로딩
  await fetchProgressiveProblems();
  // LocalStorage 마이그레이션 먼저 실행
  migrateGameDataToStages();

  // 이미지 preload (애니메이션 전에 미리 로딩)
  const imagesToPreload = [duckIdle, duckEating, duckFlying, duckSad, unitDuck];
  imagesToPreload.forEach(src => {
    const img = new Image();
    img.src = src;
  });

  // 맵 모드 체크
  if (route.query.missionId) {
    const missionId = route.query.missionId;
    const missionIndex = progressiveProblems.value.findIndex(m => m.id === missionId);

    if (missionIndex !== -1) {
      const mission = progressiveProblems.value[missionIndex];
      // [수정] 맵에서 미션을 클릭하면 항상 1-1부터 시작하도록 변경하여 순차적 진행 보장
      startProgressiveMission(mission, missionIndex, 1);
    }
  }

});

onUnmounted(() => {
  clearAllTimeouts();
  stopBugAnimations();
});
</script>




<style scoped>
/* ============================================ */
/* [NEW] Custom Layout Styles for Progressive Mission */
/* ============================================ */

/* Force Compact Header */
:deep(.header.compact) {
  padding: 10px 20px !important;
  min-height: 60px;
}

.progressive-main-layout {
  display: grid;
  grid-template-columns: 1fr 2fr; /* 1:2 Split */
  gap: 1rem; /* Reduced gap */
  height: calc(100vh - 90px) !important; /* Adjusted for smaller header */
  padding: 0.5rem 1.5rem 1.5rem 1.5rem; /* Reduced top padding */
  box-sizing: border-box;
}

.left-panel-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.left-panel-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(10, 10, 15, 0.85); /* Dark unified body background */
  border: 1px solid rgba(79, 195, 247, 0.2);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
}

.panel-box.scenario-box {
  height: 35%; /* Fixed reduced height */
  flex: none; /* Do not grow */
  background: transparent;
  border: none;
  padding: 1.5rem;
  overflow-y: auto;
  border-bottom: 1px solid rgba(79, 195, 247, 0.1);
}

.panel-title {
  font-size: 1.1rem;
  font-weight: bold;
  color: var(--neon-cyan);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.scenario-text {
  font-size: 1rem;
  line-height: 1.6;
  color: #e0f7fa;
  white-space: pre-wrap;
}

.clue-panel {
  flex: 1; /* Take all remaining space (Expanded Log Window) */
  min-height: 0; /* flex child가 shrink 가능하도록 */
  background: rgba(0, 0, 0, 0.4);
  border-top: 1px solid rgba(79, 195, 247, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.clue-header {
  padding: 0.6rem 1rem; /* Compact header */
  background: rgba(79, 195, 247, 0.05);
  border-bottom: 1px solid rgba(79, 195, 247, 0.1);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #fff;
  font-weight: bold;
}

.clue-content {
  flex: 1;
  overflow-y: auto;
  padding: 0.8rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  min-height: 0; /* flex child가 shrink 가능하도록 */
}

.clue-item {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  font-size: 0.9rem;
  padding: 0.8rem;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.03);
  animation: slideIn 0.3s ease-out;
  border-left: 3px solid transparent;
}

.clue-badge {
  font-size: 0.7rem;
  font-weight: bold;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  background: #333;
  width: fit-content;
  letter-spacing: 0.5px;
}

.clue-text {
  flex: 1;
  line-height: 1.6;
  color: #90EE90; /* 연두색 */
  white-space: pre-wrap;
  font-family: 'JetBrains Mono', 'Consolas', monospace;
  font-size: 0.85rem;
}

/* ERROR 타입 특별 스타일 */
.clue-item:has(.clue-badge:contains('ERROR')) {
  background: rgba(244, 67, 54, 0.08);
  border-left-color: #f44336;
  padding: 1rem;
}

.clue-item:has(.clue-badge:contains('ERROR')) .clue-text {
  color: #ffcdd2;
  background: rgba(0, 0, 0, 0.3);
  padding: 0.8rem;
  border-radius: 4px;
  border: 1px solid rgba(244, 67, 54, 0.3);
}

/* Clue Types */
.clue-item:has(.clue-badge:contains('INFO')) .clue-badge { background: #2196f3; color: white; }
.clue-item:has(.clue-badge:contains('INFO')) { border-left-color: #2196f3; }

.clue-item:has(.clue-badge:contains('WARN')) .clue-badge { background: #ff9800; color: black; }
.clue-item:has(.clue-badge:contains('WARN')) { border-left-color: #ff9800; }

.clue-item:has(.clue-badge:contains('ERROR')) .clue-badge { background: #f44336; color: white; }

.clue-item:has(.clue-badge:contains('SUCCESS')) .clue-badge { background: #4caf50; color: white; }
.clue-item:has(.clue-badge:contains('SUCCESS')) { border-left-color: #4caf50; }

.clue-item:has(.clue-badge:contains('HINT')) .clue-badge { background: #9c27b0; color: white; }
.clue-item:has(.clue-badge:contains('HINT')) { border-left-color: #9c27b0; }

@keyframes slideIn {
  from { opacity: 0; transform: translateX(-10px); }
  to { opacity: 1; transform: translateX(0); }
}

/* Ensure right panel frame matches style */
.full-code-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  overflow: hidden;
}


/* 성공 헤더 스타일 */
.success-header {
  background: linear-gradient(90deg, rgba(79, 195, 247, 0.1), rgba(0, 170, 255, 0.1));
  border-bottom: 2px solid #4fc3f7;
}

/* 해결 완료 상태 */
.status-success {
  color: #4fc3f7;
  font-weight: bold;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

/* 로그창 주목 효과 - 강력한 펄스 + 포인터 */
.clue-panel.attention-pulse {
  animation: attentionPulse 1.5s ease-in-out;
  position: relative;
}

.clue-panel.attention-pulse::before {
  content: '👈 주목!';
  position: absolute;
  top: 50%;
  right: -80px;
  transform: translateY(-50%);
  font-size: 1.5rem;
  font-weight: bold;
  color: #4fc3f7;
  text-shadow: 0 0 20px rgba(79, 195, 247, 1);
  animation: pointerBounce 0.6s ease-in-out infinite;
  z-index: 1000;
}

@keyframes attentionPulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 10px rgba(79, 195, 247, 0.3);
    border-color: rgba(79, 195, 247, 0.3);
  }
  25% {
    transform: scale(1.05);
    box-shadow:
      0 0 40px rgba(79, 195, 247, 1),
      0 0 80px rgba(79, 195, 247, 0.8),
      inset 0 0 30px rgba(79, 195, 247, 0.3);
    border-color: #4fc3f7;
  }
  50% {
    transform: scale(1.03);
    box-shadow:
      0 0 60px rgba(79, 195, 247, 1),
      0 0 100px rgba(79, 195, 247, 0.8),
      inset 0 0 40px rgba(79, 195, 247, 0.4);
    border-color: #4fc3f7;
  }
  75% {
    transform: scale(1.05);
    box-shadow:
      0 0 40px rgba(79, 195, 247, 1),
      0 0 80px rgba(79, 195, 247, 0.8),
      inset 0 0 30px rgba(79, 195, 247, 0.3);
    border-color: #4fc3f7;
  }
}

@keyframes pointerBounce {
  0%, 100% {
    transform: translateY(-50%) translateX(0);
  }
  50% {
    transform: translateY(-50%) translateX(-10px);
  }
}

/* 슬라이드 다운 애니메이션 (헤더) */
.slide-down-enter-active {
  animation: slideDown 0.5s ease-out;
}

@keyframes slideDown {
  0% {
    opacity: 0;
    transform: translateY(-20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 페이드 업 애니메이션 (입력창) */
.fade-up-enter-active {
  animation: fadeUp 0.6s ease-out 0.2s both;
}

@keyframes fadeUp {
  0% {
    opacity: 0;
    transform: translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}


@keyframes duckBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

/* 말풍선 팝 트랜지션 */
.speech-pop-enter-active {
  animation: speechPopIn 0.4s ease-out;
}

.speech-pop-leave-active {
  animation: speechPopOut 0.3s ease-in;
}

@keyframes speechPopIn {
  0% {
    opacity: 0;
    transform: translateY(-50%) scale(0.5);
  }
  50% {
    transform: translateY(-50%) scale(1.1);
  }
  100% {
    opacity: 1;
    transform: translateY(-50%) scale(1);
  }
}

@keyframes speechPopOut {
  0% {
    opacity: 1;
    transform: translateY(-50%) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateY(-50%) scale(0.8);
  }
}

/* 오리 팝 트랜지션 */
.duck-pop-enter-active {
  animation: duckPopIn 0.5s ease-out;
}

.duck-pop-leave-active {
  animation: duckPopOut 0.3s ease-in;
}

@keyframes duckPopIn {
  0% {
    opacity: 0;
    transform: scale(0) rotate(-20deg);
  }
  60% {
    transform: scale(1.2) rotate(5deg);
  }
  100% {
    opacity: 1;
    transform: scale(1) rotate(0);
  }
}

@keyframes duckPopOut {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  100% {
    opacity: 0;
    transform: scale(0.5) translateY(-20px);
  }
}

/* ============================================
   데이터 로딩/에러 오버레이
   ============================================ */
.loading-overlay,
.error-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-content,
.error-content {
  text-align: center;
  color: #fff;
  font-family: 'Inter', sans-serif;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top-color: #58cc02;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-content p {
  font-size: 1.2rem;
  color: #fff;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.error-content p {
  font-size: 1.2rem;
  margin-bottom: 20px;
  color: #fa5252;
}

.retry-btn {
  padding: 10px 30px;
  background: #58cc02;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s ease;
}

.retry-btn:hover {
  background: #46a302;
}

/* ============================================
   Protein Shake 스타일
   ============================================ */
/* 헤더 Shake 카운터 (메인과 동일한 스타일) */
.shake-counter {
  background: rgba(56, 189, 248, 0.1);
  color: #38bdf8;
  padding: 0.5rem 1rem;
  border-radius: 99px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(56, 189, 248, 0.2);
  transition: all 0.3s;
  margin-right: 10px;
}

.shake-icon {
  width: 20px !important;
  height: 20px !important;
  min-width: 20px;
  min-height: 20px;
  filter: drop-shadow(0 0 5px rgba(56, 187, 248, 0.6));
  flex-shrink: 0;
  display: inline-block;
  color: #38bdf8;
}

.shake-count-text {
  color: #38bdf8;
  font-weight: 700;
}

/* 미션 완료 화면 - 레이아웃 조정 */
.report-header.mission-summary {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1rem;
}

.report-header.mission-summary .project-info {
  width: 100%;
}

.report-header.mission-summary .project-info h2 {
  margin-top: 10px;
}

.report-header .score-summary.center-focus {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-top: 0.5rem;
  width: min(100%, 560px);
}

.report-header .score-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 0.5rem 1.5rem 0.2rem;
}

.report-header .score-item .value {
  font-size: clamp(4rem, 9vw, 5.2rem);
  line-height: 1;
}

/* 미션 완료 화면 - 획득한 Shake 표시 */
.shake-earned {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0.75rem 1.3rem;
  background: rgba(56, 189, 248, 0.16);
  border: 1.5px solid rgba(56, 189, 248, 0.45);
  border-radius: 16px;
  box-shadow: 0 4px 18px rgba(56, 189, 248, 0.2);
  transition: all 0.3s ease;
}

.shake-earned:hover {
  background: rgba(56, 189, 248, 0.2);
  border-color: rgba(56, 189, 248, 0.6);
  box-shadow: 0 6px 30px rgba(56, 189, 248, 0.3);
}

.shake-earned-icon {
  width: 28px;
  height: 28px;
  color: #38bdf8;
  filter: drop-shadow(0 0 10px rgba(56, 187, 248, 0.8));
  flex-shrink: 0;
  animation: shake-pulse 2s ease-in-out infinite;
}

@keyframes shake-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.shake-earned-text {
  color: #38bdf8;
  font-weight: 700;
  font-size: 1.05rem;
  text-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
}

/* 실패/감점 정보도 한눈에 보이도록 카드형 정렬 */
.penalty-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  width: 100%;
  gap: 0.5rem;
  margin-top: 0.4rem;
}

.penalty-item {
  background: rgba(255, 0, 0, 0.08);
  border: 1px solid rgba(255, 51, 102, 0.22);
  border-radius: 10px;
  padding: 0.55rem 0.7rem;
}

</style>
