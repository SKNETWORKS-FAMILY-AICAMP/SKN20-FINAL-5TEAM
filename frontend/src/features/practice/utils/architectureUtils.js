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

    // 컴포넌트 타입 배열 (기존 호환성)
    const expectedComponents = item.key_components.map(comp =>
      componentTypeMap[comp.type] || comp.type
    );

    // 컴포넌트 이름과 타입 모두 포함 (평가용)
    const keyComponents = item.key_components.map(comp => ({
      name: comp.name,
      type: componentTypeMap[comp.type] || comp.type
    }));

    return {
      level,
      title: item.title,
      description: item.requirements,
      difficulty,
      requirements: requirementsArray,
      followUpQuestion,
      expectedComponents,
      keyComponents, // 이름과 타입 모두 포함
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
 * 문제 데이터 기반 동적 Mock 평가 생성 (API 실패 시 fallback)
 * @param {Object} problem - 문제 데이터
 * @param {Array} components - 학생이 배치한 컴포넌트
 * @returns {Object} 평가 결과 객체
 */
export function generateMockEvaluation(problem, components = []) {
  const difficulty = problem?.difficulty || 'medium';
  const keyComponents = problem?.keyComponents || [];
  const referenceConcept = problem?.referenceConcept || {};
  const rubric = problem?.evaluationRubric || {};

  // 난이도별 기본 점수 범위
  const scoreRanges = {
    easy: { min: 70, max: 85 },
    medium: { min: 65, max: 80 },
    hard: { min: 60, max: 75 }
  };
  const range = scoreRanges[difficulty] || scoreRanges.medium;
  const score = Math.floor(Math.random() * (range.max - range.min + 1)) + range.min;

  // 등급 결정
  let grade = 'needs-improvement';
  if (score >= 90) grade = 'excellent';
  else if (score >= 70) grade = 'good';
  else if (score < 50) grade = 'poor';

  // 핵심 컴포넌트 기반 강점/약점 생성
  const componentTypes = components.map(c => c.type);
  const includedComponents = keyComponents.filter(kc => componentTypes.includes(kc.type));
  const missingComponents = keyComponents.filter(kc => !componentTypes.includes(kc.type));

  // 핵심 개념 기반 제안 생성
  const concepts = Object.keys(referenceConcept);
  const suggestions = concepts.slice(0, 2).map(concept =>
    `${concept} 관련 설계를 더 구체화해보세요: ${referenceConcept[concept]}`
  );

  // 평가 기준 기반 피드백 생성
  const systemArchMetrics = rubric.system_architecture || [];
  const interviewMetrics = rubric.interview_score || [];

  const systemArchitectureScores = {};
  systemArchMetrics.forEach(metric => {
    systemArchitectureScores[metric.metric] = {
      score: Math.floor(Math.random() * 20) + 60,
      feedback: `${metric.description} - API 연결 문제로 상세 분석이 제한됩니다.`
    };
  });

  const interviewScores = {};
  interviewMetrics.forEach(metric => {
    interviewScores[metric.metric] = {
      score: Math.floor(Math.random() * 20) + 60,
      feedback: `${metric.description} - API 연결 문제로 상세 분석이 제한됩니다.`
    };
  });

  return {
    score,
    grade,
    componentCoverage: {
      included: includedComponents.map(c => c.name),
      missing: missingComponents.map(c => c.name),
      extra: []
    },
    systemArchitectureScores: Object.keys(systemArchitectureScores).length > 0
      ? systemArchitectureScores
      : {
          "구조적 완성도": { score: 70, feedback: "기본적인 구조는 갖추었습니다." },
          "확장성": { score: 65, feedback: "확장성 측면에서 추가 고려가 필요합니다." },
          "가용성/복원력": { score: 68, feedback: "장애 대응 전략이 필요합니다." }
        },
    interviewScores: Object.keys(interviewScores).length > 0
      ? interviewScores
      : {
          "논리적 일관성": { score: 70, feedback: "일관된 설명이 필요합니다." },
          "근거의 타당성": { score: 68, feedback: "더 구체적인 근거가 필요합니다." },
          "전달력": { score: 72, feedback: "핵심 키워드 사용을 권장합니다." }
        },
    conceptUnderstanding: {
      demonstrated: concepts.slice(0, 1),
      needsImprovement: concepts.slice(1)
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
    summary: "API 연결 문제로 기본 평가를 제공합니다. 아키텍처 설계의 기본 구조는 갖추었습니다.",
    strengths: ["기본 컴포넌트 배치", "구조적 이해"],
    weaknesses: ["상세 연결 관계 확인 필요"],
    suggestions: ["API 연결 후 재평가를 권장합니다."]
  }
};
