/**
 * Architecture Master Agent Evaluation Service
 * 마스터 에이전트가 분석 후 필요한 하위 에이전트만 선택적으로 호출하는 다중 에이전트 구조
 *
 * 구조:
 * 1. Master Agent - 전체 조율 및 분기 결정
 * 2. Sub Agents (5개):
 *    - Operational Excellence (운영 우수성)
 *    - Security & Compliance (보안 및 컴플라이언스)
 *    - Reliability (신뢰성/안정성)
 *    - Performance (성능 최적화)
 *    - Cost & Sustainability (비용 및 지속가능성)
 */

import architectureProblems from '@/data/architecture.json';

const getApiKey = () => import.meta.env.VITE_OPENAI_API_KEY;

/**
 * OpenAI API 호출 기본 함수
 */
async function callOpenAI(prompt, options = {}) {
  const {
    model = 'gpt-3.5-turbo',
    maxTokens = 1500,
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
// 마스터 에이전트 정의
// ============================================================================

const MASTER_AGENT_SYSTEM = `너는 Google Cloud Well-Architected Framework의 6대 기둥(Pillar)을 총괄하는 **마스터 솔루션 아키텍트 에이전트**야.

시스템 설계 원칙(계층 구조, 비상태성, 결합 해제 등)을 기준으로 사용자의 아키텍처를 1차 진단하고,
상세 분석이 필요한 영역을 하위 에이전트에게 할당하는 역할을 수행해.

**핵심 원칙:**
- Stateless (비상태성): 상태를 외부 저장소에 위임
- Decoupled Architecture (결합 해제): 컴포넌트 간 느슨한 결합
- Defense in Depth (심층 방어): 다계층 보안
- Design for Failure (장애 대비 설계): 장애를 가정한 설계`;

// ============================================================================
// 5개 하위 에이전트 정의
// ============================================================================

const SUB_AGENTS = {
  operational: {
    id: 'operational',
    name: 'Operational Excellence',
    emoji: '🤖',
    trigger: '배포 방식, 관리 자동화, IaC, CI/CD, 모니터링',
    systemRole: `너는 **운영 우수성(Operational Excellence) 전문가**야.
CloudOps, 인시던트 관리, 변경 자동화, 지속적 개선을 평가해.`,
    evaluationAreas: [
      'CloudOps를 통한 운영 준비: SLO 정의, 모니터링, 용량 계획',
      '인시던트 및 문제 관리: 대응 절차, 사후 검토(PIR)',
      '클라우드 리소스 관리: 적정 크기 조정, 자동 확장',
      '변경 자동화: IaC, CI/CD 파이프라인',
      '지속적 개선: 학습 문화, 회고, 피드백 루프'
    ]
  },

  security: {
    id: 'security',
    name: 'Security & Compliance',
    emoji: '🔐',
    trigger: '보안, 규제, 데이터 보호, IAM, 암호화, 컴플라이언스',
    systemRole: `너는 **보안 및 컴플라이언스 전문가**야.
보안 파운데이션, IAM, 네트워크 보안, 데이터 보호, 개인정보 보호, 컴플라이언스를 평가해.`,
    evaluationAreas: [
      '보안 파운데이션: 리소스 계층, 조직 정책, 랜딩 존',
      'ID 및 액세스 관리(IAM): 최소 권한, 서비스 계정',
      '네트워크 보안: VPC, 마이크로 세그멘테이션',
      '데이터 보호: 암호화(KMS), DLP',
      '개인정보 보호: 데이터 최소화, 익명화',
      '컴플라이언스: 규제 요구사항 매핑'
    ]
  },

  reliability: {
    id: 'reliability',
    name: 'Reliability',
    emoji: '🏗️',
    trigger: '장애 대응, SLO, 복구 탄력성, 고가용성, DR, SPOF',
    systemRole: `너는 **사이트 신뢰성 엔지니어(SRE)**야.
신뢰성 목표, 복구 중심 설계, 모니터링, 변경 관리, 장애 대응을 평가해.`,
    evaluationAreas: [
      '신뢰성 목표: SLI/SLO 정의, 에러 버짓',
      '복구 중심 설계: 중복성, Failover, DR 계획',
      '가시성 및 모니터링: 실시간 파악, 자동 알림',
      '변경 관리: 카나리 배포, 롤백 전략',
      '장애 대응: 자동 복구, Blameless Postmortem'
    ]
  },

  performance: {
    id: 'performance',
    name: 'Performance',
    emoji: '⚡',
    trigger: '성능, 지연 시간, 처리량, 캐싱, 확장성, 병목',
    systemRole: `너는 **성능 엔지니어링 전문가**야.
요구사항 정의, 성능 설계, 모니터링, 지속적 최적화를 평가해.`,
    evaluationAreas: [
      '요구사항 정의: Latency, Throughput 기준',
      '성능 설계: 컴퓨팅, 스토리지, 네트워크 선택',
      '모니터링: 대시보드, 병목 식별, 프로파일링',
      '지속적 최적화: Autoscaling, 코드 효율화'
    ]
  },

  costSustainability: {
    id: 'costSustainability',
    name: 'Cost & Sustainability',
    emoji: '💰🌱',
    trigger: '비용 절감, 탄소 발자국, FinOps, 친환경, 리소스 효율',
    systemRole: `너는 **FinOps 및 지속가능성 전문가**야.
비용 최적화와 환경 영향을 통합적으로 평가해.`,
    evaluationAreas: [
      '비용 인식: 팀별 비용 할당, 라벨링 전략',
      '클라우드 소비 최적화: Right-sizing, 유휴 리소스 제거',
      '구매 모델: CUD, Spot VM 활용',
      '환경 영향: Carbon Footprint 모니터링',
      '저탄소 설계: 리전 선택, 서버리스 활용',
      '데이터 효율화: 스토리지 수명주기 관리'
    ]
  }
};

// ============================================================================
// Step 1: 마스터 에이전트 - 분석 및 분기 결정
// ============================================================================

/**
 * 마스터 에이전트: 아키텍처 분석 후 필요한 하위 에이전트 결정
 */
async function masterAgentAnalyze(problem, architectureContext, userAnswer) {
  const agentTriggers = Object.values(SUB_AGENTS)
    .map(a => `- ${a.name}: ${a.trigger}`)
    .join('\n');

  const prompt = `${MASTER_AGENT_SYSTEM}

---

## 평가 대상 시스템

### 문제 정보
- 제목: ${problem?.title || '시스템 아키텍처 설계'}
- 시나리오: ${problem?.scenario || ''}
- 미션: ${problem?.missions?.join(', ') || '없음'}

### 학생의 아키텍처 설계
${architectureContext}

### 학생의 설명/답변
${userAnswer || '(답변 없음)'}

---

## 하위 에이전트 트리거 조건
${agentTriggers}

---

## 작업 지시

1. 위 아키텍처를 분석하여 **Stateless**, **Decoupled Architecture** 원칙 준수 여부를 1차 판정해.
2. 상세 분석이 필요한 영역(Pillar)을 **우선순위대로** 선택해. (최소 2개, 최대 4개)
3. 각 선택 이유를 간단히 설명해.

## 출력 형식 (JSON만 출력!)

{
  "initialAssessment": {
    "statelessCompliance": "high/medium/low",
    "decoupledCompliance": "high/medium/low",
    "overallMaturity": "advanced/intermediate/beginner",
    "summary": "1차 진단 요약 (2-3문장)"
  },
  "selectedAgents": [
    {
      "agentId": "reliability",
      "priority": 1,
      "reason": "선택 이유"
    },
    {
      "agentId": "performance",
      "priority": 2,
      "reason": "선택 이유"
    }
  ],
  "skipReason": {
    "operational": "스킵 이유 (해당 시)",
    "security": "스킵 이유 (해당 시)"
  }
}`;

  try {
    const response = await callOpenAI(prompt, { maxTokens: 800, temperature: 0.3 });
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    throw new Error('Invalid JSON');
  } catch (error) {
    console.error('Master agent analysis error:', error);
    // Fallback: 기본 3개 에이전트 선택
    return {
      initialAssessment: {
        statelessCompliance: 'medium',
        decoupledCompliance: 'medium',
        overallMaturity: 'intermediate',
        summary: '분석 중 오류가 발생하여 기본 평가를 진행합니다.'
      },
      selectedAgents: [
        { agentId: 'reliability', priority: 1, reason: '기본 평가' },
        { agentId: 'performance', priority: 2, reason: '기본 평가' },
        { agentId: 'security', priority: 3, reason: '기본 평가' }
      ],
      skipReason: {}
    };
  }
}

// ============================================================================
// Step 2: 하위 에이전트 실행
// ============================================================================

/**
 * 하위 에이전트 평가 실행
 */
async function runSubAgentEvaluation(agentConfig, problem, architectureContext, userAnswer) {
  const evaluationAreasText = agentConfig.evaluationAreas.map((a, i) => `${i + 1}. ${a}`).join('\n');

  const prompt = `${agentConfig.systemRole}

---

## 평가 영역
${evaluationAreasText}

---

## 평가 대상

### 문제: ${problem?.title || '시스템 아키텍처 설계'}
시나리오: ${problem?.scenario || ''}

### 학생의 아키텍처
${architectureContext}

### 학생의 답변
${userAnswer || '(답변 없음)'}

---

## 평가 기준 (4대 기준)

1. **설계 적합성 (Suitability):** 권장 모범 사례 충실도
2. **가시성 확보 (Data Collection):** 필요한 데이터/지표 수집 가능 여부
3. **강점 및 필요성 (Strengths & Necessity):** 잘 설계된 부분과 개선 필요 영역
4. **예상 어려움 (Difficulties):** 잠재적 장애 요인 및 리스크

---

## 출력 형식 (JSON만!)

{
  "pillarScore": 0-100,
  "evaluation": {
    "suitability": {
      "score": 0-100,
      "analysis": "분석 내용 (2-3문장)"
    },
    "dataCollection": {
      "score": 0-100,
      "analysis": "분석 내용 (2-3문장)"
    },
    "strengths": {
      "score": 0-100,
      "analysis": "분석 내용 (2-3문장)",
      "highlights": ["강점1", "강점2"]
    },
    "difficulties": {
      "score": 0-100,
      "analysis": "분석 내용 (2-3문장)",
      "concerns": ["리스크1", "리스크2"]
    }
  },
  "deepDiveQuestions": [
    "이 영역에서 학생에게 물어볼 심층 질문 1",
    "심층 질문 2"
  ],
  "recommendations": {
    "shortTerm": ["즉시 개선 가능한 사항"],
    "longTerm": ["장기적 개선 과제"]
  },
  "summary": "이 Pillar 관점에서의 종합 평가 (2문장)"
}`;

  try {
    const response = await callOpenAI(prompt, { maxTokens: 1000, temperature: 0.4 });
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const result = JSON.parse(jsonMatch[0]);
      return {
        agentId: agentConfig.id,
        agentName: agentConfig.name,
        emoji: agentConfig.emoji,
        ...result
      };
    }
    throw new Error('Invalid JSON');
  } catch (error) {
    console.error(`${agentConfig.name} evaluation error:`, error);
    return {
      agentId: agentConfig.id,
      agentName: agentConfig.name,
      emoji: agentConfig.emoji,
      pillarScore: 50,
      evaluation: {
        suitability: { score: 50, analysis: '평가 오류' },
        dataCollection: { score: 50, analysis: '평가 오류' },
        strengths: { score: 50, analysis: '평가 오류', highlights: [] },
        difficulties: { score: 50, analysis: '평가 오류', concerns: [] }
      },
      deepDiveQuestions: [],
      recommendations: { shortTerm: [], longTerm: [] },
      summary: '평가 중 오류가 발생했습니다.'
    };
  }
}

// ============================================================================
// Step 3: 마스터 에이전트 - 최종 통합 리포트
// ============================================================================

/**
 * 마스터 에이전트: 하위 에이전트 결과 종합
 */
async function masterAgentSynthesize(initialAssessment, subAgentResults, problem) {
  const subResultsSummary = subAgentResults.map(r =>
    `### ${r.emoji} ${r.agentName} (${r.pillarScore}점)\n${r.summary}`
  ).join('\n\n');

  const allStrengths = subAgentResults.flatMap(r => r.evaluation?.strengths?.highlights || []);
  const allConcerns = subAgentResults.flatMap(r => r.evaluation?.difficulties?.concerns || []);

  const prompt = `${MASTER_AGENT_SYSTEM}

---

## 1차 진단 결과
- Stateless 준수: ${initialAssessment.statelessCompliance}
- Decoupled 준수: ${initialAssessment.decoupledCompliance}
- 전체 성숙도: ${initialAssessment.overallMaturity}
- 요약: ${initialAssessment.summary}

## 하위 에이전트 평가 결과
${subResultsSummary}

## 수집된 강점
${allStrengths.join(', ') || '없음'}

## 수집된 리스크
${allConcerns.join(', ') || '없음'}

---

## 최종 리포트 작성 (4대 기준)

1. **종합 적합성 (Overall Suitability):** Stateless, Decoupled Architecture 원칙 기준 클라우드 네이티브 설계 판정
2. **통합 가시성 (Unified Observability):** 6개 영역 지표를 중앙에서 통합 수집/분석 가능한 구조인지
3. **핵심 강점 및 전략적 필요성:** 최대 강점과 가장 먼저 개선할 영역(Pillar) 추천
4. **복합 리스크 (Cross-pillar Difficulties):** 한 영역 최적화가 다른 영역에 미치는 부작용

---

## 출력 형식 (JSON만!)

{
  "totalScore": 0-100,
  "grade": "excellent/good/needs-improvement/poor",

  "finalReport": {
    "overallSuitability": {
      "cloudNativeScore": 0-100,
      "statelessLevel": "high/medium/low",
      "decoupledLevel": "high/medium/low",
      "analysis": "종합 적합성 분석 (3-4문장)"
    },
    "unifiedObservability": {
      "score": 0-100,
      "integrationLevel": "high/medium/low",
      "analysis": "통합 가시성 분석 (2-3문장)"
    },
    "strategicStrengths": {
      "topStrengths": ["핵심 강점1", "강점2"],
      "priorityImprovement": {
        "pillar": "가장 먼저 개선할 Pillar",
        "reason": "이유"
      },
      "analysis": "전략적 필요성 분석 (2-3문장)"
    },
    "crossPillarRisks": {
      "tradeoffs": [
        {
          "action": "A 영역 최적화",
          "sideEffect": "B 영역에 미치는 부작용"
        }
      ],
      "technicalDebt": ["기술적 부채 항목"],
      "analysis": "복합 리스크 분석 (2-3문장)"
    }
  },

  "summary": "최종 종합 평가 (3-4문장)",
  "strengths": ["전체 강점1", "강점2", "강점3"],
  "weaknesses": ["전체 약점1", "약점2"],
  "actionPlan": {
    "immediate": ["즉시 실행할 액션"],
    "shortTerm": ["단기 과제"],
    "longTerm": ["장기 과제"]
  }
}`;

  try {
    const response = await callOpenAI(prompt, { maxTokens: 1500, temperature: 0.3 });
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    throw new Error('Invalid JSON');
  } catch (error) {
    console.error('Master synthesis error:', error);
    // Fallback
    const avgScore = Math.round(
      subAgentResults.reduce((sum, r) => sum + r.pillarScore, 0) / subAgentResults.length
    );
    return {
      totalScore: avgScore,
      grade: avgScore >= 80 ? 'excellent' : avgScore >= 60 ? 'good' : avgScore >= 40 ? 'needs-improvement' : 'poor',
      finalReport: {
        overallSuitability: { cloudNativeScore: avgScore, statelessLevel: 'medium', decoupledLevel: 'medium', analysis: '통합 분석 중 오류 발생' },
        unifiedObservability: { score: avgScore, integrationLevel: 'medium', analysis: '통합 분석 중 오류 발생' },
        strategicStrengths: { topStrengths: allStrengths.slice(0, 3), priorityImprovement: { pillar: '미정', reason: '분석 오류' }, analysis: '통합 분석 중 오류 발생' },
        crossPillarRisks: { tradeoffs: [], technicalDebt: allConcerns.slice(0, 3), analysis: '통합 분석 중 오류 발생' }
      },
      summary: '최종 통합 분석 중 오류가 발생했습니다.',
      strengths: allStrengths.slice(0, 3),
      weaknesses: allConcerns.slice(0, 3),
      actionPlan: { immediate: [], shortTerm: [], longTerm: [] }
    };
  }
}

// ============================================================================
// 메인 평가 함수
// ============================================================================

/**
 * 마스터 에이전트 기반 다중 에이전트 평가 실행
 *
 * 흐름:
 * 1. 마스터 에이전트가 아키텍처 분석 → 필요한 하위 에이전트 결정
 * 2. 선택된 하위 에이전트들이 병렬로 상세 평가
 * 3. 마스터 에이전트가 결과 종합 → 4대 기준 최종 리포트
 */
export async function evaluateWithMasterAgent(
  problem,
  architectureContext,
  generatedQuestion,
  userAnswer,
  deepDiveQnA
) {
  // 심화 답변 포함
  const deepDiveArray = Array.isArray(deepDiveQnA) ? deepDiveQnA : [];
  const deepDiveText = deepDiveArray.length > 0
    ? deepDiveArray.map((item, idx) =>
        `[심화 ${idx + 1}] Q: ${item.question}\nA: ${item.answer || '(답변 없음)'}`
      ).join('\n\n')
    : '';

  const combinedAnswer = `${userAnswer || ''}\n\n${deepDiveText}`.trim();

  console.log('🎯 Step 1: Master Agent analyzing architecture...');
  const startTime = Date.now();

  // Step 1: 마스터 에이전트 1차 분석
  const masterAnalysis = await masterAgentAnalyze(problem, architectureContext, combinedAnswer);
  console.log(`✅ Master analysis complete. Selected agents: ${masterAnalysis.selectedAgents.map(a => a.agentId).join(', ')}`);

  // Step 2: 선택된 하위 에이전트들 병렬 실행
  console.log('🔄 Step 2: Running selected sub-agents in parallel...');
  const selectedAgentConfigs = masterAnalysis.selectedAgents
    .map(sa => SUB_AGENTS[sa.agentId])
    .filter(Boolean);

  const subAgentPromises = selectedAgentConfigs.map(agentConfig =>
    runSubAgentEvaluation(agentConfig, problem, architectureContext, combinedAnswer)
  );

  const subAgentResults = await Promise.all(subAgentPromises);
  console.log(`✅ Sub-agent evaluations complete. (${subAgentResults.length} agents)`);

  // Step 3: 마스터 에이전트 최종 통합
  console.log('📊 Step 3: Master Agent synthesizing final report...');
  const finalReport = await masterAgentSynthesize(
    masterAnalysis.initialAssessment,
    subAgentResults,
    problem
  );

  const endTime = Date.now();
  console.log(`🏁 Master Agent evaluation completed in ${((endTime - startTime) / 1000).toFixed(1)}s`);

  // 기존 형식과 호환되는 결과 구성
  return {
    // 기존 호환 필드
    score: finalReport.totalScore,
    totalScore: finalReport.totalScore,
    grade: finalReport.grade,
    summary: finalReport.summary,
    strengths: finalReport.strengths,
    weaknesses: finalReport.weaknesses,
    suggestions: finalReport.actionPlan?.shortTerm || [],

    // 기존 nfrScores 호환 (하위 에이전트 점수 매핑)
    nfrScores: mapToNfrScores(subAgentResults),

    // 마스터 에이전트 전용 결과
    masterAgentEvaluation: {
      enabled: true,
      initialAssessment: masterAnalysis.initialAssessment,
      selectedAgents: masterAnalysis.selectedAgents,
      skippedAgents: masterAnalysis.skipReason,
      finalReport: finalReport.finalReport,
      actionPlan: finalReport.actionPlan
    },

    // 하위 에이전트 상세 결과
    subAgentResults,

    // 심층 질문 (하위 에이전트들이 생성한 질문 수집)
    deepDiveQuestions: subAgentResults.flatMap(r => r.deepDiveQuestions || [])
  };
}

/**
 * 하위 에이전트 결과를 기존 nfrScores 형식으로 매핑
 */
function mapToNfrScores(subAgentResults) {
  const nfrScores = {
    scalability: { score: 50, feedback: '' },
    availability: { score: 50, feedback: '' },
    performance: { score: 50, feedback: '' },
    consistency: { score: 50, feedback: '' },
    reliability: { score: 50, feedback: '' }
  };

  subAgentResults.forEach(result => {
    switch (result.agentId) {
      case 'reliability':
        nfrScores.reliability = { score: result.pillarScore, feedback: result.summary };
        nfrScores.availability = { score: result.pillarScore, feedback: result.summary };
        break;
      case 'performance':
        nfrScores.performance = { score: result.pillarScore, feedback: result.summary };
        nfrScores.scalability = { score: result.pillarScore, feedback: result.summary };
        break;
      case 'security':
        nfrScores.consistency = { score: result.pillarScore, feedback: result.summary };
        break;
      case 'operational':
        // operational은 전반적인 운영 성숙도에 영향
        break;
      case 'costSustainability':
        // cost는 별도 표시
        break;
    }
  });

  return nfrScores;
}

// ============================================================================
// 유틸리티 함수들
// ============================================================================

/**
 * 특정 하위 에이전트만 단독 실행
 */
export async function runSingleSubAgent(agentId, problem, architectureContext, userAnswer) {
  const agentConfig = SUB_AGENTS[agentId];
  if (!agentConfig) {
    throw new Error(`Unknown agent: ${agentId}`);
  }
  return runSubAgentEvaluation(agentConfig, problem, architectureContext, userAnswer);
}

/**
 * 마스터 분석만 실행 (하위 에이전트 호출 없이)
 */
export async function runMasterAnalysisOnly(problem, architectureContext, userAnswer) {
  return masterAgentAnalyze(problem, architectureContext, userAnswer);
}

/**
 * 사용 가능한 하위 에이전트 목록
 */
export function getAvailableSubAgents() {
  return Object.values(SUB_AGENTS).map(a => ({
    id: a.id,
    name: a.name,
    emoji: a.emoji,
    trigger: a.trigger
  }));
}

// ============================================================================
// 기존 API 호환 re-export
// ============================================================================

export { fetchProblems } from './architectureApiFast.js';
export { generateDeepDiveQuestion, generateArchitectureAnalysisQuestions, generateEvaluationQuestion, sendChatMessage } from './architectureApiFast.js';
