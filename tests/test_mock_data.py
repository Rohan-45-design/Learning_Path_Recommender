import json
from pathlib import Path
import pytest
from backend.database import seed_mock_courses
from backend.models import Course
from backend.schemas import CourseCreate


@pytest.fixture
def mock_json_path():
    base_dir = Path(__file__).resolve().parent.parent
    return base_dir / "data" / "mock_courses.json"


def test_mock_courses_json_validity(mock_json_path):
    """Ensure data/mock_courses.json exists and adheres to expected schema."""
    assert mock_json_path.exists(), f"mock_courses.json not found at {mock_json_path}"
    with open(mock_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 5, f"Expected 5 mock courses, found {len(data)}"

    seen_ids = set()
    for item in data:
        validated = CourseCreate(**item)
        assert validated.course_id not in seen_ids, f"Duplicate course_id: {validated.course_id}"
        seen_ids.add(validated.course_id)
        assert validated.title
        assert validated.provider
        assert validated.description
        assert isinstance(validated.skills_covered, list)
        assert isinstance(validated.prerequisites, list)
        assert validated.difficulty in ["Beginner", "Intermediate", "Advanced"]
        assert validated.est_hours > 0


def test_seed_mock_courses_into_database(mock_json_path, db_session):
    """Ensure seed_mock_courses loads all 5 courses into SQLite and is idempotent."""
    inserted = seed_mock_courses(json_path=str(mock_json_path), db=db_session)
    assert inserted == 5

    courses = db_session.query(Course).all()
    assert len(courses) == 5

    # Idempotency check
    second_run = seed_mock_courses(json_path=str(mock_json_path), db=db_session)
    assert second_run == 0
    assert len(db_session.query(Course).all()) == 5


def test_api_returns_mock_courses(mock_json_path, db_session, client):
    """Ensure API /courses accurately returns the seeded mock courses."""
    seed_mock_courses(json_path=str(mock_json_path), db=db_session)

    response = client.get("/courses")
    assert response.status_code == 200
    courses_data = response.json()
    assert len(courses_data) == 5

    # Verify specific courses from mock_courses.json
    cs101_res = client.get("/courses/CS101")
    assert cs101_res.status_code == 200
    cs101 = cs101_res.json()
    assert cs101["title"] == "Python Programming Fundamentals"
    assert cs101["provider"] == "Coursera"
    assert cs101["skills_covered"] == ["Python", "Algorithms"]
    assert cs101["difficulty"] == "Beginner"
    assert cs101["est_hours"] == 12

    de102_res = client.get("/courses/DE102")
    assert de102_res.status_code == 200
    de102 = de102_res.json()
    assert de102["title"] == "Data Warehousing & ETL Pipelines"
    assert de102["prerequisites"] == ["CS101", "DE101"]
    assert de102["difficulty"] == "Intermediate"
    assert de102["est_hours"] == 20

    de103_res = client.get("/courses/DE103")
    assert de103_res.status_code == 200
    de103 = de103_res.json()
    assert de103["prerequisites"] == ["DE102"]
    assert de103["difficulty"] == "Advanced"
