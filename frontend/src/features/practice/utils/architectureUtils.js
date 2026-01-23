/**
 * Architecture Practice Utility Functions
 */

/**
 * 문제 데이터를 앱에서 사용할 형식으로 변환
 */
export function transformProblems(data) {
  const componentTypeMap = {
    // Compute & Entry
    'entry': 'gateway',
    'compute': 'server',
    'server': 'server',
    'gateway': 'gateway',
    'loadbalancer': 'loadbalancer',
    // Storage & Search
    'storage': 'storage',
    'db': 'rdbms',
    'rdbms': 'rdbms',
    'nosql': 'nosql',
    'cache': 'cache',
    'redis': 'cache',
    'search': 'search',
    's3': 'storage',
    // Messaging
    'message_queue': 'broker',
    'kafka': 'broker',
    'broker': 'broker',
    'eventbus': 'eventbus',
    'pubsub': 'eventbus',
    // Observability
    'monitoring': 'monitoring',
    'logging': 'logging',
    'cicd': 'cicd',
    // Legacy mappings
    'network': 'monitoring',
    'cdn': 'storage',
    'external': 'gateway'
  };

  return data.map((item, index) => {
    let difficulty = 'easy';
    let level = '초급';
    if (index >= 7) {
      difficulty = 'hard';
      level = '고급';
    } else if (index >= 4) {
      difficulty = 'medium';
      level = '중급';
    }

    const requirementsArray = item.requirements
      .split(/[,،]/)
      .map(req => req.trim())
      .filter(req => req.length > 0);

    let followUpQuestion = '';
    if (item.question_topics && item.question_topics.length > 0) {
      const topic = item.question_topics[0];
      followUpQuestion = `${topic.topic}에 대해 설명해주세요. (키워드: ${topic.keywords.join(', ')})`;
    }

    const expectedComponents = item.key_components.map(comp =>
      componentTypeMap[comp.type] || comp.type
    );

    return {
      level,
      title: item.title,
      description: item.requirements,
      difficulty,
      requirements: requirementsArray,
      followUpQuestion,
      expectedComponents,
      questionTopics: item.question_topics,
      referenceMermaid: item.reference_mermaid,
      referenceConcept: item.reference_concept,
      evaluationRubric: item.evaluation_rubric
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
  context += `요구사항: ${problem.requirements.join(', ')}\n`;

  if (problem.questionTopics && problem.questionTopics.length > 0) {
    context += `\n주요 토픽:\n`;
    problem.questionTopics.forEach(topic => {
      context += `- ${topic.topic}: ${topic.keywords.join(', ')}\n`;
    });
  }

  if (problem.referenceConcept) {
    context += `\n고려해야 할 개념들: ${Object.keys(problem.referenceConcept).join(', ')}`;
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
 * Mock 평가 데이터 (API 실패 시 fallback)
 */
export const mockEvaluations = {
  0: {
    score: 85,
    grade: "good",
    summary: "기본적인 3-Tier 아키텍처 구조를 잘 이해하고 계시네요. 특히 CDN을 적절히 배치한 점이 훌륭합니다.",
    strengths: ["Client와 API의 분리", "DB 연결의 명확성", "정적 리소스 처리를 위한 CDN 배치"],
    weaknesses: ["API 서버의 이중화 부족"],
    suggestions: ["서버 장애 대비를 위해 Load Balancer 도입을 고려해보세요."]
  },
  1: {
    score: 92,
    grade: "excellent",
    summary: "트래픽 분산과 캐싱 전략이 매우 훌륭합니다. 블랙프라이데이와 같은 상황에서도 안정적으로 동작할 것 같네요.",
    strengths: ["Redis 캐시를 통한 DB 부하 감소 전략", "Load Balancer를 이용한 Scale-out 구조"],
    weaknesses: ["비동기 처리에 대한 구체적 흐름 미흡"],
    suggestions: ["주문 처리와 결제 알림 등을 분리하기 위해 Message Queue를 더 적극적으로 활용해보세요."]
  },
  2: {
    score: 78,
    grade: "needs-improvement",
    summary: "글로벌 서비스를 위한 기본적인 컴포넌트는 갖추었으나, 실시간성 보장을 위한 구조가 다소 아쉽습니다.",
    strengths: ["글로벌 CDN 활용 의도", "데이터베이스 분리"],
    weaknesses: ["UDP/TCP 서버 분리 미고려", "지역별 엣지 서버 배치 전략 부재"],
    suggestions: ["실시간 게임 서버는 상태(Stateful) 관리가 중요하므로 Redis Session Store 활용을 구체화해보세요."]
  }
};
