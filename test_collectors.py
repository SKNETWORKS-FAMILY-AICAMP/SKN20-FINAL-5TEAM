"""
Collector 시스템 테스트 스크립트

Phase 3 사이트별 최적화 Collector 테스트
"""

import sys
from pathlib import Path

# job-planner-agent를 Python path에 추가
# 참고: 폴더 이름에 하이픈(-)이 있어서 직접 import 불가, 경로로 추가
project_root = Path(__file__).resolve().parent
job_planner_agent_path = project_root / "job-planner-agent"
sys.path.insert(0, str(job_planner_agent_path))

from collectors import CollectorRouter

def test_collector(url, site_name):
    """
    단일 URL에 대해 Collector 테스트

    Args:
        url (str): 테스트할 채용공고 URL
        site_name (str): 사이트 이름 (표시용)
    """
    print(f"\n{'='*80}")
    print(f"🧪 {site_name} 테스트 시작")
    print(f"URL: {url}")
    print(f"{'='*80}\n")

    router = CollectorRouter()
    text = router.collect_with_fallback(url)

    print(f"\n{'='*80}")
    if text:
        print(f"✅ 성공! 추출된 텍스트: {len(text)} 문자")
        print(f"\n📄 미리보기 (처음 500자):")
        print("-" * 80)
        print(text[:500])
        print("-" * 80)

        # 채용 키워드 확인
        keywords_found = []
        keywords = ['채용', '모집', '필수', '우대', 'Python', 'Java', 'Django', 'React', '개발자']
        for keyword in keywords:
            if keyword in text:
                keywords_found.append(keyword)

        print(f"\n🔍 발견된 키워드: {', '.join(keywords_found)}")
    else:
        print(f"❌ 실패! 텍스트 추출 불가")
    print(f"{'='*80}\n")

    return len(text) if text else 0


def main():
    """
    메인 테스트 함수
    """
    print("\n" + "🚀 Collector 시스템 통합 테스트".center(80, "="))
    print("Phase 3: 사이트별 최적화 Collector 테스트\n")

    test_urls = [
        ("https://www.saramin.co.kr/zf_user/jobs/relay/view?view_type=search&rec_idx=52971222", "사람인"),
        ("https://www.jobkorea.co.kr/Recruit/GI_Read/48279054", "잡코리아"),
        ("https://www.wanted.co.kr/wd/337245", "원티드")
    ]

    results = []

    for url, site_name in test_urls:
        try:
            char_count = test_collector(url, site_name)
            results.append((site_name, "성공" if char_count > 0 else "실패", char_count))
        except Exception as e:
            print(f"❌ {site_name} 테스트 중 에러 발생: {e}")
            import traceback
            traceback.print_exc()
            results.append((site_name, "에러", 0))

    # 최종 결과 요약
    print("\n" + "📊 테스트 결과 요약".center(80, "="))
    print(f"{'사이트':<15} {'결과':<10} {'추출 문자 수':<15}")
    print("-" * 80)
    for site, status, count in results:
        status_icon = "✅" if status == "성공" else "❌"
        print(f"{status_icon} {site:<13} {status:<10} {count:,}자")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
