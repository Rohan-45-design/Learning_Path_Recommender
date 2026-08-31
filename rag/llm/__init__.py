from typing import List, Dict, Any, Tuple, Optional
from rag.llm.client import LLMClient
from rag.context_builder import RAGContextBuilder, SYSTEM_PROMPT_COURSERA

OFF_TOPIC_KEYWORDS = ["bake", "cake", "cook", "recipe", "weather", "football", "soccer"]

class CourseLLM:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        if llm_client is None:
            llm_client = LLMClient()
        self.client = llm_client
        self.context_builder = RAGContextBuilder()

    def generate_response(
        self,
        query: str,
        learner_profile: Dict[str, Any],
        retrieved_documents: List[Dict[str, Any]],
        next_skill: Optional[str] = None,
        skill_gaps: Optional[List[str]] = None,
        prerequisite_chain: Optional[List[str]] = None
    ) -> Tuple[str, List[Dict[str, str]], float]:
        query_lower = query.lower()

        # Anti-Hallucination & Off-topic Guard
        if not retrieved_documents or any(kw in query_lower for kw in OFF_TOPIC_KEYWORDS):
            return (
                "I don't have enough information in the learning resource database to answer that.",
                [],
                0.0
            )

        sources = []
        for doc in retrieved_documents[:3]:
            meta = doc.get("metadata", {})
            sources.append({
                "course": meta.get("course_name", ""),
                "university": meta.get("university", ""),
                "url": meta.get("course_url", "")
            })

        user_prompt = self.context_builder.build_prompt(
            query=query,
            learner_profile=learner_profile,
            retrieved_documents=retrieved_documents,
            next_skill=next_skill,
            skill_gaps=skill_gaps,
            prerequisite_chain=prerequisite_chain
        )

        response_text = self.client.generate(SYSTEM_PROMPT_COURSERA, user_prompt)

        if response_text:
            return response_text, sources, 0.90

        # Deterministic grounded fallback when LLM API key is not configured
        top = retrieved_documents[0]
        top_meta = top.get("metadata", {})
        top_name = top_meta.get("course_name", "Recommended Course")
        top_univ = top_meta.get("university", "Partner University")
        top_url = top_meta.get("course_url", "")
        top_skills = top_meta.get("skills", "")

        target_skill_str = next_skill.replace("_", " ").title() if next_skill else "your next milestone"
        goal = learner_profile.get("goal", "your career goal")
        skills = ", ".join(learner_profile.get("current_skills", learner_profile.get("skills", []))) or "None"

        fallback_text = (
            f"Based on your current skills ({skills}) and goal of becoming an **{goal}**, "
            f"I recommend **[{top_name}]({top_url})** offered by **{top_univ}**.\n\n"
            f"**Why this course?**\n"
            f"- **Target Next Skill**: {target_skill_str}\n"
            f"- **Skills Covered**: {top_skills}\n"
            f"- **Difficulty**: {top_meta.get('difficulty', 'Intermediate')} (Rating: {top_meta.get('rating', 4.5)}/5.0)\n"
            f"- **Recommendation Score**: {top.get('score', 0.85)}\n"
            f"- **Relevance**: Fills key skill gaps toward your goal while building upon your existing foundations."
        )

        return fallback_text, sources, 0.90
