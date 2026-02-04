# 🚀 Project Plan: AI-Powered Pseudocode Trainer

## 1. Project Overview (프로젝트 개요)
- **Goal**: 제공된 JSON 데이터를 활용하여 '수도코드(의사코드)'를 학습하고 평가받는 웹 플랫폼 구축.
- **Tech Stack**:
  - **Frontend**: Nuxt 3 (Vue.js), TailwindCSS, Pinia (Store)
  - **Core Libs**: `@guolao/vue-monaco-editor` (Code Editor), `vuedraggable` (Parsons Problem)
  - **Backend**: Nuxt Server Routes (`/server/api`)
  - **AI**: OpenAI API (GPT-4o)

## 2. Data Mapping Strategy (데이터 매핑 전략)
`problems_with_pseudocode.json`의 필드를 UI/기능에 1:1로 매핑하여 개발한다.

| JSON Field | UI Component / Logic | Description |
| :--- | :--- | :--- |
| `id` | **Routing** | 문제별 페이지 URL (`/solve/:id`) |
| `title_ko` / `description_ko` | **Left Panel** | 문제 제목 및 설명 표시 (Markdown 렌더링) |
| `examples` | **Test Cases UI** | 문자열(`"assert func(a)==b"`)을 파싱하여 **Input/Output 테이블**로 변환 |
| `pseudocode` | **Parsons Mode** | 줄바꿈(`\n`) 기준으로 분리 → 셔플 → **드래그 앤 드롭 퍼즐** 생성 |
| `pseudocode` | **Review Mode** | 사용자가 작성한 코드와 비교할 **Diff Editor의 정답 모델**로 사용 |
| `solution_code` | **AI Evaluator** | 사용자에게는 숨기고, **AI 채점 시 'Ground Truth(정답 기준)'**로 제공 |

## 3. Implementation Phases (단계별 구현 계획)

### ✅ Phase 1: Setup & Data Parsing (기반 구축)
**Goal**: 프로젝트를 초기화하고, JSON 데이터를 UI에서 사용할 수 있게 가공한다.
- [x] **Project Init**: 기존 Vite 환경 활용 (Node.js 미설치 환경 대응).
- [x] **Data Store**: `frontend/src/data/problems.json` 연동 및 Pinia Store 구현.
- [x] **Parser Utility (`utils/parser.js`)**: `assert` 구문 파싱 로직 구현.
- [x] **UI Scaffold**: `SplitLayout.vue` 컴포넌트 생성.

### ✅ Phase 2: Parsons Problem Mode (MVP)
**Goal**: 비용이 들지 않고 논리력을 키우는 '블록 맞추기' 모드를 구현한다.
- [x] **Logic**: 의사코드 셔플 및 `originalIndex` 기반 검증 로직 구현 (`useProblemStore.js`).
- [x] **UI**: HTML5 네이티브 Drag API를 활용한 `ParsonsPuzzle.vue` 구현.
- [x] **Validation**: 정답 여부 확인 및 피드백 UI 추가.

### ✅ Phase 3: Code Editor & AI Evaluation (Core)
**Goal**: 자유롭게 코드를 작성하고 AI에게 정밀 채점을 받는다.
- [x] **Editor UI**: 오른쪽 패널에 탭(Tab)을 추가하여 [블록 맞추기]와 [직접 작성] 모드 전환 (`LogicTrainer.vue`).
- [x] **Monaco Setup**: `plaintext`/`python` 모드로 에디터 설정 (`CodeEditor.vue`).
- [/] **Backend API (`server/api/evaluate.post.ts` -> Django 등)**: AI 채점 로직 설계 중.

### ✅ Phase 4: Review System (Feedback)
**Goal**: 학습 효과를 극대화하기 위해 내 코드와 모범 답안을 비교한다.
- [ ] **Diff View**: 채점 완료 후 [정답과 비교하기] 버튼 활성화.
- [ ] **Monaco Diff**:
  - **Original Model**: `pseudocode` (JSON 데이터)
  - **Modified Model**: `userCode` (사용자 입력)
  - 차이점을 시각적으로 하이라이팅하여 표시.