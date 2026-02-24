<template>
  <div class="history-container">
    <header class="history-header">
      <button class="back-btn" @click="$emit('close')">&times;</button>
      <div class="badge">MY RECORDS</div>
      <h1 class="title">Personal Training Logs</h1>
      <p class="subtitle">{{ authStore.user?.user_nickname }} 엔지니어님의 훈련 기록입니다.</p>
    </header>

    <div class="practice-selector">
      <button 
        v-for="unit in units" 
        :key="unit.id" 
        class="unit-chip"
        :class="{ active: selectedUnitId === unit.id }"
        @click="selectUnit(unit)"
      >
        UNIT {{ padNumber(unit.unit_number) }}
      </button>
    </div>

    <div class="content-area">
      <div v-if="loading" class="loading">Fetching logs...</div>
      <div v-else-if="answers.length === 0" class="no-data">
        <div class="empty-state">
          <span>📭</span>
          <p>해당 유닛의 완료 기록이 없습니다.<br>훈련을 시작해 보세요!</p>
        </div>
      </div>
      <div v-else class="log-timeline">
        <!-- [2026-02-19 수정] 그룹화된 미션별 카드 렌더링 -->
        <div v-for="group in answers" :key="group.detail_id" class="log-entry" :class="{ 'is-expanded': group.isExpanded }">
          <div class="log-marker" :class="{ perfect: group.attempts[0]?.is_perfect }"></div>
          <div class="log-content">
            <div class="log-header" @click="group.isExpanded = !group.isExpanded" style="cursor: pointer;">
              <div class="log-title-area">
                <span class="log-title">{{ group.title }}</span>
                <span class="attempt-count">{{ group.attempts.length }}번의 시도</span>
              </div>
              <div class="log-header-right">
                <span class="log-score">{{ group.attempts[0]?.score }}pts</span>
                <span class="toggle-icon">▼</span>
              </div>
            </div>
            
            <transition name="collapse">
              <div v-show="group.isExpanded" class="log-body-wrapper">
                <!-- 시도 내역 리스트 (성장 히스토리) -->
                <div class="attempt-history">
                  <div v-for="(ans, idx) in group.attempts" :key="idx" class="attempt-item">
                    <div class="attempt-header" @click="ans.isDetailExpanded = !ans.isDetailExpanded">
                      <span class="attempt-indicator" :class="{ latest: idx === 0 }">
                        {{ idx === 0 ? 'LATEST' : `#${group.attempts.length - idx}` }}
                      </span>
                      <span class="attempt-date">{{ formatDate(ans.solved_date) }}</span>
                      <span class="attempt-score" :class="{ perfect: ans.is_perfect }">{{ ans.score }}점</span>
                      <span class="detail-toggle">{{ ans.isDetailExpanded ? '▲' : '▼' }}</span>
                    </div>
                    <transition name="fade">
                      <div v-show="ans.isDetailExpanded" class="attempt-detail">
                        <!-- [2026-02-19 추가] 평가 대시보드 UI -->
                        <div v-if="getEvaluation(ans)" class="evaluation-audit">
                          <header class="audit-header">
                            <div class="result-badge" :class="getScoreClass(getEvaluation(ans).totalScore)">
                              <span class="score-val">{{ getEvaluation(ans).totalScore }}</span>
                              <span class="score-unit">pts</span>
                            </div>
                            <div class="audit-summary">
                              <h4 class="summary-label">Evaluation Summary</h4>
                              <p class="summary-text">{{ getEvaluation(ans).summary }}</p>
                            </div>
                          </header>

                          <div class="audit-grid">
                            <div v-for="metric in getEvaluation(ans).metrics" :key="metric.key" class="metric-card">
                              <div class="metric-label">{{ metric.label }}</div>
                              <div class="metric-bar-container">
                                <div class="metric-bar" :style="{ width: metric.score + '%' }"></div>
                              </div>
                              <div class="metric-score">{{ metric.score }}%</div>
                              
                              <!-- Basis & Improvement (ML_EVAL Only) -->
                              <div v-if="getEvaluation(ans).type === 'ML_EVAL'" class="metric-details">
                                <div v-if="metric.basis" class="detail-item">
                                  <span class="detail-label">Basis:</span> {{ metric.basis }}
                                </div>
                                <div v-if="metric.improvement" class="detail-item improvement">
                                  <span class="detail-label">Next Step:</span> {{ metric.improvement }}
                                </div>
                              </div>
                            </div>
                          </div>

                          <!-- [2026-02-19 추가] Deep Dive Q&A (SYS_DESIGN Only) -->
                          <div v-if="getEvaluation(ans).type === 'SYS_DESIGN' && getEvaluation(ans).deepDive?.length" class="audit-deepdive">
                            <h5 class="deepdive-title">Deep Dive Analysis</h5>
                            <div class="deepdive-list">
                              <div v-for="(qa, qidx) in getEvaluation(ans).deepDive" :key="qidx" class="qa-item">
                                <div class="qa-question">
                                  <span class="qa-badge">Q</span>
                                  <span class="qa-category">[{{ qa.category }}]</span> {{ qa.question }}
                                </div>
                                <div class="qa-answer">
                                  <span class="qa-badge">A</span> {{ qa.answer }}
                                </div>
                              </div>
                            </div>
                          </div>
                          
                          <div v-if="getEvaluation(ans).feedback" class="audit-feedback">
                            <i class="feedback-icon">💡</i>
                            <p class="feedback-text">{{ getEvaluation(ans).feedback }}</p>
                          </div>
                        </div>

                        <!-- [2026-02-20] 버그헌트 전용 UI -->
                        <div v-if="isBugHuntData(ans.submitted_data)" class="bughunt-log">
                          <!-- 꼬리질문 면접 기록 -->
                          <div v-if="ans.submitted_data.followup_interactions?.length || ans.submitted_data.llm_evaluation" class="bughunt-interview">
                            <h5 class="bughunt-section-title">💬 꼬리질문 면접 & 총평</h5>

                            <!-- 면접관 종합 총평 (제일 위) -->
                            <div v-if="ans.submitted_data.llm_evaluation?.overall_feedback" class="final-summary">
                              <div class="summary-header">
                                <span class="summary-icon">🎯</span>
                                <span class="summary-title">면접관 종합 총평</span>
                              </div>
                              <div class="summary-content">
                                <p>{{ ans.submitted_data.llm_evaluation.overall_feedback }}</p>
                              </div>
                              <div class="summary-scores">
                                <div class="summary-score-item">
                                  <span class="label">사고력</span>
                                  <span class="value" :class="getScoreClass(ans.submitted_data.llm_evaluation.thinking_score)">
                                    {{ ans.submitted_data.llm_evaluation.thinking_score }}점
                                  </span>
                                </div>
                                <div class="summary-score-item">
                                  <span class="label">코드 위험도</span>
                                  <span class="value risk" :class="getRiskClass(ans.submitted_data.llm_evaluation.code_risk)">
                                    {{ ans.submitted_data.llm_evaluation.code_risk }}
                                  </span>
                                </div>
                                <div class="summary-score-item">
                                  <span class="label">사고 방향</span>
                                  <span class="value" :class="ans.submitted_data.llm_evaluation.thinking_pass ? 'safe' : 'danger'">
                                    {{ ans.submitted_data.llm_evaluation.thinking_pass ? '✓ 안전' : '⚠ 주의' }}
                                  </span>
                                </div>
                              </div>
                            </div>

                            <!-- Step별 면접 -->
                            <div v-for="interview in ans.submitted_data.followup_interactions" :key="interview.step" class="interview-card">
                              <div class="interview-header">
                                <span class="step-number">Step {{ interview.step }}</span>
                                <span class="interview-score" :class="getScoreClass(interview.score)">
                                  {{ interview.score }}점
                                </span>
                                <span class="understanding-level" :class="getLevelClass(interview.understanding_level)">
                                  {{ interview.understanding_level }}
                                </span>
                              </div>

                              <div v-if="interview.matched_concepts?.length" class="matched-concepts">
                                <div class="concepts-label">파악한 개념</div>
                                <div class="concept-tags">
                                  <span v-for="(concept, idx) in interview.matched_concepts" :key="idx" class="concept-tag">
                                    {{ concept }}
                                  </span>
                                </div>
                              </div>

                              <div v-if="interview.conversation_summary?.length" class="conversation">
                                <div class="conversation-label">면접 대화</div>
                                <div v-for="(msg, idx) in interview.conversation_summary" :key="idx" class="conversation-msg" :class="msg.role">
                                  <div class="msg-role">{{ msg.role === 'interviewer' ? 'AI' : 'ME' }}</div>
                                  <div class="msg-content">{{ msg.content }}</div>
                                </div>
                              </div>

                              <div v-if="interview.weak_point" class="weak-point">
                                <div class="weak-label">보완 필요 사항</div>
                                <p>{{ interview.weak_point }}</p>
                              </div>
                            </div>
                          </div>
                        </div>

                        <!-- 기존 제출 데이터 (코드/설명 등) - 버그헌트가 아닌 경우 -->
                        <div v-else-if="isStructuredData(ans.submitted_data)" class="structured-log">
                          <template v-for="(val, key) in ans.submitted_data" :key="key">
                            <div v-if="shouldRenderSection(key)" class="log-section">
                              <div class="log-section-header">
                                <span class="section-icon">{{ getSectionIcon(key) }}</span>
                                <span class="section-title">{{ key }}</span>
                              </div>
                              <div class="section-content" :class="{ 'code-mode': key.includes('코드') || key.includes('Implementation') || key.includes('Training Log') || key.includes('설계') || isMermaidCode(val) }">
                                <template v-if="isMermaidCode(val)">
                                  <MermaidRenderer :code="val" :id="`mermaid-${group.detail_id}-${idx}-${key}`" />
                                </template>
                                <pre v-else-if="key.includes('코드') || key.includes('Implementation') || key.includes('Training Log') || key.includes('설계')">{{ val }}</pre>
                                <p v-else>{{ val }}</p>
                              </div>
                            </div>
                          </template>
                        </div>
                        <div v-else-if="isMermaidCode(ans.submitted_data)" class="mermaid-log-wrapper">
                          <MermaidRenderer :code="ans.submitted_data" :id="`mermaid-${group.detail_id}-${idx}-full`" />
                        </div>
                        <pre v-else class="log-code">{{ formatAnswer(ans.submitted_data) }}</pre>
                      </div>
                    </transition>
                  </div>
                </div>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineEmits } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import MermaidRenderer from '@/components/MermaidRenderer.vue';

const emit = defineEmits(['close']);
const authStore = useAuthStore();
const units = ref([]);
const selectedUnitId = ref('');
const answers = ref([]);
const loading = ref(false);

const isMermaidCode = (text) => {
  if (!text || typeof text !== 'string') return false;
  const trimmed = text.trim();
  const mermaidKeywords = [
    'graph', 'flowchart', 'sequenceDiagram', 'gantt', 
    'classDiagram', 'stateDiagram', 'erDiagram', 'pie', 'journey'
  ];
  return mermaidKeywords.some(keyword => trimmed.startsWith(keyword));
};

const padNumber = (num) => {
  return String(num).padStart(2, '0');
};

const fetchUnits = async () => {
  try {
    const res = await axios.get('/api/core/practices/');
    units.value = res.data;
    if (units.value.length > 0) {
      selectUnit(units.value[0]);
    }
  } catch (err) {
    console.error('Failed to fetch units:', err);
  }
};

const selectUnit = async (unit) => {
  selectedUnitId.value = unit.id;
  loading.value = true;
  try {
    const res = await axios.get(`/api/core/management/user-answers/${unit.id}/`);
    // [2026-02-19 수정] 그룹 및 각 시도별 확장 상태 초기화
    answers.value = res.data.answers.map(group => ({
      ...group,
      isExpanded: false,
      attempts: group.attempts.map(ans => ({
        ...ans,
        isDetailExpanded: false
      }))
    }));
  } catch (err) {
    console.error('Failed to fetch user records:', err);
  } finally {
    loading.value = false;
  }
};

const formatAnswer = (data) => {
  if (!data) return 'N/A';
  if (typeof data === 'string') return data;
  return JSON.stringify(data, null, 2);
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString();
};

const isStructuredData = (data) => {
  if (!data || typeof data !== 'object') return false;
  return Object.keys(data).length > 0;
};

// [2026-02-19 추가] 평가 데이터 정규화 및 추출
const getEvaluation = (ans) => {
  const data = ans.submitted_data;
  if (!data || typeof data !== 'object') return null;

  // Unit 1 형식: data.evaluation
  if (data.evaluation && typeof data.evaluation === 'object') {
    const ev = data.evaluation;
    const metrics = [];
    if (ev.dimensions) {
      Object.entries(ev.dimensions).forEach(([k, v]) => {
        metrics.push({
          key: k,
          label: v.name || translateKey(k),
          score: v.percentage || v.score || 0,
          basis: v.comment || v.basis || "",
          improvement: v.improvement || ""
        });
      });
    }
    return {
      type: 'ML_EVAL',
      totalScore: ev.total_score_100 || ans.score,
      summary: ev.summary || ev.one_line_review || "상세 평가 요약이 없습니다.",
      metrics: metrics,
      feedback: ev.senior_advice || ev.python_feedback || ""
    };
  }

  // Unit 3 형식: data.evaluation_result
  if (data.evaluation_result && typeof data.evaluation_result === 'object') {
    const ev = data.evaluation_result;
    const metrics = [];
    if (ev.pillarScores) {
      Object.entries(ev.pillarScores).forEach(([k, v]) => {
        metrics.push({
          key: k,
          label: translateKey(k),
          score: v || 0
        });
      });
    }
    return {
      type: 'SYS_DESIGN',
      totalScore: ev.totalScore || ans.score,
      summary: ev.summary || "아키텍처 설계 평가 결과입니다.",
      metrics: metrics,
      deepDive: data.deep_dive_answers || []
    };
  }

  // [2026-02-24 Fix] 구형식 호환: evaluation 래퍼 없이 metrics/summary가 최상위에 있는 경우
  // (CoduckWars의 이전 completeMission()이 저장한 형식)
  if (data.track_type === 'pseudocode' && data.metrics && typeof data.metrics === 'object') {
    const metrics = [];
    Object.entries(data.metrics).forEach(([k, v]) => {
      if (v && typeof v === 'object') {
        metrics.push({
          key: k,
          label: v.name || translateKey(k),
          score: v.percentage || v.score || 0,
          basis: v.comment || "",
          improvement: ""
        });
      }
    });
    return {
      type: 'ML_EVAL',
      totalScore: ans.score,
      summary: data.summary || "상세 평가 요약이 없습니다.",
      metrics: metrics,
      feedback: ""
    };
  }

  return null;
};

const getScoreClass = (score) => {
  if (score >= 90) return 'perfect';
  if (score >= 70) return 'good';
  if (score >= 50) return 'average';
  return 'low';
};

const translateKey = (key) => {
  const dict = {
    // Unit 1
    'design': '설계 논리',
    'consistency': '격리 원칙',
    'implementation': '구체성',
    'edge_case': '예외 처리',
    'edgeCase': '예외 처리',
    'abstraction': '추상화 레벨',
    // Unit 3
    'security': '보안성',
    'reliability': '신뢰성',
    'sustainability': '지속가능성',
    'costOptimization': '비용 최적화',
    'operationalExce': '운영 우수성',
    'performanceOpti': '성능 최적화'
  };
  return dict[key] || key;
};

// [2026-02-19 추가] 이미 대시보드에 표시된 기술적 데이터 키 필터링
const shouldRenderSection = (key) => {
  const blackList = [
    'evaluation',           // Unit 1 평가 객체
    'evaluation_result',    // Unit 3 평가 객체
    'deep_dive_answers',    // Unit 3 질답 (이미 대시보드에 포함)
    'user_explanation',      // Unit 3 설계 설명 (질답 1번과 중복)
    'problem_id',           // 내부 ID
    'missionName',          // [2026-02-24 추가] Coduck Wars 미션명 (헤더에서 표시됨)
    'title',                // [2026-02-24 추가] 공통 미션/문제 제목
    'components',           // 머메이드용 로우 데이터
    'connections',          // 머메이드용 로우 데이터

    // [2026-02-20 추가] 버그헌트 에이전트 학습용 데이터 (마이 히스토리에서 숨김)
    'mission_id',           // 미션 내부 ID
    'step_codes',           // 단계별 코드 로그
    'user_inputs',          // 사용자 입력 로그 (에이전트 학습용)
    'followup_interactions', // 꼬리질문 및 답변 (에이전트 학습용)
    'behavior_log',         // 행동 패턴 로그
    'weakness_indicators',  // 약점 분석 지표
    'track_type',           // 트랙 타입 메타데이터
    'raw_data'              // 원본 데이터 보존 (에이전트 학습용)
  ];
  return !blackList.includes(key);
};

const getSectionIcon = (key) => {
  if (key.includes('Training Log') || key.includes('설계')) return '📝';
  if (key.includes('사고') || key.includes('Architecture')) return '🧠';
  if (key.includes('AI') || key.includes('Evaluation')) return '🤖';
  if (key.includes('코드') || key.includes('Implementation')) return '💻';
  return '📝';
};

// [2026-02-20 추가] 버그헌트 데이터 식별
const isBugHuntData = (data) => {
  if (!data || typeof data !== 'object') return false;
  return data.track_type === 'bughunt' && (data.user_inputs || data.llm_evaluation);
};

// [2026-02-20 추가] Step별 피드백 가져오기
const getStepFeedback = (data, step) => {
  if (!data?.llm_evaluation?.step_feedbacks) return null;
  const feedback = data.llm_evaluation.step_feedbacks.find(f => f.step === step);
  return feedback?.feedback || null;
};

// [2026-02-20 추가] 위험도에 따른 CSS 클래스
const getRiskClass = (risk) => {
  if (risk >= 70) return 'high';
  if (risk >= 40) return 'medium';
  return 'low';
};

// [2026-02-20 추가] 이해 수준에 따른 CSS 클래스
const getLevelClass = (level) => {
  if (level === 'Deep') return 'deep';
  if (level === 'Conceptual') return 'conceptual';
  if (level === 'Surface') return 'surface';
  return 'none';
};

onMounted(fetchUnits);
</script>

<style scoped src="./MyHistoryView.css"></style>
