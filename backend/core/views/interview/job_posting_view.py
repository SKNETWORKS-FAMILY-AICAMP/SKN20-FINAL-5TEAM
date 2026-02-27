"""
job_posting_view.py — 채용공고 CRUD API
GET  /api/core/interview/job-postings/         → 저장된 채용공고 목록
POST /api/core/interview/job-postings/         → 새 공고 저장 (직접 등록)
DELETE /api/core/interview/job-postings/<id>/  → 공고 삭제
"""
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from core.models import SavedJobPosting, UserProfile


def _get_user(request):
    """세션에서 UserProfile을 가져온다. 없으면 None."""
    from django.contrib.auth.models import User
    # Django 세션에서 auth user ID 가져오기
    auth_user_id = request.session.get('_auth_user_id')
    if not auth_user_id:
        return None
    try:
        # Django User의 email로 UserProfile 조회
        django_user = User.objects.get(pk=auth_user_id)
        return UserProfile.objects.get(email=django_user.email)
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        return None


def _serialize_posting(posting) -> dict:
    return {
        "id": posting.id,
        "company_name": posting.company_name,
        "position": posting.position,
        "job_responsibilities": posting.job_responsibilities,
        "required_qualifications": posting.required_qualifications,
        "preferred_qualifications": posting.preferred_qualifications,
        "required_skills": posting.required_skills,
        "preferred_skills": posting.preferred_skills,
        "experience_range": posting.experience_range,
        "deadline": posting.deadline,
        "source": posting.source,
        "source_url": posting.source_url,
        "created_at": posting.create_date.isoformat() if posting.create_date else None,
    }


@method_decorator(csrf_exempt, name='dispatch')
class InterviewJobPostingView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        """저장된 채용공고 목록 반환"""
        user = _get_user(request)
        if not user:
            return Response({"error": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED)

        postings = SavedJobPosting.objects.filter(user=user).order_by('-create_date')
        data = [_serialize_posting(p) for p in postings]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        """채용공고 직접 저장 (Job Planner 파싱 없이 직접 등록)"""
        user = _get_user(request)
        if not user:
            return Response({"error": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        company_name = data.get('company_name', '')
        position = data.get('position', '')

        if not company_name or not position:
            return Response(
                {"error": "company_name과 position은 필수입니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        posting = SavedJobPosting.objects.create(
            user=user,
            company_name=company_name,
            position=position,
            job_responsibilities=data.get('job_responsibilities', ''),
            required_qualifications=data.get('required_qualifications', ''),
            preferred_qualifications=data.get('preferred_qualifications', ''),
            required_skills=data.get('required_skills', []),
            preferred_skills=data.get('preferred_skills', []),
            experience_range=data.get('experience_range', ''),
            deadline=data.get('deadline'),
            source=data.get('source', 'text'),
            source_url=data.get('source_url', ''),
            raw_text=data.get('raw_text', ''),
            parsed_data=data.get('parsed_data', {}),
        )

        return Response(_serialize_posting(posting), status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class InterviewJobPostingDetailView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def delete(self, request, pk):
        """채용공고 삭제"""
        user = _get_user(request)
        if not user:
            return Response({"error": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            posting = SavedJobPosting.objects.get(pk=pk, user=user)
            posting.delete()
            return Response({"message": "삭제됐습니다."}, status=status.HTTP_200_OK)
        except SavedJobPosting.DoesNotExist:
            return Response({"error": "채용공고를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
