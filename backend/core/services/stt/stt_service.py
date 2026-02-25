"""
STT 서비스 — VAD + Transcriber 통합 파이프라인
음성 파일을 받아 발화 감지 후 텍스트로 변환한다.
"""
import os
from .vad import is_speech_present
from .transcriber import transcribe, _RUNPOD_URL


def process_audio(audio_bytes: bytes) -> dict:
    """
    오디오 바이트 → 텍스트 변환 파이프라인

    RunPod URL 설정 시: VAD 스킵 → RunPod로 직접 전송 (RunPod 서버 내부에서 VAD 처리)
    미설정 시: 로컬 VAD → 로컬 faster-whisper

    Returns:
        {
            "transcript": "변환된 텍스트",
            "confidence": 0.95,
            "language": "ko",
            "has_speech": True
        }
    """
    if _RUNPOD_URL:
        # RunPod 서버가 내부적으로 vad_filter=True로 VAD 처리
        result = transcribe(audio_bytes)
        result["has_speech"] = bool(result.get("transcript"))
        return result

    # 로컬 모드: VAD 먼저 실행
    has_speech = is_speech_present(audio_bytes)
    if not has_speech:
        return {
            "transcript": "",
            "confidence": 0.0,
            "language": "ko",
            "has_speech": False,
        }

    result = transcribe(audio_bytes)
    result["has_speech"] = True
    return result
