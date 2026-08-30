import os
import shutil
import chromadb
from chromadb import EmbeddingFunction
from typing import Dict, Any, List
from rag.chunking import create_course_document
from rag.embeddings import EmbeddingModel
from rag.skill_normalizer import normalize_skills

class CustomEmbeddingAdapter(EmbeddingFunction):
    def __init__(self, embedder: EmbeddingModel):
        self.embedder = embedder

    def name(self) -> str:
        return "sentence_transformers_adapter"

    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.embedder.encode(input)

class CourseVectorStore:
    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "learning_resources", reset_if_needed: bool = False):
        if reset_if_needed and os.path.exists(db_path):
            try:
                shutil.rmtree(db_path)
            except Exception as e:
                print(f"[CourseVectorStore] DB reset warning: {e}")

        os.makedirs(db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_model = EmbeddingModel()
        self.adapter = CustomEmbeddingAdapter(self.embedding_model)

        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
                embedding_function=self.adapter
            )
        except Exception:
            try:
                self.client.delete_collection(name=collection_name)
            except Exception:
                pass
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
                embedding_function=self.adapter
            )

    def add_courses_batch(self, df, batch_size: int = 200):
        documents = [create_course_document(row) for _, row in df.iterrows()]
        ids = [str(row["course_id"]) for _, row in df.iterrows()]
        embeddings = self.embedding_model.encode(documents)
        
        metadatas = []
        for _, row in df.iterrows():
            rating_val = float(row["course_rating"]) if row["course_rating"] == row["course_rating"] else 0.0
            norm_skills = "|".join(normalize_skills(row["skills"]))

            metadatas.append({
                "course_name": str(row["course_name"]),
                "university": str(row["university"]),
                "difficulty": str(row["difficulty_level"]),
                "rating": float(rating_val),
                "skills": str(row["skills"]),
                "normalized_skills": norm_skills,
                "course_url": str(row["course_url"])
            })

        total = len(ids)
        for i in range(0, total, batch_size):
            end_idx = min(i + batch_size, total)
            self.collection.upsert(
                ids=ids[i:end_idx],
                documents=documents[i:end_idx],
                embeddings=embeddings[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )
