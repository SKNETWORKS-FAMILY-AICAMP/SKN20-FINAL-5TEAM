/**
 * 에이전트 기반 학습 분석 API 서비스
 *
 * POST /api/core/agents/analyze/ - 종합 학습 분석
 * GET /api/core/agents/weakness-profile/ - 약점 프로필 조회
 */

import axios from 'axios';

export const AgentAnalysisService = {
  /**
   * 사용자 약점 프로필 조회
   *
   * @returns {Promise<Object>} 약점 프로필
   */
  async getWeaknessProfile() {
    try {
      const response = await axios.get('/api/core/agents/weakness-profile/');
      return response.data;
    } catch (error) {
      console.error('약점 프로필 조회 실패:', error);
      throw error;
    }
  },

  /**
   * 종합 학습 분석 요청 (컨텍스트 포함)
   *
   * @param {string} message - 사용자 메시지
   * @returns {Promise<Object>} 분석 결과
   */
  async analyzeLearning(message = '내 학습을 분석해줘') {
    try {
      // Step 1: 사용자 컨텍스트 수집 (약점 프로필, 학습 기록)
      let context = {};
      try {
        const profileData = await this.getWeaknessProfile();
        context = {
          top_weaknesses: profileData.top_weaknesses || [],
          analyzed_submission_count: profileData.analyzed_submission_count || 0,
          unit_metrics: {
            unit1: profileData.unit1_metrics || {},
            unit2: profileData.unit2_metrics || {},
            unit3: profileData.unit3_metrics || {},
          }
        };
      } catch (contextError) {
        console.warn('컨텍스트 수집 실패, 메시지만 전달:', contextError);
      }

      // Step 2: 컨텍스트와 메시지를 함께 전달
      const response = await axios.post('/api/core/agents/analyze/', {
        message: message,
        context: context
      });
      return response.data;
    } catch (error) {
      console.error('학습 분석 실패:', error);
      throw error;
    }
  },

  /**
   * 상세 분석 요청 (특정 메시지)
   *
   * @param {string} message - 사용자 요청 메시지
   * @returns {Promise<Object>} 분석 결과
   */
  async requestAnalysis(message) {
    return this.analyzeLearning(message);
  },
};

export default AgentAnalysisService;
