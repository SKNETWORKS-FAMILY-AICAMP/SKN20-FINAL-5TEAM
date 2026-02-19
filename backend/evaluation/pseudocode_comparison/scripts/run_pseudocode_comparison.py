import os
import sys
import json
import time
import re
import django
from pathlib import Path
from typing import Dict, Any

# Django 설정 로드
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent.parent
sys.path.insert(0, str(backend_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

try:
    from backend.evaluation.model_comparison.scripts.model_evaluator import get_evaluator
except ImportError:
    try:
        from evaluation.model_comparison.scripts.model_evaluator import get_evaluator
    except ImportError:
        def get_evaluator(model): raise ImportError("Evaluator not found")

# 실제 PSEUDO CODE 평가 로직에서 프롬프트 가져오기 (고립을 위해 하드코딩 권장되나 여기선 참조 시도)
try:
    from core.views.pseudocode_evaluation import SYSTEM_PROMPT, MISSION_BLUEPRINTS
except ImportError:
    # 참조가 실패할 경우를 대비한 백업 (실제 파일 내용과 일치해야 함)
    SYSTEM_PROMPT = "당신은 AI 기반 데이터 과학 설계 평가 전문가입니다..."
    MISSION_BLUEPRINTS = {"1": {"mission_goal": "데이터 전처리 누수 방지", "critical_constraints": [], "required_keywords": []}}

class PseudocodeComparisonRunner:
    def __init__(self, samples_file, output_dir, models, num_trials=3):
        self.samples_file = Path(samples_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.models = models
        self.num_trials = num_trials
        self.evaluators = {}

        for model in models:
            try:
                self.evaluators[model] = get_evaluator(model)
                print(f"✅ {model} evaluator ready")
            except Exception as e:
                print(f"❌ {model} initialization failed: {e}")

    def create_prompt(self, sample):
        quest_id = sample['quest_id']
        quest_title = sample['quest_title']
        pseudocode = sample['pseudocode']
        
        blueprint = MISSION_BLUEPRINTS.get(quest_id, MISSION_BLUEPRINTS.get("1"))
        
        user_prompt = f"""
# [Evaluation Context: Mission Blueprint]
- Goal: {blueprint.get('mission_goal', '전처리')}
- Critical Constraints: {", ".join(blueprint.get('critical_constraints', []))}
- Required Keywords: {", ".join(blueprint.get('required_keywords', []))}

# [User Input]
- Title: {quest_title}
- Pseudocode: {pseudocode}
- Diagnostic Context: N/A

# [Task]
위 [Mission Blueprint]의 제약 사항을 얼마나 충실히 설계에 반영했는지 평가하세요.
- AI 점수는 총 85점 만점으로 채점합니다. (지표별 합산)
- 점수 결과에 따라 맞춤형 MCQ(tail_question or deep_dive)를 생성하세요. 
- 입력을 기반으로 실행 가능한 Python 코드로 변환하세요.
"""
        return SYSTEM_PROMPT, user_prompt

    def run_all(self):
        with open(self.samples_file, 'r', encoding='utf-8') as f:
            samples = json.load(f)

        all_results = {}
        for model_name in self.models:
            print(f"\n🚀 Testing Model: {model_name}")
            model_evals = []
            evaluator = self.evaluators.get(model_name)
            if not evaluator: continue

            for sample in samples:
                print(f"  - Sample: {sample['sample_id']} ({sample['quality_level']})")
                trials = []
                system_p, user_p = self.create_prompt(sample)
                
                for i in range(self.num_trials):
                    res = evaluator.evaluate(system_p, user_p)
                    if res['success']:
                        score = res['result'].get('overall_score', 0)
                        print(f"    Trial {i+1}: Score={score} ({res['time']:.1f}s)")
                        trials.append(res)
                    else:
                        print(f"    Trial {i+1}: FAILED - {res.get('error')}")
                    time.sleep(1)
                
                model_evals.append({
                    "sample_id": sample['sample_id'],
                    "quality_level": sample['quality_level'],
                    "expected_range": sample['expected_score_range'],
                    "trials": trials
                })
            
            all_results[model_name] = {
                "model": model_name,
                "evaluations": model_evals,
                "stats": evaluator.get_stats()
            }
            
            # Save intermediate result
            model_filename = model_name.replace("/", "_").replace("-", "_")
            with open(self.output_dir / f"PSEUDOCODE_{model_filename}_results.json", 'w', encoding='utf-8') as f:
                json.dump(all_results[model_name], f, ensure_ascii=False, indent=2)

        # Final Summary
        with open(self.output_dir / "PSEUDOCODE_comparison_summary.json", 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ All tests complete. Results saved in {self.output_dir}")

if __name__ == "__main__":
    # [2026-02-15] GPT vs Gemini vs Llama 3자 대결 설정
    models_to_test = [
        'gpt-4o-mini', 
        'gemini-1.5-flash', 
        'llama-3.3-70b-versatile'
    ]
    samples_path = backend_dir / 'evaluation' / 'pseudocode_comparison' / 'samples' / 'pseudocode_validation_samples.json'
    out_path = backend_dir / 'evaluation' / 'pseudocode_comparison' / 'results'
    
    runner = PseudocodeComparisonRunner(samples_path, out_path, models_to_test, num_trials=2)
    runner.run_all()
