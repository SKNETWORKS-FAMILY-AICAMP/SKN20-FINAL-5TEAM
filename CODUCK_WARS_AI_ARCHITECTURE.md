# Coduck Wars: AI 기반 실시간 아키텍처 서바이벌 기술 명세 (Technical Spec)

## 1. 프로젝트 비전
Coduck Wars는 단순한 코딩 교육 서비스가 아닙니다. 실시간 **Multi-Agent Orchestration**을 통해 사용자가 작성한 아키텍처의 취약점을 AI가 실시간으로 분석하고, 공학적 장애 이벤트를 발생시켜 사용자의 대응 능력을 평가하는 고난도 **AI 엔지니어링 시뮬레이션**입니다.

## 2. 핵심 기술 스택 및 개념 (Technical Pillars)

### 🤖 A. Multi-Agent Orchestration (복합 에이전트 협업 체계)
본 서비스는 단일 AI 호출 방식을 넘어, 고립된 역할을 가진 다수의 에이전트가 협력하는 오케스트레이션 모델을 따릅니다.
*   **Architectural Analyst Agent**: 사용자가 Monaco Editor에 작성하는 코드(API 설계, DB 스키마, 보안 설정)를 실시간으로 모니터링하고, 가용성(Availability)과 보안성(Security) 등 핵심 지표를 정량화합니다.
*   **Chaos/Failure Agent**: 분석 에이전트가 탐지한 취약점 정보를 수신하여 실시간으로 '장애 이벤트(Chaos Event)'를 트리거하고, 시스템을 블랙아웃 상태로 전환시켜 사용자의 순발력을 시험합니다.
*   **Pressure Interviewer Agent**: 현재 게임의 단계와 사용자의 수정 코드를 문맥적으로 이해하여, 설계 결정의 근거를 공격적으로 묻는 압박 면접 페르소나를 수행합니다.

### ⚙️ B. Finite State Machine (FSM) 기반 게임 루프
게임의 진행 상태를 상태 머신(`design` → `blackout` → `defense` → `report`)으로 관리하며, 상태 전이에 따라 AI의 페르소나와 프롬프트 지침을 동적으로 변경합니다.
*   **상태 인지형 프롬프트**: AI는 현재가 '설계 단계'인지 '장애 복구 단계'인지 명확히 구분하여 응답하며, 이를 통해 사용자에게 높은 몰입감을 제공합니다.

### ⚡ C. Event-Driven Scenario Intervention (이벤트 기반 지능형 개입)
*   정해진 코스에 따라 장애가 발생하는 것이 아니라, 사용자가 작성한 **코드의 논리적 결함에 따라 장애 종류가 결정**되는 이벤트 기반 아키텍처를 채택했습니다.
*   예시: DB 탭에서 Read Replica 설정을 누락할 경우 'DB 대역폭 폭주' 장애가 우선적으로 트리거됩니다.

### 📊 D. Real-time Design Evaluation (실시간 설계 평가 시스템)
*   **데이터 정형화(Extraction)**: LLM의 비정형 텍스트 분석 결과를 실시간 스코어보드에 반영하기 위해 전용 JSON 스키마를 활용한 데이터 추출 기법을 적용했습니다.
*   **시각적 피드백**: 실시간으로 변하는 점수 게이지바를 통해 시스템 설계의 완성도를 사용자에게 즉각적(Feedback Loop)으로 전달합니다.

## 3. AI 엔지니어 역량 증명 포인트 (Competency Proofs)

이 프로젝트는 개발자가 다음과 같은 고도의 기술적 문제를 해결할 수 있음을 증명합니다.

1.  ** Agentic Workflow 설계 능력**: 다수의 독립된 에이전트가 데이터를 주고받으며 하나의 복잡한 시나리오를 완성해나가는 '에이전틱 워크플로우' 구축 가능.
2.  **LLM 출력 제어 (JSON Mode & Framing)**: AI 응답의 형식을 완벽하게 제어하여 프론트엔드 UI/UX와 정밀하게 결합(Software Engineering + AI)시킨 경험.
3.  **지연 시간 최적화 (Latency Handling)**: 실시간 코드 분석의 부하를 조절하기 위해 비동기 분석 루프와 소켓 통신을 결합한 실시간 시뮬레이션 개발 역량.
4.  **문맥 유지 및 상태 관리 (Context Window & State)**: 장시간 이어지는 면접 세션 동안 사용자의 이전 답변과 설계 이력을 지속적으로 추적하여 일관된 논리로 반박하는 문맥 유지 시스템 설계력.

---

## 4. 핵심 기술 요약 (Tech Stack)
*   **AI Models**: GPT-4o / Claude 3.5 (에이전트 역할별 특화 프롬프트)
*   **Real-time Logic**: Socket.IO (코드 및 상태 동기화), WebRTC (화상 세션)
*   **Code Editor**: Vue-Monaco-Editor (실시간 구문 강조 및 멀티탭 지원)
*   **Evaluation Engine**: Mermaid.js (최종 설계도 시각화), Chart.js (역량 레이더 차트)
