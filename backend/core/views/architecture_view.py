# [작성일: 2026-02-20] Architecture Practice 평가 및 질문 생성 View
import openai
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import re
import traceback
import sys

# 6대 기둥 정의 (Well-Architected Framework)
PILLAR_DATA = {
    'reliability': {
        'name': '신뢰성 (Reliability)',
        'keywords': ['장애', '다운', 'spof', '중단', '복구', 'failover', 'redundancy', '가용성', 'availability']
    },
    'performance_optimization': {
        'name': '성능 최적화 (Performance Optimization)',
        'keywords': ['트래픽', '급증', '동시', 'latency', '지연', '느림', '성능', 'throughput', '처리량', 'cache', 'cdn']
    },
    'operational_excellence': {
        'name': '운영 우수성 (Operational Excellence)',
        'keywords': ['모니터링', '로그', 'alert', '경보', '운영', 'cicd', '배포', 'deploy', 'debug']
    },
    'cost_optimization': {
        'name': '비용 최적화 (Cost Optimization)',
        'keywords': ['비용', '예산', 'cost', '저렴', '절감', 'spot', 'reserved', '요금']
    },
    'security': {
        'name': '보안 (Security)',
        'keywords': ['보안', '유출', '해킹', '암호화', 'encryption', 'iam', '권한', 'vpc', 'firewall', 'waf']
    },
    'sustainability': {
        'name': '지속가능성 (Sustainability)',
        'keywords': ['환경', '효율', '장기', 'green', 'efficiency', '지속']
    }
}

# 루브릭 등급 정의 (0점부터 시작)
RUBRIC_GRADES = {
    'excellent': {
        'range': [90, 100],
        'label': '우수 (Excellent)',
        'emoji': '✨',
    },
    'good': {
        'range': [75, 89],
        'label': '양호 (Good)',
        'emoji': '✓',
    },
    'fair': {
        'range': [60, 74],
        'label': '보통 (Fair)',
        'emoji': '⚠️',
    },
    'poor': {
        'range': [40, 59],
        'label': '미흡 (Poor)',
        'emoji': '❌',
    },
    'failing': {
        'range': [0, 39],
        'label': '부족 (Failing)',
        'emoji': '✗',
    }
}

def format_axis_weights(axis_weights):
    """가중치 정보 포맷팅"""
    if not axis_weights or len(axis_weights) == 0:
        return '(가중치 정보 없음 - 균등 평가)'

    sorted_weights = sorted(
        [(k, v.get('weight', 0), v.get('reason', '')) for k, v in axis_weights.items()],
        key=lambda x: x[1],
        reverse=True
    )

    formatted = []
    for idx, (key, weight, reason) in enumerate(sorted_weights, 1):
        pillar = PILLAR_DATA.get(key, {})
        formatted.append(f"{idx}. {pillar.get('name', key)} [가중치: {weight}%]\n   {reason or ''}")

    return '\n\n'.join(formatted)


def select_relevant_pillars(scenario, missions, constraints):
    """시나리오 기반 관련 Pillar 선별"""
    full_text = ' '.join([
        scenario or '',
        *missions,
        *constraints
    ]).lower()

    scores = {}
    for key, pillar in PILLAR_DATA.items():
        scores[key] = sum(1 for keyword in pillar['keywords'] if keyword in full_text)

    sorted_pillars = sorted(
        [(k, v) for k, v in scores.items()],
        key=lambda x: x[1],
        reverse=True
    )[:3]

    # 최소 2개는 보장
    if len(sorted_pillars) < 2:
        for key in ['reliability', 'performance_optimization', 'security']:
            if not any(k == key for k, _ in sorted_pillars):
                sorted_pillars.append((key, 0))
                if len(sorted_pillars) >= 2:
                    break

    return [
        {'key': k, 'name': PILLAR_DATA[k]['name']}
        for k, _ in sorted_pillars[:3]
    ]


def categorize_components(components):
    """컴포넌트를 역할별로 분류"""
    type_map = {
        'elb': 'entry', 'alb': 'entry', 'nlb': 'entry',
        'cloudfront': 'entry', 'apigateway': 'entry', 'route53': 'entry',
        'ec2': 'compute', 'lambda': 'compute', 'ecs': 'compute',
        'eks': 'compute', 'fargate': 'compute', 'beanstalk': 'compute',
        'rds': 'storage', 's3': 'storage', 'dynamodb': 'storage',
        'elasticache': 'storage', 'redis': 'storage', 'aurora': 'storage', 'ebs': 'storage',
        'waf': 'security', 'shield': 'security', 'securitygroup': 'security',
        'iam': 'security', 'cognito': 'security',
        'vpc': 'network', 'subnet': 'network', 'natgateway': 'network',
        'internetgateway': 'network', 'transitgateway': 'network'
    }

    categories = {cat: [] for cat in set(type_map.values())}
    categories['other'] = []

    for comp in components:
        comp_type = (comp.get('type') or '').lower()
        comp_text = (comp.get('text') or '').lower()

        category = 'other'
        for keyword, cat in type_map.items():
            if keyword in comp_type or keyword in comp_text:
                category = cat
                break

        categories[category].append(comp)

    return categories


def analyze_connections(connections, components):
    """연결 관계 분석"""
    result = []
    for conn in connections:
        from_comp = next((c for c in components if c.get('id') == conn.get('from')), None)
        to_comp = next((c for c in components if c.get('id') == conn.get('to')), None)

        if not from_comp or not to_comp:
            continue

        flow_type = 'Data Flow'
        from_type = (from_comp.get('type') or '').lower()
        to_type = (to_comp.get('type') or '').lower()

        if 'elb' in from_type or 'alb' in from_type:
            flow_type = 'Traffic Distribution'
        elif 'rds' in to_type or 'dynamodb' in to_type:
            flow_type = 'Database Query'
        elif 'ec2' in from_type and 's3' in to_type:
            flow_type = 'File Storage'
        elif 'cache' in to_type or 'redis' in to_type:
            flow_type = 'Cache Access'

        result.append(f"{from_comp.get('text')} → {to_comp.get('text')} ({flow_type})")

    return result


@method_decorator(csrf_exempt, name='dispatch')
class ArchitectureEvaluationView(APIView):
    """
    [작성일: 2026-02-20]
    시스템 아키텍처 루브릭 기반 평가

    프롬프트는 프론트엔드에서 생성하여 전송
    백엔드는 프롬프트를 받아서 LLM 호출만 수행
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        prompt = data.get('prompt', '')
        deep_dive_qna = data.get('deepDiveQnA', [])

        print(f"[DEBUG] Architecture Evaluation Start (Prompt received from frontend)", flush=True)

        try:
            if not prompt:
                return Response(
                    {"error": "Prompt is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            api_key = settings.OPENAI_API_KEY
            if not api_key:
                return Response(
                    {"error": "OpenAI API Key is missing"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            client = openai.OpenAI(api_key=api_key)

            # LLM 호출
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=4500
            )

            content = response.choices[0].message.content
            print(f"[DEBUG] LLM Response received", flush=True)

            # JSON 파싱
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = json.loads(json_match.group())

                # 전체 점수 계산
                evaluations = result.get('evaluations', [])
                weighted_sum = 0
                total_weight = 0

                for ev in evaluations:
                    weight = ev.get('weight', 0)
                    score = ev.get('score', 0)
                    weighted_sum += (score * weight / 100)
                    total_weight += weight

                overall_score = int(round(weighted_sum))

                return Response({
                    "evaluations": evaluations,
                    "overallScore": overall_score,
                    "overallGrade": result.get('overallGrade', 'fair'),
                    "summary": result.get('summary', '평가 완료'),
                    "strengths": result.get('strengths', []),
                    "weaknesses": result.get('weaknesses', []),
                    "recommendations": result.get('recommendations', [])
                }, status=status.HTTP_200_OK)

            return Response(
                {"error": "Invalid JSON format from AI"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            print(f"[ERROR] Architecture Evaluation: {traceback.format_exc()}", file=sys.stderr, flush=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class ArchitectureQuestionGeneratorView(APIView):
    """
    [작성일: 2026-02-20]
    심화 질문 생성
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        problem = data.get('problem', {})
        components = data.get('components', [])
        connections = data.get('connections', [])
        mermaid_code = data.get('mermaidCode', '')
        user_explanation = data.get('userExplanation', '')

        print(f"[DEBUG] Question Generation Start", flush=True)

        try:
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                return Response(
                    {"error": "OpenAI API Key is missing"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            client = openai.OpenAI(api_key=api_key)

            # 컴포넌트 분류
            categorized = categorize_components(components)

            # 연결 분석
            meaningful_connections = analyze_connections(connections, components)

            # 관련 Pillar 선별
            scenario = problem.get('scenario', '')
            missions = problem.get('missions', [])
            constraints = problem.get('constraints', [])
            relevant_pillars = select_relevant_pillars(scenario, missions, constraints)

            # 컴포넌트 텍스트 생성
            category_texts = []
            if categorized['entry']:
                category_texts.append(
                    f"**🚪 진입점 (Entry Points)**\n" +
                    '\n'.join([f"- {c.get('text')} ({c.get('type')})" for c in categorized['entry']])
                )
            if categorized['compute']:
                category_texts.append(
                    f"**⚙️ 컴퓨팅 계층 (Compute)**\n" +
                    '\n'.join([f"- {c.get('text')} ({c.get('type')})" for c in categorized['compute']])
                )
            if categorized['storage']:
                category_texts.append(
                    f"**💾 저장소 계층 (Storage)**\n" +
                    '\n'.join([f"- {c.get('text')} ({c.get('type')})" for c in categorized['storage']])
                )
            if categorized['security']:
                category_texts.append(
                    f"**🔒 보안 계층 (Security)**\n" +
                    '\n'.join([f"- {c.get('text')} ({c.get('type')})" for c in categorized['security']])
                )

            architecture_overview = '\n\n'.join(category_texts)

            # 프롬프트 생성
            prompt = f"""당신은 **시니어 클라우드 솔루션 아키텍트**입니다.

## 🎯 당신의 임무
1. 지원자의 아키텍처를 **비판적으로 분석** (안티패턴 체크)
2. 부족한 영역 3가지에 대해 **날카로운 질문** 생성

---

## 📋 문제 상황

### 시나리오
{scenario or '시스템 아키텍처 설계'}

### 미션
{chr(10).join([f"{i+1}. {m}" for i, m in enumerate(missions)])}

### 제약조건
{chr(10).join([f"{i+1}. {c}" for i, c in enumerate(constraints)])}

---

## 🏗️ 지원자의 아키텍처

### 역할별 컴포넌트 분류
{architecture_overview or '(컴포넌트 없음)'}

### 데이터 흐름
{chr(10).join(meaningful_connections) if meaningful_connections else '(연결 없음)'}

---

## 💬 지원자의 설명
"{user_explanation or '(설명 없음)'}"

---

## 🔍 안티패턴 체크리스트 (Critical)

### ⚠️ 신뢰성 안티패턴
- [ ] **SPOF (Single Point of Failure)**: 단일 컴포넌트 장애 시 전체 서비스 중단?
- [ ] **No Redundancy**: 중요 컴포넌트의 복제본이 없음?
- [ ] **단일 AZ 배치**: 모든 리소스가 1개 가용영역에만?

### ⚡ 성능 안티패턴
- [ ] **단일 경로 병목**: 모든 트래픽이 1개 경로로만 흐름?
- [ ] **Auto Scaling 부재**: 트래픽 급증 시 수동 증설만 가능?
- [ ] **캐싱 전략 없음**: DB에 직접 쿼리만 하는 구조?

### 🔒 보안 안티패턴
- [ ] **Public DB**: 데이터베이스가 Public Subnet에 노출?
- [ ] **Network Segmentation 부족**: VPC/Subnet 분리 없음?

---

## 📝 질문 생성 규칙

질문은 다음을 만족해야 합니다:
1. **안티패턴 우선**: 체크리스트에서 발견된 문제를 먼저 질문
2. **상황 기반**: "~한 상황이 발생하면" 형태 (Failure Scenario)
3. **구체적**: 배치된 컴포넌트/상황을 언급
4. **개방형**: 설계 의도/대응 방안을 설명하게 유도

---

## 출력 형식 (JSON만)

```json
{{
  "questions": [
    {{
      "category": "신뢰성",
      "gap": "부족한 부분 설명",
      "scenario": "구체적인 장애 시나리오",
      "question": "실제 질문 (배치된 컴포넌트 언급)"
    }},
    {{
      "category": "성능",
      "gap": "부족한 부분 설명",
      "scenario": "구체적인 장애 시나리오",
      "question": "실제 질문"
    }},
    {{
      "category": "운영",
      "gap": "부족한 부분 설명",
      "scenario": "구체적인 장애 시나리오",
      "question": "실제 질문"
    }}
  ]
}}
```"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            content = response.choices[0].message.content

            # JSON 파싱
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = json.loads(json_match.group())

                return Response({
                    "questions": result.get('questions', []),
                    "selectedPillars": [p['name'] for p in relevant_pillars],
                    "metadata": {
                        "componentCount": len(components),
                        "connectionCount": len(connections)
                    }
                }, status=status.HTTP_200_OK)

            return Response(
                {"error": "Invalid JSON format from AI"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            print(f"[ERROR] Question Generation: {traceback.format_exc()}", file=sys.stderr, flush=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
