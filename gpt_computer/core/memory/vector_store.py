from pathlib import Path
from typing import Any, Dict, List, Optional

import faiss
import numpy as np

from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_queries(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(texts)

    def embed_documents(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(texts)


class VectorStore:
    def __init__(self, path: Path, embedding_model: Optional[EmbeddingModel] = None):
        self.path = path / "vector_store"
        self.path.mkdir(parents=True, exist_ok=True)
        self.embedding_model = embedding_model or EmbeddingModel()
        self.index_file = self.path / "index.faiss"
        self.metadata_file = self.path / "metadata.json"

        self.index = None
        self.metadata: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if self.index_file.exists():
            self.index = faiss.read_index(str(self.index_file))
            import json

            if self.metadata_file.exists():
                with open(self.metadata_file, "r") as f:
                    self.metadata = json.load(f)

    def _save(self):
        if self.index:
            faiss.write_index(self.index, str(self.index_file))
            import json

            with open(self.metadata_file, "w") as f:
                json.dump(self.metadata, f)

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        embeddings = self.embedding_model.embed_documents(texts)
        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)

        self.index.add(embeddings.astype("float32"))
        self.metadata.extend(metadatas)
        self._save()

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if self.index is None:
            return []

        query_embedding = self.embedding_model.embed_queries([query])
        distances, indices = self.index.search(query_embedding.astype("float32"), top_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result["distance"] = float(dist)
                results.append(result)
        return results
