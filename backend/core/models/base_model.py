# 수정일: 2026-02-12
# 수정내용: BaseModel.save() 오버라이딩 - create_id, update_id 자동 할당 로직 추가

from django.db import models
from core.middleware import get_current_user

class BaseModel(models.Model):
    """
    모든 모델에서 공통으로 사용하는 필드들을 정의하는 추상 베이스 모델
    """
    create_id = models.CharField(max_length=50, null=True, blank=True, help_text="생성자 ID")
    update_id = models.CharField(max_length=50, null=True, blank=True, help_text="수정자 ID")
    create_date = models.DateTimeField(auto_now_add=True, help_text="생성 일시")
    update_date = models.DateTimeField(auto_now=True, help_text="수정 일시")
    use_yn = models.CharField(max_length=1, default='Y', help_text="사용 여부 (Y/N)")

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        데이터 저장 시 생성자/수정자 정보를 자동으로 세팅합니다.
        """
        # 전역 미들웨어를 통해 현재 로그인한 사용자 정보를 가져옵니다.
        current_user = get_current_user()

        # 1. 신규 생성 시 (pk가 없는 경우)
        if not self.pk:
            if not self.create_id:
                self.create_id = current_user
            if not self.update_id:
                self.update_id = current_user
        # 2. 기존 데이터 수정 시
        else:
            self.update_id = current_user

        # 부모 클래스의 save() 호출하여 실제 DB 반영
        super().save(*args, **kwargs)
