import { defineStore } from 'pinia';
import { gameData } from '../features/practice/support/unit1/logic-mirror/data/stages.js';

/**
 * [수정일: 2026-01-24]
 * [수정내용: App.vue의 게임 진행도 및 챕터 로직을 분리한 게임 스토어]
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
        initGame() {
            const colors = ['#58cc02', '#1cb0f6', '#ff9600', '#ce82ff', '#ff4b4b'];
            const iconMap = {
                'Pseudo Practice': 'gamepad-2',
                'Debug Practice': 'bug',
                'System Practice': 'layers',
                'Ops Practice': 'zap',
                'Agent Practice': 'bot'
            };

            this.chapters = [
                { id: 1, name: 'Pseudo Practice', unitTitle: 'Algorithm 101', description: 'Strength Training', problems: [], image: '/image/unit_code.png' },
                { id: 2, name: 'Debug Practice', description: 'Precision Training', problems: [{ id: 2, title: 'Fix the Bug' }], image: '/image/unit_debug.png' },
                { id: 3, name: 'System Practice', description: 'Strategy Training', problems: [{ id: 3, title: 'Design System' }], image: '/image/unit_system.png' },
                { id: 4, name: 'Ops Practice', description: 'Endurance Training', problems: [{ id: 4, title: 'Server Down!' }], image: '/image/unit_ops.png' },
                { id: 5, name: 'Agent Practice', description: 'AI Training', problems: [{ id: 5, title: 'Prompt Eng' }], image: '/image/unit_agent.png' },
            ].map((ch, idx) => ({
                ...ch,
                color: colors[idx % colors.length],
                icon: iconMap[ch.name] || 'book'
            }));

            // Unit 1 매핑
            const pseudoIdx = this.chapters.findIndex(c => c.name === 'Pseudo Practice');
            if (pseudoIdx !== -1 && gameData.quests) {
                this.chapters[pseudoIdx].problems = gameData.quests.map((q, idx) => ({
                    id: q.id,
                    title: q.title,
                    questIndex: idx,
                    displayNum: `1-${idx + 1}`
                }));
            }
        },

        unlockNextStage(unitName, index) {
            const progress = this.unitProgress[unitName];
            if (progress && !progress.includes(index)) {
                progress.push(index);
            }
            // 다음 인덱스도 해금
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
