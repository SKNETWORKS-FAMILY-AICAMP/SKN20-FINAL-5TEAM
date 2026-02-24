# backend/core/views/pseudocode_execution.py
"""
Python 코드 실행 및 검증 엔드포인트 (Docker Sandbox 기반)
보안: Docker 컨테이너를 사용하여 격리된 환경에서 코드 실행
수정일: 2026-02-08
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import subprocess
import json
import time

# Docker 실행 설정
TIMEOUT_SECONDS = 10 # Relaxed timeout for Windows environment
MEMORY_LIMIT = "512m"
CPU_LIMIT = "1.0"
DOCKER_IMAGE = "coduck-sandbox:latest"

def check_security(user_code):
    """
    위험한 패턴을 정적 분석으로 사전 차단
    """
    dangerous_keywords = ['import os', 'import sys', 'import subprocess', 'from os', 'from sys', '__import__', 'eval(', 'exec(']
    for keyword in dangerous_keywords:
        if keyword in user_code:
            return {
                "success": False,
                "error": "보안 위반: 허용되지 않은 모듈이나 함수가 감지되었습니다. (os, sys, subprocess, eval 등 금지)"
            }
    return None

def generate_runner_script(user_code, function_name, test_cases):
    """
    컨테이너 내부에서 실행될 파이썬 스크립트를 생성합니다.
    """
    # JSON 직렬화를 위한 헬퍼 함수 포함
    runner_script = f"""
import sys
import json
import traceback
# 의존성 설치가 완료된 이미지 사용으로 즉시 임포트 가능
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
import random
import re

# === 사용자 코드 영역 ===
try:
{_indent_code(user_code, 4)}
except Exception as e:
    print(json.dumps({{
        "error": f"코드 정의 중 에러 발생: {{str(e)}}",
        "traceback": traceback.format_exc(),
        "success": False
    }}))
    sys.exit(1)

# === 테스트 실행 영역 ===
def run_tests():
    results = []
    passed_count = 0
    total_count = 0
    
    test_cases = {json.dumps(test_cases)}
    
    # 함수 존재 여부 확인
    if '{function_name}' not in locals():
        print(json.dumps({{
            "error": "함수 '{function_name}'를 찾을 수 없습니다.",
            "success": False
        }}))
        return

    target_func = locals()['{function_name}']
    
    for idx, test in enumerate(test_cases):
        total_count += 1
        case_result = {{
            "test_number": idx + 1,
            "description": test.get('description', f'Test {{idx + 1}}'),
            "passed": False,
            "message": "",
            "actual": None,
            "expected": test.get('expected')
        }}
        
        try:
            # 입력값 준비
            inputs = test.get('input')
            if isinstance(inputs, dict):
                actual = target_func(**inputs)
            elif isinstance(inputs, list):
                actual = target_func(*inputs)
            else:
                actual = target_func(inputs)
            
            # 결과 변환 (NumPy/Pandas -> Python Native)
            if isinstance(actual, (np.ndarray, np.generic)):
                actual = actual.tolist()
            elif isinstance(actual, pd.DataFrame):
                actual = actual.values.tolist()
            elif isinstance(actual, pd.Series):
                actual = actual.tolist()
            elif isinstance(actual, tuple):
                actual = [x.tolist() if isinstance(x, (np.ndarray, np.generic)) else x for x in actual]
                
            case_result['actual'] = actual
            
            # 검증 로직
            expected = test.get('expected')
            expected_structure = test.get('expected_structure')
            expected_error = test.get('expected_error')
            
            if expected_error:
                # 에러가 발생해야 정답인 경우 (현재 try 블록 안에 있으므로 여기 오면 실패)
                case_result['passed'] = False
                case_result['message'] = "에러가 발생해야 하는데 정상 실행됨"
                
            elif expected_structure:
                # 구조 검증 (간소화)
                case_result['passed'] = True
                case_result['message'] = "구조 검증 통과"
                
                # 상세 구조 체크 로직이 필요하면 여기에 추가
                if 'train_mean_close_to' in expected_structure:
                    if isinstance(actual, (list, tuple)) and len(actual) >= 1:
                        train_data = np.array(actual[0])
                        if abs(np.mean(train_data) - expected_structure['train_mean_close_to']) > 0.1:
                            case_result['passed'] = False
                            case_result['message'] = "학습 데이터 평균 불일치"

            else:
                # 값 비교
                if compare_values(actual, expected):
                    case_result['passed'] = True
                    case_result['message'] = "정답"
                else:
                    case_result['passed'] = False
                    case_result['message'] = f"결과 불일치"
                    
        except Exception as e:
            if test.get('expected_error'):
                case_result['passed'] = True
                case_result['message'] = f"예상된 에러 발생: {{str(e)}}"
            else:
                case_result['passed'] = False
                case_result['message'] = f"실행 중 에러: {{str(e)}}"
                case_result['error'] = str(e)
        
        if case_result['passed']:
            passed_count += 1
        results.append(case_result)

    # 최종 결과 출력
    print(json.dumps({{
        "success": True,
        "all_passed": passed_count == total_count,
        "passed_count": passed_count,
        "total_count": total_count,
        "results": results
    }}))

def compare_values(actual, expected, tolerance=1e-5):
    # 타입 불일치 허용 (리스트 vs 튜플)
    if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
        if len(actual) != len(expected): return False
        return all(compare_values(a, e, tolerance) for a, e in zip(actual, expected))
    
    # 숫자 비교
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return abs(actual - expected) <= tolerance
        
    return actual == expected

if __name__ == "__main__":
    run_tests()
"""
    return runner_script

def _indent_code(code, spaces):
    indent = " " * spaces
    return '\n'.join(indent + line if line.strip() else line for line in code.split('\n'))

def _execute_in_docker(script_code):
    """
    Docker 컨테이너에서 스크립트를 실행합니다.
    """
    docker_cmd = [
        "docker", "run",
        "--rm",             # 실행 후 컨테이너 삭제
        "--network", "none", # 네트워크 격리 (이미지 내부에 라이브러리가 있으므로 외부 통신 불필요)
        "--memory", MEMORY_LIMIT,
        "--cpus", CPU_LIMIT,
        "-i",               # stdin 개방
        DOCKER_IMAGE,
        "python", "-"       # stdin에서 코드를 읽어 실행 (sh -c 제거해도 됨)
    ]

    try:
        # Docker 실행
        process = subprocess.Popen(
            docker_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            stdout, stderr = process.communicate(input=script_code, timeout=TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            process.kill()
            return {
                "error": f"Execution timed out ({TIMEOUT_SECONDS}s)",
                "success": False
            }

        if process.returncode != 0:
            return {
                "error": f"Runtime Error: {stderr}",
                "success": False,
                "details": stderr
            }

        # 결과 파싱 (마지막 줄에 JSON이 있다고 가정)
        try:
            # stdout에 다른 출력이 섞여있을 수 있으므로 뒤에서부터 탐색
            lines = stdout.strip().split('\n')
            last_line = lines[-1] if lines else ""
            return json.loads(last_line)
        except json.JSONDecodeError:
            # SyntaxError 등으로 JSON 출력이 안된 경우
            return {
                "success": False,
                "error": f"Execution Error (Syntax/Runtime): {stdout.strip()}",
                "results": [],
                "output": stdout.strip()
            }

    except FileNotFoundError:
        return {
            "error": "Docker not found on server",
            "success": False
        }
    except Exception as e:
        return {
            "error": f"Server Error: {str(e)}",
            "success": False
        }

@api_view(['POST'])
@permission_classes([AllowAny])
def execute_python_code(request):
    """
    [POST] /api/core/pseudocode/execute/
    Docker 샌드박스를 이용한 Python 코드 실행 및 테스트
    """
    try:
        code = request.data.get('code', '')
        function_name = request.data.get('function_name', '')
        test_cases = request.data.get('test_cases', [])

        if not code or not function_name:
            return Response(
                {"error": "Code and function_name are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. 보안 체크 (정적 분석)
        security_check = check_security(code)
        if security_check:
            return Response(security_check, status=status.HTTP_200_OK)

        # 2. 실행할 스크립트 생성
        runner_script = generate_runner_script(code, function_name, test_cases)
        
        # 3. Docker에서 실행
        result = _execute_in_docker(runner_script)
        
        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        error_msg = f"Internal Server Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg) # 서버 로그에 출력
        return Response(
            {"error": str(e), "success": False, "details": traceback.format_exc()},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# URL 설정 (urls.py에 추가)
"""
from django.urls import path
from .views.code_execution import execute_python_code

urlpatterns = [
    path('api/code/execute-python/', execute_python_code, name='execute_python_code'),
]
"""