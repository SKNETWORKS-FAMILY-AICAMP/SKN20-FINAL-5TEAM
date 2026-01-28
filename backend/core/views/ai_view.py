import openai
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator



class AIEvaluationView(APIView):
    """
    [수정일: 2026-01-27]
    LLM 기반 동적 평가 및 페르소나 분석 뷰
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        quest_data = data.get('quest', {}) # 문제 전체 데이터
        quest_title = quest_data.get('title', 'Unknown Quest')
        quest_desc = quest_data.get('desc', '')
        performance = data.get('performance', {})

        try:
            api_key = settings.OPENAI_API_KEY
            client = openai.OpenAI(api_key=api_key)

            system_prompt = """
            당신은 소프트웨어 아키텍처 교육 플랫폼의 '인공지능 마스터 평가관'입니다.
            사용자가 방금 푼 문제의 정보(의도, 내용)와 사용자 풀이 데이터를 분석하여 전문적이고 교육적인 피드백을 내려주세요.

            반드시 아래 JSON 형식으로만 답변하세요:
            {
              "logicScore": 0-100 정수,
              "codingScore": 0-100 정수,
              "designScore": 0-100 정수,
              "personaTitle": "플레이 스타일에 따른 재미있는 별명",
              "feedbackMessage": "전체 총평, 문제의 학습 가치, 사용자 맞춤 제언을 포함하여 3~4개의 문단으로 구성하세요. 각 문단은 반드시 두 번의 줄바꿈(\\n\\n)으로 구분하여 프론트엔드에서 분리되어 렌더링될 수 있도록 하세요.",
              "totalScore": 0-100 정수
            }

            피드백 가이드라인:
            - 단순한 칭찬이 아니라, 문제의 '핵심 로직'이나 '비즈니스 규칙'을 언급하며 전문적으로 설명하세요.
            - 예를 들어 '배달비 자동 계산' 문제라면 '조건부 로직을 통한 비용 최적화'의 중요성을 언급하세요.
            - 사용자의 오답 횟수나 소요 시간에 따라 학습 태도에 대한 코칭도 덧붙여주세요.
            """

            user_input = f"""
            [문제 정보]
            - 제목: {quest_title}
            - 설명: {quest_desc}

            [사용자 풀이 지표]
            - 총 소요 시간: {performance.get('timeSpent')}초
            - 오답 횟수: {performance.get('penaltyCount')}회
            - 힌트 사용: {performance.get('hintsUsed')}개
            - 2단계 원샷 성공: {performance.get('perkFlags', {}).get('oneShotCoding')}
            - 3단계 설계 성공: {performance.get('perkFlags', {}).get('perfectDesign')}

            위 정보를 바탕으로 해당 문제의 교육적 목표 달성 여부를 평가하고, 사용자가 무엇을 배웠는지 설명하는 딥-피드백을 생성해줘.
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                response_format={ "type": "json_object" }
            )

            import json
            try:
                analysis = json.loads(response.choices[0].message.content)
                # 최종 점수가 없을 경우 계산
                if 'totalScore' not in analysis or not analysis['totalScore']:
                    analysis['totalScore'] = int(analysis.get('logicScore', 0) * 0.3 + analysis.get('codingScore', 0) * 0.3 + analysis.get('designScore', 0) * 0.4)
                return Response(analysis, status=status.HTTP_200_OK)
            except Exception as json_err:
                print(f"JSON Parsing Error: {json_err}")
                return Response({"error": "AI response was not valid JSON"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            print(f"AI Evaluation Exception: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

            import json
            response_text = response.choices[0].message.content.strip()

            # JSON 파싱
            json_match = None
            import re
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
