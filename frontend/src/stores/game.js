import { defineStore } from 'pinia';
import axios from 'axios';
import { aiQuests } from '../features/practice/pseudocode/data/stages.js'; // [수정일: 2026-02-06] 폴더 계층화(data) 반영
// [수정일: 2026-02-06] 비활성 데이터 임포트 경로 수정 (support -> not_use/support)
// import { aiDetectiveQuests } from '../features/practice/not_use/support/unit1/logic-mirror/data/aiDetectiveQuests.js';
// [수정일: 2026-01-31] 비활성 데이터 임포트 주석 처리
// import forestGameData from '../features/practice/PseudoForestData.js';

/**
 * [수정일: 2026-01-27]
 * [수정내용: DB Practice 연동과 Pseudo Practice(aiQuests) 및 Debug Practice(progressiveProblems)의 통합 병합]
 */
export const useGameStore = defineStore('game', {
    state: () => ({
        chapters: [],
        unitProgress: {
            'Pseudo Practice': [0],
            'Debug Practice': [0],
            'System Practice': [0],
            // [수정일: 2026-01-28] Pseudo Forest 전용 진행도 초기값 추가
            'Pseudo Forest': [0],
            // [수정일: 2026-01-29] Pseudo Company 전용 진행도 초기값 추가
            'Pseudo Company': [0],
            // [수정일: 2026-01-29] Pseudo Emergency 전용 진행도 초기값 추가
            'Pseudo Emergency': [0]
        },
        activeUnit: null,
        activeProblem: null,
        activeChapter: null,
        currentDebugMode: 'bug-hunt',
        // [수정일: 2026-01-28] Unit 1의 현재 모드 확장 (pseudo-practice | ai-detective | pseudo-forest | pseudo-company | pseudo-emergency)
        unit1Mode: 'pseudo-practice',
        selectedQuestIndex: 0,
        selectedSystemProblemIndex: 0,
        // [수정일: 2026-02-09] 서버에서 불러온 사용자 해결 문제 기록 저장
        userSolvedProblems: []
    }),

    actions: {
        /**
         * [초기 게임 데이터 로드]
         * - 백엔드 API(/api/core/practices/)로부터 연습 유닛 목록을 가져와 스토어에 저장합니다.
         * - DB에서 가져온 데이터를 프론트엔드 UI 컴포넌트에서 요구하는 형식으로 변환(Mapping)합니다.
         */
        async initGame() {
            try {
                // [2026-01-25] 백엔드로부터 활성화된 모든 연습 유닛 목록 조회 (withCredentials: 세션 쿠키 포함)
                const response = await axios.get('/api/core/practices/', {
                    withCredentials: true
                });

                // UI에서 사용할 폴백(Fallback) 매핑 테이블
                const colors = ['#58cc02', '#1cb0f6', '#ff9600', '#ce82ff', '#ff4b4b'];
                const iconMap = {
                    'Pseudo Practice': 'gamepad-2',
                    'Debug Practice': 'bug',
                    'System Practice': 'layers'
                };
                const imageMap = {
                    'Pseudo Practice': '/image/unit_code.png',
                    'Debug Practice': '/image/unit_debug.png',
                    'System Practice': '/image/unit_system.png'
                };

                // [데이터 매핑 로직] DB 필드값을 UI 카드 컴포넌트의 props 형식에 맞게 변환하여 chapters 배열 구성
                this.chapters = response.data.map((item, idx) => {
                    // [수정일: 2026-02-03] 백엔드 명칭이 다르더라도 프론트엔드 표준 명칭으로 정규화
                    let normalizedTitle = item.title;
                    const lowerTitle = (item.title || '').toLowerCase().replace(/\s+/g, '');

                    if (lowerTitle.includes('pseudo')) normalizedTitle = 'Pseudo Practice';
                    else if (lowerTitle.includes('debug')) normalizedTitle = 'Debug Practice';
                    else if (lowerTitle.includes('system')) normalizedTitle = 'System Practice';

                    const problems = this.mapDetailsToProblems({ ...item, title: normalizedTitle }, idx + 1);
                    const isDebugPractice = normalizedTitle === 'Debug Practice';

                    return {
                        id: item.id,            // 고유 ID
                        db_id: item.id,         // DB 연동 확인용 ID
                        name: normalizedTitle,  // 화면 표시 제목 (표준화됨)
                        unitTitle: item.title,  // 상세 모달 제목용
                        description: item.subtitle, // 카드 하단 부제
                        participant_count: item.participant_count, // 훈련 참여자 수
                        unit_number: item.unit_number, // 유닛 번호 (UNIT XX)
                        level: item.level,      // 권장 레벨 (LV.XX)

                        // [2026-01-25] DB 필드 우선 사용, 없으면 하드코딩 폴백 적용
                        image: item.icon_image || imageMap[item.title] || '/image/unit_code.png',
                        color: item.color_code || colors[idx % colors.length],
                        icon: item.icon_name || iconMap[item.title] || 'book',

                        // [2026-01-25] 하드코딩 제거: DB의 PracticeDetail 리스트에서 'PROBLEM' 타입만 추출하여 문제 구성
                        problems
                    };
                });

                // [2026-02-22] RDS에서 진행도 로드 (localStorage는 폴백용)
                try {
                    const progressRes = await axios.get('/api/core/activity/progress/', { withCredentials: true });
                    progressRes.data.forEach(p => {
                        const key = p.unit_title;
                        if (key && p.unlocked_nodes?.length) {
                            const existing = this.unitProgress[key] || [0];
                            this.unitProgress[key] = Array.from(new Set([...existing, ...p.unlocked_nodes])).sort((a, b) => a - b);
                        }
                    });
                    // RDS 로드 성공 시 localStorage도 동기화
                    localStorage.setItem('logic_mirror_progress', JSON.stringify(this.unitProgress));
                } catch (progressError) {
                    // RDS 실패 시 localStorage 폴백
                    console.warn('[GameStore] RDS progress load failed, using localStorage fallback:', progressError);
                    const savedProgress = localStorage.getItem('logic_mirror_progress');
                    if (savedProgress) {
                        const parsed = JSON.parse(savedProgress);
                        Object.keys(this.unitProgress).forEach(key => {
                            if (parsed[key]) {
                                this.unitProgress[key] = Array.from(new Set([...this.unitProgress[key], ...parsed[key]])).sort((a, b) => a - b);
                            }
                        });
                    }
                }

            } catch (error) {
                console.error("Failed to fetch practice units from DB:", error);
            }
        },

        /**
         * [상세 데이터를 문제 객체로 변환]
         * - [2026-01-27] 수정: Pseudo Practice와 Debug Practice(Bug Hunt)는 로컬/Progressive 데이터를 우선 사용합니다.
         * - 그 외의 유닛들은 백엔드 DB의 PracticeDetail 정보를 기반으로 동적으로 구성됩니다.
         */
        mapDetailsToProblems(unit, unitNum) {
            // [수정일: 2026-02-03] 명칭 정규화: 'pseudo'가 포함되면 Pseudo Practice로 간주
            const rawTitle = unit.name || unit.title || '';
            const unitTitle = rawTitle.toLowerCase().replace(/\s+/g, '');

            // [Unit 1] Pseudo Practice 처리
            if (unitTitle.includes('pseudo')) {
                // unit1Mode에 따라 서로 다른 문제 세트 매핑 및 반환
                if (this.unit1Mode === 'pseudo-practice') {
                    return aiQuests.map((q, idx) => ({
                        id: q.id,
                        title: q.title,
                        questIndex: idx,
                        displayNum: `${unitNum}-${idx + 1}`,
                        difficulty: q.level > 3 ? 'hard' : (q.level > 1 ? 'medium' : 'easy'),
                        config: q,
                        mode: 'pseudo-practice'
                    }));
                }
                else if (this.unit1Mode === 'pseudo-forest') {
                    // [수정일: 2026-01-28] Pseudo Forest 정규 10단계 데이터 매핑
                    return forestGameData.map((q, idx) => ({
                        id: `forest-${q.stageId}`,
                        title: `${q.character.name}의 의뢰`, // [수정일: 2026-01-28] 맵 표시 이름 변경
                        questIndex: idx,
                        displayNum: `F-${idx + 1}`,
                        difficulty: 'medium',
                        config: q,
                        mode: 'pseudo-forest'
                    }));
                }
                else if (this.unit1Mode === 'pseudo-company') {
                    // [수정일: 2026-01-29] Pseudo Company 기초 데이터 매핑
                    return [{
                        id: 'company-1',
                        title: '기업 로직 분석',
                        questIndex: 0,
                        displayNum: 'C-1',
                        difficulty: 'hard',
                        mode: 'pseudo-company'
                    }];
                }
                else if (this.unit1Mode === 'pseudo-emergency') {
                    // [수정일: 2026-01-29] Pseudo Emergency 기초 데이터 매핑
                    return [{
                        id: 'emergency-1',
                        title: '긴급 차단 스위치',
                        questIndex: 0,
                        displayNum: 'E-1',
                        difficulty: 'hard',
                        mode: 'pseudo-emergency'
                    }];
                }
                /* [수정일: 2026-01-31] 비활성 모드 데이터 매핑 주석 처리
                else {
                    return aiDetectiveQuests.map((q, idx) => ({
                        id: q.id,
                        title: q.title,
                        level: q.level, // [수정일: 2026-01-28] App.vue 필터링을 위해 level 필드 추가
                        questIndex: idx,
                        displayNum: `DNA-${idx + 1}`,
                        difficulty: q.level === '고급' ? 'hard' : (q.level === '중급' ? 'medium' : 'easy'),
                        config: q,
                        mode: 'ai-detective'
                    }));
                }
                */
            }

            // [Unit 2] Debug Practice 처리 (Bug Hunt) - DB details 기준 단일화
            if (unitTitle.includes('debug')) {
                if (!unit.details || !Array.isArray(unit.details)) {
                    return [];
                }
                const debugProblems = unit.details
                    .filter(d => d.detail_type === 'PROBLEM' && d.is_active && d.content_data?.id)
                    .sort((a, b) => a.display_order - b.display_order);

                return debugProblems.map((d, idx) => ({
                    id: d.content_data.id, // S1, S2 ...
                    missionId: d.content_data.id,
                    title: d.content_data.stage_title || d.content_data.project_title || d.detail_title,
                    displayNum: `Stage ${idx + 1}`,
                    questIndex: idx,
                    mode: d.content_data.mode || 'standard',
                    detailId: d.id // unit02_01 ...
                }));
            }

            // [Unit 3] System Practice 처리
            if (unitTitle.includes('system')) {
                // DB details 우선 사용
                if (unit.details && Array.isArray(unit.details) && unit.details.length > 0) {
                    const dbProblems = unit.details
                        .filter(d => d.detail_type === 'PROBLEM' && d.is_active)
                        .sort((a, b) => a.display_order - b.display_order);
                    if (dbProblems.length > 0) {
                        return dbProblems.map((d, idx) => ({
                            id: d.id,
                            title: d.detail_title,
                            displayNum: `3-${idx + 1}`,
                            problemIndex: idx,
                            questIndex: idx,
                            difficulty: d.content_data?.difficulty || 'medium',
                            config: d.content_data
                        }));
                    }
                }

                // DB 데이터 없을 때 하드코딩 폴백 배열 반환
                return [
                    { id: 1, title: 'Instagram Home Feed', displayNum: '3-1', problemIndex: 0 },
                    { id: 2, title: 'YouTube VOD 업로드/스트리밍', displayNum: '3-2', problemIndex: 1 },
                    { id: 3, title: '실시간 메시징', displayNum: '3-3', problemIndex: 2 },
                    { id: 4, title: '라이드헤일링 실시간 배차', displayNum: '3-4', problemIndex: 3 },
                    { id: 5, title: '짧은 영상 추천 피드', displayNum: '3-5', problemIndex: 4 },
                    { id: 6, title: 'Drive/Dropbox 파일 저장', displayNum: '3-6', problemIndex: 5 },
                    { id: 7, title: 'Checkout 주문/결제', displayNum: '3-7', problemIndex: 6 },
                    { id: 8, title: '실시간 검색 + 트렌딩', displayNum: '3-8', problemIndex: 7 },
                    { id: 9, title: '화상회의(WebRTC)', displayNum: '3-9', problemIndex: 8 },
                    { id: 10, title: 'RTB 광고 입찰', displayNum: '3-10', problemIndex: 9 }
                ].map(p => ({ ...p, questIndex: p.problemIndex }));
            }

            // 그 외 유닛: DB 상세 데이터(PracticeDetail)를 기반으로 동적 구성
            if (!unit.details || unit.details.length === 0) {
                return [];
            }

            return unit.details
                .filter(d => d.detail_type === 'PROBLEM' && d.is_active)
                .sort((a, b) => a.display_order - b.display_order)
                .map((d, idx) => ({
                    id: d.id,
                    title: d.detail_title,
                    questIndex: idx,
                    displayNum: `${unitNum}-${idx + 1}`,
                    difficulty: d.content_data?.difficulty || 'medium',
                    config: d.content_data
                }));
        },

        unlockNextStage(unitName, index) {
            // [수정일: 2026-01-28] Unit 1의 경우 현재 활성 모드에 따라 키값 결정
            let targetKey = unitName;
            if (this.activeUnit?.name === 'Pseudo Practice') {
                const modeMap = {
                    'pseudo-practice': 'Pseudo Practice',
                    'ai-detective': 'AI Detective',
                    'pseudo-forest': 'Pseudo Forest',
                    'pseudo-company': 'Pseudo Company',
                    'pseudo-emergency': 'Pseudo Emergency'
                };
                targetKey = modeMap[this.unit1Mode] || 'Pseudo Practice';
            }
            if (this.activeUnit?.name === 'Debug Practice') {
                targetKey = 'Debug Practice';
            }

            const progress = this.unitProgress[targetKey];
            if (progress && !progress.includes(index)) {
                progress.push(index);
            }
            const nextIdx = index + 1;
            // 유닛별 최대 문제 수에 맞춰 해금 제한 동적 조절
            const maxCount = targetKey === 'AI Detective'
                ? 30
                : (this.activeUnit?.problems?.length || 0);
            if (progress && nextIdx < maxCount && !progress.includes(nextIdx)) {
                progress.push(nextIdx);
            }

            // [2026-01-26] 진행도 로컬 스토리지 저장
            localStorage.setItem('logic_mirror_progress', JSON.stringify(this.unitProgress));

            // [2026-02-23 수정] RDS에도 진행도 저장 (전용 엔드포인트 사용으로 404 방지)
            const practice = this.chapters.find(c => c.name === targetKey);
            if (practice?.id) {
                axios.post('/api/core/activity/progress/', {
                    practice_id: practice.id,
                    unlocked_nodes: progress
                }, { withCredentials: true }).catch(e => console.warn('[GameStore] RDS progress save failed:', e));
            }
        },

        setActiveUnit(unit) {
            this.activeUnit = unit;
        },

        /**
         * [사용자 해결 문제 기록 조회]
         * [수정일: 2026-02-09] 유닛별 사고 과정 및 코드 복구를 위해 해결 기록을 서버에서 가져옵니다.
         */
        async fetchUserSolvedProblems() {
            try {
                const response = await axios.get('/api/core/activity/solved-problems/', {
                    withCredentials: true
                });
                this.userSolvedProblems = response.data;
            } catch (error) {
                console.error("[GameStore] Failed to fetch solved problems:", error);
            }
        }
    },

    getters: {
        currentUnitProgress: (state) => {
            if (!state.activeUnit) return [0];

            // [수정일: 2026-01-28] Unit 1의 경우 현재 모드에 따라 진행도 키값 분기 처리
            if (state.activeUnit.name === 'Pseudo Practice') {
                const modeMap = {
                    'pseudo-practice': 'Pseudo Practice',
                    'ai-detective': 'AI Detective',
                    'pseudo-forest': 'Pseudo Forest',
                    'pseudo-company': 'Pseudo Company',
                    'pseudo-emergency': 'Pseudo Emergency'
                };
                const modeKey = modeMap[state.unit1Mode] || 'Pseudo Practice';
                return state.unitProgress[modeKey] || [0];
            }

            // [수정일: 2026-01-31] 유닛 이름을 정규화하여 진행도 키값 매칭 (대소문자/공백 무시)
            const rawTitle = state.activeUnit.name || state.activeUnit.title || '';
            const unitTitle = rawTitle.toLowerCase().replace(/\s+/g, '');

            if (unitTitle.includes('debug')) {
                return state.unitProgress['Debug Practice'] || [0];
            }

            if (unitTitle === 'systempractice') {
                return state.unitProgress['System Practice'] || [0];
            }

            return state.unitProgress[state.activeUnit.name] || [0];
        }
    }
});
