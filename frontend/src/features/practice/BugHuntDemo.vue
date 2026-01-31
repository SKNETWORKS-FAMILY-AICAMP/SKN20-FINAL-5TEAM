<template>
  <div class="ac-stage" :class="{ 'shake-effect': isShaking }">
    <!-- 1. 배경: 연두색 삼각형 패턴 -->
    <div class="ac-bg-layer"></div>

    <!-- 2. 캐릭터 존 (좌우 대화형) -->
    <transition name="char-slide" mode="out-in">
      <div
        :key="activeCharKey + '-' + activeCharSide"
        class="ac-char-zone"
        :class="activeCharSide"
      >
        <img :src="activeCharImage"
             :class="['ac-char-img', { 'talking': isTyping }]"
             alt="Character" />

        <!-- 성공했을 때 나타나는 효과 -->
        <transition name="bounce-pop">
          <div v-if="phase === 'SUCCESS_SHOW'" class="ac-catch-effect">
            <div class="catch-sparkle">✨ MISSION CLEAR! ✨</div>
          </div>
        </transition>
      </div>
    </transition>

    <!-- 3. 대화 인터페이스 (시나리오 진행) -->
    <div v-if="phase !== 'CODE_MOD' && phase !== 'RESULT_REPORT' && phase !== 'EXPLAIN'" class="ac-ui-layer">
      <div class="ac-bubble-wrap">
        <div v-if="activeCharName" class="ac-name-tag">{{ activeCharName }}</div>

        <div class="ac-bubble-body" @click="handleInteraction">
          <div class="ac-text-box">
            <p style="white-space: pre-line;">{{ displayText }}</p>
          </div>
          <div v-if="!isTyping" class="ac-next-nav">→</div>
        </div>
      </div>
    </div>

    <!-- 설명 입력 인터페이스 (회사 서류 스타일) -->
    <div v-if="phase === 'EXPLAIN'" class="explain-overlay">
      <div class="explain-document">
        <div class="doc-header">
          <h2 class="doc-title">📋 디버깅 전략 보고서</h2>
          <div class="doc-number">문서번호: DBG-{{ currentStep.toString().padStart(3, '0') }}</div>
        </div>

        <div class="doc-info-section">
          <table class="doc-info-table">
            <tr>
              <th>작성자</th>
              <td>{{ scenarioData.characters.employee.name }}</td>
              <th>STEP</th>
              <td>{{ currentStep }}/3</td>
            </tr>
            <tr>
              <th>버그 유형</th>
              <td colspan="3">{{ stepContent?.bug_type }}</td>
            </tr>
          </table>
        </div>

        <div class="doc-content-section">
          <div class="doc-section-title">■ 해결 전략 및 조치 내역</div>
          <div class="doc-field-label">문제를 어떻게 파악하고 해결했는지 작성해주세요.</div>
          <textarea
            v-model="explanationInput"
            class="doc-textarea"
            placeholder="예) 데이터 누수 문제를 발견했습니다. train/test 분할 전에 전체 데이터로 스케일링을 하면 테스트 데이터의 정보가 모델에 새어나가기 때문에, train 데이터만으로 fit하도록 수정했습니다."
            rows="8"
          ></textarea>
          <div class="char-count-doc">{{ explanationInput.trim().length }}자</div>
        </div>

        <div class="doc-footer">
          <button
            class="btn-submit-doc"
            @click="submitExplanation"
            :disabled="explanationInput.trim().length === 0"
          >
            제출하기
          </button>
        </div>
      </div>
    </div>

    <!-- 4. 코드 편집 모드 (책상 오피스 스타일) -->
    <transition name="pop">
      <div v-if="phase === 'CODE_MOD'" class="ac-editor-overlay">
        <div class="office-desk-container">
          <!-- 상단 헤더 -->
          <div class="desk-header">
            <span class="step-indicator">🎯 MISSION STEP {{ currentStep }}/3</span>
            <div class="header-buttons">
              <button class="btn-reset" @click="resetCurrentCode">
                <span>🔄</span> 초기화
              </button>
              <button class="btn-submit" @click="verifyCode">
                <span>📤</span> 제출하기
              </button>
              <button class="close-btn" @click="phase = 'TALK'">✕ 나가기</button>
            </div>
          </div>

          <!-- 책상 작업 공간 -->
          <div class="desk-workspace">
            <!-- 왼쪽: 메모보드 -->
            <div class="memo-board">
              <div class="memo-board-frame">
                <div class="memo-pin top-left">📌</div>
                <div class="memo-pin top-right">📌</div>

                <div class="memo-content">
                  <div class="memo-header">
                    <span class="bug-badge">{{ stepContent?.bug_type }}</span>
                    <h3 class="memo-title">{{ stepContent?.title }}</h3>
                  </div>

                  <div class="memo-body">
                    <div class="memo-section">
                      <div class="memo-label">🔍 발견</div>
                      <p>{{ stepContent?.situation?.discovery }}</p>
                    </div>
                    <div class="memo-section">
                      <div class="memo-label">⚠️ 문제</div>
                      <p>{{ stepContent?.situation?.problem }}</p>
                    </div>
                  </div>

                  <div class="hint-section">
                    <button class="btn-hint" @click="toggleHint">
                      {{ hintOn ? '💡 힌트 닫기' : '💡 힌트 보기' }}
                    </button>
                    <transition name="fade">
                      <div v-if="hintOn" class="hint-box">
                        <div class="hint-icon">💭</div>
                        <p>{{ stepContent?.hint }}</p>
                      </div>
                    </transition>
                  </div>
                </div>
              </div>
            </div>

            <!-- 오른쪽: 모니터 -->
            <div class="monitor-container">
              <div class="monitor-frame">
                <div class="monitor-bezel">
                  <div class="monitor-screen-wrapper">
                    <div class="code-editor-section">
                      <VueMonacoEditor
                        :key="currentStep"
                        v-model:value="editorCode"
                        theme="vs-dark"
                        language="python"
                        :options="editorOptions"
                        height="100%"
                      />
                    </div>
                    <div class="terminal-section">
                      <div class="terminal-header">
                        <span class="terminal-title">📟 CONSOLE OUTPUT</span>
                        <button class="terminal-clear" @click="consoleLogs = []">Clear</button>
                      </div>
                      <div class="terminal-content" ref="terminalRef">
                        <div v-if="consoleLogs.length === 0" class="terminal-empty">
                          <span>대기 중...</span>
                        </div>
                        <div
                          v-for="(log, index) in consoleLogs"
                          :key="index"
                          class="terminal-line"
                          :class="log.type"
                        >
                          <span class="terminal-prefix">{{ log.prefix }}</span>
                          <span class="terminal-message">{{ log.message }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="monitor-stand"></div>
              </div>
            </div>
          </div>

          <!-- 버그 애니메이션 -->
          <div class="bugs-container">
            <div
              v-for="bugIndex in remainingBugs"
              :key="'bug-' + currentStep + '-' + bugIndex"
              class="flying-bug"
              :class="{ dead: killedBugs.includes(currentStep + '-' + bugIndex) }"
              :style="{ left: bugPositions[bugIndex].left, top: bugPositions[bugIndex].top }"
            >
              <span class="bug-emoji">🐛</span>
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
        </div>
      </div>
    </transition>

    <!-- 5. 최종 인사평가 리포트 (실제 회사 평가지 스타일) -->
    <div v-if="phase === 'RESULT_REPORT'" class="ac-result-screen">
      <div class="kpi-report-card">
        <!-- 문서 헤더 -->
        <div class="report-header">
          <div class="header-top">
            <div class="company-info">
              <div class="company-logo-text">A+ 통신사</div>
            </div>
            <div class="doc-info">
              <div class="doc-number">문서번호: HR-2026-Q1-001</div>
              <div class="doc-date">평가일: {{ currentDate }}</div>
            </div>
          </div>
          <h1 class="report-title">인 사 평 가 서</h1>
          <div class="eval-period">평가기간: 2026년 1분기 (01.01 ~ 03.31)</div>
        </div>

        <!-- 피평가자 정보 -->
        <div class="eval-info-section">
          <table class="info-table">
            <tr>
              <th>성명</th>
              <td>{{ scenarioData.characters.employee.name }}</td>
              <th>소속</th>
              <td>마케팅 AI팀</td>
            </tr>
            <tr>
              <th>직급</th>
              <td>인턴</td>
            </tr>
          </table>
        </div>

        <!-- 종합 평가 등급 -->
        <div class="eval-grade-section">
          <h3 class="section-title">■ 종합 평가</h3>
          <div class="grade-result-box">
            <div class="grade-info">
              <div class="grade-label-text">평가 등급</div>
              <div class="grade-badge" :class="'grade-' + evaluationResult?.grade">
                {{ evaluationResult?.grade }}
              </div>
              <div class="grade-description">{{ evaluationResult?.evaluation }}</div>
            </div>
            <div class="salary-result">
              <div class="salary-label-text">연봉 조정</div>
              <div class="salary-value-box" :class="{
                'positive': evaluationResult?.salaryChange.includes('+'),
                'negative': evaluationResult?.salaryChange.includes('-'),
                'neutral': evaluationResult?.salaryChange.includes('동결')
              }">
                {{ evaluationResult?.salaryChange }}
              </div>
              <div v-if="evaluationResult?.totalScore >= 70" class="approval-stamp">
                <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="50" cy="50" r="45" fill="none" stroke="#e74c3c" stroke-width="6" opacity="0.8"/>
                  <text x="50" y="45" font-size="18" font-weight="bold" fill="#e74c3c" text-anchor="middle">승인</text>
                  <text x="50" y="65" font-size="14" font-weight="bold" fill="#e74c3c" text-anchor="middle">HR팀</text>
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- 평가 항목 및 점수 -->
        <div class="eval-items-section">
          <h3 class="section-title">■ 평가 항목</h3>
          <table class="eval-table">
            <thead>
              <tr>
                <th width="30%">평가항목</th>
                <th width="15%">배점</th>
                <th width="15%">득점</th>
                <th width="40%">평가내용</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="item-name">문제 해결력</td>
                <td>40점</td>
                <td class="score-cell">{{ Math.round(evaluationResult?.kpi.accuracy * 0.4) }}점</td>
                <td class="desc-cell">
                  <div class="progress-bar-mini">
                    <div class="progress-fill" :style="{ width: evaluationResult?.kpi.accuracy + '%' }"></div>
                  </div>
                  <span class="score-detail">{{ evaluationResult?.kpi.accuracy }}/100 (재시도: {{ evaluationResult?.stats.codeRetries }}회)</span>
                </td>
              </tr>
              <tr>
                <td class="item-name">업무 효율성</td>
                <td>30점</td>
                <td class="score-cell">{{ Math.round(evaluationResult?.kpi.speed * 0.3) }}점</td>
                <td class="desc-cell">
                  <div class="progress-bar-mini">
                    <div class="progress-fill" :style="{ width: evaluationResult?.kpi.speed + '%' }"></div>
                  </div>
                  <span class="score-detail">{{ evaluationResult?.kpi.speed }}/100 (소요시간: {{ Math.floor(evaluationResult?.stats.totalTime / 60) }}분 {{ evaluationResult?.stats.totalTime % 60 }}초)</span>
                </td>
              </tr>
              <tr>
                <td class="item-name">자기주도성</td>
                <td>30점</td>
                <td class="score-cell">{{ Math.round(evaluationResult?.kpi.selfDirection * 0.3) }}점</td>
                <td class="desc-cell">
                  <div class="progress-bar-mini">
                    <div class="progress-fill" :style="{ width: evaluationResult?.kpi.selfDirection + '%' }"></div>
                  </div>
                  <span class="score-detail">{{ evaluationResult?.kpi.selfDirection }}/100 (힌트사용: {{ evaluationResult?.stats.hintsUsed }}회)</span>
                </td>
              </tr>
              <tr class="total-row">
                <td colspan="2"><strong>종합 점수</strong></td>
                <td colspan="2" class="total-score">{{ evaluationResult?.totalScore }}점</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 업무 수행 내역 -->
        <div class="work-detail-section">
          <h3 class="section-title">■ 주요 업무 수행 내역</h3>
          <div
            v-for="step in 3"
            :key="'log-' + step"
            class="work-item"
          >
            <div class="work-header">
              <span class="work-num">{{ step }}.</span>
              <span class="work-title">{{ scenarioData.steps[step - 1]?.title }}</span>
            </div>
            <div class="work-content">
              <div class="work-label">수행 방법 및 전략:</div>
              <div class="work-text">{{ stepExplanations[step] || '(미작성)' }}</div>
            </div>
          </div>
        </div>

        <!-- 평가자 의견 -->
        <div class="evaluator-comment-section">
          <h3 class="section-title">■ 평가자 종합 의견</h3>
          <div class="comment-box">
            <p v-if="evaluationResult?.totalScore >= 90">
              탁월한 문제 해결 능력과 빠른 학습 능력을 보여주었습니다. 자기주도적으로 업무를 수행하며
              팀의 기대치를 크게 상회하는 성과를 달성하였습니다. 향후 정규직 전환을 적극 추천합니다.
            </p>
            <p v-else-if="evaluationResult?.totalScore >= 70">
              업무 수행 능력이 우수하며, 주어진 과제를 성실히 완수하였습니다.
              지속적인 성장 가능성이 높아 보이며, 추가적인 학습과 경험을 통해 더욱 발전할 것으로 기대됩니다.
            </p>
            <p v-else-if="evaluationResult?.totalScore >= 50">
              기본적인 업무 수행 능력을 갖추고 있으나, 효율성과 자기주도성 측면에서 개선이 필요합니다.
              멘토링과 추가 교육을 통해 역량을 강화할 수 있도록 지원이 필요합니다.
            </p>
            <p v-else>
              업무 수행에 어려움을 보이고 있습니다. 기본 역량 강화를 위한 집중적인 교육과
              1:1 멘토링이 필요하며, 개선 계획 수립 및 이행이 시급합니다.
            </p>
          </div>
        </div>

        <!-- AI 평가 섹션 -->
        <div class="ai-evaluation-section">
          <h3 class="section-title">■ AI 분석 리포트</h3>

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

            <!-- 단계별 AI 피드백 -->
            <div class="step-feedbacks">
              <div class="feedback-title">📋 단계별 AI 피드백</div>
              <div
                v-for="step in 3"
                :key="'feedback-' + step"
                class="step-feedback-box"
              >
                <div class="step-feedback-header">
                  <span class="step-num">STEP {{ step }}</span>
                  <span class="step-title">{{ scenarioData.steps[step - 1]?.title }}</span>
                </div>
                <div v-if="aiEvaluationResult.step_feedbacks && aiEvaluationResult.step_feedbacks[step]" class="step-feedback-content">
                  <div class="feedback-label">🤖 AI FEEDBACK</div>
                  <p class="feedback-text">{{ aiEvaluationResult.step_feedbacks[step] }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 하단 버튼 -->
        <div class="report-actions">
          <button class="btn-restart" @click="restart">다시 평가 받기</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, reactive, nextTick } from 'vue';
import { VueMonacoEditor } from '@guolao/vue-monaco-editor';
import { loadPyodide } from 'pyodide';
import scenarioData from './bughunt-demo-data.json';
import { evaluateBugHunt } from './services/bugHuntApi';

const phase = ref('START');
const currentStep = ref(1);
const talkIdx = ref(0);
const displayText = ref('');
const isTyping = ref(false);
const typingInterval = ref(null); // 타이핑 interval 관리용
const editorCode = ref('');
const hintOn = ref(false);

// Pyodide 관련
const pyodide = ref(null);
const pyodideLoading = ref(false);
const consoleLogs = ref([]);
const terminalRef = ref(null);

// 설명 입력 관련
const stepExplanations = reactive({ 1: '', 2: '', 3: '' });
const explanationInput = ref('');

// 각 단계의 제출된 코드 저장
const stepCodes = reactive({ 1: '', 2: '', 3: '' });

// 평가 관련
const startTime = ref(Date.now());
const totalTime = ref(0);
const hintsUsed = ref(0);
const codeRetries = ref(0);

// 최종 평가 결과
const evaluationResult = ref(null);

// AI 평가 상태
const isEvaluatingAI = ref(false);
const aiEvaluationResult = ref(null);

const stepContent = computed(() => scenarioData.steps[currentStep.value - 1]);

// 현재 날짜 (YYYY.MM.DD 형식)
const currentDate = computed(() => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}.${month}.${day}`;
});

// 버그 애니메이션 관련 상태
const bugPositions = reactive({
  1: { left: '20%', top: '30%' },
  2: { left: '70%', top: '45%' },
  3: { left: '50%', top: '60%' }
});

let bugAnimationIds = { 1: null, 2: null, 3: null };

// 죽은 버그 추적
const killedBugs = ref([]);

// 해골 날아가는 애니메이션
const showFlyingSkull = ref(false);
const flyingSkullPosition = reactive({ x: 50, y: 50 });

const flyingSkullStyle = computed(() => ({
  left: `${flyingSkullPosition.x}%`,
  top: `${flyingSkullPosition.y}%`
}));

// 화면 흔들림 효과
const isShaking = ref(false);

// 저격 애니메이션 상태
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

// 배경 이미지 URL
const mainBackground = computed(() => `url(${scenarioData.scenario.backgrounds.main})`);
const editorBackground = computed(() => `url(${scenarioData.scenario.backgrounds.editor})`);

// 각 스텝에서 고쳐야 하는 버그 개수 계산
const remainingBugs = computed(() => {
  // CODE_MOD phase가 아니면 버그를 표시하지 않음
  if (phase.value !== 'CODE_MOD') return [];

  let bugCount = 1; // 기본값
  if (currentStep.value === 1) {
    bugCount = 1; // Step 1: fit_transform(X) -> fit_transform(X_train) (1곳)
  } else if (currentStep.value === 2) {
    bugCount = 1; // Step 2: stratify=y 추가 (1곳)
  } else if (currentStep.value === 3) {
    bugCount = 2; // Step 3: X_train->X_test, y_train->y_test (2곳)
  }

  return Array.from({ length: bugCount }, (_, i) => i + 1);
});

// 캐릭터 데이터 바인딩
const activeCharKey = computed(() => {
  if (phase.value === 'START') return 'employee';
  const dialogues = (phase.value === 'TALK') ? stepContent.value?.dialogues : stepContent.value?.success_dialogue;
  return dialogues?.[talkIdx.value]?.character || 'employee';
});

const activeCharName = computed(() => {
  if (phase.value === 'START') return '안내';
  return scenarioData.characters[activeCharKey.value]?.name;
});

const activeCharImage = computed(() => {
  const charKey = (phase.value === 'START') ? 'employee' : activeCharKey.value;

  // 덕인턴일 경우 감정에 따라 이미지 변경
  if (charKey === 'employee') {
    const emotion = activeEmotion.value;

    if (emotion === 'happy') {
      return '/image/duck_employee_happy.png';
    } else if (emotion === 'sad') {
      return '/image/duck_employee_sad.png';
    }
    // 기본 이미지 (START phase 등)
    return '/image/duck_employee_happy.png';
  }

  return scenarioData.characters[charKey]?.image;
});

const activeEmotion = computed(() => {
  if (phase.value === 'START') return null;
  const dialogues = (phase.value === 'TALK') ? stepContent.value?.dialogues : stepContent.value?.success_dialogue;
  return dialogues?.[talkIdx.value]?.emotion;
});

// 이전 캐릭터 추적 (좌우 배치용)
const prevCharKey = ref('employee');

// 캐릭터 좌우 배치 (왼쪽: 인턴, 오른쪽: 대리/팀장)
const activeCharSide = computed(() => {
  // employee(인턴)는 항상 왼쪽
  if (activeCharKey.value === 'employee') {
    return 'left';
  }
  // deputy(대리), teamlead(팀장)는 항상 오른쪽
  return 'right';
});

// 감정에 따른 이모지 반환
function getEmotionEmoji(emotion) {
  const emotionMap = {
    happy: '😊',
    worried: '😰',
    confused: '😕',
    explaining: '🤓',
    shocked: '😱',
    relieved: '😌',
    calm: '😊',
    frustrated: '😤',
    thinking: '🤔',
    checking: '🔍',
    understanding: '💡',
    proud: '😎',
    impressed: '👏',
    serious: '😐',
    stern: '😠',
    satisfied: '😌',
    grateful: '🙏'
  };
  return emotionMap[emotion] || '😊';
}

const type = (msg) => {
  if (!msg) return;

  // 이전 타이핑 애니메이션이 실행 중이면 중단
  if (typingInterval.value) {
    clearInterval(typingInterval.value);
    typingInterval.value = null;
  }

  displayText.value = '';
  isTyping.value = true;
  let i = 0;
  typingInterval.value = setInterval(() => {
    if (i < msg.length) {
      displayText.value += msg[i++];
    } else {
      clearInterval(typingInterval.value);
      typingInterval.value = null;
      isTyping.value = false;
    }
  }, 30);
};

const handleInteraction = async () => {
  if (isTyping.value) return;

  if (phase.value === 'START') {
    phase.value = 'TALK';
    talkIdx.value = 0;
    prevCharKey.value = activeCharKey.value;
    type(stepContent.value.dialogues[0].text);
  }
  else if (phase.value === 'TALK') {
    if (talkIdx.value < stepContent.value.dialogues.length - 1) {
      prevCharKey.value = activeCharKey.value;
      talkIdx.value++;
      type(stepContent.value.dialogues[talkIdx.value].text);
    } else {
      phase.value = 'CODE_MOD';
      editorCode.value = stepContent.value.buggy_code;
      hintOn.value = false;
      consoleLogs.value = []; // 터미널 로그 초기화

      // Pyodide 초기화 (백그라운드에서)
      if (!pyodide.value && !pyodideLoading.value) {
        initPyodide();
      }

      // 코드 입력창으로 전환 시 버그 애니메이션 시작
      setTimeout(() => {
        startBugAnimations();
      }, 300);
    }
  }
  else if (phase.value === 'SUCCESS_SHOW') {
    phase.value = 'SUCCESS_TALK';
    talkIdx.value = 0;
    prevCharKey.value = activeCharKey.value;
    type(stepContent.value.success_dialogue[0].text);
  }
  else if (phase.value === 'SUCCESS_TALK') {
    console.log('SUCCESS_TALK clicked:', {
      currentStep: currentStep.value,
      talkIdx: talkIdx.value,
      dialogueLength: stepContent.value.success_dialogue.length
    });

    if (talkIdx.value < stepContent.value.success_dialogue.length - 1) {
      prevCharKey.value = activeCharKey.value;
      talkIdx.value++;
      type(stepContent.value.success_dialogue[talkIdx.value].text);
    } else {
      console.log('Last dialogue finished, checking step:', currentStep.value);
      // 다음 단계 혹은 결과창
      if (currentStep.value < 3) {
        console.log('Moving to next step');
        currentStep.value++;
        phase.value = 'TALK';
        talkIdx.value = 0;
        prevCharKey.value = activeCharKey.value;
        type(stepContent.value.dialogues[0].text);
        // 죽은 버그 초기화 (새로운 step이므로)
        killedBugs.value = [];
        // 버그 애니메이션 재시작 (남은 버그 개수가 줄어듦)
        stopBugAnimations();
        setTimeout(() => {
          startBugAnimations();
        }, 500);
      } else {
        console.log('Showing evaluation report');
        // 평가 계산
        calculateEvaluation();
        // AI 평가 실행
        await showEvaluation();
        phase.value = 'RESULT_REPORT';
        stopBugAnimations();
      }
    }
  }
};

// Pyodide 초기화
async function initPyodide() {
  if (pyodide.value || pyodideLoading.value) return;

  pyodideLoading.value = true;
  addLog('info', 'Python 환경 초기화 중...');

  try {
    pyodide.value = await loadPyodide({
      indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.27.7/full/'
    });

    await pyodide.value.loadPackage(['scikit-learn', 'pandas', 'numpy']);
    addLog('success', 'Python 환경 준비 완료 ✓');
  } catch (error) {
    addLog('error', `초기화 실패: ${error.message}`);
  } finally {
    pyodideLoading.value = false;
  }
}

// 터미널 로그 추가
function addLog(type, message, prefix = null) {
  const prefixes = {
    info: '[INFO]',
    success: '[SUCCESS]',
    error: '[ERROR]',
    warning: '[WARNING]'
  };

  consoleLogs.value.push({
    type,
    prefix: prefix || prefixes[type] || '[LOG]',
    message
  });

  // 터미널 자동 스크롤
  nextTick(() => {
    if (terminalRef.value) {
      terminalRef.value.scrollTop = terminalRef.value.scrollHeight;
    }
  });
}

// 코드 실행 및 검증
async function verifyCode() {
  consoleLogs.value = []; // 로그 초기화

  // Pyodide 초기화가 안되어 있으면 초기화
  if (!pyodide.value) {
    addLog('info', 'Python 환경을 준비하고 있습니다...');
    await initPyodide();

    // 초기화 실패 시
    if (!pyodide.value) {
      addLog('error', 'Python 환경 초기화 실패. 페이지를 새로고침(Ctrl+Shift+R)해주세요.');
      return;
    }
  }

  // 재확인 (방어적 프로그래밍)
  if (!pyodide.value || !pyodide.value.runPythonAsync) {
    addLog('error', 'Python 환경이 준비되지 않았습니다. 페이지를 새로고침(Ctrl+Shift+R)해주세요.');
    return;
  }

  addLog('info', '코드 검증 중...');

  const check = stepContent.value.solution_check;
  const code = editorCode.value;
  let isCorrect = false;

  try {
    // Python 코드 실행
    await pyodide.value.runPythonAsync(`
import sys
from io import StringIO
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# stdout/stderr 캡처 설정
sys.stdout = StringIO()
sys.stderr = StringIO()

# 샘플 데이터 생성 (테스트용)
print("=" * 50)
print("📊 테스트 데이터 준비 중...")
df = pd.DataFrame({
    'churn': [0, 1, 0, 1, 0] * 20,
    'feature1': range(100),
    'feature2': range(100, 200)
})
print(f"데이터 크기: {df.shape}")
print(f"이탈 고객 비율: {df['churn'].mean():.1%}")
print("=" * 50)

# 사용자 코드 실행
try:
${code.split('\n').map(line => '    ' + line).join('\n')}

    print("\\n" + "=" * 50)
    print("✓ 코드 정의 완료")
    print("=" * 50)

    # 함수 실행 테스트
    print("\\n🔍 함수 실행 테스트 중...")

    # prepare_data 함수가 있으면 실행
    if 'prepare_data' in dir():
        result = prepare_data(df)
        if isinstance(result, tuple):
            if len(result) == 4:
                X_train, X_test, y_train, y_test = result
                print(f"\\n✓ 함수 실행 성공!")
                print(f"  - X_train shape: {X_train.shape}")
                print(f"  - X_test shape: {X_test.shape}")
                print(f"  - y_train 이탈률: {y_train.mean():.1%}")
                print(f"  - y_test 이탈률: {y_test.mean():.1%}")

                # 데이터 누수 체크 (Step 1)
                if hasattr(X_train, 'mean'):
                    print(f"\\n📈 데이터 통계:")
                    print(f"  - X_train mean: {X_train.mean():.4f}")
                    print(f"  - X_test mean: {X_test.mean():.4f}")

    # train_and_evaluate 함수가 있으면 실행
    if 'train_and_evaluate' in dir():
        accuracy = train_and_evaluate(df)
        print(f"\\n✓ 함수 실행 성공!")
        print(f"  - 정확도: {accuracy:.1%}")

except Exception as e:
    print("\\n" + "=" * 50)
    print(f"❌ 실행 오류 발생:")
    print(f"  {type(e).__name__}: {str(e)}")
    print("=" * 50)
    import traceback
    print("\\n📋 상세 오류 정보:")
    traceback.print_exc()
`);

    // 출력 가져오기
    const stdout = await pyodide.value.runPython('sys.stdout.getvalue()');
    const stderr = await pyodide.value.runPython('sys.stderr.getvalue()');

    if (stdout) {
      stdout.split('\n').forEach(line => {
        if (line.trim()) addLog('info', line, '>>>');
      });
    }

    if (stderr) {
      stderr.split('\n').forEach(line => {
        if (line.trim()) addLog('error', line, '[ERR]');
      });
    }

    // 패턴 체크 (Step 3 부분 정답 처리)
    let bugsToKill = [];

    if (check.type === 'multi_condition') {
      const hasAny = check.required_any ? check.required_any.some(r => code.includes(r)) : true;
      const hasAll = check.required_all ? check.required_all.every(r => code.includes(r)) : true;

      const hasForbidden = check.forbidden ? check.forbidden.some(f => {
        if (f.endsWith('(X)') && code.includes(f.replace('(X)', '(X_train)'))) return false;
        return code.includes(f);
      }) : false;

      isCorrect = hasAny && hasAll && !hasForbidden;

      // Step 3 부분 정답 체크
      if (currentStep.value === 3 && check.required_all) {
        // 버그 1: predict(X_test) 확인
        const hasBug1Fixed = code.includes('predict(X_test)');
        // 버그 2: y_test 사용 확인 (accuracy_score의 첫 번째 인자)
        const hasBug2Fixed = code.includes('accuracy_score(y_test,') || code.includes('accuracy_score( y_test,');

        const bug1Key = currentStep.value + '-1';
        const bug2Key = currentStep.value + '-2';

        if (hasBug1Fixed && !killedBugs.value.includes(bug1Key)) {
          bugsToKill.push(1);
        }
        if (hasBug2Fixed && !killedBugs.value.includes(bug2Key)) {
          bugsToKill.push(2);
        }
      }
    } else {
      isCorrect = new RegExp(check.value, check.flags || '').test(code);
    }

    // Step 3 부분 정답 처리
    if (currentStep.value === 3 && bugsToKill.length > 0) {
      // 부분 정답: 일부 버그만 죽이기
      for (const bugIndex of bugsToKill) {
        shootBugAtIndex(bugIndex, true);

        setTimeout(() => {
          const bugKey = currentStep.value + '-' + bugIndex;
          if (!killedBugs.value.includes(bugKey)) {
            killedBugs.value.push(bugKey);
          }
        }, 1000);
      }

      setTimeout(() => {
        if (isCorrect) {
          addLog('success', '✓ 버그 수정 완료! 모든 코드가 올바르게 작성되었습니다.');

          // 모든 버그 죽이고 다음 단계로
          setTimeout(() => {
            stopBugAnimations();
            phase.value = 'EXPLAIN';
            explanationInput.value = '';
          }, 1500);
        } else {
          addLog('warning', `✓ 부분 정답! ${bugsToKill.length}마리 처치 완료. 남은 버그를 찾아보세요!`);
          codeRetries.value++;
        }
      }, 1500);
    } else {
      // Step 1, 2 또는 완전 오답
      shootBug(isCorrect);

      setTimeout(() => {
        if (isCorrect) {
          addLog('success', '✓ 버그 수정 완료! 코드가 올바르게 작성되었습니다.');

          // 1.5초 후 설명 입력 페이즈로 전환
          setTimeout(() => {
            stopBugAnimations();
            phase.value = 'EXPLAIN';
            explanationInput.value = '';
          }, 1500);
        } else {
          addLog('warning', '❌ MISS! 코드가 아직 조건을 만족하지 않습니다. 힌트를 참고해보세요.');
          codeRetries.value++;
        }
      }, 500);
    }


  } catch (error) {
    addLog('error', `실행 실패: ${error.message}`);
    codeRetries.value++;
  }
}

// 설명 제출
function submitExplanation() {
  if (explanationInput.value.trim().length === 0) {
    alert('내용을 입력해주세요!');
    return;
  }

  // 현재 스텝의 설명과 코드 저장
  stepExplanations[currentStep.value] = explanationInput.value.trim();
  stepCodes[currentStep.value] = editorCode.value;

  // 성공 애니메이션 표시
  phase.value = 'SUCCESS_SHOW';

  // 2초 후 자동으로 SUCCESS_TALK로 전환
  setTimeout(() => {
    phase.value = 'SUCCESS_TALK';
    talkIdx.value = 0;
    prevCharKey.value = activeCharKey.value;
    type(stepContent.value.success_dialogue[0].text);
  }, 2000);
}

const resetCurrentCode = () => {
  if(confirm('코드를 원상복구 할까요?')) {
    editorCode.value = stepContent.value.buggy_code;
    codeRetries.value++;
  }
};

// 힌트 토글 및 사용 추적
function toggleHint() {
  // 힌트를 열 때만 카운트 증가
  if (!hintOn.value) {
    hintsUsed.value++;
  }
  hintOn.value = !hintOn.value;
}

// 평가 계산
function calculateEvaluation() {
  totalTime.value = Math.floor((Date.now() - startTime.value) / 1000); // 초 단위

  // KPI 점수 계산
  const accuracyScore = 100 - (codeRetries.value * 10); // 코드 재시도마다 -10점
  const speedScore = Math.max(0, 100 - Math.floor(totalTime.value / 30)); // 30초당 -1점
  const selfDirectionScore = 100 - (hintsUsed.value * 20); // 힌트 사용마다 -20점

  // 가중치 적용 (accuracy 40%, speed 30%, selfDirection 30%)
  const totalScore = Math.round(
    (Math.max(0, accuracyScore) * 0.4) +
    (Math.max(0, speedScore) * 0.3) +
    (Math.max(0, selfDirectionScore) * 0.3)
  );

  // 등급 결정
  let grade, salaryChange, evaluation;
  if (totalScore >= 90) {
    grade = 'S';
    salaryChange = '+500만원';
    evaluation = 'Excellent';
  } else if (totalScore >= 70) {
    grade = 'A';
    salaryChange = '+200만원';
    evaluation = 'Good';
  } else if (totalScore >= 50) {
    grade = 'B';
    salaryChange = '동결';
    evaluation = 'Average';
  } else {
    grade = 'C';
    salaryChange = '-100만원';
    evaluation = 'Needs Improvement';
  }

  // 보너스 조건 체크
  const bonuses = [];
  if (hintsUsed.value === 0) {
    bonuses.push({ name: '독립형 인재', icon: '🎯', bonus: '+100만원' });
  }
  if (codeRetries.value === 0) {
    bonuses.push({ name: '완벽주의자', icon: '💎', bonus: '+200만원' });
  }
  if (totalTime.value <= 300) { // 5분 이내
    bonuses.push({ name: '스피드 러너', icon: '⚡', bonus: '+50만원' });
  }

  evaluationResult.value = {
    totalScore,
    grade,
    salaryChange,
    evaluation,
    bonuses,
    kpi: {
      accuracy: Math.max(0, accuracyScore),
      speed: Math.max(0, speedScore),
      selfDirection: Math.max(0, selfDirectionScore)
    },
    stats: {
      totalTime: totalTime.value,
      hintsUsed: hintsUsed.value,
      codeRetries: codeRetries.value
    }
  };
}

// AI 평가 함수
async function showEvaluation() {
  isEvaluatingAI.value = true;
  try {
    aiEvaluationResult.value = await evaluateBugHunt(
      scenarioData.scenario.title,
      scenarioData.steps,
      stepExplanations,
      stepCodes,
      {
        quizIncorrectCount: 0, // 퀴즈가 없으므로 0
        codeSubmitFailCount: codeRetries.value,
        hintCount: hintsUsed.value,
        totalDebugTime: totalTime.value
      }
    );
  } catch (error) {
    console.error('❌ AI Evaluation failed:', error);
  } finally {
    isEvaluatingAI.value = false;
  }
}

// 위험도 레벨 계산
function getRiskLevel(risk) {
  if (risk <= 30) return 'low';
  if (risk <= 60) return 'medium';
  return 'high';
}

const restart = () => location.reload();

const editorOptions = {
  fontSize: 15,
  fontFamily: 'Fira Code, monospace',
  automaticLayout: true,
  minimap: { enabled: false },
  padding: { top: 20, bottom: 20 }
};

// 버그 애니메이션 함수
function animateBug(bugIndex) {
  const time = Date.now() / 1000;

  // 전체 화면을 부드럽게 돌아다니도록 노이즈 섞인 움직임 구현
  const movementRadiusX = 30;
  const movementRadiusY = 30;
  const centerX = 50;
  const centerY = 50;

  const x = centerX + Math.sin(time * 0.5 + bugIndex * 10) * movementRadiusX + Math.cos(time * 0.3) * 5;
  const y = centerY + Math.cos(time * 0.4 + bugIndex * 7) * movementRadiusY + Math.sin(time * 0.6) * 5;

  bugPositions[bugIndex] = {
    left: `${x}%`,
    top: `${y}%`
  };

  bugAnimationIds[bugIndex] = requestAnimationFrame(() => animateBug(bugIndex));
}

// 버그 애니메이션 시작
function startBugAnimations() {
  const bugsToAnimate = remainingBugs.value;
  bugsToAnimate.forEach(bugIndex => {
    if (!bugAnimationIds[bugIndex]) {
      animateBug(bugIndex);
    }
  });
}

// 버그 애니메이션 중지
function stopBugAnimations() {
  for (let i = 1; i <= 3; i++) {
    if (bugAnimationIds[i]) {
      cancelAnimationFrame(bugAnimationIds[i]);
      bugAnimationIds[i] = null;
    }
  }
}

// 해골이 버그로 날아가는 애니메이션
function animateSkullToBug() {
  const bugs = remainingBugs.value;
  if (bugs.length === 0) return;

  // 첫 번째 버그 위치로 해골 이동
  const targetBugIndex = bugs[0];
  const targetPos = bugPositions[targetBugIndex];

  // 시작 위치 (화면 중앙 하단)
  flyingSkullPosition.x = 50;
  flyingSkullPosition.y = 90;
  showFlyingSkull.value = true;

  const targetX = parseFloat(targetPos.left);
  const targetY = parseFloat(targetPos.top);

  const duration = 800;
  const startTime = performance.now();
  const startX = flyingSkullPosition.x;
  const startY = flyingSkullPosition.y;

  function animate(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const easeProgress = 1 - Math.pow(1 - progress, 3);

    flyingSkullPosition.x = startX + (targetX - startX) * easeProgress;
    flyingSkullPosition.y = startY + (targetY - startY) * easeProgress;

    if (progress < 1) {
      requestAnimationFrame(animate);
    } else {
      // 해골이 버그에 도달하면 버그를 죽임
      killedBugs.value.push(currentStep.value + '-' + targetBugIndex);

      // 해당 버그 애니메이션 중지
      if (bugAnimationIds[targetBugIndex]) {
        cancelAnimationFrame(bugAnimationIds[targetBugIndex]);
        bugAnimationIds[targetBugIndex] = null;
      }

      // 해골 숨기기
      setTimeout(() => {
        showFlyingSkull.value = false;
      }, 500);
    }
  }

  requestAnimationFrame(animate);
}

// 특정 버그를 저격하는 함수
function shootBugAtIndex(bugIndex, isHit) {
  const editorOverlay = document.querySelector('.ac-editor-overlay');
  if (!editorOverlay) return;

  const rect = editorOverlay.getBoundingClientRect();

  // 시작 위치 (화면 중앙 하단)
  const startX = rect.width / 2;
  const startY = rect.height - 50;

  // 지정된 버그 위치 계산
  const bugLeft = parseFloat(bugPositions[bugIndex].left);
  const bugTop = parseFloat(bugPositions[bugIndex].top);

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
        if (bugAnimationIds[bugIndex]) {
          cancelAnimationFrame(bugAnimationIds[bugIndex]);
          bugAnimationIds[bugIndex] = null;
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

// 저격 애니메이션 (첫 번째 버그 대상)
function shootBug(isHit) {
  const bugs = remainingBugs.value;
  if (bugs.length === 0) return;

  const targetBugIndex = bugs[0];
  shootBugAtIndex(targetBugIndex, isHit);
}

onMounted(() => {
  type(scenarioData.scenario.prologue);
});

onUnmounted(() => {
  stopBugAnimations();
});
</script>

<style scoped>
/* 동물의 숲 스타일 오피스 배경 */
.ac-stage {
  width: 100%;
  height: 100vh;
  position: relative;
  overflow: hidden;
  background-image: v-bind(mainBackground);
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
}

.ac-bg-layer {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.1);
}

/* 캐릭터 좌우 배치 */
.ac-char-zone {
  position: absolute;
  bottom: 15%;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 5;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.ac-char-zone.left {
  left: 15%;
  transform: translateX(0) scaleX(1);
}

.ac-char-zone.right {
  right: 15%;
  transform: translateX(0) scaleX(-1);
}

.ac-char-img {
  width: 500px;
  filter: drop-shadow(0 20px 30px rgba(0,0,0,0.15));
  transition: transform 0.3s ease;
}

.talking {
  animation: ac-hop 0.4s ease-in-out infinite;
}

@keyframes ac-hop {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}

/* 감정 이모지 */
.emotion-bubble {
  position: absolute;
  top: 10%;
  right: 10%;
  font-size: 80px;
  animation: emotion-pop 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
}

@keyframes emotion-pop {
  0% { transform: scale(0) rotate(-30deg); opacity: 0; }
  50% { transform: scale(1.3) rotate(10deg); }
  100% { transform: scale(1) rotate(0); opacity: 1; }
}

/* 캐릭터 전환 애니메이션 */
.char-slide-enter-active,
.char-slide-leave-active {
  transition: all 0.4s ease;
}

.char-slide-enter-from {
  opacity: 0;
  transform: translateY(50px) scale(0.8);
}

.char-slide-leave-to {
  opacity: 0;
  transform: translateY(-30px) scale(0.9);
}

/* 대화 인터페이스 */
.ac-ui-layer {
  position: absolute;
  bottom: 40px;
  width: 100%;
  display: flex;
  justify-content: center;
  z-index: 10;
}

.ac-bubble-wrap {
  width: 90%;
  max-width: 1200px;
  position: relative;
}

.ac-name-tag {
  position: absolute;
  top: -25px;
  left: 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 10px 32px;
  border-radius: 30px;
  font-size: 18px;
  font-weight: 900;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
  z-index: 15;
  letter-spacing: 1px;
}

.ac-bubble-body {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 50px;
  padding: 35px 55px;
  min-height: 140px;
  border: 8px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15), inset 0 1px 0 rgba(255,255,255,0.8);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  transition: transform 0.2s ease;
}

.ac-bubble-body:hover {
  transform: translateY(-2px);
  box-shadow: 0 25px 70px rgba(0, 0, 0, 0.2);
}

.ac-text-box {
  font-size: 22px;
  font-weight: 700;
  color: #2c3e50;
  text-align: left;
  line-height: 1.6;
}

.ac-next-nav {
  position: absolute;
  top: 50%;
  right: 30px;
  transform: translateY(-50%);
  color: #667eea;
  font-size: 32px;
  animation: bounce-right 0.8s ease-in-out infinite;
}

@keyframes bounce-right {
  0%, 100% { transform: translateY(-50%) translateX(0); }
  50% { transform: translateY(-50%) translateX(12px); }
}

/* 오피스 책상 스타일 에디터 */
.ac-editor-overlay {
  position: fixed;
  inset: 0;
  background-image: v-bind(editorBackground);
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.ac-editor-overlay::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(44, 62, 80, 0.85) 0%, rgba(52, 73, 94, 0.85) 100%);
  z-index: -1;
}

.office-desk-container {
  width: 100%;
  max-width: 1600px;
  height: 95vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, rgba(58, 74, 90, 0.95) 0%, rgba(44, 53, 64, 0.95) 100%);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  backdrop-filter: blur(5px);
}

/* 헤더 */
.desk-header {
  background: linear-gradient(135deg, #1e2a38 0%, #2c3e50 100%);
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid rgba(255, 255, 255, 0.1);
}

.step-indicator {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.close-btn {
  background: rgba(231, 76, 60, 0.9);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.close-btn:hover {
  background: #e74c3c;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.4);
}

/* 헤더 버튼 그룹 */
.header-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.header-buttons .btn-reset,
.header-buttons .btn-submit,
.header-buttons .close-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.header-buttons .btn-reset {
  background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
  color: white;
}

.header-buttons .btn-reset:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(149, 165, 166, 0.3);
}

.header-buttons .btn-submit {
  background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
  color: white;
}

.header-buttons .btn-submit:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(39, 174, 96, 0.3);
}

.header-buttons .close-btn {
  background: rgba(231, 76, 60, 0.9);
}

.header-buttons .close-btn:hover {
  background: #e74c3c;
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(231, 76, 60, 0.3);
}

/* 작업 공간 */
.desk-workspace {
  flex: 1;
  display: flex;
  gap: 30px;
  padding: 30px;
  overflow: hidden;
}

/* 왼쪽 메모보드 */
.memo-board {
  width: 420px;
  display: flex;
  flex-direction: column;
}

.memo-board-frame {
  flex: 1;
  background: linear-gradient(135deg, #f9e8d3 0%, #f5e0c3 100%);
  border-radius: 12px;
  padding: 25px;
  box-shadow:
    0 10px 30px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.5);
  position: relative;
  border: 8px solid #8b6f47;
  overflow-y: auto;
}

.memo-pin {
  position: absolute;
  top: -5px;
  font-size: 24px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.memo-pin.top-left {
  left: 20px;
}

.memo-pin.top-right {
  right: 20px;
}

.memo-content {
  margin-top: 10px;
}

.memo-header {
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px dashed #d4a574;
}

.bug-badge {
  display: inline-block;
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(231, 76, 60, 0.3);
}

.memo-title {
  font-size: 22px;
  font-weight: 800;
  color: #2c1810;
  line-height: 1.4;
  margin: 10px 0;
}

.memo-body {
  margin-bottom: 20px;
}

.memo-section {
  margin-bottom: 20px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
  border-left: 4px solid #f39c12;
}

.memo-label {
  font-size: 14px;
  font-weight: 700;
  color: #d35400;
  margin-bottom: 8px;
}

.memo-section p {
  font-size: 15px;
  line-height: 1.6;
  color: #34495e;
  margin: 0;
  white-space: pre-line;
}

.hint-section {
  margin-top: 20px;
}

.btn-hint {
  width: 100%;
  background: linear-gradient(135deg, #f1c40f 0%, #f39c12 100%);
  border: none;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 700;
  color: #2c1810;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(241, 196, 15, 0.3);
}

.btn-hint:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(241, 196, 15, 0.4);
}

.hint-box {
  margin-top: 15px;
  padding: 15px;
  background: rgba(52, 152, 219, 0.1);
  border: 2px solid #3498db;
  border-radius: 10px;
  position: relative;
}

.hint-icon {
  position: absolute;
  top: -12px;
  left: 15px;
  background: #3498db;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 18px;
}

.hint-box p {
  font-size: 14px;
  line-height: 1.6;
  color: #2c3e50;
  margin: 8px 0 0 0;
}

/* 오른쪽 모니터 */
.monitor-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.monitor-frame {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.monitor-bezel {
  flex: 1;
  width: 100%;
  background: #1a1a1a;
  border-radius: 12px;
  padding: 20px;
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  border: 15px solid #2c2c2c;
}

.monitor-screen-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #1e1e1e;
  border-radius: 4px;
  overflow: hidden;
}

.code-editor-section {
  flex: 1;
  min-height: 0;
}

.terminal-section {
  height: 200px;
  border-top: 1px solid #3a3a3a;
  display: flex;
  flex-direction: column;
  background: #0a0a0a;
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 15px;
  background: #1a1a1a;
  border-bottom: 1px solid #333;
}

.terminal-title {
  font-size: 12px;
  font-weight: 700;
  color: #4ec9b0;
  font-family: 'Consolas', 'Monaco', monospace;
}

.terminal-clear {
  background: #2d2d2d;
  border: none;
  color: #999;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Consolas', 'Monaco', monospace;
}

.terminal-clear:hover {
  background: #3a3a3a;
  color: #fff;
}

.terminal-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px 15px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #d4d4d4;
}

.terminal-empty {
  color: #666;
  font-style: italic;
}

.terminal-line {
  margin-bottom: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.terminal-prefix {
  margin-right: 8px;
  font-weight: 700;
}

.terminal-line.info .terminal-prefix {
  color: #4fc1ff;
}

.terminal-line.success .terminal-prefix {
  color: #4ec9b0;
}

.terminal-line.error .terminal-prefix {
  color: #f48771;
}

.terminal-line.warning .terminal-prefix {
  color: #dcdcaa;
}

.terminal-line.info .terminal-message {
  color: #d4d4d4;
}

.terminal-line.success .terminal-message {
  color: #4ec9b0;
}

.terminal-line.error .terminal-message {
  color: #f48771;
}

.terminal-line.warning .terminal-message {
  color: #dcdcaa;
}

.terminal-content::-webkit-scrollbar {
  width: 10px;
}

.terminal-content::-webkit-scrollbar-track {
  background: #0a0a0a;
}

.terminal-content::-webkit-scrollbar-thumb {
  background: #3a3a3a;
  border-radius: 5px;
}

.terminal-content::-webkit-scrollbar-thumb:hover {
  background: #4a4a4a;
}

.monitor-stand {
  width: 200px;
  height: 30px;
  background: linear-gradient(135deg, #3c3c3c 0%, #2c2c2c 100%);
  margin-top: 10px;
  border-radius: 0 0 20px 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

/* 하단 액션 */
.desk-actions {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 2px solid rgba(255, 255, 255, 0.1);
}

.status-message {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #ecf0f1;
}

.status-icon {
  font-size: 24px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
}

.action-buttons {
  display: flex;
  gap: 15px;
}

.btn-reset,
.btn-submit {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 30px;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn-reset {
  background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
  color: white;
}

.btn-reset:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(149, 165, 166, 0.4);
}

.btn-submit {
  background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
  color: white;
}

.btn-submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(39, 174, 96, 0.4);
}

/* Fade transition */
.fade-enter-active, .fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 설명 입력 인터페이스 */
/* 디버깅 전략 보고서 (회사 서류 스타일) */
.explain-overlay {
  position: fixed;
  inset: 0;
  background: #eceff1;
  z-index: 150;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow-y: auto;
  padding: 40px 20px;
}

.explain-document {
  background: white;
  max-width: 900px;
  width: 100%;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  border: 2px solid #dee2e6;
  animation: doc-slide-in 0.3s ease-out;
}

@keyframes doc-slide-in {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.doc-header {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  color: white;
  padding: 30px 40px;
  border-bottom: 4px solid #3498db;
  position: relative;
}

.doc-title {
  font-size: 28px;
  font-weight: 800;
  margin: 0;
  letter-spacing: 0.5px;
}

.doc-number {
  position: absolute;
  top: 30px;
  right: 40px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 600;
}

.doc-info-section {
  padding: 25px 40px;
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.doc-info-table {
  width: 100%;
  border-collapse: collapse;
}

.doc-info-table th {
  background: #e9ecef;
  padding: 12px 15px;
  text-align: left;
  font-weight: 700;
  font-size: 14px;
  color: #495057;
  border: 1px solid #dee2e6;
  width: 15%;
}

.doc-info-table td {
  padding: 12px 15px;
  border: 1px solid #dee2e6;
  font-size: 14px;
  color: #212529;
  background: white;
}

.doc-content-section {
  padding: 30px 40px;
}

.doc-section-title {
  font-size: 18px;
  font-weight: 800;
  color: #2c3e50;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #3498db;
}

.doc-field-label {
  font-size: 14px;
  color: #6c757d;
  margin-bottom: 10px;
  font-weight: 500;
}

.doc-textarea {
  width: 100%;
  min-height: 200px;
  padding: 15px;
  border: 2px solid #ced4da;
  font-size: 15px;
  font-family: inherit;
  line-height: 1.8;
  resize: vertical;
  transition: border-color 0.2s;
  background: #f8f9fa;
  color: #212529;
}

.doc-textarea:focus {
  outline: none;
  border-color: #3498db;
  background: white;
}

.char-count-doc {
  text-align: right;
  font-size: 12px;
  color: #adb5bd;
  margin-top: 8px;
}

.doc-footer {
  padding: 25px 40px;
  background: #f8f9fa;
  border-top: 1px solid #dee2e6;
  text-align: right;
}

.btn-submit-doc {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  border: none;
  padding: 12px 35px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.btn-submit-doc:hover:not(:disabled) {
  background: linear-gradient(135deg, #2980b9 0%, #2471a3 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.4);
}

.btn-submit-doc:disabled {
  background: #adb5bd;
  cursor: not-allowed;
  box-shadow: none;
}

/* 인사평가 리포트 (회사 평가지 스타일) */
.ac-result-screen {
  position: fixed;
  inset: 0;
  background: #eceff1;
  z-index: 200;
  overflow-y: auto;
  padding: 30px 15px;
}

.kpi-report-card {
  background: #fff;
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-height: auto;
}

/* 문서 헤더 */
.report-header {
  padding: 40px 50px 30px;
  border-bottom: 3px double #333;
  background: #fff;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ddd;
}

.company-info {
  text-align: left;
}

.company-logo-text {
  font-size: 22px;
  font-weight: 900;
  color: #1a237e;
  margin-bottom: 5px;
}

.company-dept {
  font-size: 14px;
  color: #666;
}

.doc-info {
  text-align: right;
}

.doc-number,
.doc-date {
  font-size: 13px;
  color: #555;
  margin-bottom: 3px;
}

.report-title {
  font-size: 32px;
  font-weight: 900;
  text-align: center;
  margin: 20px 0;
  color: #1a237e;
  letter-spacing: 8px;
}

.eval-period {
  text-align: center;
  font-size: 14px;
  color: #666;
}

/* 피평가자 정보 테이블 */
.eval-info-section {
  padding: 30px 50px;
  background: #fafafa;
}

.info-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border: 2px solid #333;
}

.info-table th,
.info-table td {
  padding: 12px 15px;
  border: 1px solid #999;
  font-size: 15px;
}

.info-table th {
  background: #e8eaf6;
  font-weight: 700;
  color: #1a237e;
  width: 20%;
  text-align: center;
}

.info-table td {
  background: #fff;
  color: #333;
}

/* 평가 항목 섹션 */
.eval-items-section {
  padding: 30px 50px;
}

.eval-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
  border: 2px solid #333;
}

.eval-table thead th {
  background: #1a237e;
  color: white;
  padding: 12px;
  font-weight: 700;
  font-size: 14px;
  border: 1px solid #333;
}

.eval-table tbody td {
  padding: 15px 12px;
  border: 1px solid #999;
  font-size: 14px;
}

.eval-table .item-name {
  font-weight: 700;
  color: #1a237e;
  text-align: center;
}

.eval-table tbody td {
  text-align: center;
}

.score-cell {
  font-weight: 900;
  color: #1976d2;
  font-size: 16px;
}

.desc-cell {
  text-align: left !important;
  padding: 10px 15px;
}

.progress-bar-mini {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #1976d2 0%, #42a5f5 100%);
  transition: width 1s ease;
}

.score-detail {
  font-size: 12px;
  color: #666;
}

.total-row {
  background: #f5f5f5;
  font-weight: 700;
}

.total-row td {
  font-size: 16px;
  padding: 15px;
}

.total-score {
  color: #1976d2;
  font-size: 20px !important;
  font-weight: 900;
}

/* 섹션 공통 스타일 */
.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #1a237e;
  margin-bottom: 15px;
  padding-left: 5px;
}

/* 종합 평가 등급 */
.eval-grade-section {
  padding: 30px 50px;
  background: #fafafa;
}

.grade-result-box {
  display: flex;
  gap: 40px;
  margin-top: 20px;
  padding: 30px;
  background: #fff;
  border: 2px solid #333;
}

.grade-info {
  flex: 1;
  text-align: center;
  border-right: 2px solid #ddd;
  padding-right: 40px;
}

.grade-label-text {
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
  font-weight: 600;
}

.grade-badge {
  width: 100px;
  height: 100px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 56px;
  font-weight: 900;
  border-radius: 50%;
  margin: 10px 0;
  border: 5px solid;
}

.grade-badge.grade-S {
  background: #fff3e0;
  color: #e65100;
  border-color: #e65100;
}

.grade-badge.grade-A {
  background: #e3f2fd;
  color: #0d47a1;
  border-color: #0d47a1;
}

.grade-badge.grade-B {
  background: #e8f5e9;
  color: #1b5e20;
  border-color: #1b5e20;
}

.grade-badge.grade-C {
  background: #f5f5f5;
  color: #616161;
  border-color: #616161;
}

.grade-description {
  font-size: 15px;
  color: #555;
  font-weight: 600;
  margin-top: 10px;
}

.salary-result {
  flex: 1;
  text-align: center;
  position: relative;
}

.salary-label-text {
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
  font-weight: 600;
}

.salary-value-box {
  display: inline-block;
  padding: 20px 40px;
  font-size: 28px;
  font-weight: 900;
  border-radius: 8px;
  margin: 10px 0;
}

.salary-value-box.positive {
  background: #e8f5e9;
  color: #2e7d32;
  border: 3px solid #2e7d32;
}

.salary-value-box.negative {
  background: #ffebee;
  color: #c62828;
  border: 3px solid #c62828;
}

.salary-value-box.neutral {
  background: #f5f5f5;
  color: #616161;
  border: 3px solid #9e9e9e;
}

.approval-stamp {
  position: absolute;
  right: -10px;
  top: 50%;
  transform: translateY(-50%) rotate(-15deg);
  animation: stamp-appear 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes stamp-appear {
  0% {
    transform: translateY(-50%) scale(0) rotate(-30deg);
    opacity: 0;
  }
  50% {
    transform: translateY(-50%) scale(1.2) rotate(5deg);
  }
  100% {
    transform: translateY(-50%) scale(1) rotate(-15deg);
    opacity: 1;
  }
}

/* 특별 성과 보너스 */
.bonus-section {
  padding: 30px 50px;
}

.bonus-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
  border: 2px solid #333;
}

.bonus-table thead th {
  background: #1a237e;
  color: white;
  padding: 12px;
  font-weight: 700;
  font-size: 14px;
  border: 1px solid #333;
  text-align: center;
}

.bonus-table tbody td {
  padding: 12px 15px;
  border: 1px solid #999;
  font-size: 14px;
  text-align: center;
}

.bonus-amount-cell {
  font-weight: 900;
  color: #f57c00;
  font-size: 16px;
}

/* 업무 수행 내역 */
.work-detail-section {
  padding: 30px 50px;
  background: #fafafa;
}

.work-item {
  margin-bottom: 20px;
  padding: 20px;
  background: #fff;
  border: 1px solid #ddd;
  border-left: 4px solid #1976d2;
}

.work-header {
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.work-num {
  font-weight: 900;
  color: #1976d2;
  margin-right: 8px;
  font-size: 16px;
}

.work-title {
  font-weight: 700;
  color: #333;
  font-size: 15px;
}

.work-content {
  padding: 10px 0;
}

.work-label {
  font-size: 13px;
  color: #666;
  font-weight: 600;
  margin-bottom: 8px;
}

.work-text {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  padding: 10px;
  background: #f9f9f9;
  border-left: 3px solid #ccc;
  white-space: pre-wrap;
}

/* 평가자 종합 의견 */
.evaluator-comment-section {
  padding: 30px 50px;
}

.comment-box {
  margin-top: 15px;
  padding: 25px;
  background: #fff;
  border: 2px solid #333;
  min-height: 120px;
  line-height: 1.8;
}

.comment-box p {
  font-size: 14px;
  color: #333;
  margin: 0;
  text-align: justify;
}

/* 서명란 */
.signature-section {
  padding: 40px 50px 30px;
  background: #fafafa;
}

.signature-box {
  display: flex;
  justify-content: space-around;
  margin-top: 30px;
  padding: 30px;
  background: #fff;
  border: 1px solid #ddd;
}

.signature-item {
  text-align: center;
  flex: 1;
}

.sig-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 15px;
  font-weight: 600;
}

.sig-name {
  font-size: 15px;
  color: #333;
  font-weight: 700;
  margin-bottom: 30px;
}

.sig-line {
  display: inline-block;
  padding: 8px 40px;
  border-bottom: 2px solid #333;
  color: #999;
  font-size: 13px;
}

/* AI 평가 섹션 */
.ai-evaluation-section {
  margin-top: 30px;
  padding: 25px 50px;
  border-top: 2px solid #e0e0e0;
  background: #fafafa;
}

.ai-loading {
  text-align: center;
  padding: 60px 20px;
}

.pulse-loader {
  width: 60px;
  height: 60px;
  margin: 0 auto 20px;
  border: 4px solid #e0e0e0;
  border-top-color: #1976d2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.ai-loading p {
  color: #666;
  font-size: 14px;
  margin-top: 15px;
}

.ai-result {
  margin-top: 20px;
}

.thinking-eval-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 25px;
}

.eval-card {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.eval-card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 15px;
}

.eval-icon {
  font-size: 20px;
}

.eval-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.eval-card-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.pass-badge {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 700;
}

.pass-badge.pass {
  background: #e8f5e9;
  color: #2e7d32;
  border: 2px solid #4caf50;
}

.pass-badge.fail {
  background: #ffebee;
  color: #c62828;
  border: 2px solid #f44336;
}

.risk-gauge {
  width: 100%;
  height: 20px;
  background: #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}

.risk-fill {
  height: 100%;
  transition: width 0.5s ease;
  border-radius: 10px;
}

.risk-fill.low {
  background: linear-gradient(90deg, #4caf50, #8bc34a);
}

.risk-fill.medium {
  background: linear-gradient(90deg, #ff9800, #ffb74d);
}

.risk-fill.high {
  background: linear-gradient(90deg, #f44336, #e57373);
}

.risk-value {
  font-size: 18px;
  font-weight: 700;
  color: #333;
}

.thinking-score-value {
  font-size: 32px;
  font-weight: 700;
  color: #1976d2;
}

.thinking-score-max {
  font-size: 18px;
  color: #666;
}

.summary-box {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 25px;
}

.summary-label {
  font-size: 16px;
  font-weight: 700;
  color: #333;
  margin-bottom: 12px;
}

.summary-text {
  font-size: 14px;
  line-height: 1.6;
  color: #555;
  margin: 0;
}

.step-feedbacks {
  margin-top: 25px;
}

.feedback-title {
  font-size: 16px;
  font-weight: 700;
  color: #333;
  margin-bottom: 15px;
}

.step-feedback-box {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
}

.step-feedback-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.step-feedback-header .step-num {
  background: #1976d2;
  color: white;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 700;
}

.step-feedback-header .step-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.step-feedback-content {
  margin-top: 10px;
}

.feedback-label {
  font-size: 13px;
  font-weight: 700;
  color: #1976d2;
  margin-bottom: 8px;
}

.feedback-text {
  font-size: 14px;
  line-height: 1.6;
  color: #555;
  margin: 0;
  white-space: pre-line;
}

/* 하단 액션 버튼 */
.report-actions {
  padding: 30px 50px 40px;
  text-align: center;
  border-top: 3px double #333;
  background: #fff;
}

.btn-restart {
  background: #1976d2;
  color: white;
  border: 2px solid #1565c0;
  padding: 15px 45px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 700;
  transition: all 0.3s;
  box-shadow: 0 4px 10px rgba(25, 118, 210, 0.3);
}

.btn-restart:hover {
  background: #1565c0;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(25, 118, 210, 0.4);
}

.ac-catch-effect { position: absolute; top: -50px; text-align: center; z-index: 10; animation: bounce-pop 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.catch-sparkle { font-size: 32px; font-weight: 900; color: #fff; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
.catch-item { font-size: 100px; filter: drop-shadow(0 10px 15px rgba(0,0,0,0.3)); }

@keyframes bounce-pop {
  0% { transform: scale(0) rotate(-20deg); }
  70% { transform: scale(1.2) rotate(10deg); }
  100% { transform: scale(1) rotate(0); }
}

@keyframes ac-hop { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-25px); } }

/* 버그 애니메이션 스타일 */
.bugs-container {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 50;
}

.flying-bug {
  position: absolute;
  font-size: 35px;
  transition: left 0.3s ease-out, top 0.3s ease-out;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
  animation: bug-float 2s ease-in-out infinite;
}

.flying-bug.dead {
  animation: bug-die 1s ease-out forwards;
}

.bug-emoji {
  display: block;
  animation: bug-wiggle 0.5s ease-in-out infinite alternate;
}

.flying-bug.dead .bug-emoji {
  animation: skull-spin 1s ease-out;
}

.eating-effect {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 5px;
}

.bite-mark {
  font-size: 20px;
  color: #ff6b6b;
  animation: bite 0.6s ease-in-out infinite;
  opacity: 0;
}

.bite-mark:nth-child(1) { animation-delay: 0s; }
.bite-mark:nth-child(2) { animation-delay: 0.2s; }
.bite-mark:nth-child(3) { animation-delay: 0.4s; }

/* 해골 날아가는 애니메이션 */
.flying-skull {
  position: fixed;
  font-size: 80px;
  z-index: 999;
  pointer-events: none;
  transition: left 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94),
              top 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  animation: skull-fly 0.8s ease-out;
  filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.5));
}

@keyframes bug-float {
  0%, 100% { transform: translateY(0) rotate(-5deg); }
  50% { transform: translateY(-10px) rotate(5deg); }
}

@keyframes bug-wiggle {
  0% { transform: rotate(-3deg); }
  100% { transform: rotate(3deg); }
}

@keyframes bite {
  0%, 100% { opacity: 0; transform: translateY(0) scale(1); }
  50% { opacity: 1; transform: translateY(-10px) scale(1.2); }
}

@keyframes bug-die {
  0% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
  50% {
    transform: scale(1.5) rotate(180deg);
  }
  100% {
    transform: scale(0) rotate(360deg);
    opacity: 0;
  }
}

@keyframes skull-spin {
  0% {
    transform: rotate(0deg) scale(1);
  }
  50% {
    transform: rotate(180deg) scale(1.2);
  }
  100% {
    transform: rotate(360deg) scale(1);
  }
}

@keyframes skull-fly {
  0% {
    transform: scale(0.5) rotate(-20deg);
    opacity: 0;
  }
  50% {
    transform: scale(1.3) rotate(10deg);
    opacity: 1;
  }
  100% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}

/* 화면 흔들림 효과 */
.shake-effect {
  animation: screenShake 0.5s ease-out;
}

@keyframes screenShake {
  0%, 100% { transform: translateX(0) rotate(0deg); }
  10% { transform: translateX(-5px) rotate(-0.5deg); }
  20% { transform: translateX(5px) rotate(0.5deg); }
  30% { transform: translateX(-5px) rotate(-0.5deg); }
  40% { transform: translateX(5px) rotate(0.5deg); }
  50% { transform: translateX(-3px) rotate(-0.3deg); }
  60% { transform: translateX(3px) rotate(0.3deg); }
  70% { transform: translateX(-2px) rotate(0deg); }
  80% { transform: translateX(2px) rotate(0deg); }
  90% { transform: translateX(-1px) rotate(0deg); }
}

/* 총알 애니메이션 */
.bullet {
  position: fixed;
  z-index: 999;
  pointer-events: none;
  font-size: 40px;
  filter: drop-shadow(0 0 10px rgba(255, 100, 0, 0.8));
  animation: bulletSpin 0.3s linear infinite;
}

@keyframes bulletSpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.bullet-trail {
  display: block;
}

/* HIT 이펙트 */
.hit-effect {
  position: fixed;
  z-index: 1000;
  pointer-events: none;
  text-align: center;
}

.hit-text {
  display: block;
  font-size: 48px;
  font-weight: 900;
  color: #ff0;
  text-shadow:
    0 0 10px rgba(255, 255, 0, 0.8),
    0 0 20px rgba(255, 100, 0, 0.6),
    2px 2px 4px rgba(0, 0, 0, 0.5);
  animation: hitTextPop 1.5s ease-out;
}

@keyframes hitTextPop {
  0% {
    transform: scale(0.5) rotate(-10deg);
    opacity: 1;
  }
  20% {
    transform: scale(1.3) rotate(5deg);
    opacity: 1;
  }
  100% {
    transform: scale(2) rotate(0deg);
    opacity: 0;
  }
}

.explosion-particles {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
}

.particle {
  position: absolute;
  width: 30px;
  height: 30px;
  background: radial-gradient(circle, #ff0 0%, #f80 50%, transparent 70%);
  border-radius: 50%;
  animation: explodeParticle 1s ease-out;
  transform-origin: center;
}

@keyframes explodeParticle {
  0% {
    transform: translate(0, 0) scale(1);
    opacity: 1;
  }
  100% {
    transform: translate(
      calc(cos(var(--angle)) * 100px),
      calc(sin(var(--angle)) * 100px)
    ) scale(0);
    opacity: 0;
  }
}

.explode-enter-active {
  animation: explodeIn 0.3s ease-out;
}

.explode-leave-active {
  animation: explodeOut 1.2s ease-out;
}

@keyframes explodeIn {
  from { transform: scale(0); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

@keyframes explodeOut {
  to { transform: scale(2); opacity: 0; }
}

/* MISS 이펙트 */
.miss-effect {
  position: fixed;
  z-index: 1000;
  pointer-events: none;
}

.miss-text {
  display: block;
  font-size: 40px;
  font-weight: 900;
  color: #f00;
  text-shadow:
    0 0 10px rgba(255, 0, 0, 0.8),
    0 0 20px rgba(255, 0, 0, 0.6),
    2px 2px 4px rgba(0, 0, 0, 0.5);
  animation: missTextFloat 1s ease-out;
}

@keyframes missTextFloat {
  0% {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
  100% {
    transform: translateY(-50px) scale(0.5);
    opacity: 0;
  }
}

.miss-enter-active,
.miss-leave-active {
  transition: all 1s ease-out;
}

.miss-enter-from {
  opacity: 0;
  transform: scale(0.5);
}

.miss-leave-to {
  opacity: 0;
  transform: translateY(-50px) scale(0.5);
}
</style>