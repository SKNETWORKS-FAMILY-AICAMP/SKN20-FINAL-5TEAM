// [수정일: 2026-02-23] 1. UI 데이터 즉시 설정 (Blocking 지점 이전에 배치)
let missionId = 'traffic_surge';
let initialScenario = 'traffic_surge';

if (gameStore.activeWarsMission) {
    const mission = gameStore.activeWarsMission;
    missionId = mission.id;
    initialScenario = mission.scenario_id || 'traffic_surge';
    missionTitle.value = mission.mission_title;
    interviewerName.value = mission.interviewer?.name || '강팀장';

    codeFiles.value = getScenarioTemplates(initialScenario);
    chatMessages.value = [
        {
            role: 'ai',
            content: `반갑습니다. 시나리오: ${mission.context}\n\n우선 과제: ${mission.initial_quest}\n\n[GUIDE] 우측 에디터에 시나리오에 맞는 코드가 준비되어 있습니다. ⚠️ 표시된 부분을 찾아 수정하고, TODO 항목을 완성하세요.`
        }
    ];
} else {
    missionTitle.value = '긴급 장애 대응 모의 훈련';
    interviewerName.value = 'AI 교관';
    codeFiles.value = getScenarioTemplates('traffic_surge');
    chatMessages.value = [
        {
            role: 'ai',
            content: `🕊️ 반갑습니다. 시스템 설계 역량을 평가할 AI 교관입니다.\n\n[GUIDE] 우측 에디터에서 ⚠️ 표시 부분을 찾아 수정하세요.`
        }
    ];

    // 3분 후 블랙아웃 자동 트리거
    blackoutTimer = setTimeout(() => {
        if (gamePhase.value === 'design') triggerBlackout();
    }, 180000);
}

// [수정일: 2026-02-23] 2. 세션 및 소켓 연결 (비동기 수행)
const startConnection = async () => {
    try {
        if (!authStore.sessionNickname) {
            // [수정일: 2026-02-23] 타임아웃 3초 설정 (무한 대기 방지)
            await Promise.race([
                authStore.checkSession(),
                new Promise((_, reject) => setTimeout(() => reject(new Error('Session timeout')), 3000))
            ]).catch(() => console.warn('[Auth] 세션 확인 지연으로 기본 닉네임 사용'));
        }

        const userName = currentUserName.value;
        console.log('[Socket] Connecting with:', userName);

        connectSocket(missionId, userName, gameStore.userRole || 'architect');

        initLocalStream().then(() => {
            setupSignaling();
        }).catch(err => console.warn('[WebRTC] 카메라 권한 실패:', err));

        // 소켓 리스너 등록
        if (socket.value) {
            socket.value.on('connect', () => {
                socket.value.emit('request_state', { mission_id: missionId });
            });

            socket.value.on('user_joined', (data) => {
                if (data.sid !== socket.value.id) callPeer(data.sid);
            });

            socket.value.on('leader_info', (data) => {
                serverLeaderSid.value = data.leader_sid;
            });

            socket.value.on('code_sync', (data) => {
                if (data.code_files) {
                    isRemoteCodeChange = true;
                    Object.keys(data.code_files).forEach(id => {
                        if (codeFiles.value[id] !== data.code_files[id]) codeFiles.value[id] = data.code_files[id];
                    });
                    nextTick(() => isRemoteCodeChange = false);
                }
            });

            socket.value.on('chat_sync', (data) => {
                if ((data.is_ai || data.is_interview) && (data.sender_name !== userName || data.is_ai)) {
                    chatMessages.value.push({ role: data.is_ai ? 'ai' : 'user', content: data.content, sender: data.sender_name });
                    nextTick(() => {
                        const chatLogEl = document.querySelector('.chat-log');
                        if (chatLogEl) chatLogEl.scrollTop = chatLogEl.scrollHeight;
                    });
                }
            });

            socket.value.on('state_sync', (data) => {
                if (data.state) {
                    gamePhase.value = data.state.phase;
                    if (Math.abs(timeLeft.value - data.state.time) >= 1) timeLeft.value = data.state.time;
                    progress.value = data.state.progress;
                }
            });

            socket.value.on('analysis_sync', (data) => applyAnalysisResult(data.analysis));

            socket.value.on('request_state', () => {
                if (isLeader.value) {
                    socket.value.emit('sync_state', { mission_id: missionId, state: { phase: gamePhase.value, time: timeLeft.value, progress: progress.value } });
                }
            });
        }
    } catch (e) {
        console.error('[System] 초기화 오류:', e);
    }
};

startConnection();

// [수정일: 2026-02-23] 4. 메인 루프 가동
timerInterval = setInterval(() => {
    if (timeLeft.value > 0) timeLeft.value--;

    // [수정일: 2026-02-23] 3초마다 리더가 전체 게임 상태를 전송 (주기 단축)
    if (isLeader.value && timeLeft.value > 0 && timeLeft.value % 3 === 0) {
        if (socket.value) {
            socket.value.emit('sync_state', {
                mission_id: missionId,
                state: {
                    phase: gamePhase.value,
                    time: timeLeft.value,
                    progress: progress.value
                }
            });
        }
    }
}, 1000);

runAnalysisLoop();
