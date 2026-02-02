"""
Vue BugHunt.vue의 checkProgressiveSolution() 로직 재현
패턴 매칭으로 정답 여부 검증
"""

import re


def simulate_validation(code: str, check: dict) -> bool:
    """
    BugHunt.vue의 checkProgressiveSolution() 로직 재현
    패턴 매칭으로 정답 여부 검증

    Args:
        code: 검증할 코드 문자열
        check: solution_check 객체
            - type: 'multi_condition', 'regex', 'contains', 'notContains'
            - required_all: 모두 포함되어야 하는 패턴 리스트
            - required_any: 하나라도 포함되어야 하는 패턴 리스트
            - forbidden: 포함되면 안 되는 패턴 리스트
            - value: regex, contains, notContains용 값

    Returns:
        bool: 검증 통과 여부
    """

    if check["type"] == "multi_condition":
        # required_all: 모두 포함되어야 함
        has_all_required = all(
            req in code
            for req in check.get("required_all", [])
        )

        # required_any: 하나라도 포함되어야 함
        has_any_required = (
            any(req in code for req in check.get("required_any", []))
            if check.get("required_any")
            else True
        )

        # forbidden: 포함되면 안 됨
        has_no_forbidden = all(
            f not in code
            for f in check.get("forbidden", [])
        )

        return has_all_required and has_any_required and has_no_forbidden

    elif check["type"] == "regex":
        try:
            pattern = re.compile(check["value"], flags=0)
            return bool(pattern.search(code))
        except:
            return False

    elif check["type"] == "contains":
        return check["value"] in code

    elif check["type"] == "notContains":
        return check["value"] not in code

    return False


def test_pattern_checker():
    """패턴 체커 유닛 테스트"""

    # Test 1: multi_condition with required_any
    check1 = {
        "type": "multi_condition",
        "required_any": ["x.view(", "x.flatten("],
        "forbidden": []
    }

    assert simulate_validation("x = x.view(-1, 784)", check1) == True
    assert simulate_validation("x = x.flatten(1)", check1) == True
    assert simulate_validation("x = x.reshape(-1, 784)", check1) == False

    # Test 2: multi_condition with forbidden
    check2 = {
        "type": "multi_condition",
        "required_any": ["optimizer.zero_grad()"],
        "forbidden": ["# optimizer.zero_grad()"]
    }

    assert simulate_validation("optimizer.zero_grad()", check2) == True
    assert simulate_validation("# optimizer.zero_grad()", check2) == False

    # Test 3: regex
    check3 = {
        "type": "regex",
        "value": r"model\.eval\(\)"
    }

    assert simulate_validation("model.eval()", check3) == True
    assert simulate_validation("model.train()", check3) == False

    print("[TEST] All pattern_checker tests passed!")


if __name__ == "__main__":
    test_pattern_checker()
