import { ref, reactive, computed } from 'vue';
import axios from 'axios';
import { checkConsistency } from '../api/pseudocodeApi.js';

export function useCodeRunner(gameState, currentMission, addSystemLog, setPhase) {

    // --- State ---
    const runnerState = reactive({
        userCode: "",
        codeSlots: null,
        executionResult: null
    });

    // [2026-02-09] Task 1.1: 에러 타입 분류 함수 (인프라 에러 vs 사용자 에러)
    const classifyError = (error) => {
        // 네트워크 에러 (서버 응답 없음)
        if (!error.response) {
            return {
                type: 'NETWORK_ERROR',
                shouldPenalize: false,
                userMessage: '네트워크 연결을 확인해주세요. 잠시 후 다시 시도해주세요.',
                logMessage: '네트워크 장애 감지 - 사용자 패널티 없음'
            };
        }

        const status = error.response.status;

        // 서버 내부 오류 (500번대)
        if (status >= 500) {
            return {
                type: 'SERVER_ERROR',
                shouldPenalize: false,
                userMessage: '시스템 재접속 중... 잠시 후 다시 시도해주세요.',
                logMessage: '서버 인프라 오류 감지 - 사용자 패널티 없음'
            };
        }

        // 사용자 입력 오류 (400번대)
        if (status >= 400 && status < 500) {
            return {
                type: 'USER_ERROR',
                shouldPenalize: true,
                userMessage: '코드 검증 실패',
                logMessage: '사용자 입력 오류'
            };
        }

        // 기타 에러
        return {
            type: 'UNKNOWN_ERROR',
            shouldPenalize: false,
            userMessage: '알 수 없는 오류가 발생했습니다.',
            logMessage: '미분류 에러'
        };
    };

    // --- Initialization ---
    const initPhase4Scaffolding = () => {
        console.log("[CodeRunner] initPhase4Scaffolding executed. Resetting state...");
        runnerState.codeSlots = {
            slot1: { placeholder: "::: [SYSTEM SLOT 01: READY] :::", content: null },
            slot2: { placeholder: "::: [SYSTEM SLOT 02: READY] :::", content: null },
            slot3: { placeholder: "::: [SYSTEM SLOT 03: READY] :::", content: null },
            slot4: { placeholder: "::: [SYSTEM SLOT 04: READY] :::", content: null },
        };
        runnerState.executionResult = null;

        // 템플릿 로드
        console.log("[CodeRunner] Current Mission:", currentMission.value?.id);
        const template = currentMission.value?.implementation?.codeFrame?.template;
        console.log("[CodeRunner] Template:", template);

        if (template) {
            runnerState.userCode = template;
            console.log("[CodeRunner] Set runnerState.userCode to template. Current value:", runnerState.userCode);
        } else {
            console.log("[CodeRunner] Template NOT FOUND. UserCode not reset.");
        }

        addSystemLog("모듈 슬롯 대기 모드 활성화", "INFO");
    };

    // --- Actions ---
    const insertSnippet = () => {
        gameState.feedbackMessage = "모듈을 마우스로 끌어서(Drag) 배치하십시오.";
        addSystemLog("안내: 클릭 대신 드래그 앤 드롭을 사용하세요.", "WARN");
    };

    const handleSlotDrop = (slotKey, snippetCode) => {
        if (runnerState.codeSlots[slotKey]) {
            runnerState.codeSlots[slotKey].content = snippetCode;
            addSystemLog(`슬롯[${slotKey}] 모듈 장착: ${snippetCode}`, "SUCCESS");
        }
    };

    const submitPythonFill = async (phase3Reasoning, handleDamage) => {
        const userCode = runnerState.userCode;

        gameState.feedbackMessage = "코드 실행 중...";
        gameState.feedbackMessage = "코드 실행 중...";
        addSystemLog(`백엔드로 코드 전송 중... (Length: ${userCode.length})`, "INFO");
        console.log("[CodeRunner] Submitting code:", userCode);

        try {
            console.log("[DEBUG] submitPythonFill: Requesting execution...");

            // [Security Update] Timeout reduced to use backend's 5s limit effectively
            const response = await axios.post('/api/core/pseudocode/execute/', {
                code: userCode,
                test_cases: currentMission.value.testCases || [],
                function_name: 'leakage_free_scaling'
            }, { timeout: 10000 }); // Frontend timeout slightly larger than backend (5s)

            runnerState.executionResult = response.data;

            // 1. 실행 및 테스트 성공
            if (response.data.success && response.data.all_passed) {
                gameState.score += 200;
                gameState.feedbackMessage = "구현 무결성 확인!";
                addSystemLog(`코드 검증 통과: 모든 테스트 통과 (${response.data.passed_count}/${response.data.total_count})`, "SUCCESS");

                // 정합성 체크
                try {
                    const consistency = await checkConsistency(
                        phase3Reasoning,
                        userCode,
                        'dataLeakage'
                    );

                    if (consistency.score >= 80) {
                        gameState.score += 50;
                        addSystemLog("정합성 체크: 의사코드와 구현 일치", "SUCCESS");
                    } else {
                        addSystemLog(`정합성 경고: ${consistency.gaps.join(', ')}`, "WARN");
                    }
                } catch (err) {
                    console.error('Consistency check error:', err);
                }

                setTimeout(() => setPhase('DEEP_QUIZ'), 1500);
            }
            // 2. 테스트 실패 (실행은 됐으나 정답이 아님)
            else if (response.data.success && !response.data.all_passed) {
                handleDamage();
                const failedTest = response.data.results.find(r => !r.passed);

                if (failedTest?.message?.includes("not defined")) {
                    gameState.feedbackMessage = "변수 정의가 누락되었습니다. (예: scaler = ...)";
                } else {
                    gameState.feedbackMessage = `검증 실패: ${failedTest?.message || '결과 불일치'}`;
                }

                if (failedTest) {
                    addSystemLog(`테스트 실패: ${failedTest.description}`, "ERROR");
                    addSystemLog(`메시지: ${failedTest.message}`, "INFO");
                }
            }
            // 3. 실행 자체 실패 (보안 위반 등)
            else {
                handleDamage();

                // 보안 위반 메시지 처리
                if (response.data.error && response.data.error.includes("보안 위반")) {
                    gameState.feedbackMessage = "보안 프로토콜 위반: 허용되지 않은 모듈 감지";
                    addSystemLog(`CRITICAL: ${response.data.error}`, "ERROR");
                } else {
                    // Fallback using Keyword Check (Local validation)
                    fallbackValidation(userCode, handleDamage, setPhase);
                }
            }
        } catch (error) {
            console.error('[CodeRunner] Execution error:', error);

            // [2026-02-09] Task 1.1: 에러 타입 분류 적용
            const errorInfo = classifyError(error);

            gameState.feedbackMessage = errorInfo.userMessage;
            addSystemLog(errorInfo.logMessage, errorInfo.shouldPenalize ? "ERROR" : "WARN");

            // 인프라 에러는 HP 차감 없음, 사용자 에러만 패널티
            if (errorInfo.shouldPenalize) {
                // 사용자 코드 문제 - fallback 검증 시도
                fallbackValidation(userCode, handleDamage, setPhase);
            } else {
                // 인프라 문제 - HP 차감 없이 안내만
                console.warn(`[Infrastructure Error] ${errorInfo.type}:`, error);
            }
        }
    };

    const fallbackValidation = (code, handleDamage, setPhase) => {
        if (!currentMission.value || !currentMission.value.implementation) {
            gameState.feedbackMessage = "미션 데이터를 불러올 수 없습니다.";
            return;
        }

        const validation = currentMission.value.implementation.codeValidation;
        const normalizedCode = code.replace(/\s+/g, '');
        const missingKeywords = validation.mustContain.filter(keyword => {
            const normalizedKeyword = keyword.replace(/\s+/g, '');
            return !normalizedCode.includes(normalizedKeyword);
        });
        const containsForbidden = validation.mustNotContain.some(keyword => {
            const normalizedKeyword = keyword.replace(/\s+/g, '');
            return normalizedCode.includes(normalizedKeyword);
        });

        if (missingKeywords.length === 0 && !containsForbidden) {
            gameState.score += 100;
            gameState.feedbackMessage = "네트워크 지연 - 로컬 아키텍처 분석으로 승인";
            addSystemLog("⚠️ 서버 응답 없음: 로컬 검증 모드로 전환하여 승인", "WARN");
            setTimeout(() => setPhase('DEEP_QUIZ'), 1000);
        } else {
            handleDamage();
            const reason = missingKeywords.length > 0
                ? `구조적 결함 감지: ${missingKeywords.join(", ")} 로직 누락`
                : "보안 위반: 금지된 패턴이 포함되었습니다.";
            gameState.feedbackMessage = reason + " (오프라인 모드)";
            addSystemLog(`오류: ${reason}`, "ERROR");
        }
    };

    return {
        runnerState,
        initPhase4Scaffolding,
        insertSnippet,
        handleSlotDrop,
        submitPythonFill
    };
}
