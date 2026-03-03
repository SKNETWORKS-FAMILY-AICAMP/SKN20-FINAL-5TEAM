"""
eval/nodes.py — EvalAgent LangGraph 노드 정의

[노드 목록]
  evaluate      : ArchEvaluator로 1차 평가 실행
  self_critique : 평가 결과의 품질 자기비판 (편향/누락/일관성 검사)
  revise        : 자기비판 반영하여 평가 수정
  finalize      : 최종 결과 확정

[루프 설명]
  evaluate → self_critique → revise → self_critique → ... (최대 2회)
                           ↘ finalize (문제 없으면 바로 확정)
"""

import json
import logging
from typing import Dict, Any

from django.conf import settings

try:
    import openai
except ImportError:
    openai = None

from core.services.wars.agents.eval.state import EvalAgentState
from core.services.arch_evaluator import ArchEvaluator

logger = logging.getLogger(__name__)

_evaluator = ArchEvaluator()

# ─────────────────────────────────────────────────────────
# 공통 상수 / 헬퍼 — 모듈 상단에 한 번만 선언 (DRY)
# ─────────────────────────────────────────────────────────

_COMP_NAMES: Dict[str, str] = {
    'lb':       'Load Balancer',
    'db':       'Database',
    'cdn':      'CDN',
    'server':   'App Server',
    'client':   'Client',
    'user':     'User',
    'cache':    'Cache',
    'api':      'API Gateway',
    'apigw':    'API Gateway',
    'auth':     'Auth Service',
    'queue':    'Message Queue',
    'producer': 'Producer',
    'consumer': 'Consumer',
    'writesvc': 'Write Service',
    'readsvc':  'Read Service',
    'writedb':  'Write DB',
    'readdb':   'Read DB',
    'order':    'Order Service',
    'payment':  'Payment Service',
    'waf':      'WAF',
    'dns':      'DNS',
    'origin':   'Origin Server',
}


def _node_label(node: Dict[str, Any]) -> str:
    """node dict → 사람이 읽기 좋은 컴포넌트 이름으로 변환"""
    comp_id = node.get('compId', '')
    return _COMP_NAMES.get(comp_id, node.get('name', comp_id) or comp_id)


def _get_client():
    if openai and getattr(settings, "OPENAI_API_KEY", None):
        return openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    return None


# ─────────────────────────────────────────────────────────
# Node 1: evaluate
# ─────────────────────────────────────────────────────────

def evaluate(state: EvalAgentState) -> EvalAgentState:
    """
    1차 평가 실행.
    기존 ArchEvaluator.evaluate_comparison() 그대로 호출.
    """
    logger.info("[EvalAgent] ▶ evaluate 노드 실행")

    try:
        result = _evaluator.evaluate_comparison(
            mission_title=state["mission_title"],
            player1_data=state["p1_data"],
            player2_data=state["p2_data"],
            rubric=state.get("rubric"),
        )
        logger.info("[EvalAgent] ✅ 1차 평가 완료")
    except Exception as e:
        logger.error(f"[EvalAgent] 1차 평가 실패: {e}")
        result = _evaluator._fallback_review(state["p1_data"], state["p2_data"])

    return {**state, "raw_result": result}


# ─────────────────────────────────────────────────────────
# Node 2: self_critique
# ─────────────────────────────────────────────────────────

def self_critique(state: EvalAgentState) -> EvalAgentState:
    """
    평가 결과를 자기비판한다.

    검사 항목:
      1. 양측 평가 길이가 너무 불균형하지 않은가?
      2. 한 플레이어에게만 일방적으로 긍정/부정이 집중되지 않았는가?
      3. my_analysis와 versus가 실제 설계 데이터와 연관되어 있는가?
      4. 구체적인 컴포넌트 이름이 등장하는가?

    LLM이 "PASS" 또는 "REVISE: <이유>" 형식으로 판단.
    """
    logger.info("[EvalAgent] ▶ self_critique 노드 실행")

    client = _get_client()
    current = state.get("revised_result") or state.get("raw_result")

    if not client or not current:
        logger.warning("[EvalAgent] self_critique 스킵 (client 없음 또는 결과 없음)")
        return {**state, "critique": "PASS", "needs_revision": False}

    p1_name = state["p1_data"].get("name", "Player1")
    p2_name = state["p2_data"].get("name", "Player2")
    p1_nodes = [_node_label(n) for n in state["p1_data"].get("nodes", [])]
    p2_nodes = [_node_label(n) for n in state["p2_data"].get("nodes", [])]

    prompt = f"""당신은 아키텍처 평가 품질 검수관입니다.
아래 평가 결과를 검토하고, 품질 기준에 따라 판단하십시오.

[실제 설계 데이터]
{p1_name} 배치 컴포넌트: {', '.join(p1_nodes) or '없음'}
{p2_name} 배치 컴포넌트: {', '.join(p2_nodes) or '없음'}

[평가 결과]
{json.dumps(current, ensure_ascii=False, indent=2)}

[품질 기준]
1. 양측 my_analysis 길이가 2배 이상 차이나면 불균형
2. 한쪽만 칭찬하고 다른 쪽은 비판만 하면 편향
3. 실제 배치된 컴포넌트 이름이 분석에 등장해야 함
4. versus 항목이 실제 설계 차이를 반영해야 함 (추상적 표현 금지)

[판단]
문제가 없으면: PASS
문제가 있으면: REVISE: <구체적인 수정 지시사항>

한 줄로만 답하십시오."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 평가 품질 검수관입니다. PASS 또는 REVISE: <이유> 형식으로만 답합니다."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            timeout=10,
        )
        critique = response.choices[0].message.content.strip()
        needs_revision = critique.upper().startswith("REVISE")
        logger.info(f"[EvalAgent] self_critique 결과: {critique[:80]}")
    except Exception as e:
        logger.error(f"[EvalAgent] self_critique 실패: {e}")
        critique = "PASS"
        needs_revision = False

    return {**state, "critique": critique, "needs_revision": needs_revision}


# ─────────────────────────────────────────────────────────
# Node 3: revise
# ─────────────────────────────────────────────────────────

def revise(state: EvalAgentState) -> EvalAgentState:
    """
    self_critique의 지적사항을 반영하여 평가를 수정한다.
    """
    logger.info(f"[EvalAgent] ▶ revise 노드 실행 (retry #{state['retry_count'] + 1})")

    client = _get_client()
    current = state.get("revised_result") or state.get("raw_result")

    if not client or not current:
        return {**state, "revised_result": current, "retry_count": state["retry_count"] + 1}

    p1_name = state["p1_data"].get("name", "Player1")
    p2_name = state["p2_data"].get("name", "Player2")
    p1_nodes = [_node_label(n) for n in state["p1_data"].get("nodes", [])]
    p2_nodes = [_node_label(n) for n in state["p2_data"].get("nodes", [])]

    prompt = f"""당신은 아키텍처 평가를 정교하게 다듬는 전문가입니다.
아래 평가를 검수관의 지적사항에 따라 수정하되, 설계의 '연결성과 흐름'에 대한 상세한 설명을 반드시 보존하거나 강화하십시오.

[실제 설계 데이터]
{p1_name} 배치 컴포넌트: {', '.join(p1_nodes) or '없음'}
{p2_name} 배치 컴포넌트: {', '.join(p2_nodes) or '없음'}

[현재 평가]
{json.dumps(current, ensure_ascii=False, indent=2)}

[검수관 지적사항]
{state.get('critique', '')}

[수정 지침]
- **서사적 깊이 유지**: "무엇이 배치되었다"는 단순 나열을 피하고, "A가 B와 연결되어 C를 목표로 한다"는 인과관계를 서술하십시오.
- **실제 명칭 사용**: 실제 배치된 컴포넌트 이름을 언급하며 분석의 신뢰도를 높이십시오.
- **양측 균형**: 한쪽 평가가 너무 짧아지지 않도록 분량을 맞추십시오.
- **Versus 강화**: 두 설계의 결정적 차이(가용성 중심 vs 성능 중심 등)를 명확히 대조하십시오.

[출력 형식 — JSON만]
{{
  "player1": {{
    "my_analysis": "수정 및 강화된 상세 분석 (3~4문장)",
    "versus": "수정 및 강화된 구체적 비교 (2~3문장)"
  }},
  "player2": {{
    "my_analysis": "수정 및 강화된 상세 분석 (3~4문장)",
    "versus": "수정 및 강화된 구체적 비교 (2~3문장)"
  }}
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 평가 수정 전문가입니다. JSON만 출력합니다."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.5,
            timeout=15,
        )
        patch = json.loads(response.choices[0].message.content)
        # [수정일: 2026-03-02] 딥카피 merge 방식으로 수정
        # revise()는 player1/player2의 my_analysis, versus만 반환하며
        # raw_result에 있던 score, winner 등 나머지 필드는 그대로 보존된다.
        revised = dict(current)  # 원본 복사
        for player_key in ("player1", "player2"):
            if player_key in patch and isinstance(patch[player_key], dict):
                player_block = dict(revised.get(player_key, {}))
                player_block.update(patch[player_key])  # my_analysis, versus만 덮어쓰기
                revised[player_key] = player_block
        logger.info("[EvalAgent] ✅ 수정 평가 완료 (merge 방식)")
    except Exception as e:
        logger.error(f"[EvalAgent] revise 실패: {e} → 기존 결과 유지")
        revised = current

    return {**state, "revised_result": revised, "retry_count": state["retry_count"] + 1}


# ─────────────────────────────────────────────────────────
# Node 4: finalize
# ─────────────────────────────────────────────────────────

def finalize(state: EvalAgentState) -> EvalAgentState:
    """
    최종 결과 확정.
    revised_result가 있으면 그걸 사용, 없으면 raw_result 사용.
    """
    logger.info("[EvalAgent] ▶ finalize 노드 실행")

    final = state.get("revised_result") or state.get("raw_result")

    if not final:
        logger.error("[EvalAgent] 최종 결과 없음 → 폴백 사용")
        final = _evaluator._fallback_review(state["p1_data"], state["p2_data"])

    logger.info("[EvalAgent] ✅ 평가 확정 완료")
    return {**state, "final_result": final}


# ─────────────────────────────────────────────────────────
# 라우팅 함수 (conditional_edge용)
# ─────────────────────────────────────────────────────────

def route_after_critique(state: EvalAgentState) -> str:
    """
    self_critique 결과에 따라 다음 노드 결정.
    - 재평가 필요 + 재시도 횟수 2 미만 → "revise"
    - 그 외 → "finalize"
    """
    MAX_RETRIES = 2
    if state.get("needs_revision") and state.get("retry_count", 0) < MAX_RETRIES:
        logger.info(f"[EvalAgent] 재평가 분기 → revise (retry={state.get('retry_count', 0)})")
        return "revise"
    logger.info("[EvalAgent] 확정 분기 → finalize")
    return "finalize"
