import { ref } from 'vue';
import {
  generatePseudocodeDeepDiveQuestions,
  evaluatePseudocode
} from '../services/pseudocodeApi';

/**
 * Pseudocode Evaluation Composable
 * SystemArchitecture의 useEvaluation 패턴 적용
 */
export function usePseudocodeEvaluation() {
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

  /**
   * Deep Dive 질문 건너뛰기
   */
  async function skipDeepDive() {
    collectedDeepDiveAnswers.value.push({
      category: deepDiveQuestions.value[currentQuestionIndex.value]?.category || '',
      question: deepDiveQuestion.value,
      answer: '(스킵됨)'
    });

    return moveToNextQuestion();
  }

  /**
   * Deep Dive 답변 제출
   */
  async function submitDeepDiveAnswer(answer) {
    if (answer) {
      collectedDeepDiveAnswers.value.push({
        category: deepDiveQuestions.value[currentQuestionIndex.value]?.category || '',
        question: deepDiveQuestion.value,
        answer: answer
      });
    }

    return moveToNextQuestion();
  }

  /**
   * 다음 질문으로 이동
   */
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

  /**
   * Deep Dive 평가 시작
   */
  async function startEvaluation(problem, pseudocode) {
    try {
      // 1단계: Deep Dive 질문 생성
      await triggerDeepDiveQuestions(problem, pseudocode);
      
      return { needsDeepDive: true };
    } catch (error) {
      console.error('Evaluation start error:', error);
      throw error;
    }
  }

  /**
   * Deep Dive 질문 생성 및 모달 표시
   */
  async function triggerDeepDiveQuestions(problem, pseudocode) {
    isDeepDiveModalActive.value = true;
    isGeneratingDeepDive.value = true;
    currentQuestionIndex.value = 0;
    collectedDeepDiveAnswers.value = [];

    try {
      deepDiveQuestions.value = await generatePseudocodeDeepDiveQuestions(
        problem,
        pseudocode
      );

      if (deepDiveQuestions.value.length > 0) {
        deepDiveQuestion.value = deepDiveQuestions.value[0].question;
      }
    } catch (error) {
      console.error('Deep dive generation error:', error);
      // Fallback 질문
      deepDiveQuestions.value = [
        { category: '논리 이해도', question: '작성하신 의사코드의 핵심 로직과 그렇게 설계한 이유를 설명해주세요.' },
        { category: '예외 처리', question: '입력값이 예상과 다르거나 엣지 케이스가 발생할 때 어떻게 처리하나요?' },
        { category: '최적화', question: '이 알고리즘의 시간 복잡도는 어떻게 되며, 더 개선할 방법이 있을까요?' }
      ];
      deepDiveQuestion.value = deepDiveQuestions.value[0].question;
    } finally {
      isGeneratingDeepDive.value = false;
    }
  }

  /**
   * 최종 평가 실행 (Deep Dive 답변 완료 후)
   */
  async function executeEvaluation(problem, pseudocode) {
    showResultScreen.value = true;
    isEvaluating.value = true;
    evaluationResult.value = null;

    const deepDiveQnA = collectedDeepDiveAnswers.value.map(item => ({
      category: item.category,
      question: item.question,
      answer: item.answer === '(스킵됨)' ? '' : item.answer
    }));

    try {
      evaluationResult.value = await evaluatePseudocode(
        problem,
        pseudocode,
        deepDiveQnA
      );
    } catch (error) {
      console.error('Evaluation error:', error);
      // Fallback 평가 결과
      evaluationResult.value = {
        totalScore: 30,
        score: 30,
        grade: 'poor',
        summary: '평가 중 오류가 발생했습니다. 다시 시도해주세요.',
        pseudocodeEvaluation: {
          score: 15,
          details: [],
          strengths: [],
          weaknesses: ['평가 오류']
        },
        interviewEvaluation: {
          score: 15,
          answerAnalysis: { length: 0, hasKeyTerms: false, keyTermsFound: [], keyTermsMissing: [] },
          questionAnalysis: []
        },
        suggestions: ['다시 시도해주세요']
      };
    } finally {
      isEvaluating.value = false;
    }
  }

  /**
   * 재시도
   */
  function handleRetry() {
    showResultScreen.value = false;
    resetEvaluationState();
  }

  /**
   * 평가 상태 초기화
   */
  function resetEvaluationState() {
    evaluationResult.value = null;
    deepDiveQuestions.value = [];
    currentQuestionIndex.value = 0;
    collectedDeepDiveAnswers.value = [];
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

    // Methods
    skipDeepDive,
    submitDeepDiveAnswer,
    startEvaluation,
    executeEvaluation,
    handleRetry,
    resetEvaluationState
  };
}
