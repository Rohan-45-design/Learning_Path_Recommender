from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from rag.vectorstore.index import VectorIndex
from rag.vectorstore.chroma_store import ChromaVectorStore
from rag.embeddings.embedder import EmbeddingGenerator
from rag.ingestion.metadata import MetadataManager
from rag.ingestion.chunker import DocumentChunk

class RetrievalResult(BaseModel):
    doc_id: str
    doc_type: str
    title: str
    content: str
    skills_covered: List[str]
    prerequisites: List[str]
    difficulty: str
    career_relevance: List[str]
    semantic_score: float
    relevance_score: float
    relevance: float
    reasoning: str

class ResourceRetriever:
    def __init__(
        self,
        index: VectorIndex,
        embedder: EmbeddingGenerator,
        metadata_mgr: MetadataManager,
        chroma_store: Optional[ChromaVectorStore] = None
    ):
        self.index = index
        self.embedder = embedder
        self.metadata_mgr = metadata_mgr
        self.chroma_store = chroma_store

    def retrieve_resources(
        self,
        query: str,
        learner_profile: Optional[Dict[str, Any]] = None,
        skill_gaps: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Public candidate retrieval API for Recommendation Engine (Member 2 & 3).
        """
        results = self.retrieve(query=query, learner_profile=learner_profile, skill_gaps=skill_gaps, top_k=top_k)
        candidates = []
        for r in results:
            primary_skill = r.skills_covered[0] if r.skills_covered else r.title
            candidates.append({
                "course": r.title,
                "skill": primary_skill,
                "relevance": round(r.relevance_score, 2),
                "doc_id": r.doc_id,
                "doc_type": r.doc_type,
                "difficulty": r.difficulty,
                "reasoning": r.reasoning,
                "content": r.content
            })
        return candidates

    def retrieve(
        self,
        query: str,
        learner_profile: Optional[Dict[str, Any]] = None,
        skill_gaps: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        Full RAG Retrieval with Query Enrichment -> ChromaDB Vector Similarity -> Metadata Filtering -> Learner Profile & Skill Gap reranking.
        """
        if learner_profile is None:
            learner_profile = {}
        if skill_gaps is None:
            skill_gaps = []

        learner_skills = [s.strip().lower() for s in learner_profile.get("skills", [])]
        learner_goal = learner_profile.get("goal", "").strip().lower()
        learner_level = learner_profile.get("level", "Intermediate").strip().lower()
        gap_set = {s.strip().lower() for s in skill_gaps}

        # Step 1: Contextual Search Query Enrichment
        search_text = query
        if any(term in query.lower() for term in ["next", "recommend", "should i learn", "what to learn", "path"]):
            search_text = f"{query} {learner_goal} {' '.join(skill_gaps)}"

        query_vec = self.embedder.embed_query(search_text)

        # Retrieve candidates from ChromaDB or VectorIndex
        initial_candidates = []
        if self.chroma_store is not None:
            chroma_results = self.chroma_store.query_similarity(
                query_text=search_text,
                query_embedding=query_vec.tolist(),
                top_k=15
            )
            # Map chroma candidates to DocumentChunk structure
            for item in chroma_results:
                meta = item["metadata"]
                prereqs = [p.strip() for p in meta.get("prerequisites", "").split(";") if p.strip() and p.strip() != "none"]
                skills_cov = [s.strip() for s in meta.get("skills_covered", "").split(";") if s.strip()]
                careers = [c.strip() for c in meta.get("career", "").split(";") if c.strip()]

                chunk = DocumentChunk(
                    doc_id=meta.get("course_id", item["id"]),
                    doc_type=meta.get("resource_type", "course"),
                    title=meta.get("title", "Resource"),
                    content=item["content"],
                    skills_covered=skills_cov,
                    prerequisites=prereqs,
                    difficulty=meta.get("difficulty", "Intermediate").capitalize(),
                    career_relevance=careers,
                    duration_hours=20.0,
                    raw_metadata=meta
                )
                initial_candidates.append((chunk, float(item["similarity"])))
        else:
            initial_candidates = self.index.search(query_vec, top_k=15)

        processed_results: List[RetrievalResult] = []

        for chunk, semantic_score in initial_candidates:
            # Step 2: Metadata Filtering & Reranking
            chunk_skills = [s.strip().lower() for s in chunk.skills_covered]
            
            # Check if all skills covered in this resource are already mastered
            all_mastered = len(chunk_skills) > 0 and all(s in learner_skills for s in chunk_skills)
            
            # Calculate prerequisite readiness ratio
            prereq_readiness = self.metadata_mgr.calculate_prerequisite_readiness(
                chunk.prerequisites, learner_skills
            )

            # Skill Gap Overlap score
            gap_overlap = sum(1 for s in chunk_skills if s in gap_set)
            gap_score = (gap_overlap / max(len(chunk_skills), 1)) if chunk_skills else 0.0

            # Career Goal alignment
            career_match = 0.0
            if learner_goal:
                for c in chunk.career_relevance:
                    if learner_goal in c.lower() or c.lower() in learner_goal:
                        career_match = 1.0
                        break

            # Boost / Penalty rules:
            mastery_penalty = 0.50 if all_mastered else 0.0
            skill_gap_boost = 0.25 * gap_score
            prereq_boost = 0.20 * prereq_readiness
            career_boost = 0.15 * career_match

            raw_score = semantic_score + skill_gap_boost + prereq_boost + career_boost - mastery_penalty
            final_relevance = max(0.05, min(0.99, raw_score))

            reasons = []
            if all_mastered:
                reasons.append("Already mastered")
            if gap_score > 0:
                reasons.append("Matches skill gap")
            if prereq_readiness >= 1.0:
                reasons.append("Prerequisites satisfied")
            elif prereq_readiness > 0:
                reasons.append("Partial prerequisites satisfied")
            if career_match > 0:
                reasons.append("Aligns with career goal")

            reasoning_str = "; ".join(reasons) if reasons else "Semantic similarity match"

            processed_results.append(
                RetrievalResult(
                    doc_id=chunk.doc_id,
                    doc_type=chunk.doc_type,
                    title=chunk.title,
                    content=chunk.content,
                    skills_covered=chunk.skills_covered,
                    prerequisites=chunk.prerequisites,
                    difficulty=chunk.difficulty,
                    career_relevance=chunk.career_relevance,
                    semantic_score=float(semantic_score),
                    relevance_score=float(final_relevance),
                    relevance=float(final_relevance),
                    reasoning=reasoning_str
                )
            )

        processed_results.sort(key=lambda x: x.relevance_score, reverse=True)
        return processed_results[:top_k]
