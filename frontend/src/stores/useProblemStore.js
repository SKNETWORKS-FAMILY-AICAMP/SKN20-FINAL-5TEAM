/**
 * [수정일: 2026-01-23]
 * [수정내용: 문제 데이터를 관리하기 위한 전역 상태 스토어 구현]
 * 
 * Pinia를 사용하여 애플리케이션 전역에서 문제 목록을 로드하고, 
 * 현재 선택된 문제를 추적하며, 문제 간 이동 로직을 관리합니다.
 */
import { defineStore } from 'pinia';
import problemsData from '../data/problems.json';

export const useProblemStore = defineStore('problem', {
    state: () => ({
        // 로드된 전체 문제 목록
        problems: problemsData,
        // 현재 선택된 문제 (상세 정보 포함)
        currentProblem: null,
        // 로딩 상태 태그
        loading: false,
        // 발생한 에러 기록
        error: null
    }),

    actions: {
        /**
         * ID를 사용하여 특정 문제를 글로벌 상태로 설정합니다.
         * @param {number|string} id - 문제 식별자
         */
        setProblemById(id) {
            const problem = this.problems.find(p => p.id === parseInt(id));
            if (problem) {
                this.currentProblem = problem;
                this.error = null;
            } else {
                this.error = '문제를 찾을 수 없습니다.';
            }
        },

        /**
         * 목록상 다음 순번의 문제로 데이터 상태를 전이합니다.
         */
        nextProblem() {
            if (!this.currentProblem) return;
            const currentIndex = this.problems.findIndex(p => p.id === this.currentProblem.id);
            if (currentIndex < this.problems.length - 1) {
                this.currentProblem = this.problems[currentIndex + 1];
            }
        },

        /**
         * [수정일: 2026-01-23]
         * [수정내용: Phase 2 블록 맞추기를 위한 의사코드 셔플 로직]
         * 현재 문제의 의사코드를 라인 단위로 쪼개고 순서를 섞습니다.
         * @returns {Array} 셔플된 블록 리스트
         */
        shufflePseudocode() {
            if (!this.currentProblem || !this.currentProblem.pseudocode) return [];

            // 마크다운 백틱 제거 및 줄바꿈 분리
            const rawText = this.currentProblem.pseudocode.replace(/```[a-z]*\n|```/g, '').trim();
            const lines = rawText.split('\n').filter(line => line.trim() !== '');

            // 각 라인에 메타데이터 부여
            let blocks = lines.map((text, index) => ({
                id: `block-${index}`,
                text: text,
                originalIndex: index
            }));

            // Fisher-Yates Shuffle 알고리즘
            for (let i = blocks.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [blocks[i], blocks[j]] = [blocks[j], blocks[i]];
            }

            return blocks;
        },

        /**
         * [수정일: 2026-01-23]
         * [수정내용: 퍼즐 정답 여부 검증]
         * @param {Array} userBlocks - 사용자가 정렬한 블록 배열
         * @returns {boolean} 정답 여부
         */
        validatePuzzle(userBlocks) {
            return userBlocks.every((block, index) => block.originalIndex === index);
        }
    },

    getters: {
        /**
         * 등록된 전체 문제 개수 반환
         */
        totalProblems: (state) => state.problems.length
    }
});
