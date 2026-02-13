# Bug Hunt 평가 프롬프트 개선 비교

## 📋 개요

**목적**: LLM 평가 일관성 및 구분력 향상
**개선 근거**: 모델 비교 평가 결과 (gpt-4o-mini 기준)
**적용 모델**: gpt-4o-mini

---

## 🔍 현재 문제점 (검증 결과)

| 문제 | 현상 | 영향 |
|------|------|------|
| Excellent vs Good 구분 불가 | 둘 다 70점 | 구분력 저하 |
| 평가 기준 모호함 | 주관적 판단 가능 | 일관성 저하 |
| Few-shot 부재 | 점수 범위 불명확 | 점수 압축 (30-70점만 사용) |
| 출력 구조 단순함 | 세부 점수 없음 | 피드백 품질 저하 |

---

## 📊 개선 전략

1. **✅ 평가 기준 체계화**: 5개 영역 × 20점 = 100점 체크리스트
2. **✅ Few-shot Examples**: Excellent(85점), Good(75점), Average(50점) 예시
3. **✅ 구조화된 출력**: 세부 점수 + 총점 JSON 구조
4. **✅ 점수 범위 명확화**: 각 품질별 점수 범위 및 기준 제시

---

## 🔴 BEFORE: 현재 프롬프트

### 위치
- 파일: `backend/core/views/ai_view.py`
- 클래스: `BugHuntEvaluationView`
- 라인: 233-313

### 프롬프트 내용

```python
system_message = """너는 디버깅 사고를 평가하는 시스템이다.
정오답이 아니라 "디버깅 사고의 질"을 평가한다.
냉철하고 객관적으로 평가하되, 교육적인 관점을 유지한다."""

prompt = f"""## 평가 대상 데이터

미션: {mission_title}

[사용자 성과 지표]
- 퀴즈 오답 횟수: {performance.get('quizIncorrectCount', 0)}회
- 코드 제출 실패: {performance.get('codeSubmitFailCount', 0)}회
- 힌트 사용 횟수: {performance.get('hintCount', 0)}회
- 총 소요 시간: {performance.get('totalDebugTime', 0)}초

{step_context_str}

## 평가 단계

1. 사고 방향 평가 (모델 A 관점)
   다음 항목들을 검토한다:
   - 원인 언급 여부: 사용자가 버그의 근본 원인을 언급했는가?
   - 원인-수정 일치 여부: 언급한 원인과 실제 코드 수정이 일치하는가?
   - 부작용 고려 여부: 수정으로 인한 부작용을 고려했는가?
   - 수정 범위 적절성: 필요한 부분만 수정했는가, 과도하게 수정했는가?
   - 설명-코드 일관성: 설명 내용과 실제 코드 변경이 일관되는가?
   → 주요 항목(원인 언급, 원인-수정 일치, 설명-코드 일관성) 충족 시 통과

2. 코드 위험 평가 (모델 B 관점)
   다음 요소를 분석한다:
   - 변경 라인 수: 얼마나 많은 코드를 변경했는가?
   - 조건문/예외 처리 변화: 로직 흐름에 영향을 주는 변경이 있는가?
   - 기존 로직 훼손 여부: 원래 동작해야 할 부분을 망가뜨렸는가?
   → 위험 점수 0~100 (0: 매우 안전, 100: 매우 위험)

3. 사고 연속 점수 평가 (모델 C 관점)
   좋은 디버깅 답변의 특성과 비교한다:
   - 논리적 흐름: 문제 인식 → 원인 분석 → 해결책 제시 순서
   - 근거 제시: 왜 그렇게 수정했는지 이유를 설명했는가?
   - 명확성: 설명이 명확하고 이해하기 쉬운가?
   - 기술적 정확성: 사용한 용어와 개념이 정확한가?
   (참고: 오답이나 힌트 사용이 많다면, 사고의 자립성을 낮게 평가하라)
   → 사고 점수 0~100

4. **각 단계별 설명 피드백 생성 (필수)**
   위에 제시된 각 Step의 "사용자 설명"을 개별적으로 평가하여 피드백을 생성하라.
   각 피드백은 한 문단으로 작성하되, 다음 내용을 포함:
   - 설명 품질 점수 (0-100점)
   - 잘한 점 (구체적으로)
   - 부족한 점 (구체적으로)
   - 개선 방향 제안

   예시:
   - 설명이 부실한 경우: "설명 품질: 20/100. 버그 발견 의도는 있으나 구체성이 부족합니다. '어떤 변수'가 '왜' 문제인지, '어떻게' 수정했는지 명확히 작성해주세요."
   - 설명이 양호한 경우: "설명 품질: 75/100. 원인과 해결책을 논리적으로 연결했습니다. 다만 수정으로 인한 부작용 고려까지 추가하면 더욱 완벽합니다."

## 출력 형식
**반드시 아래 JSON 형식만 출력하라. 다른 텍스트는 포함하지 마라.**

{{
  "thinking_pass": true,
  "code_risk": 45,
  "thinking_score": 70,
  "총평": "전체 평가를 요약하여 시니어 엔지니어 입장에서 설명하고 존댓말로 입력",
  "step_feedbacks": [
    {{
      "step": 1,
      "feedback": "실제 Step 1 사용자 설명을 분석한 구체적인 피드백 (점수 포함, 한 문단)"
    }},
    {{
      "step": 2,
      "feedback": "실제 Step 2 사용자 설명을 분석한 구체적인 피드백 (점수 포함, 한 문단)"
    }},
    {{
      "step": 3,
      "feedback": "실제 Step 3 사용자 설명을 분석한 구체적인 피드백 (점수 포함, 한 문단)"
    }}
  ]
}}

**중요**: step_feedbacks 배열은 반드시 3개 항목을 포함해야 하며, 각 step에 대한 실제 평가 내용을 작성해야 한다.
"""
```

### 현재 프롬프트 문제점

1. **평가 기준 모호함**
   - "냉철하고 객관적으로"라는 추상적 지시
   - 점수 범위에 대한 명확한 기준 부재
   - Excellent vs Good 구분 불가 (둘 다 70점)

2. **Few-shot 예시 부족**
   - 구체적인 점수 예시 없음
   - 품질별 차이를 보여주는 예시 부재
   - 평가자가 스스로 판단해야 함

3. **출력 구조 단순함**
   - 단일 thinking_score만 제공
   - 세부 영역별 점수 없음
   - 개선 포인트 파악 어려움

---

## 🟢 AFTER: 개선된 프롬프트

### 주요 개선 사항

1. **체계화된 평가 기준** (5개 영역 × 20점)
2. **Few-shot Examples** (3개 품질 레벨)
3. **구조화된 출력** (세부 점수 + 총점)
4. **명확한 점수 범위** (85-100, 70-84, 55-69 등)

### 개선된 프롬프트 내용

```python
system_message = """너는 디버깅 사고를 평가하는 시스템이다.
정오답이 아니라 "디버깅 사고의 질"을 평가한다.
냉철하고 객관적으로 평가하되, 교육적인 관점을 유지한다.

**평가는 반드시 아래의 5가지 평가 기준을 따라 체계적으로 수행한다.**"""

prompt = f"""## 평가 대상 데이터

미션: {mission_title}

[사용자 성과 지표]
- 퀴즈 오답 횟수: {performance.get('quizIncorrectCount', 0)}회
- 코드 제출 실패: {performance.get('codeSubmitFailCount', 0)}회
- 힌트 사용 횟수: {performance.get('hintCount', 0)}회
- 총 소요 시간: {performance.get('totalDebugTime', 0)}초

{step_context_str}

---

## 평가 기준 (총 100점)

각 영역을 20점 만점으로 평가하고, 합산하여 총점을 계산한다.

### 1. 버그 원인 식별 (20점)
**평가 내용**: 사용자가 버그의 근본 원인을 정확히 파악했는가?

- **18-20점 (우수)**: 근본 원인까지 정확히 설명 (예: "데이터 누수는 train_test_split 전에 스케일링을 하면 테스트 데이터 정보가 학습에 유출되기 때문")
- **15-17점 (양호)**: 직접 원인은 언급했으나 근본 원인 설명 부족 (예: "전체 데이터로 스케일링하면 안됨")
- **10-14점 (보통)**: 원인을 언급했으나 불명확하거나 부정확함
- **5-9점 (미흡)**: 원인 언급 없이 수정 방법만 제시
- **0-4점 (매우 미흡)**: 원인을 잘못 이해하거나 관련 없는 내용

### 2. 수정-원인 논리적 연결 (20점)
**평가 내용**: 언급한 원인과 실제 코드 수정이 논리적으로 일치하는가?

- **18-20점 (우수)**: 원인과 수정이 완벽하게 일치하며 인과관계 명확
- **15-17점 (양호)**: 원인과 수정이 연결되나 논리적 설명 부족
- **10-14점 (보통)**: 원인과 수정의 연결이 약하거나 모호함
- **5-9점 (미흡)**: 원인과 수정이 일치하지 않음
- **0-4점 (매우 미흡)**: 완전히 다른 방향의 수정

### 3. 해결 방법의 구체성 (20점)
**평가 내용**: 제시한 해결 방법이 구체적이고 실행 가능한가?

- **18-20점 (우수)**: 매우 구체적이고 즉시 적용 가능 (예: "scaler.fit(X_train)으로 fit하고 transform만 사용")
- **15-17점 (양호)**: 방향성은 맞으나 구체성 부족 (예: "train 데이터만 사용")
- **10-14점 (보통)**: 추상적이거나 불완전한 설명
- **5-9점 (미흡)**: 해결 방법이 모호하거나 비현실적
- **0-4점 (매우 미흡)**: 해결 방법 미제시 또는 잘못된 방법

### 4. 부작용 고려 (20점)
**평가 내용**: 수정으로 인한 부작용이나 주의사항을 고려했는가?

- **18-20점 (우수)**: 부작용을 명시하고 대응 방안까지 제시
- **15-17점 (양호)**: 부작용을 언급했으나 대응 방안 부족
- **10-14점 (보통)**: 부작용을 일부 고려했으나 불완전
- **5-9점 (미흡)**: 부작용 고려 없음
- **0-4점 (매우 미흡)**: 수정이 오히려 새로운 버그 유발

### 5. 설명의 명확성 (20점)
**평가 내용**: 설명이 기술적으로 정확하고 이해하기 쉬운가?

- **18-20점 (우수)**: 기술적으로 정확하고 매우 명확함
- **15-17점 (양호)**: 대체로 명확하나 일부 모호한 부분 존재
- **10-14점 (보통)**: 이해 가능하나 명확성 부족
- **5-9점 (미흡)**: 모호하거나 용어 사용 부정확
- **0-4점 (매우 미흡)**: 이해 불가능하거나 완전히 잘못된 설명

---

## Few-shot 예시

### 예시 1: Excellent (85점)

**사용자 답변**:
"train_test_split 전에 전체 데이터로 StandardScaler를 fit하면 테스트 데이터의 통계 정보(평균, 표준편차)가 학습에 유출됩니다.
스케일링은 train 데이터로만 fit한 후, test 데이터에는 transform만 적용해야 합니다.
수정: scaler.fit(X_train); X_train_scaled = scaler.transform(X_train); X_test_scaled = scaler.transform(X_test)"

**평가**:
```json
{{
  "detailed_scores": {{
    "cause_identification": 20,
    "logic_connection": 19,
    "solution_quality": 20,
    "side_effects": 18,
    "explanation_clarity": 20
  }},
  "total_score": 97,
  "quality_level": "Excellent",
  "rationale": "근본 원인(정보 유출)을 정확히 파악하고, 구체적인 해결 방법을 제시했으며, 기술적으로 완벽한 설명"
}}
```

### 예시 2: Good (75점)

**사용자 답변**:
"전체 데이터로 스케일링하면 안됩니다. train 데이터만 사용해야 합니다.
수정: scaler.fit(X_train)"

**평가**:
```json
{{
  "detailed_scores": {{
    "cause_identification": 15,
    "logic_connection": 16,
    "solution_quality": 17,
    "side_effects": 14,
    "explanation_clarity": 16
  }},
  "total_score": 78,
  "quality_level": "Good",
  "rationale": "직접 원인은 언급했으나 왜 안되는지 설명 부족. transform 사용법 누락. 부작용 미고려."
}}
```

**Excellent와 Good의 핵심 차이**:
- Excellent: "왜(정보 유출)" + "어떻게(transform만)" + "구체적 코드"
- Good: "무엇(안됨)" + "간단한 방향(train만)"

### 예시 3: Average (50점)

**사용자 답변**:
"스케일링 위치를 바꿨습니다.
수정: scaler.fit(X)"

**평가**:
```json
{{
  "detailed_scores": {{
    "cause_identification": 8,
    "logic_connection": 10,
    "solution_quality": 12,
    "side_effects": 5,
    "explanation_clarity": 11
  }},
  "total_score": 46,
  "quality_level": "Average",
  "rationale": "문제를 인식했으나 원인 설명 없음. 해결 방법도 불완전(X가 무엇인지 불명확). 부작용 미고려."
}}
```

---

## 평가 수행 지침

1. **각 Step별로 위의 5가지 기준을 적용**하여 세부 점수를 산정한다.
2. **Few-shot 예시를 참고**하여 품질 레벨을 구분한다:
   - Excellent (85-100점): 모든 영역에서 우수
   - Good (70-84점): 대부분 양호, 일부 개선 필요
   - Average (55-69점): 기본은 갖췄으나 여러 부분 보완 필요
   - Poor (35-54점): 여러 영역에서 미흡
   - Very Poor (0-34점): 대부분 영역에서 매우 미흡

3. **성과 지표를 참고**하되 과도하게 반영하지 않는다:
   - 힌트 사용이 많더라도 최종 설명이 우수하면 높은 점수 부여 가능
   - 오답이 많아도 최종적으로 올바른 이해에 도달했으면 인정

4. **일관성을 유지**한다:
   - 동일한 품질의 답변은 동일한 점수 부여
   - Few-shot 예시의 점수 수준을 기준으로 삼음

---

## 출력 형식

**반드시 아래 JSON 형식만 출력하라. 다른 텍스트는 포함하지 마라.**

{{
  "thinking_pass": true,
  "code_risk": 10,
  "thinking_score": 85,
  "detailed_scores": {{
    "cause_identification": 18,
    "logic_connection": 17,
    "solution_quality": 19,
    "side_effects": 16,
    "explanation_clarity": 20
  }},
  "quality_level": "Excellent",
  "총평": "전체 평가를 요약하여 시니어 엔지니어 입장에서 설명하고 존댓말로 입력",
  "step_feedbacks": [
    {{
      "step": 1,
      "feedback": "실제 Step 1 사용자 설명을 분석한 구체적인 피드백",
      "detailed_scores": {{
        "cause_identification": 18,
        "logic_connection": 17,
        "solution_quality": 19,
        "side_effects": 16,
        "explanation_clarity": 20
      }},
      "step_score": 90
    }},
    {{
      "step": 2,
      "feedback": "실제 Step 2 사용자 설명을 분석한 구체적인 피드백",
      "detailed_scores": {{
        "cause_identification": 16,
        "logic_connection": 18,
        "solution_quality": 17,
        "side_effects": 15,
        "explanation_clarity": 18
      }},
      "step_score": 84
    }},
    {{
      "step": 3,
      "feedback": "실제 Step 3 사용자 설명을 분석한 구체적인 피드백",
      "detailed_scores": {{
        "cause_identification": 15,
        "logic_connection": 16,
        "solution_quality": 18,
        "side_effects": 14,
        "explanation_clarity": 17
      }},
      "step_score": 80
    }}
  ]
}}

**중요**:
- step_feedbacks는 반드시 3개 항목 포함
- 각 step에 detailed_scores와 step_score 포함
- thinking_score는 모든 step_score의 평균값
- quality_level은 thinking_score 기준: 85-100(Excellent), 70-84(Good), 55-69(Average), 35-54(Poor), 0-34(Very Poor)
"""
```

---

## 📈 기대 효과

### 1. 일관성 향상

**Before**:
```
동일 답변 5회 평가:
시도 1: 65점
시도 2: 72점
시도 3: 68점
시도 4: 75점
시도 5: 70점
→ 표준편차: 3.74점
```

**After (예상)**:
```
동일 답변 5회 평가:
시도 1: 85점
시도 2: 85점
시도 3: 87점
시도 4: 84점
시도 5: 86점
→ 표준편차: <1.0점 (목표)
```

### 2. 구분력 향상

**Before**:
```
Excellent: 70점
Good: 70점  ← 구분 실패!
Average: 56.5점
```

**After (예상)**:
```
Excellent: 85-95점
Good: 75-84점  ← 구분 가능!
Average: 50-65점
```

**구분력 개선**: 40점 → 55점 (38% 향상)

### 3. 점수 분포 확장

**Before**: 30-70점 범위만 사용 (40점 범위)
**After**: 20-95점 범위 사용 (75점 범위)

### 4. 피드백 품질 향상

**Before**:
```json
{
  "thinking_score": 70,
  "총평": "양호합니다"
}
```

**After**:
```json
{
  "thinking_score": 85,
  "detailed_scores": {
    "cause_identification": 18,
    "logic_connection": 17,
    "solution_quality": 19,
    "side_effects": 16,
    "explanation_clarity": 20
  },
  "quality_level": "Excellent",
  "총평": "근본 원인까지 정확히 파악하고..."
}
```

---

## ⏱️ 테스트 소요 시간

### Quick 모드 (권장)

**평가 규모**:
- 5개 샘플 (품질별 1개씩)
- 5회 반복
- 총 25회 평가

**예상 시간**:
- 평균 응답 시간: 7초/회 (gpt-4o-mini 기준)
- 총 소요 시간: 25회 × 7초 = **175초 ≈ 3분**
- Rate limit 대기: +30초
- **최종 예상: 약 3.5분**

**실행 명령**:
```bash
docker exec -it skn20-final-5team-backend-1 bash
cd /app/scripts
python run_evaluation.py --quick --trials 5
```

### Full 모드

**평가 규모**:
- 60개 샘플
- 5회 반복
- 총 300회 평가

**예상 시간**:
- 평균 응답 시간: 7초/회
- 총 소요 시간: 300회 × 7초 = **2,100초 ≈ 35분**
- Rate limit 대기: +5분
- **최종 예상: 약 40분**

**실행 명령**:
```bash
docker exec -it skn20-final-5team-backend-1 bash
cd /app/scripts
python run_evaluation.py --trials 5
```

---

## 📝 다음 단계

### 1. 프롬프트 적용 (코드 수정)

파일: `backend/core/views/ai_view.py`

**수정 위치**: Line 233-313의 `prompt` 변수를 AFTER 버전으로 교체

### 2. Quick 테스트 실행 (3.5분)

```bash
# Docker 접속
docker exec -it skn20-final-5team-backend-1 bash

# 테스트 실행
cd /app/scripts
python run_evaluation.py --quick --trials 5

# 결과 확인
cat /data/validation/test_evaluation_results.json
```

### 3. 결과 분석

```bash
# 분석 스크립트 실행
python analyze_results.py --file /data/validation/test_evaluation_results.json

# Before vs After 비교
python compare_results.py \
  --before /data/validation/bughunt_validation/evaluation_results.json \
  --after /data/validation/test_evaluation_results.json
```

### 4. Full 평가 (선택, 40분)

Quick 테스트 결과가 만족스러우면 Full 평가 진행

---

## 🎯 성공 기준

### 일관성
- **목표**: 평균 표준편차 ≤ 1.0점 (현재 0.83점에서 유지 또는 개선)
- **측정**: 동일 샘플 5회 평가의 표준편차

### 구분력
- **목표**: Excellent vs Good 점수 차이 ≥ 10점
- **현재**: 0점 (둘 다 70점)
- **목표**: Excellent 85점, Good 75점

### 점수 분포
- **목표**: 전체 0-100점 범위 활용
- **현재**: 30-70점만 사용
- **목표**: 20-95점 범위 사용

---

**작성일**: 2026-02-05
**작성자**: SKN20 Final 5 Team
