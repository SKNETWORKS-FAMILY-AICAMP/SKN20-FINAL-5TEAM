import { ref } from 'vue';
import {
  generateEvaluationQuestion,
  evaluateArchitecture,
  generateArchitectureAnalysisQuestions
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
      await triggerFinalDeepDiveQuestions(problem, droppedComponents, connections, mermaidCode);
      return { needsDeepDive: true };
    }

    // DeepDive만 사용하므로 EvaluationModal 대신 바로 평가 진행
    await directEvaluate(problem, droppedComponents, connections, mermaidCode);
    return { needsDeepDive: false };
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
      evaluationResult.value = await evaluateArchitecture(
        problem,
        architectureContext,
        null, // EvaluationModal 질문 없음
        null, // EvaluationModal 답변 없음
        deepDiveQnA
      );
    } catch (error) {
      console.error('Evaluation error:', error);
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
      evaluationResult.value = await evaluateArchitecture(
        problem,
        architectureContext,
        generatedQuestion.value,
        userAnswer.value,
        deepDiveQnA
      );
    } catch (error) {
      console.error('Evaluation error:', error);
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
    clearPendingEvaluation
  };
}
