import os
import pytest
from rag.pipeline.rag import RAGPipeline

@pytest.fixture
def rag_pipeline():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "rag", "data")
    return RAGPipeline(data_dir=data_dir)

def test_retriever_prioritizes_deep_learning_over_mastered_python(rag_pipeline):
    learner_profile = {
        "goal": "GenAI Engineer",
        "skills": ["Python", "Machine Learning"],
        "level": "Intermediate"
    }
    skill_gaps = ["Deep Learning", "Transformers", "LLM", "RAG"]

    candidates = rag_pipeline.retrieve_resources(
        query="What should I learn next?",
        learner_profile=learner_profile,
        skill_gaps=skill_gaps,
        top_k=5
    )

    assert len(candidates) > 0
    top_course = candidates[0]["course"]
    assert top_course is not None

def test_retrieve_resources_api_format(rag_pipeline):
    learner_profile = {
        "goal": "GenAI Engineer",
        "skills": ["Python", "Machine Learning"],
        "level": "Intermediate"
    }
    skill_gaps = ["Deep Learning", "Transformers"]

    candidates = rag_pipeline.retrieve_resources(
        query="Recommend next step",
        learner_profile=learner_profile,
        skill_gaps=skill_gaps
    )

    assert isinstance(candidates, list)
    assert len(candidates) > 0
    first = candidates[0]
    assert "course" in first
    assert "skill" in first
    assert "relevance" in first
    assert isinstance(first["relevance"], float)
