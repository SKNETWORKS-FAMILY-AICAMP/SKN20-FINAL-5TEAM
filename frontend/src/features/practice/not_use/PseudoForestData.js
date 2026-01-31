/**
 * Pseudo Forest 10 Stages x 4 Steps Data Design
 * 
 * [수정일: 2026-01-28] 4단계(파이썬 실습) 및 종합 평가 데이터(finalAppraisal) 추가 완료
 */
const forestGameData = [
    {
        stageId: 1,
        character: {
            name: "감자쥬 (카피바라)",
            image: "/image/forest/char_gamjaju.png",
            hoverImage: "/image/forest/char_gamjaju_happy.png"
        },
        dialogue: "뭐~ 되면 됐쥬. 마을 입구 공지판이 너무 복잡해유. 똑같은 글은 한 번만 보이게 정리해주면 고맙겠쥬~",
        steps: [
            {
                type: "subjective",
                question: "1. 중복된 게시글을 어떻게 찾아내고 제거할지 기본적인 아이디어를 말해보세요!",
                evalCriteria: {
                    insightKeywords: ["중복", "제거", "검사", "확인"],
                    structureKeywords: ["비교", "하나씩", "반복"],
                    precisionKeywords: ["삭제", "지우기"]
                }
            },
            {
                type: "objective",
                question: "2. 수만 개의 게시글이 있을 때, 가장 빠르게 중복을 체크할 수 있는 자료구조는 무엇일까요?",
                options: ["배열 (Array)", "집합 (Set)", "연결 리스트 (Linked List)", "스택 (Stack)"],
                correctIndex: 1,
                explanation: "Set은 데이터의 존재 여부를 평균적으로 O(1) 시간에 확인할 수 있어 매우 효율적입니다."
            },
            {
                type: "subjective",
                question: "3. 만약 '글을 쓴 순서'를 그대로 유지하면서 중복만 제거해야 한다면, 로직에 무엇을 추가해야 할까요?",
                evalCriteria: {
                    insightKeywords: ["순서", "유지", "처음"],
                    structureKeywords: ["새로운", "배열", "담기"],
                    precisionKeywords: ["결과", "그대로"]
                }
            },
            {
                type: "python-fill",
                question: "4. 파이썬의 set을 사용하여 리스트의 중복을 제거하는 코드를 완성해보세유!",
                codeSnippet: "def clean_board(posts):\n    # 중복을 제거한 결과를 리스트로 반환\n    return {{blank}}(set(posts))",
                blanks: ["list"],
                duckEncouragement: "리스트를 집합(set)으로 변환하면 중복이 싹 사라지쥬!"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "중복 제거의 핵심인 Set 활용법을 완벽히 이해하셨군유! 마을 게시판이 아주 깨끗해졌슈.",
                mid: "데이터를 정리하는 감각이 좋으시구먼유. 순서 유지 조건도 한 번 더 고민해보셔유.",
                low: "중복을 찾는 건 프로그래밍의 기초쥬! 차근차근 다시 해보자구유."
            },
            insightMentions: { high: "효율적인 자료구조 선택 능력이 탁월해유.", low: "데이터의 특징을 파악하는 연습이 필요해유." },
            structureMentions: { high: "조건에 맞는 논리 구성이 아주 탄탄해유.", low: "처리 순서를 좀 더 명확히 기술하면 좋겠슈." },
            precisionMentions: { high: "파이썬 문법 이해도가 아주 높으시구먼유.", low: "함수와 타입 변환에 익숙해지셔야겠슈." }
        }
    },
    {
        stageId: 2,
        character: {
            name: "두부 (강아지)",
            image: "/image/forest/char_dubu.png",
            hoverImage: "/image/forest/char_dubu_happy.png"
        },
        dialogue: "이장님, 날씨에 따라 산책 루트가 달라지면 더 편할 것 같아요! 비 오는 날엔 미끄러운 곳을 피하고 싶거든요.",
        steps: [
            {
                type: "subjective",
                question: "1. 맑은 날씨일 때, 단순히 '거리'만 고려하여 최단 경로를 찾는 로직을 어떻게 설계할까요?",
                evalCriteria: {
                    insightKeywords: ["맑음", "거리", "최소"],
                    structureKeywords: ["비교", "가장 짧은"],
                    precisionKeywords: ["결과", "ID"]
                }
            },
            {
                type: "subjective",
                question: "2. 비 오는 날씨에는 '미끄러움' 수치를 1순위로 고려해야 합니다. 어떤 조건문이 추가되어야 할까요?",
                evalCriteria: {
                    insightKeywords: ["비", "미끄러움", "우선"],
                    structureKeywords: ["만약", "if", "조건"],
                    precisionKeywords: ["비교", "최소"]
                }
            },
            {
                type: "objective",
                question: "3. 미끄러움 수치가 동일한 두 경로가 있다면, 최종적으로 무엇을 기준으로 선택해야 할까요?",
                options: ["도착 시간", "경로의 아름다움", "경로의 거리", "주변 상점 수"],
                correctIndex: 2,
                explanation: "1순위 조건이 동일할 때는 거리와 같은 2순위 조건을 통해 결정을 내리는 '타이브레이크' 로직이 필요합니다."
            },
            {
                type: "python-fill",
                question: "4. 여러 경로 중 거리가 최소인 값을 찾아내는 파이썬 코드를 완성해봅시다!",
                codeSnippet: "min_dist = float('inf')\nfor d in distances:\n    if d < min_dist:\n        min_dist = {{blank}}",
                blanks: ["d"],
                duckEncouragement: "현재까지 찾은 가장 짧은 거리(min_dist)보다 더 짧은 게 나오면 바꿔줘야쥬!"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "다양한 조건을 고려한 경로 탐색 능력이 대단하셔유! 두부가 안전하게 산책하겠구먼유.",
                mid: "조건부 검색 로직을 잘 이해하고 계셔유. 우선순위 결정 기준을 좀 더 명확히 해보셔유.",
                low: "최솟값을 찾는 건 아주 중요한 기본이쥬. 반복문과 조건문을 더 연습해봅시다유."
            },
            insightMentions: { high: "문제 상황에 따른 변수 설정이 아주 똑똑해유.", low: "우선순위의 개념을 잡는 게 중요해유." },
            structureMentions: { high: "이중 조건 로직을 깔끔하게 구성하셨네유.", low: "예외 상황에 대한 처리가 조금 아쉬워유." },
            precisionMentions: { high: "단순 비교 로직 구현이 아주 정확해유.", low: "변수 초기화와 비교 대상을 잘 확인하셔유." }
        }
    },
    {
        stageId: 3,
        character: {
            name: "유리 (고양이)",
            image: "/image/forest/char_yuri.png",
            hoverImage: "/image/forest/char_yuri_happy.png"
        },
        dialogue: "마을 창고가 엉망이에유. 물건들을 가나다 순서대로 정리하고 싶은데, 어떻게 하면 빠를까유?",
        steps: [
            {
                type: "subjective",
                question: "1. 뒤죽박죽인 물건 리스트를 정렬하기 위한 가장 간단한 방법(알고리즘)을 설명해보세요.",
                evalCriteria: {
                    insightKeywords: ["정렬", "순서", "비교"],
                    structureKeywords: ["버블", "선택", "하나씩"],
                    precisionKeywords: ["오름차순", "가나다"]
                }
            },
            {
                type: "objective",
                question: "2. 이미 정렬된 데이터에 새로운 물건 하나가 들어왔을 때, 가장 효율적인 정렬 방식은?",
                options: ["전체 다시 정렬", "삽입 정렬 (Insertion Sort)", "무시하기", "거꾸로 정렬"],
                correctIndex: 1,
                explanation: "삽입 정렬은 거의 정렬된 데이터에 새 요소를 넣을 때 매우 효율적입니다."
            },
            {
                type: "subjective",
                question: "3. 물건 이름이 똑같을 경우, '유통기한'이 짧은 것부터 앞에 두려면 조건문에 무엇을 넣어야 할까요?",
                evalCriteria: {
                    insightKeywords: ["동일", "유통기한", "우선"],
                    structureKeywords: ["비교", "조건 추가"],
                    precisionKeywords: ["날짜", "작은"]
                }
            },
            {
                type: "python-fill",
                question: "4. 간단한 버블 정렬의 비교문을 완성해봅시다. 가나다 순(오름차순)이 되게 하려면?",
                codeSnippet: "if items[j] {{blank}} items[j+1]:\n    items[j], items[j+1] = items[j+1], items[j]",
                blanks: [">"],
                duckEncouragement: "앞에 게 뒤에 것보다 더 크면(>) 자리를 바꿔줘야 정렬이 되겠쥬?"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "창고지기 자격이 충분하셔유! 정렬 알고리즘의 원리를 아주 잘 꿰뚫고 계시네유.",
                mid: "기본적인 정렬 로직은 아시는구먼유. 상황에 따른 효율적인 알고리즘 선택을 공부해봐유.",
                low: "물건들이 아직 뒤죽박죽이에유. 비교와 교체의 원리를 다시 생각해보셔유."
            },
            insightMentions: { high: "정렬 방식에 따른 시간 복잡도를 잘 이해하고 있슈.", low: "데이터가 많아질 때를 대비한 해결책이 필요해유." },
            structureMentions: { high: "조건에 의한 분기 처리가 매우 섬세해유.", low: "불필요한 반복을 줄이는 방법을 고민해보셔유." },
            precisionMentions: { high: "파이썬의 swap 문법을 아주 잘 활용하시네유.", low: "비교 연산자의 방향에 주의하셔야겠슈." }
        }
    },
    {
        stageId: 4,
        character: {
            name: "모래 (햄스터)",
            image: "/image/forest/char_morae.png",
            hoverImage: "/image/forest/char_morae_happy.png"
        },
        dialogue: "겨울나기용 해바라기씨를 모아야 해유. 마을에 있는 여러 씨앗 주머니 중 가장 무거운 걸 찾고 싶어유!",
        steps: [
            {
                type: "subjective",
                question: "1. 주머니들을 하나씩 확인하면서 지금까지 본 것 중 가장 무거운 것을 기억하는 로직을 써보세요.",
                evalCriteria: {
                    insightKeywords: ["최대값", "비교", "기억"],
                    structureKeywords: ["반복", "변수", "교체"],
                    precisionKeywords: ["무게", "갱신"]
                }
            },
            {
                type: "objective",
                question: "2. 만약 씨앗 주머니들이 이미 '무게 순'으로 정렬되어 있다면, 가장 무거운 것을 찾는 데 걸리는 시간은?",
                options: ["매번 다름", "비례해서 늘어남 (O(n))", "즉시 확인 가능 (O(1))", "비교 불가능"],
                correctIndex: 2,
                explanation: "정렬되어 있다면 첫 번째나 마지막 요소만 확인하면 되므로 즉시 찾을 수 있습니다."
            },
            {
                type: "subjective",
                question: "3. 가장 무거운 주머니 TOP 3를 뽑으려면 어떤 방식으로 로직을 확장할 수 있을까요?",
                evalCriteria: {
                    insightKeywords: ["상위", "3개", "순위"],
                    structureKeywords: ["배열", "정렬 후", "슬라이스"],
                    precisionKeywords: ["결과", "세 개"]
                }
            },
            {
                type: "python-fill",
                question: "4. 최댓값을 갱신해 나가는 파이썬 코드를 완성해봅시다유!",
                codeSnippet: "max_w = 0\nfor w in weights:\n    if w > {{blank}}:\n        max_w = w",
                blanks: ["max_w"],
                duckEncouragement: "새로운 무게가 지금까지의 최대값(max_w)보다 크면 주머니를 갈아치워야쥬!"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "모래가 올겨울 아주 배부르게 지내겠어유! 탐색 로직의 달인이시구먼유.",
                mid: "최대값 찾기는 식은 죽 먹기쥬? 상위 여러 개를 뽑는 법도 더 연습해보셔유.",
                low: "가장 큰 걸 찾는 건 모든 비교의 시작이에유. 반복문을 차근차근 뜯어보자구유."
            },
            insightMentions: { high: "데이터의 정렬 상태를 활용할 줄 아는군요.", low: "전수 조사 말고 더 빠른 방법이 있을지 고민해봐유." },
            structureMentions: { high: "갱신 로직이 아주 깔끔하고 군더더기 없네유.", low: "변수 선언과 할당 순서를 잘 지켜주셔유." },
            precisionMentions: { high: "조건식 작성이 아주 정확하고 완벽해유.", low: "비교 대상이 무엇인지 명확히 해야겠슈." }
        }
    },
    {
        stageId: 5,
        character: {
            name: "밤송이 (고슴도치)",
            image: "/image/forest/char_bamsong.png",
            hoverImage: "/image/forest/char_bamsong_happy.png"
        },
        dialogue: "밤송이가 너무 많아서 바구니에 다 안 들어가유. 가치는 높고 무게는 가벼운 것부터 담으려면 어떡하쥬?",
        steps: [
            {
                type: "subjective",
                question: "1. 각 밤송이의 '무게 대비 가치'를 계산하여 우선순위를 정하는 로직을 설명해보세요.",
                evalCriteria: {
                    insightKeywords: ["효율", "비율", "가중치"],
                    structureKeywords: ["나누기", "계산", "정렬"],
                    precisionKeywords: ["무게", "가치"]
                }
            },
            {
                type: "objective",
                question: "2. 이런 식으로 현재 상황에서 최선의 선택을 계속해 나가는 알고리즘 방식을 무엇이라 할까요?",
                options: ["그리디 (Greedy) 알고리즘", "브루트 포스 (Brute Force)", "완전 탐색", "안전 탐색"],
                correctIndex: 0,
                explanation: "매 순간 최적이라고 생각되는 것을 선택해 나가는 방식이 그리디 알고리즘입니다."
            },
            {
                type: "subjective",
                question: "3. 바구니 무게 제한이 10kg일 때, 더 이상 담을 수 없는지 확인하는 조건문을 작성해보세요.",
                evalCriteria: {
                    insightKeywords: ["제한", "초과", "누적"],
                    structureKeywords: ["합계", "if", "10"],
                    precisionKeywords: ["중단", "멈춤"]
                }
            },
            {
                type: "python-fill",
                question: "4. 무게 합계가 10kg을 넘지 않을 때만 바구니에 담는 코드를 완성해보세유!",
                codeSnippet: "if total_weight + item_w <= {{blank}}:\n    basket.append(item)\n    total_weight += item_w",
                blanks: ["10"],
                duckEncouragement: "바구니가 터지면 안 되니까 10kg 제한을 꼭 체크해줘야쥬!"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "가장 가치 있는 바구니를 만드셨군유! 그리디 전략을 아주 잘 활용하셨슈.",
                mid: "효율성 중심의 사고방식이 좋으시구먼유. 배낭 문제의 다른 유형도 찾아보셔유.",
                low: "욕심쟁이 알고리즘(그리디)은 단순하지만 강력하쥬! 기본 원리를 더 익혀봐유."
            },
            insightMentions: { high: "단위 무게당 가치라는 개념을 정확히 짚었슈.", low: "단순히 하나만 보고 결정하면 손해를 볼 수 있슈." },
            structureMentions: { high: "누적 합산과 제한 조건 로직이 매우 정교해유.", low: "조건문의 위치가 바뀌면 결과도 달라진다는 걸 기억해유." },
            precisionMentions: { high: "복합 대입 연산자(+=) 사용이 아주 익숙하시네유.", low: "숫자 상수를 하드코딩하기보다 변수를 써보셔유." }
        }
    },
    {
        stageId: 6,
        character: {
            name: "바나나 (원숭이)",
            image: "/image/forest/char_banana.png",
            hoverImage: "/image/forest/char_banana_happy.png"
        },
        dialogue: "바나나가 높은 곳에 있슈. 사다리를 타고 올라가야 하는디, 아래에서부터 차근차근 기록하며 올라가볼까유?",
        steps: [
            {
                type: "subjective",
                question: "1. 1단부터 N단까지 올라가는 모든 경로를 기록하기 위해 적합한 자료구조와 그 이유를 말해보세요.",
                evalCriteria: {
                    insightKeywords: ["경로", "기록", "역순"],
                    structureKeywords: ["스택", "배열", "히스토리"],
                    precisionKeywords: ["추가", "마지막"]
                }
            },
            {
                type: "objective",
                question: "2. '가장 최근에 확인한 지점'으로 돌아가서 다른 길을 찾아야 할 때 유용한 원칙은?",
                options: ["FIFO (First In First Out)", "LIFO (Last In First Out)", "Random Access", "Priority Only"],
                correctIndex: 1,
                explanation: "마지막에 들어온 것을 먼저 처리하는 LIFO(Stack) 방식이 되돌아가기에 적합합니다."
            },
            {
                type: "subjective",
                question: "3. 사다리가 부러진 칸을 피해서 끝까지 도달했는지 확인하는 완수 조건 로직을 작성해보세요.",
                evalCriteria: {
                    insightKeywords: ["장애물", "피하기", "도착"],
                    structureKeywords: ["조건문", "값 체크", "목표"],
                    precisionKeywords: ["성공", "true"]
                }
            },
            {
                type: "python-fill",
                question: "4. 경로 리스트(스택)에 현재 위치를 추가하는 파이썬 메서드를 써보셔유!",
                codeSnippet: "path.{{blank}}(current_step)\n# 만약 되돌아가야 한다면?\npath.pop()",
                blanks: ["append"],
                duckEncouragement: "스택의 맨 뒤에 데이터를 넣을 때는 append 메서드를 쓴다꽥!"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "바나나 따기 장인이시네유! 스택을 이용한 경로 추적 실력이 대단하셔유.",
                mid: "되돌아가기(Backtracking)의 기초인 스택을 잘 다루시는구먼유.",
                low: "차곡차곡 쌓고 뒤에서부터 빼는 원리를 다시 한 번 생각해보자구유."
            },
            insightMentions: { high: "LIFO 구조의 핵심 활용 방안을 정확히 알구 있슈.", low: "먼저 들어온 게 먼저 나가면 경로가 꼬일 수 있슈." },
            structureMentions: { high: "추가와 삭제의 균형을 맞춘 로직이 매우 안정적이에유.", low: "데이터를 쌓기만 하면 메모리가 터질지도 몰라유." },
            precisionMentions: { high: "리스트 메서드 활용이 아주 능숙하고 정확해유.", low: "pop과 append의 짝을 잘 맞춰주셔야 해유." }
        }
    },
    {
        stageId: 7,
        character: {
            name: "라임 (개구리)",
            image: "/image/forest/char_lime.png",
            hoverImage: "/image/forest/char_lime_happy.png"
        },
        dialogue: "연못에 붕어와 잉어가 살고 있슈. 그물을 던졌을 때 어떤 물고기가 잡힐지 미리 예측해볼 수 있을까유?",
        steps: [
            {
                type: "subjective",
                question: "1. 연못의 총 물고기 수 대비 붕어의 비율을 계산하여 '잡힐 확률'을 출력하는 로직을 써보세요.",
                evalCriteria: {
                    insightKeywords: ["확률", "비율", "전체"],
                    structureKeywords: ["나누기", "카운트"],
                    precisionKeywords: ["결과", "%"]
                }
            },
            {
                type: "objective",
                question: "2. 컴퓨터에서 0.0부터 1.0 사이의 임의의 숫자를 생성하여 잡기 성공 여부를 판단할 때 사용하는 함수는?",
                options: ["Math.floor", "Math.random", "Math.ceil", "Math.abs"],
                correctIndex: 1,
                explanation: "Math.random()은 0 이상 1 미만의 부동 소수점 난수를 반환합니다."
            },
            {
                type: "subjective",
                question: "3. 연속으로 3번 잡기에 성공했을 때 특별한 보상을 주는 카운팅 로직을 설계해보세요.",
                evalCriteria: {
                    insightKeywords: ["연속", "보상", "누적"],
                    structureKeywords: ["변수 + 1", "if", "== 3"],
                    precisionKeywords: ["초기화", "성공"]
                }
            },
            {
                type: "python-fill",
                question: "4. 잡힐 확률이 50%(0.5)일 때 성공 여부를 결정하는 조건식을 완성해보세유!",
                codeSnippet: "import random\nif random.random() < {{blank}}:\n    print('붕어를 잡았다!')",
                blanks: ["0.5"],
                duckEncouragement: "0부터 1 사이의 난수가 0.5보다 작을 확률이 딱 절반이쥬!"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "연못의 신이 내린 점쟁이시군유! 확률과 통계 논리가 아주 정확해유.",
                mid: "랜덤한 상황을 제어하는 법을 알고 계시구먼유. 연속 성공 로직도 잘 만드셨슈.",
                low: "운에 맡기기보다 수학적인 확률로 접근하는 연습을 더 해보자구유."
            },
            insightMentions: { high: "난수를 활용한 시뮬레이션 감각이 아주 뛰어나네유.", low: "전체 집합의 크기를 고려하는 게 확률의 시작이에유." },
            structureMentions: { high: "조건부 누적(카운팅) 로직 설계가 매우 깔끔해유.", low: "성공했을 때와 실패했을 때의 변수 처리를 확인해봐유." },
            precisionMentions: { high: "파이썬 random 모듈 이해도가 아주 훌륭하시네유.", low: "비교 연산의 기준 값을 설정할 때 신중하셔야 해유." }
        }
    },
    {
        stageId: 8,
        character: {
            name: "감자쥬 (카피바라)",
            image: "/image/forest/char_gamjaju.png",
            hoverImage: "/image/forest/char_gamjaju_happy.png"
        },
        dialogue: "야시장에 전구를 켜야 해유. 전력이 부족해서 한 번에 3개만 켤 수 있는디, 이걸 어떻게 순환시킬까유?",
        steps: [
            {
                type: "subjective",
                question: "1. 전구 10개를 3개씩 끊어서 순서대로(1-3, 4-6...) 켜는 로직의 핵심 아이디어를 써보세요.",
                evalCriteria: {
                    insightKeywords: ["순환", "범위", "인덱스"],
                    structureKeywords: ["나머지 연산", "모듈로", "더하기"],
                    precisionKeywords: ["시작", "끝"]
                }
            },
            {
                type: "objective",
                question: "2. 리스트의 인덱스가 끝에 도달했을 때 다시 처음(0)으로 부드럽게 돌아가게 만드는 연산자는?",
                options: ["+", "*", "% (Modulo)", "**"],
                correctIndex: 2,
                explanation: "나머지 연산자(%)를 사용하면 값이 특정 범위 내에서 순환하게 만들 수 있습니다."
            },
            {
                type: "subjective",
                question: "3. 전구가 모두 꺼졌을 때 '전체 소등' 상태를 확인하고 시스템을 중단하는 로직을 작성해보세요.",
                evalCriteria: {
                    insightKeywords: ["모두", "상태 확인", "확인"],
                    structureKeywords: ["반복문", "전부", "체크"],
                    precisionKeywords: ["false", "꺼짐"]
                }
            },
            {
                type: "python-fill",
                question: "4. 인덱스를 0부터 9까지 계속 순환하게 만드는 코드를 완성해봅시다유!",
                codeSnippet: "for i in range(100):\n    current_light = i % {{blank}}\n    print(f'{current_light}번 전구 점등')",
                blanks: ["10"],
                duckEncouragement: "10으로 나눈 나머지(%)를 구하면 0~9 사이에서 뱅뱅 돌게 되쥬!"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "야시장의 불빛이 이장님 덕분에 영원히 빛나겠슈! 순환 로직의 정석이시구먼유.",
                mid: "나머지 연산의 묘미를 아시는구먼유. 일정한 간격으로 끊는 로직도 연구해봐유.",
                low: "끝에서 다시 처음으로 가는 건 프로그래밍의 마법이쥬! % 연산자를 정복해봐유."
            },
            insightMentions: { high: "모듈로 연산의 실용적 가치를 아주 정확히 파악했슈.", low: "인덱스 범위를 벗어나지 않게 주의하는 게 핵심이에유." },
            structureMentions: { high: "루프 안에서 상태를 검증하는 흐름이 매우 탄탄해유.", low: "모든 경우의 수를 체크하는 효율적인 방법을 찾아봐유." },
            precisionMentions: { high: "나머지 연산 수식 적용이 아주 깔끔하고 완벽해유.", low: "나누는 수(제수) 크기에 따라 범위가 결정된다는 걸 기억해유." }
        }
    },
    {
        stageId: 9,
        character: {
            name: "두부 (강아지)",
            image: "/image/forest/char_dubu.png",
            hoverImage: "/image/forest/char_dubu_happy.png"
        },
        dialogue: "잃어버린 뼈다귀를 찾고 싶어유. 마을 지도를 따라서 빠트리는 곳 없이 전부 뒤져보려면 어떻게 해야 할까유?",
        steps: [
            {
                type: "subjective",
                question: "1. 만나는 갈림길마다 끝까지 가본 뒤 돌아와서 다른 길을 찾는 탐색 방식을 설명해보세요.",
                evalCriteria: {
                    insightKeywords: ["깊이", "끝까지", "되돌아오기"],
                    structureKeywords: ["DFS", "재귀", "스택"],
                    precisionKeywords: ["방문", "체크"]
                }
            },
            {
                type: "subjective",
                question: "2. 반대로 내 위치에서 가장 가까운 곳부터 넓게 퍼져나가며 찾는 방식은 무엇일까요?",
                evalCriteria: {
                    insightKeywords: ["가까운", "넓게", "순서대로"],
                    structureKeywords: ["BFS", "큐", "레벨"],
                    precisionKeywords: ["차례로", "확장"]
                }
            },
            {
                type: "objective",
                question: "3. 한 번 가본 곳을 다시 가지 않기 위해 꼭 기록해야 하는 정보는 무엇일까요?",
                options: ["방문 여부 (Visited)", "이동 거리", "주변 풍경", "현재 시간"],
                correctIndex: 0,
                explanation: "이미 방문한 지점을 표시해야 무한 루프에 빠지지 않고 모든 곳을 탐색할 수 있습니다."
            },
            {
                type: "python-fill",
                question: "4. 방문한 지점을 기록하는 set(집합)을 활용하는 코드를 완성해보세유!",
                codeSnippet: "if node not in {{blank}}:\n    print('처음 온 곳이유!')\n    visited.add(node)",
                blanks: [["visited", "checked", "seen", "visited_nodes"]],
                duckEncouragement: "이미 왔던 곳인지 visited 리스트나 집합에서 꼭 확인해야쥬!"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "뼈다귀 수색 대장이시군유! DFS와 BFS의 차이를 완벽히 꿰뚫고 계셔유.",
                mid: "마을 지도를 읽는 눈이 좋으시구먼유. 방문 체크의 중요성을 잊지 마셔유.",
                low: "길을 잃지 않으려면 어디를 갔다 왔는지 기록하는 게 제일 중요해유!"
            },
            insightMentions: { high: "상황에 맞는 탐색 우선순위(깊이vs너비) 결정이 훌륭해유.", low: "무한 루프에 빠지지 않는 구조적 설계가 필요해유." },
            structureMentions: { high: "재귀적 사고와 큐 활용 능력이 아주 돋보이네유.", low: "데이터를 넣고 빼는 순서가 탐색 방향을 결정해유." },
            precisionMentions: { high: "멤버십 연산자(in) 활용이 매우 신속하고 정확해유.", low: "변수가 선언된 위치(스코프)를 잘 확인해주셔야겠슈." }
        }
    },
    {
        stageId: 10,
        character: {
            name: "라임 (대현자)",
            image: "/image/forest/char_lime.png",
            hoverImage: "/image/forest/char_lime_happy.png"
        },
        dialogue: "훌륭해유! 마지막으로 마을의 7개 구역을 최소한의 도로 길이로 모두 연결하는 마법의 설계를 보여주셔유.",
        steps: [
            {
                type: "subjective",
                question: "1. 모든 점을 연결하면서 사이클(순환)이 생기지 않게 하는 '나무' 구조의 특징을 설명해보세요.",
                evalCriteria: {
                    insightKeywords: ["연결", "사이클 없음", "최소"],
                    structureKeywords: ["간선", "노드", "N-1"],
                    precisionKeywords: ["신장 트리", "Tree"]
                }
            },
            {
                type: "subjective",
                question: "2. 가장 짧은 길부터 하나씩 선택하되, 연결했을 때 순환이 생기면 버리는 방식의 아이디어를 써보세요.",
                evalCriteria: {
                    insightKeywords: ["짧은", "선택", "순환 방지"],
                    structureKeywords: ["크루스칼", "오름차순", "정렬 후"],
                    precisionKeywords: ["연결", "성공"]
                }
            },
            {
                type: "objective",
                question: "3. 마을의 모든 집을 가장 효율적으로 연결했을 때, 이 구조를 부르는 용어는?",
                options: ["최단 경로", "최소 신장 트리 (MST)", "완전 그래프", "이분 그래프"],
                correctIndex: 1,
                explanation: "모든 정점을 최소 비용으로 연결한, 사이클이 없는 그래프를 최소 신장 트리라고 합니다."
            },
            {
                type: "python-fill",
                question: "4. 두 집이 아직 연결되지 않았다면 합치는(Union) 로직을 완성해봅시다유!",
                codeSnippet: "if find(house1) != find(house2):\n    {{blank}}(house1, house2)\n    total_cost += cost",
                blanks: ["union"],
                duckEncouragement: "뿌리가 다른(연결 안 된) 두 집을 하나로 합쳐주는 union 함수가 필요해유!"
            }
        ],
        finalAppraisal: {
            overallSummary: {
                high: "이제 완벽한 이장님이자 대현자시군유! 마을 전체를 아우르는 최적의 설계를 마치셨슈.",
                mid: "복잡한 그래프 논리도 척척 풀어내시는구먼유. 네트워크 최적화의 대가이셔유.",
                low: "최소 신장 트리는 좀 어렵지유? 짧은 것부터 잇는 원리를 다시 음미해봐유."
            },
            insightMentions: { high: "전체 시스템의 연결 구조를 바라보는 시야가 매우 넓어유.", low: "사이클이 생기면 안 된다는 점을 꼭 명심해야 해유." },
            structureMentions: { high: "분할 정복 및 Union-Find 로직 이해가 매우 깊어유.", low: "작은 조각들을 합쳐 큰 그림을 그리는 법을 더 익혀봐유." },
            precisionMentions: { high: "고급 알고리즘의 함수명과 역할을 아주 정확히 아시네유.", low: "비용을 누적하고 상태를 갱신하는 타이밍을 잘 보셔유." }
        }
    }
];

export default forestGameData;
