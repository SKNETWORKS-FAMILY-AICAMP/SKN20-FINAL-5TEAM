"""
BEFORE vs AFTER 프롬프트 비교 분석 스크립트

BEFORE: 원본 프롬프트 (주관적 평가)
AFTER: 개선된 프롬프트 (5가지 기준 + Few-shot)
"""
import json
import numpy as np
from pathlib import Path


class PromptComparisonAnalyzer:
    """BEFORE vs AFTER 프롬프트 비교 분석"""

    def __init__(self, before_file, after_file):
        with open(before_file, 'r', encoding='utf-8') as f:
            before_data = json.load(f)
            self.before_results = before_data['results']

        with open(after_file, 'r', encoding='utf-8') as f:
            after_data = json.load(f)
            self.after_results = after_data['results']

    def extract_scores_by_quality(self, results):
        """품질 레벨별 점수 추출"""
        quality_scores = {
            'excellent': [],
            'good': [],
            'average': [],
            'poor': [],
            'very_poor': []
        }

        for sample in results:
            quality = sample['quality_level']
            for trial in sample['trials']:
                if 'error' not in trial:
                    score = trial['thinking_score']
                    quality_scores[quality].append(score)

        return quality_scores

    def calculate_consistency(self, results):
        """일관성 분석: 동일 샘플의 표준편차"""
        std_devs = []

        for sample in results:
            sample_scores = []
            for trial in sample['trials']:
                if 'error' not in trial:
                    sample_scores.append(trial['thinking_score'])

            if len(sample_scores) > 1:
                std_devs.append(np.std(sample_scores))

        return {
            'avg_std_dev': np.mean(std_devs) if std_devs else 0,
            'max_std_dev': max(std_devs) if std_devs else 0,
            'min_std_dev': min(std_devs) if std_devs else 0,
            'all_std_devs': std_devs
        }

    def calculate_discrimination(self, quality_scores):
        """구분력: Excellent vs Very Poor 점수 차이"""
        excellent_avg = np.mean(quality_scores['excellent']) if quality_scores['excellent'] else 0
        very_poor_avg = np.mean(quality_scores['very_poor']) if quality_scores['very_poor'] else 0
        good_avg = np.mean(quality_scores['good']) if quality_scores['good'] else 0

        return {
            'excellent_avg': excellent_avg,
            'good_avg': good_avg,
            'very_poor_avg': very_poor_avg,
            'excellent_vs_very_poor_diff': excellent_avg - very_poor_avg,
            'excellent_vs_good_diff': excellent_avg - good_avg,
            'quality_means': {q: np.mean(scores) if scores else 0 for q, scores in quality_scores.items()}
        }

    def calculate_score_distribution(self, quality_scores):
        """점수 분포 분석"""
        all_scores = []
        for scores in quality_scores.values():
            all_scores.extend(scores)

        return {
            'min': min(all_scores) if all_scores else 0,
            'max': max(all_scores) if all_scores else 0,
            'mean': np.mean(all_scores) if all_scores else 0,
            'std': np.std(all_scores) if all_scores else 0,
            'range': max(all_scores) - min(all_scores) if all_scores else 0
        }

    def compare(self):
        """전체 비교 분석"""
        print("=" * 80)
        print("📊 BEFORE vs AFTER 프롬프트 비교 분석")
        print("=" * 80)

        # BEFORE 분석
        before_quality_scores = self.extract_scores_by_quality(self.before_results)
        before_consistency = self.calculate_consistency(self.before_results)
        before_discrimination = self.calculate_discrimination(before_quality_scores)
        before_distribution = self.calculate_score_distribution(before_quality_scores)

        # AFTER 분석
        after_quality_scores = self.extract_scores_by_quality(self.after_results)
        after_consistency = self.calculate_consistency(self.after_results)
        after_discrimination = self.calculate_discrimination(after_quality_scores)
        after_distribution = self.calculate_score_distribution(after_quality_scores)

        # 결과 출력
        print("\n1️⃣ 일관성 (Consistency) - 낮을수록 좋음")
        print("-" * 80)
        print(f"  BEFORE 평균 표준편차: {before_consistency['avg_std_dev']:.2f}점")
        print(f"  AFTER  평균 표준편차: {after_consistency['avg_std_dev']:.2f}점")
        improvement_consistency = ((before_consistency['avg_std_dev'] - after_consistency['avg_std_dev']) / before_consistency['avg_std_dev'] * 100) if before_consistency['avg_std_dev'] > 0 else 0
        print(f"  개선율: {improvement_consistency:+.1f}% {'✅' if improvement_consistency > 0 else '❌'}")

        print("\n2️⃣ 구분력 (Discrimination)")
        print("-" * 80)
        print(f"  BEFORE Excellent vs Very Poor 차이: {before_discrimination['excellent_vs_very_poor_diff']:.2f}점")
        print(f"  AFTER  Excellent vs Very Poor 차이: {after_discrimination['excellent_vs_very_poor_diff']:.2f}점")
        improvement_disc = after_discrimination['excellent_vs_very_poor_diff'] - before_discrimination['excellent_vs_very_poor_diff']
        print(f"  개선: {improvement_disc:+.2f}점 {'✅' if improvement_disc > 0 else '❌'}")

        print(f"\n  BEFORE Excellent vs Good 차이: {before_discrimination['excellent_vs_good_diff']:.2f}점")
        print(f"  AFTER  Excellent vs Good 차이: {after_discrimination['excellent_vs_good_diff']:.2f}점")
        improvement_ex_good = after_discrimination['excellent_vs_good_diff'] - before_discrimination['excellent_vs_good_diff']
        print(f"  개선: {improvement_ex_good:+.2f}점 {'✅' if improvement_ex_good > 0 else '❌'}")

        print("\n3️⃣ 품질 레벨별 평균 점수")
        print("-" * 80)
        print(f"  {'품질':<12} {'BEFORE':>10} {'AFTER':>10} {'변화':>10}")
        print("-" * 80)
        for quality in ['excellent', 'good', 'average', 'poor', 'very_poor']:
            before_avg = before_discrimination['quality_means'][quality]
            after_avg = after_discrimination['quality_means'][quality]
            diff = after_avg - before_avg
            print(f"  {quality:<12} {before_avg:>10.2f} {after_avg:>10.2f} {diff:>+10.2f}")

        print("\n4️⃣ 점수 분포 (Score Distribution)")
        print("-" * 80)
        print(f"  {'지표':<15} {'BEFORE':>10} {'AFTER':>10} {'개선':>10}")
        print("-" * 80)
        print(f"  {'최소값':<15} {before_distribution['min']:>10.2f} {after_distribution['min']:>10.2f} {after_distribution['min']-before_distribution['min']:>+10.2f}")
        print(f"  {'최대값':<15} {before_distribution['max']:>10.2f} {after_distribution['max']:>10.2f} {after_distribution['max']-before_distribution['max']:>+10.2f}")
        print(f"  {'평균':<15} {before_distribution['mean']:>10.2f} {after_distribution['mean']:>10.2f} {after_distribution['mean']-before_distribution['mean']:>+10.2f}")
        print(f"  {'표준편차':<15} {before_distribution['std']:>10.2f} {after_distribution['std']:>10.2f} {after_distribution['std']-before_distribution['std']:>+10.2f}")
        print(f"  {'점수 범위':<15} {before_distribution['range']:>10.2f} {after_distribution['range']:>10.2f} {after_distribution['range']-before_distribution['range']:>+10.2f}")

        print("\n" + "=" * 80)
        print("📈 종합 평가")
        print("=" * 80)

        improvements = []
        if improvement_consistency > 0:
            improvements.append(f"✅ 일관성 {improvement_consistency:.1f}% 개선")
        else:
            improvements.append(f"❌ 일관성 {abs(improvement_consistency):.1f}% 악화")

        if improvement_disc > 0:
            improvements.append(f"✅ 구분력 {improvement_disc:.2f}점 향상")
        else:
            improvements.append(f"❌ 구분력 {abs(improvement_disc):.2f}점 감소")

        if after_distribution['range'] > before_distribution['range']:
            improvements.append(f"✅ 점수 범위 {after_distribution['range'] - before_distribution['range']:.2f}점 확장")
        else:
            improvements.append(f"❌ 점수 범위 {before_distribution['range'] - after_distribution['range']:.2f}점 축소")

        for imp in improvements:
            print(f"  {imp}")

        # JSON 결과 저장
        comparison_result = {
            'before': {
                'consistency': before_consistency,
                'discrimination': before_discrimination,
                'distribution': before_distribution
            },
            'after': {
                'consistency': after_consistency,
                'discrimination': after_discrimination,
                'distribution': after_distribution
            },
            'improvements': {
                'consistency_pct': improvement_consistency,
                'discrimination_diff': improvement_disc,
                'excellent_good_diff': improvement_ex_good,
                'range_diff': after_distribution['range'] - before_distribution['range']
            }
        }

        return comparison_result


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent.parent
    before_file = base_dir / 'data' / 'validation' / 'bughunt_validation' / 'evaluation_results.json'
    after_file = base_dir / 'data' / 'validation' / 'prompt_improved_evaluation_results.json'

    analyzer = PromptComparisonAnalyzer(before_file, after_file)
    result = analyzer.compare()

    # 결과 저장
    output_file = base_dir / 'data' / 'validation' / 'before_after_comparison.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n💾 비교 결과 저장: {output_file}")
