"""
RunPod STT 서버 — faster-whisper large-v3 (GPU)
RunPod 터미널에서 실행:
    pip install faster-whisper fastapi uvicorn python-multipart
    python runpod_server.py
"""
import io
import math

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel
import uvicorn

app = FastAPI()
_model = None


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        print("[STT] faster-whisper large-v3 로딩 중 (CUDA float16)...")
        _model = WhisperModel("large-v3", device="cuda", compute_type="float16")
        print("[STT] 모델 로드 완료!")
    return _model


@app.on_event("startup")
async def startup():
    get_model()  # 서버 시작 시 미리 로드


@app.get("/health")
def health():
    return {"status": "ok", "model": "large-v3"}


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    try:
        audio_bytes = await audio.read()
        model = get_model()
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
            "has_speech": bool(transcript),
        }

    except Exception as e:
        print(f"[STT] 오류: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
