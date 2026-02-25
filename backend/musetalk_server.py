import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from fastapi import FastAPI
from pydantic import BaseModel
from core.services.interview.musetalk_service import musetalk_service

app = FastAPI()


class GenerateRequest(BaseModel):
    image_path: str
    audio_path: str
    output_path: str
    fps: int = 25


class IdleRequest(BaseModel):
    image_path: str
    output_path: str


@app.on_event("startup")
def startup():
    musetalk_service.initialize_models()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate")
def generate(req: GenerateRequest):
    result = musetalk_service.generate_video(
        req.image_path, req.audio_path, req.output_path, req.fps
    )
    return {"output_path": result}


@app.post("/idle")
def idle(req: IdleRequest):
    result = musetalk_service.get_idle_loop(req.image_path, req.output_path)
    return {"output_path": result}
