"""
의사코드 로컬 검증 엔진
수정일: 2026-02-18
수정내용: 엔트로피 및 키워드 매칭 기반 무성의 입력(Low Effort) 감지 로직 추가 (프론트엔드 연동용)
"""
import re
import math
from collections import Counter

class PseudocodeValidator:
    def __init__(self, rules):
        self.rules = rules or self.get_default_rules()

    def validate(self, pseudocode):
        normalized = self.normalize(pseudocode)
        soft_normalized = self.soft_normalize(pseudocode)
        
        is_low_effort, low_effort_reason = self.check_low_effort(pseudocode)
        critical_errors = self.check_critical_errors(normalized)
        concepts = self.extract_concepts(soft_normalized)
        structure_results = self.analyze_structure(pseudocode, soft_normalized, concepts)
        
        return {
            'passed': len(critical_errors) == 0 and not is_low_effort,
            'score': 0 if is_low_effort else structure_results['score'],
            'is_low_effort': is_low_effort,
            'low_effort_reason': low_effort_reason,
            'criticalErrors': critical_errors,
            'warnings': structure_results['warnings'],
            'details': {
                'concepts': list(concepts),
                'structure': structure_results['feedback'],
                'flow': structure_results['flow']
            }
        }

    def check_low_effort(self, text: str):
        """성의 없는 입력인지 검증 (프론트엔드 동기화 및 강화)"""
        if not text or len(text.strip()) < 10:
            return True, "분석을 시작하기엔 설계 내용이 너무 짧습니다."
        
        # 1. 포기성/무의미 키워드
        giveup_keywords = [
            r'모르', r'몰라', r'몰겠', r'어렵', r'못하', r'안됨', r'해줘', r'\?', r'help',
            r'글쎄', r'나중에', r'다음에', r'귀찮', r'패스', r'pass', r'ㅁㄴㅇㄹ', r'ㄴㄴ'
        ]
        if any(re.search(kw, text) for kw in giveup_keywords):
            return True, "설계를 포기하시거나 질문을 하셨군요. 이 단계는 당신의 '설계안'을 제출하는 곳입니다."
            
        # 2. 엔트로피 검사 (무의미한 반복 문자열 aaaaa... 등)
        clean_text = "".join([c for c in text if c.isalnum()])
        if len(clean_text) > 5:
            counter = Counter(clean_text)
            probs = [count / len(clean_text) for count in counter.values()]
            entropy = -sum(p * math.log2(p) for p in probs)
            if entropy < 2.0:
                return True, "의미를 알 수 없는 단어의 나열이 감지되었습니다."
        
        return False, None
    def normalize(self, text):
        if not text: return ""
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        # Keep essential characters for pseudocode
        text = re.sub(r'[^a-z0-9가-힣\s\.\,\(\)\_\-\:\;\=\>\<\!\?\/]', ' ', text)
        return text.strip()

    def soft_normalize(self, text):
        if not text: return ""
        return re.sub(r'\s+', ' ', text.lower()).strip()

    def check_critical_errors(self, normalized):
        errors = []
        critical_patterns = self.rules.get('criticalPatterns', [])
        
        for pattern_def in critical_patterns:
            if pattern_def.get('severity') in ['PRAISE', 'INFO']:
                continue
                
            pattern = pattern_def.get('pattern')
            is_error = False
            
            if isinstance(pattern, str): # Simple string or regex string
                if re.search(pattern, normalized, re.IGNORECASE):
                    is_error = True
            elif isinstance(pattern, dict):
                positive = pattern.get('positive')
                negatives = pattern.get('negatives', [])
                
                # In Python, we can pass regex objects or strings
                if positive:
                    if re.search(positive, normalized, re.IGNORECASE):
                        has_negative = any(re.search(neg, normalized, re.IGNORECASE) for neg in negatives)
                        if not has_negative:
                            is_error = True
            
            if is_error:
                errors.append({
                    'severity': pattern_def.get('severity', 'CRITICAL'),
                    'message': pattern_def.get('message'),
                    'example': pattern_def.get('correctExample'),
                    'why': pattern_def.get('explanation')
                })
        return errors

    def extract_concepts(self, soft_normalized):
        found_concepts = set()
        required_concepts = self.rules.get('requiredConcepts', [])
        
        for concept in required_concepts:
            patterns = concept.get('patterns', [])
            for pattern in patterns:
                if re.search(pattern, soft_normalized, re.IGNORECASE):
                    found_concepts.add(concept['id'])
                    break
        return found_concepts

    def analyze_structure(self, raw_pseudocode, soft_normalized, found_concepts):
        lines = [l.strip() for l in raw_pseudocode.split('\n') if l.strip()]
        scoring = self.rules.get('scoring', {'structure': 20, 'concepts': 40, 'flow': 40})
        
        feedback = []
        warnings = []
        score = 0
        
        # 1. Basic Structure (Lines, Numbering)
        rec = self.rules.get('recommendations', {})
        min_lines = rec.get('minLines', 3)
        max_lines = rec.get('maxLines', 20)
        
        if min_lines <= len(lines) <= max_lines:
            score += scoring['structure'] / 2
            feedback.append('✅ 적절한 길이')
        else:
            feedback.append(f"⚠️ {'너무 짧음' if len(lines) < min_lines else '너무 김'}")
            
        has_numbering = any(re.match(r'^\d+[\.\):]', l) for l in lines)
        if has_numbering:
            score += scoring['structure'] / 2
            feedback.append('✅ 번호 매기기 사용')
        
        # 2. Concepts
        required_concepts = self.rules.get('requiredConcepts', [])
        if required_concepts:
            total_weight = sum(c.get('weight', 1) for c in required_concepts)
            found_weight = sum(c.get('weight', 1) for c in required_concepts if c['id'] in found_concepts)
            
            concept_score = (found_weight / total_weight) * scoring['concepts'] if total_weight > 0 else scoring['concepts']
            score += concept_score
            
            missing = [c['name'] for c in required_concepts if c['id'] not in found_concepts]
            if not missing:
                feedback.append('✅ 모든 핵심 개념 포함')
            else:
                feedback.append(f"⚠️ 누락된 개념: {', '.join(missing)}")
                warnings.append(f"💡 누락된 개념을 추가해 보세요: {', '.join(missing)}")
        
        # 3. Flow
        flow_results = self.analyze_flow(soft_normalized, scoring['flow'])
        score += flow_results['score']
        feedback.extend(flow_results['feedback'])
        
        return {
            'score': round(score),
            'feedback': feedback,
            'warnings': warnings,
            'flow': flow_results
        }

    def analyze_flow(self, soft_normalized, max_score):
        lines = soft_normalized.split('\n')
        score = 0
        feedback = []
        
        dependencies = self.rules.get('dependencies', [])
        if not dependencies:
            return {'score': max_score, 'feedback': []}
            
        total_points = sum(d.get('points', 0) for d in dependencies)
        if total_points == 0:
            return {'score': max_score, 'feedback': []}
            
        for dep in dependencies:
            before_idx = self.find_concept_line(lines, dep['before'])
            after_idx = self.find_concept_line(lines, dep['after'])
            
            if before_idx != -1 and after_idx != -1:
                if before_idx < after_idx:
                    score += (dep.get('points', 0) / total_points) * max_score
                    feedback.append(f"✅ {dep.get('name', '순서')} 정확")
                else:
                    if dep.get('strictness') == 'REQUIRED':
                        feedback.append(f"❌ {dep.get('name', '순서')}: 순서 오류 (필수)")
                    else:
                        feedback.append(f"⚠️ {dep.get('name', '순서')}: 순서 권장됨")
                        score += ((dep.get('points', 0) / 2) / total_points) * max_score
                        
        return {'score': round(score), 'feedback': feedback}

    def find_concept_line(self, lines, concept_id):
        required_concepts = self.rules.get('requiredConcepts', [])
        concept = next((c for c in required_concepts if c['id'] == concept_id), None)
        if not concept: return -1
        
        patterns = concept.get('patterns', [])
        for i, line in enumerate(lines):
            for p in patterns:
                if re.search(p, line, re.IGNORECASE):
                    return i
        return -1

    def get_default_rules(self):
        return {
            'criticalPatterns': [],
            'requiredConcepts': [],
            'dependencies': [],
            'scoring': {'structure': 20, 'concepts': 40, 'flow': 40}
        }
