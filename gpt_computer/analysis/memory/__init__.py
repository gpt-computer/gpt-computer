"""Memory and RAG capabilities for gpt-computer.

This package provides:
- Vector store abstraction for RAG
- In-memory vector store implementation
- Enhanced memory with retrieval-augmented generation
"""

from .vector_store import Document, QueryResult, RAGPipeline, VectorStoreBackend
from .in_memory_store import InMemoryVectorStore
from .enhanced_memory import EnhancedMemory

__all__ = [
    "Document",
    "QueryResult",
    "RAGPipeline",
    "VectorStoreBackend",
    "InMemoryVectorStore",
    "EnhancedMemory",
]
