import { ref } from 'vue';
import axios from 'axios';
// 🔥 루브릭 기반 평가 (0점부터 시작, 명확한 5등급)
import { evaluateWithRubric } from '../services/architectureRubricEvaluator';
// ✅ NEW: 하이브리드 질문 생성 (안티패턴 체크 + CoT + 동적 Pillar 선별)
import { generateFollowUpQuestions } from '../services/architectureHybridQuestionGenerator';
import {
  buildArchitectureContext,
  generateMockEvaluation
} from '../utils/architectureUtils';
// ✅ NEW: 검증 로직 임포트
import { validateArchitecture, formatValidationResult } from '../utils/architectureValidator';

/**
 * 평가 Composable
 *
 * 프로세스:
 * 1. 사용자 아키텍처 설명 입력
 * 2. 고품질 질문 3개 생성 (txt 파일 참고)
 * 3. 질문에 대한 답변 수집
 * 4. 6대 기둥 기반 평가 실행
 */
export function useEvaluation() {
  // Evaluation State
  const isEvaluating = ref(false);
  const evaluationResult = ref(null);
  const showResultScreen = ref(false);

  // Deep Dive State
  const isDeepDiveModalActive = ref(false);
  const isGeneratingDeepDive = ref(false);
  const deepDiveQuestion = ref(null);
  const deepDiveQuestions = ref([]);
  const currentQuestionIndex = ref(0);
  const collectedDeepDiveAnswers = ref([]);
  const pendingEvaluationAfterDeepDive = ref(false);

  // 설명 입력 Phase 상태
  const evaluationPhase = ref('idle'); // 'idle' | 'explanation' | 'questioning' | 'evaluating'
  const userExplanation = ref('');
  const explanationAnalysis = ref(null);

  // Chat messages for evaluation context
  const chatMessages = ref([]);

  // 에러 메시지 상태
  const answerValidationError = ref('');

  /**
   * 🔥 답변 검증 - LLM 호출 전 토큰 절감
   *
   * 체크 항목:
   * 1. 공백 검증
   * 2. 최소 길이 검증 (10자 이상)
   * 3. 무의미한 답변 키워드 감지
   * 4. 단순 반응 감지 ("네", "좋아요", "응" 등)
   */
  function validateAnswer(answer) {
    const trimmed = answer.trim();

    // 1. 공백 검증
    if (!trimmed) {
      return {
        valid: false,
        message: '답변을 입력해주세요.'
      };
    }

    // 2. 최소 길이 검증 (10자 이상)
    if (trimmed.length < 10) {
      return {
        valid: false,
        message: '좀 더 구체적으로 설명해주세요. (최소 10자 이상)'
      };
    }

    // 3. 무의미한 답변 감지
    const uselessPatterns = [
      /^(잘\s*모르겠|모르겠|뭔지\s*모르겠|뭐라고\s*말해야|답을\s*모르겠|이건\s*어려워|너무\s*어려워)/gi,
      /^(음|어|흠|그런데|근데|뭐|아무튼)\s*\.?\s*$/gi,
      /^(네|맞아|그래|응|오케이|괜찮아|좋아)\s*\.?\s*$/gi,
      /^(잘\s*모름|몰라|패스|스킵|건너뛰기|다음)/gi,
      /^(이거?\s*뭐야|뭐지|뭐라고|뭐라는|뭐는|뭐가)/gi
    ];

    const answerLower = trimmed.toLowerCase();
    for (const pattern of uselessPatterns) {
      if (pattern.test(answerLower)) {
        return {
          valid: false,
          message: '더 구체적이고 의미 있는 답변을 제공해주세요. 설계 의도, 근거, 구현 방법 등을 포함해주세요.'
        };
      }
    }

    // 4. 너무 간단한 답변 (한글 기준 단어 3개 이하)
    const wordCount = trimmed.split(/[\s,.;!?]/).filter(w => w.length > 0).length;
    if (wordCount < 5) {
      return {
        valid: false,
        message: '좀 더 자세히 설명해주세요. 단순한 답변보다는 이유와 근거를 포함해주세요.'
      };
    }

    return {
      valid: true,
      message: ''
    };
  }

  /**
   * 설명 검증 - 초기 아키텍처 설명
   */
  function validateExplanation(explanation) {
    const trimmed = explanation.trim();

    // 1. 공백 검증
    if (!trimmed) {
      return {
        valid: false,
        message: '아키텍처에 대한 설명을 입력해주세요.'
      };
    }

    // 2. 최소 길이 검증 (30자 이상)
    if (trimmed.length < 30) {
      return {
        valid: false,
        message: '더 자세한 설명이 필요합니다. 설계 의도, 컴포넌트 역할, 데이터 흐름 등을 포함해주세요. (최소 30자 이상)'
      };
    }

    // 3. 무의미한 설명 감지
    const uselessPatterns = [
      /^(잘\s*모르겠|모르겠|뭔지\s*모르겠)/gi,
      /^(음|어|흠)\s*\.?\s*$/gi,
      /^(그냥|특별히|딱히)/gi
    ];

    const explanationLower = trimmed.toLowerCase();
    for (const pattern of uselessPatterns) {
      if (pattern.test(explanationLower)) {
        return {
          valid: false,
          message: '구체적인 설명이 필요합니다. 왜 이런 구조를 선택했는지, 각 컴포넌트의 역할, 데이터 흐름을 설명해주세요.'
        };
      }
    }

    return {
      valid: true,
      message: ''
    };
  }

  async function submitDeepDiveAnswer(answer) {
    // 🔥 Step 1: 답변 검증 (LLM 호출 전)
    const validation = validateAnswer(answer);
    if (!validation.valid) {
      answerValidationError.value = validation.message;
      return {
        success: false,
        error: validation.message
      };
    }

    // 검증 통과 - 에러 메시지 초기화
    answerValidationError.value = '';

    const currentQ = deepDiveQuestions.value[currentQuestionIndex.value];

    // Step 2: 검증을 통과한 답변만 저장
    collectedDeepDiveAnswers.value.push({
      category: currentQ?.category || '',
      question: deepDiveQuestion.value,
      answer: answer.trim()
    });

    chatMessages.value.push({
      role: 'user',
      content: `[심화 질문 - ${currentQ?.category}] ${deepDiveQuestion.value}\n\n[답변] ${answer.trim()}`,
      type: 'answer'
    });

    return {
      success: true,
      finished: moveToNextQuestion()
    };
  }

  function moveToNextQuestion() {
    currentQuestionIndex.value++;

    if (currentQuestionIndex.value < deepDiveQuestions.value.length) {
      deepDiveQuestion.value = deepDiveQuestions.value[currentQuestionIndex.value].question;
      return false; // Not finished
    } else {
      isDeepDiveModalActive.value = false;
      deepDiveQuestion.value = null;
      return true; // All questions done
    }
  }

  async function openEvaluationModal(problem, droppedComponents, connections, mermaidCode) {
    // ✅ Step 1: 전처리 검증 (필수)
    const submission = {
      components: droppedComponents,
      connections: connections
    };

    const validationResult = validateArchitecture(submission, problem);
    const formattedValidation = formatValidationResult(validationResult);

    // 검증 실패 시 설명 입력 모달로 이동하지 않고 검증 결과 반환
    if (!formattedValidation.passed) {
      return {
        needsValidation: true,
        validationFailed: true,
        validationResult: formattedValidation,
        rawValidation: validationResult
      };
    }

    // ✅ Step 2: 검증 통과 후 상태 초기화 (ValidationFeedback에서 "계속" 버튼을 누를 때까지 모달 열지 않음)
    if (droppedComponents.length > 0) {
      pendingEvaluationAfterDeepDive.value = true;
      // Phase 1: 설명 입력 모드 준비 (아직 모달은 열지 않음)
      evaluationPhase.value = 'explanation';
      isDeepDiveModalActive.value = false; // ← ValidationFeedback이 열릴 때까지 닫아두기
      isGeneratingDeepDive.value = false;
      currentQuestionIndex.value = 0;
      collectedDeepDiveAnswers.value = [];
      userExplanation.value = '';

      // 설명 요청 안내 메시지 준비
      deepDiveQuestion.value = '설계한 아키텍처에 대해 설명해주세요. 왜 이런 구조를 선택했는지, 각 컴포넌트의 역할과 데이터 흐름에 대해 자유롭게 작성해주세요.';
      deepDiveQuestions.value = [{ category: '아키텍처 설명', question: deepDiveQuestion.value }];

      // 경고 포함한 결과 반환
      const hasWarnings = formattedValidation.warnings && formattedValidation.warnings.length > 0;
      return {
        needsValidation: true,
        validationPassed: true,
        validationResult: formattedValidation,
        validationWarnings: hasWarnings ? formattedValidation.warnings : null,
        shouldContinue: true
      };
    }

    // DeepDive만 사용하므로 EvaluationModal 대신 바로 평가 진행
    await directEvaluate(problem, droppedComponents, connections, mermaidCode);
    return {
      needsDeepDive: false,
      validationPassed: true
    };
  }

  /**
   * ValidationFeedback에서 "계속 진행" 클릭 시 호출
   */
  function openDeepDiveModal() {
    isDeepDiveModalActive.value = true;
  }

  /**
   * 사용자 설명 제출 후 고품질 질문 3개 생성
   */
  async function submitUserExplanation(explanation, problem, droppedComponents, connections, mermaidCode) {
    // 🔥 Step 1: 설명 검증 (LLM 호출 전)
    const validation = validateExplanation(explanation);
    if (!validation.valid) {
      answerValidationError.value = validation.message;
      // ⚠️ 검증 실패 - 모달에 메시지 표시하고 반환 (진행 막기)
      return {
        success: false,
        error: validation.message,
        validationFailed: true
      };
    }

    // 검증 통과 - 에러 메시지 초기화
    answerValidationError.value = '';

    const trimmedExplanation = explanation.trim();
    userExplanation.value = trimmedExplanation;
    isGeneratingDeepDive.value = true;

    // Step 2: 검증을 통과한 설명만 저장
    collectedDeepDiveAnswers.value.push({
      category: '아키텍처 설명',
      question: deepDiveQuestion.value,
      answer: trimmedExplanation
    });

    try {
      // ✅ NEW: 하이브리드 질문 생성 (안티패턴 체크 + CoT + 동적 Pillar 선별)
      const result = await generateFollowUpQuestions(
        problem,
        droppedComponents,
        connections,
        mermaidCode,
        explanation
      );

      explanationAnalysis.value = result.analysis;

      // 질문들 설정 (정확히 3개)
      const questionsToUse = result.questions || [];
      if (questionsToUse && questionsToUse.length > 0) {
        deepDiveQuestions.value = questionsToUse;
        currentQuestionIndex.value = 0;
        deepDiveQuestion.value = questionsToUse[0].question;
        evaluationPhase.value = 'questioning';
      } else {
        // 질문이 없으면 바로 평가로
        evaluationPhase.value = 'evaluating';
        isDeepDiveModalActive.value = false;
        return {
          success: true,
          finished: true // 평가 진행 가능
        };
      }
    } catch (error) {
      console.error('Failed to generate follow-up questions:', error);
      // 에러 시 기본 질문 사용
      deepDiveQuestions.value = [
        {
          category: '신뢰성',
          question: '만약 이 시스템의 핵심 서버가 갑자기 다운된다면, 서비스 전체가 멈추나요? 아니면 다른 경로로 우회할 수 있는 구조인가요?'
        },
        {
          category: '성능',
          question: '갑자기 사용자가 10배로 늘어나는 이벤트 상황이 발생하면, 이 시스템이 자동으로 대응하나요?'
        },
        {
          category: '운영',
          question: '서비스에 장애가 났을 때, 관리자가 알기 전에 시스템이 먼저 알려주는 알람 기능이 있나요?'
        }
      ];
      currentQuestionIndex.value = 0;
      deepDiveQuestion.value = deepDiveQuestions.value[0].question;
      evaluationPhase.value = 'questioning';
    } finally {
      isGeneratingDeepDive.value = false;
    }

    return {
      success: true,
      finished: false // 아직 질문 단계
    };
  }

  /**
   * DB에 제출하는 함수
   */
  async function submitToDatabase(problem, droppedComponents, connections, mermaidCode, evaluationResult) {
    try {
      // practice_detail_id가 있는지 확인
      if (!problem.practice_detail_id) {
        console.warn('⚠️ practice_detail_id가 없어서 제출을 건너뜁니다.');
        return;
      }

      const submitData = {
        detail_id: problem.practice_detail_id,
        score: evaluationResult.totalScore || 0,
        submitted_data: {
          problem_id: problem.problem_id,
          components: droppedComponents,
          connections: connections,
          mermaid_code: mermaidCode,
          user_explanation: userExplanation.value,
          deep_dive_answers: collectedDeepDiveAnswers.value,
          evaluation_result: {
            totalScore: evaluationResult.totalScore,
            pillarScores: evaluationResult.pillarScores,
            summary: evaluationResult.summary,
            evaluatedAt: new Date().toISOString()
          }
        }
      };

      console.log('📤 제출 데이터:', submitData);

      const response = await axios.post('/api/core/activity/submit/', submitData);

      console.log('✅ 제출 성공:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ 제출 실패:', error);
      throw error;
    }
  }

  /**
   * 직접 평가 실행
   */
  async function directEvaluate(problem, droppedComponents, connections, mermaidCode) {
    showResultScreen.value = true;
    isEvaluating.value = true;
    evaluationResult.value = null;

    const architectureContext = buildArchitectureContext(
      droppedComponents,
      connections,
      mermaidCode
    );

    // 설명 항목 제외, 질문 답변만 추출 (정확히 3개)
    const deepDiveQnA = collectedDeepDiveAnswers.value
      .filter(item => item.category !== '아키텍처 설명')
      .slice(0, 3)
      .map(item => ({
        category: item.category,
        question: item.question,
        answer: item.answer
      }));

    try {
      // 🔥 루브릭 기반 평가 (0점부터, 명확한 5등급)
      evaluationResult.value = await evaluateWithRubric(
        problem,
        architectureContext,
        userExplanation.value, // 사용자 설명 전달
        deepDiveQnA
      );

      // ✅ 평가 완료 후 자동으로 DB에 제출
      await submitToDatabase(
        problem,
        droppedComponents,
        connections,
        mermaidCode,
        evaluationResult.value
      );
    } catch (error) {
      console.error('Rubric Evaluation error:', error);
      evaluationResult.value = generateMockEvaluation(problem, droppedComponents);
    } finally {
      isEvaluating.value = false;
    }
  }

  function handleRetry() {
    showResultScreen.value = false;
  }

  /**
   * 평가 상태 초기화
   */
  function resetEvaluationState() {
    evaluationResult.value = null;
    deepDiveQuestions.value = [];
    currentQuestionIndex.value = 0;
    collectedDeepDiveAnswers.value = [];
    chatMessages.value = [];
    evaluationPhase.value = 'idle';
    userExplanation.value = '';
    explanationAnalysis.value = null;
  }

  function isPendingEvaluation() {
    return pendingEvaluationAfterDeepDive.value;
  }

  function clearPendingEvaluation() {
    pendingEvaluationAfterDeepDive.value = false;
  }

  return {
    // Evaluation State
    isEvaluating,
    evaluationResult,
    showResultScreen,

    // Deep Dive State
    isDeepDiveModalActive,
    isGeneratingDeepDive,
    deepDiveQuestion,
    deepDiveQuestions,
    currentQuestionIndex,
    collectedDeepDiveAnswers,

    // 설명 Phase 상태
    evaluationPhase,
    userExplanation,
    explanationAnalysis,

    // 🔥 검증 상태
    answerValidationError,

    // Methods
    submitDeepDiveAnswer,
    openEvaluationModal,
    openDeepDiveModal, // ✅ NEW: ValidationFeedback에서 호출
    directEvaluate,
    handleRetry,
    resetEvaluationState,
    isPendingEvaluation,
    clearPendingEvaluation,

    // 설명 제출 메서드
    submitUserExplanation,

    // 🔥 검증 함수 (외부에서 사용 가능)
    validateAnswer,
    validateExplanation
  };
}
