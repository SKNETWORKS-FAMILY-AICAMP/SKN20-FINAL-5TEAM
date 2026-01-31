import forestGameData from './PseudoForestData.js';

/**
 * [수정일: 2026-01-29]
 * [내용: Pseudo Forest 데이터 정합성 검증 스크립트]
 * - codeSnippet 내 {{ blank }} 개수와 blanks 배열의 길이 일치 여부 확인
 */
function validateForestData() {
    let errorCount = 0;
    const blankRegex = /\{\{\s*blank\s*\}\}/g;

    console.log("\x1b[36m%s\x1b[0m", "=== Pseudo Forest Data Integrity Check ===");

    forestGameData.forEach(stage => {
        stage.steps.forEach((step, stepIdx) => {
            if (step.type === 'python-fill') {
                const snippet = step.codeSnippet || "";
                const matches = snippet.match(blankRegex) || [];
                const blankCount = matches.length;
                const expectedCount = step.blanks ? step.blanks.length : 0;

                if (blankCount !== expectedCount) {
                    errorCount++;
                    console.error(`\x1b[31m[Error] Stage ${stage.stageId} (Resident: ${stage.character.name}), Step ${stepIdx + 1}:\x1b[0m`);
                    console.error(`  - Placeholder count ({{ blank }}): \x1b[33m${blankCount}\x1b[0m`);
                    console.error(`  - Answer array length (blanks): \x1b[33m${expectedCount}\x1b[0m`);
                    console.error(`  - Snippet snippet: \x1b[90m${snippet.replace(/\n/g, '\\n')}\x1b[0m`);
                    console.error(`--------------------------------------------------`);
                }
            }
        });
    });

    if (errorCount === 0) {
        console.log("\x1b[32m%s\x1b[0m", "✅ All python-fill steps are valid! (Data Integrity: 100%)");
    } else {
        console.log("\x1b[31m%s\x1b[0m", `❌ Found ${errorCount} mismatch(es). Please update PseudoForestData.js.`);
        process.exit(1);
    }
}

validateForestData();
