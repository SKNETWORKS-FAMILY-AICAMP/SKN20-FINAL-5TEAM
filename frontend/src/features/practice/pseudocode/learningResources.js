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
        title: '머신러닝파이프라인',
        url: 'https://www.youtube.com/watch?v=example1',
        channel: 'StatQuest',
        curationPoint: '전처리 순서가 왜 중요한지, 데이터 분할이 왜 가장 먼저여야 하는지 논리적 흐름을 잡아줍니다.',
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
        title: '예외처리',
        url: 'https://www.youtube.com/watch?v=example3',
        channel: 'MLOps Community',
        curationPoint: '배포 후 데이터 분포가 변했을 때(Drift) 발생하는 문제와 재학습의 필요성을 실무 관점에서 설명합니다.',
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
        title: '문제구조화',
        url: 'https://www.youtube.com/watch?v=example5',
        channel: 'Data School',
        curationPoint: '복잡한 머신러닝 개념을 의사코드와 도식으로 단순화하여 시스템적으로 사고하는 법을 알려줍니다.',
        difficulty: 'beginner'
      }
    ]
  },

  implementation: {
    metric: '구현력 (Implementation)',
    theme: 'Scikit-learn 실전 활용법, 파이썬 코딩 팁',
    curationMessage: '머릿속 설계를 손 끝으로 완벽하게 구현하는 기술, 라이브러리 활용 팁을 모았습니다.',
    videos: [
      {
        title: 'Scikit-learn fit transform 차이',
        url: 'https://www.youtube.com/watch?v=example7',
        channel: 'StatQuest',
        curationPoint: 'fit, transform을 실수 없이 연결하는 실제 파이썬 코딩 테크닉과 라이브러리 활용법을 다룹니다.',
        difficulty: 'beginner'
      }
    ]
  },

  consistency: {
    metric: '정합성 (Consistency)',
    theme: '데이터 누수(Leakage) 방지 심화 강의',
    curationMessage: '작은 틈새가 모델을 망칩니다. 일관성을 유지하는 완벽한 방어 기제를 확인하세요.',
    videos: [
      {
        title: 'Data Leakage(데이터 누수) 완벽 가이드',
        url: 'https://www.youtube.com/watch?v=example10',
        channel: 'Kaggle',
        curationPoint: '사소한 코딩 실수가 어떻게 모델의 성능을 뻥튀기시키고 "거짓 모델"을 만드는지 경각심을 줍니다.',
        difficulty: 'intermediate'
      }
    ]
  },

  // ==================== 마스터 레벨 (80점 이상) ====================
  master: {
    metric: '마스터 레벨',
    theme: 'Enterprise Scale ML in Production',
    curationMessage: '"이미 완벽한 당신, 이제는 수조 개의 데이터를 처리하는 기업형 AI 시스템 설계에 도전할 때입니다. 개별 모델을 넘어 전체 시스템의 효율을 극대화하는 법을 확인하세요."',
    videos: [
      {
        title: 'Enterprise Scale Machine Learning in Production',
        url: 'https://www.youtube.com/watch?v=example12',
        channel: 'Netflix Tech Blog',
        curationPoint: '단순히 "맞는" 설계가 아니라, "확장 가능한(Scalable)" 인프라적 관점으로 시야를 넓혀줍니다.',
        difficulty: 'expert'
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
