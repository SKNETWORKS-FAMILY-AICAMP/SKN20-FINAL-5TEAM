<template>
  <div class="pseudocode-practice-container">
    <!-- 평가 결과 화면 -->
    <PseudocodeResultScreen
      v-if="showResultScreen"
      :result="evaluationResult"
      :problem="currentProblem"
      :is-loading="isEvaluating"
      @retry="handleRetry"
      @close="handleClose"
    />

    <!-- 메인 연습 화면 -->
    <template v-else>
      <div class="practice-header">
        <h1>PSEUDOCODE PRACTICE</h1>
        <p>의사코드를 작성하고 면접관의 질문에 답변하세요!</p>
      </div>

      <div class="practice-content">
        <!-- 문제 표시 -->
        <div class="problem-section">
          <h2>{{ currentProblem.title }}</h2>
          <p class="problem-description">{{ currentProblem.description }}</p>
        </div>

        <!-- 의사코드 입력 -->
        <div class="pseudocode-section">
          <h3>의사코드 작성</h3>
          <textarea
            v-model="userPseudocode"
            class="pseudocode-input"
            placeholder="의사코드를 작성하세요...

예시:
1. 입력값을 받는다
2. 조건을 확인한다
3. 결과를 반환한다"
            rows="15"
          ></textarea>
        </div>

        <!-- 제출 버튼 -->
        <div class="action-section">
          <button
            @click="submitPseudocode"
            :disabled="!userPseudocode.trim() || isEvaluating"
            class="submit-button"
          >
            제출 및 평가 시작
          </button>
        </div>
      </div>

      <!-- Deep Dive 모달 -->
      <PseudocodeDeepDiveModal
        :is-active="isDeepDiveModalActive"
        :question="deepDiveQuestion"
        :is-generating="isGeneratingDeepDive"
        :current-question="currentQuestionIndex + 1"
        :total-questions="deepDiveQuestions.length"
        :category="deepDiveQuestions[currentQuestionIndex]?.category || ''"
        :pseudocode="userPseudocode"
        @skip="handleSkipDeepDive"
        @submit="handleSubmitDeepDive"
      />
    </template>
  </div>
</template>

<script>
import { ref } from 'vue';
import PseudocodeDeepDiveModal from './components/PseudocodeDeepDiveModal.vue';
import PseudocodeResultScreen from './components/PseudocodeResultScreen.vue';
import { usePseudocodeEvaluation } from '../composables/usePseudocodeEvaluation';

export default {
  name: 'PseudocodePractice',
  components: {
    PseudocodeDeepDiveModal,
    PseudocodeResultScreen
  },
  setup() {
    // 현재 문제 (실제로는 props나 API로 받아옴)
    const currentProblem = ref({
      id: 1,
      title: '두 수의 합 구하기',
      description: '두 개의 정수를 입력받아 그 합을 반환하는 알고리즘을 의사코드로 작성하세요.',
      solution_code: 'def add(a, b):\n    return a + b',
      pseudocode: '1. 두 개의 정수 a, b를 입력받는다\n2. a와 b를 더한 결과를 계산한다\n3. 결과를 반환한다'
    });

    // 사용자 의사코드
    const userPseudocode = ref('');

    // Evaluation Composable
    const {
      isEvaluating,
      evaluationResult,
      showResultScreen,
      isDeepDiveModalActive,
      isGeneratingDeepDive,
      deepDiveQuestion,
      deepDiveQuestions,
      currentQuestionIndex,
      skipDeepDive,
      submitDeepDiveAnswer,
      startEvaluation,
      executeEvaluation,
      handleRetry: composableRetry,
      resetEvaluationState
    } = usePseudocodeEvaluation();

    // 의사코드 제출
    const submitPseudocode = async () => {
      if (!userPseudocode.value.trim()) return;

      try {
        const result = await startEvaluation(
          currentProblem.value,
          userPseudocode.value
        );

        if (result.needsDeepDive) {
          // Deep Dive 모달이 자동으로 열림
          console.log('Deep Dive 시작');
        }
      } catch (error) {
        console.error('평가 시작 오류:', error);
        alert('평가 시작 중 오류가 발생했습니다.');
      }
    };

    // Deep Dive 건너뛰기
    const handleSkipDeepDive = async () => {
      const finished = await skipDeepDive();

      if (finished) {
        // 모든 질문 완료 -> 최종 평가 실행
        await executeEvaluation(currentProblem.value, userPseudocode.value);
      }
    };

    // Deep Dive 답변 제출
    const handleSubmitDeepDive = async (answer) => {
      const finished = await submitDeepDiveAnswer(answer);

      if (finished) {
        // 모든 질문 완료 -> 최종 평가 실행
        await executeEvaluation(currentProblem.value, userPseudocode.value);
      }
    };

    // 재시도
    const handleRetry = () => {
      composableRetry();
      userPseudocode.value = '';
    };

    // 닫기
    const handleClose = () => {
      // 여기서는 단순히 상태 리셋
      // 실제로는 라우터로 이동하거나 모달을 닫음
      handleRetry();
    };

    return {
      currentProblem,
      userPseudocode,
      isEvaluating,
      evaluationResult,
      showResultScreen,
      isDeepDiveModalActive,
      isGeneratingDeepDive,
      deepDiveQuestion,
      deepDiveQuestions,
      currentQuestionIndex,
      submitPseudocode,
      handleSkipDeepDive,
      handleSubmitDeepDive,
      handleRetry,
      handleClose
    };
  }
};
</script>

<style scoped>
.pseudocode-practice-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
  color: #eaeaea;
}

/* =====================
   HEADER
===================== */
.practice-header {
  text-align: center;
  padding: 40px 20px;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 2px solid rgba(255, 255, 255, 0.1);
}

.practice-header h1 {
  font-size: 3rem;
  color: #f1c40f;
  margin-bottom: 10px;
  font-weight: bold;
}

.practice-header p {
  font-size: 1.2rem;
  color: #bbb;
}

/* =====================
   CONTENT
===================== */
.practice-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.problem-section {
  background: rgba(255, 255, 255, 0.05);
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 30px;
  border-left: 4px solid #3498db;
}

.problem-section h2 {
  font-size: 2rem;
  color: #3498db;
  margin-bottom: 15px;
}

.problem-description {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #ccc;
}

/* =====================
   PSEUDOCODE SECTION
===================== */
.pseudocode-section {
  background: rgba(255, 255, 255, 0.05);
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 30px;
  border-left: 4px solid #2ecc71;
}

.pseudocode-section h3 {
  font-size: 1.5rem;
  color: #2ecc71;
  margin-bottom: 20px;
}

.pseudocode-input {
  width: 100%;
  background: rgba(0, 0, 0, 0.5);
  border: 2px solid rgba(46, 204, 113, 0.3);
  border-radius: 8px;
  padding: 20px;
  font-family: 'Courier New', monospace;
  font-size: 1rem;
  color: #0f0;
  line-height: 1.8;
  resize: vertical;
  transition: border-color 0.3s ease;
}

.pseudocode-input:focus {
  outline: none;
  border-color: #2ecc71;
  box-shadow: 0 0 10px rgba(46, 204, 113, 0.3);
}

.pseudocode-input::placeholder {
  color: rgba(15, 255, 15, 0.3);
}

/* =====================
   ACTION SECTION
===================== */
.action-section {
  text-align: center;
}

.submit-button {
  padding: 18px 60px;
  background: linear-gradient(135deg, #f39c12 0%, #f1c40f 100%);
  color: #000;
  border: none;
  border-radius: 50px;
  font-size: 1.3rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(241, 196, 15, 0.4);
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(241, 196, 15, 0.6);
}

.submit-button:active:not(:disabled) {
  transform: translateY(-1px);
}

.submit-button:disabled {
  background: #555;
  cursor: not-allowed;
  box-shadow: none;
  opacity: 0.5;
}
</style>
