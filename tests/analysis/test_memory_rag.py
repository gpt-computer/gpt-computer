"""Tests for vector store and RAG functionality."""

import pytest
import asyncio
from gpt_computer.analysis.memory import (
    Document,
    QueryResult,
    RAGPipeline,
    VectorStoreBackend,
    InMemoryVectorStore,
    EnhancedMemory,
)


class TestInMemoryVectorStore:
    """Test in-memory vector store implementation."""

    @pytest.mark.asyncio
    async def test_add_and_query_documents(self):
        """Test adding documents and querying."""
        store = InMemoryVectorStore()
        
        # Add documents
        docs = [
            Document(content="Python is a programming language", metadata={"category": "code"}),
            Document(content="JavaScript is used for web development", metadata={"category": "code"}),
            Document(content="Machine learning is a subset of AI", metadata={"category": "ai"}),
        ]
        await store.add_documents(docs)
        
        # Query
        results = await store.query("programming languages", top_k=2)
        assert len(results) == 2
        assert all(isinstance(r, QueryResult) for r in results)
        assert all(r.score >= 0 for r in results)

    @pytest.mark.asyncio
    async def test_query_with_metadata_filter(self):
        """Test querying with metadata filters."""
        store = InMemoryVectorStore()
        
        docs = [
            Document(content="Python code", metadata={"category": "code", "language": "python"}),
            Document(content="JavaScript code", metadata={"category": "code", "language": "javascript"}),
        ]
        await store.add_documents(docs)
        
        # Query with filter
        results = await store.query(
            "code",
            filter_metadata={"language": "python"}
        )
        assert len(results) == 1
        assert results[0].metadata["language"] == "python"

    @pytest.mark.asyncio
    async def test_delete_documents(self):
        """Test deleting documents."""
        store = InMemoryVectorStore()
        
        docs = [
            Document(content="Document 1", id="doc1"),
            Document(content="Document 2", id="doc2"),
        ]
        await store.add_documents(docs)
        
        # Delete one
        await store.delete(["doc1"])
        
        # Query should only return doc2
        results = await store.query("Document", top_k=10)
        assert len(results) == 1
        assert results[0].id == "doc2"

    @pytest.mark.asyncio
    async def test_clear_store(self):
        """Test clearing the store."""
        store = InMemoryVectorStore()
        
        docs = [Document(content="Test", id="test")]
        await store.add_documents(docs)
        
        assert len(await store.query("Test", top_k=10)) == 1
        
        await store.clear()
        
        assert len(await store.query("Test", top_k=10)) == 0


class TestRAGPipeline:
    """Test RAG pipeline."""

    @pytest.mark.asyncio
    async def test_augment_prompt(self):
        """Test prompt augmentation with context."""
        store = InMemoryVectorStore()
        
        docs = [
            Document(content="Python uses indentation for code blocks"),
            Document(content="JavaScript uses curly braces for code blocks"),
        ]
        await store.add_documents(docs)
        
        rag = RAGPipeline(store, context_documents=2)
        augmented = await rag.augment_prompt("How do I write code blocks?")
        
        assert "Context from knowledge base" in augmented
        assert "Python" in augmented
        assert "JavaScript" in augmented

    @pytest.mark.asyncio
    async def test_empty_store_query(self):
        """Test RAG with empty vector store."""
        store = InMemoryVectorStore()
        rag = RAGPipeline(store)
        
        augmented = await rag.augment_prompt("Test query")
        
        # Should return original prompt if no context
        assert augmented == "Test query"


class TestEnhancedMemory:
    """Test enhanced memory with RAG."""

    @pytest.mark.asyncio
    async def test_add_to_knowledge_base(self):
        """Test adding content to knowledge base."""
        memory = EnhancedMemory()
        
        doc_id = await memory.add_to_knowledge_base(
            "FastAPI is a modern Python web framework",
            metadata={"category": "framework", "language": "python"}
        )
        
        assert doc_id is not None
        assert doc_id.startswith("doc_")

    @pytest.mark.asyncio
    async def test_retrieve_context(self):
        """Test retrieving context from knowledge base."""
        memory = EnhancedMemory()
        
        await memory.add_to_knowledge_base(
            "FastAPI is a modern Python web framework",
            metadata={"category": "framework"}
        )
        
        context = await memory.retrieve_context("web frameworks")
        
        assert "FastAPI" in context
        assert "knowledge base" in context

    @pytest.mark.asyncio
    async def test_conversation_with_rag(self):
        """Test storing conversation with RAG."""
        memory = EnhancedMemory()
        
        messages = [
            {"role": "user", "content": "What is FastAPI?"},
            {"role": "assistant", "content": "FastAPI is a modern Python web framework for building APIs"},
        ]
        
        await memory.add_conversation(messages)
        
        # Should retrieve context about FastAPI
        context = await memory.get_conversation_context("web frameworks")
        assert "FastAPI" in context
