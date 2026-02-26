"""
시스템 아키텍처 트랙 LLM 신뢰성 검증 - 결과 분석

4가지 검증:
1. 평가 일관성 (Consistency)         - 동일 샘플 반복 평가 표준편차
2. 극단 케이스 구분력 (Discrimination) - excellent vs very_poor 점수 차이
3. 순위 정확도 (Ranking)              - Kendall's Tau (문제별)
4. 수렴 타당도 (Convergent Validity)  - 필수 컴포넌트 매칭 점수와 Pearson r
"""
import json
import numpy as np
from scipy import stats
from pathlib import Path
from collections import defaultdict

# ── 문제별 필수 컴포넌트 키워드 (rule-based 교차검증용) ────────────────────────
# validation_samples.json의 _required_components + 유사 표현 포함
PROBLEM_REQUIRED_KEYWORDS = {
    'jr_001_url_shortener': {
        'core_components': ['web server', 'rdbms', 'database', 'cache', 'redis'],
        'core_flows': ['캐시', 'cache', 'read-through', '미스', '조회', '리다이렉션'],
        'performance': ['tps', '100ms', '1000건', '성능', '응답 속도', '부하'],
    },
    'jr_002_pastebin': {
        'core_components': ['web server', 'object storage', 's3', 'rdbms', 'worker', 'cleanup'],
        'core_flows': ['분리', '본문', '메타데이터', '만료', '삭제', '스토리지'],
        'performance': ['10mb', '7일', '비용', 'ttl', '만료'],
    },
    'jr_003_notification': {
        'core_components': ['web server', 'message queue', 'kafka', 'rabbitmq', 'worker', 'notification'],
        'core_flows': ['큐', 'queue', '비동기', 'async', '재시도', '발송', '소비'],
        'performance': ['10000', '스파이크', 'spike', '완충', '결합도'],
    },
    'jr_004_image_feed': {
        'core_components': ['object storage', 'cdn', 'web server', 'database', 's3'],
        'core_flows': ['cdn', '캐시', 'edge', '엣지', '원본', '대역폭'],
        'performance': ['500ms', '전 세계', '글로벌', '대역폭', '비용'],
    },
}

KEYWORD_WEIGHTS = {'core_components': 50, 'core_flows': 30, 'performance': 20}


def compute_rule_based_score(sample: dict) -> int:
    """필수 컴포넌트 및 핵심 흐름 키워드 매칭으로 규칙 기반 점수 계산 (0-100)"""
    problem_id = sample['problem_id']
    keywords = PROBLEM_REQUIRED_KEYWORDS.get(problem_id, {})

    # 검색 대상 텍스트: architectureContext + userExplanation + QnA 답변
    text_parts = [
        sample.get('architecture_context', ''),
        sample.get('user_explanation', ''),
    ]
    for qa in sample.get('deep_dive_qna', []):
        text_parts.append(qa.get('answer', ''))
    text = ' '.join(text_parts).lower()

    total_score = 0.0
    for category, weight in KEYWORD_WEIGHTS.items():
        kws = keywords.get(category, [])
        if not kws:
            total_score += weight * 0.5
            continue
        matched = sum(1 for kw in kws if kw.lower() in text)
        ratio = matched / len(kws)
        if ratio >= 0.5:
            total_score += weight
        elif ratio >= 0.3:
            total_score += weight * 0.65
        elif ratio >= 0.15:
            total_score += weight * 0.35
        else:
            total_score += 0.0

    return int(round(total_score))


class ArchitectureValidationAnalyzer:

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

        # 축별 구분력 분석
        print(f"\n축별 구분력 (excellent vs very_poor 평균 차이):")
        axis_diffs = defaultdict(lambda: {'excellent': [], 'very_poor': []})
        for s in self.eval_data['results']:
            valid_trials = [t for t in s['trials'] if 'error' not in t and 'axis_scores' in t]
            if not valid_trials:
                continue
            q = s['quality_level']
            if q not in ('excellent', 'very_poor'):
                continue
            for t in valid_trials:
                for axis, data in t['axis_scores'].items():
                    axis_diffs[axis][q].append(data['score'])
        for axis in sorted(axis_diffs.keys()):
            exc = axis_diffs[axis]['excellent']
            vp = axis_diffs[axis]['very_poor']
            if exc and vp:
                d = np.mean(exc) - np.mean(vp)
                print(f"  {axis:30s}: {d:.1f}점 차이")

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

        # 문제별로 그룹핑
        problems = defaultdict(list)
        for s in self.eval_data['results']:
            scores = self._valid_scores(s['trials'])
            if scores:
                problems[s['problem_id']].append({
                    'quality': s['quality_level'],
                    'score': float(np.mean(scores)),
                })

        taus = []
        perfect = 0
        total = 0

        print(f"\n문제별 순위:")
        for problem_id in sorted(problems.keys()):
            samples = problems[problem_id]
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
            print(f"  {problem_id:30s} [{mark}] τ={tau:.3f} | {[s['quality'][:4] for s in samples]}")

        avg_tau = float(np.mean(taus)) if taus else 0
        print(f"\n결과:")
        print(f"  평균 Kendall's Tau: {avg_tau:.3f} (목표 ≥0.75)  {'통과' if avg_tau >= 0.75 else '미달'}")
        if total:
            print(f"  완벽한 순위: {perfect}/{total} ({perfect/total*100:.1f}%)")

        return {
            'avg_kendall_tau': round(avg_tau, 4),
            'perfect_rankings': perfect,
            'total_problems': total,
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

        # 문제별 상관관계
        print(f"\n문제별 수렴 타당도:")
        problems_r = defaultdict(lambda: {'rule': [], 'llm': []})
        for s in self.eval_data['results']:
            scores = self._valid_scores(s['trials'])
            if scores and s['sample_id'] in self.rule_scores:
                problems_r[s['problem_id']]['rule'].append(self.rule_scores[s['sample_id']])
                problems_r[s['problem_id']]['llm'].append(float(np.mean(scores)))
        for pid in sorted(problems_r.keys()):
            rlist = problems_r[pid]['rule']
            llist = problems_r[pid]['llm']
            if len(rlist) >= 3:
                pr, _ = stats.pearsonr(rlist, llist)
                print(f"  {pid}: r={float(pr):.3f}")

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
    sp = base / 'data' / samples_file
    if not sp.exists():
        sp = base / 'data' / 'validation_samples.json'

    analyzer = ArchitectureValidationAnalyzer(
        evaluation_results_file=base / 'data' / result_file,
        samples_file=sp,
    )
    analyzer.run()
