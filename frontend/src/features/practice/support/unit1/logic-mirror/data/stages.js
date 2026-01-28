export const aiQuests = [
    {
        id: 1,
        title: "로그인 인증 시스템",
        category: "Auth",
        emoji: "🔐",
        desc: "아이디와 비밀번호가 일치하는지 확인하는 로직을 조립하세요.",
        rewardXP: 100,
        cards: [
            { id: 'b1', text: '만약 아이디 == "lion" 이면:', color: 'border-indigo-500', icon: '❓' },
            { id: 'b2', text: '    만약 비밀번호 == "1234" 이면:', color: 'border-indigo-500', icon: '❓' },
            { id: 'b3', text: '        반환 "성공"', color: 'border-emerald-500', icon: '✅' },
            { id: 'b4', text: '    아니면:', color: 'border-indigo-500', icon: '🔄' },
            { id: 'b5', text: '        반환 "실패"', color: 'border-rose-500', icon: '❌' }
        ],
        solution: ['b1', 'b2', 'b3', 'b4', 'b5'],
        codeValidation: { price: 'lion', fee1: '1234', fee2: 'Success' }, // 필드명은 재활용하거나 추후 일반화
        quizOptions: [
            { text: "A. 비밀번호가 틀려도 성공 처리한다.", correct: false },
            { text: "B. and 연산자를 사용하여 한 줄로 합칠 수 있다.", correct: true },
            { text: "C. 아이디 확인은 생략한다.", correct: false }
        ],
        mapPos: { x: 200, y: 150 }
    },
    {
        id: 2,
        title: "재고 관리 알림",
        category: "Inventory",
        emoji: "📦",
        desc: "재고가 부족할 때 주문 알림을 보내는 로직을 만듭니다.",
        rewardXP: 120,
        cards: [
            { id: 'b1', text: '만약 현재_수량 <= 10 이면:', color: 'border-indigo-500', icon: '❓' },
            { id: 'b2', text: '    알림_보내기("재고 부족")', color: 'border-amber-500', icon: '🔔' },
            { id: 'b3', text: '    반환 "주문 필요"', color: 'border-emerald-500', icon: '🛒' },
            { id: 'b4', text: '아니면:', color: 'border-indigo-500', icon: '🔄' },
            { id: 'b5', text: '    반환 "재고 충분"', color: 'border-emerald-500', icon: '✨' }
        ],
        solution: ['b1', 'b2', 'b3', 'b4', 'b5'],
        codeValidation: { price: '10', fee1: 'Alert', fee2: 'Safe' },
        quizOptions: [
            { text: "A. 수량이 0일 때만 주문한다.", correct: false },
            { text: "B. 최소 기준값을 상수로 관리하면 유지보수가 쉽다.", correct: true },
            { text: "C. 알림은 항상 보낸다.", correct: false }
        ],
        mapPos: { x: 350, y: 250 }
    },
    {
        id: 3,
        title: "기온별 옷차림 추천",
        category: "Service",
        emoji: "🌡️",
        desc: "날씨에 따라 적절한 의상을 추천하는 AI입니다.",
        rewardXP: 150,
        cards: [
            { id: 'b1', text: '만약 기온 >= 28 이면:', color: 'border-indigo-500', icon: '☀️' },
            { id: 'b2', text: '    추천 = "반팔"', color: 'border-emerald-500', icon: '👕' },
            { id: 'b3', text: '아니고_만약 기온 >= 15 이면:', color: 'border-indigo-500', icon: '☁️' },
            { id: 'b4', text: '    추천 = "맨투맨"', color: 'border-emerald-500', icon: '🧥' },
            { id: 'b5', text: '그외: 추천 = "패딩"', color: 'border-rose-500', icon: '❄️' }
        ],
        solution: ['b1', 'b2', 'b3', 'b4', 'b5'],
        codeValidation: { price: '28', fee1: 'Shorts', fee2: 'Coat' },
        quizOptions: [
            { text: "A. 모든 기온에서 반팔만 추천한다.", correct: false },
            { text: "B. elif(아니고 만약)를 사용해 여러 구간을 나눈다.", correct: true },
            { text: "C. 조건의 순서는 상관없다.", correct: false }
        ],
        mapPos: { x: 500, y: 350 }
    },
    {
        id: 4,
        title: "평균 제곱 오차 (MSE)",
        category: "AI Basic",
        emoji: "📈",
        desc: "예측값과 실제값의 차이를 계산하는 인공지능 기초입니다.",
        rewardXP: 180,
        cards: [
            { id: 'b1', text: '오차 = 실제 - 예측', color: 'border-indigo-500', icon: '➖' },
            { id: 'b2', text: '제곱_오차 = 오차 ** 2', color: 'border-amber-500', icon: '✖️' },
            { id: 'b3', text: '오차_총합에 더하기', color: 'border-emerald-500', icon: '➕' },
            { id: 'b4', text: '전체 개수로 나누기', color: 'border-indigo-500', icon: '➗' },
            { id: 'b5', text: '최종 MSE 반환', color: 'border-amber-500', icon: '🏁' }
        ],
        solution: ['b1', 'b2', 'b3', 'b4', 'b5'],
        codeValidation: { price: '10', fee1: '8', fee2: '4' },
        quizOptions: [
            { text: "A. 음수 오차를 없애기 위해 제곱을 사용한다.", correct: true },
            { text: "B. 오차는 항상 0이어야 한다.", correct: false },
            { text: "C. 제곱 대신 절대값을 써도 되지만 미분은 어렵다.", correct: true }
        ],
        mapPos: { x: 650, y: 250 }
    },
    {
        id: 5,
        title: "배달비 자동 계산",
        category: "Logistics",
        emoji: "🚚",
        desc: "주문 금액이 5만원 이상이면 배달비가 무료입니다.",
        rewardXP: 200,
        cards: [
            { id: 'b1', text: '만약 주문_금액 >= 50000 이면:', color: 'border-indigo-500', icon: '❓' },
            { id: 'b2', text: '    배달비 = 0', color: 'border-emerald-500', icon: '💰' },
            { id: 'b3', text: '아니면:', color: 'border-indigo-500', icon: '🔄' },
            { id: 'b4', text: '    배달비 = 2500', color: 'border-emerald-500', icon: '💰' },
            { id: 'b5', text: '최종 배달비 반환', color: 'border-amber-500', icon: '🏁' }
        ],
        solution: ['b1', 'b2', 'b3', 'b4', 'b5'],
        codeValidation: { price: '50000', fee1: '0', fee2: '2500' },
        quizOptions: [
            { text: "A. 거리에 따른 할증을 고려하지 않았다.", correct: true },
            { text: "B. 5만원 미만도 무료로 해준다.", correct: false },
            { text: "C. 배달비 변수를 먼저 선언하면 더 깔끔하다.", correct: true }
        ],
        mapPos: { x: 800, y: 150 }
    },
    {
        id: 6,
        title: "최대값 찾기",
        category: "Algorithm",
        emoji: "🔝",
        desc: "숫자 리스트에서 가장 큰 값을 찾는 기본 알고리즘입니다.",
        rewardXP: 220,
        cards: [
            { id: 'b1', text: '최댓값 = 목록[0]', color: 'border-indigo-500', icon: '0️⃣' },
            { id: 'b2', text: '반복: 목록의 단일_값에 대해:', color: 'border-indigo-500', icon: '🔁' },
            { id: 'b3', text: '    만약 단일_값 > 최댓값 이면:', color: 'border-amber-500', icon: '❓' },
            { id: 'b4', text: '        최댓값 = 단일_값', color: 'border-emerald-500', icon: '✅' },
            { id: 'b5', text: '최종 최댓값 반환', color: 'border-amber-500', icon: '🏁' }
        ],
        solution: ['b1', 'b2', 'b3', 'b4', 'b5'],
        codeValidation: { price: 'lists', fee1: 'compare', fee2: 'max' },
        quizOptions: [
            { text: "A. 처음 값을 최댓값으로 가정하고 시작한다.", correct: true },
            { text: "B. 모든 정렬 알고리즘은 최댓값을 찾는다.", correct: false },
            { text: "C. 빈 리스트일 경우 에러가 날 수 있다.", correct: true }
        ],
        mapPos: { x: 700, y: 450 }
    },
    {
        id: 7,
        title: "연속 출석 체크",
        category: "Service",
        emoji: "📅",
        desc: "하루라도 빠지면 초기화되는 스트릭 시스템을 만듭니다.",
        rewardXP: 250,
        cards: [
            { id: 'b1', text: '만약 오늘_방문 == 참 이면:', color: 'border-indigo-500', icon: '✅' },
            { id: 'b2', text: '    연속_일수 += 1', color: 'border-emerald-500', icon: '🔥' },
            { id: 'b3', text: '아니면:', color: 'border-indigo-500', icon: '❌' },
            { id: 'b4', text: '    연속_일수 = 0', color: 'border-rose-500', icon: '❄️' },
            { id: 'b5', text: '연속_일수 반환', color: 'border-amber-500', icon: '🏁' }
        ],
        solution: ['b1', 'b2', 'b3', 'b4', 'b5'],
        codeValidation: { price: 'True', fee1: 'streak+1', fee2: '0' },
        quizOptions: [
            { text: "A. 방문하지 않아도 일수를 늘린다.", correct: false },
            { text: "B. '그외(else)' 섹션이 초기화의 핵심이다.", correct: true },
            { text: "C. 데이터베이스 저장 로직이 추가로 필요하다.", correct: true }
        ],
        mapPos: { x: 550, y: 550 }
    },
    {
        id: 8,
        title: "스마트 점등 제어",
        category: "IoT",
        emoji: "💡",
        desc: "주변 밝기에 따라 전등을 자동으로 켜고 끕니다.",
        rewardXP: 280,
        cards: [
            { id: 'b1', text: '만약 조도_센서 < 100 이면:', color: 'border-indigo-500', icon: '🌑' },
            { id: 'b2', text: '    전등.상태 = "ON"', color: 'border-emerald-500', icon: '💡' },
            { id: 'b3', text: '아니고_만약 조도_센서 > 500 이면:', color: 'border-indigo-500', icon: '☀️' },
            { id: 'b4', text: '    전등.상태 = "OFF"', color: 'border-rose-500', icon: '🌑' },
            { id: 'b5', text: '상태 메시지 반환', color: 'border-amber-500', icon: '🏁' }
        ],
        solution: ['b1', 'b2', 'b3', 'b4', 'b5'],
        codeValidation: { price: '100', fee1: 'ON', fee2: 'OFF' },
        quizOptions: [
            { text: "A. 100~500 사이일 때는 이전 상태를 유지한다.", correct: true },
            { text: "B. 센서 값이 600이면 등이 켜진다.", correct: false },
            { text: "C. 센서 오차를 줄이기 위해 평균값을 쓸 수 있다.", correct: true }
        ],
        mapPos: { x: 400, y: 650 }
    },
    {
        id: 9,
        title: "비밀번호 안전성",
        category: "Security",
        emoji: "🛡️",
        desc: "길이가 너무 짧은 비밀번호를 거르는 보안 로직입니다.",
        rewardXP: 300,
        cards: [
            { id: 'b1', text: '길이 = 문자열_길이(비번)', color: 'border-indigo-500', icon: '📏' },
            { id: 'b2', text: '만약 길이 < 8 이면:', color: 'border-indigo-500', icon: '❓' },
            { id: 'b3', text: '    반환 "위험(Security Low)"', color: 'border-rose-500', icon: '🚨' },
            { id: 'b4', text: '아니면:', color: 'border-indigo-500', icon: '🔄' },
            { id: 'b5', text: '    반환 "안전(Security High)"', color: 'border-emerald-500', icon: '✅' }
        ],
        solution: ['b1', 'b2', 'b3', 'b4', 'b5'],
        codeValidation: { price: '8', fee1: 'Low', fee2: 'High' },
        quizOptions: [
            { text: "A. 길이만 체크하는 것은 충분하지 않다.", correct: true },
            { text: "B. 특수문자 포함 여부도 체크하면 더 좋다.", correct: true },
            { text: "C. 짧은 비밀번호가 더 기억하기 쉽고 안전하다.", correct: false }
        ],
        mapPos: { x: 250, y: 550 }
    },
    {
        id: 10,
        title: "비속어 필터링",
        category: "NLP",
        emoji: "🚫",
        desc: "채팅창의 깨끗한 환경을 위해 비속어를 마스킹합니다.",
        rewardXP: 500,
        cards: [
            { id: 'b1', text: '반복: 금지어_목록의 단어에 대해:', color: 'border-indigo-500', icon: '🔁' },
            { id: 'b2', text: '    만약 메시지에 단어가 포함되면:', color: 'border-amber-500', icon: '❗' },
            { id: 'b3', text: '        단어를 "***"로 치환한다', color: 'border-rose-500', icon: '🫧' },
            { id: 'b4', text: '반복 종료', color: 'border-indigo-500', icon: '🏁' },
            { id: 'b5', text: '정화된 메시지 반환', color: 'border-emerald-500', icon: '✨' }
        ],
        solution: ['b1', 'b2', 'b3', 'b4', 'b5'],
        codeValidation: { price: 'words', fee1: 'replace', fee2: 'clean_msg' },
        quizOptions: [
            { text: "A. 모든 단어를 지워버린다.", correct: false },
            { text: "B. 반복문을 통해 금지어 리스트를 순회한다.", correct: true },
            { text: "C. 대소문자를 구분하지 않도록 소문자로 바꾸면 더 좋다.", correct: true }
        ],
        mapPos: { x: 100, y: 450 }
    }
];