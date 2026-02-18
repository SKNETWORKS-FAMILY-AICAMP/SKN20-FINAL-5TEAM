import math
from collections import Counter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import openai
import json
import time
from typing import Dict, Any
from core.utils.pseudocode_validator import PseudocodeValidator
from core.utils.mission_rules import VALIDATION_RULES
from core.models import UserProfile
# [2026-02-18 상세] 평가 결과를 데이터베이스에 자동으로 기록하기 위한 공통 서비스 임포트
from core.services.activity_service import save_user_problem_record
import logging

logger = logging.getLogger(__name__)

# [2026-02-18 수정] ID 정규화 함수 및 청사진 구성 고도화 (Antigravity)
def normalize_quest_id(quest_id):
    """
    다양한 형식의 quest_id를 MISSION_BLUEPRINTS 키로 정규화
    예: 'unit01_01' -> '1', 'QUEST_01' -> '1'
    """
    if not quest_id: return "1"
    q_str = str(quest_id)
    # unit01_01 형식이면 숫자만 추출
    if q_str.startswith('unit'):
        import re
        match = re.search(r'unit(\d+)', q_str)
        if match: return str(int(match.group(1)))
    # QUEST_01 형식이면 숫자만 추출
    if q_str.startswith('QUEST_'):
        return str(int(q_str.replace('QUEST_', '')))
    return q_str

# [2026-02-14 추가] 미션별 정답 청사진 (컨텐츠 맥락 부족 해결)
MISSION_BLUEPRINTS = {
    "1": {
        "mission_goal": "데이터 전처리 과정에서의 누수(Leakage) 방지",
        "target_dataset": "Titanic Survival Dataset (age, fare 등)",
        "critical_constraints": [
            "1. Isolation: train_test_split이 Scaler 적용보다 먼저 나와야 함",
            "2. Anchor: scaler.fit은 오직 X_train 데이터에만 수행해야 함",
            "3. Consistency: X_test는 오직 transform만 수행해야 함 (fit 금지)"
        ],
        "required_keywords": ["split", "fit", "transform", "train", "test"],
        "model_answer_python": "# [청사적 격리 및 기준점 보호 파이프라인]\nimport pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.preprocessing import StandardScaler\n\n# 1. Isolation (격리)\ntrain_df, test_df = train_test_split(df, test_size=0.2)\n\n# 2. Anchor (기준점 설정): 오직 학습 데이터로만!\nscaler = StandardScaler()\nscaler.fit(train_df[['age', 'fare']])\n\n# 3. Consistency (일관성): 동일한 기준 적용\nX_train_scaled = scaler.transform(train_df[['age', 'fare']])\nX_test_scaled = scaler.transform(test_df[['age', 'fare']])",
        "blueprint_steps": [
            {"id": "s1", "python": "train_df, test_df = train_test_split(df, test_size=0.2)", "pseudo": "먼저 데이터를 학습용과 검증용으로 물리적 격리(Isolation)한다."},
            {"id": "s2", "python": "scaler.fit(train_df[['age', 'fare']])", "pseudo": "학습 데이터(train)에서만 통계량을 추출하여 기준점(Anchor)을 설정한다."},
            {"id": "s3", "python": "scaler.transform(test_df[['age', 'fare']])", "pseudo": "테스트 데이터(test)에는 fit 없이 transform만 적용하여 일관성(Consistency)을 유지한다."}
        ]
    }
}
# 하위 호환성 유지 및 기본값 설정
MISSION_BLUEPRINTS["QUEST_01"] = MISSION_BLUEPRINTS["1"]
MISSION_BLUEPRINTS["default"] = MISSION_BLUEPRINTS["1"]

# [2026-02-14 추가] 엔트로피 기반 입력 품질 검사 (부실한 필터링 해결)
def calculate_entropy(text: str) -> float:
    """문자열의 정보 밀도(엔트로피)를 계산하여 무의미한 나열을 감지"""
    if not text: return 0
    counter = Counter(text)
    probs = [count / len(text) for count in counter.values()]
    return -sum(p * math.log2(p) for p in probs)

def is_meaningful_input(text: str) -> bool:
    """성의 있는 입력인지 3중 검증"""
    clean_text = "".join([c for c in text if c.isalnum()])
    # 1. 길이 검사
    if len(clean_text) < 5: return False
    # 2. 엔트로피 검사 (낮은 엔트로피는 'aaaaa' 같은 무의미한 반복을 의미)
    if calculate_entropy(text) < 2.0 and len(text) > 10: return False
    return True

SYSTEM_PROMPT = """당신은 데이터 과학 아키텍처 전문 채점관입니다.
사용자의 [Pseudocode]가 [Mission Blueprint]의 핵심 제약 사항을 준수하는지 평가하십시오.

### [⚠️ 채점 필수 규정: 일관성 유지]
1. **치명적 결함(Leakage) 판정**:
   - 만약 사용자가 [데이터 분리(Split)] 전에 [스케일링/변환(Fit)]을 수행했다면, 이는 **'데이터 누수'**로 판정합니다.
   - **누수 판정 시**: `consistency` 점수는 **0~5점** 사이로 고정하며, `overall_score`는 절대 **40점**을 넘을 수 없습니다. (나머지 지표가 좋아도 상한선 적용)

2. **지표별 배점 (Total 85pts)**:
   - **Consistency (35pts)**: 데이터 격리 원칙 (누수 발생 시 가차 없이 감점)
   - **Design (30pts)**: 파이프라인 논리 흐름
   - **Implementation (10pts)**: 구체성
   - **Abstraction/EdgeCase (각 5pts)**: 전문성 및 안정성

### [🐍 파이썬 거울 반사]
- 사용자가 틀린 순서로 썼다면, **틀린 순서 그대로** 파이썬 코드를 생성하십시오. 수정해 주지 마십시오.

### [출력 형식 (JSON)]
{
  "self_audit": {
    "has_leakage": true/false,
    "is_order_correct": true/false,
    "reason": "점수를 주기 전 자가 진단 결과"
  },
  "overall_score": 0,
  "persona_name": "판정 페르소나",
  "one_line_review": "설계 요약 및 총평",
  "dimensions": {
    "design": { "score": 0, "basis": "근거", "improvement": "개선" },
    "consistency": { "score": 0, "basis": "근거", "improvement": "개선" },
    "implementation": { "score": 0, "basis": "근거", "improvement": "개선" },
    "edge_case": { "score": 0, "basis": "근거", "improvement": "개선" },
    "abstraction": { "score": 0, "basis": "근거", "improvement": "개선" }
  },
  "tail_question": { ... },
  "deep_dive": { ... },
  "converted_python": "...",
  "python_feedback": "기술 분석 피드백",
  "senior_advice": "아키텍트 조언",
  "strengths": [], "weaknesses": []
}
"""

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def evaluate_pseudocode_5d(request):
    """
    고도화된 5차원 메트릭 기반 의사코드 평가
    [개선] AI(85) + Rule(85) / 1.7 = 100점 만점 체계
    """
    try:
        quest_id = request.data.get('quest_id', 'default')
        quest_title = request.data.get('quest_title')
        pseudocode = request.data.get('pseudocode', '')
        
        # [2026-02-18 추가] quest_id 정규화 적용
        normalized_id = normalize_quest_id(quest_id)
        
        # 1. 백엔드 전용 룰 엔진으로 검증 수행 (정규화된 ID 사용)
        rules = VALIDATION_RULES.get(normalized_id, VALIDATION_RULES.get("1"))
        validator = PseudocodeValidator(rules)
        rule_result = validator.validate(pseudocode)
        
        # [2026-02-14 수정] 부실한 필터링 및 포기성 발언 감지 강화
        vulgar_words = ['시발', '씨발', '개새끼', '병신', '미친', '노답', '존나', '지랄', '엠창']
        giveup_keywords = [
            '모르', '몰라', '몰겠', '어렵', '못하', '안됨', '해줘', '?', 'help',
            '글쎄', '나중에', '다음에', '귀찮', '패스', 'pass', 'ㅁㄴㅇㄹ', 'ㄴㄴ'
        ]
        
        has_vulgar = any(word in pseudocode for word in vulgar_words)
        is_giveup = any(word in pseudocode for word in giveup_keywords)
        
        if has_vulgar or is_giveup or not is_meaningful_input(pseudocode):
            review_message = "건전하고 성실한 설계를 부탁드립니다." if has_vulgar else "이것은 설계도가 아닙니다. 기초부터 다시 다져봅시다."
            blueprint = MISSION_BLUEPRINTS.get(normalized_id, MISSION_BLUEPRINTS.get("1"))
            
            # [2026-02-18 상세] 무성의한 입력(Low effort)이나 포기 발언이 감지된 경우의 처리
            # - 사용자 경험을 위해 가이드 메시지를 반환함과 동시에, 시도 기록을 0점으로 저장함
            try:
                # [2026-02-18 상세] 현재 로그인한 사용자의 프로필 정보를 조회함
                profile = UserProfile.objects.get(email=request.user.email)
                
                # [2026-02-18 상세] 공통 서비스를 통해 0점 처리 및 '무성의 입력' 상태를 상세 데이터에 기록함
                save_user_problem_record(
                    user_profile=profile,
                    detail_id=quest_id if quest_id.startswith('unit') else f"unit01{normalized_id.zfill(2)}",
                    score=0,
                    submitted_data={'pseudocode': pseudocode, 'evaluation': 'Low effort / Meaningless input'}
                )
            except Exception as e:
                # [2026-02-18 상세] 저장 중 오류가 발생하더라도 프론트엔드 응답은 유지하여 사용자 흐름을 방해하지 않음
                logger.error(f"Failed to save low-effort Unit 1 record: {str(e)}")

            return Response({
                'overall_score': 0,
                'total_score_100': 0,
                'is_low_effort': True,
                'persona_name': "낙제한 견습생",
                'one_line_review': review_message,
                'dimensions': {
                    "design": {"score": 0, "basis": "포기/무성의", "improvement": "단계별 설계를 다시 시작하세요."},
                    "consistency": {"score": 0, "basis": "원칙 부재", "improvement": "격리 원칙을 처음부터 배우세요."},
                    "implementation": {"score": 0, "basis": "구체성 전무", "improvement": "동사 중심으로 명확히 쓰세요."},
                    "edge_case": {"score": 0, "basis": "측정 불가", "improvement": "예외 상황은 고려되지 않았습니다."},
                    "abstraction": {"score": 0, "basis": "구조 없음", "improvement": "구조화된 표현을 익히세요."}
                },
                'converted_python': blueprint.get("model_answer_python", "# No blueprint found"),
                'python_feedback': "학습을 돕기 위해 해당 미션의 표준 아키텍처(청사진)를 제공합니다. 아래 [청사진 복구 작전]을 통해 논리 흐름을 익혀보세요.",
                'blueprint_steps': blueprint.get("blueprint_steps", []),
                'tail_question': {
                    "should_show": True,
                    "question": f"미션: {blueprint.get('mission_goal', '전처리')}\n[청사적 격리 및 기준점 보호] 논리를 이해하지 못했습니다. 청사진을 보고 올바른 설계를 선택해 보세요.",
                    "context": "청사진 복기 학습",
                    "options": [
                        {"id": 1, "text": "아래 매칭 UI를 사용하여 설계를 완성하세요.", "is_correct": True, "feedback": "학습을 시작합니다."}
                    ]
                }
            }, status=status.HTTP_200_OK)

        # [2026-02-18 수정] 안전한 Blueprint 획득 및 폴백 강화
        blueprint = MISSION_BLUEPRINTS.get(normalized_id, MISSION_BLUEPRINTS.get("1"))

        llm_result = call_llm_evaluation(
            quest_title=quest_title,
            pseudocode=pseudocode,
            blueprint=blueprint,
            rule_score=rule_result.get('score', 0),
            user_diagnostic=request.data.get('user_diagnostic', {})
        )
        
        # [2026-02-14 수정] 점수 산출 권한 서버 회수 및 산식 단일화 
        rule_score_raw = rule_result.get('score', 0)
        rule_score_15 = round(rule_score_raw * 0.15)
        ai_score_85 = llm_result.get('overall_score', 0)
        
        final_100_score = ai_score_85 + rule_score_15
        
        llm_result['total_score_100'] = final_100_score
        llm_result['score_breakdown'] = {
            'ai_score_85': ai_score_85,
            'rule_score_15': rule_score_15,
            'rule_raw_100': rule_score_raw
        }
        llm_result['rule_details'] = rule_result

        # 유튜브 큐레이션 등 후속 처리...
        try:
            from core.utils.youtube_helper import search_youtube_videos
            weakest_dim = min(llm_result['dimensions'].items(), key=lambda x: x[1].get('score', 100))[0]
            query_map = {'design': 'ML 파이프라인 설계', 'consistency': '데이터 누수 방지', 'implementation': 'Sklearn 활용법'}
            llm_result['recommended_videos'] = search_youtube_videos(query_map.get(weakest_dim, 'ML 전처리'), max_results=2)
        except: pass
            
        # [2026-02-18 상세] 정상적인 평가가 완료된 후, 결과를 실시간으로 데이터베이스에 반영함
        try:
            profile = UserProfile.objects.get(email=request.user.email)
            target_detail_id = quest_id if quest_id.startswith('unit') and '_' in quest_id else f"unit01_{normalized_id.zfill(2)}"
            logger.info(f"Attempting to save Unit 1 record: quest_id={quest_id}, target_detail_id={target_detail_id}")
            
            # [2026-02-18 상세] 공통 서비스를 호출하여 다음 항목들을 업데이트함:
            # 1. UserSolvedProblem: 실습 이력 및 획득 점수 저장
            # 2. UserActivity: 전체 누적 포인트 및 랭킹 정산
            # 3. UserProgress: 유닛별 진행률 및 로드맵 노드 해금
            save_user_problem_record(
                user_profile=profile,
                detail_id=target_detail_id,
                score=final_100_score,
                submitted_data={
                    'pseudocode': pseudocode,
                    'evaluation': llm_result
                }
            )
            logger.info(f"Unit 1 record saved successfully for {profile.username}")
        except Exception as e:
            # [2026-02-18 상세] 기록 저장 실패 시 로그를 남기되, 사용자에게는 평가 결과를 우선적으로 보여줌
            logger.error(f"Failed to save Unit 1 record (ID: {target_detail_id}): {str(e)}")

        return Response(llm_result, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def call_llm_evaluation(quest_title, pseudocode, blueprint, rule_score, user_diagnostic=None):
    """OpenAI API를 통해 청사진 기반 정밀 평가 수행"""
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # [2026-02-14 수정] 프롬프트 과부하 해결을 위해 맥락을 구조화하여 전달
    user_prompt = f"""
# [Evaluation Context: Mission Blueprint]
- Goal: {blueprint['mission_goal']}
- Critical Constraints: {", ".join(blueprint['critical_constraints'])}
- Required Keywords: {", ".join(blueprint['required_keywords'])}

# [User Input]
- Title: {quest_title}
- Pseudocode: {pseudocode}
- Diagnostic Context: {json.dumps(user_diagnostic) if user_diagnostic else "N/A"}

# [Task]
위 [Mission Blueprint]의 제약 사항을 얼마나 충실히 설계에 반영했는지 평가하세요.
- AI 점수는 총 85점 만점으로 채점합니다. (지표별 합산)
- 점수 결과에 따라 맞춤형 MCQ(tail_question or deep_dive)를 생성하세요. 
- 입력을 기반으로 실행 가능한 Python 코드로 변환하세요.
"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.7
    )
    return json.loads(response.choices[0].message.content)

def generate_low_score_dimensions(reason):
    """낮은 성의 입력 시 기본 차원 점수 반환"""
    return {dim: {"score": 3, "basis": reason, "improvement": "다시 설계하세요"} 
            for dim in ['design', 'consistency', 'implementation', 'edge_case', 'abstraction']}
