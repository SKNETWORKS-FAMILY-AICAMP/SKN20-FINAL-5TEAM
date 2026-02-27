"""
시스템 아키텍처 트랙 LLM 신뢰성 검증 - 샘플 생성

4개 문제 × 5개 품질 레벨 = 20개 샘플 생성
각 문제에 대해 품질 레벨별 아키텍처 설명 + Q&A를 LLM으로 생성.

실행:
  python generate_validation_samples.py          # 전체 20개 생성
  python generate_validation_samples.py --quick  # 1개 문제만 (5개)
"""
import os
import sys
import json
import time
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[8] / '.env')
except ImportError:
    pass

import openai

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
MODEL = "gpt-4o-mini"

# ── 평가 문제 정의 (architecture.json에서 대표 문제 4개) ──────────────────────
PROBLEMS = [
    {
        'problem_id': 'jr_001_url_shortener',
        'title': '축제 홍보용 단축 URL 생성기',
        'scenario': '학생회에서 축제 홍보용 긴 구글 폼 링크를 짧은 URL로 변환하여 배포하려고 합니다. 홍보 문자가 발송되는 시점에 대량의 클릭이 발생합니다.',
        'missions': [
            '초당 수천 건의 읽기 요청을 처리하면서 DB 부하를 최소화하는 구조를 설계하세요.',
            '단축 URL 생성 및 원본 리다이렉션의 데이터 흐름을 다이어그램으로 나타내세요.',
        ],
        'constraints': [
            '하루 평균 1,000개 생성, 읽기 요청 초당 최대 1,000건(TPS)',
            '리다이렉션 응답 속도 100ms 이내',
            '생성된 링크는 1년간 영구 보존',
        ],
        'required_components': ['Web Server', 'RDBMS', 'Cache', 'Redis'],
        'key_flows': ['캐시 → DB 미스 시 조회', 'Read-through 캐시'],
        'deep_dive_questions': [
            {
                'category': 'performance_optimization',
                'question': '초당 1,000건의 리다이렉션 요청에서 캐시 히트율을 높이려면 어떤 전략을 사용해야 할까요?',
                'gap': '캐시 계층의 역할과 위치 이해',
            },
            {
                'category': 'reliability',
                'question': '캐시 서버가 다운되었을 때 서비스가 어떻게 유지되어야 하나요?',
                'gap': '장애 시 폴백 전략',
            },
        ],
    },
    {
        'problem_id': 'jr_002_pastebin',
        'title': '동아리 에러 로그 공유함 (Pastebin)',
        'scenario': '개발 동아리에서 긴 에러 로그를 텍스트로 업로드하고 링크로 공유하는 서비스를 만듭니다. 텍스트 본문이 매우 커서 일반적인 DB 저장 방식은 한계가 있습니다.',
        'missions': [
            '대용량 텍스트 데이터와 메타데이터의 저장소를 분리하여 설계하세요.',
            '만료된 데이터를 효율적으로 정리하는 컴포넌트를 배치하세요.',
        ],
        'constraints': [
            '일일 업로드 5,000건, 조회 50,000건',
            '텍스트 본문 최대 10MB',
            '7일 후 자동 만료 및 삭제 처리',
        ],
        'required_components': ['Web Server', 'Object Storage', 'S3', 'RDBMS', 'Cleanup Worker'],
        'key_flows': ['본문 → Object Storage', '메타데이터 → RDBMS', '만료 → Worker 처리'],
        'deep_dive_questions': [
            {
                'category': 'cost_optimization',
                'question': '10MB 텍스트를 RDBMS에 직접 저장하는 대신 Object Storage를 사용하는 이유는 무엇인가요?',
                'gap': '저장소 선택 기준과 비용 효율',
            },
            {
                'category': 'operational_excellence',
                'question': '7일 만료 데이터를 효율적으로 정리하는 Worker 설계를 구체적으로 설명해주세요.',
                'gap': '배치 작업 및 스케줄링 설계',
            },
        ],
    },
    {
        'problem_id': 'jr_003_notification',
        'title': '오늘의 학식 점심 알림',
        'scenario': '매일 점심 11시 30분에 전교생 1만 명에게 동시에 푸시 알림을 보냅니다. 알림 발송 순간 메인 서버가 멈추는 현상이 발생하고 있습니다.',
        'missions': [
            '트래픽 폭주(Spike)를 완충할 수 있는 비동기 메시징 시스템을 설계하세요.',
            '서버와 발송 로직의 결합도를 낮추는 구조를 그리세요.',
        ],
        'constraints': [
            '오전 11:30에 10,000건의 알림 요청 집중',
            '전송에 1~2분 정도의 지연은 허용됨',
            '알림 전송 실패 시 반드시 재시도 로직이 동작해야 함',
        ],
        'required_components': ['Web Server', 'Message Queue', 'Kafka', 'RabbitMQ', 'Notification Worker'],
        'key_flows': ['서버 → 큐 적재', '큐 → Worker 소비', '실패 → 재시도'],
        'deep_dive_questions': [
            {
                'category': 'reliability',
                'question': '알림 발송에 실패했을 때 재시도 로직을 어떻게 구현해야 하나요? 중복 발송을 막으려면?',
                'gap': '멱등성과 재시도 전략',
            },
            {
                'category': 'performance_optimization',
                'question': 'Message Queue를 사용하여 트래픽 스파이크를 어떻게 완충하나요?',
                'gap': '비동기 처리와 백프레셔',
            },
        ],
    },
    {
        'problem_id': 'jr_004_image_feed',
        'title': '반려 식물 성장 일기 (이미지 피드)',
        'scenario': '사용자들이 고화질 식물 사진을 업로드하고 피드를 통해 공유합니다. 전 세계 어디서든 사진이 빠르게 로딩되어야 합니다.',
        'missions': [
            '정적 콘텐츠 전송 성능을 극대화하고 서버 부하를 줄이는 캐싱 구조를 설계하세요.',
            '이미지 조회 시 데이터가 흐르는 경로를 최적화하세요.',
        ],
        'constraints': [
            '평균 5MB 내외의 고화질 이미지',
            '이미지 로딩 지연 시간 500ms 이내',
            '전 세계 각지에서 동시 접속',
            '원본 서버의 대역폭 사용료 절감 필요',
        ],
        'required_components': ['Object Storage', 'CDN', 'Web Server', 'Database'],
        'key_flows': ['클라이언트 → CDN', 'CDN 미스 → Object Storage', '지역 엣지 서버 활용'],
        'deep_dive_questions': [
            {
                'category': 'performance_optimization',
                'question': 'CDN의 캐시 히트율을 높이려면 어떤 캐시 정책을 사용해야 하나요?',
                'gap': 'CDN TTL 설정과 캐시 무효화 전략',
            },
            {
                'category': 'cost_optimization',
                'question': '원본 서버 대역폭 비용을 줄이는 구체적인 방법을 설명해주세요.',
                'gap': 'CDN을 통한 오리진 서버 트래픽 절감',
            },
        ],
    },
]

# ── 품질 레벨 정의 ──────────────────────────────────────────────────────────────
QUALITY_LEVELS = {
    'excellent': {
        'desc': '시니어 아키텍트 수준. 모든 필수 컴포넌트 명시, 구체적 기술명/수치 포함, 트레이드오프 설명, Q&A에서 심화 답변',
        'score_range': [85, 100],
        'arch_instruction': (
            '시니어 클라우드 아키텍트 수준의 설계를 작성하세요. '
            '모든 필수 컴포넌트를 명시하고, 구체적인 기술명(Redis, Kafka 등)과 수치(TTL, TPS 등)를 포함하세요. '
            '트레이드오프를 설명하고, 장애 시나리오와 복구 방법도 언급하세요. '
            '컴포넌트 목록과 데이터 흐름을 구체적으로 기술하세요.'
        ),
        'qna_instruction': (
            '각 질문에 대해 구체적인 기술명, 수치, 구현 방법을 포함하여 상세하게 답변하세요. '
            '트레이드오프와 대안도 언급하세요.'
        ),
    },
    'good': {
        'desc': '양호 수준. 핵심 컴포넌트 대부분 포함, 기술명 1-2개, 기본 흐름 설명, Q&A에서 핵심 개념 언급',
        'score_range': [72, 84],
        'arch_instruction': (
            '기본기가 있는 개발자 수준의 설계를 작성하세요. '
            '주요 컴포넌트는 포함하지만 일부 세부 사항이 빠져 있고, '
            '기술명을 1-2개 사용하며 기본적인 데이터 흐름은 설명하세요.'
        ),
        'qna_instruction': (
            '핵심 개념은 맞게 답변하되, 구체적인 구현 방법보다는 일반적인 접근법으로 답변하세요.'
        ),
    },
    'average': {
        'desc': '보통 수준. 일부 컴포넌트 누락, 추상적인 설명, Q&A에서 표면적 답변',
        'score_range': [55, 71],
        'arch_instruction': (
            '입문자 수준의 설계를 작성하세요. '
            '일반적인 컴포넌트만 언급하고(서버, 데이터베이스 등), '
            '구체적인 기술명이나 수치 없이 추상적으로 설명하세요. '
            '필수 컴포넌트 중 일부는 빠뜨리세요.'
        ),
        'qna_instruction': (
            '질문의 핵심을 이해하지만 구체적인 해결 방법 없이 표면적으로만 답변하세요.'
        ),
    },
    'poor': {
        'desc': '미흡 수준. 핵심 컴포넌트 다수 누락, 잘못된 설계 포함, Q&A에서 부정확한 답변',
        'score_range': [40, 54],
        'arch_instruction': (
            '문제를 잘 이해하지 못한 수준의 설계를 작성하세요. '
            '핵심 컴포넌트가 빠져 있고 잘못된 구조를 제안하며, '
            '성능 요구사항을 무시한 설계를 하세요.'
        ),
        'qna_instruction': (
            '질문에 대해 관련은 있지만 부정확하거나 불완전한 답변을 하세요. '
            '핵심 개념을 혼동하거나 잘못 적용하세요.'
        ),
    },
    'very_poor': {
        'desc': '불량 수준. 설계가 거의 없거나, 완전히 잘못된 방향, Q&A에서 핵심과 무관한 답변',
        'score_range': [0, 39],
        'arch_instruction': (
            '설계를 거의 하지 못한 수준의 내용을 작성하세요. '
            '매우 짧거나(1-2줄), 기술적으로 완전히 잘못된 구조이거나, '
            '문제 요구사항을 전혀 고려하지 않은 답변을 작성하세요.'
        ),
        'qna_instruction': (
            '질문과 거의 관련 없거나 매우 짧고 틀린 답변을 작성하세요.'
        ),
    },
}


def generate_sample(problem: dict, quality: str, level_info: dict) -> dict:
    """LLM으로 특정 품질 레벨의 아키텍처 설계 + Q&A 생성"""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    # 아키텍처 설계 생성
    arch_prompt = f"""시스템 아키텍처 평가 시스템의 신뢰성 검증을 위한 테스트 데이터를 생성합니다.

[문제]
{problem['title']}
시나리오: {problem['scenario']}
미션: {'; '.join(problem['missions'])}
제약조건: {'; '.join(problem['constraints'])}

[품질 레벨: {quality.upper()}]
{level_info['arch_instruction']}

아키텍처 설계와 설명을 두 부분으로 작성하세요:

ARCHITECTURE_CONTEXT:
(컴포넌트 목록과 간단한 구성도를 텍스트로 표현)

USER_EXPLANATION:
(설계 의도와 각 컴포넌트 선택 이유 설명)

마크다운 없이 순수 텍스트로 작성하세요."""

    arch_response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": arch_prompt}],
        temperature=0.7,
        max_tokens=800,
    )
    arch_text = arch_response.choices[0].message.content.strip()

    # ARCHITECTURE_CONTEXT와 USER_EXPLANATION 분리
    arch_context = ''
    user_explanation = ''
    if 'ARCHITECTURE_CONTEXT:' in arch_text and 'USER_EXPLANATION:' in arch_text:
        parts = arch_text.split('USER_EXPLANATION:')
        arch_context = parts[0].replace('ARCHITECTURE_CONTEXT:', '').strip()
        user_explanation = parts[1].strip()
    else:
        arch_context = arch_text[:400]
        user_explanation = arch_text[400:] if len(arch_text) > 400 else arch_text

    # Q&A 생성
    deep_dive_qna = []
    for q in problem['deep_dive_questions']:
        qna_prompt = f"""다음 시스템 아키텍처 질문에 답변하세요.

문제: {problem['title']}
아키텍처 설계: {arch_context[:300]}

질문 [{q['category']}]: {q['question']}

[품질 레벨: {quality.upper()}]
{level_info['qna_instruction']}

답변만 작성하세요 (마크다운 없이, 2-4문장)."""

        qna_response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": qna_prompt}],
            temperature=0.7,
            max_tokens=300,
        )
        answer = qna_response.choices[0].message.content.strip()
        deep_dive_qna.append({
            'category': q['category'],
            'question': q['question'],
            'gap': q['gap'],
            'answer': answer,
        })
        time.sleep(0.2)

    return {
        'architecture_context': arch_context,
        'user_explanation': user_explanation,
        'deep_dive_qna': deep_dive_qna,
    }


def generate_all_samples(quick: bool = False) -> list:
    problems = PROBLEMS[:1] if quick else PROBLEMS
    samples = []

    for problem in problems:
        print(f"\n문제: {problem['title']}")
        for quality, level_info in QUALITY_LEVELS.items():
            print(f"  [{quality}] 생성 중...")
            try:
                content = generate_sample(problem, quality, level_info)
                sample = {
                    'sample_id': f"{problem['problem_id']}_{quality}",
                    'problem_id': problem['problem_id'],
                    'problem': {
                        'title': problem['title'],
                        'scenario': problem['scenario'],
                        'missions': problem['missions'],
                        'constraints': problem['constraints'],
                    },
                    'quality_level': quality,
                    'expected_score_range': level_info['score_range'],
                    'architecture_context': content['architecture_context'],
                    'user_explanation': content['user_explanation'],
                    'deep_dive_qna': content['deep_dive_qna'],
                    # rule-based 검증용 메타데이터
                    '_required_components': problem['required_components'],
                    '_key_flows': problem['key_flows'],
                }
                samples.append(sample)
                print(f"  [{quality}] 완료")
                time.sleep(0.3)
            except Exception as e:
                print(f"  [{quality}] 오류: {e}")

    return samples


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true', help='문제 1개만 생성 (5개)')
    args = parser.parse_args()

    if not OPENAI_API_KEY:
        print("오류: OPENAI_API_KEY 환경 변수가 없습니다.")
        sys.exit(1)

    samples = generate_all_samples(quick=args.quick)

    out_dir = Path(__file__).parent / 'data'
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = '_quick' if args.quick else ''
    out_file = out_dir / f'validation_samples{suffix}.json'

    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)

    print(f"\n완료: {len(samples)}개 샘플 저장 → {out_file}")
