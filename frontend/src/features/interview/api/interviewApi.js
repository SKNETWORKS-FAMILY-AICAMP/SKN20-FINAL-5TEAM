/**
 * interviewApi.js — 모의면접 API 클라이언트
 * - axios: 채용공고 CRUD, 세션 생성/조회
 * - fetch + ReadableStream: 답변 제출 (SSE 스트리밍)
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/core';

// ── 아바타 영상 생성 API ─────────────────────────────────────

/**
 * 텍스트 → TTS → MuseTalk 립싱크 영상 생성
 * @param {string} text - 면접관 텍스트
 * @param {string} sessionId - 세션 ID
 * @returns {string} 영상 Object URL
 */
export async function generateAvatarVideo(text, sessionId = 'temp') {
  const response = await fetch(`${API_BASE_URL}/video/generate/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ text, session_id: sessionId, avatar_type: 'woman' }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error || `HTTP ${response.status}`);
  }

  const blob = await response.blob();
  return URL.createObjectURL(blob);
}

// ── Job Planner 파싱 API ────────────────────────────────────

/**
 * 채용공고 URL 파싱 (Job Planner 재사용)
 * 파싱 후 SavedJobPosting에 자동 저장, saved_posting_id 반환
 */
export async function parseJobPostingFromUrl(url) {
  const response = await axios.post(
    `${API_BASE_URL}/job-planner/parse/`,
    { type: 'url', url },
    { withCredentials: true }
  );
  return response.data; // { company_name, position, ..., saved_posting_id }
}

// ── 채용공고 API ────────────────────────────────────────────

/** 저장된 채용공고 목록 조회 */
export async function getJobPostings() {
  const response = await axios.get(`${API_BASE_URL}/interview/job-postings/`, {
    withCredentials: true,
  });
  return response.data;
}

/** 채용공고 직접 등록 */
export async function createJobPosting(data) {
  const response = await axios.post(`${API_BASE_URL}/interview/job-postings/`, data, {
    withCredentials: true,
  });
  return response.data;
}

/** 채용공고 삭제 */
export async function deleteJobPosting(id) {
  const response = await axios.delete(`${API_BASE_URL}/interview/job-postings/${id}/`, {
    withCredentials: true,
  });
  return response.data;
}

// ── 세션 API ───────────────────────────────────────────────

/** 세션 목록 조회 */
export async function getSessions() {
  const response = await axios.get(`${API_BASE_URL}/interview/sessions/`, {
    withCredentials: true,
  });
  return response.data;
}

/** 세션 삭제 */
export async function deleteSession(sessionId) {
  const response = await axios.delete(`${API_BASE_URL}/interview/sessions/${sessionId}/`, {
    withCredentials: true,
  });
  return response.data;
}

/** 세션 상세 조회 */
export async function getSession(sessionId) {
  const response = await axios.get(`${API_BASE_URL}/interview/sessions/${sessionId}/`, {
    withCredentials: true,
  });
  return response.data;
}

/**
 * 새 세션 생성 (첫 질문 포함)
 * @param {number|null} jobPostingId - 채용공고 ID (없으면 null)
 * @returns {{ session_id, first_question, current_slot, total_slots, slot_info }}
 */
export async function createSession(jobPostingId = null) {
  const payload = {};
  if (jobPostingId) payload.job_posting_id = jobPostingId;

  const response = await axios.post(`${API_BASE_URL}/interview/sessions/`, payload, {
    withCredentials: true,
  });
  return response.data;
}

/** 비전 분석 결과 저장 */
export async function saveVisionAnalysis(sessionId, visionData) {
  const response = await axios.patch(
    `${API_BASE_URL}/interview/sessions/${sessionId}/vision/`,
    { vision_analysis: visionData },
    { withCredentials: true }
  );
  return response.data;
}

// ── 답변 제출 (SSE 스트리밍) ─────────────────────────────────

/**
 * 답변 제출 + SSE 스트리밍으로 다음 질문 수신
 *
 * @param {number} sessionId
 * @param {string} answer
 * @param {Object} callbacks
 * @param {function} callbacks.onCoachFeedback - (text: string) => void
 * @param {function} callbacks.onToken - (token: string) => void  (question 토큰)
 * @param {function} callbacks.onMeta - (meta: object) => void
 * @param {function} callbacks.onFinalFeedback - (feedback: object) => void
 * @param {function} callbacks.onDone - () => void
 * @param {function} callbacks.onError - (error: Error) => void
 */
export async function submitAnswer(sessionId, answer, callbacks = {}) {
  const {
    onCoachFeedback = () => {},
    onToken = () => {},
    onMeta = () => {},
    onFinalFeedback = () => {},
    onDone = () => {},
    onError = () => {},
  } = callbacks;

  try {
    const response = await fetch(`${API_BASE_URL}/interview/sessions/${sessionId}/answer/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ answer }),
    });

    if (!response.ok || !response.body) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.error || `HTTP ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      let boundary = buffer.indexOf('\n\n');
      while (boundary !== -1) {
        const chunk = buffer.slice(0, boundary).trim();
        buffer = buffer.slice(boundary + 2);

        if (chunk.startsWith('data:')) {
          const payload = chunk
            .split('\n')
            .filter((line) => line.startsWith('data:'))
            .map((line) => line.slice(5).trim())
            .join('');

          if (payload === '[DONE]') {
            onDone();
            return;
          }

          try {
            const parsed = JSON.parse(payload);

            if (parsed.type === 'coach_feedback') {
              onCoachFeedback(parsed.text || '');
            } else if (parsed.type === 'question') {
              onToken(parsed.token || '');
            } else if (parsed.type === 'meta') {
              onMeta(parsed);
            } else if (parsed.type === 'final_feedback') {
              onFinalFeedback(parsed);
            } else if (parsed.error) {
              throw new Error(parsed.error);
            }
          } catch (e) {
            if (e.message && !e.message.includes('JSON')) {
              onError(e);
            }
          }
        }

        boundary = buffer.indexOf('\n\n');
      }
    }

    onDone();
  } catch (err) {
    onError(err);
  }
}
