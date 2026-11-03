# External Dependencies

**Date**: 2026-10-28
**Phase**: Phase 0 - Baseline and Inventory
**Status**: Draft - External Usage Analysis

This document catalogs external projects and examples that depend on gpt-computer/gptc. This inventory will be used to ensure the restructure doesn't break external users and to coordinate with them if necessary.

---

## Overview

External dependencies include:
1. **Projects in the repository** - Example projects using gptc
2. **Examples in etc/examples/** - Code examples demonstrating gptc usage
3. **Documentation examples** - Code snippets in documentation
4. **Unknown external users** - Projects outside this repository (not tracked)

---

## Projects in Repository

### 1. Discord Bot

**Location**: `projects/discord-bot/`
**Purpose**: Discord bot powered by gptc for AI chat with MCP tool-calling
**Status**: Active project, extensively uses gptc API

**Dependencies**:
- `discord.py` - Discord API library
- `python-dotenv` - Environment variable management
- `gptc` - Primary dependency

**gptc Imports Used**:
```python
from gptc.providers.any_provider import AnyProvider
from gptc.client import ClientFactory
from gptc.Provider import GPTCSpace
from gptc.mcp.server import MCPServer, MCPRequest
```

**Usage Pattern**:
- Uses `AsyncClient` via `ClientFactory.create_async_client()`
- Uses `GPTCSpace` provider for AI completions
- Uses `MCPServer` for tool execution
- Streaming chat completions
- Tool-calling loop with MCP tools
- Model catalog queries

**Migration Impact**: **HIGH**
- This project is a complex, real-world usage example
- Uses multiple gptc modules (client, providers, MCP)
- Would break if imports change without compatibility shims
- Should be used as a test case for compatibility layer

**Recommendation**:
1. Include in compatibility testing
2. Update imports to use new structure after restructure
3. Document migration path for this project
4. Consider as a reference implementation

---

### 2. Benchmark Template

**Location**: `projects/bench-template/`
**Purpose**: Template for benchmarking agents against APPS/MBPP datasets
**Status**: Reference template for benchmarking

**Dependencies**:
- `gpt_computer` - Primary dependency (uses core modules)

**gpt_computer Imports Used**:
```python
from gpt_computer.core.ai import AI
from gpt_computer.core.base_execution_env import BaseExecutionEnv
from gpt_computer.core.base_memory import BaseMemory
from gpt_computer.core.default.disk_execution_env import DiskExecutionEnv
from gpt_computer.core.default.disk_memory import DiskMemory
from gpt_computer.core.default.paths import PREPROMPTS_PATH, memory_path
from gpt_computer.core.default.steps import improve_fn as improve
from gpt_computer.core.files_dict import FilesDict
from gpt_computer.core.preprompts_holder import PrepromptsHolder
from gpt_computer.core.prompt import Prompt
```

**Usage Pattern**:
- Uses core AI module for LLM interaction
- Uses disk execution environment for code execution
- Uses disk memory for state management
- Uses prompt system for agent prompts
- Follows standard agent pattern

**Migration Impact**: **MEDIUM**
- Uses core modules that will be restructured
- Import paths will change (core → ai, agent, execution, etc.)
- Should be updated as part of the restructure
- Good test case for core module migration

**Recommendation**:
1. Update imports to match new structure during migration
2. Use as integration test for core modules
3. Document migration path for similar projects

---

### 3. Android Project

**Location**: `projects/android/`
**Purpose**: Android application (appears to be a work-in-progress)
**Status**: Incomplete, minimal gptc usage

**Dependencies**:
- Unknown (not investigated in detail)

**Migration Impact**: **LOW**
- Incomplete project
- May not be actively maintained
- Can be updated later if needed

---

### 4. Example Improve Project

**Location**: `projects/example-improve/`
**Purpose**: Example project demonstrating improve mode
**Status**: Simple example

**Dependencies**:
- Standard Python (no external dependencies visible)

**Migration Impact**: **LOW**
- Simple example project
- Can be easily updated

---

## Examples in etc/examples/

### 1. Video Generation Example

**Location**: `etc/examples/video.py`
**Purpose**: Demonstrate video generation using HuggingFace provider

**gptc Imports Used**:
```python
import gptc.Provider
from gptc.client import Client
```

**Usage Pattern**:
- Uses `Client` with `HuggingFaceMedia` provider
- Generates video using `client.media.generate()`
- Uses model catalog via `client.models.get_video()`

**Migration Impact**: **MEDIUM**
- Uses module-level `gptc.Provider` import
- Will need compatibility shim for `gptc.Provider`
- Should be updated to use new import paths

---

### 2. OpenAI Chat Example

**Location**: `etc/examples/openaichat.py`
**Purpose**: Demonstrate OpenAI chat with streaming and retry logic

**gptc Imports Used**:
```python
from gptc.client import Client
from gptc.Provider import OpenaiChat, RetryProvider
```

**Usage Pattern**:
- Uses `Client` with `RetryProvider` wrapping `OpenaiChat`
- Demonstrates proxy configuration
- Streaming chat completions

**Migration Impact**: **MEDIUM**
- Uses `gptc.Provider` for provider access
- Will need compatibility shim
- Good example for provider usage

---

### 3. Other Examples

**Examples Directory Contents**:
- `messages_stream.py` - Message streaming
- `text_completions_demo_sync.py` - Synchronous completions
- `aibadgr.py` - Unknown purpose
- `api_generations_image.py` - Image generation via API
- `api_completions_copilot.py` - Copilot API
- `mcp_tools_demo.py` - MCP tools demonstration
- `text_completions_streaming.py` - Text streaming
- `messages.py` - Message API
- `audio.py` - Audio generation
- `vision_images.py` - Vision/image processing
- `vision_images_reka.py` - Reka vision
- `text_completions_demo_async.py` - Async completions

**Migration Impact**: **MEDIUM**
- Multiple examples using various gptc features
- Should be reviewed and updated as part of restructure
- Good test coverage for different use cases

---

## Documentation Examples

### API Guide

**Location**: `docs/guides/api-guide.md`
**Purpose**: REST API documentation

**gpt_computer Imports Used**:
```python
from gpt_computer import GptComputerAPI
```

**Note**: This appears to be a hypothetical SDK that doesn't exist yet. The documentation shows a planned Python client library.

**Migration Impact**: **LOW**
- This is documentation for a future feature
- Not currently implemented
- Should be updated when SDK is implemented

---

### Open LLM Examples

**Location**: `docs/examples/open_llms/`
**Purpose**: Examples for using gpt-computer with local LLMs

**Files**:
- `openai_api_interface.py` - Uses OpenAI library directly (not gptc)
- `langchain_interface.py` - Uses LangChain directly (not gptc)

**Migration Impact**: **NONE**
- These examples don't import gptc or gpt_computer
- They show how to use external libraries with local LLMs
- No impact from restructure

---

## Installation Instructions

### README.md

**Installation Command**:
```bash
python -m pip install gpt-computer
```

**Migration Impact**: **NONE**
- Package name remains `gpt-computer`
- No change to installation command
- Users install the package, not individual modules

---

### Windows Setup Guide

**Location**: `docs/guides/windows-setup.md`
**Installation Command**:
```bash
pip install gpt-computer
```

**Migration Impact**: **NONE**
- Same as README
- No change needed

---

## Unknown External Users

**Status**: NOT TRACKED

There may be external projects using gptc/gpt_computer that are not in this repository. These are not tracked and would be affected by breaking changes.

**Recommendation**:
1. Check GitHub for repositories that depend on this package
2. Check PyPI download statistics to gauge usage
3. Issue deprecation warnings before breaking changes
4. Provide migration guide and compatibility period

---

## Summary of External Dependencies

| Project/Example | Type | gptc/gpt_computer Usage | Migration Impact | Priority |
|-----------------|------|-------------------------|-----------------|----------|
| Discord Bot | Project | Extensive (client, providers, MCP) | HIGH | Critical |
| Benchmark Template | Project | Core modules (ai, execution, memory) | MEDIUM | High |
| Android Project | Project | Unknown | LOW | Low |
| Example Improve | Project | Minimal | LOW | Low |
| Video Example | Example | Client, Provider | MEDIUM | Medium |
| OpenAI Chat Example | Example | Client, Provider | MEDIUM | Medium |
| Other Examples | Example | Various | MEDIUM | Medium |
| API Guide | Documentation | Hypothetical SDK | LOW | Low |
| Open LLM Examples | Example | None (external libs) | NONE | None |
| Installation Docs | Documentation | Package name only | NONE | None |

---

## Migration Strategy for External Dependencies

### High Priority (Discord Bot)

1. **Before Breaking Changes**:
   - Test Discord bot with compatibility shims
   - Ensure all imports work with deprecation warnings
   - Document specific migration steps

2. **During Migration**:
   - Update Discord bot imports to new structure
   - Test all functionality (chat, tools, streaming)
   - Update README with new import patterns

3. **After Migration**:
   - Update Discord bot as reference implementation
   - Remove old import patterns from examples
   - Document final import structure

### Medium Priority (Examples, Benchmark Template)

1. **Update Examples**:
   - Systematically update all examples in `etc/examples/`
   - Test each example after update
   - Add comments explaining new import structure

2. **Update Benchmark Template**:
   - Update imports to match new core structure
   - Test benchmark execution
   - Update documentation if needed

### Low Priority (Documentation, Incomplete Projects)

1. **Update Documentation**:
   - Review all documentation for import examples
   - Update to use new import patterns
   - Add migration guide section

2. **Incomplete Projects**:
   - Update if still maintained
   - Otherwise, can be updated later

---

## Compatibility Requirements

Based on external dependencies, the restructure must:

1. **Provide Compatibility Shims For**:
   - `gptc.Provider` module-level access
   - `gptc.client.Client` and `AsyncClient`
   - `gptc.providers.any_provider.AnyProvider`
   - `gptc.mcp.server.MCPServer` and `MCPRequest`
   - `gpt_computer.core.ai.AI`
   - `gpt_computer.core.default.*` modules
   - `gpt_computer.core.files_dict.FilesDict`
   - `gpt_computer.core.prompt.Prompt`

2. **Deprecation Period**:
   - Minimum 12 months before removing compatibility shims
   - Clear deprecation warnings for all legacy imports
   - Migration guide documenting all changes

3. **Testing**:
   - Test Discord bot with compatibility shims
   - Test all examples with compatibility shims
   - Test benchmark template with compatibility shims
   - Ensure no breaking changes without warning

---

## Next Steps

1. **Contact External Users** (if any known):
   - Check GitHub for dependent repositories
   - Reach out to maintainers of dependent projects
   - Coordinate migration timeline

2. **Update Examples**:
   - Create new versions of examples using new structure
   - Keep old versions with deprecation warnings temporarily
   - Document migration path for users

3. **Test Compatibility**:
   - Use Discord bot as integration test
   - Use examples as unit tests for compatibility
   - Ensure all documented usage patterns work

4. **Document Migration**:
   - Create comprehensive migration guide
   - Document all import path changes
   - Provide before/after examples
   - Add troubleshooting section

---

**Last Updated**: 2026-10-28
**Phase**: Phase 0 - Baseline and Inventory
