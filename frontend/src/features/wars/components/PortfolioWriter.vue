<template>
  <div class="pw-root">
    <!-- 트리거 버튼 -->
    <button v-if="!isOpen" class="pw-trigger" @click="isOpen = true">
      <span class="pw-trigger-icon">✨</span>
      <span>AI 포트폴리오 글 생성</span>
      <span class="pw-trigger-badge">NEW</span>
    </button>

    <!-- 패널 -->
    <transition name="pw-slide">
      <div v-if="isOpen" class="pw-panel">

        <!-- 헤더 -->
        <div class="pw-panel-header">
          <div class="pw-panel-title">
            <span>✨</span> AI 포트폴리오 글 생성
          </div>
          <button class="pw-close" @click="isOpen = false">✕</button>
        </div>

        <!-- Step 1: 형식 선택 -->
        <div v-if="!generated && !loading" class="pw-intro">
          <p class="pw-intro-desc">
            이 경험을 바탕으로 <strong>LinkedIn 포스팅</strong>,
            <strong>포트폴리오 설명</strong>, <strong>이력서 한 줄</strong>을
            AI가 직접 써드려요.
          </p>
          <div class="pw-format-select">
            <div
              v-for="fmt in formats" :key="fmt.id"
              class="pw-fmt-card" :class="{ active: selectedFormats.includes(fmt.id) }"
              @click="toggleFormat(fmt.id)"
            >
              <span class="pw-fmt-icon">{{ fmt.icon }}</span>
              <div class="pw-fmt-info">
                <div class="pw-fmt-label">{{ fmt.label }}</div>
                <div class="pw-fmt-desc">{{ fmt.desc }}</div>
              </div>
              <span class="pw-fmt-check">{{ selectedFormats.includes(fmt.id) ? '✅' : '⬜' }}</span>
            </div>
          </div>
          <button class="pw-gen-btn" :disabled="selectedFormats.length === 0" @click="generate">
            🚀 글 생성하기
          </button>
        </div>

        <!-- 로딩 -->
        <div v-if="loading" class="pw-loading">
          <div class="pw-spinner"></div>
          <p class="pw-loading-text">AI가 포트폴리오 글을 작성 중...</p>
          <p class="pw-loading-sub">게임 경험을 분석해서 멋진 글로 만들고 있어요 ✍️</p>
        </div>

        <!-- 결과 -->
        <div v-if="generated && !loading" class="pw-results">
          <div class="pw-tabs">
            <button
              v-for="tab in resultTabs" :key="tab.id"
              class="pw-tab" :class="{ active: activeTab === tab.id }"
              @click="activeTab = tab.id"
            >{{ tab.icon }} {{ tab.label }}</button>
          </div>

          <div class="pw-content-area">
            <div v-for="tab in resultTabs" :key="tab.id" v-show="activeTab === tab.id">
              <div class="pw-content-box">
                <pre class="pw-content-text">{{ results[tab.id] }}</pre>
              </div>
              <div class="pw-content-actions">
                <button class="pw-copy-btn" @click="copyText(tab.id)">
                  {{ copiedTab === tab.id ? '✅ 복사됨!' : '📋 복사' }}
                </button>
                <button class="pw-regen-btn" @click="regenOne(tab.id)" :disabled="regenLoading === tab.id">
                  {{ regenLoading === tab.id ? '✍️...' : '🔄 다시 쓰기' }}
                </button>
              </div>
            </div>
          </div>

          <div class="pw-footer">
            <button class="pw-reset-btn" @click="reset">← 다시 설정</button>
            <button class="pw-all-copy-btn" @click="copyAll">📦 전체 복사</button>
          </div>
        </div>

        <!-- 에러 -->
        <div v-if="error" class="pw-error">
          ⚠️ {{ error }}
          <button @click="error = ''; generated = false; loading = false">다시 시도</button>
        </div>

      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  gameType:      { type: String,  required: true },   // 'arch' | 'logic'
  scenario:      { type: String,  default: '' },
  missionTitle:  { type: String,  default: '' },
  myScore:       { type: Number,  default: 0 },
  opponentScore: { type: Number,  default: 0 },
  resultText:    { type: String,  default: '' },
  grade:         { type: String,  default: '' },
  aiReview:      { type: String,  default: '' },
  // Arch 전용
  components:    { type: Array,   default: () => [] },
  arrowCount:    { type: Number,  default: 0 },
  // Logic 전용
  pseudocode:    { type: String,  default: '' },
  phase1Score:   { type: Number,  default: 0 },
  phase2Score:   { type: Number,  default: 0 },
  strengths:     { type: Array,   default: () => [] },
  weaknesses:    { type: Array,   default: () => [] },
})

// ─── 상태 ───────────────────────────────────────────────
const isOpen      = ref(false)
const loading     = ref(false)
const generated   = ref(false)
const error       = ref('')
const results     = ref({})
const activeTab   = ref('linkedin')
const copiedTab   = ref('')
const regenLoading = ref('')

const formats = [
  { id: 'linkedin',  icon: '💼', label: 'LinkedIn',     desc: '200~300자 감성 포스팅 + 해시태그' },
  { id: 'portfolio', icon: '📂', label: '포트폴리오',   desc: '기술 중심 프로젝트 설명 3~5문장' },
  { id: 'resume',    icon: '📄', label: '이력서',       desc: '이력서용 bullet point 1~2줄' },
]

const selectedFormats = ref(['linkedin', 'portfolio', 'resume'])
const resultTabs = computed(() => formats.filter(f => selectedFormats.value.includes(f.id)))

function toggleFormat(id) {
  if (selectedFormats.value.includes(id)) {
    if (selectedFormats.value.length > 1) {
      selectedFormats.value = selectedFormats.value.filter(f => f !== id)
    }
  } else {
    selectedFormats.value.push(id)
  }
}

// ─── 게임 데이터 → 컨텍스트 텍스트 ─────────────────────
function buildContext() {
  if (props.gameType === 'arch') {
    const comps = props.components.map(c => (typeof c === 'string' ? c : c.name)).join(', ')
    return `
[게임] CoduckWars - 아키텍처 캐치마인드 (실시간 1vs1 시스템 설계 배틀)
[미션] ${props.missionTitle || props.scenario}
[시나리오] ${props.scenario}
[설계한 컴포넌트 ${props.components.length}개] ${comps}
[연결 화살표] ${props.arrowCount}개
[점수] 내 ${props.myScore}pt vs 상대 ${props.opponentScore}pt
[결과] ${props.resultText} | 등급 ${props.grade}
${props.aiReview ? '[AI 평가] ' + props.aiReview : ''}`.trim()
  } else {
    return `
[게임] CoduckWars - 로직 런 (실시간 1vs1 의사코드 설계 배틀)
[시나리오] ${props.scenario}
[내가 작성한 의사코드]
${props.pseudocode ? props.pseudocode.slice(0, 400) : '(없음)'}
[점수] Phase1 ${props.phase1Score}pt + Phase2 ${props.phase2Score}pt = 총 ${props.myScore}pt
[등급] ${props.grade}
${props.strengths.length  ? '[강점] '   + props.strengths.join(', ')  : ''}
${props.weaknesses.length ? '[개선점] ' + props.weaknesses.join(', ') : ''}
${props.aiReview ? '[AI 피드백] ' + props.aiReview : ''}`.trim()
  }
}

// ─── 포맷별 프롬프트 ─────────────────────────────────────
function getPrompt(formatId) {
  const ctx = buildContext()
  const gameName = props.gameType === 'arch' ? '아키텍처 캐치마인드' : '로직 런'

  const base = `당신은 실무 경험을 바탕으로 IT 개발자의 이력서와 포트폴리오 작성을 돕는 전문 커리어 코치입니다.
아래의 데이터는 지원자가 "제한 시간 내 압박 상황에서 시스템 시나리오를 분석하고 최적의 아키텍처/논리(의사코드)를 설계하는 훈련 과정"을 거친 기록입니다.

${ctx}

`

  const instructions = {
    linkedin: base + `이 경험을 바탕으로 LinkedIn에 올릴 한국어 포스팅을 작성해주세요.

요구사항:
- 200~300자 내외
- "CoduckWars", "미니게임", "1620pt", "등급", "배틀" 같은 게임 용어나 수치는 절대 사용 금지.
- 대신 "실시간 시스템 아키텍처 설계 훈련", "제한 시간 내 비즈니스 로직(의사코드) 구조화 챌린지" 등의 전문적인 용어로 포장할 것.
- 어떤 시나리오(문제)가 주어졌고, 이를 해결하기 위해 어떤 논리적 사고 과정을 거쳤는지를 중심으로 작성.
- 기술 내용은 비개발자도 맥락을 이해할 수 있게 쉽게 풀어서 설명.
- 이모지 3~5개 적절히 사용.
- 마지막에 해시태그 4~5개 (#개발 #아키텍처설계 #문제해결 #백엔드 등).`,

    portfolio: base + `이 경험을 포트폴리오 "활동 / 경험" 섹션 설명으로 작성해주세요.

요구사항:
- [핵심 경험]: "실시간 시스템 시나리오 기반 아키텍처/논리 설계 훈련"으로 명시.
- [문제 해결 과정]: 주어진 시나리오를 분석하여 어떻게 구조화/의사코드를 작성했는지 2문장.
- [습득 역량]: 코드 리뷰나 실시간 압박 수비(답변) 과정에서 배운 확장성/성능/보안 관련 역량 1~2문장.
- 총 4~6문장, 전문적이고 진지한 어조의 한국어.
- "게임", "합격", "점수", "등급" 절대 언급 금지.`,

    resume: base + `이 경험을 이력서의 활동 항목에 들어갈 bullet point로 작성해주세요.

요구사항:
- 정확히 1~2개의 bullet point만 작성 (• 기호 사용).
- "• [해결한 문제/시나리오]를 분석하여 [설계한 기술/컴포넌트/흐름]을 기반으로 시스템 아키텍처/비즈니스 로직을 설계함" 형식 유지.
- "게임", "점수", "등급", "pt" 절대 사용 금지!
- 50자 이내로 매우 간결하고 임팩트 있게.
- 전문적인 개발자 이력서에 들어갈 수 있는 진지한 한국어.
예시: • 대규모 트래픽 시나리오를 분석하고 로드밸런서와 읽기/쓰기 분리 DB 구조를 반영한 시스템 아키텍처 도출`,
  }

  return instructions[formatId]
}

// ─── API 호출 ─────────────────────────────────────────────
async function callAI(formatId) {
  // [수정일: 2026-02-27] 백엔드 URL 패턴 불일치 (404 에러) 해결을 위해 /api/core/ai-proxy/ 로 엔드포인트 수정
  const res = await fetch('/api/core/ai-proxy/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      max_tokens: 700,
      temperature: 0.88,
      messages: [
        { role: 'system', content: getPrompt(formatId) },
        { role: 'user',   content: '위 데이터를 바탕으로 요청한 형식의 글을 작성해주세요.' }
      ]
    })
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  if (data.error) throw new Error(data.error)
  return data.content
}

// ─── 전체 생성 ───────────────────────────────────────────
async function generate() {
  loading.value  = true
  error.value    = ''
  results.value  = {}

  try {
    await Promise.all(
      selectedFormats.value.map(async fmtId => {
        const text = await callAI(fmtId)
        results.value[fmtId] = text
      })
    )
    generated.value = true
    activeTab.value = selectedFormats.value[0]
  } catch (e) {
    error.value = 'AI 글 생성에 실패했어요. 잠시 후 다시 시도해주세요.'
  } finally {
    loading.value = false
  }
}

// ─── 개별 재생성 ─────────────────────────────────────────
async function regenOne(formatId) {
  regenLoading.value = formatId
  results.value[formatId] = '✍️ 다시 쓰는 중...'
  try {
    results.value[formatId] = await callAI(formatId)
  } catch {
    results.value[formatId] = '⚠️ 재생성 실패. 다시 시도해주세요.'
  } finally {
    regenLoading.value = ''
  }
}

// ─── 복사 ────────────────────────────────────────────────
function copyText(tabId) {
  const text = results.value[tabId] || ''
  navigator.clipboard.writeText(text).catch(() => {
    const ta = document.createElement('textarea')
    ta.value = text; document.body.appendChild(ta); ta.select()
    document.execCommand('copy'); document.body.removeChild(ta)
  })
  copiedTab.value = tabId
  setTimeout(() => { copiedTab.value = '' }, 2000)
}

function copyAll() {
  const all = resultTabs.value
    .map(t => `===== ${t.icon} ${t.label} =====\n${results.value[t.id] || ''}`)
    .join('\n\n')
  navigator.clipboard.writeText(all).catch(() => {
    const ta = document.createElement('textarea')
    ta.value = all; document.body.appendChild(ta); ta.select()
    document.execCommand('copy'); document.body.removeChild(ta)
  })
}

function reset() {
  generated.value = false
  results.value   = {}
  error.value     = ''
}
</script>

<style scoped>
/* ── 트리거 버튼 ── */
.pw-trigger {
  display: flex; align-items: center; justify-content: center; gap: .5rem;
  width: 100%; padding: .7rem 1.2rem;
  background: linear-gradient(135deg, rgba(168,85,247,.12), rgba(0,240,255,.07));
  border: 1.5px solid rgba(168,85,247,.35);
  border-radius: .65rem; color: #a855f7;
  font-size: .8rem; font-weight: 700; cursor: pointer;
  font-family: 'Orbitron', sans-serif; letter-spacing: 1px;
  transition: all .25s; margin: .6rem 0;
}
.pw-trigger:hover {
  background: linear-gradient(135deg, rgba(168,85,247,.22), rgba(0,240,255,.12));
  box-shadow: 0 0 20px rgba(168,85,247,.2); transform: translateY(-2px);
}
.pw-trigger-icon { font-size: 1.1rem; }
.pw-trigger-badge {
  font-size: .48rem; padding: 2px 6px; letter-spacing: 1px;
  background: #a855f7; color: #fff; border-radius: 3px;
}

/* ── 패널 ── */
.pw-panel {
  background: linear-gradient(135deg, #050b18, #080d1c);
  border: 1.5px solid rgba(168,85,247,.28);
  border-radius: 1rem; padding: 1.2rem;
  margin: .5rem 0;
  box-shadow: 0 4px 30px rgba(168,85,247,.08);
}
.pw-panel-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: .9rem;
}
.pw-panel-title {
  display: flex; align-items: center; gap: .4rem;
  font-family: 'Orbitron', sans-serif; font-size: .7rem;
  font-weight: 700; color: #a855f7; letter-spacing: 1.5px;
}
.pw-close {
  background: none; border: none; color: #334155;
  font-size: .85rem; cursor: pointer; padding: 3px 7px;
  border-radius: 4px; transition: all .15s;
}
.pw-close:hover { color: #64748b; background: rgba(255,255,255,.05); }

/* ── 인트로 ── */
.pw-intro-desc {
  font-size: .78rem; color: #64748b; line-height: 1.65;
  margin-bottom: .9rem;
}
.pw-intro-desc strong { color: #c084fc; }

.pw-format-select { display: flex; flex-direction: column; gap: .35rem; margin-bottom: .9rem; }
.pw-fmt-card {
  display: flex; align-items: center; gap: .6rem;
  padding: .55rem .75rem;
  background: rgba(255,255,255,.02); border: 1px solid rgba(255,255,255,.06);
  border-radius: .5rem; cursor: pointer; transition: all .18s;
}
.pw-fmt-card:hover { background: rgba(168,85,247,.07); border-color: rgba(168,85,247,.2); }
.pw-fmt-card.active {
  background: rgba(168,85,247,.1); border-color: rgba(168,85,247,.38);
}
.pw-fmt-icon { font-size: .95rem; flex-shrink: 0; }
.pw-fmt-info { flex: 1; }
.pw-fmt-label { font-size: .78rem; font-weight: 700; color: #94a3b8; }
.pw-fmt-desc  { font-size: .65rem; color: #475569; margin-top: 1px; }
.pw-fmt-check { font-size: .7rem; }

.pw-gen-btn {
  width: 100%; padding: .68rem;
  background: linear-gradient(135deg, rgba(168,85,247,.18), rgba(0,240,255,.08));
  border: 1.5px solid rgba(168,85,247,.45);
  border-radius: .6rem; color: #a855f7;
  font-size: .8rem; font-weight: 700; cursor: pointer;
  font-family: 'Orbitron', sans-serif; letter-spacing: 1px;
  transition: all .2s;
}
.pw-gen-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(168,85,247,.28), rgba(0,240,255,.12));
  box-shadow: 0 0 18px rgba(168,85,247,.22); transform: translateY(-1px);
}
.pw-gen-btn:disabled { opacity: .38; cursor: not-allowed; }

/* ── 로딩 ── */
.pw-loading {
  display: flex; flex-direction: column;
  align-items: center; gap: .65rem; padding: 1.5rem 0;
}
.pw-spinner {
  width: 30px; height: 30px;
  border: 3px solid rgba(168,85,247,.18); border-top-color: #a855f7;
  border-radius: 50%; animation: spin .75s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg) } }
.pw-loading-text { font-size: .82rem; color: #a855f7; font-weight: 600; }
.pw-loading-sub  { font-size: .7rem; color: #475569; }

/* ── 결과 ── */
.pw-tabs {
  display: flex; gap: .3rem; margin-bottom: .65rem;
}
.pw-tab {
  flex: 1; padding: .42rem;
  background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.07);
  border-radius: .4rem; color: #475569;
  font-size: .68rem; font-weight: 700; cursor: pointer;
  transition: all .15s; font-family: inherit;
}
.pw-tab.active {
  background: rgba(168,85,247,.12); border-color: rgba(168,85,247,.35);
  color: #c084fc;
}

.pw-content-box {
  background: #020810; border: 1px solid rgba(168,85,247,.13);
  border-radius: .5rem; padding: .85rem;
  max-height: 210px; overflow-y: auto; margin-bottom: .5rem;
}
.pw-content-box::-webkit-scrollbar { width: 4px; }
.pw-content-box::-webkit-scrollbar-thumb { background: rgba(168,85,247,.25); border-radius: 2px; }
.pw-content-text {
  font-family: 'Rajdhani', 'Space Grotesk', sans-serif;
  font-size: .78rem; color: #cbd5e1; line-height: 1.75;
  white-space: pre-wrap; word-break: break-word; margin: 0;
}

.pw-content-actions { display: flex; gap: .35rem; }
.pw-copy-btn, .pw-regen-btn {
  flex: 1; padding: .42rem; border-radius: .4rem;
  font-size: .7rem; font-weight: 700; cursor: pointer;
  font-family: inherit; transition: all .15s;
}
.pw-copy-btn {
  background: rgba(0,240,255,.07); border: 1px solid rgba(0,240,255,.22); color: #00f0ff;
}
.pw-copy-btn:hover { background: rgba(0,240,255,.14); }
.pw-regen-btn {
  background: rgba(100,116,139,.07); border: 1px solid rgba(100,116,139,.18); color: #64748b;
}
.pw-regen-btn:hover:not(:disabled) { background: rgba(100,116,139,.14); color: #94a3b8; }
.pw-regen-btn:disabled { opacity: .5; cursor: not-allowed; }

/* ── 푸터 ── */
.pw-footer {
  display: flex; gap: .35rem;
  padding-top: .7rem; border-top: 1px solid rgba(255,255,255,.04);
  margin-top: .7rem;
}
.pw-reset-btn {
  padding: .4rem .75rem; background: none;
  border: 1px solid rgba(100,116,139,.18); border-radius: .4rem;
  color: #475569; font-size: .7rem; cursor: pointer; font-family: inherit;
  transition: all .15s;
}
.pw-reset-btn:hover { color: #64748b; border-color: rgba(100,116,139,.3); }
.pw-all-copy-btn {
  flex: 1; padding: .4rem;
  background: rgba(168,85,247,.07); border: 1px solid rgba(168,85,247,.22);
  border-radius: .4rem; color: #a855f7;
  font-size: .7rem; font-weight: 700; cursor: pointer; font-family: inherit;
  transition: all .15s;
}
.pw-all-copy-btn:hover { background: rgba(168,85,247,.14); }

/* ── 에러 ── */
.pw-error {
  font-size: .76rem; color: #f87171;
  padding: .7rem; background: rgba(248,113,113,.06);
  border: 1px solid rgba(248,113,113,.18); border-radius: .5rem;
  display: flex; flex-direction: column; gap: .4rem; align-items: flex-start;
}
.pw-error button {
  font-size: .7rem; padding: .28rem .65rem;
  background: rgba(248,113,113,.1); border: 1px solid rgba(248,113,113,.25);
  border-radius: .35rem; color: #f87171; cursor: pointer; font-family: inherit;
}

/* ── 트랜지션 ── */
.pw-slide-enter-active, .pw-slide-leave-active { transition: all .28s ease; }
.pw-slide-enter-from, .pw-slide-leave-to { opacity: 0; transform: translateY(-6px); }
</style>
