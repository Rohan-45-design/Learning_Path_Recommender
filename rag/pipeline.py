from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from rag.retriever import CourseRetriever
from rag.reranker import LearnerAwareReranker
from rag.llm import CourseLLM

class RAGResponse(BaseModel):
    answer: str
    sources: List[Dict[str, str]]
    confidence: float
    recommendations: List[Dict[str, Any]]

class RAGPipeline:
    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "learning_resources"):
        self.retriever = CourseRetriever(db_path=db_path, collection_name=collection_name)
        self.reranker = LearnerAwareReranker()
        self.llm = CourseLLM()

    def query(self, query: str, learner_profile: Optional[Dict[str, Any]] = None, top_k_retrieval: int = 15, top_k_final: int = 3) -> RAGResponse:
        if learner_profile is None:
            learner_profile = {
                "goal": "AI Engineer",
                "current_skills": ["Python", "Machine Learning"],
                "level": "Intermediate"
            }

        # Step 1: ChromaDB Semantic Candidate Retrieval (Fetch Top 15)
        raw_results = self.retriever.retrieve(query, learner_profile=learner_profile, top_k=top_k_retrieval)

        retrieved_docs = []
        if raw_results and "documents" in raw_results and raw_results["documents"]:
            docs = raw_results["documents"][0]
            metas = raw_results["metadatas"][0] if "metadatas" in raw_results else [{}] * len(docs)
            distances = raw_results["distances"][0] if "distances" in raw_results else [1.0] * len(docs)
            for doc, meta, dist in zip(docs, metas, distances):
                retrieved_docs.append({
                    "content": doc,
                    "metadata": meta,
                    "distance": dist
                })

        # Step 2: Learner-Aware Multi-Factor Reranking (Rerank Top 15 -> Select Top 3)
        reranked_docs = self.reranker.rerank(retrieved_docs, learner_profile, top_k=top_k_final)

        # Step 3: LLM Grounded Answer Generation
        answer, sources, confidence = self.llm.generate_response(query, learner_profile, reranked_docs)

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
                "url": meta.get("course_url", "")
            })

        return RAGResponse(
            answer=answer,
            sources=sources,
            confidence=confidence,
            recommendations=recommendations
        )
