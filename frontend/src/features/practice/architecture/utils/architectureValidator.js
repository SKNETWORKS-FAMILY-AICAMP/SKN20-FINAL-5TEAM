/**
 * Architecture Validation Preprocessing Logic
 * 3-단계 검증 시스템 구현
 */

/**
 * 컴포넌트 이름을 표준 타입으로 정규화
 */
const COMPONENT_NAME_TO_TYPE = {
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
 * 컴포넌트 이름을 타입으로 변환
 */
function normalizeComponentType(name) {
  const lowerName = name.toLowerCase().trim();
  return COMPONENT_NAME_TO_TYPE[lowerName] || 'server';
}

/**
 * 두 컴포넌트가 같은 타입인지 비교 (정규화된 타입 기준)
 */
function isSameComponentType(submittedName, requiredName) {
  const submittedType = normalizeComponentType(submittedName);
  const requiredType = normalizeComponentType(requiredName);
  return submittedType === requiredType;
}

/**
 * 고립된 컴포넌트 찾기 (어떤 연결도 없는 컴포넌트)
 */
function findIsolatedComponents(components, connections) {
  if (!components || components.length === 0) return [];

  const connectedIds = new Set();

  // 모든 연결에 참여한 컴포넌트 ID 수집
  if (connections && connections.length > 0) {
    connections.forEach(conn => {
      connectedIds.add(conn.from);
      connectedIds.add(conn.to);
    });
  }

  // 연결되지 않은 컴포넌트 필터링
  return components
    .filter(comp => !connectedIds.has(comp.id))
    .map(comp => ({
      id: comp.id,
      name: comp.text,
      type: comp.type
    }));
}

/**
 * 필수 컴포넌트 충족도 계산
 */
function calculateComponentFulfillment(submittedComponents, requiredComponentNames) {
  if (!requiredComponentNames || requiredComponentNames.length === 0) {
    return { rate: 100, matched: [], missing: [] };
  }

  const matched = [];
  const missing = [];

  requiredComponentNames.forEach(requiredName => {
    const found = submittedComponents.some(submitted =>
      isSameComponentType(submitted.text, requiredName)
    );

    if (found) {
      matched.push(requiredName);
    } else {
      missing.push(requiredName);
    }
  });

  const rate = (matched.length / requiredComponentNames.length) * 100;

  return {
    rate: Math.round(rate),
    matched,
    missing,
    totalRequired: requiredComponentNames.length,
    matchedCount: matched.length
  };
}

/**
 * 필수 연결(Required Flows) 충족 확인
 */
function checkRequiredFlows(submittedComponents, submittedConnections, requiredFlows) {
  if (!requiredFlows || requiredFlows.length === 0) {
    return { fulfilled: [], missing: [] };
  }

  const fulfilled = [];
  const missing = [];

  requiredFlows.forEach(requiredFlow => {
    // 필수 Flow의 from/to 컴포넌트 찾기
    const fromFound = submittedComponents.find(comp =>
      isSameComponentType(comp.text, requiredFlow.from)
    );

    const toFound = submittedComponents.find(comp =>
      isSameComponentType(comp.text, requiredFlow.to)
    );

    // 두 컴포넌트가 모두 존재하고 연결되어 있는지 확인
    if (fromFound && toFound) {
      const connectionExists = submittedConnections?.some(conn =>
        conn.from === fromFound.id && conn.to === toFound.id
      );

      if (connectionExists) {
        fulfilled.push({
          from: requiredFlow.from,
          to: requiredFlow.to,
          reason: requiredFlow.reason
        });
      } else {
        missing.push({
          from: requiredFlow.from,
          to: requiredFlow.to,
          reason: requiredFlow.reason,
          issue: '연결 누락'
        });
      }
    } else {
      missing.push({
        from: requiredFlow.from,
        to: requiredFlow.to,
        reason: requiredFlow.reason,
        issue: fromFound ? `"${requiredFlow.to}" 컴포넌트 누락` : `"${requiredFlow.from}" 컴포넌트 누락`
      });
    }
  });

  return { fulfilled, missing };
}

/**
 * 컴포넌트 타입 다양성 확인
 */
function analyzeComponentDiversity(components) {
  if (!components || components.length === 0) {
    return {
      typeCount: 0,
      types: [],
      diversity: 0
    };
  }

  const typeSet = new Set(components.map(c => c.type));
  const types = Array.from(typeSet);

  // 다양성 점수: 타입 수 / 전체 컴포넌트 수
  const diversity = Math.round((types.length / components.length) * 100);

  return {
    typeCount: types.length,
    types: types.sort(),
    diversity,
    distribution: calculateTypeDistribution(components)
  };
}

/**
 * 타입별 컴포넌트 분포
 */
function calculateTypeDistribution(components) {
  const distribution = {};

  components.forEach(comp => {
    distribution[comp.type] = (distribution[comp.type] || 0) + 1;
  });

  return Object.entries(distribution)
    .sort((a, b) => b[1] - a[1])
    .reduce((acc, [type, count]) => {
      acc[type] = count;
      return acc;
    }, {});
}

/**
 * 1단계: 기본 구조 검증
 * @returns { isValid: boolean, errors: string[], warnings: string[] }
 */
function validateBasicStructure(components, connections) {
  const errors = [];
  const warnings = [];

  // 컴포넌트 개수 확인
  if (!components || components.length === 0) {
    errors.push('컴포넌트가 배치되지 않았습니다');
  } else if (components.length < 3) {
    errors.push(`컴포넌트가 부족합니다 (현재: ${components.length}개, 필요: 3개 이상)`);
  }

  // 연결 개수 확인
  if (!connections || connections.length === 0) {
    errors.push('컴포넌트 간 연결이 필요합니다 (최소 1개)');
  }

  // ✅ 고립된 컴포넌트 확인 (필수 조건 - ERROR로 처리)
  if (components && connections) {
    const isolated = findIsolatedComponents(components, connections);
    if (isolated.length > 0) {
      errors.push(
        `모든 컴포넌트가 연결되어야 합니다. 고립된 컴포넌트: ${isolated.map(c => c.name).join(', ')}`
      );
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
    stage: 'BASIC_STRUCTURE',
    isolated: findIsolatedComponents(components, connections)
  };
}

/**
 * 2단계: 필수 요구사항 검증
 * @returns { isValid: boolean, errors: string[], warnings: string[] }
 */
function validateRequirements(components, connections, problem) {
  const errors = [];
  const warnings = [];
  const details = {};

  const rubricFunctional = problem?.rubric_functional || {};
  const requiredComponentNames = rubricFunctional.required_components || [];
  const requiredFlows = rubricFunctional.required_flows || [];

  // 필수 컴포넌트 충족도 확인
  const fulfillment = calculateComponentFulfillment(components, requiredComponentNames);
  details.componentFulfillment = fulfillment;

  if (fulfillment.rate < 70) {
    errors.push(
      `필수 컴포넌트 충족도 부족 (현재: ${fulfillment.rate}%, 필요: 70% 이상)\n` +
      `누락된 컴포넌트: ${fulfillment.missing.join(', ')}`
    );
  } else if (fulfillment.rate < 100) {
    warnings.push(
      `필수 컴포넌트가 완전하지 않습니다 (${fulfillment.rate}%)\n` +
      `누락: ${fulfillment.missing.join(', ')}`
    );
  }

  // 필수 연결 확인
  const flowCheck = checkRequiredFlows(components, connections, requiredFlows);
  details.requiredFlows = flowCheck;

  if (flowCheck.missing.length > 0) {
    errors.push(
      `필수 연결이 누락되었습니다:\n` +
      flowCheck.missing.map(f =>
        `- "${f.from}" → "${f.to}": ${f.reason} (${f.issue})`
      ).join('\n')
    );
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
    stage: 'REQUIREMENTS',
    details
  };
}

/**
 * 3단계: 설계 품질 검증 (선택)
 */
function validateDesignQuality(components) {
  const warnings = [];
  const details = {};

  // 컴포넌트 타입 다양성
  const diversity = analyzeComponentDiversity(components);
  details.diversity = diversity;

  if (diversity.typeCount < 3) {
    warnings.push(
      `컴포넌트 타입이 부족합니다 (현재: ${diversity.typeCount}개)\n` +
      `포함된 타입: ${diversity.types.join(', ')}\n` +
      `다양한 카테고리(Server, Storage, Cache, Broker 등)를 고려하세요`
    );
  }

  // 단일 타입 우위 확인
  const singleTypeCount = Object.values(diversity.distribution)[0];
  if (components.length > 0 && singleTypeCount / components.length > 0.6) {
    warnings.push(
      `한 가지 타입이 과도하게 많습니다 (${singleTypeCount}/${components.length})\n` +
      `설계의 균형을 맞춰보세요`
    );
  }

  return {
    stage: 'DESIGN_QUALITY',
    warnings,
    details,
    isWarningOnly: true
  };
}

/**
 * 전체 검증 실행 (3단계 통합)
 */
export function validateArchitecture(submission, problem) {
  if (!submission) {
    return {
      status: 'INVALID_INPUT',
      message: '제출 데이터가 없습니다',
      validation: null
    };
  }

  const components = submission.components || [];
  const connections = submission.connections || [];

  // 1단계: 기본 구조 검증
  const basicValidation = validateBasicStructure(components, connections);

  if (!basicValidation.isValid) {
    return {
      status: 'FAIL',
      stage: 'BASIC_STRUCTURE',
      message: basicValidation.errors.join('\n'),
      validation: basicValidation,
      suggestion: '먼저 컴포넌트를 3개 이상 배치하고 연결해주세요'
    };
  }

  // 2단계: 필수 요구사항 검증
  const requirementsValidation = validateRequirements(components, connections, problem);

  if (!requirementsValidation.isValid) {
    return {
      status: 'FAIL',
      stage: 'REQUIREMENTS',
      message: requirementsValidation.errors.join('\n'),
      validation: requirementsValidation,
      suggestion: '필수 컴포넌트와 연결을 추가하고 다시 시도해주세요'
    };
  }

  // 3단계: 설계 품질 검증 (경고만)
  const qualityValidation = validateDesignQuality(components);

  // 최종 결과
  return {
    status: 'PASS',
    message: '✅ 아키텍처가 유효한 기본 요구사항을 충족합니다',
    validation: {
      stage1: basicValidation,
      stage2: requirementsValidation,
      stage3: qualityValidation
    },
    summary: {
      componentCount: components.length,
      connectionCount: connections.length,
      componentFulfillment: requirementsValidation.details.componentFulfillment,
      requiredFlowsFulfilled: requirementsValidation.details.requiredFlows.fulfilled.length,
      requiredFlowsMissing: requirementsValidation.details.requiredFlows.missing.length,
      componentDiversity: qualityValidation.details.diversity
    },
    warnings: [
      ...basicValidation.warnings,
      ...requirementsValidation.warnings,
      ...qualityValidation.warnings
    ]
  };
}

/**
 * 검증 결과를 사용자 친화적으로 포맷팅
 */
export function formatValidationResult(result) {
  if (result.status === 'PASS') {
    return {
      passed: true,
      headline: '✅ 검증 통과!',
      mainMessage: result.message,
      details: formatValidationDetails(result.validation),
      warnings: result.warnings.length > 0 ? result.warnings : null,
      nextStep: '이제 구조적 설계에 대한 심화 질문이 진행됩니다'
    };
  } else {
    return {
      passed: false,
      headline: '❌ 검증 실패',
      stage: result.stage,
      mainMessage: result.message,
      suggestion: result.suggestion,
      details: result.validation
    };
  }
}

/**
 * 검증 세부사항 포맷팅
 */
function formatValidationDetails(validation) {
  return {
    stage1: {
      title: '기본 구조',
      status: validation.stage1.isValid ? '✅' : '❌',
      isolated: validation.stage1.isolated.length > 0
        ? validation.stage1.isolated.map(c => c.name)
        : []
    },
    stage2: {
      title: '필수 요구사항',
      status: validation.stage2.isValid ? '✅' : '❌',
      componentFulfillment: validation.stage2.details.componentFulfillment.rate + '%',
      requiredFlows: {
        fulfilled: validation.stage2.details.requiredFlows.fulfilled.length,
        missing: validation.stage2.details.requiredFlows.missing.length
      }
    },
    stage3: {
      title: '설계 품질 (정보)',
      componentTypes: validation.stage3.details.diversity.typeCount,
      diversity: validation.stage3.details.diversity.diversity + '%'
    }
  };
}

// ===== Export =====
export {
  normalizeComponentType,
  isSameComponentType,
  findIsolatedComponents,
  calculateComponentFulfillment,
  checkRequiredFlows,
  analyzeComponentDiversity,
  validateBasicStructure,
  validateRequirements,
  validateDesignQuality,
  COMPONENT_NAME_TO_TYPE
};
