"""
다중 모델 비교 평가 실행 스크립트

여러 LLM 모델을 동일한 샘플로 평가하고 결과를 비교
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

from model_evaluator import get_evaluator


class ModelComparisonRunner:
    """다중 모델 비교 평가 실행기"""

    def __init__(self, samples_file, output_dir, models, num_trials=5):
        self.samples_file = samples_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.models = models
        self.num_trials = num_trials
        self.evaluators = {}

        # 각 모델별 evaluator 생성
        for model in models:
            try:
                self.evaluators[model] = get_evaluator(model)
                print(f"✅ {model} evaluator 초기화 완료")
            except Exception as e:
                print(f"❌ {model} evaluator 초기화 실패: {e}")

    def create_evaluation_prompt(self, sample):
        """샘플 데이터로부터 평가 프롬프트 생성"""
        mission_title = sample['missionTitle']
        steps = sample['steps']
        explanations = sample['explanations']
        user_codes = sample['userCodes']
        performance = sample['performance']

        # 각 단계별 데이터 구성
        step_context = []
        for idx, s in enumerate(steps):
            step_num = idx + 1
            original_code = s.get('buggy_code', '')
            modified_code = user_codes.get(str(step_num), '')
            explanation = explanations.get(str(step_num), '설명 없음')

            step_context.append(f"""### Step {step_num}: {s.get('title', s.get('bug_type', ''))}
- 문제 설명: {s.get('instruction', '')}

- 원본 버그 코드:
```python
{original_code}
```

- 사용자 수정 코드:
```python
{modified_code}
```

- 사용자 설명: {explanation}""")

        step_context_str = '\n\n'.join(step_context)

        system_message = """너는 디버깅 사고를 평가하는 시스템이다.
정오답이 아니라 "디버깅 사고의 질"을 평가한다.
냉철하고 객관적으로 평가하되, 교육적인 관점을 유지한다."""

        prompt = f"""## 평가 대상 데이터

미션: {mission_title}

[사용자 성과 지표]
- 퀴즈 오답 횟수: {performance.get('quizIncorrectCount', 0)}회
- 코드 제출 실패: {performance.get('codeSubmitFailCount', 0)}회
- 힌트 사용 횟수: {performance.get('hintCount', 0)}회
- 총 소요 시간: {performance.get('totalDebugTime', 0)}초

{step_context_str}

## 평가 단계

1. 사고 방향 평가 (모델 A 관점)
   다음 항목들을 검토한다:
   - 원인 언급 여부: 사용자가 버그의 근본 원인을 언급했는가?
   - 원인-수정 일치 여부: 언급한 원인과 실제 코드 수정이 일치하는가?
   - 부작용 고려 여부: 수정으로 인한 부작용을 고려했는가?
   - 수정 범위 적절성: 필요한 부분만 수정했는가, 과도하게 수정했는가?
   - 설명-코드 일관성: 설명 내용과 실제 코드 변경이 일관되는가?
   → 주요 항목(원인 언급, 원인-수정 일치, 설명-코드 일관성) 충족 시 통과

2. 코드 위험 평가 (모델 B 관점)
   다음 요소를 분석한다:
   - 변경 라인 수: 얼마나 많은 코드를 변경했는가?
   - 조건문/예외 처리 변화: 로직 흐름에 영향을 주는 변경이 있는가?
   - 기존 로직 훼손 여부: 원래 동작해야 할 부분을 망가뜨렸는가?
   → 위험 점수 0~100 (0: 매우 안전, 100: 매우 위험)

3. 사고 연속 점수 평가 (모델 C 관점)
   좋은 디버깅 답변의 특성과 비교한다:
   - 논리적 흐름: 문제 인식 → 원인 분석 → 해결책 제시 순서
   - 근거 제시: 왜 그렇게 수정했는지 이유를 설명했는가?
   - 명확성: 설명이 명확하고 이해하기 쉬운가?
   - 기술적 정확성: 사용한 용어와 개념이 정확한가?
   (참고: 오답이나 힌트 사용이 많다면, 사고의 자립성을 낮게 평가하라)
   → 사고 점수 0~100

4. **각 단계별 설명 피드백 생성 (필수)**
   위에 제시된 각 Step의 "사용자 설명"을 개별적으로 평가하여 피드백을 생성하라.
   각 피드백은 한 문단으로 작성하되, 다음 내용을 포함:
   - 설명 품질 점수 (0-100점)
   - 잘한 점 (구체적으로)
   - 부족한 점 (구체적으로)
   - 개선 방향 제안

   예시:
   - 설명이 부실한 경우: "설명 품질: 20/100. 버그 발견 의도는 있으나 구체성이 부족합니다. '어떤 변수'가 '왜' 문제인지, '어떻게' 수정했는지 명확히 작성해주세요."
   - 설명이 양호한 경우: "설명 품질: 75/100. 원인과 해결책을 논리적으로 연결했습니다. 다만 수정으로 인한 부작용 고려까지 추가하면 더욱 완벽합니다."

## 출력 형식
**반드시 아래 JSON 형식만 출력하라. 다른 텍스트는 포함하지 마라.**

{{
  "thinking_pass": true,
  "code_risk": 45,
  "thinking_score": 70,
  "총평": "전체 평가를 요약하여 시니어 엔지니어 입장에서 설명하고 존댓말로 입력",
  "step_feedbacks": [
    {{
      "step": 1,
      "feedback": "실제 Step 1 사용자 설명을 분석한 구체적인 피드백 (점수 포함, 한 문단)"
    }},
    {{
      "step": 2,
      "feedback": "실제 Step 2 사용자 설명을 분석한 구체적인 피드백 (점수 포함, 한 문단)"
    }},
    {{
      "step": 3,
      "feedback": "실제 Step 3 사용자 설명을 분석한 구체적인 피드백 (점수 포함, 한 문단)"
    }}
  ]
}}

**중요**: step_feedbacks 배열은 반드시 3개 항목을 포함해야 하며, 각 step에 대한 실제 평가 내용을 작성해야 한다.
"""

        return system_message, prompt

    def run_single_evaluation(self, model, sample, trial_num):
        """단일 모델로 단일 샘플 평가"""
        evaluator = self.evaluators.get(model)
        if not evaluator:
            return {'error': True, 'message': f'No evaluator for {model}'}

        system_message, prompt = self.create_evaluation_prompt(sample)

        try:
            result = evaluator.evaluate(system_message, prompt)

            if result['success']:
                eval_result = result['result']
                return {
                    'trial': trial_num,
                    'thinking_pass': eval_result.get('thinking_pass', False),
                    'code_risk': eval_result.get('code_risk', 50),
                    'thinking_score': eval_result.get('thinking_score', 50),
                    'summary': eval_result.get('총평', ''),
                    'step_feedbacks': eval_result.get('step_feedbacks', []),
                    'tokens': result.get('tokens', {}),
                    'cost': result.get('cost', 0),
                    'time': result.get('time', 0)
                }
            else:
                return {
                    'trial': trial_num,
                    'error': True,
                    'message': result.get('error', 'Unknown error'),
                    'time': result.get('time', 0)
                }

        except Exception as e:
            return {
                'trial': trial_num,
                'error': True,
                'message': str(e)
            }

    def run_all_evaluations(self):
        """모든 모델로 모든 샘플 평가"""
        # 샘플 로드
        with open(self.samples_file, 'r', encoding='utf-8') as f:
            samples = json.load(f)

        total_evaluations = len(samples) * len(self.models) * self.num_trials

        print(f"\n🚀 모델 비교 평가 시작")
        print(f"   - 샘플 수: {len(samples)}")
        print(f"   - 모델 수: {len(self.models)}")
        print(f"   - 반복 횟수: {self.num_trials}")
        print(f"   - 총 평가 횟수: {total_evaluations}")
        print(f"   - 평가 모델: {', '.join(self.models)}")

        start_time = time.time()
        completed = 0

        # 모델별 결과 저장
        all_results = {}

        for model in self.models:
            print(f"\n{'='*60}")
            print(f"🤖 모델: {model}")
            print(f"{'='*60}")

            model_results = []

            for sample_idx, sample in enumerate(samples):
                sample_id = sample['sample_id']
                print(f"\n[{sample_idx + 1}/{len(samples)}] {sample_id} 평가 중...")

                sample_result = {
                    'sample_id': sample_id,
                    'case_id': sample['case_id'],
                    'quality_level': sample['quality_level'],
                    'expected_score_range': sample['expected_score_range'],
                    'trials': []
                }

                for trial in range(self.num_trials):
                    result = self.run_single_evaluation(model, sample, trial + 1)
                    sample_result['trials'].append(result)

                    if 'error' not in result:
                        print(f"  Trial {trial + 1}: 사고점수={result['thinking_score']} "
                              f"위험도={result['code_risk']} "
                              f"통과={'✅' if result['thinking_pass'] else '❌'} "
                              f"시간={result['time']:.1f}s")
                        completed += 1
                    else:
                        print(f"  Trial {trial + 1}: ❌ 오류 - {result.get('message', 'Unknown')}")

                    # Rate limiting
                    time.sleep(0.5)

                model_results.append(sample_result)

                # 진행률 표시
                progress = (completed / total_evaluations) * 100
                elapsed = time.time() - start_time
                print(f"  진행률: {completed}/{total_evaluations} ({progress:.1f}%) | "
                      f"경과: {elapsed / 60:.1f}분")

            # 모델별 결과 저장
            all_results[model] = {
                'model_name': model,
                'results': model_results,
                'stats': self.evaluators[model].get_stats()
            }

            # 개별 모델 결과 파일 저장
            model_file = self.output_dir / f'{model.replace("/", "_")}_results.json'
            with open(model_file, 'w', encoding='utf-8') as f:
                json.dump(all_results[model], f, ensure_ascii=False, indent=2)

            print(f"\n✅ {model} 평가 완료")
            print(f"   📁 저장: {model_file}")
            print(f"   📊 통계: {self.evaluators[model].get_stats()}")

        # 전체 결과 저장
        summary_file = self.output_dir / 'model_comparison_results.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'total_samples': len(samples),
                    'models': self.models,
                    'trials_per_sample': self.num_trials,
                    'total_evaluations': total_evaluations,
                    'completed_evaluations': completed,
                    'elapsed_time_seconds': time.time() - start_time
                },
                'model_results': all_results
            }, f, ensure_ascii=False, indent=2)

        print(f"\n{'='*60}")
        print(f"✅ 전체 모델 비교 평가 완료!")
        print(f"{'='*60}")
        print(f"📁 결과 저장: {summary_file}")
        print(f"⏱️  총 소요 시간: {(time.time() - start_time) / 60:.1f}분")

        return all_results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='다중 모델 비교 평가 실행')
    parser.add_argument('--trials', type=int, default=5, help='샘플당 반복 횟수 (기본: 5)')
    parser.add_argument('--quick', action='store_true', help='빠른 테스트 (각 품질별 1개 샘플만)')
    parser.add_argument('--models', nargs='+',
                       default=['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo', 'Llama-3.1-70B', 'Mixtral-8x7B'],
                       help='비교할 모델 목록')
    args = parser.parse_args()

    # 파일 경로
    data_dir = Path(__file__).resolve().parent.parent.parent / 'data' / 'validation'
    samples_file = data_dir / 'bug_hunt_validation_samples.json'
    output_dir = data_dir / 'model_comparison'

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

    # 평가 실행
    runner = ModelComparisonRunner(samples_file, output_dir, models=args.models, num_trials=args.trials)
    runner.run_all_evaluations()
