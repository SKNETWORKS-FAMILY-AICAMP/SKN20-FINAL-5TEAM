<!--
수정일: 2026-02-14
수정 내용: 5대 지표 평가 시스템 완전 통합
-->
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
      <!-- [2026-02-14 수정] 듀토리얼 버튼 및 실습 종료 버튼 분리 -->
      <div class="header-actions">
        <!-- [2026-02-14] 힌트보기 버튼 헤더(붉은색 위치) 배치 -->
        <button v-if="isNaturalLanguagePhase" class="btn-hint-header" @click="toggleHintDuck" :class="{ 'is-active': showHintDuck }">
           <Lightbulb class="w-4 h-4 mr-1.5" /> 힌트보기
        </button>
        <button class="btn-tutorial-trigger" @click="startTutorial">
          <BookOpen class="w-4 h-4 mr-2" /> 사용법(튜토리얼)
        </button>
        <button class="btn-practice-close" @click="closePractice">
          <X class="w-4 h-4 mr-2" /> 실습 종료
        </button>
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
                  <!-- [2026-02-11] 코덕 캐릭터 이미지 연결 [2026-02-14] 클릭 시 실시간 힌트 토글 -->
                  <img src="@/assets/image/duck_det.png" alt="Coduck Detective" class="coduck-portrait cursor-pointer hover:scale-105 transition-transform" @click="toggleHintDuck" />
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
                          
                          <div class="actions relative mt-4">
                              <Transition name="fade-slide">
                                <div v-if="showHintDuck" class="hint-duck-wrapper" @click="toggleHintDuck" title="클릭하면 다시 숨깁니다">
                                    <div class="hint-bubble">
                                        <div class="hb-content">{{ dynamicHintMessage || '분석 중입니다...' }}</div>
                                        <div class="hb-tail"></div>
                                    </div>
                                    <img src="@/assets/image/unit_duck.png" alt="Hint Duck" class="hint-unit-img clickable-duck" />
                                </div>
                              </Transition>

                              <button @click="submitDiagnostic()" class="btn-execute-large w-full-btn" :disabled="(!gameState.diagnosticAnswer || gameState.diagnosticAnswer.trim().length < 5) && !gameState.diagnosticResult || gameState.isEvaluatingDiagnostic">
                                  <template v-if="gameState.isEvaluatingDiagnostic">분석 중... <RotateCcw class="w-5 h-5 ml-2 animate-spin" /></template>
                                  <template v-else-if="gameState.diagnosticResult">다음 단계 진행 <ArrowRight class="w-5 h-5 ml-2" /></template>
                                  <template v-else>분석 완료 제출 <CheckCircle class="w-5 h-5 ml-2" /></template>
                              </button>
                          </div>
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

                          <div class="actions flex items-center justify-end gap-4 relative">
                              <!-- [2026-02-14] 실시간 힌트 오리 & 말풍선 (버튼 왼쪽 위치) -->
                              <Transition name="fade-slide">
                                <div v-if="showHintDuck" class="hint-duck-wrapper" @click="toggleHintDuck" title="클릭하면 다시 숨깁니다">
                                    <div class="hint-bubble">
                                        <div class="hb-content">{{ dynamicHintMessage || '분석 중입니다...' }}</div>
                                        <div class="hb-tail"></div>
                                    </div>
                                    <img src="@/assets/image/unit_duck.png" alt="Hint Duck" class="hint-unit-img clickable-duck" />
                                </div>
                              </Transition>

                              <button 
                                  :disabled="!canSubmitPseudo || isProcessing"
                                  @click="submitPseudo"
                                  class="btn-execute-large"
                              >
                                  심화 분석 시작 <Play class="w-4 h-4 ml-1.5" />
                              </button>
                          </div>
                      </div>
                  </div>
              </div>

              <!-- [STEP 3] Python 시각화 및 분기 단계 [2026-02-13] decision-panel 내부로 이동 -->
              <div v-else-if="gameState.phase === 'PYTHON_VISUALIZATION'" class="visualization-phase flex-1 flex flex-col min-h-0">
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
              <div v-else-if="gameState.phase === 'TAIL_QUESTION'" class="tail-question-phase flex-1 flex flex-col min-h-0">
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
              <div v-else-if="gameState.phase === 'DEEP_QUIZ'" class="deep-dive-phase flex-1 flex flex-col min-h-0">
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
              <div v-else-if="gameState.phase === 'EVALUATION'" class="evaluation-phase relative flex-1 flex flex-col min-h-[700px]">
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
                  <div v-if="tutorialAnalyzing || (isProcessing && gameState.phase === 'EVALUATION')" class="ai-analysis-simulation absolute inset-0 z-[100] bg-[#0a1220] flex flex-col items-center justify-center rounded-2xl border border-blue-500/30">
                      <LoadingDuck message="AI 아키텍트가 전체 설계의 정합성과 설계 패턴을 심층 분석 중입니다..." />
                      <div class="analysis-progress-bar w-64 h-1.5 bg-slate-800 rounded-full mt-4 overflow-hidden">
                          <div class="analysis-progress-fill h-full bg-blue-500 animate-loading-bar"></div>
                      </div>
                  </div>

                  <!-- [2026-02-14] 최종 아키텍처 리포트 포탈 (PPT 레이아웃 최적화) -->
                  <div v-if="!tutorialAnalyzing && showMetrics && finalReport" class="architect-report-portal animate-fadeIn">
                      
                      <!-- Part 1: Strategic Billboard (Score & Grade) -->
                      <div class="report-billboard-premium">
                          <div class="billboard-glass"></div>
                          <div class="billboard-content">
                              <div class="score-ring-box">
                                  <svg viewBox="0 0 100 100" class="ring-svg-neo">
                                      <circle class="ring-bg" cx="50" cy="50" r="45"></circle>
                                      <circle class="ring-fill" cx="50" cy="50" r="45" :style="{ strokeDasharray: 283, strokeDashoffset: 283 - (283 * finalReport.totalScore / 100) }"></circle>
                                  </svg>
                                  <div class="score-absolute">
                                      <span class="pts-num">{{ finalReport.totalScore }}</span>
                                      <span class="pts-unit">PTS</span>
                                  </div>
                              </div>
                              <div class="grade-badge-box">
                                  <div class="grade-symbol-neo">
                                      <span class="symbol">{{ finalReport.grade.grade }}</span>
                                      <span class="label">STATUS</span>
                                  </div>
                                  <h2 class="verdict-headline">"{{ finalReport.grade.description }}"</h2>
                              </div>
                              <div class="mission-ident">
                                  <div class="ch-tag">MISSION: {{ currentMission.title }}</div>
                              </div>
                          </div>
                      </div>

                      <!-- Part 2: Analysis Center (Dual Hub) -->
                      <div class="report-hub-grid">
                          <!-- Visual Balance Scan -->
                          <div class="hub-cell visual-scan">
                              <div class="neo-glass-card">
                                  <h3 class="neo-card-title"><Activity size="14" /> Logic Balance Scan</h3>
                                  <div class="radar-container-neo">
                                      <canvas ref="radarChartCanvas"></canvas>
                                  </div>
                              </div>
                          </div>

                          <!-- Dimension Breakdowns -->
                          <div class="hub-cell metrics-matrix">
                              <div class="neo-glass-card h-full">
                                  <h3 class="neo-card-title"><Layers size="14" /> Dimension Matrix</h3>
                                  <div class="metric-progress-list">
                                      <div v-for="(metric, key) in finalReport.metrics" :key="key" class="metric-row-neo premium-feedback">
                                          <div class="m-header">
                                              <span class="m-name">{{ metric.name }}</span>
                                              <span class="m-score-tag" :style="{ color: getMetricColor(metric.percentage) }">{{ metric.percentage }}%</span>
                                          </div>
                                          <div class="m-comment-box">
                                              <p class="m-comment-text">
                                                  <span class="quote-icon">"</span>
                                                  {{ metric.comment }}
                                                  <span class="quote-icon">"</span>
                                              </p>
                                          </div>
                                      </div>
                                  </div>
                              </div>
                          </div>
                      </div>

                      <!-- Part 3: Expert Senior Verdict -->
                      <div class="expert-section-neo">
                          <div class="mentor-glass-card">
                              <div class="mentor-profile">
                                  <div class="mentor-avatar">
                                      <img src="@/assets/image/duck_det.png" alt="Architect Duck" />
                                  </div>
                                  <div class="mentor-meta">
                                      <span class="m-role">Senior Architect Monitor</span>
                                      <h4 class="m-name">{{ finalReport.finalReport.persona }}</h4>
                                  </div>
                              </div>
                              
                              <blockquote class="senior-quote">"{{ finalReport.finalReport.summary }}"</blockquote>
                              
                              <div class="feedback-dual-grid">
                                  <div class="fb-item-neo plus">
                                      <span class="tag-neo text-emerald-400">CORE STRENGTH</span>
                                      <p class="txt-neo"><b>{{ finalReport.finalReport.strength.metric }}:</b> {{ finalReport.finalReport.strength.feedback }}</p>
                                  </div>
                                  <div class="fb-item-neo minus">
                                      <span class="tag-neo text-amber-400">EVOLVE POINT</span>
                                      <p class="txt-neo"><b>{{ finalReport.finalReport.weakness.metric }}:</b> {{ finalReport.finalReport.weakness.feedback }}</p>
                                  </div>
                              </div>

                              <div class="one-point-lesson-neo">
                                  <div class="p-icon-box"><Lightbulb size="20" class="text-amber-400" /></div>
                                  <div class="p-content">
                                      <span class="p-tag">ONE-POINT LESSON</span>
                                      <p class="p-msg">{{ finalReport.finalReport.lesson }}</p>
                                  </div>
                              </div>
                          </div>
                      </div>

                      <!-- Part 4: Continuous Learning Path (YouTube) -->
                      <div class="pathway-section-neo">
                          <h3 class="path-heading-neo"><Cpu size="18" class="mr-2" /> CONTINUOUS LEARNING PATH</h3>
                          <div class="path-grid-neo">
                              <div v-for="video in getFilteredVideos()" :key="video.url" class="path-card-neo">
                                  <a :href="video.url" target="_blank" class="p-link-neo">
                                      <div class="p-info">
                                          <span class="p-author">{{ video.channel }}</span>
                                          <h5 class="p-title">{{ video.title }}</h5>
                                          <p class="p-desc">{{ video.curationPoint }}</p>
                                      </div>
                                      <div class="p-play-ico"><Play size="14" fill="currentColor" /></div>
                                  </a>
                              </div>
                          </div>
                      </div>

                      <!-- Part 5: Final Actions -->
                      <div class="terminal-actions-neo">
                          <button @click="resetFlow" class="btn-neo-restart">
                              <RotateCcw size="18" class="mr-2" /> RESTART MISSION
                          </button>
                          <button @click="handlePracticeClose" class="btn-neo-complete">
                              <CheckCircle size="18" class="mr-2" /> MISSION COMPLETE
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

    <!-- [2026-02-14 수정] 듀토리얼 오버레이 추가 (페이즈 변경 리스너 추가) -->
    <PseudocodeTutorialOverlay
      v-if="showTutorial"
      @complete="onTutorialComplete"
      @skip="onTutorialComplete"
      @quit="closePractice"
      @change-phase="handleTutorialPhaseChange"
    />

    <!-- [2026-02-11] FEEDBACK TOAST -->
    <div v-if="gameState.feedbackMessage && gameState.phase !== 'EVALUATION'" class="feedback-toast">
      <span class="toast-icon">!</span> {{ gameState.feedbackMessage }}
    </div>
  </div>
</template>

<script setup>
import { computed, ref, reactive, onMounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useGameStore } from '@/stores/game';
import { useCoduckWars } from './composables/useCoduckWars.js';
import { VueMonacoEditor } from '@guolao/vue-monaco-editor';
import { useMonacoEditor } from './composables/useMonacoEditor.js';
import { 
  AlertOctagon, Info, ArrowRight, Lightbulb, 
  RotateCcw, Play, X, Brain, CheckCircle,
  Activity, Layers, Cpu
} from 'lucide-vue-next';
import { ComprehensiveEvaluator } from './evaluationEngine.js';
import { generateCompleteLearningReport } from './reportGenerator.js';
import { filterByScore } from './learningResources.js';
import Chart from 'chart.js/auto';

const activeYoutubeId = ref(null);
import CodeFlowVisualizer from './components/CodeFlowVisualizer.vue';
import LoadingDuck from '../components/LoadingDuck.vue';

const router = useRouter();
const gameStore = useGameStore();
const emit = defineEmits(['close']);

// [2026-02-14 수정] 튜토리얼 상태 관리
import PseudocodeTutorialOverlay from './components/PseudocodeTutorialOverlay.vue';
import { BookOpen } from 'lucide-vue-next'; // BookOpen 아이콘 추가

const showTutorial = ref(false);
const originalPhase = ref(null);
const tutorialAnalyzing = ref(false);

onMounted(() => {
  if (!localStorage.getItem('pseudocode-tutorial-done')) {
    startTutorial();
  }
});

const startTutorial = () => {
    // 튜토리얼 시작 시 현재 페이즈 백업
    originalPhase.value = gameState.phase;
    showTutorial.value = true;
};


/**
 * [2026-02-14 수정] 튜토리얼 진행에 따른 페이즈 자동 전환 및 모킹
 */
const handleTutorialPhaseChange = (targetPhase) => {
    gameState.phase = targetPhase;

    // 튜토리얼 중 화면이 비어 보이지 않도록 모크 데이터 주입
    if (targetPhase === 'DIAGNOSTIC_1') {
        // 진단 단계에서 질문 데이터가 없는 경우를 대비한 모킹
        // (실제 데이터는 currentMission에서 가져오지만 튜토리얼 가독성을 위해)
    }

    if (targetPhase === 'PSEUDO_WRITE') {
        if (!gameState.phase3Reasoning) {
            gameState.phase3Reasoning = "# 데이터 전처리 아키텍처 설계\n# 1. 분리(Isolation): train_test_split\n# 2. 기준점(Anchor): fit on train only\n# 3. 일관성(Consistency): transform both";
        }
    }

    if (targetPhase === 'PYTHON_VISUALIZATION') {
        if (!evaluationResult.value?.converted_python) {
            evaluationResult.value = {
                converted_python: "import pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.preprocessing import StandardScaler\n\n# 1. Isolation: 물리적 격리\ntrain_df, test_df = train_test_split(df, test_size=0.2)\n\n# 2. Anchor: 학습 세트에서만 통계량 추출\nscaler = StandardScaler()\nscaler.fit(train_df[['age', 'income']])\n\n# 3. Consistency: 동일한 변환 적용\ntrain_scaled = scaler.transform(train_df[['age', 'income']])\ntest_scaled = scaler.transform(test_df[['age', 'income']])",
                feedback: "데이터 누수 방지 원칙을 정확하게 준수한 설계입니다. 특히 기준점 설정이 훌륭합니다."
            };
        }
        // DEEP DIVE 질문 모킹 (Box 가시성 확보)
        if (!deepQuizQuestion.value || typeof deepQuizQuestion.value === 'string') {
           deepQuizQuestion.value = {
               question: "모델 배포 후 데이터 분포가 급격히 변하는 'Data Drift'가 발생하면, 기존의 기준점(Anchor)을 어떻게 처리해야 할까요?",
               options: [
                   { text: "새로운 데이터에 맞춰 기준점을 즉시 재학습(Re-fit)한다.", is_correct: true, reason: "안정성을 위해 주기적인 기준점 업데이트가 필요합니다." },
                   { text: "모델의 일관성을 위해 초기 기준점을 절대 바꾸지 않는다.", is_correct: false, reason: "데이터 분포 변화에 대응하지 못해 성능이 저하될 수 있습니다." }
               ]
           };
        }
    }
    
    if (targetPhase === 'EVALUATION') {
        if (!finalReport.value) {
            tutorialAnalyzing.value = true;
            // 튜토리얼용 빠른 시뮬레이션
            setTimeout(() => {
                tutorialAnalyzing.value = false;
                showMetrics.value = true;
                finalReport.value = {
                    totalScore: 88,
                    grade: { grade: 'A+', description: 'Exceptional System Integrity' },
                    metrics: {
                        design: { name: '디자인', percentage: 92, score: 92, max: 100 },
                        edgeCase: { name: '예외처리', percentage: 85, score: 85, max: 100 },
                        abstraction: { name: '추상화', percentage: 95, score: 95, max: 100 },
                        implementation: { name: '구현력', percentage: 78, score: 78, max: 100 },
                        consistency: { name: '정합성', percentage: 90, score: 90, max: 100 }
                    },
                    finalReport: {
                        persona: 'Architect Duck',
                        summary: '이 설계는 완벽한 격리와 기준점 보호 전략을 보여주는 표본입니다.',
                        strength: { metric: 'Consistency', feedback: '데이터 정합성 유지를 위해 기준점을 학습 데이터에만 고정하고 테스트 데이터에 일관되게 전파했습니다.' },
                        weakness: { metric: 'Implementation', feedback: '실제 프로덕션 환경에서는 기준점 업데이트(Re-fitting) 주기를 자동화하는 코드를 추가하면 더욱 견고해질 것입니다.' },
                        lesson: '데이터 누수는 사소한 fit() 한 번으로 시작됩니다. 항상 Anchor(기준점)가 어디인지 자각하십시오.'
                    },
                    recommendedContent: {
                        curationMessage: '아키텍처 설계 역량을 한 단계 더 높여줄 추천 강의입니다.',
                        videos: [
                            { title: 'MLOps에서의 데이터 정제 전략', channel: 'Tech Insight', duration: '12:45', url: '#', curationPoint: '실무 파이프라인 구축', difficulty: 'expert' },
                            { title: 'Data Leakage 완벽 가이드', channel: 'AI School', duration: '18:20', url: '#', curationPoint: '다양한 누수 사례 분석', difficulty: 'expert' }
                        ]
                    }
                };
                nextTick(() => {
                    if (typeof renderRadarChart === 'function') renderRadarChart();
                });
            }, 1800); // 1.8초간 분석 로딩 시뮬레이션
        } else {
            showMetrics.value = true;
        }
    }
};

const onTutorialComplete = () => {
    showTutorial.value = false;
    // 실제 진행 중이던 페이즈로 복구
    if (originalPhase.value) {
        gameState.phase = originalPhase.value;
    }
    localStorage.setItem('pseudocode-tutorial-done', 'true');
};

const closePractice = () => {
  if (confirm('실습을 종료하고 목록으로 돌아가시겠습니까?')) {
    emit('close');
  }
};

// ==================== [2026-02-14] useCoduckWars 분리 (초기화 문제 해결) ====================
const coduckWarsComposable = useCoduckWars();

// submitPseudo만 따로 빼두기
const originalSubmitPseudo = coduckWarsComposable.submitPseudo;

// 나머지는 destructuring
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
    // submitPseudo는 제외! (아래에서 재정의)
    submitDeepQuiz,
    handlePythonVisualizationNext,
    handleTailSelection: originalHandleTailSelection,
    resetFlow,
    toggleHint,
    handlePracticeClose
} = coduckWarsComposable;

// [2026-02-14] 자연어 서술 단계 여부 판단 (힌트 버튼 노출용)
const isNaturalLanguagePhase = computed(() => {
    // 분석 중이거나 결과가 표시된 상태면 힌트 버튼 숨김
    if (isProcessing.value || showMetrics.value || tutorialAnalyzing.value) return false;
    
    if (gameState.phase === 'PSEUDO_WRITE') return true;
    if (gameState.phase === 'DIAGNOSTIC_1' && diagnosticQuestion.value?.type === 'DESCRIPTIVE') return true;
    return false;
});


// ==================== [2026-02-14] 5대 지표 평가 시스템 추가 ====================

// 5대 지표 상태
const showMetrics = ref(false);
const finalReport = ref(null);
const radarChartCanvas = ref(null);
let radarChartInstance = null;

/**
 * 5대 지표 평가 시작
 * (EVALUATION 단계 진입 시 자동으로 호출됨)
 */
async function runComprehensiveEvaluation() {
  if (finalReport.value || isProcessing.value) return;
  
  try {
    isProcessing.value = true;
    console.log('[5D] Starting comprehensive evaluation...');
    
    // 로딩 상태 시뮬레이션 (선택적)
    gameState.feedbackMessage = "시니어 아키텍트가 최종 검토 중입니다...";
    
    const evaluator = new ComprehensiveEvaluator(getApiKey());
    
    const evaluationResults = await evaluator.evaluate({
      pseudocode: gameState.phase3Reasoning,
      pythonCode: evaluationResult.value?.converted_python || '',
      deepdive: gameState.deepQuizAnswer || '',
      deepdiveScenario: deepQuizQuestion.value || {}
    });

    finalReport.value = await generateCompleteLearningReport(
      evaluationResults,
      getApiKey()
    );

    showMetrics.value = true;

    await nextTick();
    renderRadarChart();

    console.log('[5D] Evaluation complete:', finalReport.value);
    
  } catch (error) {
    console.error('[5D] Evaluation error:', error);
    // 폴백: 최소한 화면은 보여줌
    showMetrics.value = true;
  } finally {
    isProcessing.value = false;
  }
}

/**
 * submitPseudo 래퍼 - 기존 로직만 실행
 */
async function submitPseudoEnhanced() {
  try {
    // 기존 평가 실행 (PYTHON_VISUALIZATION 단계로 이동함)
    await originalSubmitPseudo();
  } catch (error) {
    console.error('Submission error:', error);
  }
}

/**
 * API 키 가져오기
 */
function getApiKey() {
  return import.meta.env.VITE_OPENAI_API_KEY || '';
}

/**
 * 레이더 차트 렌더링
 */
function renderRadarChart() {
  if (!radarChartCanvas.value || !finalReport.value) return;

  if (radarChartInstance) {
    radarChartInstance.destroy();
  }

  const ctx = radarChartCanvas.value.getContext('2d');
  const metrics = finalReport.value.metrics;

  radarChartInstance = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: [
        metrics.abstraction.name,
        metrics.implementation.name,
        metrics.design.name,
        metrics.edgeCase.name,
        metrics.consistency.name
      ],
      datasets: [{
        label: '당신의 점수',
        data: [
          metrics.abstraction.percentage,
          metrics.implementation.percentage,
          metrics.design.percentage,
          metrics.edgeCase.percentage,
          metrics.consistency.percentage
        ],
        backgroundColor: 'rgba(96, 165, 250, 0.3)',
        borderColor: '#60a5fa',
        pointBackgroundColor: '#60a5fa',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#60a5fa',
        borderWidth: 3,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      scales: {
        r: {
          beginAtZero: true,
          max: 100,
          ticks: { stepSize: 20, color: '#999' },
          grid: { color: '#333' },
          pointLabels: { color: '#fff', font: { size: 12 } }
        }
      },
      plugins: { 
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            titleColor: '#60a5fa',
            bodyColor: '#fff',
            cornerRadius: 8,
            padding: 12
          }
      },
      responsive: true,
      maintainAspectRatio: false
    }
  });
}

/**
 * 지표별 색상
 */
function getMetricColor(percentage) {
  if (percentage >= 90) return '#4ade80'; // Emerald
  if (percentage >= 75) return '#60a5fa'; // Blue
  if (percentage >= 60) return '#fbbf24'; // Amber
  return '#f87171'; // Rose
}

/**
 * 점수별 영상 필터링
 */
function getFilteredVideos() {
  if (!finalReport.value) return [];
  return filterByScore(
    finalReport.value.recommendedContent,
    finalReport.value.totalScore
  );
}

// submitPseudo 함수 최종 정의 (이제 에러 안 남!)
const submitPseudo = submitPseudoEnhanced;


// ==================== 기존 코드 ====================

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
    const radius = 94;
    return labels.map((text, i) => {
        const angle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
        const x = center + Math.cos(angle) * radius;
        const y = center + Math.sin(angle) * radius;

        let anchor = "middle";
        let baseline = "middle";

        const cos = Math.cos(angle);
        const sin = Math.sin(angle);

        if (Math.abs(cos) < 0.1) anchor = "middle";
        else if (cos > 0) anchor = "start";
        else anchor = "end";

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
        const score = (dims[key]?.score || 0) / 100; 
        const radius = score * maxRadius;
        const angle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
        const x = center + Math.cos(angle) * radius;
        const y = center + Math.sin(angle) * radius;
        return `${x},${y}`;
    }).join(' ');
});

watch(() => gameState.phase, (newPhase) => {
    gameState.showHint = false;
    
    // [2026-02-14] EVALUATION 단계 진입 시 5D 평가 자동 트리거
    if (newPhase === 'EVALUATION' && !showTutorial.value) {
        runComprehensiveEvaluation();
    }
});

const { monacoOptions, handleMonacoMount } = useMonacoEditor(
    currentMission, 
    reactive({
        get userCode() { return gameState.phase3Reasoning; },
        set userCode(v) { gameState.phase3Reasoning = v; }
    })
);
</script>

<style scoped src="./CoduckWars.css"></style>

<style scoped>
@keyframes loading-bar {
  0% { transform: translateX(-100%); }
  50% { transform: translateX(-20%); }
  100% { transform: translateX(0); }
}

.animate-loading-bar {
  animation: loading-bar 1.8s ease-in-out infinite;
}

.ai-analysis-simulation {
  backdrop-filter: blur(10px);
}
</style>

<style scoped>
/* 2026-02-14 수정: 헤더 신규 버튼 스타일 (튜토리얼, 실습 종료) */
.btn-tutorial-trigger {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #f1f5f9;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 13px;
  transition: all 0.2s;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.btn-tutorial-trigger:hover {
  background: rgba(59, 130, 246, 0.25);
  border-color: #3b82f6;
  color: #fff;
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);
}

.btn-practice-close {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #f1f5f9;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 13px;
  transition: all 0.2s;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.btn-practice-close:hover {
  background: rgba(239, 68, 68, 0.25);
  border-color: #ef4444;
  color: #fff;
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
}

/* [2026-02-14] 헤더용 힌트 버튼 (붉은색 위치) */
.btn-hint-header {
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.3);
  color: #fbbf24;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 13px;
  transition: all 0.2s;
  cursor: pointer;
  display: flex;
  align-items: center;
  margin-right: 8px;
}

.btn-hint-header:hover, .btn-hint-header.is-active {
  background: rgba(251, 191, 36, 0.25);
  border-color: #f59e0b;
  color: #fff;
  box-shadow: 0 0 15px rgba(245, 158, 11, 0.4);
}

.hint-duck-wrapper {
  position: relative !important;
  right: auto !important;
  bottom: auto !important;
  display: flex;
  flex-direction: column;
  align-items: center;
  pointer-events: auto !important;
  z-index: 1000;
  cursor: pointer;
  margin-right: 15px; /* 버튼과의 간격 */
  align-self: flex-end; /* 버튼 하단 라인에 맞춤 */
}

.hint-unit-img.clickable-duck {
  width: 70px;
  height: 70px;
  filter: drop-shadow(0 0 10px rgba(59, 130, 246, 0.3));
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.hint-duck-wrapper:hover .clickable-duck {
  transform: scale(1.1);
  filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.6));
}

.hint-bubble {
  position: absolute !important;
  bottom: 80px !important; /* 오리 머리 위쪽 */
  left: 50% !important;
  transform: translateX(-50%) !important;
  width: 380px !important; 
  min-width: 320px;
  margin-bottom: 0 !important;
  z-index: 1001;
  animation: bubble-bounce 0.4s ease-out;
}

.hb-tail {
  position: absolute;
  bottom: -7px;
  left: 50% !important;
  transform: translateX(-50%) rotate(45deg) !important;
  width: 14px;
  height: 14px;
  background: rgba(10, 20, 40, 0.98);
  border-right: 1.5px solid #3b82f6;
  border-bottom: 1.5px solid #3b82f6;
}

@keyframes bubble-bounce {
  0% { transform: scale(0.8) translateY(10px); opacity: 0; }
  100% { transform: scale(1) translateY(0); opacity: 1; }
}

.btn-hint-toggle {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.4);
  color: #60a5fa;
  padding: 12px 24px;
  border-radius: 14px;
  font-weight: 800;
  font-size: 14px;
  letter-spacing: 0.5px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  display: flex;
  align-items: center;
}

.btn-hint-toggle:hover, .btn-hint-toggle.is-active {
  background: rgba(59, 130, 246, 0.25);
  border-color: #3b82f6;
  color: #fff;
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
  transform: translateY(-2px);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

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

/* ==================== [2026-02-14] Premium Architect Report Portal Styles ==================== */

.architect-report-portal {
  padding: 24px;
  background: rgba(10, 15, 25, 0.4);
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Score Banner */
.report-banner-premium {
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  padding: 40px;
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 0 40px rgba(59, 130, 246, 0.15);
}

.banner-glass {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(30, 64, 175, 0.2), rgba(139, 92, 246, 0.2));
  backdrop-filter: blur(20px);
  z-index: 1;
}

.banner-content {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: 1fr 1fr 2fr;
  align-items: center;
  gap: 32px;
}

.score-circle-wrapper {
  position: relative;
  width: 140px;
  height: 140px;
  filter: drop-shadow(0 0 10px rgba(59, 130, 246, 0.5));
}

.progress-ring {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-bg {
  stroke: rgba(255, 255, 255, 0.1);
  stroke-width: 8;
  fill: none;
}

.ring-fill {
  stroke: #60a5fa;
  stroke-width: 8;
  stroke-linecap: round;
  fill: none;
  transition: stroke-dashoffset 1s ease-out;
}

.score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-text .num {
  font-size: 3rem;
  font-weight: 900;
  color: #fff;
  line-height: 1;
}

.score-text .unit {
  font-size: 0.8rem;
  color: #60a5fa;
  font-weight: 700;
  letter-spacing: 2px;
}

.banner-center {
  text-align: center;
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0 20px;
}

.grade-symbol-large {
  font-size: 5rem;
  font-weight: 900;
  color: #fff;
  text-shadow: 0 0 30px rgba(255, 255, 255, 0.5);
  line-height: 1;
  margin-bottom: 8px;
}

.grade-label {
  font-size: 0.75rem;
  color: #94a3b8;
  letter-spacing: 3px;
  font-weight: 700;
}

.architect-status-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f8fafc;
  line-height: 1.4;
  margin-bottom: 12px;
}

.mission-tag {
  display: inline-block;
  padding: 6px 12px;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.4);
  color: #60a5fa;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
}

/* Analysis Hub Grid */
.analysis-hub-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.section-card-glass {
  background: rgba(30, 41, 59, 0.5);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 24px;
}

.card-title-mini {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.75rem;
  font-weight: 800;
  color: #64748b;
  letter-spacing: 1.5px;
  margin-bottom: 20px;
  text-transform: uppercase;
}

.radar-chart-wrapper {
  height: 280px;
  position: relative;
}

.metrics-matrix-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.matrix-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mi-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mi-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #e2e8f0;
}

.mi-val {
  font-size: 0.9rem;
  font-weight: 700;
  color: #60a5fa;
}

.mi-bar-container {
  height: 6px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  overflow: hidden;
}

.mi-bar-fill {
  height: 100%;
  border-radius: 10px;
  transition: width 1s ease-out;
}

/* Verdict Section */
.verdict-card-glass {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.8));
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 24px;
  padding: 32px;
}

.verdict-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.persona-avatar {
  width: 60px;
  height: 60px;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.4);
  border-radius: 50%;
  padding: 8px;
}

.persona-avatar img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.p-role {
  font-size: 0.7rem;
  color: #60a5fa;
  font-weight: 800;
  letter-spacing: 2px;
}

.p-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #fff;
}

.verdict-summary {
  font-size: 1.1rem;
  color: #f1f5f9;
  line-height: 1.6;
  font-style: italic;
  margin-bottom: 32px;
  padding-left: 16px;
  border-left: 2px solid #3b82f6;
}

.feedback-grid-mini {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 32px;
}

.fb-item {
  padding: 20px;
  border-radius: 16px;
}

.fb-item.success { background: rgba(34, 197, 94, 0.05); border: 1px solid rgba(34, 197, 94, 0.2); }
.fb-item.warning { background: rgba(245, 158, 11, 0.05); border: 1px solid rgba(245, 158, 11, 0.2); }

.fb-tag {
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 1.5px;
  display: block;
  margin-bottom: 12px;
}

.fb-item.success .fb-tag { color: #22c55e; }
.fb-item.warning .fb-tag { color: #f59e0b; }

.fb-text {
  font-size: 0.9rem;
  color: #cbd5e1;
  line-height: 1.6;
}

.master-lesson-box {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  background: rgba(251, 191, 36, 0.05);
  border: 1px solid rgba(251, 191, 36, 0.2);
  padding: 24px;
  border-radius: 16px;
}

.lesson-label {
  font-size: 0.8rem;
  font-weight: 800;
  color: #fbbf24;
  letter-spacing: 1.5px;
  display: block;
  margin-bottom: 8px;
}

.lesson-text {
  font-size: 0.95rem;
  color: #fef3c7;
  line-height: 1.6;
}

/* Learning Path */
.path-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1rem;
  font-weight: 800;
  color: #fff;
  letter-spacing: 1.5px;
  margin-bottom: 24px;
}

.path-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.path-card {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.path-card:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.4);
  transform: translateY(-5px);
}

.pc-link {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  text-decoration: none;
}

.pc-channel {
  font-size: 0.7rem;
  color: #60a5fa;
  font-weight: 700;
  letter-spacing: 1px;
}

.pc-title {
  font-size: 1rem;
  color: #fff;
  margin: 6px 0 10px;
  line-height: 1.4;
}

.pc-reason {
  font-size: 0.8rem;
  color: #94a3b8;
  line-height: 1.5;
}

.pc-play {
  width: 32px;
  height: 32px;
  background: #3b82f6;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);
}

/* Reusable Actions Section within Evaluation */
.actions {
  margin-top: 40px;
  display: flex;
  justify-content: center;
  gap: 20px;
  padding-bottom: 60px; /* 스크롤 공간 확보 */
}

/* ==========================================================================
   [2026-02-14] Premium Architect Report Portal Styles
   ========================================================================== */

.architect-report-portal {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding: 1.5rem;
  color: #f1f5f9;
}

/* Part 1: Billboard (Grade & Score) */
.report-billboard-premium {
  position: relative;
  height: 200px;
  border-radius: 24px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.billboard-glass {
  position: absolute;
  inset: 0;
  backdrop-filter: blur(10px);
  background: radial-gradient(circle at top right, rgba(59, 130, 246, 0.1), transparent);
}

.billboard-content {
  position: relative;
  z-index: 2;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 3rem;
  gap: 3rem;
}

.score-ring-box {
  position: relative;
  width: 120px;
  height: 120px;
}

.ring-svg-neo {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.05);
  stroke-width: 8;
}

.ring-fill {
  fill: none;
  stroke: #3b82f6;
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.score-absolute {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.pts-num {
  font-size: 2.2rem;
  font-weight: 800;
  color: #fff;
  line-height: 1;
}

.pts-unit {
  font-size: 0.7rem;
  color: #60a5fa;
  font-weight: 700;
  letter-spacing: 1px;
}

.grade-badge-box {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex: 1;
}

.grade-symbol-neo {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
}

.grade-symbol-neo .symbol {
  font-size: 2.5rem;
  font-weight: 900;
  color: #3b82f6;
  text-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
}

.grade-symbol-neo .label {
  font-size: 0.6rem;
  font-weight: 700;
  color: #94a3b8;
}

.verdict-headline {
  font-size: 1.8rem;
  font-weight: 800;
  color: #fff;
  letter-spacing: -0.5px;
}

.mission-ident {
  margin-left: auto;
}

.ch-tag {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #60a5fa;
  padding: 6px 14px;
  border-radius: 99px;
  font-size: 0.75rem;
  font-weight: 700;
}

/* Part 2: Hub Grid */
.report-hub-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.neo-glass-card {
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 1.5rem;
}

.neo-card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 1.5rem;
}

.radar-container-neo {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 260px;
}

.metric-progress-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.metric-row-neo .m-top-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.metric-row-neo.premium-feedback {
    padding: 1rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.m-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.6rem;
}

.m-name {
  font-size: 0.95rem;
  font-weight: 800;
  color: #f1f5f9;
}

.m-score-tag {
    font-size: 0.8rem;
    font-weight: 900;
    font-family: 'JetBrains Mono', monospace;
    background: rgba(15, 23, 42, 0.5);
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.m-comment-box {
    position: relative;
    padding-left: 0.5rem;
}

.m-comment-text {
  font-size: 0.85rem;
  color: #94a3b8;
  line-height: 1.5;
  margin: 0;
  font-style: italic;
  font-weight: 500;
}

.quote-icon {
    color: #3b82f6;
    font-family: serif;
    font-weight: 900;
    opacity: 0.6;
}

.m-bar-inner {
  height: 100%;
  border-radius: 3px;
  transition: width 1s ease-out 0.5s;
}

/* Part 3: Senior Verdict */
.expert-section-neo {
  background: rgba(30, 41, 59, 0.2);
  border: 1px dashed rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 2rem;
}

.mentor-profile {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.mentor-avatar {
  width: 50px;
  height: 50px;
  background: #1e293b;
  border-radius: 50%;
  padding: 8px;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.mentor-avatar img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.m-role {
  font-size: 0.7rem;
  font-weight: 700;
  color: #3b82f6;
  letter-spacing: 1px;
}

.m-name {
  font-size: 1.1rem;
  font-weight: 800;
  color: #fff;
}

.senior-quote {
  font-size: 1.2rem;
  font-weight: 600;
  line-height: 1.6;
  color: #cbd5e1;
  font-style: italic;
  margin-bottom: 2rem;
  padding-left: 1rem;
  border-left: 3px solid #3b82f6;
}

.feedback-dual-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}

.fb-item-neo {
  background: rgba(255, 255, 255, 0.02);
  padding: 1.25rem;
  border-radius: 16px;
  border-left: 4px solid transparent;
}

.fb-item-neo.plus { border-color: #10b981; }
.fb-item-neo.minus { border-color: #f59e0b; }

.tag-neo {
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
  display: block;
}

.txt-neo {
  font-size: 0.95rem;
  line-height: 1.5;
  color: #e2e8f0;
}

.point-lesson-neo {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  background: rgba(245, 158, 11, 0.05);
  padding: 1.25rem;
  border-radius: 16px;
  border: 1px solid rgba(245, 158, 11, 0.15);
}

.p-icon-box {
  background: rgba(245, 158, 11, 0.15);
  padding: 10px;
  border-radius: 12px;
}

.p-tag {
  font-size: 0.65rem;
  font-weight: 800;
  color: #f59e0b;
  letter-spacing: 1px;
}

.p-msg {
  font-size: 0.95rem;
  font-weight: 600;
  color: #fde68a;
  margin-top: 0.25rem;
}

/* Part 4: Pathway Section */
.pathway-section-neo {
  margin-top: 1rem;
}

.path-heading-neo {
  display: flex;
  align-items: center;
  font-size: 1rem;
  font-weight: 800;
  color: #fff;
  letter-spacing: 1px;
  margin-bottom: 1.5rem;
}

.path-grid-neo {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.p-link-neo {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(15, 23, 42, 0.4);
  padding: 1.25rem;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-decoration: none;
}

.p-link-neo:hover {
  background: rgba(59, 130, 246, 0.08);
  border-color: rgba(59, 130, 246, 0.4);
  transform: translateY(-2px);
}

.p-author {
  font-size: 0.7rem;
  font-weight: 700;
  color: #3b82f6;
  text-transform: uppercase;
  margin-bottom: 0.25rem;
  display: block;
}

.p-title {
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 0.25rem;
}

.p-desc {
  font-size: 0.8rem;
  color: #94a3b8;
}

.p-play-ico {
  width: 32px;
  height: 32px;
  background: #3b82f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

/* Actions */
.terminal-actions-neo {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.btn-neo-restart {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #94a3b8;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  transition: all 0.2s;
}

.btn-neo-restart:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: #fff;
  color: #fff;
}

.btn-neo-complete {
  background: #3b82f6;
  border: none;
  color: #fff;
  padding: 12px 32px;
  border-radius: 12px;
  font-weight: 800;
  display: flex;
  align-items: center;
  transition: all 0.2s;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}

.btn-neo-complete:hover {
  background: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5);
}

/* Animations */
.animate-fadeIn {
  animation: fadeIn 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-loading-bar {
  animation: loadingBar 2s ease-in-out infinite;
}

@keyframes loadingBar {
  0% { transform: translateX(-100%); }
  50% { transform: translateX(0); }
  100% { transform: translateX(100%); }
}

/* [2026-02-14] Responsive Radar Fix */
#radarChartCanvas {
  max-width: 100%;
  max-height: 100%;
}
</style>