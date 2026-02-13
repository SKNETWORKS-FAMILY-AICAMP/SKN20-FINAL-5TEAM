# [수정일: 2026-02-10] 마스터 에이전트(Curriculum Master) 뷰 구현: 사용자의 장기 학습 데이터 분석 및 개인화 가이드 제공
import openai
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from core.models import UserSolvedProblem, UserProfile
from django.shortcuts import get_object_or_404
import json

@method_decorator(csrf_exempt, name='dispatch')
class MasterAgentView(APIView):
    """
    마스터 에이전트(Curriculum Master) 뷰
    사용자의 이전 학습 기록을 종합적으로 분석하여 성취도 리포트와 취약점 개선 방향을 제시합니다.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = get_object_or_404(UserProfile, email=user.email)

        # 1. 사용자의 모든 해결 기록 수집 (최신순)
        # 마스터 에이전트는 사용자가 어떤 고민을 했고 어떤 지적을 받았는지 '기억'해야 합니다.
        solved_problems = UserSolvedProblem.objects.filter(user=profile).select_related('practice_detail__practice').order_by('solved_date')
        
        if not solved_problems.exists():
            return Response({
                "message": "아직 분석할 학습 데이터가 충분하지 않습니다. 미션을 먼저 수행해주세요!",
                "has_data": False
            }, status=status.HTTP_200_OK)

        # 2. 분석을 위한 데이터 정제 (컨텍스트 구축)
        history_context = []
        for sp in solved_problems:
            # [수정일: 2026-02-10] 유닛별 다른 데이터 구조(ai_evaluation vs evaluation) 대응
            submitted = sp.submitted_data if sp.submitted_data else {}
            ai_eval = submitted.get('ai_evaluation') or submitted.get('evaluation') or {}
            
            history_context.append({
                "unit": sp.practice_detail.practice.title,
                "problem": sp.practice_detail.detail_title,
                "score": sp.score,
                "phase": submitted.get('phase', 'UNKNOWN'),
                "metrics": ai_eval.get('metrics') or ai_eval.get('pillarScores') or {},
                "critic": ai_eval.get('analysis') or ai_eval.get('advice') or ai_eval.get('summary') or '기록 없음',
                "date": sp.solved_date.strftime('%Y-%m-%d')
            })

        # 3. 마스터 에이전트 분석 (OpenAI)
        try:
            api_key = settings.OPENAI_API_KEY
            client = openai.OpenAI(api_key=api_key)
            
            system_prompt = """
            당신은 'Super Code Adventure'의 총괄 교육 설계자이자 마스터 아키텍트인 'Curriculum Master'입니다.
            사용자가 지금까지 수행한 여러 유닛의 학습 기록을 보고, 사용자의 성장을 입체적으로 분석하십시오.

            [분석 가이드라인]
            1. 성장 추이: 지표상으로 어떤 부분이 개선되고 있는지 언급하십시오.
            2. 반복되는 취약점: 여러 유닛에서 공통적으로 지적받는 '사고의 구멍'(예: 항상 예외처리를 누락하거나, 추상화가 고질적으로 부족함)을 날카롭게 짚어내십시오.
            3. 유닛 간 연결: 유닛 1에서 배운 개념이 유닛 3에서 어떻게 잘못 적용되거나, 혹은 잘 적용되고 있는지 연결하여 설명하십시오.
            4. 페르소나: 엄격하면서도 사용자의 성장을 진심으로 기뻐하는 대스승의 말투를 사용하십시오. (~하오, ~하게나, 혹은 장중한 마법사 톤)

            반드시 아래 JSON 형식으로 응답하십시오.
            {
              "summary": "전체 성취도 요약 (3-4문장)",
              "growth_points": ["성장한 점 1", "성장한 점 2"],
              "weakness_alert": "반복되는 치명적 취약점 지적",
              "unit_analysis": [
                {"unit": "유닛명", "comment": "해당 유닛에서의 활약 비평"}
              ],
              "next_step_advice": "다음에 집중해야 할 구체적인 학습 방향",
              "overall_grade": "SSS/SS/S/A/B/C"
            }
            """

            user_msg = f"사용자 '{profile.user_nickname or profile.email}'의 학습 히스토리 데이터:\n{json.dumps(history_context, ensure_ascii=False)}"

            response = client.chat.completions.create(
                model="gpt-4o-mini", # 분석 데이터가 많을 수 있으므로 가성비 좋은 모델 사용
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                response_format={"type": "json_object"}
            )

            master_report = json.loads(response.choices[0].message.content)
            
            return Response({
                "report": master_report,
                "history_count": len(history_context),
                "has_data": True
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"[MasterAgent] Error: {str(e)}")
            return Response({
                "error": "마스터 에이전트와 연결이 원활하지 않습니다.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
