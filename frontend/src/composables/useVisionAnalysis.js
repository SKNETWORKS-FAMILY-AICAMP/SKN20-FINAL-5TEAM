/**
 * [수정일: 2026-02-23] [vision] 비전 분석 관리 컴포저블
 * Web Worker와 통신하며 시선, 표정, 자세를 샘플링하고 집계합니다.
 */
import { ref, onUnmounted } from 'vue';
import { useUiStore } from '@/stores/ui';

export function useVisionAnalysis() {
    const isEnabled = ref(false);
    const isReady = ref(false);
    const isAnalysing = ref(false);
    const initError = ref(null);
    const uiStore = useUiStore();

    let worker = null;
    let analysisTimer = null;
    let frameCount = 0;
    let pendingVideoElement = null;
    let lastGazeToastTime = 0;
    let lastPoseToastTime = 0;
    const TOAST_COOLDOWN = 10000; // 같은 종류의 토스트는 최소 10초 간격

    // --- [실시간 집계 데이터 구조] ---
    const stats = ref({
        totalSamples: 0,
        faceSamples: 0, // [수정일: 2026-02-23] 페이스 샘플 별도 관리
        poseSamples: 0, // [수정일: 2026-02-23] 포즈 샘플 별도 관리
        gazeStableTicks: 0, // 정면 응시 횟수
        emotionSum: { smile: 0, tension: 0, neutral: 0 },
        poseStableTicks: 0, // 바른 자세 횟수
        events: [], // 주요 경고 로그
        baseline: null // 영점 조절 데이터
    });

    const resetStats = () => {
        stats.value = {
            totalSamples: 0,
            faceSamples: 0,
            poseSamples: 0,
            gazeStableTicks: 0,
            emotionSum: { smile: 0, tension: 0, neutral: 0 },
            poseStableTicks: 0,
            events: [],
            baseline: null
        };
    };

    // 1. WebGL 2.0 지원 체크
    const checkWebGL2 = () => {
        const canvas = document.createElement('canvas');
        return !!canvas.getContext('webgl2');
    };

    // 2. 엔진 초기화 (Preloading)
    const initEngine = () => {
        resetStats();
        if (!checkWebGL2()) {
            initError.value = "이 기기는 WebGL 2.0을 지원하지 않아 비전 분석이 불가능합니다.";
            return;
        }

        // Vite 변환을 피하기 위해 public 폴더의 워커를 로드합니다. (Classic Mode)
        worker = new Worker('/workers/visionWorker.js');

        // [수정일: 2026-02-23] [vision] Worker 동작 오류 시 타임아웃 방지
        worker.onerror = (err) => {
            initError.value = "비전 분석 프로세스가 예기치 않게 종료되었습니다.";
            isAnalysing.value = false;
            if (analysisTimer) {
                clearInterval(analysisTimer);
                analysisTimer = null;
            }
            console.error("[useVisionAnalysis] Worker Crash:", err.message || err);
        };

        worker.onmessage = (e) => {
            const { type, results, taskType, message } = e.data;

            if (type === 'INIT_DONE') {
                isReady.value = true;
                if (pendingVideoElement && !isAnalysing.value) {
                    startAnalysis(pendingVideoElement);
                }
            } else if (type === 'RESULT') {
                processResults(taskType, results);
            } else if (type === 'ERROR') {
                initError.value = message;
                console.error("[useVisionAnalysis] Worker Error:", message, e.data.stack);
            }
        };

        worker.postMessage({ type: 'INIT' });
    };

    // 3. 샘플링 및 데이터 전송
    const startAnalysis = (videoElement) => {
        pendingVideoElement = videoElement || pendingVideoElement;
        if (!pendingVideoElement || !isReady.value || isAnalysing.value) return;

        isAnalysing.value = true;
        frameCount = 0;

        analysisTimer = setInterval(async () => {
            if (!pendingVideoElement || pendingVideoElement.paused || pendingVideoElement.ended) return;

            frameCount++;
            const timestamp = performance.now();
            const taskType = (frameCount % 2 === 0) ? 'FACE' : 'POSE';

            try {
                const imageBitmap = await createImageBitmap(pendingVideoElement);
                worker.postMessage({
                    type: 'PROCESS_FRAME',
                    payload: { imageBitmap, timestamp, taskType }
                }, [imageBitmap]);
            } catch (err) {
                console.warn("[vision] Capture Error:", err);
            }
        }, 500); // 2 FPS
    };

    // 4. 결과 집계 및 휴리스틱 판별
    const processResults = (taskType, results) => {
        if (!results) return;
        stats.value.totalSamples++;

        if (taskType === 'FACE') {
            handleFaceResults(results);
        } else if (taskType === 'POSE') {
            handlePoseResults(results);
        }
    };

    // [표정 & 시선 휴리스틱 수정보강]
    const handleFaceResults = (results) => {
        // [수정일: 2026-02-23] 얼굴 미감지 시 분모(faceSamples)는 올리되, 정면 응시 횟수는 올리지 않음 (보이지 않는 이탈 페널티 반영)
        stats.value.faceSamples++;
        if (!results.faceLandmarks?.length) return;

        // A. Head Orientation (Yaw & Pitch Heuristic)
        const landmarks = results.faceLandmarks[0];
        const nose = landmarks[1];
        const leftEye = landmarks[33];
        const rightEye = landmarks[263];

        // [수정일: 2026-02-24] 1. Yaw (좌우 회전): 코가 두 눈 사이 중앙에 위치하는지 확인
        const eyeCenterY = (leftEye.y + rightEye.y) / 2;
        const eyeCenterX = (leftEye.x + rightEye.x) / 2;
        const eyeDist = Math.abs(rightEye.x - leftEye.x);
        const yawOffset = Math.abs(nose.x - eyeCenterX) / (eyeDist || 1);

        // [수정일: 2026-02-24] 2. Pitch (상하 숙임/들림): 코가 눈썹 라인 기준으로 얼마나 아래에 있는지 확인
        // 코의 Y값이 양 눈 평균 Y값보다 낮아야(크게 위치해야) 정상이지만, 그 간격이 비정상적으로 좁거나 넓은 경우
        const pitchOffset = (nose.y - eyeCenterY) / (eyeDist || 1);

        // 정면 응시 판정 (yawOffset < 0.15 및 pitchOffset이 일반적인 사람의 눈-코 간격 비율 내에 속할 때)
        // pitchOffset은 대략 0.5 ~ 0.9 사이가 일반적인 정면 각도임 (고개를 푹 숙이면 0에 가까워지고 높이 들면 커짐)
        const isFacingForward = yawOffset < 0.15 && pitchOffset > 0.4 && pitchOffset < 0.95;

        if (isFacingForward) {
            stats.value.gazeStableTicks++;
        } else {
            const now = Date.now();
            if (now - lastGazeToastTime > TOAST_COOLDOWN) {
                lastGazeToastTime = now;
                addEvent("시선이 정면을 벗어났습니다.");
                uiStore.showToast("카메라를 정면으로 바라봐 주세요.", "warning");
            }
        }

        // B. Emotion mapping
        if (!results.faceBlendshapes?.length) return;
        const shapes = results.faceBlendshapes[0].categories;
        const shapeMap = Object.fromEntries(shapes.map(c => [c.categoryName, c.score]));

        const smile = (shapeMap['mouthSmileLeft'] + shapeMap['mouthSmileRight']) / 2;
        const press = shapeMap['mouthPress'];

        // [수정일: 2026-02-24] 면접 상황에서는 활짝 웃기보다 옅은 미소가 유지되므로 임계값을 0.4 -> 0.15로 대폭 완화
        if (smile > 0.15) {
            stats.value.emotionSum.smile++;
            if (stats.value.faceSamples % 20 === 0) {
                addEvent("자연스러운 미소 감지 (긍정적 인상)");
            }
        } else if (press > 0.2) {
            stats.value.emotionSum.tension++;
            if (stats.value.faceSamples % 20 === 0) {
                addEvent("긴장된 표정 감지");
            }
        } else {
            stats.value.emotionSum.neutral++;
        }
    };

    // [자세 휴리스틱 수정보강]
    const handlePoseResults = (results) => {
        // [수정일: 2026-02-23] 어깨 등 미감지 시 분모(poseSamples)는 올리되, 바른 자세 횟수는 올리지 않음 (보이지 않는 이탈 페널티 반영)
        stats.value.poseSamples++;
        if (!results.poseLandmarks?.length) return;

        const landmarks = results.poseLandmarks[0];
        const leftShoulder = landmarks[11];
        const rightShoulder = landmarks[12];
        const nose = landmarks[0];

        // 1. 어깨 기울기 분석 (Y축)
        // [수정일: 2026-02-24] 웹캠 각도나 옷 주름에 따른 오차 범위를 고려하여 엄격했던 수평 임계값을 0.05 -> 0.10으로 완화
        const shoulderSlope = Math.abs(leftShoulder.y - rightShoulder.y);
        const isLevel = shoulderSlope < 0.10;

        // 2. 어깨 틀어짐 분석 (Z축 뎁스 차이 - 한쪽으로 치우쳐 앉음)
        const shoulderTwist = Math.abs(leftShoulder.z - rightShoulder.z);
        const isStraightTwist = shoulderTwist < 0.15; // Z축 0.15 임계값

        // 3. 거북목/기대기 분석 (코와 어깨의 Z축 상대 깊이)
        // 코의 Z값이 양쪽 어깨 평균 Z값과 지나치게 차이나면 (너무 앞으로 나오거나 뒤로 빠짐)
        const shoulderZAvg = (leftShoulder.z + rightShoulder.z) / 2;
        const neckLeaning = nose.z - shoulderZAvg;
        // 보통 코는 어깨보다 카메라에 가깝지만(음수), 그 차이가 -0.5 이하거나 0 이상으로 벗어나면 불량 판단 
        const isNotLeaning = neckLeaning > -0.4 && neckLeaning < -0.05;

        const isGoodPosture = isLevel && isStraightTwist && isNotLeaning;

        if (isGoodPosture) {
            stats.value.poseStableTicks++;
        } else {
            const now = Date.now();
            if (now - lastPoseToastTime > TOAST_COOLDOWN) {
                lastPoseToastTime = now;
                addEvent("어깨 수평, 틀어짐 또는 앞뒤 기울기(거북목) 문제가 감지되었습니다.");
                uiStore.showToast("자세가 기울어져 있습니다. 바르게 앉아주세요.", "warning");
            }
        }
    };

    const addEvent = (msg) => {
        const timeStr = new Date().toLocaleTimeString();
        stats.value.events.push(`[${timeStr}] ${msg}`);
        if (stats.value.events.length > 50) stats.value.events.shift();
    };

    const stopAnalysis = () => {
        if (analysisTimer) clearInterval(analysisTimer);
        isAnalysing.value = false;
        pendingVideoElement = null;
        return getFinalReport();
    };

    const getFinalReport = () => {
        // 분모를 각각의 샘플수로 정밀화하여 100% 초과 방지
        const faceTotal = stats.value.faceSamples || 1;
        const poseTotal = stats.value.poseSamples || 1;

        return {
            status: stats.value.totalSamples > 0 ? 'ok' : 'no_data',
            sampleCount: stats.value.totalSamples,
            faceSampleCount: stats.value.faceSamples,
            poseSampleCount: stats.value.poseSamples,
            error: initError.value,
            gazeScore: Math.min(100, Math.round((stats.value.gazeStableTicks / faceTotal) * 100)),
            poseScore: Math.min(100, Math.round((stats.value.poseStableTicks / poseTotal) * 100)),
            emotions: stats.value.emotionSum,
            events: stats.value.events
        };
    };

    onUnmounted(() => {
        if (worker) worker.terminate();
        if (analysisTimer) clearInterval(analysisTimer);
    });

    return {
        isReady,
        isAnalysing,
        initError,
        stats,
        initEngine,
        startAnalysis,
        stopAnalysis
    };
}
