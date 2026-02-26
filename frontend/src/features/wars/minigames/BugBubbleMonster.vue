<template>
  <div class="bubble-game-container">
    <!-- 방 입장 화면 -->
    <div v-if="!bs.connected.value" class="join-screen">
      <h1>👾 Bug-Bubble Monster</h1>
      <p class="desc">방 번호를 입력하고 버그 대결장에 입장하세요!</p>
      <div class="join-box">
        <input
          v-model="inputRoomId"
          placeholder="방 번호 (예: room-123)"
          @keyup.enter="joinRoom"
        />
        <button class="join-btn" @click="joinRoom" :disabled="!inputRoomId.trim()">입장하기</button>
      </div>
      <button class="back-btn" @click="router.push('/practice/coduck-wars')">뒤로 가기</button>
    </div>

    <!-- 대기실 화면 -->
    <div v-else-if="!bs.isPlaying.value && !bs.gameOver.value" class="lobby-screen">
      <h1>👾 Bug-Bubble Monster</h1>
      <p class="desc">버그를 찾아 방울에 가두고 상대에게 날려라!</p>
      <div class="how-to-play">
        <div class="htp-item">
          <span class="htp-icon">🔍</span>
          <div><strong>버그 코드 발견</strong><p>화면에 등장하는 버그 코드를 분석하세요</p></div>
        </div>
        <div class="htp-item">
          <span class="htp-icon">✅</span>
          <div><strong>정답 선택</strong><p>4지선다 중 올바른 수정 코드를 고르세요</p></div>
        </div>
        <div class="htp-item">
          <span class="htp-icon">🫧</span>
          <div><strong>버블 전송</strong><p>정답을 맞히면 버그 방울이 상대에게 날아갑니다</p></div>
        </div>
        <div class="htp-item">
          <span class="htp-icon">💀</span>
          <div><strong>화면이 버그로 가득 차면 패배!</strong><p>{{ maxMonsters }}개 이상 쌓이기 전에 버블을 날리세요</p></div>
        </div>
      </div>
      <div class="players-box">
        <div class="player me">{{ auth.sessionNickname || '나' }}</div>
        <div class="vs">VS</div>
        <div class="player opponent">{{ bs.opponentName.value || '상대 대기 중...' }}</div>
      </div>
      <button class="start-btn" :disabled="!bs.isReady.value" @click="startGame">
        {{ bs.isReady.value ? '게임 시작!' : '상대방 대기 중...' }}
      </button>
    </div>

    <!-- 게임 결과 화면 -->
    <div v-else-if="bs.gameOver.value" class="result-screen">
      <h1 :class="{ win: isWinner, lose: !isWinner }">
        {{ isWinner ? '승리! 🏆' : '패배... 💀' }}
      </h1>
      <p>{{ isWinner ? '상대방의 화면이 버그로 가득 찼습니다!' : '나의 화면이 버그로 마비되었습니다.' }}</p>
      <div class="result-stats">
        <div class="stat-item">
          <span class="stat-label">맞힌 문제</span>
          <span class="stat-value">{{ totalSolved }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">최대 콤보</span>
          <span class="stat-value">{{ bestCombo }}x</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">상대에게 보낸 버블</span>
          <span class="stat-value">{{ totalBubblesSent }}</span>
        </div>
      </div>
      <button class="exit-btn" @click="router.push('/practice/coduck-wars')">로비로 돌아가기</button>
    </div>

    <!-- 플레이 화면 -->
    <div v-else class="play-screen">
      <!-- 헤더 -->
      <header class="game-header">
        <div class="player-panel me">
          <div class="avatar"><span>🦆</span></div>
          <div class="info">
            <span class="name">{{ auth.sessionNickname || '나' }}</span>
            <div class="monster-bar">
              <div class="monster-fill" :style="{ width: (activeMonsters.length / maxMonsters * 100) + '%' }"
                   :class="{ danger: activeMonsters.length > maxMonsters * 0.7 }"></div>
              <span class="monster-count">👾 {{ activeMonsters.length }} / {{ maxMonsters }}</span>
            </div>
          </div>
        </div>
        <div class="center-hud">
          <div class="vs-badge">⚡ VS ⚡</div>
          <div class="combo-display" v-if="combo > 0" :class="{ 'mega-combo': combo >= 3 }">
            COMBO x{{ combo }}
          </div>
          <div class="fever-ready" v-if="combo >= 3">🔥 FEVER READY!</div>
        </div>
        <div class="player-panel opp">
          <div class="info right">
            <span class="name">{{ bs.opponentName.value }}</span>
            <div class="monster-bar opp-bar">
              <div class="monster-fill opp-fill" :style="{ width: (opponentMonsterCount / maxMonsters * 100) + '%' }"
                   :class="{ danger: opponentMonsterCount > maxMonsters * 0.7 }"></div>
              <span class="monster-count">👾 {{ opponentMonsterCount }} / {{ maxMonsters }}</span>
            </div>
          </div>
          <div class="avatar opp-avatar"><span>🤖</span></div>
        </div>
      </header>

      <!-- 메인 게임 영역 -->
      <main class="battle-arena">
        <!-- 버그 문제 패널 -->
        <div class="problem-panel" :class="{ 'pulse-warning': activeMonsters.length > maxMonsters * 0.7 }">
          <div class="problem-header">
            <span class="problem-badge">🐛 BUG #{{ currentProblemIndex + 1 }}</span>
            <span class="bug-type-badge">{{ currentProblem?.bug_type_name || 'BUG' }}</span>
            <span class="file-name">{{ currentProblem?.file_name || 'unknown.py' }}</span>
          </div>

          <!-- 에러 로그 -->
          <div class="error-log" v-if="currentProblem?.error_log">
            <div class="log-label">📋 ERROR LOG</div>
            <pre>{{ currentProblem.error_log }}</pre>
          </div>

          <!-- 버그 코드 -->
          <div class="code-block">
            <div class="code-header">
              <span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span>
              <span class="code-title">{{ currentProblem?.file_name }}</span>
            </div>
            <div class="code-body">
              <div v-for="(line, idx) in buggyCodeLines" :key="idx"
                   class="code-line"
                   :class="{ 'bug-line': idx + 1 === currentProblem?.bug_line }">
                <span class="line-num">{{ idx + 1 }}</span>
                <span class="line-code" :class="{ 'highlight-bug': idx + 1 === currentProblem?.bug_line }">{{ line }}</span>
                <span class="bug-marker" v-if="idx + 1 === currentProblem?.bug_line">← BUG!</span>
              </div>
            </div>
          </div>

          <!-- 힌트 -->
          <div class="hint-bar" v-if="showHint">
            💡 {{ currentProblem?.hint }}
          </div>
          <button class="hint-btn" @click="showHint = !showHint" v-if="currentProblem?.hint">
            {{ showHint ? '힌트 숨기기' : '💡 힌트 보기' }}
          </button>
        </div>

        <!-- 선택지 패널 -->
        <div class="choices-panel">
          <div class="choices-title">올바른 수정 코드를 선택하세요</div>
          <div class="choices-grid">
            <button
              v-for="(choice, idx) in currentProblem?.choices"
              :key="idx"
              class="choice-btn"
              :class="getChoiceClass(idx)"
              @click="selectChoice(idx)"
              :disabled="answerState !== 'idle'"
            >
              <span class="choice-label">{{ ['A', 'B', 'C', 'D'][idx] }}</span>
              <code class="choice-code">{{ choice.label }}</code>
            </button>
          </div>

          <!-- 결과 피드백 -->
          <transition name="slide-up">
            <div class="answer-feedback" v-if="answerState !== 'idle'" :class="answerState">
              <span v-if="answerState === 'correct'">✅ 정답! 버그를 가두고 상대에게 날렸습니다! 🫧</span>
              <span v-else>❌ 오답! 버그가 내 화면으로 파고듭니다... 👾</span>
            </div>
          </transition>
        </div>
      </main>

      <!-- 버그 몬스터 오버레이 -->
      <div class="monster-overlay">
        <div
          v-for="m in activeMonsters"
          :key="m.id"
          class="monster bug"
          :style="{ left: m.x + 'px', top: m.y + 'px', fontSize: m.size + 'rem' }"
        >👾</div>

        <!-- 전송 중인 버블 -->
        <transition-group name="bubble-fly" tag="div">
          <div
            v-for="b in flyingBubbles"
            :key="b.id"
            class="flying-bubble"
            :style="{ left: b.x + 'px', top: b.y + 'px' }"
          >🫧<span class="inner-bug">👾</span></div>
        </transition-group>

        <!-- 콤보 팝업 -->
        <transition-group name="combo-pop" tag="div">
          <div v-for="p in comboPops" :key="p.id" class="combo-pop" :style="{ left: p.x + 'px', top: p.y + 'px' }">
            {{ p.text }}
          </div>
        </transition-group>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBubbleSocket } from '../composables/useBubbleSocket'
import { addBattleRecord } from '../useBattleRecord.js'

const router = useRouter()
const auth = useAuthStore()
const bs = useBubbleSocket()

// ── 방 상태 ──
const inputRoomId = ref('')
const currentRoomId = ref('')

// ── 게임 상태 ──
const activeMonsters = ref([])
const flyingBubbles = ref([])
const comboPops = ref([])
const maxMonsters = 25
const opponentMonsterCount = ref(0)
const isWinner = ref(false)
const combo = ref(0)
const bestCombo = ref(0)
const totalSolved = ref(0)
const totalBubblesSent = ref(0)
let flyBubbleId = 0
let combPopId = 0
let animFrameId = null

// ── 문제 상태 ──
const allProblems = ref([])
const currentProblemIndex = ref(0)
const answerState = ref('idle') // 'idle' | 'correct' | 'wrong'
const showHint = ref(false)
const selectedChoiceIdx = ref(-1)

const currentProblem = computed(() => allProblems.value[currentProblemIndex.value] || null)
const buggyCodeLines = computed(() => {
  if (!currentProblem.value?.buggy_code) return []
  return currentProblem.value.buggy_code.split('\n')
})

// ── 문제 데이터 로드 (Vite static import) ──
function loadProblems() {
  try {
    // Vite에서 JSON은 정적 import로 처리 (fetch('/src/...') 불가)
    const json = { progressiveProblems: [] }
    // progressive-problems.json을 동적 import로 로드
    import('@/features/practice/bughunt/problem_data/progressive-problems.json')
      .then(module => {
        const data = module.default
        const steps = []
        for (const group of data.progressiveProblems) {
          for (const step of group.steps || []) {
            if (step.fix_mode === 'choice' && step.choices?.length) {
              steps.push(step)
            }
          }
        }
        allProblems.value = steps.sort(() => Math.random() - 0.5)
        console.log(`[BugBubble] 문제 ${steps.length}개 로드 완료`)
      })
      .catch(e => {
        console.warn('[BugBubble] JSON import 실패, 폴백 사용:', e)
        allProblems.value = getFallbackProblems()
      })
  } catch (e) {
    console.warn('[BugBubble] 문제 로드 실패, 내장 문제 사용:', e)
    allProblems.value = getFallbackProblems()
  }
}

// ── 내장 폴백 문제 ──
function getFallbackProblems() {
  return [
    {
      step: 1, title: '타입 오류 수정', bug_type: 'A', bug_type_name: 'TypeError',
      file_name: 'calculator.py', fix_mode: 'choice', bug_line: 3,
      buggy_code: 'score = "100"\nbonus = 50\ntotal = score + bonus\nprint(total)',
      error_log: 'TypeError: can only concatenate str (not "int") to str\nLine 3: total = score + bonus',
      hint: 'score의 타입이 무엇인지 확인해보세요.',
      choices: [
        { label: 'total = int(score) + bonus', correct: true },
        { label: 'total = score + str(bonus)', correct: false },
        { label: 'total = score.add(bonus)', correct: false },
        { label: 'total = float(score + bonus)', correct: false },
      ]
    },
    {
      step: 2, title: '인덱스 오류 수정', bug_type: 'B', bug_type_name: 'IndexError',
      file_name: 'list_handler.py', fix_mode: 'choice', bug_line: 2,
      buggy_code: 'items = ["a", "b", "c"]\nlast = items[3]\nprint(last)',
      error_log: 'IndexError: list index out of range\nLine 2: last = items[3]',
      hint: '리스트 인덱스는 0부터 시작합니다. 길이가 3이면 마지막 인덱스는?',
      choices: [
        { label: 'last = items[2]', correct: true },
        { label: 'last = items[-0]', correct: false },
        { label: 'last = items[4]', correct: false },
        { label: 'last = items.last()', correct: false },
      ]
    },
    {
      step: 3, title: 'None 반환 처리', bug_type: 'C', bug_type_name: 'AttributeError',
      file_name: 'user_lookup.py', fix_mode: 'choice', bug_line: 4,
      buggy_code: 'def find_user(users, name):\n    for u in users:\n        if u["name"] == name:\n            return u\n\nresult = find_user([], "Alice")\nprint(result["email"])',
      error_log: "AttributeError: 'NoneType' object has no attribute '__getitem__'\nLine 7: print(result[\"email\"])",
      hint: '함수가 아무것도 찾지 못할 때 무엇을 반환하나요?',
      choices: [
        { label: 'if result is not None: print(result["email"])', correct: true },
        { label: 'print(result.email)', correct: false },
        { label: 'print(str(result["email"]))', correct: false },
        { label: 'result = find_user([], "Alice") or {}', correct: false },
      ]
    },
    {
      step: 4, title: '무한 루프 탈출', bug_type: 'D', bug_type_name: 'LogicError',
      file_name: 'counter.py', fix_mode: 'choice', bug_line: 3,
      buggy_code: 'count = 0\nwhile count < 5:\n    print(count)\n    count = count',
      error_log: 'Program hangs (infinite loop)\nLine 4: count never changes',
      hint: 'count가 언제 변하나요? 루프가 끝나려면 무엇이 필요할까요?',
      choices: [
        { label: 'count = count + 1', correct: true },
        { label: 'count = count - 1', correct: false },
        { label: 'count == count + 1', correct: false },
        { label: 'break', correct: false },
      ]
    },
    {
      step: 5, title: '딕셔너리 키 오류', bug_type: 'E', bug_type_name: 'KeyError',
      file_name: 'config_loader.py', fix_mode: 'choice', bug_line: 3,
      buggy_code: 'config = {"host": "localhost", "port": 8080}\nhost = config["host"]\ndb_name = config["database"]',
      error_log: "KeyError: 'database'\nLine 3: db_name = config[\"database\"]",
      hint: '존재하지 않는 키에 접근할 때 안전하게 처리하는 방법은?',
      choices: [
        { label: 'db_name = config.get("database", "default_db")', correct: true },
        { label: 'db_name = config["db"]', correct: false },
        { label: 'db_name = config.database', correct: false },
        { label: 'db_name = config or "default_db"', correct: false },
      ]
    },
  ]
}

// ── 선택지 클래스 ──
function getChoiceClass(idx) {
  if (answerState.value === 'idle') return ''
  const choice = currentProblem.value?.choices?.[idx]
  if (!choice) return ''
  if (choice.correct) return 'correct-choice'
  if (idx === selectedChoiceIdx.value && !choice.correct) return 'wrong-choice'
  return 'dim-choice'
}

// ── 정답 선택 ──
function selectChoice(idx) {
  if (answerState.value !== 'idle') return
  selectedChoiceIdx.value = idx
  const choice = currentProblem.value?.choices?.[idx]
  if (!choice) return

  if (choice.correct) {
    answerState.value = 'correct'
    combo.value++
    if (combo.value > bestCombo.value) bestCombo.value = combo.value
    totalSolved.value++
    spawnComboPopup()

    // 내 화면 버그 1개 제거
    if (activeMonsters.value.length > 0) {
      activeMonsters.value.pop()
    }

    // 버블 날리기 애니메이션 후 소켓 전송
    launchBubble()

    // 콤보 3개 이상 = 피버 공격 (버그 3개 전송)
    if (combo.value >= 3 && combo.value % 3 === 0) {
      setTimeout(() => {
        bs.emitFeverAttack(currentRoomId.value, 3)
        opponentMonsterCount.value = Math.min(maxMonsters, opponentMonsterCount.value + 3)
        spawnComboPopup('🔥 FEVER! +3')
      }, 300)
    } else {
      bs.emitSendMonster(currentRoomId.value, 'normal')
      opponentMonsterCount.value = Math.min(maxMonsters, opponentMonsterCount.value + 1)
    }
  } else {
    answerState.value = 'wrong'
    combo.value = 0
    // 틀리면 내 화면에 버그 +1
    spawnMonsters(1)
  }

  // 1.2초 후 다음 문제로
  setTimeout(() => {
    answerState.value = 'idle'
    selectedChoiceIdx.value = -1
    showHint.value = false
    nextProblem()
  }, 1200)
}

function nextProblem() {
  if (allProblems.value.length === 0) return
  currentProblemIndex.value = (currentProblemIndex.value + 1) % allProblems.value.length
}

// ── 버블 날리기 애니메이션 ──
function launchBubble() {
  const id = ++flyBubbleId
  totalBubblesSent.value++
  const startX = window.innerWidth * 0.15
  const startY = window.innerHeight * 0.5
  flyingBubbles.value.push({ id, x: startX, y: startY })
  setTimeout(() => {
    flyingBubbles.value = flyingBubbles.value.filter(b => b.id !== id)
  }, 800)
}

// ── 콤보 팝업 ──
function spawnComboPopup(text) {
  const id = ++combPopId
  const txt = text || (combo.value > 1 ? `COMBO x${combo.value}! 🔥` : '정답! ✅')
  comboPops.value.push({
    id, text: txt,
    x: 30 + Math.random() * 40 + '%',
    y: 30 + Math.random() * 30 + '%'
  })
  setTimeout(() => {
    comboPops.value = comboPops.value.filter(p => p.id !== id)
  }, 1000)
}

// ── 몬스터 스폰 ──
function spawnMonsters(count) {
  for (let i = 0; i < count; i++) {
    activeMonsters.value.push({
      id: Date.now() + Math.random(),
      x: 20 + Math.random() * (window.innerWidth * 0.85 - 60),
      y: 100 + Math.random() * (window.innerHeight * 0.6),
      dx: (Math.random() - 0.5) * 3,
      dy: (Math.random() - 0.5) * 3,
      size: 1.5 + Math.random() * 0.8
    })
  }
  checkGameOver()
}

function checkGameOver() {
  if (activeMonsters.value.length >= maxMonsters) {
    bs.emitGameOver(currentRoomId.value)
  }
}

// ── 게임 루프 (몬스터 이동) ──
function startGameLoop() {
  function loop() {
    if (!bs.isPlaying.value) return
    const W = window.innerWidth * 0.9
    const H = window.innerHeight * 0.75

    activeMonsters.value.forEach(m => {
      m.x += m.dx
      m.y += m.dy
      if (m.x < 0 || m.x > W) m.dx *= -1
      if (m.y < 80 || m.y > H) m.dy *= -1
      if (Math.random() < 0.015) {
        m.dx = (Math.random() - 0.5) * 3
        m.dy = (Math.random() - 0.5) * 3
      }
    })
    animFrameId = requestAnimationFrame(loop)
  }
  loop()
}

// ── 방 입장 ──
function joinRoom() {
  if (!inputRoomId.value.trim()) return
  currentRoomId.value = inputRoomId.value.trim()
  bs.connect(currentRoomId.value, auth.sessionNickname || 'Anonymous', null)
}

function startGame() {
  bs.emitStart(currentRoomId.value)
}

// ── 소켓 이벤트 ──
onMounted(() => {
  loadProblems()

  bs.onGameStart.value = () => {
    spawnMonsters(3)
    opponentMonsterCount.value = 3
    startGameLoop()
  }

  // 상대가 내게 버그 1개 보냄
  bs.onReceiveMonster.value = () => {
    spawnMonsters(1)
  }

  // 상대가 피버 공격
  bs.onReceiveFever.value = (data) => {
    spawnMonsters(data.count || 3)
  }

  bs.onGameEnd.value = (result) => {
    cancelAnimationFrame(animFrameId)
    isWinner.value = result.isWinner
    const name = auth.sessionNickname || 'Player'
    addBattleRecord(name, result.isWinner ? 'win' : 'lose')
  }
})

onUnmounted(() => {
  cancelAnimationFrame(animFrameId)
  bs.disconnect()
})
</script>

<style scoped>
.bubble-game-container {
  min-height: 100vh;
  background: #0d1117;
  color: #c9d1d9;
  font-family: 'Space Grotesk', monospace;
  position: relative;
  overflow: hidden;
}

/* ── JOIN / LOBBY ── */
.join-screen, .lobby-screen, .result-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  gap: 1.5rem;
  padding: 2rem;
}
.join-screen h1, .lobby-screen h1 { font-size: 2.5rem; color: #58a6ff; }
.desc { color: #8b949e; text-align: center; }

.join-box { display: flex; gap: 1rem; }
.join-box input {
  padding: 0.75rem 1rem; font-size: 1rem;
  border-radius: 8px; border: 1px solid #30363d;
  background: #010409; color: #c9d1d9; width: 260px;
}
.join-btn {
  padding: 0.75rem 1.5rem; background: #238636; color: white;
  border: none; border-radius: 8px; cursor: pointer; font-weight: bold;
}
.join-btn:disabled { background: #2ea04366; cursor: not-allowed; }
.back-btn {
  padding: 0.5rem 1.5rem; background: transparent;
  border: 1px solid #8b949e; color: #8b949e; border-radius: 8px; cursor: pointer;
}

.how-to-play {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 0.75rem; max-width: 600px; width: 100%;
  background: #161b22; padding: 1.25rem; border-radius: 12px; border: 1px solid #30363d;
}
.htp-item { display: flex; align-items: flex-start; gap: 0.75rem; }
.htp-icon { font-size: 1.5rem; }
.htp-item strong { display: block; font-size: 0.9rem; color: #f0f6fc; margin-bottom: 2px; }
.htp-item p { font-size: 0.75rem; color: #8b949e; margin: 0; }

.players-box {
  display: flex; align-items: center; gap: 2rem;
  background: #161b22; padding: 1.5rem 3rem;
  border-radius: 12px; border: 1px solid #30363d;
}
.player { font-size: 1.3rem; font-weight: bold; }
.player.me { color: #3fb950; }
.player.opponent { color: #ff7b72; }
.vs { font-size: 1.5rem; color: #8b949e; }

.start-btn {
  padding: 1rem 3rem; font-size: 1.25rem; background: #238636;
  color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;
  transition: all 0.2s;
}
.start-btn:hover:not(:disabled) { background: #2ea043; transform: translateY(-2px); }
.start-btn:disabled { background: #2ea04366; cursor: not-allowed; }

/* ── RESULT ── */
.result-screen h1.win { color: #3fb950; font-size: 3rem; }
.result-screen h1.lose { color: #ff7b72; font-size: 3rem; }
.result-stats {
  display: flex; gap: 2rem;
  background: #161b22; padding: 1.5rem 3rem;
  border-radius: 12px; border: 1px solid #30363d;
}
.stat-item { display: flex; flex-direction: column; align-items: center; gap: 0.25rem; }
.stat-label { font-size: 0.75rem; color: #8b949e; }
.stat-value { font-size: 2rem; font-weight: bold; color: #58a6ff; }
.exit-btn {
  padding: 0.75rem 2rem; background: #21262d; color: #58a6ff;
  border: 1px solid #30363d; border-radius: 8px; cursor: pointer; font-size: 1rem;
}

/* ── PLAY SCREEN ── */
.play-screen { min-height: 100vh; display: flex; flex-direction: column; position: relative; }

.game-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.75rem 1.5rem;
  background: #161b22; border-bottom: 1px solid #30363d;
  position: relative; z-index: 10;
}
.player-panel { display: flex; align-items: center; gap: 0.75rem; }
.player-panel.opp { flex-direction: row-reverse; }
.avatar { font-size: 2rem; background: #21262d; width: 50px; height: 50px; border-radius: 50%; border: 2px solid #3fb950; display: flex; align-items: center; justify-content: center; }
.opp-avatar { border-color: #ff7b72; }
.info { display: flex; flex-direction: column; gap: 4px; }
.info.right { align-items: flex-end; }
.info .name { font-weight: bold; color: #f0f6fc; }
.monster-bar {
  width: 160px; height: 12px; background: #21262d;
  border-radius: 6px; border: 1px solid #30363d;
  position: relative; overflow: hidden;
}
.monster-fill {
  height: 100%; background: #3fb950;
  border-radius: 6px; transition: width 0.3s;
}
.monster-fill.danger { background: #ff7b72; animation: pulse-bar 0.5s infinite alternate; }
.opp-fill { background: #ff7b72; }
.opp-bar .opp-fill { background: #ff7b72; }
.opp-bar .opp-fill.danger { background: #ff0000; }
@keyframes pulse-bar { from { opacity: 0.7; } to { opacity: 1; } }
.monster-count {
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.6rem; font-weight: bold; color: #f0f6fc;
  white-space: nowrap;
}

.center-hud { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.vs-badge {
  background: linear-gradient(135deg, #3fb950, #58a6ff);
  color: #0d1117; padding: 4px 16px; border-radius: 20px;
  font-weight: 900; font-size: 1rem;
}
.combo-display {
  font-family: 'Orbitron', monospace; font-size: 0.9rem; font-weight: 900;
  color: #fbbf24; text-shadow: 0 0 10px rgba(251,191,36,0.5);
}
.combo-display.mega-combo { color: #ff7b72; animation: combo-flash 0.4s infinite alternate; }
@keyframes combo-flash { from { transform: scale(1); } to { transform: scale(1.2); } }
.fever-ready { font-size: 0.7rem; color: #ff7b72; font-weight: bold; animation: blink 0.8s infinite; }
@keyframes blink { 50% { opacity: 0.3; } }

/* ── BATTLE ARENA ── */
.battle-arena {
  display: grid; grid-template-columns: 1.2fr 1fr;
  gap: 1rem; padding: 1rem 1.5rem;
  flex: 1; position: relative; z-index: 5;
}

/* 문제 패널 */
.problem-panel {
  background: #161b22; border-radius: 12px;
  border: 1px solid #30363d;
  display: flex; flex-direction: column; gap: 0.75rem;
  padding: 1rem; transition: border-color 0.3s;
}
.problem-panel.pulse-warning { border-color: #ff7b72; box-shadow: 0 0 20px rgba(255,123,114,0.2); }

.problem-header {
  display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;
}
.problem-badge {
  background: #388bfd20; color: #58a6ff; border: 1px solid #388bfd;
  padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: bold;
}
.bug-type-badge {
  background: #ff7b7220; color: #ff7b72; border: 1px solid #ff7b72;
  padding: 2px 8px; border-radius: 20px; font-size: 0.7rem; font-weight: bold;
}
.file-name { color: #8b949e; font-size: 0.75rem; margin-left: auto; }

.error-log {
  background: #0d1117; border: 1px solid #ff7b7240;
  border-radius: 8px; padding: 0.5rem 0.75rem;
}
.log-label { color: #ff7b72; font-size: 0.65rem; font-weight: bold; margin-bottom: 4px; }
.error-log pre { font-size: 0.7rem; color: #ff7b72; margin: 0; white-space: pre-wrap; line-height: 1.5; }

.code-block { border-radius: 8px; overflow: hidden; }
.code-header {
  background: #21262d; padding: 0.4rem 0.75rem;
  display: flex; align-items: center; gap: 6px;
}
.dot { width: 10px; height: 10px; border-radius: 50%; }
.dot.red { background: #ff5f56; }
.dot.yellow { background: #ffbd2e; }
.dot.green { background: #27c93f; }
.code-title { color: #8b949e; font-size: 0.75rem; margin-left: 6px; }
.code-body {
  background: #010409; padding: 0.75rem;
  max-height: 220px; overflow-y: auto;
}
.code-line {
  display: flex; align-items: baseline; gap: 0.75rem;
  padding: 1px 0; border-radius: 3px;
}
.code-line.bug-line { background: rgba(255,123,114,0.1); }
.line-num { color: #484f58; font-size: 0.75rem; width: 20px; text-align: right; flex-shrink: 0; }
.line-code { color: #e6edf3; font-size: 0.8rem; font-family: monospace; white-space: pre; }
.line-code.highlight-bug { color: #ff7b72; text-decoration: underline wavy #ff7b72; }
.bug-marker { color: #ff7b72; font-size: 0.65rem; font-weight: bold; margin-left: auto; flex-shrink: 0; }

.hint-bar {
  background: rgba(88,166,255,0.1); border: 1px solid rgba(88,166,255,0.3);
  border-radius: 8px; padding: 0.5rem 0.75rem;
  font-size: 0.8rem; color: #58a6ff;
}
.hint-btn {
  background: transparent; border: 1px solid #30363d; color: #8b949e;
  padding: 4px 12px; border-radius: 6px; cursor: pointer; font-size: 0.75rem;
  transition: all 0.2s;
}
.hint-btn:hover { border-color: #58a6ff; color: #58a6ff; }

/* 선택지 패널 */
.choices-panel {
  background: #161b22; border-radius: 12px;
  border: 1px solid #30363d; padding: 1rem;
  display: flex; flex-direction: column; gap: 0.75rem;
}
.choices-title { font-size: 0.85rem; color: #8b949e; font-weight: bold; }

.choices-grid { display: flex; flex-direction: column; gap: 0.5rem; }
.choice-btn {
  display: flex; align-items: center; gap: 0.75rem;
  background: #21262d; border: 1px solid #30363d;
  border-radius: 8px; padding: 0.75rem 1rem;
  cursor: pointer; color: #c9d1d9; text-align: left;
  transition: all 0.2s; width: 100%;
}
.choice-btn:hover:not(:disabled) { border-color: #58a6ff; background: rgba(88,166,255,0.08); }
.choice-btn:disabled { cursor: not-allowed; }
.choice-label {
  width: 22px; height: 22px; border-radius: 50%; border: 1px solid #30363d;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.7rem; font-weight: bold; flex-shrink: 0; color: #8b949e;
}
.choice-code { font-family: monospace; font-size: 0.78rem; color: #e6edf3; }

.choice-btn.correct-choice { border-color: #3fb950; background: rgba(63,185,80,0.1); }
.choice-btn.correct-choice .choice-label { border-color: #3fb950; color: #3fb950; background: rgba(63,185,80,0.1); }
.choice-btn.wrong-choice { border-color: #ff7b72; background: rgba(255,123,114,0.1); }
.choice-btn.wrong-choice .choice-label { border-color: #ff7b72; color: #ff7b72; }
.choice-btn.dim-choice { opacity: 0.35; }

.answer-feedback {
  border-radius: 8px; padding: 0.6rem 1rem;
  font-size: 0.85rem; font-weight: bold;
}
.answer-feedback.correct { background: rgba(63,185,80,0.15); border: 1px solid #3fb950; color: #3fb950; }
.answer-feedback.wrong { background: rgba(255,123,114,0.15); border: 1px solid #ff7b72; color: #ff7b72; }

/* ── 몬스터 오버레이 ── */
.monster-overlay {
  position: fixed; inset: 0;
  pointer-events: none; z-index: 30; overflow: hidden;
}
.monster.bug {
  position: absolute; user-select: none;
  filter: drop-shadow(0 0 8px rgba(255,123,114,0.6));
  animation: monster-wobble 2s infinite;
}
@keyframes monster-wobble {
  0%, 100% { transform: rotate(-5deg); }
  50% { transform: rotate(5deg); }
}

.flying-bubble {
  position: absolute;
  font-size: 2.5rem;
  filter: drop-shadow(0 0 12px rgba(88,166,255,0.8));
}
.inner-bug {
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.2rem;
}

.bubble-fly-enter-active { animation: fly-to-right 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards; }
@keyframes fly-to-right {
  0% { transform: translate(0, 0) scale(1); opacity: 1; }
  50% { transform: translate(250px, -80px) scale(0.9); opacity: 0.9; }
  100% { transform: translate(600px, -30px) scale(0.5); opacity: 0; }
}

.combo-pop {
  position: absolute;
  font-size: 1.1rem; font-weight: 900; color: #fbbf24;
  text-shadow: 0 0 10px rgba(251,191,36,0.8);
  white-space: nowrap;
  pointer-events: none;
}
.combo-pop-enter-active { animation: pop-up 1s ease-out forwards; }
@keyframes pop-up {
  0% { opacity: 1; transform: translateY(0) scale(1); }
  100% { opacity: 0; transform: translateY(-60px) scale(1.3); }
}

.slide-up-enter-active { transition: all 0.2s ease-out; }
.slide-up-enter-from { opacity: 0; transform: translateY(8px); }
</style>
