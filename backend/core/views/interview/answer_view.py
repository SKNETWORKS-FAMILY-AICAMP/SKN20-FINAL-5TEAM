"""
answer_view.py — 모의면접 답변 처리 + SSE 스트리밍
POST /api/core/interview/sessions/<pk>/answer/

한 턴 처리 흐름:
1. L1 Analyst → evidence_map
2. L2 Engine → update_slot + decide_action
3. if finish → feedback_generator → SSE final_feedback → [DONE]
4. if move_slot → 다음 슬롯 이동
9. SSE meta
10. [DONE]
11. InterviewTurn DB 저장
"""
import json
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from core.models import UserProfile, InterviewSession, InterviewTurn, InterviewFeedback
from core.services.interview.analyst import extract_evidence
from core.services.interview.state_engine import StateEngine
from core.services.interview.planner import decide_intent
from core.services.interview.humanizer import build_context
from core.services.interview.interviewer import generate_question
from core.services.interview.feedback_generator import generate_feedback

engine = StateEngine()


def _get_user(request):
    """세션에서 UserProfile을 가져온다. 없으면 None."""
    user_id = request.session.get('user_id') or request.session.get('_auth_user_id')
    if not user_id:
        return None
    try:
        return UserProfile.objects.get(pk=user_id)
    except UserProfile.DoesNotExist:
        return None


def _sse(payload: dict) -> str:
    return f'data: {json.dumps(payload, ensure_ascii=False)}\n\n'


def _stream_answer(session, answer: str, old_turn: InterviewTurn):
    """
    한 턴 처리 + SSE 스트리밍 제너레이터.
    DB 저장은 [DONE] 이후에 수행.
    """
    current_slot = session.current_slot
    slot_states = session.slot_states

    # ── Phase 1: 분석 (비스트리밍) ──────────────────────────
    # 현재 슬롯의 모든 evidence 키
    current_slot_state = slot_states.get(current_slot, {})
    all_evidence_keys = list(current_slot_state.get('evidence', {}).keys())
    required = session.get_slot_required(current_slot)

    slot_status_before = current_slot_state.get('status', 'UNKNOWN')

    # L1 Analyst: 답변에서 evidence 추출
    evidence_map = extract_evidence(answer, all_evidence_keys)

    # 기존 evidence와 병합 (True는 유지, False는 덮어쓰기 안 함)
    existing_evidence = current_slot_state.get('evidence', {})
    merged_evidence = {k: existing_evidence.get(k, False) or evidence_map.get(k, False)
                       for k in set(existing_evidence) | set(evidence_map)}

    # 새 required evidence 증가 여부 감지
    existing_confirmed_count = sum(1 for k in required if existing_evidence.get(k))
    new_confirmed_count = sum(1 for k in required if merged_evidence.get(k))
    no_gain = (new_confirmed_count <= existing_confirmed_count)
    prev_no_gain = current_slot_state.get('consecutive_no_gain', 0)
    consecutive_no_gain = prev_no_gain + 1 if no_gain else 0

    # slot_states 업데이트
    slot_states[current_slot]['evidence'] = merged_evidence
    slot_states[current_slot]['attempt_count'] = current_slot_state.get('attempt_count', 0) + 1
    slot_states[current_slot]['consecutive_no_gain'] = consecutive_no_gain

    # L2 Engine: 슬롯 상태 갱신
    update_result = engine.update_slot(current_slot, merged_evidence, required)
    slot_states[current_slot]['status'] = update_result['status']
    slot_states[current_slot]['confirmed_required'] = update_result['confirmed_required']
    slot_states[current_slot]['missing_required'] = update_result['missing_required']
    session.slot_states = slot_states

    slot_status_after = update_result['status']

    # L2 Engine: 행동 결정
    action = engine.decide_action(session)

    # ── Phase 2: FINISH 처리 ─────────────────────────────────
    if action == 'finish':
        # 현재 슬롯 uncertain 처리 (CLEAR가 아닌 경우)
        if slot_status_after != 'CLEAR':
            engine.mark_uncertain(session, current_slot)

        # 세션 완료 처리
        session.status = 'completed'
        session.finished_at = timezone.now()
        session.save()

        # 이전 턴(old_turn) 완성
        old_turn.answer = answer
        old_turn.evidence_map = evidence_map
        old_turn.slot_status_before = slot_status_before
        old_turn.slot_status_after = slot_status_after
        old_turn.engine_action = 'finish'
        old_turn.save()

        # 최종 피드백 생성
        try:
            feedback_data = generate_feedback(session)
            InterviewFeedback.objects.create(
                session=session,
                slot_summary=feedback_data.get('slot_summary', {}),
                overall_summary=feedback_data.get('overall_summary', '면접이 완료됐습니다.'),
                top_strengths=feedback_data.get('top_strengths', []),
                top_improvements=feedback_data.get('top_improvements', []),
                recommendation=feedback_data.get('recommendation', ''),
            )
            yield _sse({'type': 'final_feedback', **feedback_data})
        except Exception as e:
            print(f'[AnswerView] 피드백 생성 오류: {e}')
            yield _sse({'type': 'final_feedback', 'overall_summary': '면접이 완료됐습니다.', 'error': True})

        yield 'data: [DONE]\n\n'
        return

    # ── Phase 3: MOVE_SLOT 처리 ──────────────────────────────
    if action == 'move_slot':
        if slot_status_after != 'CLEAR':
            engine.mark_uncertain(session, current_slot)
        next_slot = engine.move_to_next_slot(session)
        if not next_slot:
            # 이동할 슬롯 없음 → finish로 재처리
            session.status = 'completed'
            session.finished_at = timezone.now()
            session.save()

            old_turn.answer = answer
            old_turn.evidence_map = evidence_map
            old_turn.slot_status_before = slot_status_before
            old_turn.slot_status_after = slot_status_after
            old_turn.engine_action = 'finish'
            old_turn.save()

            try:
                feedback_data = generate_feedback(session)
                InterviewFeedback.objects.create(
                    session=session,
                    slot_summary=feedback_data.get('slot_summary', {}),
                    overall_summary=feedback_data.get('overall_summary', '면접이 완료됐습니다.'),
                    top_strengths=feedback_data.get('top_strengths', []),
                    top_improvements=feedback_data.get('top_improvements', []),
                    recommendation=feedback_data.get('recommendation', ''),
                )
                yield _sse({'type': 'final_feedback', **feedback_data})
            except Exception as e:
                print(f'[AnswerView] 피드백 생성 오류: {e}')
                yield _sse({'type': 'final_feedback', 'overall_summary': '면접이 완료됐습니다.', 'error': True})
            yield 'data: [DONE]\n\n'
            return

        session.current_slot = next_slot
        session.just_moved_slot = True
    else:
        # continue
        session.just_moved_slot = False

    # ── Phase 4: 다음 질문 생성 (L3 → L5 → L4 stream) ──────
    new_slot = session.current_slot
    new_slot_states = session.slot_states
    missing_required = new_slot_states.get(new_slot, {}).get('missing_required', [])

    intent_data = decide_intent(missing_required, session.question_history)
    intent = intent_data['intent']

    plan_slot = session.get_current_slot_plan()
    ctx = build_context(session, plan_slot)

    # 대화 히스토리 조립 (answer가 있는 턴만, 최근 4턴)
    past_turns = session.turns.exclude(answer='').order_by('turn_number').values('question', 'answer')
    conversation_history = [{"q": t['question'], "a": t['answer']} for t in past_turns][-4:]

    # ── Phase 5: L4 Interviewer SSE 스트리밍 ────────────────
    full_question = ''
    for token in generate_question(intent, ctx, previous_answer=answer, conversation_history=conversation_history):
        full_question += token
        yield _sse({'type': 'question', 'token': token})

    # ── Phase 6: Meta SSE 전송 ───────────────────────────────
    new_turn_number = session.current_turn + 1

    slot_plan_slots = session.interview_plan.get('slots', [])
    total_slots = len(slot_plan_slots)
    clear_count = sum(
        1 for s in session.slot_states.values()
        if s.get('status') == 'CLEAR'
    )

    yield _sse({
        'type': 'meta',
        'turn': new_turn_number,
        'slot': new_slot,
        'topic': plan_slot.get('topic', new_slot),
        'slot_status': new_slot_states.get(new_slot, {}).get('status', 'UNKNOWN'),
        'slots_cleared': clear_count,
        'total_slots': total_slots,
        'engine_action': action,
    })
    yield 'data: [DONE]\n\n'

    # ── Phase 7: DB 저장 (스트리밍 완료 후) ─────────────────
    old_turn.answer = answer
    old_turn.evidence_map = evidence_map
    old_turn.slot_status_before = slot_status_before
    old_turn.slot_status_after = slot_status_after
    old_turn.engine_action = action
    old_turn.intent = intent
    old_turn.save()

    # session 업데이트
    session.current_turn = new_turn_number
    history_entry = {'slot': new_slot, 'intent': intent, 'turn': new_turn_number}
    session.question_history = list(session.question_history) + [history_entry]
    session.save()

    # 새 InterviewTurn 생성 (다음 질문, answer는 빈 문자열)
    InterviewTurn.objects.create(
        session=session,
        turn_number=new_turn_number,
        slot=new_slot,
        question=full_question,
        answer='',
        evidence_map={},
        slot_status_before=new_slot_states.get(new_slot, {}).get('status', 'UNKNOWN'),
        slot_status_after='UNKNOWN',
        engine_action='',
        intent=intent,
    )


@method_decorator(csrf_exempt, name='dispatch')
class InterviewAnswerView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, pk):
        """답변 제출 + SSE 스트리밍으로 다음 질문 반환"""
        user = _get_user(request)
        if not user:
            return Response({'error': '로그인이 필요합니다.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            session = InterviewSession.objects.select_related('job_posting').get(
                pk=pk, user=user, status='in_progress'
            )
        except InterviewSession.DoesNotExist:
            return Response(
                {'error': '진행 중인 세션을 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )

        answer = (request.data.get('answer') or '').strip()
        if not answer:
            return Response({'error': '답변을 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        # 현재 턴의 InterviewTurn (아직 answer가 없는 turn)
        old_turn = session.turns.filter(answer='').order_by('-turn_number').first()
        if not old_turn:
            return Response(
                {'error': '현재 처리할 턴을 찾을 수 없습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        response = StreamingHttpResponse(
            _stream_answer(session, answer, old_turn),
            content_type='text/event-stream',
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response
