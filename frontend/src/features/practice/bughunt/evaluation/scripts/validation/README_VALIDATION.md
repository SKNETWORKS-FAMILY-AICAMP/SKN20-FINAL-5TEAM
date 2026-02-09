# Bug Hunt 평가 시스템 검증 가이드

## 📋 개요

Bug Hunt 평가 시스템의 정확성과 신뢰성을 검증하기 위한 자동화된 테스트 파이프라인입니다.

**4가지 검증 방법:**
1. **평가 일관성 (Consistency)**: 동일 입력에 대한 반복 평가의 표준편차
2. **극단 케이스 구분력 (Discrimination)**: 우수 vs 매우 미흡 답변의 점수 차이
3. **상대 평가 정확도 (Ranking)**: 품질 순위의 정확도 (Kendall's Tau)
4. **규칙 기반 교차 검증 (Convergent Validity)**: 규칙 점수와 LLM 점수의 상관계수

---

## 🚀 빠른 시작

### 방법 A: Docker 환경 (권장)

Docker Compose를 사용하는 경우 가장 간단합니다.

#### 1. Docker 컨테이너 실행 확인

```bash
# Docker Compose 실행
docker-compose up -d

# backend 컨테이너가 실행 중인지 확인
docker-compose ps
```

#### 2. OpenAI API 키 설정

프로젝트 루트의 `.env` 파일에 API 키가 설정되어 있어야 합니다.

```bash
# .env 파일 확인
OPENAI_API_KEY=sk-...
```

#### 3. Quick 테스트 (추천: 처음 실행 시)

```bash
# backend 컨테이너에 접속하여 실행
docker-compose exec backend bash -c "cd /app/scripts && python -X utf8 run_full_validation.py --quick"
```

#### 4. 전체 검증 (최종 결과용)

```bash
# backend 컨테이너에서 전체 검증 실행
docker-compose exec backend bash -c "cd /app/scripts && python -X utf8 run_full_validation.py"
```

#### 5. 결과 확인

```bash
# 컨테이너 내부에서 결과 파일 확인
docker-compose exec backend ls -la /app/../data/validation/

# 또는 호스트에서 직접 확인 (볼륨 마운트되어 있음)
ls -la data/validation/
```

---

### 방법 B: 로컬 환경 (가상환경)

Docker를 사용하지 않는 경우

#### 1. 환경 설정

```bash
# 가상환경 활성화
cd backend
source ../.venv/bin/activate  # Windows: ..\.venv\Scripts\activate

# 의존성 확인
pip install -r ../requirements.txt
```

#### 2. OpenAI API 키 설정

```bash
# .env 파일 확인
OPENAI_API_KEY=sk-...
```

#### 3. Quick 테스트

```bash
cd backend/scripts

# Quick 모드
python -X utf8 run_full_validation.py --quick
```

#### 4. 전체 검증

```bash
cd backend/scripts

# 전체 모드
python -X utf8 run_full_validation.py
```

---

## 📂 생성되는 파일

검증 완료 후 `data/validation/` 폴더에 다음 파일들이 생성됩니다:

```
data/validation/
├── bug_hunt_validation_samples.json  # 60개 샘플 데이터
├── rule_based_scores.json            # 규칙 기반 점수
├── evaluation_results.json           # LLM 평가 결과 (300회)
├── analysis_results.json             # 4가지 검증 통계 분석
└── visualizations/                   # 시각화 그래프
    ├── consistency_boxplot.png       # 일관성 박스플롯
    ├── discrimination_barchart.png   # 극단 구분 바 차트
    ├── correlation_scatter.png       # 상관관계 산점도
    └── summary_chart.png             # 종합 요약 차트
```

---

## 📊 개별 스크립트 실행

필요에 따라 각 단계를 개별적으로 실행할 수 있습니다.

### Step 1: 샘플 데이터 생성

```bash
python -X utf8 generate_validation_samples.py
```

12개 버그 케이스 × 5개 품질 레벨 = 60개 샘플 생성

### Step 2: 규칙 기반 점수 계산

```bash
python -X utf8 rule_based_scorer.py
```

객관적 지표 기반 점수 계산 (키워드, 코드 품질, 설명 충실도)

### Step 3: LLM 평가 실행

```bash
# Quick 모드 (5개 샘플)
python -X utf8 run_evaluation.py --quick

# 전체 모드 (60개 샘플)
python -X utf8 run_evaluation.py --trials 5
```

Django 서버를 통해 Bug Hunt 평가 API 호출

### Step 4: 통계 분석

```bash
python -X utf8 analyze_results.py
```

4가지 검증 메트릭 계산

### Step 5: 시각화

```bash
python -X utf8 visualize_results.py
```

결과를 그래프로 시각화

---

## 🎯 검증 기준 및 목표

| 검증 항목 | 메트릭 | 목표 | 의미 |
|----------|--------|------|------|
| **일관성** | 평균 표준편차 | ≤ 5점 | 동일 입력에 대해 안정적인 평가 |
| **극단 구분** | 점수 차이 | ≥ 30점 | 우수와 미흡을 명확히 구분 |
| **순위 정확도** | Kendall's Tau | ≥ 0.75 | 품질 순위를 정확히 매김 |
| **규칙 상관** | Pearson r | ≥ 0.65 | 객관적 지표와 일치 |

---

## 📈 결과 해석

### 통과 조건

4가지 검증이 **모두 목표 이상**이면 평가 시스템이 실무 적용 가능한 수준으로 판정됩니다.

### 실패 시 조치

1. **일관성 미달**: Temperature 값 낮추기 (0.3 → 0.1)
2. **극단 구분 미달**: 프롬프트 강화, 평가 루브릭 명확화
3. **순위 정확도 미달**: 평가 기준 세분화
4. **규칙 상관 미달**: 규칙 기반 점수 재조정 또는 LLM 프롬프트 조정

---

## 🔧 문제 해결

### UnicodeEncodeError 발생 시

```bash
# Python을 UTF-8 모드로 실행
python -X utf8 <script_name>.py

# 또는 환경 변수 설정
set PYTHONIOENCODING=utf-8
```

### Django 모듈 없음 오류

```bash
# 가상환경 활성화 확인
source ../.venv/bin/activate  # Linux/Mac
..\.venv\Scripts\activate     # Windows

# Django 설치
pip install django djangorestframework
```

### OpenAI API 오류

- API 키가 올바른지 확인
- API 사용 한도 확인
- 네트워크 연결 확인

---

## 💰 비용 예상

### Quick 모드 (테스트용)
- 평가 횟수: 5개 × 5회 = 25회
- 모델: GPT-4o-mini
- 예상 비용: **약 $0.25**
- 소요 시간: **약 2-3분**

### 전체 모드 (최종 결과용)
- 평가 횟수: 60개 × 5회 = 300회
- 모델: GPT-4o-mini
- 예상 비용: **약 $3.00**
- 소요 시간: **약 15-20분**

---

## 📝 결과 예시

```
📊 검증 1: 평가 일관성 (Consistency)
결과:
  평균 표준편차: 3.82점 (목표 ≤5점)
  최대 표준편차: 7.15점 (목표 ≤10점)
  판정: ✅ 통과

📊 검증 2: 극단 케이스 구분력 (Discrimination)
결과:
  우수 그룹 평균: 87.2점 (n=12)
  매우 미흡 그룹 평균: 31.5점 (n=12)
  점수 차이: 55.7점 (목표 ≥30점)
  판정: ✅ 통과

📊 검증 3: 상대 평가 정확도 (Ranking Validation)
결과:
  평균 Kendall's Tau: 0.82 (목표 ≥0.75)
  완벽한 순위: 11/12 (91.7%)
  판정: ✅ 통과

📊 검증 4: 규칙 기반 교차 검증 (Convergent Validity)
결과:
  Pearson 상관계수: r = 0.73 (목표 ≥0.65)
  p-value: 0.0001
  판정: ✅ 통과

📋 종합 검증 보고서
최종 판정: ✅ 전체 통과
```

---

## 📚 참고 자료

- **통계 분석**: SciPy를 사용한 Kendall's Tau, Pearson 상관계수
- **시각화**: Matplotlib를 사용한 박스플롯, 바 차트, 산점도
- **평가 API**: `core.views.ai_view.BugHuntEvaluationView`
