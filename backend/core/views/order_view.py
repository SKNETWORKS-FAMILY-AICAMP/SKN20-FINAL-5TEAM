# 수정일: 2026-01-20
# 수정내용: 팀원 C (Order 담당) - 주문 관련 뷰 정의

from rest_framework import viewsets, serializers
from core.models import Order
from .mixins import AuditLogMixin

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """
    팀원 C 담당: 주문 생성 및 내역 조회 API
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
