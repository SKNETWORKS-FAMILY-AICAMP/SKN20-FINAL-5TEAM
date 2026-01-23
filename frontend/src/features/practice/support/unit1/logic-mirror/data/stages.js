// 튜토리얼 + 11개 퀘스트 데이터
// [2026-01-24] 정밀 평가 및 파이썬 실행 검증을 위한 validation 데이터 스키마(puzzle_solution, execution) 추가
export const gameData = {
  tutorial: {
    id: 'tutorial',
    name: '🎓 튜토리얼',
    description: '게임 방법을 배워봐요',
    steps: [
      {
        id: 'step1',
        title: '환영합니다! 👋',
        description: 'Logic Mirror는 사고 순서를 훈련하는 게임입니다.',
        instruction: '카드를 드래그해서 올바른 순서로 배치하세요.',
        visual: 'welcome',
        cards: [
          {
            id: 'card1',
            text_ko: '아침에 일어난다',
            icon: '🌅',
            color: 'blue'
          },
          {
            id: 'card2',
            text_ko: '세수를 한다',
            icon: '💧',
            color: 'green'
          },
          {
            id: 'card3',
            text_ko: '아침을 먹는다',
            icon: '🍳',
            color: 'orange'
          }
        ],
        correctOrder: ['card1', 'card2', 'card3'],
        hint: '자연스러운 순서를 생각해보세요!'
      }
    ]
  },

  quests: [
    // LV1 - 순차
    {
      id: 'quest_lv1_01',
      level: 1,
      title: '맛있는 라면 끓이기',
      description: '라면을 끓이는 올바른 순서를 맞춰보세요. 순서가 바뀌면 생라면을 먹어야 할지도 몰라요!',
      logic_type: '순차',
      emoji: '🍜',
      examples: '● IN: 물, 라면, 냄비\n● OUT: 맛있는 라면 완성',
      cards: [
        {
          id: 'b1',
          text_ko: '냄비에 물을 넣고 끓인다',
          text_py: 'boil_water()',
          icon: '💧',
          color: 'blue',
          action: 'boil_water'
        },
        {
          id: 'b2',
          text_ko: '물이 끓으면 면과 스프를 넣는다',
          text_py: 'put_ingredients()',
          icon: '🍜',
          color: 'purple',
          action: 'add_ramen'
        },
        {
          id: 'b3',
          text_ko: '3분 뒤 맛있게 먹는다',
          text_py: 'eat_ramen()',
          icon: '😋',
          color: 'orange',
          action: 'eat'
        }
      ],
      correctSequence: ['b1', 'b2', 'b3'],
      validation: {
        puzzle_solution: [
          { id: 'b1', indent: 0 },
          { id: 'b2', indent: 0 },
          { id: 'b3', indent: 0 }
        ],
        execution: {
          function_name: "cook_ramen",
          test_cases: [
            { input: "", expected: "'None'", type: "public", description: "라면을 정상적으로 끓이는지 확인" }
          ]
        }
      },
      feedback: {
        success: '완벽합니다! 꼬들꼬들한 라면이 완성되었어요.',
        failure: '순서가 이상해요. 물이 끓기도 전에 먹으면 안 되겠죠?',
        hint: '프로그램은 위에서 아래로 한 줄씩 실행됩니다.'
      },
      interviewQuestions: [
        {
          trigger: 'success',
          question: '완벽해요! 그런데 만약 물이 끓지 않았는데 면을 넣으면 어떻게 될까요?',
          hint: '순서가 중요한 이유를 생각해보세요'
        }
      ]
    },
    {
      id: 'quest_lv1_02',
      level: 1,
      title: '화분에 꽃 심기',
      description: '씨앗이 꽃이 되는 과정을 순서대로 나열해 보세요.',
      logic_type: '순차',
      emoji: '🌱',
      examples: '● IN: 씨앗, 흙, 화분\n● OUT: 예쁜 꽃',
      cards: [
        {
          id: 'b1',
          text_ko: '화분에 흙을 채운다',
          text_py: 'fill_soil()',
          icon: '🪴',
          color: 'green',
          action: 'fill_soil'
        },
        {
          id: 'b2',
          text_ko: '흙 속에 씨앗을 심는다',
          text_py: 'plant_seed()',
          icon: '🌱',
          color: 'blue',
          action: 'plant_seed'
        },
        {
          id: 'b3',
          text_ko: '물을 충분히 준다',
          text_py: 'water_flower()',
          icon: '💧',
          color: 'blue',
          action: 'water'
        }
      ],
      correctSequence: ['b1', 'b2', 'b3'],
      validation: {
        puzzle_solution: [
          { id: 'b1', indent: 0 },
          { id: 'b2', indent: 0 },
          { id: 'b3', indent: 0 }
        ],
        execution: {
          function_name: "plant_flower",
          test_cases: [
            { input: "", expected: "'None'", type: "public", description: "꽃을 정상적으로 심는지 확인" }
          ]
        }
      },
      feedback: {
        success: '생명의 신비를 체험하셨군요! 올바른 순서입니다.',
        failure: '씨앗을 심기 전에 흙이 있어야 합니다.',
        hint: '일의 인과 관계(원인과 결과)를 생각해 보세요.'
      },
      interviewQuestions: [
        {
          trigger: 'success',
          question: '잘했어요! 이제 조건문을 배워볼 준비가 되었나요?',
          hint: '다음 레벨에서는 "만약 ~라면" 을 배워요'
        }
      ]
    },

    // LV2 - 선택
    {
      id: 'quest_lv2_01',
      level: 2,
      title: '비 오는 날 우산 챙기기',
      description: '날씨가 \'비\'라면 우산을 챙기는 논리를 완성하세요.',
      logic_type: '선택',
      emoji: '☔',
      examples: '● IN: weather=\'rain\'\n● OUT: take_umbrella()\n● IN: weather=\'sunny\'\n● OUT: (아무 일 없음)',
      cards: [
        {
          id: 'b1',
          text_ko: '오늘 날씨를 확인한다',
          text_py: 'weather = check_weather()',
          icon: '🌤️',
          color: 'blue',
          action: 'check_weather'
        },
        {
          id: 'b2',
          text_ko: '만약 날씨가 \'비\'와 같다면',
          text_py: 'if weather == \'rain\':',
          icon: '❓',
          color: 'purple',
          isCondition: true,
          action: 'check_rain'
        },
        {
          id: 'b3',
          text_ko: '    우산을 챙긴다',
          text_py: '    take_umbrella()',
          icon: '☔',
          color: 'green',
          indent: 1,
          action: 'take_umbrella'
        }
      ],
      correctSequence: ['b1', 'b2', 'b3'],
      validation: {
        puzzle_solution: [
          { id: 'b1', indent: 0 },
          { id: 'b2', indent: 0 },
          { id: 'b3', indent: 1 }
        ],
        execution: {
          function_name: "check_umbrella",
          test_cases: [
            { input: "'rain'", expected: "'take_umbrella'", type: "public" },
            { input: "'sunny'", expected: "'None'", type: "hidden" }
          ]
        }
      },
      feedback: {
        success: '준비성이 철저하군요! 비를 맞지 않게 되었습니다.',
        failure: '비가 올 때만 우산을 챙겨야 합니다. 들여쓰기를 확인하세요.',
        hint: '조건이 \'참\'일 때 실행할 명령은 들여쓰기(Indent)가 필요합니다.'
      },
      interviewQuestions: [
        {
          trigger: 'success',
          question: '잘했어요! 만약 화창한 날엔 선글라스를 챙기고 싶다면 어떻게 해야 할까요?',
          hint: 'else를 사용하면 조건이 거짓일 때도 처리할 수 있어요'
        }
      ]
    },
    {
      id: 'quest_lv2_02',
      level: 2,
      title: '놀이기구 키 제한',
      description: '키가 120cm 이상인 사람만 태워주는 안전 요원이 되어보세요.',
      logic_type: '선택(Else)',
      emoji: '🎢',
      examples: '● IN: height = 130\n● OUT: ride()\n● IN: height = 110\n● OUT: sorry()',
      cards: [
        {
          id: 'b1',
          text_ko: '손님의 키를 확인한다',
          text_py: 'height = check_height()',
          icon: '📏',
          color: 'blue',
          action: 'check_height'
        },
        {
          id: 'b2',
          text_ko: '만약 키가 120보다 크거나 같다면',
          text_py: 'if height >= 120:',
          icon: '❓',
          color: 'purple',
          isCondition: true,
          action: 'check_height_condition'
        },
        {
          id: 'b3',
          text_ko: '    탑승을 안내한다',
          text_py: '    ride()',
          icon: '✅',
          color: 'green',
          indent: 1,
          action: 'allow_ride'
        },
        {
          id: 'b4',
          text_ko: '아니면 (키가 작다면)',
          text_py: 'else:',
          icon: '❌',
          color: 'orange',
          isCondition: true,
          action: 'else_case'
        },
        {
          id: 'b5',
          text_ko: '    탑승 불가라고 말한다',
          text_py: '    sorry()',
          icon: '🙅',
          color: 'red',
          indent: 1,
          action: 'deny_ride'
        }
      ],
      correctSequence: ['b1', 'b2', 'b3', 'b4', 'b5'],
      validation: {
        puzzle_solution: [
          { id: 'b1', indent: 0 },
          { id: 'b2', indent: 0 },
          { id: 'b3', indent: 1 },
          { id: 'b4', indent: 0 },
          { id: 'b5', indent: 1 }
        ],
        execution: {
          function_name: "ride_safety",
          test_cases: [
            { input: "130", expected: "'ride'", type: "public" },
            { input: "110", expected: "'sorry'", type: "hidden" }
          ]
        }
      },
      feedback: {
        success: '안전 수칙을 잘 지켰습니다! 완벽한 안전 요원이네요.',
        failure: '키가 작은 어린이는 보호자가 필요해요. 탑승시키면 안 됩니다!',
        hint: 'if와 else는 짝꿍입니다. 조건이 맞을 때와 아닐 때를 모두 처리하세요.'
      },
      interviewQuestions: [
        {
          trigger: 'success',
          question: '완벽합니다! 이제 반복문을 배워볼까요?',
          hint: '같은 일을 여러 번 할 때 사용해요'
        }
      ]
    },

    // LV3 - 반복
    {
      id: 'quest_lv3_01',
      level: 3,
      title: '로켓 발사 카운트다운',
      description: '5부터 1까지 숫자를 세고 발사하는 반복문을 완성하세요.',
      logic_type: '반복',
      emoji: '🚀',
      examples: '● IN: count=5\n● OUT: 5, 4, 3, 2, 1, 발사!',
      cards: [
        {
          id: 'b1',
          text_ko: '카운트를 5로 정한다',
          text_py: 'count = 5',
          icon: '5️⃣',
          color: 'blue',
          action: 'init_count'
        },
        {
          id: 'b2',
          text_ko: '카운트가 0보다 큰 동안 반복한다',
          text_py: 'while count > 0:',
          icon: '🔁',
          color: 'purple',
          isLoop: true,
          action: 'check_loop'
        },
        {
          id: 'b3',
          text_ko: '    현재 카운트를 외친다',
          text_py: '    print(count)',
          icon: '📢',
          color: 'green',
          indent: 1,
          action: 'print_count'
        },
        {
          id: 'b4',
          text_ko: '    카운트를 1 감소시킨다',
          text_py: '    count = count - 1',
          icon: '⬇️',
          color: 'orange',
          indent: 1,
          action: 'decrease_count'
        },
        {
          id: 'b5',
          text_ko: '발사!',
          text_py: 'launch()',
          icon: '🚀',
          color: 'red',
          action: 'launch'
        }
      ],
      correctSequence: ['b1', 'b2', 'b3', 'b4', 'b5'],
      validation: {
        puzzle_solution: [
          { id: 'b1', indent: 0 },
          { id: 'b2', indent: 0 },
          { id: 'b3', indent: 1 },
          { id: 'b4', indent: 1 },
          { id: 'b5', indent: 0 }
        ],
        execution: {
          function_name: "rocket_countdown",
          test_cases: [
            { input: "", expected: "'None'", type: "public" }
          ]
        }
      },
      feedback: {
        success: '발사 성공! 우주로 날아갑니다! 🌌',
        failure: '카운트가 줄지 않으면 영원히 반복됩니다(무한루프)!',
        hint: '반복문 안에서 조건을 변화시켜야 멈출 수 있어요.'
      },
      interviewQuestions: [
        {
          trigger: 'success',
          question: '완벽해요! 만약 카운트를 줄이는 부분을 빼먹으면 어떻게 될까요?',
          hint: '무한 반복(Infinite Loop)이 발생해요'
        }
      ]
    },
    {
      id: 'quest_lv3_02',
      level: 3,
      title: '풍선 불기 게임',
      description: '풍선을 적당한 크기(10)까지 불어보세요. 너무 크면 펑!',
      logic_type: '반복',
      emoji: '🎈',
      examples: '● IN: size=0\n● OUT: 풍선 크기 10 달성',
      cards: [
        {
          id: 'b1',
          text_ko: '풍선 크기를 0으로 시작',
          text_py: 'size = 0',
          icon: '🔵',
          color: 'blue',
          action: 'init_size'
        },
        {
          id: 'b2',
          text_ko: '크기가 10보다 작은 동안 반복',
          text_py: 'while size < 10:',
          icon: '🔁',
          color: 'purple',
          isLoop: true,
          action: 'check_size'
        },
        {
          id: 'b3',
          text_ko: '    바람을 분다',
          text_py: '    blow_air()',
          icon: '💨',
          color: 'green',
          indent: 1,
          action: 'blow'
        },
        {
          id: 'b4',
          text_ko: '    크기를 1 키운다',
          text_py: '    size = size + 1',
          icon: '⬆️',
          color: 'orange',
          indent: 1,
          action: 'increase_size'
        }
      ],
      correctSequence: ['b1', 'b2', 'b3', 'b4'],
      validation: {
        puzzle_solution: [
          { id: 'b1', indent: 0 },
          { id: 'b2', indent: 0 },
          { id: 'b3', indent: 1 },
          { id: 'b4', indent: 1 }
        ],
        execution: {
          function_name: "blow_balloon",
          test_cases: [
            { input: "", expected: "'None'", type: "public" }
          ]
        }
      },
      feedback: {
        success: '적당한 크기로 풍선을 잘 불었습니다!',
        failure: '조건을 잘못 설정하면 풍선이 펑! 터져버릴지도 몰라요.',
        hint: '반복문은 \'조건이 참인 동안\'에만 계속 실행된다는 점을 기억하세요.'
      },
      interviewQuestions: [
        {
          trigger: 'success',
          question: '잘했어요! 이제 리스트를 다루는 방법을 배워볼까요?',
          hint: '여러 개의 데이터를 한 번에 처리할 수 있어요'
        }
      ]
    },

    // LV4 - 리스트
    {
      id: 'quest_lv4_01',
      level: 4,
      title: '장바구니 총액 계산',
      description: '장바구니에 담긴 물건들의 가격을 모두 더해 계산하세요.',
      logic_type: '리스트 순회',
      emoji: '🛒',
      examples: '● IN: prices=[1000, 500, 200]\n● OUT: total=1700',
      cards: [
        {
          id: 'b1',
          text_ko: '가격 리스트와 총액 변수(0)를 준비',
          text_py: 'prices = [1000, 500, 200]\ntotal = 0',
          icon: '🏪',
          color: 'blue',
          action: 'init_prices'
        },
        {
          id: 'b2',
          text_ko: '리스트의 각 가격(p)에 대해 반복',
          text_py: 'for p in prices:',
          icon: '🔁',
          color: 'purple',
          isLoop: true,
          action: 'loop_prices'
        },
        {
          id: 'b3',
          text_ko: '    total에 가격(p)을 더한다',
          text_py: '    total = total + p',
          icon: '➕',
          color: 'green',
          indent: 1,
          action: 'add_price'
        }
      ],
      correctSequence: ['b1', 'b2', 'b3'],
      validation: {
        puzzle_solution: [
          { id: 'b1', indent: 0 },
          { id: 'b2', indent: 0 },
          { id: 'b3', indent: 1 }
        ],
        execution: {
          function_name: "calculate_total",
          test_cases: [
            { input: "", expected: "'None'", type: "public" }
          ]
        }
      },
      feedback: {
        success: '계산 정확해요! 누적 합계(Accumulator) 패턴은 정말 자주 쓰인답니다.',
        failure: '더하는 동작은 반복문 안에서 계속 일어나야 합니다.',
        hint: '반복문 밖에서 더하면 마지막 물건 가격만 더해질 수 있습니다.'
      },
      interviewQuestions: [
        {
          trigger: 'success',
          question: '완벽해요! 이제 조건과 반복을 섞어볼 준비가 되었나요?',
          hint: '반복문 안에 조건문을 넣을 수 있어요'
        }
      ]
    },
    {
      id: 'quest_lv4_02',
      level: 4,
      title: '짝수 찾기 게임',
      description: '숫자 카드 중에서 짝수(2로 나누어 떨어지는 수)만 골라내 보세요.',
      logic_type: '리스트+조건',
      emoji: '🎯',
      examples: '● IN: cards = [1, 2, 3, 4]\n● OUT: 2, 4 발견',
      cards: [
        {
          id: 'b1',
          text_ko: '숫자 카드 리스트를 준비한다',
          text_py: 'cards = [1, 2, 3, 4]',
          icon: '🎴',
          color: 'blue',
          action: 'init_cards'
        },
        {
          id: 'b2',
          text_ko: '각 카드(num)에 대해 반복한다',
          text_py: 'for num in cards:',
          icon: '🔁',
          color: 'purple',
          isLoop: true,
          action: 'loop_cards'
        },
        {
          id: 'b3',
          text_ko: '    만약 2로 나눈 나머지가 0이라면',
          text_py: '    if num % 2 == 0:',
          icon: '❓',
          color: 'orange',
          isCondition: true,
          indent: 1,
          action: 'check_even'
        },
        {
          id: 'b4',
          text_ko: '        \'짝수 발견\'을 출력한다',
          text_py: '        print(num)',
          icon: '✅',
          color: 'green',
          indent: 2,
          action: 'print_even'
        }
      ],
      correctSequence: ['b1', 'b2', 'b3', 'b4'],
      validation: {
        puzzle_solution: [
          { id: 'b1', indent: 0 },
          { id: 'b2', indent: 0 },
          { id: 'b3', indent: 1 },
          { id: 'b4', indent: 2 }
        ],
        execution: {
          function_name: "find_evens",
          test_cases: [
            { input: "", expected: "'None'", type: "public" }
          ]
        }
      },
      feedback: {
        success: '짝수만 쏙쏙 잘 골라냈군요! 나머지 연산(%)을 잘 이해하셨습니다.',
        failure: '모든 숫자를 다 출력하면 안 돼요. 조건문 위치를 확인하세요.',
        hint: '반복문 안에 조건문을 넣으면 원하는 데이터만 필터링할 수 있습니다.'
      },
      interviewQuestions: [
        {
          trigger: 'success',
          question: '대단해요! 이제 고급 알고리즘에 도전할 준비가 되었나요?',
          hint: '최댓값 찾기 같은 알고리즘을 배워봐요'
        }
      ]
    },

    // LV5 - 고급
    {
      id: 'quest_lv5_01',
      level: 5,
      title: '가장 큰 숫자 찾기',
      description: '리스트에 있는 숫자들 중 가장 큰 \'대장 숫자\'를 찾아보세요.',
      logic_type: '최댓값 알고리즘',
      emoji: '👑',
      examples: '● IN: nums = [10, 50, 30]\n● OUT: max_val = 50',
      cards: [
        {
          id: 'b1',
          text_ko: '첫 번째 숫자를 현재 대장(max_val)으로 정한다',
          text_py: 'max_val = nums[0]',
          icon: '1️⃣',
          color: 'blue',
          action: 'init_max'
        },
        {
          id: 'b2',
          text_ko: '리스트의 모든 숫자(n)를 확인한다',
          text_py: 'for n in nums:',
          icon: '🔁',
          color: 'purple',
          isLoop: true,
          action: 'loop_nums'
        },
        {
          id: 'b3',
          text_ko: '    만약 현재 숫자(n)가 대장보다 크다면',
          text_py: '    if n > max_val:',
          icon: '❓',
          color: 'orange',
          isCondition: true,
          indent: 1,
          action: 'check_bigger'
        },
        {
          id: 'b4',
          text_ko: '        대장을 현재 숫자(n)로 바꾼다',
          text_py: '        max_val = n',
          icon: '👑',
          color: 'green',
          indent: 2,
          action: 'update_max'
        }
      ],
      correctSequence: ['b1', 'b2', 'b3', 'b4'],
      validation: {
        puzzle_solution: [
          { id: 'b1', indent: 0 },
          { id: 'b2', indent: 0 },
          { id: 'b3', indent: 1 },
          { id: 'b4', indent: 2 }
        ],
        execution: {
          function_name: "find_max",
          test_cases: [
            { input: "", expected: "'None'", type: "public" }
          ]
        }
      },
      feedback: {
        success: '진정한 챔피언을 찾아냈습니다! 최댓값 알고리즘을 마스터했네요.',
        failure: '비교 조건이 반대로 되면 가장 작은 수를 찾게 됩니다.',
        hint: '변수에 더 큰 값이 나타날 때마다 덮어쓰는 방식(Update)입니다.'
      },
      interviewQuestions: [
        {
          trigger: 'success',
          question: '완벽합니다! 마지막 최종 보스 문제에 도전할 준비가 되었나요?',
          hint: '조건문을 중첩해서 사용하는 고급 기술이에요'
        }
      ]
    },
    {
      id: 'quest_lv5_02',
      level: 5,
      title: '로그인 보안 시스템',
      description: '아이디와 비밀번호가 모두 맞아야만 접속을 허용하는 보안 로직을 만드세요.',
      logic_type: '중첩 조건',
      emoji: '🔒',
      examples: '● IN: id=\'admin\', pw=\'1234\'\n● OUT: \'접속 성공\'\n● IN: id=\'admin\', pw=\'0000\'\n● OUT: \'비번 오류\'',
      cards: [
        {
          id: 'b1',
          text_ko: '입력된 아이디가 \'admin\'인지 확인한다',
          text_py: 'if input_id == \'admin\':',
          icon: '🆔',
          color: 'purple',
          isCondition: true,
          action: 'check_id'
        },
        {
          id: 'b2',
          text_ko: '    비밀번호가 \'1234\'인지 확인한다',
          text_py: '    if input_pw == \'1234\':',
          icon: '🔑',
          color: 'orange',
          isCondition: true,
          indent: 1,
          action: 'check_pw'
        },
        {
          id: 'b3',
          text_ko: '        \'접속 성공\'을 출력한다',
          text_py: '        print(\'Success\')',
          icon: '✅',
          color: 'green',
          indent: 2,
          action: 'success'
        },
        {
          id: 'b4',
          text_ko: '    아니라면 (비번 틀림)',
          text_py: '    else:',
          icon: '❌',
          color: 'red',
          isCondition: true,
          indent: 1,
          action: 'else_pw'
        },
        {
          id: 'b5',
          text_ko: '        \'비밀번호 오류\'를 출력한다',
          text_py: '        print(\'Wrong PW\')',
          icon: '🚫',
          color: 'red',
          indent: 2,
          action: 'wrong_pw'
        }
      ],
      correctSequence: ['b1', 'b2', 'b3', 'b4', 'b5'],
      validation: {
        puzzle_solution: [
          { id: 'b1', indent: 0 },
          { id: 'b2', indent: 1 },
          { id: 'b3', indent: 2 },
          { id: 'b4', indent: 1 },
          { id: 'b5', indent: 2 }
        ],
        execution: {
          function_name: "login_system",
          test_cases: [
            { input: "", expected: "'None'", type: "public" }
          ]
        }
      },
      feedback: {
        success: '보안 시스템 가동 완료! 해커도 뚫지 못하겠네요.',
        failure: '아이디만 맞다고 통과시켜주면 보안 사고가 발생합니다!',
        hint: 'if문 안에 또 if문을 넣으면 더 까다롭고 정교한 조건을 만들 수 있습니다.'
      },
      interviewQuestions: [
        {
          trigger: 'success',
          question: '🎉 축하합니다! 모든 문제를 클리어했어요! 이제 진짜 코딩을 시작할 준비가 되었습니다!',
          hint: '수도코드를 이해했다면 실제 코드도 금방 배울 수 있어요'
        }
      ]
    }
  ]
};

export const getQuest = (questId) => {
  return gameData.quests.find(q => q.id === questId);
};

export const getTutorial = () => {
  return gameData.tutorial;
};

export const getTotalQuests = () => {
  return gameData.quests.length;
};
