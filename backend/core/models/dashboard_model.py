# 수정일: 2026-01-22
# 수정내용: Antigravity - BaseModel 상속 적용 및 recorded_date를 create_date로 대체

from django.db import models
from .base_model import BaseModel

class DashboardLog(BaseModel):
    """
    팀원 F 담당: 대시보드 통계/로그 모델
    """
    # 2026-01-22 수정: recorded_date -> BaseModel.create_date 사용
    event_name = models.CharField(max_length=100)
    event_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.event_name} - {self.event_count}"
