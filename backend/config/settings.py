"""
Django settings for config project.
수정일: 2026-01-20
수정내용: 프로젝트 기본 설정 및 PostgreSQL 연결 설정, 협업을 위한 앱 분리 구조 준비
"""

import os
from pathlib import Path
import environ

# env 객체 초기화
env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent

# .env 파일이 있으면 읽어옴 (2026-01-26 수정: backend/.env에서 루트/.env로 경로 변경)
environ.Env.read_env(os.path.join(BASE_DIR.parent, '.env'))

SECRET_KEY = env('SECRET_KEY', default='django-insecure-default-key-for-dev')

DEBUG = env('DEBUG', default=True)

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    
    # Local apps (담당자별 앱 분리 가능)
    'core', 
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # CORS 설정
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database 설정 (PostgreSQL)
# [수정일: 2026-01-22] Supabase 및 로컬 환경 동시 지원을 위한 DB 설정 (Antigravity)
import dj_database_url

# [수정일: 2026-01-25] 특수문자 포함 비밀번호 처리를 위해 개별 변수 우선 로직 적용
if env('DB_PASSWORD', default=None):
    DATABASES = {
        'default': {
            'ENGINE': env('DB_ENGINE', default='django.db.backends.postgresql'),
            'NAME': env('DB_NAME', default='postgres'),
            'USER': env('DB_USER', default='postgres'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST'),
            'PORT': env('DB_PORT', default='5432'),
        }
    }
elif os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # 기본 로컬 개발용 (Docker 내부 db 서비스용)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'mygym',
            'USER': 'myuser',
            'PASSWORD': 'mypassword',
            'HOST': 'db',
            'PORT': '5432',
        }
    }

# [Debug] DB 설정 확인 (프로덕션에서는 보안 주의)
print(f"Server is starting with DB Config: HOST={DATABASES['default'].get('HOST')}, USER={DATABASES['default'].get('USER')}, NAME={DATABASES['default'].get('NAME')}")

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ko-kr' # 한국어 설정
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# [수정일: 2026-02-06] 나노바나나 아바타 이미지 저장을 위한 미디어 설정
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# DRF & Swagger 설정
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# [수정일: 2026-01-22] 로그인 유지 문제 해결을 위한 CORS 및 세션 설정 (Antigravity)
# credentials 허용 시 ALL_ORIGINS = True 를 사용할 수 없으므로 화이트리스트 방식으로 변경
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
CORS_ALLOW_CREDENTIALS = True

# [수정일: 2026-01-22] CSRF 신뢰 도메인 설정 유지 및 보완 (Antigravity)
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

# 세션 및 CSRF 쿠키 설정
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True

# AI Service Settings
OPENAI_API_KEY = env('OPENAI_API_KEY', default='')
