"""
architecture_missions.py — ArchDrawQuiz Mission Pool
시스템 아키텍처 설계 미션 데이터셋.
"""

MISSIONS = [
    {
        "id": "msa_ecommerce",
        "title": "MSA 기반 전자상거래 시스템",
        "context": "대규모 트래픽 처리를 위해 모놀리식 구조를 MSA로 전환해야 합니다. 주문, 결제 서비스가 분리되어야 합니다.",
        "required": ["lb", "apigw", "order", "payment", "db"],
        "recommended": ["cache", "waf"]
    },
    {
        "id": "global_banking",
        "title": "글로벌 뱅킹 서비스 가용성 설계",
        "context": "전 세계 사용자를 대상으로 하는 뱅킹 서비스입니다. 지연 시간을 줄이고 특정 리전 장애에도 견뎌야 합니다.",
        "required": ["dns", "cdn", "lb", "server", "writedb", "readdb"],
        "recommended": ["waf", "api"]
    },
    {
        "id": "realtime_monitor",
        "title": "실시간 데이터 모니터링 파이프라인",
        "context": "초당 수만 건의 로그를 수집하여 실시간으로 대시보드에 표시해야 합니다. 데이터 유실이 없어야 합니다.",
        "required": ["producer", "queue", "consumer", "readdb", "cache"],
        "recommended": ["lb", "apigw"]
    },
    {
        "id": "secure_auth",
        "title": "보안 강화 유저 인증 인프라",
        "context": "모든 API 요청은 인증을 거쳐야 하며, DDoS 공격으로부터 서버를 보호해야 합니다.",
        "required": ["waf", "apigw", "auth", "db", "cache"],
        "recommended": ["lb", "dns"]
    },
    {
        "id": "streaming_service",
        "title": "고해상도 영상 스트리밍 플랫폼",
        "context": "대용량 영상 콘텐츠를 전 세계에 끊김 없이 전달해야 합니다. 원본 서버의 부하를 최소화하세요.",
        "required": ["cdn", "origin", "lb", "server", "cache"],
        "recommended": ["dns", "waf"]
    }
]
