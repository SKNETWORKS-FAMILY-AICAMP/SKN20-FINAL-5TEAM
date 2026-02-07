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

    # [수정일: 2026-02-07] PK 구조 리팩토링 최종 단계: 정수형 PK(BigAutoField) 채택
    id = models.BigAutoField(primary_key=True)  # 시스템용 고유 번호 (PK)
    
    # [수정일: 2026-02-07] 유저 식별용 호출명 (Unique)
    username = models.CharField(max_length=100, unique=True)
    
    user_name = models.CharField(max_length=50)  # 사용자 이름
    user_nickname = models.CharField(max_length=50, null=True, blank=True)  # 사용자 닉네임
    email = models.EmailField(unique=True)  # 이메일
    birth_date = models.DateField(null=True, blank=True)  # 생년월일
    password = models.CharField(max_length=128)  # 비밀번호   
    
    def save(self, *args, **kwargs):
        # [수정일: 2026-02-07] 유니크한 username 충돌 방지 로직 강화
        # 신규 생성(id가 없음) 명시적인 username이 있더라도 중복되면 숫자를 붙임
        if not self.id:
            if not self.username and self.email:
                self.username = self.email.split('@')[0][:90]
            
            base = self.username
            candidate = base
            counter = 1
            from django.contrib.auth.models import User
            # 자신을 제외한 중복 체크 (UserProfile뿐만 아니라 Django 기본 User와도 대조)
            while UserProfile.objects.filter(username=candidate).exists() or User.objects.filter(username=candidate).exists():
                candidate = f"{base}_{counter}"
                counter += 1
            self.username = candidate
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user_name} ({self.username})"

class UserDetail(BaseModel):
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
    
    # [수정일: 2026-02-07] 최종적으로 JSONField 적용
    job_role = models.JSONField(default=list, null=True, blank=True)
    interests = models.JSONField(default=list, null=True, blank=True)
    
    # [수정일: 2026-01-22] 참조 필드명 변경 반영
    def __str__(self):
        return f"{self.user.user_name}'s Detail"
