# PathAI — RAG & LLM Personalized Learning-Path Engine

Personalized Learning-Path Recommendation and Grounded AI Mentor Module for the **HCLTech AMPlified AIML Challenge**.

---

## 🏗️ Architecture Flow

```text
Learner Profile (Goal, Skills, Level)
       │
       ▼
Goal Skill Engine (data/goal_skills.csv)
       │
       ▼
Skill Gap Analysis
       │
       ▼
Prerequisite Graph (data/skill_prerequisites.csv)
       │
       ▼
Next Target Skill (e.g., Deep Learning)
       │
       ▼
ChromaDB Vector Retrieval (SentenceTransformer all-MiniLM-L6-v2)
       │
       ▼
Learner-Aware Composite Reranker (Target Match 25%, Semantic 25%, Gap 20%, Goal 15%)
       │
       ▼
RecommendationExplainer ("Why Not This Skill?")
       │
       ▼
RAGContextBuilder -> Gemini 2.5 Flash / Local Grounded Mode
       │
       ▼
Personalized Learning Milestones + Course Recommendations + Explanations
```

---

## 🚀 Setup & Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and add your Gemini API Key:
```bash
cp .env.example .env
```
Inside `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Build the Vector Index
```bash
python build_index.py
```

### 4. Run the API Server
```bash
uvicorn main:app --reload --port 8000
```
Interactive Swagger docs will be available at: `http://localhost:8000/docs`

---

## 🔌 API Endpoints for Backend / Frontend Integration

### 1. Chat & Learning-Path Recommendations
- **Endpoint**: `POST /rag/chat`
- **Request Body**:
```json
{
  "query": "What should I learn next?",
  "learner_profile": {
    "goal": "GenAI Engineer",
    "current_skills": ["Python", "Machine Learning"],
    "level": "Intermediate"
  },
  "requested_why_not_skill": "RAG"
}
```
- **Response**:
```json
{
  "answer": "...",
  "recommendations": [
    {
      "course_name": "Neural Networks and Deep Learning",
      "university": "DeepLearning.AI",
      "difficulty": "Beginner",
      "score": 0.7573,
      "why_recommended": [
        "Teaches target next skill: 'Deep Learning'",
        "Matches career goal: GenAI Engineer",
        "Prerequisites are fully satisfied"
      ],
      "url": "https://www.coursera.org/learn/neural-networks-deep-learning"
    }
  ],
  "learning_path": [
    {
      "stage": 1,
      "skill": "deep_learning",
      "display_name": "Deep Learning & Neural Networks",
      "status": "next",
      "prerequisites_met": true
    },
    {
      "stage": 2,
      "skill": "transformers",
      "display_name": "Transformers & Self-Attention",
      "status": "locked",
      "prerequisites_met": false
    }
  ],
  "skill_gaps": ["deep_learning", "transformers", "llm", "generative_ai", "rag", "ai_agents"],
  "next_skill": "deep_learning",
  "why_not_explanation": {
    "requested_skill": "RAG",
    "status": "prerequisite_missing",
    "explanation": "'Rag' was not selected because prerequisite skill(s) [llm] are required first."
  },
  "sources": [
    {
      "course": "Neural Networks and Deep Learning",
      "university": "DeepLearning.AI",
      "url": "https://www.coursera.org/learn/neural-networks-deep-learning"
    }
  ],
  "confidence": 0.90
}
```

### 2. Candidate Retrieval (For Teammates' Recommendation Engine)
- **Endpoint**: `POST /rag/retrieve`
- **Request Body**:
```json
{
  "query": "machine learning courses",
  "top_k": 5,
  "learner_profile": {
    "goal": "AI Engineer",
    "current_skills": ["Python"],
    "level": "Intermediate"
  }
}
```

### 3. Adaptive Learner Feedback Loop
- **Endpoint**: `POST /rag/feedback`
- **Request Body**:
```json
{
  "learner_profile": {
    "goal": "GenAI Engineer",
    "current_skills": ["Python", "Machine Learning"],
    "level": "Intermediate"
  },
  "course_completed": true,
  "completed_skills": ["deep_learning"],
  "feedback_text": "too_easy"
}
```

---

## 🧪 Tests & Evaluation

### Run Test Suite (14 Tests)
```bash
python -m pytest tests/ -v
```

### Run 10-Scenario Benchmark
```bash
python evaluate_rag.py
```
