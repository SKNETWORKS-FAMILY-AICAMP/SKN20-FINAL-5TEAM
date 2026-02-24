import { ref, onUnmounted } from 'vue'
import { io } from 'socket.io-client'

/**
 * 캐치마인드(Arch Draw) 전용 소켓 composable
 * [수정일: 2026-02-24] 2vs2 팀 모드 지원: myTeam, teammate, onTeamSync 추가
 */
export function useDrawSocket() {
  const socket = ref(null)
  const connected = ref(false)
  const roomPlayers = ref([])
  const opponentCanvas = ref({ nodes: [], arrows: [] })
  const opponentName = ref('')
  const opponentHasItem = ref(false)
  const isReady = ref(false)
  const roundQuestion = ref(null)
  const opponentSubmitted = ref(false)
  const roundResults = ref(null)

  // 이벤트 콜백
  const onRoundStart = ref(null)
  const onRoundResult = ref(null)
  const onItemEffect = ref(null)
  const onGameOver = ref(null)     // [추가] 게임 종료 콜백

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

    socket.value.on('draw_lobby', (data) => {
      roomPlayers.value = data.players || []
      isReady.value = roomPlayers.value.length === 2 // 딱 2명일 때만 준비 완료
    })

    // 2명 이상 모임 → ready
    socket.value.on('draw_ready', (data) => {
      isReady.value = data?.ready ?? true
    })

    // 라운드 시작
    socket.value.on('draw_round_start', (data) => {
      roundQuestion.value = data.question
      opponentCanvas.value = { nodes: [], arrows: [] }
      opponentSubmitted.value = false
      roundResults.value = null
      if (onRoundStart.value) onRoundStart.value(data.question)
    })


    // 상대 캔버스 실시간 업데이트 (관전용)
    socket.value.on('draw_canvas_update', (data) => {
      opponentName.value = data.sender_name || ''
      opponentCanvas.value = { nodes: data.nodes || [], arrows: data.arrows || [] }
    })

    // 아이템 효과 수신
    socket.value.on('draw_item_effect', (data) => {
      if (onItemEffect.value) onItemEffect.value(data.item_type)
    })

    // 상대방 아이템 보유 상태 수신
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

    // [추가] 5라운드 종료 → 게임 오버
    socket.value.on('draw_game_over', () => {
      if (onGameOver.value) onGameOver.value()
    })

    // 상대 퇴장
    socket.value.on('draw_player_left', (data) => {
      roomPlayers.value = roomPlayers.value.filter(p => p.sid !== data.sid)
      isReady.value = roomPlayers.value.length >= 2
    })
  }

  // 게임 시작
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

  // 아이템 사용
  function emitUseItem(roomId, itemType) {
    socket.value?.emit('draw_use_item', { room_id: roomId, item_type: itemType })
  }

  // 아이템 보유 상태 전송
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
    socket, connected, roomPlayers, isReady,
    opponentCanvas, opponentName, opponentHasItem,
    roundQuestion, opponentSubmitted, roundResults,
    onRoundStart, onRoundResult, onItemEffect, onGameOver,
    connect, emitStart, emitCanvasSync, emitUseItem,
    emitItemStatus, emitSubmit, emitNextRound, disconnect
  }
}
