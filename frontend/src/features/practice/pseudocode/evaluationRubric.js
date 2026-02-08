/**
 * Pseudocode Practice Evaluation Rubric
 * AI 기반 5차원 메트릭 평가 시스템
 * 평가 철학: 정답 채점 ❌ → 사고력 평가 ✅
 */

export const EVALUATION_RUBRIC = {
    pseudocode: {
        coherence: {
            weight: 20,
            maxScore: 100,
            name: "정합성 (Coherence)",
            description: "quest_title과 사용자 로직의 일치 여부 확인",
            criteria: [
                "문제의 목표(quest_title)를 정확히 이해하고 해결했는가?",
                "설계 의도와 구현 로직이 일치하는가?",
                "각 단계가 문제 해결에 실제로 기여하는가?"
            ],
            keywords: {
                required: ["목표", "해결", "방향"],
                forbidden: ["무관한", "관계없는"]
            }
        },
        abstraction: {
            weight: 20,
            maxScore: 100,
            name: "추상화 (Abstraction)",
            description: "의사코드의 간결성 및 핵심 로직 표현력 평가",
            criteria: [
                "핵심 로직만 간결하게 표현했는가?",
                "불필요한 세부사항을 배제했는가?",
                "적절한 추상화 레벨을 유지하는가?",
                "단순 키워드 나열이 아닌 논리적 흐름이 있는가?"
            ],
            scoring_guide: {
                excellent: "핵심 로직 명확 + 간결함 + 논리적 흐름 (80-100점)",
                good: "기본 흐름은 있으나 불필요한 세부사항 포함 (60-79점)",
                poor: "단순 키워드 나열 또는 과도한 세부사항 (0-40점)"
            }
        },
        exception_handling: {
            weight: 20,
            maxScore: 100,
            name: "예외처리 (Exception Handling)",
            description: "예외 상황 대응 키워드 및 로직 포함 여부 분석",
            criteria: [
                "엣지 케이스를 고려했는가?",
                "예외 상황 처리 로직이 명시되었는가?",
                "방어적 프로그래밍 사고가 있는가?",
                "오류 시나리오를 예상하고 대응했는가?"
            ],
            keywords: {
                positive: ["예외", "검증", "확인", "체크", "방어", "오류", "처리"],
                examples: ["if 조건 검증", "입력값 확인", "None 체크", "빈 값 처리"]
            }
        },
        implementation: {
            weight: 20,
            maxScore: 100,
            name: "구현력 (Implementation)",
            description: "의사코드의 구체성과 논리적 흐름의 명확성 평가",
            criteria: [
                "실제 구현 가능한 수준으로 구체적인가?",
                "각 단계가 명확하고 실행 가능한가?",
                "순서가 논리적으로 타당한가?",
                "실무에서 바로 코드로 옮길 수 있는가?"
            ]
        },
        architecture: {
            weight: 20,
            maxScore: 100,
            name: "설계력 (Architecture)",
            description: "단계별 연결성 및 아키텍처적 완성도 검증",
            criteria: [
                "단계 간 논리적 연결성이 있는가?",
                "전체적인 설계 구조가 견고한가?",
                "확장 가능성을 고려했는가?",
                "아키텍처 패턴을 적절히 활용했는가?"
            ],
            tail_question_trigger: "논리적 허점이 발견되면 Tail Question 자동 생성"
        }
    },
    interview: {
        depth: {
            weight: 20,
            name: "답변 깊이",
            scoring: {
                excellent: {
                    range: [45, 50],
                    criteria: [
                        "기술 용어를 정확히 사용",
                        "트레이드오프를 명시",
                        "실무 적용 예시 포함"
                    ],
                    keywords: ["파이프라인", "누수", "fit", "transform", "오염", "검증"]
                },
                good: {
                    range: [30, 44],
                    criteria: [
                        "핵심 개념은 이해함",
                        "설명이 구체적",
                        "기술 용어 일부 포함"
                    ]
                },
                poor: {
                    range: [0, 29],
                    criteria: [
                        "개념 이해 부족",
                        "설명이 추상적",
                        "오개념 포함"
                    ]
                }
            }
        },
        accuracy: {
            weight: 20,
            name: "정확성",
            criteria: [
                "질문에 정확히 답변했는가?",
                "오개념이 없는가?",
                "핵심을 파악했는가?"
            ]
        },
        completeness: {
            weight: 10,
            name: "완결성",
            criteria: [
                "모든 질문에 답변했는가?",
                "답변 길이가 적절한가?",
                "구체적인 예시가 있는가?"
            ]
        }
    }
};

export const FEW_SHOT_EXAMPLES = {
    dataLeakage: {
        excellent: {
            pseudocode: `
1. 학습 데이터(train_df)와 테스트 데이터(test_df)를 분리한다
2. StandardScaler 객체를 생성한다
3. **오직 학습 데이터로만** 스케일러를 학습시킨다 (fit)
4. 학습된 스케일러로 학습 데이터를 변환한다 (transform)
5. **동일한 스케일러로** 테스트 데이터를 변환한다 (transform)
6. 변환된 두 데이터셋을 반환한다
`,
            score: 90,
            feedback: "데이터 누수 방지 원칙을 완벽히 이해하고 있습니다. 특히 '오직 학습 데이터로만'과 '동일한 스케일러로'를 강조한 점이 우수합니다."
        },
        good: {
            pseudocode: `
1. 스케일러를 만든다
2. 학습 데이터로 fit 한다
3. 학습 데이터를 transform 한다
4. 테스트 데이터를 transform 한다
5. 결과를 반환한다
`,
            score: 70,
            feedback: "기본적인 흐름은 맞지만, 왜 이 순서인지에 대한 이유가 부족합니다. 데이터 누수 방지 원칙을 명시하면 더 좋습니다."
        },
        poor: {
            pseudocode: `
1. 모든 데이터를 합친다
2. 스케일러로 정규화한다
3. 다시 train과 test로 나눈다
`,
            score: 30,
            feedback: "치명적인 오류: 데이터 누수가 발생합니다. 테스트 데이터의 정보가 학습 과정에 유입되어서는 안 됩니다."
        }
    },
    interview: {
        excellent: {
            answer: "데이터 누수는 모델이 미래의 정보를 학습하게 만드는 치명적인 오류입니다. 예를 들어 스케일러를 전체 데이터로 fit하면 테스트 데이터의 평균/분산 정보가 학습에 유입되어, 실제 배포 환경에서는 얻을 수 없는 정보를 사용하게 됩니다. 이로 인해 학습 시 높은 성능을 보이지만 실전에서는 급격히 성능이 하락합니다. 따라서 fit은 반드시 학습 데이터로만 수행하고, transform만 테스트에 적용해야 합니다.",
            score: 48,
            feedback: "완벽한 답변입니다. 개념, 예시, 원인, 해결책을 모두 포함했습니다."
        },
        good: {
            answer: "데이터 누수는 테스트 데이터의 정보가 학습에 사용되는 것입니다. 스케일러를 만들 때 학습 데이터로만 fit해야 하고 테스트는 transform만 해야 합니다.",
            score: 35,
            feedback: "핵심은 맞지만 왜 문제인지에 대한 설명이 부족합니다."
        },
        poor: {
            answer: "데이터가 섞이면 안 좋습니다.",
            score: 15,
            feedback: "너무 추상적입니다. 구체적으로 무엇이, 왜, 어떻게 문제인지 설명해야 합니다."
        }
    }
};

export const CONSISTENCY_CHECK_RULES = {
    dataLeakage: {
        pseudocode_must_mention: [
            "학습 데이터로만 fit",
            "동일한 스케일러",
            "transform",
            "순서"
        ],
        code_must_have: [
            "StandardScaler()",
            "scaler.fit(train",
            "scaler.transform(train",
            "scaler.transform(test"
        ],
        code_must_not_have: [
            "fit(test",
            "fit(.*test.*train",
            "fit.*concat",
            "fit.*merge"
        ]
    }
};

export function buildEvaluationPrompt(problem, pseudocode, rubric, examples) {
    return `당신은 AI 기반 의사코드 평가 전문가입니다.

# 평가 철학
- 정답 채점 ❌ → 사고력 평가 ✅
- 단순 키워드 매칭이 아닌 논리적 연결성 검증
- 논리적 허점 발견 시 Tail Question 자동 생성

# 5차원 메트릭 평가 기준
${JSON.stringify(rubric, null, 2)}

# Few-shot Examples (참고용)

## 우수한 예시 (90점)
### 의사코드:
${examples.excellent.pseudocode}

### 평가:
- 점수: ${examples.excellent.score}
- 피드백: ${examples.excellent.feedback}

## 보통 예시 (70점)
### 의사코드:
${examples.good.pseudocode}

### 평가:
- 점수: ${examples.good.score}
- 피드백: ${examples.good.feedback}

## 부족한 예시 (30점)
### 의사코드:
${examples.poor.pseudocode}

### 평가:
- 점수: ${examples.poor.score}
- 피드백: ${examples.poor.feedback}

---

# 실제 평가 대상

## 문제
${problem.title || "데이터 누수 방지"}
${problem.description || problem.missionObjective}

## 학생이 작성한 의사코드
${pseudocode}

---

# 출력 형식 (JSON만 출력!)

5차원 메트릭으로 평가하여 아래 형식의 JSON만 출력하세요:

{
  "totalScore": 0,
  "details": [
    {
      "dimension": "정합성",
      "score": 0,
      "maxScore": 100,
      "basis": "quest_title과 로직의 일치도 평가 근거"
    },
    {
      "dimension": "추상화",
      "score": 0,
      "maxScore": 100,
      "basis": "간결성 및 핵심 표현력 평가 근거 (단순 나열이면 40점 이하)"
    },
    {
      "dimension": "예외처리",
      "score": 0,
      "maxScore": 100,
      "basis": "예외 상황 대응 로직 확인 근거"
    },
    {
      "dimension": "구현력",
      "score": 0,
      "maxScore": 100,
      "basis": "구체성과 실행 가능성 평가 근거"
    },
    {
      "dimension": "설계력",
      "score": 0,
      "maxScore": 100,
      "basis": "단계별 연결성 및 아키텍처 완성도 평가 근거"
    }
  ],
  "strengths": ["강점1", "강점2"],
  "weaknesses": ["약점1"],
  "tailQuestions": ["논리적 허점 발견 시 생성되는 추가 질문"],
  "seniorAdvice": "시니어 엔지니어 관점 교육적 피드백",
  "keywordCheck": {
    "found": ["발견된 긍정 키워드들"],
    "missing": ["누락된 필수 개념들"]
  }
}`;
}
