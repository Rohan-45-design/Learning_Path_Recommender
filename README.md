# PathAI — Personalized Learning-Path Recommender & Grounded AI Mentor

> **HCLTech AMPlified AIML Challenge — RAG & Generative AI Module**
> 
> *PathAI is not a generic course search engine. It is a deterministic reasoning and grounded Generative AI engine that answers:*
> **"Given where the learner is today and where they want to go, what should they learn next, in what exact sequence, and why?"**

---

## 🏛️ End-to-End System Architecture

```text
                                  LEARNER PROFILE
                        (Career Goal, Current Skills, Level)
                                         │
                                         ▼
                             ┌───────────────────────┐
                             │   Goal Skill Engine   │
                             │ (data/goal_skills.csv)│
                             └───────────┬───────────┘
                                         │
                                         ▼
                             ┌───────────────────────┐
                             │  Skill Gap Analysis   │
                             │  (Required - Current) │
                             └───────────┬───────────┘
                                         │
                                         ▼
                             ┌───────────────────────┐
                             │  Prerequisite Graph   │
                             │ (skill_prerequisites) │
                             └───────────┬───────────┘
                                         │
                                         ▼
                             ┌───────────────────────┐
                             │   Next Target Skill   │
                             │ (e.g., deep_learning) │
                             └───────────┬───────────┘
                                         │
                                         ▼
                             ┌───────────────────────┐
                             │   Query Enrichment    │
                             │ ("Target Skill: DL")  │
                             └───────────┬───────────┘
                                         │
                                         ▼
                             ┌───────────────────────┐
                             │ Sentence Transformer  │
                             │  (all-MiniLM-L6-v2)   │
                             └───────────┬───────────┘
                                         │
                                         ▼
                             ┌───────────────────────┐
                             │  ChromaDB Vector Store│
                             │(1,109 Coursera Courses│
                             └───────────┬───────────┘
                                         │ Top 15 Candidates
                                         ▼
                             ┌───────────────────────┐
                             │ Learner-Aware Reranker│
                             │• Target Match (25%)   │
                             │• Semantic Sim (25%)   │
                             │• Skill Gap (20%)      │
                             │• Goal Match (15%)     │
                             │• Novelty (10%)        │
                             │• Difficulty (5%)      │
                             └───────────┬───────────┘
                                         │ Top 3 Reranked
                                         ▼
                             ┌───────────────────────┐
                             │RecommendationExplainer│
                             │("Why Not RAG Yet?")   │
                             └───────────┬───────────┘
                                         │
                                         ▼
                             ┌───────────────────────┐
                             │   RAGContextBuilder   │
                             │(Grounding & Guardrails│
                             └───────────┬───────────┘
                                         │
                                         ▼
                             ┌───────────────────────┐
                             │   Gemini 2.5 Flash    │
                             │    (Google GenAI)     │
                             └───────────┬───────────┘
                                         │
                                         ▼
                        PERSONALIZED AI MENTOR RESPONSE
                        • Natural-Language Grounded Answer
                        • Structured Milestone Roadmap
                        • Top Course Recommendations with "Why"
                        • Cited Direct URLs
                                         │
                                         ▼
                                 Learner Feedback
                             (Course Completed / Easy)
                                         │
                                         └────────────────► Dynamic Profile Update
```

---

## 🎯 Separation of Responsibilities

| Subsystem | Component | Core Responsibility |
| :--- | :--- | :--- |
| **Domain KB** | `data/goal_skills.csv` | Defines skills required for career goals (GenAI, AI Engineer, Data Scientist, etc.) |
| **Skill Engine** | `rag/goal_engine.py` | Calculates missing skills between current learner knowledge and career goal |
| **Prerequisites**| `rag/prerequisites.py` | Enforces strict dependency sequencing (`Python` $\rightarrow$ `ML` $\rightarrow$ `Deep Learning` $\rightarrow$ `Transformers` $\rightarrow$ `LLM` $\rightarrow$ `RAG`) |
| **Vector DB** | `ChromaDB` + `SentenceTransformer` | Indexes 1,109 Coursera courses and retrieves dense semantic candidates |
| **Reranker** | `rag/reranker.py` | Computes multi-factor composite ranking prioritizing the calculated target next skill |
| **Explainability**| `rag/explainability.py` | Answers transparent *"Why not course/skill X yet?"* questions |
| **Context Builder**| `rag/context_builder.py` | Assembles anti-hallucination grounded prompts |
| **Generative LLM**| **Gemini 2.5 Flash** | Synthesizes conversational, grounded explanations and cited links |
| **Feedback Loop** | `rag/feedback.py` | Adapts learner profile skills and level dynamically upon completion |

---

## 🚀 Setup & Local Installation

### 1. Clone & Install Dependencies
```bash
git clone -b feat/rag-llm-engine https://github.com/Rohan-45-design/Learning_Path_Recommender.git
cd Learning_Path_Recommender

pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and add your Google Gemini API Key:
```bash
cp .env.example .env
```
Inside `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Build Vector Index (Takes ~15 seconds)
```bash
python build_index.py
```

### 4. Start the FastAPI Server
```bash
uvicorn main:app --reload --port 8000
```
Swagger UI documentation is available at: **`http://localhost:8000/docs`**

---

## 🔌 Communication Guide for Backend & Frontend Developers

### 1. Primary Recommendation & Chat Endpoint (`POST /rag/chat`)

This is the main endpoint used by the **Frontend Chat / Recommendation View**.

#### Request:
- **URL**: `http://localhost:8000/rag/chat`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Payload**:
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

#### Response:
```json
{
  "answer": "Based on your goal to become a GenAI Engineer and your current skills, the next logical step in your learning path is to acquire foundational knowledge in Deep Learning...",
  "recommendations": [
    {
      "course_name": "TensorFlow for AI: Computer Vision Basics",
      "university": "Coursera Project Network",
      "difficulty": "Advanced",
      "score": 0.6611,
      "why_recommended": [
        "Teaches target next skill: 'Deep Learning'",
        "Matches career goal: GenAI Engineer",
        "Fills target goal skill gap: deep_learning",
        "Prerequisite dependencies are fully satisfied"
      ],
      "url": "https://www.coursera.org/learn/tensorflow-for-ai-computer-vision-basics"
    },
    {
      "course_name": "Neural Networks and Deep Learning",
      "university": "DeepLearning.AI",
      "difficulty": "Beginner",
      "score": 0.6273,
      "why_recommended": [
        "Teaches target next skill: 'Deep Learning'",
        "Matches career goal: GenAI Engineer",
        "Fills target goal skill gap: deep_learning",
        "Beginner content is suitable because Deep Learning is your next missing foundational skill"
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
    },
    {
      "stage": 3,
      "skill": "llm",
      "display_name": "Large Language Models (LLMs)",
      "status": "locked",
      "prerequisites_met": false
    },
    {
      "stage": 4,
      "skill": "generative_ai",
      "display_name": "Generative AI",
      "status": "locked",
      "prerequisites_met": false
    },
    {
      "stage": 5,
      "skill": "rag",
      "display_name": "Retrieval-Augmented Generation (RAG)",
      "status": "locked",
      "prerequisites_met": false
    }
  ],
  "skill_gaps": [
    "deep_learning",
    "transformers",
    "llm",
    "generative_ai",
    "rag",
    "ai_agents"
  ],
  "next_skill": "deep_learning",
  "why_not_explanation": {
    "requested_skill": "RAG",
    "status": "prerequisite_missing",
    "explanation": "'Rag' was not selected as your immediate next step because prerequisite skill(s) [llm] are required first. Your current recommended next step is 'Deep Learning'."
  },
  "sources": [
    {
      "course": "TensorFlow for AI: Computer Vision Basics",
      "university": "Coursera Project Network",
      "url": "https://www.coursera.org/learn/tensorflow-for-ai-computer-vision-basics"
    }
  ],
  "confidence": 0.90
}
```

---

### 2. Candidate Retrieval Endpoint (`POST /rag/retrieve`)

Used by the **Backend recommendation pipeline** when candidate resources are needed for downstream scoring or knowledge graph traversal.

#### Request:
```json
{
  "query": "deep learning neural networks",
  "top_k": 5,
  "learner_profile": {
    "goal": "AI Engineer",
    "current_skills": ["Python", "Machine Learning"],
    "level": "Intermediate"
  }
}
```

#### Response:
Returns a list of candidate course objects with course name, university, difficulty, match relevance score, and verified Coursera URL.

---

### 3. Adaptive Feedback Endpoint (`POST /rag/feedback`)

Called when a learner clicks **"Mark as Completed"** or provides difficulty feedback on the UI.

#### Request:
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

#### Response:
```json
{
  "updated_profile": {
    "goal": "GenAI Engineer",
    "current_skills": ["Python", "Machine Learning", "deep_learning"],
    "level": "Advanced"
  },
  "action_taken": "Added 1 skills to profile; Increased difficulty level to Advanced",
  "next_recommended_query": "What should I learn next after deep_learning?"
}
```

---

## 🎨 How Frontend Developers Render the UI

The response object from `/rag/chat` maps directly to modern UI components:

```text
┌────────────────────────────────────────────────────────────────────────┐
│  AI MENTOR CHAT                                                        │
│  "Based on your Python & ML background, your next step is Deep Learning│
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│  LEARNING ROADMAP                                                      │
│  🟢 Stage 1: Deep Learning [NEXT STEP]                                 │
│  🔒 Stage 2: Transformers  [LOCKED]                                    │
│  🔒 Stage 3: LLMs          [LOCKED]                                    │
│  🔒 Stage 4: Generative AI [LOCKED]                                    │
│  🔒 Stage 5: RAG           [LOCKED]                                    │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│  TOP RECOMMENDED COURSES                                               │
│  1. TensorFlow for AI: Computer Vision Basics (Coursera Project Net)   │
│     • Teaches target next skill: Deep Learning                         │
│     • Matches career goal: GenAI Engineer                              │
│     • Prerequisites are fully satisfied                                │
│     [Enroll on Coursera ->]                                            │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│  EXPLAINABILITY MODAL: "Why can't I learn RAG now?"                    │
│  Status: Prerequisite Missing                                          │
│  Reason: RAG requires LLM knowledge first.                             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 💻 Integration Code Snippets

### Python (Backend Service Call)
```python
import requests

payload = {
    "query": "What should I learn next?",
    "learner_profile": {
        "goal": "GenAI Engineer",
        "current_skills": ["Python", "Machine Learning"],
        "level": "Intermediate"
    },
    "requested_why_not_skill": "RAG"
}

response = requests.post("http://localhost:8000/rag/chat", json=payload)
data = response.json()

print("Mentor Answer:", data["answer"])
print("Target Next Skill:", data["next_skill"])
print("Top Course:", data["recommendations"][0]["course_name"])
```

### TypeScript / React / Next.js (Frontend Call)
```typescript
import axios from 'axios';

interface RAGChatResponse {
  answer: string;
  next_skill: string;
  recommendations: Array<{
    course_name: string;
    university: string;
    difficulty: string;
    score: number;
    why_recommended: string[];
    url: string;
  }>;
  learning_path: Array<{
    stage: number;
    skill: string;
    display_name: string;
    status: 'next' | 'locked' | 'ready' | 'completed';
    prerequisites_met: boolean;
  }>;
  why_not_explanation?: {
    requested_skill: string;
    status: string;
    explanation: string;
  };
}

export async function fetchLearningPath(query: string, goal: string, skills: string[]) {
  const response = await axios.post<RAGChatResponse>('http://localhost:8000/rag/chat', {
    query,
    learner_profile: {
      goal,
      current_skills: skills,
      level: 'Intermediate'
    },
    requested_why_not_skill: 'RAG'
  });
  return response.data;
}
```

---

## 🧪 Comprehensive Evaluation Benchmark (10 Scenarios)

Run the evaluation benchmark:
```bash
python evaluate_rag.py
```

### Measured Benchmark Results:
- **Prerequisite Violation Rate**: **0.00%** (Strict sequence enforcement)
- **Target Skill Hit Rate @ Top-1**: **50.0%** (Top recommendation directly teaches missing milestone)
- **Average NDCG@3**: **0.56**
- **Average Precision@3**: **0.53**
- **Average Query Latency**: **26.2 ms** (Ultra-low latency execution)

---

## ✅ Automated Unit Tests (14 Tests)

Run the pytest test suite:
```bash
python -m pytest tests/ -v
```
Output:
```text
============================= 14 passed in 41.80s =============================
```
