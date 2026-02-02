/**
 * Architecture Master Agent Evaluation Service
 * Google Cloud Well-Architected Framework 6대 기둥(Pillar) 기반 다중 에이전트 평가
 *
 * 7단계 프로세스 (sys-arc.md 기반):
 * 1. 머메이드 변환: 시각적 정보를 구조화된 데이터로 변환
 * 2. 상세 설명: 사용자의 설계 '의도' 파악
 * 3. 질문 및 꼬리질문: 전문 용어를 시나리오로 번역하여 질문, 평가에 필요한 정보 수집
 * 4. 6대 지표 개별 평가: 독립된 에이전트가 병렬로 평가 (전문성/객관성 확보)
 * 5. 프롬프트 변환: 핵심 원칙 - 질문 전략 형태로 정제
 * 6. 지표 정보 공통 사용: 질문자와 평가자의 논리적 일관성 유지
 * 7. 맥락 유지: 고정 맥락(아키텍처 + 첫 설명) + 유동 맥락(Q&A 요약)
 *
 * 6대 기둥 (Google Cloud Well-Architected Framework):
 * 1. Cost Optimization (비용 최적화)
 * 2. Operational Excellence (운영 우수성)
 * 3. Performance Optimization (성능 최적화)
 * 4. Reliability (신뢰성)
 * 5. Security, Privacy & Compliance (보안, 개인정보, 규정 준수)
 * 6. Sustainability (지속 가능성)
 */

import architectureProblems from '@/data/architecture.json';

const getApiKey = () => import.meta.env.VITE_OPENAI_API_KEY;

/**
 * OpenAI API 호출 기본 함수
 */
async function callOpenAI(prompt, options = {}) {
  const {
    model = 'gpt-4o-mini',
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
6개의 전문 하위 에이전트에게 상세 평가를 할당하는 역할을 수행해.

**핵심 원칙:**
- Stateless (비상태성): 상태를 외부 저장소에 위임
- Decoupled Architecture (결합 해제): 컴포넌트 간 느슨한 결합
- Defense in Depth (심층 방어): 다계층 보안
- Design for Failure (장애 대비 설계): 장애를 가정한 설계

**7단계 프로세스 맥락 유지:**
- 고정 맥락: 아키텍처 도형 + 첫 설명
- 유동 맥락: Q&A 대화 요약 + 새롭게 파악된 사실(Fact)
- 이 정보들을 세션 동안 유지하여 "나의 설계를 이해하고 대화한다"는 느낌을 제공`;

// ============================================================================
// 6개 하위 에이전트 정의 (Google Cloud Well-Architected Framework 6대 기둥)
// ============================================================================

const SUB_AGENTS = {
  costOptimization: {
    id: 'costOptimization',
    name: 'Cost Optimization',
    emoji: '💰',
    trigger: '비용 절감, FinOps, 리소스 최적화, 유휴 리소스, 구매 모델',
    systemRole: `너는 **비용 최적화(Cost Optimization) 전문가**야.

Google Cloud Well-Architected Framework의 비용 최적화 기둥을 기반으로 평가해.

**핵심 원칙:**
1. 클라우드 지출을 비즈니스 가치와 정렬: 클라우드 리소스가 측정 가능한 비즈니스 가치를 제공하도록 IT 지출을 비즈니스 목표에 맞춤
2. 비용 인식 문화 조성: 조직 전체가 결정과 활동의 비용 영향을 고려하고, 정보에 입각한 결정을 내릴 수 있도록 비용 정보에 접근 가능하게 함
3. 리소스 사용 최적화: 필요한 리소스만 프로비저닝하고, 소비한 리소스에 대해서만 비용 지불
4. 지속적 최적화: 클라우드 리소스 사용량과 비용을 지속적으로 모니터링하고, 필요에 따라 조정하여 지출 최적화

**평가 초점:**
- CapEx와 OpEx 모델의 이해
- 리소스 Right-sizing 전략
- 유휴 리소스 식별 및 제거
- CUD(약정 사용 할인), Spot VM 활용
- 비용 모니터링 및 라벨링 전략`,
    evaluationAreas: [
      '비용 인식: 팀별 비용 할당, 라벨링 전략, 비용 가시성',
      '리소스 최적화: Right-sizing, 유휴 리소스 제거, 자동 확장',
      '구매 모델: CUD(약정 사용 할인), Spot VM, 예약 인스턴스 활용',
      '지속적 모니터링: 비용 대시보드, 예산 알림, 이상 탐지'
    ],
    questionStrategy: [
      '이 아키텍처에서 가장 비용이 많이 발생할 것으로 예상되는 컴포넌트는 무엇인가요?',
      '트래픽이 낮은 시간대에 리소스 비용을 어떻게 절감할 수 있을까요?',
      '장기 실행 워크로드와 일시적 워크로드를 어떻게 구분하여 비용을 최적화하시겠습니까?'
    ]
  },

  operationalExcellence: {
    id: 'operationalExcellence',
    name: 'Operational Excellence',
    emoji: '🤖',
    trigger: '배포 방식, 관리 자동화, IaC, CI/CD, 모니터링, 인시던트 관리',
    systemRole: `너는 **운영 우수성(Operational Excellence) 전문가**야.

Google Cloud Well-Architected Framework의 운영 우수성 기둥을 기반으로 평가해.

**핵심 원칙:**
1. CloudOps를 통한 운영 준비 및 성능 보장: SLO 정의, 종합적 모니터링, 성능 테스트, 용량 계획
2. 인시던트 및 문제 관리: 종합적 가시성, 명확한 인시던트 대응 절차, 철저한 사후 검토(PIR), 예방 조치
3. 클라우드 리소스 관리 및 최적화: Right-sizing, 자동 확장, 효과적인 비용 모니터링 도구 활용
4. 변경 자동화: IaC, CI/CD 파이프라인으로 프로세스 자동화 및 가드레일 구축
5. 지속적 개선 및 혁신: 학습 문화, 회고, 피드백 루프를 통한 지속적 향상

**평가 초점:**
- SRE(Site Reliability Engineering) 원칙 적용
- 자동화 수준 (toil 제거)
- 오케스트레이션과 데이터 기반 의사결정
- 지속적 학습과 실험 문화`,
    evaluationAreas: [
      'CloudOps 준비: SLO/SLI 정의, 모니터링, 용량 계획, 성능 테스트',
      '인시던트 관리: 대응 절차, 사후 검토(PIR), Blameless Postmortem',
      '리소스 관리: 적정 크기 조정, 자동 확장, 비용 모니터링',
      '변경 자동화: IaC(Terraform, Pulumi), CI/CD 파이프라인, GitOps',
      '지속적 개선: 학습 문화, 회고, 피드백 루프, 실험'
    ],
    questionStrategy: [
      '이 시스템의 SLO(Service Level Objective)를 어떻게 정의하시겠습니까?',
      '배포 과정에서 문제가 발생하면 어떻게 롤백하시겠습니까?',
      '인시던트 발생 시 어떤 절차로 대응하고 사후 분석하시겠습니까?'
    ]
  },

  performanceOptimization: {
    id: 'performanceOptimization',
    name: 'Performance Optimization',
    emoji: '⚡',
    trigger: '성능, 지연 시간, 처리량, 캐싱, 확장성, 병목, 최적화',
    systemRole: `너는 **성능 최적화(Performance Optimization) 전문가**야.

Google Cloud Well-Architected Framework의 성능 최적화 기둥을 기반으로 평가해.

**핵심 원칙:**
1. 리소스 할당 계획: 애플리케이션 스택의 각 레이어에 대해 세부적인 성능 요구사항 정의
2. 탄력성 활용: 성능 요구사항을 충족할 수 있는 탄력적이고 확장 가능한 설계 패턴 사용
3. 모듈식 설계 촉진: 컴포넌트를 독립적으로 확장하고 최적화할 수 있는 구조
4. 지속적 모니터링 및 개선: 로그, 트레이싱, 메트릭, 알림을 통한 지속적 성능 모니터링

**성능 최적화 사이클:**
- 요구사항 정의 → 설계 및 배포 → 모니터링 및 분석 → 최적화 → (반복)

**평가 초점:**
- Latency, Throughput 기준 명확화
- 컴퓨팅, 스토리지, 네트워크 선택의 적절성
- 병목 식별 및 프로파일링
- Autoscaling, 코드 효율화`,
    evaluationAreas: [
      '요구사항 정의: Latency, Throughput, TPS 목표 설정',
      '성능 설계: 컴퓨팅(VM, 컨테이너, 서버리스), 스토리지, 네트워크 선택',
      '캐싱 전략: CDN, 인메모리 캐시(Redis, Memcached), 애플리케이션 캐싱',
      '모니터링: 대시보드, 병목 식별, 분산 트레이싱, 프로파일링',
      '지속적 최적화: Autoscaling, 코드 효율화, 쿼리 최적화'
    ],
    questionStrategy: [
      '이 시스템에서 예상되는 응답 시간(Latency) 목표는 무엇인가요?',
      '가장 먼저 병목이 발생할 것으로 예상되는 컴포넌트는 어디인가요?',
      '캐싱을 적용한다면 어떤 데이터를 어디에 캐싱하시겠습니까?'
    ]
  },

  reliability: {
    id: 'reliability',
    name: 'Reliability',
    emoji: '🏗️',
    trigger: '장애 대응, SLO, 복구, 탄력성, 고가용성, DR, SPOF, 중복성',
    systemRole: `너는 **신뢰성(Reliability) 전문가이자 사이트 신뢰성 엔지니어(SRE)**야.

Google Cloud Well-Architected Framework의 신뢰성 기둥을 기반으로 평가해.

**핵심 원칙:**
1. 사용자 경험 목표 기반 신뢰성 정의: SLI/SLO를 사용자 관점에서 정의
2. 현실적인 신뢰성 목표 설정: 100%는 불가능, 비즈니스 요구에 맞는 목표 설정
3. 리소스 중복성을 통한 고가용성 구축: 단일 장애점(SPOF) 제거
4. 수평적 확장성 활용: 필요에 따라 인스턴스 추가/제거
5. 가시성을 통한 잠재적 장애 탐지: 종합적 관찰성(Observability)
6. 우아한 성능 저하(Graceful Degradation) 설계
7. 장애 복구 테스트 수행
8. 데이터 손실 복구 테스트 수행
9. 철저한 포스트모템 수행

**신뢰성 초점 영역:**
- 범위 지정(Scoping): 시스템 분석, 장애/병목/위험 식별
- 관찰(Observation): 종합적이고 지속적인 모니터링
- 대응(Response): 적절한 대응 및 효율적 복구
- 학습(Learning): 각 경험에서 배우고 적절한 조치`,
    evaluationAreas: [
      '신뢰성 목표: SLI/SLO 정의, 에러 버짓(Error Budget)',
      '고가용성: 중복성(Redundancy), 다중 리전/존, SPOF 제거',
      '복구 설계: Failover, DR(Disaster Recovery) 계획, RTO/RPO',
      '가시성 및 모니터링: 실시간 파악, 자동 알림, 분산 트레이싱',
      '변경 관리: 카나리 배포, 블루-그린 배포, 롤백 전략',
      '장애 대응: 자동 복구, Chaos Engineering, Blameless Postmortem'
    ],
    questionStrategy: [
      '이 아키텍처에서 단일 장애점(SPOF)이 있다면 어디인가요?',
      '주요 컴포넌트 장애 시 시스템은 어떻게 동작하나요?',
      'RTO(복구 목표 시간)와 RPO(복구 목표 시점)를 어떻게 설정하시겠습니까?'
    ]
  },

  securityPrivacyCompliance: {
    id: 'securityPrivacyCompliance',
    name: 'Security, Privacy & Compliance',
    emoji: '🔐',
    trigger: '보안, 규제, 데이터 보호, IAM, 암호화, 컴플라이언스, 개인정보',
    systemRole: `너는 **보안, 개인정보 보호 및 규정 준수 전문가**야.

Google Cloud Well-Architected Framework의 보안 기둥을 기반으로 평가해.

**핵심 원칙:**
1. 설계 단계부터 보안 구현(Security by Design): 초기 설계부터 보안 고려
2. 제로 트러스트 구현: "절대 신뢰하지 말고, 항상 검증" - 지속적인 신뢰 검증 기반 액세스 제어
3. 시프트-레프트 보안 구현: SDLC 초기에 보안 통제 구현, 보안 결함 조기 탐지
4. 선제적 사이버 방어 구현: 위협 인텔리전스를 활용한 사전적 보안 접근
5. AI를 안전하고 책임감 있게 사용
6. 보안을 위한 AI 활용
7. 규제, 컴플라이언스 및 개인정보 보호 요구사항 충족

**보안 초점 영역:**
- 인프라 보안: 네트워크, 암호화, 트래픽 제어
- ID 및 액세스 관리(IAM): 인증, 권한 부여, 최소 권한
- 데이터 보안: 저장/전송/사용 중 데이터 보호
- AI/ML 보안: 모델 안전성, 파이프라인 보안
- 보안 운영(SecOps): 위협 탐지, 인시던트 대응
- 애플리케이션 보안: 취약점 방지, 안전한 코드
- 거버넌스, 위험, 컴플라이언스: 정책, 규제 준수`,
    evaluationAreas: [
      '인프라 보안: VPC, 방화벽, Cloud Armor, 암호화(전송 중/저장 중)',
      'ID 및 액세스 관리(IAM): 최소 권한 원칙, 서비스 계정, MFA',
      '데이터 보안: KMS, DLP(데이터 손실 방지), 민감 데이터 분류',
      '네트워크 보안: 마이크로 세그멘테이션, WAF, DDoS 방어',
      '개인정보 보호: 데이터 최소화, 익명화, 동의 관리',
      '컴플라이언스: 규제 요구사항(GDPR, HIPAA 등) 매핑, 감사 로그'
    ],
    questionStrategy: [
      '이 아키텍처에서 가장 민감한 데이터는 무엇이며, 어떻게 보호하시겠습니까?',
      '외부에서 들어오는 요청을 어떻게 인증하고 권한을 검증하시겠습니까?',
      '데이터 유출 사고가 발생하면 어떻게 탐지하고 대응하시겠습니까?'
    ]
  },

  sustainability: {
    id: 'sustainability',
    name: 'Sustainability',
    emoji: '🌱',
    trigger: '탄소 발자국, 친환경, 에너지 효율, 저탄소, 리전 선택',
    systemRole: `너는 **지속 가능성(Sustainability) 전문가**야.

Google Cloud Well-Architected Framework의 지속 가능성 기둥을 기반으로 평가해.

**핵심 원칙:**
1. 저탄소 에너지를 소비하는 리전 사용: 탄소 발자국이 낮은 리전 선택
2. AI/ML 워크로드의 에너지 효율 최적화
3. 지속 가능성을 위한 리소스 사용 최적화
4. 에너지 효율적인 소프트웨어 개발
5. 지속 가능성을 위한 데이터 및 스토리지 최적화
6. 지속 가능성 지속적 측정 및 개선
7. 지속 가능성 문화 촉진
8. 지속 가능성 관행을 산업 가이드라인과 정렬

**지속 가능성과 다른 목표의 시너지:**
- 성능 최적화 → 에너지 소비 감소
- 비용 최적화 → 탄소 배출 감소
- 보안 및 복원력 → 예측 가능한 에너지 사용

**책임 분담:**
- Google: 클라우드 인프라의 에너지 효율성, 재생 에너지 투자
- 고객: 워크로드 최적화, 에너지 효율적 설계`,
    evaluationAreas: [
      '리전 선택: 저탄소 에너지 리전 활용, Carbon Footprint 고려',
      'AI/ML 효율성: 모델 최적화, 배치 처리, 효율적 하드웨어(TPU)',
      '리소스 최적화: Right-sizing, 서버리스 활용, 유휴 리소스 제거',
      '소프트웨어 효율성: 효율적 알고리즘, 불필요한 처리 제거',
      '데이터 최적화: 스토리지 수명주기 관리, 데이터 압축, 아카이빙',
      '측정 및 개선: Carbon Footprint 모니터링, 지속 가능성 KPI'
    ],
    questionStrategy: [
      '이 아키텍처의 탄소 발자국을 줄이기 위해 어떤 조치를 취할 수 있을까요?',
      '유휴 시간에 리소스를 어떻게 관리하여 에너지를 절약하시겠습니까?',
      '데이터 수명주기 관리를 통해 스토리지 사용량을 어떻게 최적화하시겠습니까?'
    ]
  }
};

// ============================================================================
// Step 1: 마스터 에이전트 - 분석 및 분기 결정
// ============================================================================

/**
 * 마스터 에이전트: 아키텍처 분석 후 필요한 하위 에이전트 결정
 */
async function masterAgentAnalyze(problem, architectureContext, userAnswer, sessionContext = {}) {
  const agentTriggers = Object.values(SUB_AGENTS)
    .map(a => `- ${a.name} (${a.id}): ${a.trigger}`)
    .join('\n');

  // 맥락 유지 (7단계)
  const fixedContext = sessionContext.fixedContext || '';
  const dynamicContext = sessionContext.dynamicContext || '';

  const prompt = `${MASTER_AGENT_SYSTEM}

---

## 평가 대상 시스템

### 문제 정보
- 제목: ${problem?.title || '시스템 아키텍처 설계'}
- 시나리오: ${problem?.scenario || ''}
- 미션: ${problem?.missions?.join(', ') || '없음'}

### 학생의 아키텍처 설계 (머메이드 코드 포함)
${architectureContext}

### 학생의 설명/답변
${userAnswer || '(답변 없음)'}

### 세션 맥락 (7단계 프로세스)
**고정 맥락 (아키텍처 + 첫 설명):**
${fixedContext || '(첫 평가)'}

**유동 맥락 (Q&A 요약):**
${dynamicContext || '(추가 대화 없음)'}

---

## 하위 에이전트 트리거 조건 (6대 기둥)
${agentTriggers}

---

## 작업 지시

1. 위 아키텍처를 분석하여 **Stateless**, **Decoupled Architecture** 원칙 준수 여부를 1차 판정해.
2. **모든 6개 에이전트**를 평가에 포함하되, 우선순위를 결정해.
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
      "agentId": "performanceOptimization",
      "priority": 2,
      "reason": "선택 이유"
    },
    {
      "agentId": "securityPrivacyCompliance",
      "priority": 3,
      "reason": "선택 이유"
    },
    {
      "agentId": "operationalExcellence",
      "priority": 4,
      "reason": "선택 이유"
    },
    {
      "agentId": "costOptimization",
      "priority": 5,
      "reason": "선택 이유"
    },
    {
      "agentId": "sustainability",
      "priority": 6,
      "reason": "선택 이유"
    }
  ],
  "contextUpdate": {
    "newFacts": ["새롭게 파악된 사실들"],
    "clarifiedPoints": ["명확해진 설계 의도"]
  }
}`;

  try {
    const response = await callOpenAI(prompt, { maxTokens: 1000, temperature: 0.3 });
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    throw new Error('Invalid JSON');
  } catch (error) {
    console.error('Master agent analysis error:', error);
    // Fallback: 6개 에이전트 모두 선택
    return {
      initialAssessment: {
        statelessCompliance: 'medium',
        decoupledCompliance: 'medium',
        overallMaturity: 'intermediate',
        summary: '분석 중 오류가 발생하여 기본 평가를 진행합니다.'
      },
      selectedAgents: [
        { agentId: 'reliability', priority: 1, reason: '기본 평가' },
        { agentId: 'performanceOptimization', priority: 2, reason: '기본 평가' },
        { agentId: 'securityPrivacyCompliance', priority: 3, reason: '기본 평가' },
        { agentId: 'operationalExcellence', priority: 4, reason: '기본 평가' },
        { agentId: 'costOptimization', priority: 5, reason: '기본 평가' },
        { agentId: 'sustainability', priority: 6, reason: '기본 평가' }
      ],
      contextUpdate: { newFacts: [], clarifiedPoints: [] }
    };
  }
}

// ============================================================================
// Step 2: 하위 에이전트 실행 (6대 지표 개별 평가)
// ============================================================================

/**
 * 하위 에이전트 평가 실행
 * - 5단계: 프롬프트 변환 - 핵심 원칙과 질문 전략 형태로 정제
 * - 6단계: 지표 정보 공통 사용 - 질문자와 평가자의 논리적 일관성
 */
async function runSubAgentEvaluation(agentConfig, problem, architectureContext, userAnswer, sessionContext = {}) {
  const evaluationAreasText = agentConfig.evaluationAreas.map((a, i) => `${i + 1}. ${a}`).join('\n');
  const questionStrategyText = agentConfig.questionStrategy.map((q, i) => `${i + 1}. ${q}`).join('\n');

  const prompt = `${agentConfig.systemRole}

---

## 평가 영역 (핵심 원칙 기반)
${evaluationAreasText}

## 질문 전략 (시나리오 기반 질문)
${questionStrategyText}

---

## 평가 대상

### 문제: ${problem?.title || '시스템 아키텍처 설계'}
시나리오: ${problem?.scenario || ''}

### 학생의 아키텍처 (매우 중요 - 반드시 이 내용만 기준으로 평가!)
${architectureContext}

### 학생의 답변
${userAnswer || '(답변 없음)'}

---

## ⚠️ 핵심 규칙 (반드시 준수!)

### 1. 실제 컴포넌트 기반 분석
- **학생이 실제로 배치한 컴포넌트만** 분석해야 함
- 위 '학생의 아키텍처'에 명시된 컴포넌트 목록을 정확히 파악할 것
- **없는 컴포넌트에 대해 질문하거나 평가하지 말 것**
- 예: 캐시(Redis)가 없으면 캐시 관련 질문 금지

### 2. 엄격한 채점 기준 (관대한 채점 금지!)
- **기본 점수는 30점에서 시작** (관대한 채점 절대 금지)
- 필수 컴포넌트 누락: -15점씩
- 연결이 비논리적: -10점씩
- 답변이 없거나 10자 미만: 최대 20점
- 답변이 질문과 무관하거나 이상함: 최대 30점
- 기술 용어 없이 막연한 답변: 최대 40점
- 70점 이상은 정말 잘한 경우에만 부여

### 3. 심층 질문 생성 규칙
- **학생이 실제로 배치한 컴포넌트**에 대해서만 질문
- 없는 컴포넌트(예: 캐시가 없는데 캐시 질문)는 절대 금지
- 학생의 설계에서 **부족한 부분**이나 **의도가 불명확한 연결**에 대해 질문

---

## 평가 기준 (4대 기준)

1. **설계 적합성 (Suitability):** 권장 모범 사례 충실도 - 필수 컴포넌트 포함 여부
2. **가시성 확보 (Data Collection):** 모니터링/로깅 컴포넌트 포함 여부
3. **강점 (Strengths):** 잘 설계된 부분 (있는 경우에만)
4. **리스크 (Difficulties):** 누락된 컴포넌트, 잘못된 연결, SPOF

---

## 출력 형식 (JSON만!)

{
  "pillarScore": 0-100,
  "actualComponents": ["학생이 실제로 배치한 컴포넌트 목록"],
  "missingCritical": ["이 Pillar 관점에서 누락된 중요 컴포넌트"],
  "evaluation": {
    "suitability": {
      "score": 0-100,
      "analysis": "분석 내용 - 실제 배치된 컴포넌트 기준 (2-3문장)"
    },
    "dataCollection": {
      "score": 0-100,
      "analysis": "분석 내용 (2-3문장)"
    },
    "strengths": {
      "score": 0-100,
      "analysis": "분석 내용 (2-3문장)",
      "highlights": ["실제로 잘한 부분만"]
    },
    "difficulties": {
      "score": 0-100,
      "analysis": "분석 내용 (2-3문장)",
      "concerns": ["실제 문제점"]
    }
  },
  "deepDiveQuestions": [
    "학생이 배치한 실제 컴포넌트에 대한 질문만 (없는 컴포넌트 질문 금지)"
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
      pillarScore: 30, // 오류 시 낮은 기본 점수
      actualComponents: [],
      missingCritical: ['평가 오류로 분석 불가'],
      evaluation: {
        suitability: { score: 30, analysis: '평가 오류로 분석할 수 없습니다.' },
        dataCollection: { score: 30, analysis: '평가 오류로 분석할 수 없습니다.' },
        strengths: { score: 30, analysis: '평가 오류로 분석할 수 없습니다.', highlights: [] },
        difficulties: { score: 30, analysis: '평가 오류로 분석할 수 없습니다.', concerns: ['평가 오류'] }
      },
      deepDiveQuestions: [],
      recommendations: { shortTerm: ['다시 시도해주세요'], longTerm: [] },
      summary: '평가 중 오류가 발생했습니다. 다시 시도해주세요.'
    };
  }
}

// ============================================================================
// Step 3: 마스터 에이전트 - 최종 통합 리포트
// ============================================================================

/**
 * 마스터 에이전트: 하위 에이전트 결과 종합
 * 6대 기둥 전체 평가 결과를 통합하여 최종 리포트 생성
 */
async function masterAgentSynthesize(initialAssessment, subAgentResults, problem) {
  const subResultsSummary = subAgentResults.map(r =>
    `### ${r.emoji} ${r.agentName} (${r.pillarScore}점)\n${r.summary}`
  ).join('\n\n');

  const allStrengths = subAgentResults.flatMap(r => r.evaluation?.strengths?.highlights || []);
  const allConcerns = subAgentResults.flatMap(r => r.evaluation?.difficulties?.concerns || []);

  // 하위 에이전트들의 평균 점수 계산
  const avgSubScore = Math.round(
    subAgentResults.reduce((sum, r) => sum + r.pillarScore, 0) / subAgentResults.length
  );

  // 누락된 중요 컴포넌트 수집
  const allMissingCritical = subAgentResults.flatMap(r => r.missingCritical || []);

  // 6대 기둥별 점수
  const pillarScores = subAgentResults.reduce((acc, r) => {
    acc[r.agentId] = r.pillarScore;
    return acc;
  }, {});

  const prompt = `${MASTER_AGENT_SYSTEM}

---

## 1차 진단 결과
- Stateless 준수: ${initialAssessment.statelessCompliance}
- Decoupled 준수: ${initialAssessment.decoupledCompliance}
- 전체 성숙도: ${initialAssessment.overallMaturity}
- 요약: ${initialAssessment.summary}

## 6대 기둥(Pillar) 평가 결과
${subResultsSummary}

## 6대 기둥 점수 요약
- Cost Optimization: ${pillarScores.costOptimization || 'N/A'}점
- Operational Excellence: ${pillarScores.operationalExcellence || 'N/A'}점
- Performance Optimization: ${pillarScores.performanceOptimization || 'N/A'}점
- Reliability: ${pillarScores.reliability || 'N/A'}점
- Security, Privacy & Compliance: ${pillarScores.securityPrivacyCompliance || 'N/A'}점
- Sustainability: ${pillarScores.sustainability || 'N/A'}점

## 하위 에이전트 평균 점수: ${avgSubScore}점

## 수집된 강점
${allStrengths.join(', ') || '없음'}

## 수집된 리스크
${allConcerns.join(', ') || '없음'}

## 누락된 중요 컴포넌트
${allMissingCritical.join(', ') || '없음'}

---

## ⚠️ 엄격한 최종 점수 산정 규칙 (반드시 준수!)

### 점수 기준
- **기본 점수는 하위 에이전트 평균(${avgSubScore}점)에서 시작**
- 누락된 중요 컴포넌트가 있으면: 컴포넌트당 -5점
- Stateless가 low면: -10점
- Decoupled가 low면: -10점
- 답변이 이상하거나 무관하면: -15점
- **최종 점수가 60점을 넘으려면 정말 잘해야 함**

### 등급 기준 (엄격하게!)
- excellent (80+): 모든 영역에서 우수, 누락 없음, 답변도 훌륭
- good (60-79): 대부분 양호, 약간의 누락이나 개선점
- needs-improvement (40-59): 여러 문제점, 중요 컴포넌트 누락
- poor (0-39): 심각한 설계 문제, 다수 누락, 답변 불량

---

## 최종 리포트 작성 (4대 기준)

1. **종합 적합성 (Overall Suitability):** Stateless, Decoupled Architecture 원칙 기준 클라우드 네이티브 설계 판정
2. **통합 가시성 (Unified Observability):** 6대 기둥 지표를 중앙에서 통합 수집/분석 가능한 구조인지
3. **핵심 강점 및 전략적 필요성:** 최대 강점과 가장 먼저 개선할 영역(Pillar) 추천
4. **복합 리스크 (Cross-pillar Difficulties):** 한 영역 최적화가 다른 영역에 미치는 부작용

---

## 출력 형식 (JSON만!)

{
  "totalScore": 0-100,
  "grade": "excellent/good/needs-improvement/poor",

  "pillarScores": {
    "costOptimization": ${pillarScores.costOptimization || 0},
    "operationalExcellence": ${pillarScores.operationalExcellence || 0},
    "performanceOptimization": ${pillarScores.performanceOptimization || 0},
    "reliability": ${pillarScores.reliability || 0},
    "securityPrivacyCompliance": ${pillarScores.securityPrivacyCompliance || 0},
    "sustainability": ${pillarScores.sustainability || 0}
  },

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
      pillarScores,
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
 * 7단계 프로세스 흐름:
 * 1. 머메이드 변환 (이미 완료된 상태로 전달됨)
 * 2. 상세 설명 (userAnswer에 포함)
 * 3. 질문 및 꼬리질문 (deepDiveQnA에 포함)
 * 4. 6대 지표 개별 평가 (하위 에이전트 병렬 실행)
 * 5. 프롬프트 변환 (각 에이전트의 systemRole에 반영)
 * 6. 지표 정보 공통 사용 (questionStrategy와 evaluationAreas 일관성)
 * 7. 맥락 유지 (sessionContext 전달)
 */
export async function evaluateWithMasterAgent(
  problem,
  architectureContext,
  generatedQuestion,
  userAnswer,
  deepDiveQnA,
  sessionContext = {}
) {
  // 심화 답변 포함
  const deepDiveArray = Array.isArray(deepDiveQnA) ? deepDiveQnA : [];
  const deepDiveText = deepDiveArray.length > 0
    ? deepDiveArray.map((item, idx) =>
        `[심화 ${idx + 1}] Q: ${item.question}\nA: ${item.answer || '(답변 없음)'}`
      ).join('\n\n')
    : '';

  const combinedAnswer = `${userAnswer || ''}\n\n${deepDiveText}`.trim();

  console.log('🎯 Step 1: Master Agent analyzing architecture (7단계 프로세스 시작)...');
  const startTime = Date.now();

  // Step 1: 마스터 에이전트 1차 분석
  const masterAnalysis = await masterAgentAnalyze(problem, architectureContext, combinedAnswer, sessionContext);
  console.log(`✅ Master analysis complete. Selected agents: ${masterAnalysis.selectedAgents.map(a => a.agentId).join(', ')}`);

  // Step 2: 선택된 하위 에이전트들 병렬 실행 (4단계: 6대 지표 개별 평가)
  console.log('🔄 Step 2: Running 6 pillar agents in parallel (4단계: 병렬 평가)...');
  const selectedAgentConfigs = masterAnalysis.selectedAgents
    .map(sa => SUB_AGENTS[sa.agentId])
    .filter(Boolean);

  const subAgentPromises = selectedAgentConfigs.map(agentConfig =>
    runSubAgentEvaluation(agentConfig, problem, architectureContext, combinedAnswer, sessionContext)
  );

  const subAgentResults = await Promise.all(subAgentPromises);
  console.log(`✅ 6 Pillar evaluations complete. (${subAgentResults.length} agents)`);

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

    // 6대 기둥 점수 (새로운 필드)
    pillarScores: finalReport.pillarScores || mapToPillarScores(subAgentResults),

    // 마스터 에이전트 전용 결과
    masterAgentEvaluation: {
      enabled: true,
      processVersion: '7-step',
      initialAssessment: masterAnalysis.initialAssessment,
      selectedAgents: masterAnalysis.selectedAgents,
      contextUpdate: masterAnalysis.contextUpdate,
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
      case 'performanceOptimization':
        nfrScores.performance = { score: result.pillarScore, feedback: result.summary };
        nfrScores.scalability = { score: result.pillarScore, feedback: result.summary };
        break;
      case 'securityPrivacyCompliance':
        nfrScores.consistency = { score: result.pillarScore, feedback: result.summary };
        break;
      case 'operationalExcellence':
        // operational은 전반적인 운영 성숙도에 영향
        break;
      case 'costOptimization':
        // cost는 별도 표시
        break;
      case 'sustainability':
        // sustainability는 별도 표시
        break;
    }
  });

  return nfrScores;
}

/**
 * 하위 에이전트 결과를 6대 기둥 점수로 매핑
 */
function mapToPillarScores(subAgentResults) {
  const pillarScores = {
    costOptimization: 0,
    operationalExcellence: 0,
    performanceOptimization: 0,
    reliability: 0,
    securityPrivacyCompliance: 0,
    sustainability: 0
  };

  subAgentResults.forEach(result => {
    if (pillarScores.hasOwnProperty(result.agentId)) {
      pillarScores[result.agentId] = result.pillarScore;
    }
  });

  return pillarScores;
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
 * 사용 가능한 하위 에이전트 목록 (6대 기둥)
 */
export function getAvailableSubAgents() {
  return Object.values(SUB_AGENTS).map(a => ({
    id: a.id,
    name: a.name,
    emoji: a.emoji,
    trigger: a.trigger,
    questionStrategy: a.questionStrategy
  }));
}

/**
 * 질문 전략 기반 꼬리질문 생성 (3단계 프로세스용)
 */
export function getQuestionsByPillar(pillarId) {
  const agent = SUB_AGENTS[pillarId];
  if (!agent) return [];
  return agent.questionStrategy.map((q, idx) => ({
    category: agent.name,
    question: q,
    intent: `${agent.name} 관점에서 설계 의도 확인`
  }));
}

/**
 * 모든 기둥의 질문 전략 수집
 */
export function getAllQuestionStrategies() {
  return Object.values(SUB_AGENTS).flatMap(agent =>
    agent.questionStrategy.map(q => ({
      pillarId: agent.id,
      pillarName: agent.name,
      emoji: agent.emoji,
      question: q
    }))
  );
}

// ============================================================================
// 기존 API 호환 re-export
// ============================================================================

export { fetchProblems } from './architectureApiFast.js';
export { generateDeepDiveQuestion, generateArchitectureAnalysisQuestions, generateEvaluationQuestion, sendChatMessage } from './architectureApiFast.js';
