// [생성일: 2026-02-27] 로직 런 전용 퀘스트 데이터 (깔끔한 기본 알고리즘 & 웹 개발 시나리오 버전)
export const logicQuests = [
    {
        id: 1,
        title: "배열 데이터 필터링 (Data Filtering)",
        scenario: "서버에서 받아온 사용자 목록 배열에서 '활성 상태(Active)'이면서 '나이가 20세 이상'인 성인 사용자들만 추출하여 그들의 '이름(name)'만 배열로 반환하는 로직을 의사코드로 작성하세요.",

        // Phase 1 (Speed Fill)
        speedRounds: [
            {
                round: 1,
                context: "1. 함수 선언 및 결과 배열 준비",
                codeLines: [
                    { text: "함수 성인_활성유저_이름추출(유저_목록):", type: "fixed" },
                    { text: "  결과_배열 = ________", type: "blank", answer: "[]", options: ["[]", "{}", "0", "null"] },
                ]
            },
            {
                round: 2,
                context: "2. 배열 반복문 (Loop)",
                codeLines: [
                    { text: "  만약 유저_목록._______ == 0 이면:", type: "blank", answer: "길이", options: ["길이", "타입", "값", "키"] },
                    { text: "    반환 결과_배열", type: "fixed" },
                    { text: "  // 모든 유저를 순회", type: "fixed" },
                    { text: "  ______ 유저 in 유저_목록 반복:", type: "blank", answer: "각각", options: ["각각", "조건", "선택", "예외"] }
                ]
            },
            {
                round: 3,
                context: "3. 조건 검사 (활성 상태)",
                codeLines: [
                    { text: "    // 유저가 활성 상태인지 먼저 확인", type: "fixed" },
                    { text: "    만약 유저.상태 == '________' 이면:", type: "blank", answer: "활성", options: ["활성", "정지", "탈퇴", "휴면"] }
                ]
            },
            {
                round: 4,
                context: "4. 조건 검사 (성인 여부)",
                codeLines: [
                    { text: "      // 활성 상태인 유저 중 나이가 20세 이상인지 확인", type: "fixed" },
                    { text: "      만약 유저.나이 ________ 20 이면:", type: "blank", answer: ">=", options: [">=", "==", "<=", "!="] },
                    { text: "        // 조건을 모두 만족하면 결과 배열에 추가", type: "fixed" },
                    { text: "        결과_배열.추가(유저._______)", type: "blank", answer: "이름", options: ["이름", "아이디", "비밀번호", "상태"] }
                ]
            },
            {
                round: 5,
                context: "5. 최종 결과 반환",
                codeLines: [
                    { text: "  // 반복이 모두 종료되면 결과 반환", type: "fixed" },
                    { text: "  ________ 결과_배열", type: "blank", answer: "반환", options: ["반환", "출력", "삭제", "저장"] }
                ]
            }
        ],

        // Phase 2 (Design Sprint)
        designSprint: {
            checklist: [
                { id: "c1", label: "입력된 유저 목록을 순회(반복문)하는 로직", patterns: ["반복|순회|each|for|루프|loop"] },
                { id: "c2", label: "유저 상태가 '활성'인지 확인하는 조건문", patterns: ["조건|만약|if|활성|상태|active"] },
                { id: "c3", label: "유저 나이가 '20세 이상(>= 20)'인지 검증하는 로직", patterns: ["나이|20|이상|>="] },
                { id: "c4", label: "조건을 만족하는 유저의 '이름(name)'만 추출하는 처리", patterns: ["이름|name|추가|push|append"] },
                { id: "c5", label: "최종적으로 추출된 이름 배열을 반환(Return)하는 로직", patterns: ["반환|return|결과|배열"] }
            ]
        }
    },
    {
        id: 2,
        title: "비동기 API 통신 및 에러 처리 (Async API Fetch)",
        scenario: "외부 날씨 API 서버에 '/api/weather' 주소로 HTTP GET 요청을 보내 데이터를 가져오는 비동기(Async) 함수를 작성하세요. 단, 서버 오류(500)나 네트워크 단절에 대비한 예외 처리(try-catch)가 필수적으로 포함되어야 합니다.",

        speedRounds: [
            {
                round: 1,
                context: "1. 비동기 함수 선언",
                codeLines: [
                    { text: "________ 함수 날씨_가져오기():", type: "blank", answer: "비동기", options: ["비동기", "동기", "재귀", "익명"] },
                    { text: "  // 예기치 않은 오류를 묶어주는 블록 시작", type: "fixed" }
                ]
            },
            {
                round: 2,
                context: "2. 예외 처리 블록 (Try-Catch)",
                codeLines: [
                    { text: "  ________:", type: "blank", answer: "시도", options: ["시도", "예외", "반복", "조건"] },
                    { text: "    // 외부 API로 네트워크 요청 발송", type: "fixed" }
                ]
            },
            {
                round: 3,
                context: "3. API 호출 및 대기 (Await)",
                codeLines: [
                    { text: "    응답 = ________ HTTP.GET('/api/weather')", type: "blank", answer: "대기", options: ["대기", "즉시", "예약", "스킵"] },
                    { text: "    // 응답 상태 코드가 200번대(정상)인지 확인", type: "fixed" },
                    { text: "    만약 응답.정상여부 == 거짓 이면:", type: "fixed" },
                    { text: "      오류_발생('서버_응답_오류')", type: "fixed" }
                ]
            },
            {
                round: 4,
                context: "4. JSON 데이터 파싱",
                codeLines: [
                    { text: "    // JSON 형태의 본문을 객체로 파싱 (이 작업도 비동기)", type: "fixed" },
                    { text: "    데이터 = 대기 응답.________()", type: "blank", answer: "JSON변환", options: ["JSON변환", "텍스트", "바이너리", "헤더"] },
                    { text: "    반환 데이터", type: "fixed" }
                ]
            },
            {
                round: 5,
                context: "5. 예외(Error) 캐치 및 안내",
                codeLines: [
                    { text: "  ________ (에러):", type: "blank", answer: "예외상황", options: ["예외상황", "성공", "종료", "시도"] },
                    { text: "    로그.기록(에러.메시지)", type: "fixed" },
                    { text: "    반환 기본_날씨_데이터 // 사용자에게 에러 대신 기본값 반환", type: "fixed" }
                ]
            }
        ],

        designSprint: {
            checklist: [
                { id: "c1", label: "비동기(Async) 함수의 선언", patterns: ["비동기|async"] },
                { id: "c2", label: "안전하게 네트워크 통신을 감싸는 예외 처리(Try-Catch) 구조", patterns: ["시도|예외|try|catch|except"] },
                { id: "c3", label: "네트워크 응답이 완료될 때까지 기다리기 (Await)", patterns: ["대기|await|기다림"] },
                { id: "c4", label: "HTTP 실패 응답(Status Code 에러) 시의 분기 처리", patterns: ["상태|응답|정상|에러|실패|오류"] },
                { id: "c5", label: "에러 발생 시 프로그램이 뻗지 않도록 기본값(Fallback) 반환", patterns: ["기본값|fallback|반환|대체"] }
            ]
        }
    }
];
