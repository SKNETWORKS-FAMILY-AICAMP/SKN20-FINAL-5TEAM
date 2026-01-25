import { defineStore } from 'pinia';
import axios from 'axios';

/**
 * [수정일: 2026-01-25]
 * [수정내용: 사용자의 요청에 따라 'Practice' 테이블을 중심으로 하드코딩 제거 및 상세 데이터(PracticeDetail) 동적 연동]
 */
export const useGameStore = defineStore('game', {
    state: () => ({
        chapters: [],
        unitProgress: {
            'Pseudo Practice': [0],
            'Debug Practice': [0],
            'System Practice': [0],
            'Ops Practice': [0],
            'Agent Practice': [0]
        },
        activeUnit: null,
        activeProblem: null,
        activeChapter: null,
        currentDebugMode: 'bug-hunt',
        selectedQuestIndex: 0
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
                this.chapters = response.data.map((item, idx) => ({
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
                    problems: this.mapDetailsToProblems(item, idx + 1)
                }));

            } catch (error) {
                console.error("Failed to fetch practice units from DB:", error);
            }
        },

        /**
         * [상세 데이터를 문제 객체로 변환]
         * - [2026-01-25] 수정: 'Pseudo Practice'는 기존의 풍부한 stages.js 데이터를 그대로 유지하기 위해 정적 데이터를 우선 사용합니다.
         * - 그 외의 유닛들은 백엔드 DB의 PracticeDetail 정보를 기반으로 동적으로 구성됩니다.
         */
        mapDetailsToProblems(unit, unitNum) {
            // DB 상세 데이터가 없으면 빈 배열 반환
            if (!unit.details || unit.details.length === 0) {
                return [];
            }

            // DB에서 가져온 'PROBLEM' 타입의 상세 데이터를 필터링 및 정렬
            return unit.details
                .filter(d => d.detail_type === 'PROBLEM' && d.is_active)
                .sort((a, b) => a.display_order - b.display_order)
                .map((d, idx) => ({
                    id: d.id,
                    title: d.detail_title,
                    questIndex: idx,
                    displayNum: `${unitNum}-${idx + 1}`,
                    difficulty: d.content_data?.difficulty || 'medium', // 난이도 필드 매핑
                    config: d.content_data
                }));
        },

        unlockNextStage(unitName, index) {
            const progress = this.unitProgress[unitName];
            if (progress && !progress.includes(index)) {
                progress.push(index);
            }
            const nextIdx = index + 1;
            if (progress && nextIdx < 10 && !progress.includes(nextIdx)) {
                progress.push(nextIdx);
            }
        },

        setActiveUnit(unit) {
            this.activeUnit = unit;
        }
    },

    getters: {
        currentUnitProgress: (state) => {
            if (!state.activeUnit) return [0];
            return state.unitProgress[state.activeUnit.name] || [0];
        }
    }
});
