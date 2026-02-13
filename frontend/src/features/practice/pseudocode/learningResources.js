/**
 * 학습 리소스 큐레이션 시스템
 * 취약 지표별 맞춤형 콘텐츠 추천
 */

export const LEARNING_RESOURCES = {
  // ==================== 지표별 콘텐츠 ====================
  design: {
    metric: '설계력 (Design)',
    theme: '데이터 전처리 파이프라인 설계 원칙',
    curationMessage: '설계의 뼈대가 흔들리면 모델도 흔들립니다. 파이프라인 설계의 정석을 확인하세요.',
    videos: [
      {
        title: 'Machine Learning Pipeline 완벽 가이드',
        url: 'https://www.youtube.com/watch?v=example1',
        channel: 'StatQuest with Josh Starmer',
        duration: '15:23',
        language: 'EN',
        difficulty: 'intermediate',
        curationPoint: '전처리 순서가 왜 중요한지, 데이터 분할이 왜 가장 먼저여야 하는지 논리적 흐름을 잡아줍니다.',
        keyTakeaways: [
          'Train/Test Split의 타이밍',
          'Pipeline 설계 원칙',
          '전처리 순서의 중요성'
        ]
      },
      {
        title: '데이터 전처리 파이프라인 설계 실전',
        url: 'https://www.youtube.com/watch?v=example2',
        channel: '빵형의 개발도상국',
        duration: '22:41',
        language: 'KR',
        difficulty: 'beginner',
        curationPoint: '한국어로 쉽게 설명하는 전처리 파이프라인 구축 방법과 실수 사례',
        keyTakeaways: [
          '초보자가 흔히 하는 실수',
          '단계별 체크리스트',
          '실무 적용 팁'
        ]
      }
    ],
    articles: [
      {
        title: 'Scikit-learn Pipeline: 완벽한 설계 가이드',
        url: 'https://scikit-learn.org/stable/modules/compose.html',
        readTime: '10분',
        difficulty: 'intermediate'
      }
    ]
  },

  edgeCase: {
    metric: '예외처리 (Edge Case)',
    theme: 'MLOps, 데이터 드리프트, 실전 배포',
    curationMessage: '이론은 완벽하지만 실전은 변수 투성이입니다. 변화하는 데이터에 대응하는 법을 배우세요.',
    videos: [
      {
        title: 'Data Drift Detection and Handling',
        url: 'https://www.youtube.com/watch?v=example3',
        channel: 'MLOps Community',
        duration: '18:45',
        language: 'EN',
        difficulty: 'advanced',
        curationPoint: '배포 후 데이터 분포가 변했을 때(Drift) 발생하는 문제와 재학습의 필요성을 실무 관점에서 설명합니다.',
        keyTakeaways: [
          '데이터 드리프트 감지 방법',
          '모델 재학습 전략',
          '모니터링 시스템 구축'
        ]
      },
      {
        title: 'MLOps 실전: 모델 모니터링과 재배포',
        url: 'https://www.youtube.com/watch?v=example4',
        channel: '네이버 D2',
        duration: '32:15',
        language: 'KR',
        difficulty: 'advanced',
        curationPoint: '실제 프로덕션 환경에서 발생하는 문제와 대응 전략',
        keyTakeaways: [
          '실시간 성능 모니터링',
          'A/B 테스팅 전략',
          '자동 재학습 파이프라인'
        ]
      }
    ],
    articles: [
      {
        title: 'Monitoring Machine Learning Models in Production',
        url: 'https://christophergs.com/machine%20learning/2020/03/14/how-to-monitor-machine-learning-models/',
        readTime: '15분',
        difficulty: 'advanced'
      }
    ]
  },

  abstraction: {
    metric: '추상화 (Abstraction)',
    theme: '데이터 과학 사고법, 의사코드 작성법',
    curationMessage: '개념을 코드로 옮기는 "생각의 근육"이 필요합니다. 구조적으로 사고하는 법을 추천합니다.',
    videos: [
      {
        title: 'How to Think Like a Data Scientist',
        url: 'https://www.youtube.com/watch?v=example5',
        channel: 'Data School',
        duration: '14:32',
        language: 'EN',
        difficulty: 'beginner',
        curationPoint: '복잡한 머신러닝 개념을 의사코드와 도식으로 단순화하여 시스템적으로 사고하는 법을 알려줍니다.',
        keyTakeaways: [
          '문제 구조화 방법',
          '의사코드 작성 팁',
          '추상화 레벨 설정'
        ]
      },
      {
        title: '알고리즘 설계 - 의사코드로 생각하기',
        url: 'https://www.youtube.com/watch?v=example6',
        channel: '동빈나',
        duration: '19:28',
        language: 'KR',
        difficulty: 'beginner',
        curationPoint: '코드를 작성하기 전 논리를 정리하는 의사코드 활용법',
        keyTakeaways: [
          '의사코드 표기법',
          '논리 흐름 설계',
          '코드 변환 전략'
        ]
      }
    ]
  },

  implementation: {
    metric: '구현력 (Implementation)',
    theme: 'Scikit-learn 실전 활용법, 파이썬 코딩 팁',
    curationMessage: '머릿속 설계를 손 끝으로 완벽하게 구현하는 기술, 라이브러리 활용 팁을 모았습니다.',
    videos: [
      {
        title: 'Scikit-learn: fit() vs transform() 완벽 이해',
        url: 'https://www.youtube.com/watch?v=example7',
        channel: 'StatQuest',
        duration: '11:47',
        language: 'EN',
        difficulty: 'beginner',
        curationPoint: 'fit, transform을 실수 없이 연결하는 실제 파이썬 코딩 테크닉과 라이브러리 활용법을 다룹니다.',
        keyTakeaways: [
          'fit()의 내부 동작',
          'transform() 사용 시점',
          'fit_transform() 주의사항'
        ]
      },
      {
        title: 'Sklearn Pipeline 마스터하기',
        url: 'https://www.youtube.com/watch?v=example8',
        channel: 'Corey Schafer',
        duration: '25:13',
        language: 'EN',
        difficulty: 'intermediate',
        curationPoint: 'Pipeline 객체를 활용한 깔끔한 전처리 코드 작성법',
        keyTakeaways: [
          'Pipeline 구조 이해',
          'ColumnTransformer 활용',
          '커스텀 Transformer 작성'
        ]
      },
      {
        title: '실무 머신러닝 - 전처리 코드 작성 실습',
        url: 'https://www.youtube.com/watch?v=example9',
        channel: '코딩애플',
        duration: '28:36',
        language: 'KR',
        difficulty: 'beginner',
        curationPoint: '실제 데이터로 따라하는 전처리 파이프라인 구현',
        keyTakeaways: [
          '실전 코드 예제',
          '자주 하는 실수',
          '디버깅 팁'
        ]
      }
    ],
    articles: [
      {
        title: 'Scikit-learn Preprocessing: Best Practices',
        url: 'https://scikit-learn.org/stable/modules/preprocessing.html',
        readTime: '20분',
        difficulty: 'intermediate'
      }
    ]
  },

  consistency: {
    metric: '정합성 (Consistency)',
    theme: '데이터 누수(Leakage) 방지 심화 강의',
    curationMessage: '작은 틈새가 모델을 망칩니다. 일관성을 유지하는 완벽한 방어 기제를 확인하세요.',
    videos: [
      {
        title: 'Data Leakage: The Silent Model Killer',
        url: 'https://www.youtube.com/watch?v=example10',
        channel: 'Kaggle',
        duration: '16:52',
        language: 'EN',
        difficulty: 'intermediate',
        curationPoint: '사소한 코딩 실수가 어떻게 모델의 성능을 뻥튀기시키고 "거짓 모델"을 만드는지 경각심을 줍니다.',
        keyTakeaways: [
          'Leakage 발생 패턴',
          '검증 방법',
          '실제 사례 분석'
        ]
      },
      {
        title: '데이터 누수 완벽 가이드 - 실전 예제',
        url: 'https://www.youtube.com/watch?v=example11',
        channel: '모두의연구소',
        duration: '21:34',
        language: 'KR',
        difficulty: 'intermediate',
        curationPoint: '한국어로 설명하는 데이터 누수의 모든 것',
        keyTakeaways: [
          'Temporal Leakage',
          'Target Leakage',
          '방지 체크리스트'
        ]
      }
    ],
    articles: [
      {
        title: 'Avoiding Data Leakage in Machine Learning',
        url: 'https://towardsdatascience.com/data-leakage-in-machine-learning',
        readTime: '12분',
        difficulty: 'intermediate'
      }
    ]
  },

  // ==================== 마스터 레벨 (80점 이상) ====================
  master: {
    metric: '마스터 레벨',
    theme: 'Enterprise Scale ML in Production',
    curationMessage: '이미 완벽한 당신, 이제는 수조 개의 데이터를 처리하는 기업형 AI 시스템 설계에 도전할 때입니다. 개별 모델을 넘어 전체 시스템의 효율을 극대화하는 법을 확인하세요.',
    videos: [
      {
        title: 'Scaling Machine Learning at Netflix',
        url: 'https://www.youtube.com/watch?v=example12',
        channel: 'Netflix Tech Blog',
        duration: '42:18',
        language: 'EN',
        difficulty: 'expert',
        curationPoint: '단순히 "맞는" 설계가 아니라, "확장 가능한(Scalable)" 인프라적 관점으로 시야를 넓혀줍니다.',
        keyTakeaways: [
          '대규모 ML 시스템 아키텍처',
          '실시간 추론 최적화',
          'Feature Store 설계'
        ]
      },
      {
        title: 'MLOps Maturity Model',
        url: 'https://www.youtube.com/watch?v=example13',
        channel: 'Google Cloud',
        duration: '35:47',
        language: 'EN',
        difficulty: 'expert',
        curationPoint: '레벨 0부터 레벨 4까지 MLOps 성숙도 단계별 전략',
        keyTakeaways: [
          'CI/CD for ML',
          'Model Registry',
          '자동화 파이프라인'
        ]
      },
      {
        title: '카카오 추천 시스템 아키텍처',
        url: 'https://www.youtube.com/watch?v=example14',
        channel: 'if(kakao)',
        duration: '38:22',
        language: 'KR',
        difficulty: 'expert',
        curationPoint: '국내 대기업의 실제 프로덕션 ML 시스템 설계 사례',
        keyTakeaways: [
          'A/B 테스트 인프라',
          '실시간 특성 처리',
          '모델 버저닝 전략'
        ]
      }
    ],
    articles: [
      {
        title: 'Hidden Technical Debt in Machine Learning Systems',
        url: 'https://papers.nips.cc/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf',
        readTime: '30분',
        difficulty: 'expert',
        description: 'Google의 유명한 ML 기술 부채 논문'
      }
    ]
  }
};

/**
 * 취약 지표에 맞는 콘텐츠 추천
 */
export function recommendContent(weakestMetric, totalScore) {
  // 80점 이상이면 마스터 콘텐츠
  if (totalScore >= 80) {
    return LEARNING_RESOURCES.master;
  }

  // 취약 지표 매핑
  const metricMap = {
    'abstraction': 'abstraction',
    'implementation': 'implementation',
    'design': 'design',
    'edgeCase': 'edgeCase',
    'consistency': 'consistency'
  };

  const key = metricMap[weakestMetric] || 'design';
  return LEARNING_RESOURCES[key];
}

/**
 * 점수 구간별 필터링
 */
export function filterByScore(resources, score) {
  if (score >= 80) {
    return resources.videos.filter(v => v.difficulty === 'expert');
  } else if (score >= 60) {
    return resources.videos.filter(v => 
      v.difficulty === 'intermediate' || v.difficulty === 'advanced'
    );
  } else {
    return resources.videos.filter(v => 
      v.difficulty === 'beginner' || v.difficulty === 'intermediate'
    );
  }
}
