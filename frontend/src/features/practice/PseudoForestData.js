/**
 * Pseudo Forest 7 Stages x 3 Steps Data Design
 * 
 * [수정일: 2026-01-28]
 */
const forestGameData = [
    {
        stageId: 1,
        character: { name: "감자쥬 (카피바라)", image: "/image/forest/char_gamjaju.png" },
        dialogue: "뭐~ 되면 됐쥬. 마을 입구 공지판이 너무 복잡해유. 똑같은 글은 한 번만 보이게 정리해주면 고맙겠쥬~",
        steps: [
            {
                type: "subjective",
                question: "1. 중복된 게시글을 어떻게 찾아내고 제거할지 기본적인 아이디어를 말해보세요!",
                evalCriteria: {
                    insightKeywords: ["중복", "제거", "검사", "확인"],
                    structureKeywords: ["비교", "하나씩", "반복"],
                    precisionKeywords: ["삭제", "지우기"]
                }
            },
            {
                type: "objective",
                question: "2. 수만 개의 게시글이 있을 때, 가장 빠르게 중복을 체크할 수 있는 자료구조는 무엇일까요?",
                options: ["배열 (Array)", "집합 (Set)", "연결 리스트 (Linked List)", "스택 (Stack)"],
                correctIndex: 1,
                explanation: "Set은 데이터의 존재 여부를 평균적으로 O(1) 시간에 확인할 수 있어 매우 효율적입니다."
            },
            {
                type: "subjective",
                question: "3. 만약 '글을 쓴 순서'를 그대로 유지하면서 중복만 제거해야 한다면, 로직에 무엇을 추가해야 할까요?",
                evalCriteria: {
                    insightKeywords: ["순서", "유지", "처음"],
                    structureKeywords: ["새로운", "배열", "담기"],
                    precisionKeywords: ["결과", "그대로"]
                }
            }
        ]
    },
    {
        stageId: 2,
        character: { name: "두부 (강아지)", image: "/image/forest/char_dubu.png" },
        dialogue: "이장님, 날씨에 따라 산책 루트가 달라지면 더 편할 것 같아요! 비 오는 날엔 미끄러운 곳을 피하고 싶거든요.",
        steps: [
            {
                type: "subjective",
                question: "1. 맑은 날씨일 때, 단순히 '거리'만 고려하여 최단 경로를 찾는 로직을 어떻게 설계할까요?",
                evalCriteria: {
                    insightKeywords: ["맑음", "거리", "최소"],
                    structureKeywords: ["비교", "가장 짧은"],
                    precisionKeywords: ["결과", "ID"]
                }
            },
            {
                type: "subjective",
                question: "2. 비 오는 날씨에는 '미끄러움' 수치를 1순위로 고려해야 합니다. 어떤 조건문이 추가되어야 할까요?",
                evalCriteria: {
                    insightKeywords: ["비", "미끄러움", "우선"],
                    structureKeywords: ["만약", "if", "조건"],
                    precisionKeywords: ["비교", "최소"]
                }
            },
            {
                type: "objective",
                question: "3. 미끄러움 수치가 동일한 두 경로가 있다면, 최종적으로 무엇을 기준으로 선택해야 할까요?",
                options: ["도착 시간", "경로의 아름다움", "경로의 거리", "주변 상점 수"],
                correctIndex: 2,
                explanation: "1순위 조건이 동일할 때는 거리와 같은 2순위 조건을 통해 결정을 내리는 '타이브레이크' 로직이 필요합니다."
            }
        ]
    }
    // ... 생략 (실제 구현 시 모두 포함)
];
