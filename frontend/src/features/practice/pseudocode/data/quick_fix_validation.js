/**
 * Quick Fix Script for stages.js
 * validation 필드를 자동으로 교체합니다
 * 
 * 사용법:
 * cd frontend/src/features/practice/pseudocode/data
 * node quick_fix_validation.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const stagesPath = path.join(__dirname, 'stages.js');
const backupPath = path.join(__dirname, 'stages.js.backup');

console.log('🔧 stages.js validation 필드 자동 교체 시작...\n');

// 1. 백업 생성
try {
  const content = fs.readFileSync(stagesPath, 'utf-8');
  fs.writeFileSync(backupPath, content, 'utf-8');
  console.log('✅ 백업 생성: stages.js.backup');
} catch (err) {
  console.error('❌ 백업 실패:', err.message);
  process.exit(1);
}

// 2. 파일 읽기
let content;
try {
  content = fs.readFileSync(stagesPath, 'utf-8');
} catch (err) {
  console.error('❌ 파일 읽기 실패:', err.message);
  process.exit(1);
}

// 3. validation 블록 찾기 및 교체
// validation: { ... } 형태의 블록을 찾습니다
// 중괄호가 매칭될 때까지 계속 진행

function findValidationBlock(text) {
  const startPattern = /validation:\s*\{/;
  const match = text.match(startPattern);
  
  if (!match) {
    return null;
  }
  
  const startIndex = match.index;
  let braceCount = 1;
  let currentIndex = startIndex + match[0].length;
  
  // 중괄호 매칭
  while (braceCount > 0 && currentIndex < text.length) {
    const char = text[currentIndex];
    if (char === '{') braceCount++;
    if (char === '}') braceCount--;
    currentIndex++;
  }
  
  // 뒤의 쉼표까지 포함
  if (text[currentIndex] === ',') {
    currentIndex++;
  }
  
  return {
    start: startIndex,
    end: currentIndex,
    text: text.substring(startIndex, currentIndex)
  };
}

const validationBlock = findValidationBlock(content);

if (!validationBlock) {
  console.log('⚠️ validation 블록을 찾을 수 없습니다.');
  console.log('이미 교체되었거나 파일 형식이 다릅니다.');
  process.exit(0);
}

console.log(`\n📍 validation 블록 발견:`);
console.log(`   위치: ${validationBlock.start} ~ ${validationBlock.end}`);
console.log(`   크기: ${validationBlock.text.length}자`);

// 4. 교체
const replacement = `validation: VALIDATION_LIBRARY.data_leakage,
        codeValidation: CODE_VALIDATION_LIBRARY.data_leakage,`;

const newContent = 
  content.substring(0, validationBlock.start) + 
  replacement + 
  content.substring(validationBlock.end);

// 5. 저장
try {
  fs.writeFileSync(stagesPath, newContent, 'utf-8');
  console.log('\n✅ 교체 완료!');
  console.log(`   이전: ${validationBlock.text.length}자`);
  console.log(`   이후: ${replacement.length}자`);
  console.log(`   절약: ${validationBlock.text.length - replacement.length}자`);
} catch (err) {
  console.error('\n❌ 저장 실패:', err.message);
  console.log('백업에서 복구 중...');
  fs.copyFileSync(backupPath, stagesPath);
  process.exit(1);
}

console.log('\n🎉 작업 완료!');
console.log('\n다음 단계:');
console.log('  1. npm run dev 실행');
console.log('  2. 브라우저에서 Mission 1 테스트');
console.log('  3. 문제 발생 시: copy stages.js.backup stages.js\n');
