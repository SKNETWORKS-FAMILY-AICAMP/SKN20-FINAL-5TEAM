"""
에이전트 오케스트레이션
P1 Progressive 문제 생성 및 검증 재시도 로직
"""

from agent.spec import TRACK_SPECS, PYTORCH_TRACK
from agent.generator import generate_progressive
from agent.validator import validate_all


def run_problem_agent(track_id: str = "pytorch_mnist", max_retry: int = 5) -> dict:
    """
    P1 Progressive 문제 생성 에이전트
    재시도 로직 포함 (개선 버전: 실패 이유 전파)

    Args:
        track_id: 생성할 트랙 ID (from TRACK_SPECS)
        max_retry: 최대 재시도 횟수

    Returns:
        dict: 검증 통과된 P1 문제 JSON

    Raises:
        RuntimeError: max_retry 횟수만큼 재시도 후에도 실패 시
    """

    last_failure_reason = None

    for attempt in range(1, max_retry + 1):
        print(f"\n{'='*60}")
        print(f"  ATTEMPT {attempt}/{max_retry}")
        if last_failure_reason:
            print(f"  Previous failure: {last_failure_reason.get('stage', 'unknown')}")
        print(f"{'='*60}\n")

        try:
            # 0. 트랙 설정 가져오기
            track_spec = TRACK_SPECS.get(track_id, PYTORCH_TRACK)

            # 1. 문제 생성 (실패 이유 정보 포함)
            if last_failure_reason:
                print(f"[GENERATE] Regenerating with failure reason: {last_failure_reason.get('reason', 'unknown')}")
            else:
                print(f"[GENERATE] Generating P1 Progressive problem for track: {track_id}...")

            problem = generate_progressive(track_id=track_id)
            print(f"[GENERATE] Step 1/2/3 generation complete.")

            # 2. 검증 실행
            print(f"[VALIDATE] Starting validation for: {problem['project_title']}")
            passed, failure_reason = validate_all(problem, track_spec)
            if passed:
                print(f"\n{'='*60}")
                print(f"  SUCCESS! (Attempt {attempt}/{max_retry})")
                print(f"{'='*60}\n")
                return problem
            else:
                last_failure_reason = failure_reason
                print(f"\n[RETRY] Validation failed: {failure_reason.get('detail', 'Unknown reason')}")
                print(f"[RETRY] Stage: {failure_reason.get('stage', 'unknown')}, Reason: {failure_reason.get('reason', 'unknown')}")
                print(f"[RETRY] Retrying... ({attempt}/{max_retry})")

        except Exception as e:
            print(f"\n[ERROR] Generation/validation error: {e}")
            print(f"[RETRY] Retrying... ({attempt}/{max_retry})")
            continue

    # 최종 실패 시 상세 정보 포함
    if last_failure_reason:
        raise RuntimeError(
            f"문제 생성 실패: {max_retry}번 재시도 후 실패\n"
            f"최종 실패 단계: {last_failure_reason.get('stage', 'unknown')}\n"
            f"실패 이유: {last_failure_reason.get('detail', 'Unknown')}"
        )
    else:
        raise RuntimeError(f"문제 생성 실패: {max_retry}번 재시도 후 실패")
