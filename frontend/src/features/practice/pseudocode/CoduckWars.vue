<!--
수정일: 2026-02-10
수정 내용: 이전 작업 버전(SKN20-FINAL-5TEAM_before)으로 pseudocode 프론트엔드 코드 복구
-->
<template>
  <div class="coduck-wars-container">
    <!-- BACKGROUND WATERMARK -->
    <div class="bg-watermark">CODUCK WARS</div>
    <div class="scan-line"></div>

    <!-- HEADER -->
    <header class="war-room-header">
      <div class="chapter-info">
        <span class="chapter-title">CHAPTER {{ gameState.currentStageId }}: {{ currentMission.title || '로딩 중...' }}</span>
        <span class="sub-info">{{ currentMission.subModuleTitle || 'LEAKAGE_GUARD' }}</span>
      </div>
      <div class="integrity-monitor">
        <span class="integrity-label">정화 무결성</span>
        <div class="hp-bar-bg">
             <div class="hp-bar-fill" :style="{ width: Math.max(0, gameState.playerHP) + '%' }"></div>
        </div>
        <span class="integrity-val">{{ Math.max(0, gameState.playerHP) }}%</span>

      </div>
    </header>

    <!-- MAIN VIEWPORT [2026-02-11] UI 레이아웃 2단 구성(Battle Grid) 복원 -->
    <main class="viewport">
        
      <!-- [2026-02-11] 사이드바 가이드 버튼 -->
      <button class="btn-guide-floating" @click="toggleGuide" :class="{ 'is-open': isGuideOpen }">
          <span class="icon">?</span>
          <span class="label">CHAPTER</span>
      </button>

      <!-- [2026-02-11] 사이드바 가이드 패널 -->
      <div class="guide-sidebar" :class="{ 'sidebar-open': isGuideOpen }">
          <div class="sidebar-header">
              <span class="sh-title">MISSION CHAPTERS</span>
              <button class="sh-close" @click="toggleGuide">×</button>
          </div>
          <div class="sidebar-content">
              <!-- [2026-02-11] 미션 엔지니어링 가이드 (의사코드 작성 원칙) -->
            <div v-if="currentMission.designContext?.writingGuide" class="guide-step-card g-active mt-4">
                <div class="gs-header-row">
                    <div class="gs-icon"><Lightbulb class="w-5 h-5 text-blue-400" /></div>
                    <div class="gs-info">
                        <span class="gs-step text-blue-400">ENGINEERING_GUIDE</span>
                        <p class="gs-text">의사코드 작성 전략</p>
                    </div>
                </div>
                <div class="gs-hint-content hint-box-blue">
                    <p class="hint-text-small">{{ currentMission.designContext.writingGuide }}</p>
                </div>
            </div>

            <div v-for="(guide, idx) in currentMission.guides" 
                  :key="idx"
                  class="guide-step-card"
                  :class="{ 'g-active': idx === selectedGuideIdx }"
                  @click="handleGuideClick(idx)"
              >
                  <div class="gs-header-row">
                      <div class="gs-icon">{{ guide.icon }}</div>
                      <div class="gs-info">
                          <div class="gs-step">STEP {{ idx + 1 }}</div>
                          <div class="gs-text">{{ guide.text.split(':')[1] || guide.text }}</div>
                      </div>
                  </div>
                  <div class="gs-hint-content" v-if="idx === selectedGuideIdx">
                      <div class="hint-label">💡 TACTICAL ADVICE</div>
                      <p class="hint-body text-[11px] leading-tight">"{{ guide.coduckMsg }}"</p>
                  </div>
              </div>
          </div>
      </div>

      <!-- [2026-02-11] 2단 레이아웃 핵심 컨테이너 (Combat Grid) -->
      <div class="combat-grid w-full h-full">
          
          <!-- LEFT PANEL: ENTITY CARD [2026-02-11] 코덕 캐릭터 및 상태창 -->
          <aside class="entity-card">
              <div class="entity-header">
                  <span class="e-type">ANALYZE_UNIT</span>
                  <span class="e-status">SYSTEM_ACTIVE</span>
              </div>

              <div class="visual-frame">
                  <!-- [2026-02-11] 코덕 캐릭터 이미지 연결 -->
                  <img src="@/assets/image/duck_det.png" alt="Coduck Detective" class="coduck-portrait" />
                  <div class="scan-overlay"></div>
                  
                  <!-- [2026-02-11] 손상 시 표시 -->
                  <div v-if="gameState.playerHP < 40" class="disconnect-tag">INTEGRITY_COMPROMISED</div>
              </div>

              <!-- [2026-02-11] 코덕 실시간 대사창 [2026-02-13] 모든 단계에서 시나리오가 보이도록 조건 확장 -->
              <div class="dialogue-box">
                  <span class="speaker">문제 시나리오</span>
                  <p class="dialogue-text">"{{ (isInteractionPhase && currentMission.scenario) ? currentMission.scenario : (gameState.coduckMessage || '데이터 흐름을 분석 중입니다...') }}"</p>
              </div>


          </aside>

          <!-- RIGHT PANEL: DECISION ENGINE [2026-02-11] 단계별 인터랙션 영역 -->
          <section class="decision-panel relative">
              <div v-if="gameState.phase.startsWith('DIAGNOSTIC')">
                  <div class="system-status-row">
                      <span v-if="gameState.phase === 'DIAGNOSTIC_1'">STEP_01: CONCEPT_IDENTIFICATION</span>
                      <span v-else-if="gameState.phase === 'PSEUDO_WRITE'">STEP_02: PSEUDO_ARCHITECTURE</span>
                  </div>
                  
                  <!-- 지문 내 코드 블록 렌더링 영역 [2026-02-12] 페이즈 무관하게 컨텍스트가 있으면 표시 -->
                  <div v-if="diagnosticProblemParts" class="diagnostic-code-box">
                      <div class="diagnostic-instruction">{{ diagnosticProblemParts.instruction }}</div>
                      <div class="diagnostic-code">{{ diagnosticProblemParts.code }}</div>
                  </div>

                  <h3 v-if="gameState.phase === 'DIAGNOSTIC_1' && diagnosticQuestion.type !== 'CHOICE'" class="big-question">
                      {{ diagnosticQuestion.question }}
                  </h3>
                  
                  <!-- [2026-02-12] PHASE 1 전용 블록 -->
                  <div v-if="gameState.phase === 'DIAGNOSTIC_1'" class="diagnostic-content-area">
                      <!-- 서술형 UI -->
                      <div v-if="diagnosticQuestion.type === 'DESCRIPTIVE'" class="descriptive-interaction-area">
                          <div v-if="gameState.diagnosticResult && !gameState.isEvaluatingDiagnostic" class="diagnostic-result-card animate-fadeIn">
                              <div class="dr-header">
                                  <span class="dr-label">AI_ARCHITECT_VERDICT</span>
                                  <span class="dr-score" :class="gameState.diagnosticResult.score >= 70 ? 'text-green-400' : 'text-yellow-400'">{{ gameState.diagnosticResult.score }} PTS</span>
                              </div>
                              <div class="dr-analysis">"{{ gameState.diagnosticResult.analysis }}"</div>
                              <div class="dr-feedback">{{ gameState.diagnosticResult.feedback }}</div>
                              <div v-if="diagnosticQuestion.evaluationRubric?.correctAnswer" class="model-answer-box animate-fadeIn">
                                  <div class="ma-header"><Brain class="w-4 h-4 text-purple-400" /><span class="ma-label">모범 답안</span></div>
                                  <p class="ma-content">{{ diagnosticQuestion.evaluationRubric.correctAnswer }}</p>
                              </div>
                          </div>
                          <textarea v-model="gameState.diagnosticAnswer" class="diagnostic-textarea" placeholder="분석 내용을 입력하세요..." :disabled="gameState.isEvaluatingDiagnostic"></textarea>
                          <button @click="submitDiagnostic()" class="btn-execute-large w-full-btn" :disabled="(!gameState.diagnosticAnswer || gameState.diagnosticAnswer.trim().length < 5) && !gameState.diagnosticResult || gameState.isEvaluatingDiagnostic">
                              <template v-if="gameState.isEvaluatingDiagnostic">분석 중... <RotateCcw class="w-5 h-5 ml-2 animate-spin" /></template>
                              <template v-else-if="gameState.diagnosticResult">다음 단계 진행 <ArrowRight class="w-5 h-5 ml-2" /></template>
                              <template v-else>분석 완료 제출 <CheckCircle class="w-5 h-5 ml-2" /></template>
                          </button>
                      </div>
                      <!-- 객관식 UI (CHOICE) [2026-02-12] 코덕 비주얼 복구 -->
                      <div v-else-if="diagnosticQuestion.type === 'CHOICE'" class="choice-interaction-area">
                          <div class="choice-visual-frame mb-8">
                              <div class="choice-coduck">
                                  <img :src="currentMission.character?.image || '@/assets/image/duck_det.png'" alt="Coduck Interviewer" />
                              </div>
                              <div class="choice-speech-bubble">
                                  <div class="bubble-tail"></div>
                                  <p class="bubble-text">{{ diagnosticQuestion.question }}</p>
                              </div>
                          </div>
                          <div class="options-list">
                              <div v-for="(opt, idx) in diagnosticQuestion.options" :key="idx" @click="submitDiagnostic(idx)" class="option-card">
                                  <div class="opt-index">{{ idx + 1 }}</div>
                                  <div class="opt-main text-lg">{{ opt.text }}</div>
                                  <div class="opt-arrow"><ArrowRight /></div>
                              </div>
                          </div>
                      </div>
                  </div>
                  <!-- AI 아키텍트 분석 오버레이 (진단 단계) -->
                  <div v-if="gameState.isEvaluatingDiagnostic" class="ai-loading-overlay">
                      <LoadingDuck message="데이터 흐름 및 논리적 타당성을 정밀 분석 중입니다..." />
                  </div>
              </div>

              <!-- [2026-02-11] PHASE: PSEUDO_WRITE (Step 2: 아키텍처 설계) -->
              <div v-else-if="gameState.phase === 'PSEUDO_WRITE'" class="space-y-4 flex flex-col h-full max-w-5xl mx-auto w-full">
                  <!-- AI 아키텍트 분석 오버레이 (의사코드 심화 분석 단계) [추가: 2026-02-13] -->
                  <div v-if="isProcessing" class="ai-loading-overlay">
                      <LoadingDuck message="작성하신 설계의 5차원 아키텍처 정밀 분석 및 Python 코드 변환 중입니다..." />
                  </div>
                  <!-- [2026-02-12] 이미지 싱크: 메인 타이틀 및 설명 개편 (미션/제약조건 노출) [폰트 상향 및 중복 제거] -->
                  <div class="mission-instruction-compact">
                      <div class="mi-section">
                          <h4 class="mi-title text-blue-400">[미션]</h4>
                          <p class="mi-desc">{{ currentMission.designContext?.description }}</p>
                      </div>
                      <div class="mi-section mi-border-top">
                          <h4 class="mi-title text-amber-400">[필수 포함 조건 (Constraint)]</h4>
                          <p class="mi-desc-small">{{ currentMission.designContext?.writingGuide?.replace('[필수 포함 조건 (Constraint)]\n', '') }}</p>
                      </div>
                  </div>

                  <div class="editor-layout w-full flex flex-col flex-1">
                      <div class="editor-body w-full flex-1 flex flex-col">
                          <!-- 의사코드 입력 에디터 -->
                          <div class="monaco-wrapper w-full h-[320px] border border-slate-700/50 rounded-xl overflow-hidden shadow-2xl">
                              <VueMonacoEditor
                                  theme="vs-dark"
                                  language="python"
                                  :options="monacoOptions"
                                  @mount="handleMonacoMount"
                                  class="w-full h-full"
                              />
                          </div>
                      </div>

                       <div class="editor-header w-full mt-4 flex justify-between items-end">
                          <!-- [2026-02-13] 실시간 규칙 체크리스트 UI: 하단 배치 -->
                          <div class="rule-checklist-bar flex flex-wrap gap-2 mb-2">
                              <div 
                                  v-for="rule in ruleChecklist" 
                                  :key="rule.id"
                                  class="rule-chip"
                                  :class="{ 'is-completed': rule.completed }"
                              >
                                  <CheckCircle v-if="rule.completed" class="w-3.5 h-3.5" />
                                  <div v-else class="rule-dot"></div>
                                  <span class="rule-label">{{ rule.label }}</span>
                              </div>
                          </div>

                          <div class="actions flex items-center gap-6 relative">
                              <!-- [2026-02-13] 실시간 힌트 오리 & 말풍선 (유동적 위치) -->
                              <Transition name="fade-slide">
                                <div v-if="showHintDuck" class="hint-duck-wrapper">
                                    <div class="hint-bubble">
                                        <div class="hb-content">{{ dynamicHintMessage || '분석 중입니다...' }}</div>
                                        <div class="hb-tail"></div>
                                    </div>
                                    <img src="/image/unit_duck.png" alt="Hint Duck" class="hint-unit-img" />
                                </div>
                              </Transition>

                              <button 
                                  :disabled="!canSubmitPseudo || isProcessing"
                                  @click="submitPseudo"
                                  class="btn-execute-large"
                              >
                                  심화 분석 시작 <Play class="w-4 h-4" />
                              </button>
                          </div>
                      </div>
                  </div>
              </div>

              <!-- [STEP 3] Python 시각화 및 분기 단계 [2026-02-13] decision-panel 내부로 이동 -->
              <div v-else-if="gameState.phase === 'PYTHON_VISUALIZATION'" class="visualization-phase h-full">
                  <CodeFlowVisualizer
                      :pseudo-code="gameState.phase3Reasoning"
                      :python-code="evaluationResult?.converted_python"
                      :score="evaluationResult?.overall_score"
                      :feedback="evaluationResult?.python_feedback"
                      :senior-advice="evaluationResult?.senior_advice"
                      :is-low-effort="evaluationResult?.is_low_effort"
                      :mission-title="currentMission?.title"
                      :mission-desc="currentMission?.designContext?.description"
                      :mission-constraints="currentMission?.designContext?.writingGuide"
                      :question-data="deepQuizQuestion"
                      @next="handlePythonVisualizationNext"
                      @select-option="submitDeepQuiz"
                      @retry="retryDesign"
                  />
              </div>

              <!-- [STEP 3-1] Tail Question 단계 (80점 미만) [2026-02-13] decision-panel 내부로 이동 -->
              <div v-else-if="gameState.phase === 'TAIL_QUESTION'" class="tail-question-phase">
                  <div class="tail-question-area">
                      <div class="tq-header">
                          <span class="tq-icon">💡</span>
                          <span class="tq-title">개념 보완이 필요해요 (Score: {{ evaluationResult?.overall_score }})</span>
                      </div>
                      
                      <div class="tq-content">
                          {{ deepQuizQuestion?.question }}
                      </div>
                      
                      <div class="tq-options">
                          <button 
                              v-for="(option, idx) in deepQuizQuestion?.options" 
                              :key="idx"
                              @click="handleTailSelection(option)"
                              class="btn-tq-option"
                          >
                              {{ option.text }}
                          </button>
                      </div>
                  </div>
              </div>

              <!-- [STEP 3-2] Deep Dive 단계 (80점 이상) [2026-02-13] decision-panel 내부로 이동 -->
              <div v-else-if="gameState.phase === 'DEEP_QUIZ'" class="deep-dive-phase">
                   <div class="deep-dive-container">
                      <h3 class="deep-dive-title">🚀 심화 학습 (Deep Dive)</h3>
                      <div class="deep-dive-content">
                          <p class="deep-dive-question">{{ deepQuizQuestion?.question }}</p>
                          <div class="options-list deep-dive-options">
                              <button 
                                  v-for="(option, idx) in deepQuizQuestion?.options" 
                                  :key="idx"
                                  @click="submitDeepQuiz(idx)"
                                  class="option-card full-width-card"
                              >
                                  <span class="opt-index">{{ idx + 1 }}</span>
                                  <span class="opt-main">{{ option.text }}</span>
                              </button>
                          </div>
                      </div>
                   </div>
              </div>

              <!-- [STEP 4] 최종 리포트 (EVALUATION) [2026-02-13] decision-panel 내부로 이동 -->
              <div v-else-if="gameState.phase === 'EVALUATION'" class="evaluation-phase">
                  <!-- [2026-02-13] 복기 학습 모드 시 미션 정보 재노출 -->
                  <div v-if="evaluationResult?.is_low_effort || gameState.hasUsedBlueprint" class="mission-instruction-compact animate-slideDownFade mb-6">
                      <div class="mi-section">
                          <h4 class="mi-title text-blue-400">[미션]</h4>
                          <p class="mi-desc">{{ currentMission?.designContext?.description }}</p>
                      </div>
                      <div class="mi-section mi-border-top">
                          <h4 class="mi-title text-amber-400">[필수 포함 조건 (Constraint)]</h4>
                          <p class="mi-desc-small">{{ currentMission?.designContext?.writingGuide?.replace('[필수 포함 조건 (Constraint)]\n', '') }}</p>
                      </div>
                  </div>
                  <div class="report-card full-width-report">
                      <div class="report-header">
                          <div class="medal-area">
                              <div class="medal-icon" :class="scoreTier.class">{{ scoreTier.icon }}</div>
                              <div class="medal-label">{{ scoreTier.label }}</div>
                          </div>
                          <div class="total-score">
                              <span class="score-val">{{ evaluationResult?.finalScore || 0 }}</span>
                              <span class="score-label">MISSION SCORE</span>
                          </div>
                      </div>

                      <!-- [2026-02-13] 3-Phase Weights Breakdown: 백분율 및 가중치 병기로 명확성 확보 -->
                      <!-- [2026-02-13] 유저 요청: 상세 점수 내역(integrated-score-belt) 숨김 처리 -->
                      <!--
                      <div class="integrated-score-belt">
                          <div class="step-summary">
                              <span class="step-label">DIAGNOSTIC (20%)</span>
                              <div class="step-val-group">
                                  <span class="step-val-main">{{ Math.round(evaluationResult?.gameScore || 0) }}%</span>
                                  <span class="step-val-sub">(+{{ evaluationResult?.diagnosticScoreWeighted }}pts)</span>
                              </div>
                          </div>
                          <div class="step-summary">
                              <span class="step-label">ARCHITECTURE (70%)</span>
                              <div class="step-val-group">
                                  <span class="step-val-main">{{ Math.round(evaluationResult?.aiScore || 0) }}%</span>
                                  <span class="step-val-sub">(+{{ evaluationResult?.designScoreWeighted }}pts)</span>
                              </div>
                          </div>
                          <div class="step-summary">
                              <span class="step-label">ITERATIVE (10%)</span>
                              <div class="step-val-group">
                                  <span class="step-val-main">{{ Math.round(gameState?.iterativeScore || 0) }}%</span>
                                  <span class="step-val-sub">(+{{ evaluationResult?.iterativeScoreWeighted }}pts)</span>
                              </div>
                          </div>
                      </div>
                      -->

                      <div class="evaluation-main-grid">
                          <!-- Radar Chart (5D Metrics) -->
                          <div class="radar-container">
                              <svg viewBox="0 0 200 200" class="radar-svg" preserveAspectRatio="xMidYMid meet">
                                  <!-- Background Circles -->
                                  <circle cx="100" cy="100" r="80" class="radar-bg-circle" />
                                  <circle cx="100" cy="100" r="60" class="radar-bg-circle" />
                                  <circle cx="100" cy="100" r="40" class="radar-bg-circle" />
                                  <circle cx="100" cy="100" r="20" class="radar-bg-circle" />
                                  
                                  <!-- Axis Lines -->
                                  <line v-for="(pos, i) in radarAxes" :key="'ax-'+i" 
                                        x1="100" y1="100" :x2="pos.x" :y2="pos.y" class="radar-axis-line" />
                                  
                                  <!-- Data Polygon -->
                                  <polygon :points="radarPoints" class="radar-poly" />
                                  
                                  <!-- Axis Labels -->
                                  <text v-for="(pos, i) in radarLabels" :key="'lbl-'+i"
                                        :x="pos.x" :y="pos.y" 
                                        :text-anchor="pos.anchor"
                                        :dominant-baseline="pos.baseline"
                                        class="radar-label-text">{{ pos.text }}</text>
                              </svg>
                          </div>

                          <!-- Dimension List with Details -->
                          <div class="dimension-details-grid">
                              <div v-for="dim in evaluationResult?.details" :key="dim.id" class="dim-detail-card">
                                  <div class="dim-card-header">
                                      <span class="dim-label">{{ dim.category.toUpperCase() }}</span>
                                      <span class="dim-val">{{ dim.score }}%</span>
                                  </div>
                                  <div class="dim-progress-mini"><div class="dim-fill-mini" :style="{ width: dim.score + '%' }"></div></div>
                                  <p class="dim-comment">Verdict: {{ dim.comment }}</p>
                                  <p class="dim-improvement" v-if="dim.score < 80">🎯 {{ dim.improvement }}</p>
                              </div>
                          </div>
                      </div>

                      <div class="mentor-feedback">
                          <h3>🤖 AI MONITOR FEEDBACK</h3>
                          <p class="feedback-text">"{{ evaluationResult?.seniorAdvice }}"</p>
                          <div class="blueprint-section" v-if="evaluationResult?.converted_python">
                              <div class="blueprint-header">
                                  <Brain size="16" />
                                  <span>YOUR LOGIC MAPPED TO PYTHON</span>
                              </div>
                              <pre class="blueprint-code"><code>{{ evaluationResult.converted_python }}</code></pre>
                              <div v-if="evaluationResult?.python_feedback" class="python-feedback-mini">
                                  💡 <b>Logic Probe:</b> {{ evaluationResult.python_feedback }}
                              </div>
                          </div>
                      </div>

                      <!-- [2026-02-13] Integrated Tail Question (꼬리질문) / Deep Dive -->
                      <div v-if="evaluationResult?.tailQuestion || evaluationResult?.deepDive" class="integrated-question-section">
                          <div class="iq-container">
                              <h3 class="iq-title">
                                  <AlertOctagon v-if="evaluationResult?.tailQuestion" class="iq-icon text-amber-500" />
                                  <Lightbulb v-else class="iq-icon text-cyan-400" />
                                  {{ evaluationResult?.tailQuestion ? "🧐 Architect's Tail Question (꼬리질문)" : "🚀 Architecture Deep Dive (심화질문)" }}
                              </h3>
                              <p class="iq-question">{{ (evaluationResult?.tailQuestion || evaluationResult?.deepDive)?.question }}</p>
                              
                              <div class="iq-options-grid">
                                  <button v-for="(opt, idx) in (evaluationResult?.tailQuestion || evaluationResult?.deepDive)?.options" 
                                          :key="idx"
                                          @click="handleTailSelection(opt)"
                                          class="iq-option-btn"
                                          :disabled="gameState.iterativeScore !== null"
                                          :class="{ 
                                            'correct': gameState.iterativeScore === 100 && opt.is_correct,
                                            'wrong': gameState.iterativeScore === 0 && !opt.is_correct && activeSelectedOption === opt
                                          }"
                                  >
                                      <span class="opt-id">{{ String.fromCharCode(65 + idx) }}</span>
                                      <span class="opt-txt">{{ opt.text }}</span>
                                  </button>
                              </div>
                              
                              <div v-if="gameState.feedbackMessage" class="iq-feedback-alert" :class="gameState.iterativeScore === 100 ? 'success' : 'warn'">
                                 {{ gameState.feedbackMessage }}
                              </div>
                          </div>
                      </div>

                      <!-- [2026-02-13] Recommended Lectures (YouTube) -->
                      <div v-if="evaluationResult?.recommendedLecture" class="youtube-recommendations">
                          <div class="yr-header">
                              <Play size="18" class="text-blue-400" />
                              <h3>ARCHITECT'S LEARNING LIBRARY</h3>
                          </div>
                          <a :href="evaluationResult.recommendedLecture.url" target="_blank" class="video-card-single">
                              <div class="video-info">
                                  <h4 class="v-title">{{ evaluationResult.recommendedLecture.title }}</h4>
                                  <p class="v-desc">{{ evaluationResult.recommendedLecture.reason }}</p>
                                  <span class="v-cta">강의 보러가기 →</span>
                              </div>
                          </a>
                      </div>

                      <!-- [2026-02-13] YouTube Embed Player Modal -->
                      <div v-if="activeYoutubeId" class="youtube-modal-overlay" @click.self="activeYoutubeId = null">
                          <div class="youtube-modal-content">
                              <button class="modal-close" @click="activeYoutubeId = null">
                                  <X size="24" />
                              </button>
                              <div class="video-responsive">
                                  <iframe 
                                      :src="`https://www.youtube.com/embed/${activeYoutubeId}`" 
                                      frameborder="0" 
                                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                                      allowfullscreen>
                                  </iframe>
                              </div>
                          </div>
                      </div>
                      
                      <div class="actions">
                          <button @click="resetFlow" class="btn-restart">
                              <RotateCcw class="w-4 h-4 mr-2" /> RESTART MISSION
                          </button>
                          <button @click="handlePracticeClose" class="btn-close">
                              MISSION COMPLETE
                          </button>
                      </div>
                  </div>
              </div>
          </section>
      </div>
      
      <!-- BugHunt 스타일 오리 힌트 시스템 [2026-02-13] - viewport 하단 배치 -->
      <transition name="duck-pop">
        <div v-if="gameState.showHint" class="hint-duck-container">
            <div class="hint-speech-bubble">
                <div class="bubble-header">DUC-TIP!</div>
                <div class="bubble-content">
                    <p v-for="(hintText, hIdx) in currentMission.validation?.concepts?.flatMap(c => c.hints || [])" :key="hIdx" class="hint-li">
                        • {{ hintText }}
                    </p>
                </div>
            </div>
            <img src="@/assets/image/duck_det.png" class="hint-duck-img" alt="Hint Duck">
        </div>
      </transition>
    </main>

    <!-- [2026-02-11] FEEDBACK TOAST -->
    <div v-if="gameState.feedbackMessage && gameState.phase !== 'EVALUATION'" class="feedback-toast">
      <span class="toast-icon">!</span> {{ gameState.feedbackMessage }}
    </div>
  </div>
</template>

<script setup>
import { computed, ref, reactive, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useGameStore } from '@/stores/game';
import { useCoduckWars } from './composables/useCoduckWars.js';
import { VueMonacoEditor } from '@guolao/vue-monaco-editor';
import { useMonacoEditor } from './composables/useMonacoEditor.js';
import { 
  AlertOctagon, Info, ArrowRight, Lightbulb, 
  RotateCcw, Play, X, Brain, CheckCircle
} from 'lucide-vue-next';

const activeYoutubeId = ref(null);
import CodeFlowVisualizer from './components/CodeFlowVisualizer.vue';
import LoadingDuck from '../components/LoadingDuck.vue';

const router = useRouter();
const gameStore = useGameStore();

const {
    gameState,
    currentMission,
    evaluationResult,
    deepQuizQuestion,
    ruleChecklist,
    canSubmitPseudo,
    isProcessing,
    isGuideOpen,
    selectedGuideIdx,
    showHintDuck,
    toggleHintDuck,
    dynamicHintMessage,
    retryDesign,

    toggleGuide,
    handleGuideClick,
    submitDiagnostic,
    diagnosticQuestion,
    submitPseudo,
    submitDeepQuiz,
    handlePythonVisualizationNext,
    handleTailSelection: originalHandleTailSelection,
    resetFlow,
    toggleHint,
    handlePracticeClose
} = useCoduckWars();


// [2026-02-13] 인트로를 제외한 실질적 학습/상호작용 단계 여부 (가독성 개선)
const isInteractionPhase = computed(() => {
    const p = gameState.phase;
    return p.startsWith('DIAGNOSTIC') || 
           ['PSEUDO_WRITE', 'PYTHON_VISUALIZATION', 'EVALUATION', 'TAIL_QUESTION', 'DEEP_QUIZ'].includes(p);
});

// [2026-02-12] 지문(problemContext)을 설명부와 코드부로 분리하여 가독성 증대
const diagnosticProblemParts = computed(() => {
    const context = diagnosticQuestion.value.problemContext || "";
    if (!context) return null;
    
    // 이중 개행(\n\n)을 기준으로 첫 단락(설명)과 나머지(코드)를 분리
    const parts = context.split('\n\n');
    return {
        instruction: parts[0],
        code: parts.slice(1).join('\n\n')
    };
});

// [2026-02-13] Radar Chart & Evaluation UI Compute
const scoreTier = computed(() => {
    const score = evaluationResult.finalScore || 0;
    if (score >= 90) return { icon: '🏆', label: 'MASTER ARCHITECT', class: 'tier-s' };
    if (score >= 80) return { icon: '🥇', label: 'SENIOR ARCHITECT', class: 'tier-a' };
    if (score >= 70) return { icon: '🥈', label: 'JUNIOR ARCHITECT', class: 'tier-b' };
    return { icon: '🥉', label: 'ARCH_APPRENTICE', class: 'tier-c' };
});

const radarAxes = computed(() => {
    const count = 5;
    const center = 100;
    const radius = 80;
    return Array.from({ length: count }).map((_, i) => {
        const angle = (Math.PI * 2 * i) / count - Math.PI / 2;
        return {
            x: center + Math.cos(angle) * radius,
            y: center + Math.sin(angle) * radius
        };
    });
});

const radarLabels = computed(() => {
    const labels = ['정합', '추상', '예외', '구현', '설계'];
    const center = 100;
    const radius = 94; // [2026-02-13] 레이블 가독성을 위한 간격 확보
    return labels.map((text, i) => {
        const angle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
        const x = center + Math.cos(angle) * radius;
        const y = center + Math.sin(angle) * radius;

        // [2026-02-13] 사분면(Quadrant) 기반 텍스트 정렬 최적화
        let anchor = "middle";
        let baseline = "middle";

        const cos = Math.cos(angle);
        const sin = Math.sin(angle);

        // X축 정렬 (start/middle/end)
        if (Math.abs(cos) < 0.1) anchor = "middle";
        else if (cos > 0) anchor = "start";
        else anchor = "end";

        // Y축 정렬 (hanging/middle/auto)
        if (Math.abs(sin) < 0.1) baseline = "middle";
        else if (sin > 0) baseline = "hanging";
        else baseline = "auto";

        return { text, x, y, anchor, baseline };
    });
});

const radarPoints = computed(() => {
    const dims = evaluationResult.dimensions || {};
    const keys = ['design', 'consistency', 'edge_case', 'implementation', 'abstraction'];
    const center = 100;
    const maxRadius = 80;
    
    return keys.map((key, i) => {
        // [2026-02-13] useCoduckWars.js에서 이미 100점 만점으로 정규화됨
        const score = (dims[key]?.score || 0) / 100; 
        const radius = score * maxRadius;
        const angle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
        const x = center + Math.cos(angle) * radius;
        const y = center + Math.sin(angle) * radius;
        return `${x},${y}`;
    }).join(' ');
});

// [2026-02-13] 단계 이동 시 힌트 창 자동 닫기 (BugHunt와 동작 일관성)
watch(() => gameState.phase, () => {
    gameState.showHint = false;
});

// Monaco Editor 연동
const { monacoOptions, handleMonacoMount } = useMonacoEditor(
    currentMission, 
    reactive({
        get userCode() { return gameState.phase3Reasoning; },
        set userCode(v) { gameState.phase3Reasoning = v; }
    })
);

// --- END INTEGRATION ---
</script>

<style scoped src="./CoduckWars.css"></style>

<style scoped>
/* [2026-02-13] Blueprint Reference Card (Retry Mode) */
.blueprint-reference-card {
  z-index: 5;
  margin-bottom: 2rem;
}

.brc-header {
  border-bottom: none;
}

.brc-body {
  box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
  border-bottom-left-radius: 0.75rem;
  border-bottom-right-radius: 0.75rem;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #0f172a;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #1e293b;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #334155;
}

/* Retry Button Styling */
:deep(.btn-retry-action) {
  background: rgba(30, 41, 59, 0.6);
  border: 2px solid #3b82f6;
  color: #3b82f6;
  padding: 24px 60px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

:deep(.btn-retry-action:hover) {
  background: #3b82f6;
  color: white;
  transform: translateY(-5px) scale(1.05);
  box-shadow: 0 15px 35px rgba(59, 130, 246, 0.4);
}

.animate-slideIn {
  animation: slideInDown 0.5s ease-out;
}

@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
