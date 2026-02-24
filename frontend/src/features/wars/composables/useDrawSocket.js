import { ref, onUnmounted } from 'vue'
import { io } from 'socket.io-client'

/**
 * 캐치마인드(Arch Draw) 전용 소켓 composable
 * - 방 입장/퇴장
 * - 캔버스 실시간 동기화
 * - 라운드 시작/제출/결과
 */
export function useDrawSocket() {
  const socket = ref(null)
  const connected = ref(false)
  const roomPlayers = ref([])      // [{ sid, name }]
  const opponentCanvas = ref({ nodes: [], arrows: [] })
  const opponentName = ref('')
  const opponentHasItem = ref(false) // [수정일: 2026-02-24] 상대방 아이템 보유 여부
  const isReady = ref(false)       // 2명 모였는지
  const roundQuestion = ref(null)  // 서버가 보낸 현재 라운드 문제
  const opponentSubmitted = ref(false)
  const roundResults = ref(null)   // 양쪽 결과

  // 이벤트 콜백 (컴포넌트에서 watch 가능)
  const onRoundStart = ref(null)
  const onRoundResult = ref(null)
  const onItemEffect = ref(null) // [수정일: 2026-02-24] 아이템 효과 콜백

  function connect(roomId, userName) {
    if (socket.value) return

    socket.value = io(window.location.origin, {
      path: '/socket.io',
      transports: ['websocket']
    })

    socket.value.on('connect', () => {
      connected.value = true
      socket.value.emit('draw_join', { room_id: roomId, user_name: userName })
    })

    socket.value.on('disconnect', () => { connected.value = false })

    // 로비: 플레이어 목록
    socket.value.on('draw_lobby', (data) => {
      roomPlayers.value = data.players || []
      // [수정일: 2026-02-24] 인원수에 따라 Ready 상태를 엄격하게 관리
      isReady.value = roomPlayers.value.length >= 2
    })

    // 2명 모임 → ready
    socket.value.on('draw_ready', () => { isReady.value = true })

    // 라운드 시작 (문제 수신)
    socket.value.on('draw_round_start', (data) => {
      roundQuestion.value = data.question
      opponentCanvas.value = { nodes: [], arrows: [] }
      opponentSubmitted.value = false
      roundResults.value = null
      if (onRoundStart.value) onRoundStart.value(data.question)
    })

    // 상대 캔버스 실시간 업데이트
    socket.value.on('draw_canvas_update', (data) => {
      opponentName.value = data.sender_name || ''
      opponentCanvas.value = { nodes: data.nodes || [], arrows: data.arrows || [] }
    })

    // [수정일: 2026-02-24] 아이템 효과 수신
    socket.value.on('draw_item_effect', (data) => {
      if (onItemEffect.value) onItemEffect.value(data.item_type)
    })

    // [수정일: 2026-02-24] 상대방 아이템 보유 상태 수신
    socket.value.on('draw_opponent_item_status', (data) => {
      opponentHasItem.value = data.has_item
    })

    // 상대가 제출함
    socket.value.on('draw_player_submitted', (data) => {
      if (data.sid !== socket.value.id) {
        opponentSubmitted.value = true
      }
    })

    // 양쪽 모두 제출 → 라운드 결과
    socket.value.on('draw_round_result', (data) => {
      roundResults.value = data.results
      if (onRoundResult.value) onRoundResult.value(data.results)
    })

    // 상대 퇴장
    socket.value.on('draw_player_left', (data) => {
      // [수정일: 2026-02-24] 나 자신이 아닌 퇴장한 유저의 SID로 필터링
      roomPlayers.value = roomPlayers.value.filter(p => p.sid !== data.sid)
      isReady.value = roomPlayers.value.length >= 2
    })
  }

  // 게임 시작 (문제 선택하여 서버에 전송)
  function emitStart(roomId, question) {
    socket.value?.emit('draw_start', { room_id: roomId, question })
  }

  // 내 캔버스 실시간 동기화
  function emitCanvasSync(roomId, userName, nodes, arrows) {
    socket.value?.emit('draw_canvas_sync', {
      room_id: roomId,
      user_name: userName,
      nodes: nodes.map(n => ({ compId: n.compId, name: n.name, icon: n.icon, x: n.x, y: n.y })),
      arrows: arrows.map(a => ({ fc: a.fc, tc: a.tc, x1: a.x1, y1: a.y1, x2: a.x2, y2: a.y2 }))
    })
  }

  // 제출
  function emitSubmit(roomId, score, checks, finalData) {
    socket.value?.emit('draw_submit', {
      room_id: roomId,
      score,
      checks,
      final_nodes: finalData?.nodes || [],
      final_arrows: finalData?.arrows || []
    })
  }

  // [수정일: 2026-02-24] 아이템 사용 전송
  function emitUseItem(roomId, itemType) {
    socket.value?.emit('draw_use_item', { room_id: roomId, item_type: itemType })
  }

  // [수정일: 2026-02-24] 아이템 상태(보유 여부) 전송
  function emitItemStatus(roomId, hasItem) {
    socket.value?.emit('draw_item_status', { room_id: roomId, has_item: hasItem })
  }

  // 다음 라운드
  function emitNextRound(roomId, question) {
    socket.value?.emit('draw_next_round', { room_id: roomId, question })
  }

  function disconnect(roomId) {
    socket.value?.emit('draw_leave', { room_id: roomId })
    socket.value?.disconnect()
    socket.value = null
  }

  onUnmounted(() => { if (socket.value) socket.value.disconnect() })

  return {
    socket, connected, roomPlayers, opponentCanvas, opponentName,
    opponentHasItem, // [추가]
    isReady, roundQuestion, opponentSubmitted, roundResults,
    onRoundStart, onRoundResult, onItemEffect,
    connect, emitStart, emitCanvasSync, emitUseItem,
    emitItemStatus, // [추가]
    emitSubmit, emitNextRound, disconnect
  }
}
