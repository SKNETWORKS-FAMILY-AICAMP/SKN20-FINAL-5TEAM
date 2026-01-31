/**
 * Pseudo Forest AI Engineer 10 Stages Data Design
 * [수정일: 2026-01-29] 초보 AI 엔지니어 타겟 커리큘럼 (전체 스테이지 완성본)
 * 
 * 정제되지 않은 데이터에서 시작하여 모델의 추론(Inference)까지 이어지는
 * 엔드투엔드 AI 개발 파이프라인을 의사코드 숲의 테마로 구성했습니다.
 */
const forestGameData = [
    {
        stageId: 1,
        character: {
            name: "너굴 부장 (CEO)",
            image: "/image/forest/ceo_neogul.png",
            hoverImage: "/image/forest/ceo_neogul_happy.png"
        },
        dialogue: "김 사원, 마을 버섯 무게 데이터에 999kg 같은 말도 안 되는 수치가 섞여 있구리. 이런 '이상치'를 어떻게 걸러낼지 로직을 짜보게나!",
        steps: [
            {
                type: "subjective",
                question: "1. 데이터에서 평균이나 중앙값보다 비정상적으로 크거나 작은 값을 걸러내기 위한 의사코드를 작성해보세요.",
                evalCriteria: {
                    insightKeywords: ["이상치", "임계값", "기준"],
                    structureKeywords: ["비교", "필터링", "제외"],
                    precisionKeywords: ["Outlier", "조건문"]
                },
                modelAnswer: "전체 데이터의 평균과 표준편차를 구합니다. 데이터의 값이 (평균 ± 3 * 표준편차) 범위를 벗어나는 경우 이상치로 간주하여 리스트에서 제외하거나 정상 범위의 최댓값/최솟값으로 대체합니다."
            },
            {
                type: "objective",
                question: "2. 이상치를 처리할 때, 무조건 삭제하는 것보다 더 안전한 방법은 무엇일까요?",
                options: ["그냥 0으로 바꾼다", "중앙값(Median)으로 대체한다", "무시하고 학습시킨다", "데이터를 모두 삭제한다"],
                correctIndex: 1,
                explanation: "중앙값은 이상치의 영향을 거의 받지 않기 때문에 비정상적인 데이터를 보정하는 데 유용합니다."
            },
            {
                type: "subjective",
                question: "3. 상자 그림(Box Plot)에서 이상치를 판단하는 기준인 IQR(사분위 범위)의 정의는 무엇일까요?",
                evalCriteria: {
                    insightKeywords: ["3사분위", "1사분위", "차이"],
                    structureKeywords: ["계산", "구간"],
                    precisionKeywords: ["Q3 - Q1", "범위"]
                },
                modelAnswer: "제3사분위수(Q3)에서 제1사분위수(Q1)를 뺀 값입니다. 보통 이 IQR의 1.5배를 넘어서는 구간의 값을 이상치로 판정합니다."
            },
            {
                type: "python-fill",
                question: "4. Pandas를 이용해 특정 열의 이상치를 제거하는 코드를 완성해보세유!",
                codeSnippet: "clean_df = df[df['weight'] {{blank}} 900]",
                blanks: ["<"],
                duckEncouragement: "900kg보다 작은 값들만 남겨야 이상치가 사라지겠쥬?"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "데이터 클렌징 실력이 대단하구리! 이제 깨끗한 데이터로 분석을 시작할 수 있겠어.",
                mid: "이상치 탐지 개념은 잡았구리. IQR 계산법을 조금 더 복잡하게 적용해보게나.",
                low: "데이터가 오염되면 AI도 바보가 된다구리! 필터링 조건을 다시 확인해봐."
            },
            insightMentions: { high: "통계적 기준을 아주 잘 활용하네유.", low: "이상치 판단 기준이 모호해유." },
            structureMentions: { high: "처리 로직이 매우 안정적이에유.", low: "예외 데이터 처리에 더 신경 쓰셔유." },
            precisionMentions: { high: "판다스 문법 활용이 아주 정확해유.", low: "비교 연산자 사용에 주의하셔유." }
        }
    },
    {
        stageId: 2,
        character: {
            name: "두부 대리 (Dog)",
            image: "/image/forest/char_dubu.png",
            hoverImage: "/image/forest/char_dubu_happy.png"
        },
        dialogue: "숲의 지도 일부가 찢어져서 값이 비어 있는 곳(Missing Values)이 있구먼유. 이 구멍들을 어떻게 메워야 할까유?",
        steps: [
            {
                type: "subjective",
                question: "1. 수치형 데이터에서 결측치(NaN)가 발생했을 때, 가장 보편적으로 채워넣는 값은 무엇일까요?",
                evalCriteria: {
                    insightKeywords: ["평균", "중앙값", "채우기"],
                    structureKeywords: ["대체", "계산"],
                    precisionKeywords: ["Mean", "Median"]
                },
                modelAnswer: "해당 컬럼의 전체 평균값(Mean)이나 중앙값(Median)으로 결측치를 대체하여 데이터의 손실을 방지하고 연속성을 유지합니다."
            },
            {
                type: "objective",
                question: "2. 결측치가 너무 많을 때(예: 80% 이상), 가장 알맞은 처리 방법은 무엇일까요?",
                options: ["모두 0으로 채운다", "해당 변수(컬럼)를 삭제한다", "평균으로 채운다", "무작위 숫자를 넣는다"],
                correctIndex: 1,
                explanation: "대부분의 데이터가 유실된 컬럼은 정보를 왜곡할 수 있으므로 삭제하는 것이 분석에 더 도움이 됩니다."
            },
            {
                type: "python-fill",
                question: "3. Pandas에서 결측치를 특정 값으로 채우는 메서드 이름을 적어주세유!",
                codeSnippet: "df['height'] = df['height'].{{blank}}(0)",
                blanks: ["fillna"],
                duckEncouragement: "Fill(채우다) + NA(결측치)를 합친 아주 직관적인 메서드쥬!"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "데이터의 빈틈을 완벽하게 메우셨군유! 이제 탄탄한 분석 기반이 마련됐슈.",
                mid: "결측치 처리 전략이 준수해유. 데이터의 성격에 따라 평균과 중앙값 중 무엇이 나을지 고민해보셔유.",
                low: "값이 비어 있으면 모델이 학습을 못 해유. 채우는 법부터 다시 연습해봅시다유."
            }
        }
    },
    {
        stageId: 3,
        character: {
            name: "유리 과장 (Cat)",
            image: "/image/forest/char_yuri.png",
            hoverImage: "/image/forest/char_yuri_happy.png"
        },
        dialogue: "데이터의 분포를 한눈에 파악하고 싶구랴. 숲의 나무들이 어디에 많이 몰려 있는지 지도를 그려볼 수 있겠나?",
        steps: [
            {
                type: "subjective",
                question: "1. 데이터의 분포(Distribution)를 확인하기 위해 가장 많이 사용하는 막대 그래프 형태의 차트 이름은?",
                evalCriteria: {
                    insightKeywords: ["히스토그램", "분포", "도수"],
                    structureKeywords: ["구간", "막대"],
                    precisionKeywords: ["Histogram", "bins"]
                },
                modelAnswer: "히스토그램(Histogram)입니다. 데이터를 일정 구간(bin)으로 나누어 각 구간에 속하는 데이터의 개수를 막대 형태로 시각화합니다."
            },
            {
                type: "objective",
                question: "2. 두 변수 간의 관계(상관관계)를 점의 형태로 흩뿌려 시각화하는 차트는?",
                options: ["파이 차트", "라인 그래프", "산점도 (Scatter Plot)", "박스 플롯"],
                correctIndex: 2,
                explanation: "산점도는 x축과 y축의 데이터를 점으로 표현하여 두 변수의 경향성을 파악하기에 최적입니다."
            },
            {
                type: "python-fill",
                question: "3. Matplotlib을 이용해 히스토그램을 그리는 함수는 무엇일까유?",
                codeSnippet: "plt.{{blank}}(data['age'], bins=20)\nplt.show()",
                blanks: ["hist"],
                duckEncouragement: "Histogram의 앞 네 글자만 따오면 된다꽥!"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "데이터 시각화의 정석을 보여주셨구랴! 숲의 비경이 한눈에 들어오는구먼.",
                mid: "분포 파악 능력이 좋으시네유. 상관관계 해석에도 신경을 좀 더 써보셔유.",
                low: "그림을 그려야 데이터가 말을 거는 법이지유. 차트 종류부터 익혀봅시다유."
            }
        }
    },
    {
        stageId: 4,
        character: {
            name: "모래 요원 (Hamster)",
            image: "/image/forest/char_morae.png",
            hoverImage: "/image/forest/char_morae_happy.png"
        },
        dialogue: "씨앗들의 무게는 그람(g) 단위인데, 나무 키는 미터(m) 단위라 숫자의 단위가 너무 달라유! 모델이 혼동하지 않게 범위를 맞춰줘유!",
        steps: [
            {
                type: "subjective",
                question: "1. 데이터의 범위를 [0, 1] 사이로 변환하여 단위 차이를 극복하는 기법의 이름은?",
                evalCriteria: {
                    insightKeywords: ["정규화", "최소", "최대"],
                    structureKeywords: ["범위", "스케일링"],
                    precisionKeywords: ["Normalization", "Min-Max"]
                },
                modelAnswer: "정규화(Normalization 또는 Min-Max Scaling)입니다. 데이터를 최솟값 0, 최댓값 1 사이의 일정한 범위로 변환하는 과정입니다."
            },
            {
                type: "objective",
                question: "2. 평균을 0, 표준편차를 1로 만드는 스케일링 방식은 무엇일까요?",
                options: ["로그 변환", "표준화 (Standardization)", "이진화", "절댓값 변환"],
                correctIndex: 1,
                explanation: "표준화는 데이터를 표준정규분포 형태로 변환하여 이상치에 좀 더 유연하게 대응하게 해줍니다."
            },
            {
                type: "python-fill",
                question: "3. Sklearn의 MinMaxScaler를 사용하여 데이터를 변환(Transform)하는 코드를 완성해보세유!",
                codeSnippet: "scaler = MinMaxScaler()\nscaled_data = scaler.{{blank}}_transform(data)",
                blanks: ["fit"],
                duckEncouragement: "학습(Fit)과 변환(Transform)을 동시에 하는 아주 편리한 메서드쥬!"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "데이터의 균형을 아주 잘 잡으셨군유! 모델이 씨앗이랑 나무를 헷갈리지 않겠어유.",
                mid: "스케일링의 필요성을 잘 이해하고 있네유. 정규화와 표준화의 활용 차이를 더 파헤쳐보셔유.",
                low: "숫자 크기가 다르면 편향이 생겨유. 단위 맞추기부터 다시 가르쳐주겠슈."
            }
        }
    },
    {
        stageId: 5,
        character: {
            name: "밤송이 수석 (Hedgehog)",
            image: "/image/forest/char_bamsong.png",
            hoverImage: "/image/forest/char_bamsong_happy.png"
        },
        dialogue: "연습한 데이터로만 시험을 보면 당연히 점수가 잘 나오지 않겠유? 새로운 데이터에도 강한 모델인지 테스트해봐야 해유!",
        steps: [
            {
                type: "subjective",
                question: "1. 훈련 데이터에만 너무 과하게 적응되어 새로운 데이터에 대해 성능이 떨어지는 현상을 무엇이라 하나요?",
                evalCriteria: {
                    insightKeywords: ["과적합", "적응", "훈련"],
                    structureKeywords: ["성능 저하", "일반화"],
                    precisionKeywords: ["Overfitting", "Overfit"]
                },
                modelAnswer: "과적합(Overfitting)입니다. 모델이 훈련 데이터의 노이즈까지 학습하여 실제 환경(새로운 데이터)에서의 일반화 성능이 낮아지는 현상입니다."
            },
            {
                type: "objective",
                question: "2. 데이터를 훈련용(Train)과 테스트용(Test)으로 나누는 가장 보편적인 비율은?",
                options: ["1:9", "5:5", "8:2", "0:10"],
                correctIndex: 2,
                explanation: "일반적으로 80%를 학습에 쓰고 20%를 검증에 사용하는 것이 안정적인 성능 측정을 돕습니다."
            },
            {
                type: "python-fill",
                question: "3. 데이터를 분산시키는 파이썬 함수를 적어주세유!",
                codeSnippet: "X_train, X_test, y_train, y_test = {{blank}}(X, y, test_size=0.2)",
                blanks: ["train_test_split"],
                duckEncouragement: "기차(Train)와 시험(Test) 사이의 밑줄(_)을 잊지 마세유!"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "일반화 능력이 탁월한 모델이 탄생하겠군유! 과적합 감시 능력이 매우 뛰어나셔유.",
                mid: "데이터 분할의 중요성을 잘 아시는구먼유. 검증 데이터(Validation)의 존재도 한 번 알아보셔유.",
                low: "훈련 점수만 믿다간 실전에서 큰일 나유! 데이터를 나누는 법부터 다시 해봅시다유."
            }
        }
    },
    {
        stageId: 6,
        character: {
            name: "바나나 팀장 (Monkey)",
            image: "/image/forest/char_banana.png",
            hoverImage: "/image/forest/char_banana_happy.png"
        },
        dialogue: "나무 높이를 예측했는데 정답이랑 얼마나 차이가 나는지 계산해봐야겠슈. 틀린 만큼 벌점을 주는 로직을 짜보세유!",
        steps: [
            {
                type: "subjective",
                question: "1. 정답과 예측값의 차이를 제곱하여 평균을 낸 벌점 시스템(손실 함수)의 이름은?",
                evalCriteria: {
                    insightKeywords: ["평균", "제곱", "오차"],
                    structureKeywords: ["차이", "계산"],
                    precisionKeywords: ["MSE", "Mean Squared Error"]
                },
                modelAnswer: "평균 제곱 오차(MSE, Mean Squared Error)입니다. 각 데이터의 오차를 제곱하여 평균을 냄으로써 큰 오차에 더 엄격한 벌점을 부여합니다."
            },
            {
                type: "objective",
                question: "2. 분류 문제(개인지 고양이인지)에서 주로 활용하는 손실 함수는?",
                options: ["MSE", "MAE", "교차 엔트로피 (Cross Entropy)", "히스토그램"],
                correctIndex: 2,
                explanation: "교차 엔트로피는 확률 분포의 차이를 측정하여 분류 모델의 정확도를 높이는 데 최적입니다."
            },
            {
                type: "python-fill",
                question: "3. 두 값의 차이의 절댓값을 평균 내는 MAE를 계산할 때 쓰는 함수는 무엇일까유?",
                codeSnippet: "error = np.{{blank}}(np.abs(y_pred - y_true))",
                blanks: ["mean"],
                duckEncouragement: "평균(Mean)을 구하려면 넘파이의 mean 함수를 써야쥬!"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "오차 계산이 아주 정확하시구먼유! 이제 모델이 얼마나 반성해야 할지 명확해졌슈.",
                mid: "손실 함수의 종류를 잘 파악하고 계시네유. 각 함수가 어떤 상황에 유리할지 더 깊게 파보셔유.",
                low: "얼마나 틀렸는지 모르면 고칠 수도 없어유. 오차 계산법부터 다시 배워봅시다유."
            }
        }
    },
    {
        stageId: 7,
        character: {
            name: "라임 과장 (Frog)",
            image: "/image/forest/char_lime.png",
            hoverImage: "/image/forest/char_lime_happy.png"
        },
        dialogue: "연못의 가장 깊은 곳(오차 최소점)을 찾아가야 해유. 미끄러지지 않게 보폭(Learning Rate)을 잘 조절해서 내려가 보세유!",
        steps: [
            {
                type: "subjective",
                question: "1. 기울기를 따라 조금씩 이동하며 오차가 최소가 되는 점을 찾는 알고리즘의 이름은?",
                evalCriteria: {
                    insightKeywords: ["경사하강법", "최소", "기울기"],
                    structureKeywords: ["내려가기", "반복"],
                    precisionKeywords: ["Gradient Descent", "Optimizer"]
                },
                modelAnswer: "경사하강법(Gradient Descent)입니다. 현재 위치에서의 미분값(기울기)을 구해 그 반대 방향으로 가중치를 업데이트하며 최적의 해를 찾아갑니다."
            },
            {
                type: "subjective",
                question: "2. 가중치를 업데이트할 때 보폭이 너무 크면 어떤 문제가 발생할까요?",
                evalCriteria: {
                    insightKeywords: ["발산", "지나침", "최적점"],
                    structureKeywords: ["넘어감", "못 찾음"],
                    precisionKeywords: ["Divergence", "Overshoot"]
                },
                modelAnswer: "학습율(Learning Rate)이 너무 크면 최소점을 지나쳐버리는 '발산(Divergence)' 현상이 발생하여 최적의 오차 지점에 도달하지 못할 수 있습니다."
            },
            {
                type: "python-fill",
                question: "3. 가중치를 업데이트하는 의사코드를 완성해보세유! (lr은 학습율, grad는 기울기)",
                codeSnippet: "W = W - {{blank}} * grad",
                blanks: ["lr"],
                duckEncouragement: "보폭(lr)만큼 기울기 방향으로 곱해서 빼줘야쥬!"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "최적화의 고수이시군유! 연못 바닥까지 아주 부드럽게 안착하셨슈.",
                mid: "경사하강법의 원리를 잘 이해하셨네유. 로컬 미니멈(Local Minimum) 같은 함정도 주의하셔유.",
                low: "너무 성급하면 넘어져유. 기울기를 따라 천천히 내려가는 법부터 다시 해봅시다유."
            }
        }
    },
    {
        stageId: 8,
        character: {
            name: "감자쥬 연구원 (Capybara)",
            image: "/image/forest/char_gamjaju.png",
            hoverImage: "/image/forest/char_gamjaju_happy.png"
        },
        dialogue: "신경망을 통과할 때 일정한 전기 신호(역치)가 넘어야만 다음으로 전달되게 하고 싶어유. 이 '활성화 함수'들을 점검해주셔유!",
        steps: [
            {
                type: "subjective",
                question: "1. 0보다 작은 값은 0으로, 0보다 큰 값은 그대로 통과시키는 가장 대중적인 활성화 함수는?",
                evalCriteria: {
                    insightKeywords: ["ReLU", "0 이하", "그대로"],
                    structureKeywords: ["변환", "양수"],
                    precisionKeywords: ["릴루", "Rectified Linear Unit"]
                },
                modelAnswer: "ReLU(Rectified Linear Unit) 함수입니다. 연산이 빠르고 기울기 소실 문제를 완화하여 딥러닝에서 가장 널리 사용됩니다."
            },
            {
                type: "objective",
                question: "2. 결과를 0과 1 사이의 확률값으로 압축하여 이진 분류에 주로 쓰이는 함수는?",
                options: ["ReLU", "Sigmoid (시그모이드)", "Tanh", "소프트맥스"],
                correctIndex: 1,
                explanation: "시그모이드 함수는 모든 실수를 (0, 1) 사이로 매핑하여 확률 판단에 적합합니다."
            },
            {
                type: "python-fill",
                question: "3. 파이토치에서 ReLU 활성화를 적용하는 메서드 이름을 적어주세유!",
                codeSnippet: "import torch.nn.functional as F\noutput = F.{{blank}}(input_tensor)",
                blanks: ["relu"],
                duckEncouragement: "함수 이름 그대로 소문자로 적으면 된다꽥!"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "신경망의 신호 체계가 아주 건강하군유! 활성화 함수의 특성을 완벽히 꿰뚫고 계셔유.",
                mid: "다양한 활성화 함수를 알고 계시네유. 왜 시그모이드 대신 ReLU를 쓰는지 더 연구해보셔유.",
                low: "신호가 끊기면 안 돼유. 비선형성을 부여하는 활성화 함수의 기본부터 다시 가르쳐줄게유."
            }
        }
    },
    {
        stageId: 9,
        character: {
            name: "너굴 부장 (Reviewer)",
            image: "/image/forest/ceo_neogul.png",
            hoverImage: "/image/forest/ceo_neogul_happy.png"
        },
        dialogue: "데이터 한 바퀴 다 돌았구리! 이제 전체 데이터를 반복해서 학습시키며 성능을 끌어올려보세. 몇 번이나 반복할 텐가구리?",
        steps: [
            {
                type: "subjective",
                question: "1. 전체 데이터셋을 한 번 모두 학습했을 때의 단위를 무엇이라 하나요?",
                evalCriteria: {
                    insightKeywords: ["에폭", "반복", "전체"],
                    structureKeywords: ["단위", "학습 횟수"],
                    precisionKeywords: ["Epoch", "에포크"]
                },
                modelAnswer: "에폭(Epoch)입니다. 학습 시 전체 훈련 데이터셋이 신경망을 한 번 통과한 횟수를 의미합니다."
            },
            {
                type: "objective",
                question: "2. 데이터를 작게 쪼개어 학습을 진행할 때, 그 쪼갠 조각의 크기를 무엇이라 하나요?",
                options: ["에폭 크기", "배치 사이즈 (Batch Size)", "학습율", "데이터 조각"],
                correctIndex: 1,
                explanation: "배치 사이즈는 한 번의 가중치 업데이트를 위해 사용하는 데이터의 묶음 크기입니다."
            },
            {
                type: "python-fill",
                question: "3. 10번의 에폭을 반복하는 루프문을 완성해보세유!",
                codeSnippet: "for epoch in {{blank}}(10):\n    train_model(data)",
                blanks: ["range"],
                duckEncouragement: "파이썬에서 숫자만큼 반복할 때는 range 함수가 최고쥬!"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "끈기 있는 학습이군유! 에폭과 배치의 균형을 아주 잘 잡으셨슈.",
                mid: "반복 학습의 개념을 잘 이해하고 있네유. 배치 사이즈가 너무 작으면 시간이 오래 걸린다는 것도 잊지 마셔유.",
                low: "반복 없이 천재가 될 수 없쥬. 한 번 봐선 몰라유, 여러 번 반복해서 돌려보자구유!"
            }
        }
    },
    {
        stageId: 10,
        character: {
            name: "라임 이사 (Director)",
            image: "/image/forest/char_lime.png",
            hoverImage: "/image/forest/char_lime_happy.png"
        },
        dialogue: "드디어 마지막 업무구리! 완성된 모델에 새로운 데이터를 넣어 결과를 내보내는 '추론' 파이프라인을 점검해보자구리!",
        steps: [
            {
                type: "subjective",
                question: "1. 모델을 서비스에 배포하기 전, 학습 때 썼던 가중치를 고정하고 평가 모드로 전환해야 하는 이유는?",
                evalCriteria: {
                    insightKeywords: ["가중치", "고정", "평가"],
                    structureKeywords: ["드롭아웃", "배치 정규화"],
                    precisionKeywords: ["eval()", "Inference"]
                },
                modelAnswer: "학습 시에만 사용되는 드롭아웃이나 배치 정규화를 평가 모드로 전환하여 일관된 결과를 내기 위해서입니다. 또한 기울기 계산을 멈춰 메모리를 아낍니다."
            },
            {
                type: "python-fill",
                question: "2. 모델을 평가 모드로 바꾸는 메서드 이름을 채워보세유!",
                codeSnippet: "model.{{blank}}()\nwith torch.no_grad():\n    output = model(input_data)",
                blanks: ["eval"],
                duckEncouragement: "Evaluation의 약자를 써서 모델에게 '지금은 시험 시간이야!'라고 알려주세유!"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "이제 완벽한 AI 엔지니어구리! 무인도 AI 연구소를 성공적으로 구축했어.",
                mid: "추론 파이프라인 이해도가 높으시네유. 모델 저장과 로드 방식도 마스터해보게나.",
                low: "마지막 마무리가 중요구리! 평가 모드로 바꾸는 걸 잊으면 결과가 춤을 출 거야."
            }
        }
    }
];

export default forestGameData;