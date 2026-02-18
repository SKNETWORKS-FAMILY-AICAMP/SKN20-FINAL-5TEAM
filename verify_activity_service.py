import os
import django
import sys

# Django 설정 로드
sys.path.append('c:\\SKN20-FINAL-5TEAM\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import UserProfile, PracticeDetail, UserSolvedProblem, UserActivity, UserProgress
from core.services.activity_service import save_user_problem_record

def verify_activity_service():
    print("=== Activity Service Verification Start ===")
    
    # 1. 테스트 유저 및 문제 데이터 확인
    try:
        user = UserProfile.objects.first()
        if not user:
            print("❌ No user found in database.")
            return
        
        # Unit 1 실습 데이터가 있는지 확인 (unit0101)
        # 만약 없으면 하나 가져옴
        detail = PracticeDetail.objects.filter(id__startswith='unit01').first()
        if not detail:
            print("❌ No Unit 1 PracticeDetail found (unit01XX).")
            # Unit 3라도 테스트
            detail = PracticeDetail.objects.filter(id__startswith='unit03').first()
            if not detail:
                print("❌ No PracticeDetail found at all.")
                return
        
        print(f"Testing with User: {user.username}, PracticeDetail: {detail.id}")
        
        # 2. 저장 서비스 호출
        test_score = 95
        test_data = {"test": "data", "source": "verification_script"}
        
        result = save_user_problem_record(user, detail.id, test_score, test_data)
        
        print(f"✅ Service Result: {result}")
        
        # 3. DB 실제 저장 여부 확인
        saved_record = UserSolvedProblem.objects.filter(user=user, practice_detail=detail).last()
        if saved_record and saved_record.score == test_score:
            print(f"✅ DB Record verified: Score {saved_record.score}")
        else:
            print("❌ DB Record verification failed.")
            
        # 4. 활동 포인트 업데이트 확인
        activity = UserActivity.objects.get(user=user)
        print(f"✅ User Activity Points: {activity.total_points}, Rank: {activity.current_rank}")
        
        # 5. 진행률 확인
        progress = UserProgress.objects.get(user=user, practice=detail.practice)
        print(f"✅ User Progress Rate: {progress.progress_rate}%, Unlocked Nodes: {progress.unlocked_nodes}")

    except Exception as e:
        print(f"❌ Verification failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_activity_service()
