"""
시스템 아키텍처 트랙 LLM 신뢰성 검증 - 평가 실행

generate_rubric_prompt() + OpenAI 직접 호출로 평가.
(architecture_view.py의 RubricEvaluationView와 동일한 로직)

20개 샘플 × 5회 반복 = 100회 평가

실행:
  python run_evaluation.py           # 전체 100회
  python run_evaluation.py --quick   # 5샘플 × 3회 = 15회
  python run_evaluation.py --trials 3
"""
import os
import sys
import json
import time
import re
import django
from pathlib import Path

# Django 설정
backend_dir = Path(__file__).resolve().parents[8] / 'backend'
sys.path.insert(0, str(backend_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
import openai
from core.views.architecture.architecture_view import generate_rubric_prompt


class ArchitectureEvaluationRunner:

    def __init__(self, samples_file: Path, output_file: Path, num_trials: int = 5):
        self.samples_file = samples_file
        self.output_file = output_file
        self.num_trials = num_trials
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def run_single(self, sample: dict) -> dict:
        """샘플 1개 평가 실행, 결과 반환"""
        system_message, prompt = generate_rubric_prompt(
            problem=sample['problem'],
            architecture_context=sample['architecture_context'],
            user_explanation=sample['user_explanation'],
            deep_dive_qna=sample['deep_dive_qna'],
        )

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_completion_tokens=3000,
        )
        content = response.choices[0].message.content.strip()

        # JSON 파싱
        match = re.search(r'\{[\s\S]*\}', content)
        if not match:
            return {'error': True, 'message': 'JSON 파싱 실패', 'raw': content[:200]}

        result = json.loads(match.group())

        # 전체 점수 계산 (각 축 점수 × 가중치)
        evaluations = result.get('evaluations', [])
        weighted_sum = 0.0
        axis_scores = {}
        for ev in evaluations:
            weight = ev.get('weight', 0)
            score = ev.get('score', 0)
            axis = ev.get('axis', '')
            weighted_sum += score * weight / 100
            axis_scores[axis] = {
                'score': score,
                'grade': ev.get('grade', ''),
                'weight': weight,
            }

        overall_score = int(round(weighted_sum))

        return {
            'overall_score': overall_score,
            'axis_scores': axis_scores,
            'overall_grade': result.get('overallGrade', ''),
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
                'problem_id': sample['problem_id'],
                'quality_level': sample['quality_level'],
                'expected_score_range': sample['expected_score_range'],
                'trials': [],
            }

            for trial in range(self.num_trials):
                try:
                    data = self.run_single(sample)
                    if 'error' in data:
                        print(f"  Trial {trial+1}: 오류 - {data.get('message', '')}")
                        sample_result['trials'].append({'trial': trial+1, 'error': True, 'message': data.get('message', '')})
                    else:
                        sample_result['trials'].append({
                            'trial': trial + 1,
                            'overall_score': data['overall_score'],
                            'axis_scores': data['axis_scores'],
                            'overall_grade': data['overall_grade'],
                        })
                        completed += 1
                        print(f"  Trial {trial+1}: score={data['overall_score']} grade={data['overall_grade']}")
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

    runner = ArchitectureEvaluationRunner(samples_file, output_file, num_trials=trials)
    runner.run_all()
