from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from rag.pipeline.rag import RAGResponse


@pytest.fixture
def mock_rag_pipeline():
    """Mock RAGPipeline to test endpoints without requiring real Gemini API calls or heavy models."""
    mock_pipeline = MagicMock()
    mock_response = RAGResponse(
        answer="Based on your goal to become a GenAI Engineer, start with Deep Learning foundations.",
        sources=[
            {
                "course": "Deep Learning Specialization",
                "university": "DeepLearning.AI",
                "url": "https://coursera.org/specializations/deep-learning"
            }
        ],
        confidence=0.95,
        recommendations=[
            {
                "course_name": "Deep Learning Specialization",
                "university": "DeepLearning.AI",
                "difficulty": "Intermediate",
                "score": 0.92,
                "skill_gap_score": 1.0,
                "novelty_score": 0.8,
                "prereq_violations": 0,
                "target_match_score": 1.0,
                "url": "https://coursera.org/specializations/deep-learning",
                "why_recommended": ["Matches next target skill"]
            }
        ],
        learning_path=[
            {
                "milestone": 1,
                "skill": "Deep Learning",
                "description": "Core neural network architectures"
            }
        ],
        skill_gaps=["Deep Learning", "Transformers", "RAG"],
        next_skill="Deep Learning",
        why_not_explanation={
            "requested_skill": "RAG",
            "eligible": False,
            "missing_prerequisites": ["Deep Learning"],
            "explanation": "You should master Deep Learning before advancing to RAG."
        }
    )
    mock_pipeline.query.return_value = mock_response
    mock_pipeline.retrieve_resources.return_value = [
        {
            "course": "Deep Learning Specialization",
            "skill": "Deep Learning",
            "university": "DeepLearning.AI",
            "difficulty": "Intermediate",
            "relevance": 0.92,
            "skills": "Deep Learning, PyTorch",
            "url": "https://coursera.org/specializations/deep-learning",
            "why_recommended": ["Matches next target skill"]
        }
    ]
    mock_pipeline.process_feedback.return_value = {
        "status": "updated",
        "updated_skills": ["Python", "Machine Learning", "Deep Learning"],
        "level": "Advanced",
        "feedback_received": "Great course!"
    }
    return mock_pipeline


def test_rag_chat_endpoint(client, mock_rag_pipeline):
    """Test POST /rag/chat with mock RAGPipeline."""
    payload = {
        "query": "What should I learn next?",
        "learner_profile": {
            "goal": "GenAI Engineer",
            "current_skills": ["Python", "Machine Learning"],
            "level": "Intermediate"
        },
        "requested_why_not_skill": "RAG"
    }

    with patch("rag.api.routes.get_pipeline", return_value=mock_rag_pipeline):
        response = client.post("/rag/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert data["answer"].startswith("Based on your goal")
        assert "sources" in data
        assert len(data["sources"]) == 1
        assert data["sources"][0]["course"] == "Deep Learning Specialization"
        assert data["confidence"] == 0.95
        assert data["next_skill"] == "Deep Learning"
        assert data["why_not_explanation"]["requested_skill"] == "RAG"
        assert data["why_not_explanation"]["missing_prerequisites"] == ["Deep Learning"]

        # Verify mock call parameters
        mock_rag_pipeline.query.assert_called_once()
        call_kwargs = mock_rag_pipeline.query.call_args[1]
        assert call_kwargs["query"] == "What should I learn next?"
        assert call_kwargs["requested_why_not_skill"] == "RAG"
        assert "current_skills" in call_kwargs["learner_profile"]


def test_rag_retrieve_endpoint(client, mock_rag_pipeline):
    """Test POST /rag/retrieve candidate resource retrieval."""
    payload = {
        "query": "Machine learning courses",
        "learner_profile": {
            "goal": "AI Engineer",
            "current_skills": ["Python"],
            "level": "Beginner"
        },
        "top_k": 3
    }

    with patch("rag.api.routes.get_pipeline", return_value=mock_rag_pipeline):
        response = client.post("/rag/retrieve", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "candidates" in data
        assert len(data["candidates"]) == 1
        assert data["candidates"][0]["course"] == "Deep Learning Specialization"


def test_rag_feedback_endpoint(client, mock_rag_pipeline):
    """Test POST /rag/feedback adaptive learner update."""
    payload = {
        "learner_profile": {
            "goal": "AI Engineer",
            "current_skills": ["Python", "Machine Learning"],
            "level": "Intermediate"
        },
        "course_completed": True,
        "completed_skills": ["Deep Learning"],
        "feedback_text": "Great course!"
    }

    with patch("rag.api.routes.get_pipeline", return_value=mock_rag_pipeline):
        response = client.post("/rag/feedback", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"
        assert "Deep Learning" in data["updated_skills"]


def test_rag_health_endpoint(client):
    """Test GET /rag/health endpoint."""
    response = client.get("/rag/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
