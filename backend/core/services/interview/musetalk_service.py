import os
import requests as _requests

# musetalk 컨테이너 URL (설정 시 HTTP 클라이언트 모드로 동작)
MUSETALK_SERVICE_URL = os.environ.get('MUSETALK_SERVICE_URL', '')

# Defer heavy imports to prevent server initialization hang
torch = None
np = None
load_all_model = None
get_landmarker = None
Inference = None
GFPGANer = None

def _lazy_import():
    global torch, np, load_all_model, get_landmarker, Inference, GFPGANer
    if torch is None:
        import torch
    if np is None:
        import numpy as np
    
    try:
        from musetalk.utils.utils import load_all_model as _load
        from musetalk.utils.preprocessing import get_landmarker as _get
        from musetalk.predict import Inference as _inf
        load_all_model, get_landmarker, Inference = _load, _get, _inf
    except ImportError:
        pass

    try:
        from gfpgan import GFPGANer as _gfp
        GFPGANer = _gfp
    except ImportError:
        pass

class MuseTalkService:
    """
    실시간 AI 면접관 립싱크 비디오 생성을 위한 MuseTalk 서비스
    125GB GPU를 최대한 활용하여 모형을 상주시키고 실시간성을 확보합니다.
    """
    _instance = None
    _is_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MuseTalkService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._is_initialized:
            self.device = None
            self.audio_processor = None
            self.vae = None
            self.unet = None
            self.pe = None
            self.landmarker = None
            self.restorer = None
            self._is_initialized = True

    def initialize_models(self):
        """
        초기 1회 GPU에 모델 로드 (fp16 최적화)
        """
        _lazy_import()
        
        if self.device is None:
            import torch
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if self.unet is not None:
            return # Already loaded

        print(f"[MuseTalkService] 모델 로딩 시작 (Target Device: {self.device})")
        try:
            # 1. MuseTalk 핵심 모듈 로드 (backend/models 폴더 기준)
            # MuseTalk 내부 load_all_model은 환경변수나 기본 경로를 참고하므로 설정이 필요할 수 있음
            import os
            base_dir = os.path.join(settings.BASE_DIR, "models")
            
            # 1. MuseTalk 핵심 모듈 로드
            if load_all_model:
                # MuseTalk 1.5+ 기준: 라이브러리 내부 경로 설정을 위해 환경변수 세팅 가능
                self.audio_processor, self.vae, self.unet, self.pe = load_all_model()
            
            # 2. 랜드마크 추출 모듈 (Mouth crop용)
            if get_landmarker:
                self.landmarker = get_landmarker(self.device)

            # 3. GFPGAN 얼굴 보정 모델 로드 (ROOT의 GFPGANv1.4.pth 활용)
            gfpgan_model_path = os.path.join(settings.BASE_DIR, "GFPGANv1.4.pth")
            if GFPGANer and os.path.exists(gfpgan_model_path):
                self.restorer = GFPGANer(model_path=gfpgan_model_path, upscale=2, arch='clean', channel_multiplier=2, device=self.device)
                print("[MuseTalkService] GFPGANer 로드 성공")
            else:
                print(f"[MuseTalkService] 경고: GFPGAN 모델 파일을 찾을 수 없습니다 ({gfpgan_model_path}). 화질 보정 없이 진행됩니다.")
                
            print("[MuseTalkService] 모든 모델 로드 완료")
        except Exception as e:
            print(f"[MuseTalkService] 모델 로드 중 오류 발생: {e}")
            # 리얼 모드에서는 모델 로드 실패 시 로그를 남기고 raise 하는 것이 디버깅에 유리
            raise e

    def generate_video(self, image_path: str, audio_path: str, output_path: str, fps: int = 25) -> str:
        """
        이미지와 음성(WAV/MP3)을 입력받아 실제 립싱크 영상을 생성합니다.
        """
        if MUSETALK_SERVICE_URL:
            try:
                with open(image_path, 'rb') as img_f, open(audio_path, 'rb') as aud_f:
                    resp = _requests.post(
                        f'{MUSETALK_SERVICE_URL}/generate',
                        files={'image': img_f, 'audio': aud_f},
                        data={'fps': fps},
                        timeout=120
                    )
                resp.raise_for_status()
                output_dir = os.path.dirname(output_path)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(resp.content)
                return output_path
            except Exception as e:
                print(f'[MuseTalkService] musetalk 서비스 호출 실패, mock으로 대체: {e}')
                return self._mock_generate(image_path, audio_path, output_path)

        _lazy_import()

        if self.unet is None:
            self.initialize_models()

        try:
            if Inference is None or self.landmarker is None:
                raise ImportError("MuseTalk libraries are not installed. Please check Docker environment.")

            # 1. 이미지에서 얼굴 영역 및 랜드마크 추출
            face_info = self.landmarker.get_face_area(image_path)
            
            # 2. 음성 특성 추출 및 MuseTalk 추론 엔진 초기화
            inference_engine = Inference(
                audio_processor=self.audio_processor,
                vae=self.vae,
                unet=self.unet,
                pe=self.pe,
                device=self.device
            )

            # 3. 립싱크 영상 생성
            print(f"[MuseTalkService] 실제 추론 시작. Image: {image_path}, Audio: {audio_path}")
            video_result = inference_engine.predict(
                source_image=image_path,
                source_audio=audio_path,
                face_info=face_info,
                fps=fps
            )
            
            # (옵션) 얼굴 보정 적용
            if self.restorer:
                print("[MuseTalkService] GFPGAN 얼굴 보정 적용 중...")
                video_result = self.restorer.enhance_video(video_result)

            # 4. 최종 결과물 프레임 + 오디오 합성 저장
            video_result.save(output_path)
            print(f"[MuseTalkService] 실제 영상 생성 완료: {output_path}")

            return output_path

        except Exception as e:
            print(f"[MuseTalkService] 비디오 생성 중 예외 발생: {e}")
            # 오류 발생 시에만 Mock으로 fallback (UI 중단 방지)
            return self._mock_generate(image_path, audio_path, output_path)

    def _mock_generate(self, image_path: str, audio_path: str, output_path: str) -> str:
        """
        Fallback Mock 함수: OpenCV를 사용하여 이미지를 실제 재생 가능한 MP4로 변환합니다.
        """
        print("[MuseTalkService] [WARNING] MOCK 비디오 생성을 실행합니다. (OpenCV 기반)")
        import os
        import cv2
        import numpy as np
        
        try:
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # 이미지 읽기
            img = cv2.imread(image_path)
            if img is None:
                # 이미지를 읽을 수 없는 경우 더미 데이터라도 생성
                with open(output_path, "wb") as f:
                    f.write(b"MOCK MP4 DATA (IMAGE NOT FOUND)")
                return output_path

            height, width, layers = img.shape
            size = (width, height)
            
            # MP4 파일 생성을 위한 VideoWriter 설정 (시뮬레이션용 25fps, 1초)
            # H264 대신 XVID 또는 avc1 사용 (환경에 따라 다를 수 있음)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, 25, size)
            
            # 25프레임(약 1초) 동안 동일 이미지 기록
            for _ in range(25):
                out.write(img)
            out.release()
            
            print(f"[MuseTalkService] Mock MP4 생성 완료: {output_path}")
        except Exception as e:
            print(f"[MuseTalkService] Mock 생성 중 오류: {e}")
            with open(output_path, "wb") as f:
                f.write(b"MOCK MP4 DATA (ERROR)")
        
        return output_path

    def get_idle_loop(self, image_path: str, output_path: str) -> str:
        """
        아무 말도 하지 않을 때 (Idle 상태) 사용할 기본 '눈 깜빡임 영상'을 반환/생성합니다.
        """
        if os.path.exists(output_path):
            return output_path

        if MUSETALK_SERVICE_URL:
            try:
                with open(image_path, 'rb') as img_f:
                    resp = _requests.post(
                        f'{MUSETALK_SERVICE_URL}/idle',
                        files={'image': img_f},
                        timeout=60
                    )
                resp.raise_for_status()
                output_dir = os.path.dirname(output_path)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(resp.content)
                return output_path
            except Exception as e:
                print(f'[MuseTalkService] musetalk idle 호출 실패, mock으로 대체: {e}')
                return self._mock_generate(image_path, '', output_path)
        
        # TODO: MuseV 등 이미지 기반 눈 깜빡임 루프 생성 로직
        print(f"[MuseTalkService] Idle 영상 생성 중: {output_path}")
        return self._mock_generate(image_path, "", output_path)

# 싱글톤 인스턴스 전역 접근자
musetalk_service = MuseTalkService()
