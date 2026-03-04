// [수정일: 2026-03-04] AICE 자격증 등급별 실전 문제 데이터
// Phase1: 4지선다 객관식 (options + answerIdx)
// Phase2: 의사코드 작성 (checklist 패턴 매칭)

export const logicQuests = [
  // ═══════════════════════════════════════════════════════════════
  // BASIC (2 퀘스트) — 비전공자/입문자 대상
  // ═══════════════════════════════════════════════════════════════
  {
    id: 1,
    difficulty: 'Basic',
    title: "pandas 기초 데이터 조작",
    scenario: "CSV 파일을 읽어 결측치를 처리하고, 기초 통계를 출력하는 pandas 코드를 의사코드로 작성하세요.",

    speedRounds: [
      {
        round: 1,
        context: "pandas에서 CSV 파일을 읽어 DataFrame으로 변환하는 함수는?",
        options: ["pd.read_csv()", "pd.load_csv()", "pd.open_csv()", "pd.import_csv()"],
        answerIdx: 0,
        explanation: "pd.read_csv()는 CSV 파일을 DataFrame으로 읽는 기본 함수입니다."
      },
      {
        round: 2,
        context: "DataFrame에서 결측치(NaN)가 있는지 컬럼별로 확인하는 코드는?",
        options: ["df.isnull().sum()", "df.null_count()", "df.check_nan()", "df.missing()"],
        answerIdx: 0,
        explanation: "isnull()은 NaN 여부를 Boolean으로 반환하고, sum()으로 개수를 셉니다."
      },
      {
        round: 3,
        context: "DataFrame의 '나이' 컬럼에서 결측치를 평균값으로 채우는 코드는?",
        options: [
          "df['나이'].fillna(df['나이'].mean())",
          "df['나이'].dropna(mean)",
          "df['나이'].replace(mean)",
          "df['나이'].set_null(mean)"
        ],
        answerIdx: 0,
        explanation: "fillna()는 결측치를 지정한 값으로 채우는 메서드입니다."
      },
      {
        round: 4,
        context: "DataFrame에서 '점수' 컬럼을 기준으로 내림차순 정렬하는 코드는?",
        options: [
          "df.sort_values('점수', ascending=False)",
          "df.order_by('점수', desc=True)",
          "df.sort('점수', reverse=True)",
          "df.arrange('점수', ascending=False)"
        ],
        answerIdx: 0,
        explanation: "sort_values()에서 ascending=False로 내림차순 정렬합니다."
      },
      {
        round: 5,
        context: "DataFrame의 수치형 컬럼에 대한 기초 통계(평균, 표준편차 등)를 한번에 보는 함수는?",
        options: ["df.describe()", "df.statistics()", "df.summary()", "df.info()"],
        answerIdx: 0,
        explanation: "describe()는 count, mean, std, min, max 등을 한번에 보여줍니다."
      }
    ],

    designSprint: {
      checklist: [
        { id: "c1", label: "CSV 파일 읽기 (read_csv)", patterns: ["read_csv|csv.*읽|파일.*로드|불러오기"] },
        { id: "c2", label: "결측치 확인 (isnull, isna)", patterns: ["isnull|isna|결측|null|NaN|nan"] },
        { id: "c3", label: "결측치 처리 (fillna 또는 dropna)", patterns: ["fillna|dropna|결측.*처리|결측.*제거|평균.*채"] },
        { id: "c4", label: "기초 통계 출력 (describe, mean, std 등)", patterns: ["describe|mean|std|통계|평균|표준편차"] },
        { id: "c5", label: "결과 출력 (print)", patterns: ["print|출력|표시|보여"] }
      ]
    }
  },

  {
    id: 2,
    difficulty: 'Basic',
    title: "Python 리스트와 반복문",
    scenario: "숫자 리스트에서 짝수만 필터링하고, 각 값을 제곱한 새 리스트를 만드는 코드를 의사코드로 작성하세요.",

    speedRounds: [
      {
        round: 1,
        context: "Python에서 빈 리스트를 생성하는 올바른 코드는?",
        options: ["result = []", "result = {}", "result = ()", "result = ''"],
        answerIdx: 0,
        explanation: "[]는 빈 리스트, {}는 빈 딕셔너리, ()는 빈 튜플입니다."
      },
      {
        round: 2,
        context: "숫자 n이 짝수인지 확인하는 조건식은?",
        options: ["n % 2 == 0", "n / 2 == 0", "n // 2 == 0", "n & 2 == 0"],
        answerIdx: 0,
        explanation: "% 연산자는 나머지를 구합니다. 2로 나눈 나머지가 0이면 짝수입니다."
      },
      {
        round: 3,
        context: "리스트 result에 값 x를 추가하는 메서드는?",
        options: ["result.append(x)", "result.add(x)", "result.push(x)", "result.insert(x)"],
        answerIdx: 0,
        explanation: "append()는 리스트 끝에 요소를 추가하는 메서드입니다."
      },
      {
        round: 4,
        context: "x의 제곱을 계산하는 Python 표현식은?",
        options: ["x ** 2", "x ^^ 2", "pow(x)", "x << 2"],
        answerIdx: 0,
        explanation: "Python에서 거듭제곱 연산자는 **입니다."
      },
      {
        round: 5,
        context: "리스트 컴프리헨션으로 짝수 필터링 + 제곱을 한 줄로 작성하면?",
        options: [
          "[x**2 for x in nums if x%2==0]",
          "[x**2 if x%2==0 for x in nums]",
          "{x**2 for x in nums if x%2==0}",
          "(x**2 for x in nums if x%2==0)"
        ],
        answerIdx: 0,
        explanation: "리스트 컴프리헨션은 [표현식 for 변수 in 반복 if 조건] 순서입니다."
      }
    ],

    designSprint: {
      checklist: [
        { id: "c1", label: "입력 리스트 정의", patterns: ["리스트|list|nums|numbers|배열|\\["] },
        { id: "c2", label: "반복문으로 순회 (for)", patterns: ["for|반복|순회|loop|each"] },
        { id: "c3", label: "짝수 조건 판별 (% 2)", patterns: ["%.*2|짝수|나머지|even|mod"] },
        { id: "c4", label: "제곱 계산 (** 2 또는 pow)", patterns: ["\\*\\*|제곱|pow|square|거듭"] },
        { id: "c5", label: "결과 리스트에 추가 (append)", patterns: ["append|추가|add|push|결과.*리스트"] }
      ]
    }
  },

  // ═══════════════════════════════════════════════════════════════
  // ASSOCIATE (2 퀘스트) — 실무 입문, sklearn 중심
  // ═══════════════════════════════════════════════════════════════
  {
    id: 3,
    difficulty: 'Associate',
    title: "sklearn 분류 모델 파이프라인",
    scenario: "타이타닉 데이터셋을 전처리하고, 랜덤 포레스트 분류 모델을 학습시켜 생존 여부를 예측하는 전체 파이프라인을 의사코드로 작성하세요.",

    speedRounds: [
      {
        round: 1,
        context: "train_test_split에서 테스트 데이터 비율을 20%로 설정하는 파라미터는?",
        options: ["test_size=0.2", "split_ratio=0.2", "test_ratio=0.2", "val_size=0.2"],
        answerIdx: 0,
        explanation: "test_size=0.2는 전체 데이터의 20%를 테스트 세트로 분리합니다."
      },
      {
        round: 2,
        context: "범주형 변수 '성별'을 [0, 1] 숫자로 변환하는 sklearn 클래스는?",
        options: ["LabelEncoder", "StandardScaler", "MinMaxScaler", "Normalizer"],
        answerIdx: 0,
        explanation: "LabelEncoder는 범주형 문자열을 정수로 변환합니다."
      },
      {
        round: 3,
        context: "수치형 피처의 평균을 0, 표준편차를 1로 변환하는 스케일러는?",
        options: ["StandardScaler", "MinMaxScaler", "RobustScaler", "LabelEncoder"],
        answerIdx: 0,
        explanation: "StandardScaler는 Z-score 정규화(평균 0, 표준편차 1)를 수행합니다."
      },
      {
        round: 4,
        context: "학습된 모델의 정확도를 계산하는 sklearn 함수는?",
        options: [
          "accuracy_score(y_test, y_pred)",
          "score_accuracy(y_pred, y_test)",
          "precision_score(y_test, y_pred)",
          "model.accuracy(y_test)"
        ],
        answerIdx: 0,
        explanation: "accuracy_score(실제값, 예측값) 순서로 전달합니다."
      },
      {
        round: 5,
        context: "train_acc=0.98, test_acc=0.62일 때 이 모델의 문제는?",
        options: ["과적합(Overfitting)", "과소적합(Underfitting)", "데이터 누수(Leakage)", "클래스 불균형"],
        answerIdx: 0,
        explanation: "훈련 정확도는 높고 테스트 정확도가 낮으면 과적합입니다."
      }
    ],

    designSprint: {
      checklist: [
        { id: "c1", label: "결측치 처리 (fillna 또는 dropna)", patterns: ["fillna|dropna|결측|null|NaN|median|평균|중앙값"] },
        { id: "c2", label: "범주형 인코딩 (LabelEncoder 또는 get_dummies)", patterns: ["LabelEncoder|get_dummies|인코딩|encoding|원핫|one.?hot"] },
        { id: "c3", label: "데이터 분할 (train_test_split)", patterns: ["train_test_split|split|분할|훈련.*테스트|학습.*검증"] },
        { id: "c4", label: "모델 학습 (model.fit)", patterns: ["fit|학습|훈련|train"] },
        { id: "c5", label: "예측 및 평가 (predict, accuracy_score)", patterns: ["predict|accuracy|정확도|평가|score|classification_report"] }
      ]
    }
  },

  {
    id: 4,
    difficulty: 'Associate',
    title: "데이터 전처리와 시각화",
    scenario: "고객 구매 데이터를 불러와 결측치·이상치를 처리하고, 상관관계를 분석하여 시각화하는 전체 흐름을 의사코드로 작성하세요.",

    speedRounds: [
      {
        round: 1,
        context: "IQR 방식으로 이상치를 탐지할 때, 이상치 기준은?",
        options: [
          "Q1 - 1.5*IQR 미만 또는 Q3 + 1.5*IQR 초과",
          "평균 - 2*표준편차 미만",
          "중앙값의 50% 미만",
          "최솟값의 2배 초과"
        ],
        answerIdx: 0,
        explanation: "IQR(Q3-Q1)의 1.5배를 벗어나는 값을 이상치로 판단합니다."
      },
      {
        round: 2,
        context: "pandas에서 컬럼 간 상관계수 행렬을 구하는 메서드는?",
        options: ["df.corr()", "df.correlation()", "df.cov()", "df.relate()"],
        answerIdx: 0,
        explanation: "corr()은 피어슨 상관계수 행렬을 반환합니다."
      },
      {
        round: 3,
        context: "seaborn에서 상관계수 행렬을 색상으로 시각화하는 함수는?",
        options: ["sns.heatmap()", "sns.barplot()", "sns.scatter()", "sns.corrplot()"],
        answerIdx: 0,
        explanation: "heatmap()은 2D 행렬을 색상 강도로 시각화합니다."
      },
      {
        round: 4,
        context: "pandas에서 특정 조건을 만족하는 행만 필터링하는 방법은?",
        options: [
          "df[df['나이'] > 30]",
          "df.filter('나이' > 30)",
          "df.where('나이', 30)",
          "df.select(나이=30)"
        ],
        answerIdx: 0,
        explanation: "불리언 인덱싱으로 조건에 맞는 행만 선택합니다."
      },
      {
        round: 5,
        context: "결측치를 해당 컬럼의 중앙값으로 채우는 코드는?",
        options: [
          "df['col'].fillna(df['col'].median())",
          "df['col'].replace(df['col'].median())",
          "df['col'].dropna(median)",
          "df['col'].set(df['col'].median())"
        ],
        answerIdx: 0,
        explanation: "median()은 중앙값을 반환하고, fillna()로 결측치를 채웁니다."
      }
    ],

    designSprint: {
      checklist: [
        { id: "c1", label: "데이터 로드 (read_csv, read_excel)", patterns: ["read_csv|read_excel|로드|불러|load|import.*data"] },
        { id: "c2", label: "결측치 처리 (fillna, dropna, median, mean)", patterns: ["fillna|dropna|결측|median|mean|중앙값|평균"] },
        { id: "c3", label: "이상치 탐지/처리 (IQR, Q1, Q3)", patterns: ["IQR|이상치|Q1|Q3|사분위|outlier|1\\.5"] },
        { id: "c4", label: "상관관계 분석 (corr)", patterns: ["corr|상관|correlation|피어슨|pearson"] },
        { id: "c5", label: "시각화 (heatmap, plot, 그래프)", patterns: ["heatmap|plot|시각화|그래프|chart|matplotlib|seaborn|sns|plt"] }
      ]
    }
  },

  // ═══════════════════════════════════════════════════════════════
  // PROFESSIONAL (2 퀘스트) — 딥러닝, Keras/TensorFlow 중심
  // ═══════════════════════════════════════════════════════════════
  {
    id: 5,
    difficulty: 'Professional',
    title: "Keras CNN 이미지 분류",
    scenario: "MNIST 손글씨 이미지를 분류하는 CNN 모델을 Keras로 구축하고, 학습 및 평가하는 전체 파이프라인을 의사코드로 작성하세요.",

    speedRounds: [
      {
        round: 1,
        context: "Keras에서 CNN의 핵심 레이어로, 이미지의 공간적 특징을 추출하는 레이어는?",
        options: ["Conv2D", "Dense", "Flatten", "Dropout"],
        answerIdx: 0,
        explanation: "Conv2D는 2D 합성곱 연산으로 이미지의 공간적 패턴을 학습합니다."
      },
      {
        round: 2,
        context: "다중 클래스 분류(10개 숫자)의 출력층 활성화 함수로 적절한 것은?",
        options: ["softmax", "sigmoid", "relu", "tanh"],
        answerIdx: 0,
        explanation: "softmax는 출력을 확률 분포로 변환하여 다중 클래스 분류에 적합합니다."
      },
      {
        round: 3,
        context: "다중 클래스 분류에서 정수 레이블(0~9)을 사용할 때 적절한 손실함수는?",
        options: [
          "sparse_categorical_crossentropy",
          "binary_crossentropy",
          "mean_squared_error",
          "categorical_crossentropy"
        ],
        answerIdx: 0,
        explanation: "정수 레이블에는 sparse_categorical, 원핫 레이블에는 categorical을 사용합니다."
      },
      {
        round: 4,
        context: "학습률을 자동 조절하며 모멘텀도 활용하는 옵티마이저는?",
        options: ["Adam", "SGD", "RMSprop", "Adagrad"],
        answerIdx: 0,
        explanation: "Adam은 모멘텀 + 적응적 학습률을 결합한 옵티마이저입니다."
      },
      {
        round: 5,
        context: "과적합을 방지하기 위해 학습 중 뉴런의 일부를 랜덤하게 비활성화하는 기법은?",
        options: ["Dropout", "BatchNormalization", "L2 정규화", "Early Stopping"],
        answerIdx: 0,
        explanation: "Dropout은 학습 시 지정 비율만큼 뉴런을 무작위로 끕니다."
      }
    ],

    designSprint: {
      checklist: [
        { id: "c1", label: "데이터 로드 및 정규화 (0~1 스케일링)", patterns: ["load|로드|mnist|정규화|normalize|255|스케일"] },
        { id: "c2", label: "CNN 레이어 구성 (Conv2D, MaxPooling2D)", patterns: ["Conv2D|conv|합성곱|MaxPool|풀링"] },
        { id: "c3", label: "Flatten + Dense 출력층", patterns: ["Flatten|flatten|Dense|dense|출력층|완전연결"] },
        { id: "c4", label: "모델 컴파일 (optimizer, loss, metrics)", patterns: ["compile|컴파일|optimizer|loss|손실|adam|crossentropy"] },
        { id: "c5", label: "모델 학습 및 평가 (fit, evaluate)", patterns: ["fit|학습|train|evaluate|평가|epoch|에포크"] }
      ]
    }
  },

  {
    id: 6,
    difficulty: 'Professional',
    title: "Keras 텍스트 감성 분류 (NLP)",
    scenario: "영화 리뷰 텍스트를 입력받아 긍정/부정을 분류하는 LSTM 모델을 Keras로 구축하는 전체 파이프라인을 의사코드로 작성하세요.",

    speedRounds: [
      {
        round: 1,
        context: "텍스트를 숫자 시퀀스로 변환하는 Keras 전처리 도구는?",
        options: ["Tokenizer", "LabelEncoder", "CountVectorizer", "TextProcessor"],
        answerIdx: 0,
        explanation: "Tokenizer는 텍스트를 단어 인덱스 시퀀스로 변환합니다."
      },
      {
        round: 2,
        context: "서로 다른 길이의 시퀀스를 동일 길이로 맞추는 함수는?",
        options: ["pad_sequences", "resize_sequences", "trim_sequences", "align_sequences"],
        answerIdx: 0,
        explanation: "pad_sequences는 짧은 시퀀스에 0을 채워 길이를 통일합니다."
      },
      {
        round: 3,
        context: "단어를 고정 차원 벡터로 변환하는 Keras 레이어는?",
        options: ["Embedding", "Dense", "Conv1D", "Flatten"],
        answerIdx: 0,
        explanation: "Embedding 레이어는 정수 인덱스를 밀집 벡터로 매핑합니다."
      },
      {
        round: 4,
        context: "시퀀스 데이터에서 장기 의존성을 학습할 수 있는 RNN 변형은?",
        options: ["LSTM", "SimpleRNN", "Dense", "Conv1D"],
        answerIdx: 0,
        explanation: "LSTM은 게이트 메커니즘으로 장기 기억을 유지합니다."
      },
      {
        round: 5,
        context: "이진 분류(긍정/부정)의 출력층에 적합한 활성화 함수와 손실함수 조합은?",
        options: [
          "sigmoid + binary_crossentropy",
          "softmax + categorical_crossentropy",
          "relu + mean_squared_error",
          "tanh + hinge"
        ],
        answerIdx: 0,
        explanation: "이진 분류에는 sigmoid(0~1 출력) + binary_crossentropy를 사용합니다."
      }
    ],

    designSprint: {
      checklist: [
        { id: "c1", label: "텍스트 토크나이징 (Tokenizer)", patterns: ["Tokenizer|토크나이|tokenize|texts_to_sequences|단어.*인덱스"] },
        { id: "c2", label: "시퀀스 패딩 (pad_sequences)", patterns: ["pad_sequences|패딩|padding|길이.*통일|maxlen"] },
        { id: "c3", label: "임베딩 레이어 (Embedding)", patterns: ["Embedding|임베딩|embedding|벡터.*변환"] },
        { id: "c4", label: "LSTM 또는 RNN 레이어", patterns: ["LSTM|lstm|RNN|rnn|순환|recurrent|GRU|gru"] },
        { id: "c5", label: "이진 분류 출력 (sigmoid + binary_crossentropy)", patterns: ["sigmoid|binary|이진|긍정.*부정|감성|crossentropy"] }
      ]
    }
  }
];
