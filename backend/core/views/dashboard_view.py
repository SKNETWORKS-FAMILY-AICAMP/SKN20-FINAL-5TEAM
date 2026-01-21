# 수정일: 2026-01-20
# 수정내용: 팀원 F (Dashboard 담당) - 대시보드 관련 뷰 정의

from rest_framework import viewsets, serializers
from core.models import DashboardLog
from .mixins import AuditLogMixin

class DashboardLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardLog
        fields = '__all__'

class DashboardLogViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """
    팀원 F 담당: 통계 데이터 조회 API
    """
    queryset = DashboardLog.objects.all()
    serializer_class = DashboardLogSerializer
