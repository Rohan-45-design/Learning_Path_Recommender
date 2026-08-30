import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/rag/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "ok"

def test_chat_endpoint():
    payload = {
        "query": "What should I learn next?",
        "learner_id": "user_456",
        "learner_profile": {
            "goal": "GenAI Engineer",
            "skills": ["Python", "Machine Learning"],
            "level": "Intermediate"
        },
        "skill_gaps": ["Deep Learning", "Transformers", "LLM", "RAG"]
    }
    response = client.post("/rag/chat", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert "answer" in json_data
    assert "sources" in json_data
    assert "confidence" in json_data
    assert isinstance(json_data["confidence"], float)

def test_retrieve_endpoint():
    payload = {
        "query": "Recommend candidate resources",
        "learner_profile": {
            "goal": "AI Engineer",
            "skills": ["Python", "Machine Learning"],
            "level": "Intermediate"
        },
        "skill_gaps": ["Deep Learning", "Transformers"],
        "top_k": 3
    }
    response = client.post("/rag/retrieve", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert "candidates" in json_data
    assert len(json_data["candidates"]) > 0
    first = json_data["candidates"][0]
    assert "course" in first
    assert "skill" in first
    assert "relevance" in first
