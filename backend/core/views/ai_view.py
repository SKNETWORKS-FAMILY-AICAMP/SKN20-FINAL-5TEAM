import openai
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import environ
import os
import json
import re
import sys
import traceback

env = environ.Env()

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
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                return Response({"error": "OpenAI API Key is missing"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            client = openai.OpenAI(api_key=api_key)
            
            # [중요] SDK 호환성을 위해 response_format 대신 프롬프트 지시 강화
            system_prompt = """
            당신은 시니어 소프트웨어 엔지니어 '코드 위저드'입니다. 
            반드시 아래의 **JSON 형식으로만** 응답해야 합니다. 다른 텍스트는 섞지 마세요.

            {
  "score": 0-100,
  "analysis": "답변 및 코드 논리에 대한 구체적인 분석 (특히 단순 키워드 나열인지, 실제 논리적 문장인지 판별하여 2~3문단으로 상세히 작성)",
  "advice": "제자를 위한 따뜻한 조언 및 개선 방향",
  "is_logical": true/false (단순 키워드 나열이면 false),
  "metrics": {
    "정합성": 0-100, "추상화": 0-100, "예외처리": 0-100, "구현력": 0-100, "설계력": 0-100
  },
  "tail_question": {
    "question": "논리적 헛점을 찌르는 날카로운 질문 1개",
    "options": [
      {"text": "정답", "is_correct": true, "reason": "..."},
      {"text": "오답1", "is_correct": false, "reason": "..."},
      {"text": "오답2", "is_correct": false, "reason": "..."}
    ]
  }
}
"""
            
            # [수정일: 2026-01-31] 프롬프트 지시 강화: 단순 키워드 나열(예: "반복 만약 제거")은 낮은 점수를 주도록 설정
            system_prompt += "\n**중요 지침**: 사용자가 입력한 '로직'이 단순히 '반복', '조건', '삭제' 처럼 의미 없는 단어의 나열이거나 논리적 연결이 없는 경우, `is_logical`을 `false`로 설정하고 `score`를 40점 이하로 감점하십시오. 실제 사람이 이해할 수 있는 '의사코드' 문장 형태를 갖추어야 합니다."
            
            logic_str = ', '.join(user_logic) if isinstance(user_logic, list) else str(user_logic)
            user_msg = f"""
            [미션] {quest_title} (현재 점수: {score})
            [로직] {logic_str}
            [코드] {user_code}
            [자유 답변] {user_free_answer}
            
            위 데이터를 분석하여 JSON 결과를 출력하라.
            """

            print("[DEBUG] Calling OpenAI...", flush=True)
            # response_format 제거 (SDK 호환성)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ]
            )
            
            content = response.choices[0].message.content
            print(f"[DEBUG] AI Response Received: {content[:100]}...", flush=True)

            try:
                # JSON 문자열 정제 (가끔 ```json ... ``` 으로 감싸지는 경우 대비)
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
                    "score": score,
                    "analysis": "분석 파싱 중 마법이 꼬였네. 하지만 자네의 논리는 충분히 훌륭하네.",
                    "advice": "코드의 가독성을 조금 더 신경 써보게나.",
                    "is_logical": True,
                    "metrics": { "정합성": 85, "추상화": 75, "예외처리": 65, "구현력": 85, "설계력": 80 },
                    "tail_question": {
                        "question": "파싱 에러가 발생했을 때, 시스템의 가용성을 유지하는 가장 좋은 방법은?",
                        "options": [
                            {"text": "Fallback 응답을 정의한다", "is_correct": True, "reason": "사용자 경험을 해치지 않습니다."},
                            {"text": "서버를 즉시 중단한다", "is_correct": False, "reason": "서비스 중단은 최후의 수단입니다."},
                            {"text": "에러를 무시한다", "is_correct": False, "reason": "데이터 오염의 위험이 있습니다."}
                        ]
                    }
                }, status=status.HTTP_200_OK)

        except Exception as e:
            tb = traceback.format_exc()
            print(f"[CRITICAL] AI Error: {e}\n{tb}", flush=True)
            return Response({"error": str(e), "traceback": tb}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@method_decorator(csrf_exempt, name='dispatch')
class BugHuntEvaluationView(APIView):
    """
    [수정일: 2026-01-27]
    Bug Hunt 디버깅 사고 평가 뷰
    사용자의 코드 수정과 설명을 분석하여 디버깅 능력을 평가합니다.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        mission_title = data.get('missionTitle', 'Unknown Mission')
        steps = data.get('steps', [])
        explanations = data.get('explanations', {})
        user_codes = data.get('userCodes', {})
        performance = data.get('performance', {})

        if not steps:
            return Response({"error": "Steps data is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                return Response({"error": "API Key not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            client = openai.OpenAI(api_key=api_key)

            # 각 단계별 데이터 구성
            step_context = []
            for idx, s in enumerate(steps):
                step_num = idx + 1
                original_code = s.get('buggy_code', '')
                modified_code = user_codes.get(str(step_num), '')
                explanation = explanations.get(str(step_num), '설명 없음')

                step_context.append(f"""### Step {step_num}: {s.get('title', s.get('bug_type', ''))}
- 문제 설명: {s.get('instruction', '')}

- 원본 버그 코드:
```python
{original_code}
```

- 사용자 수정 코드:
```python
{modified_code}
```

- 사용자 설명: {explanation}""")

            step_context_str = '\n\n'.join(step_context)

            system_message = """너는 디버깅 사고를 평가하는 시스템이다.
정오답이 아니라 "디버깅 사고의 질"을 평가한다.
냉철하고 객관적으로 평가하되, 교육적인 관점을 유지한다."""

            prompt = f"""## 평가 대상 데이터

미션: {mission_title}

[사용자 성과 지표]
- 퀴즈 오답 횟수: {performance.get('quizIncorrectCount', 0)}회
- 코드 제출 실패: {performance.get('codeSubmitFailCount', 0)}회
- 힌트 사용 횟수: {performance.get('hintCount', 0)}회
- 총 소요 시간: {performance.get('totalDebugTime', 0)}초

{step_context_str}

## 평가 단계

1. 사고 방향 평가 (모델 A 관점)
   다음 항목들을 검토한다:
   - 원인 언급 여부: 사용자가 버그의 근본 원인을 언급했는가?
   - 원인-수정 일치 여부: 언급한 원인과 실제 코드 수정이 일치하는가?
   - 부작용 고려 여부: 수정으로 인한 부작용을 고려했는가?
   - 수정 범위 적절성: 필요한 부분만 수정했는가, 과도하게 수정했는가?
   - 설명-코드 일관성: 설명 내용과 실제 코드 변경이 일관되는가?
   → 주요 항목(원인 언급, 원인-수정 일치, 설명-코드 일관성) 충족 시 통과

2. 코드 위험 평가 (모델 B 관점)
   다음 요소를 분석한다:
   - 변경 라인 수: 얼마나 많은 코드를 변경했는가?
   - 조건문/예외 처리 변화: 로직 흐름에 영향을 주는 변경이 있는가?
   - 기존 로직 훼손 여부: 원래 동작해야 할 부분을 망가뜨렸는가?
   → 위험 점수 0~100 (0: 매우 안전, 100: 매우 위험)

3. 사고 연속 점수 평가 (모델 C 관점)
   좋은 디버깅 답변의 특성과 비교한다:
   - 논리적 흐름: 문제 인식 → 원인 분석 → 해결책 제시 순서
   - 근거 제시: 왜 그렇게 수정했는지 이유를 설명했는가?
   - 명확성: 설명이 명확하고 이해하기 쉬운가?
   - 기술적 정확성: 사용한 용어와 개념이 정확한가?
   (참고: 오답이나 힌트 사용이 많다면, 사고의 자립성을 낮게 평가하라)
   → 사고 점수 0~100

4. **각 단계별 설명 피드백 생성 (필수)**
   위에 제시된 각 Step의 "사용자 설명"을 개별적으로 평가하여 피드백을 생성하라.
   각 피드백은 한 문단으로 작성하되, 다음 내용을 포함:
   - 설명 품질 점수 (0-100점)
   - 잘한 점 (구체적으로)
   - 부족한 점 (구체적으로)
   - 개선 방향 제안

   예시:
   - 설명이 부실한 경우: "설명 품질: 20/100. 버그 발견 의도는 있으나 구체성이 부족합니다. '어떤 변수'가 '왜' 문제인지, '어떻게' 수정했는지 명확히 작성해주세요."
   - 설명이 양호한 경우: "설명 품질: 75/100. 원인과 해결책을 논리적으로 연결했습니다. 다만 수정으로 인한 부작용 고려까지 추가하면 더욱 완벽합니다."

## 출력 형식
**반드시 아래 JSON 형식만 출력하라. 다른 텍스트는 포함하지 마라.**

{{
  "thinking_pass": true,
  "code_risk": 45,
  "thinking_score": 70,
  "총평": "전체 평가를 요약하여 시니어 엔지니어 입장에서 설명하고 존댓말로 입력",
  "step_feedbacks": [
    {{
      "step": 1,
      "feedback": "실제 Step 1 사용자 설명을 분석한 구체적인 피드백 (점수 포함, 한 문단)"
    }},
    {{
      "step": 2,
      "feedback": "실제 Step 2 사용자 설명을 분석한 구체적인 피드백 (점수 포함, 한 문단)"
    }},
    {{
      "step": 3,
      "feedback": "실제 Step 3 사용자 설명을 분석한 구체적인 피드백 (점수 포함, 한 문단)"
    }}
  ]
}}

**중요**: step_feedbacks 배열은 반드시 3개 항목을 포함해야 하며, 각 step에 대한 실제 평가 내용을 작성해야 한다.
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.3
            )

            response_text = response.choices[0].message.content.strip()

            # JSON 파싱
            json_match = None
            match = re.search(r'\{[\s\S]*\}', response_text)
            if match:
                json_match = match.group()

            if json_match:
                result = json.loads(json_match)
                print(f"AI Response Result: {result}")
                print(f"Step Feedbacks: {result.get('step_feedbacks', [])}")
                return Response({
                    "thinking_pass": bool(result.get('thinking_pass', False)),
                    "code_risk": int(result.get('code_risk', 50)),
                    "thinking_score": int(result.get('thinking_score', 50)),
                    "총평": result.get('총평', result.get('summary', '평가를 완료했습니다.')),
                    "step_feedbacks": result.get('step_feedbacks', [])
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid JSON format from AI"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            print(f"Bug Hunt Evaluation Exception: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)