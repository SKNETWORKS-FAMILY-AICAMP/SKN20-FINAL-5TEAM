<template>
  <div class="planner-history">
    <div class="history-header">
      <h3 class="history-title">분석 기록</h3>
      <p class="history-desc">총 {{ records.length }}개의 분석 기록</p>
    </div>

    <div v-if="!records.length" class="empty-msg">
      <p>저장된 분석 기록이 없습니다.</p>
      <p class="empty-sub">분석 완료 후 "분석 결과 저장" 버튼을 눌러주세요.</p>
    </div>

    <div v-else class="record-list">
      <div
        v-for="record in sortedRecords"
        :key="record.id"
        class="record-card"
        @click="openDetail(record)"
      >
        <div class="record-card__top">
          <div>
            <div class="card-company">{{ record.company_name || '기업명 없음' }}</div>
            <div class="card-position">{{ record.position || '-' }}</div>
          </div>
          <div class="card-actions">
            <div class="readiness-badge" :class="scoreClass(record.readiness_score)">
              {{ Math.round((record.readiness_score || 0) * 100) }}%
            </div>
            <button class="btn-delete" @click.stop="remove(record.id)" title="삭제">✕</button>
          </div>
        </div>
        <div class="record-card__bottom">
          <div class="card-tags">
            <span v-if="record.agent_report" class="tag">SWOT</span>
            <span v-if="record.recommendations?.length" class="tag">추천공고</span>
            <span v-if="record.portfolio_review" class="tag">포폴리뷰</span>
            <span v-if="record.company_analysis" class="tag">기업분석</span>
          </div>
          <div class="card-date">{{ formatDate(record.saved_at) }}</div>
        </div>
      </div>
    </div>

    <!-- 상세 모달 -->
    <div v-if="selected" class="detail-overlay" @click.self="selected = null">
      <div class="detail-panel">
        <div class="detail-header">
          <div>
            <h3 class="detail-company">{{ selected.company_name || '기업명 없음' }}</h3>
            <p class="detail-meta">{{ selected.position || '' }} · {{ formatDate(selected.saved_at) }}</p>
          </div>
          <button class="btn-close" @click="selected = null">✕</button>
        </div>

        <div class="detail-body">
          <!-- 준비도 점수 -->
          <div v-if="selected.analysis_result" class="detail-section">
            <h4 class="section-title">스킬 매칭 분석</h4>
            <div class="score-grid">
              <div class="score-item">
                <span class="score-label">준비도</span>
                <span class="score-val" :class="scoreClass(selected.analysis_result.readiness_score)">
                  {{ ((selected.analysis_result.readiness_score || 0) * 100).toFixed(1) }}%
                </span>
              </div>
              <div class="score-item">
                <span class="score-label">스킬 갭</span>
                <span class="score-val">{{ ((selected.analysis_result.skill_gap_score || 0) * 100).toFixed(1) }}%</span>
              </div>
              <div class="score-item">
                <span class="score-label">경력 적합도</span>
                <span class="score-val">{{ ((selected.analysis_result.experience_fit || 0) * 100).toFixed(1) }}%</span>
              </div>
            </div>

            <div v-if="selected.analysis_result.matched_skills?.length" class="skill-section">
              <strong class="skill-heading matched">매칭 스킬</strong>
              <div class="skill-tags">
                <span v-for="s in selected.analysis_result.matched_skills" :key="s.required" class="skill-tag matched">
                  {{ s.user_skill || s.required }}
                </span>
              </div>
            </div>
            <div v-if="selected.analysis_result.missing_skills?.length" class="skill-section">
              <strong class="skill-heading missing">부족 스킬</strong>
              <div class="skill-tags">
                <span v-for="s in selected.analysis_result.missing_skills" :key="s.required" class="skill-tag missing">
                  {{ s.required }}
                </span>
              </div>
            </div>
          </div>

          <!-- SWOT 분석 -->
          <div v-if="selected.agent_report?.swot" class="detail-section">
            <h4 class="section-title">SWOT 분석</h4>
            <div class="swot-grid">
              <div v-for="key in ['strengths', 'weaknesses', 'opportunities', 'threats']" :key="key" class="swot-box" :class="'swot-' + key">
                <strong class="swot-label">{{ swotLabel(key) }}</strong>
                <ul class="swot-list">
                  <li v-for="(item, i) in selected.agent_report.swot[key]" :key="i">
                    {{ item.point || item }}
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- 추천 공고 -->
          <div v-if="selected.recommendations?.length" class="detail-section">
            <h4 class="section-title">추천 채용공고 ({{ selected.recommendations.length }}개)</h4>
            <div v-for="(rec, i) in selected.recommendations" :key="i" class="rec-item">
              <div class="rec-row">
                <div>
                  <div class="rec-title">{{ rec.title }}</div>
                  <div class="rec-company-name">{{ rec.company_name }}</div>
                </div>
                <div class="rec-score" :class="scoreClass((rec.llm_score || rec.match_rate * 100) / 100)">
                  {{ rec.llm_score != null ? rec.llm_score : Math.round(rec.match_rate * 100) }}%
                </div>
              </div>
              <div v-if="rec.reason" class="rec-reason">{{ rec.reason }}</div>
              <a v-if="rec.url" :href="rec.url" target="_blank" rel="noopener" class="rec-link">공고 보기 →</a>
            </div>
          </div>

          <!-- 포트폴리오 리뷰 -->
          <div v-if="selected.portfolio_review" class="detail-section">
            <h4 class="section-title">포트폴리오 리뷰</h4>
            <div v-if="selected.portfolio_review.strengths?.length">
              <strong class="sub-label">강점</strong>
              <ul class="review-list"><li v-for="(s, i) in selected.portfolio_review.strengths" :key="i">{{ s }}</li></ul>
            </div>
            <div v-if="selected.portfolio_review.improvements?.length">
              <strong class="sub-label">개선점</strong>
              <div v-for="(item, i) in selected.portfolio_review.improvements" :key="i" class="improvement-item">
                <div class="improvement-target">{{ item.target || item }}</div>
                <div v-if="item.suggestion" class="improvement-suggestion">{{ item.suggestion }}</div>
              </div>
            </div>
            <div v-if="selected.portfolio_review.priority_actions?.length">
              <strong class="sub-label">우선 조치</strong>
              <ol class="review-list"><li v-for="(a, i) in selected.portfolio_review.priority_actions" :key="i">{{ a }}</li></ol>
            </div>
          </div>

          <!-- 기업 분석 -->
          <div v-if="selected.company_analysis" class="detail-section">
            <h4 class="section-title">기업 분석</h4>
            <div v-if="selected.company_analysis.overview?.description" class="company-desc">
              {{ selected.company_analysis.overview.description }}
            </div>
            <div v-if="selected.company_analysis.recommendation" class="company-rec">
              {{ selected.company_analysis.recommendation }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const STORAGE_KEY = 'job_planner_history';

export default {
  name: 'JobPlannerHistory',
  data() {
    return {
      records: [],
      selected: null,
    };
  },
  computed: {
    sortedRecords() {
      return [...this.records].sort((a, b) => new Date(b.saved_at) - new Date(a.saved_at));
    },
  },
  mounted() {
    this.loadRecords();
  },
  methods: {
    loadRecords() {
      try {
        this.records = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
      } catch {
        this.records = [];
      }
    },
    openDetail(record) {
      this.selected = record;
    },
    remove(id) {
      this.records = this.records.filter(r => r.id !== id);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.records));
      if (this.selected?.id === id) this.selected = null;
    },
    scoreClass(score) {
      if (score >= 0.7) return 'score--high';
      if (score >= 0.5) return 'score--mid';
      return 'score--low';
    },
    swotLabel(key) {
      return { strengths: 'Strengths', weaknesses: 'Weaknesses', opportunities: 'Opportunities', threats: 'Threats' }[key];
    },
    formatDate(isoStr) {
      if (!isoStr) return '';
      const d = new Date(isoStr);
      return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`;
    },
  },
};
</script>

<style scoped>
.planner-history { padding: 8px 0; }

.history-header { margin-bottom: 20px; }
.history-title { font-size: 20px; font-weight: 700; color: #e2e8f0; margin: 0 0 4px; }
.history-desc { font-size: 13px; color: #94a3b8; margin: 0; }

.empty-msg { text-align: center; padding: 40px 16px; color: #94a3b8; }
.empty-sub { font-size: 12px; margin-top: 4px; color: #64748b; }

/* 카드 그리드 */
.record-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.record-card {
  border: 1.5px solid rgba(59, 130, 246, 0.2);
  border-radius: 12px;
  padding: 14px 16px;
  cursor: pointer;
  background: rgba(30, 41, 59, 0.5);
  transition: border-color 0.15s, background 0.15s;
}
.record-card:hover {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(30, 41, 59, 0.8);
}

.record-card__top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.card-company { font-size: 14px; font-weight: 600; color: #e2e8f0; }
.card-position { font-size: 12px; color: #94a3b8; margin-top: 2px; }

.card-actions { display: flex; align-items: center; gap: 8px; }

.readiness-badge {
  font-size: 13px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 99px;
}
.score--high { background: rgba(34, 197, 94, 0.2); color: #4ade80; }
.score--mid { background: rgba(234, 179, 8, 0.2); color: #facc15; }
.score--low { background: rgba(239, 68, 68, 0.2); color: #f87171; }

.btn-delete {
  width: 24px; height: 24px;
  background: transparent;
  border: 1.5px solid rgba(148, 163, 184, 0.3);
  border-radius: 6px;
  color: #94a3b8;
  font-size: 11px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.15s;
}
.record-card:hover .btn-delete { opacity: 1; }
.btn-delete:hover { background: rgba(239, 68, 68, 0.2); border-color: #f87171; color: #f87171; }

.record-card__bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.card-tags { display: flex; flex-wrap: wrap; gap: 4px; }
.tag {
  font-size: 10px;
  padding: 2px 7px;
  border-radius: 99px;
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
}

.card-date { font-size: 11px; color: #64748b; flex-shrink: 0; }

/* 상세 모달 */
.detail-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 16px;
}

.detail-panel {
  background: #1e293b;
  border-radius: 16px;
  width: 100%;
  max-width: 680px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px 24px 16px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.15);
  flex-shrink: 0;
}

.detail-company { font-size: 18px; font-weight: 700; margin: 0 0 4px; color: #e2e8f0; }
.detail-meta { font-size: 13px; color: #94a3b8; margin: 0; }

.btn-close {
  background: none;
  border: none;
  font-size: 16px;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
}
.btn-close:hover { background: rgba(148, 163, 184, 0.15); color: #e2e8f0; }

.detail-body {
  overflow-y: auto;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-section {
  background: rgba(15, 23, 42, 0.6);
  border-radius: 12px;
  padding: 16px 18px;
  border: 1px solid rgba(148, 163, 184, 0.1);
}

.section-title {
  font-size: 14px;
  font-weight: 700;
  color: #60a5fa;
  margin: 0 0 12px;
  padding-left: 10px;
  border-left: 3px solid #3b82f6;
}

/* 점수 */
.score-grid { display: flex; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.score-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 16px;
  background: rgba(30, 41, 59, 0.8);
  border-radius: 8px;
  flex: 1;
  min-width: 80px;
}
.score-label { font-size: 11px; color: #94a3b8; margin-bottom: 4px; }
.score-val { font-size: 18px; font-weight: 700; }

/* 스킬 */
.skill-section { margin-top: 8px; }
.skill-heading { display: block; font-size: 12px; margin-bottom: 6px; }
.skill-heading.matched { color: #4ade80; }
.skill-heading.missing { color: #f87171; }
.skill-tags { display: flex; flex-wrap: wrap; gap: 4px; }
.skill-tag {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 99px;
}
.skill-tag.matched { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
.skill-tag.missing { background: rgba(239, 68, 68, 0.15); color: #f87171; }

/* SWOT */
.swot-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.swot-box { border-radius: 8px; padding: 10px 12px; }
.swot-strengths { background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.2); }
.swot-weaknesses { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); }
.swot-opportunities { background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); }
.swot-threats { background: rgba(234, 179, 8, 0.1); border: 1px solid rgba(234, 179, 8, 0.2); }
.swot-label { display: block; font-size: 12px; font-weight: 700; color: #cbd5e1; margin-bottom: 6px; }
.swot-list { margin: 0; padding-left: 16px; font-size: 12px; color: #cbd5e1; line-height: 1.6; }

/* 추천 공고 */
.rec-item {
  padding: 10px 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}
.rec-item:last-child { border-bottom: none; }
.rec-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.rec-title { font-size: 13px; font-weight: 600; color: #e2e8f0; }
.rec-company-name { font-size: 12px; color: #94a3b8; }
.rec-score { font-size: 14px; font-weight: 700; flex-shrink: 0; }
.rec-reason { font-size: 12px; color: #94a3b8; margin-top: 4px; line-height: 1.5; }
.rec-link {
  display: inline-block;
  font-size: 12px;
  color: #60a5fa;
  margin-top: 4px;
  text-decoration: none;
}
.rec-link:hover { text-decoration: underline; }

/* 포폴 리뷰 */
.sub-label { display: block; font-size: 12px; color: #94a3b8; margin: 8px 0 4px; }
.review-list { margin: 0; padding-left: 16px; font-size: 12px; color: #cbd5e1; line-height: 1.6; }
.improvement-item { margin-bottom: 6px; }
.improvement-target { font-size: 12px; color: #e2e8f0; font-weight: 500; }
.improvement-suggestion { font-size: 12px; color: #94a3b8; margin-top: 2px; }

/* 기업 분석 */
.company-desc { font-size: 13px; color: #cbd5e1; line-height: 1.6; margin-bottom: 8px; }
.company-rec {
  font-size: 12px;
  color: #e2e8f0;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
  padding: 10px 12px;
  line-height: 1.5;
}
</style>
