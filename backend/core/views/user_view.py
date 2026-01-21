# 수정일: 2026-01-20
# 수정내용: 팀원 A (User 담당) - 회원 관련 뷰 정의

from rest_framework import viewsets, serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from core.models import UserProfile, UserDetail

# 1. UserDetail Serializer
class UserDetailSerializer(serializers.ModelSerializer):
    job_role = serializers.ListField(
        child=serializers.CharField(),
        required=False, 
        allow_empty=True
    )
    # [수정일: 2026-01-21] 관심 분야(Interests) 리스트 처리 추가
    interests = serializers.ListField(
        child=serializers.CharField(),
        required=False, 
        allow_empty=True
    )

    class Meta:
        model = UserDetail
        fields = ['is_developer', 'job_role', 'interests']

    def to_representation(self, instance):
        """응답 시 DB 문자열 -> 리스트 변환"""
        ret = super().to_representation(instance)
        # job_role이 문자열이면 리스트로 변환
        if isinstance(instance.job_role, str) and instance.job_role:
            ret['job_role'] = instance.job_role.split(',')
        elif not instance.job_role:
             ret['job_role'] = []
             
        # interests 문자열 -> 리스트 변환
        if isinstance(instance.interests, str) and instance.interests:
            ret['interests'] = instance.interests.split(',')
        else:
            ret['interests'] = []
            
        return ret


# 2. UserProfile Serializer (Nested)
class UserProfileSerializer(serializers.ModelSerializer):
    user_detail = UserDetailSerializer(required=False)  # 중첩 Serializer

    class Meta:
        model = UserProfile
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}  # 비밀번호는 응답에서 제외
        }



    def create(self, validated_data):
        """
        [수정일: 2026-01-21] 회원가입 로직 재정의 및 auth.User 동기화
        - UserDetail(상세 정보) 데이터 분리 및 저장
        - 비밀번호 암호화(Hashing) 적용
        - Django 인증 시스템(auth.User) 계정 동시 생성 (로그인 연동용)
        """
        # 1. user_detail 데이터 분리
        detail_data = validated_data.pop('user_detail', {})
        
        raw_password = validated_data.get('password') # 평문 비밀번호 보관 (User 생성용)

        # 2. 비밀번호 암호화 (UserProfile용)
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        
        # [2026-01-21] Django 기본 인증 유저(auth.User) 생성
        # user_id(이메일)를 username으로 사용
        user_id = validated_data.get('user_id')
        email = validated_data.get('email')
        
        if user_id and raw_password:
            # 이미 존재하는지 확인 (에러 처리 필요하지만 여기선 생략 또는 try-except)
            if not User.objects.filter(username=user_id).exists():
                User.objects.create_user(username=user_id, email=email, password=raw_password)

        # 3. UserProfile(기본 정보) 생성
        user = UserProfile.objects.create(**validated_data)
        
        # 4. UserDetail(상세 정보) 생성 및 기본 프로필과 1:1 연결
        # 1:1 관계인 user 필드에 방금 생성한 user 객체를 할당
        
        if 'job_role' in detail_data and isinstance(detail_data['job_role'], list):
            detail_data['job_role'] = ','.join(detail_data['job_role'])

        # interests가 리스트라면 콤마 문자열로 변환
        if 'interests' in detail_data and isinstance(detail_data['interests'], list):
            detail_data['interests'] = ','.join(detail_data['interests'])

        UserDetail.objects.create(user_id=user, **detail_data)
        
        return user

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    팀원 A 담당: 회원가입, 프로필 조회 API
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

