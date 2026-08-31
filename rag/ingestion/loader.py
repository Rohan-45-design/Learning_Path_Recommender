import os
import pandas as pd
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class CourseModel(BaseModel):
    course_id: str
    title: str
    description: str
    skills_covered: List[str]
    prerequisites: List[str]
    difficulty: str
    duration_hours: float
    career_relevance: List[str]

class SkillModel(BaseModel):
    skill_id: str
    name: str
    description: str
    prerequisite_skills: List[str]
    category: str

class PrerequisiteModel(BaseModel):
    target_skill: str
    prerequisite_skill: str
    dependency_level: str

class DataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.courses_path = os.path.join(data_dir, "courses.csv")
        self.skills_path = os.path.join(data_dir, "skills.csv")
        self.prerequisites_path = os.path.join(data_dir, "prerequisites.csv")

    def parse_list(self, raw_str: Any) -> List[str]:
        if pd.isna(raw_str) or not raw_str or str(raw_str).strip().lower() == "none":
            return []
        return [item.strip() for item in str(raw_str).split(";") if item.strip()]

    def load_courses(self) -> List[CourseModel]:
        if not os.path.exists(self.courses_path):
            raise FileNotFoundError(f"Courses file not found at {self.courses_path}")
        df = pd.read_csv(self.courses_path)
        courses = []
        for _, row in df.iterrows():
            courses.append(
                CourseModel(
                    course_id=str(row["course_id"]),
                    title=str(row["title"]),
                    description=str(row["description"]),
                    skills_covered=self.parse_list(row["skills_covered"]),
                    prerequisites=self.parse_list(row["prerequisites"]),
                    difficulty=str(row["difficulty"]),
                    duration_hours=float(row["duration_hours"]),
                    career_relevance=self.parse_list(row["career_relevance"]),
                )
            )
        return courses

    def load_skills(self) -> List[SkillModel]:
        if not os.path.exists(self.skills_path):
            raise FileNotFoundError(f"Skills file not found at {self.skills_path}")
        df = pd.read_csv(self.skills_path)
        skills = []
        for _, row in df.iterrows():
            skills.append(
                SkillModel(
                    skill_id=str(row["skill_id"]),
                    name=str(row["name"]),
                    description=str(row["description"]),
                    prerequisite_skills=self.parse_list(row["prerequisite_skills"]),
                    category=str(row["category"]),
                )
            )
        return skills

    def load_prerequisites(self) -> List[PrerequisiteModel]:
        if not os.path.exists(self.prerequisites_path):
            raise FileNotFoundError(f"Prerequisites file not found at {self.prerequisites_path}")
        df = pd.read_csv(self.prerequisites_path)
        prereqs = []
        for _, row in df.iterrows():
            prereqs.append(
                PrerequisiteModel(
                    target_skill=str(row["target_skill"]),
                    prerequisite_skill=str(row["prerequisite_skill"]),
                    dependency_level=str(row["dependency_level"]),
                )
            )
        return prereqs
