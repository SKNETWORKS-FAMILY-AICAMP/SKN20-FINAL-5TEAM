/**
 * useInterview.js — 모의면접 상태 관리 composable
 * 채용공고 선택 → 세션 생성 → 답변 제출 → 피드백 수신 흐름을 관리한다.
 */
import { ref, computed } from 'vue';
import { createSession, submitAnswer, saveVisionAnalysis, generateAvatarVideo } from '../api/interviewApi';
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

  const videoQueue = ref([]); // { url: string, text: string }[] (비디오 URL과 해당 자막)
  let currentChunkText = '';   // 스트리밍 중 누적되는 현재 문장
  let chunkIndex = 0;          // 현재 생성 중인 청크 인덱스
  let isGeneratingVideo = false; // 백엔드 동시 요청 제한 락

  /**
   * 문장 단위 비디오 생성 처리 루프
   * - 백엔드 과부하 방지를 위해 순차적(Sequential)으로 생성 API 호출
   */
  async function processNextGeneration() {
    if (isGeneratingVideo) return;

    // 아직 생성되지 않은 첫 번째 청크 찾기
    const targetItem = videoQueue.value.find(item => !item.isReady && !item.url && !item.failed);
    if (!targetItem) return;

    isGeneratingVideo = true;
    try {
      const url = await generateAvatarVideo(targetItem.text, sessionId.value, avatarType.value);
      targetItem.url = url;
      targetItem.isReady = true;
    } catch (err) {
      console.error('[Vision] 청크 비디오 생성 실패:', err);
      targetItem.failed = true; // 실패 마킹 (무한 루프 방지)
    } finally {
      isGeneratingVideo = false;
      // 다음 항목이 있으면 이어서 처리
      processNextGeneration();
    }
  }

  /**
   * 스트리밍 중 분리된 텍스트 청크를 큐에 등록하고 생성 트리거
   */
  function processChunk(textChunk) {
    if (!textChunk.trim()) return;
    const chunkId = chunkIndex++;

    // UI 큐에 대기 상태로 등록
    const queueItem = { id: chunkId, text: textChunk, url: null, isReady: false, failed: false };
    videoQueue.value.push(queueItem);

    // 생성 루프 트리거
    processNextGeneration();
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

      // 첫 질문 영상 생성
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
    isGeneratingVideo = false;

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

        // 첫 문장만 1번 청크로 분리하고, 나머지는 모두 끝날 때까지 모아 2번 청크로 생성 (GPU 부하 절감)
        if (chunkIndex === 0 && (/[.?!]\s|\n/.test(token) || (/[.?!]$/.test(token) && currentChunkText.length > 20))) {
          processChunk(currentChunkText.trim());
          currentChunkText = '';
        }

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
    // avatarVideoUrl.value = null; // 더 이상 단일 URL 안 씀
    videoQueue.value = [];
    currentChunkText = '';
    chunkIndex = 0;
    isGeneratingVideo = false;
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
    videoQueue, // UI에서 연속 재생할 비디오 큐
  };
}
