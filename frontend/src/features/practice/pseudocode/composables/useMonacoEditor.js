// Monaco Editor용 헬퍼 파일 (성능 최적화 & 무한루프 방지 버전)
import { ref, watch, onBeforeUnmount } from 'vue';

export function useMonacoEditor(currentMission, editorState) {
    // [최적화] Monaco 인스턴스 및 데코레이션은 Vue 반응형 시스템(ref)에 넣지 않음
    let monacoEditorRaw = null;
    let decorationsCollection = null;
    let stateUpdateTimer = null;
    let decorationTimer = null;

    const monacoOptions = {
        automaticLayout: true, // [2026-02-12] 필수: 멈춤 및 입력 불가 현상 방지
        /* [수정 2026-02-14] VS Code 스타일 가독성 최적화 */
        fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace",
        fontSize: 15,
        lineHeight: 1.6,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        wordWrap: 'on',
        lineNumbers: 'on',
        glyphMargin: true,
        folding: true,
        lineDecorationsWidth: 10,
        lineNumbersMinChars: 3,
        renderLineHighlight: 'all',
        scrollbar: {
            vertical: 'visible',
            horizontal: 'visible'
        },
        dragAndDrop: false,
        dropIntoEditor: { enabled: false },
        readOnly: false,
        contextmenu: true
    };

    // 네모 박스 (TODO 하이라이트) 업데이트 함수
    const updateDecorations = () => {
        if (!monacoEditorRaw) return;
        if (decorationTimer) clearTimeout(decorationTimer);

        decorationTimer = setTimeout(() => {
            const model = monacoEditorRaw.getModel();
            if (!model) return;

            const matches = model.findMatches('#\\s*TODO', false, true, false, null, true);
            const newDecorations = (matches || []).map(match => ({
                range: match.range,
                options: {
                    isWholeLine: true,
                    className: 'todo-highlight',
                    glyphMarginClassName: 'todo-glyph'
                }
            }));

            if (decorationsCollection) {
                decorationsCollection.clear();
            }
            decorationsCollection = monacoEditorRaw.createDecorationsCollection(newDecorations);
        }, 1000);
    };

    // 코드 삽입 함수
    const insertCodeSnippet = (code) => {
        if (!monacoEditorRaw) return;
        const currentCode = editorState.userCode || "";

        const todoLineRegex = /^(\s*)#\s*todo.*$/mi;
        const match = currentCode.match(todoLineRegex);

        if (match) {
            const fullMatch = match[0];
            const indent = match[1] || "";
            const indentedCode = code.split('\n').map(line => indent + line).join('\n');
            const newTotalCode = currentCode.replace(fullMatch, indentedCode);
            editorState.userCode = newTotalCode;
            monacoEditorRaw.setValue(newTotalCode); // 즉시 적용
        } else {
            const newTotalCode = currentCode + "\n" + code;
            editorState.userCode = newTotalCode;
            monacoEditorRaw.setValue(newTotalCode);
        }
    };

    // 에디터 마운트 시 설정
    const handleMonacoMount = (editor) => {
        console.log("[Monaco] Mounted successfully");
        monacoEditorRaw = editor;

        // 드롭 이벤트 (순수 DOM 방식 유지)
        const domNode = editor.getDomNode();
        if (domNode) {
            domNode.addEventListener('dragover', (e) => e.preventDefault());
            domNode.addEventListener('drop', (e) => {
                const code = e.dataTransfer.getData('text/plain');
                if (code) {
                    e.preventDefault();
                    insertCodeSnippet(code);
                }
            });
        }

        // 초기값 결정 (undefined/null 체크)
        const currentVal = editorState.userCode;
        const templateVal = currentMission.value?.implementation?.codeFrame?.template || "";

        const finalInitialValue = (currentVal !== undefined && currentVal !== null) ? currentVal : templateVal;

        editor.setValue(finalInitialValue);
        if (editorState.userCode === undefined || editorState.userCode === null) {
            editorState.userCode = finalInitialValue;
        }

        // 내용 변경 감지 (300ms 디바운스)
        editor.onDidChangeModelContent(() => {
            if (stateUpdateTimer) clearTimeout(stateUpdateTimer);

            stateUpdateTimer = setTimeout(() => {
                const editorValue = editor.getValue();
                // [2026-02-12] 상태값과 에디터값이 다를 때만 업데이트 (루프 차단)
                if (editorState.userCode !== editorValue) {
                    editorState.userCode = editorValue;
                }
                updateDecorations();
            }, 300);
        });

        updateDecorations();
        editor.focus(); // 마운트 시 포커스
    };

    // 언마운트 시 정리
    onBeforeUnmount(() => {
        if (stateUpdateTimer) clearTimeout(stateUpdateTimer);
        if (decorationTimer) clearTimeout(decorationTimer);
    });

    // 스테이지 변경 시 템플릿 리로드
    watch(() => currentMission.value?.id, (newId) => {
        if (newId && monacoEditorRaw) {
            const template = currentMission.value?.implementation?.codeFrame?.template || "";
            editorState.userCode = template;
            monacoEditorRaw.setValue(template);
            setTimeout(() => monacoEditorRaw.layout(), 100);
        }
    });

    // [CRITICAL FIX] 외부 상태 변화 동기화 (포커스 없을 때만)
    watch(() => editorState.userCode, (newCode) => {
        if (!monacoEditorRaw) return;

        const normalize = (s) => (s || "").replace(/\r\n/g, '\n');
        const normalizedNew = normalize(newCode);
        const normalizedOld = normalize(monacoEditorRaw.getValue());

        if (normalizedNew !== normalizedOld) {
            // 사용자가 입력 중이 아닐 때만 setValue (커서 튐 방지)
            if (!monacoEditorRaw.hasTextFocus()) {
                monacoEditorRaw.setValue(newCode || "");
            }
        }
    }, { immediate: false });

    return {
        monacoOptions,
        handleMonacoMount,
        insertCodeSnippet
    };
}
