# AI-GYM SWAN Architecture Guide

**SWAN (State-Worker Agent Network)** - AI 기반 학습 분석 및 멘토링 시스템

## 📋 목차

1. [시스템 개요](#시스템-개요)
2. [아키텍처 다이어그램](#아키텍처-다이어그램)
3. [데이터 흐름](#데이터-흐름)
4. [Worker 파이프라인](#worker-파이프라인)
5. [도구 (Tools) 상세](#도구-tools-상세)
6. [상태 관리 (AgentState)](#상태-관리-agentstate)
7. [프론트엔드 렌더링](#프론트엔드-렌더링)
8. [설계 원칙](#설계-원칙)
9. [확장 가이드](#확장-가이드)

---

## 시스템 개요

### 핵심 목표
AI-GYM의 SWAN 아키텍처는 사용자의 학습 데이터를 수집, 분석하여 개인화된 AI 멘토링을 제공하는 시스템입니다.

### 주요 특징
- **Worker 기반 파이프라인**: 각 작업을 독립적인 Worker로 분리하여 유지보수성 향상
- **상태 중심 설계**: AgentState 객체가 모든 Worker를 통과하며 점진적으로 데이터 축적
- **도구 추상화**: 데이터 수집을 Tool 클래스로 캡슐화하여 재사용성 확보
- **AI 기반 분석**: GPT-4o-mini를 활용한 지능형 멘토링 메시지 생성
- **동적 콘텐츠 추천**: YouTube Data API를 통한 실시간 학습 자료 검색

---

## 아키텍처 다이어그램

### 1. 전체 시스템 구조

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend (Vue 3)                             │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  LearningAnalytics.vue                                      │    │
│  │  - 분석 요청 버튼                                             │    │
│  │  - 로딩 상태 관리                                             │    │
│  │  - 결과 시각화 (요약/레이더/성장/추천/영상)                      │    │
│  └─────────────────┬──────────────────────────────────────────┘    │
│                    │ POST /api/core/analytics/report/              │
└────────────────────┼───────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Backend (Django REST API)                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  AnalyticsAgentView.post()                                    │  │
│  │  - 사용자 인증 확인                                             │  │
│  │  - NetworkOrchestrator 초기화                                  │  │
│  │  - 파이프라인 실행                                              │  │
│  │  - 결과 반환 (report, analysis, growth_analysis, peers)        │  │
│  └────────────────┬─────────────────────────────────────────────┘  │
│                   │                                                 │
│                   ▼                                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │           NetworkOrchestrator                                 │  │
│  │  ┌─────────────────────────────────────────────────────────┐ │  │
│  │  │ Workers Pipeline (순차 실행)                              │ │  │
│  │  │                                                           │ │  │
│  │  │  1. CollectorWorker      ────────┐                       │ │  │
│  │  │     ↓ (state 전달)                │                       │ │  │
│  │  │  2. AnalyzerWorker        Tools ──┤                       │ │  │
│  │  │     ↓                             │                       │ │  │
│  │  │  3. GrowthDeltaWorker     ────────┤                       │ │  │
│  │  │     ↓                             │                       │ │  │
│  │  │  4. RecommenderWorker     ────────┘                       │ │  │
│  │  │                                                           │ │  │
│  │  └─────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Tools (데이터 수집 계층)                                       │  │
│  │  - ToolGetAllSolved: 풀이한 문제 목록                           │  │
│  │  - ToolGetPseudoMetrics: Pseudo Practice 상세 평가             │  │
│  │  - ToolGetBugMetrics: Bug Hunt 상세 평가                       │  │
│  │  - ToolGetSystemMetrics: System Architecture 평가              │  │
│  │  - ToolGetPeers: 리더보드 및 순위 정보                          │  │
│  │  - ToolGetReferences: 교육 참고 자료                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  External Services                                            │  │
│  │  - OpenAI GPT-4o-mini (AI 멘토링)                             │  │
│  │  - YouTube Data API v3 (동영상 검색)                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 2. Worker 파이프라인 상세

```
User Request (POST /api/core/analytics/report/)
         │
         ▼
   ┌─────────────────────────────────────────────────────┐
   │        NetworkOrchestrator.run(state)                │
   │  초기 state = {                                       │
   │    'user_id': request.user.id,                       │
   │    'user': request.user,                             │
   │    'raw_data': {},                                   │
   │    'analysis': {},                                   │
   │    'growth_analysis': {},                            │
   │    'report': {}                                      │
   │  }                                                   │
   └────────────────┬────────────────────────────────────┘
                    │
                    ▼
   ┌─────────────────────────────────────────────────────┐
   │  Worker 1: CollectorWorker                          │
   │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
   │  역할: 사용자 학습 데이터 수집                         │
   │                                                     │
   │  Tools 사용:                                        │
   │  • ToolGetAllSolved()                              │
   │    → state['raw_data']['solved_list']              │
   │                                                     │
   │  • ToolGetPseudoMetrics()                          │
   │    → state['raw_data']['pseudo_metrics']           │
   │                                                     │
   │  • ToolGetBugMetrics()                             │
   │    → state['raw_data']['bug_metrics']              │
   │                                                     │
   │  • ToolGetSystemMetrics()                          │
   │    → state['raw_data']['system_metrics']           │
   │                                                     │
   │  • ToolGetPeers()                                  │
   │    → state['raw_data']['peers']                    │
   │                                                     │
   │  출력: state (raw_data 필드 채워짐)                  │
   └────────────────┬────────────────────────────────────┘
                    │
                    ▼
   ┌─────────────────────────────────────────────────────┐
   │  Worker 2: AnalyzerWorker                           │
   │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
   │  역할: 수집된 데이터를 분석 가능한 형태로 가공         │
   │                                                     │
   │  처리 로직:                                         │
   │  1. Pseudo Practice 분석                           │
   │     - 각 차원별(정합성/추상화/예외처리/구현력/설계력)  │
   │       점수 배열 생성                                 │
   │     → state['analysis']['radar']['pseudo']         │
   │                                                     │
   │  2. Bug Hunt 분석                                  │
   │     - 5개 평가 항목별 점수 배열 생성                  │
   │     → state['analysis']['radar']['bug']            │
   │                                                     │
   │  3. System Architecture 분석                       │
   │     - 총점 배열 생성                                │
   │     → state['analysis']['radar']['system']         │
   │                                                     │
   │  4. 통계 계산                                       │
   │     - 전체 평균, 최대/최소값                         │
   │     → state['analysis']['stats']                   │
   │                                                     │
   │  출력: state (analysis 필드 채워짐)                  │
   └────────────────┬────────────────────────────────────┘
                    │
                    ▼
   ┌─────────────────────────────────────────────────────┐
   │  Worker 3: GrowthDeltaWorker (NEW!)                 │
   │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
   │  역할: 시계열 성장 추세 분석                          │
   │                                                     │
   │  처리 로직:                                         │
   │  1. Pseudo Practice 성장 분석                       │
   │     for 각 차원 in [정합성, 추상화, 예외처리, ...]:   │
   │       scores = state['analysis']['radar']['pseudo'][차원] │
   │       trend = _calculate_trend(scores)             │
   │       if trend:                                    │
   │         signals.append({                           │
   │           'area': 차원,                            │
   │           'delta': recent_avg - early_avg,        │
   │           'change_rate': (delta/early_avg)*100,   │
   │           'trend': '상승'|'정체'|'하락',            │
   │           'emoji': 📈|➡️|📉,                       │
   │           'evidence': "초기 X점 → 최근 Y점",        │
   │           'interpretation': "분석 메시지"           │
   │         })                                         │
   │                                                     │
   │  2. Bug Hunt 성장 분석 (동일 로직)                   │
   │  3. System Architecture 성장 분석                   │
   │                                                     │
   │  알고리즘: _calculate_trend(scores)                 │
   │    - 데이터 3개 미만: None 반환                      │
   │    - split_size = max(2, min(5, len//3))          │
   │    - early_window = scores[:split_size]            │
   │    - recent_window = scores[-split_size:]          │
   │    - delta = recent_avg - early_avg                │
   │    - direction = '상승'(delta>5) | '하락'(delta<-5) | '정체' │
   │                                                     │
   │  출력:                                              │
   │  state['growth_analysis'] = {                      │
   │    'signals': [signal1, signal2, ...],             │
   │    'summary': {                                    │
   │      'improving_areas': 2,                         │
   │      'stagnant_areas': 1,                          │
   │      'declining_areas': 0                          │
   │    }                                               │
   │  }                                                 │
   └────────────────┬────────────────────────────────────┘
                    │
                    ▼
   ┌─────────────────────────────────────────────────────┐
   │  Worker 4: RecommenderWorker                        │
   │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
   │  역할: AI 기반 멘토링 및 추천 생성                    │
   │                                                     │
   │  처리 로직:                                         │
   │  1. GPT 프롬프트 구성                               │
   │     context = {                                    │
   │       'solved': state['raw_data']['solved_list'],  │
   │       'radar': state['analysis']['radar'],         │
   │       'stats': state['analysis']['stats'],         │
   │       'growth': state['growth_analysis'],  // NEW! │
   │       'peers': state['raw_data']['peers']          │
   │     }                                              │
   │                                                     │
   │  2. OpenAI API 호출                                │
   │     model: gpt-4o-mini                             │
   │     response_format: json_object                   │
   │     temperature: 0.7                               │
   │                                                     │
   │  3. 응답 파싱                                       │
   │     gpt_response = {                               │
   │       'summary': "전체 학습 상태 요약",              │
   │       'wizard_comment': "Coduck Wizard의 한마디",   │
   │       'advice': [                                  │
   │         {                                          │
   │           'type': 'strength'|'weakness'|'growth',  │
   │           'area': '분야명',                         │
   │           'message': '조언 메시지'                  │
   │         }                                          │
   │       ],                                           │
   │       'recommended_missions': [                    │
   │         {                                          │
   │           'title': '미션명',                        │
   │           'reason': '추천 이유'                     │
   │         }                                          │
   │       ]                                            │
   │     }                                              │
   │                                                     │
   │  4. 동영상 추천 (Antigravity 기능)                  │
   │     weakness_area = advice 중 가장 심각한 weakness  │
   │     youtube_results = search_youtube(weakness_area) │
   │     OR                                             │
   │     db_reference = ToolGetReferences(weakness_area) │
   │                                                     │
   │     if youtube_results:                            │
   │       gpt_response['recommended_video'] = {        │
   │         'title': video.title,                      │
   │         'url': video.url,                          │
   │         'reason': "왜 이 영상을 추천하는지",          │
   │         'source': 'youtube'                        │
   │       }                                            │
   │     elif db_reference:                            │
   │       gpt_response['recommended_video'] = {        │
   │         'title': ref.detail_title,                 │
   │         'url': ref.content_data['url'],            │
   │         'reason': ref.content_data['description'], │
   │         'source': 'database'                       │
   │       }                                            │
   │                                                     │
   │  출력: state['report'] = gpt_response               │
   └────────────────┬────────────────────────────────────┘
                    │
                    ▼
   ┌─────────────────────────────────────────────────────┐
   │  NetworkOrchestrator returns final state            │
   │                                                     │
   │  return {                                          │
   │    'report': state['report'],                      │
   │    'analysis': state['analysis'],                  │
   │    'growth_analysis': state['growth_analysis'],    │
   │    'peers': state['raw_data']['peers']             │
   │  }                                                 │
   └────────────────┬────────────────────────────────────┘
                    │
                    ▼
              JSON Response to Frontend
```

---

## 데이터 흐름

### AgentState 진화 과정

```python
# 초기 상태 (AnalyticsAgentView에서 생성)
state = {
    'user_id': 123,
    'user': User object,
    'raw_data': {},
    'analysis': {},
    'growth_analysis': {},
    'report': {}
}

# CollectorWorker 통과 후
state = {
    'user_id': 123,
    'user': User object,
    'raw_data': {
        'solved_list': [
            {
                'practice_id': 'unit0101',
                'practice_title': 'Pseudo Code Training',
                'detail_type': 'PROBLEM',
                'detail_title': 'Array Manipulation',
                'solved_at': '2026-02-09T10:30:00Z',
                'score': 95,
                'feedback': {...}
            },
            ...
        ],
        'pseudo_metrics': [
            {
                'problem_id': 'unit0101',
                'dimensions': {
                    '정합성': 95,
                    '추상화': 88,
                    '예외처리': 92,
                    '구현력': 90,
                    '설계력': 87
                }
            },
            ...
        ],
        'bug_metrics': [...],
        'system_metrics': [...],
        'peers': {
            'rank': 'Gold',
            'global_rank': 15,
            'total_members': 150,
            'percentile': 10,
            'total_points': 8500
        }
    },
    'analysis': {},
    'growth_analysis': {},
    'report': {}
}

# AnalyzerWorker 통과 후
state = {
    'user_id': 123,
    'user': User object,
    'raw_data': {...},  # 위와 동일
    'analysis': {
        'radar': {
            'pseudo': {
                '정합성': [95, 88, 92, 90],
                '추상화': [88, 85, 90, 87],
                '예외처리': [92, 95, 88, 93],
                '구현력': [90, 92, 88, 91],
                '설계력': [87, 90, 85, 88]
            },
            'bug': {
                'cause_identification': [18, 17, 19, 20],
                'logic_connection': [16, 18, 17, 19],
                'solution_quality': [19, 18, 20, 19],
                'side_effects': [17, 19, 18, 20],
                'explanation_clarity': [18, 17, 19, 18]
            },
            'system': [85, 90, 88, 92]
        },
        'stats': {
            'avg_pseudo': 89.5,
            'avg_bug': 90.2,
            'avg_system': 88.75,
            'total_solved': 15,
            'completion_rate': 0.75
        }
    },
    'growth_analysis': {},
    'report': {}
}

# GrowthDeltaWorker 통과 후
state = {
    'user_id': 123,
    'user': User object,
    'raw_data': {...},
    'analysis': {...},
    'growth_analysis': {
        'signals': [
            {
                'area': '정합성',
                'emoji': '📈',
                'trend': '상승',
                'delta': 6.5,
                'change_rate': 7.2,
                'evidence': '초기 평균 90.0점에서 최근 평균 96.5점으로 상승',
                'interpretation': '논리적 정합성 검증 능력이 꾸준히 향상되고 있습니다. 엣지 케이스 처리가 강화되었습니다.'
            },
            {
                'area': '추상화',
                'emoji': '➡️',
                'trend': '정체',
                'delta': 1.2,
                'change_rate': 1.4,
                'evidence': '초기 평균 86.5점에서 최근 평균 87.7점으로 소폭 상승',
                'interpretation': '추상화 수준이 정체 상태입니다. 더 복잡한 문제를 통해 돌파가 필요합니다.'
            }
        ],
        'summary': {
            'improving_areas': 2,
            'stagnant_areas': 2,
            'declining_areas': 1
        }
    },
    'report': {}
}

# RecommenderWorker 통과 후 (최종 상태)
state = {
    'user_id': 123,
    'user': User object,
    'raw_data': {...},
    'analysis': {...},
    'growth_analysis': {...},
    'report': {
        'summary': '지난 2주간 15개의 미션을 완료하며 전반적으로 우수한 성장세를 보이고 있습니다. 특히 Pseudo Code의 정합성과 구현력에서 두드러진 향상이 관찰됩니다.',
        'wizard_comment': '추상화 능력 향상을 위해 더 복잡한 설계 패턴 문제에 도전해보세요! 현재 Gold 티어 상위 10%의 실력을 보유하고 계십니다.',
        'advice': [
            {
                'type': 'strength',
                'area': 'Pseudo Code - 정합성',
                'message': '논리적 정합성이 뛰어나며, 엣지 케이스를 잘 포착합니다. 이 강점을 유지하세요!'
            },
            {
                'type': 'weakness',
                'area': 'Bug Hunt - 부작용 분석',
                'message': '버그 수정 시 발생할 수 있는 부작용 예측이 다소 부족합니다. 전체 시스템 영향도를 고려하는 연습이 필요합니다.'
            },
            {
                'type': 'growth',
                'area': 'System Architecture',
                'message': '아키텍처 설계 점수가 꾸준히 상승 중입니다. 확장성을 더욱 강화하면 Platinum 티어 진입이 가능합니다.'
            }
        ],
        'recommended_missions': [
            {
                'title': 'Advanced Exception Handling',
                'reason': '예외 처리 역량 강화를 위한 심화 문제'
            },
            {
                'title': 'Design Pattern Masterclass',
                'reason': '추상화 능력 향상을 위한 패턴 학습'
            }
        ],
        'recommended_video': {
            'title': 'Effective Debugging with Python',
            'url': 'https://www.youtube.com/watch?v=6TITnB31ae4',
            'reason': '부작용 분석 능력 향상을 위한 디버깅 기법 학습',
            'source': 'database'
        }
    }
}
```

---

## Worker 파이프라인

### BaseWorker 추상 클래스

```python
from abc import ABC, abstractmethod

class BaseWorker(ABC):
    """
    모든 Worker가 상속하는 추상 베이스 클래스

    역할: Worker 간 일관된 인터페이스 제공
    """
    @abstractmethod
    def work(self, state: dict) -> dict:
        """
        Worker의 핵심 로직 구현

        Args:
            state: 현재까지의 AgentState

        Returns:
            수정된 AgentState (원본 state를 변경하여 반환)
        """
        pass
```

### 1. CollectorWorker

```python
class CollectorWorker(BaseWorker):
    """
    데이터 수집 전담 Worker

    역할:
    - 사용자의 모든 학습 기록을 DB에서 수집
    - Tool 객체를 사용하여 데이터 캡슐화
    - state['raw_data']에 원본 데이터 저장

    설계 원칙:
    - Single Responsibility: 오직 데이터 수집만 담당
    - 데이터 가공/분석은 다음 Worker에게 위임
    """

    def work(self, state):
        user_id = state['user_id']

        # Tool 인스턴스 생성
        tool_solved = ToolGetAllSolved(user_id)
        tool_pseudo = ToolGetPseudoMetrics(user_id)
        tool_bug = ToolGetBugMetrics(user_id)
        tool_system = ToolGetSystemMetrics(user_id)
        tool_peers = ToolGetPeers(user_id)

        # 각 Tool 실행하여 raw_data에 저장
        state['raw_data']['solved_list'] = tool_solved.run()
        state['raw_data']['pseudo_metrics'] = tool_pseudo.run()
        state['raw_data']['bug_metrics'] = tool_bug.run()
        state['raw_data']['system_metrics'] = tool_system.run()
        state['raw_data']['peers'] = tool_peers.run()

        return state
```

### 2. AnalyzerWorker

```python
class AnalyzerWorker(BaseWorker):
    """
    데이터 분석 전담 Worker

    역할:
    - raw_data를 분석 가능한 형태로 변환
    - 레이더 차트용 데이터 구조 생성
    - 통계 지표 계산

    출력 구조:
    state['analysis'] = {
        'radar': {
            'pseudo': {차원: [점수 배열]},
            'bug': {항목: [점수 배열]},
            'system': [점수 배열]
        },
        'stats': {...}
    }
    """

    def work(self, state):
        radar_data = {'pseudo': {}, 'bug': {}, 'system': []}

        # 1. Pseudo Practice 분석
        pseudo_dims = ['정합성', '추상화', '예외처리', '구현력', '설계력']
        for dim in pseudo_dims:
            radar_data['pseudo'][dim] = []

        for metric in state['raw_data']['pseudo_metrics']:
            dims = metric.get('dimensions', {})
            for dim in pseudo_dims:
                if dim in dims:
                    radar_data['pseudo'][dim].append(dims[dim])

        # 2. Bug Hunt 분석
        bug_fields = [
            'cause_identification',
            'logic_connection',
            'solution_quality',
            'side_effects',
            'explanation_clarity'
        ]
        for field in bug_fields:
            radar_data['bug'][field] = []

        for metric in state['raw_data']['bug_metrics']:
            for field in bug_fields:
                if field in metric:
                    radar_data['bug'][field].append(metric[field])

        # 3. System Architecture 분석
        for metric in state['raw_data']['system_metrics']:
            if 'total_score' in metric:
                radar_data['system'].append(metric['total_score'])

        state['analysis']['radar'] = radar_data

        # 4. 통계 계산
        state['analysis']['stats'] = self._calculate_stats(radar_data)

        return state

    def _calculate_stats(self, radar_data):
        """평균, 최대/최소, 완료율 등 통계 계산"""
        # 구현 생략
        pass
```

### 3. GrowthDeltaWorker

```python
class GrowthDeltaWorker(BaseWorker):
    """
    성장 추세 분석 전담 Worker (2026-02-10 신규 추가)

    역할:
    - 시계열 데이터에서 초기 vs 최근 성과 비교
    - 상승/정체/하락 트렌드 분류
    - 성장 시그널 생성

    알고리즘:
    - Early Window: 초기 데이터의 1/3 (최소 2개, 최대 5개)
    - Recent Window: 최근 데이터의 1/3
    - Delta = Recent Average - Early Average
    - Trend: delta > 5 → 상승, delta < -5 → 하락, 그 외 → 정체

    출력:
    state['growth_analysis'] = {
        'signals': [signal1, signal2, ...],
        'summary': {
            'improving_areas': count,
            'stagnant_areas': count,
            'declining_areas': count
        }
    }
    """

    def work(self, state):
        radar = state['analysis']['radar']
        signals = []

        # 1. Pseudo Practice 성장 분석
        for dim, scores in radar.get('pseudo', {}).items():
            trend = self._calculate_trend(scores)
            if trend:
                signals.append({
                    'area': f'Pseudo - {dim}',
                    'emoji': '📈' if trend['direction'] == '상승' else
                             '📉' if trend['direction'] == '하락' else '➡️',
                    'trend': trend['direction'],
                    'delta': trend['delta'],
                    'change_rate': trend['change_rate'],
                    'evidence': trend['evidence'],
                    'interpretation': self._interpret_trend(dim, trend)
                })

        # 2. Bug Hunt 성장 분석 (동일 로직)
        # 3. System Architecture 성장 분석 (동일 로직)

        # Summary 생성
        summary = {
            'improving_areas': sum(1 for s in signals if s['trend'] == '상승'),
            'stagnant_areas': sum(1 for s in signals if s['trend'] == '정체'),
            'declining_areas': sum(1 for s in signals if s['trend'] == '하락')
        }

        state['growth_analysis'] = {
            'signals': signals,
            'summary': summary
        }

        return state

    def _calculate_trend(self, scores):
        """
        시계열 점수 배열에서 성장 추세 계산

        Args:
            scores: [90, 88, 92, 95, 87, 93, 96, 94]

        Returns:
            {
                'direction': '상승'|'정체'|'하락',
                'delta': float (recent_avg - early_avg),
                'change_rate': float (변화율 %),
                'evidence': str (증거 문장),
                'early_avg': float,
                'recent_avg': float
            }
        """
        if len(scores) < 3:
            return None

        # Window 크기 계산 (최소 2, 최대 5, 기본 1/3)
        split_size = max(2, min(5, len(scores) // 3))

        early_scores = scores[:split_size]
        recent_scores = scores[-split_size:]

        early_avg = sum(early_scores) / len(early_scores)
        recent_avg = sum(recent_scores) / len(recent_scores)

        delta = recent_avg - early_avg
        change_rate = (delta / early_avg * 100) if early_avg > 0 else 0

        # 추세 분류
        if delta > 5:
            direction = '상승'
        elif delta < -5:
            direction = '하락'
        else:
            direction = '정체'

        evidence = f"초기 평균 {early_avg:.1f}점에서 최근 평균 {recent_avg:.1f}점으로 {'상승' if delta > 0 else '하락'}"

        return {
            'direction': direction,
            'delta': round(delta, 1),
            'change_rate': round(change_rate, 1),
            'evidence': evidence,
            'early_avg': round(early_avg, 1),
            'recent_avg': round(recent_avg, 1)
        }

    def _interpret_trend(self, area, trend):
        """트렌드에 대한 해석 메시지 생성"""
        if trend['direction'] == '상승':
            return f"{area} 영역에서 지속적인 성장이 관찰됩니다. 현재 방향을 유지하세요."
        elif trend['direction'] == '하락':
            return f"{area} 영역에서 점수가 하락하고 있습니다. 기본 개념을 재점검할 필요가 있습니다."
        else:
            return f"{area} 영역이 정체 상태입니다. 더 어려운 문제로 돌파구를 찾아보세요."
```

### 4. RecommenderWorker

```python
class RecommenderWorker(BaseWorker):
    """
    AI 기반 추천 생성 Worker

    역할:
    - GPT-4o-mini를 활용한 개인화 멘토링
    - 동적 영상/자료 추천 (YouTube API 연동)
    - 최종 리포트 생성

    외부 의존성:
    - OpenAI API (GPT-4o-mini)
    - YouTube Data API v3 (선택적)
    """

    def work(self, state):
        # 1. GPT 프롬프트 구성
        prompt = self._build_prompt(state)

        # 2. OpenAI API 호출
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )

        # 3. 응답 파싱
        gpt_output = json.loads(response.choices[0].message.content)

        # 4. 동영상 추천 (Antigravity 기능)
        video = self._recommend_video(gpt_output, state)
        if video:
            gpt_output['recommended_video'] = video

        state['report'] = gpt_output
        return state

    def _build_prompt(self, state):
        """
        GPT에게 전달할 컨텍스트 구성

        포함 정보:
        - 풀이한 문제 목록
        - 레이더 차트 데이터
        - 성장 추세 (GrowthDeltaWorker 결과)
        - 리더보드 순위
        """
        context = {
            'solved_problems': state['raw_data']['solved_list'],
            'radar_data': state['analysis']['radar'],
            'statistics': state['analysis']['stats'],
            'growth_trends': state['growth_analysis'],  # NEW!
            'peer_ranking': state['raw_data']['peers']
        }

        prompt = f"""
        다음은 사용자의 학습 데이터입니다:

        {json.dumps(context, ensure_ascii=False, indent=2)}

        위 데이터를 분석하여 다음 형식의 JSON을 생성하세요:
        {{
            "summary": "전체 학습 상태 요약 (2-3문장)",
            "wizard_comment": "Coduck Wizard의 격려 한마디",
            "advice": [
                {{"type": "strength", "area": "분야", "message": "조언"}},
                {{"type": "weakness", "area": "분야", "message": "조언"}},
                {{"type": "growth", "area": "분야", "message": "조언"}}
            ],
            "recommended_missions": [
                {{"title": "미션명", "reason": "추천 이유"}}
            ]
        }}

        **중요**:
        - growth_trends의 상승/하락 시그널을 반드시 반영하세요.
        - 하락 영역이 있다면 weakness로 강조하세요.
        """

        return prompt

    def _recommend_video(self, gpt_output, state):
        """
        약점 영역에 맞는 학습 영상 추천

        우선순위:
        1. YouTube Data API v3로 실시간 검색
        2. DB에 저장된 REFERENCE 타입 자료
        """
        # weakness 추출
        weaknesses = [adv for adv in gpt_output.get('advice', [])
                      if adv.get('type') == 'weakness']

        if not weaknesses:
            return None

        target_area = weaknesses[0]['area']

        # 1. YouTube API 시도
        youtube_result = self._search_youtube(target_area)
        if youtube_result:
            return {
                'title': youtube_result['title'],
                'url': youtube_result['url'],
                'reason': f"{target_area} 약점 보완을 위한 추천 영상",
                'source': 'youtube'
            }

        # 2. DB Reference 시도
        tool = ToolGetReferences(target_area)
        references = tool.run()

        if references:
            ref = references[0]
            return {
                'title': ref['title'],
                'url': ref['url'],
                'reason': ref['description'],
                'source': 'database'
            }

        return None

    def _search_youtube(self, keyword):
        """YouTube Data API v3를 사용한 동영상 검색"""
        try:
            youtube = build('youtube', 'v3',
                           developerKey=settings.YOUTUBE_API_KEY)

            request = youtube.search().list(
                part='snippet',
                q=f"{keyword} programming tutorial",
                type='video',
                maxResults=1,
                relevanceLanguage='ko'
            )

            response = request.execute()

            if response['items']:
                item = response['items'][0]
                return {
                    'title': item['snippet']['title'],
                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                }
        except Exception as e:
            print(f"YouTube API Error: {e}")

        return None
```

### NetworkOrchestrator

```python
class NetworkOrchestrator:
    """
    Worker 파이프라인 실행 오케스트레이터

    역할:
    - Worker 실행 순서 관리
    - 에러 핸들링
    - 상태 전달

    설계 패턴:
    - Pipeline Pattern: 각 Worker가 순차적으로 state 변환
    - Chain of Responsibility: 에러 발생 시 다음 Worker로 전파
    """

    def __init__(self):
        self.workers = [
            CollectorWorker(),
            AnalyzerWorker(),
            GrowthDeltaWorker(),
            RecommenderWorker()
        ]

    def run(self, initial_state):
        """
        Worker 파이프라인 실행

        Args:
            initial_state: 초기 AgentState

        Returns:
            최종 AgentState (모든 Worker 통과 후)
        """
        state = initial_state

        for worker in self.workers:
            try:
                print(f"[NetworkOrchestrator] Running {worker.__class__.__name__}...")
                state = worker.work(state)
                print(f"[NetworkOrchestrator] {worker.__class__.__name__} completed.")
            except Exception as e:
                print(f"[NetworkOrchestrator] Error in {worker.__class__.__name__}: {e}")
                # 에러 발생 시에도 다음 Worker 실행 (부분 실패 허용)
                # 또는 즉시 중단하려면 raise

        return state
```

---

## 도구 (Tools) 상세

### BaseTool 추상 클래스

```python
class BaseTool(ABC):
    """
    모든 Tool이 상속하는 추상 베이스 클래스

    역할:
    - DB 쿼리 로직 캡슐화
    - 일관된 인터페이스 제공
    """

    def __init__(self, user_id):
        self.user_id = user_id

    @abstractmethod
    def run(self):
        """Tool의 핵심 로직 (DB 쿼리 등)"""
        pass
```

### 1. ToolGetAllSolved

```python
class ToolGetAllSolved(BaseTool):
    """
    사용자가 풀이한 모든 문제 목록 조회

    쿼리:
    - UserAnswer 모델에서 user_id로 필터링
    - PracticeDetail과 JOIN하여 문제 정보 포함
    - 최신순 정렬

    반환 형식:
    [
        {
            'practice_id': 'unit0101',
            'practice_title': 'Pseudo Code Training',
            'detail_type': 'PROBLEM',
            'detail_title': 'Array Manipulation',
            'solved_at': '2026-02-09T10:30:00Z',
            'score': 95,
            'feedback': {...}
        },
        ...
    ]
    """

    def run(self):
        answers = UserAnswer.objects.filter(
            user_id=self.user_id
        ).select_related('practice_detail').order_by('-create_date')

        return [
            {
                'practice_id': ans.practice_detail.practice_id,
                'practice_title': ans.practice_detail.practice.title,
                'detail_type': ans.practice_detail.detail_type,
                'detail_title': ans.practice_detail.detail_title,
                'solved_at': ans.create_date.isoformat(),
                'score': ans.score or 0,
                'feedback': ans.feedback_data or {}
            }
            for ans in answers
        ]
```

### 2. ToolGetPseudoMetrics

```python
class ToolGetPseudoMetrics(BaseTool):
    """
    Pseudo Practice 상세 평가 지표 조회

    쿼리:
    - UserAnswer에서 Pseudo Practice 타입 필터링
    - feedback_data에서 5개 차원 점수 추출

    반환 형식:
    [
        {
            'problem_id': 'unit0101',
            'dimensions': {
                '정합성': 95,
                '추상화': 88,
                '예외처리': 92,
                '구현력': 90,
                '설계력': 87
            },
            'solved_at': '2026-02-09T10:30:00Z'
        },
        ...
    ]
    """

    def run(self):
        answers = UserAnswer.objects.filter(
            user_id=self.user_id,
            practice_detail__practice_id__startswith='unit'
        ).order_by('create_date')

        metrics = []
        for ans in answers:
            feedback = ans.feedback_data or {}
            if 'dimensions' in feedback:
                metrics.append({
                    'problem_id': ans.practice_detail_id,
                    'dimensions': feedback['dimensions'],
                    'solved_at': ans.create_date.isoformat()
                })

        return metrics
```

### 3. ToolGetBugMetrics

```python
class ToolGetBugMetrics(BaseTool):
    """
    Bug Hunt 상세 평가 지표 조회

    평가 항목 (각 20점 만점):
    - cause_identification: 원인 식별
    - logic_connection: 논리 연결
    - solution_quality: 해결 품질
    - side_effects: 부작용 고려
    - explanation_clarity: 설명 명확성

    반환 형식:
    [
        {
            'problem_id': 'bug0101',
            'cause_identification': 18,
            'logic_connection': 17,
            'solution_quality': 19,
            'side_effects': 16,
            'explanation_clarity': 18,
            'total_score': 88,
            'solved_at': '2026-02-08T15:20:00Z'
        },
        ...
    ]
    """

    def run(self):
        answers = UserAnswer.objects.filter(
            user_id=self.user_id,
            practice_detail__practice_id__startswith='bug'
        ).order_by('create_date')

        metrics = []
        for ans in answers:
            feedback = ans.feedback_data or {}
            metrics.append({
                'problem_id': ans.practice_detail_id,
                'cause_identification': feedback.get('cause_identification', 0),
                'logic_connection': feedback.get('logic_connection', 0),
                'solution_quality': feedback.get('solution_quality', 0),
                'side_effects': feedback.get('side_effects', 0),
                'explanation_clarity': feedback.get('explanation_clarity', 0),
                'total_score': feedback.get('total_score', 0),
                'solved_at': ans.create_date.isoformat()
            })

        return metrics
```

### 4. ToolGetSystemMetrics

```python
class ToolGetSystemMetrics(BaseTool):
    """
    System Architecture 평가 지표 조회

    평가 방식:
    - 종합 점수 (0-100점)

    반환 형식:
    [
        {
            'problem_id': 'arch0101',
            'total_score': 85,
            'solved_at': '2026-02-07T11:00:00Z'
        },
        ...
    ]
    """

    def run(self):
        answers = UserAnswer.objects.filter(
            user_id=self.user_id,
            practice_detail__practice_id__startswith='arch'
        ).order_by('create_date')

        return [
            {
                'problem_id': ans.practice_detail_id,
                'total_score': ans.score or 0,
                'solved_at': ans.create_date.isoformat()
            }
            for ans in answers
        ]
```

### 5. ToolGetPeers

```python
class ToolGetPeers(BaseTool):
    """
    리더보드 및 순위 정보 조회

    계산 로직:
    - 전체 사용자의 total_score로 순위 계산
    - 백분위 산출
    - 티어 결정 (Bronze/Silver/Gold/Platinum/Diamond)

    반환 형식:
    {
        'rank': 'Gold',
        'global_rank': 15,
        'total_members': 150,
        'percentile': 10,
        'total_points': 8500
    }
    """

    def run(self):
        user = UserProfile.objects.get(id=self.user_id)
        user_score = user.total_score or 0

        # 전체 사용자 수
        total_members = UserProfile.objects.count()

        # 현재 사용자보다 점수가 높은 사용자 수
        higher_count = UserProfile.objects.filter(
            total_score__gt=user_score
        ).count()

        global_rank = higher_count + 1
        percentile = (global_rank / total_members * 100) if total_members > 0 else 0

        # 티어 결정
        if percentile <= 5:
            rank = 'Diamond'
        elif percentile <= 15:
            rank = 'Platinum'
        elif percentile <= 35:
            rank = 'Gold'
        elif percentile <= 65:
            rank = 'Silver'
        else:
            rank = 'Bronze'

        return {
            'rank': rank,
            'global_rank': global_rank,
            'total_members': total_members,
            'percentile': round(percentile, 1),
            'total_points': user_score
        }
```

### 6. ToolGetReferences

```python
class ToolGetReferences(BaseTool):
    """
    교육 참고 자료 조회 (DB Fixtures)

    쿼리:
    - PracticeDetail에서 detail_type='REFERENCE' 필터링
    - keyword와 관련된 자료 검색 (태그 매칭)

    반환 형식:
    [
        {
            'title': 'Effective Debugging with Python',
            'url': 'https://www.youtube.com/watch?v=...',
            'description': '파이썬 디버깅의 기초부터...',
            'tags': ['debug', 'python', 'troubleshooting']
        },
        ...
    ]
    """

    def __init__(self, user_id, keyword=None):
        super().__init__(user_id)
        self.keyword = keyword

    def run(self):
        refs = PracticeDetail.objects.filter(
            detail_type='REFERENCE',
            is_active=True
        )

        if self.keyword:
            # 태그 기반 필터링
            refs = refs.filter(
                content_data__tags__icontains=self.keyword
            )

        return [
            {
                'title': ref.detail_title,
                'url': ref.content_data.get('url'),
                'description': ref.content_data.get('description'),
                'tags': ref.content_data.get('tags', [])
            }
            for ref in refs
        ]
```

---

## 상태 관리 (AgentState)

### AgentState 스키마

```python
AgentState = TypedDict('AgentState', {
    # 사용자 컨텍스트
    'user_id': int,
    'user': UserProfile,

    # 원본 데이터 (CollectorWorker 출력)
    'raw_data': {
        'solved_list': List[dict],
        'pseudo_metrics': List[dict],
        'bug_metrics': List[dict],
        'system_metrics': List[dict],
        'peers': dict
    },

    # 분석 데이터 (AnalyzerWorker 출력)
    'analysis': {
        'radar': {
            'pseudo': Dict[str, List[float]],
            'bug': Dict[str, List[float]],
            'system': List[float]
        },
        'stats': dict
    },

    # 성장 분석 (GrowthDeltaWorker 출력)
    'growth_analysis': {
        'signals': List[dict],
        'summary': dict
    },

    # 최종 리포트 (RecommenderWorker 출력)
    'report': {
        'summary': str,
        'wizard_comment': str,
        'advice': List[dict],
        'recommended_missions': List[dict],
        'recommended_video': dict  # Optional
    }
})
```

---

## 프론트엔드 렌더링

### Vue 컴포넌트 구조

```vue
<template>
  <div class="analytics-container">
    <!-- 1. 헤더 & 분석 버튼 -->
    <header>
      <button @click="fetchAnalysis">Refresh Analysis</button>
    </header>

    <!-- 2. 로딩/빈 상태 -->
    <div v-if="loading">Loading...</div>
    <div v-else-if="!report">Empty State</div>

    <!-- 3. 메인 콘텐츠 -->
    <div v-else>
      <!-- 3-1. 요약 리포트 -->
      <section class="summary-card">
        <div class="wizard-profile">Coduck Wizard</div>
        <p>{{ report.summary }}</p>
        <p>"{{ report.wizard_comment }}"</p>
      </section>

      <!-- 3-2. 성장 추세 (NEW!) -->
      <section v-if="hasGrowthData" class="growth-section">
        <h3>Growth Trends</h3>
        <div class="growth-summary">
          <div class="summary-stat improving">
            {{ growthAnalysis.summary.improving_areas }} 📈
          </div>
          <div class="summary-stat stagnant">
            {{ growthAnalysis.summary.stagnant_areas }} ➡️
          </div>
          <div class="summary-stat declining">
            {{ growthAnalysis.summary.declining_areas }} 📉
          </div>
        </div>

        <div v-for="signal in growthAnalysis.signals" class="growth-signal">
          <span>{{ signal.emoji }} {{ signal.area }}</span>
          <span class="delta">{{ signal.delta > 0 ? '+' : '' }}{{ signal.delta }}점</span>
          <p>{{ signal.evidence }}</p>
          <p>{{ signal.interpretation }}</p>
        </div>
      </section>

      <!-- 3-3. 레이더 차트 & 조언 -->
      <div class="metrics-grid">
        <div class="radar-card">
          <svg><!-- Radar Chart SVG --></svg>
        </div>
        <div class="advice-card">
          <div v-for="item in report.advice" :class="['advice-item', item.type]">
            <span>{{ item.type === 'strength' ? 'STRENGTH' : 'WEAKNESS' }}</span>
            <p>{{ item.message }}</p>
          </div>
        </div>
      </div>

      <!-- 3-4. 추천 미션 -->
      <section class="missions-section">
        <div v-for="mission in report.recommended_missions" class="mission-card">
          <h4>{{ mission.title }}</h4>
          <p>{{ mission.reason }}</p>
        </div>
      </section>

      <!-- 3-5. 추천 영상 -->
      <section v-if="report.recommended_video" class="video-section">
        <h4>{{ report.recommended_video.title }}</h4>
        <button @click="openVideo(report.recommended_video.url)">
          Watch Now
        </button>
      </section>

      <!-- 3-6. 리더보드 순위 -->
      <section class="footer-stats">
        <div>Tier: {{ peers.rank }}</div>
        <div>Rank: {{ peers.global_rank }} / {{ peers.total_members }}</div>
        <div>Points: {{ peers.total_points }}</div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

const loading = ref(false);
const report = ref(null);
const analysis = ref(null);
const growthAnalysis = ref(null);
const peers = ref(null);

const hasGrowthData = computed(() => {
  return growthAnalysis.value?.signals?.length > 0;
});

const fetchAnalysis = async () => {
  loading.value = true;
  try {
    const res = await axios.post('/api/core/analytics/report/');

    report.value = res.data.report;
    analysis.value = res.data.analysis;
    growthAnalysis.value = res.data.growth_analysis;
    peers.value = res.data.peers;
  } catch (err) {
    console.error('Failed to fetch analysis:', err);
  } finally {
    loading.value = false;
  }
};

const openVideo = (url) => {
  window.open(url, '_blank');
};
</script>
```

---

## 설계 원칙

### 1. Separation of Concerns (관심사의 분리)

```
CollectorWorker  → 데이터 수집만 담당
AnalyzerWorker   → 데이터 가공/분석만 담당
GrowthDeltaWorker → 성장 추세 분석만 담당
RecommenderWorker → AI 추천만 담당
```

**장점:**
- 각 Worker의 역할이 명확하여 코드 이해가 쉬움
- 한 Worker 수정이 다른 Worker에 영향을 주지 않음
- 테스트 작성이 용이

### 2. Single Responsibility Principle (단일 책임 원칙)

```python
# Bad Example (한 함수가 모든 것을 수행)
def generate_report(user_id):
    # 데이터 수집
    solved = get_solved(user_id)
    # 분석
    radar = analyze(solved)
    # AI 호출
    gpt_output = call_gpt(radar)
    # 반환
    return gpt_output

# Good Example (각 Worker가 하나의 책임만)
class CollectorWorker:
    def work(self, state):
        state['raw_data'] = collect_data(state['user_id'])
        return state

class AnalyzerWorker:
    def work(self, state):
        state['analysis'] = analyze(state['raw_data'])
        return state
```

### 3. Data Pipeline Pattern (데이터 파이프라인 패턴)

```
Initial State → Worker1 → Worker2 → Worker3 → Worker4 → Final State
     │              │          │          │          │
     └──────────────┴──────────┴──────────┴──────────┘
            각 단계에서 state가 점진적으로 풍부해짐
```

**장점:**
- 데이터 흐름이 직관적
- 중간 결과를 쉽게 디버깅 가능
- Worker 추가/제거가 간단

### 4. Extensibility (확장성)

새로운 기능 추가 시:

```python
# 새로운 Worker 추가 예시
class SentimentAnalysisWorker(BaseWorker):
    """사용자의 학습 만족도 감성 분석"""

    def work(self, state):
        comments = state['raw_data'].get('user_comments', [])
        sentiment_scores = []

        for comment in comments:
            score = analyze_sentiment(comment)
            sentiment_scores.append(score)

        state['analysis']['sentiment'] = {
            'average': sum(sentiment_scores) / len(sentiment_scores),
            'trend': 'positive' if avg > 0.5 else 'negative'
        }

        return state

# NetworkOrchestrator에 추가만 하면 됨
class NetworkOrchestrator:
    def __init__(self):
        self.workers = [
            CollectorWorker(),
            AnalyzerWorker(),
            GrowthDeltaWorker(),
            SentimentAnalysisWorker(),  # 새로운 Worker 추가!
            RecommenderWorker()
        ]
```

### 5. Pure Functions (순수 함수)

Worker 내부의 헬퍼 함수들은 순수 함수로 작성:

```python
# Pure Function (부작용 없음, 동일 입력 → 동일 출력)
def _calculate_trend(scores):
    if len(scores) < 3:
        return None

    early = scores[:len(scores)//3]
    recent = scores[-len(scores)//3:]

    return {
        'delta': sum(recent)/len(recent) - sum(early)/len(early)
    }

# Impure Function (외부 상태 의존, 부작용 발생)
def _calculate_trend_impure(self, scores):
    self.last_trend = ...  # 외부 상태 수정
    api_call_to_log_trend()  # 부작용
    return result
```

---

## 확장 가이드

### 새로운 Practice 타입 추가하기

1. **Tool 추가**

```python
class ToolGetCodeReviewMetrics(BaseTool):
    """Code Review Practice 평가 지표 조회"""

    def run(self):
        answers = UserAnswer.objects.filter(
            user_id=self.user_id,
            practice_detail__practice_id__startswith='review'
        )

        return [
            {
                'problem_id': ans.practice_detail_id,
                'readability_score': ans.feedback_data.get('readability'),
                'security_score': ans.feedback_data.get('security'),
                'performance_score': ans.feedback_data.get('performance')
            }
            for ans in answers
        ]
```

2. **CollectorWorker 수정**

```python
class CollectorWorker(BaseWorker):
    def work(self, state):
        # 기존 코드...

        # 새로운 Tool 추가
        tool_review = ToolGetCodeReviewMetrics(state['user_id'])
        state['raw_data']['code_review_metrics'] = tool_review.run()

        return state
```

3. **AnalyzerWorker 수정**

```python
class AnalyzerWorker(BaseWorker):
    def work(self, state):
        # 기존 코드...

        # Code Review 데이터 분석
        review_data = {
            'readability': [],
            'security': [],
            'performance': []
        }

        for metric in state['raw_data']['code_review_metrics']:
            review_data['readability'].append(metric['readability_score'])
            review_data['security'].append(metric['security_score'])
            review_data['performance'].append(metric['performance_score'])

        state['analysis']['radar']['code_review'] = review_data

        return state
```

4. **프론트엔드 수정**

```vue
<script>
const radarLabels = computed(() => {
  const radar = analysis.value?.radar;
  if (!radar) return ['-', '-', '-', '-', '-'];

  // 기존 코드...

  // Code Review 라벨 추가
  if (radar.code_review) {
    return ['가독성', '보안성', '성능', '유지보수성', '확장성'];
  }

  return ['-', '-', '-', '-', '-'];
});
</script>
```

---

## 디버깅 가이드

### 로깅 포인트

```python
# CollectorWorker
print(f"[CollectorWorker] Collected {len(state['raw_data']['solved_list'])} solved problems")

# AnalyzerWorker
print(f"[AnalyzerWorker] Radar data keys: {state['analysis']['radar'].keys()}")
print(f"[AnalyzerWorker] Pseudo dimensions: {list(state['analysis']['radar']['pseudo'].keys())}")

# GrowthDeltaWorker
print(f"[GrowthDeltaWorker] Generated {len(state['growth_analysis']['signals'])} growth signals")
for signal in state['growth_analysis']['signals']:
    print(f"  - {signal['area']}: {signal['trend']} ({signal['delta']:+.1f} points)")

# RecommenderWorker
print(f"[RecommenderWorker] GPT Response Keys: {state['report'].keys()}")
print(f"[RecommenderWorker] Advice Count: {len(state['report']['advice'])}")
print(f"[RecommenderWorker] Video Source: {state['report'].get('recommended_video', {}).get('source')}")
```

### 프론트엔드 디버깅

```javascript
// LearningAnalytics.vue
console.log('=== Analytics API Response ===');
console.log('Full Response:', res.data);
console.log('Report:', res.data.report);
console.log('Analysis:', res.data.analysis);
console.log('Growth Analysis:', res.data.growth_analysis);
console.log('Radar Data:', res.data.analysis?.radar);
console.log('==============================');
```

---

## 주요 디렉토리 구조

```
backend/
├── core/
│   ├── models/
│   │   ├── base_model.py          # BaseModel (공통 필드)
│   │   ├── Practice_model.py      # Practice, PracticeDetail
│   │   └── UserAnswer_model.py    # 사용자 답변 기록
│   ├── views/
│   │   └── analytics_agent_view.py  # SWAN 아키텍처 구현
│   ├── fixtures/
│   │   └── educational_references.json  # 교육 자료 Fixtures
│   └── urls.py                    # URL 라우팅

frontend/
└── src/
    └── features/
        └── dashboard/
            ├── LearningAnalytics.vue      # 분석 UI 컴포넌트
            └── LearningAnalytics.css      # 스타일링
```

---

## 버전 히스토리

### v2.0 (2026-02-10) - GrowthDeltaWorker 추가
- **신규 기능**: 시계열 성장 추세 분석
- **Worker 추가**: GrowthDeltaWorker
- **UI 추가**: Growth Trends 섹션
- **개선 사항**: RecommenderWorker에 성장 데이터 통합

### v1.0 (2026-02-01) - 초기 SWAN 아키텍처
- **Worker**: CollectorWorker, AnalyzerWorker, RecommenderWorker
- **Tools**: 6개 기본 Tool 구현
- **UI**: 레이더 차트, 조언, 미션 추천, 영상 추천

---

## FAQ

### Q1: Worker 실행 순서를 바꿀 수 있나요?
**A:** 불가능합니다. 각 Worker는 이전 Worker의 출력에 의존하므로 순서가 고정되어 있습니다.
- CollectorWorker: raw_data 생성
- AnalyzerWorker: raw_data → analysis
- GrowthDeltaWorker: analysis → growth_analysis
- RecommenderWorker: 모든 데이터 → report

### Q2: GPT-4o-mini 대신 다른 모델을 사용할 수 있나요?
**A:** 가능합니다. [RecommenderWorker.work()](#4-recommenderworker)에서 `model="gpt-4o-mini"`를 원하는 모델로 변경하세요.
- `gpt-4o`: 더 정확한 분석 (비용 증가)
- `gpt-3.5-turbo`: 더 빠른 응답 (품질 저하)

### Q3: YouTube API 없이 동작하나요?
**A:** 네, DB Fixtures의 REFERENCE 자료를 사용합니다. YouTube API는 선택적 기능입니다.

### Q4: 성장 추세 계산 알고리즘을 수정하려면?
**A:** [GrowthDeltaWorker._calculate_trend()](#3-growthdeltaworker) 함수를 수정하세요.
```python
# 임계값 조정 (현재: ±5점)
if delta > 10:  # 더 엄격한 기준
    direction = '상승'
```

### Q5: 새로운 조언 타입을 추가하려면?
**A:** GPT 프롬프트와 프론트엔드 스타일링을 모두 수정해야 합니다.
```python
# RecommenderWorker 프롬프트에 추가
"advice": [
    {"type": "strength", ...},
    {"type": "weakness", ...},
    {"type": "growth", ...},
    {"type": "urgent", ...}  # 새로운 타입!
]
```

```css
/* LearningAnalytics.css */
.advice-item.urgent {
  border-left: 4px solid #ff0000;
  background: #fff5f5;
}
```

---

## 참고 자료

- **Django Documentation**: https://docs.djangoproject.com/
- **Vue 3 Composition API**: https://vuejs.org/guide/extras/composition-api-faq.html
- **OpenAI API (JSON Mode)**: https://platform.openai.com/docs/guides/text-generation/json-mode
- **YouTube Data API v3**: https://developers.google.com/youtube/v3

---

## 라이선스 & 기여

**프로젝트**: AI-GYM Learning Analytics System
**아키텍처**: SWAN (State-Worker Agent Network)
**개발 기간**: 2026-02-01 ~ 2026-02-10
**주요 기여자**: Antigravity Team

문의 사항이나 개선 제안은 GitHub Issues로 등록해주세요.

---

**문서 버전**: 2.0
**최종 수정일**: 2026-02-10
**작성자**: AI-GYM Development Team
