import os
import pytest
from rag.ingestion.loader import DataLoader

def test_loader_courses():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "rag", "data")
    loader = DataLoader(data_dir)
    
    courses = loader.load_courses()
    assert len(courses) > 0
    course_ids = [c.course_id for c in courses]
    assert "C104" in course_ids  # Deep Learning Fundamentals

def test_loader_skills():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "rag", "data")
    loader = DataLoader(data_dir)
    
    skills = loader.load_skills()
    assert len(skills) > 0
    names = [s.name for s in skills]
    assert "Deep Learning" in names
    assert "Python" in names

def test_loader_prerequisites():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "rag", "data")
    loader = DataLoader(data_dir)
    
    prereqs = loader.load_prerequisites()
    assert len(prereqs) > 0
