# Migration Guide: gpt-computer Restructure

## Overview

The gpt-computer project has been restructured from a confusing dual-package layout
(`gpt_computer` and `gptc`) into a single, well-organized package with clear module
boundaries. This guide helps you migrate from the old import paths to the new ones.

## What Changed

### Package Structure

The old structure had two packages:
- `gpt_computer/` — Primary package (agent system)
- `gptc/` — Secondary package (AI client library)

The new structure consolidates everything under `gpt_computer/` with clear layers:

```
gpt_computer/
├── ai/              # AI Client Layer (client, models, providers, errors)
├── agent/           # Agent System (base, react, simple, tools, memory, prompts)
├── execution/       # Execution Environments (base, local, sandbox)
├── interfaces/      # User Interfaces (cli, api, gui, tray, mcp)
├── analysis/        # Analysis Tools (codemap, context, repository)
├── infrastructure/  # Supporting Infrastructure (config, logging, tracing, git, files, diff, linting)
├── benchmark/       # Benchmarking
└── utils/           # General utilities
```

### Import Migration

#### AI Client Imports

| Old Import | New Import |
|-----------|------------|
| `from gptc import Client` | `from gpt_computer.ai.client import Client` |
| `from gptc import AsyncClient` | `from gpt_computer.ai.client import AsyncClient` |
| `from gptc import ChatCompletion` | `from gpt_computer.ai.chat_completion import ChatCompletionAPI` |
| `from gptc import Model` | `from gpt_computer.ai.models import Model` |
| `from gptc.providers import BaseProvider` | `from gpt_computer.ai.providers.base import BaseProvider` |
| `from gptc.errors import GPTCError` | `from gpt_computer.ai.errors import GPTCError` |

#### Agent Imports

| Old Import | New Import |
|-----------|------------|
| `from gpt_computer.core.base_agent import BaseAgent` | `from gpt_computer.agent import BaseAgent` |
| `from gpt_computer.core.ai import AI` | `from gpt_computer.ai.client import AI` |
| `from gpt_computer.core.prompt import Prompt` | `from gpt_computer.agent.prompt import Prompt` |
| `from gpt_computer.core.files_dict import FilesDict` | `from gpt_computer.infrastructure.files import FilesDict` |

#### Infrastructure Imports

| Old Import | New Import |
|-----------|------------|
| `from gpt_computer.core.config import get_settings` | `from gpt_computer.infrastructure.config import get_settings` |
| `from gpt_computer.core.git import is_git_installed` | `from gpt_computer.infrastructure.git import is_git_installed` |
| `from gpt_computer.core.files_dict import FilesDict` | `from gpt_computer.infrastructure.files import FilesDict` |
| `from gpt_computer.core.diff import is_similar` | `from gpt_computer.infrastructure.diff import is_similar` |
| `from gpt_computer.core.linting import Linting` | `from gpt_computer.infrastructure.linting import Linting` |
| `from gpt_computer.core.logging_config import setup_logging` | `from gpt_computer.infrastructure.logging import setup_logging` |
| `from gpt_computer.core.structured_logging import get_logger` | `from gpt_computer.infrastructure.logging import get_logger` |
| `from gpt_computer.core.tracing import setup_tracing` | `from gpt_computer.infrastructure.tracing import setup_tracing` |

#### Execution Imports

| Old Import | New Import |
|-----------|------------|
| `from gpt_computer.core.base_execution_env import BaseExecutionEnv` | `from gpt_computer.execution import BaseExecutionEnv` |
| `from gpt_computer.core.default.disk_execution_env import DiskExecutionEnv` | `from gpt_computer.execution.local import DiskExecutionEnv` |
| `from gpt_computer.core.default.docker_execution_env import DockerExecutionEnv` | `from gpt_computer.execution.sandbox import DockerExecutionEnv` |

#### Analysis Imports

| Old Import | New Import |
|-----------|------------|
| `from gpt_computer.codemap import PythonAnalyzer` | `from gpt_computer.analysis.codemap import PythonAnalyzer` |
| `from gpt_computer.repository_intelligence import TreeSitterAnalyzer` | `from gpt_computer.analysis.repository import TreeSitterAnalyzer` |
| `from gpt_computer.context_os import ContextManager` | `from gpt_computer.analysis.context import ContextManager` |

#### Interface Imports

| Old Import | New Import |
|-----------|------------|
| `from gpt_computer.api import app` | `from gpt_computer.interfaces.api import app` |
| `from gpt_computer.applications.cli import CliAgent` | `from gpt_computer.interfaces.cli import CliAgent` |

## Backward Compatibility

All old imports continue to work with `DeprecationWarning` during the compatibility period
(minimum 12 months from version 0.3.0 release). No code changes are required immediately,
but you should update your imports to use the new paths.

### Enabling Deprecation Warnings

Deprecation warnings are hidden by default in Python. To see them:

```python
import warnings
warnings.simplefilter("always", DeprecationWarning)
```

Or run Python with the `-W all` flag:
```bash
python -W all your_script.py
```

## CLI Commands

CLI commands remain unchanged:
- `gptc` — Primary command (unchanged)
- `gpt-computer`, `ge` — Aliases (deprecated, will be removed in 1.0.0)
- `gptc-mcp`, `gptc-tray`, `bench` — Legacy aliases (deprecated)

## Version Schedule

- **Current**: 0.2.2
- **Restructure release**: 0.3.0 (compatibility shims added)
- **Deprecation period**: 0.3.x → 0.4.x → 0.5.x (minimum 12 months)
- **Removal scheduled**: 1.0.0

## Need Help?

If you encounter issues during migration, please:
1. Check the `PUBLIC_IMPORTS.md` for the complete list of supported imports
2. Review the `RESTRUCTURE_PLAN.md` for the full architecture
3. File an issue at https://github.com/anomalyco/opencode/issues
EOF
echo "MIGRATION_GUIDE.md created"