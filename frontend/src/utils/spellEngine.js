/**
 * [수정일: 2026-01-23]
 * [수정내용: 브라우저 내 Python 실행기 Pyodide를 활용한 정밀 평가 엔진(SpellEngine) 구현]
 */

class SpellEngine {
    constructor() {
        this.pyodide = null;
        this.isLoading = false;
        this.isReady = false;
    }

    /**
     * Pyodide 초기화 및 로드
     */
    async init() {
        if (this.isReady || this.isLoading) return;

        this.isLoading = true;
        try {
            // CDN을 통해 Pyodide 로드
            if (!window.loadPyodide) {
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js';
                document.head.appendChild(script);

                await new Promise((resolve) => {
                    script.onload = resolve;
                });
            }

            this.pyodide = await window.loadPyodide();

            // 기본 모킹(Mocking) 환경 구축
            await this.pyodide.runPythonAsync(`
import sys
import io

class GameEnvironment:
    def __init__(self):
        this.logs = []
    
    def log(self, value):
        this.logs.append(str(value))
    
    def clear(self):
        this.logs = []

env = GameEnvironment()

def prepare_brush(): env.log("prepared")
def brush_teeth(): env.log("brushed")
def rinse_mouth(): env.log("rinsed")
def cross_walk(): env.log("crossing")
def wait(): env.log("waiting")
def run_lap(): env.log("running")
def check_light(): return _current_input if '_current_input' in globals() else 'red'
      `);

            this.isReady = true;
            console.log("SpellEngine: Pyodide is ready.");
        } catch (error) {
            console.error("SpellEngine Initialization Failed:", error);
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * 사용자 코드 실행 및 테스트 케이스 검증
     */
    async evaluate(code, testCases = []) {
        if (!this.isReady) await this.init();

        const results = [];
        let allPassed = true;

        for (const testCase of testCases) {
            try {
                // 입력값 주입
                if (testCase.input) {
                    await this.pyodide.runPythonAsync(`_current_input = '${testCase.input}'`);
                }

                // 로그 초기화
                await this.pyodide.runPythonAsync(`env.clear()`);

                // 코드 실행
                await this.pyodide.runPythonAsync(code);

                // 결과 로그 획득
                const logs = await this.pyodide.runPythonAsync(`"\\n".join(env.logs)`);

                const isMatch = logs.trim() === testCase.expected_output.trim();
                if (!isMatch) allPassed = false;

                results.push({
                    input: testCase.input,
                    expected: testCase.expected_output,
                    actual: logs,
                    passed: isMatch
                });
            } catch (error) {
                allPassed = false;
                results.push({
                    input: testCase.input,
                    error: error.message,
                    passed: false
                });
            }
        }

        return {
            success: allPassed,
            testResults: results,
            score: this.calculateScore(results)
        };
    }

    calculateScore(results) {
        if (results.length === 0) return 0;
        const passedCount = results.filter(r => r.passed).length;
        return Math.floor((passedCount / results.length) * 100);
    }
}

export const spellEngine = new SpellEngine();
