import os
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from rag.retriever import CourseRetriever
from rag.reranker import LearnerAwareReranker
from rag.goal_engine import GoalSkillEngine
from rag.learning_path import LearningPathGenerator
from rag.explainability import RecommendationExplainer
from rag.feedback import LearnerFeedbackEngine
from rag.llm import CourseLLM
from learner_db.state_manager import LearnerStateManager

class RAGResponse(BaseModel):
    answer: str
    sources: List[Dict[str, str]]
    confidence: float
    recommendations: List[Dict[str, Any]]
    learning_path: List[Dict[str, Any]]
    skill_gaps: List[str]
    next_skill: Optional[str] = None
    why_not_explanation: Optional[Dict[str, Any]] = None

class RAGPipeline:
    def __init__(
        self,
        db_path: str = "./chroma_db",
        collection_name: str = "learning_resources",
        data_dir: Optional[str] = None,
        kb_dir: Optional[str] = None
    ):
        self.retriever = CourseRetriever(db_path=db_path, collection_name=collection_name)
        self.goal_engine = GoalSkillEngine()
        self.reranker = LearnerAwareReranker()
        self.path_generator = LearningPathGenerator()
        self.explainer = RecommendationExplainer()
        self.feedback_engine = LearnerFeedbackEngine()
        self.llm = CourseLLM()
        self.state_manager = LearnerStateManager()

    def _resolve_learner_profile(
        self,
        student_id: Optional[str] = None,
        learner_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if learner_profile:
            # Harmonize skills and current_skills
            skills = learner_profile.get("current_skills") or learner_profile.get("skills") or ["Python", "Machine Learning"]
            profile = dict(learner_profile)
            profile["current_skills"] = skills
            profile["skills"] = skills
            profile.setdefault("goal", "GenAI Engineer")
            profile.setdefault("level", "Intermediate")
            return profile

        if student_id:
            profile = self.state_manager.get_learner_profile_dict(student_id)
            skills = profile.get("current_skills") or profile.get("skills") or ["Python", "Machine Learning"]
            profile["current_skills"] = skills
            profile["skills"] = skills
            return profile

        return {
            "goal": "GenAI Engineer",
            "current_skills": ["Python", "Machine Learning"],
            "skills": ["Python", "Machine Learning"],
            "level": "Intermediate"
        }

    def retrieve_resources(
        self,
        query: str,
        student_id: Optional[str] = None,
        learner_profile: Optional[Dict[str, Any]] = None,
        skill_gaps: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        resolved_profile = self._resolve_learner_profile(student_id, learner_profile)
        goal = resolved_profile.get("goal", "GenAI Engineer")
        learner_skills = resolved_profile.get("current_skills", [])
        next_skill = self.goal_engine.get_next_target_skill(goal, learner_skills)

        raw_results = self.retriever.retrieve(query, learner_profile=resolved_profile, next_skill=next_skill, top_k=15)
        retrieved_docs = []
        if raw_results and "documents" in raw_results and raw_results["documents"]:
            docs = raw_results["documents"][0]
            metas = raw_results["metadatas"][0] if "metadatas" in raw_results else [{}] * len(docs)
            distances = raw_results["distances"][0] if "distances" in raw_results else [1.0] * len(docs)
            for doc, meta, dist in zip(docs, metas, distances):
                retrieved_docs.append({"content": doc, "metadata": meta, "distance": dist})

        reranked = self.reranker.rerank(retrieved_docs, resolved_profile, next_skill=next_skill, top_k=top_k)
        candidates = []
        for r in reranked:
            meta = r.get("metadata", {})
            candidates.append({
                "course": meta.get("course_name", ""),
                "skill": meta.get("skills", ""),
                "university": meta.get("university", ""),
                "difficulty": meta.get("difficulty", ""),
                "relevance": r.get("score", 0.0),
                "skills": meta.get("skills", ""),
                "url": meta.get("course_url", ""),
                "why_recommended": r.get("why_recommended", [])
            })
        return candidates

    def query(
        self,
        query: str,
        student_id: Optional[str] = None,
        learner_profile: Optional[Dict[str, Any]] = None,
        skill_gaps: Optional[List[str]] = None,
        requested_why_not_skill: Optional[str] = None,
        top_k_retrieval: int = 15,
        top_k_final: int = 3
    ) -> RAGResponse:
        resolved_profile = self._resolve_learner_profile(student_id, learner_profile)
        goal = resolved_profile.get("goal", "GenAI Engineer")
        learner_skills = resolved_profile.get("current_skills", [])

        # 1. Skill Gap Analysis & Target Skill Selection
        gaps = self.goal_engine.get_skill_gaps(goal, learner_skills)
        next_skill = self.goal_engine.get_next_target_skill(goal, learner_skills)

        # 2. Structured Learning Path Generation (Milestone stages)
        path_info = self.path_generator.generate_path(
            learner_skills=learner_skills,
            target_goal=goal,
            custom_target_skills=skill_gaps or gaps
        )

        # 3. ChromaDB Semantic Retrieval (Top 15 candidates)
        raw_results = self.retriever.retrieve(
            query,
            learner_profile=resolved_profile,
            skill_gaps=gaps,
            next_skill=next_skill,
            top_k=top_k_retrieval
        )

        retrieved_docs = []
        if raw_results and "documents" in raw_results and raw_results["documents"]:
            docs = raw_results["documents"][0]
            metas = raw_results["metadatas"][0] if "metadatas" in raw_results else [{}] * len(docs)
            distances = raw_results["distances"][0] if "distances" in raw_results else [1.0] * len(docs)
            for doc, meta, dist in zip(docs, metas, distances):
                retrieved_docs.append({"content": doc, "metadata": meta, "distance": dist})

        # 4. Learner-Aware Reranking & Sequence Check (Select Top 3)
        reranked_docs = self.reranker.rerank(
            retrieved_docs,
            resolved_profile,
            next_skill=next_skill,
            top_k=top_k_final
        )

        # 5. Build Prerequisite Chain & Grounded LLM Response
        prereq_chain = [resolved_profile.get("current_skills", [])[0] if resolved_profile.get("current_skills") else "Python"]
        if next_skill:
            prereq_chain.append(next_skill)

        answer, sources, confidence = self.llm.generate_response(
            query=query,
            learner_profile=resolved_profile,
            retrieved_documents=reranked_docs,
            next_skill=next_skill,
            skill_gaps=gaps,
            prerequisite_chain=prereq_chain
        )

        # 6. Recommendation Explainer ("Why Not This Skill?")
        why_not_res = None
        if requested_why_not_skill:
            why_not_res = self.explainer.explain_why_not_skill(
                requested_skill=requested_why_not_skill,
                current_skills=learner_skills,
                next_target_skill=next_skill or "Deep Learning"
            )

        recommendations = []
        for d in reranked_docs:
            meta = d.get("metadata", {})
            recommendations.append({
                "course_name": meta.get("course_name", ""),
                "university": meta.get("university", ""),
                "difficulty": meta.get("difficulty", ""),
                "score": d.get("score", 0.0),
                "skill_gap_score": d.get("skill_gap_score", 0.0),
                "novelty_score": d.get("novelty_score", 0.0),
                "prereq_violations": d.get("prereq_violations", 0),
                "target_match_score": d.get("target_match_score", 0.0),
                "url": meta.get("course_url", ""),
                "why_recommended": d.get("why_recommended", [])
            })

        return RAGResponse(
            answer=answer,
            sources=sources,
            confidence=confidence,
            recommendations=recommendations,
            learning_path=path_info["milestones"],
            skill_gaps=gaps,
            next_skill=next_skill,
            why_not_explanation=why_not_res
        )

    def process_feedback(
        self,
        learner_profile: Dict[str, Any],
        course_completed: bool = False,
        completed_skills: Optional[List[str]] = None,
        feedback_text: Optional[str] = None
    ) -> Dict[str, Any]:
        return self.feedback_engine.process_feedback(
            learner_profile=learner_profile,
            course_completed=course_completed,
            completed_skills=completed_skills,
            feedback_text=feedback_text
        )
