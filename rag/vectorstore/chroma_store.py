import os
import chromadb
from typing import List, Dict, Any, Optional
from rag.ingestion.chunker import DocumentChunk

class ChromaVectorStore:
    def __init__(self, persist_dir: Optional[str] = None):
        if persist_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            persist_dir = os.path.join(base_dir, "chroma_db_store")
        
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        
        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="learning_resources",
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[DocumentChunk], embeddings: Optional[List[List[float]]] = None):
        if not chunks:
            return

        documents = [c.content for c in chunks]
        ids = [f"{c.doc_type}_{c.doc_id}" for c in chunks]
        
        metadatas = []
        for c in chunks:
            primary_skill = c.skills_covered[0] if c.skills_covered else c.title
            primary_career = c.career_relevance[0] if c.career_relevance else "General"
            prereqs_str = ";".join(c.prerequisites) if c.prerequisites else "None"
            skills_str = ";".join(c.skills_covered) if c.skills_covered else c.title

            metadatas.append({
                "course_id": c.doc_id,
                "title": c.title,
                "skill": primary_skill.lower(),
                "skills_covered": skills_str.lower(),
                "difficulty": c.difficulty.lower(),
                "career": primary_career.lower(),
                "resource_type": c.doc_type.lower(),
                "prerequisites": prereqs_str.lower()
            })

        if embeddings is not None and len(embeddings) == len(documents):
            try:
                self.collection.upsert(
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
                return
            except Exception as e:
                print(f"[ChromaVectorStore] Upsert with custom embeddings failed: {e}")

        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query_similarity(
        self,
        query_text: str,
        query_embedding: Optional[List[float]] = None,
        top_k: int = 10,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        kwargs: Dict[str, Any] = {"n_results": top_k}
        if where_filter:
            kwargs["where"] = where_filter

        if query_embedding is not None:
            try:
                kwargs["query_embeddings"] = [query_embedding]
                results = self.collection.query(**kwargs)
            except Exception:
                kwargs.pop("query_embeddings", None)
                kwargs["query_texts"] = [query_text]
                results = self.collection.query(**kwargs)
        else:
            kwargs["query_texts"] = [query_text]
            results = self.collection.query(**kwargs)
        
        candidates = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
            ids = results["ids"][0] if "ids" in results else [""] * len(docs)

            for doc, meta, dist, doc_id in zip(docs, metas, distances, ids):
                similarity = max(0.01, 1.0 - float(dist)) if dist is not None else 0.80
                candidates.append({
                    "id": doc_id,
                    "content": doc,
                    "metadata": meta,
                    "similarity": round(similarity, 4)
                })
        return candidates
