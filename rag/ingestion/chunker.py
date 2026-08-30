from typing import List, Dict, Any
from pydantic import BaseModel
from rag.ingestion.loader import CourseModel, SkillModel

class DocumentChunk(BaseModel):
    doc_id: str
    doc_type: str  # "course" or "skill"
    title: str
    content: str
    skills_covered: List[str]
    prerequisites: List[str]
    difficulty: str
    career_relevance: List[str]
    duration_hours: float = 0.0
    raw_metadata: Dict[str, Any]

class LearningDataChunker:
    @staticmethod
    def chunk_course(course: CourseModel) -> DocumentChunk:
        skills_str = ", ".join(course.skills_covered) if course.skills_covered else "None"
        prereqs_str = ", ".join(course.prerequisites) if course.prerequisites else "None"
        careers_str = ", ".join(course.career_relevance) if course.career_relevance else "General"
        
        content = (
            f"Course Title: {course.title}\n"
            f"Description: {course.description}\n"
            f"Skills Covered: {skills_str}\n"
            f"Prerequisites: {prereqs_str}\n"
            f"Difficulty Level: {course.difficulty}\n"
            f"Duration: {course.duration_hours} hours\n"
            f"Career Relevance: {careers_str}"
        )
        
        return DocumentChunk(
            doc_id=course.course_id,
            doc_type="course",
            title=course.title,
            content=content,
            skills_covered=course.skills_covered,
            prerequisites=course.prerequisites,
            difficulty=course.difficulty,
            career_relevance=course.career_relevance,
            duration_hours=course.duration_hours,
            raw_metadata={
                "course_id": course.course_id,
                "title": course.title,
                "description": course.description,
            }
        )

    @staticmethod
    def chunk_skill(skill: SkillModel) -> DocumentChunk:
        prereqs_str = ", ".join(skill.prerequisite_skills) if skill.prerequisite_skills else "None"
        content = (
            f"Skill Name: {skill.name}\n"
            f"Description: {skill.description}\n"
            f"Category: {skill.category}\n"
            f"Prerequisite Skills: {prereqs_str}"
        )
        return DocumentChunk(
            doc_id=skill.skill_id,
            doc_type="skill",
            title=skill.name,
            content=content,
            skills_covered=[skill.name],
            prerequisites=skill.prerequisite_skills,
            difficulty="Intermediate",
            career_relevance=[],
            duration_hours=0.0,
            raw_metadata={
                "skill_id": skill.skill_id,
                "name": skill.name,
                "category": skill.category
            }
        )

    def process_all(self, courses: List[CourseModel], skills: List[SkillModel]) -> List[DocumentChunk]:
        chunks = []
        for course in courses:
            chunks.append(self.chunk_course(course))
        for skill in skills:
            chunks.append(self.chunk_skill(skill))
        return chunks
