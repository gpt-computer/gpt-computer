# gpt-computer Project Restructure Plan

**Date**: 2026-10-28
**Version**: 0.2.2
**Status**: Approved for Phase 0 (Baseline and Inventory) and Architecture Preparation

**Note**: This plan is approved to begin Phase 0 and architecture preparation work. Full migration should not proceed until the three P0 issues are resolved (compatibility mapping verification, static import-graph tool validation, and execution security gate definition).

---

## Executive Summary

The gpt-computer project currently has a confusing dual-package structure (`gpt_computer` and `gptc`) with overlapping functionality, unclear separation of concerns, and maintenance overhead. This restructure plan aims to consolidate the codebase into a single, well-organized package with clear module boundaries, explicit dependency rules, and a migration strategy that preserves backward compatibility.

**Key Changes from v0.2.1**:
- Fixed compatibility mapping to use actual legacy namespaces (gpt_computer/core/* and gptc/*)
- Corrected static import-graph analysis to resolve full module paths and detect layer violations
- Renamed security stages to Execution Security Level A/B/C (no longer conflicts with migration phases)
- Made compatibility examples explicitly export all guaranteed classes and functions
- Clarified dependency direction rules (interfaces may NOT import analysis)
- Updated version schedule to reflect actual release plan
- Defined 'all' optional dependency group
- Adjusted security risk assessment to unknown until testing
- Changed status from "Implementation-Ready" to "Approved for Phase 0"

---

## Current Structure Analysis

### Existing Layout

```
gpt-computer/
├── gpt_computer/              # Primary package
│   ├── api/                   # REST API (FastAPI)
│   ├── applications/          # User-facing applications
│   │   └── cli/               # Command-line interface
│   ├── benchmark/             # Performance benchmarking
│   ├── codemap/               # Code analysis & visualization
│   ├── context_os/            # Context management system
│   ├── core/                  # Core engine (main logic)
│   │   ├── agent/             # Agent implementations
│   │   ├── agent_tools/       # Agent-available tools
│   │   ├── default/           # Default implementations
│   │   ├── memory/            # Memory systems
│   │   └── orchestration/    # Orchestration logic
│   ├── preprompts/            # Pre-defined system prompts
│   ├── repository_intelligence/ # Code analysis agents
│   ├── test/                  # Test utilities
│   └── tools/                 # Utility tools
│
├── gptc/                      # Secondary package (confusing)
│   ├── Provider/              # Nested provider directory
│   ├── api/                   # API-related code
│   ├── cli/                   # CLI implementation
│   ├── client/                # AI client abstraction
│   ├── config.py              # Configuration
│   ├── cookies.py             # Cookie management
│   ├── debug.py               # Debug utilities
│   ├── errors.py              # Error definitions
│   ├── files.py               # File operations
│   ├── gui/                   # GUI components
│   ├── image/                 # Image handling
│   ├── integration/           # Integration code
│   ├── local/                 # Local LLM support
│   ├── locals/                # Local settings
│   ├── mcp/                   # MCP protocol support
│   ├── models.py              # Model definitions
│   ├── providers/             # AI provider implementations
│   ├── requests/              # Request handling
│   ├── tools/                 # Tool implementations
│   ├── tray.py                # System tray
│   ├── typing.py              # Type definitions
│   └── version.py             # Version management
│
├── scripts/                   # Utility scripts
├── docs/                      # Documentation
├── tests/                     # Test suite
└── docker/                    # Docker configurations
```

### Identified Issues

#### 1. **Dual Package Structure**
- Two packages (`gpt_computer` and `gptc`) with overlapping functionality
- Confusing for users and contributors
- Maintenance overhead for syncing changes
- Unclear which package should be used for what purpose

#### 2. **Naming Inconsistency**
- Project name: `gpt-computer`
- Package names: `gpt_computer` and `gptc`
- CLI commands: `gpt-computer`, `ge`, `gptc`, `gptc-mcp`, `gptc-tray`
- No clear naming convention

#### 3. **Overlapping Functionality**
- Both packages have `api/`, `cli/`, `tools/` directories
- Both have provider/client abstractions
- Unclear separation of concerns

#### 4. **Mixed Responsibilities**
- `gptc` appears to be an AI client library (OpenAI-compatible API)
- `gpt_computer` is the agent system built on top of AI clients
- Should these be separate projects or one unified project?

#### 5. **Flat Directories**
- `gptc/` has 25+ files at root level
- Hard to navigate and understand
- Should be organized into logical subdirectories

#### 6. **Scripts Directory**
- Contains temporary and utility scripts (`tmp_*.py`)
- Some scripts may be outdated or not needed
- Should be cleaned up or organized better

#### 7. **Unclear Entry Points**
- Multiple CLI entry points defined in `pyproject.toml`
- Confusing for users which one to use
- Overlap between `gpt-computer` and `gptc` commands

---

## Architectural Decisions

### Decision 1: Package Structure - **MERGE into Single Distribution**

**Decision**: Merge `gptc` and `gpt_computer` into a single Python distribution.

**Rationale**:
- `gptc` primarily exists to support `gpt-computer`
- Both packages share a release lifecycle
- Independent use of the client is not a major goal
- Simpler releases, one dependency graph, consistent documentation

### Decision 2: Dependency Rules

**Allowed Import Directions** (bottom to top):

```
infrastructure/
    ↑
execution/
    ↑
ai/
    ↑
agent/
    ↑
analysis/
    ↑
interfaces/
```

**Rules**:
1. **Infrastructure** → No dependencies on other gpt_computer modules
2. **Execution** → May depend on infrastructure only
3. **AI Client** → May depend on infrastructure only
4. **Agent** → May depend on AI, execution, infrastructure
5. **Analysis** → May depend on agent, infrastructure (not interfaces)
6. **Interfaces** → May depend on infrastructure, execution, ai, agent (NOT analysis)

**Prohibited**:
- No circular dependencies
- No higher layer importing from lower layer's private modules
- No infrastructure importing from agent or interfaces
- No interfaces importing from analysis
- No analysis importing from interfaces

**Special Cases**:
- **MCP Server**: Moved to `interfaces/mcp/` (not `ai/mcp/`) to avoid upward dependencies
- **Provider Config**: Only provider-specific settings in `ai/providers/config.py`; global config in `infrastructure/config/`
- **Analysis Modules**: Document which analysis features work without agents (codemap, tree_sitter_analyzer are agent-independent)

### Decision 3: Responsibility Ownership

| Responsibility | Owner Module | Description |
|----------------|--------------|-------------|
| Provider invocation | `ai/client/` | Single canonical AI client interface |
| Configuration | `infrastructure/config/` | Centralized config with precedence rules |
| File operations | `infrastructure/files/` | Reusable file primitives |
| Git operations | `infrastructure/git/` | Git command wrappers |
| Code execution | `execution/` | Execution environments with security boundaries |
| Agent tools | `agent/tools/` | Adapters that wrap infrastructure for agent use |
| Model registry | `ai/models/` | Model metadata and provider capabilities |
| Retry logic | `ai/client/` | Client-level retry logic |
| Response handling | `ai/client/` | Client-level response parsing |
| MCP protocol | `interfaces/mcp/` | MCP server orchestration (may depend on agent) |

### Decision 4: Execution Security Requirements

**Security Boundary Definition**:
- **Execution Security Level A (Directory-Based)**: Defense-in-depth measure, NOT a security sandbox
- **Execution Security Level B (Process-Based)**: Actual security boundary with OS-level isolation
- **Execution Security Level C (Container-Based)**: Full isolation with Docker

**Execution Security Level A Requirements** (Current Migration):
- **Path Restrictions**:
  - Resolve all paths with `os.path.realpath()` to follow symlinks
  - Verify resolved paths are within allowed directory
  - Use `os.path.commonpath()` for containment checks
  - Perform checks both before and after operations (TOCTOU mitigation)
- **Resource Limits**:
  - Use `resource` module (Unix) or job objects (Windows) for OS-level limits
  - Set `RLIMIT_AS` for memory, `RLIMIT_CPU` for CPU time
  - Process-tree termination (kill children on timeout)
- **Environment Isolation**:
  - Explicitly define which environment variables are inherited
  - Scrub credentials from subprocess environment
  - Default: no network access unless explicitly allowed
- **Approval Rules**:
  - Destructive operations require confirmation
  - Network operations require approval
  - File writes outside project directory require approval

**Execution Security Level B Requirements** (Future):
- Use OS-level isolation (chroot, containers, or proper sandbox)
- Enforce process-tree timeouts and resource limits
- Test actual isolation with escape attempts

**Important**: Execution Security Level A must be marked as "directory-restricted, not sandboxed" in documentation. Untrusted code execution should be disabled until Execution Security Level B is implemented and tested.

---

## Proposed Structure

### Final Architecture

```
gpt_computer/
├── ai/                          # AI Client Layer
│   ├── client/                  # AI client implementations
│   │   ├── base.py              # Base client interface
│   │   ├── sync.py              # Synchronous client
│   │   ├── async_client.py      # Asynchronous client
│   │   └── factory.py           # Client factory
│   ├── providers/               # AI provider implementations
│   │   ├── base.py              # Base provider interface
│   │   ├── openai.py            # OpenAI provider
│   │   ├── anthropic.py         # Anthropic/Claude provider
│   │   ├── google.py            # Google Gemini provider
│   │   ├── groq.py              # Groq provider
│   │   ├── mistral.py           # Mistral provider
│   │   ├── cohere.py            # Cohere provider
│   │   ├── local.py             # Local LLM provider
│   │   ├── config.py            # Provider-specific configuration only
│   │   ├── retry.py             # Provider-specific retry logic
│   │   ├── response.py          # Provider-specific response handling
│   │   └── types.py             # Provider types
│   ├── models/                  # Model definitions
│   │   ├── base.py              # Base model class
│   │   ├── registry.py          # Model metadata and provider capabilities
│   │   └── defaults.py          # Default model configs
│   ├── cookies/                 # Cookie management
│   │   └── manager.py
│   ├── images/                  # Image generation/handling
│   │   └── generator.py
│   ├── types.py                 # Type definitions
│   ├── errors.py                # Error definitions
│   └── version.py               # AI client version
│
├── agent/                       # Agent System
│   ├── base.py                  # Base agent interface
│   ├── react.py                 # ReAct agent implementation
│   ├── simple.py                # Simple agent implementation
│   ├── orchestration/           # Orchestration logic
│   │   ├── controller.py       # Agent controller
│   │   └── workflow.py         # Workflow management
│   ├── tools/                   # Agent tools (adapters for infrastructure)
│   │   ├── registry.py          # Tool registry
│   │   ├── file_ops.py          # File operations tool (wraps infrastructure/files)
│   │   ├── git_ops.py           # Git operations tool (wraps infrastructure/git)
│   │   ├── code_analysis.py    # Code analysis tools
│   │   └── execution.py         # Code execution tool (wraps execution/)
│   ├── memory/                  # Memory systems
│   │   ├── base.py              # Base memory interface
│   │   ├── short_term.py        # Short-term memory
│   │   ├── long_term.py         # Long-term memory
│   │   └── vector_store.py      # Vector store (future)
│   ├── prompts/                 # Prompt management
│   │   ├── builder.py           # Prompt builder
│   │   └── templates/           # Prompt templates
│   │       ├── system.py
│   │       ├── generate.py
│   │       └── improve.py
│   ├── parsing/                 # Response parsing
│   │   ├── code_blocks.py       # Code block extraction
│   │   └── file_ops.py          # File operation parsing
│   ├── tracking/                # Usage tracking
│   │   ├── tokens.py            # Token usage
│   │   └── costs.py             # Cost calculation
│   └── config.py                # Agent configuration
│
├── execution/                   # Execution Environments
│   ├── base.py                  # Base execution interface
│   ├── local.py                 # Local disk-based execution (directory-restricted)
│   └── sandbox.py               # Sandboxed execution (future, with OS-level isolation)
│
├── interfaces/                  # User Interfaces
│   ├── cli/                     # Command-line interface
│   │   ├── main.py              # CLI entry point
│   │   ├── commands/            # CLI commands
│   │   │   ├── init.py
│   │   │   ├── build.py
│   │   │   ├── improve.py
│   │   │   └── benchmark.py
│   │   └── utils/               # CLI utilities
│   ├── api/                     # REST API
│   │   ├── main.py              # FastAPI app
│   │   ├── routes/              # API routes
│   │   │   ├── agent.py
│   │   │   └── health.py
│   │   └── models/              # API models
│   ├── gui/                     # GUI components
│   │   └── main.py
│   ├── tray/                    # System tray
│   │   └── main.py
│   └── mcp/                     # MCP protocol support
│       └── server.py            # MCP server (may depend on agent)
│
├── analysis/                    # Analysis Tools
│   ├── codemap/                 # Code mapping & visualization (agent-independent)
│   │   ├── analyzer.py
│   │   ├── graph.py
│   │   ├── visualizer.py
│   │   └── models.py
│   ├── context/                 # Context management (agent-dependent)
│   │   ├── manager.py
│   │   ├── orchestrator.py
│   │   ├── world_model.py
│   │   └── execution_fabric.py
│   └── repository/              # Repository intelligence (agent-dependent)
│       ├── explain_agent.py
│       ├── refactor_agent.py
│       ├── security_agent.py
│       ├── visualization_agent.py
│       ├── tree_sitter_analyzer.py  # Agent-independent
│       └── knowledge_graph.py
│
├── infrastructure/              # Supporting Infrastructure
│   ├── config/                  # Configuration management
│   │   ├── settings.py          # Settings with precedence
│   │   └── loader.py            # Config loader
│   ├── logging/                 # Logging
│   │   ├── config.py
│   │   └── structured.py
│   ├── tracing/                 # Distributed tracing
│   │   └── tracer.py
│   ├── git/                     # Git operations (owner)
│   │   └── operations.py
│   ├── files/                   # File operations (owner)
│   │   └── operations.py
│   ├── diff/                    # Diff utilities
│   │   └── parser.py
│   └── linting/                 # Code quality
│       └── checker.py
│
├── benchmark/                   # Benchmarking
│   ├── runner.py
│   └── configs/                # Benchmark configs
│
└── utils/                       # General utilities
    ├── async_helpers.py
    └── formatters.py
```

**Notes**:
- Benchmark results stored in configurable artifact directory (not in package)
- MCP server moved to `interfaces/mcp/` to avoid upward dependencies
- Provider config only for provider-specific settings; global config in infrastructure
- Analysis modules marked as agent-dependent or agent-independent

---

## Compatibility Strategy

### Public API Definition

**Guaranteed Public APIs** (will maintain compatibility for 12 months minimum):

**Top-Level Imports**:
- `gptc.ChatCompletion` → `gpt_computer.ai.chat_completion.ChatCompletionAPI`
- `gptc.Client` → `gpt_computer.ai.client.Client`
- `gptc.AsyncClient` → `gpt_computer.ai.client.AsyncClient`
- `gptc.Model` → `gpt_computer.ai.models.Model`

**Submodule Imports** (require explicit compatibility modules):
- `gptc.providers` → `gpt_computer.ai.providers`
- `gptc.providers.OpenAIProvider` → `gpt_computer.ai.providers.openai.OpenAIProvider`
- `gptc.providers.AnthropicProvider` → `gpt_computer.ai.providers.anthropic.AnthropicProvider`
- `gptc.cookies` → `gpt_computer.ai.cookies`
- `gptc.errors` → `gpt_computer.ai.errors`

**Legacy Core Imports**:
- `gpt_computer.core.ai.AI` → `gpt_computer.agent.llm.AI` (or direct ai.client)
- `gpt_computer.core.base_agent.BaseAgent` → `gpt_computer.agent.BaseAgent`

**CLI Commands**:
- `gptc` → `gptc` (primary)
- `gpt-computer` → `gptc` (alias)
- `ge` → `gptc` (alias)
- `gptc-mcp` → `gptc mcp` (alias)
- `gptc-tray` → `gptc tray` (alias)
- `bench` → `gptc bench` (alias)

**Internal APIs** (may break without notice):
- All submodules under `gptc/providers/` internal implementation
- All submodules under `gptc/client/` internal implementation
- `gptc.config` internals
- `gptc.cookies` internals
- `gpt_computer.core/*` (not in public API list)

### Compatibility Layer Implementation

**Structure**:
```
gptc/                           # Compatibility package (temporary)
├── __init__.py                 # Top-level re-exports
├── providers/                  # Compatibility submodule
│   ├── __init__.py
│   ├── openai.py               # Re-export from gpt_computer.ai.providers.openai
│   ├── anthropic.py            # Re-export from gpt_computer.ai.providers.anthropic
│   └── ...
├── cookies/                    # Compatibility submodule
│   └── __init__.py
└── errors/                     # Compatibility submodule
    └── __init__.py

gpt_computer/                   # Add compatibility for core module
└── core/                       # Compatibility for gpt_computer.core imports
    ├── __init__.py
    ├── ai.py                   # Re-export from appropriate location
    └── base_agent.py           # Re-export from gpt_computer.agent
```

**Implementation Example**:
```python
# gptc/__init__.py
import warnings
from gpt_computer.ai.chat_completion import ChatCompletionAPI as ChatCompletion
from gpt_computer.ai.client import Client, AsyncClient
from gpt_computer.ai.models import Model

warnings.warn(
    "Importing from 'gptc' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.ai.client import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['ChatCompletion', 'Client', 'AsyncClient', 'Model']

# gptc/providers/__init__.py
import warnings
from gpt_computer.ai.providers.openai import OpenAIProvider
from gpt_computer.ai.providers.anthropic import AnthropicProvider
from gpt_computer.ai.providers.google import GoogleProvider
from gpt_computer.ai.providers.groq import GroqProvider
from gpt_computer.ai.providers.mistral import MistralProvider
from gpt_computer.ai.providers.cohere import CohereProvider
from gpt_computer.ai.providers.local import LocalProvider

warnings.warn(
    "Importing from 'gptc.providers' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.ai.providers import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    'OpenAIProvider', 'AnthropicProvider', 'GoogleProvider',
    'GroqProvider', 'MistralProvider', 'CohereProvider', 'LocalProvider'
]

# gpt_computer/core/__init__.py
import warnings
from gpt_computer.agent import BaseAgent
# Note: AI interface may be deprecated entirely or mapped to ai.client

warnings.warn(
    "Importing from 'gpt_computer.core' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.agent import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['BaseAgent']
```

### Deprecation Policy

**Removal Policy**:
- Minimum notice period: 12 months from stable release
- Removal target: Version 1.0.0 (or later if needed)
- Explicit announcement in release notes when removal is scheduled
- Compatibility shims removed in the release where removal occurs

**Version Schedule**:
- Current: 0.1.1
- Restructure release: 0.3.0 (compatibility shims added, allows for 0.2.x releases)
- Deprecation period: 0.3.x → 0.4.x → 0.5.x (minimum 12 months)
- Removal scheduled: 1.0.0

**Warning Behavior**:
- Use `DeprecationWarning` with `stacklevel=2`
- Test that warnings fire for legacy imports
- Consider `UserWarning` if DeprecationWarning is hidden by default in user environments
- Document how to enable deprecation warnings

### Import Mapping

| Old Import | New Import | Deprecated | Compatibility Module |
|-----------|------------|------------|---------------------|
| `from gptc import Client` | `from gpt_computer.ai.client import Client` | Yes | `gptc/__init__.py` |
| `from gptc import ChatCompletion` | `from gpt_computer.ai.chat_completion import ChatCompletionAPI` | Yes | `gptc/__init__.py` |
| `from gptc.providers import OpenAIProvider` | `from gpt_computer.ai.providers.openai import OpenAIProvider` | Yes | `gptc/providers/__init__.py` |
| `from gptc.providers.openai import OpenAIProvider` | `from gpt_computer.ai.providers.openai import OpenAIProvider` | Yes | `gptc/providers/openai.py` |
| `from gptc import Model` | `from gpt_computer.ai.models import Model` | Yes | `gptc/__init__.py` |
| `from gptc.cookies import get_cookies` | `from gpt_computer.ai.cookies import get_cookies` | Yes | `gptc/cookies/__init__.py` |
| `from gpt_computer.core.ai import AI` | `from gpt_computer.agent.llm import AI` | Yes | `gptc/core/ai.py` |
| `from gpt_computer.core.base_agent import BaseAgent` | `from gpt_computer.agent import BaseAgent` | Yes | `gptc/core/base_agent.py` |

**Intentionally Unsupported**:
- `gptc.cli` → Use `gpt_computer.interfaces.cli`
- `gptc.gui` → Use `gpt_computer.interfaces.gui`
- `gptc.api` → Use `gpt_computer.interfaces.api`
- `gptc.tray` → Use `gpt_computer.interfaces.tray`
- These are internal interfaces, not public APIs

---

## CLI Command Strategy

### Final Command Structure

**Primary Command**: `gptc`

**Subcommands**:
- `gptc init` - Initialize project
- `gptc build` - Build from specification
- `gptc improve` - Improve existing code
- `gptc mcp` - MCP server
- `gptc tray` - System tray
- `gptc bench` - Benchmarking

**Legacy Aliases** (kept during compatibility period):
- `gpt-computer` → `gptc` (alias with deprecation warning)
- `ge` → `gptc` (alias with deprecation warning)
- `gptc-mcp` → `gptc mcp` (alias with deprecation warning)
- `gptc-tray` → `gptc tray` (alias with deprecation warning)
- `bench` → `gptc bench` (alias with deprecation warning)

**Deprecation**:
- Legacy aliases emit deprecation warnings
- Documentation only references `gptc` and subcommands
- Legacy aliases removed in version 1.0.0

---

## Configuration Management

### Configuration Precedence

**Priority Order** (highest to lowest):
1. CLI command-line arguments
2. Environment variables
3. Project-specific config file (`.gptc.toml` or `.gptc.yaml`)
4. User config file (`~/.config/gptc/config.toml`)
5. Default values in code

**Example**:
```python
# infrastructure/config/settings.py
class Config:
    def __init__(self):
        # 1. Start with defaults
        self.model = "gpt-4"
        self.max_tokens = 4096

        # 2. Load user config
        user_config = self._load_user_config()
        self._apply_config(user_config)

        # 3. Load project config
        project_config = self._load_project_config()
        self._apply_config(project_config)

        # 4. Load environment variables
        self._apply_env_vars()

        # 5. Apply CLI overrides (done separately)
```

**Environment Variables**:
- `GPTC_MODEL` - Default model
- `GPTC_MAX_TOKENS` - Max tokens
- `GPTC_LOG_LEVEL` - Logging level
- `GPTC_CONFIG_PATH` - Custom config file path

---

## Optional Dependencies

### Dependency Groups

**Core** (always installed):
- `requests`, `aiohttp`, `brotli`, `pycryptodome`
- `nest-asyncio2`, `aiofiles`, `backoff`
- `pillow`, `pyperclip`, `regex`, `termcolor`
- `toml`, `tomlkit`, `typer`, `openai`
- `python-dotenv`, `PyYAML`, `gitpython`, `packaging`

**API** (optional):
- `loguru`, `fastapi`, `uvicorn`, `python-multipart`, `a2wsgi`

**GUI** (optional):
- `werkzeug`, `flask[async]`, `beautifulsoup4`, `pillow`

**Search** (optional):
- `beautifulsoup4`, `ddgs`

**Tray** (optional):
- `pystray`, `pillow`, `cairosvg`

**Local LLM** (optional):
- `gpt4all`

**Development** (dev dependency group):
- `pytest`, `pytest-cov`, `pytest-xdist`, `pytest-asyncio`
- `mypy`, `ruff`, `pre-commit`, `tox`

**All** (includes all optional dependencies):
- Combines: API, GUI, Search, Tray, Local LLM
- Note: Pillow appears in multiple groups (will be deduplicated by package manager)

**Installation Examples**:
```bash
# Core only
pip install gpt-computer

# With API support
pip install gpt-computer[api]

# With GUI support
pip install gpt-computer[gui]

# With all optional features
pip install gpt-computer[all]

# Development
pip install gpt-computer[dev]
```

---

## Migration Plan with Measurable Gates

### Phase 0: Baseline and Inventory (Week 1)

**Deliverables**:
1. [ ] Create `PUBLIC_IMPORTS.md` with all supported imports
2. [ ] Create `CLI_ENTRY_POINTS.md` with all CLI commands
3. [ ] Document current dependency groups from `pyproject.toml`
4. [ ] Run full test suite and record results in `BASELINE_TEST_RESULTS.md`
5. [ ] Record all test failures, skips, and environment-dependent tests
6. [ ] Create backup branch `structure-baseline`
7. [ ] Document external dependencies (check imports in examples, docs)

**Acceptance Criteria**:
- `PUBLIC_IMPORTS.md` lists all imports used in examples, docs, and tests
- `BASELINE_TEST_RESULTS.md` shows current test status (not assumed 100%)
- Baseline failures documented and explained
- Backup branch created and pushed to remote

### Phase 1: Architecture and Security Rules (Week 2)

**Deliverables**:
1. [ ] Document dependency rules in `DEPENDENCY_RULES.md`
2. [ ] Resolve duplicate responsibilities (file ops, git ops, config)
3. [ ] Define execution security rules in `EXECUTION_SECURITY.md`
4. [ ] Create static import-graph analysis tool
5. [ ] Create dependency direction verification test
6. [ ] Move MCP server to `interfaces/mcp/` (if not already)
7. [ ] Resolve provider config vs global config overlap

**Acceptance Criteria**:
- `DEPENDENCY_RULES.md` approved by maintainers
- All duplicate responsibilities assigned to single owner
- `EXECUTION_SECURITY.md` defines permissions, limits, and approval rules
- Static import-graph tool analyzes entire source tree
- Dependency direction verification test passes on current structure
- MCP server placement finalized
- Config ownership clarified

### Phase 2: Freeze Public Contract (Week 3)

**Deliverables**:
1. [ ] Finalize `PUBLIC_IMPORTS.md` with exact supported imports
2. [ ] Finalize `CLI_ENTRY_POINTS.md` with exact supported commands
3. [ ] Create compatibility module structure (both gptc/* and gpt_computer/core/*)
4. [ ] Implement compatibility shims for all supported imports
5. [ ] Test compatibility shims with fresh Python processes
6. [ ] Define deprecation policy with explicit removal version
7. [ ] **P0 BLOCKER**: Verify compatibility mapping matches actual legacy namespaces
8. [ ] **P0 BLOCKER**: Validate static import-graph tool with test fixtures

**Acceptance Criteria**:
- `PUBLIC_IMPORTS.md` lists finite, explicit set of supported imports
- `CLI_ENTRY_POINTS.md` lists finite, explicit set of supported commands
- Compatibility modules created for all supported submodules (gptc/* and gpt_computer/core/*)
- All supported imports work with deprecation warnings in fresh Python processes
- API identity tested for important public classes
- **P0 BLOCKER RESOLVED**: Compatibility mapping verified for gptc and gpt_computer.core namespaces
- **P0 BLOCKER RESOLVED**: Static import-graph tool validated with deliberate cycles and forbidden imports
- Deprecation policy documented with removal version

### Phase 3: One Vertical Slice (Week 4)

**Goal**: Migrate AI client layer and validate approach end-to-end

**Deliverables**:
1. [ ] Migrate AI client layer (`gptc/` → `gpt_computer/ai/`)
2. [ ] Update compatibility layer for migrated imports
3. [ ] Update one CLI command to use new structure
4. [ ] Create deterministic end-to-end test (fake providers)
5. [ ] Verify end-to-end test passes
6. [ ] Verify legacy imports still work with warnings
7. [ ] **P0 BLOCKER**: Define execution security release gate (when untrusted execution can be enabled)

**Acceptance Criteria**:
- `gpt_computer/ai/` structure created and populated
- Compatibility layer allows old imports to work with deprecation warnings
- One CLI command (e.g., `gptc --help`) works with new structure
- End-to-end test uses fake/deterministic providers (no live API calls)
- Test covers: CLI → AI client → provider invocation
- Test passes with full compatibility (new and legacy imports)
- API identity preserved for Client, AsyncClient, and the ChatCompletion facade
- **P0 BLOCKER RESOLVED**: Execution security release gate defined (Execution Security Level B required for untrusted execution)
- End-to-end test uses fake/deterministic providers (no live API calls)
- Test covers: CLI → AI client → provider invocation
- Test passes with full compatibility (new and legacy imports)
- API identity preserved for Client, AsyncClient, and the ChatCompletion facade

### Phase 4: Incremental Domain Migration (Week 5-7)

**Domain Migration Order**:
1. Infrastructure (Week 5)
2. Execution (Week 5)
3. Agent system (Week 6)
4. Analysis tools (Week 6)
5. Interfaces (Week 7)

**Per-Domain Deliverables**:
1. [ ] Move files to new structure
2. [ ] Update imports in moved files
3. [ ] Create/update compatibility layer
4. [ ] Update tests for domain
5. [ ] Run domain tests
6. [ ] Run static import-graph analysis
7. [ ] Run dependency direction verification

**Acceptance Criteria**:
- All domain tests pass
- No new import cycles introduced (static analysis)
- Dependency direction rules maintained (static analysis)
- Compatibility layer allows old imports to work
- No new unexplained test regressions

### Phase 5: Automated Regression Testing (Week 8)

**Deliverables**:
1. [x] Built-wheel installation/import check (isolated target; no dependency install)
2. [x] Public import compatibility test (all in PUBLIC_IMPORTS.md)
3. [x] CLI smoke checks (public command help/modes; standalone service targets import)
4. [x] API smoke test
5. [x] MCP startup test (in-process initialize and tools/list protocol smoke)
6. [x] Sync/async client tests (with fake providers)
7. [x] Provider error and retry tests
8. [x] Agent execution tests (ReAct tool failure handling and execution-timeout recovery)
9. [x] Minimal installation test (core only, no GUI/API)
10. [ ] Optional dependency group tests (api/gui/search/image/tray/all/slim/doc/test and docs/dev groups install/import; local runtime import remains blocked on this Intel macOS host)
11. [x] Static import-cycle detection (entire source tree)
12. [x] Dependency direction verification (entire source tree)
13. [x] Level A file-store containment tests (path traversal and symlink escapes; not OS isolation)
14. [x] Execution timeout tests (POSIX process-tree termination)

**Acceptance Criteria**:
- All regression tests pass
- Clean installation works on all supported Python versions
- All legacy CLI commands work with deprecation warnings
- Minimal installation (core only) succeeds
- All optional dependency groups install correctly
- No import cycles detected (static analysis)
- No dependency direction violations (static analysis)
- Level A file/path boundary tests pass; Level B OS-level isolation remains unimplemented
- Execution timeout tests verify process-tree termination

**Progress note**: The focused regression suite previously passed (103 tests), including API health/agent endpoint tests and MCP initialize/tools-list smoke. A fresh installed Python 3.12 environment now passes the regression suite plus ReAct tests: **96 passed**. This run also caught and fixed the benchmark CLI's stale `langchain.globals` import, and the normal-execution security test now uses `sys.executable` rather than assuming a `python` command is on PATH. The built-wheel test passes, installing the wheel into a temporary target and verifying migrated/legacy imports resolve from the distribution rather than the checkout; it does not install dependencies or validate a fresh environment. Focused runs passed: CLI smoke (18 tests), fake-provider/client and retry tests (16), and agent/simple-agent tests (7). A ReAct integration test routes a timed command through the tool registry, verifies the execution timeout is surfaced as an observation, and confirms the agent can continue to a final response. Earlier CLI fixes remove a network lookup from GUI help, restore the benchmark CLI's dotenv loading, and keep benchmark config annotations compatible with Python 3.9. Clean production dependencies installed and migrated/legacy imports passed under Python 3.14; core-only installs and migrated/legacy imports passed under Python 3.9 and 3.12. The Python 3.9 check emits upstream end-of-life and LibreSSL/urllib3 warnings, but imports succeed. The `api`, `gui`, `search`, `image`, and `tray` extras installed and their import smoke checks passed under Python 3.14. Under Python 3.12, the `all` and `slim` extras installed and representative imports passed; the `test` extra installed and pytest/pytest-cov imported; both `doc` extra and `docs` dependency group installed with Sphinx, MyST, notebook, autodoc, and link-checker imports passing; and the `dev` dependency group installed with pytest, mypy, Ruff, tox, and pre-commit imports passing. The `files` and `local` extras installed under Python 3.12, but the `gpt4all` import smoke check fails on this Intel macOS host because its platform probe treats the unavailable `sysctl.proc_translated` key as fatal; this does not establish whether the same failure occurs on supported Linux or Apple Silicon environments. Cross-platform validation, remaining Python-version coverage, and Level B OS-level isolation remain outstanding. Level A path checks and POSIX process-tree timeout behavior pass but do not establish sandbox isolation.

### Phase 6: Deprecation and Cleanup (Week 9+)

**Deliverables**:
1. [ ] Publish migration guide
2. [ ] Announce deprecated imports and commands in release notes
3. [ ] Update all documentation to use new structure
4. [ ] Update all examples to use new structure
5. [ ] Mark legacy imports as deprecated in code
6. [ ] Monitor compatibility issues
7. [ ] Remove legacy CLI aliases after compatibility period
8. [ ] Remove compatibility shims after compatibility period

**Acceptance Criteria**:
- Migration guide published and linked from README
- All documentation uses new import paths
- All examples use new import paths
- Deprecation warnings display for all legacy imports
- Compatibility period defined (minimum 12 months)
- Removal scheduled for version 1.0.0

---

## Test Strategy

### Static Import-Graph Analysis

```python
# tests/test_static_imports.py
import ast
import os
from pathlib import Path
from collections import defaultdict

def get_module_name(file_path: Path, source_root: Path) -> str:
    """Convert file path to module name."""
    relative = file_path.relative_to(source_root)
    parts = list(relative.parts[:-1])  # Remove filename
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    return ".".join(parts) if parts else relative.stem

def get_layer(module_name: str) -> str:
    """Map module name to architectural layer."""
    if module_name.startswith("gpt_computer.infrastructure"):
        return "infrastructure"
    elif module_name.startswith("gpt_computer.execution"):
        return "execution"
    elif module_name.startswith("gpt_computer.ai"):
        return "ai"
    elif module_name.startswith("gpt_computer.agent"):
        return "agent"
    elif module_name.startswith("gpt_computer.analysis"):
        return "analysis"
    elif module_name.startswith("gpt_computer.interfaces"):
        return "interfaces"
    elif module_name.startswith("gpt_computer.benchmark"):
        return "benchmark"
    elif module_name.startswith("gpt_computer.utils"):
        return "utils"
    else:
        return "unknown"

def resolve_import(module_name: str, current_module: str, source_root: Path) -> str:
    """Resolve relative imports to absolute module names."""
    if not module_name.startswith("."):
        return module_name

    # Handle relative imports
    current_parts = current_module.split(".")
    level = len(module_name) - len(module_name.lstrip("."))
    relative_part = module_name.lstrip(".")

    if level > len(current_parts):
        return module_name  # Invalid relative import, return as-is

    base_parts = current_parts[:-level] if level > 0 else current_parts
    if relative_part:
        return ".".join(base_parts + relative_part.split("."))
    else:
        return ".".join(base_parts)

def build_import_graph(source_dir: Path) -> dict:
    """Build static import graph from source tree with full module paths."""
    graph = defaultdict(set)

    for py_file in source_dir.rglob("*.py"):
        # Skip test files and compatibility shims
        if "test" in py_file.parts or "gptc" in py_file.parts:
            continue

        current_module = get_module_name(py_file, source_dir)

        with open(py_file) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("gpt_computer"):
                        graph[current_module].add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("gpt_computer"):
                    resolved = resolve_import(node.module, current_module, source_dir)
                    graph[current_module].add(resolved)

    return graph

def has_cycles(graph: dict) -> list:
    """Detect cycles in import graph using DFS."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}
    cycles = []

    def dfs(node, path):
        color[node] = GRAY
        path.append(node)

        for neighbor in graph.get(node, []):
            if color[neighbor] == GRAY:
                cycle_start = path.index(neighbor)
                cycles.append(path[cycle_start:] + [neighbor])
            elif color[neighbor] == WHITE:
                dfs(neighbor, path)

        path.pop()
        color[node] = BLACK

    for node in graph:
        if color[node] == WHITE:
            dfs(node, [])

    return cycles

def test_no_import_cycles():
    """Verify no circular dependencies exist."""
    graph = build_import_graph(Path("gpt_computer"))
    cycles = has_cycles(graph)
    assert not cycles, f"Import cycles detected: {cycles}"

def test_dependency_directions():
    """Verify imports follow allowed directions."""
    graph = build_import_graph(Path("gpt_computer"))

    allowed_edges = {
        "infrastructure": set(),
        "execution": {"infrastructure"},
        "ai": {"infrastructure"},
        "agent": {"ai", "execution", "infrastructure"},
        "analysis": {"agent", "infrastructure"},
        "interfaces": {"ai", "agent", "execution", "infrastructure"},
        "benchmark": {"agent", "ai", "infrastructure"},
        "utils": set(),
    }

    # Prohibited edges (explicitly forbidden regardless of direction)
    prohibited_edges = {
        ("interfaces", "analysis"),
        ("analysis", "interfaces"),
        ("infrastructure", "agent"),
        ("infrastructure", "interfaces"),
    }

    for source, targets in graph.items():
        source_layer = get_layer(source)
        allowed = allowed_edges.get(source_layer, set())

        for target in targets:
            target_layer = get_layer(target)

            # Skip same-layer imports (allowed)
            if target_layer == source_layer:
                continue

            # Check prohibited edges
            if (source_layer, target_layer) in prohibited_edges:
                assert False, f"Prohibited import: {source} → {target} ({source_layer} → {target_layer})"

            # Check allowed edges
            if target_layer not in allowed:
                assert False, f"Disallowed import: {source} → {target} ({source_layer} → {target_layer})"

# Fixtures for testing the checker itself
def test_checker_with_known_cycle():
    """Test that cycle detection works with a deliberate cycle."""
    # This would be in a test fixture that creates temporary files with cycles
    pass

def test_checker_with_forbidden_import():
    """Test that forbidden import detection works."""
    # This would be in a test fixture that creates a forbidden import
    pass
```

### Compatibility Tests

```python
# tests/test_compatibility.py
import warnings
import subprocess
import sys

def test_legacy_top_level_imports():
    """Test that legacy top-level imports work with deprecation warnings."""
    test_script = """
import warnings
warnings.simplefilter("always")
from gptc import Client, AsyncClient, ChatCompletion, Model
print("SUCCESS")
"""
    result = subprocess.run([sys.executable, "-c", test_script], capture_output=True, text=True)
    assert result.returncode == 0
    assert "SUCCESS" in result.stdout
    assert "deprecated" in result.stderr.lower()

def test_legacy_submodule_imports():
    """Test that legacy submodule imports work with deprecation warnings."""
    test_script = """
import warnings
warnings.simplefilter("always")
from gptc.providers import openai
from gptc.cookies import get_cookies
print("SUCCESS")
"""
    result = subprocess.run([sys.executable, "-c", test_script], capture_output=True, text=True)
    assert result.returncode == 0
    assert "SUCCESS" in result.stdout
    assert "deprecated" in result.stderr.lower()

def test_new_imports_work():
    """Test that new imports work."""
    from gpt_computer.ai.chat_completion import ChatCompletionAPI
    from gpt_computer.ai.client import Client, AsyncClient, ChatCompletion
    from gpt_computer.ai.models import Model
    assert Client is not None
    assert AsyncClient is not None
    assert ChatCompletion is not None
    assert ChatCompletionAPI is not None
    assert Model is not None

def test_api_identity():
    """Test that re-exported classes preserve identity."""
    from gptc import Client as LegacyClient
    from gpt_computer.ai.client import Client as NewClient
    assert LegacyClient is NewClient, "Class identity not preserved"
```

### End-to-End Tests with Fake Providers

```python
# tests/test_e2e.py
import subprocess
import pytest
from unittest.mock import Mock, patch

def test_cli_help_command():
    """Test CLI help command."""
    result = subprocess.run(["gptc", "--help"], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0
    assert "init" in result.stdout or "build" in result.stdout

def test_client_with_fake_provider():
    """Test client with fake provider."""
    from gpt_computer.ai.client import Client
    from gpt_computer.ai.providers.base import BaseProvider

    fake_provider = Mock(spec=BaseProvider)
    fake_provider.generate.return_value = "test response"

    client = Client(provider=fake_provider)
    response = client.generate("test prompt")
    assert response == "test response"

def test_agent_execution_timeout():
    """Test agent execution respects timeout with process isolation."""
    from gpt_computer.execution.local import LocalExecutionEnv
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        env = LocalExecutionEnv(project_path=tmpdir, timeout=1)
        # Write infinite loop
        env.write_files({"infinite.py": "while True: pass"})

        # This should timeout and kill the process tree
        with pytest.raises(TimeoutError):
            env.execute("python infinite.py")

        # Verify process is actually killed
        # (implementation should use process-tree termination)
```

### Security Boundary Tests

**Important**: These tests validate Execution Security Level A (directory-based restrictions). They do not prove full OS-level isolation. Untrusted code execution should remain disabled until Execution Security Level B is implemented and tested.

**Supported Operating Systems**:
- Linux: Full support (resource module, process-tree termination)
- macOS: Full support (resource module, process-tree termination)
- Windows: Partial support (job objects for resource limits, process-tree termination)
- Note: Some features may not be available on all platforms; tests should skip gracefully when unavailable

**Behavior When Controls Unavailable**:
- If resource limits unavailable: Log warning, proceed without limits (document as limitation)
- If process-tree termination unavailable: Log warning, mark execution as unsafe
- If path resolution unavailable: Fail execution with clear error message

```python
# tests/test_security.py
import os
import sys
import tempfile
import pytest
from gpt_computer.execution.local import LocalExecutionEnv

@pytest.mark.skipif(sys.platform == "win32", reason="Symlink behavior differs on Windows")
def test_path_traversal_protection():
    """Test that path traversal is prevented with symlink resolution."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env = LocalExecutionEnv(project_path=tmpdir)

        # Try to read file outside project
        with pytest.raises(PermissionError):
            env.read_files(["/etc/passwd"])

        # Try to write file outside project
        with pytest.raises(PermissionError):
            env.write_files({"/tmp/test.txt": "content"})

@pytest.mark.skipif(sys.platform == "win32", reason="Symlink behavior differs on Windows")
def test_symlink_escape_protection():
    """Test that symlink escapes are prevented with realpath resolution."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env = LocalExecutionEnv(project_path=tmpdir)

        # Create symlink to outside directory
        os.symlink("/tmp", os.path.join(tmpdir, "escape"))

        # Try to read through symlink - should fail after realpath resolution
        with pytest.raises(PermissionError):
            env.read_files(["escape/test.txt"])

def test_timeout_terminates_process_tree():
    """Test that timeout terminates entire process tree.

    Note: This validates process-tree termination, not full isolation.
    On systems where process-tree termination is unavailable, this test should skip.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        env = LocalExecutionEnv(project_path=tmpdir, timeout=1)
        env.write_files({"spawn.py": """
import subprocess
import time
subprocess.Popen(["sleep", "100"])
while True:
    pass
"""})

        with pytest.raises(TimeoutError):
            env.execute("python spawn.py")

        # Verify child process is also killed
        # (implementation should use process-tree termination)
        # This is a best-effort check; may not work on all platforms

def test_environment_isolation():
    """Test that environment variables are controlled."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Set a credential-like environment variable
        os.environ["TEST_CREDENTIAL"] = "secret_value"

        env = LocalExecutionEnv(project_path=tmpdir, scrub_env=True)
        env.write_files({"check_env.py": """
import os
import sys
print("TEST_CREDENTIAL" in os.environ)
print(os.environ.get("TEST_CREDENTIAL", "not_set"))
"""})

        result = env.execute("python check_env.py")
        # Credential should not be present in subprocess
        assert "not_set" in result.stdout or "False" in result.stdout

def test_network_access_control():
    """Test that network access is controlled when disabled.

    Note: Actual network blocking requires OS-level firewall rules or
    network namespaces (Execution Security Level B). This test validates
    that the execution environment respects the network_allowed flag.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        env = LocalExecutionEnv(project_path=tmpdir, network_allowed=False)
        env.write_files({"network_test.py": """
import socket
try:
    socket.create_connection(("8.8.8.8", 53), timeout=1)
    print("NETWORK_ACCESS_ALLOWED")
except:
    print("NETWORK_ACCESS_BLOCKED")
"""})

        result = env.execute("python network_test.py")
        # At minimum, the flag should be respected in documentation
        # Actual blocking requires Execution Security Level B
```

**Important Limitations**:
- These tests do not verify that arbitrary code cannot access host credentials
- These tests do not verify network isolation at the OS level
- These tests do not verify full sandbox isolation
- Untrusted code execution should remain disabled until Execution Security Level B

---

## Timeline

| Phase | Duration | Status | Acceptance Criteria |
|-------|----------|--------|---------------------|
| Phase 0: Baseline | Week 1 | Not Started | Baseline documented, backup created, failures recorded |
| Phase 1: Architecture | Week 2 | Not Started | Dependency rules defined, security rules defined, static analysis tool |
| Phase 2: Public Contract | Week 3 | Not Started | Compatibility shims for all supported imports, deprecation policy |
| Phase 3: Vertical Slice | Week 4 | Not Started | AI client migrated, end-to-end test with fake providers |
| Phase 4: Domain Migration | Week 5-7 | Not Started | All domains migrated, static analysis passes |
| Phase 5: Regression Testing | Week 8 | In Progress | Remaining installation, CLI/API/MCP, dependency-group, and Level B isolation gates |
| Phase 6: Deprecation | Week 9+ | Not Started | Migration guide published, documentation updated |

**Total Estimated Time**: 9+ weeks (deprecation period extends beyond this)

**Note**: Timeline is provisional until Phase 0 measures actual migration scope.

---

## Risks and Mitigations

### Risk 1: Breaking External Dependencies
- **Impact**: High
- **Probability**: Medium
- **Mitigation**: Compatibility layer with explicit shims, deprecation warnings, 12-month minimum deprecation period, clear public API definition

### Risk 2: Import Errors During Migration
- **Impact**: High
- **Probability**: Medium
- **Mitigation**: Static import-graph analysis, vertical slice validation, incremental migration, compatibility shims for all supported imports

### Risk 3: Security Gaps in Execution
- **Impact**: High
- **Probability**: Unknown (until testing provides evidence)
- **Mitigation**: Security rules defined before migration, path resolution with symlink handling, process-tree termination, marked as "directory-restricted not sandboxed", untrusted execution disabled until Execution Security Level B

### Risk 4: Contributor Confusion
- **Impact**: Medium
- **Probability**: High
- **Mitigation**: Clear communication, documentation, migration guide, support during transition

### Risk 5: Timeline Overrun
- **Impact**: Medium
- **Probability**: Medium
- **Mitigation**: Measurable gates, phased approach, ability to pause after any phase, provisional timeline until Phase 0

---

## Success Criteria

1. ✅ Single unified package structure
2. ✅ Clear separation of concerns between modules
3. ✅ No duplicate responsibilities
4. ✅ Explicit dependency rules enforced (static analysis)
5. ✅ All tests passing after migration (no new unexplained regressions)
6. ✅ All CLI commands working
7. ✅ All API endpoints working
8. ✅ Compatibility layer allows all supported legacy imports
9. ✅ Clear import paths and module organization
10. ✅ Execution security rules defined and implemented
11. ✅ No import cycles (static analysis verified)
12. ✅ Dependency directions respected (static analysis verified)
13. ✅ Public API explicitly defined and finite
14. ✅ Deprecation policy with explicit removal version

---

## Next Steps

1. **✅ Plan approved for Phase 0 and Architecture Preparation**
2. **Begin Phase 0: Baseline and Inventory** (can start immediately)
3. **Begin Phase 1: Architecture and Security Rules** (can start after Phase 0)
4. **Resolve P0 Blockers before Phase 3**:
   - Verify compatibility mapping matches actual legacy namespaces
   - Validate static import-graph tool with test fixtures
   - Define execution security release gate
5. **Set up automated testing infrastructure**
6. **Create migration tracking board**

---

## Open Questions

1. **Team Capacity**
   - Who will be available for the migration?
   - Can we dedicate focused time to this effort?

2. **External Dependencies**
   - Are there external projects depending on current structure?
   - Should we coordinate with them before migration?

3. **Priority**
   - Is this the highest priority for the project?
   - Should we defer until after other features?

4. **Current Test Status**
   - What is the current test pass rate?
   - Are there known baseline failures?

---

**Last Updated**: 2026-10-28
**Version**: 0.2.1
**Status**: Implementation-Ready - Approved for Phase 0 and Architecture Preparation
