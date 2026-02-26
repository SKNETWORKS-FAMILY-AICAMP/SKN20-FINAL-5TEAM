"""
의사코드 트랙 LLM 신뢰성 검증 - 평가 실행

PseudocodeEvaluator를 직접 호출하여 각 샘플을 N회 반복 평가.
30개 샘플 × 5회 반복 = 150회 평가

실행:
  python run_evaluation.py           # 전체 150회
  python run_evaluation.py --quick   # 5샘플 × 3회 = 15회
  python run_evaluation.py --trials 3
"""
import os
import sys
import json
import time
import django
from pathlib import Path

# Django 설정
backend_dir = Path(__file__).resolve().parents[8] / 'backend'
sys.path.insert(0, str(backend_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.services.pseudocode_evaluator import (
    PseudocodeEvaluator,
    EvaluationRequest,
    EvaluationMode,
    LowEffortError,
    LLMTimeoutError,
    LLMUnavailableError,
)


class PseudocodeEvaluationRunner:

    def __init__(self, samples_file: Path, output_file: Path, num_trials: int = 5):
        self.samples_file = samples_file
        self.output_file = output_file
        self.num_trials = num_trials
        self.evaluator = PseudocodeEvaluator()

    def run_single(self, sample: dict) -> dict:
        """샘플 1개 평가 실행, 결과 반환"""
        req = EvaluationRequest(
            user_id='validation_test',
            detail_id=sample['quest_id'],
            pseudocode=sample['pseudocode'],
            quest_title=sample['quest_title'],
            tail_answer='',
            deep_answer='',
            mode=EvaluationMode.OPTION2_GPTONLY,
        )
        result = self.evaluator.evaluate(req)

        # 차원 점수 추출
        dimensions = result.feedback.get('dimensions', {})
        dim_scores = {
            dim: int(round(float(data.get('score', 0))))
            for dim, data in dimensions.items()
            if isinstance(data, dict)
        }

        return {
            'overall_score': int(result.final_score),
            'dimension_scores': dim_scores,
            'grade': result.grade,
        }

    def run_all(self) -> list:
        with open(self.samples_file, 'r', encoding='utf-8') as f:
            samples = json.load(f)

        results = []
        total = len(samples) * self.num_trials
        completed = 0
        start = time.time()

        print(f"평가 시작: {len(samples)}개 샘플 × {self.num_trials}회 = {total}회")

        for idx, sample in enumerate(samples):
            sample_id = sample['sample_id']
            print(f"\n[{idx+1}/{len(samples)}] {sample_id}")

            sample_result = {
                'sample_id': sample_id,
                'quest_id': sample['quest_id'],
                'quest_title': sample['quest_title'],
                'quality_level': sample['quality_level'],
                'expected_score_range': sample['expected_score_range'],
                'trials': [],
            }

            for trial in range(self.num_trials):
                try:
                    data = self.run_single(sample)
                    sample_result['trials'].append({
                        'trial': trial + 1,
                        'overall_score': data['overall_score'],
                        'dimension_scores': data['dimension_scores'],
                        'grade': data['grade'],
                    })
                    completed += 1
                    print(f"  Trial {trial+1}: score={data['overall_score']} grade={data['grade']}")
                except (LowEffortError, LLMTimeoutError, LLMUnavailableError) as e:
                    print(f"  Trial {trial+1}: LLM 오류 - {e}")
                    sample_result['trials'].append({'trial': trial+1, 'error': True, 'message': str(e)})
                except Exception as e:
                    print(f"  Trial {trial+1}: 예외 - {e}")
                    sample_result['trials'].append({'trial': trial+1, 'error': True, 'message': str(e)})

                time.sleep(0.5)

            results.append(sample_result)
            elapsed = time.time() - start
            print(f"  진행: {completed}/{total} ({completed/total*100:.1f}%) | {elapsed/60:.1f}분 경과")

        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'total_samples': len(samples),
                    'trials_per_sample': self.num_trials,
                    'total_evaluations': total,
                    'completed_evaluations': completed,
                    'elapsed_seconds': round(time.time() - start, 1),
                },
                'results': results,
            }, f, ensure_ascii=False, indent=2)

        print(f"\n완료! 결과 저장: {self.output_file}")
        return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--trials', type=int, default=5)
    parser.add_argument('--quick', action='store_true', help='품질별 1개씩 (5개) 빠른 테스트')
    args = parser.parse_args()

    base = Path(__file__).resolve().parent

    if args.quick:
        src = base / 'data' / 'validation_samples_quick.json'
        if not src.exists():
            src = base / 'data' / 'validation_samples.json'
        # 품질별 1개씩만 추출
        with open(src, 'r', encoding='utf-8') as f:
            all_samples = json.load(f)
        test_samples = []
        for quality in ['excellent', 'good', 'average', 'poor', 'very_poor']:
            s = next((x for x in all_samples if x['quality_level'] == quality), None)
            if s:
                test_samples.append(s)
        quick_file = base / 'data' / 'quick_test_samples.json'
        with open(quick_file, 'w', encoding='utf-8') as f:
            json.dump(test_samples, f, ensure_ascii=False, indent=2)
        samples_file = quick_file
        output_file = base / 'data' / 'quick_evaluation_results.json'
        trials = min(args.trials, 3)
    else:
        samples_file = base / 'data' / 'validation_samples.json'
        output_file = base / 'data' / 'evaluation_results.json'
        trials = args.trials

    runner = PseudocodeEvaluationRunner(samples_file, output_file, num_trials=trials)
    runner.run_all()
