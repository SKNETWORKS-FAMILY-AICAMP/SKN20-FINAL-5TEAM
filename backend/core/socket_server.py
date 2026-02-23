import socketio
import asyncio
import random

# [수정일: 2026-02-23] Coduck Wars Phase 2: 실시간 협업용 Socket.io 서버 설정
# 이 서버는 다중 접속 유저 간의 아키텍처 설계 동기화 및 실시간 대화를 관리합니다.

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

@sio.event
async def connect(sid, environ):
    print(f"✅ Socket Connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"❌ Socket Disconnected: {sid}")

@sio.event
async def join_war_room(sid, data):
    """
    미션 ID를 기준으로 팀원들이 하나의 가상 룸에 입장하며 역할 정보를 등록합니다.
    data format: { "mission_id": "...", "user_name": "...", "user_role": "..." }
    """
    mission_id = data.get('mission_id')
    user_name = data.get('user_name', 'Anonymous')
    user_role = data.get('user_role', 'Architect') # 기본 역할
    
    if mission_id:
        await sio.enter_room(sid, mission_id)
        # 세션 데이터에 사용자 정보 저장
        await sio.save_session(sid, {"name": user_name, "role": user_role, "room": mission_id})
        
        print(f"👥 User {user_name}({sid}) joined War Room: {mission_id} as {user_role}")
        
        # 룸 전체에 유저 입장 및 역할 정보 방송
        await sio.emit('user_joined', {
            "sid": sid, 
            "user_name": user_name,
            "user_role": user_role
        }, room=mission_id)

        # [Phase 4] 실시간 장애 엔진 시뮬레이션 시작 (데모용)
        asyncio.create_task(trigger_chaos_events_demo(mission_id))

async def trigger_chaos_events_demo(mission_id):
    """
    데모용 장애 스케줄러: 특정 간격으로 팀원들에게 장애 과제를 투척합니다.
    사용자님의 '역할군' 기획에 맞춰 타겟을 지정합니다.
    """
    # 1단계: 트래픽 폭주 (Ops/Security 전문가 타겟)
    await asyncio.sleep(15) # 15초 후 발생
    await sio.emit('chaos_event', {
        "event_id": "traffic_surge",
        "title": "🚨 EMERGENCY: Traffic Surge detected!",
        "description": "특정 리전에서 동시 접속자가 10배 폭증했습니다. 엣지 서버의 부하 분산 설정을 검토하세요.",
        "target_role": "OPS/SECURITY",
        "target_node_ids": ["LB", "Web"]
    }, room=mission_id)

    # 2단계: DB 데드락 (DB/Performance 전문가 타겟)
    await asyncio.sleep(25) # 추가 25초 후 발생
    await sio.emit('chaos_event', {
        "event_id": "db_lock",
        "title": "🔥 CRITICAL: DB Row Lock Contention!",
        "description": "결제 모듈의 업데이트 쿼리에서 데드락이 감지되었습니다. 인덱스 최적화가 필요합니다.",
        "target_role": "DB/PERFORMANCE",
        "target_node_ids": ["DB"]
    }, room=mission_id)

@sio.event
async def update_role(sid, data):
    """
    팀원이 로비에서 역할을 변경할 때 방송합니다.
    """
    mission_id = data.get('mission_id')
    new_role = data.get('user_role')
    if mission_id and new_role:
        await sio.emit('role_sync', {"sid": sid, "user_role": new_role}, room=mission_id)

@sio.event
async def canvas_update(sid, data):
    """
    누군가 아키텍처(Mermaid)를 수정하면 해당 룸의 모든 팀원에게 동기화합니다.
    data format: { "mission_id": "...", "mermaid_code": "..." }
    """
    mission_id = data.get('mission_id')
    mermaid_code = data.get('mermaid_code')
    if mission_id and mermaid_code:
        # 보낸 사람(sender)을 제외한 나머지 팀원들에게 방송
        await sio.emit('canvas_sync', {"mermaid_code": mermaid_code, "sender": sid}, room=mission_id, skip_sid=sid)

@sio.event
async def chat_message(sid, data):
    """
    팀원 간 실시간 채팅 메시지를 브로드캐스팅합니다.
    """
    mission_id = data.get('mission_id')
    if mission_id:
        await sio.emit('chat_sync', {
            "sender_name": data.get('sender_name', 'Anonymous'),
            "content": data.get('content', ''),
            "role": 'user'
        }, room=mission_id, skip_sid=sid)

# [Phase 5] WebRTC 시그널링 (Offer, Answer, ICE Candidate)
@sio.event
async def offer(sid, data):
    """특정 팀원에게 WebRTC Offer 전달"""
    target_sid = data.get('target_sid')
    if target_sid:
        await sio.emit('offer', {
            'offer': data.get('offer'),
            'sender_sid': sid
        }, to=target_sid)

@sio.event
async def answer(sid, data):
    """특정 팀원에게 WebRTC Answer 전달"""
    target_sid = data.get('target_sid')
    if target_sid:
        await sio.emit('answer', {
            'answer': data.get('answer'),
            'sender_sid': sid
        }, to=target_sid)

@sio.event
async def ice_candidate(sid, data):
    """특정 팀원에게 WebRTC ICE Candidate 전달"""
    target_sid = data.get('target_sid')
    if target_sid:
        await sio.emit('ice_candidate', {
            'candidate': data.get('candidate'),
            'sender_sid': sid
        }, to=target_sid)
