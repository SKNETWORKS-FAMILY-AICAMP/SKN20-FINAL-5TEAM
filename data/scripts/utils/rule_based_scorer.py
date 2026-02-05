"""
규칙 기반 Bug Hunt 평가 점수 계산

LLM 평가와 비교하기 위한 객관적 지표
"""
import re


class RuleBasedScorer:
    """규칙 기반 점수 계산기"""

    # 버그 유형별 키워드
    BUG_KEYWORDS = {
        "data_leakage": ["data leakage", "데이터 누수", "train_test_split", "스케일링", "fit_transform", "leakage"],
        "label_imbalance": ["imbalance", "불균형", "f1", "recall", "precision", "weighted", "accuracy"],
        "overfitting": ["overfitting", "과적합", "validation", "검증", "early stopping"],
        "off_by_one": ["off-by-one", "인덱스", "index", "boundary", "경계", "범위"],
        "null_pointer": ["null", "none", "체크", "check", "예외", "exception"],
        "type_mismatch": ["type", "타입", "형변환", "str", "int", "casting"],
        "metric_selection": ["metric", "지표", "평가", "mse", "r2", "accuracy", "regression"],
        "feature_leakage": ["feature", "피처", "누수", "미래", "정보", "leakage"],
        "hyperparameter": ["hyperparameter", "하이퍼파라미터", "learning rate", "학습률"],
        "memory_leak": ["memory", "메모리", "누수", "leak", "해제", "generator"],
        "race_condition": ["race", "경쟁", "동기화", "lock", "thread", "멀티스레드"],
        "api_timeout": ["timeout", "타임아웃", "exception", "예외", "try", "except"]
    }

    def __init__(self):
        pass

    def score_sample(self, sample):
        """
        샘플에 대한 규칙 기반 점수 계산

        점수 구성:
        - 버그 원인 키워드 언급: 0-30점
        - 수정 코드 적절성: 0-25점
        - 설명 충실도: 0-25점
        - 부작용 고려 언급: 0-20점
        """
        case_id = sample['case_id']
        explanations = sample['explanations']
        user_codes = sample['userCodes']

        # 모든 설명 텍스트 결합
        all_text = ' '.join([
            explanations.get('1', ''),
            explanations.get('2', ''),
            explanations.get('3', '')
        ]).lower()

        score = 0

        # 1. 버그 원인 키워드 언급 (0-30점)
        score += self._score_bug_keyword_mention(case_id, all_text)

        # 2. 수정 코드 적절성 (0-25점)
        score += self._score_code_quality(sample)

        # 3. 설명 충실도 (0-25점)
        score += self._score_explanation_completeness(explanations)

        # 4. 부작용 고려 언급 (0-20점)
        score += self._score_side_effect_consideration(all_text)

        return min(100, score)  # 최대 100점

    def _score_bug_keyword_mention(self, case_id, text):
        """버그 원인 키워드 언급 여부 (0-30점)"""
        keywords = self.BUG_KEYWORDS.get(case_id, [])

        matched = 0
        for keyword in keywords:
            if keyword in text:
                matched += 1

        # 키워드 매칭 비율에 따라 점수
        if len(keywords) == 0:
            return 15  # 기본 점수

        match_ratio = matched / len(keywords)
        if match_ratio >= 0.5:
            return 30
        elif match_ratio >= 0.3:
            return 20
        elif match_ratio >= 0.1:
            return 10
        else:
            return 0

    def _score_code_quality(self, sample):
        """수정 코드 적절성 (0-25점)"""
        original_code = sample['steps'][1]['buggy_code']
        fixed_code = sample['userCodes'].get('2', '')

        score = 0

        # 코드 변경이 있는가?
        if fixed_code != original_code:
            score += 10

        # 변경 라인 수가 적절한가? (1-10줄)
        original_lines = len(original_code.split('\n'))
        fixed_lines = len(fixed_code.split('\n'))
        line_diff = abs(fixed_lines - original_lines)

        if 1 <= line_diff <= 10:
            score += 10
        elif line_diff == 0:
            score += 0  # 변경 없음
        else:
            score += 5  # 너무 많은 변경

        # 주석이 있는가?
        if '#' in fixed_code or '"""' in fixed_code:
            score += 5

        return score

    def _score_explanation_completeness(self, explanations):
        """설명 충실도 (0-25점)"""
        score = 0

        # Step 1: 진단 설명
        step1 = explanations.get('1', '')
        if len(step1) >= 50:
            score += 10
        elif len(step1) >= 20:
            score += 5

        # Step 3: 수정 설명
        step3 = explanations.get('3', '')
        if len(step3) >= 100:
            score += 15
        elif len(step3) >= 50:
            score += 10
        elif len(step3) >= 20:
            score += 5

        return score

    def _score_side_effect_consideration(self, text):
        """부작용 고려 언급 (0-20점)"""
        side_effect_keywords = [
            '부작용', 'side effect', '영향', 'impact',
            '안전', 'safe', '문제없', '재발 방지',
            '경계', 'boundary', '예외', 'exception',
            '성능', 'performance', '메모리', 'memory'
        ]

        matched = sum(1 for kw in side_effect_keywords if kw in text)

        if matched >= 3:
            return 20
        elif matched >= 2:
            return 15
        elif matched >= 1:
            return 10
        else:
            return 0

    def score_all_samples(self, samples):
        """모든 샘플에 대한 규칙 기반 점수 계산"""
        results = []

        for sample in samples:
            score = self.score_sample(sample)
            results.append({
                'sample_id': sample['sample_id'],
                'case_id': sample['case_id'],
                'quality_level': sample['quality_level'],
                'rule_based_score': score,
                'expected_score_range': sample['expected_score_range']
            })

        return results


if __name__ == "__main__":
    import json
    import os

    print("🎯 규칙 기반 점수 계산 테스트...")

    # 샘플 데이터 로드
    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'validation')
    samples_file = os.path.join(data_dir, 'bug_hunt_validation_samples.json')

    with open(samples_file, 'r', encoding='utf-8') as f:
        samples = json.load(f)

    scorer = RuleBasedScorer()
    results = scorer.score_all_samples(samples)

    # 결과 저장
    output_file = os.path.join(data_dir, 'rule_based_scores.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"✅ 규칙 기반 점수 계산 완료!")
    print(f"📁 저장 위치: {output_file}")

    # 통계 출력
    print(f"\n📊 점수 분포:")
    for quality in ['excellent', 'good', 'average', 'poor', 'very_poor']:
        quality_results = [r for r in results if r['quality_level'] == quality]
        if quality_results:
            avg_score = sum(r['rule_based_score'] for r in quality_results) / len(quality_results)
            print(f"   {quality:12s}: 평균 {avg_score:.1f}점")
