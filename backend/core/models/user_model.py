# 수정일: 2026-01-22
# 수정내용: Antigravity - user_id를 id로, UserDetail의 외래키 필드명을 user로 변경

from django.db import models
from .base_model import BaseModel

class UserProfile(BaseModel):
    """
    팀원 A 담당: 사용자 프로필 모델
    """
    # [수정일: 2026-01-21] 테이블명 변경 (gym_user)
    class Meta:
        db_table = 'gym_user'

    # [수정일: 2026-01-22] user_id -> id 변경 (상징적인 PK 명칭 통일을 위함)
    id = models.CharField(max_length=50, primary_key=True)  # 로그인 아이디 (PK)
    
    user_name = models.CharField(max_length=50)  # 사용자 이름
    user_nickname = models.CharField(max_length=50, null=True, blank=True)  # 사용자 닉네임
    email = models.EmailField(unique=True)  # 이메일
    birth_date = models.DateField(null=True, blank=True)  # 생년월일
    password = models.CharField(max_length=128)  # 비밀번호   
    
    def save(self, *args, **kwargs):
        # 1. id 자동 생성 (email @ 앞부분)
        if not self.id and self.email:
            # [수정일: 2026-01-21] id 길이 초과 방지 (최대 50자)
            self.id = self.email.split('@')[0][:50]
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user_name} ({self.id})"

class UserDetail(models.Model):
    """
    팀원 A 담당: 사용자 상세 정보 모델 (UserProfile과 1:1)
    """
    # [수정일: 2026-01-21] 테이블명 변경 (gym_userdetail)
    class Meta:
        db_table = 'gym_userdetail'

    # [수정일: 2026-01-21] user_id를 PK로 설정 (식별 관계)
    # [수정일: 2026-01-22] 필드명을 user로 변경 (Django 표준 관례)
    user = models.OneToOneField(
        UserProfile, 
        on_delete=models.CASCADE, 
        primary_key=True, 
        db_column='user_id',
        related_name='user_detail'
    )

    is_developer = models.BooleanField(default=True)  # 개발자 여부
    job_role = models.TextField(null=True, blank=True)  # 직군 (다중 선택 가능하므로 Text)
    # [수정일: 2026-01-21] IT INTERESTS (관심 분야) 추가, 길이 제한 해제
    interests = models.TextField(null=True, blank=True) 
    
    # [수정일: 2026-01-22] 참조 필드명 변경 반영
    def __str__(self):
        return f"{self.user.user_name}'s Detail"
