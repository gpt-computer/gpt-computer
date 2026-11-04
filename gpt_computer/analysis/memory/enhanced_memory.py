"""Enhanced memory with RAG capabilities.

This module extends the base memory with retrieval-augmented generation
to provide long-term memory with context-aware retrieval.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .vector_store import Document, RAGPipeline, VectorStoreBackend
from .in_memory_store import InMemoryVectorStore
from ...agent.memory import BaseMemory


class EnhancedMemory(BaseMemory):
    """Enhanced memory with RAG capabilities for long-term context."""

    def __init__(
        self,
        vector_store: Optional[VectorStoreBackend] = None,
        context_documents: int = 3,
    ):
        """Initialize enhanced memory with RAG.

        Args:
            vector_store: Vector store backend (defaults to InMemoryVectorStore)
            context_documents: Number of context documents to retrieve
        """
        super().__init__()
        self.vector_store = vector_store or InMemoryVectorStore()
        self.rag = RAGPipeline(self.vector_store, context_documents)
        self._knowledge_base: Dict[str, Any] = {}

    async def add_to_knowledge_base(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add content to the knowledge base.

        Args:
            content: Content to add
            metadata: Optional metadata for the content

        Returns:
            Document ID
        """
        doc = Document(content=content, metadata=metadata)
        await self.vector_store.add_documents([doc])
        return doc.id

    async def retrieve_context(
        self,
        query: str,
    ) -> str:
        """Retrieve relevant context for a query.

        Args:
            query: Query to retrieve context for

        Returns:
            Formatted context string
        """
        augmented_prompt = await self.rag.augment_prompt(query)
        return augmented_prompt

    async def add_conversation(
        self,
        messages: List[Dict[str, Any]],
    ) -> None:
        """Add conversation to memory and knowledge base.

        Args:
            messages: List of conversation messages
        """
        # Store in base memory
        await super().add_conversation(messages)

        # Also add to knowledge base for RAG
        for msg in messages:
            if msg.get("role") == "assistant":
                await self.add_to_knowledge_base(
                    msg.get("content", ""),
                    metadata={"role": "assistant", "timestamp": msg.get("timestamp")}
                )

    async def get_conversation_context(
        self,
        query: str,
        limit: int = 10,
    ) -> str:
        """Get conversation context with RAG augmentation.

        Args:
            query: Query to retrieve context for
            limit: Number of recent messages to include

        Returns:
            Context string with relevant information
        """
        # Get recent conversation history
        conv = await self.get_conversation(limit=limit)
        
        # Get RAG context
        rag_context = await self.retrieve_context(query)
        
        # Combine contexts
        if conv and rag_context:
            return f"""Recent conversation:
{conv}

Relevant context from knowledge base:
{rag_context}
"""
        elif conv:
            return f"Recent conversation:\n{conv}"
        elif rag_context:
            return f"Relevant context from knowledge base:\n{rag_context}"
        else:
            return ""
