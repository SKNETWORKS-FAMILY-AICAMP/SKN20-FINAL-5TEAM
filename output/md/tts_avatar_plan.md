# TTS 아바타 립싱크 기능 구현 계획서

## 1. 개요

면접 세션에서 AI 면접관을 정적 텍스트가 아닌 **립싱크 아바타 영상**으로 표현하는 기능.
OpenAI TTS로 생성한 음성과 아바타 이미지를 결합해 실시간성 있는 영상을 제공한다.

---

## 2. 전체 아키텍처

```
[Frontend]
  MockInterview.vue
    └─ TTSManager (tts.js)
         └─ POST /api/core/tts/synthesize/  → 음성(mp3) 반환
         └─ (추가 예정) POST /api/core/interview/video/generate/  → 립싱크 영상 반환

[Backend - Django (port 8000)]
  AvatarVideoView
    └─ musetalk_service.generate_video(image, audio) → mp4 반환
         ├─ MUSETALK_SERVICE_URL 있으면 → musetalk 컨테이너에 HTTP 위임
         └─ 없으면 → 로컬 MuseTalk 직접 실행 (또는 Mock fallback)

[MuseTalk 컨테이너 (port 8001, GPU profile)]
  musetalk_server.py (FastAPI)
    ├─ POST /generate  → 립싱크 영상 생성
    └─ POST /idle      → Idle 루프 영상 생성
```

---

## 3. 구성 요소별 현황

### 3-1. 아바타 이미지
- 경로: `backend/media/avatars/interviewer_man.png`, `interviewer_woman.png`
- `avatar_type` 파라미터로 남/여 구분
- **현재 상태**: 이미지 파일 준비 필요 (경로만 정의됨)

### 3-2. TTS (음성 생성)
- `frontend/src/features/interview/tts.js` — TTSManager 클래스
- OpenAI TTS API 사용 (`nova` 음성, 1.1배속)
- 큐 기반 순차 재생 지원
- **현재 상태**: 구현 완료, 단독 동작 중

### 3-3. MuseTalk 서비스
- `backend/core/services/interview/musetalk_service.py` — MuseTalkService (싱글톤)
- 기능:
  - `generate_video(image, audio, output)` — 실제 립싱크 영상 생성
  - `get_idle_loop(image, output)` — Idle 루프 영상 생성
  - `_mock_generate()` — OpenCV 기반 Mock fallback
- **현재 상태**: 구현 완료, Docker 빌드 오류 해결 중

### 3-4. MuseTalk FastAPI 서버
- `backend/musetalk_server.py`
- 엔드포인트: `GET /health`, `POST /generate`, `POST /idle`
- **현재 상태**: 구현 완료

### 3-5. Django API View
- `backend/core/views/interview/video_view.py` — AvatarVideoView
- 엔드포인트: `POST /api/core/interview/video/generate/`
- 파라미터: `audio_path`, `avatar_type`, `session_id`, `status`
- **현재 상태**: 구현 완료, URL 등록 확인 필요

### 3-6. 모델 가중치
- 다운로드 스크립트: `backend/scripts/download_musetalk_models.py`
- 저장 경로: `backend/models/`
  - `musetalk/` — UNet 가중치
  - `dwpose/` — 자세 분석 모델
  - `sd-vae-ft-mse/` — VAE 디코더
  - `GFPGANv1.4.pth` — 얼굴 화질 보정
- **현재 상태**: 다운로드 완료

### 3-7. Docker 구성
- `docker-compose.yml` — `musetalk` 서비스 (`profiles: ["gpu"]`)
- `backend/Dockerfile.musetalk` — PyTorch 2.2.1 + CUDA 12.1 기반
- **현재 상태**: `g++` 누락으로 빌드 실패 → `apt-get install g++` 추가로 수정 완료, 재빌드 중

---

## 4. 남은 작업

| # | 작업 | 우선순위 | 상태 |
|---|------|----------|------|
| 1 | Dockerfile.musetalk 빌드 성공 확인 | 높음 | 진행 중 |
| 2 | 아바타 이미지 파일 준비 (`interviewer_man.png`, `interviewer_woman.png`) | 높음 | 미완료 |
| 3 | `video_view.py` URL 라우팅 등록 확인 (`backend/core/urls.py`) | 높음 | 미확인 |
| 4 | Frontend에서 TTS 음성 → 영상 요청 연동 (TTSManager → AvatarVideoView) | 중간 | 미완료 |
| 5 | Idle 루프 영상 프론트 연동 (면접관 대기 상태 표시) | 중간 | 미완료 |
| 6 | GPU 환경 없는 개발 환경에서 Mock 모드 동작 검증 | 낮음 | 미완료 |

---

## 5. 실행 방법

### GPU 있는 환경 (전체 스택)
```bash
docker compose --profile gpu up --build
```

### GPU 없는 환경 (musetalk 제외)
```bash
docker compose up --build
# musetalk 서비스 없으면 MuseTalkService가 자동으로 Mock 모드로 동작
```

### 모델 가중치 다운로드
```bash
cd backend
python scripts/download_musetalk_models.py
```

---

## 6. 주요 파일 목록

| 파일 | 역할 |
|------|------|
| `backend/Dockerfile.musetalk` | MuseTalk GPU 컨테이너 빌드 정의 |
| `backend/musetalk_server.py` | FastAPI 서버 (포트 8001) |
| `backend/core/services/interview/musetalk_service.py` | 립싱크 서비스 로직 |
| `backend/core/views/interview/video_view.py` | Django REST API 뷰 |
| `backend/scripts/download_musetalk_models.py` | 모델 가중치 다운로드 |
| `frontend/src/features/interview/tts.js` | 프론트엔드 TTS 매니저 |
| `docker-compose.yml` | 전체 서비스 오케스트레이션 |
