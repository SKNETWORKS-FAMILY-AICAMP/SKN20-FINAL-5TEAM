import json
import openai
from django.conf import settings
import os

# [수정일: 2026-02-23] 코드 취약점 분석 + 실시간 점수 산출 + 장애 이벤트 생성 에이전트
class ChaosAgent:
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None) or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("WARNING: OPENAI_API_KEY is not set. ChaosAgent will use fallback logic.")
        openai.api_key = self.api_key

    def analyze_code(self, scenario_context, code_files, game_phase, previous_events):
        """
        유저가 작성한 코드를 분석하여:
        - 취약점 목록 (vulnerabilities)
        - 4개 지표 점수 (scores)
        - 맞춤형 장애 이벤트 (chaos_event)
        - 전체 평가 한줄 (overall_assessment)
        를 JSON으로 반환합니다.
        """
        if not self.api_key:
            return self._fallback_analysis()

        # 코드 파일들을 하나의 텍스트로 합침
        code_text = "\n\n".join([
            f"[{tab.upper()} 탭]\n{content}"
            for tab, content in code_files.items()
            if content and content.strip()
        ])

        # 이미 발동된 이벤트 목록 (중복 방지용)
        prev_text = ", ".join(previous_events) if previous_events else "없음"

        prompt = f"""당신은 AWS Senior SRE(Site Reliability Engineer)입니다.
유저가 시스템 아키텍처 설계 게임에서 작성한 코드를 분석해주세요.

[미션 시나리오]
{scenario_context}

[유저가 작성한 코드]
{code_text}

[이미 발동된 장애 이벤트 (중복 발동 금지)]
{prev_text}

[현재 게임 페이즈]
{game_phase}

다음 기준으로 분석 후 JSON으로만 응답하세요:

1. vulnerabilities: 코드에서 발견된 구조적 취약점 목록 (최대 5개)
   - severity: "critical" (즉시 서비스 장애) / "major" (성능 저하) / "minor" (개선 필요)
   - location: "api" / "db" / "security" (어느 탭에 있는 문제인지)

2. scores: 4개 지표 점수 (0~100)
   - 평가 기준 예시:
     * workers=1, loadBalancer disabled → availability: 20
     * workers=8, loadBalancer enabled → availability: 70
     * autoScaling enabled → scalability +30
     * rate_limiting enabled → security +30
     * 불필요한 리소스 없음 → cost_efficiency +20

3. chaos_event: 취약점 기반으로 발동할 장애 (이미 발동된 것 제외, 가장 심각한 취약점 기반)
   - should_trigger: critical 취약점 1개 이상 OR major 취약점 2개 이상일 때만 true

4. overall_assessment: 현재 설계 수준 한줄 평가 (20자 이내, 직설적으로)

출력 JSON 형식:
{{
    "vulnerabilities": [
        {{
            "location": "api",
            "severity": "critical",
            "description": "구체적인 취약점 설명"
        }}
    ],
    "scores": {{
        "availability": 0,
        "scalability": 0,
        "security": 0,
        "cost_efficiency": 0
    }},
    "chaos_event": {{
        "title": "장애 이름 (짧고 강렬하게)",
        "description": "장애 상황 설명 (2문장)",
        "hint": "복구 힌트 (구체적으로)",
        "target_tab": "api",
        "should_trigger": false
    }},
    "overall_assessment": "한줄 평가"
}}"""

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 시스템 아키텍처 전문가입니다. 반드시 JSON 형식으로만 응답하세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3  # 일관성 있는 점수를 위해 낮게 설정
            )
            result = json.loads(response.choices[0].message.content)
            print(f"[ChaosAgent] 분석 성공 — 취약점 {len(result.get('vulnerabilities', []))}개 발견")
            return result

        except Exception as e:
            print(f"[ChaosAgent] API 호출 실패: {e}")
            return self._fallback_analysis()

    def _fallback_analysis(self):
        """API 키 없거나 호출 실패 시 기본값 반환"""
        return {
            "vulnerabilities": [
                {
                    "location": "api",
                    "severity": "critical",
                    "description": "워커 수가 1개로 설정되어 트래픽 분산 불가능"
                },
                {
                    "location": "api",
                    "severity": "major",
                    "description": "로드밸런서가 비활성화 상태 — 단일 서버로 모든 요청 처리"
                }
            ],
            "scores": {
                "availability": 25,
                "scalability": 15,
                "security": 50,
                "cost_efficiency": 60
            },
            "chaos_event": {
                "title": "Redis 캐시 서버 전면 다운!",
                "description": "캐시 레이어가 없어 모든 요청이 DB로 직접 유입되고 있습니다. 응답 시간이 10초를 넘겼습니다.",
                "hint": "cache.provider에 'redis'를 설정하고 ttl: 300을 추가하세요.",
                "target_tab": "api",
                "should_trigger": True
            },
            "overall_assessment": "기본 구조 미완성 — 고가용성 설정 필요"
        }
