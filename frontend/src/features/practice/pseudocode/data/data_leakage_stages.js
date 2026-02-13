/**
 * 데이터 누수 방지 미션 - 전체 스테이지 구조
 * [2026-02-14] 5단계 평가 시스템
 */

export const dataLeakageMission = {
  id: 'data_leakage_prevention',
  title: '데이터 누수 방지 마스터클래스',
  scenario: `신입 개발자가 작성한 이탈 예측 모델이 검증(Validation) 정확도 95%를 기록하며 배포되었으나, 
실제 고객 데이터가 들어오는 운영(Serving) 환경에서는 68%의 성능을 보이며 비즈니스에 큰 손실을 입혔습니다. 
조사 결과, 데이터 전처리 단계에서 '정보 유출(Leakage)'이 발생한 것으로 파악되었습니다.`,

  // ==================== STAGE 1: 객관식 빌드업 ====================
  stage1_buildup: {
    title: '사고의 빌드업 (객관식)',
    description: '3대 키워드를 머릿속에 심어주는 단계',
    questions: [
      {
        id: 'isolation',
        keyword: '격리 (Isolation)',
        question: `[격리의 시점] 데이터 오염을 막는 첫 번째 방어선
        
신입 개발자가 범한 가장 큰 실수는 scaler.fit(df)를 통해 전체 데이터의 정보를 섞어버린 것입니다. 
이를 방지하기 위한 가장 우선적인 조치는 무엇인가요?`,
        options: [
          {
            text: '더 많은 데이터를 수집하여 모델을 복잡하게 만든다.',
            correct: false,
            feedback: '데이터 양 증가는 누수 방지와 무관합니다.'
          },
          {
            text: '전처리(Scaling)를 모두 마친 후 데이터를 나눈다.',
            correct: false,
            feedback: '❌ 이것이 바로 신입 개발자가 범한 실수입니다. Fit before Split!'
          },
          {
            text: '데이터 전처리 프로세스가 시작되기 전, 학습(Train)과 테스트(Test) 데이터를 물리적으로 분리(격리)한다.',
            correct: true,
            feedback: '✅ 정답! 전처리 전 분리가 가장 확실한 방어선입니다.'
          },
          {
            text: '운영 환경에서는 전처리를 생략한다.',
            correct: false,
            feedback: '학습 때와 동일한 전처리가 운영에서도 필수입니다.'
          }
        ],
        thinkingGuide: '💡 이것이 필수 조건인 **격리(Isolation)**의 핵심입니다. 벽을 먼저 세우지 않으면 정보는 반드시 흐르게 됩니다.',
        score: 0  // Stage 1은 점수 없음 (개념 주입)
      },
      {
        id: 'anchor',
        keyword: '기준점 (Anchor)',
        question: `[기준점의 설정] '저울'은 무엇으로 만들어야 하는가?
        
데이터를 분리한 후, 표준화(Standardization)를 위한 평균과 표준편차 값은 어느 데이터셋에서 추출해야 하나요?`,
        options: [
          {
            text: '전체 데이터셋: 데이터가 많을수록 통계량이 정확하기 때문이다.',
            correct: false,
            feedback: '전체 데이터 사용 시 테스트 정보가 유출됩니다.'
          },
          {
            text: '테스트 데이터셋: 실제 운영 환경과 유사한 분포를 가져야 하기 때문이다.',
            correct: false,
            feedback: '테스트는 미래 데이터 역할이므로 기준으로 사용 불가.'
          },
          {
            text: '학습 데이터셋: 모델이 "이미 알고 있는 과거의 정보"만을 기준으로 삼아야 하기 때문이다.',
            correct: true,
            feedback: '✅ 정답! 학습 데이터의 저울로 모든 데이터를 측정해야 정보 유출이 없습니다.'
          },
          {
            text: '무작위 추출: 편향을 방지하기 위해 매번 새로 계산해야 한다.',
            correct: false,
            feedback: '기준점이 매번 바뀌면 모델의 판단 기준이 흔들립니다.'
          }
        ],
        thinkingGuide: '💡 이것이 **기준점(Anchor)** 설정의 원칙입니다. 미래의 정보를 훔쳐보지 않는 유일한 방법입니다.',
        score: 0
      }
    ]
  },

  // ==================== STAGE 2: 의사코드 작성 ====================
  stage2_pseudocode: {
    title: '논리의 뼈대 (의사코드)',
    description: '3대 키워드를 사용한 파이프라인 설계',
    maxScore: 30,
    scoring: {
      abstraction: {
        name: '추상화',
        weight: 15,
        criteria: '3대 키워드(격리, 기준점, 일관성) 사용 및 논리 구조화'
      },
      ruleBased: {
        name: 'Rule 기반',
        weight: 15,
        criteria: '필수 키워드 포함 + 순서(분할→학습) 정확성'
      }
    },
    prompt: `[미션] 실제 운영 환경에서 이 모델이 '바보'가 되지 않도록, 데이터 오염을 원천 차단하는 전처리 파이프라인의 설계 원칙과 그 순서를 '의사코드(Pseudo Code)' 형태로 서술하세요.

[필수 포함 조건]
다음 3가지 키워드를 반드시 사용하여 논리를 구성하세요:
- 격리 (Isolation): 데이터를 나누는 시점
- 기준점 (Anchor): 통계량(fit)을 추출할 대상
- 일관성 (Consistency): 학습과 운영 환경의 동일한 변환 방식`,
    
    validation: {
      requiredKeywords: ['격리', '기준점', '일관성', 'train', 'test', 'fit', 'transform'],
      criticalPatterns: [
        {
          pattern: /(전체|모든|전부).*(fit|학습)/i,
          error: '전체 데이터로 fit 감지 - 데이터 누수 발생!'
        },
        {
          pattern: /(test|테스트).*(fit|학습시키)/i,
          error: '테스트 데이터로 fit 감지 - 심각한 누수!'
        }
      ],
      orderCheck: {
        required: ['split', 'fit', 'transform'],
        message: '순서 오류: 분할 → Fit(train) → Transform(train, test)'
      }
    }
  },

  // ==================== STAGE 3: 코드 변환 + 꼬리질문 ====================
  stage3_implementation: {
    title: '구현 검증 (코드 변환)',
    description: '의사코드 → Python 변환 + 논리 검증',
    maxScore: 50,
    scoring: {
      implementation: {
        name: '구현력',
        weight: 10,
        criteria: '의사코드의 Python 파싱 가능성'
      },
      design: {
        name: '설계력',
        weight: 25,
        criteria: '논리적 개연성 및 흐름 정확성'
      },
      edgeCase: {
        name: '예외처리',
        weight: 15,
        criteria: '실무 확장 상황 대응력'
      }
    },
    
    // 부족한 키워드 감지 시 꼬리질문
    followUpQuestions: {
      isolation_missing: {
        question: `Q. [격리 보완] 당신의 설계에서 "데이터 분할 시점"이 명확하지 않습니다.
        
다음 중 올바른 격리 전략은?`,
        options: [
          '전처리 완료 후 분할',
          '학습 중간에 필요 시 분할',
          '전처리 시작 전 즉시 분할 ✅',
          '분할하지 않고 전체 데이터 사용'
        ],
        correctIndex: 2
      },
      anchor_missing: {
        question: `Q. [기준점 보완] 스케일러의 fit은 어느 데이터로 수행해야 하나요?`,
        options: [
          '전체 데이터',
          '테스트 데이터',
          '학습 데이터 ✅',
          '검증 데이터'
        ],
        correctIndex: 2
      },
      consistency_missing: {
        question: `Q. [일관성 보완] 운영 환경에서 새로운 데이터가 들어올 때, 어떤 전처리를 적용해야 하나요?`,
        options: [
          '새로운 통계로 다시 fit',
          '전처리 생략',
          '학습 때 저장한 scaler로 transform만 수행 ✅',
          '테스트 데이터 통계 사용'
        ],
        correctIndex: 2
      }
    }
  },

  // ==================== STAGE 4: Deep Dive ====================
  stage4_deepdive: {
    title: 'Deep Dive 심화 분석',
    description: '3대 축(시간/환경/한계) 중 1개 랜덤 출제',
    maxScore: 0,  // Stage 3 점수에 포함
    
    scenarios: [
      {
        id: 'time_drift',
        axis: '시간의 축',
        name: '데이터 드리프트',
        question: `완벽한 파이프라인으로 배포된 모델입니다. 하지만 1년 뒤, 새로운 고객층이 유입되어 데이터 분포가 완전히 바뀌었습니다. 

기존의 **기준점(Anchor)**을 고수하면 성능이 박살 날 텐데, 이때 '일관성' 원칙을 깨고 기준을 바꿀 것인가요? 아니면 다른 대안이 있나요?

[1~2문장으로 서술하세요]`,
        intent: '설계의 영속성과 재학습(Retraining) 파이프라인의 필요성 인지',
        scoringKeywords: ['모니터링', '재학습', 'retraining', '기준점 갱신', 'update', 'drift 감지'],
        maxLength: 200
      },
      {
        id: 'environment_realtime',
        axis: '환경의 축',
        name: '실시간 서빙',
        question: `이 로직이 0.1초 내에 결과를 내놓아야 하는 실시간 결제 시스템에 들어갑니다. 

매번 전체 데이터를 다시 **격리(Split)**하고 **기준점(Fit)**을 찾는 건 불가능합니다. 정확도를 포기하지 않으면서 속도를 확보할 엔지니어링적 타협점은 무엇인가요?

[1~2문장으로 서술하세요]`,
        intent: '이론적 설계가 인프라 제약을 만났을 때의 최적화 능력',
        scoringKeywords: ['serialization', 'pickle', 'joblib', '사전 계산', 'pipeline 객체', '저장', '캐싱'],
        maxLength: 200
      },
      {
        id: 'limit_smalldata',
        axis: '한계의 축',
        name: '데이터 부족',
        question: `전체 데이터가 100건뿐입니다. '격리' 원칙을 지키며 20건을 테스트로 뺐더니 학습이 안 되고, 안 빼자니 오염이 걱정됩니다. 

원칙을 훼손하지 않으면서도 모델을 제대로 검증할 수 있는 '교차 검증(Cross-validation)' 전략을 제안해 보세요.

[1~2문장으로 서술하세요]`,
        intent: '고정된 분할 방식 외에 통계적 검증 기법의 이해도',
        scoringKeywords: ['k-fold', 'cross validation', '교차 검증', 'stratified', '리샘플링', 'cv'],
        maxLength: 200
      }
    ]
  },

  // ==================== STAGE 5: 종합 평가 ====================
  stage5_final: {
    title: '최종 진단 및 리포트',
    description: 'LLM 85% + Rule 15% 종합 평가',
    maxScore: 20,
    scoring: {
      consistency: {
        name: '정합성',
        weight: 20,
        criteria: '전체 과정에서 누수 방지 원칙의 일관성'
      }
    }
  },

  // ==================== 총점 계산 ====================
  totalScoring: {
    stage2: 30,  // 추상화(15) + Rule(15)
    stage3: 50,  // 구현(10) + 설계(25) + 예외(15)
    stage5: 20,  // 정합성(20)
    total: 100
  },

  // ==================== 5대 지표 ====================
  metrics: {
    design: {
      name: '설계력 (Design)',
      weight: 25,
      description: '전처리 순서 및 흐름의 논리성',
      stage: 'stage3'
    },
    consistency: {
      name: '정합성 (Consistency)',
      weight: 20,
      description: 'Train/Test 기준점 유지 및 일관성',
      stage: 'stage5'
    },
    implementation: {
      name: '구현력 (Implementation)',
      weight: 10,
      description: '의사코드의 Python 변환 정확도',
      stage: 'stage3'
    },
    edgeCase: {
      name: '예외처리 (Edge Case)',
      weight: 15,
      description: '데이터 변화(Drift) 및 실무 환경 대응력',
      stage: 'stage3'
    },
    abstraction: {
      name: '추상화 (Abstraction)',
      weight: 15,
      description: '핵심 키워드 사용 및 논리적 구조화',
      stage: 'stage2'
    }
  }
};
