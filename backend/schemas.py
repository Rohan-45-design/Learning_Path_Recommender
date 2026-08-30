from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CourseBase(BaseModel):
    """Base schema for course attributes."""
    course_id: str = Field(..., description="Unique course identifier", min_length=1)
    title: str = Field(..., description="Course title", min_length=1)
    provider: str = Field(..., description="Course platform/provider", min_length=1)
    description: str = Field(..., description="Course description")
    skills_covered: List[str] = Field(default_factory=list, description="List of skills covered by the course")
    prerequisites: List[str] = Field(default_factory=list, description="List of prerequisite course IDs or topics")
    difficulty: str = Field(..., description="Difficulty level (e.g. Beginner, Intermediate, Advanced)")
    est_hours: int = Field(..., description="Estimated completion hours", gt=0)


class CourseCreate(CourseBase):
    """Schema for POST /courses."""
    pass


class CourseUpdate(BaseModel):
    """Schema for PUT /courses/{course_id}. All fields optional."""
    title: Optional[str] = Field(None, min_length=1)
    provider: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    skills_covered: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    difficulty: Optional[str] = None
    est_hours: Optional[int] = Field(None, gt=0)


class CourseResponse(CourseBase):
    """Response schema for course data."""
    model_config = ConfigDict(from_attributes=True)
