"""
Bug Hunt 평가 검증용 샘플 데이터 생성 스크립트

60개 샘플 생성: 12개 버그 케이스 × 5개 품질 레벨
"""
import json
import os

# 12개 버그 케이스 정의
BUG_CASES = [
    {
        "id": "data_leakage",
        "title": "Data Leakage",
        "bug_type": "데이터 누수",
        "description": "train_test_split 전에 스케일링하여 테스트 데이터 정보가 학습에 유출",
        "buggy_code": """from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)""",
        "correct_fix": """from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)"""
    },
    {
        "id": "label_imbalance",
        "title": "Label Imbalance",
        "bug_type": "레이블 불균형",
        "description": "불균형 데이터셋에서 accuracy만으로 평가하여 모델 성능 오판",
        "buggy_code": """from sklearn.metrics import accuracy_score

y_pred = model.predict(X_test)
score = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {score}")""",
        "correct_fix": """from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
print(f"Accuracy: {accuracy}, F1: {f1}, Recall: {recall}")"""
    },
    {
        "id": "overfitting",
        "title": "Overfitting",
        "bug_type": "과적합",
        "description": "검증 세트 없이 학습하여 과적합 발생",
        "buggy_code": """model.fit(X_train, y_train, epochs=100, batch_size=32)
test_score = model.evaluate(X_test, y_test)
print(f"Test score: {test_score}")""",
        "correct_fix": """from sklearn.model_selection import train_test_split

X_train_split, X_val, y_train_split, y_val = train_test_split(
    X_train, y_train, test_size=0.2, random_state=42
)
model.fit(X_train_split, y_train_split,
          validation_data=(X_val, y_val),
          epochs=100, batch_size=32)"""
    },
    {
        "id": "off_by_one",
        "title": "Off-by-one Error",
        "bug_type": "인덱스 오류",
        "description": "리스트 인덱싱에서 경계값 처리 오류",
        "buggy_code": """def get_last_n_items(items, n):
    return items[-n:]

result = get_last_n_items([1, 2, 3], 5)  # 오류!""",
        "correct_fix": """def get_last_n_items(items, n):
    if n <= 0:
        return []
    if n >= len(items):
        return items
    return items[-n:]"""
    },
    {
        "id": "null_pointer",
        "title": "Null Pointer",
        "bug_type": "Null 참조 오류",
        "description": "None 값 체크 없이 메서드 호출",
        "buggy_code": """def process_user(user_data):
    username = user_data['name'].lower()
    return username""",
        "correct_fix": """def process_user(user_data):
    if user_data is None or 'name' not in user_data:
        return None
    if user_data['name'] is None:
        return None
    return user_data['name'].lower()"""
    },
    {
        "id": "type_mismatch",
        "title": "Type Mismatch",
        "bug_type": "타입 불일치",
        "description": "문자열과 숫자를 연산하여 타입 에러 발생",
        "buggy_code": """def calculate_total(price, quantity):
    total = price * quantity
    return "Total: " + total""",
        "correct_fix": """def calculate_total(price, quantity):
    total = price * quantity
    return f"Total: {total}"  # 또는 "Total: " + str(total)"""
    },
    {
        "id": "metric_selection",
        "title": "Metric Selection Error",
        "bug_type": "평가 지표 선택 오류",
        "description": "회귀 문제에 classification metric 사용",
        "buggy_code": """from sklearn.metrics import accuracy_score

y_pred = model.predict(X_test)
score = accuracy_score(y_test, y_pred)""",
        "correct_fix": """from sklearn.metrics import mean_squared_error, r2_score

y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)"""
    },
    {
        "id": "feature_leakage",
        "title": "Feature Leakage",
        "bug_type": "피처 누수",
        "description": "target과 강한 상관관계가 있는 미래 정보 포함",
        "buggy_code": """# 대출 승인 예측 모델
features = ['income', 'age', 'credit_score', 'loan_approved_date']
X = df[features]
y = df['loan_approved']""",
        "correct_fix": """# loan_approved_date는 미래 정보이므로 제외
features = ['income', 'age', 'credit_score']
X = df[features]
y = df['loan_approved']"""
    },
    {
        "id": "hyperparameter",
        "title": "Hyperparameter Error",
        "bug_type": "하이퍼파라미터 오류",
        "description": "learning_rate가 너무 커서 발산",
        "buggy_code": """model = keras.Sequential([...])
model.compile(optimizer=keras.optimizers.Adam(learning_rate=1.0),
              loss='mse')""",
        "correct_fix": """model = keras.Sequential([...])
model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001),
              loss='mse')"""
    },
    {
        "id": "memory_leak",
        "title": "Memory Leak",
        "bug_type": "메모리 누수",
        "description": "대용량 데이터를 메모리에 계속 축적",
        "buggy_code": """results = []
for file in large_file_list:
    data = load_large_file(file)
    results.append(data)  # 메모리 누적!""",
        "correct_fix": """def process_file(file):
    data = load_large_file(file)
    result = process(data)
    return result

# 또는 generator 사용
for file in large_file_list:
    data = load_large_file(file)
    process(data)  # 처리 후 메모리 해제"""
    },
    {
        "id": "race_condition",
        "title": "Race Condition",
        "bug_type": "경쟁 상태",
        "description": "멀티스레드에서 공유 변수 접근 시 동기화 누락",
        "buggy_code": """counter = 0

def increment():
    global counter
    counter += 1

threads = [Thread(target=increment) for _ in range(100)]
for t in threads: t.start()""",
        "correct_fix": """from threading import Lock

counter = 0
lock = Lock()

def increment():
    global counter
    with lock:
        counter += 1"""
    },
    {
        "id": "api_timeout",
        "title": "API Timeout",
        "bug_type": "API 타임아웃",
        "description": "외부 API 호출 시 타임아웃 설정 누락",
        "buggy_code": """import requests

response = requests.get('https://api.example.com/data')
data = response.json()""",
        "correct_fix": """import requests

try:
    response = requests.get('https://api.example.com/data', timeout=5)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")"""
    }
]

# 5가지 품질 레벨의 답변 템플릿
def generate_answer(case, quality_level):
    """품질 레벨에 따른 답변 생성"""

    if quality_level == "excellent":
        # 우수: 정확한 원인 + 논리적 설명 + 올바른 수정
        return {
            "quality": "excellent",
            "expected_score_range": [85, 100],
            "step1_diagnosis": f"{case['bug_type']} 문제입니다. {case['description']}로 인해 발생했습니다. 구체적으로 {case['buggy_code'][:50]}... 부분에서 문제가 발생하며, 이는 데이터 무결성/로직 안정성을 해칩니다.",
            "step2_fix": case['correct_fix'],
            "step3_explanation": f"원인은 {case['bug_type']}이었습니다. 이를 해결하기 위해 {case['correct_fix'][:50]}...와 같이 수정했습니다. 이 수정으로 문제의 근본 원인이 제거되며, 부작용 없이 안전하게 동작합니다. 추가로 유사한 문제 재발을 방지하기 위해 경계 조건 체크도 강화했습니다."
        }

    elif quality_level == "good":
        # 양호: 원인은 맞지만 설명 간략
        return {
            "quality": "good",
            "expected_score_range": [70, 84],
            "step1_diagnosis": f"{case['bug_type']} 문제로 보입니다. {case['description'][:40]}... 때문입니다.",
            "step2_fix": case['correct_fix'],
            "step3_explanation": f"{case['bug_type']} 문제였습니다. 코드를 수정하여 해결했습니다."
        }

    elif quality_level == "average":
        # 보통: 방향은 맞지만 디테일 부족
        return {
            "quality": "average",
            "expected_score_range": [55, 69],
            "step1_diagnosis": f"코드에 문제가 있는 것 같습니다.",
            "step2_fix": case['correct_fix'][:len(case['correct_fix'])//2] + "\n# ... 일부 수정",
            "step3_explanation": f"버그를 찾아서 고쳤습니다."
        }

    elif quality_level == "poor":
        # 미흡: 원인 일부만 맞음
        return {
            "quality": "poor",
            "expected_score_range": [35, 54],
            "step1_diagnosis": f"뭔가 잘못된 것 같습니다.",
            "step2_fix": case['buggy_code'] + "\n# 변수명만 변경",
            "step3_explanation": f"수정해봤는데 잘 모르겠습니다."
        }

    else:  # very_poor
        # 매우 미흡: 원인 틀림 또는 설명 없음
        return {
            "quality": "very_poor",
            "expected_score_range": [0, 34],
            "step1_diagnosis": "모르겠습니다.",
            "step2_fix": case['buggy_code'],  # 수정 안함
            "step3_explanation": "잘 모르겠어요."
        }

# 60개 샘플 생성
def generate_all_samples():
    samples = []

    quality_levels = ["excellent", "good", "average", "poor", "very_poor"]

    for case_idx, case in enumerate(BUG_CASES):
        for quality_idx, quality in enumerate(quality_levels):
            answer = generate_answer(case, quality)

            sample = {
                "sample_id": f"{case['id']}_{quality}",
                "case_id": case['id'],
                "case_title": case['title'],
                "bug_type": case['bug_type'],
                "quality_level": quality,
                "expected_score_range": answer['expected_score_range'],

                # Bug Hunt 평가 API에 전달할 형식
                "missionTitle": case['title'],
                "steps": [
                    {
                        "step": 1,
                        "title": "버그 진단",
                        "bug_type": case['bug_type'],
                        "instruction": case['description'],
                        "buggy_code": case['buggy_code']
                    },
                    {
                        "step": 2,
                        "title": "코드 수정",
                        "bug_type": case['bug_type'],
                        "instruction": "버그를 수정하세요",
                        "buggy_code": case['buggy_code']
                    },
                    {
                        "step": 3,
                        "title": "설명 작성",
                        "bug_type": case['bug_type'],
                        "instruction": "수정 이유를 설명하세요",
                        "buggy_code": case['buggy_code']
                    }
                ],
                "explanations": {
                    "1": answer['step1_diagnosis'],
                    "2": answer['step2_fix'],
                    "3": answer['step3_explanation']
                },
                "userCodes": {
                    "1": case['buggy_code'],
                    "2": answer['step2_fix'],
                    "3": answer['step2_fix']
                },
                "performance": {
                    "quizIncorrectCount": 0,
                    "codeSubmitFailCount": 0,
                    "hintCount": 0 if quality in ["excellent", "good"] else (1 if quality == "average" else 2),
                    "totalDebugTime": 180
                }
            }

            samples.append(sample)

    return samples

if __name__ == "__main__":
    print("🎯 Bug Hunt 평가 검증용 샘플 생성 시작...")

    samples = generate_all_samples()

    # 저장
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'validation')
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, 'bug_hunt_validation_samples.json')

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)

    print(f"✅ 총 {len(samples)}개 샘플 생성 완료!")
    print(f"📁 저장 위치: {output_file}")
    print(f"\n📊 구성:")
    print(f"   - 버그 케이스: {len(BUG_CASES)}개")
    print(f"   - 품질 레벨: 5개 (excellent, good, average, poor, very_poor)")
    print(f"   - 총 샘플: {len(BUG_CASES)} × 5 = {len(samples)}개")
