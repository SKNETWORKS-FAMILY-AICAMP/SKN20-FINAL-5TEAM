import socketio
import asyncio
import random
from core.services.arch_evaluator import ArchEvaluator
from core.services.pseudocode_evaluator import PseudocodeEvaluator, EvaluationRequest, EvaluationMode
from asgiref.sync import sync_to_async

# [수정일: 2026-02-24] 진짜 AI 아키텍트 리뷰를 위한 엔진 초기화
arch_evaluator = ArchEvaluator()

# [수정일: 2026-02-25] 의사코드 평가 엔진 (LLM 기반)
pseudocode_evaluator = PseudocodeEvaluator()

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
bubble_rooms = {}  # [추가: 2026-02-25] Bug-Bubble Monster 미니게임 방 관리

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

        # [추가: 2026-02-25] BUG-BUBBLE MONSTER 방 정리
        bubble_room_id = session.get('bubble_room')
        if bubble_room_id and bubble_room_id in bubble_rooms:
            b_room = bubble_rooms[bubble_room_id]
            b_room['players'] = [p for p in b_room['players'] if p['sid'] != sid]
            
            if not b_room['players']:
                del bubble_rooms[bubble_room_id]
            else:
                players_data = [{'name': p['name'], 'sid': p['sid']} for p in b_room['players']]
                await sio.emit('bubble_lobby', {'players': players_data}, room=bubble_room_id)
                await sio.emit('bubble_player_left', {'sid': sid}, room=bubble_room_id)
                
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
    
    # [수정일: 2026-02-25] 인원 제한 체크 (최대 2명) - 강화됨
    # 이미 방에 있는 플레이어(재접속)가 아니라면, 2명 이상일 때 얄짤없이 입장 거부
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
    print(f"📡 draw_start called by {sid} for room {data.get('room_id')}")
    try:
        from core.models import PracticeDetail
        from asgiref.sync import sync_to_async
        room_id = data.get('room_id', 'draw-default')
        
        # [수정일: 2026-02-25] 데이터베이스에서 아키텍처 문제 및 평가 기준(Rubric) 동적 로드
        @sync_to_async
        def get_questions():
            return list(PracticeDetail.objects.filter(practice_id='unit03').values('content_data'))
            
        questions = await get_questions()
        print(f"✅ DB Questions loaded: {len(questions)} items")
    except Exception as e:
        print(f"❌ Error in draw_start DB fetch: {e}")
        questions = []
    if questions:
        q_data = random.choice(questions)['content_data']
        required_names = q_data.get('rubric_functional', {}).get('required_components', [])
        
        # Frontend의 allComps id와 매핑하기 위한 키워드 사전
        COMP_MAP = {
            "client": ["client", "사용자", "단말", "user", "app", "web", "클라이언트"],
            "lb": ["lb", "load balancer", "로드밸런서", "elb", "alb", "분산"],
            "server": ["server", "서버", "ec2", "was", "web server", "api server", "웹서버", "어플리케이션", "랭킹", "게시물"],
            "cdn": ["cdn", "cloudfront", "콘텐츠"],
            "origin": ["origin", "오리진"],
            "cache": ["cache", "캐시", "redis", "memcached"],
            "db": ["db", "database", "데이터베이스", "rdbms", "mysql", "postgresql", "oracle", "저장소"],
            "producer": ["producer", "프로듀서"],
            "queue": ["queue", "msgq", "message queue", "큐", "메시지", "kafka", "rabbitmq", "sqs", "비동기"],
            "consumer": ["consumer", "컨슈머"],
            "api": ["api", "api gw", "api gateway", "gateway", "게이트웨이"],
            "writesvc": ["write", "쓰기"],
            "readsvc": ["read", "읽기"],
            "writedb": ["writedb", "쓰기 db", "마스터", "master"],
            "readdb": ["readdb", "읽기 db", "슬레이브", "slave", "read replica", "복제"],
            "auth": ["auth", "인증", "권리", "권한", "로그인", "iam"],
            "order": ["order", "주문"],
            "payment": ["pay", "payment", "결제", "회계"],
            "waf": ["waf", "방화벽", "보안", "방어"],
            "dns": ["dns", "route53", "도메인", "라우팅"]
        }

        mapped_required = set()
        for req_name in required_names:
            req_lower = req_name.lower()
            matched = False
            for comp_id, keywords in COMP_MAP.items():
                if any(kw in req_lower for kw in keywords):
                    mapped_required.add(comp_id)
                    matched = True
                    break
            if not matched:
                if "데이터" in req_lower: mapped_required.add("db")
                elif "서비스" in req_lower or "시스템" in req_lower: mapped_required.add("server")
        
        question = {
            "title": q_data.get('title', 'Unknown Mission'), 
            "description": q_data.get('scenario', ''), 
            "required": list(mapped_required) if mapped_required else ["client", "server", "db"],
            "hints": q_data.get('missions', []),
            "rubric": q_data.get('rubric_functional', {}),
            "axis_weights": q_data.get('axis_weights', {})
        }
    else:
        # DB에 데이터가 없을 경우 Fallback
        question = {
            "title": "글로벌 뱅킹 트래픽 분산", 
            "description": "전 세계에서 몰려오는 금융 트래픽을 지역별로 분산하고, 모든 데이터를 중앙 DB에 안전하게 복제하는 고가용성 구조를 설계하세요.", 
            "required": ["lb", "server", "db", "readdb"],
            "hints": ["부하 분산 장치가 맨 앞에 필요합니다", "읽기 성능 향상을 위해 복제본(Read Replica)을 사용하세요"],
            "rubric": {},
            "axis_weights": {}
        }
    
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
        # [수정일: 2026-02-25] DB 루브릭 연동 및 LLM 기반 정성적 아키텍트 리뷰 생성
        current_q = room.get('current_question', {})
        mission_title = current_q.get('title', 'Unknown Mission')
        rubric_data = current_q.get('rubric', {})
        if 'axis_weights' in current_q:
            rubric_data['axis_weights'] = current_q['axis_weights']

        p1 = room['players'][0]
        p2 = room['players'][1] if len(room['players']) > 1 else room['players'][0]
        
        # [수정일: 2026-02-25] LLM 호출이 블로킹되지 않도록 sync_to_async 적용
        from asgiref.sync import sync_to_async
        eval_func = sync_to_async(arch_evaluator.evaluate_comparison)
        
        try:
            ai_reviews = await eval_func(
                mission_title,
                {'name': p1['name'], 'pts': p1['last_pts'], 'checks': p1['last_checks'], 'nodes': p1.get('last_nodes', []), 'arrows': p1.get('last_arrows', [])},
                {'name': p2['name'], 'pts': p2['last_pts'], 'checks': p2['last_checks'], 'nodes': p2.get('last_nodes', []), 'arrows': p2.get('last_arrows', [])},
                rubric=rubric_data
            )
            print(f"✅ AI Review generated: {ai_reviews.keys()}")
        except Exception as e:
            print(f"❌ AI Review Error: {e}")
            ai_reviews = arch_evaluator._fallback_review(
                {'name': p1['name'], 'pts': p1['last_pts'], 'checks': p1['last_checks'], 'nodes': p1.get('last_nodes', []), 'arrows': p1.get('last_arrows', [])},
                {'name': p2['name'], 'pts': p2['last_pts'], 'checks': p2['last_checks'], 'nodes': p2.get('last_nodes', []), 'arrows': p2.get('last_arrows', [])}
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

# [수정일: 2026-02-25] Phase 2 양쪽 코드 수집 (향후 LLM 평가용)
run_phase2_submissions = {}  # { room_id: { sid: { code, checks, points }, ... } }

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
            'ready': False,
            'phase1_score': 0,  # ← 추가: Phase 1 점수
            'phase2_score': 0   # ← 추가: Phase 2 점수
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
    """플레이어 진행도 동기화 (Phase 1: 속도전, Phase 2: 설계 스프린트)"""
    room_id = data.get('room_id')

    # [수정일: 2026-02-25] Phase 1 점수 저장 (최종 점수 계산용)
    if data.get('phase') == 'speedFill' and room_id in run_rooms:
        # run_rooms의 player 객체에 phase 1 점수 저장
        for player in run_rooms[room_id]['players']:
            if player['sid'] == sid:
                player['phase1_score'] = data.get('score', 0)
                break

    # [수정일: 2026-02-25] Phase 2 코드 제출 감지 (향후 LLM 평가용)
    if data.get('phase') == 'designSprint' and data.get('state') == 'submitted':
        if room_id not in run_phase2_submissions:
            run_phase2_submissions[room_id] = {}

        # 양쪽 코드 수집
        run_phase2_submissions[room_id][sid] = {
            'code': data.get('code', ''),
            'checksCompleted': data.get('checksCompleted', 0),
            'totalPoints': data.get('score', 0)
        }

        print(f"📝 Phase 2 Submission #{len(run_phase2_submissions[room_id])}: {sid} in room {room_id}")

        # Phase 2 점수도 run_rooms에 저장
        if room_id in run_rooms:
            for player in run_rooms[room_id]['players']:
                if player['sid'] == sid:
                    player['phase2_score'] = data.get('score', 0)
                    break

        # 양쪽 모두 제출되었는지 확인
        if len(run_phase2_submissions[room_id]) >= 2:
            # [추가: 2026-02-25] LLM 평가 호출
            asyncio.create_task(evaluate_and_broadcast_designs(room_id, data))
            print(f"✅ Both players submitted in room {room_id} - LLM evaluation started")

    # 기존 실시간 동기화 로직 (모든 프로그레스 전파)
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

# [추가: 2026-02-25] LLM 기반 의사코드 평가 함수
async def evaluate_and_broadcast_designs(room_id, latest_data):
    """
    양쪽 플레이어의 의사코드를 LLM으로 평가하고 결과를 브로드캐스트.

    Args:
        room_id: 게임방 ID
        latest_data: Phase 2 제출 데이터 (scenario, quest_title 등 포함)
    """
    try:
        submissions = run_phase2_submissions.get(room_id, {})
        sids = list(submissions.keys())

        if len(sids) < 2:
            print(f"⚠️ Not enough submissions for evaluation in room {room_id}")
            return

        # 각 코드에 대해 개별 평가
        results = {}
        quest_title = latest_data.get('scenario', 'Design Sprint Challenge')

        for idx, sid in enumerate(sids, 1):
            submission = submissions[sid]
            pseudocode = submission['code']

            try:
                # [수정: 2026-02-25] sync_to_async로 동기 함수 호출
                final_result = await sync_to_async(pseudocode_evaluator.evaluate)(
                    EvaluationRequest(
                        user_id=sid,
                        detail_id='logicrun_phase2',
                        pseudocode=pseudocode,
                        mode=EvaluationMode.OPTION2_GPTONLY,
                        quest_title=quest_title
                    )
                )

                results[sid] = {
                    'status': 'success',
                    'llm_score': final_result.final_score,
                    'grade': final_result.grade,
                    'feedback': final_result.feedback.get('main_feedback', ''),
                    'strengths': final_result.feedback.get('strengths', []),
                    'weaknesses': final_result.feedback.get('weaknesses', []),
                    'improvement_suggestions': final_result.feedback.get('improvement_suggestions', ''),
                    'dimension_scores': final_result.score_breakdown.get('llm_scores', {})
                }
                print(f"✅ LLM Evaluation P{idx}: {sid} → Score: {final_result.final_score}, Grade: {final_result.grade}")

            except Exception as e:
                results[sid] = {
                    'status': 'error',
                    'error_message': str(e),
                    'llm_score': 0
                }
                print(f"❌ LLM Evaluation Error for {sid}: {str(e)}")

        # 결과 브로드캐스트
        if len(results) >= 2:
            await sio.emit('run_design_evaluation', {
                'player1_sid': sids[0],
                'player1_evaluation': results.get(sids[0], {'status': 'error'}),
                'player2_sid': sids[1],
                'player2_evaluation': results.get(sids[1], {'status': 'error'})
            }, room=room_id)
            print(f"📢 Broadcasted design evaluation results to room {room_id}")

    except Exception as e:
        print(f"❌ evaluate_and_broadcast_designs error: {str(e)}")

@sio.event
async def run_finish(sid, data):
    """게임 종료 (완료 또는 게임오버)"""
    room_id = data.get('room_id')

    # [수정일: 2026-02-25] 상대 점수 정보 추가
    if room_id in run_rooms:
        room = run_rooms[room_id]
        opponent_player = next((p for p in room['players'] if p['sid'] != sid), None)

        if opponent_player:
            # 상대 Phase 1, Phase 2 점수 가져오기
            data['opponent_phase1_score'] = opponent_player.get('phase1_score', 0)
            data['opponent_phase2_score'] = opponent_player.get('phase2_score', 0)
            print(f"✅ Added opponent scores to run_end: P1={data['opponent_phase1_score']}, P2={data['opponent_phase2_score']}")

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
            # [수정 2026-02-25] 방이 비어있으면 Phase 2 제출 관련 데이터도 정리
            if room_id in run_phase2_submissions:
                del run_phase2_submissions[room_id]
        else:
            await sio.emit('run_user_left', {
                'sid': sid, 
                'leader_sid': room.get('leader_sid')
            }, room=room_id)
    await sio.leave_room(sid, room_id)

# ==========================================
# [추가일: 2026-02-25] BUG-BUBBLE MONSTER (버그버블 몬스터)
# ==========================================

@sio.event
async def bubble_join(sid, data):
    room_id = data.get('room_id', 'bubble-default')
    user_name = data.get('user_name', 'Unknown')
    user_avatar = data.get('user_avatar', None)
    await sio.enter_room(sid, room_id)
    await sio.save_session(sid, {'bubble_room': room_id, 'name': user_name, 'avatar': user_avatar})
    
    if room_id not in bubble_rooms:
        bubble_rooms[room_id] = {'players': [], 'is_playing': False}
        
    room = bubble_rooms[room_id]
    
    if not any(p['sid'] == sid for p in room['players']):
        room['players'].append({'sid': sid, 'name': user_name, 'avatar': user_avatar})
        
    players_data = [{'name': p['name'], 'sid': p['sid'], 'avatar': p.get('avatar')} for p in room['players']]
    await sio.emit('bubble_lobby', {'players': players_data}, room=room_id)

@sio.event
async def bubble_start(sid, data):
    room_id = data.get('room_id')
    if room_id in bubble_rooms:
        bubble_rooms[room_id]['is_playing'] = True
        await sio.emit('bubble_game_start', {}, room=room_id)

@sio.event
async def bubble_send_monster(sid, data):
    room_id = data.get('room_id')
    monster_type = data.get('monster_type', 'normal')
    await sio.emit('bubble_receive_monster', {'sender_sid': sid, 'monster_type': monster_type}, room=room_id, skip_sid=sid)

@sio.event
async def bubble_fever_attack(sid, data):
    room_id = data.get('room_id')
    count = data.get('count', 5)
    await sio.emit('bubble_receive_fever', {'sender_sid': sid, 'count': count}, room=room_id, skip_sid=sid)

@sio.event
async def bubble_game_over(sid, data):
    room_id = data.get('room_id')
    await sio.emit('bubble_end', {'loser_sid': sid}, room=room_id)
