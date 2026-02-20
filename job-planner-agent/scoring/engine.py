# scoring/engine.py
"""
스킬 매칭 엔진
원본 v3.1 섹션 4 기반
"""
import config
from agent.models import UserProfile, JobPosting

class ScoringEngine:
    def __init__(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                 match_threshold: float = config.SKILL_MATCH_THRESHOLD):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self.threshold = match_threshold

    def compute_skill_match(self, user_skills: list[str], required_skills: list[str]) -> dict:
        if not required_skills or not user_skills:
            return {"matches": [], "overall_score": 0.0 if required_skills else 1.0}

        user_emb = self.model.encode(user_skills, normalize_embeddings=True)
        req_emb = self.model.encode(required_skills, normalize_embeddings=True)
        sim_matrix = user_emb @ req_emb.T

        matches = []
        for i, req in enumerate(required_skills):
            best_idx = sim_matrix[:, i].argmax()
            best_score = float(sim_matrix[best_idx, i])
            matches.append({
                "required_skill": req,
                "best_match": user_skills[best_idx],
                "similarity": round(best_score, 3),
                "matched": best_score >= self.threshold
            })

        matched_count = sum(1 for m in matches if m["matched"])
        return {
            "matches": matches,
            "overall_score": round(matched_count / len(required_skills), 3),
            "matched_count": matched_count,
            "total_required": len(required_skills)
        }

    def compute_skill_gap(self, user: UserProfile, job: JobPosting) -> float:
        req_score = self.compute_skill_match(user.skills, job.required_skills)["overall_score"]
        pref_score = self.compute_skill_match(user.skills, job.preferred_skills)["overall_score"] \
            if job.preferred_skills else 1.0
        exp_score = self._experience_fit(user.experience_years, job.experience_range)
        return round(1.0 - (req_score*0.6 + pref_score*0.2 + exp_score*0.2), 3)

    def compute_readiness(self, user: UserProfile, job: JobPosting) -> float:
        gap = self.compute_skill_gap(user, job)
        fit = 1.0 - gap
        match = self.compute_skill_match(user.skills, job.required_skills)
        matched = [m["best_match"] for m in match["matches"] if m["matched"]]
        prof = (sum(user.skill_levels.get(s,2) for s in matched) / len(matched) / 5.0) if matched else 0.0
        exp = self._experience_fit(user.experience_years, job.experience_range)
        return round(max(0.0, min(1.0, fit*0.5 + prof*0.3 + exp*0.2)), 3)

    def generate_match_report(self, user, job) -> dict:
        req_match = self.compute_skill_match(user.skills, job.required_skills)
        return {
            "skill_gap_score": self.compute_skill_gap(user, job),
            "readiness_score": self.compute_readiness(user, job),
            "matched": [m for m in req_match["matches"] if m["matched"]],
            "missing": [m for m in req_match["matches"] if not m["matched"]],
            "experience_fit": self._experience_fit(user.experience_years, job.experience_range)
        }

    def _experience_fit(self, years, req_range) -> float:
        import re
        nums = re.findall(r'\d+', req_range)
        if not nums: return 0.7
        lo, hi = int(nums[0]), int(nums[-1]) if len(nums)>1 else int(nums[0])+2
        if lo <= years <= hi: return 1.0
        elif years < lo: return max(0.0, years/lo)
        else: return max(0.7, 1.0 - (years-hi)*0.05)
