import { ref, reactive, onUnmounted } from 'vue';

export function useWebRTC(socket) {
    const localStream = ref(null);
    const remoteStreams = reactive({}); // { sid: stream }
    const peers = ref({}); // { sid: RTCPeerConnection }

    const iceServers = {
        iceServers: [
            { urls: 'stun:stun.l.google.com:19302' },
            { urls: 'stun:stun1.l.google.com:19302' }
        ]
    };

    // 로컬 미디어 스트림 획득
    const initLocalStream = async () => {
        // 1순위: 카메라 + 마이크
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            localStream.value = stream;
            return stream;
        } catch (e1) {
            console.warn('카메라+마이크 접근 실패, 마이크만 시도:', e1.message);
        }

        // 2순위: 마이크만
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: false, audio: true });
            localStream.value = stream;
            console.warn('마이크만 연결됨 (카메라 없음)');
            return stream;
        } catch (e2) {
            console.warn('마이크도 접근 실패, 음소거 모드로 진행:', e2.message);
        }

        // 3순위: 권한 없어도 게임 진행 (화상통화 없이 소켓 채팅만 사용)
        console.warn('미디어 장치 없음 — 텍스트 채팅 모드로 게임 진행');
        localStream.value = null;
        return null;
    };

    // Peer Connection 생성
    const createPeerConnection = (targetSid, isOffer) => {
        const pc = new RTCPeerConnection(iceServers);
        peers.value[targetSid] = pc;

        // 로컬 스트림 추가
        if (localStream.value) {
            localStream.value.getTracks().forEach(track => {
                pc.addTrack(track, localStream.value);
            });
        }

        // ICE Candidate 전송
        pc.onicecandidate = (event) => {
            if (event.candidate) {
                socket.value.emit('ice_candidate', {
                    target_sid: targetSid,
                    candidate: event.candidate
                });
            }
        };

        // 원격 스트림 수신
        pc.ontrack = (event) => {
            if (!remoteStreams[targetSid]) {
                remoteStreams[targetSid] = event.streams[0];
            }
        };

        return pc;
    };

    // Offer 생성 및 전송 (내가 먼저 걸 때)
    const callPeer = async (targetSid) => {
        const pc = createPeerConnection(targetSid, true);
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);

        socket.value.emit('offer', {
            target_sid: targetSid,
            offer: offer
        });
    };

    // 시그널링 이벤트 리스너 설정
    const setupSignaling = () => {
        if (!socket.value) return;

        // 누군가 나에게 Offer를 보냈을 때
        socket.value.on('offer', async (data) => {
            const pc = createPeerConnection(data.sender_sid, false);
            await pc.setRemoteDescription(new RTCSessionDescription(data.offer));

            const answer = await pc.createAnswer();
            await pc.setLocalDescription(answer);

            socket.value.emit('answer', {
                target_sid: data.sender_sid,
                answer: answer
            });
        });

        // 누군가 나의 Offer에 Answer를 보냈을 때
        socket.value.on('answer', async (data) => {
            const pc = peers.value[data.sender_sid];
            if (pc) {
                await pc.setRemoteDescription(new RTCSessionDescription(data.answer));
            }
        });

        // ICE Candidate 수신 전파
        socket.value.on('ice_candidate', async (data) => {
            const pc = peers.value[data.sender_sid];
            if (pc) {
                await pc.addIceCandidate(new RTCIceCandidate(data.candidate));
            }
        });
    };

    const stopStreams = () => {
        if (localStream.value) {
            localStream.value.getTracks().forEach(track => track.stop());
            localStream.value = null;
        }
        Object.values(peers.value).forEach(pc => pc.close());
        peers.value = {};
        // reactive 객체 초기화
        for (const key in remoteStreams) {
            delete remoteStreams[key];
        }
    };

    onUnmounted(() => {
        stopStreams();
    });

    return {
        localStream,
        remoteStreams,
        initLocalStream,
        callPeer,
        setupSignaling,
        stopStreams
    };
}
