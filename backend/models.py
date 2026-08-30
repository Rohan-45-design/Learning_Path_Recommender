from sqlalchemy import Column, Integer, String, Text, JSON
from backend.database import Base


class Course(Base):
    """
    SQLAlchemy model representing a course in the catalog.
    Matches data/mock_courses.json fields directly.
    """
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    skills_covered = Column(JSON, default=list, nullable=False)
    prerequisites = Column(JSON, default=list, nullable=False)
    difficulty = Column(String, nullable=False)
    est_hours = Column(Integer, nullable=False)

    def to_dict(self) -> dict:
        """Serialize course model to dictionary."""
        return {
            "course_id": self.course_id,
            "title": self.title,
            "provider": self.provider,
            "description": self.description,
            "skills_covered": self.skills_covered or [],
            "prerequisites": self.prerequisites or [],
            "difficulty": self.difficulty,
            "est_hours": self.est_hours,
        }
