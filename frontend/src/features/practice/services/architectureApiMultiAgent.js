/**
 * Architecture Multi-Agent Evaluation Service
 * 6개 전문 에이전트가 병렬로 평가 후 결과 종합
 *
 * 6 Pillars (Google Cloud Well-Architected Framework 기반):
 * 1. Security & Compliance (보안, 개인정보 보호 및 컴플라이언스)
 * 2. Cost Optimization (비용 최적화)
 * 3. Reliability (신뢰성/안정성)
 * 4. Operational Excellence (운영 우수성)
 * 5. Sustainability (지속 가능성)
 * 6. Performance Optimization (성능 최적화)
 */

import architectureProblems from '@/data/architecture.json';

const getApiKey = () => import.meta.env.VITE_OPENAI_API_KEY;

/**
 * OpenAI API 호출 기본 함수
 */
async function callOpenAI(prompt, options = {}) {
  const {
    model = 'gpt-4o-mini',
    maxTokens = 1000,
    temperature = 0.4,
    systemMessage = null
  } = options;

  const messages = [];
  if (systemMessage) {
    messages.push({ role: 'system', content: systemMessage });
  }
  messages.push({ role: 'user', content: prompt });

  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getApiKey()}`
      },
      body: JSON.stringify({
        model,
        messages,
        max_tokens: maxTokens,
        temperature
      })
    });

    if (!response.ok) throw new Error(`API Error: ${response.status}`);
    const data = await response.json();
    return data.choices[0].message.content.trim();
  } catch (error) {
    console.error('OpenAI Call Error:', error);
    throw error;
  }
}

// ============================================================================
// 6개 전문 에이전트 정의
// ============================================================================

/**
 * Agent 1: Security & Compliance (보안, 개인정보 보호 및 컴플라이언스)
 */
const AGENT_SECURITY = {
  name: 'Security & Compliance Agent',
  emoji: '🔐',
  systemRole: `너는 **Google Cloud 보안 및 컴플라이언스 전문 아키텍트**야.
'Security, Privacy, and Compliance' 가이드를 바탕으로 시스템 아키텍처를 진단해.`,

  evaluationFramework: `평가 영역:
1. **보안 파운데이션:** 리소스 계층 구조, 조직 정책, 랜딩 존 설계
2. **ID 및 액세스 관리(IAM):** ID 연동, 최소 권한 원칙, 서비스 계정 관리
3. **네트워크 보안:** VPC 경계 보안, 마이크로 세그멘테이션, 외부 위협 방어
4. **데이터 보호:** 암호화(KMS/HSM), 데이터 분류, 유출 방지(DLP)
5. **개인정보 보호(Privacy):** 데이터 최소화, 익명화, 거버넌스 및 주권 보장
6. **컴플라이언스:** 규제 요구사항 매핑, 제어 항목 자동 검증`,

  evaluationCriteria: `평가 기준:
1. **설계 적합성:** 공유 책임 모델(Shared Responsibility)과 보안 설계(Security by Design) 원칙 적합성
2. **가시성 확보:** 보안 로그(Audit Logs), 액세스 투명성, VPC 흐름 로그 활성화 여부
3. **강점 및 필요성:** 심층 방어(Defense in Depth) 요소, 규제 준수 우선 영역
4. **리스크:** 운영 복잡성, 성능 저하, 설정 오류(Misconfiguration) 가능성`
};

/**
 * Agent 2: Cost Optimization (비용 최적화)
 */
const AGENT_COST = {
  name: 'Cost Optimization Agent',
  emoji: '💰',
  systemRole: `너는 **Google Cloud FinOps 전문가**이자 **비용 관리 아키텍트**야.
'Cost Optimization Pillar' 가이드를 바탕으로 클라우드 소비 패턴을 분석해.`,

  evaluationFramework: `평가 영역:
1. **비용 인식 및 책임(FinOps):** 팀별 비용 할당, 라벨링(Tagging) 전략 및 비용 문화
2. **클라우드 소비 최적화:** 적정 크기 조정(Right-sizing), 유휴 리소스 제거, 자동 확장 활용
3. **구매 모델 전략:** 약정 할인(CUD), 선점형 VM(Spot VM) 등 최적의 요금제 선택
4. **데이터 기반 의사결정:** 대시보드 활용, 예산 알림(Budgets & Alerts), 이상 비용 탐지
5. **관리형 서비스 활용:** 서버리스(Serverless), SaaS 전환을 통한 운영 비용(OpEx) 절감`,

  evaluationCriteria: `평가 기준:
1. **설계 적합성:** 가변 비용 모델 적합성 (고정형 vs 탄력적 인프라)
2. **가시성 확보:** 라벨(Label) 및 프로젝트 구조, Cloud Billing 보고서 활용
3. **강점 및 필요성:** 비용 효율적 운영 부분, ROI 향상을 위한 최적화 기술
4. **리스크:** 비용 절감 시 성능 저하, 가용성 리스크, 비용 책임 소재 불분명`
};

/**
 * Agent 3: Reliability (신뢰성/안정성)
 */
const AGENT_RELIABILITY = {
  name: 'Reliability Agent',
  emoji: '🏗️',
  systemRole: `너는 **Google Cloud 사이트 신뢰성 엔지니어(SRE)**이자 **클라우드 아키텍트**야.
'Reliability Pillar' 가이드를 바탕으로 워크로드의 장애 견고성을 진단해.`,

  evaluationFramework: `평가 영역:
1. **신뢰성 목표 설정:** SLI(지표)와 SLO(목표) 정의 및 에러 버짓(Error Budget) 관리
2. **복구 중심 설계:** 중복성(Redundancy), 장애 조치(Failover), 재해 복구(DR) 계획
3. **가시성 및 모니터링:** 시스템 상태의 실시간 파악 및 자동 알림 설정
4. **변경 관리 및 배포:** 카나리 배포, 롤백 전략 등 안정적인 변경 프로세스
5. **장애 대응 및 학습:** 자동화된 복구 프로세스 및 무비난 사후 검토(Blameless Postmortem)`,

  evaluationCriteria: `평가 기준:
1. **설계 적합성:** 단일 장애점(SPOF) 제거, 고가용성(HA) 및 확장성 원칙, 적절한 SLO 설정
2. **가시성 확보:** SLI 데이터 수집, 분산 트레이싱 및 대시보드 구성
3. **강점 및 필요성:** 멀티 리전 구성, 자동 복구 스크립트, BCP 도입 필요 도구
4. **리스크:** 연쇄 장애(Cascading Failure) 위험, RTO/RPO 달성 제약 사항`
};

/**
 * Agent 4: Operational Excellence (운영 우수성)
 */
const AGENT_OPERATIONAL = {
  name: 'Operational Excellence Agent',
  emoji: '🤖',
  systemRole: `너는 **Google Cloud Well-Architected 프레임워크 전문 솔루션 아키텍트**이자 **운영 우수성 평가 전문가**야.
운영 우수성 가이드라인을 기반으로 클라우드 워크로드를 분석해.`,

  evaluationFramework: `평가 영역 (4가지 운영 준비 영역 포괄: Workforce, Processes, Tooling, Governance):
1. **CloudOps를 통한 운영 준비:** SLO 정의, 모니터링, 용량 계획 확인
2. **인시던트 및 문제 관리:** 대응 절차, 중앙 집중화된 관리, 사후 검토(PIR) 프로세스
3. **클라우드 리소스 관리 및 최적화:** 적정 크기 조정, 자동 확장, 비용 추적
4. **변경 자동화 및 관리:** IaC(코드형 인프라), CI/CD 파이프라인, 자동화된 테스트
5. **지속적인 개선 및 혁신:** 학습 문화, 회고, 피드백 루프`,

  evaluationCriteria: `평가 기준:
1. **원칙별 적합성:** Google Cloud 권장 모범 사례 충실도
2. **가시성 확보:** SLO/SLI가 SMART하게 정의, 통합 관측성(Observability) 도구 사용
3. **강점 및 필요성:** 잘 설계된 부분, 즉시 개선 필요 핵심 영역
4. **리스크:** 자동화 부족, 비난하는 문화(Blame culture), 기술적 부채로 인한 장애 요인`
};

/**
 * Agent 5: Sustainability (지속 가능성)
 */
const AGENT_SUSTAINABILITY = {
  name: 'Sustainability Agent',
  emoji: '🌱',
  systemRole: `너는 **Google Cloud 지속 가능성 아키텍트**이자 **환경 영향 평가 전문가**야.
'Sustainability Pillar' 가이드를 바탕으로 에너지 효율성과 탄소 발자국 최적화를 진단해.`,

  evaluationFramework: `평가 영역:
1. **환경 영향 측정:** Carbon Footprint 보고서 및 Google Cloud 콘솔을 통한 탄소 배출량 모니터링
2. **저탄소 지역(Region) 선택:** 탄소 집약도가 낮은 리전 선택 및 워크로드 배치
3. **탄소 인식 워크로드 설계:** 서버리스(Serverless), 관리형 서비스 활용 및 유휴 리소스 최소화
4. **운영 패턴 최적화:** 탄소 배출이 적은 시간대에 배치(Batch) 작업 수행
5. **데이터 및 스토리지 효율화:** 데이터 중복 제거, 수명주기 정책을 통한 스토리지 에너지 소비 절감`,

  evaluationCriteria: `평가 기준:
1. **설계 적합성:** 지속 가능한 설계(Sustainable by Design) 원칙, 탄소 효율적 리전, 공유 자원 효율성
2. **가시성 확보:** Google Cloud Carbon Footprint로 Scope 2/3 배출량 추적, 지속 가능성 KPI 측정
3. **강점 및 필요성:** 환경 영향 감소 설계 요소, 탄소 인식 스케줄링 도입 필요성
4. **리스크:** 저탄소 리전 이전 시 지연 시간(Latency), 비용적 제약, 측정 기술적 어려움`
};

/**
 * Agent 6: Performance Optimization (성능 최적화)
 */
const AGENT_PERFORMANCE = {
  name: 'Performance Optimization Agent',
  emoji: '⚡',
  systemRole: `너는 **Google Cloud 성능 엔지니어링 전문가**야.
'Performance Optimization Pillar' 가이드를 바탕으로 처리량(Throughput)과 지연 시간(Latency)을 진단해.`,

  evaluationFramework: `평가 영역:
1. **요구사항 정의:** 레이어별 세부 성능 요구사항(Latency, Throughput) 및 측정 기준 수립
2. **성능을 고려한 설계:** 워크로드 특성에 맞는 컴퓨팅, 스토리지, 네트워크, 데이터베이스 선택
3. **모니터링 및 분석:** 실시간 대시보드, 병목 구간 식별, 프로파일링 도구 활용
4. **지속적인 최적화:** 자동 확장(Autoscaling), 코드 효율화, 정기적인 성능 테스트`,

  evaluationCriteria: `평가 기준:
1. **설계 적합성:** 성능 요구사항에 맞는 서비스 선택, 성능-비용 트레이드오프 관리
2. **가시성 확보:** CPU/메모리 외 사용자 경험 지표(응답 시간, HEART 프레임워크), 네트워크 분석 데이터
3. **강점 및 필요성:** 캐싱 전략, 전역 로드 밸런싱, 성능 병목 지점 최적화
4. **리스크:** 과도한 자동 확장으로 인한 비용 급증, 콜드 스타트 이슈, 팀 숙련도 부족`
};

// 모든 에이전트 배열
const ALL_AGENTS = [
  AGENT_SECURITY,
  AGENT_COST,
  AGENT_RELIABILITY,
  AGENT_OPERATIONAL,
  AGENT_SUSTAINABILITY,
  AGENT_PERFORMANCE
];

// ============================================================================
// 개별 에이전트 평가 함수
// ============================================================================

/**
 * 단일 에이전트 평가 실행
 * @param {Object} agent - 에이전트 정의
 * @param {Object} problem - 문제 정보
 * @param {string} architectureContext - 학생 아키텍처 설계
 * @param {string} userAnswer - 학생 답변
 * @returns {Object} 에이전트별 평가 결과
 */
async function runAgentEvaluation(agent, problem, architectureContext, userAnswer) {
  const prompt = `${agent.systemRole}

${agent.evaluationFramework}

---

## 평가 대상 시스템

### 문제 정보
- 제목: ${problem?.title || '시스템 아키텍처 설계'}
- 시나리오: ${problem?.scenario || ''}
- 미션: ${problem?.missions?.join(', ') || '없음'}

### 학생의 아키텍처 설계
${architectureContext}

### 학생의 답변/설명
${userAnswer || '(답변 없음)'}

---

## 평가 기준
${agent.evaluationCriteria}

---

## 출력 형식 (JSON만 출력!)

{
  "pillarScore": 0-100,
  "evaluation": {
    "suitability": {
      "score": 0-100,
      "analysis": "설계 적합성 분석 (2-3문장)"
    },
    "dataCollection": {
      "score": 0-100,
      "analysis": "가시성 확보 가능성 분석 (2-3문장)"
    },
    "strengths": {
      "score": 0-100,
      "analysis": "강점 및 도입 필요성 분석 (2-3문장)",
      "highlights": ["강점1", "강점2"]
    },
    "risks": {
      "score": 0-100,
      "analysis": "예상 어려움 및 리스크 분석 (2-3문장)",
      "concerns": ["리스크1", "리스크2"]
    }
  },
  "recommendations": {
    "shortTerm": ["즉시 적용 가능한 개선사항1", "개선사항2"],
    "longTerm": ["장기적 개선 과제1", "과제2"]
  },
  "summary": "해당 pillar 관점에서의 종합 평가 (2-3문장)"
}`;

  try {
    const response = await callOpenAI(prompt, { maxTokens: 1000, temperature: 0.4 });
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const result = JSON.parse(jsonMatch[0]);
      return {
        agentName: agent.name,
        emoji: agent.emoji,
        ...result
      };
    }
    throw new Error('Invalid JSON response');
  } catch (error) {
    console.error(`${agent.name} evaluation error:`, error);
    // Fallback 결과
    return {
      agentName: agent.name,
      emoji: agent.emoji,
      pillarScore: 50,
      evaluation: {
        suitability: { score: 50, analysis: '평가 오류로 분석할 수 없습니다.' },
        dataCollection: { score: 50, analysis: '평가 오류로 분석할 수 없습니다.' },
        strengths: { score: 50, analysis: '평가 오류로 분석할 수 없습니다.', highlights: [] },
        risks: { score: 50, analysis: '평가 오류로 분석할 수 없습니다.', concerns: [] }
      },
      recommendations: { shortTerm: [], longTerm: [] },
      summary: '평가 중 오류가 발생했습니다.'
    };
  }
}

// ============================================================================
// 다중 에이전트 평가 메인 함수
// ============================================================================

/**
 * 6개 에이전트 병렬 평가 실행
 * @param {Object} problem - 문제 정보
 * @param {string} architectureContext - 학생 아키텍처 설계
 * @param {string} generatedQuestion - 생성된 질문
 * @param {string} userAnswer - 학생 답변
 * @param {Array} deepDiveQnA - 심화 질문/답변 배열
 * @returns {Object} 종합 평가 결과
 */
export async function evaluateArchitectureMultiAgent(
  problem,
  architectureContext,
  generatedQuestion,
  userAnswer,
  deepDiveQnA
) {
  // 심화 답변도 userAnswer에 포함
  const deepDiveArray = Array.isArray(deepDiveQnA) ? deepDiveQnA : [];
  const deepDiveText = deepDiveArray.length > 0
    ? deepDiveArray.map((item, idx) =>
        `[심화 질문 ${idx + 1} - ${item.category || '일반'}]\nQ: ${item.question}\nA: ${item.answer || '(답변 없음)'}`
      ).join('\n\n')
    : '';

  const combinedAnswer = `${userAnswer || ''}\n\n${deepDiveText}`.trim();

  console.log('🚀 Starting Multi-Agent Evaluation...');
  const startTime = Date.now();

  // 6개 에이전트 병렬 실행
  const agentPromises = ALL_AGENTS.map(agent =>
    runAgentEvaluation(agent, problem, architectureContext, combinedAnswer)
  );

  const agentResults = await Promise.all(agentPromises);

  const endTime = Date.now();
  console.log(`✅ Multi-Agent Evaluation completed in ${(endTime - startTime) / 1000}s`);

  // 결과 종합
  const aggregatedResult = aggregateResults(agentResults, problem, architectureContext);

  return aggregatedResult;
}

/**
 * 에이전트 결과 종합
 */
function aggregateResults(agentResults, problem, architectureContext) {
  // 각 pillar별 점수 추출
  const pillarScores = {};
  const pillarDetails = {};

  agentResults.forEach(result => {
    const key = result.agentName.toLowerCase()
      .replace(/\s+&\s+/g, '_')
      .replace(/\s+/g, '_')
      .replace(/_agent$/g, '');

    pillarScores[key] = result.pillarScore;
    pillarDetails[key] = {
      name: result.agentName,
      emoji: result.emoji,
      score: result.pillarScore,
      evaluation: result.evaluation,
      recommendations: result.recommendations,
      summary: result.summary
    };
  });

  // 전체 점수 계산 (가중 평균)
  const weights = {
    'security_compliance': 0.20,
    'cost_optimization': 0.15,
    'reliability': 0.20,
    'operational_excellence': 0.15,
    'sustainability': 0.10,
    'performance_optimization': 0.20
  };

  let totalScore = 0;
  let totalWeight = 0;

  Object.entries(pillarScores).forEach(([key, score]) => {
    const weight = weights[key] || 0.166; // 기본 균등 가중치
    totalScore += score * weight;
    totalWeight += weight;
  });

  const finalScore = Math.round(totalScore / (totalWeight || 1));

  // 등급 결정
  const grade = finalScore >= 80 ? 'excellent' :
                finalScore >= 60 ? 'good' :
                finalScore >= 40 ? 'needs-improvement' : 'poor';

  // 모든 강점/약점/제안 수집
  const allStrengths = [];
  const allWeaknesses = [];
  const allShortTermSuggestions = [];
  const allLongTermSuggestions = [];

  agentResults.forEach(result => {
    if (result.evaluation?.strengths?.highlights) {
      allStrengths.push(...result.evaluation.strengths.highlights);
    }
    if (result.evaluation?.risks?.concerns) {
      allWeaknesses.push(...result.evaluation.risks.concerns);
    }
    if (result.recommendations?.shortTerm) {
      allShortTermSuggestions.push(...result.recommendations.shortTerm);
    }
    if (result.recommendations?.longTerm) {
      allLongTermSuggestions.push(...result.recommendations.longTerm);
    }
  });

  // 기존 형식과 호환되는 nfrScores 생성
  const nfrScores = {
    scalability: {
      score: pillarDetails['performance_optimization']?.score || 50,
      feedback: pillarDetails['performance_optimization']?.summary || ''
    },
    availability: {
      score: pillarDetails['reliability']?.score || 50,
      feedback: pillarDetails['reliability']?.summary || ''
    },
    performance: {
      score: pillarDetails['performance_optimization']?.score || 50,
      feedback: pillarDetails['performance_optimization']?.summary || ''
    },
    consistency: {
      score: pillarDetails['reliability']?.score || 50,
      feedback: pillarDetails['reliability']?.summary || ''
    },
    reliability: {
      score: pillarDetails['reliability']?.score || 50,
      feedback: pillarDetails['reliability']?.summary || ''
    }
  };

  return {
    // 기존 호환 필드
    score: finalScore,
    totalScore: finalScore,
    grade,
    nfrScores,

    // 다중 에이전트 평가 결과
    multiAgentEvaluation: {
      enabled: true,
      agentCount: agentResults.length,
      pillarScores,
      pillarDetails,
      weights
    },

    // 종합 분석
    summary: generateSummary(agentResults, finalScore, grade),
    strengths: [...new Set(allStrengths)].slice(0, 5),
    weaknesses: [...new Set(allWeaknesses)].slice(0, 5),
    suggestions: [...new Set(allShortTermSuggestions)].slice(0, 3),
    longTermSuggestions: [...new Set(allLongTermSuggestions)].slice(0, 3),

    // 상세 평가 결과
    agentResults
  };
}

/**
 * 종합 요약 생성
 */
function generateSummary(agentResults, finalScore, grade) {
  const highScorePillars = agentResults
    .filter(r => r.pillarScore >= 70)
    .map(r => `${r.emoji} ${r.agentName.replace(' Agent', '')}`);

  const lowScorePillars = agentResults
    .filter(r => r.pillarScore < 50)
    .map(r => `${r.emoji} ${r.agentName.replace(' Agent', '')}`);

  let summary = `종합 점수 ${finalScore}점(${grade}). `;

  if (highScorePillars.length > 0) {
    summary += `강점 영역: ${highScorePillars.join(', ')}. `;
  }

  if (lowScorePillars.length > 0) {
    summary += `개선 필요 영역: ${lowScorePillars.join(', ')}.`;
  } else if (highScorePillars.length === 0) {
    summary += '전반적으로 균형 잡힌 설계입니다.';
  }

  return summary;
}

// ============================================================================
// 개별 Pillar 평가 함수 (선택적 사용)
// ============================================================================

/**
 * 특정 Pillar만 평가
 */
export async function evaluateSinglePillar(pillarName, problem, architectureContext, userAnswer) {
  const agentMap = {
    'security': AGENT_SECURITY,
    'cost': AGENT_COST,
    'reliability': AGENT_RELIABILITY,
    'operational': AGENT_OPERATIONAL,
    'sustainability': AGENT_SUSTAINABILITY,
    'performance': AGENT_PERFORMANCE
  };

  const agent = agentMap[pillarName.toLowerCase()];
  if (!agent) {
    throw new Error(`Unknown pillar: ${pillarName}`);
  }

  return runAgentEvaluation(agent, problem, architectureContext, userAnswer);
}

/**
 * 선택한 Pillar들만 평가
 */
export async function evaluateSelectedPillars(pillarNames, problem, architectureContext, userAnswer) {
  const agentMap = {
    'security': AGENT_SECURITY,
    'cost': AGENT_COST,
    'reliability': AGENT_RELIABILITY,
    'operational': AGENT_OPERATIONAL,
    'sustainability': AGENT_SUSTAINABILITY,
    'performance': AGENT_PERFORMANCE
  };

  const selectedAgents = pillarNames
    .map(name => agentMap[name.toLowerCase()])
    .filter(Boolean);

  if (selectedAgents.length === 0) {
    throw new Error('No valid pillars selected');
  }

  const agentPromises = selectedAgents.map(agent =>
    runAgentEvaluation(agent, problem, architectureContext, userAnswer)
  );

  return Promise.all(agentPromises);
}

// ============================================================================
// 기존 API와의 호환 함수들 (re-export)
// ============================================================================

export { fetchProblems } from './architectureApiFast.js';
export { generateDeepDiveQuestion, generateArchitectureAnalysisQuestions, generateEvaluationQuestion, sendChatMessage } from './architectureApiFast.js';
