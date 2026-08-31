from typing import List, Dict, Any, Tuple
from rag.llm.client import LLMClient
from rag.llm.prompts import SYSTEM_PROMPT, build_user_prompt
from rag.vectorstore.retriever import RetrievalResult

class AnswerGenerator:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def generate_answer(
        self,
        query: str,
        learner_profile: Dict[str, Any],
        context_str: str,
        retrieved_resources: List[RetrievalResult]
    ) -> Tuple[str, List[Dict[str, str]], float]:
        """
        Generates grounded response, sources, and confidence score.
        Returns: (answer_text, sources_list, confidence_score)
        """
        # If no resources retrieved or top semantic similarity is <= 0.03, return anti-hallucination fallback
        if not retrieved_resources or (retrieved_resources and retrieved_resources[0].semantic_score <= 0.03):
            return (
                "I don't have enough information in the learning resource database to answer that.",
                [],
                0.0
            )

        # Extract citation sources
        sources = []
        for r in retrieved_resources[:3]:
            primary_skill = r.skills_covered[0] if r.skills_covered else r.title
            sources.append({
                "course": r.title,
                "skill": primary_skill
            })

        # Calculate overall retrieval confidence score (average of top 3 relevance scores)
        confidence = sum(r.relevance_score for r in retrieved_resources[:3]) / min(3, len(retrieved_resources))
        confidence = round(confidence, 2)

        user_prompt = build_user_prompt(query, learner_profile, context_str)
        llm_response = self.llm_client.generate(SYSTEM_PROMPT, user_prompt)

        if llm_response:
            return llm_response, sources, confidence

        # Deterministic grounded fallback when LLM API key is not configured
        top = retrieved_resources[0]
        prereqs_str = ", ".join(top.prerequisites) if top.prerequisites else "None"
        skills_str = ", ".join(top.skills_covered) if top.skills_covered else top.title
        goal = learner_profile.get("goal", "your career target")

        answer_text = (
            f"Based on your current skills ({', '.join(learner_profile.get('skills', []))}) and goal ({goal}), "
            f"**{top.title}** is your most appropriate next step. "
            f"It covers key skills in {skills_str} and requires prerequisites: {prereqs_str}. "
            f"Completing this will satisfy foundational prerequisites for downstream advanced learning."
        )

        return answer_text, sources, confidence
