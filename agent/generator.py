"""
Progressive 3단계 문제 생성
GPT-4.0 mini를 사용하여 연결된 3단계 버그 수정 문제 생성
"""

import json
from agent.spec import TRACK_SPECS, PYTORCH_TRACK
from agent.llm import call_gpt_json, call_gpt


def generate_progressive(track_id: str = "pytorch_mnist") -> dict:
    """
    P1 Progressive 문제 전체 생성 (3단계)

    Args:
        track_id: 생성할 트랙 ID

    Returns:
        dict: P1 문제 JSON 객체
    """
    track_spec = TRACK_SPECS.get(track_id, PYTORCH_TRACK)

    # 1. 전체 시나리오 생성
    scenario = generate_scenario(track_spec)

    # 2. 각 단계별 생성 (Step 1 → Step 2 → Step 3)
    steps = []
    for step_spec in track_spec["steps"]:
        step = generate_step(
            step_spec,
            scenario,
            prev_steps=steps,  # 🔑 이전 단계 참조
            track_spec=track_spec # 🔑 트랙 스펙 정보 전달
        )
        steps.append(step)

    # 3. Progressive 포맷 조합
    return {
        "id": f"P-{track_id}-{hex(id(scenario))[-4:]}", # 고유 ID 생성
        "project_title": scenario["project_title"],
        "scenario": scenario["scenario"],
        "difficulty": track_spec["difficulty"],
        "totalSteps": 3,
        "steps": steps
    }


def generate_scenario(track_spec: dict) -> dict:
    """
    전체 시나리오 생성

    Args:
        track_spec: PYTORCH_TRACK 스펙

    Returns:
        dict: {"project_title": str, "scenario": str}
    """
    prompt = f"""
다음 조건으로 Progressive 디버깅 문제의 전체 시나리오를 작성하라:

트랙: {track_spec.get('track_name', track_spec.get('track', '알 수 없는 트랙'))}
컨텍스트: {track_spec.get('context', '해당 기술 스택 기반의 실무 프로젝트')}
총 3단계의 연결된 버그 수정 미션

요구사항:
1. 주어진 '트랙'과 '컨텍스트'에 부합하는 실무 상황을 반영한 자연스러운 스토리
2. 3단계의 버그가 개별적이지 않고, 하나의 프로젝트 흐름 안에서 논리적으로 연결되는 서사

출력 형식 (JSON):
{{
  "project_title": "간결한 제목 (20자 이내)",
  "scenario": "전체 스토리 (3단계 흐름 암시, 100자 이내)"
}}
"""
    return call_gpt_json(prompt)


from agent.spec import TRACK_SPECS, PYTORCH_TRACK

def generate_step(step_spec: dict, scenario: dict, prev_steps: list, track_spec: dict = PYTORCH_TRACK, failure_reason: dict = None) -> dict:
    """
    단일 단계 생성 (이전 단계 기반)

    Args:
        step_spec: 단계별 스펙 (PYTORCH_TRACK["steps"][i])
        scenario: 전체 시나리오 정보
        prev_steps: 이전 단계 리스트 (연결성 유지용)
        failure_reason: 이전 시도 실패 이유 (재생성 시 전달)

    Returns:
        dict: 단일 단계 JSON 객체
    """

    # 이전 단계 컨텍스트
    if prev_steps:
        prev_context = "\n".join([
            f"Step {s['step']}: {s['title']} - {s['bug_type_name']}"
            for s in prev_steps
        ])
        prev_code = prev_steps[-1]["correct_code"]
        prev_code_section = f"이전 단계의 correct_code를 기반으로 작성:\n{prev_code}"
    else:
        prev_context = "첫 번째 단계"
        prev_code = None
        prev_code_section = ""

    # 실패 이유 추가 (재생성 시)
    failure_section = ""
    if failure_reason:
        failure_section = f"""
⚠️ 이전 생성 시도 실패:
- Stage: {failure_reason.get('stage', 'unknown')}
- Reason: {failure_reason.get('reason', 'unknown')}
- Detail: {failure_reason.get('detail', 'No details')}

위 실패 원인을 반드시 해결하여 재생성하라!
"""

    prompt = f"""
시나리오: {scenario['scenario']}
기술 스택: {track_spec.get('tech_stack', 'PyTorch')}
트랙: {track_spec.get('track_name', '기본 트랙')}
이전 단계 요약:
{prev_context}

{prev_code_section}

{failure_section}

현재 단계 생성 (9단계 리디자인 설계도 준수):
- Step {step_spec['step']}/3
- 버그 타입: {step_spec['bug_type_name']}
- 허용된 버그: {step_spec['allowed_bugs']}
- 수정 라인: 최대 {step_spec.get('fix_lines_max', 3)}줄

요구사항 (절대 엄수):
1. **코드의 분량과 맥락 (Full Context)**: 
   - 절대 코드 한두 줄만 뱉지 말 것. **최소한 해당 버그가 포함된 클래스 전체 또는 핵심 연산 함수 전체**를 제공할 것.
   - 사용자가 전체적인 데이터 흐름(예: 데이터 로딩 -> 전처리 -> 모델 입력)을 이해할 수 있을 만큼 충분한 주석과 주변 코드를 포함할 것.
2. **로그와 코드의 논리적 일치 (Synthesized Alignment)**:
   - `execution_log`에 표시된 에러 위치(파일명, 라인 번호, 함수 이름)가 제공된 `buggy_code`와 완벽히 일치해야 함.
   - 로그를 보고 코드의 특정 지점을 즉시 찾아갈 수 있도록 설계할 것.
3. **증상 기술**: "작동 안 함" 같은 추상적 표현 대신, "데이터 로딩 중 특정 인덱스 참조 오류" 혹은 "레이어 간 차원 불일치(128 vs 256)"와 같이 공학적으로 구체적인 현상을 기술.
4. **검증 스크립트 (Fast Execution)**:
   - 절대 전체 데이터셋을 돌리지 말 것.
   - `torch.randn`이나 `DataLoader`의 첫 번째 배치(`next(iter(loader))`)만 사용하여 **최대 5초 이내**에 실행이 완료되도록 작성할 것.
   - 상태 변화(Loss 감소 등)를 최소한의 연산으로 검증할 것.

5. **패턴 생성 규칙 (CRITICAL - 검증 실패의 주 원인)**:
   ⚠️ 이 규칙을 어기면 검증에서 100% 실패함!

   - **required_patterns**: correct_code에는 있지만 buggy_code에는 없는 패턴만 포함
   - **forbidden_patterns**: buggy_code에는 있지만 correct_code에는 없는 패턴만 포함

   - **검증 로직**:
     * buggy_code가 required_patterns를 포함하면 → 실패 (잘못된 패턴)
     * correct_code가 required_patterns를 포함하지 않으면 → 실패 (패턴 누락)

   📚 **검증 통과한 실제 예시 (반드시 참고)**:

   **예시 1 - 차원 불일치 버그**:
   buggy_code:
   ```
   self.fc1 = nn.Linear(3, 8)  # 잘못된 입력 차원
   ```
   correct_code:
   ```
   self.fc1 = nn.Linear(input_dim, 8)  # 올바른 입력 차원
   ```
   required_patterns: ["nn.Linear(input_dim", "Linear(input_dim"]
   forbidden_patterns: ["nn.Linear(3"]

   → required는 correct에만 있음 ✅
   → forbidden은 buggy에만 있음 ✅

   **예시 2 - 손실 함수 선택 오류**:
   buggy_code:
   ```
   criterion = nn.CrossEntropyLoss()  # 회귀에 분류 손실 함수 사용
   ```
   correct_code:
   ```
   criterion = nn.MSELoss()  # 회귀에 적합한 손실 함수
   ```
   required_patterns: ["MSELoss", "L1Loss"]
   forbidden_patterns: ["CrossEntropyLoss", "NLLLoss"]

   → MSELoss는 correct에만 있음 ✅
   → CrossEntropyLoss는 buggy에만 있음 ✅

   **예시 3 - 평가 모드 누락**:
   buggy_code:
   ```
   # 평가 (Dropout이 계속 적용됨)
   X_val = torch.randn(5, 5)
   val_output = model(X_val)
   ```
   correct_code:
   ```
   # 평가
   model.eval()  # 평가 모드 전환
   X_val = torch.randn(5, 5)
   with torch.no_grad():
       val_output = model(X_val)
   ```
   required_patterns: ["model.eval()", ".eval()"]
   forbidden_patterns: []

   → .eval()은 correct에만 있음 ✅

   위 예시들처럼 패턴을 생성하면 100% 검증 통과함!

출력 형식 (JSON):
{{
  "title": "단계 제목",
  "symptom": "구체적인 관측 증상",
  "execution_log": "buggy_code와 완벽히 동기화된 Traceback 또는 상세 실행 로그",
  "buggy_code": "충분한 맥락을 포함한 Python 코드 (클래스/함수 전체)",
  "correct_code": "수정된 Python 코드 (문법과 구조를 유지하며 버그만 해결)",
  "test_script": "...",
  "required_patterns": ["..."],
  "forbidden_patterns": ["..."],
  "hint": "...",
  "coaching": "..."
}}
"""
    # 1단계: 초안(Draft) 생성
    draft_step_data = call_gpt_json(prompt)

    # 2단계: 자아 비판 및 보정 (Self-Reflection)
    reflection_prompt = f"""
방금 생성된 디버깅 문제의 초안입니다. 다음 기준에 따라 자아 비판을 수행하고, 결함이 있다면 수정된 최종 JSON을 출력하세요.

[초안 데이터]
{json.dumps(draft_step_data, indent=2, ensure_ascii=False)}

[비판 및 보정 기준]
1. **차원 논리(Dimension Logic)**: `execution_log`의 에러 메시지에 적힌 수치(예: 64x128)가 `buggy_code`의 레이어 설정과 수학적으로 일치하는가?
2. **라인 번호(Line Matching)**: 로그의 Traceback 라인 번호가 제공된 코드 안에서 실제로 문제가 있는 줄 번호와 일치하는가?
3. **해결 가능성(Solvability)**: `correct_code`로 수정했을 때 `test_script`가 반드시 PASS 하는가?
4. **실행 효율성(Efficiency)**: `test_script`가 5초 이내에 끝나는 수준인가? (과도한 반복문이나 큰 데이터셋 다운로드 금지)
5. **불필요한 파편 제거**: 코드가 충분한 맥락을 갖추되, 전혀 상관없는 코드가 너무 많지는 않은가?

결함이 발견되면 `buggy_code`, `execution_log`, `test_script` 등을 즉시 수정하여 완벽하게 논리적으로 일치하는 최종 JSON만 반환하라.
"""
    step_data = call_gpt_json(reflection_prompt)

    # ⚠️ 패턴 자동 보정 제거 - LLM이 생성한 패턴을 그대로 사용
    # 검증에서 실패하면 failure_reason과 함께 재생성 요청됨

    # bug_type 기본값 (A, B, C, D)
    bug_type_map = {1: "A", 2: "C", 3: "D"}
    bug_type = step_spec.get("bug_type", bug_type_map.get(step_spec["step"], "A"))

    return {
        "step": step_spec["step"],
        "title": step_data["title"],
        "bug_type": bug_type,
        "bug_type_name": step_spec["bug_type_name"],
        "symptom": step_data.get("symptom", ""),
        "execution_log": step_data.get("execution_log", ""),
        "buggy_code": step_data["buggy_code"],
        "correct_code": step_data["correct_code"],
        "test_script": step_data.get("test_script", ""),
        "hint": step_data["hint"],
        "solution_check": {
            "type": "multi_condition",
            "required_any": step_data.get("required_patterns", []),
            "forbidden": step_data.get("forbidden_patterns", [])
        },
        "coaching": generate_coaching(step_spec, step_data)
    }


def generate_coaching(step_spec: dict, step_data: dict) -> str:
    """
    코칭 메시지 생성

    Args:
        step_spec: 단계별 스펙
        step_data: 생성된 단계 데이터

    Returns:
        str: 코칭 메시지
    """
    prompt = f"""
다음 버그 수정에 대한 현업 조언을 1-2문장으로 작성하라:

버그 타입: {step_spec['bug_type_name']}
제목: {step_data['title']}

형식: "🎯 현업: [1-2문장 조언]"
"""
    return call_gpt(prompt).strip()
