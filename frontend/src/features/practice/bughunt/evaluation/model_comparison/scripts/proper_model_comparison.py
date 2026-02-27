import json
import statistics
import math

# Kendall's Tau 수동 구현
def kendalltau(x, y):
    n = len(x)
    concordant = 0
    discordant = 0

    for i in range(n):
        for j in range(i+1, n):
            if (x[i] - x[j]) * (y[i] - y[j]) > 0:
                concordant += 1
            elif (x[i] - x[j]) * (y[i] - y[j]) < 0:
                discordant += 1

    tau = (concordant - discordant) / (0.5 * n * (n - 1)) if n > 1 else 0
    return tau, 0  # p_value는 생략

models = ['gpt-4o-mini', 'gpt-5-mini', 'gpt-5', 'gpt-5.2', 'gemini-2.5-flash', 'gemini-2.5-pro']
base_path = '/app/evaluation/data/validation/model_comparison'

# 품질 레벨 순서 (정답)
quality_order = {'excellent': 5, 'good': 4, 'average': 3, 'poor': 2, 'very_poor': 1}

print("=" * 120)
print("🎯 모델 평가 성능 비교 (진짜 중요한 지표)")
print("=" * 120)
print()

results_summary = {}

for model in models:
    print(f"\n{'='*120}")
    print(f"📊 모델: {model}")
    print(f"{'='*120}")

    with open(f'{base_path}/{model}_results.json', 'r') as f:
        data = json.load(f)

    all_results = data['results']
    stats = data['stats']

    # 품질 레벨별 점수 수집
    quality_scores = {
        'excellent': [],
        'good': [],
        'average': [],
        'poor': [],
        'very_poor': []
    }

    # 일관성 계산을 위한 샘플별 점수 수집
    sample_score_variances = []

    # 순위 정확도 계산용
    sample_quality_order = []
    sample_avg_scores = []

    for sample in all_results:
        quality = sample['quality_level']
        scores = []

        for trial in sample['trials']:
            if not trial.get('error', False):
                score = trial.get('thinking_score', 0)
                quality_scores[quality].append(score)
                scores.append(score)

        # 일관성 (표준편차)
        if len(scores) >= 2:
            sample_score_variances.append(statistics.variance(scores))

        # 순위 정확도용 데이터
        if scores:
            sample_quality_order.append(quality_order[quality])
            sample_avg_scores.append(sum(scores) / len(scores))

    # 1. 일관성 (Consistency) - 낮을수록 좋음
    avg_consistency = statistics.mean([math.sqrt(v) for v in sample_score_variances]) if sample_score_variances else 0

    # 2. 구분력 (Discrimination) - 높을수록 좋음
    excellent_avg = statistics.mean(quality_scores['excellent']) if quality_scores['excellent'] else 0
    very_poor_avg = statistics.mean(quality_scores['very_poor']) if quality_scores['very_poor'] else 0
    discrimination = excellent_avg - very_poor_avg

    # 3. 순위 정확도 (Ranking Accuracy) - Kendall's Tau
    if len(sample_quality_order) > 0:
        tau, p_value = kendalltau(sample_quality_order, sample_avg_scores)
    else:
        tau = 0

    # 4. 속도 (Speed)
    avg_speed = stats['avg_time']

    # 5. 비용 (Cost)
    total_cost = stats['total_cost']

    # 6. 신뢰성 (Reliability)
    total_trials = stats['total_evaluations']
    # 실패한 trial 계산
    error_count = 0
    for sample in all_results:
        for trial in sample['trials']:
            if trial.get('error', False):
                error_count += 1

    reliability = ((total_trials - error_count) / (total_trials + error_count) * 100) if (total_trials + error_count) > 0 else 0

    # 품질 레벨별 평균 점수
    print(f"\n📈 품질 레벨별 평균 점수:")
    print("-" * 120)
    for quality in ['excellent', 'good', 'average', 'poor', 'very_poor']:
        if quality_scores[quality]:
            avg = statistics.mean(quality_scores[quality])
            std = statistics.stdev(quality_scores[quality]) if len(quality_scores[quality]) > 1 else 0
            count = len(quality_scores[quality])
            print(f"   {quality:15s}: {avg:6.1f}점 (±{std:4.1f}, n={count})")
        else:
            print(f"   {quality:15s}: 데이터 없음")

    print(f"\n1️⃣  일관성 (Consistency) - 낮을수록 좋음")
    print("-" * 120)
    print(f"   표준편차 평균: {avg_consistency:.2f}점")
    if avg_consistency <= 5:
        print(f"   ✅ 목표 달성 (≤5점)")
    elif avg_consistency <= 10:
        print(f"   ⚠️  개선 필요 (5-10점)")
    else:
        print(f"   ❌ 불안정 (>10점)")

    print(f"\n2️⃣  구분력 (Discrimination) - 높을수록 좋음")
    print("-" * 120)
    print(f"   Excellent 평균: {excellent_avg:.1f}점")
    print(f"   Very Poor 평균: {very_poor_avg:.1f}점")
    print(f"   구분력: {discrimination:.1f}점")
    if discrimination >= 30:
        print(f"   ✅ 목표 달성 (≥30점) - 우수/미흡을 잘 구분함")
    elif discrimination >= 20:
        print(f"   ⚠️  보통 (20-30점)")
    else:
        print(f"   ❌ 낮음 (<20점) - 품질 구분 능력 부족")

    print(f"\n3️⃣  순위 정확도 (Ranking Accuracy) - 높을수록 좋음")
    print("-" * 120)
    print(f"   Kendall's Tau: {tau:.3f}")
    if tau >= 0.8:
        print(f"   ✅ 목표 달성 (≥0.8) - 품질 순서를 매우 정확히 평가")
    elif tau >= 0.6:
        print(f"   ⚠️  보통 (0.6-0.8)")
    else:
        print(f"   ❌ 낮음 (<0.6) - 품질 순서 평가 부정확")

    print(f"\n4️⃣  속도 (Speed)")
    print("-" * 120)
    print(f"   평균 응답 시간: {avg_speed:.1f}초")

    print(f"\n5️⃣  비용 (Cost)")
    print("-" * 120)
    print(f"   총 비용: ${total_cost:.2f}")

    print(f"\n6️⃣  신뢰성 (Reliability)")
    print("-" * 120)
    print(f"   성공률: {reliability:.1f}%")
    print(f"   오류: {error_count}개")
    if reliability >= 95:
        print(f"   ✅ 목표 달성 (≥95%)")
    elif reliability >= 90:
        print(f"   ⚠️  개선 필요 (90-95%)")
    else:
        print(f"   ❌ 불안정 (<90%)")

    # 결과 저장
    results_summary[model] = {
        'consistency': avg_consistency,
        'discrimination': discrimination,
        'ranking_tau': tau,
        'speed': avg_speed,
        'cost': total_cost,
        'reliability': reliability,
        'excellent_avg': excellent_avg,
        'very_poor_avg': very_poor_avg
    }

print("\n" + "=" * 120)
print("🏆 종합 비교")
print("=" * 120)

# 정규화 함수 (0-100 스케일)
def normalize(value, min_val, max_val, reverse=False):
    if max_val == min_val:
        return 50
    normalized = (value - min_val) / (max_val - min_val) * 100
    return 100 - normalized if reverse else normalized

# 각 지표의 min/max 계산
consistency_vals = [r['consistency'] for r in results_summary.values()]
discrimination_vals = [r['discrimination'] for r in results_summary.values()]
ranking_vals = [r['ranking_tau'] for r in results_summary.values()]
speed_vals = [r['speed'] for r in results_summary.values()]
cost_vals = [r['cost'] for r in results_summary.values()]
reliability_vals = [r['reliability'] for r in results_summary.values()]

# 종합 점수 계산 (가중치 적용)
weights = {
    'consistency': 2.0,
    'discrimination': 2.0,
    'ranking': 1.5,
    'speed': 1.0,
    'cost': 1.5,
    'reliability': 2.0
}

total_weight = sum(weights.values())

for model, results in results_summary.items():
    # 정규화 (일관성, 속도, 비용은 낮을수록 좋음 - reverse=True)
    norm_consistency = normalize(results['consistency'], min(consistency_vals), max(consistency_vals), reverse=True)
    norm_discrimination = normalize(results['discrimination'], min(discrimination_vals), max(discrimination_vals))
    norm_ranking = normalize(results['ranking_tau'], min(ranking_vals), max(ranking_vals))
    norm_speed = normalize(results['speed'], min(speed_vals), max(speed_vals), reverse=True)
    norm_cost = normalize(results['cost'], min(cost_vals), max(cost_vals), reverse=True)
    norm_reliability = normalize(results['reliability'], min(reliability_vals), max(reliability_vals))

    # 가중 평균
    overall_score = (
        norm_consistency * weights['consistency'] +
        norm_discrimination * weights['discrimination'] +
        norm_ranking * weights['ranking'] +
        norm_speed * weights['speed'] +
        norm_cost * weights['cost'] +
        norm_reliability * weights['reliability']
    ) / total_weight

    results_summary[model]['overall_score'] = overall_score

# 정렬 및 출력
print(f"\n{'모델':<25} {'일관성':<10} {'구분력':<10} {'순위':<10} {'속도':<10} {'비용':<10} {'신뢰성':<10} {'종합점수':<10}")
print("-" * 120)

sorted_models = sorted(models, key=lambda m: results_summary[m]['overall_score'], reverse=True)

for model in sorted_models:
    r = results_summary[model]
    print(f"{model:<25} {r['consistency']:>6.1f}점   {r['discrimination']:>6.1f}점   {r['ranking_tau']:>6.3f}    {r['speed']:>6.1f}초   ${r['cost']:>6.2f}   {r['reliability']:>6.1f}%   {r['overall_score']:>6.1f}")

print("\n" + "=" * 120)
print("📌 최종 결론")
print("=" * 120)

best_model = sorted_models[0]
best_discrimination = max(models, key=lambda m: results_summary[m]['discrimination'])
best_ranking = max(models, key=lambda m: results_summary[m]['ranking_tau'])
best_consistency = min(models, key=lambda m: results_summary[m]['consistency'])

print(f"\n🏆 최우수 모델: {best_model}")
print(f"   종합 점수: {results_summary[best_model]['overall_score']:.1f}/100")
print(f"   이 모델이 Bug Hunt 평가 시스템에 최적입니다.")

print(f"\n✨ 구분력 최고: {best_discrimination}")
print(f"   구분력: {results_summary[best_discrimination]['discrimination']:.1f}점")
print(f"   (우수 코드와 미흡 코드를 가장 잘 구분함)")

print(f"\n✨ 순위 정확도 최고: {best_ranking}")
print(f"   Kendall's Tau: {results_summary[best_ranking]['ranking_tau']:.3f}")
print(f"   (품질 레벨 순서를 가장 정확히 평가함)")

print(f"\n✨ 일관성 최고: {best_consistency}")
print(f"   표준편차: {results_summary[best_consistency]['consistency']:.2f}점")
print(f"   (가장 안정적이고 일관된 평가)")

print("\n" + "=" * 120)
print("\n💡 지표 설명:")
print("   - 일관성: 같은 샘플을 여러 번 평가했을 때 점수가 얼마나 비슷한지 (낮을수록 좋음)")
print("   - 구분력: 우수한 코드와 미흡한 코드를 얼마나 잘 구분하는지 (높을수록 좋음)")
print("   - 순위 정확도: 품질 레벨 순서를 올바르게 평가하는지 (높을수록 좋음)")
print("   - 종합점수: 위 6개 지표를 가중 평균한 점수 (높을수록 좋음)")
print("=" * 120)
