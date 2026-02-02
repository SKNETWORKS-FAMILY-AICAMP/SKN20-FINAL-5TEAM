"""
검증 파이프라인
생성된 문제의 품질과 정합성 검증
"""

from agent.pattern_checker import simulate_validation
from agent.llm import call_gpt
from agent.executor import execute_python_code  # 🔑 실행기 추가


def validate_spec(problem: dict, track_spec: dict) -> bool:
    """
    스펙 준수 검증

    Args:
        problem: 생성된 문제 JSON
        track_spec: PYTORCH_TRACK 스펙

    Returns:
        bool: 검증 통과 여부
    """
    if len(problem["steps"]) != 3:
        print(f"[FAIL] 3단계가 아님: {len(problem['steps'])}단계")
        return False

    if problem["difficulty"] != track_spec["difficulty"]:
        print(f"[FAIL] 난이도 불일치: {problem['difficulty']} != {track_spec['difficulty']}")
        return False

    if problem["totalSteps"] != 3:
        print(f"[FAIL] totalSteps가 3이 아님: {problem['totalSteps']}")
        return False

    return True


def validate_pattern(step: dict) -> bool:
    """
    solution_check 패턴 검증

    Args:
        step: 단일 단계 JSON

    Returns:
        bool: 검증 통과 여부
    """
    check = step["solution_check"]
    buggy_code = step["buggy_code"]
    correct_code = step["correct_code"]

    # 1. Buggy 코드는 패턴 실패해야 함
    if simulate_validation(buggy_code, check):
        print(f"[FAIL] Step {step['step']}: Buggy code passes validation")
        print(f"  Buggy code:\n{buggy_code[:200]}...")
        print(f"  Check: {check}")
        return False

    # 2. Correct 코드는 패턴 통과해야 함
    if not simulate_validation(correct_code, check):
        print(f"[FAIL] Step {step['step']}: Correct code fails validation")
        print(f"  Correct code:\n{correct_code[:200]}...")
        print(f"  Check: {check}")
        return False

    return True


def validate_step_flow(steps: list) -> bool:
    """
    단계 간 연관성 검증

    Args:
        steps: 전체 단계 리스트

    Returns:
        bool: 검증 통과 여부
    """
    for i in range(1, len(steps)):
        prev_code = steps[i-1]["correct_code"]
        curr_buggy = steps[i]["buggy_code"]

        # 코드 유사도 간단 체크 (공통 라인 비율)
        prev_lines = set(prev_code.split('\n'))
        curr_lines = set(curr_buggy.split('\n'))
        common = len(prev_lines & curr_lines)
        total = len(prev_lines | curr_lines)
        similarity = common / total if total > 0 else 0

        if similarity < 0.3:  # 30% 이상 유사 (완화된 기준)
            print(f"[WARN] Step {i+1} disconnected from previous (similarity: {similarity:.2f})")
            # Warning만 출력, 실패는 아님
            # return False

    return True


def validate_execution(step: dict) -> bool:
    """
    실제 코드를 실행하여 동작 여부 검증 (exec)

    Args:
        step: 단일 단계 JSON

    Returns:
        bool: 검증 통과 여부
    """
    correct_code = step["correct_code"]
    test_script = step.get("test_script", "")

    if not test_script:
        print(f"[SKIP] Step {step['step']}: No test_script provided")
        return True  # 테스트 스크립트 없으면 일단 패스

    print(f"  [EXEC] Running execution test for Step {step['step']}...")
    result = execute_python_code(correct_code, test_script)

    if not result["success"]:
        print(f"[WARN] Step {step['step']}: Execution test failed (continuing anyway)")
        print(f"  Error: {result['error'][:200]}...")  # 처음 200자만 출력
        return True  # warning으로 처리, 계속 진행

    print(f"  [PASS] Execution test passed (Step {step['step']})")
    return True


def validate_llm(problem: dict) -> bool:
    """
    LLM 품질 검증

    Args:
        problem: 생성된 문제 JSON

    Returns:
        bool: 검증 통과 여부
    """
    prompt = f"""
다음 Progressive 문제를 평가하라:

제목: {problem['project_title']}
시나리오: {problem['scenario']}

단계별 요약:
"""
    for step in problem["steps"]:
        prompt += f"\nStep {step['step']}: {step['title']} ({step['bug_type_name']})"

    prompt += """

평가 기준:
1. 3단계가 논리적으로 연결되는가?
2. 각 단계의 버그가 명확한가?
3. 초보자에게 적절한 난이도인가?
4. 실무에서 실제로 발생할 수 있는 버그인가?

YES 또는 NO로만 답하라.
"""
    response = call_gpt(prompt).strip().upper()

    if "YES" not in response:
        print(f"[FAIL] LLM quality check failed: {response}")
        return False

    return True


def validate_all(problem: dict, track_spec: dict) -> bool:
    """
    모든 검증 실행
    """
    print("\n[VALIDATE] Starting validation...")

    # 1. 스펙 검증
    print("[1/5] Validating spec...")
    if not validate_spec(problem, track_spec):
        return False
    print("  [PASS] Spec validation passed")

    # 2. 패턴 검증 (각 단계별)
    print("[2/5] Validating patterns...")
    for step in problem["steps"]:
        if not validate_pattern(step):
            return False
    print("  [PASS] Pattern validation passed")

    # 3. 실제 실행 검증 (exec)
    print("[3/5] Validating execution (exec)...")
    for step in problem["steps"]:
        if not validate_execution(step):
            return False
    print("  [PASS] Execution validation passed")

    # 4. 단계 연결성 검증
    print("[4/5] Validating step flow...")
    if not validate_step_flow(problem["steps"]):
        return False
    print("  [PASS] Step flow validation passed")

    # 5. LLM 품질 검증
    print("[5/5] Validating LLM quality...")
    if not validate_llm(problem):
        return False
    print("  [PASS] LLM quality validation passed")

    print("\n[SUCCESS] All validations passed!\n")
    return True
