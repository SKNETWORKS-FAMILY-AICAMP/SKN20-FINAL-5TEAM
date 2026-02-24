<template>
  <div class="arcade-builder" :class="{ 'screen-shake': shaking, 'flash-ok': flashOk, 'flash-fail': flashFail }">
    <div class="crt-lines"></div>

    <!-- INTRO -->
    <div v-if="phase === 'intro'" class="intro-screen">
      <div class="intro-box">
        <h1 class="intro-title glitch" data-text="SPEED BUILD">SPEED BUILD</h1>
        <p class="intro-sub">스피드 아키텍처 빌더</p>
        <div class="intro-how">
          <p>⚡ 시나리오에 맞는 컴포넌트를 골라 배치하세요</p>
          <p>🎯 정답만 빠르게 골라내면 고득점!</p>
          <p>🔥 연속 PERFECT로 콤보 보너스!</p>
        </div>
        <button @click="startGame" class="btn-start blink-border">▶ START GAME</button>
      </div>
    </div>

    <!-- GAME -->
    <div v-if="phase === 'play' || phase === 'result'" class="game-view">

      <!-- HUD -->
      <div class="hud">
        <div class="hud-cell">
          <span class="hud-lbl">ROUND</span>
          <span class="hud-num neon-c">{{ round }}</span>
          <span class="hud-dim">/{{ maxRounds }}</span>
        </div>
        <div class="hud-cell timer-cell" :class="{ danger: timerDanger }">
          <div class="timer-bar-track">
            <div class="timer-bar-fill" :style="{ width: timerPct + '%' }"></div>
          </div>
          <span class="timer-num">{{ timeLeft }}s</span>
        </div>
        <div class="hud-cell">
          <span class="hud-lbl">SCORE</span>
          <span class="hud-num neon-y" :key="score">{{ score }}</span>
        </div>
        <div class="hud-cell" v-if="comboVal > 1">
          <span class="combo-pill neon-fire">{{ comboVal }}x</span>
        </div>
      </div>

      <!-- SCENARIO -->
      <div class="scenario-banner" v-if="curScenario">
        <span class="s-icon">{{ curScenario.icon }}</span>
        <div class="s-info">
          <strong>{{ curScenario.title }}</strong>
          <span>{{ curScenario.desc }}</span>
        </div>
        <div class="s-need">
          <span class="need-label">NEED</span>
          <span class="need-count neon-c">{{ remainCount }}</span>
        </div>
      </div>

      <!-- MAIN: TRAY + BOARD -->
      <div class="build-area">
        <!-- Tray -->
        <div class="tray">
          <div class="tray-title">📦 COMPONENTS</div>
          <div class="tray-grid">
            <button v-for="c in trayComps" :key="c.id"
              class="comp-btn"
              :class="{ selected: isPlaced(c.id), correct: correctIds.includes(c.id), wrong: wrongIds.includes(c.id) }"
              @click="toggleComp(c)"
              :disabled="phase !== 'play'"
            >
              <span class="cb-icon">{{ c.icon }}</span>
              <span class="cb-name">{{ c.name }}</span>
            </button>
          </div>
          <!-- Hint -->
          <div class="hint-box" v-if="hintText">
            <span>💡</span> {{ hintText }}
          </div>
          <button @click="getHint" class="btn-hint" :disabled="hints >= 2 || phase !== 'play'">
            💡 HINT ({{ 2 - hints }})
          </button>
        </div>

        <!-- Board -->
        <div class="board">
          <div class="board-title">🏗️ ARCHITECTURE BOARD</div>
          <div class="board-grid">
            <div v-for="slot in slots" :key="slot.id" class="board-slot"
              :class="{ filled: slot.comp, correct: slot.ok, wrong: slot.fail }"
            >
              <template v-if="slot.comp">
                <span class="bs-icon">{{ slot.comp.icon }}</span>
                <span class="bs-name">{{ slot.comp.name }}</span>
                <button class="bs-remove" @click="removeSlot(slot)" v-if="phase === 'play'">✕</button>
              </template>
              <template v-else>
                <span class="bs-label">{{ slot.label }}</span>
              </template>
            </div>
          </div>
          <button @click="submitBuild" class="btn-submit" :disabled="placed.length === 0 || phase !== 'play'">
            ⚡ SUBMIT
          </button>
        </div>
      </div>
    </div>

    <!-- ROUND RESULT -->
    <transition name="zoom">
      <div v-if="phase === 'result'" class="overlay">
        <div class="result-box" :class="resultClass">
          <div class="r-icon">{{ resultIcon }}</div>
          <div class="r-title">{{ resultLabel }}</div>
          <div class="r-detail">{{ correctHit }}/{{ curScenario?.required?.length }} 정답</div>
          <div class="r-pts" v-if="lastPts">+{{ lastPts }}</div>
          <div class="r-explain">{{ curScenario?.explanation }}</div>
          <button @click="nextRound" class="btn-next">{{ nextLabel }}</button>
        </div>
      </div>
    </transition>

    <!-- GAME OVER -->
    <transition name="zoom">
      <div v-if="phase === 'gameover'" class="overlay dark-overlay">
        <div class="go-box">
          <h1 class="go-title glitch" data-text="COMPLETE">COMPLETE</h1>
          <div class="go-grade" :class="'g-' + grade">{{ grade }}</div>
          <div class="go-score">{{ score }}<small>PTS</small></div>
          <div class="go-row">
            <span>{{ perfectCount }}/{{ maxRounds }} PERFECT</span>
            <span>BEST COMBO {{ maxCombo }}x</span>
          </div>
          <div class="go-btns">
            <button @click="startGame" class="btn-retry">🔄 RETRY</button>
            <button @click="$router.push('/practice/coduck-wars')" class="btn-exit">🏠 EXIT</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Float pops -->
    <transition-group name="fpop" tag="div" class="fpop-layer">
      <div v-for="f in fpops" :key="f.id" class="fpop-item" :style="f.style">+{{ f.v }}</div>
    </transition-group>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const phase = ref('intro')
const round = ref(0)
const maxRounds = 8
const timeLeft = ref(25)
const score = ref(0)
const comboVal = ref(0)
const maxCombo = ref(0)
const perfectCount = ref(0)
const hints = ref(0)
const hintText = ref('')
const placed = ref([])
const correctIds = ref([])
const wrongIds = ref([])
const correctHit = ref(0)
const lastPts = ref(0)
const shaking = ref(false)
const flashOk = ref(false)
const flashFail = ref(false)
const fpops = ref([])
let fpopId = 0
let timer = null

const allScenarios = [
  { icon: '🔥', title: '트래픽 폭주', desc: '프로모션으로 서버가 터진다!', explanation: '로드밸런서+오토스케일링+CDN+캐시가 핵심', required: ['lb','autoscale','cdn','cache'], hints: ['트래픽 분산이 필수','정적 파일은 엣지에서'], slots: [{id:'s1',label:'진입'},{id:'s2',label:'분산'},{id:'s3',label:'캐싱'},{id:'s4',label:'정적'},{id:'s5',label:'서버'},{id:'s6',label:'DB'}] },
  { icon: '💀', title: 'DB 장애', desc: 'DB 데드락! 읽기/쓰기 분리!', explanation: 'Read Replica+캐시+커넥션풀+인덱스가 핵심', required: ['replica','cache','connpool','index'], hints: ['읽기 복제본 추가','자주 조회는 캐싱'], slots: [{id:'s1',label:'앱'},{id:'s2',label:'캐시'},{id:'s3',label:'Write'},{id:'s4',label:'Read'},{id:'s5',label:'최적화'},{id:'s6',label:'풀'}] },
  { icon: '🛡️', title: 'API 보안', desc: 'SQL Injection 공격 감지!', explanation: 'WAF+Rate Limit+JWT+입력검증이 필수', required: ['waf','ratelimit','jwt','valid'], hints: ['방화벽을 앞에','모든 입력 검증'], slots: [{id:'s1',label:'방화벽'},{id:'s2',label:'제한'},{id:'s3',label:'인증'},{id:'s4',label:'검증'},{id:'s5',label:'로깅'},{id:'s6',label:'암호화'}] },
  { icon: '🌐', title: '글로벌 론칭', desc: '3개 대륙 동시 200ms 이하!', explanation: 'CDN+글로벌LB+멀티리전+DNS가 핵심', required: ['cdn','globalLB','multiregion','dns'], hints: ['리전별 엣지 필요','DNS 라우팅 고려'], slots: [{id:'s1',label:'DNS'},{id:'s2',label:'글로벌'},{id:'s3',label:'CDN'},{id:'s4',label:'리전DB'},{id:'s5',label:'복제'},{id:'s6',label:'모니터'}] },
  { icon: '💬', title: '실시간 채팅', desc: '100만 동접 메시지 유실 없이!', explanation: 'WebSocket+메시지큐+PubSub+캐시가 핵심', required: ['ws','msgq','pubsub','cache'], hints: ['양방향 통신','메시지 큐 보관'], slots: [{id:'s1',label:'연결'},{id:'s2',label:'메시지'},{id:'s3',label:'구독'},{id:'s4',label:'캐시'},{id:'s5',label:'저장'},{id:'s6',label:'알림'}] },
  { icon: '🧩', title: 'MSA 전환', desc: '모놀리식을 쪼개라!', explanation: 'API GW+서비스메시+이벤트버스+서킷브레이커가 핵심', required: ['apigw','mesh','eventbus','circuit'], hints: ['단일 진입점','장애 전파 차단'], slots: [{id:'s1',label:'진입'},{id:'s2',label:'통신'},{id:'s3',label:'이벤트'},{id:'s4',label:'차단'},{id:'s5',label:'모니터'},{id:'s6',label:'로깅'}] },
  { icon: '🚀', title: 'CI/CD', desc: '하루 100번 무중단 배포!', explanation: 'Git+CI/CD+Blue-Green+롤백이 핵심', required: ['git','cicd','bluegreen','rollback'], hints: ['배포 자동화','실패시 즉시 복구'], slots: [{id:'s1',label:'소스'},{id:'s2',label:'빌드'},{id:'s3',label:'배포'},{id:'s4',label:'롤백'},{id:'s5',label:'모니터'},{id:'s6',label:'알림'}] },
  { icon: '📊', title: '데이터 파이프', desc: '초당 10만 이벤트 실시간 분석!', explanation: 'Kafka+스트림프로세서+데이터레이크+대시보드가 핵심', required: ['kafka','stream','lake','dash'], hints: ['이벤트 버퍼링 큐','원본 그대로 저장'], slots: [{id:'s1',label:'수집'},{id:'s2',label:'스트림'},{id:'s3',label:'저장'},{id:'s4',label:'시각화'},{id:'s5',label:'알림'},{id:'s6',label:'백업'}] },
]

const allComps = [
  { id:'lb', name:'로드밸런서', icon:'⚖️' }, { id:'autoscale', name:'오토스케일링', icon:'📈' },
  { id:'cdn', name:'CDN', icon:'🌍' }, { id:'cache', name:'캐시(Redis)', icon:'💾' },
  { id:'replica', name:'Read Replica', icon:'📖' }, { id:'connpool', name:'커넥션 풀', icon:'🔗' },
  { id:'index', name:'DB 인덱스', icon:'📇' }, { id:'waf', name:'WAF', icon:'🧱' },
  { id:'ratelimit', name:'Rate Limiter', icon:'🚦' }, { id:'jwt', name:'JWT 인증', icon:'🔑' },
  { id:'valid', name:'입력 검증', icon:'✅' }, { id:'globalLB', name:'Global LB', icon:'🌐' },
  { id:'multiregion', name:'멀티리전 DB', icon:'🗺️' }, { id:'dns', name:'DNS 라우팅', icon:'📡' },
  { id:'ws', name:'WebSocket', icon:'🔌' }, { id:'msgq', name:'메시지큐', icon:'📨' },
  { id:'pubsub', name:'Pub/Sub', icon:'📢' }, { id:'apigw', name:'API Gateway', icon:'🚪' },
  { id:'mesh', name:'서비스 메시', icon:'🕸️' }, { id:'eventbus', name:'이벤트 버스', icon:'🚌' },
  { id:'circuit', name:'서킷브레이커', icon:'⚡' }, { id:'git', name:'Git', icon:'📝' },
  { id:'cicd', name:'CI/CD', icon:'🔄' }, { id:'bluegreen', name:'Blue-Green', icon:'🟢' },
  { id:'rollback', name:'롤백', icon:'↩️' }, { id:'kafka', name:'Kafka', icon:'📊' },
  { id:'stream', name:'스트림 프로세서', icon:'🌊' }, { id:'lake', name:'데이터레이크', icon:'🏊' },
  { id:'dash', name:'대시보드', icon:'📺' },
  // distractors
  { id:'blockchain', name:'Blockchain', icon:'⛓️' }, { id:'quantum', name:'Quantum DB', icon:'🔮' }, { id:'fax', name:'팩스서버', icon:'📠' },
]

const scenarios = ref([])
const curScenario = computed(() => scenarios.value[round.value - 1])
const slots = ref([])
const trayComps = ref([])
const remainCount = computed(() => {
  if (!curScenario.value) return 0
  return curScenario.value.required.length - correctIds.value.length
})
const timerPct = computed(() => (timeLeft.value / 25) * 100)
const timerDanger = computed(() => timeLeft.value <= 8)

const resultClass = computed(() => {
  if (!curScenario.value) return ''
  return correctHit.value === curScenario.value.required.length ? 'res-perfect' : correctHit.value > 0 ? 'res-partial' : 'res-miss'
})
const resultIcon = computed(() => {
  if (!curScenario.value) return ''
  return correctHit.value === curScenario.value.required.length ? '🎉' : correctHit.value > 0 ? '👍' : '💀'
})
const resultLabel = computed(() => {
  if (!curScenario.value) return ''
  return correctHit.value === curScenario.value.required.length ? 'PERFECT!' : correctHit.value > 0 ? 'PARTIAL' : 'MISS'
})
const nextLabel = computed(() => round.value >= maxRounds ? 'SEE RESULTS' : 'NEXT ▶')

const grade = computed(() => {
  const r = perfectCount.value / maxRounds
  if (r >= 0.85) return 'S'
  if (r >= 0.65) return 'A'
  if (r >= 0.45) return 'B'
  return 'C'
})

function isPlaced(id) { return placed.value.includes(id) }

onUnmounted(() => clearInterval(timer))

function startGame() {
  scenarios.value = [...allScenarios].sort(() => Math.random() - 0.5).slice(0, maxRounds)
  score.value = 0; comboVal.value = 0; maxCombo.value = 0; perfectCount.value = 0; round.value = 0
  phase.value = 'play'
  nextRound()
}

function nextRound() {
  phase.value = 'play'
  round.value++
  if (round.value > maxRounds) { phase.value = 'gameover'; return }
  timeLeft.value = 25; hints.value = 0; hintText.value = ''
  placed.value = []; correctIds.value = []; wrongIds.value = []
  slots.value = curScenario.value.slots.map(s => ({ ...s, comp: null, ok: false, fail: false }))
  // Build tray: required + random distractors
  const req = allComps.filter(c => curScenario.value.required.includes(c.id))
  const dist = allComps.filter(c => !curScenario.value.required.includes(c.id)).sort(() => Math.random() - 0.5).slice(0, 5)
  trayComps.value = [...req, ...dist].sort(() => Math.random() - 0.5)
  clearInterval(timer)
  timer = setInterval(() => {
    if (timeLeft.value > 0 && phase.value === 'play') timeLeft.value--
    if (timeLeft.value <= 0 && phase.value === 'play') submitBuild()
  }, 1000)
}

function toggleComp(c) {
  if (phase.value !== 'play') return
  if (placed.value.includes(c.id)) {
    // Remove
    placed.value = placed.value.filter(id => id !== c.id)
    const sl = slots.value.find(s => s.comp?.id === c.id)
    if (sl) { sl.comp = null; sl.ok = false; sl.fail = false }
  } else {
    // Add to first empty slot
    const empty = slots.value.find(s => !s.comp)
    if (!empty) return
    empty.comp = c
    placed.value.push(c.id)
  }
}

function removeSlot(slot) {
  if (!slot.comp) return
  placed.value = placed.value.filter(id => id !== slot.comp.id)
  slot.comp = null; slot.ok = false; slot.fail = false
}

function submitBuild() {
  clearInterval(timer); phase.value = 'result'
  const req = curScenario.value.required
  let hit = 0
  const cIds = []; const wIds = []
  slots.value.forEach(s => {
    if (s.comp) {
      if (req.includes(s.comp.id)) { s.ok = true; hit++; cIds.push(s.comp.id) }
      else { s.fail = true; wIds.push(s.comp.id) }
    }
  })
  correctIds.value = cIds; wrongIds.value = wIds; correctHit.value = hit
  const base = hit * 50
  const perfect = hit === req.length ? 100 : 0
  const tBonus = timeLeft.value * 2
  const cBonus = comboVal.value * 15
  lastPts.value = base + perfect + tBonus + cBonus
  score.value += lastPts.value
  if (hit === req.length) {
    perfectCount.value++; comboVal.value++; maxCombo.value = Math.max(maxCombo.value, comboVal.value)
    flashOk.value = true; setTimeout(() => flashOk.value = false, 400)
    spawnPop(lastPts.value)
  } else {
    comboVal.value = 0
    shaking.value = true; setTimeout(() => shaking.value = false, 300)
    flashFail.value = true; setTimeout(() => flashFail.value = false, 400)
  }
}

function getHint() {
  if (hints.value >= 2) return
  hintText.value = curScenario.value.hints[hints.value] || ''
  hints.value++
}

function spawnPop(v) {
  const id = ++fpopId
  fpops.value.push({ id, v, style: { left: (35 + Math.random() * 30) + '%' } })
  setTimeout(() => { fpops.value = fpops.value.filter(f => f.id !== id) }, 1200)
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;600;700&display=swap');

.arcade-builder { min-height:100vh; background:#030712; color:#e0f2fe; font-family:'Rajdhani',sans-serif; position:relative; overflow:hidden; }
.crt-lines { pointer-events:none; position:fixed; inset:0; z-index:9999; background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,240,255,0.012) 2px,rgba(0,240,255,0.012) 4px); }
.screen-shake { animation:shake .3s ease; }
.flash-ok::after { content:''; position:fixed; inset:0; background:rgba(57,255,20,.12); z-index:9000; pointer-events:none; animation:flashOut .4s forwards; }
.flash-fail::after { content:''; position:fixed; inset:0; background:rgba(255,45,117,.12); z-index:9000; pointer-events:none; animation:flashOut .4s forwards; }
@keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-5px)} 75%{transform:translateX(5px)} }
@keyframes flashOut { from{opacity:1} to{opacity:0} }

.glitch { position:relative; font-family:'Orbitron',sans-serif; }
.glitch::before,.glitch::after { content:attr(data-text); position:absolute; top:0; left:0; width:100%; height:100%; }
.glitch::before { color:#ff2d75; clip-path:inset(0 0 65% 0); animation:g1 2s infinite linear alternate-reverse; }
.glitch::after { color:#39ff14; clip-path:inset(65% 0 0 0); animation:g2 2s infinite linear alternate-reverse; }
@keyframes g1 { 0%{transform:translate(0)} 50%{transform:translate(-3px,2px)} 100%{transform:translate(0)} }
@keyframes g2 { 0%{transform:translate(0)} 50%{transform:translate(3px,-2px)} 100%{transform:translate(0)} }

.neon-c { color:#00f0ff; text-shadow:0 0 8px #00f0ff; }
.neon-y { color:#ffe600; text-shadow:0 0 8px rgba(255,230,0,.5); }
.neon-fire { color:#ff6b2b; text-shadow:0 0 8px rgba(255,107,43,.5); }

/* INTRO */
.intro-screen { display:flex; align-items:center; justify-content:center; min-height:100vh; }
.intro-box { text-align:center; background:rgba(8,12,30,.85); border:2px solid #00f0ff; border-radius:1.5rem; padding:3rem 4rem; box-shadow:0 0 40px rgba(0,240,255,.12); }
.intro-title { font-size:3.5rem; font-weight:900; color:#00f0ff; letter-spacing:6px; text-shadow:0 0 20px #00f0ff,0 0 60px rgba(0,240,255,.3); }
.intro-sub { color:#94a3b8; margin:.5rem 0 1.5rem; letter-spacing:3px; }
.intro-how p { font-size:.85rem; color:#64748b; margin:.3rem 0; }
.btn-start { margin-top:1.5rem; padding:.9rem 2.5rem; font-family:'Orbitron',sans-serif; font-size:1rem; font-weight:700; background:transparent; border:2px solid #ffe600; color:#ffe600; border-radius:.5rem; cursor:pointer; letter-spacing:3px; transition:all .2s; }
.btn-start:hover { background:rgba(255,230,0,.08); box-shadow:0 0 25px rgba(255,230,0,.3); transform:scale(1.05); }
.blink-border { animation:blinkB 1.5s infinite; }
@keyframes blinkB { 0%,100%{border-color:#ffe600} 50%{border-color:rgba(255,230,0,.3)} }

/* HUD */
.hud { display:flex; align-items:center; gap:1.5rem; padding:.7rem 1.5rem; margin:1rem 1.5rem 0; background:rgba(8,12,30,.85); border:1px solid rgba(0,240,255,.1); border-radius:1rem; }
.hud-cell { display:flex; flex-direction:column; align-items:center; }
.hud-lbl { font-size:.55rem; font-weight:700; color:#475569; letter-spacing:2px; }
.hud-num { font-family:'Orbitron',sans-serif; font-size:1.5rem; font-weight:900; animation:popB .3s ease; }
.hud-dim { color:#334155; font-size:.8rem; }
@keyframes popB { 0%{transform:scale(1)} 50%{transform:scale(1.25)} 100%{transform:scale(1)} }

.timer-cell { flex:1; }
.timer-bar-track { width:100%; height:6px; background:#0f172a; border-radius:3px; overflow:hidden; }
.timer-bar-fill { height:100%; background:linear-gradient(90deg,#00f0ff,#38bdf8); border-radius:3px; transition:width 1s linear; }
.timer-cell.danger .timer-bar-fill { background:linear-gradient(90deg,#ff2d75,#ef4444); }
.timer-num { font-family:'Orbitron',sans-serif; font-size:.75rem; color:#94a3b8; margin-top:2px; }
.timer-cell.danger .timer-num { color:#ff2d75; animation:blinkA .5s infinite; }
@keyframes blinkA { 50%{opacity:.3} }

.combo-pill { font-family:'Orbitron',sans-serif; font-size:.8rem; font-weight:700; padding:.2rem .6rem; border:1px solid currentColor; border-radius:.3rem; animation:comboIn .4s ease; }
@keyframes comboIn { from{transform:scale(0) rotate(-15deg); opacity:0} to{transform:scale(1) rotate(0); opacity:1} }

/* SCENARIO */
.scenario-banner { display:flex; align-items:center; gap:1rem; margin:.75rem 1.5rem; padding:.8rem 1.2rem; background:rgba(8,12,30,.7); border:1px solid rgba(0,240,255,.08); border-radius:.75rem; }
.s-icon { font-size:1.8rem; }
.s-info { display:flex; flex-direction:column; gap:.1rem; flex:1; }
.s-info strong { font-size:1rem; }
.s-info span { font-size:.8rem; color:#64748b; }
.s-need { display:flex; flex-direction:column; align-items:center; }
.need-label { font-size:.55rem; color:#475569; font-weight:700; letter-spacing:1.5px; }
.need-count { font-family:'Orbitron',sans-serif; font-size:1.8rem; font-weight:900; }

/* BUILD AREA */
.build-area { display:grid; grid-template-columns:300px 1fr; gap:1rem; padding:0 1.5rem 1.5rem; height:calc(100vh - 200px); min-height:0; }

.tray { display:flex; flex-direction:column; gap:.75rem; background:rgba(8,12,30,.6); border:1px solid rgba(0,240,255,.06); border-radius:1rem; padding:1rem; overflow-y:auto; }
.tray-title { font-family:'Orbitron',sans-serif; font-size:.7rem; color:#475569; letter-spacing:2px; }
.tray-grid { display:flex; flex-wrap:wrap; gap:.4rem; }

.comp-btn {
  display:flex; align-items:center; gap:.3rem; padding:.45rem .7rem; border-radius:.4rem;
  background:#0a0f1e; border:1.5px solid #1e293b; color:#cbd5e1; font-size:.8rem; font-weight:600;
  cursor:pointer; transition:all .15s; font-family:inherit;
}
.comp-btn:hover:not(:disabled) { border-color:#00f0ff; background:rgba(0,240,255,.04); transform:translateY(-2px); box-shadow:0 4px 12px rgba(0,240,255,.1); }
.comp-btn.selected { border-color:#38bdf8; background:rgba(56,189,248,.08); color:#38bdf8; }
.comp-btn.correct { border-color:#39ff14; background:rgba(57,255,20,.08); color:#39ff14; animation:correctPulse .4s; }
.comp-btn.wrong { border-color:#ff2d75; background:rgba(255,45,117,.08); color:#ff2d75; animation:shake .3s; }
.comp-btn:disabled { opacity:.5; cursor:not-allowed; }
@keyframes correctPulse { 0%{box-shadow:0 0 0 0 rgba(57,255,20,.4)} 100%{box-shadow:0 0 0 10px rgba(57,255,20,0)} }

.cb-icon { font-size:1rem; }

.hint-box { background:rgba(255,230,0,.06); border:1px solid rgba(255,230,0,.15); border-radius:.4rem; padding:.5rem .6rem; font-size:.8rem; color:#fde68a; }
.btn-hint { padding:.4rem; background:rgba(255,230,0,.06); border:1px solid rgba(255,230,0,.15); color:#ffe600; border-radius:.4rem; font-family:'Orbitron',sans-serif; font-size:.6rem; font-weight:700; cursor:pointer; letter-spacing:1px; }
.btn-hint:disabled { opacity:.3; cursor:not-allowed; }

/* BOARD */
.board { display:flex; flex-direction:column; gap:.75rem; background:rgba(8,12,30,.4); border:2px dashed rgba(0,240,255,.12); border-radius:1rem; padding:1.25rem; }
.board-title { font-family:'Orbitron',sans-serif; font-size:.7rem; color:#475569; letter-spacing:2px; text-align:center; }
.board-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:.75rem; flex:1; }

.board-slot {
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap:.3rem;
  background:#080c1e; border:1.5px dashed #1e293b; border-radius:.75rem; min-height:80px;
  padding:.75rem; position:relative; transition:all .25s;
}
.board-slot.filled { border-style:solid; border-color:#334155; }
.board-slot.correct { border-color:#39ff14; background:rgba(57,255,20,.06); animation:correctPulse .5s; }
.board-slot.wrong { border-color:#ff2d75; background:rgba(255,45,117,.06); animation:shake .3s; }
.bs-icon { font-size:1.4rem; }
.bs-name { font-size:.75rem; font-weight:600; }
.bs-label { font-size:.7rem; color:#334155; }
.bs-remove { position:absolute; top:4px; right:4px; width:18px; height:18px; background:rgba(255,45,117,.15); border:none; color:#ff2d75; border-radius:50%; cursor:pointer; font-size:.6rem; display:flex; align-items:center; justify-content:center; }

.btn-submit {
  padding:.8rem; font-family:'Orbitron',sans-serif; font-size:.9rem; font-weight:700; letter-spacing:2px;
  background:transparent; border:2px solid #00f0ff; color:#00f0ff; border-radius:.75rem; cursor:pointer; transition:all .2s;
}
.btn-submit:hover:not(:disabled) { background:rgba(0,240,255,.08); box-shadow:0 0 20px rgba(0,240,255,.2); transform:translateY(-2px); }
.btn-submit:disabled { border-color:#1e293b; color:#334155; cursor:not-allowed; }

/* OVERLAYS */
.overlay { position:fixed; inset:0; background:rgba(0,0,0,.7); backdrop-filter:blur(4px); display:flex; align-items:center; justify-content:center; z-index:100; }
.dark-overlay { background:rgba(0,0,0,.9); }

.result-box { background:rgba(8,12,30,.95); border:2px solid; border-radius:1.5rem; padding:2.5rem; text-align:center; max-width:400px; width:90%; }
.res-perfect { border-color:#39ff14; box-shadow:0 0 30px rgba(57,255,20,.12); }
.res-partial { border-color:#ffe600; box-shadow:0 0 30px rgba(255,230,0,.1); }
.res-miss { border-color:#ff2d75; box-shadow:0 0 30px rgba(255,45,117,.1); }
.r-icon { font-size:3rem; }
.r-title { font-family:'Orbitron',sans-serif; font-size:2rem; font-weight:900; margin:.3rem 0; }
.res-perfect .r-title { color:#39ff14; text-shadow:0 0 15px rgba(57,255,20,.4); }
.res-partial .r-title { color:#ffe600; }
.res-miss .r-title { color:#ff2d75; }
.r-detail { color:#94a3b8; font-size:.9rem; }
.r-pts { font-family:'Orbitron',sans-serif; font-size:2rem; font-weight:900; color:#ffe600; text-shadow:0 0 10px rgba(255,230,0,.4); margin:.5rem 0; }
.r-explain { font-size:.8rem; color:#475569; margin-bottom:1rem; }
.btn-next { width:100%; padding:.8rem; font-family:'Orbitron',sans-serif; font-size:.85rem; font-weight:700; background:transparent; border:2px solid #00f0ff; color:#00f0ff; border-radius:.75rem; cursor:pointer; letter-spacing:2px; transition:all .2s; }
.btn-next:hover { background:rgba(0,240,255,.08); transform:translateY(-2px); }

/* GAME OVER */
.go-box { text-align:center; }
.go-title { font-size:3rem; font-weight:900; color:#00f0ff; letter-spacing:4px; margin-bottom:1rem; }
.go-grade { font-family:'Orbitron',sans-serif; font-size:5rem; font-weight:900; }
.g-S { color:#ffe600; text-shadow:0 0 30px rgba(255,230,0,.5); } .g-A { color:#00f0ff; } .g-B { color:#39ff14; } .g-C { color:#64748b; }
.go-score { font-family:'Orbitron',sans-serif; font-size:2.5rem; font-weight:900; color:#f1f5f9; }
.go-score small { font-size:1rem; color:#475569; }
.go-row { display:flex; justify-content:center; gap:2rem; margin:1rem 0; font-size:.85rem; color:#64748b; }
.go-btns { display:flex; gap:1rem; margin-top:1rem; }
.btn-retry,.btn-exit { flex:1; padding:.75rem; font-family:'Orbitron',sans-serif; font-size:.8rem; font-weight:700; border-radius:.75rem; cursor:pointer; letter-spacing:1px; transition:all .2s; }
.btn-retry { background:transparent; border:2px solid #00f0ff; color:#00f0ff; }
.btn-retry:hover { background:rgba(0,240,255,.1); }
.btn-exit { background:transparent; border:1px solid #334155; color:#64748b; }

/* FLOAT POP */
.fpop-layer { position:fixed; inset:0; pointer-events:none; z-index:500; }
.fpop-item { position:absolute; top:40%; font-family:'Orbitron',sans-serif; font-size:1.4rem; font-weight:900; color:#ffe600; text-shadow:0 0 10px rgba(255,230,0,.5); }
.fpop-enter-active { animation:fUp 1.2s ease-out forwards; }
@keyframes fUp { 0%{opacity:1;transform:translateY(0) scale(1.2)} 100%{opacity:0;transform:translateY(-90px) scale(.8)} }

.zoom-enter-active { animation:zIn .3s ease; }
@keyframes zIn { from{transform:scale(.7);opacity:0} to{transform:scale(1);opacity:1} }
</style>
