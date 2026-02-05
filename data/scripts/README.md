# Bug Hunt 평가 시스템 스크립트

Bug Hunt 평가 시스템의 검증, 비교, 분석을 위한 스크립트 모음입니다.

## 📁 디렉토리 구조

```
data/scripts/
├── validation/           # LLM 평가 검증 스크립트
├── model_comparison/     # 모델 비교 스크립트
├── prompt_comparison/    # 프롬프트 비교 스크립트
└── utils/               # 공통 유틸리티
```

## 1️⃣ validation/ - LLM 평가 검증

**목적**: gpt-4o-mini 평가의 신뢰성 검증

### 스크립트 목록

#### `generate_validation_samples.py`
60개 검증 샘플 생성 (품질별 12개)

```bash
python data/scripts/validation/generate_validation_samples.py
```

**출력**: `data/validation/bughunt_validation/bug_hunt_validation_samples.json`

#### `run_evaluation.py`
LLM 평가 실행 (60샘플 × 5회 = 300회)

```bash
# Full 모드 (60개 샘플)
python data/scripts/validation/run_evaluation.py --trials 5

# Quick 모드 (5개 샘플, 테스트용)
python data/scripts/validation/run_evaluation.py --trials 5 --quick
```

**출력**: `data/validation/evaluation_results.json`

#### `run_full_validation.py`
전체 검증 파이프라인 실행

```bash
python data/scripts/validation/run_full_validation.py
```

**작업 순서**:
1. 검증 샘플 생성
2. LLM 평가 실행
3. Rule-based 평가 실행
4. 결과 분석
5. 시각화 생성

#### `analyze_results.py`
평가 결과 분석 (일관성, 구분력, 상관계수)

```bash
python data/scripts/validation/analyze_results.py
```

**출력**:
- `data/validation/bughunt_validation/analysis_results.json`
- `data/validation/bughunt_validation/validation_summary.csv`

#### `visualize_results.py`
분석 결과 시각화

```bash
python data/scripts/validation/visualize_results.py
```

**출력**: `data/validation/bughunt_validation/visualizations/`
- `consistency_boxplot.png` - 일관성 박스플롯
- `discrimination_barchart.png` - 품질별 평균 점수
- `correlation_scatter.png` - Rule-based 상관관계
- `summary_chart.png` - 종합 요약

## 2️⃣ model_comparison/ - 모델 비교

**목적**: 최적 OpenAI 모델 선정

### 스크립트 목록

#### `run_model_comparison.py`
여러 모델로 동일 샘플 평가

```bash
# 모든 모델 비교
python data/scripts/model_comparison/run_model_comparison.py

# 특정 모델만 실행
python data/scripts/model_comparison/run_model_comparison.py --models gpt-4o-mini gpt-4o
```

**비교 모델**:
- gpt-4o-mini
- gpt-4o
- gpt-3.5-turbo

**출력**: `data/validation/model_comparison/{model}_results.json`

#### `analyze_model_comparison.py`
모델 비교 분석 및 종합 점수 계산

```bash
python data/scripts/model_comparison/analyze_model_comparison.py
```

**분석 지표**:
- 일관성 (Consistency)
- 구분력 (Discrimination)
- 순위 정확도 (Kendall's Tau)
- 성능 (속도, 비용)
- 오류율

**출력**: `data/validation/model_comparison/model_comparison_analysis.json`

#### `visualize_model_comparison.py`
모델 비교 시각화

```bash
python data/scripts/model_comparison/visualize_model_comparison.py
```

**출력**: `data/validation/model_comparison/visualizations/`
- `consistency_comparison.png` - 일관성 비교
- `discrimination_comparison.png` - 구분력 비교
- `performance_comparison.png` - 성능 비교
- `radar_chart.png` - 레이더 차트
- `overall_ranking.png` - 종합 순위

#### `model_evaluator.py`
모델 평가 유틸리티 클래스

**용도**: 다른 스크립트에서 import하여 사용

## 3️⃣ prompt_comparison/ - 프롬프트 비교

**목적**: BEFORE vs AFTER 프롬프트 개선 효과 검증

### 스크립트 목록

#### `compare_before_after.py`
BEFORE vs AFTER 프롬프트 비교 분석

```bash
python data/scripts/prompt_comparison/compare_before_after.py
```

**입력**:
- BEFORE: `data/validation/bughunt_validation/evaluation_results.json`
- AFTER: `data/validation/prompt_comparison/after_results.json`

**출력**: `data/validation/prompt_comparison/comparison_analysis.json`

**비교 지표**:
- 일관성 변화율
- 구분력 향상
- 점수 분포 변화
- 품질별 평균 점수 변화

## 4️⃣ utils/ - 공통 유틸리티

### 스크립트 목록

#### `rule_based_scorer.py`
Rule-based 평가 시스템

**평가 기준**:
1. 원인 분석 정확도 (30점)
2. 코드 수정 적절성 (25점)
3. 설명 완성도 (20점)
4. 논리적 일관성 (15점)
5. 전문 용어 사용 (10점)

```bash
python data/scripts/utils/rule_based_scorer.py
```

#### `generate_pseudocode.py`
검증 샘플용 의사코드 생성

```bash
python data/scripts/utils/generate_pseudocode.py
```

#### `collect_data.py`
데이터 수집 유틸리티

```bash
python data/scripts/utils/collect_data.py
```

## 🚀 빠른 시작

### 1. LLM 평가 검증

```bash
# 전체 검증 파이프라인 실행 (1시간 소요)
python data/scripts/validation/run_full_validation.py

# 또는 단계별 실행
python data/scripts/validation/generate_validation_samples.py
python data/scripts/validation/run_evaluation.py --trials 5
python data/scripts/validation/analyze_results.py
python data/scripts/validation/visualize_results.py
```

### 2. 모델 비교

```bash
# 모델 비교 실행 (3-4시간 소요)
python data/scripts/model_comparison/run_model_comparison.py

# 분석 및 시각화
python data/scripts/model_comparison/analyze_model_comparison.py
python data/scripts/model_comparison/visualize_model_comparison.py
```

### 3. 프롬프트 비교

```bash
# BEFORE vs AFTER 비교
python data/scripts/prompt_comparison/compare_before_after.py
```

## 📊 주요 결과 요약

### LLM 평가 검증 (gpt-4o-mini)
- ✅ 일관성: 0.92점 표준편차
- ✅ Rule-based 상관계수: 0.85
- ❌ 구분력: Excellent = Good = 70점

### 모델 비교
- 🏆 **최종 선정: gpt-4o-mini**
- 이유: 일관성 1위 (0.83점) + 비용 효율성 19배

### 프롬프트 개선 (AFTER)
- ✅ 구분력: +7.14점
- ✅ 점수 범위: +22점
- ❌ 일관성: -169.6% (개선 필요)

## 🔧 개발 가이드

### 새 스크립트 추가 시

1. 적절한 디렉토리에 배치
2. Docstring으로 목적과 사용법 명시
3. argparse로 CLI 인터페이스 제공
4. 결과를 JSON으로 저장
5. README 업데이트

### 코딩 컨벤션

```python
"""
스크립트 설명

주요 기능과 사용 방법 설명
"""
import json
from pathlib import Path

class AnalyzerName:
    """분석기 클래스 설명"""

    def __init__(self, input_file):
        """초기화"""
        pass

    def analyze(self):
        """분석 실행"""
        pass

if __name__ == "__main__":
    # CLI 실행 코드
    pass
```

## 📚 관련 문서

- [Validation README](validation/README_VALIDATION.md)
- [Model Comparison README](model_comparison/README_MODEL_COMPARISON.md)
- [Prompt Comparison Guide](prompt_comparison/PROMPT_COMPARISON.md)
- [Main Validation Data](../../data/validation/README.md)

## 🐛 문제 해결

### 오류: "Module not found"
```bash
# Django 환경에서 실행 필요
cd data
python scripts/validation/run_evaluation.py
```

### 오류: "File not found"
```bash
# 프로젝트 루트에서 실행
cd c:/SKN20-FINAL-5TEAM
python data/scripts/validation/run_evaluation.py
```

### Docker에서 실행
```bash
docker exec skn20-final-5team-backend-1 python scripts/validation/run_evaluation.py
```
