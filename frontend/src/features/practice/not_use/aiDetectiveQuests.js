/**
 * [수정일: 2026-01-28]
 * [내용: Unit 1 'AI Detective' 모드 전체 문제 데이터 (초급/중급/고급 총 30문제)]
 * [출처: 의사코드_추리_10문제.html]
 */
export const aiDetectiveQuests = [
    // --- 초급 (01-10): 데이터 정제 및 기초 통계 ---
    {
        id: "01", level: "초급", title: "낮은 신뢰도 데이터 필터링",
        briefing: "모델의 예측 결과 중 신뢰도(Confidence)가 0.8 미만인 데이터를 검수 대상으로 분류하세요.",
        mission: "confidence 리스트를 반복하며 0.8 미만인 항목의 data_id를 출력하세요.",
        data: [{ name: "data_ids", value: "['D1', 'D2', 'D3']", color: "text-blue-400" }, { name: "confidence", value: "[0.95, 0.72, 0.88]", color: "text-orange-400" }],
        target: "D2", hint: "if (score < 0.8)를 사용하세요."
    },
    {
        id: "02", level: "초급", title: "총 추론 토큰 합산",
        briefing: "LLM API 사용량을 파악하기 위해 전체 세션에서 소비된 총 토큰 수를 계산하세요.",
        mission: "tokens 리스트의 모든 요소를 합산하여 출력하세요.",
        data: [{ name: "tokens", value: "[120, 45, 300, 80]", color: "text-yellow-400" }],
        target: "545", hint: "변수를 0으로 초기화하고 누적 합을 구하세요."
    },
    {
        id: "03", level: "초급", title: "데이터셋 노이즈 카운트",
        briefing: "라벨링이 'Unknown'으로 되어 있는 노이즈 데이터의 개수를 파악하세요.",
        mission: "labels 리스트에서 'Unknown'의 개수를 출력하세요.",
        data: [{ name: "labels", value: "['Cat', 'Unknown', 'Dog', 'Unknown']", color: "text-red-400" }],
        target: "2", hint: "값이 'Unknown'과 일치할 때마다 카운트를 늘리세요."
    },
    {
        id: "04", level: "초급", title: "불용어(Stopwords) 확인",
        briefing: "텍스트 데이터에 금지어가 포함되어 있는지 검사하세요.",
        mission: "words 리스트에 'BadWord'가 있는지 확인하여 True/False를 출력하세요.",
        data: [{ name: "words", value: "['Hello', 'AI', 'World']", color: "text-emerald-400" }],
        target: "False", hint: "리스트 내에 특정 단어가 존재하는지 체크하세요."
    },
    {
        id: "05", level: "초급", title: "정규화(Normalization) 적용",
        briefing: "데이터의 스케일을 맞추기 위해 모든 값에 0.01을 곱해 정규화하세요.",
        mission: "raw_values 리스트의 각 항목에 0.01을 곱해 출력하세요.",
        data: [{ name: "raw_values", value: "[100, 250, 500]", color: "text-indigo-400" }],
        target: "1, 2.5, 5", hint: "반복문 내에서 스케일링 연산을 수행하세요."
    },
    {
        id: "06", level: "초급", title: "학습 실패 에포크 탐지",
        briefing: "손실값(Loss)이 1.0을 초과하여 학습이 불안정한 에포크 번호를 찾으세요.",
        mission: "losses가 1.0보다 큰 경우의 epoch 번호를 출력하세요.",
        data: [{ name: "epochs", value: "[1, 2, 3]", color: "text-slate-400" }, { name: "losses", value: "[0.5, 1.2, 0.8]", color: "text-red-400" }],
        target: "2", hint: "인덱스를 사용하여 두 리스트를 비교하세요."
    },
    {
        id: "07", level: "초급", title: "이미지 포맷 검수",
        briefing: "데이터셋 중 '.png' 포맷이 아닌 이미지를 선별하세요.",
        mission: "filenames에서 '.png'로 끝나지 않는 파일명을 출력하세요.",
        data: [{ name: "filenames", value: "['a.png', 'b.jpg', 'c.png']", color: "text-blue-300" }],
        target: "b.jpg", hint: "문자열의 끝부분을 체크하는 로직이 필요합니다."
    },
    {
        id: "08", level: "초급", title: "멀티모달 데이터 매칭",
        briefing: "텍스트와 이미지가 모두 준비된 유효한 데이터 샘플 수를 구하세요.",
        mission: "has_text와 has_image가 모두 True인 샘플 수를 출력하세요.",
        data: [{ name: "has_text", value: "[True, False, True, True]", color: "text-emerald-400" }, { name: "has_image", value: "[True, True, False, True]", color: "text-blue-400" }],
        target: "2", hint: "논리 연산자 AND(&&)를 사용하세요."
    },
    {
        id: "09", level: "초급", title: "데이터 샘플링",
        briefing: "너무 긴 문장은 학습에서 제외하려 합니다. 50자 이상의 문장만 추출하세요.",
        mission: "lengths가 50 이상인 인덱스의 데이터를 출력하세요.",
        data: [{ name: "lengths", value: "[20, 55, 10, 80]", color: "text-orange-300" }],
        target: "55, 80", hint: "길이 조건을 체크하여 필터링하세요."
    },
    {
        id: "10", level: "초급", title: "모델 학습 정확도",
        briefing: "최종 검증 데이터에 대한 정확도(Accuracy)를 백분율로 계산하세요.",
        mission: "(정답수 / 전체수) * 100을 계산하세요.",
        data: [{ name: "correct", value: "95", color: "text-blue-400" }, { name: "total", value: "100", color: "text-slate-400" }],
        target: "95%", hint: "단순 비율 계산 로직입니다."
    },

    // --- 중급 (11-20): 모델 평가 및 데이터 가공 ---
    {
        id: "11", level: "중급", title: "최악의 인퍼런스 지연",
        briefing: "API 응답 시간 중 가장 긴 레이턴시(Latency)를 찾아 최적화 대상을 선정하세요.",
        mission: "latency 리스트에서 최대값을 찾아 출력하세요.",
        data: [{ name: "latency", value: "[150, 300, 2400, 800]", color: "text-purple-400" }],
        target: "2400", hint: "max_val 변수를 업데이트하며 순회하세요."
    },
    {
        id: "12", level: "중급", title: "평균 정밀도(Average Precision)",
        briefing: "여러 번의 테스트 결과에 대한 평균 정밀도를 산출하세요.",
        mission: "모든 precision 값을 더해 개수로 나누어 출력하세요.",
        data: [{ name: "precision", value: "[0.85, 0.90, 0.75, 0.88]", color: "text-yellow-400" }],
        target: "0.845", hint: "합계를 구한 후 리스트 길이로 나누세요."
    },
    {
        id: "13", level: "중급", title: "데이터 중복 라벨 검사",
        briefing: "학습셋과 검증셋에 중복으로 포함된 데이터 ID를 찾으세요.",
        mission: "train_ids와 val_ids에 공통으로 있는 ID를 출력하세요.",
        data: [{ name: "train_ids", value: "['D1', 'D2', 'D3']", color: "text-blue-400" }, { name: "val_ids", value: "['D3', 'D4', 'D5']", color: "text-pink-400" }],
        target: "D3", hint: "교집합을 찾는 이중 반복문 로직입니다."
    },
    {
        id: "14", level: "중급", title: "활성 데이터셋 추출",
        briefing: "사용 가능 상태(Available)이면서 라벨링이 완료된(Labeled) 데이터만 골라내세요.",
        mission: "is_available이 True이고 is_labeled가 True인 데이터명을 출력하세요.",
        data: [{ name: "names", value: "['A', 'B', 'C']", color: "text-slate-400" }, { name: "is_available", value: "[True, True, False]", color: "text-orange-400" }, { name: "is_labeled", value: "[True, False, True]", color: "text-emerald-400" }],
        target: "A", hint: "두 조건이 모두 참인 인덱스를 찾으세요."
    },
    {
        id: "15", level: "중급", title: "사용자 세션 유지(Retention)",
        briefing: "1일차 접속자 중 7일차에도 AI를 재사용한 유저의 ID를 추출하세요.",
        mission: "day1과 day7 리스트의 공통 요소를 출력하세요.",
        data: [{ name: "day1", value: "['U1', 'U2', 'U3']", color: "text-blue-400" }, { name: "day7", value: "['U2', 'U4']", color: "text-purple-400" }],
        target: "U2", hint: "두 데이터셋의 교집합을 구세요."
    },
    {
        id: "16", level: "중급", title: "이상치(Outlier) 탐지",
        briefing: "평균 토큰 사용량(100)보다 3배 이상 높은 이상 요청을 식별하세요.",
        mission: "평균의 3배(300) 이상인 사용량을 출력하세요.",
        data: [{ name: "usage", value: "[50, 450, 120, 800]", color: "text-red-400" }],
        target: "450, 800", hint: "임계값(Threshold)을 먼저 정하고 비교하세요."
    },
    {
        id: "17", level: "중급", title: "인퍼런스 시간차 계산",
        briefing: "요청 시간과 응답 시간을 비교해 각 샘플의 처리 시간을 구하세요.",
        mission: "response_time - request_time 결과를 리스트로 출력하세요.",
        data: [{ name: "request", value: "[1000, 2000, 3000]", color: "text-blue-400" }, { name: "response", value: "[1200, 2500, 3100]", color: "text-orange-400" }],
        target: "200, 500, 100", hint: "인덱스를 사용하여 두 리스트의 차를 구하세요."
    },
    {
        id: "18", level: "중급", title: "특정 태스크 매출 합산",
        briefing: "모델링 태스크 중 'Translation' 작업으로 발생한 수익만 합산하세요.",
        mission: "task가 'Translation'인 항목의 profit 합을 출력하세요.",
        data: [{ name: "tasks", value: "['Chat', 'Translation', 'Chat']", color: "text-blue-400" }, { name: "profit", value: "[10, 50, 15]", color: "text-emerald-400" }],
        target: "50", hint: "조건부 누적 합산 로직입니다."
    },
    {
        id: "19", level: "중급", title: "프롬프트 길이 정책",
        briefing: "최적의 답변을 위해 프롬프트 길이가 10자 이상인 것만 유효하다고 판정하세요.",
        mission: "문자열 길이가 10 이상인 프롬프트만 출력하세요.",
        data: [{ name: "prompts", value: "['Hi', 'Tell me a story about AI', 'What is Python?']", color: "text-slate-400" }],
        target: "Tell me a story about AI, What is Python?", hint: "문자열 길이를 반환하는 함수를 활용하세요."
    },
    {
        id: "20", level: "중급", title: "모델 실패율 분석",
        briefing: "인퍼런스 시도 중 에러(Error)가 발생한 비중을 구하세요.",
        mission: "(에러횟수 / 전체횟수)를 계산하여 출력하세요.",
        data: [{ name: "results", value: "['Success', 'Error', 'Success', 'Error']", color: "text-indigo-400" }],
        target: "0.5 (50%)", hint: "'Error'의 개수를 먼저 센 후 전체로 나누세요."
    },

    // --- 고급 (21-30): MLOps 및 알고리즘 ---
    {
        id: "21", level: "고급", title: "학습 손실(Loss) 추세 검증",
        briefing: "에포크가 지날수록 손실값이 줄어들고 있는지(오름차순이 아닌지) 확인하세요.",
        mission: "이전 손실보다 현재 손실이 더 큰 경우가 생기면 False를 출력하세요.",
        data: [{ name: "losses", value: "[0.9, 0.7, 0.8, 0.4]", color: "text-slate-400" }],
        target: "False", hint: "현재 값과 이전 값을 순차적으로 비교하세요."
    },
    {
        id: "22", level: "고급", title: "다중 모델 앙상블 권한",
        briefing: "특정 성능 지표를 통과한 모델(SOTA 혹은 High)만 앙상블에 참여시키세요.",
        mission: "status가 'SOTA'이거나 'High'인 모델명을 출력하세요.",
        data: [{ name: "models", value: "['M1', 'M2', 'M3']", color: "text-blue-400" }, { name: "status", value: "['Low', 'SOTA', 'High']", color: "text-purple-400" }],
        target: "M2, M3", hint: "논리 연산자 OR(||)을 사용하세요."
    },
    {
        id: "23", level: "고급", title: "개인정보(PII) 비식별화",
        briefing: "학습 데이터 보호를 위해 민감한 기호('#')를 모두 제거하세요.",
        mission: "텍스트에서 '#' 문자를 제외한 나머지 문자만 합쳐서 출력하세요.",
        data: [{ name: "raw", value: "'D#A#T#A#S#E#T'", color: "text-cyan-400" }],
        target: "DATASET", hint: "문자열을 순회하며 특정 조건의 문자만 결합하세요."
    },
    {
        id: "24", level: "고급", title: "최저 성능 체크포인트",
        briefing: "성능이 가장 낮았던 구간을 찾아 가중치를 초기화하려 합니다. 최솟값을 찾으세요.",
        mission: "accuracy 리스트에서 최솟값을 찾아 출력하세요.",
        data: [{ name: "acc", value: "[0.8, 0.6, 0.9, 0.5, 0.7]", color: "text-blue-400" }],
        target: "0.5", hint: "min_val 변수를 갱신하며 루프를 도세요."
    },
    {
        id: "25", level: "고급", title: "성능 하락(Performance Drop) 탐지",
        briefing: "데이터 드리프트로 인해 성능이 지난달보다 떨어진 유저군을 찾으세요.",
        mission: "prev_score보다 curr_score가 낮은 유저 ID를 출력하세요.",
        data: [{ name: "user", value: "['U1', 'U2']", color: "text-blue-400" }, { name: "prev", value: "[0.95, 0.80]", color: "text-slate-400" }, { name: "curr", value: "[0.88, 0.85]", color: "text-indigo-400" }],
        target: "U1", hint: "두 점수 리스트를 대조하여 비교하세요."
    },
    {
        id: "26", level: "고급", title: "데이터 상관관계 매칭",
        briefing: "피처 A와 B가 모두 활성화된 데이터 샘플을 찾으세요.",
        mission: "featureA와 featureB가 모두 True인 샘플의 ID를 출력하세요.",
        data: [{ name: "ids", value: "['S1', 'S2']", color: "text-blue-400" }, { name: "featA", value: "[True, True]", color: "text-orange-400" }, { name: "featB", value: "[False, True]", color: "text-emerald-400" }],
        target: "S2", hint: "두 불리언 리스트를 AND 조건으로 확인하세요."
    },
    {
        id: "27", level: "고급", title: "과도한 API 요청 제한",
        briefing: "시스템 부하 방지를 위해 초당 요청수(10회)를 초과한 IP를 차단하세요.",
        mission: "req_count가 10을 초과하는 IP 주소를 출력하세요.",
        data: [{ name: "ips", value: "['1.1.1.1', '2.2.2.2']", color: "text-slate-400" }, { name: "reqs", value: "[5, 15]", color: "text-red-400" }],
        target: "2.2.2.2", hint: "임계값을 기준으로 필터링하세요."
    },
    {
        id: "28", level: "고급", title: "중첩된 AI 응답 파싱",
        briefing: "LLM이 생성한 JSON 구조에서 특정 속성값(score)이 0.5 이상인 것만 선별하세요.",
        mission: "내부의 score 값이 0.5 이상인 항목을 출력하세요.",
        data: [{ name: "scores", value: "[0.4, 0.8, 0.9]", color: "text-indigo-400" }],
        target: "0.8, 0.9", hint: "리스트 내 요소를 반복하며 비교 연산을 수행하세요."
    },
    {
        id: "29", level: "고급", title: "누락된 시퀀스 번호 찾기",
        briefing: "시계열 데이터 중 타임스탬프 순번이 빠진 지점을 찾아내세요.",
        mission: "1부터 5까지 중 리스트에 없는 숫자를 찾아 출력하세요.",
        data: [{ name: "seq", value: "[1, 2, 4, 5]", color: "text-slate-400" }],
        target: "3", hint: "전체 범위(1~5)를 돌며 리스트에 포함되지 않은 값을 찾으세요."
    },
    {
        id: "30", level: "고급", title: "인텐트 분류(Intent Classification)",
        briefing: "사용자 질문 중 'Purchase' 혹은 'Refund' 인텐트만 상담원에게 전달하세요.",
        mission: "intent가 'Purchase' 또는 'Refund'인 티켓 ID를 출력하세요.",
        data: [{ name: "ids", value: "['T1', 'T2', 'T3']", color: "text-blue-400" }, { name: "intents", value: "['General', 'Purchase', 'Refund']", color: "text-red-400" }],
        target: "T2, T3", hint: "논리 연산자 OR을 사용하여 문자열을 비교하세요."
    }
];
