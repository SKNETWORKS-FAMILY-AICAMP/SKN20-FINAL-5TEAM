"""
STT (Speech-to-Text) — faster-whisper large-v3 기반
환경변수 STT_RUNPOD_URL이 설정되면 RunPod GPU 서버로 요청 전달.
미설정 시 로컬 모델(CPU) 사용.
"""
import io
import math
import os

import requests as _requests

# RunPod STT 서버 URL (예: http://213.192.2.84:40XXX)
_RUNPOD_URL = os.environ.get("STT_RUNPOD_URL", "").rstrip("/")

try:
    from faster_whisper import WhisperModel
    _WHISPER_AVAILABLE = True
except ImportError:
    _WHISPER_AVAILABLE = False

_model_instance = None


def _get_local_model() -> 'WhisperModel':
    """싱글톤 — 처음 호출 시 로컬 모델 로드"""
    global _model_instance
    if _model_instance is None:
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
        except ImportError:
            device = "cpu"
            compute_type = "int8"

        model_size = "medium"  # 로컬 CPU용 (large-v3는 너무 느림)
        print(f"[STT] faster-whisper {model_size} 로딩 중... (device={device}, compute={compute_type})")
        _model_instance = WhisperModel(model_size, device=device, compute_type=compute_type)
        print("[STT] 로컬 모델 로드 완료")

    return _model_instance


def _transcribe_remote(audio_bytes: bytes) -> dict:
    """RunPod GPU 서버로 요청 전달"""
    try:
        files = {"audio": ("recording.webm", io.BytesIO(audio_bytes), "audio/webm")}
        resp = _requests.post(
            f"{_RUNPOD_URL}/transcribe",
            files=files,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        data.setdefault("error", None)
        return data
    except Exception as e:
        print(f"[STT] RunPod 호출 실패: {e}")
        return {
            "transcript": "",
            "confidence": 0.0,
            "language": "ko",
            "error": str(e),
        }


def _transcribe_local(audio_bytes: bytes) -> dict:
    """로컬 faster-whisper 모델로 변환"""
    if not _WHISPER_AVAILABLE:
        return {
            "transcript": "",
            "confidence": 0.0,
            "language": "ko",
            "error": "faster-whisper가 설치되지 않았습니다. pip install faster-whisper",
        }

    try:
        model = _get_local_model()
        audio_io = io.BytesIO(audio_bytes)

        segments, info = model.transcribe(
            audio_io,
            language="ko",
            beam_size=5,
            best_of=5,
            temperature=0.0,
            condition_on_previous_text=False,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )

        texts = []
        logprobs = []
        for segment in segments:
            text = segment.text.strip()
            if text:
                texts.append(text)
                logprobs.append(segment.avg_logprob)

        transcript = " ".join(texts).strip()

        if logprobs:
            avg_logprob = sum(logprobs) / len(logprobs)
            confidence = round(min(1.0, max(0.0, math.exp(avg_logprob))), 3)
        else:
            confidence = 0.0

        return {
            "transcript": transcript,
            "confidence": confidence,
            "language": info.language,
            "error": None,
        }

    except Exception as e:
        print(f"[STT] 로컬 변환 오류: {e}")
        return {
            "transcript": "",
            "confidence": 0.0,
            "language": "ko",
            "error": str(e),
        }


def transcribe(audio_bytes: bytes) -> dict:
    """
    음성 바이트 → 한국어 텍스트 변환
    STT_RUNPOD_URL 환경변수 설정 시 RunPod GPU 사용, 미설정 시 로컬 모델 사용.
    """
    if _RUNPOD_URL:
        print(f"[STT] RunPod GPU 사용: {_RUNPOD_URL}")
        return _transcribe_remote(audio_bytes)
    else:
        print("[STT] 로컬 모델 사용 (STT_RUNPOD_URL 미설정)")
        return _transcribe_local(audio_bytes)
