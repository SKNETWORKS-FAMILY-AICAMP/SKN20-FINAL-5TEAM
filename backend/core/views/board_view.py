# 수정일: 2026-01-20
# 수정내용: 팀원 D (Board 담당) - 게시판 관련 뷰 정의

from rest_framework import viewsets, serializers
from core.models import Post
from .mixins import AuditLogMixin

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class PostViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """
    팀원 D 담당: 공지사항 및 Q&A API
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
