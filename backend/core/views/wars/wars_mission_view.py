"""
wars/wars_mission_view.py — Wars ArchDrawQuiz 미션 데이터 API
[작성일: 2026-03-03]

SystemArchitecturePractice(unit03) DB 데이터를 Wars 포맷으로 변환하여 제공.
기존 architecture_missions.py 하드코딩 대체.
"""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from core.models import PracticeDetail

logger = logging.getLogger(__name__)

# architecture.json의 컴포넌트 이름 → Wars 팔레트 ID 매핑
COMPONENT_NAME_TO_ID = {
    'web server':       'server',
    'server':           'server',
    'api server':       'server',
    'feed service':     'server',
    'search api':       'server',
    'location api':     'server',
    'gateway':          'apigw',
    'websocket gateway':'server',
    'load balancer':    'lb',
    'loadbalancer':     'lb',
    'rdbms':                    'db',
    'database':                 'db',
    'db':                       'db',
    'history db':               'db',
    'history db (rdbms)':       'db',
    'object storage':           'cdn',
    'object storage (s3)':      'cdn',
    's3':                       'cdn',
    'storage':                  'cdn',
    'cache':                                    'cache',
    'cache (redis)':                            'cache',
    'redis':                                    'cache',
    'redis (distributed lock/atomic)':          'cache',
    'newsfeed cache':                           'cache',
    'newsfeed cache (redis)':                   'cache',
    'in-memory store':                          'cache',
    'in-memory store (redis geo)':              'cache',
    'search engine':                            'cache',
    'in-memory search engine':                  'cache',
    'in-memory search engine (trie/redis/es)':  'cache',
    'elasticsearch':                            'cache',
    'bloom filter':                             'cache',
    'bloom filter (deduplicator)':              'cache',
    'message queue':                    'queue',
    'message queue (kafka/rabbitmq)':   'queue',
    'kafka':                            'queue',
    'rabbitmq':                         'queue',
    'task queue':                       'queue',
    'pub/sub':                          'queue',
    'pub/sub (redis)':                  'queue',
    'worker':               'consumer',
    'notification worker':  'consumer',
    'cleanup worker':       'consumer',
    'crawler worker':       'consumer',
    'cdn':      'cdn',
    'client':   'client',
    'user':     'client',
    'bus':      'client',
}


def _component_name_to_id(name: str) -> str:
    return COMPONENT_NAME_TO_ID.get(name.lower().strip(), 'server')


def _transform_to_wars_mission(detail) -> dict:
    data = detail.content_data

    rubric_functional = data.get('rubric_functional', {})
    required_component_names = rubric_functional.get('required_components', [])
    required_flows_raw = rubric_functional.get('required_flows', [])

    # required_components → 팔레트 ID (중복 제거, 순서 보존)
    required_ids = list(dict.fromkeys(
        _component_name_to_id(name) for name in required_component_names
    ))

    # required_flows: 이름 → ID 변환
    required_flows = []
    for flow in required_flows_raw:
        from_id = _component_name_to_id(flow.get('from', ''))
        to_id = _component_name_to_id(flow.get('to', ''))
        if from_id and to_id:
            required_flows.append({
                'from': from_id,
                'to': to_id,
                'reason': flow.get('reason', ''),
            })

    # required_components: 채점용 ID와 표시용 Label 쌍
    required_components_detailed = []
    for name in required_component_names:
        comp_id = _component_name_to_id(name)
        required_components_detailed.append({
            'id': comp_id,
            'label': name
        })

    # engineering_spec → context 문자열
    engineering_spec = data.get('engineering_spec', {})
    if isinstance(engineering_spec, dict):
        context = '\n'.join(f"{k}: {v}" for k, v in engineering_spec.items())
    else:
        context = str(engineering_spec)

    missions = data.get('missions', data.get('mission', []))

    return {
        'id':       data.get('problem_id', detail.id),
        'title':    data.get('title', ''),
        'scenario': data.get('scenario', ''),
        'context':  context,
        'missions': missions,
        'required': required_ids,
        'rubric': {
            'required_components': required_components_detailed,
            'required_flows': required_flows,
        },
    }


@method_decorator(csrf_exempt, name='dispatch')
class WarsMissionsView(APIView):
    """
    GET /api/core/wars/missions/
    unit03 PracticeDetail → Wars 미션 포맷으로 변환 후 반환
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            details = (
                PracticeDetail.objects
                .filter(practice_id='unit03', detail_type='PROBLEM', is_active=True)
                .order_by('display_order')
            )
            if not details.exists():
                logger.warning('[WarsMissions] unit03 PracticeDetail 없음')
                return Response(
                    {'error': 'No missions found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            missions = [_transform_to_wars_mission(d) for d in details]
            logger.info(f'[WarsMissions] {len(missions)}개 미션 반환')
            return Response({'missions': missions}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'[WarsMissions] 오류: {e}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
