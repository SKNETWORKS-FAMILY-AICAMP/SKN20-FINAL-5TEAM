<template>
  <div v-if="result" class="master-agent-result" :class="result.grade">
    <!-- 헤더: 총점 및 등급 -->
    <div class="result-header">
      <div class="score-display" :style="{ color: getGradeColor(result.grade) }">
        {{ getGradeEmoji(result.grade) }} {{ result.score }}점
      </div>
      <div class="grade-badge" :class="result.grade">
        {{ getGradeText(result.grade) }}
      </div>
    </div>

    <!-- 1차 진단 결과 (마스터 에이전트) -->
    <div v-if="masterEval?.initialAssessment" class="initial-assessment">
      <h4>🎯 1차 진단 (Master Agent)</h4>
      <div class="assessment-grid">
        <div class="assessment-item">
          <span class="label">Stateless 준수</span>
          <span class="value" :class="masterEval.initialAssessment.statelessCompliance">
            {{ formatLevel(masterEval.initialAssessment.statelessCompliance) }}
          </span>
        </div>
        <div class="assessment-item">
          <span class="label">Decoupled 준수</span>
          <span class="value" :class="masterEval.initialAssessment.decoupledCompliance">
            {{ formatLevel(masterEval.initialAssessment.decoupledCompliance) }}
          </span>
        </div>
        <div class="assessment-item">
          <span class="label">전체 성숙도</span>
          <span class="value" :class="masterEval.initialAssessment.overallMaturity">
            {{ formatMaturity(masterEval.initialAssessment.overallMaturity) }}
          </span>
        </div>
      </div>
      <p class="assessment-summary">{{ masterEval.initialAssessment.summary }}</p>
    </div>

    <!-- 선택된 하위 에이전트 표시 -->
    <div v-if="masterEval?.selectedAgents" class="selected-agents">
      <h4>🔍 상세 분석 영역</h4>
      <div class="agent-chips">
        <div
          v-for="agent in masterEval.selectedAgents"
          :key="agent.agentId"
          class="agent-chip"
          :class="{ active: expandedAgent === agent.agentId }"
          @click="toggleAgent(agent.agentId)"
        >
          <span class="agent-emoji">{{ getAgentEmoji(agent.agentId) }}</span>
          <span class="agent-name">{{ getAgentName(agent.agentId) }}</span>
          <span class="priority-badge">P{{ agent.priority }}</span>
        </div>
      </div>
    </div>

    <!-- 하위 에이전트 상세 결과 -->
    <div v-if="result.subAgentResults" class="sub-agent-results">
      <div
        v-for="subResult in result.subAgentResults"
        :key="subResult.agentId"
        class="sub-agent-card"
        :class="[getScoreClass(subResult.pillarScore), { expanded: expandedAgent === subResult.agentId }]"
      >
        <div class="sub-agent-header" @click="toggleAgent(subResult.agentId)">
          <div class="sub-agent-title">
            <span class="emoji">{{ subResult.emoji }}</span>
            <span class="name">{{ subResult.agentName }}</span>
          </div>
          <div class="sub-agent-score">{{ subResult.pillarScore }}점</div>
          <div class="expand-icon">{{ expandedAgent === subResult.agentId ? '▼' : '▶' }}</div>
        </div>

        <!-- 펼쳐진 상세 내용 -->
        <transition name="slide">
          <div v-if="expandedAgent === subResult.agentId" class="sub-agent-detail">
            <p class="sub-summary">{{ subResult.summary }}</p>

            <!-- 4대 평가 기준 -->
            <div class="eval-criteria">
              <div
                v-for="(evalItem, evalKey) in subResult.evaluation"
                :key="evalKey"
                class="eval-item"
              >
                <div class="eval-header">
                  <span class="eval-icon">{{ getEvalIcon(evalKey) }}</span>
                  <span class="eval-label">{{ getEvalLabel(evalKey) }}</span>
                  <span class="eval-score" :class="getScoreClass(evalItem.score)">
                    {{ evalItem.score }}점
                  </span>
                </div>
                <p class="eval-analysis">{{ evalItem.analysis }}</p>

                <!-- 하이라이트/concerns -->
                <div v-if="evalItem.highlights?.length" class="tags">
                  <span v-for="h in evalItem.highlights" :key="h" class="tag positive">{{ h }}</span>
                </div>
                <div v-if="evalItem.concerns?.length" class="tags">
                  <span v-for="c in evalItem.concerns" :key="c" class="tag negative">{{ c }}</span>
                </div>
              </div>
            </div>

            <!-- 심층 질문 -->
            <div v-if="subResult.deepDiveQuestions?.length" class="deep-dive-questions">
              <h6>💬 심층 질문</h6>
              <ul>
                <li v-for="q in subResult.deepDiveQuestions" :key="q">{{ q }}</li>
              </ul>
            </div>

            <!-- 권장 사항 -->
            <div v-if="subResult.recommendations" class="recommendations">
              <div v-if="subResult.recommendations.shortTerm?.length" class="rec-group">
                <h6>⚡ 단기 개선</h6>
                <ul>
                  <li v-for="r in subResult.recommendations.shortTerm" :key="r">{{ r }}</li>
                </ul>
              </div>
              <div v-if="subResult.recommendations.longTerm?.length" class="rec-group">
                <h6>🎯 장기 과제</h6>
                <ul>
                  <li v-for="r in subResult.recommendations.longTerm" :key="r">{{ r }}</li>
                </ul>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <!-- 최종 리포트 (4대 기준) -->
    <div v-if="masterEval?.finalReport" class="final-report">
      <h4>📊 최종 리포트 (4대 기준)</h4>

      <!-- 1. 종합 적합성 -->
      <div class="report-section">
        <div class="report-header">
          <span class="report-icon">🏛️</span>
          <span class="report-title">종합 적합성</span>
          <span class="report-score" :class="getScoreClass(masterEval.finalReport.overallSuitability?.cloudNativeScore)">
            {{ masterEval.finalReport.overallSuitability?.cloudNativeScore }}점
          </span>
        </div>
        <div class="level-indicators">
          <span class="level-item">
            Stateless:
            <em :class="masterEval.finalReport.overallSuitability?.statelessLevel">
              {{ formatLevel(masterEval.finalReport.overallSuitability?.statelessLevel) }}
            </em>
          </span>
          <span class="level-item">
            Decoupled:
            <em :class="masterEval.finalReport.overallSuitability?.decoupledLevel">
              {{ formatLevel(masterEval.finalReport.overallSuitability?.decoupledLevel) }}
            </em>
          </span>
        </div>
        <p>{{ masterEval.finalReport.overallSuitability?.analysis }}</p>
      </div>

      <!-- 2. 통합 가시성 -->
      <div class="report-section">
        <div class="report-header">
          <span class="report-icon">👁️</span>
          <span class="report-title">통합 가시성</span>
          <span class="report-score" :class="getScoreClass(masterEval.finalReport.unifiedObservability?.score)">
            {{ masterEval.finalReport.unifiedObservability?.score }}점
          </span>
        </div>
        <p>{{ masterEval.finalReport.unifiedObservability?.analysis }}</p>
      </div>

      <!-- 3. 핵심 강점 및 전략적 필요성 -->
      <div class="report-section">
        <div class="report-header">
          <span class="report-icon">💪</span>
          <span class="report-title">핵심 강점 및 전략적 필요성</span>
        </div>
        <div v-if="masterEval.finalReport.strategicStrengths?.topStrengths" class="strengths-list">
          <span v-for="s in masterEval.finalReport.strategicStrengths.topStrengths" :key="s" class="strength-tag">
            {{ s }}
          </span>
        </div>
        <div v-if="masterEval.finalReport.strategicStrengths?.priorityImprovement" class="priority-improvement">
          <strong>우선 개선 영역:</strong>
          {{ masterEval.finalReport.strategicStrengths.priorityImprovement.pillar }}
          <span class="reason">({{ masterEval.finalReport.strategicStrengths.priorityImprovement.reason }})</span>
        </div>
        <p>{{ masterEval.finalReport.strategicStrengths?.analysis }}</p>
      </div>

      <!-- 4. 복합 리스크 -->
      <div class="report-section">
        <div class="report-header">
          <span class="report-icon">⚠️</span>
          <span class="report-title">복합 리스크 (Cross-pillar)</span>
        </div>
        <div v-if="masterEval.finalReport.crossPillarRisks?.tradeoffs?.length" class="tradeoffs">
          <div v-for="(t, i) in masterEval.finalReport.crossPillarRisks.tradeoffs" :key="i" class="tradeoff-item">
            <span class="action">{{ t.action }}</span>
            <span class="arrow">→</span>
            <span class="side-effect">{{ t.sideEffect }}</span>
          </div>
        </div>
        <div v-if="masterEval.finalReport.crossPillarRisks?.technicalDebt?.length" class="tech-debt">
          <strong>기술적 부채:</strong>
          <span v-for="d in masterEval.finalReport.crossPillarRisks.technicalDebt" :key="d" class="debt-tag">
            {{ d }}
          </span>
        </div>
        <p>{{ masterEval.finalReport.crossPillarRisks?.analysis }}</p>
      </div>
    </div>

    <!-- 액션 플랜 -->
    <div v-if="masterEval?.actionPlan" class="action-plan">
      <h4>🚀 액션 플랜</h4>
      <div class="action-timeline">
        <div v-if="masterEval.actionPlan.immediate?.length" class="action-group immediate">
          <h5>즉시 실행</h5>
          <ul>
            <li v-for="a in masterEval.actionPlan.immediate" :key="a">{{ a }}</li>
          </ul>
        </div>
        <div v-if="masterEval.actionPlan.shortTerm?.length" class="action-group short-term">
          <h5>단기 (1-2주)</h5>
          <ul>
            <li v-for="a in masterEval.actionPlan.shortTerm" :key="a">{{ a }}</li>
          </ul>
        </div>
        <div v-if="masterEval.actionPlan.longTerm?.length" class="action-group long-term">
          <h5>장기</h5>
          <ul>
            <li v-for="a in masterEval.actionPlan.longTerm" :key="a">{{ a }}</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 종합 요약 -->
    <div class="final-summary">
      <p>{{ result.summary }}</p>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';

export default {
  name: 'MasterAgentEvaluationResult',
  props: {
    result: {
      type: Object,
      default: null
    }
  },
  setup(props) {
    const expandedAgent = ref(null);

    const masterEval = computed(() => props.result?.masterAgentEvaluation);

    const toggleAgent = (agentId) => {
      expandedAgent.value = expandedAgent.value === agentId ? null : agentId;
    };

    const agentMeta = {
      operational: { emoji: '🤖', name: 'Operational Excellence' },
      security: { emoji: '🔐', name: 'Security & Compliance' },
      reliability: { emoji: '🏗️', name: 'Reliability' },
      performance: { emoji: '⚡', name: 'Performance' },
      costSustainability: { emoji: '💰🌱', name: 'Cost & Sustainability' }
    };

    return {
      expandedAgent,
      masterEval,
      toggleAgent,
      getAgentEmoji: (id) => agentMeta[id]?.emoji || '📌',
      getAgentName: (id) => agentMeta[id]?.name || id
    };
  },
  methods: {
    getGradeColor(grade) {
      const colors = { excellent: '#00ff9d', good: '#64b5f6', 'needs-improvement': '#ffc107', poor: '#ff4785' };
      return colors[grade] || '#e0e0e0';
    },
    getGradeEmoji(grade) {
      const emojis = { excellent: '🏆', good: '👍', 'needs-improvement': '💡', poor: '📝' };
      return emojis[grade] || '❓';
    },
    getGradeText(grade) {
      const texts = { excellent: '우수', good: '양호', 'needs-improvement': '개선 필요', poor: '미흡' };
      return texts[grade] || '평가 중';
    },
    getScoreClass(score) {
      if (score >= 80) return 'excellent';
      if (score >= 60) return 'good';
      if (score >= 40) return 'needs-improvement';
      return 'poor';
    },
    formatLevel(level) {
      const labels = { high: '높음', medium: '보통', low: '낮음' };
      return labels[level] || level;
    },
    formatMaturity(maturity) {
      const labels = { advanced: '고급', intermediate: '중급', beginner: '초급' };
      return labels[maturity] || maturity;
    },
    getEvalIcon(key) {
      const icons = { suitability: '🎯', dataCollection: '📊', strengths: '✅', difficulties: '⚠️' };
      return icons[key] || '📌';
    },
    getEvalLabel(key) {
      const labels = { suitability: '설계 적합성', dataCollection: '가시성 확보', strengths: '강점', difficulties: '리스크' };
      return labels[key] || key;
    }
  }
};
</script>

<style scoped>
.master-agent-result {
  background: rgba(0, 0, 0, 0.5);
  border-radius: 16px;
  padding: 24px;
  border: 2px solid;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.master-agent-result.excellent { border-color: #00ff9d; }
.master-agent-result.good { border-color: #64b5f6; }
.master-agent-result.needs-improvement { border-color: #ffc107; }
.master-agent-result.poor { border-color: #ff4785; }

/* Header */
.result-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 24px;
}

.score-display {
  font-family: 'Orbitron', sans-serif;
  font-size: 2.5em;
  text-shadow: 0 0 20px currentColor;
}

.grade-badge {
  padding: 6px 16px;
  border-radius: 20px;
  font-weight: 600;
}

.grade-badge.excellent { background: rgba(0, 255, 157, 0.2); color: #00ff9d; }
.grade-badge.good { background: rgba(100, 181, 246, 0.2); color: #64b5f6; }
.grade-badge.needs-improvement { background: rgba(255, 193, 7, 0.2); color: #ffc107; }
.grade-badge.poor { background: rgba(255, 71, 133, 0.2); color: #ff4785; }

/* Initial Assessment */
.initial-assessment {
  background: rgba(100, 181, 246, 0.1);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.initial-assessment h4 {
  color: #64b5f6;
  margin: 0 0 12px 0;
}

.assessment-grid {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.assessment-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.assessment-item .label {
  font-size: 0.8em;
  color: #78909c;
}

.assessment-item .value {
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85em;
}

.assessment-item .value.high { background: rgba(0, 255, 157, 0.2); color: #00ff9d; }
.assessment-item .value.medium { background: rgba(255, 193, 7, 0.2); color: #ffc107; }
.assessment-item .value.low { background: rgba(255, 71, 133, 0.2); color: #ff4785; }
.assessment-item .value.advanced { background: rgba(0, 255, 157, 0.2); color: #00ff9d; }
.assessment-item .value.intermediate { background: rgba(100, 181, 246, 0.2); color: #64b5f6; }
.assessment-item .value.beginner { background: rgba(255, 193, 7, 0.2); color: #ffc107; }

.assessment-summary {
  color: #b0bec5;
  font-size: 0.9em;
  margin: 0;
  line-height: 1.5;
}

/* Selected Agents */
.selected-agents {
  margin-bottom: 20px;
}

.selected-agents h4 {
  color: #64b5f6;
  margin: 0 0 12px 0;
}

.agent-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.agent-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.agent-chip:hover, .agent-chip.active {
  background: rgba(100, 181, 246, 0.2);
  border-color: #64b5f6;
}

.agent-emoji {
  font-size: 1.2em;
}

.agent-name {
  color: #e0e0e0;
  font-size: 0.9em;
}

.priority-badge {
  background: rgba(0, 255, 157, 0.3);
  color: #00ff9d;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.75em;
  font-weight: 600;
}

/* Sub Agent Results */
.sub-agent-results {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.sub-agent-card {
  background: rgba(0, 0, 0, 0.4);
  border-radius: 12px;
  border-left: 4px solid;
  overflow: hidden;
}

.sub-agent-card.excellent { border-left-color: #00ff9d; }
.sub-agent-card.good { border-left-color: #64b5f6; }
.sub-agent-card.needs-improvement { border-left-color: #ffc107; }
.sub-agent-card.poor { border-left-color: #ff4785; }

.sub-agent-header {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.sub-agent-header:hover {
  background: rgba(255, 255, 255, 0.05);
}

.sub-agent-title {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.sub-agent-title .emoji {
  font-size: 1.3em;
}

.sub-agent-title .name {
  font-weight: 600;
  color: #e0e0e0;
}

.sub-agent-score {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.2em;
  margin-right: 12px;
}

.sub-agent-card.excellent .sub-agent-score { color: #00ff9d; }
.sub-agent-card.good .sub-agent-score { color: #64b5f6; }
.sub-agent-card.needs-improvement .sub-agent-score { color: #ffc107; }
.sub-agent-card.poor .sub-agent-score { color: #ff4785; }

.expand-icon {
  color: #78909c;
  font-size: 0.8em;
}

.sub-agent-detail {
  padding: 0 16px 16px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.sub-summary {
  color: #90a4ae;
  font-size: 0.9em;
  margin: 12px 0;
  line-height: 1.5;
}

/* Eval Criteria */
.eval-criteria {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.eval-item {
  background: rgba(255, 255, 255, 0.03);
  padding: 12px;
  border-radius: 8px;
}

.eval-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.eval-icon {
  font-size: 1em;
}

.eval-label {
  flex: 1;
  font-weight: 500;
  color: #b0bec5;
  font-size: 0.85em;
}

.eval-score {
  font-family: 'Orbitron', sans-serif;
  font-weight: 600;
  font-size: 0.85em;
}

.eval-score.excellent { color: #00ff9d; }
.eval-score.good { color: #64b5f6; }
.eval-score.needs-improvement { color: #ffc107; }
.eval-score.poor { color: #ff4785; }

.eval-analysis {
  color: #78909c;
  font-size: 0.8em;
  margin: 0;
  line-height: 1.4;
}

.tags {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 0.75em;
}

.tag.positive { background: rgba(0, 255, 157, 0.15); color: #00ff9d; }
.tag.negative { background: rgba(255, 71, 133, 0.15); color: #ff4785; }

/* Deep Dive Questions */
.deep-dive-questions {
  margin-top: 16px;
  padding: 12px;
  background: rgba(171, 71, 188, 0.1);
  border-radius: 8px;
}

.deep-dive-questions h6 {
  color: #ab47bc;
  margin: 0 0 8px 0;
  font-size: 0.85em;
}

.deep-dive-questions ul {
  margin: 0;
  padding-left: 16px;
}

.deep-dive-questions li {
  color: #b0bec5;
  font-size: 0.8em;
  margin-bottom: 4px;
}

/* Recommendations */
.recommendations {
  margin-top: 16px;
  display: flex;
  gap: 16px;
}

.rec-group {
  flex: 1;
}

.rec-group h6 {
  color: #64b5f6;
  margin: 0 0 8px 0;
  font-size: 0.8em;
}

.rec-group ul {
  margin: 0;
  padding-left: 16px;
}

.rec-group li {
  color: #90a4ae;
  font-size: 0.8em;
  margin-bottom: 4px;
}

/* Slide Animation */
.slide-enter-active, .slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from, .slide-leave-to {
  opacity: 0;
  max-height: 0;
}

/* Final Report */
.final-report {
  margin-bottom: 24px;
}

.final-report h4 {
  color: #64b5f6;
  margin: 0 0 16px 0;
}

.report-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
}

.report-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.report-icon {
  font-size: 1.3em;
}

.report-title {
  flex: 1;
  font-weight: 600;
  color: #e0e0e0;
}

.report-score {
  font-family: 'Orbitron', sans-serif;
  font-weight: 600;
}

.report-score.excellent { color: #00ff9d; }
.report-score.good { color: #64b5f6; }
.report-score.needs-improvement { color: #ffc107; }
.report-score.poor { color: #ff4785; }

.level-indicators {
  display: flex;
  gap: 16px;
  margin-bottom: 10px;
}

.level-item {
  color: #78909c;
  font-size: 0.85em;
}

.level-item em {
  font-style: normal;
  font-weight: 600;
  margin-left: 4px;
}

.level-item em.high { color: #00ff9d; }
.level-item em.medium { color: #ffc107; }
.level-item em.low { color: #ff4785; }

.report-section p {
  color: #b0bec5;
  font-size: 0.9em;
  margin: 0;
  line-height: 1.5;
}

.strengths-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.strength-tag {
  background: rgba(0, 255, 157, 0.15);
  color: #00ff9d;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8em;
}

.priority-improvement {
  background: rgba(255, 193, 7, 0.1);
  padding: 10px 12px;
  border-radius: 8px;
  margin-bottom: 10px;
  font-size: 0.9em;
  color: #ffc107;
}

.priority-improvement .reason {
  color: #78909c;
  font-size: 0.9em;
}

.tradeoffs {
  margin-bottom: 10px;
}

.tradeoff-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.tradeoff-item .action {
  color: #64b5f6;
  font-size: 0.85em;
}

.tradeoff-item .arrow {
  color: #78909c;
}

.tradeoff-item .side-effect {
  color: #ff4785;
  font-size: 0.85em;
}

.tech-debt {
  margin-bottom: 10px;
  font-size: 0.85em;
  color: #78909c;
}

.debt-tag {
  background: rgba(255, 71, 133, 0.15);
  color: #ff4785;
  padding: 3px 10px;
  border-radius: 10px;
  margin-left: 6px;
  font-size: 0.85em;
}

/* Action Plan */
.action-plan {
  margin-bottom: 24px;
}

.action-plan h4 {
  color: #64b5f6;
  margin: 0 0 16px 0;
}

.action-timeline {
  display: flex;
  gap: 16px;
}

.action-group {
  flex: 1;
  padding: 14px;
  border-radius: 12px;
}

.action-group.immediate {
  background: rgba(255, 71, 133, 0.1);
  border-left: 3px solid #ff4785;
}

.action-group.short-term {
  background: rgba(255, 193, 7, 0.1);
  border-left: 3px solid #ffc107;
}

.action-group.long-term {
  background: rgba(100, 181, 246, 0.1);
  border-left: 3px solid #64b5f6;
}

.action-group h5 {
  margin: 0 0 10px 0;
  font-size: 0.9em;
}

.action-group.immediate h5 { color: #ff4785; }
.action-group.short-term h5 { color: #ffc107; }
.action-group.long-term h5 { color: #64b5f6; }

.action-group ul {
  margin: 0;
  padding-left: 16px;
}

.action-group li {
  color: #b0bec5;
  font-size: 0.85em;
  margin-bottom: 4px;
}

/* Final Summary */
.final-summary {
  background: linear-gradient(135deg, rgba(100, 181, 246, 0.1), rgba(171, 71, 188, 0.1));
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.final-summary p {
  color: #e0e0e0;
  font-size: 1em;
  margin: 0;
  line-height: 1.6;
}

/* Responsive */
@media (max-width: 768px) {
  .assessment-grid {
    flex-direction: column;
  }

  .action-timeline {
    flex-direction: column;
  }

  .recommendations {
    flex-direction: column;
  }
}
</style>
