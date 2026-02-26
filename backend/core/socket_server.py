import socketio
import asyncio
import random
from core.services.pseudocode_evaluator import PseudocodeEvaluator, EvaluationRequest, EvaluationMode
from asgiref.sync import sync_to_async

# [Multi-Agent] 임포트
from core.services.wars.orchestrator import WarsOrchestrator
from core.services.wars.state_machine import DrawRoomState, GameState

# 전역 객체 및 상태 관리
wars_orchestrator = WarsOrchestrator()
draw_room_states: dict[str, DrawRoomState] = {}
pseudocode_evaluator = PseudocodeEvaluator()
active_rooms = set()
room_leaders = {}  
room_snapshots = {}
room_game_states = {}
active_timer_tasks = {} 

# 게임별 방 데이터 저장소
draw_rooms = {}  
run_rooms = {}  
bubble_rooms = {}
run_phase2_submissions = {}

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

@sio.event
async def connect(sid, environ):
    print(f"✅ Socket Connected: {sid}")

@sio.event
async def disconnect(sid):
    """소켓 연결 해제 시 모든 세션 및 방 데이터 정리 (통합 버전)"""
    print(f"❌ Socket Disconnected: {sid}")
    session = await sio.get_session(sid)
    if not session: return

    # 1. War Room 정리
    mission_id = session.get('room')
    if mission_id:
        await sio.emit('user_left', {"sid": sid, "user_name": session.get('name', 'Unknown')}, room=mission_id)
        if room_leaders.get(mission_id) == sid:
            del room_leaders[mission_id]
            room_sids = list(sio.manager.rooms.get('/', {}).get(mission_id, set()))
            remaining = [s for s in room_sids if s != sid]
            if remaining:
                room_leaders[mission_id] = remaining[0]
                await sio.emit('leader_info', {"leader_sid": remaining[0]}, room=mission_id)

    # 2. Draw Room 정리
    draw_room_id = session.get('draw_room')
    if draw_room_id in draw_rooms:
        room = draw_rooms[draw_room_id]
        room['players'] = [p for p in room['players'] if p['sid'] != sid]
        if not room['players']:
            del draw_rooms[draw_room_id]
            if draw_room_id in draw_room_states: del draw_room_states[draw_room_id]
        else:
            players_data = [{'name': p['name'], 'sid': p['sid']} for p in room['players']]
            await sio.emit('draw_lobby', {'players': players_data}, room=draw_room_id)
            await sio.emit('draw_player_left', {'sid': sid}, room=draw_room_id)

    # 3. Logic Run 정리
    run_room_id = session.get('run_room')
    if run_room_id in run_rooms:
        room = run_rooms[run_room_id]
        room['players'] = [p for p in room['players'] if p['sid'] != sid]
        if room.get('leader_sid') == sid:
            room['leader_sid'] = room['players'][0]['sid'] if room['players'] else None
        if not room['players']:
            del run_rooms[run_room_id]
            if run_room_id in run_phase2_submissions: del run_phase2_submissions[run_room_id]
        else:
            await sio.emit('run_user_left', {'sid': sid, 'leader_sid': room['leader_sid']}, room=run_room_id)

    # 4. Bubble Game 정리
    bubble_room_id = session.get('bubble_room')
    if bubble_room_id in bubble_rooms:
        room = bubble_rooms[bubble_room_id]
        room['players'] = [p for p in room['players'] if p['sid'] != sid]
        if not room['players']:
            del bubble_rooms[bubble_room_id]
        else:
            players_data = [{'name': p['name'], 'sid': p['sid'], 'avatar': p.get('avatar')} for p in room['players']]
            await sio.emit('bubble_lobby', {'players': players_data}, room=bubble_room_id)
            await sio.emit('bubble_player_left', {'sid': sid}, room=bubble_room_id)

# ---------- WAR ROOM EVENTS ----------
@sio.event
async def join_war_room(sid, data):
    mission_id = data.get('mission_id')
    user_name = data.get('user_name', 'Anonymous')
    user_role = data.get('user_role', 'pending')
    if mission_id:
        await sio.enter_room(sid, mission_id)
        await sio.save_session(sid, {"name": user_name, "role": user_role, "room": mission_id})
        if mission_id not in room_leaders:
            room_leaders[mission_id] = sid
            if mission_id not in room_game_states:
                room_game_states[mission_id] = {"phase": "design", "time_left": 600, "is_running": False}
        await sio.emit('leader_info', {"leader_sid": room_leaders[mission_id]}, room=mission_id)
        await sio.emit('user_joined', {"sid": sid, "user_name": user_name, "user_role": user_role}, room=mission_id)

@sio.event
async def start_mission(sid, data):
    mission_id = data.get('mission_id')
    if mission_id and room_leaders.get(mission_id) == sid:
        if mission_id in room_game_states:
            room_game_states[mission_id]["is_running"] = True
            if mission_id not in active_timer_tasks or active_timer_tasks[mission_id].done():
                active_timer_tasks[mission_id] = asyncio.create_task(run_room_timer(mission_id))
        await sio.emit('mission_start', {"mission_id": mission_id}, room=mission_id)

async def run_room_timer(mission_id):
    while mission_id in room_game_states and room_game_states[mission_id]["is_running"]:
        state = room_game_states[mission_id]
        if state["time_left"] > 0: state["time_left"] -= 1
        if state["time_left"] % 5 == 0:
            await sio.emit('state_sync', {"state": {"phase": state["phase"], "time": state["time_left"]}}, room=mission_id)
        await asyncio.sleep(1)
        if state["time_left"] <= 0:
            if state["phase"] == "design": state["phase"], state["time_left"] = "blackout", 120
            elif state["phase"] == "blackout": state["phase"], state["time_left"] = "defense", 180
            else: state["is_running"] = False
            await sio.emit('state_sync', {"state": {"phase": state["phase"], "time": state["time_left"]}}, room=mission_id)

# ---------- DRAW GAME EVENTS ----------
@sio.event
async def draw_join(sid, data):
    room_id = data.get('room_id', 'draw-default').strip()
    user_name = data.get('user_name', 'Player')
    await sio.enter_room(sid, room_id)
    await sio.save_session(sid, {'draw_room': room_id, 'draw_name': user_name})
    if room_id not in draw_rooms: draw_rooms[room_id] = {'players': [], 'phase': 'waiting'}
    room = draw_rooms[room_id]
    if not any(p['sid'] == sid for p in room['players']) and len(room['players']) < 2:
        room['players'].append({'sid': sid, 'name': user_name, 'score': 0})
    await sio.emit('draw_lobby', {'players': [{'name': p['name'], 'sid': p['sid']} for p in room['players']]}, room=room_id)
    if len(room['players']) >= 2:
        room['phase'] = 'ready'
        await sio.emit('draw_ready', {}, room=room_id)

@sio.event
async def draw_canvas_sync(sid, data):
    room_id = data.get('room_id', 'draw-default')
    await sio.emit('draw_canvas_update', {'sender_sid': sid, 'nodes': data.get('nodes'), 'arrows': data.get('arrows')}, room=room_id, skip_sid=sid)
    room_state = draw_room_states.get(room_id)
    if room_state:
        res = wars_orchestrator.on_canvas_update(room_state, sid, data.get('nodes'), data.get('arrows'))
        if res.get('coach_hint'): await sio.emit('coach_hint', res['coach_hint'], to=sid)
        if res.get('chaos_event'): await sio.emit('chaos_event', res['chaos_event'], room=room_id)
# ---------- LOGIC RUN EVENTS ----------
@sio.event
async def run_join(sid, data):
    room_id = data.get('room_id', 'run-default').strip()
    user_name = data.get('user_name', 'Anonymous')
    await sio.enter_room(sid, room_id)
    await sio.save_session(sid, {'run_room': room_id, 'run_name': user_name})
    if room_id not in run_rooms: run_rooms[room_id] = {'players': [], 'phase': 'lobby', 'leader_sid': None}
    room = run_rooms[room_id]
    if not room['leader_sid']: room['leader_sid'] = sid
    if not any(p['sid'] == sid for p in room['players']):
        room['players'].append({'sid': sid, 'name': user_name, 'avatar_url': data.get('avatar_url'), 'phase1_score': 0, 'phase2_score': 0})
    await sio.emit('run_lobby', {'players': room['players'], 'leader_sid': room['leader_sid']}, room=room_id)

@sio.event
async def run_progress(sid, data):
    room_id = data.get('room_id')
    if data.get('phase') == 'speedFill' and room_id in run_rooms:
        for p in run_rooms[room_id]['players']:
            if p['sid'] == sid: p['phase1_score'] = data.get('score', 0)
    await sio.emit('run_sync', data, room=room_id, skip_sid=sid)

# ---------- BUG-BUBBLE MONSTER (핵심 수정 포함) ----------
@sio.event
async def bubble_join(sid, data):
    room_id = data.get('room_id', 'bubble-default').strip()
    user_name = data.get('user_name', 'Unknown')
    await sio.enter_room(sid, room_id)
    await sio.save_session(sid, {'bubble_room': room_id, 'name': user_name})
    if room_id not in bubble_rooms: bubble_rooms[room_id] = {'players': [], 'is_playing': False}
    room = bubble_rooms[room_id]
    if not any(p['sid'] == sid for p in room['players']):
        room['players'].append({'sid': sid, 'name': user_name, 'avatar': data.get('user_avatar')})
    await sio.emit('bubble_lobby', {'players': room['players']}, room=room_id)

@sio.event
async def bubble_sync(sid, data):
    """실시간 위치 및 액션 동기화 (전송 로그가 뜨는데 동기화 안되는 문제 해결)"""
    room_id = data.get('room_id')
    if room_id:
        await sio.emit('bubble_move_update', {
            'sid': sid,
            'pos': data.get('pos'),
            'action': data.get('action'),
            'flipX': data.get('flipX')
        }, room=room_id, skip_sid=sid)

@sio.event
async def bubble_start(sid, data):
    room_id = data.get('room_id')
    if room_id in bubble_rooms:
        bubble_rooms[room_id]['is_playing'] = True
        await sio.emit('bubble_game_start', {}, room=room_id)

@sio.event
async def bubble_send_monster(sid, data):
    await sio.emit('bubble_receive_monster', {'sender_sid': sid, 'monster_type': data.get('monster_type')}, room=data.get('room_id'), skip_sid=sid)

@sio.event
async def bubble_game_over(sid, data):
    await sio.emit('bubble_end', {'loser_sid': sid}, room=data.get('room_id'))

# 공통 채팅 및 기타 이벤트 유지 (chat_message, update_role 등 기존 코드와 동일)
@sio.event
async def chat_message(sid, data):
    mission_id = data.get('mission_id')
    if mission_id:
        await sio.emit('chat_sync', data, room=mission_id, skip_sid=sid)
