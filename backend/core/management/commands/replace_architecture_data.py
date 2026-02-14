"""
아키텍처 문제 데이터 교체 커맨드
기존 architecture.json 데이터를 architecture_advanced_gcp.json 데이터로 교체
"""
import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Practice, PracticeDetail


class Command(BaseCommand):
    help = '아키텍처 문제 데이터를 architecture_advanced_gcp.json으로 교체'

    def add_arguments(self, parser):
        parser.add_argument(
            '--practice-id',
            type=str,
            default='unit03',
            help='아키텍처 문제가 속한 Practice ID (기본값: unit03)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제 DB 변경 없이 시뮬레이션만 실행'
        )

    def handle(self, *args, **options):
        practice_id = options['practice_id']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('[DRY RUN] 실제 DB 변경 없이 시뮬레이션만 실행합니다.\n'))

        # JSON 파일 경로 설정
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        json_path = os.path.join(base_dir, 'frontend', 'src', 'data', 'architecture_advanced_gcp.json')

        self.stdout.write(f'[INFO] JSON 파일 경로: {json_path}')

        # JSON 파일 로드
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                architecture_data = json.load(f)
            self.stdout.write(self.style.SUCCESS(f'[OK] JSON 파일 로드 완료: {len(architecture_data)}개 문제'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'[ERROR] JSON 파일을 찾을 수 없습니다: {json_path}'))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] JSON 파일 파싱 오류: {e}'))
            return

        # Practice 확인
        try:
            practice = Practice.objects.get(id=practice_id)
            self.stdout.write(self.style.SUCCESS(f'[OK] Practice 확인: {practice.title}'))
        except Practice.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'[ERROR] Practice를 찾을 수 없습니다: {practice_id}'))
            return

        if dry_run:
            # DRY RUN: 삭제될 데이터만 표시
            existing_details = PracticeDetail.objects.filter(practice=practice)
            self.stdout.write(f'\n[DELETE] 삭제 예정 PracticeDetail 수: {existing_details.count()}개')
            for detail in existing_details:
                self.stdout.write(f'  - {detail.id}: {detail.detail_title}')

            self.stdout.write(f'\n[CREATE] 추가 예정 PracticeDetail 수: {len(architecture_data)}개')
            for idx, problem in enumerate(architecture_data, 1):
                new_id = f'{practice_id}{idx:02d}'
                self.stdout.write(f'  - {new_id}: {problem["title"]}')

            self.stdout.write(self.style.WARNING('\n[DRY RUN] 완료. 실제 DB는 변경되지 않았습니다.'))
            self.stdout.write(self.style.WARNING('실제 교체를 원하시면 --dry-run 옵션 없이 실행하세요.'))
            return

        # 실제 DB 변경
        try:
            with transaction.atomic():
                # 1. 기존 아키텍처 문제 삭제
                deleted_count = PracticeDetail.objects.filter(practice=practice).delete()[0]
                self.stdout.write(self.style.WARNING(f'[DELETE] 기존 PracticeDetail 삭제: {deleted_count}개'))

                # 2. 새로운 아키텍처 문제 추가
                created_details = []
                for idx, problem in enumerate(architecture_data, 1):
                    detail_id = f'{practice_id}{idx:02d}'

                    detail = PracticeDetail(
                        id=detail_id,
                        practice=practice,
                        detail_title=problem['title'],
                        detail_type='PROBLEM',
                        content_data=problem,  # 전체 JSON 데이터를 content_data에 저장
                        display_order=idx,
                        is_active=True
                    )
                    created_details.append(detail)
                    self.stdout.write(f'  [+] {detail_id}: {problem["title"]}')

                # Bulk create로 한번에 생성
                PracticeDetail.objects.bulk_create(created_details)
                self.stdout.write(self.style.SUCCESS(f'\n[OK] 새로운 PracticeDetail 추가: {len(created_details)}개'))

                self.stdout.write(self.style.SUCCESS('\n[SUCCESS] 아키텍처 데이터 교체 완료!'))
                self.stdout.write(f'   Practice: {practice.title} (ID: {practice_id})')
                self.stdout.write(f'   총 문제 수: {len(created_details)}개')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n[ERROR] 데이터 교체 중 오류 발생: {e}'))
            raise
