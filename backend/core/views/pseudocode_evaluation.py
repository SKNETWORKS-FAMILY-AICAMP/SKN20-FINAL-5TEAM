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


SYSTEM_PROMPT = """당신은 AI 기반 데이터 과학 설계 평가 전문가입니다.
# 평가 철학
- 정답 채점 ❌ -> 공학적 사고력 평가 ✅
- 단순 키워드 매칭이 아닌 데이터 누수(Data Leakage) 방지 원칙 준수 여부 검증
- 사용자의 의사코드를 파이썬 코드로 '매핑(Mapping)'하여 논리적 허점을 시각화

# 아키텍처 평가 체계 (총 100점 만점)

## 1. 기초 설계 단계: "논리의 뼈대" (30점)
- **Abstraction (추상화, 15점)**: 3대 키워드(격리/Isolation, 기준점/Anchor, 일관성/Consistency)를 사용하여 논리를 구조화했는가?
- **Sequence/Rule (논리 순서, 15점)**: 필수 키워드 포함 및 물리적 연산 순서(데이터 분할 -> 기준값 추출)가 올바른가?

## 2. 구현 및 위기 대응 단계: "실제 구현 및 대응" (50점)
- **Implementation (구현력, 10점)**: 의사코드가 실제 파이썬 로직으로 파싱 및 변환 가능한 수준인가?
- **Design (설계력, 25점)**: Tail Question(MCQ)을 통해 사용자의 설계와 변환된 코드 사이의 논리적 개연성을 검증.
- **Edge Case (예외처리, 15점)**: Deep Dive 시나리오(데이터 드리프트 등)를 통해 확장 상황에 대한 대응력을 검증.

## 3. 종합 평가: "누수 방지 무결성" (20점)
- **Consistency (정합성, 20점)**: 설계부터 구현, 위기 대응까지 '데이터 누수 방지 원칙'이 일관되게 유지되었는지 LLM이 최종 검토.

# 질문 생성 및 출력 가이드
- **[Trigger Question]**: 사용자의 설계 결점(순서 오류, 대상 오류 등)을 정확히 저격하는 객관식 문제를 생성하세요.
- **[정답 일관성]**: 생성하는 4개 선택지 중 정답(is_correct: true)은 반드시 단 하나여야 함.
- **[JSON Output]**: 모든 점수의 합은 100점이 되어야 하며, 각 지표의 근거(basis)를 상세히 작성하세요.

# 출력 형식 (반드시 JSON)
{
  "overall_score": 0, // 85점 만점 기준 (각 지표 합산)
  "persona_name": "판정된 페르소나",
  "one_line_review": "한 줄 총평",
  "dimensions": {
    "design": { "score": 25, "basis": "근거", "improvement": "개선" },
    "consistency": { "score": 20, "basis": "근거", "improvement": "개선" },
    "implementation": { "score": 10, "basis": "근거", "improvement": "개선" },
    "edge_case": { "score": 15, "basis": "근거", "improvement": "개선" },
    "abstraction": { "score": 15, "basis": "근거", "improvement": "개선" }
  },
  "tail_question": {
    "should_show": false, // 80점 미만일 때만 true
    "question": "약점 보완 질문",
    "options": [
      { "id": 1, "text": "선택지", "is_correct": true, "feedback": "해설" },
      { "id": 2, "text": "선택지", "is_correct": false, "feedback": "해설" },
      { "id": 3, "text": "선택지", "is_correct": false, "feedback": "해설" },
      { "id": 4, "text": "선택지", "is_correct": false, "feedback": "해설" }
    ]
  },
  "deep_dive": {
    "title": "꼬리질문: [시나리오명]",
    "question": "80점 이상일 때의 심화 질문",
    "options": [
      { "id": 1, "text": "선택지", "is_correct": true, "feedback": "해설" },
      { "id": 2, "text": "선택지", "is_correct": false, "feedback": "해설" },
      { "id": 3, "text": "선택지", "is_correct": false, "feedback": "해설" },
      { "id": 4, "text": "선택지", "is_correct": false, "feedback": "해설" }
    ]
  },
  "converted_python": "매핑된 파이썬 코드",
  "python_feedback": "논리적 모순점 피드백",
  "senior_advice": "시니어의 조언",
  "strengths": ["강점1", "강점2"],
  "weaknesses": ["약점1", "약점2"]
}
"""

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # 또는 AllowAny
def evaluate_pseudocode_5d(request):
    """
    5차원 메트릭 기반 의사코드 평가
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
        
        # [2026-02-14 수정] 비속어 및 무의미한 입력 필터링 로직 추가
        # 교육적 환경 유지를 위해 부적절한 언어 및 무성의한 입력을 감지합니다.
        vulgar_words = ['시발', '씨발', '개새끼', '병신', '미친', '노답', '존나', '지랄']
        meaningless_chars = ['ㅋ', 'ㅎ', '?', '!', '.', ',', ' ']
        
        # 1. 비속어 검사
        has_vulgar = any(word in pseudocode for word in vulgar_words)
        
        # 2. 실질적 내용 검사 (특수문자/공백 제외한 글자 수)
        clean_text = "".join([c for c in pseudocode if c not in meaningless_chars])
        is_too_short = len(clean_text) < 5
        
        # 기술 키워드 포함 여부 확인
        technical_keywords = ['split', 'fit', 'transform', '분할', '학습', '변환', '나누', '기준', '격리', '일관', '누수', 'leakage']
        has_tech = any(kw in pseudocode.lower() for kw in technical_keywords)
        
        # 필터링 조건: 비속어 포함 OR (내용이 너무 짧고 기술 키워드 없음)
        if has_vulgar or (is_too_short and not has_tech):
            review_message = "건전한 학습 환경을 위해 바른 언어를 사용해 주세요." if has_vulgar else "직접 설계하기 어렵다면, 아키텍트의 청사진을 보고 흐름을 분석해 봅시다."
            persona = "주의 깊은 설계자" if has_vulgar else "성찰하는 분석가"
            
            return Response(
                {
                    'overall_score': 15,
                    'is_low_effort': True,
                    'is_vulgar': has_vulgar,
                    'persona_name': persona,
                    'one_line_review': review_message,
                    'dimensions': generate_low_score_dimensions("복기 학습 모드 전환 (입력 부적절)"),
                    'strengths': [],
                    'weaknesses': ["설계 본인 작성 누락", "모범 사례 분석 필요"],
                    'senior_advice': "설계가 막힐 때는 잘 짜여진 코드를 역으로 추적하는 것이 가장 빠릅니다. 아키텍트의 청사진을 참고해 보세요.",
                    'python_feedback': "아키텍처의 핵심: '격리(Isolation)' -> '기준점(Anchor)' -> '일관성(Consistency)'",
                    'converted_python': "# [아키텍트 청사진]\n# 1. Isolation: train_test_split\n# 2. Anchor: scaler.fit(train)\n# 3. Consistency: scaler.transform(train/test)\n\nimport pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.preprocessing import StandardScaler\n\n# 데이터 로드 및 분할 (Isolation)\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)\n\n# 스케일러 정의 및 학습 데이터로 기준점 설정 (Anchor)\nscaler = StandardScaler()\nscaler.fit(X_train)\n\n# 학습 및 테스트 데이터에 동일 기준 적용 (Consistency)\nX_train_scaled = scaler.transform(X_train)\nX_test_scaled = scaler.transform(X_test)",
                    'tail_question': {
                        "should_show": True,
                        "question": "데이터 누수(Leakage)를 방지하기 위해 전처리 도구가 Test 데이터를 보기 전에 가장 먼저 해야 할 일은?",
                        "options": [
                            { "id": 1, "text": "데이터를 Train/Test로 격리하는 것", "is_correct": True, "feedback": "정답입니다! 물리적 격리가 최우선입니다." },
                            { "id": 2, "text": "전체 데이터를 정규화하는 것", "is_correct": False, "feedback": "누수의 주범입니다!" },
                            { "id": 3, "text": "학습을 시작하는 것", "is_correct": False, "feedback": "전처리가 먼저입니다." },
                            { "id": 4, "text": "테스트 데이터로 fit 하는 것", "is_correct": False, "feedback": "치명적인 오류입니다." }
                        ]
                    },
                    'deep_dive': {
                        "title": "아키텍처 복기 학습",
                        "question": "설계가 막힐 때는 청사진을 보고 논리를 역추적하는 것이 중요합니다. 위 질문의 정답을 아시겠나요?",
                        "options": [
                            { "id": 1, "text": "데이터 격리", "is_correct": True, "feedback": "맞습니다!" },
                            { "id": 2, "text": "정규화", "is_correct": False, "feedback": "아닙니다." },
                            { "id": 3, "text": "모델 학습", "is_correct": False, "feedback": "아닙니다." },
                            { "id": 4, "text": "테스트 데이터 사용", "is_correct": False, "feedback": "절대 안 됩니다." }
                        ]
                    }
                },
                status=status.HTTP_200_OK
            )
        
        llm_result = call_llm_evaluation(
            quest_title=quest_title,
            pseudocode=pseudocode,
            rule_score=rule_result.get('score', 0),
            rule_concepts=rule_result.get('concepts', []),
            user_diagnostic=request.data.get('user_diagnostic', {}),
            request_python_conversion=request.data.get('request_python_conversion', False)
        )
        
        # [2026-02-14 수정] 취약 지표별 맞춤형 유튜브 영상 큐레이션 통합
        # 5차원 평가 결과 중 가장 점수가 낮은 지표를 추출하여 검색어를 매핑합니다.
        try:
            from core.utils.youtube_helper import search_youtube_videos
            
            dimensions = llm_result.get('dimensions', {})
            if dimensions:
                # 가장 낮은 점수의 지표 찾기
                weakest_dim = min(dimensions.items(), key=lambda x: x[1].get('score', 100))[0]
                
                query_map = {
                    'design': '머신러닝 파이프라인 설계 원칙',
                    'consistency': 'Data Leakage(데이터 누수) 방지 가이드',
                    'implementation': 'Scikit-learn fit transform 활용법',
                    'edge_case': 'MLOps 데이터 드리프트 대응 실무',
                    'abstraction': '공학적 문제 구조화 및 의사코드 작성'
                }
                
                query = query_map.get(weakest_dim, '데이터 과학 전처리 원칙')
                llm_result['recommended_videos'] = search_youtube_videos(query, max_results=3)
        except Exception as yt_err:
            print(f"[YouTube Curation Error] {str(yt_err)}")
            llm_result['recommended_videos'] = []
            
        return Response(llm_result, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        print(f"[5D Evaluation Error] {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': 'Internal server error', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def call_llm_evaluation(quest_title: str, pseudocode: str, rule_score: int, rule_concepts: list, user_diagnostic: dict = None, request_python_conversion: bool = False) -> Dict[str, Any]:
    """
    OpenAI API를 호출하여 5차원 평가 수행
    """
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    user_prompt = f"""
# 미션
{quest_title}

# 학생의 의사코드
{pseudocode}

# 진단 단계 답변 (Coherence 평가용)
{json.dumps(user_diagnostic, ensure_ascii=False) if user_diagnostic else '없음'}

# 평가 요청
위 의사코드를 5차원 메트릭(design, consistency, implementation, edge_case, abstraction)으로 평가하고 JSON으로 출력하세요.
- **design (25점)**: 논리적 개연성 및 흐름
- **consistency (20점)**: 누수 방지 원칙 준수 여부 (진단 답변과의 일관성 포함)
- **implementation (10점)**: 코드 변환 가능성
- **edge_case (15점)**: 예외 및 확장 상황 고려
- **abstraction (15점)**: 구조화 및 전문 용어 사용

**중요**: 
- overall_score는 5개 차원 점수의 총합 (85점 만점)
- 키워드만 나열한 경우 abstraction은 5점 이하로 감점
- **[질문 분기]**: 점수가 80점 미만이면 `tail_question`을 생성하고 `should_show`를 true로, 80점 이상이면 `deep_dive`를 생성하고 `tail_question`의 `should_show`는 false로 설정하세요.
- **[정답 일관성]**: 모든 질문의 선택지(options) 중 정답(`is_correct: true`)은 반드시 단 하나여야 하며, 나머지는 `false`여야 합니다.
- 의사코드를 기반으로 실행 가능한 Python 코드로 변환하여 `converted_python`에 담아주세요.

반드시 JSON 형식으로만 응답해야 합니다.
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
        "converted_python": "# [시스템 알림] AI 분석 시간이 초과되어 기본 청사진을 제공합니다.\n# 1. Isolation: train_test_split\n# 2. Anchor: scaler.fit(train)\n# 3. Consistency: scaler.transform(test)\n\nimport pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.preprocessing import StandardScaler\n\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)\nscaler = StandardScaler()\nscaler.fit(X_train)\nX_test_scaled = scaler.transform(X_test)",
        "python_feedback": "AI 엔진이 혼잡하여 상세 피드백을 생성하지 못했습니다. 설계의 3대 원칙인 '격리-기준점-일관성'을 확인해 보세요.",
        "tail_question": {
            "should_show": True,
            "question": "데이터 누수를 방지하기 위해 가장 먼저 수행해야 할 단계는 무엇인가요?",
            "options": [
                { "id": 1, "text": "훈련/테스트 데이터 격리", "is_correct": True, "feedback": "맞습니다! 격리가 최우선입니다." },
                { "id": 2, "text": "전체 데이터 정규화", "is_correct": False, "feedback": "누수의 원인이 됩니다." },
                { "id": 3, "text": "모델 학습 시작", "is_correct": False, "feedback": "전처리가 먼저입니다." },
                { "id": 4, "text": "테스트 데이터로 fit", "is_correct": False, "feedback": "절대 안 됩니다." }
            ]
        },
        "one_line_review": "AI 분석 중 시간 초과가 발생하여 룰 기반 점수로 우선 평가를 진행합니다.",
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