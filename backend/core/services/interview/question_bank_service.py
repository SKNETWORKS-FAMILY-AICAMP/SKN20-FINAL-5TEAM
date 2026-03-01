"""
question_bank_service.py -- 면접 질문 뱅크 검색 서비스

생성일: 2026-03-01
설명: InterviewQuestion DB(13,169건)에서 기업/직무/슬롯별 질문을 검색하여
      plan_generator(면접 계획 수립)와 interviewer(면접 진행)에 주입하는 서비스 모듈.

사용처:
  1. plan_generator.py  -- generate_plan() 호출 시 기출 질문을 프롬프트에 주입
  2. session_view.py    -- 세션 생성 시 슬롯별 질문 묶음(bank_questions)을 interview_plan에 저장
  3. interviewer.py     -- L4 Interviewer 시스템 프롬프트에 현재 슬롯의 기출 질문 주입
  4. question_bank_view.py -- 질문 검색 REST API 엔드포인트

주요 함수:
  - search_questions()          : 범용 질문 검색 (API 및 내부 공통)
  - get_questions_for_session() : 세션 시작 시 슬롯별 질문 묶음 반환
  - get_questions_for_plan()    : 면접 계획 생성용 기출 질문 요약 반환
  - map_slot_to_type()          : interview_plan 슬롯명 → DB slot_type 매핑
"""
from django.db.models import Q, Case, When, IntegerField

from core.models import InterviewQuestion


# ============================================================================
# 유틸리티
# ============================================================================

def map_slot_to_type(slot_name: str) -> str:
    """interview_plan의 slot명을 InterviewQuestion.slot_type으로 매핑한다.

    plan_generator가 생성하는 슬롯명(예: technical_depth, technical_depth_2)을
    DB의 slot_type 값(technical)으로 변환한다.
    motivation, collaboration, problem_solving, growth는 그대로 반환.

    Args:
        slot_name: interview_plan에서의 슬롯명
                   예: "technical_depth", "motivation", "collaboration"

    Returns:
        DB slot_type 문자열
        예: "technical", "motivation", "collaboration"
    """
    if slot_name.startswith("technical"):
        return "technical"
    return slot_name


# ============================================================================
# 질문 검색 (공통)
# ============================================================================

def search_questions(slot_type=None, company="", job="", limit=10) -> list:
    """조건에 맞는 면접 질문을 DB에서 검색한다.

    검색 우선순위:
      1) company가 지정되면 해당 기업 질문 우선 → 부족하면 범용(company='') 질문으로 보충
      2) job이 지정되면 직무명 부분 매치(icontains) 또는 범용(job='') 질문 포함
      3) 랜덤 셔플(order_by('?'))로 같은 조건이라도 매번 다른 질문 제공

    DB 인덱스 활용:
      - idx_company_slot_job (company, slot_type, job) 복합 인덱스

    Args:
        slot_type: InterviewQuestion.SlotType 값
                   (technical, motivation, collaboration, problem_solving, growth, general)
                   None이면 전체 슬롯 대상
        company: 기업명 (정확 매치 우선). 빈 문자열이면 기업 필터 없음.
        job: 직무명 (부분 매치). 빈 문자열이면 직무 필터 없음.
        limit: 최대 반환 개수 (기본 10)

    Returns:
        질문 dict 리스트:
        [
            {
                "id": int,              # DB PK
                "question_text": str,   # 질문 텍스트
                "slot_type": str,       # 슬롯 유형
                "company": str,         # 기업명 (빈 문자열이면 범용)
                "job": str,             # 직무
                "source": str,          # 데이터 소스 (aihub_ict, jobkorea, github, youtube)
                "answer_summary": str,  # 답변 요약 (AI Hub 데이터만 존재)
            },
            ...
        ]
    """
    qs = InterviewQuestion.objects.all()

    # 슬롯 필터
    if slot_type:
        qs = qs.filter(slot_type=slot_type)

    # 기업 필터: 해당 기업 질문 우선순위 0, 범용 질문 우선순위 1
    if company:
        qs = qs.filter(Q(company=company) | Q(company=''))
        qs = qs.annotate(
            company_priority=Case(
                When(company=company, then=0),
                default=1,
                output_field=IntegerField(),
            )
        ).order_by('company_priority', '?')
    else:
        qs = qs.order_by('?')

    # 직무 필터: 부분 매치 또는 범용
    if job:
        qs = qs.filter(Q(job__icontains=job) | Q(job=''))

    results = qs[:limit]

    return [
        {
            "id": q.id,
            "question_text": q.question_text,
            "slot_type": q.slot_type,
            "company": q.company,
            "job": q.job,
            "source": q.source,
            "answer_summary": q.answer_summary or "",
        }
        for q in results
    ]


# ============================================================================
# 세션용 질문 묶음
# ============================================================================

def get_questions_for_session(company="", job="", slot_types=None) -> dict:
    """세션 시작 시 슬롯별로 질문 묶음을 가져온다.

    session_view.py의 세션 생성(POST) 시 호출.
    반환된 dict는 interview_plan["bank_questions"]에 저장되어
    면접 진행 중 humanizer → interviewer로 전달된다.

    Args:
        company: 기업명 (SavedJobPosting.company_name)
        job: 직무명 (SavedJobPosting.position)
        slot_types: interview_plan의 슬롯 이름 리스트
                    예: ["motivation", "technical_depth", "collaboration", "growth"]

    Returns:
        슬롯별 질문 묶음 dict:
        {
            "motivation": [{"id", "question_text", "slot_type", ...}, ...],
            "technical":  [{"id", "question_text", "slot_type", ...}, ...],
            "collaboration": [...],
            ...
        }
        각 슬롯당 최대 5개 질문.
        technical_depth, technical_depth_2 등은 모두 "technical" 키로 통합.
    """
    if not slot_types:
        return {}

    result = {}
    seen_ids = set()  # 슬롯 간 질문 중복 방지

    for slot_name in slot_types:
        db_type = map_slot_to_type(slot_name)

        # 이미 같은 DB 타입으로 가져온 적 있으면 스킵
        # (technical_depth와 technical_depth_2가 모두 "technical"이므로)
        if db_type in result:
            continue

        questions = search_questions(
            slot_type=db_type,
            company=company,
            job=job,
            limit=5,
        )

        # 중복 질문 제거
        unique = []
        for q in questions:
            if q["id"] not in seen_ids:
                seen_ids.add(q["id"])
                unique.append(q)

        result[db_type] = unique

    return result


# ============================================================================
# 면접 계획 생성용
# ============================================================================

def get_questions_for_plan(company="", job="") -> list:
    """면접 계획 생성(plan_generator) 프롬프트에 주입할 기출 질문을 반환한다.

    plan_generator.py의 _build_plan_prompt()에서 호출.
    LLM이 허구의 토픽을 만들지 않고 실제 면접 데이터를 참고하여
    슬롯 구성과 토픽을 결정하도록 한다.

    Args:
        company: 기업명
        job: 직무명

    Returns:
        질문 요약 리스트 (최대 20개, 슬롯별 고르게 분배):
        [
            {"slot_type": "technical", "question_text": "...", "source": "jobkorea"},
            {"slot_type": "motivation", "question_text": "...", "source": "aihub_ict"},
            ...
        ]
    """
    qs = InterviewQuestion.objects.all()

    # 기업 매치 우선
    if company:
        qs = qs.filter(Q(company=company) | Q(company=''))
        qs = qs.annotate(
            company_priority=Case(
                When(company=company, then=0),
                default=1,
                output_field=IntegerField(),
            )
        ).order_by('company_priority', '?')
    else:
        qs = qs.order_by('?')

    # 직무 매치
    if job:
        qs = qs.filter(Q(job__icontains=job) | Q(job=''))

    # 슬롯별로 고르게 가져오기 (각 슬롯 최대 4개, 총 20개 이내)
    slot_types = ['technical', 'motivation', 'collaboration', 'problem_solving', 'growth', 'general']
    result = []
    for st in slot_types:
        slot_qs = qs.filter(slot_type=st)[:4]
        for q in slot_qs:
            result.append({
                "slot_type": q.slot_type,
                "question_text": q.question_text,
                "source": q.source,
            })

    return result[:20]
