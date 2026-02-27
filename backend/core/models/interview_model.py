from django.db import models
from .base_model import BaseModel
from .user_model import UserProfile

class SavedJobPosting(BaseModel):
    """
    [Job Planner] 사용자가 관심 있는 채용공고를 저장하고 관리하는 모델.
    웹에서 스크래핑하거나 직접 입력한 채용공고의 상세 정보(요구 스킬, 자격 요건 등)를 파싱하여 저장합니다.
    이 데이터는 추후 모의면접(InterviewSession)의 기준 데이터로 활용됩니다.
    """
    # UserProfile과 1:N 관계. 한 명의 유저가 여러 채용공고를 저장
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='saved_job_postings')
    
    # 채용공고 기본 정보
    company_name = models.CharField(max_length=200, help_text="기업명")
    position = models.CharField(max_length=200, help_text="지원 직무/포지션")
    
    # 채용 상세 정보 (주로 텍스트 데이터)
    job_responsibilities = models.TextField(blank=True, default='', help_text="주요 업무 내용")
    required_qualifications = models.TextField(blank=True, default='', help_text="자격 요건 (텍스트)")
    preferred_qualifications = models.TextField(blank=True, default='', help_text="우대 사항 (텍스트)")
    
    # 구조화된 스킬 데이터 (검색 및 매칭을 위해 JSON 형태로 배열 저장)
    required_skills = models.JSONField(default=list, help_text="필수 기술 스택 목록 (JSON 배열)")
    preferred_skills = models.JSONField(default=list, help_text="우대 기술 스택 목록 (JSON 배열)")
    
    experience_range = models.CharField(max_length=50, blank=True, default='', help_text="요구 경력 (예: 신입, 1~3년)")
    deadline = models.CharField(max_length=50, null=True, blank=True, help_text="마감일")
    
    # 데이터 수집 출처
    source = models.CharField(max_length=20, help_text="데이터 출처 ('url', 'image', 'text')")
    source_url = models.URLField(max_length=500, blank=True, default='', help_text="원본 채용공고 URL")
    
    # 원본 데이터 및 추가 파싱 결과 보관
    raw_text = models.TextField(blank=True, default='', help_text="파싱 전 원본 텍스트 데이터")
    parsed_data = models.JSONField(default=dict, help_text="기타 파싱된 세부 정보 (JSON 구조)")

    class Meta:
        db_table = 'gym_saved_job_posting'
        ordering = ['-create_date']  # 최신 저장된 공고가 먼저 오도록 정렬
        # UniqueConstraint: 동일한 사용자가 동일한 URL의 공고를 중복해서 저장하는 것을 방지
        # 단, source_url이 비어있는 경우(예: 직접 텍스트 입력)는 중복 체크에서 제외(condition).
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
    """
    [Interview System] 사용자가 진행하는 단일 모의면접 세션을 관리하는 모델.
    상태 기반(State-driven)으로 면접의 흐름(진행 중, 완료 등)과 각 역량(Slot)별 
    증거 수집 현황을 추적합니다.
    """
    # 면접을 진행하는 사용자 (1:N)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='interview_sessions')
    
    # 면접의 기준이 되는 채용공고 (선택사항, 채용공고가 삭제되어도 면접 기록은 남도록 SET_NULL 처리)
    job_posting = models.ForeignKey(SavedJobPosting, on_delete=models.SET_NULL, null=True, related_name='interview_sessions')

    # 핵심 데이터: 역량 슬롯별 상태 및 증거 수집 현황
    # 면접자가 답변을 통해 필요한 역량 증거(예: 상황, 행동, 결과)를 얼마나 충족했는지 실시간으로 기록
    slot_states = models.JSONField(default=dict, help_text="""
    역량 슬롯별 증거 수집 현황 (예: collaboration, leadership 등)
    구조 예시:
    {
      "collaboration": {
        "status": "PARTIAL", // UNKNOWN, PARTIAL, CLEAR 등
        "evidence": {"role": true, "action": true, "result": false},
        "confirmed_required": ["role", "action"],
        "missing_required": ["result"],
        "attempt_count": 1,
        "required": ["role", "action", "result"]
      }
    }
    """)

    # 세션 시작 시 생성되는 전체 면접의 구조 및 계획 (질문할 슬롯 목록 등)
    interview_plan = models.JSONField(default=dict, help_text="초기 생성된 면접 계획 데이터")

    # 면접 진행 상태 관리
    status = models.CharField(max_length=20, default='in_progress', help_text="면접 상태: 'in_progress', 'completed', 'abandoned'")
    current_slot = models.CharField(max_length=50, default='', help_text="현재 진행 중인 역량 평가 슬롯")
    current_turn = models.IntegerField(default=0, help_text="현재 진행된 턴(질문/답변) 횟수")
    max_turns = models.IntegerField(default=20, help_text="해당 세션의 최대 허용 턴 수")

    # 대화 흐름 제어 플래그
    just_moved_slot = models.BooleanField(default=False, help_text="방금 다른 슬롯으로 넘어갔는지 여부 (자연스러운 브릿지 멘트 생성에 활용)")

    # 이전 질문 기록을 저장하여 동일한 의도의 질문이 반복되는 것을 방지
    question_history = models.JSONField(default=list, help_text="""
    이전 질문 기록 배열.
    예: [{"slot": "collaboration", "intent": "행동 회상 유도", "turn": 1}, ...]
    """)

    # 시간 기록 (BaseModel의 create_date와 별개로 면접 자체의 시작/종료 시간 기록)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'gym_interview_session'
        ordering = ['-started_at']  # 최신 면접이 먼저 오도록 정렬

    def __str__(self):
        return f"Session {self.pk} - {self.user.username} ({self.status})"

    def get_current_slot_plan(self):
        """현재 진행 중인 슬롯의 세부 계획(interview_plan 내 항목)을 반환하는 헬퍼 메서드"""
        slots = self.interview_plan.get('slots', [])
        for s in slots:
            if s.get('slot') == self.current_slot:
                return s
        return {}

    def get_slot_required(self, slot_name):
        """특정 슬롯에서 반드시 수집해야 하는 필수 증거(required evidence) 목록을 반환"""
        slot_state = self.slot_states.get(slot_name, {})
        return slot_state.get('required', [])


class InterviewTurn(BaseModel):
    """
    [Interview System] 면접 세션 내에서 발생하는 개별 턴(질문 1회 + 답변 1회)을 기록하는 모델.
    AI 시스템(Analyst, Engine, Planner, Coach)의 각 단계별 처리 결과가 턴마다 상세히 기록
    """
    # 턴이 속한 면접 세션 (1:N)
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='turns')
    turn_number = models.IntegerField(help_text="세션 내 턴의 순번")
    slot = models.CharField(max_length=50, help_text="이 턴에서 평가 중인 역량 슬롯")

    # 대화 내용
    question = models.TextField(help_text="면접관(AI)의 질문")
    answer = models.TextField(blank=True, default='', help_text="사용자(면접자)의 답변")

    # --- AI 파이프라인 처리 결과 기록 ---
    
    # 1. L1 Analyst: 사용자의 답변에서 어떤 증거가 발견되었는지 분석한 결과
    evidence_map = models.JSONField(default=dict, help_text="답변에서 추출된 증거 맵")

    # 2. L2 Engine: Analyst의 결과를 바탕으로 슬롯의 상태를 업데이트하고 다음 행동을 결정
    slot_status_before = models.CharField(max_length=20, default='UNKNOWN', help_text="답변 전 슬롯 상태")
    slot_status_after = models.CharField(max_length=20, default='UNKNOWN', help_text="답변 후 업데이트된 슬롯 상태")
    engine_action = models.CharField(max_length=30, default='', help_text="엔진의 다음 행동 결정: 'continue'(계속 질문), 'move_slot'(다음 역량으로 이동), 'finish'(면접 종료)")

    # 3. L3 Planner: Engine의 결정에 따라 다음에 어떤 의도로 질문을 생성할지 계획
    intent = models.CharField(max_length=100, default='', help_text="다음 질문의 의도 (예: 누락된 '결과' 증거 요구)")

    class Meta:
        db_table = 'gym_interview_turn'
        ordering = ['turn_number']  # 턴 순서대로 정렬

    def __str__(self):
        return f"Turn {self.turn_number} - Session {self.session_id} - {self.slot}"


class InterviewFeedback(BaseModel):
    """
    [Interview System] 면접이 모두 종료된 후 생성되는 종합 피드백 모델.
    단순한 점수가 아닌, 턴 단위로 수집된 증거를 바탕으로 정성적인 평가와 개선점을 제공합니다.
    """
    # 하나의 면접 세션당 하나의 피드백만 존재 (1:1)
    session = models.OneToOneField(InterviewSession, on_delete=models.CASCADE, related_name='feedback')

    # 각 역량 슬롯별 최종 달성 상태 및 요약
    slot_summary = models.JSONField(default=dict, help_text="""
    역량 슬롯별 최종 상태 요약
    구조 예시:
    {
      "collaboration": {
        "final_status": "CLEAR",
        "confirmed_evidence": ["role", "action", "result"],
        "missing_evidence": ["reflection"],
        "summary": "협업 과정에서의 역할과 결과가 명확히 제시됨..."
      }
    }
    """)

    # 전체 면접에 대한 종합적인 피드백
    overall_summary = models.TextField(help_text="전체 면접 총평")
    
    # 강점과 개선점 리스트
    top_strengths = models.JSONField(default=list, help_text="주요 강점 목록 (JSON 배열)")
    top_improvements = models.JSONField(default=list, help_text="주요 개선점 목록 (JSON 배열)")
    
    recommendation = models.TextField(blank=True, default='', help_text="향후 면접 준비를 위한 조언/추천 사항")
    
    # 영상/표정/자세 분석 등 비전 AI 시스템의 추가 분석 결과 보관용 (선택)
    vision_analysis = models.JSONField(null=True, blank=True, default=None, help_text="비전 분석 데이터 (표정, 시선 처리 등)")

    class Meta:
        db_table = 'gym_interview_feedback'

    def __str__(self):
        return f"Feedback for Session {self.session_id}"


# ==========================================================
# 전체 데이터 관계 요약 (ERD 구조 요약)
# ==========================================================
# UserProfile (사용자)
# └── SavedJobPosting (사용자가 스크랩/저장한 채용공고)  [1:N]
#         └── InterviewSession (특정 채용공고를 바탕으로 진행하는 모의면접 세션)  [1:N]
#                 ├── InterviewTurn × N (면접 중 발생하는 매 턴의 질문, 답변, AI 분석 기록)  [1:N]
#                 └── InterviewFeedback × 1 (면접 종료 후 분석된 최종 종합 피드백)  [1:1]
# ==========================================================