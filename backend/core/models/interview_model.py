from django.db import models
from .base_model import BaseModel
from .user_model import UserProfile


class SavedJobPosting(BaseModel):
    """Job Planner에서 파싱된 채용공고 저장"""
    # UserProfile과 ForeignKey로 연결 (한 유저가 여러 공고 저장 가능)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='saved_job_postings')
    company_name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    job_responsibilities = models.TextField(blank=True, default='')
    required_qualifications = models.TextField(blank=True, default='')
    preferred_qualifications = models.TextField(blank=True, default='')
    required_skills = models.JSONField(default=list)
    preferred_skills = models.JSONField(default=list)
    experience_range = models.CharField(max_length=50, blank=True, default='')
    deadline = models.CharField(max_length=50, null=True, blank=True)
    source = models.CharField(max_length=20)  # 'url', 'image', 'text'
    source_url = models.URLField(max_length=500, blank=True, default='')
    raw_text = models.TextField(blank=True, default='')
    parsed_data = models.JSONField(default=dict)

    class Meta:
        db_table = 'gym_saved_job_posting'
        ordering = ['-create_date']
        # UniqueConstraint: 동일 유저가 source_url이 있는 공고를 중복 저장하지 못하도록
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'source_url'],
                condition=~models.Q(source_url=''),
                name='unique_user_source_url'
            )
        ]

    def __str__(self):
        return f"{self.company_name} - {self.position} ({self.user.username})"


class InterviewSession(BaseModel):
    """모의면접 세션"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='interview_sessions')
    # SavedJobPosting과 ForeignKey로 연결 (한 공고에 여러 세션 가능, 세션은 하나의 공고에만 연결)
    job_posting = models.ForeignKey(SavedJobPosting, on_delete=models.SET_NULL, null=True, related_name='interview_sessions')

    # 역량 슬롯 상태 (증거 기반)
    slot_states = models.JSONField(default=dict)
    # slot_states: 역량 슬롯별 증거 수집 현황 (collaboration, leadership 등)
    # {
    #   "collaboration": {
    #     "status": "PARTIAL",
    #     "evidence": {"role": true, "action": true, "result": false},
    #     "confirmed_required": ["role", "action"],
    #     "missing_required": ["result"],
    #     "attempt_count": 1,
    #     "required": ["role", "action", "result"]
    #   }
    # }

    # 면접 계획 (세션 시작 시 생성)
    interview_plan = models.JSONField(default=dict)

    # 상태 관리
    status = models.CharField(max_length=20, default='in_progress')
    # 'in_progress', 'completed', 'abandoned'
    current_slot = models.CharField(max_length=50, default='')
    current_turn = models.IntegerField(default=0)
    max_turns = models.IntegerField(default=20)

    # 슬롯 이동 여부 (Humanizer가 브릿지 생성에 사용)
    just_moved_slot = models.BooleanField(default=False)

    # 이전 질문 기록 (Planner 반복 방지에 사용)
    question_history = models.JSONField(default=list)
    # [{"slot": "collaboration", "intent": "행동 회상 유도", "turn": 1}, ...]

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'gym_interview_session'
        ordering = ['-started_at']

    def __str__(self):
        return f"Session {self.pk} - {self.user.username} ({self.status})"

    def get_current_slot_plan(self):
        """현재 슬롯의 interview_plan 항목 반환"""
        slots = self.interview_plan.get('slots', [])
        for s in slots:
            if s.get('slot') == self.current_slot:
                return s
        return {}

    def get_slot_required(self, slot_name):
        """슬롯의 required evidence 목록 반환 (plan 우선, 없으면 slot_states에서)"""
        slot_state = self.slot_states.get(slot_name, {})
        return slot_state.get('required', [])


class InterviewTurn(BaseModel):
    """면접 매 턴 기록"""
    # InterviewSession과 ForeignKey로 연결 (한 세션에 여러 턴, 턴은 하나의 세션에만 연결)
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='turns')
    turn_number = models.IntegerField()
    slot = models.CharField(max_length=50)

    question = models.TextField()
    answer = models.TextField(blank=True, default='')

    # L1 Analyst 출력
    evidence_map = models.JSONField(default=dict)

    # L2 Engine 결정
    slot_status_before = models.CharField(max_length=20, default='UNKNOWN')
    slot_status_after = models.CharField(max_length=20, default='UNKNOWN')
    engine_action = models.CharField(max_length=30, default='')
    # 'continue', 'move_slot', 'finish'

    # L3 Planner 출력
    intent = models.CharField(max_length=100, default='')

    # Coach 피드백 (LLM 없음 — evidence map 기반 구조적 메시지)
    coach_feedback = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'gym_interview_turn'
        ordering = ['turn_number']

    def __str__(self):
        return f"Turn {self.turn_number} - Session {self.session_id} - {self.slot}"


class InterviewFeedback(BaseModel):
    """면접 종료 후 최종 피드백 (점수 없음, 증거 기반 정성적 피드백)"""
    session = models.OneToOneField(InterviewSession, on_delete=models.CASCADE, related_name='feedback')

    # 역량 슬롯별 최종 상태 요약
    slot_summary = models.JSONField(default=dict)
    # {
    #   "collaboration": {
    #     "final_status": "CLEAR",
    #     "confirmed_evidence": ["role", "action", "result"],
    #     "missing_evidence": ["reflection"],
    #     "summary": "..."
    #   }
    # }

    overall_summary = models.TextField()
    top_strengths = models.JSONField(default=list)
    top_improvements = models.JSONField(default=list)
    recommendation = models.TextField(blank=True, default='')
    vision_analysis = models.JSONField(null=True, blank=True, default=None)

    class Meta:
        db_table = 'gym_interview_feedback'

    def __str__(self):
        return f"Feedback for Session {self.session_id}"
    

# 전체 관계 요약
    # UserProfile
    # └── SavedJobPosting (채용공고)
    #         └── InterviewSession (면접 세션)
    #                 ├── InterviewTurn × N (매 턴)
    #                 └── InterviewFeedback × 1 (최종 피드백)
