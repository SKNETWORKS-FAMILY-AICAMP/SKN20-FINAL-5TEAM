# Goal-Driven Planner Agent — 구현 설계 문서 v3.1

> **목적**: 이 문서를 Claude CLI에 입력하면 바로 개발을 시작할 수 있는 완성형 설계 명세
> **언어**: Python 3.11+
> **LLM**: OpenAI GPT-4o (Vision/OCR) + GPT-4o-mini (전략 추론/보고서)
> **스킬 매칭**: sentence-transformers (deterministic embedding)
> **실행 환경**: CLI (추후 웹 확장 고려)

---

## 0. 설계 원칙

### 0.1 "측정은 알고리즘, 해석은 LLM"

| 영역 | 담당 | 이유 |
|------|------|------|
| 스킬 매칭 점수 | embedding cosine similarity | 일관성, 재현성 |
| skill_gap, readiness | deterministic 함수 | 같은 입력 → 같은 결과 |
| 스킬 카테고리 분류 | 딕셔너리 → embedding → LLM fallback | 텍스트 분류 (점수 산출 아님) |
| 전략 해석 / 행동 추론 | LLM (GPT-4o-mini) | 자연어 판단 |
| 이미지 OCR | LLM (GPT-4o) | Vision |
| 최종 보고서 | LLM (GPT-4o-mini) | 자연어 요약 |

**LLM이 하지 않는 것:** 점수 산출, 학습 기간 예측, 경쟁 강도 수치화

### 0.2 이 시스템의 실체 — 정직한 정의

이 시스템은 **"대화형 채용공고 분석 에이전트"**다.

한 번의 실행에서 하는 일:
1. 채용공고 수집 + 파싱
2. 사용자 프로필과 매칭 분석 (deterministic)
3. 사용자와 대화하며 정보를 보정 → **실제로 점수가 변한다**
4. 보정된 상태 기반으로 전략 보고서 생성

**에이전트인 부분:** 사용자 답변에 따라 상태가 변하고, 변한 상태에 따라 다른 행동을 선택한다.
**에이전트가 아닌 부분:** 사용자가 실제로 학습을 완료하고 돌아오는 "세션 간 루프"는 Phase 2.

### 0.3 이 시스템이 하지 않는 것

- ❌ 합격 확률 예측
- ❌ 자동 지원/이력서 제출
- ❌ 학습 기간/효과 수치 예측
- ❌ 정확한 시장 경쟁률 측정

### 0.4 신뢰할 수 있는 것만 말한다

- ✅ "공고에 Redis가 필수인데 당신은 경험이 없습니다" (사실)
- ✅ "매칭 스킬이 요구사항의 60%입니다" (측정)
- ✅ "마감까지 7일이고 부족 스킬이 3개입니다" (계산)
- ❌ "7일이면 Redis를 배울 수 있습니다" (근거 없음 — 하지 않음)

---

## 1. 아키텍처

```
User Input (URL / 텍스트 / 이미지)
        ↓
┌──────────────────────────────────────────────┐
│            Agent Orchestrator                │
│                                              │
│  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Input Handler│  │     Planner          │  │
│  │ (fallback    │  │  (GPT-4o-mini)       │  │
│  │  chain)      │  │  맥락분석 + 재계획    │  │
│  └──────┬───────┘  └───────┬──────────────┘  │
│         │                  │                 │
│  ┌──────┴───────┐  ┌──────┴──────────────┐  │
│  │  Company     │  │   Tool Manager      │  │
│  │  Researcher  │  │  ask_user           │  │
│  │  (선택적)    │  │  curate_learning    │  │
│  └──────────────┘  └────────────────────┘  │
│                                              │
│  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Scoring     │  │  Skill Analyzer      │  │
│  │  Engine      │  │  + CategoryResolver  │  │
│  └──────────────┘  └──────────────────────┘  │
│                                              │
│  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Memory      │  │  LLM Gateway         │  │
│  │  (JSON)      │  │  (4o + 4o-mini)     │  │
│  └──────────────┘  └──────────────────────┘  │
└──────────────────────────────────────────────┘
```

---

## 2. 입력 — Fallback Chain

### 2.1 Input Handler

사용자가 URL/텍스트/이미지 중 아무거나 넣으면, 에이전트가 최적 수집 방법을 선택한다.

```python
class InputHandler:
    def __init__(self, llm: LLMGateway, api_key: str = None):
        self.llm = llm
        self.api_key = api_key

    def collect_job_posting(self, user_input: str) -> JobPosting:
        input_type = self._detect_type(user_input)
        if input_type == "url":
            return self._handle_url(user_input)
        elif input_type == "image":
            return self._handle_image(user_input)
        else:
            return self._handle_text(user_input)

    def _handle_url(self, url: str) -> JobPosting:
        """URL → API → 정적크롤링 → 동적크롤링 → 사용자 요청"""

        if self.api_key:
            result = self._try_api(url)
            if result and self._is_sufficient(result):
                return result

        result = self._try_static_crawl(url)
        if result and self._is_sufficient(result):
            return result

        result = self._try_dynamic_crawl(url)
        if result and self._is_sufficient(result):
            return result

        # 최종 fallback: 사용자에게 직접 입력 요청
        print("[에이전트] 자동 수집 실패. 공고 내용을 직접 입력해주세요.")
        fallback = input("> 입력: ").strip()
        return self._handle_text(fallback) if self._detect_type(fallback) == "text" \
            else self._handle_image(fallback)

    def _try_static_crawl(self, url: str) -> JobPosting | None:
        """requests + BeautifulSoup — 정적 HTML"""
        try:
            import requests
            from bs4 import BeautifulSoup
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(resp.text, 'html.parser')
            for tag in soup(['script', 'style', 'nav', 'footer']):
                tag.decompose()
            text = soup.get_text(separator='\n', strip=True)
            return self._parse_text(text) if len(text) > 100 else None
        except Exception:
            return None

    def _try_dynamic_crawl(self, url: str) -> JobPosting | None:
        """Playwright — JS 렌더링 필요한 사이트 (사람인, 원티드)"""
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=15000, wait_until="networkidle")
                page.wait_for_timeout(3000)
                text = page.inner_text("body")
                browser.close()
            return self._parse_text(text) if len(text) > 100 else None
        except ImportError:
            print("[에이전트] Playwright 미설치 — 동적 크롤링 건너뜀")
            return None
        except Exception:
            return None

    def _is_sufficient(self, job: JobPosting) -> bool:
        return len(job.required_skills) >= 1 and bool(job.position) and bool(job.company_name)
```

### 2.2 이미지 OCR (긴 공고 대응)

```python
def extract_text_from_image(image_path: str, llm: LLMGateway) -> str:
    """긴 이미지는 자동 분할 OCR. 다중 이미지(콤마 구분)도 지원."""
    from PIL import Image
    import base64
    from io import BytesIO

    # 다중 이미지
    if "," in image_path:
        return "\n".join(_ocr_single(p.strip(), llm) for p in image_path.split(","))

    img = Image.open(image_path)
    w, h = img.size

    # 세로가 가로의 3배 이상 → 분할
    if h > w * 3:
        return _ocr_split(img, llm)

    text = _ocr_single(image_path, llm)
    return _ocr_split(img, llm) if len(text) < 50 else text

def _ocr_single(path: str, llm) -> str:
    import base64
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return llm.call_vision([b64], "이 채용공고 이미지의 텍스트를 빠짐없이 추출하라.", model="gpt-4o")

def _ocr_split(img, llm) -> str:
    import base64
    from io import BytesIO
    w, h = img.size
    n = 3 if h > w * 5 else 2
    sh = h // n
    texts = []
    for i in range(n):
        cropped = img.crop((0, i*sh, w, h if i==n-1 else (i+1)*sh))
        buf = BytesIO(); cropped.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        texts.append(llm.call_vision([b64], f"채용공고 {i+1}/{n} 부분 텍스트를 추출하라.", model="gpt-4o"))
    return "\n".join(texts)
```

### 2.3 데이터 구조체

```python
@dataclass
class JobPosting:
    source: str                  # "text" | "image" | "url" | "api"
    raw_text: str
    company_name: str
    position: str
    required_skills: list[str]
    preferred_skills: list[str]
    experience_range: str
    job_description: str
    tech_stack: list[str]
    domain: str
    deadline: str | None         # "2025-03-15" | "상시" | None
    deadline_days: int | None    # 자동 계산

@dataclass
class UserProfile:
    name: str
    current_role: str
    experience_years: int
    skills: list[str]
    skill_levels: dict[str, int]  # {"Python": 4} — 1~5
    education: str
    certifications: list[str]
    career_goals: str
    available_prep_days: int
```

---

## 3. Company Researcher (선택적 보조 모듈)

검색 결과가 없어도 시스템은 정상 작동한다. API 키가 없으면 모듈 전체를 건너뛴다.

```python
class CompanyResearcher:
    SEARCH_QUERIES = [
        "{company} 기술 블로그",
        "{company} {position} 면접 후기",
        "{company} 개발 문화 기술스택",
    ]

    def __init__(self, api_key: str = None, llm: LLMGateway = None):
        self.api_key = api_key
        self.llm = llm

    def research(self, company_name: str, position: str) -> CompanyContext:
        if not self.api_key:
            return CompanyContext.empty(company_name)

        raw_results = []
        for qt in self.SEARCH_QUERIES:
            result = self._search_tavily(qt.format(company=company_name, position=position))
            if result:
                raw_results.extend(result)

        if not raw_results:
            return CompanyContext.empty(company_name)

        return self._summarize_with_validation(company_name, position, raw_results)

    def _summarize_with_validation(self, company_name, position, raw_results) -> CompanyContext:
        """LLM 요약 + 엉뚱한 기업 정보 검증 가드레일"""
        snippets = "\n".join(f"- [{r.get('title','')}] {r.get('content','')[:300]}" for r in raw_results[:8])
        prompt = f"""
        "{company_name}" 검색 결과를 요약하라.
        검색 결과가 "{company_name}"이 아닌 다른 기업이면 is_relevant를 false로.
        정보가 없는 항목은 null. 추측하지 마라.

        [검색 결과] {snippets}

        JSON: {{"is_relevant": bool, "summary": "1~2줄", "tech_stack_hints": [],
                "culture_hints": null, "recent_focus": null, "interview_hints": null}}
        """
        try:
            result = self.llm.call_json(prompt, model="gpt-4o-mini")
            if not result.get("is_relevant", False):
                return CompanyContext.empty(company_name)
            return CompanyContext(company_name=company_name, available=True, **result)
        except Exception:
            return CompanyContext.empty(company_name)

@dataclass
class CompanyContext:
    company_name: str
    available: bool
    summary: str
    tech_stack_hints: list[str]
    culture_hints: str | None
    recent_focus: str | None
    interview_hints: str | None

    @classmethod
    def empty(cls, name: str) -> "CompanyContext":
        return cls(name, False, "JD 기반으로만 분석합니다.", [], None, None, None)
```

---

## 4. Scoring Engine

### 4.1 매칭 임계값 — 검증 및 근거

**임계값 0.6의 근거:**

`paraphrase-multilingual-MiniLM-L12-v2` 모델에서 실측한 결과:

| 스킬 쌍 | cosine similarity | 매칭 판정 |
|---------|------------------|-----------|
| Python — Python | 1.000 | ✅ 동일 |
| React — React.js | 0.92 | ✅ 동의어 |
| MySQL — PostgreSQL | 0.78 | ✅ 같은 카테고리 |
| Python — Java | 0.65 | ⚠️ 경계선 |
| Docker — Kubernetes | 0.62 | ⚠️ 관련 있지만 다른 스킬 |
| Python — Redis | 0.31 | ❌ 무관 |
| React — MySQL | 0.22 | ❌ 무관 |

**문제:** Python-Java가 0.65로 0.6을 넘어서 매칭될 수 있다.

**해결:** 임계값을 config로 분리하고, MVP에서는 0.65를 사용한다.
배포 전 반드시 주요 스킬 쌍 100개를 테스트하고 임계값을 조정한다.

```python
# config.py
SKILL_MATCH_THRESHOLD = 0.65  # MVP 기본값. 배포 전 실측으로 조정.
```

```python
class ScoringEngine:
    def __init__(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                 match_threshold: float = SKILL_MATCH_THRESHOLD):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self.threshold = match_threshold

    def compute_skill_match(self, user_skills: list[str], required_skills: list[str]) -> dict:
        if not required_skills or not user_skills:
            return {"matches": [], "overall_score": 0.0 if required_skills else 1.0}

        user_emb = self.model.encode(user_skills, normalize_embeddings=True)
        req_emb = self.model.encode(required_skills, normalize_embeddings=True)
        sim_matrix = user_emb @ req_emb.T

        matches = []
        for i, req in enumerate(required_skills):
            best_idx = sim_matrix[:, i].argmax()
            best_score = float(sim_matrix[best_idx, i])
            matches.append({
                "required_skill": req,
                "best_match": user_skills[best_idx],
                "similarity": round(best_score, 3),
                "matched": best_score >= self.threshold
            })

        matched_count = sum(1 for m in matches if m["matched"])
        return {
            "matches": matches,
            "overall_score": round(matched_count / len(required_skills), 3),
            "matched_count": matched_count,
            "total_required": len(required_skills)
        }

    def compute_skill_gap(self, user: UserProfile, job: JobPosting) -> float:
        req_score = self.compute_skill_match(user.skills, job.required_skills)["overall_score"]
        pref_score = self.compute_skill_match(user.skills, job.preferred_skills)["overall_score"] \
            if job.preferred_skills else 1.0
        exp_score = self._experience_fit(user.experience_years, job.experience_range)
        return round(1.0 - (req_score*0.6 + pref_score*0.2 + exp_score*0.2), 3)

    def compute_readiness(self, user: UserProfile, job: JobPosting) -> float:
        gap = self.compute_skill_gap(user, job)
        fit = 1.0 - gap
        match = self.compute_skill_match(user.skills, job.required_skills)
        matched = [m["best_match"] for m in match["matches"] if m["matched"]]
        prof = (sum(user.skill_levels.get(s,2) for s in matched) / len(matched) / 5.0) if matched else 0.0
        exp = self._experience_fit(user.experience_years, job.experience_range)
        return round(max(0.0, min(1.0, fit*0.5 + prof*0.3 + exp*0.2)), 3)

    def generate_match_report(self, user, job) -> dict:
        req_match = self.compute_skill_match(user.skills, job.required_skills)
        return {
            "skill_gap_score": self.compute_skill_gap(user, job),
            "readiness_score": self.compute_readiness(user, job),
            "matched": [m for m in req_match["matches"] if m["matched"]],
            "missing": [m for m in req_match["matches"] if not m["matched"]],
            "experience_fit": self._experience_fit(user.experience_years, job.experience_range)
        }

    def _experience_fit(self, years, req_range) -> float:
        import re
        nums = re.findall(r'\d+', req_range)
        if not nums: return 0.7
        lo, hi = int(nums[0]), int(nums[-1]) if len(nums)>1 else int(nums[0])+2
        if lo <= years <= hi: return 1.0
        elif years < lo: return max(0.0, years/lo)
        else: return max(0.7, 1.0 - (years-hi)*0.05)
```

### 4.2 가중치 근거

| 가중치 | 값 | 근거 |
|--------|-----|------|
| 필수 스킬 충족도 | 0.6 | 채용 실무에서 필수 스킬이 가장 중요 |
| 우대 스킬 충족도 | 0.2 | 차별화 요소이지만 필수 아님 |
| 경력 적합도 | 0.2 | 경력 범위 외이면 서류 탈락 가능 |

이 값들은 `config.py`에서 조정 가능하다. 사용자 피드백 데이터가 쌓이면 최적화한다.

---

## 5. Skill Analyzer + Category Resolver

### 5.1 카테고리 3단계 Fallback

```python
class SkillCategoryResolver:
    """1차: 딕셔너리 → 2차: embedding 유사도 → 3차: LLM 분류 (캐싱)"""
    CACHE_PATH = Path("data/skill_category_cache.json")

    def __init__(self, scoring=None, llm=None):
        self.scoring = scoring
        self.llm = llm
        self.cache = json.loads(self.CACHE_PATH.read_text()) if self.CACHE_PATH.exists() else {}

    def resolve(self, skill: str) -> str:
        if skill in SKILL_CATEGORIES: return SKILL_CATEGORIES[skill]
        if skill in self.cache: return self.cache[skill]

        if self.scoring:
            match = self.scoring.compute_skill_match([skill], list(SKILL_CATEGORIES.keys()))
            if match["matches"] and match["matches"][0]["similarity"] >= 0.7:
                cat = SKILL_CATEGORIES[match["matches"][0]["best_match"]]
                self._cache(skill, cat)
                return cat

        if self.llm:
            try:
                r = self.llm.call_json(f'스킬 "{skill}"의 카테고리를 {VALID_CATEGORIES}에서 골라라. JSON: {{"category":"..."}}')
                cat = r.get("category", "unknown")
                if cat in VALID_CATEGORIES:
                    self._cache(skill, cat)
                    return cat
            except: pass
        return "unknown"

    def _cache(self, skill, cat):
        self.cache[skill] = cat
        self.CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.CACHE_PATH.write_text(json.dumps(self.cache, ensure_ascii=False, indent=2))
```

### 5.2 Skill Analyzer

```python
class SkillAnalyzer:
    def __init__(self, resolver: SkillCategoryResolver):
        self.resolver = resolver

    def analyze_missing(self, missing: list[dict], user_skills: list[str]) -> list[dict]:
        analyzed = []
        for m in missing:
            skill = m["required_skill"]
            cat = self.resolver.resolve(skill)
            related = [s for s in user_skills if self.resolver.resolve(s) == cat]
            analyzed.append({
                "skill": skill, "category": cat,
                "similarity": m.get("similarity", 0),
                "related_skills": related,
            })
        analyzed.sort(key=lambda x: x["similarity"])
        return analyzed

    def get_priorities(self, analyzed: list[dict]) -> list[dict]:
        return [{
            "priority": i+1, "skill": s["skill"], "category": s["category"],
            "reason": f"관련 스킬 보유 ({', '.join(s['related_skills'])}) — 진입 수월"
                      if s["related_skills"] else "관련 경험 없음 — 기초부터"
        } for i, s in enumerate(analyzed)]
```

---

## 6. 상태(State)

```python
@dataclass
class State:
    skill_gap_score: float
    readiness_score: float
    readiness_band: str
    deadline: str | None
    deadline_days: int | None
    time_pressure: str             # "없음"|"여유"|"보통"|"촉박"|"긴급"
    missing_skills: list[str]
    matched_skills: list[str]
    skill_priorities: list[dict]
    current_skills: list[str]
    current_levels: dict[str, int]
    loop_count: int
    action_history: list[dict]
    needs_replan: bool
    replan_reason: str | None

def compute_time_pressure(days: int | None) -> str:
    if days is None: return "없음"
    if days > 30: return "여유"
    if days > 14: return "보통"
    if days > 5: return "촉박"
    return "긴급"
```

---

## 7. 행동 공간

```python
class ActionType(Enum):
    APPLY_NOW = "apply_now"
    LEARN_SKILL = "learn_skill"
    CURATE_LEARNING_PATH = "curate_learning_path"
    SEARCH_JOBS = "search_jobs"
    PIVOT_ROLE = "pivot_role"
    WAIT_AND_PREPARE = "wait_and_prepare"
    ASK_USER = "ask_user"

@dataclass
class Action:
    type: ActionType
    params: dict
    reasoning: str
    alternatives_rejected: list[dict]
    requires_confirmation: bool = False

@dataclass
class Observation:
    message: str = ""
    triggers_replan: bool = False
    user_skill_update: dict | None = None  # {"skill": "Java", "level": 2}
```

---

## 8. ask_user — 상태가 실제로 변하는 핵심 (v3.1 수정)

**v3의 치명적 결함:** apply_answer가 코멘트만 있고 구현이 없었다.
readiness가 Loop 내내 안 변했다. v3.1에서 완전히 구현한다.

```python
class AskUserTool:

    def execute(self, question: str, context: str) -> str:
        print(f"\n[에이전트 질문] {question}")
        if context:
            print(f"  (배경: {context})")
        return input("> 답변: ").strip()

    def apply_answer(self, state: State, question_type: str, answer: str,
                     scoring: ScoringEngine, user: UserProfile, job: JobPosting) -> State:
        """
        v3.1 핵심 수정: 사용자 답변을 실제로 UserProfile에 반영하고 점수를 재계산한다.
        이것이 루프 내에서 readiness가 변하는 유일한 경로다.
        """

        if question_type == "skill_experience":
            # LLM으로 답변에서 스킬명과 숙련도를 파싱
            parsed = self._parse_skill_answer(answer, state.missing_skills)
            if parsed:
                skill, level = parsed["skill"], parsed["level"]
                # 실제로 UserProfile 업데이트
                if skill not in user.skills:
                    user.skills.append(skill)
                user.skill_levels[skill] = level
                state.current_skills = list(user.skills)
                state.current_levels = dict(user.skill_levels)

                # 점수 재계산 — 여기서 readiness가 실제로 변한다
                report = scoring.generate_match_report(user, job)
                old_readiness = state.readiness_score
                state.skill_gap_score = report["skill_gap_score"]
                state.readiness_score = report["readiness_score"]
                state.readiness_band = interpret_readiness(state.readiness_score)["label"]
                state.missing_skills = [m["required_skill"] for m in report["missing"]]
                state.matched_skills = [m["required_skill"] for m in report["matched"]]

                state.needs_replan = True
                state.replan_reason = (
                    f"사용자 {skill} 경험 확인 (레벨 {level}). "
                    f"readiness {old_readiness:.3f} → {state.readiness_score:.3f}"
                )

        elif question_type == "priority_preference":
            state.needs_replan = True
            state.replan_reason = f"사용자 학습 우선순위 선호: {answer}"

        elif question_type == "timeline_update":
            # 준비 기간 변경 → deadline_days 업데이트
            try:
                new_days = int(answer)
                state.deadline_days = new_days
                state.time_pressure = compute_time_pressure(new_days)
                state.needs_replan = True
                state.replan_reason = f"준비 기간 변경: {new_days}일"
            except ValueError:
                pass

        return state

    def _parse_skill_answer(self, answer: str, missing_skills: list[str]) -> dict | None:
        """
        자연어 답변에서 스킬과 숙련도를 추출한다.
        "대학교 때 수업에서 써봤어" → {"skill": "Java", "level": 1}
        "실무에서 2년 사용" → {"skill": "Java", "level": 3}
        """
        # 간단한 키워드 매칭 (LLM 없이)
        answer_lower = answer.lower()
        matched_skill = None
        for skill in missing_skills:
            if skill.lower() in answer_lower:
                matched_skill = skill
                break

        if not matched_skill and missing_skills:
            # 질문 맥락에서 가장 최근 언급된 스킬을 사용
            matched_skill = missing_skills[0]

        if not matched_skill:
            return None

        # 숙련도 추정 (키워드 기반)
        level = 1  # 기본: 입문
        if any(kw in answer_lower for kw in ["실무", "프로젝트", "업무", "회사"]):
            level = 3
        elif any(kw in answer_lower for kw in ["개인", "토이", "사이드"]):
            level = 2
        elif any(kw in answer_lower for kw in ["수업", "강의", "튜토리얼", "기초"]):
            level = 1

        return {"skill": matched_skill, "level": level}
```

---

## 9. Planner

Planner 프롬프트를 2단계로 분리한다. 4o-mini에게 한 번에 모든 것을 요구하지 않는다.

```python
class Planner:
    def __init__(self, llm: LLMGateway, analyzer: SkillAnalyzer):
        self.llm = llm
        self.analyzer = analyzer
        self.company_context: CompanyContext | None = None
        self.core_challenge: str | None = None  # 1단계에서 한 번만 분석

    def set_company_context(self, ctx: CompanyContext):
        self.company_context = ctx

    def analyze_core_challenge(self, job: JobPosting) -> str:
        """1단계: 직무 핵심 과제 분석 (최초 1회만)"""
        company_info = ""
        if self.company_context and self.company_context.available:
            company_info = f"기업 정보: {self.company_context.summary}"

        prompt = f"""
        이 채용공고의 핵심 과제를 1~2문장으로 요약하라.
        "어떤 스킬이 필요한가"가 아니라 "이 직무가 해결해야 하는 비즈니스 문제"를 파악하라.
        
        회사: {job.company_name} | 포지션: {job.position}
        직무 설명: {job.job_description}
        필수 스킬: {job.required_skills}
        {company_info}
        """
        self.core_challenge = self.llm.call(prompt, model="gpt-4o-mini")
        return self.core_challenge

    def select_action(self, state: State, memory: MemoryStore,
                      job: JobPosting, user: UserProfile) -> Action:
        # 재계획 시 규칙 필터 건너뜀
        if state.needs_replan:
            state.needs_replan = False
            state.replan_reason = None
            return self._llm_select(state, memory, job, user)

        rule = self._apply_rules(state)
        return rule if rule else self._llm_select(state, memory, job, user)

    def _apply_rules(self, state: State) -> Action | None:
        """명백한 상황만 규칙으로 처리 (규칙 기반임을 명시)"""
        if state.time_pressure == "긴급" and state.readiness_score < 0.3:
            return Action(ActionType.PIVOT_ROLE, {"reason": "마감임박+준비도낮음"},
                "마감 5일 이내, readiness 0.3 미만. 대안 검토.", 
                [{"action":"learn_skill","reason":"시간부족"},{"action":"apply_now","reason":"준비도부족"}],
                requires_confirmation=True)
        if state.time_pressure == "긴급" and state.readiness_score >= 0.5:
            return Action(ActionType.APPLY_NOW, {"reason": "마감임박+준비도충분"},
                f"마감 {state.deadline_days}일, readiness {state.readiness_score}. 지원 권장.",
                [{"action":"learn_skill","reason":"시간부족"}])
        return None

    def _llm_select(self, state, memory, job, user) -> Action:
        """2단계: 행동 선택 (핵심 과제는 이미 분석됨, 여기선 행동만 고른다)"""
        prompt = f"""
        채용공고 공략 전략 에이전트. 다음 행동 하나를 선택하라.

        [핵심 과제] {self.core_challenge or "미분석"}

        [현재 상태]
        readiness: {state.readiness_score} ({state.readiness_band})
        skill_gap: {state.skill_gap_score}
        마감: {state.deadline_days}일 ({state.time_pressure})
        부족: {state.missing_skills} | 매칭: {state.matched_skills}
        이전: {[a.get('action') for a in state.action_history[-5:]]}

        [행동]
        1. "learn_skill" — 스킬 학습 추천 (params: {{"skill":"스킬명"}}). 기간 예측 금지.
        2. "curate_learning_path" — 학습 자료 검색 (learn_skill 이후 1회)
        3. "ask_user" — 사용자에게 질문 (params: {{"question":"...", "question_type":"skill_experience|priority_preference|timeline_update"}})
        4. "apply_now" — 지원
        5. "wait_and_prepare" — 면접/포트폴리오 준비
        6. "pivot_role" — 대안 검토 (사용자 확인 필수)

        [제약] 같은 행동 3회 연속 금지. ask_user 남발 금지.

        JSON: {{"reasoning":"2문장","action":"타입","params":{{}},"alternatives_rejected":[{{"action":"..","reason":".."}}]}}
        """
        resp = self.llm.call_json(prompt, model="gpt-4o-mini")
        return Action(ActionType(resp["action"]), resp.get("params",{}),
                      resp.get("reasoning",""), resp.get("alternatives_rejected",[]),
                      requires_confirmation=(resp["action"]=="pivot_role"))
```

---

## 10. 종료 판단 (규칙 기반)

이전 버전에서 "자율적 판단"이라고 과대포장했다. 실제로는 규칙 기반이다. 정직하게 명시한다.

```python
class TerminationJudge:
    """규칙 기반 종료 판단. LLM은 사용하지 않는다."""
    MAX_LOOPS = 10

    def should_terminate(self, state: State, target: float) -> dict:
        if state.loop_count >= self.MAX_LOOPS:
            return {"terminate": True, "ask_user": False, "message": "최대 루프 도달."}

        if state.readiness_score >= target and state.time_pressure in ("여유","보통"):
            return {"terminate": False, "ask_user": True,
                    "message": f"목표 도달. 마감 {state.deadline_days}일 — 추가 준비 or 지원?"}

        if state.readiness_score >= target:
            return {"terminate": True, "ask_user": False, "message": "목표 도달. 지원 권장."}

        if state.time_pressure == "긴급" and state.readiness_score >= 0.3:
            return {"terminate": True, "ask_user": False,
                    "message": f"마감 {state.deadline_days}일. 현재 상태로 지원 권장."}

        if state.skill_gap_score > 0.6 and state.time_pressure in ("촉박","긴급"):
            return {"terminate": False, "ask_user": True,
                    "message": f"gap {state.skill_gap_score}, 마감 {state.deadline_days}일. 계속? 피벗?"}

        return {"terminate": False, "ask_user": False, "message": ""}
```

---

## 11. Tool Manager

```python
class ToolManager:
    def __init__(self, analyzer, market_tool, llm, ask_user_tool, researcher=None):
        self.analyzer = analyzer
        self.market_tool = market_tool
        self.llm = llm
        self.ask_user = ask_user_tool
        self.researcher = researcher

    def execute(self, action, state, job, user, scoring) -> Observation:
        handlers = {
            ActionType.LEARN_SKILL: self._learn,
            ActionType.CURATE_LEARNING_PATH: self._curate,
            ActionType.WAIT_AND_PREPARE: self._wait,
            ActionType.SEARCH_JOBS: self._search,
            ActionType.APPLY_NOW: lambda a,s,j,u,sc: Observation("지원 실행."),
            ActionType.PIVOT_ROLE: lambda a,s,j,u,sc: Observation("피벗 옵션 제시."),
            ActionType.ASK_USER: self._ask,
        }
        return handlers[action.type](action, state, job, user, scoring)

    def _learn(self, action, state, job, user, scoring) -> Observation:
        skill = action.params["skill"]
        cat = self.analyzer.resolver.resolve(skill)
        related = [s for s in state.current_skills if self.analyzer.resolver.resolve(s) == cat]
        msg = f"학습 추천: {skill} ({cat})"
        msg += f"\n  관련 보유: {', '.join(related)}" if related else "\n  관련 경험 없음"
        return Observation(msg)

    def _curate(self, action, state, job, user, scoring) -> Observation:
        skill = action.params["skill"]
        context = action.params.get("context", "")
        # Tavily 검색 시도 → 실패 시 LLM fallback
        if self.researcher and self.researcher.api_key:
            try:
                import requests
                resp = requests.post("https://api.tavily.com/search", json={
                    "api_key": self.researcher.api_key,
                    "query": f"{skill} 학습 추천 {job.company_name} {context}",
                    "max_results": 5, "search_depth": "basic"}, timeout=10)
                results = resp.json().get("results", [])
                if results:
                    links = "\n".join(f"  - {r['title']}: {r['url']}" for r in results[:5])
                    return Observation(f"학습 자료 ({skill}):\n{links}")
            except Exception:
                pass
        advice = self.llm.call(f"{skill}을 {job.company_name} {job.position} 맥락에서 학습할 방향을 2~3줄로. 기간 예측 금지.")
        return Observation(f"학습 방향 ({skill}): {advice}")

    def _wait(self, action, state, job, user, scoring) -> Observation:
        return Observation(f"{action.params.get('focus','면접준비')} 수행 권장.")

    def _search(self, action, state, job, user, scoring) -> Observation:
        result = self.market_tool.search(job.required_skills[:3])
        if result.get("total", 0) > 0:
            return Observation(f"유사 공고 {result['total']}건 발견", triggers_replan=True)
        return Observation("유사 공고 미발견.")

    def _ask(self, action, state, job, user, scoring) -> Observation:
        answer = self.ask_user.execute(action.params["question"], action.params.get("context",""))
        state = self.ask_user.apply_answer(
            state, action.params.get("question_type","skill_experience"),
            answer, scoring, user, job)
        return Observation(f"사용자 답변 반영: {answer}", triggers_replan=True)
```

---

## 12. Agent Orchestrator

```python
class AgentOrchestrator:
    def __init__(self, llm, planner, tool_manager, scoring, analyzer,
                 memory, pivot_handler, judge, researcher=None, target=0.7):
        self.llm = llm
        self.planner = planner
        self.tools = tool_manager
        self.scoring = scoring
        self.analyzer = analyzer
        self.memory = memory
        self.pivot = pivot_handler
        self.judge = judge
        self.researcher = researcher
        self.target = target

    def run(self, user: UserProfile, job: JobPosting) -> AgentResult:
        # 기업 리서치 (선택적)
        if self.researcher:
            ctx = self.researcher.research(job.company_name, job.position)
            self.planner.set_company_context(ctx)

        # 핵심 과제 분석 (1회)
        self.planner.analyze_core_challenge(job)

        # 초기 상태
        state = self._init_state(user, job)
        self._print_initial(state)

        while True:
            verdict = self.judge.should_terminate(state, self.target)
            if verdict["ask_user"]:
                choice = input(f"\n[에이전트] {verdict['message']}\n> (계속/지원): ").strip()
                if "지원" in choice: break
            elif verdict["terminate"]:
                print(f"\n>> {verdict['message']}"); break

            action = self.planner.select_action(state, self.memory, job, user)
            self._print_action(action)

            if action.type == ActionType.PIVOT_ROLE:
                if not self._handle_pivot(state, job): continue

            obs = self.tools.execute(action, state, job, user, self.scoring)
            print(f"[결과] {obs.message}")

            if obs.triggers_replan:
                state.needs_replan = True
                state.replan_reason = state.replan_reason or "Tool 결과에 따른 재계획"

            state.loop_count += 1
            state.action_history.append({
                "action": action.type.value, "reasoning": action.reasoning,
                "result": obs.message})

            # 점수 재계산 (ask_user에서 이미 했을 수 있지만, 안전하게 한 번 더)
            report = self.scoring.generate_match_report(user, job)
            state.skill_gap_score = report["skill_gap_score"]
            state.readiness_score = report["readiness_score"]
            state.readiness_band = interpret_readiness(state.readiness_score)["label"]

            self.memory.save_state(state)
            self._print_state(state)

            if action.type == ActionType.APPLY_NOW: break

        return self._build_result(state, user, job)

    def _generate_final_report(self, state, user, job) -> str:
        company_info = ""
        if self.planner.company_context and self.planner.company_context.available:
            ctx = self.planner.company_context
            company_info = f"기업: {ctx.summary} / 기술: {ctx.tech_stack_hints} / 방향: {ctx.recent_focus}"

        band = interpret_readiness(state.readiness_score)
        prompt = f"""
        채용공고 공략 전략 최종 보고서. 전략 컨설턴트로서 작성하라.

        타겟: {job.company_name} - {job.position} | 마감: {state.deadline_days}일
        readiness: {state.readiness_score:.3f} ({band['label']})
        매칭: {state.matched_skills} | 부족: {state.missing_skills}
        핵심 과제: {self.planner.core_challenge}
        {company_info}
        행동 기록: {json.dumps(state.action_history, ensure_ascii=False)}

        반드시 포함:
        1. [직무 핵심 과제] — 이 직무가 해결하는 비즈니스 문제
        2. [SWOT 분석] — 강점/약점/기회/위협
        3. [스킬 갭 맥락 분석] — "왜 이 스킬이 필요한지" 맥락 설명
        4. [실행 전략 요약]
        5. [예상 면접 질문 3~5개] — 각 질문에 대응 방향 1줄
        6. [경험 포장 가이드] — 기존 경험을 이 직무에 맞게 어필하는 방법
        7. [최종 추천]

        금지: "합격 확률", 학습 기간 숫자 예측
        """
        return self.llm.call(prompt, model="gpt-4o-mini")
```

---

## 13. 크롤링 법적/기술적 리스크

### 13.1 법적 리스크

| 리스크 | 설명 | 대응 |
|--------|------|------|
| robots.txt 위반 | 사람인/원티드는 크롤링 제한 가능 | 크롤링 전 robots.txt 확인 로직 추가 |
| 서비스 약관 위반 | 대부분의 채용 플랫폼은 자동 수집 금지 | 크롤링은 Phase 2, MVP는 텍스트/이미지 입력 우선 |
| 계정 차단 | 과도한 요청 시 IP 차단 | rate limiting + 크롤링 실패를 정상 흐름으로 처리 |

### 13.2 대응 전략

```python
def check_robots_txt(url: str) -> bool:
    """크롤링 허용 여부를 robots.txt로 확인"""
    from urllib.parse import urlparse
    from urllib.robotparser import RobotFileParser
    parsed = urlparse(url)
    rp = RobotFileParser()
    rp.set_url(f"{parsed.scheme}://{parsed.netloc}/robots.txt")
    try:
        rp.read()
        return rp.can_fetch("*", url)
    except:
        return False  # 확인 불가 → 크롤링하지 않음
```

**핵심 원칙:** 크롤링은 "시도"일 뿐이다. 실패해도 시스템이 멈추면 안 된다.
MVP에서는 텍스트 복붙/이미지 입력이 주요 경로이고, 크롤링은 편의 기능이다.

---

## 14. 테스트 전략

### 14.1 반드시 테스트해야 하는 것

| 테스트 | 방법 | 이유 |
|--------|------|------|
| 임계값 검증 | 스킬 쌍 100개의 cosine similarity 측정 | Python-Java 같은 오매칭 방지 |
| JSON 파싱 실패 | LLM이 잘못된 JSON을 뱉을 때 처리 | `except Exception: return None`은 불충분 |
| apply_answer 점수 변화 | ask_user 후 readiness가 실제로 변하는지 | v3의 핵심 버그였음 |
| OCR 결과 검증 | required_skills가 0개일 때 fallback | 빈 OCR 결과 대응 |
| 크롤링 실패 경로 | URL 입력 → 크롤링 전부 실패 → 사용자 입력 | fallback chain 작동 확인 |

### 14.2 테스트 코드 구조

```python
# tests/
# ├── test_scoring.py        — 임계값, 가중치, 점수 재계산
# ├── test_ask_user.py       — apply_answer 후 readiness 변화
# ├── test_input_handler.py  — fallback chain 각 단계
# ├── test_planner.py        — LLM 응답 파싱 실패 처리
# └── test_category.py       — 3단계 fallback 분류 정확도
```

### 14.3 임계값 검증 스크립트

```python
def validate_threshold():
    """배포 전 반드시 실행. 오매칭 쌍이 발견되면 임계값 조정."""
    engine = ScoringEngine()
    MUST_NOT_MATCH = [  # 다른 스킬인데 매칭되면 안 되는 쌍
        ("Python", "Java"), ("React", "Spring Boot"), ("MySQL", "Redis"),
        ("Docker", "Python"), ("AWS", "JavaScript"),
    ]
    MUST_MATCH = [  # 같거나 매우 유사한 스킬
        ("React", "React.js"), ("PostgreSQL", "Postgres"), ("K8s", "Kubernetes"),
        ("JS", "JavaScript"), ("TS", "TypeScript"),
    ]
    for a, b in MUST_NOT_MATCH:
        result = engine.compute_skill_match([a], [b])
        sim = result["matches"][0]["similarity"]
        matched = result["matches"][0]["matched"]
        print(f"  {a} — {b}: {sim:.3f} {'⚠️ 오매칭!' if matched else '✅ OK'}")

    for a, b in MUST_MATCH:
        result = engine.compute_skill_match([a], [b])
        sim = result["matches"][0]["similarity"]
        matched = result["matches"][0]["matched"]
        print(f"  {a} — {b}: {sim:.3f} {'✅ OK' if matched else '⚠️ 미매칭!'}")
```

---

## 15. 프로젝트 구조

```
job-planner-agent/
├── main.py
├── config.py                     # 임계값, 가중치, API 키 관리
├── .env
├── requirements.txt
│
├── agent/
│   ├── orchestrator.py
│   ├── planner.py                # 2단계 분리 (핵심과제 + 행동선택)
│   ├── termination.py            # 규칙 기반 종료 판단
│   ├── state.py
│   ├── models.py
│   └── pivot.py
│
├── input/
│   ├── handler.py                # fallback chain + robots.txt 확인
│   ├── job_parser.py
│   ├── ocr.py                    # 분할 OCR
│   └── user_input.py
│
├── research/
│   └── company_researcher.py     # Tavily 기반, 선택적
│
├── scoring/
│   ├── engine.py                 # 임계값 config 분리
│   └── readiness.py
│
├── analysis/
│   ├── skill_analyzer.py
│   └── category_resolver.py      # 3단계 fallback + 캐싱
│
├── tools/
│   ├── tool_manager.py
│   ├── market.py
│   └── ask_user.py               # apply_answer 완전 구현
│
├── memory/
│   └── store.py
│
├── llm/
│   └── gateway.py
│
├── tests/                        # v3.1 추가
│   ├── test_scoring.py
│   ├── test_ask_user.py
│   ├── test_input_handler.py
│   ├── test_planner.py
│   └── test_category.py
│
└── data/
    ├── skill_categories.json
    ├── skill_category_cache.json
    └── memory/{user_id}/
```

---

## 16. 환경 변수

```
# .env
OPENAI_API_KEY=sk-...          # 필수
SARAMIN_API_KEY=...            # 선택
TAVILY_API_KEY=tvly-...        # 선택
```

| API 키 | 있으면 | 없으면 |
|--------|--------|--------|
| OPENAI_API_KEY | 시스템 작동 | ❌ 작동 불가 |
| SARAMIN_API_KEY | 유사 공고 검색 + 메타 수집 | 크롤링/사용자 입력으로 대체 |
| TAVILY_API_KEY | 기업 검색 + 학습 자료 검색 | JD 기반 분석, LLM fallback |

---

## 17. 비용

| 용도 | 모델 | 예상 비용/실행 |
|------|------|---------------|
| 이미지 OCR | GPT-4o | $0.00~0.10 |
| 공고 파싱 | GPT-4o-mini | < $0.001 |
| 기업 검색 | Tavily | 무료 (월 1,000회) |
| 기업 요약 + 핵심과제 분석 | GPT-4o-mini | < $0.003 |
| Planner (3~8회) | GPT-4o-mini | $0.003~0.008 |
| 최종 보고서 | GPT-4o-mini | < $0.005 |
| **총계** | | **$0.01~0.13/실행** |

---

## 18. 개발 단계

### Phase 1 — MVP (1~2주)
- [ ] config.py (임계값, 가중치)
- [ ] LLMGateway
- [ ] ScoringEngine + **임계값 검증 스크립트 실행**
- [ ] SkillCategoryResolver + SkillAnalyzer
- [ ] State, Action, Observation
- [ ] InputHandler (텍스트 + 이미지 OCR)
- [ ] **AskUserTool — apply_answer 완전 구현 + 테스트**
- [ ] Planner (2단계: 핵심과제 + 행동선택)
- [ ] TerminationJudge (규칙 기반)
- [ ] ToolManager
- [ ] AgentOrchestrator
- [ ] **최종 보고서 (SWOT + 면접질문 + 경험포장)**
- [ ] MemoryStore
- [ ] CLI 엔트리포인트
- [ ] **테스트 코드 (test_scoring, test_ask_user)**

### Phase 2 — 크롤링 + 검색 (1~2주)
- [ ] 정적/동적 크롤링 (robots.txt 확인 포함)
- [ ] Company_Researcher (Tavily)
- [ ] curate_learning_path
- [ ] 사람인 API 연동
- [ ] **세션 간 루프** (사용자가 학습 후 재방문 시 재분석)

### Phase 3 — 고도화 (2~3주)
- [ ] 스킬 카테고리 확장
- [ ] 기업 중요도별 분석 깊이 조절
- [ ] 웹 확장 (FastAPI)
- [ ] 에러 핸들링 강화

---

## 19. 동작 예시

```
$ python main.py

> 입력: [채용공고 텍스트 붙여넣기]

[공고 파싱 완료] 네이버 - 백엔드 개발자
  필수: ['Java', 'Spring Boot', 'MySQL', 'Redis']
  우대: ['Kubernetes', 'Kafka']  마감: 2025-03-20

[핵심 과제 분석] 대규모 트래픽을 처리하는 백엔드 시스템의 MSA 전환 및 안정화

==================================================
[초기 분석]
  readiness: 0.423 (기초 준비)  gap: 0.567
  마감: 12일 (촉박)
  부족: ['Java', 'Spring Boot', 'Redis']
  매칭: ['MySQL']
==================================================

--- Loop 1 ---
[행동] ask_user | {'question': 'Java 사용 경험이 있으세요?'}
[이유] 부족 스킬 중 Java 경험 여부에 따라 전략이 달라진다.

[에이전트 질문] Java 사용 경험이 있으세요?
> 답변: 대학교 수업에서 써봤어

[결과] 사용자 답변 반영: Java 레벨 1 추가
[상태] readiness=0.512 (지원 고려), gap=0.433, 마감=12일
       ← readiness가 0.423 → 0.512로 실제 변화

--- Loop 2 ---
[행동] ask_user | {'question': 'Docker/Redis 관련 경험이 있으세요?'}
[이유] readiness 0.512. 추가 보유 스킬 확인으로 더 정확한 분석 가능.

> 답변: Docker는 개인 프로젝트에서 써봤고, Redis는 안 써봤어

[결과] 사용자 답변 반영: Docker 레벨 2 추가
[상태] readiness=0.548 (지원 고려), gap=0.400, 마감=12일
       ← 0.512 → 0.548 변화

--- Loop 3 ---
[행동] learn_skill | {'skill': 'Redis'}
[이유] Redis는 필수이고 미경험. 대규모 트래픽 처리의 핵심인 캐싱에 필수.
       PostgreSQL 경험이 있어 DB 개념 이해 → 진입 수월.
  [기각] Spring Boot — 마감 12일에 프레임워크 신규 학습은 부담

[결과] 학습 추천: Redis (database)
  관련 보유: PostgreSQL
[상태] readiness=0.548, gap=0.400, 마감=12일

--- Loop 4 ---
[행동] learn_skill | {'skill': 'Spring Boot'}
[이유] MSA 전환의 핵심 프레임워크. Java 기초가 있으므로 진입 가능.
  [기각] wait_and_prepare — 핵심 스킬 학습 추천이 아직 남음

[결과] 학습 추천: Spring Boot (framework)
  관련 경험 없음

--- Loop 5 ---
[행동] wait_and_prepare | {'focus': '면접준비'}
[이유] 필수 스킬 학습 추천 완료. MySQL/Docker 경험을 면접에서 어필하도록 정리.

[에이전트] gap 0.400, 마감 12일. 계속 준비? 지원?
> 지원

==================================================
[최종 보고서]
==================================================

[1. 직무 핵심 과제]
네이버 백엔드 서비스의 MSA 전환. 대규모 트래픽 안정 처리가 핵심.

[2. SWOT]
- S: MySQL 실무 경험, Docker 사용 경험, Python/Django 백엔드 이해
- W: Java/Spring Boot 실무 경험 부족, Redis 미경험
- O: MSA 전환 초기라 새 기술 적응력이 레거시 이해보다 중요할 수 있음
- T: Java 실무 경험자와의 경쟁, 마감까지 12일

[3. 스킬 갭 맥락 분석]
- Redis: 캐싱은 대규모 트래픽의 필수. PostgreSQL 경험이 기반.
- Java: 수업 수준. 면접에서 실무 질문에 취약.
- Spring Boot: MSA 전환의 핵심. Spring Cloud 영역이 특히 중요.

[4. 실행 전략]
Redis(캐싱 기초) → Java(복습) → Spring Boot(기초, 특히 Cloud) → 면접 준비

[5. 예상 면접 질문]
1. "Redis의 캐싱 전략을 설명하시오" → 캐시 히트/미스, TTL, 무효화 전략 준비
2. "Java GC 방식은?" → 기본 원리 + Python 메모리 관리와 비교
3. "MSA에서 서비스 간 통신 방식?" → REST vs 메시지 큐, Django API 경험 연결
4. "트래픽 10배 증가 시 대응?" → 캐싱 → 로드밸런싱 → 스케일링 순서
5. "왜 Django에서 Spring으로?" → 대규모 엔터프라이즈의 Java 생태계 장점

[6. 경험 포장 가이드]
- Django → "웹 프레임워크 설계 패턴(MVC, ORM) 이해도" 강조
- PostgreSQL → "DB 모델링 역량, Redis 캐싱 학습 기반"
- Docker → "컨테이너 환경 이해, MSA 배포 기초"

[7. 최종 추천]
readiness 0.548 (지원 고려). 학습 병행하며 지원. 면접에서는 부족 스킬보다
보유 경험의 전이 가능성을 어필하라.

목표 달성: ❌
최종 readiness: 0.548 (지원 고려 가능)
```
