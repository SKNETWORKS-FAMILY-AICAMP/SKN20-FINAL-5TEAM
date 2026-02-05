# 모델 비교 평가 시스템

여러 LLM 모델을 동일한 샘플로 평가하고 비교하는 시스템입니다.

## 개요

이 시스템은 Bug Hunt 평가를 여러 모델(OpenAI, Hugging Face)로 실행하고, 다음 지표를 비교합니다:

1. **일관성**: 동일 샘플 반복 평가의 표준편차 (낮을수록 좋음)
2. **구분력**: 우수 vs 매우 미흡 케이스 점수 차이 (높을수록 좋음)
3. **순위 정확도**: Kendall's Tau (높을수록 좋음)
4. **속도**: 평균 응답 시간 (낮을수록 좋음)
5. **비용**: 총 API 비용 (낮을수록 좋음)
6. **신뢰성**: 오류율 (낮을수록 좋음)

## 파일 구조

```
backend/scripts/
├── model_evaluator.py              # 모델별 평가 실행 모듈
├── run_model_comparison.py         # 모델 비교 평가 실행 스크립트
├── analyze_model_comparison.py     # 결과 분석 스크립트
├── visualize_model_comparison.py   # 시각화 생성 스크립트
└── run_full_model_comparison.sh    # 전체 프로세스 자동 실행 스크립트
```

## 지원 모델

### OpenAI 모델
- `gpt-4o`: 최신 GPT-4 Optimized 모델
- `gpt-4o-mini`: 경량화된 GPT-4 Optimized 모델 (현재 사용 중)
- `gpt-3.5-turbo`: GPT-3.5 Turbo 모델
- `gpt-4-turbo`: GPT-4 Turbo 모델

### Hugging Face 모델 (무료)
- `Llama-3.1-70B`: Meta의 Llama 3.1 70B Instruct 모델
- `Mixtral-8x7B`: Mistral AI의 Mixtral 8x7B Instruct 모델

## 사용 방법

### 1. Quick 테스트 (빠른 검증)

품질별 1개 샘플 × 5회 반복 = 25회 평가

```bash
# Docker 컨테이너 접속
docker exec -it skn20-final-5team-backend-1 bash

# Quick 테스트 실행
cd /app/scripts
python run_model_comparison.py --quick --trials 5
```

### 2. Full 평가 (전체 검증)

60개 샘플 × 5개 모델 × 5회 반복 = 1,500회 평가

```bash
python run_model_comparison.py --trials 5
```

### 3. 특정 모델만 평가

```bash
python run_model_comparison.py --models gpt-4o gpt-4o-mini --trials 5
```

### 4. 결과 분석

```bash
python analyze_model_comparison.py
```

### 5. 시각화 생성

```bash
python visualize_model_comparison.py
```

### 6. 전체 프로세스 자동 실행 (Quick 모드)

```bash
bash run_full_model_comparison.sh quick
```

### 7. 전체 프로세스 자동 실행 (Full 모드)

```bash
bash run_full_model_comparison.sh full
```

## 출력 결과

### 데이터 파일
```
data/validation/model_comparison/
├── model_comparison_results.json      # 전체 평가 결과
├── model_comparison_analysis.json     # 분석 결과
├── gpt-4o_results.json               # 개별 모델 결과
├── gpt-4o-mini_results.json
├── gpt-3.5-turbo_results.json
├── Llama-3.1-70B_results.json
└── Mixtral-8x7B_results.json
```

### 시각화 파일
```
data/validation/model_comparison/visualizations/
├── consistency_comparison.png         # 일관성 비교
├── discrimination_comparison.png      # 구분력 비교
├── performance_comparison.png         # 성능(속도/비용) 비교
├── quality_distribution.png           # 품질별 점수 분포
├── overall_ranking.png                # 종합 순위
└── radar_chart.png                    # 레이더 차트
```

## 예상 비용 (Full 평가 기준)

- **gpt-4o**: ~$1.50
- **gpt-4o-mini**: ~$0.10 (현재 사용 중)
- **gpt-3.5-turbo**: ~$0.30
- **Llama-3.1-70B**: 무료 (Hugging Face Inference API)
- **Mixtral-8x7B**: 무료 (Hugging Face Inference API)

**총 예상 비용**: ~$2.00 (OpenAI만) 또는 무료 (Hugging Face만)

## 평가 지표 상세

### 1. 일관성 (Consistency)
- **측정**: 동일 샘플을 5회 반복 평가했을 때의 표준편차
- **목표**: ≤ 5점
- **의미**: 낮을수록 평가가 일관적임

### 2. 구분력 (Discrimination)
- **측정**: 우수 케이스 평균 점수 - 매우 미흡 케이스 평균 점수
- **목표**: ≥ 30점
- **의미**: 높을수록 품질 차이를 잘 구분함

### 3. 순위 정확도 (Ranking Accuracy)
- **측정**: Kendall's Tau (품질 레벨 순서 일치도)
- **목표**: ≥ 0.8
- **의미**: 높을수록 품질 레벨 순서를 정확히 평가함

### 4. 속도 (Speed)
- **측정**: 평균 응답 시간 (초)
- **의미**: 낮을수록 빠름

### 5. 비용 (Cost)
- **측정**: 총 API 비용 (USD)
- **의미**: 낮을수록 경제적

### 6. 신뢰성 (Reliability)
- **측정**: 오류율 (%)
- **목표**: < 5%
- **의미**: 낮을수록 안정적

## 종합 점수 계산

각 지표를 0-100으로 정규화하고 가중치를 적용하여 종합 점수 산출:

```python
가중치:
- 일관성: 2.0
- 구분력: 2.0
- 순위 정확도: 1.5
- 속도: 1.0
- 비용: 1.5
- 신뢰성: 2.0
```

## 문제 해결

### Hugging Face 모델이 로딩 중일 때
- 에러: "Model is loading, please retry"
- 해결: 1-2분 대기 후 재시도

### API Rate Limit 에러
- OpenAI: 요청 간 0.5초 대기 (코드에 포함됨)
- Hugging Face: 무료 티어 제한 있음

### 메모리 부족
- Quick 모드로 먼저 테스트
- 모델 수를 줄여서 실행

## 권장 사항

1. **처음 실행 시**: Quick 모드로 모든 모델이 정상 작동하는지 확인
2. **비용 절감**: Hugging Face 모델만 사용 (`--models Llama-3.1-70B Mixtral-8x7B`)
3. **빠른 평가**: gpt-4o-mini + Hugging Face 조합 권장
4. **정확도 우선**: gpt-4o 포함하여 평가

## 예제 결과 해석

```
🏆 종합 순위
1. gpt-4o-mini: 8.45점
2. gpt-4o: 8.12점
3. Llama-3.1-70B: 7.23점
4. gpt-3.5-turbo: 6.98점
5. Mixtral-8x7B: 6.45점

✨ 최우수 모델: gpt-4o-mini
```

**해석**: gpt-4o-mini가 일관성, 구분력, 속도, 비용 측면에서 종합적으로 가장 우수하여 Bug Hunt 평가 시스템에 최적임을 입증
