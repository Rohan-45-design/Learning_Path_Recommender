from typing import List, Dict, Any
from rag.skill_normalizer import normalize_skills, normalize_skill
from rag.prerequisites import PrerequisiteGraph

GOAL_TARGET_MAP = {
    "genai engineer": ["python", "machine_learning", "deep_learning", "transformers", "llm", "generative_ai", "rag", "ai_agents"],
    "ai engineer": ["python", "machine_learning", "deep_learning", "neural_networks", "computer_vision", "nlp", "transformers", "llm"],
    "ml engineer": ["python", "statistics", "machine_learning", "deep_learning", "scikit-learn", "tensorflow", "mlops"],
    "data scientist": ["python", "statistics", "sql", "machine_learning", "regression", "data_analysis"],
    "software engineer": ["python", "sql", "fastapi", "docker", "cloud"]
}

SKILL_DISPLAY_NAMES = {
    "python": "Python Programming",
    "machine_learning": "Machine Learning Fundamentals",
    "deep_learning": "Deep Learning & Neural Networks",
    "neural_networks": "Neural Network Architectures",
    "computer_vision": "Computer Vision & Convolutional Nets",
    "nlp": "Natural Language Processing",
    "transformers": "Transformers & Self-Attention",
    "llm": "Large Language Models (LLMs)",
    "generative_ai": "Generative AI",
    "rag": "Retrieval-Augmented Generation (RAG)",
    "ai_agents": "Autonomous AI Agents",
    "mlops": "MLOps & Model Deployment",
    "statistics": "Statistical Analysis & Probability",
    "sql": "SQL & Data Management",
    "fastapi": "FastAPI Web Services",
    "docker": "Docker Containerization",
    "cloud": "Cloud Computing & AWS/Azure"
}

class LearningPathGenerator:
    def __init__(self):
        self.prerequisites = PrerequisiteGraph()

    def generate_path(
        self,
        learner_skills: List[str],
        target_goal: str,
        custom_target_skills: List[str] = None
    ) -> Dict[str, Any]:
        normalized_learner_skills = set(normalize_skills(learner_skills))
        goal_key = target_goal.strip().lower()

        if custom_target_skills:
            target_sequence = [normalize_skill(s) for s in custom_target_skills]
        else:
            target_sequence = GOAL_TARGET_MAP.get(goal_key, GOAL_TARGET_MAP["ai engineer"])

        missing_skills = [skill for skill in target_sequence if skill not in normalized_learner_skills]

        ordered_stages = []
        satisfied_skills = set(normalized_learner_skills)

        stage_num = 1
        for skill in missing_skills:
            # Prerequisite readiness depends strictly on CURRENT learner skills
            is_ready = self.prerequisites.is_ready(skill, list(satisfied_skills))
            display_name = SKILL_DISPLAY_NAMES.get(skill, skill.replace("_", " ").title())

            if stage_num == 1 and is_ready:
                status = "next"
            elif is_ready:
                status = "ready"
            else:
                status = "locked"

            ordered_stages.append({
                "stage": stage_num,
                "skill": skill,
                "display_name": display_name,
                "status": status,
                "prerequisites_met": is_ready,
                "prerequisites_required": self.prerequisites.get_prerequisites(skill)
            })

            # Do NOT simulate satisfied_skills.add(skill) for future locked stages!
            stage_num += 1

        next_skill = ordered_stages[0]["skill"] if ordered_stages else None

        return {
            "target_goal": target_goal,
            "mastered_skills": list(normalized_learner_skills),
            "next_skill": next_skill,
            "skill_gaps": missing_skills,
            "milestones": ordered_stages
        }
