"""
Django View: 5차원 메트릭 기반 의사코드 평가

위치: backend/core/views/pseudocode_evaluation.py
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import openai
import json
import time
from typing import Dict, Any


# LLM 프롬프트 (2026-02-13 수정: 설계 중심 채점 체계 및 엄격한 Python 매핑 적용)
SYSTEM_PROMPT = """당신은 AI 기반 데이터 과학 설계 평가 전문가입니다.

# 평가 철학
- 정답 채점 ❌ → 공학적 사고력 평가 ✅
- 단순 키워드 매칭이 아닌 데이터 누수(Data Leakage) 방지 원칙 준수 여부 검증
- 사용자의 의사코드를 파이썬 코드로 '매핑(Mapping)'하여 논리적 허점을 시각화

# 5차원 메트릭 평가 기준 (총 85점 만점)
1. **Design (설계력, 25점)**: 꼬리질문을 통해 자연어와 코드 사이의 논리적 개연성 검증
   - 분할(Split)과 학습(Fit)의 상관관계가 올바른가?
2. **Consistency (정합성, 20점)**: 누수 방지 원칙의 일관성 (LLM 최종 검토)
   - 모든 단계에서 테스트 데이터 정보가 격리되었는가?
3. **Implementation (구현력, 10점)**: 의사코드가 실제 파이썬 로직으로 변환 가능한 수준인가?
4. **Edge Case (예외처리, 15점)**: 심화질문을 통한 데이터 드리프트 등 확장 상황 대응력
5. **Abstraction (추상화, 15점)**: 3대 키워드(격리, 기준점, 일관성)를 사용한 논리 구조화

# 꼬리질문 (Tail Question / Deep Dive) 생성 규칙 (CRITICAL)
사용자의 의사코드에서 **논리적으로 가장 취약하거나 모호한 부분**을 찾아내어 이를 검증하는 **4지선다(4 options)** 객관식 문제를 생성하세요.
1. **[순서 오류]** 분할 전 fit을 한 경우 -> 데이터 누수 관련 질문
2. **[대상 오류]** 전체 데이터셋에 fit/transform을 한 경우 -> 데이터 오염 관련 질문
3. **[근거 부족]** 로직은 맞으나 구체적인 공학적 이유가 결여된 경우 -> 'Why'를 묻는 질문
4. **[논리 완벽]** 완벽한 설계인 경우 -> 데이터 드리프트 등 '확장 상황' 대응 질문

# Python 변환(Mapping) 원칙 (CRITICAL)
- **핵심 로직 흐름만 시각화**: Import 문, 데이터 로드, 불필요한 설정 코드는 모두 제외하고 사용자가 작성한 **분할-학습-변환**의 핵심 흐름만 파이썬 구문으로 보여주세요.
- **엄격한 매핑**: 사용자가 적은 '의사코드 문장' 하나하나가 파이썬의 어떤 구문으로 치환되는지 보여주어야 합니다.
- **빈칸/생략 존중**: 사용자가 특정 단계를 누락했다면 파이썬 코드에서도 해당 부분을 `# [누락] 이 단계에 대한 설계가 없습니다` 와 같이 표기하여 자신의 설계를 돌아보게 하세요.
- **강제 완성 금지**: 사용자가 언급하지 않은 라이브러리나 로직을 AI가 임의로 추가하여 '완벽한 코드'를 만들어주지 마세요. 사용자의 논리 그대로를 파이썬으로 옮기는 것이 목적입니다.
- **주석 활용**: 사용자의 의사코드가 파이썬의 어떤 부분에 해당하는지 주석으로 매핑 결과를 명확히(e.g., `# [의사코드 대응] ...`) 보여주세요.

# 출력 형식 (반드시 JSON)
{
  "overall_score": 0, // 85점 만점 기준
  "persona_name": "판정된 페르소나",
  "one_line_review": "한 줄 총평",
  "dimensions": {
    "design": { "score": 25, "basis": "한줄 평", "improvement": "개선방법" },
    "consistency": { "score": 20, "basis": "한줄 평", "improvement": "개선방법" },
    "implementation": { "score": 10, "basis": "한줄 평", "improvement": "개선방법" },
    "edge_case": { "score": 15, "basis": "한줄 평", "improvement": "개선방법" },
    "abstraction": { "score": 15, "basis": "한줄 평", "improvement": "개선방법" }
  },
  "deep_dive": {
    "title": "꼬리질문: 논리 허점 탐색",
    "question": "의사코드의 XX 단계가 모호합니다. 이 경우 발생할 수 있는 공학적 문제는?",
    "options": [
      { "id": 1, "text": "선택지 1", "is_correct": true, "feedback": "정답 해설" },
      { "id": 2, "text": "선택지 2", "is_correct": false, "feedback": "오답 해설" },
      { "id": 3, "text": "선택지 3", "is_correct": false, "feedback": "오답 해설" },
      { "id": 4, "text": "선택지 4", "is_correct": false, "feedback": "오답 해설" }
    ]
  },
  "converted_python": "사용자의 의사코드를 그대로 파이썬 구문으로 매핑한 코드",
  "python_feedback": "사용자 설계의 파이썬 변환 시 발생한 논리적 모순점",
  "senior_advice": "시니어의 핵심 조언",
  "strengths": [],
  "weaknesses": []
"""

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # 또는 AllowAny
def evaluate_pseudocode_5d(request):
    """
    5차원 메트릭 기반 의사코드 평가
    
    POST /api/core/pseudocode/evaluate-5d
    
    Request Body:
    {
        "quest_id": 1,
        "quest_title": "전처리 데이터 누수 방지",
        "pseudocode": "사용자 의사코드",
        "validation_rules": {...},
        "rule_result": {
            "score": 75,
            "concepts": ["data_split", "fit_train"],
            "warnings": [...]
        }
    }
    
    Response:
    {
        "overall_score": 85,
        "dimensions": {...},
        "strengths": [...],
        "weaknesses": [...]
    }
    """
    try:
        # Request 데이터 추출
        quest_id = request.data.get('quest_id')
        quest_title = request.data.get('quest_title')
        pseudocode = request.data.get('pseudocode')
        rule_result = request.data.get('rule_result', {})
        
        # 필수 필드 검증
        if not all([quest_title, pseudocode]):
            return Response(
                {'error': 'quest_title and pseudocode are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 포기/무성의 응답 시 '아키텍처 복기 모드' (2026-02-13 고도화)
        technical_keywords = ['split', 'fit', 'transform', '분할', '학습', '변환', '나누', '기준', '격리', '일관', '누수', 'leakage']
        has_tech = any(kw in pseudocode.lower() for kw in technical_keywords)
        
        if len(pseudocode.strip()) < 15 or (not has_tech and len(pseudocode.strip()) < 30):
            return Response(
                {
                    'overall_score': 15,
                    'is_low_effort': True,
                    'persona_name': "성찰하는 분석가",
                    'one_line_review': "직접 설계하기 어렵다면, 아키텍트의 청사진을 보고 흐름을 분석해 봅시다.",
                    'dimensions': generate_low_score_dimensions("복기 학습 모드 전환"),
                    'strengths': [],
                    'weaknesses': ["설계 본인 작성 누락", "모범 사례 분석 필요"],
                    'senior_advice': "설계가 막힐 때는 잘 짜여진 코드를 역으로 추적(Reverse Engineering)하는 것이 가장 빠릅니다. 오른쪽의 [아키텍트 청사진]을 읽고 아래 질문의 답을 찾아보세요.",
                    'python_feedback': "아키텍트의 설계 핵심 포인트: '전처리 전 분할(Isolation)' -> '훈련 데이터 기준 fit(Anchor)' -> '일관된 적용(Consistency)' 순서를 확인하세요.",
                    'converted_python': "# [아키텍트 청사진 - Blueprint]\nimport pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.preprocessing import StandardScaler\n\n# 1. 격리(Isolation): 전처리 전 데이터를 분할하여 미래 정보를 차단\ntrain_data, test_data = train_test_split(data, test_size=0.2)\n\n# 2. 기준점(Anchor): 훈련 데이터에서만 평균/표준편차를 계산\nscaler = StandardScaler()\nscaler.fit(train_data)\n\n# 3. 일관성(Consistency): 확정된 기준을 훈련/테스트 모두에 동일하게 적용\ntrain_scaled = scaler.transform(train_data)\ntest_scaled = scaler.transform(test_data)",
                    'tail_question': {
                        "should_show": True,
                        "reason": "아키텍처 복기 학습",
                        "question": "위 청사진 코드에서 '데이터 누수(Leakage)'를 막기 위해 가장 먼저 수행한 '격리' 조치는 무엇인가요?",
                        "options": [
                            { "id": 1, "text": "데이터를 Train/Test로 분할하는 것", "is_correct": True, "feedback": "딩동댕! 전처리 도구가 테스트 데이터를 보기 전에 물리적으로 벽을 세우는 것이 격리의 시작입니다." },
                            { "id": 2, "text": "StandardScaler를 생성하는 것", "is_correct": False, "feedback": "도구 생성은 준비 단계일 뿐, 격리는 '데이터 분할' 시점에 일어납니다." },
                            { "id": 3, "text": "훈련 데이터를 transform 하는 것", "is_correct": False, "feedback": "그것은 일관성 유지 단계입니다." },
                            { "id": 4, "text": "테스트 데이터로 fit 하는 것", "is_correct": False, "feedback": "그것은 오히려 데이터 누수를 유발하는 치명적 행위입니다!" }
                        ]
                    }
                },
                status=status.HTTP_200_OK
            )
        
        # LLM 평가 및 Python 변환 호출
        request_python_conversion = request.data.get('request_python_conversion', False)
        
        llm_result = call_llm_evaluation(
            quest_title=quest_title,
            pseudocode=pseudocode,
            rule_score=rule_result.get('score', 0),
            rule_concepts=rule_result.get('concepts', []),
            user_diagnostic=request.data.get('user_diagnostic', {}),
            request_python_conversion=request_python_conversion
        )
        
        # 최종 점수는 프론트에서 Rule(15) + LLM(85)를 합산하여 100점 만점으로 만듦
        
        return Response(llm_result, status=status.HTTP_200_OK)
        
    except openai.OpenAIError as e:
        # OpenAI API 에러
        return Response(
            {
                'error': 'LLM service unavailable',
                'detail': str(e),
                'fallback': True
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
        
    except Exception as e:
        # 기타 에러
        return Response(
            {
                'error': 'Internal server error',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def call_llm_evaluation(quest_title: str, pseudocode: str, rule_score: int, rule_concepts: list, user_diagnostic: dict = None, request_python_conversion: bool = False) -> Dict[str, Any]:
    """
    OpenAI API를 호출하여 5차원 평가 수행
    """
    # OpenAI 클라이언트 초기화
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # User 프롬프트 생성
    user_prompt = f"""
# 문제
{quest_title}

# 학생이 작성한 의사코드
{pseudocode}

# 학생이 직접 분석한 진단 결과 (학습 일관성 평가용)
- Phase 1 (원인 분석 - 서술/객관): {user_diagnostic.get('phase1', '없음') if user_diagnostic else '없음'}
- Phase 2 (전술 설계 - 서술/객관): {user_diagnostic.get('phase2', '없음') if user_diagnostic else '없음'}
- Phase 3 (전술 시퀀스 - 정렬형): {user_diagnostic.get('phase3', '없음') if user_diagnostic else '없음'}

# 규칙 기반 사전 검증 결과 (참고용)
- 규칙 점수: {rule_score}/100점
- 포함된 개념: {', '.join(rule_concepts) if rule_concepts else '없음'}

# 평가 요청
위 의사코드를 5차원 메트릭으로 평가하고, 반드시 JSON 형식으로만 출력하세요.
특히 **Coherence (정합성)** 차원에서는 '학생이 진단 단계(Phase 1~3)에서 도출한 결론/전술이 의사코드에 일관되게 반영되었는지'를 최우선으로 검증하세요. 진단 단계와 의사코드가 모순될 경우 Coherence 점수를 대폭 감점하고 상세 이유를 basis에 적어주세요.

JSON 형식:
{{
  "overall_score": 0-85 정수,
  "persona_name": "판정된 페르소나 명칭",
  "one_line_review": "한 줄 총평",
  "dimensions": {{
    "coherence": {{
      "score": 0-100 정수,
      "basis": "평가 근거 (1-2문장, 한글)",
      "specific_issue": "발견된 문제 (없으면 null)",
      "improvement": "구체적 개선 방법 (없으면 null)"
    }},
    "abstraction": {{ ... (동일 구조) }},
    "exception_handling": {{ ... }},
    "implementation": {{ ... }},
    "architecture": {{ ... }}
  }},
  "strengths": ["강점1", "강점2"],
  "weaknesses": ["약점1", "약점2"],
  "converted_python": "변환된 Python 코드 (문자열)",
  "python_feedback": "Python 변환 관련 피드백 (80점 미만일 때 꼬리질문 힌트용)",
  "senior_advice": "시니어 아키텍트의 전문적인 조언 (한글, 100자 이내. 따뜻하지만 냉철한 피드백)"
}}

**중요**: 
- overall_score는 5개 차원 점수의 평균
- 키워드만 나열한 경우 abstraction은 40점 이하
- 구체적인 개선 방법을 제시하세요
- 의사코드를 기반으로 실행 가능한 Python 코드로 변환하여 converted_python에 담아주세요.
"""
    
    # OpenAI API 호출 (최대 2회 재시도)
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # 또는 gpt-4
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},  # JSON 모드 강제
                temperature=0.7,
                max_tokens=1500,
                timeout=30  # 30초로 상향
            )
            
            # JSON 파싱
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            # 검증
            if not validate_llm_response(result):
                raise ValueError("Invalid LLM response structure")
            
            return result
            
        except (openai.APITimeoutError, openai.APIConnectionError) as e:
            if attempt < max_retries - 1:
                time.sleep(1)  # 1초 대기 후 재시도
                continue
            raise
        
        except json.JSONDecodeError as e:
            # JSON 파싱 실패 - 재시도
            if attempt < max_retries - 1:
                continue
            # 최종 실패 시 Fallback
            return generate_fallback_response(rule_score)
    
    # 모든 재시도 실패
    return generate_fallback_response(rule_score)


def validate_llm_response(response: Dict[str, Any]) -> bool:
    """
    LLM 응답 구조 검증
    """
    required_keys = ['overall_score', 'dimensions', 'strengths', 'weaknesses']
    if not all(key in response for key in required_keys):
        return False
    
    dimensions = response.get('dimensions', {})
    required_dims = ['design', 'consistency', 'implementation', 'edge_case', 'abstraction']
    if not all(dim in dimensions for dim in required_dims):
        return False
    
    # 각 차원이 score, basis를 가지고 있는지 확인
    for dim in required_dims:
        if 'score' not in dimensions[dim] or 'basis' not in dimensions[dim]:
            return False
    
    return True


def generate_fallback_response(rule_score: int) -> Dict[str, Any]:
    """
    LLM 실패 시 Fallback 응답 생성 (규칙 기반)
    주의: 최종 점수는 AI(85) + Rule(15) 임을 고려하여 AI 몫(85)에 대한 점수를 반환함.
    """
    # rule_score(100만점)를 85점 스케일로 변환
    base_ai_score = int(rule_score * 0.85)

    return {
        "overall_score": base_ai_score,
        "persona_name": "평가중인 아키텍트",
        "one_line_review": "AI 평가 엔진 일시 장애로 기본 규칙 점수가 부여되었습니다.",
        "dimensions": {
            "design": {
                "score": int(base_ai_score * 0.25 / 0.85),
                "basis": "규칙 기반 추정 (LLM 평가 실패)",
                "improvement": "서비스 복구 후 정밀 진단을 받아보세요"
            },
            "consistency": {
                "score": int(base_ai_score * 0.20 / 0.85),
                "basis": "규칙 기반 추정",
                "improvement": None
            },
            "implementation": {
                "score": int(base_ai_score * 0.10 / 0.85),
                "basis": "규칙 기반 추정",
                "improvement": None
            },
            "edge_case": {
                "score": int(base_ai_score * 0.15 / 0.85),
                "basis": "규칙 기반 추정",
                "improvement": None
            },
            "abstraction": {
                "score": int(base_ai_score * 0.15 / 0.85),
                "basis": "규칙 기반 추정",
                "improvement": None
            }
        },
        "strengths": ["규칙 기반 검증 통과"],
        "weaknesses": ["AI 평가 서비스 일시 장애"],
        "converted_python": "# [시스템 알림] 현재 AI 변환 서비스가 혼잡합니다.\n# 잠시 후 다시 시도하거나, 미션 조건을 다시 한 번 확인해 주세요.",
        "python_feedback": "구조적 설계 순서(격리 -> 기준점 -> 일관성)를 의사코드에 명확히 적어주시면 변환이 원활해집니다.",
        "fallback": True
    }


def generate_low_score_dimensions(reason: str) -> Dict[str, Any]:
    """
    낮은 점수용 차원 생성 (새로운 5D 이름)
    """
    return {
        "design": { "score": 5, "basis": reason, "improvement": "처음부터 다시 설계해 보세요" },
        "consistency": { "score": 5, "basis": reason, "improvement": None },
        "implementation": { "score": 5, "basis": reason, "improvement": None },
        "edge_case": { "score": 5, "basis": reason, "improvement": None },
        "abstraction": { "score": 5, "basis": reason, "improvement": None }
    }


# ===========================
# 추가: AI 프록시 (기존에 있을 가능성 높음)
# ===========================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_proxy(request):
    """
    범용 OpenAI API 프록시
    
    POST /api/core/ai-proxy/
    
    Request Body:
    {
        "model": "gpt-4o-mini",
        "messages": [...],
        "max_tokens": 200,
        "temperature": 0.7
    }
    
    Response:
    {
        "content": "LLM 응답"
    }
    """
    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        model = request.data.get('model', 'gpt-4o-mini')
        messages = request.data.get('messages', [])
        max_tokens = request.data.get('max_tokens', 500)
        temperature = request.data.get('temperature', 0.7)
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=10
        )
        
        return Response({
            'content': response.choices[0].message.content
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )