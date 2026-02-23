# Vision Analysis (AI 비전 면접관) 고도화

AI 모의 면접 중 지원자의 안면(시선/표정)과 상반신(자세)을 실시간으로 추적 및 분석하여, 면접 종료 후 종합적인 태도 평가 리포트를 제공하는 핵심 기능 3가지를 구현합니다.

## User Review Required

> [!NOTE]
> 영상 처리 방식에 있어 백엔드로 초당 수십장의 이미지를 전송(서버 부하 및 통신 지연 발생)하는 방식 대신, 지원자의 브라우저 내에서 연산을 처리하는 **Google MediaPipe (WebAssembly 기법)** 도입을 강력히 제안합니다. 이는 빠르고(Zero-Latency), 사용자 비디오가 밖으로 새어 나가지 않아 프라이버시 문제도 해결됩니다. 동의하시나요?

## Proposed Changes

---

### 1. `MediaPipe` 라이브러리 연동 준비
구글의 최신 `tasks-vision` 라이브러리를 설치하여 브라우저 내장(Client-side) AI 모델을 가동합니다.
* `npm install @mediapipe/tasks-vision`

### 2. Frontend Core Logic
분석 엔진 역할을 할 핵심 코어 모듈을 제작합니다.

#### [NEW] `frontend/src/composables/useVisionAnalysis.js`
카메라의 오디오/비디오 스트림(`videoStream`)을 받아와 내부적으로 초당 N회의 프레임을 샘플링하고 분석합니다.
* **Gaze Tracking (시선 처리)**: 
    * **방법**: `FaceLandmarker`의 **Head Pose Estimation**(Pitch, Yaw, Roll)을 주지표로 활용하여 얼굴의 정면 지향 여부를 판단합니다.
    * **한계 기술**: 일반 웹캠 환경에서의 동공 추적(Pupil Tracking)은 안경 반사, 저해상도(720p) 등으로 인해 정밀도가 낮으므로, 리포트에는 '동공의 세밀한 움직임' 대신 '전체적인 시선의 방향성' 위주로 기록함을 명시합니다.
* **Emotion Detection (표정/감정 분석)**: 52개의 Face Blendshapes(근육 수치) 데이터를 바탕으로 긍정(미소), 부정(찡그림/긴장), 무표정 등의 비율을 누적 계산합니다.
* **Pose Estimation (자세 추적)**: `PoseLandmarker`를 이용해 양측 어깨의 수평 수치와 거북목(어깨 대비 머리의 상대 위치) 여부를 분석해 불량 자세의 빈도를 체크합니다.

### 3. 하드웨어 호환성 및 폴백(Fallback) 전략
MediaPipe의 효율적인 연산을 위해 브라우저 환경에 대한 대응책을 마련합니다.

#### [WebGL 2.0 가용성 체크]
* **문제**: MediaPipe WASM 가속은 WebGL 2.0을 필수 요구하며, 구형 기기나 GPU 드라이버 이슈가 있는 브라우저에서는 엔진이 작동하지 않을 수 있습니다.
* **대응**: 
    - `useVisionAnalysis` 초기화 시 WebGL 2.0 컨텍스트 지원 여부를 먼저 검사합니다.
    - **미지원 시**: "현재 기기 환경에서 시선 분석 기능을 사용할 수 없습니다"라는 경고 토스트를 띄우고, 비전 분석 모듈을 활성화하지 않은 채 면접(음성/텍스트)은 정상 진행하도록 Fallback 처리합니다.

### 3. Frontend Orchestrator Integration
분석 엔진을 기존 면접 시스템에 연결합니다.

#### [MODIFY] [frontend/src/composables/useInterviewSession.js](file:///d:/SKN20-FINAL-5TEAM/frontend/src/composables/useInterviewSession.js)
* 면접 시작 시 `useVisionAnalysis`의 타이머를 구동(`startAnalysis()`).
* 면접 종료 시 누적된 데이터를 정산(`stopAndGetReport()`).

#### [MODIFY] [frontend/src/components/MockInterviewRoom.vue](file:///d:/SKN20-FINAL-5TEAM/frontend/src/components/MockInterviewRoom.vue)
* 기존 면접 세션 종료 훅에서 비전 분석 결과를 받아오도록 로직 수정.
* 화면 최하단(혹은 결과 페이지)에 비전 데이터의 결과를 시각적으로 표현할 수 있도록 구조체 배치.

### 4. Report UI Component
면접이 비활성화(종료)되면 결과를 띄워줄 최종 UI 컴포넌트입니다.

#### [NEW] `frontend/src/components/VisionAnalysisReport.vue`
* **시선 집중도(Gaze)**: 레이더 차트 혹은 프로그레스 바.
* **표정 변화(Emotion)**: 도넛 차트 (긍정 %, 무표정 %, 긴장 %).
* **자세 안정성(Pose)**: 타임라인 그래프 (불량 자세가 감지된 시간대 마킹).

---

## Verification Plan

### Automated Tests
* 유닛 테스트 스크립트를 작성하여 임의의 가짜 이미지 데이터를 주입했을 때 시선 및 표정 점수가 정확히 계산(Math.abs, Threshold 처리 등)되는지 확인.

### Manual Verification
* 개발자가 웹캠을 켜고 면접을 시작한 상태에서, 의도적으로 "화면 바깥 쳐다보기", "찡그린 표정 짓기", "몸을 한쪽으로 심하게 기울이기" 액션을 취한 뒤, 면접을 끝냈을 때 해당 데이터가 결과표에 극단적으로 잘 잡혔는지 확인.
