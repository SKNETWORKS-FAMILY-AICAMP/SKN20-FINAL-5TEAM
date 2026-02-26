<!--
수정일: 2026-02-14
수정 내용: 5대 지표 평가 시스템 완전 통합 및 프리미엄 리포트 UI 적용
-->
<template>
  <div class="coduck-wars-container">
    <!-- BACKGROUND WATERMARK -->
    <div class="bg-watermark">TEAM BATTLE</div>
    <div class="scan-line"></div>

    <!-- HEADER -->
    <header class="war-room-header">
      <div class="chapter-info">
        <span class="chapter-title">CHAPTER {{ gameState.currentStageId }}: {{ currentMission.title || '로딩 중...' }}</span>
        <span class="sub-info">{{ currentMission.subModuleTitle || 'LEAKAGE_GUARD' }}</span>
      </div>
      <!-- [2026-02-14 수정] 듀토리얼 버튼 및 실습 종료 버튼 분리 -->
      <div class="header-actions">
        <!-- [2026-02-14] 힌트보기 버튼 헤더 - 자연어 서술 단계에서만 노출 (분석 시 은닉) -->
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
        


      <!-- [2026-02-14 수정] 2단 레이아웃 핵심 컨테이너 (EVALUATION 시 1단으로 변경) -->
      <div class="combat-grid w-full h-full" :class="{ 'full-width-layout': gameState.phase === 'EVALUATION' }">
          
          <!-- LEFT PANEL: ENTITY CARD [2026-02-14 수정] 평가 단계에서는 좌측 패널 은닉 -->
          <aside v-if="gameState.phase !== 'EVALUATION'" class="entity-card">
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

              <!-- [2026-02-11] 코덕 실시간 대사창 [2026-02-14 수정] 평가 및 결과 화면에서는 시나리오 박스 은닉 -->
              <div v-if="gameState.phase !== 'EVALUATION'" class="dialogue-box">
                  <span class="speaker">문제 시나리오</span>
                  <p class="dialogue-text">"{{ (isInteractionPhase && currentMission.scenario) ? currentMission.scenario : (gameState.coduckMessage || '데이터 흐름을 분석 중입니다...') }}"</p>
              </div>
          </aside>

          <!-- RIGHT PANEL: DECISION ENGINE [2026-02-11] 단계별 인터랙션 영역 -->
          <section class="decision-panel relative" :class="{ 'visualization-p-zero': ['PYTHON_VISUALIZATION', 'TAIL_QUESTION', 'DEEP_DIVE_DESCRIPTIVE'].includes(gameState.phase) }">
              <div v-if="gameState.phase.startsWith('DIAGNOSTIC') && diagnosticQuestion">
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
                                <div v-if="showHintDuck && isNaturalLanguagePhase" class="hint-duck-wrapper" @click="toggleHintDuck" title="클릭하면 다시 숨깁니다">
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
                      <!-- 객관식 UI (CHOICE) [2026-02-14 수정] 피드백 루프 추가 -->
                      <div v-else-if="diagnosticQuestion.type === 'CHOICE'" class="choice-interaction-area">
                          <div class="choice-visual-frame mb-8">
                              <div class="choice-coduck">
                                  <img :src="currentMission.character?.image || '@/assets/image/duck_det.png'" alt="Coduck Interviewer" />
                              </div>
                              <div class="choice-speech-bubble" :class="{ 'correct-bubble': gameState.isDiagnosticAnswered && diagnosticQuestion.options[gameState.diagnosticAnswerIdx]?.correct, 'wrong-bubble': gameState.isDiagnosticAnswered && !diagnosticQuestion.options[gameState.diagnosticAnswerIdx]?.correct }">
                                  <div class="bubble-tail"></div>
                                  <p class="bubble-text">{{ gameState.isDiagnosticAnswered ? gameState.coduckMessage : diagnosticQuestion.question }}</p>
                              </div>
                          </div>
                          <div class="options-list">
                              <div 
                                v-for="(opt, idx) in diagnosticQuestion.options" 
                                :key="idx" 
                                @click="submitDiagnostic(idx)" 
                                class="option-card"
                                :class="{ 
                                    'is-selected': gameState.diagnosticAnswerIdx === idx,
                                    'is-correct': gameState.isDiagnosticAnswered && (opt.correct || opt.is_correct),
                                    'is-wrong': gameState.isDiagnosticAnswered && gameState.diagnosticAnswerIdx === idx && !(opt.correct || opt.is_correct),
                                    'is-disabled': gameState.isDiagnosticAnswered
                                }"
                              >
                                  <div class="opt-index">{{ idx + 1 }}</div>
                                  <div class="opt-main text-lg">{{ opt.text }}</div>
                                  <div class="opt-status-icon">
                                      <CheckCircle v-if="gameState.isDiagnosticAnswered && (opt.correct || opt.is_correct)" class="text-green-400" />
                                      <X v-else-if="gameState.isDiagnosticAnswered && gameState.diagnosticAnswerIdx === idx" class="text-red-400" />
                                      <ArrowRight v-else />
                                  </div>
                              </div>
                          </div>

                          <!-- [추가] 다음 단계 진행 버튼 (답변 후에만 등장) -->
                          <div v-if="gameState.isDiagnosticAnswered" class="mt-8 animate-fadeIn">
                              <button @click="submitDiagnostic()" class="btn-execute-large w-full-btn">
                                  다음 분석 단계로 진행 <ArrowRight class="w-5 h-5 ml-2" />
                              </button>
                          </div>
                      </div>
                  </div>
                  <!-- AI 아키텍트 분석 오버레이 (진단 단계) -->
                  <div v-if="gameState.isEvaluatingDiagnostic" class="ai-loading-overlay">
                      <AnalysisLoadingScreen message="데이터 흐름 및 논리적 타당성을 정밀 분석 중입니다..." />
                  </div>
              </div>

              <!-- [2026-02-11] PHASE: PSEUDO_WRITE (Step 2: 아키텍처 설계) -->
              <div v-else-if="gameState.phase === 'PSEUDO_WRITE'" class="space-y-4 flex flex-col h-full max-w-5xl mx-auto w-full">
                  <!-- AI 아키텍트 분석 오버레이 (의사코드 심화 분석 단계) [추가: 2026-02-13] -->
                  <div v-if="isProcessing" class="ai-loading-overlay">
                      <AnalysisLoadingScreen message="작성하신 설계의 5차원 아키텍처 정밀 분석 및 Python 코드 변환 중입니다..." />
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
                          <div class="monaco-wrapper w-full h-[320px] border border-slate-700/50 rounded-xl overflow-hidden shadow-2xl relative">
                              <!-- [2026-02-19 추가] 플레이스홀더 오버레이 -->
                              <!-- [2026-02-24 수정] 에디터 입력 시 300ms 디바운스로 인해 플레이스홀더가 늦게 사라지는 현상을 방지하기 위해 v-if를 v-show로 변경 -->
                              <div v-show="!gameState.phase3Reasoning" class="monaco-placeholder-overlay pointer-events-none">
                                  <pre class="placeholder-text">{{ currentMission.placeholder || '이곳에 의사코드를 설계하세요...' }}</pre>
                              </div>
                              <!-- [2026-02-24 수정] 입력값을 즉각적으로 상태와 동기화하여 플레이스홀더 오버레이를 즉시 숨기기 위해 v-model:value 추가 -->
                              <VueMonacoEditor
                                  theme="vs-dark"
                                  language="python"
                                  v-model:value="gameState.phase3Reasoning"
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
                              <!-- [2026-02-14] 실시간 힌트 오리 & 말풍선 (분석 중일 때는 은닉) -->
                              <Transition name="fade-slide">
                                <div v-if="showHintDuck && isNaturalLanguagePhase" class="hint-duck-wrapper" @click="toggleHintDuck" title="클릭하면 다시 숨깁니다">
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

              <!-- [STEP 3] 전술 시각화 및 2단계 검증 (MCQ + 실무 시나리오) -->
              <div v-else-if="['PYTHON_VISUALIZATION', 'TAIL_QUESTION', 'DEEP_DIVE_DESCRIPTIVE'].includes(gameState.phase)" class="visualization-phase flex-1 flex flex-col min-h-0">
                  <CodeFlowVisualizer
                    :phase="gameState.phase"
                    :pseudocode="gameState.phase3Reasoning"
                    :python-code="evaluationResult.converted_python"
                    :evaluation-score="evaluationResult.overall_score"
                    :evaluation-feedback="evaluationResult.senior_advice || evaluationResult.one_line_review || evaluationResult.feedback"
                    :mcq-data="evaluationResult.tail_question || evaluationResult.deep_dive"
                    :blueprint-steps="evaluationResult.blueprint_steps"
                    :assigned-scenario="gameState.assignedScenario"
                    :is-mcq-answered="gameState.isMcqAnswered"
                    :is-processing="isProcessing"
                    @answer-mcq="handleMcqAnswer"
                    @retry-mcq="retryMcq"
                    @submit-descriptive="submitDescriptiveDeepDive"
                    @next-phase="handlePythonVisualizationNext"
                    @blueprint-complete="handleBlueprintComplete"
                  />
              </div>

                  <!-- [STEP 4] 최종 리포트 (EVALUATION) [2026-02-13] decision-panel 내부로 이동 -->
              <div v-else-if="gameState.phase === 'EVALUATION'" class="evaluation-phase relative flex-1 flex flex-col h-full scroll-smooth">
                  <!-- [2026-02-13] 복기 학습 모드 시 미션 정보 재노출 -->
                  <!-- [2026-02-13] 복기 학습 모드 시 미션 정보 재노출 (사용자 요청으로 제거됨) -->
                  <!-- [2026-02-14 수정] 로딩 화면을 1번째 이미지 스타일로 변경 (Full Width & Background Sync) -->
                  <!-- [2026-02-22 Fix] isProcessing 단독으로 EVALUATION 로딩을 막지 않도록 수정 -->
                  <!-- submitDescriptiveDeepDive가 isProcessing=true 상태로 EVALUATION 진입 시 검은 화면 방지 -->
                  <div v-if="tutorialAnalyzing || isGeneratingReport" class="ai-analysis-simulation fixed inset-0 z-[200] bg-[#050505] flex flex-col items-center justify-center border border-emerald-500/30">
                      <div v-if="isGeneratingReport && !tutorialAnalyzing" class="pseudo-write-loading w-full h-full flex flex-col items-center justify-center">
                          <AnalysisLoadingScreen 
                            message="작성한 내용 토대로 종합평가 중입니다..."
                            :duration="4000"
                          />
                      </div>
                      <div v-else>
                          <AnalysisLoadingScreen 
                            :message="'튜토리얼 분석 중...'"
                            :duration="4000"
                          />
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
                                  <div class="verdict-wrapper">
                                      <h3 class="persona-title">최종 진단: {{ finalReport.finalReport.persona }}</h3>
                                      <h2 class="verdict-headline">"{{ finalReport.finalReport.summary }}"</h2>
                                  </div>
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
                                      <h4 class="m-name">Chief Duck Engineer</h4>
                                  </div>
                              </div>
                              
                              <!-- [2026-02-19] 감점 요인 및 점수 분석 (신규) -->
                              <div v-if="finalReport.finalReport.scoringAnalysis" class="deduction-analysis-neo">
                                  <div class="da-header">
                                      <AlertCircle class="w-5 h-5 text-rose-400 mr-2" />
                                      <span class="da-title text-rose-400">SCORE ANALYSIS (감점 요인 분석)</span>
                                  </div>
                                  <p class="da-content">{{ finalReport.finalReport.scoringAnalysis }}</p>
                              </div>

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
                          <div class="curation-header">
                              <h3 class="path-heading-neo"><Play size="18" class="mr-2" /> 📺 취약 지표 기반 맞춤 학습 큐레이션</h3>
                          </div>
                          
                          <div class="video-scroll-container-neo">
                               <!-- [2026-02-14] API로 실시간 연동된 추천 영상 목록 표시 -->
                               <div v-for="video in (evaluationResult.supplementaryVideos || [])" :key="video.videoId" class="path-card-neo curation-card scroll-item">
                                  <a :href="video.url" target="_blank" class="p-link-neo">
                                      <div class="p-thumbnail border-b border-white/5 overflow-hidden rounded-t-xl mb-3">
                                          <img :src="video.thumbnail" :alt="video.title" class="w-full h-auto transform hover:scale-105 transition-transform" />
                                      </div>
                                      <div class="p-index text-blue-400">{{ video.channelTitle }}</div>
                                      <h4 class="p-video-title text-sm font-bold text-white mb-2 leading-snug line-clamp-2">{{ video.title }}</h4>
                                      <p class="text-xs text-slate-400 line-clamp-3 leading-relaxed">{{ video.description }}</p>
                                      <div class="flex items-center justify-end mt-4 text-emerald-400 font-bold text-[10px]">
                                          <Play size="14" class="mr-1" /> WATCH NOW
                                      </div>
                                  </a>
                               </div>

                                           <!-- 추천 영상이 없을 경우 폴백 -->
                               <div v-if="!evaluationResult.supplementaryVideos?.length" class="path-card-neo curation-card scroll-item weakest-focus">
                                  <div class="weakest-badge">🚨 취약 지표 집중 보완</div>
                                  <p class="text-slate-400 text-sm mt-4">추천 영상을 불러오는 중입니다...</p>
                               </div>
                          </div>

                          <!-- [2026-02-20 수정] S-CLASS 임계값 상향 (90 -> 92) 및 명칭 동기화 -->
                          <div v-if="evaluationResult.overall_score >= 92" class="master-next-level mt-10">
                              <div class="master-header">
                                  <h3 class="path-heading-neo master-glow"><CheckCircle size="18" class="mr-2" /> 🏆 S-CLASS 아키텍트 전용 심화 세션</h3>
                                  <p class="master-message">이미 설계 원칙을 완벽히 이해하셨군요! 이제는 엔터프라이즈 레벨의 확장을 고민할 때입니다.</p>
                              </div>
                          </div>
                      </div>

                      <!-- Part 5: Final Actions -->
                          <div class="terminal-actions-neo">
                              <button @click="handleResetFlow" class="btn-neo-restart" aria-label="Restart Mission">
                                  <RotateCcw size="18" class="mr-2" /> RESTART MISSION
                              </button>
                              <button @click="completeMission" class="btn-neo-complete" aria-label="Complete Mission">
                                  <CheckCircle size="18" class="mr-2" /> MISSION COMPLETE
                              </button>
                          </div>
                  </div>
              </div>

              <!-- [2026-02-19 수정] 구조 정상화 (불필요 태그 제거) -->
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
    <div
      v-if="gameState.feedbackMessage && gameState.phase !== 'EVALUATION' && !isProcessing && !gameState.isEvaluatingDiagnostic"
      class="feedback-toast"
    >
      <span class="toast-icon">!</span> {{ gameState.feedbackMessage }}
    </div>

    <!-- [2026-02-21] 실습 종료 확인 모달 (NeoModal) -->
    <Transition name="fade-in">
      <div v-if="showCloseConfirmModal" class="neo-modal-overlay">
        <div class="neo-modal-card">
          <div class="modal-header-neo">
            <AlertTriangle class="text-rose-400 w-6 h-6 mr-2" />
            <h3 class="modal-title-neo">실습 종료</h3>
          </div>
          <div class="modal-body-neo">
            <p class="modal-main-text">실습을 종료하고 목록으로 돌아가시겠습니까?</p>
            <p class="modal-sub-text">현재까지 진행된 내용은 저장되지 않습니다.</p>
          </div>
          <div class="modal-footer-neo">
            <button class="btn-modal-cancel" @click="showCloseConfirmModal = false">
              계속 진행하기
            </button>
            <button class="btn-modal-confirm btn-modal-danger" @click="confirmClosePractice">
              종료하기 <X class="w-4 h-4 ml-1" />
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- [2026-02-19] 무성의 입력 경고용 프리미엄 모달 (NeoModal) -->
    <Transition name="fade-in">
      <div v-if="showLowEffortModal" class="neo-modal-overlay">
        <div class="neo-modal-card">
          <div class="modal-header-neo">
            <AlertTriangle class="text-amber-400 w-6 h-6 mr-2" />
            <h3 class="modal-title-neo">아키텍처 분석 가이드</h3>
          </div>
          <div class="modal-body-neo">
            <p class="modal-main-text">"{{ lowEffortReason }}"</p>
            <p class="modal-sub-text">분석을 위해 설계 내용을 보강하시겠습니까, 아니면 [청사진 복구 실습]을 통해 기초부터 다시 설계하시겠습니까?</p>
          </div>
          <div class="modal-footer-neo">
            <button class="btn-modal-cancel" @click="showLowEffortModal = false">
              더 보완하기
            </button>
            <button class="btn-modal-confirm" @click="confirmLowEffortProceed('RECONSTRUCT')">
              기초부터 배우기 <ArrowRight class="w-4 h-4 ml-1" />
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
/**
 * 수정일: 2026-02-14
 * 수정 내용: 5대 지표 평가 시스템 완전 통합 및 프리미엄 리포트 UI 적용
 */
import { computed, ref, reactive, onMounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useGameStore } from '@/stores/game';
import { usePseudocodePractice } from './composables/usePseudocodePractice.js';
import { VueMonacoEditor } from '@guolao/vue-monaco-editor';
import { useMonacoEditor } from './composables/useMonacoEditor.js';
import { 
  AlertOctagon, Info, ArrowRight, Lightbulb, 
  RotateCcw, Play, X, Brain, CheckCircle,
  Activity, Layers, Cpu, Target, PlusCircle, AlertCircle, 
  PlaySquare, AlertTriangle, User
} from 'lucide-vue-next';
// [2026-02-21] ComprehensiveEvaluator 삭제: 프론트엔드 독립 GPT 호출 제거
// import { ComprehensiveEvaluator } from './evaluationEngine.js';
import { generateCompleteLearningReport } from './services/reportGenerator.js';
import { getRecommendedVideos } from './data/learningResources.js';
import Chart from 'chart.js/auto';

const activeYoutubeId = ref(null);
import CodeFlowVisualizer from './components/CodeFlowVisualizer.vue';
import AnalysisLoadingScreen from '../components/AnalysisLoadingScreen.vue';
import PseudocodeTutorialOverlay from './components/PseudocodeTutorialOverlay.vue';
import { BookOpen } from 'lucide-vue-next';

const router = useRouter();
const gameStore = useGameStore();
const emit = defineEmits(['close']);

// [2026-02-14] 튜토리얼 및 리포트 관련 상태 변수 선언 (최상단 이동)
const showTutorial = ref(false);
const originalPhase = ref(null);
const tutorialAnalyzing = ref(false);
const showMetrics = ref(false);
const finalReport = ref(null);
const radarChartCanvas = ref(null);
let radarChartInstance = null;

// [2026-02-14] usePseudocodePractice 분리 및 데이터 선언 (상단 이동)
const practiceComposable = usePseudocodePractice();
const { resetHintTimer } = practiceComposable;
const originalSubmitPseudo = practiceComposable.submitPseudo;

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
    showLowEffortModal,
    lowEffortReason,
    confirmLowEffortProceed,
    handleBlueprintComplete,

    toggleGuide,
    handleGuideClick,
    submitDiagnostic,
    diagnosticQuestion,
    submitDeepQuiz,
    handleMcqAnswer,
    submitDescriptiveDeepDive,
    handlePythonVisualizationNext,
    handleTailSelection: originalHandleTailSelection,
    addSystemLog,
    handleReSubmitPseudo,
    retryMcq,
    submitPseudo,
    resetFlow
} = practiceComposable;

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
    }

    if (targetPhase === 'PSEUDO_WRITE') {
        // [수정] 사용자가 직접 작성할 수 있도록 자동 채우기 로직 제거
    }

    if (targetPhase === 'PYTHON_VISUALIZATION') {
        // evaluationResult는 reactive 객체이므로 .value 없이 접근
        if (!evaluationResult.converted_python) {
            Object.assign(evaluationResult, {
                converted_python: "import pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.preprocessing import StandardScaler\n\n# 1. Isolation: 물리적 격리\ntrain_df, test_df = train_test_split(df, test_size=0.2)\n\n# 2. Anchor: 학습 세트에서만 통계량 추출\nscaler = StandardScaler()\nscaler.fit(train_df[['age', 'income']])\n\n# 3. Consistency: 동일한 변환 적용\ntrain_scaled = scaler.transform(train_df[['age', 'income']])\ntest_scaled = scaler.transform(test_df[['age', 'income']])",
                feedback: "데이터 누수 방지 원칙을 정확하게 준수한 설계입니다. 특히 기준점 설정이 훌륭합니다.",
                overall_score: 88,
                one_line_review: "데이터 누수 차단을 위한 격리(Isolation)와 기준점(Anchor) 설정이 매우 논리적입니다."
            });
        }
        // deepQuizQuestion은 computed이므로 직접 할당 불가 -> evaluationResult 데이터 수정으로 우회
        if (!evaluationResult.tail_question && !evaluationResult.deep_dive) {
           evaluationResult.tail_question = {
               should_show: true,
               question: "모델 배포 후 데이터 분포가 급격히 변하는 'Data Drift'가 발생하면, 기존의 기준점(Anchor)을 어떻게 처리해야 할까요?",
               options: [
                   { id: 1, text: "새로운 데이터에 맞춰 기준점을 즉시 재학습(Re-fit)한다.", is_correct: true, feedback: "안정성을 위해 주기적인 기준점 업데이트가 필요합니다." },
                   { id: 2, text: "모델의 일관성을 위해 초기 기준점을 절대 바꾸지 않는다.", is_correct: false, feedback: "데이터 분포 변화에 대응하지 못해 성능이 저하될 수 있습니다." }
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
            }, 1800);
        } else {
            showMetrics.value = true;
            // [2026-02-19] 이미 데이터가 있더라도 캔버스가 다시 그려질 수 있도록 차트 렌더링 호출 보장
            nextTick(() => {
                if (typeof renderRadarChart === 'function') renderRadarChart();
            });
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

// [2026-02-21] 실습 종료 확인 모달 (브라우저 confirm 제거)
const showCloseConfirmModal = ref(false);

const closePractice = () => {
  showCloseConfirmModal.value = true;
};

const confirmClosePractice = () => {
  showCloseConfirmModal.value = false;
  emit('close');
};

// [2026-02-22 Fix] usePseudocodePractice에서 resetFlow로 export되므로 engineResetFlow 대신 resetFlow 사용
const handleResetFlow = () => {
    resetFlow();              // usePseudocodePractice의 resetFlow (= engineResetFlow)
    finalReport.value = null;
    showMetrics.value = false;
    isGeneratingReport.value = false;
    showHintDuck.value = false;
    addSystemLog("시스템을 처음부터 다시 시작합니다.", "INFO");
};

const completeMission = async () => {
    const stageIdx = (gameState.currentStageId || 1) - 1;

    // 1) GameStore를 통한 해금 (내부적으로 ProgressStore unlockNode도 연동되어 있음)
    await gameStore.unlockNextStage('Pseudo Practice', stageIdx);
    if (stageIdx < 9) {
        gameStore.selectedQuestIndex = stageIdx + 1;
    }

    // 2) 백엔드에 점수 전송 체계 (ProgressStore 활용)
    try {
        const { useProgressStore } = await import('@/stores/progress');
        const progressStore = useProgressStore();

        // [2026-02-24 Fix] DB PracticeDetail PK 형식에 맞춰 detail_id 조립
        // activeUnit.problems[stageIdx].dbDetailId 우선 사용, 없으면 unit01_XX 형식 폴백
        const problems = gameStore.activeUnit?.problems || [];
        const currentProblem = problems[stageIdx];
        const currentDetailId = currentProblem?.dbDetailId
            || `unit01_${String(stageIdx + 1).padStart(2, '0')}`;

        // 점수 획득 (finalReport 에서 가장 정확함)
        const finalScore = finalReport.value?.totalScore
            || evaluationResult.overall_score
            || 0;

        // [2026-02-24 Fix] MyRecordsView의 getEvaluation()이 인식하는 형식으로 submitted_data 구성
        const submittedData = {
            missionName: currentMission.value?.title || 'Unknown Pseudo Mission',
            track_type: 'pseudocode',
            '작성한 설계 (Training Log)': gameState.phase3Reasoning || '제출된 설계 데이터가 없습니다.',
            evaluation: {
                total_score_100: finalScore,
                one_line_review: finalReport.value?.finalReport?.summary
                    || evaluationResult.one_line_review
                    || '',
                dimensions: {},
                python_feedback: evaluationResult.senior_advice || ''
            }
        };

        // finalReport.metrics → dimensions 변환 (MyRecordsView가 기대하는 구조)
        if (finalReport.value?.metrics) {
            Object.entries(finalReport.value.metrics).forEach(([key, metric]) => {
                submittedData.evaluation.dimensions[key] = {
                    score: metric.percentage || metric.score || 0,
                    basis: metric.comment || '',
                    improvement: ''
                };
            });
        }

        await progressStore.submitScore(currentDetailId, finalScore, submittedData);

        addSystemLog(`미션 완료: 스테이지 ${gameState.currentStageId} 데이터베이스 기록됨.`, "SUCCESS");
    } catch (err) {
        console.error('점수 저장 실패:', err);
        addSystemLog(`점수 저장에 실패했습니다: ${err.message}`, "ERROR");
    }

    emit('close');
};

const isNaturalLanguagePhase = computed(() => {
    if (isProcessing.value || showMetrics.value || tutorialAnalyzing.value) return false;
    if (gameState.phase === 'PSEUDO_WRITE') return true;
    if (gameState.phase === 'DIAGNOSTIC_1' && diagnosticQuestion.value?.type === 'DESCRIPTIVE') return true;
    return false;
});

// [2026-02-14] 5대 지표 평가 시스템 추가 (상태 변수는 상단으로 이동됨)

// [2026-02-22 Fix] 중복 실행 차단 플래그 (finalReport와 별개)
const isGeneratingReport = ref(false);

async function runComprehensiveEvaluation() {
  // [2026-02-22 Fix] 이중 차단: 생성 중이면 스킵 (finalReport.value 체크는 제거하여 강제 갱신 허용)
  if (isGeneratingReport.value) return;
  isGeneratingReport.value = true;
  tutorialAnalyzing.value = false;

  try {
    // [2026-02-22 Fix] 생성 시작 전 기존 리포트 명시적 파기 (잔상 방지)
    finalReport.value = null;
    gameState.feedbackMessage = "시니어 아키텍트가 최종 검토 중입니다...";

    // [2026-02-22 Fix] dimensions 데이터 정합성 로그 및 정규화
    const rawDimensions = { ...evaluationResult.dimensions } || {};
    console.log('[ReportGen] Evaluating with score:', evaluationResult.overall_score, 'and dimensions keys:', Object.keys(rawDimensions));
    
    const normalizedMetrics = _normalizeDimensions(rawDimensions, evaluationResult.overall_score || 0);

    const resultsForReport = {
      metrics: normalizedMetrics,
      total: evaluationResult.overall_score || 0,
      questId: gameState.currentStageId || 1
    };

    // [2026-02-22 Fix] 최후의 보루 (Last Resort Guard): 
    // 점수는 60점 이상인데 페르소나가 '학생(저의도)'이거나 요약이 '짧습니다'인 경우 강제 복구
    let finalPersona = evaluationResult.persona_name;
    let finalSummary = evaluationResult.one_line_review;
    
    if ((evaluationResult.overall_score || 0) >= 60) {
        // [2026-02-22 Fix] 세분화된 페르소나(주니어, 전략가 등)가 이미 설정되어 있다면 보호
        const isGenericArchitect = !finalPersona || finalPersona === 'Senior Architect' || finalPersona === '아키텍트';
        if (finalPersona?.includes('학생') || isGenericArchitect) {
            finalPersona = "미래를 설계하는 아키텍트";
        }
        if (!finalSummary || finalSummary.includes('짧습니다') || finalSummary.includes('부족하여')) {
            finalSummary = "축하합니다! 핵심 설계 원리를 완벽히 파악하여 시스템 아키텍처를 성공적으로 복구하셨습니다.";
        }
    }

    const backendFeedback = {
      persona: finalPersona,
      summary: finalSummary,
      strengths: evaluationResult.strengths || [],
      improvements: evaluationResult.weaknesses || [],
      senior_advice: evaluationResult.senior_advice,
      recommended_videos: evaluationResult.recommended_videos || [], // [2026-02-22 Fix] 유튜브 데이터 전달
    };

    finalReport.value = await generateCompleteLearningReport(
      resultsForReport,
      null,
      backendFeedback
    );

    // 영상 큐레이션: 백엔드 → 로컬 폴백
    // [2026-02-23 Fix] 백엔드 필드명(channel, id)을 프론트 템플릿(channelTitle, videoId, thumbnail)으로 정규화
    if (evaluationResult.recommended_videos?.length) {
      evaluationResult.supplementaryVideos = evaluationResult.recommended_videos.map(v => ({
        ...v,
        videoId: v.videoId || v.id,
        channelTitle: v.channelTitle || v.channel || '',
        thumbnail: v.thumbnail || `https://img.youtube.com/vi/${v.videoId || v.id}/mqdefault.jpg`,
        url: v.url || `https://www.youtube.com/watch?v=${v.videoId || v.id}`,
        description: v.description || v.desc || '',
      }));
    } else if (finalReport.value?.recommendedContent?.videos?.length) {
      evaluationResult.supplementaryVideos = finalReport.value.recommendedContent.videos;
    }

    showMetrics.value = true;
    await nextTick();
    renderRadarChart();
  } catch (error) {
    console.error('[5D] Report generation error:', error);
    showMetrics.value = true;
  } finally {
    tutorialAnalyzing.value = false;
    isGeneratingReport.value = false;
  }
}

async function submitPseudoEnhanced() {
  await originalSubmitPseudo();
}

function getApiKey() {
  return import.meta.env.VITE_OPENAI_API_KEY || '';
}

/**
 * [2026-02-22 Fix] 백엔드 dimensions 키 → reportGenerator 기대 키 매핑
 * 백엔드: design, consistency, abstraction, edgeCase, implementation
 * reportGenerator: design, consistency, abstraction, edgeCase, implementation
 * 백엔드 키가 coherence, exception_handling 등으로 다를 수 있으므로 정규화
 */
function _normalizeDimensions(raw, totalScore) {
  // [2026-02-22 Fix] raw 데이터가 아예 비어있을 경우 (재평가 실패 등) 
  // totalScore를 지표별 가중치로 분배하여 최소한의 오각형을 그려줌
  const hasRawData = raw && Object.keys(raw).length > 0;
  
  // 키 매핑 테이블: 백엔드 키 → 프론트 키
  const KEY_MAP = {
    design:           'design',
    consistency:      'consistency',
    coherence:        'consistency',
    abstraction:      'abstraction',
    edgeCase:         'edgeCase',
    edge_case:        'edgeCase',
    exception_handling: 'edgeCase',
    implementation:   'implementation',
  };

  const DISPLAY_NAMES = {
    design:         '설계력',
    consistency:    '정합성',
    abstraction:    '추상화',
    edgeCase:       '예외체지력',
    implementation: '구현력',
  };

  const DEFAULTS = {
    design:         { score: 0, max: 25, percentage: 0, comment: '분석 데이터 부족' },
    consistency:    { score: 0, max: 20, percentage: 0, comment: '분석 데이터 부족' },
    abstraction:    { score: 0, max: 15, percentage: 0, comment: '분석 데이터 부족' },
    edgeCase:       { score: 0, max: 15, percentage: 0, comment: '분석 데이터 부족' },
    implementation: { score: 0, max: 10, percentage: 0, comment: '분석 데이터 부족' },
  };

  const result = { ...DEFAULTS };

  if (hasRawData) {
    for (const [rawKey, rawVal] of Object.entries(raw)) {
      const normalizedKey = KEY_MAP[rawKey];
      if (!normalizedKey) continue;

      const src = typeof rawVal === 'object' && rawVal !== null ? rawVal : {};
      const score = src.score ?? 0;
      const max = src.max ?? DEFAULTS[normalizedKey]?.max ?? 10;
      const percentage = src.percentage ?? (max > 0 ? Math.round((score / max) * 100) : 0);

      result[normalizedKey] = {
        score,
        max,
        percentage,
        comment: src.comment ?? src.feedback ?? '',
        name: DISPLAY_NAMES[normalizedKey],
      };
    }
  } else if (totalScore > 0) {
    // [2026-02-22 Fix] 데이터가 없는데 점수는 있는 경우 (복구 성공 후 재평가 오염 시)
    // 점수를 가중치 비율대로 강제 분배하여 차트 0점 현상 방어
    const ratio = totalScore / 100;
    for (const key of Object.keys(DEFAULTS)) {
      const max = DEFAULTS[key].max;
      result[key] = {
        score: Math.round(max * ratio),
        max: max,
        percentage: Math.round(totalScore),
        comment: '청사진 기반 설계 복구 완료',
        name: DISPLAY_NAMES[key]
      };
    }
  }

  // name 필드 최종 보장
  for (const [key, val] of Object.entries(result)) {
    if (!val.name) val.name = DISPLAY_NAMES[key] || key;
  }

  return result;
}

function renderRadarChart() {
  if (!radarChartCanvas.value || !finalReport.value) return;
  if (radarChartInstance) radarChartInstance.destroy();

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
          ticks: { stepSize: 20, color: '#999', display: false }, // [수정] 숫자 제거
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

function getMetricColor(percentage) {
  if (percentage >= 90) return '#4ade80';
  if (percentage >= 75) return '#60a5fa';
  if (percentage >= 60) return '#fbbf24';
  return '#f87171';
}

const weakestMetricKey = computed(() => {
  if (!finalReport.value || !finalReport.value.metrics) return null;
  const metrics = finalReport.value.metrics;
  const metricKeys = ['design', 'edgeCase', 'abstraction', 'implementation', 'consistency'];
  const priorities = { design: 5, consistency: 4, edgeCase: 3, abstraction: 2, implementation: 1 };
  
  return [...metricKeys].sort((a, b) => {
    const ma = metrics[a];
    const mb = metrics[b];
    if (ma.percentage !== mb.percentage) return ma.percentage - mb.percentage;
    return (priorities[b] || 0) - (priorities[a] || 0);
  })[0];
});

function getMetricVideo(metricKey) {
  if (!metricKey || !LEARNING_RESOURCES[metricKey]) return { title: '', url: '', curationPoint: '' };
  return LEARNING_RESOURCES[metricKey].videos[0];
}


const isInteractionPhase = computed(() => {
    const p = gameState.phase;
    return p.startsWith('DIAGNOSTIC') || 
           ['PSEUDO_WRITE', 'PYTHON_VISUALIZATION', 'EVALUATION', 'TAIL_QUESTION', 'DEEP_QUIZ'].includes(p);
});

const diagnosticProblemParts = computed(() => {
    const context = diagnosticQuestion.value?.problemContext || "";
    if (!context) return null;
    const parts = context.split('\n\n');
    return { instruction: parts[0], code: parts.slice(1).join('\n\n') };
});

watch(() => gameState.phase, async (newPhase) => {
    try {
        gameState.showHint = false;
        
        // [2026-02-22 Fix] 복구 학습 단계 진입 시 기존 리포트 초기화 (구형 데이터 노출 방지)
        // 0점 리포트 잔상 해결을 위해 감시하는 페이즈를 대폭 확대
        const resetPhases = [
            'PYTHON_VISUALIZATION', 
            'PSEUDO_WRITE', 
            'DIAGNOSTIC_1',
            'TAIL_QUESTION',
            'DEEP_DIVE_DESCRIPTIVE',
            'DEEP_QUIZ'
        ];

        if (resetPhases.includes(newPhase)) {
            finalReport.value = null;
            showMetrics.value = false;
            console.log(`[Phase Reset] ${newPhase} 진입으로 인한 리포트 초기화`);
        }

        if (newPhase === 'EVALUATION' && !showTutorial.value) {
            // [2026-02-22 Fix] isProcessing이 true인 경우 (submitDescriptiveDeepDive 진행 중)
            // finally에서 false로 바뀌는 시점을 기다린 후 리포트 생성
            await nextTick();
            await runComprehensiveEvaluation();
        }
    } catch(e) { console.warn("[PseudocodePractice] Main phase watcher error on unmount:", e); }
});

const { monacoOptions, handleMonacoMount } = useMonacoEditor(
    currentMission, 
    reactive({
        get userCode() { return gameState.phase3Reasoning; },
        set userCode(v) { gameState.phase3Reasoning = v; }
    })
);
</script>

<style scoped src="./PseudocodePractice.css"></style>

<style scoped>
/* [2026-02-14] 코덕 캐릭터 클릭 유도 효과 제거 (사용자 요청: 수동 힌트만 제공) */
.visual-frame {
    position: relative;
    cursor: pointer;
}

@keyframes pulse-hint {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 1; }
}

@keyframes pulse-glow {
    0%, 100% { filter: drop-shadow(0 0 15px rgba(59, 130, 246, 0.3)); }
    50% { filter: drop-shadow(0 0 30px rgba(59, 130, 246, 0.7)); }
}

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

.visualization-p-zero {
  padding: 0 !important;
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

/* [2026-02-21] 실습 종료 모달 위험 버튼 */
.btn-modal-danger {
  background: rgba(239, 68, 68, 0.15) !important;
  border-color: #ef4444 !important;
  color: #f87171 !important;
}
.btn-modal-danger:hover {
  background: #ef4444 !important;
  color: #fff !important;
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.5);
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
  margin-right: 15px;
  align-self: flex-end;
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
  bottom: 80px !important;
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

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
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
