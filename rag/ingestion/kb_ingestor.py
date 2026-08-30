import os
import json
from typing import List, Dict, Any
from rag.ingestion.loader import CourseModel, SkillModel
from rag.ingestion.chunker import DocumentChunk, LearningDataChunker

class KnowledgeBaseIngestor:
    def __init__(self, kb_dir: str):
        self.kb_dir = kb_dir
        self.courses_dir = os.path.join(kb_dir, "courses")
        self.skills_dir = os.path.join(kb_dir, "skills")
        self.projects_dir = os.path.join(kb_dir, "projects")
        self.careers_dir = os.path.join(kb_dir, "career_roles")

    def load_all_chunks(self) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []

        # 1. Load JSON courses
        if os.path.exists(self.courses_dir):
            for fname in os.listdir(self.courses_dir):
                if fname.endswith(".json"):
                    fpath = os.path.join(self.courses_dir, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        course = CourseModel(
                            course_id=data.get("course_id", fname.replace(".json", "")),
                            title=data.get("title", ""),
                            description=data.get("description", ""),
                            skills_covered=data.get("skills_covered", []),
                            prerequisites=data.get("prerequisites", []),
                            difficulty=data.get("difficulty", "Intermediate"),
                            duration_hours=float(data.get("duration_hours", 20)),
                            career_relevance=data.get("career_roles", [])
                        )
                        chunks.append(LearningDataChunker.chunk_course(course))

        # 2. Load Markdown skill explainers
        if os.path.exists(self.skills_dir):
            for fname in os.listdir(self.skills_dir):
                if fname.endswith(".md"):
                    fpath = os.path.join(self.skills_dir, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                        skill_name = fname.replace(".md", "").replace("_", " ").title()
                        chunks.append(
                            DocumentChunk(
                                doc_id=f"SKILL_{fname.replace('.md', '').upper()}",
                                doc_type="skill",
                                title=f"Skill Guide: {skill_name}",
                                content=content,
                                skills_covered=[skill_name],
                                prerequisites=[],
                                difficulty="Intermediate",
                                career_relevance=[],
                                duration_hours=0.0,
                                raw_metadata={"skill_name": skill_name}
                            )
                        )

        # 3. Load Markdown project specs
        if os.path.exists(self.projects_dir):
            for fname in os.listdir(self.projects_dir):
                if fname.endswith(".md"):
                    fpath = os.path.join(self.projects_dir, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                        proj_name = fname.replace(".md", "").replace("_", " ").title()
                        chunks.append(
                            DocumentChunk(
                                doc_id=f"PROJ_{fname.replace('.md', '').upper()}",
                                doc_type="project",
                                title=f"Project: {proj_name}",
                                content=content,
                                skills_covered=[proj_name],
                                prerequisites=[],
                                difficulty="Advanced",
                                career_relevance=[],
                                duration_hours=15.0,
                                raw_metadata={"project_name": proj_name}
                            )
                        )

        # 4. Load Markdown career role mappings
        if os.path.exists(self.careers_dir):
            for fname in os.listdir(self.careers_dir):
                if fname.endswith(".md"):
                    fpath = os.path.join(self.careers_dir, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                        role_name = fname.replace(".md", "").replace("_", " ").title()
                        chunks.append(
                            DocumentChunk(
                                doc_id=f"CAREER_{fname.replace('.md', '').upper()}",
                                doc_type="career_role",
                                title=f"Career Goal: {role_name}",
                                content=content,
                                skills_covered=[role_name],
                                prerequisites=[],
                                difficulty="General",
                                career_relevance=[role_name],
                                duration_hours=0.0,
                                raw_metadata={"career_role": role_name}
                            )
                        )

        return chunks
