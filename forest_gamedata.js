// gamedata.js

const gameData = [
    {
        stageId: 1,
        character: {
            name: "나노 촌장님",
            // [중요] 실제 생성한 이미지 경로로 교체하세요. 예: 'assets/chief_banana.png'
            image: "https://placehold.co/200x200/ffdf00/8b4513?text=Chief+Banana"
        },
        dialogue: "허허, 마을에 새로 온 규칙 설계자로군. 환영하네! 우리 마을은 모든 것이 '규칙'으로 움직이지. 첫 번째 임무는 마을 입구의 문지기 로봇에게 간단한 판단 능력을 주는 것일세.",
        quest: {
            description: "입력된 데이터(단어)의 길이가 **5글자 이상**이면 '통과', 그렇지 않으면 '정지'라고 출력하는 규칙을 만들어주게.",
            inputExample: "banana",
            outputExample: "통과",
        },
        // 정답 체크 로직 (간단한 키워드 매칭 방식)
        validator: (userCode) => {
            const code = userCode.toLowerCase();
            // 필수 키워드가 모두 포함되어 있는지 확인
            const keywords = ["만약", "길이", "5", "아니면", "출력"];
            const hasAllKeywords = keywords.every(kw => code.includes(kw));

            if (hasAllKeywords) {
                return { success: true, message: "훌륭하네! 기본적인 조건문 규칙을 완벽하게 이해했군." };
            } else {
                return { success: false, message: "음, 무언가 빠진 것 같네. '만약', '길이', '5 이상', '아니면' 같은 조건을 명확히 했는지 확인해보게." };
            }
        },
        scoreReward: 100
    },
    {
        stageId: 2,
        character: {
            name: "상인 다람쥐 칩",
            // [중요] 실제 생성한 이미지 경로로 교체하세요.
            image: "https://placehold.co/200x200/ffd700/8b4513?text=Squirrel+Merchant"
        },
        dialogue: "안녕! 난 도토리를 모으는 칩이야. 내가 가진 도토리 갯수에 따라 기분이 달라지는 규칙을 만들고 싶어. 도와줄래?",
        quest: {
            description: "입력된 숫자(도토리 수)가 **10 이상**이면 '기쁨', **5 이상 10 미만**이면 '보통', **5 미만**이면 '슬픔'을 출력하는 규칙을 만드세요.",
            inputExample: "7",
            outputExample: "보통",
        },
        validator: (userCode) => {
            const code = userCode.toLowerCase();
            // 다중 조건문(else if) 개념 확인
            const keywords = ["만약", "10 이상", "아니고 만약", "5 이상", "아니면", "출력"];
            // '아니고 만약' 대신 'else if' 등 다양한 표현을 허용하려면 정규식 사용 고려 필요

            // 여기서는 간단히 핵심 단어 포함 여부만 체크
            if (code.includes("10") && code.includes("5") && code.includes("만약") && (code.includes("아니고") || code.includes("그렇지 않고"))) {
                return { success: true, message: "와! 이제 내 기분을 정확히 표현할 수 있게 됐어! 고마워!" };
            }
            return { success: false, message: "어라? 조건이 세 가지가 되어야 해. 10개 이상일 때, 그게 아니고 5개 이상일 때, 그리고 나머지 경우..." };
        },
        scoreReward: 150
    },
    // ... 추가 스테이지는 이 구조를 따라 계속 추가할 수 있습니다 ...
];