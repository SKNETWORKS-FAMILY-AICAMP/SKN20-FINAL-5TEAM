/**
 * Architecture Practice Question Generator Service
 *
 * [수정일: 2026-02-20] 백엔드 API 호출로 변경 (책임분리)
 * - 프롬프트 생성 및 LLM 호출 로직은 백엔드로 이동
 * - 프론트엔드는 백엔드 API 호출만 담당
 */

/**
 * 심화 질문 생성 [백엔드 API 호출]
 * @param {Object} problem - 문제 정보
 * @param {Array} components - 아키텍처 컴포넌트
 * @param {Array} connections - 컴포넌트 연결
 * @param {String} mermaidCode - Mermaid 다이어그램 코드
 * @param {String} userExplanation - 사용자 설명
 * @returns {Promise<Object>} 생성된 질문들
 */
export async function generateFollowUpQuestions(problem, components, connections, mermaidCode, userExplanation) {
  console.log('🎯 심화 질문 생성 시작 (Backend API 호출)...');

  try {
    const response = await fetch('/api/core/architecture/generate-questions/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        problem,
        components,
        connections,
        mermaidCode,
        userExplanation
      })
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    const result = await response.json();
    console.log('✅ 심화 질문 생성 완료');

    return {
      questions: result.questions || [],
      selectedPillars: result.selectedPillars || [],
      metadata: result.metadata || {}
    };
  } catch (error) {
    console.error('질문 생성 실패:', error);
    return generateFallbackQuestions(components);
  }
}

/**
 * Fallback 질문 생성 (API 실패 시)
 */
function generateFallbackQuestions(components) {
  const mainComponent = components[0]?.text || '메인 서버';

  return {
    analysis: {
      mentioned: [],
      missing: ['신뢰성', '성능', '운영']
    },
    questions: [
      {
        category: '신뢰성',
        gap: 'SPOF (Single Point of Failure)',
        antipattern: '단일 장애점',
        scenario: `${mainComponent} 장애`,
        question: `${mainComponent}가 갑자기 다운되면, 사용자는 즉시 서비스 중단을 경험하나요? 자동 장애조치(failover)가 작동하나요? 어떻게 구현했나요?`
      },
      {
        category: '성능',
        gap: 'Auto Scaling 부재',
        antipattern: '수동 확장',
        scenario: '트래픽 50배 급증',
        question: `동시 사용자가 평소의 50배로 급증하면, 이 아키텍처가 자동으로 리소스를 확장하나요? 아니면 수동 개입이 필요한가요? 확장 전략을 설명해주세요.`
      },
      {
        category: '운영',
        gap: '모니터링/경보 전략',
        antipattern: '사후 대응',
        scenario: '밤중 성능 저하',
        question: `밤중에 시스템이 느려지기 시작하면, 운영팀이 사용자보다 먼저 알아차릴 수 있는 모니터링 시스템이 있나요? 어떤 지표를 추적하고 있나요?`
      }
    ],
    metadata: {
      fallback: true
    }
  };
}
