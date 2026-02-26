import { ref, onUnmounted } from 'vue'
import { io } from 'socket.io-client'

export function useBubbleSocket() {
    const socket = ref(null)
    const connected = ref(false)
    const roomPlayers = ref([])
    const opponentName = ref('')
    const opponentAvatar = ref(null)
    const isReady = ref(false)
    const isPlaying = ref(false)
    const gameOver = ref(false)

    // Callbacks
    const onGameStart = ref(null)
    const onReceiveMonster = ref(null)
    const onReceiveFever = ref(null)
    const onGameEnd = ref(null)

    function connect(roomId, userName, userAvatar) {
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
            socket.value.emit('bubble_join', { room_id: roomId, user_name: userName, user_avatar: userAvatar })
        })

        socket.value.on('disconnect', () => {
            connected.value = false
        })

        socket.value.on('bubble_lobby', (data) => {
            roomPlayers.value = data.players || []
            isReady.value = roomPlayers.value.length >= 2
            const opp = roomPlayers.value.find(p => p.sid !== socket.value.id)
            if (opp) {
                opponentName.value = opp.name
                opponentAvatar.value = opp.avatar
            }
        })

        socket.value.on('bubble_game_start', () => {
            isPlaying.value = true
            if (onGameStart.value) onGameStart.value()
        })

        socket.value.on('bubble_receive_monster', (data) => {
            if (onReceiveMonster.value) onReceiveMonster.value(data)
        })

        socket.value.on('bubble_receive_fever', (data) => {
            if (onReceiveFever.value) onReceiveFever.value(data)
        })

        socket.value.on('bubble_end', (data) => {
            isPlaying.value = false
            gameOver.value = true
            // data.loser_sid -> winner calculation
            const isWinner = data.loser_sid !== socket.value.id
            if (onGameEnd.value) onGameEnd.value({ isWinner })
        })

        socket.value.on('bubble_player_left', (data) => {
            roomPlayers.value = roomPlayers.value.filter(p => p.sid !== data.sid)
            if (isPlaying.value) {
                // Opponent left mid-game, you win
                isPlaying.value = false
                gameOver.value = true
                if (onGameEnd.value) onGameEnd.value({ isWinner: true })
            }
        })
    }

    function emitStart(roomId) {
        socket.value?.emit('bubble_start', { room_id: roomId })
    }

    function emitSendMonster(roomId, type = 'normal') {
        socket.value?.emit('bubble_send_monster', { room_id: roomId, monster_type: type })
    }

    function emitFeverAttack(roomId, count) {
        socket.value?.emit('bubble_fever_attack', { room_id: roomId, count })
    }

    function emitGameOver(roomId) {
        socket.value?.emit('bubble_game_over', { room_id: roomId })
    }

    function disconnect() {
        if (socket.value) {
            socket.value.disconnect()
            socket.value = null
            connected.value = false
        }
    }

    onUnmounted(() => {
        disconnect()
    })

    return {
        socket,
        connected,
        roomPlayers,
        opponentName,
        opponentAvatar,
        isReady,
        isPlaying,
        gameOver,
        connect,
        disconnect,
        emitStart,
        emitSendMonster,
        emitFeverAttack,
        emitGameOver,
        onGameStart,
        onReceiveMonster,
        onReceiveFever,
        onGameEnd
    }
}
