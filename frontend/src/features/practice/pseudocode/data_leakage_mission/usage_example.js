/**
 * 데이터 누수 방지 학습 시스템 - 통합 예제
 * Stage 1 ~ 5 전체 플로우
 */

import { dataLeakageMission } from './data_leakage_stages.js';
import { ComprehensiveEvaluator } from './evaluationEngine.js';
import { generateCompleteLearningReport } from './reportGenerator.js';
import { recommendContent } from './learningResources.js';

// ==================== Vue 컴포넌트 예제 ====================

export default {
  name: 'DataLeakageMission',
  
  data() {
    return {
      // 미션 데이터
      mission: dataLeakageMission,
      
      // 현재 Stage
      currentStage: 1,
      
      // 사용자 답변
      userAnswers: {
        stage1_q1: null,
        stage1_q2: null,
        pseudocode: '',
        pythonCode: '',
        followUpAnswers: {},
        deepdiveScenario: null,
        deepdiveAnswer: ''
      },
      
      // 평가 결과
      evaluationResults: null,
      finalReport: null,
      
      // UI 상태
      loading: false,
      showFollowUp: false,
      missingKeywords: [],
      selectedDeepDive: null
    };
  },

  computed: {
    // 현재 Stage 데이터
    currentStageData() {
      const stageMap = {
        1: this.mission.stage1_buildup,
        2: this.mission.stage2_pseudocode,
        3: this.mission.stage3_implementation,
        4: this.mission.stage4_deepdive,
        5: this.mission.stage5_final
      };
      return stageMap[this.currentStage];
    },

    // 진행률
    progress() {
      return (this.currentStage / 5) * 100;
    },

    // Stage 1 완료 여부
    stage1Complete() {
      return this.userAnswers.stage1_q1 !== null && 
             this.userAnswers.stage1_q2 !== null;
    }
  },

  methods: {
    // ==================== Stage 1: 객관식 빌드업 ====================
    
    /**
     * 객관식 답변 처리
     */
    handleMultipleChoice(questionId, optionIndex) {
      const question = this.mission.stage1_buildup.questions.find(q => q.id === questionId);
      const option = question.options[optionIndex];
      
      this.userAnswers[`stage1_${questionId}`] = {
        selected: optionIndex,
        correct: option.correct,
        feedback: option.feedback
      };

      // 모든 객관식 완료 시 Stage 2로
      if (this.stage1Complete) {
        setTimeout(() => {
          this.currentStage = 2;
        }, 2000);
      }
    },

    // ==================== Stage 2: 의사코드 작성 ====================
    
    /**
     * 의사코드 제출
     */
    async submitPseudocode() {
      if (!this.userAnswers.pseudocode.trim()) {
        alert('의사코드를 작성해주세요.');
        return;
      }

      this.loading = true;

      try {
        const evaluator = new ComprehensiveEvaluator(this.getApiKey());
        
        // 부족한 키워드 체크
        this.missingKeywords = evaluator.needsFollowUp(this.userAnswers.pseudocode);
        
        if (this.missingKeywords.length > 0) {
          // 꼬리질문 필요
          this.showFollowUp = true;
          this.loading = false;
          return;
        }

        // Stage 3로 진행
        await this.proceedToStage3();
        
      } catch (error) {
        console.error('평가 오류:', error);
        alert('평가 중 오류가 발생했습니다.');
      } finally {
        this.loading = false;
      }
    },

    /**
     * 꼬리질문 답변 처리
     */
    handleFollowUpAnswer(keyword, answerIndex) {
      this.userAnswers.followUpAnswers[keyword] = answerIndex;

      // 모든 꼬리질문 완료 시
      if (Object.keys(this.userAnswers.followUpAnswers).length === this.missingKeywords.length) {
        this.showFollowUp = false;
        this.proceedToStage3();
      }
    },

    // ==================== Stage 3: 코드 변환 + Deep Dive ====================
    
    /**
     * Stage 3 진행
     */
    async proceedToStage3() {
      this.currentStage = 3;
      
      // 의사코드 → Python 자동 변환
      this.userAnswers.pythonCode = await this.convertToPython(this.userAnswers.pseudocode);
      
      // Deep Dive 시나리오 선택 (랜덤)
      const scenarios = this.mission.stage4_deepdive.scenarios;
      this.selectedDeepDive = scenarios[Math.floor(Math.random() * scenarios.length)];
      this.userAnswers.deepdiveScenario = this.selectedDeepDive;
    },

    /**
     * 의사코드 → Python 변환
     */
    async convertToPython(pseudocode) {
      // 간단한 변환 로직 (실제로는 더 정교해야 함)
      let python = '# 자동 변환된 Python 코드\n\n';
      
      // 기본 import
      python += 'from sklearn.preprocessing import StandardScaler\n';
      python += 'from sklearn.model_selection import train_test_split\n\n';
      
      // 데이터 분할
      if (/분리|split/i.test(pseudocode)) {
        python += 'X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n\n';
      }
      
      // 스케일러
      if (/scaler|스케일러/i.test(pseudocode)) {
        python += 'scaler = StandardScaler()\n';
      }
      
      // Fit
      if (/fit.*train|학습.*train/i.test(pseudocode)) {
        python += 'scaler.fit(X_train)\n\n';
      }
      
      // Transform
      if (/transform/i.test(pseudocode)) {
        python += 'X_train_scaled = scaler.transform(X_train)\n';
        python += 'X_test_scaled = scaler.transform(X_test)\n';
      }
      
      return python;
    },

    /**
     * Deep Dive 답변 제출
     */
    async submitDeepDive() {
      if (!this.userAnswers.deepdiveAnswer.trim()) {
        alert('답변을 작성해주세요.');
        return;
      }

      this.loading = true;

      try {
        // 전체 평가 실행
        await this.runComprehensiveEvaluation();
        
        // Stage 5로
        this.currentStage = 5;
        
      } catch (error) {
        console.error('평가 오류:', error);
        alert('평가 중 오류가 발생했습니다.');
      } finally {
        this.loading = false;
      }
    },

    // ==================== Stage 5: 종합 평가 ====================
    
    /**
     * 종합 평가 실행
     */
    async runComprehensiveEvaluation() {
      const evaluator = new ComprehensiveEvaluator(this.getApiKey());
      
      // 전체 평가
      this.evaluationResults = await evaluator.evaluate({
        pseudocode: this.userAnswers.pseudocode,
        pythonCode: this.userAnswers.pythonCode,
        deepdive: this.userAnswers.deepdiveAnswer,
        deepdiveScenario: this.selectedDeepDive
      });

      // 최종 리포트 생성
      this.finalReport = await generateCompleteLearningReport(
        this.evaluationResults,
        this.getApiKey()
      );
    },

    /**
     * API 키 가져오기
     */
    getApiKey() {
      // 환경변수 또는 설정에서 가져오기
      return import.meta.env.VITE_ANTHROPIC_API_KEY || '';
    },

    // ==================== UI 헬퍼 ====================
    
    /**
     * 레이더 차트 렌더링
     */
    renderRadarChart() {
      if (!this.finalReport) return;

      const ctx = this.$refs.radarCanvas.getContext('2d');
      new Chart(ctx, {
        type: 'radar',
        data: this.finalReport.radarData,
        options: {
          scales: {
            r: {
              beginAtZero: true,
              max: 100,
              ticks: {
                stepSize: 20
              }
            }
          }
        }
      });
    },

    /**
     * 등급 배지 색상
     */
    getGradeColor(grade) {
      const colors = {
        'S': '#FFD700',
        'A': '#4CAF50',
        'B': '#2196F3',
        'C': '#FF9800',
        'D': '#FF5722',
        'F': '#F44336'
      };
      return colors[grade] || '#999';
    },

    /**
     * 리소스 필터링 (점수별)
     */
    getFilteredVideos() {
      if (!this.finalReport) return [];
      
      const content = this.finalReport.recommendedContent;
      const score = this.finalReport.totalScore;

      if (score >= 80) {
        return content.videos.filter(v => v.difficulty === 'expert');
      } else if (score >= 60) {
        return content.videos.filter(v => 
          v.difficulty === 'intermediate' || v.difficulty === 'advanced'
        );
      } else {
        return content.videos.filter(v => 
          v.difficulty === 'beginner' || v.difficulty === 'intermediate'
        );
      }
    }
  },

  mounted() {
    console.log('데이터 누수 방지 미션 시작');
  }
};
