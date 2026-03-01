<template>
  <div class="arcade-draw" :class="{ 'screen-shake': shaking, 'flash-ok': flashOk, 'flash-fail': flashFail, 'glitch-screen': activeGlitch }">
    <div class="crt-lines"></div>

    <!-- [수정일: 2026-02-24] 먹물 효과 레이어 -->
    <div v-if="activeInk" class="ink-overlay">
      <div v-for="i in 12" :key="i" class="ink-splat" :style="inkStyles[i-1]"></div>
    </div>

    <!-- ===== LOBBY: 대기 ===== -->
    <div v-if="phase === 'lobby'" class="intro-screen">
      <div class="intro-box">
        <h1 class="logo glitch" data-text="BLUEPRINT">BLUEPRINT</h1>
        <p class="sub-logo">실시간 시스템 설계 서바이벌</p>
        <div class="lobby-players">
          <div v-for="(p,i) in ds.roomPlayers.value" :key="i" class="lp"><span class="lp-icon">👤</span><span>{{ p.name }}</span></div>
          <div v-if="ds.roomPlayers.value.length < 2" class="lp waiting"><span class="lp-icon blink">⏳</span><span>대기 중...</span></div>
        </div>
        <div class="lobby-room-manager">
          <div class="room-id-label">ROOM ID</div>
          <div class="room-input-group">
            <input v-model="inputRoomId" placeholder="방 번호 입력..." class="room-input" @keyup.enter="joinCustomRoom" />
            <button @click="joinCustomRoom" class="btn-join">JOIN</button>
          </div>
          <div class="current-room-info">현재 접속: <span class="neon-c">{{ currentRoomId }}</span></div>
          <!-- [빌드버전: 2026-02-26 05:30] 캐시 확인용 태그 -->
          <div style="font-size:10px; color:#334155; margin-top:5px;">BUILD: 2026-02-26-0530-FINAL</div>
        </div>
        <div class="lobby-info" v-if="!ds.connected.value">연결 중...</div>
        <div class="lobby-info" v-else-if="!ds.isReady.value">상대를 기다리는 중... ({{ ds.roomPlayers.value.length }}/2)</div>
        <button v-if="ds.isReady.value" @click="beginGame" class="btn-start blink-border">▶ GAME START</button>
        <div class="game-guide-container">
          <div class="guide-item">
            <div class="gi-num">01</div>
            <div class="gi-content">
              <strong>주문서 분석</strong>
              <p>상단의 클라이언트 요구사항을 확인하세요.</p>
            </div>
          </div>
          <div class="guide-item">
            <div class="gi-num">02</div>
            <div class="gi-content">
              <strong>블루프린트 구축</strong>
              <p>필요한 시스템 부품을 설계판에 배치하세요.</p>
            </div>
          </div>
          <div class="guide-item">
            <div class="gi-num">03</div>
            <div class="gi-content">
              <strong>데이터 흐름 연결</strong>
              <p>부품 간의 이동 경로를 화살표로 이으세요.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== GAME ===== -->
    <div v-if="phase === 'play' || phase === 'judging'" class="game-screen">
      <!-- HUD -->
      <div class="hud">
        <div class="hud-cell"><span class="hl">ROUND</span><span class="hv neon-c">{{ round }}<span class="dim">/{{ maxRounds }}</span></span></div>
        <div class="hud-cell tcell" :class="{ danger: timerDanger }">
          <div class="ttrack"><div class="tfill" :style="{ width: timerPct + '%' }"></div></div>
          <span class="tnum">{{ timeLeft }}s</span>
        </div>
        <!-- [수정일: 2026-02-24] 멀티 인벤토리 HUD (가시성 및 전략성 강화) -->
        <div class="hud-cell inventory-cell">
          <div class="inventory-header">
            <span class="hl">INVENTORY</span>
            <div class="item-gauge-mini">
              <div class="item-gauge-fill-mini" :style="{ width: itemGauge + '%' }"></div>
            </div>
          </div>
          <div class="inventory-bar">
            <div v-for="it in ITEM_TYPES" :key="it.id" 
                 class="inv-slot" :class="{ 'has-stock': inventory[it.id] > 0 }"
                 @click="useItemById(it.id)">
              <span class="inv-key">{{ it.key }}</span>
              <span class="inv-icon">{{ it.icon }}</span>
              <span class="inv-count">x{{ inventory[it.id] }}</span>
            </div>
          </div>
        </div>
        <div class="hud-cell"><span class="hl">MY SCORE</span><span class="hv neon-y" :key="myScore">{{ myScore }}</span></div>
        <div class="hud-cell"><span class="hl">OPPONENT</span><span class="hv" :style="{color:'#ff2d75'}">{{ oppScore }}</span></div>
        <div class="hud-cell" v-if="combo > 1"><span class="combo-pill neon-fire">{{ combo }}x</span></div>
      </div>

      <!-- MISSION -->
      <div class="mission" v-if="curQ">
        <span class="m-ico">🎯</span>
        <div class="m-txt"><strong>{{ curQ.title }}</strong><span>{{ curQ.description }}</span></div>
        <div class="m-req"><span class="rl">NEED</span><span class="rn neon-c">{{ curQ.required.length }}</span></div>
      </div>
      <!-- [Multi-Agent] CoachAgent 힌트 표시 영역 (버튼 힌트 대체) -->
      <transition name="coach-slide">
        <div class="coach-toast" v-if="coachMsg">
          <span class="coach-icon">🤖</span>
          <span class="coach-text">{{ coachMsg }}</span>
        </div>
      </transition>

      <!-- [추가 2026-02-27] ChaosAgent 주도 장애 이벤트 팝업 -->
      <transition name="chaos-fade">
        <div class="chaos-overlay" v-if="chaosActive">
          <div class="chaos-box" :class="'severity-' + chaosData?.severity.toLowerCase()">
            <div class="chaos-header">
              <span class="chaos-warning">⚠️ SYSTEM INCIDENT DETECTED</span>
              <div class="chaos-scanner"></div>
            </div>
            <div class="chaos-body">
              <h2 class="chaos-title">{{ chaosData?.title }}</h2>
              <p class="chaos-desc">{{ chaosData?.description }}</p>
              <div class="chaos-hint">
                <span class="ch-lab">ADVICE:</span>
                <span class="ch-val">{{ chaosData?.hint }}</span>
              </div>
            </div>
            <div class="chaos-footer">
              <button class="btn-chaos-ack" @click="chaosActive = false">UNDERSTOOD</button>
            </div>
          </div>
        </div>
      </transition>

      <!-- SPLIT: MY CANVAS + OPPONENT CANVAS -->
      <div class="split-view">
        <!-- LEFT: 내 작업 영역 -->
        <div class="my-workspace">
          <div class="ws-header">
            <span class="ws-tag you-tag">👤 MY CANVAS</span>
            <div class="mode-toggle">
              <button :class="{ active: drawMode === 'move' }" @click="drawMode='move'">✋</button>
              <button :class="{ active: drawMode === 'arrow' }" @click="drawMode='arrow'">➡️</button>
            </div>
          </div>
          <!-- Palette -->
          <div class="palette">
            <div v-for="c in paletteComps" :key="c.id" class="pal-chip" :class="{ used: usedIds.includes(c.id) }" draggable="true" @dragstart="onDragStart($event,c)">
              <span class="pi">{{ c.icon }}</span><span class="pn">{{ c.name }}</span>
            </div>
          </div>
          <!-- Canvas -->
          <div class="canvas-wrap" ref="canvasArea" @dragover.prevent @drop="onCanvasDrop" @click="onCanvasClick" @mousemove="onCanvasMouseMove">
            <div class="canvas-hint" v-if="nodes.length === 0">⬇ 드래그하세요</div>
            <svg class="arrow-svg">
              <defs><marker id="ah" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#00f0ff"/></marker></defs>
              <line v-for="(a,i) in arrows" :key="'a'+i" :x1="a.x1" :y1="a.y1" :x2="a.x2" :y2="a.y2" class="aline" marker-end="url(#ah)"/>
              <line v-if="drawingArrow" :x1="drawStart.x" :y1="drawStart.y" :x2="mousePos.x" :y2="mousePos.y" class="aline drawing"/>
            </svg>
            <div v-for="n in nodes" :key="n.id" class="cnode" :class="{ sel: selectedNode === n.id }" :style="{ left:n.x+'px', top:n.y+'px' }" @mousedown.stop="onNodeDown($event,n)" @click.stop="onNodeClick(n)">
              <span class="ni">{{ n.icon }}</span><span class="nn">{{ n.name }}</span>
              <button class="nd" @click.stop="removeNode(n)" v-if="phase==='play'">✕</button>
            </div>
          </div>
        </div>

        <!-- DIVIDER -->
        <div class="split-divider"><div class="dv-line"></div><span>VS</span><div class="dv-line"></div></div>

        <!-- RIGHT: 상대 캔버스 (읽기 전용) -->
        <div class="opp-workspace">
          <div class="ws-header">
            <span class="ws-tag opp-tag">🤖 {{ ds.opponentName.value || 'OPPONENT' }}</span>
            <span v-if="ds.opponentHasItem.value" class="item-ready-badge pulse-neon">⚠️ ITEM READY</span>
            <span v-if="ds.opponentSubmitted.value" class="submitted-badge">✅ SUBMITTED</span>
          </div>
          <!-- [수정일: 2026-02-24] obscured 클래스 제어 로직에 activeScan 반영 -->
          <div class="opp-canvas" :class="{ 'obscured': phase === 'play' && !activeScan }">
            <div v-if="phase === 'play' && !activeScan" class="obscure-overlay">
              <div class="obs-icon">🔒</div>
              <div class="obs-txt">CONFIDENTIAL</div>
              <div class="obs-sub">상대가 설계 중입니다...</div>
            </div>
            <div v-else-if="activeScan" class="scan-active-info">📡 SCANNING OPPONENT...</div>
            <svg class="arrow-svg">
              <defs><marker id="ah2" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#ff2d75"/></marker></defs>
              <line v-for="(a,i) in ds.opponentCanvas.value.arrows" :key="'oa'+i" :x1="a.x1" :y1="a.y1" :x2="a.x2" :y2="a.y2" class="aline opp-arrow" marker-end="url(#ah2)"/>
            </svg>
            <div v-for="(n,i) in ds.opponentCanvas.value.nodes" :key="'on'+i" class="cnode opp-node" :style="{ left:n.x+'px', top:n.y+'px' }">
              <span class="ni">{{ n.icon }}</span><span class="nn">{{ n.name }}</span>
            </div>
            <div v-if="!ds.opponentCanvas.value.nodes.length && phase !== 'play'" class="opp-empty">상대가 아직 배치하지 않았습니다</div>
          </div>
        </div>
      </div>

      <!-- TOOLBAR -->
      <div class="toolbar" v-if="phase === 'play'">
        <button @click="submitDraw" class="btn-submit" :disabled="nodes.length === 0">⚡ SUBMIT</button>
        <button @click="clearCanvas" class="btn-clear">🗑️</button>
      </div>
    </div>

    <!-- JUDGING (아키텍처 대조 심사) -->
    <transition name="zoom">
      <div v-if="phase === 'judging'" class="overlay dark-ov">
        <div class="judge-container">
          <div class="judge-header">
            <div class="spinner"></div>
            <div class="jh-txt">
              <h2 class="neon-c">ARCHITECT JUDGING...</h2>
              <p>AI 아키텍트가 양측의 설계를 대조하며 정밀 분석 리포트를 생성 중입니다.</p>
            </div>
          </div>
          
          <div class="judge-view">
            <!-- 내 설계 -->
            <div class="jv-side">
              <div class="jv-tag you-tag">YOUR DESIGN</div>
              <div class="jv-canvas" ref="myJudgeCanvas">
                <div class="jv-transform-wrapper" :style="myDesignTransform">
                  <svg class="canvas-svg" style="width:2000px; height:2000px; position:absolute; pointer-events:none;">
                    <defs>
                      <marker id="jah" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#00f0ff"/>
                      </marker>
                    </defs>
                    <line v-for="(a,i) in myFinalArrows" :key="'ma'+i"
                      :x1="a.x1" :y1="a.y1" :x2="a.x2" :y2="a.y2"
                      stroke="#00f0ff" stroke-width="2" marker-end="url(#jah)"/>
                  </svg>
                  <div v-for="(n,i) in myFinalNodes" :key="'mn'+i" class="cnode" :style="{ left:n.x+'px', top:n.y+'px' }">
                    <span class="ni">{{ n.icon }}</span><span class="nn">{{ n.name }}</span>
                  </div>
                </div>
                <div v-if="!myFinalNodes.length" class="opp-empty" style="color:#475569">배치된 컴포넌트가 없습니다</div>
              </div>
            </div>

            <div class="jv-divider">VS</div>

            <!-- 상대 설계 -->
            <div class="jv-side">
              <div class="jv-tag opp-tag">{{ ds.opponentName.value || 'OPPONENT' }} DESIGN</div>
              <div class="jv-canvas">
                <div class="jv-transform-wrapper" :style="oppDesignTransform">
                  <svg class="canvas-svg" style="width:2000px; height:2000px; position:absolute; pointer-events:none;">
                    <defs>
                      <marker id="jah2" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#ff2d75"/>
                      </marker>
                    </defs>
                    <line v-for="(a,i) in judgeOppArrows" :key="'oa'+i"
                      :x1="a.x1" :y1="a.y1" :x2="a.x2" :y2="a.y2"
                      stroke="#ff2d75" stroke-width="2" marker-end="url(#jah2)"/>
                  </svg>
                  <div v-for="(n,i) in judgeOppNodes" :key="'on'+i" class="cnode opp-node" :style="{ left:n.x+'px', top:n.y+'px' }">
                    <span class="ni">{{ n.icon }}</span><span class="nn">{{ n.name }}</span>
                  </div>
                </div>
                <div v-if="!judgeOppNodes.length" class="opp-empty">상대가 아직 배치하지 않았습니다</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- ITEM ALERT (아이템 공격 알림) -->
    <transition name="slide-fade">
      <div v-if="itemAlert.show" class="item-alert-toast" :class="itemAlert.type">
        <div class="ia-ico">🚨</div>
        <div class="ia-msg">{{ itemAlert.msg }}</div>
      </div>
    </transition>

    <!-- ROUND RESULT (양쪽 비교) -->
    <transition name="zoom">
      <div v-if="phase === 'result'" class="overlay">
        <div class="result-box" :class="resultClass">
          <div class="r-ico">{{ resultEmoji }}</div>
          <div class="r-title">{{ resultLabel }}</div>
          <div class="r-compare">
            <div class="rc-side">
              <span class="rc-tag you-tag">YOU</span>
              <span class="rc-score neon-c">+{{ lastMyPts }}</span>
              <div class="rc-header">YOUR ARCHITECTURE</div>
              <div class="rc-checks">
                <div v-for="(c,i) in checkItems" :key="i" class="chk" :class="c.ok?'chk-ok':'chk-miss'">{{ c.ok?'✅':'❌' }} {{ c.label }}</div>
              </div>
            </div>
            <div class="rc-vs">VS</div>
            <div class="rc-side">
              <span class="rc-tag opp-tag">{{ ds.opponentName.value || 'OPP' }}</span>
              <span class="rc-score" style="color:#ff2d75">+{{ lastOppPts }}</span>
              <div class="rc-header" style="color:#ff2d75">OPPONENT ARCHITECTURE</div>
              <!-- [수정일: 2026-02-24] 상대방 체크리스트 공개 -->
              <div class="rc-checks">
                <div v-for="(c,i) in oppCheckItems" :key="'oc'+i" class="chk" :class="c.ok?'chk-ok-opp':'chk-miss'">{{ c.ok?'✅':'❌' }} {{ c.label }}</div>
              </div>
            </div>
          </div>

          <!-- [수정일: 2026-02-27] EvalAgent AI ARCHITECT REVIEW - 폴백 메시지 추가로 항상 표시 -->
          <div class="ai-review-board neon-border">
            <div class="ari-header">
              <span class="ari-label">🤖 EVAL AGENT REVIEW</span>
              <span v-if="!aiReview.my" class="ari-loading">분석 중...</span>
            </div>
            <div class="ari-content">
              <p class="ari-my">
                <strong>MY ANALYSIS:</strong>
                {{ aiReview.my || '설계 점수와 체크리스트 기반으로 평가되었습니다. AI 상세 피드백은 최종 리포트에서 확인하세요.' }}
              </p>
              <p class="ari-comp" v-if="aiReview.comparison || lastOppPts > 0">
                <strong>VERSUS:</strong>
                {{ aiReview.comparison || (lastMyPts > lastOppPts ? '상대보다 더 완성도 높은 아키텍처를 설계했습니다. 👍' : lastMyPts === lastOppPts ? '동점! 두 설계 모두 균등한 완성도를 보입니다.' : '상대의 설계가 더 높은 점수를 획득했습니다. 다음 라운드를 노려보세요!') }}
              </p>
            </div>
          </div>
          <button @click="goNextRound" class="btn-next">{{ nextLabel }}</button>
        </div>
      </div>
    </transition>

    <!-- GAME OVER -->
    <transition name="zoom">
      <div v-if="phase === 'gameover'" class="overlay dark-ov">
        <div class="go-box">
          <h1 class="go-title glitch" data-text="GAME OVER">GAME OVER</h1>
          <div class="go-final">
            <div class="go-fs"><span>YOU</span><strong class="neon-c">{{ myScore }}</strong></div>
            <span class="go-vs">VS</span>
            <div class="go-fs"><span>{{ ds.opponentName.value || 'OPP' }}</span><strong style="color:#ff2d75">{{ oppScore }}</strong></div>
          </div>
          <div class="go-verdict">{{ myScore > oppScore ? '🏆 YOU WIN!' : myScore === oppScore ? '🤝 DRAW' : '💪 DEFEAT' }}</div>

          <!-- [추가 2026-02-27] AI 포트폴리오 글 생성 -->
          <PortfolioWriter
            game-type="arch"
            :mission-title="curQ?.title || ''"
            :scenario="curQ?.description || ''"
            :components="myFinalNodes"
            :arrow-count="myFinalArrows.length"
            :my-score="myScore"
            :opponent-score="oppScore"
            :result-text="myScore > oppScore ? 'WIN' : myScore === oppScore ? 'DRAW' : 'LOSE'"
            :grade="myScore > oppScore ? 'A' : myScore >= oppScore * 0.8 ? 'B' : 'C'"
            :ai-review="aiReview.my || ''"
          />

          <!-- 기존 export -->
          <div class="go-portfolio">
            <div class="go-pf-title">🎓 이 설계 경험을 포트폴리오로</div>
            <div class="go-pf-preview" ref="archPortfolioCard">
              <div class="gpf-badge">🏗️ ARCH DESIGN</div>
              <div class="gpf-mission">{{ curQ?.title || '시스템 아키텍처 설계' }}</div>
              <div class="gpf-desc">{{ curQ?.description || '실무 시나리오 기반 아키텍처 배치 및 연결 설계' }}</div>
              <div class="gpf-components">
                <span v-for="n in myFinalNodes.slice(0, 6)" :key="n.id" class="gpf-comp">{{ n.icon }} {{ n.name }}</span>
                <span v-if="myFinalNodes.length > 6" class="gpf-comp-more">+{{ myFinalNodes.length - 6 }}개</span>
              </div>
              <div class="gpf-scores">
                <div class="gpf-score-row">
                  <span class="gpf-sl">MY SCORE</span>
                  <span class="gpf-sv neon-c">{{ myScore }}pt</span>
                  <span class="gpf-sl">BEST COMBO</span>
                  <span class="gpf-sv neon-y">{{ bestCombo }}x</span>
                  <span class="gpf-sl">RESULT</span>
                  <span class="gpf-sv" :style="{ color: myScore > oppScore ? '#00f0ff' : '#ff2d75' }">{{ myScore > oppScore ? 'WIN' : myScore === oppScore ? 'DRAW' : 'LOSS' }}</span>
                </div>
              </div>
              <div v-if="aiReview.my" class="gpf-ai">
                <span class="gpf-ai-label">🤖 AI:</span>
                <span class="gpf-ai-text">{{ aiReview.my.slice(0, 80) }}{{ aiReview.my.length > 80 ? '...' : '' }}</span>
              </div>
              <div class="gpf-footer">CoduckWars · ArchDrawQuiz · {{ goTodayStr }}</div>
            </div>
            <div class="go-pf-actions">
              <button class="go-pf-btn cyan" @click="archExportImage">🖼️ 이미지 저장</button>
              <button class="go-pf-btn purple" @click="archExportText">📋 클립보드 복사</button>
              <button class="go-pf-btn gray" @click="archDownloadTxt">📄 텍스트 저장</button>
            </div>
            <div v-if="archCopyToast" class="go-pf-toast">✅ 클립보드에 복사됐어요!</div>
          </div>

          <div class="go-btns"><button @click="beginGame" class="btn-retry">🔄 REMATCH</button><button @click="exitGame" class="btn-exit">🏠 EXIT</button></div>
        </div>
      </div>
    </transition>

    <transition-group name="fpop" tag="div" class="fpop-layer">
      <div v-for="f in fpops" :key="f.id" class="fpop-item" :style="f.style">+{{ f.v }}</div>
    </transition-group>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDrawSocket } from '../composables/useDrawSocket'
import { useGameStore } from '@/stores/game'
import { addBattleRecord } from '../useBattleRecord.js'

const router = useRouter()
const ds = useDrawSocket()
const gameStore = useGameStore()
const initialRoomId = gameStore.activeWarsMission?.id ? `draw-${gameStore.activeWarsMission.id}` : 'draw-default'
const currentRoomId = ref(initialRoomId)
const inputRoomId = ref(initialRoomId)
const userName = ref('Player_' + Math.floor(Math.random() * 1000))

const phase = ref('lobby')
const round = ref(0)
const maxRounds = 1 // [수정일: 2026-02-25] 1단원(1라운드) 단판 승부로 변경
const timeLeft = ref(45)
const myScore = ref(0)
const oppScore = ref(0)
const combo = ref(0)
const bestCombo = ref(0)
const coachMsg = ref('')
let coachTimer = null
const lastMyPts = ref(0)
const lastOppPts = ref(0)
const checkItems = ref([])
const oppCheckItems = ref([]) // [수정일: 2026-02-24] 상대방 체크리스트
const shaking = ref(false)
const flashOk = ref(false)
const flashFail = ref(false)
const fpops = ref([])
const aiReview = ref({ my: '', comparison: '' }) // [수정일: 2026-02-24] AI 피드백
const itemAlert = ref({ show: false, msg: '', type: '' }) // [수정일: 2026-02-24] 아이템 알림창
const myFinalNodes = ref([])   // [수정일: 2026-02-24] 심사용 내 최종 설계
const myFinalArrows = ref([])
const oppFinalNodes = ref([])  // [수정일: 2026-02-24] 심사용 상대 최종 설계 
const oppFinalArrows = ref([])
let fpopId = 0
let timer = null

// [수정일: 2026-02-24] 아이템 시스템 상태 (멀티 인벤토리)
const inventory = ref({ ink: 0, shake: 0, glitch: 0, scan: 0, swap: 0 })
const itemGauge = ref(0)
const activeInk = ref(false)
const activeGlitch = ref(false)
const activeScan = ref(false)
const inkStyles = ref([])
const totalItems = computed(() => Object.values(inventory.value).reduce((a, b) => a + b, 0))

// [추가 2026-02-27] ChaosEvent 상태
const chaosActive = ref(false)
const chaosData = ref(null)

const ITEM_TYPES = [
  { id: 'ink', name: 'INK SPLASH', icon: '🖋️', effect: 'ink', key: '1' },
  { id: 'shake', name: 'EARTHQUAKE', icon: '🫨', effect: 'shake', key: '2' },
  { id: 'glitch', name: 'BIT-GLITCH', icon: '👾', effect: 'glitch', key: '3' },
  { id: 'scan', name: 'X-RAY SCAN', icon: '🔍', effect: 'scan', key: '4' }, 
  { id: 'swap', name: 'ARCH-SWAP', icon: '🔄', effect: 'swap', key: '5' }
]

const nodes = ref([])
const arrows = ref([])
const usedIds = computed(() => nodes.value.map(n => n.compId))
const selectedNode = ref(null)
const drawMode = ref('move')
const drawingArrow = ref(false)
const arrowSource = ref(null)
const drawStart = ref({ x:0, y:0 })
const mousePos = ref({ x:0, y:0 })
const canvasArea = ref(null)
let dragComp = null
let nodeId = 0

const timerPct = computed(() => (timeLeft.value / 45) * 100)

// judging 캔버스: 노드 위치 기반 동적 높이 + 상대 노드 안전 참조
const judgeOppNodes = computed(() => 
  oppFinalNodes.value.length ? oppFinalNodes.value : ds.opponentCanvas.value.nodes
)
const judgeOppArrows = computed(() => 
  oppFinalArrows.value.length ? oppFinalArrows.value : ds.opponentCanvas.value.arrows
)
// [수정일: 2026-02-27] judging 캔버스: 모든 노드가 한눈에 들어오도록 자동 스케일링 및 중앙 정렬 로직 도입
const getDesignTransform = (nodesList) => {
  if (!nodesList || nodesList.length === 0) return { transform: 'scale(1)' }
  
  // 1. 바운딩 박스 계산
  const minX = Math.min(...nodesList.map(n => n.x))
  const maxX = Math.max(...nodesList.map(n => n.x + 100)) // 노드 너비 약 100px 반영
  const minY = Math.min(...nodesList.map(n => n.y))
  const maxY = Math.max(...nodesList.map(n => n.y + 44))  // 노드 높이 약 44px 반영
  
  const contentWidth = maxX - minX
  const contentHeight = maxY - minY
  
  // 2. 컨테이너 크기 (CSS와 일치해야 함: 약 450px 높이)
  const containerWidth = 450 // 대략적인 여유 공간
  const containerHeight = 400
  
  // 3. 스케일 계산 (여유 간격 40px 제외)
  const scaleX = (containerWidth - 60) / contentWidth
  const scaleY = (containerHeight - 60) / contentHeight
  const scale = Math.min(1.2, Math.min(scaleX, scaleY, 1)) // 너무 크게 키우지 않음
  
  // 4. 중앙 정합을 위한 이동값
  const centerX = (containerWidth - contentWidth * scale) / 2
  const centerY = (containerHeight - contentHeight * scale) / 2
  const translateX = centerX - minX * scale
  const translateY = centerY - minY * scale
  
  return {
    transform: `translate(${translateX}px, ${translateY}px) scale(${scale})`,
    transformOrigin: '0 0',
    transition: 'all 0.5s ease'
  }
}

const myDesignTransform = computed(() => getDesignTransform(myFinalNodes.value))
const oppDesignTransform = computed(() => getDesignTransform(judgeOppNodes.value))
const timerDanger = computed(() => timeLeft.value <= 10)
const nextLabel = computed(() => round.value >= maxRounds ? 'FINAL RESULT' : 'NEXT ▶')

const resultClass = computed(() => {
  if (lastMyPts.value > lastOppPts.value) return 'res-win'
  if (lastMyPts.value === lastOppPts.value) return 'res-draw'
  return 'res-lose'
})
const resultEmoji = computed(() => { if (lastMyPts.value > lastOppPts.value) return '🎉'; if (lastMyPts.value === lastOppPts.value) return '🤝'; return '😤' })
const resultLabel = computed(() => { if (lastMyPts.value > lastOppPts.value) return 'YOU WIN THIS ROUND!'; if (lastMyPts.value === lastOppPts.value) return 'DRAW'; return 'OPPONENT WINS' })

// [수정일: 2026-02-24] 로컬 미션 데이터 제거 (서버/AI 주도로 변경)
const allComps = [
  {id:'client',name:'Client',icon:'👤'},{id:'user',name:'User',icon:'👤'},{id:'lb',name:'LB',icon:'⚖️'},
  {id:'server',name:'Server',icon:'🖥️'},{id:'cdn',name:'CDN',icon:'🌍'},{id:'origin',name:'Origin',icon:'🏠'},
  {id:'cache',name:'Cache',icon:'💾'},{id:'db',name:'DB',icon:'🗄️'},{id:'producer',name:'Producer',icon:'📤'},
  {id:'queue',name:'MsgQ',icon:'📨'},{id:'consumer',name:'Consumer',icon:'📥'},{id:'api',name:'API GW',icon:'🚪'},
  {id:'apigw',name:'API GW',icon:'🚪'},{id:'writesvc',name:'Write',icon:'✍️'},{id:'readsvc',name:'Read',icon:'📖'},
  {id:'writedb',name:'WriteDB',icon:'💿'},{id:'readdb',name:'ReadDB',icon:'📀'},{id:'auth',name:'Auth',icon:'🔑'},
  {id:'order',name:'Order',icon:'📦'},{id:'payment',name:'Pay',icon:'💳'},{id:'waf',name:'WAF',icon:'🧱'},{id:'dns',name:'DNS',icon:'📡'},
]

// [수정일: 2026-02-25] 서버에서 보내주는 문제(ds.roundQuestion)를 사용
const curQ = computed(() => ds.roundQuestion.value)
const paletteComps = computed(() => {
  if (!curQ.value) return []
  
  // [수정일: 2026-03-01] 서버가 내려준 palette_ids 우선 사용 — 양측 동일 팔레트 보장
  // 서버에 palette_ids 없으면(구버전 호환) required만 표시
  const ids = curQ.value.palette_ids || curQ.value.required || []
  const result = ids.map(id => allComps.find(c => c.id === id)).filter(Boolean)
  return result
})

// ── CoachHint 소켓 리스너 등록 함수
const registerCoachHint = (sock) => {
  if (!sock) return
  sock.on('coach_hint', (data) => {
    if (coachTimer) clearTimeout(coachTimer)
    coachMsg.value = data.message
    coachTimer = setTimeout(() => { coachMsg.value = '' }, 6000)
  })
}

// ── 소켓 연결 (onMounted 1개로 통합) ──
onMounted(() => { 
  console.log(`[ArchDraw] Connecting to Room: ${currentRoomId.value} as ${userName.value}`)
  ds.connect(currentRoomId.value, userName.value)
  window.addEventListener('keydown', handleGlobalKey)

  // CoachHint 리스너 — 소켓 준비 후 등록
  if (ds.socket.value) {
    registerCoachHint(ds.socket.value)
  } else {
    const unwatch = watch(() => ds.socket.value, (sock) => {
      if (sock) { registerCoachHint(sock); unwatch() }
    })
  }

  // 게임 시작 핸들러
  ds.onGameStart.value = (data) => {
    console.log('[ArchDraw] Game start signal received:', data)
    myScore.value = 0; oppScore.value = 0; combo.value = 0; bestCombo.value = 0; round.value = 0
  }

  // ChaosEvent 핸들러
  ds.onChaosEvent.value = (data) => {
    console.log('🔥 [ArchDraw] Chaos Triggered:', data)
    chaosData.value = data
    chaosActive.value = true
    spawnPopText("🚨 CRITICAL SYSTEM INCIDENT!", "#ff2d75")
    triggerGlitch()
    setTimeout(() => { if (chaosActive.value) chaosActive.value = false }, 10000)
  }
})

// Agent 트리거용 실시간 설계 동기화
function syncMyDesign() {
  if (phase.value !== 'play') return
  ds.emitCanvasSync(currentRoomId.value, userName.value, nodes.value, arrows.value)
}

function handleCanvasChange() {
  syncMyDesign()
}
onUnmounted(() => { 
  clearInterval(timer)
  ds.disconnect(currentRoomId.value)
  window.removeEventListener('keydown', handleGlobalKey)
})

// ========== [추가 2026-02-27] 포트폴리오 export ==========
const archPortfolioCard = ref(null)
const archCopyToast = ref(false)
const goTodayStr = new Date().toISOString().slice(0, 10)

const archBuildText = () => {
  const mission = curQ.value
  const components = myFinalNodes.value.map(n => `${n.icon} ${n.name}`).join(', ')
  const arrows = myFinalArrows.value.length
  const verdict = myScore.value > oppScore.value ? 'WIN' : myScore.value === oppScore.value ? 'DRAW' : 'LOSS'
  return [
    `🎓 [CoduckWars 아키텍처 캐치마인드 포트폴리오]`,
    ``,
    `📋 미션: ${mission?.title || '시스템 아키텍처 설계'}`,
    `💡 시나리오: ${mission?.description || '실무 시나리오 기반 아키텍처 설계'}`,
    ``,
    `🛠️ 설계한 컴포넌트 (${myFinalNodes.value.length}개):`,
    `  ${components}`,
    `🔗 연결 화살표: ${arrows}개`,
    ``,
    `📊 결과`,
    `  내 점수: ${myScore.value}pt  |  상대 점수: ${oppScore.value}pt`,
    `  베스트 콤보: ${bestCombo.value}x  |  결과: ${verdict}`,
    mission?.required ? `  필수 컴포넌트: ${mission.required.join(', ')}` : '',
    ``,
    aiReview.value.my ? `🤖 AI 평가: ${aiReview.value.my}` : '',
    ``,
    `🔗 Powered by CoduckWars — 시스템 설계 AI 실습 플랫폼`,
    `📅 ${goTodayStr}`
  ].filter(l => l !== '').join('\n')
}

const archExportImage = () => {
  const card = archPortfolioCard.value
  if (!card) return
  const canvas = document.createElement('canvas')
  const scale = 2
  const rect = card.getBoundingClientRect()
  canvas.width = rect.width * scale
  canvas.height = rect.height * scale
  const ctx = canvas.getContext('2d')
  ctx.scale(scale, scale)
  const W = rect.width, H = rect.height

  // 배경
  const bg = ctx.createLinearGradient(0, 0, W, H)
  bg.addColorStop(0, '#030712'); bg.addColorStop(1, '#0f172a')
  ctx.fillStyle = bg
  ctx.roundRect(0, 0, W, H, 12); ctx.fill()
  ctx.strokeStyle = 'rgba(0,240,255,0.4)'; ctx.lineWidth = 1.5
  ctx.roundRect(0, 0, W, H, 12); ctx.stroke()

  // 배지
  ctx.fillStyle = 'rgba(0,240,255,0.08)'
  ctx.roundRect(12, 12, 150, 22, 5); ctx.fill()
  ctx.fillStyle = '#00f0ff'; ctx.font = 'bold 10px monospace'
  ctx.fillText('🏗️ ARCH DESIGN', 20, 27)

  // 미션
  ctx.fillStyle = '#f1f5f9'; ctx.font = 'bold 15px sans-serif'
  const mission = curQ.value
  const title = mission?.title || '시스템 아키텍처 설계'
  ctx.fillText(title.length > 40 ? title.slice(0, 40) + '...' : title, 12, 52)

  // 컴포넌트 칩
  let cx = 12, cy = 68
  myFinalNodes.value.slice(0, 8).forEach(n => {
    const label = `${n.icon} ${n.name}`
    const tw = ctx.measureText(label).width + 16
    if (cx + tw > W - 12) { cx = 12; cy += 22 }
    ctx.fillStyle = 'rgba(0,240,255,0.1)'
    ctx.roundRect(cx, cy, tw, 18, 4); ctx.fill()
    ctx.strokeStyle = 'rgba(0,240,255,0.25)'; ctx.lineWidth = 0.8
    ctx.roundRect(cx, cy, tw, 18, 4); ctx.stroke()
    ctx.fillStyle = '#e0f2fe'; ctx.font = '10px sans-serif'
    ctx.fillText(label, cx + 8, cy + 13)
    cx += tw + 6
  })
  cy += 28

  // 점수
  ctx.fillStyle = '#334155'; ctx.fillRect(12, cy, W - 24, 1); cy += 10
  ctx.font = '11px monospace'
  ctx.fillStyle = '#00f0ff'; ctx.fillText(`MY: ${myScore.value}pt`, 12, cy + 10)
  ctx.fillStyle = '#ff2d75'; ctx.fillText(`OPP: ${oppScore.value}pt`, 100, cy + 10)
  const verdict = myScore.value > oppScore.value ? '🏆 WIN' : myScore.value === oppScore.value ? '🤝 DRAW' : '💪 LOSS'
  ctx.fillStyle = myScore.value > oppScore.value ? '#00f0ff' : '#ff2d75'
  ctx.fillText(verdict, W - 70, cy + 10)
  cy += 22

  // AI 평가
  if (aiReview.value.my) {
    ctx.fillStyle = '#475569'; ctx.font = '9px sans-serif'
    const ai = '🤖 ' + aiReview.value.my
    ctx.fillText(ai.length > 70 ? ai.slice(0, 70) + '...' : ai, 12, cy + 10)
    cy += 16
  }

  // 푸터
  ctx.fillStyle = '#1e293b'; ctx.fillRect(0, H - 24, W, 1)
  ctx.fillStyle = '#334155'; ctx.font = '9px monospace'
  ctx.fillText('CoduckWars · ArchDrawQuiz', 12, H - 10)
  ctx.fillText(goTodayStr, W - 70, H - 10)

  const link = document.createElement('a')
  link.download = `arch_portfolio_${goTodayStr}.png`
  link.href = canvas.toDataURL('image/png')
  link.click()
}

const archExportText = () => {
  const text = archBuildText()
  navigator.clipboard.writeText(text).catch(() => {
    const ta = document.createElement('textarea')
    ta.value = text; document.body.appendChild(ta); ta.select()
    document.execCommand('copy'); document.body.removeChild(ta)
  }).finally?.(() => {})
  // catch분기 바깥
  try { navigator.clipboard.writeText(text) } catch {}
  archCopyToast.value = true
  setTimeout(() => { archCopyToast.value = false }, 2500)
}

const archDownloadTxt = () => {
  const text = archBuildText()
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
  const link = document.createElement('a')
  link.download = `arch_portfolio_${goTodayStr}.txt`
  link.href = URL.createObjectURL(blob)
  link.click()
  URL.revokeObjectURL(link.href)
}
// =========================================================

function joinCustomRoom() {
  if (!inputRoomId.value.trim()) return
  const newRoomId = inputRoomId.value.trim()
  console.log(`[ArchDraw] Switching to Room: ${newRoomId}`)
  
  // 기존 방 퇴장 후 새 방 입장
  ds.disconnect(currentRoomId.value)
  currentRoomId.value = newRoomId
  ds.connect(newRoomId, userName.value)
  
  spawnPopText(`ROOM ${newRoomId} 입장!`, '#00f0ff')
}


// [수정일: 2026-02-24] 아이템 효과 수신 처리 및 알림창 표시
const showItemAlert = (type) => {
  const item = ITEM_TYPES.find(it => it.id === type)
  const name = item ? item.name : type.toUpperCase()
  itemAlert.value = { show: true, msg: `⚠️ WARNING: OPPONENT USED ${name}!`, type }
  setTimeout(() => { itemAlert.value.show = false }, 3000)
}

ds.onItemEffect.value = (type) => {
  showItemAlert(type) // 알림 표시 추가
  if (type === 'shake') triggerShake()
  else if (type === 'ink') triggerInk()
  else if (type === 'glitch') triggerGlitch()
  else if (type === 'swap') {
    nodes.value = [...ds.opponentCanvas.value.nodes]
    arrows.value = [...ds.opponentCanvas.value.arrows]
    triggerShake()
  }
}

// [추가: 2026-02-24] 서버로부터 게임 종료 신호 수신 시 처리
ds.onGameOver.value = () => {
  console.log("🏁 Game Over signal received from server.")
  phase.value = 'gameover'
}

function triggerShake() {
  shaking.value = true
  setTimeout(() => shaking.value = false, 1500)
}

function triggerInk() {
  // [수정일: 2026-02-24] 먹물 버프: 개수 상향(12->25), 크기 상향(1~3배->2.5~6배)
  inkStyles.value = Array.from({ length: 25 }).map(() => ({
    left: Math.random() * 90 + 5 + '%',
    top: Math.random() * 90 + 5 + '%',
    transform: `scale(${Math.random() * 3.5 + 2.5}) rotate(${Math.random() * 360}deg)`,
    opacity: Math.random() * 0.2 + 0.8
  }))
  activeInk.value = true
  setTimeout(() => activeInk.value = false, 4500) // 지속시간 소폭 상향
}

function triggerGlitch() {
  activeGlitch.value = true
  setTimeout(() => activeGlitch.value = false, 3000)
}

function handleGlobalKey(e) {
  if (phase.value !== 'play') return
  
  // [수정일: 2026-02-24] 숫자키 1~5로 아이템 즉시 사용
  const item = ITEM_TYPES.find(it => it.key === e.key)
  if (item) {
    useItemById(item.id)
  }
}

// [수정일: 2026-02-24] 인벤토리 기반 아이템 사용 로직
function useItemById(itemId) {
  if (inventory.value[itemId] <= 0) return
  const item = ITEM_TYPES.find(it => it.id === itemId)
  if (!item) return

  if (itemId === 'scan') {
    activeScan.value = true
    spawnPopText("X-RAY SCAN ACTIVATED!", "#00f0ff")
    setTimeout(() => activeScan.value = false, 4000)
  } 
  else if (itemId === 'swap') {
    nodes.value = [...ds.opponentCanvas.value.nodes]
    arrows.value = [...ds.opponentCanvas.value.arrows]
    ds.emitUseItem(currentRoomId.value, 'swap')
    spawnPopText("ARCHITECTURE SWAPPED!", "#ff2d75")
  }
  else {
    ds.emitUseItem(currentRoomId.value, itemId)
    spawnPopText(`USED ${item.name}!`, '#00f0ff')
  }
  
  inventory.value[itemId]--
}

function gainRandomItem() {
  const item = ITEM_TYPES[Math.floor(Math.random() * ITEM_TYPES.length)]
  inventory.value[item.id]++
  spawnPopText(`GET ${item.name}!`, '#b6ff40')
}

function spawnPopText(txt, color) {
  const id = ++fpopId
  fpops.value.push({ id, v: txt, style: { left: '50%', color: color || '#ffe600' } })
  setTimeout(() => { fpops.value = fpops.value.filter(f => f.id !== id) }, 1200)
}

// [수정일: 2026-02-24] 라운드 결과 수신 및 심사(Judging) 단계 진입
ds.onRoundResult.value = (results) => {
  if (!results) return
  const me = results.find(r => r.sid === ds.socket.value?.id)
  const opp = results.find(r => r.sid !== ds.socket.value?.id)
  
  if (me) { 
    myScore.value = me.score 
    lastMyPts.value = me.last_pts || 0
    checkItems.value = me.last_checks || []
    // [버그수정] myFinalNodes/Arrows는 submitDraw()에서 이미 고정됨 → 여기서 덮어쓰지 않음
    // (서버 결과가 오기 전에 이미 judging 화면이 노출되므로 로컬 스냅샷이 더 신뢰성 높음)
    
    // AI 리뷰 데이터 매칭 (서버에서 같이 보낸 경우)
    if (me.ai_review) {
      aiReview.value = {
        my: me.ai_review.my_analysis,
        comparison: me.ai_review.versus
      }
    }
  }
  if (opp) { 
    oppScore.value = opp.score
    lastOppPts.value = opp.last_pts || 0
    oppCheckItems.value = opp.last_checks || []
    // [버그수정] 서버에서 받은 상대방 최종 설계 저장
    // last_nodes/last_arrows 없으면 실시간 캔버스 데이터로 폴백
    oppFinalNodes.value = (opp.last_nodes && opp.last_nodes.length)
      ? opp.last_nodes
      : JSON.parse(JSON.stringify(ds.opponentCanvas.value.nodes))
    oppFinalArrows.value = (opp.last_arrows && opp.last_arrows.length)
      ? opp.last_arrows
      : JSON.parse(JSON.stringify(ds.opponentCanvas.value.arrows))
  }
  
  // [버그수정] onRoundResult는 항상 judging 중에 도착 — phase 변경 없이 바로 result 타이머만 설정
  // (phase를 다시 judging으로 바꾸면 Vue가 컠포넌트 재렌더링해서 myFinalNodes가 순간 빈 배열로 보임)
  if (phase.value !== 'judging' && phase.value !== 'result') {
    phase.value = 'judging'
  }
  
  // 3.5초 후 자동으로 결과 리포트 화면으로 전환 (AI 분석 로딩 느낌)
  setTimeout(() => {
    if (phase.value !== 'gameover') phase.value = 'result'
  }, 3500)
}

// [수정일: 2026-02-24] .value를 사용하여 서버(AI)가 문제를 던져주었을 때의 처리 등록
ds.onRoundStart.value = (data) => {
  if (!data || !data.question) return;
  // curQ는 computed이므로 여기서 직접 할당하지 않습니다. (ds.roundQuestion이 이미 업데이트됨)
  
  // [수정일: 2026-02-24] 서버가 보내준 라운드 번호 사용 (없으면 수동 증가)
  if (data.round) round.value = data.round;
  else round.value++;
  
  phase.value = 'play';
  timeLeft.value = 45;
  coachMsg.value = '';
  nodes.value = [];
  arrows.value = [];
  selectedNode.value = null;
  drawingArrow.value = false;
  drawMode.value = 'move';
  
  // 노드 선택 해제 로직 등
  selectedNode.value = null;
  drawStart.value = null;
  drawingArrow.value = false;
  handleCanvasChange();
  
  clearInterval(timer);
  timer = setInterval(() => {
    if (timeLeft.value > 0 && phase.value === 'play') timeLeft.value--;
    if (timeLeft.value <= 0 && phase.value === 'play') submitDraw();
  }, 1000);

  // [수정일: 2026-02-24] 라운드 데이터 초기화
  aiReview.value = { my: '', comparison: '' }
  inventory.value = { ink: 1, shake: 1, glitch: 1, scan: 1, swap: 1 }
  spawnPopText("ALL ITEMS RECHARGED!", "#ffe600")
};

function beginGame() {
  // REMATCH 시 이전 결과 저장
  if (phase.value === 'gameover' && (myScore.value > 0 || oppScore.value > 0)) {
    saveResultAndExit()
  }
  myScore.value = 0; oppScore.value = 0; combo.value = 0; bestCombo.value = 0; round.value = 0
  ds.emitStart(currentRoomId.value, null)
}

function goNextRound() { 
  // [수정일: 2026-02-24] 로컬에서도 5라운드 종료 체크 (안전장치)
  if (round.value >= maxRounds) {
    phase.value = 'gameover'
    return
  }
  ds.emitNextRound(currentRoomId.value, null) // 다음 라운드 신호 전송
}
// getHint 제거됨 — CoachAgent가 대체

// ── Canvas interaction (동일) ──
function onDragStart(e, c) { dragComp = c; e.dataTransfer.effectAllowed = 'copy' }
// 컴포넌트 추가/삭제 시 동기화 호출
function onCanvasDrop(e) {
  if (!dragComp || phase.value !== 'play') return
  const r = canvasArea.value.getBoundingClientRect()
  nodes.value.push({ id: ++nodeId, compId: dragComp.id, name: dragComp.name, icon: dragComp.icon, x: e.clientX-r.left-50, y: e.clientY-r.top-22 })
  dragComp = null
  
  // [수정일: 2026-02-24] 배치 시 아이템 게이지 상승 (속도 상향: 25%)
  if (itemGauge.value < 100) {
    itemGauge.value = Math.min(100, itemGauge.value + 25)
    if (itemGauge.value >= 100) {
      itemGauge.value = 0
      gainRandomItem()
    }
  }
  handleCanvasChange();
}
function onNodeDown(e, n) {
  if (drawMode.value !== 'move' || phase.value !== 'play') return
  const r = canvasArea.value.getBoundingClientRect()
  const ox = e.clientX-r.left-n.x, oy = e.clientY-r.top-n.y
  const mv = ev => { const r2 = canvasArea.value.getBoundingClientRect(); n.x = Math.max(0,Math.min(r2.width-100,ev.clientX-r2.left-ox)); n.y = Math.max(0,Math.min(r2.height-44,ev.clientY-r2.top-oy)); arrows.value.forEach(a => { if(a.fid===n.id){a.x1=n.x+50;a.y1=n.y+22} if(a.tid===n.id){a.x2=n.x+50;a.y2=n.y+22} }); handleCanvasChange(); }
  const up = () => { window.removeEventListener('mousemove',mv); window.removeEventListener('mouseup',up) }
  window.addEventListener('mousemove',mv); window.addEventListener('mouseup',up)
}
function onNodeClick(n) {
  if (drawMode.value !== 'arrow' || phase.value !== 'play') return
  if (!drawingArrow.value) { drawingArrow.value = true; arrowSource.value = n.id; drawStart.value = {x:n.x+50,y:n.y+22}; selectedNode.value = n.id }
  else { 
    if (arrowSource.value !== n.id) { 
      const from = nodes.value.find(nd=>nd.id===arrowSource.value)
      arrows.value.push({fid:arrowSource.value,tid:n.id,fc:from?.compId,tc:n.compId,x1:drawStart.value.x,y1:drawStart.value.y,x2:n.x+50,y2:n.y+22}) 
      
      // [수정일: 2026-02-24] 화살표 연결 시에도 게이지 상승 (20%)
      if (itemGauge.value < 100) {
        itemGauge.value = Math.min(100, itemGauge.value + 20)
        if (itemGauge.value >= 100) {
          itemGauge.value = 0
          gainRandomItem()
        }
      }
      handleCanvasChange();
    }
    drawingArrow.value = false; arrowSource.value = null; selectedNode.value = null 
  }
}
function onCanvasClick() { if (drawingArrow.value) { drawingArrow.value = false; arrowSource.value = null; selectedNode.value = null } }
function onCanvasMouseMove(e) { if (!drawingArrow.value || !canvasArea.value) return; const r = canvasArea.value.getBoundingClientRect(); mousePos.value = {x:e.clientX-r.left,y:e.clientY-r.top} }
function removeNode(n) { 
  nodes.value = nodes.value.filter(nd=>nd.id!==n.id); 
  arrows.value = arrows.value.filter(a=>a.fid!==n.id&&a.tid!==n.id);
  handleCanvasChange();
}
function clearCanvas() { nodes.value = []; arrows.value = []; selectedNode.value = null; drawingArrow.value = false; handleCanvasChange(); }

// ── Submit ──
function submitDraw() {
  clearInterval(timer); 
  
  // [버그수정] 제출 직전 데이터 스냅샷 → phase 변경 전에 저장해야 watch가 덮어쓰지 않음
  myFinalNodes.value = JSON.parse(JSON.stringify(nodes.value))
  myFinalArrows.value = JSON.parse(JSON.stringify(arrows.value))
  // 스냅샷 직후 로컬 참조로 고정 (setTimeout 안에서 nodes.value 대신 사용)
  const snapNodes = myFinalNodes.value
  const snapArrows = myFinalArrows.value
  
  // [버그수정] watch([nodes, arrows]) 가 judging 전환 후에도 emit하지 않도록 play 상태를 먼저 닫음
  phase.value = 'judging'
  setTimeout(() => {
    // [수정일: 2026-02-25] 백엔드에서 온 미션의 DB rubric_functional 활용
    let checks = []
    if (curQ.value && curQ.value.rubric && curQ.value.rubric.required_components) {
      checks = curQ.value.rubric.required_components.map(compId => {
        const compName = allComps.find(c => c.id === compId)?.name || compId
        return {
          label: `${compName} 배치`,
          ok: nodes.value.some(n => n.compId === compId)
        }
      })
    } else if (curQ.value && curQ.value.required) {
      checks = curQ.value.required.map(compId => {
        const compName = allComps.find(c => c.id === compId)?.name || compId
        return {
          label: `${compName} 배치`,
          ok: snapNodes.some(n => n.compId === compId)  // nodes.value 대신 스냅샷 사용
        }
      })
    }
    
    // DB rubric에 화살표(flow) 검증 기준이 있다면 추가
    if (curQ.value && curQ.value.rubric && curQ.value.rubric.required_flows) {
      curQ.value.rubric.required_flows.forEach(flow => {
        // 흐름은 from, to, reason 구조임. 현재 컴포넌트 이름과 매핑해야 함.
        // allComps는 id를 가지고 있음 (예: 'client', 'server', 'db')
        // DB의 from/to는 "API Server", "Cache" 형태일 수 있으므로 유연하게 처리.
        // 간단히 arrows.value.some()을 쓸 수 있지만 id 매핑이 까다로울 수 있음.
        // 일단 UI상에는 명시하고 현재는 배치 컴포넌트만 필수 체크하는 방향 유지 (복잡도 회피)
      })
    } else if (curQ.value && curQ.value.required && curQ.value.required.length >= 2) {
      for (let i = 0; i < curQ.value.required.length - 1; i++) {
        const from = curQ.value.required[i]
        const to = curQ.value.required[i+1]
        checks.push({
          label: `${from} → ${to} 연결`,
          ok: snapArrows.some(a => a.fc === from && a.tc === to)  // arrows.value 대신 스냅샷 사용
        })
      }
    }
    checkItems.value = checks
    
    const hit = checks.filter(c => c.ok).length, ratio = hit / checks.length
    const pts = hit * 40 + (ratio >= 0.8 ? 100 : 0) + timeLeft.value * 2 + combo.value * 20
    lastMyPts.value = pts; myScore.value += pts
    
    if (ratio >= 0.8) { 
      combo.value++; bestCombo.value = Math.max(bestCombo.value, combo.value); flashOk.value = true; setTimeout(() => flashOk.value = false, 400); spawnPop(pts) 
      gainRandomItem()
    }
    
    ds.emitSubmit(currentRoomId.value, pts, checks.map(c => ({ label: c.label, ok: c.ok })), {
      nodes: snapNodes,
      arrows: snapArrows
    }, timeLeft.value, combo.value)  // [수정: 서버 점수 검증용 time_left, combo 전달]
  }, 1500)
}

function spawnPop(v) { const id = ++fpopId; fpops.value.push({id,v,style:{left:(35+Math.random()*30)+'%'}}); setTimeout(()=>{fpops.value=fpops.value.filter(f=>f.id!==id)},1200) }
function saveResultAndExit() {
  // 게임 결과를 전적에 기록
  const name = userName.value
  if (myScore.value > oppScore.value) addBattleRecord(name, 'win')
  else if (myScore.value < oppScore.value) addBattleRecord(name, 'lose')
  else addBattleRecord(name, 'draw')
}

function exitGame() {
  saveResultAndExit()
  ds.disconnect(currentRoomId.value)
  router.push('/practice/coduck-wars')
}

// [수정일: 2026-02-24] 내 아이템 상태 실시간 동기화 (총 수량 기준)
watch(totalItems, (newVal) => {
  ds.emitItemStatus(currentRoomId.value, newVal > 0)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;600;700&display=swap');
.arcade-draw{min-height:100vh;background:#030712;color:#e0f2fe;font-family:'Rajdhani',sans-serif;position:relative;overflow:hidden}
.crt-lines{pointer-events:none;position:fixed;inset:0;z-index:9999;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,240,255,.012) 2px,rgba(0,240,255,.012) 4px)}
.screen-shake{animation:shake .3s ease infinite}
.flash-ok::after{content:'';position:fixed;inset:0;background:rgba(57,255,20,.12);z-index:9000;pointer-events:none;animation:fo .4s forwards}
.flash-fail::after{content:'';position:fixed;inset:0;background:rgba(255,45,117,.12);z-index:9000;pointer-events:none;animation:fo .4s forwards}
@keyframes shake{0%,100%{transform:translateX(0)}20%{transform:translate(-5px, 2px)}40%{transform:translate(5px, -2px)}60%{transform:translate(-5px, -2px)}80%{transform:translate(5px, 2px)}}
@keyframes fo{from{opacity:1}to{opacity:0}}
.glitch{position:relative;font-family:'Orbitron',sans-serif;color:#00f0ff;font-size:3.5rem;letter-spacing:4px}

/* 가이드 및 배틀 버튼 스타일 가독성 강화 [2026-02-24] */
.game-guide-container { margin-top: 30px; display: flex; flex-direction: column; gap: 12px; text-align: left; width: 100%; }
.guide-item { display: flex; align-items: flex-start; gap: 15px; background: rgba(0, 240, 255, 0.05); padding: 12px; border-radius: 8px; border: 1px solid rgba(0, 240, 255, 0.1); transition: all 0.3s; }
.guide-item:hover { background: rgba(0, 240, 255, 0.1); border-color: #00f0ff; }
.gi-num { font-family: 'Orbitron', sans-serif; font-size: 1.2rem; color: #00f0ff; font-weight: 700; opacity: 0.6; }
.gi-content strong { display: block; font-size: 1rem; color: #fff; margin-bottom: 4px; }
.gi-content p { font-size: 0.85rem; color: #94a3b8; line-height: 1.4; margin: 0; }

.btn-start-battle { margin-top: 25px; width: 100%; padding: 16px; background: #00f0ff; color: #030712; border: none; font-family: 'Orbitron', sans-serif; font-weight: 900; letter-spacing: 2px; cursor: pointer; transition: all 0.3s; box-shadow: 0 0 20px rgba(0, 240, 255, 0.3); border-radius: 4px; }
.btn-start-battle:hover { background: #fff; transform: translateY(-2px); box-shadow: 0 0 30px rgba(0, 240, 255, 0.5); }
.waiting-info { margin-top: 20px; font-size: 0.9rem; color: #64748b; font-family: 'Orbitron', sans-serif; }
.glitch::before,.glitch::after{content:attr(data-text);position:absolute;top:0;left:0;width:100%;height:100%}
.glitch::before{color:#ff2d75;clip-path:inset(0 0 65% 0);animation:g1 2s infinite linear alternate-reverse}
.glitch::after{color:#39ff14;clip-path:inset(65% 0 0 0);animation:g2 2s infinite linear alternate-reverse}
@keyframes g1{0%{transform:translate(0)}50%{transform:translate(-3px,2px)}100%{transform:translate(0)}}
@keyframes g2{0%{transform:translate(0)}50%{transform:translate(3px,-2px)}100%{transform:translate(0)}}
.neon-border{border:1px solid #00f0ff;box-shadow:0 0 15px rgba(0,240,255,0.2)}

/* [수정일: 2026-02-24] AI REVIEW BOARD 스타일 */
.ai-review-board { margin-top: 20px; background: rgba(0, 240, 255, 0.05); border-radius: 12px; padding: 15px; text-align: left; animation: fadeIn 0.5s ease-out; }
.ari-header { display: flex; align-items: center; margin-bottom: 10px; border-bottom: 1px solid rgba(0, 240, 255, 0.2); padding-bottom: 5px; }
.ari-label { font-family: 'Orbitron', sans-serif; font-size: 0.75rem; font-weight: 900; color: #00f0ff; letter-spacing: 2px; }
.ari-content { display: flex; flex-direction: column; gap: 8px; }
.ari-my, .ari-comp { font-size: 0.85rem; line-height: 1.5; color: #e0f2fe; margin: 0; }
.ari-my strong, .ari-comp strong { color: #00f0ff; font-family: 'Orbitron', sans-serif; font-size: 0.7rem; margin-right: 8px; }
.ari-loading { font-size: 0.65rem; color: #64748b; font-style: italic; margin-left: auto; animation: bla 1s infinite; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* LOBBY */
.intro-screen{display:flex;align-items:center;justify-content:center;min-height:100vh}
.intro-box{text-align:center;background:rgba(8,12,30,.85);border:2px solid #00f0ff;border-radius:1.5rem;padding:2.5rem 3.5rem;box-shadow:0 0 40px rgba(0,240,255,.12);max-width:500px}
.logo{font-size:3rem;font-weight:900;color:#00f0ff;letter-spacing:6px;text-shadow:0 0 20px #00f0ff}
.sub-logo{color:#94a3b8;margin:.3rem 0 0.5rem;letter-spacing:3px}

/* [수정일: 2026-02-24] 방 관리 UI 스타일 */
.lobby-room-manager { margin: 1.5rem 0; padding: 1rem; background: rgba(0,0,0,0.3); border-radius: 12px; border: 1px solid rgba(0,240,255,0.1); }
.room-id-label { font-family: 'Orbitron', sans-serif; font-size: 0.6rem; color: #64748b; letter-spacing: 2px; margin-bottom: 6px; }
.room-input-group { display: flex; gap: 8px; justify-content: center; margin-bottom: 8px; }
.room-input { background: #0a0f1e; border: 1px solid #1e293b; color: #fff; padding: 6px 12px; border-radius: 4px; font-family: 'Orbitron', sans-serif; font-size: 0.8rem; width: 160px; text-align: center; }
.room-input:focus { border-color: #00f0ff; outline: none; box-shadow: 0 0 10px rgba(0,240,255,0.2); }
.btn-join { background: #1e293b; border: 1px solid #334155; color: #00f0ff; padding: 6px 16px; border-radius: 4px; font-family: 'Orbitron', sans-serif; font-size: 0.75rem; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.btn-join:hover { background: #00f0ff; color: #030712; }
.current-room-info { font-size: 0.75rem; color: #64748b; }
.lobby-players{display:flex;justify-content:center;flex-wrap:wrap;gap:1.5rem 2.5rem;margin:2rem 0;max-height:120px;overflow-y:auto;padding:10px}
.lp{display:flex;align-items:center;gap:.5rem;font-size:1.1rem;font-weight:700;color:#00f0ff;background:rgba(0,240,255,0.05);padding:4px 12px;border-radius:20px;border:1px solid rgba(0,240,255,0.1)}
.lp.waiting{color:#334155}
.lp-icon{font-size:1.3rem}
.blink{animation:bla 1s infinite}@keyframes bla{50%{opacity:.3}}
.lobby-info{color:#64748b;font-size:.85rem;margin:.5rem 0}
.btn-start{margin-top:1rem;padding:.8rem 2.5rem;font-family:'Orbitron',sans-serif;font-size:1rem;font-weight:700;background:transparent;border:2px solid #ffe600;color:#ffe600;border-radius:.5rem;cursor:pointer;letter-spacing:3px;transition:all .2s}
.btn-start:hover{background:rgba(255,230,0,.08);box-shadow:0 0 25px rgba(255,230,0,.3);transform:scale(1.05)}
.blink-border{animation:bb 1.5s infinite}@keyframes bb{0%,100%{border-color:#ffe600}50%{border-color:rgba(255,230,0,.3)}}
.lobby-how{text-align:left;margin:1.5rem auto 0;max-width:340px}
.how-s{display:flex;align-items:center;gap:.5rem;margin:.3rem 0;font-size:.8rem;color:#64748b}
.sn{width:20px;height:20px;display:flex;align-items:center;justify-content:center;background:rgba(0,240,255,.1);color:#00f0ff;border-radius:50%;font-family:'Orbitron',sans-serif;font-size:.55rem;font-weight:700;flex-shrink:0}

/* HUD */
.hud{display:flex;align-items:center;gap:1.2rem;padding:.6rem 1.2rem;margin:.75rem 1.2rem 0;background:rgba(8,12,30,.85);border:1px solid rgba(0,240,255,.1);border-radius:.75rem}
.hud-cell{display:flex;flex-direction:column;align-items:center}
/* [수정일: 2026-02-24] 멀티 인벤토리 HUD 스타일 */
.inventory-cell { flex: 3; align-items: stretch; padding: 0 15px; border-left: 2px solid rgba(0,240,255,0.1); border-right: 2px solid rgba(0,240,255,0.1); background: rgba(0,240,255,0.03); }
.inventory-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
.item-gauge-mini { width: 60px; height: 4px; background: rgba(0,0,0,0.3); border-radius: 2px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05); }
.item-gauge-fill-mini { height: 100%; background: #39ff14; box-shadow: 0 0 5px #39ff14; transition: width 0.3s ease; }

.inventory-bar { display: flex; gap: 6px; justify-content: space-between; }
.inv-slot { position: relative; flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.05); border-radius: 6px; padding: 4px 0; cursor: pointer; transition: all 0.2s; opacity: 0.4; }
.inv-slot.has-stock { opacity: 1; border-color: rgba(0,240,255,0.3); box-shadow: 0 0 10px rgba(0,240,255,0.1); }
.inv-slot.has-stock:hover { transform: translateY(-2px); border-color: #00f0ff; background: rgba(0,240,255,0.1); }

.inv-key { position: absolute; top: -2px; left: 4px; font-family: 'Orbitron', sans-serif; font-size: 0.45rem; color: #64748b; font-weight: 900; }
.inv-slot.has-stock .inv-key { color: #00f0ff; }
.inv-icon { font-size: 1rem; margin-bottom: 1px; }
.inv-count { font-family: 'Orbitron', sans-serif; font-size: 0.55rem; font-weight: 700; color: #fff; }
.inv-slot.has-stock .inv-count { color: #b6ff40; text-shadow: 0 0 5px rgba(182,255,64,0.5); }

/* [수정일: 2026-02-24] 커닝 방지 오버레이 스타일 */
.opp-canvas.obscured { border-style: solid; background: rgba(0,0,0,0.6); }
.obscure-overlay { position: absolute; inset: 0; z-index: 50; display: flex; flex-direction: column; align-items: center; justify-content: center; backdrop-filter: blur(8px); background: repeating-linear-gradient(45deg, rgba(0,0,0,0.4), rgba(0,0,0,0.4) 10px, rgba(0,0,0,0.5) 10px, rgba(0,0,0,0.5) 20px); }
.obs-icon { font-size: 2.5rem; margin-bottom: 10px; opacity: 0.8; }
.obs-txt { font-family: 'Orbitron', sans-serif; font-size: 1.2rem; font-weight: 900; color: #ff2d75; letter-spacing: 4px; text-shadow: 0 0 10px rgba(255,45,117,0.5); }
.obs-sub { font-size: 0.75rem; color: #64748b; margin-top: 5px; }

/* [수정일: 2026-02-24] 투시(Scan) 아이템 효과 스타일 */
.scan-active-info { position: absolute; top: 10px; left: 50%; transform: translateX(-50%); z-index: 60; background: rgba(0, 240, 255, 0.2); color: #00f0ff; padding: 4px 12px; border-radius: 20px; font-family: 'Orbitron', sans-serif; font-size: 0.7rem; font-weight: 700; border: 1px solid #00f0ff; box-shadow: 0 0 15px rgba(0,240,255,0.4); pointer-events: none; animation: bla 1s infinite; }

/* [수정일: 2026-02-24] 먹물 및 글리치 효과 */
.ink-overlay { position: fixed; inset: 0; pointer-events: none; z-index: 9500; }
.ink-splat { position: absolute; width: 120px; height: 120px; background: #000; border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%; filter: blur(3px); pointer-events: none; transition: opacity 0.5s; }
.glitch-screen .cnode { animation: glitch-node 0.2s infinite; }
@keyframes glitch-node {
  0% { transform: translate(0); }
  25% { transform: translate(-3px, 1px); filter: hue-rotate(90deg); }
  50% { transform: translate(2px, -2px); }
  75% { transform: translate(-1px, 2px); filter: hue-rotate(-90deg); }
  100% { transform: translate(0); }
}
@keyframes glitchAnim {
  0% { transform: translate(0); }
  20% { transform: translate(-2px, 2px); }
  40% { transform: translate(-2px, -2px); }
  60% { transform: translate(2px, 2px); }
  80% { transform: translate(2px, -2px); }
  100% { transform: translate(0); }
}

/* [추가 2026-02-27] Chaos Overlay Styles */
.chaos-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  z-index: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.chaos-box {
  width: 100%;
  max-width: 500px;
  background: #030712;
  border: 2px solid #ff2d75;
  box-shadow: 0 0 30px rgba(255, 45, 117, 0.3), inset 0 0 15px rgba(255, 45, 117, 0.1);
  border-radius: 8px;
  overflow: hidden;
  animation: chaosPop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
@keyframes chaosPop {
  from { transform: scale(0.8) translateY(20px); opacity: 0; }
  to { transform: scale(1) translateY(0); opacity: 1; }
}
.chaos-header {
  background: #ff2d75;
  padding: 10px 15px;
  color: #fff;
  font-weight: bold;
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
}
.chaos-scanner {
  position: absolute;
  top: 0; left: -100%; width: 50%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  animation: chaosScan 2s infinite;
}
@keyframes chaosScan {
  to { left: 200%; }
}
.chaos-body {
  padding: 25px;
  text-align: left;
}
.chaos-title {
  color: #fff;
  font-size: 22px;
  margin-bottom: 12px;
  text-shadow: 0 0 10px rgba(255,255,255,0.3);
}
.chaos-desc {
  color: #94a3b8;
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 20px;
}
.chaos-hint {
  background: rgba(0, 240, 255, 0.05);
  border-left: 3px solid #00f0ff;
  padding: 12px 15px;
  border-radius: 4px;
}
.ch-lab {
  color: #00f0ff;
  font-weight: bold;
  font-size: 11px;
  margin-right: 8px;
}
.ch-val {
  color: #e2e8f0;
  font-size: 13px;
}
.chaos-footer {
  padding: 15px 25px 25px;
  display: flex;
  justify-content: flex-end;
}
.btn-chaos-ack {
  background: transparent;
  border: 1px solid #ff2d75;
  color: #ff2d75;
  padding: 8px 24px;
  border-radius: 4px;
  font-weight: bold;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-chaos-ack:hover {
  background: #ff2d75;
  color: #fff;
}
.severity-critical { border-color: #ff0000; box-shadow: 0 0 30px rgba(255,0,0,0.4); }
.severity-critical .chaos-header { background: #ff0000; }
.severity-high { border-color: #ff2d75; }
.severity-medium { border-color: #f59e0b; }
.severity-medium .chaos-header { background: #f59e0b; }

.chaos-fade-enter-active, .chaos-fade-leave-active { transition: opacity 0.3s; }
.chaos-fade-enter-from, .chaos-fade-leave-to { opacity: 0; }

.hl{font-size:.5rem;font-weight:700;color:#475569;letter-spacing:2px}
.hv{font-family:'Orbitron',sans-serif;font-size:1.3rem;font-weight:900}
.dim{color:#334155;font-size:.7rem}
.tcell{flex:1;align-items:stretch;gap:2px}.ttrack{width:100%;height:5px;background:#0f172a;border-radius:3px;overflow:hidden}.tfill{height:100%;background:linear-gradient(90deg,#00f0ff,#38bdf8);border-radius:3px;transition:width 1s linear}.tcell.danger .tfill{background:linear-gradient(90deg,#ff2d75,#ef4444)}.tnum{font-family:'Orbitron',sans-serif;font-size:.65rem;color:#94a3b8;text-align:center}.tcell.danger .tnum{color:#ff2d75;animation:bla .5s infinite}
.combo-pill{font-family:'Orbitron',sans-serif;font-size:.75rem;font-weight:700;padding:.15rem .5rem;border:1px solid currentColor;border-radius:.25rem}
/* MISSION */
.mission{display:flex;align-items:center;gap:.6rem;margin:.4rem 1.2rem;padding:.5rem .8rem;background:rgba(8,12,30,.7);border:1px solid rgba(0,240,255,.08);border-radius:.6rem;font-size:.9rem}
.m-ico{font-size:1.2rem}.m-txt{display:flex;flex-direction:column;flex:1;gap:.05rem}.m-txt span{font-size:.75rem;color:#64748b}
.m-req{display:flex;flex-direction:column;align-items:center}.rl{font-size:.45rem;color:#475569;font-weight:700;letter-spacing:1.5px}.rn{font-family:'Orbitron',sans-serif;font-size:1.3rem;font-weight:900}
/* [Multi-Agent] CoachAgent 힌트 토스트 */
.coach-toast{display:flex;align-items:center;gap:.5rem;margin:.2rem 1.2rem 0;padding:.4rem .8rem;background:rgba(0,240,255,.06);border:1px solid rgba(0,240,255,.2);border-radius:.4rem;font-size:.78rem;color:#a5f3fc;animation:coachPulse 4s ease-in-out infinite}
.coach-icon{font-size:.9rem;flex-shrink:0}
.coach-text{line-height:1.4}
.coach-slide-enter-active{transition:all .35s ease-out}
.coach-slide-leave-active{transition:all .3s ease-in}
.coach-slide-enter-from{opacity:0;transform:translateY(-6px)}
.coach-slide-leave-to{opacity:0;transform:translateY(-6px)}
@keyframes coachPulse{0%,100%{border-color:rgba(0,240,255,.2);box-shadow:none}50%{border-color:rgba(0,240,255,.5);box-shadow:0 0 10px rgba(0,240,255,.1)}}

/* SPLIT VIEW */
.split-view{display:grid;grid-template-columns:1fr 30px 1fr;gap:0;padding:0 1.2rem;height:calc(100vh - 210px);min-height:0}
.my-workspace,.opp-workspace{display:flex;flex-direction:column;gap:.4rem;min-height:0}
.ws-header{display:flex;align-items:center;justify-content:space-between;gap:.5rem}
.ws-tag{font-family:'Orbitron',sans-serif;font-size:.6rem;font-weight:700;padding:2px 8px;border-radius:3px;letter-spacing:1px}
.you-tag{background:rgba(0,240,255,.1);color:#00f0ff}
.opp-tag{background:rgba(255,45,117,.1);color:#ff2d75}
.submitted-badge{font-size:.6rem;color:#39ff14;font-weight:700}

/* [수정일: 2026-02-24] 아이템 배지 스타일 */
.item-ready-badge { font-size: 0.65rem; font-weight: 700; color: #ff9d00; background: rgba(255,157,0,0.1); padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(255,157,0,0.3); margin-left: 5px; }
.pulse-neon { animation: pulse-item 1.5s infinite; }
@keyframes pulse-item { 0%, 100% { transform: scale(1); opacity: 1; box-shadow: 0 0 5px rgba(255,157,0,0.2); } 50% { transform: scale(1.05); opacity: 0.8; box-shadow: 0 0 12px rgba(255,157,0,0.4); } }
.mode-toggle{display:flex;border:1px solid #1e293b;border-radius:.35rem;overflow:hidden}
.mode-toggle button{padding:.2rem .5rem;background:transparent;border:none;color:#475569;font-size:.7rem;cursor:pointer}
.mode-toggle button.active{background:rgba(0,240,255,.1);color:#00f0ff}

/* PALETTE */
.palette{display:flex;flex-wrap:wrap;gap:.25rem;padding:.3rem 0}
.pal-chip{display:flex;align-items:center;gap:.2rem;padding:.25rem .45rem;border-radius:.3rem;background:#0a0f1e;border:1.5px solid #1e293b;color:#cbd5e1;font-size:.7rem;cursor:grab;transition:all .15s;user-select:none}
.pal-chip:hover{border-color:#00f0ff;transform:translateY(-1px);box-shadow:0 3px 8px rgba(0,240,255,.1)}
.pal-chip.used{opacity:.4}
.pi{font-size:.8rem}.pn{font-weight:600}

/* CANVAS */
.canvas-wrap,.opp-canvas{position:relative;flex:1;background:rgba(8,12,30,.4);border:2px dashed rgba(0,240,255,.12);border-radius:.75rem;overflow:hidden;min-height:0}
.opp-canvas{border-color:rgba(255,45,117,.12)}
.canvas-hint,.opp-empty{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#1e293b;font-size:.85rem;pointer-events:none}
.arrow-svg{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}
.aline{stroke:#00f0ff;stroke-width:2;opacity:.7}.aline.drawing{stroke-dasharray:6 4;opacity:.5}
.opp-arrow{stroke:#ff2d75}
.cnode{position:absolute;display:flex;align-items:center;gap:.2rem;padding:.3rem .5rem;background:#0f172a;border:1.5px solid #334155;border-radius:.4rem;cursor:pointer;user-select:none;transition:all .15s;z-index:10;font-size:.7rem}
.cnode:hover{border-color:#00f0ff;box-shadow:0 0 8px rgba(0,240,255,.15)}
.cnode.sel{border-color:#ffe600;box-shadow:0 0 12px rgba(255,230,0,.2)}
.cnode.opp-node{border-color:rgba(255,45,117,.3);cursor:default;pointer-events:none}
.ni{font-size:.85rem}.nn{font-weight:700}
.nd{position:absolute;top:-5px;right:-5px;width:14px;height:14px;background:rgba(255,45,117,.2);border:none;color:#ff2d75;border-radius:50%;cursor:pointer;font-size:.45rem;display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity .15s}
.cnode:hover .nd{opacity:1}

.split-divider{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.3rem;color:#334155;font-family:'Orbitron',sans-serif;font-size:.7rem;font-weight:700}
.dv-line{width:1px;flex:1;background:linear-gradient(to bottom,transparent,#1e293b,transparent)}

/* TOOLBAR */
.toolbar{display:flex;align-items:center;justify-content:center;gap:.75rem;padding:.4rem 1.2rem}
.btn-submit{padding:.5rem 2rem;font-family:'Orbitron',sans-serif;font-size:.8rem;font-weight:700;background:transparent;border:2px solid #00f0ff;color:#00f0ff;border-radius:.5rem;cursor:pointer;letter-spacing:2px;transition:all .2s}
.btn-submit:hover:not(:disabled){background:rgba(0,240,255,.08);box-shadow:0 0 15px rgba(0,240,255,.2);transform:translateY(-2px)}
.btn-submit:disabled{border-color:#1e293b;color:#334155;cursor:not-allowed}
.btn-clear{padding:.5rem .7rem;background:transparent;border:1px solid #334155;color:#64748b;border-radius:.5rem;cursor:pointer}

/* OVERLAYS */
.overlay{position:fixed;inset:0;background:rgba(0,0,0,.75);backdrop-filter:blur(4px);display:flex;align-items:center;justify-content:center;z-index:100}
.dark-ov{background:rgba(0,0,0,.9)}
/* JUDGING PHASE */
.judge-container { width: 95%; max-width: 1100px; display: flex; flex-direction: column; gap: 1.5rem; animation: slideUp 0.5s ease-out; }
@keyframes slideUp { from { transform: translateY(30px); opacity: 0 } to { transform: translateY(0); opacity: 1 } }

.judge-header { display: flex; align-items: center; gap: 1.5rem; background: rgba(15,23,42,.8); padding: 1rem 2rem; border-left: 4px solid #00f0ff; border-radius: .5rem; }
.jh-txt h2 { font-family: 'Orbitron', sans-serif; font-size: 1.4rem; font-weight: 900; letter-spacing: 2px; margin-bottom: .2rem; }
.jh-txt p { color: #94a3b8; font-size: .85rem; }

.judge-view { display: flex; align-items: stretch; gap: 1.5rem; width: 100%; min-height: 500px; }
.jv-side { flex: 1; display: flex; flex-direction: column; gap: .75rem; min-width: 0; }
.jv-tag { font-family: 'Orbitron', sans-serif; font-size: .65rem; font-weight: 700; color: #fff; padding: 4px 12px; border-radius: 4px; display: inline-block; align-self: flex-start; letter-spacing: 1px; flex-shrink: 0; }
.you-tag { background: #00f0ff; color: #000; box-shadow: 0 0 10px rgba(0,240,255,.3); }
.opp-tag { background: #ff2d75; color: #fff; box-shadow: 0 0 10px rgba(255,45,117,.3); }

.jv-canvas { position: relative; flex: 1; min-height: 450px; background: rgba(8,12,30,.6); border: 2px solid rgba(0,240,255,0.2); border-radius: 1rem; overflow: hidden; box-shadow: inset 0 0 20px rgba(0,0,0,.4); }
.jv-transform-wrapper { position: absolute; inset: 0; width: 100%; height: 100%; transition: all 0.5s ease; }
.canvas-svg { position: absolute; inset: 0; pointer-events: none; }
.jv-divider { display: flex; align-items: center; font-family: 'Orbitron', sans-serif; font-size: 1.5rem; font-weight: 900; color: #1e293b; text-shadow: 0 0 10px rgba(255,255,255,.05); flex-shrink: 0; }

.spinner{width:36px;height:36px;border:3px solid #1e293b;border-top-color:#00f0ff;border-radius:50%;animation:spin .8s linear infinite;}@keyframes spin{to{transform:rotate(360deg)}}

/* ITEM ALERT TOAST */
.item-alert-toast { position: fixed; top: 15%; left: 50%; transform: translateX(-50%); background: rgba(255,45,117,.1); border: 2px solid #ff2d75; border-radius: .75rem; padding: 1rem 2.5rem; display: flex; align-items: center; gap: 1rem; color: #ff2d75; font-family: 'Orbitron', sans-serif; font-weight: 900; backdrop-filter: blur(8px); z-index: 200; box-shadow: 0 0 30px rgba(255,45,117,.2); animation: alertShake 0.4s infinite; }
.ia-ico { font-size: 1.5rem; }
.ia-msg { font-size: 1.1rem; letter-spacing: 1px; }

@keyframes alertShake { 0%, 100% { transform: translateX(-50%) rotate(0); } 25% { transform: translateX(-52%) rotate(-1deg); } 75% { transform: translateX(-48%) rotate(1deg); } }

.slide-fade-enter-active { transition: all 0.3s ease-out; }
.slide-fade-leave-active { transition: all 0.4s cubic-bezier(1, 0.5, 0.8, 1); }
.slide-fade-enter-from, .slide-fade-leave-to { transform: translateX(-50%) translateY(-20px); opacity: 0; }

.result-box{background:rgba(8,12,30,.95);border:2px solid;border-radius:1.25rem;padding:2rem;text-align:center;max-width:520px;width:90%}
.res-win{border-color:#39ff14;box-shadow:0 0 25px rgba(57,255,20,.12)}
.res-draw{border-color:#ffe600}.res-lose{border-color:#ff2d75}
.r-ico{font-size:2rem}.r-title{font-family:'Orbitron',sans-serif;font-size:1.5rem;font-weight:900;margin:.2rem 0}
.res-win .r-title{color:#39ff14}.res-draw .r-title{color:#ffe600}.res-lose .r-title{color:#ff2d75}
.r-compare{display:grid;grid-template-columns:1fr 30px 1fr;align-items:start;gap:.5rem;margin:.75rem 0}
.rc-side{display:flex;flex-direction:column;align-items:center;gap:.3rem}
.rc-tag{font-family:'Orbitron',sans-serif;font-size:.55rem;font-weight:700;padding:2px 8px;border-radius:3px}
.rc-score{font-family:'Orbitron',sans-serif;font-size:1.5rem;font-weight:900}
.rc-vs{font-family:'Orbitron',sans-serif;color:#334155;font-weight:900;align-self:center;margin-top:20px}
.rc-header{font-family:'Orbitron',sans-serif;font-size:0.55rem;font-weight:700;color:#00f0ff;letter-spacing:1px;margin:8px 0 4px;opacity:0.8}
.rc-checks{text-align:left;font-size:.65rem;width:100%}
.chk{padding:.1rem .3rem;border-radius:.2rem;margin:.1rem 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.chk-ok{color:#39ff14;background:rgba(57,255,20,.04)}.chk-ok-opp{color:#ff2d75;background:rgba(255,45,117,.04)}.chk-miss{color:#334155;background:rgba(51,65,85,.04)}
.btn-next{width:100%;padding:.6rem;font-family:'Orbitron',sans-serif;font-size:.75rem;font-weight:700;background:transparent;border:2px solid #00f0ff;color:#00f0ff;border-radius:.5rem;cursor:pointer;letter-spacing:2px;transition:all .2s;margin-top:.5rem}
.btn-next:hover{background:rgba(0,240,255,.08);transform:translateY(-2px)}

/* GAME OVER */
.go-box{text-align:center}.go-title{font-size:2.5rem;font-weight:900;color:#00f0ff;letter-spacing:4px;margin-bottom:.75rem}
.go-final{display:flex;align-items:center;justify-content:center;gap:1.5rem;margin:1rem 0}
.go-fs{display:flex;flex-direction:column;align-items:center}.go-fs span{font-size:.6rem;color:#475569;font-weight:700}.go-fs strong{font-family:'Orbitron',sans-serif;font-size:2.5rem;font-weight:900}
.go-vs{font-family:'Orbitron',sans-serif;font-size:1rem;color:#ff2d75;font-weight:900}
.go-verdict{font-family:'Orbitron',sans-serif;font-size:1.5rem;font-weight:900;color:#ffe600;margin:.5rem 0}
/* 포트폴리오 export 스타일 */
.go-portfolio { margin: 1rem 0 0.5rem; text-align: left; }
.go-pf-title { font-family: 'Orbitron', sans-serif; font-size: .65rem; color: #00f0ff; letter-spacing: 2px; margin-bottom: .6rem; text-align: center; }
.go-pf-preview {
  background: linear-gradient(135deg, #030712, #0f172a);
  border: 1px solid rgba(0,240,255,0.25); border-radius: .75rem;
  padding: 1rem; display: flex; flex-direction: column; gap: .6rem;
  margin-bottom: .75rem;
}
.gpf-badge { font-size: .55rem; font-weight: 700; letter-spacing: 1px; padding: 3px 10px; border-radius: 4px; background: rgba(0,240,255,.08); color: #00f0ff; border: 1px solid rgba(0,240,255,.2); display: inline-block; }
.gpf-mission { font-size: .85rem; font-weight: 800; color: #f1f5f9; }
.gpf-desc { font-size: .7rem; color: #64748b; line-height: 1.4; border-left: 2px solid rgba(0,240,255,.2); padding-left: .5rem; }
.gpf-components { display: flex; flex-wrap: wrap; gap: .3rem; }
.gpf-comp { font-size: .65rem; padding: 2px 8px; background: rgba(0,240,255,.08); border: 1px solid rgba(0,240,255,.15); border-radius: 4px; color: #e0f2fe; }
.gpf-comp-more { font-size: .65rem; padding: 2px 8px; color: #475569; }
.gpf-score-row { display: flex; gap: .75rem; align-items: center; flex-wrap: wrap; }
.gpf-sl { font-size: .55rem; color: #475569; font-family: 'Orbitron', sans-serif; letter-spacing: 1px; }
.gpf-sv { font-size: .85rem; font-weight: 700; font-family: 'Orbitron', sans-serif; }
.gpf-ai { font-size: .65rem; color: #64748b; }
.gpf-ai-label { color: #00f0ff; font-weight: 700; margin-right: .3rem; }
.gpf-footer { font-size: .55rem; color: #1e293b; font-family: monospace; padding-top: .5rem; border-top: 1px solid rgba(255,255,255,.04); }
.go-pf-actions { display: flex; gap: .5rem; margin-bottom: .5rem; flex-wrap: wrap; }
.go-pf-btn { padding: .45rem 1rem; border-radius: .5rem; font-size: .7rem; font-weight: 700; cursor: pointer; border: none; transition: all .2s; }
.go-pf-btn.cyan { background: rgba(0,240,255,.1); border: 1px solid rgba(0,240,255,.3); color: #00f0ff; }
.go-pf-btn.cyan:hover { background: rgba(0,240,255,.18); }
.go-pf-btn.purple { background: rgba(168,85,247,.1); border: 1px solid rgba(168,85,247,.3); color: #a855f7; }
.go-pf-btn.purple:hover { background: rgba(168,85,247,.18); }
.go-pf-btn.gray { background: rgba(100,116,139,.1); border: 1px solid rgba(100,116,139,.3); color: #64748b; }
.go-pf-btn.gray:hover { background: rgba(100,116,139,.18); }
.go-pf-toast { font-size: .7rem; color: #22c55e; padding: .3rem .7rem; background: rgba(34,197,94,.1); border: 1px solid rgba(34,197,94,.25); border-radius: .4rem; display: inline-block; }

.go-btns{display:flex;gap:1rem;margin-top:1rem}
.btn-retry{flex:1;padding:.65rem;font-family:'Orbitron',sans-serif;font-size:.75rem;font-weight:700;background:transparent;border:2px solid #00f0ff;color:#00f0ff;border-radius:.6rem;cursor:pointer}.btn-retry:hover{background:rgba(0,240,255,.1)}
.btn-exit{flex:1;padding:.65rem;font-family:'Orbitron',sans-serif;font-size:.75rem;font-weight:700;background:transparent;border:1px solid #334155;color:#64748b;border-radius:.6rem;cursor:pointer}

.fpop-layer{position:fixed;inset:0;pointer-events:none;z-index:500}
.fpop-item{position:absolute;top:40%;font-family:'Orbitron',sans-serif;font-size:1.3rem;font-weight:900;color:#ffe600;text-shadow:0 0 10px rgba(255,230,0,.5)}
.fpop-enter-active{animation:fUp 1.2s ease-out forwards}
@keyframes fUp{0%{opacity:1;transform:translateY(0) scale(1.2)}100%{opacity:0;transform:translateY(-90px) scale(.8)}}
.zoom-enter-active{animation:zIn .3s ease}@keyframes zIn{from{transform:scale(.7);opacity:0}to{transform:scale(1);opacity:1}}
</style>
