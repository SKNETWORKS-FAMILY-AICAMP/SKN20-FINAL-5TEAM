# AI-ARCADE 개인 맞춤형 학습 이정표 구현 계획
> 작성일: 2026-02-22
> 핵심 원칙: `gym_user_solved_problem.submitted_data` 분석 → 약점 도출 → 개인별 학습 이정표 제시
> 목표: "지금 너는 여기 있고, 이걸 공부하면 다음 단계로 갈 수 있다"는 명확한 학습 로드맵 제공

---

## 0. 현황 파악

### `submitted_data` 구조 (유닛별)

유닛마다 저장되는 JSON 구조가 다름. 현재 파악된 구조:

**Unit 1 - 의사코드 (데이터 파이프라인)**
```json
{
  "phase": "COMPLETE",
  "ai_evaluation": {
    "score": 75,
    "metrics": {
      "logic_flow": 80,
      "edge_case": 50,
      "readability": 90
    },
    "analysis": "edge_case 처리가 부족합니다...",
    "advice": "예외 상황을 더 고려해보세요"
  }
}
```

**Unit 2 - 버그헌트 (디버깅)**
```json
{
  "phase": "COMPLETE",
  "ai_evaluation": {
    "score": 68,
    "metrics": {
      "bug_detection": 70,
      "root_cause": 55,
      "fix_quality": 80
    },
    "weak_point": "답변 근거의 구체성",
    "analysis": "버그 원인 분석이 표면적입니다"
  }
}
```

**Unit 3 - 시스템 아키텍처**
```json
{
  "phase": "COMPLETE",
  "ai_evaluation": {
    "score": 60,
    "pillarScores": {
      "scalability": 55,
      "reliability": 70,
      "security": 40,
      "performance": 65,
      "maintainability": 80,
      "cost_efficiency": 60
    },
    "weaknesses": ["보안 설계 미흡", "확장성 고려 부족"],
    "advice": "..."
  }
}
```

### 기존 분석 코드 (`MasterAgentView`)
- `GET /api/core/master-agent/` — 이미 submitted_data를 전부 읽어 GPT로 분석하는 로직 존재
- 하지만 **결과를 DB에 저장하지 않음** (요청마다 LLM 재호출)
- **URL이 urls.py에 등록되어 있지 않아 미연결 상태**

---

## 1. 목표 정의: 학습 이정표

```
기존 흐름:
문제 풀이 → 점수 + 피드백 → "이제 뭘 해야 하지?" (막막함)

개선 흐름:
문제 풀이 → submitted_data 저장
                  ↓
           약점 분석 & 매핑
                  ↓
        학습 이정표 생성 & 제시
                  ↓
    ┌──────────────────────────────────┐
    ▼                                  ▼
 [현재] edge_case 45점    [공부할 것]
 너는 예외처리를 생각하지 않는다   Defensive Programming
 → 실무에서 장애 유발함      경계값 테스트
                            타입 안전성
                                ↓
                        [다음 목표] edge_case 70점
                        Unit 1 재도전해서 70점 이상
```

### 학습 이정표의 3가지 구성 요소

| 요소 | 설명 | 예시 |
|------|------|------|
| **현재 위치** | 약점 + 점수 + 문제 진단 | "edge_case 45점: null 입력을 처리하지 않음" |
| **공부할 것** | 개념/원리/기술 (이론 + 자료) | Defensive Programming, 경계값 분석 |
| **다음 목표** | 구체적 마일스톤 | "Unit 1 재도전 70점 이상 달성" |

### 구현 우선순위

| 단계 | 기능 | 난이도 | 효과 |
|------|------|--------|------|
| Phase 1 | submitted_data 파싱 → 약점 점수 계산 & 진단 → DB 저장 | ★★☆ | 약점 데이터 확보 |
| Phase 2 | 약점 → 학습 로드맵 매핑 (개념/자료 제시) | ★★☆ | 즉각적 학습 방향 제시 |
| Phase 3 | AI 개인화된 이정표 생성 (사용자 풀이 기반) | ★★★ | 초개인화 경험 |

---

## 2. Phase 1: 약점 분석 엔진 구축

### 2-1. 새 모델: `UserWeaknessProfile`

**파일**: `backend/core/models/activity_model.py`

```python
class UserWeaknessProfile(BaseModel):
    """
    사용자의 약점을 유닛별로 집계해 저장.
    submitted_data를 파싱한 결과를 정규화된 형태로 보관.
    """
    user = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='weakness_profile'
    )

    # 유닛별 평균 메트릭 점수 (0~100)
    unit1_metrics = models.JSONField(default=dict)
    # 예: {"logic_flow": 72, "edge_case": 45, "readability": 88}

    unit2_metrics = models.JSONField(default=dict)
    # 예: {"bug_detection": 68, "root_cause": 50, "fix_quality": 75}

    unit3_metrics = models.JSONField(default=dict)
    # 예: {"scalability": 55, "reliability": 70, "security": 40, ...}

    # 전체 약점 요약 (상위 3개)
    top_weaknesses = models.JSONField(default=list)
    # 예: ["edge_case", "security", "root_cause"]

    # 마지막 분석 시점
    last_analyzed_at = models.DateTimeField(auto_now=True)

    # 분석된 풀이 수 (캐시 무효화 기준)
    analyzed_submission_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'gym_user_weakness_profile'
```

### 2-2. 약점 분석 서비스

**파일**: `backend/core/services/weakness_service.py` (신규)

```python
"""
submitted_data를 파싱해 UserWeaknessProfile을 업데이트하는 서비스.
LLM 없이 순수 데이터 집계로 동작 → 비용 0, 빠름.
"""

# 유닛별 파서 매핑
UNIT_METRIC_PARSERS = {
    'unit01': parse_unit1_metrics,  # logic_flow, edge_case, readability
    'unit02': parse_unit2_metrics,  # bug_detection, root_cause, fix_quality
    'unit03': parse_unit3_metrics,  # pillarScores 6개
}

# 약점 판정 기준 (이 점수 미만이면 약점)
WEAKNESS_THRESHOLD = 65


def parse_unit1_metrics(submitted_data: dict) -> dict:
    """Unit 1 submitted_data에서 메트릭 추출"""
    ai_eval = submitted_data.get('ai_evaluation', {})
    metrics = ai_eval.get('metrics', {})
    return {
        'logic_flow':   metrics.get('logic_flow', 0),
        'edge_case':    metrics.get('edge_case', 0),
        'readability':  metrics.get('readability', 0),
    }


def parse_unit2_metrics(submitted_data: dict) -> dict:
    """Unit 2 submitted_data에서 메트릭 추출"""
    ai_eval = submitted_data.get('ai_evaluation', {})
    metrics = ai_eval.get('metrics', {})
    return {
        'bug_detection': metrics.get('bug_detection', 0),
        'root_cause':    metrics.get('root_cause', 0),
        'fix_quality':   metrics.get('fix_quality', 0),
    }


def parse_unit3_metrics(submitted_data: dict) -> dict:
    """Unit 3 submitted_data에서 pillarScores 추출"""
    ai_eval = submitted_data.get('ai_evaluation', {})
    pillar = ai_eval.get('pillarScores', {})
    return {
        'scalability':      pillar.get('scalability', 0),
        'reliability':      pillar.get('reliability', 0),
        'security':         pillar.get('security', 0),
        'performance':      pillar.get('performance', 0),
        'maintainability':  pillar.get('maintainability', 0),
        'cost_efficiency':  pillar.get('cost_efficiency', 0),
    }


def aggregate_metrics(records: list[dict]) -> dict:
    """여러 제출의 메트릭을 평균으로 집계 (최근 5회 가중치 높임)"""
    if not records:
        return {}

    all_keys = records[0].keys()
    result = {}
    n = len(records)

    for key in all_keys:
        values = [r.get(key, 0) for r in records]
        # 최근 3회에 가중치 2배
        recent = values[-3:] if n >= 3 else values
        older  = values[:-3] if n > 3 else []
        weighted = (sum(recent) * 2 + sum(older)) / (len(recent) * 2 + len(older))
        result[key] = round(weighted, 1)

    return result


def compute_top_weaknesses(
    unit1: dict, unit2: dict, unit3: dict
) -> list[str]:
    """전체 메트릭 중 WEAKNESS_THRESHOLD 미만 항목을 점수 낮은 순으로 반환"""
    all_metrics = {**unit1, **unit2, **unit3}
    weak = {k: v for k, v in all_metrics.items() if v < WEAKNESS_THRESHOLD}
    sorted_weak = sorted(weak.items(), key=lambda x: x[1])
    return [k for k, _ in sorted_weak[:5]]  # 상위 5개 약점


def update_weakness_profile(user_profile) -> 'UserWeaknessProfile':
    """
    사용자의 모든 submitted_data를 파싱해 UserWeaknessProfile 갱신.
    submit 후 자동 호출 또는 수동 요청 시 호출.
    """
    solved_list = UserSolvedProblem.objects.filter(
        user=user_profile,
        submitted_data__isnull=False,
        is_best_score=True  # 최고 점수 기록만 분석
    ).select_related('practice_detail__practice').order_by('solved_date')

    unit_records = {'unit01': [], 'unit02': [], 'unit03': []}

    for sp in solved_list:
        unit_id = sp.practice_detail.practice_id  # 'unit01', 'unit02', 'unit03'
        parser  = UNIT_METRIC_PARSERS.get(unit_id)
        if not parser or not sp.submitted_data:
            continue

        metrics = parser(sp.submitted_data)
        if any(v > 0 for v in metrics.values()):  # 유효한 데이터만
            unit_records[unit_id].append(metrics)

    unit1_avg = aggregate_metrics(unit_records['unit01'])
    unit2_avg = aggregate_metrics(unit_records['unit02'])
    unit3_avg = aggregate_metrics(unit_records['unit03'])
    top_weak  = compute_top_weaknesses(unit1_avg, unit2_avg, unit3_avg)

    profile, _ = UserWeaknessProfile.objects.update_or_create(
        user=user_profile,
        defaults={
            'unit1_metrics': unit1_avg,
            'unit2_metrics': unit2_avg,
            'unit3_metrics': unit3_avg,
            'top_weaknesses': top_weak,
            'analyzed_submission_count': solved_list.count(),
        }
    )
    return profile
```

### 2-3. submit 시 자동 갱신 연결

**파일**: `backend/core/services/activity_service.py`
`save_user_problem_record` 함수 마지막에 추가:

```python
# 기존 코드 마지막에 추가
from core.services.weakness_service import update_weakness_profile

def save_user_problem_record(user_profile, detail_id, score, submitted_data):
    with transaction.atomic():
        # ... 기존 저장 로직 ...

        # 약점 프로필 비동기 갱신 (응답 지연 방지)
        # 실제로는 Celery 태스크로 분리 권장, MVP는 동기 처리
        update_weakness_profile(user_profile)

        return result
```

---

## 3. Phase 2: 학습 이정표 생성 (매핑 기반)

### 3-1. 이정표 로직 설계

```
약점 메트릭 (예: edge_case 45점)
        ↓
약점 진단 (왜 부족한가?)
"null/empty 입력을 처리하지 않음"
        ↓
학습 로드맵 매핑 조회
약점(edge_case) → {개념, 자료, 예상시간}
        ↓
개인화된 이정표 구성:
[현재] edge_case 45점 (null 미처리)
[공부] Defensive Programming (이론 1시간)
       경계값 테스트 (실습 30분)
       타입 안전성 (사례 20분)
[목표] edge_case 70점 달성 → Unit 1 재도전
```

### 3-2. 학습 로드맵 매핑 테이블 (핵심)

**파일**: `backend/core/services/roadmap_service.py` (신규)

```python
"""
약점 → 학습 개념/자료로 매핑하는 서비스.
LLM 없이 사전 정의된 이정표로 빠른 응답.
"""

# 약점별 학습 이정표 정의
WEAKNESS_LEARNING_ROADMAP = {
    # ===== Unit 1: 의사코드/파이프라인 =====
    'edge_case': {
        'diagnosis': '예외 상황(null, empty, 경계값)을 설계 단계에서 고려하지 않음',
        'why_matters': '실무: 처리하지 않은 예외는 런타임 장애로 이어짐',
        'learning_path': [
            {
                'order': 1,
                'concept': 'Defensive Programming (방어적 코딩)',
                'duration_minutes': 60,
                'type': 'THEORY',  # THEORY / PRACTICE / CASE_STUDY
                'keywords': ['null check', 'input validation', 'error handling'],
                'resources': [
                    'https://en.wikipedia.org/wiki/Defensive_programming',
                    '🎥 Defensive Programming Basics (YouTube 추천)',
                ],
            },
            {
                'order': 2,
                'concept': '경계값 분석 (Boundary Value Analysis)',
                'duration_minutes': 30,
                'type': 'PRACTICE',
                'keywords': ['min', 'max', 'empty', 'null', 'edge values'],
                'resources': [
                    '📝 연습: 파이프라인 입력으로 가능한 모든 경계값 나열해보기',
                    '💡 팁: "최소값, 최대값, 없음(empty), 잘못된 형식" 4가지 항상 고려',
                ],
            },
            {
                'order': 3,
                'concept': '타입 안전성과 검증',
                'duration_minutes': 20,
                'type': 'CASE_STUDY',
                'keywords': ['type checking', 'schema validation', 'assertion'],
                'resources': [
                    '📚 사례: 우버의 null pointer exception 장애',
                    '✅ 체크리스트: 내 설계에 타입 검증이 있는가?',
                ],
            },
        ],
        'milestone': {
            'current_score': 'PLACEHOLDER',  # 실제로는 user 약점 점수로 대체
            'target_score': 70,
            'action': 'Unit 1 "null 처리 집중" 문제 재도전',
        },
    },

    'logic_flow': {
        'diagnosis': '파이프라인의 단계 순서나 제어 흐름이 불명확함',
        'why_matters': '실무: 데이터가 잘못된 순서로 처리되면 결과 자체가 틀림',
        'learning_path': [
            {
                'order': 1,
                'concept': '데이터 흐름 시각화 (Data Flow Diagram)',
                'duration_minutes': 45,
                'type': 'THEORY',
                'keywords': ['dataflow', 'dependency', 'sequence'],
                'resources': [
                    'https://en.wikipedia.org/wiki/Data_flow_diagram',
                    '🎨 도구: draw.io로 자신의 설계를 DFD로 그려보기',
                ],
            },
            {
                'order': 2,
                'concept': '순환 참조와 의존성 해결',
                'duration_minutes': 40,
                'type': 'PRACTICE',
                'keywords': ['cyclic dependency', 'ordering', 'topological sort'],
                'resources': [
                    '💻 연습: 순서가 중요한 3단계 파이프라인 설계',
                ],
            },
        ],
        'milestone': {
            'target_score': 75,
            'action': 'Unit 1 "복잡한 흐름" 문제 한번 풀어보기',
        },
    },

    'readability': {
        'diagnosis': '설계가 이해하기 어렵게 표현됨 (변수명, 모듈 이름, 문서)',
        'why_matters': '실무: 팀원이 코드를 이해하지 못하면 유지보수 불가',
        'learning_path': [
            {
                'order': 1,
                'concept': '명확한 이름짓기 (Naming Conventions)',
                'duration_minutes': 30,
                'type': 'THEORY',
                'keywords': ['naming', 'abstraction', 'clarity'],
                'resources': [
                    '📖 "Clean Code" - Ch 2: Meaningful Names',
                    '✍️ 팁: 약자 대신 풀어서 쓰기 (auth_mgr → authentication_manager)',
                ],
            },
            {
                'order': 2,
                'concept': '구조화된 문서 작성',
                'duration_minutes': 25,
                'type': 'PRACTICE',
                'keywords': ['documentation', 'diagram', 'comments'],
                'resources': [
                    '📝 연습: 내 설계를 3문장으로 설명해보기',
                    '🎯 템플릿: "이 모듈은 [입력] → [처리] → [출력]"',
                ],
            },
        ],
        'milestone': {
            'target_score': 80,
            'action': 'Unit 1 이전 풀이를 "초심자도 이해할 수 있게" 리팩토링',
        },
    },

    # ===== Unit 2: 버그헌트/디버깅 =====
    'bug_detection': {
        'diagnosis': '숨겨진 버그를 찾지 못함 (로직 오류, 경계값 버그)',
        'why_matters': '실무: 찾지 못한 버그는 프로덕션에서 터짐',
        'learning_path': [
            {
                'order': 1,
                'concept': '버그 패턴 인식',
                'duration_minutes': 50,
                'type': 'THEORY',
                'keywords': ['off-by-one', 'type mismatch', 'logic error'],
                'resources': [
                    '📚 Common Bug Patterns (CWE Top 25)',
                    '🎯 목록: Off-by-one, null pointer, integer overflow, race condition',
                ],
            },
            {
                'order': 2,
                'concept': '스택트레이스 읽기 & 추적',
                'duration_minutes': 35,
                'type': 'PRACTICE',
                'keywords': ['stack trace', 'debugging', 'breakpoint'],
                'resources': [
                    '🔍 실습: 에러 로그에서 버그 위치 찾기',
                ],
            },
        ],
        'milestone': {
            'target_score': 75,
            'action': 'Unit 2 "숨겨진 버그" 레벨 문제들 3개 풀이',
        },
    },

    'root_cause': {
        'diagnosis': '버그는 찾았지만, 왜 발생했는지 원인을 깊이 있게 분석하지 못함',
        'why_matters': '실무: 근본 원인을 모르면 같은 버그가 계속 반복됨',
        'learning_path': [
            {
                'order': 1,
                'concept': '5 Why 분석법',
                'duration_minutes': 30,
                'type': 'THEORY',
                'keywords': ['root cause', '5 whys', 'problem solving'],
                'resources': [
                    '📖 Toyota 5 Why method 설명',
                    '💡 팁: "왜?" 5번 반복해서 진짜 원인 찾기',
                ],
            },
            {
                'order': 2,
                'concept': '가정 검증과 실험적 디버깅',
                'duration_minutes': 40,
                'type': 'PRACTICE',
                'keywords': ['hypothesis', 'testing', 'validation'],
                'resources': [
                    '🔬 연습: 버그에 대해 3가지 가설을 세우고 검증하기',
                ],
            },
        ],
        'milestone': {
            'target_score': 70,
            'action': 'Unit 2 면접 시 "버그 원인"을 2문장 이상 설명하기',
        },
    },

    # ===== Unit 3: 시스템 아키텍처 =====
    'scalability': {
        'diagnosis': '시스템이 사용자 증가에 대응할 수 있도록 설계되지 않음',
        'why_matters': '실무: 초기에 놓친 확장성은 나중에 전체 리아키텍처로 이어짐 (비용↑)',
        'learning_path': [
            {
                'order': 1,
                'concept': '수평 확장 vs 수직 확장',
                'duration_minutes': 45,
                'type': 'THEORY',
                'keywords': ['horizontal scaling', 'vertical scaling', 'load balancing'],
                'resources': [
                    '📖 AWS Scalability Best Practices',
                    '🎯 이해: "많은 서버 추가" vs "더 좋은 서버 하나"',
                ],
            },
            {
                'order': 2,
                'concept': '병렬 처리와 캐싱',
                'duration_minutes': 40,
                'type': 'PRACTICE',
                'keywords': ['parallelism', 'caching', 'queue'],
                'resources': [
                    '💻 실습: 병목 지점을 캐시/큐로 해결하는 설계',
                ],
            },
            {
                'order': 3,
                'concept': '실제 확장 사례 분석',
                'duration_minutes': 30,
                'type': 'CASE_STUDY',
                'keywords': ['case study', 'architecture evolution'],
                'resources': [
                    '📚 우버/넷플릭스의 아키텍처 진화 사례',
                ],
            },
        ],
        'milestone': {
            'target_score': 70,
            'action': 'Unit 3 "1만 명 사용자 대응" 설계 문제 도전',
        },
    },

    'security': {
        'diagnosis': '보안 위협을 고려하지 않은 설계 (인증, 인가, 데이터 암호화)',
        'why_matters': '실무: 보안 결함은 회사 신용도에 직결됨',
        'learning_path': [
            {
                'order': 1,
                'concept': 'OWASP Top 10',
                'duration_minutes': 60,
                'type': 'THEORY',
                'keywords': ['OWASP', 'injection', 'XSS', 'auth', 'encryption'],
                'resources': [
                    'https://owasp.org/www-project-top-ten/',
                    '📖 읽기: 상위 3개 (Injection, Broken Auth, XSS) 이해',
                ],
            },
            {
                'order': 2,
                'concept': '인증/인가 설계',
                'duration_minutes': 45,
                'type': 'PRACTICE',
                'keywords': ['authentication', 'authorization', 'JWT', 'OAuth'],
                'resources': [
                    '🔐 JWT vs Session 비교하기',
                    '💻 연습: 로그인 시스템의 인증/인가 플로우 설계',
                ],
            },
            {
                'order': 3,
                'concept': '데이터 보호 (암호화, PII)',
                'duration_minutes': 30,
                'type': 'PRACTICE',
                'keywords': ['encryption', 'PII', 'privacy'],
                'resources': [
                    '🔒 민감 정보 보호 체크리스트',
                ],
            },
        ],
        'milestone': {
            'target_score': 65,
            'action': 'Unit 3 "GDPR 준수" 설계 문제 풀어보기',
        },
    },

    'reliability': {
        'diagnosis': '장애에 대한 대응을 고려하지 않음 (복구, 모니터링, 롤백)',
        'why_matters': '실무: 언제든 장애가 날 수 있고, 그 때 대응할 수 있어야 함',
        'learning_path': [
            {
                'order': 1,
                'concept': '고가용성(HA) 아키텍처',
                'duration_minutes': 50,
                'type': 'THEORY',
                'keywords': ['high availability', 'redundancy', 'failover'],
                'resources': [
                    '📖 AWS HA Best Practices',
                    '💡 개념: 한 지점 장애가 전체를 마비시키면 안 됨',
                ],
            },
            {
                'order': 2,
                'concept': '모니터링과 알림',
                'duration_minutes': 35,
                'type': 'PRACTICE',
                'keywords': ['monitoring', 'logging', 'alerting', 'SLA'],
                'resources': [
                    '📊 메트릭: CPU, 메모리, 응답시간, 에러율',
                    '💻 도구 예: Prometheus, Grafana, ELK',
                ],
            },
        ],
        'milestone': {
            'target_score': 75,
            'action': 'Unit 3 "서버 1대 장애 시 자동 복구" 설계',
        },
    },
}


def get_learning_roadmap(weakness_name: str, current_score: float) -> dict:
    """약점별 학습 이정표 반환"""
    roadmap = WEAKNESS_LEARNING_ROADMAP.get(weakness_name)
    if not roadmap:
        return {}

    # 마일스톤에 현재 점수 주입
    roadmap['milestone']['current_score'] = current_score

    return {
        'weakness': weakness_name,
        'diagnosis': roadmap['diagnosis'],
        'why_matters': roadmap['why_matters'],
        'learning_path': roadmap['learning_path'],
        'milestone': roadmap['milestone'],
        'total_estimated_hours': sum(p['duration_minutes'] for p in roadmap['learning_path']) / 60,
    }
```

### 3-3. 학습 이정표 API 엔드포인트

**파일**: `backend/core/views/roadmap_view.py` (신규)

```python
class UserRoadmapView(APIView):
    """GET /api/core/roadmap/profile/
    사용자의 약점 기반 전체 학습 이정표
    """

    def get(self, request):
        user_profile = request.user.userprofile
        weakness_profile = UserWeaknessProfile.objects.filter(
            user=user_profile
        ).first()

        if not weakness_profile:
            return Response({'error': 'No weakness profile yet'}, status=404)

        roadmaps = []
        for weakness in weakness_profile.top_weaknesses:
            score = weakness_profile._get_weakness_score(weakness)
            roadmap = get_learning_roadmap(weakness, score)
            roadmaps.append(roadmap)

        return Response({
            'user_roadmaps': roadmaps,
            'analyzed_at': weakness_profile.last_analyzed_at,
        })


class WeaknessSingleRoadmapView(APIView):
    """GET /api/core/roadmap/weakness/{weakness_name}/
    특정 약점의 상세 이정표
    """

    def get(self, request, weakness_name):
        user_profile = request.user.userprofile
        weakness_profile = UserWeaknessProfile.objects.filter(
            user=user_profile
        ).first()

        if not weakness_profile:
            return Response({'error': 'No weakness profile'}, status=404)

        score = weakness_profile._get_weakness_score(weakness_name)
        roadmap = get_learning_roadmap(weakness_name, score)

        if not roadmap:
            return Response({'error': 'Unknown weakness'}, status=404)

        return Response(roadmap)
```

### 3-4. URL 등록

**파일**: `backend/core/urls.py`

```python
from core.views.roadmap_view import (
    UserRoadmapView,
    WeaknessSingleRoadmapView,
)

urlpatterns = [
    # ... 기존 ...
    path('roadmap/profile/', UserRoadmapView.as_view()),
    path('roadmap/weakness/<str:weakness_name>/', WeaknessSingleRoadmapView.as_view()),
]
```

---

## 4. Phase 3: AI 개인화된 이정표 (선택)

Phase 1~2로도 충분하지만, AI를 추가하면 더 개인화된 학습 이정표 제공 가능.

### 4-1. AI를 언제 쓰는가

Phase 1~2: **사전 정의된 이정표 제공** (빠름, 비용 0)
Phase 3: **AI로 사용자 풀이 기반 이정표 커스터마이징** (느림, 비용 ↑)

```
사용자 약점: "edge_case 45점"
        ↓
기본 이정표 제시: Defensive Programming, 경계값 분석...
        ↓
AI 분석 (선택적):
  사용자의 최근 3개 풀이 분석
  + "이 사람은 구체적으로 뭘 놓쳤나"
  → 커스텀 피드백 + 맞춤 순서 조정
```

### 4-2. AI 개인화 프롬프트 구조

```python
def build_personalized_roadmap_prompt(
    weakness_name: str,
    current_score: float,
    recent_submissions: list[dict]  # submitted_data 3개
) -> str:
    submission_summary = "\n".join([
        f"제출 {i+1}: 점수 {sub['score']} - 피드백: {sub.get('ai_evaluation', {}).get('analysis', '')[:100]}..."
        for i, sub in enumerate(recent_submissions[:3])
    ])

    return f"""
당신은 AI 엔지니어 초년생 교육 전문가입니다.
이 학습자의 실제 실수 패턴을 분석해 **개인화된** 학습 순서를 제시하세요.

## 학습자 정보
- 약점: {weakness_name}
- 현재 점수: {current_score}/100
- 최근 제출들:
{submission_summary}

## 요청
1. 이 학습자가 **구체적으로 놓친 부분** 분석 (1문장)
2. 기본 학습 순서 중 이 사람에게 **특히 중요한 항목 3개** 강조
3. "먼저 이걸 공부해야 다음이 이해됩니다" 선행 관계 1~2개 추가

간결하게, 실용적으로. 200단어 이내.
"""
```

### 4-3. AI 개인화 캐시

```python
class PersonalizedRoadmapCache(BaseModel):
    """AI 생성 개인화 이정표 캐시"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    weakness_name = models.CharField(max_length=50)
    personalization = models.TextField()  # AI가 생성한 개인화 가이드
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # 24시간 후 무효화

    class Meta:
        db_table = 'gym_personalized_roadmap_cache'
        unique_together = [('user', 'weakness_name')]
```

---

## 5. 프론트엔드 UI 설계: 학습 이정표

### 5-1. 진입 경로

```
홈페이지
  └── "내 학습 이정표" 버튼
        └── 이정표 대시보드 (모달 or 페이지)
              ├── [섹션 1] 약점 요약 (상위 3개)
              ├── [섹션 2] 약점별 이정표 카드 (펼침 가능)
              └── [섹션 3] 진행도 추적
```

### 5-2. 이정표 대시보드 상단 (약점 요약)

```
┌──────────────────────────────────────────────────────────┐
│ 📍 당신의 학습 현황                                       │
│                                                            │
│  🔴 긴급: edge_case (45점)                               │
│     └─ "null 입력 미처리"                                 │
│  🟠 주의: root_cause (50점)                              │
│     └─ "원인 분석 표면적"                                 │
│  🟡 보통: logic_flow (72점)                              │
│     └─ "흐름이 비효율적"                                  │
│                                                            │
│ 📈 지난주보다 edge_case +5점 향상! 🎉                    │
└──────────────────────────────────────────────────────────┘
```

### 5-3. 약점별 상세 이정표 카드 (확장 가능)

```
┌─────────────────────────────────────────────────────────────┐
│ 🎯 edge_case 학습 이정표                  [⬇ 펼치기]       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ 📍 [현재 위치]                                              │
│    점수: 45/100  •  진단: null/empty 입력 미처리            │
│    영향: 실무에서 처리하지 않은 예외는 런타임 장애 야기     │
│                                                               │
│ 📚 [공부해야 할 것] — 예상 소요시간: 2시간 15분            │
│    1️⃣ Defensive Programming (방어적 코딩) 60분              │
│       🔗 https://en.wikipedia.org/wiki/Defensive_programming │
│       💡 핵심: null check, input validation, error handling   │
│                                                               │
│    2️⃣ 경계값 분석 (Boundary Value Analysis) 30분            │
│       📝 연습: 파이프라인 입력으로 가능한 모든 경계값 나열   │
│       ✅ 팁: "최소값, 최대값, 없음(empty), 잘못된 형식" 확인  │
│                                                               │
│    3️⃣ 타입 안전성과 검증 20분                               │
│       📚 사례: 우버의 null pointer 장애                      │
│       ✅ 체크리스트: 내 설계에 타입 검증이 있는가?           │
│                                                               │
│ 🎯 [다음 목표]                                              │
│    ├─ 현재: 45점                                            │
│    ├─ 목표: 70점 이상                                       │
│    └─ 행동: Unit 1 "null 처리 집중" 문제 재도전             │
│       추정 시간: 30분  •  예상 효과: +15점 향상             │
│                                                               │
│                      [학습 시작하기 →]                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 🎯 root_cause 학습 이정표                  [⬇ 펼치기]       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ 📍 [현재 위치]                                              │
│    점수: 50/100  •  진단: 버그 원인을 깊이 있게 분석 못함   │
│    영향: 근본 원인을 모르면 같은 버그 계속 반복됨           │
│                                                               │
│ 📚 [공부해야 할 것] — 예상 소요시간: 1시간 5분             │
│    1️⃣ 5 Why 분석법 30분                                     │
│       📖 Toyota 5 Why method                                 │
│       💡 팁: "왜?" 5번 반복해서 진짜 원인 찾기              │
│                                                               │
│    2️⃣ 가정 검증과 실험적 디버깅 35분                       │
│       🔬 연습: 버그에 대해 3가지 가설 세우고 검증           │
│       ✅ 도구: print debugging → breakpoint debugging        │
│                                                               │
│ 🎯 [다음 목표]                                              │
│    ├─ 목표: 70점 이상                                       │
│    └─ 행동: Unit 2 면접 시 "버그 원인" 2문장 이상 설명      │
│                                                               │
│                      [학습 시작하기 →]                      │
└─────────────────────────────────────────────────────────────┘
```

### 5-4. 진행도 추적 섹션

```
┌──────────────────────────────────────────────────────────┐
│ 📊 학습 진행도                                             │
│                                                            │
│ edge_case                                                  │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ (45/100)  │
│ 학습 시작  •  예상 시간: 2시간 15분  •  완료까지: ~2일   │
│                                                            │
│ root_cause                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ (50/100)                │
│ 학습 시작  •  예상 시간: 1시간 5분  •  완료까지: ~1일   │
│                                                            │
│ logic_flow                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ (72/100)         │
│ 곧 마스터! [Unit 1 마지막 문제 도전 →]                   │
│                                                            │
│ 💡 팁: 우선순위대로 위부터 공부하세요.                    │
│       먼저 edge_case를 70점 이상 가지고 오면,             │
│       다른 약점들도 더 쉬워질 거예요.                     │
└──────────────────────────────────────────────────────────┘
```

### 5-5. 프로트엔드 컴포넌트 구조

**파일**: `frontend/src/features/learning/LearningRoadmap.vue`

```vue
<template>
  <div class="learning-roadmap">
    <!-- 상단: 약점 요약 -->
    <WeaknessSummary :weaknesses="topWeaknesses" />

    <!-- 중간: 약점별 이정표 카드 (아코디언) -->
    <div class="roadmap-cards">
      <RoadmapCard
        v-for="weakness in userRoadmaps"
        :key="weakness.weakness"
        :roadmap="weakness"
        :user-score="weakness.milestone.current_score"
        @card-clicked="expandCard"
      />
    </div>

    <!-- 하단: 진행도 -->
    <ProgressTracker :roadmaps="userRoadmaps" />
  </div>
</template>
```

**`RoadmapCard.vue` 구조**:
```
- 헤더 (약점명, 현재 점수, 진단)
- 펼침 버튼
- [펼쳐짐] 학습 경로 리스트
  - 각 항목: 순번, 개념명, 시간, 타입(이론/실습/사례), 자료 링크
- [펼쳐짐] 다음 목표
- [펼쳐짐] "학습 시작하기" 버튼 (로드맵 페이지 이동)
```

---

## 6. API 전체 정리

### 6-1. 핵심 엔드포인트

| Method | URL | 설명 | Phase | 응답시간 |
|--------|-----|------|-------|---------|
| GET | `/api/core/roadmap/profile/` | 사용자 전체 학습 이정표 (상위 약점) | 1~2 | <100ms |
| GET | `/api/core/roadmap/weakness/{name}/` | 특정 약점 상세 이정표 | 2 | <100ms |
| GET | `/api/core/weakness/profile/` | 약점 메트릭 원본 데이터 | 1 | <50ms |
| POST | `/api/core/weakness/analyze/` | 수동 재분석 요청 | 1 | 1~2s |

### 6-2. 응답 예시

**`GET /api/core/roadmap/profile/`**
```json
{
  "user_roadmaps": [
    {
      "weakness": "edge_case",
      "diagnosis": "예외 상황(null, empty, 경계값)을 설계 단계에서 고려하지 않음",
      "why_matters": "실무: 처리하지 않은 예외는 런타임 장애로 이어짐",
      "learning_path": [
        {
          "order": 1,
          "concept": "Defensive Programming (방어적 코딩)",
          "duration_minutes": 60,
          "type": "THEORY",
          "keywords": ["null check", "input validation", "error handling"],
          "resources": [
            "https://en.wikipedia.org/wiki/Defensive_programming",
            "🎥 Defensive Programming Basics (YouTube 추천)"
          ]
        },
        {
          "order": 2,
          "concept": "경계값 분석 (Boundary Value Analysis)",
          "duration_minutes": 30,
          "type": "PRACTICE",
          "keywords": ["min", "max", "empty", "null"],
          "resources": [
            "📝 연습: 파이프라인 입력으로 가능한 모든 경계값 나열해보기"
          ]
        }
      ],
      "milestone": {
        "current_score": 45,
        "target_score": 70,
        "action": "Unit 1 \"null 처리 집중\" 문제 재도전"
      },
      "total_estimated_hours": 2.25
    },
    {
      "weakness": "root_cause",
      "diagnosis": "...",
      // ...
    }
  ],
  "analyzed_at": "2026-02-22T10:30:00Z"
}
```

**`GET /api/core/weakness/profile/`**
```json
{
  "unit1_metrics": {
    "logic_flow": 72.0,
    "edge_case": 45.0,
    "readability": 88.0
  },
  "unit2_metrics": {
    "bug_detection": 68.0,
    "root_cause": 50.0,
    "fix_quality": 75.0
  },
  "unit3_metrics": {
    "scalability": 55.0,
    "reliability": 70.0,
    "security": 40.0,
    "performance": 65.0,
    "maintainability": 80.0,
    "cost_efficiency": 60.0
  },
  "top_weaknesses": ["edge_case", "root_cause", "security"],
  "last_analyzed_at": "2026-02-22T10:30:00Z"
}
```

---

## 7. 구현 순서 (실제 작업 흐름)

### Day 1~2: Phase 1 백엔드 (약점 분석)
```
□ UserWeaknessProfile 모델 작성
□ 마이그레이션 생성/적용
□ weakness_service.py 작성
  └─ parse_unit1/2/3_metrics (파서 3개)
  └─ aggregate_metrics (평균 계산)
  └─ compute_top_weaknesses (상위 약점)
  └─ update_weakness_profile (메인 함수)
□ activity_service.py 마지막에 update_weakness_profile() 호출 추가
□ weakness_view.py에 UserWeaknessView 작성
□ urls.py에 `/api/core/weakness/profile/` 등록
□ 기존 사용자 데이터 일괄 분석 스크립트 1회 실행
   → python manage.py shell
   → from core.services.weakness_service import update_weakness_profile
   → for user in UserProfile.objects.all(): update_weakness_profile(user)
```

### Day 3~4: Phase 2 백엔드 (학습 이정표)
```
□ roadmap_service.py 작성
  └─ WEAKNESS_LEARNING_ROADMAP 딕셔너리 (약점별 이정표)
  └─ get_learning_roadmap() 함수
□ roadmap_view.py 작성
  └─ UserRoadmapView (전체 이정표)
  └─ WeaknessSingleRoadmapView (개별 이정표)
□ urls.py에 2개 엔드포인트 등록
  └─ /api/core/roadmap/profile/
  └─ /api/core/roadmap/weakness/<weakness_name>/
□ API 테스트 (Postman)
  └─ GET /api/core/roadmap/profile/ 응답 확인
  └─ GET /api/core/roadmap/weakness/edge_case/ 응답 확인
```

### Day 5~7: 프론트엔드 UI (학습 이정표 대시보드)
```
□ frontend/src/features/learning/ 폴더 생성
□ RoadmapService.js (API 호출)
  └─ fetchUserRoadmaps()
  └─ fetchSingleRoadmap(weaknessName)
□ LearningRoadmap.vue (메인 컴포넌트)
□ WeaknessSummary.vue (상단 약점 요약)
□ RoadmapCard.vue (약점별 이정표 카드, 아코디언)
  └─ 헤더, 진단, 공부 경로, 마일스톤
  └─ "학습 시작하기" 버튼
□ ProgressTracker.vue (진행도 바)
□ LandingView.vue에 "내 학습 이정표" 버튼 추가
  └─ @click="$emit('open-learning-roadmap')"
□ App.vue에서 모달 또는 페이지 라우팅 처리
```

### Day 8~10: Phase 3 (AI 개인화, 선택)
```
□ PersonalizedRoadmapCache 모델 추가
□ roadmap_service.py에 AI 개인화 로직 추가
  └─ build_personalized_prompt()
  └─ generate_personalized_roadmap()
  └─ 캐시 조회/저장
□ roadmap_view.py에 WeaknessSingleRoadmapView 확장
  └─ query param: ?personalize=true
  └─ personalization 필드 추가 응답
□ 프론트엔드 RoadmapCard.vue 확장
  └─ AI 개인화 섹션 표시 (있으면)
```

---

## 8. 주의사항 및 설계 결정

### 8-1. submitted_data가 없는 경우 처리
- 풀이 기록이 없거나 submitted_data가 null인 경우 → 빈 프로필 반환
- 프론트엔드: "아직 문제를 풀지 않았어요. 먼저 문제를 풀어보세요." 메시지
- 최소 데이터 기준: 유닛별 1개 이상 제출 기록

### 8-2. 유닛별 메트릭 키 불일치 문제
- `submitted_data` 구조가 유닛별로 다르고, 과거 데이터는 필드명이 다를 수 있음
- 파서에서 `.get('key', 0)` 방어 코딩 필수
- 0점 데이터는 "미평가"로 처리 (약점 집계에서 제외)

### 8-3. 약점 진단 메시지 (WEAKNESS_LEARNING_ROADMAP의 'diagnosis')
- 사전 정의된 진단이므로 사용자 실제 데이터와 100% 맞지 않을 수 있음
- Phase 3 (AI 개인화)에서 "너는 구체적으로..."로 시작하는 개인화된 진단 추가 가능
- MVP: 사전 정의 진단으로도 충분 (일반적이지만 충분히 설득력 있음)

### 8-4. is_best_score 필터
- 분석 시 `is_best_score=True` 기록만 사용 (최고 점수 기록)
- 최신 학습 상태를 반영하기 위해 최근 3회 가중치 2배 적용

### 8-5. WEAKNESS_LEARNING_ROADMAP 유지보수
- 이정표는 하드코딩된 딕셔너리 (roadmap_service.py)
- 향후 관리 페이지를 만들어 DB 기반으로 관리 가능
- MVP: 파이썬 딕셔너리로 충분

---

## 9. 구현 가능성 확인

### 9-1. 왜 빠르게 구현 가능한가

```
✅ submitted_data에 이미 모든 메트릭이 저장됨 (새 데이터 수집 불필요)
✅ Phase 1~2는 LLM 비용 0 (순수 데이터 집계)
✅ WEAKNESS_LEARNING_ROADMAP은 기본 개념만 사전 정의 (확장 쉬움)
✅ activity_service.py 한 줄만 추가해서 자동 갱신 연결 가능
✅ 이미 작동하는 API 아키텍처 재활용
```

### 9-2. 이정표 구축의 장점

| 기존 (점수 + 피드백) | 개선 (학습 이정표) |
|---|---|
| "75점 받았어요" | "현재: 45점 → 공부: Defensive Programming → 목표: 70점" |
| "edge_case 처리 부족" | "왜?: 실무 장애 유발 / 공부할 것: 3가지 (60+30+20분) / 다음: Unit 1 재도전" |
| "다음에 뭘 해야 하지?" | "이 로드맵을 따르면 70점에 도달할 수 있어요" |

### 9-3. 확장 방향

```
MVP (이 계획):
- Phase 1: 약점 분석 + 저장
- Phase 2: 이정표 제시 (사전 정의)

추가 가능 (향후):
- Phase 3: AI 개인화
- 진행도 기반 자동 다음 이정표 추천
- 관리자 페이지 (이정표 편집)
- 멘토 매칭 (비슷한 약점의 사용자)
```

---

## 10. 파일 구조 정리

### 백엔드 신규 파일
```
backend/
├── core/
│   ├── models/
│   │   └── activity_model.py (UserWeaknessProfile 추가)
│   │
│   ├── services/
│   │   ├── weakness_service.py (NEW: 약점 분석)
│   │   ├── roadmap_service.py (NEW: 이정표 생성)
│   │   └── activity_service.py (수정: update_weakness_profile 호출 추가)
│   │
│   └── views/
│       ├── weakness_view.py (NEW: UserWeaknessView)
│       └── roadmap_view.py (NEW: UserRoadmapView, WeaknessSingleRoadmapView)
│
└── urls.py (수정: 새 엔드포인트 4개 등록)
```

### 프론트엔드 신규 파일
```
frontend/src/
├── features/
│   └── learning/ (NEW 폴더)
│       ├── services/
│       │   └── RoadmapService.js
│       │
│       └── components/
│           ├── LearningRoadmap.vue (메인)
│           ├── WeaknessSummary.vue
│           ├── RoadmapCard.vue (아코디언 카드)
│           └── ProgressTracker.vue
│
├── views/
│   └── LandingView.vue (수정: "내 학습 이정표" 버튼 추가)
│
└── App.vue (수정: 이정표 모달 라우팅)
```

---

*작성일: 2026-02-22*
*상태: 단계별 구현 계획 완료, 개발 준비 완료*
*예상 개발 기간: Phase 1~2 총 4~5일, Phase 3 추가 2~3일*
