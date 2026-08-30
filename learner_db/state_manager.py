import os
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel

class OULADStudentProfile(BaseModel):
    id_student: str
    code_module: str
    code_presentation: str
    highest_education: str
    vle_clicks: int
    assessment_score: float
    mastered_skills: list
    goal: str
    level: str
    skill_gaps: list

class LearnerStateManager:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "learner_db", "oulad_students.json")
        self.db_path = db_path
        self.students: Dict[str, OULADStudentProfile] = {}
        self._load_students()

    def _load_students(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    student = OULADStudentProfile(**item)
                    self.students[student.id_student] = student

    def get_learner(self, student_id: str) -> Optional[OULADStudentProfile]:
        return self.students.get(student_id)

    def get_learner_profile_dict(self, student_id: str) -> Dict[str, Any]:
        student = self.get_learner(student_id)
        if student:
            return {
                "goal": student.goal,
                "skills": student.mastered_skills,
                "level": student.level,
                "vle_engagement": student.vle_clicks,
                "assessment_score": student.assessment_score
            }
        # Default profile fallback
        return {
            "goal": "GenAI Engineer",
            "skills": ["Python", "Machine Learning"],
            "level": "Intermediate",
            "vle_engagement": 1000,
            "assessment_score": 85.0
        }
