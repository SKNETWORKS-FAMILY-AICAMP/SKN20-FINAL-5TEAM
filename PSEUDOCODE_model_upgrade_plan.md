# 🧪 PSEUDOCODE 모델 비교 평가 고도화 계획 (GPT vs Gemini vs Llama)

**작성일**: 2026-02-15
**목표**: Gemini 404 에러 해결 및 Groq(Llama 3.3) 모델 추가를 통한 3자 비교 수행

## 1. 모델 구성 및 이슈 해결 전략
1.  **GPT-4o-mini**: 기존 벤치마크 기준점으로 활용.
2.  **Gemini 1.5 Flash**: 
    *   **이슈**: 404 에러 발생.
    *   **해결**: 모델 명칭 확인 및 `google-generativeai` 라이브러리의 모델 초기화 방식 재점검 (`models/gemini-1.5-flash` 명칭 시도).
3.  **Llama 3.3 (Groq)**: 
    *   **추가**: Groq API를 통해 초고속 추론 성능을 가진 `llama-3.3-70b-versatile` 모델 투입.
    *   **검증**: 무료 티어 범위 내에서 5개 샘플 2회씩 반복 측정.

## 2. 작업 단계 (Action Items)
1.  **[Step 1] `model_evaluator.py` 수정**: 
    *   Gemini 모델 초기화 시 명칭 오류 방지를 위한 예외 처리 및 명칭 정규화.
    *   Groq(Llama) 평가 로직 정상 작동 확인.
2.  **[Step 2] `run_pseudocode_comparison.py` 수정**: 
    *   테스트 대상 모델 리스트에 `llama-3.3-70b-versatile` 추가.
3.  **[Step 3] 벤치마크 실행**: 
    *   도커 환경에서 3개 모델에 대한 교차 검증 수행.
4.  **[Step 4] 결과 분석 및 보고**: 
    *   `PSEUDOCODE_comparison_summary.json` 업데이트 및 최종 분석 보고서 작성.

---
수정 후 도커를 통해 실제 채점을 진행하고 결과를 보고하겠습니다.
