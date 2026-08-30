from typing import List, Dict, Any
from rag.vectorstore.retriever import RetrievalResult

class ContextBuilder:
    @staticmethod
    def build_context(learner_profile: Dict[str, Any], retrieved_resources: List[RetrievalResult]) -> str:
        goal = learner_profile.get("goal", "Not specified")
        current_skills = ", ".join(learner_profile.get("skills", [])) or "None"
        level = learner_profile.get("level", "Intermediate")

        lines = []
        lines.append("LEARNER PROFILE")
        lines.append(f"Goal: {goal}")
        lines.append(f"Current skills: {current_skills}")
        lines.append(f"Level: {level}\n")

        lines.append("RELEVANT LEARNING RESOURCES\n")
        if not retrieved_resources:
            lines.append("No matching learning resources found in database.")
        else:
            for idx, res in enumerate(retrieved_resources, 1):
                lines.append(f"--- Resource {idx} ---")
                lines.append(f"Title: {res.title}")
                lines.append(f"Type: {res.doc_type.capitalize()}")
                lines.append(f"Skills covered: {', '.join(res.skills_covered) if res.skills_covered else 'N/A'}")
                lines.append(f"Prerequisites: {', '.join(res.prerequisites) if res.prerequisites else 'None'}")
                lines.append(f"Difficulty: {res.difficulty}")
                lines.append(f"Career relevance: {', '.join(res.career_relevance) if res.career_relevance else 'General'}")
                lines.append(f"Summary: {res.content}\n")

        return "\n".join(lines)
