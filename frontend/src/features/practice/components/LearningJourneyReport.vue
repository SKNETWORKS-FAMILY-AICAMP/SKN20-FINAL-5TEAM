<template>
  <div class="learning-journey-container cyber-panel">
    <!-- Header -->
    <div class="report-header">
      <div class="title-area">
        <h2 class="glitch-text" data-text="CURRICULUM MASTER REPORT">CURRICULUM MASTER REPORT</h2>
        <p class="subtitle">마스터 에이전트의 종합 아키텍처 역량 분석</p>
      </div>
      <div v-if="reportData && reportData.has_data" class="overall-grade-box">
        <span class="label">OVERALL RANK</span>
        <span class="grade-text glowing-text">{{ reportData.report.overall_grade }}</span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <div class="cyber-spinner"></div>
      <p>마스터 에이전트가 우주 저편에서 당신의 데이터를 동기화 중입니다...</p>
    </div>

    <!-- No Data State -->
    <div v-else-if="!reportData || !reportData.has_data" class="empty-state">
      <div class="icon">🚀</div>
      <h3>분석 데이터 부족</h3>
      <p>{{ reportData?.message || '최소 1개 이상의 유닛 미션을 완료해야 마스터 리포트가 생성됩니다.' }}</p>
    </div>

    <!-- Content Area -->
    <div v-else class="report-content custom-scrollbar">
      
      <!-- Summary Section -->
      <section class="report-section summary-section">
        <h3 class="section-title"><i class="icon-summary"></i> 총평: 마스터의 비평</h3>
        <div class="glass-card summary-card">
          <p class="master-voice">"{{ reportData.report.summary }}"</p>
        </div>
      </section>

      <div class="two-column-grid">
        <!-- Growth Points -->
        <section class="report-section">
          <h3 class="section-title text-success"><i class="icon-growth"></i> 성장의 증거</h3>
          <ul class="points-list">
            <li v-for="(point, idx) in reportData.report.growth_points" :key="idx" class="point-item growth">
              <span class="bullet">+</span> {{ point }}
            </li>
          </ul>
        </section>

        <!-- Weakness Alert -->
        <section class="report-section">
          <h3 class="section-title text-danger"><i class="icon-alert"></i> 치명적 취약점 경보</h3>
          <div class="glass-card alert-card">
            <p>{{ reportData.report.weakness_alert }}</p>
            <div class="warning-scanner"></div>
          </div>
        </section>
      </div>

      <!-- Unit Specific Analysis -->
      <section class="report-section">
        <h3 class="section-title"><i class="icon-unit"></i> 유닛별 도달점 분석</h3>
        <div class="unit-analysis-grid">
          <div v-for="(unit, idx) in reportData.report.unit_analysis" :key="idx" class="unit-card glass-card">
            <div class="unit-header">
              <span class="unit-name">{{ unit.unit }}</span>
            </div>
            <p class="unit-comment">{{ unit.comment }}</p>
          </div>
        </div>
      </section>

      <!-- Next Steps -->
      <section class="report-section next-step-section">
        <h3 class="section-title text-primary"><i class="icon-target"></i> 다음 학습 궤도 제안</h3>
        <div class="glass-card advice-card">
          <div class="advice-content">
            <span class="icon">🎯</span>
            <p>{{ reportData.report.next_step_advice }}</p>
          </div>
        </div>
      </section>
    </div>

    <!-- Footer Action -->
    <div class="report-footer">
      <button class="cyber-button secondary" @click="$emit('close')">터미널 닫기</button>
      <button class="cyber-button primary" @click="loadReport">데이터 재스캔</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { fetchMasterAgentReport } from '../services/masterAgentApi';

const props = defineProps({
  // Optional initial data if passed
});

const emit = defineEmits(['close']);

const loading = ref(true);
const reportData = ref(null);

const loadReport = async () => {
  loading.value = true;
  try {
    reportData.value = await fetchMasterAgentReport();
  } catch (error) {
    console.error("Failed to load master report", error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadReport();
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@400;600&display=swap');

.learning-journey-container {
  display: flex;
  flex-direction: column;
  height: 85vh;
  width: 95vw;
  max-width: 1100px;
  background: rgba(10, 10, 26, 0.95);
  border: 1px solid rgba(107, 92, 231, 0.3);
  border-radius: 12px;
  padding: 30px;
  color: #e8eaed;
  font-family: 'Rajdhani', sans-serif;
  box-shadow: 0 0 50px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(107, 92, 231, 0.1);
  position: relative;
  overflow: hidden;
}

/* Header */
.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  border-bottom: 2px solid rgba(107, 92, 231, 0.2);
  padding-bottom: 15px;
}

.glitch-text {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.8rem;
  letter-spacing: 4px;
  color: #fff;
  position: relative;
}

.subtitle {
  color: #4fc3f7;
  font-size: 0.9rem;
  opacity: 0.8;
}

.overall-grade-box {
  background: rgba(107, 92, 231, 0.1);
  border: 1px solid var(--nebula-purple, #6b5ce7);
  padding: 10px 20px;
  border-radius: 8px;
  text-align: center;
}

.overall-grade-box .label {
  display: block;
  font-size: 0.7rem;
  color: #4fc3f7;
  margin-bottom: 5px;
}

.grade-text {
  font-size: 2.2rem;
  font-weight: 800;
  font-family: 'Orbitron', sans-serif;
}

/* Sections */
.report-content {
  flex: 1;
  overflow-y: auto;
  padding-right: 15px;
}

.section-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.1rem;
  margin: 25px 0 15px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.glass-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 20px;
  transition: all 0.3s ease;
}

.master-voice {
  font-style: italic;
  font-size: 1.15rem;
  line-height: 1.6;
  color: #e0e0f0;
}

.two-column-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.points-list {
  list-style: none;
  padding: 0;
}

.point-item {
  background: rgba(255, 255, 255, 0.05);
  margin-bottom: 10px;
  padding: 12px 15px;
  border-radius: 6px;
  border-left: 3px solid transparent;
}

.point-item.growth {
  border-left-color: #00e676;
}

.alert-card {
  border: 1px solid rgba(255, 23, 68, 0.3);
  background: rgba(255, 23, 68, 0.02);
  position: relative;
  overflow: hidden;
}

.warning-scanner {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 2px;
  background: linear-gradient(to right, transparent, #ff1744, transparent);
  animation: scan 3s linear infinite;
}

@keyframes scan {
  0% { transform: translateY(-20px); }
  100% { transform: translateY(120px); }
}

.unit-analysis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.unit-card .unit-name {
  color: #6b5ce7;
  font-weight: bold;
  font-size: 1rem;
  margin-bottom: 10px;
  display: block;
}

.advice-card {
  border: 1px solid rgba(79, 195, 247, 0.4);
  background: linear-gradient(135deg, rgba(79, 195, 247, 0.05) 0%, transparent 100%);
}

.advice-content {
  display: flex;
  gap: 15px;
  align-items: center;
}

.advice-content .icon { font-size: 2rem; }

/* Actions */
.report-footer {
  margin-top: 30px;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

.cyber-button {
  padding: 10px 25px;
  border-radius: 5px;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.cyber-button.primary {
  background: #6b5ce7;
  color: white;
}

.cyber-button.secondary {
  background: transparent;
  border-color: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.cyber-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 15px rgba(107, 92, 231, 0.4);
}

/* Utilities */
.glowing-text {
  text-shadow: 0 0 10px rgba(107, 92, 231, 0.8), 0 0 20px rgba(107, 92, 231, 0.4);
}

.loading-overlay {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 20px;
}

.cyber-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(107, 92, 231, 0.2);
  border-top-color: #6b5ce7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(107, 92, 231, 0.3);
  border-radius: 10px;
}
</style>
