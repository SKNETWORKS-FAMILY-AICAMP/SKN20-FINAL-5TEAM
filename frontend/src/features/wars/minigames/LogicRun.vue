<template>
  <div class="logic-run" :class="{ 'shake': shaking, 'flash-ok': flashOk, 'flash-fail': flashFail }">
    <div class="crt-lines"></div>

    <!-- ===== INTRO ===== -->
    <div v-if="phase === 'intro'" class="intro-screen">
      <div class="intro-box">
        <div class="intro-badge">AI PURSUIT MODE</div>
        <h1 class="intro-title glitch" data-text="LOGIC RUN">LOGIC RUN</h1>
        <p class="intro-sub">AI의 추격을 뿌리치고 논리의 성으로 질주하라!</p>
        <div class="intro-rules">
          <div class="rule-item">🏃 의사코드를 한 줄씩 입력하면 캐릭터가 전진</div>
          <div class="rule-item">🤖 AI 추격자에게 잡히면 게임 오버</div>
          <div class="rule-item">🔥 팀원이 바통을 이어받아 릴레이 질주</div>
          <div class="rule-item">⚡ 하이파이브 타이밍에 성공하면 대시 부스트!</div>
        </div>
        <div class="team-select">
          <p class="team-label">방 관리 (멀티플레이어)</p>
          <div class="room-input-group">
            <input v-model="inputRoomId" placeholder="방 번호 입력..." class="room-input" @keyup.enter="joinRoom" />
            <button @click="joinRoom" class="btn-join">입장/변경</button>
          </div>
          <div v-if="roomId" class="current-room-info">
            접속 중인 방: <span class="neon-c">{{ roomId }}</span>
            <div class="room-players">
              팀원: <span v-for="p in rs.roomPlayers.value" :key="p.sid" class="p-tag">{{ p.name }} </span>
            </div>
          </div>
          <div v-if="rs.connected.value && !rs.isReady.value" class="lobby-info">다른 팀원을 기다리는 중...</div>
          
          <p class="team-label" style="margin-top: 1rem;">모드 설정</p>
          <div class="team-btns">
            <button
              v-for="n in [2, 4, 6, 8]" :key="n"
              class="btn-team" :class="{ active: teamSize === n }"
              @click="teamSize = n"
            >{{ n }}명 ({{ n/2 }}vs{{ n/2 }})</button>
          </div>
          <p class="team-label" style="margin-top: 0.75rem; font-size: 0.65rem; color: #64748b;">
            🆚 팀A vs 팀B 대전! 같은 번호끼리 매칭됩니다.
          </p>
        </div>
        <button @click="requestStart" class="btn-start blink-border" :disabled="!rs.isReady.value">▶ START GAME</button>
      </div>
    </div>

    <!-- ===== PLAY ===== -->
    <div v-if="phase === 'play'" class="game-screen">
      <!-- 상단 HUD -->
      <div class="hud">
        <div class="hud-cell">
          <span class="hud-lbl">SECTOR</span>
          <span class="hud-val neon-c">{{ currentSector + 1 }} / {{ totalSectors }}</span>
        </div>
        <div class="hud-cell track-cell">
          <div class="track-bar">
            <div class="track-player" :style="{ left: playerPct + '%' }">
            <img :src="players[currentPlayerIdx]?.avatarUrl || '/image/duck_idle.png'" class="mini-avatar" />
            </div>
            <div class="track-ai" :style="{ left: aiPct + '%' }">
              <img src="/image/duck_det.png" class="mini-avatar ai-mini" />
            </div>
            <div class="track-fill player-fill" :style="{ width: playerPct + '%' }"></div>
            <div class="track-fill ai-fill" :style="{ width: team2Pct + '%' }"></div>
            <div class="track-goal">
              <img src="/image/unit_system.png" class="mini-goal" />
            </div>
          </div>
          <div class="track-labels">
            <span class="tl-you">팀A {{ Math.round(playerPct) }}%</span>
            <span class="tl-ai">팀B {{ Math.round(team2Pct) }}%</span>
          </div>
        </div>
        <div class="hud-cell">
          <span class="hud-lbl">SCORE</span>
          <span class="hud-val neon-y">{{ score }}</span>
        </div>
      </div>

      <!-- 게임 영역 -->
      <div class="game-area">
        <!-- 좌측: 게임 화면 -->
        <div class="game-left">
          <!-- 현재 주자 & 섹터 정보 -->
          <div class="sector-info">
            <span class="sector-badge">{{ currentSectorLabel }}</span>
            <span class="player-badge">
              {{ currentPlayerLabel }} 담당
            </span>
            <span v-if="aceMode && currentSector > 0" class="ace-badge">⚡ ACE</span>
          </div>

          <!-- 횡스크롤 캐릭터 영역 -->
          <!-- 듀얼 트랙 레이싱 영역 -->
          <div class="runner-stage dual-track">
            <!-- 상단: AI 레인 -->
            <div class="lane ai-lane">
              <div class="lane-label">팀B TRACK</div>
              <div class="ai-char" :style="{ left: team2Pct + '%' }" :class="{ visible: true }">
                <img :src="getTeam2Avatar()" class="main-ai" />
              </div>
            </div>

            <!-- 하단: 팀A 레인 -->
            <div class="lane player-lane">
              <div class="lane-label">팀A TRACK</div>
              <div class="runner-char" :style="{ left: playerPct + '%' }" :class="{ running: phase === 'play', stumble: stumbling }">
                <img :src="players[currentPlayerIdx]?.avatarUrl || '/image/duck_idle.png'" class="main-avatar" />
                <div class="baton" v-if="phase === 'play'"></div>
                <div class="dust-effect" v-if="phase === 'play'"></div>
              </div>
              <!-- 바통 패스 알림/말풍선 -->
              <div class="speech-bubble" v-if="lastCorrectLine && phase === 'play'" :style="{ left: playerPct + '%' }">
                <span>{{ lastCorrectLine }}</span>
              </div>
            </div>

            <!-- 결승선 -->
            <div class="finish-line">
              <div class="finish-icon">🏁</div>
            </div>

            <!-- 방해 요소 (플레이어 레인에 표시) -->
            <div class="obstacle logic-swamp" v-if="showObstacle === 'swamp'">🌊 논리 늪</div>
            <div class="obstacle spaghetti" v-if="showObstacle === 'spaghetti'">🔀 스파게티 존</div>
          </div>

          <!-- 팀원 상태 -->
          <div class="team-status">
            <div
              v-for="(p, idx) in players"
              :key="idx"
              class="player-pill"
              :class="{ active: idx === currentPlayerIdx, done: p.done }"
            >
              <img :src="p.avatarUrl" class="pp-avatar" />
              <span class="pp-name">{{ p.name }}</span>
              <span class="pp-lines">{{ p.completedLines }}줄</span>
            </div>
          </div>
        </div>

        <!-- 우측: 입력 + 레이더 -->
        <div class="game-right">
          <!-- 5대 지표 미니 -->
          <div class="metrics-panel">
            <div class="metrics-title">📊 실시간 지표</div>
            <div class="metric-row" v-for="m in metricList" :key="m.key">
              <span class="m-label">{{ m.label }}</span>
              <div class="m-bar-track">
                <div class="m-bar-fill" :style="{ width: metrics[m.key] + '%', background: m.color }"></div>
              </div>
              <span class="m-val">{{ Math.round(metrics[m.key]) }}</span>
            </div>
          </div>

          <!-- [개선: 2026-02-24] 미션 목표 상시 노출 -->
          <div class="mission-board neon-border">
            <div class="mb-ico">🎯</div>
            <div class="mb-content">
              <h3 class="mb-title">{{ currentQuest?.title }}</h3>
              <p class="mb-desc">{{ currentSectorData?.playerHint }}</p>
            </div>
            <div class="mb-stat">NEED <strong>{{ currentSectorLines.length }}</strong> LINES</div>
          </div>

          <!-- [개선: 2026-02-24] IDE 스타일 코드 에디터 패널 -->
          <div class="editor-panel neon-border">
            <div class="editor-header">
              <div class="editor-tabs">
                <div class="tab active">login_logic.ps</div>
                <div class="tab">auth_service.sys</div>
              </div>
              <div class="editor-meta">P{{ currentPlayerIdx + 1 }} EDITING...</div>
            </div>

            <div class="editor-body scrollbar">
              <!-- Gutter (Line Numbers) -->
              <div class="editor-gutter">
                <div v-for="n in 12" :key="n" class="line-num">{{ n }}</div>
              </div>

              <!-- Code Content -->
              <div class="editor-content">
                <!-- 이전 입력 라인들 (Context) -->
                <div v-for="(line, idx) in currentSectorLines.slice(0, currentLineIdx)" :key="'prev'+idx" class="code-line prev-line">
                  <span class="cl-text">{{ line.answer }}</span>
                </div>

                <!-- 현재 입력 힌트 및 입력창 -->
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
                      :disabled="phase !== 'play' || !isMyTurn"
                      autocomplete="off"
                      spellcheck="false"
                    />
                  </div>
                </div>

                <!-- 남은 라인들 (Placeholder) -->
                <div v-for="n in (currentSectorLines.length - currentLineIdx - 1)" :key="'next'+n" class="code-line next-line">
                  <span class="cl-dot">...</span>
                </div>
              </div>
            </div>

            <div class="editor-footer">
              <div class="ef-left">
                <div class="timeout-bar-container" v-if="phase === 'play'">
                  <div class="timeout-bar-track">
                    <div class="timeout-bar-fill" :style="{ width: lineTimeoutPct + '%' }" :class="{ danger: isTimeoutDanger }"></div>
                  </div>
                  <span class="timeout-text" :class="{ danger: isTimeoutDanger }">{{ lineTimeout }}s</span>
                </div>
                <span v-else>UTF-8 | Pseudocode | Sector {{ currentSector + 1 }}</span>
              </div>
              <div class="ef-right">
                <span class="err-msg" v-if="errorMsg">⚠️ {{ errorMsg }}</span>
                <button class="btn-ide-submit" @click="submitLine" :disabled="!userInput.trim()">RUN ↵</button>
              </div>
            </div>
          </div>

          <!-- 아이템 -->
          <div class="items-panel" v-if="activeItems.length > 0">
            <div class="item-pill" v-for="item in activeItems" :key="item.id">
              {{ item.icon }} {{ item.name }}
              <span class="item-timer">{{ item.remainSec }}s</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== RELAY (바통 패스) ===== -->
    <div v-if="phase === 'relay'" class="relay-screen">
      <div class="relay-box">
        <div class="relay-icon">🤝</div>
        <h2 class="relay-title">바통 패스!</h2>
        <p class="relay-desc">P{{ currentPlayerIdx }}의 섹터 완료!</p>
        <p class="relay-next">P{{ currentPlayerIdx + 1 }} 준비하세요</p>
        <div class="relay-timing">
          <div class="timing-bar" :style="{ width: relayTimerPct + '%' }"></div>
        </div>
        <div class="relay-pass-anim">
          <img :src="players[currentPlayerIdx]?.avatarUrl" class="pass-avatar" title="이전 주자" />
          <div class="pass-baton">👉 🥢 👉</div>
          <img :src="players[Math.min(currentPlayerIdx + 1, teamSize - 1)]?.avatarUrl" class="pass-avatar" title="다음 주자" />
        </div>
        <div class="relay-hint">타이밍에 맞춰 <kbd>SPACE</kbd> 또는 버튼을 눌러 바통을 터치하세요!</div>
        <button class="btn-highfive" @click="handleHighFive">✋ 하이파이브!</button>
        <div class="highfive-status" v-if="highFiveStatus">{{ highFiveStatus }}</div>
        <button class="btn-continue" @click="continueRelay">그냥 계속하기</button>
      </div>
    </div>

    <!-- ===== GAMEOVER ===== -->
    <transition name="zoom">
      <div v-if="phase === 'gameover'" class="overlay">
        <div class="gameover-box">
          <div class="go-icon">⚔️</div>
          <h1 class="go-title glitch" data-text="GAME OVER">GAME OVER</h1>
          <p class="go-desc">팀B에게 역전당했습니다!</p>
          <div class="go-caught-at">{{ team2Pct }}% 지점에서 추월당함</div>
          <div class="go-btns">
            <button @click="startGame" class="btn-retry">🔄 다시 도전</button>
            <button @click="$router.push('/practice/coduck-wars')" class="btn-exit">🏠 나가기</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- ===== COMPLETE ===== -->
    <transition name="zoom">
      <div v-if="phase === 'complete'" class="overlay">
        <div class="complete-box">
          <div class="cp-icon">🏰</div>
          <h1 class="cp-title">논리의 성 도달!</h1>
          <div class="cp-grade" :class="'g-' + finalGrade">{{ finalGrade }}</div>
          <div class="cp-score">{{ score }}<small>PTS</small></div>
          <div class="cp-metrics">
            <div class="cpm-row" v-for="m in metricList" :key="m.key">
              <span class="cpm-label">{{ m.label }}</span>
              <div class="cpm-bar">
                <div class="cpm-fill" :style="{ width: metrics[m.key] + '%', background: m.color }"></div>
              </div>
              <span class="cpm-val">{{ Math.round(metrics[m.key]) }}</span>
            </div>
          </div>
          <div class="cp-feedback">{{ gradeFeedback }}</div>
          <div class="cp-bonuses" v-if="bonuses.length">
            <div class="bonus-item" v-for="b in bonuses" :key="b">✨ {{ b }}</div>
          </div>
          <div class="go-btns">
            <button @click="startGame" class="btn-retry">🔄 다시 도전</button>
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
// 수정내용: 로직 런 - AI 제거 & 플레이어 vs 플레이어 구조로 변경
//  - 의사코드 릴레이 입력 → 캐릭터 전진
//  - 팀A(짝수) vs 팀B(홀수) 경쟁 구조
//  - 섹터 완료 시 바통 패스 + 하이파이브 ±300ms 판정
//  - 5대 지표 (일관성, 추상화, 예외처리, 구현력, 설계) 실시간 측정
//  - S~D 등급 최종 평가 화면

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
  // 실제 접속 인원 정보를 players 배열에 매핑 (이어달리기 핵심)
  const roomPlayers = rs.roomPlayers.value
  players.value = roomPlayers.map((p, idx) => ({
    id: idx,
    name: p.name,
    avatarUrl: p.avatar_url || '/image/duck_idle.png',
    done: false,
    completedLines: 0
  }))
  // 인원 부족 시 더미 데이터 추가 (혼자 테스트 시 등)
  while (players.value.length < teamSize.value) {
    players.value.push({ 
      id: players.value.length, 
      name: `CPU ${players.value.length + 1}`, 
      avatarUrl: '/image/duck_idle.png', 
      done: false, 
      completedLines: 0 
    })
  }

  startGame(true, qIdx)
}

rs.onSync.value = (data) => {
  // 내가 아닐 때만 원격 데이터를 내 로컬 상태에 동기화
  if (data.sid !== rs.socket.value?.id) {
    playerPos.value = data.playerPos
    currentPlayerIdx.value = data.playerIdx
    currentLineIdx.value = data.lineIdx
    currentSector.value = data.sectorIdx
    
    // 주자가 바뀐 경우 포커스 해제 등 처리
    if (currentPlayerIdx.value !== data.playerIdx) {
      // 릴레이 페이즈 진입 등은 onRelay에서 별도로 처리됨
    }
  }
  // 모든 클라이언트는 점수와 지표를 동기화
  if (data.score) score.value = data.score
  if (data.metrics) metrics.value = data.metrics
  // 마지막 정답 라인은 모든 클라이언트가 볼 수 있도록 동기화
  if (data.lastCorrectLine) lastCorrectLine.value = data.lastCorrectLine
}

rs.onRelay.value = (data) => {
  currentSector.value = data.sectorIdx
  phase.value = 'relay'
  sectorComplete(true)
}

rs.onHfSync.value = (data) => {
  if (data.status) highFiveStatus.value = data.status
  if (data.highFiveTime) highFiveTime = data.highFiveTime
  if (data.playerPos) playerPos.value = data.playerPos
  if (data.score) score.value = data.score
  if (data.triggerContinue) continueRelay(true)
}

// rs.onEnd (게임 종료 이벤트 수신)
rs.onEnd.value = (data) => {
  if (data.caught) {
    caughtAtPct.value = Math.round(data.playerPos)
    endGame('gameover')
  } else {
    // 성공 시 처리 (필요 시)
    // 현재는 sectorComplete에서 모든 섹터 완료 시 endGame('complete')를 직접 호출
    // 따라서 이 부분은 AI에게 잡혔을 때만 사용될 가능성이 높음
  }
}

// ─── 상태 ───────────────────────────────────────────
const phase = ref('intro')       // intro | play | relay | gameover | complete
const teamSize = ref(2)
const score = ref(0)
const shaking = ref(false)
const flashOk = ref(false)
const flashFail = ref(false)
const stumbling = ref(false)
const lastCorrectLine = ref('')
const errorMsg = ref('')
const userInput = ref('')
const showObstacle = ref(null)
const team2Pct_ = ref(0)  // 팀B의 진행도
const highFiveStatus = ref('')
const relayTimer = ref(10)
const lineTimeout = ref(20)  // 한 라인당 제한 시간 (초)
const isTimeoutActive = ref(false)
let relayInterval = null
let highFiveTime = null
let lineTimeoutInterval = null  // 한 라인 타임아웃 타이머

const currentSector = ref(0)
const currentPlayerIdx = ref(0)
const currentLineIdx = ref(0)
const currentTeam = ref('A')  // 현재 활성 팀 (A or B)

const playerPos = ref(0)   // 현재 활성 팀 진행도 (팀A 기준)
const playerPct = computed(() => Math.min(playerPos.value, 100))
const team2Pct = computed(() => Math.min(team2Pct_.value, 100))

// [동기화] 리더가 아닌 경우 서버에서 온 팀B 위치를 내 로컬에 강제 동기화
import { watch } from 'vue'
watch(() => rs.remoteAiPos.value, (newPos) => {
  if (!rs.isLeader.value) {
    team2Pct_.value = newPos
  }
})

// 아이템
const activeItems = ref([])
let itemIdCounter = 0

// fpop
const fpops = ref([])
let fpopId = 0

// 코드 입력 ref
const codeInput = ref(null)

// 5대 지표
const metrics = ref({ consistency: 50, abstraction: 50, exception: 50, implementation: 50, design: 50 })
const metricList = [
  { key: 'consistency',    label: '일관성', color: '#60a5fa' },
  { key: 'abstraction',    label: '추상화', color: '#a78bfa' },
  { key: 'exception',      label: '예외처리', color: '#f59e0b' },
  { key: 'implementation', label: '구현력', color: '#34d399' },
  { key: 'design',         label: '설계',  color: '#f472b6' },
]

// 플레이어 목록
const players = ref([])

// 팀 정보
const teamAPlayers = computed(() => players.value.filter((_, idx) => idx % 2 === 0))
const teamBPlayers = computed(() => players.value.filter((_, idx) => idx % 2 === 1))
const currentTeamPlayers = computed(() => currentTeam.value === 'A' ? teamAPlayers.value : teamBPlayers.value)

// 팀B 타이머
let team2Timer = null

// ─── 퀘스트 데이터 (섹터별 의사코드 라인) ───────────────
// [수정일: 2026-02-24] 의사코드 정체성 강화를 위해 표준 키워드(함수, 만약, 결과 등) 및 영문 혼용 규격 적용
const quests = [
  {
    title: '글로벌 로그인 아키텍처 구현',
    sectors: [
      {
        playerHint: '입력 보안 검증 (Security Validation)',
        lines: [
          { hint: '로그인 정보를 처리하는 함수 인터페이스 정의', answer: '함수 로그인_처리(사용자_이메일, 사용자_비번):', altAnswers: ['FUNCTION login_process(user_email, user_pw):'] },
          { hint: '이메일 형식의 유효성을 정규식을 통해 검사', answer: '  만약 이메일_형식_체크(사용자_이메일)가 아니면:', altAnswers: ['  IF NOT is_valid_email(user_email) THEN'] },
          { hint: '잘못된 입력에 대한 에러 객체 반환', answer: '    반환 오류("잘못된_이메일")', altAnswers: ['    RETURN ERROR("INVALID_EMAIL")'] },
          { hint: '비밀번호의 최소 길이(8자)를 검증', answer: '  만약 길이(사용자_비번) < 8 이면:', altAnswers: ['  IF LENGTH(user_pw) < 8 THEN'] },
          { hint: '정책 미달 시 보안 정책 예외 전달', answer: '    반환 오류("비밀번호_제한")', altAnswers: ['    RETURN ERROR("WEAK_PASSWORD")'] },
        ],
        consistencyVar: '사용자_이메일',
        obstacleAt: 3,
        obstacleType: 'swamp',
      },
      {
        playerHint: '데이터베이스 인증 (DB Authentication)',
        lines: [
          { hint: 'DB 서버로부터 사용자 계정 정보를 조회', answer: '사용자 = DB_유저_조회(사용자_이메일)', altAnswers: ['user = FETCH_USER_FROM_DB(user_email)'] },
          { hint: '조회된 사용자 데이터가 존재하는지 확인', answer: '만약 사용자가 비어있으면:', altAnswers: ['IF user IS NULL THEN'] },
          { hint: '사용자 미발견 시 에러 반환', answer: '    반환 오류("사용자_없음")', altAnswers: ['    RETURN ERROR("USER_NOT_FOUND")'] },
          { hint: '입력된 비밀번호와 해시값이 일치하는지 비교', answer: '만약 비번_검증(사용자_비번, 사용자.해시)이 실패면:', altAnswers: ['IF NOT BCRYPT_VERIFY(user_pw, user.hash) THEN'] },
          { hint: '불일치 시 권한 거부 예외 반환', answer: '    반환 오류("권한_없음")', altAnswers: ['    RETURN ERROR("UNAUTHORIZED")'] },
        ],
        consistencyVar: '사용자',
        obstacleAt: null,
        obstacleType: null,
      },
      {
        playerHint: '세션 발급 (Token Granting)',
        lines: [
          { hint: '인증 성공 후 새로운 세션 토큰 발행', answer: '토큰 = 토큰_생성(사용자.아이디)', altAnswers: ['token = JWT_SIGN(user.id, "HS256")'] },
          { hint: '최종 성공 결과와 토큰을 전달', answer: '반환 성공(토큰)', altAnswers: ['RETURN SUCCESS(token)'] },
        ],
        consistencyVar: '토큰',
        obstacleAt: 1,
        obstacleType: 'spaghetti',
      },
    ],
  },
]

// ─── 계산된 값 ───────────────────────────────────────
const totalSectors = computed(() => {
  if (!currentQuest.value) return 1
  return aceMode.value && teamSize.value === 3
    ? currentQuest.value.sectors.length
    : Math.min(teamSize.value, currentQuest.value.sectors.length)
})

// [동기화] 현재 주자가 나인지 판별
const isMyTurn = computed(() => {
  if (!rs.socket.value) return true // 로컬 테스트용
  const myIdx = rs.roomPlayers.value.findIndex(p => p.sid === rs.socket.value.id)
  return currentPlayerIdx.value === myIdx
})

const currentQuest = ref(null)
const currentSectorData = computed(() =>
  currentQuest.value?.sectors[currentSector.value] || null
)
const currentSectorLines = computed(() =>
  currentSectorData.value?.lines || []
)
const currentHint = computed(() =>
  currentSectorLines.value[currentLineIdx.value]?.hint || '완료!'
)
const currentSectorLabel = computed(() => `섹터 ${currentSector.value + 1}`)
const currentPlayerLabel = computed(() => {
  const team = currentPlayerIdx.value % 2 === 0 ? '팀A' : '팀B'
  const playerNum = Math.floor(currentPlayerIdx.value / 2) + 1
  return `${team} P${playerNum}`
})
const inputPlaceholder = computed(() =>
  currentSectorLines.value[currentLineIdx.value]?.answer
    ? `예: ${currentSectorLines.value[currentLineIdx.value].answer}`
    : '의사코드를 한글로 입력하세요...'
)

const bonuses = ref([])
const finalGrade = computed(() => {
  const avg = Object.values(metrics.value).reduce((a, b) => a + b, 0) / 5
  if (avg >= 88) return 'S'
  if (avg >= 75) return 'A'
  if (avg >= 60) return 'B'
  if (avg >= 45) return 'C'
  return 'D'
})
const gradeFeedback = computed(() => {
  const g = finalGrade.value
  if (g === 'S') return '🎉 완벽한 팀워크! 모든 지표가 빛납니다!'
  if (g === 'A') return '💪 훌륭합니다! 조금만 더 다듬으면 S등급!'
  if (g === 'B') return '👍 좋은 시작! 일관성을 더 신경 써보세요.'
  if (g === 'C') return '🌱 함께 더 많이 연습해봐요!'
  return '🔄 다시 도전해보세요!'
})
const relayTimerPct = computed(() => (relayTimer.value / 10) * 100)
const lineTimeoutPct = computed(() => (lineTimeout.value / 20) * 100)
const isTimeoutDanger = computed(() => lineTimeout.value <= 5)

// ─── 팀B 속도 설정 (CPM → ms per char) ────────────────
// 팀B는 팀A와 같은 속도로 진행 (공정한 경쟁)
const TEAM2_SPEEDS = { easy: 25, medium: 40, hard: 65 } // CPM
function getTeam2Difficulty() {
  // 현재는 medium 고정, 추후 레벨 시스템 연동
  return 'medium'
}
const team2Interval = computed(() => {
  const cpm = TEAM2_SPEEDS[getTeam2Difficulty()]
  // 캐릭터 1칸 전진 = 평균 8글자 → 전체 100칸 기준
  const totalChars = 800
  return Math.round((60000 / cpm) * (100 / totalChars) * 8)
})

// ─── 게임 시작 ────────────────────────────────────────
function startGame(fromSocket = false, qIdx = null) {
  if (qIdx !== null && quests[qIdx]) {
    currentQuest.value = quests[qIdx]
  } else {
    currentQuest.value = quests[Math.floor(Math.random() * quests.length)]
  }
  currentSector.value = 0
  currentPlayerIdx.value = 0
  currentLineIdx.value = 0
  currentTeam.value = 'A'  // 팀A부터 시작
  score.value = 0
  playerPos.value = 0
  team2Pct_.value = 0  // 팀B도 0에서 시작
  errorMsg.value = ''
  userInput.value = ''
  showObstacle.value = null
  lastCorrectLine.value = ''
  activeItems.value = []
  bonuses.value = []
  metrics.value = { consistency: 50, abstraction: 50, exception: 50, implementation: 50, design: 50 }

  // 플레이어 초기화 (멀티플레이어 아닐 때만 더미데이터로 초기화)
  if (!fromSocket) {
    players.value = Array.from({ length: teamSize.value }, (_, i) => ({
      name: `${i % 2 === 0 ? '팀A' : '팀B'} P${Math.floor(i/2) + 1}`,
      avatarUrl: '/image/duck_idle.png',
      completedLines: 0,
      done: false
    }))
  }

  phase.value = 'play'
  startTeam2Chase()
  // 첫 라인의 타임아웃 시작
  startLineTimeout()
  nextTick(() => codeInput.value?.focus())
}

// ─── 팀B 진행 시작 ────────────────────────────────────────
// [수정일: 2026-02-25] AI 제거 & 팀B 플레이어 진행도 계산
function startTeam2Chase() {
  if (team2Timer) clearInterval(team2Timer)

  // 리더가 아니면 리모트 팀B 위치만 수신합니다.
  if (!rs.isLeader.value) {
    return
  }

  // 1.5초 유예 후 팀B 진행 시작
  setTimeout(() => {
    if (phase.value !== 'play') return

    team2Timer = setInterval(() => {
      if (phase.value !== 'play') return

      // 기본 이동: 팀B도 자동으로 천천히 진행 (플레이어가 입력하지 않으면)
      team2Pct_.value += 0.5

      // 가속 모드: 팀A가 30% 이상 앞서면 팀B 속도 2배
      if (playerPos.value - team2Pct_.value > 30) {
        team2Pct_.value += 0.5  // 1배 속도 가속
      }

      // 서버에 팀B 위치 브로드캐스트
      rs.emitAiSync(roomId.value, team2Pct_.value)

      // 팀B가 먼저 완주하면 게임 오버 (팀A 패배)
      if (team2Pct_.value >= 100) {
        clearInterval(team2Timer)
        rs.emitFinish(roomId.value, {
          caught: true,  // 팀B가 팀A를 따라잡음
          playerPos: playerPos.value
        })
      }
    }, team2Interval.value)
  }, 1500)
}

// ─── 라인 제출 ────────────────────────────────────────
let lastVariables = {}

function submitLine() {
  if (!isMyTurn.value) return
  const input = userInput.value.trim()
  if (!input || phase.value !== 'play') return

  // 타임아웃 타이머 정지
  if (lineTimeoutInterval) clearInterval(lineTimeoutInterval)
  isTimeoutActive.value = false

  const lineData = currentSectorLines.value[currentLineIdx.value]
  if (!lineData) return

  const correct = checkAnswer(input, lineData)

  if (correct) {
    handleCorrect(input, lineData)
  } else {
    handleWrong(input)
  }
  userInput.value = ''
  nextTick(() => codeInput.value?.focus())
}

function checkAnswer(input, lineData) {
  // 1. 공백 및 대소문자 제거 후 완전 일치 확인 (한글 특성 반영)
  const clean = s => s.replace(/\s+/g, '').trim().toLowerCase()
  const answers = [lineData.answer, ...(lineData.altAnswers || [])]
  
  for (const ans of answers) {
    if (clean(input) === clean(ans)) return true
    
    // 2. 키워드 기반 유사도 (명사/논리 중심)
    // 한글은 1자보다 긴 단어를 키워드로 추출
    const keywords = ans.split(/[\s(),=:"'<>!]+/).filter(k => k.length >= 2)
    const matched = keywords.filter(k => input.includes(k))
    
    // 키워드가 60% 이상 포함되면 정답으로 간주하여 유연성 부여
    if (keywords.length > 0 && (matched.length / keywords.length) >= 0.6) return true
  }
  return false
}

function handleCorrect(input, lineData) {
  lastCorrectLine.value = input
  flashOk.value = true
  setTimeout(() => { flashOk.value = false }, 400)

  // 전진량: 전체 진행도 / 총 라인 수
  const totalLines = currentQuest.value.sectors
    .slice(0, totalSectors.value)
    .reduce((sum, s) => sum + s.lines.length, 0)
  const advance = 100 / totalLines
  playerPos.value = Math.min(playerPos.value + advance, 100)

  // 점수
  const pts = 100
  score.value += pts
  spawnFpop(`+${pts}`, '#34d399')

  // 지표 업데이트
  updateMetric('implementation', +3)

  // 변수 일관성 체크
  const varName = currentSectorData.value?.consistencyVar
  if (varName) {
    if (input.includes(varName)) {
      updateMetric('consistency', +5)
      spawnFpop('일관성 ✅', '#60a5fa')
    } else if (lastVariables[varName] && !input.includes(varName)) {
      updateMetric('consistency', -5)
      spawnFpop('일관성 위반 ⚠️', '#f59e0b')
    }
    lastVariables[varName] = true
  }
  // 함수/추상화 감지 (한글 키워드 대응)
  if (input.includes('함수') || input.includes('정의') || input.includes('선언') || input.includes('class')) {
    updateMetric('abstraction', +8)
    spawnFpop('추상화 ✨', '#a78bfa')
    tryGiveItem('abstraction')
  }
  // 예외 처리 및 논리 감지 (한글 키워드 대응)
  if (input.includes('만약') || input.includes('유효') || input.includes('예외') || input.includes('반환') || input.includes('결과')) {
    updateMetric('exception', +5)
    updateMetric('design', +3)
  }

  // 플레이어 완료 라인 수 증가
  players.value[currentPlayerIdx.value].completedLines++

  // 방해 요소 확인
  if (currentSectorData.value?.obstacleAt === currentLineIdx.value + 1) {
    showObstacle.value = currentSectorData.value.obstacleType
    setTimeout(() => { showObstacle.value = null }, 3000)
  }

  currentLineIdx.value++

  // [멀티플레이어] 진행도 발신
  rs.emitProgress(roomId.value, {
    playerPos: playerPos.value,
    playerIdx: currentPlayerIdx.value,
    lineIdx: currentLineIdx.value,
    lastCorrectLine: lastCorrectLine.value,
    score: score.value,
    metrics: metrics.value
  })

  // 섹터 완료 확인
  if (currentLineIdx.value >= currentSectorLines.value.length) {
    players.value[currentPlayerIdx.value].done = true
    sectorComplete()
  } else {
    // 다음 라인의 타이머 시작
    startLineTimeout()
  }
}

function handleWrong(input) {
  errorMsg.value = '정답과 다릅니다. 힌트를 참고해 다시 시도하세요.'
  setTimeout(() => { errorMsg.value = '' }, 2500)
  shaking.value = true
  stumbling.value = true
  flashFail.value = true
  setTimeout(() => { shaking.value = false; stumbling.value = false; flashFail.value = false }, 400)

  // 후진
  playerPos.value = Math.max(playerPos.value - 1.5, 0)
  updateMetric('implementation', -4)
  spawnFpop('오타 바나나 🍌', '#ef4444')

  // 같은 라인 재시도 (타이머는 리셋되지 않음 - 계속 진행)
}

// ─── 섹터 완료 / 바통 패스 ────────────────────────────
function sectorComplete(fromSocket = false) {
  if (team2Timer) clearInterval(team2Timer)
  if (lineTimeoutInterval) clearInterval(lineTimeoutInterval)
  isTimeoutActive.value = false
  const nextSector = currentSector.value + 1
  if (nextSector >= totalSectors.value) {
    // 모든 섹터 완료
    endGame('complete')
    return
  }
  
  // [멀티플레이어] 릴레이 시작 신호 발신
  if (!fromSocket) {
    rs.emitRelayStart(roomId.value, currentSector.value)
  }

  // 릴레이 화면으로
  highFiveStatus.value = ''
  relayTimer.value = 10
  highFiveTime = null
  phase.value = 'relay'
  relayInterval = setInterval(() => {
    relayTimer.value--
    if (relayTimer.value <= 0) continueRelay()
  }, 1000)
}

function handleHighFive() {
  const now = Date.now()
  if (!highFiveTime) {
    highFiveTime = now
    highFiveStatus.value = '✋ 한 명 완료! 상대방도 눌러주세요!'
    // [멀티플레이어] 하이파이브 첫 번째 클릭 공유
    rs.emitHighFive(roomId.value, { highFiveTime: now, status: highFiveStatus.value })
    return
  }
  const diff = Math.abs(now - highFiveTime)
  if (diff <= 300) {
    highFiveStatus.value = '🎉 하이파이브 성공! 대시 부스트!'
    score.value += 200
    playerPos.value = Math.min(playerPos.value + 8, 100)
    spawnFpop('하이파이브! +200', '#fbbf24')
    
    // [멀티플레이어] 결과 공유
    rs.emitHighFive(roomId.value, { 
      status: highFiveStatus.value, 
      score: score.value, 
      playerPos: playerPos.value,
      triggerContinue: true 
    })
    
    setTimeout(continueRelay, 1000)
  } else {
    highFiveStatus.value = `아쉬워요! ${diff}ms 차이. 그냥 계속합니다.`
    rs.emitHighFive(roomId.value, { status: highFiveStatus.value, triggerContinue: true })
    setTimeout(continueRelay, 1200)
  }
}

function continueRelay(fromSocket = false) {
  clearInterval(relayInterval)
  currentSector.value++
  currentLineIdx.value = 0
  
  // [멀티플레이어] 동기화 발신
  if (!fromSocket) {
    rs.emitProgress(roomId.value, {
      playerPos: playerPos.value,
      playerIdx: currentPlayerIdx.value,
      lineIdx: currentLineIdx.value,
      sectorIdx: currentSector.value
    })
  }

  // 다음 플레이어로 (짝수: 팀A, 홀수: 팀B)
  currentPlayerIdx.value = (currentPlayerIdx.value + 1) % teamSize.value
  currentTeam.value = currentPlayerIdx.value % 2 === 0 ? 'A' : 'B'

  phase.value = 'play'
  startTeam2Chase()
  // 섹터 시작 타이머
  startLineTimeout()
  nextTick(() => codeInput.value?.focus())
}

// ─── 게임 종료 ────────────────────────────────────────
function endGame(result) {
  if (team2Timer) clearInterval(team2Timer)
  if (relayInterval) clearInterval(relayInterval)
  if (lineTimeoutInterval) clearInterval(lineTimeoutInterval)
  isTimeoutActive.value = false

  if (result === 'complete') {
    // 보너스 계산
    if (score.value > 2000) bonuses.value.push('하이파이브 타임 보너스 +200pt')
    if (metrics.value.consistency >= 80) bonuses.value.push('변수 무결성 달성 +150pt')
    if (playerPos.value - team2Pct_.value > 30) { score.value += 200; bonuses.value.push('팀B와 격차 30% 이상 +200pt') }
  }
  
  // [멀티플레이어] 종료 신호 발신
  rs.emitFinish(roomId.value, { result, caughtAt: caughtAtPct.value })
  
  phase.value = result
}

// ─── 유틸 ─────────────────────────────────────────────
function updateMetric(key, delta) {
  metrics.value[key] = Math.max(0, Math.min(100, metrics.value[key] + delta))
}

function tryGiveItem(type) {
  if (type === 'abstraction') {
    const id = ++itemIdCounter
    activeItems.value.push({ id, icon: '🧪', name: '추상화 물약', remainSec: 10 })
    playerPos.value = Math.min(playerPos.value + 5, 100)
    const t = setInterval(() => {
      const item = activeItems.value.find(i => i.id === id)
      if (!item) { clearInterval(t); return }
      item.remainSec--
      if (item.remainSec <= 0) {
        activeItems.value = activeItems.value.filter(i => i.id !== id)
        clearInterval(t)
      }
    }, 1000)
  }
}

function spawnFpop(text, color = '#fbbf24') {
  const id = ++fpopId
  fpops.value.push({
    id, text,
    style: { left: (30 + Math.random() * 40) + '%', color }
  })
  setTimeout(() => { fpops.value = fpops.value.filter(f => f.id !== id) }, 1400)
}

// ─── 라인 타임아웃 ────────────────────────────────────
function startLineTimeout() {
  if (lineTimeoutInterval) clearInterval(lineTimeoutInterval)
  lineTimeout.value = 20
  isTimeoutActive.value = true

  lineTimeoutInterval = setInterval(() => {
    lineTimeout.value--

    if (lineTimeout.value <= 0) {
      clearInterval(lineTimeoutInterval)
      isTimeoutActive.value = false
      // 시간 초과: 자동으로 공란 제출 (패널티)
      handleTimeout()
    }
  }, 1000)
}

function handleTimeout() {
  // 시간 초과 처리
  errorMsg.value = '⏱️ 시간 초과! 다음 라인으로 넘어갑니다.'
  setTimeout(() => { errorMsg.value = '' }, 1500)

  // 화면 효과
  flashFail.value = true
  setTimeout(() => { flashFail.value = false }, 400)

  // 진행도 감소
  playerPos.value = Math.max(playerPos.value - 2, 0)

  // 라인 스킵
  currentLineIdx.value++

  // 멀티플레이어 동기화
  rs.emitProgress(roomId.value, {
    playerPos: playerPos.value,
    playerIdx: currentPlayerIdx.value,
    lineIdx: currentLineIdx.value,
    score: score.value,
    metrics: metrics.value
  })

  userInput.value = ''
  nextTick(() => codeInput.value?.focus())

  // 섹터 완료 확인
  if (currentLineIdx.value >= currentSectorLines.value.length) {
    players.value[currentPlayerIdx.value].done = true
    sectorComplete()
  } else {
    // 다음 라인 타이머 시작
    startLineTimeout()
  }
}

// 팀B의 현재 플레이어 아바타 반환
function getTeam2Avatar() {
  // 팀B의 현재 진행 중인 플레이어 인덱스 (홀수)
  let team2PlayerIdx = 1  // 기본값: 팀B의 첫 번째 플레이어

  if (currentPlayerIdx.value % 2 === 1) {
    // 현재 팀B 플레이어가 진행 중
    team2PlayerIdx = currentPlayerIdx.value
  } else {
    // 현재 팀A 플레이어가 진행 중이면, 팀B의 다음 플레이어
    team2PlayerIdx = Math.min(currentPlayerIdx.value + 1, teamSize.value - 1)
    if (team2PlayerIdx % 2 === 0) {
      team2PlayerIdx = Math.min(team2PlayerIdx + 1, teamSize.value - 1)
    }
  }

  return players.value[team2PlayerIdx]?.avatarUrl || '/image/duck_idle.png'
}

onUnmounted(() => {
  clearInterval(team2Timer)
  clearInterval(relayInterval)
  clearInterval(lineTimeoutInterval)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;600;700&family=Space+Grotesk:wght@400;600&display=swap');

/* ── 기본 ─────────────────────────────────────── */
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
.flash-ok::after { content:''; position:fixed; inset:0; background:rgba(57,255,20,.1); z-index:9000; pointer-events:none; animation:flashOut .4s forwards; }
.flash-fail::after { content:''; position:fixed; inset:0; background:rgba(255,45,117,.1); z-index:9000; pointer-events:none; animation:flashOut .4s forwards; }
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

/* ── INTRO ────────────────────────────────────── */
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
.team-btns { display:flex; justify-content:center; gap:.6rem; margin-bottom:.75rem; }
.btn-team { padding:.5rem 1.5rem; background:transparent; border:1.5px solid #334155; color:#64748b; border-radius:.5rem; cursor:pointer; font-family:'Orbitron',sans-serif; font-size:.7rem; font-weight:700; letter-spacing:1px; transition:all .2s; }
.btn-team.active { border-color:#00f0ff; color:#00f0ff; background:rgba(0,240,255,.06); }
.ace-toggle { display:flex; align-items:center; gap:.5rem; justify-content:center; font-size:.8rem; color:#64748b; cursor:pointer; }
.ace-toggle input { accent-color:#00f0ff; }

.btn-start { margin-top:.5rem; padding:.9rem 3rem; font-family:'Orbitron',sans-serif; font-size:1rem; font-weight:900; background:transparent; border:2px solid #ffe600; color:#ffe600; border-radius:.75rem; cursor:pointer; letter-spacing:3px; transition:all .2s; }
.btn-start:hover { background:rgba(255,230,0,.08); box-shadow:0 0 30px rgba(255,230,0,.3); transform:scale(1.04); }
.blink-border { animation:blinkB 1.5s infinite; }
@keyframes blinkB { 50%{border-color:rgba(255,230,0,.3)} }

/* ── MULTIPLAYER LOBBY UI ─────────────────────── */
.room-input-group { display: flex; gap: 8px; justify-content: center; margin-bottom: 12px; }
.room-input {
  background: rgba(0, 0, 0, 0.4); border: 1px solid #1e293b; color: #fff;
  padding: 8px 12px; border-radius: 6px; font-family: 'Orbitron', sans-serif;
  font-size: 0.9rem; width: 140px; text-align: center; outline: none;
}
.room-input:focus { border-color: #00f0ff; box-shadow: 0 0 10px rgba(0, 240, 255, 0.2); }
.btn-join {
  background: rgba(0, 240, 255, 0.1); border: 1px solid rgba(0, 240, 255, 0.3);
  color: #00f0ff; padding: 8px 16px; border-radius: 6px; font-family: 'Orbitron', sans-serif;
  font-size: 0.8rem; font-weight: 700; cursor: pointer; transition: all 0.2s;
}
.btn-join:hover { background: #00f0ff; color: #030712; }
.current-room-info { font-size: 0.8rem; color: #64748b; margin-top: 8px; }
.room-players { margin-top: 6px; display: flex; flex-wrap: wrap; justify-content: center; gap: 6px; }
.p-tag {
  font-size: 0.7rem; background: rgba(0, 240, 255, 0.05); border: 1px solid rgba(0, 240, 255, 0.1);
  padding: 2px 8px; border-radius: 4px; color: #38bdf8;
}
.lobby-info { font-size: 0.8rem; color: #ffe600; margin-top: 10px; animation: blinkB 2s infinite; }

/* ── HUD ──────────────────────────────────────── */
.hud {
  display:flex; align-items:center; gap:1rem;
  padding:.6rem 1.5rem; margin:.75rem 1rem 0;
  background:rgba(8,12,30,.85); border:1px solid rgba(0,240,255,.1);
  border-radius:1rem;
}
.hud-cell { display:flex; flex-direction:column; align-items:center; }
.hud-lbl { font-size:.5rem; font-weight:700; color:#475569; letter-spacing:2px; }
.hud-val { font-family:'Orbitron',sans-serif; font-size:1.1rem; font-weight:900; }
.track-cell { flex:1; }
.track-bar {
  position:relative; height:20px;
  background:#0f172a; border-radius:10px; overflow:visible;
  border:1px solid rgba(0,240,255,.1);
}
.track-fill { position:absolute; top:0; left:0; height:100%; border-radius:10px; transition:width .5s ease; }
.player-fill { background:linear-gradient(90deg,#00f0ff,#38bdf8); opacity:.3; }
.ai-fill     { background:linear-gradient(90deg,#ff2d75,#ef4444); opacity:.25; }
.track-player,.track-ai { position:absolute; top:-8px; transition:left .5s ease; transform:translateX(-50%); }
.mini-avatar, .mini-avatar.ai-mini { width: 22px; height: 22px; object-fit: contain; filter: drop-shadow(0 0 4px rgba(0,240,255,0.4)); }
.ai-mini { filter: drop-shadow(0 0 4px rgba(255,45,117,0.4)) !important; transform: scaleX(-1); }
.track-goal { position:absolute; right:4px; top:-6px; }
.mini-goal { width: 20px; height: 20px; object-fit: contain; }
.track-labels { display:flex; justify-content:space-between; font-size:.6rem; margin-top:4px; }
.tl-you { color:#38bdf8; } .tl-ai { color:#ef4444; }

/* ── GAME AREA ────────────────────────────────── */
.game-screen { display:flex; flex-direction:column; height:calc(100vh - 80px); }
.game-area { display:grid; grid-template-columns:1fr 380px; gap:1rem; padding:1rem; flex:1; min-height:0; overflow:hidden; }

/* 좌측 */
.game-left { display:flex; flex-direction:column; gap:.75rem; }
.sector-info { display:flex; align-items:center; gap:.5rem; }
.sector-badge { font-family:'Orbitron',sans-serif; font-size:.65rem; font-weight:700; padding:3px 10px; background:rgba(0,240,255,.08); border:1px solid rgba(0,240,255,.2); border-radius:4px; color:#00f0ff; }
.player-badge { font-size:.75rem; font-weight:600; color:#94a3b8; }
.ace-badge { font-size:.7rem; font-weight:700; padding:2px 8px; background:rgba(255,230,0,.1); border:1px solid rgba(255,230,0,.3); border-radius:4px; color:#ffe600; }

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
.ai-lane { background: rgba(255,45,117,0.03); }
.player-lane { background: rgba(0,240,255,0.03); }

.runner-char {
  position:absolute; bottom:8px; transition:left .5s ease;
  width: 64px; height: 64px; display: flex; align-items: flex-end;
  justify-content: center; transform: translateX(-50%);
}
.main-avatar { width: 56px; height: 56px; object-fit: contain; filter: drop-shadow(0 0 10px rgba(0,240,255,0.3)); }
.runner-char.running { animation:runBounce .4s infinite ease-in-out; }
.runner-char.stumble { animation:stumbleAnim .3s ease; }

.ai-char {
  position:absolute; bottom:8px; opacity:0; transition:left .5s ease, opacity .3s;
  width: 64px; height: 64px; display: flex; align-items: flex-end;
  justify-content: center; transform: scaleX(-1) translateX(50%);
}
.main-ai { width: 60px; height: 60px; object-fit: contain; filter: drop-shadow(0 0 12px rgba(255,45,117,0.4)); }
.ai-char.visible { opacity:1; animation: aiRunBounce .45s infinite ease-in-out; }

.finish-line {
  position: absolute; right: 20px; top: 0; bottom: 0; width: 40px;
  background: repeating-linear-gradient(45deg, #eee 0, #eee 5px, #222 5px, #222 10px);
  opacity: 0.15; display: flex; align-items: center; justify-content: center;
}
.finish-icon { font-size: 1.5rem; transform: rotate(-10deg); filter: grayscale(1); }

.speech-bubble {
  position:absolute; top:-35px; background:rgba(8,12,30,.9);
  border:1px solid rgba(0,240,255,.3); border-radius:.5rem;
  padding:.3rem .6rem; font-size:.75rem; color:#00f0ff;
  white-space:nowrap; max-width:150px; overflow:hidden;
  text-overflow:ellipsis; transform: translateX(-50%);
}

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
@keyframes aiRunBounce {
  0%,100%{transform:translateY(0) rotate(-5deg) scaleX(-1)} 
  50%{transform:translateY(-10px) rotate(5deg) scaleX(-1.05)} 
}
@keyframes stumbleAnim { 0%,100%{transform:rotate(0)} 50%{transform:rotate(-20deg)} }

.obstacle { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); font-size:.9rem; font-weight:700; padding:.4rem .8rem; border-radius:.5rem; animation:obstacleIn .3s ease; }
.logic-swamp { background:rgba(0,100,200,.3); border:1px solid #3b82f6; color:#93c5fd; }
.spaghetti   { background:rgba(200,50,0,.3); border:1px solid #f97316; color:#fed7aa; }
@keyframes obstacleIn { from{transform:translate(-50%,-50%) scale(0)} to{transform:translate(-50%,-50%) scale(1)} }

/* 팀 상태 */
.team-status { display:flex; gap:.5rem; }
.player-pill { display:flex; align-items:center; gap:.35rem; padding:.35rem .75rem; background:rgba(8,12,30,.5); border:1.5px solid #1e293b; border-radius:.5rem; font-size:.8rem; transition:all .3s; }
.player-pill.active { border-color:#00f0ff; background:rgba(0,240,255,.06); }
.player-pill.done { border-color:#39ff14; opacity:.7; }
.pp-avatar { width: 18px; height: 18px; border-radius: 4px; object-fit: contain; }
.pp-name { font-weight:700; font-size: 0.75rem; }
.pp-lines { color:#475569; font-size:.65rem; }

/* 우측 */
.game-right { display:flex; flex-direction:column; gap:.75rem; overflow-y:auto; }

/* 지표 패널 */
.metrics-panel { background:rgba(8,12,30,.6); border:1px solid rgba(0,240,255,.06); border-radius:.75rem; padding:.75rem 1rem; }
.metrics-title { font-size:.6rem; font-weight:700; color:#475569; letter-spacing:2px; margin-bottom:.6rem; }
.metric-row { display:flex; align-items:center; gap:.5rem; margin-bottom:.3rem; }
.m-label { font-size:.7rem; color:#94a3b8; width:55px; flex-shrink:0; }
.m-bar-track { flex:1; height:4px; background:#0f172a; border-radius:2px; overflow:hidden; }
.m-bar-fill { height:100%; border-radius:2px; transition:width .6s ease; }
.m-val { font-family:'Orbitron',sans-serif; font-size:.6rem; color:#64748b; width:28px; text-align:right; }

/* [개선: 2026-02-24] 미션 보드 디자인 - 문제 식별 강화 */
.mission-board {
  background: rgba(8, 12, 30, 0.9);
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 12px;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 12px;
  box-shadow: 0 0 20px rgba(56, 189, 248, 0.1);
  animation: fadeInDown 0.5s ease-out;
}

.mb-ico { font-size: 1.5rem; filter: drop-shadow(0 0 8px #38bdf8); }
.mb-content { flex: 1; }
.mb-title {
  margin: 0; font-size: 0.95rem; font-weight: 800; color: #38bdf8;
  letter-spacing: 1px; font-family: 'Orbitron', sans-serif;
}
.mb-desc {
  margin: 2px 0 0; font-size: 0.8rem; color: #94a3b8; line-height: 1.4;
}
.mb-stat {
  font-family: 'Orbitron', sans-serif; font-size: 0.65rem; color: #475569;
  background: rgba(255, 255, 255, 0.05); padding: 5px 12px; border-radius: 20px;
}
.mb-stat strong { color: #ffe600; font-size: 0.8rem; }

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* [개선: 2026-02-24] IDE 스타일 에디터 디자인 */
.editor-panel {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 420px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.6);
  animation: slideUp 0.5s ease-out;
}

.editor-header {
  background: #161b22;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  border-bottom: 1px solid #30363d;
}

.editor-tabs {
  display: flex;
  gap: 2px;
  height: 100%;
}

.tab {
  padding: 0 15px;
  display: flex;
  align-items: center;
  font-size: 0.7rem;
  color: #8b949e;
  background: transparent;
  border-right: 1px solid #30363d;
  cursor: default;
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 1px;
}

.tab.active {
  background: #0d1117;
  color: #c9d1d9;
  border-bottom: 2px solid #f78166;
}

.editor-meta {
  font-size: 0.6rem;
  color: #38bdf8;
  font-weight: 700;
  letter-spacing: 1px;
  font-family: 'Orbitron', sans-serif;
}

.editor-body {
  flex: 1;
  display: flex;
  overflow-y: auto;
  background: #0d1117;
  font-family: 'Fira Code', 'Cascadia Code', Consolas, monospace;
}

/* Custom Scrollbar */
.scrollbar::-webkit-scrollbar { width: 8px; }
.scrollbar::-webkit-scrollbar-track { background: #0d1117; }
.scrollbar::-webkit-scrollbar-thumb { background: #30363d; border-radius: 4px; }
.scrollbar::-webkit-scrollbar-thumb:hover { background: #484f58; }

.editor-gutter {
  width: 45px;
  background: #0d1117;
  border-right: 1px solid #30363d;
  padding: 15px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  user-select: none;
  flex-shrink: 0;
}

.line-num {
  font-size: 0.75rem;
  color: #484f58;
  height: 24px;
  line-height: 24px;
}

.editor-content {
  flex: 1;
  padding: 15px 0;
  display: flex;
  flex-direction: column;
}

.code-line {
  height: 24px;
  line-height: 24px;
  padding: 0 15px;
  font-size: 0.85rem;
  white-space: pre;
}

.prev-line {
  color: #7ee787;
  background: rgba(126, 231, 135, 0.05);
}

.active-line {
  background: rgba(56, 189, 248, 0.08);
  height: auto;
  min-height: 65px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 12px 15px;
  border-top: 1px solid rgba(56, 189, 248, 0.2);
  border-bottom: 1px solid rgba(56, 189, 248, 0.2);
  position: relative;
}

.hint-bubble {
  font-size: 0.75rem;
  color: #ffda6a;
  margin-bottom: 8px;
  background: rgba(255, 230, 0, 0.1);
  padding: 4px 12px;
  border-radius: 4px;
  align-self: flex-start;
  border: 1px solid rgba(255, 230, 0, 0.2);
  font-family: 'Pretendard', sans-serif;
}

.input-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.input-cursor {
  color: #f78166;
  font-weight: 700;
  font-size: 0.9rem;
}

.editor-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #c9d1d9;
  font-family: inherit;
  font-size: 0.85rem;
  outline: none;
  width: 100%;
}

.next-line {
  color: #30363d;
}

.editor-footer {
  background: #161b22;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  border-top: 1px solid #30363d;
  font-size: 0.65rem;
  color: #8b949e;
  font-family: 'Orbitron', sans-serif;
}

.btn-ide-submit {
  background: #238636;
  color: #fff;
  border: none;
  padding: 4px 16px;
  border-radius: 4px;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.65rem;
  font-weight: 900;
  cursor: pointer;
  transition: all 0.2s;
  letter-spacing: 1px;
}

.btn-ide-submit:hover:not(:disabled) {
  background: #2ea043;
  transform: translateY(-1px);
}

.btn-ide-submit:disabled {
  background: #21262d;
  color: #484f58;
  cursor: not-allowed;
}

.err-msg {
  color: #f85149;
  margin-right: 15px;
  font-family: 'Pretendard', sans-serif;
  font-weight: 700;
}

/* 라인 타임아웃 */
.timeout-bar-container {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}
.timeout-bar-track {
  flex: 1;
  height: 6px;
  background: #0a0f1e;
  border-radius: 3px;
  overflow: hidden;
  border: 0.5px solid #1e293b;
}
.timeout-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #00f0ff, #38bdf8);
  border-radius: 3px;
  transition: width 1s linear;
}
.timeout-bar-fill.danger {
  background: linear-gradient(90deg, #ff2d75, #ef4444);
}
.timeout-text {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.65rem;
  color: #94a3b8;
  min-width: 25px;
  text-align: right;
}
.timeout-text.danger {
  color: #ff2d75;
  font-weight: 700;
  animation: blinkA 0.5s infinite;
}
@keyframes blinkA { 50%{opacity:.3} }
@keyframes fadeIn { from{opacity:0;transform:translateY(-4px)} to{opacity:1;transform:translateY(0)} }

/* 아이템 */
.items-panel { display:flex; flex-wrap:wrap; gap:.4rem; }
.item-pill { display:flex; align-items:center; gap:.3rem; padding:.25rem .6rem; background:rgba(167,139,250,.1); border:1px solid rgba(167,139,250,.25); border-radius:.4rem; font-size:.75rem; }
.item-timer { font-family:'Orbitron',sans-serif; font-size:.55rem; color:#64748b; }

/* ── RELAY ────────────────────────────────────── */
.relay-screen { display:flex; align-items:center; justify-content:center; min-height:100vh; }
.relay-box {
  text-align:center; max-width:480px; width:90%;
  background:rgba(8,12,30,.95); border:2px solid #ffe600;
  border-radius:1.5rem; padding:3rem 2.5rem;
  box-shadow:0 0 60px rgba(255,230,0,.15);
}
.relay-icon { font-size:3rem; margin-bottom:.75rem; }
.relay-title { font-family:'Orbitron',sans-serif; font-size:2rem; font-weight:900; color:#ffe600; margin-bottom:.5rem; }
.relay-desc,.relay-next { color:#94a3b8; font-size:.9rem; margin:.2rem 0; }
.relay-next { color:#e0f2fe; font-weight:700; }
.relay-timing { height:6px; background:#0f172a; border-radius:3px; overflow:hidden; margin:1rem 0; }
.timing-bar { height:100%; background:linear-gradient(90deg,#ffe600,#f59e0b); border-radius:3px; transition:width 1s linear; }
.relay-hint { font-size:.8rem; color:#64748b; margin-bottom:1rem; }
kbd { background:rgba(255,255,255,.08); border:1px solid #334155; border-radius:3px; padding:1px 6px; font-family:'Orbitron',sans-serif; font-size:.7rem; }
.btn-highfive { width:100%; padding:1rem; font-family:'Orbitron',sans-serif; font-size:1rem; font-weight:900; background:rgba(255,230,0,.06); border:2px solid #ffe600; color:#ffe600; border-radius:.75rem; cursor:pointer; letter-spacing:2px; transition:all .2s; margin-bottom:.75rem; }
.btn-highfive:hover { background:rgba(255,230,0,.12); box-shadow:0 0 30px rgba(255,230,0,.2); transform:scale(1.02); }
.highfive-status { font-size:.85rem; color:#e0f2fe; margin-bottom:.75rem; min-height:1.2em; }
.btn-continue { background:transparent; border:1px solid #1e293b; color:#475569; padding:.5rem 1.5rem; border-radius:.5rem; cursor:pointer; font-size:.75rem; transition:all .2s; }
.btn-continue:hover { border-color:#334155; color:#64748b; }

/* ── BATON ──────────────────────────────────── */
.baton {
  position: absolute; bottom: 10px; right: 10px;
  width: 5px; height: 22px; background: #ffe600;
  border-radius: 3px; transform: rotate(15deg);
  box-shadow: 0 0 12px rgba(255,230,0,0.9);
  z-index: 2;
}
.runner-char.running .baton {
  animation: batonShake 0.4s infinite ease-in-out;
}
@keyframes batonShake {
  0%, 100% { transform: rotate(15deg) translateY(0); }
  50% { transform: rotate(25deg) translateY(-2px); }
}
.relay-pass-anim {
  display: flex; align-items: center; justify-content: center; gap: 2rem; margin: 1.5rem 0;
}
.pass-avatar { width: 50px; height: 50px; object-fit: contain; }
.pass-baton { font-size: 1.5rem; animation: passMove 1s infinite alternate; }
@keyframes passMove { 
  from { transform: translateX(-20px) rotate(0); }
  to { transform: translateX(20px) rotate(45deg); }
}

/* ── OVERLAY / GAMEOVER / COMPLETE ────────────── */
.overlay { position:fixed; inset:0; background:rgba(0,0,0,.85); backdrop-filter:blur(6px); display:flex; align-items:center; justify-content:center; z-index:200; }

.gameover-box,.complete-box {
  text-align:center; max-width:480px; width:90%;
  background:rgba(8,12,30,.98); border-radius:1.5rem; padding:3rem 2.5rem;
}
.gameover-box { border:2px solid #ff2d75; box-shadow:0 0 60px rgba(255,45,117,.15); }
.complete-box  { border:2px solid #39ff14; box-shadow:0 0 60px rgba(57,255,20,.15); }

.go-icon { font-size:3.5rem; margin-bottom:.5rem; }
.go-title { font-size:2.5rem; font-weight:900; color:#ff2d75; margin-bottom:.5rem; }
.go-desc { color:#94a3b8; font-size:.9rem; margin-bottom:.5rem; }
.go-caught-at { font-family:'Orbitron',sans-serif; color:#ff2d75; font-size:.8rem; margin-bottom:1.5rem; }

.cp-icon { font-size:3.5rem; margin-bottom:.5rem; }
.cp-title { font-family:'Orbitron',sans-serif; font-size:1.6rem; font-weight:900; color:#39ff14; margin-bottom:.75rem; }
.cp-grade { font-family:'Orbitron',sans-serif; font-size:5rem; font-weight:900; margin-bottom:.3rem; }
.g-S { color:#ffe600; text-shadow:0 0 30px rgba(255,230,0,.5); }
.g-A { color:#00f0ff; text-shadow:0 0 20px rgba(0,240,255,.3); }
.g-B { color:#39ff14; }
.g-C { color:#f59e0b; }
.g-D { color:#64748b; }
.cp-score { font-family:'Orbitron',sans-serif; font-size:2rem; font-weight:900; margin-bottom:1rem; }
.cp-score small { font-size:1rem; color:#475569; }

.cp-metrics { margin-bottom:1rem; }
.cpm-row { display:flex; align-items:center; gap:.5rem; margin-bottom:.35rem; }
.cpm-label { font-size:.75rem; color:#94a3b8; width:55px; text-align:left; }
.cpm-bar { flex:1; height:6px; background:#0f172a; border-radius:3px; overflow:hidden; }
.cpm-fill { height:100%; border-radius:3px; }
.cpm-val { font-family:'Orbitron',sans-serif; font-size:.65rem; color:#64748b; width:28px; text-align:right; }

.cp-feedback { font-size:.85rem; color:#94a3b8; margin-bottom:.75rem; line-height:1.5; }
.cp-bonuses { margin-bottom:1rem; }
.bonus-item { font-size:.78rem; color:#fbbf24; margin:.2rem 0; }

.go-btns { display:flex; gap:.75rem; margin-top:1rem; }
.btn-retry,.btn-exit { flex:1; padding:.75rem; font-family:'Orbitron',sans-serif; font-size:.8rem; font-weight:700; border-radius:.75rem; cursor:pointer; letter-spacing:1px; transition:all .2s; }
.btn-retry { background:transparent; border:2px solid #00f0ff; color:#00f0ff; }
.btn-retry:hover { background:rgba(0,240,255,.08); }
.btn-exit { background:transparent; border:1px solid #334155; color:#64748b; }
.btn-exit:hover { border-color:#475569; color:#94a3b8; }

/* ── FLOAT POP ────────────────────────────────── */
.fpop-layer { position:fixed; inset:0; pointer-events:none; z-index:500; }
.fpop-item { position:absolute; top:35%; font-family:'Orbitron',sans-serif; font-size:1rem; font-weight:700; text-shadow:0 0 10px currentColor; }
.fpop-enter-active { animation:fUp 1.4s ease-out forwards; }
@keyframes fUp { 0%{opacity:1;transform:translateY(0) scale(1.1)} 100%{opacity:0;transform:translateY(-80px) scale(.85)} }

/* ── TRANSITIONS ──────────────────────────────── */
.zoom-enter-active { animation:zIn .35s ease; }
@keyframes zIn { from{transform:scale(.7);opacity:0} to{transform:scale(1);opacity:1} }

/* ── Responsive ───────────────────────────────── */
@media (max-width: 900px) {
  .game-area { grid-template-columns: 1fr; }
  .game-right { display:none; }
}
</style>
