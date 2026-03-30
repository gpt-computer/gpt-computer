# gpt-computer Module Structure Guide

This document provides a detailed reference for the gpt-computer codebase structure and module organization.

---

## 📦 Package Structure

```
gpt_computer/
├── __init__.py                 # Package initialization
├── api/                        # REST API (FastAPI)
├── applications/              # User-facing applications
│   └── cli/                   # Command-line interface
├── benchmark/                 # Performance benchmarking
├── core/                      # Core engine (main logic)
│   ├── agent/                 # Agent implementations
│   ├── agent_tools/           # Agent-available tools
│   ├── default/               # Default implementations
│   └── memory/                # Memory systems
├── preprompts/               # Pre-defined system prompts
└── tools/                    # Utility tools
```

---

## 🔧 Core Modules Detailed Reference

### `core/ai.py` - LLM Interface Abstraction
**Purpose**: Abstract interface for interacting with language models.

**Key Classes**:
- `AI`: Synchronous wrapper for LLM operations
  - `generate(prompt, max_tokens, temperature)`: Get LLM response
  - `count_tokens(text)`: Calculate token usage
  - `validate_api_key()`: Verify API key validity

- `AsyncAI`: Asynchronous variant (incoming)
  - Same interface as `AI` with async/await support

**Supported Providers**:
- OpenAI (GPT-4, GPT-3.5-turbo)
- Claude (Anthropic)
- Groq
- Google GenAI
- Mistral AI
- Cohere

**Usage Example**:
```python
from gpt_computer.core.ai import AI

ai = AI(model="gpt-4", api_key="sk-...")
response = ai.generate("Write a Python function that...")
tokens_used = ai.count_tokens(response)
```

**See**: [core/ai.py](gpt_computer/core/ai.py)

---

### `core/base_agent.py` - Base Agent Interface
**Purpose**: Abstract base class defining the agent lifecycle.

**Key Classes**:
- `BaseAgent`: Abstract agent implementation
  - `__init__()`: Initialize agent with context
  - `improve()`: Async core improvement loop
  - `run()`: Execute and return results

**Abstract Methods** (must implement in subclasses):
- `improve(prompt: str, max_iterations: int) -> str`

**Key Properties**:
- `execution_env`: Where code is executed
- `ai`: LLM interface instance
- `current_iteration`: Iteration counter
- `file_repository`: Access to project files

**Usage Example**:
```python
from gpt_computer.core.base_agent import BaseAgent
from gpt_computer.core.default import DiskExecutionEnv

class MyAgent(BaseAgent):
    async def improve(self, prompt: str, max_iterations: int = 3):
        # Custom improvement logic
        for i in range(max_iterations):
            response = await self.ai.generate(prompt)
            # ... process response
            # ... execute changes
            # ... analyze results
        return final_result
```

**See**: [core/base_agent.py](gpt_computer/core/base_agent.py)

---

### `core/agent/react.py` - ReAct Agent Pattern
**Purpose**: Implements Reasoning + Acting pattern for complex multi-step tasks.

**Key Classes**:
- `ReActAgent`: Extends `BaseAgent` with ReAct loop
  - Explicit reasoning step (think through problem)
  - Action step (execute tool/code)
  - Observation step (analyze results)
  - Repeat until task complete

**Features**:
- Multi-step problem decomposition
- Tool use reasoning
- Error recovery with re-planning

**Usage Example**:
```python
from gpt_computer.core.agent.react import ReActAgent

agent = ReActAgent(
    ai=ai,
    execution_env=env,
    max_iterations=10
)
result = await agent.improve("Build a test framework for the project")
```

**See**: [core/agent/react.py](gpt_computer/core/agent/react.py)

---

### `core/base_execution_env.py` - Execution Environment Interface
**Purpose**: Abstract interface for executing code and managing files.

**Key Classes**:
- `BaseExecutionEnv`: Abstract execution environment
  - `write_files(file_dict)`: Write files to storage
  - `read_files(paths)`: Read files from storage
  - `execute(command)`: Run arbitrary commands
  - `get_project_state()`: Get current file state

**Implementations**:
- `DiskExecutionEnv` (`core/default/disk_execution_env.py`): On-disk file storage
  - Direct file system access
  - Process execution via subprocess
  - Git integration for history

**Usage Example**:
```python
from gpt_computer.core.default import DiskExecutionEnv

env = DiskExecutionEnv(project_path="/path/to/project")
env.write_files({
    "main.py": "print('Hello')",
    "config.yaml": "debug: true"
})
result = env.execute("python main.py")
print(result.stdout)
```

**See**:
- [core/base_execution_env.py](gpt_computer/core/base_execution_env.py)
- [core/default/disk_execution_env.py](gpt_computer/core/default/disk_execution_env.py)

---

### `core/base_memory.py` - Memory System Interface
**Purpose**: Abstract interface for knowledge retention and context management.

**Key Classes**:
- `BaseMemory`: Abstract memory interface
  - `add(type, data)`: Store information
  - `retrieve(query)`: Retrieve relevant information
  - `clear()`: Reset memory

**Planned Implementations**:
- Short-term memory (current session state)
- Long-term memory (project state)
- Vector store memory (semantic search)

**Status**: Foundational APIs ready; vector store integration coming in Phase 2.

**See**: [core/base_memory.py](gpt_computer/core/base_memory.py)

---

### `core/chat_to_files.py` - Response Parsing
**Purpose**: Parse LLM responses and extract code/file operations.

**Key Functions**:
- `extract_code_blocks(response)`: Find all code blocks in response
- `parse_file_operations(response)`: Identify which files to create/modify
- `structured_response_to_files(response)`: Convert structured output to file dict

**Usage Example**:
```python
from gpt_computer.core.chat_to_files import extract_code_blocks

response = "Here's the code:\n```python\nprint('Hi')\n```"
blocks = extract_code_blocks(response)  # [{"lang": "python", "code": "..."}]
```

**See**: [core/chat_to_files.py](gpt_computer/core/chat_to_files.py)

---

### `core/git.py` - Version Control Integration
**Purpose**: Abstract Git operations for state management and history.

**Key Functions**:
- `git_diff(project_path)`: Get diff since last commit
- `git_commit(project_path, message)`: Create new commit
- `git_restore(project_path)`: Restore from previous commit
- `get_commit_history(project_path)`: Get commit log

**Usage Example**:
```python
from gpt_computer.core.git import git_diff, git_commit

# See what changed
diff = git_diff("/project")

# Save changes
git_commit("/project", "Generated new features")
```

**See**: [core/git.py](gpt_computer/core/git.py)

---

### `core/prompt.py` - Prompt Management
**Purpose**: Build and manage AI prompts with context.

**Key Classes**:
- `PromptBuilder`: Compose prompts with multiple sections
  - System prompt
  - Context/file listings
  - Instruction
  - Examples
  - Current state

**Key Functions**:
- `build_system_prompt()`: Create base system prompt
- `build_context_prompt(project_state)`: Include current project files
- `build_instruction_prompt(user_intent)`: Format user request

**See**: [core/prompt.py](gpt_computer/core/prompt.py)

---

### `core/config.py` - Configuration Management
**Purpose**: Centralized configuration for the framework.

**Key Classes**:
- `Config`: Main configuration dataclass
  - Model selection
  - Token limits
  - Logging level
  - API keys

**Usage Example**:
```python
from gpt_computer.core.config import Config

config = Config(
    model="gpt-4",
    max_tokens=4096,
    log_level="INFO"
)
```

**See**: [core/config.py](gpt_computer/core/config.py)

---

### `core/token_usage.py` - Token Tracking
**Purpose**: Track and report token usage across operations.

**Key Classes**:
- `TokenUsage`: Dataclass for token metrics
  - `prompt_tokens`: Tokens in requests
  - `completion_tokens`: Tokens in responses
  - `total_tokens`: Combined total

**Key Functions**:
- `get_total_cost()`: Calculate API cost
- `format_usage_report()`: Generate usage summary

**See**: [core/token_usage.py](gpt_computer/core/token_usage.py)

---

### `core/linting.py` - Code Quality
**Purpose**: Run linters and formatters on generated code.

**Key Functions**:
- `lint_code(code)`: Check code quality
- `format_code(code)`: Auto-format code
- `fix_linting_issues(code)`: Auto-fix common issues

**Supported Tools**:
- Black (Python formatting)
- Ruff (Python linting)
- Custom linters per language

**See**: [core/linting.py](gpt_computer/core/linting.py)

---

## 🎯 API Module (`api/`)

### `api/main.py` - FastAPI Application
**Purpose**: REST API for programmatic access to gpt-computer.

**Key Endpoints**:
- `GET /health` - Health check
- `POST /agent/run` - Execute agent with prompt
  - Request: `{"prompt": "...", "max_iterations": 5}`
  - Response: `{"result": "...", "status": "success"}`

**Usage Example**:
```bash
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a calculator", "max_iterations": 3}'
```

**See**: [api/main.py](gpt_computer/api/main.py)

---

## 🖥️ CLI Application (`applications/cli/`)

### `applications/cli/main.py` - CLI Entry Point
**Purpose**: Command-line interface using Typer.

**Available Commands**:
- `init` - Initialize new project
- `build` - Build software from specification
- `improve` - Improve existing codebase
- `benchmark` - Run performance benchmark

**Usage Examples**:
```bash
# Initialize and build a project
gpt-computer init --name my-project
cd my-project
gpt-computer build --prompt "Create a REST API"

# Improve existing project
gpt-computer improve --iterations 3

# Run benchmark
gpt-computer benchmark
```

**See**: [applications/cli/main.py](gpt_computer/applications/cli/main.py)

---

### `applications/cli/cli_agent.py` - CLI-specific Agent
**Purpose**: CLI-optimized agent implementation with interactive features.

**Features**:
- Interactive file selection
- Progress visualization
- Real-time output streaming
- Graceful error handling

**See**: [applications/cli/cli_agent.py](gpt_computer/applications/cli/cli_agent.py)

---

## 📊 Benchmark Module (`benchmark/`)

**Purpose**: Performance testing and benchmarking infrastructure.

**Key Components**:
- `BenchConfig`: Benchmark configuration
- `run.py`: Benchmark execution
- `benchmarks/`: Individual benchmark implementations

**Usage**:
```bash
poetry run bench run --config benchmarks/llm_speed.toml
```

**See**: [benchmark/](gpt_computer/benchmark/)

---

## 🔧 Tools Module (`tools/`)

### `tools/supported_languages.py`
Lists supported programming languages and their configurations.

**Includes**:
- Syntax highlighting
- Language-specific linters
- Execution environments

### `tools/custom_steps.py`
Custom step definitions for agent workflows.

**See**: [tools/](gpt_computer/tools/)

---

## 📝 Preprompts Module (`preprompts/`)

**Purpose**: Pre-defined system prompts for different scenarios.

**Available Prompts**:
- `entrypoint` - Main system prompt
- `generate` - Code generation instructions
- `improve` - Code improvement instructions
- `philosophy` - AI philosophy/behaviors
- `file_format` - File format specifications
- `clarify` - User intent clarification

**Usage**:
```python
from gpt_computer.core.preprompts_holder import PrepromptsHolder

prompts = PrepromptsHolder()
system_prompt = prompts.get("entrypoint")
```

**See**: [preprompts/](gpt_computer/preprompts/)

---

## 🧪 Testing Structure (`tests/`)

**Organization**:
```
tests/
├── core/                    # Core module tests
│   ├── test_ai.py
│   ├── test_chat_to_files.py
│   ├── agent/
│   ├── default/
│   └── ...
├── api/                     # API endpoint tests
├── applications/            # CLI app tests
│   └── cli/
├── benchmark/               # Benchmark tests
├── test_install.py         # Installation verification
├── test_project_config.py  # Project config tests
└── mock_ai.py              # Mock LLM for testing
```

**Running Tests**:
```bash
# All tests
pytest

# Specific module
pytest tests/core/test_ai.py

# With coverage
pytest --cov=gpt_computer tests/

# Only fast tests (skip slow)
pytest -m "not slow"
```

**See**: [tests/](tests/)

---

## 📚 Documentation Files

### Core Documentation
- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture (THIS FILE)
- [MODULE_STRUCTURE.md](MODULE_STRUCTURE.md) - Module reference (THIS FILE)

### User Guides
- [docs/quickstart.rst](docs/quickstart.rst) - Getting started
- [docs/installation.rst](docs/installation.rst) - Installation guide
- [docs/tracing_debugging.md](docs/tracing_debugging.md) - Debug guide
- [docs/open_models.md](docs/open_models.md) - Using open source models

### Design Documents
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Future roadmap
- [ROADMAP.md](ROADMAP.md) - Feature roadmap

### Governance
- [CONTRIBUTING.md](.github/CONTRIBUTING.md) - Contributing guide
- [CODE_OF_CONDUCT.md](.github/CODE_OF_CONDUCT.md) - Community standards

---

## 🔄 Data Flow Examples

### Example 1: Simple Code Generation
```
User Input
  ↓
CLI Agent (applications/cli/cli_agent.py)
  ↓
BaseAgent.improve() → loop:
  ↓
Call AI.generate() (core/ai.py)
  ↓
Parse response (core/chat_to_files.py)
  ↓
Extract code blocks & file operations
  ↓
Write files (core/base_execution_env.py)
  ↓
Format/lint code (core/linting.py)
  ↓
Execute tests/builds
  ↓
Analyze results
  ↓
Loop or return results
```

### Example 2: API-based Execution
```
POST /agent/run
  ↓
FastAPI endpoint (api/main.py)
  ↓
Instantiate agent
  ↓
Call agent.improve(prompt)
  ↓
[Same as Example 1]
  ↓
Return JSON response
```

---

## 🚀 Extension Guide

### Adding a New Agent Type
1. Extend `BaseAgent` in `core/agent/my_agent.py`
2. Implement `improve()` method
3. Add to `__init__.py` exports
4. Create tests in `tests/core/agent/test_my_agent.py`

### Adding a New Tool
1. Define in `core/agent_tools/` or `tools/`
2. Register in tool registry
3. Add documentation with examples
4. Create tests

### Adding a New Execution Environment
1. Extend `BaseExecutionEnv`
2. Implement abstract methods
3. Add to `core/default/`
4. Create integration tests

---

## 📋 Quick Reference

**Most Important Files**:
- `core/ai.py` - LLM abstraction
- `core/base_agent.py` - Agent interface
- `core/agent/react.py` - Main agent implementation
- `applications/cli/cli_agent.py` - CLI entry point
- `api/main.py` - API server

**Configuration Files**:
- `pyproject.toml` - Dependencies and metadata
- `project_config.toml` - Project-specific settings
- `.env` - Environment variables

**Testing**:
- `pytest` configuration in `pyproject.toml`
- Run: `poetry run pytest`
- Coverage: `poetry run pytest --cov`

---

## 📖 Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design and patterns
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Modernization roadmap
- [CONTRIBUTING.md](.github/CONTRIBUTING.md) - How to contribute

---

**Last Updated**: March 2025
**Version**: 0.1.1
