"""
Progressive 3단계 문제 생성
GPT-4.0 mini를 사용하여 연결된 3단계 버그 수정 문제 생성
"""

from agent.spec import PYTORCH_TRACK
from agent.llm import call_gpt_json, call_gpt


def generate_progressive() -> dict:
    """
    P1 Progressive 문제 전체 생성 (3단계)

    Returns:
        dict: P1 문제 JSON 객체
    """

    # 1. 전체 시나리오 생성
    scenario = generate_scenario(PYTORCH_TRACK)

    # 2. 각 단계별 생성 (Step 1 → Step 2 → Step 3)
    steps = []
    for step_spec in PYTORCH_TRACK["steps"]:
        step = generate_step(
            step_spec,
            scenario,
            prev_steps=steps  # 🔑 이전 단계 참조
        )
        steps.append(step)

    # 3. Progressive 포맷 조합
    return {
        "id": "P1",
        "project_title": scenario["project_title"],
        "scenario": scenario["scenario"],
        "difficulty": PYTORCH_TRACK["difficulty"],
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

트랙: {track_spec.get('track_name', track_spec.get('track', 'PyTorch'))}
컨텍스트: {track_spec.get('context', track_spec.get('scenario_template', {}).get('context', 'MNIST 분류'))}
총 3단계의 연결된 버그 수정 미션

요구사항:
1. 실무 상황을 반영한 자연스러운 스토리
2. 3단계가 논리적으로 연결되는 흐름
3. MNIST 손글씨 분류 프로젝트 배경

출력 형식 (JSON):
{{
  "project_title": "간결한 제목 (20자 이내)",
  "scenario": "전체 스토리 (3단계 흐름 암시, 100자 이내)"
}}
"""
    return call_gpt_json(prompt)


def generate_step(step_spec: dict, scenario: dict, prev_steps: list) -> dict:
    """
    단일 단계 생성 (이전 단계 기반)

    Args:
        step_spec: 단계별 스펙 (PYTORCH_TRACK["steps"][i])
        scenario: 전체 시나리오 정보
        prev_steps: 이전 단계 리스트 (연결성 유지용)

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

    prompt = f"""
시나리오: {scenario['scenario']}
이전 단계:
{prev_context}

현재 단계 생성:
- Step {step_spec['step']}/3
- 버그 타입: {step_spec['bug_type_name']}
- 허용된 버그: {step_spec['allowed_bugs']}
- 수정 라인: 최대 {step_spec.get('fix_lines_max', 3)}줄

요구사항:
1. PyTorch 기반 코드 (MNIST 분류)
2. buggy_code는 단 하나의 명확한 버그만 포함
3. correct_code는 해당 버그만 수정 (다른 부분은 동일)
4. 이전 단계의 correct_code를 기반으로 작성 (연결성)
5. **중요: 정답 판별 패턴 (Differentiators) 생성 규칙**:
   - `required_patterns`는 **오직 `correct_code`를 `buggy_code`와 구별 짓는 핵심 수정 내용**이어야 함.
   - **절대 규칙**: `buggy_code`에 이미 들어있는 구문을 `required_patterns`에 넣지 말 것. (예: 버그가 `zero_grad()` 누락이라면, `zero_grad()`는 오직 `correct_code`에만 있어야 함)
   - 만약 오답 코드와 정답 코드에서 해당 단어가 공통으로 발견되면, 검증 시스템이 즉시 실패(FAIL) 처리함.
   - `forbidden_patterns`는 `buggy_code`에만 있는 잘못된 패턴을 명시할 것.
6. test_script 작성 요령:
   - **반드시** 독립적으로 실행 가능해야 함. 필요한 변수(images, labels, dataloader 등)는 테스트 코드 내에서 직접 생성(torch.randn 등)하거나 Mocking 할 것.
7. 코드는 실행 가능하고 현실적이어야 함
9. **예시 (이 포맷을 따를 것)**:
   {{
     "title": "데이터 차원 불일치",
     "buggy_code": "x = self.fc(x)  # 입력 차원이 맞지 않음",
     "correct_code": "x = x.view(x.size(0), -1)\\nx = self.fc(x)",
     "required_patterns": ["x.view("],
     "forbidden_patterns": ["self.fc(x) # 바로 호출"],
     "test_script": "model = SimpleNet(); x = torch.randn(1, 1, 28, 28); out = model(x); assert out.shape == (1, 10)"
   }}

{prev_code_section}

출력 형식 (JSON):
{{
  "title": "버그 제목 (30자 이내)",
  "buggy_code": "버그가 있는 Python 코드 (전체 함수 또는 클래스)",
  "correct_code": "수정된 Python 코드 (전체 함수 또는 클래스, buggy_code와 거의 동일하되 버그만 수정)",
  "hint": "학생 힌트 (50자 이내)",
  "required_patterns": ["패턴1", "패턴2"],
  "forbidden_patterns": ["금지패턴"],
  "test_script": "correct_code의 성공을 보장하는 테스트 코드 (예: model = SimpleNet(); loss = ...; assert loss < 100)"
}}
"""
    step_data = call_gpt_json(prompt)

    # 🔑 [강력한 보정 로직]
    correct_code = step_data.get("correct_code", "")
    buggy_code = step_data.get("buggy_code", "")
    final_required = []
    final_forbidden = []
    
    # 1. Required 패턴 보정: Correct에는 있고 Buggy에는 없는 것만 남김 (가장 중요)
    for r in step_data.get("required_patterns", []):
        if r in correct_code and r not in buggy_code:
            final_required.append(r)
            
    # 2. Forbidden 패턴 보정: Buggy에는 있고 Correct에는 없는 것만 남김
    for f in step_data.get("forbidden_patterns", []):
        if f in buggy_code and f not in correct_code:
            # required와 겹치지 않게 한 번 더 체크
            if f not in final_required:
                final_forbidden.append(f)

    # bug_type 기본값 (A, B, C, D)
    bug_type_map = {1: "A", 2: "C", 3: "D"}
    bug_type = step_spec.get("bug_type", bug_type_map.get(step_spec["step"], "A"))

    return {
        "step": step_spec["step"],
        "title": step_data["title"],
        "bug_type": bug_type,
        "bug_type_name": step_spec["bug_type_name"],
        "buggy_code": step_data["buggy_code"],
        "correct_code": step_data["correct_code"],
        "test_script": step_data.get("test_script", ""),
        "hint": step_data["hint"],
        "solution_check": {
            "type": "multi_condition",
            "required_any": final_required,
            "forbidden": final_forbidden
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
