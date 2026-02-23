# 수정일: 2026-02-12
# 수정내용: BaseModel에서 Audit 필드(create_id 등)를 자동 관리하므로 AuditLogMixin 상속 제거

from pathlib import Path
import json
from rest_framework import viewsets, serializers
from rest_framework.response import Response
from core.models import Practice, PracticeDetail

class PracticeDetailSerializer(serializers.ModelSerializer):
    """
    [PracticeDetail 시리얼라이저]
    - 목적: 각 연습 과정에 속한 세부 문제/설정 데이터 변환
    """
    class Meta:
        model = PracticeDetail
        fields = ['id', 'detail_title', 'detail_type', 'content_data', 'display_order', 'is_active']

class PracticeSerializer(serializers.ModelSerializer):
    """
    [Practice 마스터 시리얼라이저]
    - 기능: 연습 과정의 기본 정보와 연결된 모든 상세 콘텐츠(details)를 통합하여 제공
    """
    # 하위 상세 정보들을 중첩 리스트로 포함
    details = PracticeDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Practice
        fields = '__all__'

class PracticeViewSet(viewsets.ModelViewSet):
    """
    [Practice 뷰셋]
    - 역할: 서비스 전체의 연습 과정 마스터 데이터를 관리하는 중심 API 엔드포인트
    - 정렬: 사용자 지정 순서(display_order)와 유닛 번호 기준
    """
    queryset = Practice.objects.all().order_by('display_order', 'unit_number')
    # queryset = Practice.objects.prefetch_related('details').all().order_by('display_order', 'unit_number')
    serializer_class = PracticeSerializer

    def _load_bughunt_seed_map(self):
        """
        backend/progressive-problems.json을 읽어 stage id(S1..S7) 기준 맵을 생성합니다.
        """
        seed_path = Path(__file__).resolve().parents[2] / 'progressive-problems.json'
        if not seed_path.exists():
            return {}

        try:
            with seed_path.open('r', encoding='utf-8') as f:
                payload = json.load(f)
            missions = payload.get('progressiveProblems', [])
            return {m.get('id'): m for m in missions if isinstance(m, dict) and m.get('id')}
        except Exception:
            return {}

    def _merge_debug_content(self, content_data, seed_map):
        """
        DB content_data에 interview_rubric이 누락된 경우만 seed로 보강합니다.
        """
        if not isinstance(content_data, dict):
            return content_data

        mission_id = content_data.get('id')
        seed_mission = seed_map.get(mission_id)
        if not seed_mission:
            return content_data

        merged = {**seed_mission, **content_data}
        db_steps = content_data.get('steps') if isinstance(content_data.get('steps'), list) else []
        seed_steps = seed_mission.get('steps') if isinstance(seed_mission.get('steps'), list) else []

        if not db_steps:
            return merged

        seed_step_map = {
            int(s.get('step')): s
            for s in seed_steps
            if isinstance(s, dict) and str(s.get('step', '')).isdigit()
        }

        merged_steps = []
        for db_step in db_steps:
            if not isinstance(db_step, dict):
                merged_steps.append(db_step)
                continue

            step_no = db_step.get('step')
            seed_step = seed_step_map.get(int(step_no)) if str(step_no).isdigit() else None
            if not seed_step:
                merged_steps.append(db_step)
                continue

            merged_steps.append({
                **seed_step,
                **db_step,
                'interview_rubric': db_step.get('interview_rubric') or seed_step.get('interview_rubric')
            })

        merged['steps'] = merged_steps
        return merged

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Debug Practice(unit02) 조회 시 interview_rubric 누락을 서버에서 보강
        if instance.id == 'unit02' and isinstance(data.get('details'), list):
            seed_map = self._load_bughunt_seed_map()
            if seed_map:
                for detail in data['details']:
                    if not isinstance(detail, dict):
                        continue
                    detail['content_data'] = self._merge_debug_content(detail.get('content_data'), seed_map)

        return Response(data)

class PracticeDetailViewSet(viewsets.ModelViewSet):
    """
    [PracticeDetail 뷰셋]
    - 역할: 개별 연습 상세 데이터를 조회하는 API 엔드포인트
    - 용도: 특정 ID의 PracticeDetail을 동적으로 가져올 때 사용 (예: bughunt01)
    """
    queryset = PracticeDetail.objects.filter(is_active=True).order_by('display_order')
    serializer_class = PracticeDetailSerializer
