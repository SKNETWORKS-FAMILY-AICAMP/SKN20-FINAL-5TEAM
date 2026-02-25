<template>
  <div class="arcade-battle" :class="{ 'screen-shake': shaking, 'flash-win': flashWin, 'flash-lose': flashLose }">
    <div class="crt-lines"></div>

    <!-- INTRO -->
    <div v-if="phase === 'intro'" class="intro-screen">
      <div class="intro-box">
        <h1 class="intro-title glitch" data-text="ARCH BATTLE">ARCH BATTLE</h1>
        <p class="intro-sub">1:1 아키텍처 배틀</p>
        <div class="vs-art">
          <span class="vs-you">YOU</span>
          <span class="vs-icon">⚔️</span>
          <span class="vs-ai">AI</span>
        </div>
        <div class="intro-how">
          <p>📋 같은 장애 시나리오를 동시에 받습니다</p>
          <p>✍️ 아키텍처 해결책을 작성하세요</p>
          <p>🧑‍⚖️ AI 심판이 양쪽을 비교 채점합니다</p>
        </div>
        <button @click="startGame" class="btn-start blink-border">▶ FIGHT!</button>
      </div>
    </div>

    <!-- GAME -->
    <div v-if="phase === 'play' || phase === 'judging'" class="game-view">
      <div class="hud">
        <div class="hud-cell">
          <span class="hud-lbl">ROUND</span>
          <span class="hud-num neon-c">{{ round }}<span class="hud-dim">/{{ maxRounds }}</span></span>
        </div>
        <div class="hud-cell vs-scores">
          <div class="vs-sc"><span class="vs-tag you-tag">YOU</span><span class="hud-num" :class="{ 'neon-y': myTotal > aiTotal }">{{ myTotal }}</span></div>
          <span class="vs-colon">:</span>
          <div class="vs-sc"><span class="vs-tag ai-tag2">AI</span><span class="hud-num" :class="{ 'neon-fire': aiTotal > myTotal }">{{ aiTotal }}</span></div>
        </div>
        <div class="hud-cell timer-cell" :class="{ danger: timerDanger }">
          <span class="timer-num">{{ timeLeft }}s</span>
          <div class="timer-track"><div class="timer-fill" :style="{ width: timerPct + '%' }"></div></div>
        </div>
      </div>

      <div class="scenario-strip" v-if="curScenario">
        <span class="s-ico">{{ curScenario.icon }}</span>
        <div><strong>{{ curScenario.title }}</strong><br/><span class="s-desc">{{ curScenario.prompt }}</span></div>
      </div>

      <div class="split-area">
        <div class="side my-side">
          <div class="side-hdr"><span class="vs-tag you-tag">YOUR ANSWER</span></div>
          <textarea v-model="myText" class="editor" :disabled="phase !== 'play'"
            placeholder="아키텍처를 설명하세요...&#10;&#10;예: 로드밸런서로 트래픽 분산, Redis 캐시 배치..."></textarea>
          <div class="hint-row" v-if="hintMsg"><span>💡</span> {{ hintMsg }}</div>
          <button @click="getHint" class="btn-hint" :disabled="hintN >= 2 || phase !== 'play'">💡 HINT ({{ 2 - hintN }})</button>
        </div>
        <div class="divider"><div class="div-line"></div><span class="div-icon">⚔️</span><div class="div-line"></div></div>
        <div class="side">
          <div class="side-hdr"><span class="vs-tag ai-tag2">AI ANSWER</span></div>
          <div class="ai-display">
            <div v-if="phase === 'play'" class="typing-ind"><span></span><span></span><span></span> AI도 설계 중...</div>
            <p v-else class="ai-text">{{ aiText }}</p>
          </div>
        </div>
      </div>

      <div class="submit-row" v-if="phase === 'play'">
        <button @click="submit" class="btn-fight" :disabled="!myText.trim()">⚔️ SUBMIT</button>
      </div>
    </div>

    <!-- JUDGING -->
    <transition name="zoom">
      <div v-if="phase === 'judging'" class="overlay">
        <div class="judge-box"><div class="spinner"></div><p>🧑‍⚖️ AI JUDGING...</p></div>
      </div>
    </transition>

    <!-- ROUND RESULT -->
    <transition name="zoom">
      <div v-if="phase === 'result'" class="overlay">
        <div class="result-box" :class="winnerClass">
          <div class="r-ico">{{ winnerEmoji }}</div>
          <div class="r-title">{{ winnerLabel }}</div>
          <div class="judge-comment"><h4>🧑‍⚖️ 심판 코멘트</h4><p>{{ comment }}</p></div>
          <div class="r-scores">
            <div class="r-sc"><span>YOU</span><strong class="neon-c">{{ roundMy }}pt</strong></div>
            <div class="r-sc"><span>AI</span><strong>{{ roundAi }}pt</strong></div>
          </div>
          <button @click="nextRound" class="btn-next">{{ nextLabel }}</button>
        </div>
      </div>
    </transition>

    <!-- GAME OVER -->
    <transition name="zoom">
      <div v-if="phase === 'gameover'" class="overlay dark-ov">
        <div class="go-box">
          <div class="go-emoji">{{ goEmoji }}</div>
          <h1 class="go-title glitch" :data-text="goTitle">{{ goTitle }}</h1>
          <div class="go-scores">
            <div class="go-fs"><span>YOU</span><strong>{{ myTotal }}</strong></div>
            <span class="go-vs">VS</span>
            <div class="go-fs"><span>AI</span><strong>{{ aiTotal }}</strong></div>
          </div>
          <div class="go-btns">
            <button @click="startGame" class="btn-retry">🔄 REMATCH</button>
            <button @click="$router.push('/practice/coduck-wars')" class="btn-exit">🏠 EXIT</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import axios from 'axios'

const phase = ref('intro')
const round = ref(0)
const maxRounds = 5
const timeLeft = ref(60)
const myTotal = ref(0)
const aiTotal = ref(0)
const myText = ref('')
const aiText = ref('')
const hintMsg = ref('')
const hintN = ref(0)
const roundMy = ref(0)
const roundAi = ref(0)
const comment = ref('')
const shaking = ref(false)
const flashWin = ref(false)
const flashLose = ref(false)
let timer = null

const timerPct = computed(() => (timeLeft.value / 60) * 100)
const timerDanger = computed(() => timeLeft.value <= 15)
const nextLabel = computed(() => round.value >= maxRounds ? 'SEE RESULTS' : 'NEXT ▶')

const winnerClass = computed(() => { if (roundMy.value > roundAi.value) return 'res-win'; if (roundMy.value === roundAi.value) return 'res-draw'; return 'res-lose' })
const winnerEmoji = computed(() => { if (roundMy.value > roundAi.value) return '🎉'; if (roundMy.value === roundAi.value) return '🤝'; return '😤' })
const winnerLabel = computed(() => { if (roundMy.value > roundAi.value) return 'YOU WIN!'; if (roundMy.value === roundAi.value) return 'DRAW'; return 'AI WINS' })
const goEmoji = computed(() => { if (myTotal.value > aiTotal.value) return '🏆'; if (myTotal.value === aiTotal.value) return '🤝'; return '💪' })
const goTitle = computed(() => { if (myTotal.value > aiTotal.value) return 'VICTORY'; if (myTotal.value === aiTotal.value) return 'DRAW'; return 'DEFEAT' })

const allScenarios = [
  { icon:'🔥', title:'트래픽 폭주', prompt:'API 서버 트래픽 10배 급증! 대응 아키텍처를 설계하세요.', hints:['수평 확장','캐시+CDN'], aiAns:'ALB 로드밸런서로 분산, Redis 캐시 도입, CloudFront CDN, Auto Scaling Group(CPU 70% 확장), Read Replica 읽기 분산.' },
  { icon:'💀', title:'DB 장애 복구', prompt:'메인 DB 다운! 무중단 복구 전략을 세우세요.', hints:['Multi-AZ','Failover'], aiAns:'Multi-AZ RDS 자동 Failover, Read Replica 읽기 할당, PgBouncer 커넥션 풀링, Route53 헬스체크 DNS 전환.' },
  { icon:'🛡️', title:'DDoS 방어', prompt:'대규모 DDoS 공격! 방어 아키텍처를 설계하세요.', hints:['WAF 배치','Rate Limiting'], aiAns:'CloudFront+WAF 앞단 배치, IP당 Rate Limiting, Shield Advanced L3/L4 방어, API Gateway throttling.' },
  { icon:'📈', title:'실시간 랭킹', prompt:'100만 유저 실시간 랭킹 시스템을 설계하세요.', hints:['Redis Sorted Set','캐시 전략'], aiAns:'Redis Sorted Set 실시간 점수, Write-Behind 캐시 DB 동기화, Sharding 수평 확장, WebSocket push.' },
  { icon:'🔔', title:'대규모 알림', prompt:'하루 1억 건 푸시 알림 시스템을 설계하세요.', hints:['메시지큐 필수','배치 처리'], aiAns:'Kafka 이벤트 수집, Consumer Group 병렬 처리, SQS+Lambda 분기, FCM/APNs 전달, DLQ 실패 관리.' },
]

const scenarios = ref([])
const curScenario = computed(() => scenarios.value[round.value - 1])

onUnmounted(() => clearInterval(timer))

function startGame() {
  scenarios.value = [...allScenarios].sort(() => Math.random() - 0.5).slice(0, maxRounds)
  myTotal.value = 0; aiTotal.value = 0; round.value = 0
  nextRound()
}

function nextRound() {
  round.value++
  if (round.value > maxRounds) { phase.value = 'gameover'; return }
  phase.value = 'play'; timeLeft.value = 60; myText.value = ''; aiText.value = ''; hintMsg.value = ''; hintN.value = 0
  clearInterval(timer)
  timer = setInterval(() => {
    if (timeLeft.value > 0 && phase.value === 'play') timeLeft.value--
    if (timeLeft.value <= 0 && phase.value === 'play') submit()
  }, 1000)
}

function getHint() {
  if (hintN.value >= 2) return
  hintMsg.value = curScenario.value.hints[hintN.value] || ''
  hintN.value++
}

async function submit() {
  clearInterval(timer); phase.value = 'judging'
  aiText.value = curScenario.value.aiAns
  try {
    const res = await axios.post('/api/core/wars/battle-judge/', { scenario: curScenario.value.prompt, player_answer: myText.value || '(미작성)', ai_answer: aiText.value })
    if (res.data?.status === 'success') { const j = res.data.judgment; roundMy.value = j.player_score || 0; roundAi.value = j.ai_score || 0; comment.value = j.comment || '양측 합리적.' }
    else { localJudge() }
  } catch { localJudge() }
  myTotal.value += roundMy.value; aiTotal.value += roundAi.value
  if (roundMy.value > roundAi.value) { flashWin.value = true; setTimeout(() => flashWin.value = false, 400) }
  else if (roundMy.value < roundAi.value) { shaking.value = true; flashLose.value = true; setTimeout(() => { shaking.value = false; flashLose.value = false }, 400) }
  phase.value = 'result'
}

function localJudge() {
  const kw = ['로드밸런서','캐시','redis','cdn','replica','failover','waf','rate limit','scaling','kafka','queue','websocket','shard','gateway','multi-az']
  const hits = kw.filter(k => myText.value.toLowerCase().includes(k)).length
  const lenScore = Math.min(30, Math.round(myText.value.length / 15))
  roundMy.value = Math.min(100, hits * 12 + lenScore + (timeLeft.value > 30 ? 10 : 0))
  roundAi.value = 65 + Math.floor(Math.random() * 20)
  comment.value = roundMy.value >= roundAi.value ? '핵심 컴포넌트를 잘 파악했습니다!' : 'AI가 더 체계적인 설계를 제시했습니다. 핵심 컴포넌트를 빠짐없이 언급해보세요.'
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;600;700&display=swap');
.arcade-battle { min-height:100vh; background:#030712; color:#e0f2fe; font-family:'Rajdhani',sans-serif; position:relative; overflow:hidden; }
.crt-lines { pointer-events:none; position:fixed; inset:0; z-index:9999; background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,240,255,.012) 2px,rgba(0,240,255,.012) 4px); }
.screen-shake { animation:shake .3s ease; }
.flash-win::after { content:''; position:fixed; inset:0; background:rgba(57,255,20,.12); z-index:9000; pointer-events:none; animation:fo .4s forwards; }
.flash-lose::after { content:''; position:fixed; inset:0; background:rgba(255,45,117,.12); z-index:9000; pointer-events:none; animation:fo .4s forwards; }
@keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-5px)} 75%{transform:translateX(5px)} }
@keyframes fo { from{opacity:1} to{opacity:0} }
.glitch { position:relative; font-family:'Orbitron',sans-serif; }
.glitch::before,.glitch::after { content:attr(data-text); position:absolute; top:0; left:0; width:100%; height:100%; }
.glitch::before { color:#ff2d75; clip-path:inset(0 0 65% 0); animation:g1 2s infinite linear alternate-reverse; }
.glitch::after { color:#39ff14; clip-path:inset(65% 0 0 0); animation:g2 2s infinite linear alternate-reverse; }
@keyframes g1 { 0%{transform:translate(0)} 50%{transform:translate(-3px,2px)} 100%{transform:translate(0)} }
@keyframes g2 { 0%{transform:translate(0)} 50%{transform:translate(3px,-2px)} 100%{transform:translate(0)} }
.neon-c { color:#00f0ff; text-shadow:0 0 8px #00f0ff; }
.neon-y { color:#ffe600; text-shadow:0 0 8px rgba(255,230,0,.5); }
.neon-fire { color:#ff6b2b; text-shadow:0 0 8px rgba(255,107,43,.5); }

.intro-screen { display:flex; align-items:center; justify-content:center; min-height:100vh; }
.intro-box { text-align:center; background:rgba(8,12,30,.85); border:2px solid #ff2d75; border-radius:1.5rem; padding:3rem 4rem; box-shadow:0 0 40px rgba(255,45,117,.12); }
.intro-title { font-size:3.5rem; font-weight:900; color:#ff2d75; letter-spacing:6px; text-shadow:0 0 20px #ff2d75; }
.intro-sub { color:#94a3b8; margin:.5rem 0 1.5rem; letter-spacing:3px; }
.vs-art { display:flex; align-items:center; justify-content:center; gap:1.5rem; margin:1.5rem 0; font-family:'Orbitron',sans-serif; font-size:1.2rem; font-weight:700; }
.vs-you { color:#00f0ff; } .vs-ai { color:#ff2d75; } .vs-icon { font-size:2rem; }
.intro-how p { font-size:.85rem; color:#64748b; margin:.3rem 0; }
.btn-start { margin-top:1.5rem; padding:.9rem 2.5rem; font-family:'Orbitron',sans-serif; font-size:1rem; font-weight:700; background:transparent; border:2px solid #ff2d75; color:#ff2d75; border-radius:.5rem; cursor:pointer; letter-spacing:3px; transition:all .2s; }
.btn-start:hover { background:rgba(255,45,117,.08); box-shadow:0 0 25px rgba(255,45,117,.3); transform:scale(1.05); }
.blink-border { animation:bb 1.5s infinite; }
@keyframes bb { 0%,100%{border-color:#ff2d75} 50%{border-color:rgba(255,45,117,.3)} }

.hud { display:flex; align-items:center; gap:1.5rem; padding:.7rem 1.5rem; margin:1rem 1.5rem 0; background:rgba(8,12,30,.85); border:1px solid rgba(255,45,117,.1); border-radius:1rem; }
.hud-cell { display:flex; flex-direction:column; align-items:center; }
.hud-lbl { font-size:.55rem; font-weight:700; color:#475569; letter-spacing:2px; }
.hud-num { font-family:'Orbitron',sans-serif; font-size:1.4rem; font-weight:900; }
.hud-dim { color:#334155; font-size:.8rem; }
.vs-scores { flex-direction:row; gap:.75rem; align-items:center; }
.vs-sc { display:flex; flex-direction:column; align-items:center; }
.vs-tag { font-family:'Orbitron',sans-serif; font-size:.5rem; font-weight:700; padding:1px 6px; border-radius:2px; letter-spacing:1px; }
.you-tag { background:rgba(0,240,255,.1); color:#00f0ff; }
.ai-tag2 { background:rgba(255,45,117,.1); color:#ff2d75; }
.vs-colon { font-family:'Orbitron',sans-serif; font-size:1.2rem; color:#334155; }
.timer-cell { flex:1; align-items:stretch; gap:2px; }
.timer-track { width:100%; height:5px; background:#0f172a; border-radius:3px; overflow:hidden; }
.timer-fill { height:100%; background:linear-gradient(90deg,#ff2d75,#ff6b2b); transition:width 1s linear; border-radius:3px; }
.timer-cell.danger .timer-fill { background:#ef4444; }
.timer-num { font-family:'Orbitron',sans-serif; font-size:.75rem; color:#94a3b8; text-align:center; }
.timer-cell.danger .timer-num { color:#ff2d75; animation:bla .5s infinite; }
@keyframes bla { 50%{opacity:.3} }

.scenario-strip { display:flex; align-items:center; gap:1rem; margin:.75rem 1.5rem; padding:.8rem 1.2rem; background:rgba(8,12,30,.7); border:1px solid rgba(255,45,117,.1); border-radius:.75rem; }
.s-ico { font-size:1.8rem; }
.s-desc { font-size:.8rem; color:#64748b; }

.split-area { display:grid; grid-template-columns:1fr 40px 1fr; gap:0; padding:0 1.5rem; height:calc(100vh - 230px); min-height:0; }
.side { display:flex; flex-direction:column; gap:.5rem; background:rgba(8,12,30,.5); border:1px solid rgba(255,255,255,.04); border-radius:1rem; padding:1rem; }
.side-hdr { font-size:.8rem; }
.editor { flex:1; background:#0a0f1e; border:1.5px solid #1e293b; border-radius:.75rem; color:#f1f5f9; padding:1rem; font-family:'Rajdhani',sans-serif; font-size:.95rem; font-weight:600; resize:none; outline:none; line-height:1.6; }
.editor:focus { border-color:#00f0ff; box-shadow:0 0 12px rgba(0,240,255,.1); }
.editor:disabled { opacity:.4; }
.ai-display { flex:1; background:#0a0f1e; border:1.5px solid #1e293b; border-radius:.75rem; padding:1rem; overflow-y:auto; }
.typing-ind { display:flex; align-items:center; gap:.3rem; color:#475569; font-style:italic; }
.typing-ind span { width:5px; height:5px; background:#475569; border-radius:50%; animation:dt 1.2s infinite; }
.typing-ind span:nth-child(2) { animation-delay:.2s; }
.typing-ind span:nth-child(3) { animation-delay:.4s; }
@keyframes dt { 0%,100%{opacity:.3} 50%{opacity:1} }
.ai-text { color:#cbd5e1; line-height:1.6; font-size:.9rem; }
.hint-row { background:rgba(255,230,0,.06); border:1px solid rgba(255,230,0,.15); border-radius:.4rem; padding:.4rem .6rem; font-size:.8rem; color:#fde68a; }
.btn-hint { align-self:flex-start; padding:.35rem .7rem; background:rgba(255,230,0,.06); border:1px solid rgba(255,230,0,.15); color:#ffe600; border-radius:.3rem; font-family:'Orbitron',sans-serif; font-size:.55rem; font-weight:700; cursor:pointer; }
.btn-hint:disabled { opacity:.3; cursor:not-allowed; }
.divider { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:.4rem; }
.div-line { width:2px; flex:1; background:linear-gradient(to bottom,transparent,#334155,transparent); }
.div-icon { font-size:1.2rem; }
.submit-row { display:flex; justify-content:center; padding:.75rem 1.5rem; }
.btn-fight { padding:.9rem 3rem; font-family:'Orbitron',sans-serif; font-size:1rem; font-weight:700; background:transparent; border:2px solid #ff2d75; color:#ff2d75; border-radius:.75rem; cursor:pointer; letter-spacing:2px; transition:all .2s; }
.btn-fight:hover:not(:disabled) { background:rgba(255,45,117,.08); box-shadow:0 0 25px rgba(255,45,117,.3); transform:translateY(-3px); }
.btn-fight:disabled { border-color:#1e293b; color:#334155; cursor:not-allowed; }

.overlay { position:fixed; inset:0; background:rgba(0,0,0,.75); backdrop-filter:blur(4px); display:flex; align-items:center; justify-content:center; z-index:100; }
.dark-ov { background:rgba(0,0,0,.9); }
.judge-box { text-align:center; color:#94a3b8; }
.spinner { width:36px; height:36px; border:3px solid #1e293b; border-top-color:#00f0ff; border-radius:50%; animation:spin .8s linear infinite; margin:0 auto 1rem; }
@keyframes spin { to{transform:rotate(360deg)} }

.result-box { background:rgba(8,12,30,.95); border:2px solid; border-radius:1.5rem; padding:2.5rem; text-align:center; max-width:440px; width:90%; }
.res-win { border-color:#39ff14; box-shadow:0 0 30px rgba(57,255,20,.12); }
.res-draw { border-color:#ffe600; box-shadow:0 0 30px rgba(255,230,0,.1); }
.res-lose { border-color:#ff2d75; box-shadow:0 0 30px rgba(255,45,117,.1); }
.r-ico { font-size:3rem; }
.r-title { font-family:'Orbitron',sans-serif; font-size:2rem; font-weight:900; margin:.3rem 0; }
.res-win .r-title { color:#39ff14; text-shadow:0 0 15px rgba(57,255,20,.4); }
.res-draw .r-title { color:#ffe600; }
.res-lose .r-title { color:#ff2d75; }
.judge-comment { background:rgba(15,23,42,.5); border-radius:.75rem; padding:.8rem; margin:1rem 0; text-align:left; }
.judge-comment h4 { font-size:.75rem; color:#64748b; margin-bottom:.3rem; }
.judge-comment p { font-size:.85rem; color:#cbd5e1; line-height:1.5; }
.r-scores { display:flex; justify-content:center; gap:2rem; margin:.75rem 0; }
.r-sc { display:flex; flex-direction:column; align-items:center; gap:.2rem; }
.r-sc span { font-size:.65rem; color:#475569; font-weight:700; letter-spacing:1px; }
.r-sc strong { font-family:'Orbitron',sans-serif; font-size:1.2rem; font-weight:900; }
.btn-next { width:100%; padding:.8rem; font-family:'Orbitron',sans-serif; font-size:.85rem; font-weight:700; background:transparent; border:2px solid #00f0ff; color:#00f0ff; border-radius:.75rem; cursor:pointer; letter-spacing:2px; transition:all .2s; }
.btn-next:hover { background:rgba(0,240,255,.08); transform:translateY(-2px); }

.go-box { text-align:center; }
.go-emoji { font-size:3rem; }
.go-title { font-size:3rem; font-weight:900; color:#ff2d75; letter-spacing:4px; margin:.5rem 0 1rem; }
.go-scores { display:flex; align-items:center; justify-content:center; gap:1.5rem; margin:1rem 0; }
.go-fs { display:flex; flex-direction:column; align-items:center; }
.go-fs span { font-size:.65rem; color:#475569; font-weight:700; }
.go-fs strong { font-family:'Orbitron',sans-serif; font-size:2.5rem; font-weight:900; color:#f1f5f9; }
.go-vs { font-family:'Orbitron',sans-serif; font-size:1rem; color:#ff2d75; font-weight:900; }
.go-btns { display:flex; gap:1rem; margin-top:1.5rem; }
.btn-retry { flex:1; padding:.75rem; font-family:'Orbitron',sans-serif; font-size:.8rem; font-weight:700; background:transparent; border:2px solid #ff2d75; color:#ff2d75; border-radius:.75rem; cursor:pointer; }
.btn-retry:hover { background:rgba(255,45,117,.1); }
.btn-exit { flex:1; padding:.75rem; font-family:'Orbitron',sans-serif; font-size:.8rem; font-weight:700; background:transparent; border:1px solid #334155; color:#64748b; border-radius:.75rem; cursor:pointer; }

.zoom-enter-active { animation:zIn .3s ease; }
@keyframes zIn { from{transform:scale(.7);opacity:0} to{transform:scale(1);opacity:1} }
</style>
