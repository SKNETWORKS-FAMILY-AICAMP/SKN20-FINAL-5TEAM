# 수정일: 2026-01-22
# 수정내용: Antigravity - BaseModel 상속 적용 및 필드 표준화 (id)

from django.db import models
from .base_model import BaseModel

class Practice(BaseModel):
    """
    팀원 C 담당: 연습용 모델 (현재는 임시) 
    """
    class Meta:
        db_table = 'gym_practice'

    # 2026-01-22 수정: id 필드 표준화 및 BaseModel 상속
    id = models.AutoField(primary_key=True)
    practice_number = models.CharField(max_length=50, unique=True)
    practice_name = models.CharField(max_length=50)
    practice_price = models.DecimalField(max_digits=12, decimal_places=2)
    practice_description = models.TextField()
    practice_status = models.CharField(max_length=20, default='PENDING')

    def __str__(self):
        return f"{self.practice_name} ({self.id})"
