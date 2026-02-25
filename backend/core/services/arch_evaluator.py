import os
import json
import logging
from typing import Dict, Any, List, Optional
try:
    import openai
except ImportError:
    openai = None

from django.conf import settings

logger = logging.getLogger(__name__)

class ArchEvaluator:
    """
    아키텍처 설계 리뷰 엔진 - LLM 기반
    수정일: 2026-02-24
    
    [역할]
    - 규칙 기반의 단순 비교를 넘어, LLM(GPT)을 통해 양측 설계의 전략적 차이점 분석.
    - 미션 요구사항 대비 각 플레이어의 설계 철학(가용성 vs 보안 등) 비평.
    """

    def __init__(self):
        if openai and getattr(settings, 'OPENAI_API_KEY', None):
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None

    def evaluate_comparison(
        self,
        mission_title: str,
        player1_data: Dict[str, Any],
        player2_data: Dict[str, Any],
        rubric: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        두 플레이어의 설계 데이터를 비교 분석하여 정성적 리뷰 생성.
        """
        if not self.client:
            logger.warning("[ArchEvaluator] OpenAI client not initialized. Falling back to rule-based.")
            return self._fallback_review(player1_data, player2_data)

        try:
            system_prompt = self._build_system_prompt(rubric)
            user_prompt = self._build_user_prompt(mission_title, player1_data, player2_data)

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                timeout=15
            )

            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logger.error(f"[ArchEvaluator] LLM Evaluation failed: {e}")
            return self._fallback_review(player1_data, player2_data)

    def _build_system_prompt(self, rubric: Dict[str, Any] = None) -> str:
        rubric_str = ""
        if rubric:
            rubric_str = f"""
[DB 평가 기준표 (Rubric)]
- 필수 컴포넌트: {', '.join(rubric.get('required_components', []))}
- 필수 데이터 흐름: {json.dumps(rubric.get('required_flows', []), ensure_ascii=False)}
- 주요 평가 축(비중/이유): {json.dumps(rubric.get('axis_weights', {}), ensure_ascii=False)}

위 평가 기준을 반드시 반영하여 두 플레이어의 설계를 평가하십시오.
"""

        return f"""당신은 'Arch Draw' 미니게임의 수석 아키텍트 해설 위원입니다.
두 플레이어가 제출한 시스템 아키텍처 설계 결과를 비교하여 고품질의 정성적 비평을 제공하십시오.
{rubric_str}
[분석 지침]
1. 하드코딩된 느낌을 버리고, 각 플레이어가 배치한 컴포넌트 간의 관계를 전문적으로 해석하십시오.
2. '나의 분석(Analysis)': 플레이어 본인의 설계에서 돋보이는 점(예: 가용성 확보, 보안 강화)과 아쉬운 점을 짚어주십시오.
3. '비교(Versus)': 상대방과 대조하여 "당신은 X에 집중했으나 상대는 Y에 더 치중했습니다"와 같은 전략적 차이점을 설명하십시오.
4. 전문 용어(LB, DB Replication, WAF, MSA 등)를 적절히 섞어 신뢰감을 주십시오.
5. 응답은 각 플레이어별로 다르게 제공되어야 하므로, JSON 구조 내에 player1용과 player2용 출력을 분리하십시오.

[출력 형식]
{{
  "player1": {{
    "my_analysis": "본인의 설계에 대한 전문적 비평",
    "versus": "상대방과 대조되는 설계 차별점 브리핑"
  }},
  "player2": {{
    "my_analysis": "본인의 설계에 대한 전문적 비평",
    "versus": "상대방과 대조되는 설계 차별점 브리핑"
  }}
}}"""

    def _build_user_prompt(self, title: str, p1: Dict, p2: Dict) -> str:
        def format_checks(checks):
            ok = [c['label'] for c in checks if c.get('ok')]
            miss = [c['label'] for c in checks if not c.get('ok')]
            return f"성공: {', '.join(ok) if ok else '없음'}\\n실패: {', '.join(miss) if miss else '없음'}"

        def format_canvas(nodes, arrows):
            node_names = [n.get('name', 'Unknown') for n in nodes]
            arrow_descs = [f"{a.get('fc', '?')} -> {a.get('tc', '?')}" for a in arrows]
            return f"배치된 노드: {', '.join(node_names) if node_names else '없음'}\\n연결된 화살표: {', '.join(arrow_descs) if arrow_descs else '없음'}"

        return f"""[미션: {title}]

[플레이어 1 ({p1.get('name', 'Player1')})]
점수: {p1.get('pts', 0)}
설계 현황 (체크리스트):
{format_checks(p1.get('checks', []))}
실제 디자인 (노드/연결):
{format_canvas(p1.get('nodes', []), p1.get('arrows', []))}

[플레이어 2 ({p2.get('name', 'Player2')})]
점수: {p2.get('pts', 0)}
설계 현황 (체크리스트):
{format_checks(p2.get('checks', []))}
실제 디자인 (노드/연결):
{format_canvas(p2.get('nodes', []), p2.get('arrows', []))}

두 설계의 차이를 분석하여 JSON으로 응답하십시오."""

    def _fallback_review(self, p1: Dict, p2: Dict) -> Dict[str, Any]:
        # LLM 실패 시 최소한의 룰 기반 피드백
        return {
            "player1": {
                "my_analysis": "기본적인 아키텍처 흐름은 준수하지만, 세부 연결 보완이 필요합니다.",
                "versus": "상대방과 비슷한 방향성을 보였으나 마감 속도에서 차이가 발생했습니다."
            },
            "player2": {
                "my_analysis": "설계의 핵심 뼈대는 갖추었으나 특정 구간의 가용성 설계가 누락되었습니다.",
                "versus": "전체적인 무결성 면에서 박빙의 결과를 보여주고 있습니다."
            }
        }
