<template>
  <div class="bubble-game-container">
    <!-- 방 입장 화면 -->
    <div v-if="!bs.connected.value" class="join-screen">
      <h1>👾 Bug-Bubble Monster</h1>
      <p class="desc">방 번호를 입력하고 대결장에 입장하세요!</p>
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
      <p class="desc">코드를 풀고 버그를 방울에 가둬 상대에게 전송하세요!</p>
      
      <div class="players-box">
        <div class="player me">
          <span>{{ auth.sessionNickname || '나' }}</span>
        </div>
        <div class="vs">VS</div>
        <div class="player opponent">
          <span>{{ bs.opponentName.value || '상대 대기 중...' }}</span>
        </div>
      </div>

      <button 
        class="start-btn" 
        :disabled="!bs.isReady.value"
        @click="startGame"
      >
        {{ bs.isReady.value ? '게임 시작' : '대기 중...' }}
      </button>
    </div>

    <!-- 게임 결과 화면 -->
    <div v-else-if="bs.gameOver.value" class="result-screen">
      <h1 :class="{ win: isWinner, lose: !isWinner }">
        {{ isWinner ? '승리! 🎉' : '패배... 💀' }}
      </h1>
      <p>{{ isWinner ? '상대방의 화면이 버그로 가득 찼습니다!' : '나의 화면이 버그로 마비되었습니다.' }}</p>
      <button class="exit-btn" @click="router.push('/practice/coduck-wars')">로비로 돌아가기</button>
    </div>

    <!-- 플레이 화면 -->
    <div v-else class="play-screen" ref="playArea">
      <header class="game-header">
        <div class="player-panel me">
          <div class="avatar">
            <img v-if="auth.userAvatarUrl" :src="auth.userAvatarUrl" alt="My Avatar" />
            <span v-else>🦆</span>
          </div>
          <div class="info">
            <span class="name">{{ auth.sessionNickname || '나' }}</span>
            <span class="status" :class="{ danger: activeMonsters.length > 20 }">
              버그 👾: {{ activeMonsters.length }} / {{ maxMonsters }}
            </span>
            <span class="fever-gauge">콤보: {{ combo }}</span>
          </div>
        </div>
        
        <div class="center-console">
          <div class="vs-badge">⚡ V S ⚡</div>
          <span class="fever-gauge">콤보: {{ combo }}</span>
        </div>

        <div class="player-panel opp" ref="oppAvatarContainer">
          <div class="info right">
            <span class="name">{{ bs.opponentName.value }}</span>
            <span class="status" :class="{ danger: opponentMonsterCount > 20 }">
              버그 👾: {{ opponentMonsterCount }} / {{ maxMonsters }}
            </span>
          </div>
          <div class="avatar opp-avatar">
            <img v-if="bs.opponentAvatar.value" :src="bs.opponentAvatar.value" alt="Opponent Avatar" />
            <span v-else>🤖</span>
          </div>
        </div>
      </header>

      <!-- 중앙 1개의 공동 코딩 에디터 영역 -->
      <main class="battle-arena unified">
        
        <div class="editor-section">
          <div class="editor-header">
            <span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span>
            <span class="file-name">battle_ground.js</span>
          </div>
          <div class="editor-mockup">
            <div class="line" v-for="i in 15" :key="i">
              <span class="num">{{ i }}</span>
              <span class="code" v-html="dummyCode[i-1] || ''"></span>
            </div>
          </div>
        </div>

        <div class="action-panel">
          <button class="solve-btn" @click="solveTestcase">정답 제출! (버그 넘기기 🫧)</button>
          <button class="fever-btn" @click="solveAll" :disabled="combo < 3">완벽 해결! (폭탄 전송 �)</button>
        </div>
        
      </main>

      <!-- 투명 캔버스 오버레이 (버그 몬스터 표시 영역) -->
      <div class="monster-overlay">
        <!-- 돌아다니는 몬스터 -->
        <div 
          v-for="m in activeMonsters" 
          :key="m.id" 
          class="monster bug"
          :style="{ left: m.x + 'px', top: m.y + 'px', opacity: m.isMasking ? 0.2 : 1 }"
        >
          👾
        </div>
        <!-- 거품에 갇힌 몬스터 (전송 애니메이션용) -->
        <div 
          v-for="b in bubbledMonsters" 
          :key="b.id" 
          class="monster bubble flying"
          :style="{ left: b.x + 'px', top: b.y + 'px', transform: `translate(${b.targetX - b.x}px, ${b.targetY - b.y}px)` }"
        >
          🫧<span class="inner-bug">👾</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBubbleSocket } from '../composables/useBubbleSocket'

// === Stores & Routers ===
const router = useRouter()
const auth = useAuthStore()

// === Socket ===
const inputRoomId = ref('')
const currentRoomId = ref('')
const bs = useBubbleSocket()

// === Game State ===
const activeMonsters = ref([])
const bubbledMonsters = ref([])
const maxMonsters = 25
const opponentMonsterCount = ref(0) // 상대방 버그 숫자
const isWinner = ref(false)
const combo = ref(0)
let animationFrameId = null
const playArea = ref(null)
const oppAvatarContainer = ref(null) // 아바타 위치 추적용

const dummyCode = [
  "function <span style='color:#61afef'>calculateRank</span>(users) {",
  "  if (!users) return [];",
  "  return users.<span style='color:#61afef'>sort</span>((a, b) => b.score - a.score)",
  "    .<span style='color:#61afef'>map</span>((u, i) => ({ ...u, rank: i + 1 }));",
  "}",
  "",
  "const data = await <span style='color:#61afef'>fetchData</span>();",
  "const ranked = <span style='color:#61afef'>calculateRank</span>(data);",
  "console.<span style='color:#56b6c2'>log</span>(ranked);",
]

// === Lifecycle ===
onMounted(() => {
  // 컴포넌트 마운트 시 기본 소켓 이벤트 리스너 세팅
  bs.onGameStart.value = () => {
    // 게임 시작 시 양쪽에 초기 몬스터 스폰
    spawnMonsters(5)
    opponentMonsterCount.value = 5 // 초기 상대방 몬스터 동기화
    startGameLoop()
  }

  bs.onReceiveMonster.value = (data) => {
    // 상대가 나에게 보낸 몬스터 받기
    spawnMonsters(1)
  }
  
  // [추가] 상대방의 버그 개수 동기화 처리 (백엔드 개조 필요하지만, 여기서는 내가 넘긴 걸로 유추하거나 상대가 주는 이벤트 수신)
  // 임시로 내가 보낸 만큼 상대 값이 올라감
  bs.onReceiveFever.value = (data) => {
    spawnMonsters(data.count)
  }

  bs.onGameEnd.value = (result) => {
    cancelAnimationFrame(animationFrameId)
    isWinner.value = result.isWinner
  }
})

onUnmounted(() => {
  cancelAnimationFrame(animationFrameId)
  bs.disconnect()
})

// === Logics ===
function joinRoom() {
  if (!inputRoomId.value.trim()) return
  currentRoomId.value = inputRoomId.value.trim()
  bs.connect(currentRoomId.value, auth.sessionNickname || 'Anonymous', auth.userAvatarUrl)
}

function startGame() {
  bs.emitStart(currentRoomId.value)
}

function spawnMonsters(count) {
  for (let i = 0; i < count; i++) {
    const w = window.innerWidth * 0.4
    const h = window.innerHeight * 0.4
    activeMonsters.value.push({
      id: Date.now() + Math.random(),
      x: Math.random() * w + 50,
      y: Math.random() * h + 50,
      dx: (Math.random() - 0.5) * 4,
      dy: (Math.random() - 0.5) * 4,
      isMasking: false // 방해 모드 여부
    })
  }
  checkGameOver()
}

function checkGameOver() {
  if (activeMonsters.value.length >= maxMonsters) {
    // 몬스터 한도 초과 -> 내 패배 전송
    bs.emitGameOver(currentRoomId.value)
  }
}

// 문제 하나 풀었을 때 (가두고 바로 날리기)
function solveTestcase() {
  if (activeMonsters.value.length > 0) {
    const target = activeMonsters.value.pop()
    
    // 도착 지점 계산 (상대방 아바타 위치)
    let targetX = window.innerWidth * 0.8
    let targetY = 50
    if (oppAvatarContainer.value) {
      const rect = oppAvatarContainer.value.getBoundingClientRect()
      targetX = rect.left + rect.width / 2 - 30 // 거품 크기 오프셋
      targetY = rect.top + rect.height / 2 - 30
    }

    const bubbleId = target.id
    bubbledMonsters.value.push({ ...target, targetX, targetY })
    combo.value++
    
    // 비동기로 전송 효과 지연
    setTimeout(() => {
      sendBubble(bubbleId)
    }, 500) // 애니메이션 지속 시간 (CSS transition 시간과 유사하게)
  }
}

// 콤보 모아서 폭탄 쏘기 (피버)
function solveAll() {
  if (combo.value >= 3) {
    const count = activeMonsters.value.length
    
    // 남아있는 몬스터들도 다 방울로 감싸서 날아가는 연출 추가 가능 (일단은 바로 소멸 후 전송)
    activeMonsters.value = [] // 내 화면 클리어
    combo.value = 0
    const bombCount = count + 3
    bs.emitFeverAttack(currentRoomId.value, bombCount) // 필드 몬스터 + 보너스 전송
    opponentMonsterCount.value += bombCount // 프론트 예측용
  }
}

// 게임 물리 엔진 (무작위 이동)
function startGameLoop() {
  function loop() {
    if (!bs.isPlaying.value) return

    activeMonsters.value.forEach(m => {
      m.x += m.dx
      m.y += m.dy
      
      // 화면 벽 튕기기 (가운데 공동 에디터 전체를 기어다니게)
      if (m.x < 0 || m.x > window.innerWidth * 0.9) m.dx *= -1
      if (m.y < 0 || m.y > window.innerHeight * 0.8) m.dy *= -1
      
      // 가끔 방향 틀기
      if (Math.random() < 0.02) {
        m.dx = (Math.random() - 0.5) * 4
        m.dy = (Math.random() - 0.5) * 4
      }
    })

    // 거품 로직 정리 (이동은 css transform으로 위임됨)

    animationFrameId = requestAnimationFrame(loop)
  }
  loop()
}
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

.lobby-screen, .result-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  gap: 2rem;
}

.lobby-screen h1, .join-screen h1 { font-size: 3rem; color: #58a6ff; }
.desc { color: #8b949e; }

/* 방 입장 폼 */
.join-screen { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; gap: 2rem; }
.join-box { display: flex; gap: 1rem; }
.join-box input { padding: 1rem; font-size: 1.25rem; border-radius: 8px; border: 1px solid #30363d; background: #010409; color: #c9d1d9; width: 300px; }
.join-btn { padding: 1rem 2rem; font-size: 1.25rem; background: #238636; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
.join-btn:disabled { background: #2ea04366; cursor: not-allowed; }
.back-btn { padding: 0.5rem 1.5rem; background: transparent; border: 1px solid #8b949e; color: #8b949e; border-radius: 8px; cursor: pointer; }
.back-btn:hover { background: #8b949e; color: #0d1117; }

.player-panel { display: flex; align-items: center; gap: 1rem; }
.player-panel.opp { flex-direction: row; }
.avatar { 
  font-size: 3rem; 
  background: #21262d; 
  width: 80px; 
  height: 80px; 
  border-radius: 50%; 
  border: 2px solid #30363d; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  overflow: hidden; 
}
.avatar img { width: 100%; height: 100%; object-fit: cover; }
.avatar.opp-avatar { border-color: #ff7b72; }
.info { display: flex; flex-direction: column; }
.info.right { text-align: right; }
.info .name { font-size: 1.2rem; font-weight: bold; color: #c9d1d9; }
.info .status { font-size: 1rem; color: #8b949e; }

.players-box {
  display: flex;
  align-items: center;
  gap: 2rem;
  background: #161b22;
  padding: 2rem;
  border-radius: 12px;
  border: 1px solid #30363d;
}

.player {
  font-size: 1.5rem;
  font-weight: bold;
}
.player.me { color: #3fb950; }
.player.opponent { color: #ff7b72; }
.vs { font-size: 2rem; color: #8b949e; font-style: italic; }

.start-btn, .solve-btn, .exit-btn, .fever-btn {
  padding: 1rem 2rem;
  font-size: 1.25rem;
  background: #238636;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
}
.start-btn:disabled, .fever-btn:disabled { background: #2ea04366; cursor: not-allowed; }

.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: #161b22;
  border-bottom: 2px solid #30363d;
  position: relative;
  z-index: 10;
}

.center-console { display: flex; flex-direction: column; align-items: center; gap: 0.5rem; }
.vs-badge { background: linear-gradient(135deg, #d2a8ff, #ff7b72); color: #0d1117; padding: 4px 16px; border-radius: 20px; font-weight: 800; font-size: 1.2rem;}
.fever-gauge { color: #d2a8ff; font-weight: bold; font-size: 1.2rem; }

/* 1:1 대전 공동 에디터 아레나 */
.battle-arena.unified {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  height: calc(100vh - 120px);
}

.editor-section {
  width: 100%;
  max-width: 1000px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.editor-header {
  background: #161b22;
  padding: 0.5rem 1rem;
  border-radius: 12px 12px 0 0;
  border: 1px solid #30363d;
  border-bottom: none;
  display: flex;
  align-items: center;
  gap: 8px;
}
.dot { width: 12px; height: 12px; border-radius: 50%; }
.dot.red { background: #ff5f56; }
.dot.yellow { background: #ffbd2e; }
.dot.green { background: #27c93f; }
.file-name { margin-left: 10px; color: #8b949e; font-size: 0.9rem; font-family: monospace; }

.editor-mockup {
  background: #010409;
  border: 1px solid #30363d;
  border-radius: 0 0 12px 12px;
  padding: 1.5rem;
  font-family: 'Consolas', monospace;
  font-size: 1.2rem;
  height: 500px;
  overflow: hidden;
  position: relative;
}

.line { display: flex; gap: 1rem; margin-bottom: 0.25rem; }
.num { color: #484f58; width: 30px; text-align: right; user-select: none; }
.code { color: #e6edf3; }

.action-panel {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  z-index: 10;
}

.solve-btn { background: #3fb950; font-size: 1.3rem; padding: 1rem 2.5rem; }
.fever-btn { background: #a371f7; font-size: 1.3rem; padding: 1rem 2.5rem; }

/* 전체 화면 캔버스 오버레이 (버그 몬스터 표시 영역) */
.monster-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%; 
  height: 100%;
  pointer-events: none;
  overflow: hidden;
  z-index: 50;
}

.monster {
  position: absolute;
  font-size: 2rem;
  will-change: transform;
  user-select: none;
}

.monster.bug {
  filter: drop-shadow(0 0 10px rgba(255, 123, 114, 0.5));
}

.monster.bubble {
  font-size: 3.5rem;
  pointer-events: none; /* 자동 날아가므로 클릭 방지 */
  filter: drop-shadow(0 0 15px rgba(88, 166, 255, 0.8));
}

.monster.bubble.flying {
  transition: transform 0.6s cubic-bezier(0.5, 0, 0.75, 0);
  opacity: 0.5;
}

.inner-bug {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.5rem !important;
}

.result-screen h1.win { color: #3fb950; }
.result-screen h1.lose { color: #ff7b72; }
</style>
