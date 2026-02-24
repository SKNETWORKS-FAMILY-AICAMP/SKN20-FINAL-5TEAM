# Bug Hunt 평가 시스템 - 검증 및 분석

Bug Hunt 평가 시스템의 모든 검증, 분석, 스크립트를 포함하는 통합 디렉토리입니다.

## 📁 전체 구조

```
data/
├── scripts/              # 🔧 모든 분석 및 검증 스크립트
│   ├── validation/       # LLM 평가 검증
│   ├── model_comparison/ # 모델 비교 분석
│   ├── prompt_comparison/# 프롬프트 비교
│   ├── utils/           # 공통 유틸리티
│   └── README.md
│
└── validation/          # 📊 모든 검증 및 분석 결과
    ├── bughunt_validation/   # BEFORE 프롬프트 검증
    ├── model_comparison/     # 모델 비교 결과
    ├── prompt_comparison/    # BEFORE vs AFTER 비교
    ├── temp/                 # 임시 파일
    └── README.md
```

## 🚀 빠른 시작

### 1. LLM 평가 검증 실행

```bash
# 전체 검증 파이프라인
python data/scripts/validation/run_full_validation.py

# 단계별 실행
python data/scripts/validation/generate_validation_samples.py
python data/scripts/validation/run_evaluation.py --trials 5
python data/scripts/validation/analyze_results.py
python data/scripts/validation/visualize_results.py
```

**결과 위치**: `data/validation/bughunt_validation/`

### 2. 모델 비교 실행

```bash
# 여러 모델 비교
python data/scripts/model_comparison/run_model_comparison.py

# 분석 및 시각화
python data/scripts/model_comparison/analyze_model_comparison.py
python data/scripts/model_comparison/visualize_model_comparison.py
```

**결과 위치**: `data/validation/model_comparison/`

### 3. 프롬프트 비교 분석

```bash
# BEFORE vs AFTER 비교
python data/scripts/prompt_comparison/compare_before_after.py
```

**결과 위치**: `data/validation/prompt_comparison/`

## 📊 주요 분석 결과

### ✅ LLM 평가 검증 (BEFORE 프롬프트)
- **일관성**: 0.92점 표준편차 (목표 < 1.5 달성)
- **상관계수**: 0.85 (Rule-based와 높은 일치도)
- **한계**: Excellent = Good = 70점 (구분력 부족)

### ✅ 모델 비교
- **최종 선정**: gpt-4o-mini
- **선정 이유**:
  - 일관성 1위 (0.83점)
  - 비용 효율성 19배 (gpt-4o 대비)
  - 구분력 목표 달성 (40점 차이)

### 📈 프롬프트 개선 (AFTER)
- ✅ **구분력 향상**: +7.14점 (39.83 → 46.97)
- ✅ **점수 범위 확장**: +22점 (40 → 62)
- ✅ **품질별 점수 상승**: Excellent 70 → 84.57
- ❌ **일관성 악화**: 0.92 → 2.48 (-169.6%)

**개선 필요**: Temperature=0 설정, Few-shot 예시 추가

## 📚 상세 문서

### Scripts (스크립트)
- [전체 스크립트 가이드](scripts/README.md)
- [Validation 스크립트](scripts/validation/README_VALIDATION.md)
- [Model Comparison 스크립트](scripts/model_comparison/README_MODEL_COMPARISON.md)
- [Prompt Comparison 스크립트](scripts/prompt_comparison/PROMPT_COMPARISON.md)

### Validation (검증 결과)
- [전체 검증 결과 요약](validation/README.md)
- [LLM 검증 최종 보고서](validation/bughunt_validation/LLM_검증_최종_보고서.md)
- [모델 비교 평가 보고서](validation/model_comparison/모델_비교_평가_보고서.md)

## 🔄 작업 흐름

```
1. 샘플 생성
   ↓
2. LLM 평가 실행 (BEFORE)
   ↓
3. Rule-based 평가
   ↓
4. 검증 분석 (일관성, 구분력)
   ↓
5. 모델 비교 (gpt-4o-mini, gpt-4o, turbo)
   ↓
6. 최적 모델 선정 (gpt-4o-mini)
   ↓
7. 프롬프트 개선 (AFTER)
   ↓
8. BEFORE vs AFTER 비교
   ↓
9. 추가 개선 및 재검증
```

## 🎯 검증 목표 및 달성도

| 목표 | 기준 | BEFORE | AFTER | 달성 |
|------|------|--------|-------|------|
| 일관성 | < 1.5점 | 0.92점 | 2.48점 | ✅ → ❌ |
| 구분력 | > 30점 | 39.83점 | 46.97점 | ✅ → ✅ |
| 상관계수 | > 0.7 | 0.85 | - | ✅ |
| 점수 범위 | > 50점 | 40점 | 62점 | ❌ → ✅ |

## 📝 다음 단계

1. **일관성 개선**
   - [ ] OpenAI API temperature=0 설정
   - [ ] Few-shot 예시 추가 (Poor, Very Poor)
   - [ ] 평가 기준 수치 범위 명확화

2. **재검증**
   - [ ] 개선된 프롬프트로 재평가
   - [ ] 목표: 일관성 < 1.5, 구분력 > 45 유지

3. **프로덕션 배포**
   - [ ] 최종 검증 완료 후 배포
   - [ ] 모니터링 시스템 구축

## 🐛 트러블슈팅

### Scripts 실행 오류

**문제**: Module not found
```bash
# 해결: Django 환경 설정
cd c:/SKN20-FINAL-5TEAM
export DJANGO_SETTINGS_MODULE=backend.config.settings
python data/scripts/validation/run_evaluation.py
```

**문제**: File not found
```bash
# 해결: 프로젝트 루트에서 실행
cd c:/SKN20-FINAL-5TEAM
python data/scripts/validation/run_evaluation.py
```

### Docker에서 실행

```bash
# Scripts를 Docker로 복사
docker cp data/scripts/validation/run_evaluation.py skn20-final-5team-backend-1:/app/scripts/

# Docker 내에서 실행
docker exec skn20-final-5team-backend-1 python /app/scripts/run_evaluation.py
```

## 📞 연락처 및 지원

- 이슈 등록: GitHub Issues
- 문서 업데이트: Pull Request 환영

---

**마지막 업데이트**: 2026-02-05
**작성자**: SKN20-FINAL-5TEAM
