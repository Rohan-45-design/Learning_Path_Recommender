from typing import Dict, Any, List, Optional

SYSTEM_PROMPT_COURSERA = """You are PathAI, a personalized AI learning mentor and course recommender.
PathAI uses deterministic skill-gap and prerequisite reasoning to construct the learning path, while you act as a grounded conversational layer that explains recommendations and answers learner questions.

Strict Instructions:
1. Use ONLY the provided retrieved Coursera learning resources as your primary source of course information.
2. Do NOT invent course names, universities, ratings, skills, or URLs not explicitly present in the retrieved context.
3. The learner's existing skills must be treated as already known. Do not recommend introductory material solely covering skills the learner already possesses unless explicitly asked.
4. Respect the supplied prerequisite relationships.
5. Explain why the recommended target next skill is appropriate for the learner's goal.
6. If the supplied context does not contain enough information to answer the question, state:
   "I don't have enough information in the learning resource database to answer that."

Structure your response clearly:
1. Direct answer / recommendation with course name and university
2. Explanation of why this fits the learner's target next skill and goal
3. Direct course URL link when available
"""

class RAGContextBuilder:
    def __init__(self):
        pass

    def build_prompt(
        self,
        query: str,
        learner_profile: Dict[str, Any],
        retrieved_documents: List[Dict[str, Any]],
        next_skill: Optional[str] = None,
        skill_gaps: Optional[List[str]] = None,
        prerequisite_chain: Optional[List[str]] = None
    ) -> str:
        goal = learner_profile.get("goal", "Not specified")
        current_skills = ", ".join(learner_profile.get("current_skills", learner_profile.get("skills", []))) or "None"
        level = learner_profile.get("level", "Intermediate")
        target_skill_str = next_skill.replace("_", " ").title() if next_skill else "General AI"
        gaps_str = ", ".join(skill_gaps) if skill_gaps else "None"
        prereq_str = " -> ".join(prerequisite_chain) if prerequisite_chain else "None"

        context_lines = []
        for idx, doc in enumerate(retrieved_documents[:3], 1):
            meta = doc.get("metadata", {})
            name = meta.get("course_name", f"Course {idx}")
            univ = meta.get("university", "Unknown")
            diff = meta.get("difficulty", "Intermediate")
            rating = meta.get("rating", 0.0)
            url = meta.get("course_url", "")
            skills = meta.get("skills", "")
            score = doc.get("score", 0.0)
            why_recs = "; ".join(doc.get("why_recommended", []))

            context_lines.append(
                f"[{idx}] Course: {name}\n"
                f"    University: {univ}\n"
                f"    Difficulty: {diff} | Rating: {rating}\n"
                f"    Skills: {skills}\n"
                f"    Recommendation Score: {score}\n"
                f"    Why Recommended: {why_recs}\n"
                f"    URL: {url}\n"
                f"    Description Snippet: {doc.get('content', '')[:300]}...\n"
            )

        context_str = "\n".join(context_lines)

        user_prompt = f"""LEARNER PROFILE:
Goal: {goal}
Current Skills: {current_skills}
Skill Level: {level}

TARGET NEXT SKILL: {target_skill_str}
SKILL GAPS IDENTIFIED: {gaps_str}
PREREQUISITE CHAIN: {prereq_str}

RETRIEVED COURSERA RESOURCES (RANKED BY RECOMMENDATION ENGINE):
{context_str}

USER QUESTION:
{query}
"""
        return user_prompt
