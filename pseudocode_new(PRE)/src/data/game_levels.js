export const levels = [
    {
        id: 1,
        title: "🔥 서버가 또 터졌어요 (Server Explosion)",
        category: "에러 핸들링",
        tags: ["#우선순위", "#중복제거", "#유지보수"],
        description: "서버에서 500 에러가 폭주하고 있습니다. 팀장님이 슬랙 알림이 너무 시끄럽다며, '진짜 중요한' 에러만 알림을 보내달라고 합니다.",

        // Step 1: Scenario & Understanding
        input_desc: `status (숫자): HTTP 상태 코드 (예: 200, 404, 500)
msg (문자열): 에러 로그 메시지 (예: "DB Connection Failed")
count (숫자): 최근 1분간 발생 횟수
is_maint (불리언): 현재 서버 점검 중 여부`,
        constraints: [
            "점검 중(is_maint)일 때는 무조건 알림을 보내지 않아야 함",
            "500 에러가 아니면 무시해도 됨",
            "심각한 에러(DB 관련 혹은 10회 이상 발생)만 알림 전송",
            "우선순위를 명확히 할 것"
        ],

        // Step 3: Quiz
        quiz: {
            question: "알림 로직에서 가장 '먼저' 확인해야 할 조건은 무엇일까요?",
            options: [
                { id: 'A', text: "에러 메시지에 'DB'가 포함되는지 확인" },
                { id: 'B', text: "최근 1분간 발생 횟수(count) 확인" },
                { id: 'C', text: "현재 점검 중(is_maint)인지 확인" },
                { id: 'D', text: "HTTP 상태 코드가 500인지 확인" }
            ],
            answer: 'C',
            explanation: "점검 중에는 에러가 나는 것이 당연하므로, 불필요한 연산을 줄이기 위해 가장 먼저 차단해야 합니다 (Early Return)."
        },

        // Step 4: Pseudocode
        goal: "\"Alert\", \"Log\", \"Ignore\" 중 하나를 반환",
        pseudocode_guide: `// 사용할 수 있는 키워드:
IF, ELSE, RETURN, AND, OR, CONTAINS

// 논리 흐름:
1. 점검 중이면? -> "Ignore"
2. 500 에러가 아니면? -> "Log"
3. 심각하면? (DB 포함 or count >= 10) -> "Alert"
4. 그 외 -> "Log"`,

        // Step 5: Python
        python_template: `def handle_alert(status, msg, count, is_maint):
    # 여기에 코드를 작성하세요
    # 예: if is_maint: return "Ignore"
    
    pass`,

        // Evaluation Logic
        eval_rubric: {
            metrics: [
                {
                    id: 'maintenance_check',
                    label: '유지보수 모드 확인',
                    regex: /(if|If|IF).*is_maint.*(return|RETURN)/s,
                    descriptions: {
                        pass: "점검 모드를 최우선으로 확인하여 불필요한 알림을 차단했습니다.",
                        fail: "점검 중일 때의 예외 처리가 가장 먼저 이루어지지 않았습니다."
                    }
                },
                {
                    id: 'status_check',
                    label: '500 에러 필터링',
                    regex: /(status.*500|500.*status)/s,
                    descriptions: {
                        pass: "HTTP 상태 코드를 정확히 확인하여 500 에러만 선별했습니다.",
                        fail: "모든 에러를 다루고 있습니다. 500 에러만 필터링하는 로직이 필요합니다."
                    }
                },
                {
                    id: 'critical_logic',
                    label: '중요도 판단 (DB/Count)',
                    regex: /(DB|count)/s,
                    descriptions: {
                        pass: "에러 메시지와 발생 횟수를 복합적으로 고려하여 중요도를 판단했습니다.",
                        fail: "단순 에러 여부만 확인했습니다. 비즈니스 중요도(DB, 빈도) 판단이 빠졌습니다."
                    }
                }
            ],
            improvement_video: {
                title: "좋은 분기문 작성을 위한 Early Return 패턴",
                url: "https://youtu.be/35ewrBZwg4U"
            }
        },

        // Duck Commentary
        duck_script: {
            intro: "안녕, 신입! 첫 임무네. 팀장님이 화나셨어. 서버 알림 로직, 어떻게 짤 거야?",
            step1: "먼저 상황을 파악해보자. 언제 알림을 보내야 할까?",
            step2: "이 문제의 핵심은 '순서'야. 굳이 계산 안 해도 되는 건 빨리 쳐내야지.",
            step3: "퀴즈 타임! 가장 중요한 조건이 뭐라고 생각해?",
            step4: "좋아, 이제 의사코드(Pseudocode)로 논리를 그려보자. 실수해도 괜찮아!",
            step5: "오, 논리가 서는데? 이제 이걸 파이썬으로 옮겨볼까? 문법 틀려도 돼.",
            success: "완벽해! 팀장님도 만족하실 거야. 이제 우린 주니어 레벨로 한 걸음 더 갔어!"
        }
    },

    {
        id: 2,
        title: "🔐 비밀번호가 너무 짧아요",
        category: "유효성 검사",
        tags: ["#조건문", "#기초", "#회원가입"],
        description: "회원가입 과정에서 비밀번호 길이가 너무 짧아 보안 이슈가 발생하고 있습니다.",

        input_desc: `password (문자열): 사용자가 입력한 비밀번호`,
        constraints: [
            "비밀번호 길이가 8자 미만이면 가입 불가",
            "조건 판단만 정확히 하면 됨"
        ],

        quiz: {
            question: "이 문제에서 가장 먼저 확인해야 할 것은?",
            options: [
                { id: 'A', text: "비밀번호에 특수문자가 있는지" },
                { id: 'B', text: "비밀번호 길이가 8자 이상인지" },
                { id: 'C', text: "비밀번호가 이전과 같은지" },
                { id: 'D', text: "비밀번호에 숫자가 포함되는지" }
            ],
            answer: 'B',
            explanation: "가장 기본적인 조건인 길이 체크가 우선입니다."
        },

        goal: "\"Allow\" 또는 \"Block\" 반환",

        pseudocode_guide: `
IF password.length < 8
  RETURN "Block"
ELSE
  RETURN "Allow"
`,

        python_template: `def check_password(password):
    pass`,

        eval_rubric: {
            metrics: [
                {
                    id: 'length_check',
                    label: '길이 조건 확인',
                    regex: /len|length/,
                    descriptions: {
                        pass: "비밀번호 길이 조건을 정확히 확인했습니다.",
                        fail: "비밀번호 길이에 대한 조건이 없습니다."
                    }
                }
            ],
            improvement_video: {
                title: "JavaScript Form Validation (기초)",
                url: "https://www.youtube.com/watch?v=rsd4FNGTRBw"
            }
        },

        duck_script: {
            intro: "회원가입부터 막히면 안 되겠지?",
            step1: "보안의 기본은 길이야.",
            success: "좋아! 이런 건 실무에서 매일 쓰는 로직이야."
        }
    },

    /* =========================
       LV0 - 문제 2
       ========================= */
    {
        id: 3,
        title: "🚫 관리자 페이지 접근",
        category: "권한 체크",
        tags: ["#권한", "#조건문", "#보안"],
        description: "일반 유저가 관리자 페이지에 접근하려고 합니다.",

        input_desc: `role (문자열): 사용자 권한 ("admin" | "user")`,
        constraints: [
            "admin만 접근 가능",
            "그 외는 모두 차단"
        ],

        quiz: {
            question: "접근 권한을 판단하는 기준은?",
            options: [
                { id: 'A', text: "로그인 여부" },
                { id: 'B', text: "페이지 주소" },
                { id: 'C', text: "사용자 권한(role)" },
                { id: 'D', text: "요청 시간" }
            ],
            answer: 'C',
            explanation: "권한 기반 접근 제어가 핵심입니다."
        },

        goal: "\"Access Granted\" 또는 \"Access Denied\" 반환",

        pseudocode_guide: `
IF role == "admin"
  RETURN "Access Granted"
ELSE
  RETURN "Access Denied"
`,

        python_template: `def check_access(role):
    pass`,

        eval_rubric: {
            metrics: [
                {
                    id: 'role_check',
                    label: '권한 확인',
                    regex: /admin/,
                    descriptions: {
                        pass: "권한 기준이 명확합니다.",
                        fail: "권한 판단 로직이 없습니다."
                    }
                }
            ],
            improvement_video: {
                title: "Authentication vs Authorization",
                url: "https://www.youtube.com/watch?v=7z9l0mJj8Y4"
            }
        },

        duck_script: {
            intro: "아무나 관리자면 큰일 나겠지?",
            success: "좋아, 기본 보안 감각 합격!"
        }
    },

    /* =========================
       LV1 - 문제 1
       ========================= */
    {
        id: 4,
        title: "📦 재고가 없어요",
        category: "상태 분기",
        tags: ["#재고", "#조건", "#실무"],
        description: "상품 재고가 부족할 경우 구매를 막아야 합니다.",

        input_desc: `stock (숫자): 현재 재고 수량`,
        constraints: [
            "재고가 0이면 구매 불가",
            "그 외에는 구매 가능"
        ],

        quiz: {
            question: "이 문제에서 가장 중요한 기준은?",
            options: [
                { id: 'A', text: "상품 가격" },
                { id: 'B', text: "재고 수량" },
                { id: 'C', text: "카테고리" },
                { id: 'D', text: "배송지" }
            ],
            answer: 'B',
            explanation: "재고 수량이 핵심 조건입니다."
        },

        goal: "\"Sold Out\" 또는 \"Available\" 반환",

        pseudocode_guide: `
IF stock == 0
  RETURN "Sold Out"
ELSE
  RETURN "Available"
`,

        python_template: `def check_stock(stock):
    pass`,

        eval_rubric: {
            metrics: [
                {
                    id: 'stock_check',
                    label: '재고 판단',
                    regex: /0/,
                    descriptions: {
                        pass: "재고 조건을 정확히 처리했습니다.",
                        fail: "재고가 없는 경우를 처리하지 않았습니다."
                    }
                }
            ],
            improvement_video: {
                title: "조건문 기초 실무 예제",
                url: "https://www.youtube.com/watch?v=IsG4Xd6LlsM"
            }
        },

        duck_script: {
            intro: "이건 쇼핑몰에서 매일 터지는 문제야.",
            success: "깔끔해! 실무에서도 그대로 쓰인다."
        }
    },

    /* =========================
       LV1 - 문제 2
       ========================= */
    {
        id: 5,
        title: "📨 알림 설정 확인",
        category: "설정 분기",
        tags: ["#알림", "#설정", "#조건조합"],
        description: "유저가 알림을 꺼두었을 경우 푸시 알림을 보내면 안 됩니다.",

        input_desc: `is_login (불리언)
allow_push (불리언)`,

        constraints: [
            "로그인 + 알림 허용 상태일 때만 전송"
        ],

        quiz: {
            question: "알림을 보내기 위한 조건은?",
            options: [
                { id: 'A', text: "로그인 상태" },
                { id: 'B', text: "알림 허용 상태" },
                { id: 'C', text: "A와 B 모두" },
                { id: 'D', text: "둘 다 아님" }
            ],
            answer: 'C',
            explanation: "두 조건을 모두 만족해야 합니다."
        },

        goal: "\"Send\" 또는 \"Skip\" 반환",

        pseudocode_guide: `
IF is_login AND allow_push
  RETURN "Send"
ELSE
  RETURN "Skip"
`,

        python_template: `def send_push(is_login, allow_push):
    pass`,

        eval_rubric: {
            metrics: [
                {
                    id: 'and_condition',
                    label: '조건 조합',
                    regex: /and|AND/,
                    descriptions: {
                        pass: "복합 조건을 정확히 사용했습니다.",
                        fail: "조건 조합이 누락되었습니다."
                    }
                }
            ],
            improvement_video: {
                title: "AND / OR 조건문 쉽게 이해하기",
                url: "https://www.youtube.com/watch?v=3aU0hQeF5Uo"
            }
        },

        duck_script: {
            intro: "알림은 허락받고 보내는 거야.",
            success: "이제 조건 조합 감각이 생겼어!"
        }
    },

    /* =========================
       LV2 - 문제 1
       ========================= */
    {
        id: 6,
        title: "🔁 로그인 실패 횟수 제한",
        category: "상태 누적",
        tags: ["#보안", "#카운트", "#실무"],
        description: "로그인 실패가 반복되면 계정을 잠가야 합니다.",

        input_desc: `fail_count (숫자): 로그인 실패 횟수`,
        constraints: [
            "5회 이상 실패 시 계정 잠금",
            "그 전까지는 로그인 시도 가능"
        ],

        quiz: {
            question: "이 로직의 핵심은 무엇인가요?",
            options: [
                { id: 'A', text: "시간 체크" },
                { id: 'B', text: "실패 횟수 누적" },
                { id: 'C', text: "비밀번호 길이" },
                { id: 'D', text: "권한 확인" }
            ],
            answer: 'B',
            explanation: "상태가 누적되는 조건 판단이 핵심입니다."
        },

        goal: "\"Locked\" 또는 \"Try Again\" 반환",

        pseudocode_guide: `
IF fail_count >= 5
  RETURN "Locked"
ELSE
  RETURN "Try Again"
`,

        python_template: `def login_guard(fail_count):
    pass`,

        eval_rubric: {
            metrics: [
                {
                    id: 'count_logic',
                    label: '횟수 누적 판단',
                    regex: />=|>/,
                    descriptions: {
                        pass: "누적 조건을 정확히 처리했습니다.",
                        fail: "누적 조건이 없습니다."
                    }
                }
            ],
            improvement_video: {
                title: "로그인 보안과 계정 잠금 원리",
                url: "https://www.youtube.com/watch?v=GJdWESd543I"
            }
        },

        duck_script: {
            intro: "보안은 한 번 실패로 판단하지 않아.",
            success: "좋아, 이제 진짜 실무 냄새 난다."
        }
    }

];
