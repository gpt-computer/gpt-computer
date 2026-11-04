# Dependency Rules

**Date**: 2026-10-28
**Phase**: Phase 1 - Architecture and Security Rules
**Status**: Draft - Pending Review

This document defines the architectural dependency rules for the restructured gpt-computer codebase. These rules ensure clear separation of concerns, prevent circular dependencies, and maintain a clean layered architecture.

---

## Architectural Layers

The restructured codebase is organized into the following layers (from bottom to top):

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

### Layer Descriptions

| Layer | Purpose | Responsibilities |
|-------|---------|------------------|
| **infrastructure** | Low-level utilities and supporting code | Configuration, logging, file operations, git operations, diff utilities, linting |
| **execution** | Code execution environments | Local disk execution, sandboxed execution (future) |
| **ai** | AI client and provider abstractions | Client implementations, provider implementations, model registry, cookies, images |
| **agent** | Agent system and orchestration | Agent implementations, tools, memory, prompts, parsing, tracking |
| **analysis** | Code analysis and repository intelligence | Codemap, context management, repository intelligence agents |
| **interfaces** | User-facing interfaces | CLI, API, GUI, system tray, MCP server |

---

## Allowed Import Directions

### Dependency Graph

```
interfaces/
    ↓ (may import from)
agent/, execution/, ai/, infrastructure/
    ↓ (may import from)
analysis/
    ↓ (may import from)
agent/, infrastructure/
    ↓ (may import from)
agent/
    ↓ (may import from)
ai/, execution/, infrastructure/
    ↓ (may import from)
ai/
    ↓ (may import from)
infrastructure/
    ↓ (may import from)
execution/
    ↓ (may import from)
infrastructure/
```

### Allowed Dependencies by Layer

| Layer | May Import From | May NOT Import From |
|-------|-----------------|---------------------|
| **infrastructure** | None (no other gpt_computer modules) | agent, ai, execution, analysis, interfaces |
| **execution** | infrastructure only | ai, agent, analysis, interfaces |
| **ai** | infrastructure only | execution, agent, analysis, interfaces |
| **agent** | ai, execution, infrastructure | analysis, interfaces |
| **analysis** | agent, infrastructure | ai, execution, interfaces |
| **interfaces** | ai, agent, execution, infrastructure | analysis |

### Same-Layer Imports

- **Allowed**: Modules within the same layer may import from each other
- **Example**: `interfaces/cli` may import from `interfaces/api`
- **Example**: `ai/client` may import from `ai/providers`

---

## Prohibited Dependencies

### Absolute Prohibitions

1. **No Circular Dependencies**
   - Module A imports Module B, and Module B imports Module A (directly or transitively)
   - Violates architectural principles
   - Must be detected by static analysis

2. **No Higher Layer Importing from Lower Layer's Private Modules**
   - Higher layers may import from lower layers' public APIs only
   - Private modules (prefixed with `_`) should not be imported across layers
   - Example: `interfaces` should not import from `ai/providers/_internal.py`

3. **Infrastructure Importing from Higher Layers**
   - `infrastructure` must remain at the bottom
   - Cannot import from agent, ai, execution, analysis, or interfaces
   - This would create an upward dependency

4. **Interfaces Importing from Analysis**
   - `interfaces` must NOT import from `analysis`
   - Analysis is designed to be agent-dependent and may have complex dependencies
   - Interfaces should remain lightweight and user-facing

5. **Analysis Importing from Interfaces**
   - `analysis` must NOT import from `interfaces`
   - Analysis should operate on core abstractions, not UI/API code
   - Prevents analysis from depending on user-facing code

### Prohibited Edge Matrix

| From Layer | To Layer | Status | Reason |
|------------|----------|--------|--------|
| infrastructure | any | ❌ | Infrastructure is the bottom layer |
| execution | ai | ❌ | Execution should not depend on AI clients |
| execution | agent | ❌ | Execution should not depend on agents |
| execution | analysis | ❌ | Execution should not depend on analysis |
| execution | interfaces | ❌ | Execution should not depend on interfaces |
| ai | execution | ❌ | AI clients should not depend on execution |
| ai | agent | ❌ | AI clients should not depend on agents |
| ai | analysis | ❌ | AI clients should not depend on analysis |
| ai | interfaces | ❌ | AI clients should not depend on interfaces |
| agent | analysis | ❌ | Agents should not depend on analysis |
| agent | interfaces | ❌ | Agents should not depend on interfaces |
| analysis | ai | ❌ | Analysis should not depend on AI (optional, if agent-independent) |
| analysis | execution | ❌ | Analysis should not depend on execution (optional, if agent-independent) |
| analysis | interfaces | ❌ | Analysis must NOT depend on interfaces |
| interfaces | analysis | ❌ | Interfaces must NOT depend from analysis |

---

## Special Cases

### MCP Server Placement

**Decision**: MCP server is placed in `interfaces/mcp/` (not `ai/mcp/`)

**Rationale**:
- MCP server is a user-facing interface for tool calling
- It orchestrates agents and tools, making it more of an interface than a core AI component
- Placing it in `interfaces/` allows it to depend on `agent/` without violating rules
- If placed in `ai/`, it would need to depend on `agent/`, violating the AI layer's dependency constraints

**Allowed Dependencies**:
- `interfaces/mcp/` may import from: `agent/`, `ai/`, `execution/`, `infrastructure/`
- `interfaces/mcp/` must NOT import from: `analysis/`

### Provider Configuration

**Decision**: Provider-specific settings in `ai/providers/config.py`, global config in `infrastructure/config/`

**Rationale**:
- Provider configuration is provider-specific and belongs with provider implementations
- Global application configuration should be centralized in infrastructure
- This separation prevents provider config from depending on application-level concerns

**Structure**:
```
ai/providers/config.py       # Provider-specific configuration (API keys, endpoints)
infrastructure/config/       # Global application configuration (model defaults, paths)
```

### Analysis Modules

**Decision**: Some analysis modules are agent-independent

**Rationale**:
- Not all analysis features require agents
- Codemap and tree_sitter_analyzer can work independently
- Context management and repository intelligence agents are agent-dependent

**Agent-Independent Analysis**:
- `analysis/codemap/` - Code mapping and visualization
- `analysis/repository/tree_sitter_analyzer.py` - Tree-sitter based analysis

**Agent-Dependent Analysis**:
- `analysis/context/` - Context management (requires agent)
- `analysis/repository/` - Repository intelligence agents (require agent)

**Allowed Dependencies**:
- Agent-independent analysis may import from: `infrastructure/` only
- Agent-dependent analysis may import from: `agent/`, `infrastructure/`

---

## Enforcement

### Static Analysis Tool

A static import-graph analysis tool will be created to:
1. Parse all Python files in the source tree
2. Build a dependency graph of imports
3. Detect circular dependencies
4. Verify dependency directions match allowed rules
5. Report violations with clear error messages

**Tool Location**: `tests/test_static_imports.py` (see RESTRUCTURE_PLAN.md for implementation)

### Pre-Commit Hook

A pre-commit hook will run the static analysis tool to:
- Prevent commits that introduce dependency violations
- Provide immediate feedback to developers
- Maintain architectural integrity over time

### CI/CD Integration

The static analysis tool will be integrated into CI/CD to:
- Run on every pull request
- Block merges that introduce violations
- Provide architectural governance

---

## Migration Compliance

### During Migration

1. **Incremental Verification**:
   - After each domain migration, run static analysis
   - Verify no new violations introduced
   - Fix violations before proceeding to next domain

2. **Temporary Violations**:
   - If temporary violations are unavoidable, document them
   - Create issue to track resolution
   - Remove temporary violations before final release

3. **Compatibility Layer**:
   - Compatibility shims (gptc/, gpt_computer/core/) are exempt from dependency rules
   - They exist only for backward compatibility
   - Will be removed after deprecation period

### Post-Migration

1. **Full Compliance**:
   - All new code must comply with dependency rules
   - Static analysis must pass without errors
   - No circular dependencies allowed

2. **Ongoing Enforcement**:
   - Pre-commit hooks enforce rules on every commit
   - CI/CD enforces rules on every PR
   - Violations block merges

---

## Examples

### Valid Dependencies

```python
# ✅ Valid: interfaces/cli importing from agent
from gpt_computer.agent import BaseAgent

# ✅ Valid: agent importing from ai
from gpt_computer.ai.client import Client

# ✅ Valid: execution importing from infrastructure
from gpt_computer.infrastructure.files import operations

# ✅ Valid: ai importing from infrastructure
from gpt_computer.infrastructure.config import settings

# ✅ Valid: analysis importing from agent
from gpt_computer.agent import ReActAgent

# ✅ Valid: same-layer import
from gpt_computer.ai.providers.openai import OpenAIProvider
```

### Invalid Dependencies

```python
# ❌ Invalid: infrastructure importing from agent
from gpt_computer.agent import BaseAgent  # VIOLATION

# ❌ Invalid: interfaces importing from analysis
from gpt_computer.analysis.codemap import CodemapConfig  # VIOLATION

# ❌ Invalid: analysis importing from interfaces
from gpt_computer.interfaces.cli import main  # VIOLATION

# ❌ Invalid: ai importing from execution
from gpt_computer.execution.local import LocalExecutionEnv  # VIOLATION

# ❌ Invalid: circular dependency
# Module A imports Module B, Module B imports Module A
```

---

## Exceptions Process

### Requesting an Exception

If a dependency rule needs to be violated for a legitimate reason:

1. **Document the Reason**:
   - Explain why the violation is necessary
   - Propose alternative approaches and why they don't work
   - Assess the impact on architectural integrity

2. **Review with Maintainers**:
   - Submit RFC (Request for Comments) to maintainers
   - Get approval before implementing the violation
   - Document the approved exception

3. **Mark with Exception Comment**:
   ```python
   # DEPENDENCY_RULE_EXCEPTION: interfaces importing from analysis
   # Approved by: @maintainer
   # Reason: ...
   # Ticket: https://github.com/gpt-computer/gpt-computer/issues/123
   from gpt_computer.analysis import Something
   ```

4. **Track Exceptions**:
   - Maintain a list of approved exceptions
   - Review exceptions periodically
   - Remove exceptions when no longer needed

---

## Review and Maintenance

### Regular Review

The dependency rules should be reviewed:
- **Quarterly**: Assess if rules are still appropriate
- **After Major Features**: Evaluate if new features require rule adjustments
- **When Exceptions Accumulate**: If many exceptions are approved, consider updating rules

### Updating Rules

To update dependency rules:

1. **Propose Change**:
   - Document the proposed change
   - Explain the rationale
   - Assess impact on existing code

2. **Review with Team**:
   - Discuss with maintainers and contributors
   - Get consensus on the change

3. **Update Documentation**:
   - Update this document
   - Update static analysis tool
   - Communicate change to team

4. **Update Tests**:
   - Update dependency verification tests
   - Ensure tests reflect new rules

---

## References

- **RESTRUCTURE_PLAN.md**: Overall restructure plan with architectural decisions
- **tests/test_static_imports.py**: Static analysis tool implementation
- **pyproject.toml**: Pre-commit hook configuration

---

**Last Updated**: 2026-10-28
**Phase**: Phase 1 - Architecture and Security Rules
**Status**: Draft - Pending Review
