# 아키텍처 검증 시스템 통합 가이드

## 📁 파일 구조

```
frontend/src/features/practice/architecture/
├── utils/
│   ├── architectureUtils.js          ← 기존 유틸
│   ├── architectureValidator.js       ← 🆕 검증 핵심 로직
│   └── architectureValidator.example.js  ← 🆕 테스트 & 사용 예제
├── services/
│   ├── architectureApiMasterAgent.js ← API 호출 (기존)
│   └── architectureApiFastTest.js    ← 대체 API (기존)
└── [Component/Hook 파일들]
```

---

## 🔧 핵심 검증 함수

### 1. **validateArchitecture** (메인 함수)
```javascript
import { validateArchitecture } from './utils/architectureValidator';

const result = validateArchitecture(submission, problem);
// ↓
// {
//   status: 'PASS' | 'FAIL' | 'INVALID_INPUT',
//   message: string,
//   validation: { stage1, stage2, stage3 },
//   summary: { ... },
//   warnings: string[]
// }
```

### 2. **formatValidationResult** (UI용 포맷팅)
```javascript
import { formatValidationResult } from './utils/architectureValidator';

const formatted = formatValidationResult(result);
// ↓
// {
//   passed: boolean,
//   headline: string,
//   mainMessage: string,
//   suggestions?: string,
//   warnings?: string[],
//   details?: object
// }
```

### 3. **세부 검증 함수들** (필요시)
```javascript
import {
  findIsolatedComponents,
  calculateComponentFulfillment,
  checkRequiredFlows,
  analyzeComponentDiversity
} from './utils/architectureValidator';

// 고립된 컴포넌트 찾기
const isolated = findIsolatedComponents(components, connections);

// 필수 컴포넌트 충족도 (%)
const fulfillment = calculateComponentFulfillment(
  components,
  requiredComponentNames
);

// 필수 연결 확인
const flowCheck = checkRequiredFlows(
  components,
  connections,
  requiredFlows
);

// 컴포넌트 다양성 분석
const diversity = analyzeComponentDiversity(components);
```

---

## 🎯 통합 위치별 구현

### **1. 제출 버튼 (architecture-submit-step 컴포넌트)**

```javascript
// before: 직접 API 호출
async function handleSubmit() {
  const evaluation = await callMasterAgentAPI(submission);
}

// after: 검증 먼저 실행
import { validateArchitecture, formatValidationResult } from '@/features/practice/architecture/utils/architectureValidator';

async function handleSubmit() {
  // ✅ Step 1: 전처리 검증
  const validation = validateArchitecture(submission, problem);

  if (validation.status !== 'PASS') {
    showValidationError(validation.message);

    if (validation.suggestion) {
      showSuggestion(validation.suggestion);
    }
    return; // 제출 중단
  }

  // ⚠️ Step 2: 경고 표시 (통과해도 경고 있을 수 있음)
  if (validation.warnings?.length > 0) {
    showWarnings(validation.warnings);
  }

  // ✅ Step 3: API 호출 (검증 통과했을 때만)
  try {
    const evaluation = await callMasterAgentAPI(submission);
    showEvaluation(evaluation);
  } catch (error) {
    showError('평가 중 오류 발생');
  }
}
```

**컴포넌트 예시:**
```jsx
// ArchitectureSubmitStep.jsx
import { validateArchitecture, formatValidationResult } from './utils/architectureValidator';

export function ArchitectureSubmitStep({
  components,
  connections,
  problem,
  onValidationPass,
  onValidationFail
}) {
  const [validationStatus, setValidationStatus] = useState(null);

  const handleSubmit = () => {
    const submission = { components, connections };
    const result = validateArchitecture(submission, problem);
    const formatted = formatValidationResult(result);

    setValidationStatus(formatted);

    if (formatted.passed) {
      onValidationPass(result);
    } else {
      onValidationFail(result);
    }
  };

  return (
    <div>
      {validationStatus && (
        <ValidationFeedback result={validationStatus} />
      )}
      <button onClick={handleSubmit} disabled={loading}>
        아키텍처 제출
      </button>
    </div>
  );
}

// ValidationFeedback.jsx
function ValidationFeedback({ result }) {
  if (result.passed) {
    return (
      <SuccessCard>
        <h3>{result.headline}</h3>
        <p>{result.mainMessage}</p>
        {result.warnings && (
          <WarningsList warnings={result.warnings} />
        )}
      </SuccessCard>
    );
  }

  return (
    <ErrorCard>
      <h3>{result.headline}</h3>
      <p>{result.mainMessage}</p>
      {result.suggestion && (
        <SuggestionBox>{result.suggestion}</SuggestionBox>
      )}
      <DebugDetails details={result.details} />
    </ErrorCard>
  );
}
```

---

### **2. 실시간 유효성 검사 (Canvas/Editor)**

사용자가 컴포넌트를 배치/연결하는 동안 실시간 피드백:

```javascript
// useDiagramValidation hook
import { validateBasicStructure } from './utils/architectureValidator';

export function useDiagramValidation(components, connections, problem) {
  const [validationFeedback, setValidationFeedback] = useState(null);

  useEffect(() => {
    // 1단계 검증만 실시간 수행
    const stage1 = validateBasicStructure(components, connections);

    if (!stage1.isValid) {
      // 오류: 빨간 배너 표시
      setValidationFeedback({
        type: 'error',
        messages: stage1.errors
      });
    } else if (stage1.warnings.length > 0) {
      // 경고: 노란 배너
      setValidationFeedback({
        type: 'warning',
        messages: stage1.warnings
      });
    } else {
      // 정상
      setValidationFeedback({
        type: 'success',
        messages: ['✅ 기본 구조는 완료되었습니다']
      });
    }
  }, [components, connections]);

  return validationFeedback;
}

// Canvas.jsx
function ArchitectureCanvas() {
  const feedback = useDiagramValidation(components, connections, problem);

  return (
    <div>
      {feedback && <ValidationBanner feedback={feedback} />}
      <Canvas components={components} connections={connections} />
    </div>
  );
}
```

---

### **3. Backend API (Optional)**

검증 로직이 자동으로 클라이언트에서 실행되지만, 필요시 서버에서도 검증:

```javascript
// backend/routes/architecture.js
import { validateArchitecture } from '../utils/architectureValidator';

app.post('/api/architecture/validate', (req, res) => {
  const { components, connections, problemId } = req.body;

  try {
    const problem = await Problem.findById(problemId);
    const submission = { components, connections };

    const result = validateArchitecture(submission, problem);

    return res.json({
      valid: result.status === 'PASS',
      result
    });
  } catch (error) {
    return res.status(400).json({ error: error.message });
  }
});
```

---

## 📊 검증 결과 흐름

```
사용자 제출
    ↓
validateArchitecture()
    ↓
┌─────────────────────────────────────┐
│ 단계별 검증                          │
├─────────────────────────────────────┤
│ Stage 1: 기본 구조                   │
│ ├─ 컴포넌트 3개 이상?               │
│ ├─ 연결 1개 이상?                   │
│ └─ 고립 컴포넌트?                   │
│                                     │
│ Stage 2: 필수 요구사항               │
│ ├─ 필수 컴포넌트 70%+?              │
│ └─ 필수 Flow 구현?                  │
│                                     │
│ Stage 3: 설계 품질 (경고)            │
│ ├─ 타입 다양성                      │
│ └─ 균형 있는 분배                   │
└─────────────────────────────────────┘
    ↓
formatValidationResult()
    ↓
┌────────────────────┐
│ PASS              │ → 면접 진행
├────────────────────┤
│ FAIL              │ → 오류 메시지 + 제안
├────────────────────┤
│ PASS + WARNING    │ → 통과 + 경고 표시
└────────────────────┘
```

---

## 🧪 테스트 실행

```bash
# 모든 테스트 실행
npm run test:architect

# 또는 Node.js에서 직접
node -e "import('./src/features/practice/architecture/utils/architectureValidator.example.js').then(m => m.runAllTests())"
```

---

## 📝 검증 메시지 맞춤형 작성

```javascript
// 기본 오류 메시지 커스터마이징
const customErrorMessages = {
  COMPONENT_INSUFFICIENT: (current, required) =>
    `컴포넌트가 부족합니다 (현재: ${current}개, 필요: ${required}개 이상)`,

  CONNECTION_MISSING: (count) =>
    `최소 ${count}개 이상의 연결이 필요합니다`,

  COMPONENT_FULFILLMENT_LOW: (rate, missing) =>
    `필수 컴포넌트 충족도: ${rate}% (누락: ${missing.join(', ')})`,

  REQUIRED_FLOW_MISSING: (from, to, reason) =>
    `필수 연결 누락: "${from}" → "${to}" (${reason})`,

  ISOLATED_COMPONENTS: (names) =>
    `고립된 컴포넌트가 있습니다: ${names.join(', ')}`
};
```

---

## 🔐 데이터 구조

### Input: Submission
```typescript
interface Submission {
  components: Array<{
    id: string;
    text: string;      // 컴포넌트 이름
    type: string;      // 'server', 'cache', 'rdbms', 'storage', 'broker', etc.
    x?: number;        // 위치 (선택)
    y?: number;
  }>;
  connections: Array<{
    from: string;      // 시작 컴포넌트 ID
    to: string;        // 끝 컴포넌트 ID
  }>;
}
```

### Input: Problem
```typescript
interface Problem {
  rubric_functional: {
    required_components: string[];  // ["Web Server", "Redis", ...]
    required_flows: Array<{
      from: string;
      to: string;
      reason: string;
    }>;
  };
  rubric_non_functional?: Array<{
    category: string;
    question_intent: string;
    model_answer: string;
  }>;
}
```

### Output: Validation Result
```typescript
interface ValidationResult {
  status: 'PASS' | 'FAIL' | 'INVALID_INPUT';
  message: string;
  stage: 'BASIC_STRUCTURE' | 'REQUIREMENTS' | 'DESIGN_QUALITY';
  validation: {
    stage1: { isValid, errors, warnings, isolated };
    stage2: { isValid, errors, warnings, details };
    stage3: { warnings, details };
  };
  summary?: {
    componentCount: number;
    connectionCount: number;
    componentFulfillment: { rate, matched, missing };
    componentDiversity: { typeCount, types, diversity };
  };
  warnings: string[];
  suggestion?: string;
}
```

---

## ✅ 체크리스트

- [ ] `architectureValidator.js` 프로젝트에 추가
- [ ] 제출 버튼 로직에 `validateArchitecture` 호출 추가
- [ ] UI에 검증 피드백 표시 컴포넌트 생성
- [ ] 실시간 피드백 hook 구현 (선택)
- [ ] 테스트 케이스 실행 및 검증
- [ ] 오류 메시지 한글화 (필요시)
- [ ] API 통합 (서버 검증 필요시)

---

## 📞 문제해결

**Q: "같은 타입 컴포넌트"는 어떻게 판단하나?**
- 컴포넌트 이름 → 표준 타입 매핑 (COMPONENT_NAME_TO_TYPE)
- 예: "Redis Cache" → "cache", "PostgreSQL DB" → "rdbms"

**Q: 필수 Flow를 부분적으로 충족하면?**
- 필수 Flow는 모두 구현되어야 함
- 하나라도 누락되면 실패

**Q: 경고(Warning)가 있어도 제출 가능?**
- 예, 경고는 정보성이며 제출을 막지 않음
- 오류(Error)만 제출을 막음

**Q: 컴포넌트 이름 표준화가 안 되면?**
- `COMPONENT_NAME_TO_TYPE`에 새 매핑 추가
- 또는 서버에서 정규화 후 전송
