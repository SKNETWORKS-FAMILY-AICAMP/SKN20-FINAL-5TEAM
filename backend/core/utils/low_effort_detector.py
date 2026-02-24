"""
무성의 입력 감지 단일 진입점
작성일: 2026-02-19

기존에 세 군데 흩어져 있던 low_effort 감지 로직을 이 파일 하나로 통합합니다.
- backend/core/services/pseudocode_evaluator.py (surrender_keywords)
- backend/core/utils/pseudocode_validator.py (check_low_effort)
- frontend/src/features/practice/pseudocode/utils/PseudocodeValidator.js (isMeaningfulInput)

프론트엔드는 백엔드 API 응답의 is_low_effort 필드만 신뢰하면 됩니다.
자체 판단 로직은 UX 선피드백(입력 중 경고) 용도로만 최소화해서 사용하세요.
"""

import re
import math
from collections import Counter
from typing import Tuple, Optional


class LowEffortDetector:
    """
    무성의 입력 감지 단일 진입점.
    모든 판단 로직은 여기서만 정의하고, 다른 파일에서는 이 클래스를 import해서 사용합니다.
    """

    # ── 최소 길이 기준 ─────────────────────────────────────────────
    MIN_LENGTH = 15          # 15자 미만 → 무조건 low effort
    MIN_MEANINGFUL_WORDS = 3  # 의미 있는 단어 3개 이상 있어야 통과

    # ── 엔트로피 기준 (aaaaa... 같은 무의미 반복 감지) ──────────────
    MIN_ENTROPY = 2.0

    # ── 포기/무성의 키워드 ────────────────────────────────────────
    # 주의: '모르' 같은 패턴은 "모르는 개념을 정리해서 작성했어요" 같은 문장도 걸릴 수 있음.
    # 단독으로 쓰인 경우만 차단하도록 단어 경계(\b)를 활용.
    GIVEUP_PATTERNS = [
        r'^\s*(모르겠|몰라|모름)\s*$',     # 단독 사용만 차단
        r'^\s*(포기|패스|pass)\s*$',
        r'^\s*(해줘|알려줘|답 알려)\s*$',
        r'귀찮',
        r'나중에 할게',
        r'다음에 할게',
        r'\?{3,}',                        # ??? 이상 (진짜 모르겠다 표현)
        r'^[ㄱ-ㅎㅏ-ㅣ\s]+$',             # 자음/모음만 있는 문장 (ㅁㄴㅇㄹ 등)
    ]

    # ── 자음/모음(자모) 비율 기준 ────────────────────────────────
    # 완성형 한글(가-힣)이 아닌 낱자음/낱모음(ㄱ-ㅎ, ㅏ-ㅣ)의 비율이 30%를 넘으면 무성의 입력
    MAX_JAMO_RATIO = 0.30

    # ── 최소 문장 구조 기준 ──────────────────────────────────────
    # 키워드만 나열(단어 ≤3자 비율 높음, 동사/서술어 없음)하면 설계문이 아님
    MIN_LONG_WORD_COUNT = 2  # 4자 이상 단어가 최소 2개

    # ── 반복 문자 감지 ────────────────────────────────────────────
    # 같은 문자가 5번 이상 연속 반복
    REPETITION_PATTERN = re.compile(r'(.)\1{4,}')

    @classmethod
    def check(cls, text: str) -> Tuple[bool, Optional[str]]:
        """
        무성의 입력 여부를 판단합니다.

        Returns:
            (is_low_effort: bool, reason: Optional[str])
            is_low_effort=False 이면 reason은 None.
        """
        if not text:
            return True, "내용을 입력해 주세요."

        stripped = text.strip()

        # 1. 길이 체크
        if len(stripped) < cls.MIN_LENGTH:
            return True, f"설계가 너무 짧습니다. 최소 {cls.MIN_LENGTH}자 이상 작성해 주세요."

        # 2. 포기/무성의 키워드 체크
        for pattern in cls.GIVEUP_PATTERNS:
            if re.search(pattern, stripped, re.IGNORECASE):
                return True, "설계안을 작성하는 공간입니다. 모르는 부분은 추측이라도 작성해 보세요."

        # 3. 반복 문자 체크 (aaaaaaa...)
        cleaned_for_repetition = re.sub(r'\s', '', stripped)
        if cls.REPETITION_PATTERN.search(cleaned_for_repetition):
            return True, "의미 없는 문자 반복이 감지되었습니다. 정상적인 문장으로 작성해 주세요."

        # 4. 엔트로피 체크 (문자 다양성)
        clean_alnum = "".join(c for c in stripped if c.isalnum())
        if len(clean_alnum) > 5:
            counts = Counter(clean_alnum.lower())
            total = len(clean_alnum)
            probs = [n / total for n in counts.values()]
            entropy = -sum(p * math.log2(p) for p in probs)
            if entropy < cls.MIN_ENTROPY:
                return True, "의미를 알 수 없는 문자의 나열이 감지되었습니다."

        # 5. 자음/모음(낱자) 비율 체크 (ㅇㄴㄹㅂ 등이 섞여 있는 경우)
        jamo_chars = re.findall(r'[ㄱ-ㅎㅏ-ㅣ]', stripped)
        non_space = re.sub(r'\s', '', stripped)
        if non_space and len(jamo_chars) / len(non_space) > cls.MAX_JAMO_RATIO:
            return True, "의미 없는 자음/모음이 다수 포함되어 있습니다. 완성된 문장으로 작성해 주세요."

        # 6. 키워드 나열 감지 (4자 이상 단어가 최소 2개 이상이어야 설계문)
        words = [w for w in stripped.split() if len(w) >= 4]
        if len(words) < cls.MIN_LONG_WORD_COUNT:
            return True, "키워드만 나열되어 있습니다. 설계 절차를 문장으로 서술해 주세요."

        # 7. 의미 있는 단어 수 체크 (한글 없고 짧은 영문 단어만 있는 경우)
        has_korean = bool(re.search(r'[가-힣]', stripped))
        word_count = len([w for w in stripped.split() if len(w) > 1])
        if not has_korean and word_count < cls.MIN_MEANINGFUL_WORDS:
            return True, "자연어 설명이 부족합니다. 설계 의도를 한국어로 함께 작성해 주세요."

        return False, None
