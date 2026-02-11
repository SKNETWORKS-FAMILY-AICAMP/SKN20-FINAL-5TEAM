/**
 * Architecture Validator 사용 예제 및 테스트 케이스
 */

import {
  validateArchitecture,
  formatValidationResult,
  findIsolatedComponents,
  calculateComponentFulfillment,
  checkRequiredFlows,
  analyzeComponentDiversity
} from './architectureValidator.js';

// ===== 테스트 데이터 =====

// 테스트 문제 (jr_001: URL 단축)
const testProblem = {
  problem_id: 'jr_001_url_shortener',
  title: '축제 홍보용 단축 URL 생성기',
  rubric_functional: {
    required_components: ['Web Server', 'RDBMS', 'Cache (Redis)'],
    required_flows: [
      {
        from: 'Web Server',
        to: 'Cache',
        reason: '단축 URL 키로 원본 URL 우선 조회 (Read-through)'
      },
      {
        from: 'Cache',
        to: 'RDBMS',
        reason: '캐시 미스 시 DB 조회 및 결과 캐싱'
      }
    ]
  }
};

// 통과 케이스: 완벽한 제출
const passingSubmission = {
  components: [
    { id: '1', text: 'Web Server', type: 'server' },
    { id: '2', text: 'Redis Cache', type: 'cache' },
    { id: '3', text: 'PostgreSQL DB', type: 'rdbms' }
  ],
  connections: [
    { from: '1', to: '2' },  // Web Server → Cache
    { from: '2', to: '3' }   // Cache → RDBMS
  ]
};

// 실패 케이스 1: 컴포넌트 부족
const failingSubmission1 = {
  components: [
    { id: '1', text: 'Web Server', type: 'server' },
    { id: '2', text: 'Redis Cache', type: 'cache' }
  ],
  connections: [
    { id: '1', to: '2' }
  ]
};

// 실패 케이스 2: 필수 컴포넌트 충족도 낮음
const failingSubmission2 = {
  components: [
    { id: '1', text: 'Web Server', type: 'server' },
    { id: '2', text: 'API Gateway', type: 'gateway' },
    { id: '3', text: 'Load Balancer', type: 'loadbalancer' }
  ],
  connections: [
    { from: '1', to: '2' },
    { from: '2', to: '3' }
  ]
};

// 실패 케이스 3: 필수 연결 누락
const failingSubmission3 = {
  components: [
    { id: '1', text: 'Web Server', type: 'server' },
    { id: '2', text: 'Cache', type: 'cache' },
    { id: '3', text: 'Database', type: 'rdbms' }
  ],
  connections: [
    { from: '1', to: '2' }  // Cache → RDBMS 연결 누락
  ]
};

// 실패 케이스 4: 고립된 컴포넌트 있음
const failingSubmission4 = {
  components: [
    { id: '1', text: 'Web Server', type: 'server' },
    { id: '2', text: 'Cache', type: 'cache' },
    { id: '3', text: 'Database', type: 'rdbms' },
    { id: '4', text: 'Load Balancer', type: 'loadbalancer' }  // 고립됨
  ],
  connections: [
    { from: '1', to: '2' },
    { from: '2', to: '3' }
    // Load Balancer(id='4')는 어디와도 연결 안 됨
  ]
};

// 경고 케이스: 통과하지만 품질 개선 필요 (모두 연결됨)
const warningSubmission = {
  components: [
    { id: '1', text: 'Web Server', type: 'server' },
    { id: '2', text: 'Cache', type: 'cache' },
    { id: '3', text: 'Database', type: 'rdbms' },
    { id: '4', text: 'Another Server', type: 'server' },
    { id: '5', text: 'Third Server', type: 'server' }
  ],
  connections: [
    { from: '1', to: '2' },
    { from: '2', to: '3' },
    { from: '3', to: '4' },  // 모두 연결됨
    { from: '4', to: '5' }
  ]
};

// ===== 테스트 실행 함수 =====

/**
 * 단일 검증 테스트 실행
 */
export function runValidationTest(testName, submission, problem) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`테스트: ${testName}`);
  console.log('='.repeat(60));

  const result = validateArchitecture(submission, problem);
  const formattedResult = formatValidationResult(result);

  console.log('\n결과:');
  console.log(JSON.stringify(formattedResult, null, 2));

  return result;
}

/**
 * 모든 테스트 실행
 */
export function runAllTests() {
  console.log('\n\n');
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║         Architecture Validator - 테스트 스위트              ║');
  console.log('╚════════════════════════════════════════════════════════════╝');

  // Test 1: 통과
  runValidationTest(
    '[PASS] 완벽한 제출',
    passingSubmission,
    testProblem
  );

  // Test 2: 실패 - 컴포넌트 부족
  runValidationTest(
    '[FAIL] 컴포넌트 부족 (2개)',
    failingSubmission1,
    testProblem
  );

  // Test 3: 실패 - 필수 컴포넌트 미충족
  runValidationTest(
    '[FAIL] 필수 컴포넌트 미충족 (모두 다른 타입)',
    failingSubmission2,
    testProblem
  );

  // Test 4: 실패 - 필수 연결 누락
  runValidationTest(
    '[FAIL] 필수 연결 누락',
    failingSubmission3,
    testProblem
  );

  // Test 5: 실패 - 고립된 컴포넌트 있음 (중요!)
  runValidationTest(
    '[FAIL] 고립된 컴포넌트 있음 (모든 컴포넌트가 연결되어야 함)',
    failingSubmission4,
    testProblem
  );

  // Test 6: 경고 있음 (모두 연결되어 있지만 품질 개선 필요)
  runValidationTest(
    '[PASS + INFO] 모두 연결됨 (품질 개선 권장)',
    warningSubmission,
    testProblem
  );
}

// ===== 개별 함수 테스트 =====

export function testIndividualFunctions() {
  console.log('\n\n');
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║         개별 함수 테스트                                     ║');
  console.log('╚════════════════════════════════════════════════════════════╝');

  // 1. 고립된 컴포넌트 찾기
  console.log('\n[1] 고립된 컴포넌트 찾기');
  const isolated = findIsolatedComponents(
    warningSubmission.components,
    warningSubmission.connections
  );
  console.log('고립된 컴포넌트:', isolated);

  // 2. 필수 컴포넌트 충족도
  console.log('\n[2] 필수 컴포넌트 충족도');
  const fulfillment = calculateComponentFulfillment(
    passingSubmission.components,
    testProblem.rubric_functional.required_components
  );
  console.log('충족도:', fulfillment);

  // 3. 필수 연결 확인
  console.log('\n[3] 필수 연결 확인');
  const flowCheck = checkRequiredFlows(
    passingSubmission.components,
    passingSubmission.connections,
    testProblem.rubric_functional.required_flows
  );
  console.log('필수 연결 확인:', flowCheck);

  // 4. 컴포넌트 다양성 분석
  console.log('\n[4] 컴포넌트 다양성 분석');
  const diversity = analyzeComponentDiversity(passingSubmission.components);
  console.log('다양성:', diversity);
}

// ===== 실제 사용 예제 =====

/**
 * React 컴포넌트에서 사용 예제
 */
export function ReactComponentExample() {
  const exampleCode = `
import { validateArchitecture, formatValidationResult } from './architectureValidator';
import { transformProblems } from './architectureUtils';

function ArchitectureSubmitButton({ userComponents, userConnections, problemId }) {
  const handleSubmit = async () => {
    // 1. 문제 데이터 로드
    const problemsData = await fetchProblems();
    const problem = transformProblems(problemsData).find(p => p.problemId === problemId);

    // 2. 검증 실행
    const submission = {
      components: userComponents,
      connections: userConnections
    };

    const validationResult = validateArchitecture(submission, problem);
    const formattedResult = formatValidationResult(validationResult);

    // 3. 결과 표시
    if (formattedResult.passed) {
      showSuccess(formattedResult.headline);
      proceedToInterview(problem);
    } else {
      showError(formattedResult.mainMessage);
      showSuggestion(formattedResult.suggestion);
    }

    // 4. 경고 표시
    if (formattedResult.warnings) {
      formattedResult.warnings.forEach(warning => {
        showWarning(warning);
      });
    }
  };

  return <button onClick={handleSubmit}>아키텍처 제출</button>;
}
`;

  console.log(exampleCode);
}

// ===== CLI 테스트 명령어 =====

/**
 * 사용법 (Node.js 환경):
 *
 * // 모든 테스트 실행
 * npm run test:architect
 *
 * // 또는 파일에서
 * import { runAllTests, testIndividualFunctions } from './architectureValidator.example.js';
 * runAllTests();
 * testIndividualFunctions();
 */

// Auto-run if executed as main module
if (import.meta.url === `file://${process.argv[1]}`) {
  runAllTests();
  testIndividualFunctions();
}
