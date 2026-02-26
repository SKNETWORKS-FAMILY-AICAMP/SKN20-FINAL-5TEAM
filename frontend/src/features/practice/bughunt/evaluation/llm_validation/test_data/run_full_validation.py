"""
BugHunt 면접 평가자 신뢰성 검증 - 전체 파이프라인

실행 순서:
  Step 1: LLM 평가 실행   (run_evaluation.py)
  Step 2: 4가지 통계 분석 (analyze_results.py)

사용법:
  python run_full_validation.py           # 60샘플 × 5회 = 300회
  python run_full_validation.py --quick   # 5샘플 × 3회 = 15회 (빠른 테스트)
"""
import subprocess
import sys
from pathlib import Path


def run_step(name, script, args=None):
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    cmd = [sys.executable, str(script)] + (args or [])
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    if result.returncode != 0:
        print(f"  실패: {name}")
        return False
    print(f"  완료: {name}")
    return True


def main(quick=False):
    here = Path(__file__).parent

    print("=" * 60)
    print("  BugHunt 면접 평가자 신뢰성 검증 시작")
    if quick:
        print("  (Quick 모드: 5샘플 × 3회)")
    print("=" * 60)

    eval_args = ['--quick', '--trials', '3'] if quick else []
    if not run_step("Step 1: LLM 평가 실행 (가장 오래 걸림)", here / "run_evaluation.py", eval_args):
        return False

    analyze_args = ['--quick'] if quick else []
    if not run_step("Step 2: 4가지 통계 분석", here / "analyze_results.py", analyze_args):
        return False

    print("\n" + "=" * 60)
    print("  검증 파이프라인 완료")
    print("=" * 60)
    print(f"\n결과 파일 위치: {here / 'data'}/")
    print("  - evaluation_results.json  (LLM 평가 결과)")
    print("  - analysis_results.json    (4가지 검증 통계)")
    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true', help='빠른 테스트 (5샘플)')
    args = parser.parse_args()
    sys.exit(0 if main(quick=args.quick) else 1)
