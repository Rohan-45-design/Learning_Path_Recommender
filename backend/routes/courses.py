from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Course
from backend.schemas import CourseCreate, CourseResponse, CourseUpdate

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("", response_model=List[CourseResponse])
def get_all_courses(db: Session = Depends(get_db)):
    """Retrieve all courses from the database."""
    return db.query(Course).all()


@router.get("/{course_id}", response_model=CourseResponse)
def get_course_by_id(course_id: str, db: Session = Depends(get_db)):
    """Retrieve a single course by its unique course_id."""
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with course_id '{course_id}' not found.",
        )
    return course


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(course_in: CourseCreate, db: Session = Depends(get_db)):
    """Create a new course. Returns 400 if course_id already exists."""
    existing = db.query(Course).filter(Course.course_id == course_in.course_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course with course_id '{course_in.course_id}' already exists.",
        )

    course = Course(
        course_id=course_in.course_id,
        title=course_in.title,
        provider=course_in.provider,
        description=course_in.description,
        skills_covered=course_in.skills_covered,
        prerequisites=course_in.prerequisites,
        difficulty=course_in.difficulty,
        est_hours=course_in.est_hours,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(course_id: str, course_update: CourseUpdate, db: Session = Depends(get_db)):
    """Update an existing course by course_id."""
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with course_id '{course_id}' not found.",
        )

    update_data = course_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)

    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_200_OK)
def delete_course(course_id: str, db: Session = Depends(get_db)):
    """Delete a course by its unique course_id."""
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with course_id '{course_id}' not found.",
        )

    db.delete(course)
    db.commit()
    return {"message": f"Course '{course_id}' deleted successfully.", "course_id": course_id}
