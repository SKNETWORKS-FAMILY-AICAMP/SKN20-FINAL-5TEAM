# 수정일: 2026-01-25
# 수정내용: Antigravity - Practice 및 PracticeDetail 모델의 ID 체계를 UUID로 업그레이드

import uuid
from django.db import models
from .base_model import BaseModel

class Practice(BaseModel):
    """
    [연습(Practice) 마스터 모델]
    - 목적: AI-GYM 서비스의 핵심인 각 연습 과목(과정)의 기본 정보 관리
    """
    class Meta:
        db_table = 'gym_practice'
        verbose_name = '연습 과정'
        verbose_name_plural = '연습 과정 목록'

    # [2026-01-25] ID 체계를 문자열 패턴(unit01, unit02...)으로 변경
    id = models.CharField(
        primary_key=True, 
        max_length=20,
        help_text="과정 고유 ID (예: unit01)"
    )
    unit_number = models.IntegerField(help_text="유닛 번호 (예: 1 -> UNIT 01)")
    level = models.IntegerField(help_text="권장 레벨 (예: 10 -> LV.10)")
    title = models.CharField(max_length=100, help_text="과정 제목 (예: Pseudo Code Training)")
    subtitle = models.CharField(max_length=100, help_text="부제/설명")
    participant_count = models.IntegerField(default=0, help_text="훈련 참여자 수")
    
    # [2026-01-25] UI 동적 관리를 위한 필드 추가
    color_code = models.CharField(max_length=20, default="#58cc02", help_text="UI 표시 색상 (HEX)")
    icon_name = models.CharField(max_length=50, default="book-open", help_text="Lucide 아이콘 이름")
    
    icon_image = models.ImageField(upload_to='practice_icons/', null=True, blank=True)
    max_points = models.IntegerField(default=1000, help_text="해당 유닛 전체 완료 시 기준 총점")
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"UNIT {self.unit_number:02d}: {self.title}"

class PracticeDetail(BaseModel):
    """
    [연습 상세(PracticeDetail) 모델]
    - 목적: 연습 과정(Practice)에 종속된 세부 문제, AI 설정, 참고 자료 관리
    """
    class Meta:
        db_table = 'gym_practice_detail'
        verbose_name = '연습 상세 콘텐츠'
        verbose_name_plural = '연습 상세 콘텐츠 목록'

    # [2026-01-25] ID 체계를 문자열 패턴(unit0101, unit0102...)으로 변경
    id = models.CharField(
        primary_key=True, 
        max_length=20,
        help_text="상세 콘텐츠 고유 ID (예: unit0101)"
    )
    
    # [2026-01-25] Practice 모델과의 연결 (DB 컬럼명: practice_id)
    practice = models.ForeignKey(
        Practice, 
        on_delete=models.CASCADE, 
        related_name='details',
        help_text="소속된 연습 과정 (Practice.id 참조)"
    )
    detail_title = models.CharField(max_length=200, help_text="상세 항목 제목")
    
    TYPE_CHOICES = [
        ('PROBLEM', '실습 문제'),
        ('CHATTING', 'AI 채팅 설정'),
        ('REFERENCE', '참고 자료'),
    ]
    detail_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='PROBLEM')
    
    content_data = models.JSONField(help_text="콘텐츠 데이터 (JSON 형식의 문제/설정값)")
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"[{self.detail_type}] {self.detail_title} ({self.practice.title})"
