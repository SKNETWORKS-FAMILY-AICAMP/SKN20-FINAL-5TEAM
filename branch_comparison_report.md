# 🦆 pseudo_tts vs main 브런치 비교 분석 보고서

이 보고서는 `pseudo_tts` 브런치와 `main` 브런치의 주요 차이점을 분석한 결과입니다. 특히 **수도코드(Pseudocode) 연습 모듈**과 관련된 소스 코드의 변화를 중점적으로 다룹니다.

---

## 📌 1. 개요 (Overview)

*   **main**: 현재 프로젝트의 표준이 되는 브런치로, 안정적인 검증 로직과 최신 프론트엔드 UI를 포함하고 있습니다.
*   **pseudo_tts**: Web Speech API를 활용한 **음성 안내(TTS)** 기능과 관련 사운드 자산 및 초기 시나리오 검증 로직이 포함된 기능 브런치입니다.

---

## 🛠️ 2. 주요 차이점 분석

### 🔊 2.1 TTS (Text-to-Speech) 기능 및 자산
*   **`pseudo_tts` 브런치의 특징**:
    *   `frontend/src/utils/tts.js`: `SpeechSynthesisUtterance`를 활용한 한국어 음성 출력 유틸리티가 구현되어 있습니다.
    *   오리(Coduck) 캐릭터의 성격에 맞춰 피치(Pitch)를 조정(1.2)하는 등의 디테일이 포함됩니다.
    *   `frontend/public/assets/audio/`: `coduck_wars.mp4`, `synopsis_bgm.mp3` 등 시나리오 몰입을 위한 배경음 및 효과음 자산이 추가되었습니다.
*   **현재 상태**: `main` 브런치에는 해당 유틸리티 호출이 대량으로 포함된 로직들이 `not_use` 폴더로 이동되거나, TTS 호출부가 제거된 상태로 최적화되어 있습니다.

### 📝 2.2 수도코드 검증 로직 (Pseudocode Validation)
*   **입력 제한 강화**:
    *   `main`: 무성의한 입력을 방지하기 위해 최소 글자수 제한을 **15자**로 강화하였습니다.
    *   `pseudo_tts`: 초기 버전으로 최소 글자수가 **5자**로 설정되어 있습니다.
*   **검증 라이브러리 확장**:
    *   `main`에는 `data/quick_fix_validation.js`가 추가되어 즉각적인 피드백을 위한 가벼운 검증 로직이 강화되었습니다.
    *   `stages.js` 내에 각 스테이지별 `validation` 및 `codeValidation` 키가 추가되어 정밀한 아키텍처 검증이 가능해졌습니다.

### 📂 2.3 파일 구조 및 관리
*   **Legacy 코드 분리**: `main` 브런치는 TTS 기능이 통합된 초기 버전의 복잡한 로직들을 `frontend/src/features/practice/not_use/` 디렉토리로 이동시켜 코드를 정리했습니다.
*   **가이드 문서**: `pseudocode_guide.md` 파일이 `main`에서는 삭제(또는 통합)되었으나, `pseudo_tts`에는 아키텍처 설명을 위해 남아 있습니다.

---

## 📊 3. 상세 파일 비교 (주요 변경 사항)

| 파일 경로 | 주요 변경 내용 | 비고 |
| :--- | :--- | :--- |
| `backend/core/views/ai_view.py` | AI 평가 로직 강화 및 gpt-4o-mini 모델 통합 | `main`에 반영됨 |
| `frontend/src/utils/tts.js` | Web Speech API 기반 음성 출력 클래스 구현 | `pseudo_tts` 핵심 |
| `frontend/src/features/practice/pseudocode/utils/PseudocodeValidator.js` | 신뢰도 검사 강화 (최소 5자 → 15자) | `main` 최적화 |
| `frontend/src/features/practice/pseudocode/data/stages.js` | 스테이지별 검증 규칙(Validation Lib) 매핑 추가 | `main` 기능 추가 |
| `frontend/public/assets/audio/` | 시나리오 BGM 및 사운드 효과 자산 추가 | `pseudo_tts`에서 추가 |

---

## 💡 4. 종합 분석 결과

`pseudo_tts` 브런치는 **사용자 경험(UX) 측면**에서 소리라는 요소를 도입하여 학습의 재미를 높이려던 시도가 돋보이는 브런치입니다. 현재 `main` 브런치는 이 `pseudo_tts`의 성과를 대부분 흡수(Merge)한 뒤, **코드의 안정성**과 **무성의한 입력에 대한 엄격한 필터링**을 강화하는 방향으로 발전했습니다.

수도코드 관련 소스를 가장 최신 상태로 유지하고 싶다면 `main` 브런치를 사용하되, TTS 기능의 상세한 구현부를 참고하려면 `pseudo_tts`의 `frontend/src/utils/tts.js`와 `not_use` 폴더 내의 호출 로직을 확인하는 것이 좋습니다.

---
*보고서 생성일: 2026-02-19*
