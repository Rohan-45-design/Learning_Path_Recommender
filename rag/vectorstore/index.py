import numpy as np
from typing import List, Tuple, Dict, Any
from rag.ingestion.chunker import DocumentChunk

class VectorIndex:
    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self.embeddings: np.ndarray = np.empty((0, 0), dtype=np.float32)
        self.use_faiss = False
        self.faiss_index = None

    def build_index(self, chunks: List[DocumentChunk], embeddings: np.ndarray):
        self.chunks = chunks
        self.embeddings = embeddings
        dim = embeddings.shape[1] if embeddings.ndim > 1 and embeddings.shape[0] > 0 else 0
        
        if dim > 0:
            try:
                import faiss
                self.faiss_index = faiss.IndexFlatIP(dim)
                self.faiss_index.add(embeddings)
                self.use_faiss = True
            except Exception as e:
                print(f"[VectorIndex] FAISS setup fallback to NumPy cosine similarity: {e}")
                self.use_faiss = False

    def search(self, query_vector: np.ndarray, top_k: int = 10) -> List[Tuple[DocumentChunk, float]]:
        if len(self.chunks) == 0 or self.embeddings.size == 0:
            return []

        if query_vector.ndim == 1:
            query_vector = np.expand_dims(query_vector, axis=0)

        if self.use_faiss and self.faiss_index is not None:
            # Reshape query if dimension mismatch occurs with fallback TF-IDF
            if query_vector.shape[1] != self.faiss_index.d:
                # Fallback to NumPy matrix multiplication cosine similarity
                return self._numpy_search(query_vector, top_k)
            scores, indices = self.faiss_index.search(query_vector, min(top_k, len(self.chunks)))
            results = []
            for idx, score in zip(indices[0], scores[0]):
                if idx < len(self.chunks) and idx >= 0:
                    results.append((self.chunks[idx], float(score)))
            return results
        else:
            return self._numpy_search(query_vector, top_k)

    def _numpy_search(self, query_vector: np.ndarray, top_k: int) -> List[Tuple[DocumentChunk, float]]:
        # Cosine similarity dot product assuming normalized vectors
        if query_vector.shape[1] != self.embeddings.shape[1]:
            # Simple dimension alignment safety
            min_dim = min(query_vector.shape[1], self.embeddings.shape[1])
            q_vec = query_vector[:, :min_dim]
            emb_vec = self.embeddings[:, :min_dim]
        else:
            q_vec = query_vector
            emb_vec = self.embeddings

        scores = np.dot(emb_vec, q_vec.T).squeeze(axis=1)
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append((self.chunks[idx], float(scores[idx])))
        return results
