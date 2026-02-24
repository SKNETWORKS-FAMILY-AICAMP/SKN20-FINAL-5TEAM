"""
STT 서비스 — VAD + Transcriber 통합 파이프라인
음성 파일을 받아 발화 감지 후 텍스트로 변환한다.
"""
from .vad import is_speech_present
from .transcriber import transcribe


def process_audio(audio_bytes: bytes) -> dict:
    """
    오디오 바이트 → 텍스트 변환 파이프라인

    1. VAD로 발화 존재 여부 확인
    2. 발화 있으면 faster-whisper로 텍스트 변환

    Returns:
        {
            "transcript": "변환된 텍스트",
            "confidence": 0.95,
            "language": "ko",
            "has_speech": True
        }
    """
    # Step 1: 발화 존재 확인
    has_speech = is_speech_present(audio_bytes)

    if not has_speech:
        return {
            "transcript": "",
            "confidence": 0.0,
            "language": "ko",
            "has_speech": False,
        }

    # Step 2: 텍스트 변환
    result = transcribe(audio_bytes)
    result["has_speech"] = True

    return result
