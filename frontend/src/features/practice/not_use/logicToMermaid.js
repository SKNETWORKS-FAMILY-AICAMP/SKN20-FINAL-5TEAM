/**
 * [수정일: 2026-01-23]
 * [수정내용: Python/Pseudocode를 Mermaid Flowchart 구문으로 변환하는 간단한 파서 구현]
 */

export const convertToMermaid = (code) => {
    if (!code || code.trim() === '') {
        return 'graph TD\n  Start([Neural_Core_Standby])';
    }

    const lines = code.split('\n').map(line => line.trim()).filter(line => line !== '');
    let mermaid = 'graph TD\n';
    mermaid += '  style Start fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#fff\n';
    mermaid += '  Start([Logic_Initiated]) --> Node0\n';

    let nodeCount = 0;
    let lastNode = 'Start';
    const stack = [];

    lines.forEach((line, index) => {
        const currentNode = `Node${index}`;

        // 제어문 감지
        if (line.startsWith('if') || line.endsWith(':') && line.includes('if')) {
            mermaid += `  ${currentNode}{{"${line.replace(':', '')}"}}\n`;
            mermaid += `  style ${currentNode} fill:#1e1b4b,stroke:#818cf8,color:#fff\n`;
            stack.push({ type: 'if', node: currentNode });
        } else if (line.startsWith('for') || line.startsWith('while')) {
            mermaid += `  ${currentNode}(("${line.replace(':', '')}"))\n`;
            mermaid += `  style ${currentNode} fill:#172554,stroke:#3b82f6,color:#fff\n`;
            stack.push({ type: 'loop', node: currentNode });
        } else {
            mermaid += `  ${currentNode}["${line.replace(/"/g, "'") || 'Processing...'}"]\n`;
            mermaid += `  style ${currentNode} fill:#020617,stroke:#1e293b,color:#94a3b8\n`;
        }

        // 연결 (단순화된 순차 연결)
        if (index > 0) {
            const prevNode = `Node${index - 1}`;
            mermaid += `  ${prevNode} --> ${currentNode}\n`;
        } else {
            mermaid += `  Start --> ${currentNode}\n`;
        }

        // 스택 기반 흐름 제어 (매우 단순화된 버전)
        // 실제 파이썬 파싱은 복잡하므로 여기서는 시각적 흐름만 표현
    });

    return mermaid;
};
