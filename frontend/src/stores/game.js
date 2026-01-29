import { defineStore } from 'pinia';
import axios from 'axios';
import { aiQuests } from '../features/practice/support/unit1/logic-mirror/data/stages.js';
import { aiDetectiveQuests } from '../features/practice/support/unit1/logic-mirror/data/aiDetectiveQuests.js';
import progressiveData from '../features/practice/progressive-problems.json';
import forestGameData from '../features/practice/PseudoForestData.js'; // [수정일: 2026-01-28] Forest 데이터 임포트

/**
 * [수정일: 2026-01-27]
 * [수정내용: DB Practice 연동과 Pseudo Practice(aiQuests) 및 Debug Practice(progressiveProblems)의 통합 병합]
 */
export const useGameStore = defineStore('game', {
    state: () => ({
        chapters: [],
        unitProgress: {
            'Pseudo Practice': [0],
            // [수정일: 2026-01-28] 난이도별(초/중/고) 첫 문제를 기본 해금하여 즉시 선택 가능하도록 설정
            'AI Detective': [0, 10, 20],
            'Debug Practice': [0],
            // [수정일: 2026-01-28] Vibe Clean Up 전용 진행도
            'Vibe Clean Up': [0],
            'System Practice': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            'Ops Practice': [0],
            'Agent Practice': [0],
            // [수정일: 2026-01-28] Pseudo Forest 전용 진행도 초기값 추가
            'Pseudo Forest': [0]
        },
        activeUnit: null,
        activeProblem: null,
        activeChapter: null,
        currentDebugMode: 'bug-hunt',
        // [수정일: 2026-01-28] Unit 1의 현재 모드 확장 (pseudo-practice | ai-detective | pseudo-forest)
        unit1Mode: 'pseudo-practice',
        selectedQuestIndex: 0,
        selectedSystemProblemIndex: 0
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
                    'System Practice': 'layers',
                    'Ops Practice': 'zap',
                    'Agent Practice': 'bot'
                };
                const imageMap = {
                    'Pseudo Practice': '/image/unit_code.png',
                    'Debug Practice': '/image/unit_debug.png',
                    'System Practice': '/image/unit_system.png',
                    'Ops Practice': '/image/unit_ops.png',
                    'Agent Practice': '/image/unit_agent.png'
                };

                // [데이터 매핑 로직] DB 필드값을 UI 카드 컴포넌트의 props 형식에 맞게 변환하여 chapters 배열 구성
                this.chapters = response.data.map((item, idx) => {
                    const problems = this.mapDetailsToProblems(item, idx + 1);
                    const isDebugPractice = item.title === 'Debug Practice';

                    return {
                    id: item.id,            // 고유 ID
                    db_id: item.id,         // DB 연동 확인용 ID
                    name: item.title,       // 화면 표시 제목
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
                    problems,
                    // [2026-01-28] Debug Practice의 Vibe Clean Up 전용 문제 세트
                    vibeProblems: isDebugPractice
                        ? (progressiveData.progressiveProblems || []).map((m, mIdx) => ({
                            id: `vibe-${m.id}`,
                            missionId: `vibe-${m.id}`,
                            title: `Vibe ${mIdx + 1} - ${m.project_title}`,
                            displayNum: `Vibe ${mIdx + 1}`,
                            questIndex: mIdx
                        }))
                        : undefined
                    };
                });

                // [2026-01-26] 로컬 스토리지에서 저장된 진행도 로드
                const savedProgress = localStorage.getItem('logic_mirror_progress');
                if (savedProgress) {
                    const parsed = JSON.parse(savedProgress);

                    // [수정일: 2026-01-28] 전체 덮어쓰기 대신 기존 초기값(state)과 '병합(Merge)' 처리
                    // 이렇게 하면 새로운 모드(Pseudo Forest 등)가 추가되어도 기존 유저의 로컬 데이터에 의해 지워지지 않습니다.
                    Object.keys(this.unitProgress).forEach(key => {
                        if (parsed[key]) {
                            // 기존 데이터가 있으면 병합 후 중복 제거
                            this.unitProgress[key] = Array.from(new Set([...this.unitProgress[key], ...parsed[key]])).sort((a, b) => a - b);
                        }
                    });

                    // [수정일: 2026-01-28] AI Detective 난이도별 시작점 보장
                    if (this.unitProgress['AI Detective']) {
                        [0, 10, 20].forEach(idx => {
                            if (!this.unitProgress['AI Detective'].includes(idx)) {
                                this.unitProgress['AI Detective'].push(idx);
                            }
                        });
                        this.unitProgress['AI Detective'].sort((a, b) => a - b);
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
            // [수정일: 2026-01-28] 필드명 유연성 확보: unit.name과 unit.title 모두 체크
            const unitTitle = unit.name || unit.title;

            // [Unit 1] Pseudo Practice 처리
            if (unitTitle === 'Pseudo Practice') {
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
            }

            // [Unit 2] Debug Practice 처리
            if (unitTitle === 'Debug Practice' && progressiveData.progressiveProblems) {
                return progressiveData.progressiveProblems.map((m, idx) => ({
                    id: m.id,
                    missionId: m.id,
                    title: m.project_title,
                    displayNum: `Campaign ${idx + 1}`,
                    questIndex: idx
                }));
            }

            // [Unit 3] System Practice 처리
            if (unitTitle === 'System Practice') {
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
                ].map(p => ({
                    ...p,
                    questIndex: p.problemIndex
                }));
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
                    'pseudo-forest': 'Pseudo Forest'
                };
                targetKey = modeMap[this.unit1Mode] || 'Pseudo Practice';
            }
            if (this.activeUnit?.name === 'Debug Practice') {
                targetKey = this.currentDebugMode === 'vibe-cleanup' ? 'Vibe Clean Up' : 'Debug Practice';
            }

            const progress = this.unitProgress[targetKey];
            if (progress && !progress.includes(index)) {
                progress.push(index);
            }
            const nextIdx = index + 1;
            // [수정일: 2026-01-28] 유닛별 최대 문제 수에 맞춰 해금 제한 동적 조절
            const maxCount = targetKey === 'AI Detective'
                ? 30
                : (targetKey === 'Debug Practice' || targetKey === 'Vibe Clean Up')
                    ? (progressiveData.progressiveProblems?.length || 0)
                    : 10;
            if (progress && nextIdx < maxCount && !progress.includes(nextIdx)) {
                progress.push(nextIdx);
            }

            // [2026-01-26] 진행도 로컬 스토리지 저장
            localStorage.setItem('logic_mirror_progress', JSON.stringify(this.unitProgress));
        },

        setActiveUnit(unit) {
            this.activeUnit = unit;
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
                    'pseudo-forest': 'Pseudo Forest'
                };
                const modeKey = modeMap[state.unit1Mode] || 'Pseudo Practice';
                return state.unitProgress[modeKey] || [0];
            }

            // [수정일: 2026-01-28] Debug Practice는 현재 디버그 모드에 따라 진행도 키값 분기 처리
            if (state.activeUnit.name === 'Debug Practice') {
                const modeKey = state.currentDebugMode === 'vibe-cleanup' ? 'Vibe Clean Up' : 'Debug Practice';
                return state.unitProgress[modeKey] || [0];
            }

            return state.unitProgress[state.activeUnit.name] || [0];
        }
    }
});
