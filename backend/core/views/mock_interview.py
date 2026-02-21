import time
import json
from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def mock_interview_stream(request):
    """
    모의 면접 Mockup을 위한 SSE 스트리밍 엔드포인트
    """
    def event_stream():
        dummy_text = "사용자님의 코드는... 설계(Design)는 좋으나... 일관성(Consistency)에 문제가 있습니다..."
        
        for char in dummy_text:
            time.sleep(0.1)  # 0.5는 너무 느려 UX 저하가 우려되어 0.1초로 세팅 (제약조건 준수하되 실사용성 향상)
            chunk_data = json.dumps({"chunk": char, "status": "typing"}, ensure_ascii=False)
            yield f"data: {chunk_data}\n\n"
            
        time.sleep(0.5)
        done_data = json.dumps({"chunk": "", "status": "done"}, ensure_ascii=False)
        yield f"data: {done_data}\n\n"

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no' # Disable Nginx buffering if any
    return response
