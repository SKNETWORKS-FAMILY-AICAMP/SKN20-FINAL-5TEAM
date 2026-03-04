from django.http import JsonResponse
from django.views import View
from core.models.activity_model import UserBattleRecord
from core.models.user_model import UserProfile

class UserBattleRecordView(View):
    """
    [수정일: 2026-03-03] 유저의 배틀 게임 전적(승/무/패)을 조회하는 API
    """
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        
        try:
            # [수정일: 2026-03-03] UserProfile 조회 (email 필드 기준)
            profile = UserProfile.objects.get(email=request.user.email)
            # 전적 정보 조회 또는 생성
            record, created = UserBattleRecord.objects.get_or_create(user=profile)
            
            return JsonResponse({
                'win': record.win_count,
                'draw': record.draw_count,
                'lose': record.lose_count,
                'total': record.win_count + record.draw_count + record.lose_count
            })
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'Profile not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
