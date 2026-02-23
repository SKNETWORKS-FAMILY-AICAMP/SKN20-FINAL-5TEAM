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

    <main class="report-content">
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
import { ref, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { Chart, registerables } from 'chart.js';
import mermaid from 'mermaid';
import { useGameStore } from '@/stores/game';

Chart.register(...registerables);

// [수정일: 2026-02-23] Coduck Wars Step 3: 성장 보고서 UI 구현
const router = useRouter();
const gameStore = useGameStore();
const evaluationData = ref(gameStore.lastEvaluation);
const radarChart = ref(null);
const mermaidTarget = ref(null);

onMounted(async () => {
  if (!evaluationData.value) {
    // 데이터가 없으면 홈으로 리다이렉트 (실제 운영 시)
    // router.push('/practice/coduck-wars');
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
const replayMission = () => router.push('/practice/coduck-wars');
const downloadPdf = () => alert('PDF 생성 기능은 준비 중입니다.');

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
</style>
