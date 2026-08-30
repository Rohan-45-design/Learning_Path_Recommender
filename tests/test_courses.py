import pytest


def test_health_check(client):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_empty_courses(client):
    """Test GET /courses when database is empty."""
    response = client.get("/courses")
    assert response.status_code == 200
    assert response.json() == []


def test_create_course_success(client):
    """Test creating a course via POST /courses."""
    payload = {
        "course_id": "CS101",
        "title": "Python Programming Fundamentals",
        "provider": "Coursera",
        "description": "Learn syntax, variables, loops, functions, and data structures in Python.",
        "skills_covered": ["Python", "Algorithms"],
        "prerequisites": [],
        "difficulty": "Beginner",
        "est_hours": 12,
    }
    response = client.post("/courses", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["course_id"] == "CS101"
    assert data["title"] == "Python Programming Fundamentals"
    assert data["skills_covered"] == ["Python", "Algorithms"]
    assert data["est_hours"] == 12


def test_create_duplicate_course_error(client):
    """Test creating a course with an existing course_id returns 400."""
    payload = {
        "course_id": "DE101",
        "title": "SQL & Relational Databases",
        "provider": "edX",
        "description": "Master SQL queries, table creation, joins, indexing, and normalization.",
        "skills_covered": ["SQL", "PostgreSQL"],
        "prerequisites": [],
        "difficulty": "Beginner",
        "est_hours": 15,
    }
    res1 = client.post("/courses", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/courses", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_create_course_invalid_payload(client):
    """Test creating a course with missing or invalid fields returns 422."""
    invalid_payload = {
        "course_id": "INV101",
        "provider": "edX",
        "est_hours": -5,
    }
    response = client.post("/courses", json=invalid_payload)
    assert response.status_code == 422


def test_get_course_by_id_success(client):
    """Test GET /courses/{course_id} for existing course."""
    payload = {
        "course_id": "DE103",
        "title": "Real-Time Streaming with Apache Kafka",
        "provider": "Pluralsight",
        "description": "Implement event streaming, producers, consumers, and topic partitioning.",
        "skills_covered": ["Kafka", "Event Streaming", "System Architecture"],
        "prerequisites": ["DE102"],
        "difficulty": "Advanced",
        "est_hours": 25,
    }
    client.post("/courses", json=payload)

    response = client.get("/courses/DE103")
    assert response.status_code == 200
    data = response.json()
    assert data["course_id"] == "DE103"
    assert data["title"] == "Real-Time Streaming with Apache Kafka"
    assert data["difficulty"] == "Advanced"


def test_get_course_by_id_not_found(client):
    """Test GET /courses/{course_id} for non-existent course returns 404."""
    response = client.get("/courses/NONEXISTENT")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_course_success(client):
    """Test PUT /courses/{course_id} updates specified fields."""
    payload = {
        "course_id": "ML101",
        "title": "Applied Machine Learning with Scikit-Learn",
        "provider": "Coursera",
        "description": "Supervised and unsupervised ML models.",
        "skills_covered": ["Python", "Machine Learning"],
        "prerequisites": ["CS101"],
        "difficulty": "Intermediate",
        "est_hours": 15,
    }
    client.post("/courses", json=payload)

    update_payload = {
        "est_hours": 18,
        "skills_covered": ["Python", "Machine Learning", "Scikit-Learn"],
    }
    response = client.put("/courses/ML101", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["est_hours"] == 18
    assert data["skills_covered"] == ["Python", "Machine Learning", "Scikit-Learn"]
    assert data["title"] == "Applied Machine Learning with Scikit-Learn"


def test_update_course_not_found(client):
    """Test PUT /courses/{course_id} for non-existent course returns 404."""
    response = client.put("/courses/NONEXISTENT", json={"title": "New Title"})
    assert response.status_code == 404


def test_delete_course_success(client):
    """Test DELETE /courses/{course_id} removes the course."""
    payload = {
        "course_id": "DEL101",
        "title": "Delete Target",
        "provider": "Provider",
        "description": "Target for deletion",
        "skills_covered": [],
        "prerequisites": [],
        "difficulty": "Beginner",
        "est_hours": 5,
    }
    client.post("/courses", json=payload)

    del_res = client.delete("/courses/DEL101")
    assert del_res.status_code == 200
    assert del_res.json()["course_id"] == "DEL101"

    get_res = client.get("/courses/DEL101")
    assert get_res.status_code == 404


def test_delete_course_not_found(client):
    """Test DELETE /courses/{course_id} for non-existent course returns 404."""
    response = client.delete("/courses/NONEXISTENT")
    assert response.status_code == 404
