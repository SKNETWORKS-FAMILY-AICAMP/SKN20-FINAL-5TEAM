"""
새 검증 샘플 생성 스크립트

기존 샘플의 코드/버그 정보는 유지하고 explanations만 새로 생성.
품질 레벨을 새 루브릭(core/mechanism/application) 기준에 맞게 조정.

실행:
  python generate_validation_samples.py          # 전체 60개 생성
  python generate_validation_samples.py --quick  # 1개 버그 유형만 (테스트)
"""
import os
import sys
import json
import time
from pathlib import Path

try:
    from dotenv import load_dotenv
    # 프로젝트 루트의 .env 로드
    load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / '.env')
except ImportError:
    pass

import openai

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
MODEL = "gpt-4o-mini"

# analyze_results.py의 RUBRIC_KEYWORDS와 동일
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

# 새 루브릭 기준 예상 점수 범위
# good/average 상한을 넓힌 이유: 일부 application/mechanism 키워드가 일상 단어여서
# 금지해도 자연 언어에서 등장할 수 있음 (예: "확인", "if", "처리", "공유" 등)
NEW_EXPECTED_RANGES = {
    "excellent": [80, 100],
    "good":      [55,  90],
    "average":   [25,  65],
    "poor":      [5,   24],
    "very_poor": [0,    4]
}

def get_quality_instruction(case_id, quality):
    """루브릭 키워드 기반으로 품질별 동적 지침 생성 (excellent/good/average만 사용)"""
    kw = RUBRIC_KEYWORDS.get(case_id, {})
    core = kw.get('core', [])
    mech = kw.get('mechanism', [])
    appl = kw.get('application', [])

    if quality == 'excellent':
        # 모든 카테고리 키워드 포함 → 40+35+25=100점
        return (
            f"[excellent - 90점] 3-5문장 답변. 아래 단어들을 그대로 사용 (exact string):\n"
            f"core (모두 사용): {', '.join(core)}\n"
            f"mechanism (모두 사용): {', '.join(mech)}\n"
            f"application (모두 사용): {', '.join(appl)}"
        )

    elif quality == 'good':
        # core 전체 (40점) + mechanism 전체 (35점) + appl 완전 제외 → 75점
        return (
            f"[good - 65점] 2-3문장 답변. 아래 단어들을 그대로 사용 (exact string):\n"
            f"core (모두 사용): {', '.join(core)}\n"
            f"mechanism (모두 사용): {', '.join(mech)}\n"
            f"⚠️ 절대 포함 금지 (application): {', '.join(appl)}\n"
            f"실무 해결책(application)은 언급하지 말고, 원인과 내부 동작만 설명."
        )

    elif quality == 'average':
        # core 전체 (40점) + mech/appl 완전 제외 → 40점
        forbidden = mech + appl
        return (
            f"[average - 35점] 1-2문장 답변. 아래 core 단어들을 그대로 사용 (exact string):\n"
            f"core (모두 사용): {', '.join(core)}\n"
            f"⚠️ 절대 포함 금지 (mechanism + application): {', '.join(forbidden)}\n"
            f"버그 이름은 알지만 내부 동작이나 해결책을 모르는 피상적 답변."
        )

    return ""


def build_poor_answer(case_id):
    """poor 품질 답변 템플릿 생성 (API 없이) - core[0] 1개 포함 → ~14점"""
    core = RUBRIC_KEYWORDS.get(case_id, {}).get('core', [])
    keyword = core[0] if core else case_id
    return {
        "step1": f"이 코드에서 {keyword} 관련 문제가 있어서 오류가 발생했습니다.",
        "step3": f"{keyword}을(를) 수정하여 코드가 동작하도록 했습니다."
    }


def build_very_poor_answer():
    """very_poor 품질 답변 하드코딩 (API 없이) - 키워드 0개 → 0점"""
    return {
        "step1": "코드를 실행하니 오류가 발생했습니다.",
        "step3": "오류를 수정하여 코드가 실행됩니다."
    }


def compute_rule_score(case_id, explanation_text):
    """규칙 기반 점수 계산 (리뷰용)"""
    keywords = RUBRIC_KEYWORDS.get(case_id, {})
    text = explanation_text.lower()

    def score_cat(kws, max_s):
        if not kws:
            return max_s // 2
        ratio = sum(1 for kw in kws if kw.lower() in text) / len(kws)
        if ratio >= 0.5:   return max_s
        if ratio >= 0.3:   return round(max_s * 0.65)
        if ratio >= 0.15:  return round(max_s * 0.35)
        return 0

    return (
        score_cat(keywords.get('core', []),        MAX_SCORES['core']) +
        score_cat(keywords.get('mechanism', []),   MAX_SCORES['mechanism']) +
        score_cat(keywords.get('application', []), MAX_SCORES['application'])
    )


def generate_explanations(case_id, bug_type, buggy_code, bug_description, rubric, quality_level):
    """품질 레벨에 맞는 학습자 답변 생성 (poor/very_poor는 API 없이 템플릿 사용)"""
    # poor/very_poor: 템플릿으로 보장된 점수 생성
    if quality_level == 'very_poor':
        return build_very_poor_answer()
    if quality_level == 'poor':
        return build_poor_answer(case_id)

    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    core_str        = ', '.join(rubric.get('core_concepts', []))
    mechanism_str   = ', '.join(rubric.get('mechanism_concepts', []))
    application_str = ', '.join(rubric.get('application_concepts', []))
    instruction     = get_quality_instruction(case_id, quality_level)

    prompt = f"""주니어 AI 엔지니어 기술 면접 시뮬레이션용 학습자 답변을 생성해줘.

[버그 정보]
버그 유형: {bug_type}
버그 설명: {bug_description}
코드:
{buggy_code}

[채점 루브릭]
core 개념 (40점): {core_str}
mechanism 개념 (35점): {mechanism_str}
application 개념 (25점): {application_str}

[생성 지침 - {quality_level}]
{instruction}

[출력 형식]
버그를 진단하고 수정 이유를 설명하는 학습자 답변 2개를 JSON으로 출력.
답변은 자연스러운 구어체 한국어로 작성 (면접 답변 스타일).
루브릭 키워드를 자연스럽게 포함하거나 배제할 것.

{{
  "step1": "버그 원인을 설명하는 답변 (2-4문장)",
  "step3": "수정 이유를 설명하는 답변 (2-4문장)"
}}

JSON만 출력. 다른 텍스트 없음."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500,
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)


def run_review(samples):
    """생성된 샘플 자동 검토 - 점수 범위 확인"""
    print("\n" + "="*70)
    print("검토 결과 (규칙 기반 점수 vs 기대 범위)")
    print("="*70)

    issues = []
    quality_stats = {q: {'ok': 0, 'fail': 0} for q in NEW_EXPECTED_RANGES}

    for s in samples:
        case_id     = s['case_id']
        quality     = s['quality_level']
        exp_min, exp_max = s['expected_score_range']

        text = " ".join(filter(None, [
            s['explanations'].get('1', ''),
            s['explanations'].get('3', '')
        ]))
        score = compute_rule_score(case_id, text)
        in_range = exp_min <= score <= exp_max

        if in_range:
            quality_stats[quality]['ok'] += 1
        else:
            quality_stats[quality]['fail'] += 1
            issues.append({
                'sample_id': s['sample_id'],
                'quality': quality,
                'score': score,
                'expected': f"{exp_min}-{exp_max}",
                'step1': s['explanations'].get('1', '')[:80],
                'step3': s['explanations'].get('3', '')[:80]
            })

    # 품질별 통과율
    print(f"\n{'품질':12s} {'통과':>6s} {'실패':>6s} {'통과율':>8s}")
    print("-"*40)
    total_ok = total_fail = 0
    for quality in ['excellent', 'good', 'average', 'poor', 'very_poor']:
        ok   = quality_stats[quality]['ok']
        fail = quality_stats[quality]['fail']
        total = ok + fail
        rate = ok / total * 100 if total else 0
        mark = "O" if fail == 0 else "X"
        print(f"[{mark}] {quality:12s} {ok:>6d} {fail:>6d} {rate:>7.0f}%")
        total_ok += ok
        total_fail += fail

    print("-"*40)
    total = total_ok + total_fail
    print(f"    {'전체':12s} {total_ok:>6d} {total_fail:>6d} {total_ok/total*100:>7.0f}%")

    # 범위 이탈 샘플 상세
    if issues:
        print(f"\n[범위 이탈 샘플 {len(issues)}개]")
        for issue in issues:
            print(f"\n  {issue['sample_id']}")
            print(f"  규칙 점수: {issue['score']}점  기대: {issue['expected']}점")
            print(f"  step1: {issue['step1']}...")
            print(f"  step3: {issue['step3']}...")
    else:
        print("\n모든 샘플이 기대 점수 범위 내에 있습니다.")

    return issues


def main(quick=False):
    if not OPENAI_API_KEY:
        print("OPENAI_API_KEY가 설정되지 않았습니다.")
        sys.exit(1)

    # 기존 샘플 로드
    samples_file = Path(__file__).parent.parent / 'model_comparison' / 'scripts' / 'bug_hunt_validation_samples.json'
    with open(samples_file, 'r', encoding='utf-8') as f:
        original_samples = json.load(f)

    # quick 모드: data_leakage만
    if quick:
        original_samples = [s for s in original_samples if s['case_id'] == 'data_leakage']
        print(f"Quick 모드: {len(original_samples)}개 샘플만 생성")

    # 루브릭 (run_evaluation.py의 RUBRICS와 동일)
    RUBRICS = {
        "data_leakage":    {"core_concepts": ["train/test split 이전 fit", "테스트 정보 유출", "data leakage"], "mechanism_concepts": ["fit_transform 전체 데이터 적용", "통계 정보 누출", "test set 오염"], "application_concepts": ["split 후 fit/transform 분리", "pipeline 사용", "교차검증 주의"]},
        "label_imbalance": {"core_concepts": ["클래스 불균형", "majority class 편향", "accuracy 함정"], "mechanism_concepts": ["소수 클래스 무시", "weighted loss", "불균형 영향"], "application_concepts": ["f1-score 사용", "stratified split", "class_weight 설정"]},
        "overfitting":     {"core_concepts": ["과적합", "train/val 성능 차이", "일반화 실패"], "mechanism_concepts": ["모델 복잡도", "훈련 데이터 암기", "분산 증가"], "application_concepts": ["dropout", "regularization", "early stopping"]},
        "off_by_one":      {"core_concepts": ["인덱스 경계", "off-by-one", "범위 초과"], "mechanism_concepts": ["0-based indexing", "len()-1", "boundary condition"], "application_concepts": ["경계값 테스트", "range 함수 확인", "슬라이싱 주의"]},
        "null_pointer":    {"core_concepts": ["None 체크 누락", "null 참조", "NoneType 오류"], "mechanism_concepts": ["None 반환 조건", "속성 접근 실패", "AttributeError"], "application_concepts": ["방어적 프로그래밍", "None 처리", "is not None 확인"]},
        "type_mismatch":   {"core_concepts": ["타입 불일치", "형변환 필요", "TypeError"], "mechanism_concepts": ["암묵적 형변환", "문자열/숫자 혼용", "dtype 불일치"], "application_concepts": ["명시적 형변환", "isinstance 확인", "타입 검증"]},
        "metric_selection":{"core_concepts": ["잘못된 평가 지표", "회귀/분류 혼용", "metric 선택 오류"], "mechanism_concepts": ["accuracy vs f1 차이", "MSE vs MAE", "태스크별 적절한 지표"], "application_concepts": ["태스크 확인 후 지표 선택", "비즈니스 목적 고려", "다중 지표 사용"]},
        "feature_leakage": {"core_concepts": ["특성 누수", "타겟 정보 포함 피처", "미래 정보 사용"], "mechanism_concepts": ["피처 엔지니어링 시점", "타겟 파생 변수", "예측 불가능 피처"], "application_concepts": ["피처 의존성 분석", "시간 순서 주의", "pipeline 사용"]},
        "hyperparameter":  {"core_concepts": ["하이퍼파라미터 오류", "학습률 문제", "배치 크기 부적절"], "mechanism_concepts": ["학습률 너무 크면 발산", "너무 작으면 수렴 지연", "배치 크기 영향"], "application_concepts": ["grid search", "learning rate scheduler", "validation 모니터링"]},
        "memory_leak":     {"core_concepts": ["메모리 누수", "자원 해제 누락", "메모리 증가"], "mechanism_concepts": ["참조 유지", "generator vs list", "순환 참조"], "application_concepts": ["with 문 사용", "명시적 del", "메모리 프로파일링"]},
        "race_condition":  {"core_concepts": ["경쟁 상태", "동기화 문제", "비결정적 결과"], "mechanism_concepts": ["공유 자원 접근", "스레드 안전성", "원자성 부재"], "application_concepts": ["Lock 사용", "동기화 메커니즘", "스레드 안전 자료구조"]},
        "api_timeout":     {"core_concepts": ["타임아웃", "API 응답 지연", "네트워크 오류 처리"], "mechanism_concepts": ["timeout 설정 부재", "무한 대기", "에러 전파"], "application_concepts": ["try/except 사용", "timeout 파라미터 설정", "재시도 로직"]},
    }

    new_samples = []
    total = len(original_samples)

    print(f"\n총 {total}개 샘플 생성 시작")
    print(f"모델: {MODEL}")

    for idx, sample in enumerate(original_samples):
        case_id     = sample['case_id']
        quality     = sample['quality_level']
        bug_type    = sample['bug_type']
        buggy_code  = sample['steps'][0]['buggy_code']
        bug_desc    = sample['steps'][0]['instruction']
        rubric      = RUBRICS.get(case_id, {})

        print(f"\n[{idx+1}/{total}] {sample['sample_id']} 생성 중...")

        try:
            generated = generate_explanations(
                case_id, bug_type, buggy_code, bug_desc, rubric, quality
            )

            new_sample = {k: v for k, v in sample.items()}  # 기존 필드 유지
            new_sample['explanations'] = {
                '1': generated.get('step1', ''),
                '2': sample['explanations'].get('2', ''),  # 코드 수정은 유지
                '3': generated.get('step3', '')
            }
            new_sample['expected_score_range'] = NEW_EXPECTED_RANGES[quality]
            new_samples.append(new_sample)

            # 생성된 내용 미리보기
            print(f"  step1: {generated.get('step1', '')[:100]}...")
            print(f"  step3: {generated.get('step3', '')[:100]}...")

            time.sleep(0.3)

        except Exception as e:
            print(f"  오류: {e} → 기존 샘플 유지")
            new_samples.append(sample)

    # 저장 (검토 전에 먼저 저장)
    out_dir = Path(__file__).parent / 'data'
    out_dir.mkdir(parents=True, exist_ok=True)
    draft_file = out_dir / ('quick_new_samples_draft.json' if quick else 'new_validation_samples_draft.json')

    with open(draft_file, 'w', encoding='utf-8') as f:
        json.dump(new_samples, f, ensure_ascii=False, indent=2)

    print(f"\n초안 저장: {draft_file}")

    # 자동 검토
    issues = run_review(new_samples)

    if issues:
        print(f"\n범위 이탈 샘플 {len(issues)}개가 있습니다.")
        print("draft 파일을 검토 후 문제가 없으면 아래 명령으로 확정하세요:")
    else:
        print("\n모든 샘플이 기대 범위 내입니다.")
        print("아래 명령으로 확정하세요:")

    final_name = 'quick_new_validation_samples.json' if quick else 'new_validation_samples.json'
    print(f"  python confirm_samples.py {'--quick' if quick else ''}")
    print(f"  → {out_dir / final_name} 으로 저장됩니다.")

    return issues


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true', help='data_leakage 5개만 (테스트)')
    args = parser.parse_args()
    main(quick=args.quick)
