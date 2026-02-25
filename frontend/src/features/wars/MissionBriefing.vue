<template>
  <div class="mission-briefing-container">
    <header class="page-header">
      <h1 class="neon-text">TEAM BATTLE: MISSION SELECT</h1>
      <p class="tagline">시나리오를 선택하여 아키텍처 서바이벌에 도전하세요</p>
    </header>

    <main class="briefing-layout">
      <!-- 좌측: 시나리오 카드 그리드 -->
      <!-- [수정일: 2026-02-23] JD 입력 제거, 시나리오 카드 선택 방식으로 전환 -->
      <section class="glass-panel scenario-select-panel">
        <div class="panel-header">
          <span class="icon">🎯</span>
          <h2>SCENARIO SELECT</h2>
        </div>

        <div class="scenario-grid">
          <div
            v-for="scenario in presetScenarios"
            :key="scenario.id"
            class="scenario-card"
            :class="{ selected: selectedScenario?.id === scenario.id }"
            @click="selectScenario(scenario)"
          >
            <div class="card-icon">{{ scenario.icon }}</div>
            <h3 class="card-title">{{ scenario.title }}</h3>
            <p class="card-desc">{{ scenario.shortDesc }}</p>
            <div class="card-tags">
              <span class="tag" v-for="tag in scenario.tags" :key="tag">{{ tag }}</span>
            </div>
            <div class="difficulty-bar">
              <span class="diff-label">난이도</span>
              <div class="diff-dots">
                <span v-for="i in 5" :key="i" class="dot" :class="{ filled: i <= scenario.difficulty }"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- [P1] 난이도별 권장 플레이어 수 안내 -->
        <div class="difficulty-guide">
          <span class="dg-item easy">⭐1~2 쉬움</span>
          <span class="dg-item medium">⭐⭐⭐ 권장 3인</span>
          <span class="dg-item hard">⭐⭐⭐⭐⭐ 고급</span>
        </div>

        <!-- 시나리오 랜덤 생성 버튼 -->
        <button @click="generateRandomScenario" :disabled="isGenerating" class="btn-random">
          <span v-if="!isGenerating">🎲 랜덤 시나리오 생성 (AI)</span>
          <span v-else class="loader"></span>
        </button>
      </section>

      <!-- 우측: 미션 정보 (결과) -->
      <section class="glass-panel mission-card-panel" :class="{ 'is-active': missionData }">
        <div class="panel-header">
          <span class="icon">🚀</span>
          <h2>MISSION INFORMATION</h2>
        </div>
        <div class="panel-content">
          <div v-if="!missionData" class="empty-state">
            <div class="ai-orb"></div>
            <p>시나리오를 선택하세요...</p>
          </div>

          <div v-else class="mission-details">
            <div class="mission-header">
              <h3 class="mission-title">{{ missionData.title }}</h3>
              <div class="mission-difficulty">Difficulty: {{ missionData.difficultyLabel }}</div>
            </div>

            <div class="mission-info-item">
              <h4>Background Context</h4>
              <p>{{ missionData.context }}</p>
            </div>

            <div class="mission-info-item highlight">
              <h4>Initial Quest</h4>
              <p>{{ missionData.initialQuest }}</p>
            </div>

            <div class="mission-info-item">
              <h4>Interviewer Persona</h4>
              <p><strong>{{ missionData.interviewer.name }}:</strong> {{ missionData.interviewer.persona }}</p>
            </div>

            <div class="mission-info-item chaos">
              <h4>⚡ Chaos Event (게임 중 발동)</h4>
              <p>{{ missionData.chaosEvent }}</p>
            </div>
          </div>
        </div>
      </section>
    </main>

    <footer class="page-footer">
      <button
        :disabled="!missionData"
        class="btn-secondary btn-large"
        @click="enterGame"
      >
        ENTER SIMULATION
      </button>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { useGameStore } from '@/stores/game';

// [수정일: 2026-02-23] JD 입력 제거, 시나리오 카드 선택 방식으로 전환
const router = useRouter();
const gameStore = useGameStore();
const isGenerating = ref(false);
const missionData = ref(null);
const selectedScenario = ref(null);

// 프리셋 시나리오 4종
const presetScenarios = ref([
  {
    id: 'traffic_surge',
    icon: '🔥',
    title: '트래픽 폭주 대응',
    shortDesc: '프로모션 성공으로 트래픽이 10배 급증! 서버가 버티지 못하고 있다.',
    tags: ['로드밸런싱', '오토스케일링', 'CDN'],
    difficulty: 3,
    scenario: {
      mission_title: '긴급 장애 대응: 트래픽 폭주',
      context: '갑작스러운 프로모션 성공으로 아시아 리전 API 서버의 CPU 사용률이 95%를 상회하며 평균 응답 시간이 5초를 넘겼습니다. 고객 불만이 폭주하고 있으며, 이대로라면 30분 내 서비스가 완전히 다운됩니다.',
      initial_quest: '현재 Single-Server 아키텍처를 고가용성 구조로 즉시 전환하세요. L7 로드밸런서, 오토스케일링, CDN을 활용한 긴급 대응 아키텍처를 설계하세요.',
      interviewer: { name: '박책임', persona: '자원 낭비를 극도로 혐오하며, 비용 근거 없는 답변은 신뢰하지 않는 냉철한 실무자' },
      chaos_event: '메인 DB의 커넥션 풀이 가득 차서 새로운 요청을 처리하지 못하는 상황이 추가 발생합니다.'
    }
  },
  {
    id: 'db_deadlock',
    icon: '⚡',
    title: 'DB 데드락 복구',
    shortDesc: '결제 시스템에서 데드락 발생! 주문이 멈추고 금전 손실이 커지고 있다.',
    tags: ['DB 최적화', '트랜잭션', '캐시'],
    difficulty: 4,
    scenario: {
      mission_title: '결제 시스템 데드락 위기',
      context: '블랙프라이데이 세일 중 결제 트랜잭션에서 데드락이 빈번하게 발생하고 있습니다. 주문 처리율이 80% 감소했으며, 분당 수백만 원의 매출 손실이 발생 중입니다. DBA팀은 이미 퇴근했습니다.',
      initial_quest: '데드락을 해소할 수 있는 DB 아키텍처를 설계하세요. 읽기/쓰기 분리, 캐시 레이어, 인덱스 최적화를 고려하세요.',
      interviewer: { name: '김수석', persona: '데이터 정합성에 집착하며, 트랜잭션 격리 수준에 대한 깊은 이해를 요구하는 DB 전문가' },
      chaos_event: 'Read Replica 지연 시간이 30초를 넘기며 데이터 정합성 문제가 추가 발생합니다.'
    }
  },
  {
    id: 'security_breach',
    icon: '🛡️',
    title: '보안 침해 대응',
    shortDesc: 'API에서 대량의 비정상 요청 감지! 개인정보 유출 가능성.',
    tags: ['WAF', '제로트러스트', '암호화'],
    difficulty: 5,
    scenario: {
      mission_title: '보안 침해: API 공격 대응',
      context: '새벽 3시, 모니터링 시스템에서 API Gateway로 분당 10만 건 이상의 비정상 요청이 감지되었습니다. SQL Injection과 SSRF 공격이 동시에 진행 중이며, 일부 사용자 데이터가 이미 노출되었을 가능성이 있습니다.',
      initial_quest: 'WAF, API Rate Limiting, 네트워크 세그먼테이션을 포함한 보안 강화 아키텍처를 즉시 설계하세요.',
      interviewer: { name: '이보안관', persona: '제로 트러스트 원칙을 신봉하며, 모든 설계에 대해 "그게 뚫리면?" 질문을 멈추지 않는 보안 전문가' },
      chaos_event: '공격자가 내부 VPN을 통해 백엔드 서버에 직접 접근을 시도합니다.'
    }
  },
  {
    id: 'global_expansion',
    icon: '🌐',
    title: '글로벌 확장 설계',
    shortDesc: '서비스를 해외에 론칭해야 한다! 글로벌 아키텍처를 설계하라.',
    tags: ['멀티리전', 'CDN', 'DNS'],
    difficulty: 4,
    scenario: {
      mission_title: '글로벌 서비스 확장 프로젝트',
      context: '국내에서 성공한 서비스를 미국, 유럽, 동남아시아에 동시 론칭해야 합니다. 각 리전별 200ms 이하의 응답 속도를 보장해야 하며, GDPR 등 지역별 데이터 규정도 준수해야 합니다. 론칭까지 2주 남았습니다.',
      initial_quest: '멀티 리전 아키텍처를 설계하세요. CDN, Global Load Balancer, 데이터 복제 전략을 포함해야 합니다.',
      interviewer: { name: '최아키텍트', persona: '확장성과 비용의 밸런스를 중시하며, "그게 10배 커지면 어떡합니까?"를 입버릇처럼 묻는 시니어 아키텍트' },
      chaos_event: '유럽 리전의 데이터센터에서 네트워크 파티션이 발생하여 일부 유저가 접속 불가능해집니다.'
    }
  }
]);

// 시나리오 카드 선택
const selectScenario = (scenario) => {
  selectedScenario.value = scenario;
  const s = scenario.scenario;
  missionData.value = {
    title: s.mission_title,
    context: s.context,
    initialQuest: s.initial_quest,
    interviewer: s.interviewer,
    chaosEvent: s.chaos_event,
    difficultyLabel: ['', 'Easy', 'Normal', 'Hard', 'Expert', 'Nightmare'][scenario.difficulty]
  };

  // 스토어에 시나리오 저장 (id 포함)
  // [수정일: 2026-02-23] 소켓 방 입장을 위해 id 필드를 scenario.id로 설정
  gameStore.setWarsMission({ ...s, id: scenario.id, scenario_id: scenario.id });
};

// AI 랜덤 시나리오 생성
const generateRandomScenario = async () => {
  isGenerating.value = true;
  try {
    const response = await axios.post('/api/core/wars/start/', {
      scenario_type: 'random'
    });

    if (response.data.status === 'success') {
      const s = response.data.scenario;
      selectedScenario.value = { id: 'random', icon: '🎲', title: s.mission_title };
      missionData.value = {
        title: s.mission_title,
        context: s.context,
        initialQuest: s.initial_quest,
        interviewer: s.interviewer || { name: 'AI 면접관', persona: '실무진 면접관' },
        chaosEvent: s.chaos_event || '예측 불가능한 장애가 발생합니다.',
        difficultyLabel: 'Randomized'
      };
      // [수정일: 2026-02-23] 랜덤 시나리오의 경우 고유 ID 생성이 필요할 수 있으나, 
      // 현재는 테스트 편의를 위해 'random_mission'으로 고정하거나 타임스탬프를 활용할 수 있습니다.
      // 여기서는 'random'을 id로 사용하여 동일 시나리오 선택 시 같은 방에 입장을 유도합니다.
      gameStore.setWarsMission({ ...s, id: 'random' });
    }
  } catch (error) {
    console.error('랜덤 시나리오 생성 실패:', error);
    alert('시나리오 생성 중 오류가 발생했습니다. 프리셋 시나리오를 선택해주세요.');
  } finally {
    isGenerating.value = false;
  }
};

// [버그수정] 로비에서 역할 선택 후 배틀룸으로 이동 (기존에 로비 건너뛰던 것 수정)
const enterGame = () => {
  if (missionData.value) {
    console.log('[MissionBriefing] 로비로 이동, 미션:', missionData.value.title);
    router.push('/practice/coduck-wars/lobby');
  }
};
</script>

<style scoped>
/* [수정일: 2026-02-23] 시나리오 카드 선택 방식 UI */
.mission-briefing-container {
  min-height: 100vh;
  background: radial-gradient(circle at top right, #1e293b, #030712);
  color: #f8fafc;
  padding: 4rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 3rem;
  font-family: 'Inter', sans-serif;
}

.page-header { text-align: center; }

.neon-text {
  font-size: 3rem;
  font-weight: 900;
  letter-spacing: -1px;
  background: linear-gradient(to right, #38bdf8, #818cf8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 0 10px rgba(56, 189, 248, 0.3));
}

.tagline { color: #94a3b8; margin-top: 0.5rem; }

.briefing-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  flex: 1;
}

.glass-panel {
  background: rgba(30, 41, 59, 0.4);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1.5rem;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  transition: all 0.4s ease;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.panel-header h2 {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: 1px;
  color: #38bdf8;
}

/* 시나리오 카드 그리드 */
.scenario-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.scenario-card {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid #334155;
  border-radius: 1rem;
  padding: 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.scenario-card:hover {
  border-color: #38bdf8;
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(56, 189, 248, 0.15);
}

.scenario-card.selected {
  border-color: #38bdf8;
  background: rgba(56, 189, 248, 0.1);
  box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);
}

.scenario-card.selected::before {
  content: '✓';
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: #38bdf8;
  color: #030712;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 900;
}

.card-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.card-title {
  font-size: 1rem;
  font-weight: 800;
  margin-bottom: 0.4rem;
  color: #f1f5f9;
}

.card-desc {
  font-size: 0.75rem;
  color: #94a3b8;
  line-height: 1.5;
  margin-bottom: 0.6rem;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  margin-bottom: 0.5rem;
}

.tag {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
}

.difficulty-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.diff-label {
  font-size: 0.65rem;
  color: #64748b;
}

.diff-dots {
  display: flex;
  gap: 3px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #334155;
}

.dot.filled {
  background: #f59e0b;
}

/* [P1] 난이도 가이드 */
.difficulty-guide {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}
.dg-item {
  font-size: 0.7rem;
  padding: 3px 10px;
  border-radius: 20px;
  font-weight: 700;
}
.dg-item.easy   { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }
.dg-item.medium { background: rgba(56,189,248,0.15);  color: #38bdf8; border: 1px solid rgba(56,189,248,0.3); }
.dg-item.hard   { background: rgba(239,68,68,0.15);   color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }

/* 랜덤 생성 버튼 */
.btn-random {
  padding: 0.8rem;
  border-radius: 0.75rem;
  background: rgba(139, 92, 246, 0.15);
  border: 1px solid rgba(139, 92, 246, 0.3);
  color: #a78bfa;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-random:hover:not(:disabled) {
  background: rgba(139, 92, 246, 0.25);
  transform: translateY(-1px);
}

.btn-random:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 우측 미션 정보 패널 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #64748b;
}

.ai-orb {
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, #38bdf8, transparent);
  border-radius: 50%;
  margin-bottom: 2rem;
  animation: pulse 3s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.8; }
  100% { transform: scale(1); opacity: 0.5; }
}

.mission-details {
  animation: fadeIn 0.8s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.mission-title {
  font-size: 1.75rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  line-height: 1.3;
}

.mission-difficulty {
  font-size: 0.8rem;
  color: #f59e0b;
  font-weight: 700;
  margin-bottom: 1.5rem;
}

.mission-info-item {
  margin-bottom: 1.5rem;
}

.mission-info-item h4 {
  color: #38bdf8;
  font-size: 0.9rem;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.mission-info-item p {
  color: #cbd5e1;
  line-height: 1.7;
}

.highlight {
  background: rgba(56, 189, 248, 0.05);
  padding: 1rem;
  border-left: 4px solid #38bdf8;
  border-radius: 0 0.5rem 0.5rem 0;
}

.chaos {
  background: rgba(239, 68, 68, 0.05);
  padding: 1rem;
  border-left: 4px solid #ef4444;
  border-radius: 0 0.5rem 0.5rem 0;
}

.page-footer {
  display: flex;
  justify-content: center;
  padding-bottom: 2rem;
}

.btn-secondary {
  padding: 1.5rem 4rem;
  border-radius: 3rem;
  background: #f8fafc;
  color: #030712;
  font-weight: 800;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:disabled {
  background: #334155;
  color: #64748b;
  cursor: not-allowed;
}

.btn-secondary:hover:not(:disabled) {
  box-shadow: 0 0 30px rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.loader {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
