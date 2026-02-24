import { ref, onUnmounted } from 'vue'
import { io } from 'socket.io-client'

/**
 * 로직 런(Logic Run) 전용 소켓 composable
 * [수정일: 2026-02-24] 멀티플레이어 실시간 동기화 지원
 */
export function useRunSocket() {
    const socket = ref(null)
    const connected = ref(false)
    const roomPlayers = ref([])
    const isLeader = ref(false)
    const isReady = ref(false)
    const gameStarted = ref(false)

    // 동기화 데이터
    const remotePlayerPos = ref(0)
    const remoteAiPos = ref(0)
    const remoteCurrentSector = ref(0)
    const remoteCurrentLineIdx = ref(0)
    const remoteLastCorrectLine = ref('')
    const remoteCurrentPlayerIdx = ref(0)

    // 이벤트 콜백
    const onGameStart = ref(null)
    const onSync = ref(null)
    const onRelay = ref(null)
    const onHfSync = ref(null)
    const onEnd = ref(null)
    const onUserLeft = ref(null)

    function connect(roomId, userName, avatarUrl) {
        if (socket.value) return

        socket.value = io(window.location.origin, {
            path: '/socket.io',
            transports: ['websocket'],
            forceNew: true
        })

        socket.value.on('connect', () => {
            connected.value = true
            socket.value.emit('run_join', { room_id: roomId, user_name: userName, avatar_url: avatarUrl })
        })

        socket.value.on('disconnect', () => { connected.value = false })

        // 로비 업데이트
        socket.value.on('run_lobby', (data) => {
            roomPlayers.value = data.players || []
            isLeader.value = socket.value.id === data.leader_sid
            isReady.value = roomPlayers.value.length >= 2
        })

        // 준비 완료
        socket.value.on('run_ready', (data) => {
            isReady.value = data.ready
        })

        // 게임 시작
        socket.value.on('run_game_start', (data) => {
            gameStarted.value = true
            if (onGameStart.value) onGameStart.value(data?.quest_idx ?? 0)
        })

        // 진행도 동기화
        socket.value.on('run_sync', (data) => {
            if (onSync.value) onSync.value(data)
        })

        // 릴레이 시작
        socket.value.on('run_relay', (data) => {
            if (onRelay.value) onRelay.value(data)
        })

        // 하이파이브 동기화
        socket.value.on('run_hf_sync', (data) => {
            if (onHfSync.value) onHfSync.value(data)
        })

        // AI 위치 동기화
        socket.value.on('run_ai_pos', (data) => {
            remoteAiPos.value = data.aiPos
        })

        // 게임 종료
        socket.value.on('run_end', (data) => {
            if (onEnd.value) onEnd.value(data)
        })

        // 유저 퇴장
        socket.value.on('run_user_left', (data) => {
            roomPlayers.value = roomPlayers.value.filter(p => p.sid !== data.sid)
            isLeader.value = socket.value.id === data.leader_sid
            if (onUserLeft.value) onUserLeft.value(data.sid)
        })
    }

    // 발신 함수들
    function emitStart(roomId) {
        socket.value?.emit('run_start', { room_id: roomId })
    }

    function emitProgress(roomId, payload) {
        socket.value?.emit('run_progress', { room_id: roomId, ...payload })
    }

    function emitRelayStart(roomId, sectorIdx) {
        socket.value?.emit('run_relay_start', { room_id: roomId, sectorIdx })
    }

    function emitHighFive(roomId, payload) {
        socket.value?.emit('run_highfive', { room_id: roomId, ...payload })
    }

    function emitAiSync(roomId, aiPos) {
        socket.value?.emit('run_ai_sync', { room_id: roomId, aiPos })
    }

    function emitFinish(roomId, resultData) {
        socket.value?.emit('run_finish', { room_id: roomId, ...resultData })
    }

    function disconnect(roomId) {
        socket.value?.emit('run_leave', { room_id: roomId })
        socket.value?.disconnect()
        socket.value = null
    }

    onUnmounted(() => { if (socket.value) socket.value.disconnect() })

    return {
        socket, connected, roomPlayers, isLeader, isReady, gameStarted,
        remotePlayerPos, remoteAiPos, remoteCurrentSector, remoteCurrentLineIdx,
        remoteLastCorrectLine, remoteCurrentPlayerIdx,
        onGameStart, onSync, onRelay, onHfSync, onEnd, onUserLeft,
        connect, emitStart, emitProgress, emitRelayStart, emitHighFive,
        emitAiSync, emitFinish, disconnect
    }
}
