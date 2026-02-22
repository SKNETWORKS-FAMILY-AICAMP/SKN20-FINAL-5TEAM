"""
에이전트 기반 학습 분석 API

POST /api/core/agents/analyze/ - 사용자 학습 종합 분석
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import UserProfile
from core.agents.agent_runner import (
    run_orchestrator_agent,
    run_data_analyzer_agent,
    run_problem_generator_agent,
    run_learning_guide_agent,
    run_integration_agent,
)
from core.services.weakness_service import analyze_user_learning

logger = logging.getLogger(__name__)


class UserLearningAnalysisView(APIView):
    """
    사용자 학습 종합 분석 API

    POST /api/core/agents/analyze/
    {
        "message": "내 약점을 분석하고 공부 방법을 알려줘"
    }

    응답:
    {
        "overview": "종합 분석",
        "action_plan": [...],
        "motivation": "격려의 말"
    }
    """

    def post(self, request):
        """
        사용자 요청 → Orchestrator → 필요 에이전트 병렬 실행 → Integration
        """
        try:
            # UserProfile을 email로 조회 (Django User와의 관계가 email 기반)
            user_profile = UserProfile.objects.get(email=request.user.email)
        except (AttributeError, UserProfile.DoesNotExist) as e:
            logger.error(f"[ERROR] UserProfile 조회 실패: {e}, user: {request.user}, email: {getattr(request.user, 'email', 'N/A')}")
            return Response(
                {"error": "사용자 프로필을 찾을 수 없습니다"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 사용자 메시지 받기
        user_message = request.data.get('message', '내 학습을 분석해줘')

        logger.info(f"[에이전트] 사용자 ID {user_profile.id} - 요청: {user_message}")

        # Step 1: Data Analyzer Agent (AI 우선 - 모든 submitted_data 직접 분석)
        # → 점수 기반 분석은 제거 (Data Analyzer가 이미 깊이 있게 분석)
        logger.info("[Data Analyzer] 실행 중...")
        agent_results = {}
        agent_results['analysis'] = run_data_analyzer_agent(user_profile)
        logger.info(f"[Data Analyzer] 완료 - 약점: {len(agent_results['analysis'].get('weaknesses', []))} 강점: {len(agent_results['analysis'].get('strengths', []))}")

        # Step 2: Orchestrator 실행 - 필요 에이전트 결정
        # Data Analyzer 결과 기반으로 사용자 의도 파악
        weaknesses_for_orchestrator = [w.get('description', '') for w in agent_results['analysis'].get('weaknesses', [])]
        orchestrator_result = run_orchestrator_agent(
            user_message=user_message,
            user_weaknesses={
                "analysis_summary": agent_results['analysis'].get('analysis_summary', ''),
                "weaknesses": weaknesses_for_orchestrator
            }
        )

        logger.info(f"[Orchestrator] 선택 에이전트: {orchestrator_result.get('agents')}")

        # Step 3: 필요한 추가 에이전트 실행

        # Problem Generator Agent
        if "ProblemGenerator" in orchestrator_result.get('agents', []):
            # Data Analyzer의 약점 중 가장 심각한 것 선택
            analysis_weaknesses = agent_results.get('analysis', {}).get('weaknesses', [])
            if analysis_weaknesses:
                # severity 순서: HIGH > MEDIUM > LOW
                high_severity = [w for w in analysis_weaknesses if w.get('severity') == 'HIGH']
                focus_weakness = high_severity[0].get('description') if high_severity else analysis_weaknesses[0].get('description', '')

                if focus_weakness:
                    logger.info(f"[Problem Generator] 실행 중... (약점: {focus_weakness})")
                    agent_results['problems'] = run_problem_generator_agent(
                        user_profile,
                        focus_weakness
                    )
                    logger.info("[Problem Generator] 완료")

        # Learning Guide Agent
        if "LearningGuide" in orchestrator_result.get('agents', []):
            # Data Analyzer의 약점 중 가장 심각한 것 선택
            analysis_weaknesses = agent_results.get('analysis', {}).get('weaknesses', [])
            if analysis_weaknesses:
                # severity 순서: HIGH > MEDIUM > LOW
                high_severity = [w for w in analysis_weaknesses if w.get('severity') == 'HIGH']
                focus_weakness = high_severity[0].get('description') if high_severity else analysis_weaknesses[0].get('description', '')

                if focus_weakness:
                    logger.info(f"[Learning Guide] 실행 중... (약점: {focus_weakness})")
                    agent_results['guide'] = run_learning_guide_agent(
                        user_profile,
                        focus_weakness
                    )
                    logger.info("[Learning Guide] 완료")

        # Step 4: Integration Agent - 결과 통합
        logger.info("[Integration Agent] 실행 중...")
        final_response = run_integration_agent(agent_results, user_message)
        logger.info("[Integration Agent] 완료")

        return Response(final_response, status=status.HTTP_200_OK)


class WeaknessProfileView(APIView):
    """
    사용자 약점 프로필 조회 API

    GET /api/core/agents/weakness-profile/

    응답:
    {
        "unit1_metrics": {...},
        "unit2_metrics": {...},
        "unit3_metrics": {...},
        "top_weaknesses": [...],
        "analyzed_submission_count": 5
    }
    """

    def get(self, request):
        """사용자의 약점 프로필 조회"""
        try:
            # UserProfile을 email로 조회 (Django User와의 관계가 email 기반)
            user_profile = UserProfile.objects.get(email=request.user.email)
        except (AttributeError, UserProfile.DoesNotExist) as e:
            logger.error(f"[ERROR] GET UserProfile 조회 실패: {e}, user: {request.user}, email: {getattr(request.user, 'email', 'N/A')}")
            return Response(
                {"error": "사용자 프로필을 찾을 수 없습니다"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            weakness_data = analyze_user_learning(user_profile.id)
            logger.info(f"[약점프로필] 사용자 {user_profile.id} - 기록 수: {weakness_data.get('analyzed_submission_count')}, 약점: {weakness_data.get('top_weaknesses')}")
            return Response(weakness_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"약점 프로필 조회 오류: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
