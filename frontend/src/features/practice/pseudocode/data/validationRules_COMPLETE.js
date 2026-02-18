/**
 * 寃利?洹쒖튃 ?쇱씠釉뚮윭由?- 利됱떆 ?ъ슜 媛?? * stages.js??蹂듭궗?댁꽌 ?ъ슜
 * 
 * [2026-02-14] ?ㅼ쟾 諛고룷 踰꾩쟾
 */

// ==================== Mission 1: Data Leakage ====================
export const VALIDATION_DATA_LEAKAGE = {
  type: 'data_leakage',
  
  criticalPatterns: [
    {
      pattern: {
        positive: /(?꾩껜|紐⑤뱺|all|whole|entire).*(?곗씠??data).*(fit|?숈뒿|fitting)/i,
        negatives: [
          /????湲덉?|留?never|not|don't|avoid|prevent/i
        ]
      },
      message: '?슚 ?곗씠???꾩닔: ?꾩껜 ?곗씠?곕줈 fit 湲덉?',
      correctExample: 'scaler.fit(X_train) ??scaler.transform(X_train), scaler.transform(X_test)',
      explanation: '?ㅼ??쇰윭???숈뒿 ?곗씠?곗쓽 ?듦퀎留??숈뒿?댁빞 ?⑸땲?? ?뚯뒪???곗씠???뺣낫媛 ?좎엯?섎㈃ 怨쇱쟻?⑸맗?덈떎.',
      severity: 'CRITICAL'
    },
    {
      pattern: {
        positive: /(test|?뚯뒪??寃利?.*(fit|?숈뒿?쒗궎|fitting)/i,
        negatives: [
          /????湲덉?|never|not|don't/i,
          /transform/i  // "test瑜?transform"? OK
        ]
      },
      message: '?슚 ?뚯뒪???곗씠?곕줈 fit 湲덉?',
      correctExample: '?숈뒿 ?곗씠?곕줈留?fit ???뚯뒪?몃뒗 transform留?,
      explanation: '?뚯뒪???곗씠?곕뒗 誘몃옒??蹂댁씠吏 ?딅뒗 ?곗씠?곕? ?쒕??덉씠?섑빀?덈떎.',
      severity: 'CRITICAL'
    }
  ],

  requiredConcepts: [
    {
      id: 'data_split',
      name: '?곗씠??遺꾨━',
      weight: 15,
      patterns: [
        /遺꾨━|?섎늻|?섎닎|split|separate|divide/i,
        /train.*test|?숈뒿.*?뚯뒪??training.*testing/i,
        /train_test_split/i
      ],
      hints: [
        '?곗씠?곕? ?숈뒿?⑷낵 ?뚯뒪?몄슜?쇰줈 ?섎늻???④퀎媛 ?꾩슂?⑸땲??',
        'train_test_split() 媛숈? ?⑥닔瑜??ъ슜?섏꽭??'
      ]
    },
    {
      id: 'scaler_create',
      name: '?ㅼ??쇰윭 ?앹꽦',
      weight: 15,
      patterns: [
        /scaler|?ㅼ??쇰윭|standardscaler|minmaxscaler/i,
        /?뺢퇋??*?꾧뎄|normalization.*tool|scaling.*object/i,
        /StandardScaler\(\)|MinMaxScaler\(\)/i
      ],
      hints: [
        '?곗씠???ㅼ??쇰쭅???꾪븳 媛앹껜瑜??앹꽦?댁빞 ?⑸땲??',
        'StandardScaler ?먮뒗 MinMaxScaler瑜??몄뒪?댁뒪?뷀븯?몄슂.'
      ]
    },
    {
      id: 'fit_train',
      name: '?숈뒿 ?곗씠?곕줈 fit',
      weight: 20,
      patterns: [
        /(train|?숈뒿|training).*(fit|?숈뒿??fitting)/i,
        /fit.*train|?숈뒿??*train/i,
        /scaler\.fit\(.*train/i
      ],
      hints: [
        '?ㅼ??쇰윭瑜??숈뒿 ?곗씠?곕줈 ?숈뒿?쒖폒???⑸땲??',
        'scaler.fit(X_train) ?뺥깭濡??묒꽦?섏꽭??'
      ]
    },
    {
      id: 'transform_train',
      name: '?숈뒿 ?곗씠??蹂??,
      weight: 15,
      patterns: [
        /(train|?숈뒿).*(transform|蹂??transforming)/i,
        /transform.*train|蹂??*train/i,
        /scaler\.transform\(.*train/i
      ],
      hints: [
        '?숈뒿 ?곗씠?곕룄 ?ㅼ??쇰쭅 蹂?섏씠 ?꾩슂?⑸땲??',
        'X_train_scaled = scaler.transform(X_train)'
      ]
    },
    {
      id: 'transform_test',
      name: '?뚯뒪???곗씠??蹂??,
      weight: 15,
      patterns: [
        /(test|?뚯뒪??testing).*(transform|蹂??transforming)/i,
        /transform.*test|蹂??*test/i,
        /scaler\.transform\(.*test/i
      ],
      hints: [
        '?뚯뒪???곗씠?곕뒗 transform留??섑뻾?댁빞 ?⑸땲??',
        'X_test_scaled = scaler.transform(X_test)'
      ]
    },
    {
      id: 'same_scaler',
      name: '?숈씪 ?ㅼ??쇰윭 ?ъ슜',
      weight: 10,
      patterns: [
        /媛숈?.*scaler|?숈씪.*scaler|same.*scaler/i,
        /?섎굹??*scaler|??*scaler|one.*scaler/i
      ],
      hints: [
        '?숈뒿怨??뚯뒪?몄뿉 媛숈? ?ㅼ??쇰윭 ?몄뒪?댁뒪瑜??ъ슜?섏꽭??'
      ]
    }
  ],

  dependencies: [
    {
      name: '遺꾨━ ???ㅼ??쇰윭 ?앹꽦',
      before: 'data_split',
      after: 'scaler_create',
      points: 8,
      strictness: 'RECOMMENDED'
    },
    {
      name: 'fit ??transform(train)',
      before: 'fit_train',
      after: 'transform_train',
      points: 15,
      strictness: 'REQUIRED'
    },
    {
      name: 'fit ??transform(test)',
      before: 'fit_train',
      after: 'transform_test',
      points: 15,
      strictness: 'REQUIRED'
    },
    {
      name: 'transform(train) ??transform(test)',
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
      name: 'fit() 硫붿꽌??,
      mustNotContainIn: 'comments'
    },
    {
      pattern: /\.transform\s*\(/i,
      name: 'transform() 硫붿꽌??,
      mustNotContainIn: 'comments'
    },
    {
      pattern: /train_test_split/i,
      name: 'train_test_split ?⑥닔'
    }
  ],

  forbiddenPatterns: [
    {
      pattern: /\.fit\s*\(\s*[^)]*test[^)]*\)/i,
      message: '?뚯뒪???곗씠?곕줈 fit() ?몄텧 湲덉?',
      excludeComments: true
    },
    {
      pattern: /\.fit\s*\(\s*X\s*\)/i,  // X留??⑤룆?쇰줈 (?꾩껜 ?곗씠??
      message: '?꾩껜 ?곗씠??X)濡?fit() ?몄텧 湲덉?',
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
        positive: /(test|?뚯뒪??.*(cross.*validation|cv|援먯감.*寃利?/i,
        negatives: [/????not|never/i]
      },
      message: '?슚 CV???숈뒿 ?곗씠?곗뿉留??곸슜',
      correctExample: 'cv = cross_val_score(model, X_train, y_train)',
      explanation: '援먯감 寃利앹? ?숈뒿 ?④퀎?먯꽌留??ъ슜?⑸땲??'
    }
  ],

  requiredConcepts: [
    {
      id: 'data_split',
      name: '?곗씠??遺꾨━',
      weight: 15,
      patterns: [/train_test_split/i]
    },
    {
      id: 'cv_apply',
      name: 'CV ?곸슜',
      weight: 25,
      patterns: [
        /cross_val_score|KFold|StratifiedKFold/i,
        /援먯감.*寃利?cross.*validation/i
      ]
    },
    {
      id: 'only_train',
      name: '?숈뒿 ?곗씠?곕쭔 ?ъ슜',
      weight: 20,
      patterns: [
        /cv.*train|cross.*validation.*train/i
      ]
    },
    {
      id: 'final_test',
      name: '理쒖쥌 ?뚯뒪???됯?',
      weight: 20,
      patterns: [
        /(理쒖쥌|final).*(test|?뚯뒪??.*(?됯?|evaluation)/i
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
        positive: /(test|?뚯뒪??.*(?앹꽦|create|engineer).*(feature|?뱀꽦)/i,
        negatives: [/????not/i, /媛숈?|same|identical/i]
      },
      message: '?슚 ?뱀꽦 ?붿??덉뼱留곸쓣 ?뚯뒪?몄뿉 癒쇱? ?곸슜?섎㈃ ???⑸땲??,
      correctExample: '?숈뒿 ?곗씠?곕줈 ?뱀꽦 ?앹꽦 洹쒖튃 ?숈뒿 ???숈씪 洹쒖튃???뚯뒪?몄뿉 ?곸슜',
      explanation: '?뱀꽦 ?앹꽦 洹쒖튃? ?숈뒿 ?곗씠?곗뿉?쒕쭔 ?숈뒿?섏뼱???⑸땲??'
    }
  ],

  requiredConcepts: [
    {
      id: 'feature_idea',
      name: '?뱀꽦 ?꾩씠?붿뼱',
      weight: 20,
      patterns: [
        /?덈줈??*?뱀꽦|new.*feature|feature.*engineering/i,
        /議고빀|combination|interaction/i
      ]
    },
    {
      id: 'train_apply',
      name: '?숈뒿 ?곗씠???곸슜',
      weight: 25,
      patterns: [
        /(train|?숈뒿).*(?곸슜|apply|?앹꽦|create)/i
      ]
    },
    {
      id: 'test_same_rule',
      name: '?뚯뒪?몄뿉 ?숈씪 洹쒖튃',
      weight: 25,
      patterns: [
        /(媛숈?|?숈씪|same|identical).*(洹쒖튃|rule|method)/i,
        /(test|?뚯뒪??.*(媛숈?|?숈씪|same)/i
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

// ==================== ?쇱씠釉뚮윭由?(stages.js?먯꽌 李몄“) ====================
export const VALIDATION_LIBRARY = {
  data_leakage: VALIDATION_DATA_LEAKAGE,
  cross_validation: VALIDATION_CROSS_VALIDATION,
  feature_engineering: VALIDATION_FEATURE_ENGINEERING
};

export const CODE_VALIDATION_LIBRARY = {
  data_leakage: CODE_VALIDATION_DATA_LEAKAGE
};

/**
 * stages.js ?ъ슜 ?덉떆:
 * 
 * import { VALIDATION_LIBRARY } from './validationRules_COMPLETE.js';
 * 
 * export const aiQuests = [
 *   {
 *     id: 1,
 *     title: "?곗씠???꾩닔 諛⑹??섍린",
 *     validation: VALIDATION_LIBRARY.data_leakage,
 *     codeValidation: CODE_VALIDATION_LIBRARY.data_leakage,
 *     // ... 湲고? ?꾨뱶
 *   }
 * ];
 */
