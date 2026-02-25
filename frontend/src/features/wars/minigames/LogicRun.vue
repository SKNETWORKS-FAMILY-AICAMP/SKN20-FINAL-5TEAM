<template>
  <div class="logic-run" :class="{ 'shake': shaking, 'flash-ok': flashOk, 'flash-fail': flashFail }">
    <div class="crt-lines"></div>

    <!-- ===== INTRO ===== -->
    <div v-if="phase === 'intro'" class="intro-screen">
      <div class="intro-box">
        <div class="intro-badge">1 vs 1 SPEED MODE</div>
        <h1 class="intro-title glitch" data-text="LOGIC RUN">LOGIC RUN</h1>
        <p class="intro-sub">의사코드를 빨리 맞춰서 이겨라!</p>
        <div class="intro-rules">
          <div class="rule-item">⚡ 의사코드 정답을 빨리 입력하기</div>
          <div class="rule-item">🏆 정답 개수가 많은 사람이 승리</div>
          <div class="rule-item">⏱️ 총 1분 제한시간</div>
          <div class="rule-item">🎯 같은 라인을 동시에 풀어라!</div>
        </div>
        <div class="team-select">
          <p class="team-label">방 관리 (1대1 경쟁)</p>
          <div class="room-input-group">
            <input v-model="inputRoomId" placeholder="방 번호 입력..." class="room-input" @keyup.enter="joinRoom" />
            <button @click="joinRoom" class="btn-join">입장/변경</button>
          </div>
          <div v-if="roomId" class="current-room-info">
            접속 중인 방: <span class="neon-c">{{ roomId }}</span>
            <div class="room-players">
              선수: <span v-for="p in rs.roomPlayers.value" :key="p.sid" class="p-tag">{{ p.name }} </span>
            </div>
          </div>
          <div v-if="rs.connected.value && !rs.isReady.value" class="lobby-info">상대방을 기다리는 중...</div>
        </div>
        <button @click="requestStart" class="btn-start blink-border" :disabled="!rs.isReady.value">▶ START GAME</button>
      </div>
    </div>

    <!-- ===== PLAY ===== -->
    <div v-if="phase === 'play'" class="game-screen">
      <!-- 상단 HUD: 타이머 & 정답 수 -->
      <div class="hud">
        <div class="hud-cell">
          <span class="hud-lbl">P1</span>
          <span class="hud-val neon-c">{{ correctCountP1 }}정답</span>
        </div>
        <div class="hud-cell timer-cell" :class="{ danger: roundTimeout <= 10 }">
          <div class="timer-bar-track">
            <div class="timer-bar-fill" :style="{ width: roundTimeoutPct + '%' }" :class="{ danger: roundTimeout <= 10 }"></div>
          </div>
          <span class="timer-num">{{ roundTimeout }}s</span>
        </div>
        <div class="hud-cell">
          <span class="hud-lbl">P2</span>
          <span class="hud-val neon-y">{{ correctCountP2 }}정답</span>
        </div>
      </div>

      <!-- 게임 영역 -->
      <div class="game-area">
        <!-- 좌측: 게임 화면 -->
        <div class="game-left">
          <!-- 듀얼 트랙 레이싱 영역 -->
          <div class="runner-stage dual-track">
            <!-- 상단: P2 레인 -->
            <div class="lane p2-lane">
              <div class="lane-label">P2 TRACK</div>
              <div class="runner-char" :style="{ left: p2CorrectPct + '%' }">
                <img :src="playerP2?.avatarUrl || '/image/duck_idle.png'" class="main-avatar" />
              </div>
            </div>

            <!-- 하단: P1 레인 -->
            <div class="lane p1-lane">
              <div class="lane-label">P1 TRACK</div>
              <div class="runner-char" :style="{ left: p1CorrectPct + '%' }" :class="{ running: phase === 'play', stumble: stumbling }">
                <img :src="playerP1?.avatarUrl || '/image/duck_idle.png'" class="main-avatar" />
                <div class="dust-effect" v-if="phase === 'play'"></div>
              </div>
            </div>

            <!-- 결승선 -->
            <div class="finish-line">
              <div class="finish-icon">🏁</div>
            </div>
          </div>

          <!-- 라인 정보 -->
          <div class="line-info">
            <span class="line-badge">라인 {{ currentLineIdx + 1 }} / {{ totalLines }}</span>
            <span class="hint-text">💡 {{ currentHint }}</span>
          </div>
        </div>

        <!-- 우측: 입력 패널 -->
        <div class="game-right">
          <!-- IDE 스타일 에디터 -->
          <div class="editor-panel neon-border">
            <div class="editor-header">
              <div class="editor-tabs">
                <div class="tab active">logic_challenge.ps</div>
              </div>
              <div class="editor-meta">SPEED MODE</div>
            </div>

            <div class="editor-body scrollbar">
              <!-- 현재 라인 입력 -->
              <div class="code-line active-line">
                <div class="hint-bubble" v-if="currentHint">
                  <span class="hb-ico">💡</span> {{ currentHint }}
                </div>
                <div class="input-row">
                  <span class="input-cursor">&gt;</span>
                  <input
                    ref="codeInput"
                    v-model="userInput"
                    class="editor-input"
                    :placeholder="inputPlaceholder"
                    @keydown.enter.prevent="submitLine"
                    :disabled="phase !== 'play'"
                    autocomplete="off"
                    spellcheck="false"
                  />
                </div>
              </div>
            </div>

            <div class="editor-footer">
              <div class="ef-left">UTF-8 | Pseudocode</div>
              <div class="ef-right">
                <span class="err-msg" v-if="errorMsg">⚠️ {{ errorMsg }}</span>
                <button class="btn-ide-submit" @click="submitLine" :disabled="!userInput.trim()">RUN ↵</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== RESULT ===== -->
    <transition name="zoom">
      <div v-if="phase === 'result'" class="overlay">
        <div class="result-box" :class="resultClass">
          <div class="r-icon">{{ resultIcon }}</div>
          <h1 class="r-title">{{ resultTitle }}</h1>
          <div class="r-scores">
            <div class="score-item p1">
              <span class="p-name">{{ playerP1?.name }}</span>
              <span class="p-score">{{ correctCountP1 }}</span>
            </div>
            <span class="vs">VS</span>
            <div class="score-item p2">
              <span class="p-name">{{ playerP2?.name }}</span>
              <span class="p-score">{{ correctCountP2 }}</span>
            </div>
          </div>
          <div class="r-detail">{{ resultDetail }}</div>
          <div class="go-btns">
            <button @click="startGame" class="btn-retry">🔄 다시하기</button>
            <button @click="$router.push('/practice/coduck-wars')" class="btn-exit">🏠 나가기</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- 플로팅 팝업 -->
    <transition-group name="fpop" tag="div" class="fpop-layer">
      <div v-for="f in fpops" :key="f.id" class="fpop-item" :style="f.style">{{ f.text }}</div>
    </transition-group>
  </div>
</template>

<script setup>
// 수정일: 2026-02-25
// 수정내용: 1대1 경쟁형 스피드 게임 (팀전 제거, 전체 1분 타임아웃, 동시 풀기)

import { ref, computed, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

// ─── 멀티플레이어 소켓 ───────────────────────────────
import { useRunSocket } from '../composables/useRunSocket'
const rs = useRunSocket()
const inputRoomId = ref('9999')
const roomId = ref('')

// 방 입장
function joinRoom() {
  if (!inputRoomId.value.trim()) return
  roomId.value = inputRoomId.value.trim()
  rs.connect(roomId.value, auth.sessionNickname, auth.userAvatarUrl)
}

function requestStart() {
  if (rs.isReady.value) {
    rs.emitStart(roomId.value)
  }
}

// 소켓 리스너 등록
rs.onGameStart.value = (qIdx) => {
  const roomPlayers = rs.roomPlayers.value
  // 1대1이므로 정확히 2명만 사용
  playerP1.value = roomPlayers[0] || { name: 'P1', avatar_url: '/image/duck_idle.png', sid: '' }
  playerP2.value = roomPlayers[1] || { name: 'P2', avatar_url: '/image/duck_idle.png', sid: '' }

  startGame(true, qIdx)
}

rs.onSync.value = (data) => {
  // 상대방 정답 수 동기화
  if (data.sid !== rs.socket.value?.id) {
    const myIdx = rs.roomPlayers.value.findIndex(p => p.sid === rs.socket.value.id)
    if (myIdx === 0) {
      // 내가 P1이면 P2 데이터 받기
      correctCountP2.value = data.correctCountP2
    } else {
      // 내가 P2이면 P1 데이터 받기
      correctCountP1.value = data.correctCountP1
    }
  }
  // 라인 동기화
  if (data.currentLineIdx !== undefined) {
    currentLineIdx.value = data.currentLineIdx
  }
}

rs.onEnd.value = (data) => {
  endGame(data.result)
}

// ─── 상태 ───────────────────────────────────────────
const phase = ref('intro')  // intro | play | result
const errorMsg = ref('')
const userInput = ref('')
const shaking = ref(false)
const flashOk = ref(false)
const flashFail = ref(false)
const stumbling = ref(false)
const lastCorrectLine = ref('')

// 플레이어 정보
const playerP1 = ref(null)
const playerP2 = ref(null)

// 게임 상태
const currentLineIdx = ref(0)
const correctCountP1 = ref(0)
const correctCountP2 = ref(0)
const roundTimeout = ref(60)  // 전체 1분 타임아웃

let roundTimeoutInterval = null
let fpopId = 0
const fpops = ref([])
const codeInput = ref(null)

// 퀘스트 데이터
const quests = [
  {
    title: '글로벌 로그인 아키텍처 구현',
    lines: [
      { hint: '로그인 정보를 처리하는 함수 인터페이스 정의', answer: '함수 로그인_처리(사용자_이메일, 사용자_비번):', altAnswers: ['FUNCTION login_process(user_email, user_pw):'] },
      { hint: '이메일 형식의 유효성을 정규식을 통해 검사', answer: '  만약 이메일_형식_체크(사용자_이메일)가 아니면:', altAnswers: ['  IF NOT is_valid_email(user_email) THEN'] },
      { hint: '잘못된 입력에 대한 에러 객체 반환', answer: '    반환 오류("잘못된_이메일")', altAnswers: ['    RETURN ERROR("INVALID_EMAIL")'] },
      { hint: '비밀번호의 최소 길이(8자)를 검증', answer: '  만약 길이(사용자_비번) < 8 이면:', altAnswers: ['  IF LENGTH(user_pw) < 8 THEN'] },
      { hint: '정책 미달 시 보안 정책 예외 전달', answer: '    반환 오류("비밀번호_제한")', altAnswers: ['    RETURN ERROR("WEAK_PASSWORD")'] },
      { hint: 'DB 서버로부터 사용자 계정 정보를 조회', answer: '사용자 = DB_유저_조회(사용자_이메일)', altAnswers: ['user = FETCH_USER_FROM_DB(user_email)'] },
      { hint: '조회된 사용자 데이터가 존재하는지 확인', answer: '만약 사용자가 비어있으면:', altAnswers: ['IF user IS NULL THEN'] },
      { hint: '사용자 미발견 시 에러 반환', answer: '    반환 오류("사용자_없음")', altAnswers: ['    RETURN ERROR("USER_NOT_FOUND")'] },
      { hint: '입력된 비밀번호와 해시값이 일치하는지 비교', answer: '만약 비번_검증(사용자_비번, 사용자.해시)이 실패면:', altAnswers: ['IF NOT BCRYPT_VERIFY(user_pw, user.hash) THEN'] },
      { hint: '불일치 시 권한 거부 예외 반환', answer: '    반환 오류("권한_없음")', altAnswers: ['    RETURN ERROR("UNAUTHORIZED")'] },
      { hint: '인증 성공 후 새로운 세션 토큰 발행', answer: '토큰 = 토큰_생성(사용자.아이디)', altAnswers: ['token = JWT_SIGN(user.id, "HS256")'] },
      { hint: '최종 성공 결과와 토큰을 전달', answer: '반환 성공(토큰)', altAnswers: ['RETURN SUCCESS(token)'] },
    ]
  },
]

const currentQuest = ref(null)
const totalLines = computed(() => currentQuest.value?.lines.length || 0)
const currentHint = computed(() =>
  currentQuest.value?.lines[currentLineIdx.value]?.hint || '완료!'
)
const inputPlaceholder = computed(() =>
  currentQuest.value?.lines[currentLineIdx.value]?.answer
    ? `예: ${currentQuest.value.lines[currentLineIdx.value].answer}`
    : '의사코드를 입력하세요...'
)

// 진행도 (정답 개수 기반)
const maxCorrect = computed(() => totalLines.value)
const p1CorrectPct = computed(() => (correctCountP1.value / maxCorrect.value) * 100)
const p2CorrectPct = computed(() => (correctCountP2.value / maxCorrect.value) * 100)

// 결과 표시
const roundTimeoutPct = computed(() => (roundTimeout.value / 60) * 100)
const resultClass = computed(() => {
  if (correctCountP1.value > correctCountP2.value) return 'res-p1-win'
  if (correctCountP2.value > correctCountP1.value) return 'res-p2-win'
  return 'res-draw'
})
const resultIcon = computed(() => {
  if (correctCountP1.value > correctCountP2.value) return '🏆'
  if (correctCountP2.value > correctCountP1.value) return '🏆'
  return '🤝'
})
const resultTitle = computed(() => {
  if (correctCountP1.value > correctCountP2.value) return `${playerP1.value?.name} 승리!`
  if (correctCountP2.value > correctCountP1.value) return `${playerP2.value?.name} 승리!`
  return '무승부!'
})
const resultDetail = computed(() => {
  return `${playerP1.value?.name} ${correctCountP1.value}개 vs ${playerP2.value?.name} ${correctCountP2.value}개`
})

// ─── 게임 시작 ────────────────────────────────────────
function startGame(fromSocket = false, qIdx = null) {
  if (qIdx !== null && quests[qIdx]) {
    currentQuest.value = quests[qIdx]
  } else {
    currentQuest.value = quests[0]
  }

  currentLineIdx.value = 0
  correctCountP1.value = 0
  correctCountP2.value = 0
  roundTimeout.value = 60
  errorMsg.value = ''
  userInput.value = ''
  shaking.value = false
  flashOk.value = false
  flashFail.value = false
  fpops.value = []

  phase.value = 'play'
  startRoundTimeout()
  nextTick(() => codeInput.value?.focus())
}

// ─── 라운드 타임아웃 (전체 1분) ────────────────────────────────
function startRoundTimeout() {
  if (roundTimeoutInterval) clearInterval(roundTimeoutInterval)

  roundTimeoutInterval = setInterval(() => {
    roundTimeout.value--

    if (roundTimeout.value <= 0) {
      clearInterval(roundTimeoutInterval)
      endGame('timeout')
    }
  }, 1000)
}

// ─── 라인 제출 ────────────────────────────────────────
function submitLine() {
  const input = userInput.value.trim()
  if (!input || phase.value !== 'play') return

  const lineData = currentQuest.value.lines[currentLineIdx.value]
  if (!lineData) return

  const correct = checkAnswer(input, lineData)

  if (correct) {
    handleCorrect(input)
  } else {
    handleWrong()
  }

  userInput.value = ''
  nextTick(() => codeInput.value?.focus())
}

function checkAnswer(input, lineData) {
  const clean = s => s.replace(/\s+/g, '').trim().toLowerCase()
  const answers = [lineData.answer, ...(lineData.altAnswers || [])]

  for (const ans of answers) {
    if (clean(input) === clean(ans)) return true

    const keywords = ans.split(/[\s(),=:"'<>!]+/).filter(k => k.length >= 2)
    const matched = keywords.filter(k => input.includes(k))

    if (keywords.length > 0 && (matched.length / keywords.length) >= 0.6) return true
  }
  return false
}

function handleCorrect(input) {
  // 현재 플레이어의 정답 카운트 증가
  const myIdx = rs.roomPlayers.value.findIndex(p => p.sid === rs.socket.value?.id)
  if (myIdx === 0) {
    correctCountP1.value++
  } else {
    correctCountP2.value++
  }

  lastCorrectLine.value = input
  flashOk.value = true
  setTimeout(() => { flashOk.value = false }, 300)
  spawnFpop('+100', '#34d399')

  currentLineIdx.value++

  // 멀티플레이어 동기화
  const myCorrect = myIdx === 0 ? correctCountP1.value : correctCountP2.value
  rs.emitProgress(roomId.value, {
    correctCountP1: myIdx === 0 ? myCorrect : correctCountP1.value,
    correctCountP2: myIdx === 1 ? myCorrect : correctCountP2.value,
    currentLineIdx: currentLineIdx.value,
    sid: rs.socket.value?.id
  })

  // 모든 라인 완료
  if (currentLineIdx.value >= totalLines.value) {
    endGame('complete')
  }
}

function handleWrong() {
  errorMsg.value = '정답과 다릅니다. 다시 시도하세요.'
  setTimeout(() => { errorMsg.value = '' }, 1500)

  shaking.value = true
  stumbling.value = true
  flashFail.value = true
  setTimeout(() => {
    shaking.value = false
    stumbling.value = false
    flashFail.value = false
  }, 300)

  spawnFpop('오타! 🍌', '#ef4444')
}

// ─── 게임 종료 ────────────────────────────────────────
function endGame(result) {
  if (roundTimeoutInterval) clearInterval(roundTimeoutInterval)
  phase.value = 'result'

  // 멀티플레이어 동기화
  rs.emitFinish(roomId.value, { result })
}

// ─── 유틸 ─────────────────────────────────────────────
function spawnFpop(text, color = '#fbbf24') {
  const id = ++fpopId
  fpops.value.push({
    id, text,
    style: { left: (30 + Math.random() * 40) + '%', color }
  })
  setTimeout(() => { fpops.value = fpops.value.filter(f => f.id !== id) }, 1200)
}

onUnmounted(() => {
  clearInterval(roundTimeoutInterval)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;600;700&family=Space+Grotesk:wght@400;600&display=swap');

/* ── 기본 ─────────────────────────────────── */
.logic-run {
  min-height: 100vh;
  background: #03070f;
  color: #e0f2fe;
  font-family: 'Rajdhani', sans-serif;
  position: relative;
  overflow: hidden;
}
.crt-lines {
  pointer-events: none;
  position: fixed; inset: 0; z-index: 9999;
  background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,240,255,0.01) 2px, rgba(0,240,255,0.01) 4px);
}
.shake { animation: shake .3s ease; }
.flash-ok::after { content:''; position:fixed; inset:0; background:rgba(57,255,20,.1); z-index:9000; pointer-events:none; animation:flashOut .3s forwards; }
.flash-fail::after { content:''; position:fixed; inset:0; background:rgba(255,45,117,.1); z-index:9000; pointer-events:none; animation:flashOut .3s forwards; }
@keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-6px)} 75%{transform:translateX(6px)} }
@keyframes flashOut { from{opacity:1} to{opacity:0} }
.glitch { position:relative; font-family:'Orbitron',sans-serif; }
.glitch::before,.glitch::after { content:attr(data-text); position:absolute; top:0; left:0; width:100%; height:100%; }
.glitch::before { color:#ff2d75; clip-path:inset(0 0 65% 0); animation:g1 2s infinite linear alternate-reverse; }
.glitch::after  { color:#39ff14; clip-path:inset(65% 0 0 0);  animation:g2 2s infinite linear alternate-reverse; }
@keyframes g1 { 50%{transform:translate(-3px,2px)} }
@keyframes g2 { 50%{transform:translate(3px,-2px)} }
.neon-c { color:#00f0ff; text-shadow:0 0 8px #00f0ff; }
.neon-y { color:#ffe600; text-shadow:0 0 8px rgba(255,230,0,.5); }

/* ── INTRO ────────────────────────────────── */
.intro-screen { display:flex; align-items:center; justify-content:center; min-height:100vh; padding:2rem; }
.intro-box {
  text-align:center; max-width:580px; width:100%;
  background:rgba(8,12,30,.9); border:2px solid #00f0ff;
  border-radius:1.5rem; padding:3rem 2.5rem;
  box-shadow:0 0 60px rgba(0,240,255,.12);
}
.intro-badge { display:inline-block; font-size:.6rem; letter-spacing:3px; font-weight:700; padding:4px 14px; background:rgba(0,240,255,.08); border:1px solid rgba(0,240,255,.25); border-radius:4px; color:#00f0ff; margin-bottom:1.5rem; }
.intro-title { font-size:3rem; font-weight:900; color:#00f0ff; letter-spacing:6px; text-shadow:0 0 30px #00f0ff; margin-bottom:.5rem; }
.intro-sub { color:#64748b; letter-spacing:1px; margin-bottom:1.5rem; font-size:.95rem; }
.intro-rules { text-align:left; margin-bottom:1.5rem; }
.rule-item { font-size:.85rem; color:#94a3b8; padding:.3rem 0; border-bottom:1px solid rgba(255,255,255,.04); }
.team-select { margin-bottom:1.5rem; }
.team-label { font-size:.7rem; font-weight:700; color:#475569; letter-spacing:2px; margin-bottom:.6rem; }
.room-input-group { display: flex; gap: 8px; justify-content: center; margin-bottom: 12px; }
.room-input { background: rgba(0, 0, 0, 0.4); border: 1px solid #1e293b; color: #fff; padding: 8px 12px; border-radius: 6px; font-family: 'Orbitron', sans-serif; font-size: 0.9rem; width: 140px; text-align: center; outline: none; }
.room-input:focus { border-color: #00f0ff; box-shadow: 0 0 10px rgba(0, 240, 255, 0.2); }
.btn-join { background: rgba(0, 240, 255, 0.1); border: 1px solid rgba(0, 240, 255, 0.3); color: #00f0ff; padding: 8px 16px; border-radius: 6px; font-family: 'Orbitron', sans-serif; font-size: 0.8rem; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.btn-join:hover { background: #00f0ff; color: #030712; }
.current-room-info { font-size: 0.8rem; color: #64748b; margin-top: 8px; }
.room-players { margin-top: 6px; display: flex; flex-wrap: wrap; justify-content: center; gap: 6px; }
.p-tag { font-size: 0.7rem; background: rgba(0, 240, 255, 0.05); border: 1px solid rgba(0, 240, 255, 0.1); padding: 2px 8px; border-radius: 4px; color: #38bdf8; }
.lobby-info { font-size: 0.8rem; color: #ffe600; margin-top: 10px; animation: blinkB 2s infinite; }

.btn-start { margin-top:1rem; padding:.9rem 3rem; font-family:'Orbitron',sans-serif; font-size:1rem; font-weight:900; background:transparent; border:2px solid #ffe600; color:#ffe600; border-radius:.75rem; cursor:pointer; letter-spacing:3px; transition:all .2s; }
.btn-start:hover { background:rgba(255,230,0,.08); box-shadow:0 0 30px rgba(255,230,0,.3); transform:scale(1.04); }
.blink-border { animation:blinkB 1.5s infinite; }
@keyframes blinkB { 50%{border-color:rgba(255,230,0,.3)} }

/* ── HUD ──────────────────────────────────── */
.hud {
  display:flex; align-items:center; gap:1rem;
  padding:.6rem 1.5rem; margin:.75rem 1rem 0;
  background:rgba(8,12,30,.85); border:1px solid rgba(0,240,255,.1);
  border-radius:1rem;
}
.hud-cell { display:flex; flex-direction:column; align-items:center; }
.hud-lbl { font-size:.5rem; font-weight:700; color:#475569; letter-spacing:2px; }
.hud-val { font-family:'Orbitron',sans-serif; font-size:1.1rem; font-weight:900; }
.timer-cell { flex:1; }
.timer-bar-track { width:100%; height:8px; background:#0f172a; border-radius:4px; overflow:hidden; border:1px solid rgba(0,240,255,.1); }
.timer-bar-fill { height:100%; background:linear-gradient(90deg,#00f0ff,#38bdf8); border-radius:4px; transition:width 1s linear; }
.timer-bar-fill.danger { background:linear-gradient(90deg,#ff2d75,#ef4444); }
.timer-cell.danger .timer-bar-fill { background:linear-gradient(90deg,#ff2d75,#ef4444); }
.timer-num { font-family:'Orbitron',sans-serif; font-size:.75rem; color:#94a3b8; margin-top:2px; }
.timer-cell.danger .timer-num { color:#ff2d75; animation:blinkA .5s infinite; }
@keyframes blinkA { 50%{opacity:.3} }

/* ── GAME AREA ────────────────────────────── */
.game-screen { display:flex; flex-direction:column; height:calc(100vh - 80px); }
.game-area { display:grid; grid-template-columns:1fr 380px; gap:1rem; padding:1rem; flex:1; min-height:0; overflow:hidden; }

/* 좌측 */
.game-left { display:flex; flex-direction:column; gap:.75rem; }
.line-info { display:flex; align-items:center; gap:.5rem; padding:.5rem 1rem; background:rgba(8,12,30,.6); border:1px solid rgba(0,240,255,.1); border-radius:.5rem; }
.line-badge { font-family:'Orbitron',sans-serif; font-size:.7rem; font-weight:700; color:#00f0ff; }
.hint-text { font-size:.8rem; color:#64748b; flex:1; }

/* 달리기 스테이지 */
.runner-stage.dual-track {
  flex:1; position:relative; background:rgba(8,12,30,.8);
  border:1.5px solid rgba(0,240,255,.1); border-radius:1rem;
  overflow:hidden; min-height:220px; display: flex; flex-direction: column;
}
.lane {
  flex: 1; position: relative; display: flex; align-items: flex-end;
  padding-bottom: 8px; border-bottom: 1px dashed rgba(255,255,255,0.05);
  background: linear-gradient(0deg, rgba(255,255,255,0.02) 0%, transparent 100%);
}
.lane:last-child { border-bottom: none; }
.lane-label {
  position: absolute; top: 10px; left: 15px; font-family: 'Orbitron', sans-serif;
  font-size: 0.6rem; font-weight: 700; color: rgba(255,255,255,0.2);
  letter-spacing: 2px; pointer-events: none;
}
.p1-lane { background: rgba(0,240,255,0.03); }
.p2-lane { background: rgba(255,45,117,0.03); }

.runner-char {
  position:absolute; bottom:8px; transition:left .5s ease;
  width: 64px; height: 64px; display: flex; align-items: flex-end;
  justify-content: center; transform: translateX(-50%);
}
.main-avatar { width: 56px; height: 56px; object-fit: contain; filter: drop-shadow(0 0 10px rgba(0,240,255,0.3)); }
.runner-char.running { animation:runBounce .4s infinite ease-in-out; }
.runner-char.stumble { animation:stumbleAnim .3s ease; }

.finish-line {
  position: absolute; right: 20px; top: 0; bottom: 0; width: 40px;
  background: repeating-linear-gradient(45deg, #eee 0, #eee 5px, #222 5px, #222 10px);
  opacity: 0.15; display: flex; align-items: center; justify-content: center;
}
.finish-icon { font-size: 1.5rem; transform: rotate(-10deg); filter: grayscale(1); }

.dust-effect {
  position: absolute; bottom: 0; left: 0;
  width: 12px; height: 8px; background: rgba(255,255,255,0.3);
  border-radius: 50%; filter: blur(2px);
  animation: dustAnim 0.4s infinite;
}
@keyframes dustAnim {
  0% { transform: scale(1) translateX(0); opacity: 0.6; }
  100% { transform: scale(3) translateX(-40px); opacity: 0; }
}

@keyframes runBounce {
  0%,100%{transform:translateY(0) rotate(5deg) scaleX(1)}
  50%{transform:translateY(-10px) rotate(-5deg) scaleX(1.05)}
}
@keyframes stumbleAnim { 0%,100%{transform:rotate(0)} 50%{transform:rotate(-20deg)} }

/* 우측 */
.game-right { display:flex; flex-direction:column; gap:.75rem; overflow-y:auto; }

/* IDE 에디터 */
.editor-panel { background:rgba(8,12,30,.8); border:1px solid rgba(0,240,255,.15); border-radius:.75rem; overflow:hidden; display:flex; flex-direction:column; height:100%; }
.editor-header { background:#0a0f1e; padding:.75rem; border-bottom:1px solid #1e293b; display:flex; align-items:center; justify-content:space-between; }
.editor-tabs { display:flex; gap:.5rem; }
.tab { font-size:.65rem; color:#64748b; padding:.4rem .75rem; border-bottom:2px solid transparent; cursor:pointer; }
.tab.active { color:#00f0ff; border-bottom-color:#00f0ff; }
.editor-meta { font-size:.6rem; color:#475569; }
.editor-body { flex:1; background:#0f1419; overflow-y:auto; padding:.75rem; font-family:'Courier New',monospace; }
.code-line { margin-bottom:.5rem; }
.code-line.active-line { }
.hint-bubble { display:flex; align-items:center; gap:.4rem; background:rgba(59,182,254,.1); border:1px solid rgba(59,182,254,.3); border-radius:.4rem; padding:.4rem .6rem; margin-bottom:.4rem; font-size:.75rem; color:#93c5fd; }
.hb-ico { font-size:.9rem; }
.input-row { display:flex; align-items:center; gap:.4rem; }
.input-cursor { color:#00f0ff; font-weight:700; }
.editor-input { flex:1; background:transparent; border:none; color:#e0f2fe; font-family:'Courier New',monospace; font-size:.85rem; outline:none; }
.editor-footer { background:#161b22; padding:.6rem .75rem; border-top:1px solid #30363d; display:flex; justify-content:space-between; align-items:center; font-size:.65rem; color:#8b949e; }
.ef-left { }
.ef-right { display:flex; align-items:center; gap:.75rem; }
.err-msg { color:#f85149; font-weight:700; }
.btn-ide-submit { background:#238636; color:#fff; border:none; padding:4px 16px; border-radius:4px; font-family:'Orbitron',sans-serif; font-size:.65rem; font-weight:900; cursor:pointer; transition:all .2s; }
.btn-ide-submit:hover:not(:disabled) { background:#2ea043; }
.btn-ide-submit:disabled { background:#21262d; color:#484f58; cursor:not-allowed; }

.neon-border { border:1px solid rgba(0,240,255,.15) !important; }

/* ── RESULT ────────────────────────────────── */
.overlay { position:fixed; inset:0; background:rgba(0,0,0,.85); display:flex; align-items:center; justify-content:center; z-index:8000; }
.result-box {
  text-align:center; max-width:520px; width:90%;
  background:rgba(8,12,30,.95); border:2px solid #00f0ff;
  border-radius:1.5rem; padding:3rem 2.5rem;
  box-shadow:0 0 60px rgba(0,240,255,.2);
}
.result-box.res-p1-win { border-color:#38bdf8; }
.result-box.res-p2-win { border-color:#ff2d75; }
.result-box.res-draw { border-color:#ffe600; }

.r-icon { font-size:3.5rem; margin-bottom:1rem; }
.r-title { font-size:2rem; font-weight:900; color:#00f0ff; margin-bottom:1.5rem; letter-spacing:2px; }
.r-scores {
  display:flex; align-items:center; justify-content:center; gap:1.5rem;
  margin-bottom:1.5rem;
}
.score-item { display:flex; flex-direction:column; align-items:center; gap:.4rem; }
.score-item.p1 {  }
.p-name { font-size:.9rem; color:#64748b; }
.p-score { font-family:'Orbitron',sans-serif; font-size:2rem; font-weight:900; color:#38bdf8; }
.score-item.p2 .p-score { color:#ff2d75; }
.vs { font-size:1.2rem; color:#475569; font-weight:700; }
.r-detail { font-size:.85rem; color:#94a3b8; margin-bottom:1.5rem; }

.go-btns { display:flex; gap:1rem; justify-content:center; }
.btn-retry { padding:.75rem 2rem; background:transparent; border:2px solid #00f0ff; color:#00f0ff; border-radius:.5rem; font-family:'Orbitron',sans-serif; font-weight:700; cursor:pointer; transition:all .2s; }
.btn-retry:hover { background:rgba(0,240,255,.1); }
.btn-exit { padding:.75rem 2rem; background:transparent; border:2px solid #64748b; color:#64748b; border-radius:.5rem; font-family:'Orbitron',sans-serif; font-weight:700; cursor:pointer; transition:all .2s; }
.btn-exit:hover { color:#94a3b8; border-color:#94a3b8; }

/* ── FLOAT POP ─────────────────────────────── */
.fpop-layer { position:fixed; inset:0; pointer-events:none; z-index:7000; }
.fpop-item { position:absolute; font-family:'Orbitron',sans-serif; font-size:1rem; font-weight:700; animation:popUp 1.2s ease-out forwards; }
@keyframes popUp {
  0% { transform:translateY(0) scale(1); opacity:1; }
  100% { transform:translateY(-60px) scale(0.8); opacity:0; }
}

/* ── 트랜지션 ──────────────────────────────── */
.zoom-enter-active, .zoom-leave-active { transition: transform 0.3s ease, opacity 0.3s ease; }
.zoom-enter-from, .zoom-leave-to { transform: scale(0.9); opacity: 0; }

.fpop-enter-active { transition: all 0.3s ease; }
.fpop-leave-active { transition: all 0.2s ease; }
.fpop-enter-from { opacity: 0; transform: translateY(20px); }
.fpop-leave-to { opacity: 0; transform: translateY(-30px); }
</style>
