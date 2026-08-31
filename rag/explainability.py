from typing import Dict, Any, List
from rag.skill_normalizer import normalize_skills, normalize_skill
from rag.prerequisites import PrerequisiteGraph

class RecommendationExplainer:
    def __init__(self):
        self.prerequisites = PrerequisiteGraph()

    def explain_why_not_skill(
        self,
        requested_skill: str,
        current_skills: List[str],
        next_target_skill: str
    ) -> Dict[str, Any]:
        req_norm = normalize_skill(requested_skill)
        current_set = set(normalize_skills(current_skills))
        missing_prereqs = [p for p in self.prerequisites.get_prerequisites(req_norm) if p not in current_set]

        if req_norm in current_set:
            return {
                "requested_skill": requested_skill,
                "status": "already_mastered",
                "explanation": f"You have already mastered {requested_skill}. PathAI focuses on building new skills toward your career target."
            }

        if missing_prereqs:
            prereq_str = ", ".join(missing_prereqs)
            return {
                "requested_skill": requested_skill,
                "status": "prerequisite_missing",
                "missing_prerequisites": missing_prereqs,
                "explanation": (
                    f"'{requested_skill.title()}' was not selected as your immediate next step because "
                    f"prerequisite skill(s) [{prereq_str}] are required first. "
                    f"Your current recommended next step is '{next_target_skill.replace('_', ' ').title()}'."
                )
            }

        return {
            "requested_skill": requested_skill,
            "status": "ready",
            "explanation": f"'{requested_skill.title()}' is ready to learn! Prerequisites are fully satisfied."
        }
