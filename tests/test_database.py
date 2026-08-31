import pytest
from sqlalchemy.exc import IntegrityError
from backend.models import Course


def test_create_course(db_session):
    """Test creating a course in the database."""
    course = Course(
        course_id="CS101",
        title="Python Programming Fundamentals",
        provider="Coursera",
        description="Learn syntax, variables, loops, functions, and data structures in Python.",
        skills_covered=["Python", "Algorithms"],
        prerequisites=[],
        difficulty="Beginner",
        est_hours=12,
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)

    assert course.id is not None
    assert course.course_id == "CS101"
    assert course.title == "Python Programming Fundamentals"
    assert course.skills_covered == ["Python", "Algorithms"]
    assert course.est_hours == 12


def test_retrieve_course(db_session):
    """Test retrieving a course from the database."""
    course = Course(
        course_id="DE101",
        title="SQL & Relational Databases",
        provider="edX",
        description="Master SQL queries, table creation, joins, indexing, and normalization.",
        skills_covered=["SQL", "PostgreSQL", "Data Modeling"],
        prerequisites=[],
        difficulty="Beginner",
        est_hours=15,
    )
    db_session.add(course)
    db_session.commit()

    retrieved = db_session.query(Course).filter(Course.course_id == "DE101").first()
    assert retrieved is not None
    assert retrieved.title == "SQL & Relational Databases"
    assert retrieved.difficulty == "Beginner"


def test_update_course(db_session):
    """Test updating course fields."""
    course = Course(
        course_id="DE102",
        title="Original Title",
        provider="Udacity",
        description="Old description",
        skills_covered=["ETL"],
        prerequisites=["CS101"],
        difficulty="Intermediate",
        est_hours=10,
    )
    db_session.add(course)
    db_session.commit()

    course.title = "Data Warehousing & ETL Pipelines"
    course.est_hours = 20
    course.skills_covered = ["ETL", "Data Warehousing", "Python", "SQL"]
    course.prerequisites = ["CS101", "DE101"]
    db_session.commit()
    db_session.refresh(course)

    updated = db_session.query(Course).filter(Course.course_id == "DE102").first()
    assert updated.title == "Data Warehousing & ETL Pipelines"
    assert updated.est_hours == 20
    assert updated.skills_covered == ["ETL", "Data Warehousing", "Python", "SQL"]
    assert updated.prerequisites == ["CS101", "DE101"]


def test_delete_course(db_session):
    """Test deleting a course from the database."""
    course = Course(
        course_id="DEL101",
        title="To Delete",
        provider="Provider",
        description="Description",
        skills_covered=[],
        prerequisites=[],
        difficulty="Beginner",
        est_hours=5,
    )
    db_session.add(course)
    db_session.commit()

    db_session.delete(course)
    db_session.commit()

    deleted = db_session.query(Course).filter(Course.course_id == "DEL101").first()
    assert deleted is None


def test_unique_course_id_constraint(db_session):
    """Test that duplicate course_id raises an IntegrityError."""
    course1 = Course(
        course_id="CS101",
        title="Course 1",
        provider="Provider 1",
        description="Description 1",
        skills_covered=[],
        prerequisites=[],
        difficulty="Beginner",
        est_hours=10,
    )
    course2 = Course(
        course_id="CS101",
        title="Course 2",
        provider="Provider 2",
        description="Description 2",
        skills_covered=[],
        prerequisites=[],
        difficulty="Intermediate",
        est_hours=20,
    )
    db_session.add(course1)
    db_session.commit()

    db_session.add(course2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
