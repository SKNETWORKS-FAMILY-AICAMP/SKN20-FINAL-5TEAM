"""
chaos_agent.py — ChaosAgent
현재 미션 제목과 배치된 컴포넌트를 읽어 맥락에 맞는 장애 이벤트를 동적 생성한다.

[기존 방식 — 하드코딩]
    await asyncio.sleep(15)
    await sio.emit('chaos_event', {"event_id": "traffic_surge", ...})  # 항상 같은 이벤트

[에이전트 방식 — 동적 생성]
    state = draw_room_states[room_id]           # 현재 게임 상태 스냅샷 읽기
    event = await ChaosAgent().generate(state)  # 미션 맥락에 맞는 장애 생성
    await sio.emit('chaos_event', event)

LLM 1회 호출. 실패 시 룰 기반 폴백으로 자동 전환.
"""

import json
import time
import random
import logging
from typing import Dict, Any, Optional

try:
    import openai
except ImportError:
    openai = None

from django.conf import settings

logger = logging.getLogger(__name__)

# 룰 기반 폴백 이벤트 풀 — LLM 실패 시 사용
FALLBACK_EVENTS = [
    {
        "event_id": "traffic_surge",
        "title": "🚨 EMERGENCY: Traffic Surge!",
        "description": "특정 리전에서 동시 접속자가 10배 폭증했습니다. 부하 분산 구조를 재검토하세요.",
        "severity": "HIGH",
        "target_components": ["lb", "server"],
        "hint": "로드밸런서(LB) 앞단에 CDN이나 캐시 레이어를 추가하면 트래픽을 흡수할 수 있습니다.",
    },
    {
        "event_id": "db_failure",
        "title": "🔥 CRITICAL: Primary DB Down!",
        "description": "메인 DB 서버가 응답을 멈췄습니다. 데이터 유실 없이 서비스를 유지할 방법을 설계하세요.",
        "severity": "CRITICAL",
        "target_components": ["db", "readdb"],
        "hint": "Read Replica를 Primary로 승격하는 Failover 구조를 설계에 반영하세요.",
    },
    {
        "event_id": "budget_cut",
        "title": "💰 NOTICE: 인프라 예산 30% 삭감",
        "description": "경영진 결정으로 이번 분기 인프라 예산이 30% 삭감됩니다. 비용 효율적인 구조로 재설계하세요.",
        "severity": "MEDIUM",
        "target_components": ["server", "cdn"],
        "hint": "서버리스(Lambda) 또는 스팟 인스턴스를 활용하면 비용을 절감할 수 있습니다.",
    },
    {
        "event_id": "security_breach",
        "title": "🛡️ ALERT: DDoS 공격 탐지",
        "description": "외부에서 초당 50만 건의 비정상 요청이 감지되었습니다. 보안 레이어를 추가하세요.",
        "severity": "HIGH",
        "target_components": ["waf", "lb"],
        "hint": "WAF(Web Application Firewall)를 LB 앞에 배치하여 악성 트래픽을 필터링하세요.",
    },
    {
        "event_id": "region_outage",
        "title": "🌏 WARNING: 특정 리전 장애",
        "description": "ap-northeast-2 리전 전체가 다운됐습니다. 멀티 리전 구조로 설계를 수정하세요.",
        "severity": "CRITICAL",
        "target_components": ["dns", "lb"],
        "hint": "DNS Failover와 멀티 리전 LB를 사용하면 리전 장애를 자동으로 우회할 수 있습니다.",
    },
]


class ChaosAgent:
    """
    미션 맥락을 읽고 장애 이벤트를 동적으로 생성하는 에이전트.

    역할:
        - StateMachine이 can_trigger_chaos() 조건 검사
        - ChaosAgent가 실제 이벤트 내용 생성 (LLM 또는 폴백)
        - socket_server가 생성된 이벤트를 클라이언트에 emit
    """

    def __init__(self):
        if openai and getattr(settings, 'OPENAI_API_KEY', None):
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None

    def generate(
        self,
        mission_title: str,
        deployed_nodes: list,
        round_num: int = 1,
    ) -> Dict[str, Any]:
        """
        미션 제목과 현재 배치 컴포넌트를 기반으로 장애 이벤트 생성.

        Args:
            mission_title: 현재 라운드 미션 제목 (예: "글로벌 뱅킹 트래픽 분산")
            deployed_nodes: 플레이어들이 현재 배치한 컴포넌트 ID 목록 (예: ["lb", "server", "db"])
            round_num: 현재 라운드 번호

        Returns:
            {event_id, title, description, severity, target_components, hint}
        """
        if not self.client:
            logger.warning("[ChaosAgent] OpenAI client 없음 → 룰 기반 폴백 사용")
            return self._fallback(deployed_nodes)

        try:
            event = self._llm_generate(mission_title, deployed_nodes, round_num)
            logger.info(f"[ChaosAgent] ✅ 동적 이벤트 생성: {event.get('event_id')}")
            return event
        except Exception as e:
            logger.error(f"[ChaosAgent] LLM 호출 실패: {e} → 폴백 사용")
            return self._fallback(deployed_nodes)

    def _llm_generate(
        self, mission_title: str, deployed_nodes: list, round_num: int
    ) -> Dict[str, Any]:
        node_str = ", ".join(deployed_nodes) if deployed_nodes else "없음"

        prompt = f"""당신은 시스템 아키텍처 교육 게임의 ChaosAgent입니다.
플레이어가 현재 설계하고 있는 미션과 배치한 컴포넌트를 분석하여,
그 설계의 취약점을 직접 겨냥한 현실적인 장애 이벤트를 1개 생성하세요.

[현재 미션]
{mission_title}

[플레이어가 배치한 컴포넌트]
{node_str}

[생성 규칙]
1. 배치된 컴포넌트의 실제 약점을 파고드는 이벤트여야 합니다.
2. 단순히 "서버가 죽었습니다"가 아닌, 구체적인 수치와 상황을 묘사하세요.
3. hint는 해결 방향을 직접 알려주지 말고 생각할 포인트를 제시하세요.
4. severity는 반드시 "LOW", "MEDIUM", "HIGH", "CRITICAL" 중 하나입니다.

[출력 형식 — JSON만 출력]
{{
  "event_id": "고유_영문_스네이크케이스_ID",
  "title": "이모지 포함 긴급 제목",
  "description": "구체적인 장애 상황 설명 (2-3문장)",
  "severity": "HIGH",
  "target_components": ["관련_컴포넌트_id_목록"],
  "hint": "설계 개선 포인트 힌트 (1문장)"
}}"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 시스템 장애 시나리오 생성 전문가입니다. JSON만 출력합니다."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.8,
            timeout=10,
        )

        return json.loads(response.choices[0].message.content)

    def _fallback(self, deployed_nodes: list) -> Dict[str, Any]:
        """LLM 실패 시 배치 컴포넌트 기반으로 가장 연관성 높은 폴백 이벤트 선택"""
        node_set = set(deployed_nodes)

        # 배치된 컴포넌트와 겹치는 target이 가장 많은 이벤트 우선 선택
        scored = []
        for event in FALLBACK_EVENTS:
            overlap = len(set(event["target_components"]) & node_set)
            scored.append((overlap, event))

        scored.sort(key=lambda x: x[0], reverse=True)

        # 점수 동률이면 랜덤 선택
        top_score = scored[0][0]
        top_events = [e for score, e in scored if score == top_score]
        return random.choice(top_events)
