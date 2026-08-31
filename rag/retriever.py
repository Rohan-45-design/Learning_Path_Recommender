import os
import chromadb
from typing import Dict, Any, Optional, List
from rag.embeddings import EmbeddingModel
from rag.vector_store import CustomEmbeddingAdapter, CourseVectorStore
from rag.load_data import load_courses

class CourseRetriever:
    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "learning_resources"):
        os.makedirs(db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_model = EmbeddingModel()
        self.adapter = CustomEmbeddingAdapter(self.embedding_model)
        
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.adapter
            )
        except Exception:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.adapter
            )

        # Auto-index if collection is empty (e.g. fresh clone / test runner)
        if self.collection.count() == 0:
            csv_path = "data/Coursera.csv"
            if not os.path.exists(csv_path):
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                csv_path = os.path.join(base_dir, "data", "Coursera.csv")
            
            if os.path.exists(csv_path):
                print(f"[CourseRetriever] Auto-indexing courses from {csv_path}...")
                df = load_courses(csv_path)
                store = CourseVectorStore(db_path=db_path, collection_name=collection_name)
                store.add_courses_batch(df)
                self.collection = store.collection

    def retrieve(
        self,
        query: str,
        learner_profile: Optional[Dict[str, Any]] = None,
        skill_gaps: Optional[List[str]] = None,
        next_skill: Optional[str] = None,
        top_k: int = 15
    ) -> Dict[str, Any]:
        search_query = query
        if learner_profile:
            goal = learner_profile.get("goal", "")
            skills_list = learner_profile.get("current_skills", learner_profile.get("skills", []))
            skills_str = ", ".join(skills_list) if isinstance(skills_list, list) else str(skills_list)
            level = learner_profile.get("level", "Intermediate")
            target_skill_str = next_skill if next_skill else (skill_gaps[0] if skill_gaps else "General")

            search_query = f"""
Career Goal: {goal}

Current Skills:
{skills_str}

Learner Level:
{level}

Target Skill:
{target_skill_str}

Question:
{query}
""".strip()

        count = self.collection.count()
        if count == 0:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        actual_k = min(top_k, count)
        query_embedding = self.embedding_model.encode([search_query])[0]
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=actual_k
        )
        return results