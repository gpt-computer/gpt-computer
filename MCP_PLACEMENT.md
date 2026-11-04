# MCP Server Placement

**Date**: 2026-10-28
**Phase**: Phase 1 - Architecture and Security Rules
**Status**: Documented - Migration Pending

This document confirms the MCP server placement decision and documents the migration plan.

---

## Current Location

**Path**: `gptc/mcp/`

**Contents**:
- `server.py` - MCP server implementation
- `tools.py` - MCP tool definitions
- `pa_provider.py` - PA provider for code execution
- `apply_patch.py` - Patch application utility
- `pa_downloader.py` - PA provider downloader
- `__init__.py` - Package initialization
- `__main__.py` - CLI entry point

---

## Target Location

**Path**: `gpt_computer/interfaces/mcp/`

**Rationale** (from RESTRUCTURE_PLAN.md):

The MCP server is placed in `interfaces/mcp/` (not `ai/mcp/`) because:
- MCP server is a user-facing interface for tool calling
- It orchestrates agents and tools, making it more of an interface than a core AI component
- Placing it in `interfaces/` allows it to depend on `agent/` without violating rules
- If placed in `ai/`, it would need to depend on `agent/`, violating the AI layer's dependency constraints

---

## Allowed Dependencies

**From** `interfaces/mcp/`:
- `agent/` - Agent orchestration
- `ai/` - AI client and providers
- `execution/` - Code execution environments
- `infrastructure/` - File operations, config, etc.

**Must NOT Import From**:
- `analysis/` - Analysis should not depend on interfaces

---

## Migration Plan

### Phase 4 (Domain Migration - Interfaces Week)

**Steps**:

1. **Create New Directory**:
   ```bash
   mkdir -p gpt_computer/interfaces/mcp
   ```

2. **Move Files**:
   ```bash
   mv gptc/mcp/* gpt_computer/interfaces/mcp/
   ```

3. **Update Imports**:
   - Update all imports in moved files
   - Update imports from `gptc.mcp` to `gpt_computer.interfaces.mcp`
   - Update `gptc/mcp/__main__.py` to `gpt_computer/interfaces/mcp/__main__.py`

4. **Update pyproject.toml**:
   ```toml
   # Old
   gptc-mcp = "gptc.mcp.server:main"
   
   # New
   gptc-mcp = "gpt_computer.interfaces.mcp.server:main"
   ```

5. **Update CLI**:
   - Update `gptc/cli/__init__.py` to import from new location
   - Update mode handler for MCP

6. **Add Compatibility Shim**:
   ```python
   # gptc/mcp/__init__.py (compatibility shim)
   import warnings
   from gpt_computer.interfaces.mcp.server import MCPServer, MCPRequest
   
   warnings.warn(
       "Importing from gptc.mcp is deprecated. "
       "Use gpt_computer.interfaces.mcp instead.",
       DeprecationWarning,
       stacklevel=2
   )
   
   __all__ = ['MCPServer', 'MCPRequest']
   ```

7. **Update Tests**:
   - Update test imports
   - Update Discord bot imports
   - Run tests to verify

8. **Update Documentation**:
   - Update RESTRUCTURE_PLAN.md status
   - Update any documentation referencing MCP location
   - Update Discord bot README

---

## External Dependencies

### Discord Bot

**Current Import**:
```python
from gptc.mcp.server import MCPServer, MCPRequest
```

**New Import**:
```python
from gpt_computer.interfaces.mcp.server import MCPServer, MCPRequest
```

**Compatibility**:
- Old import will work with deprecation warning
- Update after deprecation period

---

## Testing

### Unit Tests

- Test MCP server functionality after move
- Test tool execution after move
- Test PA provider after move

### Integration Tests

- Test Discord bot with new MCP location
- Test CLI MCP mode with new location
- Test gptc-mcp CLI entry point

### Compatibility Tests

- Test old imports work with deprecation warnings
- Test new imports work correctly
- Test API identity preserved

---

## Risk Assessment

**Risk**: Medium

**Reasons**:
- MCP server is used by Discord bot (external dependency)
- MCP server has complex dependencies (agent, execution, ai)
- Moving it may break existing workflows

**Mitigation**:
- Provide compatibility shim
- Test thoroughly with Discord bot
- Document migration clearly
- Provide deprecation period

---

## Status

**Current**: Located at `gptc/mcp/`
**Target**: `gpt_computer/interfaces/mcp/`
**Migration Phase**: Phase 4 (Interfaces)
**Status**: Documented, migration pending

---

**Last Updated**: 2026-10-28
**Phase**: Phase 1 - Architecture and Security Rules
