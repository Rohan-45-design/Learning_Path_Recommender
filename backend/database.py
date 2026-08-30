import json
import os
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# SQLite database URL (can be overridden via environment variable)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./courses.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a database session and closing it on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(target_engine=None) -> None:
    """Create database tables."""
    from backend import models  # noqa: F401 - ensure models are imported
    eng = target_engine or engine
    Base.metadata.create_all(bind=eng)


def seed_mock_courses(json_path: str = None, db: Session = None) -> int:
    """
    Seed course records from data/mock_courses.json into SQLite.
    Skips courses that already exist by course_id to maintain idempotency.
    Returns the count of newly inserted courses.
    """
    from backend.models import Course

    if json_path is None:
        base_dir = Path(__file__).resolve().parent.parent
        json_path = str(base_dir / "data" / "mock_courses.json")

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Mock courses file not found at: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        courses_data = json.load(f)

    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True

    inserted_count = 0
    try:
        for item in courses_data:
            existing = db.query(Course).filter(Course.course_id == item["course_id"]).first()
            if not existing:
                course = Course(
                    course_id=item["course_id"],
                    title=item["title"],
                    provider=item["provider"],
                    description=item["description"],
                    skills_covered=item.get("skills_covered", []),
                    prerequisites=item.get("prerequisites", []),
                    difficulty=item["difficulty"],
                    est_hours=item["est_hours"],
                )
                db.add(course)
                inserted_count += 1
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        if close_session:
            db.close()

    return inserted_count
