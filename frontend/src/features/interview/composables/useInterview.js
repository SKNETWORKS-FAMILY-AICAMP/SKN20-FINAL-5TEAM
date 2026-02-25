/**
 * useInterview.js — 모의면접 상태 관리 composable
 * 채용공고 선택 → 세션 생성 → 답변 제출 → 피드백 수신 흐름을 관리한다.
 */
import { ref, computed } from 'vue';
import { createSession, submitAnswer, saveVisionAnalysis, generateAvatarVideo } from '../api/interviewApi';
import { useVisionAnalysis } from '@/composables/useVisionAnalysis'; // [수정일: 2026-02-23] [vision] 비전 분석 연동

export function useInterview() {
  // ── 상태 ──────────────────────────────────────────────────
  const sessionId = ref(null);
  const currentQuestion = ref('');
  const currentSlot = ref('');
  const currentTopic = ref('');
  const currentTurn = ref(0);
  const totalSlots = ref(0);
  const slotsCleared = ref(0);

  // 대화 메시지 목록
  // { role: 'interviewer' | 'user' | 'coach', content: string }
  const messages = ref([]);

  // 로딩 / 스트리밍 상태
  const isLoading = ref(false);
  const isStreaming = ref(false);
  const hasStreamedToken = ref(false);

  // 면접 완료 여부 + 최종 피드백
  const isFinished = ref(false);
  const finalFeedback = ref(null);

  const visionSystem = useVisionAnalysis(); // [수정일: 2026-02-23] [vision] 비전 시스템 인스턴스

  // 아바타 영상 URL
  const avatarVideoUrl = ref(null);

  // 오류
  const error = ref('');

  // ── Computed ───────────────────────────────────────────────
  const slotProgress = computed(() => {
    if (!totalSlots.value) return 0;
    return Math.round((slotsCleared.value / totalSlots.value) * 100);
  });

  // ── Actions ────────────────────────────────────────────────

  /**
   * 세션 시작
   * @param {number|null} jobPostingId
   */
  async function startSession(jobPostingId = null) {
    // [vision] 면접 데이터 초기화 시 비전 엔진 프리로딩 시작
    visionSystem.initEngine();

    isLoading.value = true;
    error.value = '';

    try {
      const data = await createSession(jobPostingId);

      sessionId.value = data.session_id;
      currentTurn.value = data.current_turn;
      totalSlots.value = data.total_slots;
      currentSlot.value = data.current_slot;
      currentTopic.value = data.slot_info?.topic || data.current_slot;

      currentQuestion.value = data.first_question;
      messages.value = [
        { role: 'interviewer', content: data.first_question },
      ];
    } catch (err) {
      error.value = err.response?.data?.error || err.message || '세션 생성에 실패했습니다.';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * 답변 제출 + SSE 수신
   * @param {string} answer
   */
  async function submitUserAnswer(answer) {
    if (!sessionId.value || isStreaming.value) return;

    isStreaming.value = true;
    hasStreamedToken.value = false;
    error.value = '';

    // 사용자 메시지 추가
    messages.value.push({ role: 'user', content: answer });

    // 다음 면접관 메시지 자리 확보 (스트리밍으로 채워짐)
    const nextInterviewerMsg = { role: 'interviewer', content: '' };

    await submitAnswer(sessionId.value, answer, {
      onCoachFeedback(_text) {
        // 코치 피드백은 채팅에 표시하지 않음
      },

      onToken(token) {
        if (!hasStreamedToken.value) {
          hasStreamedToken.value = true;
          messages.value.push(nextInterviewerMsg);
        }
        nextInterviewerMsg.content += token;
        // Vue 반응성 트리거
        messages.value = [...messages.value];
      },

      onMeta(meta) {
        currentTurn.value = meta.turn || currentTurn.value;
        currentSlot.value = meta.slot || currentSlot.value;
        currentTopic.value = meta.topic || currentTopic.value;
        slotsCleared.value = meta.slots_cleared ?? slotsCleared.value;
        totalSlots.value = meta.total_slots || totalSlots.value;
        currentQuestion.value = nextInterviewerMsg.content;
      },

      onFinalFeedback(feedback) {
        isFinished.value = true;
        // [vision] 면접 종료 시 분석 정지 및 데이터 취합
        const visionReport = visionSystem.stopAnalysis();

        // 피드백 데이터에 비전 분석 결과 병합 (로컬 표시용)
        const enhancedFeedback = { ...feedback, vision_analysis: visionReport };
        finalFeedback.value = enhancedFeedback;

        // [vision] 비전 분석 결과 백엔드에 저장 (실패해도 무시)
        if (sessionId.value && visionReport) {
          saveVisionAnalysis(sessionId.value, visionReport).catch(() => {});
        }
      },

      onDone() {
        isStreaming.value = false;
        hasStreamedToken.value = false;
        // 새 영상 로딩 동안 정적 이미지 표시
        avatarVideoUrl.value = null;
        // 면접관 텍스트 완성 → 아바타 영상 생성
        if (nextInterviewerMsg.content) {
          generateAvatarVideo(nextInterviewerMsg.content, sessionId.value)
            .then(url => { avatarVideoUrl.value = url; })
            .catch(() => {});
        }
      },

      onError(err) {
        error.value = err.message || '오류가 발생했습니다.';
        isStreaming.value = false;
      },
    });
  }

  function resetSession() {
    sessionId.value = null;
    currentQuestion.value = '';
    currentSlot.value = '';
    currentTopic.value = '';
    currentTurn.value = 0;
    totalSlots.value = 0;
    slotsCleared.value = 0;
    messages.value = [];
    isLoading.value = false;
    isStreaming.value = false;
    hasStreamedToken.value = false;
    isFinished.value = false;
    finalFeedback.value = null;
    error.value = '';
    avatarVideoUrl.value = null;
  }

  return {
    // state
    sessionId,
    currentQuestion,
    currentSlot,
    currentTopic,
    currentTurn,
    totalSlots,
    slotsCleared,
    messages,
    isLoading,
    isStreaming,
    hasStreamedToken,
    isFinished,
    finalFeedback,
    error,
    // computed
    slotProgress,
    // actions
    startSession,
    submitUserAnswer,
    resetSession,
    // [vision] 비전 시스템 내보내기
    visionSystem,
    avatarVideoUrl,
  };
}
