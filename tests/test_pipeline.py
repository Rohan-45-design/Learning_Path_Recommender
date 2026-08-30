import os
import pytest
from rag.pipeline.rag import RAGPipeline

@pytest.fixture
def rag_pipeline():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "rag", "data")
    kb_dir = os.path.join(base_dir, "knowledge_base")
    return RAGPipeline(data_dir=data_dir, kb_dir=kb_dir)

def test_recommendation_question_with_oulad_student(rag_pipeline):
    # Query using OULAD student_123 who has mastered Python and Machine Learning
    response = rag_pipeline.query(
        query="What should I learn next?",
        student_id="student_123"
    )
    assert response.answer is not None
    assert len(response.sources) > 0
    assert response.confidence > 0.0

def test_explanation_question(rag_pipeline):
    response = rag_pipeline.query(
        query="Why should I learn Deep Learning next?",
        student_id="student_123"
    )
    assert response.answer is not None
    assert response.confidence > 0.0

def test_learning_concept_question(rag_pipeline):
    response = rag_pipeline.query(
        query="What is backpropagation?",
        student_id="student_456"
    )
    assert response.answer is not None
    assert len(response.sources) > 0

def test_anti_hallucination_unsupported_query(rag_pipeline):
    response = rag_pipeline.query(
        query="How do I bake a chocolate cake?",
        student_id="student_123"
    )
    assert "I don't have enough information in the learning resource database to answer that." in response.answer
    assert len(response.sources) == 0
    assert response.confidence == 0.0
