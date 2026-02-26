"""
생성된 샘플 검토 및 확정

generate_validation_samples.py 실행 후 draft 파일을 검토하고
문제 없으면 최종 파일로 확정.

사용법:
  python confirm_samples.py           # 전체 검토 후 확정
  python confirm_samples.py --quick   # quick draft 검토 후 확정
  python confirm_samples.py --show    # 내용 전체 출력 (확정 없이 보기만)
"""
import json
import shutil
from pathlib import Path

# analyze_results.py와 동일한 RUBRIC_KEYWORDS
RUBRIC_KEYWORDS = {
    "data_leakage":    {"core": ["train_test_split","split","누수","leakage","유출","테스트 정보","스케일링"], "mechanism": ["fit_transform","통계","mean","std","전체 데이터","오염","scaler"], "application": ["fit(X_train)","transform(X_test)","pipeline","교차검증","분리"]},
    "label_imbalance": {"core": ["불균형","imbalance","accuracy","편향","majority","소수"], "mechanism": ["weighted","클래스 비율","f1","recall","precision","over","under"], "application": ["class_weight","stratified","smote","f1-score","resampling"]},
    "overfitting":     {"core": ["과적합","overfitting","일반화","val","validation","차이"], "mechanism": ["복잡도","암기","분산","noise","파라미터","용량"], "application": ["dropout","regularization","early stopping","l1","l2","augment"]},
    "off_by_one":      {"core": ["off-by-one","인덱스","index","경계","범위","boundary"], "mechanism": ["0-based","len(","len()-1","boundary","조건"], "application": ["range(","슬라이싱","테스트","확인","검증"]},
    "null_pointer":    {"core": ["none","null","nonetype","체크","누락"], "mechanism": ["none 반환","속성","attributeerror","접근 실패","조건"], "application": ["is not none","if","방어","처리","isinstance"]},
    "type_mismatch":   {"core": ["타입","type","형변환","typeerror","불일치"], "mechanism": ["str(","int(","float(","dtype","암묵적","혼용"], "application": ["isinstance","명시적","형변환","검증","astype"]},
    "metric_selection":{"core": ["지표","metric","평가","회귀","분류","선택"], "mechanism": ["accuracy","f1","mse","mae","r2","차이","태스크"], "application": ["태스크","목적","비즈니스","다중","선택 기준"]},
    "feature_leakage": {"core": ["피처","feature","누수","leakage","타겟","미래"], "mechanism": ["파생","시점","정보","포함","예측 불가"], "application": ["의존성","시간","pipeline","검증","순서"]},
    "hyperparameter":  {"core": ["하이퍼파라미터","hyperparameter","학습률","learning rate","배치"], "mechanism": ["발산","수렴","너무 크","너무 작","배치 크기","영향"], "application": ["grid search","scheduler","validation","모니터링","튜닝"]},
    "memory_leak":     {"core": ["메모리","memory","누수","leak","증가","해제"], "mechanism": ["참조","generator","list","순환","gc","accumulate"], "application": ["with","del","프로파일링","generator","yield"]},
    "race_condition":  {"core": ["경쟁","race","동기화","비결정","thread","스레드"], "mechanism": ["공유","원자","atomic","안전","순서","접근"], "application": ["lock","mutex","동기화","queue","스레드 안전"]},
    "api_timeout":     {"core": ["timeout","타임아웃","지연","네트워크","응답"], "mechanism": ["무한 대기","설정 부재","에러","전파","blocking"], "application": ["try","except","timeout=","retry","재시도"]},
}
MAX_SCORES = {"core": 40, "mechanism": 35, "application": 25}


def compute_rule_score(case_id, text):
    kw = RUBRIC_KEYWORDS.get(case_id, {})
    t = text.lower()
    def sc(keys, mx):
        if not keys: return mx // 2
        r = sum(1 for k in keys if k.lower() in t) / len(keys)
        if r >= 0.5: return mx
        if r >= 0.3: return round(mx * 0.65)
        if r >= 0.15: return round(mx * 0.35)
        return 0
    return sc(kw.get('core',[]), MAX_SCORES['core']) + sc(kw.get('mechanism',[]), MAX_SCORES['mechanism']) + sc(kw.get('application',[]), MAX_SCORES['application'])


def show_samples(samples, verbose=False):
    """샘플 내용 출력"""
    print(f"\n{'='*70}")
    print(f"총 {len(samples)}개 샘플 검토")
    print(f"{'='*70}")

    issues = []
    by_quality = {}

    for s in samples:
        quality = s['quality_level']
        exp_min, exp_max = s['expected_score_range']
        text = " ".join(filter(None, [s['explanations'].get('1',''), s['explanations'].get('3','')]))
        score = compute_rule_score(s['case_id'], text)
        in_range = exp_min <= score <= exp_max

        by_quality.setdefault(quality, []).append({'sample': s, 'score': score, 'in_range': in_range})
        if not in_range:
            issues.append({'sample_id': s['sample_id'], 'score': score, 'expected': f"{exp_min}-{exp_max}"})

    # 품질별 요약
    print(f"\n{'품질':12s} {'샘플수':>6s} {'평균점수':>8s} {'범위통과':>8s}")
    print("-" * 40)
    for quality in ['excellent', 'good', 'average', 'poor', 'very_poor']:
        items = by_quality.get(quality, [])
        if not items: continue
        avg = sum(i['score'] for i in items) / len(items)
        ok = sum(1 for i in items if i['in_range'])
        print(f"  {quality:12s} {len(items):>6d} {avg:>8.1f} {ok}/{len(items):>5d}")

        if verbose:
            for item in items:
                s = item['sample']
                mark = "O" if item['in_range'] else "X"
                print(f"    [{mark}] {s['sample_id']} ({item['score']}점)")
                print(f"       진단: {s['explanations'].get('1','')[:120]}")
                print(f"       설명: {s['explanations'].get('3','')[:120]}")

    # 범위 이탈 목록
    if issues:
        print(f"\n[범위 이탈 {len(issues)}개]")
        for iss in issues:
            print(f"  {iss['sample_id']}: {iss['score']}점 (기대: {iss['expected']})")
    else:
        print("\n모든 샘플이 기대 범위 내입니다.")

    return issues


def main(quick=False, show_only=False):
    data_dir = Path(__file__).parent / 'data'
    draft_name = 'quick_new_samples_draft.json' if quick else 'new_validation_samples_draft.json'
    final_name = 'quick_new_validation_samples.json' if quick else 'new_validation_samples.json'

    draft_file = data_dir / draft_name
    final_file = data_dir / final_name

    if not draft_file.exists():
        print(f"draft 파일이 없습니다: {draft_file}")
        print("먼저 generate_validation_samples.py를 실행하세요.")
        return

    with open(draft_file, 'r', encoding='utf-8') as f:
        samples = json.load(f)

    issues = show_samples(samples, verbose=True)

    if show_only:
        print("\n(--show 모드: 확정하지 않음)")
        return

    # 확정 여부 확인
    if issues:
        print(f"\n범위 이탈 샘플이 {len(issues)}개 있습니다.")
        print("그래도 확정하시겠습니까? (y/n): ", end='')
        answer = input().strip().lower()
        if answer != 'y':
            print("취소됨. draft 파일을 수동으로 수정 후 다시 실행하세요.")
            return

    shutil.copy(draft_file, final_file)
    print(f"\n확정 완료: {final_file}")
    print("이제 run_full_validation.py를 실행할 때 이 파일을 사용하세요.")
    print(f"  run_evaluation.py의 samples_file 경로를 {final_name}으로 변경 필요")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true')
    parser.add_argument('--show', action='store_true', help='보기만 하고 확정 안 함')
    args = parser.parse_args()
    main(quick=args.quick, show_only=args.show)
