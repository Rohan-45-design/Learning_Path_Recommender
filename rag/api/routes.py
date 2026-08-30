import os
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from rag.pipeline.rag import RAGPipeline

router = APIRouter(prefix="/rag", tags=["RAG"])

_rag_pipeline: Optional[RAGPipeline] = None

def get_pipeline() -> RAGPipeline:
    global _rag_pipeline
    if _rag_pipeline is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")
        kb_dir = os.path.join(os.path.dirname(base_dir), "knowledge_base")
        _rag_pipeline = RAGPipeline(data_dir=data_dir, kb_dir=kb_dir)
    return _rag_pipeline

class LearnerProfileInput(BaseModel):
    goal: Optional[str] = "GenAI Engineer"
    skills: Optional[List[str]] = None
    current_skills: Optional[List[str]] = None
    level: Optional[str] = "Intermediate"

    def get_profile_dict(self) -> Dict[str, Any]:
        data = self.model_dump(exclude_none=True)
        # Ensure both skills and current_skills keys are harmonized
        skills_list = data.get("current_skills") or data.get("skills") or ["Python", "Machine Learning"]
        data["skills"] = skills_list
        data["current_skills"] = skills_list
        return data

class ChatRequest(BaseModel):
    query: str
    learner_id: Optional[str] = "student_123"
    learner_profile: Optional[LearnerProfileInput] = None
    skill_gaps: Optional[List[str]] = None
    requested_why_not_skill: Optional[str] = None

class RetrieveRequest(BaseModel):
    query: str
    learner_id: Optional[str] = "student_123"
    learner_profile: Optional[LearnerProfileInput] = None
    skill_gaps: Optional[List[str]] = None
    top_k: Optional[int] = 5

class FeedbackRequest(BaseModel):
    learner_profile: LearnerProfileInput
    course_completed: Optional[bool] = False
    completed_skills: Optional[List[str]] = None
    feedback_text: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, str]]
    confidence: float
    recommendations: Optional[List[Dict[str, Any]]] = None
    learning_path: Optional[List[Dict[str, Any]]] = None
    skill_gaps: Optional[List[str]] = None
    next_skill: Optional[str] = None
    why_not_explanation: Optional[Dict[str, Any]] = None

@router.post("/chat", response_model=ChatResponse)
def rag_chat(request: ChatRequest):
    """Main RAG endpoint returning grounded answer, structured recommendations, learning path, and sources."""
    try:
        pipeline = get_pipeline()
        profile_dict = request.learner_profile.get_profile_dict() if request.learner_profile else None
        
        response = pipeline.query(
            query=request.query,
            student_id=request.learner_id,
            learner_profile=profile_dict,
            skill_gaps=request.skill_gaps,
            requested_why_not_skill=request.requested_why_not_skill
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/retrieve")
def rag_retrieve(request: RetrieveRequest):
    """Candidate resource retrieval endpoint for Recommendation Engine (Member 2 & 3)."""
    try:
        pipeline = get_pipeline()
        profile_dict = request.learner_profile.model_dump() if request.learner_profile else None
        
        candidates = pipeline.retrieve_resources(
            query=request.query,
            student_id=request.learner_id,
            learner_profile=profile_dict,
            skill_gaps=request.skill_gaps,
            top_k=request.top_k or 5
        )
        return {"candidates": candidates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
def rag_feedback(request: FeedbackRequest):
    """Adaptive feedback endpoint updating learner profile skills & level."""
    try:
        pipeline = get_pipeline()
        profile_dict = request.learner_profile.model_dump()
        res = pipeline.process_feedback(
            learner_profile=profile_dict,
            course_completed=request.course_completed,
            completed_skills=request.completed_skills,
            feedback_text=request.feedback_text
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def rag_health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "PathAI RAG Engine",
        "vectorstore": "ChromaDB Persistent",
        "learner_db": "OULAD Student State DB"
    }
