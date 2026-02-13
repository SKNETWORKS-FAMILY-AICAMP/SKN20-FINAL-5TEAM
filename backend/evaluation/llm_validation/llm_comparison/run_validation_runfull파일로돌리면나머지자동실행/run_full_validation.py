"""
Bug Hunt 평가 검증 전체 파이프라인 실행

1. 샘플 생성
2. 규칙 기반 점수 계산
3. 평가 실행 (300회)
4. 통계 분석
5. 시각화
"""
import subprocess
import sys
from pathlib import Path


def run_step(step_name, script_name, args=None):
    """단계별 스크립트 실행"""
    print(f"\n{'='*60}")
    print(f"🚀 {step_name}")
    print(f"{'='*60}\n")

    cmd = [sys.executable, script_name]
    if args:
        cmd.extend(args)

    result = subprocess.run(cmd, cwd=Path(__file__).parent)

    if result.returncode != 0:
        print(f"\n❌ {step_name} 실패!")
        return False

    print(f"\n✅ {step_name} 완료!")
    return True


def main(quick_mode=False):
    """전체 검증 파이프라인 실행"""
    scripts_dir = Path(__file__).parent

    print("="*60)
    print("🎯 Bug Hunt 평가 검증 파이프라인 시작")
    print("="*60)

    if quick_mode:
        print("⚡ Quick 모드: 품질별 1개 샘플만 테스트")

    # Step 1: 샘플 생성
    if not run_step("Step 1: 샘플 데이터 생성",
                   scripts_dir / "generate_validation_samples.py"):
        return False

    # Step 2: 규칙 기반 점수 계산
    if not run_step("Step 2: 규칙 기반 점수 계산",
                   scripts_dir / "rule_based_scorer.py"):
        return False

    # Step 3: 평가 실행
    eval_args = ['--quick'] if quick_mode else []
    if not run_step("Step 3: LLM 평가 실행 (이 단계가 가장 오래 걸립니다)",
                   scripts_dir / "run_evaluation.py", eval_args):
        return False

    # Step 4: 통계 분석
    if not run_step("Step 4: 4가지 검증 통계 분석",
                   scripts_dir / "analyze_results.py"):
        return False

    # Step 5: 시각화
    if not run_step("Step 5: 결과 시각화",
                   scripts_dir / "visualize_results.py"):
        return False

    print("\n" + "="*60)
    print("🎉 전체 검증 파이프라인 완료!")
    print("="*60)
    print(f"\n📁 결과 위치: {scripts_dir.parent.parent / 'data' / 'validation'}")
    print("\n생성된 파일:")
    print("  - bug_hunt_validation_samples.json (샘플 데이터)")
    print("  - rule_based_scores.json (규칙 기반 점수)")
    print("  - evaluation_results.json (LLM 평가 결과)")
    print("  - analysis_results.json (통계 분석)")
    print("  - visualizations/ (그래프)")

    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Bug Hunt 평가 검증 전체 파이프라인')
    parser.add_argument('--quick', action='store_true',
                       help='Quick 모드 (품질별 1개 샘플만, 테스트용)')
    args = parser.parse_args()

    success = main(quick_mode=args.quick)
    sys.exit(0 if success else 1)
