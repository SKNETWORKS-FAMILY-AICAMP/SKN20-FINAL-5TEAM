"""
coach/nodes.py — CoachAgent LangGraph 노드 정의

[노드 목록]
  analyze_situation : 현재 설계 상태를 분류 (상황 파악)
  decide_strategy   : 힌트 이력 보고 전략 결정 (판단)
  generate_hint     : 전략에 맞는 힌트 생성 (행동)
  skip              : 힌트 불필요 시 종료

[기존 CoachAgent와 차이점]
  기존: if/else 분기 → 즉시 힌트 반환 (단발성)
  신규: 상황 분석 → 전략 결정 → 힌트 생성 (3단계 추론)
       + hint_history로 이미 준 힌트는 다른 방식으로 재시도
       + "직접 알려주기" vs "소크라테스식 질문"을 상황별로 구분
"""

import json
import logging
from typing import Dict, Any, List

from django.conf import settings

try:
    import openai
except ImportError:
    openai = None

from core.services.wars.agents.coach.state import CoachAgentState

logger = logging.getLogger(__name__)

# 컴포넌트별 역할 설명 (generate_hint 폴백용)
COMPONENT_HINTS = {
    "client":   "사용자 단말(Client)이 없으면 트래픽 진입점이 불명확합니다.",
    "lb":       "로드밸런서(LB)는 트래픽을 여러 서버에 분산시켜 단일 장애점을 제거합니다.",
    "server":   "실제 비즈니스 로직을 처리할 서버(WAS/EC2)를 배치해야 합니다.",
    "cdn":      "정적 리소스를 CDN으로 분산하면 응답 속도와 서버 부하를 크게 개선할 수 있습니다.",
    "cache":    "Redis 같은 캐시 레이어를 추가하면 DB 부하를 줄이고 응답 속도를 높일 수 있습니다.",
    "db":       "데이터를 영속적으로 저장할 DB가 없으면 설계가 완성되지 않습니다.",
    "readdb":   "읽기 전용 복제본(Read Replica)을 추가하면 조회 성능을 수평 확장할 수 있습니다.",
    "writedb":  "쓰기 전용 마스터 DB를 분리하면 읽기/쓰기 부하를 독립적으로 관리할 수 있습니다.",
    "api":      "API Gateway는 인증, 라우팅, 속도 제한을 중앙에서 처리하는 진입점입니다.",
    "auth":     "인증(Auth) 서비스가 없으면 보안 취약점이 발생할 수 있습니다.",
    "queue":    "메시지 큐(Queue)는 비동기 처리로 서비스 간 결합도를 낮춥니다.",
    "waf":      "WAF는 DDoS, SQL Injection 등 외부 공격으로부터 시스템을 보호합니다.",
    "dns":      "DNS 설정이 없으면 외부 트래픽 유입 경로가 불명확합니다.",
    "origin":   "On-Premise 원본 서버(Origin)와의 연결을 설계에 포함해야 합니다.",
    "payment":  "결제(Payment) 서비스는 트랜잭션 원자성과 보안을 별도로 설계해야 합니다.",
    "order":    "주문(Order) 서비스는 재고 시스템과의 정합성을 고려해야 합니다.",
}


def _get_client():
    if openai and getattr(settings, "OPENAI_API_KEY", None):
        return openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    return None


# ─────────────────────────────────────────────────────────
# Node 1: analyze_situation
# ─────────────────────────────────────────────────────────

def analyze_situation(state: CoachAgentState) -> CoachAgentState:
    """
    현재 설계 상태를 분석하여 situation 분류.

    situation 종류:
      empty            - 아무것도 배치 안 함
      missing_critical - 필수 컴포넌트 절반 이상 누락
      missing_optional - 필수 컴포넌트 일부 누락
      no_arrows        - 컴포넌트는 있는데 화살표 없음
      stuck_same       - 이전 힌트와 같은 상황 (정체 감지)
      complete         - 필수 컴포넌트 + 화살표 모두 완료
    """
    logger.info("[CoachAgent] ▶ analyze_situation 노드 실행")

    deployed = set(state["deployed_nodes"])
    required = set(state["mission_required"])
    missing = required - deployed
    missing_ratio = len(missing) / max(len(required), 1)

    # 이전 힌트에서 언급된 missing 컴포넌트들
    prev_missing_types = {h.get("type") for h in state.get("hint_history", [])}

    if state["node_count"] == 0:
        situation = "empty"
    elif missing_ratio >= 0.5:
        situation = "missing_critical"
    elif missing:
        # 이전에도 같은 타입의 힌트를 줬는데 여전히 누락이면 → 정체 감지
        if "missing_component" in prev_missing_types and len(state["hint_history"]) >= 2:
            situation = "stuck_same"
        else:
            situation = "missing_optional"
    elif state["arrow_count"] == 0 and state["node_count"] >= 2:
        situation = "no_arrows"
    else:
        situation = "complete"

    logger.info(f"[CoachAgent] 상황 분류: {situation} (missing={list(missing)[:3]})")
    return {**state, "situation": situation}


# ─────────────────────────────────────────────────────────
# Node 2: decide_strategy
# ─────────────────────────────────────────────────────────

def decide_strategy(state: CoachAgentState) -> CoachAgentState:
    """
    상황 + 힌트 이력을 보고 코칭 전략 결정.

    전략 종류:
      direct     - 직접 알려주기 ("LB를 추가하세요")
      socratic   - 소크라테스식 질문 ("트래픽이 급증하면 어디서 처리해야 할까요?")
      escalate   - 더 구체적으로 단계별 안내
      skip       - 힌트 불필요 (complete 상태)
    """
    logger.info("[CoachAgent] ▶ decide_strategy 노드 실행")

    situation = state["situation"]
    history_count = len(state.get("hint_history", []))

    if situation == "complete":
        strategy = "skip"

    elif situation == "empty":
        strategy = "direct"  # 처음엔 직접 안내

    elif situation == "stuck_same":
        # 같은 힌트 2번 무시했으면 → 더 구체적 에스컬레이션
        strategy = "escalate"

    elif history_count == 0:
        # 첫 힌트는 항상 직접 안내
        strategy = "direct"

    elif history_count == 1:
        # 두 번째 힌트는 소크라테스식으로 생각 유도
        strategy = "socratic"

    else:
        # 세 번 이상이면 다시 직접 안내 (포기하지 않고 명확하게)
        strategy = "direct"

    logger.info(f"[CoachAgent] 전략 결정: {strategy} (history={history_count})")
    return {**state, "strategy": strategy}


# ─────────────────────────────────────────────────────────
# Node 3: generate_hint
# ─────────────────────────────────────────────────────────

def generate_hint(state: CoachAgentState) -> CoachAgentState:
    """
    결정된 전략에 맞는 힌트를 생성한다.

    direct   → 룰 기반 명확한 힌트 (LLM 불필요)
    socratic → LLM으로 질문 형식 힌트 생성
    escalate → LLM으로 단계별 상세 가이드 생성
    """
    logger.info(f"[CoachAgent] ▶ generate_hint 노드 실행 (strategy={state['strategy']})")

    strategy = state["strategy"]
    situation = state["situation"]
    deployed = set(state["deployed_nodes"])
    required = set(state["mission_required"])
    missing = list(required - deployed)

    if strategy == "direct":
        hint = _generate_direct_hint(situation, missing, state)

    elif strategy == "socratic":
        hint = _generate_socratic_hint(state, missing)

    elif strategy == "escalate":
        hint = _generate_escalate_hint(state, missing)

    else:
        hint = {"message": "", "missing_components": [], "type": "complete", "level": 0}

    logger.info(f"[CoachAgent] 힌트 생성: type={hint.get('type')}, level={hint.get('level')}")
    return {**state, "hint": hint, "done": True}


def _generate_direct_hint(situation: str, missing: list, state: CoachAgentState) -> Dict:
    """룰 기반 직접 힌트"""
    if situation == "empty":
        return {
            "message": "💡 아직 아무것도 배치하지 않으셨네요. 사용자(Client)부터 시작해보는 건 어떨까요?",
            "missing_components": list(state["mission_required"]),
            "type": "general",
            "level": 1,
        }

    if missing:
        # 우선순위: required 순서 기준 첫 번째 누락
        priority = missing[0]
        for req in state["mission_required"]:
            if req in missing:
                priority = req
                break
        msg = COMPONENT_HINTS.get(priority, f"'{priority}' 컴포넌트를 추가해보세요.")
        return {
            "message": f"💡 {msg}",
            "missing_components": missing,
            "type": "missing_component",
            "level": 1,
        }

    if state["arrow_count"] == 0:
        return {
            "message": "💡 컴포넌트를 모두 배치했네요! 이제 데이터 흐름(화살표)을 연결해보세요.",
            "missing_components": [],
            "type": "no_arrows",
            "level": 1,
        }

    return {"message": "", "missing_components": [], "type": "complete", "level": 0}


def _generate_socratic_hint(state: CoachAgentState, missing: list) -> Dict:
    """LLM 기반 소크라테스식 질문 힌트"""
    client = _get_client()

    if not client or not missing:
        return _generate_direct_hint(state["situation"], missing, state)

    priority = missing[0]
    for req in state["mission_required"]:
        if req in missing:
            priority = req
            break

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 시스템 아키텍처 교육 코치입니다. 답을 직접 알려주지 말고, 생각을 유도하는 질문 1개를 한국어로 만드세요. 이모지 포함, 1문장.",
                },
                {
                    "role": "user",
                    "content": f"플레이어가 '{priority}' 컴포넌트를 아직 배치하지 않았습니다. 힌트가 되는 질문을 만들어주세요.",
                },
            ],
            temperature=0.7,
            timeout=8,
        )
        message = response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"[CoachAgent] socratic LLM 실패: {e}")
        message = COMPONENT_HINTS.get(priority, f"'{priority}'에 대해 생각해보세요.")

    return {
        "message": message,
        "missing_components": missing,
        "type": "missing_component",
        "level": 2,
    }


def _generate_escalate_hint(state: CoachAgentState, missing: list) -> Dict:
    """LLM 기반 에스컬레이션 — 단계별 상세 가이드"""
    client = _get_client()

    if not client or not missing:
        return _generate_direct_hint(state["situation"], missing, state)

    deployed_str = ", ".join(state["deployed_nodes"]) or "없음"
    missing_str = ", ".join(missing)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 시스템 아키텍처 교육 코치입니다. 플레이어가 같은 힌트를 2번 받았지만 진전이 없습니다. 이번엔 구체적인 단계별 가이드를 2문장으로 알려주세요. 이모지 포함, 한국어.",
                },
                {
                    "role": "user",
                    "content": f"현재 배치: {deployed_str}\n누락된 필수 컴포넌트: {missing_str}\n단계별 가이드를 주세요.",
                },
            ],
            temperature=0.5,
            timeout=8,
        )
        message = response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"[CoachAgent] escalate LLM 실패: {e}")
        message = f"🚨 {missing_str} 컴포넌트를 지금 바로 캔버스에 추가하세요. 왼쪽 패널에서 드래그해서 배치할 수 있습니다."

    return {
        "message": message,
        "missing_components": missing,
        "type": "escalate",
        "level": 3,
    }


# ─────────────────────────────────────────────────────────
# Node 4: skip
# ─────────────────────────────────────────────────────────

def skip(state: CoachAgentState) -> CoachAgentState:
    """힌트 불필요 — complete 상태"""
    logger.info("[CoachAgent] ▶ skip 노드 (설계 완료 상태)")
    return {
        **state,
        "hint": {"message": "", "missing_components": [], "type": "complete", "level": 0},
        "done": True,
    }


# ─────────────────────────────────────────────────────────
# 라우팅 함수 (conditional_edge용)
# ─────────────────────────────────────────────────────────

def route_after_strategy(state: CoachAgentState) -> str:
    """전략에 따라 분기"""
    if state.get("strategy") == "skip":
        return "skip"
    return "generate_hint"
