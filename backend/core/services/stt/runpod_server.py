import io, uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel

app = FastAPI()
_model = None

def get_model():
    global _model
    if _model is None:
        print("[STT] Loading Large-V3 model on High-RAM Server...")
        # 125GB RAM이 확보되었으므로 최상위 품질의 large-v3 모델을 사용합니다.
        # RTX 3090/4090 환경에 최적화된 float16 연산을 사용합니다.
        _model = WhisperModel("large-v3", device="cuda", compute_type="float16")
        print("[STT] Ready! Large-V3 loaded.")
    return _model

@app.on_event("startup")
async def startup():
    get_model()

@app.get("/health")
def health():
    return {"status": "ok", "model": "large-v3"}

@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    try:
        audio_bytes = await audio.read()
        model = get_model()
        
        # 최상위 품질을 위해 beam_size=5 유지, 한국어 지정
        segments, info = model.transcribe(
            io.BytesIO(audio_bytes), 
            language="ko", 
            beam_size=5,
            word_timestamps=False # 필요한 경우 True로 변경 가능
        )
        
        texts = [s.text.strip() for s in segments if s.text.strip()]
        transcript = " ".join(texts).strip()
        
        return {
            "transcript": transcript, 
            "language": info.language, 
            "has_speech": bool(transcript)
        }
    except Exception as e:
        print(f"[STT] Error during transcription: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    # 0.0.0.0으로 열어야 런팟 프록시를 통해 외부(로컬 PC)에서 접속 가능합니다.
    uvicorn.run(app, host="0.0.0.0", port=8000)
