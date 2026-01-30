import { ref } from 'vue';
// 마스터 에이전트 기반 다중 에이전트 평가 사용
import { evaluateWithMasterAgent } from '../services/architectureApiMasterAgent';
import {
  generateEvaluationQuestion,
  generateArchitectureAnalysisQuestions,
  generateFollowUpQuestions
} from '../services/architectureApiFastTest';
import {
  buildArchitectureContext,
  generateMockEvaluation
} from '../utils/architectureUtils';

export function useEvaluation() {
  // Evaluation State
  const isModalActive = ref(false);
  const isEvaluating = ref(false);
  const evaluationResult = ref(null);
  const isGeneratingQuestion = ref(false);
  const generatedQuestion = ref(null);
  const userAnswer = ref('');
  const showResultScreen = ref(false);

  // Deep Dive State
  const isDeepDiveModalActive = ref(false);
  const isGeneratingDeepDive = ref(false);
  const deepDiveQuestion = ref(null);
  const deepDiveQuestions = ref([]);
  const currentQuestionIndex = ref(0);
  const collectedDeepDiveAnswers = ref([]);
  const pendingEvaluationAfterDeepDive = ref(false);

  // NEW: 설명 입력 Phase 상태
  const evaluationPhase = ref('idle'); // 'idle' | 'explanation' | 'questioning' | 'evaluating'
  const userExplanation = ref('');
  const explanationAnalysis = ref(null);

  // Chat messages for evaluation context
  const chatMessages = ref([]);

  async function skipDeepDive() {
    collectedDeepDiveAnswers.value.push({
      category: deepDiveQuestions.value[currentQuestionIndex.value]?.category || '',
      question: deepDiveQuestion.value,
      answer: '(스킵됨)'
    });

    return moveToNextQuestion();
  }

  async function submitDeepDiveAnswer(answer) {
    if (answer) {
      collectedDeepDiveAnswers.value.push({
        category: deepDiveQuestions.value[currentQuestionIndex.value]?.category || '',
        question: deepDiveQuestion.value,
        answer: answer
      });

      chatMessages.value.push({
        role: 'user',
        content: `[심화 질문 - ${deepDiveQuestions.value[currentQuestionIndex.value]?.category}] ${deepDiveQuestion.value}\n\n[답변] ${answer}`,
        type: 'answer'
      });
    }

    return moveToNextQuestion();
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
    if (droppedComponents.length > 0) {
      pendingEvaluationAfterDeepDive.value = true;
      // Phase 1: 설명 입력 모드로 시작
      evaluationPhase.value = 'explanation';
      isDeepDiveModalActive.value = true;
      isGeneratingDeepDive.value = false;
      currentQuestionIndex.value = 0;
      collectedDeepDiveAnswers.value = [];
      userExplanation.value = '';

      // 설명 요청 안내 메시지
      deepDiveQuestion.value = '설계한 아키텍처에 대해 설명해주세요. 왜 이런 구조를 선택했는지, 각 컴포넌트의 역할과 데이터 흐름에 대해 자유롭게 작성해주세요.';
      deepDiveQuestions.value = [{ category: '아키텍처 설명', question: deepDiveQuestion.value }];

      return { needsDeepDive: true, phase: 'explanation' };
    }

    // DeepDive만 사용하므로 EvaluationModal 대신 바로 평가 진행
    await directEvaluate(problem, droppedComponents, connections, mermaidCode);
    return { needsDeepDive: false };
  }

  // NEW: 사용자 설명 제출 후 꼬리질문 생성
  async function submitUserExplanation(explanation, problem, droppedComponents, connections, mermaidCode) {
    userExplanation.value = explanation;
    isGeneratingDeepDive.value = true;

    // 설명을 첫 번째 답변으로 저장
    collectedDeepDiveAnswers.value.push({
      category: '아키텍처 설명',
      question: deepDiveQuestion.value,
      answer: explanation
    });

    try {
      // 사용자 설명 기반 꼬리질문 생성
      const result = await generateFollowUpQuestions(
        problem,
        droppedComponents,
        connections,
        mermaidCode,
        explanation
      );

      explanationAnalysis.value = result.analysis;

      // 꼬리질문들 설정
      if (result.questions && result.questions.length > 0) {
        deepDiveQuestions.value = result.questions;
        currentQuestionIndex.value = 0;
        deepDiveQuestion.value = result.questions[0].question;
        evaluationPhase.value = 'questioning';
      } else {
        // 질문이 없으면 바로 평가로
        evaluationPhase.value = 'evaluating';
        isDeepDiveModalActive.value = false;
        return true; // 평가 진행 가능
      }
    } catch (error) {
      console.error('Failed to generate follow-up questions:', error);
      // 에러 시 기본 질문 사용
      deepDiveQuestions.value = [
        { category: '설계 의도', question: '이 아키텍처에서 가장 중요하게 고려한 부분은 무엇인가요?' },
        { category: '확장성', question: '트래픽이 10배로 증가하면 어떤 부분을 수정해야 할까요?' },
        { category: '장애 대응', question: '주요 컴포넌트 장애 시 어떻게 대응하시겠습니까?' }
      ];
      currentQuestionIndex.value = 0;
      deepDiveQuestion.value = deepDiveQuestions.value[0].question;
      evaluationPhase.value = 'questioning';
    } finally {
      isGeneratingDeepDive.value = false;
    }

    return false; // 아직 질문 단계
  }

  async function directEvaluate(problem, droppedComponents, connections, mermaidCode) {
    showResultScreen.value = true;
    isEvaluating.value = true;
    evaluationResult.value = null;

    const architectureContext = buildArchitectureContext(
      droppedComponents,
      connections,
      mermaidCode
    );

    const deepDiveQnA = collectedDeepDiveAnswers.value.map(item => ({
      category: item.category,
      question: item.question,
      answer: item.answer === '(스킵됨)' ? '' : item.answer
    }));

    try {
      // 마스터 에이전트 기반 다중 에이전트 평가 사용
      evaluationResult.value = await evaluateWithMasterAgent(
        problem,
        architectureContext,
        null, // EvaluationModal 질문 없음
        null, // EvaluationModal 답변 없음
        deepDiveQnA
      );
    } catch (error) {
      console.error('Master Agent Evaluation error:', error);
      evaluationResult.value = generateMockEvaluation(problem, droppedComponents);
    } finally {
      isEvaluating.value = false;
    }
  }

  async function showEvaluationModal(problem, droppedComponents, connections, mermaidCode) {
    isModalActive.value = true;
    isGeneratingQuestion.value = true;
    generatedQuestion.value = null;

    try {
      const architectureContext = buildArchitectureContext(
        droppedComponents,
        connections,
        mermaidCode
      );
      generatedQuestion.value = await generateEvaluationQuestion(
        problem,
        architectureContext
      );
    } finally {
      isGeneratingQuestion.value = false;
    }
  }

  async function triggerFinalDeepDiveQuestions(problem, droppedComponents, connections, mermaidCode) {
    isDeepDiveModalActive.value = true;
    isGeneratingDeepDive.value = true;
    currentQuestionIndex.value = 0;
    collectedDeepDiveAnswers.value = [];

    try {
      deepDiveQuestions.value = await generateArchitectureAnalysisQuestions(
        problem,
        droppedComponents,
        connections,
        mermaidCode
      );

      if (deepDiveQuestions.value.length > 0) {
        deepDiveQuestion.value = deepDiveQuestions.value[0].question;
      }
    } finally {
      isGeneratingDeepDive.value = false;
    }
  }

  function closeModal() {
    isModalActive.value = false;
    generatedQuestion.value = null;
  }

  async function submitEvaluationAnswer(answer) {
    userAnswer.value = answer;
    isModalActive.value = false;
    showResultScreen.value = true;
  }

  async function evaluate(problem, droppedComponents, connections, mermaidCode) {
    isEvaluating.value = true;
    evaluationResult.value = null;

    const architectureContext = buildArchitectureContext(
      droppedComponents,
      connections,
      mermaidCode
    );

    const deepDiveQnA = collectedDeepDiveAnswers.value.map(item => ({
      category: item.category,
      question: item.question,
      answer: item.answer === '(스킵됨)' ? '' : item.answer
    }));

    try {
      // 마스터 에이전트 기반 다중 에이전트 평가 사용
      evaluationResult.value = await evaluateWithMasterAgent(
        problem,
        architectureContext,
        generatedQuestion.value,
        userAnswer.value,
        deepDiveQnA
      );
    } catch (error) {
      console.error('Master Agent Evaluation error:', error);
      evaluationResult.value = generateMockEvaluation(problem, droppedComponents);
    } finally {
      isEvaluating.value = false;
    }
  }

  function handleRetry() {
    showResultScreen.value = false;
  }

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
    isModalActive,
    isEvaluating,
    evaluationResult,
    isGeneratingQuestion,
    generatedQuestion,
    userAnswer,
    showResultScreen,

    // Deep Dive State
    isDeepDiveModalActive,
    isGeneratingDeepDive,
    deepDiveQuestion,
    deepDiveQuestions,
    currentQuestionIndex,
    collectedDeepDiveAnswers,

    // NEW: 설명 Phase 상태
    evaluationPhase,
    userExplanation,
    explanationAnalysis,

    // Chat
    chatMessages,

    // Methods
    skipDeepDive,
    submitDeepDiveAnswer,
    openEvaluationModal,
    showEvaluationModal,
    closeModal,
    submitEvaluationAnswer,
    evaluate,
    directEvaluate,
    handleRetry,
    resetEvaluationState,
    isPendingEvaluation,
    clearPendingEvaluation,

    // NEW: 설명 제출 메서드
    submitUserExplanation
  };
}
