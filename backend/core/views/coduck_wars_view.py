from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from core.agents.scenario_agent import ScenarioAgent
from core.agents.chaos_agent import ChaosAgent

# [수정일: 2026-02-23] 코드 분석 API — ChaosAgent 연결
class CoduckWarsAnalyzeCodeView(APIView):
    """
    유저 코드를 AI로 분석하여 취약점 + 실시간 점수 + 장애 이벤트를 반환하는 API
    30초마다 PressureInterviewRoom.vue에서 호출됨
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            scenario_context = request.data.get('scenario_context', '')
            code_files = request.data.get('code_files', {})
            game_phase = request.data.get('game_phase', 'design')
            previous_events = request.data.get('previous_events', [])

            # 코드가 아무것도 없으면 분석 스킵
            if not any(v and v.strip() for v in code_files.values()):
                return Response({
                    "status": "skipped",
                    "message": "코드 내용이 없어 분석을 건너뜁니다."
                }, status=status.HTTP_200_OK)

            agent = ChaosAgent()
            analysis = agent.analyze_code(
                scenario_context=scenario_context,
                code_files=code_files,
                game_phase=game_phase,
                previous_events=previous_events
            )

            return Response({
                "status": "success",
                "analysis": analysis
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"❌ CoduckWarsAnalyzeCodeView Error: {e}")
            return Response({
                "status": "error",
                "message": f"코드 분석 중 오류가 발생했습니다: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# [수정일: 2026-02-23] JD 입력 제거, 시나리오 타입 기반으로 전환
class CoduckWarsStartView(APIView):
    """
    게임 시작/미션 브리핑 시나리오 생성 API
    - scenario_type: 'random' → AI가 랜덤 시나리오 생성
    - 프리셋 시나리오(traffic_surge 등)는 프론트엔드에서 직접 처리
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            scenario_type = request.data.get('scenario_type', 'random')

            agent = ScenarioAgent()
            scenario = agent.generate_random_scenario()

            return Response({
                "status": "success",
                "scenario": scenario
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"❌ CoduckWarsStartView Error: {e}")
            return Response({
                "status": "error",
                "message": f"시나리오 생성 중 오류가 발생했습니다: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CoduckWarsPressureView(APIView):
    """
    실시간 압박 질문 생성 API
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            context = request.data.get('context', '')
            current_design = request.data.get('current_design', '')
            user_input = request.data.get('user_input', '')

            agent = ScenarioAgent()
            question_data = agent.generate_pressure_question(context, current_design, user_input)

            return Response({
                "status": "success",
                "question": question_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"❌ CoduckWarsPressureView Error: {e}")
            return Response({
                "status": "error",
                "message": f"압박 질문 생성 중 오류가 발생했습니다: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CoduckWarsEvaluationView(APIView):
    """
    게임 결과 최종 평가 생성 API
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            context = request.data.get('context', '')
            final_design = request.data.get('final_design', '')
            chat_history = request.data.get('chat_history', '')

            agent = ScenarioAgent()
            evaluation = agent.generate_evaluation(context, final_design, chat_history)

            return Response({
                "status": "success",
                "evaluation": evaluation
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"❌ CoduckWarsEvaluationView Error: {e}")
            return Response({
                "status": "error",
                "message": f"평가 생성 중 오류가 발생했습니다: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
