"""
작성일: 2026-02-21
작성자: Antigravity (수석 에이전트)
작성내용: 
- AI-GYM 프로젝트의 모의 면접 시스템 Mockup(PoC) 백엔드 API
- 클라이언트(프론트엔드)에게 더미 인터뷰 텍스트를 청크 단위로 전송하여
  LLM 응답 지연(Latency)을 시뮬레이션하기 위한 SSE(Server-Sent Events) 스트리밍 엔드포인트 구현.
- 기존 PracticeDetail의 JSON 스키마 구조를 모방하여 data 필드 내부에 chunk와 status를 담아 전송함.
"""
import time
import json
from django.http import StreamingHttpResponse

# Django Rest Framework decorators removed to prevent content negotiation (406) errors on text/event-stream.
# CSRF exemption is sometimes needed if requests come from other origins, but this is a GET request.
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
