# job_planner_view.py
"""
Job Planner Agent - Django REST API
원본 v3.1 기반 - URL 크롤링 및 이미지 OCR 지원
"""
import os
import json
import base64
import traceback
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# 외부 라이브러리
try:
    import requests
    from bs4 import BeautifulSoup
    import openai
    CRAWLER_AVAILABLE = True
except ImportError:
    CRAWLER_AVAILABLE = False

def _embed_texts(texts: list):
    """OpenAI API로 텍스트 임베딩 후 L2 정규화된 numpy 배열 반환 (shape: n x dim)"""
    import numpy as np
    import openai as _openai
    client = _openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    response = client.embeddings.create(model="text-embedding-3-small", input=texts)
    vectors = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
    arr = np.array(vectors, dtype=np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    return arr / np.maximum(norms, 1e-8)


@method_decorator(csrf_exempt, name='dispatch')
class JobPlannerParseView(APIView):
    """
    채용공고 파싱 API
    - URL 크롤링
    - 이미지 OCR (OpenAI Vision)
    - 텍스트 직접 입력
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        input_type = request.data.get('type')  # 'url', 'image', 'text'

        try:
            if input_type == 'url':
                return self._parse_from_url(request)
            elif input_type == 'image':
                return self._parse_from_image(request)
            elif input_type == 'text':
                return self._parse_from_text(request)
            else:
                return Response({
                    "error": "Invalid input type. Use 'url', 'image', or 'text'."
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"❌ Parse 에러: {e}")
            print(traceback.format_exc())
            return Response({
                "error": f"파싱 중 오류 발생: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _parse_from_url(self, request):
        """
        URL 크롤링으로 채용공고 파싱 (Collector 시스템 사용)

        Collector 레이어를 통해 채용공고 텍스트를 수집한 후,
        LLM으로 구조화된 정보를 파싱합니다.

        Collector 시스템 단계별 설명:
        - Phase 1: StaticCollector (requests + BeautifulSoup)
          → 정적 HTML 페이지 크롤링 (서버에서 완성된 HTML을 반환하는 사이트)
        - Phase 2+: BrowserCollector, ApiCollector 추가 예정
          → BrowserCollector: JavaScript로 렌더링되는 SPA 사이트 크롤링 (Selenium/Playwright)
          → ApiCollector: 채용 사이트 공식 API를 통한 데이터 수집

        Args:
            request: URL이 포함된 HTTP 요청 객체

        Returns:
            Response: 파싱된 채용공고 정보 (JSON)
        """
        if not CRAWLER_AVAILABLE:
            return Response({
                "error": "크롤링 라이브러리가 설치되지 않았습니다."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        url = request.data.get('url')
        if not url:
            return Response({
                "error": "URL이 필요합니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # === Collector 시스템으로 텍스트 수집 ===
            from .collectors import CollectorRouter

            router = CollectorRouter()
            text = router.collect_with_fallback(url)

            # 텍스트가 너무 짧으면 경고
            if len(text) < 100:
                print(f"⚠️  추출된 텍스트가 짧습니다 ({len(text)}자). SPA 사이트일 수 있습니다.")

            # LLM으로 구조화된 채용공고 정보 추출
            parsed_data = self._extract_job_info_with_llm(text, source='url')

            # 파싱 결과 SavedJobPosting에 저장
            saved_id = self._save_job_posting(request, parsed_data, source='url', source_url=url)
            if saved_id:
                parsed_data['saved_posting_id'] = saved_id

            return Response(parsed_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": f"URL 파싱 실패: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

    def _parse_from_image(self, request):
        """이미지 OCR로 채용공고 파싱 (OpenAI Vision)"""
        image_data = request.data.get('image')  # base64 encoded
        if not image_data:
            return Response({
                "error": "이미지 데이터가 필요합니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return Response({
                "error": "OPENAI_API_KEY가 설정되지 않았습니다."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            client = openai.OpenAI(api_key=api_key)

            # Vision API 호출
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """당신은 IT 채용공고 이미지 분석 전문가입니다.
이미지에서 채용공고 정보를 정확하게 추출하여 JSON 형식으로 반환하세요.

🎯 **핵심 미션**: required_skills와 preferred_skills 배열을 최대한 많이 추출하는 것이 가장 중요합니다!

## 추출 정보:
1. 회사명과 포지션
2. 주요 업무 (담당할 업무, 하게 될 일)
3. 필수 요건 (자격 요건, 필수 조건) - **원문 그대로**
4. 우대 조건 (우대 사항, 플러스 요소) - **원문 그대로**
5. **기술 스택 (가장 중요!)** - 프로그래밍 언어, 프레임워크, 도구, DB, 클라우드 등 모두 추출

## 기술 스택 추출 가이드:
이미지 텍스트에서 다음 **모든** 기술을 찾아 배열로 추출하세요:

### 언어
- Python, Java, JavaScript, TypeScript, C++, C#, Go, Kotlin, Swift, Ruby, PHP, Rust, Scala 등
- 한글: 파이썬, 자바, 자바스크립트, 타입스크립트 → 영문으로 변환

### 프레임워크/라이브러리
- Django, Flask, FastAPI, Spring, SpringBoot, React, Vue, Angular, Next.js, Node.js, Express 등
- 한글: 장고, 플라스크, 스프링, 리액트, 뷰 → 영문으로 변환

### 데이터베이스
- MySQL, PostgreSQL, MongoDB, Redis, Oracle, MariaDB, Elasticsearch 등

### 클라우드/인프라
- AWS, Azure, GCP, Docker, Kubernetes, Jenkins, Linux, Nginx 등

### AI/ML/데이터
- TensorFlow, PyTorch, Pandas, NumPy, Spark, Kafka 등

### 도구
- Git, GitHub, GitLab, Jira, Figma, Postman 등

## 추출 규칙:
1. **문장에서도 기술 추출**: "Python과 Django를 활용한 백엔드 개발" → ["Python", "Django"]
2. **리스트 형태도 추출**: "• Python\n• Django\n• PostgreSQL" → ["Python", "Django", "PostgreSQL"]
3. **쉼표 구분도 추출**: "Python, Django, React 경험자" → ["Python", "Django", "React"]
4. **한글을 영문으로**: "파이썬" → "Python", "장고" → "Django"
5. **버전 제거**: "Python 3.x" → "Python", "Django 4.0" → "Django"
6. **기술이 아닌 것 제외**: "팀워크", "성실성", "커뮤니케이션", "책임감" 등은 제외
7. **최소 3개 이상** 추출 (있다면 최대한 많이)

## JSON 형식:
{
  "company_name": "회사명",
  "position": "포지션명",
  "job_responsibilities": "주요 업무 내용 (원문 그대로, 줄바꿈 포함)",
  "required_qualifications": "필수 자격 요건 (원문 그대로, 줄바꿈 포함)",
  "preferred_qualifications": "우대 사항 (원문 그대로, 줄바꿈 포함)",
  "required_skills": ["Python", "Django", "PostgreSQL", "..."],
  "preferred_skills": ["Docker", "AWS", "..."],
  "experience_range": "신입/경력 (예: 신입, 2-4년, 5년 이상)",
  "deadline": "YYYY-MM-DD 또는 null"
}

## 예시:
입력 텍스트: "Python, Django를 활용한 백엔드 개발 경험 3년 이상. PostgreSQL 또는 MySQL 사용 경험. Docker 및 AWS 경험자 우대"
출력:
{
  "required_skills": ["Python", "Django", "PostgreSQL", "MySQL"],
  "preferred_skills": ["Docker", "AWS"]
}

⚠️ **중요**: required_skills와 preferred_skills 배열을 절대 비워두지 마세요! 이미지에서 기술 스택을 최대한 찾아내세요!"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_data  # data:image/jpeg;base64,... 형식
                                }
                            }
                        ]
                    }
                ],
                max_tokens=3000,  # 2000 → 3000 (더 많은 정보 추출)
                temperature=0.2   # 0.3 → 0.2 (더 정확한 추출)
            )

            content = response.choices[0].message.content

            # JSON 추출
            try:
                # JSON 코드 블록 제거
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0].strip()

                parsed_data = json.loads(content)
                parsed_data['source'] = 'image'
                parsed_data['raw_text'] = ''

                # 파싱 결과 SavedJobPosting에 저장
                saved_id = self._save_job_posting(request, parsed_data, source='image', source_url='')
                if saved_id:
                    parsed_data['saved_posting_id'] = saved_id

                return Response(parsed_data, status=status.HTTP_200_OK)
            except json.JSONDecodeError:
                return Response({
                    "error": "이미지에서 채용공고 정보를 추출할 수 없습니다.",
                    "raw_response": content
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "error": f"Vision API 오류: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _parse_from_text(self, request):
        """텍스트에서 채용공고 파싱"""
        text = request.data.get('text')
        if not text:
            return Response({
                "error": "텍스트가 필요합니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        parsed_data = self._extract_job_info_with_llm(text, source='text')

        # 파싱 결과 SavedJobPosting에 저장
        saved_id = self._save_job_posting(request, parsed_data, source='text', source_url='')
        if saved_id:
            parsed_data['saved_posting_id'] = saved_id

        return Response(parsed_data, status=status.HTTP_200_OK)

    def _save_job_posting(self, request, parsed_data: dict, source: str, source_url: str) -> int | None:
        """
        파싱된 채용공고를 SavedJobPosting에 저장한다.
        세션에 user_id가 없으면 저장하지 않는다.
        동일 사용자 + 동일 URL → update_or_create (중복 저장 방지)

        Returns:
            저장된 SavedJobPosting의 id (실패 시 None)
        """
        try:
            from core.models import SavedJobPosting, UserProfile

            # 세션에서 user_id 추출
            user_id = request.session.get('user_id') or request.session.get('_auth_user_id')
            if not user_id:
                return None

            user = UserProfile.objects.get(pk=user_id)

            defaults = {
                'company_name': parsed_data.get('company_name', ''),
                'position': parsed_data.get('position', ''),
                'job_responsibilities': parsed_data.get('job_responsibilities', ''),
                'required_qualifications': parsed_data.get('required_qualifications', ''),
                'preferred_qualifications': parsed_data.get('preferred_qualifications', ''),
                'required_skills': parsed_data.get('required_skills', []),
                'preferred_skills': parsed_data.get('preferred_skills', []),
                'experience_range': parsed_data.get('experience_range', ''),
                'deadline': parsed_data.get('deadline'),
                'source': source,
                'raw_text': parsed_data.get('raw_text', ''),
                'parsed_data': {k: v for k, v in parsed_data.items()
                                if k not in ('saved_posting_id',)},
            }

            if source == 'url' and source_url:
                saved, _ = SavedJobPosting.objects.update_or_create(
                    user=user, source_url=source_url, defaults=defaults
                )
            else:
                defaults['source_url'] = ''
                saved = SavedJobPosting.objects.create(user=user, **defaults)

            return saved.id

        except Exception as e:
            print(f"[JobPlanner] SavedJobPosting 저장 실패: {e}")
            return None

    def _extract_job_info_with_llm(self, text, source='text'):
        """
        LLM으로 채용공고 정보 추출

        비정형 텍스트에서 OpenAI GPT를 사용하여 구조화된 채용공고 정보를 추출합니다.
        회사명, 포지션, 업무 내용, 필수/우대 요건, 기술 스택 등을 JSON 형태로 변환합니다.

        Args:
            text (str): 채용공고 원문 텍스트
            source (str): 데이터 출처 ('url', 'text', 'image')

        Returns:
            dict: 구조화된 채용공고 정보
        """
        print(f"\n📄 [LLM 파싱] 입력 텍스트 ({len(text)}자)")
        print(f"   앞 500자: {text[:500]}")

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            # Fallback: API 키가 없을 때 기본 응답 반환
            return {
                "source": source,
                "raw_text": text,
                "company_name": "알 수 없음",
                "position": "개발자",
                "job_responsibilities": text[:200] if len(text) > 200 else text,
                "required_qualifications": "정보 없음",
                "preferred_qualifications": "정보 없음",
                "required_skills": [],
                "preferred_skills": [],
                "experience_range": "",
                "deadline": None
            }

        try:
            client = openai.OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """당신은 채용공고 파싱 전문가입니다.
아래 규칙을 반드시 따르세요:
1. 텍스트에 실제로 존재하는 정보만 추출한다.
2. 텍스트에 없는 정보는 절대 만들어내지 마라. 없으면 빈 문자열("") 또는 빈 배열([])로 반환한다.
3. 반드시 JSON만 출력한다."""
                    },
                    {
                        "role": "user",
                        "content": f"""다음 채용공고 텍스트에서 정보를 추출하세요.

{text[:5000]}

위 텍스트를 바탕으로 아래 JSON 키를 채우세요. 텍스트에 없는 정보는 "" 또는 []로 두세요:
- company_name: string
- position: string
- job_responsibilities: string
- required_qualifications: string
- preferred_qualifications: string
- required_skills: array of strings
- preferred_skills: array of strings
- experience_range: string
- deadline: null"""
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=2000,
            )

            content = response.choices[0].message.content

            # JSON 추출
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()

            parsed_data = json.loads(content)
            parsed_data['source'] = source
            parsed_data['raw_text'] = text

            # 파싱 결과 로그 출력
            print(f"\n✅ [LLM 파싱 완료]")
            print(f"   회사명: {parsed_data.get('company_name', '없음')}")
            print(f"   포지션: {parsed_data.get('position', '없음')}")
            print(f"   필수 스킬: {len(parsed_data.get('required_skills', []))}개 - {parsed_data.get('required_skills', [])}")
            print(f"   우대 스킬: {len(parsed_data.get('preferred_skills', []))}개 - {parsed_data.get('preferred_skills', [])}")
            print(f"   주요 업무: {len(parsed_data.get('job_responsibilities', ''))}자 - {parsed_data.get('job_responsibilities', '')[:100]}...")
            print(f"   필수 요건: {len(parsed_data.get('required_qualifications', ''))}자 - {parsed_data.get('required_qualifications', '')[:100]}...")

            return parsed_data

        except Exception as e:
            print(f"⚠️  LLM 파싱 실패: {e}")
            # Fallback
            return {
                "source": source,
                "raw_text": text,
                "company_name": "알 수 없음",
                "position": "개발자",
                "job_responsibilities": text[:200] if len(text) > 200 else text,
                "required_qualifications": "정보 없음",
                "preferred_qualifications": "정보 없음",
                "required_skills": [],
                "preferred_skills": [],
                "experience_range": "",
                "deadline": None
            }


@method_decorator(csrf_exempt, name='dispatch')
class JobPlannerAnalyzeView(APIView):
    """
    스킬 매칭 분석 API

    사용자의 스킬셋과 채용공고의 요구 스킬을 비교 분석하여
    준비도 점수, 스킬 갭, 매칭 정보 등을 제공합니다.

    주요 기능:
    1. 3단계 스킬 매칭 시스템 (정확 일치 → 동의어 → 임베딩 유사도)
    2. 한영 스킬 정규화 (예: "파이썬" → "python")
    3. 준비도 점수 계산 (매칭률 + 경력 적합도 + 숙련도)
    4. 맞춤형 인사이트 생성
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    # 한영 스킬 동의어 사전
    # 다양한 표기를 통일된 형태로 정규화하기 위한 매핑 테이블
    # 예: "파이썬", "Python", "python" → 모두 "python"으로 통일
    # 참고: 'python': 'python' 같은 중복은 불필요 (_normalize_skill에서 자동 처리)
    SKILL_SYNONYMS = {
        # 프로그래밍 언어
        '파이썬': 'python',
        '자바': 'java',
        '자바스크립트': 'javascript', 'js': 'javascript',
        '타입스크립트': 'typescript', 'ts': 'typescript',
        'c++': 'cpp',
        'c#': 'csharp', '씨샵': 'csharp',
        '고': 'go', 'golang': 'go',
        '코틀린': 'kotlin',
        '스위프트': 'swift',
        '루비': 'ruby',

        # 프레임워크/라이브러리
        '장고': 'django',
        '플라스크': 'flask',
        '스프링': 'spring', '스프링부트': 'springboot',
        '리액트': 'react', 'reactjs': 'react',
        '뷰': 'vue', 'vuejs': 'vue',
        '앵귤러': 'angular',
        '노드': 'node', 'nodejs': 'node', 'node.js': 'node',
        '익스프레스': 'express', 'expressjs': 'express',
        '넥스트': 'next', 'nextjs': 'next', 'next.js': 'next',
        '넥스트제이에스': 'next',
        '넥스트js': 'next',

        # 데이터베이스
        '마이에스큐엘': 'mysql',
        '포스트그레': 'postgresql',
        '몽고디비': 'mongodb',
        '레디스': 'redis',
        '오라클': 'oracle',

        # 클라우드/인프라
        '애저': 'azure',
        '구글클라우드': 'gcp',
        '도커': 'docker',
        '쿠버네티스': 'kubernetes', 'k8s': 'kubernetes',

        # AI/ML
        '텐서플로': 'tensorflow',
        '파이토치': 'pytorch',
        '케라스': 'keras',
        '사이킷런': 'sklearn', 'scikit-learn': 'sklearn',

        # 도구
        '깃': 'git',
        '깃허브': 'github',
        '지라': 'jira',
    }

    def _normalize_skill(self, skill):
        """
        스킬명을 정규화 (한글->영어, 소문자 변환)

        동의어 사전을 사용하여 다양한 표기를 통일된 형태로 변환합니다.
        예: "파이썬" → "python", "장고" → "django", "JS" → "javascript"

        Args:
            skill (str): 원본 스킬명

        Returns:
            str: 정규화된 스킬명 (소문자)
        """
        skill_lower = skill.lower().strip()
        return self.SKILL_SYNONYMS.get(skill_lower, skill_lower)

    def _extract_skills_from_text(self, required_text, preferred_text, responsibilities_text):
        """
        필수/우대 요건 및 업무 텍스트에서 기술 스택과 역량을 추출
        - 정규식 패턴 매칭으로 빠르게 추출
        - LLM 없이도 작동하도록 구현
        """
        import re

        # 전체 텍스트 결합
        full_text = f"{required_text} {preferred_text} {responsibilities_text}"

        # 알려진 기술 스택 키워드 (대소문자 구분 없이)
        tech_keywords = [
            # 언어
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Kotlin',
            'Swift', 'Ruby', 'PHP', 'Rust', 'Scala', 'R',
            '파이썬', '자바', '자바스크립트', '타입스크립트', '코틀린',

            # 프레임워크
            'Django', 'Flask', 'FastAPI', 'Spring', 'SpringBoot', 'React', 'Vue',
            'Angular', 'Next.js', 'Nuxt', 'Express', 'Node.js', 'Nest.js',
            '장고', '플라스크', '스프링', '리액트', '뷰', '앵귤러', '노드',

            # 데이터베이스
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'MariaDB',
            'SQLite', 'Elasticsearch', 'DynamoDB', 'Cassandra',
            '마이에스큐엘', '몽고디비', '레디스', '오라클',

            # 클라우드/인프라
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI',
            'Terraform', 'Ansible', 'Linux', 'Nginx', 'Apache',
            '도커', '쿠버네티스', '리눅스',

            # AI/ML/Data
            'TensorFlow', 'PyTorch', 'Keras', 'scikit-learn', 'Pandas', 'NumPy',
            'Spark', 'Hadoop', 'Airflow', 'Kafka',
            '텐서플로', '파이토치',

            # 도구
            'Git', 'GitHub', 'GitLab', 'Jira', 'Confluence', 'Slack', 'Notion',
            'Figma', 'Postman', 'Swagger',
            '깃', '깃허브', '지라',

            # 방법론/개념
            'Agile', 'Scrum', 'Kanban', 'CI/CD', 'DevOps', 'TDD', 'DDD',
            'Microservices', 'REST', 'GraphQL', 'gRPC', 'WebSocket',
            '애자일', '스크럼', '칸반', '마이크로서비스'
        ]

        found_skills = []

        # 각 키워드가 텍스트에 있는지 확인 (단어 경계 고려)
        for keyword in tech_keywords:
            # 대소문자 구분 없이, 단어 경계를 고려한 검색
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, full_text, re.IGNORECASE):
                # 이미 추가되지 않았으면 추가
                normalized = self._normalize_skill(keyword)
                if normalized not in [self._normalize_skill(s) for s in found_skills]:
                    found_skills.append(keyword)

        # 필수와 우대 구분 (간단한 휴리스틱)
        required_found = []
        preferred_found = []

        for skill in found_skills:
            # 필수 요건 텍스트에 있으면 필수로 분류
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, required_text, re.IGNORECASE):
                required_found.append(skill)
            elif re.search(pattern, preferred_text, re.IGNORECASE):
                preferred_found.append(skill)
            else:
                # 업무 내용에만 있으면 필수로 간주
                required_found.append(skill)

        return {
            'required': required_found,
            'preferred': preferred_found
        }

    def post(self, request):
        try:
            # 기본 프로필
            user_skills = request.data.get('user_skills', [])
            skill_levels = request.data.get('skill_levels', {})  # {"Python": 4, "Django": 3}
            experience_years = int(request.data.get('experience_years', 0))

            # 상세 프로필 (선택사항)
            name = request.data.get('name', '지원자')
            current_role = request.data.get('current_role', '')
            education = request.data.get('education', '')
            certifications = request.data.get('certifications', [])
            career_goals = request.data.get('career_goals', '')
            available_prep_days = request.data.get('available_prep_days', None)

            # 채용공고 정보
            required_skills = request.data.get('required_skills', [])
            preferred_skills = request.data.get('preferred_skills', [])
            experience_range = request.data.get('experience_range', '')

            # 필수/우대 요건 전체 텍스트 (추가 역량 추출용)
            required_qualifications = request.data.get('required_qualifications', '')
            preferred_qualifications = request.data.get('preferred_qualifications', '')
            job_responsibilities = request.data.get('job_responsibilities', '')

            if not user_skills:
                return Response({
                    "error": "사용자 스킬 정보가 필요합니다."
                }, status=status.HTTP_400_BAD_REQUEST)

            # 필수 요건 텍스트에서 추가 스킬/역량 추출
            extracted_skills = self._extract_skills_from_text(
                required_qualifications,
                preferred_qualifications,
                job_responsibilities
            )

            # 기존 스킬 배열과 추출된 스킬 결합 (중복 제거)
            all_required_skills = list(set(required_skills + extracted_skills['required']))
            all_preferred_skills = list(set(preferred_skills + extracted_skills['preferred']))

            # 최소 1개 이상의 필수 스킬이 있어야 함
            if not all_required_skills:
                all_required_skills = extracted_skills['required'] if extracted_skills['required'] else ['개발 역량']

            print(f"📊 필수 스킬: {len(required_skills)}개 → {len(all_required_skills)}개 (텍스트 분석 추가)")

            # 스킬 정규화 (한영 통일)
            user_skills_normalized = [self._normalize_skill(s) for s in user_skills]
            required_skills_normalized = [self._normalize_skill(s) for s in all_required_skills]

            matched_skills = []
            missing_skills = []
            matched_indices = set()  # 이미 매칭된 사용자 스킬 인덱스

            # === 3단계 매칭 시스템 ===
            # 각 필수 스킬에 대해 사용자 스킬 중 가장 적합한 것을 찾습니다.
            # 단계별로 엄격한 기준부터 적용하여 정확도를 높입니다.
            # Stage 1: 정확 일치 (100% 매칭)
            # Stage 2: 동의어 매칭 (95% 매칭)
            # Stage 3: 임베딩 유사도 (75%+ 매칭)

            # Stage 3 배치 임베딩 캐시 (루프 시작 전에는 None, 첫 Stage 3 필요 시 일괄 계산)
            user_embeddings_cache = None
            req_embeddings_cache = None

            for i, req_skill in enumerate(all_required_skills):
                req_normalized = required_skills_normalized[i]
                best_match = None
                best_score = 0.0
                best_idx = -1
                match_type = None

                # 1단계: 정확 일치 (정규화 후)
                # 예: "Python" vs "python", "파이썬" vs "Python" (모두 "python"으로 정규화됨)
                for j, user_skill in enumerate(user_skills):
                    if j in matched_indices:
                        continue  # 이미 다른 스킬과 매칭된 경우 스킵 (1:1 매칭 보장)
                    user_normalized = user_skills_normalized[j]
                    if user_normalized == req_normalized:
                        best_match = user_skill
                        best_score = 1.0  # 완벽한 매칭
                        best_idx = j
                        match_type = "exact"
                        break

                # 2단계: 동의어 매칭 (정확 일치 실패 시)
                # 원본 스킬을 정규화했을 때 같은 값으로 변환되는지 확인
                # 예: "Node.js" vs "Node", "React" vs "ReactJS"
                if not best_match:
                    for j, user_skill in enumerate(user_skills):
                        if j in matched_indices:
                            continue
                        # 원본 스킬들이 동의어 사전을 통해 같은 값으로 정규화되는지 체크
                        user_original_normalized = self._normalize_skill(user_skill)
                        req_original_normalized = self._normalize_skill(req_skill)

                        # 정규화 전에는 달랐지만, 정규화 후 같아지면 동의어로 간주
                        if user_original_normalized == req_original_normalized and user_skill.lower() != req_skill.lower():
                            best_match = user_skill
                            best_score = 0.95  # 거의 완벽한 매칭
                            best_idx = j
                            match_type = "synonym"
                            break

                # 3단계: 임베딩 유사도 (높은 threshold)
                # 의미론적 유사도를 통해 관련 스킬 매칭
                # 예: "Flask" vs "Django" (둘 다 Python 웹 프레임워크)
                if not best_match:
                    # 첫 Stage 3 진입 시 모든 스킬을 한 번에 배치 인코딩
                    if user_embeddings_cache is None:
                        all_texts = user_skills_normalized + required_skills_normalized
                        all_embs = _embed_texts(all_texts)
                        user_embeddings_cache = all_embs[:len(user_skills_normalized)]
                        req_embeddings_cache = all_embs[len(user_skills_normalized):]

                    req_emb = req_embeddings_cache[i:i+1]

                    for j, user_skill in enumerate(user_skills):
                        if j in matched_indices:
                            continue
                        user_emb = user_embeddings_cache[j:j+1]
                        # 코사인 유사도 계산 (정규화된 벡터의 내적)
                        similarity = float((user_emb @ req_emb.T)[0][0])

                        # 높은 threshold (0.85) - 정확한 매칭만 허용
                        if similarity >= 0.85 and similarity > best_score:
                            best_match = user_skill
                            best_score = similarity
                            best_idx = j
                            match_type = "similar"

                # 매칭 결과 저장
                if best_match and best_score >= 0.85:  # 최소 85% 유사도 기준
                    matched_skills.append({
                        "required": req_skill,        # 채용공고의 필수 스킬
                        "user_skill": best_match,     # 매칭된 사용자 스킬
                        "similarity": round(best_score, 3),  # 유사도 점수 (0.85~1.0)
                        "match_type": match_type      # 매칭 방식 (exact/synonym/similar)
                    })
                    matched_indices.add(best_idx)  # 중복 매칭 방지
                else:
                    # 매칭 실패 - missing_skills에 추가
                    # 가장 가까운 스킬을 참고용으로 저장
                    closest_user = user_skills[0] if user_skills else "없음"
                    closest_score = 0.0
                    if user_skills and best_idx >= 0:
                        closest_user = user_skills[best_idx] if best_idx < len(user_skills) else user_skills[0]
                        closest_score = best_score

                    missing_skills.append({
                        "required": req_skill,
                        "closest_match": closest_user,
                        "similarity": round(closest_score, 3)
                    })

            # === 점수 계산 ===

            # 매칭률: 필수 스킬 중 얼마나 보유하고 있는지
            match_rate = len(matched_skills) / len(all_required_skills) if all_required_skills else 0

            # 경력 적합도: 요구 경력 범위와 사용자 경력 비교
            exp_fit = self._calculate_exp_fit(experience_years, experience_range)

            # 숙련도 가중치 (스킬 레벨이 있으면 반영)
            # 단순히 스킬을 보유하는 것뿐 아니라 숙련도까지 고려
            proficiency_score = 0.0
            if skill_levels and matched_skills:
                level_sum = 0
                for m in matched_skills:
                    user_skill = m["user_skill"]
                    level = skill_levels.get(user_skill, 3)  # 기본값 3 (중급)
                    level_sum += level
                # 평균 숙련도를 0.0-1.0 범위로 정규화 (1-5 레벨 → 0.2-1.0)
                proficiency_score = round(level_sum / len(matched_skills) / 5.0, 3) if matched_skills else 0.0

            # 준비도 점수 개선 (더 직관적인 계산)
            # 1. 기본: 매칭률 (60%)
            # 2. 경력 적합도 (25%)
            # 3. 숙련도 (15%)
            base_score = match_rate * 0.60
            exp_score = exp_fit * 0.25
            skill_score = proficiency_score * 0.15 if proficiency_score > 0 else 0

            readiness = round(base_score + exp_score + skill_score, 3)

            # readiness가 1.0을 초과하지 않도록
            readiness = min(readiness, 1.0)

            # skill_gap: 매칭되지 않은 비율
            skill_gap = round(1.0 - match_rate, 3)

            # 추가 인사이트
            insights = self._generate_insights(
                name, current_role, education, certifications,
                career_goals, available_prep_days,
                matched_skills, missing_skills, readiness, skill_gap
            )

            return Response({
                "readiness_score": readiness,
                "skill_gap_score": skill_gap,
                "experience_fit": exp_fit,
                "proficiency_score": proficiency_score,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "insights": insights,
                "profile_summary": {
                    "name": name,
                    "current_role": current_role,
                    "education": education,
                    "certifications": certifications,
                    "career_goals": career_goals,
                    "available_prep_days": available_prep_days
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"❌ 분석 에러: {e}")
            print(traceback.format_exc())
            return Response({
                "error": f"분석 중 오류 발생: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _calculate_exp_fit(self, years, req_range):
        """
        경력 적합도 계산

        채용공고의 요구 경력 범위와 사용자의 경력을 비교하여
        적합도를 0.0~1.0 사이의 점수로 반환합니다.

        Args:
            years (int): 사용자의 경력 (년)
            req_range (str): 요구 경력 범위 (예: "3-5년", "5년 이상", "신입")

        Returns:
            float: 경력 적합도 점수 (0.0-1.0)
                - 1.0: 요구 범위 내에 정확히 포함
                - 0.7-1.0: 경력 초과 (경험 많음)
                - 0.0-1.0: 경력 부족 (years/lo 비율)
        """
        import re
        # 정규식으로 숫자 추출 (예: "3-5년" → [3, 5], "신입" → [])
        nums = re.findall(r'\d+', req_range)
        if not nums:
            # 숫자 정보가 없으면 중간 점수 반환
            return 0.7

        # 최소 경력과 최대 경력 파싱
        lo = int(nums[0])
        hi = int(nums[-1]) if len(nums) > 1 else lo + 2  # 단일 숫자면 +2년 범위

        if lo <= years <= hi:
            # 요구 범위 내: 완벽한 적합
            return 1.0
        elif years < lo:
            # 경력 부족: 비율로 계산 (예: 2년 경력 / 3년 요구 = 0.67)
            return max(0.0, years / lo)
        else:
            # 경력 초과: 약간의 감점 (경력이 너무 많으면 오버스펙)
            # 예: 8년 경력, 5년 요구 → 1.0 - (8-5)*0.05 = 0.85
            return max(0.7, 1.0 - (years - hi) * 0.05)

    def _generate_insights(self, name, current_role, education, certifications,
                          career_goals, available_prep_days,
                          matched_skills, missing_skills, readiness, skill_gap):
        """
        프로필 기반 인사이트 생성

        사용자의 프로필 정보와 분석 결과를 바탕으로
        맞춤형 조언과 인사이트를 생성합니다.

        Args:
            name, current_role, education, certifications: 프로필 정보
            career_goals: 커리어 목표
            available_prep_days: 준비 가능한 기간 (일)
            matched_skills, missing_skills: 매칭 결과
            readiness, skill_gap: 준비도 점수

        Returns:
            list: 인사이트 목록 (각 인사이트는 type, title, message 포함)
        """
        insights = []

        # 준비도 기반 조언
        if readiness >= 0.7:
            insights.append({
                "type": "positive",
                "title": "높은 준비도",
                "message": "현재 스킬셋이 공고 요구사항과 잘 맞습니다. 자신감을 갖고 지원하세요!"
            })
        elif readiness >= 0.5:
            insights.append({
                "type": "neutral",
                "title": "중간 준비도",
                "message": f"부족한 스킬 {len(missing_skills)}개를 보완하면 경쟁력이 크게 향상됩니다."
            })
        else:
            insights.append({
                "type": "warning",
                "title": "준비 필요",
                "message": "핵심 스킬 보완이 필요합니다. 우선순위를 정해 집중적으로 학습하세요."
            })

        # 준비 기간 조언
        if available_prep_days:
            days = int(available_prep_days)
            if days < 7 and skill_gap > 0.4:
                insights.append({
                    "type": "warning",
                    "title": "시간 부족",
                    "message": f"준비 기간({days}일)이 부족 스킬 수({len(missing_skills)}개)에 비해 짧습니다. 가장 중요한 스킬 1-2개에 집중하세요."
                })
            elif days >= 30:
                insights.append({
                    "type": "positive",
                    "title": "충분한 준비 시간",
                    "message": f"{days}일 동안 체계적으로 학습하면 준비도를 크게 향상시킬 수 있습니다."
                })

        # 자격증 활용
        if certifications and len(certifications) > 0:
            insights.append({
                "type": "positive",
                "title": "자격증 보유",
                "message": f"보유 자격증({', '.join(certifications)})을 이력서와 면접에서 적극 어필하세요."
            })

        # 커리어 목표 일치성
        if career_goals:
            insights.append({
                "type": "neutral",
                "title": "커리어 목표 확인",
                "message": f"목표({career_goals})와 이 포지션이 일치하는지 다시 한번 확인하세요."
            })

        # 현재 직무와의 연관성
        if current_role:
            insights.append({
                "type": "neutral",
                "title": "경력 연속성",
                "message": f"현재 직무({current_role})와의 연관성을 면접에서 강조하면 좋습니다."
            })

        return insights


@method_decorator(csrf_exempt, name='dispatch')
class JobPlannerAgentQuestionsView(APIView):
    """
    동적 질문 생성 API

    부족한 스킬에 대해 LLM을 활용하여 맞춤형 질문을 생성합니다.
    사용자의 현재 수준, 학습 계획, 실무 경험 등을 파악하기 위한
    구체적이고 실용적인 질문을 제공합니다.

    주요 기능:
    - 부족한 스킬별 맞춤 질문 생성 (최대 5개)
    - 구체적 경험 파악 질문
    - 학습 준비도 확인 질문
    - 실무 적용 가능성 평가 질문
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            missing_skills = request.data.get('missing_skills', [])
            matched_skills = request.data.get('matched_skills', [])
            user_profile = request.data.get('user_profile', {})

            if not missing_skills:
                return Response({
                    "questions": [],
                    "message": "부족한 스킬이 없어 추가 질문이 필요하지 않습니다."
                }, status=status.HTTP_200_OK)

            # LLM으로 동적 질문 생성
            questions = self._generate_questions_with_llm(
                missing_skills, matched_skills, user_profile
            )

            return Response({
                "questions": questions,
                "total_questions": len(questions)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"❌ 질문 생성 에러: {e}")
            print(traceback.format_exc())
            return Response({
                "error": f"질문 생성 중 오류 발생: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _generate_questions_with_llm(self, missing_skills, matched_skills, user_profile):
        """LLM으로 맞춤형 질문 생성"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            # Fallback: 기본 질문
            return [
                {
                    "id": f"q_{i}",
                    "skill": skill['required'],
                    "question": f"{skill['required']}에 대한 경험이나 학습 계획을 간단히 설명해주세요.",
                    "type": "text",
                    "required": True
                }
                for i, skill in enumerate(missing_skills[:3])
            ]

        try:
            client = openai.OpenAI(api_key=api_key)

            # 최대 5개 스킬까지만 질문 생성
            skills_to_ask = missing_skills[:5]

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """당신은 IT 채용 및 커리어 전문 코치입니다.
부족한 스킬에 대해 실제 경험과 준비 상태를 파악할 수 있는 질문을 생성하세요.

**질문 생성 원칙**:
1. 구체적 경험 파악: "프로젝트에서 사용한 경험", "문제 해결 사례" 등
2. 학습 준비도 확인: "현재 학습 중", "학습 계획", "예상 소요 기간" 등
3. 실무 적용 가능성: "비슷한 기술 경험", "관련 개념 이해도" 등
4. 한국어로 자연스럽게 작성
5. 면접관이 물어볼 법한 실용적 질문"""
                    },
                    {
                        "role": "user",
                        "content": f"""다음 정보를 바탕으로 질문을 생성하세요:

부족한 스킬: {json.dumps([s['required'] for s in skills_to_ask], ensure_ascii=False)}
보유한 스킬: {json.dumps([s['user_skill'] for s in matched_skills], ensure_ascii=False)}
사용자 프로필: {json.dumps(user_profile, ensure_ascii=False)}

각 부족한 스킬에 대해 1개씩 질문을 만들어주세요. 질문은:
- 구체적이고 실용적이어야 함
- 현재 수준 파악 또는 학습 계획 확인
- 한국어로 작성

JSON 형식:
{{
  "questions": [
    {{
      "id": "q_0",
      "skill": "스킬명",
      "question": "질문 내용",
      "type": "text",
      "required": true
    }}
  ]
}}"""
                    }
                ],
                temperature=0.7
            )

            content = response.choices[0].message.content

            # JSON 추출
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()

            data = json.loads(content)
            return data.get('questions', [])

        except Exception as e:
            print(f"⚠️  LLM 질문 생성 실패: {e}")
            # Fallback
            return [
                {
                    "id": f"q_{i}",
                    "skill": skill['required'],
                    "question": f"{skill['required']}에 대한 경험이나 학습 계획을 간단히 설명해주세요.",
                    "type": "text",
                    "required": True
                }
                for i, skill in enumerate(skills_to_ask)
            ]


@method_decorator(csrf_exempt, name='dispatch')
class JobPlannerAgentReportView(APIView):
    """
    최종 종합 보고서 생성 API
    - SWOT 분석
    - 면접 예상 질문 5개
    - 경험 포장 가이드
    - 실행 전략
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # 분석 결과 데이터
            job_data = request.data.get('job_data', {})
            analysis_result = request.data.get('analysis_result', {})
            company_analysis = request.data.get('company_analysis', {})
            agent_answers = request.data.get('agent_answers', {})  # 에이전트 질문 답변

            # LLM으로 종합 보고서 생성
            available_prep_days = analysis_result.get('profile_summary', {}).get('available_prep_days')
            report = self._generate_report_with_llm(
                job_data, analysis_result, company_analysis, agent_answers, available_prep_days
            )

            return Response(report, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"❌ 보고서 생성 에러: {e}")
            print(traceback.format_exc())
            return Response({
                "error": f"보고서 생성 중 오류 발생: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _generate_report_with_llm(self, job_data, analysis_result, company_analysis, agent_answers, available_prep_days=None):
        """LLM으로 최종 종합 보고서 생성"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {
                "error": "OPENAI_API_KEY가 설정되지 않았습니다.",
                "swot": {
                    "strengths": ["스킬 매칭률이 높습니다"],
                    "weaknesses": ["일부 스킬이 부족합니다"],
                    "opportunities": ["성장 가능성이 있습니다"],
                    "threats": ["경쟁이 치열할 수 있습니다"]
                },
                "interview_questions": [],
                "experience_packaging": [],
                "execution_strategy": ""
            }

        try:
            client = openai.OpenAI(api_key=api_key)

            # 준비 기간에 따른 전략 기간 레이블 생성
            print(f"[DEBUG] available_prep_days = {available_prep_days}, type = {type(available_prep_days)}")

            # 타입 변환 (문자열이나 숫자 모두 처리)
            try:
                days = int(float(available_prep_days)) if available_prep_days else 0
            except (ValueError, TypeError):
                days = 0

            if days > 0:
                print(f"[INFO] 준비 기간 {days}일 기반으로 전략 기간 설정")
                if days <= 7:
                    short_term_label = f"단기 ({days}일)"
                    mid_term_label = "중기 (2주)"
                elif days <= 14:
                    short_term_label = "단기 (1주)"
                    mid_term_label = f"중기 ({days}일)"
                elif days <= 21:
                    short_term_label = "단기 (1주)"
                    mid_term_label = f"중기 (3주, {days}일)"
                elif days <= 30:
                    short_term_label = "단기 (1-2주)"
                    mid_term_label = f"중기 (1개월, {days}일)"
                else:
                    short_term_label = "단기 (1-2주)"
                    mid_term_label = f"중기 (1-2개월, {days}일)"
                prep_days_info = f"\n- 준비 가능 기간: {days}일"
            else:
                print(f"[WARN] 준비 기간 정보 없음, 기본값 사용")
                short_term_label = "단기 (1-2주)"
                mid_term_label = "중기 (1개월)"
                prep_days_info = ""

            # 컨텍스트 구성
            context = f"""
채용공고:
- 회사: {job_data.get('company_name', '미정')}
- 포지션: {job_data.get('position', '개발자')}
- 필수 스킬: {', '.join(job_data.get('required_skills', []))}
- 우대 스킬: {', '.join(job_data.get('preferred_skills', []))}

분석 결과:
- 준비도: {analysis_result.get('readiness_score', 0)}
- 스킬 갭: {analysis_result.get('skill_gap_score', 0)}
- 매칭된 스킬: {len(analysis_result.get('matched_skills', []))}개
- 부족한 스킬: {len(analysis_result.get('missing_skills', []))}개{prep_days_info}

사용자 프로필:
{json.dumps(analysis_result.get('profile_summary', {}), ensure_ascii=False)}

에이전트 질문 답변:
{json.dumps(agent_answers, ensure_ascii=False)}

기업 분석:
{json.dumps(company_analysis, ensure_ascii=False) if company_analysis else '정보 없음'}
"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """당신은 전문 커리어 컨설턴트입니다.
취업 준비생을 위한 종합 보고서를 작성하세요.
구체적이고 실행 가능한 조언을 제공해야 합니다."""
                    },
                    {
                        "role": "user",
                        "content": f"""{context}

위 정보를 바탕으로 다음 내용을 포함한 종합 보고서를 JSON 형식으로 작성하세요:

1. **SWOT 분석**
   - Strengths: 강점 3-5개 (구체적으로)
   - Weaknesses: 약점 2-4개 (보완 방법 포함)
   - Opportunities: 기회 2-3개
   - Threats: 위협 요소 1-2개

2. **면접 예상 질문 5개**
   - 해당 포지션/회사에 특화된 질문
   - 답변 가이드 포함

3. **경험 포장 가이드**
   - 이력서/포트폴리오에서 강조할 점
   - 프로젝트 경험 어필 방법
   - 부족한 스킬을 보완하는 방법

4. **실행 전략**
   - {short_term_label}: 즉시 할 일
   - {mid_term_label}: 스킬 보완
   - 지원 시점: 최적 타이밍

JSON 형식:
{{
  "swot": {{
    "strengths": ["강점1", "강점2", ...],
    "weaknesses": ["약점1 (보완: ...)", "약점2 (보완: ...)", ...],
    "opportunities": ["기회1", "기회2", ...],
    "threats": ["위협1", "위협2", ...]
  }},
  "interview_questions": [
    {{
      "question": "질문 내용",
      "answer_guide": "답변 가이드 (3-5문장)",
      "tips": "추가 팁"
    }},
    ...5개
  ],
  "experience_packaging": {{
    "resume_highlights": ["이력서에 강조할 점1", "강조할 점2", ...],
    "portfolio_tips": ["포트폴리오 팁1", "팁2", ...],
    "skill_compensation": ["부족 스킬 보완법1", "보완법2", ...]
  }},
  "execution_strategy": {{
    "immediate": ["즉시 할 일1", "할 일2", ...],
    "short_term": ["{short_term_label} 내 할 일1", "할 일2", ...],
    "mid_term": ["{mid_term_label} 내 할 일1", "할 일2", ...],
    "application_timing": "최적 지원 시점 및 이유"
  }},
  "final_message": "최종 격려 메시지 (2-3문장)"
}}"""
                    }
                ],
                temperature=0.7
            )

            content = response.choices[0].message.content

            # JSON 추출
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()

            report = json.loads(content)
            return report

        except Exception as e:
            print(f"⚠️  LLM 보고서 생성 실패: {e}")
            return {
                "error": f"보고서 생성 실패: {str(e)}",
                "swot": {
                    "strengths": ["분석 정보가 부족합니다"],
                    "weaknesses": [],
                    "opportunities": [],
                    "threats": []
                },
                "interview_questions": [],
                "experience_packaging": {
                    "resume_highlights": [],
                    "portfolio_tips": [],
                    "skill_compensation": []
                },
                "execution_strategy": {
                    "immediate": [],
                    "short_term": [],
                    "mid_term": [],
                    "application_timing": ""
                },
                "final_message": "정보가 부족하여 상세 보고서를 생성할 수 없습니다."
            }


@method_decorator(csrf_exempt, name='dispatch')
class JobPlannerRecommendView(APIView):
    """
    채용공고 추천 API

    현재 분석 중인 공고보다 더 적합한 대안 공고를 추천합니다.
    사람인을 실시간 크롤링하여 최신 공고를 수집하고,
    3단계 매칭 시스템으로 사용자 스킬과 비교합니다.

    주요 기능:
    - 실시간 채용공고 크롤링 (사람인)
    - 3단계 스킬 매칭 시스템 적용
    - 중복 공고 필터링
    - 매칭률 기반 정렬 및 추천 이유 생성

    추천 조건:
    - 최소 30% 이상 매칭
    - 현재 준비도보다 높은 매칭률
    - 또는 비슷한 수준이면서 새로운 기술 학습 기회 제공
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    # JobPlannerAnalyzeView와 동일한 스킬 동의어 사전 재사용
    SKILL_SYNONYMS = JobPlannerAnalyzeView.SKILL_SYNONYMS

    def _normalize_skill(self, skill):
        """
        스킬명을 정규화 (한글->영어, 소문자 변환)

        JobPlannerAnalyzeView와 동일한 정규화 로직을 사용하여
        일관된 스킬 매칭을 보장합니다.

        Args:
            skill (str): 원본 스킬명

        Returns:
            str: 정규화된 스킬명 (소문자)
        """
        skill_lower = skill.lower().strip()
        return self.SKILL_SYNONYMS.get(skill_lower, skill_lower)

    def post(self, request):
        try:
            if not CRAWLER_AVAILABLE:
                return Response({
                    "error": "필요한 라이브러리가 설치되지 않았습니다."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 사용자 정보
            user_skills = request.data.get('user_skills', [])
            skill_levels = request.data.get('skill_levels', {})
            readiness_score = float(request.data.get('readiness_score', 0.0))
            job_position = request.data.get('job_position', '개발자')  # 관심 직무

            # 현재 분석 중인 공고 정보 (중복 제거용)
            current_job_url = request.data.get('current_job_url', '')
            current_job_company = request.data.get('current_job_company', '')
            current_job_title = request.data.get('current_job_title', '')

            if not user_skills:
                return Response({
                    "error": "사용자 스킬 정보가 필요합니다."
                }, status=status.HTTP_400_BAD_REQUEST)

            print(f"🔍 추천 공고 검색 시작 (준비도: {readiness_score}, 스킬: {user_skills})")
            print(f"📍 원본 직무: '{job_position}'")

            # 직무명을 검색에 적합하게 정제
            search_keyword = self._simplify_job_position(job_position)
            print(f"🔍 검색 키워드: '{search_keyword}'")

            if current_job_url:
                print(f"🚫 제외할 공고: {current_job_company} - {current_job_title}")

            # 1. 사람인에서 공고 크롤링 (정확도순, 최대 30개)
            job_listings = []

            # 사람인 크롤링
            print(f"🔍 사람인 크롤링 시작: '{search_keyword}' 검색")
            saramin_jobs = self._crawl_saramin(search_keyword, limit=15)
            job_listings.extend(saramin_jobs)
            print(f"✅ 사람인: {len(saramin_jobs)}개 공고")

            if not job_listings:
                return Response({
                    "recommendations": [],
                    "message": "현재 추천 가능한 공고가 없습니다."
                }, status=status.HTTP_200_OK)

            # 1.5. 사용자가 이미 분석한 공고 제외
            filtered_listings = self._filter_duplicate_jobs(
                job_listings, current_job_url, current_job_company, current_job_title
            )
            print(f"🔍 중복 제거 후: {len(filtered_listings)}개 공고")

            # 1.7. 개별 공고 페이지 파싱으로 실제 기술 스킬 보완 (병렬)
            print(f"🔍 개별 공고 상세 파싱 시작 (5개씩 병렬)...")
            filtered_listings = self._enrich_jobs_with_detail_skills(filtered_listings)
            print(f"✅ 상세 파싱 완료")

            # 2. 스킬 매칭으로 추천 공고 선정
            recommendations = self._match_jobs_with_skills(
                filtered_listings, user_skills, skill_levels, readiness_score
            )

            print(f"✅ 최종 추천: {len(recommendations)}개")

            return Response({
                "recommendations": recommendations[:5],  # 최대 10개
                "total_found": len(job_listings),
                "total_recommendations": len(recommendations)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"❌ 추천 에러: {e}")
            print(traceback.format_exc())
            return Response({
                "error": f"추천 중 오류 발생: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _filter_duplicate_jobs(self, job_listings, current_url, current_company, current_title):
        """사용자가 이미 분석한 공고를 제외"""
        filtered = []

        for job in job_listings:
            # URL이 정확히 일치하면 제외
            if current_url and job.get('url') == current_url:
                print(f"  ❌ URL 중복 제외: {job['title']}")
                continue

            # 회사명 + 제목이 매우 유사하면 제외
            if current_company and current_title:
                job_company = job.get('company_name', '').lower().strip()
                job_title = job.get('title', '').lower().strip()
                curr_company = current_company.lower().strip()
                curr_title = current_title.lower().strip()

                # 회사명과 제목이 모두 포함되어 있으면 중복으로 간주
                if (curr_company in job_company or job_company in curr_company) and \
                   (curr_title in job_title or job_title in curr_title):
                    print(f"  ❌ 제목 중복 제외: {job['company_name']} - {job['title']}")
                    continue

            filtered.append(job)

        return filtered

    def _simplify_job_position(self, job_position: str) -> str:
        """
        직무명을 검색에 적합한 간단한 키워드로 정제합니다.

        예시:
        - "AI리서치엔지니어-LLM포스트트레이닝" → "AI 엔지니어"
        - "(주)헥토 AI개발" → "AI개발"
        - "백엔드 개발자 (Python/Django)" → "백엔드 개발자"
        - "데이터 분석가 [신입/경력]" → "데이터 분석가"

        Args:
            job_position (str): 원본 직무명

        Returns:
            str: 정제된 검색 키워드
        """
        import re

        # 괄호와 그 내용 제거 (영어 괄호)
        simplified = re.sub(r'\([^)]*\)', '', job_position)
        # 대괄호와 그 내용 제거
        simplified = re.sub(r'\[[^\]]*\]', '', simplified)
        # 중괄호와 그 내용 제거
        simplified = re.sub(r'\{[^}]*\}', '', simplified)

        # 하이픈 이후 제거 (보통 상세 설명)
        if '-' in simplified:
            simplified = simplified.split('-')[0]

        # 슬래시로 구분된 경우 첫 번째 항목만
        if '/' in simplified:
            parts = simplified.split('/')
            # 가장 긴 부분 선택 (보통 메인 직무명)
            simplified = max(parts, key=len)

        # 회사명 패턴 제거
        simplified = re.sub(r'(주\)|㈜|\(주\))', '', simplified)

        # 특수문자 제거하되 공백은 유지
        simplified = re.sub(r'[^\w\s가-힣]', ' ', simplified)

        # 다중 공백을 단일 공백으로
        simplified = ' '.join(simplified.split())

        # 핵심 키워드 추출 시도
        # AI/데이터/개발 관련 키워드가 있으면 우선 사용
        keywords_priority = {
            'AI': ['AI', '인공지능', 'LLM', 'GPT'],
            '머신러닝': ['머신러닝', 'ML', '기계학습'],
            '딥러닝': ['딥러닝', 'DL', '심층학습'],
            '데이터': ['데이터', 'Data'],
            '백엔드': ['백엔드', 'Backend', '서버'],
            '프론트엔드': ['프론트엔드', 'Frontend', '프론트'],
            '풀스택': ['풀스택', 'Full Stack', 'Fullstack'],
            'DevOps': ['DevOps', '데브옵스'],
            '클라우드': ['클라우드', 'Cloud'],
            'QA': ['QA', '테스트', 'Test']
        }

        for main_keyword, variants in keywords_priority.items():
            for variant in variants:
                if variant in simplified:
                    # 해당 키워드와 "엔지니어", "개발자", "분석가" 등이 함께 있는지 확인
                    if any(role in simplified for role in ['엔지니어', '개발자', '분석가', '매니저', 'Engineer', 'Developer', 'Analyst']):
                        # 키워드와 역할을 함께 반환
                        for role in ['엔지니어', '개발자', '분석가', '매니저', 'Engineer', 'Developer', 'Analyst']:
                            if role in simplified:
                                return f"{main_keyword} {role}"
                    # 역할이 없으면 키워드만 반환
                    return main_keyword

        # 우선순위 키워드가 없으면 정제된 텍스트 그대로 반환
        # 단, 너무 길면 앞부분만 (15자 제한)
        if len(simplified) > 15:
            simplified = simplified[:15].strip()

        return simplified.strip() if simplified.strip() else '개발자'

    def _crawl_saramin(self, job_position, limit=15):
        """
        사람인에서 채용공고 크롤링 (정확도순)

        사람인 검색 결과를 크롤링하여 채용공고 정보를 수집합니다.
        회사명, 공고 제목, URL, 스킬, 지역, 조건 등을 파싱합니다.

        Args:
            job_position (str): 검색할 직무 (예: "백엔드 개발자", "Python 개발자")
            limit (int): 최대 수집 공고 수 (기본값: 15)

        Returns:
            list: 채용공고 리스트
        """
        jobs = []
        try:
            # 사람인 검색 URL (정확도순 - 기본값)
            # searchType=search : 통합검색
            # 정확도순이 기본이므로 sort 파라미터 생략
            search_url = f"https://www.saramin.co.kr/zf_user/search?searchType=search&searchword={job_position}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }

            response = requests.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 채용공고 아이템 찾기 (실제 HTML 구조에 맞게 조정 필요)
            job_items = soup.select('.item_recruit')[:limit]

            for item in job_items:
                try:
                    # 회사명
                    company_elem = item.select_one('.corp_name a')
                    company_name = company_elem.get_text(strip=True) if company_elem else "알 수 없음"

                    # 채용 제목
                    title_elem = item.select_one('.job_tit a')
                    title = title_elem.get_text(strip=True) if title_elem else "채용 공고"
                    job_url = "https://www.saramin.co.kr" + title_elem['href'] if title_elem and title_elem.get('href') else ""

                    # 조건 (경력, 학력 등)
                    conditions = item.select('.job_condition span')
                    conditions_text = [c.get_text(strip=True) for c in conditions]

                    # 스킬/기술 스택
                    skills_elem = item.select('.job_sector a')
                    skills = [s.get_text(strip=True) for s in skills_elem]

                    # 디버그: 스킬 추출 결과 확인
                    print(f"  [사람인] {company_name} - 추출된 스킬: {skills if skills else '없음'}")

                    # 지역
                    location_elem = item.select_one('.job_condition span:first-child')
                    location = location_elem.get_text(strip=True) if location_elem else ""

                    jobs.append({
                        "source": "사람인",
                        "company_name": company_name,
                        "title": title,
                        "url": job_url,
                        "skills": skills if skills else [],
                        "location": location,
                        "conditions": conditions_text,
                        "description": f"{title} - {company_name}"
                    })

                except Exception as e:
                    print(f"⚠️  사람인 아이템 파싱 실패: {e}")
                    continue

        except Exception as e:
            print(f"⚠️  사람인 크롤링 실패: {e}")

        return jobs

    def _fetch_job_detail_skills(self, url):
        """개별 공고 페이지 전문에서 기술 키워드 추출"""
        import re
        if not url:
            return []
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=8)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()

            tech_keywords = [
                'Python', 'Java', 'JavaScript', 'TypeScript', 'C\\+\\+', 'C#', 'Go', 'Kotlin',
                'Swift', 'Ruby', 'PHP', 'Rust', 'Scala',
                'Django', 'Flask', 'FastAPI', 'Spring', 'SpringBoot', 'React', 'Vue',
                'Angular', 'Next\\.js', 'Nuxt', 'Express', 'Node\\.js', 'Nest\\.js',
                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'MariaDB',
                'Elasticsearch', 'DynamoDB',
                'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins',
                'Git', 'Linux', 'REST', 'GraphQL', 'gRPC', 'Kafka', 'RabbitMQ',
            ]
            found = []
            for kw in tech_keywords:
                display = kw.replace('\\+\\+', '++').replace('\\.', '.')
                if re.search(r'(?<![a-zA-Z])' + kw + r'(?![a-zA-Z])', text, re.IGNORECASE):
                    found.append(display)
            return found
        except Exception:
            return []

    def _enrich_jobs_with_detail_skills(self, jobs):
        """개별 공고 페이지를 5개씩 병렬 파싱하여 기술 스킬 보완"""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def enrich_one(job):
            detail_skills = self._fetch_job_detail_skills(job.get('url', ''))
            if detail_skills:
                existing_lower = {s.lower() for s in job.get('skills', [])}
                new_skills = [s for s in detail_skills if s.lower() not in existing_lower]
                job['skills'] = job.get('skills', []) + new_skills
            return job

        enriched = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(enrich_one, job): job for job in jobs}
            for future in as_completed(futures):
                try:
                    enriched.append(future.result())
                except Exception:
                    enriched.append(futures[future])
        return enriched


    def _match_jobs_with_skills(self, job_listings, user_skills, skill_levels, readiness_score):
        """
        사용자 스킬과 공고 매칭 (3단계 매칭 시스템)

        크롤링한 채용공고들과 사용자 스킬을 3단계 매칭 시스템으로 비교하여
        적합한 공고를 추천합니다.

        Args:
            job_listings: 크롤링한 채용공고 리스트
            user_skills: 사용자 스킬 배열
            skill_levels: 스킬별 숙련도
            readiness_score: 현재 분석 중인 공고의 준비도 점수

        Returns:
            list: 추천 공고 리스트 (매칭률 순으로 정렬)
        """
        MIN_MATCH_RATE = 0.20  # 최소 20% 이상 매칭되어야 추천 (크롤링 공고는 스킬 정보가 적어 완화)

        # 사용자 스킬 정규화
        user_skills_normalized = [self._normalize_skill(s) for s in user_skills]

        recommendations = []
        # 사용자 스킬 임베딩을 jobs 루프 전에 한 번만 계산
        user_embeddings_precomputed = None

        for job in job_listings:
            job_skills = job.get('skills', [])
            print(f"  🔍 [{job.get('source', '')}] {job['company_name']} - 스킬 개수: {len(job_skills)}")

            # 스킬 정보가 없으면 제목/설명에서 추출 시도
            if not job_skills:
                job_text = f"{job['title']} {job['description']}"
                # 간단한 키워드 추출
                common_skills = ['Python', 'Java', 'JavaScript', 'React', 'Vue', 'Django',
                                'Spring', 'Node.js', 'Docker', 'Kubernetes', 'AWS', 'GCP']
                job_skills = [skill for skill in common_skills if skill.lower() in job_text.lower()]

            if not job_skills:
                # 스킬 정보가 전혀 없으면 건너뛰기
                continue

            # 공고 스킬 정규화
            job_skills_normalized = [self._normalize_skill(s) for s in job_skills]

            # === 3단계 매칭 시스템으로 공고 스킬 매칭 ===
            # JobPlannerAnalyzeView와 동일한 매칭 로직 사용
            matched_skills = []
            matched_user_indices = set()  # 이미 매칭된 사용자 스킬 인덱스 (1:1 매칭)

            for i, job_skill in enumerate(job_skills):
                job_normalized = job_skills_normalized[i]
                best_match = None
                best_score = 0.0
                best_user_idx = -1
                match_type = None

                # 1단계: 정확 일치
                for j, user_skill in enumerate(user_skills):
                    if j in matched_user_indices:
                        continue
                    user_normalized = user_skills_normalized[j]
                    if user_normalized == job_normalized:
                        best_match = user_skill
                        best_score = 1.0
                        best_user_idx = j
                        match_type = "exact"
                        break

                # 2단계: 동의어 매칭
                if not best_match:
                    for j, user_skill in enumerate(user_skills):
                        if j in matched_user_indices:
                            continue
                        # 원본 스킬을 정규화했을 때 같은 값으로 변환되는지 확인
                        user_original_normalized = self._normalize_skill(user_skill)
                        job_original_normalized = self._normalize_skill(job_skill)

                        if user_original_normalized == job_original_normalized and user_skill.lower() != job_skill.lower():
                            best_match = user_skill
                            best_score = 0.95
                            best_user_idx = j
                            match_type = "synonym"
                            break

                # 3단계: 임베딩 유사도
                if not best_match:
                    # 사용자 스킬 임베딩: 처음 한 번만 계산 후 재사용
                    if user_embeddings_precomputed is None:
                        user_embeddings_precomputed = _embed_texts(user_skills_normalized)
                    # 현재 공고 스킬 임베딩
                    job_emb = _embed_texts([job_normalized])

                    for j, user_skill in enumerate(user_skills):
                        if j in matched_user_indices:
                            continue
                        user_emb = user_embeddings_precomputed[j:j+1]
                        similarity = float((user_emb @ job_emb.T)[0][0])

                        # threshold 0.70 (recommend용 - analyze보다 완화)
                        if similarity >= 0.70 and similarity > best_score:
                            best_match = user_skill
                            best_score = similarity
                            best_user_idx = j
                            match_type = "similar"

                # 매칭 성공 시 저장 (70% 이상)
                if best_match and best_score >= 0.70:
                    matched_skills.append({
                        "job_skill": job_skill,
                        "user_skill": best_match,
                        "similarity": round(best_score, 3),
                        "match_type": match_type
                    })
                    matched_user_indices.add(best_user_idx)

            # 매칭률 계산
            matched_count = len(matched_skills)
            match_rate = matched_count / len(job_skills) if job_skills else 0

            # 평균 유사도 계산
            avg_similarity = sum([m['similarity'] for m in matched_skills]) / len(matched_skills) if matched_skills else 0

            # === 추천 조건 판단 ===
            # 현재 분석 중인 공고보다 더 적합한 공고를 추천하기 위한 로직
            #
            # 조건 1: 최소 30% 이상 매칭 (너무 낮으면 부적합)
            # 조건 2: 다음 중 하나를 만족
            #   - 현재 준비도보다 높은 매칭률 (더 적합한 공고)
            #   - 준비도의 90% 이상이면서 95% 미만 (비슷한 수준 + 새 기술 학습 기회)

            # 디버그: 모든 공고의 매칭률 출력
            print(f"  📊 [{job.get('source', '')}] {job['company_name']} - {job['title'][:30]}...")
            print(f"     매칭: {matched_count}/{len(job_skills)} ({match_rate*100:.1f}%), 평균 유사도: {avg_similarity*100:.1f}%")

            if match_rate >= MIN_MATCH_RATE:
                print(f"     ✅ 추천 조건 만족!")
                recommendations.append({
                    "source": job.get('source', ''),
                    "company_name": job['company_name'],
                    "title": job['title'],
                    "url": job['url'],
                    "skills": job_skills,
                    "location": job.get('location', ''),
                    "match_rate": round(match_rate, 3),
                    "avg_similarity": round(avg_similarity, 3),
                    "matched_skills": matched_skills,
                    "matched_count": matched_count,
                    "total_skills": len(job_skills),
                    "reason": self._generate_recommendation_reason(match_rate, readiness_score, matched_count, len(job_skills))
                })
            else:
                # 필터링 이유 출력
                if match_rate < MIN_MATCH_RATE:
                    print(f"     ❌ 필터링: 매칭률 {match_rate*100:.1f}% < 최소 {MIN_MATCH_RATE*100:.0f}%")
                else:
                    print(f"     ❌ 필터링: 현재 공고({readiness_score*100:.1f}%)보다 유의미하게 높지 않음")

        # 매칭률 순으로 정렬 (가장 적합한 공고가 맨 위로)
        recommendations.sort(key=lambda x: x['match_rate'], reverse=True)

        return recommendations

    def _generate_recommendation_reason(self, match_rate, readiness_score, matched_count, total_skills):
        """추천 이유 생성"""
        if match_rate > readiness_score + 0.2:
            return f"현재보다 {int((match_rate - readiness_score) * 100)}% 높은 매칭률로 더 적합한 공고입니다."
        elif match_rate > readiness_score + 0.1:
            return f"보유 스킬과 잘 맞고, {matched_count}/{total_skills}개 스킬이 일치합니다."
        else:
            return f"현재 수준과 비슷하면서 새로운 기술을 배울 수 있는 기회입니다."


@method_decorator(csrf_exempt, name='dispatch')
class JobPlannerCompanyAnalyzeView(APIView):
    """
    기업 분석 API
    - URL 크롤링 또는 텍스트 입력으로 회사 정보 수집
    - LLM으로 종합 분석:
      1. 회사 개요 및 비전
      2. 기술 스택 및 개발 문화
      3. 성장성 및 안정성
      4. 복지 및 근무환경
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            input_type = request.data.get('type')  # 'url' or 'text'
            company_name = request.data.get('company_name', '회사')

            # 회사 정보 수집
            if input_type == 'url':
                company_info = self._fetch_from_url(request.data.get('url'))
            elif input_type == 'text':
                company_info = request.data.get('text', '')
            else:
                return Response({
                    "error": "Invalid input type. Use 'url' or 'text'."
                }, status=status.HTTP_400_BAD_REQUEST)

            # LLM으로 종합 분석
            analysis = self._analyze_company_with_llm(company_name, company_info)

            return Response(analysis, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"❌ 기업분석 에러: {e}")
            print(traceback.format_exc())
            return Response({
                "error": f"기업분석 중 오류 발생: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _fetch_from_url(self, url):
        """URL에서 회사 정보 크롤링"""
        if not CRAWLER_AVAILABLE:
            raise Exception("크롤링 라이브러리가 설치되지 않았습니다.")

        if not url:
            raise Exception("URL이 필요합니다.")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 스크립트와 스타일 제거
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text(separator='\n', strip=True)
        return text

    def _analyze_company_with_llm(self, company_name, company_info):
        """LLM으로 기업 종합 분석"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {
                "error": "OPENAI_API_KEY가 설정되지 않았습니다.",
                "company_name": company_name,
                "overview": "",
                "tech_stack": {},
                "growth": {},
                "welfare": {}
            }

        try:
            client = openai.OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """당신은 IT 기업 분석 전문가입니다.
회사 정보를 바탕으로 다음 4가지 항목을 분석하여 JSON 형식으로 반환하세요:
1. 회사 개요 및 비전
2. 기술 스택 및 개발 문화
3. 성장성 및 안정성
4. 복지 및 근무환경

정보가 부족하면 일반적인 인사이트를 제공하세요."""
                    },
                    {
                        "role": "user",
                        "content": f"""다음 회사 정보를 분석해주세요:

회사명: {company_name}

정보:
{company_info[:3000]}

JSON 형식으로 반환:
{{
  "company_name": "{company_name}",
  "overview": {{
    "description": "회사 소개 (2-3문장)",
    "vision": "비전 및 미션",
    "industry": "산업 분야",
    "founded_year": "설립연도 (알 수 없으면 null)",
    "size": "회사 규모 (예: 50-100명)"
  }},
  "tech_stack": {{
    "languages": ["주요 프로그래밍 언어"],
    "frameworks": ["주요 프레임워크"],
    "tools": ["개발 도구 및 협업 툴"],
    "culture": "개발 문화 설명 (2-3문장)",
    "tech_blog": "기술 블로그 활동 여부 및 평가"
  }},
  "growth": {{
    "funding": "투자 유치 현황",
    "market_position": "시장 위치 및 경쟁력",
    "growth_potential": "성장 가능성 평가 (상/중/하)",
    "stability": "안정성 평가 (상/중/하)"
  }},
  "welfare": {{
    "salary_level": "연봉 수준 (평균 또는 범위)",
    "benefits": ["복지 혜택 리스트"],
    "work_life_balance": "워라밸 평가 및 설명",
    "remote_work": "리모트 근무 가능 여부"
  }},
  "overall_score": {{
    "tech_score": 0.0-1.0,
    "growth_score": 0.0-1.0,
    "welfare_score": 0.0-1.0,
    "total_score": 0.0-1.0
  }},
  "recommendation": "이 회사에 지원하면 좋은 이유 또는 주의사항 (3-4문장)"
}}"""
                    }
                ],
                temperature=0.5
            )

            content = response.choices[0].message.content

            # JSON 추출
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()

            analysis = json.loads(content)
            return analysis

        except Exception as e:
            print(f"⚠️  LLM 기업분석 실패: {e}")
            return {
                "error": f"분석 실패: {str(e)}",
                "company_name": company_name,
                "overview": {"description": "정보 부족", "vision": "", "industry": "", "founded_year": None, "size": ""},
                "tech_stack": {"languages": [], "frameworks": [], "tools": [], "culture": "", "tech_blog": ""},
                "growth": {"funding": "", "market_position": "", "growth_potential": "중", "stability": "중"},
                "welfare": {"salary_level": "", "benefits": [], "work_life_balance": "", "remote_work": ""},
                "overall_score": {"tech_score": 0.5, "growth_score": 0.5, "welfare_score": 0.5, "total_score": 0.5},
                "recommendation": "정보가 부족하여 분석할 수 없습니다."
            }
