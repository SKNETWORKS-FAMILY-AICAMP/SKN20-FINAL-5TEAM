# 수정일: 2026-02-12
# 수정내용: BaseModel 기반 필드 자동화를 위해 AuditLogMixin 제거

from rest_framework import viewsets, serializers
from core.models import DashboardLog

class DashboardLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardLog
        fields = '__all__'

class DashboardLogViewSet(viewsets.ModelViewSet):
    """
    팀원 F 담당: 통계 데이터 조회 API
    """
    queryset = DashboardLog.objects.all()
    serializer_class = DashboardLogSerializer
