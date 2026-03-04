# 생성일: 2026-03-04
# Wars 미니게임 점수 제출 API (명예의 전당 연동)
# - PracticeDetail 의존성 없이 Wars 전용 점수를 저장
# - UserActivity.total_points에 Wars 최고 점수를 합산하여 리더보드 반영

import logging
from django.db import transaction
from django.db.models import Sum, Max
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404

from core.models import UserProfile, UserActivity, UserSolvedProblem, UserWarsScore

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class WarsScoreSubmitView(APIView):
    """
    Wars 미니게임 점수 제출 및 리더보드 반영 API

    POST /api/core/wars/submit-score/
    Body: {
        "game_type": "logic_run",
        "score": 83,
        "submitted_data": {
            "difficulty": "Associate",
            "phase1_score": 30,
            "phase2_score": 53,
            "grade": "A",
            "quest_title": "sklearn 분류 파이프라인"
        }
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        profile = get_object_or_404(UserProfile, email=user.email)

        game_type = request.data.get('game_type')
        score = request.data.get('score', 0)
        submitted_data = request.data.get('submitted_data', {})

        if not game_type:
            return Response({'error': 'game_type is required'}, status=status.HTTP_400_BAD_REQUEST)

        score = max(0, min(100, int(score)))

        try:
            with transaction.atomic():
                # 1. Wars 점수 기록 저장
                UserWarsScore.objects.create(
                    user=profile,
                    game_type=game_type,
                    score=score,
                    submitted_data=submitted_data,
                    is_perfect=score >= 90,
                )

                # 2. total_points 재계산: Practice 최고점 + Wars 최고점
                # 2-a. Practice 문제별 최고점 합산 (기존 로직)
                practice_points_data = UserSolvedProblem.objects.filter(user=profile) \
                    .values('practice_detail') \
                    .annotate(max_score=Max('score')) \
                    .aggregate(total=Sum('max_score'))
                practice_points = practice_points_data['total'] or 0

                # 2-b. Wars game_type별 최고점 합산
                wars_points_data = UserWarsScore.objects.filter(user=profile) \
                    .values('game_type') \
                    .annotate(max_score=Max('score')) \
                    .aggregate(total=Sum('max_score'))
                wars_points = wars_points_data['total'] or 0

                total_points = practice_points + wars_points

                # 3. UserActivity 갱신
                activity, _ = UserActivity.objects.get_or_create(user=profile)
                activity.total_points = total_points

                if total_points > 3000:
                    activity.current_rank = 'ENGINEER'
                elif total_points > 1000:
                    activity.current_rank = 'GOLD'
                elif total_points > 500:
                    activity.current_rank = 'SILVER'
                else:
                    activity.current_rank = 'BRONZE'

                activity.save()

            return Response({
                'message': 'Wars score saved successfully',
                'total_points': total_points,
                'current_rank': activity.current_rank,
                'wars_points': wars_points,
                'practice_points': practice_points,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error saving wars score: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
