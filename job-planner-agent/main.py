# main.py
"""
Job Planner Agent - 전체 플로우
원본 v3.1 기반
"""
from agent.models import UserProfile, JobPosting
from agent.orchestrator import AgentOrchestrator
from agent.planner import Planner
from scoring.engine import ScoringEngine
from llm.gateway import LLMGateway
import os

def main():
    print("=" * 60)
    print("Job Planner Agent v1.0")
    print("=" * 60 + "\n")

    # OPENAI_API_KEY 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("테스트 모드로 실행합니다 (LLM 기능 제한).\n")

    # 테스트용 사용자 프로필
    user = UserProfile(
        name="테스트 유저",
        current_role="주니어 개발자",
        experience_years=2,
        skills=["Python", "Django", "MySQL"],
        skill_levels={"Python": 4, "Django": 3, "MySQL": 3},
        education="학사",
        certifications=[],
        career_goals="백엔드 개발자",
        available_prep_days=30
    )

    # 테스트용 채용공고
    job = JobPosting(
        source="text",
        raw_text="백엔드 개발자 채용",
        company_name="테스트 회사",
        position="백엔드 개발자",
        required_skills=["Python", "Django", "PostgreSQL", "Redis"],
        preferred_skills=["Docker", "Kubernetes"],
        experience_range="2-4년",
        job_description="대규모 트래픽 처리 및 데이터베이스 최적화",
        tech_stack=["Python", "Django", "PostgreSQL", "Redis"],
        domain="웹 서비스",
        deadline="2026-03-15",
        deadline_days=28
    )

    print(f"[사용자] {user.name}")
    print(f"  보유 스킬: {user.skills}")
    print(f"  경력: {user.experience_years}년\n")

    print(f"[공고] {job.company_name} - {job.position}")
    print(f"  필수 스킬: {job.required_skills}")
    print(f"  우대 스킬: {job.preferred_skills}\n")

    # 컴포넌트 초기화
    try:
        llm = LLMGateway()
        planner = Planner(llm)
        scoring = ScoringEngine()
        orchestrator = AgentOrchestrator(planner, scoring)

        # 에이전트 실행
        result = orchestrator.run(user, job)

        print("\n✅ 에이전트 실행 완료!")

    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        print("\n스킬 매칭만 실행합니다...\n")

        # Fallback: 스킬 매칭만
        scoring = ScoringEngine()
        report = scoring.generate_match_report(user, job)

        print("=" * 60)
        print("매칭 결과")
        print("=" * 60)
        print(f"Readiness: {report['readiness_score']:.3f}")
        print(f"Skill Gap: {report['skill_gap_score']:.3f}\n")

        print(f"매칭된 스킬 ({len(report['matched'])}개):")
        for m in report['matched']:
            print(f"  ✅ {m['required_skill']} ↔ {m['best_match']} "
                  f"(유사도: {m['similarity']:.3f})")

        print(f"\n부족한 스킬 ({len(report['missing'])}개):")
        for m in report['missing']:
            print(f"  ❌ {m['required_skill']} "
                  f"(가장 유사: {m['best_match']}, 유사도: {m['similarity']:.3f})")

        print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
