from typing import Dict, Any, List, Optional
from rag.skill_normalizer import normalize_skills

LEVEL_ORDER = ["beginner", "conversant", "intermediate", "advanced"]

class LearnerFeedbackEngine:
    def __init__(self):
        pass

    def process_feedback(
        self,
        learner_profile: Dict[str, Any],
        course_completed: bool = False,
        completed_skills: Optional[List[str]] = None,
        feedback_text: Optional[str] = None
    ) -> Dict[str, Any]:
        updated_profile = dict(learner_profile)
        current_skills = set(normalize_skills(updated_profile.get("current_skills", updated_profile.get("skills", []))))

        # 1. Update skills upon completion
        if course_completed and completed_skills:
            new_skills = set(normalize_skills(completed_skills))
            current_skills.update(new_skills)
            updated_profile["current_skills"] = list(current_skills)
            updated_profile["skills"] = list(current_skills)

        # 2. Update learning level on feedback
        if feedback_text:
            fb = feedback_text.strip().lower()
            current_level = updated_profile.get("level", "Intermediate").lower()
            if current_level in LEVEL_ORDER:
                idx = LEVEL_ORDER.index(current_level)
                if "too_easy" in fb or "easy" in fb:
                    new_idx = min(len(LEVEL_ORDER) - 1, idx + 1)
                    updated_profile["level"] = LEVEL_ORDER[new_idx].capitalize()
                elif "too_hard" in fb or "hard" in fb:
                    new_idx = max(0, idx - 1)
                    updated_profile["level"] = LEVEL_ORDER[new_idx].capitalize()

        return {
            "status": "success",
            "message": "Learner profile updated successfully.",
            "updated_profile": updated_profile
        }
