<template>
  <div v-if="level" class="modal-overlay">
    <Confetti v-if="step === 6" :number-of-pieces="200" />

    <div class="modal-content v3-layout">
      <!-- Header -->
      <div class="v3-header">
        <div class="header-info">
          <span class="quest-label">QUEST LV.{{ level.id }}</span>
          <h1 class="quest-title">{{ level.title }}</h1>
        </div>

        <div class="step-indicator">
          <div
            v-for="s in 6"
            :key="s"
            :class="`step-dot ${s === step ? 'active' : ''} ${s < step ? 'completed' : ''}`"
          >
            {{ s }}
          </div>
        </div>

        <button class="close-btn" @click="() => setCurrentLevelId(null)">✕</button>
      </div>

      <!-- Body -->
      <div class="v3-body">
        <div class="v3-sidebar">
          <div class="duck-companion">
            <Duck />
            <div class="duck-bubble">
              <p>{{ duckMsg }}</p>
            </div>
          </div>
        </div>

        <div class="v3-main">
          <!-- Step 1: Scenario -->
          <div v-if="step === 1" class="step-content">
            <div class="scenario-card">
              <h3 class="section-title">📌 상황 (Scenario)</h3>
              <p class="section-text">{{ level.description }}</p>
            </div>

            <div class="specs-card">
              <h3 class="section-title">📥 입력 변수 & 제약 조건</h3>
              <pre class="code-block">{{ level.input_desc }}</pre>
              <ul class="constraints-list">
                <li v-for="(c, i) in level.constraints" :key="i">{{ c }}</li>
              </ul>
            </div>

            <div class="interaction-card">
              <h3 class="section-title">✍️ 자유 서술</h3>
              <p class="instruction-text">이 상황에서 알림을 보내야 하는 기준을 당신의 말로 정리해보세요.</p>
              <textarea
                v-model="freeInput"
                class="free-input"
                placeholder="예: 점검 중이면 무시하고, DB 에러면 무조건 보낸다..."
              ></textarea>
              <button class="next-btn" :disabled="freeInput.length < 5" @click="step++">
                다음 단계로 →
              </button>
            </div>
          </div>

          <!-- Step 2: Purpose -->
          <div v-if="step === 2" class="step-content centered-content">
            <div class="purpose-card">
              <h2>💡 이 문제의 핵심</h2>
              <div class="purpose-body">
                <p>이 문제는 <strong>조건을 나열하는 능력</strong>이 아니라,</p>
                <p class="highlight-text">"무엇을 먼저 쳐내야 하는가?" (Prioritization)</p>
                <p>를 보는 문제입니다.</p>
                <br />
                <p>불필요한 연산을 줄이는 <strong>Early Return</strong> 패턴을 익혀봅시다.</p>
              </div>
              <button class="next-btn" @click="step++">네, 알겠습니다.</button>
            </div>
          </div>

          <!-- Step 3: Quiz -->
          <div v-if="step === 3" class="step-content">
            <div class="quiz-card">
              <h3 class="quiz-question">Q. {{ level.quiz.question }}</h3>
              <div class="quiz-options">
                <div
                  v-for="opt in level.quiz.options"
                  :key="opt.id"
                  :class="`quiz-option ${selected === opt.id ? 'selected' : ''} ${
                    result === 'correct' && opt.id === level.quiz.answer ? 'correct' : ''
                  } ${result === 'wrong' && selected === opt.id ? 'wrong' : ''}`"
                  @click="!result && (selected = opt.id)"
                >
                  <span class="opt-id">{{ opt.id }}</span>
                  <span class="opt-text">{{ opt.text }}</span>
                </div>
              </div>

              <div v-if="result" :class="`quiz-feedback ${result}`">
                {{ result === 'correct' ? '✅ 정답입니다!' : '❌ 다시 생각해보세요.' }}
                <p>{{ level.quiz.explanation }}</p>
              </div>

              <button
                class="next-btn"
                :disabled="!selected"
                @click="result === 'correct' ? step++ : handleCheckAnswer()"
              >
                {{ result === 'correct' ? '다음 단계로 →' : '정답 확인' }}
              </button>
            </div>
          </div>

          <!-- Step 4: Pseudocode -->
          <div v-if="step === 4" class="step-content split-view">
            <div class="left-pane">
              <h3 class="section-title">📝 의사코드 요구사항</h3>
              <pre class="guide-block">{{ level.pseudocode_guide }}</pre>
            </div>
            <div class="right-pane">
              <div class="editor-wrapper">
                <div class="editor-header">solution.pseudo</div>
                <textarea
                  v-model="pseudoCode"
                  class="code-editor"
                  placeholder="// 여기에 의사코드를 작성하세요..."
                ></textarea>
              </div>
              <button class="next-btn" :disabled="pseudoCode.length < 10" @click="step++">
                파이썬 구현하러 가기 →
              </button>
            </div>
          </div>

          <!-- Step 5: Python -->
          <div v-if="step === 5" class="step-content split-view">
            <div class="left-pane">
              <h3 class="section-title">🐍 파이썬 구현</h3>
              <p>작성한 논리를 파이썬 문법으로 옮겨보세요.</p>
              <div class="hint-box">
                <p>Tip: 파이썬에서는 `else if` 대신 `elif`를 씁니다.</p>
                <p>Tip: 불리언 값은 `True`, `False` (대문자)입니다.</p>
              </div>
            </div>
            <div class="right-pane">
              <div class="editor-wrapper python-theme">
                <div class="editor-header">solution.py</div>
                <textarea
                  v-model="pyCode"
                  class="code-editor python"
                ></textarea>
              </div>
              <button class="next-btn" @click="step++">
                코드 제출 및 평가받기 →
              </button>
            </div>
          </div>

          <!-- Step 6: Evaluation -->
          <div v-if="step === 6" class="step-content">
            <div class="report-card">
              <div class="report-header">
                <h2>📄 근무 평가서 (Performance Review)</h2>
                <span class="report-date">{{ new Date().toLocaleDateString() }}</span>
              </div>

              <div class="eval-grid">
                <div v-for="(item, idx) in evaluatedMetrics" :key="idx" class="eval-item">
                  <div class="eval-top">
                    <span class="eval-label">{{ item.label }}</span>
                    <span :class="`traffic-light ${item.statusColor}`"></span>
                  </div>
                  <p class="eval-desc-llm">
                    🤖 {{ item.generatedText }}
                  </p>
                </div>
              </div>

              <div class="llm-summary-section">
                <h3>🤖 AI 총평</h3>
                <p class="llm-text">{{ overallReview }}</p>
              </div>

              <div class="improvement-section">
                <h3>🔧 보완 포인트: <span class="highlight">{{ improvementPoint }}</span></h3>

                <a
                  v-if="level.eval_rubric?.improvement_video"
                  :href="level.eval_rubric.improvement_video.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="video-recommendation"
                >
                  <div class="video-thumbnail">
                    <span>▶</span>
                  </div>
                  <div class="video-info">
                    <p class="video-label">추천 학습 영상</p>
                    <span class="video-title">
                      {{ level.eval_rubric.improvement_video.title }}
                    </span>
                  </div>
                </a>
              </div>

              <div class="report-footer-actions">
                <button class="btn-retry" @click="() => window.location.reload()">
                  다시 도전하기
                </button>
                <button class="next-btn final" @click="close">
                  확인서 서명 및 종료
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useGame } from '../composables/useGame'
import Duck from './Duck.vue'
import Confetti from '../components/Confetti.vue'
import '../styles/ProblemSolver.css'

const { levels, currentLevelId, setCurrentLevelId, completeLevel } = useGame()

const level = computed(() => levels.find(l => l.id === currentLevelId.value))

const step = ref(1)
const freeInput = ref('')
const pseudoCode = ref('')
const pyCode = ref('')
const selected = ref(null)
const result = ref(null)

watch(level, (newLevel) => {
  if (newLevel) {
    step.value = 1
    freeInput.value = ''
    pseudoCode.value = ''
    pyCode.value = newLevel.python_template || ''
    selected.value = null
    result.value = null
  }
})

const close = () => {
  if (step.value === 6) {
    completeLevel(level.value.id)
  }
  setCurrentLevelId(null)
}

const handleCheckAnswer = () => {
  if (selected.value === level.value.quiz.answer) {
    result.value = 'correct'
  } else {
    result.value = 'wrong'
  }
}

const evaluatedMetrics = computed(() => {
  if (!level.value?.eval_rubric?.metrics) return []

  const fullContext = pseudoCode.value + '\n' + pyCode.value

  return level.value.eval_rubric.metrics.map(metric => {
    const isPass = metric.regex.test(fullContext)
    return {
      ...metric,
      status: isPass ? 'pass' : 'fail',
      statusColor: isPass ? 'green' : 'red',
      generatedText: isPass ? metric.descriptions.pass : metric.descriptions.fail
    }
  })
})

const passedCount = computed(() => evaluatedMetrics.value.filter(m => m.status === 'pass').length)
const totalCount = computed(() => evaluatedMetrics.value.length)

const overallReview = computed(() => {
  if (passedCount.value === totalCount.value) {
    return "완벽합니다! 요구하신 모든 조건을 논리적으로 잘 처리하셨습니다. 특히 점검 모드를 가장 먼저 확인하는 'Early Return' 패턴을 잘 적용하여 서버 리소스를 효율적으로 아꼈습니다. 실무에서도 이 코드는 바로 사용할 수 있을 수준입니다."
  } else if (passedCount.value > 0) {
    return "핵심적인 로직은 잘 잡으셨지만, 일부 엣지 케이스(Edge Case) 처리가 아쉽습니다. 특히 비즈니스 중요도가 높은 DB 에러나 유지보수 모드에 대한 예외 처리를 조금 더 명확히 하면 훨씬 좋은 코드가 될 것입니다."
  } else {
    return "아직 논리 구조를 잡는 데 어려움이 있어 보입니다. 순차적으로 코드를 실행했을 때, 가장 먼저 걸러내야 할 조건이 무엇인지 다시 한 번 생각해보는 것이 좋겠습니다."
  }
})

const failedMetric = computed(() => evaluatedMetrics.value.find(m => m.status === 'fail'))

const improvementPoint = computed(() =>
  failedMetric.value ? failedMetric.value.label : '코드 가독성 및 주석'
)

const duckMsg = computed(() => {
  if (!level.value?.duck_script) return ''

  const messages = {
    1: level.value.duck_script.step1,
    2: level.value.duck_script.step2,
    3: level.value.duck_script.step3,
    4: level.value.duck_script.step4,
    5: level.value.duck_script.step5,
    6: level.value.duck_script.success
  }

  return messages[step.value] || level.value.duck_script.intro || ''
})
</script>

<style scoped>
@import '../styles/ProblemSolver.css';
</style>
