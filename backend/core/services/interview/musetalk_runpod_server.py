import copy, os, sys, tempfile, uvicorn, hashlib
import numpy as np
import cv2
import torch
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response
from tqdm import tqdm

# /opt/musetalk 기준 상대 경로
MODEL_DIR = './models'

app = FastAPI()

_vae = None
_unet = None
_pe = None
_audio_processor = None
_whisper = None
_device = None
_weight_dtype = None
_timesteps = None

# 아바타 이미지 사전처리 캐시 (이미지별로 캐싱)
_avatar_cache = {}  # { img_hash: cache_data }


def get_models():
    global _vae, _unet, _pe, _audio_processor, _whisper, _device, _weight_dtype, _timesteps
    if _unet is not None:
        return

    os.chdir('/opt/musetalk')
    sys.path.insert(0, '/opt/musetalk')

    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _weight_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    print(f"[MuseTalk] Loading models on {_device}...")

    from musetalk.utils.utils import load_all_model
    from musetalk.utils.audio_processor import AudioProcessor
    from transformers import WhisperModel

    _vae, _unet, _pe = load_all_model(
        unet_model_path=f"{MODEL_DIR}/musetalk/pytorch_model.bin",
        vae_type="sd-vae",
        unet_config=f"{MODEL_DIR}/musetalk/musetalk.json",
        device=_device,
    )
    _pe = _pe.to(dtype=_weight_dtype, device=_device)
    _vae.vae = _vae.vae.to(dtype=_weight_dtype, device=_device)
    _unet.model = _unet.model.to(dtype=_weight_dtype, device=_device)
    _timesteps = torch.tensor([0], device=_device)

    _audio_processor = AudioProcessor(feature_extractor_path=f"{MODEL_DIR}/whisper")
    _whisper = WhisperModel.from_pretrained(f"{MODEL_DIR}/whisper")
    _whisper = _whisper.to(device=_device, dtype=_weight_dtype).eval()
    _whisper.requires_grad_(False)

    print("[MuseTalk] All models loaded.")


def _precompute_avatar(image_path: str, img_hash: str):
    """아바타 이미지의 랜드마크 + VAE latent를 사전 계산하여 캐시에 저장."""
    global _avatar_cache

    from musetalk.utils.preprocessing import get_landmark_and_bbox, coord_placeholder
    from musetalk.utils.face_parsing import FaceParsing

    print("[MuseTalk] 아바타 사전처리 시작...")
    extra_margin = 10

    coord_list, frame_list = get_landmark_and_bbox([image_path], upperbondrange=0)

    input_latent_list = []
    for bbox, frame in zip(coord_list, frame_list):
        if bbox == coord_placeholder:
            continue
        x1, y1, x2, y2 = bbox
        y2 = min(y2 + extra_margin, frame.shape[0])
        crop_frame = cv2.resize(frame[y1:y2, x1:x2], (256, 256), interpolation=cv2.INTER_LANCZOS4)
        latents = _vae.get_latents_for_unet(crop_frame)
        input_latent_list.append(latents)

    if not input_latent_list:
        raise ValueError("아바타 이미지에서 얼굴을 감지하지 못했습니다.")

    _avatar_cache[img_hash] = {
        'coord_list_cycle': coord_list + coord_list[::-1],
        'frame_list_cycle': frame_list + frame_list[::-1],
        'input_latent_list_cycle': input_latent_list + input_latent_list[::-1],
        'fp': FaceParsing(),
        'extra_margin': extra_margin,
    }
    print(f"[MuseTalk] 아바타 사전처리 완료 ({img_hash[:8]}). 이후 요청은 캐시를 사용합니다.")


@app.on_event("startup")
def startup():
    get_models()

    # 서버 시작 시 두 아바타 미리 워밍업 (첫 요청 지연 방지)
    avatar_dir = '/app/media/avatars'
    for avatar_file in ['interviewer_woman.png', 'interviewer_man.png']:
        avatar_path = os.path.join(avatar_dir, avatar_file)
        if os.path.exists(avatar_path):
            with open(avatar_path, 'rb') as f:
                image_bytes = f.read()
            img_hash = hashlib.md5(image_bytes).hexdigest()
            if img_hash not in _avatar_cache:
                print(f"[MuseTalk] 워밍업: {avatar_file}")
                import tempfile as _tmp
                with _tmp.NamedTemporaryFile(suffix='.png', delete=False) as tf:
                    tf.write(image_bytes)
                    tmp_path = tf.name
                try:
                    _precompute_avatar(tmp_path, img_hash)
                finally:
                    os.unlink(tmp_path)


@app.get("/health")
def health():
    return {"status": "ok", "model": "musetalk-v15"}


@app.post("/generate")
async def generate(
    image: UploadFile = File(...),
    audio: UploadFile = File(...),
    fps: int = Form(20),
):
    try:
        get_models()

        from musetalk.utils.utils import datagen
        from musetalk.utils.blending import get_image

        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = os.path.join(tmpdir, "avatar.png")
            audio_path = os.path.join(tmpdir, "audio.wav")

            image_bytes = await image.read()
            with open(image_path, 'wb') as f:
                f.write(image_bytes)
            with open(audio_path, 'wb') as f:
                f.write(await audio.read())

            # 이미지 해시로 캐시 조회, 없으면 사전처리
            img_hash = hashlib.md5(image_bytes).hexdigest()
            if img_hash not in _avatar_cache:
                _precompute_avatar(image_path, img_hash)

            cache = _avatar_cache[img_hash]
            coord_list_cycle = cache['coord_list_cycle']
            frame_list_cycle = cache['frame_list_cycle']
            input_latent_list_cycle = cache['input_latent_list_cycle']
            fp = cache['fp']
            extra_margin = cache['extra_margin']

            # 오디오 피처 추출
            whisper_input_features, librosa_length = _audio_processor.get_audio_feature(audio_path)
            whisper_chunks = _audio_processor.get_whisper_chunk(
                whisper_input_features, _device, _weight_dtype, _whisper, librosa_length,
                fps=fps, audio_padding_length_left=0, audio_padding_length_right=0,
            )

            # 배치 추론
            from musetalk.utils.preprocessing import coord_placeholder
            video_num = len(whisper_chunks)
            batch_size = 16
            gen = datagen(
                whisper_chunks=whisper_chunks,
                vae_encode_latents=input_latent_list_cycle,
                batch_size=batch_size,
                delay_frame=0,
                device=_device,
            )

            res_frame_list = []
            for whisper_batch, latent_batch in tqdm(gen, total=int(np.ceil(video_num / batch_size))):
                audio_feature_batch = _pe(whisper_batch)
                latent_batch = latent_batch.to(dtype=_weight_dtype)
                pred_latents = _unet.model(latent_batch, _timesteps, encoder_hidden_states=audio_feature_batch).sample
                recon = _vae.decode_latents(pred_latents)
                res_frame_list.extend(recon)

            # 합성
            result_frames = []
            for i, res_frame in enumerate(res_frame_list):
                bbox = coord_list_cycle[i % len(coord_list_cycle)]
                ori_frame = copy.deepcopy(frame_list_cycle[i % len(frame_list_cycle)])
                if bbox == coord_placeholder:
                    result_frames.append(ori_frame)
                    continue
                x1, y1, x2, y2 = bbox
                y2 = min(y2 + extra_margin, ori_frame.shape[0])
                try:
                    res_frame = cv2.resize(res_frame.astype(np.uint8), (x2 - x1, y2 - y1))
                except Exception:
                    result_frames.append(ori_frame)
                    continue
                combine_frame = get_image(ori_frame, res_frame, [x1, y1, x2, y2], mode="jaw", fp=fp)
                result_frames.append(combine_frame)

            # BGR → RGB 변환 후 저장
            import imageio
            output_path = os.path.join(tmpdir, "output.mp4")
            final_path = os.path.join(tmpdir, "final.mp4")
            result_frames_rgb = [cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in result_frames]
            imageio.mimwrite(output_path, result_frames_rgb, 'FFMPEG', fps=fps, codec='libx264', pixelformat='yuv420p')

            # 오디오 합치기
            os.system(f"ffmpeg -i {output_path} -i {audio_path} -c:v copy -c:a aac -shortest {final_path} -y -loglevel quiet")
            out_path = final_path if os.path.exists(final_path) else output_path

            with open(out_path, 'rb') as f:
                video_data = f.read()

        return Response(content=video_data, media_type="video/mp4")

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/idle")
async def idle(image: UploadFile = File(...)):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = os.path.join(tmpdir, "avatar.png")
            output_path = os.path.join(tmpdir, "idle.mp4")

            with open(image_path, 'wb') as f:
                f.write(await image.read())

            img = cv2.imread(image_path)
            height, width = img.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, 20, (width, height))
            for _ in range(20):
                out.write(img)
            out.release()

            with open(output_path, 'rb') as f:
                video_data = f.read()

        return Response(content=video_data, media_type="video/mp4")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
