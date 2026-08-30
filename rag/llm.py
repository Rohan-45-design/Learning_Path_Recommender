from typing import List, Dict, Any, Tuple
from rag.llm.client import LLMClient

SYSTEM_PROMPT_COURSERA = """You are PathAI, a personalized AI learning mentor and course recommender.
Use ONLY the provided retrieved Coursera learning resources as your primary source of information.
Do NOT invent course names, universities, ratings, or skills not explicitly present in the retrieved context.

If the retrieved context does not contain enough information to answer the question, state:
"I don't have enough information in the Coursera learning resource database to answer that."

Structure your response clearly:
1. Direct answer / recommendation with course name and university
2. Explanation of why this fits the learner's goal and skills
3. Direct course URL link when available
"""

class CourseLLM:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        if llm_client is None:
            llm_client = LLMClient()
        self.client = llm_client

    def generate_response(
        self,
        query: str,
        learner_profile: Dict[str, Any],
        retrieved_documents: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, str]], float]:
        if not retrieved_documents:
            return (
                "I don't have enough information in the Coursera learning resource database to answer that.",
                [],
                0.0
            )

        # Context assembly
        context_lines = []
        sources = []
        for idx, doc in enumerate(retrieved_documents[:3], 1):
            meta = doc.get("metadata", {})
            name = meta.get("course_name", f"Course {idx}")
            univ = meta.get("university", "Unknown")
            diff = meta.get("difficulty", "Intermediate")
            rating = meta.get("rating", 0.0)
            url = meta.get("course_url", "")
            skills = meta.get("skills", "")

            sources.append({
                "course": name,
                "university": univ,
                "url": url
            })

            context_lines.append(
                f"[{idx}] Course: {name}\n"
                f"    University: {univ}\n"
                f"    Difficulty: {diff} | Rating: {rating}\n"
                f"    Skills: {skills}\n"
                f"    URL: {url}\n"
                f"    Description Snippet: {doc.get('content', '')[:300]}...\n"
            )

        context_str = "\n".join(context_lines)
        goal = learner_profile.get("goal", "Not specified")
        skills = ", ".join(learner_profile.get("current_skills", learner_profile.get("skills", []))) or "None"
        level = learner_profile.get("level", "Intermediate")

        user_prompt = f"""LEARNER PROFILE:
Goal: {goal}
Current Skills: {skills}
Skill Level: {level}

RETRIEVED COURSERA RESOURCES:
{context_str}

USER QUESTION:
{query}
"""

        # Call LLM client if API key is present
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

        fallback_text = (
            f"Based on your current skills ({skills}) and goal of becoming an **{goal}**, "
            f"I recommend **[{top_name}]({top_url})** offered by **{top_univ}**.\n\n"
            f"**Why this course?**\n"
            f"- **Skills Covered**: {top_skills}\n"
            f"- **Difficulty**: {top_meta.get('difficulty', 'Intermediate')} (Rating: {top_meta.get('rating', 4.5)}/5.0)\n"
            f"- **Relevance**: Matches your career target and builds upon your existing foundations."
        )

        return fallback_text, sources, 0.90
