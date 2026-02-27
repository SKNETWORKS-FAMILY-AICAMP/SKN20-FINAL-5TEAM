"""
BugHunt 면접 평가자 신뢰성 검증 - 평가 실행

BugHuntInterviewView의 최종 평가 턴(turn > MAX_TURNS)만 대상으로 검증.
기존 test data의 explanations를 대화 내용으로, RUBRICS를 채점 기준으로 사용.

60개 샘플 × 5회 반복 = 300회
"""
import os
import sys
import json
import time
import django
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from core.views.bughunt.bughunt_interview_view import BugHuntInterviewView

# 버그 유형별 채점 루브릭
# BugHuntInterviewView._build_system_prompt()에 그대로 전달됨
RUBRICS = {
    "data_leakage": {
        "core_concepts": ["train/test split 이전 fit", "테스트 정보 유출", "data leakage"],
        "mechanism_concepts": ["fit_transform 전체 데이터 적용", "통계 정보 누출", "test set 오염"],
        "application_concepts": ["split 후 fit/transform 분리", "pipeline 사용", "교차검증 주의"]
    },
    "label_imbalance": {
        "core_concepts": ["클래스 불균형", "majority class 편향", "accuracy 함정"],
        "mechanism_concepts": ["소수 클래스 무시", "weighted loss", "불균형 영향"],
        "application_concepts": ["f1-score 사용", "stratified split", "class_weight 설정"]
    },
    "overfitting": {
        "core_concepts": ["과적합", "train/val 성능 차이", "일반화 실패"],
        "mechanism_concepts": ["모델 복잡도", "훈련 데이터 암기", "분산 증가"],
        "application_concepts": ["dropout", "regularization", "early stopping"]
    },
    "off_by_one": {
        "core_concepts": ["인덱스 경계", "off-by-one", "범위 초과"],
        "mechanism_concepts": ["0-based indexing", "len()-1", "boundary condition"],
        "application_concepts": ["경계값 테스트", "range 함수 확인", "슬라이싱 주의"]
    },
    "null_pointer": {
        "core_concepts": ["None 체크 누락", "null 참조", "NoneType 오류"],
        "mechanism_concepts": ["None 반환 조건", "속성 접근 실패", "AttributeError"],
        "application_concepts": ["방어적 프로그래밍", "None 처리", "is not None 확인"]
    },
    "type_mismatch": {
        "core_concepts": ["타입 불일치", "형변환 필요", "TypeError"],
        "mechanism_concepts": ["암묵적 형변환", "문자열/숫자 혼용", "dtype 불일치"],
        "application_concepts": ["명시적 형변환", "isinstance 확인", "타입 검증"]
    },
    "metric_selection": {
        "core_concepts": ["잘못된 평가 지표", "회귀/분류 혼용", "metric 선택 오류"],
        "mechanism_concepts": ["accuracy vs f1 차이", "MSE vs MAE", "태스크별 적절한 지표"],
        "application_concepts": ["태스크 확인 후 지표 선택", "비즈니스 목적 고려", "다중 지표 사용"]
    },
    "feature_leakage": {
        "core_concepts": ["특성 누수", "타겟 정보 포함 피처", "미래 정보 사용"],
        "mechanism_concepts": ["피처 엔지니어링 시점", "타겟 파생 변수", "예측 불가능 피처"],
        "application_concepts": ["피처 의존성 분석", "시간 순서 주의", "pipeline 사용"]
    },
    "hyperparameter": {
        "core_concepts": ["하이퍼파라미터 오류", "학습률 문제", "배치 크기 부적절"],
        "mechanism_concepts": ["학습률 너무 크면 발산", "너무 작으면 수렴 지연", "배치 크기 영향"],
        "application_concepts": ["grid search", "learning rate scheduler", "validation 모니터링"]
    },
    "memory_leak": {
        "core_concepts": ["메모리 누수", "자원 해제 누락", "메모리 증가"],
        "mechanism_concepts": ["참조 유지", "generator vs list", "순환 참조"],
        "application_concepts": ["with 문 사용", "명시적 del", "메모리 프로파일링"]
    },
    "race_condition": {
        "core_concepts": ["경쟁 상태", "동기화 문제", "비결정적 결과"],
        "mechanism_concepts": ["공유 자원 접근", "스레드 안전성", "원자성 부재"],
        "application_concepts": ["Lock 사용", "동기화 메커니즘", "스레드 안전 자료구조"]
    },
    "api_timeout": {
        "core_concepts": ["타임아웃", "API 응답 지연", "네트워크 오류 처리"],
        "mechanism_concepts": ["timeout 설정 부재", "무한 대기", "에러 전파"],
        "application_concepts": ["try/except 사용", "timeout 파라미터 설정", "재시도 로직"]
    }
}


class InterviewEvaluationRunner:
    """면접 최종 평가 턴 실행기"""

    # BugHuntInterviewView.MAX_TURNS = 3 이므로 4로 설정하면 is_final_turn=True
    FINAL_TURN = 4

    def __init__(self, samples_file, output_file, num_trials=5):
        self.samples_file = samples_file
        self.output_file = output_file
        self.num_trials = num_trials
        self.factory = RequestFactory()
        self.view = BugHuntInterviewView.as_view()

    def _build_request_data(self, sample):
        """샘플에서 BugHuntInterviewView 요청 데이터 구성"""
        case_id = sample['case_id']
        rubric = RUBRICS.get(case_id, {})
        explanations = sample['explanations']

        # step_context: 코드 + 버그 정보 + 루브릭
        step_context = {
            "buggy_code": sample['steps'][0]['buggy_code'],
            "user_code": sample['userCodes'].get('2', ''),
            "error_info": {
                "type": sample['bug_type'],
                "description": sample['steps'][0]['instruction']
            },
            "interview_rubric": rubric
        }

        # conversation: explanations를 대화 형식으로 변환
        # 진단(1) + 설명(3)을 면접 답변으로 사용
        answer = "\n\n".join(filter(None, [
            explanations.get('1', ''),
            explanations.get('3', '')
        ]))
        conversation = [
            {"role": "assistant", "content": f"코드를 수정하셨는데, 버그의 원인과 수정 방법을 설명해주세요."},
            {"role": "user", "content": answer}
        ]

        return {
            "step_context": step_context,
            "conversation": conversation,
            "turn": self.FINAL_TURN,
            "stream": False
        }

    def run_single_evaluation(self, sample):
        """단일 샘플 최종 평가 실행"""
        request_data = self._build_request_data(sample)

        request = self.factory.post(
            '/api/bughunt/interview/',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        response = self.view(request)

        if response.status_code == 200:
            return response.data
        else:
            return {
                'error': True,
                'status_code': response.status_code,
                'message': str(response.data) if hasattr(response, 'data') else 'Unknown error'
            }

    def run_all_evaluations(self):
        """모든 샘플 반복 평가"""
        with open(self.samples_file, 'r', encoding='utf-8') as f:
            samples = json.load(f)

        results = []
        total = len(samples) * self.num_trials

        print(f"평가 시작: {len(samples)}개 샘플 × {self.num_trials}회 = {total}회")
        start = time.time()
        completed = 0

        for idx, sample in enumerate(samples):
            sample_id = sample['sample_id']
            print(f"\n[{idx+1}/{len(samples)}] {sample_id}")

            sample_result = {
                'sample_id': sample_id,
                'case_id': sample['case_id'],
                'quality_level': sample['quality_level'],
                'expected_score_range': sample['expected_score_range'],
                'trials': []
            }

            for trial in range(self.num_trials):
                try:
                    result = self.run_single_evaluation(sample)

                    if 'error' not in result:
                        trial_data = {
                            'trial': trial + 1,
                            # analyze_results.py와 호환되도록 thinking_score 키 사용
                            'thinking_score': result.get('score', 50),
                            'understanding_level': result.get('understanding_level', ''),
                            'matched_concepts': result.get('matched_concepts', []),
                            'weak_point': result.get('weak_point', '')
                        }
                        sample_result['trials'].append(trial_data)
                        completed += 1
                        print(f"  Trial {trial+1}: score={trial_data['thinking_score']} "
                              f"level={trial_data['understanding_level']}")
                    else:
                        print(f"  Trial {trial+1}: 오류 - {result.get('message', '')}")
                        sample_result['trials'].append({'trial': trial+1, 'error': True, 'message': result.get('message', '')})

                    time.sleep(0.5)

                except Exception as e:
                    print(f"  Trial {trial+1}: 예외 - {e}")
                    sample_result['trials'].append({'trial': trial+1, 'error': True, 'message': str(e)})

            results.append(sample_result)
            elapsed = time.time() - start
            print(f"  진행: {completed}/{total} ({completed/total*100:.1f}%) | {elapsed/60:.1f}분 경과")

        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'total_samples': len(samples),
                    'trials_per_sample': self.num_trials,
                    'total_evaluations': total,
                    'completed_evaluations': completed,
                    'elapsed_time_seconds': time.time() - start
                },
                'results': results
            }, f, ensure_ascii=False, indent=2)

        print(f"\n완료! 결과 저장: {self.output_file}")
        return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--trials', type=int, default=5)
    parser.add_argument('--quick', action='store_true', help='품질별 1개 샘플만 (5개)')
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    samples_file = base_dir / 'data' / 'new_validation_samples.json'
    output_file = base_dir / 'data' / 'evaluation_results.json'

    if args.quick:
        with open(samples_file, 'r', encoding='utf-8') as f:
            all_samples = json.load(f)
        test_samples = []
        for quality in ['excellent', 'good', 'average', 'poor', 'very_poor']:
            s = next((x for x in all_samples if x['quality_level'] == quality), None)
            if s:
                test_samples.append(s)
        quick_file = base_dir / 'data' / 'quick_test_samples.json'
        os.makedirs(quick_file.parent, exist_ok=True)
        with open(quick_file, 'w', encoding='utf-8') as f:
            json.dump(test_samples, f, ensure_ascii=False, indent=2)
        samples_file = quick_file
        output_file = base_dir / 'data' / 'quick_evaluation_results.json'

    runner = InterviewEvaluationRunner(samples_file, output_file, num_trials=args.trials)
    runner.run_all_evaluations()
