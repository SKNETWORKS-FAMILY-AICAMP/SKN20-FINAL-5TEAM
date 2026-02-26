"""
BugHunt 면접 평가자 신뢰성 검증 - 결과 분석

4가지 검증:
1. 평가 일관성 (Consistency)         - 동일 샘플 반복 평가 표준편차
2. 극단 케이스 구분력 (Discrimination) - excellent vs very_poor 점수 차이
3. 순위 정확도 (Ranking)              - Kendall's Tau
4. 수렴 타당도 (Convergent Validity)  - 규칙 기반 점수와 Pearson r
"""
import json
import numpy as np
from scipy import stats
from pathlib import Path
from collections import defaultdict

# 버그 유형별 루브릭 키워드 (core 40점 + mechanism 35점 + application 25점)
RUBRIC_KEYWORDS = {
    "data_leakage": {
        "core": ["train_test_split", "split", "누수", "leakage", "유출", "테스트 정보", "스케일링"],
        "mechanism": ["fit_transform", "통계", "mean", "std", "전체 데이터", "오염", "scaler"],
        "application": ["fit(X_train)", "transform(X_test)", "pipeline", "교차검증", "분리"]
    },
    "label_imbalance": {
        "core": ["불균형", "imbalance", "accuracy", "편향", "majority", "소수"],
        "mechanism": ["weighted", "클래스 비율", "f1", "recall", "precision", "over", "under"],
        "application": ["class_weight", "stratified", "smote", "f1-score", "resampling"]
    },
    "overfitting": {
        "core": ["과적합", "overfitting", "일반화", "val", "validation", "차이"],
        "mechanism": ["복잡도", "암기", "분산", "noise", "파라미터", "용량"],
        "application": ["dropout", "regularization", "early stopping", "l1", "l2", "augment"]
    },
    "off_by_one": {
        "core": ["off-by-one", "인덱스", "index", "경계", "범위", "boundary"],
        "mechanism": ["0-based", "len(", "len()-1", "boundary", "조건"],
        "application": ["range(", "슬라이싱", "테스트", "확인", "검증"]
    },
    "null_pointer": {
        "core": ["none", "null", "nonetype", "체크", "누락"],
        "mechanism": ["none 반환", "속성", "attributeerror", "접근 실패", "조건"],
        "application": ["is not none", "if", "방어", "처리", "isinstance"]
    },
    "type_mismatch": {
        "core": ["타입", "type", "형변환", "typeerror", "불일치"],
        "mechanism": ["str(", "int(", "float(", "dtype", "암묵적", "혼용"],
        "application": ["isinstance", "명시적", "형변환", "검증", "astype"]
    },
    "metric_selection": {
        "core": ["지표", "metric", "평가", "회귀", "분류", "선택"],
        "mechanism": ["accuracy", "f1", "mse", "mae", "r2", "차이", "태스크"],
        "application": ["태스크", "목적", "비즈니스", "다중", "선택 기준"]
    },
    "feature_leakage": {
        "core": ["피처", "feature", "누수", "leakage", "타겟", "미래"],
        "mechanism": ["파생", "시점", "정보", "포함", "예측 불가"],
        "application": ["의존성", "시간", "pipeline", "검증", "순서"]
    },
    "hyperparameter": {
        "core": ["하이퍼파라미터", "hyperparameter", "학습률", "learning rate", "배치"],
        "mechanism": ["발산", "수렴", "너무 크", "너무 작", "배치 크기", "영향"],
        "application": ["grid search", "scheduler", "validation", "모니터링", "튜닝"]
    },
    "memory_leak": {
        "core": ["메모리", "memory", "누수", "leak", "증가", "해제"],
        "mechanism": ["참조", "generator", "list", "순환", "gc", "accumulate"],
        "application": ["with", "del", "프로파일링", "generator", "yield"]
    },
    "race_condition": {
        "core": ["경쟁", "race", "동기화", "비결정", "thread", "스레드"],
        "mechanism": ["공유", "원자", "atomic", "안전", "순서", "접근"],
        "application": ["lock", "mutex", "동기화", "queue", "스레드 안전"]
    },
    "api_timeout": {
        "core": ["timeout", "타임아웃", "지연", "네트워크", "응답"],
        "mechanism": ["무한 대기", "설정 부재", "에러", "전파", "blocking"],
        "application": ["try", "except", "timeout=", "retry", "재시도"]
    }
}

MAX_SCORES = {"core": 40, "mechanism": 35, "application": 25}


def _score_category(keywords, text, max_score):
    if not keywords:
        return max_score // 2
    matched = sum(1 for kw in keywords if kw.lower() in text)
    ratio = matched / len(keywords)
    if ratio >= 0.5:
        return max_score
    elif ratio >= 0.3:
        return round(max_score * 0.65)
    elif ratio >= 0.15:
        return round(max_score * 0.35)
    return 0


def compute_rule_based_score(sample):
    """explanations 텍스트에서 루브릭 키워드 매칭으로 점수 계산"""
    keywords = RUBRIC_KEYWORDS.get(sample['case_id'], {})
    text = " ".join(filter(None, [
        sample['explanations'].get('1', ''),
        sample['explanations'].get('3', '')
    ])).lower()

    return (
        _score_category(keywords.get('core', []), text, MAX_SCORES['core']) +
        _score_category(keywords.get('mechanism', []), text, MAX_SCORES['mechanism']) +
        _score_category(keywords.get('application', []), text, MAX_SCORES['application'])
    )


class InterviewValidationAnalyzer:

    def __init__(self, evaluation_results_file, samples_file):
        with open(evaluation_results_file, 'r', encoding='utf-8') as f:
            self.eval_data = json.load(f)
        with open(samples_file, 'r', encoding='utf-8') as f:
            samples = json.load(f)

        # 규칙 기반 점수를 직접 계산 (파일 저장 없이)
        self.rule_scores = {s['sample_id']: compute_rule_based_score(s) for s in samples}

        print(f"데이터 로드 완료")
        print(f"  평가 결과: {len(self.eval_data['results'])}개 샘플")

    def _get_valid_scores(self, trials):
        return [t['thinking_score'] for t in trials if 'error' not in t]

    def analyze_consistency(self):
        """검증 1: 평가 일관성 - 표준편차"""
        print("\n" + "="*60)
        print("검증 1: 평가 일관성 (Consistency)")
        print("="*60)

        std_devs = []
        details = []

        for s in self.eval_data['results']:
            scores = self._get_valid_scores(s['trials'])
            if len(scores) < 2:
                continue
            sd = np.std(scores, ddof=1)
            std_devs.append(sd)
            details.append({'sample_id': s['sample_id'], 'quality': s['quality_level'],
                            'mean': np.mean(scores), 'std_dev': sd, 'scores': scores})

        avg_sd = np.mean(std_devs)
        max_sd = np.max(std_devs)

        print(f"\n결과:")
        print(f"  평균 표준편차: {avg_sd:.2f}점 (목표 ≤5점)  {'통과' if avg_sd <= 5 else '미달'}")
        print(f"  최대 표준편차: {max_sd:.2f}점 (목표 ≤10점) {'통과' if max_sd <= 10 else '미달'}")

        print(f"\n품질별 일관성:")
        for quality in ['excellent', 'good', 'average', 'poor', 'very_poor']:
            q_sds = [d['std_dev'] for d in details if d['quality'] == quality]
            if q_sds:
                print(f"  {quality:12s}: 평균 σ = {np.mean(q_sds):.2f}점")

        return {'avg_std_dev': avg_sd, 'max_std_dev': max_sd,
                'passed': avg_sd <= 5, 'details': details}

    def analyze_discrimination(self):
        """검증 2: 극단 케이스 구분력"""
        print("\n" + "="*60)
        print("검증 2: 극단 케이스 구분력 (Discrimination)")
        print("="*60)

        quality_avgs = {}
        for s in self.eval_data['results']:
            scores = self._get_valid_scores(s['trials'])
            if scores:
                quality_avgs[s['sample_id']] = {'score': np.mean(scores), 'quality': s['quality_level']}

        excellent = [v['score'] for v in quality_avgs.values() if v['quality'] == 'excellent']
        very_poor = [v['score'] for v in quality_avgs.values() if v['quality'] == 'very_poor']

        exc_mean = np.mean(excellent) if excellent else 0
        vp_mean = np.mean(very_poor) if very_poor else 0
        diff = exc_mean - vp_mean

        print(f"\n결과:")
        print(f"  excellent 평균: {exc_mean:.1f}점 (n={len(excellent)})")
        print(f"  very_poor 평균: {vp_mean:.1f}점 (n={len(very_poor)})")
        print(f"  점수 차이: {diff:.1f}점 (목표 ≥30점)  {'통과' if diff >= 30 else '미달'}")

        print(f"\n품질별 평균:")
        for quality in ['excellent', 'good', 'average', 'poor', 'very_poor']:
            qs = [v['score'] for v in quality_avgs.values() if v['quality'] == quality]
            if qs:
                print(f"  {quality:12s}: {np.mean(qs):.1f}±{np.std(qs):.1f}점")

        return {'excellent_mean': exc_mean, 'very_poor_mean': vp_mean,
                'score_diff': diff, 'passed': diff >= 30}

    def analyze_ranking(self):
        """검증 3: 순위 정확도 - Kendall's Tau"""
        print("\n" + "="*60)
        print("검증 3: 순위 정확도 (Ranking)")
        print("="*60)

        quality_rank = {'excellent': 5, 'good': 4, 'average': 3, 'poor': 2, 'very_poor': 1}

        cases = defaultdict(list)
        for s in self.eval_data['results']:
            scores = self._get_valid_scores(s['trials'])
            if scores:
                cases[s['case_id']].append({'quality': s['quality_level'], 'score': np.mean(scores)})

        taus = []
        perfect = 0
        total = 0

        print(f"\n케이스별 순위:")
        for case_id, samples in cases.items():
            if len(samples) < 5:
                continue
            total += 1
            samples.sort(key=lambda x: x['score'], reverse=True)
            expected = [quality_rank[s['quality']] for s in samples]
            actual = list(range(len(samples), 0, -1))
            tau, _ = stats.kendalltau(expected, actual)
            taus.append(tau)

            expected_order = ['excellent', 'good', 'average', 'poor', 'very_poor']
            actual_order = [s['quality'] for s in samples]
            is_perfect = expected_order == actual_order
            if is_perfect:
                perfect += 1

            mark = "O" if is_perfect else "X"
            print(f"  {case_id:20s} [{mark}] τ={tau:.3f} | {[s['quality'][:4] for s in samples]}")

        avg_tau = np.mean(taus) if taus else 0
        print(f"\n결과:")
        print(f"  평균 Kendall's Tau: {avg_tau:.3f} (목표 ≥0.75)  {'통과' if avg_tau >= 0.75 else '미달'}")
        if total:
            print(f"  완벽한 순위: {perfect}/{total} ({perfect/total*100:.1f}%)")

        return {'avg_kendall_tau': avg_tau, 'perfect_rankings': perfect,
                'total_cases': total, 'passed': avg_tau >= 0.75}

    def analyze_convergent_validity(self):
        """검증 4: 수렴 타당도 - Pearson r"""
        print("\n" + "="*60)
        print("검증 4: 수렴 타당도 (Convergent Validity)")
        print("="*60)

        rule_list, llm_list = [], []

        for s in self.eval_data['results']:
            if s['sample_id'] not in self.rule_scores:
                continue
            scores = self._get_valid_scores(s['trials'])
            if not scores:
                continue
            rule_list.append(self.rule_scores[s['sample_id']])
            llm_list.append(np.mean(scores))

        r, p = stats.pearsonr(rule_list, llm_list)

        print(f"\n결과:")
        print(f"  Pearson r = {r:.3f} (목표 ≥0.65)  {'통과' if r >= 0.65 else '미달'}")
        print(f"  p-value = {p:.4f}")

        return {'pearson_r': r, 'p_value': p, 'passed': r >= 0.65}

    def run(self):
        results = {
            'consistency': self.analyze_consistency(),
            'discrimination': self.analyze_discrimination(),
            'ranking': self.analyze_ranking(),
            'convergent_validity': self.analyze_convergent_validity()
        }

        all_passed = all(v['passed'] for v in results.values())
        print("\n" + "="*60)
        print("종합 검증 결과")
        print("="*60)
        print(f"  일관성:      {'통과' if results['consistency']['passed'] else '미달'} "
              f"(σ={results['consistency']['avg_std_dev']:.2f})")
        print(f"  구분력:      {'통과' if results['discrimination']['passed'] else '미달'} "
              f"(차이={results['discrimination']['score_diff']:.1f}점)")
        print(f"  순위 정확도: {'통과' if results['ranking']['passed'] else '미달'} "
              f"(τ={results['ranking']['avg_kendall_tau']:.3f})")
        print(f"  수렴 타당도: {'통과' if results['convergent_validity']['passed'] else '미달'} "
              f"(r={results['convergent_validity']['pearson_r']:.3f})")
        print(f"\n최종: {'전체 통과' if all_passed else '일부 미달'}")

        results['all_passed'] = all_passed

        output = Path(__file__).parent / 'data' / 'analysis_results.json'
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n분석 결과 저장: {output}")

        return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true')
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    result_file = 'quick_evaluation_results.json' if args.quick else 'evaluation_results.json'
    analyzer = InterviewValidationAnalyzer(
        evaluation_results_file=base / 'data' / result_file,
        samples_file=base / 'data' / 'new_validation_samples.json'
    )
    analyzer.run()
