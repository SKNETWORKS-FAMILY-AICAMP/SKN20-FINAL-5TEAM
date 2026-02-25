import json
import openai
from django.conf import settings

# [수정일: 2026-02-23] Coduck Wars 핵심 로직: JD 기반 시나리오 및 압박 질문 생성 엔진
class ScenarioAgent:
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if not self.api_key:
            # 로컬 테스트 환경 등에서 settings에 없을 경우 환경 변수 확인
            import os
            self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            print("WARNING: OPENAI_API_KEY is not set. Using fallback logic.")
            
        openai.api_key = self.api_key

    # [수정일: 2026-02-23] JD 없이 랜덤 시나리오 생성 메서드 추가
    def generate_random_scenario(self):
        """
        JD 입력 없이 AI가 랜덤 장애 시나리오를 생성합니다.
        """
        if not self.api_key:
            return self._get_fallback_scenario()

        prompt = """
        당신은 시스템 엔지니어링 면접 시뮬레이션 게임 'Coduck Wars'의 시나리오 디자이너입니다.
        실무에서 발생할 수 있는 참신하고 다양한 '최악의 시스템 장애' 시나리오를 랜덤으로 하나 생성해주세요.

        [테마 예시 - 이 중 하나를 랜덤으로 선택하되 변형을 가하세요]
        - 마이크로서비스 장애 전파
        - 캐시 스탬피드
        - DNS 장애로 인한 글로벌 서비스 중단
        - 컨테이너 오케스트레이션 장애
        - 데이터 파이프라인 병목
        - 서드파티 API 장애 대응

        출력 포맷: JSON
        {{
            "mission_title": "짧고 강렬한 미션 제목",
            "context": "왜 이 상황이 벌어졌는지 비즈니스 임팩트 포함 2~3문장",
            "initial_quest": "플레이어가 먼저 해결해야 할 구체적 과제",
            "interviewer": {{
                "name": "면접관 이름 (한국어)",
                "persona": "면접관 성향 1줄 설명"
            }},
            "chaos_event": "게임 중 발생할 추가 장애 이벤트"
        }}
        """

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 전문적인 시스템 아키텍트이자 게임 시나리오 디자이너입니다."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Random Scenario Generation Error: {e}")
            return self._get_fallback_scenario()

    def generate_game_scenario(self, jd_text):
        """
        JD 텍스트를 분석하여 실전 장애 시나리오를 생성합니다.
        """
        if not self.api_key:
            return self._get_fallback_scenario()

        prompt = f"""
        당신은 실무 기반의 시스템 엔지니어링 면접 시뮬레이션 게임 'Coduck Wars'의 시나리오 디자이너입니다.
        아래의 채용공고(JD)를 분석하여, 해당 직무의 엔지니어가 실무에서 맞닥뜨릴 수 있는 '최악의 시스템 장애' 또는 '대규모 아키텍처 개편' 시나리오를 생성해주세요.

        [분석할 JD]
        {jd_text}

        [생성 가이드라인]
        1. 시나리오는 단순히 기술 스택을 묻는 것이 아니라, 비즈니스 상황과 결합된 구체적인 장애 상황이어야 합니다.
        2. 미션 제목(mission_title): 짧고 강렬한 제목
        3. 배경(context): 왜 이 일이 벌어졌는지, 비즈니스 임팩트는 무엇인지 상세히 설명 (2~3문장)
        4. 초기 과제(initial_quest): 플레이어가 가장 먼저 해결해야 할 구체적인 과제
        5. 면접관 페르소나(interviewer): 
           - 이름(name)
           - 성격 및 말투(persona): 날카롭거나, 부드럽거나, 데이터 중심적이거나 등 핵심 성향 1줄
        6. 돌발 장애 이벤트(chaos_event): 게임 중 발생할 수 있는 추가적인 변수 (예: 트래픽 2배 급증, DB 락 발생 등)

        [출력 포맷]
        JSON 형식으로만 대답하세요.
        {{
            "mission_title": "...",
            "context": "...",
            "initial_quest": "...",
            "interviewer": {{
                "name": "...",
                "persona": "..."
            }},
            "chaos_event": "..."
        }}
        """

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 전문적인 시스템 아키트트이자 게임 시나리오 디자이너입니다."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Scenario Generation Error: {e}")
            return self._get_fallback_scenario()

    def generate_pressure_question(self, context, current_design, user_input):
        """
        사용자의 답변이나 설계 내용을 바탕으로 면접관의 압박 질문을 생성합니다.
        """
        if not self.api_key:
            return {
                "question": "현재 설계가 비용 최적화 관점에서 타당하다고 보십니까?",
                "focus_area": "비용"
            }

        prompt = f"""
        당신은 'Coduck Wars'의 면접관입니다. 현재 진행 중인 미션과 사용자의 설계 내용을 분석하여 정곡을 찌르는 압박 질문을 던지세요.

        [미션 배경]
        {context}

        [현재 설계 상태]
        {current_design}

        [사용자의 최근 답변]
        {user_input}

        [가이드라인]
        - 사용자의 논리적 허점을 찾아 비판적으로 질문하세요.
        - 비용, 가용성, 성능, 보안 중 하나 이상의 관점에서 공격하세요.
        - 짧지만 묵직한 질문이어야 합니다.

        출력 포맷: JSON
        {{
            "question": "...",
            "focus_area": "보안 | 성능 | 비용 | 가용성"
        }}
        """

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 냉철한 실무 면접관입니다."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "question": "해당 설계가 단일 장애점(SPOF) 문제를 완전히 해결했다고 확신하십니까?",
                "focus_area": "가용성"
            }

    def generate_evaluation(self, context, final_design, chat_history):
        """
        게임 종료 후 최종 설계와 대화 기록을 바탕으로 플레이어의 역량을 평가합니다.
        """
        if not self.api_key:
            return self._get_fallback_evaluation()

        prompt = f"""
        당신은 'Coduck Wars'의 최종 평가 에이전트입니다. 플레이어의 미션 수행 결과를 분석하여 상세 성장 리포트를 작성하세요.

        [미션 배경]
        {context}

        [최종 아키텍처 설계]
        {final_design}

        [면접 대화 기록]
        {chat_history}

        [평가 가이드라인]
        1. 5개 항목에 대해 100점 만점 기준으로 점수를 산정하세요:
           - 논리성(Logic): 답변의 논리적 일관성과 방어 능력
           - 설계력(Design): 아키텍처의 완성도 및 확장성
           - 대응력(Resilience): 장애 및 압박에 대한 유연한 대처
           - 기술력(Stack): 기술 선택의 적절성
           - 비용 최적화(Cost): 인프라 자원 효율성
        2. 종합 등급(S, A, B, C)을 결정하세요.
        3. 정성 평가:
           - The Good: 가장 인상 깊었던 설계적 결정 2가지
           - The Bad: 보완이 필요한 치명적인 약점 2가지
           - Action Items: 실무 역량 향상을 위한 구체적인 조언 3가지

        출력 포맷: JSON
        {{
            "scores": {{
                "logic": 0,
                "design": 0,
                "resilience": 0,
                "stack": 0,
                "cost": 0
            }},
            "total_score": 0,
            "grade": "S | A | B | C",
            "feedback": {{
                "the_good": ["...", "..."],
                "the_bad": ["...", "..."],
                "action_items": ["...", "...", "..."]
            }}
        }}
        """

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 전문적인 시스템 아키텍트이자 면접관 교육가입니다."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Evaluation Generation Error: {e}")
            return self._get_fallback_evaluation()

    def _get_fallback_evaluation(self):
        return {
            "scores": {
                "logic": 85,
                "design": 70,
                "resilience": 75,
                "stack": 80,
                "cost": 60
            },
            "total_score": 74,
            "grade": "B",
            "feedback": {
                "the_good": ["객체 지향적인 서버 분리 시도가 좋았습니다.", "트래픽 폭주 시나리오를 인지하고 L7 로드밸런서를 도입했습니다."],
                "the_bad": ["데이터베이스 Read Replica 도입 시 데이터 정합성 문제에 대한 대안이 부족했습니다.", "비용 효율성을 고려하지 않은 오버 프로비저닝 설계가 우려됩니다."],
                "action_items": ["인프라 비용 산정 방식에 대해 학습하세요.", "CAP 이론과 데이터베이스 정합성 모델을 복습하세요.", "Mermaid.js를 이용한 더 정교한 시스템 문서화 연습이 필요합니다."]
            }
        }

    def _get_fallback_scenario(self):
        return {
            "mission_title": "글로벌 트래픽 폭주 대응",
            "context": "갑작스러운 프로모션 성공으로 인해 아시아 지역 API 서버의 CPU 사용률이 95%를 상회하며 응답 속도가 급격히 저하되었습니다.",
            "initial_quest": "현재의 부하를 분산시키기 위한 긴급 L7 로드밸런싱 전략과 데이터베이스 읽기 전용 복제본(Read Replica) 구성을 제안하세요.",
            "interviewer": {
                "name": "박책임",
                "persona": "자원을 낭비하지 않는 극한의 비용 효율성을 추구하며, 지표에 기반하지 않은 답변은 신뢰하지 않습니다."
            },
            "chaos_event": "주요 데이터베이스의 커넥션 풀이 가득 차서 새로운 요청을 처리하지 못하는 상황이 발생합니다."
        }
