@echo off
REM 수정일: 2026-02-06
REM 수정내용: PyTorch 샌드박스 이미지 빌드 스크립트 (Windows)

echo Building PyTorch sandbox image...
docker build -t pytorch-sandbox:latest .

if %ERRORLEVEL% EQU 0 (
    echo Build successful!
    echo Image: pytorch-sandbox:latest
    docker images pytorch-sandbox
) else (
    echo Build failed!
    exit /b 1
)
