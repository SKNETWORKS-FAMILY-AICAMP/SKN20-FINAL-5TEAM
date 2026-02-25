import { ref, onUnmounted } from 'vue';
import { useGameStore } from '@/stores/game';
import { io } from 'socket.io-client';

export function useWarsSocket() {
    const gameStore = useGameStore();
    const socket = ref(null);
    const isConnected = ref(false);
    const teamMessages = ref([]);
    const teamMembers = ref([]);
    const chaosEvents = ref([]); // [Phase 4] 실시간 장애 이벤트 목록

    // 소켓 연결
    const connectSocket = (missionId, userName, userRole) => {
        if (socket.value) return;

        // 현재 호스트 기반으로 소켓 연결 (ASGI 서버가 8000번 등에서 실행 중이라고 가정)
        socket.value = io(window.location.origin, {
            path: '/socket.io',
            transports: ['websocket'],
            forceNew: true
        });

        socket.value.on('connect', () => {
            isConnected.value = true;
            console.log('Connected to War Room Socket');

            // 방 입장
            // [수정일: 2026-02-23] 역할 정보를 포함하여 입장
            socket.value.emit('join_war_room', {
                mission_id: missionId,
                user_name: userName,
                user_role: userRole
            });
        });

        socket.value.on('disconnect', () => {
            isConnected.value = false;
        });

        // [수정일: 2026-02-23] 기존 팀원 목록 수신
        socket.value.on('members_list', (data) => {
            if (data.members) {
                teamMembers.value = data.members;
            }
        });

        // 팀원 입장 알림
        socket.value.on('user_joined', (data) => {
            const exists = teamMembers.value.find(m => m.sid === data.sid);
            if (!exists && data.sid !== socket.value.id) {
                teamMembers.value.push({
                    sid: data.sid,
                    user_name: data.user_name,
                    user_role: data.user_role || 'pending' // [수정일: 2026-02-24] 기본값 ARCHITECT 제거
                });
            }
        });

        // [수정일: 2026-02-23] 팀원 퇴장 처리
        socket.value.on('user_left', (data) => {
            teamMembers.value = teamMembers.value.filter(m => m.sid !== data.sid);
            console.log(`[Socket] 팀원 퇴장: ${data.user_name} (${data.sid})`);
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
        // [버그수정] 내 sid면 gameStore도 업데이트, 팀원이면 teamMembers 업데이트
        socket.value.on('role_sync', (data) => {
            if (data.sid === socket.value?.id) {
                // 내 자신의 역할 확인 (에코백)
                gameStore.setUserRole(data.user_role);
            } else {
                // 다른 팀원 역할 업데이트
                const member = teamMembers.value.find(m => m.sid === data.sid);
                if (member) {
                    member.user_role = data.user_role;
                } else {
                    // 아직 members_list에 없으면 추가
                    teamMembers.value.push({
                        sid: data.sid,
                        user_name: data.user_name || '팀원',
                        user_role: data.user_role || 'pending'
                    });
                }
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

        // [수정일: 2026-02-24] 리더가 미션을 시작했을 때 모든 팀원에게 알림
        socket.value.on('mission_start', (data) => {
            console.log('🚀 Mission Starting:', data.mission_id);
            if (onMissionStart.value) onMissionStart.value(data.mission_id);
        });

        return socket.value;
    };

    const onMissionStart = ref(null);

    // [수정일: 2026-02-24] 리더가 미션을 시작함 (방 전체 신호 전송)
    const startMission = (missionId) => {
        if (!socket.value || !isConnected.value) return;
        socket.value.emit('start_mission', { mission_id: missionId });
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

    // [수정일: 2026-02-23] 실시간 코드 동기화 전파
    const emitCodeUpdate = (missionId, codeFiles) => {
        if (!socket.value || !isConnected.value) {
            console.warn('[Socket] 전송 실패: 연결되지 않음 (CodeUpdate)');
            return;
        }

        socket.value.emit('code_update', {
            mission_id: missionId,
            code_files: codeFiles
        });
    };

    // 팀 채팅 전송
    const sendTeamChat = (missionId, userName, content) => {
        if (!socket.value || !isConnected.value) {
            console.warn('[Socket] 전송 실패: 연결되지 않음 (Chat)');
            return;
        }

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

    // [수정일: 2026-02-23] AI 분석 결과 방 전체 공유 (점수 및 장애 동기화)
    const emitAnalysisSync = (missionId, analysis) => {
        if (!socket.value || !isConnected.value) return;

        socket.value.emit('sync_analysis', {
            mission_id: missionId,
            analysis: analysis
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
        emitCodeUpdate,
        emitAnalysisSync,
        sendTeamChat,
        changeRole,
        startMission,
        onMissionStart,
        disconnectSocket
    };
}
