# 수정일: 2026-01-22
# 수정내용: practice 모델

from django.db import models
from .base_model import BaseModel

class Practice(models.Model):
    """
    팀원 C 담당: practice 모델(현재는 임시. 추후 변경 가능)
    """
    class Meta:
        db_table = 'gym_practice'  # 원하는 테이블 이름

    practice_number = models.CharField(max_length=50, unique=True)
    practice_id = models.DecimalField(max_digits=12, decimal_places=2)
    practice_name = models.CharField(max_length=50)
    practice_price = models.DecimalField(max_digits=12, decimal_places=2)
    practice_description = models.TextField()
    practice_status = models.CharField(max_length=20, default='PENDING')
    

    def __str__(self):
        return self.practice_id
