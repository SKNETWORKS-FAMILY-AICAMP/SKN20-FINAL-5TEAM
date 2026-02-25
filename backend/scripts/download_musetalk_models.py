"""
MuseTalk 서비스 구동에 필요한 모델 가중치를 HuggingFace Hub에서 다운로드하는 스크립트.

사용법:
    backend/ 디렉터리에서 실행:
        python scripts/download_musetalk_models.py

다운로드 항목:
    1. MuseTalk 핵심 가중치 + DWpose + face-parse-bisent (TMElyralab/MuseTalk)
    2. VAE 디코더 (stabilityai/sd-vae-ft-mse)

사전 조건:
    pip install huggingface_hub
"""

import os
from huggingface_hub import snapshot_download


def download_models():
    # 모델 저장 루트 디렉터리 (backend/models)
    base_model_dir = "models"
    os.makedirs(base_model_dir, exist_ok=True)

    print("--- [MuseTalk] 모델 가중치 전체 다운로드 시작 ---")

    # ------------------------------------------------------------------ #
    # 1. MuseTalk 핵심 가중치 + DWpose + 유틸 모델
    #
    #    [MuseTalk UNet]  musetalk/*.bin, *.json
    #      핵심 두뇌. 오디오 신호를 분석해서 입 모양을 어떻게 바꿀지 계산합니다.
    #
    #    [DWPose]  dwpose/*.pth, *.onnx
    #      자세 분석. 영상 속 인물의 얼굴 위치와 윤곽선을 정확하게 파악합니다.
    #
    #    [Face-parse-bisent]  face-parse-bisent/*.pth
    #      얼굴 영역 구분. 얼굴 내에서 입술, 피부, 배경 등을 세밀하게 나누어
    #      합성 부위만 골라냅니다.
    #
    #    ※ 전체 저장소 용량이 크므로 필요한 파일만 allow_patterns로 필터링
    # ------------------------------------------------------------------ #
    print("1. MuseTalk 핵심 및 DWpose 다운로드 중...")
    snapshot_download(
        repo_id="TMElyralab/MuseTalk",
        local_dir=base_model_dir,
        allow_patterns=[
            "musetalk/*.json",
            "musetalk/*.bin",
            "dwpose/*.pth",
            "dwpose/*.onnx",
            "face-parse-bisent/*.pth",
            "resnet18.pth",
        ],
    )

    # ------------------------------------------------------------------ #
    # 2. VAE 디코더  (sd-vae-ft-mse)  stabilityai/sd-vae-ft-mse
    #
    #    [VAE (sd-vae-ft-mse)]
    #      화질 복원. 압축된 데이터를 우리가 볼 수 있는 고화질 이미지로
    #      다시 그려냅니다. (kl-f8 오토인코더를 MSE 손실로 파인튜닝한 버전)
    #
    #    - base_model_dir/sd-vae-ft-mse/ 하위에 저장
    # ------------------------------------------------------------------ #
    print("2. VAE (sd-vae-ft-mse) 다운로드 중...")
    vae_dir = os.path.join(base_model_dir, "sd-vae-ft-mse")
    snapshot_download(
        repo_id="stabilityai/sd-vae-ft-mse",
        local_dir=vae_dir,
    )

    print("\n--- ✅ 모든 모델 다운로드 및 배치 완료 ---")
    print(f"위치: {os.path.abspath(base_model_dir)}")


if __name__ == "__main__":
    download_models()
