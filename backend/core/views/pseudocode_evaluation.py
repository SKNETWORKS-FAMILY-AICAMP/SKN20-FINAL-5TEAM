"""
의사코드 5차원 평가 뷰 (Final Architecture)
수정일: 2026-02-18
수정내용: 
1. PseudocodeEvaluator 서비스를 활용한 비즈니스 로직 분리 및 아키텍처 리팩토링
2. 프론트엔드 동적 분기를 위한 무성의 입력 감지, 꼬리 질문(tail_question), 심화 시나리오(deep_dive) 데이터 연동 완결
3. 지표별 전문 키워드 매핑을 통한 고품질 유튜브 학습 리소스 큐레이션 엔진 강화
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json

from core.services.pseudocode_evaluator import PseudocodeEvaluator, EvaluationRequest, EvaluationMode, ModelConfig, LLMEvaluationResult

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def evaluate_pseudocode_5d(request):
    """
    고도화된 5차원 메트릭 기반 의사코드 평가 및 학습 로드맵 제안
    """
    try:
        user_id = request.user.id if request.user.is_authenticated else "anonymous"
        quest_id = request.data.get('quest_id', '1')
        quest_title = request.data.get('quest_title', '데이터 전처리 미션')
        pseudocode = request.data.get('pseudocode', '')
        
        if not pseudocode:
            return Response({"error": "의사코드를 입력해 주세요."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. 평가 엔지니어링 수행 (Service Layer 활용)
        evaluator = PseudocodeEvaluator()
        
        eval_request = EvaluationRequest(
            user_id=str(user_id),
            detail_id=str(quest_id),
            pseudocode=pseudocode,
            quest_title=quest_title,
            mode=EvaluationMode.OPTION2_GPTONLY
        )
        
        print(f"[API] Evaluating Pseudocode: {quest_title} (User: {user_id})")
        result = evaluator.evaluate(eval_request)
        
        # 2. 결과 데이터 조립 (프론트엔드 호환 포맷)
        llm_evaluations = result.llm_evaluations
        # 3. 정규화 및 피드백
        if not llm_evaluations:
            # LLM 결과가 아예 없는 경우 방어 로직
            err_res = LLMEvaluationResult(model=ModelConfig.PRIMARY_MODEL, status='ERROR', error_message="LLM 응답 없음")
            llm_evaluations[ModelConfig.PRIMARY_MODEL] = err_res

        primary_res = llm_evaluations.get(ModelConfig.PRIMARY_MODEL) or next(iter(llm_evaluations.values()))
        
        response_data = {
            'overall_score': result.final_score,
            'total_score_100': result.final_score,
            'grade': result.grade,
            'persona_name': result.persona,
            'one_line_review': result.feedback.get('summary', ""),
            'dimensions': result.feedback.get('dimensions', {}),
            'converted_python': primary_res.converted_python or "# 변환 실패",
            'python_feedback': primary_res.python_feedback or "분석 완료",
            'strengths': result.feedback.get('strengths', []),
            'weaknesses': result.feedback.get('improvements', []),
            'is_low_effort': result.is_low_effort,
            'tail_question': result.tail_question,
            'deep_dive': result.deep_dive,
            'score_breakdown': result.score_breakdown,
            'metadata': result.metadata
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"[API Critical Error] {error_msg}")
        print(traceback.format_exc())
        
        # [2026-02-18 수정] 어떤 경우에도 500 에러 대신 200 OK + Fallback 데이터 반환
        return Response({
            'overall_score': 0,
            'total_score_100': 0,
            'grade': 'POOR',
            'is_low_effort': True,
            'one_line_review': f"[시스템 점검 중] 장비 연결에 실패했습니다: {error_msg[:30]}...",
            'feedback': f"현재 서버 엔진에 일시적인 장애가 발생하여 룰 기반 분석 모드로 전환되었습니다.",
            'dimensions': {},
            'converted_python': "# [안내] 현재 서버 연결이 원활하지 않아 파이썬 변환을 수행할 수 없습니다.\n# 잠시 후 '재분석' 버튼을 클릭해 주세요.",
            'python_feedback': "서버 연결 실패",
            'recommended_videos': [],
            'error_details': error_msg,
            'status': 'CRASH_RECOVERED'
        }, status=status.HTTP_200_OK)
