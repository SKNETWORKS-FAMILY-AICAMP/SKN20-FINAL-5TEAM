# 수정일: 2026-01-25
# 수정내용: Antigravity - 'Practice'를 서비스의 핵심 마스터로 설정 (명칭 및 구조 통일)

from rest_framework import viewsets, serializers
from core.models import Practice, PracticeDetail
from .mixins import AuditLogMixin

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

class PracticeViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """
    [Practice 뷰셋]
    - 역할: 서비스 전체의 연습 과정 마스터 데이터를 관리하는 중심 API 엔드포인트
    - 정렬: 사용자 지정 순서(display_order)와 유닛 번호 기준
    """
    queryset = Practice.objects.all().order_by('display_order', 'unit_number')
    serializer_class = PracticeSerializer
