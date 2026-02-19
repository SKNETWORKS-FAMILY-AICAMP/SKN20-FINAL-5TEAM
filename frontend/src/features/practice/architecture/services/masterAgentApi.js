// [수정일: 2026-02-10] 마스터 에이전트(Curriculum Master) API 서비스 구현
import axios from 'axios';

/**
 * 마스터 에이전트 성취도 리포트 가져오기
 * @returns {Promise<Object>} 분석 리포트 데이터
 */
export const fetchMasterAgentReport = async () => {
    try {
        const response = await axios.get('/api/core/master-agent/report/', {
            withCredentials: true
        });
        return response.data;
    } catch (error) {
        console.error('[MasterAgentApi] Failed to fetch report:', error);
        throw error;
    }
};
