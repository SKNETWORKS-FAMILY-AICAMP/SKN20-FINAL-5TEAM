# 수정일: 2026-02-06
# 수정내용: 나노바나나(Gemini API)를 활용한 아바타 생성 유틸리티 구현 및 Supabase Storage 연동

import os
import uuid
import requests
import io
from PIL import Image
from django.conf import settings
from google import genai
from google.genai import types

def upload_to_supabase(file_data, bucket_name='avatars', file_path=None):
    """
    Supabase Storage에 파일을 업로드합니다.
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY") # Service Role Key 필요
    
    if not supabase_url or not supabase_key:
        print("DEBUG: Supabase credentials missing (SUPABASE_URL/SUPABASE_KEY)")
        return None

    if not file_path:
        file_path = f"avatar_{uuid.uuid4().hex}.png"

    # Supabase Storage API Endpoint
    # URL 형식: https://[PROJECT_ID].supabase.co/storage/v1/object/[BUCKET]/[PATH]
    url = f"{supabase_url.rstrip('/')}/storage/v1/object/{bucket_name}/{file_path}"
    
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "image/png"
    }

    try:
        response = requests.post(url, headers=headers, data=file_data)
        if response.status_code == 200:
            # 퍼블릭 URL 반환
            return f"{supabase_url.rstrip('/')}/storage/v1/object/public/{bucket_name}/{file_path}"
        else:
            print(f"DEBUG: Supabase upload failed ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        print(f"DEBUG: Supabase upload exception: {e}")
        return None

def optimize_image(image_bytes, size=(512, 512), quality=80):
    """
    이미지 데이터를 WebP 포맷으로 변환하고 리사이징하여 용량을 최적화합니다.
    [수정일: 2026-02-09] (Antigravity)
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # RGBA -> RGB 변환 (WebP는 투명도를 지원하지만 용량 최적화를 위해 필요한 경우)
        # 여기서는 투명도를 유지하면서 최적화 진행
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGBA")
        
        # 리사이징 (Lanczos 필터 사용)
        img = img.resize(size, Image.Resampling.LANCZOS)
        
        # WebP로 출력
        output = io.BytesIO()
        img.save(output, format="WEBP", quality=quality)
        optimized_data = output.getvalue()
        
        print(f"DEBUG: Image optimized. {len(image_bytes)} -> {len(optimized_data)} bytes")
        return optimized_data
    except Exception as e:
        print(f"DEBUG: Image optimization failed: {e}")
        return image_bytes # 실패 시 원본 반환

def generate_nano_banana_avatar(prompt, seed=None, save_local=True):
    """
    나노바나나(Gemini)를 통해 오리(Coduck) 기반 아바타 이미지를 생성합니다.
    save_local=False 인 경우 이미지 데이터를 bytes로 반환할 수 있도록 옵션 제공.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")

    import random
    
    # 아바타 본체(오리) 고정을 위한 핵심 프롬프트 (가장 앞에 배치)
    # [TIP] "A cute 3D character of a duck (Coduck)"를 항상 유지하여 결과 일관성 확보
    base_duck_prompt = "A cute 3D character of a duck (Coduck) as a main subject, Pixar style animation, highly detailed, "
    
    # 사용자의 입력이 오리 자체를 바꾸지 않도록 구조적 결합
    full_prompt = f"{base_duck_prompt} wearing {prompt}, cinematic lighting, vibrant colors"

    try:
        client = genai.Client(api_key=api_key)
        
        # 가용성 및 퀄리티가 검증된 최신 Imagen 모델 후보군
        model_candidates = [
            'models/imagen-3.0-generate-001',
            'models/imagen-3.0-fast-generate-001',
            'models/imagen-4.0-generate-001',
        ]
        
        response = None
        last_error = "No successful model response"
        
        for model_id in model_candidates:
            print(f"DEBUG: AI Generation attempt with {model_id}...", flush=True)
            try:
                # [수정일: 2026-02-07] 시드(Seed) 값 적용 (Antigravity)
                # 시드값이 없거나 비정상적일 경우 랜덤 생성
                safe_seed = int(seed) if seed and str(seed).isdigit() else random.randint(0, 2147483647)
                
                response = client.models.generate_images(
                    model=model_id,
                    prompt=full_prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        output_mime_type='image/png',
                        # [참고] 현재 Gemini API(google-genai)의 generate_images는 seed 파라미터를 지원하지 않아 제거함
                    )
                )
                if response and response.generated_images:
                    image_data = response.generated_images[0].image.image_bytes
                    
                    # [수정일: 2026-02-09] 이미지 최적화 적용
                    image_data = optimize_image(image_data)

                    if not save_local:
                        return {
                            'image_data': image_data,
                            'seed': seed,
                            'ai_generated': True,
                            'model_used': model_id
                        }

                    # 고유 파일명 생성 및 저장 (.webp 확장자 권장)
                    filename = f"avatar_{uuid.uuid4().hex}.webp"
                    media_path = os.path.join('avatars', filename)
                    abs_path = os.path.join(settings.MEDIA_ROOT, media_path)
                    
                    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                    with open(abs_path, 'wb') as f:
                        f.write(image_data)
                    
                    print(f"DEBUG: SUCCESSful AI generation with {model_id}", flush=True)
                    return {
                        'url': f"{settings.MEDIA_URL}{media_path}",
                        'seed': seed,
                        'ai_generated': True,
                        'model_used': model_id
                    }
            except Exception as e:
                last_error = str(e)
                print(f"DEBUG: AI attempt failed ({model_id}): {last_error}", flush=True)
                # Billing 관련 에러가 아니라면 다음 모델 시도
                if "INVALID_ARGUMENT" in last_error and "billed" in last_error.lower():
                    print("DEBUG: Billing restriction detected. Switching to intelligent fallback.", flush=True)
                    break
                continue

    except Exception as global_e:
        last_error = f"Client initialization error: {str(global_e)}"

    # [나노-바나나 폴백] AI 생성 실패 시 기본 오리 이미지로 대응
    # 복잡한 키워드 맵을 제거하고 시스템 안정성을 위해 기본 오리로 통일합니다.
    selected_fallback = "default_duck.png"
    
    print(f"DEBUG: AI Generation failed. Falling back to {selected_fallback}. Error: {last_error}", flush=True)

    return {
        'url': f"/media/avatars/{selected_fallback}",
        'seed': seed,
        'fallback': True,
        'error_msg': last_error # AI 실패 사유 전달
    }
