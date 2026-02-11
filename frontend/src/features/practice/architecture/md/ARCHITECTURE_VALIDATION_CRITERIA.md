# 아키텍처 제출 검증 기준 분석

## 📊 현황 분석

### 데이터 기반 현황
- **총 10개 문제** 분석
- **필수 컴포넌트**: 문제당 최소 3개, 최대 4개
- **필수 연결(Flow)**: 문제당 최소 2개
- **각 문제별 상세 분석**:

| 문제 ID | 제목 | 필수 컴포넌트 | 필수 연결 |
|---------|------|-------------|---------|
| jr_001 | URL 단축 | 3개 (Web Server, RDBMS, Cache) | 2개 |
| jr_002 | Pastebin | 4개 (Web Server, S3, RDBMS, Cleanup Worker) | 2개 |
| jr_003 | 알림 시스템 | 3개 (Web Server, MQ, Worker) | 2개 |
| jr_004 | 이미지 피드 | 4개 (S3, CDN, Web Server, DB) | 2개 |
| jr_005 | 수강신청 | 3개 (Web Server, Redis, RDBMS) | 2개 |
| jr_006 | 채팅 | 3개 (WebSocket Gateway, Pub/Sub, RDBMS) | 2개 |
| jr_007 | 뉴스피드 | 3개 (Feed Service, Cache, DB) | 2개 |
| jr_008 | 자동완성 | 3개 (Search API, Search Engine, DB) | 2개 |
| jr_009 | 위치 추적 | 3개 (Location API, Redis, History DB) | 2개 |
| jr_010 | 크롤러 | 4개 (Worker, Queue, Bloom Filter, DB) | 2개 |

---

## 💡 당신의 제안 평가

### 제안 1: "컴포넌트 연결이 안되어있으면 불통과"
✅ **매우 타당함**
- 모든 문제에서 필수 연결(required_flows)이 존재
- 건축 설계도에서 "배선 없는 집"과 같은 상태를 피하기 위함
- **권장**: 필수 연결이 1개 이상 있어야 통과

### 제안 2: "컴포넌트 배치가 1-2개 이하면 불통과"
✅ **적절하지만 기준 조정 필요**
- 현황: 모든 문제에서 최소 3개 필수
- **문제**: 단순히 개수만 세면 구조적 의미 부족
- **개선안**: "필수 컴포넌트 충족 여부" 기준으로 변경

---

## 🎯 최종 권장 검증 기준

### 3계층 검증 방식

#### **1단계: 기본 구조 검증 (필수 통과)**
```
□ 컴포넌트 최소 3개 배치
  └─ 이유: 아키텍처 작업 자체를 포기한 상태 방지

□ 필수 연결 1개 이상 존재
  └─ 이유: 컴포넌트 간 상호작용의 의도 표현

□ 배치된 모든 컴포넌트가 연결됨 (고립된 컴포넌트 없음)
  └─ 이유: 계획 없는 임의 배치 방지
```

#### **2단계: 핵심 요구사항 검증 (맞춤형)**
```
□ 필수 컴포넌트 충족도
  ├─ 필수: 총 컴포넌트의 70% 이상 필수 컴포넌트 포함
  └─ 예시: jr_001의 경우 [Web Server, RDBMS, Cache] 중 2개 이상

□ 필수 연결(Required Flow) 충족
  ├─ 각 required_flow마다 해당 연결이 존재해야 함
  └─ 예: "Web Server → Cache" 반드시 포함
```

#### **3단계: 설계 품질 검증 (선택)**
```
□ 컴포넌트 타입의 다양성
  ├─ Server, Storage, Cache, Broker 등 다양한 카테고리 포함
  └─ 단순 "모두 서버" 구조 회피

□ 명확한 데이터 흐름
  ├─ 순환 구조 없음 (일반적인 아키텍처 원칙)
  └─ 진입점 → 처리 → 저장소 구조 확인
```

---

## 📋 검증 로직 구현 아이디어

```javascript
// 유효성 검사 함수 (의사 코드)
function validateArchitecture(userSubmission, problem) {
  const errors = [];
  const warnings = [];

  // 1단계: 기본 검증
  if (userSubmission.components.length < 3) {
    errors.push('❌ 컴포넌트 최소 3개 배치 필요');
  }

  if (userSubmission.connections.length === 0) {
    errors.push('❌ 최소 1개 이상의 연결이 필요합니다');
  }

  // 고립된 컴포넌트 확인
  const isolatedComponents = findIsolatedComponents(
    userSubmission.components,
    userSubmission.connections
  );
  if (isolatedComponents.length > 0) {
    warnings.push(`⚠️ 고립된 컴포넌트: ${isolatedComponents.join(', ')}`);
  }

  // 2단계: 필수 요구사항 검증
  const essentialComponents = problem.rubric_functional.required_components;
  const matchedComponents = userSubmission.components.filter(c =>
    essentialComponents.some(ec =>
      isSameComponentType(c.type, convertToType(ec))
    )
  );

  const fulfillmentRate = (matchedComponents.length / essentialComponents.length) * 100;
  if (fulfillmentRate < 70) {
    errors.push(`❌ 필수 컴포넌트 충족도 ${fulfillmentRate.toFixed(0)}% (최소 70% 필요)`);
  }

  // 필수 연결 확인
  const requiredFlows = problem.rubric_functional.required_flows;
  const missingFlows = requiredFlows.filter(flow =>
    !userSubmission.connections.some(conn =>
      isFlowMatched(conn, flow, userSubmission.components)
    )
  );

  if (missingFlows.length > 0) {
    errors.push(`❌ 필수 연결 누락: ${missingFlows.map(f => f.reason).join(', ')}`);
  }

  // 판정
  if (errors.length === 0) {
    return { status: 'PASS', message: '✅ 유효한 아키텍처입니다', warnings };
  } else {
    return { status: 'FAIL', message: errors.join('\n'), errors };
  }
}
```

---

## 🔄 불통과 → 재제출 플로우

```
제출
  ↓
[검증]
  ├─ 1단계 실패 → "기본 틀 부족 (컴포넌트/연결)"
  │  └─ 재작업 요청: "최소 3개 이상 배치 + 연결 구성"
  │
  ├─ 2단계 실패 → "필수 요구사항 미충족"
  │  └─ 재작업 요청: "다음 컴포넌트 추가 필요: [목록]"
  │
  └─ 통과 ✅
     └─ 면접 진행
```

---

## 🚀 최종 권장사항

### ✅ 채택할 기준
1. **컴포넌트 최소 3개** (사용자 제안 개선)
2. **필수 연결 1개 이상** (사용자 제안 수정)
3. **고립된 컴포넌트 없음** (신규 추가)
4. **필수 컴포넌트 70% 이상 충족** (신규 추가)

### ❌ 권장하지 않을 기준
- 연결 개수에 대한 최소 기준 (강한 제약, 문제마다 다름)
- 특정 컴포넌트 타입 강제 (유연성 저하)

### 📈 기대 효과
- 기본 틀을 갖춘 설계만 평가 대상으로 선정
- 사소한 오류는 경고로 피드백 (재제출 불필요)
- 공정한 평가 기준 제공

---

## 🎓 인터뷰 연결
유효성 검사 통과 후, 비기능 요구사항(Non-Functional Requirements) 기반 면접 질문:
- "캐시가 구조 어디에 위치하고 왜 그렇게 배치했나?"
- "이 시스템에서 단일 장애점(SPOF)은 어디인가?"
- "스케일링을 위해 어떤 컴포넌트를 추가할 것인가?"
