"""
의사코드 평가 엔진 - 테스트 및 사용 가이드
작성일: 2026-02-15

이 파일은 pseudocode_evaluator.py의 기능을 테스트하고 
실제 사용 방법을 보여주는 예제들입니다.
"""

import os
import sys
import json
from pathlib import Path

# Django 설정
django_setup_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(django_setup_path))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from core.services.pseudocode_evaluator import (
    PseudocodeEvaluator,
    EvaluationRequest,
    EvaluationMode,
    RuleValidationEngine as LocalValidationEngine  # 구버전 호환
)


# ============================================================================
# 1. 테스트 샘플들 (다양한 품질의 의사코드)
# ============================================================================

TEST_SAMPLES = {
    # 정답 - 완벽한 의사코드
    'perfect': """
1. Raw 데이터 로드
2. Train/Test 데이터 분할 (80/20)
3. Train 데이터로만 StandardScaler fit
4. Train과 Test 데이터 모두 StandardScaler transform 적용
5. DecisionTreeClassifier 모델 초기화
6. Train 데이터로 모델 fit
7. Test 데이터로 예측 수행
8. 정확도, 정밀도, 재현율 계산
9. 결과 분석 및 보고
""",
    
    # 좋은 의사코드 - 약간의 개선 필요
    'good': """
1. 데이터 로드
2. Train/Test 분할
3. Train 데이터로 스케일러 fit
4. 데이터 transform
5. 모델 생성
6. 모델 fit
7. 예측
8. 점수 계산
""",
    
    # 평범한 의사코드 - 개념은 있지만 불명확
    'average': """
1. 데이터 준비
2. 데이터 분리
3. 전처리
4. 모델 학습
5. 평가
""",
    
    # 데이터 누수 - 치명적 오류
    'data_leakage': """
1. 데이터 로드
2. 전체 데이터로 스케일러 fit  <-- 오류! 테스트 데이터 정보 포함
3. 전체 데이터 transform
4. Train/Test 분할
5. 모델 fit
6. 예측
7. 평가
""",
    
    # 순서 오류 - fit이 split 전에
    'wrong_order': """
1. 데이터 로드
2. 스케일러 fit (데이터)
3. Transform
4. Train/Test 분할
5. 모델 학습
6. 예측
""",
    
    # 너무 짧은 의사코드 - 너무 추상적
    'too_short': """
1. 데이터 준비
2. 학습
3. 예측
""",
    
    # 개념 누락 - split이 없음
    'missing_concepts': """
1. 데이터 로드
2. 전처리 (정규화)
3. 모델 fit
4. 예측
5. 평가
""",
}


# ============================================================================
# 2. 기본 설명: 현재 스크립트 구성
# ============================================================================

def explain_script_structure():
    """
    pseudocode_evaluator.py의 구조 설명
    """
    print("\n" + "="*70)
    print("📚 pseudocode_evaluator.py 구조 설명")
    print("="*70)
    
    explanation = """
【8개 핵심 엔진】

1️⃣ EvaluationMode (Enum)
   • STANDARD: GPT-4o-mini만 사용 (기본, 빠름)
   • COMPARISON: 3개 모델 비교 (상세, 느림)
   • DEEP_DIVE: 비교 + 심화 질문 (미구현)

2️⃣ LocalValidationEngine
   • Rule 기반 검증 (빠름, ~50ms)
   • 의사코드 형식, 개념, 순서 확인
   • critic_patterns, required_concepts, dependencies 정의

3️⃣ LLMEvaluationEngine
   • OpenAI (GPT-4o-mini)
   • Google Gemini (1.5 Flash)
   • Groq (Llama 3.3)
   • 3박자 프롬프트: System + Module-specific + User

4️⃣ ScoringEngine
   • Self-Audit: 치명적 오류 감지
   • Score Ceiling: 상한선 적용 (40점)
   • Grade Normalization: 등급별 정규화
   • Multi-model aggregation: 가중평균 (GPT 50%, Gemini 30%, Llama 20%)

5️⃣ FeedbackEngine
   • 요약 문장 생성
   • 페르소나 분류 (5가지): 완벽한 설계자, 이론가, 코더, 기획자, 초심자
   • 다음 단계 제시
   • 학습 자원 추천

6️⃣ Model Selection
   • PRIMARY_MODEL = "gpt-4o-mini"
   • BACKUP_MODELS = ["gemini-1.5-flash", "llama-3.3-70b-versatile"]

7️⃣ 데이터 클래스
   • EvaluationRequest: 입력
   • LocalValidationResult: 로컬 검증 결과
   • LLMEvaluationResult: 각 모델 결과
   • FinalEvaluationResult: 최종 결과

8️⃣ PseudocodeEvaluator (메인 오케스트레이터)
   • 5단계 파이프라인 실행
   • 모드에 따라 다른 평가 방식 적용
   • 자동 폴백 (표준 실패 시 비교 모드 전환)

【5단계 평가 파이프라인】

[Step 1] 로컬 검증 (~50ms)
   입력값 → 형식/개념/순서 확인 → 로컬 점수

[Step 2] LLM 평가 (표준/비교 모드)
   의사코드 + 로컬 결과 → 3박자 프롬프트 → LLM 호출 → 점수 + 피드백

[Step 3] 점수 정규화
   LLM 점수 → 자가진단 → 상한선 → 그레이드 정규화 → 최종 점수

[Step 4] 피드백 생성
   LLM 응답 + 점수 + 다중 모델 결과 → 요약/강점/개선/페르소나/다음단계

[Step 5] 최종 결과 포장
   모든 정보 통합 → JSON 반환 → 저장/응답

【3단계 프롬프트 구조】

SYSTEM PROMPT (고정)
├─ 역할: 의사코드 평가 전문가
├─ 5차원 루브릭 정의
└─ JSON 응답 형식

MODULE-SPECIFIC PROMPT (모듈별)
├─ 미션 설명
├─ 필수 개념
└─ 평가 중점

USER PROMPT (동적)
├─ 사용자 의사코드
├─ 로컬 검증 결과
└─ 평가 요청
"""
    
    print(explanation)


# ============================================================================
# 3. 기본 사용법
# ============================================================================

def example_1_option1_always_multimodel():
    """
    예제 1: 옵션1 - 항상 3개 모델 사용 (최고 신뢰도)
    """
    print("\n" + "="*70)
    print("📝 [옵션1] 항상 3개 모델 사용")
    print("="*70)
    
    print("""
전략: GPT (50%) + Gemini (30%) + Llama (20%) 가중평균

사용 시나리오:
  • 교수/관리자 최종 검수 (최고 신뢰도 필요)
  • 학생 민원 응처 (3개 모델 합의)
  • 중요 평가 기록 (감사 추적)
  • 시스템 성능 분석

특징:
  ✅ 최고의 신뢰도 (3개 모델 검증)
  ✅ 모델 간 합의 강화
  ✅ 각 모델의 강점 활용
  ❌ 느림 (~8-10초)
  ❌ 높은 비용 (3배)
""")
    
    code_example = """
from core.services.pseudocode_evaluator import (
    PseudocodeEvaluator,
    EvaluationRequest,
    EvaluationMode
)

evaluator = PseudocodeEvaluator()

# 옵션1: 항상 3개 모델
request = EvaluationRequest(
    user_id='user_123',
    detail_id='unit0401',
    pseudocode='... 의사코드 ...',
    mode=EvaluationMode.OPTION2_GPTONLY  # 현재 지원 모드
)

result = evaluator.evaluate(request)

# 결과: 모델별 점수 + 가중평균
print(f"최종 점수: {result.final_score}점 (3모델 가중평균)")
print(f"신뢰도: {result.feedback.get('model_comparison', {}).get('confidence', 0):.0%}")

# 모델별 상세 비교
for model, eval_result in result.llm_evaluations.items():
    print(f"{model}: {eval_result.raw_score}점")
"""
    
    print("\n💻 코드:")
    print(code_example)


def example_2_option2_gptonly():
    """
    예제 2: 옵션2 - GPT만 사용 (빠르고 저비용)
    """
    print("\n" + "="*70)
    print("📝 [옵션2] GPT-4o-mini만 사용")
    print("="*70)
    
    print("""
전략: 단일 모델로 빠른 평가

사용 시나리오:
  • 일반 학생 평가 (피드백 속도 중요)
  • 대량 평가 (비용 절감)
  • 프로덕션 기본 평가 (신뢰도 95%+)
  • 실시간 피드백

특징:
  ✅ 매우 빠름 (~2-3초)
  ✅ 저비용 (1/3)
  ✅ 높은 신뢰도 (95%+)
  ❌ 단일 모델 (검증 불가)
  ❌ 모델 실패 시 폴백 필요
""")
    
    code_example = """
from core.services.pseudocode_evaluator import (
    PseudocodeEvaluator,
    EvaluationRequest,
    EvaluationMode
)

evaluator = PseudocodeEvaluator()

# 옵션2: GPT만
request = EvaluationRequest(
    user_id='user_123',
    detail_id='unit0401',
    pseudocode='... 의사코드 ...',
    mode=EvaluationMode.OPTION2_GPTONLY  # GPT만!
)

result = evaluator.evaluate(request)

print(f"최종 점수: {result.final_score}점")
print(f"사용 모델: GPT-4o-mini (단일)")
print(f"소요 시간: {result.metadata['total_latency_ms']}ms")
"""
    
    print("\n💻 코드:")
    print(code_example)


def example_3_option3_hybrid():
    """
    예제 3: 옵션3 - 하이브리드 (로컬 기반 선택)
    """
    print("\n" + "="*70)
    print("📝 [옵션3] 하이브리드 모드")
    print("="*70)
    
    print("""
전략: 로컬 검증 결과에 따라 동적으로 모델 선택

동작 방식:
  1. 로컬 검증 실행
  2. 통과 → GPT만 사용 (빠름)
  3. 실패 → 3개 모델 사용 (검증)

사용 시나리오:
  • 자동 평가 시스템 (균형잡힌 비용/신뢰도)
  • 문제 있는 답변만 재검증
  • 동적 자원 할당

특징:
  ✅ 효율적 (필요시에만 3모델)
  ✅ 합리적 비용
  ✅ 높은 신뢰도
  ✅ 자동 폴백
""")
    
    code_example = """
from core.services.pseudocode_evaluator import (
    PseudocodeEvaluator,
    EvaluationRequest,
    EvaluationMode
)

evaluator = PseudocodeEvaluator()

# 옵션3: 하이브리드
request = EvaluationRequest(
    user_id='user_123',
    detail_id='unit0401',
    pseudocode='... 의사코드 ...',
    mode=EvaluationMode.OPTION2_GPTONLY  # 현재 지원 모드
)

result = evaluator.evaluate(request)

# 로컬 검증 결과에 따라 다른 모델 사용됨
if result.local_validation.passed:
    print("로컬 검증 ✅ → GPT만 사용")
else:
    print("로컬 검증 ❌ → 3개 모델 재검증")

print(f"최종 점수: {result.final_score}점")
print(f"사용 모델: {result.metadata['llm_models_successful']}")
"""
    
    print("\n💻 코드:")
    print(code_example)


# ============================================================================
# 4. 실제 테스트 실행
# ============================================================================

def run_test_with_sample(sample_name: str, pseudocode: str):
    """
    샘플 의사코드로 실제 테스트 실행
    """
    print("\n" + "-"*70)
    print(f"📌 테스트: {sample_name}")
    print("-"*70)
    print(f"\n의사코드 입력:\n{pseudocode}")
    
    evaluator = PseudocodeEvaluator()
    
    # 표준 모드로 평가
    print(f"\n🔄 표준 모드(GPT)로 평가 중...")
    request = EvaluationRequest(
        user_id='test_user',
        detail_id='test_001',
        pseudocode=pseudocode,
        mode=EvaluationMode.OPTION2_GPTONLY
    )
    
    try:
        result = evaluator.evaluate(request)
        
        # 결과 출력
        print(f"\n✅ 평가 완료!")
        print(f"  • 최종 점수: {result.final_score}점")
        print(f"  • 등급: {result.grade}")
        print(f"  • 페르소나: {result.persona}")
        print(f"  • 평가 모드: {result.mode.value}")
        
        # 피드백 출력
        print(f"\n📋 피드백:")
        print(f"  • 요약: {result.feedback.get('summary', 'N/A')}")
        
        if result.feedback.get('strengths'):
            print(f"  • 강점: {', '.join(result.feedback['strengths'][:2])}")
        
        if result.feedback.get('improvements'):
            print(f"  • 개선: {', '.join(result.feedback['improvements'][:2])}")
        
        print(f"  • 다음 단계:")
        for step in result.feedback.get('next_steps', [])[:2]:
            print(f"    - {step}")
        
        # 메타데이터
        print(f"\n⏱️ 성능:")
        print(f"  • 총 소요 시간: {result.metadata['total_latency_ms']}ms")
        print(f"  • 사용 모델: {', '.join(result.metadata['llm_models_successful'])}")
        
        return result
    
    except Exception as e:
        print(f"\n❌ 평가 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def run_all_tests():
    """
    모든 테스트 샘플 실행
    """
    print("\n" + "="*70)
    print("🧪 전체 테스트 실행")
    print("="*70)
    
    results = {}
    
    for sample_name, pseudocode in TEST_SAMPLES.items():
        print(f"\n\n{'='*70}")
        print(f"테스트: {sample_name.upper()}")
        print(f"{'='*70}")
        result = run_test_with_sample(sample_name, pseudocode)
        results[sample_name] = result
    
    # 종합 비교
    print("\n\n" + "="*70)
    print("📊 종합 비교")
    print("="*70)
    
    summary = {}
    for name, result in results.items():
        if result:
            summary[name] = {
                'score': result.final_score,
                'grade': result.grade,
                'persona': result.persona
            }
    
    print(json.dumps(summary, ensure_ascii=False, indent=2))


# ============================================================================
# 5. 로컬 검증만 테스트
# ============================================================================

def test_local_validation_only():
    """
    로컬 검증만 빠르게 테스트 (LLM 호출 없음)
    """
    print("\n" + "="*70)
    print("🏃 빠른 테스트: 로컬 검증만 (LLM 제외)")
    print("="*70)
    
    validator = LocalValidationEngine()
    
    for sample_name, pseudocode in TEST_SAMPLES.items():
        print(f"\n📌 {sample_name}:")
        result = validator.validate(pseudocode)
        
        print(f"  • 통과: {result.passed}")
        print(f"  • 점수: {result.score}점")
        print(f"  • 피드백: {', '.join(result.feedback)}")
        if result.warnings:
            print(f"  • 경고: {', '.join(result.warnings)}")
        print(f"  • 처리 시간: {result.processing_time_ms}ms")


# ============================================================================
# 6. 메인 실행
# ============================================================================

if __name__ == '__main__':
    print("\n" + "▓"*70)
    print("▓  의사코드 평가 엔진 - 사용 가이드 및 테스트")
    print("▓" * 70)
    
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        command = 'explain'
    
    if command == 'explain':
        # 1. 스크립트 구조 설명
        explain_script_structure()
        
        # 2. 3가지 옵션 설명
        example_1_option1_always_multimodel()
        example_2_option2_gptonly()
        example_3_option3_hybrid()
    
    elif command == 'local_only':
        # 3. 로컬 검증만 (빠름, LLM 불필요)
        test_local_validation_only()
    
    elif command == 'test_all':
        # 4. 전체 테스트 실행 (시간 걸림)
        print("\n⚠️  전체 테스트는 시간이 오래 걸립니다 (~30-50초)")
        print("LLM API 키가 설정되어 있는지 확인하세요")
        proceed = input("\n계속하시겠습니까? (y/n): ")
        if proceed.lower() == 'y':
            run_all_tests()
    
    elif command == 'test_single':
        # 5. 단일 샘플 선택 테스트
        print("\n사용 가능한 샘플:")
        for i, name in enumerate(TEST_SAMPLES.keys(), 1):
            print(f"  {i}. {name}")
        
        choice = input("\n선택 (1-6): ")
        sample_names = list(TEST_SAMPLES.keys())
        
        try:
            idx = int(choice) - 1
            sample_name = sample_names[idx]
            pseudocode = TEST_SAMPLES[sample_name]
            run_test_with_sample(sample_name, pseudocode)
        except (ValueError, IndexError):
            print("❌ 잘못된 선택입니다")
    
    elif command == 'test_option1':
        # 6. 옵션1 테스트 (항상 3개 모델)
        print("\n🧪 옵션1 테스트: 항상 3개 모델 사용")
        pseudocode = TEST_SAMPLES['perfect']
        evaluator = PseudocodeEvaluator()
        request = EvaluationRequest(
            user_id='test_user',
            detail_id='option1_test',
            pseudocode=pseudocode,
            mode=EvaluationMode.OPTION2_GPTONLY
        )
        result = evaluator.evaluate(request)
        print(f"\n최종 점수: {result.final_score}점")
        print(f"사용 모델: {result.metadata['llm_models_successful']}")
    
    elif command == 'test_option2':
        # 7. 옵션2 테스트 (GPT만)
        print("\n🧪 옵션2 테스트: GPT만 사용")
        pseudocode = TEST_SAMPLES['perfect']
        evaluator = PseudocodeEvaluator()
        request = EvaluationRequest(
            user_id='test_user',
            detail_id='option2_test',
            pseudocode=pseudocode,
            mode=EvaluationMode.OPTION2_GPTONLY
        )
        result = evaluator.evaluate(request)
        print(f"\n최종 점수: {result.final_score}점")
        print(f"사용 모델: {result.metadata['llm_models_successful']}")
    
    elif command == 'test_option3':
        # 8. 옵션3 테스트 (하이브리드)
        print("\n🧪 옵션3 테스트: 하이브리드 모드")
        pseudocode = TEST_SAMPLES['data_leakage']  # 실패하는 샘플
        evaluator = PseudocodeEvaluator()
        request = EvaluationRequest(
            user_id='test_user',
            detail_id='option3_test',
            pseudocode=pseudocode,
            mode=EvaluationMode.OPTION2_GPTONLY
        )
        result = evaluator.evaluate(request)
        print(f"\n최종 점수: {result.final_score}점")
        print(f"사용 모델: {result.metadata['llm_models_successful']}")
        if result.local_validation.passed:
            print("로컬 검증: ✅ → GPT만 사용")
        else:
            print("로컬 검증: ❌ → 3개 모델 재검증")
    
    else:
        print(f"❌ 알 수 없는 명령: {command}")
        print("\n사용법:")
        print("  python test_pseudocode_evaluator.py explain       # 3가지 옵션 설명")
        print("  python test_pseudocode_evaluator.py local_only    # 로컬 검증만")
        print("  python test_pseudocode_evaluator.py test_single   # 단일 샘플 테스트")
        print("  python test_pseudocode_evaluator.py test_all      # 전체 테스트")
        print("  python test_pseudocode_evaluator.py test_option1  # 옵션1 테스트 (항상 3모델)")
        print("  python test_pseudocode_evaluator.py test_option2  # 옵션2 테스트 (GPT만)")
        print("  python test_pseudocode_evaluator.py test_option3  # 옵션3 테스트 (하이브리드)")
    
    print("\n" + "▓"*70)
    print("▓ 테스트 완료")
    print("▓" * 70 + "\n")
