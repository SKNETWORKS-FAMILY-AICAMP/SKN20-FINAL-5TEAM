"""
Bug Hunt 평가 검증 결과 분석

4가지 검증:
1. 평가 일관성 (Consistency)
2. 극단 케이스 구분력 (Discrimination)
3. 상대 평가 정확도 (Ranking)
4. 규칙 기반 교차 검증 (Convergent Validity)
"""
import json
import numpy as np
from scipy import stats
from pathlib import Path
from collections import defaultdict


class ValidationAnalyzer:
    """검증 결과 분석기"""

    def __init__(self, evaluation_results_file, rule_based_scores_file):
        self.evaluation_results_file = evaluation_results_file
        self.rule_based_scores_file = rule_based_scores_file
        self.evaluation_data = None
        self.rule_scores = None

    def load_data(self):
        """데이터 로드"""
        with open(self.evaluation_results_file, 'r', encoding='utf-8') as f:
            self.evaluation_data = json.load(f)

        with open(self.rule_based_scores_file, 'r', encoding='utf-8') as f:
            self.rule_scores = {item['sample_id']: item['rule_based_score']
                               for item in json.load(f)}

        print(f"✅ 데이터 로드 완료")
        print(f"   평가 결과: {len(self.evaluation_data['results'])}개 샘플")
        print(f"   규칙 점수: {len(self.rule_scores)}개 샘플")

    def analyze_consistency(self):
        """
        검증 1: 평가 일관성
        동일 샘플을 반복 평가했을 때 점수의 표준편차 측정
        """
        print("\n" + "="*60)
        print("📊 검증 1: 평가 일관성 (Consistency)")
        print("="*60)

        consistency_results = []

        for sample_result in self.evaluation_data['results']:
            sample_id = sample_result['sample_id']
            trials = sample_result['trials']

            # 에러 제외
            valid_trials = [t for t in trials if 'error' not in t]

            if len(valid_trials) < 2:
                continue

            # 사고 점수의 표준편차 계산
            thinking_scores = [t['thinking_score'] for t in valid_trials]
            std_dev = np.std(thinking_scores, ddof=1)
            mean_score = np.mean(thinking_scores)

            consistency_results.append({
                'sample_id': sample_id,
                'quality': sample_result['quality_level'],
                'mean_score': mean_score,
                'std_dev': std_dev,
                'scores': thinking_scores
            })

        # 통계
        all_std_devs = [r['std_dev'] for r in consistency_results]
        avg_std_dev = np.mean(all_std_devs)
        max_std_dev = np.max(all_std_devs)

        print(f"\n결과:")
        print(f"  평균 표준편차: {avg_std_dev:.2f}점 (목표 ≤5점)")
        print(f"  최대 표준편차: {max_std_dev:.2f}점 (목표 ≤10점)")
        print(f"  판정: {'✅ 통과' if avg_std_dev <= 5 else '❌ 미달'}")

        # 품질별 일관성
        print(f"\n품질별 일관성:")
        for quality in ['excellent', 'good', 'average', 'poor', 'very_poor']:
            quality_results = [r for r in consistency_results if r['quality'] == quality]
            if quality_results:
                quality_std = np.mean([r['std_dev'] for r in quality_results])
                print(f"  {quality:12s}: 평균 σ = {quality_std:.2f}점")

        return {
            'avg_std_dev': avg_std_dev,
            'max_std_dev': max_std_dev,
            'passed': avg_std_dev <= 5,
            'details': consistency_results
        }

    def analyze_discrimination(self):
        """
        검증 2: 극단 케이스 구분력
        우수 그룹과 매우 미흡 그룹의 점수 차이
        """
        print("\n" + "="*60)
        print("📊 검증 2: 극단 케이스 구분력 (Discrimination)")
        print("="*60)

        # 각 샘플의 평균 점수 계산
        sample_avg_scores = {}
        for sample_result in self.evaluation_data['results']:
            sample_id = sample_result['sample_id']
            quality = sample_result['quality_level']
            trials = sample_result['trials']

            valid_trials = [t for t in trials if 'error' not in t]
            if not valid_trials:
                continue

            avg_score = np.mean([t['thinking_score'] for t in valid_trials])
            sample_avg_scores[sample_id] = {
                'score': avg_score,
                'quality': quality
            }

        # 우수 vs 매우 미흡 비교
        excellent_scores = [v['score'] for k, v in sample_avg_scores.items()
                           if v['quality'] == 'excellent']
        very_poor_scores = [v['score'] for k, v in sample_avg_scores.items()
                           if v['quality'] == 'very_poor']

        excellent_mean = np.mean(excellent_scores) if excellent_scores else 0
        very_poor_mean = np.mean(very_poor_scores) if very_poor_scores else 0
        score_diff = excellent_mean - very_poor_mean

        print(f"\n결과:")
        print(f"  우수 그룹 평균: {excellent_mean:.1f}점 (n={len(excellent_scores)})")
        print(f"  매우 미흡 그룹 평균: {very_poor_mean:.1f}점 (n={len(very_poor_scores)})")
        print(f"  점수 차이: {score_diff:.1f}점 (목표 ≥30점)")
        print(f"  판정: {'✅ 통과' if score_diff >= 30 else '❌ 미달'}")

        # 모든 품질 레벨의 평균
        print(f"\n품질별 평균 점수:")
        for quality in ['excellent', 'good', 'average', 'poor', 'very_poor']:
            quality_scores = [v['score'] for k, v in sample_avg_scores.items()
                            if v['quality'] == quality]
            if quality_scores:
                quality_mean = np.mean(quality_scores)
                quality_std = np.std(quality_scores)
                print(f"  {quality:12s}: {quality_mean:.1f}±{quality_std:.1f}점")

        return {
            'excellent_mean': excellent_mean,
            'very_poor_mean': very_poor_mean,
            'score_diff': score_diff,
            'passed': score_diff >= 30,
            'all_scores': sample_avg_scores
        }

    def analyze_ranking(self):
        """
        검증 3: 상대 평가 정확도
        같은 케이스 내 5개 품질 레벨의 순위 일치도 (Kendall's Tau)
        """
        print("\n" + "="*60)
        print("📊 검증 3: 상대 평가 정확도 (Ranking Validation)")
        print("="*60)

        # 케이스별로 그룹화
        cases = defaultdict(list)
        for sample_result in self.evaluation_data['results']:
            case_id = sample_result['case_id']
            quality = sample_result['quality_level']
            trials = sample_result['trials']

            valid_trials = [t for t in trials if 'error' not in t]
            if not valid_trials:
                continue

            avg_score = np.mean([t['thinking_score'] for t in valid_trials])
            cases[case_id].append({
                'quality': quality,
                'score': avg_score
            })

        # 기대 순위: excellent > good > average > poor > very_poor
        quality_rank = {
            'excellent': 5,
            'good': 4,
            'average': 3,
            'poor': 2,
            'very_poor': 1
        }

        kendall_taus = []
        perfect_rankings = 0
        total_cases = 0

        print(f"\n케이스별 순위 분석:")
        for case_id, samples in cases.items():
            if len(samples) < 5:  # 5개 품질이 모두 있어야 함
                continue

            total_cases += 1

            # 정렬
            samples.sort(key=lambda x: x['score'], reverse=True)

            # 기대 순위와 실제 순위 비교
            expected_ranks = [quality_rank[s['quality']] for s in samples]
            actual_ranks = list(range(len(samples), 0, -1))

            tau, p_value = stats.kendalltau(expected_ranks, actual_ranks)
            kendall_taus.append(tau)

            # 완벽한 순위인지 확인
            expected_order = ['excellent', 'good', 'average', 'poor', 'very_poor']
            actual_order = [s['quality'] for s in samples]
            is_perfect = expected_order == actual_order

            if is_perfect:
                perfect_rankings += 1

            status = "✅" if is_perfect else "⚠️"
            print(f"  {case_id:20s} {status} τ={tau:.3f} | {[s['quality'][:4] for s in samples]}")

        avg_tau = np.mean(kendall_taus) if kendall_taus else 0
        perfect_ratio = perfect_rankings / total_cases if total_cases > 0 else 0

        print(f"\n결과:")
        print(f"  평균 Kendall's Tau: {avg_tau:.3f} (목표 ≥0.75)")
        print(f"  완벽한 순위: {perfect_rankings}/{total_cases} ({perfect_ratio*100:.1f}%)")
        print(f"  판정: {'✅ 통과' if avg_tau >= 0.75 else '❌ 미달'}")

        return {
            'avg_kendall_tau': avg_tau,
            'perfect_rankings': perfect_rankings,
            'total_cases': total_cases,
            'passed': avg_tau >= 0.75
        }

    def analyze_convergent_validity(self):
        """
        검증 4: 규칙 기반 교차 검증
        규칙 기반 점수와 LLM 점수의 상관관계 (Pearson r)
        """
        print("\n" + "="*60)
        print("📊 검증 4: 규칙 기반 교차 검증 (Convergent Validity)")
        print("="*60)

        rule_scores_list = []
        llm_scores_list = []

        for sample_result in self.evaluation_data['results']:
            sample_id = sample_result['sample_id']
            trials = sample_result['trials']

            if sample_id not in self.rule_scores:
                continue

            valid_trials = [t for t in trials if 'error' not in t]
            if not valid_trials:
                continue

            rule_score = self.rule_scores[sample_id]
            llm_score = np.mean([t['thinking_score'] for t in valid_trials])

            rule_scores_list.append(rule_score)
            llm_scores_list.append(llm_score)

        # Pearson 상관계수
        r, p_value = stats.pearsonr(rule_scores_list, llm_scores_list)

        print(f"\n결과:")
        print(f"  Pearson 상관계수: r = {r:.3f} (목표 ≥0.65)")
        print(f"  p-value: {p_value:.4f}")
        print(f"  판정: {'✅ 통과' if r >= 0.65 else '❌ 미달'}")

        # 품질별 상관관계
        print(f"\n품질별 상관관계:")
        for quality in ['excellent', 'good', 'average', 'poor', 'very_poor']:
            quality_rule = []
            quality_llm = []

            for sample_result in self.evaluation_data['results']:
                if sample_result['quality_level'] != quality:
                    continue

                sample_id = sample_result['sample_id']
                if sample_id not in self.rule_scores:
                    continue

                trials = sample_result['trials']
                valid_trials = [t for t in trials if 'error' not in t]
                if not valid_trials:
                    continue

                quality_rule.append(self.rule_scores[sample_id])
                quality_llm.append(np.mean([t['thinking_score'] for t in valid_trials]))

            if len(quality_rule) >= 3:  # 최소 3개 이상
                r_quality, _ = stats.pearsonr(quality_rule, quality_llm)
                print(f"  {quality:12s}: r = {r_quality:.3f}")

        return {
            'pearson_r': r,
            'p_value': p_value,
            'passed': r >= 0.65,
            'rule_scores': rule_scores_list,
            'llm_scores': llm_scores_list
        }

    def generate_summary_report(self, results):
        """종합 보고서 생성"""
        print("\n" + "="*60)
        print("📋 종합 검증 보고서")
        print("="*60)

        all_passed = all([
            results['consistency']['passed'],
            results['discrimination']['passed'],
            results['ranking']['passed'],
            results['convergent_validity']['passed']
        ])

        print(f"\n검증 결과:")
        print(f"  1. 평가 일관성:        {'✅ 통과' if results['consistency']['passed'] else '❌ 미달'} "
              f"(σ={results['consistency']['avg_std_dev']:.2f}점)")
        print(f"  2. 극단 케이스 구분:   {'✅ 통과' if results['discrimination']['passed'] else '❌ 미달'} "
              f"(차이={results['discrimination']['score_diff']:.1f}점)")
        print(f"  3. 상대 평가 정확도:   {'✅ 통과' if results['ranking']['passed'] else '❌ 미달'} "
              f"(τ={results['ranking']['avg_kendall_tau']:.3f})")
        print(f"  4. 규칙 기반 교차검증: {'✅ 통과' if results['convergent_validity']['passed'] else '❌ 미달'} "
              f"(r={results['convergent_validity']['pearson_r']:.3f})")

        print(f"\n최종 판정: {'✅ 전체 통과' if all_passed else '⚠️ 일부 미달'}")

        return {
            'all_passed': all_passed,
            'summary': {
                'consistency': {
                    'passed': results['consistency']['passed'],
                    'avg_std_dev': results['consistency']['avg_std_dev']
                },
                'discrimination': {
                    'passed': results['discrimination']['passed'],
                    'score_diff': results['discrimination']['score_diff']
                },
                'ranking': {
                    'passed': results['ranking']['passed'],
                    'avg_kendall_tau': results['ranking']['avg_kendall_tau']
                },
                'convergent_validity': {
                    'passed': results['convergent_validity']['passed'],
                    'pearson_r': results['convergent_validity']['pearson_r']
                }
            }
        }

    def run_all_analyses(self):
        """모든 분석 실행"""
        self.load_data()

        results = {
            'consistency': self.analyze_consistency(),
            'discrimination': self.analyze_discrimination(),
            'ranking': self.analyze_ranking(),
            'convergent_validity': self.analyze_convergent_validity()
        }

        summary = self.generate_summary_report(results)
        results['summary'] = summary

        # 결과 저장
        output_file = Path(self.evaluation_results_file).parent / 'analysis_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)

        print(f"\n📁 분석 결과 저장: {output_file}")

        return results


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent.parent.parent / 'data' / 'validation'
    evaluation_results = data_dir / 'evaluation_results.json'
    rule_scores = data_dir / 'rule_based_scores.json'

    analyzer = ValidationAnalyzer(evaluation_results, rule_scores)
    results = analyzer.run_all_analyses()
