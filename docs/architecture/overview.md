# gpt-computer Architecture Documentation

## System Overview

gpt-computer is an **execution-native AI software generation platform** that implements a closed-loop system for autonomous code generation and iteration.

### Core Philosophy

The system operates on a fundamental principle:
```
Intent → Plan → Generate → Execute → Analyze → Repair → Repeat
```

This deterministic loop enables controlled experimentation, execution-aware evaluation, and infrastructure alignment.

---

## System Architecture

```
┌─────────────────────────────────────────────────┐
│          User Intent/API Request                │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │  Orchestration Layer    │
        │  (Agents & Controllers) │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │  Model Abstraction      │
        │  (AI Interface)         │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │  Execution Runtime      │
        │  (Env & File Ops)       │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │  Analysis & Monitoring  │
        │  (Logging & Feedback)   │
        └────────────────────────┘
```

---

## Core Components

### 1. **AI Module** (`core/ai.py`)
- **Purpose**: Abstract interface for LLM interactions
- **Responsibilities**:
  - Token counting and usage tracking
  - Model provider abstraction (OpenAI, Claude, Groq, etc.)
  - Prompt caching and optimization
  - Error handling and retry logic
- **Key Classes**: `AI` (synchronous), `AsyncAI` (asynchronous)

### 2. **Agent System** (`core/base_agent.py`, `core/agent/`)
- **Purpose**: Core execution loop orchestration
- **Responsibilities**:
  - Initialization and state management
  - Iterative improvement cycles
  - Error recovery and repair mechanisms
- **Agent Types**:
  - `SimpleAgent`: Basic agent implementation
  - `ReActAgent`: Reasoning + Acting pattern for complex tasks
  - `CliAgent`: CLI-specialized agent (`applications/cli/cli_agent.py`)

### 3. **Execution Environment** (`core/base_execution_env.py`, `core/default/`)
- **Purpose**: Safe code execution and file management
- **Implementations**:
  - `DiskExecutionEnv`: On-disk file-based execution
  - Sandboxing mechanisms for code execution
- **Responsibilities**:
  - File read/write operations
  - Process execution and output capture
  - State preservation between iterations

### 4. **Memory System** (`core/memory/`, `core/base_memory.py`)
- **Purpose**: Context and knowledge retention
- **Types**:
  - Short-term: Current session state
  - Long-term: Project and learning state (optional vector store integration)
- **Status**: Foundational (vector store integration pending)

### 5. **Tool System** (`tools/`, `core/agent_tools/`)
- **Purpose**: Extensible action registry for agents
- **Includes**:
  - File operations
  - Code generation and analysis
  - Git integration
  - Linting and formatting

### 6. **API Layer** (`api/main.py`)
- **Purpose**: REST API for external tool integration
- **Framework**: FastAPI
- **Endpoints**:
  - `/health`: Health check
  - `/agent/run`: Execute agent with prompt
  - `/agent/status`: Check execution status (planned)

### 7. **CLI Application** (`applications/cli/`)
- **Purpose**: Command-line interface for end users
- **Features**:
  - Interactive project creation
  - Build and improve workflows
  - Learning analytics collection
  - File selection and management

---

## Data Flow: Detailed Sequence

### Example: Code Generation Task

```
1. User Input (CLI/API)
   ├─ Prompt: "Create a REST API with FastAPI"
   ├─ Project Path: ./my_api
   └─ Configuration: model, max_iterations, etc.

2. Orchestration (Agent)
   ├─ Initialize execution environment
   ├─ Load project context
   ├─ Prepare system prompt
   └─ Start iteration loop

3. AI Interaction (AI Module)
   ├─ Count tokens in context
   ├─ Call LLM with prompt
   ├─ Track token usage
   └─ Return response with reasoning

4. Code Generation (Agent)
   ├─ Parse LLM response
   ├─ Extract code blocks
   ├─ Identify file operations
   └─ Queue operations for execution

5. Execution (Execution Environment)
   ├─ Write generated files to disk
   ├─ Run linter/formatter
   ├─ Execute tests if present
   ├─ Capture output/errors
   └─ Update project state

6. Analysis (Agent)
   ├─ Evaluate execution results
   ├─ Identify issues or improvements
   ├─ Decide repair/continuation
   └─ Loop if max_iterations not reached

7. Output (User Interface)
   ├─ Display generated code
   ├─ Show execution logs
   ├─ Report metrics (time, tokens, iterations)
   └─ Offer further improvements
```

---

## Configuration Management

### Environment Variables (Priority Order)
1. `.env` file (project root)
2. Shell environment
3. Default values in code

### Key Configurations
- `OPENAI_API_KEY`: Primary LLM provider
- `CLAUDE_API_KEY`: Alternative provider (via Claude)
- `GROQ_API_KEY`: Alternative provider (via Groq)
- `LOG_LEVEL`: Logging verbosity (default: INFO)
- `MAX_TOKENS`: Token limit per request
- `MODEL_NAME`: Default model selection

### Project Configuration (`project_config.toml`)
- Project metadata
- Agent settings
- Execution preferences
- Custom prompts and behaviors

---

## Extension Points

### 1. **Custom Agents**
Extend `BaseAgent` to implement specialized agent types:
```python
from gpt_computer.core.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    async def improve(self, prompt: str) -> str:
        # Custom improvement logic
        pass
```

### 2. **Custom Execution Environments**
Extend `BaseExecutionEnv` for different runtime targets:
```python
from gpt_computer.core.base_execution_env import BaseExecutionEnv

class DockerExecutionEnv(BaseExecutionEnv):
    # Execute in Docker container
    pass
```

### 3. **Custom Memory Implementations**
Extend `BaseMemory` for knowledge retention:
```python
from gpt_computer.core.base_memory import BaseMemory

class VectorStoreMemory(BaseMemory):
    # Vector-based semantic memory
    pass
```

### 4. **Custom Tools**
Register new tools in the agent's tool registry:
```python
from gpt_computer.tools import register_tool

@register_tool
def custom_operation(param: str) -> str:
    return f"Processed: {param}"
```

---

## Error Handling & Recovery

### Error Categories

1. **LLM Errors** (TransientError, RateLimitError)
   - Automatic retry with exponential backoff
   - Fallback to alternative models

2. **Execution Errors** (code fails, tools unavailable)
   - Captured and reported to LLM
   - Agent attempts repair in next iteration

3. **File System Errors** (permission denied, disk full)
   - Transaction-like rollback on critical failures
   - Git-based state preservation

### Repair Loop
When execution fails:
1. Capture error output
2. Provide error context to LLM
3. Request fix/alternative approach
4. Re-execute with improved code
5. Verify results before continuing

---

## Performance Considerations

### Token Optimization
- **Prompt Caching**: Reuse system prompts across requests
- **Context Pruning**: Remove irrelevant files from context
- **Lazy Loading**: Load large files only when needed
- **Incremental Diffs**: Send only changed code sections

### Execution Efficiency
- **Parallel Tool Execution**: Run independent tools concurrently
- **Smart Retries**: Avoid repeating failed operations
- **File Change Tracking**: Only include modified files in next iteration
- **Cached Analysis**: Reuse linting/test results when possible

---

## Security Considerations

### Code Execution Sandboxing
- Execution environment isolation from host system
- Read/write restrictions to project directory
- Process timeout limits
- Resource limits (memory, CPU)

### API Security
- Authentication token validation
- Rate limiting per user/API key
- Input validation and sanitization
- Audit logging of all operations

### Secret Management
- Environment variable isolation
- No secret printing in logs
- API key rotation support
- Secret scanning in generated code

---

## Testing Strategy

### Test Tiers
1. **Unit Tests**: Individual component behavior
2. **Integration Tests**: Component interactions
3. **API Tests**: REST endpoint functionality
4. **E2E Tests**: Full workflow execution

### Coverage Goals
- **Unit**: 80%+ of core modules
- **Integration**: 70%+ of key workflows
- **E2E**: Major use cases covered

### Running Tests Locally
```bash
# Install test dependencies
poetry install --with=test

# Run all tests
pytest

# Run with coverage
pytest --cov=gpt_computer

# Run specific test suite
pytest tests/core/test_ai.py
```

---

## Deployment Architecture

### Local Execution
- Direct process execution on developer machine
- Used for CLI and single-user scenarios

### API Server Deployment
- FastAPI server with Uvicorn/Gunicorn
- Container-based (Docker) deployment
- Load balancing for multiple instances

### Future: Distributed Execution
- Agent coordination across multiple workers
- Redis/message queue for task distribution
- Centralized result aggregation

---

## Roadmap & Future Enhancements

### Phase 1: Foundation ✅ (In Progress)
- [x] Core agent loop
- [x] CLI interface
- [x] API layer
- [ ] Async migration
- [ ] Enhanced logging

### Phase 2: Intelligence 🔄 (Planned)
- [ ] Vector store memory
- [ ] ReAct pattern enhancements
- [ ] Tool system improvements
- [ ] Multi-agent coordination

### Phase 3: Scale 📋 (Future)
- [ ] Distributed execution
- [ ] Multi-tenant support
- [ ] Advanced analytics

---

## Contributing

For architectural changes or extensions, see [CONTRIBUTING.md](CONTRIBUTING.md).

For detailed module-level documentation, see [MODULE_STRUCTURE.md](MODULE_STRUCTURE.md).
