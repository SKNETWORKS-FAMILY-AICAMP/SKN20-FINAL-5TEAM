#!/bin/bash

# 모델 비교 평가 전체 프로세스 자동 실행 스크립트

MODE=${1:-quick}  # quick 또는 full (기본값: quick)

echo "=================================="
echo "모델 비교 평가 시스템"
echo "=================================="
echo "모드: $MODE"
echo ""

# 1. 평가 실행
echo "🚀 1단계: 모델 비교 평가 실행 중..."
if [ "$MODE" = "quick" ]; then
    python run_model_comparison.py --quick --trials 5
else
    python run_model_comparison.py --trials 5
fi

if [ $? -ne 0 ]; then
    echo "❌ 평가 실행 실패"
    exit 1
fi

echo "✅ 평가 완료"
echo ""

# 2. 결과 분석
echo "🔍 2단계: 결과 분석 중..."
python analyze_model_comparison.py

if [ $? -ne 0 ]; then
    echo "❌ 분석 실패"
    exit 1
fi

echo "✅ 분석 완료"
echo ""

# 3. 시각화 생성
echo "🎨 3단계: 시각화 생성 중..."
python visualize_model_comparison.py

if [ $? -ne 0 ]; then
    echo "❌ 시각화 생성 실패"
    exit 1
fi

echo "✅ 시각화 완료"
echo ""

# 4. 결과 요약 출력
echo "=================================="
echo "✅ 모든 프로세스 완료!"
echo "=================================="
echo ""
echo "📁 결과 파일 위치:"
echo "  - 평가 결과: data/validation/model_comparison/model_comparison_results.json"
echo "  - 분석 결과: data/validation/model_comparison/model_comparison_analysis.json"
echo "  - 시각화: data/validation/model_comparison/visualizations/"
echo ""
echo "📊 생성된 그래프:"
echo "  1. consistency_comparison.png - 일관성 비교"
echo "  2. discrimination_comparison.png - 구분력 비교"
echo "  3. performance_comparison.png - 성능(속도/비용) 비교"
echo "  4. quality_distribution.png - 품질별 점수 분포"
echo "  5. overall_ranking.png - 종합 순위"
echo "  6. radar_chart.png - 레이더 차트"
echo ""
echo "💡 Docker 외부에서 결과 복사:"
echo "   docker cp skn20-final-5team-backend-1:/app/../data/validation/model_comparison ./data/validation/"
echo ""
