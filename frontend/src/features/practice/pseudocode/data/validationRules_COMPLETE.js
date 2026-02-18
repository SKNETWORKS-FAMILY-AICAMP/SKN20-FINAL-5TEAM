/**
 * 검증 규칙 라이브러리 - 즉시 사용 가능
 * stages.js에 복사해서 사용
 * 
 * [2026-02-18] pseudo_tts 브랜치와 프론트엔드 UI 및 로직 완전 동기화 (HMR 에러 및 인코딩 복구)
 */

// ==================== Mission 1: Data Leakage ====================
export const VALIDATION_DATA_LEAKAGE = {
  type: 'data_leakage',

  criticalPatterns: [
    {
      pattern: {
        positive: /(전체|모든|all|whole|entire).*(데이터|data).*(fit|학습|fitting)/i,
        negatives: [
          /않|안|금지|말|never|not|don't|avoid|prevent/i
        ]
      },
      message: '🚨 데이터 누수: 전체 데이터로 fit 금지',
      correctExample: 'scaler.fit(X_train) → scaler.transform(X_train), scaler.transform(X_test)',
      explanation: '스케일러는 학습 데이터의 통계만 학습해야 합니다. 테스트 데이터 정보가 유입되면 과적합됩니다.',
      severity: 'CRITICAL'
    },
    {
      pattern: {
        positive: /(test|테스트|검증).*(fit|학습시키|fitting)/i,
        negatives: [
          /않|안|금지|never|not|don't/i,
          /transform/i  // "test를 transform"은 OK
        ]
      },
      message: '🚨 테스트 데이터로 fit 금지',
      correctExample: '학습 데이터로만 fit → 테스트는 transform만',
      explanation: '테스트 데이터는 미래의 보이지 않는 데이터를 시뮬레이션합니다.',
      severity: 'CRITICAL'
    }
  ],

  requiredConcepts: [
    {
      id: 'data_split',
      name: '데이터 분리',
      weight: 15,
      patterns: [
        /분리|나누|나눔|split|separate|divide/i,
        /train.*test|학습.*테스트|training.*testing/i,
        /train_test_split/i
      ],
      hints: [
        '데이터를 학습용과 테스트용으로 나누는 단계가 필요합니다.',
        'train_test_split() 같은 함수를 사용하세요.'
      ]
    },
    {
      id: 'scaler_create',
      name: '스케일러 생성',
      weight: 15,
      patterns: [
        /scaler|스케일러|standardscaler|minmaxscaler/i,
        /정규화.*도구|normalization.*tool|scaling.*object/i,
        /StandardScaler\(\)|MinMaxScaler\(\)/i
      ],
      hints: [
        '데이터 스케일링을 위한 객체를 생성해야 합니다.',
        'StandardScaler 또는 MinMaxScaler를 인스턴스화하세요.'
      ]
    },
    {
      id: 'fit_train',
      name: '학습 데이터로 fit',
      weight: 20,
      patterns: [
        /(train|학습|training).*(fit|학습시|fitting)/i,
        /fit.*train|학습시.*train/i,
        /scaler\.fit\(.*train/i
      ],
      hints: [
        '스케일러를 학습 데이터로 학습시켜야 합니다.',
        'scaler.fit(X_train) 형태로 작성하세요.'
      ]
    },
    {
      id: 'transform_train',
      name: '학습 데이터 변환',
      weight: 15,
      patterns: [
        /(train|학습).*(transform|변환|transforming)/i,
        /transform.*train|변환.*train/i,
        /scaler\.transform\(.*train/i
      ],
      hints: [
        '학습 데이터도 스케일링 변환이 필요합니다.',
        'X_train_scaled = scaler.transform(X_train)'
      ]
    },
    {
      id: 'transform_test',
      name: '테스트 데이터 변환',
      weight: 15,
      patterns: [
        /(test|테스트|testing).*(transform|변환|transforming)/i,
        /transform.*test|변환.*test/i,
        /scaler\.transform\(.*test/i
      ],
      hints: [
        '테스트 데이터는 transform만 수행해야 합니다.',
        'X_test_scaled = scaler.transform(X_test)'
      ]
    },
    {
      id: 'same_scaler',
      name: '동일 스케일러 사용',
      weight: 10,
      patterns: [
        /같은.*scaler|동일.*scaler|same.*scaler/i,
        /하나의.*scaler|한.*scaler|one.*scaler/i
      ],
      hints: [
        '학습과 테스트에 같은 스케일러 인스턴스를 사용하세요.'
      ]
    }
  ],

  dependencies: [
    {
      name: '분리 → 스케일러 생성',
      before: 'data_split',
      after: 'scaler_create',
      points: 8,
      strictness: 'RECOMMENDED'
    },
    {
      name: 'fit → transform(train)',
      before: 'fit_train',
      after: 'transform_train',
      points: 15,
      strictness: 'REQUIRED'
    },
    {
      name: 'fit → transform(test)',
      before: 'fit_train',
      after: 'transform_test',
      points: 15,
      strictness: 'REQUIRED'
    },
    {
      name: 'transform(train) → transform(test)',
      before: 'transform_train',
      after: 'transform_test',
      points: 12,
      strictness: 'RECOMMENDED'
    }
  ],

  scoring: {
    structure: 20,
    concepts: 40,
    flow: 40
  },

  recommendations: {
    minLines: 4,
    maxLines: 12,
    preferredStyle: 'numbered'
  }
};

// Code validation (Phase 4)
export const CODE_VALIDATION_DATA_LEAKAGE = {
  requiredCalls: [
    {
      pattern: /\.fit\s*\(/i,
      name: 'fit() 메서드',
      mustNotContainIn: 'comments'
    },
    {
      pattern: /\.transform\s*\(/i,
      name: 'transform() 메서드',
      mustNotContainIn: 'comments'
    },
    {
      pattern: /train_test_split/i,
      name: 'train_test_split 함수'
    }
  ],

  forbiddenPatterns: [
    {
      pattern: /\.fit\s*\(\s*[^)]*test[^)]*\)/i,
      message: '테스트 데이터로 fit() 호출 금지',
      excludeComments: true
    },
    {
      pattern: /\.fit\s*\(\s*X\s*\)/i,  // X만 단독으로 (전체 데이터)
      message: '전체 데이터(X)로 fit() 호출 금지',
      excludeComments: true
    }
  ],

  commentPatterns: [
    /#.*$/gm,
    /"""[\s\S]*?"""/g,
    /'''[\s\S]*?'''/g
  ]
};

// ==================== Mission 2: Cross Validation ====================
export const VALIDATION_CROSS_VALIDATION = {
  type: 'cross_validation',

  criticalPatterns: [
    {
      pattern: {
        positive: /(test|테스트).*(cross.*validation|cv|교차.*검증)/i,
        negatives: [/않|안|not|never/i]
      },
      message: '🚨 CV는 학습 데이터에만 적용',
      correctExample: 'cv = cross_val_score(model, X_train, y_train)',
      explanation: '교차 검증은 학습 단계에서만 사용됩니다.'
    }
  ],

  requiredConcepts: [
    {
      id: 'data_split',
      name: '데이터 분리',
      weight: 15,
      patterns: [/train_test_split/i]
    },
    {
      id: 'cv_apply',
      name: 'CV 적용',
      weight: 25,
      patterns: [
        /cross_val_score|KFold|StratifiedKFold/i,
        /교차.*검증|cross.*validation/i
      ]
    },
    {
      id: 'only_train',
      name: '학습 데이터만 사용',
      weight: 20,
      patterns: [
        /cv.*train|cross.*validation.*train/i
      ]
    },
    {
      id: 'final_test',
      name: '최종 테스트 평가',
      weight: 20,
      patterns: [
        /(최종|final).*(test|테스트).*(평가|evaluation)/i
      ]
    }
  ],

  dependencies: [
    {
      before: 'data_split',
      after: 'cv_apply',
      points: 15,
      strictness: 'REQUIRED'
    },
    {
      before: 'cv_apply',
      after: 'final_test',
      points: 20,
      strictness: 'REQUIRED'
    }
  ],

  scoring: { structure: 20, concepts: 40, flow: 40 },
  recommendations: { minLines: 3, maxLines: 10 }
};

// ==================== Mission 3: Feature Engineering ====================
export const VALIDATION_FEATURE_ENGINEERING = {
  type: 'feature_engineering',

  criticalPatterns: [
    {
      pattern: {
        positive: /(test|테스트).*(생성|create|engineer).*(feature|특성)/i,
        negatives: [/않|안|not/i, /같은|same|identical/i]
      },
      message: '🚨 특성 엔지니어링을 테스트에 먼저 적용하면 안 됩니다',
      correctExample: '학습 데이터로 특성 생성 규칙 학습 → 동일 규칙을 테스트에 적용',
      explanation: '특성 생성 규칙은 학습 데이터에서만 학습되어야 합니다.'
    }
  ],

  requiredConcepts: [
    {
      id: 'feature_idea',
      name: '특성 아이디어',
      weight: 20,
      patterns: [
        /새로운.*특성|new.*feature|feature.*engineering/i,
        /조합|combination|interaction/i
      ]
    },
    {
      id: 'train_apply',
      name: '학습 데이터 적용',
      weight: 25,
      patterns: [
        /(train|학습).*(적용|apply|생성|create)/i
      ]
    },
    {
      id: 'test_same_rule',
      name: '테스트에 동일 규칙',
      weight: 25,
      patterns: [
        /(같은|동일|same|identical).*(규칙|rule|method)/i,
        /(test|테스트).*(같은|동일|same)/i
      ]
    }
  ],

  dependencies: [
    {
      before: 'train_apply',
      after: 'test_same_rule',
      points: 30,
      strictness: 'REQUIRED'
    }
  ],

  scoring: { structure: 20, concepts: 50, flow: 30 },
  recommendations: { minLines: 3, maxLines: 10 }
};

// ==================== 라이브러리 (stages.js에서 참조) ====================
export const VALIDATION_LIBRARY = {
  data_leakage: VALIDATION_DATA_LEAKAGE,
  cross_validation: VALIDATION_CROSS_VALIDATION,
  feature_engineering: VALIDATION_FEATURE_ENGINEERING
};

export const CODE_VALIDATION_LIBRARY = {
  data_leakage: CODE_VALIDATION_DATA_LEAKAGE
};

/**
 * stages.js 사용 예시:
 * 
 * import { VALIDATION_LIBRARY } from './validationRules_COMPLETE.js';
 * 
 * export const aiQuests = [
 *   {
 *     id: 1,
 *     title: "데이터 누수 방지하기",
 *     validation: VALIDATION_LIBRARY.data_leakage,
 *     codeValidation: CODE_VALIDATION_LIBRARY.data_leakage,
 *     // ... 기타 필드
 *   }
 * ];
 */
