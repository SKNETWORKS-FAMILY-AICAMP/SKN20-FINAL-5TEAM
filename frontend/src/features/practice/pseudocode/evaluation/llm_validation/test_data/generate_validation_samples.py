"""
의사코드 트랙 LLM 신뢰성 검증 - 샘플 생성

6개 Quest × 5개 품질 레벨 = 30개 샘플 생성 (× 5회 반복 = 150회 평가)
각 Quest별로 의사코드 품질 레벨에 맞는 샘플을 LLM으로 생성.

실행:
  python generate_validation_samples.py          # 전체 30개 생성
  python generate_validation_samples.py --quick  # 1개 Quest만 (5개)
"""
import os
import sys
import json
import time
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[8] / '.env')
except ImportError:
    pass

import openai

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
MODEL = "gpt-4o-mini"

# ── Quest 정의 ─────────────────────────────────────────────────────────────────
# 각 Quest의 핵심 개념과 기대 키워드 (rule-based 교차검증에 활용)
QUESTS = [
    {
        'id': '1',
        'title': '데이터 전처리 누수 방어 시스템 설계',
        'topic': '데이터 누수(Data Leakage) 방지, train/test 격리, fit/transform 분리 적용',
        'context': '고객 이탈 예측 모델에서 전처리 단계의 데이터 누수로 인해 운영 환경 성능이 급락하는 문제 해결',
        'key_concepts': ['train_test_split', 'fit/transform 분리', 'StandardScaler', 'Pipeline', '데이터 누수'],
    },
    {
        'id': '2',
        'title': '과적합 방어 정규화 시스템 설계',
        'topic': '과적합(Overfitting) 탐지 및 L1/L2 정규화, 조기 종료 전략',
        'context': '복잡한 회귀 모델의 과적합 문제를 Ridge/Lasso 정규화와 교차검증으로 해결',
        'key_concepts': ['Ridge', 'Lasso', 'L1/L2 정규화', 'cross-validation', 'early stopping', '과적합'],
    },
    {
        'id': '3',
        'title': '불균형 데이터 처리 시스템 설계',
        'topic': '클래스 불균형(Class Imbalance) 처리, SMOTE, 적절한 평가지표 선택',
        'context': '의료 데이터의 극심한 클래스 불균형 상황에서 소수 클래스를 정확히 예측하는 모델 설계',
        'key_concepts': ['SMOTE', 'class_weight', 'F1-score', 'AUC-ROC', 'stratified split', '불균형'],
    },
    {
        'id': '4',
        'title': '피처 엔지니어링 최적화 설계',
        'topic': '피처 선택, 차원 축소(PCA), 결측치/이상치 처리, 피처 스케일링',
        'context': '수백 개의 피처가 있는 고차원 데이터에서 모델 성능을 최대화하는 피처 엔지니어링 설계',
        'key_concepts': ['PCA', 'feature importance', 'correlation', 'StandardScaler', '결측치', '이상치'],
    },
    {
        'id': '5',
        'title': '하이퍼파라미터 튜닝 전략 설계',
        'topic': '체계적인 하이퍼파라미터 탐색, GridSearchCV/RandomSearch, 교차검증 전략',
        'context': '딥러닝 모델의 학습률, 배치 크기, 레이어 수 등 핵심 하이퍼파라미터를 효율적으로 탐색',
        'key_concepts': ['GridSearchCV', 'RandomizedSearchCV', 'learning rate', 'cross-validation', '하이퍼파라미터'],
    },
    {
        'id': '6',
        'title': '모델 해석성과 설명가능성 설계',
        'topic': '블랙박스 모델 해석, SHAP/LIME, 특성 중요도, 편향 탐지',
        'context': '금융 대출 심사 AI의 의사결정을 규제 기관에 설명하고 편향을 제거하는 설계',
        'key_concepts': ['SHAP', 'LIME', 'feature importance', '설명가능성', '편향', 'XAI'],
    },
]

# ── 품질 레벨 정의 ──────────────────────────────────────────────────────────────
QUALITY_LEVELS = {
    'excellent': {
        'desc': '실무 전문가 수준. 5단계 이상 구체적 설계, 전문 용어 다수 사용, 핵심 알고리즘 명시, 예외 처리 고려, 트레이드오프 언급',
        'score_range': [75, 85],
        'instruction': (
            '전문 ML 엔지니어가 작성한 수준의 매우 상세한 의사코드를 작성하세요. '
            '핵심 라이브러리/함수명을 정확히 사용하고, 각 단계별 이유를 간략히 포함하며, '
            '예외 상황(결측치, 이상치 등)도 처리하세요. 7단계 이상으로 작성하세요.'
        ),
    },
    'good': {
        'desc': '양호 수준. 핵심 흐름 완성, 전문 용어 1-2개 사용, 주요 단계 포함, 일부 구체성 있음',
        'score_range': [60, 74],
        'instruction': (
            '기본기가 있는 학습자 수준의 의사코드를 작성하세요. '
            '핵심 단계는 있지만 일부 세부 구현이 추상적이고, 1-2개 전문 용어를 사용하세요. '
            '예외 처리는 일부만 포함하고, 5단계 내외로 작성하세요.'
        ),
    },
    'average': {
        'desc': '보통 수준. 방향성은 맞으나 추상적, 전문 용어 부족, 핵심 단계 일부 누락',
        'score_range': [45, 59],
        'instruction': (
            '입문자 수준의 의사코드를 작성하세요. '
            '전체적인 방향은 맞지만 세부 구현이 매우 추상적이고 일반적입니다. '
            '전문 용어 없이 일반적인 표현을 사용하고, 3-4단계로 작성하세요.'
        ),
    },
    'poor': {
        'desc': '미흡 수준. 단편적, 핵심 개념 오해 또는 누락, 잘못된 접근법 포함',
        'score_range': [25, 44],
        'instruction': (
            '핵심 개념을 잘 모르는 수준의 의사코드를 작성하세요. '
            '일부 단계가 잘못되거나 핵심 처리가 빠져 있고, 용어 사용이 부정확합니다. '
            '2-3단계로 작성하고 중요한 처리 과정을 생략하세요.'
        ),
    },
    'very_poor': {
        'desc': '불량 수준. 매우 짧거나, 관련 없거나, 거의 모든 단계 누락',
        'score_range': [5, 24],
        'instruction': (
            '문제를 제대로 이해하지 못한 수준의 의사코드를 작성하세요. '
            '매우 짧고(2줄 이내), 핵심 단계가 대부분 빠져 있거나, '
            '잘못된 방향으로 설계된 내용을 작성하세요.'
        ),
    },
}


def generate_pseudocode(quest: dict, quality: str, level_info: dict) -> str:
    """LLM을 사용해 특정 품질 레벨의 의사코드 생성"""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""당신은 ML 교육 플랫폼의 테스트 데이터 생성 전문가입니다.
의사코드 평가 시스템을 검증하기 위한 샘플 데이터를 생성합니다.

[미션]
{quest['title']}

[배경]
{quest['context']}

[핵심 개념]
{', '.join(quest['key_concepts'])}

[품질 레벨: {quality.upper()}]
{level_info['instruction']}

지금 이 미션에 대해 위 품질 레벨에 맞는 의사코드를 작성해주세요.
의사코드만 작성하세요 (설명 없이, 제목 없이, 마크다운 없이, 순수 텍스트).
한국어로 작성하세요."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=600,
    )
    return response.choices[0].message.content.strip()


def generate_all_samples(quick: bool = False) -> list:
    quests = QUESTS[:1] if quick else QUESTS
    samples = []

    for quest in quests:
        print(f"\nQuest {quest['id']}: {quest['title']}")
        for quality, level_info in QUALITY_LEVELS.items():
            print(f"  [{quality}] 생성 중...")
            try:
                pseudocode = generate_pseudocode(quest, quality, level_info)
                sample = {
                    'sample_id': f"quest{quest['id']}_{quality}",
                    'quest_id': quest['id'],
                    'quest_title': quest['title'],
                    'quality_level': quality,
                    'expected_score_range': level_info['score_range'],
                    'pseudocode': pseudocode,
                }
                samples.append(sample)
                print(f"  [{quality}] 완료 (길이: {len(pseudocode)}자)")
                time.sleep(0.3)
            except Exception as e:
                print(f"  [{quality}] 오류: {e}")

    return samples


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true', help='Quest 1만 생성 (5개)')
    args = parser.parse_args()

    if not OPENAI_API_KEY:
        print("오류: OPENAI_API_KEY 환경 변수가 없습니다.")
        sys.exit(1)

    samples = generate_all_samples(quick=args.quick)

    out_dir = Path(__file__).parent / 'data'
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = '_quick' if args.quick else ''
    out_file = out_dir / f'validation_samples{suffix}.json'

    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)

    print(f"\n완료: {len(samples)}개 샘플 저장 → {out_file}")
