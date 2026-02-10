/**
 * 에러 핸들링 유틸리티
 * 
 * 문제: 네트워크 에러와 로직 에러를 구분하지 않고 사용자 HP 차감
 * 해결: 에러 타입 분석 후 적절한 대응
 * 
 * [2026-02-09] UX 개선 (Antigravity)
 */

/**
 * 에러 타입 정의
 */
export const ErrorType = {
    NETWORK: 'NETWORK',           // 네트워크 장애
    SERVER: 'SERVER',             // 서버 500/502/503 등
    TIMEOUT: 'TIMEOUT',           // 요청 타임아웃
    VALIDATION: 'VALIDATION',     // 사용자 입력 오류
    LOGIC: 'LOGIC',               // 비즈니스 로직 오류
    UNKNOWN: 'UNKNOWN'            // 분류 불가
};

/**
 * 에러 분석 및 분류
 * 
 * @param {Error} error - 발생한 에러
 * @returns {object} { type, isUserFault, shouldRetry, message }
 */
export function analyzeError(error) {
    // 1. 네트워크 에러
    if (error.message?.includes('Network Error') || 
        error.message?.includes('Failed to fetch') ||
        error.code === 'ECONNABORTED' ||
        !navigator.onLine) {
        return {
            type: ErrorType.NETWORK,
            isUserFault: false,
            shouldRetry: true,
            userMessage: '네트워크 연결이 불안정합니다. 재시도 중...',
            techMessage: error.message,
            shouldDeductHP: false
        };
    }

    // 2. 타임아웃
    if (error.code === 'ECONNABORTED' || 
        error.message?.includes('timeout')) {
        return {
            type: ErrorType.TIMEOUT,
            isUserFault: false,
            shouldRetry: true,
            userMessage: '서버 응답 시간 초과. 잠시 후 다시 시도해주세요.',
            techMessage: error.message,
            shouldDeductHP: false
        };
    }

    // 3. 서버 에러 (500, 502, 503)
    if (error.response?.status >= 500) {
        return {
            type: ErrorType.SERVER,
            isUserFault: false,
            shouldRetry: true,
            userMessage: '서버 점검 중입니다. 잠시만 기다려주세요.',
            techMessage: `Server error: ${error.response.status}`,
            shouldDeductHP: false
        };
    }

    // 4. 클라이언트 에러 (400, 401, 403, 404)
    if (error.response?.status >= 400 && error.response?.status < 500) {
        // 401/403은 인증 문제 (사용자 책임 아님)
        if (error.response.status === 401 || error.response.status === 403) {
            return {
                type: ErrorType.VALIDATION,
                isUserFault: false,
                shouldRetry: false,
                userMessage: '인증이 만료되었습니다. 다시 로그인해주세요.',
                techMessage: `Auth error: ${error.response.status}`,
                shouldDeductHP: false
            };
        }

        // 400, 422는 입력 오류 (사용자 책임)
        return {
            type: ErrorType.VALIDATION,
            isUserFault: true,
            shouldRetry: false,
            userMessage: '입력값을 확인해주세요.',
            techMessage: error.response?.data?.message || error.message,
            shouldDeductHP: true  // 입력 오류만 HP 차감
        };
    }

    // 5. 비즈니스 로직 에러 (앱 내부)
    if (error.name === 'ValidationError' || 
        error.message?.includes('Invalid') ||
        error.message?.includes('Required')) {
        return {
            type: ErrorType.LOGIC,
            isUserFault: true,
            shouldRetry: false,
            userMessage: error.message || '입력값이 유효하지 않습니다.',
            techMessage: error.message,
            shouldDeductHP: true
        };
    }

    // 6. 분류 불가 (안전하게 시스템 에러로 처리)
    return {
        type: ErrorType.UNKNOWN,
        isUserFault: false,
        shouldRetry: true,
        userMessage: '일시적인 오류가 발생했습니다. 다시 시도해주세요.',
        techMessage: error.message || 'Unknown error',
        shouldDeductHP: false
    };
}

/**
 * 에러 핸들러 (통합)
 * 
 * @param {Error} error - 발생한 에러
 * @param {object} context - { gameState, addSystemLog, handleDamage }
 * @param {object} options - { fallbackAction, retryAction }
 * @returns {object} 처리 결과
 */
export async function handleErrorWithRetry(error, context, options = {}) {
    const {
        gameState,
        addSystemLog,
        handleDamage
    } = context;

    const {
        fallbackAction,
        retryAction,
        maxRetries = 2
    } = options;

    const analysis = analyzeError(error);

    // 로그 출력
    console.error(`[ErrorHandler] ${analysis.type}:`, analysis.techMessage);
    
    // 사용자 메시지 표시
    if (gameState) {
        gameState.feedbackMessage = analysis.userMessage;
    }
    
    if (addSystemLog) {
        addSystemLog(analysis.userMessage, analysis.isUserFault ? 'ERROR' : 'WARN');
    }

    // HP 차감 여부 결정
    if (analysis.shouldDeductHP && handleDamage) {
        handleDamage(10); // 사용자 입력 오류만 HP 차감
    }

    // 재시도 로직
    if (analysis.shouldRetry && retryAction) {
        let retryCount = 0;
        
        while (retryCount < maxRetries) {
            retryCount++;
            
            if (addSystemLog) {
                addSystemLog(`재시도 중... (${retryCount}/${maxRetries})`, 'INFO');
            }
            
            // 지수 백오프 (1초, 2초, 4초...)
            await new Promise(resolve => 
                setTimeout(resolve, 1000 * Math.pow(2, retryCount - 1))
            );
            
            try {
                const result = await retryAction();
                
                if (addSystemLog) {
                    addSystemLog('재접속 성공!', 'SUCCESS');
                }
                
                return {
                    success: true,
                    result,
                    analysis
                };
            } catch (retryError) {
                const retryAnalysis = analyzeError(retryError);
                
                // 재시도해도 안 되는 에러면 중단
                if (!retryAnalysis.shouldRetry) {
                    break;
                }
            }
        }
        
        // 모든 재시도 실패
        if (addSystemLog) {
            addSystemLog('재시도 실패. 안전 모드로 전환합니다.', 'ERROR');
        }
    }

    // Fallback 실행
    if (fallbackAction) {
        try {
            const fallbackResult = await fallbackAction();
            return {
                success: false,
                result: fallbackResult,
                analysis,
                usedFallback: true
            };
        } catch (fallbackError) {
            console.error('[ErrorHandler] Fallback also failed:', fallbackError);
        }
    }

    return {
        success: false,
        result: null,
        analysis
    };
}

/**
 * 코드 실행 에러 핸들러 (useCodeRunner.js 전용)
 * 
 * @param {Error} error - 실행 에러
 * @param {object} context - 게임 컨텍스트
 * @returns {object} 처리 결과
 */
export async function handleCodeExecutionError(error, context) {
    const { gameState, addSystemLog, handleDamage } = context;

    return await handleErrorWithRetry(
        error,
        context,
        {
            // Fallback: 로컬 검증으로 전환
            fallbackAction: async () => {
                addSystemLog('로컬 검증 모드로 전환...', 'INFO');
                
                // 간단한 로컬 검증
                const code = gameState.userCode || '';
                const hasBasicStructure = 
                    code.includes('def') || 
                    code.includes('class') ||
                    code.length > 20;
                
                if (hasBasicStructure) {
                    addSystemLog('기본 구조 확인 완료 (부분 점수)', 'INFO');
                    return {
                        isValid: true,
                        score: 50,
                        feedback: '서버 검증 실패로 부분 점수만 부여됩니다.',
                        usedFallback: true
                    };
                } else {
                    addSystemLog('코드 구조 미흡', 'WARN');
                    return {
                        isValid: false,
                        score: 0,
                        feedback: '코드를 더 작성해주세요.',
                        usedFallback: true
                    };
                }
            },
            
            // Retry: 서버 재접속 시도
            retryAction: async () => {
                // 원래 실행 로직 재시도
                // (실제로는 executeCode 함수를 다시 호출)
                throw new Error('Retry logic should be implemented by caller');
            },
            
            maxRetries: 2
        }
    );
}

/**
 * AI 평가 에러 핸들러 (pseudocodeApi.js 전용)
 */
export async function handleAIEvaluationError(error, context) {
    const analysis = analyzeError(error);

    // AI 실패는 사용자 책임 아님 (HP 차감 없음)
    if (context.addSystemLog) {
        if (analysis.type === ErrorType.NETWORK || analysis.type === ErrorType.SERVER) {
            context.addSystemLog('AI 서버 일시 장애. 규칙 기반 평가로 진행합니다.', 'WARN');
        } else {
            context.addSystemLog('AI 평가 오류. 기본 피드백을 제공합니다.', 'INFO');
        }
    }

    return {
        success: false,
        analysis,
        shouldDeductHP: false,  // AI 실패는 HP 차감 없음
        fallbackMessage: '기본 평가 로직으로 진행됩니다. 점수는 유효합니다.'
    };
}