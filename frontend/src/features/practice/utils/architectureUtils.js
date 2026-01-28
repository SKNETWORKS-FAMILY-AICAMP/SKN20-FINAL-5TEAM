/**
 * Architecture Practice Utility Functions
 */

/**
 * 문제 데이터를 앱에서 사용할 형식으로 변환
 * 새로운 architecture.json 구조에 맞춤
 */
export function transformProblems(data) {
  // 컴포넌트 이름을 팔레트 타입으로 매핑
  const componentNameToType = {
    // Server & Gateway
    'web server': 'server',
    'server': 'server',
    'api server': 'server',
    'feed service': 'server',
    'search api': 'server',
    'location api': 'server',
    'gateway': 'gateway',
    'websocket gateway': 'gateway',
    'load balancer': 'loadbalancer',
    'loadbalancer': 'loadbalancer',
    // Storage
    'rdbms': 'rdbms',
    'database': 'rdbms',
    'db': 'rdbms',
    'history db': 'rdbms',
    'history db (rdbms)': 'rdbms',
    'object storage': 'storage',
    'object storage (s3)': 'storage',
    's3': 'storage',
    'storage': 'storage',
    // Cache & Search
    'cache': 'cache',
    'cache (redis)': 'cache',
    'redis': 'cache',
    'redis (distributed lock/atomic)': 'cache',
    'newsfeed cache': 'cache',
    'newsfeed cache (redis)': 'cache',
    'in-memory store': 'cache',
    'in-memory store (redis geo)': 'cache',
    'search engine': 'search',
    'in-memory search engine': 'search',
    'in-memory search engine (trie/redis/es)': 'search',
    'elasticsearch': 'search',
    // Messaging
    'message queue': 'broker',
    'message queue (kafka/rabbitmq)': 'broker',
    'kafka': 'broker',
    'rabbitmq': 'broker',
    'task queue': 'broker',
    'pub/sub': 'eventbus',
    'pub/sub (redis)': 'eventbus',
    'pubsub': 'eventbus',
    // Workers
    'worker': 'server',
    'notification worker': 'server',
    'cleanup worker': 'server',
    'crawler worker': 'server',
    // Others
    'cdn': 'storage',
    'client': 'user',
    'user': 'user',
    'bus': 'user',
    'bloom filter': 'cache',
    'bloom filter (deduplicator)': 'cache',
    'deduplicator': 'cache'
  };

  /**
   * 컴포넌트 이름을 팔레트 타입으로 변환
   */
  const getComponentType = (name) => {
    const lowerName = name.toLowerCase().trim();
    return componentNameToType[lowerName] || 'server';
  };

  return data.map((item) => {
    // engineering_spec을 요구사항 배열로 변환
    const requirementsArray = [];
    if (item.engineering_spec) {
      Object.entries(item.engineering_spec).forEach(([key, value]) => {
        requirementsArray.push(`${key}: ${value}`);
      });
    }

    // mission 배열 추가
    const missions = item.mission || [];

    // rubric_functional에서 필수 컴포넌트 추출
    const rubricFunctional = item.rubric_functional || {};
    const requiredComponentNames = rubricFunctional.required_components || [];
    const requiredFlows = rubricFunctional.required_flows || [];

    // 컴포넌트 이름과 타입 매핑
    const keyComponents = requiredComponentNames.map(name => ({
      name: name,
      type: getComponentType(name)
    }));

    // 타입만 추출 (기존 호환성)
    const expectedComponents = keyComponents.map(c => c.type);

    // rubric_non_functional에서 평가 토픽 추출
    const rubricNonFunctional = item.rubric_non_functional || [];
    const questionTopics = rubricNonFunctional.map(nfr => ({
      topic: nfr.category,
      keywords: [nfr.question_intent],
      modelAnswer: nfr.model_answer
    }));

    // 후속 질문 생성
    let followUpQuestion = '';
    if (rubricNonFunctional.length > 0) {
      const firstNfr = rubricNonFunctional[0];
      followUpQuestion = `${firstNfr.category}에 대해 설명해주세요. (${firstNfr.question_intent})`;
    }

    return {
      problemId: item.problem_id,
      title: item.title,
      scenario: item.scenario,
      description: item.scenario, // 기존 호환성
      requirements: requirementsArray,
      missions: missions,
      engineeringSpec: item.engineering_spec,
      followUpQuestion,
      expectedComponents,
      keyComponents,
      requiredFlows, // 필수 연결 관계
      questionTopics,
      rubricFunctional,
      rubricNonFunctional
    };
  });
}

/**
 * 메시지 타입 감지
 */
export function detectMessageType(message) {
  const lowerMsg = message.toLowerCase();

  if (lowerMsg.includes('요구사항') || lowerMsg.includes('requirement') ||
      lowerMsg.includes('p95') || lowerMsg.includes('지연') || lowerMsg.includes('latency') ||
      lowerMsg.includes('트래픽') || lowerMsg.includes('성능')) {
    return 'requirement';
  }

  if (lowerMsg.includes('캐시') || lowerMsg.includes('cache') ||
      lowerMsg.includes('데이터베이스') || lowerMsg.includes('db') ||
      lowerMsg.includes('로드밸런서') || lowerMsg.includes('큐') ||
      lowerMsg.includes('서버') || lowerMsg.includes('스토리지')) {
    return 'component';
  }

  if (lowerMsg.includes('트레이드오프') || lowerMsg.includes('trade-off') ||
      lowerMsg.includes('장단점') || lowerMsg.includes('비교') ||
      lowerMsg.includes('vs') || lowerMsg.includes('선택')) {
    return 'tradeoff';
  }

  if (lowerMsg.includes('확장') || lowerMsg.includes('scale') ||
      lowerMsg.includes('샤딩') || lowerMsg.includes('파티션')) {
    return 'scaling';
  }

  return 'general';
}

/**
 * 중요한 연결인지 확인 (Deep Dive 질문 트리거용)
 */
export function isImportantConnection(fromType, toType, questionedTypes, questionCount) {
  const importantConnections = [
    // Compute & Entry flows
    ['user', 'loadbalancer'],
    ['user', 'gateway'],
    ['loadbalancer', 'gateway'],
    ['loadbalancer', 'server'],
    ['gateway', 'server'],
    // Server to Storage connections
    ['server', 'rdbms'],
    ['server', 'nosql'],
    ['server', 'cache'],
    ['server', 'storage'],
    ['server', 'search'],
    ['cache', 'rdbms'],
    ['cache', 'nosql'],
    // Messaging connections
    ['server', 'broker'],
    ['broker', 'server'],
    ['server', 'eventbus'],
    ['eventbus', 'server'],
    // Observability connections
    ['server', 'monitoring'],
    ['server', 'logging'],
  ];

  // Check if already questioned (bidirectional)
  const key1 = `${fromType}-${toType}`;
  const key2 = `${toType}-${fromType}`;
  if (questionedTypes.has(key1) || questionedTypes.has(key2)) return false;

  // Maximum 3 questions per session
  if (questionCount >= 3) return false;

  // Check if it's an important connection
  return importantConnections.some(([a, b]) =>
    (fromType === a && toType === b) || (fromType === b && toType === a)
  );
}

/**
 * 채팅 컨텍스트 생성
 */
export function buildChatContext(problem) {
  if (!problem) return '';

  let context = `문제: ${problem.title}\n`;
  context += `시나리오: ${problem.scenario || ''}\n`;

  if (problem.missions && problem.missions.length > 0) {
    context += `\n미션:\n`;
    problem.missions.forEach(mission => {
      context += `- ${mission}\n`;
    });
  }

  if (problem.engineeringSpec) {
    context += `\n기술 요구사항:\n`;
    Object.entries(problem.engineeringSpec).forEach(([key, value]) => {
      context += `- ${key}: ${value}\n`;
    });
  }

  if (problem.questionTopics && problem.questionTopics.length > 0) {
    context += `\n주요 토픽:\n`;
    problem.questionTopics.forEach(topic => {
      const keywords = topic.keywords?.join(', ') || topic.modelAnswer || '';
      context += `- ${topic.topic}: ${keywords}\n`;
    });
  }

  return context;
}

/**
 * 아키텍처 컨텍스트 생성 (평가용)
 */
export function buildArchitectureContext(components, connections, mermaidCode) {
  if (components.length === 0) {
    return '배치된 컴포넌트가 없습니다.';
  }

  let context = `배치된 컴포넌트 (${components.length}개):\n`;
  components.forEach(comp => {
    context += `- ${comp.text} (${comp.type})\n`;
  });

  if (connections.length > 0) {
    context += `\n연결 (${connections.length}개):\n`;
    connections.forEach(conn => {
      const from = components.find(c => c.id === conn.from);
      const to = components.find(c => c.id === conn.to);
      if (from && to) {
        context += `- ${from.text} → ${to.text}\n`;
      }
    });
  }

  context += `\nMermaid 코드:\n${mermaidCode}`;

  return context;
}

/**
 * Mermaid 코드 생성
 */
export function generateMermaidCode(components, connections) {
  if (components.length === 0) {
    return 'graph LR\n    %% 컴포넌트를 배치하고 연결하세요!';
  }

  let code = 'graph LR\n';

  components.forEach(comp => {
    const label = comp.text.replace(/[^\w\s가-힣]/g, '');
    code += `    ${comp.id}["${label}"]\n`;
  });

  code += '\n';
  connections.forEach(conn => {
    code += `    ${conn.from} --> ${conn.to}\n`;
  });

  code += '\n';
  const styleMap = {
    // Compute & Entry
    'user': 'fill:#ff4785,stroke:#ff1744,stroke-width:3px,color:#fff',
    'loadbalancer': 'fill:#26c6da,stroke:#00acc1,stroke-width:3px,color:#0a0e27',
    'gateway': 'fill:#64b5f6,stroke:#2196f3,stroke-width:3px,color:#fff',
    'server': 'fill:#ab47bc,stroke:#8e24aa,stroke-width:3px,color:#fff',
    // Storage & Search
    'rdbms': 'fill:#00ff9d,stroke:#00e676,stroke-width:3px,color:#0a0e27',
    'nosql': 'fill:#4db6ac,stroke:#26a69a,stroke-width:3px,color:#0a0e27',
    'cache': 'fill:#ffc107,stroke:#ffa000,stroke-width:3px,color:#0a0e27',
    'search': 'fill:#7c4dff,stroke:#651fff,stroke-width:3px,color:#fff',
    'storage': 'fill:#ff7043,stroke:#f4511e,stroke-width:3px,color:#fff',
    // Messaging
    'broker': 'fill:#ff8a65,stroke:#ff5722,stroke-width:3px,color:#fff',
    'eventbus': 'fill:#ba68c8,stroke:#ab47bc,stroke-width:3px,color:#fff',
    // Observability
    'monitoring': 'fill:#66bb6a,stroke:#43a047,stroke-width:3px,color:#fff',
    'logging': 'fill:#78909c,stroke:#607d8b,stroke-width:3px,color:#fff',
    'cicd': 'fill:#42a5f5,stroke:#1e88e5,stroke-width:3px,color:#fff'
  };

  components.forEach(comp => {
    if (styleMap[comp.type]) {
      code += `    style ${comp.id} ${styleMap[comp.type]}\n`;
    }
  });

  return code;
}

/**
 * 문제 데이터 기반 동적 Mock 평가 생성 (API 실패 시 fallback)
 * 5가지 NFR 기반 평가 형식으로 반환
 * @param {Object} problem - 문제 데이터
 * @param {Array} components - 학생이 배치한 컴포넌트
 * @returns {Object} 평가 결과 객체
 */
export function generateMockEvaluation(problem, components = []) {
  const keyComponents = problem?.keyComponents || [];
  const rubricNonFunctional = problem?.rubricNonFunctional || [];
  const missions = problem?.missions || [];

  // 컴포넌트 배치에 따른 점수 계산 (0-100 전체 범위)
  const baseScore = 50;
  const componentBonus = Math.min(components.length * 5, 30); // 최대 30점
  const score = baseScore + componentBonus + Math.floor(Math.random() * 20);

  // 등급 결정
  let grade = 'needs-improvement';
  if (score >= 90) grade = 'excellent';
  else if (score >= 70) grade = 'good';
  else if (score < 50) grade = 'poor';

  // 핵심 컴포넌트 기반 강점/약점 생성
  const componentTypes = components.map(c => c.type);
  const includedComponents = keyComponents.filter(kc => componentTypes.includes(kc.type));
  const missingComponents = keyComponents.filter(kc => !componentTypes.includes(kc.type));

  // NFR 기반 제안 생성 (새 데이터 구조)
  const suggestions = rubricNonFunctional.length > 0
    ? rubricNonFunctional.slice(0, 2).map(nfr =>
        `[${nfr.category}] ${nfr.question_intent}: ${nfr.model_answer?.substring(0, 100) || ''}...`
      )
    : missions.slice(0, 2).map(m => m);

  // 컴포넌트 타입 기반으로 NFR 체크리스트 자동 판정
  const hasLoadBalancer = componentTypes.includes('loadbalancer');
  const hasCache = componentTypes.includes('cache');
  const hasBroker = componentTypes.includes('broker') || componentTypes.includes('eventbus');
  const hasRdbms = componentTypes.includes('rdbms');
  const hasNosql = componentTypes.includes('nosql');
  const hasStorage = componentTypes.includes('storage');
  const hasMultipleServers = components.filter(c => c.type === 'server').length > 1;

  // NFR 점수 생성 (컴포넌트 기반)
  const generateNfrScore = (base, hasFeatures = []) => {
    const bonus = hasFeatures.filter(Boolean).length * 10;
    return Math.min(100, base + bonus + Math.floor(Math.random() * 10));
  };

  return {
    score,
    grade,
    componentCoverage: {
      included: includedComponents.map(c => c.name),
      missing: missingComponents.map(c => c.name),
      extra: []
    },
    nfrScores: {
      scalability: {
        score: generateNfrScore(50, [hasLoadBalancer, hasMultipleServers, hasNosql]),
        feedback: hasLoadBalancer
          ? "Load Balancer가 포함되어 수평 확장 기반이 마련되었습니다. API 연결 후 상세 분석이 가능합니다."
          : "수평 확장을 위한 Load Balancer 추가를 고려해보세요.",
        checklist: {
          scaleOut: hasMultipleServers || hasLoadBalancer,
          loadBalancing: hasLoadBalancer,
          sharding: hasNosql
        }
      },
      availability: {
        score: generateNfrScore(50, [hasLoadBalancer, hasMultipleServers]),
        feedback: hasMultipleServers
          ? "다중 서버 구성으로 가용성 기반이 마련되었습니다."
          : "단일 장애점(SPOF) 제거를 위해 서버 다중화를 고려해보세요.",
        checklist: {
          noSPOF: hasMultipleServers,
          replication: hasRdbms || hasNosql,
          failover: hasLoadBalancer
        }
      },
      performance: {
        score: generateNfrScore(50, [hasCache, hasBroker]),
        feedback: hasCache
          ? "캐시가 포함되어 성능 최적화 기반이 마련되었습니다."
          : "자주 조회되는 데이터를 위한 캐시 레이어 추가를 권장합니다.",
        checklist: {
          caching: hasCache,
          asyncProcessing: hasBroker,
          indexing: hasRdbms
        }
      },
      consistency: {
        score: generateNfrScore(55, [hasRdbms]),
        feedback: hasRdbms
          ? "RDBMS를 통해 ACID 트랜잭션 지원이 가능합니다."
          : "데이터 일관성이 중요한 경우 RDBMS 사용을 고려해보세요.",
        checklist: {
          acidTransaction: hasRdbms,
          lockingStrategy: hasRdbms,
          eventualConsistency: hasNosql || hasCache
        }
      },
      reliability: {
        score: generateNfrScore(55, [hasStorage, hasRdbms, hasNosql]),
        feedback: (hasStorage || hasRdbms || hasNosql)
          ? "영구 저장소가 포함되어 데이터 지속성이 확보되었습니다."
          : "데이터 영구 저장을 위한 스토리지 또는 데이터베이스가 필요합니다.",
        checklist: {
          dataPersistence: hasStorage || hasRdbms || hasNosql,
          idempotency: hasBroker
        }
      }
    },
    interviewScore: {
      score: Math.floor(Math.random() * 20) + 60,
      feedback: "API 연결 문제로 면접 답변에 대한 상세 분석이 제한됩니다. 재시도해주세요."
    },
    conceptUnderstanding: {
      demonstrated: rubricNonFunctional.slice(0, 1).map(r => r.category),
      needsImprovement: rubricNonFunctional.slice(1).map(r => r.category)
    },
    summary: `${problem?.title || '시스템 아키텍처'}에 대한 기본적인 이해를 보여주셨습니다. API 연결 문제로 상세 평가가 제한되어 기본 피드백을 제공합니다. ${missingComponents.length > 0 ? `누락된 핵심 컴포넌트: ${missingComponents.map(c => c.name).join(', ')}` : ''}`,
    strengths: includedComponents.length > 0
      ? includedComponents.slice(0, 2).map(c => `${c.name} 컴포넌트 포함`)
      : ["기본 아키텍처 구조 이해", "컴포넌트 배치 시도"],
    weaknesses: missingComponents.length > 0
      ? missingComponents.slice(0, 2).map(c => `${c.name} 컴포넌트 누락`)
      : ["세부 연결 관계 보완 필요"],
    suggestions: suggestions.length > 0
      ? suggestions
      : ["아키텍처 문서를 참고하여 핵심 컴포넌트를 추가해보세요."]
  };
}

/**
 * 레거시 호환용 Mock 평가 데이터
 * @deprecated generateMockEvaluation 사용 권장
 */
export const mockEvaluations = {
  0: {
    score: 75,
    grade: "good",
    nfrScores: {
      scalability: { score: 70, feedback: "기본 확장성 고려됨", checklist: { scaleOut: false, loadBalancing: false, sharding: false } },
      availability: { score: 65, feedback: "가용성 개선 필요", checklist: { noSPOF: false, replication: false, failover: false } },
      performance: { score: 70, feedback: "성능 최적화 고려 필요", checklist: { caching: false, asyncProcessing: false, indexing: false } },
      consistency: { score: 75, feedback: "일관성 기본 구조 포함", checklist: { acidTransaction: false, lockingStrategy: false, eventualConsistency: false } },
      reliability: { score: 70, feedback: "신뢰성 개선 필요", checklist: { dataPersistence: false, idempotency: false } }
    },
    interviewScore: { score: 70, feedback: "API 연결 후 상세 평가 가능" },
    summary: "API 연결 문제로 기본 평가를 제공합니다. 아키텍처 설계의 기본 구조는 갖추었습니다.",
    strengths: ["기본 컴포넌트 배치", "구조적 이해"],
    weaknesses: ["상세 연결 관계 확인 필요"],
    suggestions: ["API 연결 후 재평가를 권장합니다."]
  }
};
