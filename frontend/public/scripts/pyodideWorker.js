// [수정일: 2026-01-31] 브라우저 내 실제 파이썬 코드 실행을 위한 Pyodide Worker
importScripts("https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js");

let pyodide = null;

async function initPyodide() {
    if (!pyodide) {
        pyodide = await loadPyodide();
    }
}

self.onmessage = async (event) => {
    const { code, data } = event.data;

    try {
        await initPyodide();

        // 데이터 주입 (news_list 등)
        pyodide.globals.set("target_data", data);

        // stdout 캡처를 위한 리다이렉션
        await pyodide.runPythonAsync(`
import sys
import io
sys.stdout = io.StringIO()
        `);

        // 사용자 코드 실행
        await pyodide.runPythonAsync(code);

        // 실행 결과 캡처
        const stdout = await pyodide.runPythonAsync("sys.stdout.getvalue()");

        self.postMessage({
            success: true,
            output: stdout || "코드 실행 완료 (출력값 없음)",
        });
    } catch (error) {
        self.postMessage({
            success: false,
            error: error.message,
        });
    }
};
