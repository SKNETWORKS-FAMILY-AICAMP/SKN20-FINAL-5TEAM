"""
의사코드 Rule 기반 검증 엔진
수정일: 2026-02-19

[변경 사항]
- check_low_effort 제거 → LowEffortDetector로 통합 (low_effort_detector.py 참조)
  이 클래스는 더 이상 무성의 입력 판단을 하지 않습니다.
- validate() 반환값에서 is_low_effort 필드 제거
- 역할: 치명적 오류 감지 + 개념/구조 점수 산출만 담당
"""

import re
from typing import Set, List, Dict, Any


class PseudocodeValidator:
    """
    Rule 기반 의사코드 검증기.
    무성의 입력 감지는 LowEffortDetector에서 처리하므로 여기선 하지 않습니다.
    """

    def __init__(self, rules: Dict[str, Any]):
        self.rules = rules or self._default_rules()

    def validate(self, pseudocode: str) -> Dict[str, Any]:
        normalized = self._normalize(pseudocode)
        soft = self._soft_normalize(pseudocode)

        critical_errors = self._check_critical_errors(normalized)
        concepts = self._extract_concepts(soft)
        structure = self._analyze_structure(pseudocode, soft, concepts)

        return {
            'passed': len(critical_errors) == 0,
            'score': structure['score'],
            'criticalErrors': critical_errors,
            'warnings': structure['warnings'],
            'details': {
                'concepts': list(concepts),
                'structure': structure['feedback'],
                'flow': structure['flow'],
            },
        }

    # ── 정규화 ────────────────────────────────────────────────────

    def _normalize(self, text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^a-z0-9가-힣\s\.\,\(\)\_\-\:\;\=\>\<\!\?\/]', ' ', text)
        return text.strip()

    def _soft_normalize(self, text: str) -> str:
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.lower()).strip()

    # ── 치명적 오류 체크 ──────────────────────────────────────────

    def _check_critical_errors(self, normalized: str) -> List[Dict[str, Any]]:
        errors = []
        for p in self.rules.get('criticalPatterns', []):
            if p.get('severity') in ('PRAISE', 'INFO'):
                continue

            pattern = p.get('pattern')
            is_error = False

            if isinstance(pattern, str):
                if re.search(pattern, normalized, re.IGNORECASE):
                    is_error = True
            elif isinstance(pattern, dict):
                positive = pattern.get('positive')
                negatives = pattern.get('negatives', [])
                if positive and re.search(positive, normalized, re.IGNORECASE):
                    has_neg = any(re.search(n, normalized, re.IGNORECASE) for n in negatives)
                    if not has_neg:
                        is_error = True

            if is_error:
                errors.append({
                    'severity': p.get('severity', 'CRITICAL'),
                    'message': p.get('message'),
                    'example': p.get('correctExample'),
                    'why': p.get('explanation'),
                })
        return errors

    # ── 개념 추출 ────────────────────────────────────────────────

    def _extract_concepts(self, soft: str) -> Set[str]:
        found: Set[str] = set()
        for concept in self.rules.get('requiredConcepts', []):
            for pattern in concept.get('patterns', []):
                if re.search(pattern, soft, re.IGNORECASE):
                    found.add(concept['id'])
                    break
        return found

    # ── 구조 분석 ────────────────────────────────────────────────

    def _analyze_structure(
        self, raw: str, soft: str, found_concepts: Set[str]
    ) -> Dict[str, Any]:
        lines = [l.strip() for l in raw.split('\n') if l.strip()]
        scoring = self.rules.get('scoring', {'structure': 20, 'concepts': 40, 'flow': 40})
        rec = self.rules.get('recommendations', {})
        feedback: List[str] = []
        warnings: List[str] = []
        score = 0.0

        # 1. 기본 구조 (길이 + 번호)
        min_lines = rec.get('minLines', 3)
        max_lines = rec.get('maxLines', 20)
        if min_lines <= len(lines) <= max_lines:
            score += scoring['structure'] / 2
            feedback.append('✅ 적절한 길이')
        else:
            feedback.append(f"⚠️ {'너무 짧음' if len(lines) < min_lines else '너무 김'}")

        if any(re.match(r'^\d+[\.\):]', l) for l in lines):
            score += scoring['structure'] / 2
            feedback.append('✅ 번호 매기기 사용')

        # 2. 핵심 개념
        required = self.rules.get('requiredConcepts', [])
        if required:
            total_w = sum(c.get('weight', 1) for c in required)
            found_w = sum(c.get('weight', 1) for c in required if c['id'] in found_concepts)
            score += (found_w / total_w * scoring['concepts']) if total_w else scoring['concepts']

            missing = [c['name'] for c in required if c['id'] not in found_concepts]
            if not missing:
                feedback.append('✅ 모든 핵심 개념 포함')
            else:
                feedback.append(f"⚠️ 누락된 개념: {', '.join(missing)}")
                warnings.append(f"💡 누락된 개념을 추가해 보세요: {', '.join(missing)}")

        # 3. 논리적 흐름
        flow = self._analyze_flow(soft, scoring['flow'])
        score += flow['score']
        feedback.extend(flow['feedback'])

        return {
            'score': round(score),
            'feedback': feedback,
            'warnings': warnings,
            'flow': flow,
        }

    def _analyze_flow(self, soft: str, max_score: float) -> Dict[str, Any]:
        lines = soft.split('\n')
        deps = self.rules.get('dependencies', [])
        if not deps:
            return {'score': max_score, 'feedback': []}

        total_pts = sum(d.get('points', 0) for d in deps)
        if total_pts == 0:
            return {'score': max_score, 'feedback': []}

        score = 0.0
        feedback: List[str] = []
        for dep in deps:
            before = self._find_concept_line(lines, dep['before'])
            after = self._find_concept_line(lines, dep['after'])
            if before == -1 or after == -1:
                continue
            pts = dep.get('points', 0)
            if before < after:
                score += (pts / total_pts) * max_score
                feedback.append(f"✅ {dep.get('name', '순서')} 정확")
            elif dep.get('strictness') == 'REQUIRED':
                feedback.append(f"❌ {dep.get('name', '순서')}: 순서 오류 (필수)")
            else:
                score += (pts / 2 / total_pts) * max_score
                feedback.append(f"⚠️ {dep.get('name', '순서')}: 순서 권장됨")

        return {'score': round(score), 'feedback': feedback}

    def _find_concept_line(self, lines: List[str], concept_id: str) -> int:
        concept = next(
            (c for c in self.rules.get('requiredConcepts', []) if c['id'] == concept_id),
            None,
        )
        if not concept:
            return -1
        for i, line in enumerate(lines):
            for p in concept.get('patterns', []):
                if re.search(p, line, re.IGNORECASE):
                    return i
        return -1

    def _default_rules(self) -> Dict[str, Any]:
        return {
            'criticalPatterns': [],
            'requiredConcepts': [],
            'dependencies': [],
            'scoring': {'structure': 20, 'concepts': 40, 'flow': 40},
        }
