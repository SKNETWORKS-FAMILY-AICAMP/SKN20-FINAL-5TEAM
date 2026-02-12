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


# LLM 프롬프트 (고정)
SYSTEM_PROMPT = """당신은 AI 기반 의사코드 평가 전문가입니다.

# 평가 철학
- 정답 채점 ❌ → 사고력 평가 ✅
- 단순 키워드 매칭이 아닌 논리적 연결성 검증
- 논리적 허점 발견 시 구체적 개선 방안 제시

# 점수 인플레이션 방지 및 엄격한 기준
- **완벽하지 않으면 100점 주지 마세요**
- **키워드만 나열한 경우 40점 이하**
- 점수 분포:
  * 100점: 완벽한 논리와 예외처리
  * 80-99점: 훌륭하지만 사소한 개선점 존재
  * 60-79점: 핵심은 맞지만 디테일 부족
  * 40-59점: 방향은 맞지만 논리적 비약 심함
  * 0-39점: 핵심 오개념 또는 무관한 내용

# 5차원 메트릭 평가 기준
1. **Coherence (정합성, 20%)**: quest_title과 사용자 로직의 일치 여부
   - 문제의 목표를 정확히 이해하고 해결했는가?
   - 설계 의도와 구현 로직이 일치하는가?

2. **Abstraction (추상화, 20%)**: 의사코드의 간결성 및 핵심 로직 표현력
   - 핵심 로직만 간결하게 표현했는가?
   - 불필요한 세부사항을 배제했는가?
   - **단순 키워드 나열이면 40점 이하**

3. **Exception Handling (예외처리, 20%)**: 예외 상황 대응 키워드 및 로직 포함 여부
   - 엣지 케이스를 고려했는가?
   - 예외 상황 처리 로직이 명시되었는가?

4. **Implementation (구현력, 20%)**: 의사코드의 구체성과 논리적 흐름의 명확성
   - 실제 구현 가능한 수준으로 구체적인가?
   - 각 단계가 명확하고 실행 가능한가?

5. **Architecture (설계력, 20%)**: 단계별 연결성 및 아키텍처적 완성도
   - 단계 간 논리적 연결성이 있는가?
   - 전체적인 설계 구조가 견고한가?

# 출력 형식
반드시 JSON 형식으로만 출력하세요. 마크다운, 설명문 등 불필요.

{
  "overall_score": 0,
  "dimensions": {
    "coherence": {
      "score": 0,
      "basis": "평가 근거 (1-2문장)",
      "specific_issue": "발견된 문제 (없으면 null)",
      "improvement": "구체적 개선 방법 (없으면 null)"
    },
    "abstraction": { ... },
    "exception_handling": { ... },
    "implementation": { ... },
    "architecture": { ... }
  },
  "strengths": ["강점1", "강점2"],
  "weaknesses": ["약점1"]
}
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
        
        # 너무 짧은 의사코드 거부
        if len(pseudocode.strip()) < 20:
            return Response(
                {
                    'overall_score': 20,
                    'dimensions': generate_low_score_dimensions("의사코드가 너무 짧습니다"),
                    'strengths': [],
                    'weaknesses': ["의사코드 길이 부족 (최소 20자 필요)"]
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
        
        # 규칙 점수와 LLM 점수 혼합 (Rule 40% + LLM 60%)
        rule_score = rule_result.get('score', 0)
        llm_score = llm_result.get('overall_score', 0)
        
        # 최종 점수는 프론트에서 계산하므로 LLM 점수만 반환
        # (프론트에서 (rule * 0.4) + (llm * 0.6) 계산)
        
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
  "overall_score": 0-100 정수,
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
  "python_feedback": "Python 변환 관련 피드백 (80점 미만일 때 꼬리질문 힌트용)"
}}

**중요**: 
- overall_score는 5개 차원 점수의 평균
- 키워드만 나열한 경우 abstraction은 40점 이하
- 구체적인 개선 방법을 제시하세요
- 의사코드를 기반으로 실행 가능한 Python 코드로 변환하여 converted_python에 담아주세요.
"""
    
    # OpenAI API 호출 (최대 3회 재시도)
    max_retries = 3
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
                timeout=15  # 15초 타임아웃
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
    required_dims = ['coherence', 'abstraction', 'exception_handling', 'implementation', 'architecture']
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
    """
    return {
        "overall_score": rule_score,
        "dimensions": {
            "coherence": {
                "score": int(rule_score * 0.9),
                "basis": "규칙 기반 추정 (LLM 평가 실패)",
                "specific_issue": "AI 평가 서비스 일시 장애",
                "improvement": "잠시 후 다시 시도해주세요"
            },
            "abstraction": {
                "score": int(rule_score * 0.8),
                "basis": "규칙 기반 추정",
                "specific_issue": None,
                "improvement": None
            },
            "exception_handling": {
                "score": int(rule_score * 0.7),
                "basis": "규칙 기반 추정",
                "specific_issue": None,
                "improvement": None
            },
            "implementation": {
                "score": rule_score,
                "basis": "규칙 기반 추정",
                "specific_issue": None,
                "improvement": None
            },
            "architecture": {
                "score": int(rule_score * 0.85),
                "basis": "규칙 기반 추정",
                "specific_issue": None,
                "improvement": None
            }
        },
        "strengths": ["규칙 기반 검증 통과"],
        "weaknesses": ["AI 평가 서비스 일시 장애로 정확도 낮음"],
        "fallback": True
    }


def generate_low_score_dimensions(reason: str) -> Dict[str, Any]:
    """
    낮은 점수용 차원 생성
    """
    return {
        "coherence": {
            "score": 20,
            "basis": reason,
            "specific_issue": reason,
            "improvement": "의사코드를 더 자세히 작성하세요"
        },
        "abstraction": {
            "score": 20,
            "basis": reason,
            "specific_issue": None,
            "improvement": None
        },
        "exception_handling": {
            "score": 20,
            "basis": reason,
            "specific_issue": None,
            "improvement": None
        },
        "implementation": {
            "score": 20,
            "basis": reason,
            "specific_issue": None,
            "improvement": None
        },
        "architecture": {
            "score": 20,
            "basis": reason,
            "specific_issue": None,
            "improvement": None
        }
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