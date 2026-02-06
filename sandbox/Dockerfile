# 수정일: 2026-02-06
# 수정내용: PyTorch 디버깅 문제 실행을 위한 샌드박스 이미지

FROM python:3.10-slim

# 시스템 패키지 설치 (최소화)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
# CPU 버전 PyTorch (가벼움), numpy, scikit-learn
RUN pip install --no-cache-dir \
    torch==2.1.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir \
    numpy==1.24.3 \
    scikit-learn==1.3.2 \
    transformers==4.35.0

# 보안: 루트가 아닌 사용자로 실행
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
