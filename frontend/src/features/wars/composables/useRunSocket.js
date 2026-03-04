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
    const onGenProgress = ref(null)  // [2026-03-04] AI 문제 생성 진행상황
    const onSync = ref(null)
    const onRelay = ref(null)
    const onHfSync = ref(null)
    const onDesignEvaluation = ref(null)  // ← 추가: LLM 평가 결과
    const onEnd = ref(null)
    const onUserLeft = ref(null)
    const onJoinError = ref(null)  // ← 추가: 입장 실패 핸들러
    const onDifficultyChanged = ref(null) // ← 추가: 난이도 변경 핸들러

    function connect(roomId, userName, avatarUrl, userId, difficulty) {
        if (socket.value) return

        // [수정일: 2026-02-26] Mixed Content 방지 및 배포 환경(ngrok) 탄력성 강화
        const envSocketUrl = import.meta.env.VITE_SOCKET_URL;
        // HTTPS(ngrok 등) 환경에서는 반드시 상대 경로를 사용하여 Vite 프록시를 타도록 강제함
        const socketUrl = (window.location.protocol === 'https:' || !envSocketUrl) ? "" : envSocketUrl;

        console.log(`[Socket Debug] Protocol: ${window.location.protocol}`);
        console.log(`[Socket Debug] Env Variable VITE_SOCKET_URL: "${envSocketUrl}"`);
        console.log(`[Socket Debug] Final Connection URL: "${socketUrl || window.location.origin}"`);

        socket.value = io(socketUrl, {
            // [수정일: 2026-02-26] AWS ALB 및 Nginx의 /socket.io/ 라우팅 누락 문제 해결을 위해 /api/socket.io 로 경로 변경
            path: '/api/socket.io',
            transports: ['polling', 'websocket'],
            forceNew: true
        })

        socket.value.on('connect', () => {
            connected.value = true
            // [수정일: 2026-03-03] DB 연동을 위해 user_id 포함
            socket.value.emit('run_join', { room_id: roomId, user_name: userName, avatar_url: avatarUrl, user_id: userId, difficulty })
        })

        socket.value.on('disconnect', () => { connected.value = false })

        // 로비 업데이트
        socket.value.on('run_lobby', (data) => {
            roomPlayers.value = data.players || []
            isLeader.value = socket.value.id === data.leader_sid
            isReady.value = roomPlayers.value.length >= 2
        })

        // 난이도 변경 수신
        socket.value.on('run_difficulty_changed', (data) => {
            const playerIndex = roomPlayers.value.findIndex(p => p.sid === data.sid)
            if (playerIndex !== -1) {
                roomPlayers.value[playerIndex].difficulty = data.difficulty
                roomPlayers.value = [...roomPlayers.value] // Vue 강제 반응성 트리거
            }
            if (onDifficultyChanged.value) onDifficultyChanged.value(data)
        })

        // 준비 완료
        socket.value.on('run_ready', (data) => {
            isReady.value = data.ready
        })

        // [2026-03-04] AI 문제 생성 진행
        socket.value.on('run_gen_progress', (data) => {
            if (onGenProgress.value) onGenProgress.value(data)
        })

        // 게임 시작
        socket.value.on('run_game_start', (data) => {
            gameStarted.value = true
            if (onGameStart.value) onGameStart.value(data?.quest_idx ?? 0, data?.quests ?? null)
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

        // LLM 평가 결과 (Phase 2 끝)
        socket.value.on('run_design_evaluation', (data) => {
            if (onDesignEvaluation.value) onDesignEvaluation.value(data)
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

        // 입장 에러
        socket.value.on('run_error', (data) => {
            if (onJoinError.value) onJoinError.value(data.message)
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

    // LogicRun 전용: 각 플레이어에게 상대 점수를 개별 전송 (run_finish는 broadcast라 버그 발생)
    function emitLogicFinish(roomId, resultData) {
        socket.value?.emit('run_logic_finish', { room_id: roomId, ...resultData })
    }

    // LogicRun 전용: 선택한 난이도를 실시간으로 서버에 전송
    function emitDifficultyChange(roomId, difficulty) {
        socket.value?.emit('run_change_difficulty', { room_id: roomId, difficulty })
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
        onGameStart, onGenProgress, onSync, onRelay, onHfSync, onDesignEvaluation, onEnd, onUserLeft, onJoinError, onDifficultyChanged,
        connect, emitStart, emitProgress, emitRelayStart, emitHighFive,
        emitAiSync, emitFinish, emitLogicFinish, emitDifficultyChange, disconnect
    }
}
