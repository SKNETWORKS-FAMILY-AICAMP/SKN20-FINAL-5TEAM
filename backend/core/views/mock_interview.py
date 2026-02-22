"""
작성일: 2026-02-21
수정일: 2026-02-22
수정자: 수석 에이전트
작성내용: 
- AI-GYM 프로젝트의 모의 면접 시스템 백엔드 API
- [수정내용] Multi-Agent 아키텍처 도입 (Analyst + Interviewer)
- 1단계: Analyst가 유저 데이터(Job Planner + Code + History)를 분석해 공격 벡터(Attack Vector) 도출
- 2단계: Interviewer(도덕)가 공격 벡터를 바탕으로 스트리밍 꼬리 질문 생성
"""
import time
import json
import os
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from django.conf import settings

from core.models.user_model import UserProfile
from core.models.activity_model import UserSolvedProblem

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ==========================================
# 1. Analyst Agent (분석가 페르소나)
# ==========================================
def run_analyst_agent(request, job_planner_data=None, user_msg=None, history=None):
    """
    유저 눈에 보이지 않는 백그라운드 AI (Analyst)
    유저의 과거 코드 이력, 지원 회사 정보, 현재 대화 맥락을 분석하여
    '도덕(면접관)'이 공격해야 할 단 1개의 핵심 약점(Attack Vector)을 추출합니다.
    """
    context_str = ""
    job_str = ""

    # 1) 지원 회사 정보 추출
    if job_planner_data:
        job_data = job_planner_data.get('jobData', {})
        if job_data:
            company_name = job_data.get('company_name', '특정 회사')
            position_name = job_data.get('position', '특정 직무')
            req_skills = job_data.get('required_skills', [])
            skills_str = ', '.join(req_skills) if req_skills else '관련 기술'
            
            job_str = f"[지원 회사: {company_name}] | [포지션: {position_name}] | [요구 기술: {skills_str}]\n"

    # 2) 과거 코드 이력 추출
    user = request.user if request.user.is_authenticated else None
    if user:
        try:
            recent_solved = UserSolvedProblem.objects.filter(
                user=user
            ).select_related('practice_detail', 'practice_detail__practice').order_by('-solved_date')[:5]
            
            if recent_solved.exists():
                for sp in recent_solved:
                    unit_name = sp.practice_detail.practice.title if sp.practice_detail and sp.practice_detail.practice else "미상"
                    score = sp.score
                    code_snippet = ""
                    if sp.submitted_data and isinstance(sp.submitted_data, dict):
                        code_snippet = str(sp.submitted_data.get('code', ''))[:200]
                    context_str += f"- 유닛: {unit_name}, 점수: {score}점, 코드 요약: {code_snippet}...\n"
        except Exception as e:
            print(f"Failed to fetch user context for Analyst: {e}")
            pass

    # 3) 히스토리 요약
    history_str = ""
    if history:
        # 최근 3~4개의 대화만 분석에 활용
        recent_history = history[-4:]
        for h in recent_history:
            role = '면접관' if h['role'] == 'assistant' else '지원자'
            history_str += f"{role}: {h['content']}\n"
    if user_msg:
        history_str += f"지원자(현재답변): {user_msg}\n"

    analyst_prompt = f"""당신은 AI-GYM의 심층 면접 분석가(Analyst)입니다.
당신의 임무는 아래 제공된 데이터들을 분석하여, 최종 면접관(도덕)이 지원자에게 던져야 할 **단 1개의 가장 날카롭고 예리한 질문 방향(Attack Vector)**을 설계하는 것입니다.

[데이터]
1. 지원 회사 정보: {job_str if job_str else "없음 (일반 CS 면접으로 진행)"}
2. 지원자의 과거 코드(Python) 이력:
{context_str if context_str else "과거 코드 정보 없음"}
3. 최근 면접 대화 흐름:
{history_str if history_str else "면접 시작 전입니다."}

[분석 규칙]
1. 단순한 지식 확인을 넘어서, '지원 회사의 요구 기술'과 '지원자의 코드 약점' 또는 '현재 답변의 허점'을 교묘하게 엮으세요.
2. 예시: 회사가 프론트엔드(React)를 요구하는데 지원자 코드가 파이썬 기초인 경우 -> 파이썬을 억지로 묻지 말고, "과거 코드에서 상태 관리가 미흡했는데, 이를 프론트엔드의 React 컴포넌트 환경에서는 어떻게 안정적으로 설계할 건가?" 식으로 치환해서 공격하세요.
3. 지원자가 오답을 냈거나 대답이 빈약하면 집요하게 파고드는 방향을 제시하세요.
4. 예의를 차릴 필요 없습니다. 오직 날카로운 단 1개의 공격 포인트만 서술하세요.
5. 반드시 JSON 포맷으로 "attack_vector" 키 하나만 포함하여 반환하세요.

출력 예시:
{{
  "attack_vector": "지원자는 직전 답변에서 예외 처리를 두루뭉술하게 얼버무렸음. 과거 파이썬 코드에서도 예외 처리가 전혀 안 되어 있었음을 지적하고, 지원하는 A회사의 대규모 트래픽 환경에서 에러 헨들링이 누락되었을 때의 치명적인 사이드 이펙트를 묻는 압박 질문을 던지시오."
}}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": analyst_prompt}],
            response_format={ "type": "json_object" },
            temperature=0.7,
        )
        result = json.loads(response.choices[0].message.content)
        attack_vector = result.get("attack_vector", "지원자의 이력과 답변을 바탕으로 핵심 기술 질문을 1개 던지세요.")
        print(f"\n🕵️ [Analyst] 추출된 공격 벡터:\n{attack_vector}\n")
        return attack_vector
    except Exception as e:
        print(f"Analyst Error: {e}")
        return "지원자의 대답을 바탕으로 꼬리 질문을 던지세요."


# ==========================================
# 2. Interviewer Agent (면접관 페르소나 - 스트리밍)
# ==========================================
def get_interviewer_prompt(attack_vector):
    """
    최종 면접관 '도덕'의 깐깐한 시스템 프롬프트.
    Analyst가 넘겨준 지령(attack_vector)만 수행합니다.
    """
    return f"""당신은 픽사 감성의 오리 캐릭터이자 AI-GYM의 수석 기술 면접관 '도덕(Coduck)'입니다.
진중하고 프로페셔널한 태도를 유지하는 시니어 멘토입니다.

[당신의 절대 규칙]
1. 한 번에 **단 한 개의 질문**만 던지세요. 서론이나 칭찬은 아주 짧게, 혹은 생략하세요.
2. 기계적인 AI 말투나 이모지 남발은 금지합니다. 단, 말투 끝에 약간의 오리 캐릭터성(깐깐함)이 묻어나도 좋습니다.
3. 마크다운을 적절히 활용하여 핵심 기술명이나 변수명은 강조하세요.

[이번 턴의 핵심 지령 (Attack Vector)]
백그라운드 분석가가 당신에게 다음 방향으로 질문할 것을 지시했습니다:
"{attack_vector}"

이 지령을 완벽하게 숙지하고, 지원자에게 날카롭고 직관적인 질문을 스트리밍으로 뱉으세요.
"""

@csrf_exempt
def mock_interview_stream(request):
    """
    모의 면접 첫 진입 시 호출되는 SSE 스트리밍 (첫 인사 + 첫 질문)
    """
    job_planner_data = None
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            job_planner_data = body.get("job_planner")
        except json.JSONDecodeError:
            pass

    def event_stream():
        try:
            # 1단계: Analyst 가동 (공격 벡터 추출)
            attack_vector = run_analyst_agent(request, job_planner_data, user_msg=None, history=None)
            
            # 2단계: Interviewer 가동 (스트리밍 응답)
            system_prompt = get_interviewer_prompt(attack_vector)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "지원자가 면접에 방금 입장했습니다. 과장된 인사는 생략하고 실제 면접관처럼 첫 인사를 건넨 뒤, 주어진 지령(Attack Vector)에 따라 첫 질문을 가볍게 던져주세요."}
                ],
                stream=True,
                temperature=0.7,
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    time.sleep(0.02)
                    char = chunk.choices[0].delta.content
                    chunk_data = json.dumps({"chunk": char, "status": "typing"}, ensure_ascii=False)
                    yield f"data: {chunk_data}\n\n"
                    
            done_data = json.dumps({"chunk": "", "status": "done"}, ensure_ascii=False)
            yield f"data: {done_data}\n\n"
            
        except Exception as e:
            error_msg = json.dumps({"chunk": f"오류 발생 꽥! ({str(e)})", "status": "done"}, ensure_ascii=False)
            yield f"data: {error_msg}\n\n"

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response

@csrf_exempt
def mock_interview_reply(request):
    """
    유저가 채팅(답변) 입력 시 호출되어 SSE로 꼬리 질문을 생성하는 엔드포인트
    """
    history = []
    user_msg = ""
    job_planner_data = None
    
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            history = body.get("history", [])
            job_planner_data = body.get("job_planner")
            if history and history[-1].get("role") == "user":
                user_msg = history[-1].get("content")
        except json.JSONDecodeError:
            pass
    else:
        user_msg = request.GET.get('msg', '')
        if user_msg:
            history.append({"role": "user", "content": user_msg})
    
    def event_stream():
        if not user_msg and not history:
            yield f"data: {json.dumps({'chunk': '말씀하신 내용을 잘 듣지 못했어요 꽥!', 'status': 'done'}, ensure_ascii=False)}\n\n"
            return
            
        try:
            # 1단계: Analyst 가동 (유저 답변 기반으로 새로운 공격 벡터 추출)
            attack_vector = run_analyst_agent(request, job_planner_data, user_msg=user_msg, history=history)
            
            # 2단계: Interviewer 가동 (공격 벡터에 기반한 스트리밍 꼬리 질문 생성)
            system_prompt = get_interviewer_prompt(attack_vector)
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True,
                temperature=0.7,
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    time.sleep(0.02)
                    char = chunk.choices[0].delta.content
                    chunk_data = json.dumps({"chunk": char, "status": "typing"}, ensure_ascii=False)
                    yield f"data: {chunk_data}\n\n"
                    
            done_data = json.dumps({"chunk": "", "status": "done"}, ensure_ascii=False)
            yield f"data: {done_data}\n\n"
            
        except Exception as e:
            error_msg = json.dumps({"chunk": f"오류 발생 꽥! ({str(e)})", "status": "done"}, ensure_ascii=False)
            yield f"data: {error_msg}\n\n"

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response
