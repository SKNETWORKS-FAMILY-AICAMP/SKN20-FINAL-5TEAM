"""unit03(시스템아키텍처) 문제 데이터 개수를 확인하는 스크립트 (1회성 유틸리티)."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models.Practice_model import Practice, PracticeDetail

unit_id = 'unit03'
total_details = PracticeDetail.objects.filter(practice_id=unit_id).count()
problems = PracticeDetail.objects.filter(practice_id=unit_id, detail_type='PROBLEM').count()
others = PracticeDetail.objects.filter(practice_id=unit_id).exclude(detail_type='PROBLEM')

from core.models.activity_model import UserSolvedProblem

print(f"--- Unit 3 Inspection ---")
print(f"Total Detail Records: {total_details}")
print(f"Detail Type 'PROBLEM': {problems}")

problem_items = PracticeDetail.objects.filter(practice_id=unit_id, detail_type='PROBLEM').order_by('id')
pattern_no_underscore = problem_items.filter(id__regex=r'^unit03\d{2}$').count()
pattern_underscore = problem_items.filter(id__regex=r'^unit03_\d{2}$').count()

print(f"\nID Patterns:")
print(f"  - unit03XX style: {pattern_no_underscore}")
print(f"  - unit03_XX style: {pattern_underscore}")

ids_no_underscore = list(problem_items.filter(id__regex=r'^unit03\d{2}$').values_list('id', flat=True))
ids_underscore = list(problem_items.filter(id__regex=r'^unit03_\d{2}$').values_list('id', flat=True))

print(f"\nUsage in UserSolvedProblem:")
usage_no_underscore = UserSolvedProblem.objects.filter(practice_detail_id__in=ids_no_underscore).count()
usage_underscore = UserSolvedProblem.objects.filter(practice_detail_id__in=ids_underscore).count()
print(f"  - unit03XX used: {usage_no_underscore} times")
print(f"  - unit03_XX used: {usage_underscore} times")
