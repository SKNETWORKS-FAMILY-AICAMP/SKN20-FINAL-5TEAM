<template>
  <div class="interview-history">
    <div class="history-header">
      <button class="btn-back" @click="$emit('back')">← 돌아가기</button>
      <div>
        <h2 class="history-title">면접 기록</h2>
        <p class="history-desc">총 {{ sessions.length }}개의 면접 기록</p>
      </div>
    </div>

    <div v-if="isLoading" class="loading-msg">불러오는 중...</div>

    <div v-else-if="!sessions.length" class="empty-msg">
      <div class="empty-icon">📋</div>
      <p>완료된 면접 기록이 없습니다.</p>
      <p class="empty-sub">면접을 진행하면 여기서 결과를 확인할 수 있어요.</p>
    </div>

    <div v-else class="session-list">
      <div
        v-for="session in sortedSessions"
        :key="session.id"
        class="session-card"
        @click="openDetail(session.id)"
      >
        <div class="session-card__top">
          <div class="session-company">
            <span class="company-icon">🏢</span>
            <div>
              <div class="company-name">{{ session.job_posting?.company_name || '공고 없이 진행' }}</div>
              <div class="company-position">{{ session.job_posting?.position || '-' }}</div>
            </div>
          </div>
          <div class="session-card__actions">
            <div class="session-status" :class="statusClass(session.status)">
              {{ statusLabel(session.status) }}
            </div>
            <button class="btn-delete-session" @click.stop="removeSession(session.id)" title="삭제">✕</button>
          </div>
        </div>

        <div class="session-card__bottom">
          <div class="session-slots">
            <span
              v-for="slot in session.slot_progress"
              :key="slot.slot"
              class="slot-pill"
              :class="slotStatusClass(slot.status)"
              :title="slot.topic"
            >
              {{ slot.topic }}
            </span>
          </div>
          <div class="session-date">{{ formatDate(session.started_at) }}</div>
        </div>
      </div>
    </div>

    <!-- 상세 모달 -->
    <div v-if="selectedSession" class="detail-overlay" @click.self="selectedSession = null">
      <div class="detail-panel">
        <div class="detail-header">
          <div>
            <h3 class="detail-company">{{ selectedSession.job_posting?.company_name || '공고 없이 진행' }}</h3>
            <p class="detail-meta">
              {{ selectedSession.job_posting?.position || '' }}
              <span v-if="selectedSession.job_posting?.position"> · </span>
              {{ formatDate(selectedSession.started_at) }}
            </p>
          </div>
          <button class="btn-close" @click="selectedSession = null">✕</button>
        </div>

        <div class="detail-body">
          <!-- 피드백 섹션 -->
          <div v-if="selectedSession.feedback" class="detail-feedback">
            <h4 class="section-title">📊 전체 평가</h4>
            <p class="feedback-summary">{{ selectedSession.feedback.overall_summary }}</p>

            <div class="feedback-two-col">
              <div v-if="selectedSession.feedback.top_strengths?.length" class="feedback-col">
                <strong class="feedback-col__title strength">강점</strong>
                <ul class="feedback-list">
                  <li v-for="s in selectedSession.feedback.top_strengths" :key="s">{{ s }}</li>
                </ul>
              </div>
              <div v-if="selectedSession.feedback.top_improvements?.length" class="feedback-col">
                <strong class="feedback-col__title improve">개선점</strong>
                <ul class="feedback-list">
                  <li v-for="i in selectedSession.feedback.top_improvements" :key="i">{{ i }}</li>
                </ul>
              </div>
            </div>

            <div v-if="selectedSession.feedback.recommendation" class="feedback-recommendation">
              💡 {{ selectedSession.feedback.recommendation }}
            </div>
          </div>

          <!-- 역량별 결과 -->
          <div class="detail-slots">
            <h4 class="section-title">역량별 결과</h4>
            <div
              v-for="slot in selectedSession.slot_progress"
              :key="slot.slot"
              class="slot-result-row"
            >
              <span class="slot-topic-label">{{ slot.topic }}</span>
              <span class="slot-status-badge" :class="slotStatusClass(slot.status)">
                {{ slotStatusKo(slot.status) }}
              </span>
            </div>
          </div>

          <!-- Q&A 목록 -->
          <div v-if="selectedSession.turns?.length" class="detail-qa">
            <h4 class="section-title">면접 Q&A</h4>
            <div v-for="turn in selectedSession.turns" :key="turn.turn_number" class="qa-item">
              <div class="qa-q">Q{{ turn.turn_number }}. {{ turn.question }}</div>
              <div class="qa-a">{{ turn.answer }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { getSessions, getSession, deleteSession } from '../api/interviewApi';

defineEmits(['back']);

const sessions = ref([]);
const isLoading = ref(true);
const selectedSession = ref(null);

const sortedSessions = computed(() =>
  [...sessions.value].sort((a, b) => new Date(b.started_at) - new Date(a.started_at))
);

onMounted(async () => {
  try {
    sessions.value = await getSessions();
  } catch {}
  finally { isLoading.value = false; }
});

async function openDetail(sessionId) {
  try {
    selectedSession.value = await getSession(sessionId);
  } catch {}
}

async function removeSession(sessionId) {
  try {
    await deleteSession(sessionId);
    sessions.value = sessions.value.filter(s => s.id !== sessionId);
    if (selectedSession.value?.id === sessionId) selectedSession.value = null;
  } catch {}
}

function statusLabel(s) {
  return { completed: '완료', in_progress: '진행중', abandoned: '중단' }[s] || s;
}

function statusClass(s) {
  return { completed: 'status--done', in_progress: 'status--progress', abandoned: 'status--abandoned' }[s] || '';
}

function slotStatusClass(s) {
  return { CLEAR: 'pill--clear', PARTIAL: 'pill--partial', UNKNOWN: 'pill--unknown', UNCERTAIN: 'pill--uncertain' }[s] || '';
}

function slotStatusKo(s) {
  return { CLEAR: '✅ 완료', PARTIAL: '🔶 부분', UNKNOWN: '❓ 미확인', UNCERTAIN: '❓ 미확인' }[s] || s;
}

function formatDate(isoStr) {
  if (!isoStr) return '';
  const d = new Date(isoStr);
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`;
}
</script>

<style scoped>
.interview-history {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 40px;
  position: relative;
}

.history-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.btn-back {
  padding: 8px 14px;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  font-size: 13px;
  color: #374151;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s;
}
.btn-back:hover { background: #f3f4f6; }

.history-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin: 0; }
.history-desc { font-size: 13px; color: #9ca3af; margin: 2px 0 0; }

.loading-msg, .empty-msg {
  text-align: center;
  padding: 48px 16px;
  color: #9ca3af;
}

.empty-icon { font-size: 40px; margin-bottom: 12px; }
.empty-sub { font-size: 12px; margin-top: 4px; }

/* 세션 목록 */
.session-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.session-card {
  border: 1.5px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  background: white;
}
.session-card:hover { border-color: #6366f1; background: #f5f3ff; }

.session-card__top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.session-company {
  display: flex;
  align-items: center;
  gap: 10px;
}

.company-icon { font-size: 22px; }
.company-name { font-size: 14px; font-weight: 600; color: #111; }
.company-position { font-size: 12px; color: #6b7280; margin-top: 2px; }

.session-status {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 99px;
}
.status--done { background: #dcfce7; color: #15803d; }
.status--progress { background: #dbeafe; color: #1d4ed8; }
.status--abandoned { background: #f3f4f6; color: #6b7280; }

.session-card__actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-delete-session {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  background: transparent;
  border: 1.5px solid #e5e7eb;
  border-radius: 6px;
  color: #9ca3af;
  font-size: 11px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  opacity: 0;
}

.session-card:hover .btn-delete-session { opacity: 1; }

.btn-delete-session:hover {
  background: #fee2e2;
  border-color: #f87171;
  color: #ef4444;
}

.session-card__bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.session-slots { display: flex; flex-wrap: wrap; gap: 4px; }

.slot-pill {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 99px;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.pill--clear { background: #dcfce7; color: #15803d; }
.pill--partial { background: #fef9c3; color: #92400e; }
.pill--unknown, .pill--uncertain { background: #f3f4f6; color: #6b7280; }

.session-date { font-size: 12px; color: #9ca3af; flex-shrink: 0; }

/* 상세 모달 */
.detail-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.detail-panel {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.detail-company { font-size: 18px; font-weight: 700; margin: 0 0 4px; color: #111; }
.detail-meta { font-size: 13px; color: #6b7280; margin: 0; }

.btn-close {
  background: none;
  border: none;
  font-size: 16px;
  color: #9ca3af;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.15s;
}
.btn-close:hover { background: #f3f4f6; color: #374151; }

.detail-body {
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-title {
  font-size: 14px;
  font-weight: 700;
  color: #374151;
  margin: 0 0 12px;
}

/* 피드백 */
.detail-feedback { }

.feedback-summary {
  font-size: 14px;
  color: #374151;
  line-height: 1.6;
  margin: 0 0 14px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.feedback-two-col { display: flex; gap: 16px; margin-bottom: 12px; }

.feedback-col { flex: 1; }

.feedback-col__title {
  display: block;
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 6px;
}
.feedback-col__title.strength { color: #15803d; }
.feedback-col__title.improve { color: #b45309; }

.feedback-list {
  margin: 0;
  padding-left: 16px;
  font-size: 13px;
  color: #374151;
  line-height: 1.7;
}

.feedback-recommendation {
  font-size: 13px;
  color: #374151;
  background: #fef9c3;
  border: 1px solid #fde047;
  border-radius: 8px;
  padding: 10px 14px;
  line-height: 1.6;
}

/* 역량별 결과 */
.slot-result-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}
.slot-result-row:last-child { border-bottom: none; }

.slot-topic-label { font-size: 14px; color: #374151; }

.slot-status-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 99px;
}
.slot-status-badge.pill--clear { background: #dcfce7; color: #15803d; }
.slot-status-badge.pill--partial { background: #fef9c3; color: #92400e; }
.slot-status-badge.pill--unknown,
.slot-status-badge.pill--uncertain { background: #f3f4f6; color: #6b7280; }

/* Q&A */
.detail-qa { }

.qa-item {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
}
.qa-item:last-child { border-bottom: none; margin-bottom: 0; }

.qa-q {
  font-size: 13px;
  font-weight: 600;
  color: #4f46e5;
  margin-bottom: 6px;
  line-height: 1.5;
}

.qa-a {
  font-size: 13px;
  color: #374151;
  line-height: 1.6;
  background: #f8fafc;
  padding: 10px 12px;
  border-radius: 8px;
  white-space: pre-wrap;
}
</style>
