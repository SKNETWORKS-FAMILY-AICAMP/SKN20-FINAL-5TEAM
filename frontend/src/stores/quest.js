/**
 * [수정일: 2026-01-23]
 * [수정내용: 일상 논리 팩토리(Everyday Logic Factory)를 위한 퀘스트 스토어 구현]
 */
import { defineStore } from 'pinia';
import questsData from '../data/quests.json';

export const useQuestStore = defineStore('quest', {
    state: () => ({
        // 로드된 전체 퀘스트 목록
        quests: questsData,
        // 현재 진행 중인 퀘스트
        currentQuest: null,
        loading: false,
        error: null
    }),

    actions: {
        /**
         * 난이도(LV1~3)에 맞는 퀘스트를 로드합니다.
         * @param {number} difficulty - 난이도 레벨 (1, 2, 3)
         */
        getQuestsByDifficulty(difficulty) {
            const levelQuests = this.quests.filter(q => q.difficulty === parseInt(difficulty));
            if (levelQuests.length > 0) {
                // 해당 난이도의 첫 번째 퀘스트를 기본으로 설정
                this.currentQuest = levelQuests[0];
            } else {
                this.error = `난이도 ${difficulty}의 퀘스트를 찾을 수 없습니다.`;
            }
        },

        /**
         * 특정 ID의 퀘스트를 설정합니다.
         */
        setQuestById(id) {
            const quest = this.quests.find(q => q.id === id);
            if (quest) {
                this.currentQuest = quest;
            }
        },

        /**
         * [Stage 1: 파슨스 퍼즐]용 블록 셔플 로직
         * 퀘스트의 blocks를 가져와 순서를 무작위로 섞습니다.
         * @returns {Array} 셔플된 블록 리스트
         */
        shuffleBlocks() {
            if (!this.currentQuest || !this.currentQuest.blocks) return [];

            // 원본 데이터 보호를 위해 복사본 생성 후 셔플
            let blocks = this.currentQuest.blocks.map((block, index) => ({
                ...block,
                originalIndex: index // 정답 확인을 위한 원본 인덱스 저장
            }));

            // Fisher-Yates Shuffle
            for (let i = blocks.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [blocks[i], blocks[j]] = [blocks[j], blocks[i]];
            }

            return blocks;
        },

        /**
         * 퍼즐 정답 여부 검증 (순서 + 들여쓰기 정밀 비교)
         */
        validatePuzzle(userBlocks) {
            if (this.currentQuest?.judgement_criteria?.block_solution) {
                const solution = this.currentQuest.judgement_criteria.block_solution;
                if (userBlocks.length !== solution.length) return false;

                return userBlocks.every((block, index) => {
                    return block.id === solution[index].id &&
                        parseInt(block.indent) === parseInt(solution[index].indent);
                });
            }

            // 폴백: 이전 방식 (단순 원본 인덱스 비교)
            return userBlocks.every((block, index) => block.originalIndex === index);
        }
    },

    getters: {
        totalQuests: (state) => state.quests.length
    }
});
