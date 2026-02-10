import { reactive, computed } from 'vue';
import { aiQuests } from '../data/stages.js';
import { useGameStore } from '@/stores/game';

export function useGameEngine() {
    const gameStore = useGameStore();

    // [수정일: 2026-02-08] 맵에서 선택한 문제를 표시하기 위해 gameStore.selectedQuestIndex 사용
    const initialStageId = (gameStore.selectedQuestIndex || 0) + 1;

    // --- Game State ---
    const gameState = reactive({
        currentStageId: initialStageId,
        // Phases: DIAGNOSTIC_1 -> DIAGNOSTIC_2 -> PSEUDO_WRITE -> PYTHON_FILL -> DEEP_QUIZ -> EVALUATION
        phase: 'DIAGNOSTIC_1',
        playerHP: 100,
        score: 0,
        combo: 0,

        // State for Decisions
        selectedStrategyLabel: "", // Set in Phase 2
        // Phase 3 State
            phase3Reasoning: "",
            phase3Score: 0,
            phase3Feedback: "",
            phase3EvaluationResult: null,
            showHint: false,
        // Interactive Messages
        coduckMessage: "경고! 접근하는 모든 데이터는 적입니다!",
        feedbackMessage: null,

        // System Logs
        systemLogs: [
            { time: "10:42:01", type: "WARN", message: "7번 구역에서 인지 부조화 감지됨." },
            { time: "10:42:05", type: "INFO", message: "아키텍트의 개입을 대기 중..." },
            { time: "10:42:09", type: "READY", message: "의사결정 입력 대기 중_" }
        ]
    });

    // --- Logging System ---
    const getTimestamp = () => {
        const now = new Date();
        return now.toTimeString().split(' ')[0]; // HH:MM:SS
    };

    const addSystemLog = (message, type = "INFO") => {
        if (gameState.systemLogs.length > 5) {
            gameState.systemLogs.shift();
        }
        gameState.systemLogs.push({
            time: getTimestamp(),
            type,
            message
        });
    };

    // --- Mission Data ---
    const currentMission = computed(() => {
        if (!aiQuests || aiQuests.length === 0) return {};
        return aiQuests.find(q => q.id === gameState.currentStageId) || aiQuests[0];
    });

    const missionContext = computed(() => {
        const mission = currentMission.value;
        return mission.designContext?.currentIncident || "미션 정보를 불러오는 중입니다.";
    });

    const constraints = computed(() => {
        const mission = currentMission.value;
        return mission.designContext?.engineeringRules || [];
    });

    // Threat Info
    const enemyThreat = computed(() => {
        const mission = currentMission.value;
        return {
            name: mission.category || "Unknown Anomaly",
            description: mission.missionObjective || "No Objective",
            hp: 100
        };
    });

    // --- Phase Management ---
    const setPhase = (newPhase) => {
        console.log(`[GameEngine] Transitioning to phase: ${newPhase}`);
        gameState.phase = newPhase;
        gameState.feedbackMessage = null;

        try {
            switch (newPhase) {
                case 'DIAGNOSTIC_1':
                    gameState.coduckMessage = "이 선택은 이후 모든 판단에 영향을 줍니다.";
                    addSystemLog("진단 프로토콜 1단계 개시", "INFO");
                    break;
                case 'DIAGNOSTIC_2':
                    gameState.coduckMessage = "무엇을 신뢰할지 결정해야 합니다.";
                    addSystemLog("진단 프로토콜 2단계 진입", "INFO");
                    break;
                case 'PSEUDO_WRITE':
                    gameState.coduckMessage = "어떤 순서로 생각하는지 보여주세요.";
                    addSystemLog("자연어 처리 에디터 로드됨", "SUCCESS");
                    break;
                case 'PYTHON_FILL':
                    gameState.coduckMessage = "사고와 코드가 일치하는지 확인하십시오.";
                    addSystemLog("구현 환경 동기화 완료", "SUCCESS");
                    break;
                case 'DEEP_QUIZ':
                    gameState.coduckMessage = "설명할 수 있다면, 이해한 것입니다.";
                    addSystemLog("최종 검증 프로세스 시작", "WARN");
                    break;
                case 'EVALUATION':
                    gameState.coduckMessage = "평가가 완료되었습니다.";
                    addSystemLog("미션 리포트 생성 중...", "INFO");
                    break;
            }
        } catch (e) {
            console.error("[GameEngine] Error in setPhase:", e);
            addSystemLog("단계 전환 중 오류 발생", "ERROR");
        }
    };

    // --- Game Logic ---
    const handleDamage = (amount = 15) => {
        gameState.playerHP -= amount;
        addSystemLog(`시스템 손상: HP -${amount} (현재: ${gameState.playerHP}%)`, "WARN");
        if (gameState.playerHP <= 0) {
            gameState.phase = 'DEFEAT';
            addSystemLog("CRITICAL: 시스템 무결성 붕괴", "ERROR");
        }
    };

    const nextMission = () => {
        const nextId = gameState.currentStageId + 1;
        const nextQuest = aiQuests.find(q => q.id === nextId);
        if (nextQuest) {
            gameState.currentStageId = nextId;
            setPhase('DIAGNOSTIC_1');
        } else {
            gameState.phase = 'CAMPAIGN_END';
        }
    };

    const restartMission = () => {
        addSystemLog("시스템 재부팅 시퀀스 초기화...", "WARN");
        gameState.playerHP = 100;
        setPhase('DIAGNOSTIC_1');
    };

    const startGame = () => {
        gameState.currentStageId = 1;
        gameState.score = 0;
        gameState.playerHP = 100;
        gameState.systemLogs = [];
        addSystemLog("시스템 부팅... 초기화 완료.", "READY");
        setPhase('DIAGNOSTIC_1');
    };

    // 맵에서 단계 선택
    const selectStage = (stageId) => {
        const targetQuest = aiQuests.find(q => q.id === stageId);
        if (!targetQuest) return;

        gameState.currentStageId = stageId;
        gameState.playerHP = 100;
        gameState.score = 0;
        gameState.systemLogs = [];
        addSystemLog(`스테이지 ${stageId}: ${targetQuest.title} 시작`, "INFO");
        setPhase('DIAGNOSTIC_1');
    };

    return {
        gameState,
        currentMission,
        missionContext,
        constraints,
        enemyThreat,

        addSystemLog,
        setPhase,
        handleDamage,
        nextMission,
        restartMission,
        startGame,
        selectStage
    };
}
