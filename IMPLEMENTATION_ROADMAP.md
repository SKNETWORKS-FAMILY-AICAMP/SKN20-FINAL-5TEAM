# 종합 구현 전략: 에이전트 기반 학습 성장 플랫폼

## 🎯 최종 목표

```
현재:
"분석 → 추천 → 끝"
사용자 경험: 60점 (분석은 좋은데 그 이후가...)

목표 (3개월):
"분석 → 학습 → 실습 → 검증 → 피드백 → 재분석 → 격려 → 반복"
사용자 경험: 85점 (완전한 학습 성장 플랫폼)

KPI:
- 사용자 만족도: 60% → 85% (+25%)
- 월간 활성 사용자: 100명 → 300명 (+200%)
- 평균 사용 시간: 3주 → 8주 (+5주)
- 약점 극복률: 40% → 75% (+35%)
```

---

## 📅 Phase별 구현 계획

### Phase 1: 기반 마련 (1주) - 데이터 모델 & DB 설계

#### 1-1. DB 모델 추가

**새로운 모델 생성:**

```python
# backend/core/models.py (추가)

class AnalysisHistory(models.Model):
    """사용자 분석 이력"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    analysis_result = models.JSONField()  # {summary, weaknesses, strengths}
    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-analyzed_at']
        indexes = [
            models.Index(fields=['user', '-analyzed_at']),
        ]

class VerificationResult(models.Model):
    """검증 결과"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    focus_weakness = models.CharField(max_length=100)  # "edge_case"
    recommended_problems = models.JSONField()  # [problem_id, ...]

    # 검증 전 데이터
    initial_score = models.FloatField()
    initial_analysis = models.JSONField()

    # 검증 후 데이터
    improved = models.BooleanField()
    improvement_level = models.CharField(
        max_length=10,
        choices=[('HIGH', 'High'), ('MEDIUM', 'Medium'), ('LOW', 'Low')]
    )
    verification_result = models.JSONField()
    verified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-verified_at']
        indexes = [
            models.Index(fields=['user', 'focus_weakness', '-verified_at']),
        ]

class GeneratedProblem(models.Model):
    """생성된 맞춤형 문제"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    focus_weakness = models.CharField(max_length=100)
    difficulty = models.CharField(
        max_length=10,
        choices=[('EASY', 'Easy'), ('MEDIUM', 'Medium'), ('HARD', 'Hard')]
    )
    problem_data = models.JSONField()  # {title, description, examples, ...}
    generated_at = models.DateTimeField(auto_now_add=True)

    # 피드백
    solved = models.BooleanField(default=False)
    score = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-generated_at']

class LearningProgress(models.Model):
    """학습 진행도"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    weakness = models.CharField(max_length=100)

    # 개선 추이
    initial_score = models.FloatField()
    current_score = models.FloatField()
    attempt_count = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('NOT_STARTED', 'Not Started'),
            ('IMPROVING', 'Improving'),
            ('STAGNANT', 'Stagnant'),
            ('COMPLETED', 'Completed')
        ],
        default='NOT_STARTED'
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['user', 'weakness']]
        indexes = [
            models.Index(fields=['user', 'status']),
        ]

class FeedbackLog(models.Model):
    """사용자 피드백 (학습 후 결과)"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    problem_type = models.CharField(max_length=50)  # "recommended", "generated"
    problem_id = models.CharField(max_length=50, null=True, blank=True)
    weakness = models.CharField(max_length=100)

    score = models.FloatField()
    helpful_flag = models.BooleanField(null=True)  # 도움 되었는가?

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
```

#### 1-2. Migration 작성

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 1-3. 체크리스트

```
□ DB 모델 코드 작성
□ 마이그레이션 생성
□ DB 마이그레이션 적용
□ 인덱스 생성 확인
□ 백업 계획 수립
```

---

### Phase 2: 에이전트 기본 구현 (2주)

#### 2-1. Verification Agent 구현

**파일: `backend/core/agents/verification_agent.py` (신규)**

```python
import json
import logging
from typing import Dict, Any
from openai import OpenAI
from core.models import VerificationResult, UserSolvedProblem

logger = logging.getLogger(__name__)
client = OpenAI()
AGENT_MODEL = "gpt-4o-mini"

def run_verification_agent(
    user_profile,
    focus_weakness: str,
    initial_score: float,
    initial_analysis: Dict[str, Any],
    verification_window_days: int = 7
) -> Dict[str, Any]:
    """
    검증 에이전트: 사용자가 실제로 약점을 극복했는가?

    Args:
        user_profile: 사용자 프로필
        focus_weakness: 검증 대상 약점 (예: "edge_case")
        initial_score: 이전 점수 (예: 45)
        initial_analysis: 이전 분석 결과
        verification_window_days: 검증 기간 (기본 7일)

    Returns:
        {
            "improved": bool,
            "improvement_level": "HIGH/MEDIUM/LOW",
            "improvement_percentage": float,
            "evidence": [...],
            "remaining_issues": [...],
            "next_step": "CONTINUE/ADVANCE/REMEDIAL"
        }
    """

    # 1. 검증 기간 동안의 풀이 기록 조회
    from datetime import timedelta
    from django.utils import timezone

    cutoff_date = timezone.now() - timedelta(days=verification_window_days)
    recent_problems = UserSolvedProblem.objects.filter(
        user=user_profile,
        solved_date__gte=cutoff_date,
        submitted_data__isnull=False
    ).order_by('-solved_date')[:5]

    if not recent_problems:
        return {
            "improved": False,
            "improvement_level": "NONE",
            "evidence": ["검증 기간 내 풀이 기록이 없습니다"],
            "next_step": "REMEDIAL"
        }

    # 2. 현재 점수 계산
    current_scores = [p.score for p in recent_problems if p.score]
    if not current_scores:
        current_score = 0
    else:
        current_score = sum(current_scores) / len(current_scores)

    # 3. OpenAI에 검증 요청
    problems_data = []
    for sp in recent_problems:
        problems_data.append({
            "problem_title": str(sp.practice_detail),
            "score": sp.score,
            "submitted_data": sp.submitted_data[:500],  # 처음 500자만
            "solved_date": sp.solved_date.isoformat()
        })

    prompt = f"""
당신은 프로그래머의 성장을 평가하는 전문가입니다.

검증 대상 약점: {focus_weakness}
이전 점수: {initial_score}
현재 점수: {current_score}

검증 기간 풀이 결과:
{json.dumps(problems_data, ensure_ascii=False, indent=2)}

이전 분석:
{json.dumps(initial_analysis, ensure_ascii=False, indent=2)}

질문:
1. 약점이 실제로 개선되었는가?
2. 개선 수준은 어느 정도인가? (HIGH/MEDIUM/LOW)
3. 개선의 구체적 증거는?
4. 여전히 부족한 부분은?
5. 다음 스텝은 어떻게 해야 하는가?

JSON 형식 응답:
{{
  "improved": boolean,
  "improvement_level": "HIGH/MEDIUM/LOW",
  "improvement_percentage": 0-100,
  "evidence": [
    "구체적 개선 증거 1",
    "구체적 개선 증거 2"
  ],
  "remaining_issues": [
    "여전히 부족한 부분 1",
    "여전히 부족한 부분 2"
  ],
  "next_step": "CONTINUE/ADVANCE/REMEDIAL"
}}
"""

    try:
        response = client.chat.completions.create(
            model=AGENT_MODEL,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.choices[0].message.content
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(response_text)

        # DB에 저장
        VerificationResult.objects.create(
            user=user_profile,
            focus_weakness=focus_weakness,
            recommended_problems=[p.practice_detail_id for p in recent_problems],
            initial_score=initial_score,
            initial_analysis=initial_analysis,
            improved=result.get("improved", False),
            improvement_level=result.get("improvement_level", "LOW"),
            verification_result=result
        )

        logger.info(f"[Verification] {user_profile.id} - {focus_weakness}: {result.get('improvement_level')}")
        return result

    except Exception as e:
        logger.error(f"Verification Agent 오류: {e}")
        return {
            "improved": False,
            "improvement_level": "ERROR",
            "evidence": [f"검증 중 오류: {str(e)}"],
            "next_step": "REMEDIAL"
        }
```

#### 2-2. API 엔드포인트 추가

**파일: `backend/core/views/agent_view.py` (수정)**

```python
# 기존 코드에 추가

class VerificationView(APIView):
    """검증 API"""

    def post(self, request):
        """
        검증 실행

        요청:
        {
            "focus_weakness": "edge_case",
            "initial_score": 45,
            "initial_analysis": {...}
        }
        """
        try:
            user_profile = UserProfile.objects.get(email=request.user.email)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "사용자 프로필을 찾을 수 없습니다"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        focus_weakness = request.data.get('focus_weakness')
        initial_score = request.data.get('initial_score', 0)
        initial_analysis = request.data.get('initial_analysis', {})

        from core.agents.verification_agent import run_verification_agent

        result = run_verification_agent(
            user_profile,
            focus_weakness,
            initial_score,
            initial_analysis
        )

        return Response(result, status=status.HTTP_200_OK)
```

#### 2-3. URLs 등록

```python
# backend/core/urls.py (기존 urls에 추가)

from core.views.agent_view import VerificationView

urlpatterns = [
    # ... 기존 urls ...
    path('agents/verify/', VerificationView.as_view(), name='verify'),
]
```

#### 2-4. 체크리스트

```
□ Verification Agent 코드 작성
□ API 뷰 작성
□ URL 라우팅 등록
□ 로컬 테스트
□ 에러 핸들링 검증
```

---

### Phase 3: 추가 에이전트 구현 (2주)

#### 3-1. Adaptive Roadmap Agent

**파일: `backend/core/agents/adaptive_roadmap_agent.py` (신규)**

```python
import json
import logging
from typing import Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)
client = OpenAI()
AGENT_MODEL = "gpt-4o-mini"

def run_adaptive_roadmap_agent(
    verification_result: Dict[str, Any],
    current_weakness: str,
    all_weaknesses: list
) -> Dict[str, Any]:
    """
    적응형 로드맵 에이전트

    Verification 결과에 따라 다음 학습 경로 결정
    """

    improvement_level = verification_result.get("improvement_level", "LOW")
    next_step = verification_result.get("next_step", "REMEDIAL")

    if next_step == "CONTINUE":
        # 다음 약점으로 진행
        next_weakness = _select_next_weakness(current_weakness, all_weaknesses)
        return {
            "roadmap_type": "ADVANCE",
            "next_weakness": next_weakness,
            "message": f"{current_weakness} 마스터 완료! 이제 {next_weakness}으로 이동합니다.",
            "recommended_problems": _get_recommended_problems(next_weakness),
            "learning_path": _get_learning_path(next_weakness)
        }

    elif next_step == "ADVANCE":
        # 같은 약점, 심화 문제
        return {
            "roadmap_type": "DEEPEN",
            "next_weakness": current_weakness,
            "message": f"{current_weakness} 기본을 마스터했어요. 이제 심화 문제로 도전해봅시다.",
            "difficulty": "HARD",
            "recommended_problems": _get_recommended_problems(current_weakness, difficulty="HARD"),
            "learning_path": _get_learning_path(current_weakness, level="advanced")
        }

    else:  # REMEDIAL
        # 다른 각도로 재학습
        return {
            "roadmap_type": "REMEDIAL",
            "next_weakness": current_weakness,
            "message": f"{current_weakness}를 다른 각도에서 다시 학습해봅시다.",
            "approach": "DIFFERENT_ANGLE",
            "recommended_approach": _analyze_better_approach(verification_result),
            "recommended_problems": _get_recommended_problems(current_weakness, level="remedial")
        }

def _select_next_weakness(current: str, all_weaknesses: list) -> str:
    """다음 약점 선택 (현재 기준 다음 약점)"""
    weakness_priority = [
        "edge_case",
        "root_cause",
        "security",
        "logic_design",
        "performance",
        "readability"
    ]

    try:
        current_idx = weakness_priority.index(current)
        for next_weakness in weakness_priority[current_idx + 1:]:
            if next_weakness in all_weaknesses:
                return next_weakness
    except (ValueError, IndexError):
        pass

    return all_weaknesses[0] if all_weaknesses else "general_improvement"

def _analyze_better_approach(verification_result: Dict) -> Dict:
    """더 나은 접근 방법 분석"""
    remaining_issues = verification_result.get("remaining_issues", [])

    # LLM에 다른 접근 방법 요청
    prompt = f"""
사용자의 약점 극복이 진행 중입니다.

여전히 부족한 부분:
{json.dumps(remaining_issues, ensure_ascii=False)}

더 나은 접근 방법은 무엇일까요?

JSON 형식:
{{
  "root_cause": "근본 원인 분석",
  "suggested_approach": "제안하는 새로운 방법",
  "recommended_first_step": "첫 번째 시도할 것"
}}
"""

    try:
        response = client.chat.completions.create(
            model=AGENT_MODEL,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.choices[0].message.content
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        return json.loads(response_text)
    except:
        return {"suggested_approach": "기초 개념부터 다시 학습"}

# ... 추가 헬퍼 함수들 ...
```

#### 3-2. Problem Generation Agent

**파일: `backend/core/agents/problem_generation_agent.py` (신규)**

```python
import json
import logging
from typing import Dict, Any
from openai import OpenAI
from core.models import GeneratedProblem

logger = logging.getLogger(__name__)
client = OpenAI()
AGENT_MODEL = "gpt-4o-mini"

def run_problem_generation_agent(
    user_profile,
    weakness: str,
    difficulty: str = "MEDIUM",
    user_submitted_code: str = None,
    generation_reason: str = "FIRST_ATTEMPT"
) -> Dict[str, Any]:
    """
    문제 생성 에이전트

    Args:
        user_profile: 사용자 프로필
        weakness: 약점 (예: "null/empty 입력 처리 부족")
        difficulty: 난이도 (EASY/MEDIUM/HARD)
        user_submitted_code: 사용자의 최근 제출 코드
        generation_reason: 생성 사유 (FIRST_ATTEMPT/RETRY/DEEPEN)

    Returns:
        생성된 문제 데이터
    """

    # 1. 사용자 코드 수집 (없으면 skip)
    if not user_submitted_code:
        from core.models import UserSolvedProblem
        recent_submission = UserSolvedProblem.objects.filter(
            user=user_profile,
            submitted_data__isnull=False
        ).order_by('-solved_date').first()

        if recent_submission:
            user_submitted_code = recent_submission.submitted_data[:1000]

    # 2. 프롬프트 구성
    code_context = f"사용자의 최근 코드:\n```\n{user_submitted_code}\n```" if user_submitted_code else ""

    difficulty_guidance = {
        "EASY": "기본 개념만 적용하는 쉬운 문제",
        "MEDIUM": "실제 상황에서 적용 가능한 중간 난이도 문제",
        "HARD": "엣지 케이스와 복잡한 상황을 포함한 어려운 문제"
    }

    prompt = f"""
당신은 프로그래밍 교사입니다.
학생의 약점에 정확히 맞춘 맞춤형 문제를 생성하세요.

약점: {weakness}
난이도: {difficulty} - {difficulty_guidance.get(difficulty, '')}
생성 사유: {generation_reason}

{code_context}

요구사항:
1. 학생의 현재 코드 스타일과 유사하게
2. 정확히 이 약점을 다루는
3. 단계적으로 풀 수 있는
4. 실제 상황과 유사한

문제를 생성하세요.

JSON 형식 (필수):
{{
  "problem_title": "명확하고 이해하기 쉬운 제목",
  "problem_description": "문제 설명 (2-3문장)",
  "problem_statement": "상세 설명",
  "input_format": "입력 형식 설명",
  "output_format": "출력 형식 설명",
  "examples": [
    {{"input": "...", "output": "...", "explanation": "..."}}
  ],
  "constraints": ["제약사항 1", "제약사항 2"],
  "hints": [
    "힌트 1",
    "힌트 2"
  ],
  "learning_focus": "이 문제로 배울 핵심 개념",
  "step_by_step_guide": ["첫 번째 단계", "두 번째 단계", ...]
}}
"""

    try:
        response = client.chat.completions.create(
            model=AGENT_MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.choices[0].message.content
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        problem_data = json.loads(response_text)

        # DB에 저장
        generated_problem = GeneratedProblem.objects.create(
            user=user_profile,
            focus_weakness=weakness,
            difficulty=difficulty,
            problem_data=problem_data
        )

        logger.info(f"[Problem Generation] {user_profile.id} - {weakness} ({difficulty})")

        return {
            "problem_id": str(generated_problem.id),
            "problem_data": problem_data,
            "created_at": generated_problem.generated_at.isoformat()
        }

    except Exception as e:
        logger.error(f"Problem Generation 오류: {e}")
        return {
            "error": str(e),
            "fallback_message": "문제 생성 중 오류가 발생했습니다. 기존 문제를 추천드립니다."
        }
```

#### 3-3. 체크리스트

```
□ Adaptive Roadmap Agent 구현
□ Problem Generation Agent 구현
□ API 엔드포인트 추가
□ URL 라우팅 등록
□ 로컬 테스트
```

---

### Phase 4: 문제 생성 통합 (1주)

#### 4-1. Problem Generation View

```python
# backend/core/views/agent_view.py 추가

class ProblemGenerationView(APIView):
    """맞춤형 문제 생성 API"""

    def post(self, request):
        """
        맞춤형 문제 생성

        요청:
        {
            "weakness": "null 처리 부족",
            "difficulty": "MEDIUM",
            "generation_reason": "RETRY"
        }
        """
        try:
            user_profile = UserProfile.objects.get(email=request.user.email)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "사용자 프로필을 찾을 수 없습니다"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        weakness = request.data.get('weakness')
        difficulty = request.data.get('difficulty', 'MEDIUM')
        generation_reason = request.data.get('generation_reason', 'FIRST_ATTEMPT')

        from core.agents.problem_generation_agent import run_problem_generation_agent

        result = run_problem_generation_agent(
            user_profile,
            weakness,
            difficulty,
            generation_reason=generation_reason
        )

        return Response(result, status=status.HTTP_200_OK)
```

#### 4-2. Performance Tracker & Deep Dive & Motivation Agents

**간단한 버전으로 구현 (Phase 5에서 고도화)**

```python
# backend/core/agents/simple_agents.py

def get_performance_summary(user_profile) -> Dict:
    """성능 요약"""
    from core.models import LearningProgress

    all_progress = LearningProgress.objects.filter(user=user_profile)

    completed = all_progress.filter(status='COMPLETED').count()
    improving = all_progress.filter(status='IMPROVING').count()

    avg_improvement = all_progress.aggregate(
        avg=models.Avg(models.F('current_score') - models.F('initial_score'))
    )['avg'] or 0

    return {
        "overall_progress": int((completed / max(all_progress.count(), 1)) * 100),
        "weaknesses_solved": completed,
        "weaknesses_in_progress": improving,
        "average_improvement": avg_improvement,
        "trend": "UPWARD" if avg_improvement > 5 else "STABLE"
    }

def get_deep_dive_analysis(user_profile, weakness: str) -> Dict:
    """심화 분석"""
    # 같은 약점으로 반복 실패한 경우의 분석
    from core.models import VerificationResult

    failures = VerificationResult.objects.filter(
        user=user_profile,
        focus_weakness=weakness,
        improved=False
    ).order_by('-verified_at')[:3]

    if len(failures) >= 2:
        return {
            "pattern_detected": True,
            "message": f"{weakness}에서 반복 실패 감지됨",
            "suggestion": "기초 개념을 다시 학습해보세요",
            "root_cause": "설계 단계부터 약한 것 같습니다"
        }

    return {"pattern_detected": False}

def get_motivation_message(user_profile) -> str:
    """동기 유지 메시지"""
    from core.models import LearningProgress
    from django.utils import timezone
    from datetime import timedelta

    recent_progress = LearningProgress.objects.filter(
        user=user_profile,
        updated_at__gte=timezone.now() - timedelta(days=7)
    ).count()

    if recent_progress >= 3:
        return "이번주에 3개 약점을 작업했네요! 계속 화이팅! 🔥"
    elif recent_progress >= 1:
        return "꾸준히 노력 중이네요. 한 발 한 발이 모여 성장이 됩니다! 💪"
    else:
        return "새로운 주가 시작되었어요. 오늘부터 시작해봅시다! 🚀"
```

---

### Phase 5: 프론트엔드 통합 (2주)

#### 5-1. 분석 결과 UI 개선

**파일: `frontend/src/components/AgentAnalysisModal.vue` (수정)**

```vue
<template>
  <div class="agent-modal">
    <!-- 기존 코드 유지 -->

    <!-- 새로운 Tab: 검증 결과 -->
    <div v-if="activeTab === 'verification'" class="verification-section">
      <div class="improvement-card">
        <h3>✨ 약점 개선 현황</h3>

        <div v-if="verificationResult.improved" class="improved-badge">
          ✅ {{ verificationResult.improvement_level }} 개선됨!
        </div>
        <div v-else class="not-improved-badge">
          ⚠️ 아직 개선이 필요합니다
        </div>

        <div class="improvement-details">
          <div class="score-comparison">
            <span>이전: {{ initialScore }}</span>
            →
            <span class="current-score">현재: {{ currentScore }}</span>
          </div>

          <div class="evidence">
            <h4>개선 증거:</h4>
            <ul>
              <li v-for="(item, idx) in verificationResult.evidence" :key="idx">
                {{ item }}
              </li>
            </ul>
          </div>

          <div v-if="verificationResult.remaining_issues.length" class="remaining">
            <h4>아직 부족한 부분:</h4>
            <ul>
              <li v-for="(item, idx) in verificationResult.remaining_issues" :key="idx">
                {{ item }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 다음 스텝 -->
      <div class="next-step-card">
        <h3>🎯 다음 스텝</h3>
        <div v-if="nextRoadmap">
          <p>{{ nextRoadmap.message }}</p>

          <div v-if="nextRoadmap.roadmap_type === 'ADVANCE'" class="next-action">
            다음 약점: <strong>{{ nextRoadmap.next_weakness }}</strong>
          </div>

          <button @click="proceedNext" class="proceed-btn">
            다음으로 진행하기
          </button>
        </div>
      </div>
    </div>

    <!-- 새로운 Tab: 진행도 -->
    <div v-if="activeTab === 'progress'" class="progress-section">
      <div class="progress-chart">
        <h3>📊 학습 진행도</h3>

        <div class="overall">
          <div class="progress-bar">
            <div :style="{width: progressData.overall_progress + '%'}"></div>
          </div>
          <span>{{ progressData.overall_progress }}% 완료</span>
        </div>

        <div class="details">
          <div class="stat">
            <span>완료한 약점:</span>
            <strong>{{ progressData.weaknesses_solved }}/7</strong>
          </div>
          <div class="stat">
            <span>평균 개선도:</span>
            <strong>+{{ progressData.average_improvement.toFixed(1) }}점</strong>
          </div>
          <div class="stat">
            <span>추이:</span>
            <strong :class="progressData.trend.toLowerCase()">
              {{ progressData.trend }}
            </strong>
          </div>
        </div>
      </div>
    </div>

    <!-- 새로운 Tab: 맞춤형 문제 -->
    <div v-if="activeTab === 'generated'" class="generated-problem-section">
      <div class="generated-problem">
        <h3>🤖 맞춤형 문제</h3>

        <div v-if="generatedProblem" class="problem-card">
          <h4>{{ generatedProblem.problem_data.problem_title }}</h4>
          <p>{{ generatedProblem.problem_data.problem_description }}</p>

          <div class="problem-details">
            <div class="statement">
              {{ generatedProblem.problem_data.problem_statement }}
            </div>

            <div v-if="generatedProblem.problem_data.examples" class="examples">
              <h5>예제:</h5>
              <div v-for="(ex, idx) in generatedProblem.problem_data.examples" :key="idx">
                입력: {{ ex.input }} → 출력: {{ ex.output }}
              </div>
            </div>

            <div v-if="showHints" class="hints">
              <h5>힌트:</h5>
              <ul>
                <li v-for="(hint, idx) in generatedProblem.problem_data.hints" :key="idx">
                  {{ hint }}
                </li>
              </ul>
            </div>

            <button @click="showHints = !showHints" class="hint-toggle">
              {{ showHints ? '힌트 숨기기' : '힌트 보기' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AgentAnalysisService from '@/services/AgentAnalysisService'

const activeTab = ref('result')
const verificationResult = ref(null)
const nextRoadmap = ref(null)
const progressData = ref(null)
const generatedProblem = ref(null)
const showHints = ref(false)

const initialScore = ref(0)
const currentScore = ref(0)

onMounted(async () => {
  await loadVerificationData()
  await loadProgressData()
})

async function loadVerificationData() {
  try {
    const result = await AgentAnalysisService.getVerification({
      focus_weakness: 'edge_case',
      initial_score: 45
    })

    verificationResult.value = result
    currentScore.value = result.improvement_percentage || 0

    // 다음 로드맵 조회
    const roadmap = await AgentAnalysisService.getAdaptiveRoadmap(result)
    nextRoadmap.value = roadmap
  } catch (error) {
    console.error('검증 데이터 로드 실패:', error)
  }
}

async function loadProgressData() {
  try {
    const progress = await AgentAnalysisService.getPerformanceProgress()
    progressData.value = progress
  } catch (error) {
    console.error('진행도 로드 실패:', error)
  }
}

async function proceedNext() {
  if (nextRoadmap.value?.next_weakness) {
    // 맞춤형 문제 생성
    try {
      const problem = await AgentAnalysisService.generateProblem({
        weakness: nextRoadmap.value.next_weakness,
        difficulty: 'MEDIUM',
        generation_reason: 'ADVANCE'
      })

      generatedProblem.value = problem
      activeTab.value = 'generated'
    } catch (error) {
      console.error('문제 생성 실패:', error)
    }
  }
}
</script>

<style scoped>
.improvement-card {
  background: #f0f9ff;
  border: 2px solid #0ea5e9;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.improved-badge {
  background: #10b981;
  color: white;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 12px;
  font-weight: bold;
}

.not-improved-badge {
  background: #f97316;
  color: white;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 12px;
  font-weight: bold;
}

.next-step-card {
  background: #fef3c7;
  border: 2px solid #eab308;
  border-radius: 8px;
  padding: 16px;
}

.proceed-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 12px;
}

.proceed-btn:hover {
  background: #2563eb;
}

.progress-chart {
  background: #f0fdf4;
  border: 2px solid #16a34a;
  border-radius: 8px;
  padding: 16px;
}

.progress-bar {
  background: #e5e7eb;
  border-radius: 6px;
  height: 20px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-bar > div {
  background: linear-gradient(90deg, #10b981, #059669);
  height: 100%;
  transition: width 0.3s ease;
}

.problem-card {
  background: #faf5ff;
  border: 2px solid #a78bfa;
  border-radius: 8px;
  padding: 16px;
}

.hints {
  background: #fef3c7;
  padding: 12px;
  border-radius: 6px;
  margin-top: 12px;
}

.hint-toggle {
  background: #8b5cf6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 12px;
}
</style>
```

#### 5-2. 서비스 코드 업데이트

**파일: `frontend/src/services/AgentAnalysisService.js` (수정)**

```javascript
// 기존 코드에 추가

export default {
  // 기존 메서드들...

  // 검증
  async getVerification(payload) {
    const response = await fetch(`${API_BASE_URL}/agents/verify/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify(payload)
    })
    return response.json()
  },

  // 적응형 로드맵
  async getAdaptiveRoadmap(verificationResult) {
    const response = await fetch(`${API_BASE_URL}/agents/adaptive-roadmap/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify(verificationResult)
    })
    return response.json()
  },

  // 문제 생성
  async generateProblem(payload) {
    const response = await fetch(`${API_BASE_URL}/agents/generate-problem/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify(payload)
    })
    return response.json()
  },

  // 진행도 조회
  async getPerformanceProgress() {
    const response = await fetch(`${API_BASE_URL}/agents/progress/`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    })
    return response.json()
  }
}
```

#### 5-3. 체크리스트

```
□ AgentAnalysisModal 컴포넌트 수정
□ 탭 UI 추가 (검증, 진행도, 맞춤형 문제)
□ 서비스 메서드 추가
□ 로컬 테스트
□ 반응형 디자인 검증
```

---

### Phase 6: 통합 테스트 및 최적화 (1주)

#### 6-1. 엔드-투-엔드 테스트

```python
# backend/tests/test_learning_agent_flow.py

from django.test import TestCase
from core.models import UserProfile, UserSolvedProblem

class LearningAgentFlowTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(email="test@example.com")

    def test_complete_flow(self):
        """전체 학습 사이클 테스트"""

        # 1. 초기 분석
        from core.agents.agent_runner import run_data_analyzer_agent
        analysis = run_data_analyzer_agent(self.user)
        self.assertIsNotNone(analysis)

        # 2. 검증
        from core.agents.verification_agent import run_verification_agent
        verification = run_verification_agent(
            self.user,
            "edge_case",
            45,
            analysis
        )
        self.assertIsNotNone(verification)

        # 3. 로드맵
        from core.agents.adaptive_roadmap_agent import run_adaptive_roadmap_agent
        roadmap = run_adaptive_roadmap_agent(
            verification,
            "edge_case",
            ["root_cause", "security"]
        )
        self.assertIsNotNone(roadmap)

        # 4. 문제 생성
        from core.agents.problem_generation_agent import run_problem_generation_agent
        problem = run_problem_generation_agent(
            self.user,
            "null 처리 부족",
            "MEDIUM"
        )
        self.assertIsNotNone(problem)
```

#### 6-2. 성능 모니터링

```python
# backend/core/management/commands/monitor_agents.py

from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        from core.models import VerificationResult, GeneratedProblem
        from django.utils import timezone
        from datetime import timedelta

        # 지난 24시간 통계
        today = timezone.now() - timedelta(days=1)

        verifications = VerificationResult.objects.filter(verified_at__gte=today)
        problems = GeneratedProblem.objects.filter(generated_at__gte=today)

        logger.info(f"검증 실행: {verifications.count()}")
        logger.info(f"문제 생성: {problems.count()}")
        logger.info(f"평균 개선도: {verifications.aggregate(Avg('improvement_percentage'))}")
```

#### 6-3. 체크리스트

```
□ 엔드-투-엔드 테스트 작성 및 실행
□ API 응답 시간 측정
□ 에러 핸들링 검증
□ 로그 모니터링 설정
□ 성능 최적화
□ 보안 검토
```

---

### Phase 7: 배포 및 모니터링 (1주)

#### 7-1. 배포 체크리스트

```
□ DB 마이그레이션 검증
□ 환경 변수 설정 확인
□ API 키 (OpenAI) 확인
□ 캐시 초기화
□ 로그 설정 확인
□ 백업 계획 수립
```

#### 7-2. 배포 후 모니터링

```bash
# 배포 후 첫 주
- API 에러율 모니터링 (목표: < 1%)
- 응답 시간 모니터링 (목표: < 5초)
- 사용자 피드백 수집
- 버그 리포트 대응
```

#### 7-3. 체크리스트

```
□ 스테이징 환경 배포
□ 프로덕션 배포
□ 모니터링 대시보드 설정
□ 알림 규칙 설정
□ 사용자 피드백 채널 설정
```

---

## 📊 전체 일정

| Phase | 내용 | 기간 | 인원 |
|-------|------|------|------|
| **1** | DB 모델 & 마이그레이션 | 1주 | 1명 |
| **2** | Verification Agent | 2주 | 2명 |
| **3** | Adaptive + Generation Agents | 2주 | 2명 |
| **4** | 문제 생성 통합 | 1주 | 1명 |
| **5** | 프론트엔드 통합 | 2주 | 2명 |
| **6** | 통합 테스트 | 1주 | 2명 |
| **7** | 배포 & 모니터링 | 1주 | 1명 |
| **합계** | | **10주** | **~2-3명** |

---

## 💾 커밋 전략

### Phase별 PR/커밋 구조

```
feat/learning-agent-foundation
├─ DB 모델 추가
├─ 마이그레이션 파일

feat/learning-agent-verification
├─ Verification Agent
├─ API 엔드포인트
├─ 테스트

feat/learning-agent-roadmap-and-generation
├─ Adaptive Roadmap Agent
├─ Problem Generation Agent
├─ API 엔드포인트들

feat/learning-agent-frontend
├─ AgentAnalysisModal 수정
├─ 새 탭 UI
├─ 서비스 메서드

feat/learning-agent-testing-deployment
├─ 통합 테스트
├─ 성능 최적화
├─ 배포 준비
```

---

## 📈 성공 지표

### 정량적 KPI

```
구현 전:
- 약점 극복률: 40%
- 평균 사용 기간: 3주
- 반복 학습율: 30%
- 사용자 만족도: 60%

구현 후 (목표 3개월):
- 약점 극복률: 75% (+35%)
- 평균 사용 기간: 8주 (+5주)
- 반복 학습율: 70% (+40%)
- 사용자 만족도: 85% (+25%)
```

### 정성적 피드백

```
구현 전:
"분석은 좋은데... 그 이후는?"
"같은 문제만 나오네"
"정말 도움 되는지 모르겠어"

구현 후:
"내 성장이 눈에 띄네!"
"매번 다른 문제가 나와서 좋아"
"이 시스템이 내를 이해하는 것 같아"
```

---

## 🚨 위험 요소 및 대응

| 위험 | 영향도 | 대응 |
|------|--------|------|
| OpenAI API 비용 증가 | 중간 | 캐싱/배치 처리 |
| LLM 응답 시간 증가 | 높음 | 비동기 처리 + 큐 시스템 |
| DB 성능 저하 | 중간 | 인덱싱 + 쿼리 최적화 |
| 사용자 데이터 프라이버시 | 높음 | 데이터 암호화 + GDPR 준수 |
| 새 기능 버그 | 중간 | 철저한 테스트 + 베타 테스트 |

---

## ✅ 최종 체크리스트

```
□ 모든 Phase 일정 확인
□ 인력 배치 계획 수립
□ 예산 검토 (OpenAI API 비용 등)
□ 위험 요소 모니터링 계획
□ 사용자 피드백 채널 준비
□ 모니터링 대시보드 설계
□ 롤백 계획 수립
□ 문서화 계획
```

---

## 🎯 구현 시작

### 즉시 시작 가능한 작업

```
1. DB 모델 작성 (지금 바로)
2. 마이그레이션 생성
3. Verification Agent 기본 구현
4. API 테스트

→ 1주 후: 첫 번째 검증 기능 출시 가능
```

### 필요한 준비사항

```
□ Git 브랜치 전략 확인 (feature branches)
□ 팀 커뮤니케이션 채널 (Slack/Discord)
□ 버전 관리 계획
□ 테스트 서버 준비
□ 스테이징 환경 구성
```

---

## 📝 다음 스텝

**지금 바로 할 수 있는 것:**

```
1. Phase 1 DB 모델 코드 작성
2. 마이그레이션 테스트
3. Verification Agent 프롬프트 최적화
4. 팀 워크숍 (아키텍처 리뷰)
```

**권장 순서:**

```
Phase 1 → Phase 2 → Phase 3 → 4 → 5 → 6 → 7
완료 후 다음 phase로 진행
(병렬 처리 가능한 부분은 병렬화)
```

이 로드맵을 따르면 **3개월 후 완전한 학습 성장 플랫폼**을 완성할 수 있습니다! 🚀
