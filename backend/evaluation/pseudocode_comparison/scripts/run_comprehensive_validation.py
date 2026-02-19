"""
[의사코드 검증 스크립트] 3-Option 평가 시스템 전용 테스트
수정일: 2026-02-15
수정내용: 의사코드 평가 3가지 옵션(Multimodel, GPT-only, Hybrid)을 정교하게 검증
"""

import os
import sys
import json
import time
import django
from pathlib import Path

# Django 설정 로드
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent.parent
sys.path.insert(0, str(backend_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.services.pseudocode_evaluator import PseudocodeEvaluator, EvaluationRequest, EvaluationMode

class PseudocodeThreeOptionValidator:
    def __init__(self):
        self.pseudocode_evaluator = PseudocodeEvaluator()
        self.results_dir = backend_dir / 'evaluation' / 'pseudocode_comparison' / 'results'
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def test_option_1_multimodel(self):
        """옵션 1: 다중 모델 (병렬 평가) 검증"""
        print("\n" + "="*60)
        print("🔍 TEST: Option 1 (Always Multimodel)")
        print("="*60)
        return self._run_test(EvaluationMode.OPTION1_ALWAYS_MULTIMODEL)

    def test_option_2_gptonly(self):
        """옵션 2: GPT-4o-mini 단일 모델 검증"""
        print("\n" + "="*60)
        print("🔍 TEST: Option 2 (GPT-4o-mini Only)")
        print("="*60)
        return self._run_test(EvaluationMode.OPTION2_GPTONLY)

    def test_option_3_hybrid(self):
        """옵션 3: 하이브리드 전략 검증"""
        print("\n" + "="*60)
        print("🔍 TEST: Option 3 (Hybrid Strategy)")
        print("="*60)
        return self._run_test(EvaluationMode.OPTION3_HYBRID)

    def _run_test(self, mode):
        test_case = {
            "quest_id": "1",
            "quest_title": "데이터 전처리 누수 차단",
            "pseudocode": "1. 데이터를 나눈다.\n2. 학습 데이터로만 스케일러를 fit 한다.\n3. 둘 다 transform 한다."
        }
        
        start_time = time.time()
        request = EvaluationRequest(
            user_id="test_user",
            detail_id=test_case["quest_id"],
            pseudocode=test_case["pseudocode"],
            quest_title=test_case["quest_title"],
            mode=mode
        )
        
        try:
            result = self.pseudocode_evaluator.evaluate(request)
            elapsed = time.time() - start_time
            print(f"  ✅ Result: Score={result.final_score}, Grade={result.grade}")
            print(f"  ⏱️ Time: {elapsed:.2f}s")
            print(f"  📦 Models: {', '.join(result.llm_evaluations.keys())}")
            
            return {
                "score": result.final_score,
                "grade": result.grade,
                "latency": elapsed,
                "models": list(result.llm_evaluations.keys())
            }
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return {"error": str(e)}

    def run_all(self):
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": {
                "option1": self.test_option_1_multimodel(),
                "option2": self.test_option_2_gptonly(),
                "option3": self.test_option_3_hybrid()
            }
        }
        
        # 파일명도 더 정확하게 변경
        output_file = self.results_dir / "PSEUDOCODE_3OPTION_VALIDATION.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        print("\n" + "="*60)
        print(f"🎉 Pseudocode 3-Option Test Complete!")
        print(f"Report: {output_file}")
        print("="*60)

if __name__ == "__main__":
    validator = PseudocodeThreeOptionValidator()
    validator.run_all()
