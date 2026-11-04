"""In-memory vector store implementation for testing and development.

This provides a simple, production-ready in-memory vector store using
sentence-transformers for embeddings without requiring external dependencies
like ChromaDB or Qdrant.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .vector_store import Document, QueryResult, VectorStoreBackend


class InMemoryVectorStore(VectorStoreBackend):
    """In-memory vector store using sentence-transformers for embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize in-memory vector store.

        Args:
            model_name: Sentence-transformers model name for embeddings
        """
        self.model_name = model_name
        self._documents: List[Document] = []
        self._embeddings: Optional[List[List[float]]] = None
        self._model = None

    def _load_model(self):
        """Lazy-load the embedding model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for InMemoryVectorStore. "
                    "Install it with: pip install sentence-transformers"
                )

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        self._load_model()
        embedding = self._model.encode(text)
        return embedding.tolist()

    async def add_documents(
        self,
        documents: List[Document],
    ) -> None:
        """Add documents to vector store.

        Args:
            documents: List of Document objects with content and metadata
        """
        for doc in documents:
            # Generate unique ID if not provided
            if doc.id is None:
                doc.id = f"doc_{len(self._documents)}_{hash(doc.content)}"

            self._documents.append(doc)

        # Invalidate cached embeddings
        self._embeddings = None

    def _compute_embeddings(self) -> List[List[float]]:
        """Compute embeddings for all documents."""
        if self._embeddings is None:
            self._load_model()
            texts = [doc.content for doc in self._documents]
            embeddings = self._model.encode(texts)
            self._embeddings = embeddings.tolist()
        return self._embeddings

    async def query(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[QueryResult]:
        """Query vector store for similar documents.

        Args:
            query: Query text
            top_k: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of QueryResult objects with content and scores
        """
        if not self._documents:
            return []

        # Compute query embedding
        query_embedding = self._get_embedding(query)

        # Compute document embeddings
        doc_embeddings = self._compute_embeddings()

        # Compute cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        query_vec = np.array(query_embedding).reshape(1, -1)
        doc_vecs = np.array(doc_embeddings)
        similarities = cosine_similarity(query_vec, doc_vecs)[0]

        # Filter by metadata if provided
        filtered_indices = list(range(len(self._documents)))
        if filter_metadata:
            filtered_indices = [
                i
                for i, doc in enumerate(self._documents)
                if self._matches_metadata(doc.metadata, filter_metadata)
            ]

        # Get top-k results
        top_indices = sorted(
            [(i, similarities[i]) for i in filtered_indices],
            key=lambda x: x[1],
            reverse=True,
        )[:top_k]

        # Build results
        results = []
        for idx, score in top_indices:
            doc = self._documents[idx]
            results.append(
                QueryResult(
                    content=doc.content,
                    score=float(score),
                    metadata=doc.metadata,
                    id=doc.id,
                )
            )

        return results

    def _matches_metadata(
        self, doc_metadata: Optional[Dict[str, Any]], filter_metadata: Dict[str, Any]
    ) -> bool:
        """Check if document metadata matches filter.

        Args:
            doc_metadata: Document metadata
            filter_metadata: Metadata filter criteria

        Returns:
            True if metadata matches all filter criteria
        """
        if doc_metadata is None:
            return not filter_metadata

        for key, value in filter_metadata.items():
            if key not in doc_metadata:
                return False
            if doc_metadata[key] != value:
                return False
        return True

    async def delete(
        self,
        document_ids: List[str],
    ) -> None:
        """Delete documents by ID.

        Args:
            document_ids: List of document IDs to delete
        """
        id_set = set(document_ids)
        self._documents = [doc for doc in self._documents if doc.id not in id_set]
        self._embeddings = None

    async def clear(self) -> None:
        """Clear all documents from the vector store."""
        self._documents = []
        self._embeddings = None

    async def save(self, path: Path) -> None:
        """Save vector store to disk.

        Args:
            path: Path to save directory
        """
        path.mkdir(parents=True, exist_ok=True)

        # Save documents
        docs_data = [
            {"content": doc.content, "metadata": doc.metadata, "id": doc.id}
            for doc in self._documents
        ]
        (path / "documents.json").write_text(json.dumps(docs_data), encoding="utf-8")

    async def load(self, path: Path) -> None:
        """Load vector store from disk.

        Args:
            path: Path to load directory
        """
        docs_file = path / "documents.json"
        if not docs_file.exists():
            return

        docs_data = json.loads(docs_file.read_text(encoding="utf-8"))
        self._documents = [
            Document(
                content=item["content"],
                metadata=item.get("metadata"),
                id=item.get("id"),
            )
            for item in docs_data
        ]
        self._embeddings = None
