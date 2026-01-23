/* 
  생성일: 2026-01-24
  내용: Pyodide(WASM 기반 파이썬 엔진) 로드 및 코드 실행을 위한 Vue Composable
*/
import { ref, onMounted } from 'vue';

export function usePyodide() {
    const pyodide = ref(null);
    const isLoading = ref(true);
    const error = ref(null);
    const stdout = ref('');

    const initPyodide = async () => {
        try {
            if (window.loadPyodide) {
                pyodide.value = await window.loadPyodide({
                    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.1/full/",
                    stdout: (text) => {
                        stdout.value += text + '\n';
                        console.log("Python stdout:", text);
                    },
                    stderr: (text) => {
                        console.error("Python stderr:", text);
                    }
                });
                isLoading.value = false;
                console.log("Pyodide loaded successfully.");
            } else {
                throw new Error("Pyodide script not found in window.");
            }
        } catch (e) {
            error.value = e.message;
            isLoading.value = false;
            console.error("Failed to load Pyodide:", e);
        }
    };

    const runCode = async (code: string, testCases: any[] = [], functionName: string = "") => {
        if (!pyodide.value) return { success: false, error: "Pyodide not initialized" };

        stdout.value = '';
        try {
            // 1. Run user code
            await pyodide.value.runPythonAsync(code);

            // 2. Run test cases if provided
            if (testCases.length > 0 && functionName) {
                for (const test of testCases) {
                    const testCode = `
# Execution within try-except for structured output
try:
    _input_val = ${test.input !== '' ? test.input : 'None'}
    if ${test.input === '' ? 'True' : 'False'}:
        _user_result = ${functionName}()
    else:
        _user_result = ${functionName}(_input_val)
        
    _repr_result = repr(_user_result)
    _is_passed = _repr_result == ${test.expected} or str(_user_result) == ${test.expected}
    print(f"TEST_CASE|{repr(_input_val)}|{_repr_result}|{_is_passed}")
except Exception as e:
    print(f"TEST_CASE|ERROR|ERROR: {str(e)}|False")
`;
                    await pyodide.value.runPythonAsync(testCode);
                }
            }

            return { success: true, output: stdout.value };
        } catch (e: any) {
            return { success: false, error: e.message, output: stdout.value };
        }
    };

    return {
        pyodide,
        isLoading,
        error,
        stdout,
        initPyodide,
        runCode
    };
}
