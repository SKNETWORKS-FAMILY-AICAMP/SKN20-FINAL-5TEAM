"""
모델 비교 분석 스크립트

여러 모델의 평가 결과를 분석하고 비교 지표 산출
"""
import json
import numpy as np
from pathlib import Path
from scipy import stats


class ModelComparisonAnalyzer:
    """모델 비교 분석기"""

    def __init__(self, results_file):
        self.results_file = results_file
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.metadata = data['metadata']
            self.model_results = data['model_results']

    def extract_scores(self, model_name):
        """모델별 점수 추출"""
        model_data = self.model_results[model_name]
        scores = []
        quality_scores = {'excellent': [], 'good': [], 'average': [], 'poor': [], 'very_poor': []}

        for sample_result in model_data['results']:
            quality = sample_result['quality_level']
            for trial in sample_result['trials']:
                if 'error' not in trial:
                    score = trial['thinking_score']
                    scores.append(score)
                    quality_scores[quality].append(score)

        return scores, quality_scores

    def calculate_consistency(self, model_name):
        """일관성 분석: 동일 샘플 반복 평가의 표준편차"""
        model_data = self.model_results[model_name]
        std_devs = []

        for sample_result in model_data['results']:
            sample_scores = []
            for trial in sample_result['trials']:
                if 'error' not in trial:
                    sample_scores.append(trial['thinking_score'])

            if len(sample_scores) > 1:
                std_devs.append(np.std(sample_scores))

        return {
            'avg_std_dev': np.mean(std_devs) if std_devs else 0,
            'max_std_dev': max(std_devs) if std_devs else 0,
            'min_std_dev': min(std_devs) if std_devs else 0
        }

    def calculate_discrimination(self, model_name):
        """극단 케이스 구분력: 우수 vs 매우 미흡 점수 차이"""
        _, quality_scores = self.extract_scores(model_name)

        excellent_avg = np.mean(quality_scores['excellent']) if quality_scores['excellent'] else 0
        very_poor_avg = np.mean(quality_scores['very_poor']) if quality_scores['very_poor'] else 0

        return {
            'excellent_avg': excellent_avg,
            'very_poor_avg': very_poor_avg,
            'score_diff': excellent_avg - very_poor_avg,
            'quality_means': {q: np.mean(scores) if scores else 0 for q, scores in quality_scores.items()}
        }

    def calculate_ranking_accuracy(self, model_name):
        """순위 정확도: Kendall's Tau"""
        _, quality_scores = self.extract_scores(model_name)

        # 품질 레벨별 평균 점수
        quality_order = ['excellent', 'good', 'average', 'poor', 'very_poor']
        actual_means = [np.mean(quality_scores[q]) if quality_scores[q] else 0 for q in quality_order]

        # 예상 순위 (높은 점수부터 낮은 점수)
        expected_ranks = [5, 4, 3, 2, 1]  # excellent=5, very_poor=1
        actual_ranks = stats.rankdata(actual_means)

        # Kendall's Tau
        tau, p_value = stats.kendalltau(expected_ranks, actual_ranks)

        return {
            'kendall_tau': tau,
            'p_value': p_value,
            'actual_means': dict(zip(quality_order, actual_means))
        }

    def calculate_performance_metrics(self, model_name):
        """성능 지표: 비용, 속도, 토큰"""
        model_data = self.model_results[model_name]
        stats_data = model_data.get('stats', {})

        times = []
        costs = []

        for sample_result in model_data['results']:
            for trial in sample_result['trials']:
                if 'error' not in trial:
                    times.append(trial.get('time', 0))
                    costs.append(trial.get('cost', 0))

        return {
            'avg_time': np.mean(times) if times else 0,
            'total_cost': sum(costs),
            'total_tokens': stats_data.get('total_tokens', 0),
            'total_evaluations': len(times)
        }

    def calculate_error_rate(self, model_name):
        """오류율 계산"""
        model_data = self.model_results[model_name]
        total = 0
        errors = 0

        for sample_result in model_data['results']:
            for trial in sample_result['trials']:
                total += 1
                if 'error' in trial:
                    errors += 1

        return {
            'error_count': errors,
            'total_count': total,
            'error_rate': (errors / total * 100) if total > 0 else 0
        }

    def analyze_all_models(self):
        """모든 모델 분석"""
        analysis = {}

        for model_name in self.model_results.keys():
            print(f"📊 분석 중: {model_name}")

            analysis[model_name] = {
                'consistency': self.calculate_consistency(model_name),
                'discrimination': self.calculate_discrimination(model_name),
                'ranking': self.calculate_ranking_accuracy(model_name),
                'performance': self.calculate_performance_metrics(model_name),
                'error_rate': self.calculate_error_rate(model_name)
            }

        return analysis

    def create_comparison_summary(self, analysis):
        """비교 요약 생성"""
        summary = {
            'models': list(analysis.keys()),
            'comparison': {}
        }

        # 각 지표별 순위
        metrics = {
            'consistency': {model: analysis[model]['consistency']['avg_std_dev'] for model in analysis},
            'discrimination': {model: analysis[model]['discrimination']['score_diff'] for model in analysis},
            'ranking_accuracy': {model: analysis[model]['ranking']['kendall_tau'] for model in analysis},
            'speed': {model: analysis[model]['performance']['avg_time'] for model in analysis},
            'cost': {model: analysis[model]['performance']['total_cost'] for model in analysis},
            'error_rate': {model: analysis[model]['error_rate']['error_rate'] for model in analysis}
        }

        # 순위 계산 (낮을수록 좋음: consistency, speed, cost, error_rate / 높을수록 좋음: discrimination, ranking_accuracy)
        for metric, values in metrics.items():
            if metric in ['consistency', 'speed', 'cost', 'error_rate']:
                # 낮을수록 좋음 (오름차순)
                sorted_models = sorted(values.items(), key=lambda x: x[1])
            else:
                # 높을수록 좋음 (내림차순)
                sorted_models = sorted(values.items(), key=lambda x: x[1], reverse=True)

            summary['comparison'][metric] = {
                'values': values,
                'ranking': [model for model, _ in sorted_models],
                'best': sorted_models[0][0],
                'worst': sorted_models[-1][0]
            }

        # 종합 점수 계산 (각 지표를 정규화하여 합산)
        model_scores = {model: 0 for model in analysis}

        for metric, data in summary['comparison'].items():
            values = list(data['values'].values())
            min_val = min(values)
            max_val = max(values)
            range_val = max_val - min_val if max_val > min_val else 1

            for model in analysis:
                value = data['values'][model]

                if metric in ['consistency', 'speed', 'cost', 'error_rate']:
                    # 낮을수록 좋음 (역정규화)
                    normalized = 1 - (value - min_val) / range_val
                else:
                    # 높을수록 좋음
                    normalized = (value - min_val) / range_val

                # 가중치 적용
                weights = {
                    'consistency': 2.0,
                    'discrimination': 2.0,
                    'ranking_accuracy': 1.5,
                    'speed': 1.0,
                    'cost': 1.5,
                    'error_rate': 2.0
                }

                model_scores[model] += normalized * weights.get(metric, 1.0)

        # 종합 순위
        sorted_scores = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        summary['overall_ranking'] = {
            'scores': model_scores,
            'ranking': [model for model, _ in sorted_scores],
            'best_model': sorted_scores[0][0],
            'best_score': sorted_scores[0][1]
        }

        return summary

    def generate_report(self, output_file):
        """전체 분석 보고서 생성"""
        print("\n🔍 모델 비교 분석 시작...")

        analysis = self.analyze_all_models()
        summary = self.create_comparison_summary(analysis)

        report = {
            'metadata': self.metadata,
            'analysis': analysis,
            'summary': summary
        }

        # 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 분석 완료!")
        print(f"📁 저장: {output_file}")

        # 요약 출력
        print(f"\n{'='*60}")
        print(f"📊 모델 비교 요약")
        print(f"{'='*60}")

        for model in summary['models']:
            print(f"\n🤖 {model}")
            print(f"  일관성 (표준편차): {analysis[model]['consistency']['avg_std_dev']:.2f}")
            print(f"  구분력 (점수 차이): {analysis[model]['discrimination']['score_diff']:.2f}")
            print(f"  순위 정확도 (Kendall τ): {analysis[model]['ranking']['kendall_tau']:.3f}")
            print(f"  평균 응답 시간: {analysis[model]['performance']['avg_time']:.2f}s")
            print(f"  총 비용: ${analysis[model]['performance']['total_cost']:.4f}")
            print(f"  오류율: {analysis[model]['error_rate']['error_rate']:.1f}%")

        print(f"\n{'='*60}")
        print(f"🏆 종합 순위")
        print(f"{'='*60}")

        for idx, model in enumerate(summary['overall_ranking']['ranking'], 1):
            score = summary['overall_ranking']['scores'][model]
            print(f"{idx}. {model}: {score:.2f}점")

        print(f"\n✨ 최우수 모델: {summary['overall_ranking']['best_model']}")

        return report


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent.parent.parent / 'data' / 'validation' / 'model_comparison'
    results_file = data_dir / 'model_comparison_results.json'
    output_file = data_dir / 'model_comparison_analysis.json'

    analyzer = ModelComparisonAnalyzer(results_file)
    analyzer.generate_report(output_file)
