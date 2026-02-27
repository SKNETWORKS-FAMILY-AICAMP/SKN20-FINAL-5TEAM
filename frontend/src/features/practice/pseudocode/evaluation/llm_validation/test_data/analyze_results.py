"""
의사코드 트랙 LLM 신뢰성 검증 - 결과 분석

4가지 검증:
1. 평가 일관성 (Consistency)         - 동일 샘플 반복 평가 표준편차
2. 극단 케이스 구분력 (Discrimination) - excellent vs very_poor 점수 차이
3. 순위 정확도 (Ranking)              - Kendall's Tau (Quest별)
4. 수렴 타당도 (Convergent Validity)  - 규칙 기반 점수와 Pearson r
"""
import json
import numpy as np
from scipy import stats
from pathlib import Path
from collections import defaultdict

# ── Quest별 루브릭 키워드 (rule-based 교차검증용) ───────────────────────────────
# 각 차원별 키워드 매칭으로 규칙 기반 점수를 계산
# LLM 점수와 비교하여 수렴 타당도 검증
QUEST_RUBRIC_KEYWORDS = {
    '1': {  # 데이터 전처리 누수 방어
        'design':         ['train_test_split', '분리', '격리', 'data leakage', '누수', 'split'],
        'consistency':    ['fit_transform', 'transform', 'fit(x_train', '기준점', 'scaler', '오염'],
        'abstraction':    ['pipeline', '모듈', '클래스', '재사용', '캡슐화', '함수'],
        'edgeCase':       ['결측', '이상치', '예외', 'null', 'nan', '방어'],
        'implementation': ['standardscaler', 'minmaxscaler', 'x_train', 'x_test', 'sklearn'],
    },
    '2': {  # 과적합 방어 정규화
        'design':         ['ridge', 'lasso', '정규화', 'regularization', 'overfitting', '과적합'],
        'consistency':    ['l1', 'l2', 'alpha', 'lambda', '계수', '가중치'],
        'abstraction':    ['교차검증', 'cross.validation', 'k-fold', '모델 선택', '파이프라인'],
        'edgeCase':       ['조기종료', 'early stopping', '검증 손실', 'val_loss', '모니터링'],
        'implementation': ['ridge(', 'lasso(', 'alpha=', 'fit(', 'score(', 'sklearn'],
    },
    '3': {  # 불균형 데이터 처리
        'design':         ['불균형', 'imbalance', '클래스', 'class', 'smote', '오버샘플링'],
        'consistency':    ['f1', 'auc', 'recall', 'precision', '평가지표', 'metric'],
        'abstraction':    ['stratified', 'class_weight', '가중치', '균형', '분포'],
        'edgeCase':       ['소수 클래스', 'minority', '극단', '비율', '임계값'],
        'implementation': ['smote(', 'f1_score', 'roc_auc', 'class_weight=', 'stratifiedkfold'],
    },
    '4': {  # 피처 엔지니어링
        'design':         ['pca', '차원축소', 'feature', '피처', '선택', '변환'],
        'consistency':    ['상관관계', 'correlation', '중요도', 'importance', '다중공선성'],
        'abstraction':    ['결측치', 'missing', '이상치', 'outlier', '전처리', 'preprocessing'],
        'edgeCase':       ['차원의 저주', '과적합', '스케일', '분산', 'variance'],
        'implementation': ['pca(', 'selectkbest', 'feature_importances_', 'fillna', 'dropna'],
    },
    '5': {  # 하이퍼파라미터 튜닝
        'design':         ['하이퍼파라미터', 'hyperparameter', '학습률', 'learning rate', '탐색'],
        'consistency':    ['교차검증', 'cross.validation', 'k-fold', '검증 셋', 'validation'],
        'abstraction':    ['gridsearch', 'randomsearch', 'bayesian', '자동화', '탐색 공간'],
        'edgeCase':       ['과적합', '수렴', '발산', '조기종료', '배치 크기'],
        'implementation': ['gridsearchcv', 'randomizedsearchcv', 'param_grid', 'cv=', 'best_params_'],
    },
    '6': {  # 모델 해석성
        'design':         ['shap', 'lime', '설명가능', 'xai', '해석', 'interpretability'],
        'consistency':    ['특성 중요도', 'feature importance', '기여도', '영향', '설명'],
        'abstraction':    ['편향', 'bias', '공정성', 'fairness', '규제', '투명성'],
        'edgeCase':       ['블랙박스', 'black box', '지역', '전역', '반사실적', 'counterfactual'],
        'implementation': ['shap.explainer', 'shap_values', 'lime.', 'feature_importances_', 'eli5'],
    },
}

DIM_WEIGHTS = {'design': 25, 'consistency': 20, 'abstraction': 15, 'edgeCase': 15, 'implementation': 10}


def compute_rule_based_score(sample: dict) -> int:
    """의사코드 텍스트에서 Quest별 키워드 매칭으로 규칙 기반 점수 계산 (0-100)"""
    keywords_by_dim = QUEST_RUBRIC_KEYWORDS.get(sample['quest_id'], {})
    text = sample['pseudocode'].lower()

    total_score = 0.0
    total_weight = sum(DIM_WEIGHTS.values())  # 85

    for dim, weight in DIM_WEIGHTS.items():
        kws = keywords_by_dim.get(dim, [])
        if not kws:
            total_score += weight * 0.5  # 키워드 없으면 중간값
            continue
        matched = sum(1 for kw in kws if kw.lower() in text)
        ratio = matched / len(kws)
        if ratio >= 0.4:
            dim_score = weight
        elif ratio >= 0.2:
            dim_score = weight * 0.6
        elif ratio >= 0.1:
            dim_score = weight * 0.3
        else:
            dim_score = 0.0
        total_score += dim_score

    # 0-85 스케일 → 0-100으로 변환
    return int(round(total_score / total_weight * 100))


class PseudocodeValidationAnalyzer:

    def __init__(self, evaluation_results_file: Path, samples_file: Path):
        with open(evaluation_results_file, 'r', encoding='utf-8') as f:
            self.eval_data = json.load(f)
        with open(samples_file, 'r', encoding='utf-8') as f:
            samples = json.load(f)

        self.rule_scores = {s['sample_id']: compute_rule_based_score(s) for s in samples}
        self.samples_by_id = {s['sample_id']: s for s in samples}

        print(f"데이터 로드 완료")
        print(f"  평가 결과: {len(self.eval_data['results'])}개 샘플")
        print(f"  규칙 점수 범위: {min(self.rule_scores.values())} ~ {max(self.rule_scores.values())}")

    def _valid_scores(self, trials: list) -> list:
        return [t['overall_score'] for t in trials if 'error' not in t and 'overall_score' in t]

    # ── 검증 1: 일관성 ─────────────────────────────────────────────────────────
    def analyze_consistency(self) -> dict:
        print("\n" + "="*60)
        print("검증 1: 평가 일관성 (Consistency)")
        print("="*60)

        std_devs = []
        details = []

        for s in self.eval_data['results']:
            scores = self._valid_scores(s['trials'])
            if len(scores) < 2:
                continue
            sd = np.std(scores, ddof=1)
            std_devs.append(sd)
            details.append({
                'sample_id': s['sample_id'],
                'quality': s['quality_level'],
                'mean': round(float(np.mean(scores)), 2),
                'std_dev': round(float(sd), 2),
                'scores': scores,
            })

        avg_sd = float(np.mean(std_devs))
        max_sd = float(np.max(std_devs))

        print(f"\n결과:")
        print(f"  평균 표준편차: {avg_sd:.2f}점 (목표 ≤5점)  {'통과' if avg_sd <= 5 else '미달'}")
        print(f"  최대 표준편차: {max_sd:.2f}점 (목표 ≤10점) {'통과' if max_sd <= 10 else '미달'}")

        print(f"\n품질별 일관성:")
        for q in ['excellent', 'good', 'average', 'poor', 'very_poor']:
            q_sds = [d['std_dev'] for d in details if d['quality'] == q]
            if q_sds:
                print(f"  {q:12s}: 평균 σ = {np.mean(q_sds):.2f}점 (n={len(q_sds)})")

        return {
            'avg_std_dev': round(avg_sd, 3),
            'max_std_dev': round(max_sd, 3),
            'passed': avg_sd <= 5,
            'details': details,
        }

    # ── 검증 2: 극단 구분력 ────────────────────────────────────────────────────
    def analyze_discrimination(self) -> dict:
        print("\n" + "="*60)
        print("검증 2: 극단 케이스 구분력 (Discrimination)")
        print("="*60)

        quality_avgs = {}
        for s in self.eval_data['results']:
            scores = self._valid_scores(s['trials'])
            if scores:
                quality_avgs[s['sample_id']] = {
                    'score': float(np.mean(scores)),
                    'quality': s['quality_level'],
                }

        excellent = [v['score'] for v in quality_avgs.values() if v['quality'] == 'excellent']
        very_poor = [v['score'] for v in quality_avgs.values() if v['quality'] == 'very_poor']

        exc_mean = float(np.mean(excellent)) if excellent else 0
        vp_mean = float(np.mean(very_poor)) if very_poor else 0
        diff = exc_mean - vp_mean

        print(f"\n결과:")
        print(f"  excellent 평균: {exc_mean:.1f}점 (n={len(excellent)})")
        print(f"  very_poor 평균: {vp_mean:.1f}점 (n={len(very_poor)})")
        print(f"  점수 차이: {diff:.1f}점 (목표 ≥30점)  {'통과' if diff >= 30 else '미달'}")

        print(f"\n품질별 평균:")
        for q in ['excellent', 'good', 'average', 'poor', 'very_poor']:
            qs = [v['score'] for v in quality_avgs.values() if v['quality'] == q]
            if qs:
                print(f"  {q:12s}: {np.mean(qs):.1f}±{np.std(qs):.1f}점")

        return {
            'excellent_mean': round(exc_mean, 2),
            'very_poor_mean': round(vp_mean, 2),
            'score_diff': round(diff, 2),
            'passed': diff >= 30,
        }

    # ── 검증 3: 순위 정확도 ────────────────────────────────────────────────────
    def analyze_ranking(self) -> dict:
        print("\n" + "="*60)
        print("검증 3: 순위 정확도 (Ranking) - Kendall's Tau")
        print("="*60)

        quality_rank = {'excellent': 5, 'good': 4, 'average': 3, 'poor': 2, 'very_poor': 1}

        # Quest별로 그룹핑
        quests = defaultdict(list)
        for s in self.eval_data['results']:
            scores = self._valid_scores(s['trials'])
            if scores:
                quests[s['quest_id']].append({
                    'quality': s['quality_level'],
                    'score': float(np.mean(scores)),
                })

        taus = []
        perfect = 0
        total = 0

        print(f"\nQuest별 순위:")
        for quest_id in sorted(quests.keys()):
            samples = quests[quest_id]
            if len(samples) < 5:
                continue
            total += 1
            samples.sort(key=lambda x: x['score'], reverse=True)
            expected = [quality_rank[s['quality']] for s in samples]
            actual = list(range(len(samples), 0, -1))
            tau, _ = stats.kendalltau(expected, actual)
            taus.append(float(tau))

            expected_order = ['excellent', 'good', 'average', 'poor', 'very_poor']
            actual_order = [s['quality'] for s in samples]
            is_perfect = expected_order == actual_order
            if is_perfect:
                perfect += 1

            mark = "O" if is_perfect else "X"
            title = self.samples_by_id.get(f"quest{quest_id}_excellent", {}).get('quest_title', f'Quest {quest_id}')
            print(f"  Quest {quest_id} [{mark}] τ={tau:.3f} | {[s['quality'][:4] for s in samples]}")
            print(f"    → {title[:35]}")

        avg_tau = float(np.mean(taus)) if taus else 0
        print(f"\n결과:")
        print(f"  평균 Kendall's Tau: {avg_tau:.3f} (목표 ≥0.75)  {'통과' if avg_tau >= 0.75 else '미달'}")
        if total:
            print(f"  완벽한 순위: {perfect}/{total} ({perfect/total*100:.1f}%)")

        return {
            'avg_kendall_tau': round(avg_tau, 4),
            'perfect_rankings': perfect,
            'total_quests': total,
            'passed': avg_tau >= 0.75,
        }

    # ── 검증 4: 수렴 타당도 ────────────────────────────────────────────────────
    def analyze_convergent_validity(self) -> dict:
        print("\n" + "="*60)
        print("검증 4: 수렴 타당도 (Convergent Validity) - Pearson r")
        print("="*60)

        rule_list, llm_list = [], []

        for s in self.eval_data['results']:
            if s['sample_id'] not in self.rule_scores:
                continue
            scores = self._valid_scores(s['trials'])
            if not scores:
                continue
            rule_list.append(self.rule_scores[s['sample_id']])
            llm_list.append(float(np.mean(scores)))

        r, p = stats.pearsonr(rule_list, llm_list)
        r, p = float(r), float(p)

        print(f"\n결과:")
        print(f"  Pearson r = {r:.3f} (목표 ≥0.65)  {'통과' if r >= 0.65 else '미달'}")
        print(f"  p-value = {p:.4f}")
        print(f"  샘플 수: {len(rule_list)}")

        # Quest별 상관관계
        print(f"\nQuest별 수렴 타당도:")
        quests_r = defaultdict(lambda: {'rule': [], 'llm': []})
        for s in self.eval_data['results']:
            scores = self._valid_scores(s['trials'])
            if scores and s['sample_id'] in self.rule_scores:
                quests_r[s['quest_id']]['rule'].append(self.rule_scores[s['sample_id']])
                quests_r[s['quest_id']]['llm'].append(float(np.mean(scores)))
        for qid in sorted(quests_r.keys()):
            rlist = quests_r[qid]['rule']
            llist = quests_r[qid]['llm']
            if len(rlist) >= 3:
                qr, _ = stats.pearsonr(rlist, llist)
                print(f"  Quest {qid}: r={float(qr):.3f}")

        return {
            'pearson_r': round(r, 4),
            'p_value': round(p, 6),
            'n_samples': len(rule_list),
            'passed': r >= 0.65,
        }

    # ── 종합 실행 ──────────────────────────────────────────────────────────────
    def run(self) -> dict:
        results = {
            'consistency': self.analyze_consistency(),
            'discrimination': self.analyze_discrimination(),
            'ranking': self.analyze_ranking(),
            'convergent_validity': self.analyze_convergent_validity(),
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

        out = Path(__file__).parent / 'data' / 'analysis_results.json'
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n분석 결과 저장: {out}")

        return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true')
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    result_file = 'quick_evaluation_results.json' if args.quick else 'evaluation_results.json'
    samples_file = 'validation_samples_quick.json' if args.quick else 'validation_samples.json'
    # quick 모드일 때 전체 샘플 파일이 없으면 폴백
    sp = base / 'data' / samples_file
    if not sp.exists():
        sp = base / 'data' / 'validation_samples.json'

    analyzer = PseudocodeValidationAnalyzer(
        evaluation_results_file=base / 'data' / result_file,
        samples_file=sp,
    )
    analyzer.run()
