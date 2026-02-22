"""
에이전트 실행 엔진

각 에이전트의 실행 함수 정의:
- Orchestrator: 사용자 의도 파악 + 필요 에이전트 결정
- Analysis: 사용자 학습 분석 + 약점 도출
"""
import json
import logging
from typing import Dict, Any, List
from openai import OpenAI
from core.services.weakness_service import analyze_user_learning, get_focus_weakness
from core.models import UserProfile, UserSolvedProblem

logger = logging.getLogger(__name__)

# OpenAI 클라이언트 초기화
client = OpenAI()

# 에이전트 모델
AGENT_MODEL = "gpt-4o-mini"


def run_orchestrator_agent(user_message: str, user_weaknesses: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestrator Agent: 사용자 의도 파악 + 필요 에이전트 결정

    Args:
        user_message: 사용자 요청 메시지
        user_weaknesses: 사용자 현재 약점 정보

    Returns:
        {
            "intent": "사용자가 원하는 것",
            "agents": ["Analysis", "ProblemGenerator", ...],
            "execution_mode": "PARALLEL" or "SEQUENTIAL"
        }
    """
    prompt = f"""
당신은 AI 엔지니어 학습 시스템의 오케스트레이터입니다.
사용자의 요청을 분석해서 필요한 에이전트를 결정하세요.

사용자 요청: {user_message}

사용자 현재 약점:
{json.dumps(user_weaknesses, ensure_ascii=False, indent=2)}

요청 의도 판단:
- "나 약점 뭔지 보여줘", "분석해줘" → ["Analysis"]
- "이 약점 해결할 문제 줘", "문제 만들어줘" → ["Analysis", "ProblemGenerator"]
- "뭘 공부해야 하나", "학습 경로" → ["Analysis", "LearningGuide"]
- "종합 분석해줘", "전체적으로" → ["Analysis", "ProblemGenerator", "LearningGuide"]

다음 JSON 형식으로 응답:
{{
  "intent": "사용자의 의도 (한 줄)",
  "agents": ["Analysis", "ProblemGenerator"],
  "execution_mode": "PARALLEL"
}}
"""

    try:
        response = client.chat.completions.create(
            model=AGENT_MODEL,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.choices[0].message.content
        # JSON 파싱 (마크다운 코드 블록 제거)
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(response_text)

        return result
    except Exception as e:
        logger.error(f"Orchestrator Agent 오류: {e}")
        # 폴백: Analysis만 실행
        return {
            "intent": "학습 분석",
            "agents": ["Analysis"],
            "execution_mode": "PARALLEL"
        }


def run_analysis_agent(user_profile: UserProfile) -> Dict[str, Any]:
    """
    Analysis Agent: submitted_data 분석 → 약점 도출

    Args:
        user_profile: 사용자 프로필

    Returns:
        {
            "summary": "전체 분석 요약",
            "weaknesses": [
                {
                    "name": "edge_case",
                    "score": 45.0,
                    "diagnosis": "null/empty 입력 미처리",
                    "impact": "HIGH"
                },
                ...
            ]
        }
    """
    # 1. Django 함수로 데이터 준비
    analysis_data = analyze_user_learning(user_profile.id)

    if not analysis_data['top_weaknesses']:
        return {
            "summary": "아직 풀이 기록이 부족합니다. 먼저 문제를 풀어보세요.",
            "weaknesses": [],
            "analyzed_submission_count": 0
        }

    # 2. Claude에 분석 요청 (선택사항: 더 깊이 있는 분석이 필요시)
    metrics_json = json.dumps({
        "unit1": analysis_data['unit1_metrics'],
        "unit2": analysis_data['unit2_metrics'],
        "unit3": analysis_data['unit3_metrics'],
    }, ensure_ascii=False, indent=2)

    prompt = f"""
당신은 AI 엔지니어 학습 분석가입니다.
사용자의 풀이 메트릭을 분석해서 약점을 파악하세요.

제출 메트릭 (최근 5개의 평균):
{metrics_json}

상위 약점: {analysis_data['top_weaknesses']}

다음 JSON 형식으로 응답:
{{
  "summary": "종합 분석 요약 (1문장)",
  "weaknesses": [
    {{
      "name": "edge_case",
      "score": 45.0,
      "diagnosis": "null/empty 입력을 처리하지 않음",
      "root_cause": "설계 단계에서 정상 케이스만 고려하는 습관",
      "impact": "HIGH"
    }},
    ...
  ]
}}
"""

    try:
        response = client.chat.completions.create(
            model=AGENT_MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.choices[0].message.content
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        analysis_result = json.loads(response_text)

        return {
            "summary": analysis_result.get("summary", analysis_data['summary']),
            "weaknesses": analysis_result.get("weaknesses", []),
            "analyzed_submission_count": analysis_data['analyzed_submission_count']
        }

    except Exception as e:
        logger.error(f"Analysis Agent 오류: {e}")
        # 폴백: 기본 분석 결과 반환
        return {
            "summary": analysis_data['summary'],
            "weaknesses": [
                {
                    "name": w,
                    "score": analysis_data.get('unit1_metrics', {}).get(w)
                    or analysis_data.get('unit2_metrics', {}).get(w)
                    or analysis_data.get('unit3_metrics', {}).get(w, 0),
                    "diagnosis": f"{w} 약점이 감지되었습니다",
                    "impact": "MEDIUM"
                }
                for w in analysis_data['top_weaknesses']
            ],
            "analyzed_submission_count": analysis_data['analyzed_submission_count']
        }


def run_data_analyzer_agent(user_profile: UserProfile) -> Dict[str, Any]:
    """
    Data Analyzer Agent: 모든 형식의 submitted_data 직접 분석

    Unit별 데이터 형식이 다르더라도 자연스러운 약점 표현으로 분석

    Args:
        user_profile: 사용자 프로필

    Returns:
        {
            "analysis_summary": "분석 요약",
            "weaknesses": [
                {
                    "description": "null/empty 입력 처리 부족",
                    "severity": "HIGH",
                    "affected_areas": ["Unit1", "Unit2"],
                    "recommendation": "방어적 프로그래밍 학습"
                },
                ...
            ],
            "strengths": [
                {
                    "description": "논리 흐름 설계 능력",
                    "evidence": "Unit1에서 일관되게 높은 점수"
                }
            ]
        }
    """
    # 1. 사용자의 최근 풀이 기록 조회 (최대 10개)
    solved_problems = UserSolvedProblem.objects.filter(
        user=user_profile,
        submitted_data__isnull=False
    ).select_related('practice_detail__practice').order_by('-solved_date')[:10]

    if not solved_problems:
        return {
            "analysis_summary": "아직 풀이 기록이 없습니다. 문제를 풀어보세요.",
            "weaknesses": [],
            "strengths": []
        }

    # 2. submitted_data를 OpenAI에 분석 요청
    problems_data = []
    for sp in solved_problems:
        problems_data.append({
            "unit": sp.practice_detail.practice_id,
            "problem_title": str(sp.practice_detail),
            "score": sp.score,
            "submission_data": sp.submitted_data  # 형식 무관하게 전달
        })

    problems_json = json.dumps(problems_data, ensure_ascii=False, indent=2)

    prompt = f"""
당신은 AI 엔지니어의 학습을 깊이 있게 분석하는 전문가입니다.

사용자의 최근 풀이 기록을 분석해서:
1. 실제로 부족한 부분이 무엇인지
2. 강점이 무엇인지
자연스러운 표현으로 파악하세요.

데이터 형식:
{problems_json}

분석 시 고려사항:
- 제출된 코드/설계의 질
- 점수 추이
- 반복되는 패턴 (부족한 부분)
- 잘하는 부분

다음 JSON 형식으로 응답:
{{
  "analysis_summary": "전체 분석 요약 (2~3문장)",
  "weaknesses": [
    {{
      "description": "구체적으로 부족한 부분 (예: null/empty 입력 처리 부족)",
      "severity": "HIGH/MEDIUM/LOW",
      "affected_areas": ["Unit1", "Unit2"],
      "recommendation": "구체적인 학습/개선 방법"
    }}
  ],
  "strengths": [
    {{
      "description": "잘하는 부분 (예: 논리 흐름 설계)",
      "evidence": "근거"
    }}
  ]
}}
"""

    try:
        response = client.chat.completions.create(
            model=AGENT_MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.choices[0].message.content
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(response_text)

        logger.info(f"[Data Analyzer] 분석 완료 - 약점 {len(result.get('weaknesses', []))}개, 강점 {len(result.get('strengths', []))}개")
        return result

    except Exception as e:
        logger.error(f"Data Analyzer Agent 오류: {e}")
        return {
            "analysis_summary": f"분석 중 오류가 발생했습니다: {str(e)}",
            "weaknesses": [],
            "strengths": []
        }


def run_problem_generator_agent(user_profile: UserProfile, weakness: str) -> Dict[str, Any]:
    """
    Problem Generator Agent: 문제 추천 또는 생성 (데모용 간단 버전)

    Args:
        user_profile: 사용자 프로필
        weakness: 약점 이름

    Returns:
        {
            "method": "RECOMMEND",
            "problems": [
                {
                    "problem_id": "unit0103",
                    "title": "예외 처리 집중 문제",
                    "reason": "..."
                }
            ]
        }
    """
    # 데모용: 하드코딩된 문제 추천
    weakness_to_problems = {
        "edge_case": [
            {
                "problem_id": "unit0103",
                "title": "데이터 파이프라인 예외 처리 설계",
                "reason": "null/empty 입력 처리를 집중 연습할 수 있습니다"
            },
            {
                "problem_id": "unit0105",
                "title": "경계값 검증 설계",
                "reason": "min, max, boundary value 처리를 다룹니다"
            }
        ],
        "root_cause": [
            {
                "problem_id": "unit0201",
                "title": "버그 원인 분석 심화",
                "reason": "5Why 분석을 통한 근본 원인 파악 연습"
            }
        ],
        "security": [
            {
                "problem_id": "unit0301",
                "title": "보안 아키텍처 설계",
                "reason": "OWASP Top 10을 다루는 보안 설계 문제"
            }
        ]
    }

    problems = weakness_to_problems.get(weakness, [])

    return {
        "method": "RECOMMEND",
        "problems": problems if problems else [
            {
                "problem_id": f"unit01_custom_{weakness}",
                "title": f"{weakness} 집중 연습 문제",
                "reason": f"{weakness} 약점을 보완하는 맞춤형 문제"
            }
        ]
    }


def run_learning_guide_agent(user_profile: UserProfile, weakness: str) -> Dict[str, Any]:
    """
    Learning Guide Agent: 학습 경로 + 자료 추천 (데모용 간단 버전)

    Args:
        user_profile: 사용자 프로필
        weakness: 약점 이름

    Returns:
        {
            "personalized_message": "너는...",
            "learning_path": [...],
            "estimated_total_hours": 2.25
        }
    """
    # 데모용: 기본 학습 이정표
    learning_paths = {
        "edge_case": {
            "personalized_message": "null/empty 입력 처리를 설계 단계에서 고려하지 않는 패턴이 보입니다. 방어적 코딩부터 학습하세요.",
            "learning_path": [
                {
                    "order": 1,
                    "concept": "Defensive Programming",
                    "duration_minutes": 60,
                    "why_important": "실무에서 처리하지 않은 예외는 런타임 장애로 이어집니다",
                    "resources": [
                        {
                            "type": "article",
                            "title": "Defensive Programming Wikipedia",
                            "url": "https://en.wikipedia.org/wiki/Defensive_programming"
                        }
                    ]
                },
                {
                    "order": 2,
                    "concept": "경계값 분석",
                    "duration_minutes": 30,
                    "why_important": "min, max, empty, null 등 경계값에서 버그가 자주 발생합니다",
                    "resources": []
                }
            ],
            "estimated_total_hours": 1.5
        },
        "root_cause": {
            "personalized_message": "버그를 찾지만 원인 분석이 표면적입니다. 5Why 분석으로 근본 원인을 찾는 훈련을 하세요.",
            "learning_path": [
                {
                    "order": 1,
                    "concept": "5Why 분석법",
                    "duration_minutes": 30,
                    "why_important": "근본 원인을 찾아야 같은 실수를 반복하지 않습니다",
                    "resources": []
                }
            ],
            "estimated_total_hours": 1.0
        },
        "security": {
            "personalized_message": "시스템 설계에서 보안 고려가 부족합니다. OWASP Top 10부터 학습하세요.",
            "learning_path": [
                {
                    "order": 1,
                    "concept": "OWASP Top 10",
                    "duration_minutes": 60,
                    "why_important": "웹 애플리케이션의 가장 흔한 보안 취약점들입니다",
                    "resources": [
                        {
                            "type": "article",
                            "title": "OWASP Top 10",
                            "url": "https://owasp.org/www-project-top-ten/"
                        }
                    ]
                }
            ],
            "estimated_total_hours": 2.0
        }
    }

    roadmap = learning_paths.get(weakness, {
        "personalized_message": f"{weakness} 약점을 보완하기 위한 학습을 추천합니다.",
        "learning_path": [
            {
                "order": 1,
                "concept": f"{weakness} 개념",
                "duration_minutes": 60,
                "why_important": f"{weakness}는 중요한 기술입니다",
                "resources": []
            }
        ],
        "estimated_total_hours": 1.0
    })

    return roadmap


def run_integration_agent(agent_results: Dict[str, Any], user_message: str) -> Dict[str, Any]:
    """
    Integration Agent: 모든 에이전트 결과 통합 → 최종 응답

    Args:
        agent_results: {
            "analysis": {...},
            "problems": {...},
            "guide": {...}
        }
        user_message: 원본 사용자 메시지

    Returns:
        {
            "overview": "종합 분석",
            "action_plan": [...],
            "motivation": "격려 메시지"
        }
    """
    # 분석 결과에서 주요 약점 추출
    analysis = agent_results.get('analysis', {})
    weaknesses = analysis.get('weaknesses', [])
    top_weakness = weaknesses[0] if weaknesses else None

    # 프롬프트 구성
    analysis_json = json.dumps(analysis, ensure_ascii=False, indent=2)
    problems_json = json.dumps(agent_results.get('problems', {}), ensure_ascii=False, indent=2)
    guide_json = json.dumps(agent_results.get('guide', {}), ensure_ascii=False, indent=2)

    prompt = f"""
당신은 학습 결과를 종합해서 사용자에게 명확하게 전달하는 커뮤니케이터입니다.

분석 결과:
{analysis_json}

추천 문제:
{problems_json}

학습 가이드:
{guide_json}

사용자 요청: {user_message}

다음 JSON 형식으로 응답:
{{
  "overview": "종합 분석 요약 (2~3문장)",
  "action_plan": [
    {{
      "step": 1,
      "title": "학습할 개념",
      "description": "설명",
      "time_estimate": "60분"
    }}
  ],
  "problems": [
    {{
      "problem_id": "unit0103",
      "title": "문제 제목",
      "reason": "왜 이 문제를 풀어야 하는가"
    }}
  ],
  "motivation": "종합 평가 + 격려의 말 (1문장)"
}}
"""

    try:
        response = client.chat.completions.create(
            model=AGENT_MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.choices[0].message.content
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        integration_result = json.loads(response_text)

        return integration_result

    except Exception as e:
        logger.error(f"Integration Agent 오류: {e}")
        # 폴백: 기본 응답
        return {
            "overview": "분석이 완료되었습니다. 위의 약점들을 개선하기 위한 학습을 추천합니다.",
            "action_plan": [
                {
                    "step": 1,
                    "title": "학습 시작",
                    "description": "추천된 학습 자료를 통해 개념을 이해합니다",
                    "time_estimate": "1시간"
                },
                {
                    "step": 2,
                    "title": "문제 풀이",
                    "description": "약점을 다루는 문제를 풀어봅니다",
                    "time_estimate": "30분"
                }
            ],
            "motivation": "화이팅! 꾸준한 학습으로 약점을 극복할 수 있습니다."
        }
