# 수정일: 2026-01-20
# 수정내용: 팀원 B (Product 담당) - 상품 관련 뷰 정의

from rest_framework import viewsets, serializers
from core.models import Product
from .mixins import AuditLogMixin

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """
    팀원 B 담당: 상품 목록 및 상세 조회 API
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
