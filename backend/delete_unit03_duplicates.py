import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models.Practice_model import PracticeDetail
from core.models.activity_model import UserSolvedProblem
from django.db import transaction

def delete_unit03_duplicates():
    unit_id = 'unit03'
    # 언더바 없는 ID 패턴 (unit0301 ~ unit0331)
    target_ids = [f"unit03{i:02d}" for i in range(1, 32)]
    
    print(f"🚀 Unit 3 중복 데이터 삭제 시작 (대상: {len(target_ids)}개)")
    
    try:
        with transaction.atomic():
            # 1. 삭제 전 사용자 기록이 있는지 최종 확인
            usage_count = UserSolvedProblem.objects.filter(practice_detail_id__in=target_ids).count()
            if usage_count > 0:
                print(f"❌ 오류: 삭제 대상 ID 중 {usage_count}건의 사용자 기록이 발견되었습니다. 삭제를 중단합니다.")
                return

            # 2. 데이터 삭제
            deleted_count, _ = PracticeDetail.objects.filter(id__in=target_ids, practice_id=unit_id).delete()
            
            # 3. 결과 확인
            remaining_count = PracticeDetail.objects.filter(practice_id=unit_id, detail_type='PROBLEM').count()
            
            print(f"✅ 성공적으로 {deleted_count}개의 중복 데이터를 삭제했습니다.")
            print(f"📊 Unit 3 남은 미션 수: {remaining_count}개")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == '__main__':
    # 수동 확인을 한 번 더 거치기 위해 실행 전 문구 출력
    print("⚠️  이 스크립트는 Unit 3의 중복 데이터를 영구적으로 삭제합니다.")
    delete_unit03_duplicates()
