# 의사코드 학습 고도화 및 유튜브 연동 실행 계획서

수정일: 2026-02-14
작성자: Antigravity

본 계획서는 사용자의 요구사항(맞춤형 복기 학습, 비속어 필터링, 유튜브 API 연동)을 반영하기 위한 구체적인 수정 사항을 담고 있습니다.

## 1. 비속어 및 무의미한 입력 필터링 (Backend)

### 1.1. 필터링 로직 구현 (`pseudocode_evaluation.py`)
- **비속어 필터**: 한국어 비속어 리스트를 사전에 정의하여 입력값 포함 여부 확인.
- **무의미 입력 필터**: 단순 자음/모음 나열(예: 'ㅋㅋㅋ', 'ㅎㅎㅎ'), 무의미한 반복 단어, 너무 짧은 입력을 감지.
- **처리**: 필터링된 경우 "복기 학습 모드(Recovery Mode)"로 강제 전환하며, 적절한 시니어 조언("정성을 담은 설계가 필요합니다.")을 제공.

## 2. 맞춤형 복기 학습 창 (Frontend/Backend)

### 2.1. 복기 학습 시나리오 (Recovery Mode)
- **트리거**: 
  - 점수가 60점 미만이거나 AI가 '무성의'로 판단한 경우.
  - 비속어/무의미 필터에 걸린 경우.
- **기능**:
  - '아키텍트의 청사진(Python 코드)'을 먼저 보여주고, 이를 자연어로 다시 서술하도록 유도.
  - 복기 학습을 통한 재도전 시 최종 점수는 최대 80점으로 제한.

### 2.2. 화면 및 로직 수정
- **`useCoduckWars.js`**: `isRecoveryMode` 상태 관리 추가. 복기 학습 제출 시 전용 API 호출 또는 플래그 처리.
- **`CoduckWars.vue`**: 복기 학습 전용 모달 또는 오버레이 영역 구현. Python 코드 뷰어와 자연어 입력창 포함.

## 3. 유튜브 API 기반 단계별 영상 큐레이션 (Backend/Frontend)

### 3.1. 유튜브 API 연동 (`youtube_service.py` 신규 생성)
- **기능**: `GOOGLE_API_KEY`를 사용하여 취약 지표(설계력, 정합성 등)와 관련된 실시간 교육 영상 검색.
- **검색어 매핑**:
  - 설계력 부족 -> "머신러닝 파이트라인 설계 원칙"
  - 정합성 부족 -> "Data Leakage 방지"
  - 예외처리 부족 -> "MLOps 데이터 드리프트"

### 3.2. 단계별 큐레이션 구현 (`learningResources.js` 및 UI)
- 기존 하드코딩된 리소스를 API 결과로 대체.
- 학습 단계(입문, 중급, 마스터)에 맞는 영상 큐레이션 기능 강화.

## 4. 상세 수정 파일 및 내용

1.  **Backend (`backend/core/views/pseudocode_evaluation.py`)**:
    - `filter_content()` 함수 추가 및 평가 로직 최상단에 배치.
    - 점수 60점 이하 시 `is_recovery_eligible: true` 반환.
2.  **Backend (`backend/core/services/youtube_service.py`)**:
    - 유튜브 검색 API 연동 및 결과 파싱.
3.  **Frontend (`frontend/src/features/practice/pseudocode/composables/useCoduckWars.js`)**:
    - 복기 학습 진입 및 제출 로직 추가.
    - 점수 캡(80점) 적용.
4.  **Frontend (`frontend/src/features/practice/pseudocode/CoduckWars.vue`)**:
    - 복기 학습 UI 컴포넌트 추가.
    - 동적 유튜브 큐레이션 카드 UI 개선.

---
**보고**: 위 계획에 따라 수정을 진행하겠습니다. 특히 비속어 필터링은 교육적 환경 유지를 위해 엄격히 적용하며, 유튜브 API는 실시간성을 확보하여 학습 효율을 높일 것입니다.
