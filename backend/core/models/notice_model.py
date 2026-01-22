# 수정일: 2026-01-22
# 수정내용: Antigravity - 공지사항 용도에 맞게 Post 모델을 Notice로 변경 (테이블명 및 필드명 리팩토링)

from django.db import models
from .base_model import BaseModel

class Notice(BaseModel):
    """
    공지사항 모델
    """
    class Meta:
        db_table = 'gym_notice'

    # 2026-01-22 수정: board_id -> id 변경 반영 유지 및 필드명 간결화
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)  # 제목 (기존 board_title)
    contents = models.TextField()  # 내용 (기존 board_contents)
    open_date = models.DateTimeField(null=True, blank=True)  # 게시 시작일
    close_date = models.DateTimeField(null=True, blank=True)  # 게시 종료일

    def __str__(self):
        return self.title
