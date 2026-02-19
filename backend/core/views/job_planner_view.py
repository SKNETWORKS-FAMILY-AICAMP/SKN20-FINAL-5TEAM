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

# Sentence Transformers (스킬 매칭용)
try:
    from sentence_transformers import SentenceTransformer
    import torch
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False


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
        """URL 크롤링으로 채용공고 파싱"""
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
            # 웹페이지 가져오기
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 텍스트 추출
            # 스크립트와 스타일 제거
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text(separator='\n', strip=True)

            # OpenAI로 구조화된 정보 추출
            parsed_data = self._extract_job_info_with_llm(text, source='url')

            return Response(parsed_data, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response({
                "error": f"URL 접근 실패: {str(e)}"
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
                                "text": """당신은 채용공고 이미지 분석 전문가입니다.
이미지에서 채용공고 정보를 정확하게 추출하여 JSON 형식으로 반환하세요.

다음 정보를 추출하세요:
1. 회사명과 포지션
2. 주요 업무 (담당할 업무, 하게 될 일)
3. 필수 요건 (자격 요건, 필수 조건)
4. 우대 조건 (우대 사항, 플러스 요소)
5. 기술 스택 (각 항목에서 언급된 프로그래밍 언어, 프레임워크, 도구)

JSON 형식:
{
  "company_name": "회사명",
  "position": "포지션",

  "job_responsibilities": "주요 업무 내용 (원문 그대로, 3-5개 항목)",
  "required_qualifications": "필수 요건 (원문 그대로, 자격 요건)",
  "preferred_qualifications": "우대 조건 (원문 그대로, 플러스 요소)",

  "required_skills": ["필수 스킬 배열 - 기술 스택만 추출"],
  "preferred_skills": ["우대 스킬 배열 - 기술 스택만 추출"],

  "experience_range": "경력 요구사항 (예: 신입, 2-4년, 5년 이상)",
  "deadline": "마감일 (YYYY-MM-DD 또는 null)"
}

중요 사항:
- job_responsibilities: "담당 업무", "주요 업무", "하게 될 일" 섹션의 내용을 원문 그대로 추출
- required_qualifications: "필수 자격 요건", "지원 자격", "필수 요건" 섹션의 내용을 원문 그대로 추출
- preferred_qualifications: "우대 사항", "우대 조건", "가산점" 섹션의 내용을 원문 그대로 추출
- required_skills: 필수 요건에서 언급된 기술만 배열로 추출 (예: Python, Java, React, Docker, AWS)
- preferred_skills: 우대 조건에서 언급된 기술만 배열로 추출
- 각 기술은 정확한 이름으로 추출 (예: "파이썬" → "Python", "리액트" → "React")
- 기술이 아닌 것은 제외 (예: "팀워크", "성실성", "커뮤니케이션" 등)

이미지의 모든 텍스트를 주의 깊게 읽고 정확하게 추출하세요."""
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
                max_tokens=2000,
                temperature=0.3
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
        return Response(parsed_data, status=status.HTTP_200_OK)

    def _extract_job_info_with_llm(self, text, source='text'):
        """LLM으로 채용공고 정보 추출"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            # Fallback: 기본 파싱
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
                        "content": """당신은 채용공고 분석 전문가입니다.
채용공고에서 다음 정보를 추출하세요:
1. 주요 업무 (담당 업무, 하게 될 일)
2. 필수 요건 (자격 요건, 필수 조건)
3. 우대 조건 (우대 사항, 플러스 요소)

각 항목은 원문 그대로 유지하되, 기술 스택은 별도 배열로 추출하세요.
정보가 없으면 빈 문자열이나 빈 배열을 사용하세요."""
                    },
                    {
                        "role": "user",
                        "content": f"""다음 채용공고에서 정보를 추출하세요:

{text}

JSON 형식:
{{
  "company_name": "회사명",
  "position": "포지션",

  "job_responsibilities": "주요 업무 내용 (원문 그대로, 3-5개 항목)",
  "required_qualifications": "필수 요건 (원문 그대로, 자격 요건)",
  "preferred_qualifications": "우대 조건 (원문 그대로, 플러스 요소)",

  "required_skills": ["필수 스킬 배열 - 기술 스택만 추출"],
  "preferred_skills": ["우대 스킬 배열 - 기술 스택만 추출"],

  "experience_range": "경력 요구사항 (예: 신입, 2-4년, 5년 이상)",
  "deadline": "마감일 (YYYY-MM-DD 또는 null)"
}}

주의사항:
- job_responsibilities: 담당 업무, 하게 될 일 등을 원문 그대로 작성
- required_qualifications: 필수 자격 요건, 지원 자격을 원문 그대로 작성
- preferred_qualifications: 우대 사항, 가산점 항목을 원문 그대로 작성
- required_skills/preferred_skills: 위 내용에서 기술 스택만 배열로 추출 (예: Python, Django, React)"""
                    }
                ],
                temperature=0.3
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
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    # 한영 스킬 동의어 사전
    SKILL_SYNONYMS = {
        # 프로그래밍 언어
        '파이썬': 'python', 'python': 'python',
        '자바': 'java', 'java': 'java',
        '자바스크립트': 'javascript', 'javascript': 'javascript', 'js': 'javascript',
        '타입스크립트': 'typescript', 'typescript': 'typescript', 'ts': 'typescript',
        'C++': 'cpp', 'c++': 'cpp', 'cpp': 'cpp',
        'C#': 'csharp', 'c#': 'csharp', 'csharp': 'csharp', '씨샵': 'csharp',
        '고': 'go', 'go': 'go', 'golang': 'go',
        '코틀린': 'kotlin', 'kotlin': 'kotlin',
        '스위프트': 'swift', 'swift': 'swift',
        'R': 'r', 'r': 'r',
        '루비': 'ruby', 'ruby': 'ruby',
        'PHP': 'php', 'php': 'php',

        # 프레임워크/라이브러리
        '장고': 'django', 'django': 'django',
        '플라스크': 'flask', 'flask': 'flask',
        '스프링': 'spring', 'spring': 'spring', '스프링부트': 'springboot', 'springboot': 'springboot',
        '리액트': 'react', 'react': 'react', 'reactjs': 'react',
        '뷰': 'vue', 'vue': 'vue', 'vuejs': 'vue',
        '앵귤러': 'angular', 'angular': 'angular',
        '노드': 'node', 'node': 'node', 'nodejs': 'node', 'node.js': 'node',
        '익스프레스': 'express', 'express': 'express', 'expressjs': 'express',
        '넥스트': 'next', 'next': 'next', 'nextjs': 'next', 'next.js': 'next',
        '넥스트제이에스': 'next',
        '넥스트js': 'next',

        # 데이터베이스
        'MySQL': 'mysql', 'mysql': 'mysql', '마이에스큐엘': 'mysql',
        'PostgreSQL': 'postgresql', 'postgresql': 'postgresql', '포스트그레': 'postgresql',
        'MongoDB': 'mongodb', 'mongodb': 'mongodb', '몽고디비': 'mongodb',
        'Redis': 'redis', 'redis': 'redis', '레디스': 'redis',
        'Oracle': 'oracle', 'oracle': 'oracle', '오라클': 'oracle',

        # 클라우드/인프라
        'AWS': 'aws', 'aws': 'aws',
        'Azure': 'azure', 'azure': 'azure', '애저': 'azure',
        'GCP': 'gcp', 'gcp': 'gcp', '구글클라우드': 'gcp',
        '도커': 'docker', 'docker': 'docker',
        '쿠버네티스': 'kubernetes', 'kubernetes': 'kubernetes', 'k8s': 'kubernetes',

        # AI/ML
        '텐서플로': 'tensorflow', 'tensorflow': 'tensorflow',
        '파이토치': 'pytorch', 'pytorch': 'pytorch',
        '케라스': 'keras', 'keras': 'keras',
        '사이킷런': 'sklearn', 'sklearn': 'sklearn', 'scikit-learn': 'sklearn',

        # 도구
        '깃': 'git', 'git': 'git',
        '깃허브': 'github', 'github': 'github',
        '지라': 'jira', 'jira': 'jira',
    }

    def _normalize_skill(self, skill):
        """스킬명을 정규화 (한글->영어, 소문자 변환)"""
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
            '깃', '깃허브', '지라'
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
        if not EMBEDDING_AVAILABLE:
            return Response({
                "error": "Sentence Transformers가 설치되지 않았습니다."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

            # 스킬 매칭 엔진
            model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
            threshold = 0.50  # 0.65 → 0.50으로 낮춤

            # 필수 스킬 매칭
            user_emb = model.encode(user_skills_normalized, normalize_embeddings=True)
            req_emb = model.encode(required_skills_normalized, normalize_embeddings=True)
            sim_matrix = user_emb @ req_emb.T

            matched_skills = []
            missing_skills = []

            for i, req in enumerate(required_skills):
                best_idx = sim_matrix[:, i].argmax()
                best_score = float(sim_matrix[best_idx, i])

                if best_score >= threshold:
                    matched_skills.append({
                        "required": req,
                        "user_skill": user_skills[best_idx],
                        "similarity": round(best_score, 3)
                    })
                else:
                    missing_skills.append({
                        "required": req,
                        "closest_match": user_skills[best_idx],
                        "similarity": round(best_score, 3)
                    })

            # 점수 계산
            match_rate = len(matched_skills) / len(required_skills) if required_skills else 0

            # 경력 적합도
            exp_fit = self._calculate_exp_fit(experience_years, experience_range)

            # 숙련도 가중치 (스킬 레벨이 있으면 반영)
            proficiency_score = 0.0
            if skill_levels and matched_skills:
                matched_skill_names = [m["required"] for m in matched_skills]
                level_sum = sum(skill_levels.get(user_skills[user_skills.index(m["user_skill"])], 3)
                               for m in matched_skills if m["user_skill"] in user_skills)
                proficiency_score = round(level_sum / len(matched_skills) / 5.0, 3) if matched_skills else 0.0

            # 준비도 점수 (숙련도 반영)
            if proficiency_score > 0:
                readiness = round(match_rate * 0.5 + exp_fit * 0.2 + proficiency_score * 0.3, 3)
            else:
                readiness = round(match_rate * 0.7 + exp_fit * 0.3, 3)

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
        """경력 적합도 계산"""
        import re
        nums = re.findall(r'\d+', req_range)
        if not nums:
            return 0.7

        lo = int(nums[0])
        hi = int(nums[-1]) if len(nums) > 1 else lo + 2

        if lo <= years <= hi:
            return 1.0
        elif years < lo:
            return max(0.0, years / lo)
        else:
            return max(0.7, 1.0 - (years - hi) * 0.05)

    def _generate_insights(self, name, current_role, education, certifications,
                          career_goals, available_prep_days,
                          matched_skills, missing_skills, readiness, skill_gap):
        """프로필 기반 인사이트 생성"""
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
    - 부족한 스킬에 대한 맞춤형 질문 생성
    - 사용자의 현재 수준과 학습 계획 파악
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
                        "content": """당신은 커리어 코칭 전문가입니다.
부족한 스킬에 대해 구체적이고 실용적인 질문을 생성하세요.
질문은 사용자의 현재 수준, 학습 계획, 준비 전략을 파악하기 위한 것입니다."""
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
            report = self._generate_report_with_llm(
                job_data, analysis_result, company_analysis, agent_answers
            )

            return Response(report, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"❌ 보고서 생성 에러: {e}")
            print(traceback.format_exc())
            return Response({
                "error": f"보고서 생성 중 오류 발생: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _generate_report_with_llm(self, job_data, analysis_result, company_analysis, agent_answers):
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
- 부족한 스킬: {len(analysis_result.get('missing_skills', []))}개

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
   - 단기 (1-2주): 즉시 할 일
   - 중기 (1개월): 스킬 보완
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
    "short_term": ["1-2주 내 할 일1", "할 일2", ...],
    "mid_term": ["1개월 내 할 일1", "할 일2", ...],
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
    - 매칭률이 낮을 때 (readiness_score < 0.6) 추천 공고 제공
    - 사람인, 잡코리아 실제 크롤링
    - 사용자 스킬 기반 매칭
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    # JobPlannerAnalyzeView와 동일한 스킬 동의어 사전
    SKILL_SYNONYMS = JobPlannerAnalyzeView.SKILL_SYNONYMS

    def _normalize_skill(self, skill):
        """스킬명을 정규화 (한글->영어, 소문자 변환)"""
        skill_lower = skill.lower().strip()
        return self.SKILL_SYNONYMS.get(skill_lower, skill_lower)

    def post(self, request):
        try:
            if not CRAWLER_AVAILABLE or not EMBEDDING_AVAILABLE:
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
            if current_job_url:
                print(f"🚫 제외할 공고: {current_job_company} - {current_job_title}")

            # 1. 사람인과 잡코리아에서 공고 크롤링 (정확도순, 각 최대 15개)
            job_listings = []

            # 사람인 크롤링
            saramin_jobs = self._crawl_saramin(job_position)
            job_listings.extend(saramin_jobs)
            print(f"✅ 사람인: {len(saramin_jobs)}개 공고")

            # 잡코리아 크롤링
            jobkorea_jobs = self._crawl_jobkorea(job_position)
            job_listings.extend(jobkorea_jobs)
            print(f"✅ 잡코리아: {len(jobkorea_jobs)}개 공고")

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

            # 2. 스킬 매칭으로 추천 공고 선정
            recommendations = self._match_jobs_with_skills(
                filtered_listings, user_skills, skill_levels, readiness_score
            )

            print(f"✅ 최종 추천: {len(recommendations)}개")

            return Response({
                "recommendations": recommendations[:10],  # 최대 10개
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

    def _crawl_saramin(self, job_position):
        """사람인에서 채용공고 크롤링 (정확도순)"""
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
            job_items = soup.select('.item_recruit')[:15]  # 최대 15개

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

    def _crawl_jobkorea(self, job_position):
        """잡코리아에서 채용공고 크롤링 (정확도순)"""
        jobs = []
        try:
            # 잡코리아 검색 URL (정확도순 - 기본값)
            search_url = f"https://www.jobkorea.co.kr/Search/?stext={job_position}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }

            response = requests.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 채용공고 아이템 찾기
            job_items = soup.select('.list-post article')[:15]  # 최대 15개

            for item in job_items:
                try:
                    # 회사명
                    company_elem = item.select_one('.name')
                    company_name = company_elem.get_text(strip=True) if company_elem else "알 수 없음"

                    # 채용 제목
                    title_elem = item.select_one('.title a')
                    title = title_elem.get_text(strip=True) if title_elem else "채용 공고"
                    job_url = title_elem['href'] if title_elem and title_elem.get('href') else ""
                    if job_url and not job_url.startswith('http'):
                        job_url = "https://www.jobkorea.co.kr" + job_url

                    # 조건
                    conditions_elem = item.select('.option li')
                    conditions = [c.get_text(strip=True) for c in conditions_elem]

                    # 기술 스택 (있으면)
                    skills_elem = item.select('.etc .tag')
                    skills = [s.get_text(strip=True) for s in skills_elem]

                    # 지역
                    location = conditions[0] if conditions else ""

                    jobs.append({
                        "source": "잡코리아",
                        "company_name": company_name,
                        "title": title,
                        "url": job_url,
                        "skills": skills if skills else [],
                        "location": location,
                        "conditions": conditions,
                        "description": f"{title} - {company_name}"
                    })

                except Exception as e:
                    print(f"⚠️  잡코리아 아이템 파싱 실패: {e}")
                    continue

        except Exception as e:
            print(f"⚠️  잡코리아 크롤링 실패: {e}")

        return jobs

    def _match_jobs_with_skills(self, job_listings, user_skills, skill_levels, readiness_score):
        """사용자 스킬과 공고 매칭"""
        model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        threshold = 0.50  # 0.55 → 0.50으로 낮춤 (분석과 동일)

        # 사용자 스킬 정규화
        user_skills_normalized = [self._normalize_skill(s) for s in user_skills]

        recommendations = []
        user_emb = model.encode(user_skills_normalized, normalize_embeddings=True)

        for job in job_listings:
            job_skills = job.get('skills', [])

            # 스킬 정보가 없으면 제목/설명에서 추출 시도
            if not job_skills:
                job_text = f"{job['title']} {job['description']}"
                # 간단한 키워드 추출 (실제로는 LLM 사용 가능)
                common_skills = ['Python', 'Java', 'JavaScript', 'React', 'Vue', 'Django',
                                'Spring', 'Node.js', 'Docker', 'Kubernetes', 'AWS', 'GCP']
                job_skills = [skill for skill in common_skills if skill.lower() in job_text.lower()]

            if not job_skills:
                # 스킬 정보가 전혀 없으면 건너뛰기
                continue

            # 공고 스킬 정규화
            job_skills_normalized = [self._normalize_skill(s) for s in job_skills]

            # 스킬 매칭
            job_emb = model.encode(job_skills_normalized, normalize_embeddings=True)
            sim_matrix = user_emb @ job_emb.T

            # 평균 유사도 계산
            avg_similarity = float(sim_matrix.max(axis=0).mean())

            # 매칭된 스킬 찾기
            matched_count = 0
            matched_skills = []
            for i, job_skill in enumerate(job_skills):
                best_idx = sim_matrix[:, i].argmax()
                best_score = float(sim_matrix[best_idx, i])
                if best_score >= threshold:
                    matched_count += 1
                    matched_skills.append({
                        "job_skill": job_skill,
                        "user_skill": user_skills[best_idx],
                        "similarity": round(best_score, 3)
                    })

            # 매칭률 계산
            match_rate = matched_count / len(job_skills) if job_skills else 0

            # 현재 준비도보다 높은 매칭률을 가진 공고만 추천
            # 또는 매칭률이 비슷하지만 배울 만한 새로운 스킬이 있는 경우
            if match_rate > readiness_score or (match_rate >= readiness_score * 0.9 and match_rate < 0.95):
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

        # 매칭률 순으로 정렬
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
