<template>
  <div class="mode-select-container">
    <!-- Animated Background -->
    <div class="bg-grid"></div>
    <div class="bg-orb orb-1"></div>
    <div class="bg-orb orb-2"></div>
    <div class="bg-orb orb-3"></div>

    <header class="mode-header">
      <div class="logo-area">
        <span class="logo-icon">⚔️</span>
        <h1 class="logo-text">BATTLE GAME</h1>
      </div>
      <p class="tagline">아키텍처 능력을 증명하라. 당신의 전장을 선택하세요.</p>
      
      <!-- [추가: 2026-03-03] 나가기 버튼 -->
      <button class="exit-btn" @click="goTo('/dashboard')">
        <span class="exit-icon">🚪</span>
        <span class="exit-text">EXIT</span>
      </button>
    </header>

    <main class="mode-grid">
      <!-- Mode 1: 로직 런 (2026-03-03 수정 - Wars 경로 통일) -->
      <div class="mode-card speed" @click="goTo('/practice/wars/logic-run')">
        <div class="card-glow"></div>
        <div class="card-inner">
          <div class="mode-badge hot">NEW</div>
          <div class="mode-icon">🏃</div>
          <h2 class="mode-title">로직 런</h2>
          <p class="mode-desc">빈칸 채우기 스피드전 + 설계 드로잉 대결! 더 빠르고 정확한 엔지니어가 승리한다.</p>
          <div class="mode-tags">
            <span class="tag">빈칸 채우기</span>
            <span class="tag">스피드</span>
            <span class="tag">의사코드</span>
          </div>
          <div class="mode-meta">
            <span>⏱ 10분</span>
            <span>👥 1vs1</span>
            <span>⭐ 중급</span>
          </div>
        </div>
        <div class="card-arrow">→</div>
      </div>

      <!-- Mode 2: 1:1 버그 버블 몬스터 (신규) -->
      <div class="mode-card battle" @click="goTo('/practice/wars/bug-bubble')">
        <div class="card-glow"></div>
        <div class="card-inner">
          <div class="mode-badge hot">NEW</div>
          <div class="mode-icon">🫧</div>
          <h2 class="mode-title">버그버블 몬스터</h2>
          <p class="mode-desc">문제를 풀고 버그를 가둬 상대에게 날려라! 보글보글 1:1 디펜스 승부.</p>
          <div class="mode-tags">
            <span class="tag">디버깅</span>
            <span class="tag">몬스터 어택</span>
            <span class="tag">서바이벌</span>
          </div>
          <div class="mode-meta">
            <span>⏱ 무제한</span>
            <span>👤 1vs1</span>
            <span>🔥 버그 파티</span>
          </div>
        </div>
        <div class="card-arrow">→</div>
      </div>

      <!-- Mode 3: 아키텍처 드로잉 퀴즈 (2026-03-03 수정 - Wars 경로 통일) -->
      <div class="mode-card drawing card-solo-last" @click="goTo('/practice/wars/draw-quiz')">
        <div class="card-glow"></div>
        <div class="card-inner">
          <div class="mode-badge hot">NEW</div>
          <div class="mode-icon">🎨</div>
          <h2 class="mode-title">아키텍처 캐치마인드</h2>
          <p class="mode-desc">제시된 아키텍처를 직접 드래그&드롭으로 설계하라! AI가 실시간으로 평가하는 1vs1 드로잉 배틀.</p>
          <div class="mode-tags">
            <span class="tag">시스템 설계</span>
            <span class="tag">드로잉</span>
            <span class="tag">AI 리뷰</span>
          </div>
          <div class="mode-meta">
            <span>⏱ 45초</span>
            <span>👤 1vs1</span>
            <span>⭐ 초급~중급</span>
          </div>
        </div>
        <div class="card-arrow">→</div>
      </div>
    </main>

    <!-- 전적 표 -->
    <footer class="mode-footer">
      <div class="leaderboard-peek glass-card">
        <div class="lb-header">
          <span class="lb-icon">⚔️</span>
          <span>BATTLE RECORDS</span>
          <button class="lb-reset-btn" @click="resetRecords" title="전적 초기화">↺</button>
        </div>

        <!-- 전적 없을 때 -->
        <div v-if="!records.length" class="lb-empty">
          <span>아직 전적이 없습니다. 첫 대전을 시작하세요!</span>
        </div>

        <!-- 전적 있을 때 -->
        <template v-else>
          <div class="lb-col-header">
            <span class="col-name">플레이어</span>
            <span class="col-w">승</span>
            <span class="col-d">무</span>
            <span class="col-l">패</span>
            <span class="col-rate">승률</span>
          </div>
          <div class="lb-row" v-for="(r, idx) in records" :key="r.name">
            <span class="lb-rank" :class="'rank-' + (idx + 1)">{{ idx === 0 ? '👑' : '#' + (idx + 1) }}</span>
            <span class="lb-name">{{ r.name }}</span>
            <span class="col-w stat-win">{{ r.win }}</span>
            <span class="col-d stat-draw">{{ r.draw }}</span>
            <span class="col-l stat-lose">{{ r.lose }}</span>
            <span class="col-rate">
              <span class="rate-bar-wrap">
                <span class="rate-bar" :style="{ width: winRate(r) + '%' }"></span>
              </span>
              <span class="rate-txt">{{ winRate(r) }}%</span>
            </span>
          </div>
        </template>
      </div>
      <div class="footer-hint">
        <span>💡 대전 결과가 자동으로 이 화면에 기록됩니다</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { loadBattleRecords, clearBattleRecords } from './useBattleRecord.js';
import { useAuthStore } from '@/stores/auth'; // [추가]

const router = useRouter();
const auth = useAuthStore(); // [추가]

const rawRecords = ref([])
onMounted(async () => { 
  // [수정일: 2026-03-03] 비동기로 서버에서 전적 로드
  rawRecords.value = await loadBattleRecords(auth.sessionNickname) 
})

// 승률 기준 내림차순 정렬
const records = computed(() =>
  [...rawRecords.value]
    .map(r => ({ ...r, total: r.win + r.draw + r.lose }))
    .sort((a, b) => {
      const rateA = a.total ? a.win / a.total : 0
      const rateB = b.total ? b.win / b.total : 0
      if (rateB !== rateA) return rateB - rateA
      return b.win - a.win
    })
)

function winRate(r) {
  const total = r.win + r.draw + r.lose
  return total ? Math.round((r.win / total) * 100) : 0
}

function resetRecords() {
  if (!confirm('전적을 모두 삭제하시겠습니까?')) return
  clearBattleRecords()
  rawRecords.value = []
}

const goTo = (path) => router.push(path);
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Syne:wght@700;800&display=swap');

.mode-select-container {
  min-height: 100vh;
  background: #04060e;
  color: #e8ecf4;
  padding: 3rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 3rem;
  position: relative;
  overflow: hidden;
  font-family: 'Space Grotesk', sans-serif;
}

/* Animated grid background */
.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(56, 189, 248, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(56, 189, 248, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  z-index: 0;
  animation: gridDrift 20s linear infinite;
}

@keyframes gridDrift {
  0% { transform: translate(0, 0); }
  100% { transform: translate(60px, 60px); }
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  z-index: 0;
  animation: orbFloat 8s ease-in-out infinite;
}
.orb-1 { width: 500px; height: 500px; top: -10%; left: -5%; background: rgba(59, 130, 246, 0.12); }
.orb-2 { width: 400px; height: 400px; bottom: 0; right: -5%; background: rgba(168, 85, 247, 0.1); animation-delay: 3s; }
.orb-3 { width: 300px; height: 300px; top: 50%; left: 40%; background: rgba(16, 185, 129, 0.08); animation-delay: 5s; }

@keyframes orbFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(30px, -20px) scale(1.05); }
}

/* Header */
.mode-header {
  position: relative;
  z-index: 10;
  text-align: center;
}

.logo-area {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.logo-icon { font-size: 2.5rem; }

.logo-text {
  font-family: 'Syne', sans-serif;
  font-size: 3.5rem;
  font-weight: 800;
  letter-spacing: -2px;
  background: linear-gradient(135deg, #60a5fa, #a78bfa, #34d399);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 0 20px rgba(96, 165, 250, 0.3));
}

.tagline {
  color: #64748b;
  font-size: 1rem;
  letter-spacing: 0.5px;
}

/* [추가: 2026-03-03] 나가기 버튼 스타일 */
.exit-btn {
  position: absolute;
  top: 0;
  right: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  color: #94a3b8;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: 0.8rem;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 20;
}

.exit-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #f87171;
  transform: translateX(-5px);
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.1);
}

.exit-icon { font-size: 1rem; }

/* Mode Grid */
.mode-grid {
  position: relative;
  z-index: 10;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  max-width: 1100px;
  margin: 0 auto;
  width: 100%;
}

/* 세 번째 카드가 단독으로 있을 때 양쪽 중앙 정렬 */
.mode-card:last-child:nth-child(odd) {
  grid-column: 1 / -1;
  max-width: 520px;
  margin: 0 auto;
  width: 100%;
}

/* 카드 3개일 때 3번째만 중앙정렬 - 클래스 직접 지정 방식 (보조 규칙의 선택자 문제 방지) */
.card-solo-last {
  grid-column: 1 / -1;
  max-width: 520px;
  margin: 0 auto;
  width: 100%;
}

.mode-card {
  position: relative;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 1.5rem;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.mode-card:hover {
  transform: translateY(-6px);
  border-color: rgba(255, 255, 255, 0.15);
}

.mode-card:hover .card-glow { opacity: 1; }
.mode-card:hover .card-arrow { opacity: 1; transform: translateX(0); }

.card-glow {
  position: absolute;
  inset: 0;
  border-radius: 1.5rem;
  opacity: 0;
  transition: opacity 0.4s;
  z-index: 0;
}

.survival .card-glow { background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(96, 165, 250, 0.04)); }
.drawing .card-glow { background: linear-gradient(135deg, rgba(251, 191, 36, 0.08), rgba(245, 158, 11, 0.04)); }
.speed .card-glow { background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(52, 211, 153, 0.04)); }
.battle .card-glow { background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(248, 113, 113, 0.04)); }

.survival:hover { border-color: rgba(59, 130, 246, 0.4); box-shadow: 0 8px 40px rgba(59, 130, 246, 0.1); }
.drawing:hover { border-color: rgba(251, 191, 36, 0.4); box-shadow: 0 8px 40px rgba(251, 191, 36, 0.1); }
.speed:hover { border-color: rgba(16, 185, 129, 0.4); box-shadow: 0 8px 40px rgba(16, 185, 129, 0.1); }
.battle:hover { border-color: rgba(239, 68, 68, 0.4); box-shadow: 0 8px 40px rgba(239, 68, 68, 0.1); }

.card-inner { position: relative; z-index: 1; }

.mode-badge {
  display: inline-block;
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 2px;
  padding: 3px 10px;
  border-radius: 4px;
  background: rgba(100, 116, 139, 0.2);
  color: #94a3b8;
  margin-bottom: 1rem;
}

.mode-badge.hot {
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
  animation: badgePulse 2s infinite;
}

@keyframes badgePulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.3); }
  50% { box-shadow: 0 0 0 6px rgba(251, 191, 36, 0); }
}

.mode-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3));
}

.mode-title {
  font-family: 'Syne', sans-serif;
  font-size: 1.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  color: #f1f5f9;
}

.mode-desc {
  font-size: 0.85rem;
  color: #94a3b8;
  line-height: 1.6;
  margin-bottom: 1.25rem;
}

.mode-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 1rem;
}

.tag {
  font-size: 0.65rem;
  padding: 3px 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
  color: #cbd5e1;
  font-weight: 600;
}

.mode-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.7rem;
  color: #64748b;
  font-weight: 600;
}

.card-arrow {
  position: absolute;
  bottom: 2rem;
  right: 2rem;
  font-size: 1.5rem;
  color: #64748b;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s ease;
}

/* Footer */
.mode-footer {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  max-width: 600px;
  margin: 0 auto;
  width: 100%;
}

.glass-card {
  width: 100%;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 1rem;
  padding: 1.25rem;
}

.lb-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: 1.5px;
  margin-bottom: 0.75rem;
}

.lb-rows { display: flex; flex-direction: column; gap: 0.4rem; }

.lb-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.4rem 0.5rem;
  border-radius: 0.5rem;
  transition: background 0.2s;
}

.lb-row:hover { background: rgba(255, 255, 255, 0.03); }

.lb-rank { width: 24px; text-align: center; font-size: 0.8rem; }
.lb-rank.rank-1 { font-size: 1rem; }
.lb-name { flex: 1; font-weight: 600; font-size: 0.8rem; color: #e2e8f0; }
.lb-score { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 0.8rem; color: #fbbf24; }

.footer-hint {
  font-size: 0.75rem;
  color: #475569;
}

/* 전적 테이블 */
.lb-reset-btn {
  margin-left: auto;
  background: transparent;
  border: 1px solid rgba(255,255,255,0.08);
  color: #475569;
  border-radius: 4px;
  padding: 1px 6px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}
.lb-reset-btn:hover { color: #ff2d75; border-color: rgba(255,45,117,0.4); }

.lb-empty {
  text-align: center;
  padding: 1rem 0;
  font-size: 0.8rem;
  color: #475569;
}

.lb-col-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.2rem 0.5rem;
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 1px;
  color: #475569;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  margin-bottom: 0.3rem;
}

.lb-row { display: flex; align-items: center; gap: 0.5rem; padding: 0.45rem 0.5rem; border-radius: 0.5rem; transition: background 0.2s; }
.lb-row:hover { background: rgba(255,255,255,0.03); }

.lb-rank { width: 24px; text-align: center; font-size: 0.8rem; flex-shrink: 0; }
.lb-rank.rank-1 { font-size: 1rem; }
.lb-name { flex: 1; font-weight: 600; font-size: 0.8rem; color: #e2e8f0; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.col-name { flex: 1; }
.col-w  { width: 28px; text-align: center; flex-shrink: 0; }
.col-d  { width: 28px; text-align: center; flex-shrink: 0; }
.col-l  { width: 28px; text-align: center; flex-shrink: 0; }
.col-rate { width: 90px; display: flex; align-items: center; gap: 5px; flex-shrink: 0; }

.stat-win  { font-weight: 700; font-size: 0.82rem; color: #34d399; }
.stat-draw { font-weight: 700; font-size: 0.82rem; color: #94a3b8; }
.stat-lose { font-weight: 700; font-size: 0.82rem; color: #f87171; }

.rate-bar-wrap { flex: 1; height: 4px; background: rgba(255,255,255,0.06); border-radius: 2px; overflow: hidden; }
.rate-bar { height: 100%; background: linear-gradient(90deg, #34d399, #60a5fa); border-radius: 2px; transition: width 0.5s ease; }
.rate-txt { font-size: 0.68rem; color: #94a3b8; font-weight: 600; white-space: nowrap; }

/* Responsive */
@media (max-width: 768px) {
  .mode-grid { grid-template-columns: 1fr; }
  .logo-text { font-size: 2.5rem; }
}
</style>
