/**
 * useInterview.js — 모의면접 상태 관리 composable
 * 채용공고 선택 → 세션 생성 → 답변 제출 → 피드백 수신 흐름을 관리한다.
 */
import { ref, computed } from 'vue';
import { createSession, submitAnswer, saveVisionAnalysis } from '../api/interviewApi';
import { tts } from '../tts';
import { useVisionAnalysis } from './useVisionAnalysis'; // [수정일: 2026-02-23] [vision] 비전 분석 연동

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

  // 오류
  const error = ref('');

  // ── Computed ───────────────────────────────────────────────
  const slotProgress = computed(() => {
    if (!totalSlots.value) return 0;
    return Math.round((slotsCleared.value / totalSlots.value) * 100);
  });

  const videoQueue = ref([]); // { text: string, isReady: bool }[] (TTS + 자막 재생 큐)
  let currentChunkText = '';   // 스트리밍 중 누적되는 현재 문장
  let chunkIndex = 0;          // 현재 청크 인덱스

  /**
   * 스트리밍 중 분리된 텍스트 청크를 큐에 즉시 등록 (정적 이미지 모드: 비디오 생성 없음)
   */
  function processChunk(textChunk) {
    if (!textChunk.trim()) return;
    const chunkId = chunkIndex++;
    videoQueue.value.push({ id: chunkId, text: textChunk, isReady: true, failed: false });
  }

  /**
   * 세션 시작
   * @param {number|null} jobPostingId
   */
  const avatarType = ref('woman');

  async function startSession(jobPostingId = null, selectedAvatarType = 'woman') {
    avatarType.value = selectedAvatarType;
    tts.voice = selectedAvatarType === 'man' ? 'onyx' : 'nova';
    visionSystem.initEngine();

    isLoading.value = true;
    error.value = '';
    videoQueue.value = [];
    currentChunkText = '';
    chunkIndex = 0;

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

      // 첫 질문 TTS 큐 등록
      if (data.first_question) {
        processChunk(data.first_question);
      }
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

    // 새 답변 제출 시 큐 초기화
    videoQueue.value = [];
    currentChunkText = '';
    chunkIndex = 0;

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
        currentChunkText += token;

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
        const visionReport = visionSystem.stopAnalysis();
        const enhancedFeedback = { ...feedback, vision_analysis: visionReport };
        finalFeedback.value = enhancedFeedback;

        if (sessionId.value && visionReport) {
          saveVisionAnalysis(sessionId.value, visionReport).catch(() => { });
        }
      },

      onDone() {
        isStreaming.value = false;
        hasStreamedToken.value = false;

        // 남은 텍스트가 있다면 마지막 청크로 처리
        if (currentChunkText.trim().length > 0) {
          processChunk(currentChunkText.trim());
          currentChunkText = '';
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
    videoQueue.value = [];
    currentChunkText = '';
    chunkIndex = 0;
  }

  return {
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
    slotProgress,
    startSession,
    submitUserAnswer,
    resetSession,
    visionSystem,
    avatarType,
    videoQueue, // UI에서 TTS + 자막 재생할 텍스트 큐
  };
}
