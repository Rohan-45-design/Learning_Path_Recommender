from typing import Dict, Any, List, Optional
from rag.skill_normalizer import normalize_skills, normalize_skill
from rag.prerequisites import PrerequisiteGraph

GOAL_TARGET_SKILLS = {
    "genai engineer": ["python", "machine_learning", "deep_learning", "transformers", "llm", "generative_ai", "rag", "ai_agents"],
    "ai engineer": ["python", "machine_learning", "deep_learning", "neural_networks", "computer_vision", "nlp", "transformers", "llm"],
    "ml engineer": ["python", "statistics", "machine_learning", "deep_learning", "scikit-learn", "tensorflow", "pytorch", "mlops"],
    "data scientist": ["python", "statistics", "sql", "data_analysis", "machine_learning", "regression"],
    "software engineer": ["python", "sql", "fastapi", "docker", "cloud"]
}

class LearnerAwareReranker:
    def __init__(self):
        self.prerequisites = PrerequisiteGraph()

    def score_course(
        self,
        course: Dict[str, Any],
        learner_profile: Dict[str, Any],
        next_skill: Optional[str] = None
    ) -> Dict[str, Any]:
        metadata = course.get("metadata", {})

        course_skills = normalize_skills(
            metadata.get("normalized_skills", metadata.get("skills", ""))
        )

        learner_skills_list = learner_profile.get("current_skills", learner_profile.get("skills", []))
        learner_skills = set(normalize_skills(learner_skills_list))

        goal_str = learner_profile.get("goal", "").strip().lower()
        target_goal_skills = GOAL_TARGET_SKILLS.get(goal_str, GOAL_TARGET_SKILLS["ai engineer"])

        # 1. Target Next Skill Match Score
        target_skill_norm = normalize_skill(next_skill) if next_skill else ""
        target_match_score = 0.0
        if target_skill_norm:
            if target_skill_norm in course_skills or any(target_skill_norm in s for s in course_skills):
                target_match_score = 1.0
            elif any(s in target_skill_norm for s in course_skills):
                target_match_score = 0.70

        # 2. Goal Skill Gap Score (Filter strictly against career goal skills)
        relevant_new_skills = [s for s in course_skills if s in target_goal_skills and s not in learner_skills]
        all_new_skills = [s for s in course_skills if s not in learner_skills]
        skill_gap_score = (len(relevant_new_skills) / len(target_goal_skills)) if target_goal_skills else 0.50

        # 3. Novelty Score (Avoid heavy overlap with already mastered skills)
        overlap = len(set(course_skills) & learner_skills) / max(len(course_skills), 1)
        novelty_score = 1.0 - overlap

        # 4. Difficulty Score & Reasoning
        difficulty = metadata.get("difficulty", "").lower()
        learner_level = learner_profile.get("level", "Intermediate").lower()
        difficulty_score = self._difficulty_score(difficulty, learner_level)

        # 5. Target Career Goal Alignment Boost
        goal_match_count = sum(1 for s in course_skills if s in target_goal_skills or any(t in s for t in target_goal_skills))
        goal_score = (goal_match_count / max(len(target_goal_skills), 1)) if target_goal_skills else 0.50
        goal_score = min(1.0, goal_score * 2.0)

        # 6. Semantic Score
        distance = course.get("distance", 1.0)
        semantic_score = max(0.0, 1.0 - distance)

        # 7. Prerequisite Validation & Sequencing Check
        prereq_violations = 0
        for s in course_skills:
            if not self.prerequisites.is_ready(s, list(learner_skills)):
                prereq_violations += 1

        prereq_score = 1.0 if prereq_violations == 0 else 0.20

        # COMPOSITE HYPERPARAMETER WEIGHTED SCORE
        final_score = (
            0.25 * semantic_score +
            0.25 * target_match_score +
            0.20 * skill_gap_score +
            0.15 * goal_score +
            0.10 * novelty_score +
            0.05 * difficulty_score
        ) * prereq_score

        # WHY RECOMMENDED EXPLANATIONS (Clean & Precise)
        why_recommended = []
        if target_match_score > 0 and next_skill:
            why_recommended.append(f"Teaches target next skill: '{next_skill.replace('_', ' ').title()}'")
        if goal_str and goal_match_count > 0:
            why_recommended.append(f"Matches career goal: {learner_profile.get('goal', 'AI Engineer')}")
        if relevant_new_skills:
            why_recommended.append(f"Fills target goal skill gap: {', '.join(relevant_new_skills[:2])}")
        if prereq_violations == 0:
            why_recommended.append("Prerequisite dependencies are fully satisfied")
        
        # Precise Difficulty Reasoning
        if difficulty == "beginner" and learner_level in ["intermediate", "advanced"] and target_match_score > 0:
            why_recommended.append(f"Beginner content is suitable because {next_skill.replace('_', ' ').title() if next_skill else 'this topic'} is your next missing foundational skill")
        elif difficulty_score >= 0.7:
            why_recommended.append(f"Appropriate difficulty level ({metadata.get('difficulty', 'Intermediate')})")

        return {
            **course,
            "score": round(final_score, 4),
            "target_match_score": round(target_match_score, 4),
            "skill_gap_score": round(skill_gap_score, 4),
            "novelty_score": round(novelty_score, 4),
            "goal_score": round(goal_score, 4),
            "semantic_score": round(semantic_score, 4),
            "difficulty_score": round(difficulty_score, 4),
            "prereq_score": round(prereq_score, 4),
            "prereq_violations": prereq_violations,
            "why_recommended": why_recommended
        }

    def _difficulty_score(self, course_level: str, learner_level: str) -> float:
        levels = {"beginner": 1, "conversant": 2, "intermediate": 3, "advanced": 4}
        course_val = levels.get(course_level, 3)
        learner_val = levels.get(learner_level, 3)
        diff = abs(course_val - learner_val)
        return 1.0 if diff == 0 else (0.7 if diff == 1 else 0.3)

    def rerank(
        self,
        courses: List[Dict[str, Any]],
        learner_profile: Dict[str, Any],
        next_skill: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        scored = [self.score_course(c, learner_profile, next_skill=next_skill) for c in courses]
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
