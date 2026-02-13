# 수정일: 2026-02-12
# 수정내용: BaseModel에서 Audit 필드(create_id 등)를 자동 관리하므로 AuditLogMixin 상속 제거

from rest_framework import viewsets, serializers
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
    serializer_class = PracticeSerializer

class PracticeDetailViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """
    [PracticeDetail 뷰셋]
    - 역할: 개별 연습 상세 데이터를 조회하는 API 엔드포인트
    - 용도: 특정 ID의 PracticeDetail을 동적으로 가져올 때 사용 (예: bughunt01)
    """
    queryset = PracticeDetail.objects.filter(is_active=True).order_by('display_order')
    serializer_class = PracticeDetailSerializer
