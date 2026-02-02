import { ref } from 'vue';
// 마스터 에이전트 기반 다중 에이전트 평가 사용 (6대 기둥 + 7단계 프로세스)
import { evaluateWithMasterAgent, getAvailableSubAgents, getAllQuestionStrategies } from '../services/architectureApiMasterAgent';
import { generateFollowUpQuestions } from '../services/architectureApiFastTest';
import {
  buildArchitectureContext,
  generateMockEvaluation
} from '../utils/architectureUtils';

/**
 * 평가 Composable
 *
 * 7단계 프로세스 (sys-arc.md 기반):
 * 1. 머메이드 변환: 시각적 정보를 구조화된 데이터로 변환
 * 2. 상세 설명: 사용자의 설계 '의도' 파악
 * 3. 질문 및 꼬리질문: 전문 용어를 시나리오로 번역하여 질문
 * 4. 6대 지표 개별 평가: 독립된 에이전트가 병렬로 평가
 * 5. 프롬프트 변환: 핵심 원칙 - 질문 전략 형태로 정제
 * 6. 지표 정보 공통 사용: 질문자와 평가자의 논리적 일관성
 * 7. 맥락 유지: 고정 맥락 + 유동 맥락 세션 동안 유지
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

  // NEW: 설명 입력 Phase 상태
  const evaluationPhase = ref('idle'); // 'idle' | 'explanation' | 'questioning' | 'evaluating'
  const userExplanation = ref('');
  const explanationAnalysis = ref(null);

  // Chat messages for evaluation context
  const chatMessages = ref([]);

  // NEW: 7단계 프로세스 - 세션 맥락 유지 (7단계)
  const sessionContext = ref({
    fixedContext: '', // 고정 맥락: 아키텍처 도형 + 첫 설명
    dynamicContext: '', // 유동 맥락: Q&A 대화 요약 + 새로운 사실
    facts: [], // 파악된 사실들
    clarifiedPoints: [] // 명확해진 설계 의도
  });

  // NEW: 6대 기둥 정보 (평가지표)
  const sixPillars = ref(getAvailableSubAgents());
  const allQuestionStrategies = ref(getAllQuestionStrategies());

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

  /**
   * 직접 평가 실행 (7단계 프로세스 통합)
   *
   * 프로세스:
   * 1. 머메이드 변환 (architectureContext에 이미 포함)
   * 2. 상세 설명 (userExplanation에 포함)
   * 3. 질문 및 꼬리질문 (deepDiveQnA에 포함)
   * 4. 6대 지표 개별 평가 (병렬 실행)
   * 5-7. 프롬프트 변환, 지표 공통 사용, 맥락 유지 (architectureApiMasterAgent에서 처리)
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

    // 7단계 프로세스: 고정 맥락 설정 (첫 평가 시)
    if (!sessionContext.value.fixedContext) {
      sessionContext.value.fixedContext = `아키텍처 구조:\n${architectureContext}\n\n첫 설명:\n${userExplanation.value}`;
    }

    const deepDiveQnA = collectedDeepDiveAnswers.value.map(item => ({
      category: item.category,
      question: item.question,
      answer: item.answer === '(스킵됨)' ? '' : item.answer
    }));

    // 7단계 프로세스: 유동 맥락 업데이트 (Q&A 대화 요약)
    if (deepDiveQnA.length > 0) {
      const qaSummary = deepDiveQnA
        .filter(item => item.answer && item.answer !== '(스킵됨)')
        .map(item => `[${item.category}] Q: ${item.question}\nA: ${item.answer}`)
        .join('\n\n');
      sessionContext.value.dynamicContext = qaSummary;
    }

    try {
      // 마스터 에이전트 기반 6대 기둥 평가 (7단계 프로세스 적용)
      evaluationResult.value = await evaluateWithMasterAgent(
        problem,
        architectureContext,
        null, // EvaluationModal 질문 없음
        userExplanation.value, // 사용자 설명 전달
        deepDiveQnA,
        sessionContext.value // 7단계: 세션 맥락 전달
      );

      // 맥락 업데이트 (마스터 에이전트 결과에서)
      if (evaluationResult.value?.masterAgentEvaluation?.contextUpdate) {
        const update = evaluationResult.value.masterAgentEvaluation.contextUpdate;
        sessionContext.value.facts.push(...(update.newFacts || []));
        sessionContext.value.clarifiedPoints.push(...(update.clarifiedPoints || []));
      }
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

  /**
   * 평가 상태 초기화 (7단계 프로세스 맥락 포함)
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

    // 7단계 프로세스: 세션 맥락 초기화
    sessionContext.value = {
      fixedContext: '',
      dynamicContext: '',
      facts: [],
      clarifiedPoints: []
    };
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

    // 7단계 프로세스 상태
    sessionContext,
    sixPillars,
    allQuestionStrategies,

    // Methods
    skipDeepDive,
    submitDeepDiveAnswer,
    openEvaluationModal,
    directEvaluate,
    handleRetry,
    resetEvaluationState,
    isPendingEvaluation,
    clearPendingEvaluation,

    // 설명 제출 메서드
    submitUserExplanation
  };
}
