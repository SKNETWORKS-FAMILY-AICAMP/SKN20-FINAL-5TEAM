"""
검증 파이프라인
생성된 문제의 품질과 정합성 검증 (개선 버전)
"""

from agent.pattern_checker import simulate_validation
from agent.executor import execute_python_code


def validate_spec(problem: dict, track_spec: dict) -> tuple[bool, dict]:
    """
    스펙 준수 검증

    Args:
        problem: 생성된 문제 JSON
        track_spec: TRACK_SPECS 스펙

    Returns:
        (bool, dict): (검증 통과 여부, 실패 이유)
    """
    if len(problem["steps"]) != 3:
        return False, {
            "stage": "spec",
            "reason": "step_count_mismatch",
            "detail": f"3단계가 아님: {len(problem['steps'])}단계"
        }

    if problem["difficulty"] != track_spec["difficulty"]:
        return False, {
            "stage": "spec",
            "reason": "difficulty_mismatch",
            "detail": f"난이도 불일치: {problem['difficulty']} != {track_spec['difficulty']}"
        }

    if problem["totalSteps"] != 3:
        return False, {
            "stage": "spec",
            "reason": "total_steps_mismatch",
            "detail": f"totalSteps가 3이 아님: {problem['totalSteps']}"
        }

    return True, {}


def validate_pattern(step: dict) -> tuple[bool, dict]:
    """
    solution_check 패턴 검증

    Args:
        step: 단일 단계 JSON

    Returns:
        (bool, dict): (검증 통과 여부, 실패 이유)
    """
    check = step["solution_check"]
    buggy_code = step["buggy_code"]
    correct_code = step["correct_code"]

    # 1. Buggy 코드는 패턴 실패해야 함
    if simulate_validation(buggy_code, check):
        return False, {
            "stage": "pattern",
            "step": step["step"],
            "reason": "buggy_passes_validation",
            "detail": f"Buggy code가 패턴을 통과함 (잘못된 패턴 설계)",
            "check": check,
            "buggy_code_preview": buggy_code[:150]
        }

    # 2. Correct 코드는 패턴 통과해야 함
    if not simulate_validation(correct_code, check):
        return False, {
            "stage": "pattern",
            "step": step["step"],
            "reason": "correct_fails_validation",
            "detail": f"Correct code가 패턴을 통과하지 못함 (패턴이 너무 엄격하거나 잘못됨)",
            "check": check,
            "correct_code_preview": correct_code[:150]
        }

    return True, {}


def validate_execution(step: dict) -> tuple[bool, dict]:
    """
    실제 코드를 실행하여 동작 여부 검증 (exec)
    ⚠️ Step 1은 Hard Fail, Step 2-3은 Soft Fail

    Args:
        step: 단일 단계 JSON

    Returns:
        (bool, dict): (검증 통과 여부, 실패 이유)
    """
    correct_code = step["correct_code"]
    test_script = step.get("test_script", "")

    if not test_script:
        print(f"[SKIP] Step {step['step']}: No test_script provided")
        return True, {}  # 테스트 스크립트 없으면 패스

    print(f"  [EXEC] Running execution test for Step {step['step']}...")
    result = execute_python_code(correct_code, test_script)

    if not result["success"]:
        is_step_1 = (step["step"] == 1)
        severity = "FAIL" if is_step_1 else "WARN"

        print(f"[{severity}] Step {step['step']}: Execution test failed")
        print(f"  Error: {result['error'][:200]}...")

        if is_step_1:
            # Step 1은 Hard Fail
            return False, {
                "stage": "execution",
                "step": step["step"],
                "reason": "step1_not_executable",
                "detail": f"Step 1 코드가 실행되지 않음 (Hard Fail)",
                "error": result["error"][:300]
            }
        else:
            # Step 2-3은 Warning만
            print(f"  [WARN] Continuing anyway (Step {step['step']} is soft fail)")
            return True, {}

    print(f"  [PASS] Execution test passed (Step {step['step']})")
    return True, {}


def validate_thinking_connectivity(steps: list, track_spec: dict) -> tuple[bool, dict]:
    """
    사고 연결성 검증
    각 단계가 이전 단계의 thinking_objective를 기반으로 하는지 확인

    Args:
        steps: 전체 단계 리스트
        track_spec: TRACK_SPECS 스펙

    Returns:
        (bool, dict): (검증 통과 여부, 실패 이유)
    """
    thinking_objectives = track_spec.get("thinking_objectives", [])

    if not thinking_objectives:
        print("[WARN] No thinking_objectives in spec, skipping connectivity check")
        return True, {}

    for i in range(1, len(steps)):
        prev_step = steps[i-1]
        curr_step = steps[i]

        # 이전 단계의 thinking objective
        prev_objective = next(
            (obj for obj in thinking_objectives if obj["step"] == i),
            None
        )
        curr_objective = next(
            (obj for obj in thinking_objectives if obj["step"] == i+1),
            None
        )

        if not prev_objective or not curr_objective:
            continue

        # 현재 단계의 buggy_code가 이전 단계의 correct_code를 기반으로 하는지
        prev_code = prev_step["correct_code"]
        curr_buggy = curr_step["buggy_code"]

        # 핵심 로직 라인 추출 (공백/주석 제외)
        def extract_logic_lines(code):
            lines = [
                line.strip()
                for line in code.split('\n')
                if line.strip() and not line.strip().startswith('#')
            ]
            return set(lines)

        prev_logic = extract_logic_lines(prev_code)
        curr_logic = extract_logic_lines(curr_buggy)

        common = len(prev_logic & curr_logic)
        prev_total = len(prev_logic)

        # 이전 코드의 50% 이상이 현재 코드에 포함되어야 함
        if prev_total > 0:
            inheritance_rate = common / prev_total
            if inheritance_rate < 0.5:
                return False, {
                    "stage": "thinking_connectivity",
                    "step": curr_step["step"],
                    "reason": "disconnected_thinking",
                    "detail": f"Step {curr_step['step']}가 Step {prev_step['step']}의 사고를 이어받지 않음 (상속률: {inheritance_rate:.2%})",
                    "prev_objective": prev_objective["objective"],
                    "curr_objective": curr_objective["objective"]
                }

    return True, {}


def validate_thinking_necessity(step: dict, track_spec: dict) -> tuple[bool, dict]:
    """
    사고 필수성 검증
    "이 Step은 이 사고 없이는 풀 수 없는가?"를 검증

    Args:
        step: 단일 단계 JSON
        track_spec: TRACK_SPECS 스펙

    Returns:
        (bool, dict): (검증 통과 여부, 실패 이유)
    """
    thinking_objectives = track_spec.get("thinking_objectives", [])
    objective = next(
        (obj for obj in thinking_objectives if obj["step"] == step["step"]),
        None
    )

    if not objective:
        print(f"[WARN] No thinking_objective for Step {step['step']}, skipping necessity check")
        return True, {}

    hint = step.get("hint", "")
    required_keywords = objective.get("required_in_hint", [])

    # 1. 힌트에 사고 관련 키워드가 포함되어 있는가?
    hint_lower = hint.lower()
    missing_keywords = [kw for kw in required_keywords if kw.lower() not in hint_lower]

    if missing_keywords:
        return False, {
            "stage": "thinking_necessity",
            "step": step["step"],
            "reason": "hint_missing_thinking_keywords",
            "detail": f"힌트에 사고 관련 키워드 누락: {missing_keywords}",
            "objective": objective["objective"],
            "hint": hint
        }

    # 2. solution_check가 단순 패턴 암기가 아닌 사고를 요구하는가?
    check = step.get("solution_check", {})

    # 패턴이 너무 단순하면 (1개 이하) 암기로 풀 수 있음
    required_all = check.get("required_all", [])
    required_any = check.get("required_any", [])
    total_patterns = len(required_all) + len(required_any)

    if total_patterns <= 1:
        return False, {
            "stage": "thinking_necessity",
            "step": step["step"],
            "reason": "pattern_too_simple",
            "detail": f"패턴이 너무 단순함 (총 {total_patterns}개) - 암기로 풀 수 있음",
            "objective": objective["objective"],
            "check": check
        }

    # 3. buggy_code와 correct_code의 차이가 명확한가?
    buggy_lines = set(step["buggy_code"].split('\n'))
    correct_lines = set(step["correct_code"].split('\n'))
    diff_lines = buggy_lines.symmetric_difference(correct_lines)

    if len(diff_lines) == 0:
        return False, {
            "stage": "thinking_necessity",
            "step": step["step"],
            "reason": "no_code_difference",
            "detail": "buggy_code와 correct_code가 동일함",
            "objective": objective["objective"]
        }

    return True, {}


def validate_all(problem: dict, track_spec: dict) -> tuple[bool, dict]:
    """
    모든 검증 실행 (개선 버전)

    Returns:
        (bool, dict): (검증 통과 여부, 실패 이유)
    """
    print("\n[VALIDATE] Starting validation...")

    # 1. 스펙 검증
    print("[1/5] Validating spec...")
    passed, failure_reason = validate_spec(problem, track_spec)
    if not passed:
        print(f"  [FAIL] {failure_reason['detail']}")
        return False, failure_reason
    print("  [PASS] Spec validation passed")

    # 2. 패턴 검증 (각 단계별)
    print("[2/5] Validating patterns...")
    for step in problem["steps"]:
        passed, failure_reason = validate_pattern(step)
        if not passed:
            print(f"  [FAIL] {failure_reason['detail']}")
            return False, failure_reason
    print("  [PASS] Pattern validation passed")

    # 3. 실제 실행 검증 (Step 1 Hard Fail)
    print("[3/5] Validating execution (Step 1 = Hard Fail)...")
    for step in problem["steps"]:
        passed, failure_reason = validate_execution(step)
        if not passed:
            print(f"  [FAIL] {failure_reason['detail']}")
            return False, failure_reason
    print("  [PASS] Execution validation passed")

    # 4. 사고 연결성 검증
    print("[4/5] Validating thinking connectivity...")
    passed, failure_reason = validate_thinking_connectivity(problem["steps"], track_spec)
    if not passed:
        print(f"  [FAIL] {failure_reason['detail']}")
        return False, failure_reason
    print("  [PASS] Thinking connectivity passed")

    # 5. 사고 필수성 검증
    print("[5/5] Validating thinking necessity...")
    for step in problem["steps"]:
        passed, failure_reason = validate_thinking_necessity(step, track_spec)
        if not passed:
            print(f"  [FAIL] {failure_reason['detail']}")
            return False, failure_reason
    print("  [PASS] Thinking necessity passed")

    print("\n[SUCCESS] All validations passed!\n")
    return True, {}
