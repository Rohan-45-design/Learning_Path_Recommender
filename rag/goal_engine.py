import os
import pandas as pd
from typing import List, Set, Dict, Any, Optional
from rag.skill_normalizer import normalize_skills, normalize_skill
from rag.prerequisites import PrerequisiteGraph

class GoalSkillEngine:
    def __init__(self, csv_path: str = "data/goal_skills.csv"):
        if not os.path.exists(csv_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            csv_path = os.path.join(base_dir, "data", "goal_skills.csv")

        self.goal_skills = {}
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                goal = str(row["goal"]).strip().lower()
                skill = str(row["skill"]).strip().lower()
                self.goal_skills.setdefault(goal, []).append(skill)

        self.prerequisites = PrerequisiteGraph()

    def get_required_skills(self, goal: str) -> List[str]:
        goal_key = goal.strip().lower()
        skills = self.goal_skills.get(goal_key, [])
        if not skills:
            skills = self.goal_skills.get("ai engineer", ["python", "machine_learning", "deep_learning"])
        return skills

    def get_skill_gaps(self, goal: str, current_skills: List[str]) -> List[str]:
        required = self.get_required_skills(goal)
        current = set(normalize_skills(current_skills))
        gaps = [skill for skill in required if skill not in current]
        return gaps

    def get_ordered_skill_gaps(self, goal: str, current_skills: List[str]) -> List[Dict[str, Any]]:
        gaps = self.get_skill_gaps(goal, current_skills)
        current_set = set(normalize_skills(current_skills))

        ordered = []
        satisfied = set(current_set)

        for skill in gaps:
            is_ready = self.prerequisites.is_ready(skill, list(satisfied))
            prereqs = self.prerequisites.get_prerequisites(skill)

            ordered.append({
                "skill": skill,
                "is_ready": is_ready,
                "missing_prerequisites": [p for p in prereqs if p not in current_set]
            })
            satisfied.add(skill)

        ordered.sort(key=lambda x: (not x["is_ready"], len(x["missing_prerequisites"])))
        return ordered

    def get_next_target_skill(self, goal: str, current_skills: List[str]) -> Optional[str]:
        ordered_gaps = self.get_ordered_skill_gaps(goal, current_skills)
        if ordered_gaps:
            return ordered_gaps[0]["skill"]
        return None
