/**
 * 검증 규칙 메타데이터 (stages.js에 추가)
 * 
 * 문제: PseudocodeValidator.js에 하드코딩된 규칙
 * 해결: 데이터 레이어로 분리 (OCP 원칙 준수)
 * 
 * [2026-02-09] 확장성 개선 (Antigravity)
 */

/**
 * 각 미션에 추가할 검증 규칙 구조
 * 
 * stages.js의 각 quest 객체에 이 구조를 추가:
 */
export const VALIDATION_RULES_TEMPLATE = {
    // 미션 ID
    id: 1,
    title: "데이터 누수 방지하기",
    
    // ... 기존 필드들 ...
    
    // ✨ 새로 추가: 검증 규칙 메타데이터
    validation: {
        // 치명적 오류 패턴 (블로킹)
        criticalPatterns: [
            {
                // 부정어를 고려한 정규식 (5번 해결책 포함)
                pattern: {
                    // 양성 패턴 (이게 있으면 오류)
                    positive: /(전체|모든|all).*(데이터|data).*(fit|학습)/i,
                    // 부정어가 있으면 통과
                    negatives: [
                        /않|안|금지|never|not|don't|avoid/i
                    ]
                },
                message: '🚨 데이터 누수 발생: 전체 데이터로 fit하면 안 됩니다',
                correctExample: '학습 데이터로만 fit → 두 데이터셋 모두 transform',
                explanation: '스케일러는 학습 데이터의 통계만 학습해야 합니다.',
                severity: 'CRITICAL'
            },
            {
                pattern: {
                    positive: /(test|테스트|검증).*(fit|학습시)/i,
                    negatives: [
                        /않|안|금지|never|not|don't/i,
                        /transform/i  // "test를 transform"은 OK
                    ]
                },
                message: '🚨 테스트 데이터로 fit하면 안 됩니다',
                correctExample: 'train으로 fit → test는 transform만',
                explanation: '테스트 데이터는 미래의 데이터를 시뮬레이션합니다.',
                severity: 'CRITICAL'
            }
        ],

        // 필수 개념 (동의어 포함)
        requiredConcepts: [
            {
                id: 'data_split',
                name: '데이터 분리',
                weight: 15,  // 점수 가중치
                patterns: [
                    /분리|나누|나눔|split|separate|divide/i,
                    /train.*test|학습.*테스트/i
                ],
                hints: [
                    '데이터를 학습용과 테스트용으로 나누는 단계가 필요합니다.',
                    'train_test_split 같은 함수를 사용할 수 있습니다.'
                ]
            },
            {
                id: 'scaler_create',
                name: '스케일러 생성',
                weight: 15,
                patterns: [
                    /scaler|스케일러|standardscaler/i,
                    /정규화.*도구|normalization/i
                ]
            },
            {
                id: 'fit_train',
                name: '학습 데이터로 fit',
                weight: 20,
                patterns: [
                    /(train|학습).*(fit|학습시)/i,
                    /fit.*(train|학습)/i
                ]
            },
            {
                id: 'transform_train',
                name: '학습 데이터 변환',
                weight: 15,
                patterns: [
                    /(train|학습).*(transform|변환)/i
                ]
            },
            {
                id: 'transform_test',
                name: '테스트 데이터 변환',
                weight: 15,
                patterns: [
                    /(test|테스트).*(transform|변환)/i
                ]
            }
        ],

        // 논리적 의존성 (순서)
        dependencies: [
            {
                name: '분리 → 스케일러 생성',
                before: 'data_split',
                after: 'scaler_create',
                points: 8,
                strictness: 'RECOMMENDED'  // REQUIRED | RECOMMENDED | OPTIONAL
            },
            {
                name: 'fit → transform',
                before: 'fit_train',
                after: 'transform_train',
                points: 12,
                strictness: 'REQUIRED'
            }
        ],

        // 점수 구성 (총 100점)
        scoring: {
            structure: 20,      // 기본 구조 (번호, 길이 등)
            concepts: 40,       // 필수 개념 포함
            flow: 40           // 논리적 순서
        },

        // 추가 권장사항
        recommendations: {
            exceptionHandling: true,
            minLines: 3,
            maxLines: 15,
            preferredStyle: 'numbered'  // numbered | bullet | prose
        }
    },

    // 코드 검증 규칙 (Phase 4용, 6번 해결책 포함)
    codeValidation: {
        // 필수 메서드/함수 호출
        requiredCalls: [
            {
                pattern: /\.fit\s*\(/i,
                name: 'fit() 메서드',
                mustNotContainIn: 'comments'  // 주석에만 있으면 안 됨
            },
            {
                pattern: /\.transform\s*\(/i,
                name: 'transform() 메서드',
                mustNotContainIn: 'comments'
            }
        ],

        // 금지 패턴
        forbiddenPatterns: [
            {
                pattern: /fit\s*\(\s*.*test/i,
                message: '테스트 데이터로 fit 호출 금지',
                excludeComments: true  // 주석 제외하고 검사
            }
        ],

        // 주석 제거 규칙
        commentPatterns: [
            /#.*$/gm,           // Python single-line
            /"""[\s\S]*?"""/g,  // Python docstring
            /'''[\s\S]*?'''/g   // Python docstring alt
        ]
    }
};

/**
 * 실제 stages.js에 추가할 예시
 * 
 * 기존 aiQuests 배열의 각 객체에 위 validation 필드를 추가:
 */
export const EXAMPLE_STAGE_WITH_VALIDATION = {
    id: 1,
    title: "데이터 누수 방지하기 (Data Leakage Prevention)",
    category: "ML Safety",
    difficulty: "⭐⭐⭐",
    
    // ... 기존 필드들 (missionObjective, npcDialogue 등) ...
    
    // ✨ 검증 규칙 추가
    validation: {
        type: 'data_leakage',  // 검증 타입 (재사용 가능)
        
        criticalPatterns: [
            {
                pattern: {
                    positive: /(전체|모든|all).*(데이터|data).*(fit|학습)/i,
                    negatives: [/않|안|not|never/i]
                },
                message: '🚨 전체 데이터로 fit 금지',
                correctExample: '학습 데이터로만 fit',
                explanation: '테스트 정보가 학습에 유입됩니다.'
            }
        ],
        
        requiredConcepts: [
            {
                id: 'data_split',
                name: '데이터 분리',
                weight: 15,
                patterns: [/분리|split/i, /train.*test/i]
            },
            // ... 나머지 개념들
        ],
        
        dependencies: [
            {
                before: 'data_split',
                after: 'scaler_create',
                points: 8
            }
            // ... 나머지 의존성들
        ],
        
        scoring: {
            structure: 20,
            concepts: 40,
            flow: 40
        }
    },
    
    codeValidation: {
        requiredCalls: [
            { pattern: /\.fit\s*\(/i, name: 'fit()' },
            { pattern: /\.transform\s*\(/i, name: 'transform()' }
        ],
        forbiddenPatterns: [
            {
                pattern: /fit\s*\(.*test/i,
                message: '테스트 데이터로 fit 금지',
                excludeComments: true
            }
        ],
        commentPatterns: [/#.*$/gm, /"""[\s\S]*?"""/g]
    }
};

/**
 * 재사용 가능한 검증 타입 라이브러리
 * 
 * stages.js 파일 하단에 추가:
 */
export const VALIDATION_TYPE_LIBRARY = {
    // Data Leakage 타입 (여러 미션에서 재사용)
    data_leakage: {
        criticalPatterns: [/* ... */],
        requiredConcepts: [/* ... */],
        // ...
    },
    
    // Cross Validation 타입
    cross_validation: {
        criticalPatterns: [
            {
                pattern: {
                    positive: /(test|테스트).*(cross.*validation|cv)/i,
                    negatives: [/않|안|not/i]
                },
                message: '🚨 CV는 학습 데이터에만 적용',
                // ...
            }
        ],
        // ...
    },
    
    // Feature Engineering 타입
    feature_engineering: {
        // ...
    }
};

/**
 * 사용 방법:
 * 
 * 1. stages.js에 VALIDATION_TYPE_LIBRARY 추가
 * 2. 각 quest에 validation.type 지정
 * 3. PseudocodeValidator는 quest.validation을 주입받아 사용
 * 
 * 예:
 * {
 *   id: 1,
 *   validation: {
 *     type: 'data_leakage',  // 라이브러리에서 불러옴
 *     // 미션별 커스터마이징 추가 가능
 *     customPatterns: [...]
 *   }
 * }
 */