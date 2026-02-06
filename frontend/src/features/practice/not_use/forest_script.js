// script.js

// --- 게임 상태 관리 변수 ---
let currentStageIndex = 0;
let totalScore = 0;

// --- DOM 요소 참조 ---
const scoreDisplay = document.getElementById('score-display');
const stageDisplay = document.getElementById('stage-display');
const characterImg = document.getElementById('character-img');
const speakerName = document.getElementById('speaker-name');
const dialogueText = document.getElementById('dialogue-text');
const questDesc = document.getElementById('quest-desc');
const ioInput = document.getElementById('io-input');
const ioOutput = document.getElementById('io-output');
const codeInput = document.getElementById('code-input');
const submitBtn = document.getElementById('submit-btn');
const nextBtn = document.getElementById('next-btn');

// 모달 관련 요소
const feedbackModal = document.getElementById('feedback-modal');
const feedbackTitle = document.getElementById('feedback-title');
const feedbackBody = document.getElementById('feedback-body');
const closeFeedbackBtn = document.getElementById('close-feedback-btn');


// --- 게임 초기화 및 스테이지 로드 함수 ---

function initGame() {
    // 전체 스테이지 수 표시 업데이트
    document.querySelector('#status-bar .status-item:nth-child(2)').innerHTML = `📅 Stage: <span id="stage-display">1</span> / ${gameData.length}`;
    loadStage(currentStageIndex);
}

function loadStage(index) {
    if (index >= gameData.length) {
        alert("축하합니다! 모든 스테이지를 클리어했습니다!");
        return;
    }

    const stage = gameData[index];

    // UI 업데이트
    stageDisplay.textContent = stage.stageId;
    scoreDisplay.textContent = totalScore;

    characterImg.src = stage.character.image;
    speakerName.textContent = stage.character.name;
    dialogueText.textContent = stage.dialogue;

    questDesc.innerHTML = stage.quest.description; // HTML 태그 허용 (강조 등을 위해)
    ioInput.textContent = stage.quest.inputExample;
    ioOutput.textContent = stage.quest.outputExample;

    // 입력창 및 버튼 초기화
    codeInput.value = "";
    nextBtn.style.display = "none";
    submitBtn.disabled = false;
}


// --- 이벤트 핸들러 함수 ---

// 1. 제출 버튼 클릭 시
submitBtn.addEventListener('click', () => {
    const userCode = codeInput.value.trim();
    if (userCode === "") {
        showFeedback(false, "규칙을 작성해주세요!");
        return;
    }

    const currentStage = gameData[currentStageIndex];
    const result = currentStage.validator(userCode);

    if (result.success) {
        // 정답 처리
        totalScore += currentStage.scoreReward;
        scoreDisplay.textContent = totalScore;
        showFeedback(true, result.message + `<br><br>추가 점수: +${currentStage.scoreReward}점!`);
        submitBtn.disabled = true; // 중복 제출 방지
        nextBtn.style.display = "block"; // 다음 스테이지 버튼 표시
    } else {
        // 오답 처리
        showFeedback(false, result.message);
    }
});

// 2. 다음 스테이지 버튼 클릭 시
nextBtn.addEventListener('click', () => {
    currentStageIndex++;
    loadStage(currentStageIndex);
});

// 3. 피드백 모달 닫기 버튼 클릭 시
closeFeedbackBtn.addEventListener('click', () => {
    feedbackModal.classList.add('hidden');
});


// --- 유틸리티 함수 ---
function showFeedback(isSuccess, message) {
    feedbackTitle.textContent = isSuccess ? "성공! 🎉" : "다시 시도해보세요 🤔";
    feedbackBody.innerHTML = message; // HTML 태그 허용

    feedbackBody.className = isSuccess ? 'success-text' : 'fail-text';

    feedbackModal.classList.remove('hidden');
}


// --- 게임 시작 ---
// 모든 리소스가 로드된 후 게임 초기화
window.addEventListener('DOMContentLoaded', initGame);