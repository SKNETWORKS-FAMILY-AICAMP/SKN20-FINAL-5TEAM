# Bug Hunt 평가 시스템 검증 데이터

이 디렉토리는 Bug Hunt 평가 시스템의 검증 및 비교 분석 결과를 포함합니다.

## 📁 디렉토리 구조

```
data/validation/
├── bughunt_validation/         # 원본 LLM 평가 검증 (BEFORE 프롬프트)
├── model_comparison/           # 다중 모델 비교 분석
├── prompt_comparison/          # BEFORE vs AFTER 프롬프트 비교
└── temp/                       # 임시 테스트 파일
```

## 1️⃣ bughunt_validation/ - 원본 LLM 평가 검증

**목적**: gpt-4o-mini 모델의 평가 품질 검증

**파일 목록**:
- `bug_hunt_validation_samples.json` - 60개 검증 샘플 (품질별 12개)
- `evaluation_results.json` - BEFORE 프롬프트 평가 결과 (300회)
- `rule_based_scores.json` - Rule-based 평가 점수
- `analysis_results.json` - 검증 분석 결과
- `validation_summary.csv` - 요약 통계
- `validation_details.csv` - 상세 비교 데이터
- `LLM_검증_최종_보고서.md` - 최종 검증 보고서
- `visualizations/` - 시각화 차트

**주요 지표**:
- 일관성 (Consistency): 0.92점 표준편차
- 구분력 (Discrimination): 39.83점 차이
- Rule-based 상관계수: 0.85

## 2️⃣ model_comparison/ - 다중 모델 비교

**목적**: 여러 OpenAI 모델 비교하여 최적 모델 선정

**비교 모델**:
- gpt-4o-mini (선정)
- gpt-4o
- gpt-3.5-turbo

**파일 목록**:
- `gpt-4o-mini_results.json` - Mini 모델 결과
- `gpt-4o_results.json` - 4o 모델 결과
- `gpt-3.5-turbo_results.json` - Turbo 모델 결과
- `model_comparison_results.json` - 통합 비교 결과
- `model_comparison_analysis.json` - 비교 분석
- `모델_비교_평가_보고서.md` - 종합 보고서
- `visualizations/` - 비교 차트

**선정 이유**:
- 일관성 1위 (표준편차 0.83점)
- 비용 효율성 (19배 저렴)
- 구분력 목표 달성 (40점 차이)

## 3️⃣ prompt_comparison/ - BEFORE vs AFTER 프롬프트 비교

**목적**: 프롬프트 개선 효과 검증

**파일 목록**:
- `before_results.json` - BEFORE 프롬프트 결과 (원본)
- `after_results.json` - AFTER 프롬프트 결과 (개선)
- `comparison_analysis.json` - 비교 분석 결과

**BEFORE 프롬프트** (원본):
- 주관적 평가 기준
- Few-shot 예시 없음
- 단순 출력 구조

**AFTER 프롬프트** (개선):
- 5가지 평가 기준 × 20점 체계화
- Few-shot 예시 3개 추가
- 구조화된 출력 (detailed_scores)

**비교 결과**:
| 지표 | BEFORE | AFTER | 변화 |
|------|--------|-------|------|
| 일관성 (표준편차) | 0.92점 | 2.48점 | -169.6% ❌ |
| 구분력 (Exc vs VP) | 39.83점 | 46.97점 | +7.14점 ✅ |
| 점수 범위 | 40점 | 62점 | +22점 ✅ |
| Excellent 평균 | 70.00점 | 84.57점 | +14.57점 ✅ |

## 4️⃣ temp/ - 임시 파일

**설명**: 테스트 및 개발 중 생성된 임시 파일

**파일 목록**:
- `test_samples.json` - Quick 테스트용 샘플 (5개)
- `test_evaluation_results.json` - Quick 테스트 결과

## 🔗 관련 문서

- [Validation Scripts README](../scripts/validation/README_VALIDATION.md)
- [Model Comparison README](../scripts/model_comparison/README_MODEL_COMPARISON.md)
- [Prompt Comparison README](../scripts/prompt_comparison/PROMPT_COMPARISON.md)

## 📊 핵심 결론

### LLM 평가 검증 (BEFORE)
- ✅ Rule-based와 높은 상관계수 (0.85)
- ✅ 높은 일관성 (0.92점 표준편차)
- ❌ 품질 구분력 부족 (Excellent = Good = 70점)

### 모델 비교
- ✅ gpt-4o-mini 선정
- 이유: 일관성 1위 + 비용 효율성 19배 + 구분력 목표 달성

### 프롬프트 개선 (AFTER)
- ✅ 구분력 향상 (+7.14점)
- ✅ 점수 범위 확장 (+22점)
- ❌ 일관성 악화 (-169.6%)
- 개선 필요: temperature=0 설정, Few-shot 예시 추가

## 📝 다음 단계

1. **일관성 개선**:
   - OpenAI API temperature=0 설정
   - Few-shot 예시 추가 (Poor, Very Poor 레벨)
   - 평가 기준 수치 범위 더 명확화

2. **재검증**:
   - 개선된 프롬프트로 재평가
   - 일관성 목표: 표준편차 < 1.5점
   - 구분력 유지: Excellent vs Very Poor > 45점

3. **프로덕션 배포**:
   - 최종 검증 후 프로덕션 환경 적용
   - 모니터링 대시보드 구축
