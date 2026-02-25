import socketio
import asyncio
import random
from core.services.arch_evaluator import ArchEvaluator

# [수정일: 2026-02-24] 진짜 AI 아키텍트 리뷰를 위한 엔진 초기화
arch_evaluator = ArchEvaluator()

# [수정일: 2026-02-23] 방별 상태 관리 (장애 이벤트 및 방장 추적)
active_rooms = set()
room_leaders = {}  # { mission_id: leader_sid }

# [재접속 복원] 방별 최신 상태 스냅샷 저장
room_snapshots = {}

# [수정일: 2026-02-24] 방별 실시간 게임 상태 (타이머, 페이즈) 권위적 관리
room_game_states = {}
active_timer_tasks = {} # { mission_id: Task }

# [수정일: 2026-02-23] Coduck Wars Phase 2: 실시간 협업용 Socket.io 서버 설정
# 이 서버는 다중 접속 유저 간의 아키텍처 설계 동기화 및 실시간 대화를 관리합니다.

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

@sio.event
async def connect(sid, environ):
    print(f"✅ Socket Connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"❌ Socket Disconnected: {sid}")
    # [수정일: 2026-02-23] 방장이 나갔을 경우 방장 교체 + 퇴장 알림
    session = await sio.get_session(sid)
    if session:
        mission_id = session.get('room')
        user_name = session.get('name', 'Unknown')
        user_role = session.get('role', '')

        if mission_id:
            # 방 전체에 퇴장 알림 브로드캐스트
            await sio.emit('user_left', {
                "sid": sid,
                "user_name": user_name,
                "user_role": user_role
            }, room=mission_id)
            print(f"📢 Broadcasted user_left: {user_name}({sid}) in room {mission_id}")

        if mission_id and room_leaders.get(mission_id) == sid:
            # 새로운 방장 선출
            del room_leaders[mission_id]
            room_sids = list(sio.manager.rooms.get('/', {}).get(mission_id, set()))
            # 나 자신은 이미 나가는 중이므로 제외
            remaining = [s for s in room_sids if s != sid]
            if remaining:
                new_leader = remaining[0]
                room_leaders[mission_id] = new_leader
                print(f"👑 New Leader assigned: {new_leader} for room {mission_id}")
                await sio.emit('leader_info', {"leader_sid": new_leader}, room=mission_id)
            else:
                # 방에 아무도 없으면 활성 방 목록에서도 제거
                if mission_id in active_rooms:
                    active_rooms.remove(mission_id)
        
        # [추가: 2026-02-24] LOGIC RUN 미니게임 방 정리
        run_room_id = session.get('run_room')
        if run_room_id and run_room_id in run_rooms:
            run_rooms[run_room_id]['players'] = [p for p in run_rooms[run_room_id]['players'] if p['sid'] != sid]
            if not run_rooms[run_room_id]['players']:
                del run_rooms[run_room_id]
            else:
                await sio.emit('run_user_left', {'sid': sid}, room=run_room_id)

        # [추가: 2026-02-24] BLUEPRINT(Arch Draw) 미니게임 방 정리
        draw_room_id = session.get('draw_room')
        if draw_room_id and draw_room_id in draw_rooms:
            room = draw_rooms[draw_room_id]
            room['players'] = [p for p in room['players'] if p['sid'] != sid]
            
            if not room['players']:
                del draw_rooms[draw_room_id]
            else:
                # 남은 인원에게 로비 정보 갱신 전송
                players_data = [{'name': p['name'], 'sid': p['sid']} for p in room['players']]
                await sio.emit('draw_lobby', {'players': players_data}, room=draw_room_id)
                print(f"📡 draw_lobby (cleanup) sent to room {draw_room_id}")

@sio.event
async def join_war_room(sid, data):
    """
    미션 ID를 기준으로 팀원들이 하나의 가상 룸에 입장하며 역할 정보를 등록합니다.
    data format: { "mission_id": "...", "user_name": "...", "user_role": "..." }
    """
    mission_id = data.get('mission_id')
    user_name = data.get('user_name', 'Anonymous')
    user_role = data.get('user_role', 'pending') # [수정일: 2026-02-24] 기본 역할을 Architect에서 pending으로 변경
    
    if mission_id:
        await sio.enter_room(sid, mission_id)
        # 세션 데이터에 사용자 정보 저장
        await sio.save_session(sid, {"name": user_name, "role": user_role, "room": mission_id})
        
        # [수정일: 2026-02-23] 입장 로그 강화
        print(f"👥 User {user_name}({sid}) joined War Room: [{mission_id}] as {user_role}")

        # [수정일: 2026-02-23] 방장(Analyzer) 지정: 방에 아무도 없으면 첫 입장자가 방장
        if mission_id not in room_leaders:
            room_leaders[mission_id] = sid
            # [수정일: 2026-02-24] 방이 처음 생성될 때 타이머 초기화 (10분)
            if mission_id not in room_game_states:
                room_game_states[mission_id] = {
                    "phase": "design",
                    "time_left": 600,
                    "is_running": False
                }
            print(f"👑 Leader assigned: {user_name}({sid}) for room {mission_id}")
        
        # 현재 방의 방장 정보를 팀원들에게 알림
        await sio.emit('leader_info', {"leader_sid": room_leaders[mission_id]}, room=mission_id)
        
        # [수정일: 2026-02-24] 현재 방의 게임 상태(타이머 등)를 신규 유입자에게 전송
        current_state = room_game_states.get(mission_id, {"phase": "design", "time_left": 600, "is_running": False})
        await sio.emit('state_sync', {"state": {
            "phase": current_state["phase"],
            "time": current_state["time_left"],
            "progress": 0
        }}, to=sid)

        # [수정일: 2026-02-23] 기존 팀원 목록 조회 및 신규 유저에게 전송
        room_sids = sio.manager.rooms.get('/', {}).get(mission_id, set())
        current_members = []
        for member_sid in room_sids:
            if member_sid == sid: continue
            session = await sio.get_session(member_sid)
            if session:
                current_members.append({
                    "sid": member_sid,
                    "user_name": session.get('name'),
                    "user_role": session.get('role')
                })
        
        await sio.emit('members_list', {"members": current_members}, to=sid)

        # 룸 전체에 유저 입장 및 역할 정보 방송
        await sio.emit('user_joined', {
            "sid": sid, 
            "user_name": user_name,
            "user_role": user_role
        }, room=mission_id)

        # [Phase 4] 실시간 장애 엔진 시뮬레이션 시작 (데모용)
        if mission_id not in active_rooms:
            active_rooms.add(mission_id)
            asyncio.create_task(trigger_chaos_events_demo(mission_id))

@sio.event
async def start_mission(sid, data):
    """[수정일: 2026-02-24] 리더가 미션을 시작하면 모든 팀원을 배틀 화면으로 이동시킴"""
    mission_id = data.get('mission_id')
    if mission_id and room_leaders.get(mission_id) == sid:
        # 서버측 타이머 가동 시작
        if mission_id in room_game_states:
            room_game_states[mission_id]["is_running"] = True
            # 이미 타이머가 돌고 있는지 확인
            if mission_id not in active_timer_tasks or active_timer_tasks[mission_id].done():
                active_timer_tasks[mission_id] = asyncio.create_task(run_room_timer(mission_id))
        
        # 모든 팀원에게 게임 시작 신호 전송
        await sio.emit('mission_start', {"mission_id": mission_id}, room=mission_id)
        print(f"🚀 Mission Started by Leader: {sid} in room {mission_id}")

async def run_room_timer(mission_id):
    """[수정일: 2026-02-24] 서버측에서 방별 1초 단위 타이머 관리"""
    while mission_id in room_game_states and room_game_states[mission_id]["is_running"]:
        state = room_game_states[mission_id]
        if state["time_left"] > 0:
            state["time_left"] -= 1
        
        # 5초마다 전체 동기화 브로드캐스트 (네트워크 부하 최적화)
        if state["time_left"] % 5 == 0:
            await sio.emit('state_sync', {
                "state": {
                    "phase": state["phase"],
                    "time": state["time_left"]
                }
            }, room=mission_id)
            
        await asyncio.sleep(1)
        
        if state["time_left"] <= 0:
            # 페이즈 자동 전환 로직
            if state["phase"] == "design":
                state["phase"] = "blackout"
                state["time_left"] = 120
            elif state["phase"] == "blackout":
                state["phase"] = "defense"
                state["time_left"] = 180
            else:
                state["is_running"] = False
            
            await sio.emit('state_sync', {
                "state": {
                    "phase": state["phase"],
                    "time": state["time_left"]
                }
            }, room=mission_id)

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

    # 이벤트 종료 후 룸 상태 초기화 (추후 다시 시작 가능하게)
    # active_rooms.remove(mission_id) # 무한 루프가 아니므로 필요 시 주석 해제

@sio.event
async def sync_analysis(sid, data):
    """
    한 명의 분석 결과를 방 전체 팀원에게 공유합니다. (중복 분석 방지 및 동기화)
    data format: { "mission_id": "...", "analysis": { ... } }
    """
    mission_id = data.get('mission_id')
    if mission_id:
        await sio.emit('analysis_sync', data, room=mission_id, skip_sid=sid)

@sio.event
async def update_role(sid, data):
    """
    팀원이 로비에서 역할을 변경할 때 방송합니다.
    [버그수정] skip_sid 제거 → 본인에게도 에코백하여 gameStore 동기화
    """
    mission_id = data.get('mission_id')
    new_role = data.get('user_role')
    if mission_id and new_role:
        # 세션에 역할 저장
        session = await sio.get_session(sid)
        if session:
            session['role'] = new_role
            await sio.save_session(sid, session)
        # 방 전체에 브로드쾐스트 (skip_sid 없이 본인도 포함)
        await sio.emit('role_sync', {"sid": sid, "user_role": new_role}, room=mission_id)

@sio.event
async def request_state(sid, data):
    """
    신규 입장자가 현재 방의 공통 상태(시간 등)를 리더에게 요청합니다.
    """
    mission_id = data.get('mission_id')
    if mission_id:
        # 방 전체에 요청을 방송 (리더가 응답할 것임)
        await sio.emit('request_state', {"requester_sid": sid}, room=mission_id, skip_sid=sid)

@sio.event
async def player_status(sid, data):
    """
    [P1] 플레이어 상태(typing / idle / submitted) + 점수를 방 전체에 동기화
    data format: { "mission_id": "...", "user_name": "...", "status": "...", "score": 0 }
    """
    mission_id = data.get('mission_id')
    if mission_id:
        await sio.emit('player_status_sync', {
            "user_name": data.get('user_name'),
            "status":    data.get('status'),
            "score":     data.get('score', 0)
        }, room=mission_id, skip_sid=sid)

@sio.event
async def sync_state(sid, data):
    """
    방의 전체 상태(Phase, Time, Progress)를 동기화합니다.
    [수정일: 2026-02-24] 서버측 상태도 함께 업데이트
    """
    mission_id = data.get('mission_id')
    state_data = data.get('state')
    if mission_id and state_data:
        if mission_id in room_game_states:
            room_game_states[mission_id]["phase"] = state_data.get("phase", room_game_states[mission_id]["phase"])
            room_game_states[mission_id]["time_left"] = state_data.get("time", room_game_states[mission_id]["time_left"])
        
        await sio.emit('state_sync', data, room=mission_id, skip_sid=sid)

@sio.event
async def code_update(sid, data):
    """
    누군가 코드를 수정하면 해당 룸의 모든 팀원에게 동기화합니다.
    data format: { "mission_id": "...", "code_files": { "api": "...", "db": "...", "security": "..." } }
    """
    mission_id = data.get('mission_id')
    code_files = data.get('code_files')
    if mission_id and code_files:
        # 보낸 사람(sender)을 제외한 나머지 팀원들에게 방송
        await sio.emit('code_sync', {"code_files": code_files, "sender": sid}, room=mission_id, skip_sid=sid)

@sio.event
async def canvas_update(sid, data):
    """
    아키텍처(Mermaid) 수정 동기화 (하위 호환성 유지)
    """
    mission_id = data.get('mission_id')
    mermaid_code = data.get('mermaid_code')
    if mission_id and mermaid_code:
        await sio.emit('canvas_sync', {"mermaid_code": mermaid_code, "sender": sid}, room=mission_id, skip_sid=sid)

@sio.event
async def chat_message(sid, data):
    """
    팀원 간 실시간 채팅 메시지를 브로드캐스팅합니다.
    """
    mission_id = data.get('mission_id')
    if mission_id:
        # [수정일: 2026-02-23] 모든 추가 필드(is_ai, is_interview 등)를 포함하여 브로드캐스팅
        sync_data = {
            "sender_name": data.get('sender_name', 'Anonymous'),
            "content": data.get('content', ''),
            "role": 'user'
        }
        # 추가 메타데이터가 있으면 합침
        sync_data.update({k: v for k, v in data.items() if k not in ['mission_id']})
        
        await sio.emit('chat_sync', sync_data, room=mission_id, skip_sid=sid)

# ========== ARCH DRAW (Catch Mind) ==========
# 방별 캐치마인드 상태 관리
draw_rooms = {}  # { room_id: { players: [], round, question, phase, scores } }

@sio.event
async def draw_join(sid, data):
    """Draw 방 입장. 2명 다 모이면 게임 시작"""
    room_id = data.get('room_id', 'draw-default')
    user_name = data.get('user_name', 'Player')
    
    # [수정일: 2026-02-24] 공백 제거 및 로그 강화
    room_id = room_id.strip()
    print(f"📡 draw_join: {user_name} ({sid}) -> room: {room_id}")

    await sio.enter_room(sid, room_id)
    
    # [수정일: 2026-02-24] 세션 정보 저장 (disconnect 시 방 정리에 필요)
    await sio.save_session(sid, {'draw_room': room_id, 'draw_name': user_name})
    
    if room_id not in draw_rooms:
        draw_rooms[room_id] = {'players': [], 'phase': 'waiting'}
    
    room = draw_rooms[room_id]
    
    # [수정일: 2026-02-24] 인원 제한 체크 (최대 2명)
    # 이미 방에 있는 플레이어(재접속)가 아니라면, 2명 이상일 때 입장 거부
    is_existing_player = any(p['sid'] == sid for p in room['players'])
    if not is_existing_player and len(room['players']) >= 2:
        print(f"🚫 draw_join Rejected: Room {room_id} is FULL.")
        await sio.emit('draw_error', {'message': '방이 이미 가득 찼습니다. (최대 2명)'}, to=sid)
        return

    # [수정일: 2026-02-24] 동일 SID 제거 (재접속 대응)
    # 이름이 같더라도 SID가 다르면 별개 인원으로 처리하도록 유지하되, 
    # 같은 SID가 들어오면 기존 데이터 갱신
    room['players'] = [p for p in room['players'] if p['sid'] != sid]
    room['players'].append({'sid': sid, 'name': user_name, 'score': 0})
    
    players_data = [{'name': p['name'], 'sid': p['sid']} for p in room['players']]
    print(f"👥 Room {room_id} players: {[p['name'] for p in room['players']]}")
    print(f"📂 Active draw rooms: {list(draw_rooms.keys())}")
    
    await sio.emit('draw_lobby', {'players': players_data}, room=room_id)
    
    if len(room['players']) >= 2:
        if room['phase'] == 'waiting':
            room['phase'] = 'ready'
        await sio.emit('draw_ready', {}, room=room_id)
        print(f"🏁 Room {room_id} is READY!")

@sio.event
async def draw_start(sid, data):
    """게임 시작: 서버에서 시나리오를 결정하여 배포"""
    room_id = data.get('room_id', 'draw-default')
    
    # [수정일: 2026-02-24] 사용자 경험 개선을 위해 미션을 단순 나열형에서 '비즈니스 시나리오' 기반으로 개편
    ARCH_MISSIONS = [
        {
            "title": "글로벌 뱅킹 트래픽 분산", 
            "description": "전 세계에서 몰려오는 금융 트래픽을 지역별로 분산하고, 모든 데이터를 중앙 DB에 안전하게 복제하는 고가용성 구조를 설계하세요.", 
            "required": ["lb", "server", "db", "readdb"],
            "hints": ["부하 분산 장치가 맨 앞에 필요합니다", "읽기 성능 향상을 위해 복제본(Read Replica)을 사용하세요"]
        },
        {
            "title": "실시간 OTT 스트리밍 최적화", 
            "description": "사용자에게 가장 가까운 곳에서 영상을 빠르게 전달(캐싱)하고, 대용량 원본 파일은 안전한 저장소에 보관하는 전달 체계를 설계하세요.", 
            "required": ["user", "cdn", "server", "origin"],
            "hints": ["사용자와 가까운 거리의 Edge 서버(CDN)가 핵심입니다", "원본은 Origin 서버나 스토리지에 둡니다"]
        },
        {
            "title": "비동기 대용량 로그 수집", 
            "description": "순식간에 쏟아지는 수백만 건의 데이터를 유실 없이 수집하여 분석 시스템으로 안전하게 전달하는 비동기 파이프라인을 구축하세요.", 
            "required": ["producer", "queue", "consumer", "db"],
            "hints": ["데이터 완충 지역인 메시지 큐가 필요합니다", "소비자(Consumer)가 큐에서 데이터를 꺼내 처리합니다"]
        },
        {
            "title": "읽기/쓰기 분리(CQRS) 시스템", 
            "description": "주문이 폭주해도 상품 조회가 느려지지 않도록, 데이터를 생성하는 경로와 조회하는 경로를 완전히 분리한 고성능 아키텍처를 설계하세요.", 
            "required": ["api", "writesvc", "readsvc", "writedb", "readdb"],
            "hints": ["API Gateway가 요청을 두 갈래로 나눕니다", "DB도 쓰기 전용과 읽기 전용을 분리하세요"]
        },
        {
            "title": "보안 강화 하이브리드 클라우드", 
            "description": "외부 공격으로부터 API 서버를 보호하고, 온프레미스의 기존 데이터 센터와 클라우드 자원을 안전하게 연결하는 구조를 설계하세요.", 
            "required": ["user", "waf", "api", "origin"],
            "hints": ["최전방에 웹 방화벽(WAF)을 배치하세요", "기존 인프라는 전용선(Direct Connect) 등으로 연결됩니다"]
        }
    ]
    question = random.choice(ARCH_MISSIONS)
    
    if room_id in draw_rooms:
        draw_rooms[room_id]['phase'] = 'playing'
        draw_rooms[room_id]['current_question'] = question
        draw_rooms[room_id]['round'] = 1  # [추가] 라운드 추적 시작
        
    await sio.emit('draw_round_start', {'question': question, 'round': 1}, room=room_id)

@sio.event
async def draw_canvas_sync(sid, data):
    """내 캔버스를 상대에게 실시간 전송 (nodes + arrows)"""
    room_id = data.get('room_id', 'draw-default')
    await sio.emit('draw_canvas_update', {
        'sender_sid': sid,
        'sender_name': data.get('user_name', ''),
        'nodes': data.get('nodes', []),
        'arrows': data.get('arrows', [])
    }, room=room_id, skip_sid=sid)

@sio.event
async def draw_submit(sid, data):
    """플레이어가 제출. 둘 다 제출하면 결과 비교"""
    room_id = data.get('room_id', 'draw-default')
    score = data.get('score', 0)
    checks = data.get('checks', [])
    final_nodes = data.get('final_nodes', [])
    final_arrows = data.get('final_arrows', [])
    
    room = draw_rooms.get(room_id)
    if not room: return
    # 플레이어 점수 업데이트
    for p in room['players']:
        if p['sid'] == sid:
            p['score'] += score       # 누적 점수
            p['last_pts'] = score     # 이번 라운드 획득 점수
            p['last_checks'] = checks
            p['last_nodes'] = final_nodes
            p['last_arrows'] = final_arrows
            p['submitted'] = True
    
    await sio.emit('draw_player_submitted', {'sid': sid, 'score': score}, room=room_id)
    
    # 모두 제출했으면 결과 방송
    if all(p.get('submitted') for p in room['players']):
        # [수정일: 2026-02-24] LLM 기반 정성적 아키텍트 리뷰 생성
        mission_title = room.get('current_question', {}).get('title', 'Unknown Mission')
        p1 = room['players'][0]
        p2 = room['players'][1] if len(room['players']) > 1 else room['players'][0]
        
        # 비동기 상황이지만 LLM 호출은 블로킹으로 처리 (timeout 15s 설정됨)
        ai_reviews = arch_evaluator.evaluate_comparison(
            mission_title,
            {'name': p1['name'], 'pts': p1['last_pts'], 'checks': p1['last_checks']},
            {'name': p2['name'], 'pts': p2['last_pts'], 'checks': p2['last_checks']}
        )
        
        results = []
        for i, p in enumerate(room['players']):
            review_key = f"player{i+1}"
            p_review = ai_reviews.get(review_key, {})
            results.append({
                'name': p['name'], 
                'sid': p['sid'], 
                'score': p['score'],      # 누적 점수
                'last_pts': p.get('last_pts', 0), # 라운드 점수
                'last_checks': p.get('last_checks', []),
                'last_nodes': p.get('last_nodes', []),
                'last_arrows': p.get('last_arrows', []),
                'ai_review': p_review     # 진짜 AI가 생성한 리뷰 추가
            })
            
        await sio.emit('draw_round_result', {'results': results}, room=room_id)
        for p in room['players']: 
            p['submitted'] = False
            p['last_pts'] = 0  # 초기화

@sio.event
async def draw_use_item(sid, data):
    """아이템 사용 이벤트 브로드캐스트"""
    room_id = data.get('room_id', 'draw-default')
    item_type = data.get('item_type')
    await sio.emit('draw_item_effect', {'item_type': item_type}, room=room_id, skip_sid=sid)

@sio.event
async def draw_item_status(sid, data):
    """아이템 보유 상태(Ready 여부) 동기화"""
    room_id = data.get('room_id', 'draw-default')
    has_item = data.get('has_item', False)
    await sio.emit('draw_opponent_item_status', {'sid': sid, 'has_item': has_item}, room=room_id, skip_sid=sid)

@sio.event
async def draw_next_round(sid, data):
    """
    [수정일: 2026-02-24] 다음 라운드 시작 신호 및 미션 데이터 고도화.
    기존에 room_id가 누락되어 발생하던 NameError 수정.
    """
    room_id = data.get('room_id', 'draw-default')
    
    # [수정일: 2026-02-24] 다음 라운드 미션 고도화 (비즈니스 시뮬레이션 강화)
    ARCH_MISSIONS = [
        {
            "title": "서버리스(Serverless) API 플랫폼", 
            "description": "서버 관리 부담을 최소화하고 트래픽에 따라 자동 확장되는 API 환경을 구축하세요. 정적 자원은 게이트웨이 뒤의 함수를 거쳐 DB에 저장됩니다.", 
            "required": ["client", "api", "server", "db"],
            "hints": ["진입점에 API Gateway를 배치하세요", "Lambda와 같은 함수 기반 서버(Server)를 사용합니다"]
        },
        {
            "title": "하이브리드 멀티클라우드 연결", 
            "description": "기존 데이터 센터의 원본 데이터를 클라우드의 로드밸런서를 통해 전 세계 사용자에게 서비스하는 하이브리드 인프라를 설계하세요.", 
            "required": ["origin", "dns", "lb", "server"],
            "hints": ["On-Premise 센터(Origin)와 연결이 필요합니다", "트래픽 유입을 위한 DNS 설정을 잊지 마세요"]
        }
    ]
    question = random.choice(ARCH_MISSIONS)
    if room_id in draw_rooms:
        room = draw_rooms[room_id]
        room['round'] = room.get('round', 1) + 1
        
        # [수정일: 2026-02-24] 5라운드 제한 적용
        if room['round'] > 5:
            print(f"🏁 Room {room_id} finished all rounds (5/5).")
            # 게임 종료 전용 이벤트를 보내거나, 클라이언트가 UI상에서 처리하도록 유항
            await sio.emit('draw_game_over', {}, room=room_id) 
            return

        room['current_question'] = question
        await sio.emit('draw_round_start', {'question': question, 'round': room['round']}, room=room_id)

@sio.event
async def draw_leave(sid, data):
    room_id = data.get('room_id', 'draw-default')
    if room_id in draw_rooms:
        draw_rooms[room_id]['players'] = [p for p in draw_rooms[room_id]['players'] if p['sid'] != sid]
        if not draw_rooms[room_id]['players']:
            del draw_rooms[room_id]
        else:
            # [수정일: 2026-02-24] UI 동기화를 위해 draw_lobby 전송
            players_data = [{'name': p['name'], 'sid': p['sid']} for p in draw_rooms[room_id]['players']]
            await sio.emit('draw_lobby', {'players': players_data}, room=room_id)
            print(f"📡 draw_lobby (leave) sent to room {room_id}")
    await sio.leave_room(sid, room_id)

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

# ========== LOGIC RUN (Relay Race) ==========
# [수정일: 2026-02-24] 로직 런 실시간 멀티플레이어 상태 관리
run_rooms = {}  # { room_id: { players: [], phase, current_quest, ai_pos, player_pos } }

@sio.event
async def run_join(sid, data):
    """로직 런 방 입장: 이름과 아바타 정보를 포함"""
    room_id = data.get('room_id', 'run-default').strip()
    user_name = data.get('user_name', 'Anonymous')
    avatar_url = data.get('avatar_url', '/image/duck_idle.png')
    
    print(f"🏃 run_join: {user_name} ({sid}) -> room: {room_id}")
    await sio.enter_room(sid, room_id)
    await sio.save_session(sid, {'run_room': room_id, 'run_name': user_name})
    
    if room_id not in run_rooms:
        run_rooms[room_id] = {'players': [], 'phase': 'lobby', 'quest': None, 'leader_sid': None}
    
    room = run_rooms[room_id]
    # 방장(Leader) 지정: 첫 번째 플레이어
    if not room.get('leader_sid'):
        room['leader_sid'] = sid

    # 중복 입장 방지 및 기존 플레이어 정보 업데이트
    existing_player = next((p for p in room['players'] if p['sid'] == sid), None)
    if existing_player:
        existing_player.update({'name': user_name, 'avatar_url': avatar_url})
    else:
        room['players'].append({
            'sid': sid, 
            'name': user_name, 
            'avatar_url': avatar_url,
            'ready': False
        })
    
    players_data = [{'name': p['name'], 'sid': p['sid'], 'avatar_url': p['avatar_url']} for p in room['players']]
    await sio.emit('run_lobby', {
        'players': players_data, 
        'leader_sid': room['leader_sid']
    }, room=room_id)
    
    if len(room['players']) >= 2:
        await sio.emit('run_ready', {'ready': True}, room=room_id)

@sio.event
async def run_start(sid, data):
    """게임 시작: 퀘스트 인덱스를 결정하여 모든 플레이어에게 전파"""
    room_id = data.get('room_id')
    if room_id in run_rooms:
        run_rooms[room_id]['phase'] = 'playing'
        # 퀘스트 인덱스 생성 (현재 quests가 1개뿐이므로 0 고정 가능하나 확장성 위해 전송)
        quest_idx = random.randint(0, 0) # 퀘스트 추가 시 범위 수정 필요
        await sio.emit('run_game_start', {'quest_idx': quest_idx}, room=room_id)

@sio.event
async def run_progress(sid, data):
    """플레이어 진행도 동기화 (전진, 힌트 등)"""
    room_id = data.get('room_id')
    # 받은 데이터(playerPos, playerIdx, lineIdx 등)를 다른 팀원에게 전달
    await sio.emit('run_sync', data, room=room_id, skip_sid=sid)

@sio.event
async def run_relay_start(sid, data):
    """섹터 완료 후 바통 패스 페이즈 진입"""
    room_id = data.get('room_id')
    await sio.emit('run_relay', data, room=room_id, skip_sid=sid)

@sio.event
async def run_highfive(sid, data):
    """하이파이브 성공 여부 동기화"""
    room_id = data.get('room_id')
    await sio.emit('run_hf_sync', data, room=room_id, skip_sid=sid)

@sio.event
async def run_ai_sync(sid, data):
    """AI 위치 동기화 (주로 방장이 관리)"""
    room_id = data.get('room_id')
    await sio.emit('run_ai_pos', data, room=room_id, skip_sid=sid)

@sio.event
async def run_finish(sid, data):
    """게임 종료 (완료 또는 게임오버)"""
    room_id = data.get('room_id')
    await sio.emit('run_end', data, room=room_id)

@sio.event
async def run_leave(sid, data):
    """방 퇴장"""
    room_id = data.get('room_id', 'run-default')
    if room_id in run_rooms:
        room = run_rooms[room_id]
        room['players'] = [p for p in room['players'] if p['sid'] != sid]
        
        # 방장이 나갔다면 권한 위임
        if room.get('leader_sid') == sid:
            if room['players']:
                room['leader_sid'] = room['players'][0]['sid']
            else:
                room['leader_sid'] = None

        if not room['players']:
            del run_rooms[room_id]
        else:
            await sio.emit('run_user_left', {
                'sid': sid, 
                'leader_sid': room.get('leader_sid')
            }, room=room_id)
    await sio.leave_room(sid, room_id)
