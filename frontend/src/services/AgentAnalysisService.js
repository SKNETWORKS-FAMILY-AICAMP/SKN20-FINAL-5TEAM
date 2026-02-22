/**
 * 에이전트 기반 학습 분석 API 서비스
 *
 * POST /api/core/agents/analyze/ - 종합 학습 분석
 * GET /api/core/agents/weakness-profile/ - 약점 프로필 조회
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/core';

export const AgentAnalysisService = {
  /**
   * 사용자 약점 프로필 조회
   *
   * @returns {Promise<Object>} 약점 프로필
   */
  async getWeaknessProfile() {
    try {
      const response = await axios.get(`${API_BASE_URL}/agents/weakness-profile/`);
      return response.data;
    } catch (error) {
      console.error('약점 프로필 조회 실패:', error);
      throw error;
    }
  },

  /**
   * 종합 학습 분석 요청
   *
   * @param {string} message - 사용자 메시지
   * @returns {Promise<Object>} 분석 결과
   */
  async analyzeLearning(message = '내 학습을 분석해줘') {
    try {
      const response = await axios.post(`${API_BASE_URL}/agents/analyze/`, {
        message: message,
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
