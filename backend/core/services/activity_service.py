import logging
from django.db.models import Sum, Max
from django.db import transaction
from core.models import UserActivity, UserSolvedProblem, UserProgress, PracticeDetail

logger = logging.getLogger(__name__)

# [2026-02-18 수정] 사용자 활동 기록 및 포인트 정산 공통 서비스 정의 (Antigravity)
# - Unit 1과 Unit 3에서 공통으로 사용하여 코드 중복을 제거하고 데이터 일관성을 보장함
# - 각 문제별 최고 점수를 합산하여 전체 포인트를 계산하는 로직을 포함함
def save_user_problem_record(user_profile, detail_id, score, submitted_data):
    """
    Args:
        user_profile: UserProfile 객체
        detail_id: PracticeDetail ID (예: unit0101, unit0301)
        score: 획득 점수 (0-100)
        submitted_data: 사용자가 제출한 상세 데이터 (JSON)
        
    Returns:
        dict: 업데이트된 활동 정보 (total_points, current_rank, progress_rate)
    """
    try:
        # [2026-02-18 상세] 제공된 ID를 통해 상세 문제 정보를 데이터베이스에서 조회함
        detail = PracticeDetail.objects.get(id=detail_id)
        
        with transaction.atomic():
            # [2026-02-18 상세] 1. 새로운 문제 해결 기록을 UserSolvedProblem 모델에 생성함
            # - score는 0점 미만이 되지 않도록 보호 처리함
            # - 90점 이상인 경우 완벽 수행(is_perfect)으로 간주함
            UserSolvedProblem.objects.create(
                user=user_profile,
                practice_detail=detail,
                score=max(score, 0),
                submitted_data=submitted_data,
                is_perfect=score >= 90
            )
            
            # [2026-02-18 상세] 2. 누적 포인트 업데이트
            # - 단순 합산이 아닌, 동일 문제에 대해 여러 번 기록이 있을 경우 '최고 점수'만 반영함
            # - values('practice_detail')로 그룹화하여 문제별 Max 점수를 구한 뒤 최종 합산(Sum)함
            total_points_data = UserSolvedProblem.objects.filter(user=user_profile) \
                .values('practice_detail') \
                .annotate(max_score=Max('score')) \
                .aggregate(total=Sum('max_score'))
                
            total_points = total_points_data['total'] or 0
            
            # [2026-02-18 상세] 유저 활동 정보(UserActivity) 갱신 또는 생성
            activity, _ = UserActivity.objects.get_or_create(user=user_profile)
            activity.total_points = total_points
            
            # [2026-02-18 상세] 획득 점수에 따른 사용자 등급(Rank) 자동 조정 로직
            # - ENGINEER(3000초과), GOLD(1000초과), SILVER(500초과), BRONZE(기본)
            if total_points > 3000:
                activity.current_rank = 'ENGINEER'
            elif total_points > 1000:
                activity.current_rank = 'GOLD'
            elif total_points > 500:
                activity.current_rank = 'SILVER'
            else:
                activity.current_rank = 'BRONZE'
            
            activity.save()
            
            # [2026-02-18 상세] 3. 해당 유닛(Practice)의 진행도(UserProgress) 업데이트
            practice = detail.practice
            progress, _ = UserProgress.objects.get_or_create(user=user_profile, practice=practice)
            
            # [2026-02-18 상세] 해결한 '고유' 문제 수를 계산하여 진행률 산출에 활용함
            solved_count = UserSolvedProblem.objects.filter(
                user=user_profile, 
                practice_detail__practice=practice
            ).values('practice_detail').distinct().count()
            
            # [2026-02-18 상세] 해금된 노드 리스트 업데이트
            # - 문제 ID의 마지막 두 자리를 인덱스로 사용하여 unlocked_nodes 배열을 구성함
            try:
                node_idx = int(detail_id[-2:]) - 1
                current_nodes = set(progress.unlocked_nodes or [])
                current_nodes.add(node_idx)
                progress.unlocked_nodes = sorted(list(current_nodes))
            except (ValueError, TypeError, IndexError):
                pass

            # [2026-02-18 상세] 전체 문제 수 대비 해결 수로 진행률(0-100)을 계산함
            total_unit_problems = PracticeDetail.objects.filter(practice=practice).count()
            if total_unit_problems > 0:
                progress.progress_rate = (solved_count / total_unit_problems) * 100
            
            progress.save()
            
            return {
                'total_points': total_points,
                'current_rank': activity.current_rank,
                'progress_rate': progress.progress_rate
            }
            
    except PracticeDetail.DoesNotExist:
        logger.error(f"PracticeDetail not found: {detail_id}")
        raise ValueError(f"Invalid detail_id: {detail_id}")
    except Exception as e:
        logger.error(f"Error in save_user_problem_record: {str(e)}")
        raise e
