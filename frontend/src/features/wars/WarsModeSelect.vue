<template>
  <div class="mode-select-container">
    <!-- Animated Background -->
    <div class="bg-grid"></div>
    <div class="bg-orb orb-1"></div>
    <div class="bg-orb orb-2"></div>
    <div class="bg-orb orb-3"></div>

    <header class="mode-header">
      <div class="logo-area">
        <span class="logo-icon">🗡️</span>
        <h1 class="logo-text">TEAM BATTLE</h1>
      </div>
      <p class="tagline">아키텍처 능력을 증명하라. 당신의 전장을 선택하세요.</p>
    </header>

    <main class="mode-grid">
      <!-- Mode 1: 기존 아키텍처 서바이벌 -->
      <div class="mode-card survival" @click="goTo('/practice/coduck-wars/briefing')">
        <div class="card-glow"></div>
        <div class="card-inner">
          <div class="mode-badge">ORIGINAL</div>
          <div class="mode-icon">🏗️</div>
          <h2 class="mode-title">아키텍처 서바이벌</h2>
          <p class="mode-desc">AI 면접관의 압박 속에서 실시간으로 시스템을 설계하고, 장애를 복구하라.</p>
          <div class="mode-tags">
            <span class="tag">3인 협동</span>
            <span class="tag">실시간 코딩</span>
            <span class="tag">AI 면접</span>
          </div>
          <div class="mode-meta">
            <span>⏱ 10분</span>
            <span>👥 1~3인</span>
            <span>🔥 고급</span>
          </div>
        </div>
        <div class="card-arrow">→</div>
      </div>

      <!-- Mode 2: 아키텍처 드로잉 퀴즈 -->
      <div class="mode-card drawing" @click="goTo('/practice/coduck-wars/draw-quiz')">
        <div class="card-glow"></div>
        <div class="card-inner">
          <div class="mode-badge hot">NEW</div>
          <div class="mode-icon">🎨</div>
          <h2 class="mode-title">아키텍처 캐치마인드</h2>
          <p class="mode-desc">AI가 다이어그램을 하나씩 그린다. 완성되기 전에 어떤 아키텍처 패턴인지 맞춰라!</p>
          <div class="mode-tags">
            <span class="tag">실시간 드로잉</span>
            <span class="tag">AI 힌트</span>
            <span class="tag">5라운드</span>
          </div>
          <div class="mode-meta">
            <span>⏱ 5분</span>
            <span>👤 1인</span>
            <span>⭐ 초급~중급</span>
          </div>
        </div>
        <div class="card-arrow">→</div>
      </div>

      <!-- Mode 3: 로직 런 (2026-02-24 수정 - 스피드 아키텍처 빌더에서 교체) -->
      <div class="mode-card speed" @click="goTo('/practice/coduck-wars/logic-run')">
        <div class="card-glow"></div>
        <div class="card-inner">
          <div class="mode-badge hot">NEW</div>
          <div class="mode-icon">🏃</div>
          <h2 class="mode-title">로직 런</h2>
          <p class="mode-desc">AI 추격자를 피해 팀원과 릴레이로 의사코드를 작성하며 논리의 성을 향해 질주하라!</p>
          <div class="mode-tags">
            <span class="tag">릴레이 코딩</span>
            <span class="tag">AI 추격</span>
            <span class="tag">팀 협동</span>
          </div>
          <div class="mode-meta">
            <span>⏱ 10분</span>
            <span>👥 2~3인</span>
            <span>⭐ 중급</span>
          </div>
        </div>
        <div class="card-arrow">→</div>
      </div>

      <!-- Mode 4: 1:1 버그 버블 몬스터 (신규) -->
      <div class="mode-card battle" @click="goTo('/practice/coduck-wars/bug-bubble')">
        <div class="card-glow"></div>
        <div class="card-inner">
          <div class="mode-badge hot">NEW</div>
          <div class="mode-icon">🫧</div>
          <h2 class="mode-title">버그버블 몬스터</h2>
          <p class="mode-desc">문제를 풀고 버그를 가둬 상대에게 날려라! 보글보글 1:1 디펜스 승부.</p>
          <div class="mode-tags">
            <span class="tag">1:1 대전</span>
            <span class="tag">실시간 어택</span>
            <span class="tag">디펜스</span>
          </div>
          <div class="mode-meta">
            <span>⏱ 무제한</span>
            <span>👤 1vs1</span>
            <span>🔥 버그 파티</span>
          </div>
        </div>
        <div class="card-arrow">→</div>
      </div>
    </main>

    <!-- Leaderboard Peek -->
    <footer class="mode-footer">
      <div class="leaderboard-peek glass-card">
        <div class="lb-header">
          <span class="lb-icon">🏆</span>
          <span>TOP ARCHITECTS</span>
        </div>
        <div class="lb-rows">
          <div class="lb-row" v-for="(player, idx) in topPlayers" :key="idx">
            <span class="lb-rank" :class="'rank-' + (idx + 1)">{{ idx === 0 ? '👑' : '#' + (idx + 1) }}</span>
            <span class="lb-name">{{ player.name }}</span>
            <span class="lb-score">{{ player.score }}pt</span>
          </div>
        </div>
      </div>
      <div class="footer-hint">
        <span>💡 새 모드에서 획득한 점수는 통합 랭킹에 반영됩니다</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const topPlayers = ref([
  { name: 'ArchMaster_Kim', score: 2480 },
  { name: 'CloudNinja_23', score: 2210 },
  { name: 'SRE_Hero', score: 1950 },
  { name: 'DevOps_Duck', score: 1820 },
  { name: 'SystemPro_J', score: 1700 },
]);

const goTo = (path) => {
  router.push(path);
};
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

/* Responsive */
@media (max-width: 768px) {
  .mode-grid { grid-template-columns: 1fr; }
  .logo-text { font-size: 2.5rem; }
}
</style>
