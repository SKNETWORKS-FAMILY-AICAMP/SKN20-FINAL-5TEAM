import { defineStore } from 'pinia';
import axios from 'axios';
import { aiQuests } from '../features/practice/pseudocode/data/stages.js'; // [?�정?? 2026-02-06] ?�더 계층??data) 반영
import { useProgressStore } from '@/stores/progress';

export const useGameStore = defineStore('game', {
    state: () => ({
        chapters: [],
        activeUnit: null,
        activeProblem: null,
        activeChapter: null,
        currentDebugMode: 'bug-hunt',
        // [?�정?? 2026-01-28] Unit 1???�재 모드 ?�장 (pseudo-practice | ai-detective | pseudo-forest | pseudo-company | pseudo-emergency)
        unit1Mode: 'pseudo-practice',
        selectedQuestIndex: 0,
        selectedSystemProblemIndex: 0,
        // [?�정?? 2026-02-09] ?�버?�서 불러???�용???�결 문제 기록 ?�??
        userSolvedProblems: []
    }),

    actions: {
        setUserRole(role) {
            this.userRole = role;
            // [버그수정] sessionStorage에도 저장 → 탭 이동/새로고침 후에도 유지
            if (role) sessionStorage.setItem('wars_user_role', role);
        },
        // [P1] 팀 점수 저장 (GrowthReport 비교용)
        setPlayerScores(scores) {
            this.lastPlayerScores = scores;
        },
        /**
         * [초기 게임 ?�이??로드]
         * - 백엔??API(/api/core/practices/)로�????�습 ?�닛 목록??가?��? ?�토?�에 ?�?�합?�다.
         * - DB?�서 가?�온 ?�이?��? ?�론?�엔??UI 컴포?�트?�서 ?�구?�는 ?�식?�로 변??Mapping)?�니??
         */
        async initGame() {
            try {
                // [2026-01-25] 백엔?�로부???�성?�된 모든 ?�습 ?�닛 목록 조회 (withCredentials: ?�션 쿠키 ?�함)
                const response = await axios.get('/api/core/practices/', {
                    withCredentials: true
                });

                // UI?�서 ?�용???�백(Fallback) 매핑 ?�이�?
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

                // [?�이??매핑 로직] DB ?�드값을 UI 카드 컴포?�트??props ?�식??맞게 변?�하??chapters 배열 구성
                this.chapters = response.data.map((item, idx) => {
                    // [?�정?? 2026-02-03] 백엔??명칭???�르?�라???�론?�엔???��? 명칭?�로 ?�규??
                    let normalizedTitle = item.title;
                    const lowerTitle = (item.title || '').toLowerCase().replace(/\s+/g, '');

                    if (lowerTitle.includes('pseudo')) normalizedTitle = 'Pseudo Practice';
                    else if (lowerTitle.includes('debug')) normalizedTitle = 'Debug Practice';
                    else if (lowerTitle.includes('system')) normalizedTitle = 'System Practice';

                    const problems = this.mapDetailsToProblems({ ...item, title: normalizedTitle }, idx + 1);
                    const isDebugPractice = normalizedTitle === 'Debug Practice';

                    return {
                        id: item.id,            // 고유 ID
                        db_id: item.id,         // DB ?�동 ?�인??ID
                        name: normalizedTitle,  // ?�면 ?�시 ?�목 (?��??�됨)
                        unitTitle: item.title,  // ?�세 모달 ?�목??
                        description: item.subtitle, // 카드 ?�단 부??
                        participant_count: item.participant_count, // ?�련 참여????
                        unit_number: item.unit_number, // ?�닛 번호 (UNIT XX)
                        level: item.level,      // 권장 ?�벨 (LV.XX)

                        // [2026-01-25] DB ?�드 ?�선 ?�용, ?�으�??�드코딩 ?�백 ?�용
                        image: item.icon_image || imageMap[item.title] || '/image/unit_code.png',
                        color: item.color_code || colors[idx % colors.length],
                        icon: item.icon_name || iconMap[item.title] || 'book',

                        // [2026-01-25] ?�드코딩 ?�거: DB??PracticeDetail 리스?�에??'PROBLEM' ?�?�만 추출?�여 문제 구성
                        problems
                    };
                });

            } catch (error) {
                console.error("Failed to fetch practice units from DB:", error);
            }
        },

        /**
         * [?�세 ?�이?��? 문제 객체�?변??
         * - [2026-01-27] ?�정: Pseudo Practice?� Debug Practice(Bug Hunt)??로컬/Progressive ?�이?��? ?�선 ?�용?�니??
         * - �??�의 ?�닛?��? 백엔??DB??PracticeDetail ?�보�?기반?�로 ?�적?�로 구성?�니??
         */
        mapDetailsToProblems(unit, unitNum) {
            // [?�정?? 2026-02-03] 명칭 ?�규?? 'pseudo'가 ?�함?�면 Pseudo Practice�?간주
            const rawTitle = unit.name || unit.title || '';
            const unitTitle = rawTitle.toLowerCase().replace(/\s+/g, '');

            // [Unit 1] Pseudo Practice 처리
            if (unitTitle.includes('pseudo')) {
                // unit1Mode???�라 ?�로 ?�른 문제 ?�트 매핑 �?반환
                if (this.unit1Mode === 'pseudo-practice') {
                    // [?�정?? 2026-02-24] DB(content_data)�??�전???��????�이?��? 로딩?�도�?변�?
                    if (unit.details && Array.isArray(unit.details) && unit.details.length > 0) {
                        return unit.details
                            .filter(d => d.detail_type === 'PROBLEM' && d.is_active)
                            .sort((a, b) => a.display_order - b.display_order)
                            .map((d, idx) => {
                                const q = d.content_data || {};
                                return {
                                    id: q.id || d.id,
                                    dbDetailId: d.id, // unit01_01 ??DB PK 기록
                                    title: q.title || d.detail_title,
                                    questIndex: idx,
                                    displayNum: `${unitNum}-${idx + 1}`,
                                    difficulty: q.level > 3 ? 'hard' : (q.level > 1 ? 'medium' : 'easy'),
                                    config: q,
                                    mode: 'pseudo-practice'
                                };
                            });
                    }

                    // 만약 DB ?�동 ?�패 ??Fallback
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
                    // [?�정?? 2026-01-28] Pseudo Forest ?�규 10?�계 ?�이??매핑
                    return forestGameData.map((q, idx) => ({
                        id: `forest-${q.stageId}`,
                        title: `${q.character.name}???�뢰`, // [?�정?? 2026-01-28] �??�시 ?�름 변�?
                        questIndex: idx,
                        displayNum: `F-${idx + 1}`,
                        difficulty: 'medium',
                        config: q,
                        mode: 'pseudo-forest'
                    }));
                }
                else if (this.unit1Mode === 'pseudo-company') {
                    // [?�정?? 2026-01-29] Pseudo Company 기초 ?�이??매핑
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
                    // [?�정?? 2026-01-29] Pseudo Emergency 기초 ?�이??매핑
                    return [{
                        id: 'emergency-1',
                        title: '긴급 차단 스위치',
                        questIndex: 0,
                        displayNum: 'E-1',
                        difficulty: 'hard',
                        mode: 'pseudo-emergency'
                    }];
                }
                /* [?�정?? 2026-01-31] 비활??모드 ?�이??매핑 주석 처리
                else {
                    return aiDetectiveQuests.map((q, idx) => ({
                        id: q.id,
                        title: q.title,
                        level: q.level, // [?�정?? 2026-01-28] App.vue ?�터링을 ?�해 level ?�드 추�?
                        questIndex: idx,
                        displayNum: `DNA-${idx + 1}`,
                        difficulty: q.level === '고급' ? 'hard' : (q.level === '중급' ? 'medium' : 'easy'),
                        config: q,
                        mode: 'ai-detective'
                    }));
                }
                */
            }

            // [Unit 2] Debug Practice 처리 (Bug Hunt) - DB details 기�? ?�일??
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
                // DB details ?�선 ?�용
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

                // DB ?�이???�을 ???�드코딩 ?�백 배열 반환
                return [
                    { id: 1, title: 'Instagram Home Feed', displayNum: '3-1', problemIndex: 0 },
                    { id: 2, title: 'YouTube VOD ?�로???�트리밍', displayNum: '3-2', problemIndex: 1 },
                    { id: 3, title: '실시간 메시징', displayNum: '3-3', problemIndex: 2 },
                    { id: 4, title: '?�이?�헤?�링 ?�시�?배차', displayNum: '3-4', problemIndex: 3 },
                    { id: 5, title: '짧�? ?�상 추천 ?�드', displayNum: '3-5', problemIndex: 4 },
                    { id: 6, title: 'Drive/Dropbox 파일 저장', displayNum: '3-6', problemIndex: 5 },
                    { id: 7, title: 'Checkout 주문/결제', displayNum: '3-7', problemIndex: 6 },
                    { id: 8, title: '실시간 검색 + 트렌딩', displayNum: '3-8', problemIndex: 7 },
                    { id: 9, title: '?�상?�의(WebRTC)', displayNum: '3-9', problemIndex: 8 },
                    { id: 10, title: 'RTB 광고 ?�찰', displayNum: '3-10', problemIndex: 9 }
                ].map(p => ({ ...p, questIndex: p.problemIndex }));
            }

            // �????�닛: DB ?�세 ?�이??PracticeDetail)�?기반?�로 ?�적 구성
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

        async unlockNextStage(unitName, index) {
            // [?�정?? 2026-02-24] Progress ?�토???�동?�로 ?�전???��?
            const { useProgressStore } = await import('@/stores/progress');
            const progressStore = useProgressStore();

            // 기존 ?�백 매핑
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

            const practice = this.chapters.find(c => c.name === targetKey);

            // maxCount 판별
            const maxCount = targetKey === 'AI Detective'
                ? 30
                : (practice?.problems?.length || this.activeUnit?.problems?.length || 10);

            // progressStore 측의 action 호출 (index, 추가로 다음 노드까지 해금 시도)
            if (practice?.id) {
                await progressStore.unlockNode(practice.id, index);

                const nextIdx = index + 1;
                if (nextIdx < maxCount) {
                    await progressStore.unlockNode(practice.id, nextIdx);
                }
            } else {
                console.warn('[GameStore] Practice ID not found for unlock', targetKey);
            }
        },

        setActiveUnit(unit) {
            this.activeUnit = unit;
        },

        /**
         * [?�용???�결 문제 기록 조회]
         * [?�정?? 2026-02-09] ?�닛�??�고 과정 �?코드 복구�??�해 ?�결 기록???�버?�서 가?�옵?�다.
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
        },

        /**
         * [수정일: 2026-02-23] Job Planner 분석 결과 저장
         * - Coduck Wars 섹션에서 '불러오기' 기능을 제공하기 위해 데이터를 저장합니다.
         */
        setLastParsedJob(jobData) {
            this.lastParsedJob = jobData;
        },

        /**
         * [수정일: 2026-02-23] Coduck Wars 활성 미션 데이터 저장
         */
        setWarsMission(mission) {
            this.activeWarsMission = mission;
            if (mission) {
                sessionStorage.setItem('active_wars_mission', JSON.stringify(mission));
            } else {
                sessionStorage.removeItem('active_wars_mission');
            }
        },

        /**
         * [수정일: 2026-02-23] Coduck Wars 평가 결과 저장
         */
        setEvaluation(evaluation, finalDesign) {
            this.lastEvaluation = evaluation;
            this.lastFinalDesign = finalDesign;
        },

        /**
         * [수정일: 2026-02-23] 게임 점수 계산 (4개 비율점수 + 속도 보너스)
         * @param {object} scores - { availability, scalability, security, cost_efficiency } (0~100)
         * @param {number} submitTimeSeconds - 제출 시점 관당 시간(초), 빠를수록 미제출
         * @param {number} totalSeconds - 방 전체 제한 시간(초), 기본값 600
         * @returns {number} 최종 점수 (0~100)
         */
        calculateGameScore(scores, submitTimeSeconds = 0, totalSeconds = 600) {
            if (!scores) return 0;

            // 기본 점수: 네 항목 가중 평균
            const weights = {
                availability: 0.35,  // 가용성 중요
                scalability: 0.30,  // 확장성
                security: 0.20,  // 보안
                cost_efficiency: 0.15   // 비용효율
            };
            const baseScore =
                (scores.availability || 0) * weights.availability +
                (scores.scalability || 0) * weights.scalability +
                (scores.security || 0) * weights.security +
                (scores.cost_efficiency || 0) * weights.cost_efficiency;

            // 속도 보너스: 전체 시간 50% 이내에 제출하면 +5점, 25% 이내면 +10점
            let speedBonus = 0;
            if (submitTimeSeconds > 0 && totalSeconds > 0) {
                const ratio = submitTimeSeconds / totalSeconds;
                if (ratio <= 0.25) speedBonus = 10;
                else if (ratio <= 0.50) speedBonus = 5;
            }

            return Math.min(100, Math.round(baseScore + speedBonus));
        },

        /**
         * [수정일: 2026-02-23] 3인 팀 점수 합산 및 등급 반환
         * @param {number[]} playerScores - 각 플레이어 점수 배열 [p1, p2, p3]
         * @returns {{ total: number, average: number, grade: string }}
         */
        calcTeamResult(playerScores = []) {
            if (!playerScores.length) return { total: 0, average: 0, grade: 'C' };
            const total = playerScores.reduce((a, b) => a + b, 0);
            const average = Math.round(total / playerScores.length);
            let grade = 'C';
            if (average >= 90) grade = 'S';
            else if (average >= 75) grade = 'A';
            else if (average >= 60) grade = 'B';
            return { total, average, grade };
        }
    },

    getters: {
        currentUnitProgress: (state) => {
            if (!state.activeUnit) return [0];

            // [수정일: 2026-02-24] Pinia 크로스스토어 getter-with-arguments 반응성 이슈 해결
            // - getUnlockedNodes(id) 패턴은 내부 함수 호출 시 Vue 반응성 추적이 누락될 수 있음
            // - unitProgresses 배열을 직접 참조하여 Vue가 확실히 의존성을 추적하도록 변경
            const progressStore = useProgressStore();
            const progresses = progressStore.unitProgresses; // 배열 참조를 직접 추적
            const entry = progresses.find(p => p.unit_id === state.activeUnit.id);
            return entry ? entry.unlocked_nodes : [0];
        }
    }
});
