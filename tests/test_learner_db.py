import pytest
from learner_db.state_manager import LearnerStateManager

def test_oulad_student_lookup():
    manager = LearnerStateManager()
    student = manager.get_learner("student_123")
    assert student is not None
    assert student.goal == "GenAI Engineer"
    assert "Python" in student.mastered_skills
    assert "Machine Learning" in student.mastered_skills
    assert "Deep Learning" in student.skill_gaps

def test_learner_profile_dict():
    manager = LearnerStateManager()
    profile = manager.get_learner_profile_dict("student_123")
    assert profile["goal"] == "GenAI Engineer"
    assert profile["skills"] == ["Python", "Machine Learning"]
    assert profile["vle_engagement"] == 1420
