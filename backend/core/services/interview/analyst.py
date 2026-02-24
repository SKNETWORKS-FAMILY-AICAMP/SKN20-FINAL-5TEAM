"""
analyst.py — L1 Analyst (증거 추출기)
사용자 답변에서 evidence 존재 여부만 True/False로 태깅한다.
LLM이 "좋다/나쁘다" 판단하는 것을 절대 금지한다.
"""
import json
import openai
from django.conf import settings


def extract_evidence(answer: str, evidence_keys: list) -> dict:
    """
    사용자 답변에서 각 evidence 항목의 존재 여부를 True/False로 반환한다.

    Args:
        answer: 사용자 답변 텍스트
        evidence_keys: 확인할 evidence 항목 목록 (예: ["role", "action", "result"])

    Returns:
        {evidence_key: bool, ...}
        예: {"role": True, "action": False, "result": False}
    """
    if not answer.strip() or not evidence_keys:
        return {key: False for key in evidence_keys}

    try:
        api_key = getattr(settings, 'OPENAI_API_KEY', '') or ''
        if not api_key:
            print("[Analyst] OPENAI_API_KEY 없음 — 모든 evidence False 반환")
            return {key: False for key in evidence_keys}

        client = openai.OpenAI(api_key=api_key)

        evidence_descriptions = _build_evidence_descriptions(evidence_keys)
        prompt = _build_analyst_prompt(answer, evidence_descriptions)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "너는 텍스트 분석기다. 주어진 발화에서 특정 정보의 존재 여부만 판단한다.\n"
                        "판단 기준: '이 발화에 해당 내용이 존재하는가?'\n"
                        "절대 금지: 좋다/나쁘다 평가, 점수 부여, 질적 판단\n"
                        "오직 True/False만 반환한다."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=200,
        )

        raw = response.choices[0].message.content
        result = json.loads(raw)

        # 반환된 dict에서 evidence_keys에 해당하는 값만 추출
        evidence_map = {}
        for key in evidence_keys:
            val = result.get(key, False)
            evidence_map[key] = bool(val)

        return evidence_map

    except Exception as e:
        print(f"[Analyst] 오류: {e}")
        return {key: False for key in evidence_keys}


def _build_evidence_descriptions(evidence_keys: list) -> dict:
    """evidence 키에 대한 한국어 설명을 반환한다."""
    descriptions = {
        # Collaboration
        "role": "본인의 역할이나 담당 업무를 명시했는가",
        "action": "본인이 직접 취한 행동이나 실행 내용을 설명했는가",
        "result": "그 행동으로 인한 결과나 변화가 언급됐는가",
        "conflict": "갈등 상황이나 어려움이 언급됐는가",
        "reflection": "경험에서 배운 점이나 깨달음이 언급됐는가",
        # Problem Solving
        "situation": "문제가 발생한 상황이나 맥락을 설명했는가",
        "analysis": "문제의 원인을 분석했는가",
        "approach": "문제 해결을 위한 접근 방법이나 전략을 설명했는가",
        "learning": "경험에서 얻은 교훈이나 배운 점을 언급했는가",
        # Motivation
        "reason": "지원 이유나 동기를 설명했는가",
        "research": "회사나 직무에 대해 조사/리서치한 내용을 언급했는가",
        "alignment": "본인의 역량이나 목표가 직무와 맞는지 설명했는가",
        "aspiration": "앞으로의 성장 방향이나 목표를 언급했는가",
        # Growth
        "challenge": "도전적인 경험이나 어려움을 언급했는가",
        "effort": "극복하거나 개선하기 위한 노력을 설명했는가",
        "change": "그 과정에서의 변화나 성장을 설명했는가",
    }

    result = {}
    for key in evidence_keys:
        result[key] = descriptions.get(key, f"'{key}'에 해당하는 내용이 언급됐는가")
    return result


def _build_analyst_prompt(answer: str, evidence_descriptions: dict) -> str:
    """Analyst LLM 프롬프트 생성"""
    evidence_list = "\n".join(
        f'- "{key}": {desc}'
        for key, desc in evidence_descriptions.items()
    )

    keys_str = ", ".join(f'"{k}"' for k in evidence_descriptions.keys())

    return f"""다음 발화를 분석하라.

[발화]
{answer}

[확인할 항목]
{evidence_list}

각 항목에 대해 발화에 해당 내용이 존재하면 true, 없으면 false로 답하라.
반드시 다음 JSON 형식으로만 출력하라:
{{{keys_str.replace('"', '"')}}}

예시 (collaboration 슬롯):
{{"role": true, "action": false, "result": false, "conflict": true, "reflection": false}}

주의:
- 내용의 품질을 판단하지 마라
- 명시적으로 언급되지 않은 내용은 false
- 암묵적으로 추론 가능한 내용도 false (직접 발화만 true)"""
