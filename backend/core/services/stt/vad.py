"""
VAD (Voice Activity Detection) — silero-vad 기반
음성 파일에서 실제 발화 구간이 존재하는지 감지한다.
"""
import io

try:
    import torch
    import torchaudio
    from silero_vad import load_silero_vad, get_speech_timestamps
    _VAD_AVAILABLE = True
except ImportError:
    _VAD_AVAILABLE = False

_vad_model = None


def _get_vad_model():
    global _vad_model
    if _vad_model is None:
        _vad_model = load_silero_vad()
    return _vad_model


def is_speech_present(audio_bytes: bytes) -> bool:
    """
    오디오 바이트에서 발화가 존재하는지 확인한다.

    Returns:
        True  — 발화 감지됨
        False — 침묵 또는 노이즈만 존재
    """
    if not _VAD_AVAILABLE:
        # VAD 미설치 시 항상 발화 있다고 처리 (Whisper에 위임)
        return True

    try:
        model = _get_vad_model()

        audio_io = io.BytesIO(audio_bytes)
        waveform, sr = torchaudio.load(audio_io)

        # 모노 변환
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)

        # 16kHz 리샘플링 (silero-vad 요구사항)
        if sr != 16000:
            resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=16000)
            waveform = resampler(waveform)

        waveform = waveform.squeeze()

        speech_timestamps = get_speech_timestamps(
            waveform,
            model,
            threshold=0.5,
            sampling_rate=16000,
            min_speech_duration_ms=250,
            min_silence_duration_ms=100,
        )

        return len(speech_timestamps) > 0

    except Exception as e:
        print(f"[VAD] 오류 발생, 발화 있다고 처리: {e}")
        return True  # 오류 시 Whisper에 위임
