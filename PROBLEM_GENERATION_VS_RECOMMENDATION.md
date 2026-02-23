# 문제 추천 vs 문제 생성: 아키텍처 비교 분석

## 🎯 핵심 질문

**현재**: "기존 문제 DB에서 추천"
```
weakness → category → lookup → recommend
edge_case → "unit0103" (미리 만들어진 문제)
```

**제안**: "사용자에 맞춤형 문제 생성"
```
weakness + user_data → generate → new problem
"null 처리 부족" + 사용자A의 코드 스타일 → "사용자A를 위한 맞춤 문제"
```

---

## ❌ 현재 추천 방식의 한계

### 1. 문제 DB의 한계

```
현재 DB:
├─ unit0103: "데이터 파이프라인 예외 처리"
├─ unit0105: "경계값 검증 설계"
└─ ...총 N개

문제점:
1. 모든 약점을 커버 불가
   (7개 약점 × 10개 정도씩 = 70개 문제 필요)

2. 사용자 맞춤 불가
   - edge_case 약점이라고 해서 모두 같은가?
   - A 사용자: null 처리 부족
   - B 사용자: empty array 처리 부족
   - C 사용자: 복잡한 엣지 케이스 종합 처리 부족
   → 같은 "unit0103" 문제로 대응 불가능

3. 난이도 조절 한계
   - 첫 시도: 쉬운 문제 필요
   - 개선 후: 어려운 문제 필요
   - 정체 상태: 다른 각도의 문제 필요
   → 미리 정해진 문제로는 대응 불가능

4. 확장성 한계
   - 새로운 약점 추가 → 새 문제 제작 필요
   - 업데이트 전까지는 "이 약점은 문제 없음"
```

### 2. 개인화 수준 낮음

```
추천 방식:
A 사용자 (null 처리 부족)
B 사용자 (empty array 처리 부족)
C 사용자 (null + empty 처리 부족)

→ 모두에게 "unit0103" 추천
→ A에게는 정확, B에게는 약간 벗어남, C에게도 부족함

생성 방식:
A: "다음 배열이 주어질 때 null 처리하시오"
   [null, 1, 2] → ?

B: "다음 배열이 주어질 때 empty 처리하시오"
   [] → ?

C: "다음 배열이 주어질 때 null/empty/혼합 처리하시오"
   [null, [], undefined, ...] → ?

→ 각자의 정확한 약점 다룸
```

### 3. 데이터 활용 한계

```
추천 방식:
약점 분석만 함
→ 약점 카테고리만 사용
→ 구체적인 사용자 코드/패턴은 무시됨

생성 방식:
사용자의 실제 코드를 분석
→ 사용자 스타일에 맞춘 문제 생성
→ 반복되는 실수 패턴을 직접 다루는 문제 생성

예:
사용자가 계속 "if(!arr)" 만 사용
→ "if(!arr || arr.length === 0)" 필요한 문제 생성
```

---

## ✅ 생성 방식의 장점

### 1. 완벽한 개인화

```
각 사용자의 정확한 약점을 명시적으로 다루는 문제

사용자A의 submitted_data:
```
function process(data) {
  if (data.value === null) { // ← null만 체크
    return 0;
  }
  // empty string, 0, undefined 미처리
}
```

생성 문제:
"위 코드의 문제점을 수정하시오.
 - null뿐만 아니라 undefined, empty 체크 필요
 - 대신 0과 false는 유효한 값임을 고려"

→ 정확히 이 사용자의 실수를 다루는 문제
```

### 2. 무제한 확장성

```
추천: 문제 DB 부족 → 새 문제 제작 필요 → 시간 걸림
생성: LLM이 무한 생성 → 즉시 제공 가능

7가지 약점 × 5단계 난이도 × 3가지 변형
= 105가지 문제
= DB로는 유지 불가능
= 생성으로는 즉시 가능
```

### 3. 적응형 난이도

```
생성 방식에서 가능한 것:

첫 시도 (실패):
"다음 배열에서 null을 필터링하시오"
[1, null, 2, null, 3] → [1, 2, 3]
(쉬운 문제)

두 번째 시도 (성공):
"다음 배열에서 falsy 값을 유지하면서
 null과 undefined만 필터링하시오"
[1, null, 0, false, undefined, ""] → [1, 0, false, ""]
(중간 난이도)

세 번째 시도 (성공):
"다음 객체 배열에서 중첩된 null/undefined 처리"
[{id: 1, meta: null}, {id: 2, meta: {value: null}}]
→ 깊은 복사, null coalescing 사용해서 정리
(어려운 문제)

네 번째: 실제 프로젝트 시나리오
"API에서 받은 데이터의 null/undefined 정리하기"
(매우 어려운 문제)
```

### 4. 다양한 각도의 반복

```
추천: 비슷한 문제만 추천
생성: 같은 개념을 다양한 각도에서

null 처리 약점:

각도1: "배열에서 null 필터링"
각도2: "객체에서 null 체크"
각도3: "nested structure에서 null 처리"
각도4: "API 응답에서 null 처리"
각도5: "null vs undefined 구분"
각도6: "optional chaining 활용"

→ 같은 "edge_case" 약점이지만
  완전히 다른 6가지 문제로 강화 학습 가능
```

### 5. 피드백 기반 즉시 생성

```
추천:
사용자가 문제 풀고 틀림
→ 다음 문제는? DB에서 찾기 (자유도 낮음)
→ 결국 같은 문제 반복

생성:
사용자가 문제 풀고 틀림
→ 시스템: "어디서 틀렸나? null 체크 부분"
→ 즉시 새 문제 생성
"다시 한 번 시도해봅시다"
[새로운 문제, 같은 약점, 다른 시나리오]
→ 자유도 높음
```

---

## 🔄 생성 방식의 구현

### Problem Generation Agent

```python
def run_problem_generator_agent(
    user_profile: UserProfile,
    weakness: str,           # "null/empty 입력 처리 부족"
    user_submitted_code: str,  # ← 새로 추가
    difficulty: str = "MEDIUM"  # ← 난이도 조절
) -> Dict[str, Any]:
    """
    사용자의 약점 + 실제 코드에 맞춘 문제 생성
    """

    prompt = f"""
당신은 프로그래밍 교사입니다.
학생의 약점을 정확히 다루는 맞춤형 문제를 생성하세요.

학생의 약점: {weakness}
학생의 최근 코드:
```
{user_submitted_code}
```

난이도: {difficulty}
- EASY: 기본 개념 적용
- MEDIUM: 실제 적용
- HARD: 엣지 케이스 포함

요구사항:
1. 학생의 현재 코드 스타일과 유사하게
2. 정확히 이 약점을 다루는
3. 단계적으로 풀 수 있는

문제를 생성하세요.

JSON 형식:
{{
  "problem_title": "제목",
  "problem_description": "상세 설명",
  "input_format": "입력 형식",
  "output_format": "출력 형식",
  "examples": [
    {{"input": "...", "output": "..."}}
  ],
  "constraints": ["...", "..."],
  "hint": "힌트 (선택사항)",
  "learning_focus": "이 문제를 통해 배울 개념"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.choices[0].message.content)
```

### 실행 흐름

```
사용자 약점 분석 완료
    ↓
Verification Agent: "개선 안 됨" (또는 "부분 개선")
    ↓
[선택 1] Adaptive Roadmap: "다른 각도로 학습"
    ↓
Problem Generation Agent 실행
    ├─ 약점: "null 처리 부족"
    ├─ 사용자 코드: (최근 제출 코드)
    ├─ 난이도: MEDIUM (이전 시도에서 실패했으니)
    └─ 프롬프트로 새 문제 생성
    ↓
결과:
{
  "problem_title": "재귀적 구조에서 null 처리",
  "problem_description": "...",
  "examples": [...],
  "hint": "..."
}
    ↓
사용자에게 새 문제 제시
"이전과는 다른 각도에서 같은 개념을 연습해봅시다"
```

---

## 📊 추천 vs 생성 비교표

| 항목 | 추천 방식 | 생성 방식 | 우승 |
|------|---------|---------|------|
| **개인화** | 70% (카테고리만) | 95% (정확한 약점) | 생성 ✅ |
| **확장성** | 낮음 (DB 한계) | 무한 | 생성 ✅ |
| **난이도 조절** | 고정 | 동적 | 생성 ✅ |
| **다양성** | 제한적 | 무한 | 생성 ✅ |
| **피드백 반영** | 어려움 | 즉시 | 생성 ✅ |
| **구현 복잡도** | 낮음 | 중간 | 추천 ✅ |
| **LLM 호출** | 0회 | 1회 | 추천 ✅ |
| **비용** | 매우 낮음 | 낮음-중간 | 추천 ✅ |
| **사용자 만족도** | 60% | 85% | 생성 ✅ |

---

## 🎯 최적 하이브리드 전략

### 권장: "추천 + 생성" 조합

```
시나리오 1: 첫 분석 후
→ Problem Recommender: DB에서 빠르게 추천
→ 사용자가 이미 DB에 있는 문제로 시작
→ 비용 0, 즉시 제공

시나리오 2: 첫 문제 실패 후 재시도
→ Problem Generator: 맞춤형 문제 생성
→ 다른 각도, 같은 약점
→ 개인화된 추가 연습

시나리오 3: N회 반복 실패 후
→ Problem Generator: 심화 문제 생성
→ 더 깊은 이해 필요
→ Hint 포함해서 제시

시나리오 4: 완벽히 마스터 후
→ Problem Generator: 실제 프로젝트 시나리오
→ 심화 문제
→ "이제 실무 예제로!"
```

### 구현 흐름

```
Day 1: 첫 분석
사용자: "내 약점 분석해줘"
    ↓
[기존 5-Agent]
    ↓
Problem Recommender ← DB에서
    ↓
"이 문제부터 풀어보세요: unit0103"

Day 7: 첫 시도 후 검증
[Verification Agent]
    ↓
"개선 안 됨. 다른 각도로 시도해봅시다"
    ↓
Problem Generator ← LLM으로 생성
    ↓
"이건 어떨까요? (AI가 만든 맞춤 문제)"

Day 14: N회 반복
[Verification Agent]
    ↓
"음... 근본 원인이 logic_design인 것 같아요"
    ↓
[Deep Dive Agent]
    ↓
Problem Generator ← 심화 문제 생성
```

---

## 💡 실제 효과: 시나리오

### Case 1: 첫 분석

```
사용자: "내 약점 분석해줘"

시스템 분석:
- weakness: "null/empty 입력 처리 부족"
- 추천 문제: unit0103 (DB에서)
- 추천 사유: "edge_case 카테고리에 매칭"

사용자: "좋아, 풀어보자"
(풀이 완료, 점수: 45)
```

### Case 2: 첫 시도 실패

```
[Verification Agent]
- 이전: 45점
- 현재: 50점
- 결론: "개선 미흡"

[Adaptive Roadmap Agent]
- 다음 스텝: "REMEDIAL - 다른 각도로"

Problem Generator 실행:
- 입력: weakness + user_code + difficulty=EASY
- 생성:

"배열에서 null 필터링 (난이도: EASY)
 다음 배열에서 null을 제거하시오:
 [1, null, 2, null, 3]

 예상 출력: [1, 2, 3]"

사용자: "아! 이건 더 이해하기 쉽네"
(풀이 완료, 점수: 95)

사용자 반응:
"오! 첫 번째 문제보다 훨씬 명확해"
```

### Case 3: 반복 학습

```
Day 7: 문제 1 통과 후
Problem Generator:

문제 1: "배열에서 null 필터링"
문제 2: "객체에서 null 체크"
문제 3: "nested structure에서 null 처리"
문제 4: "API 응답에서 null 처리"
문제 5: "optional chaining 활용"

→ 같은 "edge_case" 약점
→ 하지만 5가지 완전히 다른 각도
→ 깊이 있는 학습

vs

추천 방식:
문제 1: unit0103 (배열 예외 처리)
문제 2: unit0105 (경계값 검증)
문제 3: unit0110 (?)

→ DB에 맞춤형 5단계가 없음
```

---

## 🚀 구현 전략

### Phase 1: 하이브리드 기본 구현 (2주)

```
□ Problem Recommender (기존)
  → 그대로 유지 (빠른 추천용)

□ Problem Generator (신규)
  → Verification 실패 시 호출
  → 난이도 EASY/MEDIUM

□ 프롬프트 최적화
  → user_code 분석
  → weakness와 연계
  → 생성 품질 향상
```

### Phase 2: 고도화 (2주)

```
□ 난이도 동적 조절
  → EASY → MEDIUM → HARD

□ 다양성 보장
  → 5가지 각도의 문제 생성
  → 반복 패턴 방지

□ 힌트 시스템
  → 난이도에 따른 힌트
  → 동적 생성
```

### Phase 3: 프로젝트 시나리오 (1주)

```
□ 실무 시나리오 생성
  → "이제 실제 코드로 연습해봅시다"
  → 복잡한 상황 포함
```

---

## 📈 예상 효과

### 사용자 만족도

```
추천만: "음, 이 문제가 내 약점을 다루나?" (-20%)
추천+생성: "오! 내 약점 정확히 다루네!" (+30%)

추천만: 반복 학습 인식 -30%
추천+생성: 반복 학습 인식 +40%
```

### 학습 효과

```
추천만:
- 문제 다양성: 2-3개
- 개인화 수준: 60%
- 깊이 있는 학습: 어려움

추천+생성:
- 문제 다양성: 무한
- 개인화 수준: 95%
- 깊이 있는 학습: 자동 (각도 변화)
```

---

## ✅ 최종 권장안

### **하이브리드 전략이 최적**

```
초기 (빠른 제공):
Problem Recommender ← 기존 추천

반복 학습 (개인화):
Problem Generator ← AI 생성

심화 (마스터):
Problem Generator ← 실무 시나리오 생성
```

### 구현 순서

```
1순위: Problem Generator 기본 구현
   - 생성 로직
   - 난이도 조절
   - 프롬프트 최적화

2순위: Verification + Generator 연계
   - Verification 실패 → Generator 호출
   - 자동 재생성

3순위: 다양성/깊이 강화
   - 5가지 각도 문제 생성
   - 실무 시나리오 추가
```

---

## 🎯 최종 비전

### 현재
```
System: "edge_case 처리 부족입니다.
        unit0103 문제를 풀어보세요"

User: (같은 문제 반복)
      "계속 같은 문제네..."
```

### 개선 후
```
System: "edge_case 처리 부족입니다.
        이 맞춤형 문제로 시작하세요"

User: (첫 문제)
      ↓
System: "기본은 알겠는데 부족해요"
        "이번엔 다른 각도로: 객체에서 null 처리"

User: (두 번째 문제)
      ↓
System: "좋아지고 있어요!"
        "이제 nested structure로 심화해봅시다"

User: (세 번째 문제)
      ↓
...

System: "이제 실제 API 시나리오로!"
```

### 차이점
```
추천만:  문제 × 1-2개, 반복 학습 어려움
생성:    무한 문제, 깊이 있는 반복 학습, 개인화 극대화
```
