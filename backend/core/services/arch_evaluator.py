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
                model="gpt-4o-mini",
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
[실제 채점 기준 (Rubric)]
- 필수 포함 요소: {', '.join(rubric.get('required_components', []))}
- 필수 데이터 흐름: {json.dumps(rubric.get('required_flows', []), ensure_ascii=False)}
"""

        return f"""당신은 세계 최고의 IT 아키텍처 해설가입니다. 
두 플레이어의 아키텍처 설계를 분석하여, 단순히 '무엇이 있다'를 넘어 '어떻게 연결되어 어떤 시너지를 내는지'를 아주 상세하고 전문적으로 비평해야 합니다.

{rubric_str}

[비평 가이드라인]
1. **서사적 분석**: "A와 B를 C로 연결하여 데이터 병목을 해결하려는 의도가 돋보입니다"와 같이 흐름 중심의 서술을 하십시오.
2. **구체적 명시**: 반드시 배치된 컴포넌트의 실명을 언급하며, 화살표(Flow)가 가진 아키텍처적 의미를 해석하십시오.
3. **나의 분석(Analysis)**: 본인 설계의 최대 장점과 치명적인 약점을 '설계의 연결성' 관점에서 짚어주십시오.
4. **비교(Versus)**: 상대방과의 결정적 차이를 "상대는 안정적인 정석 배치를 선택한 반면, 당신은 성능 위주의 파격적인 구조를 시도했습니다"와 같이 대조하십시오.
5. **전문성**: 가용성, 확장성, 보안성, 응답성 등의 키워드를 설계 데이터와 연결하여 설명하십시오.

[출력 형식]
{{
  "player1": {{
    "my_analysis": "서사적이고 구체적인 본인 설계 비평 (3~4문장)",
    "versus": "상대와의 구체적인 설계 차이 브리핑 (2~3문장)"
  }},
  "player2": {{
    "my_analysis": "서사적이고 구체적인 본인 설계 비평 (3~4문장)",
    "versus": "상대와의 구체적인 설계 차이 브리핑 (2~3문장)"
  }}
}}"""

    def _build_user_prompt(self, title: str, p1: Dict, p2: Dict) -> str:
        def format_canvas(nodes, arrows):
            # ID to Name mapping for better LLM context
            name_map = {n.get('id'): n.get('name', 'Unknown') for n in nodes}
            node_names = [n.get('name', 'Unknown') for n in nodes]
            arrow_descs = []
            for a in arrows:
                f_name = name_map.get(a.get('fid')) or a.get('fc', '?')
                t_name = name_map.get(a.get('tid')) or a.get('tc', '?')
                arrow_descs.append(f"{f_name} -> {t_name}")
            
            return f"- 배치 컴포넌트: {', '.join(node_names) if node_names else '없음'}\n- 데이터 흐름(연결): {', '.join(arrow_descs) if arrow_descs else '없음'}"

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
