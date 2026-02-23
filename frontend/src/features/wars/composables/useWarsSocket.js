import { ref, onUnmounted } from 'vue';
import { io } from 'socket.io-client';

export function useWarsSocket() {
    const socket = ref(null);
    const isConnected = ref(false);
    const teamMessages = ref([]);
    const teamMembers = ref([]);
    const chaosEvents = ref([]); // [Phase 4] 실시간 장애 이벤트 목록

    // 소켓 연결
    const connectSocket = (missionId, userName) => {
        if (socket.value) return;

        // 현재 호스트 기반으로 소켓 연결 (ASGI 서버가 8000번 등에서 실행 중이라고 가정)
        socket.value = io(window.location.origin, {
            path: '/socket.io',
            transports: ['websocket']
        });

        socket.value.on('connect', () => {
            isConnected.value = true;
            console.log('Connected to War Room Socket');

            // 방 입장
            socket.value.emit('join_war_room', {
                mission_id: missionId,
                user_name: userName
            });
        });

        socket.value.on('disconnect', () => {
            isConnected.value = false;
        });

        // 팀원 입장 알림
        socket.value.on('user_joined', (data) => {
            const exists = teamMembers.value.find(m => m.sid === data.sid);
            if (!exists) {
                teamMembers.value.push({
                    sid: data.sid,
                    user_name: data.user_name,
                    user_role: data.user_role || 'ARCHITECT'
                });
            }
        });

        // 채팅 동기화
        socket.value.on('chat_sync', (data) => {
            teamMessages.value.push({
                role: 'team',
                sender_name: data.sender_name,
                content: data.content,
                timestamp: new Date()
            });
        });

        // [Phase 3] 역할 변경 동기화 수신
        socket.value.on('role_sync', (data) => {
            const member = teamMembers.value.find(m => m.sid === data.sid);
            if (member) {
                member.user_role = data.user_role;
            }
        });

        // [Phase 4] 장애 이벤트(Chaos) 수신
        socket.value.on('chaos_event', (data) => {
            chaosEvents.value.push({
                ...data,
                timestamp: new Date(),
                is_read: false
            });
            console.log('⚠️ Chaos Event Detected:', data.title);
        });

        return socket.value;
    };

    // [Phase 3] 역할 변경 발신
    const changeRole = (missionId, newRole) => {
        if (!socket.value || !isConnected.value) return;
        socket.value.emit('update_role', {
            mission_id: missionId,
            user_role: newRole
        });
    };

    // 아키텍처 변경 전파
    const emitCanvasUpdate = (missionId, components, connections) => {
        if (!socket.value || !isConnected.value) return;

        socket.value.emit('canvas_update', {
            mission_id: missionId,
            mermaid_code: JSON.stringify({ components, connections })  // 버그 수정: canvas_state → mermaid_code
        });
    };

    // 팀 채팅 전송
    const sendTeamChat = (missionId, userName, content) => {
        if (!socket.value || !isConnected.value) return;

        socket.value.emit('chat_message', {
            mission_id: missionId,
            sender_name: userName,
            content: content
        });

        // 내 메시지도 로컬에 추가
        teamMessages.value.push({
            role: 'team-me',
            sender_name: userName,
            content: content,
            timestamp: new Date()
        });
    };

    const disconnectSocket = () => {
        if (socket.value) {
            socket.value.disconnect();
            socket.value = null;
        }
    };

    onUnmounted(() => {
        disconnectSocket();
    });

    return {
        socket,
        isConnected,
        teamMessages,
        teamMembers,
        chaosEvents,
        connectSocket,
        emitCanvasUpdate,
        sendTeamChat,
        changeRole,
        disconnectSocket
    };
}
