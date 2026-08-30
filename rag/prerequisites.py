import os
import pandas as pd
from typing import List, Set

class PrerequisiteGraph:
    def __init__(self, path: str = "data/skill_prerequisites.csv"):
        if not os.path.exists(path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(base_dir, "data", "skill_prerequisites.csv")

        self.graph = {}
        if os.path.exists(path):
            df = pd.read_csv(path)
            for _, row in df.iterrows():
                skill = str(row["skill"]).strip().lower()
                prerequisite = str(row["prerequisite"]).strip().lower()
                self.graph.setdefault(skill, []).append(prerequisite)

    def get_prerequisites(self, skill: str) -> List[str]:
        return self.graph.get(skill.lower(), [])

    def is_ready(self, skill: str, learner_skills: List[str]) -> bool:
        prerequisites = self.get_prerequisites(skill)
        learner_set = {s.lower() for s in learner_skills}
        return all(prereq in learner_set for prereq in prerequisites)
