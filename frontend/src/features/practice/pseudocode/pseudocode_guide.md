# 🦆 Pseudocode Practice Unit: File Guide & Architecture

이 문서는 **Coduck Wars (Pseudo Practice)** 모듈의 파일 구조와 각 파일의 역할을 정리한 가이드입니다. 신규 스테이지 추가나 로직 수정 시 참고하십시오.

---

## 📂 디렉토리 구조 및 파일 역할

### 1. 핵심 컴포넌트 & 스타일
*   **`CoduckWars.vue`**: 모듈의 메인 엔트리 포인트입니다. 진단(Diagnostic), 설계(Pseudo Write), 구현(Implementation), 평가(Evaluation)의 전체 흐름을 관리하는 최상위 UI 컴포넌트입니다.
*   **`monaco-styles.css`**: Monaco Editor 및 에디터 주변 레이아웃(라인 넘버, 스크롤바 등)의 커스텀 스타일을 담고 있습니다.

### 2. 비즈니스 로직 (Composables)
*   **`useCoduckWars.js`**: 게임의 모든 상태 보관 및 로직을 처리합니다.
    *   HP, 점수, 현재 단계(Phase) 관리
    *   AI 평가 요청 (`generateEvaluation`) 및 결과 가공
    *   시스템 로그 기록 및 스테이지 전환 로직
*   **`useMonacoEditor.js`**: Monaco Editor 인스턴스 설정 및 조작 헬퍼입니다.
    *   에디터 초기 설정 (ReadOnly 모드, 테마 등)
    *   모듈 클릭 시 에디터에 코드 자동 삽입 (`insertCodeSnippet`)

### 3. 데이터 및 API
*   **`data/stages.js`**: 총 10개 스테이지의 모든 시나리오 데이터가 정의되어 있습니다.
    *   미션 제목, 인터뷰 질문/옵션, Python 템플릿 코드, 제공 스니펫
*   **`api/pseudocodeApi.js`**: AI와의 통신 및 로컬 검증 역할을 수행합니다.
    *   의사코드와 실제 코드 간의 키워드 정합성 체크 (`checkConsistency`)
    *   AI 프록시 서버 호출 로직
*   **`evaluationRubric.js`**: AI가 사용자를 평가할 때 사용하는 '채점 기준표'입니다.
    *   프롬프트 템플릿, 우수/부족 사례(Few-shot), 평가 메트릭 정의

### 4. 서브 컴포넌트
*   **`components/LogicMirrorGuidebook.vue`**: 설계 단계에서 사용자에게 가이드를 제공하는 사이드바 컴포넌트입니다.

---

## 🛠️ 개발 및 유지보수 가이드

### 신규 스테이지 추가 방법
1.  `data/stages.js`의 `aiQuests` 배열에 새로운 객체를 추가합니다.
2.  필수 필드: `id`, `title`, `interviewQuestions`, `pythonTemplate`, `snippets`를 작성합니다.
3.  필요시 `evaluationRubric.js`에 해당 스테이지에 대한 특화된 평가 기준(Key terms)을 추가합니다.

### 평가 로직 수정 방법
*   전체적인 평가 비중(40:60)이나 점수 계산식은 `useCoduckWars.js`의 `generateEvaluation` 함수를 수정하세요.
*   AI의 말투나 평가 관점을 수정하려면 `backend/core/views/ai_view.py`의 `system_prompt`를 조정해야 합니다.

---

## 🗑️ 정리된 파일 목록 (삭제 권장)
다음 파일들은 개발 중 생성된 임시 파일이거나 중복된 정보이므로 삭제를 권장합니다.
- `PHASE4_HTML_REPLACEMENT.html`: 리팩토링 중 사용된 임시 코드 조각
- `MONACO_SETUP_GUIDE.txt`: `useMonacoEditor.js`에 통합된 설정 가이드
- `README.txt`: 본 가이드 문서로 대체 가능

---

*Last Updated: 2026.02.09*
