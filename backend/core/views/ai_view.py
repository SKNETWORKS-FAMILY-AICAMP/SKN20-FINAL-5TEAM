# [수정일: 2026-02-04] pseudo_tts 브런치를 main 브런치로 머지: AI 평가 로직 강화(gpt-4o-mini) 및 관련 기능 통합
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

            # [수정일: 2026-02-04] 수석 아키텍트급 정밀 평가를 위한 프롬프트 강화 및 모델 업그레이드 (gpt-4o-mini)
            system_prompt = """
            당신은 20년 경력의 예리한 수석 소프트웨어 아키텍트 'Coduck Wizard'입니다. 
            당신은 단순히 로직을 평가하는 것을 넘어, 사용자가 인터뷰에서 정한 '설계 지침'을 충실히 따랐는지, 
            그리고 로직이 실무 수준의 정밀도를 갖췄는지 엄격하게 심사합니다.

            반드시 아래의 **JSON 형식으로만** 응답해야 합니다.

            [평가 규칙]
            1. 사용자가 문장 형태의 '의사코드'를 작성하지 않고 단어만 나열했다면 'is_logical'을 false로 하고 30점 이하를 부여하십시오.
            2. '필수 설계 요구사항'이 제공된 경우, 
            이를 하나라도 누락하거나 잘못 해석했다면 가차 없이 'is_logical'을 false로 하고 승인을 반려하십시오.
            3. 말투는 시의적절하게 전문적이고, 보완이 필요한 부분은 날카롭고 구체적으로 지적하십시오.

            [JSON 구조]
            {
              "score": 0-100,
              "analysis": "사용자 로직의 타당성 및 설계 지침 준수 여부 정밀 분석 (2~3문단)",
              "advice": "다음 단계를 위한 시니어의 핵심 조언",
              "is_logical": true/false (지침 미준수 시 false),
              "metrics": {
                "정합성": 0-100, "추상화": 0-100, "예외처리": 0-100, "구현력": 0-100, "설계력": 0-100
              },
              "tail_question": {
                "question": "현재 설계된 아키텍처의 맹점을 찌르거나 다음 구현 단계에서 고려해야 할 예외 상황 질문",
                "options": [
                  {"text": "정답", "is_correct": true, "reason": "이유..."},
                  {"text": "오답1", "is_correct": false, "reason": "이유..."},
                  {"text": "오답2", "is_correct": false, "reason": "이유..."}
                ]
              }
            }
            """
            
            logic_str = ', '.join(user_logic) if isinstance(user_logic, list) else str(user_logic)
            user_msg = f"""
            [미션] {quest_title}
            [사용자 로직]
            {logic_str}
            
            [비즈니스 요구사항/데이터]
            - Python Template: {user_code}
            - 추가 서술: {user_free_answer}
            
            위 데이터를 아키텍트의 관점에서 분석하여 JSON 결과를 출력하라.
            """

            print("[DEBUG] Calling AI for Logic Evaluation with gpt-4o-mini...", flush=True)
            response = client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            print(f"[DEBUG] AI Response Received: {content[:100]}...", flush=True)

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
            print(f"[CRITICAL] AI Error: {e}\n{tb}", flush=True)
            return Response({"error": str(e), "traceback": tb}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@method_decorator(csrf_exempt, name='dispatch')
class BugHuntEvaluationView(APIView):
    """
    [수정일: 2026-01-27]
    JSON 정답 데이터를 기반으로 사용자의 디버깅 사고 전략을 평가합니다.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        mission_title = data.get('missionTitle', 'Unknown Mission')
        steps = data.get('steps', []) # JSON의 원본 데이터가 포함된 배열
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

            # [변경 사항] 각 단계별 '정답 데이터'를 컨텍스트에 포함시켜 LLM의 평가 기준을 명확히 함
            step_context = []
            for idx, s in enumerate(steps):
                step_num = idx + 1
                original_code = s.get('buggy_code', '')
                modified_code = user_codes.get(str(step_num), '')
                explanation = explanations.get(str(step_num), '설명 없음')
                
                # JSON 파일 내의 정답 정보 추출
                true_cause = s.get('error_info', {}).get('description', '정보 없음') # 
                correct_logic = s.get('error_info', {}).get('suggestion', '정보 없음') # 
                coaching_point = s.get('coaching', '정보 없음') # 

                step_context.append(f"""### Step {step_num}: {s.get('title', '')}
- 문제 원인(정답): {true_cause}
- 권장 해결책(정답): {correct_logic}
- 실무 코칭 가이드: {coaching_point}

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
냉철하고 객관적으로 평가하되, 교육적인 관점을 유지한다.

**평가는 반드시 아래의 5가지 평가 기준을 따라 체계적으로 수행한다.**"""

            prompt = f"""## 평가 대상 데이터

미션: {mission_title}

[사용자 성과 지표]
- 퀴즈 오답 횟수: {performance.get('quizIncorrectCount', 0)}회
- 코드 제출 실패: {performance.get('codeSubmitFailCount', 0)}회
- 힌트 사용 횟수: {performance.get('hintCount', 0)}회
- 총 소요 시간: {performance.get('totalDebugTime', 0)}초

{step_context_str}

---

## 평가 기준 (총 100점)

각 영역을 20점 만점으로 평가하고, 합산하여 총점을 계산한다.

### 1. 버그 원인 식별 (20점)
**평가 내용**: 사용자가 버그의 근본 원인을 정확히 파악했는가?

- **18-20점 (우수)**: 근본 원인까지 정확히 설명 (예: "데이터 누수는 train_test_split 전에 스케일링을 하면 테스트 데이터 정보가 학습에 유출되기 때문")
- **15-17점 (양호)**: 직접 원인은 언급했으나 근본 원인 설명 부족 (예: "전체 데이터로 스케일링하면 안됨")
- **10-14점 (보통)**: 원인을 언급했으나 불명확하거나 부정확함
- **5-9점 (미흡)**: 원인 언급 없이 수정 방법만 제시
- **0-4점 (매우 미흡)**: 원인을 잘못 이해하거나 관련 없는 내용

### 2. 수정-원인 논리적 연결 (20점)
**평가 내용**: 언급한 원인과 실제 코드 수정이 논리적으로 일치하는가?

- **18-20점 (우수)**: 원인과 수정이 완벽하게 일치하며 인과관계 명확
- **15-17점 (양호)**: 원인과 수정이 연결되나 논리적 설명 부족
- **10-14점 (보통)**: 원인과 수정의 연결이 약하거나 모호함
- **5-9점 (미흡)**: 원인과 수정이 일치하지 않음
- **0-4점 (매우 미흡)**: 완전히 다른 방향의 수정

### 3. 해결 방법의 구체성 (20점)
**평가 내용**: 제시한 해결 방법이 구체적이고 실행 가능한가?

- **18-20점 (우수)**: 매우 구체적이고 즉시 적용 가능 (예: "scaler.fit(X_train)으로 fit하고 transform만 사용")
- **15-17점 (양호)**: 방향성은 맞으나 구체성 부족 (예: "train 데이터만 사용")
- **10-14점 (보통)**: 추상적이거나 불완전한 설명
- **5-9점 (미흡)**: 해결 방법이 모호하거나 비현실적
- **0-4점 (매우 미흡)**: 해결 방법 미제시 또는 잘못된 방법

### 4. 부작용 고려 (20점)
**평가 내용**: 수정으로 인한 부작용이나 주의사항을 고려했는가?

- **18-20점 (우수)**: 부작용을 명시하고 대응 방안까지 제시
- **15-17점 (양호)**: 부작용을 언급했으나 대응 방안 부족
- **10-14점 (보통)**: 부작용을 일부 고려했으나 불완전
- **5-9점 (미흡)**: 부작용 고려 없음
- **0-4점 (매우 미흡)**: 수정이 오히려 새로운 버그 유발

### 5. 설명의 명확성 (20점)
**평가 내용**: 설명이 기술적으로 정확하고 이해하기 쉬운가?

- **18-20점 (우수)**: 기술적으로 정확하고 매우 명확함
- **15-17점 (양호)**: 대체로 명확하나 일부 모호한 부분 존재
- **10-14점 (보통)**: 이해 가능하나 명확성 부족
- **5-9점 (미흡)**: 모호하거나 용어 사용 부정확
- **0-4점 (매우 미흡)**: 이해 불가능하거나 완전히 잘못된 설명

---

## Few-shot 예시

### 예시 1: Excellent (97점)

**사용자 답변**:
"train_test_split 전에 전체 데이터로 StandardScaler를 fit하면 테스트 데이터의 통계 정보(평균, 표준편차)가 학습에 유출됩니다.
스케일링은 train 데이터로만 fit한 후, test 데이터에는 transform만 적용해야 합니다.
수정: scaler.fit(X_train); X_train_scaled = scaler.transform(X_train); X_test_scaled = scaler.transform(X_test)"

**평가**:
{{
  "detailed_scores": {{
    "cause_identification": 20,
    "logic_connection": 19,
    "solution_quality": 20,
    "side_effects": 18,
    "explanation_clarity": 20
  }},
  "total_score": 97,
  "quality_level": "Excellent"
}}

### 예시 2: Good (78점)

**사용자 답변**:
"전체 데이터로 스케일링하면 안됩니다. train 데이터만 사용해야 합니다.
수정: scaler.fit(X_train)"

**평가**:
{{
  "detailed_scores": {{
    "cause_identification": 15,
    "logic_connection": 16,
    "solution_quality": 17,
    "side_effects": 14,
    "explanation_clarity": 16
  }},
  "total_score": 78,
  "quality_level": "Good"
}}

**Excellent와 Good의 핵심 차이**:
- Excellent: "왜(정보 유출)" + "어떻게(transform만)" + "구체적 코드"
- Good: "무엇(안됨)" + "간단한 방향(train만)"

### 예시 3: Average (46점)

**사용자 답변**:
"스케일링 위치를 바꿨습니다.
수정: scaler.fit(X)"

**평가**:
{{
  "detailed_scores": {{
    "cause_identification": 8,
    "logic_connection": 10,
    "solution_quality": 12,
    "side_effects": 5,
    "explanation_clarity": 11
  }},
  "total_score": 46,
  "quality_level": "Average"
}}

---

## 평가 수행 지침

1. **각 Step별로 위의 5가지 기준을 적용**하여 세부 점수를 산정한다.
2. **Few-shot 예시를 참고**하여 품질 레벨을 구분한다:
   - Excellent (85-100점): 모든 영역에서 우수
   - Good (70-84점): 대부분 양호, 일부 개선 필요
   - Average (55-69점): 기본은 갖췄으나 여러 부분 보완 필요
   - Poor (35-54점): 여러 영역에서 미흡
   - Very Poor (0-34점): 대부분 영역에서 매우 미흡

3. **성과 지표를 참고**하되 과도하게 반영하지 않는다:
   - 힌트 사용이 많더라도 최종 설명이 우수하면 높은 점수 부여 가능
   - 오답이 많아도 최종적으로 올바른 이해에 도달했으면 인정

4. **일관성을 유지**한다:
   - 동일한 품질의 답변은 동일한 점수 부여
   - Few-shot 예시의 점수 수준을 기준으로 삼음

---

## 출력 형식

**반드시 아래 JSON 형식만 출력하라. 다른 텍스트는 포함하지 마라.**

{{
  "thinking_pass": true,
  "code_risk": 10,
  "thinking_score": 85,
  "detailed_scores": {{
    "cause_identification": 18,
    "logic_connection": 17,
    "solution_quality": 19,
    "side_effects": 16,
    "explanation_clarity": 20
  }},
  "quality_level": "Excellent",
  "총평": "전체 평가를 요약하여 시니어 엔지니어 입장에서 설명하고 존댓말로 입력",
  "step_feedbacks": [
    {{
      "step": 1,
      "feedback": "실제 Step 1 사용자 설명을 분석한 구체적인 피드백",
      "detailed_scores": {{
        "cause_identification": 18,
        "logic_connection": 17,
        "solution_quality": 19,
        "side_effects": 16,
        "explanation_clarity": 20
      }},
      "step_score": 90
    }},
    {{
      "step": 2,
      "feedback": "실제 Step 2 사용자 설명을 분석한 구체적인 피드백",
      "detailed_scores": {{
        "cause_identification": 16,
        "logic_connection": 18,
        "solution_quality": 17,
        "side_effects": 15,
        "explanation_clarity": 18
      }},
      "step_score": 84
    }},
    {{
      "step": 3,
      "feedback": "실제 Step 3 사용자 설명을 분석한 구체적인 피드백",
      "detailed_scores": {{
        "cause_identification": 15,
        "logic_connection": 16,
        "solution_quality": 18,
        "side_effects": 14,
        "explanation_clarity": 17
      }},
      "step_score": 80
    }}
  ]
}}

**중요**:
- step_feedbacks는 반드시 3개 항목 포함
- 각 step에 detailed_scores와 step_score 포함
- thinking_score는 모든 step_score의 평균값
- quality_level은 thinking_score 기준: 85-100(Excellent), 70-84(Good), 55-69(Average), 35-54(Poor), 0-34(Very Poor)
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