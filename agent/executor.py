import sys
import io
import traceback

def execute_python_code(code_string: str, test_script: str) -> dict:
    """
    Python 코드를 동적으로 실행하여 성공 여부를 확인합니다.
    """
    # 표준 출력 캡처
    stdout_capture = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = stdout_capture
    
    # 🔑 NameError 방지를 위해 글로벌 네임스페이스 복사 및 통합 사용
    # 클래스 내 super(SimpleNet, self) 등이 정상 작동하려면 exec 시 globals/locals를 동일하게 두는 것이 안전함
    exec_env = globals().copy() 
    
    full_code = f"{code_string}\n\n{test_script}"
    
    success = False
    error_msg = ""
    
    try:
        # 🔑 exec() 실행 시 네임스페이스를 하나로 통일하여 참조 문제 해결
        exec(full_code, exec_env)
        success = True
    except Exception:
        # 에러 발생 시 트레이스백 캡처
        error_msg = traceback.format_exc()
        success = False
    finally:
        # 표준 출력 복구
        sys.stdout = old_stdout
        
    return {
        "success": success,
        "output": stdout_capture.getvalue(),
        "error": error_msg
    }
