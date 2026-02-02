"""
버그헌트 문제 출제 에이전트 (관리자용 CLI)
P1 Progressive 문제 생성 및 Supabase DB 저장
"""

import argparse
import json
import sys
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 상위 디렉토리를 path에 추가 (import 가능하도록)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.agent import run_problem_agent
from agent.spec import TRACK_SPECS
from db.repository import save_problem


def main():
    parser = argparse.ArgumentParser(
        description="버그헌트 문제 출제 에이전트 (관리자용 CLI)"
    )

    parser.add_argument(
        "--track",
        type=str,
        default="pytorch_mnist",
        help=f"트랙 ID (지원: {', '.join(TRACK_SPECS.keys())})"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="DB 저장 없이 생성만 테스트"
    )

    parser.add_argument(
        "--max-retry",
        type=int,
        default=5,
        help="최대 재시도 횟수 (기본값: 5)"
    )

    parser.add_argument(
        "--output",
        type=str,
        help="JSON 파일로 저장할 경로 (예: problem.json)"
    )

    args = parser.parse_args()

    if args.track not in TRACK_SPECS:
        print(f"[ERROR] 지원되지 않는 트랙입니다: {args.track}")
        print(f"        지원 가능한 트랙: {', '.join(TRACK_SPECS.keys())}")
        return

    print("\n" + "="*60)
    print(f"  버그헌트 문제 생성 에이전트")
    print(f"  Track: {args.track}")
    print(f"  Target: P1 Progressive (3 steps)")
    print(f"  Max Retry: {args.max_retry}")
    print(f"  Dry Run: {args.dry_run}")
    print("="*60 + "\n")

    # 환경변수 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("[ERROR] OPENAI_API_KEY가 설정되지 않았습니다.")
        print("        .env 파일에 OPENAI_API_KEY를 추가해주세요.")
        return

    if not args.dry_run:
        required_vars = ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME"]
        missing = [v for v in required_vars if not os.getenv(v)]
        if missing:
            print(f"[ERROR] DB 환경변수가 설정되지 않았습니다: {missing}")
            return

    try:
        # 문제 생성
        problem = run_problem_agent(track_id=args.track, max_retry=args.max_retry)

        print("\n" + "="*60)
        print("  생성 완료!")
        print("="*60)

        # JSON 파일로 저장 (누적 저장 지원)
        if args.output:
            output_path = args.output
            
            # 기존 파일 읽기
            final_data = {"progressiveProblems": []}
            if os.path.exists(output_path):
                try:
                    with open(output_path, 'r', encoding='utf-8') as f:
                        file_content = json.load(f)
                        if isinstance(file_content, dict) and "progressiveProblems" in file_content:
                            final_data = file_content
                except Exception as e:
                    print(f"[WARN] 기존 파일 로드 실패: {e}. 새로 생성합니다.")

            # 새로운 문제 추가 (ID 중복 체크는 생략)
            final_data["progressiveProblems"].append(problem)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=2, ensure_ascii=False)
            print(f"\n[FILE] JSON 저장 완료: {output_path} (현재 총 {len(final_data['progressiveProblems'])}개 문제)")
        else:
            # 콘솔에 출력 (Windows cp949 인코딩 문제 방지)
            try:
                print(json.dumps(problem, indent=2, ensure_ascii=False))
            except UnicodeEncodeError:
                print(json.dumps(problem, indent=2, ensure_ascii=True))

        # DB 저장
        if not args.dry_run:
            print("\n[DB] Saving to Supabase...")
            save_problem(problem)
            print("\n[SUCCESS] DB 저장 완료")
        else:
            print("\n[DRY-RUN] DB 저장 스킵")

    except Exception as e:
        print(f"\n[ERROR] 문제 생성 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
