# AI 비전 분석 시스템 통합 문서

**작성일자:** 2026년 2월 24일
**대상 주요 파일:**
- `frontend/src/features/interview/composables/useVisionAnalysis.js` (상태 관리 및 분석 로직)
- `frontend/public/workers/visionWorker.js` (비동기 추론 워커)
- `frontend/src/features/interview/components/VisionAnalysisReport.vue` (결과 UI)

---

## 1. 구현 계획 (Implementation Plan)

AI 모의 면접 중 지원자의 안면(시선/표정)과 상반신(자세)을 실시간으로 추적 및 분석하여, 면접 종료 후 종합적인 태도 평가 리포트를 제공하는 핵심 기능 3가지를 구현합니다.

> [!NOTE]
> 영상 처리 방식에 있어 백엔드로 초당 수십 장의 이미지를 전송(서버 부하 및 통신 지연 발생)하는 방식 대신, 지원자의 브라우저 내에서 연산을 처리하는 **Google MediaPipe (WebAssembly 기법)** 도입을 강력히 제안합니다. 이는 빠르고(Zero-Latency), 사용자 비디오가 밖으로 새어 나가지 않아 프라이버시 문제도 해결됩니다.

### 1-1. `MediaPipe` 라이브러리 연동 준비
구글의 최신 `tasks-vision` 라이브러리를 설치하여 브라우저 내장(Client-side) AI 모델을 가동합니다.
- `npm install @mediapipe/tasks-vision`
- CDN 차단 환경을 우회하기 위해 WASM 파일은 로컬 번들로 제공합니다: `/workers/mediapipe/wasm`

### 1-2. Frontend Core Logic — `useVisionAnalysis.js` [IMPLEMENTED]
카메라의 비디오 엘리먼트(`videoElement`)를 받아와 내부적으로 초당 2회의 프레임을 샘플링하고 분석합니다.
- **Gaze Tracking (시선 처리)**: `FaceLandmarker`의 Head Pose Estimation(Yaw, Pitch)을 주지표로 활용하여 얼굴의 정면 지향 여부를 판단합니다. 동공 추적(Pupil Tracking) 대신 '전체적인 시선의 방향성' 위주로 기록합니다.
- **Emotion Detection (표정/감정 분석)**: 52개의 Face Blendshapes(근육 수치) 데이터를 바탕으로 긍정(미소), 부정(긴장), 무표정의 비율을 누적 계산합니다.
- **Pose Estimation (자세 추적)**: `PoseLandmarker`를 이용해 어깨 수평도와 횡방향 기울기를 분석하여 불량 자세의 빈도를 체크합니다.

### 1-3. 하드웨어 호환성 및 폴백(Fallback) 전략

**[WebGL 2.0 가용성 체크]**
- **문제**: MediaPipe WASM 가속은 WebGL 2.0을 필수 요구하며, 구형 기기나 GPU 드라이버 이슈가 있는 브라우저에서는 엔진이 작동하지 않을 수 있습니다.
- **대응**: `useVisionAnalysis` 초기화 시 WebGL 2.0 컨텍스트 지원 여부를 먼저 검사합니다. 미지원 시 경고 토스트를 띄우고, 비전 분석 모듈을 활성화하지 않은 채 면접(음성/텍스트)은 정상 진행하도록 Fallback 처리합니다.
  ```javascript
  checkWebGL2() = !!canvas.getContext('webgl2')
  ```

### 1-4. Frontend Orchestrator Integration

**`useInterview.js` [INTEGRATED]**
- 면접 시작 시 `useVisionAnalysis`의 엔진 초기화(`initEngine()`).
- 면접 종료 시 누적된 데이터를 정산(`stopAndGetReport()`), API로 저장(`saveVisionAnalysis(sessionId, report)`).

**`MockInterview.vue` [INTEGRATED]**
- 기존 면접 세션 종료 훅에서 비전 분석 결과를 받아오도록 로직 수정.
- WebcamDisplay의 `@ready` 이벤트에서 `visionSystem.startAnalysis(videoEl)` 호출.

### 1-5. Report UI Component — `VisionAnalysisReport.vue` [IMPLEMENTED]
면접이 종료되면 결과를 띄워줄 최종 UI 컴포넌트입니다.
- **시선 집중도(Gaze)**: SVG 기반 원형 프로그레스 링 (에메랄드 그린).
- **표정 밸런스(Emotion)**: 이모지 + 카테고리별 퍼센트 분류.
- **자세 안정성(Posture)**: SVG 기반 원형 프로그레스 링 (앰버 컬러).

---

## 2. 사용 기술 스택 (Tech Stack)

비전 분석 시스템은 브라우저 환경에서 고성능의 AI 추론을 실시간으로 수행하기 위해 다음과 같은 현대적인 웹 기술을 혼합하여 구축되었습니다.

- **Google MediaPipe Tasks Vision:** 클라이언트 사이드(브라우저)에서 기계학습 모델을 돌리기 위한 핵심 프레임워크입니다. 별도의 백엔드 서버 비용이나 통신 지연시간(Latency) 없이, 사용자 기기의 자원을 활용하여 얼굴(FaceLandmarker) 및 자세(PoseLandmarker)의 핵심 특징점(Landmarks)과 안면 구조(Blendshapes)를 실시간 추출합니다.
  - **FaceLandmarker**: `face_landmarker.task` (float16), 478개 랜드마크 + 52개 Blendshapes 출력
  - **PoseLandmarker**: `pose_landmarker_lite.task` (float16), 33개 관절 좌표 출력
  - **RunningMode**: VIDEO, **Delegate**: GPU
- **Web Workers API:** MediaPipe 추론 과정을 전용 백그라운드 워커 스레드(`visionWorker.js`)로 완전히 분리하여 메인(UI) 스레드의 블로킹 없이 부드러운 화면 갱신을 보장합니다.
- **WebGL 2.0 / WASM (WebAssembly):** MediaPipe가 브라우저 내에서 GPU 가속 처리되기 위한 필수 기술이며, WASM 파일은 로컬 번들(`/workers/mediapipe/wasm`)로 제공하여 CDN 의존성을 제거합니다.
- **Vue 3 (Composition API):** 자체 제작한 `useVisionAnalysis` 컴포저블을 통해, 비동기 비전 워커의 상태(로딩 완료 여부 `isReady`, 현재 분석 중 `isAnalyzing`, 집계된 통계 결과, 에러 메시지 `initError`)를 반응형(Reactivity) 데이터로 UI와 연결합니다.

---

## 3. 시스템 아키텍처

현재 구현된 카메라 기반 AI 비전 분석 시스템은 사용자의 면접 태도(시선, 표정, 자세)를 실시간으로 분석하여 점수화하고 피드백을 제공하는 기능을 수행합니다.

모든 무거운 모델 추론 연산은 **Web Worker (`visionWorker.js`)**로 분리되어 비동기로 처리됩니다.

### 3-1. 분석 엔진 및 샘플링 방식
- **샘플링 주기**: 웹캠 영상을 **500ms마다 한 번(2 FPS)** 캡처하여 워커에 전송합니다. `createImageBitmap()`으로 프레임을 추출하고, Transferable Objects로 워커에 전달하여 메모리 복사 없이 이전합니다. 처리 후 즉시 dispose합니다.
- **스위칭 로직**: 들어오는 프레임을 교차(짝수 번째=`FACE`, 홀수 번째=`POSE`)하여 분석합니다. 연산 부하를 절반으로 줄이며, 샘플 수는 `faceSamples`와 `poseSamples`로 별도 집계됩니다.
- **워커 메시지 흐름**:
  1. 메인 스레드 → 워커: `{ type: 'PROCESS_FRAME', imageBitmap, timestamp, taskType }`
  2. 워커 → 메인 스레드: `{ type: 'RESULT', landmarks, blendshapes }` (WASM 객체를 순수 JS 객체로 직렬화하여 반환)

---

## 4. 주요 분석 로직 (휴리스틱)

### 4-1. 시선 및 고개 유지 분석 (Head Orientation)
얼굴 인식 결과 중 코(index 1), 왼쪽 눈(index 33), 오른쪽 눈(index 263)의 좌표를 기반으로 고개의 각도를 판별합니다.

- **좌우 회전 (Yaw Offset):** 코가 두 눈 사이의 중앙에서 얼마나 벗어났는지 계산합니다. 웹캠 좌우 반전을 고려하여 두 눈 간격은 절대값을 사용합니다.
  - `수식: abs(코.x - 눈중앙.x) / abs(오른쪽눈.x - 왼쪽눈.x)`
  - 계산된 값이 **0.15 미만**일 때 정면으로 간주합니다.
- **상하 숙임 (Pitch Offset):** 코끝과 양 눈 중앙의 Y축 간격 비율로 고개를 과도하게 숙이거나 치켜들었는지 판별합니다.
  - `수식: (코.y - 눈중앙.y) / 양안거리`
  - 값이 **0.4 ~ 0.95 사이**에 속할 때만 정면 응시로 인정합니다.
- 좌우(Yaw) 및 상하(Pitch) 양쪽 조건을 모두 만족할 때만 `isFacingForward = true`로 판정합니다.
- **예외 처리 (이탈 페널티):** 얼굴이 화면에서 이탈하면 `faceSamples`(분모)는 증가하지만 `gazeStableTicks`(분자)는 누적되지 않아 점수가 깎입니다.

### 4-2. 표정 분석 (Emotion Mapping)
MediaPipe의 `Face Blendshapes`(안면 근육 추적)를 활용하여, 미소와 긴장을 수치로 변환합니다.

- **긍정 (Smile):** 양쪽 입꼬리 당김 지수(`mouthSmileLeft`, `mouthSmileRight`)의 평균이 **0.15 초과**일 때 판정합니다. 면접 환경에서 활짝 웃기 힘든 점을 고려해 옅은 미소도 감지하도록 임계값을 완화했습니다. (기존 0.4 → 0.15)
- **긴장 (Tension):** 입술 압착 지수(`mouthPress`)가 **0.2 초과**일 때 굳어있거나 긴장한 상태로 분류합니다.
- **중립 (Neutral):** 위 두 가지에 해당하지 않으면 무표정으로 집계됩니다.

### 4-3. 자세 유지 분석 (Posture Analysis)
코(index 0), 왼쪽 어깨(index 11), 오른쪽 어깨(index 12)의 2D 좌표를 활용해 자세 안정성을 측정합니다. 3프레임 이동 평균(Moving Average)으로 노이즈를 필터링한 후 판별합니다.

- **어깨 수평 (Y축):** 좌우 어깨의 높낮이 차이가 **0.07 미만**이어야 수평으로 인정합니다.
  - `수식: abs(왼어깨.y - 오른어깨.y) < 0.07`
- **횡방향 기울기 (X축):** 코와 어깨 중심 사이의 좌우 이탈 비율이 **0.08 미만**이어야 합니다. 0.10 이상이면 더 강한 경고 메시지를 표시합니다.
  - `수식: abs(코.x - 어깨중심.x) / 어깨너비 < 0.08`
- 두 조건(수평 + 횡방향)을 모두 통과해야 1회 '바른 자세'(`poseStableTicks`)로 카운트됩니다.

---

## 5. 세부 지표 산출 원리

본 섹션은 "AI 비언어 태도 분석 결과" 화면에 나타난 각종 지표가 시스템 내부에서 어떻게 측정되고 산출되는지 설명합니다.

### 5-1. 시선 집중도 (Gaze Focus) 점수 산출
- **수식**: `gazeScore = Math.min(100, Math.round((gazeStableTicks / faceSamples) * 100))`
- 전체 얼굴 감지 샘플(`faceSamples`) 중 정면 응시 판별(`gazeStableTicks`) 횟수의 비율을 퍼센트로 변환합니다.

### 5-2. 자세 유지력 (Posture) 점수 산출
- **수식**: `poseScore = Math.min(100, Math.round((poseStableTicks / poseSamples) * 100))`
- 전체 자세 샘플(`poseSamples`) 중 '바른 자세'로 판별된 횟수(`poseStableTicks`)의 비율을 퍼센트로 변환합니다.
- 0%로 측정된 경우, 검사 기간 내내 어깨 수평도 또는 횡방향 기울기 조건 중 하나라도 지속적으로 범위를 벗어났음을 의미합니다.

### 5-3. 표정 밸런스 (Emotions) 점수 산출
- **수식**:
  ```
  smilePct   = Math.round((emotions.smile   / total) * 100)
  tensionPct = Math.round((emotions.tension / total) * 100)
  neutralPct = Math.max(0, 100 - smilePct - tensionPct)
  ```
- 전체 표정 데이터 중 각 카테고리가 차지하는 비중을 계산합니다. 지배적인 감정(`dominantEmotion`)은 세 값 중 가장 높은 항목으로 결정됩니다.

### 5-4. 종합 안정성 (Stability) 점수 산출
- **시선 집중도와 자세 유지력의 평균**으로 산출됩니다.
- `수식: Math.round((gazeScore + poseScore) / 2)`
- 예시: (99 + 0) / 2 = 49.5 → **50**

### 5-5. 최종 리포트 구조
```javascript
{
  status: 'ok' | 'no_data',
  sampleCount: number,       // 전체 샘플 수
  faceSampleCount: number,   // 얼굴 분석 샘플 수
  poseSampleCount: number,   // 자세 분석 샘플 수
  error: null | string,
  gazeScore: 0-100,
  poseScore: 0-100,
  emotions: { smile: number, tension: number, neutral: number },
  events: string[]           // 타임스탬프 포함 이벤트 로그 (최대 50개)
}
```

---

## 6. 실시간 피드백 및 최종 평가 산출

### 6-1. 실시간 토스트 경고 (Cooldown System)
사용자가 면접 중 좋지 않은 행동이 반복되면 실시간 경고 메시지를 발송합니다. 같은 종류의 알람은 **최소 10초(10000ms)의 쿨다운** 타이머를 거쳐 한 번씩만 발송됩니다.

| 조건 | 토스트 메시지 |
|------|-------------|
| Yaw/Pitch 이탈 | "카메라를 정면으로 바라봐 주세요." |
| 어깨 기울기 (`< 0.07` 미충족) | "자세가 기울어져 있습니다. 바르게 앉아주세요." |
| 횡방향 쏠림 (`>= 0.10`) | "상체가 한쪽으로 쏠려 있습니다." |

### 6-2. 최종 평가 방어 로직
- `Math.min(100, ...)` 및 `Math.max(0, ...)` 적용으로 100 초과 또는 음수 방지.
- `sampleCount > 0` 조건 미충족 시 `status: 'no_data'` 반환, UI에서 분석 불충분 경고 표시.
- 결과는 `VisionAnalysisReport.vue` 컴포넌트 내 SVG 원형 프로그레스 링과 이모지 바로 시각화됩니다.

---

## 7. 행동 로그 기록 조건 (BEHAVIORAL LOGS)
분석 진행 중 특정 수치가 임계점을 넘어갈 때 로그 기록과 함께 알림을 남깁니다. 이벤트 배열에 최대 **50개**까지 저장됩니다.

- **`[시간] 시선이 정면을 벗어났습니다.`**
  - Yaw 이탈 값이 0.25를 초과할 때 발생합니다.
  - 10초 쿨다운(`TOAST_COOLDOWN`) 적용.

- **`[시간] 자연스러운 미소 감지 (긍정적 인상)`**
  - 입꼬리 당김 지수 평균이 **0.4 초과** 시 감지됩니다. (표정 감지 임계값 0.15와 별도)
  - 얼굴 분석 **20프레임마다(약 20초 간격)** 1번씩 로그를 남겨 빈도를 조절합니다.

- **`[시간] 긴장된 표정 감지`**
  - `mouthPress > 0.2` 조건 충족 시 발생합니다.
  - 동일하게 20프레임 주기로 로그 빈도를 조절합니다.

---

## 8. 검증 계획 (Verification Plan)

### 8-1. Automated Tests
유닛 테스트 스크립트를 작성하여 임의의 가짜 이미지 데이터를 주입했을 때 시선 및 표정 점수가 정확히 계산(Math.abs, Threshold 처리 등)되는지 확인합니다.

### 8-2. Manual Verification
개발자가 웹캠을 켜고 면접을 시작한 상태에서, 의도적으로 아래 액션을 취한 뒤 면접을 끝냈을 때 해당 데이터가 결과표에 극단적으로 잘 잡혔는지 확인합니다.
- "화면 바깥 쳐다보기" → 시선 집중도 하락 확인
- "찡그린 표정 짓기" → 긴장(Tension) 비율 상승 확인
- "몸을 한쪽으로 심하게 기울이기" → 자세 유지력 하락 확인
