<template>
  <div class="growth-report-container">
    <header class="report-header">
      <div class="header-left">
        <span class="report-tag">MISSION ACCOMPLISHED</span>
        <h1>INTEL GROWTH REPORT</h1>
      </div>
      <div class="total-score-card">
        <div class="grade-badge" :class="evaluationData?.grade">{{ evaluationData?.grade || '-' }}</div>
        <div class="score-info">
          <span class="label">TOTAL SCORE</span>
          <span class="value">{{ evaluationData?.total_score || 0 }}</span>
        </div>
      </div>
    </header>

    <main class="report-content" :class="{ 'has-team': teamScoreList.length > 1 }">
      <!-- Left: Visualization -->
      <section class="glass-panel visual-panel">
        <div class="panel-header">
          <span class="icon">📊</span>
          <h2>CAPABILITY ANALYSIS</h2>
        </div>
        <div class="chart-container">
          <canvas ref="radarChart"></canvas>
        </div>
        <div class="stat-grid">
          <div v-for="(score, key) in evaluationData?.scores" :key="key" class="stat-pill">
            <span class="stat-label">{{ key.toUpperCase() }}</span>
            <span class="stat-value">{{ score }}</span>
          </div>
        </div>
      </section>

      <!-- Center: 팀 점수 비교 (playerScores가 있을 때만) -->
      <section class="glass-panel team-score-panel" v-if="teamScoreList.length > 1">
        <div class="panel-header">
          <span class="icon">🏆</span>
          <h2>TEAM SCORE COMPARISON</h2>
        </div>
        <div class="team-score-list">
          <div
            v-for="(player, idx) in teamScoreList"
            :key="player.name"
            class="team-score-row"
            :class="{ 'top-player': idx === 0 }"
          >
            <span class="rank-badge">{{ idx === 0 ? '👑' : '#' + (idx + 1) }}</span>
            <div class="player-info">
              <span class="player-name">{{ player.name }}</span>
              <span class="player-role">{{ player.role }}</span>
            </div>
            <div class="score-bar-wrap">
              <div class="score-bar-bg">
                <div class="score-bar-val" :style="{ width: player.score + '%' }" :class="'rank-' + (idx + 1)"></div>
              </div>
              <span class="score-num">{{ player.score }}pt</span>
            </div>
          </div>
        </div>
        <div class="team-avg">
          <span>팀 평균</span>
          <span class="avg-val">{{ teamAvg }}pt</span>
          <span class="avg-grade" :class="teamGrade">{{ teamGrade }}</span>
        </div>
      </section>

      <!-- Right: AI Feedback -->
      <section class="glass-panel feedback-panel">
        <div class="panel-header">
          <span class="icon">🧠</span>
          <h2>EXPERT AI FEEDBACK</h2>
        </div>
        
        <div class="feedback-section good">
          <h3>The Good</h3>
          <ul>
            <li v-for="(item, idx) in evaluationData?.feedback?.the_good" :key="idx">
              {{ item }}
            </li>
          </ul>
        </div>

        <div class="feedback-section bad">
          <h3>The Bad</h3>
          <ul>
            <li v-for="(item, idx) in evaluationData?.feedback?.the_bad" :key="idx">
              {{ item }}
            </li>
          </ul>
        </div>

        <div class="feedback-section action">
          <h3>Action Items</h3>
          <div class="action-grid">
            <div v-for="(item, idx) in evaluationData?.feedback?.action_items" :key="idx" class="action-card">
              <span class="action-num">0{{ idx + 1 }}</span>
              <p>{{ item }}</p>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- [추가 2026-02-27] 인바스켓 위기대응 타임라인 섹션 - 데모 데이터 포함하므로 항상 표시 -->
    <section class="incident-timeline-section">
      <div class="itl-header">
        <span class="itl-icon">🚨</span>
        <h2>INCIDENT RESPONSE TIMELINE</h2>
        <span class="itl-badge">IN-BASKET SIMULATION</span>
      </div>
      <div class="itl-desc">실무 발생 시나리오에 따른 위기 대응 경과기니다.</div>
      <div class="itl-list">
        <div v-for="(incident, idx) in incidentTimeline" :key="idx" class="itl-item">
          <div class="itl-time-col">
            <div class="itl-time">T+{{ incident.elapsed }}m</div>
            <div class="itl-connector" v-if="idx < incidentTimeline.length - 1"></div>
          </div>
          <div class="itl-card" :class="'severity-' + incident.severity">
            <div class="itl-card-header">
              <span class="itl-event-icon">{{ incident.icon }}</span>
              <span class="itl-event-name">{{ incident.event }}</span>
              <span class="itl-severity-badge">{{ incident.severity.toUpperCase() }}</span>
            </div>
            <div class="itl-card-body">
              <div class="itl-action">
                <span class="itl-label">RESPONSE</span>
                <span class="itl-text">{{ incident.action }}</span>
              </div>
              <div class="itl-result" :class="incident.resolved ? 'resolved' : 'pending'">
                {{ incident.resolved ? '✅ RESOLVED' : '⚠️ IN PROGRESS' }}
                <span v-if="incident.scoreImpact" class="itl-score">
                  {{ incident.scoreImpact > 0 ? '+' : '' }}{{ incident.scoreImpact }}pt
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- [추가 2026-02-27] 포트폴리오 익스포트 섹션 -->
    <section class="portfolio-export-section">
      <div class="pf-header">
        <span class="pf-icon">🎓</span>
        <div>
          <h2>PORTFOLIO EXPORT</h2>
          <p class="pf-desc">이 게임에서 경험한 실무 시나리오 대응 내역을 포트폴리오 자료로 가져가세요</p>
        </div>
      </div>

      <!-- 포트폴리오 카드 미리보기 -->
      <div class="pf-card-preview" ref="portfolioCard">
        <div class="pfc-top">
          <div class="pfc-badge">🏗️ SYSTEM ARCHITECTURE</div>
          <div class="pfc-grade-badge" :class="evaluationData?.grade || 'A'">{{ evaluationData?.grade || 'A' }}</div>
        </div>
        <div class="pfc-title">{{ portfolioTitle }}</div>
        <div class="pfc-scenario">{{ portfolioScenario }}</div>
        <div class="pfc-scores">
          <div class="pfc-score-item" v-for="(val, key) in portfolioScores" :key="key">
            <div class="pfc-score-bar-wrap">
              <div class="pfc-score-bar" :style="{ width: val + '%', background: pfc_barColor(key) }"></div>
            </div>
            <div class="pfc-score-label">{{ key }}</div>
            <div class="pfc-score-val">{{ val }}</div>
          </div>
        </div>
        <div class="pfc-highlights">
          <div class="pfc-hl-item" v-for="(hl, idx) in portfolioHighlights" :key="idx">
            <span class="pfc-hl-icon">✓</span>
            <span>{{ hl }}</span>
          </div>
        </div>
        <div class="pfc-footer">
          <span class="pfc-source">Wars AI Simulation</span>
          <span class="pfc-date">{{ todayStr }}</span>
        </div>
      </div>

      <!-- 액션 버튼들 -->
      <div class="pf-actions">
        <button class="pf-btn pf-btn-img" @click="downloadPortfolioImage">
          <span>🖼️</span> 이미지 저장
        </button>
        <button class="pf-btn pf-btn-clip" @click="copyPortfolioText">
          <span>📋</span> 클립보드 복사
          <small>노션 / LinkedIn 바로 붙여넣기</small>
        </button>
        <div class="pf-copy-toast" v-if="copyToastVisible">✅ 클립보드에 복사됐어요!</div>
      </div>
    </section>

    <footer class="report-footer">
      <div class="final-design-preview">
        <span>FINAL ARCHITECTURE PREVIEW</span>
        <div class="mini-mermaid" ref="mermaidTarget"></div>
      </div>
      <div class="action-group">
        <button class="btn-outline" @click="downloadPdf">DOWNLOAD PDF</button>
        <button class="btn-outline" @click="replayMission">REPLAY</button>
        <button class="btn-primary" @click="goHome">EXIT TO LOBBY</button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { Chart, registerables } from 'chart.js';
import mermaid from 'mermaid';
import { useGameStore } from '@/stores/game';

Chart.register(...registerables);

// [수정일: 2026-03-03] Wars Step 3: 성장 보고서 UI 구현 (CoduckWars -> Wars)
const router = useRouter();
const gameStore = useGameStore();
// [수정일: 2026-02-23] 점수 시스템 연동: liveScores 기반 최종 점수 산정
const rawEvaluation = gameStore.lastEvaluation;
let evaluationData = ref(rawEvaluation);

if (rawEvaluation) {
    // liveScores가 있으면 가중평균 점수로 total_score 재산정
    if (rawEvaluation.scores && !rawEvaluation.total_score) {
        const computed = gameStore.calculateGameScore(rawEvaluation.scores);
        evaluationData.value = { ...rawEvaluation, total_score: computed };
    }
}
const radarChart = ref(null);
const mermaidTarget = ref(null);

// [수정일: 2026-02-27] PressureInterviewRoom 관련 주석 제거 -> [P1] 팀 점수 비교: playerScores 데이터 활용
const rawPlayerScores = gameStore.lastPlayerScores || {};

const teamScoreList = computed(() => {
  const entries = Object.entries(rawPlayerScores)
    .map(([name, info]) => ({
      name,
      role: (info.role || 'ARCHITECT').toUpperCase(),
      score: typeof info === 'number' ? info : (info.score || 0)
    }))
    .sort((a, b) => b.score - a.score);
  return entries;
});

const teamAvg = computed(() => {
  if (!teamScoreList.value.length) return 0;
  const sum = teamScoreList.value.reduce((acc, p) => acc + p.score, 0);
  return Math.round(sum / teamScoreList.value.length);
});

const teamGrade = computed(() => {
  const avg = teamAvg.value;
  if (avg >= 90) return 'S';
  if (avg >= 75) return 'A';
  if (avg >= 60) return 'B';
  return 'C';
});

// [추가 2026-02-27] 인바스켓 위기대응 타임라인
// gameStore.chaosEvents에 저장된 ChaosAgent 발화 이벤트를 타임라인 형태로 변환
const incidentTimeline = computed(() => {
  const events = gameStore.chaosEvents || []
  if (!events.length) {
    // 데모데이터: 실제 게임 데이터가 없으면 포트폴리오용 시나리오 샘플 표시
    return [
      {
        elapsed: 2,
        icon: '💀',
        event: 'Server Node Failure',
        severity: 'critical',
        action: 'Load Balancer 헬스체크를 통해 장애 노드 감지, Auto Scaling으로 신규 인스턴스 2개 기동. DB Replica로 Failover 실행.',
        resolved: true,
        scoreImpact: 120
      },
      {
        elapsed: 5,
        icon: '🔥',
        event: 'Traffic Surge (10x)',
        severity: 'high',
        action: 'CDN 캐시 트래픽 분산 + Rate Limit 적용. Redis 캐시로 의존 DB Query 70% 감소. 담당 엔지니어 비상 대렀 실행.',
        resolved: true,
        scoreImpact: 80
      },
      {
        elapsed: 7,
        icon: '🔒',
        event: 'Security Breach Detected',
        severity: 'critical',
        action: 'WAF에서 SQL Injection 패턴 감지. 해당 IP 블랙리스트에 추가하고 Zero Trust 정책 적용. 보안팀 에스커레이션.',
        resolved: true,
        scoreImpact: 150
      },
      {
        elapsed: 12,
        icon: '📊',
        event: 'DB Deadlock',
        severity: 'medium',
        action: 'Write→Read DB 분리로 쿼리 조율. 또한 Index 재구성으로 P99 Latency 340ms에서 45ms로 개선.',
        resolved: true,
        scoreImpact: 60
      }
    ]
  }
  // 실제 게임 데이터가 있는 경우
  return events.map((ev, idx) => ({
    elapsed: (idx + 1) * 2 + Math.floor(Math.random() * 2),
    icon: ev.icon || '🚨',
    event: ev.title || ev.type || 'Incident ' + (idx + 1),
    severity: ev.severity || (idx === 0 ? 'critical' : 'high'),
    action: ev.response || '아키텍처 설계를 바탕으로 신속한 대응 실행',
    resolved: ev.resolved !== false,
    scoreImpact: ev.scoreImpact || Math.floor(Math.random() * 100 + 50)
  }))
})

onMounted(async () => {
  if (!evaluationData.value) {
    // 데이터가 없으면 홈으로 리다이렉트 (실제 운영 시)
    // router.push('/practice/wars');
    // return;
  }

  // 차트 생성
  initChart();
  
  // 최종 설계도 렌더링
  if (gameStore.lastFinalDesign) {
    mermaid.initialize({ startOnLoad: false, theme: 'dark' });
    const { svg } = await mermaid.render('final-mermaid-svg', gameStore.lastFinalDesign);
    mermaidTarget.value.innerHTML = svg;
  }
});

const initChart = () => {
  if (!radarChart.value || !evaluationData.value) return;

  const scores = evaluationData.value.scores;
  const data = {
    labels: ['LOGIC', 'DESIGN', 'RESILIENCE', 'STACK', 'COST'],
    datasets: [{
      label: 'Capability',
      data: [scores.logic, scores.design, scores.resilience, scores.stack, scores.cost],
      fill: true,
      backgroundColor: 'rgba(129, 140, 248, 0.2)',
      borderColor: '#818cf8',
      pointBackgroundColor: '#818cf8',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: '#818cf8'
    }]
  };

  new Chart(radarChart.value, {
    type: 'radar',
    data: data,
    options: {
      elements: {
        line: { borderWidth: 3 }
      },
      scales: {
        r: {
          angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
          grid: { color: 'rgba(255, 255, 255, 0.1)' },
          pointLabels: { color: '#94a3b8', font: { size: 12, weight: 'bold' } },
          ticks: { display: false },
          suggestedMin: 0,
          suggestedMax: 100
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
};

const goHome = () => router.push('/');
const replayMission = () => router.push('/practice/wars');
const downloadPdf = () => alert('PDF 생성 기능은 준비 중입니다.');

// ========== [추가 2026-02-27] 포트폴리오 익스포트 ==========
const portfolioCard = ref(null)
const copyToastVisible = ref(false)

// 오늘 날짜
const todayStr = new Date().toISOString().slice(0, 10)

// 미션에서 포트폴리오 제목 생성
const portfolioTitle = computed(() => {
  const mission = gameStore.activeWarsMission
  if (mission?.mission_title) return mission.mission_title
  return '시스템 아키텍처 대응 시뮬레이션'
})

// 시나리오 설명 생성
const portfolioScenario = computed(() => {
  const mission = gameStore.activeWarsMission
  const title = (mission?.mission_title || '').toLowerCase()
  if (title.includes('트래픽') || title.includes('traffic')) return '트래픽 급증 시나리오: 초당 10만원 처리 요청에서 가용성및 확장성 설계'
  if (title.includes('라이더') || title.includes('ride')) return '라이드헤일링 배차 시스템: 실시간 위치 추적과 매칭알고리즘 설계'
  if (title.includes('메시지') || title.includes('chat')) return '대규모 메시지 시스템: WebSocket 기반 실시간 채팅 아키텍처 설계'
  if (title.includes('유튜브') || title.includes('video')) return 'VOD 스트리밍 시스템: CDN + 적응형 비트레이트 스트리밍 설계'
  return '실무 위기 시나리오에서 AI ChaosAgent의 장애 이벤트를 대응하며 아키텍처를 설계한 실습'
})

// 포트폴리오 점수 맵
 const portfolioScores = computed(() => {
  const s = evaluationData.value?.scores
  if (!s) return { AVAIL: 82, SCALE: 75, SEC: 88, COST: 70 }
  return {
    'AVAIL': s.availability || s.avail || 0,
    'SCALE': s.scalability || s.scale || 0,
    'SEC':   s.security || s.sec || 0,
    'COST':  s.cost_efficiency || s.cost || 0
  }
})

// 포트폴리오 하이라이트 (내가 잘한 것)
const portfolioHighlights = computed(() => {
  const goods = evaluationData.value?.feedback?.the_good || []
  if (goods.length) return goods.slice(0, 3)
  // 데모 폴백
  return [
    'ChaosAgent 장애 이벤트에 대한 실시간 아키텍처 대응',
    'Load Balancer + Auto Scaling 무중단 확장 설계',
    'Redis 캐시 전략으로 DB 부하 70% 감소'
  ]
})

// 점수변 색상
const pfc_barColor = (key) => {
  const map = { 'AVAIL': '#00f0ff', 'SCALE': '#38bdf8', 'SEC': '#a855f7', 'COST': '#22c55e' }
  return map[key] || '#64748b'
}

// 이미지 저장: Canvas API로 카드를 PNG로 렌더링
const downloadPortfolioImage = async () => {
  const card = portfolioCard.value
  if (!card) return

  const canvas = document.createElement('canvas')
  const scale = 2  // Retina
  const rect = card.getBoundingClientRect()
  canvas.width = rect.width * scale
  canvas.height = rect.height * scale
  const ctx = canvas.getContext('2d')
  ctx.scale(scale, scale)

  // 데이터 수집
  const title = portfolioTitle.value
  const scenario = portfolioScenario.value
  const scores = portfolioScores.value
  const highlights = portfolioHighlights.value
  const grade = evaluationData.value?.grade || 'A'
  const total = evaluationData.value?.total_score || 0

  const W = rect.width
  const H = rect.height

  // 배경
  const bg = ctx.createLinearGradient(0, 0, W, H)
  bg.addColorStop(0, '#030712')
  bg.addColorStop(1, '#0f172a')
  ctx.fillStyle = bg
  ctx.roundRect(0, 0, W, H, 16)
  ctx.fill()

  // 테두리
  ctx.strokeStyle = 'rgba(0,240,255,0.3)'
  ctx.lineWidth = 1
  ctx.roundRect(0, 0, W, H, 16)
  ctx.stroke()

  // 상단 배지
  ctx.fillStyle = 'rgba(0,240,255,0.08)'
  ctx.roundRect(16, 16, 200, 28, 6)
  ctx.fill()
  ctx.fillStyle = '#00f0ff'
  ctx.font = 'bold 11px monospace'
  ctx.fillText('🏗️ SYSTEM ARCHITECTURE', 26, 34)

  // 등급 배지
  const gradeColors = { S: '#fbbf24', A: '#00f0ff', B: '#38bdf8', C: '#94a3b8' }
  ctx.fillStyle = gradeColors[grade] || '#94a3b8'
  ctx.font = 'bold 20px monospace'
  ctx.fillText(grade, W - 40, 35)

  // 제목
  ctx.fillStyle = '#f1f5f9'
  ctx.font = 'bold 18px sans-serif'
  ctx.fillText(title.length > 36 ? title.slice(0, 36) + '...' : title, 16, 68)

  // 시나리오
  ctx.fillStyle = '#64748b'
  ctx.font = '12px sans-serif'
  const lines = wrapText(ctx, scenario, W - 32, 12)
  lines.forEach((line, i) => ctx.fillText(line, 16, 90 + i * 16))
  const yAfterScenario = 90 + lines.length * 16 + 12

  // 점수 바 그리기
  let y = yAfterScenario
  Object.entries(scores).forEach(([k, v]) => {
    ctx.fillStyle = '#334155'
    ctx.fillText(k, 16, y + 4)
    ctx.fillStyle = '#1e293b'
    ctx.roundRect(60, y - 8, W - 80, 12, 4)
    ctx.fill()
    ctx.fillStyle = pfc_barColor(k)
    ctx.roundRect(60, y - 8, Math.max(4, (W - 80) * v / 100), 12, 4)
    ctx.fill()
    ctx.fillStyle = '#94a3b8'
    ctx.fillText(String(v), W - 18, y + 4)
    y += 20
  })
  y += 8

  // 하이라이트
  highlights.forEach((hl, i) => {
    ctx.fillStyle = '#00f0ff'
    ctx.font = 'bold 13px sans-serif'
    ctx.fillText('✓', 16, y + i * 20)
    ctx.fillStyle = '#e0f2fe'
    ctx.font = '12px sans-serif'
    const hlLines = wrapText(ctx, hl, W - 44, 12)
    ctx.fillText(hlLines[0], 32, y + i * 20)
  })
  y += highlights.length * 20 + 12

  // 푸터
  ctx.fillStyle = '#334155'
  ctx.fillRect(0, H - 36, W, 1)
  ctx.fillStyle = '#64748b'
  ctx.font = '10px monospace'
  ctx.fillText('Wars AI Simulation', 16, H - 16)
  ctx.fillText(todayStr, W - 80, H - 16)

  // PNG 다운로드
  const link = document.createElement('a')
  link.download = `portfolio_${todayStr}.png`
  link.href = canvas.toDataURL('image/png')
  link.click()
}

// 텍스트 래핑 헬퍼
function wrapText(ctx, text, maxWidth, fontSize) {
  const words = text.split(' ')
  const lines = []
  let line = ''
  for (const word of words) {
    const test = line + word + ' '
    if (ctx.measureText(test).width > maxWidth && line) {
      lines.push(line.trim())
      line = word + ' '
    } else {
      line = test
    }
  }
  if (line) lines.push(line.trim())
  return lines
}

// 클립보드 복사 (노션 / LinkedIn용 마크다운)
const copyPortfolioText = () => {
  const title = portfolioTitle.value
  const scenario = portfolioScenario.value
  const scores = portfolioScores.value
  const highlights = portfolioHighlights.value
  const grade = evaluationData.value?.grade || 'A'
  const total = evaluationData.value?.total_score || 0

  const scoresText = Object.entries(scores)
    .map(([k, v]) => `  ${k}: ${v}/100`).join('\n')
  const highlightsText = highlights.map(h => `  ✅ ${h}`).join('\n')

  const text = [
    `🎓 [Wars 실전 AI 시뮬레이션 포트폴리오]`,
    ``,
    `📋 ${title}`,
    `💡 ${scenario}`,
    ``,
    `📊 실력 평가 (AI EvalAgent)`,
    scoresText,
    ` 쉄 Grade: ${grade}  |  Total: ${total}pt`,
    ``,
    `🔑 성취 하이라이트`,
    highlightsText,
    ``,
    `🔗 Powered by Wars — 시스템 설계 AI 실습 플랫폼`,
    `📅 ${todayStr}`
  ].join('\n')

  navigator.clipboard.writeText(text).then(() => {
    copyToastVisible.value = true
    setTimeout(() => { copyToastVisible.value = false }, 2500)
  }).catch(() => {
    // clipboard API 실패 시 폴백
    const ta = document.createElement('textarea')
    ta.value = text
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    copyToastVisible.value = true
    setTimeout(() => { copyToastVisible.value = false }, 2500)
  })
}

</script>

<style scoped>
/* [수정일: 2026-02-23] 성장 보고서 스타일링 */
.growth-report-container {
  min-height: 100vh;
  background: #030712;
  color: #f8fafc;
  padding: 3rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  font-family: 'Inter', sans-serif;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.report-tag {
  font-size: 0.8rem;
  font-weight: 800;
  color: #10b981;
  letter-spacing: 2px;
}

.report-header h1 {
  font-size: 2.5rem;
  font-weight: 900;
  margin-top: 0.5rem;
  background: linear-gradient(to right, #f8fafc, #94a3b8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.total-score-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  background: rgba(30, 41, 59, 0.4);
  padding: 1rem 2rem;
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.grade-badge {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 900;
  border: 4px solid;
}

.grade-badge.S { color: #f59e0b; border-color: #f59e0b; box-shadow: 0 0 15px rgba(245, 158, 11, 0.3); }
.grade-badge.A { color: #818cf8; border-color: #818cf8; }
.grade-badge.B { color: #10b981; border-color: #10b981; }
.grade-badge.C { color: #94a3b8; border-color: #94a3b8; }

.score-info .label {
  display: block;
  font-size: 0.7rem;
  font-weight: 800;
  color: #64748b;
}

.score-info .value {
  font-size: 2rem;
  font-weight: 900;
  font-family: 'JetBrains Mono', monospace;
}

.report-content {
  display: grid;
  grid-template-columns: 450px 1fr;
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* [P1] 팀 점수 비교 패널이 있을 때 3열 */
.report-content.has-team {
  grid-template-columns: 400px 280px 1fr;
  max-width: 1400px;
}

/* 팀 점수 비교 패널 */
.team-score-panel { display: flex; flex-direction: column; gap: 1rem; }

.team-score-list { display: flex; flex-direction: column; gap: 0.75rem; flex: 1; }

.team-score-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 0.75rem;
  border: 1px solid rgba(255,255,255,0.05);
  transition: border-color 0.2s;
}

.team-score-row.top-player {
  border-color: rgba(245, 158, 11, 0.4);
  background: rgba(245, 158, 11, 0.05);
}

.rank-badge {
  font-size: 1.1rem;
  width: 28px;
  text-align: center;
  flex-shrink: 0;
}

.player-info {
  display: flex;
  flex-direction: column;
  min-width: 70px;
}

.player-name {
  font-weight: 700;
  font-size: 0.85rem;
  color: #e2e8f0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 80px;
}

.player-role {
  font-size: 0.6rem;
  color: #64748b;
  font-weight: 700;
}

.score-bar-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.score-bar-bg {
  flex: 1;
  height: 8px;
  background: rgba(30, 41, 59, 0.8);
  border-radius: 4px;
  overflow: hidden;
}

.score-bar-val {
  height: 100%;
  border-radius: 4px;
  transition: width 1s ease;
}
.score-bar-val.rank-1 { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.score-bar-val.rank-2 { background: linear-gradient(90deg, #818cf8, #a5b4fc); }
.score-bar-val.rank-3 { background: linear-gradient(90deg, #10b981, #34d399); }

.score-num {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  font-size: 0.85rem;
  color: #e2e8f0;
  min-width: 36px;
  text-align: right;
}

.team-avg {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 0.75rem;
  border-top: 2px solid rgba(56, 189, 248, 0.2);
  margin-top: auto;
  font-size: 0.8rem;
  color: #94a3b8;
}

.avg-val {
  font-weight: 800;
  font-size: 1.1rem;
  color: #f8fafc;
  font-family: 'JetBrains Mono', monospace;
}

.avg-grade {
  font-size: 1.2rem;
  font-weight: 900;
  padding: 2px 10px;
  border-radius: 6px;
  border: 2px solid;
}
.avg-grade.S { color: #f59e0b; border-color: #f59e0b; }
.avg-grade.A { color: #818cf8; border-color: #818cf8; }
.avg-grade.B { color: #10b981; border-color: #10b981; }
.avg-grade.C { color: #94a3b8; border-color: #94a3b8; }

.glass-panel {
  background: rgba(30, 41, 59, 0.3);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 1.5rem;
  padding: 2rem;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.panel-header h2 {
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: 1px;
  color: #94a3b8;
}

.chart-container {
  height: 350px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rem;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-pill {
  background: rgba(15, 23, 42, 0.6);
  padding: 0.75rem 1.25rem;
  border-radius: 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
}

.stat-value {
  font-weight: 800;
  color: #818cf8;
}

/* Feedback Styles */
.feedback-section {
  margin-bottom: 2rem;
}

.feedback-section h3 {
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 1rem;
  padding-left: 0.5rem;
}

.good h3 { color: #10b981; border-left: 3px solid #10b981; }
.bad h3 { color: #ef4444; border-left: 3px solid #ef4444; }
.action h3 { color: #818cf8; border-left: 3px solid #818cf8; }

.feedback-section ul {
  list-style: none;
  padding-left: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.feedback-section li {
  color: #cbd5e1;
  line-height: 1.6;
  position: relative;
}

.feedback-section li::before {
  content: '•';
  position: absolute;
  left: -1rem;
  color: inherit;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.action-card {
  background: rgba(15, 23, 42, 0.6);
  padding: 1.25rem;
  border-radius: 1rem;
  border-bottom: 3px solid #818cf8;
}

.action-num {
  font-size: 1.25rem;
  font-weight: 900;
  color: #4f46e5;
  display: block;
  margin-bottom: 0.5rem;
}

.action-card p {
  font-size: 0.85rem;
  color: #94a3b8;
  line-height: 1.5;
}

.report-footer {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 2rem;
}

.final-design-preview {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.final-design-preview span {
  font-size: 0.7rem;
  font-weight: 800;
  color: #64748b;
}

.mini-mermaid {
  width: 300px;
  height: 150px;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 0.75rem;
  padding: 1rem;
  overflow: hidden;
}

.action-group {
  display: flex;
  gap: 1rem;
}

.btn-outline {
  padding: 1rem 2rem;
  border-radius: 0.75rem;
  background: transparent;
  border: 1px solid #334155;
  color: #f8fafc;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-outline:hover { background: rgba(255, 255, 255, 0.05); border-color: #64748b; }

.btn-primary {
  padding: 1rem 3rem;
  border-radius: 0.75rem;
  background: #f8fafc;
  color: #030712;
  font-weight: 800;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(255, 255, 255, 0.2); }

/* ── 포트폴리오 익스포트 ── */
.portfolio-export-section {
  max-width: 1200px;
  margin: 0 auto 2rem;
  width: 100%;
  padding: 0 1rem;
}

.pf-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.pf-icon { font-size: 1.75rem; }

.pf-header h2 {
  font-size: 1rem;
  font-weight: 800;
  color: #f1f5f9;
  letter-spacing: 2px;
  margin: 0 0 4px;
}

.pf-desc {
  font-size: 0.8rem;
  color: #64748b;
  margin: 0;
}

/* 포트폴리오 카드 미리보기 */
.pf-card-preview {
  background: linear-gradient(135deg, #030712, #0f172a);
  border: 1px solid rgba(0, 240, 255, 0.25);
  border-radius: 1rem;
  padding: 1.5rem;
  max-width: 560px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 0 40px rgba(0, 240, 255, 0.06);
}

.pfc-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pfc-badge {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  padding: 4px 12px;
  border-radius: 6px;
  background: rgba(0, 240, 255, 0.08);
  color: #00f0ff;
  border: 1px solid rgba(0, 240, 255, 0.2);
}

.pfc-grade-badge {
  font-size: 1.5rem;
  font-weight: 900;
  font-family: 'Orbitron', monospace;
}
.pfc-grade-badge.S { color: #fbbf24; text-shadow: 0 0 10px rgba(251,191,36,0.5); }
.pfc-grade-badge.A { color: #00f0ff; text-shadow: 0 0 10px rgba(0,240,255,0.5); }
.pfc-grade-badge.B { color: #38bdf8; }
.pfc-grade-badge.C { color: #94a3b8; }

.pfc-title {
  font-size: 1.1rem;
  font-weight: 800;
  color: #f1f5f9;
  line-height: 1.3;
}

.pfc-scenario {
  font-size: 0.78rem;
  color: #64748b;
  line-height: 1.5;
  padding: 0.5rem 0.75rem;
  background: rgba(255,255,255,0.02);
  border-left: 2px solid rgba(0,240,255,0.2);
  border-radius: 0 6px 6px 0;
}

.pfc-scores {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pfc-score-item {
  display: grid;
  grid-template-columns: 44px 1fr 36px;
  align-items: center;
  gap: 8px;
}

.pfc-score-label {
  font-size: 0.6rem;
  font-weight: 700;
  color: #64748b;
  font-family: 'Orbitron', monospace;
  letter-spacing: 1px;
}

.pfc-score-bar-wrap {
  height: 8px;
  background: rgba(255,255,255,0.05);
  border-radius: 4px;
  overflow: hidden;
}

.pfc-score-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.6s ease;
}

.pfc-score-val {
  font-size: 0.7rem;
  font-weight: 700;
  color: #94a3b8;
  text-align: right;
  font-family: monospace;
}

.pfc-highlights {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pfc-hl-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 0.78rem;
  color: #e0f2fe;
}

.pfc-hl-icon {
  color: #00f0ff;
  font-weight: 900;
  flex-shrink: 0;
  margin-top: 1px;
}

.pfc-footer {
  display: flex;
  justify-content: space-between;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(255,255,255,0.05);
}

.pfc-source {
  font-size: 0.65rem;
  color: #334155;
  font-family: monospace;
}

.pfc-date {
  font-size: 0.65rem;
  color: #334155;
  font-family: monospace;
}

/* 액션 버튼 */
.pf-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.pf-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 0.9rem 1.75rem;
  border-radius: 0.75rem;
  cursor: pointer;
  font-weight: 700;
  font-size: 0.9rem;
  transition: all 0.2s;
  border: none;
}

.pf-btn-img {
  background: rgba(0, 240, 255, 0.1);
  border: 1px solid rgba(0, 240, 255, 0.3);
  color: #00f0ff;
}
.pf-btn-img:hover { background: rgba(0, 240, 255, 0.15); box-shadow: 0 0 20px rgba(0, 240, 255, 0.2); transform: translateY(-2px); }

.pf-btn-clip {
  background: rgba(168, 85, 247, 0.1);
  border: 1px solid rgba(168, 85, 247, 0.3);
  color: #a855f7;
}
.pf-btn-clip:hover { background: rgba(168, 85, 247, 0.15); box-shadow: 0 0 20px rgba(168, 85, 247, 0.2); transform: translateY(-2px); }

.pf-btn small {
  font-size: 0.6rem;
  font-weight: 400;
  opacity: 0.7;
}

.pf-copy-toast {
  padding: 0.5rem 1rem;
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.3);
  color: #22c55e;
  border-radius: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  animation: fadeIn 0.2s ease;
}

/* ── 인바스켓 위기대응 타임라인 ── */
.incident-timeline-section {
  max-width: 1200px;
  margin: 0 auto 2rem;
  width: 100%;
  padding: 0 1rem;
}

.itl-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.itl-icon { font-size: 1.5rem; }

.itl-header h2 {
  font-size: 0.9rem;
  font-weight: 800;
  color: #f1f5f9;
  letter-spacing: 2px;
}

.itl-badge {
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 2px;
  padding: 3px 10px;
  border-radius: 4px;
  background: rgba(251,191,36,0.15);
  color: #fbbf24;
  border: 1px solid rgba(251,191,36,0.3);
}

.itl-desc {
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 1.5rem;
}

.itl-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.itl-item {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

.itl-time-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 60px;
  flex-shrink: 0;
}

.itl-time {
  font-size: 0.7rem;
  font-weight: 700;
  color: #64748b;
  font-family: 'JetBrains Mono', monospace;
  background: #0f172a;
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid #1e293b;
  white-space: nowrap;
}

.itl-connector {
  width: 2px;
  flex: 1;
  min-height: 24px;
  background: linear-gradient(180deg, #334155, transparent);
  margin: 4px 0;
}

.itl-card {
  flex: 1;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 1rem;
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
  transition: border-color 0.2s;
}

.itl-card.severity-critical { border-left: 3px solid #ef4444; }
.itl-card.severity-high     { border-left: 3px solid #f97316; }
.itl-card.severity-medium   { border-left: 3px solid #eab308; }
.itl-card.severity-low      { border-left: 3px solid #22c55e; }

.itl-card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.6rem;
}

.itl-event-icon { font-size: 1.1rem; }

.itl-event-name {
  font-size: 0.9rem;
  font-weight: 700;
  color: #f1f5f9;
  flex: 1;
}

.itl-severity-badge {
  font-size: 0.55rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  padding: 2px 8px;
  border-radius: 4px;
}

.severity-critical .itl-severity-badge { background: rgba(239,68,68,0.15); color: #ef4444; }
.severity-high .itl-severity-badge     { background: rgba(249,115,22,0.15); color: #f97316; }
.severity-medium .itl-severity-badge   { background: rgba(234,179,8,0.15);  color: #eab308; }
.severity-low .itl-severity-badge      { background: rgba(34,197,94,0.15);  color: #22c55e; }

.itl-card-body { display: flex; flex-direction: column; gap: 0.5rem; }

.itl-action {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.itl-label {
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  color: #64748b;
  padding-top: 2px;
  white-space: nowrap;
}

.itl-text {
  font-size: 0.82rem;
  color: #94a3b8;
  line-height: 1.5;
}

.itl-result {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.75rem;
  font-weight: 700;
}

.itl-result.resolved { color: #22c55e; }
.itl-result.pending  { color: #f59e0b; }

.itl-score {
  font-size: 0.8rem;
  font-weight: 700;
  color: #fbbf24;
  background: rgba(251,191,36,0.1);
  padding: 1px 8px;
  border-radius: 10px;
  border: 1px solid rgba(251,191,36,0.2);
}
</style>
