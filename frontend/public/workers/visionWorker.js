/**
 * [수정일: 2026-02-23] [vision] MediaPipe 연산 전용 Web Worker (Public Classic Mode)
 * CDN ORB 차단을 우회하기 위해 로컬(public/workers/mediapipe) 라이브러리를 사용합니다.
 */

// CommonJS 모듈 형식 에러(exports is not defined) 방지용 폴리필
self.exports = {};

// MediaPipe 태스크 라이브러리 로컬 위치 로드
importScripts("/workers/mediapipe/vision_bundle.js");

// 글로벌 네임스페이스 추출 (폴리필 객체에서)
const { FaceLandmarker, PoseLandmarker, FilesetResolver } = self.exports;

let faceLandmarker;
let poseLandmarker;
let isInitialized = false;

// Worker 초기화
const initModels = async () => {
    try {
        const wasmPath = "/workers/mediapipe/wasm";
        const vision = await FilesetResolver.forVisionTasks(wasmPath);

        // 1. Face Landmarker 초기화
        faceLandmarker = await FaceLandmarker.createFromOptions(vision, {
            baseOptions: {
                modelAssetPath: `https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task`,
                delegate: "GPU"
            },
            outputFaceBlendshapes: true,
            runningMode: "VIDEO",
            numFaces: 1
        });

        // 2. Pose Landmarker 초기화
        poseLandmarker = await PoseLandmarker.createFromOptions(vision, {
            baseOptions: {
                modelAssetPath: `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task`,
                delegate: "GPU"
            },
            runningMode: "VIDEO",
            numPoses: 1
        });

        isInitialized = true;
        self.postMessage({ type: 'INIT_DONE' });
    } catch (error) {
        console.error("[visionWorker] Init Error:", error);
        self.postMessage({
            type: 'ERROR',
            message: error.message,
            stack: error.stack
        });
    }
};

// 메인 스레드로부터 메시지 수신
self.onmessage = async (event) => {
    const { type, payload } = event.data;

    if (type === 'INIT') {
        await initModels();
        return;
    }

    if (!isInitialized) return;

    if (type === 'PROCESS_FRAME') {
        const { imageBitmap, timestamp, taskType } = payload;

        try {
            // MediaPipe 결과는 WASM 기반 객체라 postMessage 직렬화가 불가능하므로
            // 필요한 데이터만 plain object로 추출하여 전송합니다.
            let results = null;
            if (taskType === 'FACE') {
                const raw = faceLandmarker.detectForVideo(imageBitmap, timestamp);
                results = {
                    faceLandmarks: raw.faceLandmarks?.map(face =>
                        face.map(lm => ({ x: lm.x, y: lm.y, z: lm.z }))
                    ),
                    faceBlendshapes: raw.faceBlendshapes?.map(bs => ({
                        categories: bs.categories.map(c => ({
                            categoryName: c.categoryName,
                            score: c.score
                        }))
                    }))
                };
            } else if (taskType === 'POSE') {
                const raw = poseLandmarker.detectForVideo(imageBitmap, timestamp);
                results = {
                    poseLandmarks: raw.landmarks?.map(pose =>
                        pose.map(lm => ({ x: lm.x, y: lm.y, z: lm.z }))
                    )
                };
            }

            self.postMessage({
                type: 'RESULT',
                taskType,
                results,
                timestamp
            });

            imageBitmap.close();
        } catch (err) {
            self.postMessage({ type: 'ERROR', message: `Process Error: ${err.message}`, stack: err.stack });
        }
    }
};
