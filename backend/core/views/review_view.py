# 수정일: 2026-01-20
# 수정내용: 팀원 E (Review 담당) - 리뷰 관련 뷰 정의

from rest_framework import viewsets, serializers
from core.models import Review
from .mixins import AuditLogMixin

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class ReviewViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """
    팀원 E 담당: 리뷰 작성 및 조회 API
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
