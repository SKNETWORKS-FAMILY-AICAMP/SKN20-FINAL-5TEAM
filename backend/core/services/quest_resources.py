"""
[2026-02-21 대폭 개편]
의사코드 퀘스트별 추천 영상, 차원 우선순위, Deep Dive 패턴 통합 관리 서비스

아키텍처:
  - QUEST_VIDEOS: 모든 차원이 [list] 구조 (consistency 유지)
  - DIMENSION_PRIORITY_BY_QUEST: 퀘스트별 차원 가중치
  - DEEP_DIVE_PATTERNS: 각 Quest의 깊이 학습 시나리오 틀
  - validate_* 함수들: 데이터 검증 로직
"""

import logging

logger = logging.getLogger(__name__)


# ============================================================================
# 1. 차원별 우선순위 (퀘스트별로 다름 - 한 번에 하나씩 점검)
# ============================================================================

DIMENSION_PRIORITY_BY_QUEST = {
    '1': ['consistency', 'design', 'implementation', 'abstraction', 'edgeCase'],
    '2': ['design', 'consistency', 'implementation', 'edgeCase', 'abstraction'],
    '3': ['consistency', 'design', 'edgeCase', 'abstraction', 'implementation'],
    '4': ['design', 'implementation', 'consistency', 'abstraction', 'edgeCase'],
    '5': ['design', 'consistency', 'implementation', 'abstraction', 'edgeCase'],
    '6': ['abstraction', 'consistency', 'design', 'implementation', 'edgeCase'],
}

# 폴백 (Quest ID를 모를 때)
DEFAULT_DIMENSION_PRIORITY = ['consistency', 'design', 'implementation', 'abstraction', 'edgeCase']


# ============================================================================
# 2. YouTube 추천 영상 맵 (모든 차원이 [list] 구조로 통일)
# ============================================================================

QUEST_VIDEOS = {
    # ──────────────────────────────────────────────────────────
    # Quest 1: 데이터 누수 방어 시스템 설계
    # 우선순위: consistency > design > implementation > abstraction > edgeCase
    # ──────────────────────────────────────────────────────────
    1: {
        'consistency': [
            {'id': 'A88rDEf-pfk', 'title': 'Standardization vs Normalization — fit/transform (StatQuest)', 'channel': 'StatQuest'},
            {'id': 'fSytzGwwBVw', 'title': 'What is Data Leakage? (StatQuest)', 'channel': 'StatQuest'},
        ],
        'design': [
            {'id': 'fSytzGwwBVw', 'title': 'What is Data Leakage? (StatQuest)', 'channel': 'StatQuest'},
        ],
        'implementation': [
            {'id': 'rmEa9_8GKQY', 'title': 'Sklearn Pipeline으로 Data Leakage 방지 (Krish Naik)', 'channel': 'Krish Naik'},
        ],
        'abstraction': [
            {'id': 'gJo0uNL-5Lw', 'title': 'K-Fold Cross Validation (StatQuest)', 'channel': 'StatQuest'},
        ],
        'edgeCase': [
            {'id': 'Gmq7mXv6M-c', 'title': 'Saving & Loading ML Models — Pickle & Joblib (NeuralNine)', 'channel': 'NeuralNine'},
        ],
        'default': [
            {'id': 'fSytzGwwBVw', 'title': 'What is Data Leakage?', 'channel': 'StatQuest'},
            {'id': 'A88rDEf-pfk', 'title': 'Standardization vs Normalization', 'channel': 'StatQuest'},
            {'id': 'rmEa9_8GKQY', 'title': 'Sklearn Pipeline', 'channel': 'Krish Naik'},
        ],
    },

    # ──────────────────────────────────────────────────────────
    # Quest 2: 과적합 방어 정규화 시스템 설계
    # 우선순위: design > consistency > implementation > edgeCase > abstraction
    # ──────────────────────────────────────────────────────────
    2: {
        'design': [
            {'id': 'Q81RR3yKn30', 'title': 'Ridge & Lasso Regularization 완전 이해 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'consistency': [
            {'id': 'EuBBz3bI-aA', 'title': 'Bias and Variance Tradeoff (StatQuest)', 'channel': 'StatQuest'},
        ],
        'implementation': [
            {'id': 'Q81RR3yKn30', 'title': 'Ridge & Lasso 구현 (sklearn) (StatQuest)', 'channel': 'StatQuest'},
        ],
        'edgeCase': [
            {'id': 'CRlYPodahlE', 'title': 'Early Stopping & Dropout (DeepLearningAI)', 'channel': 'DeepLearningAI'},
        ],
        'abstraction': [
            {'id': 'EuBBz3bI-aA', 'title': 'Underfitting & Overfitting 원리 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'default': [
            {'id': 'EuBBz3bI-aA', 'title': 'Bias and Variance', 'channel': 'StatQuest'},
            {'id': 'Q81RR3yKn30', 'title': 'Ridge & Lasso', 'channel': 'StatQuest'},
            {'id': 'CRlYPodahlE', 'title': 'Early Stopping & Dropout', 'channel': 'DeepLearningAI'},
        ],
    },

    # ──────────────────────────────────────────────────────────
    # Quest 3: 불균형 데이터 처리 시스템 설계
    # 우선순위: consistency > design > edgeCase > abstraction > implementation
    # ──────────────────────────────────────────────────────────
    3: {
        'consistency': [
            {'id': '4jRBRDbJemM', 'title': 'ROC Curve & AUC — 불균형 평가의 표준 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'design': [
            {'id': '_eG4_5tWlM4', 'title': 'Imbalanced Data 처리 전략 설계 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'edgeCase': [
            {'id': 'RwtP8TToimY', 'title': 'Class Weights & Cost-Sensitive Learning (Krish Naik)', 'channel': 'Krish Naik'},
        ],
        'abstraction': [
            {'id': 'gJo0uNL-5Lw', 'title': 'StratifiedKFold & 계층화 분할 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'implementation': [
            {'id': 'U3X98xZ4_no', 'title': 'SMOTE 완전 구현 (imbalanced-learn)', 'channel': 'imbalanced-learn'},
        ],
        'default': [
            {'id': '_eG4_5tWlM4', 'title': 'Handling Imbalanced Data', 'channel': 'StatQuest'},
            {'id': '4jRBRDbJemM', 'title': 'ROC AUC', 'channel': 'StatQuest'},
            {'id': 'U3X98xZ4_no', 'title': 'SMOTE', 'channel': 'imbalanced-learn'},
        ],
    },

    # ──────────────────────────────────────────────────────────
    # Quest 4: 피처 엔지니어링 최적화 설계
    # 우선순위: design > implementation > consistency > abstraction > edgeCase
    # ──────────────────────────────────────────────────────────
    4: {
        'design': [
            {'id': 'md8IrSMPi6o', 'title': 'Feature Engineering 실전 (Kaggle Course)', 'channel': 'Kaggle'},
        ],
        'implementation': [
            {'id': '68ABAU_V8qI', 'title': 'Feature Selection — RandomForest 중요도 분석 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'consistency': [
            {'id': 'A88rDEf-pfk', 'title': 'StandardScaler fit/transform 분리 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'abstraction': [
            {'id': 'viZrOnJclY0', 'title': 'Polynomial Features & 상호작용 특성 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'edgeCase': [
            {'id': 'FgakZw6K1QQ', 'title': 'Curse of Dimensionality & PCA (StatQuest)', 'channel': 'StatQuest'},
        ],
        'default': [
            {'id': 'md8IrSMPi6o', 'title': 'Feature Engineering', 'channel': 'Kaggle'},
            {'id': '68ABAU_V8qI', 'title': 'Feature Selection', 'channel': 'StatQuest'},
            {'id': 'FgakZw6K1QQ', 'title': 'Curse of Dimensionality', 'channel': 'StatQuest'},
        ],
    },

    # ──────────────────────────────────────────────────────────
    # Quest 5: 하이퍼파라미터 튜닝 전략 설계
    # 우선순위: design > consistency > implementation > abstraction > edgeCase
    # ──────────────────────────────────────────────────────────
    5: {
        'design': [
            {'id': 'HdlDYng7g58', 'title': 'Hyperparameter Tuning — GridSearch vs RandomSearch (StatQuest)', 'channel': 'StatQuest'},
        ],
        'consistency': [
            {'id': 'gJo0uNL-5Lw', 'title': 'K-Fold Cross Validation — 튜닝 신뢰도 확보 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'implementation': [
            {'id': 'HdlDYng7g58', 'title': 'GridSearchCV 완전 구현 (sklearn)', 'channel': 'StatQuest'},
        ],
        'abstraction': [
            {'id': 'Np8h_U9PmFw', 'title': '파라미터 상호작용 & Warm-start (W&B)', 'channel': 'W&B'},
        ],
        'edgeCase': [
            {'id': 'Np8h_U9PmFw', 'title': 'Bayesian Optimization & Optuna — 효율적 탐색 (W&B)', 'channel': 'W&B'},
        ],
        'default': [
            {'id': 'HdlDYng7g58', 'title': 'Hyperparameter Tuning', 'channel': 'StatQuest'},
            {'id': 'gJo0uNL-5Lw', 'title': 'K-Fold Cross Validation', 'channel': 'StatQuest'},
            {'id': 'Np8h_U9PmFw', 'title': 'Bayesian Optimization', 'channel': 'W&B'},
        ],
    },

    # ──────────────────────────────────────────────────────────
    # Quest 6: 모델 해석성과 설명가능성 설계
    # 우선순위: abstraction > consistency > design > implementation > edgeCase
    # ──────────────────────────────────────────────────────────
    6: {
        'abstraction': [
            {'id': 'B-c8tIgchu0', 'title': 'SHAP Values — 전역·개별 해석 설계 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'consistency': [
            {'id': 'B-c8tIgchu0', 'title': 'SHAP Summary Plot — 일관된 해석 기준 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'design': [
            {'id': 'GfGpXMBjOBg', 'title': 'Counterfactual Explanation & Actionable AI (Google)', 'channel': 'Google'},
        ],
        'implementation': [
            {'id': 'C80SQe16Rao', 'title': 'LIME 구현 — 개별 예측 설명 (Towards Data Science)', 'channel': 'Towards Data Science'},
        ],
        'edgeCase': [
            {'id': 'GfGpXMBjOBg', 'title': 'AI Fairness & Proxy Bias 감지 (Google Developers)', 'channel': 'Google'},
        ],
        'default': [
            {'id': 'B-c8tIgchu0', 'title': 'SHAP Values', 'channel': 'StatQuest'},
            {'id': 'C80SQe16Rao', 'title': 'LIME', 'channel': 'Towards Data Science'},
            {'id': 'GfGpXMBjOBg', 'title': 'AI Fairness', 'channel': 'Google'},
        ],
    },
}

# ============================================================================
# 3. Deep Dive 시나리오 패턴 (꼬리질문 정답을 알아도 더 깊이 생각해야 함)
# ============================================================================

DEEP_DIVE_PATTERNS = {
    '1': {
        'title': '대규모 실시간 서빙 환경의 누수 대응',
        'pattern': '[대규모 실시간 서빙] {데이터 볼륨}, {시간 제약}의 환경에서 {역할}을 수행해야 할 때, 누수를 방지하려면?',
        'example_scenario': '[대규모 실시간 서빙] 매초 10만 건의 거래 데이터가 들어오는데, 모델 서빙 중 매주 재학습을 해야 합니다. 이전 주 데이터로 만든 Scaler를 새 주 데이터에 그대로 사용하면 문제가 생길까?',
        'model_answer': '예, 심각한 누수가 발생합니다. 새 주 데이터(분포가 변했을 수 있음)의 통계량을 학습 중에 포함하므로, Scaler를 주 단위로 재학습해야 합니다. 또는 데이터 드리프트를 모니터링하여 임계값을 넘으면 경고합니다.',
    },
    '2': {
        'title': '제약된 데이터에서의 과적합 대응 설계',
        'pattern': '[제약된 학습 데이터] {샘플 수}건, {특성 수}개의 데이터로 {요구 정확도}를 달성해야 할 때, 과적합 없이 신뢰도 높은 모델을 만들려면?',
        'example_scenario': '[제약된 학습 데이터] 학습셋 100건뿐인데, 검증 정확도 85% 이상을 달성해야 합니다. 정규화, K-Fold, 조기종료 중 어떤 조합이 가장 효과적일까?',
        'model_answer': 'K-Fold(cv=5)로 신뢰도 확보, L2 정규화(Ridge)는 약하게, 조기종료(EarlyStopping)로 과적합 시점 감지. 단, 데이터 부족 시 augmentation 고려. 최종 평가는 테스트셋이 아닌 k-fold 평균으로 신뢰성 판단.',
    },
    '3': {
        'title': '불균형 환경에서의 비용 민감 문제',
        'pattern': '[비용 불균형] 양성(거짓음성 cost={비용} 손실) vs 음성(거짓양성 cost={비용} 손실)의 불균형에서 {제약}을 만족하려면?',
        'example_scenario': '[비용 불균형] 이상 거래 1건 놓치면 $10,000 손실인데, 오탐지 1건은 $100 비용. 정확도 90%인 모델(불균형 고려 없음)은 신뢰할 수 있을까?',
        'model_answer': '아니요. class_weight="balanced"를 사용하거나 sample_weight로 비용을 반영. 임계값을 기본 0.5에서 더 높게 조정(0.7~0.8)하여 양성 예측을 보수적으로. ROC AUC로 평가해야 정확도의 함정을 피합니다.',
    },
    '4': {
        'title': '고차원 피처 공간에서의 차원의 저주',
        'pattern': '[차원 증가] {원시 특성 개수}에서 {파생 방식}으로 {결과 차원}까지 늘렸을 때, 성능이 {저하 패턴}이면 어떻게 대응할까?',
        'example_scenario': '[차원 증가] 원래 특성 5개에서 PolynomialFeatures(degree=2)로 20개로 늘렸더니 모델 성능이 하락했습니다. 원인은 무엇이고 해결책은?',
        'model_answer': '차원의 저주(동일 샘플 수로 공간 희소성 증가)와 과적합 위험 상승. 해결책: (1) PCA로 10개로 축소, (2) SelectKBest(f_classif, k=10)로 중요도 기반 선택, (3) L1 정규화(Lasso)로 자동 특성제거.',
    },
    '5': {
        'title': '하이퍼파라미터 상호작용과 효율적 탐색',
        'pattern': '[탐색 효율성] {파라미터 조합 수}개를 {예산 제약} 초과 없이 탐색할 때, n_estimators와 max_depth의 상호작용을 고려하려면?',
        'example_scenario': '[탐색 효율성] GridSearchCV(cv=5)로 100개 조합을 탐색하면 12시간이 걸립니다. Optuna를 쓰면 빠를까? n_estimators=1000은 max_depth를 낮게 해야 할까?',
        'model_answer': '예, Optuna(베이지안 최적화)로 40% 시간 단축 가능. n_estimators ↑ → max_depth는 ↓ (과적합 위험 완화). Warm-start 사용하여 이전 학습 상태 계승 가능.',
    },
    '6': {
        'title': '대리변수 차별(Proxy Bias)과 공정성 검증',
        'pattern': '[공정성 검증] {보호속성}이 모델 특성에 없는데도 {간접 차별}이 의심될 때, 편향을 감지하고 완화하려면?',
        'example_scenario': '[공정성 검증] 대출 승인 모델에서 성별은 특성에 없지만, 직업과 거주지로 간접 차별이 발생할 수 있습니다. 이를 감지하고 개선하려면?',
        'model_answer': 'SHAP로 각 속성의 기여도 시각화. 성별별 정확도 비교하여 disparity 추출. Proxy Bias 제거: (1) 의심 특성 제거(직업/거주지), (2) adversarial debiasing, (3) 보호속성별 모델 분리.',
    },
}


# ============================================================================
# 4. 검증 함수들
# ============================================================================

def get_dimension_priority(quest_id: str) -> list:
    """
    퀘스트별 차원 우선순위를 반환합니다.
    
    Args:
        quest_id: 퀘스트 ID (1~6, 또는 '1'~'6')
    
    Returns:
        차원을 우선순위 순으로 정렬한 리스트
    """
    quest_str = str(quest_id)
    return DIMENSION_PRIORITY_BY_QUEST.get(quest_str, DEFAULT_DIMENSION_PRIORITY)


def get_quest_videos(quest_id: str) -> dict:
    """
    특정 퀘스트의 모든 영상 데이터를 반환합니다.
    
    Args:
        quest_id: 퀘스트 ID
    
    Returns:
        영상 맵 (차원명 -> [영상 리스트])
    """
    quest_int = int(quest_id) if isinstance(quest_id, str) else quest_id
    return QUEST_VIDEOS.get(quest_int, QUEST_VIDEOS[1])  # 기본값: Quest 1


def get_deep_dive_pattern(quest_id: str) -> dict:
    """
    특정 퀘스트의 Deep Dive 시나리오 패턴을 반환합니다.
    
    Args:
        quest_id: 퀘스트 ID
    
    Returns:
        패턴 데이터 (title, pattern, example_scenario, model_answer)
    """
    quest_str = str(quest_id)
    pattern = DEEP_DIVE_PATTERNS.get(quest_str)
    if not pattern:
        logger.warning(f"[quest_resources] Deep Dive Pattern for Quest {quest_id} not found")
        return {
            'title': '추가 학습 시나리오',
            'pattern': '[상황] 이전 문제의 핵심을 알고 있어도 더 복잡한 제약에서는 어떻게 대응하실 건가요?',
            'example_scenario': '실무 상황을 더 깊이 있게 분석하는 연습입니다.',
            'model_answer': '제시된 제약을 고려하여 설계 원칙을 응용하세요.',
        }
    return pattern


def validate_tail_question(tail_q: dict) -> tuple:
    """
    꼬리질문 데이터 구조를 검증합니다.
    
    Returns:
        (is_valid: bool, error_message: str)
    """
    required_fields = ['context', 'question', 'options']
    for field in required_fields:
        if field not in tail_q:
            return False, f"Required field missing: {field}"
    
    # context: 단어 수 ≤ 5
    context_words = tail_q['context'].split()
    if len(context_words) > 5:
        logger.warning(f"[validate_tail_question] context 단어 수 초과: {len(context_words)}")
    
    # question: [상황] 또는 [사례] 시작 권장
    if not any(tail_q['question'].startswith(prefix) for prefix in ['[상황]', '[사례]', '[문제]']):
        logger.warning(f"[validate_tail_question] question이 '[상황]' 등으로 시작하지 않음")
    
    # options: 정확히 1개 is_correct
    correct_count = sum(1 for opt in tail_q['options'] if opt.get('is_correct', False))
    if correct_count != 1:
        return False, f"Expected exactly 1 correct option, found {correct_count}"
    
    # 모든 옵션에 reason 필드 필수
    for i, opt in enumerate(tail_q['options']):
        if 'reason' not in opt:
            return False, f"Option {i} missing 'reason' field"
    
    return True, None


def validate_deep_dive(deep_dive: dict) -> tuple:
    """
    Deep Dive 데이터 구조를 검증합니다.
    
    Returns:
        (is_valid: bool, error_message: str)
    """
    required_fields = ['title', 'scenario', 'question', 'model_answer']
    for field in required_fields:
        if field not in deep_dive:
            return False, f"Required field missing: {field}"
    
    # scenario: 구체적/비추상적 확인
    if len(deep_dive['scenario']) < 20:
        logger.warning(f"[validate_deep_dive] scenario가 너무 짧음: {len(deep_dive['scenario'])} chars")
    
    return True, None


# ============================================================================
# 5. 폴백 데이터 생성 함수들
# ============================================================================

def generate_fallback_tail_question(context: str = "설계 원칙 확인") -> dict:
    """
    LLM이 tail_question을 생성하지 못할 때의 폴백 구조."""
    return {
        'context': context,
        'question': '[상황] 이전 설계에서 놓친 핵심 요소가 있다면 무엇일까요?',
        'options': [
            {
                'text': '설계 원칙의 실무 응용 및 제약 조건 고려',
                'is_correct': True,
                'reason': '설계만으로는 부족하며, 현업 환경(규모, 비용, 시간)의 제약을 반영해야 합니다.',
            },
            {
                'text': '코드 최적화 및 성능 튜닝',
                'is_correct': False,
                'reason': '성능은 부차적 고려사항입니다. 먼저 논리적 정확성과 일관성이 우선입니다.',
            },
            {
                'text': '학습 데이터 양 대폭 증가',
                'is_correct': False,
                'reason': '데이터 양의 증가만으로는 설계 오류를 보정할 수 없습니다.',
            },
            {
                'text': '더 복잡한 모델 아키텍처 도입',
                'is_correct': False,
                'reason': '복잡도가 높아지면 오히려 과적합과 유지보수 어려움이 증가합니다.',
            }
        ]
    }


def generate_fallback_deep_dive(quest_id: str) -> dict:
    """
    LLM이 deep_dive를 생성하지 못할 때의 폴백 구조."""
    pattern = get_deep_dive_pattern(quest_id)
    return {
        'title': pattern['title'],
        'scenario': pattern['example_scenario'],
        'question': pattern['pattern'],
        'model_answer': pattern['model_answer'],
    }


# ============================================================================
# 6. 하위호환성 유지 (learningResources.js 폴백 호출용)
# ============================================================================

def get_recommended_videos_legacy(quest_id: str, dimensions: dict, max_count: int = 3) -> list:
    """
    [폐기 예정] learningResources.js 호출과의 하위호환성을 위한 래퍼.
    프론트는 백엔드 recommended_videos를 먼저 사용해야 합니다.
    """
    try:
        quest_videos = get_quest_videos(quest_id)
        quest_int = int(quest_id) if isinstance(quest_id, str) else quest_id
        priority = get_dimension_priority(quest_id)
        
        # 취약 차원 정렬
        dim_ratios = []
        for dim in priority:
            d = dimensions.get(dim, {})
            pct = d.get('percentage', 100) if isinstance(d, dict) else 100
            dim_ratios.append((dim, pct))
        dim_ratios.sort(key=lambda x: x[1])
        
        candidates = []
        used_ids = set()
        
        # 취약 차원 순으로 선택
        for dim, _ in dim_ratios:
            if len(candidates) >= max_count:
                break
            videos = quest_videos.get(dim, [])
            if not isinstance(videos, list):
                videos = [videos]
            for video in videos:
                if len(candidates) >= max_count:
                    break
                if video['id'] not in used_ids:
                    candidates.append({**video, '_dim': dim})
                    used_ids.add(video['id'])
        
        # default로 보완
        default_videos = quest_videos.get('default', [])
        if not isinstance(default_videos, list):
            default_videos = [default_videos]
        for video in default_videos:
            if len(candidates) >= max_count:
                break
            if video['id'] not in used_ids:
                candidates.append({**video, '_dim': 'default'})
                used_ids.add(video['id'])
        
        return candidates
    except Exception as e:
        logger.error(f"[get_recommended_videos_legacy] Error: {e}")
        return []