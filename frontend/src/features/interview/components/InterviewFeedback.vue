<template>
  <div class="interview-feedback">
    <div class="feedback-header">
      <div class="feedback-icon"></div>
      <h2 class="feedback-title">면접 완료</h2>
      <p class="feedback-subtitle">모의면접이 끝났습니다. 아래 피드백을 확인해보세요.</p>
    </div>

    <!-- [수정일: 2026-02-23] [vision] 비전 분석 리포트 오버레이 -->
    <VisionAnalysisReport v-if="feedback.vision_analysis" :analysis="feedback.vision_analysis" />

    <!-- 전체 총평 -->
    <section class="feedback-section mt-8">
      <h3 class="section-title">전체 총평</h3>
      <p class="overall-summary">{{ feedback.overall_summary }}</p>
    </section>

    <!-- 강점 -->
    <section v-if="feedback.top_strengths?.length" class="feedback-section feedback-section--strength">
      <h3 class="section-title">강점</h3>
      <ul class="feedback-list feedback-list--strength">
        <li v-for="(item, idx) in feedback.top_strengths" :key="idx">{{ item }}</li>
      </ul>
    </section>

    <!-- 개선 방향 -->
    <section v-if="feedback.top_improvements?.length" class="feedback-section feedback-section--improve">
      <h3 class="section-title">개선 방향</h3>
      <ul class="feedback-list feedback-list--improve">
        <li v-for="(item, idx) in feedback.top_improvements" :key="idx">{{ item }}</li>
      </ul>
    </section>

    <!-- 학습 추천 -->
    <section v-if="feedback.recommendation" class="feedback-section">
      <h3 class="section-title">학습 추천</h3>
      <p class="recommendation">{{ feedback.recommendation }}</p>
    </section>

    <!-- 역량 슬롯별 상세 -->
    <section v-if="slotSummaryList.length" class="feedback-section">
      <h3 class="section-title">역량별 결과</h3>
      <div class="slot-cards">
        <div
          v-for="(item, idx) in slotSummaryList"
          :key="idx"
          class="slot-card"
          :class="`slot-card--${item.status.toLowerCase()}`"
        >
          <div class="slot-card__header">
            <span class="slot-card__name">{{ item.topic }}</span>
            <span class="slot-card__status">{{ statusLabel(item.status) }}</span>
          </div>
          <p v-if="item.summary" class="slot-card__summary">{{ item.summary }}</p>
          <div v-if="item.confirmed_evidence?.length" class="slot-card__evidence">
            <span class="evidence-label">확인됨:</span>
            <span
              v-for="ev in item.confirmed_evidence"
              :key="ev"
              class="evidence-tag evidence-tag--confirmed"
            >{{ formatLabel(ev) }}</span>
          </div>
          <div v-if="item.missing_evidence?.length" class="slot-card__evidence">
            <span class="evidence-label">미확인:</span>
            <span
              v-for="ev in item.missing_evidence"
              :key="ev"
              class="evidence-tag evidence-tag--missing"
            >{{ formatLabel(ev) }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 다시 시작 버튼 -->
    <div class="feedback-actions">
      <button class="restart-btn" @click="emit('restart')">다시 면접하기</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import VisionAnalysisReport from './VisionAnalysisReport.vue'; // [수정일: 2026-02-23] [vision] 리포트 임포트

const props = defineProps({
  feedback: { type: Object, required: true },
});

const emit = defineEmits(['restart']);

const SLOT_LABELS = {
  motivation: '지원 동기',
  collaboration: '협업 능력',
  technical_depth: '기술 활용 능력',
  growth: '성장 경험',
  problem_solving: '문제 해결력',
};

const slotSummaryList = computed(() => {
  const summary = props.feedback.slot_summary;
  if (!summary || typeof summary !== 'object') return [];
  return Object.entries(summary).map(([slot, data]) => ({
    slot,
    topic: SLOT_LABELS[slot] || data.topic || slot.replace(/_/g, ' '),
    status: data.final_status || 'UNKNOWN',
    summary: data.summary || '',
    confirmed_evidence: data.confirmed_evidence || [],
    missing_evidence: data.missing_evidence || [],
  }));
});

function formatLabel(str) {
  return str.replace(/_/g, ' ');
}

function statusLabel(status) {
  const map = {
    CLEAR: '확인 완료',
    PARTIAL: '일부 확인',
    UNCERTAIN: '미확인',
    UNKNOWN: '미확인',
  };
  return map[status] || status;
}
</script>

<style scoped>
.interview-feedback {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px 40px 48px;
}

.feedback-header {
  text-align: center;
  margin-bottom: 32px;
}

.feedback-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.feedback-title {
  font-size: 26px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 6px;
}

.feedback-subtitle {
  color: #6b7280;
  font-size: 14px;
}

.feedback-section {
  margin-bottom: 16px;
  background: white;
  border-radius: 12px;
  padding: 20px 24px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}
.feedback-section--strength {
  background: #f0fdf4;
  border-color: #86efac;
}
.feedback-section--improve {
  background: #fff5f5;
  border-color: #fca5a5;
}

.section-title {
  font-family: 'Outfit', sans-serif;
  font-size: 15px;
  font-weight: 700;
  color: #1f2937;
  -webkit-text-fill-color: #1f2937;
  background: none;
  -webkit-background-clip: unset;
  background-clip: unset;
  margin-bottom: 14px;
  padding-left: 10px;
  border-left: 3px solid #6366f1;
}

.overall-summary {
  font-size: 14px;
  line-height: 1.75;
  color: #374151;
  background: #f9fafb;
  border-radius: 8px;
  padding: 14px;
}

.recommendation {
  font-size: 14px;
  line-height: 1.75;
  color: #374151;
  background: #eff6ff;
  border-radius: 10px;
  padding: 16px;
  border-left: 4px solid #3b82f6;
}

.feedback-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.feedback-list li {
  font-size: 14px;
  line-height: 1.6;
  color: #374151;
  padding: 10px 14px 10px 36px;
  border-radius: 8px;
  position: relative;
}

.feedback-list li::before {
  position: absolute;
  left: 12px;
  top: 11px;
}

.feedback-list--strength li {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
}

.feedback-list--strength li::before {
  content: '✓';
  color: #16a34a;
}

.feedback-list--improve li {
  background: #fffbeb;
  border: 1px solid #fde68a;
}

.feedback-list--improve li::before {
  content: '→';
  color: #d97706;
}

/* 슬롯 카드 */
.slot-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px;
}

.slot-card {
  border: 1.5px solid #e5e7eb;
  border-radius: 12px;
  padding: 14px 16px;
}

.slot-card--clear { border-color: #86efac; background: #f0fdf4; }
.slot-card--partial { border-color: #fcd34d; background: #fffbeb; }
.slot-card--uncertain, .slot-card--unknown { border-color: #d1d5db; background: #f9fafb; }

.slot-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.slot-card__name {
  font-weight: 600;
  font-size: 14px;
  color: #111;
}

.slot-card__status {
  font-size: 12px;
  color: #555;
}

.slot-card__summary {
  font-size: 13px;
  color: #374151;
  line-height: 1.6;
  margin-bottom: 8px;
}

.slot-card__evidence {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}

.evidence-label {
  font-size: 11px;
  color: #888;
  margin-right: 2px;
}

.evidence-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 99px;
}

.evidence-tag--confirmed {
  background: #d1fae5;
  color: #065f46;
}

.evidence-tag--missing {
  background: #fee2e2;
  color: #991b1b;
}

/* 액션 */
.feedback-actions {
  text-align: center;
  margin-top: 32px;
}

.restart-btn {
  padding: 12px 32px;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.restart-btn:hover {
  background: #4f46e5;
}
</style>
