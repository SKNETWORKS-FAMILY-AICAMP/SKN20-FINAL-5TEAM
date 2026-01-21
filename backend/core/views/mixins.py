from rest_framework import viewsets

class AuditLogMixin:
    """
    데이터 생성/수정 시 create_id, update_id를 자동으로 세팅하는 Mixin
    """
    def perform_create(self, serializer):
        user_id = 'admin' # 기본값
        if self.request.user.is_authenticated:
            user_id = self.request.user.username
            
        # 모델에 create_id, update_id 필드가 있어야 함
        try:
            serializer.save(create_id=user_id, update_id=user_id)
        except TypeError:
            # 모델에 해당 필드가 없는 경우 무시하고 저장
            serializer.save()

    def perform_update(self, serializer):
        user_id = 'admin'
        if self.request.user.is_authenticated:
            user_id = self.request.user.username
            
        try:
            serializer.save(update_id=user_id)
        except TypeError:
            serializer.save()
