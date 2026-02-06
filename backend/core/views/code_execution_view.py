# 수정일: 2026-02-06
# 수정내용: On-demand Docker 기반 코드 실행 샌드박스 뷰

import subprocess
import tempfile
import os
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class CodeExecutionView(APIView):
    """
    On-demand Docker 코드 실행 샌드박스

    사용자가 제출한 Python 코드를 격리된 Docker 컨테이너에서 실행하고
    stdout/stderr 결과를 반환합니다.

    - 컨테이너는 요청 시 자동 생성되고 실행 후 자동 삭제됩니다
    - 리소스 제한: CPU 0.5, 메모리 256MB, 타임아웃 30초
    - 네트워크 비활성화로 외부 접근 차단
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    # 실행 제한 설정
    TIMEOUT_SECONDS = 30
    MEMORY_LIMIT = "256m"
    CPU_LIMIT = "0.5"

    # 지원되는 Docker 이미지
    SUPPORTED_IMAGES = {
        "basic": "python:3.10-slim",
        "pytorch": "pytorch-sandbox:latest"  # 커스텀 PyTorch 이미지
    }

    def post(self, request):
        code = request.data.get('code', '')
        test_code = request.data.get('test_code', '')  # 검증용 테스트 코드
        image_type = request.data.get('image', 'basic')  # basic 또는 pytorch

        if not code:
            return Response(
                {"error": "코드가 필요합니다"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 이미지 타입 검증
        if image_type not in self.SUPPORTED_IMAGES:
            image_type = "basic"

        # 실행할 전체 코드 구성
        full_code = code
        if test_code:
            full_code = f"{code}\n\n# === 자동 검증 코드 ===\n{test_code}"

        try:
            docker_image = self.SUPPORTED_IMAGES[image_type]
            result = self._execute_in_docker(full_code, docker_image)
            return Response(result, status=status.HTTP_200_OK)

        except subprocess.TimeoutExpired:
            return Response({
                "success": False,
                "stdout": "",
                "stderr": f"실행 시간 초과 ({self.TIMEOUT_SECONDS}초)",
                "exit_code": -1,
                "error_type": "timeout"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "error_type": "system"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _execute_in_docker(self, code: str, docker_image: str = "python:3.10-slim") -> dict:
        """
        Docker 컨테이너에서 코드를 실행합니다.

        Windows에서는 docker run의 stdin으로 코드를 전달하고,
        컨테이너 내부에서 python -c로 실행합니다.
        """
        start_time = time.time()

        # PyTorch 이미지는 더 큰 메모리가 필요
        memory_limit = "512m" if "pytorch" in docker_image else self.MEMORY_LIMIT

        # Docker 명령어 구성
        # --rm: 컨테이너 자동 삭제
        # --network none: 네트워크 비활성화 (보안)
        # --memory: 메모리 제한
        # --cpus: CPU 제한
        # --read-only: 파일시스템 읽기 전용 (임시 디렉토리 제외)
        docker_cmd = [
            "docker", "run",
            "--rm",
            "--network", "none",
            "--memory", memory_limit,
            "--cpus", self.CPU_LIMIT,
            "--read-only",
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=128m",
            "-i",  # stdin 사용
            docker_image,
            "python", "-c", code
        ]

        try:
            # 프로세스 실행
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT_SECONDS
            )

            execution_time = time.time() - start_time

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "execution_time": round(execution_time, 2),
                "error_type": None if result.returncode == 0 else "runtime"
            }

        except FileNotFoundError:
            # Docker가 설치되어 있지 않은 경우
            return {
                "success": False,
                "stdout": "",
                "stderr": "Docker가 설치되어 있지 않습니다. Docker Desktop을 설치해주세요.",
                "exit_code": -1,
                "error_type": "docker_not_found"
            }


@method_decorator(csrf_exempt, name='dispatch')
class BehaviorVerificationView(APIView):
    """
    행동 기반 검증 뷰

    사용자 코드를 실행하여 실제 동작을 검증합니다.
    문자열 매칭이 아닌 실제 코드 실행 결과로 정답 여부를 판단합니다.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    TIMEOUT_SECONDS = 30
    MEMORY_LIMIT = "512m"  # PyTorch 등을 위해 더 큰 메모리
    CPU_LIMIT = "1.0"

    # 지원되는 Docker 이미지
    SUPPORTED_IMAGES = {
        "basic": "python:3.10-slim",
        "pytorch": "pytorch-sandbox:latest"
    }

    def post(self, request):
        user_code = request.data.get('user_code', '')
        verification_code = request.data.get('verification_code', '')
        problem_id = request.data.get('problem_id', '')
        image_type = request.data.get('image', 'pytorch')  # 기본값 pytorch

        if not user_code or not verification_code:
            return Response(
                {"error": "user_code와 verification_code가 필요합니다"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 이미지 타입 검증
        if image_type not in self.SUPPORTED_IMAGES:
            image_type = "pytorch"

        docker_image = self.SUPPORTED_IMAGES[image_type]

        # 검증 코드 구성
        # verification_code에 __USER_CODE__ 플레이스홀더가 있으면 치환
        # 없으면 사용자 코드 실행 후 검증 코드로 결과 확인
        if '__USER_CODE__' in verification_code:
            # 플레이스홀더 방식: verification_code 내에서 사용자 코드 위치 제어
            # __USER_CODE__ 앞의 들여쓰기를 감지하여 user_code에 적용
            import re
            match = re.search(r'^(\s*)__USER_CODE__', verification_code, re.MULTILINE)
            if match:
                indent = match.group(1)
                # user_code의 모든 줄에 들여쓰기 추가
                indented_user_code = '\n'.join(indent + line if line.strip() else line
                                               for line in user_code.split('\n'))
                full_code = verification_code.replace(match.group(0), indented_user_code)
            else:
                # 들여쓰기 없이 단순 치환
                full_code = verification_code.replace('__USER_CODE__', user_code)
        else:
            # 기존 방식: 사용자 코드 먼저, 검증 코드 나중
            full_code = f"""
import sys
import json

# === 사용자 코드 ===
try:
{self._indent_code(user_code, 4)}
except Exception as e:
    print(json.dumps({{"verified": False, "error": str(e), "error_type": "user_code"}}))
    sys.exit(0)

# === 검증 코드 ===
try:
{self._indent_code(verification_code, 4)}
except Exception as e:
    print(json.dumps({{"verified": False, "error": str(e), "error_type": "verification"}}))
    sys.exit(0)
"""

        try:
            # 디버그: 실행할 전체 코드 출력 (처음 500자)
            print(f"[DEBUG] ===== FULL CODE TO EXECUTE =====")
            print(f"[DEBUG] {full_code[:1000]}")
            print(f"[DEBUG] ===== END OF CODE =====")

            result = self._execute_in_docker(full_code, docker_image)

            # 디버그 로깅
            print(f"[DEBUG] Docker result success: {result['success']}")
            print(f"[DEBUG] stdout length: {len(result.get('stdout', ''))}")
            print(f"[DEBUG] stdout: {result.get('stdout', '')[:500]}")
            print(f"[DEBUG] stderr: {result.get('stderr', '')[:500]}")

            # stdout에서 검증 결과 파싱
            if result["success"] and result["stdout"]:
                import json as json_module
                try:
                    last_line = result["stdout"].strip().split('\n')[-1]
                    print(f"[DEBUG] Parsing last line: {last_line}")
                    verification_result = json_module.loads(last_line)
                    return Response({
                        "verified": verification_result.get("verified", False),
                        "message": verification_result.get("message", ""),
                        "details": verification_result.get("details", {}),
                        "execution_time": result["execution_time"]
                    }, status=status.HTTP_200_OK)
                except json_module.JSONDecodeError as e:
                    print(f"[DEBUG] JSON decode error: {e}")
                    pass

            return Response({
                "verified": False,
                "message": result.get("stderr", "실행 오류"),
                "stdout": result.get("stdout", ""),
                "execution_time": result.get("execution_time", 0)
            }, status=status.HTTP_200_OK)

        except subprocess.TimeoutExpired:
            return Response({
                "verified": False,
                "message": f"실행 시간 초과 ({self.TIMEOUT_SECONDS}초)",
                "error_type": "timeout"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "verified": False,
                "message": str(e),
                "error_type": "system"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _indent_code(self, code: str, spaces: int) -> str:
        """코드를 지정된 공백만큼 들여쓰기합니다."""
        indent = " " * spaces
        lines = code.split('\n')
        return '\n'.join(indent + line for line in lines)

    def _execute_in_docker(self, code: str, docker_image: str = "pytorch-sandbox:latest") -> dict:
        """Docker 컨테이너에서 코드를 실행합니다."""
        import time
        start_time = time.time()

        # PyTorch 이미지는 더 큰 메모리가 필요
        memory_limit = "512m" if "pytorch" in docker_image else "256m"

        docker_cmd = [
            "docker", "run",
            "--rm",
            "--network", "none",
            "--memory", memory_limit,
            "--cpus", self.CPU_LIMIT,
            "--read-only",
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=128m",
            "-i",
            docker_image,
            "python", "-c", code
        ]

        try:
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT_SECONDS
            )

            execution_time = time.time() - start_time

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "execution_time": round(execution_time, 2)
            }

        except FileNotFoundError:
            raise Exception("Docker가 설치되어 있지 않습니다. Docker Desktop을 설치하거나 문자열 검증을 사용하세요.")
