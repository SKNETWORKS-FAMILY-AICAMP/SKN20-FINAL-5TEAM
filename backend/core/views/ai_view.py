# [수정일: 2026-02-04] pseudo_tts 브런치를 main 브런치로 머지: AI 평가 로직 강화(gpt-4o-mini) 및 관련 기능 통합
import openai
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import StreamingHttpResponse
import os
import json
import re
import sys
import time
import traceback

@method_decorator(csrf_exempt, name='dispatch')
class AIChatView(APIView):
    """
    AI 학습 도우미 챗봇 뷰 (JRPG 코드 위저드 컨셉)
    """
    authentication_classes = [] 
    permission_classes = [AllowAny]

    def post(self, request):
        user_message = request.data.get('message')
        quest_context = request.data.get('quest_context', '')
        
        if not user_message:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                return Response({"error": "API Key not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            client = openai.OpenAI(api_key=api_key)
            
            system_prompt = f"""
            당신은 'Super Code Adventure' 게임의 AI 튜터 '코드 위저드'입니다.
            현재 사용자는 다음 퀘스트를 수행 중입니다: {quest_context}
            
            평가 및 대화 규칙:
            1. 친절한 JRPG 게임 캐릭터 말투를 사용하세요 (~하오, ~하게나, 혹은 신비로운 마법사 톤).
            2. 한국어로 핵심만 전달하세요.
            """

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )

            ai_message = response.choices[0].message.content
            return Response({"message": ai_message}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class AIEvaluationView(APIView):
    """
    실습 결과 AI 정밀 평가 및 꼬리 질문 생성 뷰
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        # [수정일: 2026-01-27] AxiosError 500 해결을 위한 데이터 및 SDK 호환성 수정한 버전
        score = request.data.get('score', 0)
        grade = request.data.get('grade', 'F')
        quest_title = request.data.get('quest_title', '알 수 없는 퀘스트')
        user_logic = request.data.get('user_logic', [])
        user_code = request.data.get('user_code', {})
        user_free_answer = request.data.get('user_free_answer', '')
        
        # 디버그 로그 (실시간 확인용)
        print(f"[DEBUG] Eval Start: {quest_title} / {score}", flush=True)
        
        try:
            # [DEBUG] API Key Check
            # [DEBUG] API Key Check
            api_key = settings.OPENAI_API_KEY
            if api_key:
                print(f"[DEBUG] OPENAI_API_KEY Loaded. Prefix: {api_key[:8]}...", flush=True)
            else:
                print(f"[DEBUG] OPENAI_API_KEY is Missing or Empty.", flush=True)
            
            if not api_key:
                print("[CRITICAL] OpenAI API Key is missing in settings!", flush=True)
                return Response({"error": "OpenAI API Key is missing"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            client = openai.OpenAI(api_key=api_key)
            print("[DEBUG] OpenAI Client Initialized", flush=True)

            # [수정일: 2026-02-04] 수석 아키텍트급 정밀 평가를 위한 프롬프트 강화 및 모델 업그레이드 (gpt-4o-mini)
            # [2026-02-09] 프론트엔드에서 전달받은 정밀 평가 기준 추출
            criteria = request.data.get('evaluation_criteria', {})
            rules = criteria.get('rules', [])
            constraints = criteria.get('constraints', {})
            code_constraints = criteria.get('code_constraints', {})
            
            # 규칙 텍스트 포맷팅
            rules_str = "\n".join([f"- {r}" for r in rules]) if rules else "정보 없음"
            must_keywords = ", ".join(constraints.get('must_include_keywords', []))
            must_code = ", ".join(code_constraints.get('must_contain', []))
            
            system_prompt = f"""
            당신은 20년 경력의 예리한 수석 소프트웨어 아키텍트 'Coduck Wizard'입니다. 
            당신은 단순히 로직을 평가하는 것을 넘어, 사용자가 인터뷰에서 정한 '설계 지침'을 충실히 따랐는지, 
            그리고 로직이 실무 수준의 정밀도를 갖췄는지 엄격하게 심사합니다.

            [현재 미션의 핵심 평가 기준]
            1. 엔지니어링 규칙 준수 여부:
            {rules_str}
            
            2. 필수 포함 키워드 (설계 서술): {must_keywords}
            3. 필수 포함 코드 패턴: {must_code}

            반드시 아래의 **JSON 형식으로만** 응답해야 합니다.

            [평가 규칙 - [수정일: 2026-02-23] 학습 의욕 고취를 위해 채점 기준 완화]
            1. **긍정적 강화 (Positive Reinforcement)**: 
               - 핵심 의도를 파악한 '일반적인 정답'은 **80~89점** 사이로 넉넉히 배점하십시오. (기존 70~79에서 상향)
               - **100점(만점)**은 엔지니어링 규칙을 완벽히 준수하고, 심오한 아키텍처적 통찰이 있을 때 부여하십시오.
               - 방향성은 맞으나 세부 사항이 부족한 경우에도 **60점 이상**을 주어 격려하십시오.
            
            2. **감점 완화**:
               - '엔지니어링 규칙' 미준수 시 감점 폭을 줄여 **-10점** 정도로 조정하십시오.
               - 필수 키워드 누락은 **-5점** 정도로 반영하십시오.
               - 단순 자연어 서술이라도 논리 흐름이 맞다면 과도한 감점은 피하십시오.

            3. **피드백 스타일**: 
               - 날카로운 시니어 아키텍트의 페르소나를 유지하십시오. 
               - 칭찬보다는 **"무엇이 부족해서 100점이 아닌지"**를 구체적으로 지적하십시오.

            [JSON 구조]
            {{
              "score": 0-100,
              "analysis": "사용자 로직의 타당성 및 설계 지침 준수 여부 정밀 분석 (2~3문단)",
              "advice": "다음 단계를 위한 시니어의 핵심 조언",
              "is_logical": true/false (지침 미준수 시 false),
              "metrics": {{
              "metrics": {{
                "정합성": {{ "score": 0-100, "comment": "요구사항과 비교하여 누락된 점을 날카롭게 지적 (30자 내외)", "improvement": "구체적으로 무엇을 추가해야 하는지 명시" }},
                "추상화": {{ "score": 0-100, "comment": "코드의 모듈화 수준에 대한 비평", "improvement": "함수 분리 또는 클래스 도입 제안" }},
                "예외처리": {{ "score": 0-100, "comment": "예상치 못한 입력에 대한 방어 로직 평가", "improvement": "구체적인 예외 케이스(예: 빈 값, 특수문자) 제시" }},
                "구현력": {{ "score": 0-100, "comment": "문법 선택의 적절성 비평", "improvement": "더 효율적인 파이썬 내장 함수나 패턴 제안" }},
                "설계력": {{ "score": 0-100, "comment": "전체 데이터 흐름의 효율성 평가", "improvement": "병목 현상 해결 방안 또는 확장성 제안" }}
              }},
              "tail_question": {{
                "question": "현재 설계된 아키텍처의 맹점을 찌르거나 다음 구현 단계에서 고려해야 할 예외 상황 질문",
                "options": [
                  {{"text": "정답", "is_correct": true, "reason": "이유..."}},
                  {{"text": "오답1", "is_correct": false, "reason": "이유..."}},
                  {{"text": "오답2", "is_correct": false, "reason": "이유..."}}
                ]
              }},
              "supplementary_videos": [
                {{
                  "title": "추천 학습 주제 (예: Python Data Scaling Best Practices)",
                  "desc": "추천 이유 (예: 데이터 누수를 방지하기 위함)",
                  "search_query": "유튜브 검색어 (예: python sklearn standardscaler train test split leak)"
                }}
              ]
            }}
            """
            
            logic_str = ', '.join(user_logic) if isinstance(user_logic, list) else str(user_logic)
            user_msg = f"""
            [미션] {quest_title}
            
            [평가 기준 요약]
            - 규칙: {rules_str}
            - 코드 필수 포함: {must_code}
            
            [사용자 로직]
            {logic_str}
            
            [비즈니스 요구사항/데이터]
            - Python Template: {user_code}
            - 추가 서술: {user_free_answer}
            
            위 데이터를 아키텍트의 관점에서 분석하여 JSON 결과를 출력하라.
            """

            print("[DEBUG] Calling AI for Logic Evaluation with gpt-4o-mini...", flush=True)
            print(f"[DEBUG] System Prompt: {system_prompt[:500]}...", flush=True) # Check if strict mode is active

            response = client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            print(f"[DEBUG] Raw AI Response: {content}", flush=True) # Check raw JSON response

            try:
                # JSON 문자열 정제
                if "```" in content:
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                
                result = json.loads(content.strip())
                
                # 프론트엔드 호환성 유지
                if 'feedback' not in result and 'analysis' in result:
                    result['feedback'] = result['analysis']
                    
                return Response(result, status=status.HTTP_200_OK)
            
            except Exception as parse_e:
                print(f"[DEBUG] JSON Parse Fail: {parse_e}", flush=True)
                # 파싱 실패 시 기본 응답 구조 반환
                return Response({
                    "score": 50,
                    "analysis": "분석 엔진이 자네의 복잡한 논리를 이해하려다 과부하가 걸렸네. 형식을 다시 갖춰보게.",
                    "advice": "JSON 구조가 깨졌을 수 있으니 다시 시도하게나.",
                    "is_logical": False,
                    "metrics": { "정합성": 50, "추상화": 50, "예외처리": 50, "구현력": 50, "설계력": 50, "효율성": 50, "가독성": 50 },
                    "tail_question": {
                        "question": "시스템 오류 발생 시 아키텍트가 가장 먼저 해야 할 일은?",
                        "options": [
                            {"text": "로그를 분석하여 원인을 파악한다", "is_correct": True, "reason": "데이터가 모든 것을 말해줍니다."},
                            {"text": "서버를 껐다 켠다", "is_correct": False, "reason": "임시방편일 뿐입니다."},
                            {"text": "무시하고 그대로 둔다", "is_correct": False, "reason": "기술 부채가 쌓입니다."}
                        ]
                    }
                }, status=status.HTTP_200_OK)

        except Exception as e:
            tb = traceback.format_exc()
            print(f"[CRITICAL] AI Error: {e}\n{tb}", file=sys.stderr, flush=True)
            
            # [Fallback Response] 에러 발생 시에도 프론트엔드가 멈추지 않도록 기본 응답 반환
            fallback_result = {
                "score": 75,
                "analysis": f"AI 신경망 연결이 불안정하여 정밀 분석을 완료하지 못했습니다. (Error: {str(e)})",
                "advice": "잠시 후 다시 시도하거나, 네트워크 상태를 확인해주세요.",
                "is_logical": True,
                "metrics": { "정합성": 70, "추상화": 70, "예외처리": 70, "구현력": 70, "설계력": 70 },
                "tail_question": {
                    "question": "네트워크 분할(Network Partition) 상황에서 시스템 가용성을 유지하기 위한 전략은?",
                    "options": [
                        {"text": "CAP 이론에 따라 일관성(Consistency)을 일부 희생하고 가용성(Availability)을 택한다.", "is_correct": True, "reason": "가용성이 중요할 때의 일반적인 선택입니다."},
                        {"text": "시스템을 즉시 종료한다.", "is_correct": False, "reason": "가용성을 0으로 만드는 행위입니다."},
                        {"text": "모든 요청을 대기시킨다.", "is_correct": False, "reason": "사용자 경험을 크게 저해합니다."}
                    ]
                }
            }
            return Response(fallback_result, status=status.HTTP_200_OK)
        

@method_decorator(csrf_exempt, name='dispatch')
class BugHuntEvaluationView(APIView):
    """
    [수정일: 2026-02-11]
    Step별 딥다이브 면접 결과를 종합하여 최종 평가를 생성합니다.
    면접 점수를 재채점하지 않고, 기존 면접 결과를 종합·분석하여
    전체적인 디버깅 역량 요약과 학습 방향을 제시합니다.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    EVAL_MODEL = "gpt-5-mini"

    def post(self, request):
        data = request.data
        mission_title = data.get('missionTitle', 'Unknown Mission')
        steps = data.get('steps', [])
        explanations = data.get('explanations', {})
        user_codes = data.get('userCodes', {})
        performance = data.get('performance', {})
        interview_results = data.get('interviewResults', {})

        if not steps:
            return Response({"error": "Steps data is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                return Response({"error": "API Key not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            client = openai.OpenAI(api_key=api_key)

            # Step별 컨텍스트 구성
            step_context_parts = []
            for idx, s in enumerate(steps):
                step_num = idx + 1
                step_num_str = str(step_num)
                original_code = s.get('buggy_code', '')
                modified_code = user_codes.get(step_num_str, '')
                true_cause = s.get('error_info', {}).get('description', '정보 없음')
                correct_logic = s.get('error_info', {}).get('suggestion', '정보 없음')

                # 면접 결과가 있는 경우
                iv = interview_results.get(step_num_str, {})
                iv_score = iv.get('score', '없음')
                iv_level = iv.get('understanding_level', '없음')
                iv_concepts = ', '.join(iv.get('matched_concepts', [])) or '없음'
                iv_weak = iv.get('weak_point', '없음') or '없음'

                step_context_parts.append(f"""### Step {step_num}: {s.get('title', '')}
- 버그 원인(정답): {true_cause}
- 권장 해결책(정답): {correct_logic}
- 원본 코드 → 사용자 수정 코드: (코드 수정 완료됨)
- [면접 결과] 점수: {iv_score}/100 | 이해 수준: {iv_level}
- [면접 결과] 파악한 개념: {iv_concepts}
- [면접 결과] 보완 필요: {iv_weak}""")

            step_context_str = '\n\n'.join(step_context_parts)

            # 면접 점수 통계
            iv_scores = []
            for idx in range(len(steps)):
                iv = interview_results.get(str(idx + 1), {})
                if isinstance(iv.get('score'), (int, float)):
                    iv_scores.append(iv['score'])
            avg_score = round(sum(iv_scores) / len(iv_scores)) if iv_scores else 50

            system_message = """너는 주니어 AI 엔지니어의 디버깅 역량을 종합 평가하는 시니어 멘토이다.

[역할]
- 각 Step별 딥다이브 면접 결과가 이미 채점되어 있다.
- 너는 점수를 재채점하지 않는다.
- 면접 결과를 종합 분석하여 전체적인 디버깅 역량 평가와 학습 방향을 제시한다.
- 교육적이고 격려하는 톤을 유지하되, 부족한 점은 명확히 짚어준다.
- 존댓말을 사용한다."""

            prompt = f"""## 종합 평가 대상

미션: {mission_title}

[풀이 성과]
- 코드 제출 실패: {performance.get('codeSubmitFailCount', 0)}회
- 힌트 사용: {performance.get('hintCount', 0)}회
- 총 소요 시간: {performance.get('totalDebugTime', 0)}초

[Step별 면접 결과]
{step_context_str}

[면접 점수 평균]: {avg_score}/100

---

## 종합 평가 지침

1. **Step별 면접 점수를 그대로 인정**한다. 재채점하지 않는다.
2. **thinking_score**는 면접 점수 평균({avg_score})을 기본으로 하되, 아래 보정을 적용한다:
   - 힌트 0회 + 제출 실패 0회 → +3점 보너스
   - 힌트 3회 이상 → -2점
   - 전 Step 이해 수준이 모두 Deep 이상 → +5점 보너스
   - 보정 후 0~100 범위로 클램프
3. **code_risk**: 이해 수준이 낮을수록 위험도가 높다.
   - Deep → 10, Conceptual → 25, Surface → 50, None/Unknown → 70
   - 여러 Step의 평균으로 계산
4. **thinking_pass**: thinking_score >= 60이면 true
5. **step_feedbacks**: 각 Step별로 면접에서 드러난 강점과 약점을 1~2문장으로 요약
6. **총평**: 전체 디버깅 역량을 3~5문장으로 종합 분석. 잘한 점, 부족한 점, 구체적 학습 방향을 포함

---

## 출력 형식

**반드시 아래 JSON만 출력하라. 다른 텍스트 금지.**

{{
  "thinking_pass": true,
  "code_risk": 25,
  "thinking_score": {avg_score},
  "총평": "종합 평가 내용을 존댓말로 작성",
  "step_feedbacks": [
    {{"step": 1, "feedback": "Step 1 면접 결과 기반 요약 피드백", "step_score": 0}},
    {{"step": 2, "feedback": "Step 2 면접 결과 기반 요약 피드백", "step_score": 0}},
    {{"step": 3, "feedback": "Step 3 면접 결과 기반 요약 피드백", "step_score": 0}}
  ]
}}

**주의**:
- step_feedbacks의 step_score는 해당 Step의 면접 점수를 그대로 사용
- step_feedbacks 개수는 실제 Step 수({len(steps)}개)와 일치
- thinking_score는 보정 적용된 최종 값
"""

            response = client.chat.completions.create(
                model=self.EVAL_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=2000
            )

            response_text = response.choices[0].message.content.strip()
            print(f"[BugHuntEval] Raw response: {response_text[:500]}")

            # JSON 파싱
            json_match = None
            match = re.search(r'\{[\s\S]*\}', response_text)
            if match:
                json_match = match.group()

            if json_match:
                result = json.loads(json_match)
                print(f"[BugHuntEval] Parsed result: thinking_score={result.get('thinking_score')}")
                return Response({
                    "thinking_pass": bool(result.get('thinking_pass', False)),
                    "code_risk": int(result.get('code_risk', 50)),
                    "thinking_score": int(result.get('thinking_score', avg_score)),
                    "총평": result.get('총평', result.get('summary', '평가를 완료했습니다.')),
                    "step_feedbacks": result.get('step_feedbacks', [])
                }, status=status.HTTP_200_OK)
            else:
                print(f"[BugHuntEval] JSON parse failed, raw: {response_text}")
                return Response({"error": "Invalid JSON format from AI"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            print(f"[BugHuntEval] Exception: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class BugHuntInterviewView(APIView):
    """
    S4+ 딥다이브 면접 API.
    Step별로 LLM 면접관이 유저와 2~3턴 대화하며 이해도를 평가한다.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    MAX_TURNS = 3
    INTERVIEW_MODEL = "gpt-5.2"

    @staticmethod
    def _parse_json_object(raw_text):
        if not raw_text:
            raise json.JSONDecodeError("empty response", "", 0)

        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", cleaned)
            if not match:
                raise
            return json.loads(match.group(0))

    def post(self, request):
        data = request.data
        step_context = data.get('step_context', {})
        conversation = data.get('conversation', [])
        turn = data.get('turn', 0)
        candidate_name = data.get('candidate_name', '')
        use_stream = bool(data.get('stream', False))

        if not step_context:
            return Response({"error": "step_context is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            api_key = getattr(settings, "OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
            if not api_key:
                return Response({"error": "OPENAI_API_KEY not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            client = openai.OpenAI(api_key=api_key)

            rubric = step_context.get('interview_rubric', {})
            is_final_turn = (turn > self.MAX_TURNS)

            # 스트리밍은 질문 턴에서만 사용 (최종 평가는 구조화 JSON 유지)
            if use_stream and not is_final_turn:
                return self._stream_question_response(
                    client=client,
                    step_context=step_context,
                    rubric=rubric,
                    conversation=conversation,
                    turn=turn,
                    candidate_name=candidate_name
                )

            system_prompt = self._build_system_prompt(step_context, rubric, is_final_turn, candidate_name)

            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation)

            response = client.chat.completions.create(
                model=self.INTERVIEW_MODEL,
                messages=messages,
                temperature=0.6,
                max_completion_tokens=800,
                response_format={"type": "json_object"}
            )

            raw = response.choices[0].message.content
            result = self._parse_json_object(raw)

            if not isinstance(result, dict):
                raise json.JSONDecodeError("result is not object", str(raw), 0)

            if is_final_turn:
                result.setdefault("type", "evaluation")
                result.setdefault("message", "답변을 종합해 보면 핵심 개념 이해는 좋지만 근거를 더 구체화하면 좋겠습니다.")
                result.setdefault("score", 65)
                result.setdefault("understanding_level", "Surface")
                result.setdefault("matched_concepts", [])
                result.setdefault("weak_point", "답변 근거의 구체성")
            else:
                result.setdefault("type", "question")
                result.setdefault("message", "좋은 설명입니다. 한 단계 더 깊게 설명해주시겠어요?")

            return Response(result, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            if is_final_turn:
                return Response({
                    "type": "evaluation",
                    "message": "종합적으로 핵심은 이해하셨습니다. 다만 실무 적용 근거를 더 구체적으로 말하면 더 높은 점수를 받을 수 있습니다.",
                    "score": 60,
                    "understanding_level": "Surface",
                    "matched_concepts": [],
                    "weak_point": "실무 적용 근거의 구체성"
                }, status=status.HTTP_200_OK)
            return Response({
                "type": "question",
                "message": "답변을 분석하고 있습니다. 조금 더 구체적으로 설명해주시겠어요?",
                "turn": turn
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _stream_question_response(self, client, step_context, rubric, conversation, turn, candidate_name=''):
        system_prompt = self._build_stream_prompt(step_context, rubric, turn, candidate_name)
        messages = [{"role": "system", "content": system_prompt}] + conversation

        def event_stream():
            try:
                stream = client.chat.completions.create(
                    model=self.INTERVIEW_MODEL,
                    messages=messages,
                    temperature=0.6,
                    max_completion_tokens=400,
                    stream=True,
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    token = getattr(delta, "content", None) or ""
                    if token:
                        payload = json.dumps({"token": token}, ensure_ascii=False)
                        yield f"data: {payload}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                payload = json.dumps({"error": str(e)}, ensure_ascii=False)
                yield f"data: {payload}\n\n"
                yield "data: [DONE]\n\n"

        response = StreamingHttpResponse(
            event_stream(),
            content_type='text/event-stream; charset=utf-8'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

    def _build_system_prompt(self, step_context, rubric, is_final_turn, candidate_name=''):
        buggy_code = step_context.get('buggy_code', '')
        user_code = step_context.get('user_code', '')
        error_info = step_context.get('error_info', {})
        display_name = (candidate_name or '').strip() or '지원자'

        core = rubric.get('core_concepts', [])
        mechanism = rubric.get('mechanism_concepts', [])
        application = rubric.get('application_concepts', [])

        rubric_text = (
            f"핵심 개념 (core): {', '.join(core)}\n"
            f"메커니즘 개념 (mechanism): {', '.join(mechanism)}\n"
            f"응용 개념 (application): {', '.join(application)}"
        )

        if is_final_turn:
            return f"""너는 주니어 AI 엔지니어 기술 면접관이다. 한국어로 대화한다.
{display_name}님이 아래 코드의 버그를 수정했고, 지금까지 대화를 나눴다.
이번이 마지막 턴이다. {display_name}님의 마지막 답변을 평가하고 종합 평가를 JSON으로 반환하라.

[버그 코드]
{buggy_code}

[유저가 수정한 코드]
{user_code}

[버그 정보]
타입: {error_info.get('type', '')}
설명: {error_info.get('description', '')}

[평가 기준 - 채점 루브릭]
{rubric_text}

[채점 방법 - 주니어 엔지니어 기준으로 관대하게 채점하라]
대화 전체를 종합해서 채점하라 (마지막 답변만이 아님).
피드백 문장에서는 반드시 "{display_name}님" 호칭을 사용하라.

1) core (40점 만점):
   - 핵심 원인을 자기 말로 설명했으면 30~40점 (전문 용어 불필요, 의미가 맞으면 충분)
   - 방향은 맞지만 부정확하면 15~25점
   - 전혀 모르면 0~10점

2) mechanism (35점 만점):
   - 내부 동작을 구체적으로 설명했으면 25~35점
   - 개념은 알지만 설명이 모호하면 10~20점
   - 언급 없으면 0~5점

3) application (25점 만점):
   - 실무 적용 방법을 1가지라도 구체적으로 제시하면 15~25점
   - 추상적으로만 언급하면 5~12점
   - 언급 없으면 0점

[understanding_level 기준]
- 90점 이상: "Excellent"
- 70~89점: "Good"
- 40~69점: "Surface"
- 39점 이하: "Poor"

반드시 아래 JSON 형식으로만 응답하라:
{{
  "type": "evaluation",
  "message": "2~3문장의 종합 피드백 (잘한 점 + 부족한 점)",
  "score": 0에서 100 사이 정수 (core + mechanism + application의 합),
  "core_score": 0에서 40 사이 정수,
  "mechanism_score": 0에서 35 사이 정수,
  "application_score": 0에서 25 사이 정수,
  "understanding_level": "Excellent|Good|Surface|Poor",
  "matched_concepts": ["유저가 보여준 개념들"],
  "weak_point": "부족한 부분 (없으면 null)"
}}"""

    def _build_stream_prompt(self, step_context, rubric, turn, candidate_name=''):
        buggy_code = step_context.get('buggy_code', '')
        user_code = step_context.get('user_code', '')
        error_info = step_context.get('error_info', {})
        display_name = (candidate_name or '').strip() or '지원자'
        remaining = self.MAX_TURNS - turn

        core = rubric.get('core_concepts', [])
        mechanism = rubric.get('mechanism_concepts', [])
        application = rubric.get('application_concepts', [])

        rubric_text = (
            f"핵심 개념 (core): {', '.join(core)}\n"
            f"메커니즘 개념 (mechanism): {', '.join(mechanism)}\n"
            f"응용 개념 (application): {', '.join(application)}"
        )

        return f"""너는 주니어 AI 엔지니어를 면접하는 기술 면접관이다. 한국어로 대화한다.
{display_name}님이 아래 코드의 버그를 수정했다. 수정 이유와 이해도를 파악하기 위해 질문한다.

[대상 수준 - 매우 중요]
상대방은 AI/ML을 배우고 있는 주니어 엔지니어다.
- 물어봐도 되는 것: 개념의 "왜", 내부 동작 원리, 코드 동작 순서, 해당 버그와 직접 관련된 내용
- 절대 물어보면 안 되는 것: gradient accumulation 구현, loss scaling, learning rate scheduling 전략, 분산 학습, 커스텀 옵티마이저 등 시니어 레벨 주제
- 루브릭에 있는 개념 범위 안에서만 질문하라. 루브릭에 없는 심화 주제로 넘어가지 마라.

[현재 진행 상황]
현재 {turn}/{self.MAX_TURNS}턴 (남은 질문 기회: {remaining}회)

턴별 질문 방향:
- 1턴 (첫 답변 후): core 개념을 정확히 이해했는지 확인. 틀린 부분이 있으면 반드시 짚어라.
- 2턴: mechanism 개념으로 넘어가라. "내부적으로 어떤 일이 일어나는지" 물어라.
- 3턴 (마지막): application 개념을 물어라. 단, 주니어 수준의 실무 (디버깅 방법, 확인 방법) 한정.

[버그 코드]
{buggy_code}

[유저가 수정한 코드]
{user_code}

[버그 정보]
타입: {error_info.get('type', '')}
설명: {error_info.get('description', '')}

[평가 기준 - 채점 루브릭]
{rubric_text}

[적응형 질문 전략 - 유저의 직전 답변을 기준으로 판단하라]

1) 답변이 정확하고 구체적인 경우:
   → "잘 이해하고 계시네요"를 짧게 인정한 뒤, 루브릭의 다음 단계 개념을 물어라.
   → 단, 반드시 루브릭 범위 안의 개념만 물어라.

2) 방향은 맞지만 부정확하거나 빠진 부분이 있는 경우:
   → 틀린 부분을 부드럽게 짚어라. (예: "~라고 하셨는데, 실제로는 조금 다릅니다. 그러면 ~는 어떤 식으로 동작할까요?")
   → 틀린 것을 그냥 넘어가지 마라. 교정이 최우선이다.

3) "모르겠다" 또는 매우 모호한 답변인 경우:
   → 난이도를 확 낮춰라. 같은 개념을 더 쉽게 다시 물어라.
   → 짧은 힌트를 제시하라. (예: "힌트를 드리자면, backward()를 호출할 때 .grad 값이 어떻게 변하는지 생각해보시면 됩니다. 혹시 아시나요?")
   → 절대로 같은 난이도나 더 어려운 질문을 내지 마라.

4) 완전히 방향이 틀린 경우:
   → 틀린 부분을 정중하게 알려주고, 올바른 방향의 단서를 준 뒤 더 쉬운 질문을 하라.

[규칙]
- 정답을 직접 알려주지 마라. 유도 질문만 하라.
- 질문은 1~2문장으로 짧고 명확하게 하라. 한 번에 여러 질문을 하지 마라.
- 반드시 존댓말을 사용하라.
- 유저를 부를 때는 반드시 "{display_name}님" 호칭을 사용하라.
- 내부 평가/분석 과정은 절대 노출하지 마라.
- 출력은 JSON이 아닌, 사용자에게 보여줄 "질문 문장만" 출력하라.
"""
