import numpy as np
from typing import List

class EmbeddingGenerator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.use_st = False
        self.st_model = None
        self.is_fitted = False
        
        # Initialize fast, robust TF-IDF embedding generator by default
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, 128), dtype=np.float32)

        if not self.is_fitted:
            matrix = self.vectorizer.fit_transform(texts)
            self.is_fitted = True
        else:
            matrix = self.vectorizer.transform(texts)
        
        arr = matrix.toarray().astype(np.float32)
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        return (arr / norms).astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        embeddings = self.embed_texts([query])
        return embeddings[0]
