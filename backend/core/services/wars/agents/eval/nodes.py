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
    # 현재 평가 대상: 수정본이 있으면 수정본, 없으면 1차
    current = state.get("revised_result") or state.get("raw_result")

    if not client or not current:
        logger.warning("[EvalAgent] self_critique 스킵 (client 없음 또는 결과 없음)")
        return {**state, "critique": "PASS", "needs_revision": False}

    p1_name = state["p1_data"].get("name", "Player1")
    p2_name = state["p2_data"].get("name", "Player2")
    # [수정: compId를 풀네임으로 변환 — 약어(LB, DB)만 넘기면 LLM 품질 저하]
    COMP_NAMES = {
        'lb': 'Load Balancer', 'db': 'Database', 'cdn': 'CDN',
        'server': 'App Server', 'client': 'Client', 'user': 'User',
        'cache': 'Cache', 'api': 'API Gateway', 'apigw': 'API Gateway',
        'auth': 'Auth Service', 'queue': 'Message Queue',
        'producer': 'Producer', 'consumer': 'Consumer',
        'writesvc': 'Write Service', 'readsvc': 'Read Service',
        'writedb': 'Write DB', 'readdb': 'Read DB',
        'order': 'Order Service', 'payment': 'Payment Service',
        'waf': 'WAF', 'dns': 'DNS', 'origin': 'Origin Server',
    }
    def _node_label(n):
        comp_id = n.get('compId', '')
        return COMP_NAMES.get(comp_id, n.get('name', comp_id) or comp_id)

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
    COMP_NAMES = {
        'lb': 'Load Balancer', 'db': 'Database', 'cdn': 'CDN',
        'server': 'App Server', 'client': 'Client', 'user': 'User',
        'cache': 'Cache', 'api': 'API Gateway', 'apigw': 'API Gateway',
        'auth': 'Auth Service', 'queue': 'Message Queue',
        'producer': 'Producer', 'consumer': 'Consumer',
        'writesvc': 'Write Service', 'readsvc': 'Read Service',
        'writedb': 'Write DB', 'readdb': 'Read DB',
        'order': 'Order Service', 'payment': 'Payment Service',
        'waf': 'WAF', 'dns': 'DNS', 'origin': 'Origin Server',
    }
    def _node_label(n):
        comp_id = n.get('compId', '')
        return COMP_NAMES.get(comp_id, n.get('name', comp_id) or comp_id)
    p1_nodes = [_node_label(n) for n in state["p1_data"].get("nodes", [])]
    p2_nodes = [_node_label(n) for n in state["p2_data"].get("nodes", [])]

    prompt = f"""당신은 아키텍처 평가 전문가입니다.
아래 평가를 검수관의 지적사항에 따라 수정하십시오.

[실제 설계 데이터]
{p1_name} 배치 컴포넌트: {', '.join(p1_nodes) or '없음'}
{p2_name} 배치 컴포넌트: {', '.join(p2_nodes) or '없음'}

[현재 평가]
{json.dumps(current, ensure_ascii=False, indent=2)}

[검수관 지적사항]
{state.get('critique', '')}

[수정 지침]
- 실제 배치된 컴포넌트 이름을 분석에 반드시 포함
- 양측 평가 분량을 균형 있게 조정
- versus는 설계 차이를 구체적으로 서술

[출력 형식 — JSON만]
{{
  "player1": {{
    "my_analysis": "수정된 분석",
    "versus": "수정된 비교"
  }},
  "player2": {{
    "my_analysis": "수정된 분석",
    "versus": "수정된 비교"
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
        revised = json.loads(response.choices[0].message.content)
        logger.info("[EvalAgent] ✅ 수정 평가 완료")
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
