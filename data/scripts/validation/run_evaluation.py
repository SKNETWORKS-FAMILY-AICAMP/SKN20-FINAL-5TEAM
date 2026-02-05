"""
Bug Hunt 평가 실행 스크립트

60개 샘플 × 5회 반복 = 300회 평가 수행
"""
import os
import sys
import json
import time
import django
from pathlib import Path

# Django 설정 로드
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from core.views.ai_view import BugHuntEvaluationView


class EvaluationRunner:
    """평가 실행기"""

    def __init__(self, samples_file, output_file, num_trials=5):
        self.samples_file = samples_file
        self.output_file = output_file
        self.num_trials = num_trials
        self.factory = RequestFactory()
        self.view = BugHuntEvaluationView.as_view()

    def run_single_evaluation(self, sample):
        """단일 샘플에 대한 평가 실행"""
        # Django request 객체 생성
        request = self.factory.post(
            '/api/ai/bug-hunt-evaluation/',
            data=json.dumps({
                'missionTitle': sample['missionTitle'],
                'steps': sample['steps'],
                'explanations': sample['explanations'],
                'userCodes': sample['userCodes'],
                'performance': sample['performance']
            }),
            content_type='application/json'
        )

        # 평가 실행
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
        """모든 샘플에 대해 반복 평가 실행"""
        # 샘플 로드
        with open(self.samples_file, 'r', encoding='utf-8') as f:
            samples = json.load(f)

        results = []
        total_evaluations = len(samples) * self.num_trials

        print(f"🚀 평가 시작: {len(samples)}개 샘플 × {self.num_trials}회 = {total_evaluations}회")
        print(f"⏱️  예상 소요 시간: {total_evaluations * 3 / 60:.1f}분")

        start_time = time.time()
        completed = 0

        for sample_idx, sample in enumerate(samples):
            sample_id = sample['sample_id']
            print(f"\n[{sample_idx + 1}/{len(samples)}] {sample_id} 평가 중...")

            sample_results = {
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
                        trial_result = {
                            'trial': trial + 1,
                            'thinking_pass': result.get('thinking_pass', False),
                            'code_risk': result.get('code_risk', 50),
                            'thinking_score': result.get('thinking_score', 50),
                            'summary': result.get('총평', ''),
                            'step_feedbacks': result.get('step_feedbacks', [])
                        }

                        sample_results['trials'].append(trial_result)
                        completed += 1

                        print(f"  Trial {trial + 1}: 사고점수={trial_result['thinking_score']} "
                              f"위험도={trial_result['code_risk']} "
                              f"통과={'✅' if trial_result['thinking_pass'] else '❌'}")
                    else:
                        print(f"  Trial {trial + 1}: ❌ 오류 - {result.get('message', 'Unknown')}")
                        sample_results['trials'].append({
                            'trial': trial + 1,
                            'error': True,
                            'message': result.get('message', 'Unknown error')
                        })

                    # API Rate Limiting 방지
                    time.sleep(0.5)

                except Exception as e:
                    print(f"  Trial {trial + 1}: ❌ 예외 발생 - {str(e)}")
                    sample_results['trials'].append({
                        'trial': trial + 1,
                        'error': True,
                        'message': str(e)
                    })

            results.append(sample_results)

            # 진행률 표시
            progress = (completed / total_evaluations) * 100
            elapsed = time.time() - start_time
            print(f"  진행률: {completed}/{total_evaluations} ({progress:.1f}%) | "
                  f"경과 시간: {elapsed / 60:.1f}분")

        # 결과 저장
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'total_samples': len(samples),
                    'trials_per_sample': self.num_trials,
                    'total_evaluations': total_evaluations,
                    'completed_evaluations': completed,
                    'elapsed_time_seconds': time.time() - start_time
                },
                'results': results
            }, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 평가 완료!")
        print(f"📁 결과 저장: {self.output_file}")
        print(f"⏱️  총 소요 시간: {(time.time() - start_time) / 60:.1f}분")

        return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Bug Hunt 평가 실행')
    parser.add_argument('--trials', type=int, default=5, help='샘플당 반복 횟수 (기본: 5)')
    parser.add_argument('--quick', action='store_true', help='빠른 테스트 (각 품질별 1개 샘플만)')
    args = parser.parse_args()

    # 파일 경로
    data_dir = Path(__file__).resolve().parent.parent.parent / 'data' / 'validation'
    samples_file = data_dir / 'bug_hunt_validation_samples.json'
    output_file = data_dir / 'evaluation_results.json'

    # Quick 모드: 테스트용 (5개 샘플만)
    if args.quick:
        print("⚡ Quick 모드: 품질별 1개 샘플만 평가")
        with open(samples_file, 'r', encoding='utf-8') as f:
            all_samples = json.load(f)

        # 각 품질 레벨에서 첫 번째 샘플만 선택
        test_samples = []
        for quality in ['excellent', 'good', 'average', 'poor', 'very_poor']:
            sample = next((s for s in all_samples if s['quality_level'] == quality), None)
            if sample:
                test_samples.append(sample)

        # 임시 파일로 저장
        test_samples_file = data_dir / 'test_samples.json'
        with open(test_samples_file, 'w', encoding='utf-8') as f:
            json.dump(test_samples, f, ensure_ascii=False, indent=2)

        samples_file = test_samples_file
        output_file = data_dir / 'test_evaluation_results.json'

    # 평가 실행
    runner = EvaluationRunner(samples_file, output_file, num_trials=args.trials)
    runner.run_all_evaluations()
