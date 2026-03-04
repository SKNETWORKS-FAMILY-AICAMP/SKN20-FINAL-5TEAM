# 수정일: 2026-02-12
# 수정내용: UserSolvedProblem의 unique_together 제약 조건 제거 (모든 제출 이력 보존)

from django.db import models
from .base_model import BaseModel
from .user_model import UserProfile
from .practice_model import Practice, PracticeDetail

class UserAvatar(BaseModel):
    """
    나노바나나(Nano Banana)로 생성된 아바타의 이력과 버전 관리
    """
    user = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='avatars',
        help_text="아바타 소유자"
    )

    image_url = models.URLField(max_length=500, help_text="나노바나나로 생성된 아바타 이미지 URL")
    prompt = models.TextField(help_text="아바타 생성에 사용된 AI 프롬프트")
    seed = models.BigIntegerField(null=True, blank=True, help_text="이미지 재생성을 위한 고유 시드값")
    version = models.IntegerField(default=1, help_text="아바타 진화/수정 버전")
    is_active = models.BooleanField(default=False, help_text="현재 사용 중인 대표 아바타 여부")

    class Meta:
        db_table = 'gym_user_avatar'
        verbose_name = '사용자 아바타'
        verbose_name_plural = '사용자 아바타 목록'

    def __str__(self):
        return f"{self.user.id}'s Avatar v{self.version} ({'Active' if self.is_active else 'Inactive'})"

class UserActivity(BaseModel):
    """
    사용자의 통합 포인트, 랭킹 및 현재 아바타 상태 관리
    """
    user = models.OneToOneField(
        UserProfile, 
        on_delete=models.CASCADE, 
        primary_key=True,
        related_name='activity'
    )
    total_points = models.IntegerField(default=0, help_text="누적 아케이드 포인트")
    current_rank = models.CharField(
        max_length=20, 
        default='BRONZE', 
        help_text="현재 유저 등급 (BRONZE, SILVER, GOLD, ENGINEER 등)"
    )
    active_avatar = models.ForeignKey(
        UserAvatar, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='active_in_activities',
        help_text="현재 장착 중인 아바타"
    )
    last_activity_date = models.DateTimeField(auto_now=True, help_text="마지막 활동 일시")

    class Meta:
        db_table = 'gym_user_activity'
        verbose_name = '사용자 활동 정보'
        verbose_name_plural = '사용자 활동 정보 목록'

    def __str__(self):
        return f"{self.user.id}: {self.current_rank} ({self.total_points}pts)"

class UserSolvedProblem(BaseModel):
    """
    사용자별 개별 문제 해결 이력 및 획득 점수 기록
    """
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='solved_problems'
    )
    practice_detail = models.ForeignKey(
        PracticeDetail,
        on_delete=models.CASCADE,
        help_text="해결한 세부 문제"
    )
    score = models.IntegerField(default=0, help_text="해당 문제에서 획득한 점수")
    submitted_data = models.JSONField(null=True, blank=True, help_text="사용자가 제출한 최종 데이터/코드")
    is_perfect = models.BooleanField(default=False, help_text="만점 해결 여부")
    solved_date = models.DateTimeField(auto_now_add=True)
    attempt_number = models.IntegerField(default=1, help_text="문제 제출 시도 횟수")
    is_best_score = models.BooleanField(default=True, help_text="최고 점수 기록 여부")

    class Meta:
        db_table = 'gym_user_solved_problem'
        verbose_name = '문제 해결 기록'
        verbose_name_plural = '문제 해결 기록 목록'

class UserProgress(BaseModel):
    """
    연습 과정(Unit)별 진행 상태 및 해금 노드 관리
    """
    user = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='progresses'
    )
    practice = models.ForeignKey(
        Practice, 
        on_delete=models.CASCADE,
        help_text="참여 중인 유닛"
    )
    unlocked_nodes = models.JSONField(default=list, help_text="해금된 문제 인덱스 목록 (예: [0, 1, 2])")
    progress_rate = models.FloatField(default=0.0, help_text="해당 유닛 진행률 (%)")

    class Meta:
        db_table = 'gym_user_progress'
        unique_together = ('user', 'practice')
        verbose_name = '유닛 진행 상태'
        verbose_name_plural = '유닛 진행 상태 목록'

# [수정일: 2026-03-03] 배틀 게임 전적 저장을 위한 모델 추가
class UserBattleRecord(BaseModel):
    user = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='battle_record',
        help_text="전적 소유자"
    )
    win_count = models.IntegerField(default=0, help_text="승리 횟수")
    draw_count = models.IntegerField(default=0, help_text="무승부 횟수")
    lose_count = models.IntegerField(default=0, help_text="패배 횟수")

    class Meta:
        db_table = 'gym_wars_battle_record'
        verbose_name = '사용자 배틀 전적'
        verbose_name_plural = '사용자 배틀 전적 목록'

    def __str__(self):
        return f"{self.user.username}: {self.win_count}W {self.draw_count}D {self.lose_count}L"


# [수정일: 2026-03-04] Wars 미니게임 점수 기록 모델 (명예의 전당 연동용)
# - PracticeDetail 의존성 없이 Wars 전용 점수를 저장
# - game_type별 최고 점수를 합산하여 UserActivity.total_points에 반영
class UserWarsScore(BaseModel):
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='wars_scores',
        help_text="점수 소유자"
    )
    game_type = models.CharField(
        max_length=30,
        help_text="미니게임 종류 (logic_run, code_typing 등)"
    )
    score = models.IntegerField(default=0, help_text="획득 점수 (0-100)")
    submitted_data = models.JSONField(null=True, blank=True, help_text="게임 결과 상세 (난이도, 페이즈별 점수, 등급 등)")
    is_perfect = models.BooleanField(default=False, help_text="만점 여부")

    class Meta:
        db_table = 'gym_wars_score'
        verbose_name = 'Wars 게임 점수'
        verbose_name_plural = 'Wars 게임 점수 목록'

    def __str__(self):
        return f"{self.user.username}: {self.game_type} {self.score}pts"
