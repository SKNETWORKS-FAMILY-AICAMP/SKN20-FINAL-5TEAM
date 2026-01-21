# 수정일: 2026-01-20
# 수정내용: 팀원 A (User 담당) - 회원 관련 모델 정의

from django.db import models

class UserProfile(models.Model):
    """
    팀원 A 담당: 사용자 프로필 모델
    """
    # [수정일: 2026-01-21] 테이블명 변경 (gym_user)
    class Meta:
        db_table = 'gym_user'

    # [수정일: 2026-01-21] user_id를 PK로 변경, user_seq 추가
    user_id = models.CharField(max_length=50, primary_key=True)  # 로그인 아이디 (PK)
    user_seq = models.IntegerField(unique=True, null=True, blank=True) # 순번 (자동 채번)
    
    user_name = models.CharField(max_length=50)  # 사용자 이름
    user_nickname = models.CharField(max_length=50, null=True, blank=True)  # 사용자 닉네임
    email = models.EmailField(unique=True)  # 이메일
    birth_date = models.DateField(null=True, blank=True)  # 생년월일
    password = models.CharField(max_length=128)  # 비밀번호   
    
    # 추가 필드
    create_id = models.CharField(max_length=50, null=True, blank=True)
    update_id = models.CharField(max_length=50, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    use_yn = models.CharField(max_length=1, default='Y')
    
    def save(self, *args, **kwargs):
        # 1. user_id 자동 생성 (email @ 앞부분)
        if not self.user_id and self.email:
            # [수정일: 2026-01-21] user_id 길이 초과 방지 (최대 50자)
            self.user_id = self.email.split('@')[0][:50]
            
        # 2. user_seq 자동 채번
        if not self.user_seq:
            last_user = UserProfile.objects.order_by('-user_seq').first()
            if last_user and last_user.user_seq is not None:
                self.user_seq = last_user.user_seq + 1
            else:
                self.user_seq = 1
                
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user_name} ({self.user_id})"

class UserDetail(models.Model):
    """
    팀원 A 담당: 사용자 상세 정보 모델 (UserProfile과 1:1)
    """
    # [수정일: 2026-01-21] 테이블명 변경 (gym_userdetail)
    class Meta:
        db_table = 'gym_userdetail'

    # [수정일: 2026-01-21] user_id를 PK로 설정 (식별 관계)
    # 필드명을 user_id로 변경하고 db_column도 user_id로 지정
    user_id = models.OneToOneField(
        UserProfile, 
        on_delete=models.CASCADE, 
        primary_key=True, 
        db_column='user_id',
        related_name='user_detail'
    )
    
    # [수정일: 2026-01-21] detail_seq는 단순 순번 필드로 변경 (PK 아님)
    detail_seq = models.IntegerField(null=True, blank=True)

    is_developer = models.BooleanField(default=True)  # 개발자 여부
    job_role = models.TextField(null=True, blank=True)  # 직군 (다중 선택 가능하므로 Text)
    # [수정일: 2026-01-21] IT INTERESTS (관심 분야) 추가, 길이 제한 해제
    interests = models.TextField(null=True, blank=True) 
    
    def save(self, *args, **kwargs):
        # detail_seq 자동 채번
        if not self.detail_seq:
            last_detail = UserDetail.objects.order_by('-detail_seq').first()
            if last_detail and last_detail.detail_seq is not None:
                self.detail_seq = last_detail.detail_seq + 1
            else:
                self.detail_seq = 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user_id.user_name}'s Detail"
