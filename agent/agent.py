"""
에이전트 오케스트레이션
P1 Progressive 문제 생성 및 검증 재시도 로직
"""

from agent.spec import PYTORCH_TRACK
from agent.generator import generate_progressive
from agent.validator import validate_all


def run_problem_agent(max_retry: int = 5) -> dict:
    """
    P1 Progressive 문제 생성 에이전트
    재시도 로직 포함

    Args:
        max_retry: 최대 재시도 횟수

    Returns:
        dict: 검증 통과된 P1 문제 JSON

    Raises:
        RuntimeError: max_retry 횟수만큼 재시도 후에도 실패 시
    """

    for attempt in range(1, max_retry + 1):
        print(f"\n{'='*60}")
        print(f"  ATTEMPT {attempt}/{max_retry}")
        print(f"{'='*60}\n")

        try:
            # 1. 문제 생성
            print("[GENERATE] Generating P1 Progressive problem...")
            problem = generate_progressive()
            print(f"[GENERATE] Generated problem: {problem['project_title']}")

            # 2. 검증 실행
            if validate_all(problem, PYTORCH_TRACK):
                print(f"\n{'='*60}")
                print(f"  SUCCESS! (Attempt {attempt}/{max_retry})")
                print(f"{'='*60}\n")
                return problem
            else:
                print(f"\n[RETRY] Validation failed, retrying... ({attempt}/{max_retry})")

        except Exception as e:
            print(f"\n[ERROR] Generation/validation error: {e}")
            print(f"[RETRY] Retrying... ({attempt}/{max_retry})")
            continue

    raise RuntimeError(f"문제 생성 실패: {max_retry}번 재시도 후 실패")
