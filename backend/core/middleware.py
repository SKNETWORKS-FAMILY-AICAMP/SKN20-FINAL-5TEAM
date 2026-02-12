# 수정일: 2026-02-12
# 수정내용: CurrentUserMiddleware 구현 - 전역에서 현재 요청 중인 사용자를 추적하기 위함

import threading

# 스레드별로 독립적인 데이터를 저장할 수 있는 로컬 저장소 생성
_user_storage = threading.local()

def get_current_user():
    """
    어디서든 현재 요청 중인 사용자의 username을 가져올 수 있는 헬퍼 함수
    주로 모델의 save() 메서드에서 사용됩니다.
    """
    return getattr(_user_storage, 'user', 'system')

class CurrentUserMiddleware:
    """
    모든 HTTP 요청을 가로채서 인증된 유저 정보를 스레드 로컬에 저장하는 미들웨어
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. 요청이 들어올 때 유저 정보 저장
        if request.user.is_authenticated:
            _user_storage.user = request.user.username
        else:
            _user_storage.user = 'anonymous'

        # 2. 다음 미들웨어 또는 뷰 실행
        response = self.get_response(request)

        # 3. 요청 처리가 끝난 후 메모리 누수 방지를 위해 데이터 삭제
        if hasattr(_user_storage, 'user'):
            del _user_storage.user

        return response
