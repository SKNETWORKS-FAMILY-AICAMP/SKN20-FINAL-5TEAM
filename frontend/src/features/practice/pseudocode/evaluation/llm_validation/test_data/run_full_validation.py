"""
의사코드 트랙 LLM 신뢰성 검증 - 전체 파이프라인

실행 순서:
  Step 1: 샘플 생성        (generate_validation_samples.py)
  Step 2: LLM 평가 실행   (run_evaluation.py)
  Step 3: 4가지 통계 분석 (analyze_results.py)

사용법:
  python run_full_validation.py           # 30샘플 × 5회 = 150회
  python run_full_validation.py --quick   # 5샘플 × 3회 = 15회 (빠른 테스트)
  python run_full_validation.py --skip-generate  # 기존 샘플 재사용
"""
import subprocess
import sys
from pathlib import Path


def run_step(name: str, script: Path, args: list = None) -> bool:
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    cmd = [sys.executable, str(script)] + (args or [])
    result = subprocess.run(cmd, cwd=script.parent)
    if result.returncode != 0:
        print(f"  실패: {name}")
        return False
    print(f"  완료: {name}")
    return True


def main(quick: bool = False, skip_generate: bool = False) -> bool:
    here = Path(__file__).parent

    print("=" * 60)
    print("  의사코드 트랙 LLM 신뢰성 검증 시작")
    if quick:
        print("  (Quick 모드: 5샘플 × 3회)")
    print("=" * 60)

    # Step 1: 샘플 생성
    if not skip_generate:
        gen_args = ['--quick'] if quick else []
        if not run_step("Step 1: 테스트 샘플 생성", here / "generate_validation_samples.py", gen_args):
            return False
    else:
        print("\n샘플 생성 건너뜀 (기존 파일 재사용)")

    # Step 2: LLM 평가
    eval_args = ['--quick', '--trials', '3'] if quick else []
    if not run_step("Step 2: LLM 평가 실행 (가장 오래 걸림)", here / "run_evaluation.py", eval_args):
        return False

    # Step 3: 분석
    analyze_args = ['--quick'] if quick else []
    if not run_step("Step 3: 4가지 통계 분석", here / "analyze_results.py", analyze_args):
        return False

    print("\n" + "=" * 60)
    print("  검증 파이프라인 완료")
    print("=" * 60)
    result_file = 'quick_evaluation_results.json' if quick else 'evaluation_results.json'
    print(f"\n결과 파일 위치: {here / 'data'}/")
    print(f"  - validation_samples.json    (테스트 샘플)")
    print(f"  - {result_file}  (LLM 평가 결과)")
    print(f"  - analysis_results.json      (4가지 검증 통계)")
    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true', help='빠른 테스트 (5샘플)')
    parser.add_argument('--skip-generate', action='store_true', help='샘플 생성 건너뜀')
    args = parser.parse_args()

    success = main(quick=args.quick, skip_generate=args.skip_generate)
    sys.exit(0 if success else 1)
