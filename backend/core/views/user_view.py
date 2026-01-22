# 수정일: 2026-01-22
# 수정내용: Antigravity - PK 명칭 id 통일에 따른 참조 필드 수정

from rest_framework import viewsets, serializers, permissions
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from core.models import UserProfile, UserDetail
import traceback # [수정일: 2026-01-22] 에러 디버깅을 위한 traceback 추가

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

    def validate(self, data):
        """
        [수정일: 2026-01-21] 회원가입 전체 데이터 검증 (필수값, 비밀번호, 닉네임 등)
        """
        # 1. 닉네임 검증
        if 'user_nickname' in data:
            if len(data['user_nickname']) < 2:
                raise serializers.ValidationError({"user_nickname": "닉네임을 2글자 이상 입력해주세요."})
            if len(data['user_nickname']) > 20:
                raise serializers.ValidationError({"user_nickname": "닉네임은 20글자 이하이어야 합니다."})

        # 2. 비밀번호 검증 (생성 시에만 체크)
        if self.instance is None and 'password' in data:
            password = data['password']
            if len(password) < 8:
                raise serializers.ValidationError({"password": "비밀번호는 8자 이상이어야 합니다."})
            # (추가적인 복잡도 검사는 필요 시 여기에 추가)
            
        return data

    def validate_email(self, value):
        """
        [수정일: 2026-01-21] 이메일 중복 체크 로직 추가
        """
        if UserProfile.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 가입된 이메일입니다.")
        return value



    def create(self, validated_data):
        """
        [수정일: 2026-01-21] 회원가입 로직 재정의 및 auth.User 동기화
        - UserDetail(상세 정보) 데이터 분리 및 저장
        - 비밀번호 암호화(Hashing) 적용
        - Django 인증 시스템(auth.User) 계정 동시 생성 (로그인 연동용)
        - 트랜잭션 처리 추가 (데이터 일관성 보장)
        """
        from django.db import transaction

        # [2026-01-21] create_id, update_id 자동 설정 (회원가입 시 admin)
        validated_data['create_id'] = 'admin'
        validated_data['update_id'] = 'admin'

        # 1. user_detail 데이터 분리
        detail_data = validated_data.pop('user_detail', {})

        raw_password = validated_data.get('password') # 평문 비밀번호 보관 (User 생성용)
        # [수정일: 2026-01-22] id가 없으면 이메일에서 생성 (save 메서드와 동기화)
        id = validated_data.get('id')
        email = validated_data.get('email')
        if not id and email:
            id = email.split('@')[0][:50]
            validated_data['id'] = id

        # 2. 비밀번호 암호화 (UserProfile용)
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])

        # [수정일: 2026-01-21] 트랜잭션으로 모든 DB 작업 묶기 (원자성 보장)
        try:
            with transaction.atomic():
                # 3. Django 기본 인증 유저(auth.User) 생성
                # id(이메일)를 username으로 사용
                if id and raw_password:
                    try:
                        # auth.User 중복 체크 및 생성
                        if User.objects.filter(username=id).exists():
                            raise serializers.ValidationError({"detail": "이미 가입된 계정입니다."})
                        if User.objects.filter(email=email).exists():
                            raise serializers.ValidationError({"detail": "이미 가입된 이메일입니다."})

                        User.objects.create_user(username=id, email=email, password=raw_password)
                    except serializers.ValidationError:
                        raise  # ValidationError는 그대로 전파
                    except Exception as e:
                        # 기타 에러 처리
                        raise serializers.ValidationError({"detail": f"인증 계정 생성 실패: {str(e)}"})

                # 4. UserProfile(기본 정보) 생성
                user = UserProfile.objects.create(**validated_data)

                # 5. UserDetail(상세 정보) 생성 및 기본 프로필과 1:1 연결
                # 1:1 관계인 user 필드에 방금 생성한 user 객체를 할당

                if 'job_role' in detail_data and isinstance(detail_data['job_role'], list):
                    detail_data['job_role'] = ','.join(detail_data['job_role'])

                if 'interests' in detail_data and isinstance(detail_data['interests'], list):
                    detail_data['interests'] = ','.join(detail_data['interests'])

                # [수정일: 2026-01-22] UserDetail 생성 로직 확인
                UserDetail.objects.create(user=user, **detail_data)

                return user

        except serializers.ValidationError:
            raise  # ValidationError는 그대로 전파
        except Exception as e:
            # 예상치 못한 에러 처리
            print(f"!!! Signup Error: {e}") # [수정일: 2026-01-22] 에러 로그 출력
            traceback.print_exc()
            raise serializers.ValidationError({"detail": f"회원가입 처리 중 오류가 발생했습니다: {str(e)}"})

    def update(self, instance, validated_data):
        """
        [수정일: 2026-01-21] 회원 정보 수정 로직
        - user_detail 정보 업데이트 처리
        - 비밀번호 변경 로직 추가
        """
        detail_data = validated_data.pop('user_detail', {})
        
        # [2026-01-21] 비밀번호 변경 처리
        if 'password' in validated_data:
             # 입력된 평문 비밀번호를 해싱하여 저장
             raw_password = validated_data['password']
             validated_data['password'] = make_password(raw_password)
             
             # 연동된 auth.User의 비밀번호도 함께 변경
             # instance.user_id는 이메일 앞부분 등이므로 정확한 매핑 필요.
             # UserProfile.email을 통해 auth.User를 찾아서 변경
             if instance.email:
                 try:
                     auth_user = User.objects.get(email=instance.email)
                     auth_user.set_password(raw_password)
                     auth_user.save()
                 except User.DoesNotExist:
                     pass # auth.User가 없으면 무시 (하지만 데이터 정합성 문제 주의)
        
        # 기본 정보 업데이트
        super().update(instance, validated_data)
        
        # 상세 정보 업데이트
        if hasattr(instance, 'user_detail'):
            detail = instance.user_detail
            
            # 리스트 -> 문자열 변환
            if 'job_role' in detail_data and isinstance(detail_data['job_role'], list):
                detail.job_role = ','.join(detail_data['job_role'])
            elif 'job_role' in detail_data: # 수정 시 빈 값이면
                detail.job_role = detail_data['job_role'] # 문자열이거나 null일 것임
                
            if 'interests' in detail_data and isinstance(detail_data['interests'], list):
                detail.interests = ','.join(detail_data['interests'])
            elif 'interests' in detail_data:
                detail.interests = detail_data['interests']
                
            if 'is_developer' in detail_data:
                detail.is_developer = detail_data['is_developer']
                
            detail.save()
            
        return instance

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    팀원 A 담당: 회원가입, 프로필 조회 API
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def initialize_request(self, request, *args, **kwargs):
        """
        [수정일: 2026-01-21] 회원가입(POST) 시 CSRF 검사 방지를 위해 인증(SessionAuthentication) 제외
        """
        if request.method == 'POST':
            # POST 요청일 경우에만 인증 클래스를 비워서 CSRF 체크를 스킵
            self.authentication_classes = []
        return super().initialize_request(request, *args, **kwargs)

    def get_permissions(self):
        # 회원가입은 누구나, 수정/삭제는 본인만
        if self.action in ['update', 'partial_update', 'destroy']:
            # 커스텀 권한 체크 필요 (여기서는 간단히 로그인 여부만, 실제 본인 체크는 IsOwner 필요함)
            # 그러나 일단 로그인한 유저만 접근하도록 설정
            return [permissions.IsAuthenticated()]
        return super().get_permissions()