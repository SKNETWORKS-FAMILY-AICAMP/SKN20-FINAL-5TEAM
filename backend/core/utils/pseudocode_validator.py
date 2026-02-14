import re
import math

class PseudocodeValidator:
    def __init__(self, rules):
        self.rules = rules or self.get_default_rules()

    def validate(self, pseudocode):
        normalized = self.normalize(pseudocode)
        soft_normalized = self.soft_normalize(pseudocode)
        
        critical_errors = self.check_critical_errors(normalized)
        concepts = self.extract_concepts(soft_normalized)
        structure_results = self.analyze_structure(pseudocode, soft_normalized, concepts)
        
        return {
            'passed': len(critical_errors) == 0,
            'score': structure_results['score'],
            'criticalErrors': critical_errors,
            'warnings': structure_results['warnings'],
            'details': {
                'concepts': list(concepts),
                'structure': structure_results['feedback'],
                'flow': structure_results['flow']
            }
        }

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
