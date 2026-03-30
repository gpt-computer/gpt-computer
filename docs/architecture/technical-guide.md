# Technical Implementation Guide

## Developer Quick Start for Feature Implementation

This guide helps developers understand how to implement the 10 new features in phases.

---

## Table of Contents
1. [Environment Setup](#environment-setup)
2. [Phase 1: Async Migration](#phase-1-async-migration)
3. [Phase 2: Knowledge Integration](#phase-2-knowledge-integration)
4. [Phase 3: UX Enhancements](#phase-3-ux-enhancements)
5. [Phase 4: Reliability](#phase-4-reliability)
6. [Testing Guide](#testing-guide)
7. [Deployment Strategy](#deployment-strategy)

---

## Environment Setup

### Prerequisites
```bash
# Python 3.10+
python --version

# Install dev dependencies
poetry install --with dev

# Install additional development tools for Phase 1
poetry add -D pytest-asyncio pytest-cov pytest-xdist aiodebug
```

### Development Setup
```bash
# Create feature branch
git checkout -b feature/async-migration

# Setup pre-commit hooks (for code quality)
pre-commit install

# Run tests to ensure baseline
pytest tests/ -v --cov=gpt_computer
```

### IDE Configuration

#### VS Code
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python",
    "editor.formatOnPasteEnabled": true
  }
}
```

#### PyCharm
```
Settings → Project → Python Interpreter → [Select poetry environment]
Settings → Tools → Python Integrated Tools → Default Test Runner → pytest
```

---

## Phase 1: Async Migration

### 1.1 Understand Current Architecture

**Current Flow** (synchronous):
```
CLI Input → Typer → AI.generate() → OpenAI API → Response
                      ↓
                  synchronous I/O
                      ↓
                   blocks other requests
```

**Target Flow** (asynchronous):
```
CLI Input → asyncio.run() → AsyncAI.generate() → AsyncOpenAI → Response
                ↑                                      ↑
      Handle multiple                            non-blocking I/O
      concurrently                              supports 10+ concurrent

```

### 1.2 Implement AsyncAI Module

**Step 1: Create new async wrapper**
```bash
touch gpt_computer/core/ai_async.py
```

**Step 2: Implement AsyncAI class**
```python
# gpt_computer/core/ai_async.py
import asyncio
from typing import Optional, Dict, List
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import structlog

log = structlog.get_logger(__name__)

class AsyncAI:
    """Async LLM interface."""

    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
    ):
        self.model = model
        self.temperature = temperature

        if "gpt" in model.lower():
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
            self.provider = "openai"
        elif "claude" in model.lower():
            self.client = AsyncAnthropic(api_key=api_key)
            self.provider = "anthropic"
        else:
            raise ValueError(f"Unknown model: {model}")

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> str:
        """Generate text asynchronously."""
        temp = temperature or self.temperature

        log.info(
            "llm_request_start",
            model=self.model,
            prompt_length=len(prompt),
            max_tokens=max_tokens,
        )

        try:
            if self.provider == "openai":
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temp,
                )
                return response.choices[0].message.content

            elif self.provider == "anthropic":
                response = await self.client.messages.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temp,
                )
                return response.content[0].text

        except Exception as e:
            log.error("llm_request_failed", error=str(e), model=self.model)
            raise

    async def generate_stream(
        self,
        prompt: str,
        max_tokens: int = 4096,
    ):
        """Generate text with streaming."""
        if self.provider == "openai":
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        elif self.provider == "anthropic":
            async with self.client.messages.stream(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            ) as stream:
                async for text in stream.text_stream:
                    yield text

    async def count_tokens(self, text: str) -> int:
        """Count tokens (implementation depends on provider)."""
        if self.provider == "openai":
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model)
            return len(encoding.encode(text))

        # Anthropic: approximate (1 token ≈ 4 chars)
        return len(text) // 4
```

**Step 3: Add tests**
```bash
touch tests/core/test_ai_async.py
```

```python
# tests/core/test_ai_async.py
import pytest
from gpt_computer.core.ai_async import AsyncAI
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_async_ai_generate():
    """Test basic async generation."""
    with patch('gpt_computer.core.ai_async.AsyncOpenAI') as mock_client:
        # Setup mock
        mock_response = AsyncMock()
        mock_response.choices[0].message.content = "Hello, World!"
        mock_client.return_value.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        # Test
        ai = AsyncAI(model="gpt-4", api_key="test")
        result = await ai.generate("Test prompt")

        assert result == "Hello, World!"

@pytest.mark.asyncio
async def test_async_ai_concurrent():
    """Test concurrent requests."""
    import asyncio

    ai = AsyncAI(model="gpt-4", api_key="test")

    # Run 5 requests concurrently
    tasks = [
        ai.generate(f"Prompt {i}")
        for i in range(5)
    ]

    results = await asyncio.gather(*tasks)
    assert len(results) == 5
```

### 1.3 Update BaseAgent

**Step 1: Update agent interface**
```python
# gpt_computer/core/base_agent.py
from abc import ABC, abstractmethod
import asyncio

class BaseAgent(ABC):
    """Base agent with async support."""

    def __init__(self, ai: AsyncAI, execution_env, memory):
        self.ai = ai
        self.execution_env = execution_env
        self.memory = memory

    @abstractmethod
    async def improve(
        self,
        prompt: str,
        max_iterations: int = 3,
        **kwargs
    ) -> str:
        """Improve code/output asynchronously."""
        pass

    def run(self, prompt: str) -> str:
        """Synchronous wrapper for backwards compatibility."""
        return asyncio.run(self.improve(prompt))
```

**Step 2: Update ReActAgent**
```python
# gpt_computer/core/agent/react.py
class ReActAgent(BaseAgent):  # Already async-capable, update as needed
    async def improve(self, prompt: str, **kwargs) -> str:
        """ReAct loop with async tool execution."""
        for iteration in range(self.max_iterations):
            # Async tool execution
            result = await self._execute_react_loop(prompt)
            if self._is_complete(result):
                return result

        return result
```

### 1.4 Update CLI

**Step 1: Update Typer command**
```python
# gpt_computer/applications/cli/main.py
from typer import Typer
import asyncio

app = Typer()

@app.command()
def build_app(
    prompt: str,
    model: str = typer.Option("gpt-4"),
    async_mode: bool = typer.Option(True),
):
    """Build application."""
    if async_mode:
        asyncio.run(build_app_async(prompt, model))
    else:
        # Fallback to sync
        agent = create_agent(model)
        print(agent.run(prompt))

async def build_app_async(prompt: str, model: str):
    """Async version of build_app."""
    ai = AsyncAI(model=model, api_key=os.getenv("OPENAI_API_KEY"))
    agent = ReActAgent(ai, execution_env, memory)
    result = await agent.improve(prompt)
    print(result)
```

### 1.5 Performance Testing

**Create benchmark script**
```bash
touch scripts/benchmark_async.py
```

```python
# scripts/benchmark_async.py
import asyncio
import time
from gpt_computer.core.ai_async import AsyncAI

async def benchmark_async():
    """Benchmark async performance."""
    ai = AsyncAI(model="gpt-4", api_key=os.getenv("OPENAI_API_KEY"))

    # Concurrent requests
    start = time.time()
    tasks = [ai.generate(f"Count to {i}") for i in range(10)]
    await asyncio.gather(*tasks)
    async_time = time.time() - start

    print(f"Async (10 concurrent): {async_time:.2f}s")
    print(f"Throughput: {10/async_time:.1f} req/s")

if __name__ == "__main__":
    asyncio.run(benchmark_async())
```

**Run benchmark**
```bash
poetry run python scripts/benchmark_async.py
```

### 1.6 Validation Checklist

✅ **Before merging Phase 1:**
- [ ] AsyncAI module implemented and tested (80%+ coverage)
- [ ] All agent types updated to async interface
- [ ] CLI works with async mode
- [ ] Backwards compatibility maintained
- [ ] Performance tests show ≥20% improvement
- [ ] Documentation updated
- [ ] No breaking changes to public API

---

## Phase 2: Knowledge Integration

### 2.1 Vector Store Integration

**Step 1: Install dependencies**
```bash
poetry add chromadb qdrant-client langchain sentence-transformers
```

**Step 2: Implement VectorStoreBackend**
```python
# gpt_computer/core/memory/vector_store.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import asyncio

class VectorStoreBackend(ABC):
    """Abstract vector store interface."""

    @abstractmethod
    async def add_documents(
        self,
        documents: List[str],
        metadata: Optional[List[Dict]] = None,
    ) -> None:
        """Add documents to store."""
        pass

    @abstractmethod
    async def query(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict]:
        """Query store, returns [{'content': str, 'score': float, 'metadata': dict}]."""
        pass

    @abstractmethod
    async def delete(self, doc_ids: List[str]) -> None:
        """Delete documents."""
        pass

class ChromaDBBackend(VectorStoreBackend):
    """ChromaDB implementation."""

    def __init__(self, persist_directory: str = "./chroma_data"):
        import chromadb
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="gpt_computer",
            metadata={"hnsw:space": "cosine"}
        )

    async def add_documents(
        self,
        documents: List[str],
        metadata: Optional[List[Dict]] = None,
    ) -> None:
        """Add documents asynchronously."""
        def _add():
            self.collection.add(
                documents=documents,
                ids=[f"doc_{i}" for i in range(len(documents))],
                metadatas=metadata or [{"index": i} for i in range(len(documents))]
            )

        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _add)

    async def query(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict]:
        """Query documents."""
        def _query():
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                include=["documents", "distances", "metadatas"]
            )

            return [
                {
                    "content": results["documents"][0][i],
                    "score": 1 - results["distances"][0][i],  # Convert distance to similarity
                    "metadata": results["metadatas"][0][i],
                }
                for i in range(len(results["documents"][0]))
            ]

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _query)
```

**Step 3: Implement RAG Pipeline**
```python
# gpt_computer/core/memory/rag.py
class RAGPipeline:
    """Retrieval-augmented generation."""

    def __init__(self, vector_store: VectorStoreBackend, ai: AsyncAI):
        self.vector_store = vector_store
        self.ai = ai

    async def augment_prompt(
        self,
        prompt: str,
        context_count: int = 3,
    ) -> str:
        """Augment prompt with retrieved context."""
        # Retrieve relevant documents
        results = await self.vector_store.query(prompt, top_k=context_count)

        # Format context
        context_str = "\n\n".join([
            f"[Relevance: {doc['score']:.2%}]\n{doc['content']}"
            for doc in results
        ])

        # Build augmented prompt
        augmented = f"""Use the following context to answer the question:

CONTEXT:
{context_str}

QUESTION:
{prompt}

ANSWER:"""

        return augmented
```

### 2.2 Multi-Agent Orchestration

**Create orchestrator**
```python
# gpt_computer/core/orchestration/orchestrator.py
from dataclasses import dataclass
from typing import Dict, List, Optional
import asyncio
import structlog

log = structlog.get_logger(__name__)

@dataclass
class Task:
    id: str
    name: str
    description: str
    agent_type: str
    dependencies: List[str] = None
    context: Dict = None
    result: Optional[str] = None

class Orchestrator:
    """Multi-agent task coordinator."""

    def __init__(self):
        self.agents = {}
        self.results = {}

    def register_agent(self, agent_type: str, agent):
        """Register agent implementation."""
        self.agents[agent_type] = agent

    async def execute_workflow(
        self,
        tasks: List[Task],
    ) -> Dict[str, str]:
        """Execute workflow with task dependencies."""

        # Build dependency graph
        graph = self._build_graph(tasks)

        # Execute in dependency order
        for task in graph:
            log.info("task_start", task_id=task.id, task_name=task.name)

            try:
                # Gather context from dependencies
                context = self._gather_context(task, self.results)

                # Execute task
                agent = self.agents[task.agent_type]
                result = await agent.improve(
                    task.description,
                    context=context,
                )

                self.results[task.id] = result
                log.info("task_complete", task_id=task.id)

            except Exception as e:
                log.error("task_failed", task_id=task.id, error=str(e))
                raise

        return self.results

    def _build_graph(self, tasks: List[Task]) -> List[Task]:
        """Topological sort of tasks."""
        # Implementation of topological sort
        # Returns tasks in execution order
        pass

    def _gather_context(self, task: Task, results: Dict) -> Dict:
        """Gather results from dependencies."""
        context = task.context or {}
        if task.dependencies:
            for dep_id in task.dependencies:
                context[dep_id] = results.get(dep_id)
        return context
```

---

## Phase 3: UX Enhancements

### 3.1 WebSocket Streaming

**Add FastAPI WebSocket endpoint**
```python
# gpt_computer/api/websocket.py
from fastapi import FastAPI, WebSocket
from gpt_computer.core.ai_async import AsyncAI
import json

app = FastAPI()

@app.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    """WebSocket endpoint for streaming generation."""
    await websocket.accept()

    try:
        # Receive prompt
        message = await websocket.receive_text()
        prompt = json.loads(message)["prompt"]

        # Stream generation
        async for chunk in ai.generate_stream(prompt):
            await websocket.send_json({
                "type": "chunk",
                "content": chunk,
            })

        # Send completion
        await websocket.send_json({
            "type": "complete",
            "status": "success",
        })

    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e),
        })

    finally:
        await websocket.close()
```

### 3.2 Server-Sent Events

**Add SSE endpoint**
```python
# gpt_computer/api/streaming.py
from fastapi import StreamingResponse
import json

@app.get("/stream/generate")
async def stream_generate(prompt: str):
    """Stream via Server-Sent Events."""

    async def event_generator():
        try:
            async for chunk in ai.generate_stream(prompt):
                yield f"data: {json.dumps({'content': chunk})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
```

---

## Phase 4: Reliability

### 4.1 Error Recovery

**Error classification**
```python
# gpt_computer/core/error_handling/classifier.py
from enum import Enum
import re

class ErrorType(Enum):
    SYNTAX = "syntax"
    RUNTIME = "runtime"
    SEMANTIC = "semantic"
    IMPORT = "import"
    TIMEOUT = "timeout"

class ErrorClassifier:
    """Classify and recover from errors."""

    async def classify(self, error: Exception) -> ErrorType:
        """Classify error type."""
        if isinstance(error, SyntaxError):
            return ErrorType.SYNTAX
        elif isinstance(error, ImportError):
            return ErrorType.IMPORT
        elif isinstance(error, TimeoutError):
            return ErrorType.TIMEOUT
        else:
            return ErrorType.RUNTIME

    async def suggest_fix(self, error: Exception, code: str) -> str:
        """Suggest fix for error."""
        error_type = await self.classify(error)

        prompt = f"""Code has {error_type.value} error:

Error: {error}

Code:
```python
{code}
```

Provide a fixed version of the code that resolves this error."""

        return await self.ai.generate(prompt)
```

---

## Testing Guide

### Unit Testing

```python
# Test async code
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

### Integration Testing

```python
# Test components together
@pytest.mark.asyncio
async def test_agent_with_execution():
    ai = AsyncAI(...)
    agent = ReActAgent(ai, execution_env, memory)
    result = await agent.improve("Generate hello world")
    assert "hello" in result.lower()
```

### Load Testing

```bash
# Use locust for load testing
pip install locust

# Run load tests
locust -f tests/load/locustfile.py
```

---

## Deployment Strategy

### Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

# Copy code
COPY gpt_computer/ ./gpt_computer/

# Run app
CMD ["uvicorn", "gpt_computer.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gpt-computer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gpt-computer
  template:
    metadata:
      labels:
        app: gpt-computer
    spec:
      containers:
      - name: gpt-computer
        image: gpt-computer:v0.2.0
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-keys
              key: openai
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/feature-release.yml
name: Feature Release

on:
  push:
    branches: [main]
    tags: [v*]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install poetry
      - run: poetry install
      - run: pytest tests/ --cov=gpt_computer
      - run: coverage report --fail-under=90

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install ruff
      - run: ruff check gpt_computer/

  build:
    needs: [test, lint]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: poetry build
      - uses: actions/upload-artifact@v3
        with:
          name: dist
          path: dist/
```

---

## Performance Monitoring

### Key Metrics

```python
# Monitor during development
from gpt_computer.core.observability import monitor

@monitor(metric="generation_time")
async def generate(prompt: str):
    # Automatically recorded
    return await ai.generate(prompt)
```

### Dashboards

Use Grafana to visualize:
- Response latency
- Throughput (req/s)
- Error rates
- Token usage
- Memory consumption

---

## Troubleshooting

### Common Issues

**Q: "RuntimeError: Event loop is closed"**
A: Use `asyncio.run()` instead of `asyncio.get_event_loop().run_until_complete()`

**Q: Tests timeout**
A: Add `@pytest.mark.timeout(300)` or use fixture `asyncio_mode = "auto"`

**Q: Memory leaks with concurrent requests**
A: Ensure connections are properly closed (use context managers)

---

**Last Updated**: March 31, 2026
**Status**: 🟡 Ready for Phase 1 Implementation
