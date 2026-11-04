"""Vector Store Abstraction for RAG

This module provides an abstract interface for vector store backends
to support Retrieval-Augmented Generation (RAG) capabilities.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypedDict
from dataclasses import dataclass


@dataclass
class Document:
    """A document with content and optional metadata."""

    content: str
    metadata: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


@dataclass
class QueryResult:
    """Result from a vector store query."""

    content: str
    score: float
    metadata: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


class VectorStoreBackend(ABC):
    """Abstract interface for vector store backends."""

    @abstractmethod
    async def add_documents(
        self,
        documents: List[Document],
    ) -> None:
        """Add documents to vector store.

        Args:
            documents: List of Document objects with content and metadata
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def delete(
        self,
        document_ids: List[str],
    ) -> None:
        """Delete documents by ID.

        Args:
            document_ids: List of document IDs to delete
        """
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all documents from the vector store."""
        pass


class RAGPipeline:
    """Retrieval-augmented generation pipeline."""

    def __init__(self, vector_store: VectorStoreBackend, context_documents: int = 3):
        """Initialize RAG pipeline.

        Args:
            vector_store: Vector store backend instance
            context_documents: Number of context documents to retrieve
        """
        self.vector_store = vector_store
        self.context_documents = context_documents

    async def augment_prompt(
        self,
        prompt: str,
    ) -> str:
        """Augment prompt with relevant context from vector store.

        Args:
            prompt: Original user prompt

        Returns:
            Augmented prompt with context from knowledge base
        """
        # Retrieve relevant documents
        results = await self.vector_store.query(prompt, top_k=self.context_documents)

        if not results:
            return prompt

        # Build augmented prompt
        context = self._format_context(results)
        augmented = f"""Context from knowledge base:
{context}

User request:
{prompt}
"""
        return augmented

    def _format_context(self, results: List[QueryResult]) -> str:
        """Format retrieved documents for LLM.

        Args:
            results: List of QueryResult objects

        Returns:
            Formatted context string
        """
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"[Document {i} - Score: {result.score:.2f}]")
            formatted.append(result.content)
            if result.metadata:
                formatted.append(f"Metadata: {result.metadata}")
            formatted.append("")  # Empty line between documents
        return "\n".join(formatted)
